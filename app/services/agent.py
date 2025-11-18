# agent/agent.py  (minimal Windows agent)
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import subprocess, os
from dotenv import load_dotenv
from .parse_utils import parse_netsh_interfaces, parse_ipconfig

load_dotenv(dotenv_path=".env")
AGENT_TOKEN = os.getenv("AGENT_TOKEN", "")

app = FastAPI()

def check_token(req: Request):
    if not AGENT_TOKEN:
        return True
    token = req.headers.get("x-agent-token") or req.headers.get("X-AGENT-TOKEN")
    if not token or token != AGENT_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid agent token")
    return True

@app.get("/")
async def root():
    return {"status":"agent-running"}

@app.get("/scan-wifi")
async def scan_wifi(request: Request):
    check_token(request)
    # run netsh to get interface info
    try:
        raw = subprocess.check_output("netsh wlan show interfaces", shell=True, stderr=subprocess.STDOUT, text=True)
        info = parse_netsh_interfaces(raw)
        # ipconfig for IP & gateway
        raw_ip = subprocess.check_output("ipconfig /all", shell=True, stderr=subprocess.STDOUT, text=True)
        ipinfo = parse_ipconfig(raw_ip)
        return JSONResponse({"os":"windows", "interfaces": info, "ipinfo": ipinfo})
    except Exception as e:
        return JSONResponse({"error": str(e)})
