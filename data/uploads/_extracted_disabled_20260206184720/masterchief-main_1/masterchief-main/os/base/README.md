# MasterChief OS Base Configuration

This directory contains the base OS configuration for MasterChief OS.

## Components

- **Distribution**: Ubuntu Server 22.04 LTS / Debian 12
- **Kernel**: Latest stable kernel with security patches
- **Init System**: systemd
- **Security**: CIS Level 1 compliance, AppArmor enabled

## Features

### Hardened by Default

- Kernel hardening (sysctl)
- AppArmor profiles
- Firewall (UFW) pre-configured
- SSH hardened (no root login, key-based auth)
- Automatic security updates
- Audit logging (auditd)

### Pre-configured Services

- Docker with socket activation
- SSH server
- Network Manager
- Systemd timers for maintenance tasks

### System Optimization

- Minimal package set for reduced attack surface
- Optimized for DevOps workloads
- Fast boot time (~10 seconds)
- Low memory footprint (~500MB idle)

## Customization

To customize the base OS before building the ISO:

1. Edit `os/iso-builder/packages/base.list` to add/remove packages
2. Modify `os/iso-builder/scripts/customize.sh` for system configuration
3. Update `os/iso-builder/preseed/preseed.cfg` for installation options

## Security Compliance

The base OS meets the following security standards:

- CIS Ubuntu Linux 22.04 LTS Benchmark Level 1
- PCI DSS v3.2.1 (selected controls)
- NIST 800-53 (selected controls)

## Performance Tuning

The base OS includes the following optimizations:

- I/O scheduler: mq-deadline for SSDs, bfq for HDDs
- Network: TCP BBR congestion control
- Memory: vm.swappiness=10 for server workloads
- Disk: noatime mount option for reduced I/O
