import os
import json
import asyncio
import re
from typing import List, Dict, Any
from tavily import TavilyClient
from browser_use import Agent
from langchain.tools import Tool

# Import the LLM models that will be used for research
from langchain_groq import ChatGroq

# Initialize LLM models
llm = ChatGroq(model="deepseek-r1-distill-llama-70b", reasoning_format="hidden")
llm1 = ChatGroq(model="deepseek-r1-distill-llama-70b", reasoning_format="hidden")

# Create a function that will use the browser agent
async def use_browser_search(query):
    agent = Agent(
        task=query,
        llm=llm,
    )
    result = await agent.run()
    return result

# Create a tool that wraps the browser search functionality
browser_search = Tool(
    name="browser_search",
    description="Search the web for information using a browser",
    func=lambda query: asyncio.run(use_browser_search(query))
)

# Function to perform research using Tavily
def TavilyResearcher(question: str) -> List[Dict[str, Any]]:
    """
    This function performs a search using Tavily and returns the results as a list of dictionaries.
    """
    try:
        tavily = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
        print(f"Using Tavily API key: ")  # Print first few chars for debugging
        
        # Get keywords from the question
        result = llm1.invoke(f"Shorten the provided idea to only include a few keywords related to it : only return a few keywords to search for and nothing else. Idea is : {question}")
        keywords = result.content
        print(f"Search keywords: {keywords}")
        
        # For advanced search with simplified parameters
        response = tavily.search(
            query=keywords,
            search_depth="basic",  # Try basic first to ensure it works
            max_results=5  # Reduce to minimize potential issues
        )
        
        # Get the search results as context
        context = [{"url": obj["url"], "content": obj["content"]} for obj in response["results"]]
        return context
    except Exception as e:
        print(f"Tavily search error: {type(e).__name__}: {str(e)}")
        # Return empty results on error so the workflow can continue
        return [{"url": "error", "content": f"Error performing Tavily search: {str(e)}. Continuing with browser search only."}]

# Function to perform research using browser search
async def async_browser_search(query, item, i):
    """Run a single browser search asynchronously"""
    try:
        print(f"\nStarting research task {i+1}: {item}")
        item_results = await use_browser_search(query)
        
        # Process results
        result = {
            "content": str(item_results),
            "url": f"browser_search_result_{i+1}",
            "outline_item": item
        }
        
        # Try to parse JSON if possible
        if isinstance(item_results, str):
            try:
                parsed_results = json.loads(item_results)
                if isinstance(parsed_results, list):
                    for r in parsed_results:
                        r['outline_item'] = item
                    return parsed_results
            except json.JSONDecodeError:
                pass
        
        print(f"Completed research task {i+1}: {item}")
        return [result]
    except Exception as e:
        print(f"Error researching outline item {i+1}: {str(e)}")
        return [{
            "content": f"Error researching: {str(e)}",
            "url": f"browser_search_error_{i+1}",
            "outline_item": item
        }]

async def gather_results(tasks):
    """Gather results from multiple async tasks"""
    return await asyncio.gather(*tasks)

def Researcher(query):
    """Use Tavily for initial research and browser search for detailed information"""
    # First use Tavily to get initial research
    tavily_results = TavilyResearcher(query)
    
    # Generate an outline based on Tavily results
    outline_content = ""
    for result in tavily_results[:3]:  # Use first 3 results for brevity
        outline_content += result["content"] + "\n\n"
    
    outline_prompt = f"""
    Based on this initial research about \"{query}\", create a brief outline of key areas to investigate further.
    {outline_content[:2000]}
    
    List exactly 3-5 specific aspects that need more detailed research. Format your response as a numbered list.
    IMPORTANT: Each item must be a simple, focused search query (5-10 words maximum) that directly relates to {query}.
    For example, if researching AI, good items would be:
    1. AI ethics current challenges
    2. Machine learning latest advancements
    3. Neural networks business applications
    """
    
    outline_response = llm1.invoke(outline_prompt)
    research_outline = outline_response.content
    
    # Parse the outline into separate tasks
    outline_items = []
    for line in research_outline.split('\n'):
        line = line.strip()
        if line and (line[0].isdigit() and line[1:3] in ['. ', '- ', ') ']):
            outline_items.append(line[line.find(' ')+1:])
    
    # If parsing failed, try to split by numbers
    if not outline_items:
        outline_items = re.findall(r'\d+\.\s*(.*?)(?=\d+\.|$)', research_outline, re.DOTALL)
        outline_items = [item.strip() for item in outline_items if item.strip()]
    
    # Ensure we have at least one item
    if not outline_items:
        outline_items = [research_outline]
    
    print(f"Broken down research tasks:")
    for i, item in enumerate(outline_items):
        print(f"{i+1}. {item}")
    
    # Execute browser search for each outline item simultaneously
    combined_results = tavily_results.copy()
    
    # Create search queries for each outline item
    search_tasks = []
    for i, item in enumerate(outline_items):
        search_query = f"Research the following specific aspect of {query}: {item}. Do a brief research in 3 steps at most"
        search_tasks.append(async_browser_search(search_query, item, i))
    
    # Run all searches in parallel and wait for all to complete
    all_results = asyncio.run(gather_results(search_tasks))
    
    # Combine all results
    for result_list in all_results:
        combined_results.extend(result_list)
    
    return combined_results