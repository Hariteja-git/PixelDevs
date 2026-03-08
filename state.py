from typing import TypedDict, List

class AgentState(TypedDict):
    task: str
    language: str              
    code: str
    review_feedback: str
    test_result: str
    conversation_history: List[str]
    iteration_count: int
    current_status: str