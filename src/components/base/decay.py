from dataclasses import dataclass


@dataclass(slots=True)
class DecayComponent:
    frames_till_decay: int
