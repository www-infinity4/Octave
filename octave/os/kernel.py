from enum import Enum
import time

from octave.core.signals import Signal, SignalBus, SignalType
from octave.os.scheduler import Scheduler
from octave.token.mint import TokenMint
from octave.core.notes import Note, NoteName


class KernelState(Enum):
    SILENT = "SILENT"
    TUNING = "TUNING"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    FERMATA = "FERMATA"


class OctaveKernel:
    def __init__(self, node_id: str, bpm: float = 120.0):
        self.node_id = node_id
        self._state = KernelState.SILENT
        self.scheduler = Scheduler(bpm=bpm)
        self.signal_bus = SignalBus()
        self.token_mint = TokenMint(node_id=node_id)

    @property
    def state(self) -> KernelState:
        return self._state

    def start(self) -> None:
        self._state = KernelState.TUNING
        self._state = KernelState.PLAYING
        self.emit(Signal(
            type=SignalType.PING,
            payload={"node_id": self.node_id, "action": "start"},
            timestamp=time.time(),
            source=self.node_id,
            target="*",
        ))

    def stop(self) -> None:
        self._state = KernelState.SILENT
        self.emit(Signal(
            type=SignalType.NOTE_OFF,
            payload={"node_id": self.node_id, "action": "stop"},
            timestamp=time.time(),
            source=self.node_id,
            target="*",
        ))

    def pause(self) -> None:
        self._state = KernelState.PAUSED

    def resume(self) -> None:
        self._state = KernelState.PLAYING

    def halt(self, reason: str = "") -> None:
        self._state = KernelState.FERMATA

    def tick(self, beats: float = 1.0) -> None:
        if self._state == KernelState.PLAYING:
            self.scheduler.tick(beats)

    def emit(self, signal: Signal) -> None:
        self.signal_bus.publish(signal)
