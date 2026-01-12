#!/bin/bash
# MasterChief USB Creator
# Creates a bootable USB drive from an ISO image

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <iso-file> <usb-device>"
    echo "Example: $0 masterchief-1.0.0-amd64.iso /dev/sdb"
    exit 1
fi

ISO_FILE="$1"
USB_DEVICE="$2"

# Verify ISO file exists
if [ ! -f "$ISO_FILE" ]; then
    log_error "ISO file not found: $ISO_FILE"
    exit 1
fi

# Verify USB device exists
if [ ! -b "$USB_DEVICE" ]; then
    log_error "USB device not found: $USB_DEVICE"
    exit 1
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    log_error "Please run as root (sudo $0 $@)"
    exit 1
fi

# Warn about data loss
log_warn "WARNING: This will erase all data on $USB_DEVICE!"
echo -n "Are you sure you want to continue? (yes/no): "
read -r response
if [ "$response" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

# Unmount any mounted partitions
log_info "Unmounting any mounted partitions..."
umount ${USB_DEVICE}* 2>/dev/null || true

# Write ISO to USB
log_info "Writing ISO to USB device..."
log_info "This may take several minutes..."
dd if="$ISO_FILE" of="$USB_DEVICE" bs=4M status=progress oflag=sync

# Sync to ensure all data is written
log_info "Syncing..."
sync

log_info "Done! USB drive is now bootable."
log_info "You can safely remove the USB drive."
