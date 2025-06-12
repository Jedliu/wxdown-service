import argparse
import multiprocessing
import sys

import mitm
import utils
import watcher
from console import console


def main():
    # 命令行参数解析
    parser = argparse.ArgumentParser(prog='wxdown-service', description='微信公众号文章下载助手')
    parser.add_argument('-p', '--port', type=str, default='65000', help='mitmproxy proxy port (default: 65000)')
    parser.add_argument('-v', '--version', action='version', version=utils.get_version(), help='display version')
    args, unparsed = parser.parse_known_args()

    utils.print_logo()

    # 启动 mitmproxy 进程
    mitm_proxy_address = mitm.start(args.port)
    if mitm_proxy_address is None:
        utils.print_error_message("启动 mitmproxy 失败，请切换端口进行重试")
        sys.exit(1)
    utils.print_info_message(f"mitmproxy listening at: {mitm_proxy_address}")

    # 启动文件监控及 ws 服务进程
    ws_address = watcher.start()
    if ws_address is None:
        utils.print_error_message("启动 watcher 失败，请查看错误日志")
        sys.exit(1)
    utils.print_info_message(f"websocket listening at: {ws_address}")


    print()
    console.rule("[bold red]服务已启动")

    # 检查环境是否配置正确
    utils.wait_until_env_configured(mitm_proxy_address)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    try:
        main()
    except KeyboardInterrupt:
        print("Ctrl+C pressed, exiting.")
