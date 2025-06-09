import platform
import re
import urllib.request

import requests

from cert import macos


# 检查代理是否正确
def is_proxy_correct(target_proxy_address):
    proxy = urllib.request.getproxies()
    response = requests.get('http://mitm.it', proxies=proxy).text

    if re.search(r'If you can see this, traffic is not passing through mitmproxy',
                 response) or proxy != target_proxy_address:
        print("\n检测到系统的网络代理设置不正确")
        print(f"当前网络代理: {proxy}")
        print(f"目标网络代理: {target_proxy_address}")
        return False
    else:
        return True


# 检查证书是否安装
def wait_until_certificate_installed():
    while True:
        if macos.is_certificate_installed('mitmproxy'):
            break
        else:
            input(
                "系统中未检测到 mitmproxy 的证书，请进行手动安装。\n证书安装教程请参考: https://docs.mitmproxy.org/stable/concepts/certificates/#installing-the-mitmproxy-ca-certificate-manually\n\n证书安装后请按任意键继续")


# 检查系统代理是否设置正确
def wait_until_proxy_setting(proxy_address):
    while True:
        if is_proxy_correct({"http": proxy_address, "https": proxy_address}):
            break
        else:
            input("\n按任意键继续")


def wait_until_env_configured(proxy_address=None):
    # 检查证书是否安装
    wait_until_certificate_installed()

    # 检查系统代理是否设置正确
    wait_until_proxy_setting(proxy_address)
