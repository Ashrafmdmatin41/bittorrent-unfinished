from typing import Type
from dataclasses import dataclass
import struct

@dataclass
class Port:
    listen_port: int
    
    message_length: int = 3
    message_id: int = 9
    
    MESSAGE_FMT: str = ">IBH"
    PAYLOAD_FMT: str = ">H"
    
    def to_bytes(self: "Port") -> bytes:
        return struct.pack(self.MESSAGE_FMT, self.message_length, self.message_id, self.index, self.begin, self.length)
    
    @classmethod
    def from_bytes(cls: Type["Port"], payload: bytes) -> "Port":
        return cls(*struct.unpack(cls.PAYLOAD_FMT, payload))