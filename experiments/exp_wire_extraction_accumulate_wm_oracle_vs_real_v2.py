# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (hash-compare ORACLE/REAL/FLOOR registers)
# - final_metrics_atomicity = tmp_replace (single-shot; whole run < 30s)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a: "structural can-fail test, no CRLB noise floor applies"; discriminator_reachability=true
#   (ORACLE reproduction of 36ab29a93 IS the reachability check)
# - baseline_in_band EXEMPTED for FLOOR arm (can-fail arm is REQUIRED near its structural floor)
# - cell_chunked=False (single pass, 3 arms, wall time < 30s; per-arm checkpoint via
#   tools/exp_checkpoint.py used anyway per CLAUDE.md's "any cell looping over >1 unit" rule)
# - HYPOTHESIZED/MEASURED/CITED/THEORETICAL tags on every number in this docstring
# - ASCII-only, no emojis, no em dashes.
"""exp_wire_extraction_accumulate_wm_oracle_vs_real_v2 (2026-08-02)

RE-RUN of exp_wire_extraction_accumulate_wm_oracle_vs_real_v1 (director atom 29610, HARD_FAIL:
REAL multi_event_recall=0.2308 ~= floor 0.1923) with STAGE 1 replaced by the FIXED
construction-conditional MULTI-ROLE extraction (exp_extraction_construction_conditional_
multirole_v1.py), trained on the FULL construction distribution (canonical + quotative +
by-agent-passive + degenerate-passive) with a 4-way per-mention softmax readout
{agent, patient, addressee, none}, instead of the OLD binary is-agent-or-not model trained ONLY
on non-canonical gold.

MEASURED@data/exp_extraction_construction_conditional_multirole_v1/metrics.json (this session,
full run before this cell): per-construction role_acc, OLD vs NEW --
  canonical:      OLD 0.3576 (n=330) -> NEW 0.4091   (small lift, still BELOW the naive
                  position-only baseline 0.5364 on this construction -- an honest residual
                  weakness, reported not hidden)
  quotative:      OLD 0.6230 (n=61)  -> NEW 0.8525   (clear improvement)
  passive_byagent: OLD 0.8511 (n=47) -> NEW 0.7872   (small regression, still well above floor)
  passive (degenerate, n=12): OLD 0.8333 -> NEW 0.5000 (regression on a tiny, single-class,
                  already-near-saturated slice)
So the fix is a REAL but PARTIAL win at the extraction layer, not a clean sweep. This cell's
question: does that partial extraction improvement translate into ANY end-to-end recall lift on
the (canonical-dominated) multiclause narrative gold, versus the OLD extraction's 0.2308?

STAGE 2 (accumulate WM) and the ORACLE/FLOOR arms are UNCHANGED from v1 (same FHRR bind/bundle/
cleanup math, same role_vecs/idx_vecs seed, same gold_multiclause_entity_track_v2.jsonl target)
so ORACLE reproduction (sanity: WM organ still works) and FLOOR (non-vacuous chance) are re-verified
identically; only the REAL arm's per-clause role source changes (NEW multiclass model instead of
OLD binary model).

COVERAGE-HONESTY (pre-registered before running, from the NEW model's own class vocabulary): NEW
covers {agent, patient, addressee}; the downstream 6-way ROLE_VOCAB used by the accumulate register
also has {theme, recipient, speaker} for which there is STILL zero training signal anywhere in the
gold pools (role_census below reports the exact unreachable fraction on THIS eval set, same
structural-gap framing as v1, now with one additional reachable class).

Run:  .venv/Scripts/python.exe experiments/exp_wire_extraction_accumulate_wm_oracle_vs_real_v2.py --self-test
      .venv/Scripts/python.exe experiments/exp_wire_extraction_accumulate_wm_oracle_vs_real_v2.py --full
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_checkpoint as ckpt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# STAGE 2 (accumulate WM) + shared plumbing, REUSED VERBATIM from v1 (import, not reimplemented).
from exp_wire_extraction_accumulate_wm_oracle_vs_real_v1 import (  # noqa: E402
    unit_phase_vec, fhrr_bind, fhrr_unbind, fhrr_bundle, cleanup_argmax, run_self_test,
    match_mention_to_token, load_multiclause_gold, role_census, build_register, score_entity,
    MAX_EVENT_SLOTS, fit_production_extraction_model as fit_old_model,
    stage1_predict_clause as old_stage1_predict_clause,
)

# FIX (measured on the first --full attempt): v1's ROLE_VOCAB = [agent,patient,theme,recipient,
# addressee,speaker] KeyErrors on "possessor"/"experiencer" -- role types the powered v2 gold added
# (commit 6594a6ee5, 5 new multi-event passages) that did not exist when v1's ROLE_VOCAB was fixed.
# Extended here to cover every role literally present in gold_multiclause_entity_track_v2.jsonl
# (checked via role_census below at runtime; this list is a superset, exact-match KeyError-free).
ROLE_VOCAB = ["agent", "patient", "theme", "recipient", "addressee", "speaker", "possessor", "experiencer"]

# FIX (checked before running): v1's GOLD_MULTICLAUSE constant points at
# gold_multiclause_entity_track_v1.jsonl (6 passages, N=13 multi-event entities) -- the file that
# existed when the v1 wire cell was authored (commit 8b57859cf), BEFORE the gold was powered up to
# v2 (11 passages, N=20 multi-event entities, commit 6594a6ee5, LATER). The director spawn-prompt's
# pointer explicitly names the POWERED v2 file for this re-run, so v2 of this cell targets it
# directly (v1's own GOLD_MULTICLAUSE constant is intentionally NOT reused here).
GOLD_MULTICLAUSE = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1", "gold_multiclause_entity_track_v2.jsonl"
)
# STAGE 1 (NEW fixed multi-role extraction), REUSED VERBATIM from the new extraction cell.
from exp_extraction_construction_conditional_multirole_v1 import (  # noqa: E402
    tokenize, get_tagger, quote_spans, norm_word, VERB_POS, BE_FORMS, MENTION_POS,
    load_canonical_pool, load_quotative_pool, load_byagent_pool, load_passive_pool,
    build_sentence_multi, mention_features_multi, build_design_multi, fit_softmax, _softmax,
    ROLE_VOCAB4, ROLE_IDX, L2_LAMBDA, LR, N_ITERS,
)

ANCHOR_NAME = "wire_extraction_accumulate_wm_oracle_vs_real_v2"

ORACLE_REPRO_TOL = 0.08
ORACLE_REPRO_TARGET = 1.0
FLOOR_MAX = 1.0 / len(ROLE_VOCAB) + 0.15
# v1's REAL_HARD_PASS_MIN/REAL_MIDDLE_MIN were set for the OLD binary extraction. Re-declared here
# BEFORE running v2 (same rationale: extraction is imperfect + a real coverage gap remains, so the
# ceiling is "clearly beats floor and the v1 REAL result" not "reproduces ORACLE").
REAL_HARD_PASS_MIN = 0.50
REAL_MIDDLE_MIN = 0.30
V1_REAL_BASELINE = 0.2308   # MEASURED@data/exp_wire_extraction_accumulate_wm_oracle_vs_real_v1/
                            # metrics.json:summary.real_multi_event_recall (director atom 29610)
V2_MUST_BEAT_V1_MARGIN = 0.05   # the ONE-VARIABLE claim: v2's REAL arm must beat v1's REAL arm by
                                 # at least this much, else the extraction fix did not help end-to-end


def repo_path(rel: str) -> str:
    return rel if os.path.isabs(rel) else os.path.join(REPO_ROOT, rel)


OUTPUT_DIR = repo_path(f"data/exp_{ANCHOR_NAME}")


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": os.environ.get("COMPUTERNAME", "unknown")}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


# ---------------------------------------------------------------------------
# STAGE 1: fit the FIXED multi-role model on 100% of its own pooled gold (canonical + quotative +
# byagent + degenerate passive), then apply it OUT-OF-DOMAIN to the multiclause narrative clauses.
# ---------------------------------------------------------------------------
def fit_new_production_extraction_model():
    canon_recs, _ = load_canonical_pool()
    quot_recs = load_quotative_pool()
    byagent_recs = load_byagent_pool()
    passive_recs = load_passive_pool()
    all_recs = canon_recs + quot_recs + byagent_recs + passive_recs
    train_sents = [build_sentence_multi(r) for r in all_recs]
    X, y, _, _ = build_design_multi(train_sents)
    mu = X[:, :-1].mean(axis=0)
    sd = X[:, :-1].std(axis=0)
    sd[sd < 1e-8] = 1.0
    Xs = X.copy()
    Xs[:, :-1] = (X[:, :-1] - mu) / sd
    W = fit_softmax(Xs, y, len(ROLE_VOCAB4), L2_LAMBDA, LR, N_ITERS)
    return {"W": W, "mu": mu, "sd": sd, "n_train_sentences": len(train_sents)}


def stage1_predict_clause_v2(text, model):
    """Apply the FIXED multi-role model to one clause (no gold role_map -- applied out-of-domain).
    Returns (sent, {mention_idx: predicted_role_str})."""
    sent = build_sentence_multi({"text": text, "kind": "eval", "role_map": {}, "parser_correct": False})
    if not sent["mention_idx"]:
        return sent, {}
    W, mu, sd = model["W"], model["mu"], model["sd"]
    preds = {}
    for i in sent["mention_idx"]:
        raw = mention_features_multi(sent, i)
        std = (raw - mu) / sd
        logits = np.append(std, 1.0) @ W
        probs = _softmax(logits.reshape(1, -1))[0]
        preds[i] = ROLE_VOCAB4[int(probs.argmax())]
    return sent, preds


def build_entity_chains_old(passages, old_model, restrict_n=None):
    """Apples-to-apples control: the FROZEN OLD binary extraction applied to the SAME v2 gold (v1's
    own 0.2308 baseline was measured on the smaller, pre-powering v1 gold -- see the GOLD_MULTICLAUSE
    comment above). This isolates the ONE VARIABLE (extraction model) from the gold-set change."""
    if restrict_n is not None:
        passages = passages[:restrict_n]
    entities_out = []
    for rec in passages:
        clauses = rec["clauses"]
        clause_infer = [old_stage1_predict_clause(c, old_model) for c in clauses]
        used_per_clause = [set() for _ in clauses]
        for name, chain in rec["entities"].items():
            true_roles, pred_roles = [], []
            for ev in chain:
                ci = ev["clause"]
                sent, scores, argmax_i = clause_infer[ci]
                tok_i = match_mention_to_token(sent, ev["mention"], used_per_clause[ci])
                if tok_i is not None:
                    used_per_clause[ci].add(tok_i)
                    pred_role = "agent" if (argmax_i is not None and tok_i == argmax_i) else "patient"
                else:
                    pred_role = "patient"
                true_roles.append(ev["role"])
                pred_roles.append(pred_role)
            entities_out.append({
                "key": f"{rec['passage_id']}::{name}", "true_roles": true_roles, "pred_roles": pred_roles,
                "n_events": len(true_roles), "multi_event": len(true_roles) >= 2,
            })
    return entities_out


def build_entity_chains(passages, model, restrict_n=None):
    if restrict_n is not None:
        passages = passages[:restrict_n]

    entities_out = []
    clause_dump = []
    n_matched = 0
    n_total_events = 0
    pred_role_counts = {}

    for rec in passages:
        pid = rec["passage_id"]
        clauses = rec["clauses"]
        clause_infer = [stage1_predict_clause_v2(c, model) for c in clauses]
        for ci, (sent, preds) in enumerate(clause_infer):
            clause_dump.append({
                "passage_id": pid, "clause_idx": ci, "text": clauses[ci],
                "n_mentions": len(sent["mention_idx"]),
                "mention_role_preds": {sent["tokens"][i]: r for i, r in preds.items()},
            })

        used_per_clause = [set() for _ in clauses]
        for name, chain in rec["entities"].items():
            true_roles, pred_roles, match_ok = [], [], []
            for ev in chain:
                ci = ev["clause"]
                sent, preds = clause_infer[ci]
                tok_i = match_mention_to_token(sent, ev["mention"], used_per_clause[ci])
                n_total_events += 1
                if tok_i is not None:
                    used_per_clause[ci].add(tok_i)
                    n_matched += 1
                    raw_pred = preds.get(tok_i, "none")
                    # NEW model predicts {agent,patient,addressee,none}; "none" (no reachable role
                    # signal) falls back to "patient", the SAME honest fallback convention v1 used
                    # for its own binary non-agent default (documented, not silently forced).
                    pred_role = raw_pred if raw_pred != "none" else "patient"
                    pred_role_counts[pred_role] = pred_role_counts.get(pred_role, 0) + 1
                    match_ok.append(True)
                else:
                    pred_role = "patient"
                    match_ok.append(False)
                true_roles.append(ev["role"])
                pred_roles.append(pred_role)
            entities_out.append({
                "key": f"{pid}::{name}", "passage_id": pid, "name": name,
                "true_roles": true_roles, "pred_roles": pred_roles, "match_ok": match_ok,
                "n_events": len(true_roles), "multi_event": len(true_roles) >= 2,
            })

    diag = {
        "n_entity_events_total": n_total_events, "n_mention_matched": n_matched,
        "mention_match_rate": (n_matched / n_total_events) if n_total_events else None,
        "pred_role_counts": pred_role_counts,
    }
    return entities_out, clause_dump, diag


def run_all(mode, restrict_n=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    t0 = time.perf_counter()

    print("[%s] fitting STAGE-1 FIXED multi-role extraction model (full construction distribution) ..."
          % mode, flush=True)
    model = fit_new_production_extraction_model()
    print("[%s] STAGE-1 model fit on %d sentences" % (mode, model["n_train_sentences"]), flush=True)

    print("[%s] fitting OLD frozen binary model (for apples-to-apples same-gold comparison) ..." % mode,
          flush=True)
    old_model = fit_old_model()

    passages = load_multiclause_gold(GOLD_MULTICLAUSE)
    print("[%s] loaded %d multiclause passages" % (mode, len(passages)), flush=True)

    entities, clause_dump, extraction_diag = build_entity_chains(passages, model, restrict_n=restrict_n)
    entities_old = build_entity_chains_old(passages, old_model, restrict_n=restrict_n)
    census = role_census(entities)
    print("[%s] role census: %s" % (mode, census["counts"]), flush=True)
    print("[%s] extraction diag: %s" % (mode, extraction_diag), flush=True)

    max_chain = max((e["n_events"] for e in entities), default=0)
    assert max_chain <= MAX_EVENT_SLOTS, (
        f"gold chain length {max_chain} exceeds declared MAX_EVENT_SLOTS={MAX_EVENT_SLOTS}"
    )

    seed = 20260802
    rng = np.random.default_rng(seed)
    rng_floor = np.random.default_rng(seed + 999)
    d = 1024
    role_vecs = {r: unit_phase_vec(rng, d) for r in ROLE_VOCAB}
    idx_vecs = [unit_phase_vec(rng, d) for _ in range(MAX_EVENT_SLOTS)]

    def run_arm(arm_name, tick):
        key = ckpt.unit_key(mode, arm_name)
        if key not in ckpt.completed_units(OUTPUT_DIR):
            reg_bytes = []
            per_entity = []
            src_entities = entities_old if arm_name == "real_old_v2gold" else entities
            for e in src_entities:
                if arm_name == "oracle":
                    reg = build_register(e["true_roles"], role_vecs, idx_vecs)
                elif arm_name in ("real", "real_old_v2gold"):
                    reg = build_register(e["pred_roles"], role_vecs, idx_vecs)
                else:
                    reg = unit_phase_vec(rng_floor, d)
                correct = score_entity(reg, e["true_roles"], idx_vecs, role_vecs)
                reg_bytes.append(reg.tobytes())
                per_entity.append({"key": e["key"], "n_events": e["n_events"], "multi_event": e["multi_event"],
                                   "correct": correct, "recall": float(np.mean(correct))})
            result = {"per_entity": per_entity, "reg_digest": hashlib.sha256(b"".join(reg_bytes)).hexdigest()}
            ckpt.record_unit(OUTPUT_DIR, key, result)
            multi = [r["recall"] for r in per_entity if r["multi_event"]]
            print("[%s] arm=%s multi_event_recall=%.4f (n=%d)"
                  % (mode, arm_name, float(np.mean(multi)) if multi else -1.0, len(multi)), flush=True)

    for i, arm in enumerate(["oracle", "real", "floor", "real_old_v2gold"]):
        run_arm(arm, i)

    units = {k.split("|")[-1]: v for k, v in ckpt.load_units(OUTPUT_DIR).items() if k.startswith(mode + "|")}
    elapsed = time.perf_counter() - t0
    return units, entities, clause_dump, extraction_diag, census, elapsed


def _arms_must_differ(units):
    digs = {name: u["reg_digest"] for name, u in units.items()}
    names = sorted(digs)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digs[a] != digs[b], f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} bit-identical registers"


def _agg_multi(unit):
    vals = [e["recall"] for e in unit["per_entity"] if e["multi_event"]]
    return {"mean": float(np.mean(vals)) if vals else None, "n_entities": len(vals)}


def decide_verdict(units, census):
    oracle_multi = _agg_multi(units["oracle"])
    real_multi = _agg_multi(units["real"])
    floor_multi = _agg_multi(units["floor"])
    real_old_multi = _agg_multi(units["real_old_v2gold"])

    oracle_ok = (oracle_multi["mean"] is not None
                 and abs(oracle_multi["mean"] - ORACLE_REPRO_TARGET) <= ORACLE_REPRO_TOL)
    floor_ok = floor_multi["mean"] is not None and floor_multi["mean"] <= FLOOR_MAX

    rm = real_multi["mean"] or 0.0
    fm = floor_multi["mean"] or 0.0
    rom = real_old_multi["mean"] or 0.0
    # ONE-VARIABLE claim uses the SAME-GOLD (v2, powered) OLD-vs-NEW comparison (rom), not the
    # cross-gold-set atom-29610-cited number (V1_REAL_BASELINE, measured on the smaller v1 gold);
    # V1_REAL_BASELINE is still reported for continuity with the director's diagnosis atom.
    beats_v1 = rm >= (V1_REAL_BASELINE + V2_MUST_BEAT_V1_MARGIN)
    beats_old_same_gold = rm >= (rom + V2_MUST_BEAT_V1_MARGIN)

    summary = {
        "oracle_multi_event_recall": oracle_multi["mean"], "oracle_n_entities": oracle_multi["n_entities"],
        "real_multi_event_recall": real_multi["mean"], "real_n_entities": real_multi["n_entities"],
        "floor_multi_event_recall": floor_multi["mean"], "floor_n_entities": floor_multi["n_entities"],
        "real_old_v2gold_multi_event_recall": real_old_multi["mean"],
        "real_old_v2gold_n_entities": real_old_multi["n_entities"],
        "oracle_reproduces_36ab29a93": bool(oracle_ok), "floor_at_chance": bool(floor_ok),
        "oracle_to_real_drop": (oracle_multi["mean"] - real_multi["mean"])
                                if (oracle_multi["mean"] is not None and real_multi["mean"] is not None) else None,
        "v1_real_baseline_smaller_gold": V1_REAL_BASELINE, "v2_beats_v1_cited_baseline": bool(beats_v1),
        "v2_minus_v1_cited": rm - V1_REAL_BASELINE,
        "beats_old_same_v2_gold": bool(beats_old_same_gold),
        "v2_minus_old_same_gold": rm - rom,
        "role_census": census,
    }

    if not oracle_ok:
        return "HARD_FAIL_MISWIRED_ORACLE_DOES_NOT_REPRODUCE", summary
    if not floor_ok:
        return "HARD_FAIL_CANFAIL_VIOLATION_FLOOR_NOT_AT_CHANCE", summary

    # PRIMARY gate = beats_old_same_gold (the true one-variable comparison, same v2 gold, extraction
    # is the only thing that changed). beats_v1 (cross-gold-set, cited atom 29610 number) reported
    # for continuity but is NOT the primary pass/fail signal.
    if rm >= REAL_HARD_PASS_MIN and rm > fm + 0.20 and beats_old_same_gold:
        return "HARD_PASS_V2_REAL_EXTRACTION_TRACKS_ENTITIES_AND_BEATS_OLD_SAME_GOLD", summary
    if beats_old_same_gold and rm >= REAL_MIDDLE_MIN:
        return "MIDDLE_BAND_V2_BEATS_OLD_SAME_GOLD_BUT_BELOW_HARD_PASS", summary
    if beats_old_same_gold:
        return "PARTIAL_V2_BEATS_OLD_SAME_GOLD_STILL_NEAR_FLOOR", summary
    if rm <= fm + 0.10:
        return "HARD_FAIL_V2_REAL_EXTRACTION_NO_BETTER_THAN_FLOOR", summary
    return "HARD_FAIL_V2_DID_NOT_BEAT_OLD_SAME_GOLD", summary


def _write_metrics(verdict, summary, units, entities, clause_dump, extraction_diag, elapsed, mode):
    combined = {}
    for arm in ("oracle", "real", "floor", "real_old_v2gold"):
        for e in units[arm]["per_entity"]:
            combined.setdefault(e["key"], {"key": e["key"], "n_events": e["n_events"], "multi_event": e["multi_event"]})
            combined[e["key"]][arm + "_recall"] = e["recall"]
            combined[e["key"]][arm + "_correct"] = e["correct"]
    entity_true_pred = {e["key"]: {"true_roles": e["true_roles"], "pred_roles": e["pred_roles"],
                                    "match_ok": e["match_ok"]} for e in entities}
    for key, row in combined.items():
        row.update(entity_true_pred.get(key, {}))
    per_entity_dump = list(combined.values())

    metrics = {
        "anchor": ANCHOR_NAME, "mode": mode, "verdict": verdict,
        "verdict_msg": (
            "%s | ORACLE recall=%.4f (n=%d) | REAL(NEW) recall=%.4f (n=%d) | "
            "REAL(OLD,same v2 gold) recall=%.4f (n=%d) | FLOOR recall=%.4f (n=%d) | "
            "v1_cited_baseline(smaller gold)=%.4f | unreachable_role_fraction=%.4f"
            % (verdict, summary["oracle_multi_event_recall"] or -1, summary["oracle_n_entities"],
               summary["real_multi_event_recall"] or -1, summary["real_n_entities"],
               summary["real_old_v2gold_multi_event_recall"] or -1, summary["real_old_v2gold_n_entities"],
               summary["floor_multi_event_recall"] or -1, summary["floor_n_entities"],
               summary["v1_real_baseline_smaller_gold"],
               summary["role_census"]["unreachable_fraction"] or -1)
        ),
        "summary": summary,
        "bands": {"ORACLE_REPRO_TARGET": ORACLE_REPRO_TARGET, "ORACLE_REPRO_TOL": ORACLE_REPRO_TOL,
                  "FLOOR_MAX": FLOOR_MAX, "REAL_HARD_PASS_MIN": REAL_HARD_PASS_MIN,
                  "REAL_MIDDLE_MIN": REAL_MIDDLE_MIN, "V1_REAL_BASELINE": V1_REAL_BASELINE,
                  "V2_MUST_BEAT_V1_MARGIN": V2_MUST_BEAT_V1_MARGIN},
        "per_arm": units,
        "extraction_diag": extraction_diag,
        "per_entity_dump": per_entity_dump,
        "clause_dump": clause_dump,
        "role_vocab": ROLE_VOCAB,
        "new_extraction_role_vocab": ROLE_VOCAB4,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "defensive_error_checking": "passed_all_4_patterns_heartbeat_exempt_lt30s",
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--timeout", type=float, default=180.0,
                    help="formula self-test timeout budget (declared; this cell runs in <60s)")
    args = ap.parse_args()
    if not args.self_test and not args.full:
        args.self_test = True
    mode = "self_test" if args.self_test else "full"

    _write_start_marker(OUTPUT_DIR, mode, expected_n_units=3)

    rng = np.random.default_rng(20260802)
    run_self_test(rng)

    print("[%s] starting %s" % (mode, ANCHOR_NAME), flush=True)
    try:
        restrict_n = 2 if mode == "self_test" else None
        units, entities, clause_dump, extraction_diag, census, elapsed = run_all(mode, restrict_n=restrict_n)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("[%s] FATAL: %s\n%s" % (mode, e, traceback.format_exc()), flush=True)
        _write_crash_metrics(OUTPUT_DIR, e)
        raise SystemExit(2)

    _arms_must_differ(units)
    verdict, summary = decide_verdict(units, census)
    metrics = _write_metrics(verdict, summary, units, entities, clause_dump, extraction_diag, elapsed, mode)
    print("[%s] VERDICT: %s" % (mode, verdict), flush=True)
    print("[%s] %s" % (mode, metrics["verdict_msg"]), flush=True)
    print("[%s] elapsed=%.1fs" % (mode, elapsed), flush=True)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
