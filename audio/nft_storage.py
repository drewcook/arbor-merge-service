from multiprocessing.sharedctypes import Value
from typing import Dict, Any, List, Type
import requests
import json
import wget
import os
import time


class NFTStorage:
    def __init__(self, token: str):
        self._base_url = "https://api.nft.storage"
        self._token = token

    def api(self, path: str = "", method: str = "get", data: Any = {}) -> Dict[str, Any]:
        with getattr(requests, method)(self._base_url + path, headers={"Authorization": f"Bearer {self._token}"}, data=data) as resp:
            if resp.json().get("ok") is None or resp.json().get("ok") == False:
                raise Exception(
                    f"Failed to connect to nft.storage... {resp.json()['error']['message']}")
            return resp.json()

    def list(self) -> List[str]:
        return [nft['cid'] for nft in self.api()['value']]

    def get_nft(self, cid: str) -> Dict[str, Any]:
        return self.api(f"/{cid}")['value']

    def upload(self, data) -> str:
        return self.api("/upload", "post", data)['value']['cid']

    def delete(self, cid: str) -> bool:
        return self.api(f"/{cid}", "delete")['ok']

    def download(self, cid: str):
        fname = "tmp.wav"
        try:
            if not isinstance(cid, str):
                raise TypeError(f"{cid}")
            wget.download(f"https://ipfs.io/ipfs/{cid}", out=fname)
            while fname not in os.listdir():
                time.sleep(.1)
            os.rename(fname, f"{os.getcwd()}/downloads/{cid}.wav")
        finally:
            for f in os.listdir():
                if f == fname:
                    os.remove(f)
