import logging
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import time
from audio.audio import load_audio_folder, merge_audio
from audio.nft_storage import NFTStorage
from dotenv import load_dotenv
load_dotenv()


stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s',
                    handlers=[logging.FileHandler("audiomerge.log", mode='w'),
                              stream_handler])

_logger = logging.getLogger(__name__)


app = FastAPI()


class SampleList(BaseModel):
    sample_cids: List[str]


DOWNLOAD_PATH = "downloads/"


@app.post("/merge")
async def merge(samples: SampleList):
    '''
        Downloads a list of samples and merges them, uploads the merge to ipfs, and returns the CID of the IPFS upload
    '''
    try:
        nfts: NFTStorage = NFTStorage(os.getenv("NFT_STORAGE_API"))
        [nfts.download(cid) for cid in samples.sample_cids]
        audio_segments: Dict[str, Any] = load_audio_folder(DOWNLOAD_PATH)
        temp_file = f"tmp_{time.time()}_output.wav"
        merge_audio(list(audio_segments.values()), temp_file)
        with open(temp_file, "r") as f:
            cid = nfts.upload(f.buffer)
            _logger.info(f"Merge result: {cid}")
        os.remove(temp_file)
        return {"success": True, "cid": cid}
    except Exception as e:
        _logger.error(f"Failed to merge audio samples... {e}")
        return {'success': False}
    finally:
        for d in os.listdir(DOWNLOAD_PATH):
            if d.split(".")[0] in samples.sample_cids:
                os.remove(f"{DOWNLOAD_PATH}{d}")
