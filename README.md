# wxdown-proxy

## 功能说明

第一版是一个命令行程序，没有图形界面，使用 pyinstaller 进行打包。

1. 启动 mitmproxy 服务进程，并加载 credential.py 插件
2. 启动 watcher 服务进程，监听 credentials.json 文件的变动，并通过 websocket 通知浏览器
3. 检查系统证书安装情况，若没有安装，则提示手动安装后继续
4. 尝试自动设置系统代理为 mitmproxy 监听的端口，若设置失败，则提示手动设置后继续
5. 最后，提示成功
