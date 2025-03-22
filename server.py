from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# API Route to Fetch Activity Logs
@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        conn = sqlite3.connect("user_activity.db")
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, event_type, data FROM activity_log ORDER BY id DESC LIMIT 20")
        logs = cursor.fetchall()
        conn.close()

        # Convert logs to JSON
        logs_list = [{"timestamp": log[0], "event_type": log[1], "data": log[2]} for log in logs]
        return jsonify(logs_list)

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
