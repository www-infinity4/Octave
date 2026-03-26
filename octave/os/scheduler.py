from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class Priority(Enum):
    PRESTISSIMO = 1  # fastest
    PRESTO = 2
    ALLEGRO = 3
    MODERATO = 4
    ANDANTE = 5
    ADAGIO = 6
    LARGO = 7  # slowest


@dataclass
class Process:
    id: str
    name: str
    priority: Priority
    beats_remaining: float
    handler: Callable
    metadata: dict = field(default_factory=dict)


class Scheduler:
    def __init__(self, bpm: float = 120.0):
        self._bpm = bpm
        self._processes: dict = {}  # id -> Process

    @property
    def beat_duration(self) -> float:
        return 60.0 / self._bpm

    def register(self, process: Process) -> str:
        self._processes[process.id] = process
        return process.id

    def unregister(self, process_id: str) -> None:
        self._processes.pop(process_id, None)

    def tick(self, beats: float = 1.0) -> None:
        for process in list(self._processes.values()):
            process.beats_remaining -= beats
            if process.beats_remaining <= 0:
                process.handler(process)
                self._processes.pop(process.id, None)

    def set_tempo(self, bpm: float) -> None:
        self._bpm = bpm

    @property
    def running_processes(self) -> list:
        return list(self._processes.keys())
