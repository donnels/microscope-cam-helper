#!/usr/bin/env python3
"""
Pimoroni Unicorn HAT LED Status Display
4 rows x 8 columns for microscope camera status

Row 0 (bottom): System Status - Green when operational
Row 1: Streaming Status - Red when actively streaming
Row 2-3: Flash bright white on image capture
"""
import os
import time
import threading
import sys

try:
    import unicornhat as uh
    UNICORN_AVAILABLE = True
except ImportError:
    UNICORN_AVAILABLE = False
    print("WARNING: unicornhat library not available, LED features disabled")


class LEDStatus:
    """Control Pimoroni Unicorn HAT for status display"""
    
    def __init__(self, enabled=True):
        self.enabled = enabled and UNICORN_AVAILABLE
        self.flash_thread = None
        self.streaming = False
        self.system_ok = False
        
        if self.enabled:
            try:
                uh.set_layout(uh.PHAT)
                uh.rotation(0)
                uh.brightness(0.5)
                print("Unicorn HAT initialized successfully")
            except Exception as e:
                print(f"ERROR: Failed to initialize Unicorn HAT: {e}")
                self.enabled = False
        else:
            print("LED status display disabled")
    
    def set_row(self, row, r, g, b):
        """Set entire row to specified color"""
        if not self.enabled:
            return
        try:
            for col in range(8):
                uh.set_pixel(col, row, r, g, b)
            uh.show()
        except Exception as e:
            print(f"ERROR setting row {row}: {e}")
    
    def clear_row(self, row):
        """Clear entire row (set to black)"""
        self.set_row(row, 0, 0, 0)
    
    def clear_all(self):
        """Clear entire display"""
        if not self.enabled:
            return
        try:
            uh.clear()
            uh.show()
        except Exception as e:
            print(f"ERROR clearing display: {e}")
    
    def update_system_status(self, camera_ok=False):
        """Update row 0 (bottom) with system status - green when operational"""
        if not self.enabled:
            return
        
        self.system_ok = camera_ok
        
        try:
            if camera_ok:
                self.set_row(0, 0, 255, 0)  # Green
            else:
                self.clear_row(0)
        except Exception as e:
            print(f"ERROR updating system status: {e}")
    
    def set_streaming(self, active=True):
        """Update row 1 with streaming status - red when active"""
        if not self.enabled:
            return
        
        self.streaming = active
        
        try:
            if active:
                self.set_row(1, 255, 0, 0)  # Red
            else:
                self.clear_row(1)
        except Exception as e:
            print(f"ERROR updating streaming status: {e}")
    
    def flash_capture(self, duration=0.5):
        """Flash rows 2-3 bright white when image captured (non-blocking)"""
        if not self.enabled:
            return
        
        def _flash():
            try:
                self.set_row(2, 255, 255, 255)
                self.set_row(3, 255, 255, 255)
                time.sleep(duration)
                self.clear_row(2)
                self.clear_row(3)
            except Exception as e:
                print(f"ERROR during flash: {e}")
        
        if self.flash_thread is None or not self.flash_thread.is_alive():
            self.flash_thread = threading.Thread(target=_flash, daemon=True)
            self.flash_thread.start()
    
    def cleanup(self):
        """Clean up and turn off all LEDs"""
        if self.enabled:
            try:
                self.clear_all()
                print("LED display cleaned up")
            except Exception as e:
                print(f"ERROR during cleanup: {e}")


def run_tests():
    """Standalone test mode"""
    print("Testing Unicorn HAT LED Status Display")
    leds = LEDStatus(enabled=True)
    
    if not leds.enabled:
        print("ERROR: LEDs not available")
        return 1
    
    try:
        print("Row 0 (bottom): Red")
        leds.set_row(0, 255, 0, 0)
        time.sleep(2)
        
        print("Row 1: Green")
        leds.set_row(1, 0, 255, 0)
        time.sleep(2)
        
        print("Row 2: Blue")
        leds.set_row(2, 0, 0, 255)
        time.sleep(2)
        
        print("Row 3 (top): Yellow")
        leds.set_row(3, 255, 255, 0)
        time.sleep(2)
        
        print("All rows: White")
        for row in range(4):
            leds.set_row(row, 255, 255, 255)
        time.sleep(2)
        
        print("\nTesting system status (green)")
        leds.clear_all()
        leds.update_system_status(camera_ok=True)
        time.sleep(2)
        
        print("Testing streaming status (red)")
        leds.set_streaming(True)
        time.sleep(2)
        
        print("Testing capture flash (white)")
        leds.flash_capture()
        time.sleep(1)
        leds.flash_capture()
        time.sleep(2)
        
        print("Stopping stream")
        leds.set_streaming(False)
        time.sleep(1)
        
        print("Cleanup")
        leds.cleanup()
        print("Test complete")
        return 0
        
    except Exception as e:
        print(f"ERROR during test: {e}")
        leds.cleanup()
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
