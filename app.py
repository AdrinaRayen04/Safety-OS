
from flask import Flask, render_template, Response, request, redirect, url_for, session, jsonify
import cv2
from ultralytics import YOLO
import sqlite3
import os
import requests
from datetime import datetime
app = Flask(__name__)
app.secret_key = "safety_project_key_2025"


# Initialize YOLO
model = YOLO("models/best.pt")
current_status = "System Initializing..."
# Database setup
def init_db():
    conn = sqlite3.connect('industry_safety.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS chat_history (user TEXT, message TEXT, response TEXT)')
    c.execute('''
CREATE TABLE IF NOT EXISTS audit_logs (
    timestamp TEXT,
    status_message TEXT
)
''')

    conn.commit()
    conn.close()

init_db()

# --- CAMERA LOGIC ---
def gen_frames():
    global current_status
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        results = model(frame)
        
        # Get detected class names
        detected_labels = [model.names[int(c)] for c in results[0].boxes.cls]
        missing = []
        if 'NO-Hardhat' in detected_labels: 
            missing.append("HARD HAT")
        if 'NO-Mask' in detected_labels: 
            missing.append("MASK")
        if 'NO-Safety Vest' in detected_labels: 
            missing.append("SAFETY VEST")

        # Determine current status
        if missing:
            new_status = f"⚠️ ALERT: {', '.join(missing)} MISSING"
        elif len(detected_labels) > 0:
            new_status = "✅ ALL PPE DETECTED"
        else:
            new_status = "🔍 Scanning for personnel..."

        # If status changed, update and log it
        if new_status != current_status:
            current_status = new_status
            if "ALERT" in current_status:  # Only log alerts
                conn = sqlite3.connect('industry_safety.db')
                conn.execute(
                    "INSERT INTO audit_logs (timestamp, status_message) VALUES (?, ?)",
                    (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), current_status)
                )
                conn.commit()
                conn.close()

        # Annotate frame and yield
        annotated_frame = results[0].plot()
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


# --- ROUTES ---
@app.route('/report_hazard')
def report_hazard():
    return "<h1>Hazard Reporting System</h1><p>Log active site risks here.</p>"

@app.route('/documents')
def documents():
    return "<h1>Safety Manuals & Documents</h1><p>Access ISO 45001 and PPE compliance PDFs.</p>"

@app.route('/emergency')
def emergency():
    return "<h1>Emergency Contact List</h1><p>Ambulance: 911 | Site Lead: 555-0199</p>"

@app.route('/history')
def history():
    return "<h1>Audit History Logs</h1><p>Reviewing stored safety logs from the database.</p>"

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')  

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message", "")

    try:
        response = requests.post(
            "http://127.0.0.1:11434/api/chat",
            headers={"Content-Type": "application/json"},
            json={
                "model": "mistral:latest",
                "messages": [
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 150,  # smaller response
                "temperature": 0.7,
                "stream":False
            },
            timeout=120
        )

        print("OLLAMA RESPONSE:", response.text)

        if response.status_code != 200:
            return jsonify({"response": "AI engine error"})

        data = response.json()
        return jsonify({"response": data["message"]["content"]})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"response": "Local AI service not responding"})

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        u, p = request.form['username'], request.form['password']
        conn = sqlite3.connect('industry_safety.db')
        conn.execute('INSERT INTO users VALUES (?, ?)', (u, p))
        conn.commit()
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    u, p = request.form['username'], request.form['password']
    conn = sqlite3.connect('industry_safety.db')
    user = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (u, p)).fetchone()
    if user:
        session['user'] = u
        return redirect(url_for('home'))
    return "Invalid Credentials. Go back and try again."

@app.route('/home')
def home():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('home.html')

@app.route('/camera_page')
def camera_page():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('camera.html')

@app.route('/video_feed')
def video_feed():
    # This matches url_for('video_feed') in the HTML
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/get_status')
def get_status():
    global current_status
    return jsonify({"status": current_status})

@app.route("/test")
def test():
    return "FLASK IS RUNNING"
ai_enabled = True
detection_threshold = 0.5

@app.route('/snapshot', methods=['POST'])
def snapshot():
    # Ensure a directory exists for captures
    if not os.path.exists('captures'):
        os.makedirs('captures')
    
    # Generate filename with timestamp
    filename = f"incident_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    filepath = os.path.join('captures', filename)
    
    # Logic: Capture the global 'current_frame' from your camera loop
    # (Assuming you have a global 'frame' variable in your video_feed logic)
    global last_processed_frame
    if last_processed_frame is not None:
        cv2.imwrite(filepath, last_processed_frame)
        return jsonify({"status": "success", "filename": filename})
    return jsonify({"status": "error", "message": "No frame available"})

@app.route('/toggle_ai', methods=['POST'])
def toggle_ai():
    global ai_enabled
    data = request.get_json()
    ai_enabled = data.get('active', True)
    return jsonify({"status": "AI state updated", "active": ai_enabled})

alarm_active = True

@app.route('/toggle_alarm', methods=['POST'])
def toggle_alarm():
    global alarm_active
    data = request.get_json()
    alarm_active = data.get('enabled', True)
    return jsonify({"status": "Alarm state updated", "active": alarm_active})

@app.route('/audit_logs')
def audit_logs():
    conn = sqlite3.connect('industry_safety.db')
    logs = conn.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC").fetchall()
    conn.close()
    return render_template('audit_logs.html', logs=logs)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))   # ✅ redirect to GET login page


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
