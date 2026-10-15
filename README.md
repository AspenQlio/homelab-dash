# Homelab Dashboard

> A minimalist, monochromatic dashboard for your homelab designed with strict aesthetics and raw functionality.

Homelab Dashboard is a clean, data-first interface that gives you real-time telemetry and easy access to your services. It integrates directly with Docker and Pi-hole, allowing you to monitor your server's vitals without unnecessary fluff.

## Features

- **Dynamic Configuration:** Add and manage your services directly via the UI without touching configuration files.
- **Real-Time Telemetry:** Monitor your server's CPU, RAM, and Disk usage instantly.
- **Docker Engine Sync:** Automatically reads `/var/run/docker.sock` to display running containers.
- **Pi-Hole Integration:** Displays real-time ad-blocking metrics from your local Pi-hole instance.
- **Neo-Brutalist UI:** Hover and active states mimic physical mechanical switches for a tactile feel.

## Tech Stack

- **Frontend:** React + Vite (Pure CSS Monochromatic Theme)
- **Backend:** Python + FastAPI
- **Deployment:** Multi-stage Docker build

## Getting Started

The dashboard is built to be "Plug & Play" using Docker. No prior knowledge of React or Python is required.

### Prerequisites

- Docker and Docker Compose installed on your server.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/homelab-dash.git
   cd homelab-dash
   ```

2. **Start the services:**
   Run the following command to build and start the dashboard in the background:
   ```bash
   docker compose up -d --build
   ```
   *Note: The dashboard runs on port `9000` by default. You can change this in the `docker-compose.yml` file.*

## Usage

1. Open your browser and navigate to `http://YOUR_SERVER_IP:9000`.
2. Scroll to the bottom and click the **[ + ADD SERVICE ]** block.
3. Fill in the modal with your service details (Name, Description, Tag, and URL).
4. The dashboard will instantly update and save your configuration permanently.

*Advanced:* You can also manually edit the `backend/config.json` file inside the directory to manage your services.

## License

This project is licensed under the MIT License.
