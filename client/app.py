import streamlit as st
import requests
import json
from datetime import datetime
import time
import uuid
from dotenv import load_dotenv
import os

# Page configuration
st.set_page_config(
    page_title="Calendar Assistant",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }

    .chat-message {
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        border-radius: 15px;
        max-width: 80%;
        line-height: 1.5;
        font-size: 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        word-wrap: break-word;
    }

    .user-message {
        background-color: #dcf8c6;
        margin-left: auto;
        text-align: right;
        color: #000;
    }

    .assistant-message {
        background-color: #f1f0f0;
        margin-right: auto;
        text-align: left;
        color: #000;
    }

    .status-indicator {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
    }

    .status-connected {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }

    .status-disconnected {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# Load environment variables from .env file
load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL")

if not API_BASE_URL:
    st.error("⚠️ API_BASE_URL is not set in the .env file.")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "api_connected" not in st.session_state:
    st.session_state.api_connected = False

# Functions
def check_api_connection():
    """Check if the API is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_message(message: str, thread_id: str):
    """Send message to the API"""
    try:
        payload = {
            "message": message,
            "thread_id": thread_id
        }
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}"}
    except requests.exceptions.Timeout:
        return {"error": "Request timeout. The assistant might be processing your request."}
    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}

def get_api_status():
    """Get API status information"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"error": "API not responding"}
    except:
        return {"error": "Cannot connect to API"}

# Header
st.markdown('<div class="main-header">📅 Calendar Assistant</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Configuration")
    
    # API Status
    st.subheader("API Status")
    if st.button("Check Connection"):
        st.session_state.api_connected = check_api_connection()
    
    if st.session_state.api_connected:
        st.markdown('<div class="status-indicator status-connected">✅ Connected</div>', unsafe_allow_html=True)
        
        # Get API info
        api_info = get_api_status()
        if "error" not in api_info:
            st.info(f"**Current Date:** {api_info.get('current_date', 'N/A')}")
            st.info(f"**Current Time:** {api_info.get('current_time', 'N/A')}")
    else:
        st.markdown('<div class="status-indicator status-disconnected">❌ Disconnected</div>', unsafe_allow_html=True)
        st.error("Make sure the FastAPI server is running on http://localhost:8001")
    
    # Thread Management
    st.subheader("Session Management")
    st.text(f"Thread ID: {st.session_state.thread_id[:8]}...")
    
    if st.button("New Session"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    # Instructions
    st.subheader("How to Use")
    st.markdown("""
    **Calendar Assistant can help you:**
    - Create new calendar events
    - Check your availability
    - Update existing events
    - Answer schedule questions
    
    **Example commands:**
    - "Schedule a meeting tomorrow at 2 PM"
    - "What's my schedule for today?"
    - "Cancel my 3 PM meeting"
    - "Check if I'm free at 10 AM on Friday"
    """)

# Main chat interface
st.header("Chat with your Calendar Assistant")

# Check API connection on startup
if not st.session_state.api_connected:
    st.session_state.api_connected = check_api_connection()

if not st.session_state.api_connected:
    st.warning("⚠️ Cannot connect to the Calendar Assistant API. Please make sure the FastAPI server is running.")
    st.code("python fastapi_server.py", language="bash")

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>Assistant:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)


# --- START OF CHANGES ---

# 1. New callback function to handle sending the message and clearing the input.
def handle_send_click():
    """Handles the logic when the send button is clicked."""
    # We check if the input is not empty before processing.
    if st.session_state.user_input:
        user_message = st.session_state.user_input
        
        # Add user message to chat history
        st.session_state.messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Show a spinner while the assistant is thinking
        with st.spinner("Calendar Assistant is thinking..."):
            # Send message to API
            response = send_message(user_message, st.session_state.thread_id)
        
        # Handle the API response
        if "error" in response:
            st.error(f"Error: {response['error']}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Sorry, I encountered an error: {response['error']}"
            })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["response"]
            })
        
        # 2. This is the key change: Clearing the input by setting its session state value.
        # This is allowed within a callback function like this one.
        st.session_state.user_input = ""


# Chat input and send button
if st.session_state.api_connected:
    # Use columns for better layout
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # 3. We use `on_change` to trigger the callback when the user presses Enter.
        #    The `key` parameter is used to link the widget to its session state value.
        st.text_input(
            "Type your message:",
            key="user_input",
            placeholder="Ask me about your calendar...",
            label_visibility="collapsed",
            on_change=handle_send_click  
        )
    
    with col2:
        # 4. We use `on_click` to trigger the callback when the user clicks the Send button.
        st.button("Send", type="primary", use_container_width=True, on_click=handle_send_click)

    # 5. The old message sending logic is removed because it's now handled by the callback.
    #    The block 'if (send_button or user_input) and user_input.strip():' is gone.

else:
    st.text_input(
        "Type your message:",
        disabled=True,
        placeholder="Connect to API first...",
        label_visibility="collapsed"
    )

# --- END OF CHANGES ---


# Quick action buttons
if st.session_state.api_connected:
    st.subheader("Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    quick_actions = [
        "What's my schedule for today?",
        "What meetings do I have this week?",
        "Am I free at 2 PM today?",
        "Show me my calendar for tomorrow"
    ]
    
    for i, action in enumerate(quick_actions):
        with [col1, col2, col3, col4][i]:
            if st.button(action, key=f"quick_action_{i}"):
                # Add message and get response
                st.session_state.messages.append({
                    "role": "user",
                    "content": action
                })
                
                with st.spinner("Processing..."):
                    response = send_message(action, st.session_state.thread_id)
                
                if "error" not in response:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["response"]
                    })
                
                st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Calendar Assistant powered by LangGraph and Google Calendar API"
    "</div>",
    unsafe_allow_html=True
)