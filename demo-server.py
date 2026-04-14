"""Tiny backend that runs the Layer 3 cycle and streams output via SSE."""
import subprocess, sys, os, json, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
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

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_): pass   # silence default logs

    def do_GET(self):
        path = urlparse(self.path).path

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

    def do_OPTIONS(self):
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
