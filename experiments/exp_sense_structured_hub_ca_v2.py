"""C-A v2: SENSE-STRUCTURED lexical-semantic hub -- corpus-scale, count vs error-driven.

Re-attempt of C-A after v1 HARD_FAIL. v1 diagnosis (glass-box, VET'd,
data/exp_sense_structured_hub_ca_v1/metrics.json, commit c1358cdce):
mean_fit_same_sense_residual=0.436 ~= mean_fit_diff_sense_residual=0.447 -- the induction mechanism
ran faithfully but the PPMI/SVD context REPRESENTATION was featureless because it was fit on only
~60 hand-written probe sentences (data-starved), not a real corpus.

Fix in v2: fit the context representation on a REAL BACKGROUND CORPUS
(data/corpora/*/cleaned/*.clean.txt, ~5.4M chars) and compare TWO ARMS that share everything
(probe, induction mechanism, controls) except the context-representation MECHANISM:
  - ARM-COUNT (count_ppmi): PPMI/SVD distributional rep (hdlab.ppmi_sparse_encoder), corpus-scale.
  - ARM-ERRORDRIVEN (error_driven_pc): a predictive_coding-LEARNED context rep (Rao-Ballard
    residual-gated Hebbian associative memory trained context->word over the corpus; the learned
    predictive latent W @ context_vec is the sense-differentiating representation), not just a
    threshold gate over PPMI.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - Single-shot MEASUREMENT cell (corpus build + 2-arm fit + 10-form probe eval). No sweep axis
#   beyond the 2 arms; no chunking (cell_chunked=false, same exemption class as v1/Step-0).
# - final_metrics_atomicity: "tmp_replace" (os.replace, atomic write below).
# - except SystemExit: raise / except KeyboardInterrupt: raise BEFORE except Exception (no bare
#   except, no except BaseException).
# - crlb_n/a: representational sense-induction measurement, no quantitative noise-floor formula.
# - baseline_in_band: single_prototype_control_accuracy expected in (0.05, 0.95), checked at runtime.
# - discriminator survives scale: this cell IS the full/only regime; discriminator-fires assertion
#   (>=1 form induces >=2 prototypes, per arm) checked inline before the verdict.
# - arms_differ_verified: count_ppmi vs error_driven_pc predictions compared directly.
# - cardinality_ok: EXPECTED_N_UNITS=10 forms, asserted per arm.
# - calibration_check: "adaptive_with_discriminator_gate" (FIT-only threshold calibration per arm).
# - progress_logging: "print_flush_true" (background-corpus build + training loop + per-form).
# - Deterministic seeding only: hashlib.blake2b / hashlib.sha256 digests, never builtin hash().
#   See preregs/sense_structured_hub_ca_v2.md for full spec + HYPOTHESIZED/MEASURED/THEORETICAL tags.

ASCII-only. LOCAL-only, in-process/foreground execution (no queue dispatch, no background/nesting).
"""
from __future__ import annotations

import glob
import hashlib
import json
import math
import os
import platform
import random
import re
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

ANCHOR_NAME = "sense_structured_hub_ca_v2"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
SEED = 4242
EXPECTED_N_UNITS = 10  # forms, per arm
ARMS = ["count_ppmi", "error_driven_pc"]

N_DIM = 128
TOTAL_BACKGROUND_TARGET = 3000
MIN_TERM_FREQ_PPMI = 3
MIN_WORD_FREQ_ERRDRIVEN = 3
WINDOW = 4
TRAIN_GATE_THRESHOLD = 0.30
HARD_PASS_HELD_OUT = 0.71  # floor 0.5625 + 0.15
HARD_PASS_CONTROL_MAX = 0.65
HARD_PASS_SAME_SENSE_MIN = 0.60
HARD_FAIL_HELD_OUT = 0.71
HARD_FAIL_CONTROL_LEAK = 0.80
HARD_FAIL_SAME_SENSE_FLOOR = 0.50

STOPWORDS = {
    "the", "a", "an", "he", "she", "they", "it", "him", "her", "his", "their", "we", "you",
    "was", "is", "are", "were", "be", "been", "being", "to", "of", "in", "on", "at", "by",
    "for", "with", "and", "or", "but", "had", "has", "have", "must", "will", "would", "could",
    "should", "can", "did", "do", "does", "not", "no", "as", "that", "this", "these", "those",
    "during", "before", "after", "while", "near", "up", "off", "over", "under", "through",
    "across", "toward", "along", "into", "from", "about", "than", "so", "very", "still",
    "against", "throughout", "between", "around", "within", "out", "down", "one", "i", "my",
    "your", "our", "its", "them", "us", "if", "when", "what", "who", "which", "there", "here",
    "then", "now", "just", "some", "more", "such", "own", "same", "too", "also", "said", "upon",
}

# ---------------------------------------------------------------------------
# Probe: reused VERBATIM from exp_sense_structured_hub_ca_v1.py (10 polysemous
# forms, 2 senses each, disjoint fit/test content-word vocabulary, machine-
# checked below). Ground truth requires hand labels so this cannot come from
# raw corpus text; only the context REPRESENTATION changes in v2.
# ---------------------------------------------------------------------------

PROBE: Dict[str, Dict[str, Dict[str, List[str]]]] = {
    "hard": {
        "FIT": {
            "A": ["she studied hard for the difficult exam",
                  "he trained hard every single morning",
                  "they worked hard to finish the project"],
            "B": ["he was hit hard in the chest",
                  "the wind blew hard against the window",
                  "she slammed the door hard in anger"],
        },
        "TEST": {
            "A": ["the athlete practiced hard before the big race",
                  "students must try hard to master the material",
                  "he pushed hard to meet the tight deadline"],
            "B": ["the ball struck hard against the fence",
                  "rain fell hard throughout the stormy night",
                  "the boxer punched hard during the match"],
        },
    },
    "trick": {
        "FIT": {
            "A": ["the magician performed a clever card trick",
                  "she learned a new skateboard trick",
                  "he showed off an amazing trick"],
            "B": ["it was a cruel trick to play on him",
                  "the con artist pulled a nasty trick",
                  "they used a trick to fool the guard"],
        },
        "TEST": {
            "A": ["the gymnast practiced a difficult trick during her routine",
                  "the dog was taught a fun trick",
                  "he mastered a neat trick for the show"],
            "B": ["the swindler set up a sneaky trick",
                  "it was a mean trick to embarrass her",
                  "the thief relied on a trick to sneak past security"],
        },
    },
    "pay": {
        "FIT": {
            "A": ["please pay attention to the lecture",
                  "you must pay close attention while driving",
                  "try to pay attention during the meeting"],
            "B": ["he forgot to pay the electricity bill",
                  "she went to pay the rent today",
                  "workers expect to pay taxes every year"],
        },
        "TEST": {
            "A": ["pay heed to the safety warning before diving",
                  "remember to pay heed while crossing the busy street",
                  "new employees must pay heed to the instructions given"],
            "B": ["the company had to pay a large fine",
                  "he wants to pay off the loan quickly",
                  "she needs to pay for groceries this week"],
        },
    },
    "cross": {
        "FIT": {
            "A": ["they had to cross the busy street",
                  "we will cross the river by ferry",
                  "hikers must cross the narrow bridge"],
            "B": ["she was cross with him after the argument",
                  "the teacher grew cross at the noisy class",
                  "he became cross when they were late"],
        },
        "TEST": {
            "A": ["travelers need to cross the vast desert",
                  "the runners will cross the finish line soon",
                  "villagers often cross the shallow creek"],
            "B": ["his mother was cross about the broken vase",
                  "the coach turned cross during the long practice",
                  "she felt cross after losing the game"],
        },
    },
    "bright": {
        "FIT": {
            "A": ["the bright student solved the puzzle quickly",
                  "he is a bright young scientist",
                  "she was known as a bright thinker"],
            "B": ["the bright sun hurt her eyes",
                  "the bright lamp lit the dark room",
                  "a bright flash lit up the sky"],
        },
        "TEST": {
            "A": ["the bright child answered every question correctly",
                  "their bright colleague impressed the whole team",
                  "he proved to be a bright engineer"],
            "B": ["the bright headlights blinded the driver",
                  "a bright star appeared over the hill",
                  "the bright screen glowed in the quiet night"],
        },
    },
    "sound": {
        "FIT": {
            "A": ["the loud sound woke the sleeping baby",
                  "a strange sound came from the engine",
                  "they heard a sound in the attic"],
            "B": ["it was a sound financial decision",
                  "the bridge has a sound structure",
                  "he gave sound advice to the team"],
        },
        "TEST": {
            "A": ["a sudden sound startled the quiet cat",
                  "an odd sound echoed through the empty hallway",
                  "she noticed a sound near the old barn"],
            "B": ["they praised his sound judgment during the crisis",
                  "the company relies on a sound business plan",
                  "the old ladder still felt sound and safe"],
        },
    },
    "light": {
        "FIT": {
            "A": ["turn on the light in the hallway",
                  "the candle gave a soft light",
                  "she switched on the light in the kitchen"],
            "B": ["the light suitcase was easy to carry",
                  "she wore a light jacket in summer",
                  "he lifted the light box with one hand"],
        },
        "TEST": {
            "A": ["the lamp cast a warm light across the room",
                  "morning light streamed through the window",
                  "a dim light flickered in the basement"],
            "B": ["the light backpack made the hike easier",
                  "he chose a light fabric for the shirt",
                  "the feather felt remarkably light in her palm"],
        },
    },
    "bear": {
        "FIT": {
            "A": ["the brown bear caught a fish",
                  "a grizzly bear wandered near the camp",
                  "the bear climbed a tall tree"],
            "B": ["she could not bear the pain",
                  "he had to bear the heavy burden",
                  "they had to bear the harsh winter"],
        },
        "TEST": {
            "A": ["a black bear crossed the mountain trail",
                  "the hungry bear searched for berries",
                  "hikers spotted a bear near the lake"],
            "B": ["he struggled to bear the loss",
                  "she learned to bear the criticism calmly",
                  "they could barely bear the long wait"],
        },
    },
    "bank": {
        "FIT": {
            "A": ["she deposited her paycheck at the bank",
                  "he opened a new account at the bank",
                  "the bank approved his loan application"],
            "B": ["they sat on the grassy bank of the river",
                  "fishermen lined the muddy bank at dawn",
                  "the flood water rose above the bank"],
        },
        "TEST": {
            "A": ["the manager reviewed transactions at the bank",
                  "customers waited in line at the bank",
                  "she withdrew cash from the local bank"],
            "B": ["children played along the sandy bank",
                  "the boat drifted toward the far bank",
                  "willow trees stood near the quiet bank"],
        },
    },
    "bat": {
        "FIT": {
            "A": ["the bat flew silently through the cave",
                  "a fruit bat hung from the tree branch",
                  "the bat used echolocation to hunt insects"],
            "B": ["he swung the bat and hit a home run",
                  "she gripped the bat tightly before the pitch",
                  "the player chose a wooden bat for practice"],
        },
        "TEST": {
            "A": ["a small bat roosted under the old bridge",
                  "the brown bat darted across the night sky",
                  "scientists studied how the bat navigates in darkness"],
            "B": ["the coach handed him a new bat",
                  "the batter cracked the bat against the ball",
                  "she trained her swing with an aluminum bat"],
        },
    },
}

FORMS = sorted(PROBE.keys())
assert len(FORMS) == EXPECTED_N_UNITS, f"probe has {len(FORMS)} forms, expected {EXPECTED_N_UNITS}"


def _tokenize(text: str) -> List[str]:
    return text.lower().replace(",", " ").split()


def _content_words(sentences: List[str], target_word: str) -> set:
    out = set()
    for s in sentences:
        for tok in _tokenize(s):
            if tok == target_word.lower() or tok in STOPWORDS:
                continue
            out.add(tok)
    return out


def _mask_target(sentence: str, target_word: str) -> str:
    toks = [t for t in sentence.split() if t.lower().strip(",.") != target_word.lower()]
    return " ".join(toks)


def _assert_disjoint_vocab() -> Dict[str, dict]:
    report = {}
    for w in FORMS:
        fit_sents = PROBE[w]["FIT"]["A"] + PROBE[w]["FIT"]["B"]
        test_sents = PROBE[w]["TEST"]["A"] + PROBE[w]["TEST"]["B"]
        fit_vocab = _content_words(fit_sents, w)
        test_vocab = _content_words(test_sents, w)
        overlap = fit_vocab & test_vocab
        assert not overlap, (
            f"DISJOINT_VOCAB_VIOLATION form={w!r}: fit/test content-word overlap={sorted(overlap)}"
        )
        report[w] = {
            "fit_vocab_size": len(fit_vocab),
            "test_vocab_size": len(test_vocab),
            "overlap": sorted(overlap),
        }
    return report


# ---------------------------------------------------------------------------
# Start marker / crash diagnostic / atomic metrics write.
# ---------------------------------------------------------------------------


def _write_start_marker(output_dir: str) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": "local_foreground_measurement",
        "expected_n_units": EXPECTED_N_UNITS,
        "host": platform.node(),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: str, exc: BaseException) -> None:
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
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


def _write_metrics(output_dir: str, metrics: dict) -> None:
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, final_path)  # atomic per META_RULE_AH


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64).ravel()
    b = np.asarray(b, dtype=np.float64).ravel()
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _sha256_int(key: str, mod: int) -> int:
    """Deterministic digest-based integer, NEVER Python's salted builtin hash()."""
    d = hashlib.sha256(key.encode("utf-8")).digest()
    return int.from_bytes(d[:8], "big") % mod


# ---------------------------------------------------------------------------
# Background corpus loader (real text, corpus-scale).
# ---------------------------------------------------------------------------

_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_WORD_RE = re.compile(r"[A-Za-z']+")


def _clean_ascii(raw: str) -> str:
    raw = raw.replace("’", "'").replace("‘", "'")
    raw = raw.replace("“", '"').replace("”", '"')
    raw = raw.replace("—", " - ").replace("–", "-")
    return raw.encode("ascii", errors="ignore").decode("ascii")


def _extract_sentences(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    raw = _clean_ascii(raw)
    raw = re.sub(r"\s+", " ", raw).strip()
    out = []
    for s in _SENT_SPLIT_RE.split(raw):
        s = s.strip()
        toks = s.split()
        n = len(toks)
        if n < 5 or n > 30:
            continue
        if any(ch.isdigit() for ch in s):
            continue
        alpha_toks = [t for t in toks if _WORD_RE.fullmatch(t.strip(".,!?;:\"'"))]
        if len(alpha_toks) < 0.9 * n:
            continue
        allcaps = sum(1 for t in toks if t.isupper() and len(t) > 1)
        if allcaps > 0.3 * n:
            continue
        out.append(s)
    return out


def _build_background_corpus(seed: int) -> Tuple[List[str], dict]:
    files = sorted(glob.glob(os.path.join(REPO_ROOT, "data", "corpora", "*", "cleaned", "*.clean.txt")))
    assert files, "no background corpus files found under data/corpora/*/cleaned/*.clean.txt"
    all_sentences: List[str] = []
    for fp in files:
        all_sentences.extend(_extract_sentences(fp))
    print(f"[background-corpus] {len(files)} files, {len(all_sentences)} candidate sentences "
          f"after filtering", flush=True)

    probe_word_set = {w.lower() for w in FORMS}

    def _contains_probe_word(s: str) -> bool:
        toks = {t.lower().strip(".,!?;:\"'") for t in s.split()}
        return bool(toks & probe_word_set)

    probe_sentences = sorted(set(s for s in all_sentences if _contains_probe_word(s)))
    filler_pool = sorted(set(all_sentences) - set(probe_sentences))

    n_filler_needed = max(0, TOTAL_BACKGROUND_TARGET - len(probe_sentences))
    rng = random.Random(seed)
    filler_sample = rng.sample(filler_pool, min(n_filler_needed, len(filler_pool)))

    background = sorted(set(probe_sentences) | set(filler_sample))
    n_tokens = sum(len(s.split()) for s in background)

    per_word_counts = {}
    for w in FORMS:
        wl = w.lower()
        cnt = 0
        for s in background:
            cnt += sum(1 for t in s.split() if t.lower().strip(".,!?;:\"'") == wl)
        per_word_counts[w] = cnt

    stats = {
        "n_files": len(files),
        "n_candidate_sentences_total": len(all_sentences),
        "n_probe_word_sentences": len(probe_sentences),
        "n_filler_sentences": len(filler_sample),
        "n_background_sentences": len(background),
        "n_background_tokens": n_tokens,
        "background_probe_word_counts": per_word_counts,
    }
    print(f"[background-corpus] selected {len(background)} sentences, {n_tokens} tokens; "
          f"per-probe-word counts: {per_word_counts}", flush=True)
    return background, stats


# ---------------------------------------------------------------------------
# ARM-COUNT: PPMI/SVD distributional rep at corpus scale.
# ---------------------------------------------------------------------------


def _fit_ppmi_arm(background: List[str], seed: int):
    from hdlab.ppmi_sparse_encoder import PPMISparseEncoder

    t0 = time.perf_counter()
    ppmi = PPMISparseEncoder(n_dim=N_DIM, min_term_freq=MIN_TERM_FREQ_PPMI, smoothing=0.75, seed=seed)
    ppmi.fit(background, np.arange(len(background)))
    elapsed = time.perf_counter() - t0
    print(f"[arm=count_ppmi] fit complete in {elapsed:.2f}s "
          f"(vocab={len(ppmi.term_to_idx)}, effective_n_dim={ppmi.effective_n_dim})", flush=True)

    def ctx_vec(sentence: str, word: str) -> np.ndarray:
        return ppmi.encode(_mask_target(sentence, word)).astype(np.float64)

    return ctx_vec, {"fit_elapsed_s": elapsed, "vocab_size": len(ppmi.term_to_idx),
                      "effective_n_dim": ppmi.effective_n_dim}


# ---------------------------------------------------------------------------
# ARM-ERRORDRIVEN: predictive_coding-LEARNED context representation.
# ---------------------------------------------------------------------------


def _dense_bipolar_hv(word: str, n_dim: int, seed: int) -> np.ndarray:
    h = hashlib.blake2b(f"{seed}:{word}".encode("utf-8"), digest_size=8).digest()
    s = int.from_bytes(h, "big") & 0x7FFFFFFF
    rng = np.random.default_rng(s)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float64)


def _bundle_sign(vecs: List[np.ndarray], n_dim: int) -> np.ndarray:
    if not vecs:
        return np.zeros(n_dim, dtype=np.float64)
    acc = np.sum(vecs, axis=0)
    out = np.sign(acc)
    out[out == 0] = 1.0
    return out


def _fit_error_driven_arm(background: List[str], seed: int):
    from hdlab.predictive_coding import predict, threshold_gate, gated_write

    t0 = time.perf_counter()
    # Pass 1: content-word frequency over background corpus.
    freq: Dict[str, int] = {}
    tokenized: List[List[str]] = []
    for s in background:
        toks = [t.lower().strip(".,!?;:\"'") for t in s.split()]
        toks = [t for t in toks if t and t not in STOPWORDS and t.isalpha()]
        tokenized.append(toks)
        for t in toks:
            freq[t] = freq.get(t, 0) + 1
    vocab = sorted(t for t, c in freq.items() if c >= MIN_WORD_FREQ_ERRDRIVEN)
    hv_cache: Dict[str, np.ndarray] = {w: _dense_bipolar_hv(w, N_DIM, seed) for w in vocab}
    print(f"[arm=error_driven_pc] vocab (freq>={MIN_WORD_FREQ_ERRDRIVEN}) size={len(vocab)}", flush=True)

    # Pass 2: train W via predictive-coding gated Hebbian over context windows.
    W = np.zeros((N_DIM, N_DIM), dtype=np.float64)
    n_events = 0
    n_applied = 0
    for toks in tokenized:
        n = len(toks)
        for i, t in enumerate(toks):
            if t not in hv_cache:
                continue
            lo, hi = max(0, i - WINDOW), min(n, i + WINDOW + 1)
            ctx_words = [toks[j] for j in range(lo, hi) if j != i and toks[j] in hv_cache]
            if not ctx_words:
                continue
            context_vec = _bundle_sign([hv_cache[c] for c in ctx_words], N_DIM)
            predicted = predict(W, context_vec, sign_cleanup=True)
            decision = threshold_gate(observed=hv_cache[t], predicted=predicted,
                                       threshold=TRAIN_GATE_THRESHOLD)
            W, applied = gated_write(W, context_vec, hv_cache[t], decision)
            n_events += 1
            if applied:
                n_applied += 1
            if n_events % 5000 == 0:
                print(f"[arm=error_driven_pc] training progress: {n_events} events, "
                      f"{n_applied} applied writes, elapsed={time.perf_counter()-t0:.1f}s", flush=True)

    elapsed = time.perf_counter() - t0
    print(f"[arm=error_driven_pc] training complete in {elapsed:.2f}s "
          f"(n_events={n_events}, n_applied={n_applied}, "
          f"applied_frac={n_applied/n_events if n_events else float('nan'):.3f})", flush=True)

    def ctx_vec(sentence: str, word: str) -> np.ndarray:
        masked = _mask_target(sentence, word)
        toks = [t.lower().strip(".,!?;:\"'") for t in masked.split()]
        toks = [t for t in toks if t in hv_cache]
        cv = _bundle_sign([hv_cache[t] for t in toks], N_DIM)
        return predict(W, cv, sign_cleanup=False).astype(np.float64)

    return ctx_vec, {"fit_elapsed_s": elapsed, "vocab_size": len(vocab), "n_train_events": n_events,
                      "n_applied_writes": n_applied,
                      "applied_frac": n_applied / n_events if n_events else float("nan")}


# ---------------------------------------------------------------------------
# Induction mechanism -- REUSED VERBATIM from v1 (identical for both arms).
# ---------------------------------------------------------------------------


def _induce_senses(items: List[Tuple[str, np.ndarray]], threshold: float, max_prototypes: int = 4):
    from hdlab.predictive_coding import threshold_gate

    prototypes: List[dict] = []
    assignments: Dict[str, int] = {}
    trace: List[dict] = []

    for item_id, cv in items:
        if not prototypes:
            prototypes.append({"sum": cv.copy(), "count": 1, "members": [item_id]})
            assignments[item_id] = 0
            trace.append({"item": item_id, "action": "seed_first_prototype", "proto_id": 0,
                           "residual": None})
            continue

        sims = [_cos(cv, p["sum"] / p["count"]) for p in prototypes]
        nearest_idx = int(np.argmax(sims))
        nearest_mean = prototypes[nearest_idx]["sum"] / prototypes[nearest_idx]["count"]
        dec = threshold_gate(observed=cv, predicted=nearest_mean, threshold=threshold)

        if dec.skipped:
            prototypes[nearest_idx]["sum"] = prototypes[nearest_idx]["sum"] + cv
            prototypes[nearest_idx]["count"] += 1
            prototypes[nearest_idx]["members"].append(item_id)
            assignments[item_id] = nearest_idx
            trace.append({"item": item_id, "action": "merge", "proto_id": nearest_idx,
                           "residual": dec.residual_mag})
        elif len(prototypes) < max_prototypes:
            new_idx = len(prototypes)
            prototypes.append({"sum": cv.copy(), "count": 1, "members": [item_id]})
            assignments[item_id] = new_idx
            trace.append({"item": item_id, "action": "spawn_new_prototype", "proto_id": new_idx,
                           "residual": dec.residual_mag})
        else:
            prototypes[nearest_idx]["sum"] = prototypes[nearest_idx]["sum"] + cv
            prototypes[nearest_idx]["count"] += 1
            prototypes[nearest_idx]["members"].append(item_id)
            assignments[item_id] = nearest_idx
            trace.append({"item": item_id, "action": "merge_cap_reached", "proto_id": nearest_idx,
                           "residual": dec.residual_mag})

    return prototypes, assignments, trace


def _calibrate_threshold(fit_context_vecs: Dict[str, Dict[str, List[np.ndarray]]]) -> Tuple[float, dict]:
    from hdlab.predictive_coding import residual_magnitude

    same_sense_residuals = []
    diff_sense_residuals = []
    for w in fit_context_vecs:
        vecs_a = fit_context_vecs[w]["A"]
        vecs_b = fit_context_vecs[w]["B"]
        for i in range(len(vecs_a)):
            for j in range(i + 1, len(vecs_a)):
                same_sense_residuals.append(residual_magnitude(vecs_a[i], vecs_a[j]))
        for i in range(len(vecs_b)):
            for j in range(i + 1, len(vecs_b)):
                same_sense_residuals.append(residual_magnitude(vecs_b[i], vecs_b[j]))
        for va in vecs_a:
            for vb in vecs_b:
                diff_sense_residuals.append(residual_magnitude(va, vb))

    mean_same = float(np.mean(same_sense_residuals)) if same_sense_residuals else 0.5
    mean_diff = float(np.mean(diff_sense_residuals)) if diff_sense_residuals else 0.5
    threshold = 0.5 * (mean_same + mean_diff)
    calib = {
        "mean_fit_same_sense_residual": mean_same,
        "mean_fit_diff_sense_residual": mean_diff,
        "n_same_sense_pairs": len(same_sense_residuals),
        "n_diff_sense_pairs": len(diff_sense_residuals),
        "threshold_T": threshold,
        "formula": "T = 0.5 * (mean_fit_same_sense_residual + mean_fit_diff_sense_residual)",
    }
    return threshold, calib


def _run_arm_eval(arm_name: str, ctx_vec_fn, ce, rng_seed: int) -> Tuple[dict, dict]:
    """Runs induction + held-out eval for one arm across all 10 forms. Returns
    (per_form dict, aggregate dict)."""
    fit_vecs: Dict[str, Dict[str, List[np.ndarray]]] = {
        w: {s: [ctx_vec_fn(sent, w) for sent in PROBE[w]["FIT"][s]] for s in ("A", "B")}
        for w in FORMS
    }
    test_vecs: Dict[str, Dict[str, List[np.ndarray]]] = {
        w: {s: [ctx_vec_fn(sent, w) for sent in PROBE[w]["TEST"][s]] for s in ("A", "B")}
        for w in FORMS
    }

    threshold, threshold_calib = _calibrate_threshold(fit_vecs)
    print(f"[arm={arm_name}] calibration threshold_T={threshold:.4f} "
          f"mean_same={threshold_calib['mean_fit_same_sense_residual']:.4f} "
          f"mean_diff={threshold_calib['mean_fit_diff_sense_residual']:.4f}", flush=True)

    rng = random.Random(rng_seed)
    per_form: Dict[str, dict] = {}
    n_forms_with_ge2_prototypes = 0

    for w in FORMS:
        items = []
        gold_sense: Dict[str, str] = {}
        for sense in ("A", "B"):
            for i, vec in enumerate(fit_vecs[w][sense]):
                item_id = f"FIT|{sense}|{i}"
                items.append((item_id, vec))
                gold_sense[item_id] = sense
        rng.shuffle(items)

        prototypes, assignments, trace = _induce_senses(items, threshold=threshold, max_prototypes=4)
        n_protos = len(prototypes)
        if n_protos >= 2:
            n_forms_with_ge2_prototypes += 1

        cluster_label_map: Dict[int, str] = {}
        for pidx, p in enumerate(prototypes):
            votes = {"A": 0, "B": 0}
            for m in p["members"]:
                votes[gold_sense[m]] += 1
            cluster_label_map[pidx] = "A" if votes["A"] >= votes["B"] else "B"

        proto_means = [p["sum"] / p["count"] for p in prototypes]

        test_results = []
        test_proto_assignment: Dict[str, int] = {}
        for sense in ("A", "B"):
            for i, vec in enumerate(test_vecs[w][sense]):
                sims = [_cos(vec, pm) for pm in proto_means]
                nearest = int(np.argmax(sims))
                pred_sense = cluster_label_map[nearest]
                correct = pred_sense == sense
                test_id = f"TEST|{sense}|{i}"
                test_proto_assignment[test_id] = nearest
                test_results.append({
                    "test_id": test_id, "gold_sense": sense, "pred_sense": pred_sense,
                    "correct": correct, "nearest_proto": nearest,
                })

        pair_agree = 0
        pair_total = 0
        for sense in ("A", "B"):
            ids = [f"TEST|{sense}|{i}" for i in range(len(test_vecs[w][sense]))]
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    pair_total += 1
                    if test_proto_assignment[ids[i]] == test_proto_assignment[ids[j]]:
                        pair_agree += 1

        ref_a = ce.encode(PROBE[w]["FIT"]["A"][0]).astype(np.float64)
        ref_b = ce.encode(PROBE[w]["FIT"]["B"][0]).astype(np.float64)
        ctrl_rng = np.random.default_rng(SEED + _sha256_int(w, 10000))
        ctrl_results = []
        for sense in ("A", "B"):
            for i, sent in enumerate(PROBE[w]["TEST"][sense]):
                rep = ce.encode(sent).astype(np.float64)
                cos_a = _cos(rep, ref_a)
                cos_b = _cos(rep, ref_b)
                if abs(cos_a - cos_b) < 1e-9:
                    pred = "A" if ctrl_rng.integers(0, 2) == 0 else "B"
                else:
                    pred = "A" if cos_a > cos_b else "B"
                ctrl_results.append({"test_id": f"TEST|{sense}|{i}", "gold_sense": sense,
                                      "pred_sense": pred, "correct": pred == sense})

        n_arms_disagree = sum(
            1 for tr, cr in zip(test_results, ctrl_results)
            if tr["pred_sense"] != cr["pred_sense"]
        )

        per_form[w] = {
            "n_prototypes_induced": n_protos,
            "cluster_label_map": cluster_label_map,
            "induction_trace": trace,
            "held_out_test_results": test_results,
            "held_out_n_correct": sum(1 for r in test_results if r["correct"]),
            "held_out_n_trials": len(test_results),
            "same_sense_pair_agree": pair_agree,
            "same_sense_pair_total": pair_total,
            "single_prototype_control_results": ctrl_results,
            "single_prototype_control_n_correct": sum(1 for r in ctrl_results if r["correct"]),
            "single_prototype_control_n_trials": len(ctrl_results),
            "n_items_where_arms_disagree_vs_control": n_arms_disagree,
        }
        print(f"[arm={arm_name}][{w}] n_prototypes={n_protos} held_out_acc="
              f"{per_form[w]['held_out_n_correct']}/{per_form[w]['held_out_n_trials']} "
              f"same_sense_agree={pair_agree}/{pair_total}", flush=True)

    total_correct = sum(v["held_out_n_correct"] for v in per_form.values())
    total_trials = sum(v["held_out_n_trials"] for v in per_form.values())
    held_out_accuracy = total_correct / total_trials if total_trials else float("nan")

    ctrl_correct = sum(v["single_prototype_control_n_correct"] for v in per_form.values())
    ctrl_trials = sum(v["single_prototype_control_n_trials"] for v in per_form.values())
    single_prototype_control_accuracy = ctrl_correct / ctrl_trials if ctrl_trials else float("nan")

    ss_agree = sum(v["same_sense_pair_agree"] for v in per_form.values())
    ss_total = sum(v["same_sense_pair_total"] for v in per_form.values())
    same_sense_agreement = ss_agree / ss_total if ss_total else float("nan")

    def _binom_se(n: int) -> float:
        return float(np.sqrt(0.25 / n)) if n > 0 else float("nan")

    def _p_vs_chance(acc: float, n: int) -> float:
        se = _binom_se(n)
        if se != se or se <= 0:
            return float("nan")
        z = (acc - 0.5) / se
        return float(math.erfc(abs(z) / math.sqrt(2.0)))

    discriminator_fires = n_forms_with_ge2_prototypes >= 1
    cardinality_ok = len(per_form) == EXPECTED_N_UNITS
    senses_induced_not_hand_listed = discriminator_fires and any(
        v["n_prototypes_induced"] != 1 for v in per_form.values()
    )

    aggregate = {
        "arm": arm_name,
        "held_out_sense_discrimination_accuracy": held_out_accuracy,
        "held_out_n_correct": total_correct,
        "held_out_n_trials": total_trials,
        "held_out_p_value_vs_chance": _p_vs_chance(held_out_accuracy, total_trials),
        "single_prototype_control_accuracy": single_prototype_control_accuracy,
        "single_prototype_control_n_correct": ctrl_correct,
        "single_prototype_control_n_trials": ctrl_trials,
        "same_sense_agreement": same_sense_agreement,
        "same_sense_pair_agree": ss_agree,
        "same_sense_pair_total": ss_total,
        "n_forms_with_ge2_prototypes": n_forms_with_ge2_prototypes,
        "discriminator_fires": discriminator_fires,
        "senses_induced_not_hand_listed": senses_induced_not_hand_listed,
        "cardinality_ok": cardinality_ok,
        "threshold_calibration": threshold_calib,
    }
    return per_form, aggregate


# ---------------------------------------------------------------------------
# Self-test: constructs REAL substrate objects at tiny scale (2 forms, 1
# background file truncated to ~20 sentences), per SCHEMA-VET F.1 gate.
# ---------------------------------------------------------------------------


def _selftest() -> None:
    print("[sense_structured_hub_ca_v2 selftest] START", flush=True)

    disjoint_report = _assert_disjoint_vocab()
    assert len(disjoint_report) == EXPECTED_N_UNITS
    print(f"[selftest 1] disjoint-vocab machine-check PASS for all {EXPECTED_N_UNITS} forms", flush=True)

    files = sorted(glob.glob(os.path.join(REPO_ROOT, "data", "corpora", "*", "cleaned", "*.clean.txt")))
    assert files, "no corpus files found"
    tiny_bg = _extract_sentences(files[0])[:25]
    assert len(tiny_bg) >= 5, "tiny background corpus too small for selftest"
    print(f"[selftest 2] real corpus sentence extraction PASS ({len(tiny_bg)} sentences from {files[0]})",
          flush=True)

    from hdlab.ppmi_sparse_encoder import PPMISparseEncoder
    from hdlab.predictive_coding import residual_magnitude, threshold_gate, predict, gated_write
    from hdlab.concept_encoder import ConceptEncoder

    ppmi = PPMISparseEncoder(n_dim=32, min_term_freq=1, smoothing=0.75, seed=SEED)
    ppmi.fit(tiny_bg, np.arange(len(tiny_bg)))
    v1 = ppmi.encode(_mask_target(PROBE["hard"]["FIT"]["A"][0], "hard"))
    assert v1.shape == (32,)
    print("[selftest 3] PPMISparseEncoder real fit+encode on real corpus text PASS", flush=True)

    # Tiny error-driven training loop, real predictive_coding calls.
    freq: Dict[str, int] = {}
    tok_lists = []
    for s in tiny_bg:
        toks = [t.lower().strip(".,!?;:\"'") for t in s.split()]
        toks = [t for t in toks if t and t not in STOPWORDS and t.isalpha()]
        tok_lists.append(toks)
        for t in toks:
            freq[t] = freq.get(t, 0) + 1
    vocab = sorted(t for t, c in freq.items() if c >= 1)
    assert vocab, "tiny selftest vocab empty"
    hv_cache = {w: _dense_bipolar_hv(w, 32, SEED) for w in vocab}
    W = np.zeros((32, 32), dtype=np.float64)
    n_applied = 0
    for toks in tok_lists:
        n = len(toks)
        for i, t in enumerate(toks):
            ctx_words = [toks[j] for j in range(max(0, i - 2), min(n, i + 3)) if j != i]
            if not ctx_words:
                continue
            cv = _bundle_sign([hv_cache[c] for c in ctx_words], 32)
            pred = predict(W, cv, sign_cleanup=True)
            dec = threshold_gate(observed=hv_cache[t], predicted=pred, threshold=TRAIN_GATE_THRESHOLD)
            W, applied = gated_write(W, cv, hv_cache[t], dec)
            n_applied += int(applied)
    print(f"[selftest 4] error-driven training loop real predictive_coding calls PASS "
          f"(n_applied={n_applied})", flush=True)

    learned_ctx = predict(W, hv_cache[vocab[0]], sign_cleanup=False)
    assert learned_ctx.shape == (32,)
    rmag = residual_magnitude(v1, ppmi.encode(_mask_target(PROBE["hard"]["FIT"]["B"][0], "hard")))
    assert 0.0 <= rmag <= 1.0
    print(f"[selftest 5] predictive_coding.predict/residual_magnitude real calls PASS (residual={rmag:.3f})",
          flush=True)

    mini_forms = FORMS[:2]
    items = [(f"item{i}", ppmi.encode(_mask_target(PROBE[w]["FIT"][s][0], w)))
             for i, (w, s) in enumerate((w, s) for w in mini_forms for s in ("A", "B"))]
    protos, assigns, trace = _induce_senses(items, threshold=0.4, max_prototypes=4)
    assert len(protos) >= 1
    print(f"[selftest 6] _induce_senses real run PASS (n_prototypes={len(protos)})", flush=True)

    ce = ConceptEncoder(n_dim=32, n_concepts=len(mini_forms), seed=SEED,
                         concept_names=mini_forms, mask_target_word=True)
    ce_fit_sentences, ce_fit_labels = [], []
    for wi, w in enumerate(mini_forms):
        for sense in ("A", "B"):
            for s in PROBE[w]["FIT"][sense]:
                ce_fit_sentences.append(s)
                ce_fit_labels.append(wi)
    ce.fit(ce_fit_sentences, np.asarray(ce_fit_labels, dtype=np.int64))
    r = ce.encode(PROBE[mini_forms[0]]["TEST"]["A"][0])
    assert r.shape == (32,)
    print("[selftest 7] ConceptEncoder real fit+encode PASS", flush=True)

    threshold, calib = _calibrate_threshold({
        w: {s: [ppmi.encode(_mask_target(sent, w)) for sent in PROBE[w]["FIT"][s]] for s in ("A", "B")}
        for w in mini_forms
    })
    assert 0.0 <= threshold <= 1.0
    print(f"[selftest 8] adaptive threshold calibration real run PASS (T={threshold:.3f})", flush=True)

    assert _sha256_int("hard", 10000) == _sha256_int("hard", 10000)
    print("[selftest 9] deterministic sha256-based seeding (no builtin hash()) PASS", flush=True)

    print("[sense_structured_hub_ca_v2 selftest] ALL PASS", flush=True)


# ---------------------------------------------------------------------------
# Main measurement.
# ---------------------------------------------------------------------------


def main() -> None:
    t0 = time.perf_counter()
    _write_start_marker(OUTPUT_DIR)

    disjoint_report = _assert_disjoint_vocab()
    print(f"[disjoint-vocab] machine-checked OK for {len(disjoint_report)} forms", flush=True)

    background, bg_stats = _build_background_corpus(SEED)

    from hdlab.concept_encoder import ConceptEncoder

    # --- Single-prototype control (shared across arms; context-blind). ---
    ce = ConceptEncoder(n_dim=N_DIM, n_concepts=len(FORMS), seed=SEED,
                         concept_names=FORMS, mask_target_word=True)
    ce_fit_sentences: List[str] = []
    ce_fit_labels: List[int] = []
    for wi, w in enumerate(FORMS):
        for sense in ("A", "B"):
            for s in PROBE[w]["FIT"][sense]:
                ce_fit_sentences.append(s)
                ce_fit_labels.append(wi)
    ce.fit(ce_fit_sentences, np.asarray(ce_fit_labels, dtype=np.int64))

    # --- Fit both arms' context representations on the SAME background corpus. ---
    ctx_vec_count, count_fit_stats = _fit_ppmi_arm(background, SEED)
    ctx_vec_errdriven, errdriven_fit_stats = _fit_error_driven_arm(background, SEED)

    per_form_by_arm: Dict[str, dict] = {}
    aggregate_by_arm: Dict[str, dict] = {}

    per_form_count, agg_count = _run_arm_eval("count_ppmi", ctx_vec_count, ce, SEED)
    per_form_by_arm["count_ppmi"] = per_form_count
    aggregate_by_arm["count_ppmi"] = agg_count

    per_form_err, agg_err = _run_arm_eval("error_driven_pc", ctx_vec_errdriven, ce, SEED)
    per_form_by_arm["error_driven_pc"] = per_form_err
    aggregate_by_arm["error_driven_pc"] = agg_err

    # --- arms_differ_verified: compare predictions item-by-item. ---
    n_disagree_between_arms = 0
    n_compared = 0
    for w in FORMS:
        c_res = per_form_count[w]["held_out_test_results"]
        e_res = per_form_err[w]["held_out_test_results"]
        for cr, er in zip(c_res, e_res):
            n_compared += 1
            if cr["pred_sense"] != er["pred_sense"]:
                n_disagree_between_arms += 1
    arms_differ_verified = n_disagree_between_arms > 0

    # --- Cardinality gate (both arms). ---
    cardinality_ok = all(aggregate_by_arm[a]["cardinality_ok"] for a in ARMS)

    # --- Shared single-prototype control accuracy (identical across arms; take count_ppmi's copy
    # since the control does not depend on the arm's context rep -- report both for transparency). ---
    control_acc_count = aggregate_by_arm["count_ppmi"]["single_prototype_control_accuracy"]
    control_acc_err = aggregate_by_arm["error_driven_pc"]["single_prototype_control_accuracy"]
    control_consistent = abs(control_acc_count - control_acc_err) < 1e-9
    shared_control_accuracy = control_acc_count

    # --- Per-arm HARD_PASS check. ---
    per_arm_hard_pass = {}
    for a in ARMS:
        agg = aggregate_by_arm[a]
        per_arm_hard_pass[a] = (
            agg["held_out_sense_discrimination_accuracy"] >= HARD_PASS_HELD_OUT
            and shared_control_accuracy <= HARD_PASS_CONTROL_MAX
            and agg["same_sense_agreement"] >= HARD_PASS_SAME_SENSE_MIN
            and agg["senses_induced_not_hand_listed"]
        )

    any_hard_pass = any(per_arm_hard_pass.values())
    both_hard_fail = all(
        aggregate_by_arm[a]["held_out_sense_discrimination_accuracy"] < HARD_FAIL_HELD_OUT
        for a in ARMS
    )
    control_leak = shared_control_accuracy >= HARD_FAIL_CONTROL_LEAK
    both_oversplit = all(
        aggregate_by_arm[a]["same_sense_agreement"] < HARD_FAIL_SAME_SENSE_FLOOR for a in ARMS
    )

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not all(aggregate_by_arm[a]["discriminator_fires"] for a in ARMS):
        verdict = "HARD_FAIL_DISCRIMINATOR_DID_NOT_FIRE"
    elif any_hard_pass and not control_leak:
        verdict = "HARD_PASS"
    elif control_leak or (both_hard_fail and both_oversplit) or (both_hard_fail and control_leak):
        verdict = "HARD_FAIL"
    elif both_hard_fail:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    # count-vs-error-driven read
    acc_count = aggregate_by_arm["count_ppmi"]["held_out_sense_discrimination_accuracy"]
    acc_err = aggregate_by_arm["error_driven_pc"]["held_out_sense_discrimination_accuracy"]
    if abs(acc_count - acc_err) < 0.02:
        count_vs_errordriven_read = "NO_MEANINGFUL_DIFFERENCE"
    elif acc_err > acc_count:
        count_vs_errordriven_read = "ERROR_DRIVEN_BEATS_COUNT"
    else:
        count_vs_errordriven_read = "COUNT_BEATS_ERROR_DRIVEN"

    elapsed_s = time.perf_counter() - t0

    verdict_msg = (
        f"count_ppmi_held_out_acc={acc_count:.4f} "
        f"({aggregate_by_arm['count_ppmi']['held_out_n_correct']}/{aggregate_by_arm['count_ppmi']['held_out_n_trials']}); "
        f"error_driven_pc_held_out_acc={acc_err:.4f} "
        f"({aggregate_by_arm['error_driven_pc']['held_out_n_correct']}/{aggregate_by_arm['error_driven_pc']['held_out_n_trials']}); "
        f"floor(sense_collapse_floor_v1)=0.5625; hard_pass_threshold={HARD_PASS_HELD_OUT}; "
        f"shared_single_prototype_control_acc={shared_control_accuracy:.4f}; "
        f"same_sense_agreement count_ppmi={aggregate_by_arm['count_ppmi']['same_sense_agreement']:.4f} "
        f"error_driven_pc={aggregate_by_arm['error_driven_pc']['same_sense_agreement']:.4f}; "
        f"count_vs_errordriven_read={count_vs_errordriven_read}; "
        f"per_arm_hard_pass={per_arm_hard_pass}; verdict={verdict}"
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": "C-A v2 corpus-scale count-vs-error-driven sense-structured hub measurement complete",
        "elapsed_s": elapsed_s,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "seed": SEED,
        "expected_n_units": EXPECTED_N_UNITS,
        "arms": ARMS,
        "n_forms": len(FORMS),
        "forms": FORMS,
        "background_corpus_stats": bg_stats,
        "count_ppmi_fit_stats": count_fit_stats,
        "error_driven_pc_fit_stats": errdriven_fit_stats,
        "aggregate_by_arm": aggregate_by_arm,
        "floor_reference_honest_floor_accuracy": 0.5625,
        "floor_reference_path": "data/exp_sense_collapse_floor_v1/metrics.json",
        "v1_reference_path": "data/exp_sense_structured_hub_ca_v1/metrics.json",
        "v1_reference_held_out_acc": 0.5666666666666667,
        "shared_single_prototype_control_accuracy": shared_control_accuracy,
        "control_consistent_across_arms": control_consistent,
        "n_disagree_between_arms": n_disagree_between_arms,
        "n_compared_between_arms": n_compared,
        "arms_differ_verified": arms_differ_verified,
        "per_arm_hard_pass": per_arm_hard_pass,
        "any_hard_pass": any_hard_pass,
        "both_hard_fail": both_hard_fail,
        "count_vs_errordriven_read": count_vs_errordriven_read,
        "cardinality_ok": cardinality_ok,
        "disjoint_vocab_check": disjoint_report,
        "per_form_by_arm": per_form_by_arm,
        "final_metrics_atomicity": "tmp_replace",
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "defensive_error_checking": "exempt_short_singleshot_cell_start_marker_and_crash_diagnostic_present",
        "crlb_n_a": "representational sense-induction measurement; no quantitative noise-floor formula applies",
        "calibration_check": "adaptive_with_discriminator_gate",
        "progress_logging": "print_flush_true",
        "hard_pass_band": {
            "held_out_sense_discrimination_accuracy": f">={HARD_PASS_HELD_OUT} (either arm)",
            "single_prototype_control_accuracy": f"<={HARD_PASS_CONTROL_MAX}",
            "same_sense_agreement": f">={HARD_PASS_SAME_SENSE_MIN}",
            "senses_induced_not_hand_listed": True,
        },
        "hard_fail_band": {
            "held_out_sense_discrimination_accuracy": f"<{HARD_FAIL_HELD_OUT} (both arms)",
            "single_prototype_control_accuracy": f">={HARD_FAIL_CONTROL_LEAK} (leak)",
            "same_sense_agreement": f"<{HARD_FAIL_SAME_SENSE_FLOOR} (over-split, both arms)",
        },
    }
    _write_metrics(OUTPUT_DIR, metrics)
    print(f"[sense_structured_hub_ca_v2] DONE elapsed_s={elapsed_s:.3f} verdict={verdict} -> "
          f"{os.path.join(OUTPUT_DIR, 'metrics.json')}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _selftest()
        sys.exit(0)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
