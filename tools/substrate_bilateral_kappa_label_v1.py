"""DECISION 131-approved bilateral kappa labeling tool (Track 1 pre-stage).

Per Skunkworks ITEM 1 design + 129a dispatch + 131 ACK:
  Skunkworks emits sealed sample (labeled) + blind version (src, tgt, rel_type,
                                                            src_tier, tgt_tier ONLY; shuffled)
  Testbed (this tool) blind-labels each edge: {STRUCTURALLY_VALID,
                                                UNDECIDABLE-or-PLAUSIBLE,
                                                NOT_VALID}
  After labeling: compute Cohen's kappa (3-cat + 2-cat collapse) + 95% CI
                  + per-label confusion matrix

Blindness discipline (per 110a/112a + 129a):
  Testbed sees ONLY (src, tgt, rel_type, src_tier, tgt_tier)
  Testbed does NOT see Skunkworks labels, rationale, source-batch, vet text
  Testbed labels BEFORE seeing Skunkworks labels (kappa computed after)

Usage modes:
  --blind  data/audit/<sample>.json  data/audit/<labels_out>.json
    -> reads blind sample; writes Testbed labels (no peeking at Skunkworks)
  --compute data/audit/<labels_testbed>.json data/audit/<labels_skunkworks>.json
    -> joins both label sets by edge_id; computes kappa + CI + confusion matrix
"""
from __future__ import annotations
import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path


LABELS_3CAT = ['STRUCTURALLY_VALID', 'UNDECIDABLE_or_PLAUSIBLE', 'NOT_VALID']
LABELS_2CAT = ['VALID', 'NOT_VALID']   # collapsing UNDECIDABLE+NOT_VALID -> NOT_VALID
                                        # OR UNDECIDABLE -> dropped (per Skunkworks design TBD)


def map_3cat_to_2cat_skunkworks_dropped(label: str) -> str | None:
    """Skunkworks recommended 2-cat collapse: drop UNDECIDABLE (PLAUSIBLE scarce);
    VALID = STRUCTURALLY_VALID; NOT_VALID = NOT_VALID."""
    if label == 'STRUCTURALLY_VALID':
        return 'VALID'
    if label == 'NOT_VALID':
        return 'NOT_VALID'
    return None  # UNDECIDABLE dropped from 2-cat


def cohen_kappa(rater_a: list, rater_b: list, categories: list) -> tuple[float, dict]:
    """Cohen's kappa for nominal categorical labels. Returns (kappa, confusion_matrix_dict)."""
    assert len(rater_a) == len(rater_b)
    n = len(rater_a)
    if n == 0:
        return float('nan'), {}
    # Observed agreement
    agreed = sum(1 for a, b in zip(rater_a, rater_b) if a == b)
    p_o = agreed / n
    # Expected agreement (chance)
    count_a = Counter(rater_a)
    count_b = Counter(rater_b)
    p_e = sum((count_a[c] / n) * (count_b[c] / n) for c in categories)
    if abs(1 - p_e) < 1e-12:
        kappa = 1.0 if p_o == 1.0 else 0.0
    else:
        kappa = (p_o - p_e) / (1 - p_e)
    # Confusion matrix: keys = (a_label, b_label) -> count
    cm = Counter(zip(rater_a, rater_b))
    cm_dict = {f'{a}|{b}': cm[(a, b)] for a in categories for b in categories}
    return kappa, cm_dict


def kappa_ci_95(kappa: float, n: int, p_o: float, p_e: float) -> tuple[float, float]:
    """Approximate 95% CI for kappa (Fleiss 1971 large-sample SE)."""
    if n < 2 or abs(1 - p_e) < 1e-12:
        return (float('nan'), float('nan'))
    se = math.sqrt(p_o * (1 - p_o) / (n * (1 - p_e) ** 2))
    return (kappa - 1.96 * se, kappa + 1.96 * se)


def landis_koch(kappa: float) -> str:
    if math.isnan(kappa):
        return 'undefined'
    if kappa < 0.0: return '<0 (poor)'
    if kappa < 0.20: return '0-0.20 (slight)'
    if kappa < 0.40: return '0.20-0.40 (fair)'
    if kappa < 0.60: return '0.40-0.60 (moderate)'
    if kappa < 0.80: return '0.60-0.80 (substantial)'
    return '0.80+ (almost perfect)'


def hard_pass_threshold(kappa: float) -> str:
    """Per DECISION 115b + 129a + Drill C pre-registration."""
    if math.isnan(kappa):
        return 'UNDEFINED'
    if kappa >= 0.65:
        return 'HARD_PASS (>=0.65 substantial; Landis-Koch)'
    if kappa <= 0.30:
        return 'HARD_FAIL (<=0.30 slight)'
    return 'MIDDLE_BAND (0.30-0.65 fair-to-moderate)'


def cmd_blind(blind_sample_path: Path, labels_out_path: Path):
    """Load blind sample; allow Testbed to label each edge; write labels."""
    with open(blind_sample_path) as f:
        sample = json.load(f)
    edges = sample.get('edges', sample.get('sample', []))
    print(f'Loaded {len(edges)} blind edges from {blind_sample_path}')
    print('Allowed labels:', LABELS_3CAT)
    print()
    print('Instructions (per 110a/129a discipline):')
    print('  STRUCTURALLY_VALID = relation textbook-correct; not fan-out artifact')
    print('  UNDECIDABLE_or_PLAUSIBLE = unclear / partial / mid-band')
    print('  NOT_VALID = relation wrong / mis-typed / authoring error')
    print()
    # Non-interactive: read labels from stdin JSONL OR via env var
    # In auto-execute mode, the actual labeling happens in a separate authored note
    # This scaffold is the kappa-compute side; the labeling side is done by Testbed
    # the LLM, recorded inline as a JSON output file
    out = {
        'description': 'DECISION 131 bilateral kappa Testbed blind labels',
        'source_blind_sample': str(blind_sample_path),
        'labels_3cat_allowed': LABELS_3CAT,
        'discipline': 'per 110a/129a: no consultation of Skunkworks labels/rationale/source-batch/vet',
        'edges': edges,  # blind edges (no labels yet; placeholder)
        'testbed_labels': []  # to be filled by authored labeling pass
    }
    labels_out_path.parent.mkdir(exist_ok=True, parents=True)
    with open(labels_out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'Wrote scaffold to {labels_out_path}; next: author Testbed labels in testbed_labels field')


def cmd_compute(testbed_labels_path: Path, skunkworks_labels_path: Path,
                output_report_path: Path):
    """Join Testbed + Skunkworks labels by edge_id; compute kappa + CI + confusion matrix."""
    with open(testbed_labels_path) as f:
        tb = json.load(f)
    with open(skunkworks_labels_path) as f:
        sk = json.load(f)
    # Build edge_id -> label maps
    tb_map = {}
    for label_entry in tb.get('testbed_labels', []):
        tb_map[label_entry['edge_id']] = label_entry['label']
    sk_map = {}
    for entry in sk.get('sealed_labels', sk.get('labels', [])):
        sk_map[entry['edge_id']] = entry['label']
    # Compute joint
    common = sorted(set(tb_map.keys()) & set(sk_map.keys()))
    tb_3cat = [tb_map[eid] for eid in common]
    sk_3cat = [sk_map[eid] for eid in common]

    # Skunkworks may use {STRICT, PLAUSIBLE, REJECT} categories; map to {VALID, UNDECIDABLE, NOT_VALID}
    sk_map_3cat = {'STRICT': 'STRUCTURALLY_VALID',
                   'PLAUSIBLE': 'UNDECIDABLE_or_PLAUSIBLE',
                   'REJECT': 'NOT_VALID'}
    sk_3cat = [sk_map_3cat.get(s, s) for s in sk_3cat]

    # 3-cat kappa
    kappa3, cm3 = cohen_kappa(tb_3cat, sk_3cat, LABELS_3CAT)
    # Recompute p_o, p_e for CI
    n3 = len(common)
    agreed3 = sum(1 for a, b in zip(tb_3cat, sk_3cat) if a == b)
    p_o3 = agreed3 / n3 if n3 else 0.0
    ca = Counter(tb_3cat); cb = Counter(sk_3cat)
    p_e3 = sum((ca[c] / n3) * (cb[c] / n3) for c in LABELS_3CAT) if n3 else 0.0
    ci3_lo, ci3_hi = kappa_ci_95(kappa3, n3, p_o3, p_e3)

    # 2-cat collapse (drop UNDECIDABLE per Skunkworks ITEM 1 design)
    tb_2 = [map_3cat_to_2cat_skunkworks_dropped(x) for x in tb_3cat]
    sk_2 = [map_3cat_to_2cat_skunkworks_dropped(x) for x in sk_3cat]
    paired_2 = [(a, b) for a, b in zip(tb_2, sk_2) if a is not None and b is not None]
    tb_2 = [a for a, _ in paired_2]
    sk_2 = [b for _, b in paired_2]
    kappa2, cm2 = cohen_kappa(tb_2, sk_2, LABELS_2CAT)
    n2 = len(tb_2)
    agreed2 = sum(1 for a, b in zip(tb_2, sk_2) if a == b)
    p_o2 = agreed2 / n2 if n2 else 0.0
    ca2 = Counter(tb_2); cb2 = Counter(sk_2)
    p_e2 = sum((ca2[c] / n2) * (cb2[c] / n2) for c in LABELS_2CAT) if n2 else 0.0
    ci2_lo, ci2_hi = kappa_ci_95(kappa2, n2, p_o2, p_e2)

    report = {
        'description': 'DECISION 131 bilateral kappa audit results',
        'sample_size_3cat': n3,
        'sample_size_2cat_drop_undecidable': n2,
        '3cat': {
            'categories': LABELS_3CAT,
            'cohen_kappa': kappa3,
            'p_observed': p_o3,
            'p_expected': p_e3,
            'ci_95_lo': ci3_lo,
            'ci_95_hi': ci3_hi,
            'landis_koch': landis_koch(kappa3),
            'hard_pass_threshold': hard_pass_threshold(kappa3),
            'confusion_matrix': cm3,
        },
        '2cat_drop_undecidable': {
            'categories': LABELS_2CAT,
            'cohen_kappa': kappa2,
            'p_observed': p_o2,
            'p_expected': p_e2,
            'ci_95_lo': ci2_lo,
            'ci_95_hi': ci2_hi,
            'landis_koch': landis_koch(kappa2),
            'hard_pass_threshold': hard_pass_threshold(kappa2),
            'confusion_matrix': cm2,
        },
        'same_family_residual_caveat': (
            'Per Drill C L4 / Li 2025 / Wataoka 2024: Testbed is same-LLM-family '
            'architecturally; ~50-60pct representation-level self-preference residual '
            'persists. Kappa BRIDGES from degenerate (one-rater) to measurable, but '
            'does NOT fully close self-preference floor. External (non-same-family) '
            'rater needed for full closure (USER-architectural).'
        ),
    }
    with open(output_report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f'Report written: {output_report_path}')
    print(f'\n3-cat kappa: {kappa3:.4f}  CI95=[{ci3_lo:.4f}, {ci3_hi:.4f}]  ({landis_koch(kappa3)})')
    print(f'2-cat kappa: {kappa2:.4f}  CI95=[{ci2_lo:.4f}, {ci2_hi:.4f}]  ({landis_koch(kappa2)})')
    print(f'\n3-cat verdict: {hard_pass_threshold(kappa3)}')
    print(f'2-cat verdict: {hard_pass_threshold(kappa2)}')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=['blind', 'compute'])
    p.add_argument('arg1')
    p.add_argument('arg2')
    p.add_argument('arg3', nargs='?', default='data/audit/131_bilateral_kappa_report.json')
    args = p.parse_args()
    if args.mode == 'blind':
        cmd_blind(Path(args.arg1), Path(args.arg2))
    elif args.mode == 'compute':
        cmd_compute(Path(args.arg1), Path(args.arg2), Path(args.arg3))


if __name__ == '__main__':
    main()
