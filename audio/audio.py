from pydub import AudioSegment
from pydub.playback import play
from typing import List 
import os

def load_audio_folder(path: str) -> List[AudioSegment]:
    return [AudioSegment.from_file(file=f"{path}/{file}") for file in os.listdir(path)]

def merge_audio(wavs: List[AudioSegment], out: str = "output.wav"):
    assert len(wavs) > 1
    init_seg = wavs[0]
    for segment in wavs[1:]:
        init_seg = init_seg.overlay(segment)
    init_seg.export("output.wav", format="wav")

