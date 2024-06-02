from typing import Type
from dataclasses import dataclass
import struct

@dataclass
class Request:
    index: int
    begin: int
    length: int
    
    message_length: int = 1
    message_id: int = 6
    
    MESSAGE_FMT: str = ">IBIII"
    PAYLOAD_FMT: str = ">III"
    
    def to_bytes(self: "Request") -> bytes:
        return struct.pack(self.MESSAGE_FMT, self.message_length, self.message_id, self.index, self.begin, self.length)
    
    @classmethod
    def from_bytes(cls: Type["Request"], payload: bytes) -> "Request":
        return cls(*struct.unpack(cls.PAYLOAD_FMT, payload))