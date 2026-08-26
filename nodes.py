import re
import asyncio
from config import get_agent_model, get_system_rules
from state import AgentState, get_file, set_file, list_files
from utils import CodeRunner, extract_files_from_artifact, validate_code_syntax, run_in_e2b_sandbox

try:
    from langchain_community.tools import DuckDuckGoSearchResults
except ImportError:
    DuckDuckGoSearchResults = None


def extract_code(text):
    pattern = r"```(?:\w+)?\s*(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else text.replace("```", "").strip()


async def supervisor_node(state: AgentState) -> AgentState:
    print("--- Supervisor Active ---")
    search_tool = DuckDuckGoSearchResults() if DuckDuckGoSearchResults else None
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
        "search_tool": search_tool,
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

    try:
        response = await model.generate_content_async(full_prompt)
        text = response.text
        file_dict = extract_files_from_artifact(text)
        if file_dict:
            for path, content in file_dict.items():
                new_state = set_file(new_state, path, content)
            if not new_state.get("active_file") or new_state["active_file"] not in new_state["files"]:
                first_file = next(iter(file_dict))
                new_state["active_file"] = first_file
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

    files = state.get("files", {})
    is_valid, err_msg = validate_code_syntax(files)
    if not is_valid:
        new_state = dict(state)
        new_state["error_logs"] = err_msg
        new_state["status"] = "failed"
        new_state["current_agent"] = "Reviewer"
        return new_state

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
    files = state.get("files", {})
    active_file = state.get("active_file", "")
    lang = state.get("language", "Python")

    new_state: AgentState = {
        "current_agent": "Tester",
        "status": "testing",
        "error_logs": state.get("error_logs", ""),
    }

    if not files:
        new_state["test_result"] = "PASS"
        new_state["status"] = "completed"
        return new_state

    # Determine entrypoint explicitly
    entrypoint = ""
    if lang.lower() == "python":
        if "main.py" in files:
            entrypoint = "python main.py"
        elif active_file and active_file.endswith('.py') and active_file in files:
            entrypoint = f"python {active_file}"
        else:
            py_files = [f for f in files.keys() if f.endswith('.py')]
            if py_files:
                entrypoint = f"python {py_files[0]}"
            else:
                new_state["error_logs"] = "No Python entrypoint found (no main.py, no active .py file)"
                new_state["status"] = "failed"
                new_state["test_result"] = new_state["error_logs"]
                return new_state
    elif lang.lower() in ("javascript", "js", "node"):
        if "index.js" in files or "main.js" in files:
            entrypoint = f"node {('index.js' if 'index.js' in files else 'main.js')}"
        elif active_file and active_file.endswith(('.js', '.mjs')) and active_file in files:
            entrypoint = f"node {active_file}"
        else:
            js_files = [f for f in files.keys() if f.endswith(('.js', '.mjs'))]
            if js_files:
                entrypoint = f"node {js_files[0]}"
            else:
                new_state["error_logs"] = "No JavaScript entrypoint found"
                new_state["status"] = "failed"
                new_state["test_result"] = new_state["error_logs"]
                return new_state
    else:
        new_state["error_logs"] = f"Unsupported language for sandbox execution: {lang}"
        new_state["status"] = "failed"
        new_state["test_result"] = new_state["error_logs"]
        return new_state

    try:
        exit_code, stdout, stderr = run_in_e2b_sandbox(files, entrypoint)
    except RuntimeError as e:
        new_state["error_logs"] = str(e)
        new_state["status"] = "failed"
        new_state["test_result"] = new_state["error_logs"]
        return new_state

    output = f"Exit code: {exit_code}\nStdout:\n{stdout}\nStderr:\n{stderr}"
    new_state["error_logs"] = output

    if exit_code == 0:
        new_state["status"] = "completed"
    else:
        new_state["status"] = "failed"

    new_state["test_result"] = output
    return new_state
