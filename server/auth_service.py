import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from config import SCOPES, CREDENTIALS_FILE, TOKEN_FILE, OAUTH_PORT


class GoogleAuthService:
    """Service for handling Google OAuth authentication."""
    
    def __init__(self):
        self.scopes = SCOPES
        self.credentials_file = CREDENTIALS_FILE
        self.token_file = TOKEN_FILE
        self.oauth_port = OAUTH_PORT
    
    def get_access_token(self) -> Credentials:
        """
        Get valid Google OAuth credentials.
        
        Returns:
            Credentials: Valid Google OAuth credentials
        """
        creds = None
        
        # Load existing credentials if available
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
        
        # If credentials are not valid, refresh or get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    creds = self._get_new_credentials()
            else:
                creds = self._get_new_credentials()
            
            # Save the credentials for future use
            self._save_credentials(creds)
        
        return creds
    
    def _get_new_credentials(self) -> Credentials:
        """Get new credentials through OAuth flow."""
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"Credentials file '{self.credentials_file}' not found. "
                "Please download it from Google Cloud Console."
            )
        
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_file, 
            self.scopes
        )
        creds = flow.run_local_server(port=self.oauth_port)
        return creds
    
    def _save_credentials(self, creds: Credentials):
        """Save credentials to token file."""
        with open(self.token_file, "w") as token:
            token.write(creds.to_json())
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        try:
            creds = self.get_access_token()
            return creds and creds.valid
        except Exception:
            return False