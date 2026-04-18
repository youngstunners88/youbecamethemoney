"""Tiny backend that runs the Layer 3 cycle and streams output via SSE.

Also mounts the Ramsees gateway under /api/ramsees/* so the command center
serves both the dashboard and the agent front door from a single origin.
"""
import subprocess, sys, os, json, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, 'hermes'))
try:
    import ramsees_gateway  # noqa: E402
except Exception as _e:      # pragma: no cover
    ramsees_gateway = None
    print(f'⚠️  ramsees_gateway not loaded: {_e}')

clients = []
clients_lock = threading.Lock()

def broadcast(data: str):
    dead = []
    with clients_lock:
        for wfile in clients:
            try:
                msg = f"data: {json.dumps({'line': data})}\n\n"
                wfile.write(msg.encode())
                wfile.flush()
            except:
                dead.append(wfile)
        for d in dead:
            clients.remove(d)

def _delegate_to_ramsees(req):
    """Hand this request to the Ramsees gateway handler in-process."""
    if ramsees_gateway is None:
        req.send_response(503)
        req.send_header('Content-Type', 'application/json')
        req.end_headers()
        req.wfile.write(b'{"error":"ramsees gateway not loaded"}')
        return
    rg = ramsees_gateway
    method = req.command.upper()
    path = urlparse(req.path).path
    body = rg._read_json(req) if method == 'POST' else {}
    if method == 'OPTIONS':
        return rg._send_json(req, 204, {})
    if method == 'GET' and path == '/api/ramsees/health':
        # Rebuild the gateway's health payload here so we don't need a GET handler call.
        from datetime import datetime, timezone
        return rg._send_json(req, 200, {
            'service': 'ramsees-gateway',
            'location': 'command-center',
            'upstream': rg.HERMES_UPSTREAM,
            'model': rg.HERMES_MODEL,
            'hermes_source': 'github.com/NousResearch/hermes-agent',
            'turns_in_memory': len(rg._history),
            'ts': datetime.now(timezone.utc).isoformat(),
        })
    if method == 'GET' and path == '/api/ramsees/history':
        from dataclasses import asdict
        return rg._send_json(req, 200, {'turns': [asdict(t) for t in rg._history[-50:]]})
    # POST handlers
    handler = rg.RamseesHandler
    if method == 'POST' and path == '/api/ramsees/chat':
        return handler._handle_chat(req, body)
    if method == 'POST' and path == '/api/ramsees/retell':
        return handler._handle_retell(req, body)
    if method == 'POST' and path == '/api/ramsees/embark':
        return handler._handle_embark(req, body)
    rg._send_json(req, 404, {'error': 'unknown endpoint'})


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_): pass   # silence default logs

    def do_GET(self):
        path = urlparse(self.path).path

        if path.startswith('/api/ramsees/'):
            return _delegate_to_ramsees(self)

        if path == '/api/run':
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            with clients_lock:
                clients.append(self.wfile)
            # run in background thread
            t = threading.Thread(target=self._run_cycle, daemon=True)
            t.start()
            t.join()
            return

        if path in ('/', '/demo-interface.html'):
            path = '/demo-interface.html'
        
        full = os.path.join(ROOT, path.lstrip('/'))
        if os.path.exists(full) and os.path.isfile(full):
            ext = full.rsplit('.', 1)[-1]
            ct = {'html':'text/html','js':'application/javascript','css':'text/css',
                  'json':'application/json'}.get(ext, 'text/plain')
            self.send_response(200)
            self.send_header('Content-Type', ct)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            with open(full, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        if path.startswith('/api/ramsees/'):
            return _delegate_to_ramsees(self)
        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self):
        path = urlparse(self.path).path
        if path.startswith('/api/ramsees/'):
            return _delegate_to_ramsees(self)
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def _run_cycle(self):
        try:
            proc = subprocess.Popen(
                [sys.executable, os.path.join(ROOT, 'optimization/layer3/run.py')],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, cwd=ROOT
            )
            for line in proc.stdout:
                broadcast(line.rstrip())
            proc.wait()
            broadcast('__DONE__')
        except Exception as e:
            broadcast(f'ERROR: {e}')
            broadcast('__DONE__')

if __name__ == '__main__':
    port = 8080
    print(f'\n✅  Demo server running on http://localhost:{port}')
    print(f'   Open: http://localhost:{port}/demo-interface.html\n')
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()
