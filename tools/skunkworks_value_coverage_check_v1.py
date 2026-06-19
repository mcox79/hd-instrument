#!/usr/bin/env python3
"""Skunkworks 2026-06-19 -- VALUE-COVERAGE CHECK (the standing 'never overlook the
treasure trove' structural check; the durable answer to the USER value-mining concern).

A 5th cert-LENS alongside engine / checklist / invariant / integration:
  engine      = atomize-time per-atom cert-correctness (7 gates)
  checklist   = dispatch-time per-cell readiness
  invariant   = whole-Store cert-FLOOR (skunkworks_substrate_invariant_check)
  integration = cap-int Track-A correctness (skunkworks_capint_integration_check)
  VALUE-COVERAGE (this) = is the non-cert RESERVE being mined? Flags high-VALUE
     findings that are un-cert-graded + not yet onboarded, so they can never be
     silently overlooked (inst-242). Mechanizes the value x cert-gap triage rule.

It does NOT mutate. It RANKS the non-cert experiment_records by VALUE (relevance_tier
+ strategic-theme match + head-to-head-significance) and reports the top un-surfaced
high-value findings + coverage stats. Run periodically (e.g. with the invariant-check
cadence). The substrate is usually MORE capable than the cert-inventory implies; this
check keeps that surfaced.

Usage: python tools/skunkworks_value_coverage_check_v1.py [--top N] [--min-score S]
Read-only; ASCII.
"""
from __future__ import annotations
import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

# strategic-theme keywords (the substrate frontier; extend as themes evolve)
THEMES = {
    'depth_composition': ['resonator', 'cleanup', 'iterative', 'hopfield', 'depth', 'multihop', 'khop', 'compose', 'chain_depth'],
    'readout_capacity': ['readout', 'nonlinear', 'entmax', 'sparse', 'dim_expansion', 'whiten', 'pseudoinverse', 'pinv', 'capacity'],
    'glassbox_llm': ['minilm', 'llama', 'pythia', 'qwen', 'encoder', 'gen_lm', 'trigram', 'bigram', 'language_model', 'distill', 'generative', 'direct_gen'],
    'trust_integrity': ['refuse', 'provenance', 'attribution', 'hallucination', 'introspection', 'grounding', 'conformal', 'calibrat', 'coverage_guarantee', 'uncertainty'],
    'highval_caps': ['continual', 'catastrophic', 'oneshot', 'one_shot', 'rollback', 'transfer', 'superadd', 'world_model'],
}
HEADTOHEAD = ['headtohead', 'head_to_head', 'vs_qwen', 'vs_llm', 'beats', 'vs_gpt', 'vs_pythia', 'margin']
WIN_VERDICTS = {'PASS', 'HARD_PASS', 'ALREADY_SEPARATES', 'VALIDATED'}
# a finding counts as "surfaced/onboarded" if it's already cap-int integrated or has a queue marker
SURFACED_KEYS = ('capint_integrated', 'value_mine_queued', 'pull_up_queued')


def md(a):
    return getattr(a, 'metadata', {}) or {}


def kname(a):
    return a.kind.value if hasattr(a.kind, 'value') else str(a.kind)


def value_score(a):
    blob = (a.id + ' ' + str(getattr(a, 'name', '') or '') + ' ' + str(getattr(a, 'description', '') or '')).lower()
    themes = [t for t, kw in THEMES.items() if any(w in blob for w in kw)]
    rel = {'HIGH': 4, 'MEDIUM': 3}.get(md(a).get('relevance_tier'), 1)
    hp = 2 if (md(a).get('verdict') or '') == 'HARD_PASS' else 0
    h2h = 3 if any(w in blob for w in HEADTOHEAD) else 0  # beats-a-baseline = high strategic value
    return len(themes) * 2 + rel + hp + h2h, themes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--top', type=int, default=25)
    ap.add_argument('--min-score', type=int, default=8)
    args = ap.parse_args()

    ps = PartitionedStore(Path('data/substrate_index'))
    atoms = list(ps.all_atoms())
    exp = [a for a in atoms if kname(a) == 'experiment_record']
    noncert = [a for a in exp if md(a).get('provenance_quality') != 'CERT_CHAIN_GRADE']
    wins = [a for a in noncert if (md(a).get('verdict') or '').upper() in WIN_VERDICTS]
    # un-surfaced = not already cap-int integrated / queued
    unsurfaced = [a for a in wins if not any(md(a).get(k) for k in SURFACED_KEYS)]

    scored = sorted(((value_score(a)[0], value_score(a)[1], a) for a in unsurfaced), key=lambda t: -t[0])
    flagged = [t for t in scored if t[0] >= args.min_score]

    print('=' * 78)
    print('VALUE-COVERAGE CHECK v1 (5th cert-lens: is the non-cert reserve being mined?) -- READ-ONLY')
    print(f'  non-cert experiment_records: {len(noncert)} | non-cert WINS: {len(wins)} | un-surfaced wins: {len(unsurfaced)}')
    print(f'  un-surfaced wins by relevance_tier: {dict(Counter(md(a).get("relevance_tier") for a in unsurfaced))}')
    print(f'  HIGH-VALUE un-surfaced (score>={args.min_score}): {len(flagged)}  <-- the treasure-trove the queue must cover')
    print('-' * 78)
    print(f'TOP {args.top} un-surfaced high-value findings (score | themes | id | tier | verdict):')
    for s, th, a in scored[:args.top]:
        tag = 'FLAG' if s >= args.min_score else 'ok  '
        print(f'  [{tag}] {s:>2} {"+".join(th)[:26]:<26} {a.id.split("/")[-1][:42]:<42} | {md(a).get("relevance_tier")} {md(a).get("verdict")}')
    print('-' * 78)
    # coverage verdict: the check PASSES (informationally) by reporting; a high FLAG count = work-to-do, not a failure
    print(f'RESULT: VALUE-COVERAGE REPORT | {len(flagged)} high-value findings await onboarding/cert-grading '
          f'(rank by value x cert-gap; pull up by priority). Re-run each cycle -- the reserve is never silently overlooked.')
    print('=' * 78)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
