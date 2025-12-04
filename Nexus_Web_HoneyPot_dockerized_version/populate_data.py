import sqlite3
from datetime import datetime, timedelta
import random

DB_NAME = "honeypot.db"
import sqlite3
from datetime import datetime, timedelta
import random

DB_NAME = "honeypot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY, ip TEXT, user_agent TEXT, 
                  username TEXT, password TEXT, timestamp DATETIME, 
                  location TEXT, lat REAL, lon REAL, country TEXT)''')
    conn.commit()
    conn.close()

def populate():
    init_db()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Clear existing data
    c.execute("DELETE FROM logs")
    
    ips = [
        ("192.168.1.55", "Moscow, Russia", 55.7558, 37.6173, "Russia"),
        ("10.0.0.2", "Beijing, China", 39.9042, 116.4074, "China"),
        ("172.16.0.5", "New York, USA", 40.7128, -74.0060, "USA"),
        ("45.33.22.11", "London, UK", 51.5074, -0.1278, "UK"),
        ("185.22.1.9", "Berlin, Germany", 52.5200, 13.4050, "Germany")
    ]
    
    payloads = [
        ("admin", "password123"),
        ("root", "toor"),
        ("' OR 1=1 --", "anything"),
        ("admin", "' UNION SELECT 1,2,3 --"),
        ("<script>alert(1)</script>", "test"),
        ("user", "123456")
    ]

    print("Populating database with dummy data...")
    
    for _ in range(50):
        ip_data = random.choice(ips)
        payload = random.choice(payloads)
        
        # Random time in last 24 hours
        time_offset = random.randint(0, 24 * 60)
        timestamp = datetime.now() - timedelta(minutes=time_offset)

        c.execute("INSERT INTO logs (ip, user_agent, username, password, timestamp, location, lat, lon, country) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (ip_data[0], "Mozilla/5.0 (Dummy)", payload[0], payload[1], timestamp, ip_data[1], ip_data[2], ip_data[3], ip_data[4]))

    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    populate()
