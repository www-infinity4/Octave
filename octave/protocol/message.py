from dataclasses import dataclass, field
from enum import Enum
import json
import time

from octave.core.notes import Note, NoteName, Accidental
from octave.core.dynamics import Dynamic


class MessageType(Enum):
    HANDSHAKE = "HANDSHAKE"
    DATA = "DATA"
    ACK = "ACK"
    NACK = "NACK"
    HEARTBEAT = "HEARTBEAT"
    CHORD_SYNC = "CHORD_SYNC"
    TOKEN_TRANSFER = "TOKEN_TRANSFER"


@dataclass
class OctaveMessage:
    type: MessageType
    sender: str
    recipient: str
    sequence: int
    payload: dict
    signature: Note
    dynamic: Dynamic
    timestamp: float = field(default_factory=time.time)

    def to_bytes(self) -> bytes:
        data = {
            "type": self.type.value,
            "sender": self.sender,
            "recipient": self.recipient,
            "sequence": self.sequence,
            "payload": self.payload,
            "signature": {
                "name": self.signature.name.name,
                "accidental": self.signature.accidental.name,
                "octave": self.signature.octave,
            },
            "dynamic": self.dynamic.name,
            "timestamp": self.timestamp,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def from_bytes(cls, b: bytes) -> "OctaveMessage":
        data = json.loads(b.decode("utf-8"))
        sig_data = data["signature"]
        signature = Note(
            name=NoteName[sig_data["name"]],
            accidental=Accidental[sig_data["accidental"]],
            octave=sig_data["octave"],
        )
        return cls(
            type=MessageType(data["type"]),
            sender=data["sender"],
            recipient=data["recipient"],
            sequence=data["sequence"],
            payload=data["payload"],
            signature=signature,
            dynamic=Dynamic[data["dynamic"]],
            timestamp=data.get("timestamp", 0.0),
        )
