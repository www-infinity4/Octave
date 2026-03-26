import pytest
from octave.core.dynamics import Dynamic, DynamicChange


def test_dynamic_values():
    assert Dynamic.ppp.value == 16
    assert Dynamic.fff.value == 127
    assert Dynamic.mf.value == 80


def test_dynamic_label():
    assert Dynamic.ppp.label == "ppp"
    assert Dynamic.ff.label == "ff"


def test_from_velocity():
    d = Dynamic.from_velocity(64)
    assert d == Dynamic.mp

    d2 = Dynamic.from_velocity(0)
    assert d2 == Dynamic.ppp

    d3 = Dynamic.from_velocity(127)
    assert d3 == Dynamic.fff


def test_from_label():
    assert Dynamic.from_label("ppp") == Dynamic.ppp
    assert Dynamic.from_label("ff") == Dynamic.ff
    assert Dynamic.from_label("mf") == Dynamic.mf


def test_dynamic_change():
    dc = DynamicChange(from_dynamic=Dynamic.p, to_dynamic=Dynamic.f, beats=4.0)
    assert dc.from_dynamic == Dynamic.p
    assert dc.to_dynamic == Dynamic.f
    assert dc.beats == 4.0
