#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

COMMIT = "6bc610e40083ef61a40966dfb5d38612cabc4c5b"
OWNER = "Leeham06972452"
REPO = "erdos-36-lower-bound"
RAW_BASE = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{COMMIT}/certificate/"
API_BASE = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/certificate/"
ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "cache"
SHA_FILE = ROOT / "SHA256SUMS.txt"
TOKEN = os.environ.get("GITHUB_TOKEN")


def load_expected() -> dict[str, str]:
    result: dict[str, str] = {}
    for line in SHA_FILE.read_text().splitlines():
        if not line.strip():
            continue
        digest, name = line.split(maxsplit=1)
        name = name.strip()
        if name in result:
            raise ValueError(f"duplicate upstream hash path: {name}")
        if Path(name).name != name or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise ValueError(f"unsafe name or invalid SHA-256: {name}")
        result[name] = digest
    return result


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def request(url: str, *, accept: str | None = None, timeout: int = 35) -> bytes:
    headers = {"User-Agent": "erdos36-parseval-prefix/0.1.0-preprint"}
    if accept:
        headers["Accept"] = accept
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def download_raw(name: str) -> bytes:
    return request(RAW_BASE + name)


def download_api(name: str) -> bytes:
    url = API_BASE + urllib.parse.quote(name) + f"?ref={COMMIT}"
    payload = json.loads(request(url, accept="application/vnd.github+json").decode("utf-8"))
    if payload.get("encoding") != "base64" or "content" not in payload:
        raise RuntimeError(f"unexpected GitHub API response for {name}")
    return base64.b64decode(payload["content"], validate=False)


def fetch_one(name: str) -> bytes:
    errors: list[str] = []
    for method in (download_raw, download_api):
        for attempt in range(1, 4):
            try:
                return method(name)
            except Exception as exc:  # network errors are reported in aggregate
                errors.append(f"{method.__name__} attempt {attempt}: {exc}")
                time.sleep(min(2**attempt, 8))
    raise RuntimeError("; ".join(errors))


def main() -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    expected = load_expected()
    failures: list[str] = []
    for name, digest in expected.items():
        target = CACHE / name
        if not target.exists() or sha256(target) != digest:
            print(f"downloading {name}", flush=True)
            try:
                data = fetch_one(name)
                target.write_bytes(data)
            except Exception as exc:
                failures.append(f"{name}: download failed: {exc}")
                continue
        actual = sha256(target)
        if actual != digest:
            failures.append(f"{name}: {actual} != {digest}")
        else:
            print(f"OK {name}")
    if failures:
        print("FAIL", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        print(
            "Hint: set GITHUB_TOKEN to avoid unauthenticated API limits, or place "
            "the pinned files in upstream/cache manually.",
            file=sys.stderr,
        )
        return 1
    print(f"PASS: {len(expected)} upstream files at {COMMIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
