"""
exp_substrate_distill_verify_2_class_b_relationship_discrimination_cpu_v1.py -- CELL-DISTILL-VERIFY-2: the verifier must REFUSE to over-distill (soundness/discrimination half of the closed loop) -- CPU/local (no heat).

ROUTING: SKUNKWORKS handoff (skunkworks_to_exp_dev_DISTILL_PRESCREEN_5_dupes_are_KP_PROMOTION_PAIRS...). Skunkworks adversarially
  pre-screened its own DETECT list: the 5 flagged "duplicates" are KP P1 PROMOTION PAIRS (T3 source + T2 promotion, differ only in
  metadata.kp_p1_promotion) -> Class A, trivial schema-collapse, goes to Testbed (NOT a proof cell). The REAL proof-needing distill
  targets are Class B: operator GROUPS that share an output type / capability but are DIFFERENT operators. CELL-DISTILL-VERIFY-1 proved
  the verifier MERGES true duplicates; this cell (V2) proves the verifier REFUSES to merge mere capability-siblings and instead names the
  correct WEAKER relationship (shared-abstraction extraction vs theorem-link). That refusal-to-over-distill is what makes the self-
  improvement loop SOUND -- a loop that collapses adam into sgd would destroy capability. Ungated: atom-level algebra_dict + serves_capability
  (race-tolerant relations read for the theorem-derivation lookup); NOT SHARES_MATH / parser-v2 / codebook growth.

  Class B groups (from Skunkworks, confirmed against local index signatures):
    - optimizer FAMILY: gradient_descent(T1) + adam_optimizer(T3) + stochastic_gradient_descent(T3)
        same domain=convex_optimization, same output=parameter_vector, same cap_discriminative_perceptron; DIFFERENT operation_type.
        Expected: SHARED_ABSTRACTION (distill = extract abstract first-order-optimizer supertype + SPECIALIZES links; do NOT merge).
    - convolution-theorem pair: circular_convolution(T2) <-> discrete_fourier_transform(T3)
        IDENTICAL caps (cap_circular_convolution, cap_fhrr_bind) but DIFFERENT signatures (real_vector vs frequency_spectrum out).
        Expected: THEOREM_LINKED (related by conv = IDFT(DFT.x .* DFT.y)); PROVABLE only if the derivation chain is authored, else SOUND REFUSAL.

  RELATIONSHIP TAXONOMY (CHTV-1 typed reasoning; sound by construction):
    MERGEABLE          -- all members have a full typed signature, ALL identical, AND identical non-empty caps (collapse to one atom).
    SHARED_ABSTRACTION -- same output_type AND same domain, operation_type DIFFERS, caps consistent (common supertype; SPECIALIZES not merge).
    THEOREM_LINKED     -- identical non-empty caps but DIFFERENT output_type (related by an identity/theorem); merge REFUSED; derivation
                          asserted PROVABLE only if a relation chain links the pair, else UNPROVABLE_IN_GRAPH (sound refusal).
    DISTINCT           -- neither shared abstraction nor theorem link.

PRE-REGISTERED (soundness/discrimination is the bar): HARD-PASS iff ZERO Class B groups are MERGEABLE (the verifier never over-distills a
  distinct algorithm) AND the optimizer family is SHARED_ABSTRACTION AND the conv<->DFT pair is THEOREM_LINKED (all relationship classes
  correctly discriminated). MIDDLE_BAND iff 0 false-merge but >=1 relationship misclassified. HARD-FAIL iff ANY Class B group is MERGEABLE
  (unsound over-distillation -- would destroy a distinct operator). UNKNOWN if the targeted atoms are absent. ASCII-only. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple, List, Set
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_distill_verify_2_class_b_relationship_discrimination_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SIG_FIELDS = ("domain", "operation_type", "signature_input_type", "signature_output_type", "complexity_class")
# Class B groups (short ids). Each group = candidate distill set that is NOT a same-name duplicate.
CLASS_B = {
    "optimizer_family": ["gradient_descent", "adam_optimizer", "stochastic_gradient_descent"],
    "convolution_theorem": ["circular_convolution", "discrete_fourier_transform"],
}


def _short(x):
    return str(x).split("::")[-1].split("/")[-1].strip().lower()


def classify_group(sigs: List[dict], caps: List[Set[str]]) -> str:
    """CHTV-1 typed-relationship classification over a Class B candidate group (>=2 members)."""
    full = [s for s in sigs if len(s) >= 4]
    cap_ne = [c for c in caps if c]
    caps_ident = len(cap_ne) >= 2 and all(c == cap_ne[0] for c in cap_ne[1:])
    # MERGEABLE: every member fully typed, all identical, caps identical -> collapse to one atom
    if len(full) == len(sigs) and len(full) >= 2 and all(s == full[0] for s in full[1:]) and caps_ident:
        return "MERGEABLE"
    def field(f): return set(s.get(f) for s in sigs if s.get(f))
    out_types = field("signature_output_type"); domains = field("domain"); ops = field("operation_type")
    # SHARED_ABSTRACTION: one output_type, one domain, operation_type differs (common supertype; specialize, don't merge)
    if len(out_types) == 1 and len(domains) == 1 and len(ops) >= 2:
        return "SHARED_ABSTRACTION"
    # THEOREM_LINKED: identical caps but different output type (related by a provable identity/theorem)
    if caps_ident and len(out_types) >= 2:
        return "THEOREM_LINKED"
    return "DISTINCT"


def _selftest():
    base = {"domain": "convex_optimization", "operation_type": "x", "signature_input_type": "function_and_gradient",
            "signature_output_type": "parameter_vector", "complexity_class": "O(N) per step"}
    # MERGEABLE: identical full sigs + caps
    assert classify_group([dict(base), dict(base)], [{"c"}, {"c"}]) == "MERGEABLE"
    # SHARED_ABSTRACTION: same out+domain, op differs
    s2 = {**base, "operation_type": "y"}
    assert classify_group([dict(base), s2], [{"c"}, {"c"}]) == "SHARED_ABSTRACTION"
    # THEOREM_LINKED: identical caps, different output type
    conv = {"domain": "vsa", "operation_type": "binding", "signature_input_type": "real_vector_pair",
            "signature_output_type": "real_vector", "complexity_class": "O(N log N)"}
    dft = {"domain": "signal", "operation_type": "linear_transform", "signature_input_type": "discrete_signal",
           "signature_output_type": "frequency_spectrum", "complexity_class": "O(N log N)"}
    assert classify_group([conv, dft], [{"a", "b"}, {"a", "b"}]) == "THEOREM_LINKED"
    # DISTINCT: different out type, different caps
    assert classify_group([conv, dft], [{"a"}, {"z"}]) == "DISTINCT"
    print("[selftest] PASS: substrate_distill_verify_2_class_b_relationship_discrimination_cpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# A theorem is "derivable" only via a TYPED derivation edge -- a generic RELATES association is NOT a proof.
DERIV_RELS = {"DEPENDS_ON", "USES", "DERIVES", "DERIVED_FROM", "IMPLIES", "EQUALS", "EQUIVALENT_TO", "PROVES"}


def _derivation_links(root: Path, members_full: List[str]) -> bool:
    """Race-tolerant: is there a TYPED DERIVATION edge (not a generic RELATES) between two members -> the theorem is provably chained?"""
    shorts = set(_short(m) for m in members_full)
    for rp in root.rglob("relations.jsonl"):
        try:
            for ln in open(rp, encoding="utf-8"):
                ln = ln.strip()
                if not ln: continue
                try: r = json.loads(ln)
                except Exception: continue
                rt = (r.get("rel_type", "") or "").upper()
                if rt not in DERIV_RELS: continue            # generic RELATES / association does NOT prove the theorem
                s = _short(r.get("src_id", "")); t = _short(r.get("tgt_id", ""))
                if s in shorts and t in shorts and s != t:
                    return True
        except Exception:
            continue
    return False


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    from backend.substrate_index.partition import PartitionedStore
    # race-tolerant atom load
    by = defaultdict(list)
    for _ in range(5):
        try:
            for a in PartitionedStore(root).all_atoms():
                by[_short(a.id)].append(a)
            break
        except Exception:
            by = defaultdict(list); time.sleep(8)

    def alg(a):
        x = getattr(a, "algebra", None); return x if isinstance(x, dict) else {}

    groups = []
    for gname, shorts in CLASS_B.items():
        members = []
        for s in shorts:
            members.extend(by.get(s, []))
        if len(members) < 2:
            groups.append({"group": gname, "verdict": "UNKNOWN", "n_found": len(members), "expected": None})
            continue
        sigs = [{f: alg(a).get(f) for f in SIG_FIELDS if alg(a).get(f) is not None} for a in members]
        caps = [set(_short(c) for c in (getattr(a, "serves_capability", ()) or ())) for a in members]
        ids = [str(a.id) for a in members]
        rel = classify_group(sigs, caps)
        shared_caps = sorted(set.intersection(*caps)) if all(caps) else []
        deriv = None
        if rel == "THEOREM_LINKED":
            deriv = _derivation_links(root, ids)   # provable iff a relation chain is authored, else sound refusal
        groups.append({"group": gname, "verdict": rel, "n_found": len(members), "ids": ids,
                       "shared_caps": shared_caps, "out_types": sorted(set(s.get("signature_output_type") for s in sigs if s.get("signature_output_type"))),
                       "operation_types": sorted(set(s.get("operation_type") for s in sigs if s.get("operation_type"))),
                       "derivation_present": deriv})
    expected = {"optimizer_family": "SHARED_ABSTRACTION", "convolution_theorem": "THEOREM_LINKED"}
    n_mergeable = sum(1 for g in groups if g["verdict"] == "MERGEABLE")
    n_correct = sum(1 for g in groups if g["verdict"] == expected.get(g["group"]))
    n_eval = sum(1 for g in groups if g["verdict"] != "UNKNOWN")
    for g in groups:
        exp = expected.get(g["group"]); ok = "OK" if g["verdict"] == exp else ("MERGE!" if g["verdict"] == "MERGEABLE" else "miss")
        print("  %-22s -> %-18s (expected %-18s) [%s] caps=%s out=%s deriv=%s" % (
            g["group"], g["verdict"], exp, ok, g.get("shared_caps", [])[:2], g.get("out_types"), g.get("derivation_present")), flush=True)
    print("  Class B groups evaluated=%d | false-MERGEABLE=%d | correctly-discriminated=%d/%d" % (n_eval, n_mergeable, n_correct, n_eval), flush=True)
    bf = root / "bench_reports"; bf.mkdir(parents=True, exist_ok=True)
    (bf / "distill_verify_2_class_b_relationship.json").write_text(json.dumps({"groups": groups, "expected": expected,
        "n_mergeable": n_mergeable, "n_correct": n_correct, "n_eval": n_eval}, indent=2), encoding="utf-8")
    return {"groups": groups, "n_eval": n_eval, "n_mergeable": n_mergeable, "n_correct": n_correct, "expected": expected}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    if r["n_eval"] == 0:
        return ("UNKNOWN", "UNKNOWN: no Class B target atoms found in index (codebook may be mid-sync).")
    nm = r["n_mergeable"]; nc = r["n_correct"]; ne = r["n_eval"]
    gv = {g["group"]: g["verdict"] for g in r["groups"]}
    opt = gv.get("optimizer_family"); conv = gv.get("convolution_theorem")
    conv_deriv = next((g.get("derivation_present") for g in r["groups"] if g["group"] == "convolution_theorem"), None)
    s = ("Class B relationship discrimination (CHTV-1 typed reasoning): optimizer_family=%s, convolution_theorem=%s (derivation_present=%s). "
         "%d/%d groups correctly discriminated; false-MERGEABLE=%d. The convolution-theorem pair shares capability but has different typed "
         "signatures -> merge REFUSED; the identity conv=IDFT(DFT.x .* DFT.y) is asserted PROVABLE only if a relation chain links the pair "
         "(derivation_present), otherwise the verifier SOUNDLY refuses to assert an unproven theorem. The optimizer family shares output "
         "type+domain+capability but differs in algorithm -> SHARED_ABSTRACTION (extract a first-order-optimizer supertype + SPECIALIZES; "
         "do NOT merge distinct algorithms).") % (opt, conv, conv_deriv, nc, ne, nm)
    if nm == 0 and opt == "SHARED_ABSTRACTION" and conv == "THEOREM_LINKED":
        return ("HARD_PASS", "HARD_PASS (verifier is SOUNDLY DISCRIMINATIVE -- the over-distillation guard works): ZERO Class B groups marked "
                "MERGEABLE (never collapses a distinct algorithm), optimizer family correctly SHARED_ABSTRACTION, conv<->DFT correctly "
                "THEOREM_LINKED with merge refused%s. This is the soundness half of the closed loop: V1 showed the substrate MERGES true "
                "duplicates; V2 shows it REFUSES to over-distill capability-siblings and instead names the correct weaker relationship "
                "(abstraction extraction / theorem link). Distillation that preserves distinct operators by construction. " % (
                    " (derivation absent -> sound refusal to assert the theorem)" if conv_deriv is False else "") + s)
    if nm == 0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: no unsound over-distillation (0 false-MERGEABLE) but %d/%d relationships discriminated -- one class "
                "misclassified (optimizer=%s, conv=%s). Guard holds; taxonomy refinement needed. " % (nc, ne, opt, conv) + s)
    return ("HARD_FAIL", "HARD_FAIL: %d Class B group(s) marked MERGEABLE -- UNSOUND over-distillation; the verifier would collapse a distinct "
            "operator and destroy capability. The self-improvement loop's distill step is NOT safe. " % nm + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
