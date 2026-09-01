import os
import time
import html
import threading
import requests
import feedparser

from flask import Flask
from deep_translator import GoogleTranslator

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

RSS_FEEDS = [
    ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
    ("Cointelegraph", "https://cointelegraph.com/rss"),
]

CHECK_INTERVAL = 900  # هر 15 دقیقه
seen_links = set()

app = Flask(__name__)


@app.route("/")
def home():
    return "NB Telegram Crypto Bot is running ✅"


def translate_to_persian(text):
    try:
        return GoogleTranslator(source="auto", target="fa").translate(text)
    except Exception:
        return text


def send_to_telegram(source, title, link):
    if not BOT_TOKEN or not CHANNEL_ID:
        print("BOT_TOKEN or CHANNEL_ID is missing.")
        return

    persian_title = translate_to_persian(title)

    message = (
        f"🟢 <b>خبر کریپتو | Crypto News</b>\n\n"
        f"🇦🇫 <b>فارسی:</b>\n"
        f"{html.escape(persian_title)}\n\n"
        f"🇬🇧 <b>English:</b>\n"
        f"{html.escape(title)}\n\n"
        f"🔗 <b>Source:</b> {html.escape(source)}\n"
        f'<a href="{html.escape(link)}">Read full news</a>'
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHANNEL_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        },
        timeout=30,
    )

    print(response.text)


def get_articles():
    articles = []

    for source, feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:10]:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()

                if title and link:
                    articles.append((source, title, link))

        except Exception as e:
            print(f"RSS error: {e}")

    return articles


def initialize_seen():
    for _, _, link in get_articles():
        seen_links.add(link)


def news_worker():
    initialize_seen()

    while True:
        try:
            articles = get_articles()
            new_articles = []

            for article in articles:
                source, title, link = article

                if link not in seen_links:
                    seen_links.add(link)
                    new_articles.append(article)

            # حداکثر 3 خبر در هر بررسی
            for source, title, link in new_articles[:3]:
                send_to_telegram(source, title, link)
                time.sleep(10)

        except Exception as e:
            print(f"Worker error: {e}")

        time.sleep(CHECK_INTERVAL)


threading.Thread(target=news_worker, daemon=True).start()

