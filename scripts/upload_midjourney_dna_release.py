#!/usr/bin/env python3
"""Create/resume the Midjourney DNA 4K release; credentials stay in git's helper."""
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
WEBAPP_ROOT = Path("/opt/data/projects/Hermes-project-webapp/august-dashboard")
INVENTORY = Path("/opt/data/tmp/Hermes-project-assets/inventory/midjourney-dna-archive-2026-10-release.json")
REPORT = Path("/opt/data/tmp/Hermes-project-assets/inventory/midjourney-dna-archive-2026-10-upload-report.json")
API = f"https://api.github.com/repos/{OWNER}/{REPO}"


def token() -> str:
    result = subprocess.run(["git", "credential", "fill"], input=b"protocol=https\nhost=github.com\n\n", stdout=subprocess.PIPE, check=True)
    fields = dict(line.split("=", 1) for line in result.stdout.decode().splitlines() if "=" in line)
    value = fields.get("password")
    if not value:
        raise RuntimeError("No GitHub HTTPS credential available.")
    return value


HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {token()}",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "Hermes-midjourney-dna-migration",
}


def request(url: str, method: str = "GET", body: bytes | None = None, headers: dict[str, str] | None = None):
    merged = dict(HEADERS)
    if headers:
        merged.update(headers)
    req = urllib.request.Request(url, data=body, headers=merged, method=method)
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()


def release_for(source: dict) -> dict:
    tag = source["releaseTag"]
    status, raw = request(f"{API}/releases/tags/{urllib.parse.quote(tag)}")
    if status == 200:
        return json.loads(raw)
    if status != 404:
        raise RuntimeError(f"Release lookup failed: HTTP {status}")
    payload = json.dumps({
        "tag_name": tag,
        "target_commitish": "main",
        "name": source["releaseName"],
        "body": "4K downloadable originals for the Midjourney Design DNA Archive. The webapp retains local display previews.",
        "draft": False,
        "prerelease": False,
    }).encode()
    status, raw = request(f"{API}/releases", "POST", payload, {"Content-Type": "application/json"})
    if status not in (200, 201):
        raise RuntimeError(f"Release creation failed: HTTP {status}")
    return json.loads(raw)


def main() -> None:
    source = json.loads(INVENTORY.read_text())
    release = release_for(source)
    status, raw = request(f"{API}/releases/{release['id']}/assets?per_page=100")
    if status != 200:
        raise RuntimeError(f"Asset list failed: HTTP {status}")
    existing = {item["name"]: item for item in json.loads(raw)}
    upload_base = release["upload_url"].split("{")[0]
    report = {"release": {"tag": source["releaseTag"], "url": release["html_url"]}, "uploaded": [], "skipped": [], "failed": []}
    for index, asset in enumerate(source["assets"], 1):
        name = asset["releaseAssetName"]
        if existing.get(name, {}).get("size") == asset["bytes"] and existing[name].get("state") == "uploaded":
            report["skipped"].append(name)
            print(f"[{index}/{len(source['assets'])}] skip {name}", flush=True)
            continue
        local = WEBAPP_ROOT / "public" / asset["sourcePath"]
        if not local.is_file() or local.stat().st_size != asset["bytes"]:
            raise RuntimeError(f"Source verification failed: {local}")
        content_type = mimetypes.guess_type(name)[0] or "application/octet-stream"
        print(f"[{index}/{len(source['assets'])}] upload {name}", flush=True)
        status, raw = request(f"{upload_base}?name={urllib.parse.quote(name)}", "POST", local.read_bytes(), {"Content-Type": content_type, "Content-Length": str(asset["bytes"])})
        if status not in (200, 201):
            report["failed"].append({"name": name, "status": status})
            REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
            raise RuntimeError(f"Upload failed for {name}: HTTP {status}")
        report["uploaded"].append(name)
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        time.sleep(0.1)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"release": release["html_url"], "uploaded": len(report["uploaded"]), "skipped": len(report["skipped"])}), flush=True)


if __name__ == "__main__":
    main()
