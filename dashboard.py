"""
=== PERSONAL DASHBOARD ===
A terminal app that shows weather, news headlines, and your to-do list.
We'll build this step by step. Each section teaches new Python concepts.

RUN: python dashboard.py
"""

import json
import os
from datetime import datetime

# ============================================================
# STEP 1: Basic display (print, f-strings, datetime)
# ============================================================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_header():
    now = datetime.now()
    date_str = now.strftime("%A, %d %B %Y")  # e.g. "Wednesday, 25 June 2026"
    time_str = now.strftime("%H:%M")

    print("=" * 50)
    print(f"   PERSONAL DASHBOARD")
    print(f"   {date_str} | {time_str}")
    print("=" * 50)
    print()

# ============================================================
# STEP 2: To-Do List (file handling, lists, functions)
# ============================================================

TODO_FILE = "todos.json"

def load_todos():
    """Load todos from file. If file doesn't exist, return empty list."""
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as f:
            return json.load(f)
    return []

def save_todos(todos):
    """Save todos to file."""
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)

def show_todos():
    """Display the to-do list."""
    todos = load_todos()
    print("--- TO-DO LIST ---")
    if not todos:
        print("  No tasks yet. Add one from the menu!")
    else:
        for i, task in enumerate(todos, 1):
            status = "Done" if task["done"] else "    "
            print(f"  {i}. [{status}] {task['text']}")
    print()

def add_todo():
    """Add a new to-do item."""
    text = input("  Enter task: ").strip()
    if text:
        todos = load_todos()
        todos.append({"text": text, "done": False})
        save_todos(todos)
        print(f"  Added: {text}")
    else:
        print("  Empty task, skipping.")

def complete_todo():
    """Mark a to-do as done."""
    todos = load_todos()
    if not todos:
        print("  No tasks to complete.")
        return
    show_todos()
    try:
        num = int(input("  Task number to complete: "))
        if 1 <= num <= len(todos):
            todos[num - 1]["done"] = True
            save_todos(todos)
            print(f"  Marked '{todos[num-1]['text']}' as done!")
        else:
            print("  Invalid number.")
    except ValueError:
        print("  Please enter a number.")

def delete_todo():
    """Delete a to-do item."""
    todos = load_todos()
    if not todos:
        print("  No tasks to delete.")
        return
    show_todos()
    try:
        num = int(input("  Task number to delete: "))
        if 1 <= num <= len(todos):
            removed = todos.pop(num - 1)
            save_todos(todos)
            print(f"  Deleted: {removed['text']}")
        else:
            print("  Invalid number.")
    except ValueError:
        print("  Please enter a number.")

# ============================================================
# STEP 3: Weather (API calls with requests)
# ============================================================

def show_weather():
    """Fetch and display weather for your city."""
    print("--- WEATHER (Cologne) ---")
    try:
        import requests
        # Free API, no key needed
        url = "https://wttr.in/Cologne?format=j1"
        response = requests.get(url, timeout=5)
        data = response.json()

        current = data["current_condition"][0]
        temp = current["temp_C"]
        feels = current["FeelsLikeC"]
        desc = current["weatherDesc"][0]["value"]
        humidity = current["humidity"]

        print(f"  {desc}")
        print(f"  Temperature: {temp}°C (feels like {feels}°C)")
        print(f"  Humidity: {humidity}%")
    except ImportError:
        print("  Install requests: pip install requests")
    except Exception as e:
        print(f"  Could not fetch weather: {e}")
    print()

# ============================================================
# STEP 4: News Headlines (API + list slicing)
# ============================================================

def show_news():
    """Fetch top news headlines."""
    print("--- TOP NEWS ---")
    try:
        import requests
        # Using a free RSS-to-JSON service
        url = "https://wttr.in/:help"  # placeholder
        # For real news, you'd use NewsAPI (free tier):
        # url = "https://newsapi.org/v2/top-headlines?country=de&apiKey=YOUR_KEY"

        # For now, show placeholder
        headlines = [
            "Tech stocks surge as AI adoption accelerates",
            "Germany announces new green energy initiative",
            "Champions League final breaks viewership records",
            "New study reveals benefits of 4-day work week",
            "SpaceX completes historic Mars cargo mission",
        ]
        for i, headline in enumerate(headlines, 1):
            print(f"  {i}. {headline}")
    except Exception as e:
        print(f"  Could not fetch news: {e}")
    print()

# ============================================================
# STEP 5: Menu system (while loop, input handling)
# ============================================================

def show_menu():
    """Display the main menu."""
    print("--- MENU ---")
    print("  [1] Refresh dashboard")
    print("  [2] Add to-do")
    print("  [3] Complete to-do")
    print("  [4] Delete to-do")
    print("  [5] Weather only")
    print("  [6] News only")
    print("  [0] Exit")
    print()

def show_full_dashboard():
    """Display the complete dashboard."""
    clear_screen()
    show_header()
    show_weather()
    show_news()
    show_todos()
    show_menu()

# ============================================================
# MAIN LOOP
# ============================================================

def main():
    show_full_dashboard()

    while True:
        choice = input("  > ").strip()

        if choice == "1":
            show_full_dashboard()
        elif choice == "2":
            add_todo()
            print()
        elif choice == "3":
            complete_todo()
            print()
        elif choice == "4":
            delete_todo()
            print()
        elif choice == "5":
            print()
            show_weather()
        elif choice == "6":
            print()
            show_news()
        elif choice == "0":
            print("\n  Goodbye! Have a great day.\n")
            break
        else:
            print("  Invalid option. Try 1-6 or 0 to exit.\n")

if __name__ == "__main__":
    main()
