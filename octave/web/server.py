"""Simple HTTP server that serves the Octave project website at the root /."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

_INDEX_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Octave OS</title>
  <style>
    body { font-family: sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; }
    h1 { font-size: 2.5rem; margin-bottom: 0.25rem; }
    h2 { color: #555; margin-top: 2rem; }
    code { background: #f4f4f4; padding: 0.15rem 0.4rem; border-radius: 3px; }
    pre { background: #f4f4f4; padding: 1rem; overflow-x: auto; border-radius: 4px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 0.5rem 0.75rem; text-align: left; }
    th { background: #f0f0f0; }
  </style>
</head>
<body>
  <h1>🎵 Octave OS</h1>
  <p>
    A musical operating system and token mint. Every concept — from inter-process
    scheduling to inter-machine communication and asset minting — is expressed
    through the vocabulary of music: notes, accidentals, octaves, dynamics, chords,
    and tempo.
  </p>

  <h2>Quick Start</h2>
  <pre><code>from octave import OctaveKernel, Note, TokenMint, Dynamic
from octave.core.notes import NoteName, Accidental

kernel = OctaveKernel(node_id="main", bpm=140.0)
kernel.start()                       # KernelState.PLAYING

a4 = Note(NoteName.A, Accidental.NATURAL, 4)
token = kernel.token_mint.mint(a4, Dynamic.mf, creator="alice")
print(token.value)                   # 69 * 80 = 5520</code></pre>

  <h2>Architecture</h2>
  <table>
    <tr><th>Module</th><th>Description</th></tr>
    <tr><td><code>octave.core.notes</code></td><td>Note, Chord, MIDI number &amp; Hz frequency</td></tr>
    <tr><td><code>octave.core.dynamics</code></td><td>Dynamic levels (ppp → fff) &amp; velocity mapping</td></tr>
    <tr><td><code>octave.core.signals</code></td><td>Signal, SignalBus pub/sub router</td></tr>
    <tr><td><code>octave.os.kernel</code></td><td>OctaveKernel lifecycle &amp; orchestration</td></tr>
    <tr><td><code>octave.os.scheduler</code></td><td>BPM-driven process scheduler</td></tr>
    <tr><td><code>octave.protocol.message</code></td><td>OctaveMessage — typed network messages</td></tr>
    <tr><td><code>octave.protocol.codec</code></td><td>OctaveCodec — encode/decode messages &amp; chords</td></tr>
    <tr><td><code>octave.token.mint</code></td><td>TokenMint — mint, burn, transfer tokens</td></tr>
  </table>
</body>
</html>
"""


class _OctaveHandler(BaseHTTPRequestHandler):
    """Request handler that serves the Octave website at every path."""

    def do_GET(self) -> None:
        body = _INDEX_HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:  # suppress default stderr logging
        pass


class OctaveWebServer:
    """HTTP server that serves the Octave project website at the root ``/``.

    Parameters
    ----------
    host:
        Hostname or IP address to bind to (default ``"localhost"``).
    port:
        TCP port to listen on (default ``8080``).

    Examples
    --------
    >>> server = OctaveWebServer(port=8080)
    >>> server.start()   # non-blocking — runs in a background thread
    >>> server.stop()
    """

    def __init__(self, host: str = "localhost", port: int = 8080) -> None:
        self.host = host
        self.port = port
        self._httpd: HTTPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def address(self) -> tuple[str, int]:
        """Return the ``(host, port)`` tuple the server is bound to."""
        return (self.host, self.port)

    def start(self) -> None:
        """Start the server in a background daemon thread."""
        self._httpd = HTTPServer((self.host, self.port), _OctaveHandler)
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Shut down the server and wait for the background thread to exit."""
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd = None
        if self._thread is not None:
            self._thread.join()
            self._thread = None

    def __enter__(self) -> "OctaveWebServer":
        self.start()
        return self

    def __exit__(self, *_) -> None:
        self.stop()
