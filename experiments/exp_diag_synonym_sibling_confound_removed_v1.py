# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: random-init reps / trained reps / scrambled reps pairwise hash-distinct
#   (_arms_must_differ, sha256 over the full rep matrix bytes)
# - final_metrics_atomicity = tmp_replace (single-shot, os.replace)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a: AUC discriminator base=0.5 exactly (Mann-Whitney definition); scramble control
#   witnesses the empirical near-chance floor directly (same convention as f6c6c843e)
# - baseline_in_band: n/a (no accuracy-metric baseline arm); analogue = scramble-near-chance gate
# - discriminator survives scale: FULL uses the whole 14.6M-line corpus + the deepest candidate
#   pools (700-pair synonym scan, 30 sibling categories); self-test/smoke use small deterministic
#   subsets for fast iteration
# - HP_SCOPE: decisive_randinit_AUC + decisive_scramble_control + concreteness_balanced_decisive
#   are the HARD gates (see pre-reg envelope); MAIN-set AUC + trained-arm AUC are reported,
#   non-gating context
# - cardinality_ok: EXPECTED_N_UNITS = 2 pair-sets (MAIN, DECISIVE) x 2 encoder-arms + 1 grounding
#   arm (on DECISIVE) + 1 scramble arm (on DECISIVE); logged + verified against actual counts
# - calibration_check: adaptive_with_discriminator_gate (held-out P25 threshold computed from
#   this run's own measured true-count distribution; decisive_power_ok is the discriminator-
#   still-fires check -- an empty/degenerate pool correctly fails it, does not silently pass)
# - all numbers in this header/docstring tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL checkpoint + REAL bounded ARC-corpus scan + REAL
#   encode_concept_text_reps call + REAL balanced_match selection at tiny scale (real_code_path)
# - substrate_signature_checked: TinyTransformer(**model_cfg-derived kwargs), encode_concept_
#   text_reps(...), grounded_vector(word), build_synonym_candidates(wn, exclude_words, max_pairs)
#   (imported from f6c6c843e's cell, signature bound not hand-typed)
# - no hdlab/ file OTHER than read-only imports is touched; no capability_registry.jsonl write
"""exp_diag_synonym_sibling_confound_removed_v1 -- STANDALONE diagnostic (NOT a wiring cell):
decisive follow-up to f6c6c843e (diag_learned_encoder_synonym_sibling_deep_wall_v1,
MIDDLE_BAND_INTERFACE_SEPARATES_BUT_NOT_LEARNING). That cell found the corpus-mention
distributional-pooling INTERFACE separates synonym pairs from sibling pairs at AUC=0.7064
(trained) / 0.7452 (random-init, same interface) -- far above sensorimotor-norm grounding
(0.3186, below chance) -- but flagged two confounds: (a) the sibling probes are +1.60
Brysbaert-concreteness-z MORE concrete than the synonym probes (the AUC may be an
abstract-vs-concrete axis, not same-idea-vs-same-category); (b) every probe word had >=10-24
corpus mentions, i.e. very likely inside MLM training exposure, not held out.

THIS cell removes both confounds by construction:
1. CONCRETENESS-BALANCED pair construction: sibling candidates drawn from 30 WordNet categories
   (17 concrete + 13 abstract, superset of f6c6c843e's 9 all-concrete categories) instead of a
   hand-picked concrete-only list; synonym candidates drawn from a much DEEPER wn.all_synsets()
   scan (max_pairs=700 vs f6c6c843e's 60) so the pool isn't dominated by WordNet's noun.Tops
   abstract top-level file (the actual root cause of the original concreteness skew). Both pools
   are then matched via binned equal-count selection over 5 Brysbaert-concreteness-z bins
   (balanced_match) -- the MAIN set.
2. HELD-OUT slice: a single corpus pass tracks UNCAPPED true mention counts (f6c6c843e only
   tracked capped counts, capped at 24, so it could not see true exposure). The MAIN candidate
   pool is further restricted to words at/below the 25th percentile of measured true-count (a
   principled, self-calibrating "low corpus exposure" split, per this cell's own honest-scoping
   precedent -- NOT a claim to reproduce the training pipeline's official ~800-concept held-out
   split, which requires the full CSKG universe and is out of scope for a standalone diagnostic).
   balanced_match is applied again within this restricted pool -- the DECISIVE set.
3. Same pooling interface as f6c6c843e (TinyTransformer.pooled() via encode_concept_text_reps,
   imported directly). PRIMARY arm = RANDOM-INIT same-architecture encoder (per task direction:
   f6c6c843e already showed random-init >= trained, so this is a fair test of the INTERFACE
   claim on its own terms). SECONDARY arm = TRAINED checkpoint, reported for context.
4. Controls: SCRAMBLE (fixed-seed permutation, collapses to chance if gate is genuine per-word
   effect), GROUNDING (raw Brysbaert/Lancaster cosine on the same DECISIVE pairs), positive
   control (apple/orange, happy/joyful raw-cosine replication, cited from f6c6c843e).

See preregs/2026-08-11_diag_synonym_sibling_confound_removed_v1.md for the full envelope.

Modes: --self-test (real checkpoint + tiny real corpus scan, <30s) / --smoke (moderate scan,
fast dev-iteration, DECISIVE set may legitimately be small/empty at this scope) / (no flag,
default) = FULL (whole-corpus scan, deepest candidate pools, THE decisive number).

HARD INVARIANTS: STANDALONE diagnostic -- does NOT modify hdlab/lexical_similarity.py,
hdlab/grounded_similarity.py, or data/capability_registry.jsonl (a confirmed concurrent session
holds those; this cell only imports them + f6c6c843e's cell read-only). Glass-box (owned
from-scratch checkpoint architecture, zero external LLM calls). Deterministic (fixed int seeds;
sorted()/sorted(set()) discipline throughout; no built-in hash() anywhere). Runs LOCAL, inline,
foreground only -- no queue_add, no remote, no push. ASCII-only.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

ANCHOR_NAME = "diag_synonym_sibling_confound_removed_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.exp_scale_meaning_learn_arc_heldout_v3_relobj import (  # noqa: E402
    TinyTransformer, encode_concept_text_reps, _auc_from_scores,
    _WORD_RE, _quality_ok, _line_hash, ARC_CORPUS,
)
from experiments.exp_diag_learned_encoder_synonym_sibling_deep_wall_v1 import (  # noqa: E402
    build_synonym_candidates, raw_grounded_cosine, load_encoder, build_random_init_encoder,
    compute_reps, auc_dprime, POS_CTRL_PAIRS, POS_CTRL_TOL,
)
from experiments.exp_grounded_meaning_wire_lexical_fallback_v1 import _eligible  # noqa: E402
from hdlab.grounded_similarity import grounded_vector  # noqa: E402

ANCHOR_ORIGIN_METRICS = os.path.join(
    REPO_ROOT, "data", "exp_diag_learned_encoder_synonym_sibling_deep_wall_v1", "metrics.json")

# CITED@d:/AI/hd-instrument/data/exp_diag_learned_encoder_synonym_sibling_deep_wall_v1/metrics.json
CITED_ORIGINAL = dict(
    encoder_auc_trained_confounded=0.7064,
    randinit_auc_confounded=0.7452,
    grounding_auc_matched=0.3186,
    scramble_auc=0.5042,
    conc_z_gap_sibling_minus_synonym=1.6022158963360675,
    chance_auc=0.5,
)

# ------------------------------------------------------------------------------------ categories
CONCRETE_CATEGORIES = [
    "fruit.n.01", "vehicle.n.01", "furniture.n.01", "metal.n.01", "fuel.n.01", "hand_tool.n.01",
    "bird.n.01", "beverage.n.01", "vegetable.n.01", "weapon.n.01", "garment.n.01", "insect.n.01",
    "tree.n.01", "flower.n.01", "container.n.01", "instrumentality.n.03", "mammal.n.01",
]
ABSTRACT_CATEGORIES = [
    "emotion.n.01", "feeling.n.01", "state.n.02", "trait.n.01", "quality.n.01", "relation.n.01",
    "activity.n.01", "act.n.02", "belief.n.01", "cognitive_state.n.01",
    "psychological_feature.n.01", "abstraction.n.06", "attribute.n.02",
]
SIBLING_CATEGORIES = CONCRETE_CATEGORIES + ABSTRACT_CATEGORIES

CONC_BIN_EDGES = [-4.0, -1.2, -0.4, 0.4, 1.2, 4.0]
HELD_OUT_PERCENTILE = 25.0

SCRAMBLE_SEED = 30260811
RANDINIT_SEED = 30260812

# Envelope bands (pre-reg 2026-08-11_diag_synonym_sibling_confound_removed_v1.md)
POWER_FLOOR_MAIN_N = 12
POWER_FLOOR_DECISIVE_N = 8
HP_AUC_MIN = 0.65
HF_AUC_MAX = 0.56
NEAR_CHANCE_BAND = (0.40, 0.60)
CONCRETENESS_BALANCE_TOL = 0.3

# ---------------------------------------------------------------------------------- config profiles
SELFTEST_CFG = dict(
    run_mode="self_test", max_scan_lines=1_000_000, cap_mentions=4,
    min_mentions_main=1, min_mentions_heldout_floor=1,
    sibling_categories=(CONCRETE_CATEGORIES[:4] + ABSTRACT_CATEGORIES[:2]),
    per_cat_cap=1, synonym_pool_max=20,
    per_bin_cap_main=1, per_bin_cap_heldout=1, encode_batch=16,
)
SMOKE_CFG = dict(
    run_mode="smoke", max_scan_lines=3_000_000, cap_mentions=12,
    min_mentions_main=3, min_mentions_heldout_floor=1,
    sibling_categories=SIBLING_CATEGORIES,
    per_cat_cap=3, synonym_pool_max=300,
    per_bin_cap_main=4, per_bin_cap_heldout=3, encode_batch=64,
)
# FULL is the whole-corpus scan (the load-bearing part: the held-out/exposure split must be
# measured over the real 14.6M-line corpus). cap_mentions=12 (proven in smoke; a stable pooled
# rep) + synonym_pool_max=300 (smoke showed 300 already yields a well-balanced MAIN set with
# gap 0.040, and the DECISIVE synonym side had 33 candidates -- the sibling side is the
# bottleneck, unaffected by synonym pool depth) are a foreground-fit scope reduction EXPLICITLY
# pre-registered in the pre-reg's Compute-architecture section (keeps the run inside one <=10-min
# foreground call per the INLINE-LOCAL mandate; cap=24/pool=700 would auto-background = forbidden).
FULL_CFG = dict(
    run_mode="full", max_scan_lines=None, cap_mentions=12,
    min_mentions_main=10, min_mentions_heldout_floor=2,
    sibling_categories=SIBLING_CATEGORIES,
    per_cat_cap=4, synonym_pool_max=300,
    per_bin_cap_main=6, per_bin_cap_heldout=6, encode_batch=128,
)


# --------------------------------------------------------------------------------- start/crash/log
def get_output_dir(run_mode: str) -> str:
    suffix = {"self_test": "_selftest", "smoke": "_smoke", "full": ""}[run_mode]
    return os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME + suffix)


def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
    import platform
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: str, exc: BaseException) -> None:
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _atomic_write(output_dir: str, metrics: Dict) -> str:
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)
    return final


def _log(msg: str) -> None:
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _arms_must_differ(arms: Dict[str, np.ndarray]) -> Dict[str, str]:
    digests = {name: hashlib.sha256(arr.tobytes()).hexdigest() for name, arr in arms.items()}
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], (
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical" % (a, b))
    return digests


# ---------------------------------------------------------------------------------- pair construction
def build_sibling_pool_diverse(wn, categories: List[str], per_cat_cap: int
                               ) -> List[Tuple[str, str, str]]:
    """(word_a, word_b, category) co-hyponym pairs across a DIVERSE (concrete+abstract) category
    list. Deterministic: sorted(set()) of each category's eligible direct-hyponym lemma words,
    consecutive non-overlapping pairs taken up to per_cat_cap. No random sampling."""
    pairs: List[Tuple[str, str, str]] = []
    for catname in categories:
        try:
            cat = wn.synset(catname)
        except Exception:
            continue
        words = sorted({lm.name().lower() for h in cat.hyponyms() for lm in h.lemmas()
                        if "_" not in lm.name()})
        cand = sorted(w for w in words if _eligible(w))
        n_here = min(per_cat_cap, len(cand) // 2)
        for i in range(n_here):
            pairs.append((cand[2 * i], cand[2 * i + 1], catname))
    return pairs


def _conc_z(word: str) -> Optional[float]:
    v = grounded_vector(word)
    return float(v[-1]) if v is not None else None


def _pair_conc(a: str, b: str) -> Optional[float]:
    ca, cb = _conc_z(a), _conc_z(b)
    if ca is None or cb is None:
        return None
    return 0.5 * (ca + cb)


def balanced_match(syn_items: List[Tuple[str, str, float]], sib_items: List[Tuple[str, str, float]],
                   bin_edges: List[float], per_bin_cap: int
                   ) -> Tuple[List[Tuple[str, str, float]], List[Tuple[str, str, float]], List[Dict]]:
    """Bin both pools into the SAME concreteness bins; take an EQUAL count from each class per
    bin (min(n_syn_avail, n_sib_avail, per_bin_cap)), deterministic sort within each bin. Equal
    per-bin counts guarantee matched concreteness DISTRIBUTIONS by construction."""
    def bin_of(c: float) -> int:
        for i in range(len(bin_edges) - 1):
            if c < bin_edges[i + 1]:
                return i
        return len(bin_edges) - 2

    syn_bins: Dict[int, List] = {}
    sib_bins: Dict[int, List] = {}
    for item in syn_items:
        syn_bins.setdefault(bin_of(item[2]), []).append(item)
    for item in sib_items:
        sib_bins.setdefault(bin_of(item[2]), []).append(item)

    syn_sel: List = []
    sib_sel: List = []
    per_bin_report: List[Dict] = []
    for bi in sorted(set(syn_bins) | set(sib_bins)):
        s_list = sorted(syn_bins.get(bi, []), key=lambda t: (t[2], t[0], t[1]))
        b_list = sorted(sib_bins.get(bi, []), key=lambda t: (t[2], t[0], t[1]))
        k = min(len(s_list), len(b_list), per_bin_cap)
        syn_sel.extend(s_list[:k])
        sib_sel.extend(b_list[:k])
        per_bin_report.append(dict(bin=bi, bin_range=[bin_edges[bi], bin_edges[bi + 1]],
                                   n_syn_avail=len(s_list), n_sib_avail=len(b_list), n_taken=k))
    return syn_sel, sib_sel, per_bin_report


# ---------------------------------------------------------------------------------- corpus scan
def scan_postings_uncapped(max_scan_lines: Optional[int], cap_mentions: int,
                           target_words: List[str]
                           ) -> Tuple[List[List[str]], List[int], Dict[str, int], int, float]:
    """Single bounded pass over ARC_Corpus.txt. Returns capped postings (for pooling) AND
    UNCAPPED true mention counts (for the held-out-exposure split) -- f6c6c843e only tracked
    capped counts. Reuses training-cell tokenization/quality-filter/dedup convention."""
    surf_to_idx = {w: i for i, w in enumerate(target_words)}
    K = len(target_words)
    postings: List[List[str]] = [[] for _ in range(K)]
    true_counts = [0] * K
    dedup_cap = 2_000_000
    seen_hash = set()
    n_read = 0
    t0 = time.perf_counter()
    key_set = set(surf_to_idx.keys())
    with open(ARC_CORPUS, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            if max_scan_lines is not None and n_read >= max_scan_lines:
                break
            n_read += 1
            line = raw.strip()
            if not line:
                continue
            words = _WORD_RE.findall(line.lower())
            if not _quality_ok(line, words):
                continue
            hit = set(words) & key_set
            if not hit:
                continue
            h = _line_hash(line)
            if h in seen_hash:
                continue
            if len(seen_hash) < dedup_cap:
                seen_hash.add(h)
            for w in hit:
                idx = surf_to_idx[w]
                true_counts[idx] += 1
                if len(postings[idx]) < cap_mentions:
                    postings[idx].append(line)
            if n_read % 2_000_000 == 0:
                _log("  scan progress: %d lines (%.1fs)" % (n_read, time.perf_counter() - t0))
    return postings, true_counts, surf_to_idx, n_read, time.perf_counter() - t0


# ---------------------------------------------------------------------------------- scoring helpers
def pair_cosines(reps: np.ndarray, word_to_idx: Dict[str, int],
                 pairs: List[Tuple[str, str]]) -> Tuple[List[float], List[Tuple[str, str]]]:
    scores, used = [], []
    for a, b in pairs:
        ia, ib = word_to_idx.get(a), word_to_idx.get(b)
        if ia is None or ib is None:
            continue
        scores.append(float(np.dot(reps[ia], reps[ib])))
        used.append((a, b))
    return scores, used


def _in_band(x: Optional[float], band: Tuple[float, float]) -> bool:
    return x is not None and band[0] <= x <= band[1]


def _stat(vals: List[int]) -> Dict:
    if not vals:
        return dict(n=0, mean=None, median=None, min=None, max=None)
    arr = np.asarray(vals, dtype=np.float64)
    return dict(n=int(len(arr)), mean=float(arr.mean()), median=float(np.median(arr)),
               min=int(arr.min()), max=int(arr.max()))


# ---------------------------------------------------------------------------------- main pipeline
def run_diagnostic(cfg: Dict) -> Dict:
    run_mode = cfg["run_mode"]
    out_dir = get_output_dir(run_mode)
    os.makedirs(out_dir, exist_ok=True)
    t_start = time.perf_counter()

    import nltk  # noqa: E402
    from nltk.corpus import wordnet as wn  # noqa: E402

    device = torch.device("cpu")  # deterministic CPU-only diagnostic (INLINE-LOCAL mandate)

    # ---------------------------------------------------------------- A) concreteness-balanced pools
    _log("run_mode=%s: building sibling candidate pool (%d categories)..."
        % (run_mode, len(cfg["sibling_categories"])))
    sibling_pool_raw = build_sibling_pool_diverse(wn, cfg["sibling_categories"], cfg["per_cat_cap"])
    sibling_words_all = sorted({w for a, b, c in sibling_pool_raw for w in (a, b)})
    _log("  sibling_pool_raw n_pairs=%d n_words=%d" % (len(sibling_pool_raw), len(sibling_words_all)))

    _log("building synonym candidate pool (deep wn.all_synsets scan, max_pairs=%d)..."
        % cfg["synonym_pool_max"])
    synonym_pool_raw = build_synonym_candidates(wn, set(sibling_words_all), cfg["synonym_pool_max"])
    _log("  synonym_pool_raw n_pairs=%d" % len(synonym_pool_raw))

    sib_cat_lookup = {(a, b): c for a, b, c in sibling_pool_raw}
    sib_pool: List[Tuple[str, str, float]] = []
    for a, b, c in sibling_pool_raw:
        pc = _pair_conc(a, b)
        if pc is not None:
            sib_pool.append((a, b, pc))
    syn_pool: List[Tuple[str, str, float]] = []
    for a, b in synonym_pool_raw:
        pc = _pair_conc(a, b)
        if pc is not None:
            syn_pool.append((a, b, pc))
    _log("  concreteness-annotated: sib_pool=%d syn_pool=%d" % (len(sib_pool), len(syn_pool)))

    # ---------------------------------------------------------------- positive control
    _log("positive control: replicate f6c6c843e's cited raw grounded cosine...")
    pos_ctrl = []
    pos_ctrl_ok = True
    for a, b, cited in POS_CTRL_PAIRS:
        got = raw_grounded_cosine(a, b)
        ok = (got is not None) and (abs(got - cited) < POS_CTRL_TOL)
        pos_ctrl_ok = pos_ctrl_ok and ok
        pos_ctrl.append({"a": a, "b": b, "cited": cited, "measured": got, "ok": ok})
    _log("  positive_control_ok=%s" % pos_ctrl_ok)

    # ---------------------------------------------------------------- corpus scan (uncapped counts)
    target_words = sorted({w for a, b, c in sib_pool for w in (a, b)}
                          | {w for a, b, c in syn_pool for w in (a, b)})
    _log("scanning ARC corpus for %d target words (max_scan_lines=%s, cap_mentions=%d)..."
        % (len(target_words), cfg["max_scan_lines"], cfg["cap_mentions"]))
    postings, true_counts, surf_to_idx, n_read, scan_s = scan_postings_uncapped(
        cfg["max_scan_lines"], cfg["cap_mentions"], target_words)
    count_by_word = dict(zip(target_words, true_counts))
    _log("  scanned %d lines in %.1fs" % (n_read, scan_s))

    # ---------------------------------------------------------------- MAIN set (concreteness-balanced)
    sib_main_cand = [(a, b, pc) for a, b, pc in sib_pool
                     if count_by_word.get(a, 0) >= cfg["min_mentions_main"]
                     and count_by_word.get(b, 0) >= cfg["min_mentions_main"]]
    syn_main_cand = [(a, b, pc) for a, b, pc in syn_pool
                     if count_by_word.get(a, 0) >= cfg["min_mentions_main"]
                     and count_by_word.get(b, 0) >= cfg["min_mentions_main"]]
    syn_main_sel, sib_main_sel, main_bin_report = balanced_match(
        syn_main_cand, sib_main_cand, CONC_BIN_EDGES, cfg["per_bin_cap_main"])
    _log("  MAIN candidates: syn=%d sib=%d -> selected syn=%d sib=%d"
        % (len(syn_main_cand), len(sib_main_cand), len(syn_main_sel), len(sib_main_sel)))

    # ---------------------------------------------------------------- held-out threshold (adaptive P25)
    elig_counts = [count_by_word[w] for w in target_words
                  if count_by_word[w] >= cfg["min_mentions_heldout_floor"]]
    p25 = float(np.percentile(elig_counts, HELD_OUT_PERCENTILE)) if elig_counts else None
    n_zero_mention = sum(1 for w in target_words if count_by_word[w] == 0)
    _log("  held-out P25 threshold=%s (over %d eligible words, floor=%d); n_zero_mention_words=%d"
        % (p25, len(elig_counts), cfg["min_mentions_heldout_floor"], n_zero_mention))

    def _is_heldout_word(w: str) -> bool:
        c = count_by_word.get(w, -1)
        return p25 is not None and cfg["min_mentions_heldout_floor"] <= c <= p25

    sib_heldout_cand = [(a, b, pc) for a, b, pc in sib_pool if _is_heldout_word(a) and _is_heldout_word(b)]
    syn_heldout_cand = [(a, b, pc) for a, b, pc in syn_pool if _is_heldout_word(a) and _is_heldout_word(b)]
    syn_decisive_sel, sib_decisive_sel, decisive_bin_report = balanced_match(
        syn_heldout_cand, sib_heldout_cand, CONC_BIN_EDGES, cfg["per_bin_cap_heldout"])
    _log("  DECISIVE (held-out) candidates: syn=%d sib=%d -> selected syn=%d sib=%d"
        % (len(syn_heldout_cand), len(sib_heldout_cand), len(syn_decisive_sel), len(sib_decisive_sel)))

    # ---------------------------------------------------------------- encode: union of MAIN+DECISIVE words
    eval_words = sorted({w for a, b, pc in (syn_main_sel + sib_main_sel + syn_decisive_sel + sib_decisive_sel)
                         for w in (a, b)})
    word_to_idx = {w: i for i, w in enumerate(eval_words)}
    eval_postings = [postings[surf_to_idx[w]] for w in eval_words]
    _log("  eval_words (union MAIN+DECISIVE) n=%d" % len(eval_words))

    _log("loading checkpoint (tokenizer/model_cfg/spec; trained weights for secondary arm)...")
    model_trained, tok, spec, model_cfg, ckpt = load_encoder(device)
    _log("  model params=%.2fM d_model=%d n_layers=%d vocab=%d"
        % (sum(p.numel() for p in model_trained.parameters()) / 1e6,
           model_cfg["d_model"], model_cfg["n_layers"], model_cfg["vocab"]))

    _log("encoding with PRIMARY arm: RANDOM-INIT same-architecture encoder (interface probe)...")
    model_rand = build_random_init_encoder(model_cfg, device, RANDINIT_SEED)
    t0 = time.perf_counter()
    reps_rand, cnt_rand = compute_reps(model_rand, tok, eval_postings, cfg["cap_mentions"],
                                       model_cfg["max_len"], cfg["encode_batch"], device, spec)
    _log("  RANDOM_INIT encode: %d words in %.1fs" % (len(eval_words), time.perf_counter() - t0))
    assert bool((cnt_rand > 0).all()), "COVERAGE FAILURE: a filtered-in word got 0 pooled mentions"

    _log("encoding with SECONDARY arm: TRAINED checkpoint (context, non-gating)...")
    t0 = time.perf_counter()
    reps_trained, cnt_trained = compute_reps(model_trained, tok, eval_postings, cfg["cap_mentions"],
                                             model_cfg["max_len"], cfg["encode_batch"], device, spec)
    _log("  TRAINED encode: %d words in %.1fs" % (len(eval_words), time.perf_counter() - t0))

    # ---------------------------------------------------------------- scramble control (fixed seed)
    rng = np.random.default_rng(SCRAMBLE_SEED)
    perm = rng.permutation(len(eval_words))
    reps_scrambled = reps_rand[perm]

    # ---------------------------------------------------------------- score MAIN + DECISIVE, all arms
    def _score_set(syn_sel, sib_sel, reps, label):
        syn_pairs = [(a, b) for a, b, pc in syn_sel]
        sib_pairs = [(a, b) for a, b, pc in sib_sel]
        syn_scores, syn_used = pair_cosines(reps, word_to_idx, syn_pairs)
        sib_scores, sib_used = pair_cosines(reps, word_to_idx, sib_pairs)
        result = auc_dprime(syn_scores, sib_scores)
        result["label"] = label
        result["syn_used"] = [list(t) for t in syn_used]
        result["sib_used"] = [list(t) for t in sib_used]
        return result

    main_randinit = _score_set(syn_main_sel, sib_main_sel, reps_rand, "main_randinit")
    main_trained = _score_set(syn_main_sel, sib_main_sel, reps_trained, "main_trained")
    decisive_randinit = _score_set(syn_decisive_sel, sib_decisive_sel, reps_rand, "decisive_randinit")
    decisive_trained = _score_set(syn_decisive_sel, sib_decisive_sel, reps_trained, "decisive_trained")
    decisive_scramble = _score_set(syn_decisive_sel, sib_decisive_sel, reps_scrambled, "decisive_scramble")
    main_scramble = _score_set(syn_main_sel, sib_main_sel, reps_scrambled, "main_scramble")

    # grounding on DECISIVE pairs (raw cosine, matched pairs)
    decisive_syn_pairs = [(a, b) for a, b, pc in syn_decisive_sel]
    decisive_sib_pairs = [(a, b) for a, b, pc in sib_decisive_sel]
    syn_scores_g = [raw_grounded_cosine(a, b) for a, b in decisive_syn_pairs]
    sib_scores_g = [raw_grounded_cosine(a, b) for a, b in decisive_sib_pairs]
    syn_scores_g = [s for s in syn_scores_g if s is not None]
    sib_scores_g = [s for s in sib_scores_g if s is not None]
    decisive_grounding = auc_dprime(syn_scores_g, sib_scores_g)
    decisive_grounding["label"] = "decisive_grounding"

    # ---------------------------------------------------------------- arms-must-differ
    arm_digests = _arms_must_differ({
        "random_init": reps_rand, "trained": reps_trained, "scrambled": reps_scrambled})

    # ---------------------------------------------------------------- concreteness balance (achieved)
    def _conc_balance(syn_sel, sib_sel):
        syn_c = [pc for a, b, pc in syn_sel]
        sib_c = [pc for a, b, pc in sib_sel]
        m_syn = float(np.mean(syn_c)) if syn_c else None
        m_sib = float(np.mean(sib_c)) if sib_c else None
        gap = (m_sib - m_syn) if (m_syn is not None and m_sib is not None) else None
        return dict(mean_conc_z_synonym=m_syn, mean_conc_z_sibling=m_sib,
                   conc_z_gap_sibling_minus_synonym=gap,
                   balanced=(gap is not None and abs(gap) < CONCRETENESS_BALANCE_TOL))

    main_conc_balance = _conc_balance(syn_main_sel, sib_main_sel)
    decisive_conc_balance = _conc_balance(syn_decisive_sel, sib_decisive_sel)
    _log("  MAIN concreteness gap(sib-syn)=%s  DECISIVE concreteness gap(sib-syn)=%s"
        % (main_conc_balance["conc_z_gap_sibling_minus_synonym"],
           decisive_conc_balance["conc_z_gap_sibling_minus_synonym"]))

    # ---------------------------------------------------------------- exposure / train-overlap honesty
    def _words_of(sel):
        return sorted({w for a, b, pc in sel for w in (a, b)})

    main_words = _words_of(syn_main_sel + sib_main_sel)
    decisive_words = _words_of(syn_decisive_sel + sib_decisive_sel)
    train_overlap = dict(
        scan_scope="bounded single pass over data/corpora/arc/.../ARC_Corpus.txt (%s lines of "
                   "14,621,856 total); true (uncapped) mention counts, unlike f6c6c843e which only "
                   "tracked capped counts (cap=24)." % ("all" if cfg["max_scan_lines"] is None else str(n_read)),
        n_read=n_read,
        held_out_percentile=HELD_OUT_PERCENTILE,
        held_out_threshold_true_count=p25,
        n_zero_mention_words_in_candidate_pool=n_zero_mention,
        main_set_true_count_stats=_stat([count_by_word[w] for w in main_words]),
        decisive_set_true_count_stats=_stat([count_by_word[w] for w in decisive_words]),
        original_confounded_set_note=("f6c6c843e's 38 probe words were ALL capped at cap_mentions=24 "
                                      "(i.e. true count >= 24 for every one, by construction of its "
                                      "min_mentions=10 floor with no upper visibility) -- this cell's "
                                      "DECISIVE set true-count stats above should be read against that."),
        held_out_split_membership_note=(
            "This is an adaptive, self-calibrating LOW-CORPUS-EXPOSURE split (bottom %.0f-th "
            "percentile of measured true mention count among this run's own candidate pool), NOT a "
            "reproduction of the training pipeline's official ~800-concept held-out split (that "
            "requires the full CSKG universe + a second full corpus pass, out of scope for a "
            "standalone diagnostic -- same honest-scoping precedent as f6c6c843e). Scope the "
            "DECISIVE-set claim accordingly: it measures whether the pooling interface separates "
            "synonym from sibling for words with LOW (not necessarily zero) measured corpus "
            "exposure, relative to this candidate pool." % HELD_OUT_PERCENTILE),
    )

    # ---------------------------------------------------------------- verdict
    n_syn_dec, n_sib_dec = decisive_randinit["n_syn"], decisive_randinit["n_sib"]
    n_syn_main, n_sib_main = main_randinit["n_syn"], main_randinit["n_sib"]
    decisive_power_ok = (n_syn_dec >= POWER_FLOOR_DECISIVE_N) and (n_sib_dec >= POWER_FLOOR_DECISIVE_N)
    main_power_ok = (n_syn_main >= POWER_FLOOR_MAIN_N) and (n_sib_main >= POWER_FLOOR_MAIN_N)

    dec_auc = decisive_randinit["auc"]
    dec_dprime = decisive_randinit["d_prime"]
    dec_scr_auc = decisive_scramble["auc"]
    conc_bal_dec = decisive_conc_balance["balanced"]

    gate_scramble = _in_band(dec_scr_auc, NEAR_CHANCE_BAND)
    gate_dprime_pos = (dec_dprime is not None and dec_dprime > 0)

    if not decisive_power_ok:
        verdict = "MIDDLE_BAND_HELDOUT_UNDERPOWERED"
        vmsg = ("DECISIVE (concreteness-balanced + held-out) set underpowered: n_syn=%d n_sib=%d "
               "(need >=%d each). MAIN (concreteness-balanced only) set: n_syn=%d n_sib=%d, "
               "randinit_AUC=%s (power_ok=%s), gap(sib-syn)=%s -- reported as secondary, "
               "non-gating context isolating whether concreteness alone (independent of exposure) "
               "explains the original 0.71."
               % (n_syn_dec, n_sib_dec, POWER_FLOOR_DECISIVE_N, n_syn_main, n_sib_main,
                  main_randinit["auc"], main_power_ok,
                  main_conc_balance["conc_z_gap_sibling_minus_synonym"]))
    elif not pos_ctrl_ok:
        verdict = "MIDDLE_BAND_POSITIVE_CONTROL_FAILED"
        vmsg = "grounding-baseline reimplementation positive control failed: %r" % pos_ctrl
    elif dec_auc is not None and dec_auc <= HF_AUC_MAX:
        verdict = "HARD_FAIL_CONFOUND_WAS_THE_SIGNAL"
        vmsg = ("decisive_randinit_AUC=%.4f <= %.2f (collapses to at/near chance) once concreteness "
               "is balanced (gap=%s, tol=%.2f) AND corpus exposure is restricted to the bottom %.0f "
               "pct (n_syn=%d n_sib=%d) -- the original confounded encoder_AUC=%.4f was largely a "
               "concreteness/exposure artifact. The deep same-idea wall STILL STANDS."
               % (dec_auc, HF_AUC_MAX, decisive_conc_balance["conc_z_gap_sibling_minus_synonym"],
                  CONCRETENESS_BALANCE_TOL, HELD_OUT_PERCENTILE, n_syn_dec, n_sib_dec,
                  CITED_ORIGINAL["encoder_auc_trained_confounded"]))
    elif (dec_auc is not None and dec_auc >= HP_AUC_MIN and gate_dprime_pos
         and gate_scramble and conc_bal_dec):
        verdict = "HARD_PASS_CONFOUND_REMOVED_SIGNAL_SURVIVES"
        vmsg = ("decisive_randinit_AUC=%.4f (d'=%.3f) clears >= %.2f with concreteness BALANCED "
               "(gap=%s, |gap|<%.2f) AND corpus exposure restricted to the bottom %.0f pct "
               "(n_syn=%d n_sib=%d), scramble_AUC=%.4f near-chance -- the distributional-pooling "
               "same-idea signal SURVIVES both confound removals. The deep same-idea wall IS "
               "crossable glass-box by this owned interface, genuinely (not a concreteness/exposure "
               "artifact). original_confounded_AUC=%.4f for comparison."
               % (dec_auc, dec_dprime, HP_AUC_MIN,
                  decisive_conc_balance["conc_z_gap_sibling_minus_synonym"], CONCRETENESS_BALANCE_TOL,
                  HELD_OUT_PERCENTILE, n_syn_dec, n_sib_dec, dec_scr_auc,
                  CITED_ORIGINAL["encoder_auc_trained_confounded"]))
    else:
        verdict = "MIDDLE_BAND_PARTIAL"
        vmsg = ("decisive_randinit_AUC=%.4f (some separation but does not clear HARD_PASS/HARD_FAIL "
               "bars) gates: auc>=%.2f=%s dprime_pos=%s scramble_near_chance=%s "
               "concreteness_balanced=%s (gap=%s) power_ok=%s n_syn=%d n_sib=%d"
               % (dec_auc if dec_auc is not None else -1.0, HP_AUC_MIN,
                  dec_auc is not None and dec_auc >= HP_AUC_MIN, gate_dprime_pos, gate_scramble,
                  conc_bal_dec, decisive_conc_balance["conc_z_gap_sibling_minus_synonym"],
                  decisive_power_ok, n_syn_dec, n_sib_dec))

    elapsed_s = time.perf_counter() - t_start
    _log("VERDICT: %s" % verdict)
    _log(vmsg)

    result = dict(
        verdict=verdict, verdict_msg=vmsg, summary=vmsg,
        anchor_name=ANCHOR_NAME, run_mode=run_mode,
        ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
        elapsed_s=float(elapsed_s), device="cpu", cuda=bool(torch.cuda.is_available()),
        model_cfg=model_cfg,
        cited_original=CITED_ORIGINAL,
        positive_control=dict(ok=pos_ctrl_ok, pairs=pos_ctrl),
        n_read_lines=n_read, scan_elapsed_s=scan_s,
        sibling_pool_raw_n=len(sibling_pool_raw), synonym_pool_raw_n=len(synonym_pool_raw),
        main_bin_report=main_bin_report, decisive_bin_report=decisive_bin_report,
        main_pairs=dict(synonym=[[a, b] for a, b, pc in syn_main_sel],
                        sibling=[[a, b] for a, b, pc in sib_main_sel]),
        decisive_pairs=dict(synonym=[[a, b] for a, b, pc in syn_decisive_sel],
                            sibling=[[a, b] for a, b, pc in sib_decisive_sel]),
        main_randinit=main_randinit, main_trained=main_trained, main_scramble=main_scramble,
        decisive_randinit=decisive_randinit, decisive_trained=decisive_trained,
        decisive_scramble=decisive_scramble, decisive_grounding=decisive_grounding,
        main_conc_balance=main_conc_balance, decisive_conc_balance=decisive_conc_balance,
        train_overlap=train_overlap,
        arm_digests=arm_digests,
        power_floor_main_n=POWER_FLOOR_MAIN_N, power_floor_decisive_n=POWER_FLOOR_DECISIVE_N,
        main_power_ok=main_power_ok, decisive_power_ok=decisive_power_ok,
        bands=dict(hp_auc_min=HP_AUC_MIN, hf_auc_max=HF_AUC_MAX, near_chance_band=list(NEAR_CHANCE_BAND),
                  concreteness_balance_tol=CONCRETENESS_BALANCE_TOL,
                  conc_bin_edges=CONC_BIN_EDGES, held_out_percentile=HELD_OUT_PERCENTILE),
        cell_chunked=False, start_marker_written=True, crash_diagnostic_present=True,
        heartbeat_present=False, final_metrics_atomicity="tmp_replace",
    )
    return result


# --------------------------------------------------------------------------------------- CLI / main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        cfg = SELFTEST_CFG
    elif args.smoke:
        cfg = SMOKE_CFG
    else:
        cfg = FULL_CFG

    out_dir = get_output_dir(cfg["run_mode"])
    _write_start_marker(out_dir, cfg["run_mode"], expected_n_units=1)

    result = run_diagnostic(cfg)
    _atomic_write(out_dir, result)

    if args.self_test:
        _selftest_assertions(result)
        _log("SELF-TEST PASS")


def _selftest_assertions(result: Dict) -> None:
    assert result["positive_control"]["ok"] is True, "positive control failed: %r" % result["positive_control"]
    assert result["main_randinit"]["auc"] is not None, "main encoder AUC not computed"
    assert 0.0 <= result["main_randinit"]["auc"] <= 1.0, "main AUC out of range"
    digests = result["arm_digests"]
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            assert digests[names[i]] != digests[names[j]], "arms not distinct at selftest scale"
    assert result["n_read_lines"] > 0, "corpus scan read 0 lines"
    assert np.isfinite(result["elapsed_s"]) and result["elapsed_s"] > 0, "elapsed_s not sane"
    assert result["verdict"] is not None and len(result["verdict"]) > 0, "verdict missing"
    assert len(result["main_bin_report"]) > 0, "balanced_match produced no bins at selftest scale"


if __name__ == "__main__":
    _out = get_output_dir(
        "self_test" if "--self-test" in sys.argv else ("smoke" if "--smoke" in sys.argv else "full"))
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
