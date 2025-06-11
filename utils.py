import re
import urllib.request
import requests
import cert
import version

from logger import logger
from termcolor import colored


# 检查代理是否正确
def is_proxy_setting(target_proxy_address):
    proxy = urllib.request.getproxies()
    logger.debug(f"检测到系统代理设置为: {proxy}")
    logger.debug(f"mitmproxy 代理为: {target_proxy_address}")

    try:
        response = requests.get('http://mitm.it', proxies=proxy).text
    except requests.exceptions.ProxyError as e:
        print_error_message("\n代理配置有误，请检查设置")
        logger.error(f"检测 http://mitm.it 代理时出错: {e}")
        return False

    is_match = re.search(r'If you can see this, traffic is not passing through mitmproxy', response)
    if is_match or proxy['http'] != target_proxy_address['http'] or proxy['https'] != target_proxy_address['https']:
        print_error_message("\n检测到系统的网络代理设置不正确")
        print(f"当前网络代理: {proxy}")
        print(f"目标网络代理: {target_proxy_address}")
        return False
    else:
        return True


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
def wait_until_proxy_setting(proxy_address):
    while True:
        if is_proxy_setting({"http": proxy_address, "https": proxy_address}):
            break
        else:
            print_info_message("\n(press <enter> to continue)")
            input()


def wait_until_env_configured(proxy_address=None):
    # 检查证书是否安装
    wait_until_certificate_installed()

    # 检查系统代理是否设置正确
    wait_until_proxy_setting(proxy_address)


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
