from typing import Type
from dataclasses import dataclass, field
import struct

@dataclass
class BitField:
    bitfield: bytes
    
    message_length: int = field(init=False)
    message_id: int = 5
    
    MESSAGE_FMT: str = ">IB"
    
    def __post_init__(self: "BitField") -> None:
        self.message_length = 1 + len(self.bitfield)
    
    def to_bytes(self: "BitField") -> bytes:
        return struct.pack(self.MESSAGE_FMT, self.message_length, self.message_id) + self.bitfield
    
    @classmethod
    def from_bytes(cls: Type["BitField"], payload: bytes) -> "BitField":
        return cls(payload)