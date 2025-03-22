import sqlite3
import time
import psutil
import pygetwindow as gw
from pynput import keyboard, mouse
import threading
import queue

# Initialize Database
conn = sqlite3.connect("user_activity.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        event_type TEXT,
        data TEXT
    )
''')
conn.commit()

# Use a queue for thread-safe database logging
log_queue = queue.Queue()

# Function to process queued log events
def process_logs():
    while True:
        timestamp, event_type, data = log_queue.get()
        cursor.execute("INSERT INTO activity_log (timestamp, event_type, data) VALUES (?, ?, ?)",
                       (timestamp, event_type, data))
        conn.commit()
        print(f"[LOG] {event_type}: {data}")

# Start a separate thread for database operations
db_thread = threading.Thread(target=process_logs, daemon=True)
db_thread.start()

# Function to add logs to queue
def log_event(event_type, data):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_queue.put((timestamp, event_type, data))

# Track Keystrokes
def on_key_press(key):
    try:
        log_event("Keystroke", str(key.char))
    except AttributeError:
        log_event("Keystroke", str(key))

keyboard_listener = keyboard.Listener(on_press=on_key_press)

# Track Mouse Clicks
def on_click(x, y, button, pressed):
    if pressed:
        log_event("Mouse Click", f"Button {button} at ({x}, {y})")

mouse_listener = mouse.Listener(on_click=on_click)

# Track Active Window Changes
last_window = None

def track_active_window():
    global last_window
    while True:
        try:
            active_window = gw.getActiveWindow()
            if active_window and active_window.title != last_window:
                log_event("Window Change", active_window.title)
                last_window = active_window.title
        except:
            pass
        time.sleep(2)

# Run Tracking in Background
keyboard_thread = threading.Thread(target=keyboard_listener.start, daemon=True)
mouse_thread = threading.Thread(target=mouse_listener.start, daemon=True)
window_thread = threading.Thread(target=track_active_window, daemon=True)

keyboard_thread.start()
mouse_thread.start()
window_thread.start()

print("🟢 Tracking started... Press CTRL+C to stop.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("🛑 Stopping tracking...")
    conn.close()
