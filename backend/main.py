from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import psutil
import docker
import httpx
import json
import os
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CONFIG_FILE = "backend/config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"pihole_url": "http://pi.hole", "services": []}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.get("/api/config")
def get_config():
    return load_config()

@app.post("/api/services")
async def add_service(request: Request):
    new_service = await request.json()
    cfg = load_config()
    
    # Calcular el nuevo ID
    max_id = max([s.get("id", 0) for s in cfg.get("services", [])], default=0)
    new_service["id"] = max_id + 1
    
    # Extraer el puerto si viene en la url, si no poner por defecto
    if "port" not in new_service:
        parts = new_service.get("url", "").split(":")
        new_service["port"] = parts[-1].replace("/", "") if len(parts) > 2 else "80"
        
    cfg["services"].append(new_service)
    save_config(cfg)
    return {"status": "success", "service": new_service}

@app.get("/api/system")
def get_system():
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return {
        "cpu": cpu,
        "ram": ram.percent,
        "ram_used": round(ram.used / (1024**3), 1),
        "disk": disk.percent,
        "disk_used": round(disk.used / (1024**3), 1),
        "uptime": round((datetime.now().timestamp() - psutil.boot_time()) / 3600, 1)
    }

@app.get("/api/docker")
def get_docker():
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        running = sum(1 for c in containers if c.status == 'running')
        return {"status": "online", "running": running, "total": len(containers)}
    except Exception:
        return {"status": "offline", "running": 0, "total": 0}

@app.get("/api/pihole")
async def get_pihole():
    cfg = load_config()
    pihole_api = f"{cfg.get('pihole_url', 'http://pi.hole')}/admin/api.php?summaryRaw"
    try:
        async with httpx.AsyncClient(timeout=1.0) as client:
            resp = await client.get(pihole_api)
            data = resp.json()
            return {
                "status": "online",
                "ads_blocked": data.get("ads_blocked_today", 0),
                "ratio": round(data.get("ads_percentage_today", 0), 1),
                "domains": data.get("domains_being_blocked", 0)
            }
    except Exception:
        return {"status": "mock", "ads_blocked": 14205, "ratio": 12.4, "domains": 185002}

if os.path.exists("dist"):
    app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        return FileResponse("dist/index.html")
