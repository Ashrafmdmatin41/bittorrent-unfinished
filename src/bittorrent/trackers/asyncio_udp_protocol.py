from typing import Tuple
import asyncio

class AsyncIOUDPProtocol(asyncio.DatagramProtocol):
    def __init__(self: "UDPProtocol") -> None:
        self.transport: asyncio.transports.DatagramTransport = None
        self.received_data: asyncio.Queue[Tuple[bytes, Tuple[str, int]]] = asyncio.Queue()
    
    def connection_made(self: "UDPProtocol", transport: asyncio.transports.DatagramTransport) -> None:
        self.transport = transport
    
    def datagram_received(self: "UDPProtocol", data: bytes, addr: Tuple[str, int]) -> None:
        asyncio.ensure_future(self.received_data.put((data, addr)))
    
    def send(self: "UDPProtocol", message: bytes) -> None:
        self.transport.sendto(message)
    
    async def recv(self: "UDPProtocol") -> bytes:
        return (await self.received_data.get())[0]