import sys
import mitm
import watcher
import utils


def main():
    # 启动 mitmproxy 进程
    proxy_address = mitm.start()
    if proxy_address is None:
        print("启动 mitmproxy 失败，请切换端口进行重试")
        sys.exit(1)

    print(f"mitmproxy 代理地址: {proxy_address}")

    # 检查证书是否安装，以及代理设置是否正确
    utils.wait_until_env_configured(proxy_address)

    # 启动文件监控及 ws 服务
    watcher.start()


if __name__ == '__main__':
    main()

