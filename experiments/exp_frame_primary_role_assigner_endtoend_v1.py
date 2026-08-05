#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_frame_primary_role_assigner_endtoend_v1

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (n/a here: single real-pipeline arm vs the already-landed
  gold-parsed 3c number, cited not re-derived)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n_a: accuracy over a discrete 2-class axis, no capacity/CRLB floor
- baseline_in_band n/a: this is a HONEST-NUMBER measurement cell, not a HARD_PASS/FAIL gate
- discriminator survives scale: this IS the full-N run (all N=65 subj-axis real sentences)
- cardinality_ok: single deterministic unit, no sweep axis
- per-unit failure-class instrumentation: locate/parse failures logged as UNRESOLVED, never dropped
- calibration_check: default_ok_for_this_regime
- progress_logging: print_flush_true

WHY: notes/skunkworks_reVET_frame_primary_role_assigner_v1.md re-VET'd exp_frame_primary_role_
assigner_v1 (commit 7d41ca28d) DOWN to MIDDLE_BAND and flagged that its headline 0.8769 subj-
experiencer accuracy is measured against GOLD-PARSED args (record["args"][*]["head"] located via
FI.locate_head_idx on the raw text.split() tokens) -- i.e. it assumes a perfect parse. That is NOT
the real Component-3 capability number: the real pipeline is parse -> candidate_generator ->
frame_primary_role, and the persisted UD-EWT front-end (PosTagger UPOS + ArcParser UAS~0.79) does
NOT resolve every sentence's (verb, subject-argument) pair correctly. This cell measures the HONEST
end-to-end number: for each subj-axis sentence, tag+parse with the REAL persisted front-end,
generate REAL (verb_idx, arg_idx) candidates via hdlab.candidate_generator.CandidateGenerator, and
only score a prediction when the parser's own candidate set actually LICENSES the gold (verb, subj)
pair (mirrors the intended parse -> candidate_generator -> frame_primary_role -> role-label chain).
Sentences the real parser fails to license are UNRESOLVED (counted as wrong in the end-to-end
accuracy, per the spawn contract "unresolved = wrong").

BASELINE: acc_gold_parsed=0.8769 CITED@data/exp_frame_primary_role_assigner_v1/metrics.json (the
"assumes-perfect-parse" number this cell corrects, NOT re-derived here).

COMPUTE ARCHITECTURE: class (b) sequential-CPU. PosTagger.tag + ArcParser.parse are per-sentence
closed-form (hashed perceptron forward pass), no matmul batching opportunity at N=118 sentences;
wall time ~seconds total (persisted front-end load dominates). LOCAL-ONLY, no queue, no push.
SUPPLIED vs EARNED: identical disclosure to exp_frame_primary_role_assigner_v1 (frame table +
construction-cue detectors SUPPLIED; OOV construction->frame mapping EARNED via induction, verb
lemma never a feature) -- this cell additionally measures how much of that EARNED signal survives
being routed through a REAL (imperfect) parse instead of a gold parse.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import sys
import time
import traceback
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ANCHOR_NAME = "frame_primary_role_assigner_endtoend_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab import frame_induction as FI  # noqa: E402
from hdlab.thematic_role_labeler import VERB_FRAMES  # noqa: E402
from hdlab.candidate_generator import CandidateGenerator, ud_tokenize  # noqa: E402

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
DATA_PATH = os.path.join(REPO_ROOT, "experiments", "data", "experiencer_narrative_roles_v1.jsonl")
POS_PATH = os.path.join(REPO_ROOT, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")
ARC_PATH = os.path.join(REPO_ROOT, "data", "frontend_assets", "arc_parser_hashed_ud_ewt.npz")
GOLD_PARSED_METRICS_PATH = os.path.join(
    REPO_ROOT, "data", "exp_frame_primary_role_assigner_v1", "metrics.json")

EPS = 1e-9


def _load_records():
    recs = []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    return recs


def _find_experiencer_arg(record):
    for a in record["args"]:
        if a["role"] == "EXPERIENCER":
            return a
    return None


def build_train_corpus(exclude_lemmas):
    """IDENTICAL leak-safe training protocol to exp_frame_primary_role_assigner_v1.py:
    build_train_corpus (gold-locate on text.split(), not the real parser -- induction TRAINING is
    unaffected by the real-parser question being asked here; only the EVAL/apply path below is
    routed through the real parser). Reused as-is (not re-implemented) to guarantee the induced
    hypothesis is byte-identical to the one already re-VET'd."""
    recs = _load_records()
    train_eps = []
    unresolved = []
    for r in recs:
        lemma = r["verb_lemma"]
        if lemma in exclude_lemmas:
            continue
        tokens = r["text"].split()
        v_idx = FI.locate_verb_idx(tokens, lemma)
        if v_idx is None:
            unresolved.append({"reason": "verb_not_located", "text": r["text"], "lemma": lemma})
            continue
        for a in r["args"]:
            a_idx = FI.locate_head_idx(tokens, a["head"])
            if a_idx is None:
                unresolved.append({"reason": "arg_not_located", "text": r["text"], "head": a["head"]})
                continue
            gold = "EXPERIENCER" if a["role"] == "EXPERIENCER" else "OTHER"
            feats = FI.real_construction_feats(tokens, v_idx, a_idx)
            train_eps.append({"feats": feats, "gold_class": gold})
    return train_eps, unresolved


def _induce(train_eps):
    classes = sorted({e["gold_class"] for e in train_eps})
    spec = FI.default_spec(classes, atoms=FI.REAL_CONSTRUCTION_ATOMS)
    return FI.induce(train_eps, spec=spec)


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _resolve_real_parse(gen, record):
    """Real front-end: UD-tokenize, tag+parse, find the gold verb+experiencer-arg positions in the
    UD-tokenized stream, and require the REAL candidate_generator to have LICENSED that (verb, arg)
    pair -- i.e. the arc parser's own structure must connect them, not just string-locate. Returns
    a dict with resolved bool, slot ('subj'/'obj'/None), predicted role, and diagnostics."""
    text = record["text"]
    lemma = record["verb_lemma"]
    arg = _find_experiencer_arg(record)
    cr = gen.generate(text)
    toks = cr.tokens  # UD-tokenized, 0-based positions match FI.locate_* below
    v_idx0 = FI.locate_verb_idx(toks, lemma)
    arg_idx0 = FI.locate_head_idx(toks, arg["head"]) if arg is not None else None
    diag = {"text": text, "lemma": lemma, "gold_head": arg["head"] if arg is not None else None}
    if v_idx0 is None or arg_idx0 is None:
        diag["failure_class"] = "LOCATE_FAILURE_IN_UD_TOKENS"
        return {"resolved": False, "diag": diag}
    v1, a1 = v_idx0 + 1, arg_idx0 + 1  # candidate_generator pairs are 1-based
    if (v1, a1) not in cr.candidates:
        diag["failure_class"] = "PARSER_DID_NOT_LICENSE_PAIR"
        diag["cand_pairs_for_verb"] = sorted(a for (vv, a) in cr.candidates if vv == v1)
        return {"resolved": False, "diag": diag}
    slot = "subj" if arg_idx0 < v_idx0 else "obj"
    diag["slot"] = slot
    diag["cand_rule"] = cr.cand_rules.get((v1, a1))
    return {"resolved": True, "tokens": toks, "v_idx": v_idx0, "arg_idx": arg_idx0, "slot": slot, "diag": diag}


def run_pipeline(run_mode):
    t0 = time.perf_counter()
    print("[%s] loading real persisted front-end (PosTagger + ArcParser)" % run_mode, flush=True)
    gen = CandidateGenerator.load(POS_PATH, ARC_PATH)

    print("[%s] loading dataset + building subj-axis induced hypothesis (leak-safe, "
          "identical protocol to exp_frame_primary_role_assigner_v1)" % run_mode, flush=True)
    recs = _load_records()
    subj_recs = [r for r in recs if r["exp_type"] == "subj"]
    n_subj_total = len(subj_recs)
    oov_subj_lemmas = sorted({r["verb_lemma"] for r in subj_recs if r["verb_lemma"] not in VERB_FRAMES})
    subj_train_eps, _unresolved_train = build_train_corpus(exclude_lemmas=set(oov_subj_lemmas))
    subj_name, subj_chosen, _all_results = _induce(subj_train_eps)
    subj_hyp = subj_chosen.hypothesis if subj_chosen is not None else None
    print("[%s] induced plugin=%s n_train_episodes=%d" % (run_mode, subj_name, len(subj_train_eps)), flush=True)

    per_record = []
    n_resolved = 0
    n_resolved_correct = 0
    n_resolved_wrong_slot = 0  # real parser licensed the pair but at the WRONG slot vs dataset exp_type=subj
    known_resolved_correct = known_resolved_total = 0
    oov_resolved_correct = oov_resolved_total = 0
    failure_classes = {}

    for i, r in enumerate(subj_recs):
        lemma = r["verb_lemma"]
        res = _resolve_real_parse(gen, r)
        if not res["resolved"]:
            fc = res["diag"].get("failure_class", "UNKNOWN")
            failure_classes[fc] = failure_classes.get(fc, 0) + 1
            per_record.append({"idx": i, "text": r["text"], "lemma": lemma, "resolved": False,
                               "pred": "UNRESOLVED", "correct": False, "diag": res["diag"]})
            continue
        n_resolved += 1
        toks, v_idx, arg_idx, slot = res["tokens"], res["v_idx"], res["arg_idx"], res["slot"]
        if slot != "subj":
            # real parser found the gold head, but on the WRONG SIDE of the verb (post-verbal) --
            # frame_primary_role would score this as the DEFERRED obj-axis path, not the subj-axis
            # EXPERIENCER contract this cell is measuring. Counted as resolved-but-wrong (not a
            # locate/parse failure) -- an honest end-to-end miss, not silently dropped.
            n_resolved_wrong_slot += 1
            per_record.append({"idx": i, "text": r["text"], "lemma": lemma, "resolved": True,
                               "slot": slot, "pred": "WRONG_SLOT", "correct": False, "diag": res["diag"]})
            continue
        pred = FI.frame_primary_role(lemma, toks, v_idx, arg_idx, "subj",
                                     chosen_name=subj_name, hypothesis=subj_hyp, default="AGENT")
        correct = bool(pred == "EXPERIENCER")
        if correct:
            n_resolved_correct += 1
        is_known = lemma in VERB_FRAMES
        if is_known:
            known_resolved_total += 1
            known_resolved_correct += int(correct)
        else:
            oov_resolved_total += 1
            oov_resolved_correct += int(correct)
        per_record.append({"idx": i, "text": r["text"], "lemma": lemma, "resolved": True,
                           "slot": slot, "pred": pred, "correct": correct, "known": is_known,
                           "diag": res["diag"]})

    resolve_rate = n_resolved / n_subj_total if n_subj_total else None
    on_resolved_acc = (n_resolved_correct / n_resolved) if n_resolved else None
    end_to_end_acc = n_resolved_correct / n_subj_total if n_subj_total else None  # unresolved = wrong
    known_resolved_acc = (known_resolved_correct / known_resolved_total) if known_resolved_total else None
    oov_resolved_acc = (oov_resolved_correct / oov_resolved_total) if oov_resolved_total else None

    digests = {"end_to_end_preds": hashlib.sha256(
        ("|".join(pr["pred"] for pr in per_record)).encode("utf-8")).hexdigest()}

    gold_parsed_acc = None
    gold_parsed_source = None
    if os.path.exists(GOLD_PARSED_METRICS_PATH):
        with open(GOLD_PARSED_METRICS_PATH, "r", encoding="utf-8") as f:
            gm = json.load(f)
        gold_parsed_acc = gm.get("acc_subj_experiencer_axis")
        gold_parsed_source = GOLD_PARSED_METRICS_PATH

    msg = (
        "END-TO-END subj-exp-axis (real parse): resolve_rate=%.4f (resolved=%d/%d) | "
        "on_resolved_acc=%s (N=%d) | effective_end_to_end_acc=%.4f (unresolved=wrong) | "
        "n_resolved_wrong_slot=%d | known_resolved_acc=%s (N=%d) oov_resolved_acc=%s (N=%d) | "
        "gold_parsed_acc_CITED=%s (from %s) | failure_classes=%s" % (
            resolve_rate, n_resolved, n_subj_total,
            ("%.4f" % on_resolved_acc) if on_resolved_acc is not None else "n/a", n_resolved,
            end_to_end_acc, n_resolved_wrong_slot,
            ("%.4f" % known_resolved_acc) if known_resolved_acc is not None else "n/a", known_resolved_total,
            ("%.4f" % oov_resolved_acc) if oov_resolved_acc is not None else "n/a", oov_resolved_total,
            ("%.4f" % gold_parsed_acc) if gold_parsed_acc is not None else "n/a", gold_parsed_source,
            failure_classes))

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "verdict": "MEASURED_HONEST_NUMBER",
        "verdict_msg": msg, "summary": msg, "elapsed_s": round(elapsed, 4),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "data_source": DATA_PATH, "pos_path": POS_PATH, "arc_path": ARC_PATH,
        "n_subj_axis_sentences": n_subj_total,
        "n_resolved": n_resolved, "n_unresolved": n_subj_total - n_resolved,
        "resolve_rate": resolve_rate,
        "n_resolved_correct": n_resolved_correct, "n_resolved_wrong_slot": n_resolved_wrong_slot,
        "on_resolved_acc": on_resolved_acc,
        "effective_end_to_end_acc": end_to_end_acc,
        "known_resolved_acc": known_resolved_acc, "n_known_resolved": known_resolved_total,
        "oov_resolved_acc": oov_resolved_acc, "n_oov_resolved": oov_resolved_total,
        "failure_classes": failure_classes,
        "gold_parsed_acc_cited": gold_parsed_acc, "gold_parsed_source": gold_parsed_source,
        "induced_plugin_subj_axis": subj_name, "n_train_episodes_subj_axis": len(subj_train_eps),
        "oov_subj_lemmas": oov_subj_lemmas,
        "per_record": per_record,
        "arms_differ": digests,
        "hp_band": "n/a: honest-number measurement cell, not a HARD_PASS/FAIL gate",
        "cell_chunked": False, "final_metrics_atomicity": "tmp_replace",
        "crlb_n_a": "accuracy over a discrete 2-class axis; no capacity/CRLB floor",
        "baseline_in_band": "n/a (measurement cell)",
        "cardinality_ok": True, "expected_n_units": 1,
        "calibration_check": "default_ok_for_this_regime",
        "deterministic_seeding": True,
        "progress_logging": "print_flush_true",
        "honest_scope": (
            "This is the REAL end-to-end number: sentences where the persisted PosTagger+ArcParser "
            "front-end does not license the gold (verb, subject-argument) pair as its own candidate "
            "are UNRESOLVED and counted as wrong in effective_end_to_end_acc, per the unresolved=wrong "
            "contract. Distinct from acc_gold_parsed=%s (assumes a perfect parse; the isolated 3c "
            "cell's headline number) -- do NOT conflate the two." % (
                ("%.4f" % gold_parsed_acc) if gold_parsed_acc is not None else "n/a")),
    }
    return metrics


def _instrumentation_selftest():
    FI._selftest()
    FI._selftest_real_adapter()
    FI._selftest_frame_primary()
    recs = _load_records()
    assert len(recs) == 118, "dataset record count changed: %d (expected 118)" % len(recs)
    assert os.path.exists(POS_PATH), "missing persisted POS model: %s" % POS_PATH
    assert os.path.exists(ARC_PATH), "missing persisted ARC model: %s" % ARC_PATH


_instrumentation_selftest()


def self_test():
    """Real-code-path smoke: load the REAL persisted front-end, generate REAL candidates for a
    tiny hand-built known-psych sentence, and confirm the resolved -> frame_primary_role path
    produces EXPERIENCER (not a synthetic-only branch)."""
    t0 = time.perf_counter()
    gen = CandidateGenerator.load(POS_PATH, ARC_PATH)
    fake_rec = {"text": "He feared the storm.", "verb_lemma": "fear",
               "args": [{"head": "he", "role": "EXPERIENCER"}, {"head": "storm", "role": "THEME"}],
               "exp_type": "subj"}
    res = _resolve_real_parse(gen, fake_rec)
    assert res["resolved"], "self-test sentence failed to resolve via real parser: %s" % res["diag"]
    assert res["slot"] == "subj", res
    pred = FI.frame_primary_role("fear", res["tokens"], res["v_idx"], res["arg_idx"], "subj")
    assert pred == "EXPERIENCER", pred
    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": "self_test", "verdict": "SELFTEST_PASS",
        "verdict_msg": "SELFTEST_PASS: real front-end (PosTagger+ArcParser) + candidate_generator "
                       "+ frame_primary_role exercised end-to-end on a real-code-path smoke sentence",
        "summary": "SELFTEST_PASS", "elapsed_s": round(elapsed, 4),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "cell_chunked": False, "final_metrics_atomicity": "tmp_replace",
    }
    _write_metrics(OUTPUT_DIR, metrics)
    print("[self_test] verdict=%s elapsed=%.2fs" % (metrics["verdict"], elapsed), flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run-mode", choices=["full", "self_test"], default="full")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(0 if self_test() else 1)
    metrics = run_pipeline(run_mode=args.run_mode)
    _write_metrics(OUTPUT_DIR, metrics)
    print("[%s] verdict=%s" % (args.run_mode, metrics["verdict"]), flush=True)
    print("[%s] %s" % (args.run_mode, metrics["verdict_msg"]), flush=True)
    print(json.dumps({k: v for k, v in metrics.items() if k not in ("per_record",)}, indent=2), flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise
