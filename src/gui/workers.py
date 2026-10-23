from PySide6.QtCore import QThread, Signal
import time
import re
import os
import random

from ..models import FileKeeperLink, ResolvedFile

class PasteWorker(QThread):
    finished_signal = Signal(list)
    error_signal = Signal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        # 1. Direct validation check
        if not self.url or not self.url.startswith("http"):
            self.error_signal.emit("Please enter a valid FitGirl paste URL (e.g. https://paste.fitgirl-repacks.site/?id#key)")
            return

        if "?" not in self.url or "#" not in self.url:
            self.error_signal.emit("Invalid FitGirl paste URL format. It must contain '?' and '#<key>' (e.g. https://paste.fitgirl-repacks.site/?id#key)")
            return

        # 2. Ultra-fast native PrivateBin decryption (<0.2s, no browser needed)
        try:
            from ..paste_parser import PasteParser
            parser = PasteParser()
            links = parser.get_filekeeper_links(self.url)
            if links:
                self.finished_signal.emit(links)
                return
            else:
                self.error_signal.emit("No FileKeeper links found in the paste.")
                return
        except Exception as e:
            # If native decryption fails, report the actual decryption error directly
            self.error_signal.emit(f"Failed to decrypt paste: {e}")


class ResolverWorker(QThread):
    progress_signal = Signal(int, int, str)
    file_resolved_signal = Signal(ResolvedFile)
    finished_signal = Signal(list)
    error_signal = Signal(str)
    
    def __init__(self, links):
        super().__init__()
        self.links = links
        self._is_cancelled = False
        
    def cancel(self):
        self._is_cancelled = True
        
    def run(self):
        resolved = []
        import requests
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        try:
            total = len(self.links)
            completed = 0
            
            def resolve_single(link):
                if self._is_cancelled:
                    return None
                    
                filename_match = re.search(r'filekeeper\.[a-z]+/[^/]+/(.+)$', link.url)
                filename = filename_match.group(1) if filename_match else "unknown_file"
                
                match = re.search(r'filekeeper\.[a-z]+/(?P<id>[^/]+)/', link.url)
                if not match:
                    return ResolvedFile(link.url, "", filename, "", "Failed (Invalid URL)")
                    
                file_id = match.group('id')
                data = {
                    'op': 'download2',
                    'id': file_id,
                    'rand': '',
                    'referer': '',
                    'method_free': '',
                    'down_direct': '1'
                }
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                    'Referer': link.url
                }
                
                success = False
                direct_url = ""
                delays = [2, 4, 8]
                
                for attempt in range(4):
                    if self._is_cancelled:
                        break
                        
                    try:
                        resp = requests.post(link.url, data=data, headers=headers, allow_redirects=False, timeout=30)
                        if resp.status_code in [301, 302, 303]:
                            direct_url = resp.headers.get('Location')
                            success = True
                            break
                        elif resp.status_code == 429 or resp.status_code >= 500:
                            if attempt < 3:
                                time.sleep(delays[attempt] + random.uniform(0.1, 1.0))
                            continue
                        else:
                            break # fatal error
                    except Exception:
                        if attempt < 3:
                            time.sleep(delays[attempt] + random.uniform(0.1, 1.0))
                            
                return ResolvedFile(
                    original_url=link.url,
                    direct_url=direct_url if success else "",
                    filename=filename,
                    size="Unknown",
                    status="Ready" if success else "Failed"
                )

            with ThreadPoolExecutor(max_workers=5) as executor:
                # Submit all tasks
                future_to_url = {executor.submit(resolve_single, link): link for link in self.links}
                
                for future in as_completed(future_to_url):
                    if self._is_cancelled:
                        break
                        
                    res = future.result()
                    if res:
                        completed += 1
                        self.progress_signal.emit(completed, total, res.original_url)
                        self.file_resolved_signal.emit(res)
                        resolved.append(res)
                        
            self.finished_signal.emit(resolved)
        except Exception as e:
            self.error_signal.emit(str(e))

class PollerWorker(QThread):
    stats_updated_signal = Signal(dict)
    
    def __init__(self, downloader, active_downloads):
        super().__init__()
        self.downloader = downloader
        self.active_downloads = active_downloads
        self._is_running = True
        
    def stop(self):
        self._is_running = False
        
    def run(self):
        while self._is_running:
            try:
                updates = {}
                if self.active_downloads:
                    for gid, row in list(self.active_downloads.items()):
                        stat = self.downloader.get_progress(gid)
                        if stat:
                            updates[gid] = stat
                self.stats_updated_signal.emit(updates)
            except Exception:
                pass
            time.sleep(0.5)
