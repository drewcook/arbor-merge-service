import os

from audio.nft_storage import NFTStorage
from audio.audio import load_audio_folder, merge_audio
from audio import __version__
from pydub import AudioSegment

def test_version():
    assert __version__ == '0.1.0'


def test_audio():
    wavs = load_audio_folder("downloads")
    out = "output.wav"
    for wav in wavs:
        assert isinstance(wav, AudioSegment)
    merge_audio(wavs)
    
