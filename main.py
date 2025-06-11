import multiprocessing
import sys

import mitm
import utils
import watcher


def main():
    # 启动 mitmproxy 进程
    mitm_proxy_address = mitm.start()
    if mitm_proxy_address is None:
        utils.print_error_message("启动 mitmproxy 失败，请切换端口进行重试")
        sys.exit(1)

    # utils.print_info_message(f"mitmproxy listening at {mitm_proxy_address}")

    # 检查环境是否配置正确
    utils.wait_until_env_configured(mitm_proxy_address)

    # 启动文件监控及 ws 服务
    watcher.start()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()

