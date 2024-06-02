from typing import Any, List, Dict, Optional, Union, IO
from dataclasses import dataclass, field

import bencode

from .utils import generate_info_hash, generate_peer_id

@dataclass
class Torrent:
    data: Union[str, bytes]
    decoded: bytes = field(init=False)
    peer_id: bytes = field(init=False)
    announce: bytes = field(init=False)
    announce_list: Optional[List[List[bytes]]] = field(init=False)
    info: Dict[bytes, Any] = field(init=False)
    info_hash: bytes = field(init=False)
    total_length: int = field(init=False)

    def __post_init__(self: "Torrent"):
        self.decoded = self._parse_data(self.data)
        self.peer_id = generate_peer_id()
        
        self.announce = self.decoded[b"announce"]
        self.announce_list = self.decoded.get(b"announce-list")
        
        self.info = self.decoded[b"info"]
        self.info_hash = generate_info_hash(self.info)
        
        self.total_length = sum((file[b"length"] for file in self.info[b"files"])) if b"files" in self.info else self.info[b"length"]
    
    def _parse_data(self: "Torrent", data: Union[str, bytes, IO[bytes]]) -> bytes:
        if isinstance(data, str):
            with open(data, "rb") as f:
                return bencode.decode(f.read())
        elif isinstance(data, bytes):
            return bencode.decode(data)
        elif hasattr(data, "read") and callable(data.read):
            return bencode.decode(data.read())
        else:
            raise ValueError("Unsupported data type. Please provide either a file path (as a string), raw bytes, or a file-like object")
