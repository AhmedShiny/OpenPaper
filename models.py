from typing import TypedDict, List, Dict, Any

# Define the state for our research paper workflow
class ReportState(TypedDict):
    system_prompt: str
    topic: str
    outline: str
    draft: str
    sources: List[str]
    intermediate_steps: List[str]
    research_results: List[Dict[str, Any]]
    score: List[Any]