from dataclasses import dataclass, field
from enum import Enum
import json
import time
from typing import Callable

class SignalType(Enum):
    NOTE_ON = "NOTE_ON"
    NOTE_OFF = "NOTE_OFF"
    CHORD = "CHORD"
    DYNAMIC_CHANGE = "DYNAMIC_CHANGE"
    TEMPO_CHANGE = "TEMPO_CHANGE"
    REST = "REST"
    PING = "PING"
    PONG = "PONG"


@dataclass
class Signal:
    type: SignalType
    payload: dict
    timestamp: float = 0.0
    source: str = ""
    target: str = ""

    def to_bytes(self) -> bytes:
        data = {
            "type": self.type.value,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "source": self.source,
            "target": self.target,
        }
        return json.dumps(data).encode("utf-8")

    @classmethod
    def from_bytes(cls, b: bytes) -> "Signal":
        data = json.loads(b.decode("utf-8"))
        return cls(
            type=SignalType(data["type"]),
            payload=data["payload"],
            timestamp=data.get("timestamp", 0.0),
            source=data.get("source", ""),
            target=data.get("target", ""),
        )


class SignalBus:
    def __init__(self):
        self._handlers: dict = {}

    def subscribe(self, node_id: str, handler: Callable) -> None:
        self._handlers[node_id] = handler

    def unsubscribe(self, node_id: str) -> None:
        self._handlers.pop(node_id, None)

    def publish(self, signal: Signal) -> None:
        if signal.target == "*":
            self.broadcast(signal)
        elif signal.target in self._handlers:
            self._handlers[signal.target](signal)

    def broadcast(self, signal: Signal) -> None:
        for handler in self._handlers.values():
            handler(signal)
