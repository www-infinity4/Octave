from dataclasses import dataclass, field
from enum import Enum
import time

from octave.core.notes import Note, NoteName, Accidental
from octave.core.dynamics import Dynamic


class TokenState(Enum):
    MINTED = "MINTED"
    ACTIVE = "ACTIVE"
    TRANSFERRED = "TRANSFERRED"
    BURNED = "BURNED"


@dataclass
class OctaveToken:
    id: str
    note: Note
    dynamic: Dynamic
    octave_number: int
    creator: str
    state: TokenState
    created_at: float
    metadata: dict = field(default_factory=dict)

    @property
    def frequency(self) -> float:
        return self.note.frequency

    @property
    def value(self) -> int:
        return self.note.midi_number * self.dynamic.value

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "note": {
                "name": self.note.name.name,
                "accidental": self.note.accidental.name,
                "octave": self.note.octave,
            },
            "dynamic": self.dynamic.name,
            "octave_number": self.octave_number,
            "creator": self.creator,
            "state": self.state.value,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "OctaveToken":
        note_data = d["note"]
        note = Note(
            name=NoteName[note_data["name"]],
            accidental=Accidental[note_data["accidental"]],
            octave=note_data["octave"],
        )
        return cls(
            id=d["id"],
            note=note,
            dynamic=Dynamic[d["dynamic"]],
            octave_number=d["octave_number"],
            creator=d["creator"],
            state=TokenState(d["state"]),
            created_at=d["created_at"],
            metadata=d.get("metadata", {}),
        )
