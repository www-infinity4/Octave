from dataclasses import dataclass, field
import time
import uuid

from octave.core.notes import Note, NoteName
from octave.core.dynamics import Dynamic
from octave.token.token import OctaveToken, TokenState


@dataclass
class MintPolicy:
    max_supply: int = 1_000_000
    min_dynamic: Dynamic = Dynamic.pp
    allowed_notes: list = field(default_factory=lambda: list(NoteName))


class TokenMint:
    def __init__(self, node_id: str, policy: MintPolicy = None):
        self.node_id = node_id
        self.policy = policy or MintPolicy()
        self._tokens: dict = {}

    def mint(self, note: Note, dynamic: Dynamic, creator: str, metadata: dict = None) -> OctaveToken:
        if self.total_supply() >= self.policy.max_supply:
            raise ValueError(f"Max supply of {self.policy.max_supply} reached")
        if dynamic.value < self.policy.min_dynamic.value:
            raise ValueError(f"Dynamic {dynamic.label} is below minimum {self.policy.min_dynamic.label}")
        if note.name not in self.policy.allowed_notes:
            raise ValueError(f"Note {note.name} is not in allowed notes")

        token = OctaveToken(
            id=str(uuid.uuid4()),
            note=note,
            dynamic=dynamic,
            octave_number=note.octave,
            creator=creator,
            state=TokenState.MINTED,
            created_at=time.time(),
            metadata=metadata or {},
        )
        self._tokens[token.id] = token
        return token

    def burn(self, token_id: str) -> OctaveToken:
        token = self.get_token(token_id)
        token.state = TokenState.BURNED
        return token

    def transfer(self, token_id: str, new_owner: str) -> OctaveToken:
        token = self.get_token(token_id)
        token.creator = new_owner
        token.state = TokenState.TRANSFERRED
        return token

    def get_token(self, token_id: str) -> OctaveToken:
        if token_id not in self._tokens:
            raise KeyError(f"Token {token_id} not found")
        return self._tokens[token_id]

    def list_tokens(self, state: TokenState = None) -> list:
        tokens = list(self._tokens.values())
        if state is not None:
            tokens = [t for t in tokens if t.state == state]
        return tokens

    def total_supply(self) -> int:
        return sum(1 for t in self._tokens.values() if t.state != TokenState.BURNED)

    def supply_by_note(self) -> dict:
        counts = {}
        for token in self._tokens.values():
            if token.state != TokenState.BURNED:
                key = token.note.name.name
                counts[key] = counts.get(key, 0) + 1
        return counts
