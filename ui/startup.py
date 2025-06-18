from ui.header import Header
from ui.layout import make_layout
from ui.main import make_message
from ui.footer import StatusPanel
from rich.live import Live
import time
import utils
import cert
import platform


def startup_ui(mitm_proxy_address = None, ws_address = None):
    layout = make_layout()
    layout['header'].update(Header())
    layout['main'].update(make_message([
        {'name': 'mitmproxy', 'address': mitm_proxy_address},
        {'name': 'websocket', 'address': ws_address},
    ]))
    layout['footer'].update(StatusPanel())

    with Live(layout, refresh_per_second=1, screen=False, transient=True):
        while True:
            time.sleep(1)

            # 检查证书是否安装
            try:
                if not cert.is_certificate_installed('mitmproxy'):
                    if platform.system() == 'Windows':
                        cmd = 'certutil -addstore root %userprofile%\\.mitmproxy\\mitmproxy-ca-cert.cer'
                    elif platform.system() == 'Darwin':
                        cmd = 'sudo security add-trusted-cert -d -p ssl -p basic -k /Library/Keychains/System.keychain ~/.mitmproxy/mitmproxy-ca-cert.pem'
                    layout['footer'].update(
                        StatusPanel(is_success=False, reason="系统中未检测到 mitmproxy 的证书，请手动安装。",
                                    details=f"执行以下命令安装证书:\n[bold green]{cmd}[/]"))
                    continue
            except Exception as e:
                layout['footer'].update(
                    StatusPanel(is_success=False, reason="系统检测 mitmproxy 证书时异常。",
                                details="请将日志文件发送给开发者"))
                continue

            # 检查代理是否正确
            success, reason, details = utils.check_system_proxy(mitm_proxy_address)
            layout['footer'].update(StatusPanel(is_success=success, ws_address=ws_address, reason=reason, details=details))
            continue
