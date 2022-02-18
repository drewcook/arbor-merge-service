import os
from audio.nft_storage import NFTStorage
from dotenv import load_dotenv
load_dotenv()


def get_storage():
    return NFTStorage(os.getenv("NFT_STORAGE_API"))


def test_nft_storage():
    nft = get_storage()
    assert isinstance(nft, NFTStorage)
    [nft.delete(cid) for cid in nft.list()]
    cids = {nft.upload(test_data): test_data for test_data in [
        'test', {'test': 'test'}]}
    for cid in cids:
        assert isinstance(cid, str) or isinstance(cid, dict)
    assert len(nft.list()) == len(cids)
    for cid in nft.list():
        assert nft.get_nft(cid)['cid'] == cid
        nft.delete(cid)
    assert len(nft.list()) == 0
