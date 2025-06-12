import io
import operator
import os
import queue
import re
import sys
import time
from multiprocessing import Process, Queue
from pathlib import Path

from mitmproxy.tools.main import mitmdump

from logger import logger

SRC_PATH = Path.absolute(Path(__file__)).parent
PLUGIN_FILE = str(SRC_PATH / 'resources' / 'credential.py')
CREDENTIALS_FILE = str(SRC_PATH / 'resources' / 'data' / 'credentials.json')


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


def mitmproxy_process(args: list[str], q: Queue):
    sys.stdout = sys.stderr = Capture(q)
    print(f'Run mitmdump process {args} ({os.getpid()})...')
    mitmdump(args)


def start(port):
    # 启动 mitmproxy 并加载 credentials 插件
    args = ['-p', port, '-s', PLUGIN_FILE, '--set', 'credentials='+CREDENTIALS_FILE]
    q = Queue()
    p = Process(target=mitmproxy_process, args=(args, q))
    p.start()

    start_time = time.time()
    proxy_address = None

    while time.time() - start_time < 10:
        try:
            message = q.get_nowait()
            logger.info(message)
            if operator.contains(message, "HTTP(S) proxy listening at"):
                match = re.search(r'\*:(\d+)', message)
                port = match.group(1)
                proxy_address = f"127.0.0.1:{port}"
                break
            elif operator.contains(message, "address already in use"):
                break
        except queue.Empty:
            time.sleep(0.1)

    return proxy_address
