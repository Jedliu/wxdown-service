import multiprocessing
import operator
import os
import queue
import re
import sys
import threading
import time
from pathlib import Path

from mitmproxy.tools.main import mitmdump

import utils
from logger import logger

SRC_PATH = Path.absolute(Path(__file__)).parent
PLUGIN_FILE = str(SRC_PATH / 'resources' / 'credential.py')
CREDENTIALS_FILE = str(SRC_PATH / 'resources' / 'data' / 'credentials.json')


def mitmproxy_process(args: list[str], output_queue: multiprocessing.Queue):
    sys.stdout = sys.stderr = utils.Capture(output_queue)
    print(f'Run mitmdump process {args} ({os.getpid()})...', flush=True)
    mitmdump(args)


def start(port: str):
    # 启动 mitmproxy 并加载 credentials 插件
    args = ['-p', port, '-s', PLUGIN_FILE, '--set', 'credentials='+CREDENTIALS_FILE]
    mitm_output_queue = multiprocessing.Queue()
    mitm_process = multiprocessing.Process(target=mitmproxy_process, args=(args, mitm_output_queue))
    mitm_process.start()

    start_time = time.time()
    proxy_address = None

    while time.time() - start_time < 10:
        try:
            message = mitm_output_queue.get(timeout=0.1)
            logger.info(message)
            if operator.contains(message, "HTTP(S) proxy listening at"):
                match = re.search(r'\*:(\d+)', message)
                port = match.group(1)
                proxy_address = f"http://127.0.0.1:{port}"
                break
            elif operator.contains(message, "address already in use"):
                break
        except queue.Empty:
            pass

    if proxy_address:
        pass
        # mitmproxy 启动成功，用一个守护线程处理后续日志
        # threading.Thread(target=handle_mitm_output, args=(mitm_output_queue,), daemon=True).start()
    else:
        mitm_process.terminate()

    return proxy_address


def handle_mitm_output(output_queue: multiprocessing.Queue):
    while True:
        message = output_queue.get()
        logger.info(message)
