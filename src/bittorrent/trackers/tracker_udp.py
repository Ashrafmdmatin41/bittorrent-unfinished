from typing import List, Dict, Tuple, Optional
import logging
import asyncio
import struct

from ..exceptions import TrackerError
from ..enums import ActionType
from ..utils import generate_transaction_id, generate_tracker_key, decode_compact_peers

from .asyncio_udp_protocol import AsyncIOUDPProtocol

logger = logging.getLogger(__name__)

class TrackerUDP:
    def __init__(self: "TrackerUDP", remote_addr: Tuple[str, int], timeout: Optional[int] = 15, retries: Optional[int] = 8) -> None:
        self.MAGIC_PROTOCOL_ID: int = 0x41727101980
        
        self.remote_addr = remote_addr
        self.protocol: Optional[asyncio.DatagramProtocol] = None
        
        self.timeout = timeout
        self.retries = retries
        
        self.connection_id: int = 0
        self.last_connection_id_time: float = 0.0
        
        self.interval: Optional[int] = None
        self.leechers: Optional[int] = None
        self.seeders: Optional[int] = None
        self.peers: List[Tuple[str, int]] = []
    
    async def initialize(self: "TrackerUDP") -> None:
        _, self.protocol = await asyncio.get_event_loop().create_datagram_endpoint(
            protocol_factory=AsyncIOUDPProtocol,
            remote_addr=self.remote_addr
            )
    
    def is_connection_id_expired(self: "TrackerUDP") -> bool:
        return asyncio.get_event_loop().time() - self.last_connection_id_time > 60
    
    async def connect(self: "TrackerUDP") -> None:
        if not self.protocol:
            raise TrackerError("Protocol not initialized. Call initialize() first")
        
        transaction_id: int = generate_transaction_id()
        
        message: bytes = struct.pack(
            ">QII",
            self.MAGIC_PROTOCOL_ID,
            ActionType.CONNECT.value,
            transaction_id
            )
        try:
            self.protocol.send(message)
        except Exception as exc:
            raise TrackerError(f"Connect request error: {exc}")
        
        for retry in range(self.retries):
            try:
                response: bytes = await asyncio.wait_for(
                    self.protocol.recv(),
                    timeout=self.timeout*(2**retry)
                    )
                break
            except asyncio.TimeoutError:
                logger.debug(f"Connect timeout. Retrying for {retry+1}")
        else:
            logger.debug(f"Connect timeout. All retries failed ({self.retries})")
            raise TrackerError("Connect timeout")
        
        if len(response) < 16:
            logger.debug(f"Connect response length ({len(response)}) is less than 16.")
            raise TrackerError("Connect response length is less than 16.")
        
        action, tx_id, connection_id = struct.unpack(">IIQ", response)
        
        if tx_id != transaction_id:
            logger.debug(f"transaction id does not match. Received: {tx_id}, Expected: {transaction_id}.")
            raise TrackerError("transaction id does not match")
        if action != ActionType.CONNECT.value:
            logger.debug(f"action does not match. Received: {action}, Expected: {ActionType.CONNECT.value}.")
            raise TrackerError("action does not match")
        
        self.connection_id = connection_id
        self.last_connection_id_time = asyncio.get_event_loop().time()
    
    async def announce(
        self: "TrackerUDP",
        info_hash: bytes,
        peer_id: bytes,
        port: int,
        downloaded: int,
        left: int,
        uploaded: int,
        event: Optional[int] = 0,
        ip: Optional[int] = 0,
        key: Optional[int] = None,
        numwant: Optional[int] = -1,
        ) -> List[Tuple[str, int]]:
        if not self.connection_id:
            raise TrackerError("connection id not found. Call connect() first")
        
        transaction_id: int = generate_transaction_id()
        
        message: bytes = struct.pack(
            ">QII20s20sQQQIIIiH",
            self.connection_id, # Q
            ActionType.ANNOUNCE.value, # I
            transaction_id, # I
            info_hash, # 20s
            peer_id, # 20s
            downloaded, # Q
            left, # Q
            uploaded, # Q
            event, # I
            ip, # I
            key or generate_tracker_key("udp"), # I
            numwant, # i
            port # H
            )
        
        try:
            self.protocol.send(message)
        except Exception as exc:
            raise TrackerError(f"Announce request error: {exc}")
        
        for retry in range(self.retries):
            if self.is_connection_id_expired():
                logger.debug("connection id expired. requesting new one.")
                await self.connect()
            
            try:
                response: bytes = await asyncio.wait_for(
                    self.protocol.recv(),
                    timeout=self.timeout*(2**retry)
                    )
                break
            except asyncio.TimeoutError:
                logger.debug(f"Announce timeout. Retrying for {retry+1}")
        else:
            logger.debug(f"Announce timeout. All retries failed ({self.retries})")
            raise TrackerError("Announce timeout")
        
        if len(response) < 20:
            logger.debug(f"Announce response length ({len(response)}) is less than 20.")
            raise TrackerError("Announce response length is less than 20.")
        
        action, tx_id, interval, leechers, seeders, = struct.unpack(
            ">IIIII",
            response[:20]
            )
        if tx_id != transaction_id:
            logger.debug(f"transaction id does not match. Received: {tx_id}, Expected: {transaction_id}.")
            raise TrackerError("transaction id does not match")
        if action != ActionType.ANNOUNCE.value:
            logger.debug(f"action does not match. Received: {action}, Expected: {ActionType.ANNOUNCE.value}.")
            raise TrackerError("action does not match")
        
        self.interval = interval
        self.leechers = leechers
        self.seeders = seeders
        self.peers = decode_compact_peers(response[20:])
        
        return {
            "interval": self.interval,
            "leechers": self.leechers,
            "seeders": self.seeders,
            "peers": self.peers
        }