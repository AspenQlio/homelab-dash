"""FastAPI backend for the homelab dashboard."""

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

import docker
import httpx
import psutil
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, ValidationError

CONFIG_FILE: Final = Path("backend/config.json")
GOTERO_STATE_FILE: Final = Path(os.getenv("GOTERO_STATE_FILE", "/app/data/gotero.json"))
PIHOLE_PASSWORD: Final = os.getenv("PIHOLE_PASSWORD", "")


class GoteroState(BaseModel):
    """Persisted number of commits awaiting publication."""

    model_config = ConfigDict(frozen=True)
    pending: int


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
pihole_sid: str | None = None


def load_config() -> dict:
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"pihole_url": "http://pi.hole", "services": []}


def save_config(data: dict) -> None:
    CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_gotero_state(path: Path = GOTERO_STATE_FILE) -> GoteroState:
    """Loads persisted queue state or returns an empty queue."""
    try:
        return GoteroState.model_validate_json(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValidationError):
        return GoteroState(pending=0)


def save_gotero_state(state: GoteroState, path: Path = GOTERO_STATE_FILE) -> None:
    """Atomically persists queue state inside the mounted data directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(state.model_dump_json(), encoding="utf-8")
    temporary.replace(path)


@app.get("/api/config")
def get_config() -> dict:
    return load_config()


@app.post("/api/services")
async def add_service(request: Request) -> dict:
    new_service = await request.json()
    config = load_config()
    services = config.setdefault("services", [])
    new_service["id"] = max((service.get("id", 0) for service in services), default=0) + 1
    if "port" not in new_service:
        parts = new_service.get("url", "").split(":")
        new_service["port"] = parts[-1].replace("/", "") if len(parts) > 2 else "80"
    services.append(new_service)
    save_config(config)
    return {"status": "success", "service": new_service}


@app.get("/api/system")
def get_system() -> dict:
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    return {
        "cpu": psutil.cpu_percent(interval=0.1),
        "ram": ram.percent,
        "ram_used": round(ram.used / (1024**3), 1),
        "disk": disk.percent,
        "disk_used": round(disk.used / (1024**3), 1),
        "uptime": round((datetime.now(tz=UTC).timestamp() - psutil.boot_time()) / 3600, 1),
    }


@app.get("/api/docker")
def get_docker() -> dict:
    try:
        containers = docker.from_env().containers.list(all=True)
        return {
            "status": "online",
            "running": sum(container.status == "running" for container in containers),
            "total": len(containers),
        }
    except docker.errors.DockerException:
        return {"status": "offline", "running": 0, "total": 0}


async def fetch_pihole_stats(base_url: str, sid: str) -> dict | None:
    async with httpx.AsyncClient(timeout=2.0) as client:
        response = await client.get(f"{base_url}/api/stats/summary", headers={"sid": sid})
    if response.status_code != 200:
        return None
    data = response.json()
    return {
        "status": "online",
        "ads_blocked": data.get("queries", {}).get("blocked", 0),
        "ratio": round(data.get("queries", {}).get("percent_blocked", 0), 1),
        "domains": data.get("gravity", {}).get("domains_being_blocked", 0),
    }


@app.get("/api/pihole")
async def get_pihole() -> dict:
    global pihole_sid
    base_url = load_config().get("pihole_url", "http://pi.hole")
    if not PIHOLE_PASSWORD:
        return {"status": "unconfigured", "ads_blocked": 0, "ratio": 0, "domains": 0}
    try:
        if pihole_sid:
            stats = await fetch_pihole_stats(base_url, pihole_sid)
            if stats is not None:
                return stats
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.post(
                f"{base_url}/api/auth",
                json={"password": PIHOLE_PASSWORD},
            )
            response.raise_for_status()
        session = response.json().get("session", {})
        if session.get("valid"):
            pihole_sid = session["sid"]
            stats = await fetch_pihole_stats(base_url, pihole_sid)
            if stats is not None:
                return stats
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        pass
    return {"status": "offline", "ads_blocked": 0, "ratio": 0, "domains": 0}


@app.post("/api/gotero")
def update_gotero(state: GoteroState) -> dict[str, str]:
    save_gotero_state(state)
    return {"status": "success"}


@app.get("/api/gotero")
def get_gotero() -> GoteroState:
    return load_gotero_state()


if Path("dist").exists():
    app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str) -> FileResponse:
        del full_path
        return FileResponse("dist/index.html")
