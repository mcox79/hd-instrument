"""Skunkworks 2026-06-19 -- cap-int INTEGRATION-CHECK cert-LAYER v1.

A NEW cert-layer alongside the other three:
  engine    = atomize-time per-atom cert-correctness (the 7 gates)
  checklist = dispatch-time per-cell readiness (the 7-item remote checklist)
  invariant = periodic whole-Store integrity (the cert-FLOOR; skunkworks_substrate_invariant_check)
  INTEGRATION (this) = capability-integration correctness (the cap-int Track-A cert-gate)

This asserts that capabilities INTEGRATED into Track-A (metadata-FIRST: cluster_id + interface_contract
+ current_best citation on the existing cert-grade evidence atoms; NO new AtomKind per Item-7) are
correctly integrated, per the 5 binding rigor rules from the cap-int per-row VET. Read-ONLY (asserts,
never mutates). Self-certification at the capability-MODEL layer (substrate-autonomy directive).

Detection: an atom is "cap-int Track-A integrated" iff metadata.capint_integrated is truthy (the marker
Track-A writes). Until Track-A populates, this reports "0 integrated -- layer ready" (graceful).

The 5 INTEGRATION checks (one per binding rule; I3/I4/I5 are the load-bearing cap-int-specific ones):
  I1 cert-grade-required: the integrated atom is CERT_CHAIN_GRADE (Track-A is cert-grade-only;
     non-cert evidence belongs in Track-B pull-up, not Track-A).
  I2 value-RESOLVES: capint_current_best_citation + the atom's evidence ids resolve to real atoms.
  I3 verdict-FAITHFUL (honest-scoped): capint_verdict is recorded AND the integration is faithful to it
     -- a HARD_FAIL / HONEST_NEGATIVE capability MUST be integrated as a BOUND (capint_is_bound True),
     NOT advertised as a win. Catches a negative dressed as a positive (the reasoning-gap failure mode).
  I4 cluster-CONSISTENCY: a scale-series is ONE capability, not N. Every member of a capint_cluster_id
     shares a cluster_id + shared_benchmark; each cluster has EXACTLY ONE canonical member
     (cluster_member_role=canonical); scale_points carry a cluster_id (no orphan scale-point minted as a
     standalone capability). Catches the 16-row q_a3_cross_layer series becoming 16 capabilities.
  I5 no-Goodhart (honest-scoped proven-bound): capint_proven_bound is present + non-empty -- the metric
     measures the CLAIMED thing (the honest bound), not a game-able proxy. Composes the no-Goodhart
     discipline atom (AUDIT_no_goodhart_..., inst 239) once it lands.

Usage: python tools/skunkworks_capint_integration_check_v1.py [--expect-integrated N]
Read-only; prints a report; exit 0 iff all HARD integration-checks pass (I1-I5 all hard once populated).
ASCII.
"""
from __future__ import annotations
import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

# verdicts that MUST integrate as a bound (not a win) -- verdict-faithful (I3)
BOUND_VERDICTS = {'HARD_FAIL', 'HONEST_NEGATIVE', 'HONEST_BOUNDED', 'MIDDLE_BAND', 'REFUTED', 'SATURATION',
                  'DISCRIMINATING_DEPTH_EXTENT'}  # v1.1: HONEST_BOUNDED + DISCRIMINATING_DEPTH_EXTENT (HYP-5 depth-bound) added (vocab-completeness from the retrieval-domain scan)
# v1.1: NEUTRAL verdicts = a characterization (invariance / non-result), NEITHER win NOR bound (e.g. sparsity has no
# effect; a non-discriminating non-test). Integrate honestly: is_bound=False + no win-language (don't dress as achievement).
NEUTRAL_VERDICTS = {'SPARSITY_NEUTRAL', 'NEUTRAL', 'INVARIANT', 'NO_EFFECT', 'DEGENERATE_REGIME', 'NON_TEST'}
# v1.1: WIN verdicts -- for I6 cross-class cluster detection.
WIN_VERDICTS = {'PASS', 'HARD_PASS', 'ALREADY_SEPARATES', 'VALIDATED', 'SPARSITY_NEUTRAL_LIFT'}
WIN_LANGUAGE = ('proven', 'achieves', 'demonstrates strong', 'validated strong', 'breakthrough', 'solves')


def kname(a):
    return a.kind.value if hasattr(a.kind, 'value') else str(a.kind)


def verdict_class(v):  # v1.1: classify a verdict for I6 cross-class cluster detection
    v = (v or '').upper()
    if v in BOUND_VERDICTS:
        return 'BOUND'
    if v in NEUTRAL_VERDICTS:
        return 'NEUTRAL'
    if v in WIN_VERDICTS:
        return 'WIN'
    return 'OTHER'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--expect-integrated', type=int, default=None)
    args = ap.parse_args()

    ps = PartitionedStore(Path('data/substrate_index'))
    atoms = list(ps.all_atoms())
    resolvable = set(ps.all_qualified_ids()) | {a.id for a in atoms}

    def md(a):
        return getattr(a, 'metadata', {}) or {}

    integ = [a for a in atoms if md(a).get('capint_integrated')]
    n = len(integ)

    checks = []  # (name, ok, detail, samples)
    # I1 cert-grade-required
    non_cert = [a.id for a in integ if md(a).get('provenance_quality') != 'CERT_CHAIN_GRADE']
    checks.append(('I1 cert-grade-required (Track-A is CERT_CHAIN_GRADE only)', not non_cert,
                   f'non_cert_integrated={len(non_cert)}', non_cert[:8]))
    # I2 value-RESOLVES (current_best citation + evidence ids)
    bad_refs = []
    for a in integ:
        for f in ('capint_current_best_citation', 'evidence_atom_ids', 'capint_evidence_atom_ids'):
            v = md(a).get(f)
            if not v:
                continue
            for ref in (v if isinstance(v, list) else [v]):
                if isinstance(ref, str) and ref not in resolvable and ref.split('::')[-1] not in resolvable:
                    bad_refs.append((a.id, f, ref))
    checks.append(('I2 value-RESOLVES (current_best + evidence cite real atoms)', not bad_refs,
                   f'unresolved_refs={len(bad_refs)}', bad_refs[:8]))
    # I3 verdict-FAITHFUL (honest-scoped: bound-verdict -> integrated as a bound, not a win)
    faithless = []
    for a in integ:
        v = (md(a).get('capint_verdict') or '').upper()
        if not v:
            faithless.append((a.id, 'NO_VERDICT'))
            continue
        name = (md(a).get('capint_capability_name') or a.id).lower()
        is_bound = md(a).get('capint_is_bound')
        if v in BOUND_VERDICTS:
            if not is_bound:
                faithless.append((a.id, f'{v}_not_marked_bound'))
            if any(w in name for w in WIN_LANGUAGE):  # a bound dressed with win-language
                faithless.append((a.id, f'{v}_with_win_language'))
        elif v in NEUTRAL_VERDICTS:  # v1.1: NEUTRAL = neither win nor bound -> is_bound False + no win-dressing
            if is_bound:
                faithless.append((a.id, f'{v}_marked_bound_but_NEUTRAL'))
            if any(w in name for w in WIN_LANGUAGE):
                faithless.append((a.id, f'{v}_NEUTRAL_with_win_language'))
    checks.append(('I3 verdict-FAITHFUL (bound->bound; neutral->neither; no win-dressing)', not faithless,
                   f'faithless={len(faithless)}', faithless[:8]))
    # I4 cluster-CONSISTENCY (scale-series = ONE capability)
    cluster_members = defaultdict(list)
    orphan_scale = []
    for a in integ:
        cid = md(a).get('capint_cluster_id')
        role = md(a).get('capint_cluster_member_role')
        if role == 'scale_point' and not cid:
            orphan_scale.append((a.id, 'scale_point_without_cluster_id'))
        if cid:
            cluster_members[cid].append((a.id, role, md(a).get('capint_shared_benchmark'), md(a).get('capint_verdict')))
    cluster_problems = list(orphan_scale)
    for cid, members in cluster_members.items():
        canon = [m for m in members if m[1] == 'canonical']
        if len(canon) != 1:
            cluster_problems.append((cid, f'{len(canon)}_canonical_members_expect_1'))
        benches = {m[2] for m in members if m[2]}
        if len(benches) > 1:
            cluster_problems.append((cid, f'cluster_spans_{len(benches)}_benchmarks'))
    checks.append(('I4 cluster-CONSISTENCY (scale-series=1 capability; 1 canonical/cluster)', not cluster_problems,
                   f'cluster_problems={len(cluster_problems)} clusters={len(cluster_members)}', cluster_problems[:8]))
    # I5 no-Goodhart (honest-scoped proven-bound present)
    no_bound = [a.id for a in integ if not (md(a).get('capint_proven_bound') or '').strip()]
    checks.append(('I5 no-Goodhart (honest-scoped proven_bound present; metric measures claimed thing)', not no_bound,
                   f'missing_proven_bound={len(no_bound)}', no_bound[:8]))
    # I7/I8/I9 (v1.2) -- A/B-iterate IMPROVE-track swap-discipline (DRILL_D M2). GATE-ON-POPULATE: these fire only
    # when a capability has a capint_superseded_chain (a current_best was swapped via an A/B-iterate). With 0 swaps
    # they pass trivially ("layer ready"), exactly like the whole check did before Track-A populated. Field schema
    # proposed to Research 2026-06-19 (coordinate before the A/B-iterate apply is built).
    pq_by_id = {}
    for a in atoms:
        pq_by_id[a.id] = md(a).get('provenance_quality')
        pq_by_id[a.id.split('::')[-1]] = md(a).get('provenance_quality')
    swapped = [a for a in integ if md(a).get('capint_superseded_chain')]
    n_swapped = len(swapped)
    # I7 superseded_chain-consistency: every prior current_best preserved + RESOLVES (no silent history loss).
    i7_bad = []
    for a in swapped:
        chain = md(a).get('capint_superseded_chain') or []
        for prior in (chain if isinstance(chain, list) else [chain]):
            if isinstance(prior, str) and prior not in resolvable and prior.split('::')[-1] not in resolvable:
                i7_bad.append((a.id, f'superseded_unresolved:{prior}'))
    checks.append(('I7 superseded_chain-consistency (swap history preserved + resolves) [v1.2; gate-on-populate]',
                   not i7_bad, f'swapped={n_swapped} unresolved_superseded={len(i7_bad)}', i7_bad[:8]))
    # I8 cert-grade-on-swap: the NEW current_best must itself be CERT_CHAIN_GRADE (cannot swap in a non-cert winner).
    i8_bad = []
    for a in swapped:
        cb = md(a).get('capint_current_best_citation')
        cb_id = cb if isinstance(cb, str) else None
        cb_pq = pq_by_id.get(cb_id) or pq_by_id.get((cb_id or '').split('::')[-1])
        if cb_pq != 'CERT_CHAIN_GRADE':
            i8_bad.append((a.id, f'current_best_not_cert:{cb_id}={cb_pq}'))
    checks.append(('I8 cert-grade-on-swap (new current_best is CERT_CHAIN_GRADE) [v1.2; gate-on-populate]',
                   not i8_bad, f'swapped={n_swapped} non_cert_winner={len(i8_bad)}', i8_bad[:8]))
    # I9 pre-reg-win-condition: the swap win-condition must be RECORDED (the no-Goodhart pre-reg discipline-marker;
    # a swap with no recorded win-condition is a candidate post-hoc "it scored higher"). Winner verdict-faithfulness
    # is already covered by I3 on the winner atom.
    i9_bad = []
    for a in swapped:
        if not (md(a).get('capint_swap_win_condition') or '').strip():
            i9_bad.append((a.id, 'no_swap_win_condition'))
    checks.append(('I9 pre-reg-win-condition (swap win-condition recorded; no post-hoc it-scored-higher) [v1.2; gate-on-populate]',
                   not i9_bad, f'swapped={n_swapped} missing_win_condition={len(i9_bad)}', i9_bad[:8]))
    # I6 (v1.1) cluster verdict-HOMOGENEITY -- SOFT FLAG (review, NOT a hard gate). A cluster spanning MULTIPLE
    # verdict-CLASSES (e.g. WIN + BOUND) is EITHER a legitimate scaling-cliff (capability degrades with scale)
    # OR a candidate-mis-cluster (distinct configs wrongly grouped -- the decomposition_resonator lesson).
    # Surface for cert-owner review: verify the canonical's proven_bound captures the spread + judge
    # cluster-vs-singletons. Uniform-class clusters (all WIN / all BOUND / all NEUTRAL) are clean.
    soft_checks = []
    mixed_clusters = []
    for cid, members in cluster_members.items():
        classes = {verdict_class(m[3]) for m in members}
        classes.discard('OTHER')
        if len(classes) > 1:
            mixed_clusters.append((cid, sorted(classes)))
    soft_checks.append(('I6 cluster verdict-homogeneity (mixed-class -> REVIEW: scaling-cliff vs mis-cluster)',
                        not mixed_clusters, f'mixed_verdict_clusters={len(mixed_clusters)}', mixed_clusters[:8]))

    # report
    print('=' * 78)
    print('CAP-INT INTEGRATION-CHECK v1.2 (capability-integration cert-gate; +I7/I8/I9 A/B-iterate) -- READ-ONLY')
    print(f'  cap-int Track-A integrated atoms = {n}'
          + ('' if args.expect_integrated is None else f' (expect {args.expect_integrated}: '
             + ("OK" if n == args.expect_integrated else "MISMATCH") + ')'))
    if n == 0:
        print('  (0 integrated -- Track-A not yet populated; layer READY. I1-I5 gate on populate.)')
    print('-' * 78)
    print('HARD checks (I1-I5; gate the result):')
    all_ok = True
    for name, ok, detail, samples in checks:
        all_ok = all_ok and ok
        tag = 'PASS' if ok else 'FAIL'
        print(f'  [{tag}] {name}  ({detail})')
        if not ok and samples:
            print(f'         samples: {samples}')
    print('SOFT flags (I6; review-only, do NOT gate):')
    n_soft = 0
    for name, ok, detail, samples in soft_checks:
        if not ok:
            n_soft += 1
        print(f'  [{"ok  " if ok else "FLAG"}] {name}  ({detail})')
        if not ok and samples:
            print(f'         review: {samples}')
    print('-' * 78)
    # distribution (informational)
    if n:
        print('  verdict distribution:', dict(Counter((md(a).get("capint_verdict") or "NONE") for a in integ)))
        print('  cluster count:', len(cluster_members), '| singletons:',
              sum(1 for a in integ if not md(a).get('capint_cluster_id')))
    print('RESULT:', 'INTEGRATION-PASS' if all_ok else 'INTEGRATION-FAIL',
          f'| integrated={n} | soft-flags(I6)={n_soft}')
    print('=' * 78)
    return 0 if all_ok else 5


if __name__ == '__main__':
    raise SystemExit(main())
