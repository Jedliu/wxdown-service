import asyncio
import io
import operator
import queue
import re
import sys
import time
from multiprocessing import Process, Queue
from pathlib import Path

import websockets
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer
from websockets.asyncio.server import serve, ServerConnection

import utils
from logger import logger

# Credentials.json 文件位置
SRC_PATH = Path.absolute(Path(__file__)).parent
CREDENTIALS_DIR = SRC_PATH / 'resources' / 'data'
CREDENTIALS_JSON_PATH = CREDENTIALS_DIR / 'credentials.json'
CREDENTIALS_JSON_FILE = str(CREDENTIALS_JSON_PATH)


# 保存所有连接的 websocket 客户端
ws_clients = set()


# 处理 websocket 连接
async def connect_handler(client: ServerConnection):
    ws_clients.add(client)
    utils.print_info_message(f"当前连接客户端数: {len(ws_clients)}")
    try:
        while True:
            await client.recv()
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        ws_clients.remove(client)
        utils.print_info_message(f"当前连接客户端数: {len(ws_clients)}")


# 通知所有客户端
async def notify_clients(notification_queue: asyncio.Queue):
    try:
        while True:
            data = await notification_queue.get()
            if len(ws_clients) > 0:
                utils.print_info_message('通知所有客户端最新 Credentials 数据')

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

    def on_modified(self, event):
        logger.debug(f"on_modified: {event}")
        if event.src_path == self.filename:
            try:
                with open(self.filename, 'r') as file:
                    data = file.read()
                asyncio.run_coroutine_threadsafe(self.notification_queue.put(data), self.loop)
            except Exception as e:
                utils.print_error_message(f"Error reading file: {e}")


# 启动 websocket 服务
async def main(notification_queue):
    asyncio.create_task(notify_clients(notification_queue))

    logger.info(f"开始启动 websocket 服务")
    async with serve(connect_handler, "localhost") as server:
        for socket in server.sockets:
            port = socket.getsockname()[1]
            logger.info(f"websocket 端口: {port}")
            print(f"服务启动成功:{port}")
            break

        logger.info(f"websocket 服务启动完毕")
        await server.serve_forever()


class Capture(io.TextIOBase):
    def __init__(self, q):
        self.queue = q
        self.buffer = ""

    def writable(self):
        return True

    def write(self, s):
        self.buffer += s
        while '\n' in self.buffer:
            line, _, self.buffer = self.buffer.partition('\n')
            try:
                self.queue.put_nowait(line)
            except queue.Full:
                pass


def watcher_process(q: Queue):
    sys.stdout = sys.stderr = Capture(q)

    Path(CREDENTIALS_JSON_FILE).parent.mkdir(parents=True, exist_ok=True)
    Path(CREDENTIALS_JSON_FILE).touch()


    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    notification_queue = asyncio.Queue()
    event_handler = CredentialsFileHandler(CREDENTIALS_JSON_FILE, loop, notification_queue)
    observer = Observer()
    observer.schedule(event_handler, str(CREDENTIALS_DIR), recursive=True)

    try:
        observer.start()
        loop.run_until_complete(main(notification_queue))
    finally:
        observer.stop()
        observer.join()


def start():
    q = Queue()
    p = Process(target=watcher_process, args=(q,))
    p.start()

    start_time = time.time()
    ws_address = None

    while time.time() - start_time < 10:
        try:
            message = q.get_nowait()
            if operator.contains(message, "服务启动成功"):
                match = re.search(r':(\d+)', message)
                port = match.group(1)
                ws_address = f"ws://127.0.0.1:{port}"
                break
        except queue.Empty:
            time.sleep(0.1)

    return ws_address
