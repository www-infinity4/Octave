"""Tests for octave.web.server — OctaveWebServer."""

import urllib.request
import pytest
from octave.web.server import OctaveWebServer


def _free_port() -> int:
    """Return an available TCP port on localhost."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_server_serves_root():
    port = _free_port()
    server = OctaveWebServer(host="127.0.0.1", port=port)
    server.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/") as resp:
            assert resp.status == 200
            body = resp.read().decode("utf-8")
        assert "Octave" in body
        assert "<!DOCTYPE html>" in body
    finally:
        server.stop()


def test_server_content_type():
    port = _free_port()
    server = OctaveWebServer(host="127.0.0.1", port=port)
    server.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/") as resp:
            content_type = resp.headers.get("Content-Type", "")
        assert "text/html" in content_type
    finally:
        server.stop()


def test_server_address():
    port = _free_port()
    server = OctaveWebServer(host="127.0.0.1", port=port)
    assert server.address == ("127.0.0.1", port)


def test_server_context_manager():
    port = _free_port()
    with OctaveWebServer(host="127.0.0.1", port=port) as server:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/") as resp:
            assert resp.status == 200
    # After __exit__ the server should be stopped; subsequent connections should fail
    import socket
    with pytest.raises(Exception):
        with socket.create_connection(("127.0.0.1", port), timeout=0.5):
            pass


def test_server_exported_from_root():
    from octave import OctaveWebServer as _OWS
    assert _OWS is OctaveWebServer
