from dataclasses import dataclass, field
from enum import Enum
import math

class NoteName(Enum):
    C = 0
    D = 2
    E = 4
    F = 5
    G = 7
    A = 9
    B = 11

class Accidental(Enum):
    FLAT = -1
    NATURAL = 0
    SHARP = 1

@dataclass
class Note:
    name: NoteName
    accidental: Accidental = Accidental.NATURAL
    octave: int = 4

    @property
    def midi_number(self) -> int:
        return (self.octave + 1) * 12 + self.name.value + self.accidental.value

    @property
    def frequency(self) -> float:
        return 440.0 * (2 ** ((self.midi_number - 69) / 12))

    def __str__(self) -> str:
        acc = "#" if self.accidental == Accidental.SHARP else ("b" if self.accidental == Accidental.FLAT else "")
        return f"{self.name.name}{acc}{self.octave}"

    @classmethod
    def from_str(cls, s: str) -> "Note":
        i = 0
        note_char = s[i].upper()
        i += 1
        name = NoteName[note_char]
        accidental = Accidental.NATURAL
        if i < len(s) and s[i] == '#':
            accidental = Accidental.SHARP
            i += 1
        elif i < len(s) and s[i] == 'b':
            accidental = Accidental.FLAT
            i += 1
        octave = int(s[i:]) if i < len(s) else 4
        return cls(name=name, accidental=accidental, octave=octave)

    @classmethod
    def from_midi(cls, n: int) -> "Note":
        octave = (n // 12) - 1
        semitone = n % 12
        semitone_map = {
            0: (NoteName.C, Accidental.NATURAL),
            1: (NoteName.C, Accidental.SHARP),
            2: (NoteName.D, Accidental.NATURAL),
            3: (NoteName.D, Accidental.SHARP),
            4: (NoteName.E, Accidental.NATURAL),
            5: (NoteName.F, Accidental.NATURAL),
            6: (NoteName.F, Accidental.SHARP),
            7: (NoteName.G, Accidental.NATURAL),
            8: (NoteName.G, Accidental.SHARP),
            9: (NoteName.A, Accidental.NATURAL),
            10: (NoteName.A, Accidental.SHARP),
            11: (NoteName.B, Accidental.NATURAL),
        }
        name, accidental = semitone_map[semitone]
        return cls(name=name, accidental=accidental, octave=octave)


@dataclass
class Chord:
    notes: list  # list[Note]

    @property
    def frequencies(self) -> list:
        return [note.frequency for note in self.notes]
