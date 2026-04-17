#!/usr/bin/env python3
"""
Camera Perception Verification Script
Yocto QEMU Camera Pipeline - Rock 5B / RK3588
"""

import cv2
import time
import sys
import os

print("=== Camera Perception Verification ===")
print()

# Try each video device using V4L2 backend directly
cap = None
device_index = None

for i in range(4):
    test_cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
    if test_cap.isOpened():
        print(f"Device /dev/video{i} opened successfully")
        cap = test_cap
        device_index = i
        break
    else:
        print(f"Device /dev/video{i} not available, trying next...")
    test_cap.release()

if cap is None or device_index is None:
    print("ERROR: No camera device available")
    print("Try: modprobe vivid")
    sys.exit(1)

# Set format explicitly
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y', 'U', 'Y', 'V'))

print()
print(f"Device          : /dev/video{device_index}")
print(f"Width           : {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}")
print(f"Height          : {int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
print(f"FPS             : {cap.get(cv2.CAP_PROP_FPS)}")
print()

# Read and verify frames
frames_received = 0
total_bytes = 0
start_time = time.time()

for i in range(30):
    ret, frame = cap.read()
    if ret:
        frames_received += 1
        total_bytes += frame.nbytes
        if frames_received == 1:
            print(f"Frame shape     : {frame.shape}")
            print(f"Frame dtype     : {frame.dtype}")
            print(f"Bytes per frame : {frame.nbytes}")
            print(f"First pixel RGB : {frame[0, 0]}")
            print()
    else:
        print(f"WARNING: Frame {i} read failed")

elapsed = time.time() - start_time
fps = frames_received / elapsed if elapsed > 0 else 0

print(f"=== Results ===")
print(f"Frames received : {frames_received}/30")
print(f"Total bytes     : {total_bytes:,}")
print(f"Achieved FPS    : {fps:.2f}")
print(f"Elapsed time    : {elapsed:.2f} seconds")

if frames_received >= 25:
    print()
    print("SUCCESS: Camera byte stream pipeline fully verified!")
    sys.exit(0)
else:
    print(f"WARNING: Only received {frames_received} of 30 frames")
    sys.exit(1)

cap.release()
