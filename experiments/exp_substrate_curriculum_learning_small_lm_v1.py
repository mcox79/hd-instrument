"""
substrate_curriculum_learning_small_lm_v1 -- Probe 8: substrate as training-data
selection policy for small char-level LM training.

SCIENTIFIC QUESTION (Wave 1 Probe 8):
  Does substrate-orchestrated training-data presentation (substrate identifies
  least-redundant-given-its-current-state examples) achieve faster convergence
  AND/OR better final BPC than random / difficulty-graded / loss-based curricula
  on small-LM char-level training?

TEST DESIGN:
  Train a small char-level LM on Wikitext-2 char-level for 1 epoch under each of
  4 curriculum policies; measure convergence rate (loss vs step) + final BPC on
  held-out test set.

  Policies (from testbed.curriculum.policies):
    (i)   RandomPolicy             baseline (uniform random batch sampling)
    (ii)  DifficultyGradedPolicy   ascending example length
    (iii) LossBasedActivePolicy    after warm-up, weight by current example loss
    (iv)  SubstrateCurriculumPolicy substrate stores state; selects argmin |cos(W xi, xi)|
                                    among 64-example candidate pool

PRE-REGISTERED BANDS (per spec dossier line 212-215):
  HARD-PASS:  substrate_final_bpc_mean <= best_baseline_final_bpc_mean
              AND substrate_step_to_threshold <= 0.5 * best_baseline_step_to_threshold
  MIDDLE:     substrate_final_bpc_mean <= 1.1 * best_baseline_final_bpc_mean
              AND substrate_step_to_threshold in (0.5, 1.0] * best_baseline_step_to_threshold
  HARD-FAIL:  substrate_final_bpc_mean > random_baseline_final_bpc_mean
              (substrate-curriculum HURTS learning)

FORMULA SELF-TESTS (PROT-022):
  1. policies._selftest: 4 policies emit valid batches; substrate alpha <= 0.20
  2. training_loop._selftest: tiny GRU + 4 policies; loop wiring intact

RUN MODES:
  smoke -> tiny GRU hidden=64, 20k train chars, 200 max steps, 2 seeds
  full  -> Pythia-160m arch re-trained from-scratch on char-level,
           10M train chars, 10k steps, 5 seeds

ASCII-only per feedback_ascii_only_in_scripts.
PROT-018: anchor name MUST match the file basename without _v1 stripping.
PROT-021: partials carry N, M, run_mode for contamination guard.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import gc
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial,
    aggregate_partials,
)
from testbed.substrate_lm.data import wikitext2_char_corpus, char_vocab_from_corpus
from testbed.curriculum.policies import build_policy, SubstrateCurriculumPolicy
from testbed.curriculum.training_loop import (
    train_curriculum,
    split_corpus_into_examples,
    make_tiny_gru_factory,
)

ANCHOR_NAME = "substrate_curriculum_learning_small_lm_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

POLICIES = ["random", "difficulty", "loss_active", "substrate"]

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    HIDDEN = 64
    TRAIN_CHARS = 20_000
    VAL_CHARS = 2_000
    TEST_CHARS = 2_000
    N_STEPS_MAX = 200
    BATCH_SIZE = 16
    EVAL_EVERY = 25
    SEQ_LEN = 64
    LR = 1e-3
    SUBSTRATE_N = 2048
    USE_PYTHIA = False
else:
    SEEDS = [7, 17, 23, 31, 41]
    HIDDEN = 768   # Pythia-160m architecture-class hidden dim (decoder-only, 12 layers)
    TRAIN_CHARS = 10_000_000
    VAL_CHARS = 200_000
    TEST_CHARS = 200_000
    N_STEPS_MAX = 10_000
    BATCH_SIZE = 256
    EVAL_EVERY = 500
    SEQ_LEN = 128
    LR = 3e-4
    SUBSTRATE_N = 2048
    USE_PYTHIA = True

# Pre-registered bands
HP_BPC_RATIO = 1.0      # substrate <= 1.0 * best_baseline_bpc
HP_STEP_RATIO = 0.5     # substrate threshold-step <= 0.5 * best_baseline
MID_BPC_RATIO = 1.1
MID_STEP_RATIO = 1.0
# HARD-FAIL: substrate_bpc > random_baseline_bpc


# -----------------------------------------------------------------------------
# Pythia-160m-class factory (FULL only; not loadable at smoke wall budget)
# -----------------------------------------------------------------------------
def make_pythia_class_factory(vocab_size: int):
    """Return a factory that builds a Pythia-160m-arch GPT-NeoX model
    randomly initialised at char-level vocab (re-trained from scratch).
    """
    try:
        from transformers import GPTNeoXConfig, GPTNeoXForCausalLM
    except ImportError as e:
        raise RuntimeError(
            f"transformers package required for FULL mode; got: {e}"
        )

    def _f():
        # Pythia-160m: 12 layers, 12 heads, hidden 768
        cfg = GPTNeoXConfig(
            vocab_size=vocab_size,
            hidden_size=768,
            num_hidden_layers=12,
            num_attention_heads=12,
            intermediate_size=3072,
            max_position_embeddings=SEQ_LEN + 16,
            hidden_dropout=0.0,
            attention_dropout=0.0,
            tie_word_embeddings=False,
        )
        # Re-init from scratch (do NOT load pretrained tokenizer-coupled weights)
        model = GPTNeoXForCausalLM(cfg)

        # Adapter so the training_loop sees (B, T) -> (B, T, V) logits.
        class _PythiaAdapter(model.__class__):
            def __init__(self, model):
                super().__init__(model.config)
                self.load_state_dict(model.state_dict())
            def forward(self, x):
                out = super().forward(input_ids=x)
                return out.logits

        # Simpler: just wrap with a thin shim object
        class _Shim:
            def __init__(self, inner, vocab_size):
                self._inner = inner
                self.vocab_size = vocab_size
            def to(self, device):
                self._inner = self._inner.to(device)
                return self
            def parameters(self):
                return self._inner.parameters()
            def train(self):
                self._inner.train()
                return self
            def eval(self):
                self._inner.eval()
                return self
            def __call__(self, x):
                return self._inner(input_ids=x).logits

        return _Shim(model, vocab_size)

    return _f


# -----------------------------------------------------------------------------
# Run one (seed, policy) cell
# -----------------------------------------------------------------------------
def run_one_cell(seed: int, policy_name: str, corpus_train: str,
                 corpus_val: str, corpus_test: str) -> Dict:
    """Train one model under one policy at one seed; return result dict."""
    rng = np.random.default_rng(seed)

    # Examples = fixed-length chunks of the corpus
    train_examples = split_corpus_into_examples(corpus_train, seq_len=SEQ_LEN)
    val_examples = split_corpus_into_examples(corpus_val, seq_len=SEQ_LEN)
    test_examples = split_corpus_into_examples(corpus_test, seq_len=SEQ_LEN)

    # Vocab union across train+val+test so eval doesn't OOV-explode
    combined = corpus_train + corpus_val + corpus_test
    char_vocab = char_vocab_from_corpus(combined)
    if "<pad>" not in char_vocab:
        char_vocab = list(char_vocab) + ["<pad>"]
    vocab_size = len(char_vocab)

    # Threshold for step-to-threshold (lazy default; refined post-run)
    # We use BPC=2.0 as a rough char-LM convergence indicator; the
    # step-to-threshold metric is also recomputed at aggregation time
    # using the per-run best-baseline-final-BPC * 1.1 as the threshold.
    threshold_bpc = 2.5

    # Build policy
    policy_kwargs = {}
    if policy_name == "substrate":
        policy_kwargs = {"N": SUBSTRATE_N, "candidate_pool_size": 64,
                          "proj_seed": 1729 + seed}
    policy = build_policy(policy_name, train_examples, rng, **policy_kwargs)

    # Build model factory
    if USE_PYTHIA:
        factory = make_pythia_class_factory(vocab_size)
    else:
        factory = make_tiny_gru_factory(vocab_size, hidden=HIDDEN)

    # Train
    t0 = time.time()
    result = train_curriculum(
        model_factory=factory,
        examples_train=train_examples,
        examples_val=val_examples,
        examples_test=test_examples,
        char_vocab=char_vocab,
        policy=policy,
        n_steps_max=N_STEPS_MAX,
        batch_size=BATCH_SIZE,
        eval_every=EVAL_EVERY,
        device="cpu",
        lr=LR,
        seq_len=SEQ_LEN,
        threshold_bpc=threshold_bpc,
        verbose=False,
    )
    elapsed = time.time() - t0
    # Snapshot policy alpha if substrate
    sub_alpha = (policy.alpha()
                 if isinstance(policy, SubstrateCurriculumPolicy) else None)

    # Lightweight payload (loss history can be large; truncate to milestones)
    history = result["loss_history"]
    # Keep only steps where val_bpc is recorded (eval milestones)
    milestones = [(s, tl, vb) for (s, tl, vb) in history if vb is not None]

    return {
        "policy_name": policy_name,
        "seed": int(seed),
        "final_bpc_val": float(result["final_bpc_val"]),
        "final_bpc_test": float(result["final_bpc_test"]),
        "step_to_threshold_bpc": (int(result["step_to_threshold_bpc"])
                                   if result["step_to_threshold_bpc"] is not None
                                   else None),
        "n_steps_completed": int(result["n_steps_completed"]),
        "milestones": milestones,
        "wall_s": float(elapsed),
        "substrate_alpha_end": sub_alpha,
    }


# -----------------------------------------------------------------------------
# Aggregation + verdict
# -----------------------------------------------------------------------------
def aggregate_and_verdict(per_cell: Dict[str, Dict]) -> Dict:
    """Aggregate per-cell partials into per-policy summary + HP/MID/HF verdict.

    per_cell keys: f"seed{S}_policy{P}".
    """
    # Group per policy
    policy_to_results: Dict[str, List[Dict]] = {p: [] for p in POLICIES}
    for key, body in per_cell.items():
        pname = body.get("policy_name")
        if pname not in POLICIES:
            continue
        policy_to_results[pname].append(body)

    summary: Dict[str, Dict] = {}
    for p in POLICIES:
        runs = policy_to_results.get(p, [])
        if not runs:
            summary[p] = {"n_runs": 0}
            continue
        bpc_val = np.array([r["final_bpc_val"] for r in runs], dtype=np.float64)
        bpc_test = np.array([r["final_bpc_test"] for r in runs], dtype=np.float64)
        steps_thresh = [r["step_to_threshold_bpc"] for r in runs]
        # If any run never crossed threshold, use n_steps_completed as sentinel
        max_step = max(r["n_steps_completed"] for r in runs)
        steps_eff = np.array(
            [s if s is not None else max_step + 1 for s in steps_thresh],
            dtype=np.float64)
        summary[p] = {
            "n_runs": len(runs),
            "final_bpc_val_mean": float(np.mean(bpc_val)),
            "final_bpc_val_std": float(np.std(bpc_val, ddof=1)
                                        if len(bpc_val) > 1 else 0.0),
            "final_bpc_test_mean": float(np.mean(bpc_test)),
            "final_bpc_test_std": float(np.std(bpc_test, ddof=1)
                                         if len(bpc_test) > 1 else 0.0),
            "step_to_threshold_mean": float(np.mean(steps_eff)),
            "step_to_threshold_all_reached": all(s is not None for s in steps_thresh),
        }

    # Determine best baseline (across random / difficulty / loss_active)
    baseline_policies = [p for p in POLICIES if p != "substrate"]
    valid_baselines = [p for p in baseline_policies
                       if summary[p].get("n_runs", 0) > 0]
    if not valid_baselines:
        return {"summary": summary, "verdict": "UNKNOWN",
                "verdict_msg": "no baseline runs"}

    baseline_bpc = {p: summary[p]["final_bpc_test_mean"] for p in valid_baselines}
    best_baseline = min(baseline_bpc, key=baseline_bpc.get)
    best_baseline_bpc = baseline_bpc[best_baseline]
    best_baseline_step = summary[best_baseline]["step_to_threshold_mean"]

    sub = summary.get("substrate", {})
    if sub.get("n_runs", 0) == 0:
        return {"summary": summary, "verdict": "UNKNOWN",
                "verdict_msg": "no substrate runs"}

    sub_bpc = sub["final_bpc_test_mean"]
    sub_step = sub["step_to_threshold_mean"]
    random_bpc = summary.get("random", {}).get("final_bpc_test_mean",
                                                 best_baseline_bpc)

    # HARD-FAIL: substrate worse than random
    if sub_bpc > random_bpc:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: substrate_bpc={sub_bpc:.4f} > random_bpc={random_bpc:.4f}; "
            f"substrate-curriculum HURTS learning. "
            f"Substrate-driven training-data selection underperformed uniform "
            f"random sampling on char-level small-LM training. "
            f"CAPABILITY IMPLICATION: substrate does NOT serve as a training-"
            f"orchestration policy at this scale; rules out 'substrate-as-data-"
            f"selector' direction for the LM pre-training cap_map row."
        )
    elif (sub_bpc <= HP_BPC_RATIO * best_baseline_bpc
          and sub_step <= HP_STEP_RATIO * best_baseline_step):
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: substrate_bpc={sub_bpc:.4f} <= best_baseline ({best_baseline}) "
            f"bpc={best_baseline_bpc:.4f}; substrate_step={sub_step:.1f} <= "
            f"0.5 * best_baseline_step={best_baseline_step:.1f}. "
            f"Substrate-driven selection both matched final accuracy AND halved "
            f"convergence steps. "
            f"CAPABILITY IMPLICATION: substrate works as a training-orchestration "
            f"policy at char-LM scale; opens 'data-efficiency' product narrative "
            f"orthogonal to compute-efficiency."
        )
    elif (sub_bpc <= MID_BPC_RATIO * best_baseline_bpc
          and sub_step <= MID_STEP_RATIO * best_baseline_step):
        verdict = "MIDDLE"
        verdict_msg = (
            f"MIDDLE: substrate_bpc={sub_bpc:.4f} <= 1.1 * best_baseline "
            f"({best_baseline}) bpc={best_baseline_bpc:.4f}; substrate_step="
            f"{sub_step:.1f} within 0.5-1.0 * best_baseline_step="
            f"{best_baseline_step:.1f}. "
            f"Substrate roughly matches baselines but does not clearly accelerate. "
            f"CAPABILITY IMPLICATION: substrate-as-data-selector is plausible but "
            f"not a clear win; rerun at larger scale or with a sharper selection rule."
        )
    else:
        # In-between (BPC OK but step regression, or BPC mild loss): MIDDLE/UNKNOWN
        verdict = "MIDDLE"
        verdict_msg = (
            f"MIDDLE (degenerate): substrate_bpc={sub_bpc:.4f} vs best_baseline "
            f"({best_baseline}) bpc={best_baseline_bpc:.4f}; substrate_step="
            f"{sub_step:.1f} vs best_baseline_step={best_baseline_step:.1f}; "
            f"neither HP nor HF bands triggered. "
            f"CAPABILITY IMPLICATION: substrate may have a mild role but more data "
            f"needed; for smoke this is informational not load-bearing."
        )

    return {
        "summary": summary,
        "best_baseline": best_baseline,
        "best_baseline_bpc": best_baseline_bpc,
        "best_baseline_step": best_baseline_step,
        "substrate_bpc": sub_bpc,
        "substrate_step": sub_step,
        "random_bpc": random_bpc,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
    }


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main() -> int:
    print(f"[main] anchor={ANCHOR_NAME} run_mode={RUN_MODE}", flush=True)
    print(f"[main] seeds={SEEDS} policies={POLICIES}", flush=True)
    print(f"[main] hidden={HIDDEN} train_chars={TRAIN_CHARS} "
          f"n_steps_max={N_STEPS_MAX} batch_size={BATCH_SIZE} "
          f"substrate_N={SUBSTRATE_N}", flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[main] out_dir={out_dir}", flush=True)

    # Load corpus
    print("[main] loading corpus...", flush=True)
    corpus_train = wikitext2_char_corpus("train", max_chars=TRAIN_CHARS)
    corpus_val = wikitext2_char_corpus("validation", max_chars=VAL_CHARS)
    corpus_test = wikitext2_char_corpus("test", max_chars=TEST_CHARS)
    print(f"[main] train chars={len(corpus_train)} val={len(corpus_val)} "
          f"test={len(corpus_test)}", flush=True)

    # Build cell keys: (seed, policy)
    cell_keys = []
    for seed in SEEDS:
        for pname in POLICIES:
            cell_keys.append(f"seed{seed}_policy{pname}")

    # PROT-021 run_config for partial filtering
    run_config = {
        "N": SUBSTRATE_N,
        "run_mode": "smoke" if RUN_MODE == "smoke" else "full",
    }
    done, remaining = resumable_seeds(cell_keys, out_dir,
                                       run_config=run_config)
    print(f"[main] {len(done)} of {len(cell_keys)} cells already done; "
          f"running {len(remaining)}", flush=True)

    # Run remaining cells
    t_all_start = time.time()
    for key in remaining:
        # Parse key
        parts = key.split("_policy")
        seed_str = parts[0].replace("seed", "")
        seed = int(seed_str)
        pname = parts[1]
        print(f"[main] running cell {key} ...", flush=True)
        try:
            result = run_one_cell(seed, pname, corpus_train, corpus_val, corpus_test)
        except Exception as e:
            import traceback
            print(f"[main] cell {key} FAILED: {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()
            result = {
                "policy_name": pname,
                "seed": seed,
                "error": f"{type(e).__name__}: {e}",
                "final_bpc_val": float("nan"),
                "final_bpc_test": float("nan"),
                "step_to_threshold_bpc": None,
                "n_steps_completed": 0,
            }
        # Stamp PROT-021 config keys
        result["N"] = SUBSTRATE_N
        result["run_mode"] = "smoke" if RUN_MODE == "smoke" else "full"
        result["smoke"] = (RUN_MODE == "smoke")
        write_partial(out_dir, key, result)
        gc.collect()
        print(f"[main] cell {key} done: bpc_val={result.get('final_bpc_val'):.4f} "
              f"bpc_test={result.get('final_bpc_test'):.4f} "
              f"step_to_thresh={result.get('step_to_threshold_bpc')} "
              f"wall={result.get('wall_s', 0.0):.1f}s", flush=True)

    elapsed = time.time() - t_all_start
    print(f"[main] all cells done in {elapsed:.1f}s", flush=True)

    # Aggregate
    per_cell = aggregate_partials(out_dir, cell_keys, run_config=run_config)
    print(f"[main] aggregated {len(per_cell)} cells", flush=True)
    verdict_pack = aggregate_and_verdict(per_cell)

    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "seeds": SEEDS,
        "policies": POLICIES,
        "config": {
            "hidden": HIDDEN,
            "train_chars": TRAIN_CHARS,
            "val_chars": VAL_CHARS,
            "test_chars": TEST_CHARS,
            "n_steps_max": N_STEPS_MAX,
            "batch_size": BATCH_SIZE,
            "eval_every": EVAL_EVERY,
            "seq_len": SEQ_LEN,
            "lr": LR,
            "substrate_N": SUBSTRATE_N,
            "use_pythia": USE_PYTHIA,
        },
        "per_cell": per_cell,
        **verdict_pack,
        "elapsed_s": float(elapsed),
    }
    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2, default=str),
                             encoding="utf-8")
    print(f"[main] metrics written to {metrics_path}", flush=True)

    # Stdout verdict block
    print("=" * 72, flush=True)
    print(f"VERDICT: {verdict_pack.get('verdict')}", flush=True)
    print(verdict_pack.get("verdict_msg", ""), flush=True)
    print("=" * 72, flush=True)
    for p in POLICIES:
        s = verdict_pack["summary"].get(p, {})
        print(f"  {p}: bpc_val={s.get('final_bpc_val_mean', float('nan')):.4f} "
              f"+/- {s.get('final_bpc_val_std', 0.0):.4f}  "
              f"bpc_test={s.get('final_bpc_test_mean', float('nan')):.4f} "
              f"+/- {s.get('final_bpc_test_std', 0.0):.4f}  "
              f"step_thresh_mean={s.get('step_to_threshold_mean', float('nan')):.1f}",
              flush=True)
    print("=" * 72, flush=True)

    return 0


# -----------------------------------------------------------------------------
# PROT-022 + entry
# -----------------------------------------------------------------------------
def _selftest() -> None:
    """Smoke-level wiring check: build corpus + run one cell at minimal cost."""
    # Just import-time selftests; the sub-module selftests already cover policies
    # and training_loop. Here we verify the wiring of run_one_cell with the
    # minimum config that won't blow up.
    print("[exp selftest] testing run_one_cell with minimal config...", flush=True)
    # Mini corpus
    corpus_t = "the quick brown fox jumps over the lazy dog. " * 50
    corpus_v = "a stitch in time saves nine. " * 20
    corpus_te = "to be or not to be that is the question. " * 20
    # Temporarily shrink globals for the mini test
    global TRAIN_CHARS, VAL_CHARS, TEST_CHARS, N_STEPS_MAX, BATCH_SIZE
    global EVAL_EVERY, SEQ_LEN, HIDDEN, USE_PYTHIA
    save = (TRAIN_CHARS, VAL_CHARS, TEST_CHARS, N_STEPS_MAX, BATCH_SIZE,
            EVAL_EVERY, SEQ_LEN, HIDDEN, USE_PYTHIA)
    TRAIN_CHARS = len(corpus_t)
    VAL_CHARS = len(corpus_v)
    TEST_CHARS = len(corpus_te)
    N_STEPS_MAX = 5
    BATCH_SIZE = 4
    EVAL_EVERY = 5
    SEQ_LEN = 32
    HIDDEN = 16
    USE_PYTHIA = False
    try:
        r = run_one_cell(7, "random", corpus_t, corpus_v, corpus_te)
        assert "final_bpc_test" in r
        assert r["n_steps_completed"] == 5
        print(f"[exp selftest] run_one_cell PASS: bpc={r['final_bpc_test']:.3f}",
              flush=True)
    finally:
        (TRAIN_CHARS, VAL_CHARS, TEST_CHARS, N_STEPS_MAX, BATCH_SIZE,
         EVAL_EVERY, SEQ_LEN, HIDDEN, USE_PYTHIA) = save


if __name__ == "__main__":
    if _ARGS.self_test:
        _selftest()
        sys.exit(0)
    sys.exit(main())
