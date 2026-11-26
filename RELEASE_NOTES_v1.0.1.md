# 🚀 v1.0.1 — Clean Windows Setup Installer & SmartScreen Fix

This release introduces an **official Windows Setup Installer (`FileKeeper-Downloader-Setup.exe`)** and moves build generation entirely to GitHub's verified Microsoft Azure runners.

This eliminates the antivirus false positives (such as generic Trojan/heuristic blocks) caused by standalone temporary-extraction bootloaders.

---

### 🌟 What's New in v1.0.1

- 🛡️ **Clean Windows Setup Wizard (`Inno Setup 6`):**
  - Switches from hidden `Temp\_MEI...` extraction to a standard, clean installation folder.
  - Automatically creates Start Menu and Desktop shortcuts.
  - Registers a clean uninstaller in Windows *Settings -> Installed Apps*.

- ☁️ **Verifiable Cloud Build Provenance:**
  - Built directly on **GitHub Actions Azure runners**, providing transparent build logs from public source code.
  - Generates verifiable **SHA-256 checksums** for security audits.

- ⚡ **Zero-Overhead Client-Side Decryption:**
  - Native Python **AES-256-GCM + PBKDF2** decryption for FitGirl PrivateBin pastes (100+ links resolved in `<0.2s`).
  - No bloated Playwright/headless browser requirements.

- 🔄 **JIT Self-Healing Resume Engine:**
  - Automatically regenerates expired download tokens mid-queue and resumes chunked downloads seamlessly with `--continue=true`.

- 🚀 **High-Speed Multi-Threaded Engine:**
  - Embedded `aria2c` multi-connection download engine tuned to prevent Cloudflare `503` rate limits.

---

### 📦 Downloads & Verification

| Asset | Description | Size | Checksum (SHA-256) |
| :--- | :--- | :--- | :--- |
| **`FileKeeper-Downloader-Setup.exe`** | **Recommended** — Full Windows Setup Wizard (Installs shortcuts & app) | ~40 MB | `5C9E7E7069FE38E7EEC4A4C104E2E5F881B557820B107E01C6F623A39D0EDAC3` |
| **`checksums-sha256.txt`** | Cryptographic hash list for file verification | 99 B | `8F8CDCA9835E19B6C584FB0164D26C55A708DF1F9A50FD8F0D5815F94B161E73` |
| **`Source code (zip / tar.gz)`** | Full Python source with `install.bat` 1-click script | — | Verified Git tree |

---

### 📖 Installation Instructions

1. Download **`FileKeeper-Downloader-Setup.exe`** below.
2. Run the installer and follow the setup wizard.
3. Launch **FileKeeper Batch Downloader** from your Desktop or Start Menu!
