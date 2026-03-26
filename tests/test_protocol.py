import pytest
from octave.core.notes import Note, NoteName, Accidental, Chord
from octave.core.dynamics import Dynamic
from octave.core.signals import Signal, SignalType
from octave.protocol.message import OctaveMessage, MessageType
from octave.protocol.codec import OctaveCodec


def make_message():
    sig = Note(NoteName.A, Accidental.NATURAL, 4)
    return OctaveMessage(
        type=MessageType.HANDSHAKE,
        sender="node-1",
        recipient="node-2",
        sequence=1,
        payload={"hello": "world"},
        signature=sig,
        dynamic=Dynamic.mf,
        timestamp=1000.0,
    )


def test_message_serialization():
    msg = make_message()
    b = msg.to_bytes()
    restored = OctaveMessage.from_bytes(b)
    assert restored.type == MessageType.HANDSHAKE
    assert restored.sender == "node-1"
    assert restored.recipient == "node-2"
    assert restored.sequence == 1
    assert restored.payload == {"hello": "world"}
    assert restored.signature.name == NoteName.A
    assert restored.dynamic == Dynamic.mf


def test_codec_encode_decode():
    codec = OctaveCodec()
    msg = make_message()
    encoded = codec.encode(msg)
    decoded = codec.decode(encoded)
    assert decoded.type == msg.type
    assert decoded.sender == msg.sender
    assert decoded.payload == msg.payload


def test_codec_chord():
    codec = OctaveCodec()
    chord = Chord(notes=[
        Note(NoteName.C, Accidental.NATURAL, 4),
        Note(NoteName.E, Accidental.NATURAL, 4),
        Note(NoteName.G, Accidental.NATURAL, 4),
    ])
    encoded = codec.encode_chord(chord)
    decoded = codec.decode_chord(encoded)
    assert len(decoded.notes) == 3
    assert decoded.notes[0].name == NoteName.C
    assert decoded.notes[1].name == NoteName.E
    assert decoded.notes[2].name == NoteName.G


def test_codec_signal():
    codec = OctaveCodec()
    signal = Signal(
        type=SignalType.PING,
        payload={"msg": "hello"},
        timestamp=123.0,
        source="node-1",
        target="node-2",
    )
    encoded = codec.encode_signal(signal)
    decoded = codec.decode_signal(encoded)
    assert decoded.type == SignalType.PING
    assert decoded.payload == {"msg": "hello"}
    assert decoded.source == "node-1"
