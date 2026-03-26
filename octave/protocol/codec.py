import json
import struct

from octave.core.notes import Note, NoteName, Accidental, Chord
from octave.core.signals import Signal, SignalType
from octave.protocol.message import OctaveMessage


class OctaveCodec:
    def encode(self, message: OctaveMessage) -> bytes:
        return message.to_bytes()

    def decode(self, data: bytes) -> OctaveMessage:
        return OctaveMessage.from_bytes(data)

    def encode_chord(self, chord: Chord) -> bytes:
        midi_numbers = [note.midi_number for note in chord.notes]
        result = bytes([len(midi_numbers)]) + bytes(midi_numbers)
        return result

    def decode_chord(self, data: bytes) -> Chord:
        count = data[0]
        notes = []
        for i in range(count):
            midi = data[1 + i]
            notes.append(Note.from_midi(midi))
        return Chord(notes=notes)

    def encode_signal(self, signal: Signal) -> bytes:
        return signal.to_bytes()

    def decode_signal(self, data: bytes) -> Signal:
        return Signal.from_bytes(data)
