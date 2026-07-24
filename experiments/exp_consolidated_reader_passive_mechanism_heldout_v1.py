"""SYSTEMATIC PASSIVE MECHANISM -- held-out hard-syntax capability test (v1).

Turns the banked reader's DIRECTIONAL passive result (fires on 2/13 held-out passages by parse-luck,
seq 29503) into a real CAPABILITY via a systematic thematic-reanalysis mechanism
(experiments/exp_reader_passive_thematic_reanalysis_v1.py). On EVERY detected passive: pre-verbal
grammatical subject -> PATIENT, by-object NP head -> AGENT. Overrides the perceptron/ECM-routing for
passive predicates only; non-passive predicates byte-identical to the banked composed reader.

CONDITIONS (one composed reader, one naive, one gold; the ONLY variable is the mechanism flag):
  ON  : CR patched + flags['passive_reanalysis']=True on the held-out hard-syntax gold (24 items,
        13 passages, VET'd-solid, seq 29503). METRIC = distinct passages that FIRE (>=1 correct
        who-did-what item) + reader-vs-naive margin + per-passage reversal correctness.
  OFF : same patched CR, flag=False == banked behavior (P2 ablation: the passages must drop back to the
        parse-luck baseline -- proves the mechanism fires, not luck).
  P1  : McGuffey composed patient-F1 on FULL_SLICE (163 golded sentences), full_general config,
        WITHOUT vs WITH the mechanism -- non-regression (precise passive detection must not over-fire on
        actives). Baseline reproduces the banked composed F1 (~0.6423).

NEVER-CONFIDENTLY-WRONG: the mechanism emits only when a subject is found AND a real agent (by-PP head
or carried antecedent) exists; abstains on agentless passives with no antecedent + on self-loops.
ANTI-CIRCULAR: the hard-syntax gold is HELD-OUT and was authored BLIND to any reader; the mechanism is a
GENERAL passive rule (structural POS/preposition/order cues; word-identity-free), NOT tuned to the gold
items. NOT banked (skunkworks VETs; chain-grade re-attempt if it lands as a capability).

PRE-REGISTERED BANDS (set BEFORE this run):
  Let ON_fired = distinct passages (of 13) with >=1 correct reader item WITH the mechanism.
  Let OFF_fired = same WITHOUT the mechanism (ablation).
  VALIDITY: naive_acc <= 0.20 on the hard-syntax gold (inherited fairness self-check).
  HARD_PASS (CAPABILITY): VALIDITY AND ON_fired >= 6 AND (ON_fired - OFF_fired) >= 3 AND reader strictly
    beats naive (n_reader_on - n_naive >= 3) AND McGuffey NON-REGRESSION (mcg_f1_on >= mcg_f1_base - 0.002).
  MIDDLE (mechanism helps but sub-capability): VALIDITY AND 4 <= ON_fired <= 5 AND no McGuffey regression.
  HARD_FAIL: ON_fired < 4  OR  mcg_f1_on < mcg_f1_base - 0.01 (over-fires on actives)  OR
    n_reader_on <= n_naive (reader no better than order).

BRAIN-CHECK: constraint-based lexicalist parsing -- passive morphology (aux-be + participle) + by-PP
  licenses a NON-canonical thematic mapping that OVERRIDES linear order. The perceptron/order baseline is
  the linear-order null the human overrides using morphosyntax; the mechanism installs exactly that
  override as a structural rule, firing on every detected passive rather than by parse-luck.

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- from-scratch arc-eager parser train
  (~44s once) + per-clause greedy decode + AveragedPerceptron + dict lookups; NO matmul/GPU primitive.
  McGuffey FULL_SLICE (163 sents) + 13 hard-syntax passages x {ON, OFF}. Wall ~2-4min foreground.
  Storage: no_storage. Runtime invariant: glass-box, NO LLM/network/autograd at inference. Determinism:
  OMP/MKL/OPENBLAS=1, fixed int SEED (inherited from CR), sorted(set). LOCAL-ONLY, foreground-to-
  completion. NO push / NO remote-persist / NO queue_add / NO bank.

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground candidate cell):
  - arms_differ_verified at self-test (ON vs OFF reader kept-tuple hashes differ)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - VALIDITY gate: naive_acc <= 0.20 (fairness self-check inherited from seq 29503)
  - discriminator can-fail: mechanism CAN under-fire / CAN regress McGuffey (honest HARD_FAIL bands)
  - P2 ablation built in (flag OFF must reproduce banked parse-luck baseline)
  - deterministic seeding (fixed int SEED inherited from CR; sorted(set))
  - all numbers tagged MEASURED@ (printed at run) / CITED@ (banked component metrics) in this docstring
  - N/A: KGStore (no KG); N/A CRLB (discrete count/accuracy, no HD noise floor); N/A multi-seed
  - progress_logging: print_flush_true (sys.stdout line-buffered at cell start)

CITED: banked composed McGuffey F1 ~0.6423 (full_general) @ exp_consolidated_reader_chaingrade_FULL_v1;
       banked hard-syntax held-out reader 4/24 over 2/13 passages, margin +4 @
       data/exp_consolidated_reader_hardsyntax_heldout_v1/metrics.json (seq 29503).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

ANCHOR_NAME = "consolidated_reader_passive_mechanism_heldout_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from experiments import exp_consolidated_reader_chaingrade_FULL_v1 as CR             # noqa: E402
from experiments import exp_consolidated_reader_hardsyntax_heldout_v1 as H           # noqa: E402
from experiments import exp_reader_passive_thematic_reanalysis_v1 as PM              # noqa: E402
from experiments import exp_multipred_depparse_argstruct_recall_v2 as M              # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L   # noqa: E402

SEED = CR.SEED

# Pre-registered bands
VALIDITY_MAX_NAIVE_ACC = 0.20
HP_MIN_FIRED = 6            # distinct passages of 13 firing WITH the mechanism (capability threshold)
HP_MIN_DELTA_FIRED = 3     # ON_fired - OFF_fired (mechanism drives the gain, not parse-luck)
HP_MIN_READER_MARGIN = 3   # n_reader_on - n_naive
MCG_REGRESS_TOL = 0.002    # non-regression: mcg_f1_on >= mcg_f1_base - this
MCG_HARD_FAIL_TOL = 0.01   # over-fire regression => HARD_FAIL
MB_MIN_FIRED = 4


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def _flags(passive_on):
    f = CR.full_general_flags()
    f["passive_reanalysis"] = bool(passive_on)
    return f


def _score_hardsyntax(passages, gold, order, W, clf, sel_fn, flags):
    """Composed reader vs naive on the hard-syntax gold with a given flags dict (mechanism via patch)."""
    arm, gate, supp = CR.build_composed_arm(order, passages, W, clf, sel_fn, CR.DITRANS_FN, flags)
    n_reader, per_reader = CR._score_litbank(arm, gold)
    naive = CR.naive_positional_on_text(order, passages)
    n_naive, per_naive = CR._score_litbank(naive, gold)
    r_hit = {x["qid"]: x["correct"] for x in per_reader}
    n_hit = {x["qid"]: x["correct"] for x in per_naive}
    # distinct passages that FIRE (>=1 correct reader item)
    fired_pids = sorted({g["pid"] for g in gold if r_hit.get(g["qid"], False)})
    naive_fired_pids = sorted({g["pid"] for g in gold if n_hit.get(g["qid"], False)})
    per_item = []
    for g in gold:
        per_item.append(dict(qid=g["qid"], pid=g["pid"], kind=g["kind"], verb=g["verb"],
                             answer=g["answer"], reader=bool(r_hit.get(g["qid"], False)),
                             naive=bool(n_hit.get(g["qid"], False)),
                             reader_emitted=next((x["matched"] for x in per_reader
                                                  if x["qid"] == g["qid"]), None)))
    return dict(n_reader=n_reader, n_naive=n_naive, fired_pids=fired_pids,
                naive_fired_pids=naive_fired_pids, per_item=per_item,
                arm_hash=M.arm_hash(arm), naive_hash=M.arm_hash(naive),
                passive_fired=int(supp.get("passive_reanalysis_fired", 0)))


def _mcguffey_f1(W, clf, sel_fn, slice_lessons, passive_on):
    """McGuffey composed patient-F1 on the given slice, full_general config, mechanism ON/OFF."""
    order, sent_text, _reader_svo = L.load_slice_and_reader(slice_lessons)
    gold, _meta = L.load_gold(slice_lessons)
    arm, _gate, _supp = CR.build_composed_arm(order, sent_text, W, clf, sel_fn, CR.DITRANS_FN,
                                              _flags(passive_on))
    sc, _rc = CR._score_mcg(arm, gold)
    return dict(f1=round(sc["f1"], 4), precision=round(sc["precision"], 4),
                recall=round(sc["recall"], 4), n_pred=sc["n_pred"], tp=sc["tp"], n_gold=sc["n_gold"],
                arm_hash=M.arm_hash(arm))


# =======================================================================================
# Markers / metrics / crash-diagnostic (atomic).
# =======================================================================================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=f"{type(exc).__name__}: {str(exc)[:500]}",
                summary=f"CELL_CRASHED: {type(exc).__name__}", elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(), anchor_name=ANCHOR_NAME)
    _write_metrics(output_dir, diag)


# =======================================================================================
# Self-test (design-gate).
# =======================================================================================
def self_test():
    print("[self-test] build gold + fit pipeline ...", flush=True)
    passages, gold, n_novels = H.build_hardsyntax_gold()
    order = sorted(passages.keys())
    clf, sel_fn, W, parser_info = H._fit_pipeline("smoke")
    assert parser_info["uas_dev"] > 0.5, f"parser UAS low: {parser_info}"

    # structural helper unit tests (a couple of the diagnosed cases) -- NOT gold-tuned, just POS logic
    import experiments.exp_oracle_mention_upperbound_reader_v1 as ORC
    tg = ORC.pos_tag_sentence("Presently he was met by an elderly parson astride on a gray mare")
    lows = [t[1] for t in tg]
    v0 = next(i for i, t in enumerate(tg) if t[1] == "met")
    byh = PM.by_object_head(tg, v0, ORC)
    subj = PM.passive_subject(tg, v0, byh, ORC)
    print(f"[self-test] met: by_head={tg[byh][0] if byh is not None else None} "
          f"subj={tg[subj][0] if subj is not None else None}", flush=True)
    assert byh is not None and tg[byh][1] == "parson", "by-head should skip adjective to 'parson'"
    assert subj is not None and tg[subj][1] == "he", "subject should be pre-verbal 'he'"

    # VALIDITY: naive fails on the hard-syntax gold
    naive = CR.naive_positional_on_text(order, passages)
    n_naive, _ = CR._score_litbank(naive, gold)
    naive_acc = n_naive / len(gold)
    print(f"[self-test] VALIDITY naive={n_naive}/{len(gold)} acc={naive_acc:.3f}", flush=True)
    assert naive_acc <= VALIDITY_MAX_NAIVE_ACC, f"INVALID_SLICE naive_acc={naive_acc}"

    # install; ON vs OFF arms must differ (mechanism is the lever)
    PM.install(CR)
    try:
        on = _score_hardsyntax(passages, gold, order, W, clf, sel_fn, _flags(True))
        off = _score_hardsyntax(passages, gold, order, W, clf, sel_fn, _flags(False))
    finally:
        PM.uninstall(CR)
    print(f"[self-test] ON n_reader={on['n_reader']} fired={len(on['fired_pids'])} "
          f"passive_fired={on['passive_fired']} | OFF n_reader={off['n_reader']} "
          f"fired={len(off['fired_pids'])}", flush=True)
    assert on["arm_hash"] != off["arm_hash"], "META_RULE_AF: ON/OFF arms bit-identical (flag inert)"
    assert on["passive_fired"] >= 1, "mechanism did not fire on any passive"
    # OFF must reproduce the banked baseline (flag off == byte-identical to banked)
    assert off["n_reader"] == 4, f"OFF (ablation) should reproduce banked 4/24, got {off['n_reader']}"

    print("[self-test] PASS", flush=True)
    return 0


# =======================================================================================
# Full run (foreground to completion).
# =======================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode, expected_n_units=13)
    print(f"[full] mode={run_mode} systematic passive mechanism held-out capability test", flush=True)

    passages, gold, n_novels = H.build_hardsyntax_gold()
    order = sorted(passages.keys())
    n_gold = len(gold)
    n_passages = len(order)
    clf, sel_fn, W, parser_info = H._fit_pipeline(run_mode)
    print(f"[full] parser uas={parser_info['uas_dev']}", flush=True)

    PM.install(CR)
    try:
        on = _score_hardsyntax(passages, gold, order, W, clf, sel_fn, _flags(True))
        off = _score_hardsyntax(passages, gold, order, W, clf, sel_fn, _flags(False))
        # P1 McGuffey non-regression (full_general baseline vs +mechanism)
        slice_lessons = M.SMOKE_SLICE if run_mode == "smoke" else M.FULL_SLICE
        mcg_base = _mcguffey_f1(W, clf, sel_fn, slice_lessons, passive_on=False)
        mcg_on = _mcguffey_f1(W, clf, sel_fn, slice_lessons, passive_on=True)
    finally:
        PM.uninstall(CR)

    on_fired = len(on["fired_pids"])
    off_fired = len(off["fired_pids"])
    naive_acc = round(on["n_naive"] / n_gold, 4)
    reader_acc_on = round(on["n_reader"] / n_gold, 4)
    reader_margin = on["n_reader"] - on["n_naive"]
    delta_fired = on_fired - off_fired
    validity_ok = (naive_acc <= VALIDITY_MAX_NAIVE_ACC)
    mcg_non_regression = (mcg_on["f1"] >= mcg_base["f1"] - MCG_REGRESS_TOL)
    mcg_hard_regress = (mcg_on["f1"] < mcg_base["f1"] - MCG_HARD_FAIL_TOL)

    print(f"[full] ON fired={on_fired}/{n_passages} pids={on['fired_pids']} n_reader={on['n_reader']} "
          f"passive_fired={on['passive_fired']}", flush=True)
    print(f"[full] OFF fired={off_fired}/{n_passages} pids={off['fired_pids']} n_reader={off['n_reader']}",
          flush=True)
    print(f"[full] naive={on['n_naive']} acc={naive_acc} reader_margin=+{reader_margin} "
          f"delta_fired=+{delta_fired}", flush=True)
    print(f"[full] McGuffey f1 base={mcg_base['f1']} on={mcg_on['f1']} "
          f"non_regression={mcg_non_regression}", flush=True)

    is_capability = (validity_ok and on_fired >= HP_MIN_FIRED and delta_fired >= HP_MIN_DELTA_FIRED
                     and reader_margin >= HP_MIN_READER_MARGIN and mcg_non_regression)
    is_middle = (validity_ok and MB_MIN_FIRED <= on_fired <= (HP_MIN_FIRED - 1) and not mcg_hard_regress)

    if not validity_ok:
        verdict = "INVALID_SLICE_NAIVE_NOT_LOW"
        vmsg = (f"VALIDITY FAIL: naive {on['n_naive']}/{n_gold} (acc={naive_acc} > "
                f"{VALIDITY_MAX_NAIVE_ACC}); slice not hard-syntax.")
    elif mcg_hard_regress:
        verdict = "PASSIVE_MECHANISM_HARD_FAIL_MCGUFFEY_REGRESSION"
        vmsg = (f"OVER-FIRES ON ACTIVES: McGuffey composed F1 {mcg_on['f1']} < base {mcg_base['f1']} - "
                f"{MCG_HARD_FAIL_TOL}. Precise passive detection failed the P1 fairness gate. "
                f"hard-syntax ON_fired={on_fired}/{n_passages}.")
    elif is_capability:
        verdict = "PASSIVE_MECHANISM_CAPABILITY_EARNED"
        vmsg = (f"SYSTEMATIC PASSIVE = CAPABILITY: mechanism fires on {on_fired}/{n_passages} independent "
                f"held-out passages (up from OFF={off_fired}; delta +{delta_fired}), reader recovers "
                f"{on['n_reader']}/{n_gold} who-did-what (acc={reader_acc_on}) vs naive {on['n_naive']}/"
                f"{n_gold} (acc={naive_acc}), margin +{reader_margin}. McGuffey composed F1 non-regression: "
                f"base={mcg_base['f1']} -> on={mcg_on['f1']}. P2 ablation (flag OFF) reproduces the banked "
                f"parse-luck baseline ({off_fired} passages). fired_pids={on['fired_pids']}. Systematic "
                f"(subject->PATIENT, by-object->AGENT on every detected passive), NOT parse-luck. "
                f"CHAIN-GRADE CANDIDATE -- HYPOTHESIS pending skunkworks landed-VET; NOT banked.")
    elif is_middle:
        verdict = "PASSIVE_MECHANISM_MIDDLE_SUBCAPABILITY"
        vmsg = (f"Mechanism helps but below capability: ON_fired={on_fired}/{n_passages} "
                f"(OFF={off_fired}, delta +{delta_fired}), reader {on['n_reader']}/{n_gold} vs naive "
                f"{on['n_naive']}, margin +{reader_margin}. McGuffey base={mcg_base['f1']} on={mcg_on['f1']}. "
                f"Autopsy which passives still fail. fired_pids={on['fired_pids']}.")
    else:
        verdict = "PASSIVE_MECHANISM_HARD_FAIL_UNDERFIRE"
        vmsg = (f"HONEST NEGATIVE: mechanism fires on only {on_fired}/{n_passages} passages "
                f"(<{MB_MIN_FIRED}); OFF={off_fired}, delta +{delta_fired}, reader margin +{reader_margin}. "
                f"Autopsy the still-failing passives. fired_pids={on['fired_pids']}.")

    # autopsy: which passages STILL fail under the mechanism + why-signal
    still_failing = sorted(set(order) - set(on["fired_pids"]))
    recovered_by_mechanism = sorted(set(on["fired_pids"]) - set(off["fired_pids"]))

    elapsed = round(time.perf_counter() - t0, 2)
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: ON_fired={on_fired}/{n_passages} (OFF={off_fired}, delta +{delta_fired}) "
                 f"reader={on['n_reader']}/{n_gold} (acc={reader_acc_on}) vs naive={on['n_naive']} "
                 f"margin=+{reader_margin} | McGuffey f1 {mcg_base['f1']}->{mcg_on['f1']} "
                 f"non_regress={mcg_non_regression} | capability={is_capability} | "
                 f"parser_uas={parser_info['uas_dev']}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED,
        n_gold=n_gold, n_passages=n_passages, n_novels=n_novels,
        naive_acc=naive_acc, reader_acc_on=reader_acc_on,
        on_fired=on_fired, off_fired=off_fired, delta_fired=delta_fired,
        on_fired_pids=on["fired_pids"], off_fired_pids=off["fired_pids"],
        recovered_by_mechanism=recovered_by_mechanism, still_failing_pids=still_failing,
        n_reader_on=on["n_reader"], n_reader_off=off["n_reader"], n_naive=on["n_naive"],
        reader_margin=reader_margin, passive_reanalysis_fired=on["passive_fired"],
        is_capability=bool(is_capability),
        mcguffey=dict(base=mcg_base, on=mcg_on, non_regression=mcg_non_regression,
                      hard_regress=mcg_hard_regress, regress_tol=MCG_REGRESS_TOL),
        validity_ok=validity_ok,
        per_item_on=on["per_item"], per_item_off=off["per_item"],
        arm_hash_on=on["arm_hash"], arm_hash_off=off["arm_hash"], naive_hash=on["naive_hash"],
        bars=dict(ARM_A_reader_acc_on=reader_acc_on,
                  ARM_B_reader_margin=reader_margin,
                  ARM_B_reader_beats_naive=bool(on["n_reader"] > on["n_naive"]),
                  ARM_C_passages_fired_on=on_fired,
                  ARM_D_mcguffey_non_regression=bool(mcg_non_regression)),
        bands=dict(VALIDITY_MAX_NAIVE_ACC=VALIDITY_MAX_NAIVE_ACC, HP_MIN_FIRED=HP_MIN_FIRED,
                   HP_MIN_DELTA_FIRED=HP_MIN_DELTA_FIRED, HP_MIN_READER_MARGIN=HP_MIN_READER_MARGIN,
                   MCG_REGRESS_TOL=MCG_REGRESS_TOL, MCG_HARD_FAIL_TOL=MCG_HARD_FAIL_TOL,
                   MB_MIN_FIRED=MB_MIN_FIRED),
        parser_info=parser_info,
        one_variable=("the passive_reanalysis flag (systematic thematic reversal ON vs OFF) on ONE composed "
                      "reader / ONE naive / ONE held-out hard-syntax gold. OFF == banked reader byte-"
                      "identically (P2 ablation). McGuffey P1 = same full_general config +/- mechanism."),
        anti_circular_note=("Hard-syntax gold HELD-OUT + authored blind to any reader (seq 29503). Mechanism "
                            "is a GENERAL passive rule (POS/preposition/order; word-identity-free), NOT tuned "
                            "to gold items. Agentless-passive patients (no antecedent) intentionally ABSTAIN "
                            "(never-confidently-wrong) -- a named residual gap, not a silent miss."),
        scope_caveat=("Small held-out probe (N=%d items, %d passages, %d novels). CHAIN-GRADE CANDIDATE, "
                      "CLAIM-VET-pending; NOT banked." % (n_gold, n_passages, n_novels)),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"], flush=True)
    print("verdict:", verdict, flush=True)
    print("verdict_msg:", vmsg, flush=True)
    print("recovered_by_mechanism:", recovered_by_mechanism, flush=True)
    print("still_failing_pids:", still_failing, flush=True)
    print("per_item_on:", json.dumps([{k: it[k] for k in ("qid", "answer", "reader", "naive")}
                                       for it in on["per_item"]]), flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run-mode", default="full")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    run_mode = "smoke" if args.smoke else args.run_mode
    output_dir = _out_dir(run_mode)
    return build_verdict(output_dir, run_mode)


if __name__ == "__main__":
    try:
        rc = main()
        sys.exit(rc if rc is not None else 0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_out_dir("full"), e)
        raise
