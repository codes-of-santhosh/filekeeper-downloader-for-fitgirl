from dataclasses import dataclass
from typing import Optional

@dataclass
class FileKeeperLink:
    url: str

@dataclass
class ResolvedFile:
    original_url: str
    direct_url: str
    filename: str
    size: str
    status: str = "Pending"
    gid: Optional[str] = None
    progress: float = 0.0
