# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (hash-compare ORACLE/REAL/FLOOR registers)
# - final_metrics_atomicity = tmp_replace (single-shot; whole run < 10s)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a: "structural can-fail test, no CRLB noise floor applies"; discriminator_reachability=true
#   (ORACLE reproduction of 36ab29a93 IS the reachability check)
# - baseline_in_band EXEMPTED for FLOOR arm (can-fail arm is REQUIRED near its structural floor)
# - cell_chunked=False (single pass, 3 arms, wall time < 10s; per-arm checkpoint via
#   tools/exp_checkpoint.py used anyway per CLAUDE.md's "any cell looping over >1 unit" rule)
# - HYPOTHESIZED/MEASURED/CITED/THEORETICAL tags on every number in this docstring
# - ASCII-only, no emojis, no em dashes.
"""exp_wire_extraction_accumulate_wm_oracle_vs_real_v1 (2026-08-02)

Assembles the two VALIDATED organs named in the director spawn prompt / design note
(notes/wire_extraction_wm_real_text_entity_tracking_design_2026-08-02.md, Findings 1-3):

STAGE 1 (extraction, reused verbatim as a FROZEN production model): the interactive top-down
role-mapping from experiments/exp_interactive_loop_real_gold_mcguffey_v1.py, which resolved
quotative agent-selection HARD_PASS (MEASURED@data/exp_interactive_loop_real_gold_mcguffey_v1_
byagent_v2/metrics.json:summary.on_quot_hard = 0.895 per commit history) and by-agent passive
agent-selection HARD_PASS (MEASURED@ same file: summary.on_byagent_hard = 0.739). That cell fits
a ridge-logistic top-down model over pooled quotative + by-agent-passive gold and predicts a
binary is_agent score per candidate mention via LOOCV. Here the SAME feature builder + model
form is refit on 100% of that gold (the "frozen production" weights, no held-out split needed
because this gold is not the evaluation set here) and APPLIED OUT-OF-DOMAIN to brand-new
multiclause narrative clauses it was never trained on.

STAGE 2 (accumulate WM, reused verbatim): the FHRR bundle-accumulate register validated in
experiments/exp_situation_model_accumulate_vs_overwrite_v1.py (commit 36ab29a93, HARD_PASS:
accumulate recovers 100% of multi-event entities' role-events vs pure-overwrite 0.4615 vs floor
0.2051 -- MEASURED@data/exp_situation_model_accumulate_vs_overwrite_v1/metrics.json:
multi_event_agg.accumulate.mean). Reimplemented here bit-for-bit (same bind/bundle/cleanup math),
because this cell needs to build TWO registers per entity (one from GOLD roles = ORACLE, one from
STAGE-1-PREDICTED roles = REAL) and compare them side by side.

THE HEADLINE MEASUREMENT (oracle-vs-real split; isolates the WM from extraction error):
  ORACLE arm: accumulate register fed GOLD per-clause roles -> expect ~reproduce 36ab29a93
              (sanity: the WM organ still works; if this does NOT hold, something is mis-wired,
              per the contract's explicit CAN-FAIL).
  REAL arm:   accumulate register fed STAGE-1 EXTRACTION-PREDICTED roles -> the DROP from ORACLE
              is the extraction-error-propagation number. THIS is the end-to-end result.
  FLOOR arm:  independent random register unrelated to content (non-vacuous floor; MUST fail,
              same floor construction as 36ab29a93's ARM C).

COVERAGE-HONESTY (pre-registered BEFORE running, from reading the STAGE-1 mechanism's own task
definition): STAGE 1 was built as a BINARY is-agent-or-not selector (that is what quotative
speaker-selection and by-agent-phrase agent-selection both reduce to). The new multiclause gold
(data/eval_gold_mention_role_mcguffey_v1/gold_multiclause_entity_track_v1.jsonl) uses a 6-way
role vocab (agent/patient/theme/recipient/addressee/speaker). STAGE 1 CANNOT natively predict
theme/recipient/addressee/speaker-as-distinct-from-agent -- it can only ever emit "agent" (the
argmax-scoring mention in a clause) or "patient" (the fallback for every other mention, mirroring
STAGE 1's own degenerate-passive convention: non-agent surface subject = patient). This is a
STRUCTURAL COVERAGE GAP, not a bug: it is reported honestly as a finding (per contract), not
forced or faked. Read off disk BEFORE running (see role_census below): of 36 total role-events
across 15 entities in the 6-passage gold, roles outside {agent, patient} are structurally
unreachable by STAGE 1 regardless of how well it generalizes.

Run:  .venv/Scripts/python.exe experiments/exp_wire_extraction_accumulate_wm_oracle_vs_real_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_wire_extraction_accumulate_wm_oracle_vs_real_v1.py --full
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
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

# Reuse STAGE-1 building blocks VERBATIM from the validated extraction cell (import, do not
# reimplement): tokenizer, POS-tagger accessor, quote-span detector, feature assembler, design-
# matrix builder, ridge-logistic fitter, gold loader, per-sentence feature builder.
from exp_interactive_loop_real_gold_mcguffey_v1 import (  # noqa: E402
    tokenize, get_tagger, quote_spans, mention_features, build_design, fit_logreg, norm_word,
    load_gold as load_extraction_gold, build_sentence, QUOT_PATH, BYAGENT_PATH_V2,
    VERB_POS, BE_FORMS, MENTION_POS, L2_LAMBDA, LR, N_ITERS,
)

ANCHOR_NAME = "wire_extraction_accumulate_wm_oracle_vs_real_v1"
GOLD_MULTICLAUSE = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1", "gold_multiclause_entity_track_v1.jsonl"
)
ROLE_VOCAB = ["agent", "patient", "theme", "recipient", "addressee", "speaker"]
MAX_EVENT_SLOTS = 8

# ---------------------------------------------------------------------------
# PRE-REGISTERED BANDS (fixed BEFORE running; ONE run, no post-hoc tuning)
# ---------------------------------------------------------------------------
ORACLE_REPRO_TOL = 0.08          # ORACLE must reproduce 36ab29a93's accumulate_multi (MEASURED@ 1.0)
                                  # within this tolerance (same tolerance the source cell used for its
                                  # own can-fail formula check, small-N sampling discipline)
ORACLE_REPRO_TARGET = 1.0        # MEASURED@data/exp_situation_model_accumulate_vs_overwrite_v1/
                                  # metrics.json:multi_event_agg.accumulate.mean
FLOOR_MAX = 1.0 / len(ROLE_VOCAB) + 0.15   # floor must stay near chance (same construction as
                                  # 36ab29a93's gate_canfail_floor: chance + 0.15)
REAL_HARD_PASS_MIN = 0.50         # HYPOTHESIZED: given the coverage gap (agent/patient-only extraction
                                  # vs 6-way vocab), a real end-to-end HARD_PASS bar is set at "clearly
                                  # beats floor and recovers a majority of the reachable (agent/patient)
                                  # subspace" rather than reproducing ORACLE's ceiling -- ORACLE's ceiling
                                  # is NOT achievable by construction once extraction is binary.
REAL_MIDDLE_MIN = 0.30            # HYPOTHESIZED: floor+~0.15-0.30 = partial signal, extraction propagates
                                  # real but incomplete role information.


def repo_path(rel: str) -> str:
    return rel if os.path.isabs(rel) else os.path.join(REPO_ROOT, rel)


OUTPUT_DIR = repo_path(f"data/exp_{ANCHOR_NAME}")


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "expected_n_units": expected_n_units, "host": os.environ.get("COMPUTERNAME", "unknown"),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(), "anchor_name": ANCHOR_NAME,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


# ---------------------------------------------------------------------------
# FHRR primitives (bare numpy; bit-for-bit the same math as hdlab.binding /
# hdlab.bundling and as exp_situation_model_accumulate_vs_overwrite_v1's reimplementation)
# ---------------------------------------------------------------------------
def unit_phase_vec(rng, d):
    theta = rng.uniform(0.0, 2.0 * np.pi, size=d)
    return np.exp(1j * theta).astype(np.complex64)


def fhrr_bind(a, b):
    return (a * b).astype(np.complex64)


def fhrr_unbind(c, b):
    return (c * np.conj(b)).astype(np.complex64)


def fhrr_bundle(vecs):
    s = vecs.sum(axis=0)
    mag = np.abs(s)
    mag = np.where(mag > 0, mag, 1.0)
    return (s / mag).astype(np.complex64)


def cleanup_argmax(readback, vocab):
    d = readback.shape[0]
    scores = {name: float(np.real(np.sum(np.conj(v) * readback))) / d for name, v in vocab.items()}
    best = max(scores.items(), key=lambda kv: kv[1])[0]
    return best, scores


def run_self_test(rng, d=64):
    v1 = unit_phase_vec(rng, d)
    v2 = unit_phase_vec(rng, d)
    bound = fhrr_bind(v1, v2)
    roundtrip = fhrr_unbind(bound, v2)
    err = float(np.max(np.abs(roundtrip - v1)))
    assert err < 1e-3, f"SELF_TEST FAIL: FHRR bind/unbind round-trip err={err}"
    v3 = unit_phase_vec(rng, d)
    v4 = unit_phase_vec(rng, d)
    unrelated = unit_phase_vec(rng, d)
    b1 = fhrr_bind(v1, v3)
    b2 = fhrr_bind(v2, v4)
    bundled = fhrr_bundle(np.stack([b1, b2], axis=0))
    rb1 = fhrr_unbind(bundled, v3)
    score_true = float(np.real(np.sum(np.conj(v1) * rb1))) / d
    score_unrelated = float(np.real(np.sum(np.conj(unrelated) * rb1))) / d
    assert score_true > score_unrelated, "SELF_TEST FAIL: bundle-of-2 unbind did not favor true content"


# ---------------------------------------------------------------------------
# STAGE 1: fit the FROZEN production top-down extraction model on 100% of its own
# validated gold (quotative + by-agent-passive v2), then apply it OUT-OF-DOMAIN to
# the new multiclause narrative clauses. Reuses build_sentence/build_design/
# mention_features/fit_logreg VERBATIM from exp_interactive_loop_real_gold_mcguffey_v1.
# ---------------------------------------------------------------------------
def fit_production_extraction_model():
    quot_recs = load_extraction_gold(QUOT_PATH)
    byagent_recs = load_extraction_gold(BYAGENT_PATH_V2)
    train_sents = ([build_sentence(r, "quotative") for r in quot_recs]
                   + [build_sentence(r, "passive_byagent") for r in byagent_recs])
    X, y, _, _ = build_design(train_sents, "ON")
    mu = X[:, :-1].mean(axis=0)
    sd = X[:, :-1].std(axis=0)
    sd[sd < 1e-8] = 1.0
    Xs = X.copy()
    Xs[:, :-1] = (X[:, :-1] - mu) / sd
    w = fit_logreg(Xs, y, L2_LAMBDA, LR, N_ITERS)
    return {"w": w, "mu": mu, "sd": sd, "n_train_sentences": len(train_sents)}


def build_clause_sent(text):
    """Lightweight equivalent of exp_interactive_loop_real_gold_mcguffey_v1.build_sentence, for a
    clause with NO gold-target label (STAGE 1 applied out-of-domain). Returns the same
    {tokens, pos, mention_idx, feats, sent_summary} shape that mention_features() consumes."""
    tokens = tokenize(text)
    pos = get_tagger().tag(tokens)
    n = len(tokens)
    in_quote, after_close = quote_spans(tokens)

    verb_idx = [i for i, p in enumerate(pos) if p in VERB_POS]
    has_be = any(tokens[i].lower() in BE_FORMS for i in range(n))
    by_idx = [i for i in range(n) if tokens[i].lower() == "by" and pos[i] == "ADP"]
    has_by = len(by_idx) > 0
    verb_after_close = any((p == "VERB") and after_close[i] and not in_quote[i]
                            for i, p in enumerate(pos))
    frac_in_quote = (sum(1 for f in in_quote if f) / n) if n else 0.0

    mention_idx = [i for i, p in enumerate(pos) if p in MENTION_POS and tokens[i] != '"']
    first_ment = mention_idx[0] if mention_idx else None
    subj_idx = None
    for i in mention_idx:
        if not in_quote[i]:
            subj_idx = i
            break
    if subj_idx is None and mention_idx:
        subj_idx = mention_idx[0]

    feats = {}
    for i in mention_idx:
        follows_verb = (i - 1) in verb_idx
        is_subject = (i == subj_idx)
        in_passive_ctx = has_be and any(j in verb_idx and pos[j] == "VERB" and j > i - 3
                                        for j in range(max(0, i - 2), min(n, i + 3)))
        follows_by = any(0 < i - j <= 3 for j in by_idx)
        base = np.array([i / max(1, n - 1), 1.0 if i == first_ment else 0.0], dtype=np.float64)
        constr = np.array([
            1.0 if in_quote[i] else 0.0, 1.0 if after_close[i] else 0.0,
            1.0 if follows_verb else 0.0, 1.0 if is_subject else 0.0,
            1.0 if in_passive_ctx else 0.0, 1.0 if follows_by else 0.0, 1.0,
        ], dtype=np.float64)
        feats[i] = (base, constr)

    sent_summary = np.array([
        1.0 if verb_after_close else 0.0, frac_in_quote,
        1.0 if has_be else 0.0, 1.0 if has_by else 0.0, 1.0,
    ], dtype=np.float64)

    return {"tokens": tokens, "pos": pos, "mention_idx": mention_idx, "feats": feats,
            "sent_summary": sent_summary}


def stage1_predict_clause(text, model):
    """Apply the frozen production model to one clause. Returns (sent, {mention_idx: is_agent_score},
    argmax_mention_idx or None)."""
    sent = build_clause_sent(text)
    if not sent["mention_idx"]:
        return sent, {}, None
    w, mu, sd = model["w"], model["mu"], model["sd"]
    scores = {}
    for i in sent["mention_idx"]:
        raw = mention_features(sent, i, "ON")
        std = (raw - mu) / sd
        z = float(np.dot(np.append(std, 1.0), w))
        scores[i] = 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))
    argmax_i = max(scores.items(), key=lambda kv: kv[1])[0]
    return sent, scores, argmax_i


def match_mention_to_token(sent, mention_text, used, entity_name=None):
    """Coref/mention-grounding is SUPPLIED (per contract): find which token index in this clause's
    tokenization corresponds to a gold entity's recorded mention string, via last-word normalized
    match (same technique exp_interactive_loop_real_gold_mcguffey_v1 uses for its own gold_target).
    `used` = set of already-claimed token indices this clause (avoid double-assigning ambiguous
    identical anchors).

    `entity_name` (optional, ADDITIVE 2026-08-02 fix): the gold entity chain's own canonical key
    (e.g. "Edgar"), tried as an anchor BEFORE the mention-text-last-word anchor. ROOT CAUSE this
    fixes: for a two-word proper name mention like "Edgar Rose" / "Thomas Read", the LAST WORD is
    the surname ("Rose"/"Read"), a token clause_position_predict5's per-clause subject rule
    correctly does NOT select as subject (the given name "Edgar"/"Thomas" is the actual clause
    subject and the recurring single-token identity used for this entity elsewhere in the passage)
    -- so anchoring on the surname silently grades the WRONG token and reports "agent predicted as
    patient" when the pipeline's clause-subject prediction was already correct. Independently
    corroborated: exp_extraction_commit_then_revise_v4_animacy.py's own probe already flagged
    "Thomas Read"/"Patty"/"Dash" as PROPER-NOUN HOMOGRAPH lexicon artifacts on this same eval file.
    Default None preserves the exact prior behavior for every OTHER caller (v2-v5 wire cells).

    GUARD (MEASURED regression caught this session): the entity_name anchor is used ONLY when the
    entity's own canonical name literally appears as a WORD inside mention_text (e.g. "Edgar Rose"
    contains "Edgar"). Without this guard, a DESCRIPTIVE mention that shares no words with the
    entity name (e.g. gold mention "his dog" for entity "Bounce", in willie_bounce) let the
    entity_name anchor over-eagerly grab an unrelated same-name token appearing later in the same
    clause ("... said that Bounce could do ..."), stealing the wrong token and regressing an
    already-correct prediction. Requiring the name to be a substring-word of the mention itself
    confines the fix to its intended case (multi-word proper names) and leaves purely-descriptive
    mentions on the original last-word behavior."""
    anchors = []
    mention_words = [norm_word(w) for w in mention_text.split()] if mention_text else []
    if entity_name:
        name_words = [norm_word(w) for w in entity_name.split() if norm_word(w)]
        if name_words and all(w in mention_words for w in name_words):
            for w in name_words:
                if w not in anchors:
                    anchors.append(w)
    mention_anchor = norm_word(mention_text.split()[-1]) if mention_text else None
    if mention_anchor and mention_anchor not in anchors:
        anchors.append(mention_anchor)
    if not anchors:
        return None
    for anchor in anchors:
        candidates = [i for i in sent["mention_idx"]
                      if i not in used and norm_word(sent["tokens"][i]) == anchor]
        if candidates:
            break
    else:
        candidates = []
    if not candidates:
        # tagger-noise fallback: scan ALL tokens (not just tagged mentions), same forgiveness
        # exp_interactive_loop_real_gold_mcguffey_v1 grants its own gold_target matching
        for anchor in anchors:
            candidates = [i for i in range(len(sent["tokens"]))
                          if i not in used and norm_word(sent["tokens"][i]) == anchor]
            if candidates:
                break
    return candidates[0] if candidates else None


def load_multiclause_gold(path):
    recs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    return recs


def build_entity_chains(passages, model, restrict_n=None):
    """Returns list of {key, passage_id, name, true_roles: [...], pred_roles: [...],
    match_ok: [...]} plus per-clause diagnostic dump. restrict_n truncates passages for smoke."""
    if restrict_n is not None:
        passages = passages[:restrict_n]

    entities_out = []
    clause_dump = []
    n_matched = 0
    n_total_events = 0
    n_predicted_agent = 0

    for rec in passages:
        pid = rec["passage_id"]
        clauses = rec["clauses"]
        # per-clause STAGE-1 inference (real code path: builds real POS-tagged sent + scores)
        clause_infer = [stage1_predict_clause(c, model) for c in clauses]
        for ci, (sent, scores, argmax_i) in enumerate(clause_infer):
            clause_dump.append({
                "passage_id": pid, "clause_idx": ci, "text": clauses[ci],
                "n_mentions": len(sent["mention_idx"]),
                "argmax_token": sent["tokens"][argmax_i] if argmax_i is not None else None,
            })

        # per-entity chain assembly: SUPPLIED coref (gold entity->mention link), PREDICTED role
        used_per_clause = [set() for _ in clauses]
        for name, chain in rec["entities"].items():
            true_roles, pred_roles, match_ok = [], [], []
            for ev in chain:
                ci = ev["clause"]
                sent, scores, argmax_i = clause_infer[ci]
                tok_i = match_mention_to_token(sent, ev["mention"], used_per_clause[ci])
                n_total_events += 1
                if tok_i is not None:
                    used_per_clause[ci].add(tok_i)
                    n_matched += 1
                    pred_role = "agent" if (argmax_i is not None and tok_i == argmax_i) else "patient"
                    if pred_role == "agent":
                        n_predicted_agent += 1
                    match_ok.append(True)
                else:
                    # extraction could not ground the mention to a token at all (tagger/coref
                    # miss) -- honest fallback: patient (the non-agent default), NOT a crash,
                    # NOT the gold answer.
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
        "n_predicted_agent": n_predicted_agent, "n_predicted_patient": n_matched - n_predicted_agent,
    }
    return entities_out, clause_dump, diag


def role_census(entities_gold_only):
    """Honest pre-flight: how many true role-events fall OUTSIDE {agent, patient} (structurally
    unreachable by the binary STAGE-1 extraction, regardless of extraction quality)."""
    from collections import Counter
    c = Counter()
    for e in entities_gold_only:
        for r in e["true_roles"]:
            c[r] += 1
    total = sum(c.values())
    reachable = c.get("agent", 0) + c.get("patient", 0)
    return {"counts": dict(c), "total_events": total, "reachable_agent_patient_events": reachable,
            "unreachable_events": total - reachable,
            "unreachable_fraction": (total - reachable) / total if total else None}


def build_register(roles, role_vecs, idx_vecs):
    bound = [fhrr_bind(role_vecs[r], idx_vecs[i]) for i, r in enumerate(roles)]
    if len(bound) > 1:
        return fhrr_bundle(np.stack(bound, axis=0))
    return bound[0]


def score_entity(reg, true_roles, idx_vecs, role_vecs):
    correct = []
    for i, true_role in enumerate(true_roles):
        readback = fhrr_unbind(reg, idx_vecs[i])
        pred_role, _ = cleanup_argmax(readback, role_vecs)
        correct.append(1 if pred_role == true_role else 0)
    return correct


def run_all(mode, restrict_n=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    t0 = time.perf_counter()

    print("[%s] fitting STAGE-1 frozen production extraction model (quotative+byagent gold) ..."
          % mode, flush=True)
    model = fit_production_extraction_model()
    print("[%s] STAGE-1 model fit on %d sentences" % (mode, model["n_train_sentences"]), flush=True)

    passages = load_multiclause_gold(GOLD_MULTICLAUSE)
    print("[%s] loaded %d multiclause passages" % (mode, len(passages)), flush=True)

    entities, clause_dump, extraction_diag = build_entity_chains(passages, model, restrict_n=restrict_n)
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
            for e in entities:
                if arm_name == "oracle":
                    reg = build_register(e["true_roles"], role_vecs, idx_vecs)
                    correct = score_entity(reg, e["true_roles"], idx_vecs, role_vecs)
                elif arm_name == "real":
                    reg = build_register(e["pred_roles"], role_vecs, idx_vecs)
                    correct = score_entity(reg, e["true_roles"], idx_vecs, role_vecs)
                else:  # floor
                    reg = unit_phase_vec(rng_floor, d)
                    correct = score_entity(reg, e["true_roles"], idx_vecs, role_vecs)
                reg_bytes.append(reg.tobytes())
                per_entity.append({
                    "key": e["key"], "n_events": e["n_events"], "multi_event": e["multi_event"],
                    "correct": correct, "recall": float(np.mean(correct)),
                })
            result = {
                "per_entity": per_entity,
                "reg_digest": hashlib.sha256(b"".join(reg_bytes)).hexdigest(),
            }
            ckpt.record_unit(OUTPUT_DIR, key, result)
            multi = [r["recall"] for r in per_entity if r["multi_event"]]
            print("[%s] arm=%s multi_event_recall=%.4f (n=%d)"
                  % (mode, arm_name, float(np.mean(multi)) if multi else -1.0, len(multi)), flush=True)

    for i, arm in enumerate(["oracle", "real", "floor"]):
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

    oracle_ok = (oracle_multi["mean"] is not None
                 and abs(oracle_multi["mean"] - ORACLE_REPRO_TARGET) <= ORACLE_REPRO_TOL)
    floor_ok = floor_multi["mean"] is not None and floor_multi["mean"] <= FLOOR_MAX

    summary = {
        "oracle_multi_event_recall": oracle_multi["mean"], "oracle_n_entities": oracle_multi["n_entities"],
        "real_multi_event_recall": real_multi["mean"], "real_n_entities": real_multi["n_entities"],
        "floor_multi_event_recall": floor_multi["mean"], "floor_n_entities": floor_multi["n_entities"],
        "oracle_reproduces_36ab29a93": bool(oracle_ok), "floor_at_chance": bool(floor_ok),
        "oracle_to_real_drop": (oracle_multi["mean"] - real_multi["mean"])
                                if (oracle_multi["mean"] is not None and real_multi["mean"] is not None) else None,
        "role_census": census,
    }

    if not oracle_ok:
        return "HARD_FAIL_MISWIRED_ORACLE_DOES_NOT_REPRODUCE", summary
    if not floor_ok:
        return "HARD_FAIL_CANFAIL_VIOLATION_FLOOR_NOT_AT_CHANCE", summary

    rm = real_multi["mean"] or 0.0
    fm = floor_multi["mean"] or 0.0
    if rm >= REAL_HARD_PASS_MIN and rm > fm + 0.20:
        return "HARD_PASS_REAL_EXTRACTION_TRACKS_ENTITIES_ABOVE_COVERAGE_CEILING", summary
    if rm >= REAL_MIDDLE_MIN:
        return "MIDDLE_BAND_REAL_EXTRACTION_PARTIAL_ABOVE_FLOOR_BELOW_HARD_PASS", summary
    if rm <= fm + 0.10:
        return "HARD_FAIL_REAL_EXTRACTION_NO_BETTER_THAN_FLOOR", summary
    return "MIDDLE_PARTIAL_SIGNAL", summary


def _write_metrics(verdict, summary, units, entities, clause_dump, extraction_diag, elapsed, mode):
    per_entity_dump = []
    for arm in ("oracle", "real", "floor"):
        by_key = {e["key"]: e for e in units[arm]["per_entity"]}
        for key in by_key:
            pass
    # combine per-entity rows across arms for a single glass-box dump
    combined = {}
    for arm in ("oracle", "real", "floor"):
        for e in units[arm]["per_entity"]:
            combined.setdefault(e["key"], {"key": e["key"], "n_events": e["n_events"],
                                            "multi_event": e["multi_event"]})
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
            "%s | ORACLE multi_event_recall=%.4f (n=%d, target=%.4f tol=%.2f) | "
            "REAL multi_event_recall=%.4f (n=%d) | FLOOR multi_event_recall=%.4f (n=%d) | "
            "oracle_to_real_drop=%s | unreachable_role_fraction=%.4f"
            % (verdict, summary["oracle_multi_event_recall"] or -1, summary["oracle_n_entities"],
               ORACLE_REPRO_TARGET, ORACLE_REPRO_TOL,
               summary["real_multi_event_recall"] or -1, summary["real_n_entities"],
               summary["floor_multi_event_recall"] or -1, summary["floor_n_entities"],
               ("%.4f" % summary["oracle_to_real_drop"]) if summary["oracle_to_real_drop"] is not None else "n/a",
               summary["role_census"]["unreachable_fraction"] or -1)
        ),
        "summary": summary,
        "bands": {"ORACLE_REPRO_TARGET": ORACLE_REPRO_TARGET, "ORACLE_REPRO_TOL": ORACLE_REPRO_TOL,
                  "FLOOR_MAX": FLOOR_MAX, "REAL_HARD_PASS_MIN": REAL_HARD_PASS_MIN,
                  "REAL_MIDDLE_MIN": REAL_MIDDLE_MIN},
        "per_arm": units,
        "extraction_diag": extraction_diag,
        "per_entity_dump": per_entity_dump,
        "clause_dump": clause_dump,
        "role_vocab": ROLE_VOCAB,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "defensive_error_checking": "passed_all_4_patterns_heartbeat_exempt_lt10s",
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
    ap.add_argument("--timeout", type=float, default=120.0,
                     help="formula self-test timeout budget (declared; this cell runs in <30s)")
    args = ap.parse_args()
    if not args.self_test and not args.full:
        args.self_test = True
    mode = "self_test" if args.self_test else "full"

    _write_start_marker(OUTPUT_DIR, mode, expected_n_units=3)

    rng = np.random.default_rng(20260802)
    run_self_test(rng)  # FHRR primitive correctness, always run

    print("[%s] starting %s" % (mode, ANCHOR_NAME), flush=True)
    try:
        # self-test exercises the REAL code path (STAGE-1 tagger + model fit + gold load +
        # STAGE-2 FHRR accumulate) at a restricted 2-passage slice, NOT a synthetic-only branch
        # (gate F.1). full = all 6 passages (still < 30s; tiny data, no restriction needed).
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
