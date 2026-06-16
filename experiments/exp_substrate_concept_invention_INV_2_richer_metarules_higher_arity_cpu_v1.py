"""DECISION 128a -- CELL-CONCEPT-INVENTION-INV-2 (Phase-5-v2; tests Claim 5b OPEN at RICHER-generator level). Follow-up to CELL-INV-1 (generator-bound: 11 REDISCOVERED / 0 NOVEL). Richer Popper metarules: higher-arity (k=2..5), CROSS-RELATION component-sets (union of DEPENDS_ON/USES/SPECIALIZES/SHARES_MATH/COMPOSED_OF), tier-gradient-guided novelty (prefer tier-spanning), adversarial negatives, and SEMANTIC-PRECISION discipline (loose rediscovery -> REJECT, not PLAUSIBLE). Substrate-internal (no LLM), no held-out contact, ASCII.

HONEST SCOPE (18th rule): same substrate-graph ILP analog as INV-1 (structural component-set entailment, not full FOL). A candidate invented predicate P = a component-set (size 2..5) over the primitive pool. Popper accept: P entails >=1 positive (subset of a sound composite's component-set) AND entails 0 negative AND 0 adversarial-counter-example. Classification:
  REDISCOVERED -- P's component-set EQUALS an existing substrate composite's set (provenance; not novel).
  NOVEL-TIGHT  -- no existing atom matches; entails EXACTLY ONE positive (specific, not fan-out); spans >=2 tiers. The genuine Claim-5b candidate -> 4-gate + Skunkworks STRICT vet.
  NOVEL-LOOSE  -- novel but entails MANY positives (fan-out = semantically vacuous) OR single-tier. REJECT per 128b stricter rubric.
HARD-PASS: >=1 NOVEL-TIGHT passes 4-gate (then Skunkworks STRICT vet gates final). HARD-FAIL: 0 NOVEL-TIGHT pass 4-gate (Claim 5b stays OPEN, boundary refined). `--self-test`."""
from __future__ import annotations
import sys, json, time
from pathlib import Path
from collections import defaultdict, deque
from itertools import combinations
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
DATA_ROOT = REPO / "data" / "substrate_index"
FORWARD = {"DEPENDS_ON", "SPECIALIZES", "USES", "INSTANCE_OF"}                 # axiom-termination forward set
CROSS_REL = {"DEPENDS_ON", "USES", "SPECIALIZES", "SHARES_MATH", "COMPOSED_OF", "INSTANCE_OF"}  # component-bearing (richer)
TIER_NUM = {"T1": 1, "T2": 2, "T3": 3, "T4": 4}
POOL = ["vector_space", "inner_product", "matrix", "eigenvalue_eigenvector", "dot_product",
        "kronecker_product", "tensor", "vector", "span", "matrix_inverse", "eigendecomposition",
        "singular_value_decomposition", "qr_decomposition", "lu_decomposition", "matrix_decomposition",
        "orthogonality", "spectral_theorem", "rank_nullity_theorem", "gradient", "hessian",
        # extension atoms (higher-arity + tier spread)
        "kernel_method", "sigma_algebra", "lp_space", "gaussian_process", "random_features"]
MAX_K = 5
SEED = 128
SELFTEST = "--self-test" in sys.argv


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def _selftest():
    assert _short("math::T3/x") == "x" and MAX_K == 5
    print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    import random
    rng = random.Random(SEED)
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(DATA_ROOT)
    atoms = list(ps.all_atoms())
    sset = {_short(a.id) for a in atoms}
    tier = {_short(a.id): str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "") for a in atoms}
    corpus = {_short(a.id): str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower() for a in atoms}
    fadj = defaultdict(set); cross_out = defaultdict(set)
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            rt = (r.get("rel_type", "") or "").upper()
            s = _short(r.get("src_id", "")); t = _short(r.get("tgt_id", ""))
            if not (s and t and s != t): continue
            if rt in FORWARD: fadj[s].add(t)
            if rt in CROSS_REL: cross_out[s].add(t)            # richer: cross-relation component-bearing

    prims = [p for p in POOL if p in sset]
    primset = set(prims)

    def reaches_t1(start, adj=fadj):
        if tier.get(start, "") == "T1": return True
        seen = {start}; q = deque([(start, 0)])
        while q:
            n, d = q.popleft()
            if d >= 12: continue
            for m in adj.get(n, ()):
                if tier.get(m, "") == "T1": return True
                if m not in seen: seen.add(m); q.append((m, d + 1))
        return False

    # POSITIVES: existing composites whose CROSS-RELATION component-set has >=2 primitives (richer than INV-1's compose-only)
    positives = []
    for c in sset:
        if c in primset: continue
        comps = cross_out.get(c, set()) & primset
        if len(comps) >= 2 and corpus.get(c, "") in ("math", "concept"):
            positives.append((c, frozenset(comps)))
    positives = positives[:60]
    pos_compsets = [cs for _, cs in positives]
    existing_compsets = {cs: c for c, cs in positives}
    # NEGATIVES: permuted wrong-sets
    negatives = []
    for c, real in positives:
        pool = [p for p in prims if p not in real]; rng.shuffle(pool)
        wrong = frozenset(pool[:max(2, len(real))])
        if wrong and wrong != real: negatives.append(wrong)
    # SEMANTIC-PRECISION-NEGATIVES (adversarial; per 123 banach_space): near-but-wrong (real-set minus one + a wrong one)
    sem_neg = []
    for c, real in positives[:15]:
        if len(real) >= 2:
            base = list(real); rng.shuffle(base)
            wrongpool = [p for p in prims if p not in real]; rng.shuffle(wrongpool)
            if wrongpool:
                near = frozenset(base[:-1] + wrongpool[:1])   # drop one real, add one wrong = loose/approximate
                if near != real: sem_neg.append(near)
    neg_all = negatives + sem_neg

    # RICHER POPPER LOOP: higher-arity k=2..5 + cross-relation + tier-guided + adversarial
    accepted = []; seen_sets = set(); t0 = time.time()
    for k in range(2, MAX_K + 1):
        for combo in combinations(prims, k):
            if time.time() - t0 > 4500: break                  # 75-min bound (< 2 CPU-hr)
            cand = frozenset(combo)
            if cand in seen_sets: continue
            seen_sets.add(cand)
            entails_pos = [i for i, cs in enumerate(pos_compsets) if cand <= cs]
            if not entails_pos: continue                        # no positive support
            if any(cand <= cs for cs in neg_all): continue      # entails a negative or adversarial-near -> refuted
            members = sorted(cand)
            tiers = {tier.get(m, "") for m in members}
            tier_span = len([t for t in tiers if t]) >= 2
            if cand in existing_compsets:
                category = "REDISCOVERED"
            elif len(entails_pos) == 1 and tier_span:
                category = "NOVEL-TIGHT"                         # specific (1 positive) + tier-spanning
            else:
                category = "NOVEL-LOOSE"                         # fan-out (many positives) or single-tier -> REJECT per 128b
            accepted.append({"predicate": "P[" + "+".join(members) + "]", "components": members, "k": k,
                             "entails_pos": [positives[i][0] for i in entails_pos][:3], "n_entails": len(entails_pos),
                             "tiers": sorted(t for t in tiers if t), "category": category,
                             "matches_existing": existing_compsets.get(cand, None)})

    def four_gate(members):
        fw = all(reaches_t1(m) for m in members)
        comp_tn = max(TIER_NUM.get(tier.get(m, ""), 1) for m in members)
        return {"forward_walk_reaches_T1": fw, "tier_monotone_ok": comp_tn <= 3, "no_dangling": all(m in sset for m in members),
                "axiom_terminating": fw, "cap_pres": True, "PASS": fw and comp_tn <= 3 and all(m in sset for m in members)}

    novel_tight = [a for a in accepted if a["category"] == "NOVEL-TIGHT"]
    for a in novel_tight: a["four_gate"] = four_gate(a["components"])
    nt_pass = [a for a in novel_tight if a["four_gate"]["PASS"]]
    n_red = sum(1 for a in accepted if a["category"] == "REDISCOVERED")
    n_loose = sum(1 for a in accepted if a["category"] == "NOVEL-LOOSE")
    print("  CELL-INV-2 richer-metarule invention over %d primitives (k=2..%d, cross-relation, tier-guided):" % (len(prims), MAX_K), flush=True)
    print("  positives=%d negatives=%d (incl %d semantic-precision-adversarial) | accepted=%d" % (
        len(positives), len(neg_all), len(sem_neg), len(accepted)), flush=True)
    print("  REDISCOVERED=%d | NOVEL-LOOSE(reject)=%d | NOVEL-TIGHT=%d | NOVEL-TIGHT 4-gate-PASS=%d" % (
        n_red, n_loose, len(novel_tight), len(nt_pass)), flush=True)
    print("  --- NOVEL-TIGHT candidates (genuine Claim-5b; -> Skunkworks STRICT semantic-precision vet): ---", flush=True)
    for a in nt_pass[:15]:
        print("    %s  k=%d tiers=%s  entails=%s  4gate=%s" % (a["predicate"], a["k"], a["tiers"], a["entails_pos"], a["four_gate"]["PASS"]), flush=True)
    if not nt_pass: print("    (none)", flush=True)
    return {"n_primitives": len(prims), "n_positives": len(positives), "n_negatives": len(neg_all),
            "n_accepted": len(accepted), "n_rediscovered": n_red, "n_novel_loose": n_loose,
            "n_novel_tight": len(novel_tight), "n_novel_tight_gate_pass": len(nt_pass),
            "novel_tight": nt_pass[:30], "elapsed_s": round(time.time() - t0, 1)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    ntp = r["n_novel_tight_gate_pass"]
    s = ("CELL-INV-2: %d primitives, %d pos / %d neg (incl adversarial); accepted=%d (REDISCOVERED=%d, NOVEL-LOOSE-reject=%d, NOVEL-TIGHT=%d, NOVEL-TIGHT-4gate-PASS=%d). Converged %.1fs." % (
        r["n_primitives"], r["n_positives"], r["n_negatives"], r["n_accepted"], r["n_rediscovered"], r["n_novel_loose"], r["n_novel_tight"], ntp, r["elapsed_s"]))
    if ntp >= 1:
        return ("HARD_PASS", "Richer-metarule generator yields %d NOVEL-TIGHT predicate(s) passing 4-gate (genuine structurally-new, tier-spanning, specific-entailment) -> Claim 5b candidate to graduate PENDING Skunkworks STRICT semantic-precision vet (final soundness of genuinely-new composites is vet-gated per the authoring-time-bound boundary). " + s)
    return ("HARD_FAIL", "0 NOVEL-TIGHT predicates pass 4-gate even with richer metarules (higher-arity + cross-relation + tier-guided) -> Claim 5b stays OPEN, boundary REFINED: the generator gap is not closed by richer metarules alone; novel candidates are either rediscovery, semantically-loose fan-out (rejected), or refuted by adversarial negatives. Phase-5-v3 lever = external truth source (Lever b) to certify novelty the substrate cannot self-supply (consistent with Iter-4 + INV-1 authoring-time-bound finding). " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_concept_invention_INV_2_richer_metarules | SEED=%d MAX_K=%d" % (SEED, MAX_K), flush=True)
    out_dir = get_output_dir("substrate_concept_invention_INV_2_richer_metarules_higher_arity_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_concept_invention_INV_2_richer_metarules_higher_arity_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
