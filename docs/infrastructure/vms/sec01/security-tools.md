# Security Tools Reference

Comprehensive reference for security tools available on sec01 VM, including installation, configuration, and usage examples.

## Tool Categories

### 🌐 Network Discovery & Scanning
- [Nmap](#nmap) - Network discovery and port scanning
- [Masscan](#masscan) - High-speed port scanner
- [Zmap](#zmap) - Internet-wide network scanner
- [Unicornscan](#unicornscan) - Asynchronous network scanner

### 🔍 Web Application Testing
- [Burp Suite Professional](#burp-suite-professional) - Comprehensive web app security
- [OWASP ZAP](#owasp-zap) - Web application security scanner
- [Gobuster](#gobuster) - Directory/file brute-forcer
- [FFuF](#ffuf) - Fast web fuzzer
- [SQLMap](#sqlmap) - SQL injection tool
- [Nikto](#nikto) - Web server scanner

### 🎯 Exploitation & Post-Exploitation
- [Metasploit Framework](#metasploit-framework) - Exploitation framework
- [SearchSploit](#searchsploit) - Exploit database search
- [Social Engineer Toolkit](#social-engineer-toolkit) - Social engineering attacks

### 📡 Wireless Security
- [Aircrack-ng](#aircrack-ng) - Wireless security auditing
- [Reaver](#reaver) - WPS brute-force attack
- [Hostapd](#hostapd) - Wireless access point daemon
- [Dnsmasq](#dnsmasq) - DHCP and DNS server

### 🕵️ Network Analysis
- [Wireshark](#wireshark) - Network protocol analyzer
- [Ettercap](#ettercap) - Network interceptor/sniffer
- [Tcpdump](#tcpdump) - Command-line packet analyzer
- [Netcat](#netcat) - Network Swiss Army knife

### 🔬 Forensics & Analysis
- [Autopsy](#autopsy) - Digital forensics platform
- [Volatility](#volatility) - Memory forensics framework
- [Binwalk](#binwalk) - Binary analysis tool
- [Foremost](#foremost) - File recovery tool

### 🛡️ Vulnerability Scanning
- [Greenbone/OpenVAS](#greenbone-openvas) - Vulnerability scanner
- [Nessus](#nessus) - Commercial vulnerability scanner

---

## Network Discovery & Scanning

### Nmap

**Purpose**: Network discovery and security auditing

**Installation**: Pre-installed with Kali Linux

```bash
# Basic host discovery
nmap -sn 192.168.1.0/24

# Comprehensive scan
nmap -sS -sV -sC -O -A target.example.com

# Stealth scan
nmap -sS -f -T2 --source-port 53 target.example.com

# Script scanning
nmap --script vuln target.example.com
nmap --script=smb-enum-shares target.example.com

# Output formats
nmap -oA scan-results target.example.com  # All formats
nmap -oN scan.txt target.example.com      # Normal format
nmap -oX scan.xml target.example.com      # XML format
```

**Configuration Files**:
- Custom scripts: `/usr/share/nmap/scripts/`
- NSE script database: `nmap --script-updatedb`

**X11 Tools**:
- `zenmap` - Graphical frontend for Nmap

```bash
# Launch Zenmap (requires X11 forwarding)
zenmap &
```

### Masscan

**Purpose**: High-speed port scanner for large networks

```bash
# Scan entire internet for web servers (be careful!)
sudo masscan 0.0.0.0/0 -p80,443 --rate=1000

# Scan specific network
sudo masscan 192.168.1.0/24 -p1-65535 --rate=1000

# Output to file
sudo masscan 192.168.1.0/24 -p80,443,8080,8443 --rate=1000 -oG masscan.txt
```

### Zmap

**Purpose**: Internet-wide network scanning

```bash
# Scan for HTTP servers
sudo zmap -p 80 -o http-servers.txt

# Scan with specific source port
sudo zmap -p 443 -s 53 -o https-servers.txt

# Rate-limited scan
sudo zmap -p 22 -r 100 -o ssh-servers.txt
```

### Unicornscan

**Purpose**: Asynchronous network scanner

```bash
# TCP connect scan
unicornscan -mT 192.168.1.1-254:1-1000

# UDP scan
unicornscan -mU 192.168.1.1-254:53,67,68,137,138,161,162

# Comprehensive scan with timing
unicornscan -mT -r300 192.168.1.0/24:a
```

---

## Web Application Testing

### Burp Suite Professional

**Purpose**: Comprehensive web application security testing platform

**Launch**:
```bash
# Standard launch (requires X11 forwarding)
burpsuite &

# Launch with specific memory allocation
java -Xmx6g -jar /opt/BurpSuitePro/burpsuite_pro.jar &

# Launch with custom JVM options
java -Xmx6g -XX:+UseG1GC -Djava.awt.headless=false \
     -jar /opt/BurpSuitePro/burpsuite_pro.jar &
```

**Configuration**:
```bash
# Project files location
mkdir -p ~/workspace/burp-projects

# Custom extensions directory
mkdir -p ~/.BurpSuite/extensions

# Certificate for HTTPS interception
# Export Burp's CA certificate from http://burp/cert
```

**Common Workflows**:

1. **Proxy Setup**:
   - Configure browser to use 127.0.0.1:8080
   - Install Burp CA certificate
   - Enable invisible proxying for non-proxy-aware clients

2. **Active Scanning**:
   - Spider application to discover content
   - Configure scan settings (crawl depth, forms handling)
   - Run active scan on discovered content

3. **Manual Testing**:
   - Use Repeater for request modification
   - Use Intruder for automated attacks
   - Use Extensions (SQLMap, J2EE Scan, etc.)

### OWASP ZAP

**Purpose**: Web application security scanner

**Launch**:
```bash
# Standard launch
zaproxy &

# Launch with specific memory
export ZAP_OPTS="-Xmx4g"
zaproxy &

# Headless mode
zap.sh -daemon -port 8090 -config api.disablekey=true
```

**API Usage**:
```bash
# Start ZAP daemon
zap.sh -daemon -port 8090 &

# Spider a target
curl "http://127.0.0.1:8090/JSON/spider/action/scan/?url=http://target.com"

# Active scan
curl "http://127.0.0.1:8090/JSON/ascan/action/scan/?url=http://target.com"

# Generate report
curl "http://127.0.0.1:8090/OTHER/core/other/htmlreport/" > report.html
```

### Gobuster

**Purpose**: Directory/file/subdomain brute-forcer

```bash
# Directory brute-forcing
gobuster dir -u http://target.com -w /usr/share/wordlists/dirb/big.txt

# File extension brute-forcing
gobuster dir -u http://target.com -w /usr/share/wordlists/dirb/common.txt -x php,html,js

# Subdomain enumeration
gobuster dns -d target.com -w /usr/share/wordlists/subdomains-top1million-5000.txt

# Virtual host discovery
gobuster vhost -u http://target.com -w /usr/share/wordlists/subdomains-top1million-5000.txt

# Custom options
gobuster dir -u http://target.com \
             -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
             -x php,html,txt \
             -t 50 \
             -q \
             -o gobuster-results.txt
```

### FFuF

**Purpose**: Fast web fuzzer

```bash
# Directory fuzzing
ffuf -w /usr/share/wordlists/dirb/big.txt -u http://target.com/FUZZ

# Parameter fuzzing
ffuf -w /usr/share/wordlists/parameters.txt -u http://target.com/page?FUZZ=test

# Subdomain fuzzing
ffuf -w /usr/share/wordlists/subdomains.txt -u http://FUZZ.target.com

# POST data fuzzing
ffuf -w /usr/share/wordlists/parameters.txt -u http://target.com/login \
     -X POST -d "username=admin&password=FUZZ" -H "Content-Type: application/x-www-form-urlencoded"

# Filter responses
ffuf -w wordlist.txt -u http://target.com/FUZZ -fs 4242  # Filter by size
ffuf -w wordlist.txt -u http://target.com/FUZZ -fc 404   # Filter by status code
```

### SQLMap

**Purpose**: Automated SQL injection exploitation

```bash
# Basic SQL injection test
sqlmap -u "http://target.com/page?id=1"

# Test with POST data
sqlmap -u "http://target.com/login" --data="username=test&password=test"

# Test with cookies
sqlmap -u "http://target.com/page" --cookie="PHPSESSID=abc123"

# Dump database
sqlmap -u "http://target.com/page?id=1" --dbs
sqlmap -u "http://target.com/page?id=1" -D database_name --tables
sqlmap -u "http://target.com/page?id=1" -D database_name -T table_name --columns
sqlmap -u "http://target.com/page?id=1" -D database_name -T table_name -C column_name --dump

# Advanced options
sqlmap -u "http://target.com/page?id=1" \
       --level 5 \
       --risk 3 \
       --random-agent \
       --threads 5 \
       --batch
```

### Nikto

**Purpose**: Web server scanner

```bash
# Basic scan
nikto -h http://target.com

# Scan with specific port
nikto -h target.com -p 8080

# Scan with authentication
nikto -h http://target.com -id username:password

# Save results
nikto -h http://target.com -o nikto-results.txt -Format txt

# Comprehensive scan
nikto -h http://target.com \
      -Tuning 1,2,3,4,5,6,7,8,9,0,a,b,c \
      -timeout 10 \
      -Display 1,2,3,4,E,V
```

---

## Exploitation & Post-Exploitation

### Metasploit Framework

**Purpose**: Exploitation framework

**Setup**:
```bash
# Initialize database
sudo systemctl start postgresql
sudo msfdb init

# Update Metasploit
sudo msfupdate

# Start msfconsole
msfconsole
```

**Basic Usage**:
```bash
# Search for exploits
msf6 > search type:exploit platform:linux ssh

# Use an exploit
msf6 > use exploit/unix/ssh/ssh_login
msf6 exploit(unix/ssh/ssh_login) > show options
msf6 exploit(unix/ssh/ssh_login) > set RHOSTS 192.168.1.0/24
msf6 exploit(unix/ssh/ssh_login) > set USERNAME_FILE /usr/share/metasploit-framework/data/wordlists/unix_users.txt
msf6 exploit(unix/ssh/ssh_login) > run

# Post-exploitation
meterpreter > sysinfo
meterpreter > getuid
meterpreter > shell
```

**Armitage GUI**:
```bash
# Start required services
sudo systemctl start postgresql
sudo msfdb init

# Launch Armitage (requires X11 forwarding)
armitage &
```

### SearchSploit

**Purpose**: Local search tool for Exploit Database

```bash
# Search for exploits
searchsploit apache 2.4
searchsploit windows smb
searchsploit -w drupal  # Include URLs

# Copy exploit to current directory
searchsploit -m 16051.rb

# Update database
searchsploit -u
```

### Social Engineer Toolkit

**Purpose**: Social engineering attack platform

```bash
# Launch SET
sudo setoolkit

# Common attack vectors:
# 1) Social-Engineering Attacks
# 2) Website Attack Vectors
# 3) Infectious Media Generator
# 4) Create a Payload and Listener
# 5) Mass Mailer Attack
```

---

## Wireless Security

### Aircrack-ng

**Purpose**: Wireless security auditing suite

**Monitor Mode Setup**:
```bash
# Check wireless interfaces
iwconfig

# Enable monitor mode
sudo airmon-ng start wlan0

# Verify monitor mode
iwconfig wlan0mon
```

**Network Discovery**:
```bash
# Scan for wireless networks
sudo airodump-ng wlan0mon

# Target specific network
sudo airodump-ng -c 6 -w capture --bssid AA:BB:CC:DD:EE:FF wlan0mon
```

**WEP Cracking**:
```bash
# Capture WEP traffic
sudo airodump-ng -c 6 -w wep-capture --bssid AA:BB:CC:DD:EE:FF wlan0mon

# Generate traffic (if needed)
sudo aireplay-ng -3 -b AA:BB:CC:DD:EE:FF wlan0mon

# Crack WEP key
aircrack-ng wep-capture*.cap
```

**WPA/WPA2 Cracking**:
```bash
# Capture handshake
sudo airodump-ng -c 6 -w wpa-capture --bssid AA:BB:CC:DD:EE:FF wlan0mon

# Deauth clients to force reconnection
sudo aireplay-ng -0 1 -a AA:BB:CC:DD:EE:FF -c CLIENT:MAC:HERE wlan0mon

# Crack with dictionary
aircrack-ng -w /usr/share/wordlists/rockyou.txt wpa-capture*.cap

# Crack with hashcat (GPU acceleration)
hcxpcaptool -o hash.hc22000 wpa-capture.cap
hashcat -m 22000 hash.hc22000 /usr/share/wordlists/rockyou.txt
```

### Reaver

**Purpose**: WPS brute-force attack tool

```bash
# Scan for WPS-enabled networks
wash -i wlan0mon

# Attack WPS PIN
sudo reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -vv -S

# Pixie dust attack
sudo reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -vv -K
```

### Hostapd & Dnsmasq

**Purpose**: Create rogue access points

**Configuration Files**:
```bash
# /etc/hostapd/hostapd.conf
interface=wlan0
driver=nl80211
ssid=FreeWiFi
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=YourPassphrase
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP

# /etc/dnsmasq.conf
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.30,255.255.255.0,24h
```

**Launch Rogue AP**:
```bash
# Configure interface
sudo ifconfig wlan0 192.168.4.1/24

# Start services
sudo hostapd /etc/hostapd/hostapd.conf &
sudo dnsmasq -C /etc/dnsmasq.conf -d &

# Enable IP forwarding
sudo echo 1 > /proc/sys/net/ipv4/ip_forward

# Set up iptables rules
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
```

---

## Network Analysis

### Wireshark

**Purpose**: Network protocol analyzer

**Launch**:
```bash
# Launch with GUI (requires X11 forwarding)
sudo wireshark &

# Command-line version
sudo tshark -i eth0 -w capture.pcap

# Capture with filters
sudo tshark -i eth0 -f "tcp port 80" -w http-traffic.pcap
```

**Common Filters**:
- `tcp.port == 80` - HTTP traffic
- `tcp.port == 443` - HTTPS traffic
- `dns` - DNS queries
- `icmp` - ICMP packets
- `arp` - ARP requests/responses
- `ip.addr == 192.168.1.1` - Traffic to/from specific IP

**Analysis Commands**:
```bash
# View capture file info
capinfos capture.pcap

# Split large capture files
editcap -c 1000 large-capture.pcap split-capture.pcap

# Merge capture files
mergecap -w merged.pcap file1.pcap file2.pcap

# Extract objects from HTTP traffic
tshark -r capture.pcap --export-objects http,extracted-files/
```

### Ettercap

**Purpose**: Network interceptor for man-in-the-middle attacks

**GUI Version**:
```bash
# Launch GUI (requires X11 forwarding)
sudo ettercap -G
```

**Command Line Usage**:
```bash
# ARP poisoning
sudo ettercap -T -M arp:remote /192.168.1.1// /192.168.1.100//

# DNS spoofing
# Edit /etc/ettercap/etter.dns first
sudo ettercap -T -M arp:remote -P dns_spoof /192.168.1.1// /192.168.1.0/24//

# SSL strip attack
sudo ettercap -T -M arp:remote -P sslstrip /192.168.1.1// /192.168.1.0/24//
```

### Tcpdump

**Purpose**: Command-line packet analyzer

```bash
# Capture all traffic on interface
sudo tcpdump -i eth0

# Capture to file
sudo tcpdump -i eth0 -w capture.pcap

# Capture with filters
sudo tcpdump -i eth0 host 192.168.1.1
sudo tcpdump -i eth0 port 80
sudo tcpdump -i eth0 'tcp port 80 and host 192.168.1.1'

# Read from file
tcpdump -r capture.pcap

# Advanced options
sudo tcpdump -i eth0 -nn -v -c 100 -s 0 'tcp port 80'
```

---

## Forensics & Analysis

### Autopsy

**Purpose**: Digital forensics platform

**Launch**:
```bash
# Start Autopsy (requires X11 forwarding)
autopsy &

# Access via web interface (alternative)
autopsy --help
```

**Case Management**:
1. Create new case
2. Add data source (disk image, directory)
3. Configure ingest modules
4. Analyze results
5. Generate reports

### Volatility

**Purpose**: Memory forensics framework

```bash
# Analyze memory dump
vol.py -f memory-dump.raw imageinfo

# List processes
vol.py -f memory-dump.raw --profile=Win7SP1x64 pslist

# Dump process memory
vol.py -f memory-dump.raw --profile=Win7SP1x64 procdump -p 1234 --dump-dir=./

# Network connections
vol.py -f memory-dump.raw --profile=Win7SP1x64 netscan

# Registry analysis
vol.py -f memory-dump.raw --profile=Win7SP1x64 printkey -K "Software\Microsoft\Windows\CurrentVersion\Run"

# Timeline analysis
vol.py -f memory-dump.raw --profile=Win7SP1x64 timeliner --output-file=timeline.csv
```

### Binwalk

**Purpose**: Binary analysis tool

```bash
# Basic analysis
binwalk firmware.bin

# Extract embedded files
binwalk -e firmware.bin

# Entropy analysis
binwalk -E firmware.bin

# Signature scan
binwalk -B firmware.bin

# Custom signature file
binwalk -f custom.magic firmware.bin
```

### Foremost

**Purpose**: File recovery tool

```bash
# Recover files from disk image
foremost -i disk-image.dd -o recovered-files/

# Specific file types only
foremost -t jpg,png,pdf -i disk-image.dd -o recovered-files/

# Configuration file customization
# Edit /etc/foremost.conf for custom file signatures
```

---

## Vulnerability Scanning

### Greenbone/OpenVAS

**Purpose**: Comprehensive vulnerability scanner

**Setup**:
```bash
# Install and setup (if not already configured)
sudo gvm-setup
sudo gvm-start

# Create admin user
sudo runuser -u _gvm -- gvmd --create-user=admin --password=admin

# Update vulnerability feeds
sudo runuser -u _gvm -- greenbone-feed-sync
```

**Access**:
```bash
# Web interface via SSH tunnel
ssh -L 9392:127.0.0.1:9392 sec01

# Then open: https://127.0.0.1:9392 in local browser
```

### Nessus

**Purpose**: Commercial vulnerability scanner

**Setup** (if licensed):
```bash
# Download and install Nessus
# Visit https://www.tenable.com/downloads/nessus

# Start Nessus service
sudo systemctl start nessusd
sudo systemctl enable nessusd

# Access via SSH tunnel
ssh -L 8834:127.0.0.1:8834 sec01

# Then open: https://127.0.0.1:8834 in local browser
```

---

## Tool Management

### Custom Tool Installation

```bash
# Create tools directory
mkdir -p /opt/custom-tools
cd /opt/custom-tools

# Example: Install custom tool
git clone https://github.com/author/security-tool.git
cd security-tool
chmod +x install.sh
sudo ./install.sh
```

### Version Management

```bash
# Update Kali repositories
sudo apt update && sudo apt upgrade

# Update specific tools
sudo apt install --only-upgrade metasploit-framework
sudo msfupdate

# Update wordlists
sudo apt install --only-upgrade wordlists
```

### Performance Monitoring

```bash
# Monitor tool resource usage
htop
iotop
nethogs

# Check memory usage by tool
ps aux | grep -E "(burp|wireshark|metasploit)"

# Monitor network usage during scans
iftop -i eth0
```

## Related Documentation

- [sec01 VM Overview](README.md) - VM specifications and setup
- [X11 Forwarding Guide](x11-forwarding.md) - GUI tool access setup
- [Workspace Guide](workspace-guide.md) - Evidence handling and workflows
- [Troubleshooting Guide](troubleshooting.md) - Common issues and solutions