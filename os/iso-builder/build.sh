#!/bin/bash
# MasterChief OS ISO Builder
# Builds a bootable ISO image with the MasterChief platform pre-installed

set -e

VERSION="1.0.0"
BUILD_DIR="./build"
OUTPUT_DIR="./output"
ISO_NAME="masterchief-${VERSION}-amd64.iso"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    log_error "Please run as root (sudo ./build.sh)"
    exit 1
fi

# Check dependencies
log_info "Checking dependencies..."
REQUIRED_PACKAGES="debootstrap squashfs-tools genisoimage syslinux-utils isolinux xorriso"
MISSING_PACKAGES=""

for pkg in $REQUIRED_PACKAGES; do
    if ! dpkg -l | grep -q "^ii  $pkg"; then
        MISSING_PACKAGES="$MISSING_PACKAGES $pkg"
    fi
done

if [ -n "$MISSING_PACKAGES" ]; then
    log_info "Installing missing packages:$MISSING_PACKAGES"
    apt-get update
    apt-get install -y $MISSING_PACKAGES
fi

# Clean previous build
log_info "Cleaning previous build..."
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR
mkdir -p $OUTPUT_DIR

# Create base system
log_info "Creating base Ubuntu 22.04 system..."
debootstrap --arch=amd64 jammy $BUILD_DIR/chroot http://archive.ubuntu.com/ubuntu/

# Mount necessary filesystems
log_info "Mounting necessary filesystems..."
mount --bind /dev $BUILD_DIR/chroot/dev
mount --bind /dev/pts $BUILD_DIR/chroot/dev/pts
mount --bind /proc $BUILD_DIR/chroot/proc
mount --bind /sys $BUILD_DIR/chroot/sys

# Cleanup function
cleanup() {
    log_info "Cleaning up mounts..."
    umount -l $BUILD_DIR/chroot/dev/pts 2>/dev/null || true
    umount -l $BUILD_DIR/chroot/dev 2>/dev/null || true
    umount -l $BUILD_DIR/chroot/proc 2>/dev/null || true
    umount -l $BUILD_DIR/chroot/sys 2>/dev/null || true
}

trap cleanup EXIT

# Configure apt sources
log_info "Configuring apt sources..."
cat > $BUILD_DIR/chroot/etc/apt/sources.list <<EOF
deb http://archive.ubuntu.com/ubuntu jammy main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu jammy-updates main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu jammy-security main restricted universe multiverse
EOF

# Install base packages
log_info "Installing base packages..."
chroot $BUILD_DIR/chroot apt-get update
cat packages/base.list | xargs chroot $BUILD_DIR/chroot apt-get install -y

# Install DevOps tools
log_info "Installing DevOps tools..."
cat packages/devops.list | xargs chroot $BUILD_DIR/chroot apt-get install -y

# Copy platform files
log_info "Installing MasterChief platform..."
mkdir -p $BUILD_DIR/chroot/opt/masterchief
cp -r ../../platform $BUILD_DIR/chroot/opt/masterchief/
cp -r ../../addons $BUILD_DIR/chroot/opt/masterchief/
cp -r ../../scripts $BUILD_DIR/chroot/opt/masterchief/
cp -r ../../docs $BUILD_DIR/chroot/opt/masterchief/

# Run customization script
log_info "Running customization script..."
cp scripts/customize.sh $BUILD_DIR/chroot/tmp/
chroot $BUILD_DIR/chroot /bin/bash /tmp/customize.sh

# Install platform installer
log_info "Installing platform installer..."
cp scripts/install-platform.sh $BUILD_DIR/chroot/usr/local/bin/
chmod +x $BUILD_DIR/chroot/usr/local/bin/install-platform.sh

# Copy first boot script
log_info "Installing first boot script..."
cp scripts/first-boot.sh $BUILD_DIR/chroot/etc/init.d/masterchief-firstboot
chmod +x $BUILD_DIR/chroot/etc/init.d/masterchief-firstboot
chroot $BUILD_DIR/chroot update-rc.d masterchief-firstboot defaults

# Clean up
log_info "Cleaning up chroot..."
chroot $BUILD_DIR/chroot apt-get clean
rm -rf $BUILD_DIR/chroot/tmp/*
rm -rf $BUILD_DIR/chroot/var/lib/apt/lists/*

# Create squashfs
log_info "Creating squashfs filesystem..."
mkdir -p $BUILD_DIR/image/casper
mksquashfs $BUILD_DIR/chroot $BUILD_DIR/image/casper/filesystem.squashfs -comp xz

# Copy kernel and initrd
log_info "Copying kernel and initrd..."
cp $BUILD_DIR/chroot/boot/vmlinuz-* $BUILD_DIR/image/casper/vmlinuz
cp $BUILD_DIR/chroot/boot/initrd.img-* $BUILD_DIR/image/casper/initrd

# Create isolinux configuration
log_info "Creating bootloader configuration..."
mkdir -p $BUILD_DIR/image/isolinux
cat > $BUILD_DIR/image/isolinux/isolinux.cfg <<EOF
DEFAULT live
LABEL live
  KERNEL /casper/vmlinuz
  APPEND initrd=/casper/initrd boot=casper quiet splash ---
LABEL install
  KERNEL /casper/vmlinuz
  APPEND initrd=/casper/initrd boot=casper automatic-ubiquity quiet splash ---
EOF

cp /usr/lib/ISOLINUX/isolinux.bin $BUILD_DIR/image/isolinux/
cp /usr/lib/syslinux/modules/bios/*.c32 $BUILD_DIR/image/isolinux/

# Create GRUB configuration
mkdir -p $BUILD_DIR/image/boot/grub
cat > $BUILD_DIR/image/boot/grub/grub.cfg <<EOF
set timeout=10
set default=0

menuentry "MasterChief OS - Live Boot" {
    linux /casper/vmlinuz boot=casper quiet splash ---
    initrd /casper/initrd
}

menuentry "MasterChief OS - Install" {
    linux /casper/vmlinuz boot=casper automatic-ubiquity quiet splash ---
    initrd /casper/initrd
}
EOF

# Create manifest
log_info "Creating manifest..."
chroot $BUILD_DIR/chroot dpkg-query -W --showformat='${Package} ${Version}\n' > $BUILD_DIR/image/casper/filesystem.manifest

# Build ISO
log_info "Building ISO image..."
cd $BUILD_DIR/image
xorriso -as mkisofs \
    -iso-level 3 \
    -full-iso9660-filenames \
    -volid "MasterChief_OS_${VERSION}" \
    -eltorito-boot isolinux/isolinux.bin \
    -eltorito-catalog isolinux/boot.cat \
    -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    -output ../../$OUTPUT_DIR/$ISO_NAME \
    .

cd ../..

# Calculate checksums
log_info "Calculating checksums..."
cd $OUTPUT_DIR
md5sum $ISO_NAME > ${ISO_NAME}.md5
sha256sum $ISO_NAME > ${ISO_NAME}.sha256
cd ..

# Print summary
log_info "Build complete!"
echo ""
echo "======================================"
echo "ISO Build Summary"
echo "======================================"
echo "ISO file: $OUTPUT_DIR/$ISO_NAME"
echo "Size: $(du -h $OUTPUT_DIR/$ISO_NAME | cut -f1)"
echo "MD5: $(cat $OUTPUT_DIR/${ISO_NAME}.md5 | cut -d' ' -f1)"
echo "SHA256: $(cat $OUTPUT_DIR/${ISO_NAME}.sha256 | cut -d' ' -f1)"
echo "======================================"
