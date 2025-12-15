#!/usr/bin/env python3
"""
Standalone LED HAT test
Tests Unicorn HAT display
"""
import time
import sys

try:
    import unicornhat as hat
    hat.set_layout(hat.PHAT)  # 4x8 Unicorn pHAT
    hat.rotation(0)
    hat.brightness(0.5)
    print("Unicorn HAT initialized")
except ImportError:
    print("ERROR: unicornhat library not found")
    print("Install: pip install unicornhat")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Cannot initialize HAT: {e}")
    sys.exit(1)

def clear():
    """Turn off all LEDs"""
    for x in range(8):
        for y in range(4):
            hat.set_pixel(x, y, 0, 0, 0)
    hat.show()

def test_pattern():
    """Show test pattern"""
    print("Test 1: Red row")
    clear()
    for x in range(8):
        hat.set_pixel(x, 0, 255, 0, 0)
    hat.show()
    time.sleep(2)
    
    print("Test 2: Green row")
    clear()
    for x in range(8):
        hat.set_pixel(x, 1, 0, 255, 0)
    hat.show()
    time.sleep(2)
    
    print("Test 3: Blue row")
    clear()
    for x in range(8):
        hat.set_pixel(x, 2, 0, 0, 255)
    hat.show()
    time.sleep(2)
    
    print("Test 4: White row")
    clear()
    for x in range(8):
        hat.set_pixel(x, 3, 255, 255, 255)
    hat.show()
    time.sleep(2)
    
    print("Test 5: All white")
    for x in range(8):
        for y in range(4):
            hat.set_pixel(x, y, 255, 255, 255)
    hat.show()
    time.sleep(2)
    
    print("Test 6: Clear")
    clear()

def main():
    """Run tests"""
    print("Starting Unicorn HAT test")
    print("Press Ctrl+C to exit")
    
    try:
        test_pattern()
        print("Test complete - LEDs should be off")
    except KeyboardInterrupt:
        print("\nStopping...")
        clear()
    except Exception as e:
        print(f"ERROR: {e}")
        clear()
        sys.exit(1)

if __name__ == '__main__':
    main()
