# 🧠 Second Brain Bot (Voice-to-Calendar Agent)

**Second Brain** is a multimodal AI agent that lives in Telegram. It listens to your voice notes, intelligently extracts tasks and events, and automatically syncs them to your **Google Calendar** and **Google Tasks**.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-Whisper_%7C_GPT--4o-green?style=for-the-badge&logo=openai&logoColor=white)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-Calendar_API-yellow?style=for-the-badge&logo=googlecloud&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)

## ✨ Features

- **🗣️ Voice-First Interface:** Send raw voice notes; the bot handles transcription (Whisper).
- **🧠 Intelligent Extraction:** Distinguishes between "Events" (at 2 PM) and "Tasks" (buy milk).
- **📅 Real-Time Sync:** Instantly creates Google Calendar events and Google Tasks.
- **⚡ Non-Blocking Core:** Uses asynchronous threading to handle processing without freezing the chat interface.

## 🏗️ Architecture

```mermaid
graph LR
    User[User (Voice Note)] -->|Telegram| Bot[Telegram Bot]
    Bot -->|Async Thread| Agent[AI Agent]
    
    subgraph "The Brain"
        Agent -->|Audio| Whisper[OpenAI Whisper]
        Whisper -->|Text| LLM[GPT-4o (Function Calling)]
    end
    
    subgraph "The Hands"
        LLM -->|JSON| Tools[Google Utils]
        Tools -->|API| GCal[Google Calendar]
        Tools -->|API| GTask[Google Tasks]
    end
    
    Tools -->|Confirmation| Bot
```

## 🚀 Installation

### Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/second-brain-bot.git
cd second-brain-bot
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Setup Credentials

1. Create a `.env` file with `OPENAI_API_KEY` and `TELEGRAM_BOT_TOKEN`.
2. Place your `credentials.json` (Desktop App) from Google Cloud in the root folder.

### Run

```bash
python src/main.py
```

## 📦 Dependencies


```bash
uv pip freeze > requirements.txt
```

## 📄 License

MIT