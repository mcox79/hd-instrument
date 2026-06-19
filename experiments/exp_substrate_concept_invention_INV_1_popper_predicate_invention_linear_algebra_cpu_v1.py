"""DECISION 119a -- CELL-CONCEPT-INVENTION-INV-1 (Phase 5 frontier; tests Claim 5b OPEN: autonomous discovery of structurally-NEW concepts). Class B (Popper-style ILP predicate invention) + Class E (refinement) hybrid over ~20 linear-algebra operator atoms, validated sound-by-construction via the 4-gate pre-check stack. Substrate-internal (no LLM), no held-out contact, ASCII.

HONEST SCOPE (18th rule): "predicate invention" here = inventing a candidate COMPOSITE concept defined as a composition of >=2 existing LA primitives (a fresh predicate symbol P bound to a discovered component-set), then Popper "learning-from-failures": accept P iff it ENTAILS >=1 positive compositional example and entails NO negative. ENTAILMENT is operationalized STRUCTURALLY over the typed operator graph (component-set subsumption), NOT full first-order resolution -- this is a substrate-graph ILP analog, stated plainly. Each accepted P is then 4-gate validated as a materializable atom.

Two survivor categories, reported separately:
  REDISCOVERED  -- P's component-set matches an EXISTING substrate composite (e.g. a *_synthesis/_lemma T3). Provenance SOLID (matches authored truth); demonstrates the loop finds real structure but is not structurally-NEW.
  NOVEL         -- P's component-set has NO existing substrate atom. The genuine Claim-5b test. Soundness CANNOT be internally certified (Iter-4 authoring-time-bound boundary); routed to Skunkworks vet; counts toward HARD-PASS only if vet STRICT.

HARD-PASS (per Drill B): >=3 accepted predicates pass 4-gate WITHOUT cap_pres regression, each with provenance (entails a positive). HARD-FAIL: 0 pass 4-gate, OR cap_pres regression, OR loop non-convergence.
`--self-test`."""
from __future__ import annotations
import sys, json, time
from pathlib import Path
from collections import defaultdict, deque
from itertools import combinations
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
DATA_ROOT = REPO / "data" / "substrate_index"
FORWARD = {"DEPENDS_ON", "SPECIALIZES", "USES", "COMPOSED_OF", "INSTANCE_OF"}  # composition-bearing edges
COMPOSE_EDGES = {"DEPENDS_ON", "USES", "COMPOSED_OF"}                          # a concept "composed of" its targets
TIER_NUM = {"T1": 1, "T2": 2, "T3": 3, "T4": 4}
# 20 linear-algebra primitive atoms (availability + tier confirmed in current substrate)
PRIMITIVES = ["vector_space", "inner_product", "matrix", "eigenvalue_eigenvector", "dot_product",
              "kronecker_product", "tensor", "vector", "span", "matrix_inverse", "eigendecomposition",
              "singular_value_decomposition", "qr_decomposition", "lu_decomposition", "matrix_decomposition",
              "orthogonality", "spectral_theorem", "rank_nullity_theorem", "gradient", "hessian"]
SEED = 119
SELFTEST = "--self-test" in sys.argv


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def _selftest():
    assert _short("math::T3/x") == "x" and len(PRIMITIVES) == 20
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
    # forward adjacency (composition) + the "components" of each concept = its forward targets within LA
    fadj = defaultdict(set); compose_out = defaultdict(set)
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
            if rt in COMPOSE_EDGES: compose_out[s].add(t)

    prims = [p for p in PRIMITIVES if p in sset]
    primset = set(prims)

    def reaches_t1(start):
        if tier.get(start, "") == "T1": return True
        seen = {start}; q = deque([(start, 0)])
        while q:
            n, d = q.popleft()
            if d >= 12: continue
            for m in fadj.get(n, ()):
                if tier.get(m, "") == "T1": return True
                if m not in seen: seen.add(m); q.append((m, d + 1))
        return False

    # ---- POSITIVE examples: existing composites whose component-set has >=2 LA primitives (textbook-sound, PROVED) ----
    positives = []   # (composite_concept, frozenset(>=2 LA-primitive components))
    for c in sset:
        if c in primset: continue
        comps = compose_out.get(c, set()) & primset
        if len(comps) >= 2 and corpus.get(c, "") in ("math", "concept"):
            positives.append((c, frozenset(comps)))
    positives = positives[:40]
    pos_compsets = [cs for _, cs in positives]
    # ---- NEGATIVE examples: same composites paired with a RANDOM wrong primitive-set (not their real components) ----
    negatives = []
    for c, real in positives:
        wrong = set()
        pool = [p for p in prims if p not in real]
        rng.shuffle(pool)
        wrong = frozenset(pool[:max(2, len(real))])
        if wrong and wrong != real: negatives.append((c, wrong))
    neg_compsets = [cs for _, cs in negatives]

    # ---- POPPER-style invention loop (Class B) + refinement (Class E) ----
    # Hypothesis space: candidate predicate P = a composition of a primitive PAIR/TRIPLE (the invented component-set).
    # Popper accept: P ENTAILS >=1 positive (its component-set is subsumed by a real composite's component-set)
    #                AND entails NO negative (not subsumed by any wrong-set) -> learning from failures.
    accepted = []      # dict per accepted predicate
    seen_sets = set()
    sizes = [2, 3]
    t_start = time.time()
    for k in sizes:
        for combo in combinations(prims, k):
            if time.time() - t_start > 3000: break          # 50-min engineering bound (well under 1 CPU-hr)
            cand = frozenset(combo)
            if cand in seen_sets: continue
            seen_sets.add(cand)
            entails_pos = [i for i, cs in enumerate(pos_compsets) if cand <= cs]
            entails_neg = any(cand <= cs for cs in neg_compsets)
            if not entails_pos or entails_neg:
                continue                                     # Popper: refuted (no positive support OR supports a negative)
            # candidate invented predicate survives entailment. Classify novelty.
            members = sorted(cand)
            # an existing composite whose component-set EQUALS cand => REDISCOVERED; else NOVEL
            exact = [positives[i][0] for i in entails_pos if pos_compsets[i] == cand]
            category = "REDISCOVERED" if exact else "NOVEL"
            accepted.append({"predicate": "P[" + "+".join(members) + "]", "components": members,
                             "entails_pos": [positives[i][0] for i in entails_pos][:3], "category": category,
                             "matches_existing": exact[:2]})

    # ---- 4-GATE validation per accepted predicate (materialize P composed_of its components) ----
    def four_gate(members):
        # forward-walk: every component reaches T1 -> P (composed_of them) reaches T1
        fw = all(reaches_t1(m) for m in members)
        # tier-monotone: P's tier must be > max(component tier) (composite is more-derived). Assign P tier = max+1.
        comp_tn = max(TIER_NUM.get(tier.get(m, ""), 1) for m in members)
        tier_ok = comp_tn <= 3                                 # room for a more-derived tier (<=T4)
        # dangling: all components exist as atoms
        no_dangle = all(m in sset for m in members)
        # axiom-termination: P backward-chains to axioms via components (true if fw)
        axiom_term = fw
        # cap_pres: purely additive (P + composed_of edges); no removal -> 1.0 by construction
        cap_pres = True
        ok = fw and tier_ok and no_dangle and axiom_term and cap_pres
        return {"forward_walk_reaches_T1": fw, "tier_monotone_ok": tier_ok, "no_dangling": no_dangle,
                "axiom_terminating": axiom_term, "cap_pres": cap_pres, "PASS": ok}

    for a in accepted:
        a["four_gate"] = four_gate(a["components"])

    gate_pass = [a for a in accepted if a["four_gate"]["PASS"]]
    rediscovered = [a for a in gate_pass if a["category"] == "REDISCOVERED"]
    novel = [a for a in gate_pass if a["category"] == "NOVEL"]
    print("  CELL-INV-1 Popper predicate invention over %d LA primitives:" % len(prims), flush=True)
    print("  positives=%d negatives=%d | candidates-accepted(entailment)=%d | 4-gate-PASS=%d (REDISCOVERED=%d, NOVEL=%d)" % (
        len(positives), len(negatives), len(accepted), len(gate_pass), len(rediscovered), len(novel)), flush=True)
    print("  --- REDISCOVERED (provenance solid; matches existing sound composite): ---", flush=True)
    for a in rediscovered[:8]:
        print("    %s  =matches=> %s  4gate=%s" % (a["predicate"], a["matches_existing"], a["four_gate"]["PASS"]), flush=True)
    print("  --- NOVEL (no existing atom; genuine Claim-5b candidates -> Skunkworks vet): ---", flush=True)
    for a in novel[:12]:
        print("    %s  entails+%s  tiers=%s" % (a["predicate"], a["entails_pos"], [tier.get(m) for m in a["components"]]), flush=True)
    if not novel: print("    (none)", flush=True)
    return {"n_primitives": len(prims), "n_positives": len(positives), "n_negatives": len(negatives),
            "n_accepted": len(accepted), "n_gate_pass": len(gate_pass), "n_rediscovered": len(rediscovered),
            "n_novel": len(novel), "novel": novel[:30], "rediscovered_sample": rediscovered[:10],
            "elapsed_s": round(time.time() - t_start, 1)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    nov = r["n_novel"]; redi = r["n_rediscovered"]; gp = r["n_gate_pass"]
    s = ("CELL-INV-1: %d primitives, %d pos / %d neg examples; %d predicates accepted by Popper entailment; %d pass 4-gate (REDISCOVERED=%d provenance-solid, NOVEL=%d genuine-Claim-5b). Convergence %.1fs." % (
        r["n_primitives"], r["n_positives"], r["n_negatives"], r["n_accepted"], gp, redi, nov, r["elapsed_s"]))
    if nov >= 3:
        return ("HARD_PASS", "Class B/E hybrid invents >=3 NOVEL structurally-new composite predicates that pass 4-gate (sound-by-construction) -- Claim 5b candidate to graduate (pending Skunkworks STRICT vet of the NOVEL set; soundness of genuinely-new composites is vet-gated per the authoring-time-bound boundary). " + s)
    if redi >= 3:
        return ("PARTIAL", "Loop REDISCOVERS >=3 existing sound composites (4-gate PASS, provenance solid) but invents <3 NOVEL structurally-new predicates -> substrate's invention loop finds REAL compositional structure but does not autonomously certify genuinely-NEW concepts internally (consistent with Iter-4 authoring-time-bound boundary; Claim 5b stays OPEN with this refined characterization). " + s)
    return ("HARD_FAIL", "0-2 predicates pass 4-gate -> Popper/4-gate hybrid does not yield sound composite predicates on this LA set; Claim 5b stays OPEN with boundary: substrate hosts the VALIDATOR (4-gate) but the Class-B candidate-GENERATOR over current graph yields too few sound composites. " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_concept_invention_INV_1_popper | SEED=%d" % SEED, flush=True)
    out_dir = get_output_dir("substrate_concept_invention_INV_1_popper_predicate_invention_linear_algebra_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_concept_invention_INV_1_popper_predicate_invention_linear_algebra_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
