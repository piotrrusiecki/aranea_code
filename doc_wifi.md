# Aranea Robot WiFi Configuration Guide

*Complete guide for configuring WiFi priorities and remote access*

## Overview

The Aranea robot uses **NetworkManager** with priority-based WiFi connections to enable seamless remote access via mobile hotspot while maintaining fallback to home networks.

## Priority System

**Higher priority number = Preferred network**

| Network Type | Priority | Purpose |
|--------------|----------|---------|
| Phone Hotspot | 100 | Remote field operations |
| Home Network | 50 | Indoor development/testing |
| Wired Connection | -999 | Emergency fallback |

## Configuration Steps

### 1. Check Current System

```bash
# Verify NetworkManager is running
sudo systemctl status NetworkManager

# View existing connections
nmcli connection show

# Check current WiFi networks
nmcli device wifi list
```

### 2. Add Phone Hotspot (High Priority)

```bash
# Add WiFi hotspot connection
sudo nmcli connection add \
    type wifi \
    ifname wlan0 \
    con-name "Morningdew" \
    autoconnect yes \
    ssid "Morningdew"

# Configure security (WPA2-Personal)
sudo nmcli connection modify "Morningdew" \
    wifi-sec.key-mgmt wpa-psk \
    wifi-sec.psk "sasanka86"

# Set IPv4 to DHCP and disable IPv6
sudo nmcli connection modify "Morningdew" \
    ipv4.method auto \
    ipv6.method ignore

# Set HIGH priority (100)
sudo nmcli connection modify "Morningdew" \
    connection.autoconnect-priority 100
```

### 3. Configure Home Network Priority

```bash
# Set medium priority for existing home network
sudo nmcli connection modify "Atryo.at" \
    connection.autoconnect-priority 50
```

### 4. Verify Configuration

```bash
# Check all connections with priorities
nmcli -f NAME,TYPE,AUTOCONNECT,AUTOCONNECT-PRIORITY connection show

# Verify WiFi security settings
nmcli connection show "Morningdew" | grep -E "(wifi-sec|ipv4)"

# Check current active connection
nmcli connection show --active
```

## Connection Behavior

### Automatic Priority Switching
1. **Phone hotspot active** → Robot connects to mobile hotspot
2. **Phone hotspot off** → Robot falls back to home network  
3. **No WiFi available** → Falls back to wired connection

### Manual Connection Testing
```bash
# Switch to phone hotspot (if active)
sudo nmcli connection up "Morningdew"

# Switch back to home network
sudo nmcli connection up "Atryo.at"

# Check current IP address
ip addr show wlan0 | grep "inet "
```

## Troubleshooting

### Common Issues

**1. Robot connects but can't browse to IP**
```bash
# Check if Aranea service is running
sudo systemctl status aranea-server.service

# Verify web server is listening
sudo netstat -tlnp | grep :80

# Get current IP
ip addr show wlan0 | grep "inet " | awk '{print $2}' | cut -d/ -f1
```

**2. WiFi priority not working**
```bash
# Restart NetworkManager
sudo systemctl restart NetworkManager

# Force reconfiguration
sudo nmcli connection reload
```

**3. Connection drops frequently**
```bash
# Check WiFi signal strength
nmcli device wifi list

# View connection logs
sudo journalctl -u NetworkManager -f
```

**4. Robot connects to hotspot but can't access web interface**
- **Solution**: Change phone hotspot from "5GHz steering" to "Concurrent 2.4GHz + 5GHz"
- **Reason**: Raspberry Pi WiFi adapters have better compatibility with dual-band concurrent mode
- **Location**: Phone Settings → Mobile Hotspot → Advanced → Band Selection

### Reset WiFi Configuration
```bash
# Remove problematic connection
sudo nmcli connection delete "ConnectionName"

# Restart networking
sudo systemctl restart NetworkManager
```

## Remote Access Setup

### 1. Ensure Auto-Start Service
```bash
# Copy service file to system
sudo cp .services/aranea-server.service /etc/systemd/system/

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable aranea-server.service
sudo systemctl start aranea-server.service
```

### 2. Test Remote Access

**From Robot (verify services):**
```bash
# Check service status
sudo systemctl status aranea-server.service

# Verify web server listening
sudo netstat -tlnp | grep :80

# Get IP for remote access
ip addr show wlan0 | grep "inet " | awk '{print $2}' | cut -d/ -f1
```

**From Phone/Computer:**
1. Connect to same network as robot
2. Open browser to `http://[robot_ip]/`
3. Access full web interface

## Network Security Notes

- **WPA2-Personal**: Standard security for phone hotspots
- **Dual-Band Operation**: Use concurrent 2.4GHz + 5GHz for best compatibility
- **IPv6 Disabled**: Simplifies routing and connectivity
- **Auto-DHCP**: Ensures proper IP assignment from any network

## Field Testing Results ✅

**Successful outdoor tests** with following configuration requirements:

### Phone Hotspot Settings
- **Band Selection**: **Concurrent 2.4GHz + 5GHz** (not 5GHz-only steering)
- **Compatibility**: Raspberry Pi WiFi adapters work better with dual-band concurrent mode
- **Performance**: Full remote web interface functionality confirmed in field conditions

## Usage Workflow

### Field Operations
1. **Enable phone hotspot** "Morningdew"
2. **Robot auto-connects** (highest priority)
3. **Access via browser** at assigned IP
4. **Full remote control** available

### Home Development
1. **Disable phone hotspot**
2. **Robot falls back** to home network
3. **Continue development** with same interface

## Files Modified
- **NetworkManager connections**: `/etc/NetworkManager/system-connections/`
- **Service file**: `.services/aranea-server.service`
- **System service**: `/etc/systemd/system/aranea-server.service`

---

*Last updated: August 2025 - Mobile hotspot priority configuration*