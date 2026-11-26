<div align="center">

<img src="assets/banner.png" alt="FileKeeper Batch Downloader" width="100%">

# FileKeeper Batch Downloader

**One-click batch downloader for FitGirl FileKeeper game repacks.**  
No ad redirects, no clicking 100 links by hand, and no failed downloads from expired tokens.

[![Latest Release](https://img.shields.io/github/v/release/codes-of-santhosh/filekeeper-downloader-for-fitgirl?style=flat-square&color=blue)](https://github.com/codes-of-santhosh/filekeeper-downloader-for-fitgirl/releases)
[![Windows 10 / 11](https://img.shields.io/badge/Windows-10%20%7C%2011-0078D6?style=flat-square&logo=windows&logoColor=white)](https://github.com/codes-of-santhosh/filekeeper-downloader-for-fitgirl/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[**Download Windows Installer (.exe)**](https://github.com/codes-of-santhosh/filekeeper-downloader-for-fitgirl/releases/latest)

</div>

---

## 🎬 30-Second Tutorial

Watch how to paste the link, decrypt all parts in 1 second, and start downloading:

https://github.com/codes-of-santhosh/filekeeper-downloader-for-fitgirl/releases/download/v1.0.1/demo-tutorial.mp4

---

## ⚡ Quick Start

### 1. Download
Grab **`FileKeeper-Downloader-Setup.exe`** from the **[Releases Page](https://github.com/codes-of-santhosh/filekeeper-downloader-for-fitgirl/releases/latest)** and run the installer.

### 2. Copy the Paste Link
On any FitGirl game page, open the FileKeeper paste link and copy the full URL from your browser address bar:
```text
https://paste.fitgirl-repacks.site/?14c8d85201f33c3b#Dxx12MDLV7snCqH11LeGWndxunzAhsvJWZ3r6eQybrRn
```
*(Make sure to copy the entire link including the `#...` key at the end — that key is what decrypts the file list).*

### 3. Fetch & Download
1. Paste the link into the app and click **Fetch Links**.
2. Click **Browse** to choose where to save the files.
3. Click **Start Download**.

---

## ✨ Features That Matter

- **Instant Decryption:** Decrypts FitGirl paste links (AES-256-GCM) in under 0.2 seconds.
- **Auto-Resume Expired Links:** FileKeeper download tokens expire after 1–2 hours. The app automatically requests a fresh token and resumes where it left off without losing downloaded progress.
- **Cloudflare Safe:** Limits concurrent connections to avoid `503 Service Unavailable` bans from file hosters.
- **Portable & Clean:** Uses a standard Windows setup installer with clean start menu shortcuts and an uninstaller.

---

## 🛠️ Run from Source (Optional)

If you have Python 3.10+ installed and prefer running from terminal:

```bash
git clone https://github.com/codes-of-santhosh/filekeeper-downloader-for-fitgirl.git
cd filekeeper-downloader-for-fitgirl
install.bat
```

Or run manually:
```bash
pip install -r requirements.txt
python main.py
```

---

## ❓ FAQ

**Q: Why did one file fail with "404 Not Found"?**  
A: FileKeeper occasionally loses a specific part during server maintenance. Download that single missing part from an alternative mirror on FitGirl (like FuckingFast or DataNodes) and place it into the same folder. FitGirl archives are identical across all hosts.

**Q: What is the recommended concurrent downloads setting?**  
A: Keep it at **2 or 3**. Setting it higher can trigger temporary IP blocks from FileKeeper's Cloudflare shield.

---

## 📄 License

Distributed under the [MIT License](LICENSE).
