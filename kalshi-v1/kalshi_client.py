from dataclasses import dataclass
import base64
import time
import requests
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization


@dataclass
class KalshiConfig:
    base_url: str
    api_key_id: str
    private_key_path: str


class KalshiClient:
    def __init__(self, cfg: KalshiConfig):
        self.cfg = cfg
        with open(cfg.private_key_path, "rb") as fh:
            self._key = serialization.load_pem_private_key(fh.read(), password=None)

    def _sign(self, ts: str, method: str, path: str) -> str:
        message = f"{ts}{method}{path}".encode()
        signature = self._key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return base64.b64encode(signature).decode()

    def _request(self, method: str, path: str, **kwargs):
        ts = str(int(time.time() * 1000))
        method_up = method.upper()
        signature = self._sign(ts, method_up, path)
        headers = {
            "KALSHI-ACCESS-KEY": self.cfg.api_key_id,
            "KALSHI-ACCESS-TIMESTAMP": ts,
            "KALSHI-ACCESS-SIGNATURE": signature,
        }
        url = self.cfg.base_url.rstrip("/") + path
        return requests.request(method_up, url, headers=headers, timeout=10, **kwargs)

    def get(self, path: str, params=None):
        return self._request("GET", path, params=params)

    def post(self, path: str, json=None):
        return self._request("POST", path, json=json)
