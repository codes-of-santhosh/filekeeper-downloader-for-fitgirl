import json
import base64
import zlib
import re
import urllib.request
import base58
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256

from .models import FileKeeperLink

class PasteParser:
    """
    Lightning-fast, native Python PrivateBin decrypter.
    Decrypts FitGirl AES-256-GCM / PBKDF2 pastes in <0.2 seconds
    without needing any browser or external binaries!
    """
    
    @staticmethod
    def decrypt_privatebin(url: str) -> list[str]:
        # URL format: https://paste.fitgirl-repacks.site/?<id>#<key>
        if '#' not in url or '?' not in url:
            raise ValueError("Invalid FitGirl paste URL. Must contain '?' and '#<key>'.")
            
        base_url = url.split('?')[0]
        query_part = url.split('?')[1]
        paste_id, key_b58 = query_part.split('#')
        
        # 1. Decode Base58 key
        key = base58.b58decode(key_b58)
        
        # 2. Fetch encrypted JSON payload
        req_url = f"{base_url}?{paste_id}"
        req = urllib.request.Request(
            req_url,
            headers={
                "X-Requested-With": "JSONHttpRequest",
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        if data.get("status") != 0:
            raise ValueError(f"Failed to fetch paste: status {data.get('status')}")
            
        # 3. Extract spec and ciphertext
        # spec: [iv, salt, iterations, keysize, tagsize, algo, mode, compression]
        spec = data["adata"][0]
        iv = base64.b64decode(spec[0])
        salt = base64.b64decode(spec[1])
        iterations = spec[2]
        ksize = spec[3] // 8
        tag_size = spec[4] // 8
        
        # 4. Derive key using PBKDF2 with SHA-256
        derived_key = PBKDF2(key, salt, dkLen=ksize, count=iterations, hmac_hash_module=SHA256)
        
        # 5. Extract AES-GCM ciphertext and authentication tag
        ct_data = base64.b64decode(data["ct"])
        tag = ct_data[-tag_size:]
        ciphertext = ct_data[:-tag_size]
        
        # Additional authenticated data (compact json)
        adata = json.dumps(data["adata"], separators=(',', ':')).encode('utf-8')
        
        # 6. Decrypt and verify AES-256-GCM
        cipher = AES.new(derived_key, AES.MODE_GCM, nonce=iv)
        cipher.update(adata)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        
        # 7. Decompress raw deflate
        decompressed = zlib.decompress(plaintext, -zlib.MAX_WBITS).decode('utf-8')
        paste_data = json.loads(decompressed)
        paste_text = paste_data.get("paste", "")
        
        # 8. Extract FileKeeper links
        urls = re.findall(r'https?://[^\s<>"\']+', paste_text)
        fk_urls = [u for u in urls if 'filekeeper.net' in u or 'filekeeper.com' in u]
        
        # Deduplicate while preserving order
        seen = set()
        unique_urls = []
        for u in fk_urls:
            if u not in seen:
                seen.add(u)
                unique_urls.append(u)
                
        return unique_urls

    def get_filekeeper_links(self, paste_url: str) -> list[FileKeeperLink]:
        urls = self.decrypt_privatebin(paste_url)
        return [FileKeeperLink(url=u) for u in urls]
