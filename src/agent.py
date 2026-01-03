import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from google_utils import add_calendar_event, add_google_task
from datetime import datetime

load_dotenv()
client = OpenAI()

# --- TOOL DEFINITIONS ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_calendar_event",
            "description": "Schedule an event in Google Calendar",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Title of the event"},
                    "start_time": {"type": "string", "description": "ISO 8601 start time (e.g., 2024-01-03T15:00:00)"},
                    "end_time": {"type": "string", "description": "ISO 8601 end time"}
                },
                "required": ["summary", "start_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_google_task",
            "description": "Add a to-do item to Google Tasks",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The content of the task"}
                },
                "required": ["title"]
            }
        }
    }
]

def process_voice_memo(audio_file_path=None, text_input=None):
    """
    Handles EITHER audio file path OR raw text input.
    """
    print(f"DEBUG: Processing... Audio: {audio_file_path}, Text: {text_input}")

    # 1. Get Text (Transcription or Direct Input)
    text = ""
    if audio_file_path:
        with open(audio_file_path, "rb") as audio_file:
            transcript_obj = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        text = transcript_obj.text
    elif text_input:
        text = text_input
    else:
        return "No input provided", []

    print(f"🗣️ Transcribed/Input text: {text}")

    # --- CRITICAL FIX: Initialize results list here ---
    results = [] 

    # 2. Think & Extract Actions
    current_time = datetime.now().isoformat()
    system_prompt = f"You are a personal assistant. Current time: {current_time}. Extract tasks and events."

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        tools=tools,
        tool_choice="auto" 
    )

    tool_calls = response.choices[0].message.tool_calls

    # 3. Execute Tools (If any)
    if tool_calls:
        print(f"🛠️ Tool calls detected: {len(tool_calls)}")
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            print(f"   -> Executing {function_name} with args: {args}")

            try:
                if function_name == "add_calendar_event":
                    # This line triggers the Google Login Popup if not authenticated!
                    res = add_calendar_event(
                        args['summary'], 
                        args['start_time'], 
                        args.get('end_time')
                    )
                    results.append(res)
                
                elif function_name == "add_google_task":
                    res = add_google_task(args['title'])
                    results.append(res)
            except Exception as e:
                error_msg = f"Error executing {function_name}: {str(e)}"
                print(error_msg)
                results.append(error_msg)
    else:
        print("ℹ️ No tools called by AI.")
    
    return text, results