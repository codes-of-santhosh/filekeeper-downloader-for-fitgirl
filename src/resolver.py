import re
import httpx
import asyncio
import random
from typing import Optional
from .models import FileKeeperLink, ResolvedFile

class LinkResolver:
    def __init__(self):
        # Use a persistent HTTPX client for connection pooling
        self.client = httpx.AsyncClient(timeout=15.0)
        
    async def resolve_links(self, links: list[FileKeeperLink], progress_callback=None) -> list[ResolvedFile]:
        resolved = []
        for i, link in enumerate(links):
            if progress_callback:
                progress_callback(i, len(links), link.url)
                
            if i > 0:
                await asyncio.sleep(random.uniform(0.5, 1.5))
                
            res_file = await self.resolve_single_with_backoff(link.url)
            if res_file:
                resolved.append(res_file)
                
        return resolved

    async def resolve_single_with_backoff(self, url: str, max_retries=3) -> Optional[ResolvedFile]:
        match = re.search(r'filekeeper\.[a-z]+/(?P<id>[^/]+)/', url)
        if not match:
            return ResolvedFile(url, "", "", "", "Failed (Invalid URL)")
            
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
            'Referer': url
        }
        
        base_delay = 2
        for attempt in range(max_retries):
            try:
                # We need the direct link and also let's try to extract filename/size from the page first
                # Actually, wait, the GET request first to get filename/size is good!
                # Or we can just do the POST request which gives us the redirect, and the redirect URL usually contains the filename!
                # FileKeeper URLs typically look like: /u6m0tranbenr/RE4_Gold_--_fitgirl-repacks.site_--_.part083.rar
                # We can extract the filename from the original URL!
                filename_match = re.search(r'filekeeper\.[a-z]+/[^/]+/(.+)$', url)
                filename = filename_match.group(1) if filename_match else "unknown_file"
                
                response = await self.client.post(url, data=data, headers=headers, follow_redirects=False)
                
                if response.status_code in [301, 302, 303]:
                    direct_url = response.headers.get('Location')
                    return ResolvedFile(
                        original_url=url,
                        direct_url=direct_url,
                        filename=filename,
                        size="Unknown", # Will be fetched by aria2
                        status="Ready"
                    )
                elif response.status_code == 429 or response.status_code >= 500:
                    pass # rate limited, let it retry
                else:
                    return ResolvedFile(url, "", filename, "", f"Failed (HTTP {response.status_code})")
                    
            except Exception as e:
                pass # network error, let it retry
                
            if attempt < max_retries - 1:
                delay = (base_delay ** attempt) + random.uniform(0.1, 1.5)
                await asyncio.sleep(delay)
                
        return ResolvedFile(url, "", "", "", "Failed (Max retries)")

    async def close(self):
        await self.client.aclose()
