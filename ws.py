import asyncio
import time
import os
import websockets.exceptions

from websockets.asyncio.server import serve, ServerConnection
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from pathlib import Path


# Define the JSON file to monitor
FILENAME = os.fspath(Path('resources/credentials.json').absolute())

class CredentialsFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == FILENAME:
            try:
                with open(FILENAME, 'r') as file:
                    data = file.read()
                    notify_clients(data)

            except Exception as e:
                print(f"Error reading file: {e}")


# 保存所有连接的 websocket 客户端
ws_clients = set()


# 处理 websocket 连接
async def connect_handler(client: ServerConnection):
    ws_clients.add(client)
    print(f"当前连接客户端数: {len(ws_clients)}")
    try:
        while True:
            await client.recv()
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        ws_clients.remove(client)
        print(f"当前连接客户端数: {len(ws_clients)}")


# 通知所有客户端
async def notify_clients(data: str):
    print('通知所有的客户端:', data)
    for client in list(ws_clients):
        try:
            await client.send(data)
        except websockets.ConnectionClosed:
            pass


# 启动 websocket 服务
async def start_ws():
    async with serve(connect_handler, "localhost") as server:
        for socket in server.sockets:
            port = socket.getsockname()[1]
            print(f"Listening on ws://127.0.0.1:{port}")
        await server.serve_forever()


def main():
    Path(FILENAME).touch()

    event_handler = CredentialsFileHandler()
    observer = Observer()
    observer.schedule(event_handler, FILENAME, recursive=True)
    observer.start()

    try:
        asyncio.run(start_ws())
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
