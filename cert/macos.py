import subprocess


def is_certificate_installed(cert_name = 'mitmproxy'):
    try:
        result = subprocess.run(['security', 'find-certificate', '-c', cert_name], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        raise NotImplementedError("此系统中未找到 security 命令")
