#!/usr/bin/env python3
"""
Raw V4L2 Byte Stream Verification Script
Yocto QEMU Camera Pipeline - Rock 5B / RK3588
"""

import os
import time
import sys

DEVICE = "/dev/video0"
WIDTH = 640
HEIGHT = 480
BYTES_PER_PIXEL = 2  # YUYV format = 2 bytes per pixel
FRAME_SIZE = WIDTH * HEIGHT * BYTES_PER_PIXEL

print("=== Raw V4L2 Byte Stream Verification ===")
print()
print(f"Device          : {DEVICE}")
print(f"Resolution      : {WIDTH}x{HEIGHT}")
print(f"Format          : YUYV")
print(f"Expected bytes  : {FRAME_SIZE} ({WIDTH}x{HEIGHT}x{BYTES_PER_PIXEL})")
print()

if not os.path.exists(DEVICE):
    print(f"ERROR: {DEVICE} not found")
    print("Try: modprobe vivid")
    sys.exit(1)

try:
    fd = os.open(DEVICE, os.O_RDWR)
    print(f"Device opened successfully (fd={fd})")

    start = time.time()
    data = os.read(fd, FRAME_SIZE)
    elapsed = time.time() - start

    print(f"Bytes received  : {len(data)}")
    print(f"Time taken      : {elapsed:.3f} seconds")
    print(f"First 16 bytes  : {data[:16].hex()}")
    print(f"Last  16 bytes  : {data[-16:].hex()}")

    if len(data) == FRAME_SIZE:
        print()
        print("SUCCESS: Full frame byte stream received!")
    else:
        print(f"WARNING: Expected {FRAME_SIZE} bytes, got {len(data)}")

    os.close(fd)

except PermissionError:
    print(f"ERROR: Permission denied opening {DEVICE}")
    print("Check: ls -lh /dev/video0")
except OSError as e:
    print(f"ERROR: {e}")
    sys.exit(1)
