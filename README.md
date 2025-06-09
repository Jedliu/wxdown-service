# wxdown-service

## 功能说明

第一版是一个命令行程序，没有图形界面，使用 pyinstaller 进行打包。

1. 启动 mitmproxy 服务进程，并加载 credential.py 插件，拦截微信流量并写入 credentials.json 文件
2. 检查证书是否安装，若没有安装，则提示手动安装后继续
3. 检查网络代理是否设置正确，若设置有误，则提示手动设置后继续
4. 启动 watcher 服务进程，监听 credentials.json 文件的变动，并通过 websocket 通知浏览器
5. 最后，提示成功

## 打包命令(pyinstaller)

```shell
pyinstaller -y --clean -D -c -n wxdown-service --add-data=resources/credential.py:resources/ main.py
```

### 参数说明

- `-D` 打包为一个目录
- `-c` 打开控制台窗口用来输入/输出
- `-add-data` 添加资源文件

## macOS 系统

由于 macOS 系统要求必须签名才能分发应用程序，所以从 [Releases](https://github.com/wechat-article/wxdown-service/releases) 下载的 macOS 版本不一定能用，这种情况下
推荐从源码自己进行构建。构建步骤如下：

> 如果有大佬知道其他能够解决签名问题的话，不惜赐教。

### 1. 下载源码
```shell
git clone git@github.com:wechat-article/wxdown-service.git
```

### 2. 配置环境 & 安装依赖
```shell
# 创建虚拟环境
python3 -m venv .
source bin/activate

pip3 install -r requirements.txt
pip3 install pyinstaller
```

### 3. 打包
```shell
pyinstaller -y --clean wxdown-service.spec
```

### 4. 运行
```shell
cd dist/wxdown-service
./wxdown-service
```
