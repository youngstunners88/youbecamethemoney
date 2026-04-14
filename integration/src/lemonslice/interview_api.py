"""
Lemonslice Interview API
Receives interview submissions from the portal and runs interview_analyzer.
"""
import sys, os, json, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

from optimization.skills.interview_analyzer import analyze_interview
from optimization.skills.hall_of_fame_curator import curate_profile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InterviewHandler(BaseHTTPRequestHandler):
    def log_message(self, *_): pass

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        # Serve the portal
        if path in ('/', '/portal', '/portal.html'):
            portal_path = os.path.join(os.path.dirname(__file__), 'portal.html')
            with open(portal_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self._cors()
            self.end_headers()
            self.wfile.write(content)
        elif path == '/api/interview/status':
            self._json({'status': 'ready', 'version': '1.0.0'})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)

        try:
            data = json.loads(body)
        except Exception:
            self._json({'error': 'invalid JSON'}, 400)
            return

        if path == '/api/interview/submit':
            self._handle_submit(data)
        elif path == '/api/interview/curate':
            self._handle_curate(data)
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_submit(self, data: dict):
        """Run interview_analyzer on submission."""
        result = analyze_interview(
            interview_id=data.get('interview_id', ''),
            video_url=data.get('video_url', ''),
            transcript=data.get('transcript', ''),
            lead_id=data.get('lead_id', ''),
            current_warmth=float(data.get('current_warmth', 50.0))
        )
        logger.info(f"Interview analyzed: warmth {result['warmth_score_before']} → {result['warmth_score_after']}")
        self._json(result)

    def _handle_curate(self, data: dict):
        """Create Hall of Fame profile from closed case."""
        result = curate_profile(
            lead_id=data.get('lead_id', ''),
            case_outcome=data.get('case_outcome', 'won'),
            interview_id=data.get('interview_id', ''),
            transcript=data.get('transcript', ''),
            case_value=int(data.get('case_value', 0)),
            service_type=data.get('service_type', ''),
            jurisdiction=data.get('jurisdiction', ''),
            auto_publish=data.get('auto_publish', True)
        )
        self._json(result)

    def _json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')


if __name__ == '__main__':
    port = int(os.getenv('INTERVIEW_PORT', 8090))
    print(f'\n✅  Lemonslice Interview API running on http://localhost:{port}')
    print(f'   Portal: http://localhost:{port}/portal\n')
    HTTPServer(('0.0.0.0', port), InterviewHandler).serve_forever()
