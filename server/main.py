from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from calendar_agent import CalendarAgent
from models import ChatMessage, ChatResponse, HealthResponse, StatusResponse
from config import (
    API_HOST, API_PORT, CORS_ORIGINS, CORS_ALLOW_CREDENTIALS, 
    CORS_ALLOW_METHODS, CORS_ALLOW_HEADERS
)


# Global state
app_state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("Initializing Calendar Assistant...")
    
    try:
        # Initialize the calendar agent
        calendar_agent = CalendarAgent()
        app_state["calendar_agent"] = calendar_agent
        
        # Get initial status
        status = calendar_agent.get_status()
        print(f"Calendar Assistant initialized. Today is {status['current_date']}")
        print(f"Ready: {status['ready']}, Authenticated: {status['authenticated']}")
        
    except Exception as e:
        print(f"Error initializing Calendar Assistant: {e}")
        # Still start the app, but mark as not ready
        app_state["calendar_agent"] = None
        app_state["initialization_error"] = str(e)
    
    yield
    
    # Shutdown
    print("Shutting down Calendar Assistant...")
    app_state.clear()


# Create FastAPI app
app = FastAPI(
    title="Calendar Assistant API",
    description="AI-powered calendar assistant with Google Calendar integration",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)


@app.get("/")
async def root():
    """Root endpoint with basic information."""
    calendar_agent = app_state.get("calendar_agent")
    
    if calendar_agent:
        status = calendar_agent.get_status()
        return {
            "message": "Calendar Assistant API",
            "version": "1.0.0",
            "current_date": status["current_date"],
            "current_time": status["current_time"],
            "ready": status["ready"]
        }
    else:
        error = app_state.get("initialization_error", "Unknown initialization error")
        return {
            "message": "Calendar Assistant API",
            "version": "1.0.0",
            "status": "initialization_failed",
            "error": error
        }


@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Chat endpoint for interacting with the calendar assistant."""
    calendar_agent = app_state.get("calendar_agent")
    
    if not calendar_agent:
        error_msg = app_state.get("initialization_error", "Calendar Assistant not initialized")
        raise HTTPException(status_code=500, detail=error_msg)
    
    if not calendar_agent.is_ready():
        raise HTTPException(
            status_code=503, 
            detail="Calendar Assistant is not ready. Please check authentication."
        )
    
    try:
        response = calendar_agent.process_message(
            message.message, 
            message.thread_id
        )
        
        return ChatResponse(
            response=response, 
            thread_id=message.thread_id
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing message: {str(e)}"
        )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    calendar_agent = app_state.get("calendar_agent")
    return HealthResponse(
        status="healthy" if calendar_agent and calendar_agent.is_ready() else "unhealthy",
        initialized=calendar_agent is not None
    )


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Detailed status endpoint."""
    calendar_agent = app_state.get("calendar_agent")
    
    if calendar_agent:
        status = calendar_agent.get_status()
        return StatusResponse(**status)
    else:
        # Return default status when not initialized
        from datetime import datetime
        return StatusResponse(
            ready=False,
            authenticated=False,
            current_date=datetime.now().strftime("%A, %B %d, %Y"),
            current_time=datetime.now().strftime("%I:%M %p"),
            llm_initialized=False,
            graph_built=False
        )


@app.post("/refresh")
async def refresh_agent():
    """Refresh the calendar agent (useful after authentication issues)."""
    try:
        print("Refreshing Calendar Assistant...")
        calendar_agent = CalendarAgent()
        app_state["calendar_agent"] = calendar_agent
        
        status = calendar_agent.get_status()
        return {
            "message": "Calendar Assistant refreshed successfully",
            "status": status
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error refreshing Calendar Assistant: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=API_HOST, 
        port=API_PORT,
    )