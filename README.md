# Octave

Octave is an operating system, it's also a token mint. It's a musical based operating system with sharps flats and notes and dynamics the way it communicates with other machines.

---

## Overview

Octave is a Python-based musical operating system and token mint. Every concept — from inter-process scheduling to inter-machine communication and asset minting — is expressed through the vocabulary of music: notes, accidentals, octaves, dynamics, chords, and tempo. Octave uses only the Python standard library.

---

## Architecture

```
octave/
  core/
    notes.py      # Note, Accidental, NoteName, Chord primitives
    dynamics.py   # Dynamic levels (ppp → fff) and DynamicChange
    signals.py    # Signal, SignalType, SignalBus (pub/sub)
  token/
    token.py      # OctaveToken dataclass and serialisation
    mint.py       # TokenMint — mint, burn, transfer, policy enforcement
  os/
    kernel.py     # OctaveKernel — lifecycle, scheduler, signal bus
    scheduler.py  # BPM-based Process scheduler
  protocol/
    message.py    # OctaveMessage — typed network messages
    codec.py      # OctaveCodec — encode/decode messages, chords, signals
tests/            # pytest suite (30 tests)
pyproject.toml
```

---

## Core Concepts

### Notes
A `Note` is defined by a `NoteName` (C, D, E, F, G, A, B), an `Accidental` (FLAT, NATURAL, SHARP), and an octave number. It exposes:
- `midi_number` — standard MIDI integer (C4 = 60, A4 = 69)
- `frequency` — Hz derived from equal temperament (A4 = 440 Hz)
- `from_str("C#4")` / `from_midi(69)` factory methods

A `Chord` wraps a list of `Note` objects and exposes their combined frequencies.

### Dynamics
`Dynamic` is a velocity-mapped enum covering the standard dynamic range:

| Symbol | MIDI velocity |
|--------|--------------|
| ppp    | 16           |
| pp     | 32           |
| p      | 48           |
| mp     | 64           |
| mf     | 80           |
| f      | 96           |
| ff     | 112          |
| fff    | 127          |

`Dynamic.from_velocity(v)` snaps an arbitrary velocity to the nearest level.

### Signals
`Signal` is a typed message carrying a `SignalType` (NOTE_ON, NOTE_OFF, CHORD, DYNAMIC_CHANGE, TEMPO_CHANGE, REST, PING, PONG), a payload dict, timestamp, source, and target. Signals serialise to/from JSON bytes.

`SignalBus` is a lightweight pub/sub broker — nodes subscribe with a string ID and a handler callable; signals are routed by target or broadcast with `target="*"`.

### Scheduler & BPM
`Scheduler` manages `Process` objects measured in *beats*, not wall-clock seconds. Calling `tick(beats)` advances all processes; those whose `beats_remaining` reaches zero fire their handler and are removed. Tempo is set with `set_tempo(bpm)`.

`Priority` is expressed as musical tempo markings (PRESTISSIMO → LARGO), from fastest (1) to slowest (7).

---

## Quick Start

```python
from octave import OctaveKernel, Note, TokenMint, Dynamic
from octave.core.notes import NoteName, Accidental
from octave.core.signals import SignalType
from octave.os.scheduler import Process, Priority

# Boot the kernel at 140 BPM
kernel = OctaveKernel(node_id="main", bpm=140.0)
kernel.start()
print(kernel.state)  # KernelState.PLAYING

# Listen for broadcast signals
kernel.signal_bus.subscribe("listener", lambda sig: print(f"Received: {sig.type}"))

# Schedule a one-shot process to fire after 4 beats
def on_fire(process):
    print(f"Process {process.name} fired!")

kernel.scheduler.register(Process(
    id="p1", name="fanfare",
    priority=Priority.ALLEGRO,
    beats_remaining=4.0,
    handler=on_fire,
))

kernel.tick(4.0)  # advances the scheduler — process fires here

# Mint a token on A4 at mezzo-forte
a4 = Note(NoteName.A, Accidental.NATURAL, 4)
token = kernel.token_mint.mint(a4, Dynamic.mf, creator="alice")
print(token.value)  # 69 * 80 = 5520
```

---

## Token Mint

`TokenMint` creates, burns, and transfers `OctaveToken` objects. Each token embeds a `Note` and a `Dynamic`, giving it a musical identity and a numeric `value = midi_number × velocity`.

```python
from octave.token.mint import TokenMint, MintPolicy
from octave.core.dynamics import Dynamic

policy = MintPolicy(
    max_supply=10_000,       # hard cap
    min_dynamic=Dynamic.mp,  # no tokens below mp (velocity 64)
)
mint = TokenMint("node-1", policy=policy)

note = Note.from_str("G#5")
token = mint.mint(note, Dynamic.ff, creator="bob")
print(token.to_dict())

# Lifecycle
mint.transfer(token.id, "carol")
mint.burn(token.id)

# Analytics
print(mint.supply_by_note())   # {"G": 1, ...}
print(mint.total_supply())     # burned tokens excluded
```

Tokens serialise to/from plain dicts (JSON-safe) via `to_dict()` / `OctaveToken.from_dict()`.

---

## Inter-Machine Protocol

Machines communicate using `OctaveMessage`, typed with `MessageType` (HANDSHAKE, DATA, ACK, NACK, HEARTBEAT, CHORD_SYNC, TOKEN_TRANSFER). Every message carries a `Note` as its cryptographic *signature* and a `Dynamic` indicating urgency.

```python
from octave.protocol.codec import OctaveCodec
from octave.protocol.message import OctaveMessage, MessageType
from octave.core.notes import Note, NoteName, Accidental
from octave.core.dynamics import Dynamic

codec = OctaveCodec()

msg = OctaveMessage(
    type=MessageType.HANDSHAKE,
    sender="node-1",
    recipient="node-2",
    sequence=1,
    payload={"version": "0.1.0"},
    signature=Note(NoteName.A, Accidental.NATURAL, 4),
    dynamic=Dynamic.mf,
)

wire = codec.encode(msg)          # bytes
restored = codec.decode(wire)     # OctaveMessage

# Chord encoding (compact binary: 1 byte count + N midi bytes)
from octave.core.notes import Chord
chord = Chord(notes=[Note.from_str(n) for n in ["C4", "E4", "G4"]])
chord_bytes = codec.encode_chord(chord)
decoded_chord = codec.decode_chord(chord_bytes)
```
<script src="https://www-infinity4.github.io/Mint-For-Infinity/infinity-wallet-menu.js" defer></script>
