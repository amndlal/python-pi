"""
=== AURA DASHBOARD — Personal Command Center ===
Better than Google News because it's not just news.
It's weather + news + stocks + crypto + world clock + notes + tasks + quotes + search — all in one.

RUN: python -m streamlit run app.py
"""

import streamlit as st
import requests
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Aura+",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# STYLING — Premium dark UI
# ============================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #888;
        margin-top: 0;
    }
    .news-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
        border-left: 4px solid #667eea;
        transition: all 0.2s;
    }
    .news-card:hover {
        background: #eef0f5;
        border-left-color: #764ba2;
    }
    .news-title {
        font-weight: 600;
        font-size: 14px;
        color: #1a1a2e;
        text-decoration: none;
    }
    .news-meta {
        font-size: 11px;
        color: #888;
        margin-top: 4px;
    }
    .metric-box {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        color: white;
    }
    .metric-box h3 {
        margin: 0;
        font-size: 24px;
        font-weight: 700;
    }
    .metric-box p {
        margin: 4px 0 0;
        font-size: 12px;
        opacity: 0.7;
    }
    .clock-widget {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        border-radius: 12px;
        padding: 12px 16px;
        color: white;
        margin-bottom: 8px;
    }
    .clock-city {
        font-size: 12px;
        opacity: 0.7;
    }
    .clock-time {
        font-size: 20px;
        font-weight: 700;
    }
    .quote-box {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 12px;
        padding: 20px 24px;
        color: white;
        font-style: italic;
        font-size: 15px;
        line-height: 1.6;
        margin: 16px 0;
    }
    .quote-author {
        font-style: normal;
        font-weight: 600;
        margin-top: 8px;
        font-size: 13px;
        opacity: 0.9;
    }
    .bookmark-btn {
        cursor: pointer;
        font-size: 16px;
    }
    .trending-tag {
        display: inline-block;
        background: #eef0f5;
        border-radius: 20px;
        padding: 4px 12px;
        margin: 3px;
        font-size: 12px;
        color: #444;
    }
    div[data-testid="stSidebar"] {
        background: #fafbfc;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA FILES
# ============================================================

TODO_FILE = "todos.json"
NOTES_FILE = "notes.txt"
BOOKMARKS_FILE = "bookmarks.json"

def load_json(filepath, default):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return default

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

# ============================================================
# API FUNCTIONS
# ============================================================

@st.cache_data(ttl=300)
def get_news(topic="world", count=10):
    """Fetch real news from Google News RSS."""
    try:
        url = f"https://news.google.com/rss/search?q={topic}&hl=en-IN&gl=IN&ceid=IN:en"
        response = requests.get(url, timeout=5)
        root = ET.fromstring(response.content)
        items = root.findall(".//item")
        headlines = []
        for item in items[:count]:
            title = item.find("title").text
            link = item.find("link").text if item.find("link") is not None else ""
            source = item.find("source").text if item.find("source") is not None else ""
            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
            headlines.append({"title": title, "source": source, "date": pub_date, "link": link})
        return headlines
    except:
        return []

@st.cache_data(ttl=600)
def get_weather(city):
    """Fetch weather + 3-day forecast."""
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=5)
        return response.json()
    except:
        return None

@st.cache_data(ttl=60)
def get_crypto():
    """Fetch top crypto prices."""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,dogecoin&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url, timeout=5)
        return response.json()
    except:
        return None

@st.cache_data(ttl=300)
def get_quote():
    """Fetch a motivational quote."""
    try:
        response = requests.get("https://zenquotes.io/api/random", timeout=5)
        data = response.json()
        return {"text": data[0]["q"], "author": data[0]["a"]}
    except:
        return {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"}

@st.cache_data(ttl=300)
def get_trending():
    """Get trending topics from Google News RSS categories."""
    topics = []
    try:
        url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
        response = requests.get(url, timeout=5)
        root = ET.fromstring(response.content)
        items = root.findall(".//item")
        for item in items[:15]:
            title = item.find("title").text
            words = [w for w in title.split() if len(w) > 4 and w[0].isupper()]
            topics.extend(words[:2])
        return list(set(topics))[:12]
    except:
        return ["AI", "Technology", "India", "Climate", "Markets", "Sports"]

@st.cache_data(ttl=300)
def get_exchange_rates():
    """Fetch currency exchange rates."""
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        response = requests.get(url, timeout=5)
        data = response.json()
        return data.get("rates", {})
    except:
        return {}

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown('<p class="main-header">✨ aura+</p>', unsafe_allow_html=True)
    st.caption("Your personal command center")
    st.divider()

    # World Clock
    st.markdown("**🕐 World Clock**")
    clocks = {
        "Cologne": timezone(timedelta(hours=2)),
        "Mumbai": timezone(timedelta(hours=5, minutes=30)),
        "New York": timezone(timedelta(hours=-4)),
        "Tokyo": timezone(timedelta(hours=9)),
        "London": timezone(timedelta(hours=1)),
    }
    for city, tz in clocks.items():
        time_now = datetime.now(tz).strftime("%H:%M")
        day = datetime.now(tz).strftime("%a")
        st.markdown(f"""<div class="clock-widget">
            <span class="clock-city">{city} · {day}</span><br>
            <span class="clock-time">{time_now}</span>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # Crypto Prices
    st.markdown("**₿ Crypto**")
    crypto = get_crypto()
    if crypto:
        for coin, data in crypto.items():
            price = f"${data['usd']:,.0f}" if data['usd'] > 100 else f"${data['usd']:.4f}"
            change = data.get('usd_24h_change', 0)
            arrow = "🟢" if change >= 0 else "🔴"
            st.markdown(f"{arrow} **{coin.capitalize()}**: {price} ({change:+.1f}%)")
    else:
        st.caption("Could not fetch crypto data")

    st.divider()

    # Currency Converter
    st.markdown("**💱 Currency**")
    rates = get_exchange_rates()
    if rates:
        amount = st.number_input("Amount (USD)", value=1.0, step=1.0, min_value=0.0)
        currencies = ["INR", "EUR", "GBP", "JPY", "AED"]
        for cur in currencies:
            if cur in rates:
                converted = amount * rates[cur]
                st.caption(f"${amount:.0f} = {cur} {converted:,.2f}")

# ============================================================
# MAIN CONTENT
# ============================================================

now = datetime.now()

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f'<p class="main-header">Good {"morning" if now.hour < 12 else "afternoon" if now.hour < 17 else "evening"}, Aman</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">{now.strftime("%A, %d %B %Y")} · {now.strftime("%H:%M")}</p>', unsafe_allow_html=True)
with col2:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

# Quote of the day
quote = get_quote()
st.markdown(f"""<div class="quote-box">
    "{quote['text']}"
    <div class="quote-author">— {quote['author']}</div>
</div>""", unsafe_allow_html=True)

# ============================================================
# WEATHER ROW
# ============================================================

weather = get_weather("Cologne")
if weather:
    current = weather["current_condition"][0]
    forecast = weather.get("weather", [])

    w1, w2, w3, w4, w5 = st.columns(5)
    with w1:
        st.metric("🌡️ Temp", f"{current['temp_C']}°C", f"Feels {current['FeelsLikeC']}°C")
    with w2:
        st.metric("💧 Humidity", f"{current['humidity']}%")
    with w3:
        st.metric("💨 Wind", f"{current['windspeedKmph']} km/h")
    with w4:
        st.metric("☁️ Sky", current["weatherDesc"][0]["value"])
    with w5:
        if forecast:
            st.metric("📅 Tomorrow", f"{forecast[1]['maxtempC'] if len(forecast) > 1 else '—'}°C")

st.divider()

# ============================================================
# TRENDING
# ============================================================

trending = get_trending()
if trending:
    st.markdown("**🔥 Trending Now**")
    trending_html = " ".join([f'<span class="trending-tag">{t}</span>' for t in trending])
    st.markdown(trending_html, unsafe_allow_html=True)
    st.write("")

# ============================================================
# NEWS TABS
# ============================================================

tabs = st.tabs(["🌍 World", "💻 Technology", "📈 Business", "⚽ Sports", "🇮🇳 India", "🇩🇪 Germany", "🔍 Search"])

categories = ["world", "technology", "business", "sports", "india", "germany"]

for i, cat in enumerate(categories):
    with tabs[i]:
        news = get_news(cat, 12)
        if news:
            # Two column layout for news
            left_col, right_col = st.columns(2)
            for idx, h in enumerate(news):
                target = left_col if idx % 2 == 0 else right_col
                with target:
                    st.markdown(f"""<div class="news-card">
                        <a href="{h['link']}" target="_blank" class="news-title">{h['title']}</a>
                        <div class="news-meta">{h['source']} · {h['date'][:16] if h['date'] else ''}</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.warning("No news available for this category.")

# Search tab
with tabs[6]:
    search_query = st.text_input("Search any topic", placeholder="e.g. AI, cricket, electric cars...")
    if search_query:
        results = get_news(search_query, 12)
        if results:
            left_col, right_col = st.columns(2)
            for idx, h in enumerate(results):
                target = left_col if idx % 2 == 0 else right_col
                with target:
                    st.markdown(f"""<div class="news-card">
                        <a href="{h['link']}" target="_blank" class="news-title">{h['title']}</a>
                        <div class="news-meta">{h['source']} · {h['date'][:16] if h['date'] else ''}</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("No results found.")

st.divider()

# ============================================================
# BOTTOM ROW: TASKS + NOTES + BOOKMARKS
# ============================================================

b1, b2, b3 = st.columns(3)

# --- TO-DO LIST ---
with b1:
    st.subheader("📝 Tasks")
    todos = load_json(TODO_FILE, [])

    new_task = st.text_input("Add task", placeholder="What needs to be done?", key="new_task")
    if new_task:
        todos.append({"text": new_task, "done": False, "added": now.isoformat()})
        save_json(TODO_FILE, todos)
        st.rerun()

    if todos:
        for i, task in enumerate(todos):
            col_check, col_text, col_del = st.columns([0.5, 4, 0.5])
            with col_check:
                done = st.checkbox("", value=task["done"], key=f"todo_{i}")
                if done != task["done"]:
                    todos[i]["done"] = done
                    save_json(TODO_FILE, todos)
                    st.rerun()
            with col_text:
                if task["done"]:
                    st.markdown(f"~~{task['text']}~~")
                else:
                    st.write(task["text"])
            with col_del:
                if st.button("×", key=f"del_{i}"):
                    todos.pop(i)
                    save_json(TODO_FILE, todos)
                    st.rerun()

        done_count = sum(1 for t in todos if t["done"])
        st.progress(done_count / len(todos) if todos else 0)
        st.caption(f"{done_count}/{len(todos)} completed")

        if done_count > 0 and st.button("Clear completed"):
            todos = [t for t in todos if not t["done"]]
            save_json(TODO_FILE, todos)
            st.rerun()
    else:
        st.caption("No tasks. Add one above!")

# --- QUICK NOTES ---
with b2:
    st.subheader("📌 Notes")
    existing_notes = ""
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r") as f:
            existing_notes = f.read()

    notes = st.text_area("Your notes", value=existing_notes, height=300, label_visibility="collapsed")
    if notes != existing_notes:
        with open(NOTES_FILE, "w") as f:
            f.write(notes)
        st.toast("Notes saved!")

# --- BOOKMARKS ---
with b3:
    st.subheader("🔖 Bookmarks")
    bookmarks = load_json(BOOKMARKS_FILE, [])

    with st.expander("Add bookmark"):
        bm_title = st.text_input("Title", key="bm_title")
        bm_url = st.text_input("URL", key="bm_url")
        if st.button("Save bookmark") and bm_title and bm_url:
            bookmarks.append({"title": bm_title, "url": bm_url})
            save_json(BOOKMARKS_FILE, bookmarks)
            st.rerun()

    if bookmarks:
        for i, bm in enumerate(bookmarks):
            col_link, col_rm = st.columns([5, 1])
            with col_link:
                st.markdown(f"[{bm['title']}]({bm['url']})")
            with col_rm:
                if st.button("×", key=f"bm_del_{i}"):
                    bookmarks.pop(i)
                    save_json(BOOKMARKS_FILE, bookmarks)
                    st.rerun()
    else:
        st.caption("Save useful links here.")

# ============================================================
# FOOTER
# ============================================================

st.divider()
st.markdown("""
<center style='color: #999; font-size: 12px;'>
    aura+ v2.0 · Built with Python + Streamlit · All data refreshes automatically
</center>
""", unsafe_allow_html=True)
