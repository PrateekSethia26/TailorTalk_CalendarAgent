# 🗓️ TailorTalk Calendar Agent

> A powerful, modular FastAPI application that brings AI-powered natural language processing to Google Calendar management. Schedule meetings, check availability, and manage your calendar using simple conversational commands.

## ✨ Features

🤖 **AI-Powered Conversations** - Natural language processing with Google's Gemini AI  
📅 **Smart Calendar Management** - Create, update, delete, and query calendar events  
🔐 **Secure Authentication** - Google OAuth 2.0 with automatic token refresh  
💬 **Conversation Memory** - Maintains context across multiple interactions  
🏗️ **Modular Architecture** - Clean, maintainable code structure  
📊 **Comprehensive Monitoring** - Health checks, status reporting, and error handling  
🚀 **Production Ready** - FastAPI with automatic OpenAPI documentation  

## 🎯 What Can It Do?

- **"Schedule a meeting with John tomorrow at 2 PM"**
- **"Do I have any conflicts this Friday afternoon?"**
- **"Move my 3 PM meeting to 4 PM"**
- **"What's on my schedule for next week?"**
- **"Cancel my dentist appointment"**
- **"Find a free slot for a 1-hour meeting this week"**

## 📁 Project Structure

```
calendar-assistant/
├── 🚀 main.py                 # FastAPI application & API endpoints
├── 🤖 calendar_agent.py       # AI agent logic with LangGraph
├── 📅 calendar_service.py     # Google Calendar API operations
├── 🔐 auth_service.py         # OAuth authentication service
├── 📋 models.py              # Pydantic data models
├── ⚙️ config.py              # Configuration management
├── 📦 requirements.txt       # Python dependencies
├── 🌍 .env                   # Environment variables (create this)
├── 🔑 credentials.json       # Google OAuth credentials (download)
└── 🎫 token.json            # OAuth token (auto-generated)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google account with Calendar access
- Google AI API key (from [Google AI Studio](https://makersuite.google.com/app/apikey))

### 1. Clone & Install

```bash
git clone https://github.com/PrateekSethia26/TailorTalk_CalendarAgent
cd calendar-assistant
pip install -r requirements.txt
```

### 2. Setup Environment Variables

Create a `.env` file:

```bash
# Required
GOOGLE_API_KEY=your_google_ai_api_key_here

### 3. Google Cloud Console Setup

#### Step 1: Create Project & Enable API
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Navigate to **APIs & Services** → **Library**
4. Search and enable **Google Calendar API**

#### Step 2: Create OAuth Credentials
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Choose **Web application**
4. Download the JSON file as `credentials.json`
5. Also set the scope to google calendar
5. Place it in your project root directory

### 4. Launch the Application

```bash
python main.py

streamlit run app.py
```

🎉 **Success!** Your API is now running at:
- **Main API**: http://localhost:8001
- **Interactive Docs**: http://localhost:8001/docs
- **Alternative Docs**: http://localhost:8001/redoc

### 5. First Run Authentication

On your first request, you'll be redirected to Google's OAuth consent screen to authorize calendar access. This creates a `token.json` file for future use.


## ⚙️ Configuration Options

### Environment Variables

```bash
# Google AI Configuration
GOOGLE_API_KEY=your_api_key_here          # Required: Google AI API key
# OAuth callback port (default: 8000)

# Google Calendar Configuration  
SCOPES=["https://www.googleapis.com/auth/calendar"]  # OAuth scopes
CREDENTIALS_FILE=credentials.json         # OAuth credentials file
TOKEN_FILE=token.json                     # OAuth token storage
```

### Version 1.0.0 (Current)
- ✅ Initial release with core functionality
- ✅ Google Calendar integration
- ✅ AI-powered natural language processing
- ✅ OAuth 2.0 authentication
- ✅ RESTful API with FastAPI
- ✅ Comprehensive documentation

### Demo

https://calendar-agent-tailortalk.streamlit.app/


## 🙋‍♂️ Support

### Getting Help

- 📖 **Documentation**: Check this README and the `/docs` endpoint
- 🐛 **Bug Reports**: Open an issue on GitHub
- 💡 **Feature Requests**: Open an issue with the "enhancement" label
- 💬 **Discussions**: Use GitHub Discussions for questions

### FAQ

**Q: Can I use this with multiple Google accounts?**
A: Currently supports one account per instance. Multi-account support is planned for v1.1.0.


**Q: Can I customize the AI responses?**
A: Yes! Modify the system prompt in `calendar_agent.py` to customize the assistant's personality and behavior.

**Q: Is my calendar data secure?**
A: Yes! We use Google's OAuth 2.0 for secure authentication and don't store your calendar data. All operations go directly through Google's API.


---

<div align="center">

**Built with ❤️ by Prateek using FastAPI, LangGraph, and Google AI**

[⭐ Star this repo](https://github.com/your-username/calendar-assistant) • [🍴 Fork it](https://github.com/your-username/calendar-assistant/fork) • [📝 Contribute](https://github.com/your-username/calendar-assistant/blob/main/CONTRIBUTING.md)

</div>
