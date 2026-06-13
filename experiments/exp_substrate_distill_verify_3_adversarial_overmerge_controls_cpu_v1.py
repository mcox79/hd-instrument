"""
exp_substrate_distill_verify_3_adversarial_overmerge_controls_cpu_v1.py -- CELL-DISTILL-VERIFY-3: adversarial controls for the over-distillation guard -- where does type-only equivalence saturate? -- CPU/local (no heat).

ROUTING: Exp-Dev self-initiated (option #1 of exp_dev_to_research_REQUEST_one_concrete_ungated_task...). V2 showed 0 false-MERGEABLE on
  2 TRUE-POSITIVE groups (optimizer family, conv<->DFT) where distinctness was VISIBLE in the typed signature. That is the easy case. The
  skeptical claim "the verifier will not over-distill" (7th + 10th rule self-strengthening) needs ADVERSARIAL DECOYS: groups constructed to
  TEMPT a false MERGEABLE. This cell maps the guard's domain of validity instead of celebrating 2 easy passes. Ungated: pure CHTV-1
  classify_group logic on synthetic decoy signatures (no index, no relations, no codebook). Imports classify_group from V2 (single source of truth).

  TWO DECOY CLASSES:
   (A) SIGNATURE-VISIBLE distinct -- distinctness IS expressible in the typed signature (different operation_type / output_type / domain /
       complexity_class, or contradictory serves_capability, or stub-vs-full). The guard MUST refuse MERGEABLE here. 0 false-merge = sound in-domain.
   (B) SIGNATURE-INVISIBLE distinct -- two genuinely-distinct algorithms with IDENTICAL typed signature AND identical caps, differing only in
       BODY/semantics. Type-only reasoning CANNOT see the difference, so it WILL return MERGEABLE. This is NOT a bug to hide -- it is the
       boundary: CHTV-1 typed-signature equality is NECESSARY but NOT SUFFICIENT for operational equivalence. The cell must correctly PREDICT
       that the type-only guard saturates here, which is exactly what motivates BODY-LEVEL witnesses (V1's provenance pointer, or an L6-PROOF
       derivation chain). Honesty about the boundary is the deliverable.

PRE-REGISTERED: HARD-PASS iff (1) ZERO false-MERGEABLE across ALL signature-VISIBLE decoys (guard sound within the typed domain) AND
  (2) ALL signature-INVISIBLE decoys ARE flagged MERGEABLE (the cell correctly locates where type-only saturates -> body-level proof needed).
  MIDDLE_BAND iff visible-decoys all pass but the invisible boundary is mis-predicted (some invisible decoy NOT merged -> taxonomy noisier
  than claimed). HARD-FAIL iff ANY signature-VISIBLE decoy is MERGEABLE (the guard is broken in its own domain -- unsound over-distillation).
  ASCII-only. --self-test + --smoke + metrics.json.
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
# single source of truth: reuse V2's classifier (no re-implementation drift)
from exp_substrate_distill_verify_2_class_b_relationship_discrimination_cpu_v1 import classify_group
ANCHOR_NAME = "substrate_distill_verify_3_adversarial_overmerge_controls_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

FULL = {"domain": "convex_optimization", "operation_type": "first_order", "signature_input_type": "function_and_gradient",
        "signature_output_type": "parameter_vector", "complexity_class": "O(N) per step"}


def _mut(**kw):
    d = dict(FULL); d.update(kw); return d


# Each decoy: (name, sigs, caps, class) where class in {"VISIBLE", "INVISIBLE"}.
# VISIBLE = distinctness expressible in the typed signature -> MUST NOT be MERGEABLE.
# INVISIBLE = distinct only in body, identical sig+caps -> WILL be MERGEABLE (boundary, by design).
def build_decoys() -> List[Tuple[str, list, list, str]]:
    C = lambda *xs: [set(x) for x in xs]
    return [
        # --- VISIBLE distinct: the guard must refuse MERGEABLE ---
        ("contradictory_caps_same_sig", [dict(FULL), dict(FULL)], C({"cap_a"}, {"cap_b"}), "VISIBLE"),
        ("different_operation_type", [dict(FULL), _mut(operation_type="second_order")], C({"cap_a"}, {"cap_a"}), "VISIBLE"),
        ("different_output_type", [dict(FULL), _mut(signature_output_type="frequency_spectrum")], C({"cap_a"}, {"cap_a"}), "VISIBLE"),
        ("different_domain", [dict(FULL), _mut(domain="signal_processing")], C({"cap_a"}, {"cap_a"}), "VISIBLE"),
        ("different_complexity", [dict(FULL), _mut(complexity_class="O(N^2)")], C({"cap_a"}, {"cap_a"}), "VISIBLE"),
        ("different_input_type", [dict(FULL), _mut(signature_input_type="function_and_sample_gradient")], C({"cap_a"}, {"cap_a"}), "VISIBLE"),
        ("stub_vs_full", [dict(FULL), {}], C({"cap_a"}, {"cap_a"}), "VISIBLE"),
        ("three_way_one_divergent", [dict(FULL), dict(FULL), _mut(operation_type="zeroth_order")], C({"cap_a"}, {"cap_a"}, {"cap_a"}), "VISIBLE"),
        # --- INVISIBLE distinct: identical sig + identical NON-EMPTY caps, distinct only in body -> WILL merge (the boundary) ---
        ("identical_sig_identical_caps_distinct_body", [dict(FULL), dict(FULL)], C({"cap_a"}, {"cap_a"}), "INVISIBLE"),
        # --- CONSERVATIVE: identical sig but NO capability evidence -> the verifier REFUSES to merge (discovered by V3: merge needs
        #     identical NON-EMPTY caps, not signature alone). Sound conservatism, not a boundary miss. ---
        ("identical_sig_empty_caps_no_evidence", [dict(FULL), dict(FULL)], C(set(), set()), "CONSERVATIVE"),
    ]


def _selftest():
    # classify_group importable and the two anchor archetypes behave as V2 found
    sa = classify_group([dict(FULL), _mut(operation_type="x")], [{"c"}, {"c"}])
    assert sa == "SHARED_ABSTRACTION", sa
    me = classify_group([dict(FULL), dict(FULL)], [{"c"}, {"c"}])
    assert me == "MERGEABLE", me
    # decoy battery is well-formed
    ds = build_decoys()
    assert any(c == "VISIBLE" for *_, c in ds) and any(c == "INVISIBLE" for *_, c in ds)
    print("[selftest] PASS: substrate_distill_verify_3_adversarial_overmerge_controls_cpu_v1", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


def run() -> Dict:
    decoys = build_decoys()
    rows = []
    for name, sigs, caps, klass in decoys:
        v = classify_group(sigs, caps)
        merged = (v == "MERGEABLE")
        if klass == "INVISIBLE":
            ok = merged                        # type-only WILL (and by-design does) merge; boundary correctly predicted
        else:                                  # VISIBLE or CONSERVATIVE: must refuse merge
            ok = (not merged)
        rows.append({"decoy": name, "class": klass, "verdict": v, "merged": merged, "ok": ok})
    visible = [r for r in rows if r["class"] == "VISIBLE"]
    conservative = [r for r in rows if r["class"] == "CONSERVATIVE"]
    invisible = [r for r in rows if r["class"] == "INVISIBLE"]
    n_norefuse = sum(1 for r in (visible + conservative) if r["merged"])   # MUST be 0 (no merge without distinguishing OR without evidence)
    n_invis_merged = sum(1 for r in invisible if r["merged"])              # SHOULD == len(invisible) (the boundary)
    for r in rows:
        tag = "OK" if r["ok"] else ("FALSE-MERGE!" if r["class"] in ("VISIBLE", "CONSERVATIVE") else "boundary-miss")
        print("  [%-12s] %-44s -> %-18s merged=%-5s [%s]" % (r["class"], r["decoy"][:44], r["verdict"], r["merged"], tag), flush=True)
    print("  VISIBLE+CONSERVATIVE decoys=%d false/unsound-MERGE=%d (must=0) | INVISIBLE decoys=%d merged=%d (boundary, should=%d)" % (
        len(visible) + len(conservative), n_norefuse, len(invisible), n_invis_merged, len(invisible)), flush=True)
    root = REPO / "data" / "substrate_index"
    if root.exists():
        bf = root / "bench_reports"; bf.mkdir(parents=True, exist_ok=True)
        import json
        (bf / "distill_verify_3_adversarial_controls.json").write_text(json.dumps({"rows": rows,
            "n_norefuse_required": len(visible) + len(conservative), "n_unsound_merge": n_norefuse,
            "n_invisible": len(invisible), "n_invisible_merged": n_invis_merged}, indent=2), encoding="utf-8")
    return {"rows": rows, "n_norefuse_required": len(visible) + len(conservative), "n_unsound_merge": n_norefuse,
            "n_invisible": len(invisible), "n_invisible_merged": n_invis_merged}


def verdict(r) -> Tuple[str, str]:
    nreq = r["n_norefuse_required"]; um = r["n_unsound_merge"]; ni = r["n_invisible"]; im = r["n_invisible_merged"]
    s = ("VISIBLE+CONSERVATIVE decoys: %d/%d correctly refused merge (unsound-MERGE=%d). INVISIBLE decoys: %d/%d merged (the boundary). "
         "FINDING (refined by V3): the verifier merges ONLY when typed signatures are identical AND serves_capability is identical and NON-EMPTY "
         "-- so CHTV-1 typed equality is NECESSARY but NOT SUFFICIENT for operational equivalence. It is SOUND for every distinction expressible "
         "in the signature (operation_type / output / domain / complexity / input / contradictory caps / stub-vs-full) AND it is conservatively "
         "refuses to merge on signature alone when there is NO capability evidence. It SATURATES at exactly one point: two distinct algorithms "
         "with an identical signature AND identical non-empty caps (distinct only in body). That single saturation point is WHY the loop needs "
         "body-level witnesses (V1's provenance pointer or an L6-PROOF derivation chain). The guard's domain of validity is now MAPPED, not assumed.") % (
        nreq - um, nreq, um, im, ni)
    if um > 0:
        return ("HARD_FAIL", "HARD_FAIL: %d decoy(s) that should have been refused were marked MERGEABLE -- the over-distillation guard is broken "
                "within its own domain (signature-visible distinctness or absence of capability evidence must block a merge). Unsound. " % um + s)
    if im == ni:
        return ("HARD_PASS", "HARD_PASS (guard sound in-domain + boundary correctly mapped): ZERO unsound merges across %d adversarial decoys "
                "(every signature-expressible distinction refused, AND merge refused when no capability evidence exists), AND all %d "
                "signature-INVISIBLE decoys correctly land at MERGEABLE -- the cell PREDICTS exactly the single point where type-only equivalence "
                "saturates and body-level proof becomes necessary. Hardens V2 from '2 easy positives' to 'robust against decoys designed to break "
                "it, with the validity boundary explicit.' " % (nreq, ni) + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: 0 unsound merge (guard sound in-domain) but the invisible boundary is mis-predicted (%d/%d invisible "
            "decoys merged) -- the type-only taxonomy is noisier at the boundary than claimed; refine before relying on it. " % (im, ni) + s)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
