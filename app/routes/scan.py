# app/routes/scan.py
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import asyncio, time, socket, json, subprocess, httpx
from typing import List
from sqlalchemy.orm import Session

# DB
from app.db.database import get_db
from app.db.crud import create_scan_history, list_scan_history

# Utils parser windows
from app.utils.parse_utils import parse_netsh_interfaces, parse_ipconfig

router = APIRouter(prefix="/scan", tags=["Scan"])

# ======================
# INPUT MODELS
# ======================

class RunScanIn(BaseModel):
    url: str

class BulkScanIn(BaseModel):
    urls: List[str]

# ======================
# WEBSOCKET MANAGER
# ======================

class ConnectionManager:
    def __init__(self):
        self.active = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: dict):
        text = json.dumps(message, default=str)
        for ws in list(self.active):
            try:
                await ws.send_text(text)
            except:
                self.disconnect(ws)

manager = ConnectionManager()

# ======================================
# FUNGSI HTTP SCAN
# ======================================

async def do_http_scan(url: str, timeout=15):
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    result = {
        "url": url,
        "status_code": None,
        "elapsed_ms": None,
        "content_length": None,
        "dns": None,
        "error": None
    }

    # HTTP part
    try:
        start = time.time()
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as c:
            r = await c.get(url)
        result["status_code"] = r.status_code
        result["elapsed_ms"] = int((time.time() - start)*1000)
        result["content_length"] = len(r.content)
    except Exception as e:
        result["error"] = str(e)

    # DNS part
    try:
        host = url.split("//")[1].split("/")[0]
        result["dns"] = socket.gethostbyname_ex(host)
    except:
        result["dns"] = None

    return result

# ======================================
# 1. RUN SCAN (SINGLE)
# ======================================

@router.post("/run")
async def run_scan(payload: RunScanIn, db: Session = Depends(get_db)):
    url = payload.url.strip()
    if not url:
        raise HTTPException(400, "URL kosong")

    result = await do_http_scan(url)

    rec = create_scan_history(
        db,
        url=result["url"],
        status_code=result["status_code"],
        latency_ms=result["elapsed_ms"],
        content_length=result["content_length"],
        dns=json.dumps(result["dns"]),
        error=result["error"],
        source="run"
    )

    await manager.broadcast({
        "type": "scan_result",
        "data": {
            "id": rec.id,
            "url": rec.url,
            "status_code": rec.status_code,
            "latency_ms": rec.latency_ms,
            "created_at": str(rec.created_at)
        }
    })

    return {"ok": True, "result": result, "id": rec.id}

# ======================================
# 2. BULK SCAN
# ======================================

scan_stop_flag = False

@router.post("/bulk")
async def bulk_scan(payload: BulkScanIn, db: Session = Depends(get_db)):
    global scan_stop_flag
    scan_stop_flag = False

    urls = [u.strip() for u in payload.urls if u.strip()]
    if not urls:
        raise HTTPException(400, "Tidak ada URL")

    semaphore = asyncio.Semaphore(8)

    async def worker(u):
        global scan_stop_flag
        if scan_stop_flag:
            return {"url": u, "stopped": True}

        async with semaphore:
            res = await do_http_scan(u)
            rec = create_scan_history(
                db,
                url=res["url"],
                status_code=res["status_code"],
                latency_ms=res["elapsed_ms"],
                content_length=res["content_length"],
                dns=json.dumps(res["dns"]),
                error=res["error"],
                source="bulk"
            )

            await manager.broadcast({
                "type": "scan_result",
                "data": {
                    "id": rec.id,
                    "url": rec.url,
                    "status_code": rec.status_code,
                    "latency_ms": rec.latency_ms,
                    "created_at": str(rec.created_at)
                }
            })

            return res

    results = await asyncio.gather(*[worker(u) for u in urls])
    return {"ok": True, "count": len(results), "results": results}

# ======================================
# 3. STOP BULK SCAN
# ======================================

@router.post("/stop")
async def stop_scan():
    global scan_stop_flag
    scan_stop_flag = True
    return {"ok": True, "message": "Bulk scan dihentikan"}

# ======================================
# 4. HISTORY
# ======================================

@router.get("/history")
def get_history(limit: int = 100, db: Session = Depends(get_db)):
    rows = list_scan_history(db, limit)
    return {
        "ok": True,
        "rows": [
            {
                "id": r.id,
                "url": r.url,
                "status_code": r.status_code,
                "latency_ms": r.latency_ms,
                "content_length": r.content_length,
                "dns": r.dns,
                "error": r.error,
                "source": r.source,
                "created_at": str(r.created_at)
            }
            for r in rows
        ]
    }

# ======================================
# 5. SCAN NETWORK
# ======================================

@router.get("/network")
async def scan_network(db: Session = Depends(get_db)):
    try:
        wifi_raw = subprocess.check_output("netsh wlan show interfaces", shell=True, text=True)
        wifi = parse_netsh_interfaces(wifi_raw)

        ip_raw = subprocess.check_output("ipconfig /all", shell=True, text=True)
        ip_data = parse_ipconfig(ip_raw)

        rec = create_scan_history(
            db,
            url="network://local",
            status_code=None,
            latency_ms=None,
            content_length=None,
            dns=json.dumps({"wifi": wifi, "ip": ip_data}),
            error=None,
            source="network"
        )

        await manager.broadcast({
            "type": "network_result",
            "data": {
                "id": rec.id,
                "wifi": wifi,
                "ip": ip_data,
                "created_at": str(rec.created_at)
            }
        })

        return {"ok": True, "wifi": wifi, "ip": ip_data}

    except Exception as e:
        return {"ok": False, "error": str(e)}

# ======================================
# 6. AGENT
# ======================================

@router.get("/agent")
async def scan_agent(db: Session = Depends(get_db)):
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get("http://127.0.0.1:8008/")
        data = r.json()

        create_scan_history(
            db,
            url="agent://local",
            status_code=200,
            latency_ms=0,
            content_length=0,
            dns=json.dumps(data),
            error=None,
            source="agent"
        )

        return {"ok": True, "agent": data}

    except Exception as e:
        return {"ok": False, "error": str(e)}

# ======================================
# 7. WEBSOCKET
# ======================================

@router.websocket("/ws")
async def ws_stream(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
