# Midjourney asset library

This folder is the single reusable entry point for every public Midjourney resource held in [`Hermes-project-assets`](https://github.com/woongs2021/Hermes-project-assets).

## What this folder is

GitHub Release assets cannot be placed in folders and should not be copied into Git history. `catalog.json` provides the folder-like library view instead:

- one record per canonical public original
- stable filename, category, Release tag, byte size, timestamp, and direct download URL
- all originals remain in their existing versioned GitHub Releases, so current webapp download links stay valid
- no binary is duplicated in this repository

The catalog currently includes an asset when either:

1. its Release tag starts with `midjourney-dna-`, or
2. its filename contains `midjourney`.

That includes the DNA archive originals and Midjourney-derived mockup/package resources. It does not include unrelated GoYJ/GPT assets.

## Reuse

Use `catalog.json` as the lookup source. Each item has a public `downloadUrl`, which is the canonical original. Keep project-specific lightweight previews in the consuming project; do not copy a high-resolution original into the webapp repository.

## Future update rule

**This `midjourney/` folder is the only Git folder to update for the reusable Midjourney library.**

1. Upload a public-safe original to its appropriate dated GitHub Release.
2. Verify the Release asset’s direct URL returns the expected bytes.
3. From the repository root, run:
   ```bash
   python3 midjourney/refresh_catalog.py
   ```
4. Inspect the generated diff and commit only `midjourney/catalog.json` and, if the rules change, `midjourney/README.md` or `midjourney/refresh_catalog.py`.
5. For a consuming webapp, point `downloadSrc` to the catalog entry’s `downloadUrl`; preserve a lightweight local preview.

Do not download all Releases to rebuild this library, and do not delete or rename existing Release assets: their direct URLs can already be referenced by live projects.
