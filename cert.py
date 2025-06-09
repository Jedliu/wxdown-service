import platform
import subprocess
from logger import logger


def is_certificate_installed(cert_name = 'mitmproxy'):
    if platform.system() == 'Windows':
        import wincertstore

        logger.debug(f"证书检测结果:")
        stores = ["MY", "ROOT", "CA"]
        for store_name in stores:
            with wincertstore.CertSystemStore(store_name) as store:
                for cert in store.itercerts():
                    name = cert.get_name()
                    logger.debug(f"{name}")
                    if name == cert_name:
                        return True
        return False
    elif platform.system() == 'Darwin':
        try:
            result = subprocess.run(['security', 'find-certificate', '-c', cert_name], capture_output=True, text=True)
            logger.debug(f"证书检测结果: {result}")
            return result.returncode == 0
        except FileNotFoundError:
            logger.error("此系统中未找到 security 命令")
            raise NotImplementedError("此系统中未找到 security 命令")
    else:
        logger.error(f"暂不支持该系统: {platform.system()}")
        raise NotImplementedError(f"暂不支持该系统: {platform.system()}")
