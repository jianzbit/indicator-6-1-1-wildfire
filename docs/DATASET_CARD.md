# Dataset card — Indicator 6.1.1 wildfire exposure

Documented 2026-09-25 against repository commit `19324e1f893e8b444c64177cfb7c4b5c4008a174`. This card inventories the implemented inputs and committed evidence; it reports no new raster experiment or method adoption. The [indicator card](INDICATOR_CARD.md) and [conditional review](CONDITIONAL_RESEARCH.md) govern interpretation: Luxembourg is a selected source-record diagnostic; all 195 primary national values remain withheld.

## Inputs, access and resolution

| Input | Version and role | Coverage and limits |
|---|---|---|
| GABAM burned-area GeoTIFFs | The [v3 publisher record](https://zenodo.org/records/17707433) describes 2014–2024 annual maps in WGS84 at 0.00025° (nominally about 30 m), in 5° × 5° tiles from 80°N to 60°S. This runner accepts **2024 only**. | Raw tiles/ZIP are external. Recorded `GABAM2024.zip` MD5: `b6c4b70bc95f9c3c30f4dfd5505ef12d`. Arbitrary local tiles are not authenticated by that archive checksum. |
| GHS-OBAT CSV | Retained Luxembourg archive: `GHS_OBAT_CSV_LUX_E2020_R2024A_V1_0.zip`; E2020 attributes and R2024A geometry/release form a mixed-vintage source frame. | Raw bytes are external. The runner reads `lon`/`lat` from one CSV and counts rows; it does not deduplicate IDs or establish complete national stock. Representative points are not footprints. |
| [Country roster](../config/countries.csv) | 195 rows: `iso3`, `country_name`, `category`, `m49`. [Frozen source](../provenance/country_ontology.json): `BIT-ONT-GEO-2026.1`. | Jurisdiction review roster, not geometry or a physical-building denominator. Preserve leading zeros in M49. |

The sampler transforms longitude/latitude into each raster's CRS and indexes its actual pixels. It does not create a resampled raster or claim exact 30 m ground resolution everywhere. The Luxembourg receipt records `EPSG:4326` and 0.00025° pixels for both tiles. Point classification is not whole-building coverage.

Raw data belong in approved local/private cloud storage outside Git. Caller-supplied filenames do not authenticate lineage. The Luxembourg replay requires the exact historical bytes; repository access does not grant access to the private mirror. No credentials or signed URLs are recorded here. Dataset-specific reuse/licence terms and missing original acquisition dates must accompany future source acquisition; download availability alone does not establish redistribution rights.

## Committed evidence and outputs

| Artifact | Contents and interpretation |
|---|---|
| [Legacy CSV](../review/source/legacy_GABAM2024.csv) | Frozen negative-result table from `jianzbit/indicator-6-1-1-wildfire@92b84728ad3095949607311640132d82505378db`: 228 rows, 27 columns; 192 primary countries and 36 supplements, missing LBR/LKA/NRU. Masking/tile-selection defects preclude corrected national estimates. |
| [Review ledger](../review/conditional_research.json) | Conditions, checksums and all 195 primary countries. Null primary estimates are intentional missing results, not zeros. |
| [Luxembourg CSV](../review/luxembourg/LUX_GABAM2024.csv) | One row, 27 columns: 226,721 supplied/classified records and zero burned-code intersections. This does not establish absence of real fire or damage. |
| [Run manifest](../review/luxembourg/LUX_GABAM2024_manifest.json) | Input/output/code hashes and byte counts, runtime versions, missing-record bounds and scope warnings. |
| [Replay receipt](../review/luxembourg/independent_replay.json) | Archive membership, 226,721 distinct source IDs, independent raw-window comparison and raster metadata. This checks selected source-frame computation, not fire-detection accuracy. |

`src/wildfire_exposure/exposure.py::COUNTRY_RESULT_COLUMNS` defines the CSV: ISO3/year/source fields; supplied, coordinate-valid, tile-covered, binary-classified, unknown and exposed counts; denominator-specific percentages; tile/part/chunk counts and execution markers. Generic source-identity cells remain blank because local paths do not establish archive identity. Do not fill them from the legacy table without evidence. The generic manifest conservatively leaves archive completeness unverified; the separate Luxembourg receipt adds archive/ID checks for that case only.

## Missingness and unresolved evidence

Binary `1` is a mapped burned-area intersection; `0` is operational background. The retained rasters also declare nodata `0`, so this does not independently establish observation availability or observed unburned land. Invalid coordinates, outside points and invalid pixel codes stay unclassified.

For supplied records N, classified V, burned intersections H and unknown U = N − V, retain H/V where V > 0 and [H/N, (H+U)/N] where N > 0. These are conditional source-frame bounds, not confidence intervals or coverage bounds for omitted buildings. Optional 15/30 m cardinal perturbations sample five points, not a disk or footprint. One supplied CSV does not demonstrate multi-member archive completeness.

The Luxembourg result was previously inspected; it is neither a blind holdout nor a positive-detection test. Corrected national reruns, parent-ZIP lineage, observation availability and geographically representative independent accuracy evidence remain outstanding. Historic notebooks/HTML and earlier methodology are archival where they conflict with the current conditional review.

## Provenance checksums

SHA-256 values below were checked against committed bytes for this documentation update:

| File | SHA-256 |
|---|---|
| `config/countries.csv` | `a6154088b6ae81fd308cfafda4a8ea3090c17bb9d769876176a2dec82930afd6` |
| `provenance/country_ontology.json` | `936339f16bf0cf5dc7b842dbb84e69240b919841423a815307db9043643c82ad` |
| `review/source/legacy_GABAM2024.csv` | `96d87a21af5301d8e971d679efd466f9c83a8556d492ee9cf102dcf93053c9cb` |
| `review/conditional_research.json` | `61819016c197221aab37ca0dfb10ca00ee541ec552e53b643cd6c4461a1921a9` |
| `review/luxembourg/LUX_GABAM2024.csv` | `5ae286dd2d1b99e9300dbc68f35369962d71cf33355c3048d6c47c277d292a10` |
| `review/luxembourg/LUX_GABAM2024_manifest.json` | `2b4d8d98d9b5c4c9893c6a8e4f3d706ab6e828d588b23f9b14456327e0c51bca` |
| `review/luxembourg/independent_replay.json` | `3aa4aa7a8303105ed294faaf6d9f1335713bb2a9139a3718b7eb0aa6b0b2107c` |

External hashes below are retained receipt values; raw data were not downloaded or rehashed for this card:

| Input | SHA-256 |
|---|---|
| Luxembourg GHS-OBAT ZIP | `1034976556805f37961794794fd388769315754f7ff03b565a8a0c0f95a72edd` |
| Luxembourg GHS-OBAT CSV | `e91f9a833dc1b8b2b82544b3f1767001188f1ef2faf467e9ec43bde25342135a` |
| `N50E005.tif` | `ba5402ac25948b185c64efc3e65df1f44078ccef3705ba2c8147e2f7ffc83091` |
| `N55E005.tif` | `ce82106ca8122352147abb261e879a95e0f941f01fb9f9d3fdc1ff9b4ce36f66` |

The receipt pins replay implementation `c0e0128996acc8919aee7c0fa503849c0860d771` and reports a building-archive hash match with an independently acquired official JRC copy retained by indicator 6.1.5. Tile-to-Zenodo-ZIP lineage remains unverified. Future releases should append new evidence without overwriting this negative-result/pilot history.

## Reproduction

From the repository root, `python scripts/review_release.py --check` verifies the saved ledger, not national rasters. With verified external inputs, `python scripts/replay_luxembourg.py --inputs <verified-private-input-directory> --output <new-output-directory>` verifies input hashes and reruns the selected pilot. See [README](../README.md) for dependency setup. No new raw-data experiment was run to create this card.
