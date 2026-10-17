# Hermes Project Assets

Public high-resolution download archive for the [Hermes Project Webapp](https://woongs2021.github.io/Hermes-project-webapp/).

## Storage contract

- **GitHub Releases** hold downloadable 4K/HQ originals.
- **Hermes-project-webapp** retains only display-ready previews and thumbnails.
- Webapp manifests point `downloadSrc` to a versioned release URL; preview paths remain local to GitHub Pages.

## Releases

- `design-dna-2026-10` — initial Design DNA 4K/HQ migration batch.

## Repository hygiene

Do not commit binary source originals, credentials, session data, logs, or generated release downloads to this repository. The `inventory/` directory contains only public-safe migration metadata: source-relative paths, checksums, sizes, release names, and webapp manifest references.
