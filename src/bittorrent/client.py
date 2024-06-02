from typing import List, Union
import logging

from .torrent import Torrent
from .trackers import Tracker

logger = logging.getLogger(__name__)

class BitTorrent:
    def __init__(self: "BitTorrent") -> None:
        self.torrents: List[Torrent] = []
    
    def add_torrent(self: "BitTorrent", file: Union[str, bytes]) -> None:
        self.torrents.append(Torrent(file))