from typing import TypedDict, List, Dict

class AgentState(TypedDict):
    task: str
    language: str
    files: Dict[str, str]  # VFS: maps relative file paths to content
    active_file: str       # Currently edited/previewed file
    task_plan: List[str]   # Ordered steps from Supervisor
    error_logs: str        # Compiler/lint/runtime output
    iteration_count: int   # Loop cycles between agents
    current_agent: str     # Active node name
    status: str            # 'planning', 'coding', 'auditing', 'testing', 'completed', 'failed'
    conversation_history: List[str]
    review_feedback: str
    test_result: str


def get_file(state: AgentState, path: str) -> str:
    """Read a file from the VFS. Returns empty string if missing."""
    files = state.get("files", {})
    return files.get(path, "")


def set_file(state: AgentState, path: str, content: str) -> AgentState:
    """Write a file into the VFS. Returns a new state dict (immutable-safe)."""
    files = dict(state.get("files", {}))
    files[path] = content
    new_state = dict(state)
    new_state["files"] = files
    return new_state


def delete_file(state: AgentState, path: str) -> AgentState:
    """Remove a file from the VFS. Clears active_file if it matches. Returns a new state dict."""
    files = dict(state.get("files", {}))
    files.pop(path, None)
    new_state = dict(state)
    new_state["files"] = files
    if state.get("active_file") == path:
        new_state["active_file"] = ""
    return new_state


def list_files(state: AgentState) -> List[str]:
    """Return sorted list of all file paths in the VFS."""
    return sorted(state.get("files", {}).keys())


def get_active_file(state: AgentState) -> str:
    """Return the currently active file path, or empty string."""
    return state.get("active_file", "")