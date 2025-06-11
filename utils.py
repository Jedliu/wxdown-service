import re
import time
import urllib.request
import requests
import cert
import version

from logger import logger
from termcolor import colored
from yaspin import yaspin


# 检查代理是否正确
def is_proxy_setting(mitm_proxy_obj):
    with yaspin(text="检查中"):
        proxy_obj = urllib.request.getproxies()
        logger.debug(f"检测到系统代理设置为: {proxy_obj}")
        logger.debug(f"mitmproxy 代理为: {mitm_proxy_obj}")

        try:
            response = requests.get('http://mitm.it', proxies=proxy_obj).text
        except requests.exceptions.ProxyError as e:
            print_error_message("\n代理配置有误，请检查设置")
            logger.error(f"检测 http://mitm.it 代理时出错: {e}")
            return False

    traffic_not_passing = re.search(r'If you can see this, traffic is not passing through mitmproxy', response)
    if traffic_not_passing:
        # 流量未经过 mitmproxy
        success = False
    elif proxy_obj.keys() < {'http', 'https'}:
        # 代理需要全部设置
        success = False
    elif proxy_obj['http'] != mitm_proxy_obj['http'] or proxy_obj['https'] != mitm_proxy_obj['https']:
        success = False
    else:
        success = True

    if not success:
        print_error_message("\n检测到系统的网络代理设置不正确")
        print(f"当前网络代理: {proxy_obj}")
        print(f"目标网络代理: {mitm_proxy_obj}")

    return success


# 检查证书是否安装
def wait_until_certificate_installed():
    while True:
        if cert.is_certificate_installed('mitmproxy'):
            break
        else:
            print_error_message("\n系统中未检测到 mitmproxy 的证书，请进行手动安装。")
            print_info_message("证书安装教程请参考: https://docs.mitmproxy.org/stable/concepts/certificates/#installing-the-mitmproxy-ca-certificate-manually")
            print_info_message("\n(press <enter> to continue)")
            input()


# 检查系统代理是否设置正确
def wait_until_proxy_setting(mitm_proxy_address):
    while True:
        if is_proxy_setting({"http": mitm_proxy_address, "https": mitm_proxy_address}):
            break
        else:
            print_info_message("\n(press <enter> to continue)")
            input()


def wait_until_env_configured(mitm_proxy_address = None):
    # 检查证书是否安装
    wait_until_certificate_installed()

    # 检查系统代理是否设置正确
    wait_until_proxy_setting(mitm_proxy_address)


def print_logo():
    with open("logo.txt") as file:
        print(file.read())
    print(f"v{version.version}\n")

def print_success_message(message):
    print(colored(message, "green", attrs=["bold"]))

def print_error_message(message):
    print(colored(message, "red", attrs=["bold"]))

def print_info_message(message):
    print(colored(message, "grey", None, attrs=["bold"]))
