import argparse
import multiprocessing
import sys

import mitm
import utils
import watcher
from ui.startup import startup_ui


def main():
    # 命令行参数解析
    parser = argparse.ArgumentParser(prog='wxdown-service', description='微信公众号下载助手')
    parser.add_argument('-p', '--port', type=str, default='65000', help='mitmproxy proxy port (default: 65000)')
    parser.add_argument('-v', '--version', action='version', version=utils.get_version(), help='display version')
    args, unparsed = parser.parse_known_args()


    # 启动 mitmproxy 进程
    mitm_proxy_address = mitm.start(args.port)
    if mitm_proxy_address is None:
        utils.print_error_message("启动 mitmproxy 失败，请切换端口进行重试")
        sys.exit(1)

    # 启动文件监控及 ws 服务进程
    ws_address = watcher.start()
    if ws_address is None:
        utils.print_error_message("启动 watcher 失败，请查看错误日志")
        sys.exit(1)

    # 启动 UI
    startup_ui(mitm_proxy_address, ws_address)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    try:
        main()
    except KeyboardInterrupt:
        print("Ctrl+C pressed, exiting.")
