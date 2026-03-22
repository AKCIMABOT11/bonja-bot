import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from groq import Groq
from flask import Flask, request as freq

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
SERPAPI_KEY = os.environ["SERPAPI_KEY"]
PORT = int(os.environ.get("PORT", 8080))

client = Groq(api_key=GROQ_API_KEY)
flask_app = Flask(__name__)

def search_web(query):
    try:
        url = "https://serpapi.com/search"
        params = {"q": query, "api_key": SERPAPI_KEY, "num": 3}
        r = requests.get(url, params=params, timeout=15)
        results = r.json()
        snippets = []
        for item in results.get("organic_results", [])[:3]:
            snippets.append(item.get("snippet", ""))
        return "\n".join(snippets)
    except:
        return ""

async def handle_message(update: Update, context):
    question = update.message.text
    await update.message.reply_text("Recherche en cours...")
    web = search_web(question)
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": f"Informations web: {web}\nQuestion: {question}\nRéponds en français et en anglais, de façon précise et concise."}]
    )
    await update.message.reply_text(response.choices[0].message.content)

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@flask_app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
async def webhook():
    await app.update_queue.put(Update.de_json(freq.json, app.bot))
    return "OK"

@flask_app.route("/")
def index():
    return "Bot actif!"

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=PORT)
