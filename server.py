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


def _build_initial_state(task: str, language: str) -> dict:
    return {
        "task": task,
        "language": language,
        "files": {},
        "active_file": "",
        "task_plan": [],
        "error_logs": "",
        "iteration_count": 0,
        "current_agent": "Supervisor",
        "status": "planning",
        "conversation_history": [],
        "review_feedback": "",
        "test_result": "",
    }


@app.get("/run_stream")
async def run_stream(task: str, language: str):
    async def event_generator():
        try:
            workflow = create_workflow()
            initial_state = _build_initial_state(task, language)
            final_files: dict = {}
            final_active_file = ""
            final_status = "completed"

            async for event in workflow.astream(initial_state):
                for agent, data in event.items():
                    if isinstance(data, dict):
                        if data.get("files"):
                            final_files = data["files"]
                        if data.get("active_file"):
                            final_active_file = data["active_file"]
                        if data.get("status"):
                            final_status = data["status"]

                    payload = {
                        "agent": agent,
                        "status": data.get("status", "processing") if isinstance(data, dict) else "processing",
                        "files": data.get("files", {}) if isinstance(data, dict) else {},
                        "active_file": data.get("active_file", "") if isinstance(data, dict) else "",
                        "active_file_content": (
                            data.get("files", {}).get(data.get("active_file", ""), "")
                            if isinstance(data, dict) and data.get("active_file")
                            else ""
                        ),
                        "error_logs": data.get("error_logs", "") if isinstance(data, dict) else "",
                        "feedback": data.get("review_feedback", "") if isinstance(data, dict) else "",
                        "test_result": data.get("test_result", "") if isinstance(data, dict) else "",
                    }

                    yield json.dumps(payload) + "\n"
                    await asyncio.sleep(0.1)

            if supabase:
                try:
                    primary_file = final_active_file or (next(iter(final_files), "") if final_files else "")
                    primary_content = final_files.get(primary_file, "")
                    supabase.table("pixeldevs_runs").insert({
                        "task": task,
                        "language": language,
                        "final_code": primary_content,
                        "files": final_files,
                        "status": final_status,
                    }).execute()
                    print("Successfully saved run to Supabase.")
                except Exception as db_e:
                    print(f"Failed to save to Supabase: {db_e}")

        except Exception as e:
            print("Server Error Traceback:")
            traceback.print_exc()
            yield json.dumps({"error": str(e), "status": "failed"}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

# Mount static frontend files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
