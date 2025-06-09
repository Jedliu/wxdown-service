# mitmproxy 命令采用单独的进程进行启动

from multiprocessing import Process
from mitmproxy.tools.main import mitmdump
from logger import logger
import multiprocessing
import os
import argparse
import io
import sys
import time
import operator
import re
from pathlib import Path

SRC_PATH = Path.absolute(Path(__file__)).parent
PLUGIN_PATH = SRC_PATH / 'resources' / 'credential.py'
PLUGIN_FILE = str(PLUGIN_PATH)


class Capture(io.TextIOBase):
    def __init__(self, queue):
        self.queue = queue
        self.buffer = ""

    def writable(self):
        return True

    def write(self, s):
        self.buffer += s
        while '\n' in self.buffer:
            line, _, self.buffer = self.buffer.partition('\n')
            self.queue.put(line)


def run_mitmdump(args: list[str], queue: multiprocessing.Queue):
    sys.stdout = Capture(queue)
    logger.info(f'Run mitmdump process {args} ({os.getpid()})...')
    mitmdump(args)


def start():
    parser = argparse.ArgumentParser(description='Run mitmproxy using the specified port.')
    parser.add_argument('-p', '--port', type=str, default='65000', help='Proxy Port (default: 65000)')
    args, unparsed = parser.parse_known_args()

    # 启动 mitmproxy 并加载 credentials 插件
    args_arr = ["-p", args.port, "-s", PLUGIN_FILE]
    queue = multiprocessing.Queue()
    p = Process(target=run_mitmdump, args=(args_arr, queue))
    p.start()

    start_time = time.time()
    proxy_address = None

    while time.time() - start_time < 10:
        try:
            message = queue.get_nowait()
            logger.info(message)
            if operator.contains(message, "HTTP(S) proxy listening at"):
                match = re.search(r'\*:(\d+)', message)
                port = match.group(1)
                proxy_address = f"http://127.0.0.1:{port}"
                break
            elif operator.contains(message, "address already in use"):
                break
        except multiprocessing.queues.Empty:
            time.sleep(0.1)

    return proxy_address
