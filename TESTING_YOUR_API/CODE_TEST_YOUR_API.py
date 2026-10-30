import os
import requests

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)


# =========================
# CONFIG
# =========================

BOT_TOKEN = YOUR_BOT_TOKEN

API_URL = os.getenv(
    "API_URL",
    "YOUR_WEB_URL"
).rstrip("/")

API_KEY = YOUR_API_KEY


# =========================
# HELPERS
# =========================

def api_get(endpoint, params=None):
    url = f"{API_URL}{endpoint}"

    try:
        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        try:
            data = response.json()
        except Exception:
            data = {
                "raw_response": response.text
            }

        return response.status_code, data

    except requests.RequestException as e:
        return None, {
            "error": str(e)
        }


def format_json(data):
    import json

    return json.dumps(
        data,
        indent=2,
        ensure_ascii=False
    )


# =========================
# /start
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    text = (
        "🤖 <b>KRUTIK CYBER EXPERT</b>\n"
        "🧪 <b>API TESTING BOT</b>\n\n"

        f"👤 Name: {user.first_name}\n"
        f"🆔 User ID: <code>{user.id}</code>\n"
        f"💬 Chat ID: <code>{chat.id}</code>\n\n"

        "🔧 <b>Commands</b>\n"
        "/search QUERY - API search test\n"
        "/status - API key status\n"
        "/usage - API usage\n"
        "/health - API health check\n"
        "/id - Show Chat ID\n\n"

        f"🌐 API:\n<code>{API_URL}</code>"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )


# =========================
# /id
# =========================

async def chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🆔 Chat ID:\n<code>{update.effective_chat.id}</code>",
        parse_mode="HTML"
    )


# =========================
# /health
# =========================

async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Checking API...")

    status_code, data = api_get("/health")

    if status_code is None:
        await update.message.reply_text(
            "❌ API connection failed.\n\n"
            f"<code>{data.get('error')}</code>",
            parse_mode="HTML"
        )
        return

    result = format_json(data)

    await update.message.reply_text(
        f"🩺 <b>API HEALTH</b>\n\n"
        f"HTTP: <code>{status_code}</code>\n\n"
        f"<pre>{result[:3500]}</pre>",
        parse_mode="HTML"
    )


# =========================
# /status
# =========================

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not API_KEY:
        await update.message.reply_text(
            "❌ API_KEY environment variable is not set."
        )
        return

    await update.message.reply_text(
        "🔄 Checking API key..."
    )

    status_code, data = api_get(
        "/api/status",
        {
            "api_key": API_KEY
        }
    )

    if status_code is None:
        await update.message.reply_text(
            "❌ Connection error."
        )
        return

    result = format_json(data)

    await update.message.reply_text(
        f"🔐 <b>API KEY STATUS</b>\n\n"
        f"HTTP: <code>{status_code}</code>\n\n"
        f"<pre>{result[:3500]}</pre>",
        parse_mode="HTML"
    )


# =========================
# /usage
# =========================

async def usage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not API_KEY:
        await update.message.reply_text(
            "❌ API_KEY environment variable is not set."
        )
        return

    await update.message.reply_text(
        "📊 Checking usage..."
    )

    status_code, data = api_get(
        "/api/status",
        {
            "api_key": API_KEY
        }
    )

    if status_code is None:
        await update.message.reply_text(
            "❌ Connection error."
        )
        return

    result = format_json(data)

    await update.message.reply_text(
        f"📈 <b>API USAGE</b>\n\n"
        f"<pre>{result[:3500]}</pre>",
        parse_mode="HTML"
    )


# =========================
# /search
# =========================

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not API_KEY:
        await update.message.reply_text(
            "❌ API_KEY environment variable is not set."
        )
        return

    if not context.args:
        await update.message.reply_text(
            "❌ Query missing.\n\n"
            "Example:\n"
            "<code>/search TEST123</code>",
            parse_mode="HTML"
        )
        return

    query = " ".join(context.args)

    await update.message.reply_text(
        f"🔎 Searching:\n<code>{query}</code>\n\n"
        "⏳ Please wait..."
        ,
        parse_mode="HTML"
    )

    status_code, data = api_get(
        "/api/search",
        {
            "api_key": API_KEY,
            "query": query,
            "limit": 20
        }
    )

    if status_code is None:
        await update.message.reply_text(
            "❌ API connection failed.\n\n"
            f"<code>{data.get('error')}</code>",
            parse_mode="HTML"
        )
        return

    result = format_json(data)

    # Telegram message limit protection
    if len(result) > 3500:
        result = result[:3500] + "\n..."

    if status_code == 200:
        title = "✅ API SEARCH SUCCESS"
    else:
        title = "❌ API SEARCH ERROR"

    await update.message.reply_text(
        f"<b>{title}</b>\n\n"
        f"HTTP: <code>{status_code}</code>\n\n"
        f"<pre>{result}</pre>",
        parse_mode="HTML"
    )


# =========================
# /help
# =========================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🧪 <b>API TESTING BOT</b>\n\n"

        "🔎 <code>/search QUERY</code>\n"
        "Test API search endpoint.\n\n"

        "🔐 <code>/status</code>\n"
        "Check API key status.\n\n"

        "📊 <code>/usage</code>\n"
        "Check API usage.\n\n"

        "🩺 <code>/health</code>\n"
        "Check API server health.\n\n"

        "🆔 <code>/id</code>\n"
        "Show Telegram Chat ID."
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )


# =========================
# ERROR HANDLER
# =========================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(
        "BOT ERROR:",
        repr(context.error)
    )


# =========================
# MAIN
# =========================

def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN is not set.")
        return

    if not API_KEY:
        print("WARNING: API_KEY is not set.")
        print("The bot will start, but API commands will fail.")

    print("=" * 50)
    print("KRUTIK CYBER EXPERT - API TESTING BOT")
    print("=" * 50)
    print("API:", API_URL)
    print("Bot starting...")
    print("=" * 50)

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("help", help_command)
    )

    app.add_handler(
        CommandHandler("search", search)
    )

    app.add_handler(
        CommandHandler("status", status)
    )

    app.add_handler(
        CommandHandler("usage", usage)
    )

    app.add_handler(
        CommandHandler("health", health)
    )

    app.add_handler(
        CommandHandler("id", chat_id)
    )

    app.add_error_handler(
        error_handler
    )

    print("Bot is running...")
    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()