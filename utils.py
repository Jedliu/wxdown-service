import io
import multiprocessing
import re
import urllib.request
from pathlib import Path

import requests
from termcolor import colored

import version

SRC_PATH = Path.absolute(Path(__file__)).parent
LOGO_FILE = str(SRC_PATH / 'resources' / 'logo.txt')

# 检查系统代理是否设置正确
def check_system_proxy(mitm_proxy_address):
    proxy_obj = urllib.request.getproxies()

    details = f'将系统代理设置为 [bold green]{mitm_proxy_address.removeprefix('http://')}[/]\n当前系统代理为:\n{proxy_obj}'

    try:
        response = requests.get('http://mitm.it', proxies=proxy_obj, timeout=3).text
    except Exception as e:
        return False, '代理配置有误，请检查设置', details

    traffic_not_passing = re.search(r'If you can see this, traffic is not passing through mitmproxy', response)
    if traffic_not_passing:
        # 流量未经过 mitmproxy
        success = False
    elif proxy_obj.keys() < {'http', 'https'}:
        # 代理需要全部设置
        success = False
    elif proxy_obj['http'] != mitm_proxy_address or proxy_obj['https'] != mitm_proxy_address:
        success = False
    else:
        success = True

    if not success:
        return False, '检测到系统的网络代理设置不正确', details

    return True, '成功', proxy_obj


def print_info_message(message):
    print(colored(message, "grey", None, attrs=["bold"]))

def get_version():
    return f"wxdown-service {version.version}"

class Capture(io.TextIOBase):
    def __init__(self, q: multiprocessing.Queue):
        self.queue = q
        self.buffer = ""

    def writable(self):
        return True

    def write(self, s):
        self.buffer += s
        while '\n' in self.buffer:
            line, _, self.buffer = self.buffer.partition('\n')
            self.queue.put(line)
