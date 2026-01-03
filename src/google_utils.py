import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Permissions we need
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/tasks'
]

def authenticate_google():
    """Shows a login popup to authenticate the user."""
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def add_calendar_event(summary, start_time, end_time=None):
    """Adds an event to Google Calendar."""
    creds = authenticate_google()
    service = build('calendar', 'v3', credentials=creds)
    
    # Default to 1 hour duration if no end time provided
    if not end_time:
        # Simple logic: start_time + 1 hour (Requires datetime math, handled by LLM ideally)
        pass 

    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'GMT+1'}, # Morocco Time
        'end': {'dateTime': end_time or start_time, 'timeZone': 'GMT+1'},
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    return f"📅 Event created: {event.get('htmlLink')}"

def add_google_task(title):
    """Adds a task to Google Tasks."""
    creds = authenticate_google()
    service = build('tasks', 'v1', credentials=creds)

    task = {'title': title}
    result = service.tasks().insert(tasklist='@default', body=task).execute()
    return f"✅ Task added: {result['title']}"