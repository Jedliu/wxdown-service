import re
import urllib.request
from pathlib import Path

import requests
from termcolor import colored

import cert
import version
from console import console
from logger import logger

SRC_PATH = Path.absolute(Path(__file__)).parent
LOGO_FILE = str(SRC_PATH / 'resources' / 'logo.txt')

# 检查系统代理是否设置正确
def check_system_proxy(mitm_proxy_address):
    proxy_obj = urllib.request.getproxies()
    logger.debug(f"检测到系统代理设置为: {proxy_obj}")
    logger.debug(f"mitmproxy 代理为: {mitm_proxy_address}")

    try:
        response = requests.get('http://mitm.it', proxies=proxy_obj).text
    except requests.exceptions.ProxyError as e:
        print_error_message("\n代理配置有误，请检查设置")
        print("当前代理设置:", proxy_obj)
        logger.error(f"检测 http://mitm.it 代理时出错: {e}")
        return False

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
        print_error_message("\n检测到系统的网络代理设置不正确")
        print("当前代理设置:", proxy_obj)

    return success


# 检查证书是否安装
def check_certificate_installed():
    if not cert.is_certificate_installed('mitmproxy'):
        print_error_message("\n系统中未检测到 mitmproxy 的证书，请进行手动安装。")
        print_info_message(
            "证书安装教程请参考: https://docs.mitmproxy.org/stable/concepts/certificates/#installing-the-mitmproxy-ca-certificate-manually")
        return False
    return True


def wait_until_env_configured(mitm_proxy_address = None):
    while True:
        with console.status("Checking..."):
            # 检查证书是否安装
            v1 = check_certificate_installed()

            # 检查系统代理是否设置正确
            v2 = check_system_proxy(mitm_proxy_address)

            if v1 and v2:
                print_success_message('环境配置正确')

        print_info_message("\n(press <enter> to check again, press <ctrl-c> to exit)")
        input()


def print_logo():
    with open(LOGO_FILE) as file:
        print(file.read())
    print(f"v{version.version}\n")

def print_success_message(message):
    print(colored(message, "green", attrs=["bold"]))

def print_error_message(message):
    print(colored(message, "red", attrs=["bold"]))

def print_info_message(message):
    print(colored(message, "grey", None, attrs=["bold"]))

def get_version():
    return f"wxdown-service {version.version}"
