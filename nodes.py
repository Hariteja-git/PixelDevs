import re
import asyncio
from config import get_agent_model, get_system_rules
from state import AgentState, get_file, set_file, list_files
from utils import CodeRunner, extract_files_from_artifact


def extract_code(text):
    pattern = r"```(?:\w+)?\s*(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else text.replace("```", "").strip()


async def supervisor_node(state: AgentState) -> AgentState:
    print("--- Supervisor Active ---")
    return {
        "status": "planning",
        "current_agent": "Supervisor",
        "task_plan": list(state.get("task_plan", [])),
        "files": dict(state.get("files", {})),
        "active_file": state.get("active_file", ""),
        "iteration_count": 0,
        "review_feedback": "",
        "test_result": "",
        "error_logs": "",
    }


async def developer_node(state: AgentState) -> AgentState:
    print("--- Developer Active ---")
    await asyncio.sleep(2)

    model = get_agent_model()
    rules = get_system_rules("Developer")

    task = state["task"]
    lang = state.get("language", "Python")
    active_file = state.get("active_file", "")
    existing_content = get_file(state, active_file) if active_file else ""
    feedback = state.get("review_feedback", "")

    if not existing_content:
        user_request = (
            f"Write {lang} code for: {task}. "
            f"Output multi-file source code wrapped inside XML artifact blocks formatted exactly as: "
            f"<file path=\"relative/path/to/file.ext\">... complete file content ...</file>"
        )
    else:
        user_request = (
            f"Fix this {lang} code based on feedback: {feedback}\n"
            f"FILE: {active_file}\nCODE:\n{existing_content}\n"
            f"Output the fixed file wrapped in the same XML artifact block format."
        )

    full_prompt = f"SYSTEM RULES:\n{rules}\n\nUSER REQUEST:\n{user_request}"

    new_state = dict(state)
    new_state["current_agent"] = "Developer"
    new_state["status"] = "coding"

    if not active_file:
        active_file = "main.py" if lang.lower() == "python" else f"main.{lang.lower()}"
        new_state["active_file"] = active_file

    try:
        response = await model.generate_content_async(full_prompt)
        text = response.text
        file_dict = extract_files_from_artifact(text)
        if file_dict:
            for path, content in file_dict.items():
                new_state = set_file(new_state, path, content)
                if not new_state.get("active_file"):
                    new_state["active_file"] = path
            new_state["error_logs"] = ""
        else:
            new_state["error_logs"] = "Developer Error: No valid XML artifact blocks found in response"
            new_state["status"] = "failed"
    except Exception as e:
        print(f"Developer Error: {e}")
        new_state["error_logs"] = f"Developer API Error: {e}"
        new_state["status"] = "failed"

    new_state["iteration_count"] = state.get("iteration_count", 0) + 1
    return new_state


async def reviewer_node(state: AgentState) -> AgentState:
    print("--- Reviewer Active ---")
    await asyncio.sleep(2)

    model = get_agent_model()
    rules = get_system_rules("Reviewer")

    active_file = state.get("active_file", "")
    code = get_file(state, active_file) if active_file else ""
    lang = state.get("language", "Python")

    if not code:
        return {
            "review_feedback": "APPROVED",
            "status": "auditing",
            "current_agent": "Reviewer",
            "error_logs": state.get("error_logs", ""),
        }

    user_request = (
        f"Review this {lang} code. If perfect, reply 'APPROVED'. Else, list bugs.\n"
        f"FILE: {active_file}\n{code}"
    )
    full_prompt = f"SYSTEM RULES:\n{rules}\n\nUSER REQUEST:\n{user_request}"

    try:
        response = await model.generate_content_async(full_prompt)
        feedback = response.text
    except Exception as e:
        print(f"Reviewer Error: {e}")
        feedback = "APPROVED"

    return {
        "review_feedback": feedback,
        "status": "auditing",
        "current_agent": "Reviewer",
    }


async def tester_node(state: AgentState) -> AgentState:
    print("--- Tester Active ---")
    active_file = state.get("active_file", "")
    code = get_file(state, active_file) if active_file else ""
    lang = state.get("language", "Python")

    new_state: AgentState = {
        "current_agent": "Tester",
        "status": "testing",
        "error_logs": state.get("error_logs", ""),
    }

    if lang.lower() == "python" and code:
        output = CodeRunner.run_with_timeout(code)
        new_state["error_logs"] = output
    else:
        if not code:
            output = "PASS"
        else:
            await asyncio.sleep(2)
            model = get_agent_model()
            rules = get_system_rules("Tester")
            user_request = (
                f"Check this {lang} code for syntax errors. Reply 'PASS' or list errors.\n"
                f"FILE: {active_file}\n{code}"
            )
            full_prompt = f"SYSTEM RULES:\n{rules}\n\nUSER REQUEST:\n{user_request}"
            try:
                res = await model.generate_content_async(full_prompt)
                output = res.text
            except Exception as e:
                print(f"Tester Error: {e}")
                output = "PASS"

    if "PASS" in output.upper() or "EXECUTION PASSED" in output.upper():
        new_state["status"] = "completed"
    else:
        new_state["status"] = "failed"

    new_state["test_result"] = output
    return new_state
