<p align="center">
  <img src="assets/banner.png" alt="FileKeeper Batch Downloader Banner" width="100%">
</p>

# FileKeeper Batch Downloader for FitGirl

A desktop tool to download split FileKeeper archives from FitGirl paste pages in one go, without clicking through dozens of ad pages or fighting expired download tokens.

[![Latest Release](https://img.shields.io/github/v/release/codes-of-santhosh/filekeeper-downloader-for-fitgirl?style=flat-square&color=blue)](https://github.com/codes-of-santhosh/filekeeper-downloader-for-fitgirl/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue?style=flat-square)](https://github.com/codes-of-santhosh/filekeeper-downloader-for-fitgirl/releases)

---

## 📹 Demo & Tutorial

<div align="center">
  <video src="https://github.com/user-attachments/assets/YOUR_VIDEO_ID" controls width="100%" poster="assets/banner.png">
    Your browser does not support the video tag.
  </video>
</div>

> *Tip: Watch the demo above to see how to copy the FitGirl paste URL, decrypt all 100+ files instantly, and download them automatically.*

---

## 📥 Installation

Choose whichever method you prefer:

### Method 1: Windows Installer (Recommended)
1. Go to **[Releases](https://github.com/codes-of-santhosh/filekeeper-downloader-for-fitgirl/releases)**.
2. Download **`FileKeeper-Downloader-Setup.exe`**.
3. Run the installer. It installs the app cleanly, adds a Desktop shortcut, and works right away.

### Method 2: Run from Source (Python)
If you already have Python 3.10+ installed:
```bash
git clone https://github.com/codes-of-santhosh/filekeeper-downloader-for-fitgirl.git
cd filekeeper-downloader-for-fitgirl
install.bat
```
`install.bat` installs all dependencies (`PySide6`, `pycryptodome`, `base58`, `aria2p`, `requests`), ensures `aria2c.exe` is present, and creates a desktop shortcut.

---

## 🚀 Step-by-Step Guide

```
[FitGirl Paste URL]  --->  [Fetch Links]  --->  [Pick Folder]  --->  [Start Download]
```

### 1. Copy the Paste URL from FitGirl
On any FitGirl game page using FileKeeper, copy the full paste URL:
```text
https://paste.fitgirl-repacks.site/?14c8d85201f33c3b#Dxx12MDLV7snCqH11LeGWndxunzAhsvJWZ3r6eQybrRn
```
*(Make sure to copy the entire link including the `#...` key at the end — that key is what decrypts the links).*

### 2. Fetch the Links
* Open **FileKeeper Batch Downloader**.
* Paste the link into the URL bar at the top.
* Click **Fetch Links**.
* The app decrypts the paste client-side in under a second and lists all archive parts in the table with their filenames and statuses.

### 3. Select Files and Destination Folder
* Use **Select All**, **Deselect All**, or check individual checkboxes to choose which parts you want.
* Click **Browse** next to *Download Folder* to choose where files will be saved on your hard drive.
* Leave **Concurrent** set to `2` or `3` (recommended to avoid Cloudflare rate limiting).

### 4. Click Start Download
* Click **Start Download**.
* Downloads run in the background with live progress bars, speed metrics, and ETAs.
* You can pause, resume, or cancel at any time.

---

## 🛠️ How It Handles Common Host Issues

- **Expired Links / Dropped Connections:** FileKeeper invalidates direct download tokens after 1–2 hours. When a file queued in a long list hits an expired token or error, the downloader automatically requests a fresh token and resumes the file where it stopped (`--continue=true`).
- **Missing or 404 Parts:** If FileKeeper deletes a single file part on their server, that row will show as failed. You can download that single part from an alternative mirror on FitGirl (like FuckingFast or DataNodes) and drop it into the same download folder — FitGirl split archives are bit-for-bit identical across all hosts.
- **Rate Limits:** To keep your IP from receiving `503 Service Unavailable` bans from Cloudflare, downloads are paced using a concurrent socket limit.

---

## 🧩 Building from Source

To compile the standalone directory or installer yourself:

1. Install requirements:
   ```bash
   pip install -r requirements.txt pyinstaller
   ```
2. Build the app folder:
   ```bash
   pyinstaller --clean filekeeper.spec
   ```
3. Compile the setup installer with Inno Setup:
   ```powershell
   & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
   ```
   The installer executable will be saved in `dist-installer/`.

---

## 📄 License

Distributed under the [MIT License](LICENSE).
