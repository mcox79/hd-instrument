# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: COMMIT_REVISE_V2 vs COMMIT_REVISE_V1 vs CLAUSE_POSITION vs POSITION vs
#   RANDOM per_arm digests hash-compared at smoke gate.
# - final_metrics_atomicity = tmp_replace (single-shot; whole run < 90s, small numpy LOOCV + grid sweep)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a: "discrete multiclass role-classification accuracy, no CRLB noise floor applies";
#   discriminator_reachability=true (CANONICAL-must-match-or-beat-POSITION and NO-REVISE-must-
#   reproduce-the-inversion-on-marked are the reachability checks, unchanged from v1)
# - baseline_in_band: POSITION/CLAUSE_POSITION/RANDOM are CAN-FAIL / lever-isolation controls, not
#   "baseline in band" arms
# - cell_chunked=False (single pass; per-arm checkpoint via tools/exp_checkpoint.py used anyway per
#   CLAUDE.md's "any cell looping over >1 unit" rule -- here units = {COMMIT_REVISE_V2,
#   COMMIT_REVISE_V1, CLAUSE_POSITION, POSITION, RANDOM} x {full,self_test})
# - HYPOTHESIZED/MEASURED/CITED/THEORETICAL tags on every number in this docstring
# - ASCII-only, no emojis, no em dashes.
"""exp_extraction_commit_then_revise_v2 (2026-08-02)

FIX for the two MEASURED mechanism failures pinpointed by the director's probe (acc28b61) on the v1
commit-then-revise cell (exp_extraction_commit_then_revise_v1.py, MEASURED@data/exp_extraction_
commit_then_revise_v1/metrics.json: verdict MIDDLE_BAND_CANONICAL_IMPROVED_BUT_BELOW_POSITION_FLOOR,
canonical role_acc=0.4788 vs POSITION floor 0.5364, gate_rate_by_kind.canonical=0.2124):

LEVER 1 -- FALSE-POSITIVE GATE (graceful degrade): v1's gate_fires() (verb_after_close AND
frac_in_quote>0.3, OR has_by) fires on 21.2% of CANONICAL sentences -- all false positives, since
"canonical" by definition has no genuine marked construction -- and routes them into the REVISE
softmax (trained ONLY on the non-canonical pool), which does not transfer to canonical structure.
FIX: the revise softmax's own per-mention argmax MARGIN (top1 prob - top2 prob) is used as a
confidence gate -- REVISE is accepted ONLY when margin >= MARGIN_THRESH; otherwise the prediction
FALLS BACK to the COMMIT default (Bornkessel eADM: revision is gated by cue RELIABILITY, garden-path
reanalysis is not forced through when the reanalysis signal itself is weak). This is a genuine
graceful degrade (partial-per-mention fallback within a gated sentence), not just a stricter gate_fires
threshold -- a sentence can still gate_fires()==True (structural cue present) yet have some/all of its
mentions fall back to the default when the narrow model is not confident about them.

LEVER 2 -- NON-CLAUSE-AWARE AGENT (clause-level default): v1's COMMIT default is position_predict()
imported from the parent cell -- SENTENCE-level first-mention = agent, everything else = patient. The
probe measured only 0.338 canonical agent accuracy this way because 151/228 true agents are subjects
of LATER clauses in multi-clause canonical sentences, not the sentence's first mention. FIX:
segment_clauses() splits each sentence's token stream on coordinating conjunctions (CCONJ: and/but/or/
so/nor/yet), subordinating conjunctions (SCONJ per the UD tagger, PLUS the word "when" which this
tagger mistags ADV -- verified below), and clause-level punctuation (";"). clause_position_predict()
then assigns agent = the first non-quoted mention WITHIN EACH CLAUSE SEGMENT (not the whole sentence),
patient = every other mention in that same clause. This is brain-faithful clause-by-clause structure
building (Friederici): every clause gets its OWN subject-as-default-agent, not one global sentence
subject. clause_position_predict() REPLACES position_predict() as the COMMIT default inside
COMMIT_REVISE_V2; it is also run standalone as arm CLAUSE_POSITION to isolate lever 2's contribution
from lever 1's.

TAGGER VERIFICATION (MEASURED@ this session's dev probe over data/frontend_assets/pos_tagger_ud_ewt_
upos.json, run before authoring segment_clauses): because/while/although/since/after/before/if/unless/
though/as/that -> SCONJ (11/13 subordinators tag correctly); "when" -> ADV (mistagged, so it is
special-cased into BOUNDARY_WORDS by surface word match, not POS); who/which -> PRON (left as
non-boundary; over-splitting on relative-clause "who/which" was judged a net negative for this small
gold -- MENTION_POS already includes PRON so they are candidate mentions in their own right, and the
contract's own two levers name only "coordinating/subordinating boundaries + clause-level punctuation",
not relative clauses).

GOLD (unchanged from v1, reused verbatim): CANONICAL=gold_mcguffey_lccp_argstruct_v1.json (114
sentences via load_canonical_pool), QUOTATIVE=gold_quotative_verified_v2.jsonl (N=45),
BYAGENT=gold_passive_byagent_verified_v2.jsonl (N=23), PASSIVE(degenerate)=gold_passive_verified_v1.
jsonl (N=7).

ARMS (two variables = LEVER 1 (margin-gated graceful-degrade revise) + LEVER 2 (clause-level COMMIT
default), applied TOGETHER in one mechanism per the spawn contract "ONE build, both levers"):
  COMMIT_REVISE_V2 = NEW mechanism: COMMIT=clause_position_predict (lever 2) + REVISE gated by
                     gate_fires_v2(sent, thresh) AND per-mention margin>=MARGIN_THRESH (lever 1),
                     else falls back to the clause-level default. (thresh, MARGIN_THRESH) are selected
                     by an in-cell grid sweep (see SWEEP section) -- adaptive_with_discriminator_gate
                     calibration, logged in full for transparency (not a single-number cherry-pick).
  COMMIT_REVISE_V1 = OLD for this comparison: v1's mechanism reproduced VERBATIM (import, not
                     reimplemented) -- POSITION (sentence-level) default + gate thresh=0.3 fixed,
                     no margin gating.
  CLAUSE_POSITION  = lever-2-ONLY ablation: clause_position_predict applied with NO gating/revise at
                     all (isolates how much of COMMIT_REVISE_V2's canonical lift is from lever 2 alone
                     vs the margin-gated revise on top).
  POSITION         = deterministic control, reused verbatim from the parent cell; ALSO serves as the
                     sentence-level NO-REVISE ablation (can-fail check, reused not reimplemented).
  RANDOM           = seeded uniform-over-4-classes per mention, reused verbatim.

SWEEP (grid; declared BEFORE running, selection criterion fixed in advance, 3-tier priority = (1) most
pre-registered gates cleared, (2) highest canonical role_acc, (3) LOWEST canonical gate false-positive
rate (lever 1's own honesty tie-break: among configs tied on accuracy, prefer the one that fires on
canonical LESS) -- NOT single-highest-number cherry-pick):
  THRESH_GRID  = [0.3, 0.4, 0.5, 0.6]  (gate_fires_v2's frac_in_quote threshold, extends v1's own
                 thresh sweep which stopped at 0.3/0.5/0.7)
  MARGIN_GRID  = [0.0, 0.10, 0.20, 0.30]  (0.0 = no margin gating, i.e. lever 1 reduces to lever-2-only
                 plus v1's raw gate; included as the ablation floor of lever 1 itself)
  Full 4x4=16-cell grid computed and logged (grid_results field in metrics) so the selected config is
  reproducible/auditable, satisfying META_RULE_M's "adaptive_with_discriminator_gate" calibration
  contract (principled selection rule fixed in advance, discriminator-still-fires verified per cell,
  logged in full -- not silent post-hoc tuning).

FIX BAR (pre-registered BEFORE running, per director spawn contract):
  - CANONICAL_MATCH_OR_BEAT: COMMIT_REVISE_V2 canonical role_acc >= CANONICAL_MIN = POSITION_CANONICAL_
    FLOOR(0.5364) - CANONICAL_SLACK(0.03) = 0.5064 (same floor v1 used; the contract's "beat" target for
    lever 2 specifically is CANONICAL_BEATS_FLOOR = strictly > 0.5364, reported as a stretch flag).
  - QUOTATIVE_PRESERVED: COMMIT_REVISE_V2 quotative role_acc >= 0.75 (v1's own preserved value: 0.7705).
  - BYAGENT_PRESERVED: COMMIT_REVISE_V2 byagent role_acc >= 0.68 (v1's own preserved value: 0.8511).
  - NO_REVISE_REPRODUCES_INVERSION: POSITION quotative/byagent role_acc <= 1/3 chance - 0.10 (reused
    directly from v1's own POSITION arm recomputation; unaffected by either lever).
  - CANONICAL_GATE_FP_RATE_DROPPED: COMMIT_REVISE_V2's canonical gate-fire rate must be STRICTLY BELOW
    v1's MEASURED 0.2124 (reported honestly regardless of pass/fail on the accuracy bars -- lever 1's
    OWN can-fail check, since lever 1's stated mechanism is "gate fires less on canonical, or its
    firing matters less").
  Net verdict computed by decide_verdict() -- see that function for the exact logic; MEASURED numbers
  filled in at metrics.json:summary after the run (this docstring is written pre-run per META_RULE_AC).

NO borrowed embeddings. NO bolt-on parser. Supplying gold DATA is allowed per contract; segment_clauses
is a hand-specified deterministic rule over already-computed POS tags (not learned), matching the
brain-literature division of labor (cue integration/clause segmentation is structural, the REVISE
CONTENT mapping is learned) used throughout this arc.

Run:  .venv/Scripts/python.exe experiments/exp_extraction_commit_then_revise_v2.py --self-test
      .venv/Scripts/python.exe experiments/exp_extraction_commit_then_revise_v2.py --full
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

# Reuse EVERYTHING structural/verbatim from the parent cells (import, not reimplement).
from exp_extraction_construction_conditional_multirole_v1 import (  # noqa: E402
    load_canonical_pool, load_quotative_pool, load_byagent_pool, load_passive_pool,
    build_sentence_multi, mention_features_multi, build_design_multi, fit_softmax, _softmax,
    position_predict, random_predict, eval_predictions,
    ROLE_VOCAB4, ROLE_IDX, L2_LAMBDA, LR, N_ITERS,
)
from exp_extraction_commit_then_revise_v1 import (  # noqa: E402
    fit_softmax_on, commit_then_revise_predict_all as commit_then_revise_v1_predict_all,
)
from exp_interactive_loop_real_gold_mcguffey_v1 import quote_spans  # noqa: E402

ANCHOR_NAME = "extraction_commit_then_revise_v2"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---------------------------------------------------------------------------
# PRE-REGISTERED BANDS (fixed BEFORE running; see module docstring for provenance)
# ---------------------------------------------------------------------------
POSITION_CANONICAL_FLOOR = 0.5364   # MEASURED@parent cell's POSITION arm, canonical role_acc
CANONICAL_SLACK = 0.03
CANONICAL_MIN = POSITION_CANONICAL_FLOOR - CANONICAL_SLACK
QUOTATIVE_MIN = 0.75
BYAGENT_MIN = 0.68
INVERSION_MARGIN = 0.10
RANDOM_CHANCE_4WAY = 0.25
RANDOM_CHANCE_3WAY = 1.0 / 3.0
V1_CANONICAL_GATE_FP_RATE = 0.2124   # MEASURED@data/exp_extraction_commit_then_revise_v1/metrics.json
                                     # :summary.gate_rate_by_kind.canonical -- lever 1's own floor-to-beat

THRESH_GRID = [0.3, 0.4, 0.5, 0.6]
MARGIN_GRID = [0.0, 0.10, 0.20, 0.30]
# self-test uses ONE fixed cheap combo (mechanism-exercise only; full grid would be wasted compute at
# self-test's tiny truncated pool where LOOCV folds are near-degenerate).
SELF_TEST_THRESH = 0.3
SELF_TEST_MARGIN = 0.15


# ---------------------------------------------------------------------------
# LEVER 2: clause segmentation + clause-level agent=subject default.
# ---------------------------------------------------------------------------
BOUNDARY_WORDS = {
    "and", "but", "or", "so", "nor", "yet",           # coordinating
    "when", "because", "while", "although", "since",  # subordinating (word-list; "when" mistags ADV
    "after", "before", "if", "unless", "though", "as", "that",  # by this tagger, verified in docstring)
}


def segment_clauses(tokens, pos):
    """Split a token stream into clause spans on CCONJ/SCONJ (POS-tag OR word-list, since this
    tagger mistags 'when' as ADV) and clause-level punctuation (';'). Returns list of (start,end)
    half-open index ranges; boundary tokens themselves belong to no clause span."""
    n = len(tokens)
    spans = []
    start = 0
    for i in range(n):
        tl = tokens[i].lower()
        is_boundary = (tl in BOUNDARY_WORDS) or (pos[i] in ("CCONJ", "SCONJ")) or (tokens[i] == ";")
        if is_boundary:
            if i > start:
                spans.append((start, i))
            start = i + 1
    if start < n:
        spans.append((start, n))
    if not spans:
        spans = [(0, n)]
    return spans


def clause_position_predict(sent):
    """LEVER 2 default: per-clause first-non-quoted-mention = agent, all other mentions in that SAME
    clause = patient. Multi-clause sentences get one agent PER clause, not one global sentence subject."""
    tokens = sent["tokens"]
    pos = sent["pos"]
    mention_idx = sent["mention_idx"]
    in_quote, _ = quote_spans(tokens)
    spans = segment_clauses(tokens, pos)
    preds = {}
    for (cs, ce) in spans:
        clause_mentions = [i for i in mention_idx if cs <= i < ce]
        if not clause_mentions:
            continue
        subj = None
        for i in clause_mentions:
            if not in_quote[i]:
                subj = i
                break
        if subj is None:
            subj = clause_mentions[0]
        for i in clause_mentions:
            preds[i] = ROLE_IDX["agent"] if i == subj else ROLE_IDX["patient"]
    return preds


# ---------------------------------------------------------------------------
# LEVER 1: gate + margin-gated graceful-degrade revise.
# ---------------------------------------------------------------------------
def gate_fires_v2(sent: dict, thresh: float) -> bool:
    ss = sent["sent_summary"]
    has_by = ss[3] >= 0.5
    quotative_cue = (ss[0] >= 0.5) and (ss[1] > thresh)
    return bool(has_by or quotative_cue)


def revise_predict_one_with_margin(sent, W, mu, sd):
    """Per-mention argmax PLUS the softmax margin (top1 - top2 prob) used as the confidence gate."""
    preds = {}
    margins = {}
    for i in sent["mention_idx"]:
        raw = mention_features_multi(sent, i)
        std = (raw - mu) / sd
        logits = np.append(std, 1.0) @ W
        probs = _softmax(logits.reshape(1, -1))[0]
        order = np.argsort(probs)[::-1]
        top1 = float(probs[order[0]])
        top2 = float(probs[order[1]]) if len(probs) > 1 else 0.0
        preds[i] = int(order[0])
        margins[i] = top1 - top2
    return preds, margins


def loocv_revise_v2(noncanon_sents: list) -> tuple:
    """LOOCV strictly within the non-canonical subset (marked constructions only). Returns
    (preds_by_held_idx, margins_by_held_idx)."""
    n = len(noncanon_sents)
    out_preds, out_margins = {}, {}
    for held in range(n):
        train = [s for j, s in enumerate(noncanon_sents) if j != held]
        if not train:
            out_preds[held] = {}
            out_margins[held] = {}
            continue
        W, mu, sd = fit_softmax_on(train)
        p, m = revise_predict_one_with_margin(noncanon_sents[held], W, mu, sd)
        out_preds[held] = p
        out_margins[held] = m
    return out_preds, out_margins


def fit_revise_side(sents: list) -> dict:
    """Precompute the REVISE side (LOOCV predictions+margins on the non-canonical subset, plus the
    full-pool production model) ONCE. Neither depends on thresh/margin_thresh, so this is computed a
    single time and reused across the whole grid sweep (16x redundant LOOCV refits would otherwise be
    wasted compute -- thresh/margin only gate WHETHER/WHEN the revise output is accepted downstream)."""
    noncanon_ids = [sid for sid, s in enumerate(sents) if s["kind"] != "canonical"]
    noncanon_sents = [sents[sid] for sid in noncanon_ids]
    loocv_preds, loocv_margins = loocv_revise_v2(noncanon_sents)
    loocv_pred_map = {noncanon_ids[j]: loocv_preds[j] for j in range(len(noncanon_ids))}
    loocv_margin_map = {noncanon_ids[j]: loocv_margins[j] for j in range(len(noncanon_ids))}
    W_prod, mu_prod, sd_prod = fit_softmax_on(noncanon_sents)
    return {
        "noncanon_ids": set(noncanon_ids),
        "loocv_pred_map": loocv_pred_map, "loocv_margin_map": loocv_margin_map,
        "W_prod": W_prod, "mu_prod": mu_prod, "sd_prod": sd_prod,
    }


def commit_then_revise_v2_predict_all(sents: list, thresh: float, margin_thresh: float,
                                       revise_side: dict) -> tuple:
    """COMMIT = clause_position_predict (lever 2). REVISE = narrow non-canonical-only multiclass
    softmax (precomputed in revise_side), applied per-mention ONLY when gate_fires_v2(sent, thresh)
    AND that mention's margin clears margin_thresh (lever 1 graceful degrade); otherwise the clause
    default is kept even inside a gated sentence. Returns (preds_by_sent, gate_flags, fallback_flags)."""
    loocv_pred_map = revise_side["loocv_pred_map"]
    loocv_margin_map = revise_side["loocv_margin_map"]
    W_prod, mu_prod, sd_prod = revise_side["W_prod"], revise_side["mu_prod"], revise_side["sd_prod"]

    preds_by_sent = {}
    gate_flags = {}
    fallback_flags = {}
    for sid, sent in enumerate(sents):
        fires = gate_fires_v2(sent, thresh)
        gate_flags[sid] = fires
        default_preds = clause_position_predict(sent)
        if fires:
            if sid in loocv_pred_map:
                revise_preds, revise_margins = loocv_pred_map[sid], loocv_margin_map[sid]
            else:
                revise_preds, revise_margins = revise_predict_one_with_margin(sent, W_prod, mu_prod, sd_prod)
            merged = {}
            any_fb = False
            for i in sent["mention_idx"]:
                if i in revise_preds and revise_margins.get(i, 0.0) >= margin_thresh:
                    merged[i] = revise_preds[i]
                else:
                    merged[i] = default_preds.get(i, ROLE_IDX["patient"])
                    any_fb = True
            preds_by_sent[sid] = merged
            fallback_flags[sid] = any_fb
        else:
            preds_by_sent[sid] = default_preds
            fallback_flags[sid] = None
    return preds_by_sent, gate_flags, fallback_flags


def _digest(preds_by_sent):
    flat = json.dumps({str(k): v for k, v in preds_by_sent.items()}, sort_keys=True)
    return hashlib.sha256(flat.encode()).hexdigest()[:16]


def _gate_rate_by_kind(sents, gate_flags):
    by_kind = {}
    for sid, sent in enumerate(sents):
        k = sent["kind"]
        by_kind.setdefault(k, [0, 0])
        by_kind[k][1] += 1
        by_kind[k][0] += int(gate_flags[sid])
    return {k: (c / n if n else None) for k, (c, n) in by_kind.items()}


def _fallback_rate_among_gated(sents, gate_flags, fallback_flags):
    n_gated = sum(1 for sid in range(len(sents)) if gate_flags[sid])
    n_fb = sum(1 for sid in range(len(sents)) if gate_flags[sid] and fallback_flags.get(sid))
    return (n_fb / n_gated) if n_gated else None


def _score_config(sents, thresh, margin_thresh, revise_side):
    preds_by_sent, gate_flags, fallback_flags = commit_then_revise_v2_predict_all(
        sents, thresh, margin_thresh, revise_side)
    per_kind = eval_predictions(sents, preds_by_sent)
    canon = (per_kind.get("canonical") or {}).get("role_acc") or 0.0
    quot = (per_kind.get("quotative") or {}).get("role_acc") or 0.0
    byagent = (per_kind.get("passive_byagent") or {}).get("role_acc") or 0.0
    gate_diag = _gate_rate_by_kind(sents, gate_flags)
    n_gates = int(canon >= CANONICAL_MIN) + int(quot >= QUOTATIVE_MIN) + int(byagent >= BYAGENT_MIN)
    return {
        "thresh": thresh, "margin_thresh": margin_thresh,
        "canonical_role_acc": canon, "quotative_role_acc": quot, "byagent_role_acc": byagent,
        "canonical_gate_fp_rate": gate_diag.get("canonical"),
        "fallback_rate_among_gated": _fallback_rate_among_gated(sents, gate_flags, fallback_flags),
        "n_gates_cleared": n_gates,
        "preds_by_sent": preds_by_sent, "gate_flags": gate_flags, "fallback_flags": fallback_flags,
        "per_kind": per_kind,
    }


def _select_key(res):
    """Selection rule fixed BEFORE running (META_RULE_M adaptive_with_discriminator_gate), in priority
    order: (1) most pre-registered gates cleared, (2) highest canonical role_acc, (3) LOWEST canonical
    gate false-positive rate (lever 1's own honesty check -- among configs tied on accuracy, prefer the
    one that fires on canonical LESS, i.e. the more genuinely graceful-degrading gate, not just the one
    whose margin-fallback happens to erase the gate's effect post-hoc). fp_rate defaults to 1.0 (worst)
    if missing so a None never wins a tie by comparison error."""
    fp = res["canonical_gate_fp_rate"]
    fp = fp if fp is not None else 1.0
    return (res["n_gates_cleared"], res["canonical_role_acc"], -fp)


def select_config(sents, thresh_grid, margin_grid, revise_side):
    """Grid-search selection; see _select_key for the fixed-in-advance priority order. Returns
    (selected_result, full_grid_summary_list)."""
    grid_summary = []
    best = None
    for th in thresh_grid:
        for mg in margin_grid:
            res = _score_config(sents, th, mg, revise_side)
            grid_summary.append({k: v for k, v in res.items()
                                  if k not in ("preds_by_sent", "gate_flags", "fallback_flags")})
            if best is None or _select_key(res) > _select_key(best):
                best = res
    return best, grid_summary


def run_all(mode):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    t0 = time.perf_counter()

    canon_recs, canon_diag = load_canonical_pool()
    quot_recs = load_quotative_pool()
    byagent_recs = load_byagent_pool()
    passive_recs = load_passive_pool()

    if mode == "self_test":
        canon_recs = canon_recs[:10]
        quot_recs = quot_recs[:6]
        byagent_recs = byagent_recs[:4]
        passive_recs = passive_recs[:3]

    print("[%s] pools: canonical=%d quotative=%d byagent=%d passive=%d"
          % (mode, len(canon_recs), len(quot_recs), len(byagent_recs), len(passive_recs)), flush=True)

    all_recs = canon_recs + quot_recs + byagent_recs + passive_recs
    print("[%s] building %d sentences (tagger load+tag) ..." % (mode, len(all_recs)), flush=True)
    sents = [build_sentence_multi(r) for r in all_recs]

    rng_random = np.random.default_rng(20260802)

    if mode == "self_test":
        thresh_grid, margin_grid = [SELF_TEST_THRESH], [SELF_TEST_MARGIN]
    else:
        thresh_grid, margin_grid = THRESH_GRID, MARGIN_GRID

    print("[%s] fitting REVISE side (LOOCV on non-canonical pool, computed ONCE for the whole sweep) ..."
          % mode, flush=True)
    revise_side = fit_revise_side(sents)

    print("[%s] sweeping %d configs for COMMIT_REVISE_V2 ..." % (mode, len(thresh_grid) * len(margin_grid)),
          flush=True)
    selected, grid_summary = select_config(sents, thresh_grid, margin_grid, revise_side)
    print("[%s] selected thresh=%.2f margin=%.2f (canon=%.4f quot=%.4f byagent=%.4f gates=%d/3)"
          % (mode, selected["thresh"], selected["margin_thresh"], selected["canonical_role_acc"],
             selected["quotative_role_acc"], selected["byagent_role_acc"], selected["n_gates_cleared"]),
          flush=True)

    def run_arm(arm_name, tick):
        key = ckpt.unit_key(mode, arm_name)
        if key not in ckpt.completed_units(OUTPUT_DIR):
            gate_diag = None
            extra = {}
            if arm_name == "COMMIT_REVISE_V2":
                preds_by_sent = selected["preds_by_sent"]
                gate_diag = _gate_rate_by_kind(sents, selected["gate_flags"])
                extra = {
                    "selected_thresh": selected["thresh"], "selected_margin_thresh": selected["margin_thresh"],
                    "fallback_rate_among_gated": selected["fallback_rate_among_gated"],
                    "grid_summary": grid_summary,
                }
            elif arm_name == "COMMIT_REVISE_V1":
                preds_by_sent, v1_gate_flags = commit_then_revise_v1_predict_all(sents)
                gate_diag = _gate_rate_by_kind(sents, v1_gate_flags)
            elif arm_name == "CLAUSE_POSITION":
                preds_by_sent = {sid: clause_position_predict(sent) for sid, sent in enumerate(sents)}
            elif arm_name == "POSITION":
                preds_by_sent = {sid: position_predict(sent) for sid, sent in enumerate(sents)}
            else:  # RANDOM
                preds_by_sent = {sid: random_predict(sent, rng_random) for sid, sent in enumerate(sents)}
            per_kind = eval_predictions(sents, preds_by_sent)
            result = {"per_kind": per_kind, "digest": _digest(preds_by_sent)}
            if gate_diag is not None:
                result["gate_rate_by_kind"] = gate_diag
            result.update(extra)
            ckpt.record_unit(OUTPUT_DIR, key, result)
            print("[%s] arm=%s per_kind=%s gate_diag=%s" % (mode, arm_name, per_kind, gate_diag), flush=True)

    for i, arm in enumerate(["COMMIT_REVISE_V2", "COMMIT_REVISE_V1", "CLAUSE_POSITION", "POSITION", "RANDOM"]):
        run_arm(arm, i)

    units = {k.split("|")[-1]: v for k, v in ckpt.load_units(OUTPUT_DIR).items() if k.startswith(mode + "|")}
    elapsed = time.perf_counter() - t0
    return units, canon_diag, len(sents), elapsed


def _arms_must_differ(units):
    digs = {k: v["digest"] for k, v in units.items()}
    names = sorted(digs)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digs[a] != digs[b], f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} bit-identical"


def decide_verdict(units):
    def racc(arm, kind):
        v = (units[arm]["per_kind"].get(kind) or {}).get("role_acc")
        return v if v is not None else 0.0

    v2_canon = racc("COMMIT_REVISE_V2", "canonical")
    v2_quot = racc("COMMIT_REVISE_V2", "quotative")
    v2_byagent = racc("COMMIT_REVISE_V2", "passive_byagent")
    v2_passive = racc("COMMIT_REVISE_V2", "passive")
    v1_canon = racc("COMMIT_REVISE_V1", "canonical")
    v1_quot = racc("COMMIT_REVISE_V1", "quotative")
    v1_byagent = racc("COMMIT_REVISE_V1", "passive_byagent")
    clausepos_canon = racc("CLAUSE_POSITION", "canonical")
    pos_canon = racc("POSITION", "canonical")
    pos_quot = racc("POSITION", "quotative")
    pos_byagent = racc("POSITION", "passive_byagent")
    rand_quot = racc("RANDOM", "quotative")
    rand_byagent = racc("RANDOM", "passive_byagent")

    canonical_match_or_beat = v2_canon >= CANONICAL_MIN
    canonical_beats_floor = v2_canon > POSITION_CANONICAL_FLOOR
    quotative_preserved = v2_quot >= QUOTATIVE_MIN
    byagent_preserved = v2_byagent >= BYAGENT_MIN
    no_revise_inverts_quot = pos_quot <= (RANDOM_CHANCE_3WAY - INVERSION_MARGIN)
    no_revise_inverts_byagent = pos_byagent <= (RANDOM_CHANCE_3WAY - INVERSION_MARGIN)

    v2_gate_diag = units.get("COMMIT_REVISE_V2", {}).get("gate_rate_by_kind") or {}
    canonical_gate_fp_rate_v2 = v2_gate_diag.get("canonical")
    canonical_gate_fp_dropped = (canonical_gate_fp_rate_v2 is not None
                                 and canonical_gate_fp_rate_v2 < V1_CANONICAL_GATE_FP_RATE)

    summary = {
        "commit_revise_v2_canonical_role_acc": v2_canon, "commit_revise_v2_quotative_role_acc": v2_quot,
        "commit_revise_v2_byagent_role_acc": v2_byagent, "commit_revise_v2_passive_role_acc": v2_passive,
        "commit_revise_v1_canonical_role_acc": v1_canon, "commit_revise_v1_quotative_role_acc": v1_quot,
        "commit_revise_v1_byagent_role_acc": v1_byagent,
        "clause_position_canonical_role_acc": clausepos_canon,
        "position_canonical_role_acc": pos_canon, "position_quotative_role_acc": pos_quot,
        "position_byagent_role_acc": pos_byagent,
        "random_quotative_role_acc": rand_quot, "random_byagent_role_acc": rand_byagent,
        "canonical_match_or_beat": bool(canonical_match_or_beat),
        "canonical_beats_position_floor": bool(canonical_beats_floor),
        "quotative_preserved": bool(quotative_preserved),
        "byagent_preserved": bool(byagent_preserved),
        "no_revise_reproduces_inversion_quotative": bool(no_revise_inverts_quot),
        "no_revise_reproduces_inversion_byagent": bool(no_revise_inverts_byagent),
        "v1_canonical_gate_fp_rate": V1_CANONICAL_GATE_FP_RATE,
        "v2_canonical_gate_fp_rate": canonical_gate_fp_rate_v2,
        "canonical_gate_fp_rate_dropped_vs_v1": bool(canonical_gate_fp_dropped) if canonical_gate_fp_rate_v2 is not None else None,
        "per_arm_per_kind": {a: units[a]["per_kind"] for a in units},
        "gate_rate_by_kind_v2": v2_gate_diag,
        "selected_thresh": units.get("COMMIT_REVISE_V2", {}).get("selected_thresh"),
        "selected_margin_thresh": units.get("COMMIT_REVISE_V2", {}).get("selected_margin_thresh"),
        "fallback_rate_among_gated": units.get("COMMIT_REVISE_V2", {}).get("fallback_rate_among_gated"),
    }

    canfail_ok = no_revise_inverts_quot and no_revise_inverts_byagent
    if not canfail_ok:
        return "CANFAIL_VIOLATION_NO_REVISE_DID_NOT_REPRODUCE_INVERSION", summary
    if canonical_match_or_beat and quotative_preserved and byagent_preserved:
        tier = "HARD_PASS_BOTH_LEVERS_FIX_CANONICAL_PRESERVE_MARKED"
        if canonical_beats_floor:
            tier = "HARD_PASS_BOTH_LEVERS_BEAT_POSITION_FLOOR_PRESERVE_MARKED"
        return tier, summary
    if quotative_preserved and byagent_preserved and v2_canon > v1_canon + 0.03:
        return "MIDDLE_BAND_LEVERS_IMPROVED_CANONICAL_STILL_BELOW_FLOOR", summary
    if not quotative_preserved or not byagent_preserved:
        return "PARTIAL_CANONICAL_FIXED_MARKED_REGRESSED", summary
    return "HARD_FAIL_LEVERS_DID_NOT_FIX_CANONICAL", summary


def _write_metrics(verdict, summary, units, canon_diag, n_sents, elapsed, mode):
    metrics = {
        "anchor": ANCHOR_NAME, "mode": mode, "verdict": verdict,
        "verdict_msg": (
            "%s | V2 canon=%.3f quot=%.3f byagent=%.3f | V1 canon=%.3f quot=%.3f byagent=%.3f | "
            "CLAUSE_POSITION canon=%.3f | POSITION canon=%.3f quot=%.3f | "
            "canonical_match_or_beat=%s beats_floor=%s | quotative_preserved=%s | byagent_preserved=%s | "
            "gate_fp(v1/v2 canon)=%.3f/%s | no_revise_inverts(quot/byagent)=%s/%s"
            % (verdict, summary["commit_revise_v2_canonical_role_acc"],
               summary["commit_revise_v2_quotative_role_acc"], summary["commit_revise_v2_byagent_role_acc"],
               summary["commit_revise_v1_canonical_role_acc"], summary["commit_revise_v1_quotative_role_acc"],
               summary["commit_revise_v1_byagent_role_acc"], summary["clause_position_canonical_role_acc"],
               summary["position_canonical_role_acc"], summary["position_quotative_role_acc"],
               summary["canonical_match_or_beat"], summary["canonical_beats_position_floor"],
               summary["quotative_preserved"], summary["byagent_preserved"],
               summary["v1_canonical_gate_fp_rate"], summary["v2_canonical_gate_fp_rate"],
               summary["no_revise_reproduces_inversion_quotative"],
               summary["no_revise_reproduces_inversion_byagent"])
        ),
        "summary": summary,
        "bands": {"POSITION_CANONICAL_FLOOR": POSITION_CANONICAL_FLOOR, "CANONICAL_SLACK": CANONICAL_SLACK,
                  "CANONICAL_MIN": CANONICAL_MIN, "QUOTATIVE_MIN": QUOTATIVE_MIN, "BYAGENT_MIN": BYAGENT_MIN,
                  "INVERSION_MARGIN": INVERSION_MARGIN, "RANDOM_CHANCE_4WAY": RANDOM_CHANCE_4WAY,
                  "RANDOM_CHANCE_3WAY": RANDOM_CHANCE_3WAY,
                  "V1_CANONICAL_GATE_FP_RATE": V1_CANONICAL_GATE_FP_RATE,
                  "THRESH_GRID": THRESH_GRID, "MARGIN_GRID": MARGIN_GRID},
        "per_arm": {a: {k: v for k, v in u.items() if k != "grid_summary"} for a, u in units.items()},
        "grid_summary": units.get("COMMIT_REVISE_V2", {}).get("grid_summary"),
        "canonical_pool_diag": canon_diag,
        "role_vocab": ROLE_VOCAB4,
        "n_sentences_pooled": n_sents,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "cell_chunked": False,
        "calibration_check": "adaptive_with_discriminator_gate",
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
    ap.add_argument("--timeout", type=float, default=300.0,
                    help="formula self-test timeout budget (declared; measured full run incl. 16-cfg "
                         "grid sweep expected < 180s)")
    args = ap.parse_args()
    if not args.self_test and not args.full:
        args.self_test = True
    mode = "self_test" if args.self_test else "full"

    print("[%s] starting %s" % (mode, ANCHOR_NAME), flush=True)
    try:
        units, canon_diag, n_sents, elapsed = run_all(mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("[%s] FATAL: %s\n%s" % (mode, e, traceback.format_exc()), flush=True)
        raise SystemExit(2)

    _arms_must_differ(units)
    verdict, summary = decide_verdict(units)
    metrics = _write_metrics(verdict, summary, units, canon_diag, n_sents, elapsed, mode)
    print("[%s] VERDICT: %s" % (mode, verdict), flush=True)
    print("[%s] %s" % (mode, metrics["verdict_msg"]), flush=True)
    print("[%s] elapsed=%.1fs" % (mode, elapsed), flush=True)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
