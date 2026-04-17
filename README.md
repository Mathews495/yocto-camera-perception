# Yocto Camera Perception Image for QEMU (RK3588 / Rock 5B)

## Project Overview

This project builds a **camera perception ready Linux image** using the Yocto Project, targeting the **Radxa Rock 5B** (RK3588 SoC). The image runs inside **QEMU (qemuarm64)** for development and verification purposes, with a full **V4L2 camera byte stream pipeline** that can be tested without physical hardware.

The pipeline enables:
- Virtual camera device creation via the `vivid` kernel driver
- V4L2 subsystem for standardized camera access
- GStreamer multimedia framework for stream processing
- Python + OpenCV for camera perception application verification

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    QEMU Guest (aarch64)                         │
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌────────────┐    ┌────────┐  │
│  │  vivid   │───▶│  V4L2   │───▶│ GStreamer  │───▶│ Python │  │
│  │ (driver) │    │ subsys  │    │  pipeline  │    │ OpenCV │  │
│  └──────────┘    └──────────┘    └────────────┘    └────────┘  │
│  Generates        /dev/video0     Reads &           Processes   │
│  fake frames      interface       processes          frames     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Hardware Target

| Property | Value |
|---|---|
| Board | Radxa Rock 5B |
| SoC | Rockchip RK3588 |
| Architecture | AArch64 (ARM64) |
| Yocto Machine (QEMU) | `qemuarm64` |
| Yocto Machine (HW) | `rockchip-rk3588-evb` |

---

## Software Stack

| Component | Version |
|---|---|
| Yocto Project | 5.2 (Walnascar) |
| Linux Kernel | 6.12.19-yocto-standard |
| BitBake | 2.12.0 |
| GStreamer | 1.x |
| Python | 3.x |
| OpenCV | 4.x |

---

## Repository Structure

```
.
├── meta-camera/                          ← Custom Yocto layer (THIS REPO)
│   ├── conf/
│   │   └── layer.conf                   ← Layer configuration
│   ├── recipes-kernel/
│   │   └── linux/
│   │       ├── linux-yocto_%.bbappend   ← Kernel customization
│   │       └── files/
│   │           ├── camera-v4l2.cfg      ← V4L2 kernel config fragment
│   │           └── camera-v4l2.scc      ← Kernel feature descriptor
│   └── README
│
├── build/
│   └── conf/
│       ├── local.conf                   ← Build configuration
│       └── bblayers.conf                ← Layer paths
│
├── scripts/
│   ├── verify_stream.py                 ← Raw byte stream verification
│   └── camera_perception.py             ← OpenCV perception verification
│
├── .gitignore                           ← Excludes build artifacts
├── .gitattributes                       ← Line endings + LFS config
└── README.md                            ← This file
```

---

## Prerequisites

### Host System Requirements

| Requirement | Minimum |
|---|---|
| OS | Ubuntu 22.04 / 24.04 LTS |
| RAM | 8 GB (16 GB recommended) |
| Disk | 100 GB free |
| CPU | 4 cores (8+ recommended) |

### Required Host Packages

```bash
sudo apt update
sudo apt install -y \
    gawk wget git diffstat unzip texinfo gcc build-essential \
    chrpath socat cpio python3 python3-pip python3-pexpect \
    xz-utils debianutils iputils-ping python3-git python3-jinja2 \
    libegl1-mesa libsdl1.2-dev pylint xterm python3-subunit \
    mesa-common-dev zstd liblz4-tool file locales libacl1 \
    qemu-system-arm qemu-utils
```

### Ubuntu 24.04 Specific Fix

Ubuntu 24.04 restricts unprivileged user namespaces which breaks BitBake's network sandboxing. Apply this fix:

```bash
# Disable AppArmor restriction for user namespaces
sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0

# Make permanent
echo 'kernel.apparmor_restrict_unprivileged_userns=0' | \
  sudo tee /etc/sysctl.d/99-yocto-userns.conf
sudo sysctl --system
```

---

## Setup Instructions

### Step 1: Clone Poky and Required Layers

```bash
mkdir -p ~/Learn/yocto
cd ~/Learn/yocto

# Clone Poky (Yocto reference distribution)
git clone https://git.yoctoproject.org/poky -b walnascar

cd poky

# Clone meta-openembedded (provides multimedia, python, networking)
git clone https://github.com/openembedded/meta-openembedded.git -b walnascar

# Clone meta-rockchip (RK3588 BSP)
git clone https://github.com/JeffyCN/meta-rockchip.git -b walnascar
```

### Step 2: Clone This Repository

```bash
cd ~/Learn/yocto/poky
git clone <this-repo-url> meta-camera
```

### Step 3: Initialize Build Environment

```bash
source ~/Learn/yocto/poky/oe-init-build-env ~/Learn/yocto/poky/build
```

### Step 4: Configure bblayers.conf

Edit `build/conf/bblayers.conf`:

```bash
BBLAYERS ?= " \
  /home/<user>/Learn/yocto/poky/meta \
  /home/<user>/Learn/yocto/poky/meta-poky \
  /home/<user>/Learn/yocto/poky/meta-yocto-bsp \
  /home/<user>/Learn/yocto/poky/meta-openembedded/meta-oe \
  /home/<user>/Learn/yocto/poky/meta-openembedded/meta-python \
  /home/<user>/Learn/yocto/poky/meta-openembedded/meta-multimedia \
  /home/<user>/Learn/yocto/poky/meta-openembedded/meta-networking \
  /home/<user>/Learn/yocto/poky/meta-rockchip \
  /home/<user>/Learn/yocto/poky/meta-camera \
"
```

### Step 5: Configure local.conf

Key settings in `build/conf/local.conf`:

```bash
# Target machine
MACHINE ?= "qemuarm64"

# Image filesystem type
IMAGE_FSTYPES += "ext4"

# Image features (replaces deprecated debug-tweaks)
EXTRA_IMAGE_FEATURES += " \
    allow-empty-password \
    allow-root-login \
    serial-autologin-root \
    ssh-server-openssh \
"

# Required packages
IMAGE_INSTALL:append = " \
    v4l-utils \
    gstreamer1.0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    python3 \
    python3-numpy \
    python3-opencv \
    kernel-modules \
"

# Kernel module autoload
KERNEL_MODULE_AUTOLOAD += "vivid"

# QA fix for meta-rockchip patch headers
WARN_QA:append = " patch-status"
ERROR_QA:remove = "patch-status"

# Build performance (adjust to your CPU)
BB_NUMBER_THREADS = "8"
PARALLEL_MAKE = "-j8"
```

### Step 6: Verify Layers

```bash
bitbake-layers show-layers
bitbake-layers show-appends | grep linux-yocto
```

### Step 7: Verify Kernel Config Fragment

```bash
# Confirm fragment is in SRC_URI
bitbake -e virtual/kernel | grep "camera-v4l2"
```

### Step 8: Build the Image

```bash
bitbake core-image-full-cmdline
```

> **Note:** First build takes 2–4 hours depending on hardware.

---

## Running in QEMU

### Boot the Image

```bash
source ~/Learn/yocto/poky/oe-init-build-env ~/Learn/yocto/poky/build
runqemu qemuarm64 core-image-full-cmdline nographic
```

Login as `root` — no password required.

### Verify V4L2 Inside QEMU

```bash
# Check kernel config
zcat /proc/config.gz | grep -E "VIDEO_VIVID|VIDEO_DEV|MEDIA_SUPPORT"

# Load virtual camera driver
modprobe vivid

# Confirm video devices
ls /dev/video*
v4l2-ctl --list-devices

# Check supported formats
v4l2-ctl --device=/dev/video0 --list-formats-ext
```

### Capture a Raw Frame

```bash
v4l2-ctl --device=/dev/video0 \
  --set-fmt-video=width=640,height=480,pixelformat=YUYV \
  --stream-mmap \
  --stream-count=1 \
  --stream-to=/tmp/frame.raw

# Verify (should be 614400 bytes = 640x480x2)
ls -lh /tmp/frame.raw
wc -c /tmp/frame.raw
```

### GStreamer Pipeline Test

```bash
gst-launch-1.0 v4l2src device=/dev/video0 num-buffers=10 ! \
  video/x-raw,width=640,height=480 ! \
  filesink location=/tmp/gst_frame.raw

ls -lh /tmp/gst_frame.raw
```

### Python + OpenCV Verification

```bash
python3 /path/to/scripts/camera_perception.py
```

Expected output:
```
=== Camera Perception Verification ===
Device /dev/video0 opened successfully
Width           : 640
Height          : 480
Frame shape     : (480, 640, 3)
Bytes per frame : 921600
Frames received : 30/30
Total bytes     : 27,648,000
SUCCESS: Camera byte stream pipeline fully verified!
```

---

## Kernel Configuration

The `camera-v4l2.cfg` kernel fragment enables:

| Config Option | Value | Purpose |
|---|---|---|
| `CONFIG_VIDEO_DEV` | y | V4L2 core device support |
| `CONFIG_VIDEO_V4L2` | y | V4L2 API |
| `CONFIG_MEDIA_SUPPORT` | y | Media framework |
| `CONFIG_MEDIA_CAMERA_SUPPORT` | y | Camera device support |
| `CONFIG_MEDIA_CONTROLLER` | y | Media controller API |
| `CONFIG_USB_VIDEO_CLASS` | y | USB camera (UVC) support |
| `CONFIG_VIDEO_VIVID` | m | Virtual video test driver |
| `CONFIG_VIDEO_VIVID_CEC` | y | CEC support for vivid |

---

## Troubleshooting

### `debug-tweaks` is not a valid image feature
Replace with individual features in `local.conf`:
```bash
EXTRA_IMAGE_FEATURES += "allow-empty-password allow-root-login serial-autologin-root"
```

### `v4l2loopback` module not found
`v4l2loopback` is an out-of-tree module not available in linux-yocto. Use `vivid` instead which is built into the mainline kernel.

### PermissionError writing to `/proc/self/uid_map`
Ubuntu 24.04 blocks user namespaces. Fix:
```bash
sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0
```

### Kernel config fragment not applied
The linux-yocto kernel requires an `.scc` file alongside the `.cfg` file. Ensure both exist in `meta-camera/recipes-kernel/linux/files/`.

### `/dev/video0` is busy
```bash
fuser -k /dev/video0
modprobe -r vivid
modprobe vivid
```

### runqemu path error (`build/build/`)
Always source the environment with explicit path:
```bash
source ~/Learn/yocto/poky/oe-init-build-env ~/Learn/yocto/poky/build
```

---

## Git LFS — Is It Required?

**No, Git LFS is NOT required** for this project as long as you follow the `.gitignore` correctly.

| File Type | Size | Git LFS Needed? |
|---|---|---|
| `meta-camera/` layer files | KB | No — commit normally |
| `build/conf/*.conf` | KB | No — commit normally |
| `build/tmp/` build artifacts | 50–100 GB | **Excluded by .gitignore** |
| `build/sstate-cache/` | 10–30 GB | **Excluded by .gitignore** |
| `build/downloads/` | 5–20 GB | **Excluded by .gitignore** |
| Generated `.ext4` image | 700 MB | Excluded — use LFS if needed |

If you ever want to store pre-built images in the repo, then enable LFS:
```bash
git lfs install
git lfs track "*.ext4"
git lfs track "*.wic"
git add .gitattributes
```

---

## Next Steps

- [ ] Switch `MACHINE` to `rockchip-rk3588-evb` for real hardware deployment
- [ ] Add MIPI CSI camera driver support for Rock 5B physical camera
- [ ] Integrate real camera byte stream from host into QEMU via USB passthrough
- [ ] Add camera perception application (object detection, lane detection etc.)
- [ ] Add automated test scripts for CI/CD pipeline

---

## References

- [Yocto Project Documentation](https://docs.yoctoproject.org/)
- [Linux V4L2 Documentation](https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/v4l2.html)
- [vivid Virtual Video Driver](https://www.kernel.org/doc/html/latest/admin-guide/media/vivid.html)
- [meta-rockchip Layer](https://github.com/JeffyCN/meta-rockchip)
- [GStreamer V4L2 Plugin](https://gstreamer.freedesktop.org/documentation/video4linux2/)
- [Radxa Rock 5B](https://wiki.radxa.com/Rock5/hardware/5b)
