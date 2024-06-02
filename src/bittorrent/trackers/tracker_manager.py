from typing import Any, List, Dict, Optional, Tuple, Union

from ..torrent import Torrent
from ..utils import parse_url

from .tracker_http import TrackerHTTP
from .tracker_udp import TrackerUDP

class TrackerManager:
    def __init__(
        self: "TrackerManager",
        torrent: Torrent,
        port: int,
        uploaded: Optional[int] = 0,
        downloaded: Optional[int] = 0,
        left: Optional[int] = None,
        compact: Optional[bool] = None,
        no_peer_id: Optional[bool] = None,
        event: Optional[str] = None,
        ip: Optional[str] = None,
        numwant: Optional[int] = None,
        key: Optional[Union[str, int]] = None,
        tracker_http_timeout: Optional[int] = 30,
        tracker_udp_timeout: Optional[int] = 15,
        tracker_udp_retries: Optional[int] = 2,
        max_concurrent_announce: Optional[int] = 5
        ) -> None:
        self.torrent = torrent
        self.announce_urls: List[List[bytes]] = self.torrent.announce_list if self.torrent.announce_list else [[self.torrent.announce]]
        
        self.port = port
        self.uploaded = uploaded
        self.downloaded = downloaded
        self.left = left if left else self.torrent.total_length
        self.compact = compact
        self.no_peer_id = no_peer_id
        self.event = event
        self.ip = ip
        self.numwant = numwant
        self.key = key
        
        self.tracker_http_timeout = tracker_http_timeout
        self.tracker_udp_retries = tracker_udp_retries
        self.max_concurrent_announce = max_concurrent_announce
        
        self.last_tier_idx: int = 0
        self.last_url_idx: int = 0
        self.trackers: List[Union[TrackerHTTP, TrackerUDP]] = []
        self.peers: List[Peer] = []
    
    def _shuffle_tier_urls(self: "TrackerManager") -> None:
        for tier in self.announce_urls:
            random.shuffle(tier)
    
    async def __announce_http(self: "TrackerManager", url: str) -> Optional[Tuple[TrackerHTTP, Dict[str, Any]]]:
        tracker: TrackerHTTP = TrackerHTTP(url)
        try:
            response = await tracker.announce(
                info_hash=self.torrent.info_hash,
                peer_id=self.torrent.peer_id,
                port=self.port,
                uploaded=self.uploaded,
                downloaded=self.downloaded,
                left=self.left,
                compact=self.compact,
                no_peer_id=self.no_peer_id,
                event=self.event,
                ip=self.ip,
                numwant=self.numwant,
                key=self.key
                )
            return (tracker, response)
        except TrackerError as exc:
            logger.error(exc)
        except Exception as exc:
            logger.exception(exc)
        
        return (None, None)
    
    async def __announce_udp(self: "TrackerManager", address: Tuple[str, int]) -> Optional[Tuple[TrackerUDP, Dict[str, Any]]]:
        tracker = TrackerUDP(address)
        try:
            await tracker.initialize()
            await tracker.connect()
            response = await tracker.announce(
                info_hash=self.torrent.info_hash,
                peer_id=self.torrent.peer_id,
                port=self.port,
                downloaded=self.downloaded,
                left=self.left,
                uploaded=self.downloaded,
                event=self.event,
                ip=self.ip,
                key=self.key,
                numwant=self.numwant
                )
            return (tracker, response)
        except TrackerError as exc:
            logger.error(exc)
        except Exception as exc:
            logger.exception(exc)
        
        return (None, None)
    
    def select_trackers(self: "TrackerManager") -> None:
        self._shuffle_tier_urls()
        
        tier_idx = self.last_tier_idx + 1
        url_idx = self.last_url_idx + 1
        
        if tier_idx > len(self.announce_urls):
            self.last_tier_idx, tier_idx = (0, 0)
        if url_idx > len(self.announce_urls[tier_idx]):
            self.last_url_idx, url_idx = (0, 0)
        
        announced: int = 0
        results = []
        while announced < self.max_concurrent_announce:
            for tier in self.announce_urls[tier_idx]:
                for url in tier[url_idx]:
                    scheme, endpoint = parse_url(url)
                    if scheme == "http":
                        results.append(
                            asyncio.create_task(self.__announce_http(endpoint))
                            )
                        announced += 1
                    elif scheme == "udp":
                        results.append(
                            asyncio.create_task(self.__announce_udp(endpoint))
                            )
                        announced += 1
                    
                    url_idx += 1
                
                tier_idx += 1
        
        self.last_tier_idx = tier_idx
        self.last_url_idx = url_idx
        
        for tracker, response in results:
            if response is None:
                continue
            elif len(response["peers"]) == 0:
                continue
            
            self.trackers.append(tracker)
