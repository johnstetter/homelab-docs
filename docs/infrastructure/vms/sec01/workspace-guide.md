# Workspace Organization Guide

Best practices for organizing security assessments, managing evidence, and maintaining professional workflows on sec01.

## Workspace Philosophy

### Directory Structure Principles

1. **Standardization**: Consistent structure across all engagements
2. **Traceability**: Clear audit trail from discovery to reporting
3. **Scalability**: Structure that works for small tests and large assessments
4. **Compliance**: Meets evidence handling requirements for professional engagements

### Evidence Integrity

- **Chain of custody**: Documented handling of all evidence
- **Integrity verification**: Checksums for all collected artifacts
- **Secure storage**: Proper encryption and access controls
- **Retention policies**: Clear guidelines for data lifecycle management

## Standard Directory Structure

### Primary Workspace (`~/workspace`)

```
~/workspace/
├── templates/                    # Engagement templates and checklists
│   ├── external-pentest/
│   ├── internal-assessment/
│   ├── web-app-test/
│   └── wireless-audit/
├── tools/                        # Custom scripts and configurations
│   ├── scripts/
│   ├── payloads/
│   └── wordlists/
└── [YYYY-MM-DD]-[CLIENT]-[TYPE]/ # Individual engagement directories
    ├── 00-scope/                 # Scope documentation and authorization
    ├── 01-recon/                 # Reconnaissance findings
    ├── 02-scanning/              # Port scans, vulnerability scans
    ├── 03-exploitation/          # Exploitation attempts and results
    ├── 04-post-exploitation/     # Post-exploitation artifacts
    ├── 05-evidence/              # Screenshots, packet captures, logs
    ├── 06-reporting/             # Draft and final reports
    ├── 07-deliverables/          # Client deliverables
    └── notes.md                  # Running notes and observations
```

### Tool-Specific Directories (`/opt/pentest`)

```
/opt/pentest/
├── burp/                         # Burp Suite configurations
│   ├── projects/
│   ├── extensions/
│   └── configs/
├── metasploit/                   # Metasploit resources
│   ├── modules/
│   ├── payloads/
│   └── loot/
├── wordlists/                    # Custom wordlists
│   ├── subdomains/
│   ├── directories/
│   ├── usernames/
│   └── passwords/
├── payloads/                     # Custom payloads
│   ├── web-shells/
│   ├── reverse-shells/
│   └── privilege-escalation/
└── scripts/                      # Automation scripts
    ├── recon/
    ├── scanning/
    └── post-exploitation/
```

### Evidence Storage (`/mnt/synology/sec01`)

```
/mnt/synology/sec01/
├── archives/                     # Completed engagement archives
│   └── [YYYY]/
│       └── [YYYY-MM-DD]-[CLIENT]-[TYPE].tar.gz.enc
├── active/                       # Current engagement large files
│   ├── [ENGAGEMENT-ID]/
│   │   ├── packet-captures/
│   │   ├── memory-dumps/
│   │   ├── disk-images/
│   │   └── large-datasets/
├── templates/                    # Document templates
│   ├── reports/
│   ├── checklists/
│   └── contracts/
├── wordlists/                    # Large wordlist collections
│   ├── subdomain-enumeration/
│   ├── password-cracking/
│   └── directory-brute-forcing/
└── tools/                        # Tool backups and configurations
    ├── burp-backup/
    ├── metasploit-backup/
    └── vm-snapshots/
```

## Engagement Workflow

### 1. Pre-Engagement Setup

```bash
# Create engagement directory
ENGAGEMENT="2024-12-15-acme-corp-external-pentest"
cd ~/workspace
mkdir -p "$ENGAGEMENT"
cd "$ENGAGEMENT"

# Initialize directory structure
mkdir -p {00-scope,01-recon,02-scanning,03-exploitation,04-post-exploitation,05-evidence,06-reporting,07-deliverables}

# Create engagement notes
cat > notes.md << EOF
# $ENGAGEMENT

## Engagement Details
- **Client**: Acme Corporation
- **Type**: External Penetration Test
- **Scope**: 203.0.113.0/24, acme.com, *.acme.com
- **Start Date**: $(date +%Y-%m-%d)
- **Tester**: Your Name
- **Authorization**: SOW-2024-001

## Objectives
- [ ] Network perimeter assessment
- [ ] Web application security testing
- [ ] Social engineering assessment
- [ ] Wireless security audit

## Timeline
- Day 1-2: Reconnaissance and scanning
- Day 3-4: Vulnerability assessment and exploitation
- Day 5: Post-exploitation and evidence collection
- Day 6-7: Reporting and deliverable preparation

## Notes
EOF

# Copy scope documents
cp /mnt/synology/sec01/templates/scope-template.pdf 00-scope/
cp /mnt/synology/sec01/templates/authorization-letter.pdf 00-scope/
```

### 2. Reconnaissance Phase

```bash
cd 01-recon

# Passive reconnaissance
echo "# Passive Reconnaissance" > README.md
echo "Date: $(date)" >> README.md
echo "" >> README.md

# OSINT gathering
mkdir -p {osint,dns,social-media,public-records}

# DNS reconnaissance
dig acme.com > dns/initial-dns.txt
dnsrecon -d acme.com -t std > dns/dnsrecon-output.txt
fierce -dns acme.com > dns/fierce-output.txt

# Subdomain enumeration
sublist3r -d acme.com -o dns/sublist3r-results.txt
amass enum -d acme.com -o dns/amass-results.txt

# Social media reconnaissance
# Document findings in social-media/README.md

# Certificate transparency
curl -s "https://crt.sh/?q=%.acme.com&output=json" | jq -r '.[].name_value' | sort -u > dns/certificate-transparency.txt

# Archive findings
tar -czf ../05-evidence/01-recon-$(date +%Y%m%d).tar.gz .
```

### 3. Scanning Phase

```bash
cd ../02-scanning

# Create scanning structure
mkdir -p {port-scans,vulnerability-scans,web-scans,ssl-scans}

# Port scanning
echo "# Port Scanning Results" > README.md
nmap -sS -sV -sC -oA port-scans/initial-scan 203.0.113.0/24

# Web application scanning
gobuster dir -u http://acme.com -w /usr/share/wordlists/dirb/big.txt -o web-scans/gobuster-acme.txt

# SSL/TLS scanning
sslscan acme.com > ssl-scans/sslscan-acme.txt
testssl.sh acme.com > ssl-scans/testssl-acme.txt

# Vulnerability scanning
mkdir -p vulnerability-scans/nmap-scripts
nmap --script vuln 203.0.113.0/24 -oA vulnerability-scans/nmap-scripts/vuln-scan

# Archive scanning results
tar -czf ../05-evidence/02-scanning-$(date +%Y%m%d).tar.gz .
```

### 4. Exploitation Phase

```bash
cd ../03-exploitation

# Create exploitation structure
mkdir -p {web-apps,network-services,wireless,social-engineering}

# Document exploitation attempts
echo "# Exploitation Attempts" > README.md
echo "Date: $(date)" >> README.md

# Web application exploitation
cd web-apps
burpsuite &  # GUI tool for manual testing

# SQL injection testing
sqlmap -u "http://acme.com/login.php?id=1" --batch --dbs > sqlmap-results.txt

# Network service exploitation
cd ../network-services
# Use Metasploit for service exploitation
msfconsole -q -x "
workspace -a acme-corp
db_nmap -sS -sV 203.0.113.0/24
hosts
services
exit
"

# Archive exploitation evidence
cd ..
tar -czf ../05-evidence/03-exploitation-$(date +%Y%m%d).tar.gz .
```

### 5. Post-Exploitation

```bash
cd ../04-post-exploitation

# Create post-exploitation structure
mkdir -p {privilege-escalation,lateral-movement,persistence,data-exfiltration}

# Document post-exploitation activities
echo "# Post-Exploitation Activities" > README.md

# Example: Privilege escalation on compromised system
# (This would be done on actual compromised systems)
echo "## Compromised Systems" >> README.md
echo "- 203.0.113.10: Web server (www-data user)" >> README.md
echo "- 203.0.113.20: Database server (postgres user)" >> README.md

# Archive post-exploitation evidence
tar -czf ../05-evidence/04-post-exploitation-$(date +%Y%m%d).tar.gz .
```

### 6. Evidence Collection

```bash
cd ../05-evidence

# Create evidence manifest
cat > evidence-manifest.md << EOF
# Evidence Manifest

## Engagement: $ENGAGEMENT
## Collection Date: $(date)
## Collector: Your Name

| File | Description | Hash (SHA256) | Collection Method |
|------|-------------|---------------|-------------------|
EOF

# Calculate checksums for all evidence
find . -name "*.tar.gz" -type f -exec sha256sum {} \; > checksums.txt

# Take screenshots of key findings
mkdir -p screenshots
# Use screenshot tools to capture evidence

# Create evidence package
EVIDENCE_PACKAGE="${ENGAGEMENT}-evidence-$(date +%Y%m%d)"
mkdir -p "/mnt/synology/sec01/active/$EVIDENCE_PACKAGE"

# Copy evidence to secure storage
cp -r . "/mnt/synology/sec01/active/$EVIDENCE_PACKAGE/"

# Encrypt sensitive evidence
gpg --symmetric --cipher-algo AES256 "/mnt/synology/sec01/active/$EVIDENCE_PACKAGE/checksums.txt"
```

### 7. Reporting

```bash
cd ../06-reporting

# Copy report template
cp /mnt/synology/sec01/templates/reports/pentest-report-template.docx ./

# Create findings summary
cat > findings-summary.md << EOF
# Executive Summary

## Engagement Overview
- **Client**: Acme Corporation
- **Assessment Type**: External Penetration Test
- **Test Dates**: $(date -d '-7 days' +%Y-%m-%d) to $(date +%Y-%m-%d)
- **Tester**: Your Name

## Key Findings
- X critical vulnerabilities identified
- Y high-risk vulnerabilities identified
- Z medium-risk vulnerabilities identified

## Risk Summary
Overall risk rating: HIGH/MEDIUM/LOW

## Recommendations
1. Priority 1: Address critical SQL injection vulnerabilities
2. Priority 2: Implement proper SSL/TLS configuration
3. Priority 3: Strengthen password policies

EOF

# Generate detailed technical findings
# (Use tools like Burp, OWASP ZAP exports, etc.)
```

## Evidence Management

### Chain of Custody

```bash
# Create chain of custody log
cat > chain-of-custody.log << EOF
CHAIN OF CUSTODY LOG
===================

Engagement: $ENGAGEMENT
Evidence Item: [Description]
Collected By: Your Name
Collection Date: $(date)
Collection Method: [Tool/Manual]
Hash Verification: [SHA256 checksum]

Custody Transfers:
- $(date): Collected by Your Name
- $(date): Stored on secure NFS (10.0.10.10:/volume1/sec01)
- $(date): Delivered to client (if applicable)

EOF
```

### Data Integrity

```bash
# Verify evidence integrity
sha256sum -c checksums.txt

# Create integrity verification script
cat > verify-evidence.sh << 'EOF'
#!/bin/bash
echo "Evidence Integrity Verification"
echo "==============================="
echo "Engagement: $1"
echo "Verification Date: $(date)"
echo ""

if sha256sum -c checksums.txt; then
    echo "PASS: All evidence integrity checks passed"
    exit 0
else
    echo "FAIL: Evidence integrity check failed"
    exit 1
fi
EOF

chmod +x verify-evidence.sh
```

### Secure Deletion

```bash
# Secure deletion of temporary files
shred -vfz -n 3 temp-file.txt

# Secure deletion of directories
find /tmp/engagement-temp -type f -exec shred -vfz -n 3 {} \;
rm -rf /tmp/engagement-temp

# Clear bash history of sensitive commands
history -d $((HISTCMD-1))  # Delete last command
unset HISTFILE             # Disable history for session
```

## Automation Scripts

### Engagement Initialization Script

```bash
#!/bin/bash
# ~/workspace/tools/scripts/init-engagement.sh

if [ $# -ne 3 ]; then
    echo "Usage: $0 <YYYY-MM-DD> <client-name> <engagement-type>"
    echo "Example: $0 2024-12-15 acme-corp external-pentest"
    exit 1
fi

DATE=$1
CLIENT=$2
TYPE=$3
ENGAGEMENT="${DATE}-${CLIENT}-${TYPE}"

echo "Initializing engagement: $ENGAGEMENT"

cd ~/workspace
mkdir -p "$ENGAGEMENT"
cd "$ENGAGEMENT"

# Create directory structure
mkdir -p {00-scope,01-recon,02-scanning,03-exploitation,04-post-exploitation,05-evidence,06-reporting,07-deliverables}

# Create notes template
cat > notes.md << EOF
# $ENGAGEMENT

## Engagement Details
- **Client**: ${CLIENT^}
- **Type**: ${TYPE^}
- **Start Date**: $DATE
- **Tester**: $(whoami)

## Scope
- [ ] Define IP ranges
- [ ] Define domain names
- [ ] Define excluded systems
- [ ] Obtain written authorization

## Objectives
- [ ] Objective 1
- [ ] Objective 2
- [ ] Objective 3

## Timeline
- Day 1:
- Day 2:
- Day 3:

## Notes
EOF

# Create evidence manifest
cat > 05-evidence/evidence-manifest.md << EOF
# Evidence Manifest - $ENGAGEMENT

| Date | File | Description | Hash | Notes |
|------|------|-------------|------|-------|
|      |      |             |      |       |
EOF

echo "Engagement directory created: ~/workspace/$ENGAGEMENT"
echo "Next steps:"
echo "1. Review scope documentation"
echo "2. Obtain proper authorization"
echo "3. Begin reconnaissance phase"
```

### Evidence Archival Script

```bash
#!/bin/bash
# ~/workspace/tools/scripts/archive-engagement.sh

if [ $# -ne 1 ]; then
    echo "Usage: $0 <engagement-directory>"
    exit 1
fi

ENGAGEMENT=$1

if [ ! -d "$ENGAGEMENT" ]; then
    echo "Error: Engagement directory $ENGAGEMENT not found"
    exit 1
fi

echo "Archiving engagement: $ENGAGEMENT"

cd "$ENGAGEMENT"

# Generate final checksums
find . -type f -name "*.txt" -o -name "*.log" -o -name "*.pcap" -o -name "*.png" -o -name "*.pdf" | \
    xargs sha256sum > 05-evidence/final-checksums.txt

# Create archive
ARCHIVE_NAME="${ENGAGEMENT}-complete-$(date +%Y%m%d).tar.gz"
cd ..
tar -czf "$ARCHIVE_NAME" "$ENGAGEMENT"

# Encrypt archive
gpg --symmetric --cipher-algo AES256 "$ARCHIVE_NAME"
rm "$ARCHIVE_NAME"

# Move to long-term storage
YEAR=$(echo "$ENGAGEMENT" | cut -d'-' -f1)
mkdir -p "/mnt/synology/sec01/archives/$YEAR"
mv "${ARCHIVE_NAME}.gpg" "/mnt/synology/sec01/archives/$YEAR/"

echo "Engagement archived to: /mnt/synology/sec01/archives/$YEAR/${ARCHIVE_NAME}.gpg"
echo "Archive password required for decryption"
```

## Compliance and Best Practices

### Professional Standards

#### Documentation Requirements

1. **Methodology Documentation**
   - Clear description of testing approach
   - Step-by-step procedures followed
   - Tools and techniques used
   - Rationale for testing decisions

2. **Finding Documentation**
   - Technical details of vulnerabilities
   - Business impact assessment
   - Risk ratings with justification
   - Remediation recommendations

3. **Evidence Documentation**
   - Screenshots of vulnerabilities
   - Tool output and logs
   - Proof-of-concept code
   - Network captures (sanitized)

#### Quality Assurance

```bash
# Create QA checklist
cat > ~/workspace/templates/qa-checklist.md << EOF
# Quality Assurance Checklist

## Pre-Engagement
- [ ] Scope clearly defined and documented
- [ ] Written authorization obtained
- [ ] Testing methodology approved
- [ ] Emergency contact information available

## During Engagement
- [ ] All activities logged with timestamps
- [ ] Evidence collected for each finding
- [ ] Client notified of critical findings
- [ ] No testing outside defined scope

## Post-Engagement
- [ ] All evidence properly collected and archived
- [ ] Chain of custody maintained
- [ ] Findings verified and validated
- [ ] Report reviewed by senior team member
- [ ] Client deliverables prepared and delivered
- [ ] Engagement closure documented

## Data Handling
- [ ] Client data handled according to agreement
- [ ] Evidence stored securely
- [ ] Data retention policy followed
- [ ] Secure disposal procedures implemented
EOF
```

### Legal and Ethical Considerations

#### Authorization Management

```bash
# Store authorization documents
mkdir -p ~/workspace/templates/authorization-templates

# Example authorization checklist
cat > ~/workspace/templates/authorization-templates/authorization-checklist.md << EOF
# Authorization Checklist

## Required Documents
- [ ] Statement of Work (SOW)
- [ ] Signed Testing Agreement
- [ ] Get Out of Jail Free Letter
- [ ] Emergency Contact Information
- [ ] Scope Definition Document

## Verification Steps
- [ ] Confirm client authority to authorize testing
- [ ] Verify all systems in scope are owned/controlled by client
- [ ] Confirm testing window and any restrictions
- [ ] Establish emergency procedures
- [ ] Document any special considerations

## Before Testing Begins
- [ ] All authorization documents signed and stored
- [ ] Testing scope verified with client
- [ ] Emergency contacts confirmed
- [ ] Testing methodology approved
- [ ] Ethical guidelines reviewed
EOF
```

## Performance and Resource Management

### Large Dataset Management

```bash
# Monitor storage usage
df -h ~/workspace
df -h /mnt/synology/sec01

# Clean up temporary files
find ~/workspace -name "*.tmp" -delete
find ~/workspace -name "core.*" -delete

# Compress old datasets
find ~/workspace -name "*.pcap" -mtime +30 -exec gzip {} \;

# Archive completed engagements
for engagement in ~/workspace/20??-??-??-*; do
    if [ -f "$engagement/06-reporting/final-report.pdf" ]; then
        echo "Archiving completed engagement: $engagement"
        ~/workspace/tools/scripts/archive-engagement.sh "$engagement"
    fi
done
```

### Resource Monitoring

```bash
# Monitor tool resource usage
cat > ~/workspace/tools/scripts/monitor-resources.sh << 'EOF'
#!/bin/bash
echo "Resource Usage Monitor"
echo "====================="
echo "Date: $(date)"
echo ""

echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//'

echo ""
echo "Memory Usage:"
free -h

echo ""
echo "Disk Usage:"
df -h | grep -E "(Filesystem|/dev/|/mnt/)"

echo ""
echo "Active Security Tools:"
ps aux | grep -E "(burp|wireshark|metasploit|nmap)" | grep -v grep

echo ""
echo "Network Connections:"
ss -tuln | grep -E "(8080|8090|4444)"
EOF

chmod +x ~/workspace/tools/scripts/monitor-resources.sh
```

## Related Documentation

- [sec01 VM Overview](README.md) - VM setup and specifications
- [X11 Forwarding Guide](x11-forwarding.md) - GUI tool access
- [Security Tools Reference](security-tools.md) - Tool documentation
- [Troubleshooting Guide](troubleshooting.md) - Problem resolution