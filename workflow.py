from typing import List, Dict, Any
import asyncio
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph

# Import the ReportState model
from models import ReportState

# Import research functionality
from research import Researcher

# Initialize LLM model for content generation
llm1 = ChatGroq(model="deepseek-r1-distill-llama-70b", reasoning_format="hidden")

# Research function for the graph
def research_topic(state: ReportState) -> ReportState:
    """Perform initial research on the topic using Tavily and browser search"""
    search_results = Researcher(f"{state['topic']}")
    # Extract URLs from search results for sources
    sources = []
    for result in search_results:
        if 'url' in result:
            sources.append(result['url'])
    
    return {
        "system_prompt": state["system_prompt"],
        "topic": state["topic"],
        "outline": state["outline"],
        "draft": state["draft"],
        "sources": sources,
        "intermediate_steps": state["intermediate_steps"] + ["Completed initial research"],
        "research_results": search_results,
        "score": state["score"]
    }

# Generate outline function for the graph
def generate_outline(state: ReportState) -> ReportState:
    """Generate an outline for the research paper based on research results"""
    # Prepare the research content for the LLM, but limit the size
    research_content = ""
    total_chars = 0
    char_limit = 4000  
    
    # First prioritize results with outline_item tags (from browser search)
    prioritized_results = []
    other_results = []
    
    for result in state["research_results"]:
        if 'content' in result:
            if 'outline_item' in result:
                prioritized_results.append(result)
            else:
                other_results.append(result)
    
    # Add prioritized results first
    for result in prioritized_results:
        content = result['content']
        # Truncate very long content entries
        if len(content) > 1000:
            content = content[:1000] + "... [content truncated]"
        
        if total_chars + len(content) < char_limit:
            research_content += content + "\n\n"
            total_chars += len(content) + 2
        else:
            break
    
    # Then add other results if there's still room
    for result in other_results:
        content = result['content']
        # Truncate very long content entries
        if len(content) > 500:
            content = content[:500] + "... [content truncated]"
            
        if total_chars + len(content) < char_limit:
            research_content += content + "\n\n"
            total_chars += len(content) + 2
        else:
            break
    
    # Create a prompt for the LLM to generate an outline
    outline_prompt = f"""
    Based on the following research about "{state['topic']}", create a detailed outline for a research paper.
    The outline should include:
    1. Introduction
    2. Main sections with key points
    3. Conclusion
    
    Research information:
    {research_content}
    
    Generate a well-structured outline:
    """
    
    # Use the LLM to generate the outline
    outline_result = llm1.invoke(outline_prompt)
    outline = outline_result.content if hasattr(outline_result, 'content') else str(outline_result)
    
    return {
        "system_prompt": state["system_prompt"],
        "topic": state["topic"],
        "outline": outline,
        "draft": state["draft"],
        "sources": state["sources"],
        "intermediate_steps": state["intermediate_steps"] + ["Generated outline"],
        "research_results": state["research_results"],
        "score": state["score"]
    }

# Generate draft function for the graph
def generate_draft(state: ReportState) -> ReportState:
    """Generate a complete research paper draft based on the outline and research"""
    # Prepare the research content for the LLM, but limit the size
    research_content = ""
    total_chars = 0
    char_limit = 2500  # limit to stay under token limits
    
    # First prioritize results with outline_item tags (from browser search)
    prioritized_results = []
    other_results = []
    
    for result in state["research_results"]:
        if 'content' in result:
            if 'outline_item' in result:
                prioritized_results.append(result)
            else:
                other_results.append(result)
    
    # Add prioritized results first
    for result in prioritized_results:
        content = result['content']
        # Truncate very long content entries
        if len(content) > 500:
            content = content[:500] + "... [content truncated]"
        
        if total_chars + len(content) < char_limit:
            research_content += content + "\n\n"
            total_chars += len(content) + 2
        else:
            break
    
    # Then add other results if there's still room
    for result in other_results:
        content = result['content']
        # Truncate very long content entries
        if len(content) > 300:
            content = content[:300] + "... [content truncated]"
            
        if total_chars + len(content) < char_limit:
            research_content += content + "\n\n"
            total_chars += len(content) + 2
        else:
            break
    
    # Create a prompt for the LLM to generate a draft
    draft_prompt = f"""
    Write a comprehensive research paper on "{state['topic']}" following this outline:
    
    {state['outline']}
    
    Use the following research information:
    {research_content}
    
    Include proper citations to these sources:
    {', '.join(state['sources'][:5])}
    
    The paper should be well-structured, informative, and academically sound.
    """
    
    # Use the LLM to generate the draft
    draft_result = llm1.invoke(draft_prompt)
    draft = draft_result.content if hasattr(draft_result, 'content') else str(draft_result)
    
    return {
        "system_prompt": state["system_prompt"],
        "topic": state["topic"],
        "outline": state["outline"],
        "draft": draft,
        "sources": state["sources"],
        "intermediate_steps": state["intermediate_steps"] + ["Generated draft"],
        "research_results": state["research_results"],
        "score": state["score"]
    }

# Create the research paper workflow graph
def create_research_paper_workflow():
    # Initialize the graph
    workflow = StateGraph(ReportState)
    
    # Add nodes - rename to avoid conflict with state keys
    workflow.add_node("research_node", research_topic)
    workflow.add_node("outline_node", generate_outline)
    workflow.add_node("draft_node", generate_draft)
    
    # Add edges
    workflow.set_entry_point("research_node")
    workflow.add_edge("research_node", "outline_node")
    workflow.add_edge("outline_node", "draft_node")
    
    # Set the final node
    workflow.set_finish_point("draft_node")
    
    return workflow.compile()