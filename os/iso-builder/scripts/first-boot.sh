#!/bin/bash
# MasterChief First Boot Initialization
# This script runs on first boot to configure the system

### BEGIN INIT INFO
# Provides:          masterchief-firstboot
# Required-Start:    $network $remote_fs
# Required-Stop:     $network $remote_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: MasterChief first boot configuration
### END INIT INFO

FIRST_BOOT_FLAG="/var/lib/masterchief/.first-boot-done"

if [ -f "$FIRST_BOOT_FLAG" ]; then
    exit 0
fi

echo "======================================"
echo "MasterChief First Boot Configuration"
echo "======================================"

# Run the first boot wizard
if [ -f /opt/masterchief/os/first-boot/wizard.sh ]; then
    /opt/masterchief/os/first-boot/wizard.sh
fi

# Mark first boot as complete
touch "$FIRST_BOOT_FLAG"

# Disable this service after first run
update-rc.d -f masterchief-firstboot remove

echo "First boot configuration complete!"
