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
        translated = GoogleTranslator(source="en", target="fa").translate(text)
        if translated and "Error 500" not in translated and "Server Error" not in translated:
            return translated
    except Exception as e:
        print(f"Translation error: {e}")

    return "ترجمه فارسی موقتاً در دسترس نیست."

def send_to_telegram(source, title, link):
    if not BOT_TOKEN or not CHANNEL_ID:
        print("BOT_TOKEN or CHANNEL_ID is missing.")
        return

    persian_title = translate_to_persian(title)

    message = ( 
        f"🌐 <b>فارسی:</b>\n"
        f"{html.escape(persian_title)}\n\n"
        f"🌐 <b>English:</b>\n"
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

def binance_referral_worker():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    text = (
        "🟡 <b>Binance</b>\n\n"
        "قیمت ارزهای دیجیتال را مشاهده کنید و در Binance ثبت‌نام کنید 👇"
    )

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "🟡 مشاهده Binance",
                    "url": "https://www.binance.com/activity/referral-entry/CPA?ref=CPA_00UDM2H9E6"
                }
            ]
        ]
    }

    while True:
        try:
            requests.post(
                url,
                data={
                    "chat_id": CHANNEL_ID,
                    "text": text,
                    "parse_mode": "HTML",
                    "reply_markup": __import__("json").dumps(keyboard)
                },
                timeout=20
            )
        except Exception as e:
            print(f"Binance referral error: {e}")


        time.sleep(86400)
def referrals_worker():      
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    text = (
        
             "برای ورود به هر برنامه، روی دکمه مربوطه در پایین بزنید 👇\n"
        "⚠️ قبل از استفاده از هر پروژه، خودتان تحقیق کنید."
    )

    keyboard = {
        "inline_keyboard": [
            [{"text": "🟡 Binance", "url": "https://www.binance.com/activity/referral-entry/CPA?ref=CPA_00UDM2H9E6"}],
            [{"text": "⚫ OKX", "url": "https://okx.com/en-ae/join/75348298"}],
            [{"text": "🟠 Bybit", "url": "https://www.bybit.com/invite?ref=OQKN2P&medium=referral&utm_campaign=evergreen&share_to=post"}],
            [{"text": "⚽ Football Farm", "url": "https://farm.goalmanager.io"}],
            [{"text": "💎 Rubi Block", "url": "https://rubi.click/join/NH555"}],
            [{"text": "⚽ Goal Chain", "url": "https://goalmanager.io"}],
            [{"text": "🐝 Bee Network", "url": "https://j.bee.com/s?a=nabiullah1991"}],
            [{"text": "🔷 Alpha Network", "url": "https://www.minealpha.net"}],
            [{"text": "🟣 Pi Network", "url": "https://minepi.com/kabee11"}],
            [{"text": "⛏ PERIA", "url": "https://miningperia.com/pages/join.php?ref=B424BE29"}],
            [{"text": "🌱 Sprout Network", "url": "https://play.google.com/store/apps/details?id=com.sproutnetwork.app"}],
            [{"text": "🔐 DeNet", "url": "https://links.denet.app/mobile?referrer=0x4e4afb9f1d19d071bf5d782f96e401ededc26601"}],
            [{"text": "💎 TON Station", "url": "https://tonstation.app/i/WCPUHAJ8"}],
            [{"text": "🔥 HOT Labs", "url": "https://app.hot-labs.org/link?916094uu"}],
            [{"text": "🤖 ATF Airdrop", "url": "https://t.me/ATF_AIRDROP_bot?start=1469027938"}]
        ]
    }

    while True:
        try:
            requests.post(
                url,
                data={
                    "chat_id": CHANNEL_ID,
                    "text": text,
                    "parse_mode": "HTML",
                    "reply_markup": __import__("json").dumps(keyboard)
                },
                timeout=20
            )
        except Exception as e:
            print(f"Referral worker error: {e}")

        time.sleep(86400)
        def price_worker():
    message_id = None

    coins = {
        "BTCUSDT": "₿ Bitcoin (BTC)",
        "ETHUSDT": "♦️ Ethereum (ETH)",
        "BNBUSDT": "🟡 BNB",
        "SOLUSDT": "🟣 Solana (SOL)",
        "TONUSDT": "💎 TON",
        "DOGEUSDT": "🐕 Dogecoin (DOGE)",
        "TRXUSDT": "🔴 TRON (TRX)"
    }

    while True:
        try:
            lines = ["<b>💰 قیمت لحظه‌ای ارزهای دیجیتال</b>\n"]

            for symbol, name in coins.items():
                r = requests.get(
                    f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}",
                    timeout=20
                )
                data = r.json()

                price = float(data["lastPrice"])
                change = float(data["priceChangePercent"])

                lines.append(
                    f"{name} — <b>${price:,.4f}</b> ({change:+.2f}%)"
                )

            lines.append(
                f"\n🕒 بروزرسانی: {time.strftime('%H:%M UTC', time.gmtime())}"
            )

            text = "\n".join(lines)

            if message_id is None:
                r = requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    data={
                        "chat_id": CHANNEL_ID,
                        "text": text,
                        "parse_mode": "HTML"
                    },
                    timeout=20
                )

                message_id = r.json()["result"]["message_id"]

            else:
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
                    data={
                        "chat_id": CHANNEL_ID,
                        "message_id": message_id,
                        "text": text,
                        "parse_mode": "HTML"
                    },
                    timeout=20
                )

        except Exception as e:
            print(f"Price worker error: {e}")

        time.sleep(3600)
threading.Thread(target=news_worker, daemon=True).start()


threading.Thread(target=referrals_worker, daemon=True).start()
threading.Thread(target=price_worker, daemon=True).start()

