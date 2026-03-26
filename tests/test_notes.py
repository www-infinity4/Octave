import math
import pytest
from octave.core.notes import Note, NoteName, Accidental, Chord


def test_note_midi_number():
    c4 = Note(NoteName.C, Accidental.NATURAL, 4)
    assert c4.midi_number == 60

    a4 = Note(NoteName.A, Accidental.NATURAL, 4)
    assert a4.midi_number == 69

    cs4 = Note(NoteName.C, Accidental.SHARP, 4)
    assert cs4.midi_number == 61

    bb3 = Note(NoteName.B, Accidental.FLAT, 3)
    assert bb3.midi_number == 58  # B3=59, Bb3=58


def test_note_frequency():
    a4 = Note(NoteName.A, Accidental.NATURAL, 4)
    assert abs(a4.frequency - 440.0) < 0.01

    c4 = Note(NoteName.C, Accidental.NATURAL, 4)
    expected = 440.0 * (2 ** ((60 - 69) / 12))
    assert abs(c4.frequency - expected) < 0.01


def test_note_str():
    assert str(Note(NoteName.C, Accidental.SHARP, 4)) == "C#4"
    assert str(Note(NoteName.B, Accidental.FLAT, 3)) == "Bb3"
    assert str(Note(NoteName.D, Accidental.NATURAL, 4)) == "D4"


def test_note_from_str():
    n = Note.from_str("C#4")
    assert n.name == NoteName.C
    assert n.accidental == Accidental.SHARP
    assert n.octave == 4

    n2 = Note.from_str("Bb3")
    assert n2.name == NoteName.B
    assert n2.accidental == Accidental.FLAT
    assert n2.octave == 3

    n3 = Note.from_str("D4")
    assert n3.name == NoteName.D
    assert n3.accidental == Accidental.NATURAL
    assert n3.octave == 4


def test_note_from_midi():
    note = Note.from_midi(60)
    assert note.name == NoteName.C
    assert note.accidental == Accidental.NATURAL
    assert note.octave == 4

    note_a4 = Note.from_midi(69)
    assert note_a4.name == NoteName.A
    assert note_a4.octave == 4


def test_chord():
    notes = [
        Note(NoteName.C, Accidental.NATURAL, 4),
        Note(NoteName.E, Accidental.NATURAL, 4),
        Note(NoteName.G, Accidental.NATURAL, 4),
    ]
    chord = Chord(notes=notes)
    freqs = chord.frequencies
    assert len(freqs) == 3
    assert all(f > 0 for f in freqs)
