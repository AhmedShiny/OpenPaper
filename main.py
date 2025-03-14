from dotenv import load_dotenv
import os
import asyncio
import traceback

# Load environment variables
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Import from our modules
from models import ReportState
from workflow import create_research_paper_workflow
from pdf_generator import save_report_as_pdf

async def run_research_paper_workflow(topic):
    """Run the research paper generation workflow"""
    # Create the research paper workflow
    research_workflow = create_research_paper_workflow()
    
    # Initialize the state
    initial_state = {
        "system_prompt": f"Generate a research paper about {topic}",
        "topic": topic,
        "outline": "",
        "draft": "",
        "sources": [],
        "intermediate_steps": ["Started workflow"],
        "research_results": [],
        "score": []
    }
    
    # Run the workflow
    print(f"Starting research paper generation on: {topic}")
    try:
        result = await research_workflow.ainvoke(initial_state)
        
        # Print the results
        print("\n=== RESEARCH PAPER GENERATION COMPLETE ===")
        print(f"\nTOPIC: {result['topic']}")
        print("\nOUTLINE:")
        print(result['outline'])
        print("\nDRAFT:")
        print(result['draft'])
        print("\nSOURCES:")
        for source in result['sources']:
            print(f"- {source}")
        
        # Save the report as PDF
        save_report_as_pdf(result)
        
        return result
    except Exception as e:
        print(f"An error occurred in the research workflow: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        return None

async def main(topic):
    """Main function to run the research paper workflow"""
    await run_research_paper_workflow(topic)

if __name__ == "__main__":
    # Allow user to input their research topic
    print("Enter a research topic (or press Enter for default):")
    user_input = input("> ").strip()
    topic = user_input if user_input else "Making Diffusion Models Better"
        
    asyncio.run(main(topic))