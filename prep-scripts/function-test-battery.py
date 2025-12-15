#!/usr/bin/env python3
"""
Comprehensive UPS-Lite v1.3 Battery Monitor Test
CW2015 fuel gauge at I2C address 0x62

Combines:
- I2C device detection and register dumping
- Voltage and capacity reading
- Continuous monitoring
- Full status reporting
"""
import struct
import sys
import time

try:
    import smbus
    SMBUS_AVAILABLE = True
except ImportError:
    try:
        import smbus2 as smbus
        SMBUS_AVAILABLE = True
    except ImportError:
        SMBUS_AVAILABLE = False
        print("ERROR: smbus/smbus2 not available")
        sys.exit(1)

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

# CW2015 fuel gauge constants
CW2015_ADDRESS = 0x62
CW2015_REG_VCELL = 0x02
CW2015_REG_SOC = 0x04
CW2015_REG_MODE = 0x0A

I2C_BUS = 1

def dump_registers():
    """Dump first 16 CW2015 registers"""
    print("Register dump (first 16 registers):")
    try:
        bus = smbus.SMBus(I2C_BUS)
        for reg in range(0x10):
            try:
                val = bus.read_byte_data(CW2015_ADDRESS, reg)
                print("5d")
            except Exception as e:
                print("5d")
        bus.close()
    except Exception as e:
        print(f"ERROR: Cannot access I2C bus: {e}")
        return False
    return True

def read_voltage():
    """Read battery voltage in mV"""
    try:
        bus = smbus.SMBus(I2C_BUS)
        # Try byte reads instead of word
        high = bus.read_byte_data(CW2015_ADDRESS, 0x02)
        low = bus.read_byte_data(CW2015_ADDRESS, 0x03)
        bus.close()

        voltage = (high << 8) | low
        voltage = voltage * 1.25  # Scale factor for CW2015
        return int(voltage)
    except Exception as e:
        return None, str(e)

def read_capacity():
    """Read battery capacity percentage"""
    try:
        bus = smbus.SMBus(I2C_BUS)
        # Try byte reads
        high = bus.read_byte_data(CW2015_ADDRESS, 0x04)
        low = bus.read_byte_data(CW2015_ADDRESS, 0x05)
        bus.close()

        capacity = (high << 8) | low
        capacity = capacity / 256.0
        return int(capacity)
    except Exception as e:
        return None, str(e)

def is_charging():
    """Check if power adapter is connected"""
    if not GPIO_AVAILABLE:
        return False
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(4, GPIO.IN)
        return GPIO.input(4) == GPIO.HIGH
    except Exception as e:
        return False

def get_status():
    """Get complete battery status"""
    voltage = read_voltage()
    capacity = read_capacity()
    charging = is_charging()

    if isinstance(voltage, tuple) or isinstance(capacity, tuple):
        return None

    if capacity >= 100:
        status = 'full'
    elif capacity < 5:
        status = 'low'
    elif charging:
        status = 'charging'
    else:
        status = 'discharging'

    return {
        'voltage_mv': voltage,
        'voltage_v': voltage / 1000,
        'capacity': capacity,
        'charging': charging,
        'status': status
    }

def test_device():
    """Test I2C device presence"""
    try:
        bus = smbus.SMBus(I2C_BUS)
        bus.read_byte(CW2015_ADDRESS)
        bus.close()
        return True
    except Exception as e:
        return False, str(e)

def main():
    """Run comprehensive battery tests"""
    print("UPS-Lite v1.3 Battery Monitor Test")
    print(f"I2C Address: 0x{CW2015_ADDRESS:02x}")
    print()

    # Test 1: Device presence
    print("Test 1: I2C Device Detection")
    result = test_device()
    if isinstance(result, tuple):
        print(f"FAIL: {result[1]}")
        print("Try: sudo i2cdetect -y 1")
        return
    print("PASS: Device found")
    print()

    # Test 2: Register dump
    print("Test 2: Register Dump")
    if not dump_registers():
        return
    print()

    # Test 3: Single readings
    print("Test 3: Single Readings")
    voltage = read_voltage()
    capacity = read_capacity()

    if isinstance(voltage, tuple):
        print(f"Voltage: FAIL - {voltage[1]}")
    else:
        print(".2f")

    if isinstance(capacity, tuple):
        print(f"Capacity: FAIL - {capacity[1]}")
    else:
        print(f"Capacity: {capacity}%")

    charging = is_charging()
    print(f"Charging: {charging}")
    print()

    # Test 4: Status summary
    print("Test 4: Status Summary")
    status = get_status()
    if status:
        print(f"Status: {status['status'].upper()}")
        print(".2f")
        print(f"Capacity: {status['capacity']}%")
        print(f"Charging: {status['charging']}")
    else:
        print("FAIL: Cannot read status")
    print()

    # Test 5: Continuous monitoring
    print("Test 5: Continuous Monitoring (Ctrl+C to stop)")
    try:
        while True:
            status = get_status()
            if status:
                print("6.2f")
            else:
                print("ERROR: Cannot read status")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nTest completed")

if __name__ == '__main__':
    main()
