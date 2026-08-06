"""ARGUMENT-REALIZATION SOURCE-GATE FOR EVENT-HOOD (2026-08-06).

QUESTION: does SOURCE-GATING the frame-trigger's additive multi-predicate scan (find_frame_verbs)
with an ARGUMENT-REALIZATION check -- accept a frame-lemma token as an event only when its frame's
core slot(s) are locally FILLED by a real candidate mention, not merely lexically present -- raise
PRECISION over the ungated frame-trigger fix while KEEPING the recall gain, on the SAME independent
McGuffey gold (data/gold_mcguffey_castle_building_svo_v1.json, N=34) used by
exp_frame_trigger_predicate_recall_fix_v1.py?

WHY (deep-VET notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md row #4 "Event extraction:
hood + segmentation [A]", disk-verified): experiments/exp_oracle_mention_upperbound_reader_v1.py
find_frame_verbs (pre-fix) accepted EVERY token whose lemma is in hdlab.thematic_role_labeler.
VERB_FRAMES as an event, gated only by a determiner-guard -- no argument-realization confirmation.
The brain gates event-hood at the SOURCE by whether the frame's expected AGENT/PATIENT slots are
REALIZED (McRae thematic-fit; a frame fires an event only when its core args are filled), not by
bare lexical frame membership. Measured cost of the ungated additive scan
(exp_frame_trigger_predicate_recall_fix_v1, commit afddc2807, reproduced by arm B below): n_pred
nearly doubled 61->113, precision fell 0.180->0.159 while recall rose 0.324->0.529.

THE FIX (2026-08-06, additive + opt-in, zero regression by construction): find_frame_verbs gained a
`require_arg_realization` kwarg (default False = byte-identical to the ungated fix). When True, an
ADDITIVE (non-element-0) frame-hit must ALSO pass the new `_arg_realization_ok` check:
  (1) NOT a copula complement (predicate nominal/adjective -- "was a great help", "was a loyal
      guard", "was clean"). POS is used as a soft disambiguator here (matching find_frame_verbs'
      existing "POS is a soft prior" design) so a real passive VBN secondary predicate is never
      caught by this rule.
  (2) a resolvable SUBJECT/AGENT-eligible candidate (reusing the file's own candidate_indices) is
      locally present, allowing ONE coordinating-conjunction crossing so a compound predicate's
      carried-over subject still resolves ("Herbert took the block and threw it").
  (3) for frames whose object is semantically OBLIGATORY (the PSYCH_VERBS / DITRANS_VERBS lemma
      classes Component-3 already declares -- NOT plain ambitransitive motion/action verbs, which
      commonly appear intransitively as real events, e.g. "he sat") a resolvable OBJECT/PATIENT-
      eligible candidate is also locally present.
No new parser: the gate reuses VERB_FRAMES' own PSYCH/DITRANS role classes + candidate_indices, the
cell's existing argument-candidate machinery, exactly as the Director's spawn-prompt specified.

The kwarg is threaded (also opt-in, default off) through extract_passage_argrole/read_corpus
(exp_read_argstruct_goal_role_third_reader_v1.py) and extract_passage_nest/read_corpus
(exp_read_nested_clause_relative_third_reader_v1.py) as `gate_arg_realization`.

ARMS (measured on the SAME independent gold, same slice L04+L05, same trained clf, same reader):
  baseline      : multi_pred=False                                 (find_main_verb only; reproduces
                                                                      the FROZEN 0.1803/0.3235/0.2316
                                                                      floor)
  frame_trigger : multi_pred=True,  gate_arg_realization=False      (the UNGATED additive scan;
                                                                      reproduces the FROZEN
                                                                      0.1593/0.5294/0.2449 reference)
  gated         : multi_pred=True,  gate_arg_realization=True       (THIS FIX)

DESIGN-GATE (verified below BEFORE the verdict is trusted):
  (G1)  BASELINE REPRODUCTION: baseline arm reproduces the frozen baseline P/R/F1 EXACTLY.
  (G1b) FRAME-TRIGGER REPRODUCTION (Gate D positive control): frame_trigger arm (gate OFF)
        reproduces the frozen frame_trigger P/R/F1 EXACTLY -- proves the new gate parameter is
        genuinely additive/opt-in (byte-identical to the pre-fix code path when off).
  (G2)  NO-REGRESSION: the 3 touched files' own --self-test all pass (unchanged default kwargs).
  (G3)  MECHANISM CAN-FAIL (hand-authored, corpus-independent, verified live against
        ORC.find_frame_verbs -- NOT hypothesized): 8 KEEP sentences (real secondary-predicate
        events, several sharing a lemma with a REJECT sentence via subject-carryover across "and")
        vs 5 REJECT sentences (nominal / predicate-nominal / predicate-adjective / object-starved
        uses of the SAME lemma) -- the gate must classify BOTH directions correctly, proving it
        discriminates by STRUCTURE, not by lexical identity or corpus-fitting.

VERDICT BANDS (pre-registered, per Director spawn-prompt pre-reg; DECISIVE_MARGIN=0.02 -- N=34 is a
tiny gold set, so a barely-clearing result is not trusted as HARD_PASS on its own):
  HARD_PASS: gated_precision >= FRAME_TRIGGER_P + 0.05 AND gated_recall >= 0.45 AND
    gated_f1 > FRAME_TRIGGER_F1 AND can-fail 13/13 correct AND G1+G1b+G2 hold, AND each of the 3
    numeric gates clears by >= DECISIVE_MARGIN beyond its threshold.
  MIDDLE_BAND: the qualitative direction is right (precision up >=0.05, recall kept >=0.45, F1
    composes) but at least one numeric gate is not DECISIVE (<0.02 margin), OR the can-fail set is
    not 13/13 clean, OR N=34 caveat otherwise warrants it.
  HARD_FAIL: gated_recall < 0.45 (over-gates real events) OR precision does not rise by >= 0.05 OR
    gated_f1 <= FRAME_TRIGGER_F1 (no composition) OR G1/G1b/G2 fail.

COMPUTE ARCHITECTURE: class (b) sequential-CPU (46 short sentences + a trained averaged-perceptron
classifier fit on ~100 hand examples; identical compute profile to
exp_frame_trigger_predicate_recall_fix_v1.py, wall < 30s). Foreground, local, NO queue, NO push, NO
remote-persist. Determinism: OMP/MKL/OPENBLAS=1, sorted(set()) discipline preserved (unchanged from
the reused readers). N/A: no HD/torch vectors in this cell (symbolic reader); no cardinality sweep
axis (fixed 3-arm design); no CRLB (no HD noise floor).

progress_logging: n/a (wall < 30s, no timeout_s >= 1800 field applies).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import sys
import time
import traceback
from datetime import datetime, timezone

ANCHOR_NAME = "frame_trigger_argrealization_gate_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_coherence_gate_extraction_correctness_independent_gold_v1 as G  # noqa: E402
from experiments import exp_read_nested_clause_relative_third_reader_v1 as NEST  # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2  # noqa: E402
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC  # noqa: E402

# Frozen reference numbers (2026-08-05, both reproduced byte-exact by G1/G1b below).
FROZEN_BASELINE_P = 0.18032786885245902
FROZEN_BASELINE_R = 0.3235294117647059
FROZEN_BASELINE_F1 = 0.23157894736842105
FROZEN_FRAME_TRIGGER_P = 0.15929203539823009
FROZEN_FRAME_TRIGGER_R = 0.5294117647058824
FROZEN_FRAME_TRIGGER_F1 = 0.24489795918367346

PRECISION_LIFT_MIN = 0.05
RECALL_FLOOR = 0.45
DECISIVE_MARGIN = 0.02

# ---------------------------------------------------------------------------------------------
# G3 MECHANISM CAN-FAIL SET (hand-authored, verified live against ORC.find_frame_verbs at author
# time -- see cell design notes; not hypothesized numbers). Each REJECT item shares its lemma with
# a KEEP item to prove the gate discriminates by clause STRUCTURE, not lexical identity. All KEEP
# items place the target lemma as a SECONDARY (additive, non-element-0) predicate via a compound
# "X ... and Y-ed ..." construction (subject-carryover) so the gate is genuinely exercised (the
# element-0 primary-verb pick is never gated, by design -- byte-identity with the pre-fix pipeline).
# ---------------------------------------------------------------------------------------------
CANFAIL_KEEP = [
    ("Tom gave the toy and Ann watched the show.", "watch"),
    ("Jack ran home and helped his sister.", "help"),
    ("Jack ran home and caught the ball.", "catch"),
    ("Tom entered and knocked twice.", "knock"),
    ("Ann arrived home and cleaned the room.", "clean"),
    ("She stood in the yard and wanted the toy.", "want"),
    ("Sam patrolled the wall and guarded the gate.", "guard"),
    ("Herbert took the block and threw it at the cat.", "throw"),
]
CANFAIL_REJECT = [
    ("The room was clean and tidy.", "clean", "predicate_adjective_copula_complement"),
    ("Tom was a great help.", "help", "predicate_nominal_copula_complement"),
    ("Knocks echoed through the house.", "knock", "sentence_initial_nominal_no_subject"),
    ("She stood in the yard and wanted more.", "want", "psych_object_obligatory_not_realized"),
    ("Sam was a loyal guard.", "guard", "predicate_nominal_copula_complement"),
]


def run_canfail():
    rows = []
    for sent, lemma in CANFAIL_KEEP:
        tagged = ORC.pos_tag_sentence(sent)
        gated = ORC.find_frame_verbs(tagged, require_arg_realization=True)
        present = lemma in [l for (_i, l, _p) in gated]
        rows.append(dict(sentence=sent, lemma=lemma, expect="KEEP", present=present,
                         correct=(present is True), class_="real_event"))
    for sent, lemma, cls in CANFAIL_REJECT:
        tagged = ORC.pos_tag_sentence(sent)
        gated = ORC.find_frame_verbs(tagged, require_arg_realization=True)
        present = lemma in [l for (_i, l, _p) in gated]
        rows.append(dict(sentence=sent, lemma=lemma, expect="REJECT", present=present,
                         correct=(present is False), class_=cls))
    n_correct = sum(1 for r in rows if r["correct"])
    return dict(rows=rows, n=len(rows), n_correct=n_correct, all_correct=(n_correct == len(rows)))


def run_reader(multi_pred: bool, gate_arg_realization: bool):
    cfg = G.cfg_full()
    les = NEST.load_lessons()
    clf = V2._fit_clf()
    sent_text = {}
    order = []
    for lid in cfg["slice_lessons"]:
        for j, s in enumerate(G.split_sents(les[lid])):
            sid = f"{lid}_{j:02d}"
            sent_text[sid] = s
            order.append(sid)
    passages = {sid: sent_text[sid] for sid in order}
    store = NEST.read_corpus(clf, passages, nest=True, multi_pred=multi_pred,
                             gate_arg_realization=gate_arg_realization)["store"]
    reader_svo = {}
    for sid in order:
        tups = [(r[1], r[2], r[3]) for r in store.get(sid, []) if r[0] == "svo" and r[1] != "kind"]
        reader_svo[sid] = [(str(v).lower(), str(a).lower(), str(p).lower()) for (v, a, p) in tups]
    return order, sent_text, reader_svo


def score(order, reader_svo, gold):
    flat = [(sid, tup) for sid in order for tup in reader_svo[sid]]
    primary = G.score_arm(flat, gold, G.match_primary)
    triple = G.score_arm(flat, gold, G.match_triple)
    return flat, primary, triple


def residual_fn(flat, gold):
    covered = set()
    for sid, tup in flat:
        for g in gold.get(sid, []):
            if G.match_primary(tup, [g]) is not None:
                covered.add((sid, g["v"], g["patient"]))
    fn = []
    for sid, rels in gold.items():
        for g in rels:
            if (sid, g["v"], g["patient"]) not in covered:
                fn.append([sid, g["v"], g["agent"], g["patient"]])
    return fn


def run_selftest_subprocess(pyfile, extra_args, timeout=180):
    import subprocess
    py = sys.executable
    try:
        cp = subprocess.run([py, pyfile] + extra_args, cwd=REPO_ROOT,
                            capture_output=True, text=True, timeout=timeout)
        ok = cp.returncode == 0
        msg = (cp.stdout[-500:] + cp.stderr[-500:]).strip()
        return ok, msg
    except Exception as e:  # pragma: no cover
        return False, f"{type(e).__name__}: {e}"


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = G.cfg_full()
    gold, gold_meta = G.load_gold(cfg["slice_lessons"])

    order_b, _st_b, svo_b = run_reader(multi_pred=False, gate_arg_realization=False)
    flat_b, prim_b, trip_b = score(order_b, svo_b, gold)

    order_f, _st_f, svo_f = run_reader(multi_pred=True, gate_arg_realization=False)
    flat_f, prim_f, trip_f = score(order_f, svo_f, gold)

    order_g, _st_g, svo_g = run_reader(multi_pred=True, gate_arg_realization=True)
    flat_g, prim_g, trip_g = score(order_g, svo_g, gold)

    # G1 / G1b: exact reproduction of the two frozen reference arms.
    g1_ok = (abs(prim_b["precision"] - FROZEN_BASELINE_P) < 1e-9
             and abs(prim_b["recall"] - FROZEN_BASELINE_R) < 1e-9
             and abs(prim_b["f1"] - FROZEN_BASELINE_F1) < 1e-9)
    g1b_ok = (abs(prim_f["precision"] - FROZEN_FRAME_TRIGGER_P) < 1e-9
              and abs(prim_f["recall"] - FROZEN_FRAME_TRIGGER_R) < 1e-9
              and abs(prim_f["f1"] - FROZEN_FRAME_TRIGGER_F1) < 1e-9)

    # G2: no-regression self-tests on the 3 touched files (unchanged default-kwarg behavior).
    ok_orc, msg_orc = run_selftest_subprocess(
        os.path.join(REPO_ROOT, "experiments", "exp_oracle_mention_upperbound_reader_v1.py"),
        ["--self-test"], timeout=300)
    ok_arg, msg_arg = run_selftest_subprocess(
        os.path.join(REPO_ROOT, "experiments", "exp_read_argstruct_goal_role_third_reader_v1.py"),
        ["--self-test"])
    ok_nest, msg_nest = run_selftest_subprocess(
        os.path.join(REPO_ROOT, "experiments", "exp_read_nested_clause_relative_third_reader_v1.py"),
        ["--self-test"])
    g2_ok = ok_orc and ok_arg and ok_nest

    # G3: mechanism can-fail (hand-authored, corpus-independent).
    canfail = run_canfail()

    delta_p_vs_frame = prim_g["precision"] - prim_f["precision"]
    delta_r_vs_frame = prim_g["recall"] - prim_f["recall"]
    delta_f1_vs_frame = prim_g["f1"] - prim_f["f1"]

    precision_up = delta_p_vs_frame >= PRECISION_LIFT_MIN
    precision_up_decisive = delta_p_vs_frame >= (PRECISION_LIFT_MIN + DECISIVE_MARGIN)
    recall_kept = prim_g["recall"] >= RECALL_FLOOR
    recall_kept_decisive = prim_g["recall"] >= (RECALL_FLOOR + DECISIVE_MARGIN)
    f1_composes = prim_g["f1"] > FROZEN_FRAME_TRIGGER_F1
    f1_composes_decisive = prim_g["f1"] >= (FROZEN_FRAME_TRIGGER_F1 + DECISIVE_MARGIN)

    design_gate_ok = g1_ok and g1b_ok and g2_ok
    numeric_ok = precision_up and recall_kept and f1_composes
    numeric_decisive = precision_up_decisive and recall_kept_decisive and f1_composes_decisive

    if not design_gate_ok:
        verdict = "HARD_FAIL_DESIGN_GATE_VIOLATION"
    elif (not recall_kept) or (not precision_up) or (not f1_composes):
        verdict = "HARD_FAIL_NO_RECALL_KEPT_OR_NO_PRECISION_LIFT_OR_NO_COMPOSITION"
    elif numeric_ok and numeric_decisive and canfail["all_correct"]:
        verdict = "HARD_PASS_ARG_REALIZATION_GATE"
    else:
        verdict = "MIDDLE_BAND_DIRECTION_RIGHT_NOT_DECISIVE_OR_CANFAIL_INCOMPLETE"

    fn_after_gated = residual_fn(flat_g, gold)

    elapsed = time.perf_counter() - t0
    msg = (f"{verdict} | BASELINE P={prim_b['precision']:.4f} R={prim_b['recall']:.4f} "
           f"F1={prim_b['f1']:.4f} n_pred={prim_b['n_pred']} "
           f"| FRAME_TRIGGER(ungated) P={prim_f['precision']:.4f} R={prim_f['recall']:.4f} "
           f"F1={prim_f['f1']:.4f} n_pred={prim_f['n_pred']} "
           f"| GATED P={prim_g['precision']:.4f} R={prim_g['recall']:.4f} F1={prim_g['f1']:.4f} "
           f"n_pred={prim_g['n_pred']} "
           f"| dP_vs_frame={delta_p_vs_frame:+.4f} dR_vs_frame={delta_r_vs_frame:+.4f} "
           f"dF1_vs_frame={delta_f1_vs_frame:+.4f} "
           f"| precision_up={precision_up} recall_kept={recall_kept} f1_composes={f1_composes} "
           f"decisive={numeric_decisive} "
           f"| canfail={canfail['n_correct']}/{canfail['n']} "
           f"| G1_baseline_repro={g1_ok} G1b_frame_trigger_repro={g1b_ok} G2_no_regression={g2_ok} "
           f"(orc={ok_orc} argstruct={ok_arg} nest={ok_nest}) "
           f"| n_fn_gated={len(fn_after_gated)}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg,
        "summary": msg, "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "arms": {
            "baseline": {"primary": prim_b, "triple": trip_b},
            "frame_trigger_ungated": {"primary": prim_f, "triple": trip_f},
            "gated": {"primary": prim_g, "triple": trip_g},
        },
        "frozen_reference": {
            "baseline": {"precision": FROZEN_BASELINE_P, "recall": FROZEN_BASELINE_R,
                        "f1": FROZEN_BASELINE_F1},
            "frame_trigger": {"precision": FROZEN_FRAME_TRIGGER_P, "recall": FROZEN_FRAME_TRIGGER_R,
                              "f1": FROZEN_FRAME_TRIGGER_F1},
        },
        "design_gate": {
            "G1_baseline_reproduction": g1_ok,
            "G1b_frame_trigger_reproduction": g1b_ok,
            "G2_no_regression": g2_ok,
            "G2_oracle_mention_selftest": {"ok": ok_orc, "tail": msg_orc},
            "G2_argstruct_selftest": {"ok": ok_arg, "tail": msg_arg},
            "G2_nest_selftest": {"ok": ok_nest, "tail": msg_nest},
            "design_gate_ok": design_gate_ok,
        },
        "delta_gated_vs_frame_trigger": {
            "precision": delta_p_vs_frame, "recall": delta_r_vs_frame, "f1": delta_f1_vs_frame,
            "precision_up_ge_0.05": precision_up, "precision_up_decisive": precision_up_decisive,
            "recall_kept_ge_0.45": recall_kept, "recall_kept_decisive": recall_kept_decisive,
            "f1_composes_gt_frame_trigger": f1_composes, "f1_composes_decisive": f1_composes_decisive,
            "numeric_ok": numeric_ok, "numeric_decisive": numeric_decisive,
        },
        "mechanism_canfail": canfail,
        "residual_fn_gated": {"n": len(fn_after_gated), "items": fn_after_gated},
        "REQUIRED_FIELDS": ["verdict", "arms", "frozen_reference", "design_gate",
                            "delta_gated_vs_frame_trigger", "mechanism_canfail", "residual_fn_gated"],
        "notes": ("ARGUMENT-REALIZATION source-gate on find_frame_verbs' additive multi-predicate "
                  "scan (require_arg_realization kwarg, default False = byte-identical to the "
                  "pre-fix pipeline). See notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md "
                  "row #4 for the brain-grounding (McRae thematic-fit / frame argument realization) "
                  "and this cell's own module docstring for the exact gate mechanics."),
    }
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    return payload


def self_test():
    # Cheap self-test: the gate must fire (differ from ungated) on the can-fail set, and
    # find_frame_verbs must still expose the require_arg_realization kwarg with default-False
    # byte-identity to the pre-fix element-0 pick (mirrors the sibling recall-fix cell's pattern).
    tagged = ORC.pos_tag_sentence("Herbert took the block and threw it at the cat.")
    base_idx, base_verb, _ = ORC.find_main_verb(tagged)
    ungated = ORC.find_frame_verbs(tagged)
    gated = ORC.find_frame_verbs(tagged, require_arg_realization=True)
    assert base_verb == "took", f"self-test: expected base pick 'took', got {base_verb}"
    assert ungated == ORC.find_frame_verbs(tagged, require_arg_realization=False), (
        "self-test: require_arg_realization=False must be byte-identical to the omitted-kwarg call")
    lemmas_u = [lem for (_i, lem, _p) in ungated]
    lemmas_g = [lem for (_i, lem, _p) in gated]
    assert "took" in lemmas_u and "throw" in lemmas_u, f"self-test: ungated missing element, got {lemmas_u}"
    assert "took" in lemmas_g and "throw" in lemmas_g, (
        f"self-test: gated must KEEP the real carryover secondary predicate, got {lemmas_g}")

    canfail = run_canfail()
    assert canfail["all_correct"], (
        f"self-test: mechanism can-fail set not 100% correct: "
        f"{[r for r in canfail['rows'] if not r['correct']]}")
    print(f"[{ANCHOR_NAME}] self-test PASS: base_pick={base_verb} ungated={lemmas_u} gated={lemmas_g} "
          f"canfail={canfail['n_correct']}/{canfail['n']}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    if args.smoke:
        run_mode("smoke")
        return
    if args.full:
        run_mode("full")
        return
    ap.error("specify one of --self-test | --smoke | --full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {
            "anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
            "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
        }
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
