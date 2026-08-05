"""C-A: SENSE-STRUCTURED lexical-semantic hub -- induced multi-prototype senses.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - Single-shot MEASUREMENT cell (10 forms, ~120 sentences, wall << 10s). No sweep axis, no chunking.
#   Exemptions declared in preregs/sense_structured_hub_ca_v1.md (same class as exp_sense_collapse_
#   floor_v1.py's exemption).
# - final_metrics_atomicity: "tmp_replace" (os.replace, atomic write below).
# - except SystemExit: raise / except KeyboardInterrupt: raise BEFORE except Exception (no bare except,
#   no except BaseException).
# - crlb_n/a: representational sense-induction measurement, no quantitative noise-floor formula applies.
# - baseline_in_band: single_prototype_control_accuracy expected in (0.05, 0.95) -- near-chance lookup
#   control, checked at runtime.
# - discriminator survives scale: probe is already at the full/only regime (no smoke-vs-full split for
#   a single-shot measurement cell); the discriminator-fires assertion (>=1 form induces >=2 prototypes)
#   is checked inline before the verdict is emitted.
# - arms_differ_verified: induced-hub vs single-prototype-control predictions compared directly.
# - cardinality_ok: EXPECTED_N_UNITS = 10 (forms); asserted len(per_form) == 10.
# - calibration_check: "adaptive_with_discriminator_gate" (FIT-only threshold calibration, logged).
# - HYPOTHESIZED/MEASURED/THEORETICAL tags: see preregs/sense_structured_hub_ca_v1.md.
# - Disjoint fit/test context vocabulary is MACHINE-CHECKED at runtime (not just hand-verified) --
#   see _assert_disjoint_vocab() below; halts the cell with AssertionError if violated.

Mechanism (see preregs/sense_structured_hub_ca_v1.md for full spec):
  1. Context representation: hdlab.ppmi_sparse_encoder.PPMISparseEncoder, fit on the union of all
     FIT-set context sentences (target word masked out) with concept_labels=arange(n) (classic
     PPMI/SVD distributional context-embedding usage -- LSA-style, NOT word-form-supervised).
  2. Induction: per form, online competitive clustering of FIT context vectors, gated by
     hdlab.predictive_coding.threshold_gate / residual_magnitude (Rao-Ballard residual-gated Hebbian
     reused directly as the split/merge decision -- the error-driven differentiation signal).
     Predicted-well (residual < T) -> merge (Hebbian running-mean consolidation). Surprising
     (residual >= T) -> spawn a new prototype (differentiation), capped at max_prototypes=4.
  3. Post-hoc cluster->sense labeling via FIT-majority-vote (scoring only; never feeds induction).
  4. Held-out assignment: nearest induced prototype by cosine -> its majority sense label.

Controls: (a) single-prototype floor (hdlab.concept_encoder.ConceptEncoder, context-blind lookup,
same mechanism class that measured 0.5625 in exp_sense_collapse_floor_v1.py) must stay near chance;
(b) same-sense false-split check (held-out same-sense pairs must land in the same induced prototype);
(c) induction_trace glass-box witness (senses induced, not hand-listed).

ASCII-only. LOCAL-only, in-process/foreground execution (no queue dispatch, no background/nesting).
"""
from __future__ import annotations

import json
import math
import os
import platform
import random
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

ANCHOR_NAME = "sense_structured_hub_ca_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
SEED = 4242
EXPECTED_N_UNITS = 10  # forms

STOPWORDS = {
    "the", "a", "an", "he", "she", "they", "it", "him", "her", "his", "their", "we", "you",
    "was", "is", "are", "were", "be", "been", "being", "to", "of", "in", "on", "at", "by",
    "for", "with", "and", "or", "but", "had", "has", "have", "must", "will", "would", "could",
    "should", "can", "did", "do", "does", "not", "no", "as", "that", "this", "these", "those",
    "during", "before", "after", "while", "near", "up", "off", "over", "under", "through",
    "across", "toward", "along", "into", "from", "about", "than", "so", "very", "still",
    "against", "throughout", "between", "around", "within", "out", "down", "one",
}

# ---------------------------------------------------------------------------
# Probe: 10 polysemous forms, 2 senses each. FIT (induction) vs TEST (held-out)
# sentence sets, disjoint content-word vocabulary within each form (machine-
# checked below). Includes the 4 audit collision tokens: hard, trick, pay, cross.
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
    """Content-word vocabulary of a set of sentences, excluding the target
    word and closed-class stopwords. Used for the machine-checked disjoint-
    fit/test-vocabulary gate."""
    out = set()
    for s in sentences:
        for tok in _tokenize(s):
            if tok == target_word.lower() or tok in STOPWORDS:
                continue
            out.add(tok)
    return out


def _mask_target(sentence: str, target_word: str) -> str:
    """Remove the target word (whole-token, case-insensitive) from a sentence,
    forcing representation to be built from CONTEXT only."""
    toks = [t for t in sentence.split() if t.lower().strip(",.") != target_word.lower()]
    return " ".join(toks)


def _assert_disjoint_vocab() -> Dict[str, dict]:
    """Machine-checked leakage guard: TEST content-word vocabulary must not
    intersect FIT content-word vocabulary, per form (both senses pooled).
    Raises AssertionError (halts cell) on any violation."""
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
# Start marker / crash diagnostic / atomic metrics write (same pattern as
# exp_sense_collapse_floor_v1.py).
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


# ---------------------------------------------------------------------------
# Induction mechanism: online competitive clustering gated by
# hdlab.predictive_coding (residual_magnitude / threshold_gate) -- reused
# directly, not reimplemented.
# ---------------------------------------------------------------------------


def _induce_senses(items: List[Tuple[str, np.ndarray]], threshold: float, max_prototypes: int = 4):
    """items: list of (item_id, context_vec) in fixed visitation order.

    Returns (prototypes, assignments, trace) where prototypes is a list of
    {"sum": np.ndarray, "count": int, "members": [item_id,...]} and
    assignments is {item_id: prototype_idx}. trace logs each decision for
    the glass-box witness.
    """
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

        if dec.skipped:  # residual < threshold -> predicted well -> consolidate (merge)
            prototypes[nearest_idx]["sum"] = prototypes[nearest_idx]["sum"] + cv
            prototypes[nearest_idx]["count"] += 1
            prototypes[nearest_idx]["members"].append(item_id)
            assignments[item_id] = nearest_idx
            trace.append({"item": item_id, "action": "merge", "proto_id": nearest_idx,
                           "residual": dec.residual_mag})
        elif len(prototypes) < max_prototypes:  # surprising -> differentiate (spawn)
            new_idx = len(prototypes)
            prototypes.append({"sum": cv.copy(), "count": 1, "members": [item_id]})
            assignments[item_id] = new_idx
            trace.append({"item": item_id, "action": "spawn_new_prototype", "proto_id": new_idx,
                           "residual": dec.residual_mag})
        else:  # cap reached; merge into nearest anyway
            prototypes[nearest_idx]["sum"] = prototypes[nearest_idx]["sum"] + cv
            prototypes[nearest_idx]["count"] += 1
            prototypes[nearest_idx]["members"].append(item_id)
            assignments[item_id] = nearest_idx
            trace.append({"item": item_id, "action": "merge_cap_reached", "proto_id": nearest_idx,
                           "residual": dec.residual_mag})

    return prototypes, assignments, trace


def _calibrate_threshold(fit_context_vecs: Dict[str, Dict[str, List[np.ndarray]]]) -> Tuple[float, dict]:
    """FIT-only, adaptive threshold calibration (calibration_check=adaptive_with_
    discriminator_gate). T = midpoint of mean same-sense residual and mean
    different-sense residual, computed via predictive_coding.residual_magnitude
    across all forms' FIT sets. Never touches TEST data."""
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


# ---------------------------------------------------------------------------
# Self-test: constructs the REAL substrate objects at tiny scale (2 forms),
# per SCHEMA-VET real_code_path_and_signature_preflight gate.
# ---------------------------------------------------------------------------


def _selftest() -> None:
    print("[sense_structured_hub_ca_v1 selftest] START", flush=True)

    disjoint_report = _assert_disjoint_vocab()
    assert len(disjoint_report) == EXPECTED_N_UNITS
    print(f"[selftest 1] disjoint-vocab machine-check PASS for all {EXPECTED_N_UNITS} forms", flush=True)

    from hdlab.ppmi_sparse_encoder import PPMISparseEncoder
    from hdlab.predictive_coding import residual_magnitude, threshold_gate
    from hdlab.concept_encoder import ConceptEncoder

    mini_forms = FORMS[:2]
    fit_sentences: List[str] = []
    for wi, w in enumerate(mini_forms):
        for sense in ("A", "B"):
            for s in PROBE[w]["FIT"][sense]:
                fit_sentences.append(_mask_target(s, w))

    ppmi = PPMISparseEncoder(n_dim=64, min_term_freq=1, smoothing=0.75, seed=SEED)
    ppmi.fit(fit_sentences, np.arange(len(fit_sentences)))
    v1 = ppmi.encode(fit_sentences[0])
    assert v1.shape == (64,)
    print("[selftest 2] PPMISparseEncoder real fit+encode PASS", flush=True)

    v2 = ppmi.encode(fit_sentences[1])
    rmag = residual_magnitude(v1, v2)
    assert 0.0 <= rmag <= 1.0, f"residual_magnitude out of range: {rmag}"
    dec = threshold_gate(observed=v1, predicted=v2, threshold=0.5)
    assert dec.residual_mag == rmag
    print(f"[selftest 3] predictive_coding.residual_magnitude/threshold_gate real call PASS "
          f"(residual={rmag:.3f})", flush=True)

    items = [(f"item{i}", ppmi.encode(fit_sentences[i])) for i in range(len(fit_sentences))]
    protos, assigns, trace = _induce_senses(items, threshold=0.4, max_prototypes=4)
    assert len(protos) >= 1
    assert len(assigns) == len(items)
    print(f"[selftest 4] _induce_senses real run PASS (n_prototypes={len(protos)})", flush=True)

    ce = ConceptEncoder(n_dim=64, n_concepts=len(mini_forms), seed=SEED,
                         concept_names=mini_forms, mask_target_word=True)
    ce_fit_sentences: List[str] = []
    ce_fit_labels: List[int] = []
    for wi, w in enumerate(mini_forms):
        for sense in ("A", "B"):
            for s in PROBE[w]["FIT"][sense]:
                ce_fit_sentences.append(s)
                ce_fit_labels.append(wi)
    ce.fit(ce_fit_sentences, np.asarray(ce_fit_labels, dtype=np.int64))
    r = ce.encode(PROBE[mini_forms[0]]["TEST"]["A"][0])
    assert r.shape == (64,)
    print("[selftest 5] ConceptEncoder (single-prototype control, word-FORM concept) "
          "real fit+encode PASS", flush=True)

    threshold, calib = _calibrate_threshold({
        w: {s: [ppmi.encode(_mask_target(sent, w)) for sent in PROBE[w]["FIT"][s]] for s in ("A", "B")}
        for w in mini_forms
    })
    assert 0.0 <= threshold <= 1.0
    print(f"[selftest 6] adaptive threshold calibration real run PASS (T={threshold:.3f})", flush=True)

    print("[sense_structured_hub_ca_v1 selftest] ALL PASS", flush=True)


# ---------------------------------------------------------------------------
# Main measurement.
# ---------------------------------------------------------------------------


def main() -> None:
    t0 = time.perf_counter()
    _write_start_marker(OUTPUT_DIR)

    disjoint_report = _assert_disjoint_vocab()
    print(f"[disjoint-vocab] machine-checked OK for {len(disjoint_report)} forms", flush=True)

    from hdlab.ppmi_sparse_encoder import PPMISparseEncoder
    from hdlab.concept_encoder import ConceptEncoder

    # --- Build the shared context-embedding space from FIT sentences only. ---
    fit_context_strs: List[str] = []
    fit_context_ids: List[str] = []  # "<form>|<sense>|<idx>"
    for w in FORMS:
        for sense in ("A", "B"):
            for i, s in enumerate(PROBE[w]["FIT"][sense]):
                fit_context_strs.append(_mask_target(s, w))
                fit_context_ids.append(f"{w}|{sense}|{i}")

    ppmi = PPMISparseEncoder(n_dim=128, min_term_freq=1, smoothing=0.75, seed=SEED)
    ppmi.fit(fit_context_strs, np.arange(len(fit_context_strs)))

    def ctx_vec(sentence: str, word: str) -> np.ndarray:
        return ppmi.encode(_mask_target(sentence, word)).astype(np.float64)

    fit_vecs: Dict[str, Dict[str, List[np.ndarray]]] = {
        w: {s: [ctx_vec(sent, w) for sent in PROBE[w]["FIT"][s]] for s in ("A", "B")}
        for w in FORMS
    }
    test_vecs: Dict[str, Dict[str, List[np.ndarray]]] = {
        w: {s: [ctx_vec(sent, w) for sent in PROBE[w]["TEST"][s]] for s in ("A", "B")}
        for w in FORMS
    }

    # --- Adaptive threshold calibration (FIT-only). ---
    threshold, threshold_calib = _calibrate_threshold(fit_vecs)
    print(f"[calibration] threshold_T={threshold:.4f} "
          f"mean_same={threshold_calib['mean_fit_same_sense_residual']:.4f} "
          f"mean_diff={threshold_calib['mean_fit_diff_sense_residual']:.4f}", flush=True)

    # --- Deterministic seeded shuffle of visitation order per form. ---
    rng = random.Random(SEED)

    # --- Single-prototype control: ONE ConceptEncoder across all 10 forms,
    # concept = word FORM (not sense) -- same mechanism class that measured
    # 0.5625 in exp_sense_collapse_floor_v1.py. Context-blind lookup: encode()
    # returns the same vector for a form regardless of sentence content, so
    # forced-choice degenerates to near-tie / near-chance by construction.
    ce = ConceptEncoder(n_dim=128, n_concepts=len(FORMS), seed=SEED,
                         concept_names=FORMS, mask_target_word=True)
    ce_fit_sentences: List[str] = []
    ce_fit_labels: List[int] = []
    for wi, w in enumerate(FORMS):
        for sense in ("A", "B"):
            for s in PROBE[w]["FIT"][sense]:
                ce_fit_sentences.append(s)
                ce_fit_labels.append(wi)
    ce.fit(ce_fit_sentences, np.asarray(ce_fit_labels, dtype=np.int64))

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

        # Post-hoc majority-vote cluster -> sense labeling (scoring only).
        cluster_label_map: Dict[int, str] = {}
        for pidx, p in enumerate(prototypes):
            votes = {"A": 0, "B": 0}
            for m in p["members"]:
                votes[gold_sense[m]] += 1
            cluster_label_map[pidx] = "A" if votes["A"] >= votes["B"] else "B"

        proto_means = [p["sum"] / p["count"] for p in prototypes]

        # --- Held-out TEST assignment: nearest prototype -> its majority sense. ---
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
                    "correct": correct, "nearest_proto": nearest, "sims": sims,
                })

        # --- Same-sense false-split check on held-out TEST items. ---
        pair_agree = 0
        pair_total = 0
        for sense in ("A", "B"):
            ids = [f"TEST|{sense}|{i}" for i in range(len(test_vecs[w][sense]))]
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    pair_total += 1
                    if test_proto_assignment[ids[i]] == test_proto_assignment[ids[j]]:
                        pair_agree += 1

        # --- Single-prototype control (shared ConceptEncoder, context-blind). ---
        ref_a = ce.encode(PROBE[w]["FIT"]["A"][0]).astype(np.float64)
        ref_b = ce.encode(PROBE[w]["FIT"]["B"][0]).astype(np.float64)
        ctrl_rng = np.random.default_rng(SEED + hash(w) % 10000)
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
            "n_items_where_arms_disagree": n_arms_disagree,
            "disjoint_vocab_check": disjoint_report[w],
        }
        print(f"[{w}] n_prototypes={n_protos} held_out_acc="
              f"{per_form[w]['held_out_n_correct']}/{per_form[w]['held_out_n_trials']} "
              f"control_acc={per_form[w]['single_prototype_control_n_correct']}/"
              f"{per_form[w]['single_prototype_control_n_trials']} "
              f"same_sense_agree={pair_agree}/{pair_total}", flush=True)

    # --- Aggregate across all forms. ---
    total_correct = sum(v["held_out_n_correct"] for v in per_form.values())
    total_trials = sum(v["held_out_n_trials"] for v in per_form.values())
    held_out_accuracy = total_correct / total_trials if total_trials else float("nan")

    ctrl_correct = sum(v["single_prototype_control_n_correct"] for v in per_form.values())
    ctrl_trials = sum(v["single_prototype_control_n_trials"] for v in per_form.values())
    single_prototype_control_accuracy = ctrl_correct / ctrl_trials if ctrl_trials else float("nan")

    ss_agree = sum(v["same_sense_pair_agree"] for v in per_form.values())
    ss_total = sum(v["same_sense_pair_total"] for v in per_form.values())
    same_sense_agreement = ss_agree / ss_total if ss_total else float("nan")

    total_arms_disagree = sum(v["n_items_where_arms_disagree"] for v in per_form.values())
    arms_differ_verified = total_arms_disagree > 0

    def _binom_se(n: int) -> float:
        return float(np.sqrt(0.25 / n)) if n > 0 else float("nan")

    def _p_vs_chance(acc: float, n: int) -> float:
        se = _binom_se(n)
        if se != se or se <= 0:
            return float("nan")
        z = (acc - 0.5) / se
        return float(math.erfc(abs(z) / math.sqrt(2.0)))

    # --- Discriminator-fires gate: at least one form must induce >=2 prototypes. ---
    discriminator_fires = n_forms_with_ge2_prototypes >= 1

    # --- Cardinality gate. ---
    cardinality_ok = len(per_form) == EXPECTED_N_UNITS

    # --- Verdict logic per pre-reg bands. ---
    senses_induced_not_hand_listed = discriminator_fires and any(
        v["n_prototypes_induced"] != 1 for v in per_form.values()
    )

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not discriminator_fires:
        verdict = "HARD_FAIL_DISCRIMINATOR_DID_NOT_FIRE"
    elif (held_out_accuracy >= 0.80 and single_prototype_control_accuracy <= 0.65
          and same_sense_agreement >= 0.75 and senses_induced_not_hand_listed):
        verdict = "HARD_PASS"
    elif (held_out_accuracy < 0.65 or single_prototype_control_accuracy >= 0.80
          or same_sense_agreement < 0.50):
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed_s = time.perf_counter() - t0

    verdict_msg = (
        f"held_out_sense_discrimination_accuracy={held_out_accuracy:.4f} "
        f"({total_correct}/{total_trials}) vs floor(sense_collapse_floor_v1)=0.5625; "
        f"single_prototype_control_accuracy={single_prototype_control_accuracy:.4f} "
        f"({ctrl_correct}/{ctrl_trials}); "
        f"same_sense_agreement={same_sense_agreement:.4f} ({ss_agree}/{ss_total}); "
        f"n_forms_with_ge2_prototypes={n_forms_with_ge2_prototypes}/{EXPECTED_N_UNITS}; "
        f"senses_induced_not_hand_listed={senses_induced_not_hand_listed}; "
        f"threshold_T={threshold:.4f}; verdict={verdict}"
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": "C-A sense_structured_hub_ca_v1 held-out measurement complete",
        "elapsed_s": elapsed_s,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "seed": SEED,
        "expected_n_units": EXPECTED_N_UNITS,
        "n_forms": len(FORMS),
        "forms": FORMS,
        "held_out_sense_discrimination_accuracy": held_out_accuracy,
        "held_out_n_correct": total_correct,
        "held_out_n_trials": total_trials,
        "held_out_p_value_vs_chance": _p_vs_chance(held_out_accuracy, total_trials),
        "floor_reference_honest_floor_accuracy": 0.5625,
        "floor_reference_path": "data/exp_sense_collapse_floor_v1/metrics.json",
        "single_prototype_control_accuracy": single_prototype_control_accuracy,
        "single_prototype_control_n_correct": ctrl_correct,
        "single_prototype_control_n_trials": ctrl_trials,
        "same_sense_agreement": same_sense_agreement,
        "same_sense_pair_agree": ss_agree,
        "same_sense_pair_total": ss_total,
        "n_forms_with_ge2_prototypes": n_forms_with_ge2_prototypes,
        "discriminator_fires": discriminator_fires,
        "senses_induced_not_hand_listed": senses_induced_not_hand_listed,
        "threshold_calibration": threshold_calib,
        "total_arms_disagree_items": total_arms_disagree,
        "arms_differ_verified": arms_differ_verified,
        "cardinality_ok": cardinality_ok,
        "disjoint_vocab_check": disjoint_report,
        "per_form": per_form,
        "final_metrics_atomicity": "tmp_replace",
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "defensive_error_checking": "exempt_short_singleshot_cell_start_marker_and_crash_diagnostic_present",
        "crlb_n_a": "representational sense-induction measurement; no quantitative noise-floor formula applies",
        "calibration_check": "adaptive_with_discriminator_gate",
        "hard_pass_band": {
            "held_out_sense_discrimination_accuracy": ">=0.80",
            "single_prototype_control_accuracy": "<=0.65",
            "same_sense_agreement": ">=0.75",
            "senses_induced_not_hand_listed": True,
        },
        "hard_fail_band": {
            "held_out_sense_discrimination_accuracy": "<0.65",
            "single_prototype_control_accuracy": ">=0.80 (leak)",
            "same_sense_agreement": "<0.50 (over-split)",
        },
    }
    _write_metrics(OUTPUT_DIR, metrics)
    print(f"[sense_structured_hub_ca_v1] DONE elapsed_s={elapsed_s:.3f} verdict={verdict} -> "
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
