# Dockerized Nexus Web Honeypot

This folder contains a fully containerized version of the Nexus Web Honeypot.

## Prerequisites
-   Docker
-   Docker Compose

## How to Run

1.  **Start the Honeypot**:
    Run the following command in this directory:
    ```bash
    docker-compose up -d --build
    ```
    This will build the image and start the `honeypot` container (and the `hydra` container).

2.  **Access the App**:
    -   **Honeypot Login**: [http://localhost:5000/admin](http://localhost:5000/admin)
    -   **Dashboard**: [http://localhost:5000/dashboard-login](http://localhost:5000/dashboard-login)
        -   **Username**: `operator`
        -   **Password**: `nexus-secure-882a`

3.  **Run Attacks from Hydra Container**:
    You can use the built-in `hydra` container to simulate attacks within the Docker network.
    
    Access the Hydra container:
    ```bash
    docker exec -it attacker-hydra /bin/sh
    ```

    This /bin/sh opens up a shell in the container.
    
    Run an attack (targeting the `honeypot` service name):
    ```bash
    hydra -l admin -P /passwords.txt -s 5000 nexus-honeypot http-post-form "/admin:username=^USER^&password=^PASS^:Incorrect username or password"
    ```
    *Note: The honeypot uses a secure password. Hydra will complete without finding a match, which confirms the honeypot is successfully trapping and logging attempts without being breached.*

4.  **View Logs**:
    ```bash
    docker-compose logs -f honeypot
    ```

5.  **Stop**:
    ```bash
    docker-compose down
    ```
