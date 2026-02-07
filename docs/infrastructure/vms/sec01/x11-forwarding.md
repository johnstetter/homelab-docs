# X11 Forwarding Setup Guide

Complete setup guide for X11 forwarding to access GUI security tools on sec01 from macOS and Linux clients.

## Overview

X11 forwarding allows GUI applications running on the headless sec01 VM to display on your local desktop. This enables full access to graphical security tools like Burp Suite, Wireshark, and OWASP ZAP.

### Architecture

```
┌─────────────────┐    SSH -X Connection    ┌─────────────────┐
│  Local Client   │ ◄─────────────────────► │    sec01 VM     │
│                 │                         │                 │
│  ┌───────────┐  │    X11 Protocol over   │  ┌───────────┐  │
│  │ X Server  │  │ ◄─── SSH Tunnel ─────► │  │ X Client  │  │
│  │(XQuartz/X)│  │                         │  │(Security  │  │
│  │           │  │                         │  │  Tools)   │  │
│  └───────────┘  │                         │  └───────────┘  │
└─────────────────┘                         └─────────────────┘
   Display: :0.0                              Display: :10.0
```

## macOS Setup

### Prerequisites

- macOS 10.14 or later
- Administrative access for software installation
- Network access to sec01 VM (192.168.1.25)

### Step 1: Install XQuartz

XQuartz is the X11 server implementation for macOS.

=== "Homebrew (Recommended)"

    ```bash
    # Install via Homebrew
    brew install --cask xquartz

    # Or download directly from https://www.xquartz.org/
    ```

=== "Manual Installation"

    1. Download XQuartz from [xquartz.org](https://www.xquartz.org/)
    2. Open the `.dmg` file
    3. Run the installer package
    4. Follow the installation wizard

### Step 2: Configure XQuartz

```bash
# Launch XQuartz (required for initial setup)
open -a XQuartz

# Configure XQuartz preferences
defaults write org.xquartz.X11 enable_iglx -bool true
defaults write org.xquartz.X11 nolisten_tcp -bool false
defaults write org.xquartz.X11 no_auth -bool false
```

**Important:** Log out and log back in after installation for XQuartz to take effect.

### Step 3: Configure SSH Client

Create or edit your SSH configuration:

```bash
# Create SSH config directory if it doesn't exist
mkdir -p ~/.ssh

# Edit SSH configuration
vim ~/.ssh/config
```

Add the following configuration:

```ssh
# sec01 Security VM with X11 forwarding
Host sec01
    HostName 192.168.1.25
    User stetter
    Port 22
    ForwardX11 yes
    ForwardX11Trusted yes
    Compression yes
    ServerAliveInterval 60
    ServerAliveCountMax 3

# Optional: X11 forwarding for all homelab hosts
Host 192.168.1.*
    ForwardX11 yes
    ForwardX11Trusted yes
    Compression yes
```

### Step 4: Test X11 Forwarding

```bash
# Connect with X11 forwarding
ssh -X sec01

# Test basic X11 functionality
echo $DISPLAY  # Should show something like localhost:10.0
xeyes &        # Should display moving eyes on your desktop
xclock &       # Should display a clock window

# Test with Kali tools
xterm &        # Should open a terminal window
```

### Step 5: Launch Security Tools

```bash
# Launch GUI security tools
burpsuite &
wireshark &
zaproxy &

# Launch with specific memory settings
java -Xmx4g -jar /opt/BurpSuitePro/burpsuite_pro.jar &
```

## Linux Setup

### Prerequisites

- Linux distribution with X11 or Wayland
- SSH client installed
- Network access to sec01 VM

### Step 1: Install X11 Server (if needed)

Most Linux distributions include X11 by default. Install if missing:

=== "Ubuntu/Debian"

    ```bash
    # Install X11 server and utilities
    sudo apt update
    sudo apt install xorg xauth xhost

    # For minimal installations
    sudo apt install xserver-xorg-core xauth
    ```

=== "RHEL/CentOS/Fedora"

    ```bash
    # Install X11 server and utilities
    sudo dnf install xorg-x11-server-Xorg xorg-x11-xauth xorg-x11-apps

    # Or on older systems
    sudo yum install xorg-x11-server-Xorg xorg-x11-xauth xorg-x11-apps
    ```

=== "Arch Linux"

    ```bash
    # Install X11 server and utilities
    sudo pacman -S xorg-server xorg-xauth xorg-apps
    ```

### Step 2: Configure SSH Client

Edit your SSH configuration:

```bash
vim ~/.ssh/config
```

Add the sec01 configuration:

```ssh
# sec01 Security VM with X11 forwarding
Host sec01
    HostName 192.168.1.25
    User stetter
    Port 22
    ForwardX11 yes
    ForwardX11Trusted yes
    Compression yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

### Step 3: Configure X11 Authorization

```bash
# Allow X11 connections from localhost (be cautious on multi-user systems)
xhost +localhost

# Or more secure: allow specific display
xhost +local:

# Generate and transfer X11 authentication cookies (automatic with SSH -X)
xauth list
```

### Step 4: Test X11 Forwarding

```bash
# Connect with X11 forwarding
ssh -X sec01

# Verify X11 environment
echo $DISPLAY      # Should show localhost:10.0 or similar
xauth list         # Should show authentication entries

# Test with simple X11 applications
xeyes &
xclock &
xterm &
```

### Step 5: Launch Security Tools

```bash
# GUI security tools
burpsuite &
wireshark &
zaproxy &

# Terminal-based tools that may use GUI
msfconsole
# In Metasploit: use auxiliary modules with GUI components
```

## Wayland Support (Linux)

For systems using Wayland instead of X11:

### XWayland Setup

```bash
# Ensure XWayland is installed
sudo apt install xwayland    # Ubuntu/Debian
sudo dnf install xorg-x11-server-Xwayland  # Fedora

# Set environment variable for X11 apps
export XDG_SESSION_TYPE=x11
export GDK_BACKEND=x11
export QT_QPA_PLATFORM=xcb

# Connect with X11 forwarding
ssh -X sec01
```

### Alternative: Enable X11 on Wayland

```bash
# For GNOME on Wayland
sudo vim /etc/gdm3/custom.conf

# Uncomment the following line:
WaylandEnable=false

# Restart display manager
sudo systemctl restart gdm3
```

## Performance Optimization

### Network Optimization

```bash
# Use SSH compression for slower connections
ssh -X -C sec01

# Enable trusted X11 forwarding for better performance (local network only)
ssh -Y sec01

# Use multiplexed connections for multiple sessions
ssh -X -o ControlMaster=auto -o ControlPath=~/.ssh/master-%r@%h:%p sec01
```

### X11 Performance Tuning

```bash
# On sec01, optimize X11 forwarding
echo "export DISPLAY=:10.0" >> ~/.bashrc

# Reduce X11 network traffic
export QT_X11_NO_MITSHM=1
export _JAVA_AWT_WM_NONREPARENTING=1

# For high-latency connections
export LIBGL_ALWAYS_INDIRECT=1
```

### Memory Management

```bash
# Monitor X11 memory usage on client
ps aux | grep X

# Adjust tool memory settings
export JAVA_OPTS="-Xmx4g -XX:+UseG1GC"

# Kill unused X11 applications
pkill -f "burpsuite|wireshark"
```

## Troubleshooting

### Common Issues

#### "Cannot open display" Error

```bash
# Symptom
Error: Can't open display: localhost:10.0

# Solutions
1. Check X11 forwarding is enabled:
   ssh -X -v sec01  # Look for "Requesting X11 forwarding"

2. Verify DISPLAY variable:
   echo $DISPLAY    # Should show localhost:10.0 or similar

3. Check X11 authentication:
   xauth list

4. Restart SSH connection:
   exit; ssh -X sec01
```

#### "X11 forwarding request failed" Error

```bash
# Check SSH server configuration on sec01
sudo vim /etc/ssh/sshd_config

# Ensure these settings are enabled:
X11Forwarding yes
X11DisplayOffset 10
X11UseLocalhost yes

# Restart SSH service
sudo systemctl restart sshd
```

#### Performance Issues

```bash
# Symptoms: Slow GUI response, choppy graphics

# Solutions:
1. Enable compression:
   ssh -X -C sec01

2. Use trusted forwarding (local networks only):
   ssh -Y sec01

3. Reduce color depth:
   ssh -X sec01
   export DISPLAY=:10.0
   xdpyinfo | grep "depth of root"  # Check current depth
```

#### macOS-Specific Issues

```bash
# XQuartz not starting automatically
launchctl load -w /Library/LaunchAgents/org.xquartz.startx.plist

# Security & Privacy blocking XQuartz
# System Preferences → Security & Privacy → Privacy → Accessibility
# Add XQuartz.app to allowed applications

# Firewall blocking X11 connections
# System Preferences → Security & Privacy → Firewall → Firewall Options
# Allow XQuartz to accept incoming connections
```

#### Linux-Specific Issues

```bash
# X11 authentication failed
xauth generate :0 . trusted

# Wrong X11 display
export DISPLAY=:0.0
ssh -X sec01

# Wayland interference
export GDK_BACKEND=x11
export QT_QPA_PLATFORM=xcb
```

### Diagnostic Commands

```bash
# On local client:
echo $DISPLAY                    # Check display variable
xauth list                       # Check X11 authentication
netstat -tlnp | grep :60         # Check X11 listening ports
ps aux | grep ssh                # Check SSH processes

# On sec01:
echo $DISPLAY                    # Should show localhost:10.0
ss -tlnp | grep :60              # Check X11 forwarding sockets
who                              # Check logged in users with display
```

### Performance Monitoring

```bash
# Monitor X11 traffic
ssh -X -v sec01  # Verbose SSH output

# Monitor network usage
iftop -i eth0    # On sec01
iftop -i en0     # On macOS client

# Monitor X11 server resources
top -p $(pgrep X)  # Linux
ps aux | grep X    # macOS
```

## Security Considerations

### Network Security

```bash
# Use SSH key authentication only
ssh-keygen -t ed25519 -C "sec01-x11-access"
ssh-copy-id -i ~/.ssh/id_ed25519.pub stetter@192.168.1.25

# Disable X11 forwarding for other hosts
Host *
    ForwardX11 no
    ForwardX11Trusted no

Host sec01
    ForwardX11 yes
    ForwardX11Trusted yes
```

### X11 Security

```bash
# Use untrusted X11 forwarding for external networks
ssh -x sec01  # Lowercase 'x' for untrusted

# Limit X11 authentication timeout
ssh -o ForwardX11Timeout=60 sec01

# Clean up X11 authentication after use
xauth remove $DISPLAY
```

### Firewall Configuration

```bash
# On sec01: Restrict X11 to SSH connections only
sudo iptables -A INPUT -p tcp --dport 6000:6063 -m state --state ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 6000:6063 -j DROP

# Save firewall rules
sudo netfilter-persistent save
```

## Tool-Specific Configuration

### Burp Suite Professional

```bash
# Create optimized launcher script
cat > ~/bin/burp-x11.sh << 'EOF'
#!/bin/bash
export DISPLAY=${DISPLAY:-:10.0}
export _JAVA_AWT_WM_NONREPARENTING=1
java -Xmx6g -XX:+UseG1GC -Djava.awt.headless=false \
     -jar /opt/BurpSuitePro/burpsuite_pro.jar &
EOF

chmod +x ~/bin/burp-x11.sh
```

### Wireshark

```bash
# Run with proper permissions
sudo wireshark &

# Or configure non-root capture
sudo usermod -a -G wireshark $USER
# Logout and login again
wireshark &
```

### OWASP ZAP

```bash
# Launch with adequate memory
export ZAP_OPTS="-Xmx4g"
zaproxy &

# Or use direct command
java -Xmx4g -jar /usr/share/zaproxy/zap.jar &
```

### Metasploit Armitage

```bash
# Start required services
sudo systemctl start postgresql
sudo msfdb init

# Launch Armitage
armitage &
```

## Related Documentation

- [sec01 VM Overview](README.md) - VM specifications and quick start
- [Security Tools Reference](security-tools.md) - Detailed tool documentation
- [Troubleshooting Guide](troubleshooting.md) - Additional troubleshooting information
- [Workspace Guide](workspace-guide.md) - Evidence collection workflows