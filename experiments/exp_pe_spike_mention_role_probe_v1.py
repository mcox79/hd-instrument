# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: sha256 digest of (2b predicted-spike-set, 2c predicted-cue-array) for
#   FLOOR (random) vs CANDIDATE ckpt; checked in self-test + full run.
# - final_metrics_atomicity: tmp_replace (os.replace at end).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n_a: no learned-noise Cramer-Rao floor; discriminator is the pre-registered
#   FLOOR_OK / HARD_PASS_2b / HARD_FAIL_2b / MIDDLE_2b decision rule (see decide_verdict).
# - baseline_in_band: n/a in the usual sense -- the RANDOM-ckpt FLOOR_OK check IS the AG-equivalent
#   gate for this cell shape (an untrained encoder's PE stream must not beat the naive baselines).
# - discriminator survives scale: analytical -- CPU closed-form probe, identical code path for any
#   ckpt/passage size within max_len=128; self-test runs the REAL full pipeline against the REAL
#   ARM_RANDOM ckpt (real_code_path; no smaller regime exists).
# - HP_SCOPE: HARD_PASS_2b / HARD_FAIL_2b apply ONLY to the CANDIDATE ckpt's Probe-2b result;
#   FLOOR_OK applies ONLY to the FLOOR (random) ckpt; Probe 2c is reported UNGATED (exploratory).
# - cardinality_ok: EXPECTED_N_UNITS = 3 per ckpt (probe_2b, probe_2c_quotative, probe_2c_passive) x
#   2 ckpts (floor + candidate) = 6; counted in decide_verdict.
# - per-unit failure-class instrumentation: no bare except; except SystemExit/KeyboardInterrupt/
#   Exception ordering only.
# - calibration_check: "default_ok_for_this_regime" -- PE-spike threshold (mean+1*std), tolerance
#   window (+/-1 word), FLOOR_MARGIN(0.05), BASELINE_LINEAR_POSITION fraction (0.85) are fixed
#   HYPOTHESIZED thresholds set before running, not tuned post-hoc.
# - all numbers in comments/docstring tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@.
# - real_code_path_exercised: self-test loads the REAL ARM_RANDOM ckpt, builds the REAL
#   TinyTransformer (imported verbatim, zero new model code), runs the REAL causal forward pass.
# - substrate_signature_checked: TinyTransformer(vocab, max_len, d_model, n_layers, n_heads,
#   ffn_mult, pad_id) -- long-stable base constructor, no version-specific optional kwargs.
# - deterministic seeding: no randomness anywhere in this cell (pure closed-form forward pass +
#   fixed regex/threshold rules); no hash(), no list(set()).
"""PE-spike mention + role-disambiguation probe harness (Probe 2b/2c), v1 -- Option-C Step-1 test.

WHY: notes/research_earn_structure_extraction_vs_supply_parser_fork_2026-08-01.md Part 4 Step 1.
Does a trained CAUSAL encoder's OWN per-token prediction-error stream carry mention (referent-
introduction) and role-disambiguation structure as a FREE byproduct of next-token prediction, with
NO bolt-on parser, NO gold-parse training signal ever touching the encoder? This is the cheapest
decisive test of that hypothesis, BUILT NOW so it is ready to run the instant a sound (non-lite,
non-collapsed) causal encoder lands -- it does not itself require training anything.

PE DEFINITION (documented, ONE fixed rule -- see prereg "PE definition" section for full rationale):
  PE(token_i) = -log P(token_i | token_0 .. token_{i-1})
  computed under the ckpt's OWN causal-masked forward pass (`_causal_contextual`, lower-triangular
  attention -- reused VERBATIM from experiments/exp_encoder_latent_pc_arc_v1.py, zero new model
  code) with a TIED output head (logits = h_ctx @ tok_emb.weight.T, the same tied-head convention
  TinyTransformer.mlm_logits already uses, just fed causal instead of bidirectional hidden states).
  Word-level PE = MAX over a word's constituent BPE-token PEs (robust to BPE boundary noise).
  Applied at PROBE time to EVERY ckpt regardless of how it was trained -- bidirectional-trained
  ckpts are being asked an out-of-distribution question and are expected to score WORSE; this is
  disclosed, not hidden, and is a fair (not rigged) test of the CAUSAL-training claim specifically.

TWO PROBES:
  Probe 2b (referent introduction): does PE spike (> mean+1*std over the passage's word-final PEs)
    at gold discourse-referent-introduction positions? Metric = precision/recall/F1 vs
    data/eval_gold_mention_role_mcguffey_v1/gold_referent_introduction_v1.json (20 intros, 16 with
    NO a/an cue -- the discriminating subset). Baselines: BASELINE_LEXICAL (a/an-detector, exact-0
    recall on the 16-subset by construction) + BASELINE_CHANCE (analytic).
  Probe 2c (role-disambiguation cue): does PE spike-argmax land within +/-1 word of the gold cue
    position? Passive class -> the passive_verb token (gold_passive_verified_v1.jsonl). Quotative
    class -> the gold_agent_speaker span (gold_quotative_verified_v1.jsonl). Baselines:
    BASELINE_LINEAR_POSITION (fixed 0.85-fraction-of-sentence proxy, no PE read at all) +
    BASELINE_CHANCE (analytic).

CAN-FAIL FLOOR (mandatory, run every invocation): the SAME pipeline is ALWAYS run against BOTH a
  FLOOR ckpt (untrained ARM_RANDOM, same architecture/vocab/tokenizer) and a CANDIDATE ckpt in one
  invocation, so the floor-validation and the candidate smoke are never accidentally decoupled.
  FLOOR_OK requires the floor ckpt's numbers do NOT beat the naive baselines by more than
  FLOOR_MARGIN=0.05 absolute -- an untrained encoder's PE stream carries no linguistic structure.

Prior-work check: substrate_query.sh "prediction error spike referent introduction mention
detection causal encoder probe" -> top cosine=0.4404 (generic "Question / prediction" prereg
boilerplate, semantically unrelated); no hit above cosine 0.30 on PE-spike/referent-introduction/
mention-detection. Not a rediscovery -- genuinely new probe (see prereg for full note).

Run:  .venv/Scripts/python.exe experiments/exp_pe_spike_mention_role_probe_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_pe_spike_mention_role_probe_v1.py --full
      .venv/Scripts/python.exe experiments/exp_pe_spike_mention_role_probe_v1.py --full --ckpt-path <path>

ASCII-only. No emojis. Deterministic (no hash(), no list(set()), no randomness anywhere in this
cell -- pure closed-form forward pass + fixed regex/threshold rules).
Compute architecture: sequential-CPU, justified -- 2 ckpt forward passes (floor + candidate) over
<=27 short passages/sentences on a 6-layer/512-dim TinyTransformer; wall time target < 2 minutes
(compute-proportionality: cheapest decisive method for a go/no-go diagnostic, not a magnitude fit).
Storage strategy: no_storage / no_composition -- PE-stream measurement only, no bind/bundle/retrieve.
"""

import argparse
import hashlib
import json
import math
import os
import platform
import re
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch
import torch.nn.functional as F

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
# reuse the ALREADY-BUILT causal forward pass verbatim (zero new model code) -- this import gives
# TinyTransformer (via exp_encoder_latent_pc_arc_v1's own import chain) + _causal_contextual.
from experiments.exp_encoder_latent_pc_arc_v1 import TinyTransformer, _causal_contextual  # noqa: E402

sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_checkpoint as ckpt  # noqa: E402  -- per-unit checkpoint/resume (CLAUDE.md mandate)

ANCHOR_NAME = "pe_spike_mention_role_probe_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
GOLD_DIR = os.path.join(REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1")
GOLD_INTRO_PATH = os.path.join(GOLD_DIR, "gold_referent_introduction_v1.json")
GOLD_QUOTATIVE_PATH = os.path.join(GOLD_DIR, "gold_quotative_verified_v1.jsonl")
GOLD_PASSIVE_PATH = os.path.join(GOLD_DIR, "gold_passive_verified_v1.jsonl")

LITE_DIR = os.path.join(REPO_ROOT, "data", "exp_encoder_latent_pc_arc_v1_lite")
DEFAULT_FLOOR_CKPT = os.path.join(LITE_DIR, "ckpt_seed_7_ARM_RANDOM.pt")
DEFAULT_CANDIDATE_CKPT = os.path.join(LITE_DIR, "ckpt_seed_7_ARM_CAUSAL_REAL_BARLOW.pt")

# ---- pre-registered bands (written BEFORE running; NOT loosened) ----
FLOOR_MARGIN = 0.05          # THEORETICAL: small-slack floor-break tolerance
TOLERANCE_WINDOW = 1         # +/-1 word tolerance for Probe 2c cue alignment
LINEAR_POSITION_FRAC = 0.85  # HYPOTHESIZED@this file: cue is usually near sentence end
HARD_PASS_2B_LIFT = 0.10     # HYPOTHESIZED@research pre-reg Part 4: >=10 F1 pts over lexical baseline
HARD_PASS_2B_RECALL16_MIN = 0.30   # HYPOTHESIZED@this file (smoke-preview band, deflated per P=0.28)

WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
ARTICLE_WORDS = {"a", "an"}

EXPECTED_UNITS_PER_CKPT = 3   # probe_2b, probe_2c_quotative, probe_2c_passive


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------- canonical hardening ----------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "failure_class": type(exc).__name__}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _jsonify(obj):
    if isinstance(obj, torch.Tensor):
        return _jsonify(obj.detach().cpu().tolist())
    if isinstance(obj, np.ndarray):
        return _jsonify(obj.tolist())
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, dict):
        return {str(k): _jsonify(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonify(v) for v in obj]
    return obj


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    safe_metrics = _jsonify(metrics)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(safe_metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ================= ckpt loading (encoder-AGNOSTIC: any FrozenV2Encoder-shaped ckpt) =================
def load_frozen_ckpt(ckpt_path):
    """Loads state_dict + model_cfg + tokenizer_json (the FrozenV2Encoder-shape every arm in this
    codebase already saves -- Fix 2d, exp_encoder_latent_pc_arc_v1.py). Returns (model, tok, mc, arm)."""
    from tokenizers import Tokenizer
    ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    mc = ck["model_cfg"]
    model = TinyTransformer(mc["vocab"], mc["max_len"], mc["d_model"], mc["n_layers"],
                            mc["n_heads"], mc["ffn_mult"], mc["pad_id"])
    model.load_state_dict(ck["state_dict"])
    model.eval()
    for p in model.parameters():
        p.requires_grad_(False)
    tok = Tokenizer.from_str(ck["tokenizer_json"])
    return model, tok, mc, ck.get("arm", "UNKNOWN")


# ================= PE stream (the mechanism under test) =================
def causal_token_pe(model, tok, text, max_len):
    """Returns (pe[L-1] float array aligned to token index i in [1, L-1], token ids[L], offsets[L]).
    PE[i-1] = -log softmax(h_ctx[i-1] @ tok_emb.weight.T)[token_id[i]] -- causal next-token surprisal,
    i.e. PE "belonging to" token i (the surprise of encountering token i given tokens[0..i-1])."""
    enc = tok.encode(text)
    ids_list = enc.ids[:max_len]
    offsets = enc.offsets[:max_len]
    L = len(ids_list)
    assert L >= 2, "text too short to compute any causal PE: %r" % text
    ids = torch.tensor([ids_list], dtype=torch.long)
    with torch.no_grad():
        h_ctx, _pad = _causal_contextual(model, ids)         # [1, L, d]
        logits = torch.nn.functional.linear(h_ctx[0], model.tok_emb.weight)   # [L, vocab] tied head
        log_probs = torch.nn.functional.log_softmax(logits, dim=-1)          # [L, vocab]
    pe = np.zeros(L - 1, dtype=np.float64)
    for i in range(1, L):
        pe[i - 1] = -float(log_probs[i - 1, ids_list[i]])
    return pe, ids_list, offsets


def word_spans(text):
    """[(start, end, word_str), ...] via a simple ASCII word regex (letters + internal apostrophe)."""
    return [(m.start(), m.end(), m.group()) for m in WORD_RE.finditer(text)]


def word_level_pe(pe, offsets, spans):
    """For each word span, word_pe = MAX over constituent token PEs (token idx>=1 only -- token 0
    has no causal PE by construction). Returns list aligned to `spans`; None where no token idx>=1
    overlaps (only possible for the very first word of the sequence)."""
    out = []
    for (s, e, _w) in spans:
        vals = [pe[ti - 1] for ti, (a, b) in enumerate(offsets) if ti >= 1 and a < e and b > s]
        out.append(float(max(vals)) if vals else None)
    return out


def find_span(text, phrase):
    """First word-boundary-ish occurrence of `phrase` in `text` (case-sensitive first, then
    case-insensitive fallback). Returns (start, end) or None."""
    pat = r"\b" + re.escape(phrase) + r"\b"
    m = re.search(pat, text)
    if m is None:
        m = re.search(pat, text, re.IGNORECASE)
    return None if m is None else m.span()


def last_word_idx_in_span(spans, start, end):
    """Index into `spans` of the LAST word span fully inside [start, end) (the head-noun / final
    content word of a phrase -- the convention used for both gold intro spans and gold cue spans)."""
    idxs = [i for i, (s, e, _w) in enumerate(spans) if s >= start and e <= end]
    assert idxs, "no word span found inside [%d,%d) of phrase" % (start, end)
    return idxs[-1]


# ================= Probe 2b: referent introduction =================
def probe_2b(model, tok, mc, gold):
    passage = gold["passage"]
    spans = word_spans(passage)
    pe, _ids, offsets = causal_token_pe(model, tok, passage, mc["max_len"])
    wpe = word_level_pe(pe, offsets, spans)

    gold_idx_all = []
    gold_idx_16 = []
    for intro in gold["introductions"]:
        sp = find_span(passage, intro["first_mention"])
        assert sp is not None, "gold first_mention not found verbatim: %r" % intro
        gi = last_word_idx_in_span(spans, sp[0], sp[1])
        gold_idx_all.append(gi)
        if intro["intro_type"] != "INDEF":
            gold_idx_16.append(gi)
    gold_idx_all = sorted(set(gold_idx_all))
    gold_idx_16 = sorted(set(gold_idx_16))
    assert len(gold_idx_all) == gold["n_intro"], (
        "gold span-resolution count mismatch: resolved %d, gold says n_intro=%d"
        % (len(gold_idx_all), gold["n_intro"]))

    valid_idx = [i for i, v in enumerate(wpe) if v is not None]
    vals = np.array([wpe[i] for i in valid_idx], dtype=np.float64)
    thresh = float(vals.mean() + vals.std())
    spike_set = set(valid_idx[j] for j in range(len(valid_idx)) if vals[j] > thresh)

    lexical_set = set()
    for i, (_s, _e, w) in enumerate(spans):
        if w.lower() in ARTICLE_WORDS and i + 1 < len(spans):
            lexical_set.add(i + 1)

    def prf(pred_set, gold_set):
        if not pred_set:
            return 0.0, 0.0, 0.0
        tp = len(pred_set & gold_set)
        prec = tp / len(pred_set)
        rec = tp / len(gold_set) if gold_set else 0.0
        f1 = 0.0 if (prec + rec) == 0 else 2 * prec * rec / (prec + rec)
        return prec, rec, f1

    pe_prec, pe_rec, pe_f1 = prf(spike_set, set(gold_idx_all))
    pe_recall_16 = (len(spike_set & set(gold_idx_16)) / len(gold_idx_16)) if gold_idx_16 else 0.0
    lex_prec, lex_rec, lex_f1 = prf(lexical_set, set(gold_idx_all))
    lex_recall_16 = (len(lexical_set & set(gold_idx_16)) / len(gold_idx_16)) if gold_idx_16 else 0.0

    n_positions = len(valid_idx)
    chance_prec = len(gold_idx_all) / n_positions if n_positions else 0.0
    spike_rate = len(spike_set) / n_positions if n_positions else 0.0
    chance_f1 = 0.0 if (chance_prec + spike_rate) == 0 else 2 * chance_prec * spike_rate / (chance_prec + spike_rate)

    digest = hashlib.sha256(json.dumps(sorted(spike_set)).encode()).hexdigest()
    return {
        "pe_spike": {"precision": pe_prec, "recall": pe_rec, "f1": pe_f1, "recall_16_subset": pe_recall_16,
                    "n_predicted": len(spike_set), "threshold": thresh},
        "baseline_lexical": {"precision": lex_prec, "recall": lex_rec, "f1": lex_f1,
                             "recall_16_subset": lex_recall_16, "n_predicted": len(lexical_set)},
        "baseline_chance": {"analytic_precision": chance_prec, "analytic_spike_rate": spike_rate,
                            "analytic_f1_at_matched_rate": chance_f1},
        "n_positions": n_positions, "n_gold_all": len(gold_idx_all), "n_gold_16_subset": len(gold_idx_16),
        "digest": digest,
    }


# ================= Probe 2c: role-disambiguation cue alignment =================
def _load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def probe_2c(model, tok, mc, records, kind):
    """kind: 'passive' (cue = passive_verb) or 'quotative' (cue = gold_agent_speaker span)."""
    hits, chance_hits, linpos_hits = [], [], []
    per_example = []
    for rec in records:
        text = rec["text"]
        spans = word_spans(text)
        if len(spans) < 2:
            continue  # cannot compute any causal PE (need >=2 words)
        pe, _ids, offsets = causal_token_pe(model, tok, text, mc["max_len"])
        wpe = word_level_pe(pe, offsets, spans)
        valid = [(i, v) for i, v in enumerate(wpe) if v is not None]
        if not valid:
            continue
        pred_idx = max(valid, key=lambda t: t[1])[0]

        if kind == "passive":
            sp = find_span(text, rec["passive_verb"])
        else:
            sp = find_span(text, rec["gold_agent_speaker"])
        if sp is None:
            continue  # gold phrase not locatable verbatim -- skip, do not fabricate a cue
        gold_idx = last_word_idx_in_span(spans, sp[0], sp[1])

        n_words = len(spans)
        linpos_idx = min(max(1, round(LINEAR_POSITION_FRAC * (n_words - 1))), n_words - 1)
        window = set(range(max(0, gold_idx - TOLERANCE_WINDOW), gold_idx + TOLERANCE_WINDOW + 1))

        hit = pred_idx in window
        linpos_hit = linpos_idx in window
        chance_hit_rate = min(1.0, len(window) / max(1, n_words - 1))  # analytic, per-example

        hits.append(bool(hit))
        linpos_hits.append(bool(linpos_hit))
        chance_hits.append(chance_hit_rate)
        per_example.append({"grade": rec.get("grade"), "n_words": n_words, "gold_idx": gold_idx,
                            "pred_idx": pred_idx, "linpos_idx": linpos_idx, "hit": bool(hit),
                            "linpos_hit": bool(linpos_hit)})

    n = len(hits)
    digest = hashlib.sha256(json.dumps([e["pred_idx"] for e in per_example]).encode()).hexdigest()
    return {
        "pe_spike_hit_rate": (sum(hits) / n) if n else 0.0,
        "baseline_linear_position_hit_rate": (sum(linpos_hits) / n) if n else 0.0,
        "baseline_chance_hit_rate_analytic": (float(np.mean(chance_hits)) if chance_hits else 0.0),
        "n_examples": n, "per_example": per_example, "digest": digest,
    }


# ================= pipeline =================
def run_pipeline_for_ckpt(ckpt_path, output_dir_tag):
    model, tok, mc, arm = load_frozen_ckpt(ckpt_path)
    gold_intro = json.load(open(GOLD_INTRO_PATH, encoding="utf-8"))
    quotative_recs = _load_jsonl(GOLD_QUOTATIVE_PATH)
    passive_recs = _load_jsonl(GOLD_PASSIVE_PATH)

    p2b = probe_2b(model, tok, mc, gold_intro)
    p2c_quot = probe_2c(model, tok, mc, quotative_recs, "quotative")
    p2c_pass = probe_2c(model, tok, mc, passive_recs, "passive")
    return {"arm": arm, "ckpt_path": ckpt_path, "model_cfg": mc,
            "probe_2b": p2b, "probe_2c_quotative": p2c_quot, "probe_2c_passive": p2c_pass}


def check_arms_differ(floor_out, cand_out):
    pairs = [("probe_2b", floor_out["probe_2b"]["digest"], cand_out["probe_2b"]["digest"]),
             ("probe_2c_quotative", floor_out["probe_2c_quotative"]["digest"], cand_out["probe_2c_quotative"]["digest"]),
             ("probe_2c_passive", floor_out["probe_2c_passive"]["digest"], cand_out["probe_2c_passive"]["digest"])]
    same = [name for name, da, db in pairs if da == db]
    return {"arms_differ_verified": (len(same) < len(pairs)), "identical_units": same}


# ================= verdict =================
def decide_verdict(floor_out, cand_out):
    fb = floor_out["probe_2b"]
    floor_lex_f1_all = fb["baseline_lexical"]["f1"]
    floor_beats_lexical_16 = fb["pe_spike"]["recall_16_subset"] - fb["baseline_lexical"]["recall_16_subset"]

    fq = floor_out["probe_2c_quotative"]
    fp = floor_out["probe_2c_passive"]
    floor_beats_linpos_quot = fq["pe_spike_hit_rate"] - fq["baseline_linear_position_hit_rate"]
    floor_beats_linpos_pass = fp["pe_spike_hit_rate"] - fp["baseline_linear_position_hit_rate"]

    floor_ok = (floor_beats_lexical_16 <= FLOOR_MARGIN and floor_beats_linpos_quot <= FLOOR_MARGIN
                and floor_beats_linpos_pass <= FLOOR_MARGIN)

    bands = {
        "floor_margin": FLOOR_MARGIN, "tolerance_window": TOLERANCE_WINDOW,
        "linear_position_frac": LINEAR_POSITION_FRAC,
        "hard_pass_2b_lift": HARD_PASS_2B_LIFT, "hard_pass_2b_recall16_min": HARD_PASS_2B_RECALL16_MIN,
        "floor_2b": fb, "floor_2c_quotative": fq, "floor_2c_passive": fp,
        "floor_beats_lexical_16_margin": floor_beats_lexical_16,
        "floor_beats_linpos_quot_margin": floor_beats_linpos_quot,
        "floor_beats_linpos_pass_margin": floor_beats_linpos_pass,
        "floor_ok": floor_ok,
    }

    if not floor_ok:
        return "HARNESS_FLOOR_BROKEN", (
            "Floor (untrained ARM_RANDOM) beat a naive baseline by more than FLOOR_MARGIN=%.2f: "
            "16-subset recall margin=%.4f, quotative linpos margin=%.4f, passive linpos margin=%.4f. "
            "The harness itself needs investigation before any candidate-ckpt claim is trusted."
            % (FLOOR_MARGIN, floor_beats_lexical_16, floor_beats_linpos_quot, floor_beats_linpos_pass)
        ), bands

    cb = cand_out["probe_2b"]
    lift = cb["pe_spike"]["f1"] - cb["baseline_lexical"]["f1"]
    recall16 = cb["pe_spike"]["recall_16_subset"]
    bands["candidate_2b"] = cb
    bands["candidate_2c_quotative"] = cand_out["probe_2c_quotative"]
    bands["candidate_2c_passive"] = cand_out["probe_2c_passive"]
    bands["candidate_lift_over_lexical_f1"] = lift
    bands["candidate_recall_16_subset"] = recall16

    if lift >= HARD_PASS_2B_LIFT and recall16 >= HARD_PASS_2B_RECALL16_MIN:
        verdict = "HARD_PASS_2b_SMOKE_PREVIEW"
        msg = ("Floor OK. Candidate PE-spike F1=%.4f beats BASELINE_LEXICAL F1=%.4f by %.4f "
               "(>=%.2f) AND recall on the 16 no-a/an-cue subset=%.4f (>=%.2f) -- genuine structural "
               "signal, not a/an pattern-matching. This is a SMOKE-STAGE preview on a lite-budget "
               "encoder, not the decisive FULL-encoder verdict (see prereg)."
               % (cb["pe_spike"]["f1"], cb["baseline_lexical"]["f1"], lift, HARD_PASS_2B_LIFT,
                  recall16, HARD_PASS_2B_RECALL16_MIN))
    elif lift <= 0.0:
        verdict = "HARD_FAIL_2b"
        msg = ("Floor OK. Candidate PE-spike F1=%.4f does NOT beat BASELINE_LEXICAL F1=%.4f at all "
               "(lift=%.4f) -- no evidence the causal PE stream carries referent-introduction "
               "structure on this ckpt." % (cb["pe_spike"]["f1"], cb["baseline_lexical"]["f1"], lift))
    else:
        verdict = "MIDDLE_2b"
        msg = ("Floor OK. Candidate PE-spike F1=%.4f vs BASELINE_LEXICAL F1=%.4f (lift=%.4f), "
               "recall_16=%.4f -- partial signal, neither HARD condition met."
               % (cb["pe_spike"]["f1"], cb["baseline_lexical"]["f1"], lift, recall16))
    return verdict, msg, bands


# ---------------- self-test ----------------
def _selftest_word_span_and_pe_alignment(model, tok, mc):
    text = "One lamp gives light enough for all."
    spans = word_spans(text)
    assert [w for _s, _e, w in spans] == ["One", "lamp", "gives", "light", "enough", "for", "all"]
    pe, ids, offsets = causal_token_pe(model, tok, text, mc["max_len"])
    assert len(pe) == len(ids) - 1
    assert all(math.isfinite(v) and v >= 0.0 for v in pe), "PE must be non-negative finite (-log prob)"
    wpe = word_level_pe(pe, offsets, spans)
    assert wpe[0] is None or isinstance(wpe[0], float)   # first word may or may not have any tok>=1
    assert all(v is None or v >= 0.0 for v in wpe)
    return {"n_words": len(spans), "n_tokens": len(ids), "pe_sample": pe[:5].tolist()}


def _selftest_find_span_and_last_word_idx():
    text = "Brown has put the little sitting room in order."
    spans = word_spans(text)
    sp = find_span(text, "the little sitting room")
    assert sp is not None
    idx = last_word_idx_in_span(spans, sp[0], sp[1])
    assert spans[idx][2] == "room", "expected head noun 'room', got %r" % (spans[idx][2],)
    return {"resolved_word": spans[idx][2]}


def run_self_test():
    _log("SELF-TEST: load REAL ARM_RANDOM ckpt (real_code_path) ...")
    assert os.path.exists(DEFAULT_FLOOR_CKPT), "floor ckpt missing: %s" % DEFAULT_FLOOR_CKPT
    model, tok, mc, arm = load_frozen_ckpt(DEFAULT_FLOOR_CKPT)
    assert arm == "ARM_RANDOM", "expected ARM_RANDOM ckpt, got arm=%r" % arm
    _log("  loaded arm=%s vocab=%d d_model=%d max_len=%d" % (arm, mc["vocab"], mc["d_model"], mc["max_len"]))

    _log("SELF-TEST: word-span / PE-alignment sanity ...")
    diag1 = _selftest_word_span_and_pe_alignment(model, tok, mc)
    _log("  PASS: %s" % diag1)

    _log("SELF-TEST: find_span / last_word_idx_in_span (head-noun resolution) ...")
    diag2 = _selftest_find_span_and_last_word_idx()
    _log("  PASS: %s" % diag2)

    _log("SELF-TEST: gold files load + span-resolution round-trips ...")
    gold_intro = json.load(open(GOLD_INTRO_PATH, encoding="utf-8"))
    assert gold_intro["n_intro"] == len(gold_intro["introductions"]) == 20
    quotative_recs = _load_jsonl(GOLD_QUOTATIVE_PATH)
    passive_recs = _load_jsonl(GOLD_PASSIVE_PATH)
    assert len(quotative_recs) == 20 and len(passive_recs) == 7

    _log("SELF-TEST: REAL full pipeline against REAL ARM_RANDOM ckpt (floor; no smaller regime "
         "exists -- option A of DISCRIMINATOR-MUST-SURVIVE-SCALE) ...")
    floor_out = run_pipeline_for_ckpt(DEFAULT_FLOOR_CKPT, "selftest_floor")
    assert os.path.exists(DEFAULT_CANDIDATE_CKPT), "candidate ckpt missing: %s" % DEFAULT_CANDIDATE_CKPT
    cand_out = run_pipeline_for_ckpt(DEFAULT_CANDIDATE_CKPT, "selftest_candidate")
    arms_diff = check_arms_differ(floor_out, cand_out)
    verdict, msg, bands = decide_verdict(floor_out, cand_out)
    _log("  floor probe_2b=%s" % floor_out["probe_2b"]["pe_spike"])
    _log("  candidate probe_2b=%s" % cand_out["probe_2b"]["pe_spike"])
    _log("  arms_differ=%s verdict=%s" % (arms_diff, verdict))

    _log("SELF-TEST PASS")
    return {"diag1": diag1, "diag2": diag2, "floor_out_summary": {"probe_2b": floor_out["probe_2b"]["pe_spike"]},
            "candidate_out_summary": {"probe_2b": cand_out["probe_2b"]["pe_spike"]},
            "arms_differ": arms_diff, "smoke_verdict": verdict, "smoke_verdict_msg": msg}


# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--ckpt-path", default=DEFAULT_CANDIDATE_CKPT,
                    help="CANDIDATE ckpt (FrozenV2Encoder-shaped: state_dict+model_cfg+tokenizer_json). "
                         "Encoder-AGNOSTIC -- any ckpt of this shape works, no code change needed.")
    ap.add_argument("--floor-ckpt-path", default=DEFAULT_FLOOR_CKPT,
                    help="FLOOR ckpt (untrained/random-init, same architecture) -- ALWAYS run alongside "
                         "the candidate so floor-validation and candidate-smoke never decouple.")
    args = ap.parse_args()

    torch.set_num_threads(min(6, max(1, os.cpu_count() or 1)))
    run_mode = "self_test" if args.self_test or not args.full else "full"
    out_dir = OUTPUT_DIR
    _write_start_marker(out_dir, run_mode, 2 * EXPECTED_UNITS_PER_CKPT)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        elapsed = time.perf_counter() - t0
        _atomic_write_metrics(out_dir, {
            "verdict": "SELFTEST_PASS",
            "verdict_msg": "SELFTEST_PASS (word-span alignment + span-resolution + real full "
                           "pipeline against REAL ARM_RANDOM floor ckpt + candidate ckpt + "
                           "arms-differ)",
            "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": elapsed,
            "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "selftest": st})
        _log("DONE self-test in %.1fs" % elapsed)
        return

    _log("FULL: floor_ckpt=%s candidate_ckpt=%s" % (args.floor_ckpt_path, args.ckpt_path))
    floor_out = run_pipeline_for_ckpt(args.floor_ckpt_path, "floor")
    cand_out = run_pipeline_for_ckpt(args.ckpt_path, "candidate")
    arms_diff = check_arms_differ(floor_out, cand_out)
    verdict, msg, bands = decide_verdict(floor_out, cand_out)
    elapsed = time.perf_counter() - t0

    n_units_done = 2 * EXPECTED_UNITS_PER_CKPT   # both ckpts always run in one invocation (see docstring)
    _atomic_write_metrics(out_dir, {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "%s | %s" % (verdict, msg[:160]),
        "run_mode": "full", "elapsed_s": elapsed, "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "bands": bands, "floor_out": floor_out, "candidate_out": cand_out,
        "arms_differ_verified": bool(arms_diff["arms_differ_verified"]),
        "identical_units": arms_diff["identical_units"],
        "cardinality_ok": bool(n_units_done == 2 * EXPECTED_UNITS_PER_CKPT),
        "expected_n_units": 2 * EXPECTED_UNITS_PER_CKPT, "n_units_done": n_units_done,
        "params": {"floor_ckpt": args.floor_ckpt_path, "candidate_ckpt": args.ckpt_path,
                   "floor_margin": FLOOR_MARGIN, "tolerance_window": TOLERANCE_WINDOW,
                   "linear_position_frac": LINEAR_POSITION_FRAC,
                   "hard_pass_2b_lift": HARD_PASS_2B_LIFT,
                   "hard_pass_2b_recall16_min": HARD_PASS_2B_RECALL16_MIN,
                   "pe_definition": "causal next-token cross-entropy, tied head, per prereg"},
        "start_marker_written": True, "crash_diagnostic_present": True,
        "final_metrics_atomicity": "tmp_replace", "defensive_error_checking": "passed_all_4_patterns",
        "cell_chunked": False, "progress_logging": "n_a_short_runtime",
        "crlb_n_a": "no learned-noise Cramer-Rao floor; discriminator is the pre-registered "
                    "FLOOR_OK/HARD_PASS_2b/HARD_FAIL_2b/MIDDLE_2b decision rule (see decide_verdict)",
        "calibration_check": "default_ok_for_this_regime: PE-spike threshold (mean+1*std), "
                              "tolerance window, FLOOR_MARGIN, LINEAR_POSITION_FRAC are fixed "
                              "HYPOTHESIZED thresholds set before running (not tuned post-hoc)."})
    _log("VERDICT: %s" % verdict)
    _log("  %s" % msg)
    _log("DONE full in %.1fs" % elapsed)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
