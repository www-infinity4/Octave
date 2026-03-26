import pytest
from octave.core.notes import Note, NoteName, Accidental
from octave.core.dynamics import Dynamic
from octave.token.mint import TokenMint, MintPolicy
from octave.token.token import TokenState


def test_mint_token():
    mint = TokenMint("node-1")
    note = Note(NoteName.A, Accidental.NATURAL, 4)
    token = mint.mint(note, Dynamic.mf, "alice")
    assert token.state == TokenState.MINTED
    assert token.note == note
    assert token.dynamic == Dynamic.mf
    assert token.creator == "alice"


def test_burn_token():
    mint = TokenMint("node-1")
    note = Note(NoteName.C, Accidental.NATURAL, 4)
    token = mint.mint(note, Dynamic.f, "bob")
    burned = mint.burn(token.id)
    assert burned.state == TokenState.BURNED
    assert mint.total_supply() == 0


def test_transfer_token():
    mint = TokenMint("node-1")
    note = Note(NoteName.G, Accidental.NATURAL, 4)
    token = mint.mint(note, Dynamic.mp, "carol")
    transferred = mint.transfer(token.id, "dave")
    assert transferred.creator == "dave"
    assert transferred.state == TokenState.TRANSFERRED


def test_policy_max_supply():
    policy = MintPolicy(max_supply=2)
    mint = TokenMint("node-1", policy=policy)
    note = Note(NoteName.A, Accidental.NATURAL, 4)
    mint.mint(note, Dynamic.mf, "alice")
    mint.mint(note, Dynamic.mf, "alice")
    with pytest.raises(ValueError, match="Max supply"):
        mint.mint(note, Dynamic.mf, "alice")


def test_policy_min_dynamic():
    policy = MintPolicy(min_dynamic=Dynamic.mf)
    mint = TokenMint("node-1", policy=policy)
    note = Note(NoteName.A, Accidental.NATURAL, 4)
    with pytest.raises(ValueError, match="below minimum"):
        mint.mint(note, Dynamic.p, "alice")


def test_supply_by_note():
    mint = TokenMint("node-1")
    mint.mint(Note(NoteName.A, Accidental.NATURAL, 4), Dynamic.mf, "alice")
    mint.mint(Note(NoteName.A, Accidental.NATURAL, 4), Dynamic.f, "bob")
    mint.mint(Note(NoteName.C, Accidental.NATURAL, 4), Dynamic.ff, "carol")
    counts = mint.supply_by_note()
    assert counts["A"] == 2
    assert counts["C"] == 1


def test_list_tokens_by_state():
    mint = TokenMint("node-1")
    note = Note(NoteName.A, Accidental.NATURAL, 4)
    t1 = mint.mint(note, Dynamic.mf, "alice")
    t2 = mint.mint(note, Dynamic.f, "bob")
    mint.burn(t2.id)
    active = mint.list_tokens(state=TokenState.MINTED)
    burned = mint.list_tokens(state=TokenState.BURNED)
    assert len(active) == 1
    assert len(burned) == 1


def test_token_value():
    mint = TokenMint("node-1")
    note = Note(NoteName.A, Accidental.NATURAL, 4)  # MIDI=69
    token = mint.mint(note, Dynamic.mf, "alice")  # Dynamic.mf=80
    assert token.value == 69 * 80


def test_token_serialization():
    mint = TokenMint("node-1")
    note = Note(NoteName.A, Accidental.NATURAL, 4)
    token = mint.mint(note, Dynamic.mf, "alice")
    d = token.to_dict()
    from octave.token.token import OctaveToken
    restored = OctaveToken.from_dict(d)
    assert restored.id == token.id
    assert restored.note.name == token.note.name
    assert restored.dynamic == token.dynamic
