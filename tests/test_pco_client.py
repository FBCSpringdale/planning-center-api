"""Offline checks for scripts/pco_client.py against a local mock server. Run: python3 tests/test_pco_client.py"""
import http.server
import json
import os
import sys
import tempfile
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "planning-center-api", "scripts"))
import pco_client  # noqa: E402

hits = []
fail_first = set()  # paths that answer 429 on their first request


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _reply(self, code, body, headers=None):
        raw = json.dumps(body).encode()
        self.send_response(code)
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _handle(self):
        length = int(self.headers.get("Content-Length") or 0)
        hits.append((self.command, self.path, self.headers.get("Content-Type"), self.rfile.read(length)))
        path = self.path.split("?")[0]
        if path in fail_first:
            fail_first.discard(path)
            return self._reply(429, {"errors": [{"code": "429"}]}, {"Retry-After": "0"})
        if path == "/people":
            nxt = f"http://127.0.0.1:{self.server.server_port}/people2?offset=1"
            return self._reply(200, {
                "data": [{"type": "Person", "id": "1", "relationships": {"emails": {"data": [{"type": "Email", "id": "9"}]}}}],
                "included": [{"type": "Email", "id": "9", "attributes": {"address": "a@example.com"}}],
                "links": {"next": nxt}})
        if path == "/people2":
            return self._reply(200, {"data": [{"type": "Person", "id": "2"}], "links": {}})
        if path == "/files":
            return self._reply(200, {"data": [{"type": "File", "id": "us1-abc"}]})
        if path == "/boom":
            return self._reply(500, {"errors": [{"code": "500"}]})
        return self._reply(201, {"data": {"type": "Donation", "id": "7"}})

    do_GET = do_POST = _handle


server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_port}"
client = pco_client.PCO(app_id="id", secret="secret", max_retries=2)


def test_paginate_follows_next_and_resolves_includes():
    rows = list(client.paginate(BASE + "/people", params={"include": "emails"}))
    assert [r["id"] for r in rows] == ["1", "2"]
    assert rows[0]["_included"]["emails"][0]["attributes"]["address"] == "a@example.com"


def test_post_retries_after_429():
    fail_first.add("/donations")
    out = client.post(BASE + "/donations", {"payment_method": "check"}, type_="Donation")
    assert out["data"]["id"] == "7"
    assert sum(1 for h in hits if h[1] == "/donations") == 2


def test_post_does_not_retry_500():
    before = len(hits)
    try:
        client.post(BASE + "/boom", {})
        raise AssertionError("expected PCOError")
    except pco_client.PCOError as e:
        assert e.status == 500
    assert len(hits) - before == 1


def test_upload_uses_shared_retry():
    pco_client.UPLOAD = BASE + "/files"
    fail_first.add("/files")
    with tempfile.NamedTemporaryFile(suffix=".png") as f:
        f.write(b"png")
        f.flush()
        assert client.upload(f.name) == "us1-abc"
    uploads = [h for h in hits if h[1] == "/files"]
    assert len(uploads) == 2 and uploads[-1][2].startswith("multipart/form-data")


def test_default_user_agent_has_contact_link():
    assert "https://" in client.user_agent


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
