#!/usr/bin/env python3
"""
Web Server - Flask HTTP interface for CSI camera
Serves camera stream and gallery
"""
from flask import Flask, Response, render_template_string, jsonify, request, send_from_directory
from functools import wraps
from pathlib import Path
import time
import zipfile
import io
import os
import secrets
import threading
import multiprocessing
from werkzeug.serving import run_simple

from camera_service import get_camera_service

app = Flask(__name__)

# Authentication credentials from environment
USERNAME = os.getenv('WEB_USERNAME', 'admin')
if 'WEB_PASSWORD' in os.environ:
    PASSWORD = os.environ['WEB_PASSWORD']
else:
    PASSWORD = secrets.token_urlsafe(16)
    print(f"WARNING: No WEB_PASSWORD set. Generated random password: {PASSWORD}")

def check_auth(username, password):
    """Check if username/password is valid"""
    return username == USERNAME and password == PASSWORD

def authenticate():
    """Send 401 response for authentication required"""
    return Response(
        'Authentication required',
        401,
        {'WWW-Authenticate': 'Basic realm="CSI Camera"'}
    )

def requires_auth(f):
    """Decorator for routes requiring authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/health')
def health():
    """Health check endpoint - no auth required"""
    return jsonify({
        'status': 'ok',
        'service': 'csi-camera',
        'timestamp': time.time()
    })

@app.route('/')
@requires_auth
def index():
    """Main page with stream and controls"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>CSI Camera</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            img { max-width: 100%; height: auto; border: 1px solid #ccc; }
            button { margin: 5px; padding: 10px; }
        </style>
    </head>
    <body>
        <h1>CSI Camera Stream</h1>
        <img src="/stream" alt="CSI Camera Stream">
        <br>
        <button onclick="capture()">Capture Image</button>
        <button onclick="location.href='/gallery'">View Gallery</button>
        <div id="status"></div>
        
        <script>
            function capture() {
                fetch('/capture', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('status').innerText = 
                            data.success ? 'Captured: ' + data.filename : 'Capture failed';
                    });
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/stream')
@requires_auth
def stream():
    """MJPEG stream endpoint"""
    camera = get_camera_service()
    if not camera.start():
        return Response('Camera failed to start', 500)
    
    def generate():
        try:
            yield from camera.generate_stream()
        finally:
            camera.stop()
    
    return Response(
        generate(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/capture', methods=['POST'])
@requires_auth
def capture():
    """Capture still image"""
    camera = get_camera_service()
    filepath = camera.capture_image()
    
    if filepath and filepath.exists():
        return jsonify({
            'success': True,
            'filename': filepath.name,
            'path': str(filepath)
        })
    else:
        return jsonify({'success': False}), 500

@app.route('/gallery')
@requires_auth
def gallery():
    """Image gallery"""
    capture_dir = Path('/app/captures')
    images = []
    
    if capture_dir.exists():
        for img in sorted(capture_dir.glob('*.jpg'), reverse=True):
            images.append({
                'filename': img.name,
                'url': f'/captures/{img.name}',
                'size': img.stat().st_size,
                'mtime': time.ctime(img.stat().st_mtime)
            })
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>CSI Camera Gallery</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .image { margin: 10px; display: inline-block; }
            img { max-width: 200px; height: auto; border: 1px solid #ccc; }
            .info { font-size: 12px; color: #666; }
        </style>
    </head>
    <body>
        <h1>CSI Camera Gallery</h1>
        <a href="/">Back to Stream</a>
        <div>
            {% for img in images %}
            <div class="image">
                <a href="{{ img.url }}" target="_blank">
                    <img src="{{ img.url }}" alt="{{ img.filename }}">
                </a>
                <div class="info">
                    {{ img.filename }}<br>
                    {{ img.mtime }}<br>
                    {{ "%.1f"|format(img.size / 1024) }} KB
                </div>
            </div>
            {% endfor %}
        </div>
    </body>
    </html>
    '''
    return render_template_string(html, images=images)

@app.route('/captures/<filename>')
@requires_auth
def serve_capture(filename):
    """Serve captured images"""
    return send_from_directory('/app/captures', filename)

def run_http():
    """Run HTTP server"""
    run_simple('0.0.0.0', 8081, app, threaded=True)

def run_https():
    """Run HTTPS server"""
    ssl_context = ('/app/certs/cert.pem', '/app/certs/key.pem')
    run_simple('0.0.0.0', 8444, app, threaded=True, ssl_context=ssl_context)

if __name__ == '__main__':
    # Start both HTTP and HTTPS servers
    http_process = multiprocessing.Process(target=run_http)
    https_process = multiprocessing.Process(target=run_https)
    
    http_process.start()
    https_process.start()
    
    http_process.join()
    https_process.join()