import multiprocessing
import sys
import mitm
import watcher
import utils


def main():
    # 启动 mitmproxy 进程
    proxy_address = mitm.start()
    if proxy_address is None:
        utils.print_error_message("启动 mitmproxy 失败，请切换端口进行重试")
        sys.exit(1)

    # utils.print_info_message(f"mitmproxy listening at {proxy_address}")

    # 检查环境是否配置正确
    utils.wait_until_env_configured(proxy_address)

    # 启动文件监控及 ws 服务
    watcher.start()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()

