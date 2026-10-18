# Hermes Project Assets

Public high-resolution download archive for the [Hermes Project Webapp](https://woongs2021.github.io/Hermes-project-webapp/).

- **Repository:** https://github.com/woongs2021/Hermes-project-assets
- **Webapp:** https://github.com/woongs2021/Hermes-project-webapp
- **Public app:** https://woongs2021.github.io/Hermes-project-webapp/

## Purpose

This repository keeps downloadable 4K/HQ originals out of the GitHub Pages webapp repository. It preserves high-quality design resources without making the product surface, Pages build, or day-to-day webapp clone unnecessarily heavy.

## Architecture contract

```text
Hermes-project-webapp
  ├── UI, public manifests, thumbnails, display-ready previews
  └── GitHub Pages product surface
             │
             └── downloadSrc
                    │
Hermes-project-assets
  └── GitHub Releases: 4K/HQ original downloads
```

| Asset role | Storage | User experience |
| --- | --- | --- |
| Thumbnail and display preview | `Hermes-project-webapp` | fast card and modal rendering on Pages |
| 4K/HQ original | GitHub Release in this repository | download only when explicitly requested |

Every connected webapp manifest item uses:

- `imageSrc` / `previewImageSrc` for the local lightweight preview
- `downloadSrc` for a versioned Release URL in this repository
- `sourceAssetStore`, `sourceAssetRelease`, and `assetTier` for provenance when supported

## Delivery phases and implemented state

### Phase 1 — Repository foundation

**Implemented**

- public repository initialized with repository hygiene rules
- `.gitignore` excludes credentials, secrets, runtime state, logs, local editor files, and release binary folders
- README and metadata remain public-safe; no raw access tokens or private runtime data are stored

### Phase 2 — Design DNA initial migration

**Implemented — `design-dna-2026-10`**

- created public GitHub Release [`design-dna-2026-10`](https://github.com/woongs2021/Hermes-project-assets/releases/tag/design-dna-2026-10)
- uploaded **84** Design DNA 4K/HQ originals (**844,607,892 bytes** total)
- generated a manifest-derived inventory containing source-relative path, file size, SHA-256, deterministic Release filename, and connected webapp references
- checked all Release assets against source byte sizes and verified each generated download URL before the webapp manifest was switched

### Phase 3 — Webapp integration and cleanup

**Implemented**

- the corresponding webapp manifest now shows local WebP previews and uses these Release URLs for original downloads
- all 84 connected preview/download pairs were verified during migration
- tracked high-resolution copies have been removed from the current `Hermes-project-webapp` tree only after Release and Pages verification
- historical git objects are intentionally retained; history rewrite/force push is not part of normal asset delivery

## Current releases

| Release | Contents | Status |
| --- | --- | --- |
| [`design-dna-2026-10`](https://github.com/woongs2021/Hermes-project-assets/releases/tag/design-dna-2026-10) | 84 Design DNA 4K/HQ originals | active public download source |
| [`midjourney-dna-archive-2026-10`](https://github.com/woongs2021/Hermes-project-assets/releases/tag/midjourney-dna-archive-2026-10) | 35 Midjourney DNA Archive 4K originals (949,598,285 bytes) | active public download source |

## Adding a new resource

Use this flow whenever Chris asks to save a Midjourney 4K file or Go Youn-jung approves a public downloadable original.

1. Decide whether the original is public-safe. Never publish personal, confidential, unreleased, or prompt-sensitive material.
2. Keep or generate a lightweight WebP/JPEG preview for `Hermes-project-webapp`.
3. Add only the approved original to a dated/collection Release in this repository.
4. Verify the upload and URL before changing the webapp manifest.
5. Set the webapp item's local preview path and external `downloadSrc` together.
6. Build, deploy, and verify the live Pages preview and download link.

## Repository hygiene

### Commit here

- public-safe inventory and checksums
- deterministic release naming metadata
- release-upload tooling that reads credentials only at runtime and never prints or stores them
- documentation of the asset/webapp contract

### Do not commit here

- original binaries or downloaded Release payloads in Git history
- secrets, OAuth tokens, API keys, credential files, local session data, logs, or caches
- broad runtime directories or unreviewed source folders

## Operational notes

- GitHub **Releases**, not git commits, are the delivery channel for high-resolution originals.
- Release names and filenames should be stable because the webapp's `downloadSrc` is a direct URL.
- If an upload is interrupted, use the inventory/upload workflow to resume after checking existing asset name and size.
- Do not delete a webapp original until the matching Release asset, manifest URL, local preview, build, and live Pages path are verified.
