from langchain_google_community import CalendarToolkit
from langchain_google_community.calendar.utils import build_resource_service
from auth_service import GoogleAuthService


class CalendarService:
    """Service for managing Google Calendar operations."""
    
    def __init__(self):
        self.auth_service = GoogleAuthService()
        self._api_resource = None
        self._tools = None
    
    def _get_api_resource(self):
        """Build and cache the Google Calendar API resource."""
        if self._api_resource is None:
            credentials = self.auth_service.get_access_token()
            self._api_resource = build_resource_service(credentials=credentials)
        return self._api_resource
    
    def get_calendar_tools(self):
        """
        Get the calendar tools for LangChain integration.
        
        Returns:
            List of calendar tools for the LLM to use
        """
        if self._tools is None:
            api_resource = self._get_api_resource()
            toolkit = CalendarToolkit(api_resource=api_resource)
            self._tools = toolkit.get_tools()
        return self._tools
    
    def refresh_tools(self):
        """Refresh the calendar tools (useful after token refresh)."""
        self._api_resource = None
        self._tools = None
        return self.get_calendar_tools()
    
    def is_ready(self) -> bool:
        """Check if the calendar service is ready to use."""
        try:
            return self.auth_service.is_authenticated()
        except Exception:
            return False