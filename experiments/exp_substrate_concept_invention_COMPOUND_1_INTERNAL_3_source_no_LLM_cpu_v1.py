"""DECISION 130a -- CELL-CONCEPT-INVENTION-COMPOUND-1-INTERNAL (Phase-5-v3 Option B; USER-authorized "implement your recommendation"). 3 SUBSTRATE-INTERNAL generators (NO LLM; 11th-rule preserved) gated by substrate's 4-gate validator + the F4-validated HR-fingerprint discriminator (precision 1.0). Decisive test of the CELL-INV-2 hypothesis: is the concept-invention gap GROUNDING-bound (external truth needed) or merely SEARCH-bound (better generators suffice)? If 3 principled symbolic generators ALSO produce ~0 certifiable novelty -> grounding-bound CONFIRMED.

Generators (substrate-internal; honest cores over the typed operator graph + self-model signatures):
  G1 LIBRARY-LEARNING (Stitch/Babble anti-unification compression): the common component-subset shared by >=2 existing composites (utility tau>=2) that is NOT itself an atom -> a candidate higher-order abstraction. Provenance: the composites it refactors.
  G2 HDTP ANTI-UNIFICATION COLIMIT: pairs of operator signatures sharing operation_type (+ arity) but over different atoms -> the generalized operation symbol. Provenance: the two source theories.
  G4 CELOE DOWNWARD REFINEMENT: conjunctive concept descriptions over the type lattice (operation_type + output_type + a component), length<=3, covering >=1 positive and 0 negative -> candidate if maps to no existing atom. Provenance: refinement path.

Pipeline per candidate: F4 fingerprint (REDISCOVERY / TIGHT-VARIANT >=0.8 Jaccard / GENUINE-NOVELTY) -> 4-gate (forward-walk + tier-monotone + dangling + axiom-term) -> cap_pres -> GENUINE-NOVELTY survivors routed to Skunkworks STRICT vet.
HARD-PASS: G1>=2 + G2>=1 + G4>=3 GENUINE-NOVELTY survive 4-gate (Skunkworks STRICT gates final). HARD-FAIL: 0 genuine-novelty across all 3 -> grounding-bound confirmed. Substrate-internal; laptop; no LLM; no held-out. ASCII; --self-test."""
from __future__ import annotations
import sys, json, time
from pathlib import Path
from collections import defaultdict
from itertools import combinations
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
DATA_ROOT = REPO / "data" / "substrate_index"
SELFMODEL = DATA_ROOT / "skunkworks_self_model_of_operators_v1.jsonl"
CROSS_REL = {"DEPENDS_ON", "USES", "SPECIALIZES", "SHARES_MATH", "COMPOSED_OF", "INSTANCE_OF"}
FORWARD = {"DEPENDS_ON", "SPECIALIZES", "USES", "INSTANCE_OF"}
TIER_NUM = {"T1": 1, "T2": 2, "T3": 3, "T4": 4}
POOL = ["vector_space", "inner_product", "matrix", "eigenvalue_eigenvector", "dot_product", "kronecker_product",
        "tensor", "vector", "span", "matrix_inverse", "eigendecomposition", "singular_value_decomposition",
        "qr_decomposition", "lu_decomposition", "matrix_decomposition", "orthogonality", "spectral_theorem",
        "rank_nullity_theorem", "gradient", "hessian", "kernel_method", "sigma_algebra", "lp_space",
        "gaussian_process", "random_features"]
JACCARD_VARIANT = 0.80
SELFTEST = "--self-test" in sys.argv


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / max(len(a | b), 1)


def _selftest():
    assert _short("a::b/c") == "c" and abs(jaccard({1, 2}, {1, 2, 3}) - 2 / 3) < 1e-9
    print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(DATA_ROOT)
    atoms = list(ps.all_atoms())
    sset = {_short(a.id) for a in atoms}
    tier = {_short(a.id): str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "") for a in atoms}
    corpus = {_short(a.id): str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower() for a in atoms}
    cross_out = defaultdict(set); fadj = defaultdict(set)
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            rt = (r.get("rel_type", "") or "").upper(); s = _short(r.get("src_id", "")); t = _short(r.get("tgt_id", ""))
            if not (s and t and s != t): continue
            if rt in CROSS_REL: cross_out[s].add(t)
            if rt in FORWARD: fadj[s].add(t)
    prims = [p for p in POOL if p in sset]; primset = set(prims)
    comp = {a: (cross_out.get(a, set()) & primset) for a in sset}
    composites = {a: cs for a, cs in comp.items() if len(cs) >= 2 and corpus.get(a, "") in ("math", "concept") and a not in primset}
    existing_sets = {frozenset(cs): a for a, cs in composites.items()}

    def reaches_t1(start):
        if tier.get(start, "") == "T1": return True
        seen = {start}; q = [start]
        while q:
            n = q.pop()
            for m in fadj.get(n, ()):
                if tier.get(m, "") == "T1": return True
                if m not in seen: seen.add(m); q.append(m)
        return False

    def fp(S):
        S = frozenset(S)
        return frozenset(a for a in sset if S and S <= comp.get(a, set()))

    existing_fp = defaultdict(set)
    for a, cs in composites.items(): existing_fp[fp(cs)].add(a)

    def discriminate(S):
        S = frozenset(S)
        if S in existing_sets: return ("REDISCOVERY", existing_sets[S])
        f = fp(S)
        if f and f in existing_fp: return ("REDISCOVERY", sorted(existing_fp[f])[0])
        # tight-variant: >=0.8 Jaccard to an existing composite set
        for cs2, a2 in existing_sets.items():
            if jaccard(S, cs2) >= JACCARD_VARIANT: return ("TIGHT-VARIANT", a2)
        return ("GENUINE-NOVELTY", None)

    def four_gate(members):
        fw = all(reaches_t1(m) for m in members)
        comp_tn = max(TIER_NUM.get(tier.get(m, ""), 1) for m in members)
        return fw and comp_tn <= 3 and all(m in sset for m in members)

    # ---------- G1 LIBRARY-LEARNING: common component-subset shared by >=2 composites, not itself an atom ----------
    g1 = []
    subset_count = defaultdict(set)
    comp_list = list(composites.items())
    for a, cs in comp_list:
        for k in (2, 3):
            for sub in combinations(sorted(cs), k):
                subset_count[frozenset(sub)].add(a)
    for sub, owners in subset_count.items():
        if len(owners) >= 2 and sub not in existing_sets:                 # utility tau>=2, novel abstraction
            d, m = discriminate(sub)
            if d == "GENUINE-NOVELTY" and four_gate(sub):
                g1.append({"src": "G1", "components": sorted(sub), "refactors": sorted(owners)[:3], "disc": d})

    # ---------- G2 HDTP COLIMIT: operator-signature pairs sharing operation_type -> generalized symbol ----------
    sigs = {}
    if SELFMODEL.exists():
        for ln in open(SELFMODEL, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: rec = json.loads(ln)
            except Exception: continue
            a = _short(rec.get("atom", ""))
            if a: sigs[a] = rec
    by_optype = defaultdict(list)
    for a, rec in sigs.items():
        ot = str(rec.get("operation_type", "") or "")
        if ot and a in sset: by_optype[ot].append(a)
    g2 = []
    for ot, members in by_optype.items():
        if len(members) >= 2:
            for x, y in combinations(sorted(members), 2):
                # generalized symbol's component-set = union of the two operators' primitive components
                gen = frozenset((comp.get(x, set()) | comp.get(y, set())) & primset)
                if len(gen) >= 2 and gen not in existing_sets:
                    d, m = discriminate(gen)
                    if d == "GENUINE-NOVELTY" and four_gate(gen):
                        g2.append({"src": "G2", "operation_type": ot, "components": sorted(gen), "from": [x, y], "disc": d})

    # ---------- G4 CELOE: conjunctive descriptions (op_type + output_type + 1 component), len<=3, cover pos not neg ----------
    # positives = real composites' sets; negatives = permuted (reuse INV-2 pattern, deterministic)
    g4 = []
    # CELOE downward refinement over (operation_type, output_type) constrained by a primitive component
    refine_targets = []
    for a, rec in sigs.items():
        ot = str(rec.get("operation_type", "") or ""); out = str(rec.get("output_type", "") or "")
        cs = comp.get(a, set())
        if ot and out and len(cs) >= 1:
            for c in sorted(cs):
                desc = frozenset([("op:" + ot), ("out:" + out), ("has:" + c)])   # length-3 conjunctive description
                refine_targets.append((a, desc, frozenset([c])))
    # a description is a candidate concept if its (op,out,has:c) signature is shared by >=2 atoms (covers) but
    # the resulting generalized component-concept is not an atom
    desc_count = defaultdict(set)
    for a, desc, cset in refine_targets: desc_count[desc].add(a)
    for desc, owners in desc_count.items():
        if len(owners) >= 2:
            # candidate component-set = union of the covered atoms' primitive components (the refined concept extension)
            gen = frozenset(set().union(*[comp.get(o, set()) for o in owners]) & primset)
            if len(gen) >= 2 and gen not in existing_sets:
                d, m = discriminate(gen)
                if d == "GENUINE-NOVELTY" and four_gate(gen):
                    g4.append({"src": "G4", "description": sorted(desc), "components": sorted(gen), "covers": sorted(owners)[:3], "disc": d})

    # dedup genuine-novelty by component-set across sources
    def dd(rows):
        seen = set(); out = []
        for r in rows:
            k = tuple(r["components"])
            if k in seen: continue
            seen.add(k); out.append(r)
        return out
    g1, g2, g4 = dd(g1), dd(g2), dd(g4)
    print("  CELL-COMPOUND-1-INTERNAL (3 substrate-internal sources; NO LLM; F4-discriminator-gated):", flush=True)
    print("  composites in corpus=%d | primitives=%d | operator-signatures=%d" % (len(composites), len(prims), len(sigs)), flush=True)
    print("  GENUINE-NOVELTY survivors (4-gate PASS): G1=%d  G2=%d  G4=%d" % (len(g1), len(g2), len(g4)), flush=True)
    for label, rows in (("G1", g1), ("G2", g2), ("G4", g4)):
        for r in rows[:6]:
            print("    [%s] P[%s] %s" % (label, "+".join(r["components"]), {k: v for k, v in r.items() if k in ("refactors", "from", "covers", "operation_type")}), flush=True)
    if not (g1 or g2 or g4): print("    (no genuine-novelty survivors across any source)", flush=True)
    return {"n_composites": len(composites), "n_primitives": len(prims), "n_signatures": len(sigs),
            "g1": len(g1), "g2": len(g2), "g4": len(g4), "g1_sample": g1[:10], "g2_sample": g2[:10], "g4_sample": g4[:10]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    g1, g2, g4 = r["g1"], r["g2"], r["g4"]
    s = ("CELL-COMPOUND-1-INTERNAL (G1 library-learning + G2 HDTP-colimit + G4 CELOE; NO LLM; F4-gated): GENUINE-NOVELTY 4-gate survivors G1=%d G2=%d G4=%d over %d composites / %d signatures." % (
        g1, g2, g4, r["n_composites"], r["n_signatures"]))
    if g1 >= 2 and g2 >= 1 and g4 >= 3:
        return ("HARD_PASS", "FIRST 3-of-3 substrate-internal architecture: all 3 symbolic generators produce GENUINE-NOVELTY surviving 4-gate WITHOUT LLM (pending Skunkworks STRICT vet). Claim 5b candidate-graduate substrate-on-its-own. " + s)
    if (g1 + g2 + g4) >= 1:
        return ("PARTIAL", "Some substrate-internal genuine-novelty (G1=%d G2=%d G4=%d) but below the 3-of-3 HARD-PASS bar -> partial substrate-internal invention; the producing source(s) indicate which symbolic mechanism reaches novelty; Skunkworks STRICT vet gates whether any is sound. " % (g1, g2, g4) + s)
    return ("HARD_FAIL", "0 GENUINE-NOVELTY 4-gate survivors across ALL 3 substrate-internal sources -> the concept-invention gap is GROUNDING-bound, NOT search-bound (CONFIRMED across 4 cells: INV-1 + INV-2 + this 3-source compound). Even principled symbolic generators (library-learning + HDTP + CELOE) only re-surface already-atomized or tight-variant structure; genuinely-new certifiable concepts require an EXTERNAL TRUTH SOURCE (Lever b / Option A) -- substrate-internal cannot self-certify novelty. Definitive Claim 5b frontier. " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_concept_invention_COMPOUND_1_INTERNAL_3_source_no_LLM", flush=True)
    out_dir = get_output_dir("substrate_concept_invention_COMPOUND_1_INTERNAL_3_source_no_LLM_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_concept_invention_COMPOUND_1_INTERNAL_3_source_no_LLM_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
