import pytest
from octave.os.scheduler import Scheduler, Process, Priority
import uuid


def make_process(beats_remaining=2.0, priority=Priority.MODERATO):
    results = []
    def handler(p):
        results.append(p.id)
    pid = str(uuid.uuid4())
    p = Process(
        id=pid,
        name="test-process",
        priority=priority,
        beats_remaining=beats_remaining,
        handler=handler,
    )
    return p, results


def test_register_unregister():
    s = Scheduler()
    p, _ = make_process()
    s.register(p)
    assert p.id in s.running_processes
    s.unregister(p.id)
    assert p.id not in s.running_processes


def test_tick_runs_process():
    s = Scheduler(bpm=120.0)
    p, results = make_process(beats_remaining=2.0)
    s.register(p)
    s.tick(1.0)
    assert p.id in s.running_processes  # not yet done
    s.tick(1.0)
    assert p.id not in s.running_processes  # should have run
    assert len(results) == 1


def test_priority_enum():
    assert Priority.PRESTISSIMO.value < Priority.LARGO.value
    assert Priority.PRESTO.value == 2


def test_beat_duration():
    s = Scheduler(bpm=120.0)
    assert abs(s.beat_duration - 0.5) < 0.001


def test_set_tempo():
    s = Scheduler(bpm=120.0)
    s.set_tempo(60.0)
    assert abs(s.beat_duration - 1.0) < 0.001


def test_multiple_processes():
    s = Scheduler()
    results = []

    def make_handler(name):
        def handler(p):
            results.append(name)
        return handler

    p1 = Process(id="p1", name="fast", priority=Priority.PRESTISSIMO, beats_remaining=1.0, handler=make_handler("fast"))
    p2 = Process(id="p2", name="slow", priority=Priority.LARGO, beats_remaining=3.0, handler=make_handler("slow"))
    s.register(p1)
    s.register(p2)
    s.tick(1.0)
    assert "fast" in results
    assert "slow" not in results
    s.tick(2.0)
    assert "slow" in results
