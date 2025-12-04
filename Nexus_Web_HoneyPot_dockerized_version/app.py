from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from datetime import datetime
import sqlite3
import requests
import json
import os
import re

app = Flask(__name__)
app.secret_key = os.urandom(24) # Required for session

# --- CONFIGURATION ---
DB_NAME = "honeypot.db"
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN" # Placeholder
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID" # Placeholder

# --- VULNERABLE MODE CONFIGURATION ---
HONEYPOT_USERNAME = "admin" 
HONEYPOT_PASSWORD = "Sup3rS3cur3R@nd0mP@ssw0rd!999" # Changed to be unguessable

# --- REAL DASHBOARD CREDENTIALS ---
REAL_ADMIN_USER = "operator"
REAL_ADMIN_PASS = "nexus-secure-882a"

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Added lat, lon, country columns
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY, ip TEXT, user_agent TEXT, 
                  username TEXT, password TEXT, timestamp DATETIME, 
                  location TEXT, lat REAL, lon REAL, country TEXT)''')
    conn.commit()
    conn.close()

# --- GEOIP HELPER ---
def get_geoip_data(ip):
    if ip == '127.0.0.1':
        return "Localhost", 0.0, 0.0, "Local"
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = response.json()
        if data['status'] == 'success':
            location = f"{data['city']}, {data['country']}"
            return location, data['lat'], data['lon'], data['country']
        return "Unknown", 0.0, 0.0, "Unknown"
    except:
        return "Unknown", 0.0, 0.0, "Unknown"

# --- TELEGRAM ALERT FUNCTION ---
def send_telegram_alert(ip, username, password, location):
    msg = f"🚨 **Honeypot Triggered!**\n\nIP: {ip}\nLocation: {location}\nUser: {username}\nPass: {password}"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Alert failed: {e}")

# --- PAYLOAD HIGHLIGHTER ---
def highlight_payload(text):
    if not text: return ""
    # Keywords to highlight
    keywords = ["UNION", "SELECT", "DROP", "INSERT", "UPDATE", "DELETE", "OR", "AND", "1=1", "<script>", "alert(", "javascript:"]
    
    # Simple case-insensitive replacement with neon span
    for kw in keywords:
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        text = pattern.sub(lambda m: f'<span class="neon-highlight">{m.group(0)}</span>', text)
    return text

# --- PUBLIC FACE ROUTES ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

# --- THE TRAP (Fake Admin) ---
@app.route('/admin', methods=['GET', 'POST'])
def fake_admin():
    if request.method == 'POST':
        # 1. Capture Data
        ip = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Get GeoIP data
        location, lat, lon, country = get_geoip_data(ip)

        # 2. Log to DB
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO logs (ip, user_agent, username, password, timestamp, location, lat, lon, country) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (ip, user_agent, username, password, datetime.now(), location, lat, lon, country))
        conn.commit()
        conn.close()

        # 3. Optional: Trigger Alert for specific keywords
        suspicious_patterns = ["'", "OR", "1=1", "script", "UNION", "SELECT", "DROP"]
        if any(x.upper() in username.upper() for x in suspicious_patterns) or any(x.upper() in password.upper() for x in suspicious_patterns):
            send_telegram_alert(ip, username, password, location)

        # 4. Check for "Vulnerable" Credentials (Hidden Feature)
        if username == HONEYPOT_USERNAME and password == HONEYPOT_PASSWORD:
            return "Login Successful! (Honeypot Vulnerable Mode Triggered)"

        # 5. The Fake Response (Always Fail otherwise)
        return render_template('login.html', error="Incorrect username or password.")

    return render_template('login.html')

# --- SECURE DASHBOARD LOGIN ---
@app.route('/dashboard-login', methods=['GET', 'POST'])
def dashboard_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == REAL_ADMIN_USER and password == REAL_ADMIN_PASS:
            session.permanent = False # Session expires when browser closes
            session['logged_in'] = True
            return redirect('/nexus-security-view-882a')
        else:
            return render_template('dashboard_login.html', error="Access Denied")
    return render_template('dashboard_login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

# --- DASHBOARD: COMMAND CENTER (Main) ---
@app.route('/nexus-security-view-882a')
def dashboard_command():
    if not session.get('logged_in'):
        return redirect('/dashboard-login')

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. KPIs
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT COUNT(*) FROM logs WHERE date(timestamp) = ?", (today,))
    total_attacks_today = c.fetchone()[0]

    c.execute("SELECT COUNT(DISTINCT ip) FROM logs")
    unique_attackers = c.fetchone()[0]

    # Top Vector Logic
    c.execute("SELECT username, password FROM logs")
    all_logs = c.fetchall()
    sqli_count = 0
    xss_count = 0
    brute_force_count = 0

    for u, p in all_logs:
        u_str = u or ""
        p_str = p or ""
        
        is_sqli = False
        is_xss = False
        
        # Check for SQLi
        if "OR" in u_str or "UNION" in u_str or "OR" in p_str or "UNION" in p_str:
            sqli_count += 1
            is_sqli = True
            
        # Check for XSS
        if "<script>" in u_str or "<script>" in p_str:
            xss_count += 1
            is_xss = True
            
        # If neither, assume Brute Force
        if not is_sqli and not is_xss:
            brute_force_count += 1
    
    # Determine winner
    counts = {'SQL Injection': sqli_count, 'XSS': xss_count, 'Brute Force': brute_force_count}
    top_vector = max(counts, key=counts.get) if all_logs else "None"

    # 2. Map Data (Lat, Lon)
    c.execute("SELECT lat, lon FROM logs WHERE lat != 0 AND lon != 0")
    map_points = c.fetchall()

    # 3. Velocity Graph (Attacks per Hour - Last 24h Rolling)
    # Get counts for each hour in the last 24 hours
    c.execute("""
        SELECT strftime('%H', timestamp) as hour, COUNT(*) 
        FROM logs 
        WHERE timestamp >= datetime('now', '-24 hours') 
        GROUP BY hour
    """)
    hourly_data = c.fetchall()
    attacks_per_hour = [0] * 24
    for hour, count in hourly_data:
        attacks_per_hour[int(hour)] = count

    conn.close()
    
    return render_template('dashboard_command.html', 
                           total_attacks=total_attacks_today,
                           unique_attackers=unique_attackers,
                           top_vector=top_vector,
                           map_points=json.dumps(map_points),
                           attacks_per_hour=json.dumps(attacks_per_hour))

# --- DASHBOARD: LIVE THREAT FEED ---
@app.route('/nexus-feed')
def dashboard_feed():
    if not session.get('logged_in'):
        return redirect('/dashboard-login')
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, timestamp, ip, username, password, user_agent FROM logs ORDER BY id DESC LIMIT 50")
    raw_logs = c.fetchall()
    conn.close()

    # Process logs for highlighting
    processed_logs = []
    for log in raw_logs:
        lid, ts, ip, user, pwd, ua = log
        # Determine type
        attack_type = "Brute Force"
        if "OR" in (user or "") or "UNION" in (user or ""): attack_type = "SQLi"
        elif "<script>" in (user or ""): attack_type = "XSS"
        
        # Highlight payload
        payload_display = highlight_payload(user) if user else highlight_payload(pwd)
        
        processed_logs.append({
            'id': lid,
            'timestamp': ts,
            'ip': ip,
            'type': attack_type,
            'payload': payload_display,
            'raw_user': user,
            'raw_pass': pwd,
            'ua': ua
        })

    return render_template('dashboard_feed.html', logs=processed_logs)

# --- DASHBOARD: ATTACKER PROFILE ---
@app.route('/nexus-profile/<ip>')
def dashboard_profile(ip):
    if not session.get('logged_in'):
        return redirect('/dashboard-login')

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Get all logs for this IP
    c.execute("SELECT timestamp, username, password, user_agent FROM logs WHERE ip = ? ORDER BY id DESC", (ip,))
    history = c.fetchall()
    
    # Get basic info (from first log or re-fetch)
    c.execute("SELECT location, country, lat, lon FROM logs WHERE ip = ? LIMIT 1", (ip,))
    info = c.fetchone()
    conn.close()

    location = info[0] if info else "Unknown"
    country = info[1] if info else "Unknown"
    
    # Mock ASN for MVP (Real lookup requires another API call)
    asn = "AS12345 (ISP Name)" 

    return render_template('dashboard_profile.html', 
                           ip=ip, 
                           location=location, 
                           country=country, 
                           asn=asn, 
                           history=history,
                           total_events=len(history))

# --- DASHBOARD: ATTACKER DATABASE (Index) ---
@app.route('/nexus-database')
def dashboard_database():
    if not session.get('logged_in'):
        return redirect('/dashboard-login')

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Get unique IPs with stats
    c.execute('''
        SELECT ip, location, country, COUNT(*) as count, MAX(timestamp) as last_seen 
        FROM logs 
        GROUP BY ip 
        ORDER BY count DESC
    ''')
    attackers = c.fetchall()
    conn.close()

    return render_template('dashboard_database.html', attackers=attackers)

# --- API FOR REAL-TIME UPDATES (Optional, keeping for Command Center polling) ---
@app.route('/api/stats')
def api_stats():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT COUNT(*) FROM logs WHERE date(timestamp) = ?", (today,))
    total_attacks = c.fetchone()[0]

    c.execute("SELECT COUNT(DISTINCT ip) FROM logs")
    unique_attackers = c.fetchone()[0]

    # Top Vector Logic (Replicated for API)
    c.execute("SELECT username, password FROM logs")
    all_logs = c.fetchall()
    sqli_count = 0
    xss_count = 0
    brute_force_count = 0

    for u, p in all_logs:
        u_str = u or ""
        p_str = p or ""
        is_sqli = False
        is_xss = False
        
        if "OR" in u_str or "UNION" in u_str or "OR" in p_str or "UNION" in p_str:
            sqli_count += 1
            is_sqli = True
        if "<script>" in u_str or "<script>" in p_str:
            xss_count += 1
            is_xss = True
        if not is_sqli and not is_xss:
            brute_force_count += 1
            
    counts = {'SQL Injection': sqli_count, 'XSS': xss_count, 'Brute Force': brute_force_count}
    top_vector = max(counts, key=counts.get) if all_logs else "None"

    # Velocity Graph Data
    c.execute("""
        SELECT strftime('%H', timestamp) as hour, COUNT(*) 
        FROM logs 
        WHERE timestamp >= datetime('now', '-24 hours') 
        GROUP BY hour
    """)
    hourly_data = c.fetchall()
    attacks_per_hour = [0] * 24
    for hour, count in hourly_data:
        attacks_per_hour[int(hour)] = count

    conn.close()

    return jsonify({
        'total_attacks': total_attacks,
        'unique_attackers': unique_attackers,
        'attacks_per_hour': attacks_per_hour,
        'top_vector': top_vector
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
