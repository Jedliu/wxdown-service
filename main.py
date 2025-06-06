import sys
import mitm
import asyncio
import watcher


def main():
    # 启动 mitmproxy 进程
    proxy_address = mitm.start()
    if proxy_address is None:
        print("启动 mitmproxy 失败，请切换端口进行重试")
        sys.exit(1)

    print(f"mitmproxy has started successfully on {proxy_address}")

    # 设置系统代理
    # watcher.start_websocket()
    # 检查证书是否安装

    # 检查系统代理是否设置正确


if __name__ == '__main__':
    # print(utils.proxy_correct())
    # print(utils.is_certificate_installed_macos())
    # proxy = urllib.request.getproxies()
    # print(proxy)
    # response = requests.get('http://mitm.it', proxies=proxy)
    # print(response.text)
    main()

