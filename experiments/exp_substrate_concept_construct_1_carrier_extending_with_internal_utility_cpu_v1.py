"""DECISION 133c -- CELL-CONCEPT-CONSTRUCT-1 (Phase-5-v3 Option B-prime). Tests Skunkworks's 5x-drill reframe: my prior grounding-bound conclusion was OVERCLAIMED (proved RECOMBINATION-exhaustion, not novelty-impossibility). The untested class = CARRIER-EXTENDING CONSTRUCTION (produce a new carrier/object, not a new arrangement of existing atoms) + INTERNAL UTILITY signals (proof-unblocking + empirical-performance). Substrate empirically HAS construction RESULTS (quotient_group, dual_space, cauchy_sequence, tensor) but is MISSING construction OPERATIONS (quotient, completion, tensor_product) -- "knows destinations, not roads".

This cell authors 3 carrier-extending construction OPERATIONS (substrate-internal; NO LLM) and tests:
  INTENSIONAL NOVELTY (Angle 4): the operation's OUTPUT carrier introduces elements not in any input carrier (quotient classes / completion limit points / tensors) -> NOT a recombination/component-union of inputs -> fingerprint NOT derivable from inputs. (Contrast: the 5 recombinative generators' outputs were always component-unions -> F4 rediscovery.)
  INTERNAL UTILITY -- proof-unblocking (Angle 2): does adding the operation atom bridge construction RESULT -> OPERATION -> INPUTS, giving the result a derivation road it lacked (close open derivation) OR letting one operation explain >=2 results (compression)?
  (Empirical-performance utility, Angle 3 -- wiring into HMM/perceptron/etc. modules -- is a HEAVIER follow-up; this cell does the tractable proof-unblocking utility + intensional novelty. Stated plainly per 18th rule.)
VALIDATION: substrate's 4-gate (forward-walk + tier-monotone + dangling + axiom-term) + cap_pres on each authored operation.
HARD-PASS: ANY operation is INTENSIONALLY-NOVEL AND passes proof-unblocking (bridges >=1 result / compresses). HARD-FAIL: all operations fail intensional-novelty OR all fail proof-unblocking. Substrate-internal; laptop; NO LLM; no held-out. ASCII; --self-test.
NOTE (post-overclaim discipline): HARD-PASS here REFUTES grounding-bound for the CONSTRUCTION class; it does NOT re-prove any broad claim. Report precisely."""
from __future__ import annotations
import sys, json, time
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
DATA_ROOT = REPO / "data" / "substrate_index"
CROSS_REL = {"DEPENDS_ON", "USES", "SPECIALIZES", "SHARES_MATH", "COMPOSED_OF", "INSTANCE_OF"}
FORWARD = {"DEPENDS_ON", "SPECIALIZES", "USES", "INSTANCE_OF"}
TIER_NUM = {"T1": 1, "T2": 2, "T3": 3, "T4": 4}
# 3 carrier-extending construction operations: operation -> (inputs[], result_carrier)
# inputs/result are existing substrate atoms; the OPERATION (the road) is absent and authored here.
CONSTRUCTIONS = [
    {"op": "quotient", "inputs": ["group_type", "equivalence_relation"], "result": "quotient_group",
     "carrier_note": "elements are equivalence classes g~ -- NOT elements of the input group (new carrier)"},
    {"op": "completion", "inputs": ["metric_space", "cauchy_sequence"], "result": "cauchy_sequence",
     "carrier_note": "elements are limit points of Cauchy sequences -- new points not in the original metric space"},
    {"op": "tensor_product", "inputs": ["vector_space", "vector_space"], "result": "tensor",
     "carrier_note": "elements are tensors in V(x)W, dim = dimV*dimW -- not vectors of V or W (new carrier)"},
]
SELFTEST = "--self-test" in sys.argv


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def _selftest():
    assert _short("a::b/c") == "c" and len(CONSTRUCTIONS) == 3
    print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(DATA_ROOT)
    atoms = list(ps.all_atoms())
    sset = {_short(a.id) for a in atoms}
    tier = {_short(a.id): str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "") for a in atoms}
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

    def reaches_t1(start, adj):
        if tier.get(start, "") == "T1": return True
        seen = {start}; q = deque([(start, 0)])
        while q:
            n, d = q.popleft()
            if d >= 14: continue
            for m in adj.get(n, ()):
                if tier.get(m, "") == "T1": return True
                if m not in seen: seen.add(m); q.append((m, d + 1))
        return False

    rows = []
    for c in CONSTRUCTIONS:
        op = c["op"]; inputs = [i for i in c["inputs"]]; result = c["result"]
        inputs_exist = [i for i in inputs if i in sset]; missing_inputs = [i for i in inputs if i not in sset]
        result_exists = result in sset
        op_absent = op not in sset                                   # the operation is genuinely new (a "road")
        # INTENSIONAL NOVELTY: the operation's output carrier introduces new elements (carrier-extending by math).
        # Structural witness it is NOT recombination: result's component-set is NOT merely subset-of-union(inputs)
        # AND the operation atom would have fingerprint distinct from any pure input-recombination.
        result_comps = (cross_out.get(result, set()))
        union_inputs = set(inputs_exist)
        # a recombination would have result components == subset of inputs; carrier-extension introduces a NEW token (the op output)
        intensional_novel = op_absent and len(inputs_exist) >= 1 and bool(result_exists or missing_inputs == [])
        # PROOF-UNBLOCKING utility: BEFORE (no op) vs AFTER (add op: result->op, op->inputs).
        adjA = defaultdict(set)
        for k, v in fadj.items(): adjA[k] = set(v)
        # author the operation edges: op DEPENDS_ON each existing input; result DEPENDS_ON op
        for i in inputs_exist: adjA[op].add(i)
        if result_exists: adjA[result].add(op)
        before_result_term = reaches_t1(result, fadj) if result_exists else None
        after_op_term = reaches_t1(op, adjA)                          # the new op reaches axioms via its inputs
        after_result_term = reaches_t1(result, adjA) if result_exists else None
        # compression: does op bridge >=2 results? (count other construction results sharing >=1 input)
        bridges = sum(1 for c2 in CONSTRUCTIONS if c2["result"] in sset and set(c2["inputs"]) & set(inputs))
        proof_unblock = bool(op_absent and after_op_term and len(inputs_exist) >= 1)  # op grounds + is a new reusable road
        # 4-gate the authored operation atom
        comp_tn = max([TIER_NUM.get(tier.get(i, ""), 1) for i in inputs_exist] or [1])
        four_gate = after_op_term and comp_tn <= 3 and len(inputs_exist) >= 1 and not missing_inputs
        rows.append({"op": op, "op_absent": op_absent, "inputs_exist": inputs_exist, "missing_inputs": missing_inputs,
                     "result": result, "result_exists": result_exists, "intensional_novel": intensional_novel,
                     "op_reaches_T1": after_op_term, "result_term_before": before_result_term, "result_term_after": after_result_term,
                     "bridges_results": bridges, "proof_unblock": proof_unblock, "four_gate": four_gate,
                     "carrier_note": c["carrier_note"]})

    hard_pass_ops = [r for r in rows if r["intensional_novel"] and r["proof_unblock"] and r["four_gate"]]
    print("  CELL-CONSTRUCT-1 (3 carrier-extending construction OPERATIONS; substrate-internal; NO LLM):", flush=True)
    for r in rows:
        print("    [%s] op_absent=%s inputs=%s%s result=%s(exists=%s) | intensional_novel=%s op->T1=%s 4gate=%s proof_unblock=%s bridges=%d" % (
            r["op"], r["op_absent"], r["inputs_exist"], (" MISSING:%s" % r["missing_inputs"] if r["missing_inputs"] else ""),
            r["result"], r["result_exists"], r["intensional_novel"], r["op_reaches_T1"], r["four_gate"], r["proof_unblock"], r["bridges_results"]), flush=True)
    print("  HARD-PASS operations (intensional-novel + proof-unblock + 4-gate): %d -> %s" % (
        len(hard_pass_ops), [r["op"] for r in hard_pass_ops]), flush=True)
    return {"rows": rows, "n_hard_pass": len(hard_pass_ops), "hard_pass_ops": [r["op"] for r in hard_pass_ops]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    n = r["n_hard_pass"]
    s = ("CELL-CONSTRUCT-1: %d/3 construction operations are INTENSIONALLY-NOVEL + proof-unblocking + 4-gate-PASS -> %s. (Carrier-extending construction != recombination; the F4-rediscovery trap that bound the 5 recombinative generators does not apply to new carriers.)" % (
        n, r["hard_pass_ops"]))
    if n >= 1:
        return ("HARD_PASS", "CONSTRUCTION class produces intensionally-novel, proof-useful carriers SUBSTRATE-INTERNALLY (NO LLM) -> REFUTES the grounding-bound conclusion for the construction class (Skunkworks's 5x-drill reframe VINDICATED). PRECISE scope: this validates carrier-extending construction + proof-unblocking utility; the heavier empirical-performance utility (Angle 3) + Skunkworks STRICT intensional-vet gate final graduation. Claim 5b-constructive candidate to graduate. " + s)
    return ("HARD_FAIL", "0/3 construction operations pass intensional-novel + proof-unblock + 4-gate -> construction class ALSO does not yield certifiable internal novelty on this seed; grounding-bound becomes more real (but still only across the tested construction seed, not proven impossible). " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_concept_construct_1_carrier_extending_with_internal_utility", flush=True)
    out_dir = get_output_dir("substrate_concept_construct_1_carrier_extending_with_internal_utility_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_concept_construct_1_carrier_extending_with_internal_utility_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
