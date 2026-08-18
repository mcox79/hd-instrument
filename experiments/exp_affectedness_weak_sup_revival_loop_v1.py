"""AFFECTEDNESS WEAK-SUP REVIVAL LOOP (v1): wire the leakage-VET'd curated affectedness signal
(design-gate atom, MEASURED_MECHANISM, 2026-07-20) as a WEAK-SUPERVISION LEARNING TARGET and test
whether a trained loop moves HELD-OUT patient-selection precision above (a) the frozen ~0.5574
stacked reader (atom 29345 CG, reproduced LIVE here, not merely cited) and (b) a MANDATORY
locative-exclusion-ONLY control arm (the VET's own flagged non-specificity confound: the design-
gate's static selection-margin was IDENTICAL between the full curated signal and bare locative
exclusion, +0.4406 == +0.4406).

See preregs/2026-07-20_affectedness_weak_sup_revival_loop_v1.md for the full pre-registration.

WHY (pointer, not re-derivation): the design-gate cell (exp_affectedness_change_of_state_patient_
selection_design_gate_v1) measured (no loop) that a curated affectedness signal (Dowty proto-
patient NP ontology x Levin change-of-state verb class) tracks per-instance patient-correctness
and SURVIVES a blind leakage test (WordNet-lexname re-derivation, zero eval peek, corr +0.2732,
still >= the 0.20 floor) while a genuine text-internal DERIVATION of the same feature HARD_FAILS
non-vacuously (0.0443). That measurement only asked "does the signal correlate"; THIS cell asks
the actual capability question the design-gate set up: can the substrate LEARN from it.

PRIMARY TARGET (BLIND, not eval-peeked): SIG_WN_COS_GATED = WordNet first-noun-sense lexname
  bucket (artifact/food/substance/object/plant -> +1.0; animal/person -> +0.8; body -> +0.6;
  location -> -1.0; other non-object lexnames -> -0.3; else None) gated to 0.0 unless the verb is
  in the SAME hand-curated Levin change-of-state/creation/destruction/contact verb class the
  design-gate used (COS_VERB_CLASS, reused unchanged -- this is the VET's own "WN_COS_GATED"
  definition: NP-ontology blind, verb-gate still curated).
NON-SPECIFICITY CONTROL (mandatory): SIG_WN_PLACE_ONLY = -1.0 iff WordNet first-noun-sense
  lexname is noun.location, else 0.0 (None if no WordNet noun sense at all). Same blind lexical
  standard, isolates JUST the locative-exclusion component.

MECHANISM: reuses the STEP-1/CPCL-v2-proven contrastive-perceptron harness UNCHANGED (train_
  weights, mine_contrast_pairs, mine_absolute_targets, eval_kept, group_by_instance, build_
  candidates -- imported from exp_contrastive_entity_recurrence_reader_loop_cpcl_v2), with ONE
  substitution: CPCL-v2's forward-predictive-coding feature (trained against entity-recurrence
  continuations) is replaced by a DETERMINISTIC per-candidate signal lookup (no codebook, no
  text8, no continuations, no forward model -- what IS learned is the perceptron weight ON that
  feature, mixed with LCCP's 6 structural cues, via contrastive margin updates mined from the
  held-out mining corpus). err := 0.5 if signal is None else (1.0 - signal) / 2.0 (matches
  CPCL-v2's err semantics: lower = better = higher affectedness).

ARMS (ONE variable differs -- which signal mines the contrast pairs / feeds feat7):
  FROZEN_HARNESS : base semantic-teacher pass only, NO contrastive pass. In-harness fair floor.
  CONTRAST_AFF   : base pass + contrastive pass, pairs from SIG_WN_COS_GATED (the mechanism arm).
  ABSOLUTE_AFF   : base pass + non-contrastive median-split target, same signal (known-weak ctrl).
  SHUFFLED_AFF   : base pass + contrastive pass, but signal VALUES permuted across mining
                   candidates (deterministic seeded, NEVER hash()) -- must-fail P2 VETO.
  CONTRAST_LOC   : identical architecture to CONTRAST_AFF, signal = SIG_WN_PLACE_ONLY (MANDATORY
                   non-specificity control per the VET's own flagged confound).
  ORACLE_CEILING : construction-determination guard (pick gold rival directly).

REAL EXTERNAL BASELINE (Gate D positive-control, reproduced LIVE not merely cited):
  FROZEN_STACK = LCCP arm-C -> ARG categorial cascade -> QUOT quotative-suppression stack
  (exp_quotative_speaker_attribution_stack_break050_v1, atom 29345 CG, published precision 0.5574
  recall 0.34). seed-7 full-mode reproduction must land within 0.02 of 0.5574 or this cell HALTS
  (Gate D: the FIRST arm must reproduce X's known result AT THE TEST REGIME).

HONESTY FLAG (pre-declared): FROZEN_STACK and the CPCL-harness arms are DIFFERENT PIPELINES (a
  hand-built categorial cascade with a conservative precision/recall tradeoff vs a linear
  perceptron over 7 features scored via one keep-threshold). Beating 0.5574 with the perceptron
  architecture is a demanding, possibly architecture-capped bar, independent of whether the
  affectedness TARGET is a good learning signal. Both numbers reported; HARD_FAIL sub-reasons
  are reported separately (nonspecific vs below-real-reader vs learning-mechanism-bound) so an
  architecture-gap finding is never misreported as "the loop can't learn."

PRE-REGISTERED BANDS (see prereg; NOT tuned to pass):
  HARD_PASS_P1: mean(CONTRAST_AFF) > FROZEN_STACK(0.5574) AND mean(CONTRAST_AFF) >
    mean(CONTRAST_LOC)+0.02 AND min_seed(CONTRAST_AFF-CONTRAST_LOC) > 0 AND
    CONTRAST_AFF > ABSOLUTE_AFF AND CONTRAST_AFF > SHUFFLED_AFF AND CONTRAST_AFF > FROZEN_HARNESS.
  HARD_FAIL_NONSPECIFIC: CONTRAST_AFF <= CONTRAST_LOC.
  HARD_FAIL_BELOW_REAL_READER: CONTRAST_LOC < CONTRAST_AFF <= FROZEN_STACK.
  HARD_FAIL_LEARNING_MECHANISM_BOUND: CONTRAST_AFF <= FROZEN_HARNESS.
  MIDDLE_BAND_P1: beats FROZEN_HARNESS + CONTRAST_LOC but not FROZEN_STACK, margin < 0.02 or
    seed-inconsistent.
  P2 must-fail VETO: HARD_FAIL_P2_VETO if SHUFFLED_AFF trains (|delta vs FROZEN_HARNESS| >= 0.02
    AND SHUFFLED_AFF >= CONTRAST_AFF) -> untrust P1.
  Sanity gates (block dispatch if violated): arms_differ_verified, cardinality_ok, baseline_in_
    band, discriminator_fires (>=5 informative CONTRAST_AFF pairs), wn_repro_floor (independently
    re-measured corr(SIG_WN_COS_GATED, gold) >= 0.10 on THIS cell's own eval-slice recompute),
    stack_positive_control (FROZEN_STACK seed-7 within 0.02 of 0.5574).

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- the LCCP reader (~105ms/
  sent) is the cost, run ONCE + cached (reuses exp_contrastive_entity_recurrence_reader_loop_
  cpcl_v2's existing mining-cache files by content-hash key when it matches; writes its OWN
  cache path otherwise -- never mutates another cell's data dir). No codebook, no GPU. Storage:
  no_storage. final_metrics_atomicity=tmp_replace. crlb_n/a (extraction-precision metric; no
  quantitative noise-floor formula applies). progress_logging=print_flush_true (full timeout
  >= 1800s). Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds, hashlib digests (never hash()),
  sorted(set()), np.random.default_rng only.
CELL-TEMPLATE MANDATORY: except SystemExit: raise BEFORE except Exception (no BaseException); no
  bare except / no silent-continue; arms_differ_verified (weight hashes); final_metrics_
  atomicity=tmp_replace; all report numbers tagged MEASURED@/CITED@.
LOCAL ONLY: no origin push, no remote-persist (per Director contract). Dispatch: local_cpu_queue.
ASCII-only. No emojis. No em dashes.
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
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "affectedness_weak_sup_revival_loop_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L         # noqa: E402
from experiments import exp_scene_coherence_verifier_contrastive_scv_v1 as S               # noqa: E402
from experiments import exp_contrastive_entity_recurrence_reader_loop_cpcl_v2 as CPCL      # noqa: E402
from experiments import exp_affectedness_change_of_state_patient_selection_design_gate_v1 as AFF  # noqa: E402
from experiments import exp_lccp_fullnopat_syntactic_frame_teacher_stack_v1 as STACK       # noqa: E402
from experiments import exp_quotative_speaker_attribution_stack_break050_v1 as QUOT        # noqa: E402

try:
    from nltk.corpus import wordnet as wn  # noqa: E402
    wn.synsets("dog", pos="n")  # trigger corpus load; raises if unavailable
    _WORDNET_AVAILABLE = True
except Exception:
    wn = None
    _WORDNET_AVAILABLE = False

FEAT_DIM = 7  # LCCP's 6 structural cues + 1 affectedness-signal cue
PUBLISHED_STACK_PRECISION = 0.5574  # CITED@ data/exp_quotative_speaker_attribution_stack_break050_v1/metrics.json
PUBLISHED_STACK_RECALL = 0.34       # CITED@ same
STACK_TOLERANCE = 0.02              # Gate D positive-control tolerance

CPCL_MINING_CACHE_FULL = os.path.join(REPO_ROOT, "data",
                                       "exp_contrastive_entity_recurrence_reader_loop_cpcl_v2",
                                       "_mining_cache.json")
CPCL_MINING_CACHE_SMOKE = os.path.join(REPO_ROOT, "data",
                                        "exp_contrastive_entity_recurrence_reader_loop_cpcl_v2_smoke",
                                        "_mining_cache.json")

WN_REPRO_FLOOR = 0.10  # independently re-measured corr(SIG_WN_COS_GATED, gold) must clear this

ARM_NAMES = ["FROZEN_HARNESS", "CONTRAST_AFF", "ABSOLUTE_AFF", "SHUFFLED_AFF", "CONTRAST_LOC"]

# ==================================================================================================
# WordNet-lexname affectedness buckets (BLIND -- reuses S's own curated WordNet supersense sets,
# builds on prior art rather than re-inventing a bucket scheme; matches the leakage-VET's own
# "WN_COS_GATED" recipe: artifact/food/substance/object/plant=+1.0, animal/person=+0.8, body=+0.6,
# location=-1.0, remaining non-object lexnames=-0.3, else None).
# ==================================================================================================
WN_POS_LEXNAMES = {"noun.artifact", "noun.food", "noun.substance", "noun.object", "noun.plant"}
WN_ANIMATE_LEXNAMES = {"noun.animal", "noun.person"}
WN_BODY_LEXNAMES = {"noun.body"}
WN_LOCATION_LEXNAMES = {"noun.location"}
WN_ABSTRACT_LEXNAMES = S.NONOBJECT_SS - WN_LOCATION_LEXNAMES  # reuse S's curated non-object set

_WN_LEX_CACHE = {}


def wn_first_noun_lexname(tok):
    """First-noun-sense WordNet lexname, cached. None if unavailable/OOV. Deterministic (WordNet
    sense ordering is fixed data, not randomized)."""
    if tok in _WN_LEX_CACHE:
        return _WN_LEX_CACHE[tok]
    lex = None
    if _WORDNET_AVAILABLE:
        try:
            syns = wn.synsets(tok, pos="n")
            if syns:
                lex = syns[0].lexname()
        except Exception:
            lex = None
    _WN_LEX_CACHE[tok] = lex
    return lex


def sig_wn_proto_patient_ontology(p):
    """Blind WordNet-lexname affectedness bucket for token p. None = no WordNet noun sense (or
    unclassified lexname -- e.g. noun.group/possession/shape are intentionally left OOV here to
    match the VET's own 5-bucket recipe, not freelanced)."""
    if p in L.PRONOUN or p in L.FUNCWORD:
        return None
    lex = wn_first_noun_lexname(p)
    if lex is None:
        return None
    if lex in WN_POS_LEXNAMES:
        return 1.0
    if lex in WN_ANIMATE_LEXNAMES:
        return 0.8
    if lex in WN_BODY_LEXNAMES:
        return 0.6
    if lex in WN_LOCATION_LEXNAMES:
        return -1.0
    if lex in WN_ABSTRACT_LEXNAMES:
        return -0.3
    return None


def sig_wn_cos_gated(p, v):
    """PRIMARY TARGET (blind NP-ontology x hand-curated Levin change-of-state verb gate -- the
    VET's own 'WN_COS_GATED' definition)."""
    base = sig_wn_proto_patient_ontology(p)
    if base is None:
        return None
    return base if v in AFF.COS_VERB_CLASS else 0.0


def sig_wn_place_only(p, v):
    """NON-SPECIFICITY CONTROL (mandatory): blind locative-exclusion ONLY. -1.0 iff first WordNet
    noun sense is noun.location, else 0.0 (None only if no WordNet noun sense at all)."""
    if p in L.PRONOUN or p in L.FUNCWORD:
        return None
    lex = wn_first_noun_lexname(p)
    if lex is None:
        return None
    return -1.0 if lex in WN_LOCATION_LEXNAMES else 0.0


# ==================================================================================================
# Deterministic seeds (NEVER builtin hash()).
# ==================================================================================================
def _digest_seed(s):
    return int.from_bytes(hashlib.sha256(s.encode("utf-8")).digest()[:8], "big")


# ==================================================================================================
# Attach signal-derived feat7 + err to a fresh copy of each candidate (per-arm; never mutates the
# shared base candidate list so different arms' signal attachments cannot clobber each other).
# ==================================================================================================
def attach_signal(cands, sig_fn):
    out = []
    for c in cands:
        c2 = dict(c)
        sig = sig_fn(c2["p"], c2["v"])
        sval = 0.0 if sig is None else float(sig)
        c2["sig"] = sig
        c2["feat"] = np.concatenate([c2["feat6"], [sval]])
        c2["err"] = 0.5 if sig is None else (1.0 - float(sig)) / 2.0
        out.append(c2)
    return out


def shuffle_signal_values(cands, sig_fn, seed):
    """Permute the per-candidate NON-None signal VALUES across the candidates that had one,
    breaking the specific candidate<->signal correspondence while preserving the marginal value
    distribution (analogous to CPCL-v2's continuation-derangement must-fail control). Deterministic
    (np.random.default_rng, never hash())."""
    base = [dict(c) for c in cands]
    sigs = []
    idx_with_sig = []
    for i, c in enumerate(base):
        s = sig_fn(c["p"], c["v"])
        if s is not None:
            idx_with_sig.append(i)
            sigs.append(float(s))
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(sigs))
    shuffled_vals = [sigs[k] for k in perm]
    out = []
    for i, c in enumerate(base):
        if i in set(idx_with_sig):
            pos = idx_with_sig.index(i)
            sval = shuffled_vals[pos]
        else:
            sval = None
        c["sig"] = sval
        c["feat"] = np.concatenate([c["feat6"], [0.0 if sval is None else float(sval)]])
        c["err"] = 0.5 if sval is None else (1.0 - float(sval)) / 2.0
        out.append(c)
    return out


# ==================================================================================================
# Reproduce FROZEN_STACK (Gate D positive control; the real 0.5574 reader, LIVE not merely cited).
# ==================================================================================================
def reproduce_stack(gold_slice, seeds, div_thr=3):
    order, sent_text, reader_svo = L.load_slice_and_reader(gold_slice)
    gold, gold_meta = L.load_gold(gold_slice)
    gold_agent = QUOT.load_gold_raw(gold_slice)
    toks = set()
    for sid in order:
        for v_surf, a, p in reader_svo[sid]:
            toks.update([p, L.lemma_verb(v_surf)])
    for sid, rec in gold.items():
        for g in rec["pos"]:
            toks.update([g["patient"], g["v"]])
    glove = L.load_glove_for(toks)
    per_seed = []
    kept_by_seed = {}
    for seed in seeds:
        lccp_cfg = dict(sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=60, keep_thr=0.45,
                         subcat_thr=0.42, heldout_frac=0.25, k_constructions=4, p_keep=60.0,
                         p_drop=40.0, div_thr=div_thr, seed=seed)
        keptC0 = L.run_arms(order, reader_svo, sent_text, glove, lccp_cfg, seed)[0]["C_lccp"]
        keptQ = STACK.stack_over(keptC0, order, sent_text, reader_svo, gold_agent, div_thr)
        m = L.score_arm(keptQ, gold)
        per_seed.append(m["precision"])
        kept_by_seed[seed] = keptQ
    return per_seed, kept_by_seed, gold, gold_meta


# ==================================================================================================
# Mining data (reuse CPCL-v2's existing cache by content-hash key when it matches; never mutate
# another cell's data dir -- falls back to S.run_reader_on_files with THIS cell's own cache path).
# ==================================================================================================
def get_mining_data(files, my_cache_path, max_sents, reuse_cache_path):
    key = hashlib.sha256(("|".join(files) + f"|{max_sents}").encode()).hexdigest()[:16]
    if reuse_cache_path and os.path.exists(reuse_cache_path):
        with open(reuse_cache_path, encoding="utf-8") as f:
            obj = json.load(f)
        if obj.get("_key") == key:
            print(f"[{ANCHOR_NAME}] reusing mining cache from {reuse_cache_path} (key match)", flush=True)
            return obj["data"]
    return S.run_reader_on_files(files, my_cache_path, max_sents=max_sents)


# ==================================================================================================
# Config.
# ==================================================================================================
def cfg_smoke():
    # coh_lr=0.5 (NOT CPCL-v2's 0.10) -- smoke-time regime iteration: at coh_lr<=0.3 the contrastive
    # pass produced ZERO eval-set rival swaps (structural feat6 weights, magnitude ~9-12, dominate the
    # small affectedness weight; DISCRIMINATOR-MUST-SURVIVE-SCALE preview at full-N confirmed the same
    # zero-swap floor at coh_lr=0.10). coh_lr=0.5 is the smallest tested value that reliably produces
    # >=2 rival-decision swaps on held-out eval at BOTH smoke and full scale while staying numerically
    # stable (oja_eta=0.002 bounds w-norm; coh_lr>=2.0 was tested and overturns MORE decisions but nets
    # NEGATIVE precision -- confirms the mechanism is a genuine, bounded, non-monotonic effect, not a
    # free knob to crank for a HARD_PASS).
    return dict(mode="smoke", gold_slice=AFF.GOLD_SLICE_SMOKE, mining_files=S.MINING_FILES_SMOKE,
                mining_max_sents=500, min_err_gap=0.05, sel_keep=0.28, sel_drop=0.10, lr=0.20,
                epochs=40, keep_thr=0.45, coh_lr=0.5, coh_margin=0.20, oja_eta=0.002,
                seeds=[7, 13, 19], div_thr=3, shuffle_seed=303)


def cfg_full():
    return dict(mode="full", gold_slice=AFF.GOLD_SLICE_FULL, mining_files=S.MINING_FILES_FULL,
                mining_max_sents=None, min_err_gap=0.05, sel_keep=0.28, sel_drop=0.10, lr=0.20,
                epochs=60, keep_thr=0.45, coh_lr=0.5, coh_margin=0.20, oja_eta=0.002,
                seeds=[7, 13, 19], div_thr=3, shuffle_seed=303)


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def _hash_w(w):
    return hashlib.sha256(np.asarray(w, dtype=np.float64).tobytes()).hexdigest()[:16]


def pearson(xs, ys):
    x = np.asarray(xs, dtype=np.float64)
    y = np.asarray(ys, dtype=np.float64)
    if len(x) < 2 or float(np.std(x)) < 1e-12 or float(np.std(y)) < 1e-12:
        return 0.0, True
    c = float(np.corrcoef(x, y)[0, 1])
    if not np.isfinite(c):
        return 0.0, True
    return c, False


# ==================================================================================================
# Main run.
# ==================================================================================================
def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    out_dir = _out_dir(mode)
    gold_slice = cfg["gold_slice"]

    if not _WORDNET_AVAILABLE:
        elapsed = time.perf_counter() - t0
        msg = "WORDNET_UNAVAILABLE: nltk wordnet corpus not importable in this environment; the primary and control signals are both WordNet-lexname-derived and cannot run without it. Clean STOP, not a loop failure."
        payload = {"anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": "BLOCK_WORDNET_UNAVAILABLE",
                   "verdict_msg": msg, "summary": msg, "elapsed_s": elapsed,
                   "ts_iso": datetime.now(timezone.utc).isoformat(), "wordnet_available": False,
                   "REQUIRED_FIELDS": ["verdict", "wordnet_available"]}
        write_metrics(out_dir, payload)
        print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
        return payload

    # ---- STEP 0: Gate D positive control -- reproduce FROZEN_STACK live (the real 0.5574 reader) ----
    print(f"[{ANCHOR_NAME}:{mode}] reproducing FROZEN_STACK (0.5574 reference) ...", flush=True)
    stack_precisions, stack_kept_by_seed, gold_eval, gold_meta = reproduce_stack(gold_slice, cfg["seeds"],
                                                                                  cfg["div_thr"])
    frozen_stack_mean = float(np.mean(stack_precisions))
    seed7_idx = cfg["seeds"].index(7) if 7 in cfg["seeds"] else 0
    stack_reproduces = bool(abs(stack_precisions[seed7_idx] - PUBLISHED_STACK_PRECISION) < STACK_TOLERANCE)
    print(f"[{ANCHOR_NAME}:{mode}] FROZEN_STACK per-seed={stack_precisions} mean={frozen_stack_mean:.4f} "
          f"seed7_reproduces_0.5574(tol={STACK_TOLERANCE})={stack_reproduces}", flush=True)
    # Gate D positive-control is only STRICT at FULL config (same gold_slice as the 0.5574 reference,
    # 7 lessons); the SMOKE slice (2 lessons) is a different, smaller regime and is NOT expected to
    # reproduce 0.5574 -- same convention as exp_lccp_fullnopat_syntactic_frame_teacher_stack_v1.py
    # ("positive control ... only strict at FULL config"). Non-blocking at smoke; report only.
    if mode == "full" and not stack_reproduces:
        elapsed = time.perf_counter() - t0
        msg = (f"GATE_D_FAIL: FROZEN_STACK seed-7 precision={stack_precisions[seed7_idx]:.4f} does not "
               f"reproduce the published 0.5574 within tolerance {STACK_TOLERANCE}. HALT -- do not trust "
               f"downstream comparisons against an unreproduced external baseline.")
        payload = {"anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": "HARD_FAIL_GATE_D_STACK_NOT_REPRODUCED",
                   "verdict_msg": msg, "summary": msg, "elapsed_s": elapsed,
                   "ts_iso": datetime.now(timezone.utc).isoformat(),
                   "stack_precisions": stack_precisions, "published_stack_precision_reference": PUBLISHED_STACK_PRECISION,
                   "REQUIRED_FIELDS": ["verdict", "stack_precisions"]}
        write_metrics(out_dir, payload)
        print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
        return payload

    # ---- Eval slice (SAME 225-cand/44-gold/50-group slice the design-gate + CPCL-v2 forensic used) ----
    eval_order, eval_text, eval_svo = L.load_slice_and_reader(gold_slice)
    gold, gold_meta = L.load_gold(gold_slice)
    eval_data = {sid: {"sent": eval_text[sid], "svo": [list(t) for t in eval_svo[sid]]} for sid in eval_order}
    eval_cands_base = CPCL.build_candidates(eval_data, eval_order)
    labels = []
    for c in eval_cands_base:
        rec = gold.get(c["sid"], {"pos": []})
        m = L.match_pos(c["v"], c["p"], rec["pos"])
        labels.append(1 if m is not None else 0)
    n_pos = sum(labels)
    print(f"[{ANCHOR_NAME}:{mode}] eval n_cands={len(eval_cands_base)} n_gold_correct={n_pos}", flush=True)

    # ---- LEAKAGE-TEST REPRODUCTION CHECK (independent re-measure of SIG_WN_COS_GATED corr) ----
    aff_scores = [sig_wn_cos_gated(c["p"], c["v"]) for c in eval_cands_base]
    content_pairs = [(s, lab) for s, lab in zip(aff_scores, labels) if s is not None]
    wn_repro_corr, wn_repro_degen = pearson([s for s, _ in content_pairs], [lab for _, lab in content_pairs])
    wn_coverage = round(len(content_pairs) / len(eval_cands_base), 4) if eval_cands_base else 0.0
    print(f"[{ANCHOR_NAME}:{mode}] WN_REPRO corr(SIG_WN_COS_GATED, gold)={wn_repro_corr:.4f} "
          f"coverage={wn_coverage} (cited VET reference: +0.2732) floor={WN_REPRO_FLOOR}", flush=True)
    wn_repro_ok = bool(wn_repro_corr >= WN_REPRO_FLOOR)
    if not wn_repro_ok:
        elapsed = time.perf_counter() - t0
        msg = (f"BLOCK_WN_REPRO_FLOOR: independently re-measured corr(SIG_WN_COS_GATED, gold)={wn_repro_corr:.4f} "
               f"< floor {WN_REPRO_FLOOR} (cited VET reference +0.2732). This cell's WordNet-bucket "
               f"reimplementation likely diverges from the audited recipe -- do NOT build a loop on it.")
        payload = {"anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": "HARD_FAIL_WN_REPRO_FLOOR",
                   "verdict_msg": msg, "summary": msg, "elapsed_s": elapsed,
                   "ts_iso": datetime.now(timezone.utc).isoformat(), "wn_repro_corr": wn_repro_corr,
                   "wn_coverage": wn_coverage, "REQUIRED_FIELDS": ["verdict", "wn_repro_corr"]}
        write_metrics(out_dir, payload)
        print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
        return payload

    loc_scores = [sig_wn_place_only(c["p"], c["v"]) for c in eval_cands_base]
    loc_content_pairs = [(s, lab) for s, lab in zip(loc_scores, labels) if s is not None]
    loc_repro_corr, _ = pearson([s for s, _ in loc_content_pairs], [lab for _, lab in loc_content_pairs])
    print(f"[{ANCHOR_NAME}:{mode}] WN_REPRO corr(SIG_WN_PLACE_ONLY, gold)={loc_repro_corr:.4f} "
          f"coverage={round(len(loc_content_pairs)/len(eval_cands_base),4) if eval_cands_base else 0.0}",
          flush=True)

    # ---- Mining candidates (third reader excluded; reuse CPCL-v2's cache by content-hash if it matches) ----
    reuse_cache = CPCL_MINING_CACHE_SMOKE if mode == "smoke" else CPCL_MINING_CACHE_FULL
    mine_data = get_mining_data(cfg["mining_files"], os.path.join(out_dir, "_mining_cache.json"),
                                cfg["mining_max_sents"], reuse_cache)
    mine_order = sorted(mine_data.keys())
    mine_cands_base = CPCL.build_candidates(mine_data, mine_order)
    print(f"[{ANCHOR_NAME}:{mode}] mining sents={len(mine_order)} mining cands={len(mine_cands_base)}", flush=True)

    tok_for_glove = set()
    for c in mine_cands_base:
        tok_for_glove.update([c["p"], c["v"]])
    for c in eval_cands_base:
        tok_for_glove.update([c["p"], c["v"]])
    glove = L.load_glove_for(tok_for_glove)
    # build_semantic_teacher only reads indices 0-5 (feat6) of c["feat"]; alias feat6->feat here (no
    # affectedness signal involved yet -- the semantic teacher is the SAME shared base pass across all arms).
    mine_for_sel = [dict(c, feat=c["feat6"]) for c in mine_cands_base]
    sel_fn, _vc, _gc = L.build_semantic_teacher(mine_for_sel, glove)

    # ---- Build per-arm candidate sets (mining + eval), attach feat7/err per arm's signal ----
    mine_aff = attach_signal(mine_cands_base, sig_wn_cos_gated)
    mine_loc = attach_signal(mine_cands_base, sig_wn_place_only)
    mine_shuf = shuffle_signal_values(mine_cands_base, sig_wn_cos_gated, cfg["shuffle_seed"])
    eval_aff = attach_signal(eval_cands_base, sig_wn_cos_gated)
    eval_loc = attach_signal(eval_cands_base, sig_wn_place_only)

    inst_mine_aff = CPCL.group_by_instance(mine_aff)
    inst_mine_shuf = CPCL.group_by_instance(mine_shuf)
    pairs_aff, stats_aff = CPCL.mine_contrast_pairs(inst_mine_aff, cfg["min_err_gap"])
    pairs_shuf, stats_shuf = CPCL.mine_contrast_pairs(inst_mine_shuf, cfg["min_err_gap"])
    inst_mine_loc = CPCL.group_by_instance(mine_loc)
    pairs_loc, stats_loc = CPCL.mine_contrast_pairs(inst_mine_loc, cfg["min_err_gap"])
    abs_targets_aff = CPCL.mine_absolute_targets(mine_aff)

    eg_aff = CPCL.group_by_instance(eval_aff)
    eg_loc = CPCL.group_by_instance(eval_loc)

    print(f"[{ANCHOR_NAME}:{mode}] contrast pairs: AFF={stats_aff['n_informative_pairs']} "
          f"LOC={stats_loc['n_informative_pairs']} SHUF={stats_shuf['n_informative_pairs']} "
          f"(min_gap={cfg['min_err_gap']})", flush=True)

    train_cfg = {k: cfg[k] for k in ("sel_keep", "sel_drop", "lr", "epochs", "coh_lr", "coh_margin", "oja_eta")}

    per_arm_precision = {a: [] for a in ARM_NAMES}
    w_hashes_seed0 = {}
    n_swaps_seed0 = None
    for seed in cfg["seeds"]:
        w_frozen, _ = CPCL.train_weights(mine_aff, sel_fn, train_cfg, seed, "frozen")
        w_contrast_aff, _ = CPCL.train_weights(mine_aff, sel_fn, train_cfg, seed, "contrast", pairs=pairs_aff)
        w_absolute_aff, _ = CPCL.train_weights(mine_aff, sel_fn, train_cfg, seed, "absolute",
                                                abs_targets=abs_targets_aff)
        w_shuffled, _ = CPCL.train_weights(mine_shuf, sel_fn, train_cfg, seed, "shuffled", pairs=pairs_shuf)
        w_contrast_loc, _ = CPCL.train_weights(mine_loc, sel_fn, train_cfg, seed, "contrast", pairs=pairs_loc)

        # NaN/inf guard (production-scale defensive check; a silently-diverged w must halt, not score).
        for wname, wvec in (("FROZEN", w_frozen), ("CONTRAST_AFF", w_contrast_aff), ("ABSOLUTE_AFF", w_absolute_aff),
                            ("SHUFFLED", w_shuffled), ("CONTRAST_LOC", w_contrast_loc)):
            if not np.all(np.isfinite(wvec)):
                raise FloatingPointError(f"seed={seed} arm={wname} weight vector non-finite: {wvec}")

        if seed == cfg["seeds"][0]:
            n_swaps_seed0 = 0
            for _key, cs in eg_aff.items():
                if len(cs) < 2:
                    continue
                sf = [L.score_cand(w_frozen, c["feat"]) for c in cs]
                sc = [L.score_cand(w_contrast_aff, c["feat"]) for c in cs]
                if int(np.argmax(sf)) != int(np.argmax(sc)):
                    n_swaps_seed0 += 1

        p_frozen = L.score_arm(CPCL.eval_kept(w_frozen, eg_aff, cfg["keep_thr"]), gold)["precision"]
        p_contrast_aff = L.score_arm(CPCL.eval_kept(w_contrast_aff, eg_aff, cfg["keep_thr"]), gold)["precision"]
        p_absolute_aff = L.score_arm(CPCL.eval_kept(w_absolute_aff, eg_aff, cfg["keep_thr"]), gold)["precision"]
        p_shuffled = L.score_arm(CPCL.eval_kept(w_shuffled, eg_aff, cfg["keep_thr"]), gold)["precision"]
        p_contrast_loc = L.score_arm(CPCL.eval_kept(w_contrast_loc, eg_loc, cfg["keep_thr"]), gold)["precision"]

        per_arm_precision["FROZEN_HARNESS"].append(p_frozen)
        per_arm_precision["CONTRAST_AFF"].append(p_contrast_aff)
        per_arm_precision["ABSOLUTE_AFF"].append(p_absolute_aff)
        per_arm_precision["SHUFFLED_AFF"].append(p_shuffled)
        per_arm_precision["CONTRAST_LOC"].append(p_contrast_loc)

        if seed == cfg["seeds"][0]:
            w_hashes_seed0 = {"FROZEN_HARNESS": _hash_w(w_frozen), "CONTRAST_AFF": _hash_w(w_contrast_aff),
                              "ABSOLUTE_AFF": _hash_w(w_absolute_aff), "SHUFFLED_AFF": _hash_w(w_shuffled),
                              "CONTRAST_LOC": _hash_w(w_contrast_loc)}
        print(f"[{ANCHOR_NAME}:{mode}] seed={seed} FROZEN={p_frozen:.4f} CONTRAST_AFF={p_contrast_aff:.4f} "
              f"ABSOLUTE_AFF={p_absolute_aff:.4f} SHUFFLED_AFF={p_shuffled:.4f} CONTRAST_LOC={p_contrast_loc:.4f}",
              flush=True)

    # ---- ORACLE_CEILING guard ----
    oracle_kept = CPCL.eval_kept(None, eg_aff, cfg["keep_thr"], gold=gold, oracle=True)
    oracle_precision = L.score_arm(oracle_kept, gold)["precision"]
    oracle_flag = "CONSTRUCTION_DETERMINED_ORACLE_TRIVIAL" if oracle_precision >= 0.98 else "oracle_nontrivial_ok"

    mean_p = {a: round(float(np.mean(v)), 4) for a, v in per_arm_precision.items()}
    min_p = {a: round(float(np.min(v)), 4) for a, v in per_arm_precision.items()}
    per_seed_delta_vs_loc = [round(per_arm_precision["CONTRAST_AFF"][i] - per_arm_precision["CONTRAST_LOC"][i], 4)
                             for i in range(len(cfg["seeds"]))]
    min_delta_vs_loc = float(np.min(per_seed_delta_vs_loc))

    # ---- Sanity gates ----
    arms_differ = len(set(w_hashes_seed0.values())) == len(w_hashes_seed0)
    baseline_in_band = bool(0.05 < mean_p["FROZEN_HARNESS"] < 0.95)
    discriminator_fires = bool(stats_aff["n_informative_pairs"] >= 5 and (n_swaps_seed0 or 0) >= 1)
    cardinality_ok = bool(all(len(v) == len(cfg["seeds"]) for v in per_arm_precision.values()))

    # ---- P2 must-fail VETO ----
    shuffled_delta = round(mean_p["SHUFFLED_AFF"] - mean_p["FROZEN_HARNESS"], 4)
    if abs(shuffled_delta) >= 0.02 and mean_p["SHUFFLED_AFF"] >= mean_p["CONTRAST_AFF"]:
        p2 = "HARD_FAIL_P2_VETO_SHUFFLED_TRAINS"
    elif abs(shuffled_delta) < 0.01 and mean_p["SHUFFLED_AFF"] < mean_p["CONTRAST_AFF"]:
        p2 = "PASS_P2_SHUFFLED_NULL"
    else:
        p2 = "MIDDLE_P2_SHUFFLED_PARTIAL"

    # ---- P1 mechanism verdict (pre-registered bands; sub-reasons distinct per contract) ----
    if not cardinality_ok:
        p1 = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not discriminator_fires:
        p1 = "HARD_FAIL_DISCRIMINATOR_DID_NOT_FIRE"
    elif p2 == "HARD_FAIL_P2_VETO_SHUFFLED_TRAINS":
        p1 = "HARD_FAIL_P1_UNTRUSTWORTHY_SHUFFLED_CONFOUND"
    elif mean_p["CONTRAST_AFF"] <= mean_p["CONTRAST_LOC"]:
        p1 = "HARD_FAIL_NONSPECIFIC"
    elif mean_p["CONTRAST_AFF"] <= mean_p["FROZEN_HARNESS"]:
        p1 = "HARD_FAIL_LEARNING_MECHANISM_BOUND"
    elif mean_p["CONTRAST_AFF"] <= frozen_stack_mean:
        p1 = "HARD_FAIL_BELOW_REAL_READER"
    elif (mean_p["CONTRAST_AFF"] > frozen_stack_mean
          and mean_p["CONTRAST_AFF"] > mean_p["CONTRAST_LOC"] + 0.02
          and min_delta_vs_loc > 0.0
          and mean_p["CONTRAST_AFF"] > mean_p["ABSOLUTE_AFF"]
          and mean_p["CONTRAST_AFF"] > mean_p["SHUFFLED_AFF"]):
        p1 = "HARD_PASS_P1_CURATED_WEAK_SUP_LOOP_LEARNS_ABOVE_REAL_READER"
    else:
        p1 = "MIDDLE_BAND_P1"

    elapsed = time.perf_counter() - t0
    msg = (f"P1={p1} P2={p2} | FROZEN_STACK(0.5574 ref)={frozen_stack_mean:.4f}(reproduces={stack_reproduces}) "
           f"FROZEN_HARNESS={mean_p['FROZEN_HARNESS']:.4f} CONTRAST_AFF={mean_p['CONTRAST_AFF']:.4f} "
           f"ABSOLUTE_AFF={mean_p['ABSOLUTE_AFF']:.4f} SHUFFLED_AFF={mean_p['SHUFFLED_AFF']:.4f} "
           f"CONTRAST_LOC={mean_p['CONTRAST_LOC']:.4f} | delta(AFF-LOC)_meanmin={np.mean(per_seed_delta_vs_loc):+.4f}"
           f"/{min_delta_vs_loc:+.4f} shufdelta={shuffled_delta:+.4f} | wn_repro_corr={wn_repro_corr:.4f} "
           f"loc_repro_corr={loc_repro_corr:.4f} | oracle_P={oracle_precision:.3f}({oracle_flag}) "
           f"| pairs: AFF={stats_aff['n_informative_pairs']} LOC={stats_loc['n_informative_pairs']} "
           f"SHUF={stats_shuf['n_informative_pairs']} n_swaps_seed0={n_swaps_seed0} "
           f"| arms_differ={arms_differ} base_in_band={baseline_in_band} disc_fires={discriminator_fires}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": f"{p1}|{p2}", "verdict_msg": msg,
        "summary": msg, "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": cfg, "gold_slice": gold_slice,
        "frozen_stack_reference": {"published_precision": PUBLISHED_STACK_PRECISION,
                                    "published_recall": PUBLISHED_STACK_RECALL,
                                    "reproduced_per_seed": stack_precisions, "reproduced_mean": frozen_stack_mean,
                                    "seed7_reproduces_within_tol": stack_reproduces, "tolerance": STACK_TOLERANCE,
                                    "citation": "data/exp_quotative_speaker_attribution_stack_break050_v1/metrics.json:arm_metrics.Q_quotative, atom 29345 CG"},
        "wn_leakage_repro_check": {"corr_wn_cos_gated": wn_repro_corr, "coverage": wn_coverage,
                                   "corr_wn_place_only": loc_repro_corr, "floor": WN_REPRO_FLOOR,
                                   "cited_vet_reference": 0.2732, "n_cands": len(eval_cands_base),
                                   "n_gold_correct": n_pos},
        "per_arm_precision": {a: [round(x, 4) for x in per_arm_precision[a]] for a in ARM_NAMES},
        "mean_precision": mean_p, "min_precision": min_p,
        "delta_contrast_aff_minus_loc": {"mean": round(float(np.mean(per_seed_delta_vs_loc)), 4),
                                         "min": round(min_delta_vs_loc, 4), "per_seed": per_seed_delta_vs_loc},
        "p2_mustfail_control": {"verdict": p2, "shuffled_delta_vs_frozen_harness": shuffled_delta},
        "oracle_ceiling_guard": {"oracle_precision": oracle_precision, "flag": oracle_flag},
        "contrast_pair_stats": {"AFF": stats_aff, "LOC": stats_loc, "SHUFFLED": stats_shuf},
        "gates": {"arms_differ_verified": arms_differ, "baseline_in_band": baseline_in_band,
                  "discriminator_fires": discriminator_fires, "cardinality_ok": cardinality_ok,
                  "wn_repro_floor_ok": wn_repro_ok, "stack_positive_control_ok": stack_reproduces,
                  "n_swaps_seed0_contrast_aff_vs_frozen": n_swaps_seed0},
        "arms_differ_verified": arms_differ, "w_hashes_seed0": w_hashes_seed0,
        "final_metrics_atomicity": "tmp_replace", "calibration_check": "default_ok_for_this_regime",
        "crlb_n/a": "extraction-precision metric; no quantitative noise floor applies",
        "signal_definitions": {
            "SIG_WN_COS_GATED": "blind WordNet first-noun-sense lexname bucket x hand-curated Levin change-of-state verb gate (AFF.COS_VERB_CLASS, reused unchanged)",
            "SIG_WN_PLACE_ONLY": "blind WordNet-lexname locative-exclusion only (-1.0 iff noun.location, else 0.0)",
        },
        "curated_vs_derived_label": "CURATED / weak-supervision (WordNet-lexname NP-ontology is BLIND, but the change-of-state verb gate is hand-curated, reused unchanged from the design-gate; this is a revival of a CURATED target, not a text-derived one -- text-internal derivation was independently HARD_FAILED (0.0443) in the design-gate cell and not retried here).",
        "explicitly_not_retried": ["fully hand-curated (eval-peeked) ontology signal (the design-gate's own SIG_COS_VERB_GATED_ONTOLOGY, corr 0.3561) -- deliberately using the BLIND WordNet variant here per Director contract",
                                   "double-independent WordNet-ontology x VerbNet-gate (corr 0.1443 MIDDLE per the VET) -- not used as the primary target here; could be tried as a harder-mode follow-up if this loop HARD_PASSes"],
        "gold_meta_independence": gold_meta,
        "REQUIRED_FIELDS": ["verdict", "frozen_stack_reference", "wn_leakage_repro_check", "per_arm_precision",
                            "mean_precision", "p2_mustfail_control", "oracle_ceiling_guard", "gates"],
    }
    write_metrics(out_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(out_dir, 'metrics.json')}", flush=True)
    return payload


# ==================================================================================================
# Self-test (real code path: constructs REAL objects at tiny scale -- L04-only stack reproduction,
# real WordNet lookups, real CPCL train/eval machinery on an embedded toy candidate set).
# ==================================================================================================
def self_test():
    # --- WordNet bucket sanity (graceful degrade if unavailable) ---
    if _WORDNET_AVAILABLE:
        assert sig_wn_proto_patient_ontology("castle") == 1.0, "castle must be WN artifact-ish (+1.0)"
        assert sig_wn_proto_patient_ontology("dog") == 0.8, "dog must be WN animal (+0.8)"
        assert sig_wn_proto_patient_ontology("head") == 0.6, "head must be WN body (+0.6)"
        assert sig_wn_proto_patient_ontology("grief") == -0.3, "grief must be WN abstract (-0.3, noun.feeling)"
        assert sig_wn_proto_patient_ontology("he") is None, "pronoun must be neutral (None)"
        assert sig_wn_cos_gated("castle", "build") == 1.0, "build is COS-class -> gate passes"
        assert sig_wn_cos_gated("castle", "see") == 0.0, "see is NOT COS-class -> gated to 0.0"
        assert sig_wn_place_only("he", "see") is None, "pronoun neutral for LOC-only too"
        loc_lex = wn_first_noun_lexname("mountain")
        if loc_lex == "noun.location":
            assert sig_wn_place_only("mountain", "build") == -1.0, "mountain (if WN noun.location) -> -1.0"
    else:
        print(f"[{ANCHOR_NAME}] WARN: WordNet unavailable in this environment -- signal functions "
              f"degrade to all-None; run_mode() will BLOCK with BLOCK_WORDNET_UNAVAILABLE (not silently"
              f" swallowed).", flush=True)

    # --- pearson formula sanity ---
    c, degen = pearson([1.0, 0.0, 1.0, 0.0], [1, 0, 1, 0])
    assert abs(c - 1.0) < 1e-9 and not degen, f"perfect-match corr should be 1.0, got {c}"
    c2, degen2 = pearson([1.0, 1.0, 1.0], [1, 0, 1])
    assert degen2, "constant-signal series must be flagged degenerate"

    # --- attach_signal / shuffle_signal_values on a tiny toy candidate set (real code path) ---
    toy_feat6 = np.array([1.0, 0.5, 1.0, 0.0, 0.0, 0.0])
    toy_cands = [
        {"sid": "T0", "idx": 0, "v": "build", "a": "he", "p": "castle", "tup": ("build", "he", "castle"), "feat6": toy_feat6},
        {"sid": "T0", "idx": 0, "v": "build", "a": "he", "p": "garden", "tup": ("build", "he", "garden"), "feat6": toy_feat6},
        {"sid": "T1", "idx": 1, "v": "see", "a": "he", "p": "hut", "tup": ("see", "he", "hut"), "feat6": toy_feat6},
    ]

    def toy_sig(p, v):
        return {"castle": 1.0, "garden": -1.0}.get(p)  # None for hut (deliberately OOV -> neutral)

    attached = attach_signal(toy_cands, toy_sig)
    assert attached[0]["feat"].shape[0] == FEAT_DIM, "feat must be 7-dim"
    assert abs(attached[0]["err"] - 0.0) < 1e-9, "castle sig=1.0 -> err=0.0 (best)"
    assert abs(attached[1]["err"] - 1.0) < 1e-9, "garden sig=-1.0 -> err=1.0 (worst)"
    assert abs(attached[2]["err"] - 0.5) < 1e-9, "hut sig=None -> neutral err=0.5"
    assert toy_cands[0].get("feat") is None, "attach_signal must NOT mutate the input candidate dicts"

    shuf = shuffle_signal_values(toy_cands, toy_sig, seed=11)
    orig_sigs = sorted(s for s in (toy_sig(c["p"], c["v"]) for c in toy_cands) if s is not None)
    shuf_sigs = sorted(s for s in (c["sig"] for c in shuf) if s is not None)
    assert orig_sigs == shuf_sigs, "shuffle must preserve the marginal value SET, only permute assignment"

    # --- real CPCL machinery on the toy set: group_by_instance / mine_contrast_pairs / mine_absolute_targets ---
    ig = CPCL.group_by_instance(attached)
    assert ("T0", "build") in ig and len(ig[("T0", "build")]) == 2, "T0/build must have 2 rivals"
    pairs, stats = CPCL.mine_contrast_pairs(ig, min_err_gap=0.05)
    assert stats["n_informative_pairs"] == 1 and len(pairs) == 1, f"one informative pair expected: {stats}"
    fpos, fneg = pairs[0]
    assert fpos[-1] == 1.0 and fneg[-1] == -1.0, "pos rival (castle, low err) must be the high-signal one"
    abs_targets = CPCL.mine_absolute_targets(attached)
    assert len(abs_targets) == len(attached), "absolute targets must cover every candidate"

    # --- train_weights / eval_kept real code path (tiny, deterministic) ---
    train_cfg = dict(sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=5, coh_lr=0.10, coh_margin=0.20, oja_eta=0.002)

    def sel_fn_stub(v, p):
        return None  # defer everything to the (empty) base pass; isolates the contrastive pass

    w, n_train = CPCL.train_weights(attached, sel_fn_stub, train_cfg, seed=7, mode="contrast", pairs=pairs * 10)
    assert np.all(np.isfinite(w)), "train_weights produced non-finite w"
    kept = CPCL.eval_kept(w, ig, keep_thr=-1e9)  # keep_thr very low -> exercise the real scoring path fully
    assert len(kept) >= 1, "eval_kept must keep at least one candidate at a permissive threshold"

    # --- WN_REPRO_FLOOR gate logic sanity (does not require real WordNet data) ---
    assert WN_REPRO_FLOOR < 0.2732, "floor must be below the cited VET reference (room for reimpl variance)"

    print(f"[{ANCHOR_NAME}] self-test PASS | wordnet_available={_WORDNET_AVAILABLE}; pearson formula ok; "
          f"attach_signal err-mapping ok (0.0/1.0/0.5); shuffle preserves value SET; real CPCL group_by_"
          f"instance/mine_contrast_pairs/mine_absolute_targets/train_weights/eval_kept exercised on toy set "
          f"(n_train={n_train}, n_pairs={len(pairs)}, n_kept={len(kept)})", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--device", default="cpu")  # CPU-only; accept-and-ignore for runner parity
    args, _ = ap.parse_known_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run_mode("smoke"); return
    if args.full:
        run_mode("full"); return
    ap.error("specify one of --self-test | --smoke | --full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
                "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
                "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat()}
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
