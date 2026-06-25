"""
=== PERSONAL DASHBOARD — Web App ===
A visual dashboard built with Streamlit (Python).

RUN: python -m streamlit run app.py
"""

import streamlit as st
import requests
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Aura Dashboard",
    page_icon="✨",
    layout="wide"
)

# ============================================================
# STYLING
# ============================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-top: 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================

now = datetime.now()
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<p class="main-header">✨ Aura Dashboard</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">{now.strftime("%A, %d %B %Y")} | {now.strftime("%H:%M")}</p>', unsafe_allow_html=True)
with col2:
    st.write("")

st.divider()

# ============================================================
# WEATHER SECTION
# ============================================================

col1, col2, col3 = st.columns(3)

@st.cache_data(ttl=600)
def get_weather(city):
    """Fetch weather data (cached for 10 minutes)."""
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=5)
        return response.json()
    except:
        return None

weather = get_weather("Cologne")

if weather:
    current = weather["current_condition"][0]
    with col1:
        st.metric(
            label="🌡️ Temperature",
            value=f"{current['temp_C']}°C",
            delta=f"Feels like {current['FeelsLikeC']}°C"
        )
    with col2:
        st.metric(
            label="💧 Humidity",
            value=f"{current['humidity']}%"
        )
    with col3:
        st.metric(
            label="☁️ Condition",
            value=current["weatherDesc"][0]["value"]
        )
else:
    st.warning("Could not fetch weather data.")

st.divider()

# ============================================================
# TO-DO LIST + NEWS SIDE BY SIDE
# ============================================================

left, right = st.columns(2)

# --- TO-DO LIST ---
TODO_FILE = "todos.json"

def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as f:
            return json.load(f)
    return []

def save_todos(todos):
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)

with left:
    st.subheader("📝 To-Do List")

    todos = load_todos()

    # Add new task
    new_task = st.text_input("Add a task", placeholder="Type a task and press Enter")
    if new_task:
        todos.append({"text": new_task, "done": False})
        save_todos(todos)
        st.rerun()

    # Display tasks
    if todos:
        for i, task in enumerate(todos):
            col_check, col_text, col_del = st.columns([0.5, 4, 0.5])
            with col_check:
                done = st.checkbox("", value=task["done"], key=f"todo_{i}")
                if done != task["done"]:
                    todos[i]["done"] = done
                    save_todos(todos)
                    st.rerun()
            with col_text:
                if task["done"]:
                    st.markdown(f"~~{task['text']}~~")
                else:
                    st.write(task["text"])
            with col_del:
                if st.button("🗑️", key=f"del_{i}"):
                    todos.pop(i)
                    save_todos(todos)
                    st.rerun()

        # Clear completed
        completed = [t for t in todos if t["done"]]
        if completed:
            if st.button("Clear completed"):
                todos = [t for t in todos if not t["done"]]
                save_todos(todos)
                st.rerun()
    else:
        st.info("No tasks yet. Add one above!")

# --- NEWS ---
@st.cache_data(ttl=300)
def get_news(topic="world"):
    """Fetch real news from Google News RSS (no API key needed)."""
    try:
        url = f"https://news.google.com/rss/search?q={topic}&hl=en-IN&gl=IN&ceid=IN:en"
        response = requests.get(url, timeout=5)
        root = ET.fromstring(response.content)
        items = root.findall(".//item")
        headlines = []
        for item in items[:8]:
            title = item.find("title").text
            source = item.find("source").text if item.find("source") is not None else ""
            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
            headlines.append({"title": title, "source": source, "date": pub_date})
        return headlines
    except:
        return []

with right:
    st.subheader("📰 Live Headlines")

    news_topic = st.selectbox("Topic", ["world", "technology", "business", "sports", "india", "germany"], label_visibility="collapsed")
    headlines = get_news(news_topic)

    if headlines:
        for h in headlines:
            st.markdown(f"**{h['title']}**  \n*{h['source']}*")
            st.divider()
    else:
        st.warning("Could not fetch news. Check your internet connection.")

# ============================================================
# QUICK NOTES
# ============================================================

st.divider()
st.subheader("📌 Quick Notes")

NOTES_FILE = "notes.txt"

existing_notes = ""
if os.path.exists(NOTES_FILE):
    with open(NOTES_FILE, "r") as f:
        existing_notes = f.read()

notes = st.text_area("Your notes (auto-saved)", value=existing_notes, height=150)
if notes != existing_notes:
    with open(NOTES_FILE, "w") as f:
        f.write(notes)
    st.toast("Notes saved!")

# ============================================================
# FOOTER
# ============================================================

st.divider()
st.markdown(
    "<center style='color: #999; font-size: 12px;'>Built with Python + Streamlit | Aura Dashboard v1.0</center>",
    unsafe_allow_html=True
)
