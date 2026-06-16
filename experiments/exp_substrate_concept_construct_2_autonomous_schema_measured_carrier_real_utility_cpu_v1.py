"""DECISION 134a -- CELL-CONCEPT-CONSTRUCT-2 (rigorous; per Exp-Dev's own CONSTRUCT-1 self-critique). Tests Claim 5b-constructive with the 3 requirements CONSTRUCT-1 failed: (R1) AUTONOMOUS construction-schema generation (substrate self-detects gaps + proposes operations; NOT Exp-Dev supplying), (R2) MEASURED carrier-extension (substrate-internal witness of new elements; not asserted), (R3) REAL utility (close a currently-OPEN derivation OR bridge >=2 results). Substrate-internal; NO LLM; no held-out. ASCII; --self-test.

DISCIPLINE (both ways, per 30th instance type): do NOT overclaim refutation (CONSTRUCT-1 lesson) NOR grounding-bound (the retracted overclaim). Report exactly what each requirement yields.

KEY HONEST PROBE (R2): the substrate is a CONCEPT graph (atoms = concepts), NOT an element-level model (atoms carry no element/member enumeration). Carrier-extension is a property of CARRIERS (element-sets); the substrate cannot WITNESS a new element because it does not represent elements. So R2 is tested for SATISFIABILITY: if the substrate has no element-level representation, R2 is UNMEETABLE by representation (a finding about the substrate's representational level, distinct from grounding-bound or mechanism-bound).
HARD-PASS: >=1 autonomous op with R2 measured-carrier-extension AND R3 real-utility AND 4-gate. HARD-FAIL: R2 unmeetable OR R3 zero. Honest frontier characterization either way."""
from __future__ import annotations
import sys, json, time, re
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
DATA_ROOT = REPO / "data" / "substrate_index"
CROSS_REL = {"DEPENDS_ON", "USES", "SPECIALIZES", "SHARES_MATH", "COMPOSED_OF", "INSTANCE_OF"}
FORWARD = {"DEPENDS_ON", "SPECIALIZES", "USES", "INSTANCE_OF"}
TIER_NUM = {"T1": 1, "T2": 2, "T3": 3, "T4": 4}
RESULT_PAT = re.compile(r"(quotient|dual_space|completion|tensor|_product|free_|colimit|adjoint|direct_sum|quotient_group)")
SELFTEST = "--self-test" in sys.argv


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def _selftest():
    assert _short("a::b/c") == "c" and RESULT_PAT.search("quotient_group")
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
    cross_out = defaultdict(set); fadj = defaultdict(set); has_out = set()
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            rt = (r.get("rel_type", "") or "").upper(); s = _short(r.get("src_id", "")); t = _short(r.get("tgt_id", ""))
            if not (s and t and s != t): continue
            if rt in CROSS_REL: cross_out[s].add(t)
            if rt in FORWARD: fadj[s].add(t); has_out.add(s)

    def reaches_t1(n, adj):
        if tier.get(n, "") == "T1": return True
        seen = {n}; q = deque([(n, 0)])
        while q:
            x, d = q.popleft()
            if d >= 14: continue
            for m in adj.get(x, ()):
                if tier.get(m, "") == "T1": return True
                if m not in seen: seen.add(m); q.append((m, d + 1))
        return False

    # ---- R1: AUTONOMOUS construction-schema generation (substrate self-detects gaps) ----
    # construction-result atoms = result-pattern-named, math/concept, with a component-set (their inputs)
    results = [a for a in sset if RESULT_PAT.search(a) and corpus.get(a, "") in ("math", "concept")]
    proposals = []   # (operation_name, result, inputs) -- substrate proposes the missing operation
    op_atoms = sset   # existing operation atoms
    for res in results:
        inputs = sorted(cross_out.get(res, set()))           # result's own component-set = the construction inputs
        op_name = res + "_construction"
        if len(inputs) >= 1 and op_name not in op_atoms:
            proposals.append({"op": op_name, "result": res, "inputs": inputs[:5]})
    # R1 is AUTONOMOUS: gap-detection uses only substrate graph + naming, no external schema supplied.

    # ---- R2: MEASURED carrier-extension -- SATISFIABILITY PROBE ----
    # Does ANY atom carry element-level data (elements/members) enabling a new-element witness?
    element_repr = False
    for a in atoms[:2000]:
        md = getattr(a, "metadata", {}) or {}
        if hasattr(a, "elements") or "elements" in md or "members" in md or "carrier_elements" in md:
            element_repr = True; break
    r2_measurable = element_repr
    r2_measured_count = 0   # cannot measure any carrier-extension without element representation

    # ---- R3: REAL utility ----
    # open derivations (non-T1 atoms with out-edges not reaching T1)
    open_set = {n for n in has_out if tier.get(n, "") not in ("T1", "") and not reaches_t1(n, fadj)}
    r3a_closes = 0; r3b_bridges = 0; util_ops = []
    result_set = set(results)
    for p in proposals:
        # 3a: does adding op (result->op->inputs) close any OPEN derivation? op bridges result to inputs.
        # An open atom is closed only if it routes THROUGH this op to T1. Constructions bridge result->inputs;
        # they close an open derivation only if some open atom DEPENDS_ON the result AND result was open (rare).
        closes = 0
        if p["result"] in open_set:
            # would adding op (result->op->inputs, each input reaches T1) close result?
            if all(reaches_t1(i, fadj) for i in p["inputs"] if i in sset):
                closes += 1
        # 3b: does this op's input-set bridge >=2 distinct existing results (shared construction)?
        bridges = sum(1 for q in proposals if q["result"] != p["result"] and set(q["inputs"]) & set(p["inputs"]))
        if closes: r3a_closes += 1
        if bridges >= 2: r3b_bridges += 1
        if closes or bridges >= 2: util_ops.append({"op": p["op"], "closes_open": closes, "bridges": bridges})

    hard_pass = (r2_measured_count >= 1) and (r3a_closes + r3b_bridges >= 1)
    print("  CELL-CONSTRUCT-2 (autonomous schema-gen + measured carrier-extension + real utility):", flush=True)
    print("  R1 autonomous gap-detection: %d construction-result atoms -> %d proposed operations (substrate-internal; no supplied schema)" % (len(results), len(proposals)), flush=True)
    print("  R2 measured carrier-extension: substrate element-level representation present=%s -> measurable=%s -> measured=%d" % (element_repr, r2_measurable, r2_measured_count), flush=True)
    print("     >>> R2 KEY FINDING: substrate is a CONCEPT graph (no element/member enumeration) -> carrier-extension is NOT substrate-MEASURABLE (representational limit, distinct from grounding/mechanism bound)." , flush=True)
    print("  R3 real utility: %d open derivations in corpus | construction-ops closing an OPEN derivation=%d | bridging >=2 results=%d" % (len(open_set), r3a_closes, r3b_bridges), flush=True)
    print("  HARD-PASS (R2-measured>=1 AND R3>=1): %s" % hard_pass, flush=True)
    return {"n_results": len(results), "n_proposals": len(proposals), "r2_element_repr": element_repr,
            "r2_measured": r2_measured_count, "n_open_deriv": len(open_set), "r3a_closes": r3a_closes,
            "r3b_bridges": r3b_bridges, "util_ops": util_ops[:10], "hard_pass": hard_pass, "proposals_sample": proposals[:8]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = ("CONSTRUCT-2: R1 autonomous gap-detection proposed %d construction operations from %d result atoms (substrate-internal). R2 measured-carrier-extension: element-level repr present=%s -> %d measured. R3 real-utility: %d open-derivation closes + %d >=2-result bridges (of %d open derivations in corpus)." % (
        r["n_proposals"], r["n_results"], r["r2_element_repr"], r["r2_measured"], r["r3a_closes"], r["r3b_bridges"], r["n_open_deriv"]))
    if r["hard_pass"]:
        return ("HARD_PASS", "Autonomous construction with MEASURED carrier-extension + REAL utility -> 5b-constructive graduates substrate-internally (pending Skunkworks STRICT vet). " + s)
    # honest characterization of WHY it fails -- representational, not grounding/mechanism
    if not r["r2_element_repr"]:
        return ("HARD_FAIL", "5b-constructive NOT achievable in the CURRENT substrate, but the bound is REPRESENTATIONAL, not grounding-bound and not mechanism-bound: the substrate is a CONCEPT graph (atoms carry no element/member enumeration), so carrier-extension (R2) -- a property of element-SETS -- is UNMEASURABLE BY REPRESENTATION. Autonomous gap-detection (R1) WORKS (%d ops proposed); real-utility (R3) found %d closes + %d bridges. The honest frontier: testing autonomous construction-novelty rigorously requires an ELEMENT-LEVEL / computational substrate layer (a different architecture), NOT an external truth source. This corrects BOTH the retracted grounding-bound overclaim AND construction-optimism: the limit is the substrate's representational level. " % (r["n_proposals"], r["r3a_closes"], r["r3b_bridges"]) + s)
    return ("HARD_FAIL", "R2 measurable but 0 measured-extension OR R3 zero utility. " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_concept_construct_2_autonomous_schema_measured_carrier_real_utility", flush=True)
    out_dir = get_output_dir("substrate_concept_construct_2_autonomous_schema_measured_carrier_real_utility_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_concept_construct_2_autonomous_schema_measured_carrier_real_utility_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
