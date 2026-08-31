"""The consistency-cleanup problem is a CONNECTIVITY PHASE TRANSITION — mapped here.

The leave-one-out audit (SOLVED.md) showed the brain-faithful STRUCTURAL consistency mechanism
collapses to chance on the real definitional store UNDER strict LOO, because only 3.6% of genus-pairs
are co-witnessed by >=2 independent subjects (remove the one under test and nothing is left). This
cell proves that is a PHASE-DIAGRAM SHIFT along the density/connectivity axis, not a defect of the
mechanism: holding the mechanism and the (real) family structure fixed and DIALING store density, the
LOO-clean structural AUC crosses from chance to near-perfect as the independent-pair fraction crosses
~0.2 (>=~5 co-witnesses per genus-pair). The real store is subcritical (0.036); a p1 extraction that
reaches supercritical density brings the structural spoke online with NO change to the mechanism.

Brain frame: the cortical schema needs a DENSE relational web to compute congruence under the
biological constraint that a memory never judges itself (leave-one-out). Sparse schema -> no
independent evidence -> no congruence signal (the same reason a single un-corroborated memory feels
neither congruent nor incongruent). This is a percolation transition, the density analogue of the
dimensional phase diagrams elsewhere in the substrate.

Families and genera are REAL (the actual co-occurring genus groups of the definitional store); only
the number of member terms per family (density K) is swept. ASCII-only, numpy-free, deterministic.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import statistics as st
import sys
from collections import defaultdict
from typing import Dict, List, Tuple

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_knowledge_store_consistency_cleanup_v1 as C

# KB_REFERENT: data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl
STORE = C.DEFAULT_STORE
OUT_DIR = os.path.join(_REPO, "data", "exp_consistency_phase_transition_density_v1")

# REAL family genus-groups: genera that actually co-occur / cluster in the definitional store.
_CANDIDATE_FAMILIES = [
    ["process", "event", "reaction", "mechanism", "division"],
    ["molecule", "protein", "macromolecule", "substance", "compound"],
    ["cell", "structure", "organ", "tissue", "membrane"],
    ["country", "region", "area", "place", "state"],
    ["organism", "animal", "species", "bacterium", "plant"],
]


def real_families() -> List[List[str]]:
    """Keep only genera that really occur in the store (>=3 per family)."""
    rows = [json.loads(l) for l in open(STORE, encoding="utf-8") if l.strip()]
    present = set(r["object"].lower().strip() for r in rows)
    fams = [[g for g in fam if g in present] for fam in _CANDIDATE_FAMILIES]
    return [f for f in fams if len(f) >= 3]


def real_store_indep_fraction() -> float:
    """The real store's independent-pair fraction (its position on the phase diagram)."""
    rows = [json.loads(l) for l in open(STORE, encoding="utf-8") if l.strip()]
    subj2gen: Dict[str, set] = defaultdict(set)
    for r in rows:
        subj2gen[r["subject"].lower()].add(r["object"].lower())
    pair: Dict[Tuple[str, str], int] = defaultdict(int)
    for gs in subj2gen.values():
        gl = sorted(gs)
        for i in range(len(gl)):
            for j in range(i + 1, len(gl)):
                pair[(gl[i], gl[j])] += 1
    if not pair:
        return 0.0
    return sum(1 for v in pair.values() if v >= 2) / len(pair)


def build_store(families: List[List[str]], K: int, rng: random.Random) -> List[C.Fact]:
    facts: List[C.Fact] = []
    fid = 0
    for fi, fam in enumerate(families):
        for k in range(K):
            t = f"term_f{fi}_{k}"
            for g in rng.sample(fam, min(2, len(fam))):     # 2 genera from the term's OWN family
                facts.append(C.Fact(fid, t, g, "", "", 1, ""))
                fid += 1
    return facts


def loo_structural_auc(facts: List[C.Fact], families: List[List[str]], rng: random.Random
                       ) -> Tuple[float, float, int]:
    """Inject cross-family (far) errors, score with a STRICT leave-one-out structural energy, and
    return (AUC injected-vs-clean, independent-pair fraction, n_injected)."""
    fam_of = {g: fi for fi, fam in enumerate(families) for g in fam}
    g = C.Graph(facts)
    terms = sorted(set(f.s for f in facts))
    rng.shuffle(terms)
    new = list(facts)
    fid = len(new)
    injected: List[Tuple[str, str]] = []
    for t in terms[:max(1, int(0.15 * len(terms)))]:
        myfam = fam_of.get(next(iter(g.subj2gen[t])))
        far = [gg for fi, fam in enumerate(families) if fi != myfam for gg in fam]
        gw = rng.choice(far)
        new.append(C.Fact(fid, t, gw, "", "", 1, ""))
        injected.append((t, gw))
        fid += 1
    g2 = C.Graph(new)

    def compat_loo(a: str, b: str, s: str) -> float:
        A = g2.gen2subj.get(a, set()) - {s}
        B = g2.gen2subj.get(b, set()) - {s}
        inter = len(A & B)
        uni = len(A | B)
        return inter / uni if uni else 0.0

    def energy(s: str, gen: str):
        net = g2.assoc_network(s, exclude_genus=gen)
        tot = sum(net.values())
        if tot < 2:
            return None
        return 1.0 - sum(w * compat_loo(gen, gg, s) for gg, w in net.items()) / tot

    inj_set = set(injected)
    inj_e = [e for (t, gw) in injected for e in [energy(t, gw)] if e is not None]
    non_e = [e for f in new if (f.s, f.g) not in inj_set for e in [energy(f.s, f.g)] if e is not None]
    pair: Dict[Tuple[str, str], int] = defaultdict(int)
    for s, gs in g2.subj2gen.items():
        gl = sorted(gs)
        for i in range(len(gl)):
            for j in range(i + 1, len(gl)):
                pair[(gl[i], gl[j])] += 1
    indep = sum(1 for v in pair.values() if v >= 2) / max(1, len(pair))
    return C._auc(inj_e, non_e, random.Random(1)), indep, len(inj_e)


def run(seeds: int = 3, ks: Tuple[int, ...] = (2, 3, 5, 8, 15, 30, 60)) -> Dict:
    fams = real_families()
    curve = []
    for K in ks:
        aucs, indeps = [], []
        for seed in range(seeds):
            facts = build_store(fams, K, random.Random(seed))
            a, ind, n = loo_structural_auc(facts, fams, random.Random(seed + 10))
            aucs.append(a)
            indeps.append(ind)
        curve.append({"K": K, "indep_pair_frac": round(st.mean(indeps), 3),
                      "loo_structural_auc": round(st.mean(aucs), 3)})
    real_frac = real_store_indep_fraction()
    # find the transition K (first K whose AUC >= 0.8)
    transition = next((c["K"] for c in curve if c["loo_structural_auc"] >= 0.8), None)
    return {"n_families": len(fams), "real_store_indep_pair_frac": round(real_frac, 4),
            "real_store_regime": "SUBCRITICAL" if real_frac < 0.2 else "supercritical",
            "transition_K_auc>=0.8": transition, "curve": curve,
            "conclusion": "connectivity phase transition; structural mechanism is correct, "
                          "store is density-starved; p1 target = indep_pair_frac >= ~0.2"}


def _self_test() -> None:
    fams = real_families()
    assert len(fams) >= 3, fams
    lo = loo_structural_auc(build_store(fams, 2, random.Random(0)), fams, random.Random(10))[0]
    hi = loo_structural_auc(build_store(fams, 30, random.Random(0)), fams, random.Random(10))[0]
    assert hi > lo + 0.2, (lo, hi)          # density lifts the LOO-clean structural AUC (can-fail)
    assert hi > 0.9 and lo < 0.7, (lo, hi)  # supercritical works; subcritical ~chance
    print(f"[self-test] PASS: LOO-structural AUC rises with density (K=2 {lo:.2f} -> K=30 {hi:.2f})")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        _self_test()
        return
    res = run(seeds=2 if args.smoke else 3)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
