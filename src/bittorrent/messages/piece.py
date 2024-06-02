from typing import Type
from dataclasses import dataclass, field
import struct

@dataclass
class Piece:
    index: int
    begin: int
    block: bytes
    
    message_length: int = field(init=False)
    message_id: int = 7
    
    MESSAGE_FMT: str = ">IBIII"
    PAYLOAD_FMT: str = ">III"
    
    def __post_init__(self: "Piece") -> None:
        self.message_length = 9 + len(self.block)
    
    def to_bytes(self: "Piece") -> bytes:
        return struct.pack(self.MESSAGE_FMT, self.message_length, self.message_id, self.index, self.begin, self.block)
    
    @classmethod
    def from_bytes(cls: Type["Piece"], payload: bytes) -> "Piece":
        return cls(*struct.unpack(cls.PAYLOAD_FMT, payload))