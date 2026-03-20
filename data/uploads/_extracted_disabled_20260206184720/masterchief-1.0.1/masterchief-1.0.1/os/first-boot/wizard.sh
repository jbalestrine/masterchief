#!/bin/bash
# MasterChief First Boot Configuration Wizard

set -e

CONFIG_FILE="/etc/masterchief/first-boot.conf"

# Check if we're running in a terminal
if [ ! -t 0 ]; then
    echo "This wizard requires an interactive terminal"
    exit 1
fi

# Install dialog if not present
if ! command -v dialog &> /dev/null; then
    apt-get update -qq
    apt-get install -y dialog
fi

TEMP_FILE=$(mktemp)
trap "rm -f $TEMP_FILE" EXIT

# Welcome screen
dialog --title "MasterChief DevOps Platform" \
       --msgbox "Welcome to MasterChief OS!\n\nThis wizard will help you configure your system.\n\nPress Enter to continue." 10 60

# Set hostname
dialog --title "Hostname Configuration" \
       --inputbox "Enter hostname for this system:" 8 60 "masterchief" 2>$TEMP_FILE
HOSTNAME=$(cat $TEMP_FILE)
hostnamectl set-hostname "$HOSTNAME"

# Network configuration
dialog --title "Network Configuration" \
       --menu "Select network configuration:" 12 60 2 \
       1 "DHCP (automatic)" \
       2 "Static IP" 2>$TEMP_FILE
NETWORK_CHOICE=$(cat $TEMP_FILE)

if [ "$NETWORK_CHOICE" = "2" ]; then
    dialog --title "Static IP Configuration" \
           --form "Enter network details:" 12 60 4 \
           "IP Address:" 1 1 "192.168.1.100" 1 20 20 0 \
           "Netmask:" 2 1 "255.255.255.0" 2 20 20 0 \
           "Gateway:" 3 1 "192.168.1.1" 3 20 20 0 \
           "DNS:" 4 1 "8.8.8.8" 4 20 20 0 2>$TEMP_FILE
fi

# Create admin user
dialog --title "Admin User Creation" \
       --inputbox "Enter admin username:" 8 60 "admin" 2>$TEMP_FILE
ADMIN_USER=$(cat $TEMP_FILE)

dialog --title "Admin User Creation" \
       --passwordbox "Enter password for $ADMIN_USER:" 8 60 2>$TEMP_FILE
ADMIN_PASS=$(cat $TEMP_FILE)

# Create user
useradd -m -s /bin/bash -G sudo,docker "$ADMIN_USER" 2>/dev/null || true
echo "$ADMIN_USER:$ADMIN_PASS" | chpasswd

# SSH configuration
dialog --title "SSH Configuration" \
       --yesno "Enable SSH access?" 7 40
if [ $? -eq 0 ]; then
    systemctl enable ssh
    systemctl start ssh
    
    dialog --title "SSH Configuration" \
           --yesno "Allow password authentication?" 7 40
    if [ $? -ne 0 ]; then
        sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
        systemctl restart ssh
    fi
fi

# Timezone
TIMEZONE=$(dialog --stdout --title "Timezone Selection" \
           --menu "Select your timezone:" 20 60 10 \
           "UTC" "Coordinated Universal Time" \
           "America/New_York" "Eastern Time" \
           "America/Chicago" "Central Time" \
           "America/Denver" "Mountain Time" \
           "America/Los_Angeles" "Pacific Time" \
           "Europe/London" "UK Time" \
           "Europe/Paris" "Central European Time")
timedatectl set-timezone "$TIMEZONE"

# Initialize platform services
dialog --title "Platform Services" \
       --yesno "Initialize MasterChief platform services?" 7 50
if [ $? -eq 0 ]; then
    /usr/local/bin/install-platform.sh
    systemctl start masterchief
fi

# Final message
dialog --title "Configuration Complete" \
       --msgbox "MasterChief OS is now configured!\n\nYou can access the web interface at:\nhttps://$(hostname -I | awk '{print $1}'):8443\n\nUsername: $ADMIN_USER\nPassword: (as set)\n\nPress Enter to finish." 12 60

clear
echo "======================================"
echo "MasterChief OS Configuration Complete"
echo "======================================"
echo ""
echo "System Details:"
echo "  Hostname: $HOSTNAME"
echo "  Admin User: $ADMIN_USER"
echo "  IP Address: $(hostname -I | awk '{print $1}')"
echo "  Web Interface: https://$(hostname -I | awk '{print $1}'):8443"
echo ""
echo "You can now log in with your admin credentials."
