from langgraph.graph import StateGraph, END
from state import AgentState
from nodes import supervisor_node, developer_node, reviewer_node, tester_node

def create_workflow():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("Supervisor", supervisor_node)
    workflow.add_node("Developer", developer_node)
    workflow.add_node("Reviewer", reviewer_node)
    workflow.add_node("Tester", tester_node)
    
    workflow.set_entry_point("Supervisor")
    workflow.add_edge("Supervisor", "Developer")
    workflow.add_edge("Developer", "Reviewer")
    
    def check_review(state):
        fb = state.get("review_feedback", "").upper()
        
        if "APPROVED" in fb or state.get("iteration_count", 0) >= 2:
            return "Tester"
        return "Developer"
            
    def check_test(state):
        res = state.get("test_result", "").upper()
       
        if "PASS" in res or "SUCCESSFULLY" in res or state.get("iteration_count", 0) >= 3:
            return END
        return "Developer"

    workflow.add_conditional_edges("Reviewer", check_review)
    workflow.add_conditional_edges("Tester", check_test)
    
    return workflow.compile()