from dataclasses import dataclass
import struct

@dataclass
class Unchoke:
    message_length: int = 1
    message_id: int = 1
    
    MESSAGE_FMT: str = ">IB"
    
    def to_bytes(self: "Unchoke") -> bytes:
        return struct.pack(self.MESSAGE_FMT, self.message_length, self.message_id)