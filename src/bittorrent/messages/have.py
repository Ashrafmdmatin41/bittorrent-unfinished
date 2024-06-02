from typing import Type
from dataclasses import dataclass
import struct

@dataclass
class Have:
    index: int
    
    message_length: int = 1
    message_id: int = 4
    
    MESSAGE_FMT: str = ">IBI"
    PAYLOAD_FMT: str = ">I"
    
    def to_bytes(self: "Have") -> bytes:
        return struct.pack(self.MESSAGE_FMT, self.message_length, self.message_id, self.index)
    
    @classmethod
    def from_bytes(cls: Type["Have"], payload: bytes) -> "Have":
        return cls(*struct.unpack(cls.PAYLOAD_FMT, payload))