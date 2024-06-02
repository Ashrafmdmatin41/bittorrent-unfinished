from enum import Enum, IntEnum

class ActionType(IntEnum):
    CONNECT: int = 0
    ANNOUNCE: int = 1

class HTTPEventType(Enum):
    STARTED: str = "started"
    STOPPED: str = "stopped"
    COMPLETED: str = "completed"

class UDPEventType(IntEnum):
    COMPLETED: int = 1
    STARTED: int = 2
    STOPPED: int = 3

class EventType:
    HTTP: HTTPEventType = HTTPEventType
    UDP: UDPEventType = UDPEventType

class ProtocolStrings(Enum):
    BITTORRENT_PROTOCOL_V1: bytes = b"BitTorrent protocol"