# Indicator 6.1.1 — Conditional burned-area exposure research

Version: conditional-review-2026-09-21. Current implementation repository: Building-Insights-Together/indicator-6.1.1-wildfire-risk. Legacy published snapshot: jianzbit/indicator-6-1-1-wildfire at `92b84728ad3095949607311640132d82505378db`.

**Status: conditional source-record diagnostics. One selected Luxembourg archive pilot is reproduced; global primary publication remains withheld.** See [evidence and conditions](CONDITIONAL_RESEARCH.md) and the reproducible 195-country ledger in `review/conditional_research.json`.

| Step | Current implementation and limits |
|---|---|
| 1. Scope | Supplied CSV records whose representative coordinates sample binary burned-area code 1 in GABAM 2024. This is exposure, not damage, wildfire attribution, annual probability or loss. |
| 2. Data | Caller-supplied CSV and raster files with actual hashes. GABAM v 3 publisher has 0.00025° nominal 30 m distribution. GHS-OBAT R2024A geometry and E2020 attributes are a mixed-vintage source frame. Local filenames do not authenticate archive lineage. |
| 3. Missingness | Invalid coordinates, outside pixels and invalid pixel codes stay unclassified. Binary zero is operational background; observation availability is not independently verified. Missing national results remain null. |
| 4. Structure | Single direct endpoint; no fitted composite, PCA or predictive cross-validation claimed. Shared pixels create correlated classifications; no empirical spatial error study has been run. |
| 5. Units | Record counts and percentages; no normalized score. Percent of all supplied records is a source-frame lower bound when unclassified records remain. |
| 6. Weighting | One input CSV row, one count. ID deduplication, floorspace and volume weighting are not implemented by this runner. |
| 7. Aggregation | Exposed H, classified V, supplied N, unknown U=N−V. Report H/V where V>0 and [H/N,(H+U)/N] bounds where N>0. These omit buildings absent from the supplied frame. |
| 8. Uncertainty | Centroid and four geodesic cardinal offsets at 15/30 m; five-point diagnostic, not disk/footprint coverage or statistical error interval. Full independent reference validation remains outstanding. |
| 9. Presentation | Do not publish legacy country values as corrected results. Keep 195 authoritative states, supplements separate, null primary values and explicit rerun conditions. |
| 10. Relationships | Related to other hazard-exposure indicators; no empirically established relationship or operational GFA denominator dependency is asserted. |

Reproduction: `python scripts/review_release.py --check`; `uv run pytest`; supplied-record execution through `python -m wildfire_exposure run`. The historical notebook and earlier methodology are archival context. The current implementation manifest records runtime, input/output and source-code hashes, incomplete archive/identity scope and missing-data bounds. A software pass is not scientific validation.

Selected-case evidence: [Luxembourg receipt](../review/luxembourg/independent_replay.json), 226,721 unique source IDs; production point sampling and independent raw-window indexing agree, with zero burned-code intersections. The earlier zero result was known; this is not a blind holdout or empirical global accuracy test.
