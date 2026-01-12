#!/bin/bash
# MasterChief OS Customization Script
# This script runs in the chroot environment during ISO build

set -e

echo "Running MasterChief OS customization..."

# Set timezone
ln -sf /usr/share/zoneinfo/UTC /etc/localtime

# Set hostname
echo "masterchief" > /etc/hostname

# Configure locales
locale-gen en_US.UTF-8
update-locale LANG=en_US.UTF-8

# Configure system settings
cat >> /etc/sysctl.conf <<EOF

# MasterChief OS - Security hardening
net.ipv4.conf.all.rp_filter=1
net.ipv4.conf.default.rp_filter=1
net.ipv4.tcp_syncookies=1
net.ipv4.icmp_echo_ignore_broadcasts=1
net.ipv4.icmp_ignore_bogus_error_responses=1
net.ipv4.conf.all.accept_source_route=0
net.ipv6.conf.all.accept_source_route=0
EOF

# Configure SSH
sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Enable Docker service
systemctl enable docker

# Enable SSH service
systemctl enable ssh

# Configure automatic updates for security
cat > /etc/apt/apt.conf.d/50unattended-upgrades <<EOF
Unattended-Upgrade::Allowed-Origins {
    "\${distro_id}:\${distro_codename}-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF

# Create MasterChief user (will be customized on first boot)
useradd -m -s /bin/bash -G sudo,docker masterchief || true

# Set up MasterChief platform directories
mkdir -p /opt/masterchief
mkdir -p /etc/masterchief
mkdir -p /var/log/masterchief
mkdir -p /var/lib/masterchief

# Add MasterChief banner
cat > /etc/update-motd.d/00-masterchief <<'EOF'
#!/bin/bash
cat << "BANNER"
 __  __           _            ____ _     _       __ 
|  \/  | __ _ ___| |_ ___ _ __/ ___| |__ (_) ___ / _|
| |\/| |/ _` / __| __/ _ \ '__\___ \ '_ \| |/ _ \ |_ 
| |  | | (_| \__ \ ||  __/ |   ___) | | | |  __/  _|
|_|  |_|\__,_|___/\__\___|_|  |____/|_| |_|\___|_|  
                                                      
    Enterprise DevOps Platform - Version 1.0.0
BANNER
EOF
chmod +x /etc/update-motd.d/00-masterchief

echo "Customization complete!"
