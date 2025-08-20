import os
import inspect
from typing import Callable, TypeVar, List
from dotenv import load_dotenv

import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
from streamlit.delta_generator import DeltaGenerator

from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from toolbox_langchain import ToolboxClient

# Load environment variables
load_dotenv()

# Initialize tools from Toolbox server and memory
toolbox_client = ToolboxClient("http://127.0.0.1:5000")
tools = toolbox_client.load_toolset()
memory = MemorySaver()

# System prompt for the investment research assistant
SYSTEM_PROMPT = """
You are a helpful investment research assistant. Use the provided tools to search for companies, 
people, industries, and news articles from 2023. Leverage prior tool outputs and conversation memory 
to look up entities by ID or filter by attributes like location or sentiment. Use detailed tool outputs 
for filtering or sorting as needed. Do not ask for user confirmations.
"""

# Predefined queries for the dropdown
QUERIES = [
    "What industries deal with neurological implants?",
    "List 5 companies in those industries with descriptions, filtered by California.",
    "Who is working at these companies?",
    "What were the news articles in January 2023 with positive sentiment? List top 5.",
    "Summarize these articles.",
    "Which 3 companies were mentioned in these articles?",
    "Who are the board members at these companies?",
]

# Validate API key
def ensure_api_key() -> None:
    """Ensures GEMINI_API_KEY is set, prompting user input if missing."""
    if not os.getenv("GEMINI_API_KEY"):
        st.sidebar.header("GEMINI_API_KEY Setup")
        api_key = st.sidebar.text_input(
            label="API Key", type="password", label_visibility="collapsed"
        )
        if not api_key:
            st.info("Please enter your GEMINI_API_KEY in the sidebar.")
            st.stop()
        os.environ["GEMINI_API_KEY"] = api_key

# Initialize LLM
def initialize_llm() -> ChatOpenAI:
    """Initializes and returns the ChatOpenAI model with Gemini configuration."""
    return ChatOpenAI(
        model="gemini-2.5-flash",
        api_key=os.environ["GEMINI_API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

def get_streamlit_callback(parent_container: DeltaGenerator) -> BaseCallbackHandler:
    """
    Creates a Streamlit callback handler for LangChain integration, ensuring all callback methods
    run within the Streamlit execution context to avoid NoSessionContext errors.

    Args:
        container (DeltaGenerator): Streamlit container for rendering LLM outputs.

    Returns:
        BaseCallbackHandler: Configured StreamlitCallbackHandler with context-aware methods.
    """
    T = TypeVar('T')

    # Decorator function to add Streamlit's execution context to a function
    def add_context(fn: Callable[..., T]) -> Callable[..., T]:
        """Decorator to add Streamlit execution context to a function."""
        ctx = get_script_run_ctx()
        def wrapper(*args, **kwargs) -> T:
            add_script_run_ctx(ctx=ctx)
            return fn(*args, **kwargs)
        return wrapper

    # Create an instance of Streamlit's StreamlitCallbackHandler with the provided Streamlit container
    callback = StreamlitCallbackHandler(parent_container)

    # Iterate over all methods of the StreamlitCallbackHandler instance
    for name, method in inspect.getmembers(callback, predicate=inspect.ismethod):
        if name.startswith('on_'):  # Identify callback methods that respond to LLM events
            # Wrap each callback method with the Streamlit context setup to prevent session errors
            setattr(callback, name, add_context(method))

    # Return the fully configured StreamlitCallbackHandler instance, now context-aware and integrated with any ChatLLM
    return callback

def create_agent():
    """Creates and configures the LangGraph agent with memory and tools."""
    llm = initialize_llm()
    return create_react_agent(llm, tools, checkpointer=memory)

# Function to invoke the compiled graph externally
def invoke_agent(messages: List, callbacks: List, thread_id: str) -> dict:
    """
    Invoke the LangGraph agent with messages, callbacks, and thread ID.

    Args:
        messages (List): List of messages to pass to the graph.
        callbacks (List): List of callback handlers for the graph.
        thread_id (str): Thread ID for conversation persistence.
    Returns:
        dict: The response from the graph invocation.
    """
    if not isinstance(callbacks, list):
        raise TypeError("Callbacks must be a list")
    agent = create_agent()
    # Invoke the graph with the current messages and callback configuration
    return agent.invoke(
        {"messages": messages},
        stream_mode="values",
        config={"configurable": {"thread_id": thread_id}, "callbacks": callbacks}
    )

# Streamlit app setup
st.set_page_config(page_title="Investment Research Agent")
st.title("💼 Investment Research Agent")
st.markdown("### 🧠 LangGraph 🔗 Gen AI Toolbox 📊 Neo4j ⚙️ Streamlit")

# Ensure API key is set
ensure_api_key()

if "messages" not in st.session_state:
    # default initial message to render in message state
    st.session_state["messages"] = [
        SystemMessage(content=SYSTEM_PROMPT),
        AIMessage(content="How can I help you? You can research companies, articles, people.")
    ]
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = "thread-1"

# Reset conversation button
if st.button("Start New Conversation"):
    st.session_state["messages"] = [
        SystemMessage(content=SYSTEM_PROMPT),
        AIMessage(content="How can I help you? You can research companies, articles, people.")
    ]
    st.session_state["thread_id"] = f"thread-{len(st.session_state.get('threads', [])) + 1}"
    st.session_state["threads"] = st.session_state.get("threads", []) + [st.session_state["thread_id"]]

# Display messages
for msg in st.session_state.messages:
    # https://docs.streamlit.io/develop/api-reference/chat/st.chat_message
    # we store them as AIMessage and HumanMessage as its easier to send to LangGraph
    if isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)
    elif isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)

# UI: Dropdown or text input
question = st.selectbox("Questions", QUERIES, index=None, placeholder="Possible questions", label_visibility="hidden")
prompt = st.chat_input(placeholder="Ask a question or select one above")
prompt = question or prompt

if prompt:
    st.session_state.messages.append(HumanMessage(content=prompt))
    st.chat_message("user").write(prompt)

    # Process the AI's response and handles graph events using the callback mechanism
    with st.chat_message("assistant"):
        placeholder = st.empty()
        callback = get_streamlit_callback(placeholder)
        response = invoke_agent(st.session_state.messages, [callback], st.session_state["thread_id"])
        last_message = response["messages"][-1].content
        st.session_state.messages.append(AIMessage(content=last_message))
        placeholder.write(last_message)
