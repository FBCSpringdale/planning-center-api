#!/usr/bin/env python3
"""Minimal Planning Center API client for agents and scripts.

Handles: Basic (PAT) or Bearer (OAuth) auth, User-Agent, version header,
rate-limit backoff (reads X-PCO-API-Request-Rate-* and Retry-After),
pagination (follows links.next), include-flattening, and JSON:API write envelopes.

Usage as a library:
    from pco_client import PCO
    pco = PCO.from_env()                      # PCO_APP_ID + PCO_SECRET, or PCO_ACCESS_TOKEN
    me = pco.get("/current/v2/me")
    for person in pco.paginate("/people/v2/people", params={"where[last_name]": "Doe", "include": "emails"}):
        print(person["id"], person["attributes"]["name"], person.get("_included", {}).get("emails"))
    pco.post("/people/v2/people", {"first_name": "Jane", "last_name": "Doe"}, type_="Person")

Usage from the shell:
    python scripts/pco_client.py GET /people/v2/people 'where[search_name]=jane' 'per_page=5'
    python scripts/pco_client.py GET /services/v2/service_types --all
    python scripts/pco_client.py POST /people/v2/people '{"attributes":{"first_name":"Jane","last_name":"Doe"}}'

Environment:
    PCO_APP_ID / PCO_SECRET        Personal Access Token pair (HTTP Basic)
    PCO_ACCESS_TOKEN               OAuth bearer token (takes precedence if set)
    PCO_API_VERSION                Optional X-PCO-API-Version (e.g. 2026-10-05); applies to every product
    PCO_USER_AGENT                 Optional; default "pco_client.py (agent skill)"
"""
from __future__ import annotations

import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Iterator, List, Optional

BASE = "https://api.planningcenteronline.com"
UPLOAD = "https://upload.planningcenteronline.com/v2/files"


class PCOError(Exception):
    def __init__(self, status: int, body: Any, url: str):
        self.status, self.body, self.url = status, body, url
        super().__init__(f"HTTP {status} for {url}: {json.dumps(body)[:800]}")


class PCO:
    def __init__(self, app_id: Optional[str] = None, secret: Optional[str] = None,
                 access_token: Optional[str] = None, version: Optional[str] = None,
                 user_agent: Optional[str] = None, max_retries: int = 5):
        if access_token:
            self._auth = f"Bearer {access_token}"
        elif app_id and secret:
            self._auth = "Basic " + base64.b64encode(f"{app_id}:{secret}".encode()).decode()
        else:
            raise ValueError("Provide access_token or app_id+secret")
        self.version = version
        self.user_agent = user_agent or "pco_client.py (agent skill)"
        self.max_retries = max_retries
        self.last_rate: Dict[str, Optional[str]] = {}

    @classmethod
    def from_env(cls) -> "PCO":
        return cls(app_id=os.getenv("PCO_APP_ID"), secret=os.getenv("PCO_SECRET"),
                   access_token=os.getenv("PCO_ACCESS_TOKEN"),
                   version=os.getenv("PCO_API_VERSION"), user_agent=os.getenv("PCO_USER_AGENT"))

    # ---- low level -------------------------------------------------------
    def request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None,
                body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = path if path.startswith("http") else BASE + path
        if params:
            sep = "&" if "?" in url else "?"
            url += sep + urllib.parse.urlencode(params, doseq=True, safe="[],")
        data = json.dumps(body).encode() if body is not None else None
        headers = {"Authorization": self._auth, "User-Agent": self.user_agent, "Accept": "application/json"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        if self.version:
            headers["X-PCO-API-Version"] = self.version
        for attempt in range(self.max_retries + 1):
            req = urllib.request.Request(url, data=data, method=method, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    self._record_rate(resp.headers)
                    raw = resp.read()
                    return json.loads(raw) if raw else {}
            except urllib.error.HTTPError as e:
                self._record_rate(e.headers)
                raw = e.read()
                try:
                    err = json.loads(raw) if raw else {}
                except json.JSONDecodeError:
                    err = {"raw": raw.decode(errors="replace")}
                if e.code == 429 and attempt < self.max_retries and method in ("GET", "HEAD"):
                    wait = int(e.headers.get("Retry-After") or 1)
                    time.sleep(wait)
                    continue
                if e.code in (500, 503) and attempt < self.max_retries and method in ("GET", "HEAD"):
                    time.sleep(2 ** attempt)
                    continue
                raise PCOError(e.code, err, url) from None
        raise PCOError(0, {"error": "max retries exceeded"}, url)

    def _record_rate(self, headers) -> None:
        self.last_rate = {
            "limit": headers.get("X-PCO-API-Request-Rate-Limit"),
            "count": headers.get("X-PCO-API-Request-Rate-Count"),
            "period": headers.get("X-PCO-API-Request-Rate-Period"),
        }
        try:
            if int(self.last_rate["count"] or 0) >= 0.8 * int(self.last_rate["limit"] or 100):
                time.sleep(1)
        except ValueError:
            pass

    # ---- convenience -----------------------------------------------------
    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.request("GET", path, params=params)

    def post(self, path: str, attributes: Optional[Dict[str, Any]] = None, type_: Optional[str] = None,
             relationships: Optional[Dict[str, Any]] = None, included: Optional[List[Dict[str, Any]]] = None,
             params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.request("POST", path, params=params,
                            body=envelope(attributes, type_, relationships, included))

    def patch(self, path: str, attributes: Optional[Dict[str, Any]] = None, type_: Optional[str] = None,
              relationships: Optional[Dict[str, Any]] = None, included: Optional[List[Dict[str, Any]]] = None,
              params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.request("PATCH", path, params=params,
                            body=envelope(attributes, type_, relationships, included))

    def delete(self, path: str) -> Dict[str, Any]:
        return self.request("DELETE", path)

    def action(self, path: str, type_: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None,
               relationships: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """POST to a custom action endpoint (e.g. /lists/{id}/run, /batches/{id}/commit)."""
        body = envelope(attributes, type_, relationships) if (type_ or attributes or relationships) else {}
        return self.request("POST", path, body=body)

    def paginate(self, path: str, params: Optional[Dict[str, Any]] = None, per_page: int = 100,
                 flatten_includes: bool = True) -> Iterator[Dict[str, Any]]:
        """Yield every resource in a collection, following links.next."""
        params = dict(params or {})
        params.setdefault("per_page", per_page)
        url: Optional[str] = path
        first = True
        while url:
            page = self.request("GET", url, params=params if first else None)
            first = False
            included = index_included(page.get("included", []))
            for item in page.get("data", []):
                if flatten_includes and included:
                    item["_included"] = resolve(item, included)
                yield item
            url = (page.get("links") or {}).get("next")

    def upload(self, filepath: str) -> str:
        """Upload a file; returns the File UUID to assign to a file attribute (avatar, art, …)."""
        boundary = "----pco" + os.urandom(8).hex()
        name = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            content = f.read()
        body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\n"
                f"Content-Type: application/octet-stream\r\n\r\n").encode() + content + f"\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request(UPLOAD, data=body, method="POST", headers={
            "Authorization": self._auth, "User-Agent": self.user_agent,
            "Content-Type": f"multipart/form-data; boundary={boundary}"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())["data"][0]["id"]


# ---- JSON:API helpers -----------------------------------------------------
def envelope(attributes=None, type_=None, relationships=None, included=None) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    if type_:
        data["type"] = type_
    if attributes is not None:
        data["attributes"] = attributes
    if relationships:
        data["relationships"] = {
            k: (v if isinstance(v, dict) and "data" in v else {"data": v}) for k, v in relationships.items()
        }
    body: Dict[str, Any] = {"data": data}
    if included:
        body["included"] = included
    return body


def rel(type_: str, id_: Any) -> Dict[str, Any]:
    """Build a to-one relationship linkage: rel('Person', 123)."""
    return {"data": {"type": type_, "id": str(id_)}}


def rels(type_: str, ids: List[Any]) -> Dict[str, Any]:
    """Build a to-many relationship linkage."""
    return {"data": [{"type": type_, "id": str(i)} for i in ids]}


def index_included(included: List[Dict[str, Any]]) -> Dict[tuple, Dict[str, Any]]:
    return {(r["type"], r["id"]): r for r in included}


def resolve(item: Dict[str, Any], index: Dict[tuple, Dict[str, Any]]) -> Dict[str, Any]:
    """Map relationship name -> included resource(s) for one item."""
    out: Dict[str, Any] = {}
    for name, link in (item.get("relationships") or {}).items():
        data = link.get("data")
        if isinstance(data, list):
            out[name] = [index.get((d["type"], d["id"]), d) for d in data]
        elif isinstance(data, dict):
            out[name] = index.get((data["type"], data["id"]), data)
    return out


# ---- CLI ------------------------------------------------------------------
def _main(argv: List[str]) -> int:
    if len(argv) < 2 or argv[0].upper() not in ("GET", "POST", "PATCH", "DELETE"):
        print(__doc__)
        return 2
    method, path, rest = argv[0].upper(), argv[1], argv[2:]
    pco = PCO.from_env()
    if method == "GET":
        all_pages = "--all" in rest
        params: Dict[str, Any] = {}
        for kv in rest:
            if kv.startswith("--"):
                continue
            k, _, v = kv.partition("=")
            params[k] = v
        if all_pages:
            rows = list(pco.paginate(path, params=params, flatten_includes=False))
            print(json.dumps({"data": rows, "count": len(rows)}, indent=2))
        else:
            print(json.dumps(pco.get(path, params=params), indent=2))
        return 0
    if method == "DELETE":
        print(json.dumps(pco.delete(path), indent=2))
        return 0
    payload = json.loads(rest[0]) if rest else {}
    body = payload if "data" in payload else {"data": payload}
    print(json.dumps(pco.request(method, path, body=body), indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(_main(sys.argv[1:]))
    except PCOError as e:
        print(json.dumps({"error": e.status, "url": e.url, "body": e.body}, indent=2), file=sys.stderr)
        sys.exit(1)
