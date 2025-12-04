# Dockerized Nexus Web Honeypot And Threat Console
![LOGO](https://github.com/user-attachments/assets/085e7e78-c7d3-47aa-ac2f-556bbf6053dc)

This folder contains a fully containerized version of the Nexus Web Honeypot.

## Prerequisites
- Docker
- Docker Compose

## How to Run

1. **Start the Honeypot**:  
Run the following command in this directory:
```bash
docker-compose up -d --build
```
This will build the image and start the `honeypot` container (and the `hydra` container).

2. **Access the App**:
- **Honeypot Login**: http://localhost:5000/admin  
- **Dashboard**: http://localhost:5000/dashboard-login  
    - **Username**: `operator`  
    - **Password**: `nexus-secure-882a`

3. **Run Attacks from Hydra Container**:  
You can use the built-in `hydra` container to simulate attacks within the Docker network.

Access the Hydra container:
```bash
docker exec -it attacker-hydra /bin/sh
```

This `/bin/sh` opens up a shell inside the attacker container.

Run an attack (targeting the `honeypot` service name):
```bash
hydra -l admin -P /passwords.txt -s 5000 nexus-honeypot http-post-form "/admin:username=^USER^&password=^PASS^:Incorrect username or password"
```

*Note: The honeypot uses a secure password. Hydra will complete without finding a match, which confirms the honeypot is successfully trapping and logging attempts without being breached.*

4. **View Logs**:
```bash
docker-compose logs -f honeypot
```

5. **Stop**:
```bash
docker-compose down
```

## 🖼 Screenshots (placeholders)

### Fake Website
<img width="2311" height="1746" alt="Screenshot 2025-12-04 at 19-44-18 Apex Solutions" src="https://github.com/user-attachments/assets/aa56d585-10d0-4b5a-8175-af8aa8d37a38" />

### Login Portal (HoneyPot)
<img width="2311" height="1520" alt="Screenshot 2025-12-04 at 19-46-22 Login - Apex Solutions" src="https://github.com/user-attachments/assets/bc6077df-9670-46d2-a4cc-1265fdc3d3d0" />

### HoneyPot-Management-Daashboard
<img width="2311" height="1520" alt="Screenshot 2025-12-04 at 19-45-18 Nexus Security Access" src="https://github.com/user-attachments/assets/cf2a889d-c11d-41a6-82c1-55e7aa616918" />

### Command Center  
<img width="2311" height="1520" alt="Screenshot 2025-12-04 at 19-45-49 Nexus SOC Command" src="https://github.com/user-attachments/assets/b9338d48-3503-49e1-9fda-76073e22e2d7" />

### Live Threat Feed  
<img width="2311" height="1520" alt="Screenshot 2025-12-04 at 19-45-56 Nexus SOC Command" src="https://github.com/user-attachments/assets/87514a72-e7f0-4bfe-b7a0-fb9f7af79de0" />

### Attacker Database
<img width="2311" height="1520" alt="Screenshot 2025-12-04 at 19-46-02 Nexus SOC Command" src="https://github.com/user-attachments/assets/2ac71ad2-2708-4897-9cf9-01422f873ac0" />

### Detailed Profile Review
<img width="2311" height="1520" alt="Screenshot 2025-12-04 at 20-03-28 Nexus SOC Command" src="https://github.com/user-attachments/assets/aea5374b-626e-443e-91c1-b99fd70d120d" />


**For Non Dockerized Version Or Need Any Additional Details Visit** --> https://github.com/AkhilBangaru/Nexus_Web_Honeypot/


## ⚠️ Security Disclaimer
> **This project is STRICTLY for educational & research purposes.**  
> Do **NOT** deploy publicly or attempt attacks on systems without explicit permission.  
> The author assumes zero liability for misuse.

---

## 🚀 Future Roadmap
- SMTP email alerts  
- Automated attacker fingerprinting  
- CSV / JSON export  
- High-interaction fake admin shell  
- ML-based anomaly detection  

---

## 📜 License
Released under the **MIT License** — free for personal & commercial use.

---

## ⭐ Final Note
If you like this project, consider giving it a **GitHub star ⭐** and contributing enhancements!
