import wincertstore
import os


def is_certificate_installed(cert_name = "mitmproxy"):
    stores = ["MY", "ROOT", "CA"]
    for storename in stores:
        with wincertstore.CertSystemStore(storename) as store:
            for cert in store.itercerts():
                name = cert.get_name()
                if name == cert_name:
                    return True
    return False
