import subprocess
import re
import sys
import os
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def start_tunnel(port: int = 8080) -> str | None:
    exe_path = BASE_DIR / "cloudflared.exe"
    if not exe_path.exists():
        return None

    cmd = [str(exe_path), "tunnel", "--url", f"http://127.0.0.1:{port}"]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    tunnel_url = None
    start_time = time.time()
    
    # Wait up to 20 seconds for the URL
    while time.time() - start_time < 20:
        line = proc.stdout.readline()
        if not line and proc.poll() is not None:
            break
        if line:
            match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
            if match:
                tunnel_url = match.group(0)
                break

    return tunnel_url
