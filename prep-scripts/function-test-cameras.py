#!/usr/bin/env python3
"""
Camera Capture Test
Tests various camera devices and captures sample frames

Usage:
  python3 test-camera.py                # Test all available cameras
  python3 test-camera.py /dev/video0    # Test specific device
  python3 test-camera.py --list         # List available devices
"""
import cv2
import sys
import os
import argparse

def list_devices():
    """List available video devices"""
    print("Available video devices:")
    for i in range(10):  # Check /dev/video0 through /dev/video9
        device = f"/dev/video{i}"
        if os.path.exists(device):
            try:
                cap = cv2.VideoCapture(device)
                if cap.isOpened():
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    print("8s")
                    cap.release()
                else:
                    print("8s")
            except Exception as e:
                print("8s")
        else:
            break

def test_camera(device, output_file=None):
    """Test a specific camera device"""
    if output_file is None:
        # Generate output filename based on device
        dev_name = device.replace('/dev/', '').replace('/', '-')
        output_file = f"test-{dev_name}.jpg"

    print(f"Testing camera: {device}")
    print(f"Output file: {output_file}")

    try:
        cap = cv2.VideoCapture(device)

        # Try different formats for different camera types
        if 'video0' in device:
            # CSI camera
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        else:
            # USB cameras
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y', 'U', 'Y', 'V'))

        if not cap.isOpened():
            print(f"ERROR: Cannot open {device}")
            return False

        # Get camera properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        print(f"Resolution: {width}x{height}")
        print(".1f")

        # Warmup - let camera stabilize
        print("Warming up camera...")
        for i in range(5):
            cap.read()

        # Capture frame
        print("Capturing frame...")
        ret, frame = cap.read()

        if ret:
            cv2.imwrite(output_file, frame)
            print(f"SUCCESS: Captured {output_file}")
            print(f"Frame size: {frame.shape}")
            cap.release()
            return True
        else:
            print("ERROR: Cannot read frame")
            cap.release()
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Test camera capture')
    parser.add_argument('device', nargs='?', help='Camera device to test (e.g., /dev/video0)')
    parser.add_argument('--list', action='store_true', help='List available devices')
    parser.add_argument('--output', help='Output filename for captured image')

    args = parser.parse_args()

    if args.list:
        list_devices()
        return

    if args.device:
        # Test specific device
        success = test_camera(args.device, args.output)
        sys.exit(0 if success else 1)
    else:
        # Test common devices
        devices_to_test = ['/dev/video0', '/dev/video1', '/dev/video2']
        success_count = 0

        print("Testing available camera devices...")
        print()

        for device in devices_to_test:
            if os.path.exists(device):
                if test_camera(device):
                    success_count += 1
                print()
            else:
                print(f"Device {device} not found, skipping")
                print()

        if success_count == 0:
            print("No cameras found or all tests failed")
            sys.exit(1)
        else:
            print(f"Successfully tested {success_count} camera(s)")

if __name__ == '__main__':
    main()
