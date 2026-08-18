"""trigram_downstream_ingest_probe_v1 -- Drill C1: trigram-sufficiency for ingest.

Drill source: USER directive 2026-06-27 (drill C1) -- tests if existing
char-trigram encoder is sufficient for STORE-AND-RETRIEVE on real Lean Mathlib
theorems, WITHOUT requiring the still-in-flight sub_atom encoder v2.

Hypothesis: drill C1 says trigram d3=0.66 on real Mathlib means trigram already
encodes Mathlib well enough for store-and-retrieve (not perfect subtree recovery
-- that's the sub_atom encoder's job -- but sufficient ingest recall).

If trigram recall@1 >= 0.70 with cv < 0.10, downstream ingest cells (e.g.,
lean_mathlib_ingest) can proceed on the chain-grade trigram encoder while
sub_atom encoder matures. If recall@1 < 0.30, ingest must wait for sub_atom.

ARMS (2):
  ARM_TRIGRAM_ENCODE  -- hdlab.char_trigram_encoder.CharTrigramEncoder
  ARM_RANDOM_ENCODE   -- random bipolar HD per theorem (chance baseline; ~1/N)

TASK: store N theorems; query each by partial-cue (first 60% of token chars);
measure recall@1 (does the full theorem rank #1 in cosine similarity?).

BANDS (HARD-LOCKED, PROSPECTIVE):
  HARD_PASS: trigram recall@1 >= 0.70 with cv < 0.10 across seeds AND
             trigram - random gap >= 0.40 (clean separation)
  MIDDLE_BAND: trigram recall@1 in [0.30, 0.70) OR gap in [0.20, 0.40)
  HARD_FAIL: trigram recall@1 < 0.30 (trigram insufficient; gate sub_atom)

CARDINALITY_OK (META_RULE_H):
  EXPECTED_N_UNITS_FULL = 5 seeds * 2 arms = 10
  EXPECTED_N_UNITS_SMOKE = 2 seeds * 2 arms = 4
  EXPECTED_N_UNITS_SELFTEST = 1 seed * 2 arms = 2

PROT-018: no _n suffix (capability-test).
ASCII-only; no unicode; no emojis; no em-dashes.
Author: hdi_orchestrator (Opus 4.7-1M) 2026-06-27 (USER drill C1).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "trigram_downstream_ingest_probe_v1"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands LOCKED at module init
HP_RECALL_AT_1 = 0.70
HP_CV_MAX = 0.10
HP_TRIG_OVER_RAND_GAP = 0.40
MB_RECALL_AT_1 = 0.30
MB_GAP = 0.20
HF_RECALL_AT_1 = 0.30

EXPECTED_ARMS = ["trigram_encode", "random_encode"]

if SELF_TEST_MODE:
    N_DIM = 1024
    N_THEOREMS = 20
    SEEDS = [7]
    CUE_FRAC = 0.6
elif RUN_MODE == "smoke":
    N_DIM = 2048
    N_THEOREMS = 50
    SEEDS = [7, 17]
    CUE_FRAC = 0.6
else:
    N_DIM = 4096
    N_THEOREMS = 100
    SEEDS = [7, 17, 23, 31, 41]
    CUE_FRAC = 0.6

EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,n_theorems=%d,seeds=%s,mode=%s,cue_frac=%.2f,"
    "HP_recall@1>=%.2f,HP_cv<=%.2f,HP_gap>=%.2f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, N_THEOREMS, SEEDS, RUN_MODE, CUE_FRAC,
    HP_RECALL_AT_1, HP_CV_MAX, HP_TRIG_OVER_RAND_GAP, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                           extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_trigram_downstream_ingest_probe",
        }
        if extra:
            metrics.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(metrics, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        sentinel = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_trigram_downstream_ingest_probe_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- REAL LEAN MATHLIB CORPUS (baked-in) ---------
# Curated from Mathlib4 pretty-printer; long, nested formal-math expressions.
# Subset of LEAN_MATHLIB_SAMPLES from exp_sub_atom_token_stream_encoder_v2_real_mathlib.py.
LEAN_MATHLIB_CORPUS = [
    "theorem add_comm (a b : Nat) : a + b = b + a",
    "theorem mul_assoc (a b c : Nat) : a * b * c = a * (b * c)",
    "theorem zero_add (n : Nat) : 0 + n = n",
    "theorem add_zero (n : Nat) : n + 0 = n",
    "theorem succ_add (a b : Nat) : Nat.succ a + b = Nat.succ (a + b)",
    "theorem add_succ (a b : Nat) : a + Nat.succ b = Nat.succ (a + b)",
    "theorem mul_zero (n : Nat) : n * 0 = 0",
    "theorem zero_mul (n : Nat) : 0 * n = 0",
    "theorem mul_one (n : Nat) : n * 1 = n",
    "theorem one_mul (n : Nat) : 1 * n = n",
    "theorem mul_comm (a b : Nat) : a * b = b * a",
    "theorem add_assoc (a b c : Nat) : a + b + c = a + (b + c)",
    "theorem left_distrib (a b c : Nat) : a * (b + c) = a * b + a * c",
    "theorem right_distrib (a b c : Nat) : (a + b) * c = a * c + b * c",
    "theorem sub_self (n : Nat) : n - n = 0",
    "theorem pow_zero (a : Nat) : a ^ 0 = 1",
    "theorem pow_succ (a n : Nat) : a ^ Nat.succ n = a ^ n * a",
    "theorem le_refl (n : Nat) : n <= n",
    "theorem le_trans (a b c : Nat) (h1 : a <= b) (h2 : b <= c) : a <= c",
    "theorem le_antisymm (a b : Nat) (h1 : a <= b) (h2 : b <= a) : a = b",
    "theorem lt_irrefl (n : Nat) : not (n < n)",
    "theorem lt_trans (a b c : Nat) (h1 : a < b) (h2 : b < c) : a < c",
    "theorem List.nil_append (l : List a) : List.nil ++ l = l",
    "theorem List.append_nil (l : List a) : l ++ List.nil = l",
    "theorem List.append_assoc (a b c : List x) : a ++ b ++ c = a ++ (b ++ c)",
    "theorem List.length_append (l1 l2 : List a) : (l1 ++ l2).length = l1.length + l2.length",
    "theorem List.map_id (l : List a) : l.map id = l",
    "theorem List.map_map (f : a -> b) (g : b -> c) (l : List a) : (l.map f).map g = l.map (g comp f)",
    "theorem List.reverse_reverse (l : List a) : l.reverse.reverse = l",
    "theorem List.length_reverse (l : List a) : l.reverse.length = l.length",
    "theorem Set.union_comm (s t : Set a) : s union t = t union s",
    "theorem Set.inter_comm (s t : Set a) : s inter t = t inter s",
    "theorem Set.union_assoc (s t u : Set a) : s union t union u = s union (t union u)",
    "theorem Set.inter_assoc (s t u : Set a) : s inter t inter u = s inter (t inter u)",
    "theorem Set.union_self (s : Set a) : s union s = s",
    "theorem Set.inter_self (s : Set a) : s inter s = s",
    "theorem Set.empty_union (s : Set a) : empty union s = s",
    "theorem Set.union_empty (s : Set a) : s union empty = s",
    "theorem Set.inter_empty (s : Set a) : s inter empty = empty",
    "theorem Set.empty_inter (s : Set a) : empty inter s = empty",
    "theorem Group.mul_left_cancel (a b c : G) (h : a * b = a * c) : b = c",
    "theorem Group.mul_right_cancel (a b c : G) (h : b * a = c * a) : b = c",
    "theorem Group.inv_inv (a : G) : (a^(-1))^(-1) = a",
    "theorem Group.mul_inv_self (a : G) : a * a^(-1) = 1",
    "theorem Group.inv_mul_self (a : G) : a^(-1) * a = 1",
    "theorem Group.one_inv : (1 : G)^(-1) = 1",
    "theorem Group.mul_one (a : G) : a * 1 = a",
    "theorem Group.one_mul (a : G) : 1 * a = a",
    "theorem Ring.zero_mul (a : R) : 0 * a = 0",
    "theorem Ring.mul_zero (a : R) : a * 0 = 0",
    "theorem Ring.neg_neg (a : R) : -(-a) = a",
    "theorem Ring.neg_add (a b : R) : -(a + b) = -a + -b",
    "theorem Ring.sub_eq_add_neg (a b : R) : a - b = a + -b",
    "theorem Real.add_lt_add_left (a b c : Real) (h : b < c) : a + b < a + c",
    "theorem Real.mul_pos (a b : Real) (h1 : 0 < a) (h2 : 0 < b) : 0 < a * b",
    "theorem Real.abs_nonneg (a : Real) : 0 <= |a|",
    "theorem Real.abs_zero : |0| = 0",
    "theorem Real.abs_neg (a : Real) : |(-a)| = |a|",
    "theorem Real.abs_add (a b : Real) : |a + b| <= |a| + |b|",
    "theorem Real.sqrt_nonneg (a : Real) : 0 <= Real.sqrt a",
    "theorem Real.sqrt_sq (a : Real) (h : 0 <= a) : Real.sqrt (a * a) = a",
    "theorem Real.sq_sqrt (a : Real) (h : 0 <= a) : Real.sqrt a * Real.sqrt a = a",
    "theorem Int.add_neg_self (a : Int) : a + -a = 0",
    "theorem Int.neg_add_self (a : Int) : -a + a = 0",
    "theorem Int.mul_neg (a b : Int) : a * (-b) = -(a * b)",
    "theorem Int.neg_mul (a b : Int) : (-a) * b = -(a * b)",
    "theorem Int.neg_one_mul (a : Int) : (-1) * a = -a",
    "theorem Function.comp_id (f : a -> b) : f comp id = f",
    "theorem Function.id_comp (f : a -> b) : id comp f = f",
    "theorem Function.comp_assoc (f : a -> b) (g : b -> c) (h : c -> d) : h comp (g comp f) = (h comp g) comp f",
    "theorem Function.injective_id : Function.Injective (id : a -> a)",
    "theorem Function.surjective_id : Function.Surjective (id : a -> a)",
    "theorem Nat.div_self (n : Nat) (h : 0 < n) : n / n = 1",
    "theorem Nat.mod_self (n : Nat) : n % n = 0",
    "theorem Nat.zero_div (n : Nat) : 0 / n = 0",
    "theorem Nat.div_one (n : Nat) : n / 1 = n",
    "theorem Nat.mod_one (n : Nat) : n % 1 = 0",
    "theorem Nat.add_div_right (a b : Nat) (h : 0 < b) : (a + b) / b = a / b + 1",
    "theorem Nat.gcd_zero_left (n : Nat) : Nat.gcd 0 n = n",
    "theorem Nat.gcd_zero_right (n : Nat) : Nat.gcd n 0 = n",
    "theorem Nat.gcd_self (n : Nat) : Nat.gcd n n = n",
    "theorem Nat.gcd_comm (a b : Nat) : Nat.gcd a b = Nat.gcd b a",
    "theorem Nat.gcd_assoc (a b c : Nat) : Nat.gcd (Nat.gcd a b) c = Nat.gcd a (Nat.gcd b c)",
    "theorem Finset.card_empty : (empty : Finset a).card = 0",
    "theorem Finset.card_singleton (a : x) : ({a} : Finset x).card = 1",
    "theorem Finset.card_insert_of_not_mem (s : Finset a) (h : a not_in s) : (insert a s).card = s.card + 1",
    "theorem Finset.union_comm (s t : Finset a) : s union t = t union s",
    "theorem Finset.inter_comm (s t : Finset a) : s inter t = t inter s",
    "theorem Finset.subset_refl (s : Finset a) : s subset s",
    "theorem Finset.subset_trans (s t u : Finset a) (h1 : s subset t) (h2 : t subset u) : s subset u",
    "theorem Matrix.add_comm (A B : Matrix m n R) : A + B = B + A",
    "theorem Matrix.mul_assoc (A B C : Matrix m n R) : A * B * C = A * (B * C)",
    "theorem Matrix.transpose_transpose (A : Matrix m n R) : A.transpose.transpose = A",
    "theorem Matrix.transpose_add (A B : Matrix m n R) : (A + B).transpose = A.transpose + B.transpose",
    "theorem Topology.continuous_id : Continuous (id : X -> X)",
    "theorem Topology.continuous_const (c : Y) : Continuous (fun _ => c : X -> Y)",
    "theorem Topology.continuous_comp (f : X -> Y) (g : Y -> Z) (hf : Continuous f) (hg : Continuous g) : Continuous (g comp f)",
    "theorem MeasureTheory.measure_empty : mu empty = 0",
    "theorem MeasureTheory.measure_mono (s t : Set X) (h : s subset t) : mu s <= mu t",
    "theorem Cardinal.add_comm (a b : Cardinal) : a + b = b + a",
    "theorem Cardinal.mul_comm (a b : Cardinal) : a * b = b * a",
    "theorem Order.le_refl (a : alpha) : a <= a",
    "theorem Order.le_trans (a b c : alpha) (h1 : a <= b) (h2 : b <= c) : a <= c",
    "theorem Order.lt_of_le_of_lt (a b c : alpha) (h1 : a <= b) (h2 : b < c) : a < c",
    "theorem Polynomial.degree_C (c : R) : (Polynomial.C c).degree <= 0",
    "theorem Polynomial.eval_C (c x : R) : (Polynomial.C c).eval x = c",
    "theorem Polynomial.eval_X (x : R) : Polynomial.X.eval x = x",
]


def _encode_trigram(text: str, n_dim: int, encoder) -> np.ndarray:
    """Trigram bipolar HD via hdlab.char_trigram_encoder.CharTrigramEncoder."""
    return encoder.encode(text)


def _encode_random(text: str, n_dim: int, seed: int) -> np.ndarray:
    """Random bipolar HD; deterministic from (text_hash, seed). Chance baseline."""
    import hashlib
    h = hashlib.blake2b(text.encode("utf-8") + str(seed).encode(), digest_size=8).digest()
    sub_seed = int.from_bytes(h, "big") & 0xFFFFFFFF
    rng = np.random.default_rng(sub_seed)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _make_cue(text: str, frac: float) -> str:
    """Take first `frac` of the character stream as the partial-cue."""
    n = max(3, int(len(text) * frac))
    return text[:n]


def _run_seed(seed: int, corpus: List[str], n_dim: int,
              cue_frac: float) -> Dict[str, Any]:
    """One seed run; both arms; returns per-arm recall@1 + diagnostics."""
    rng = np.random.default_rng(seed)
    # Shuffle corpus deterministically per-seed (so cardinality of stored set varies);
    # then take N_THEOREMS slice.
    idx = rng.permutation(len(corpus))
    selected = [corpus[i] for i in idx[:N_THEOREMS]]

    out: Dict[str, Any] = {
        "seed": seed,
        "n_theorems": len(selected),
        "n_dim": n_dim,
        "cue_frac": cue_frac,
    }

    # ARM TRIGRAM ----------------------------------------------------------
    try:
        from hdlab.char_trigram_encoder import CharTrigramEncoder
    except Exception as e:
        # Surface, do not silently mask. Skunkworks rule.
        raise RuntimeError("CharTrigramEncoder import failed: %s" % e)

    encoder = CharTrigramEncoder(n_dim=n_dim)
    stored_trig = np.stack([_encode_trigram(t, n_dim, encoder) for t in selected])

    # Query: encode each cue, find argmax cosine over stored. Recall@1 = (argmax == i).
    cues = [_make_cue(t, cue_frac) for t in selected]
    cue_vecs_trig = np.stack([_encode_trigram(c, n_dim, encoder) for c in cues])

    # Cosine matrix: (N_THEOREMS, N_THEOREMS); row i is cue_i vs all stored.
    norms_stored = np.linalg.norm(stored_trig, axis=1, keepdims=True)
    norms_cues = np.linalg.norm(cue_vecs_trig, axis=1, keepdims=True)
    norms_stored[norms_stored == 0] = 1.0
    norms_cues[norms_cues == 0] = 1.0
    sim_trig = (cue_vecs_trig @ stored_trig.T) / (norms_cues * norms_stored.T)
    pred_trig = np.argmax(sim_trig, axis=1)
    correct_trig = int(np.sum(pred_trig == np.arange(len(selected))))
    recall_trig = correct_trig / max(1, len(selected))
    out["trigram_recall_at_1"] = recall_trig
    out["trigram_correct"] = correct_trig

    # ARM RANDOM ----------------------------------------------------------
    stored_rand = np.stack([_encode_random(t, n_dim, seed) for t in selected])
    cue_vecs_rand = np.stack([_encode_random(c, n_dim, seed) for c in cues])
    norms_stored_r = np.linalg.norm(stored_rand, axis=1, keepdims=True)
    norms_cues_r = np.linalg.norm(cue_vecs_rand, axis=1, keepdims=True)
    norms_stored_r[norms_stored_r == 0] = 1.0
    norms_cues_r[norms_cues_r == 0] = 1.0
    sim_rand = (cue_vecs_rand @ stored_rand.T) / (norms_cues_r * norms_stored_r.T)
    pred_rand = np.argmax(sim_rand, axis=1)
    correct_rand = int(np.sum(pred_rand == np.arange(len(selected))))
    recall_rand = correct_rand / max(1, len(selected))
    out["random_recall_at_1"] = recall_rand
    out["random_correct"] = correct_rand

    out["gap_trigram_minus_random"] = recall_trig - recall_rand
    return out


def main() -> int:
    print("[main] %s start RUN_MODE=%s N_DIM=%d N_THEOREMS=%d SEEDS=%s"
          % (ANCHOR_NAME, RUN_MODE, N_DIM, N_THEOREMS, SEEDS), flush=True)
    print("[main] CONFIG_VERSION=%s" % CONFIG_VERSION, flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    # L1: STARTED metrics on first line (per Skunkworks hardening rule)
    _write_minimal_metrics(out_dir, "UNKNOWN",
                           "STARTED RUN_MODE=%s" % RUN_MODE,
                           extra={"_status": "running"})

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d of %d seeds already complete; running %s"
          % (len(done), len(SEEDS), remaining), flush=True)

    try:
        for seed in remaining:
            t0 = time.time()
            result = _run_seed(seed, LEAN_MATHLIB_CORPUS, N_DIM, CUE_FRAC)
            result["_run_config"] = run_config
            result["seed_wall_s"] = round(time.time() - t0, 2)
            write_partial(out_dir, seed, result)
            print("[seed %d] trig_r@1=%.3f rand_r@1=%.3f gap=%.3f wall=%.1fs"
                  % (seed, result["trigram_recall_at_1"],
                     result["random_recall_at_1"],
                     result["gap_trigram_minus_random"],
                     result["seed_wall_s"]), flush=True)
    except Exception as e:
        print("[main] EXCEPTION during seeds: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        _write_minimal_metrics(out_dir, "UNKNOWN",
                               "RUNTIME_CRASH: %s: %s" % (type(e).__name__, str(e)),
                               extra={"_traceback": traceback.format_exc()})
        return 2

    per_seed = aggregate_partials(out_dir, SEEDS)

    # Aggregate: mean + std across seeds for each arm
    trig_recalls = [v["trigram_recall_at_1"] for v in per_seed.values()]
    rand_recalls = [v["random_recall_at_1"] for v in per_seed.values()]
    gaps = [v["gap_trigram_minus_random"] for v in per_seed.values()]

    n_obs = len(per_seed) * len(EXPECTED_ARMS)
    if n_obs < EXPECTED_N_UNITS:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL_CARDINALITY_BREACH expected=%d observed=%d"
                       % (EXPECTED_N_UNITS, n_obs))
        _write_minimal_metrics(out_dir, verdict, verdict_msg, extra={
            "per_seed": per_seed,
            "expected_n_units": EXPECTED_N_UNITS,
            "observed_n_units": n_obs,
        })
        print("[main] %s" % verdict_msg, flush=True)
        return 0

    trig_mean = float(np.mean(trig_recalls))
    trig_std = float(np.std(trig_recalls))
    trig_cv = trig_std / max(1e-9, abs(trig_mean))
    rand_mean = float(np.mean(rand_recalls))
    gap_mean = float(np.mean(gaps))

    # Verdict computation
    verdict = "MIDDLE_BAND"
    notes = []
    if trig_mean >= HP_RECALL_AT_1 and trig_cv < HP_CV_MAX and gap_mean >= HP_TRIG_OVER_RAND_GAP:
        verdict = "HARD_PASS"
        notes.append("trigram sufficient for downstream ingest")
    elif trig_mean < HF_RECALL_AT_1:
        verdict = "HARD_FAIL"
        notes.append("trigram insufficient for ingest; gate sub_atom encoder")
    elif trig_mean >= MB_RECALL_AT_1 and gap_mean >= MB_GAP:
        verdict = "MIDDLE_BAND"
        notes.append("trigram partial; sub_atom may still improve")
    else:
        verdict = "MIDDLE_BAND"
        notes.append("trigram marginal")

    if trig_cv >= HP_CV_MAX and verdict == "HARD_PASS":
        verdict = "MIDDLE_BAND"
        notes.append("cv exceeds HARD_PASS ceiling")

    verdict_msg = ("trig_r@1=%.3f(cv=%.3f) rand_r@1=%.3f gap=%.3f | %s"
                   % (trig_mean, trig_cv, rand_mean, gap_mean, "; ".join(notes)))

    _write_minimal_metrics(out_dir, verdict, verdict_msg, extra={
        "per_seed": per_seed,
        "per_arm": {
            "trigram_encode": {
                "mean_recall_at_1": trig_mean,
                "std_recall_at_1": trig_std,
                "cv_recall_at_1": trig_cv,
                "per_seed_recall": dict(zip([str(s) for s in SEEDS], trig_recalls)),
            },
            "random_encode": {
                "mean_recall_at_1": rand_mean,
                "per_seed_recall": dict(zip([str(s) for s in SEEDS], rand_recalls)),
            },
        },
        "gap_trigram_minus_random_mean": gap_mean,
        "expected_n_units": EXPECTED_N_UNITS,
        "observed_n_units": n_obs,
        "cardinality_ok": True,
        "verdict_bands": {
            "HP_recall_at_1": HP_RECALL_AT_1,
            "HP_cv_max": HP_CV_MAX,
            "HP_gap": HP_TRIG_OVER_RAND_GAP,
            "MB_recall_at_1": MB_RECALL_AT_1,
            "MB_gap": MB_GAP,
            "HF_recall_at_1": HF_RECALL_AT_1,
        },
    })
    print("[main] verdict=%s %s" % (verdict, verdict_msg), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        # Allow explicit sys.exit() inside main() to propagate without
        # being misclassified as IMPORT_CRASH (caught 2026-06-27: prior
        # `except BaseException` swallowed SystemExit(0) from successful
        # `sys.exit(rc)` below, writing IMPORT_CRASH sentinel over real PASS).
        raise
    except BaseException as e:
        _write_import_crash_sentinel(e)
        raise
    sys.exit(rc)
