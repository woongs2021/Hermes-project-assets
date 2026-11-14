#!/usr/bin/env python3
"""Sync only the resources rendered in Design DNA → DNA Dashboard → Midjourney.

The canonical collection is the public webapp manifest. This script deliberately
keeps unrelated Midjourney mockups/package assets out of this reusable library.
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

WEBAPP = "https://woongs2021.github.io/Hermes-project-webapp/"
MANIFEST_URL = urllib.parse.urljoin(WEBAPP, "data/midjourney-dna-archive.json")
ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "catalog.json"


def public_url(path_or_url: str) -> str:
    return path_or_url if path_or_url.startswith("http") else urllib.parse.urljoin(WEBAPP, path_or_url.lstrip("/"))


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Hermes-DNA-Dashboard-Catalog"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def image_status(url: str) -> str:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Hermes-DNA-Dashboard-Catalog"})
    with urllib.request.urlopen(request, timeout=30) as response:
        content_type = response.headers.get_content_type()
        if not content_type.startswith("image/"):
            raise RuntimeError(f"Expected an image for {url}, got {content_type}")
        return content_type


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-urls", action="store_true", help="HEAD-check every Dashboard preview URL")
    args = parser.parse_args()

    manifest = fetch_json(MANIFEST_URL)
    source_items = manifest.get("items")
    if not isinstance(source_items, list):
        raise RuntimeError("Unexpected Midjourney manifest: missing items list")

    items: list[dict] = []
    for source in source_items:
        title = source.get("title", "")
        match = re.search(r"Midjourney\s+(\d+)", title)
        if not match or not source.get("id") or not source.get("imageSrc"):
            raise RuntimeError(f"Incomplete dashboard item: {source.get('id', title)}")
        preview_url = public_url(source["imageSrc"])
        item = {
            "sequence": int(match.group(1)),
            "id": source["id"],
            "title": title,
            "created": source.get("created"),
            "previewUrl": preview_url,
            "downloadUrl": source.get("highResDownloadSrc"),
            "width": source.get("width"),
            "height": source.get("height"),
            "assetHash": source.get("assetHash"),
        }
        if args.verify_urls:
            item["previewContentType"] = image_status(preview_url)
        items.append(item)

    items.sort(key=lambda item: item["sequence"])
    if len({item["id"] for item in items}) != len(items):
        raise RuntimeError("Duplicate DNA Dashboard item ids")
    if len({item["sequence"] for item in items}) != len(items):
        raise RuntimeError("Duplicate DNA Dashboard sequence numbers")

    release_originals = sum(1 for item in items if item["downloadUrl"])
    payload = {
        "schemaVersion": 2,
        "collection": "Design DNA → DNA Dashboard → Midjourney",
        "webappManifestUrl": MANIFEST_URL,
        "generatedAt": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "totals": {
            "resources": len(items),
            "releaseOriginals": release_originals,
            "previewOnly": len(items) - release_originals,
        },
        "items": items,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"cataloged {len(items)} DNA Dashboard resources; {release_originals} Release originals; {len(items)-release_originals} preview-only")


if __name__ == "__main__":
    main()
