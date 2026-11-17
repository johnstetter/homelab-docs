# Postmortem: nexus boot disk failure and rebuild

- **Date of incident:** Tuesday, November 10, 2026
- **Host:** nexus (Minisforum MS-A2, 192.168.1.12, nexus.rsdn.io)
- **Severity:** High. Primary hypervisor down, so every VM and container (ctr01, dev01, sec01, Docker stacks, the secondary DNS) was offline for several hours.
- **Data loss:** None for VM disks or Proxmox config. Host-level files on the old root disk were not captured (see "What was lost").
- **Status:** Resolved. Open follow-ups are listed at the end.

---

## Summary

After an update, nexus stopped booting and hung with no network. Diagnosis from the recovery console showed the boot NVMe (Kingston 1TB, only about 421 power-on hours) was throwing media errors. The kernel (7.0.14-pve) was initially suspected but was not the cause.

The VM disks lived on a separate ZFS pool (`vm-storage` on a 4TB Samsung 990 EVO Plus) and were never at risk. We backed up the Proxmox cluster database and a few config files from the rescue environment, exported the pool cleanly, replaced the boot disk with a Samsung 970 EVO Plus 1TB reused from the Synology (its unused read-only SSD cache), reinstalled Proxmox VE 9.2-1, re-imported the pool, restored the config, rebuilt the network (including the 10G NFS link to the Synology), and started the VMs. Claude Code then restored access, re-ran the Ansible playbooks, and added a weekly host-config backup.

Along the way two side incidents occurred: LAN DNS broke because Technitium depended on a host that was down, and the Synology storage pool degraded when drive trays were disturbed during the SSD removal.

---

## Timeline (all November 10, 2026, CST)

Times come from nexus logs (`zpool history`, journal) where available; the rest is approximate order.

1. **Failure noticed.** nexus hung during boot after an update and did not answer ping.
2. **Recovery attempts.** Rebooted, then tried recovery/rescue mode, which dropped to an initramfs shell with a frozen systemd (`poweroff -f` was needed to shut down).
3. **Diagnosis.** Journal output showed repeated I/O errors on `nvme1n1`. `lsblk`, `pvs` and `smartctl` confirmed `nvme1n1` (Kingston 1TB, home of the `pve` LVM volume group: root, swap, data thin pool) had media errors. `nvme0n1` (3.6TB, ZFS pool `vm-storage`) was healthy. (Device names are from the old install; they swapped after the rebuild.)
4. **Data secured from the rescue shell (17:28 to 18:15).** Imported `vm-storage` at 17:28 and copied to `/vm-storage/rescue/`: `config.db` (pmxcfs database), `fstab`, `hostname`, `hosts`, `interfaces`, and raw rootfs images of LXCs 501 (mail-bridge) and 502 (ci01). Exported the pool at 18:15 before power-off.
5. **Replacement plan.** Rather than buy a drive, reuse the Samsung 970 EVO Plus 1TB sitting in the Synology DS1621+ as read-only SSD cache. Removed the cache properly through DSM (Storage Manager), then shut the NAS down.
6. **Installer USB.** Downloaded `proxmox-ve_9.2-1.iso`, verified the SHA256, and wrote it to a Samsung 128GB USB stick from the Mac Studio. First `dd` attempt failed because zsh does not expand `~` after `if=`; fixed with a full path.
7. **DNS side incident.** The Mac's browser and apps showed ERR_NAME_NOT_RESOLVED. Cause: DHCP handed out two resolvers, 192.168.1.4 (Technitium primary on the Synology) and 192.168.1.20 (the Technitium secondary on ctr01, dead), and the primary itself forwarded to 192.168.1.20. Fixed UniFi to stop handing out `.20`; the Technitium forwarder change was queued.
8. **Synology incident.** Reaching the M.2 slots required pulling trays. After power-up DSM reported Drive 2 "System Partition Failed" and Drive 5 not seated, and Storage Pool 1 (SHR, 1-drive tolerance) went Degraded. Volume 1 stayed mounted throughout. Drive 5 was reseated, Repair System Partition fixed Drive 2, and a pool repair (about 22 hours) was started for Drive 5.
9. **MS-A2 hardware swap.** Removed the bottom panel. The Kingston was under the finned heatsink; the 990 (vm-storage) was the exposed drive beside it. Installed the 970 in the Kingston's slot. The 990 was left in place; the installer disk picker was used carefully to pick the 970 by model and size. The Kingston was set aside (not RMA'd).
10. **Proxmox install (first boot 21:06).** Booted the installer in Terminal UI mode (no mouse attached). Selected `/dev/nvme0n1` (970 EVO Plus), ext4, hostname `nexus.rsdn.io`, management NIC `nic1`. The first summary screen showed the host IP as 192.168.1.20 (ctr01's address); caught and corrected to 192.168.1.12/24 before installing. Interface name pinning left on.
11. **Restore (21:12 to 21:17).** Imported `vm-storage` at 21:12 (no `zpool upgrade`). At 21:17 stopped `pve-cluster`, saved the fresh DB, copied in the rescued `config.db`, removed stale `-wal`/`-shm` files, restarted, ran `pvecm updatecerts --force`. `qm list` showed ctr01 (100), dev01 (101), sec01 (110) and templates 9000-9003, 9100.
12. **Network rebuild (about 21:20).** Rewrote `/etc/network/interfaces`: `vmbr0` on `nic1` (LAN, VLAN-aware, 192.168.1.12/24), `vmbr1` on `nic2` (SFP+ DAC to the Synology, 10.0.10.1/24, MTU 9000). Verified 10G link, jumbo-frame ping (8972 bytes) and NFS storage `synology` active.
13. **VM start (21:24 to 21:30).** At 21:24 ctr01 refused to start: "USB Mapping invalid", because its passthrough optical drive (413c:9016) was unplugged. The drive was plugged in at 21:26 and ctr01 started. dev01 followed at 21:29 (1 warning), then sec01.
14. **Gaps found, handoff (about 21:35).** The Linux account and SSH keys on nexus were gone, and PVE users and Terraform tokens needed auditing. Work handed to Claude Code (see below).
15. **Access restored (21:36 to 21:37).** Root key login from the Mac refused. dev01's key still worked through the restored `/etc/pve/priv/authorized_keys` and was used to add `ssh-auth-key`. `stetter` recreated by Ansible.
16. **Audit and health checks (21:38).** All PVE users and tokens present and working; all VMs, NFS mounts, GPU and DNS healthy.
17. **Monitoring and logs back (21:40 to 21:42).** node_exporter and Alloy re-installed by Ansible after switching apt to the no-subscription repos. Prometheus scraping nexus and logs reaching Loki again.
18. **Config backup live (21:43).** First run of the new `pve-config-backup` timer job wrote a verified archive to the Synology over 10G.
19. **Docs and MRs (21:45 onward).** Fixes and docs pushed as MRs; follow-up issues filed. vm-platform !96 to !98 merged 21:51 to 21:56.
20. **LXC restore (22:09 to 22:10).** A first `pct restore --force` of 501 and 502 failed at 22:09 and deleted both CT configs (see below). They were restored without `--force` at 22:10 from the 2026-11-08 vzdumps; ci01 (502) started at 22:10.
21. **Backups moved to 10G (22:14).** The PVE `synology` storage was repointed from `syn.rsdn.io` (1G LAN) to 10.0.10.4 (vmbr1 DAC).

---

## Root cause

The Kingston 1TB NVMe boot drive (the stock drive that shipped with the MS-A2) developed media errors after very little use. The update-triggered reboot exposed it. The kernel and Proxmox update were red herrings.

**Contributing factors**

- A single boot disk with no mirror and no host-level backup of `/etc`, user accounts, SSH keys, or locally installed agents.
- No alerting on NVMe SMART attributes (media errors, available spare, percentage used).
- Host-level configuration (users, exporters, log shipping, tokens) not fully captured in code.

---

## What went well

- VM disks were on a separate ZFS pool, so they survived untouched. This design decision paid off.
- The rescue copy of `config.db`, `interfaces` and the other files made the restore fast and mostly mechanical. `config.db` alone brought back every PVE user, API token, ACL, storage definition, backup job, resource mapping and VM/LXC config, so no CI secrets had to be rotated.
- Exporting the pool before power-off meant a clean import with no `-f`.
- Reusing the 970 from the Synology avoided an emergency purchase.
- The installer's disk, IP, and NIC choices were checked against a summary screen before committing, which caught the `.20` typo.
- The NFS link was verified (ping, jumbo ping, `pvesm status`) before starting ctr01, preventing writes into empty mount points.
- Most host-level extras were already in vm-platform's Ansible, so they were re-run rather than rebuilt by hand.

## What went poorly

- Only `config.db` and four small files were saved from the rescue shell. A copy of all of `/etc`, `/root`, `/home`, and crontabs would have avoided the gaps.
- DNS had a hidden dependency: the Technitium primary forwarded to the secondary on a VM hosted by the failed machine, so a hypervisor outage took down LAN name resolution.
- Opening the Synology to reach the M.2 slots while the pool was healthy but unprotected caused a loose-tray degradation. Tray handling on a NAS is risky without a pre-check.
- A VM passthrough device blocked VM start with an unhelpful dependency on physical hardware.
- The installer's `maxvz=0` setting did not take effect, leaving an unneeded 794G thin pool (harmless).
- The LXC rootfs volumes for 501 and 502 lived on the Kingston's `local-lvm`, so those containers were down until restored from vzdump later that evening.
- `pct restore --force` onto CT IDs whose volumes were missing deleted the volume it had just allocated (same name), failed, and removed the CT configs. Nothing was lost, but restore onto a missing volume needs the stale config removed first, not `--force`.

## Where we got lucky

- The Kingston stayed readable enough to copy files from before shutdown.
- The Synology pool stayed Degraded rather than Crashed, and Volume 1 never unmounted.
- The 990 holding all VM disks was not the failing drive.
- dev01's SSH key was still in the restored `/etc/pve/priv/authorized_keys`, which gave a way back in without a console session.

---

## What was lost

Everything that lived only on the old root disk (Kingston `pve` VG) and was not in `config.db`:

- The Linux user account, home directory and SSH `authorized_keys`.
- Locally installed agents and units (node_exporter, Grafana Alloy log shipping, pulse-sensor-proxy), crontabs and scripts.
- Anything under `/etc` other than the five files rescued.
- The rootfs volumes of LXCs 501 and 502 (on `local-lvm`). Raw images were rescued, and vzdump archives from 2026-11-08 exist on the Synology.

The Kingston itself was not erased and has not been RMA'd. It also uses a volume group named `pve`, so it must not be present at boot alongside the new install. Optional recovery plan: install it in the empty NVME_3 slot, boot the Proxmox installer in debug mode, rename its VG, mount read-only, and copy files off. The only things still worth pulling are crontabs, custom units in `/etc/systemd/system`, and anything in `/usr/local`, `/root` or `/home`, to confirm nothing unknown ran there.

---

## Final state

- **Boot disk:** Samsung 970 EVO Plus 1TB, ext4, Proxmox VE 9.2 (pve-manager 9.2.2, kernel 7.0.2-6-pve). Includes a `local-lvm` thin pool (794G) holding the LXC rootfs volumes.
- **VM storage:** ZFS pool `vm-storage` on the Samsung 990 EVO Plus 4TB (unchanged).
- **Names:** NIC names are pinned by MAC in `/usr/local/lib/systemd/network/50-pmx-nic*.link`. `nic1` = enp3s0 (Realtek RJ45, LAN, links at 1G), `nic2` = enp5s0f0np0 (Intel SFP+, 10G DAC to Synology), `nic0` = enp4s0 (Intel RJ45, unused), `nic3` = enp5s0f1np1 (unused SFP+), `nic4` = wlp6s0 (pinned, but no device present under PVE 9.2).
- **Bridges:** `vmbr0` on `nic1` (192.168.1.12/24, gw 192.168.1.1, VLAN-aware); `vmbr1` on `nic2` (10.0.10.1/24, MTU 9000, Synology at 10.0.10.4).
- **Backup copies on nexus:** `/root/config.db.fresh`, `/root/interfaces.fresh`. Rescue files in `/vm-storage/rescue/`.
- **VMs:** ctr01 (100, 192.168.1.20), dev01 (101, 192.168.1.21), sec01 (110, 192.168.1.25), plus templates. LXCs 501 (mail-bridge, stopped, `onboot: 0`) and 502 (ci01, 192.168.1.22, running; GitLab runner not yet installed, #118).
- **Host config backup:** weekly, Sunday 02:30, to `10.0.10.4:/volume1/proxmox-nexus/host-config/nexus/` over the 10G link.
- **vzdump target:** PVE storage `synology` mounts `10.0.10.4:/volume1/proxmox-nexus` over the 10G link (was `syn.rsdn.io` on the 1G LAN).

---

## Work completed by Claude Code after handoff

All changes went through vm-platform's Ansible playbooks where they existed. Repo changes are on branches with MRs; nothing was merged, rebooted, or stopped.

**Access**

- `~/.ssh/config` had no nexus alias; the inventory uses `stetter@192.168.1.12`. The key is `ssh-auth-key` from the macOS Keychain, not the 1Password agent.
- Root key auth from the Mac was refused. dev01's key was still in the restored `/etc/pve/priv/authorized_keys`, so `ssh-auth-key` was added from dev01.
- `create-stetter-user.yml` recreated `stetter` (uid 1000, sudo NOPASSWD, password locked so key-only). `ssh-authorized-keys.yml` applied the repo key list and revoked the retired M1 MacBook key.
- That playbook replaced root's `authorized_keys` symlink into `/etc/pve/priv` with a regular file. The symlink was restored by hand and the playbook fixed with `follow: true` (vm-platform #130, MR !97), tested on nexus with a throwaway key.

**PVE auth audit**

- Users: root@pam, stetter@pam, terraform-prov@pve, prometheus@pve, homeassistant@pve, mcp-user@pve, pulse-monitor@pam, pulse-monitor@pve.
- All 8 API tokens authenticate (HTTP 200) against the local API, including `terraform-prov@pve!terraform-token`. No rotation needed; GitLab CI variables are still valid.
- The TerraformProv role and its ACLs, plus the PCI (GPU) and USB (optical drive) resource mappings, were intact and matched the hardware.

**Health checks**

- ctr01: 64 containers running, none exited, restarting or unhealthy. All 4 NFS mounts from 10.0.10.4 present. GPU visible (driver 550.163).
- dev01 and sec01 up; sec01 has its 5 NFS mounts.
- DNS answering on both 192.168.1.20 and 192.168.1.4, including local `rsdn.io` names.

**Host extras rebuilt**

- The fresh install had the enterprise apt repos enabled with no subscription (401). They were disabled and the `pve-no-subscription` and Ceph `no-subscription` repos added. 214 packages are upgradable but were left alone, since the outage followed an update.
- Re-ran `node-exporter.yml`, `alloy.yml` and `hermes-user.yml`. Prometheus scrapes `nexus-node-exporter` again and nexus logs reach Loki. The PVE exporter runs on ctr01 and was never affected.
- `proxmox-storage.yml` and `proxmox-backup.yml` ran clean in `--check`: their config came back with `config.db`.
- `pulse-sensor-proxy.yml` failed: Pulse v6 no longer ships `install-sensor-proxy.sh`. Filed as #131.

**Host config backup**

- New role `pve_config_backup` (vm-platform #129, MR !96), applied from the branch.
- Archives `/etc/pve`, an online `sqlite3 .backup` of `config.db` (integrity-checked), `/etc/network/interfaces{,.d}`, the NIC pin `.link` files, `/etc/hosts`, `/etc/hostname`, `/etc/fstab` and `/root/.ssh`.
- Writes to `10.0.10.4:/volume1/proxmox-nexus` through a mount unit that is mounted only while the job runs, so the traffic goes over the 10G DAC. Keeps 12 archives and writes a node_exporter textfile metric for alerting.
- The test archive was 40K and its `config.db` passed `PRAGMA integrity_check`.

**LXC restore**

- Restored 501 and 502 to `local-lvm` from the 2026-11-08 vzdumps (both logs show "Finished Backup"). Configs match the pre-restore ones; ci01's description was re-applied.
- The first attempt used `--force` and failed as described under "What went poorly". The configs had been saved to `/root/lxc-50{1,2}.conf.pre-restore` beforehand.
- Started ci01 (its `onboot: 1`), which came up at 192.168.1.22 and resolves DNS. It has no gitlab-runner yet, which matches #118 being open. mail-bridge left stopped.

**vzdump target moved to 10G**

- ctr01's 307G archive on 2026-11-08 wrote at about 109 MB/s, the ceiling of the 1G LAN link, and that traffic shared nic1 with every VM's LAN traffic.
- `pvesm set` refuses to change `server`, so `/etc/pve/storage.cfg` was edited directly (old copy at `/root/storage.cfg.pre-10g`), the share unmounted, and PVE remounted it. Verified `addr=10.0.10.4`, `clientaddr=10.0.10.1`, active and writable.
- It also removes the storage's dependence on DNS. First real run: Sunday 03:00; compare with last week's 48 minutes for ctr01.

**Docs**

- vm-platform `infrastructure-inventory.md` and `progress.md` (MR !98); homelab-docs hardware page and DR runbook (MR !9, with this postmortem).

**Not completed**

- **Technitium forwarders:** Chrome wasn't connected, and the UI and API need the admin password. There is no Pi-hole on .20 (it's the Technitium secondary), so the recommendation is to clear the primary's forwarders and let it resolve itself, or use a public resolver.
- **Synology scrub:** waiting for the pool repair to finish.
- **Pulse temperature agent:** #131.

**Findings along the way**

- The Synology `proxmox-pve-tc1` NFS export allows `109.168.1.11`, a typo for 192.168.1.11.
- The LAN cable is on the Realtek port, which links at 1G. The old install bridged `nic0` (Intel 2.5G), though old and new names may not map to the same ports.
- The Synology share ignores the 0600 mode on backup archives, so anyone with access to the share can read the `/etc/pve/priv` secrets inside them.
- A grep exposed the `prometheus@pve!exporter` token value in a session tool output. It's a read-only, LAN-only token; rotate it optionally.

---

## Action items

| # | Item | Status |
|---|------|--------|
| 1 | Weekly backup of `/etc/pve`, `config.db`, `/etc/network/interfaces`, `/etc/hosts`, `/root/.ssh` to the Synology (systemd timer) | Done, live on nexus (vm-platform !96, awaiting merge) |
| 2 | Capture host-level config in Ansible (user, SSH keys, node_exporter, Alloy, interface config) so a reinstall is one run | Partly done: existing playbooks re-run and fixed. Open: interfaces and apt repos not in Ansible, pulse role broken (#131) |
| 3 | Add NVMe SMART alerting (media errors, available spare, percentage used) to Prometheus/Grafana | Open |
| 4 | Fix Technitium forwarders (not `192.168.1.20`; clear them or use a public resolver) and avoid DHCP handing out a resolver on a single VM host | DHCP fixed; forwarders open |
| 5 | After the Synology pool repair completes, confirm Healthy, then run one data scrub | Open (about 22h after Nov 10 evening) |
| 6 | Decide whether to recover files from the Kingston (VG rename required) or discard it | Open |
| 7 | Document the NIC name map and which port goes where | Done (above, and vm-platform inventory) |
| 8 | Consider a mirrored boot disk or a second Proxmox host with replication for the next hypervisor failure | Optional |
| 9 | For VMs with USB passthrough, consider whether the dependency is worth blocking boot over | Optional |
| 10 | Restore LXC 501 (mail-bridge) and 502 (ci01) from the 2026-11-08 vzdumps; 502 has `onboot: 1` | Done |
| 11 | Point the PVE `synology` storage at 10.0.10.4 so vzdump uses the 10G link | Done |
| 12 | Fix the `proxmox-pve-tc1` NFS export typo (`109.168.1.11`) | Open |
| 13 | Alert on `pve_config_backup_last_success_timestamp_seconds` going stale | Open |

## Lessons

- Keep VM disks off the boot drive. This saved the whole recovery.
- When something dies, copy more than you think you need before powering off, including `/etc`, `/root`, `/home`, and crontabs.
- Do not let LAN DNS depend on the host you may need to rebuild.
- Verify the IP and disk choice on the installer summary screen before pressing Install.
- Avoid physically touching drives in a NAS at the same time as an unrelated outage. If you must, pause writes and expect to reseat trays carefully.
- On Proxmox, `config.db` is most of the host. Back it up off-box on a schedule, not by luck.
