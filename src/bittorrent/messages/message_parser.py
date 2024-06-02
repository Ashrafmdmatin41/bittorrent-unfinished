from typing import Any, Dict, Type
import struct

from .handshake import Handshake
from .keep_alive import KeepAlive
from .choke import Choke
from .unchoke import Unchoke
from .interested import Interested
from .not_interested import NotInterested
from .have import Have
from .bitfield import BitField
from .request import Request
from .piece import Piece
from .cancel import Cancel
from .port import Port

message_id_mapper: Dict[int, Type] = {
    0: Choke,
    1: Unchoke,
    2: Interested,
    3: NotInterested,
    4: Have,
    5: BitField,
    6: Request,
    7: Piece,
    8: Cancel,
    9: Port
}

def parse_message(message: bytes) -> Type[Any]:
    message_length: int = struct.unpack(">I", message[:4])[0]
    if message_length == 0:
        return KeepAlive()
    
    message_id: int = struct.unpack(">B", message[4:5])[0]
    message_class: Type[Any] = message_id_mapper[message_id]
    
    return message_class.from_bytes(payload) if (payload := message[5:]) and hasattr(message_class, "from_bytes") else message_class()