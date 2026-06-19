"""SHARES_MATH auto-discovery cell v1: 5 INDEPENDENT structural signals.

Per research_to_testbed_exp_dev_SHARES_MATH_auto_discovery_cell_DESIGN_*.md
(MASTER PLAN Phase 2 R2.2). Auto-discovers candidate SHARES_MATH edges between
atoms via 5 signals ORTHOGONAL to bge/codebook geometry (preserves P3 independence
from P4 sleep-replay).

Signals (all SYMBOLIC + STRUCTURAL + categorical; ZERO geometry):
  S1 algebra_fingerprint_overlap: shared {algebra dict key->value} pairs (e.g. both
     atoms have vsa_family=fhrr + operation_role=decompose). Adapts spec's
     axiom_overlap signal to actual substrate field population (algebra.axioms is
     sparse; algebra fingerprint pairs are well-populated for 242 atoms).
  S2 depends_on_shared_prereqs: jaccard of in-neighbors via DEPENDS_ON edge type.
  S3 serves_capability_overlap: jaccard of shared capability ids.
  S4 specialize_instance_cycle: A SPECIALIZES X and B INSTANCE_OF X -> bisim at
     categorical level; symmetric check.
  S5 category_tier_match: same metadata.science_algebra_category AND same tier ->
     categorical-functor analogous; partial match on category prefix lower score.

Candidate requires: >= MIN_SIGNAL_COUNT distinct signals + total_score >= MIN_TOTAL_SCORE.

Output: data/substrate_index/bench_reports/shares_math_auto_discovery_candidates.json

NO LLM. NO bge. NO torch. Pure structural; runs cpu-only; minutes wall.
"""
from __future__ import annotations
import sys
import json
import time
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


MIN_TOTAL_SCORE = 0.5
MIN_SIGNAL_COUNT = 2
TOP_K_OUTPUT = 500  # cap report size

# Algebra-dict keys whose value contributes to the structural fingerprint.
# These are SYMBOLIC tags (not floats); equality is meaningful.
FINGERPRINT_KEYS = (
    "structure", "domain", "vsa_family", "operation_role", "operation_type",
    "category_int", "signature_input_type", "signature_output_type",
    "preserves_unit_modulus", "has_inverse", "is_symmetric", "is_axiom",
    "process_property", "about_topic", "complexity_class",
)

OUT_PATH = Path("data/substrate_index/bench_reports/shares_math_auto_discovery_candidates.json")


def algebra_fingerprint(atom) -> set:
    """Build atom's structural fingerprint as set of (key, value) pairs from algebra dict."""
    alg = atom.algebra or {}
    fp = set()
    for k in FINGERPRINT_KEYS:
        v = alg.get(k)
        if v is None or v == "" or v == []:
            continue
        if isinstance(v, (list, tuple)):
            for item in v:
                fp.add((k, str(item)))
        else:
            fp.add((k, str(v)))
    return fp


def signal_algebra_fingerprint_overlap(fp_a: set, fp_b: set):
    if not fp_a or not fp_b:
        return None
    overlap = fp_a & fp_b
    if len(overlap) < 2:
        return None
    jaccard = len(overlap) / len(fp_a | fp_b)
    return {
        "signal": "algebra_fingerprint_overlap",
        "score": jaccard,
        "shared_count": len(overlap),
        "shared_sample": [list(t) for t in sorted(overlap)[:5]],
    }


def signal_depends_on_overlap(preds_a: set, preds_b: set):
    if not preds_a or not preds_b:
        return None
    overlap = preds_a & preds_b
    if len(overlap) < 2:
        return None
    jaccard = len(overlap) / len(preds_a | preds_b)
    return {
        "signal": "depends_on_shared_prereqs",
        "score": jaccard,
        "shared_count": len(overlap),
        "shared_sample": sorted(overlap)[:5],
    }


def signal_serves_capability_overlap(caps_a: set, caps_b: set):
    if not caps_a or not caps_b:
        return None
    overlap = caps_a & caps_b
    if len(overlap) < 2:
        return None
    jaccard = len(overlap) / len(caps_a | caps_b)
    return {
        "signal": "serves_capability_overlap",
        "score": jaccard,
        "shared_count": len(overlap),
        "shared_sample": sorted(overlap)[:5],
    }


def signal_specialize_instance_cycle(qid_a: str, qid_b: str, spec_out, inst_out):
    """A SPECIALIZES X and B INSTANCE_OF X (same X), or symmetric."""
    a_spec = spec_out.get(qid_a, set())
    b_inst = inst_out.get(qid_b, set())
    shared = a_spec & b_inst
    if shared:
        return {
            "signal": "specialize_instance_cycle",
            "score": 0.8,
            "shared_parent_class": sorted(shared)[:5],
            "direction": "a_specializes_b_instance_of",
        }
    b_spec = spec_out.get(qid_b, set())
    a_inst = inst_out.get(qid_a, set())
    shared = b_spec & a_inst
    if shared:
        return {
            "signal": "specialize_instance_cycle",
            "score": 0.8,
            "shared_parent_class": sorted(shared)[:5],
            "direction": "b_specializes_a_instance_of",
        }
    return None


def _coerce_category(v) -> str:
    """science_algebra_category may be str, list, or int; coerce to single category string."""
    if v is None:
        return ""
    if isinstance(v, (list, tuple)):
        return str(v[0]) if v else ""
    return str(v)


def signal_category_tier_match(atom_a, atom_b):
    cat_a = _coerce_category((atom_a.metadata or {}).get("science_algebra_category"))
    cat_b = _coerce_category((atom_b.metadata or {}).get("science_algebra_category"))
    if cat_a and cat_b and cat_a == cat_b and atom_a.tier == atom_b.tier:
        return {
            "signal": "category_tier_match",
            "score": 0.7,
            "shared_category": cat_a,
            "tier": atom_a.tier.value if hasattr(atom_a.tier, "value") else str(atom_a.tier),
        }
    if cat_a and cat_b:
        pa, pb = cat_a.split("::")[0], cat_b.split("::")[0]
        if pa == pb and atom_a.corpus == atom_b.corpus:
            return {
                "signal": "category_prefix_match",
                "score": 0.4,
                "shared_category_prefix": pa,
            }
    return None


def main():
    t0 = time.time()
    ps = PartitionedStore(Path("data/substrate_index"))
    atoms = ps.all_atoms()
    n = len(atoms)
    print(f"loaded {n} atoms from substrate")

    # --- Pre-compute per-atom structural fields once ---
    qids = [a.qualified_id for a in atoms]
    fingerprints = [algebra_fingerprint(a) for a in atoms]
    caps = [set(a.serves_capability or ()) for a in atoms]

    # Predecessors via DEPENDS_ON (per-atom set of in-neighbors).
    # Filter out provenance-style _history corpora -- those are decision/findings/research
    # log entries that show up as DEPENDS_ON via authoring trace, not genuine prereqs.
    HISTORY_PREFIXES = ("decision_history::", "findings_history::", "research_history::",
                        "exp_dev_history::", "testbed_history::", "session_history::")
    def _filter_prereqs(s: set) -> set:
        return {q for q in s if not any(q.startswith(p) for p in HISTORY_PREFIXES)}
    deps_pred = {}
    for q in qids:
        try:
            raw = ps.in_neighbors(q, RelationType.DEPENDS_ON) or set()
            deps_pred[q] = _filter_prereqs(raw)
        except Exception:
            deps_pred[q] = set()

    # Successors via SPECIALIZES and INSTANCE_OF (per-atom set of out-neighbors)
    spec_out = {}
    inst_out = {}
    for q in qids:
        try:
            spec_out[q] = ps.out_neighbors(q, RelationType.SPECIALIZES) or set()
        except Exception:
            spec_out[q] = set()
        try:
            inst_out[q] = ps.out_neighbors(q, RelationType.INSTANCE_OF) or set()
        except Exception:
            inst_out[q] = set()

    t_pre = time.time() - t0
    print(f"pre-compute done in {t_pre:.1f}s")

    # Coverage stats
    n_with_fp = sum(1 for fp in fingerprints if fp)
    n_with_caps = sum(1 for c in caps if c)
    n_with_deps = sum(1 for q in qids if deps_pred[q])
    n_with_spec = sum(1 for q in qids if spec_out[q])
    n_with_inst = sum(1 for q in qids if inst_out[q])
    print(f"  atoms with algebra fingerprint: {n_with_fp}")
    print(f"  atoms with serves_capability:   {n_with_caps}")
    print(f"  atoms with DEPENDS_ON preds:    {n_with_deps}")
    print(f"  atoms with SPECIALIZES out:     {n_with_spec}")
    print(f"  atoms with INSTANCE_OF out:     {n_with_inst}")

    # --- Pair iteration with prefilter ---
    # Prefilter: skip pairs where BOTH atoms have empty fp + caps + deps (no signal can fire).
    has_any_struct = [
        bool(fingerprints[i]) or bool(caps[i]) or bool(deps_pred[qids[i]])
        or bool(spec_out[qids[i]]) or bool(inst_out[qids[i]])
        for i in range(n)
    ]
    candidate_idx = [i for i in range(n) if has_any_struct[i]]
    nc = len(candidate_idx)
    print(f"prefilter: {nc} atoms have at least one structural field populated ({nc*(nc-1)//2} pairs)")

    candidates = []
    pair_count = 0
    fire_count = 0
    t1 = time.time()
    for ii in range(nc):
        i = candidate_idx[ii]
        qi, fpi, ci = qids[i], fingerprints[i], caps[i]
        pi_deps = deps_pred[qi]
        atom_a = atoms[i]
        for jj in range(ii + 1, nc):
            j = candidate_idx[jj]
            pair_count += 1
            qj = qids[j]
            atom_b = atoms[j]
            signals = []
            r = signal_algebra_fingerprint_overlap(fpi, fingerprints[j])
            if r: signals.append(r)
            r = signal_depends_on_overlap(pi_deps, deps_pred[qj])
            if r: signals.append(r)
            r = signal_serves_capability_overlap(ci, caps[j])
            if r: signals.append(r)
            r = signal_specialize_instance_cycle(qi, qj, spec_out, inst_out)
            if r: signals.append(r)
            r = signal_category_tier_match(atom_a, atom_b)
            if r: signals.append(r)

            if len(signals) >= MIN_SIGNAL_COUNT:
                total = sum(s["score"] for s in signals)
                if total >= MIN_TOTAL_SCORE:
                    fire_count += 1
                    candidates.append({
                        "atom_a": qi,
                        "atom_b": qj,
                        "name_a": atom_a.name,
                        "name_b": atom_b.name,
                        "tier_a": atom_a.tier.value if hasattr(atom_a.tier, "value") else str(atom_a.tier),
                        "tier_b": atom_b.tier.value if hasattr(atom_b.tier, "value") else str(atom_b.tier),
                        "total_score": round(total, 4),
                        "signal_count": len(signals),
                        "signals": signals,
                    })
        if ii > 0 and ii % 200 == 0:
            elapsed = time.time() - t1
            print(f"  progress: {ii}/{nc} outer atoms; {pair_count} pairs; {fire_count} candidates; {elapsed:.1f}s")

    candidates.sort(key=lambda c: -c["total_score"])
    t_total = time.time() - t0

    print(f"\n=== DISCOVERY SUMMARY ===")
    print(f"total atoms: {n}")
    print(f"candidate atoms (prefiltered): {nc}")
    print(f"pairs evaluated: {pair_count}")
    print(f"candidates (>={MIN_SIGNAL_COUNT} signals, total>={MIN_TOTAL_SCORE}): {fire_count}")
    print(f"wall time: {t_total:.1f}s")

    # Signal-type breakdown
    signal_counts = defaultdict(int)
    for c in candidates:
        for s in c["signals"]:
            signal_counts[s["signal"]] += 1
    print(f"\nsignal-type breakdown across candidates:")
    for k, v in sorted(signal_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {k}: {v}")

    # Tier distribution
    tier_pairs = defaultdict(int)
    for c in candidates:
        tier_pairs[(c["tier_a"], c["tier_b"])] += 1
    print(f"\ntop tier-pair distributions:")
    for k, v in sorted(tier_pairs.items(), key=lambda kv: -kv[1])[:8]:
        print(f"  {k}: {v}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "discovery_method": "5 independent structural signals (algebra_fingerprint_overlap + depends_on_shared_prereqs + serves_capability_overlap + specialize_instance_cycle + category_tier_match)",
        "independence_note": "ZERO bge / codebook cosine inputs; ZERO P4 geometry; orthogonal mechanism class (SYMBOLIC + STRUCTURAL + categorical)",
        "thresholds": {"min_total_score": MIN_TOTAL_SCORE, "min_signal_count": MIN_SIGNAL_COUNT},
        "atom_count": n,
        "candidate_atom_count_prefiltered": nc,
        "pairs_evaluated": pair_count,
        "candidate_count": fire_count,
        "wall_time_seconds": round(t_total, 1),
        "signal_breakdown": dict(signal_counts),
        "candidates": candidates[:TOP_K_OUTPUT],
        "candidates_truncated_to": TOP_K_OUTPUT if fire_count > TOP_K_OUTPUT else None,
    }
    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nwrote top {min(fire_count, TOP_K_OUTPUT)} candidates to {OUT_PATH}")
    print(f"(total candidates: {fire_count}; report capped at {TOP_K_OUTPUT})")


if __name__ == "__main__":
    main()
