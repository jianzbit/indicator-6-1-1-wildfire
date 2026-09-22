# Conditional research review — 21 September 2026

**Disposition: conditional source-record research; global primary numerical publication remains withheld.**
The newer organization repository fixes tile indexing and binary sampling, but initially contained no regenerated national release. Its supplied-CSV runner counts records, cannot establish completeness of a multi-member national archive, and does not deduplicate building IDs. Software coverage percentages are not a scientific-quality score.

The frozen published legacy table from `jianzbit/indicator-6-1-1-wildfire` commit `92b84728ad3095949607311640132d82505378db` contains 228 jurisdictions: 192 of the authoritative 195 countries and 36 supplements. Liberia, Sri Lanka and Nauru are missing. Every row has valid-pixel count equal to exposed count, reproducing the documented masking defect. This signature alone is not ground-truth validation, and the earlier tile-selection defect cannot be repaired from country aggregates. `review/source/legacy_GABAM2024.csv` is retained solely as an immutable negative-result snapshot. All 195 primary national values in the new review ledger are null pending a corrected original-data rerun.

## Fixes and permitted use

The supplied-record diagnostic now respects each raster's CRS and actual pixel boundaries, records exact local input/output and implementation hashes, reports unclassified-record bounds, and refuses unsupported analysis years. It no longer claims that arbitrary local tiles were verified against the published GABAM archive checksum. Sensitivity uses per-point geodesic cardinal offsets, tracks unknown samples and explicitly says it samples five points rather than an entire buffer or footprint. No corrected global estimate has been invented.

Conditional use is exploration of the cited source-record frame, with its manifest and limitations attached. GABAM binary zero is treated as background by the operational model; absence of a burn code does not independently establish unburned land or adequate Landsat observation. The data publisher describes a 0.00025° distribution (approximately 30 m), annual coverage 2014–2024 and tiles spanning 80°N–60°S. Burned-area intersection is not proof of wildfire cause, building damage, future probability or loss. See the [GABAM v3 source](https://zenodo.org/records/17707433).

## Evidence needed for national publication

1. Retrieve and hash the original building archive and all members; verify identity and inventory completeness, with unknown records explicit.
2. Run the corrected sampler for all 195 countries; pin raster/ZIP lineage and document background versus unavailable observations.
3. Compare a geographically diverse probability sample with dated, independent fire perimeters or imagery, including negatives and positional perturbations. A selected software example does not estimate global error.
4. Reconcile the downstream published table with that exact release; preserve earlier negative results and missing countries.

Reproduce the legacy audit with `python scripts/review_release.py --check`. Execute package regression tests with `uv run pytest`. The audit checks saved records and current fixes; it is not a new full raster experiment or empirical accuracy certification. The prior notebook and prior methodology are historical implementation records where they conflict with this current disposition. The authoritative roster is frozen from Forge `BIT-ONT-GEO-2026.1`; its exact source snapshot is in `provenance/country_ontology.json`.

## Executed Luxembourg source-frame pilot

An existing private mirror supplied the complete original Luxembourg archive and two GABAM-labeled tiles. The archive SHA-256 exactly matches the independently acquired official JRC archive retained for indicator 6.1.5; its single CSV has 226,721 nonmissing, distinct source IDs. The two exact raster hashes are pinned, but linkage to the parent Zenodo ZIP was not independently re-established.

The corrected production sampler and a separate raw-window/NumPy-index calculation agreed on all five checked counts: total records, valid coordinates, tile coverage and binary-classified records were each 226,721; burned-code intersections were zero. The full result and provenance are under `review/luxembourg/`. This is a selected computational pilot with a previously inspected zero result; it supplies no positive-detection evaluation, blind accuracy holdout, global error rate or proof of no real fire/building damage. Full country-frame integrity does not establish complete physical building stock.

Reproduce with `python scripts/replay_luxembourg.py --inputs <verified-private-input-directory> --output <new-output-directory>`. The script rejects input hashes that differ from the retained snapshot. Raw data are not added to Git. All 195 primary national values remain withheld; the Luxembourg pilot value is separately identified in the review ledger. This bounded result extends implementation-only evidence without promoting the legacy global table.
