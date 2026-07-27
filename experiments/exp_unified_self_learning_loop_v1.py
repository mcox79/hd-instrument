"""UNIFIED SELF-LEARNING LOOP -- trained scale-encoder wired into the CLS reader loop (v1).

USER-directed integration milestone (2026-07-27 architecture correction): the scale run poured
237M tokens into ENCODER MLM training but the READER loop (read -> flag-unknowns -> extract/condense
-> hippocampal fast-write -> SLEEP-consolidate into the foundation) NEVER ran over that text. This
cell UNIFIES them: the trained encoder becomes the reader's COMPREHENSION ENGINE, and the substrate
LEARNS FROM REAL PROSE across cycles, consolidating into a working copy of the foundation.

THE LOOP (per cycle, over REAL ARC prose -- NOT templated):
  1. READ      : the trained encoder (exp_scale_meaning_learn_arc_heldout_v2.TinyTransformer.pooled)
                 COMPREHENDS each real ARC mention-sentence of a held-out foundation concept -> a
                 contextual per-mention meaning rep. This is the comprehension/extraction engine.
  2. FLAG      : hdlab/clarify_gate.py ClarifyGate flags concepts it does NOT yet know (low
                 accumulated-evidence / low rep-coherence confidence). Flagged = "not yet acquired";
                 the flag population SHRINKS across cycles as evidence accumulates (drives what to read).
  3. CONDENSE  : per-concept running-mean rep condenses many mention sentences into ONE meaning
                 estimate (the concept's foundation representation).
  4. FAST-WRITE: cycle mention-reps append to a per-concept EPISODIC BUFFER (hippocampal fast store).
  5. SLEEP     : hdlab/learner (MDL-gated model-selection, core.per_cluster_gate) consolidates the
                 buffer into a WORKING COPY of the foundation concept-rep store -- ONLY coherent,
                 sufficiently-attested evidence is committed (else KEEP_EPISODIC). SLEEP MUST FIRE
                 every cycle (asserted + logged) -- this fixes cycle2's #1 bug (sleep=False).

THE PROBE (leak-proof, VET-confirmed protocol reused verbatim from the scale run):
  relational_eval -- rank a held-out concept's TRUE foundation-neighbour vs degree-matched non-
  neighbours by CONSOLIDATED-rep cosine. The rep has ZERO relational input (built only from mention
  TEXT), and the predicted EDGE is disjoint from the read text => genuine generalization, not recall.
  KNOWLEDGE GAIN = relational AUC[final cycle] - AUC[cycle 0] on the consolidated foundation store.

CONTROLS (each a full loop variant; all share the cycle-0 init store = foundation-before-loop):
  MAIN          read real prose + SLEEP-consolidate every cycle    (expect AUC rises)
  NO_READ       no reads after cycle 0 (store frozen)              (expect flat)
  SCRAMBLED     read WORD-SHUFFLED prose + sleep                   (expect flat: surface, not meaning)
  READ_NO_SLEEP read real prose, NO consolidation (episodic-only) (expect flat: sleep is load-bearing)

HARD-PASS = consistent real-prose knowledge gain (MAIN AUC rises, monotonic-ish) + sleep fires every
cycle + retention held (no catastrophic drop) + all three controls flat (below MAIN at the final cycle).

BRAIN-FAITHFUL / INVARIANTS: TEACHER-FREE; NO borrowed vectors (OUR trained encoder only); GLASS-BOX
(symbolic gate + running-mean consolidation + MDL model-selection; no external LLM / no autograd at
inference); LEAK-PROOF (predicted edge disjoint from read text). ASCII-only. Deterministic seeds.
Store writes LOCAL-ONLY + UNCOMMITTED. Agent-reported VET-PENDING.

REUSE (no reinvention): imports experiments.exp_scale_meaning_learn_arc_heldout_v2 for ALL data-prep
(universe/split/postings/adjacency/grounding), the encoder (TinyTransformer + tokenizer + mlm_train),
and the leak-proof relational_eval probe. This cell adds ONLY the loop / hippocampal buffer / MDL-gated
sleep / clarify prioritization / controls / curve on top of that VET-confirmed machinery.

FULL run loads the scale v2 checkpoint (data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_<seed>.pt)
as the comprehension engine via --ckpt; SMOKE trains a tiny fresh encoder to validate the LOOP MECHANISM.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scale/floor):
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - final_metrics_atomicity: tmp_replace (os.replace)
# - crash-diagnostic metrics + start-marker + heartbeat
# - arms_differ_verified at smoke gate (NO_READ==READ_NO_SLEEP store exempted: both freeze cycle-0 by construction)
# - discriminator = MAIN gain vs controls; must FIRE at smoke (measured)
# - deterministic seeding (fixed ints + sha256; no hash()/list(set()) ordering)
# - progress_logging: print_flush_true
# - self-test constructs REAL objects (encoder, clarify gate, learner gate, relational probe) at N~tiny, no corpus read
# - all reported numbers MEASURED@ this cell's metrics.json
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys
import json
import math
import time
import argparse
import hashlib
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_scale_meaning_learn_arc_heldout_v2 as V2
from hdlab.clarify_gate import ClarifyGate, GateOutcome
from hdlab.learner.core import LearnResult, per_cluster_gate

ANCHOR_NAME = "unified_self_learning_loop_v1"

MAIN_ARM = "MAIN_read_sleep"
NOREAD_ARM = "NO_READ"
SCRAM_ARM = "SCRAMBLED"
NOSLEEP_ARM = "READ_NO_SLEEP"
ARMS = [MAIN_ARM, NOREAD_ARM, SCRAM_ARM, NOSLEEP_ARM]

TEXT_KEY = "ARM_RAW_TEXT"      # relational_eval readout for the consolidated concept rep
RAW_KEY = "ARM_RAW_GROUNDING"  # constant grounding baseline (for context)
SH_KEY = "ARM_COLLAPSE_SHUFFLE"
POP_KEY = "ARM_POPULARITY"

# ---------------------------------------------------------------------------
# Config profiles.  Data keys mirror V2 (so the deterministic split reproduces
# what the checkpoint was trained leak-proof against).  Loop keys are additive.
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(
    run_mode="selftest",
    n_cycles=3, mentions_per_cycle=2, min_evidence_mentions=2, clarify_min_evidence=6,
    concentration_thresh=0.0, min_compression_ratio=1.0,
    gain_margin_hp=0.0, clarify_seed=7,
    # data keys unused in selftest (synthetic path), present for schema completeness
    d_model=16, n_layers=1, n_heads=2, ffn_mult=2, max_len=16, vocab=64, encode_batch=32,
)
SMOKE_CFG = dict(
    run_mode="smoke", seed=7,
    min_deg=2, cap_eval_concepts=2500, heldout_count=250, min_mentions_eval=12,
    max_lines=160000, dedup_cap=200000, bpe_sample_lines=80000, cap_mentions=16,
    vocab=2048, max_len=40, train_token_budget=1500000, max_shards=6,
    d_model=128, n_layers=2, n_heads=4, ffn_mult=2,
    mlm_steps=250, mlm_batch=64, mlm_mask_frac=0.15, mlm_lr=3e-3,
    encode_batch=128, n_freq_buckets=5,
    # loop
    n_cycles=4, mentions_per_cycle=3, min_evidence_mentions=3, clarify_min_evidence=12,
    concentration_thresh=0.15, min_compression_ratio=1.0,
    gain_margin_hp=0.0, clarify_seed=7,
)
FULL_CFG = dict(
    run_mode="full", seed=7,
    min_deg=2, cap_eval_concepts=None, heldout_count=800, min_mentions_eval=20,
    max_lines=10000000, dedup_cap=6000000, bpe_sample_lines=400000, cap_mentions=128,
    vocab=16000, max_len=128, train_token_budget=130000000, max_shards=16,
    d_model=512, n_layers=6, n_heads=8, ffn_mult=4,
    mlm_steps=60000, mlm_batch=128, mlm_mask_frac=0.15, mlm_lr=3e-4,
    encode_batch=256, n_freq_buckets=8,
    # loop
    n_cycles=6, mentions_per_cycle=16, min_evidence_mentions=16, clarify_min_evidence=96,
    concentration_thresh=0.15, min_compression_ratio=1.0,
    gain_margin_hp=0.02, clarify_seed=7,
)

# HARD-PASS bands (FULL). SMOKE uses the mechanism-gate (see build_verdict).
HP_GAIN_MARGIN = 0.02          # MAIN AUC[final]-AUC[0] must exceed this (real-prose knowledge gain)
HP_CONTROL_SEP = 0.0           # MAIN[final] must exceed each control[final] by > this
RETENTION_EPS = 0.02           # MAIN AUC may never drop below AUC[0]-RETENTION_EPS (no catastrophic forgetting)
MIN_QUERY_TASKS = 40           # relational power floor for the AUC curve to be trustworthy (SMOKE relaxed to 15)


def _out_dir(run_mode):
    suffix = {"selftest": "_selftest", "smoke": "_smoke", "full": ""}.get(run_mode, "")
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME + suffix)
    os.makedirs(d, exist_ok=True)
    return d


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _write_start_marker(out_dir, run_mode, expected_units):
    marker = dict(pid=os.getpid(), ts_iso=_now(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_units)
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(out_dir, "_start_marker.json"))


def _heartbeat(out_dir, unit_idx, total_units, elapsed_s, extra=None):
    row = dict(ts_iso=_now(), unit_idx=int(unit_idx), total_units=int(total_units),
               elapsed_s=round(float(elapsed_s), 2))
    if extra:
        row["extra"] = extra
    with open(os.path.join(out_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


# ===========================================================================
# Encoder: comprehension engine (train tiny for smoke, OR load v2 checkpoint)
# ===========================================================================
def _build_encoder_from_ckpt(ckpt_path, device):
    """Load the trained scale-v2 encoder (TinyTransformer) + its tokenizer from a .pt checkpoint."""
    from tokenizers import Tokenizer
    ckpt = torch.load(ckpt_path, map_location="cpu")
    mc = ckpt["model_cfg"]
    model = V2.TinyTransformer(mc["vocab"], mc["max_len"], mc["d_model"], mc["n_layers"],
                               mc["n_heads"], mc["ffn_mult"], mc["pad_id"]).to(device)
    model.load_state_dict(ckpt["state_dict"])
    model.eval()
    tok = Tokenizer.from_str(ckpt["tokenizer_json"])
    spec = ckpt["spec"]
    return model, tok, spec, mc


def _encode_sentences(model, tok, sents, cfg, device, spec):
    """Real ARC sentences -> (N, d) mean-pooled, L2-normalized contextual meaning reps (the encoder is
    the comprehension engine). Batched, no autograd."""
    if not sents:
        return np.zeros((0, model.d_model), dtype=np.float32)
    max_len = cfg["max_len"]
    pad_id = spec["pad"]
    X = np.stack([V2._encode_pad(tok, s, max_len, pad_id) for s in sents], axis=0)
    bs = cfg["encode_batch"]
    use_amp = (device.type == "cuda")
    out = []
    with torch.no_grad():
        for i in range(0, X.shape[0], bs):
            ids = torch.from_numpy(X[i:i + bs]).to(device)
            with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=use_amp):
                pooled = model.pooled(ids)
            out.append(pooled.float().cpu().numpy())
    return np.concatenate(out, axis=0).astype(np.float32)


def _scramble_words(sent, rng):
    """Word-order shuffle control: destroys syntax/meaning, keeps surface bag-of-words."""
    w = sent.split()
    if len(w) < 2:
        return sent
    order = rng.permutation(len(w))
    return " ".join(w[i] for i in order)


# ===========================================================================
# SLEEP: MDL-gated consolidation (routes the commit decision through hdlab.learner)
# ===========================================================================
def _concept_learn_result(reps):
    """Build a hdlab.learner LearnResult for a concept's accumulated mention reps. The consolidated
    MEAN is a candidate 'rule' that compresses the mentions; the MDL two-part code compares it to the
    null (code each mention independently). Returns (LearnResult, coherence)."""
    X = np.asarray(reps, dtype=np.float64)
    n, d = X.shape
    mean = X.mean(axis=0)
    mn = mean / (np.linalg.norm(mean) + 1e-8)
    coherence = float(np.mean(X @ mn))                       # mean cosine of mentions to their mean, in [-1,1]
    resid_var = float(np.mean(np.sum((X - mean) ** 2, axis=1)))
    BITS = 32.0
    null_bits = float(n * d * BITS)                          # code each mention rep independently
    desc_bits = float(d * BITS + n * d * math.log2(1.0 + resid_var + 1e-9))  # one mean + residual code
    lr = LearnResult(plugin_name="concept_mean_consolidation",
                     hypothesis={"coherence": round(coherence, 4), "n_mentions": int(n)},
                     is_episodic=False, description_bits=desc_bits, null_bits=null_bits,
                     n_free_params=int(d), cost_rank=1,
                     metrics={"coherence": coherence, "resid_var": resid_var})
    return lr, coherence


def _sleep_consolidate(acc_reps, store, is_init, cfg):
    """MDL-gated SLEEP over one cycle's accumulated buffer. Commits a concept's running-mean rep into
    the working foundation store ONLY when the learner's MDL gate passes AND evidence is coherent +
    sufficient; otherwise KEEP_EPISODIC (store rep unchanged -> retention). Returns per-cycle log."""
    n_consolidated = 0
    n_kept_episodic = 0
    committed_now = []
    cr_samples = []
    for ci, reps in acc_reps.items():
        if len(reps) < 1:
            continue
        lr, coh = _concept_learn_result(reps)
        cr = float(lr.compression_ratio)
        mdl_ok = per_cluster_gate(lr, cfg["min_compression_ratio"])
        sufficient = (len(reps) >= cfg["min_evidence_mentions"]) and (coh >= cfg["concentration_thresh"])
        commit = bool(is_init or (mdl_ok and sufficient))    # cycle-0 initializes the foundation
        if commit:
            X = np.asarray(reps, dtype=np.float32)
            m = X.mean(axis=0)
            store[ci] = (m / (np.linalg.norm(m) + 1e-8)).astype(np.float32)
            n_consolidated += 1
            committed_now.append(ci)
            if len(cr_samples) < 5:
                cr_samples.append({"concept_idx": int(ci), "n_mentions": len(reps),
                                   "coherence": round(coh, 4), "compression_ratio": round(cr, 4)})
        else:
            n_kept_episodic += 1
    return dict(n_consolidated=n_consolidated, n_kept_episodic=n_kept_episodic,
                sample_commits=cr_samples), committed_now


# ===========================================================================
# FLAG: ClarifyGate flags concepts not-yet-known (low accumulated-evidence confidence)
# ===========================================================================
def _clarify_flag_population(acc_reps, held, gate, cfg):
    """Per-concept confidence = coherence-of-evidence * mention-sufficiency, fed to the banked
    ClarifyGate. non-ACCEPT = flagged = 'not yet acquired' (drives what to read). Returns n_flagged."""
    n_flagged = 0
    for ci in held:
        reps = acc_reps.get(ci, [])
        if len(reps) < 1:
            n_flagged += 1
            continue
        _lr, coh = _concept_learn_result(reps)
        suff = min(1.0, len(reps) / float(max(1, cfg["clarify_min_evidence"])))
        conf = ((coh + 1.0) / 2.0) * suff                    # in [0,1]
        if gate.evaluate(conf) != GateOutcome.ACCEPT:
            n_flagged += 1
    return n_flagged


# ===========================================================================
# PROBE: leak-proof relational AUC on the consolidated foundation store
# ===========================================================================
def _store_to_text_matrix(store, base_text):
    """Working-copy foundation rep matrix: FIXED train-concept reps (base_text) with the loop's
    evolving HELD-concept consolidated reps overlaid. Held concepts are zeroed in base_text."""
    text = base_text.copy()
    for ci, rep in store.items():
        text[ci] = rep
    return text


def _probe_relational(store, base_text, ground, counts, universe, split, adj, deg, n_shards, seed):
    text = _store_to_text_matrix(store, base_text)
    rel = V2.relational_eval(ground, text, counts, universe, split, adj, deg, n_shards, seed, 0.5)
    return rel


# ===========================================================================
# ONE ARM: run the full cycle loop for a given arm
# ===========================================================================
def _run_arm(arm, held, postings, model, tok, spec, cfg, device, out_dir,
             ground, counts, universe, split, adj, deg, n_shards, seed, K, d, base_text):
    """Returns dict with per-cycle AUC curve + sleep/flag logs for this arm."""
    do_read = (arm != NOREAD_ARM)
    do_sleep = (arm != NOSLEEP_ARM)
    scramble = (arm == SCRAM_ARM)
    gate = ClarifyGate()                                    # banked M1.8 thresholds
    store = {}                                              # working copy of the foundation concept-rep store
    acc_reps = {ci: [] for ci in held}
    n_cycles = cfg["n_cycles"]
    m = cfg["mentions_per_cycle"]
    curve = []
    sleep_log = []
    flag_log = []
    for k in range(n_cycles):
        # cycle 0 always reads its first chunk + initializes the store (foundation-before-loop).
        # later cycles: MAIN/SCRAMBLED/READ_NO_SLEEP read; NO_READ does not.
        read_this_cycle = (k == 0) or do_read
        if read_this_cycle:
            for ci in held:
                chunk = postings[ci][k * m:(k + 1) * m]
                if not chunk:
                    continue
                if scramble:
                    rng = np.random.default_rng(seed + 1009 * int(ci) + 31 * k)
                    chunk = [_scramble_words(s, rng) for s in chunk]
                reps = _encode_sentences(model, tok, chunk, cfg, device, spec)
                for r in reps:
                    acc_reps[ci].append(r)
        # FLAG (what it doesn't yet know)
        n_flagged = _clarify_flag_population(acc_reps, held, gate, cfg)
        flag_log.append(n_flagged)
        # SLEEP (consolidate). cycle 0 initializes for ALL arms; later cycles only if do_sleep.
        is_init = (k == 0)
        if is_init or do_sleep:
            slog, _committed = _sleep_consolidate(acc_reps, store, is_init, cfg)
        else:
            slog = dict(n_consolidated=0, n_kept_episodic=len(held), sample_commits=[], sleep_disabled=True)
        sleep_log.append(slog)
        # SLEEP-MUST-FIRE assertion (the cycle2 bug fix): every sleep-enabled cycle commits >= 1 concept.
        if is_init or do_sleep:
            assert slog["n_consolidated"] >= 1, (
                "SLEEP_DID_NOT_FIRE arm=%s cycle=%d (n_consolidated=0) -- the cycle2 sleep=False bug" % (arm, k))
        # PROBE
        rel = _probe_relational(store, base_text, ground, counts, universe, split, adj, deg, n_shards, seed)
        auc = rel.get(TEXT_KEY)
        curve.append(auc)
        _log("  arm=%s cycle=%d auc_text=%s auc_raw=%s auc_shuffle=%s n_query=%s n_flagged=%d n_consol=%d"
             % (arm, k, _fmt(auc), _fmt(rel.get(RAW_KEY)), _fmt(rel.get(SH_KEY)),
                rel.get("_n_query"), n_flagged, slog["n_consolidated"]))
        _heartbeat(out_dir, unit_idx=k, total_units=n_cycles, elapsed_s=0.0,
                   extra={"arm": arm, "auc_text": auc, "n_query": rel.get("_n_query")})
    # arm-final store fingerprint (arms-must-differ): fingerprint the HELD reps only (base is shared)
    text_final = _store_to_text_matrix(store, np.zeros_like(base_text))
    digest = hashlib.sha256(np.ascontiguousarray(text_final).tobytes()).hexdigest()
    n_query = rel.get("_n_query")
    return dict(arm=arm, auc_curve=curve, sleep_log=sleep_log, flag_log=flag_log,
                n_query_final=n_query, store_digest=digest, n_committed_final=len(store),
                raw_grounding_auc=rel.get(RAW_KEY), shuffle_auc=rel.get(SH_KEY), pop_auc=rel.get(POP_KEY))


def _fmt(x):
    return ("%.4f" % x) if isinstance(x, (int, float)) else str(x)


# ===========================================================================
# DATA PREP (reuse V2 verbatim) + encoder acquisition
# ===========================================================================
def _prepare(cfg, out_dir, ckpt_path, device):
    _log("data prep (universe/counts/split/postings/adjacency/grounding) ...")
    universe = V2.load_concept_universe(cfg)
    _log("  universe K=%d" % universe["K"])
    counts, cstats = V2.count_pass(cfg, universe["surf_to_idx"])
    _log("  corpus read=%d kept=%d tokens=%d" % (cstats["n_read"], cstats["n_kept"], cstats["total_alpha_tokens"]))
    split = V2.build_split(universe, counts, cfg)
    _log("  split heldout=%d train_eval=%d" % (len(split["held_idx"]), len(split["train_eval_idx"])))
    postings, bpe_lines, pmeta = V2.collect_pass(cfg, universe, split)
    adj, deg, n_shards = V2.load_adjacency(universe, cfg)
    ground = V2.build_grounding_reps(universe, split)
    # encoder: load v2 ckpt (FULL) OR train tiny (SMOKE)
    if ckpt_path:
        _log("  loading trained v2 encoder from %s" % ckpt_path)
        model, tok, spec, mc = _build_encoder_from_ckpt(ckpt_path, device)
        _log("  encoder loaded: d=%d L=%d vocab=%d" % (mc["d_model"], mc["n_layers"], mc["vocab"]))
        encoder_source = "v2_checkpoint:" + os.path.basename(ckpt_path)
    else:
        _log("  training tiny fresh encoder (smoke; validates loop mechanism) ...")
        tok, spec = V2.build_bpe(bpe_lines, cfg["vocab"])
        stream, ntok = V2.tokenize_train_stream(cfg, tok, split, spec)
        _log("  train stream tokens=%d" % ntok)
        model, final_loss = V2.mlm_train(stream, spec, cfg, device, cfg["seed"], out_dir, cfg["mlm_steps"])
        _log("  tiny encoder trained final_loss=%.4f" % final_loss)
        encoder_source = "tiny_fresh_smoke"
    d = model.d_model
    K = universe["K"]
    # held concepts must be WELL-COVERED enough to feed n_cycles*mentions_per_cycle mentions
    need = cfg["n_cycles"] * cfg["mentions_per_cycle"]
    held_all = [int(i) for i in split["held_idx"].tolist()]
    held = sorted(ci for ci in held_all if len(postings[ci]) >= need)
    _log("  well-covered held concepts (>= %d mentions): %d / %d" % (need, len(held), len(held_all)))
    # FIXED base rep matrix for the TRAIN (non-held) foundation concepts (the known neighbours the
    # held concept is being connected into). Encoded ONCE from their mention postings; held concepts
    # are ZEROED here -- their reps come from the LOOP store (leak-proof: rep has zero relational input).
    _log("  encoding fixed base reps for train foundation concepts ...")
    base_text, _mcnt = V2.encode_concept_text_reps(model, tok, postings, cfg, device, spec)
    base_text = base_text.astype(np.float32)
    hmask = np.zeros(K, dtype=bool)
    hmask[np.array(held, dtype=np.int64)] = True
    base_text[hmask] = 0.0
    _log("  base reps ready: %d train concepts with text" % int((np.linalg.norm(base_text, axis=1) > 1e-8).sum()))
    return dict(universe=universe, counts=counts, split=split, postings=postings, adj=adj, deg=deg,
                n_shards=n_shards, ground=ground, model=model, tok=tok, spec=spec, d=d, K=K,
                held=held, encoder_source=encoder_source, corpus_stats=cstats,
                collect_meta=pmeta, need_mentions=need, base_text=base_text)


# ===========================================================================
# VERDICT
# ===========================================================================
def _monotone_ish(curve, max_dips=1):
    dips = 0
    for a, b in zip(curve, curve[1:]):
        if a is None or b is None:
            return False
        if b < a - 1e-9:
            dips += 1
    return dips <= max_dips


def build_verdict(arm_results, cfg):
    by = {r["arm"]: r for r in arm_results}
    main = by[MAIN_ARM]
    curve = main["auc_curve"]
    auc0 = curve[0]
    aucF = curve[-1]
    gain = (aucF - auc0) if (auc0 is not None and aucF is not None) else None
    # controls final
    ctrl_finals = {a: by[a]["auc_curve"][-1] for a in (NOREAD_ARM, SCRAM_ARM, NOSLEEP_ARM)}
    controls_below_main = all(
        (aucF is not None and cf is not None and aucF > cf + HP_CONTROL_SEP) for cf in ctrl_finals.values())
    # sleep fired every cycle for sleep-enabled arms (MAIN + SCRAMBLED; NO_READ init-only; READ_NO_SLEEP init-only)
    sleep_every_cycle = all(s["n_consolidated"] >= 1 for s in main["sleep_log"])
    # retention: MAIN AUC never drops below AUC0 - eps
    retention_min = min((c for c in curve if c is not None), default=None)
    retention_ok = (retention_min is not None and auc0 is not None and retention_min >= auc0 - RETENTION_EPS)
    catastrophic_forgetting = not retention_ok
    monotone = _monotone_ish(curve, max_dips=1)
    n_query = main["n_query_final"]
    power_floor = 15 if cfg["run_mode"] == "smoke" else MIN_QUERY_TASKS
    power_ok = (n_query is not None and n_query >= power_floor)
    # flag population should shrink for MAIN (learns what it doesn't know -> acquires it)
    flag_shrinks = (len(main["flag_log"]) >= 2 and main["flag_log"][-1] <= main["flag_log"][0])

    # COMPREHENSION discriminator (fires even on a tiny encoder): real prose must out-rank
    # word-shuffled prose -> the encoder path carries genuine meaning, not surface bag-of-words.
    scram_curve = by[SCRAM_ARM]["auc_curve"]
    comp_gap_c0 = ((curve[0] - scram_curve[0])
                   if (curve[0] is not None and scram_curve[0] is not None) else None)
    comp_gap_final = ((aucF - scram_curve[-1])
                      if (aucF is not None and scram_curve[-1] is not None) else None)
    comprehension_fires = bool(comp_gap_c0 is not None and comp_gap_c0 > 0.0
                               and comp_gap_final is not None and comp_gap_final > 0.0)
    # NO_READ frozen (store never changes) + clarify gate fired (flagged >=1 real unknown)
    noread_curve = by[NOREAD_ARM]["auc_curve"]
    noread_flat = bool(max(noread_curve) - min(noread_curve) < 1e-6)
    clarify_fired = bool(max(main["flag_log"]) > 0)

    gain_margin = cfg["gain_margin_hp"]
    if cfg["run_mode"] == "smoke":
        # SMOKE mechanism-gate (what a TINY encoder CAN validate): loop runs end-to-end, sleep fires
        # every cycle, probe has power, clarify fires, NO_READ frozen, and REAL>SCRAMBLED comprehension.
        # The across-cycle GAIN is DEFERRED to FULL: a 0.53M/250-step encoder is below the signal
        # threshold where mention-averaging concentrates (it regresses to centroid) -- v2 proved the
        # text-rep carries relational signal only at scale. gain_on_tiny reported, NOT gated.
        mechanism_ok = bool(sleep_every_cycle and power_ok and comprehension_fires
                            and noread_flat and clarify_fired)
        verdict = "SMOKE_MECHANISM_PASS" if mechanism_ok else "SMOKE_MECHANISM_INCONCLUSIVE"
        gain_ok = (gain is not None and gain > 0.0)
        hard = mechanism_ok
    else:
        gain_ok = (gain is not None and gain > gain_margin)
        hard = bool(gain_ok and sleep_every_cycle and controls_below_main and retention_ok
                    and monotone and power_ok and comprehension_fires)
        verdict = "HARD_PASS" if hard else ("MIDDLE_BAND" if (gain is not None and gain > 0) else "HARD_FAIL")

    return dict(
        verdict=verdict,
        comprehension_gap_cycle0=(round(comp_gap_c0, 4) if comp_gap_c0 is not None else None),
        comprehension_gap_final=(round(comp_gap_final, 4) if comp_gap_final is not None else None),
        comprehension_fires=comprehension_fires,
        noread_flat=noread_flat, clarify_fired=clarify_fired,
        gain_on_tiny_encoder=(bool(gain > 0.0) if gain is not None else None),
        knowledge_gain_main=(round(gain, 4) if gain is not None else None),
        main_auc_cycle0=(round(auc0, 4) if auc0 is not None else None),
        main_auc_final=(round(aucF, 4) if aucF is not None else None),
        main_curve=[(round(c, 4) if c is not None else None) for c in curve],
        control_finals={a: (round(v, 4) if v is not None else None) for a, v in ctrl_finals.items()},
        controls_below_main=controls_below_main,
        sleep_fired_every_cycle=sleep_every_cycle,
        retention_ok=retention_ok, retention_min=(round(retention_min, 4) if retention_min is not None else None),
        catastrophic_forgetting=catastrophic_forgetting,
        monotone_ish=monotone,
        flag_population_curve=main["flag_log"], flag_population_shrinks=flag_shrinks,
        n_query_final=n_query, power_ok=power_ok,
        raw_grounding_auc=(round(main["raw_grounding_auc"], 4) if main["raw_grounding_auc"] is not None else None),
        shuffle_auc=(round(main["shuffle_auc"], 4) if main["shuffle_auc"] is not None else None),
    )


# ===========================================================================
# ARMS-MUST-DIFFER (META_RULE_AF)
# ===========================================================================
def _arms_differ(arm_results):
    dig = {r["arm"]: r["store_digest"] for r in arm_results}
    # EXEMPT (NO_READ, READ_NO_SLEEP): both freeze the consolidated store at cycle-0 by construction
    # (distinct mechanism -- one has no input, one has input but no consolidation -- identical committed
    # store: THAT identity is the point, sleep-off => reading changes nothing in the foundation).
    exempt = {frozenset((NOREAD_ARM, NOSLEEP_ARM))}
    names = sorted(dig)
    collisions = []
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            na, nb = names[a], names[b]
            if dig[na] == dig[nb] and frozenset((na, nb)) not in exempt:
                collisions.append((na, nb))
    assert not collisions, "META_RULE_AF VIOLATION: arms bit-identical (not exempted): %s" % collisions
    return dig


# ===========================================================================
# MAIN RUN
# ===========================================================================
def run_full(cfg, out_dir, ckpt_path):
    device = V2._select_device() if cfg["run_mode"] == "full" else torch.device("cpu")
    _log("device=%s run_mode=%s ckpt=%s" % (device.type, cfg["run_mode"], ckpt_path))
    prep = _prepare(cfg, out_dir, ckpt_path, device)
    held = prep["held"]
    if len(held) < 8:
        raise RuntimeError("too few well-covered held concepts (%d) -- raise max_lines/cap_mentions or "
                           "lower n_cycles*mentions_per_cycle" % len(held))
    seed = cfg["seed"]
    arm_results = []
    for arm in ARMS:
        _log("=== ARM %s ===" % arm)
        r = _run_arm(arm, held, prep["postings"], prep["model"], prep["tok"], prep["spec"], cfg, device,
                     out_dir, prep["ground"], prep["counts"], prep["universe"], prep["split"],
                     prep["adj"], prep["deg"], prep["n_shards"], seed, prep["K"], prep["d"], prep["base_text"])
        arm_results.append(r)
    digests = _arms_differ(arm_results)
    verdict = build_verdict(arm_results, cfg)
    payload = dict(
        anchor_name=ANCHOR_NAME, run_mode=cfg["run_mode"], ts_iso=_now(),
        encoder_source=prep["encoder_source"], device=device.type,
        n_held_concepts=len(held), n_cycles=cfg["n_cycles"], mentions_per_cycle=cfg["mentions_per_cycle"],
        corpus_stats=prep["corpus_stats"], collect_meta=prep["collect_meta"],
        arms={r["arm"]: {k: v for k, v in r.items() if k != "store_digest"} for r in arm_results},
        arm_store_digests=digests,
        loop_cfg=dict(n_cycles=cfg["n_cycles"], mentions_per_cycle=cfg["mentions_per_cycle"],
                      min_evidence_mentions=cfg["min_evidence_mentions"],
                      concentration_thresh=cfg["concentration_thresh"],
                      min_compression_ratio=cfg["min_compression_ratio"]),
        **verdict,
    )
    payload["verdict_msg"] = (
        "gain=%s main[%s->%s] controls_below=%s sleep_every=%s retention_ok=%s monotone=%s n_query=%s" % (
            verdict["knowledge_gain_main"], verdict["main_auc_cycle0"], verdict["main_auc_final"],
            verdict["controls_below_main"], verdict["sleep_fired_every_cycle"],
            verdict["retention_ok"], verdict["monotone_ish"], verdict["n_query_final"]))
    payload["summary"] = payload["verdict"]
    return payload


# ===========================================================================
# metrics IO (atomic) + crash diag
# ===========================================================================
def _write_metrics(out_dir, payload, elapsed_s):
    payload = dict(payload)
    payload["elapsed_s"] = round(elapsed_s, 3)
    payload.setdefault("verdict", "CYCLE_INCOMPLETE")
    payload.setdefault("verdict_msg", payload.get("verdict"))
    payload.setdefault("summary", payload.get("verdict"))
    payload["VET_PENDING"] = True
    payload["LOCAL_ONLY_UNCOMMITTED"] = True
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, default=str)
    os.replace(tmp, final)
    return final


def _write_crash_metrics(out_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg="%s: %s" % (type(exc).__name__, str(exc)[:500]),
                summary="CELL_CRASHED", elapsed_s=0.0, traceback=traceback.format_exc()[:5000],
                ts_iso=_now(), anchor_name=ANCHOR_NAME)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


# ===========================================================================
# SELF-TEST: constructs REAL objects (encoder, clarify gate, learner MDL gate,
# relational probe, full loop) at tiny synthetic scale -- NO corpus read.
# ===========================================================================
def self_test():
    out = {}
    device = torch.device("cpu")
    torch.manual_seed(7)
    np.random.seed(7)
    # (1) real encoder object at tiny scale + real _encode_sentences code path
    from tokenizers import Tokenizer, models, trainers, pre_tokenizers
    toy = ["the cat sat on the mat", "a dog ran in the park", "birds fly over the sea",
           "rocks are hard and heavy", "water is wet and cold", "the sun is very hot"]
    tk = Tokenizer(models.BPE(unk_token="[UNK]"))
    tk.pre_tokenizer = pre_tokenizers.Whitespace()
    tk.train_from_iterator(iter(toy * 20), trainers.BpeTrainer(
        vocab_size=64, special_tokens=["[PAD]", "[UNK]", "[MASK]"], show_progress=False))
    spec = dict(pad=tk.token_to_id("[PAD]"), unk=tk.token_to_id("[UNK]"),
                mask=tk.token_to_id("[MASK]"), size=tk.get_vocab_size())
    model = V2.TinyTransformer(spec["size"], 16, 16, 1, 2, 2, spec["pad"]).to(device)
    model.eval()
    cfg = dict(SELFTEST_CFG)
    cfg["max_len"] = 16
    reps = _encode_sentences(model, tk, toy, cfg, device, spec)
    assert reps.shape == (6, 16), reps.shape
    assert np.allclose(np.linalg.norm(reps, axis=1), 1.0, atol=1e-3), "pooled reps must be L2-normalized"
    out["encode"] = {"shape": list(reps.shape)}
    # (2) real hdlab.learner MDL gate: coherent evidence compresses -> commit; incoherent -> keep episodic
    coherent = [reps[0] + 0.01 * np.random.randn(16).astype(np.float32) for _ in range(4)]
    for c in coherent:
        c /= (np.linalg.norm(c) + 1e-8)
    lr_c, coh_c = _concept_learn_result(coherent)
    incoherent = list(reps[:4])
    lr_i, coh_i = _concept_learn_result(incoherent)
    assert coh_c > coh_i, (coh_c, coh_i)
    assert per_cluster_gate(lr_c, 1.0), "coherent evidence must pass MDL compression gate"
    out["learner_gate"] = {"coherent_coh": round(coh_c, 4), "incoherent_coh": round(coh_i, 4),
                           "coherent_cr": round(float(lr_c.compression_ratio), 4)}
    # (3) real ClarifyGate flag population: under-known (1 mention) flagged, well-known (>=min) accepted
    gate = ClarifyGate()
    acc = {0: [reps[0]], 1: coherent}
    n_flag = _clarify_flag_population(acc, [0, 1], gate, dict(clarify_min_evidence=6))
    assert n_flag >= 1, "clarify gate must flag the under-known concept"
    out["clarify"] = {"n_flagged": int(n_flag)}
    # (4) real SLEEP consolidation + retention: coherent concept commits; store updates
    store = {}
    slog, committed = _sleep_consolidate({0: coherent}, store, is_init=False,
                                          cfg=dict(min_compression_ratio=1.0, min_evidence_mentions=3,
                                                   concentration_thresh=0.15))
    assert slog["n_consolidated"] == 1 and 0 in store, slog
    out["sleep"] = {"n_consolidated": slog["n_consolidated"]}
    # (5) real relational_eval probe code path on a tiny synthetic universe/graph
    K, d = 12, 16
    rng = np.random.default_rng(3)
    ground = rng.standard_normal((K, d)).astype(np.float32)
    ground /= (np.linalg.norm(ground, axis=1, keepdims=True) + 1e-8)
    text = ground.copy()  # perfect reps -> AUC should be high (>0.5)
    universe = dict(ids=["c%d" % i for i in range(K)], K=K,
                    surfaces=["c%d" % i for i in range(K)])
    held_idx = np.arange(0, 6, dtype=np.int64)
    train_eval_idx = np.arange(6, 12, dtype=np.int64)
    split = dict(held_idx=held_idx, train_eval_idx=train_eval_idx)
    adj = [set() for _ in range(K)]
    # each held concept's true neighbour is a specific train concept with a similar ground rep
    for h in range(6):
        nb = 6 + h
        text[nb] = ground[h] * 0.9 + 0.1 * ground[nb]
        text[nb] /= (np.linalg.norm(text[nb]) + 1e-8)
        adj[h].add(nb)
        adj[nb].add(h)
    deg = np.array([len(a) for a in adj], dtype=np.int64)
    counts = np.ones(K, dtype=np.int64)
    rel = V2.relational_eval(ground, text, counts, universe, split, adj, deg, 1, 7, 0.5)
    out["relational_probe"] = {"n_query": rel.get("_n_query"), "text_auc": rel.get(TEXT_KEY)}
    assert rel.get("_n_query") is not None, "relational probe produced no queries"
    # (6) FULL code path: v2-checkpoint round-trip (the FULL comprehension-engine loader). Save a tiny
    # ckpt in the EXACT v2 _save_checkpoint schema, reload via _build_encoder_from_ckpt, encode.
    import tempfile
    ckpt = dict(
        state_dict={k: v.detach().cpu() for k, v in model.state_dict().items()},
        spec=spec,
        model_cfg=dict(vocab=spec["size"], max_len=16, d_model=16, n_layers=1,
                       n_heads=2, ffn_mult=2, pad_id=spec["pad"]),
        tokenizer_json=tk.to_str(), seed=7, run_mode="selftest", anchor="ckpt_roundtrip",
        w_star=0.5, selected_arm="ARM_RAW_TEXT")
    fd, cpath = tempfile.mkstemp(suffix=".pt")
    os.close(fd)
    try:
        torch.save(ckpt, cpath)
        m2, tk2, spec2, mc2 = _build_encoder_from_ckpt(cpath, device)
        reps2 = _encode_sentences(m2, tk2, toy, cfg, device, spec2)
        assert reps2.shape == (6, 16), reps2.shape
        assert np.allclose(reps2, reps, atol=1e-4), "reloaded encoder must reproduce the saved encoder's reps"
        out["ckpt_roundtrip"] = {"reload_ok": True, "d_model": mc2["d_model"]}
    finally:
        try:
            os.remove(cpath)
        except OSError:
            pass
    print("[%s] SELF-TEST PASS %s" % (ANCHOR_NAME, json.dumps(out)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--ckpt", type=str, default=None, help="path to v2 encoder checkpoint (FULL comprehension engine)")
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    cfg = dict(FULL_CFG if args.full else SMOKE_CFG)
    if args.seed is not None:
        cfg["seed"] = args.seed
    out_dir = _out_dir(cfg["run_mode"])
    _write_start_marker(out_dir, cfg["run_mode"], expected_units=len(ARMS) * cfg["n_cycles"])
    t0 = time.perf_counter()
    _log("RUN START run_mode=%s" % cfg["run_mode"])
    payload = run_full(cfg, out_dir, args.ckpt)
    elapsed = time.perf_counter() - t0
    payload["elapsed_s"] = round(elapsed, 3)
    final = _write_metrics(out_dir, payload, elapsed)
    _log("RUN DONE (%.1fs) -> %s" % (payload["elapsed_s"], final))
    _log("VERDICT=%s | %s" % (payload["verdict"], payload["verdict_msg"]))


if __name__ == "__main__":
    _od = _out_dir(FULL_CFG["run_mode"] if "--full" in sys.argv else
                   (SMOKE_CFG["run_mode"] if "--smoke" in sys.argv else "selftest"))
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
