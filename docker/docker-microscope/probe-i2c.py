#!/usr/bin/env python3
"""Quick I2C device probe"""
import sys

try:
    import smbus2
except ImportError:
    print("ERROR: Install smbus2")
    sys.exit(1)

addr = 0x62
bus = smbus2.SMBus(1)

print(f"Probing 0x{addr:02x}...")

# Try different register reads
registers = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x08, 0x0A, 0x0C, 0x0E]

for reg in registers:
    try:
        # Byte read
        val = bus.read_byte_data(addr, reg)
        print(f"  Reg 0x{reg:02x}: 0x{val:02x} ({val})")
    except Exception as e:
        print(f"  Reg 0x{reg:02x}: ERROR - {e}")

bus.close()
print("Done")
