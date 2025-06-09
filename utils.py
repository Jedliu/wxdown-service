import re
import subprocess
import time
import urllib.request
import requests

def proxy_correct():
    proxy = urllib.request.getproxies()
    print(proxy)
    response = requests.get('http://mitm.it', proxies=proxy).text
    if re.search(r'If you can see this, traffic is not passing through mitmproxy', response):
        return False
    else:
        return True

cert_name = 'mitmproxy'

def is_certificate_installed_macos():
    try:
        result = subprocess.run(['security', 'find-certificate', '-c', cert_name], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        raise NotImplementedError("此系统中未找到 security 命令")

def is_certificate_installed_windows():
    import wincertstore
    import os
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    import hashlib

    def is_certificate_installed(cert_name, thumbprint=None):
        if os.name != 'nt':
            raise NotImplementedError("此函数仅适用于 Windows")

        stores = ["MY", "ROOT", "CA"]
        for storename in stores:
            with wincertstore.CertSystemStore(storename) as store:
                for cert in store.itercerts():
                    name = cert.get_name()
                    pem = cert.get_pem().decode("ascii")
                    if name == cert_name:
                        if thumbprint is None:
                            return True
                        else:
                            cert_obj = x509.load_pem_x509_certificate(pem.encode('utf-8'), default_backend())
                            der = cert_obj.public_bytes(x509.Encoding.DER)
                            computed_thumbprint = hashlib.sha1(der).hexdigest().upper()
                            if computed_thumbprint == thumbprint:
                                return True
        return False

def wait_until_certificate_installed():
    while True:
        if is_certificate_installed_macos():
            break
        else:
            input("系统中未检测到 mitmproxy 的证书，请进行手动安装。\n证书安装教程请参考: https://docs.mitmproxy.org/stable/concepts/certificates/#installing-the-mitmproxy-ca-certificate-manually\n\n证书安装后请按任意键继续")

def wait_until_env_configured():
    # 检查证书是否安装
    wait_until_certificate_installed()

    # 检查系统代理是否设置正确
