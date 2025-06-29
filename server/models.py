from pydantic import BaseModel, Field
from typing import Optional


class ChatMessage(BaseModel):
    """Model for incoming chat messages."""
    message: str = Field(..., description="The user's message")
    thread_id: str = Field(default="1", description="Conversation thread ID")


class ChatResponse(BaseModel):
    """Model for chat responses."""
    response: str = Field(..., description="The assistant's response")
    thread_id: str = Field(..., description="Conversation thread ID")


class HealthResponse(BaseModel):
    """Model for health check responses."""
    status: str = Field(..., description="Health status")
    initialized: bool = Field(..., description="Whether the system is initialized")


class StatusResponse(BaseModel):
    """Model for detailed status responses."""
    ready: bool = Field(..., description="Whether the system is ready")
    authenticated: bool = Field(..., description="Whether authenticated with Google")
    current_date: str = Field(..., description="Current date")
    current_time: str = Field(..., description="Current time")
    llm_initialized: bool = Field(..., description="Whether LLM is initialized")
    graph_built: bool = Field(..., description="Whether the graph is built")


class ErrorResponse(BaseModel):
    """Model for error responses."""
    detail: str = Field(..., description="Error detail message")
    error_type: Optional[str] = Field(None, description="Type of error")