# Troubleshooting Guide

Common issues and solutions for sec01 VM, security tools, and X11 forwarding.

## Quick Diagnostics

### System Health Check

```bash
#!/bin/bash
# Quick health check script
echo "SEC01 System Health Check"
echo "========================"
echo "Date: $(date)"
echo ""

# System resources
echo "=== System Resources ==="
echo "Uptime: $(uptime -p)"
echo "Load: $(uptime | awk -F'load average:' '{print $2}')"
echo "Memory: $(free -h | awk 'NR==2{printf "%.1f%%", $3*100/$2}')"
echo "Disk: $(df -h / | awk 'NR==2{print $5}')"
echo ""

# Network connectivity
echo "=== Network Connectivity ==="
ping -c 1 192.168.1.1 > /dev/null && echo "✓ Gateway reachable" || echo "✗ Gateway unreachable"
ping -c 1 8.8.8.8 > /dev/null && echo "✓ Internet reachable" || echo "✗ Internet unreachable"
ping -c 1 10.0.10.10 > /dev/null && echo "✓ NFS server reachable" || echo "✗ NFS server unreachable"
echo ""

# Services
echo "=== Services ==="
systemctl is-active ssh > /dev/null && echo "✓ SSH active" || echo "✗ SSH inactive"
systemctl is-active postgresql > /dev/null && echo "✓ PostgreSQL active" || echo "✗ PostgreSQL inactive"
mount | grep synology > /dev/null && echo "✓ NFS mounted" || echo "✗ NFS not mounted"
echo ""

# X11 forwarding
echo "=== X11 Forwarding ==="
[ -n "$DISPLAY" ] && echo "✓ DISPLAY set: $DISPLAY" || echo "✗ DISPLAY not set"
[ -n "$SSH_CLIENT" ] && echo "✓ SSH connection detected" || echo "✗ No SSH connection"
xauth list | grep -q unix && echo "✓ X11 auth configured" || echo "✗ X11 auth missing"
```

## X11 Forwarding Issues

### Cannot Open Display

**Symptoms:**
```
Error: Can't open display: localhost:10.0
gtk_init: cannot open display: localhost:10.0
```

**Diagnosis:**
```bash
# Check X11 forwarding status
echo $DISPLAY
echo $SSH_CLIENT
xauth list
```

**Solutions:**

=== "Missing DISPLAY Variable"

    ```bash
    # Manual DISPLAY export (temporary fix)
    export DISPLAY=:10.0

    # For persistent fix, check SSH configuration
    ssh -X -v sec01  # Look for X11 forwarding messages
    ```

=== "SSH X11 Forwarding Disabled"

    ```bash
    # On sec01: Check SSH server config
    sudo grep -i x11 /etc/ssh/sshd_config

    # Should show:
    # X11Forwarding yes
    # X11DisplayOffset 10
    # X11UseLocalhost yes

    # If not, edit and restart SSH:
    sudo systemctl restart sshd
    ```

=== "Client X11 Configuration Issue"

    ```bash
    # On macOS: Check XQuartz
    ps aux | grep -i xquartz
    launchctl list | grep xquartz

    # On Linux: Check X server
    ps aux | grep -E "(Xorg|X |Xwayland)"
    echo $XDG_SESSION_TYPE
    ```

### X11 Authentication Failed

**Symptoms:**
```
X11 connection rejected because of wrong authentication.
Invalid MIT-MAGIC-COOKIE-1 key
```

**Solutions:**

```bash
# Regenerate X11 authentication
ssh -X sec01
xauth remove $DISPLAY
xauth generate $DISPLAY . trusted

# Or reconnect SSH session
exit
ssh -X sec01

# For trusted forwarding (local network only)
ssh -Y sec01
```

### Performance Issues

**Symptoms:**
- Slow GUI response
- Choppy graphics
- Tool freezing

**Diagnosis:**
```bash
# Check network latency
ping -c 10 192.168.1.25

# Check X11 traffic
ssh -X -v -v sec01  # Double verbose

# Monitor bandwidth usage
iftop -i eth0
```

**Solutions:**

```bash
# Enable compression
ssh -X -C sec01

# Use trusted forwarding (faster, less secure)
ssh -Y sec01

# Optimize for high-latency connections
export LIBGL_ALWAYS_INDIRECT=1
export QT_X11_NO_MITSHM=1
export _JAVA_AWT_WM_NONREPARENTING=1

# Reduce color depth (if needed)
ssh -X sec01 'DISPLAY=:10.0 xdpyinfo | grep depth'
```

## Security Tool Issues

### Burp Suite Problems

#### Won't Launch

**Symptoms:**
```bash
burpsuite
# Nothing happens or immediate exit
```

**Diagnosis:**
```bash
# Check Java installation
java -version
which java

# Check Burp installation
ls -la /usr/bin/burpsuite
ls -la /opt/BurpSuitePro/

# Check for conflicting processes
ps aux | grep -i burp
```

**Solutions:**

```bash
# Launch with explicit Java path
/usr/lib/jvm/java-11-openjdk-amd64/bin/java -jar /opt/BurpSuitePro/burpsuite_pro.jar &

# Increase memory allocation
java -Xmx6g -jar /opt/BurpSuitePro/burpsuite_pro.jar &

# Clear Burp configuration (backup first!)
mv ~/.BurpSuite ~/.BurpSuite.backup
burpsuite &
```

#### High Memory Usage

**Symptoms:**
- System slowdown
- Out of memory errors
- Tool crashes

**Solutions:**

```bash
# Monitor Burp memory usage
ps aux | grep -i burp

# Optimize JVM settings
cat > ~/bin/burp-optimized.sh << 'EOF'
#!/bin/bash
java -Xmx6g -Xms2g \
     -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=200 \
     -XX:G1HeapRegionSize=16m \
     -Djava.awt.headless=false \
     -jar /opt/BurpSuitePro/burpsuite_pro.jar "$@" &
EOF

chmod +x ~/bin/burp-optimized.sh
```

### Wireshark Issues

#### Permission Denied

**Symptoms:**
```
Couldn't run /usr/bin/dumpcap in child process: Permission denied
```

**Solutions:**

```bash
# Option 1: Run as root (not recommended for regular use)
sudo wireshark &

# Option 2: Add user to wireshark group
sudo usermod -a -G wireshark $USER
# Logout and login again

# Option 3: Set capabilities on dumpcap
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/dumpcap

# Verify permissions
getcap /usr/bin/dumpcap
```

#### No Interfaces Available

**Symptoms:**
- No interfaces shown in Wireshark
- "No capture interfaces found" error

**Diagnosis:**
```bash
# List available interfaces
ip link show
ifconfig -a

# Check interface permissions
ls -la /dev/net/tun
```

**Solutions:**

```bash
# Restart network manager
sudo systemctl restart NetworkManager

# Check for interface issues
sudo dmesg | tail -20

# Manual interface configuration
sudo ip link set eth0 up
```

### Metasploit Issues

#### Database Connection Failed

**Symptoms:**
```
[*] Failed to connect to the database: could not connect to server
```

**Solutions:**

```bash
# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Initialize Metasploit database
sudo msfdb init

# Check database status
sudo msfdb status

# Reinitialize if corrupted
sudo msfdb delete
sudo msfdb init

# Test connection
msfconsole -q -x "db_status; exit"
```

#### Module Load Errors

**Symptoms:**
```
[-] Failed to load module: <module_name>
```

**Solutions:**

```bash
# Update Metasploit
sudo msfupdate

# Reload modules
msfconsole -q -x "reload_all; exit"

# Check module paths
msfconsole -q -x "show module_paths; exit"

# Clear module cache
rm -rf ~/.msf4/module_cache/
```

### Nmap Issues

#### Slow Scanning

**Symptoms:**
- Very slow scan completion
- High scan times

**Diagnosis:**
```bash
# Test network connectivity
ping -c 5 target_host

# Check system load
htop
iostat 1 5
```

**Solutions:**

```bash
# Optimize timing template
nmap -T4 target_host  # Aggressive timing

# Limit scan scope
nmap --top-ports 1000 target_host

# Use multiple scan windows
nmap --min-parallelism 100 --max-parallelism 200 target_host

# Skip DNS resolution
nmap -n target_host

# Reduce retries
nmap --max-retries 1 target_host
```

## Network and Storage Issues

### NFS Mount Problems

#### Mount Fails

**Symptoms:**
```bash
mount.nfs: access denied by server while mounting 10.0.10.10:/volume1/sec01
```

**Diagnosis:**
```bash
# Check NFS server availability
ping 10.0.10.10
telnet 10.0.10.10 2049

# Check NFS client packages
dpkg -l | grep nfs

# Check mount options
cat /proc/mounts | grep nfs
```

**Solutions:**

```bash
# Install NFS client if missing
sudo apt update
sudo apt install nfs-common

# Manual mount with options
sudo mount -t nfs -o vers=4,soft,intr 10.0.10.10:/volume1/sec01 /mnt/synology/sec01

# Add to fstab for permanent mount
echo "10.0.10.10:/volume1/sec01 /mnt/synology/sec01 nfs4 defaults,soft,intr 0 0" | sudo tee -a /etc/fstab

# Test mount
sudo mount -a
df -h /mnt/synology/sec01
```

#### Slow NFS Performance

**Symptoms:**
- Slow file transfers
- High latency for file operations

**Diagnosis:**
```bash
# Test network throughput
iperf3 -c 10.0.10.10

# Check NFS stats
nfsstat -c
nfsstat -m

# Monitor I/O
iotop
```

**Solutions:**

```bash
# Optimize mount options
sudo umount /mnt/synology/sec01
sudo mount -t nfs -o vers=4,rsize=65536,wsize=65536,hard,intr,timeo=600 \
     10.0.10.10:/volume1/sec01 /mnt/synology/sec01

# Update fstab
sudo sed -i 's/defaults,soft,intr/vers=4,rsize=65536,wsize=65536,hard,intr,timeo=600/' /etc/fstab

# Verify improvements
dd if=/dev/zero of=/mnt/synology/sec01/test-file bs=1M count=100
rm /mnt/synology/sec01/test-file
```

### Network Connectivity Issues

#### SSH Connection Drops

**Symptoms:**
- SSH sessions disconnecting
- "Connection reset by peer" errors

**Solutions:**

```bash
# Client-side SSH keepalive
echo "ServerAliveInterval 60" >> ~/.ssh/config
echo "ServerAliveCountMax 3" >> ~/.ssh/config

# Or use command-line options
ssh -o ServerAliveInterval=60 -o ServerAliveCountMax=3 sec01

# Server-side configuration
sudo vim /etc/ssh/sshd_config
# Add:
# ClientAliveInterval 60
# ClientAliveCountMax 3
sudo systemctl restart sshd
```

#### DNS Resolution Issues

**Symptoms:**
- Domain names not resolving
- Slow DNS queries

**Diagnosis:**
```bash
# Test DNS resolution
nslookup google.com
dig google.com
cat /etc/resolv.conf
```

**Solutions:**

```bash
# Use reliable DNS servers
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
echo "nameserver 8.8.4.4" | sudo tee -a /etc/resolv.conf

# Or configure via netplan (Ubuntu)
sudo vim /etc/netplan/50-cloud-init.yaml
# Add nameservers section
sudo netplan apply

# Clear DNS cache
sudo systemctl restart systemd-resolved
```

## System Performance Issues

### High Memory Usage

**Symptoms:**
- System slowdown
- Out of memory errors
- Process killing

**Diagnosis:**
```bash
# Check memory usage
free -h
top
htop

# Identify memory-hungry processes
ps aux --sort=-%mem | head -10

# Check for memory leaks
cat /proc/meminfo
```

**Solutions:**

```bash
# Clear system caches (temporary relief)
sudo sysctl vm.drop_caches=3

# Kill unnecessary processes
pkill -f "process_name"

# Adjust OOM killer behavior
echo 0 | sudo tee /proc/sys/vm/oom_kill_allocating_task

# Add swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### High CPU Usage

**Symptoms:**
- System unresponsiveness
- High load average
- Slow tool execution

**Diagnosis:**
```bash
# Monitor CPU usage
top
htop
iostat 1 5

# Identify CPU-intensive processes
ps aux --sort=-%cpu | head -10

# Check system load
uptime
cat /proc/loadavg
```

**Solutions:**

```bash
# Nice/renice CPU-intensive processes
nice -n 10 nmap -sS target_network
renice 10 -p $(pgrep nmap)

# Limit process CPU usage
cpulimit -l 50 -p $(pgrep burpsuite)

# Kill runaway processes
pkill -f "runaway_process"

# Check for I/O wait issues
iostat -x 1 5
```

### Storage Issues

#### Disk Full

**Symptoms:**
```
No space left on device
```

**Diagnosis:**
```bash
# Check disk usage
df -h
du -sh /home/stetter/*
du -sh /tmp/*

# Find large files
find / -size +100M -ls 2>/dev/null | head -20
```

**Solutions:**

```bash
# Clean up common locations
sudo apt autoremove
sudo apt autoclean
sudo journalctl --vacuum-time=7d

# Clean up user data
rm -rf ~/.cache/*
rm -rf /tmp/*

# Move large files to NFS
mv ~/workspace/large-dataset /mnt/synology/sec01/active/

# Set up log rotation
sudo vim /etc/logrotate.conf
```

## Emergency Procedures

### System Recovery

#### SSH Access Lost

**Emergency Access via Proxmox Console:**

1. Access Proxmox web interface: https://pve-ms-a2.rsdn.io:8006
2. Navigate to sec01 VM
3. Open console (noVNC)
4. Login with local credentials
5. Diagnose SSH issues:

```bash
# Check SSH service
sudo systemctl status sshd
sudo systemctl restart sshd

# Check firewall
sudo ufw status
sudo iptables -L

# Check network configuration
ip addr show
ip route show

# Reset SSH configuration if needed
sudo cp /etc/ssh/sshd_config.backup /etc/ssh/sshd_config
sudo systemctl restart sshd
```

#### System Corruption

**VM Restoration Process:**

```bash
# On Proxmox host
ssh pve-ms-a2

# List available snapshots
qm listsnapshot 125  # sec01 VM ID

# Restore from snapshot
qm rollback 125 snapshot-name --force

# Or restore from backup
vzdump-restore backup-file.tar.lzo 125 --force
```

### Data Recovery

#### Evidence Loss

**Recovery Steps:**

```bash
# Check NFS storage
ls -la /mnt/synology/sec01/active/
ls -la /mnt/synology/sec01/archives/

# Recover from local snapshots
sudo dmsetup ls
sudo lvcreate -L1G -s -n recover-snap /dev/vg/root

# File-level recovery tools
sudo apt install testdisk photorec
sudo testdisk
```

### Incident Response

#### Security Incident

**If compromise suspected:**

1. **Immediate Actions:**
   ```bash
   # Disconnect from network (if safe to do so)
   sudo ip link set eth0 down

   # Preserve evidence
   sudo dd if=/dev/vda of=/mnt/synology/sec01/incident-$(date +%Y%m%d).img

   # Document current state
   ps auxf > /tmp/processes.txt
   netstat -tulpn > /tmp/network.txt
   sudo find / -mtime -1 -ls > /tmp/recent-files.txt
   ```

2. **Contact escalation:**
   - Notify system administrator
   - Document all actions taken
   - Preserve logs and evidence

3. **Recovery planning:**
   - Assess damage scope
   - Plan restoration from clean backups
   - Implement additional security measures

## Monitoring and Alerting

### System Monitoring Script

```bash
#!/bin/bash
# ~/workspace/tools/scripts/system-monitor.sh

ALERT_EMAIL="admin@rsdn.io"
LOG_FILE="/var/log/sec01-monitor.log"

# Check critical resources
check_disk_space() {
    USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $USAGE -gt 85 ]; then
        echo "$(date): ALERT - Disk usage at ${USAGE}%" | tee -a $LOG_FILE
        # Send alert email here if configured
        return 1
    fi
    return 0
}

check_memory() {
    MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ $MEM_USAGE -gt 90 ]; then
        echo "$(date): ALERT - Memory usage at ${MEM_USAGE}%" | tee -a $LOG_FILE
        return 1
    fi
    return 0
}

check_services() {
    for service in ssh postgresql; do
        if ! systemctl is-active --quiet $service; then
            echo "$(date): ALERT - Service $service is not running" | tee -a $LOG_FILE
            return 1
        fi
    done
    return 0
}

# Run checks
echo "$(date): Running system checks" | tee -a $LOG_FILE
check_disk_space
check_memory
check_services

echo "$(date): System check completed" | tee -a $LOG_FILE
```

### Log Analysis

```bash
# Check for common issues in logs
sudo grep -i error /var/log/syslog | tail -20
sudo grep -i failed /var/log/auth.log | tail -20
sudo journalctl -u ssh -f  # Follow SSH service logs

# Monitor X11 forwarding issues
grep -i x11 ~/.xsession-errors
```

## Related Documentation

- [sec01 VM Overview](README.md) - VM specifications and setup
- [X11 Forwarding Setup](x11-forwarding.md) - Detailed X11 configuration
- [Security Tools Reference](security-tools.md) - Tool-specific documentation
- [Workspace Guide](workspace-guide.md) - Evidence handling procedures
- [VM Lifecycle Management](../../runbooks/vm-lifecycle.md) - VM operations