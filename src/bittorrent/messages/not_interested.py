from dataclasses import dataclass
import struct

@dataclass
class NotInterested:
    message_length: int = 1
    message_id: int = 3
    
    MESSAGE_FMT: str = ">IB"
    
    def to_bytes(self: "NotInterested") -> bytes:
        return struct.pack(self.MESSAGE_FMT, self.message_length, self.message_id)