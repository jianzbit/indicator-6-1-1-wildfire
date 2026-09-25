# Indicator 6.1.1: buildings in burned-area pixels

The [dataset card](docs/DATASET_CARD.md) documents input versions, schemas, retained artifact hashes, access requirements and unresolved source/validation limits.

**Conditional source-record research.** The sampler supports supplied-record exploration; the full global release remains withheld. One original-archive Luxembourg pilot has now been reproduced with an independent calculation. The legacy published table contains the documented masking/coverage defects and is retained only for audit.

The [current indicator card](docs/INDICATOR_CARD.md) defines the actual scope. The [scientific review](docs/CONDITIONAL_RESEARCH.md) explains issues, fixes and conditions for national publication. `review/conditional_research.json` accounts for all 195 authoritative countries with null primary estimates pending rerun. The legacy 228 jurisdictions comprise 192 authoritative countries and 36 supplements; Liberia, Sri Lanka and Nauru are absent.

The implementation now transforms coordinates for each raster, samples actual pixel boundaries, records actual input hashes and unknown-record bounds, and reports geodesic five-point perturbations accurately. GABAM binary background does not independently establish observed unburned land. Counts describe supplied CSV records; multi-member archive completeness, unique building identity and real-world accuracy remain unverified.

```bash
uv sync --locked
uv run pytest
uv run python scripts/review_release.py --check
uv run python -m wildfire_exposure run --help
```

The [GABAM v3 publisher](https://zenodo.org/records/17707433) supplies the source description. `provenance/country_ontology.json` freezes the Forge country roster. Earlier notebook and methodology files preserve the implementation history; use the current card and review for release interpretation. No software-coverage or Clanker score certifies scientific quality.

The [Luxembourg replay receipt](review/luxembourg/independent_replay.json) matches all 226,721 distinct source IDs and finds zero intersections with burned-code pixels in the two pinned tiles. This selected, previously inspected case tests computation, not positive fire detection, physical stock completeness or global transfer. The GABAM tiles are fingerprinted from the existing mirror; parent-ZIP lineage remains unverified.
