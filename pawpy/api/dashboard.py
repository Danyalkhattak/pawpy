"""Web dashboard with WebSocket real-time logging.

Provides a simple browser-based interface to trigger wordlist generation
and watch progress in real time.
"""

from __future__ import annotations

import json
import logging
from typing import Set

logger = logging.getLogger("pawpy.dashboard")

_connections: Set = set()


# Minimal HTML for the dashboard
_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pawpy Dashboard</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0d1117; color: #c9d1d9;
            display: flex; min-height: 100vh;
        }
        .sidebar {
            width: 280px; background: #161b22; padding: 20px;
            border-right: 1px solid #30363d;
        }
        .sidebar h1 { color: #58a6ff; font-size: 1.5rem; margin-bottom: 20px; }
        .sidebar label { display: block; color: #8b949e; margin: 12px 0 4px; font-size: 0.85rem; }
        .sidebar input[type="file"], .sidebar input[type="text"],
        .sidebar select { width: 100%; padding: 8px; background: #0d1117;
            border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; }
        .sidebar button { width: 100%; padding: 10px; margin-top: 16px;
            background: #238636; color: #fff; border: none; border-radius: 6px;
            cursor: pointer; font-size: 1rem; font-weight: bold; }
        .sidebar button:hover { background: #2ea043; }
        .sidebar .checkbox { display: flex; align-items: center; gap: 8px; margin: 6px 0; }
        .sidebar .checkbox input { width: auto; }
        .main { flex: 1; display: flex; flex-direction: column; }
        .header { padding: 16px 20px; background: #161b22;
            border-bottom: 1px solid #30363d; font-size: 1.1rem; }
        .log-area { flex: 1; padding: 16px; overflow-y: auto; font-family: 'Fira Code', monospace;
            font-size: 0.85rem; line-height: 1.6; }
        .log-line { padding: 2px 0; }
        .log-line.info { color: #58a6ff; }
        .log-line.success { color: #3fb950; }
        .log-line.warning { color: #d29922; }
        .log-line.error { color: #f85149; }
        .stats { padding: 12px 20px; background: #161b22;
            border-top: 1px solid #30363d; display: flex; gap: 24px; }
        .stat-item span.label { color: #8b949e; font-size: 0.8rem; }
        .stat-item span.value { color: #58a6ff; font-size: 1.2rem; font-weight: bold; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h1>Pawpy</h1>
        <label>Profile JSON</label>
        <input type="file" id="profileFile" accept=".json">
        <label>Output File</label>
        <input type="text" id="outputFile" placeholder="pawpy_wordlist.txt">
        <label>Mode</label>
        <select id="mode">
            <option value="normal">Normal</option>
            <option value="lite">Lite (fast)</option>
            <option value="extreme">Extreme (all mutations)</option>
        </select>
        <div class="checkbox"><input type="checkbox" id="markov"> <label for="markov" style="margin:0">Markov Blending</label></div>
        <div class="checkbox"><input type="checkbox" id="scoring"> <label for="scoring" style="margin:0">zxcvbn Scoring</label></div>
        <button onclick="startGeneration()">Generate Wordlist</button>
    </div>
    <div class="main">
        <div class="header">Generation Log</div>
        <div class="log-area" id="logArea"></div>
        <div class="stats">
            <div class="stat-item"><span class="label">Candidates</span><br><span class="value" id="statCandidates">0</span></div>
            <div class="stat-item"><span class="label">Output Size</span><br><span class="value" id="statSize">0 B</span></div>
            <div class="stat-item"><span class="label">Status</span><br><span class="value" id="statStatus">Idle</span></div>
        </div>
    </div>
    <script>
        const ws = new WebSocket(`ws://127.0.0.1:8080/ws`);
        ws.onmessage = (e) => {
            const msg = JSON.parse(e.data);
            const logArea = document.getElementById('logArea');
            const line = document.createElement('div');
            line.className = `log-line ${msg.level || 'info'}`;
            line.textContent = msg.text;
            logArea.appendChild(line);
            logArea.scrollTop = logArea.scrollHeight;
            if (msg.candidates) document.getElementById('statCandidates').textContent = Number(msg.candidates).toLocaleString();
            if (msg.size) document.getElementById('statSize').textContent = (msg.size / (1024*1024)).toFixed(2) + ' MB';
            if (msg.status) document.getElementById('statStatus').textContent = msg.status;
        };
        ws.onclose = () => { addLog('WebSocket disconnected', 'error'); };
        function addLog(text, level) {
            const logArea = document.getElementById('logArea');
            const line = document.createElement('div');
            line.className = `log-line ${level}`;
            line.textContent = text;
            logArea.appendChild(line);
        }
        async function startGeneration() {
            const fileInput = document.getElementById('profileFile');
            if (!fileInput.files.length) { addLog('Please select a profile JSON file.', 'warning'); return; }
            const formData = new FormData();
            formData.append('profile', fileInput.files[0]);
            formData.append('output', document.getElementById('outputFile').value || 'pawpy_wordlist.txt');
            const mode = document.getElementById('mode').value;
            formData.append('lite', mode === 'lite');
            formData.append('extreme', mode === 'extreme');
            formData.append('markov', document.getElementById('markov').checked);
            formData.append('min_strength', document.getElementById('scoring').checked ? '2' : '');
            addLog('Starting generation...', 'info');
            try {
                const resp = await fetch('http://127.0.0.1:8000/generate', {method: 'POST', body: formData});
                const data = await resp.json();
                if (data.download_url) {
                    addLog('Done! Download: ' + data.download_url, 'success');
                } else {
                    addLog('Error: ' + (data.message || 'Unknown'), 'error');
                }
            } catch (err) { addLog('Fetch error: ' + err.message, 'error'); }
        }
    </script>
</body>
</html>
"""


async def _websocket_handler(websocket):
    """Handle a single WebSocket connection for real-time logging."""
    _connections.add(websocket)
    try:
        async for message in websocket:
            pass  # Dashboard only receives; no client commands over WS
    finally:
        _connections.discard(websocket)


async def broadcast_log(text: str, level: str = "info", **extra):
    """Broadcast a log message to all connected WebSocket clients."""
    msg = json.dumps({"text": text, "level": level, **extra})
    for ws in list(_connections):
        try:
            await ws.send_text(msg)
        except Exception:
            _connections.discard(ws)


def run_dashboard(host: str = "127.0.0.1", port: int = 8080):
    """Launch the web dashboard with both HTTP and WebSocket support."""
    try:
        import uvicorn
        from fastapi import FastAPI, WebSocket
        from fastapi.responses import HTMLResponse
    except ImportError:
        raise ImportError(
            "FastAPI and uvicorn are required for dashboard mode. "
            "Install them with: pip install fastapi uvicorn websockets"
        )

    app = FastAPI(title="Pawpy Dashboard")

    @app.get("/", response_class=HTMLResponse)
    async def dashboard_page():
        return _DASHBOARD_HTML

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        _connections.add(websocket)

        try:
            while True:
                await websocket.receive_text()  # keep connection alive
        except Exception:
            _connections.discard(websocket)
        finally:
            _connections.discard(websocket)

    logger.info("Starting Pawpy Dashboard on http://%s:%d", host, port)
    uvicorn.run(app, host=host, port=port)
