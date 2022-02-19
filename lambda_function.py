import logging
from typing import List, Dict, Any
import os
import time
import json
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


DOWNLOAD_PATH = "downloads/"

def lambda_handler(event, context):
    try:
        req = json.loads(event['body'])
        nfts: NFTStorage = NFTStorage(os.getenv("NFT_STORAGE_API"))
        [nfts.download(cid) for cid in req["sample_cids"]]
        audio_segments: Dict[str, Any] = load_audio_folder(DOWNLOAD_PATH)
        temp_file = f"tmp_{time.time()}_output.wav"
        merge_audio(list(audio_segments.values()), temp_file)
        with open(temp_file, "r") as f:
            cid = nfts.upload(f.buffer)
            _logger.info(f"Merge result: {cid}")
        os.remove(temp_file)
        return {'statusCode': 200, 'body': {"success": True, "cid": cid}}
    except Exception as e:
        _logger.error(f"Failed to merge audio samples... {e}")
        return {'statusCode': 500, 'body': {'success': False}}
    finally:
        for d in os.listdir(DOWNLOAD_PATH):
            if d.split(".")[0] in req["sample_cids"]:
                os.remove(f"{DOWNLOAD_PATH}{d}")
