import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from groq import Groq

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
SERPAPI_KEY = os.environ["SERPAPI_KEY"]

client = Groq(api_key=GROQ_API_KEY)

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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
app.run_polling()
