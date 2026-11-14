# DNA Dashboard — Midjourney resource library

This folder is the **only reusable library for the resources actually displayed in**:

**Hermes webapp → Corporate AX → Design DNA → DNA Dashboard → Midjourney**

It intentionally excludes unrelated Midjourney mockups, packaging experiments, and other Release assets.

## Scope

`catalog.json` is generated from the live [Midjourney DNA Dashboard manifest](https://woongs2021.github.io/Hermes-project-webapp/data/midjourney-dna-archive.json). It contains exactly the Dashboard’s published Midjourney items, in their visible numeric order.

Each item includes:

- stable Dashboard ID and visible sequence
- title, creation date, dimensions, and SHA-256 asset hash when supplied by the Dashboard
- `previewUrl`: the public Dashboard resource
- `downloadUrl`: its canonical GitHub Release original when one exists

Some Dashboard resources have only a public webapp preview today; their `downloadUrl` is `null`. The catalog makes that distinction explicit instead of implying they are 4K originals.

## Reuse

For another project, use `downloadUrl` when it exists. Otherwise use `previewUrl` and treat it as the published web-size resource. Do not pull unrelated assets from the broader Release history.

## Update rule

**Update only this `midjourney/` folder when the DNA Dashboard collection changes.**

After the webapp change is deployed, run:

```bash
python3 midjourney/refresh_catalog.py --verify-urls
```

This refreshes `catalog.json` from the live Dashboard manifest and checks every listed preview is a live image. Commit only the changed files within `midjourney/` (plus this root README only if the repository-level architecture changes).

The script does not download or duplicate high-resolution Release binaries. Existing Release URLs remain stable and existing consuming projects are not affected.
