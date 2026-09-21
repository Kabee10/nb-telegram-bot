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

CHECK_INTERVAL = 600

app = Flask(__name__)

seen_links = set()


@app.route("/")
def home():
    return "NB Telegram Crypto Bot is running ✅"



def translate_to_persian(text):
    for attempt in range(3):
        try:
            time.sleep(3)
            translated = GoogleTranslator(
                source="en",
                target="fa"
            ).translate(text)

            if translated and translated != text:
                return translated

        except Exception as e:
            print(f"Translation attempt {attempt + 1} error: {e}")
            time.sleep(5)

    return text


def send_to_telegram(source, title, link):
    if not BOT_TOKEN or not CHANNEL_ID:
        print("BOT_TOKEN or CHANNEL_ID is missing.")
        return

    

    message = (
        
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

    if response.ok:
        print(f"Sent: {title}")
    else:
        print(f"Telegram error: {response.text}")


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
    print("News worker started.")

    while True:
        try:
            articles = get_articles()
            new_articles = []

            for source, title, link in articles:
                if link not in seen_links:
                    seen_links.add(link)
                    new_articles.append((source, title, link))

            for source, title, link in new_articles[:3]:
                send_to_telegram(source, title, link)
                time.sleep(10)

        except Exception as e:
            print(f"Worker error: {e}")

        time.sleep(CHECK_INTERVAL)


threading.Thread(
    target=news_worker,
    daemon=True
).start()

def price_worker():
    coins = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "BNB": "binance-coin",
        "SOL": "solana",
        "TON": "toncoin",
        "XRP": "xrp",
        "DOGE": "dogecoin",
        "TRX": "tron",
    }

    while True:
        try:
            message = "💰 <b>Crypto Prices — 24h</b>\n\n"
            added = 0

            for symbol, coin_id in coins.items():
                try:
                    response = requests.get(
                        f"https://api.coinbase.com/v2/prices/{symbol}-USD/spot",
                        timeout=20,
                    )
                    response.raise_for_status()
                    data = response.json()["data"]

                    price = float(data["amount"])
                    change = 0
                    if price < 1:
                        price_text = f"${price:.6f}"
                    else:
                        price_text = f"${price:,.2f}"

                    sign = "🟢" if change >= 0 else "🔴"

                    message += (
                        f"{sign} <b>{symbol}</b>: {price_text} "
                        f"({change:+.2f}%)\n"
                    )
                    added += 1

                except Exception as e:
                    print(f"{symbol} price error: {e}")

            if added > 0:
                message += (
                    '\n🔗 Source: '
                    '<a href="https://www.binance.com/activity/referral-entry/CPA?ref=CPA_00UDM2H9E6">'
                    'Binance</a>'
                )

                response = requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    data={
                        "chat_id": CHANNEL_ID,
                        "text": message,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": True,
                    },
                    timeout=30,
                )
                response.raise_for_status()

                print("Daily crypto prices sent.")
            else:
                print("Price worker error: no prices received.")

        except Exception as e:
            print(f"Price worker error: {e}")

        time.sleep(60)


threading.Thread(
    target=price_worker,
    daemon=True
).start()
