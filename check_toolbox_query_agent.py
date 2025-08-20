import asyncio
import os
from typing import Dict

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

from toolbox_langchain import ToolboxClient
from dotenv import load_dotenv

load_dotenv(".env")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


SYSTEM_PROMPT = """
You are an investment research assistant. Use the provided tools to search for companies, 
people, industries, and news articles from 2023. Leverage prior tool outputs to filter results 
(e.g., by location or sentiment) or as inputs for subsequent queries. Fetch detailed information 
when needed for filtering or sorting. Do not ask for user confirmations.
"""

QUERIES = [
    "What industries deal with neurological implants?",
    "List 5 companies in those industries with their description and filter afterwards by California.",
    "Who is working at these companies?",
    "What were the news in January 2023 with positive sentiment? List top 5 articles.",
    "Summarize these articles.",
    "Which 3 companies were mentioned by these articles?",
    "Who is working there as board members?",
]

async def run_agent_query(agent, query: str, config: Dict) -> str:
    """Run a single query through the agent and return the response."""
    inputs = {"messages": [("user", SYSTEM_PROMPT + query)]}
    response = await agent.ainvoke(inputs, stream_mode="values", config=config)
    return response["messages"][-1].content

async def main():
    """Main function to initialize the agent and process queries."""
    try:
        # Initialize the model
        model = ChatOpenAI(model="gemini-2.5-flash", 
                           api_key=GEMINI_API_KEY, 
                           base_url=GEMINI_BASE_URL)

        # Load tools from the Toolbox server
        client = ToolboxClient("http://127.0.0.1:5000")
        tools = client.load_toolset()

        # Set up memory and agent
        memory = MemorySaver()
        agent = create_react_agent(model, tools, checkpointer=memory)
        config = {"configurable": {"thread_id": "thread-1"}}

        # Process each query
        for query in QUERIES:
            print(f"\n{query}:\n")
            response = await run_agent_query(agent, query, config)
            print(f"> {response}")
            print("------------------------------------")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
