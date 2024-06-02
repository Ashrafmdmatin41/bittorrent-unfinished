from typing import Any, Dict, List, Optional
import urllib.parse
import logging

import bencode
import httpx

from ..exceptions import TrackerError
from ..utils import generate_tracker_key, decode_compact_peers

logger = logging.getLogger(__name__)

class TrackerHTTP:
    def __init__(self: "Tracker", url: str, timeout: Optional[int] = 30) -> None:
        self.url = url
        self.timeout = timeout
        
        self.interval: Optional[int] = None
        self.min_interval: Optional[int] = None
        self.tracker_id: Optional[bytes] = None
        self.complete: Optional[int] = None
        self.incomplete: Optional[int] = None
        self.peers: List[str, int] = []
    
    async def announce(
        self: "TrackerHTTP",
        info_hash: bytes,
        peer_id: bytes,
        port: int,
        uploaded: int,
        downloaded: int,
        left: int,
        compact: Optional[bool] = True,
        no_peer_id: Optional[bool] = None,
        event: Optional[str] = None,
        ip: Optional[str] = None,
        numwant: Optional[int] = None,
        key: Optional[str] = None,
        trackerid: Optional[str] = None,
        timeout: Optional[int] = 5
        ) -> Dict[bytes, Any]:
        params: Dict[str, Any] = {
            "info_hash": info_hash,
            "peer_id": peer_id,
            "port": port,
            "uploaded": uploaded,
            "downloaded": downloaded,
            "left": left,
            "compact": compact,
            "no_peer_id": no_peer_id,
            "event": event,
            "ip": ip,
            "numwant": numwant,
            "key": key or generate_tracker_key("http"),
            "trackerid": trackerid or self.trackerid
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response: httpx.Response = await client.get(self.url, params={k: v for k, v in params.items() if v})
            if not response.content:
                response.raise_for_status()
            
            decoded_response: Dict[bytes, Any] = bencode.decode(response.content)
            
            if response.status_code != 200 or (failure_reason := decoded_response.get(b"failure reason")):
                logger.debug(f"Announce request failed: {decoded_response}")
                raise TrackerError(f"Announce request failed: {failure_reason}")
            elif (warning_message := decoded_response.get(b"warning message")):
                logger.warning(warning_message)
            
            self.interval = decoded_response["interval"]
            self.min_interval = decoded_response.get("min_interval")
            self.trackerid = decoded_response.get("trackerid")
            self.complete = decoded_response.get("complete")
            self.incomplete = decoded_response.get("incomplete")
            
            peers = decoded_response["peers"]
            if isinstance(peers, bytes):
                decoded_response["peers"] = decode_compact_peers(peers)
            
            self.peers.extend((p for p in decoded_response["peers"] if p not in self.peers))
            return decoded_response
