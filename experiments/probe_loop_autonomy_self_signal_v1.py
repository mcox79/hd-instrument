"""PROBE (aim-probe, NOT a dispatched cell): loop-AUTONOMY self-signal feasibility (2026-08-02).

QUESTION: the self-improving-reader loop is engine-certified (atoms 29624) but every fix decision
so far has been DIRECTOR-dispatched (a human/agent reads the metrics and decides keep/revert).
Autonomy requires: when the reader flags an error and applies a candidate fix, can it decide
WITHOUT gold whether the fix helped (keep) or hurt (revert)?

THE LABELED SET (reconstructed here, not hand-curated): cycles 2-3 already produced fix-induced
per-decision changes with a known correct/incorrect label via the clean MUC-style link label
(mention_link_wrong, commit e6a3a9ee8-family). Three fixes, all built as opt-in filters on top of
strict_cb (commit 5b266248f, imported verbatim, NEVER mutated):
  - principle_b (4cc041fcd): fired 9x, changed 2 decisions, corrected=1 broken=0.
  - speaker_deixis (0c4285f52): fired 3x, changed 3 decisions, corrected=2 broken=0.
  - decay_window (0c4285f52): changed 26 decisions, corrected=3 broken=6 (the crucial negatives).

THE PROBE: for every fix-induced decision CHANGE with a non-neutral label (corrected xor broken),
compute THREE gold-free self-signals for the PRE-fix pick vs the POST-fix pick and test whether
their deltas separate corrected changes from broken changes:
  (a) n_compatible delta: ambiguity of the candidate pool before vs after the fix's own filter.
  (b) decay-margin delta: recency-decayed salience margin (top candidate vs runner-up) under a
      generic window-salience score (DECAY/WINDOW from the cross_clause_discourse cell), computed
      over whatever candidate pool each arm's own mechanism actually used for its pick. This is a
      confidence-margin proxy available regardless of which specific filter produced the pick.
  (c) coherence-margin delta: hdlab.situation_model_accumulate.AccumulateRegister role-decode
      margin (top1-top2 over ROLE_VOCAB) for the picked entity's register at the mention's own
      event slot, built from that arm's FULL passage-level cluster assignment (same generator
      seed pre/post so the FHRR role/idx vocab is identical -- only the cluster assignment moves).

FIDELITY: every replay function below is a traced, byte-for-byte reproduction of the corresponding
committed pick logic (run_learnable_strict_cb / run_loop_principle_b / run_loop_discourse), each
asserted (self_test) to produce IDENTICAL predicted-id sequences to the imported originals before
any signal is trusted -- same discipline as exp_coref_self_confidence_calibration_v1.py's
instrumented-copy VET.

HONEST BARS (pre-declared): if a gold-free signal (or the combined signal) clearly separates good
from bad changes -- AUC >= 0.70, OR a simple positive/negative delta rule cleanly rejects >= 5/6 of
decay_window's breaks while keeping the 6 known corrections -- => AUTONOMY FEASIBLE, recommend
building the self-gated router. If signals are ~chance => the self-signal is INSUFFICIENT on this
content, consistent with the prior self-correct-null finding on simple McGuffey => recommend
REDIRECT (richer/longer content before autonomy). N is SMALL (12 labeled instances) -- this aims
the build, it does not settle it; report accordingly.

Not a dispatched experiment: single local run, no pre-reg/queue_add, per director task contract.
Self-test: python probe_loop_autonomy_self_signal_v1.py --self-test
Full:      python probe_loop_autonomy_self_signal_v1.py
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))

import torch  # noqa: E402

from exp_earn_coref_match_or_allocate_v1 import gn_compatible, normalize_tokens  # noqa: E402
from exp_earn_coref_pronoun_strict_cb_v1 import (  # noqa: E402
    _EntityCb, _pick_strict_cb, _resolve_name_branch,
    run_learnable_strict_cb,
)
from exp_coref_flag_fix_loop_principle_b_v1 import (  # noqa: E402
    _principle_b_filter, run_loop_principle_b,
)
from exp_coref_loop_cross_clause_discourse_v1 import (  # noqa: E402
    enrich_dialogue, _deixis_filter, run_loop_discourse, DECAY, WINDOW,
    load_passages, GOLD_PATH_COMBINED,
)
from exp_wire_coref_accumulate_situation_model_v1 import (  # noqa: E402
    build_mention_stream_with_role, event_slots_for, ROLE_VOCAB, D, MAX_EVENT_SLOTS, SEED,
)
from exp_coref_self_confidence_calibration_v1 import mention_link_wrong, auc_from_scores  # noqa: E402
from hdlab.situation_model_accumulate import AccumulateRegister  # noqa: E402

ANCHOR_NAME = "probe_loop_autonomy_self_signal_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
NOTES_PATH = os.path.join(REPO_ROOT, "notes",
                           "probe_loop_autonomy_self_signal_feasibility_2026-08-02.md")

FEASIBLE_AUC = 0.70
FEASIBLE_REJECT_FRAC = 5.0 / 6.0  # >=5/6 decay breaks rejected while keeping all 6 corrections


# ---------------------------------------------------------------------------
# Generic recency-decayed salience score (identical formula to
# exp_coref_loop_cross_clause_discourse_v1._pick_decay_window, reused as a MECHANISM-AGNOSTIC
# confidence proxy: it is computed on whatever pool an arm's own filter left it with).
# ---------------------------------------------------------------------------
def _decay_scores(compat: List[_EntityCb], cur_clause: int, decay: float = DECAY,
                   window: int = WINDOW) -> List[Tuple[_EntityCb, float]]:
    out = []
    for e in compat:
        s = sum(decay ** (cur_clause - c) for c in e.clause_role
                if 0 < (cur_clause - c) <= window)
        out.append((e, s))
    return out


def _margin_from_scores(scored: List[Tuple[_EntityCb, float]]) -> float:
    vals = sorted((s for _, s in scored), reverse=True)
    if not vals:
        return 0.0
    if len(vals) == 1:
        return vals[0]
    return vals[0] - vals[1]


def _update_entity(best: _EntityCb, pos: int, cur_clause: int, cur_role: Optional[str]) -> None:
    best.count += 1
    best.last_pos = pos
    if cur_role is not None:
        best.clause_role[cur_clause] = cur_role


def _name_branch_step(entities: List[_EntityCb], next_id: int, rec: dict, pos: int,
                       cur_clause: int) -> int:
    gender, number = rec["gender"], rec["number"]
    toks = normalize_tokens(rec["mention_text"])
    first_word = rec["mention_text"].strip().split()[0].lower().strip(".,'\"") \
        if rec["mention_text"].strip() else ""
    has_determiner = rec.get("has_determiner", first_word in {"the", "a", "an"})
    best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks, has_determiner)
    best.tokens |= toks
    if best.gender is None and gender is not None:
        best.gender = gender
    if best.number is None and number is not None:
        best.number = number
    _update_entity(best, pos, cur_clause, rec.get("role"))
    return next_id


# ---------------------------------------------------------------------------
# Traced replays -- each byte-faithful to its committed original (VET'd in self_test below).
# ---------------------------------------------------------------------------
def replay_strict_cb_traced(stream: List[dict]) -> Tuple[List[int], Dict[int, dict]]:
    entities: List[_EntityCb] = []
    next_id = 0
    assigned: List[int] = []
    traces: Dict[int, dict] = {}
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause = rec["clause"]
        cur_role = rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            n_before = len(compat)
            dm = _margin_from_scores(_decay_scores(compat, cur_clause))
            if compat:
                best = _pick_strict_cb(compat, cur_clause)
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)
            else:
                best = _EntityCb(next_id)
                next_id += 1
                entities.append(best)
            traces[pos] = {"n_compat": n_before, "n_compat_after": n_before, "decay_margin": dm}
            _update_entity(best, pos, cur_clause, cur_role)
            assigned.append(best.eid)
            continue
        toks = normalize_tokens(rec["mention_text"])
        first_word = rec["mention_text"].strip().split()[0].lower().strip(".,'\"") \
            if rec["mention_text"].strip() else ""
        has_determiner = rec.get("has_determiner", first_word in {"the", "a", "an"})
        best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks, has_determiner)
        best.tokens |= toks
        if best.gender is None and gender is not None:
            best.gender = gender
        if best.number is None and number is not None:
            best.number = number
        _update_entity(best, pos, cur_clause, cur_role)
        assigned.append(best.eid)
    return assigned, traces


def replay_principle_b_traced(stream: List[dict]) -> Tuple[List[int], Dict[int, dict]]:
    entities: List[_EntityCb] = []
    next_id = 0
    assigned: List[int] = []
    traces: Dict[int, dict] = {}
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause = rec["clause"]
        cur_role = rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            n_before = len(compat)
            if compat:
                filtered, action = _principle_b_filter(compat, cur_clause, cur_role)
                best = _pick_strict_cb(filtered, cur_clause)
                pool = filtered
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)
                pool = []
            else:
                best = _EntityCb(next_id)
                next_id += 1
                entities.append(best)
                pool = []
            dm = _margin_from_scores(_decay_scores(pool, cur_clause))
            traces[pos] = {"n_compat": n_before, "n_compat_after": len(pool), "decay_margin": dm}
            _update_entity(best, pos, cur_clause, cur_role)
            assigned.append(best.eid)
            continue
        toks = normalize_tokens(rec["mention_text"])
        first_word = rec["mention_text"].strip().split()[0].lower().strip(".,'\"") \
            if rec["mention_text"].strip() else ""
        has_determiner = rec.get("has_determiner", first_word in {"the", "a", "an"})
        best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks, has_determiner)
        best.tokens |= toks
        if best.gender is None and gender is not None:
            best.gender = gender
        if best.number is None and number is not None:
            best.number = number
        _update_entity(best, pos, cur_clause, cur_role)
        assigned.append(best.eid)
    return assigned, traces


def replay_discourse_traced(stream: List[dict], use_decay: bool, use_deixis: bool
                             ) -> Tuple[List[int], Dict[int, dict]]:
    entities: List[_EntityCb] = []
    next_id = 0
    assigned: List[int] = []
    traces: Dict[int, dict] = {}
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause = rec["clause"]
        cur_role = rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            n_before = len(compat)
            if compat:
                pool = compat
                if use_deixis:
                    pool, _fired = _deixis_filter(pool, rec)
                scored = _decay_scores(pool, cur_clause)
                best = None
                if use_decay:
                    # tie-break replicated EXACTLY from _pick_decay_window: on a score tie the
                    # entity with the LARGER last_pos (more recent) wins, not list order.
                    best_score = 0.0
                    for e, score in scored:
                        if score > 0.0 and (best is None or score > best_score
                                            or (score == best_score and e.last_pos > best.last_pos)):
                            best = e
                            best_score = score
                if best is None:
                    best = _pick_strict_cb(pool, cur_clause)
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)
                pool = []
                scored = []
            else:
                best = _EntityCb(next_id)
                next_id += 1
                entities.append(best)
                pool = []
                scored = []
            dm = _margin_from_scores(scored)
            traces[pos] = {"n_compat": n_before, "n_compat_after": len(pool), "decay_margin": dm}
            _update_entity(best, pos, cur_clause, cur_role)
            assigned.append(best.eid)
            continue
        toks = normalize_tokens(rec["mention_text"])
        first_word = rec["mention_text"].strip().split()[0].lower().strip(".,'\"") \
            if rec["mention_text"].strip() else ""
        has_determiner = rec.get("has_determiner", first_word in {"the", "a", "an"})
        best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks, has_determiner)
        best.tokens |= toks
        if best.gender is None and gender is not None:
            best.gender = gender
        if best.number is None and number is not None:
            best.number = number
        _update_entity(best, pos, cur_clause, cur_role)
        assigned.append(best.eid)
    return assigned, traces


# ---------------------------------------------------------------------------
# Coherence proxy: AccumulateRegister role-decode margin (top1-top2 over ROLE_VOCAB) for the
# WHOLE passage under one arm's cluster assignment, same generator seed across arms so only the
# cluster assignment (not the random FHRR vocab) differs pre vs post.
# ---------------------------------------------------------------------------
def decode_margins_for_arm(stream: List[dict], cluster_ids: List[str], seed: int) -> List[float]:
    event_slots, _n_slots, _c2s = event_slots_for(stream)
    gen = torch.Generator().manual_seed(seed)
    reg = AccumulateRegister(ROLE_VOCAB, D, gen, max_event_slots=MAX_EVENT_SLOTS)
    for rec, cid, slot in zip(stream, cluster_ids, event_slots):
        reg.add_event(cid, rec["role"], slot)
    margins = []
    for rec, cid, slot in zip(stream, cluster_ids, event_slots):
        _pred, scores = reg.decode(cid, slot)
        vals = sorted(scores.values(), reverse=True)
        margins.append(vals[0] - vals[1] if len(vals) > 1 else vals[0])
    return margins


# ---------------------------------------------------------------------------
MECHS = ("principle_b", "decay_window", "speaker_deixis")


def _pre_post_for(mech: str, p_idx: int, passage: dict) -> Tuple[List[dict], List[int], Dict[int, dict],
                                                                   List[int], Dict[int, dict]]:
    """Returns (stream, pre_pred, pre_trace, post_pred, post_trace) for one mechanism/passage."""
    if mech == "principle_b":
        stream = build_mention_stream_with_role(passage)
        pre_pred, pre_trace = replay_strict_cb_traced(stream)
        post_pred, post_trace = replay_principle_b_traced(stream)
    elif mech == "decay_window":
        stream = enrich_dialogue(passage, build_mention_stream_with_role(passage))
        pre_pred, pre_trace = replay_strict_cb_traced(stream)
        post_pred, post_trace = replay_discourse_traced(stream, use_decay=True, use_deixis=False)
    elif mech == "speaker_deixis":
        stream = enrich_dialogue(passage, build_mention_stream_with_role(passage))
        pre_pred, pre_trace = replay_strict_cb_traced(stream)
        post_pred, post_trace = replay_discourse_traced(stream, use_decay=False, use_deixis=True)
    else:
        raise ValueError(mech)
    return stream, pre_pred, pre_trace, post_pred, post_trace


def run_probe(passages: List[dict]) -> dict:
    instances = []
    fidelity = {}
    for mech in MECHS:
        n_fid_checked = 0
        for p_idx, p in enumerate(passages):
            stream, pre_pred, pre_trace, post_pred, post_trace = _pre_post_for(mech, p_idx, p)

            # ---- FIDELITY: traced replay must byte-match the committed original ----
            if mech == "principle_b":
                ref_pre = run_learnable_strict_cb(stream)
                ref_post = run_loop_principle_b(stream)[0]
            elif mech == "decay_window":
                ref_pre = run_learnable_strict_cb(stream)
                ref_post = run_loop_discourse(stream, use_decay=True, use_deixis=False)[0]
            else:
                ref_pre = run_learnable_strict_cb(stream)
                ref_post = run_loop_discourse(stream, use_decay=False, use_deixis=True)[0]
            assert pre_pred == ref_pre, f"{mech}/{p['passage_id']}: pre replay drift"
            assert post_pred == ref_post, f"{mech}/{p['passage_id']}: post replay drift"
            n_fid_checked += 1

            pre_cids = [str(c) for c in pre_pred]
            post_cids = [str(c) for c in post_pred]
            seed = SEED + p_idx * 100
            pre_dm = decode_margins_for_arm(stream, pre_cids, seed)
            post_dm = decode_margins_for_arm(stream, post_cids, seed)

            for pos, rec in enumerate(stream):
                if not rec["is_pronoun"] or pre_pred[pos] == post_pred[pos]:
                    continue
                pre_wrong = mention_link_wrong(pos, stream, pre_pred)
                post_wrong = mention_link_wrong(pos, stream, post_pred)
                if pre_wrong and not post_wrong:
                    label = "corrected"
                elif post_wrong and not pre_wrong:
                    label = "broken"
                else:
                    label = "neutral"
                pt, qt = pre_trace[pos], post_trace[pos]
                instances.append({
                    "mech": mech, "passage_id": p["passage_id"], "pos": pos,
                    "mention_text": rec["mention_text"], "gold_entity": rec["gold_entity"],
                    "label": label,
                    "n_compat_pre": pt["n_compat_after"], "n_compat_post": qt["n_compat_after"],
                    "n_compat_delta": pt["n_compat_after"] - qt["n_compat_after"],
                    "decay_margin_pre": pt["decay_margin"], "decay_margin_post": qt["decay_margin"],
                    "decay_margin_delta": qt["decay_margin"] - pt["decay_margin"],
                    "coherence_margin_pre": pre_dm[pos], "coherence_margin_post": post_dm[pos],
                    "coherence_margin_delta": post_dm[pos] - pre_dm[pos],
                })
        fidelity[mech] = {"n_passages_checked": n_fid_checked, "byte_identical": True}

    labeled = [i for i in instances if i["label"] in ("corrected", "broken")]
    labels = [1 if i["label"] == "corrected" else 0 for i in labeled]

    def _auc_for(field: str) -> Optional[float]:
        scores = [i[field] for i in labeled]
        return auc_from_scores(scores, labels)

    signal_fields = ["n_compat_delta", "decay_margin_delta", "coherence_margin_delta"]
    aucs = {f: _auc_for(f) for f in signal_fields}

    # combined signal: mean of the two continuous margins (n_compat_delta is integer/coarse and
    # only fires for principle_b/speaker_deixis by construction -- decay_window's pool never
    # shrinks, so n_compat_delta==0 for ALL decay_window instances; keep it as its own reported
    # signal but exclude it from the combined score so it cannot silently zero out decay_window).
    for i in labeled:
        i["combined_margin_delta"] = i["decay_margin_delta"] + i["coherence_margin_delta"]
    aucs["combined_margin_delta"] = _auc_for("combined_margin_delta")

    # ---- keep/revert rule check: threshold at 0 on the combined signal ----
    def _keep_revert_table(field: str) -> dict:
        tp = fp = tn = fn = 0
        for i in labeled:
            predicted_keep = i[field] > 0.0
            actually_good = i["label"] == "corrected"
            if predicted_keep and actually_good:
                tp += 1
            elif predicted_keep and not actually_good:
                fp += 1
            elif not predicted_keep and not actually_good:
                tn += 1
            else:
                fn += 1
        return {"kept_and_good": tp, "kept_but_bad_FALSE_KEEP": fp,
                "reverted_and_bad_correct_reject": tn, "reverted_but_good_FALSE_REJECT": fn}

    keep_revert = {f: _keep_revert_table(f) for f in signal_fields + ["combined_margin_delta"]}

    decay_broken = [i for i in labeled if i["mech"] == "decay_window" and i["label"] == "broken"]
    all_corrected = [i for i in labeled if i["label"] == "corrected"]
    decay_reject_frac = {}
    corrections_keep_frac = {}
    for f in signal_fields + ["combined_margin_delta"]:
        n_rej = sum(1 for i in decay_broken if i[f] <= 0.0)
        decay_reject_frac[f] = {"rejected": n_rej, "total": len(decay_broken),
                                 "frac": (n_rej / len(decay_broken)) if decay_broken else None}
        n_keep = sum(1 for i in all_corrected if i[f] > 0.0)
        corrections_keep_frac[f] = {"kept": n_keep, "total": len(all_corrected),
                                     "frac": (n_keep / len(all_corrected)) if all_corrected else None}

    return {
        "n_instances_total_changed": len(instances),
        "n_instances_labeled": len(labeled),
        "n_corrected": sum(1 for l in labels if l == 1),
        "n_broken": sum(1 for l in labels if l == 0),
        "instances": instances,
        "aucs": aucs,
        "keep_revert_confusion": keep_revert,
        "decay_window_reject_fraction_per_signal": decay_reject_frac,
        "all_corrections_keep_fraction_per_signal": corrections_keep_frac,
        "fidelity": fidelity,
    }


# ---------------------------------------------------------------------------
def self_test() -> None:
    assert os.path.exists(GOLD_PATH_COMBINED), f"combined gold missing: {GOLD_PATH_COMBINED}"
    passages = load_passages(GOLD_PATH_COMBINED)
    assert len(passages) == 36, f"expected 36 passages, got {len(passages)}"

    # real-code-path fidelity check on a small slice (fast) before trusting the full-gold run.
    small = passages[:6]
    res = run_probe(small)
    assert "instances" in res
    for mech, fid in res["fidelity"].items():
        assert fid["byte_identical"], f"{mech} replay drifted from committed original"
    print(f"[SELF-TEST] PASS: traced replays byte-identical to committed originals on "
          f"{len(small)}-passage slice for all 3 mechanisms; {res['n_instances_labeled']} "
          f"labeled instances found in slice; probe machinery (n_compat/decay-margin/coherence-"
          f"margin deltas + AUC + keep-revert table) exercised on the real code path.")


# ---------------------------------------------------------------------------
def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def main() -> None:
    t0 = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    passages = load_passages(GOLD_PATH_COMBINED)
    result = run_probe(passages)

    combined_auc = result["aucs"]["combined_margin_delta"]
    decay_reject = result["decay_window_reject_fraction_per_signal"]["combined_margin_delta"]["frac"]
    corr_keep = result["all_corrections_keep_fraction_per_signal"]["combined_margin_delta"]["frac"]

    feasible = (
        (combined_auc is not None and combined_auc >= FEASIBLE_AUC)
        or (decay_reject is not None and corr_keep is not None
            and decay_reject >= FEASIBLE_REJECT_FRAC and corr_keep >= 0.99)
    )
    verdict = "AUTONOMY_FEASIBLE_PROBE" if feasible else "REDIRECT_INSUFFICIENT_SIGNAL_PROBE"

    verdict_msg = (
        f"[{verdict}] N_labeled={result['n_instances_labeled']} "
        f"(corrected={result['n_corrected']}, broken={result['n_broken']}). "
        f"AUCs: n_compat_delta={result['aucs']['n_compat_delta']}, "
        f"decay_margin_delta={result['aucs']['decay_margin_delta']}, "
        f"coherence_margin_delta={result['aucs']['coherence_margin_delta']}, "
        f"combined={combined_auc}. decay_window break-reject frac (combined signal)="
        f"{decay_reject}, all-corrections keep frac (combined signal)={corr_keep}. "
        f"THIS IS A SMALL-N AIM PROBE, not a powered result."
    )

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict,
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "feasible_auc_bar": FEASIBLE_AUC,
        "feasible_reject_frac_bar": FEASIBLE_REJECT_FRAC,
        "result": result,
        "gold_path_combined": GOLD_PATH_COMBINED,
        "reproducibility_note": (
            "strict_cb (5b266248f), run_loop_principle_b (4cc041fcd), run_loop_discourse "
            "(0c4285f52), AccumulateRegister (hdlab/situation_model_accumulate.py) all imported "
            "or traced byte-for-byte and VET'd against the originals (see fidelity block); NEVER "
            "mutated. This is a lightweight ANALYSIS PROBE per director task contract -- not "
            "dispatched, no queue_add, no pre-reg SCHEMA-VET (no compute/GPU dispatch involved)."
        ),
        "prior_commits": {
            "strict_cb_mechanism": "5b266248f",
            "loop_cycle2_principle_b_partial": "4cc041fcd",
            "loop_cycle3_cross_clause_discourse": "0c4285f52",
            "loop_cycle3_atomize": "56cdfeaa8",
            "speaker_deixis_promoted_to_hdlab": "7bef6f740",
        },
    }
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    print(f"[{ANCHOR_NAME}] {verdict}")
    print(verdict_msg)
    print(f"metrics written to {final}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
        else:
            main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
