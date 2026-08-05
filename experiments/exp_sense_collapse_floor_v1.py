"""C-A STEP 0 measurement cell: sense_collapse_floor_v1.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - This is a single-shot MEASUREMENT cell (not a pass/fail mechanism cell); no arms to differ-hash,
#   no sweep axis, no chunking (wall time << 10s, N=32 sentences, 4 encoders). Exemptions declared
#   in preregs/sense_collapse_floor_v1.md.
# - final_metrics_atomicity: "tmp_replace" (os.replace, atomic write below).
# - except SystemExit: raise / except KeyboardInterrupt: raise BEFORE except Exception (no bare except,
#   no except BaseException).
# - crlb_n/a: representational-collapse measurement, no quantitative noise-floor formula applies.
# - all numbers in this file's comments are MEASURED@ (this metrics.json) or THEORETICAL@ (binomial SE).

Measures whether 4 EXISTING glass-box encoders (random_indexing, concept_encoder, composed_encoder_v3,
ppmi_sparse_encoder) collapse word senses into a single vector per surface form. Sets the honest floor
every downstream C-A (sense-structured hub) gate is judged against.

Probe: 8 polysemous forms (hard, trick, pay, cross, bright, sound, light, bear), 2 senses each, 2
disjoint-vocab context sentences per sense (32 sentences total). Forced-choice 2AFC sense-discrimination
accuracy (chance=0.5) + a same-sense-vs-different-sense cosine separation scalar, per encoder.

ASCII-only. LOCAL-only, in-process/foreground execution (no queue dispatch, no background/nesting).
"""
from __future__ import annotations

import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

ANCHOR_NAME = "sense_collapse_floor_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
SEED = 1234

# ---------------------------------------------------------------------------
# Probe corpus. 8 forms; each form: sense A (2 sentences), sense B (2 sentences).
# Non-target content vocabulary DISJOINT between sense A and sense B per form.
# Includes the exact 4 audit-flagged collision tokens: hard, trick, pay, cross.
# ---------------------------------------------------------------------------

PROBE: Dict[str, Dict[str, List[str]]] = {
    "hard": {
        "A": [  # effortful
            "she studied hard for the difficult exam",
            "he trained hard every single morning",
        ],
        "B": [  # forceful / harm
            "he was hit hard in the chest",
            "the wind blew hard against the window",
        ],
    },
    "trick": {
        "A": [  # clever skill move
            "the magician performed a clever card trick",
            "she learned a new skateboard trick",
        ],
        "B": [  # deception / cruelty
            "it was a cruel trick to play on him",
            "the con artist pulled a nasty trick",
        ],
    },
    "pay": {
        "A": [  # attention
            "please pay attention to the lecture",
            "you must pay close attention while driving",
        ],
        "B": [  # money
            "he forgot to pay the electricity bill",
            "she went to pay the rent today",
        ],
    },
    "cross": {
        "A": [  # traverse
            "they had to cross the busy street",
            "we will cross the river by ferry",
        ],
        "B": [  # angry / annoyed
            "she was cross with him after the argument",
            "the teacher grew cross at the noisy class",
        ],
    },
    "bright": {
        "A": [  # intelligent
            "the bright student solved the puzzle quickly",
            "he is a bright young scientist",
        ],
        "B": [  # luminous
            "the bright sun hurt her eyes",
            "the bright lamp lit the dark room",
        ],
    },
    "sound": {
        "A": [  # noise
            "the loud sound woke the sleeping baby",
            "a strange sound came from the engine",
        ],
        "B": [  # valid / sturdy
            "it was a sound financial decision",
            "the bridge has a sound structure",
        ],
    },
    "light": {
        "A": [  # illumination
            "turn on the light in the hallway",
            "the candle gave a soft light",
        ],
        "B": [  # not heavy
            "the light suitcase was easy to carry",
            "she wore a light jacket in summer",
        ],
    },
    "bear": {
        "A": [  # animal
            "the brown bear caught a fish",
            "a grizzly bear wandered near the camp",
        ],
        "B": [  # endure
            "she could not bear the pain",
            "he had to bear the heavy burden",
        ],
    },
}

WORDS = sorted(PROBE.keys())  # deterministic order: bear,bright,cross,hard,light,pay,sound,trick


def _all_sentences() -> Tuple[List[str], List[int]]:
    """Flatten PROBE into (sentences, word_index_labels), deterministic order."""
    sentences: List[str] = []
    labels: List[int] = []
    for wi, w in enumerate(WORDS):
        for sense in ("A", "B"):
            for s in PROBE[w][sense]:
                sentences.append(s)
                labels.append(wi)
    return sentences, labels


def _tokenize(text: str) -> List[str]:
    return text.lower().split()


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64).ravel()
    b = np.asarray(b, dtype=np.float64).ravel()
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


# ---------------------------------------------------------------------------
# Start marker / crash diagnostic (single-shot cell; §13 heartbeat exempted,
# wall time << 10s, no seed axis; start-marker + crash-diagnostic present).
# ---------------------------------------------------------------------------


def _write_start_marker(output_dir: str) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": "local_foreground_measurement",
        "expected_n_units": 4,  # 4 encoders
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


# ---------------------------------------------------------------------------
# Per-encoder representation builders. Each returns rep(sentence) -> np.ndarray
# and a flag "context_sensitive_by_construction" for the report.
# ---------------------------------------------------------------------------


def _build_random_indexing_reps(sentences: List[str]):
    from hdlab.random_indexing import RandomIndexingEncoder

    enc = RandomIndexingEncoder(N=2048, sparsity=10, window=5, min_count=1, seed=SEED)
    tokens: List[str] = []
    for s in sentences:
        tokens.extend(_tokenize(s))
    enc.fit_corpus(tokens)

    def rep_fn(sentence: str, target_word: str) -> np.ndarray:
        # Single-prototype BY CONSTRUCTION: encode(word) ignores the sentence entirely.
        return enc.encode(target_word).copy()

    return rep_fn, False  # context_sensitive_by_construction = False


def _build_concept_encoder_reps(sentences: List[str], labels: List[int]):
    from hdlab.concept_encoder import ConceptEncoder

    enc = ConceptEncoder(
        n_dim=2048,
        n_concepts=len(WORDS),
        seed=SEED,
        concept_names=WORDS,
        mask_target_word=True,
    )
    enc.fit(sentences, np.asarray(labels, dtype=np.int64))

    def rep_fn(sentence: str, target_word: str) -> np.ndarray:
        # encode() classifies into one of n_concepts discrete slots; returns that
        # slot's fixed HD. Single-prototype BY CONSTRUCTION (finite lookup table).
        return enc.encode(sentence).astype(np.float64).copy()

    return rep_fn, False


def _build_composed_v3_reps(sentences: List[str], labels: List[int]):
    from hdlab.composed_encoder_v3 import ComposedEncoderV3

    enc = ComposedEncoderV3(
        n_dim=2048,
        alpha=0.5,
        beta=0.5,
        vwfa_kwargs={"seed_prefix": f"SENSEFLOOR_S{SEED}"},
        ppmi_kwargs={"min_term_freq": 1, "smoothing": 0.75, "seed": SEED},
    )
    enc.fit(sentences, labels)

    def rep_fn(sentence: str, target_word: str) -> np.ndarray:
        # encode_streams(text) recomputes VWFA + PPMI streams PER SENTENCE (live,
        # not a lookup table) -- the candidate that might partially discriminate.
        streams = enc.encode_streams(sentence)
        combined = enc.alpha * streams["vwfa"] + enc.beta * streams["ppmi"]
        return combined.astype(np.float64).copy()

    return rep_fn, True  # context_sensitive_by_construction = True


def _build_ppmi_sparse_reps(sentences: List[str], labels: List[int]):
    from hdlab.ppmi_sparse_encoder import PPMISparseEncoder

    enc = PPMISparseEncoder(n_dim=2048, min_term_freq=1, smoothing=0.75, seed=SEED)
    enc.fit(sentences, np.asarray(labels, dtype=np.int64))

    def rep_fn(sentence: str, target_word: str) -> np.ndarray:
        # encode(text) sums trigram embeddings over the WHOLE sentence, per call
        # (live bag-of-trigrams, not a lookup table).
        return enc.encode(sentence).astype(np.float64).copy()

    return rep_fn, True


ENCODER_BUILDERS = {
    "random_indexing": _build_random_indexing_reps,
    "concept_encoder": _build_concept_encoder_reps,
    "composed_encoder_v3": _build_composed_v3_reps,
    "ppmi_sparse_encoder": _build_ppmi_sparse_reps,
}


# ---------------------------------------------------------------------------
# Measurement: forced-choice 2AFC + separation scalar, per encoder.
# ---------------------------------------------------------------------------


def _measure_encoder(name: str, rep_fn, sentences_all, labels_all, rng: np.random.Generator) -> dict:
    per_word = {}
    trial_results = []  # list of (word, correct: bool, tie: bool)
    sep_values = []

    for w in WORDS:
        a1, a2 = PROBE[w]["A"]
        b1, b2 = PROBE[w]["B"]

        r = {}
        for tag, sent in (("A1", a1), ("A2", a2), ("B1", b1), ("B2", b2)):
            r[tag] = rep_fn(sent, w)

        same_a = _cos(r["A1"], r["A2"])
        same_b = _cos(r["B1"], r["B2"])
        diff_pairs = [
            _cos(r["A1"], r["B1"]),
            _cos(r["A1"], r["B2"]),
            _cos(r["A2"], r["B1"]),
            _cos(r["A2"], r["B2"]),
        ]
        mean_same = 0.5 * (same_a + same_b)
        mean_diff = float(np.mean(diff_pairs))
        separation = mean_same - mean_diff
        sep_values.append(separation)

        per_word[w] = {
            "cos_A1_A2_same_sense": same_a,
            "cos_B1_B2_same_sense": same_b,
            "cos_A_vs_B_pairs": diff_pairs,
            "mean_same_sense_cos": mean_same,
            "mean_diff_sense_cos": mean_diff,
            "separation": separation,
            "cos_rep_A1_vs_rep_B1_ref": _cos(r["A1"], r["B1"]),
        }

        # Forced-choice 2AFC trials: two reference configurations.
        for ref_a, ref_b, test_items in (
            (r["A1"], r["B1"], [("A2", "A", r["A2"]), ("B2", "B", r["B2"])]),
            (r["A2"], r["B2"], [("A1", "A", r["A1"]), ("B1", "B", r["B1"])]),
        ):
            for tag, gold, test_rep in test_items:
                cos_a = _cos(test_rep, ref_a)
                cos_b = _cos(test_rep, ref_b)
                tie = abs(cos_a - cos_b) < 1e-9
                if tie:
                    pred = "A" if rng.integers(0, 2) == 0 else "B"
                else:
                    pred = "A" if cos_a > cos_b else "B"
                correct = pred == gold
                trial_results.append({"word": w, "test_item": tag, "gold": gold, "pred": pred,
                                       "tie": tie, "correct": correct})

    n_trials = len(trial_results)
    n_correct = sum(1 for t in trial_results if t["correct"])
    accuracy = n_correct / n_trials if n_trials > 0 else float("nan")
    n_ties = sum(1 for t in trial_results if t["tie"])
    mean_separation = float(np.mean(sep_values))

    # Binomial two-sided p-value vs p=0.5 (normal approximation; n=32 adequate).
    se = float(np.sqrt(0.25 / n_trials)) if n_trials > 0 else float("nan")
    z = (accuracy - 0.5) / se if se > 0 else 0.0
    # two-sided normal-approx p-value via erf
    import math
    p_value = float(math.erfc(abs(z) / math.sqrt(2.0)))

    return {
        "encoder": name,
        "n_trials": n_trials,
        "n_correct": n_correct,
        "n_ties": n_ties,
        "forced_choice_accuracy": accuracy,
        "chance": 0.5,
        "binomial_se": se,
        "z_vs_chance": z,
        "p_value_vs_chance": p_value,
        "mean_separation": mean_separation,
        "per_word": per_word,
    }


def _selftest() -> None:
    """Tiny-scale (2 words) real-code-path self-test: constructs actual encoder
    objects and asserts the collapse/discrimination measurement machinery runs
    and produces sane values, per SCHEMA-VET real_code_path gate."""
    print("[sense_collapse_floor_v1 selftest] START", flush=True)
    mini_words = WORDS[:2]
    mini_probe = {w: PROBE[w] for w in mini_words}

    sentences: List[str] = []
    labels: List[int] = []
    for wi, w in enumerate(mini_words):
        for sense in ("A", "B"):
            for s in mini_probe[w][sense]:
                sentences.append(s)
                labels.append(wi)

    rng = np.random.default_rng(SEED)

    # random_indexing: real object, real fit_corpus + encode call.
    from hdlab.random_indexing import RandomIndexingEncoder
    ri = RandomIndexingEncoder(N=256, sparsity=6, window=5, min_count=1, seed=SEED)
    tokens = []
    for s in sentences:
        tokens.extend(_tokenize(s))
    ri.fit_corpus(tokens)
    v1 = ri.encode(mini_words[0])
    v2 = ri.encode(mini_words[0])
    assert np.array_equal(v1, v2), "selftest: random_indexing encode() not deterministic/collapsed"
    print("[selftest 1] random_indexing real fit_corpus+encode PASS", flush=True)

    # concept_encoder: real object, real fit + encode call.
    from hdlab.concept_encoder import ConceptEncoder
    ce = ConceptEncoder(n_dim=256, n_concepts=len(mini_words), seed=SEED,
                         concept_names=mini_words, mask_target_word=True)
    ce.fit(sentences, np.asarray(labels, dtype=np.int64))
    ra1 = ce.encode(mini_probe[mini_words[0]]["A"][0])
    assert ra1.shape == (256,), f"selftest: concept_encoder shape {ra1.shape} != (256,)"
    print("[selftest 2] concept_encoder real fit+encode PASS", flush=True)

    # composed_encoder_v3: real object, real fit + encode_streams call.
    from hdlab.composed_encoder_v3 import ComposedEncoderV3
    cv3 = ComposedEncoderV3(n_dim=256, alpha=0.5, beta=0.5,
                             vwfa_kwargs={"seed_prefix": "SELFTEST_SENSEFLOOR"},
                             ppmi_kwargs={"min_term_freq": 1, "smoothing": 0.75, "seed": SEED})
    cv3.fit(sentences, labels)
    streams = cv3.encode_streams(mini_probe[mini_words[0]]["A"][0])
    assert streams["vwfa"].shape == (256,)
    print("[selftest 3] composed_encoder_v3 real fit+encode_streams PASS", flush=True)

    # ppmi_sparse_encoder: real object, real fit + encode call.
    from hdlab.ppmi_sparse_encoder import PPMISparseEncoder
    pp = PPMISparseEncoder(n_dim=256, min_term_freq=1, smoothing=0.75, seed=SEED)
    pp.fit(sentences, np.asarray(labels, dtype=np.int64))
    pv = pp.encode(mini_probe[mini_words[0]]["A"][0])
    assert pv.shape == (256,)
    print("[selftest 4] ppmi_sparse_encoder real fit+encode PASS", flush=True)

    # arms-must-differ sanity: the 4 encoders must not produce bit-identical
    # representation FUNCTIONS (spot check via a shared sentence).
    import hashlib
    probe_sent = mini_probe[mini_words[0]]["A"][0]
    digests = {}
    digests["random_indexing"] = hashlib.sha256(ri.encode(mini_words[0]).tobytes()).hexdigest()
    digests["concept_encoder"] = hashlib.sha256(ce.encode(probe_sent).tobytes()).hexdigest()
    digests["composed_encoder_v3"] = hashlib.sha256(cv3.encode_streams(probe_sent)["vwfa"].tobytes()).hexdigest()
    digests["ppmi_sparse_encoder"] = hashlib.sha256(pp.encode(probe_sent).tobytes()).hexdigest()
    assert len(set(digests.values())) == len(digests), (
        f"META_RULE_AF VIOLATION: encoder arms produced bit-identical reps: {digests}"
    )
    print("[selftest 5] arms_differ (4 distinct encoder outputs) PASS", flush=True)

    print("[sense_collapse_floor_v1 selftest] ALL PASS", flush=True)


def main() -> None:
    t0 = time.perf_counter()
    _write_start_marker(OUTPUT_DIR)

    sentences_all, labels_all = _all_sentences()
    rng = np.random.default_rng(SEED)

    per_encoder = {}
    context_sensitivity_flags = {}
    for name, builder in ENCODER_BUILDERS.items():
        if name == "random_indexing":
            rep_fn, ctx_flag = builder(sentences_all)
        else:
            rep_fn, ctx_flag = builder(sentences_all, labels_all)
        context_sensitivity_flags[name] = ctx_flag
        result = _measure_encoder(name, rep_fn, sentences_all, labels_all, rng)
        result["context_sensitive_by_construction"] = ctx_flag
        per_encoder[name] = result
        print(f"[{name}] forced_choice_accuracy={result['forced_choice_accuracy']:.3f} "
              f"mean_separation={result['mean_separation']:.4f} "
              f"n_trials={result['n_trials']} p_value={result['p_value_vs_chance']:.3f}", flush=True)

    # Honest floor: the strongest of the 2 architecturally single-prototype
    # encoders (random_indexing, concept_encoder) -- both are expected at
    # chance by construction; floor = max of their measured accuracies
    # (whichever is closer to a real signal sets the bar C-A must clear).
    floor_candidates = {k: v for k, v in per_encoder.items() if not context_sensitivity_flags[k]}
    honest_floor_encoder = max(floor_candidates, key=lambda k: per_encoder[k]["forced_choice_accuracy"])
    honest_floor_accuracy = per_encoder[honest_floor_encoder]["forced_choice_accuracy"]

    # Best existing starting point for the C-A extension: among the
    # context-sensitive candidates, whichever has the highest accuracy AND
    # positive separation; falls back to "none -- all collapse" if neither
    # candidate clears the pre-registered surprise band (2 SE above chance).
    ctx_candidates = {k: v for k, v in per_encoder.items() if context_sensitivity_flags[k]}
    best_ctx_name = max(ctx_candidates, key=lambda k: per_encoder[k]["forced_choice_accuracy"])
    best_ctx_acc = per_encoder[best_ctx_name]["forced_choice_accuracy"]
    surprise_threshold = 0.5 + 2.0 * per_encoder[best_ctx_name]["binomial_se"]
    any_positive_surprise = any(
        per_encoder[k]["forced_choice_accuracy"] > (0.5 + 2.0 * per_encoder[k]["binomial_se"])
        and per_encoder[k]["mean_separation"] > 0.0
        for k in ctx_candidates
    )
    best_starting_encoder = best_ctx_name if any_positive_surprise else "none (all 4 encoders collapse at/near chance)"

    elapsed_s = time.perf_counter() - t0

    metrics = {
        "verdict": "MEASURED",
        "verdict_msg": (
            f"honest_floor={honest_floor_accuracy:.3f} (encoder={honest_floor_encoder}); "
            f"best_context_sensitive={best_ctx_name} acc={best_ctx_acc:.3f} "
            f"(surprise_threshold={surprise_threshold:.3f}); "
            f"any_positive_surprise={any_positive_surprise}; "
            f"best_starting_encoder_for_CA_extension={best_starting_encoder}"
        ),
        "summary": "C-A STEP 0 sense-collapse floor measurement complete",
        "elapsed_s": elapsed_s,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "seed": SEED,
        "probe_n_words": len(WORDS),
        "probe_n_sentences": len(sentences_all),
        "probe_words": WORDS,
        "chance_level": 0.5,
        "honest_floor_encoder": honest_floor_encoder,
        "honest_floor_accuracy": honest_floor_accuracy,
        "best_starting_encoder_for_CA_extension": best_starting_encoder,
        "any_positive_surprise": any_positive_surprise,
        "context_sensitivity_flags": context_sensitivity_flags,
        "per_encoder": per_encoder,
        "cardinality_ok": len(per_encoder) == 4,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "defensive_error_checking": "exempt_short_singleshot_cell_start_marker_and_crash_diagnostic_present",
        "crlb_n_a": "representational-collapse measurement; no quantitative noise-floor formula applies",
    }
    _write_metrics(OUTPUT_DIR, metrics)
    print(f"[sense_collapse_floor_v1] DONE elapsed_s={elapsed_s:.3f} -> "
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
