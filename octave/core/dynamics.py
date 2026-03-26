from dataclasses import dataclass
from enum import Enum

class Dynamic(Enum):
    ppp = 16
    pp = 32
    p = 48
    mp = 64
    mf = 80
    f = 96
    ff = 112
    fff = 127

    @property
    def label(self) -> str:
        return self.name

    @classmethod
    def from_velocity(cls, v: int) -> "Dynamic":
        return min(cls, key=lambda d: abs(d.value - v))

    @classmethod
    def from_label(cls, s: str) -> "Dynamic":
        return cls[s]


@dataclass
class DynamicChange:
    from_dynamic: Dynamic
    to_dynamic: Dynamic
    beats: float
