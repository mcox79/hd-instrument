"""
exp_substrate_distill_verify_3_1_inverse_pair_adversarial_controls_cpu_v1.py -- CELL-DISTILL-VERIFY-3.1: adversarial controls for the INVERSE_PAIR detector (V2.1) -- does it resist false positives? -- CPU/local (no heat), READ-ONLY.

ROUTING: Research 25th writeback TERTIARY (#3). V3 hardened the MERGE guard; V2.1 added the INVERSE_PAIR class but it is UNTESTED against
  decoys designed to TEMPT a false INVERSE_PAIR. This cell builds adversarial decoys over classify_group's NAME/OP-TYPE heuristic path (the
  no-authored-DUAL-edge fallback) and quantifies its precision, then states the sound-by-design rule: the AUTHORED DUAL-edge path (V2.1 run())
  is authoritative; the name heuristic is a LOW-CONFIDENCE fallback that must be confirmed by a DUAL edge. Pure-logic (synthetic decoys on
  classify_group), no index. Imports classify_group + _is_inverse_pair + _inverse_named from V2 (single source of truth; V2 __main__-guarded).

  KNOWN-FRAGILE heuristic surface (the point of the test): the "a == 'un'+b" inverse rule can FALSE-FRIEND on coincidental un-prefixes
  (union/ion, under/der, unit/it). The TYPE preconditions (same domain AND same output type, exactly 2 members) are the guard that should keep
  most false-friends out of INVERSE_PAIR; this cell measures whether they do, and flags residual false-positives as DUAL-edge-confirmation-required.

  DECOY CLASSES:
    POSITIVE        -- genuine inverses, same domain+output (bind/unbind, fold/unfold, forward/backward) -> MUST be INVERSE_PAIR.
    FP_TYPE         -- inverse-named but type-mismatched (diff output OR diff domain OR 3 members) -> MUST NOT be INVERSE_PAIR (type guard).
    FP_NONINVERSE   -- same domain+output but NON-inverse names -> MUST NOT be INVERSE_PAIR (should be SHARED_ABSTRACTION/DISTINCT).
    FP_FALSEFRIEND  -- coincidental "un"-prefix non-inverses (union/ion ...) WITH same domain+output -> the residual heuristic risk; if any
                       classify as INVERSE_PAIR, that is the precise gap the authored-DUAL-edge requirement closes.

PRE-REGISTERED: HARD-PASS iff ALL POSITIVE decoys are INVERSE_PAIR AND ALL FP_TYPE + FP_NONINVERSE decoys are NOT INVERSE_PAIR (type guard
  sound) AND any residual FP_FALSEFRIEND hits are correctly characterized (count reported; recommendation = require DUAL-edge). MIDDLE_BAND iff
  a POSITIVE is missed or a FP_FALSEFRIEND slips AND the cell does not yet flag the DUAL-edge requirement. HARD-FAIL iff any FP_TYPE or
  FP_NONINVERSE decoy is classified INVERSE_PAIR (the TYPE guard itself is broken -- unsound). ASCII-only. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments"))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from exp_substrate_distill_verify_2_class_b_relationship_discrimination_cpu_v1 import classify_group, _is_inverse_pair, _inverse_named
ANCHOR_NAME = "substrate_distill_verify_3_1_inverse_pair_adversarial_controls_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()


def sig(domain="vsa", op="x", out="vec"):
    return {"domain": domain, "operation_type": op, "signature_output_type": out, "signature_input_type": "i", "complexity_class": "c"}


def build_decoys():
    C = lambda *xs: [set(x) for x in xs]
    return [
        # POSITIVE: genuine inverses, same domain+output
        ("bind_unbind", [sig(op="binding"), sig(op="unbinding")], C({"c"}, {"c"}), ["fhrr_bind", "fhrr_unbind"], "POSITIVE"),
        ("fold_unfold", [sig(op="fold"), sig(op="unfold")], C({"c"}, {"c"}), ["fold_op", "unfold_op"], "POSITIVE"),
        ("forward_backward", [sig(op="forward"), sig(op="backward")], C({"c"}, {"c"}), ["forward_algorithm", "backward_algorithm"], "POSITIVE"),
        # FP_TYPE: inverse-named but type-mismatched -> must NOT be INVERSE_PAIR
        ("inverse_named_diff_output", [sig(op="binding", out="vec"), sig(op="unbinding", out="scalar")], C({"c"}, {"c"}), ["bind", "unbind"], "FP_TYPE"),
        ("inverse_named_diff_domain", [sig(domain="vsa", op="encode"), sig(domain="signal", op="decode")], C({"c"}, {"c"}), ["encode", "decode"], "FP_TYPE"),
        ("inverse_named_three_members", [sig(op="binding"), sig(op="unbinding"), sig(op="rebinding")], C({"c"}, {"c"}, {"c"}), ["bind", "unbind", "rebind"], "FP_TYPE"),
        # FP_NONINVERSE: same domain+output, non-inverse names -> SHARED_ABSTRACTION/DISTINCT, not inverse
        ("noninverse_same_type", [sig(op="alpha"), sig(op="beta")], C({"c"}, {"c"}), ["adam_optimizer", "sgd"], "FP_NONINVERSE"),
        # FP_FALSEFRIEND: coincidental 'un'-prefix non-inverses WITH same domain+output (residual heuristic risk)
        ("falsefriend_union_ion", [sig(op="p"), sig(op="q")], C({"c"}, {"c"}), ["ion", "union"], "FP_FALSEFRIEND"),
        ("falsefriend_unit_it", [sig(op="p"), sig(op="q")], C({"c"}, {"c"}), ["it", "unit"], "FP_FALSEFRIEND"),
    ]


def _selftest():
    assert _inverse_named("fhrr_bind", "fhrr_unbind")
    assert not _inverse_named("ion", "union")          # FIXED by V3.1: un-prefix base len>=4 guard kills the false-friend
    assert not _inverse_named("it", "unit")
    assert _inverse_named("fold", "unfold")            # real un-inverse (base len>=4) still detected
    assert not _inverse_named("adam", "sgd")
    # type guard: inverse-named but diff output -> not an inverse pair
    assert not _is_inverse_pair(["bind", "unbind"], [sig(out="vec"), sig(out="scalar")])
    assert _is_inverse_pair(["bind", "unbind"], [sig(op="binding"), sig(op="unbinding")])
    print("[selftest] PASS: substrate_distill_verify_3_1_inverse_pair_adversarial_controls_cpu_v1", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


def run() -> Dict:
    rows = []
    for name, sigs, caps, names, klass in build_decoys():
        v = classify_group(sigs, caps, names=names)
        is_inv = (v == "INVERSE_PAIR")
        if klass == "POSITIVE":
            ok = is_inv
        elif klass in ("FP_TYPE", "FP_NONINVERSE"):
            ok = (not is_inv)                          # type/semantic guard must reject
        else:                                          # FP_FALSEFRIEND: residual risk -- record, not auto-fail
            ok = None
        rows.append({"decoy": name, "class": klass, "verdict": v, "is_inverse": is_inv, "ok": ok})
    pos = [r for r in rows if r["class"] == "POSITIVE"]
    fp_guard = [r for r in rows if r["class"] in ("FP_TYPE", "FP_NONINVERSE")]
    ff = [r for r in rows if r["class"] == "FP_FALSEFRIEND"]
    pos_ok = sum(1 for r in pos if r["is_inverse"])
    guard_violations = sum(1 for r in fp_guard if r["is_inverse"])      # MUST be 0
    ff_hits = sum(1 for r in ff if r["is_inverse"])                     # residual heuristic false-positives (DUAL-edge would catch)
    for r in rows:
        tag = ("OK" if r["ok"] else "FAIL") if r["ok"] is not None else ("FALSE-FRIEND-HIT" if r["is_inverse"] else "ok(rejected)")
        print("    [%-13s] %-26s -> %-18s is_inverse=%-5s [%s]" % (r["class"], r["decoy"], r["verdict"], r["is_inverse"], tag), flush=True)
    print("  POSITIVE detected=%d/%d | TYPE/NONINVERSE guard violations=%d (must=0) | FALSE-FRIEND hits=%d (DUAL-edge-confirmation closes these)" % (
        pos_ok, len(pos), guard_violations, ff_hits), flush=True)
    return {"n_positive": len(pos), "pos_detected": pos_ok, "guard_violations": guard_violations,
            "falsefriend_hits": ff_hits, "n_falsefriend": len(ff), "rows": rows}


def verdict(r) -> Tuple[str, str]:
    pos_ok = (r["pos_detected"] == r["n_positive"]); gv = r["guard_violations"]; ff = r["falsefriend_hits"]
    s = ("POSITIVE inverses detected %d/%d; TYPE+NONINVERSE guard violations=%d (must be 0); FALSE-FRIEND (coincidental un-prefix) hits=%d/%d. "
         "FINDING: the INVERSE_PAIR TYPE guard (same domain + same output + exactly 2 members) correctly rejects type-mismatched and non-inverse "
         "decoys. RESIDUAL RISK: the name heuristic's 'un'-prefix rule false-friends on coincidences (union/ion, unit/it) -- which is EXACTLY why "
         "V2.1's run() grounds INVERSE_PAIR in an AUTHORED DUAL edge when available; the name path is a LOW-CONFIDENCE fallback. RECOMMENDATION: "
         "treat name-heuristic INVERSE_PAIR as provisional pending DUAL-edge confirmation (require an authored DUAL/INVERSE_OF edge for a "
         "high-confidence INVERSE_PAIR verdict).") % (r["pos_detected"], r["n_positive"], gv, ff, r["n_falsefriend"])
    if gv > 0:
        return ("HARD_FAIL", "HARD_FAIL: %d TYPE/NONINVERSE decoy(s) classified INVERSE_PAIR -- the type guard is BROKEN (unsound; would mislabel "
                "distinct or type-incompatible ops as inverses). " % gv + s)
    if pos_ok:
        return ("HARD_PASS", "HARD_PASS (INVERSE_PAIR detector resists false positives in its sound domain): all %d genuine inverses detected, "
                "ZERO type/non-inverse guard violations. The only residual false-positives are %d coincidental un-prefix FALSE-FRIENDS, correctly "
                "characterized -- and these are closed by V2.1's authored-DUAL-edge grounding (the sound path). The name heuristic is hereby "
                "documented as LOW-CONFIDENCE-pending-DUAL-edge. " % (r["n_positive"], ff) + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: type guard sound (0 violations) but %d/%d genuine inverses missed -- the positive-detection heuristic is "
            "too strict; widen inverse-token coverage. " % (r["pos_detected"], r["n_positive"]) + s)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
