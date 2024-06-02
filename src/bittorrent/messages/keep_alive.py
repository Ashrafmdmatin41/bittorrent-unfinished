from typing import Type
from dataclasses import dataclass
import struct

@dataclass
class KeepAlive:
    message_length: int = 0
    
    MESSAGE_FMT: str = ">I"
    PAYLOAD_FMT: str = ">I"
    
    def to_bytes(self: "KeepAlive") -> bytes:
        return struct.pack(self.MESSAGE_FMT, self.message_length)