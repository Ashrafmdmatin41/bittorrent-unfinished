from typing import Any, List, Dict, Tuple, Optional, Union
from urllib.parse import urlparse, ParseResult
import asyncio
import socket
import struct
import secrets
import hashlib
import os

import bencode

def generate_transaction_id() -> int:
    return int.from_bytes(os.urandom(4), byteorder="big")

def generate_tracker_key(protocol: str) -> bytes:
    if protocol == "http":
        return secrets.token_urlsafe(20)
    elif protocol == "udp":
        return os.urandom(20)
    else:
        ValueError(f"Unknown protocol: {protocol}. Expected 'http' or 'udp'")

def generate_info_hash(info: Dict[bytes, Any]) -> bytes:
    return hashlib.sha1(bencode.encode(info)).digest()

def generate_peer_id(prefix: Optional[bytes] = None, sep: Optional[bytes] = b"-") -> bytes:
    if not prefix:
        prefix = os.urandom(9)
    
    length: int = 20-len(prefix)-len(sep)
    if length < 0:
        raise ValueError("Prefix and separator combined length exceeds the maximum allowed length (20 bytes)")
    
    peer_id: bytes = prefix + sep + os.urandom(length)
    return peer_id

def parse_url(url: Union[bytes, str]) -> Union[Tuple[str, Union[str, Tuple[str, int]]]]:
    if isinstance(url, bytes):
        url = url.decode()
    
    parsed: ParsedResult = urlparse(url)
    if parsed.scheme in ("http", "https"):
        return (parsed.scheme, url.decode())
    elif parsed.scheme == "udp":
        return (parsed.scheme, (parsed.hostname, parsed.port))
    else:
        raise ValueError(f"Unknown tracker scheme: {scheme}")

def decode_compact_peers(data: bytes) -> List[Tuple[str, int]]:
    return [
        (
            socket.inet_ntoa(data[i:i+4]), # IP
            struct.unpack(">H", data[i+4:i+6])[0] # PORT
        ) for i in range(0, len(data), 6)
        ]

async def get_random_port() -> int:
    for port in range(6881, 6889+1):
        try:
            _, writer = await asyncio.open_connection(socket.gethostname(), port)
        except OSError:
            return port
        finally:
            writer.close()
            await writer.wait_closed()
    else:
        raise RuntimeError("No free port found in the range (6881-6889)")