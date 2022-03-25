from csv import excel_tab
from io import BytesIO
import random
import asyncio
import logging
from fastapi import FastAPI, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware


from pydantic import BaseModel
from typing import List, Dict, Any
import os
import time
from audio.audio import merge_audio, merge_audio_bytes
from audio.nft_storage import NFTStorage
from dotenv import load_dotenv
from pydub import AudioSegment
load_dotenv()

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s',
                    handlers=[logging.FileHandler("audiomerge.log", mode='w'),
                              stream_handler])

_logger = logging.getLogger(__name__)


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SampleList(BaseModel):
    sample_cids: List[str]

class Samples(BaseModel):
    samples: List[bytes]

DOWNLOAD_PATH = "downloads/"


@app.post("/merge_old")
async def merge_old(samples: SampleList):
    '''
        Downloads a list of samples and merges them, uploads the merge to ipfs, and returns the CID of the IPFS upload
    '''
    loop = asyncio.get_running_loop()
    cids: List[str] = samples.sample_cids
    if len(cids) < 2:
        return {"success": False, "error": "Number of cids must be greater than 1."}
    fnames: Dict[str, Any] = {}
    try:
        nfts: NFTStorage = NFTStorage(os.getenv("NFT_STORAGE_API"))
        tasks = []
        for cid in cids:
            n_fname = None
            while True:
                n_fname = "tmp_" + str(int(random.random() * 100000)) + ".wav"
                if n_fname in fnames.values():
                    continue
                else:
                    break
            if isinstance(n_fname, str):
                fnames[cid] = n_fname
            else:
                raise Exception("Failed to find file name")
            tasks.append(loop.run_in_executor(
                None, nfts.download, cid, fnames[cid]))
        await asyncio.gather(*tasks)
        _logger.debug(f"Downloads finished for {','.join(cids)}")
        audio_segments: Dict[str, Any] = {}
        tasks = []
        for cid in cids:
            audio_segments[cid] = AudioSegment.from_file(DOWNLOAD_PATH +
                                                         fnames[cid], format="wav")
        _logger.debug("Audio segments built...")
        temp_file = f"tmp_{random.random() * 1000}_output.wav"
        merge_audio(list(audio_segments.values()), temp_file)
        _logger.debug("Merge done.")
        with open(temp_file, "r") as f:
            cid = await loop.run_in_executor(None, nfts.upload, f.buffer)
            _logger.info(f"Merge result: {cid}")
        os.remove(temp_file)
        return {"success": True, "cid": cid}
    except Exception as e:
        _logger.error(f"Failed to merge audio samples... {e}")
        return {'success': False, 'error': "Unhandled exception..."}
    finally:
        for d in os.listdir(DOWNLOAD_PATH):
            if d in fnames.values():
                os.remove(f"{DOWNLOAD_PATH}{d}")


@app.post("/merge")
async def merge(files: List[UploadFile]):
    try:
        
        samples = [AudioSegment.from_file(BytesIO(await file.read())) for file in files]
        merged_bytes = merge_audio_bytes(samples)
        return Response(content = merged_bytes.getvalue(), media_type='audio/wav')
    except Exception as e:
        print("Merge error:")
        print(e)
