"""Reproduce a bounded audit of the frozen legacy release; no raster rerun."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def review():
    source = ROOT/'review/source/legacy_GABAM2024.csv'
    roster = ROOT/'config/countries.csv'
    rows = list(csv.DictReader(source.open()))
    countries = list(csv.DictReader(roster.open()))
    by_iso = {r['iso3']: r for r in rows}
    assert len(by_iso) == len(rows), 'Duplicate source ISO3'
    assert len(countries) == len({r['iso3'] for r in countries}) == 195
    for r in rows:
        assert int(r['valid_gabam_pixel_buildings']) == int(r['exposed_buildings']), r['iso3']
    pilot = json.loads((ROOT/'review/luxembourg/independent_replay.json').read_text())
    assert pilot['passed'] and pilot['unique_ids'] == 226721
    assert all(v['passed'] and v['production'] == v['independent'] for v in pilot['comparisons'].values())
    assert pilot['comparisons']['exposed_buildings']['production'] == 0
    ledger = [{**c, 'research_status': 'selected_source_frame_pilot_only' if c['iso3'] == 'LUX' else 'awaiting_corrected_full_archive_rerun',
               'primary_exposure_percent': None,
               'selected_pilot_source_coded_exposure_percent': 0.0 if c['iso3'] == 'LUX' else None,
               'legacy_row_present': c['iso3'] in by_iso} for c in countries]
    return {
        'indicator_id': '6.1.1', 'research_level': 'conditional_source_record_diagnostics',
        'source_commit': '92b84728ad3095949607311640132d82505378db',
        'source_repository': 'jianzbit/indicator-6-1-1-wildfire',
        'checksums': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [source, roster]},
        'legacy_rows': len(rows), 'legacy_authoritative_countries': sum(r['legacy_row_present'] for r in ledger),
        'legacy_supplements': sorted(set(by_iso)-{c['iso3'] for c in countries}),
        'legacy_valid_pixels_equal_exposed_rows': len(rows),
        'corrected_published_country_results': 0,
        'reproduced_selected_source_frame_pilots': 1,
        'pilot_result_sha256': hashlib.sha256((ROOT/'review/luxembourg/independent_replay.json').read_bytes()).hexdigest(),
        'global_accuracy_validation': 'not established',
        'conditions': ['Regenerate original full country archives with corrected indexing and coding.',
                       'Verify binary-background observation semantics and actual archive provenance.',
                       'Audit record identity, physical inventory coverage and reference fire accuracy.'],
        'countries': ledger,
    }

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    value = json.dumps(review(), indent=2) + '\n'; target = ROOT/'review/conditional_research.json'
    if args.check:
        assert target.read_text() == value, 'Review differs; inspect inputs and regenerate.'
    else:
        target.write_text(value)
    print('195 country states audited; one selected Luxembourg pilot; legacy global outputs quarantined.')
