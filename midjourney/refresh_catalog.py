#!/usr/bin/env python3
"""Build the public, link-only Midjourney asset catalog from GitHub Releases.

This intentionally indexes Release assets instead of downloading or committing their
binary payloads. GitHub Release assets remain the canonical original downloads.
"""
from __future__ import annotations

import json
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

OWNER = "woongs2021"
REPOSITORY = "Hermes-project-assets"
API_URL = f"https://api.github.com/repos/{OWNER}/{REPOSITORY}/releases?per_page=100"
ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "catalog.json"


def is_midjourney_asset(release: dict, asset: dict) -> bool:
    tag = release["tag_name"].lower()
    name = asset["name"].lower()
    return tag.startswith("midjourney-dna-") or "midjourney" in name


def category_for(release: dict, asset: dict) -> str:
    tag = release["tag_name"].lower()
    name = asset["name"].lower()
    if tag.startswith("midjourney-dna-archive-"):
        return "dna-archive"
    if "mockup" in name:
        return "mockup"
    return "midjourney-derived"


def fetch_releases() -> list[dict]:
    request = urllib.request.Request(
        API_URL,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "Hermes-Midjourney-Catalog"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def main() -> None:
    releases = fetch_releases()
    items: list[dict] = []
    for release in releases:
        for asset in release.get("assets", []):
            if not is_midjourney_asset(release, asset):
                continue
            items.append(
                {
                    "name": asset["name"],
                    "category": category_for(release, asset),
                    "releaseTag": release["tag_name"],
                    "releaseUrl": release["html_url"],
                    "downloadUrl": asset["browser_download_url"],
                    "bytes": asset["size"],
                    "contentType": asset.get("content_type", "application/octet-stream"),
                    "updatedAt": asset["updated_at"],
                }
            )
    items.sort(key=lambda item: (item["category"], item["releaseTag"], item["name"]))
    totals: dict[str, dict[str, int]] = {}
    for item in items:
        bucket = totals.setdefault(item["category"], {"assets": 0, "bytes": 0})
        bucket["assets"] += 1
        bucket["bytes"] += item["bytes"]
    payload = {
        "schemaVersion": 1,
        "repository": f"{OWNER}/{REPOSITORY}",
        "assetStorage": "GitHub Releases",
        "generatedAt": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "selectionRule": "Release tag starts with midjourney-dna- OR asset filename contains midjourney.",
        "totals": {"assets": len(items), "bytes": sum(item["bytes"] for item in items), "byCategory": totals},
        "items": items,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"cataloged {len(items)} assets ({payload['totals']['bytes']} bytes) -> {OUTPUT}")


if __name__ == "__main__":
    main()
