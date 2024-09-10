from dataclasses import dataclass
from pythonosc.osc_message import OscMessage

@dataclass
class SynthDefMessage:
    content: str
    name: str
    load_msg: OscMessage

@dataclass
class Sample:
    path: str
    sample_pack: str
    buffer_index: int
    category: str
    tone_index: int

    def as_args(self) -> list[str | float | int]:
        # ("/load_sample", [wav_file, "testsamples", 100, "bd"])
        return [self.path, self.sample_pack, self.buffer_index, self.category, self.tone_index]

@dataclass
class SampleMessage:
    sample: Sample
    load_msg: OscMessage
