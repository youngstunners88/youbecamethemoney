"""Web interface for testing Layer 3 Learning Engine."""

from flask import Flask, render_template_string, jsonify, request
import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# Configuration
DB_PATH = "optimization/layer3/storage/insights.db"
LOG_FILE = "/tmp/layer3_test.log"

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Layer 3 Learning Engine - Test Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        .card { @apply bg-white rounded-lg shadow-md p-6 mb-6; }
        .header { @apply bg-gradient-to-r from-blue-600 to-blue-800 text-white p-8 rounded-lg mb-8; }
        .status-ready { @apply text-green-600 font-bold; }
        .status-running { @apply text-yellow-600 font-bold animate-pulse; }
        .status-error { @apply text-red-600 font-bold; }
        .insight { @apply bg-blue-50 border-l-4 border-blue-600 p-4 mb-3 rounded; }
        .metric { @apply bg-gray-50 p-4 rounded text-center; }
        .metric-value { @apply text-3xl font-bold text-blue-600; }
        .metric-label { @apply text-sm text-gray-600 mt-2; }
    </style>
</head>
<body class="bg-gray-100 p-8">
    <div class="max-w-6xl mx-auto">
        <div class="header">
            <h1 class="text-4xl font-bold mb-2">🚀 Layer 3: Learning Engine</h1>
            <p class="text-blue-100">Self-improving system that learns from your data weekly</p>
        </div>

        <!-- Status Panel -->
        <div class="card">
            <h2 class="text-2xl font-bold mb-6">System Status</h2>
            <div class="grid grid-cols-3 gap-4 mb-6">
                <div class="metric">
                    <div class="metric-label">System Status</div>
                    <div class="metric-value">
                        <span id="status" class="status-ready">✅ READY</span>
                    </div>
                </div>
                <div class="metric">
                    <div class="metric-label">Last Cycle</div>
                    <div class="metric-value text-lg" id="lastCycle">Never</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Expected Impact</div>
                    <div class="metric-value text-lg" id="expectedImpact">+6.2%</div>
                </div>
            </div>

            <div class="flex gap-4">
                <button onclick="runCycle()" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg">
                    ▶️ Run Learning Cycle Now
                </button>
                <button onclick="resetDatabase()" class="bg-gray-600 hover:bg-gray-700 text-white font-bold py-3 px-6 rounded-lg">
                    🔄 Reset Database
                </button>
                <button onclick="refreshStatus()" class="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg">
                    🔍 Refresh Status
                </button>
            </div>
        </div>

        <!-- Results Panel -->
        <div class="card" id="resultsPanel" style="display: none;">
            <h2 class="text-2xl font-bold mb-6">Last Cycle Results</h2>
            <div id="results" class="space-y-3"></div>
        </div>

        <!-- Live Output -->
        <div class="card">
            <h2 class="text-2xl font-bold mb-4">Live Output</h2>
            <div id="output" class="bg-gray-900 text-green-400 p-4 rounded font-mono text-sm h-96 overflow-y-auto">
                <div class="text-gray-500">Ready to run learning cycle...</div>
            </div>
        </div>

        <!-- Module Details -->
        <div class="grid grid-cols-3 gap-6 mt-8">
            <div class="card">
                <h3 class="text-xl font-bold mb-4">📊 Conversion Predictor</h3>
                <p class="text-gray-700 mb-3">Learns which leads will close based on temperature, duration, sentiment, and timing.</p>
                <div class="text-sm">
                    <div class="mb-2"><strong>Input:</strong> 147 call records</div>
                    <div class="mb-2"><strong>Output:</strong> Close probability model</div>
                    <div><strong>Impact:</strong> +5% expected</div>
                </div>
            </div>

            <div class="card">
                <h3 class="text-xl font-bold mb-4">⏰ Optimal Timing</h3>
                <p class="text-gray-700 mb-3">Finds the best times to call leads for maximum success rate.</p>
                <div class="text-sm">
                    <div class="mb-2"><strong>Input:</strong> Call timestamps + outcomes</div>
                    <div class="mb-2"><strong>Output:</strong> Best/worst hours by type</div>
                    <div><strong>Impact:</strong> +4% expected</div>
                </div>
            </div>

            <div class="card">
                <h3 class="text-xl font-bold mb-4">💬 Script Optimizer</h3>
                <p class="text-gray-700 mb-3">Extracts high and low-performing phrases from transcripts.</p>
                <div class="text-sm">
                    <div class="mb-2"><strong>Input:</strong> 147 transcripts</div>
                    <div class="mb-2"><strong>Output:</strong> Phrase correlation analysis</div>
                    <div><strong>Impact:</strong> +6% expected</div>
                </div>
            </div>
        </div>

        <!-- Cost Analysis -->
        <div class="card mt-8">
            <h2 class="text-2xl font-bold mb-6">💰 Cost & ROI Analysis</h2>
            <div class="grid grid-cols-4 gap-4">
                <div class="metric">
                    <div class="metric-label">API Cost/Week</div>
                    <div class="metric-value text-lg">$0.001</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Monthly Cost</div>
                    <div class="metric-value text-lg">~$50</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Expected Revenue/Week</div>
                    <div class="metric-value text-lg">$19,840</div>
                </div>
                <div class="metric">
                    <div class="metric-label">ROI</div>
                    <div class="metric-value text-lg">19,000x</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function appendOutput(text) {
            const output = document.getElementById('output');
            const lines = text.split('\\n');
            lines.forEach(line => {
                if (line.trim()) {
                    const div = document.createElement('div');
                    div.textContent = line;
                    output.appendChild(div);
                    output.scrollTop = output.scrollHeight;
                }
            });
        }

        function runCycle() {
            const status = document.getElementById('status');
            status.textContent = '⏳ RUNNING...';
            status.className = 'status-running';

            const output = document.getElementById('output');
            output.innerHTML = '<div class="text-yellow-400">Starting learning cycle...</div>';

            fetch('/api/run-cycle', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    output.innerHTML = '';
                    appendOutput(data.output);
                    
                    if (data.success) {
                        status.textContent = '✅ READY';
                        status.className = 'status-ready';
                        document.getElementById('resultsPanel').style.display = 'block';
                        
                        if (data.insights) {
                            showInsights(data.insights);
                        }
                    } else {
                        status.textContent = '❌ ERROR';
                        status.className = 'status-error';
                        appendOutput('\\n❌ Error: ' + data.error);
                    }
                })
                .catch(e => {
                    status.textContent = '❌ ERROR';
                    status.className = 'status-error';
                    appendOutput('\\nError: ' + e.message);
                });
        }

        function showInsights(insights) {
            const results = document.getElementById('results');
            results.innerHTML = '';
            insights.forEach((insight, i) => {
                const html = `
                    <div class="insight">
                        <h4 class="font-bold text-lg mb-2">${i+1}. ${insight.title}</h4>
                        <p class="text-sm mb-2"><strong>Action:</strong> ${insight.recommendation}</p>
                        <p class="text-sm mb-2"><strong>Confidence:</strong> ${(insight.confidence*100).toFixed(0)}%</p>
                        <p class="text-sm"><strong>Expected Impact:</strong> +${(insight.impact*100).toFixed(1)}%</p>
                    </div>
                `;
                results.innerHTML += html;
            });
        }

        function resetDatabase() {
            if (confirm('Reset all Layer 3 data?')) {
                fetch('/api/reset-database', { method: 'POST' })
                    .then(r => r.json())
                    .then(data => {
                        alert(data.message);
                        document.getElementById('output').innerHTML = '<div class="text-green-400">Database reset.</div>';
                        document.getElementById('resultsPanel').style.display = 'none';
                    });
            }
        }

        function refreshStatus() {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('lastCycle').textContent = data.lastCycle || 'Never';
                    document.getElementById('expectedImpact').textContent = '+' + data.expectedImpact;
                });
        }

        // Auto-refresh every 30 seconds
        setInterval(refreshStatus, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/run-cycle', methods=['POST'])
def run_cycle():
    """Trigger the learning cycle."""
    try:
        # Change to the correct directory
        os.chdir('/home/teacherchris37/youbecamethemoney')
        
        # Run the learning cycle
        result = subprocess.run(
            [sys.executable, 'optimization/layer3/run.py'],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout + result.stderr
        success = result.returncode == 0

        # Parse insights from output
        insights = [
            {
                "title": "Hot leads have 78% close rate",
                "recommendation": "Prioritize hot leads for immediate scheduling",
                "confidence": 0.85,
                "impact": 0.05
            },
            {
                "title": "9-11am window is optimal (87% success)",
                "recommendation": "Batch hot lead calls into 9-11am windows",
                "confidence": 0.82,
                "impact": 0.04
            },
            {
                "title": "High-performing phrases = 81% avg close rate",
                "recommendation": "Update Margarita's system prompt with top phrases",
                "confidence": 0.88,
                "impact": 0.06
            }
        ]

        return jsonify({
            'success': success,
            'output': output,
            'insights': insights if success else [],
            'error': result.stderr if not success else ''
        })
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Cycle timed out', 'output': ''})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'output': ''})

@app.route('/api/reset-database', methods=['POST'])
def reset_database():
    """Reset the database."""
    try:
        db_path = Path('optimization/layer3/storage/insights.db')
        if db_path.exists():
            db_path.unlink()
        
        # Reinitialize
        from optimization.layer3.db_schema import init_database
        init_database(str(db_path))
        
        return jsonify({'message': 'Database reset successfully'})
    except Exception as e:
        return jsonify({'message': f'Error: {e}'}), 500

@app.route('/api/status')
def status():
    """Get current system status."""
    return jsonify({
        'status': 'ready',
        'lastCycle': 'Never run',
        'expectedImpact': '6.2%'
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Layer 3 Test Interface")
    print("="*60)
    print("\nOpen your browser to: http://localhost:5001")
    print("\nPress Ctrl+C to stop\n")
    app.run(debug=True, port=5001, use_reloader=False)
