import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from agent import process_voice_memo, tools # Reuse your existing logic!

# Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🎙️ I'm ready! Send me a voice note or text message."
    )

import asyncio  # <--- NEW IMPORT

# ... (Keep your existing imports and setup)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    status_msg = await context.bot.send_message(chat_id=update.effective_chat.id, text="⬇️ Downloading...")

    file_path = f"voice_{user_id}.oga"

    try:
        # 1. Download File (This is already Async, so it's fine)
        new_file = await context.bot.get_file(update.message.voice.file_id)
        await new_file.download_to_drive(file_path)

        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=status_msg.message_id, text="🧠 Thinking (Whisper + GPT-4o)...")
        
        # 2. RUN BLOCKING CODE IN A THREAD (The Fix ⚡)
        # This tells the main loop: "Don't freeze! Run this heavy function in the background."
        loop = asyncio.get_running_loop()
        
        # We pass the function reference and the argument
        transcript, actions = await loop.run_in_executor(None, process_voice_memo, file_path, None)

        # 3. Formulate Response
        response_text = f"**Transcript:**\n_{transcript}_\n\n"
        if actions:
            response_text += "**✅ Actions Taken:**\n"
            for action in actions:
                response_text += f"- {action}\n"
        else:
            response_text += "No specific calendar events or tasks found."

        await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text, parse_mode='Markdown')

    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"❌ Error: {str(e)}")
    
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles text messages (e.g., 'Remind me to buy bread')"""
    text = update.message.text
    status_msg = await context.bot.send_message(chat_id=update.effective_chat.id, text="🧠 Processing text...")

    try:
        # We can reuse the agent logic, skipping the transcription step
        # Ideally, refactor agent.py to separate 'transcribe' from 'think', 
        # but for now we can just use the 'Thinking' part.
        # Let's create a quick helper or just call the LLM directly here for simplicity,
        # OR better: Refactor agent.py slightly to handle text input.
        
        # For now, let's just tell the user this is for voice, 
        # or we can quickly mock a "transcript" to reuse the function.
        transcript, actions = process_voice_memo(text_input=text) # We need to modify agent.py slightly for this!
        
        response_text = f"**Actions Taken:**\n"
        for action in actions:
            response_text += f"- {action}\n"
            
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=status_msg.message_id, text=response_text)

    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"❌ Error: {str(e)}")

if __name__ == '__main__':
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in .env")
        exit(1)
        
    application = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    start_handler = CommandHandler('start', start)
    voice_handler = MessageHandler(filters.VOICE, handle_voice)
    # text_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text) # Optional

    application.add_handler(start_handler)
    application.add_handler(voice_handler)
    # application.add_handler(text_handler)

    print("🤖 Bot is polling...")
    application.run_polling()