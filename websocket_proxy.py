import asyncio
import socket
import json
import struct
from websockets.server import serve

async def to_vectorun(websocket, soc):
    """Relaye les messages de la page Web vers Vectorun."""
    while True:
        from_web_page = await websocket.recv()  # Attend un message du client WebSocket
        print(f"Reçu de la page Web : {from_web_page}")
        message = from_web_page.encode()
        taille = struct.pack('>I', len(message))  # '>I' = entier non signé, 4 octets, big endian
        await asyncio.get_running_loop().sock_sendall(soc, taille + message)  # Envoi non bloquant

async def to_web_page(websocket, soc):
    """Relaye les messages de Vectorun vers la page Web."""
    asyncio.create_task(to_vectorun(websocket, soc))  # Lance l'envoi en parallèle

    while True:
        try:
            data = await asyncio.wait_for(asyncio.get_running_loop().sock_recv(soc, 100000), timeout=3)
            if data:
                data = data[4:]
                print("data", data)
                data = data.decode()
                print(f"Reçu de Vectorun : {data}")
                await websocket.send(data)  # Envoie le message au WebSocket
        except asyncio.TimeoutError:
            pass  # Timeout évité, continue la boucle

async def main():
    """Initialise la connexion socket et le serveur WebSocket."""
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setblocking(False)  # Mode non bloquant
    await asyncio.get_running_loop().sock_connect(soc, ("localhost", 1664))  # Connexion asynchrone

    async with serve(lambda ws: to_web_page(ws, soc), "localhost", 1665):
        print("Serveur WebSocket démarré sur ws://localhost:1665")
        await asyncio.Future()  # Bloque indéfiniment

if __name__ == "__main__":
    asyncio.run(main())
