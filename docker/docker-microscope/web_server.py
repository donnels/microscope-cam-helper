#!/usr/bin/env python3
"""
Web Server - Flask HTTP interface
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
        {'WWW-Authenticate': 'Basic realm="Microscope"'}
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

# HTML template with VSaGCR branding
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>VSaGCR Microscope</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: monospace;
            background: #000;
            color: #0f0;
            margin: 0;
            padding: 20px;
        }
        h1 {
            border-bottom: 2px solid #0f0;
            padding-bottom: 10px;
        }
        .video {
            max-width: 100%;
            border: 2px solid #0f0;
            margin: 20px 0;
        }
        button {
            background: #000;
            color: #0f0;
            border: 2px solid #0f0;
            padding: 10px 20px;
            font-family: monospace;
            font-size: 14px;
            cursor: pointer;
            margin: 5px;
        }
        button:hover {
            background: #0f0;
            color: #000;
        }
        .status {
            background: #111;
            padding: 15px;
            margin: 20px 0;
            border: 1px solid #0f0;
        }
        .captures {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
            margin: 20px 0;
        }
        .capture-item {
            position: relative;
            border: 1px solid #0f0;
            padding: 5px;
        }
        .capture-item.selected {
            border: 2px solid #0f0;
            background: #002200;
        }
        .capture-checkbox {
            position: absolute;
            top: 10px;
            left: 10px;
            width: 20px;
            height: 20px;
            cursor: pointer;
            z-index: 10;
        }
        .capture-thumb {
            width: 100%;
            border: 1px solid #0f0;
            cursor: pointer;
            display: block;
        }
        .batch-controls {
            margin: 10px 0;
            padding: 10px;
            background: #111;
            border: 1px solid #0f0;
        }
        .selection-info {
            display: inline-block;
            margin-right: 15px;
            color: #0f0;
        }
        .viewer-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.95);
            z-index: 1000;
        }
        .viewer-content {
            position: relative;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .viewer-image {
            max-width: 90%;
            max-height: 80vh;
            border: 2px solid #0f0;
        }
        .viewer-nav {
            margin-top: 20px;
        }
        .viewer-info {
            color: #0f0;
            margin-top: 10px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <h1>VSaGCR MICROSCOPE INTERFACE</h1>
    
    <div>
        <img src="/stream" class="video" alt="Camera Stream">
    </div>
    
    <div>
        <button onclick="capture()">CAPTURE IMAGE</button>
        <button onclick="refreshStatus()">REFRESH STATUS</button>
        <button onclick="location.reload()">RELOAD STREAM</button>
    </div>
    
    <div class="status" id="status">
        Loading status...
    </div>
    
    <h2>CAPTURES</h2>
    
    <div class="batch-controls">
        <span class="selection-info" id="selection-info">0 selected</span>
        <button onclick="selectAll()">SELECT ALL</button>
        <button onclick="deselectAll()">DESELECT ALL</button>
        <button onclick="downloadSelected()">DOWNLOAD SELECTED</button>
        <button onclick="deleteSelected()">DELETE SELECTED</button>
    </div>
    
    <div class="captures" id="captures">
        Loading captures...
    </div>
    
    <!-- Image Viewer Overlay -->
    <div class="viewer-overlay" id="viewer">
        <div class="viewer-content">
            <img id="viewer-image" class="viewer-image" src="" alt="Image">
            <div class="viewer-info" id="viewer-info"></div>
            <div class="viewer-nav">
                <button onclick="viewPrevious()">◀ PREVIOUS</button>
                <button onclick="closeViewer()">▲ BACK TO OVERVIEW</button>
                <button onclick="viewNext()">NEXT ▶</button>
            </div>
        </div>
    </div>
    
    <script>
        let allCaptures = [];
        let currentIndex = -1;
        let selectedCaptures = new Set();
        
        function capture() {
            fetch('/capture')
                .then(r => r.json())
                .then(d => {
                    alert('Captured: ' + d.filename);
                    loadCaptures();
                })
                .catch(e => alert('Capture failed: ' + e));
        }
        
        function refreshStatus() {
            fetch('/status')
                .then(r => r.json())
                .then(d => {
                    document.getElementById('status').innerHTML = 
                        '<strong>CAMERA:</strong> ' + (d.camera_ready ? 'OK' : 'ERROR');
                })
                .catch(e => console.error(e));
        }
        
        function loadCaptures() {
            fetch('/captures')
                .then(r => r.json())
                .then(d => {
                    allCaptures = d.captures;
                    const container = document.getElementById('captures');
                    container.innerHTML = '';
                    
                    if (d.captures.length === 0) {
                        container.innerHTML = 'No captures yet';
                        return;
                    }
                    
                    d.captures.forEach((c, idx) => {
                        const item = document.createElement('div');
                        item.className = 'capture-item';
                        item.id = 'item-' + idx;
                        if (selectedCaptures.has(c)) {
                            item.classList.add('selected');
                        }
                        
                        const checkbox = document.createElement('input');
                        checkbox.type = 'checkbox';
                        checkbox.className = 'capture-checkbox';
                        checkbox.checked = selectedCaptures.has(c);
                        checkbox.onchange = function() { toggleSelection(c, idx); };
                        
                        const img = document.createElement('img');
                        img.src = '/captures/' + c;
                        img.className = 'capture-thumb';
                        img.onclick = function() { openViewer(idx); };
                        
                        const label = document.createElement('small');
                        label.textContent = c;
                        
                        item.appendChild(checkbox);
                        item.appendChild(img);
                        item.appendChild(label);
                        container.appendChild(item);
                    });
                })
                .catch(e => console.error(e));
        }
        
        function toggleSelection(filename, idx) {
            if (selectedCaptures.has(filename)) {
                selectedCaptures.delete(filename);
                document.getElementById('item-' + idx).classList.remove('selected');
            } else {
                selectedCaptures.add(filename);
                document.getElementById('item-' + idx).classList.add('selected');
            }
            updateSelectionInfo();
        }
        
        function selectAll() {
            allCaptures.forEach(c => selectedCaptures.add(c));
            loadCaptures();
            updateSelectionInfo();
        }
        
        function deselectAll() {
            selectedCaptures.clear();
            loadCaptures();
            updateSelectionInfo();
        }
        
        function updateSelectionInfo() {
            document.getElementById('selection-info').textContent = selectedCaptures.size + ' selected';
        }
        
        function downloadSelected() {
            if (selectedCaptures.size === 0) {
                alert('No images selected');
                return;
            }
            
            if (selectedCaptures.size === 1) {
                // Single file download
                const filename = Array.from(selectedCaptures)[0];
                window.location.href = '/captures/' + filename;
            } else {
                // Batch download as zip
                const files = Array.from(selectedCaptures);
                fetch('/batch/download', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({files: files})
                })
                .then(r => r.blob())
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'captures_' + new Date().toISOString().slice(0,10) + '.zip';
                    a.click();
                    window.URL.revokeObjectURL(url);
                })
                .catch(e => alert('Download failed: ' + e));
            }
        }
        
        function deleteSelected() {
            if (selectedCaptures.size === 0) {
                alert('No images selected');
                return;
            }
            
            if (!confirm('Delete ' + selectedCaptures.size + ' image(s)?')) {
                return;
            }
            
            const files = Array.from(selectedCaptures);
            fetch('/batch/delete', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({files: files})
            })
            .then(r => r.json())
            .then(d => {
                alert('Deleted ' + d.deleted + ' image(s)');
                selectedCaptures.clear();
                loadCaptures();
            })
            .catch(e => alert('Delete failed: ' + e));
        }
        
        function openViewer(index) {
            currentIndex = index;
            updateViewer();
            document.getElementById('viewer').style.display = 'block';
        }
        
        function closeViewer() {
            document.getElementById('viewer').style.display = 'none';
        }
        
        function viewNext() {
            if (currentIndex < allCaptures.length - 1) {
                currentIndex++;
                updateViewer();
            }
        }
        
        function viewPrevious() {
            if (currentIndex > 0) {
                currentIndex--;
                updateViewer();
            }
        }
        
        function updateViewer() {
            const img = document.getElementById('viewer-image');
            const info = document.getElementById('viewer-info');
            img.src = '/captures/' + allCaptures[currentIndex];
            info.textContent = allCaptures[currentIndex] + ' (' + (currentIndex + 1) + ' / ' + allCaptures.length + ')';
        }
        
        // Keyboard navigation
        document.addEventListener('keydown', function(e) {
            if (document.getElementById('viewer').style.display === 'block') {
                if (e.key === 'ArrowLeft') viewPrevious();
                if (e.key === 'ArrowRight') viewNext();
                if (e.key === 'Escape') closeViewer();
            }
        });
        
        // Auto-refresh
        setInterval(refreshStatus, 5000);
        setInterval(loadCaptures, 10000);
        
        // Initial load
        refreshStatus();
        loadCaptures();
    </script>
</body>
</html>
'''

@app.route('/')
@requires_auth
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/stream')
@requires_auth
def stream():
    """MJPEG video stream"""
    camera = get_camera_service()
    return Response(
        camera.generate_stream(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/capture')
@requires_auth
def capture():
    """Capture single image"""
    camera = get_camera_service()
    filepath = camera.capture_image()
    
    if filepath:
        return jsonify({
            'status': 'ok',
            'filename': filepath.name,
            'path': str(filepath)
        })
    else:
        return jsonify({'status': 'error', 'message': 'Capture failed'}), 500

@app.route('/status')
@requires_auth
def status():
    """System status"""
    camera = get_camera_service()
    
    return jsonify({
        'camera_ready': camera.camera is not None and camera.camera.isOpened()
    })

@app.route('/health')
def health():
    """Health check endpoint (unauthenticated for monitoring)"""
    camera = get_camera_service()
    camera_ok = camera.camera is not None and camera.camera.isOpened()
    
    status_code = 200 if camera_ok else 503
    
    return jsonify({
        'status': 'healthy' if camera_ok else 'unhealthy',
        'camera': 'ok' if camera_ok else 'error'
    }), status_code

@app.route('/captures')
@requires_auth
def list_captures():
    """List captured images"""
    captures_dir = Path('/app/captures')
    captures = sorted([f.name for f in captures_dir.glob('*.jpg')], reverse=True)
    return jsonify({'captures': captures})

@app.route('/captures/<filename>')
@requires_auth
def get_capture(filename):
    """Serve captured image"""
    captures_dir = Path('/app/captures')
    filepath = captures_dir / filename
    
    # Prevent path traversal attacks
    try:
        filepath = filepath.resolve()
        if not filepath.is_relative_to(captures_dir.resolve()):
            return jsonify({'error': 'Invalid file path'}), 400
    except (ValueError, OSError):
        return jsonify({'error': 'Invalid file path'}), 400
    
    if not filepath.exists() or filepath.suffix != '.jpg':
        return jsonify({'error': 'File not found'}), 404
    
    return send_from_directory('/app/captures', filename)

@app.route('/batch/download', methods=['POST'])
@requires_auth
def batch_download():
    """Download multiple images as zip"""
    data = request.get_json()
    files = data.get('files', [])
    
    if not files:
        return jsonify({'error': 'No files specified'}), 400
    
    captures_dir = Path('/app/captures').resolve()
    
    # Create zip in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename in files:
            filepath = (captures_dir / filename).resolve()
            
            # Prevent path traversal attacks
            try:
                if not filepath.is_relative_to(captures_dir):
                    continue
            except (ValueError, OSError):
                continue
            
            if filepath.exists() and filepath.suffix == '.jpg':
                zip_file.write(filepath, filename)
    
    # Important: seek to beginning before sending
    zip_buffer.seek(0)
    
    # Return the BytesIO object directly
    return Response(
        zip_buffer.getvalue(),
        mimetype='application/zip',
        headers={'Content-Disposition': 'attachment; filename=captures.zip'}
    )

@app.route('/batch/delete', methods=['POST'])
@requires_auth
def batch_delete():
    """Delete multiple images"""
    data = request.get_json()
    files = data.get('files', [])
    
    if not files:
        return jsonify({'error': 'No files specified'}), 400
    
    captures_dir = Path('/app/captures').resolve()
    deleted = 0
    
    for filename in files:
        filepath = (captures_dir / filename).resolve()
        
        # Prevent path traversal attacks
        try:
            if not filepath.is_relative_to(captures_dir):
                print(f"Rejected path traversal attempt: {filename}")
                continue
        except (ValueError, OSError) as e:
            print(f"Invalid file path {filename}: {e}")
            continue
        
        if filepath.exists() and filepath.suffix == '.jpg':
            try:
                os.remove(filepath)
                deleted += 1
            except Exception as e:
                print(f"Error deleting {filename}: {e}")
    
    return jsonify({'deleted': deleted, 'requested': len(files)})

def main():
    """Start camera service and web server"""
    print("Starting VSaGCR Microscope System")
    print(f"Authentication: username={USERNAME}")
    
    # Start camera
    camera = get_camera_service()
    camera.start()
    
    # Give camera time to initialize
    time.sleep(1)
    
    # Get configuration from environment
    use_ssl = os.getenv('ENABLE_HTTPS', 'true').lower() == 'true'
    
    def run_http():
        print("Starting HTTP web server on port 8080")
        run_simple('0.0.0.0', 8080, app, threaded=True)
    
    def run_https():
        cert_file = '/app/certs/cert.pem'
        key_file = '/app/certs/key.pem'
        if os.path.exists(cert_file) and os.path.exists(key_file):
            print("Starting HTTPS web server on port 8443")
            run_simple('0.0.0.0', 8443, app, threaded=True, ssl_context=(cert_file, key_file))
        else:
            print("WARNING: SSL certificates not found, HTTPS not available")
    
    # Start HTTP server on 8080
    http_process = multiprocessing.Process(target=run_http)
    http_process.start()
    
    # Start HTTPS server on 8443 if enabled
    if use_ssl:
        https_process = multiprocessing.Process(target=run_https)
        https_process.start()
    
    # Keep main process alive
    http_process.join()

if __name__ == '__main__':
    main()
