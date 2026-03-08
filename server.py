import os
import json
import asyncio
import traceback
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from graph import create_workflow

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- SUPABASE INITIALIZATION ---
# Grab API keys securely from Environment Variables (Injected by Cloud Run)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Initialize client only if keys are present
supabase: Client | None = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("Warning: Supabase environment variables not found. DB saves are disabled.")

@app.get("/run_stream")
async def run_stream(task: str, language: str):
    async def event_generator():
        try:
            workflow = create_workflow()
            
            initial_state = {
                "task": task,
                "language": language,
                "code": "",
                "review_feedback": "",
                "test_result": "",
                "conversation_history": [],  
                "iteration_count": 0,
                "current_status": "Supervisor:  Preparing..."
            }
            
            final_code = "" # Variable to capture the code as it updates
            
            async for event in workflow.astream(initial_state):
                for agent, data in event.items():
                    
                    # Update final_code whenever an agent modifies the code state
                    if "code" in data and data["code"]:
                        final_code = data["code"]
                        
                    payload = {
                        "agent": agent,
                        "status": data.get("current_status", "Processing..."),
                        "code": data.get("code", ""),
                        "feedback": data.get("review_feedback", ""),
                        "test_result": data.get("test_result", "")
                    }
                    
                    yield json.dumps(payload) + "\n"
                    
                    await asyncio.sleep(0.1)

            # --- SUPABASE SAVE OPERATION ---
            # Save the final code to the database after the workflow finishes
            if supabase:
                try:
                    supabase.table("pixeldevs_runs").insert({
                        "task": task,
                        "language": language,
                        "final_code": final_code,
                        "status": "Success"
                    }).execute()
                    print("Successfully saved run to Supabase.")
                except Exception as db_e:
                    print(f"Failed to save to Supabase: {db_e}")

        except Exception as e:
            print("Server Error Traceback:")
            traceback.print_exc()
            yield json.dumps({"error": str(e)}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

# Mount static frontend files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Cloud Run dynamically assigns a port via the PORT environment variable. 
    # We default to 8080 here so it works both locally and on the cloud.
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)