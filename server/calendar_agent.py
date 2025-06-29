import os
from typing import Annotated
from typing_extensions import TypedDict
from datetime import datetime

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI

from calendar_service import CalendarService
from config import GOOGLE_API_KEY


class State(TypedDict):
    """State definition for the calendar agent."""
    messages: Annotated[list, add_messages]


class CalendarAgent:
    """Calendar booking agent with LangGraph integration."""
    
    def __init__(self):
        self.calendar_service = CalendarService()
        self.memory = MemorySaver()
        self.llm = None
        self.graph = None
        self._setup_llm()
        self._build_graph()
    
    def _setup_llm(self):
        """Setup the language model with Google AI."""
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    
    def _get_system_prompt(self) -> str:
        """Generate the system prompt with current date and time."""
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        current_time = datetime.now().strftime("%I:%M %p")
        
        return f"""You are a helpful calendar assistant. Today's date is {current_date} and the current time is {current_time}. 

When users ask about scheduling events, meetings, or calendar-related tasks, always consider this current date and time context. You can help users:

- Important Thing: when creating a meeting, check first if there is already a meeting scheduled. If so, ask the user if they want to delete the existing meeting or schedule it at another time.
- Create new calendar events
- Check their calendar for availability
- Update or modify existing events
- Answer questions about their schedule

Always be precise with dates and times, and ask for clarification if the user's request is ambiguous about timing."""
    
    def _chatbot_node(self, state: State):
        """Main chatbot node that processes messages."""
        messages = state["messages"]
        
        # Check if system message exists
        has_system_message = any(
            msg.get("role") == "system" 
            for msg in messages 
            if hasattr(msg, 'get') or isinstance(msg, dict)
        )
        
        # Add system message if not present
        if not has_system_message:
            system_message = {"role": "system", "content": self._get_system_prompt()}
            messages_with_system = [system_message] + messages
        else:
            messages_with_system = messages
        
        # Get tools and bind to LLM
        tools = self.calendar_service.get_calendar_tools()
        llm_with_tools = self.llm.bind_tools(tools)
        
        # Invoke the LLM
        response = llm_with_tools.invoke(messages_with_system)
        return {"messages": [response]}
    
    def _build_graph(self):
        """Build the LangGraph workflow."""
        # Get calendar tools
        tools = self.calendar_service.get_calendar_tools()
        
        # Build the graph
        graph_builder = StateGraph(State)
        graph_builder.add_node("chatbot", self._chatbot_node)
        
        # Add tool node
        tool_node = ToolNode(tools)
        graph_builder.add_node("tools", tool_node)
        
        # Add edges
        graph_builder.add_conditional_edges("chatbot", tools_condition)
        graph_builder.add_edge("tools", "chatbot")
        graph_builder.add_edge(START, "chatbot")
        
        # Compile the graph
        self.graph = graph_builder.compile(checkpointer=self.memory)
    
    def process_message(self, message: str, thread_id: str = "1") -> str:
        """
        Process a user message and return the assistant's response.
        
        Args:
            message: User's message
            thread_id: Conversation thread ID
            
        Returns:
            Assistant's response
        """
        if not self.graph:
            raise RuntimeError("Calendar agent not properly initialized")
        
        config = {"configurable": {"thread_id": thread_id}}
        
        # Stream the graph updates
        events = self.graph.stream(
            {"messages": [{"role": "user", "content": message}]},
            config,
            stream_mode="values",
        )
        
        # Get the last response
        last_response = None
        for event in events:
            if "messages" in event and event["messages"]:
                last_message = event["messages"][-1]
                if hasattr(last_message, 'content'):
                    last_response = last_message.content
                elif isinstance(last_message, dict) and 'content' in last_message:
                    last_response = last_message['content']
        
        if last_response is None:
            last_response = "I'm sorry, I couldn't process your request. Please try again."
        
        return last_response
    
    def is_ready(self) -> bool:
        """Check if the agent is ready to process requests."""
        return (
            self.calendar_service.is_ready() and 
            self.llm is not None and 
            self.graph is not None
        )
    
    def get_status(self) -> dict:
        """Get the current status of the agent."""
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        current_time = datetime.now().strftime("%I:%M %p")
        
        return {
            "ready": self.is_ready(),
            "authenticated": self.calendar_service.is_ready(),
            "current_date": current_date,
            "current_time": current_time,
            "llm_initialized": self.llm is not None,
            "graph_built": self.graph is not None
        }