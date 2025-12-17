#!/usr/bin/env python3
"""
CSI Camera Service - RPi CSI camera with libcamera
Streams MJPEG via libcamera-vid subprocess
"""
import subprocess
import os
import time
from pathlib import Path
from datetime import datetime

class CSICameraService:
    """Manages CSI camera via libcamera-vid subprocess"""
    
    def __init__(self, width=640, height=480, fps=30):
        self.width = width
        self.height = height
        self.fps = fps
        self.process = None
        self.capture_dir = Path('/app/captures')
        self.capture_dir.mkdir(exist_ok=True)
    
    def start(self):
        """Start rpicam-vid subprocess"""
        try:
            cmd = [
                'rpicam-vid',
                '--timeout', '0',
                '--width', str(self.width),
                '--height', str(self.height),
                '--framerate', str(self.fps),
                '--codec', 'mjpeg',
                '--output', '-',
                '--nopreview'
            ]
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Give it a moment to start
            time.sleep(1)
            
            # Check if process is still running
            if self.process.poll() is not None:
                stderr = self.process.stderr.read().decode()
                raise RuntimeError(f"rpicam-vid failed: {stderr}")
            
            print(f"CSI camera started: {self.width}x{self.height}@{self.fps}fps")
            return True
            
        except Exception as e:
            print(f"CSI camera error: {e}")
            return False
    
    def generate_stream(self):
        """Generate MJPEG stream from subprocess"""
        if not self.process:
            return
        
        try:
            while True:
                chunk = self.process.stdout.read(4096)
                if not chunk:
                    break
                yield chunk
        except Exception as e:
            print(f"Stream error: {e}")
    
    def capture_image(self):
        """Capture still image"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'csi_capture_{timestamp}.jpg'
        filepath = self.capture_dir / filename
        
        try:
            subprocess.run([
                'rpicam-still',
                '-o', str(filepath),
                '--width', '1920',
                '--height', '1080',
                '--timeout', '1000'
            ], check=True)
            
            return filepath
        except subprocess.CalledProcessError as e:
            print(f"Capture error: {e}")
            return None
    
    def stop(self):
        """Stop camera subprocess"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

def get_camera_service():
    """Factory function for camera service"""
    return CSICameraService()