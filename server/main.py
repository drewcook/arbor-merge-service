import logging
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import time
from audio.audio import merge_audio
from audio.nft_storage import NFTStorage
from dotenv import load_dotenv
from pydub import AudioSegment
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

    cids: List[str] = samples.sample_cids
    fnames: Dict[str, Any] = {}
    try:
        nfts: NFTStorage = NFTStorage(os.getenv("NFT_STORAGE_API"))
        for cid in cids:
            fnames[cid] = "tmp_" + str(int(time.time())) + ".wav"
            nfts.download(cid, fnames[cid])
        audio_segments: Dict[str, Any] = {}
        for cid in cids:
            audio_segments[cid] = AudioSegment.from_file(DOWNLOAD_PATH +
                                                         fnames[cid], format="wav")

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
            if d in fnames.values():
                os.remove(f"{DOWNLOAD_PATH}{d}")
