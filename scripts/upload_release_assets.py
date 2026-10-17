#!/usr/bin/env python3
"""Create/resume the public Design DNA release and upload the inventoried originals.
Credentials are read from git's HTTPS credential helper and never printed or persisted.
"""
from __future__ import annotations

import json
import mimetypes
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

OWNER = "woongs2021"
REPO = "Hermes-project-assets"
ROOT = Path("/opt/data/projects/Hermes-project-webapp/august-dashboard")
INVENTORY = Path("/opt/data/tmp/Hermes-project-assets/inventory/design-dna-2026-10.json")
REPORT = Path("/opt/data/tmp/Hermes-project-assets/inventory/design-dna-2026-10-upload-report.json")
API = f"https://api.github.com/repos/{OWNER}/{REPO}"


def github_token() -> str:
    completed = subprocess.run(
        ["git", "credential", "fill"],
        input=b"protocol=https\nhost=github.com\n\n",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    values = {}
    for line in completed.stdout.decode().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    token = values.get("password")
    if not token:
        raise RuntimeError("No GitHub HTTPS credential is available to create/upload a release.")
    return token


TOKEN = github_token()
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "Hermes-asset-migration",
}


def request(url: str, method: str = "GET", body: bytes | None = None, headers: dict | None = None):
    merged = dict(HEADERS)
    if headers:
        merged.update(headers)
    req = urllib.request.Request(url, data=body, headers=merged, method=method)
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            return response.status, response.headers, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.headers, error.read()


def release_for(tag: str) -> dict:
    status, _, raw = request(f"{API}/releases/tags/{urllib.parse.quote(tag)}")
    if status == 200:
        return json.loads(raw)
    if status != 404:
        raise RuntimeError(f"Release lookup failed ({status}): {raw[:500].decode(errors='replace')}")
    payload = json.dumps({
        "tag_name": tag,
        "target_commitish": "main",
        "name": "Design DNA 4K & HQ Assets — 2026-10",
        "body": "Public downloadable originals for Hermes Project Webapp. Display previews remain in the webapp repository.",
        "draft": False,
        "prerelease": False,
    }).encode()
    status, _, raw = request(f"{API}/releases", "POST", payload, {"Content-Type": "application/json"})
    if status not in (200, 201):
        raise RuntimeError(f"Release creation failed ({status}): {raw[:500].decode(errors='replace')}")
    return json.loads(raw)


def main() -> None:
    source = json.loads(INVENTORY.read_text())
    release = release_for(source["releaseTag"])
    release_id = release["id"]
    upload_base = release["upload_url"].split("{")[0]
    status, _, raw = request(f"{API}/releases/{release_id}/assets?per_page=100")
    if status != 200:
        raise RuntimeError(f"Asset list failed ({status}): {raw[:500].decode(errors='replace')}")
    existing = {item["name"]: item for item in json.loads(raw)}
    report = {"release": {"id": release_id, "tag": source["releaseTag"], "html_url": release["html_url"]}, "uploaded": [], "skipped": [], "failed": []}
    for index, asset in enumerate(source["assets"], 1):
        name = asset["releaseAssetName"]
        local = ROOT / asset["sourcePath"]
        if name in existing and existing[name].get("size") == asset["bytes"]:
            report["skipped"].append(name)
            print(f"[{index}/{len(source['assets'])}] skip {name}", flush=True)
            continue
        content_type = mimetypes.guess_type(name)[0] or "application/octet-stream"
        data = local.read_bytes()
        endpoint = f"{upload_base}?name={urllib.parse.quote(name)}"
        status, _, raw = request(endpoint, "POST", data, {"Content-Type": content_type, "Content-Length": str(len(data))})
        if status in (200, 201):
            report["uploaded"].append(name)
            print(f"[{index}/{len(source['assets'])}] uploaded {name}", flush=True)
        else:
            report["failed"].append({"name": name, "status": status, "message": raw[:500].decode(errors="replace")})
            print(f"[{index}/{len(source['assets'])}] FAILED {name}: HTTP {status}", flush=True)
            break
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        time.sleep(0.15)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    if report["failed"]:
        raise SystemExit(1)
    print(json.dumps({"release": report["release"]["html_url"], "uploaded": len(report["uploaded"]), "skipped": len(report["skipped"])}), flush=True)


if __name__ == "__main__":
    main()
