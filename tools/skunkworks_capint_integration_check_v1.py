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
BOUND_VERDICTS = {'HARD_FAIL', 'HONEST_NEGATIVE', 'MIDDLE_BAND', 'REFUTED', 'SATURATION'}
WIN_LANGUAGE = ('proven', 'achieves', 'demonstrates strong', 'validated strong', 'breakthrough', 'solves')


def kname(a):
    return a.kind.value if hasattr(a.kind, 'value') else str(a.kind)


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
        if v in BOUND_VERDICTS and not md(a).get('capint_is_bound'):
            faithless.append((a.id, f'{v}_not_marked_bound'))
        # a bound-verdict whose capability name carries win-language is a dressed negative
        name = (md(a).get('capint_capability_name') or a.id).lower()
        if v in BOUND_VERDICTS and any(w in name for w in WIN_LANGUAGE):
            faithless.append((a.id, f'{v}_with_win_language'))
    checks.append(('I3 verdict-FAITHFUL (bound-verdict integrated as bound, not a win)', not faithless,
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
            cluster_members[cid].append((a.id, role, md(a).get('capint_shared_benchmark')))
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

    # report
    print('=' * 78)
    print('CAP-INT INTEGRATION-CHECK v1 (capability-integration cert-gate) -- READ-ONLY')
    print(f'  cap-int Track-A integrated atoms = {n}'
          + ('' if args.expect_integrated is None else f' (expect {args.expect_integrated}: '
             + ("OK" if n == args.expect_integrated else "MISMATCH") + ')'))
    if n == 0:
        print('  (0 integrated -- Track-A not yet populated; layer READY. Checks I1-I5 will gate on populate.)')
    print('-' * 78)
    all_ok = True
    for name, ok, detail, samples in checks:
        all_ok = all_ok and ok
        tag = 'PASS' if ok else 'FAIL'
        print(f'  [{tag}] {name}  ({detail})')
        if not ok and samples:
            print(f'         samples: {samples}')
    print('-' * 78)
    # distribution (informational)
    if n:
        print('  verdict distribution:', dict(Counter((md(a).get("capint_verdict") or "NONE") for a in integ)))
        print('  cluster count:', len(cluster_members), '| singletons:',
              sum(1 for a in integ if not md(a).get('capint_cluster_id')))
    print('RESULT:', 'INTEGRATION-PASS' if all_ok else 'INTEGRATION-FAIL',
          f'| integrated={n}')
    print('=' * 78)
    return 0 if all_ok else 5


if __name__ == '__main__':
    raise SystemExit(main())
