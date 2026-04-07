import re
import asyncio
from config import get_agent_model, get_system_rules
from state import AgentState
from utils import CodeRunner


def extract_code(text):
    pattern = r"```(?:\w+)?\s*(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else text.replace("```", "").strip()


# async def supervisor_node(state: AgentState) -> AgentState:
#     print("--- Supervisor Active ---")
    
#     return {
#         "current_status": "Supervisor: 📋 Task initialized. Handing off to Developer...",
#         "iteration_count": 0,
#         "code": "",
#         "review_feedback": "",
#         "test_result": ""
#     }


# async def developer_node(state: AgentState) -> AgentState:
#     print("--- Developer Active (Waiting 15s for Rate Limit)... ---")
    
    
#     await asyncio.sleep(15) 

#     model = get_agent_model("Developer")
#     task = state["task"]
#     lang = state.get("language", "Python")
#     code = state.get("code", "")
#     feedback = state.get("review_feedback", "")

#     if not code:
#         prompt = f"Write {lang} code for: {task}. Return ONLY code inside ```{lang.lower()}``` blocks."
#     else:
#         prompt = f"Fix this {lang} code based on feedback: {feedback}\nCODE:\n{code}"

#     try:
        
#         if hasattr(model, "generate_content_async"):
#             response = await model.generate_content_async(prompt)
#             text = response.text
#         else:
            
#             response = model.models.generate_content(model='gemini-2.5-flash', contents=prompt)
#             text = response.text

#         clean_code = extract_code(text)
#         status = f"Developer: 💻 Finished writing {lang} code."
#     except Exception as e:
#         print(f"Developer Error: {e}")
#         clean_code = code
#         status = f"Developer: ⚠️ API Error: {str(e)}"
    
#     return {"code": clean_code, "current_status": status, "iteration_count": state["iteration_count"] + 1}


# async def reviewer_node(state: AgentState) -> AgentState:
#     print("--- Reviewer Active (Waiting 15s for Rate Limit)... ---")
    
    
#     await asyncio.sleep(15)

#     model = get_agent_model("Reviewer")
#     code = state["code"]
#     lang = state.get("language", "Python")

#     prompt = f"Review this {lang} code. If perfect, reply 'APPROVED'. Else, list bugs.\n{code}"
#     try:
#         if hasattr(model, "generate_content_async"):
#             response = await model.generate_content_async(prompt)
#             feedback = response.text
#         else:
#             response = model.models.generate_content(model='gemini-2.5-flash', contents=prompt)
#             feedback = response.text
#     except:
#         feedback = "APPROVED" 
        
#     return {"review_feedback": feedback, "current_status": "Reviewer: 🔍 Logic check complete."}


# async def tester_node(state: AgentState) -> AgentState:
#     print("--- Tester Active ---")
#     code = state.get("code", "")
#     lang = state.get("language", "Python")
    
#     if lang.lower() == "python":
#         output = CodeRunner.run_with_timeout(code)
#     else:
#         print("--- Tester Waiting 15s for Rate Limit... ---")
#         await asyncio.sleep(15)
        
#         model = get_agent_model("Tester")
#         prompt = f"Check this {lang} code for syntax errors. Reply 'PASS' or list errors.\n{code}"
#         try:
#             if hasattr(model, "generate_content_async"):
#                 res = await model.generate_content_async(prompt)
#                 output = res.text
#             else:
#                 res = model.models.generate_content(model='gemini-2.5-flash', contents=prompt)
#                 output = res.text
#         except:
#             output = "PASS"

#     # NEW LOGIC: Look for "PASS" or "Execution Passed"
#     if "PASS" in output.upper() or "EXECUTION PASSED" in output.upper():
#         status = "Tester: ✅ PASS"
#     else:
#         status = "Tester: ❌ FAIL"
        
#     return {"test_result": output, "current_status": status}
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
    print("--- Developer Active ---")
    # Lowered sleep from 15s to 2s because Gemma gives us 30 RPM!
    await asyncio.sleep(2) 

    model = get_agent_model()
    rules = get_system_rules("Developer")
    
    task = state["task"]
    lang = state.get("language", "Python")
    code = state.get("code", "")
    feedback = state.get("review_feedback", "")

    if not code:
        user_request = f"Write {lang} code for: {task}. Return ONLY code inside ```{lang.lower()}``` blocks."
    else:
        user_request = f"Fix this {lang} code based on feedback: {feedback}\nCODE:\n{code}"

    # Injecting the System Rules directly into the prompt to bypass the API error
    full_prompt = f"SYSTEM RULES:\n{rules}\n\nUSER REQUEST:\n{user_request}"

    try:
        response = await model.generate_content_async(full_prompt)
        text = response.text
        clean_code = extract_code(text)
        status = f"Developer: 💻 Finished writing {lang} code."
    except Exception as e:
        print(f"Developer Error: {e}")
        clean_code = code
        status = f"Developer: ⚠️ API Error: {str(e)}"
    
    return {"code": clean_code, "current_status": status, "iteration_count": state["iteration_count"] + 1}

async def reviewer_node(state: AgentState) -> AgentState:
    print("--- Reviewer Active ---")
    await asyncio.sleep(2)

    model = get_agent_model()
    rules = get_system_rules("Reviewer")
    
    code = state["code"]
    lang = state.get("language", "Python")

    user_request = f"Review this {lang} code. If perfect, reply 'APPROVED'. Else, list bugs.\n{code}"
    full_prompt = f"SYSTEM RULES:\n{rules}\n\nUSER REQUEST:\n{user_request}"
    
    try:
        response = await model.generate_content_async(full_prompt)
        feedback = response.text
    except Exception as e:
        print(f"Reviewer Error: {e}")
        feedback = "APPROVED" 
        
    return {"review_feedback": feedback, "current_status": "Reviewer: 🔍 Logic check complete."}

async def tester_node(state: AgentState) -> AgentState:
    print("--- Tester Active ---")
    code = state.get("code", "")
    lang = state.get("language", "Python")
    
    if lang.lower() == "python":
        output = CodeRunner.run_with_timeout(code)
    else:
        print("--- Tester Active (Non-Python) ---")
        await asyncio.sleep(2)
        
        model = get_agent_model()
        rules = get_system_rules("Tester")
        
        user_request = f"Check this {lang} code for syntax errors. Reply 'PASS' or list errors.\n{code}"
        full_prompt = f"SYSTEM RULES:\n{rules}\n\nUSER REQUEST:\n{user_request}"
        
        try:
            res = await model.generate_content_async(full_prompt)
            output = res.text
        except Exception as e:
            print(f"Tester Error: {e}")
            output = "PASS"

    if "PASS" in output.upper() or "EXECUTION PASSED" in output.upper():
        status = "Tester: ✅ PASS"
    else:
        status = "Tester: ❌ FAIL"
        
    return {"test_result": output, "current_status": status}