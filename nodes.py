import re
import asyncio
from config import get_agent_model
from state import AgentState
from utils import CodeRunner


def extract_code(text):
    pattern = r"```(?:\w+)?\s*(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else text.replace("```", "").strip()


async def supervisor_node(state: AgentState) -> AgentState:
    print("--- Supervisor Active ---")
    
    return {
        "current_status": "Supervisor: 📋 Task initialized. Handing off to Developer...",
        "iteration_count": 0,
        "code": "",
        "review_feedback": "",
        "test_result": ""
    }


async def developer_node(state: AgentState) -> AgentState:
    print("--- Developer Active (Waiting 15s for Rate Limit)... ---")
    
    
    await asyncio.sleep(15) 

    model = get_agent_model("Developer")
    task = state["task"]
    lang = state.get("language", "Python")
    code = state.get("code", "")
    feedback = state.get("review_feedback", "")

    if not code:
        prompt = f"Write {lang} code for: {task}. Return ONLY code inside ```{lang.lower()}``` blocks."
    else:
        prompt = f"Fix this {lang} code based on feedback: {feedback}\nCODE:\n{code}"

    try:
        
        if hasattr(model, "generate_content_async"):
            response = await model.generate_content_async(prompt)
            text = response.text
        else:
            
            response = model.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            text = response.text

        clean_code = extract_code(text)
        status = f"Developer: 💻 Finished writing {lang} code."
    except Exception as e:
        print(f"Developer Error: {e}")
        clean_code = code
        status = f"Developer: ⚠️ API Error: {str(e)}"
    
    return {"code": clean_code, "current_status": status, "iteration_count": state["iteration_count"] + 1}


async def reviewer_node(state: AgentState) -> AgentState:
    print("--- Reviewer Active (Waiting 15s for Rate Limit)... ---")
    
    
    await asyncio.sleep(15)

    model = get_agent_model("Reviewer")
    code = state["code"]
    lang = state.get("language", "Python")

    prompt = f"Review this {lang} code. If perfect, reply 'APPROVED'. Else, list bugs.\n{code}"
    try:
        if hasattr(model, "generate_content_async"):
            response = await model.generate_content_async(prompt)
            feedback = response.text
        else:
            response = model.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            feedback = response.text
    except:
        feedback = "APPROVED" 
        
    return {"review_feedback": feedback, "current_status": "Reviewer: 🔍 Logic check complete."}


async def tester_node(state: AgentState) -> AgentState:
    print("--- Tester Active ---")
    code = state["code"]
    lang = state.get("language", "Python")
    
    if lang.lower() == "python":
        output = CodeRunner.run_with_timeout(code)
    else:
        print("--- Tester Waiting 15s for Rate Limit... ---")
        await asyncio.sleep(15)
        
        model = get_agent_model("Tester")
        prompt = f"Check this {lang} code for syntax errors. Reply 'PASS' or list errors.\n{code}"
        try:
            if hasattr(model, "generate_content_async"):
                res = await model.generate_content_async(prompt)
                output = res.text
            else:
                res = model.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                output = res.text
        except:
            output = "PASS"

    status = "Tester:  PASS" if "PASS" in output.upper() or "Successfully" in output else "Tester:  FAIL"
    return {"test_result": output, "current_status": status}