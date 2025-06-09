import asyncio
from pathlib import Path

import websockets
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer
from websockets.asyncio.server import serve, ServerConnection
from logger import logger


# Credentials.json 文件位置
SRC_PATH = Path.absolute(Path(__file__)).parent
CREDENTIALS_JSON_PATH = SRC_PATH / "resources" / "credentials.json"
CREDENTIALS_JSON_FILE = str(CREDENTIALS_JSON_PATH)


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
async def notify_clients(notification_queue: asyncio.Queue):
    try:
        while True:
            data = await notification_queue.get()
            if len(ws_clients) > 0:
                print('通知所有客户端最新 Credentials 数据')

            for client in list(ws_clients):
                try:
                    await client.send(data)
                except websockets.ConnectionClosed:
                    ws_clients.remove(client)
    except Exception as e:
        logger.error(f"通知客户端时发生错误: {e}")


class CredentialsFileHandler(FileSystemEventHandler):
    def __init__(self, filename, eventloop, notification_queue):
        self.filename = filename
        self.loop = eventloop
        self.notification_queue = notification_queue
        logger.debug(f"开始监控文件: {filename}")

    def on_any_event(self, event: FileSystemEvent) -> None:
        logger.debug(f"on_any_event: {event}")

    def on_modified(self, event):
        logger.debug(f"on_modified: {event}")
        if event.src_path == self.filename:
            try:
                with open(self.filename, 'r') as file:
                    data = file.read()
                asyncio.run_coroutine_threadsafe(self.notification_queue.put(data), self.loop)
            except Exception as e:
                print(f"Error reading file: {e}")


# 启动 websocket 服务
async def main(notification_queue):
    asyncio.create_task(notify_clients(notification_queue))

    logger.info(f"开始启动 websocket 服务")
    async with serve(connect_handler, "localhost") as server:
        for socket in server.sockets:
            port = socket.getsockname()[1]
            logger.info(f"websocket 端口: {port}")
            print(f"WebSocket 监听地址: ws://localhost:{port}")
            print("\n所有服务已启动完毕! \n\n请配置网站的 Credentials 设置以抓取阅读量等数据")

        logger.info(f"websocket 服务启动完毕")
        await server.serve_forever()


def start():
    Path(CREDENTIALS_JSON_FILE).touch()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    notification_queue = asyncio.Queue()
    event_handler = CredentialsFileHandler(CREDENTIALS_JSON_FILE, loop, notification_queue)
    observer = Observer()
    observer.schedule(event_handler, CREDENTIALS_JSON_FILE, recursive=True)

    try:
        observer.start()
        loop.run_until_complete(main(notification_queue))
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
        loop.close()

