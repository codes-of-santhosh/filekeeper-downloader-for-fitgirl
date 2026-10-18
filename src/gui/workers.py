from PySide6.QtCore import QThread, Signal
from playwright.sync_api import sync_playwright
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
        try:
            # 1. Ultra-fast native PrivateBin decryption (<0.2s, no browser needed)
            from ..paste_parser import PasteParser
            parser = PasteParser()
            links = parser.get_filekeeper_links(self.url)
            if links:
                self.finished_signal.emit(links)
                return
        except Exception:
            pass

        # 2. Fallback to Playwright if native decrypt encounters unexpected paste format
        try:
            from playwright.sync_api import sync_playwright
            links = []
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                page.goto(self.url, wait_until="networkidle")
                page.wait_for_timeout(4000)
                
                hrefs = page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('a'))
                                .map(a => a.href)
                                .filter(href => href.includes('filekeeper.net') || href.includes('filekeeper.com'));
                }''')
                
                unique_hrefs = list(set(hrefs))
                links = [FileKeeperLink(url=h) for h in unique_hrefs]
                browser.close()
                
            self.finished_signal.emit(links)
        except Exception as e:
            self.error_signal.emit(str(e))


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
