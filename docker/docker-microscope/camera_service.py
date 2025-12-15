#!/usr/bin/env python3
"""
Camera Service - Single camera instance with MJPEG streaming
Clean. Simple. Works.
"""
import cv2
import os
import time
from pathlib import Path
from datetime import datetime

class CameraService:
    """Manages single camera for streaming and capture"""
    
    def __init__(self, device='/dev/video0', width=1280, height=720):
        self.device = device
        self.width = width
        self.height = height
        self.camera = None
        self.capture_dir = Path('/app/captures')
        self.capture_dir.mkdir(exist_ok=True)
    
    def start(self):
        """Initialize camera"""
        try:
            self.camera = cv2.VideoCapture(self.device, cv2.CAP_V4L2)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            
            if not self.camera.isOpened():
                raise RuntimeError(f"Cannot open {self.device}")
            
            # Warmup - discard first few frames
            print(f"Camera opened: {self.device}, warming up...")
            for i in range(3):
                self.camera.read()
                time.sleep(0.05)
            
            # Test actual read
            success, frame = self.camera.read()
            if not success or frame is None:
                raise RuntimeError(f"Camera opened but cannot read frames from {self.device}")
            
            print(f"Camera ready: {self.device} ({frame.shape})")
            return True
            
        except Exception as e:
            print(f"Camera error: {e}")
            return False
    
    def read_frame(self):
        """Read single frame"""
        if not self.camera or not self.camera.isOpened():
            return None
        
        success, frame = self.camera.read()
        if not success:
            return None
        
        return frame
    
    def generate_stream(self):
        """Generate MJPEG stream"""
        if not self.camera or not self.camera.isOpened():
            return
        
        while True:
            frame = self.read_frame()
            if frame is None:
                break
            
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ret:
                continue
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    
    def capture_image(self):
        """Capture single image to disk"""
        frame = self.read_frame()
        if frame is None:
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'capture_{timestamp}.jpg'
        filepath = self.capture_dir / filename
        
        cv2.imwrite(str(filepath), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        return filepath
    
    def stop(self):
        """Release camera"""
        if self.camera:
            self.camera.release()
            self.camera = None

# Global camera service
_camera_service = None

def get_camera_service() -> CameraService:
    """Get global camera service"""
    global _camera_service
    if _camera_service is None:
        device = os.getenv('VIDEO_DEVICE', '/dev/video0')
        width = int(os.getenv('VIDEO_WIDTH', '1280'))
        height = int(os.getenv('VIDEO_HEIGHT', '720'))
        _camera_service = CameraService(device, width, height)
    return _camera_service
