from typing import Type
from dataclasses import dataclass, field
import struct

@dataclass
class Handshake:
    pstrlen: int
    pstr: bytes
    reserved: bytes
    info_hash: bytes
    peer_id: bytes
    
    MESSAGE_FMT: str = field(init=False)
    
    def __post_init__(self: "Handshake") -> None:
        self.MESSAGE_FMT = f"B{self.pstrlen}s8s20s20s"
    
    def to_bytes(self: "Handshake") -> bytes:
        return struct.pack(
            self.MESSAGE_FMT,
            self.pstrlen,
            self.pstr,
            self.reserved,
            self.info_hash,
            self.peer_id
            )
    
    @classmethod
    def from_bytes(cls: Type["Handshake"], payload: bytes) -> "Handshake":
        pstrlen: int = struct.unpack(">B", payload[:1])[0]
        return cls(pstrlen, *struct.unpack(f"{pstrlen}s8s20s20s", payload[1:]))