# OPENCODE // HOMELAB DASHBOARD

> A brutalist, ultra-minimalist, monochromatic dashboard for your homelab. 
Designed with strict aesthetics and raw functionality. No fluff, just data.

## // FEATURES
* **Dynamic Configuration:** Add your services via a simple `config.json` without touching the code.
* **Real-Time Telemetry:** Monitors your server's CPU, RAM, and Disk directly.
* **Docker Engine Sync:** Reads `/var/run/docker.sock` to display running containers.
* **Pi-Hole Integration:** Displays real-time ad-blocking metrics.
* **Neo-Brutalist UI:** Hover and active states mimic physical mechanical switches. 

## // INSTALLATION (DOCKER)

1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/homelab-dash.git
cd homelab-dash
```

2. Edit your services in `backend/config.json`:
```json
{
  "pihole_url": "http://192.168.1.X",
  "services": [
    { "id": 1, "name": "ROUTER", "desc": "Gateway", "port": "80", "type": "NET", "url": "http://192.168.1.1" }
  ]
}
```

3. Spin up the container:
```bash
docker compose up -d
```

## // STACK
* Frontend: React + Vite
* Backend: Python + FastAPI
* Styling: Pure CSS (Monochromatic OpenCode Theme)

## // LICENSE
MIT
