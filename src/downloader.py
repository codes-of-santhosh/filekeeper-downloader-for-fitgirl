import subprocess
import aria2p
import time
import os
import sys
import atexit

class Downloader:
    def __init__(self):
        self.process = None
        self.aria2 = None
        
    def start_aria2(self):
        # Locate aria2c.exe whether running from source or PyInstaller bundle
        aria2_bin = "aria2c"
        if os.name == 'nt':
            candidates = [
                # PyInstaller extraction dir
                os.path.join(getattr(sys, '_MEIPASS', ''), "aria2c.exe"),
                # Executable directory (for onedir or alongside exe)
                os.path.join(os.path.dirname(sys.executable), "aria2c.exe"),
                # Project root when running as script
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "aria2c.exe"),
                # Current working directory
                os.path.join(os.getcwd(), "aria2c.exe"),
                "aria2c.exe"
            ]
            for cand in candidates:
                if cand and os.path.isfile(cand):
                    aria2_bin = cand
                    break
        
        # Spawn aria2c
        cmd = [
            aria2_bin,
            "--enable-rpc",
            "--rpc-listen-all=false",
            "--rpc-listen-port=6800",
            "--max-concurrent-downloads=3",
            "--split=2",
            "--max-connection-per-server=2",
            "--continue=true",
            "--file-allocation=none" # Better for Windows
        ]
        
        # We start it detached
        try:
            # CREATE_NO_WINDOW = 0x08000000
            self.process = subprocess.Popen(
                cmd, 
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(1) # wait for rpc to start
        except FileNotFoundError:
            raise Exception("aria2c not found in PATH! Please install aria2c.")
            
        self.aria2 = aria2p.API(
            aria2p.Client(
                host="http://localhost",
                port=6800,
                secret=""
            )
        )
        atexit.register(self.stop_aria2)
        
    def add_download(self, url: str, out_dir: str, filename: str, referer: str = None) -> str:
        headers = [
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        ]
        if referer:
            headers.append(f"Referer: {referer}")
            
        options = {
            "dir": out_dir,
            "out": filename,
            "header": headers
        }
        download = self.aria2.add(url, options=options)
        return download[0].gid
        
    def get_progress(self, gid: str):
        try:
            download = self.aria2.get_download(gid)
            return {
                "completed": download.completed_length,
                "total": download.total_length,
                "speed": download.download_speed,
                "eta": download.eta.seconds if download.eta else 0,
                "status": download.status
            }
        except Exception:
            return None
            
    def set_global_options(self, max_concurrent: int, speed_limit_bytes: int):
        options = {
            "max-concurrent-downloads": str(max_concurrent)
        }
        if speed_limit_bytes > 0:
            options["max-overall-download-limit"] = str(speed_limit_bytes)
        else:
            options["max-overall-download-limit"] = "0"
            
        self.aria2.set_global_options(options)

    def pause_all(self):
        self.aria2.pause_all()

    def resume_all(self):
        self.aria2.resume_all()

    def cancel_all(self):
        for d in self.aria2.get_downloads():
            d.remove(force=True)

    def stop_aria2(self):
        if self.process:
            self.process.kill()
            self.process = None
