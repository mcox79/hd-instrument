"""
tier2_substrate_preloaded_icl_pythia410m_v1 -- Probe 2 (Wave 1).

SCIENTIFIC QUESTION:
  Can K=10 few-shot examples be PRE-LOADED into a substrate W (Hebbian write,
  once) and then retrieved at inference time via residual-stream injection,
  achieving accuracy comparable to standard K-shot ICL while using <10% of the
  context-token budget and >=50x less per-learning-instance wall time?

DESIGN (per-task-SHARED substrate; routing-intent correction 2026-06-03):
  Per task in {analogy, arithmetic, sentiment}, per seed in SEEDS:
    Generate a FIXED set of K demos ONCE (deterministic from seed + task_type
    via the seeded task generator, taking demos from problem 0).  Generate
    task_n queries by iterating problems[0..task_n-1] and taking only their
    (query, answer) -- ignoring per-problem demos in conditions (i) and (ii).
    Three conditions:
      (i)   Standard ICL:        SHARED K demos + query in prompt (every q).
      (ii)  Substrate-loaded:    SHARED K demos Hebbian-written to W ONCE per
                                 (seed, task_type); only query in prompt; for
                                 each query call injector.set_query(xi_q) and
                                 reuse the SAME W.  Substrate retrieval is
                                 injected at layer round(0.7 * num_layers) via
                                 forward hook (alpha=0.1).
      (iii) Zero-shot:           only query in prompt.

  ROUTING INTENT (the bug this corrects, 2026-06-03):
    Prior implementation rebuilt W per-problem (200x Hebbian-writes per task),
    defeating persistent-memory claim and making the HP gate
    "wall_per_learning_instance >= 50x faster" structurally unreachable.  Fix:
    Hebbian-write ONCE per (seed, task_type); amortize setup over task_n
    queries.  Standard ICL uses the SAME shared demos to isolate the
    substrate-vs-in-context variable cleanly.

  Metrics per (seed, task_type, condition):
    accuracy (fraction of queries answered correctly)
    mean_tokens_in (mean prompt token count)
    total_wall_query_s (sum of per-query wall times)
    setup_wall_s (Hebbian-write wall; >0 only for condition (ii); paid ONCE)
    learning_instance_wall_s = (setup + total_wall_query) / task_n
       -- amortized per query.  For condition (ii) setup is paid once and
          divided over task_n; for (i)/(iii) setup_wall_s=0.

PRE-REGISTERED BANDS (per dossier section 1 Probe 2 + integration checklist):
  HARD-PASS: acc_substrate_loaded >= acc_standard_icl - 0.05  AND
             mean_tokens_substrate / mean_tokens_standard <= 0.10  AND
             learning_instance_wall_speedup_standard_vs_substrate >= 50
  HARD-FAIL: acc_substrate_loaded < acc_zero_shot
  MIDDLE:    everything else

SMOKE MODE (HDLAB_RUN_MODE=smoke):
  Uses a HeuristicMockLM (no real LLM weights downloaded) which:
   - Tokenizes prompts with HF Pythia tokenizer (real token counts) IF available;
     else a deterministic whitespace tokenizer.
   - Emits an answer string via a deterministic heuristic.
   - The SubstrateInjector hook, when present + has a current retrieval,
     biases the heuristic's answer toward retrieved demo content, so condition
     (ii) is MEASURABLY different from condition (iii).
   This validates plumbing: tokenization counts, hook attach/detach, metric
   computation, partial-checkpoint write/read.

FULL MODE (HDLAB_RUN_MODE=full):
  Loads EleutherAI/pythia-410m (24 layers, hidden_size=1024).  Substrate
  N=1024 matches hidden_size so injection projection is identity.  Hook
  attaches to model.gpt_neox.layers[17] (round(0.7 * 24) = 17).  Greedy
  decoding for the answer token(s).

PROT-018: anchor name `tier2_substrate_preloaded_icl_pythia410m_v1` has no
`_nN` suffix because N is fixed to model hidden_size (1024 for Pythia-410M),
not a swept parameter.

ASCII-only stdout per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)
from testbed.llm_integration.substrate_audit import hebbian_write  # noqa: E402
from testbed.icl.tasks import (  # noqa: E402
    generate_analogy_problems,
    generate_arithmetic_problems,
    generate_sentiment_problems,
)
from testbed.icl.encoder import encode_text_bipolar, encode_pair_bipolar  # noqa: E402
from testbed.icl.substrate_inject import SubstrateInjector  # noqa: E402


ANCHOR_NAME = "tier2_substrate_preloaded_icl_pythia410m_v1"

# Pre-reg thresholds
HP_ACC_GAP = 0.05       # acc_substrate >= acc_standard - 0.05
HP_TOK_RATIO = 0.10     # tokens_substrate / tokens_standard <= 0.10
HP_SPEEDUP = 50.0       # wall_per_learning_instance speedup >= 50x

MID_ACC_GAP = 0.10
MID_TOK_RATIO_HI = 0.30
MID_SPEEDUP = 10.0

# Mode-dependent config
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]
TASK_N_FULL = 200
TASK_N_SMOKE = 20
K_DEMOS_FULL = 10
K_DEMOS_SMOKE = 4
N_SUBSTRATE = 1024       # matches Pythia-410M hidden_size
ALPHA_INJECT = 0.1
LAYER_FRAC = 0.7         # inject at round(0.7 * num_layers)
MODEL_NAME_FULL = "EleutherAI/pythia-410m"

TASK_GENERATORS = [
    ("analogy", generate_analogy_problems),
    ("arithmetic", generate_arithmetic_problems),
    ("sentiment", generate_sentiment_problems),
]


# -----------------------------------------------------------------------------
# Whitespace tokenizer fallback (used when HF Pythia tokenizer is unavailable)
# -----------------------------------------------------------------------------
class _WhitespaceTokenizer:
    """Deterministic whitespace tokenizer for smoke fallback."""
    def __init__(self):
        self.vocab: Dict[str, int] = {}

    def count_tokens(self, text: str) -> int:
        return len(text.split())


# -----------------------------------------------------------------------------
# HeuristicMockLM (smoke)
# -----------------------------------------------------------------------------
class _MockLayer:
    """Stand-in for an HF transformer layer in smoke mode.

    Exposes register_forward_hook so SubstrateInjector can attach.  The mock
    layer's `forward` returns a zero hidden state; the hook adds the
    retrieval, and the wrapping HeuristicMockLM reads back what the layer
    produced to bias its heuristic decision.
    """
    def __init__(self, d_model: int):
        self.d_model = d_model
        self._h_fn = None
        self.last_hidden: Optional[np.ndarray] = None

    def register_forward_hook(self, fn):
        self._h_fn = fn
        outer = self
        class _Handle:
            def remove(self_h):
                outer._h_fn = None
        return _Handle()

    def forward(self) -> np.ndarray:
        """Return a zero hidden state, then let the hook modify it."""
        h = np.zeros((1, self.d_model), dtype=np.float32)
        if self._h_fn is not None:
            out = self._h_fn(self, None, h)
            if isinstance(out, tuple):
                out = out[0]
            return out
        return h


class HeuristicMockLM:
    """Deterministic mock language model for smoke validation.

    Behavior:
      - count_tokens(text): whitespace token count (real counts when HF tokenizer
        is available; else whitespace fallback).
      - answer(prompt, demos, problem, with_substrate): emits an answer string
        via a heuristic that:
          (a) If with_substrate is True AND the substrate-injection hook has a
              non-zero current retrieval: use the FIRST demo's output as the
              answer if any.  (This simulates "I have access to demo content
              via substrate".)
          (b) Else if `demos` is non-empty in-prompt (len(demos)>0): use the
              FIRST demo's output as the answer.
          (c) Else: emit a deterministic fallback ("the", "0", "happy" by task).

    For demos=[] but with_substrate=True, behaviour (a) fires (substrate has
    content).  For demos=[] and with_substrate=False, behaviour (c) fires
    (zero-shot lower bound).
    """
    def __init__(self, d_model: int = 1024, num_layers: int = 24,
                 tokenizer=None):
        self.d_model = d_model
        self.num_layers = num_layers
        self.layers = [_MockLayer(d_model) for _ in range(num_layers)]
        self._tokenizer = tokenizer  # may be None for whitespace fallback
        self._ws = _WhitespaceTokenizer()
        self.injector: Optional[SubstrateInjector] = None  # set externally

    def count_tokens(self, text: str) -> int:
        if self._tokenizer is not None:
            try:
                return len(self._tokenizer.encode(text))
            except Exception:
                pass
        return self._ws.count_tokens(text)

    def answer(self, prompt: str, demos: List[Tuple[str, str]],
               problem: Dict[str, Any], with_substrate: bool) -> str:
        """Emit a heuristic answer."""
        # Fire the (mock) layer forward to give the SubstrateInjector hook a
        # chance to run.  This validates hook plumbing in smoke.
        layer_idx = int(round(LAYER_FRAC * self.num_layers))
        layer_idx = max(0, min(layer_idx, self.num_layers - 1))
        target_layer = self.layers[layer_idx]
        _ = target_layer.forward()
        hook_fired = (self.injector is not None and self.injector.n_fires > 0
                      and with_substrate)

        # Substrate path: simulate retrieving the joint (in, out) of a relevant demo
        if with_substrate and self.injector is not None \
                and self.injector._retrieval_np is not None:
            # Use the substrate's "stored" demos: we passed them in as `demos`
            # but in condition (ii) the prompt won't contain them.  We have
            # them available through self._substrate_demos which gets set
            # by the experiment driver before each query.
            store = getattr(self, "_substrate_demos", None)
            if store and len(store) > 0:
                return store[0][1].strip()

        # In-prompt demos path
        if len(demos) > 0:
            return demos[0][1].strip()

        # Zero-shot fallback (deterministic dummy answer per task)
        tt = problem.get("task_type", "")
        if tt == "analogy":
            return "thing"
        if tt == "arithmetic":
            return "0"
        if tt == "sentiment":
            return "happy"
        return "unknown"

    def set_substrate_demos(self, demos: List[Tuple[str, str]]) -> None:
        """Smoke-only: stash the substrate-loaded demos so the heuristic can
        simulate retrieving them when the hook is active."""
        self._substrate_demos = list(demos)

    def clear_substrate_demos(self) -> None:
        self._substrate_demos = []


# -----------------------------------------------------------------------------
# Real Pythia-410M wrapper (FULL mode)
# -----------------------------------------------------------------------------
class _PythiaWrapper:
    """Thin wrapper around HF Pythia-410M for greedy single-answer generation.

    Provides the same surface as HeuristicMockLM:
      count_tokens(text), answer(prompt, demos, problem, with_substrate)
    """
    def __init__(self, model_name: str = MODEL_NAME_FULL, device: Optional[str] = None):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()

        self.num_layers = self.model.config.num_hidden_layers
        self.d_model = self.model.config.hidden_size
        # Expose layer list at .layers for SubstrateInjector attach
        self.layers = self.model.gpt_neox.layers
        self.injector: Optional[SubstrateInjector] = None

    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def answer(self, prompt: str, demos, problem, with_substrate: bool) -> str:
        import torch
        # Encode and generate up to 8 tokens; take first non-whitespace token
        enc = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        max_new = 8
        with torch.no_grad():
            out = self.model.generate(
                **enc, max_new_tokens=max_new, do_sample=False,
                pad_token_id=self.tokenizer.pad_token_id,
            )
        gen_tokens = out[0, enc["input_ids"].shape[1]:]
        text = self.tokenizer.decode(gen_tokens, skip_special_tokens=True)
        # Trim: take first word/number-like token sequence
        text = text.strip()
        m = re.match(r"[A-Za-z0-9\-]+", text)
        if m:
            return m.group(0)
        return text

    def set_substrate_demos(self, demos):
        # Not needed for real model -- the substrate hook does the work
        pass

    def clear_substrate_demos(self):
        pass


# -----------------------------------------------------------------------------
# Build the three prompts for a given problem
# -----------------------------------------------------------------------------
def build_prompt(problem: Dict[str, Any], condition: str,
                 shared_demos: Optional[List[Tuple[str, str]]] = None
                 ) -> Tuple[str, List[Tuple[str, str]]]:
    """Return (prompt_text, demos_in_prompt) for the given condition.

    Conditions:
      "standard"  : SHARED K demos + query (shared_demos required)
      "substrate" : query only (demos go into substrate, not prompt)
      "zero_shot" : query only

    NOTE (per-task-shared fix, 2026-06-03): standard ICL now uses the SAME K
    shared demos across all 200 queries within (seed, task_type) so the only
    variable distinguishing (i) vs (ii) is in-context-vs-substrate delivery of
    the SAME demos.
    """
    if condition == "standard":
        demos = shared_demos if shared_demos is not None else list(problem["demos"])
        parts = []
        for d_in, d_out in demos:
            parts.append(f"{d_in} {d_out}")
        parts.append(problem["query"])
        return ("\n".join(parts), list(demos))
    elif condition in ("substrate", "zero_shot"):
        return (problem["query"], [])
    else:
        raise ValueError(f"unknown condition {condition}")


# -----------------------------------------------------------------------------
# Match predictions
# -----------------------------------------------------------------------------
def _match(pred: str, gold: str) -> bool:
    """Case-insensitive whitespace-trimmed exact match on first token."""
    if pred is None or gold is None:
        return False
    p = pred.strip().split()
    g = gold.strip().split()
    if not p or not g:
        return False
    return p[0].lower() == g[0].lower()


# -----------------------------------------------------------------------------
# Single (seed, task_type) run
# -----------------------------------------------------------------------------
def run_one_seed_task(seed: int, task_type: str, task_n: int, k_demos: int,
                     lm, run_mode: str) -> Dict[str, Any]:
    """Run all 3 conditions on task_n problems with a PER-TASK SHARED substrate.

    Per-task-shared substrate (routing-intent correction 2026-06-03):
      - One fixed set of K demos is extracted from problem 0 of the seeded
        generator (deterministic) and SHARED across all task_n queries.
      - Hebbian-write happens ONCE per (seed, task_type) -- not per problem.
      - Condition (i) standard ICL uses the SAME shared K demos to isolate
        the in-context-vs-substrate delivery variable.
      - For each of the task_n queries, condition (ii) only calls
        injector.set_query(xi_q) and reuses the same W.

    Returns per-condition metrics including setup_wall_s (paid once for
    substrate) and learning_instance_wall_s = (setup + total_wall_query) /
    task_n.
    """
    # Generate problems (deterministic from seed + task_type)
    gens = dict(TASK_GENERATORS)
    gen_fn = gens[task_type]
    problems = gen_fn(task_n, seed=seed, k_demos=k_demos)
    assert len(problems) == task_n

    # SHARED K demos: take problem 0's demos (deterministic from seed).
    # Used for BOTH condition (i) standard ICL and condition (ii) substrate.
    shared_demos: List[Tuple[str, str]] = list(problems[0]["demos"])
    assert len(shared_demos) == k_demos, (
        f"shared_demos len={len(shared_demos)} != k_demos={k_demos}")

    results: Dict[str, Dict[str, Any]] = {}

    # ---- Condition (i): Standard ICL (shared K demos in prompt) ----
    n_correct = 0
    tokens_sum = 0
    wall_q_sum = 0.0
    for prob in problems:
        prompt, demos_in_prompt = build_prompt(prob, "standard",
                                               shared_demos=shared_demos)
        t_q = time.perf_counter()
        pred = lm.answer(prompt, demos_in_prompt, prob, with_substrate=False)
        wall_q_sum += (time.perf_counter() - t_q)
        tokens_sum += lm.count_tokens(prompt)
        if _match(pred, prob["answer"]):
            n_correct += 1
    results["standard"] = {
        "accuracy": n_correct / task_n,
        "mean_tokens": tokens_sum / task_n,
        "total_wall_query_s": wall_q_sum,
        "setup_wall_s": 0.0,
        "learning_instance_wall_s": wall_q_sum / task_n,
    }

    # ---- Condition (ii): Substrate-loaded ICL (W built ONCE) ----
    # Setup: Hebbian-write the K SHARED demos into W ONCE for this
    # (seed, task_type).  Then iterate task_n queries against the same W.
    layer_idx = int(round(LAYER_FRAC * lm.num_layers))
    layer_idx = max(0, min(layer_idx, lm.num_layers - 1))
    target_layer = lm.layers[layer_idx]

    t_setup = time.perf_counter()
    W = np.zeros((N_SUBSTRATE, N_SUBSTRATE), dtype=np.float32)
    for d_in, d_out in shared_demos:
        xi = encode_pair_bipolar(d_in, d_out, N=N_SUBSTRATE, proj_seed=1729)
        W = hebbian_write(W, xi, decay=0.0)
    setup_wall_s = time.perf_counter() - t_setup
    print(f"  task={task_type} seed={seed}: setup W with K={k_demos} demos "
          f"in {setup_wall_s*1000.0:.1f}ms", flush=True)

    # Attach injector ONCE.  Smoke heuristic uses set_substrate_demos to
    # simulate retrieval; real model uses the forward-hook residual injection.
    injector = SubstrateInjector(
        layer=target_layer, W=W, N=N_SUBSTRATE, d_model=lm.d_model,
        alpha=ALPHA_INJECT, proj_seed=2026,
        device=getattr(lm, "device", "cpu"),
    )
    lm.injector = injector
    lm.set_substrate_demos(shared_demos)

    wall_q_sum_sub = 0.0
    tokens_sum_sub = 0
    n_correct_sub = 0
    with injector:
        for prob in problems:
            # Per-query: only update the query vector; W is unchanged.
            xi_q = encode_text_bipolar(prob["query"], N=N_SUBSTRATE, proj_seed=1729)
            injector.set_query(xi_q)
            prompt, demos_in_prompt = build_prompt(prob, "substrate")
            t_q = time.perf_counter()
            pred = lm.answer(prompt, demos_in_prompt, prob, with_substrate=True)
            wall_q_sum_sub += (time.perf_counter() - t_q)
            tokens_sum_sub += lm.count_tokens(prompt)
            if _match(pred, prob["answer"]):
                n_correct_sub += 1

    lm.injector = None
    lm.clear_substrate_demos()

    # Per-learning-instance wall: setup paid ONCE, amortized over task_n queries.
    li_wall_sub = (setup_wall_s + wall_q_sum_sub) / task_n
    results["substrate"] = {
        "accuracy": n_correct_sub / task_n,
        "mean_tokens": tokens_sum_sub / task_n,
        "total_wall_query_s": wall_q_sum_sub,
        "setup_wall_s": setup_wall_s,
        "learning_instance_wall_s": li_wall_sub,
    }

    # ---- Condition (iii): Zero-shot ----
    n_correct_z = 0
    tokens_sum_z = 0
    wall_q_sum_z = 0.0
    for prob in problems:
        prompt, demos_in_prompt = build_prompt(prob, "zero_shot")
        t_q = time.perf_counter()
        pred = lm.answer(prompt, demos_in_prompt, prob, with_substrate=False)
        wall_q_sum_z += (time.perf_counter() - t_q)
        tokens_sum_z += lm.count_tokens(prompt)
        if _match(pred, prob["answer"]):
            n_correct_z += 1
    results["zero_shot"] = {
        "accuracy": n_correct_z / task_n,
        "mean_tokens": tokens_sum_z / task_n,
        "total_wall_query_s": wall_q_sum_z,
        "setup_wall_s": 0.0,
        "learning_instance_wall_s": wall_q_sum_z / task_n,
    }

    return {
        "seed": seed,
        "task_type": task_type,
        "task_n": task_n,
        "k_demos": k_demos,
        "conditions": results,
    }


# -----------------------------------------------------------------------------
# Aggregate across seeds + task_types -> verdict
# -----------------------------------------------------------------------------
def aggregate(per_seed: Dict[str, Dict[str, Any]],
              seeds: List[int]) -> Dict[str, Any]:
    """Combine per-seed (which holds per-task_type) into condition-level means."""
    # Group: per_seed[str(seed)] -> { "<task_type>": {conditions: {...}} }
    by_cond: Dict[str, Dict[str, List[float]]] = {
        "standard": {"accuracy": [], "mean_tokens": [], "learning_instance_wall_s": []},
        "substrate": {"accuracy": [], "mean_tokens": [], "learning_instance_wall_s": []},
        "zero_shot": {"accuracy": [], "mean_tokens": [], "learning_instance_wall_s": []},
    }
    by_task_cond: Dict[str, Dict[str, Dict[str, List[float]]]] = {}

    for s in seeds:
        body = per_seed.get(str(s))
        if not body:
            continue
        per_task = body.get("per_task", {})
        for tt, td in per_task.items():
            by_task_cond.setdefault(tt, {
                "standard": {"accuracy": [], "mean_tokens": [], "learning_instance_wall_s": []},
                "substrate": {"accuracy": [], "mean_tokens": [], "learning_instance_wall_s": []},
                "zero_shot": {"accuracy": [], "mean_tokens": [], "learning_instance_wall_s": []},
            })
            for cond, m in td["conditions"].items():
                for metric in ("accuracy", "mean_tokens", "learning_instance_wall_s"):
                    by_cond[cond][metric].append(float(m[metric]))
                    by_task_cond[tt][cond][metric].append(float(m[metric]))

    def _mean(xs):
        return float(np.mean(xs)) if xs else float("nan")

    means = {
        cond: {metric: _mean(vals) for metric, vals in d.items()}
        for cond, d in by_cond.items()
    }
    per_task_means = {
        tt: {cond: {metric: _mean(vals) for metric, vals in d.items()}
             for cond, d in cond_d.items()}
        for tt, cond_d in by_task_cond.items()
    }

    return {"overall_means": means, "per_task_means": per_task_means}


def classify_verdict(agg: Dict[str, Any]) -> Tuple[str, str]:
    """Apply pre-registered bands."""
    m = agg["overall_means"]
    acc_std = m["standard"]["accuracy"]
    acc_sub = m["substrate"]["accuracy"]
    acc_zs = m["zero_shot"]["accuracy"]
    tok_std = m["standard"]["mean_tokens"]
    tok_sub = m["substrate"]["mean_tokens"]
    li_std = m["standard"]["learning_instance_wall_s"]
    li_sub = m["substrate"]["learning_instance_wall_s"]

    # Tokens ratio
    tok_ratio = (tok_sub / tok_std) if tok_std > 0 else float("inf")
    # Speedup: substrate is faster per-learning-instance if li_sub < li_std
    speedup = (li_std / li_sub) if li_sub > 1e-12 else float("inf")
    # Accuracy gap (positive = substrate beats standard)
    acc_gap = acc_sub - acc_std

    # HARD-FAIL: substrate-loaded accuracy below zero-shot (substrate provides no signal)
    if acc_sub < acc_zs:
        verdict = "HARD_FAIL"
        cap_impl = ("Substrate-loaded ICL provides NO measurable signal beyond zero-shot. "
                    "Hebbian-written demos are not retrievable through residual-stream "
                    "injection at this alpha/layer/encoder setting. Capability of "
                    "pre-loading demos via substrate is REFUTED for Pythia-410M.")
    elif (acc_gap >= -HP_ACC_GAP and tok_ratio <= HP_TOK_RATIO
          and speedup >= HP_SPEEDUP):
        verdict = "HARD_PASS"
        cap_impl = ("Substrate-loaded ICL matches standard ICL accuracy "
                    f"(gap={acc_gap:+.3f}) while using {tok_ratio*100:.1f}% of "
                    f"the context tokens and being {speedup:.1f}x faster per "
                    "learning instance. Few-shot demos CAN be pre-loaded into "
                    "substrate once and retrieved per-query without context-window "
                    "overhead. Capability of substrate-as-persistent-ICL-cache "
                    "CONFIRMED for Pythia-410M.")
    elif (acc_gap >= -MID_ACC_GAP
          and (tok_ratio <= MID_TOK_RATIO_HI or speedup >= MID_SPEEDUP)):
        verdict = "MIDDLE"
        cap_impl = ("Substrate-loaded ICL shows partial signal: accuracy gap "
                    f"{acc_gap:+.3f} (need <={HP_ACC_GAP:.2f} for HP), token "
                    f"ratio {tok_ratio:.3f} (HP<={HP_TOK_RATIO:.2f}), speedup "
                    f"{speedup:.1f}x (HP>={HP_SPEEDUP:.0f}x). Substrate IS "
                    "retrievable but not yet competitive with in-context demos; "
                    "rescue paths: tune alpha, choose layer, train projection, "
                    "or richer encoder.")
    else:
        verdict = "MIDDLE"
        cap_impl = ("Substrate-loaded ICL is above zero-shot but well below "
                    "standard-ICL targets on at least one band axis "
                    f"(acc_gap={acc_gap:+.3f}, tok_ratio={tok_ratio:.3f}, "
                    f"speedup={speedup:.1f}x).")

    verdict_msg = (
        f"Probe 2 (substrate-pre-loaded ICL, Pythia-410M):\n"
        f"  acc_standard={acc_std:.3f}  acc_substrate={acc_sub:.3f}  "
        f"acc_zero_shot={acc_zs:.3f}\n"
        f"  tokens_standard={tok_std:.1f}  tokens_substrate={tok_sub:.1f}  "
        f"(ratio={tok_ratio:.3f})\n"
        f"  learning_instance_wall: std={li_std:.6f}s  sub={li_sub:.6f}s  "
        f"(speedup={speedup:.1f}x)\n"
        f"  Verdict: {verdict}\n"
        f"  Capability implication: {cap_impl}"
    )
    return verdict, verdict_msg


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main() -> int:
    run_mode = os.environ.get("HDLAB_RUN_MODE", "smoke").lower()
    smoke = (run_mode == "smoke")

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    if smoke:
        seeds = SEEDS_SMOKE
        task_n = TASK_N_SMOKE
        k_demos = K_DEMOS_SMOKE
        print(f"[{ANCHOR_NAME}] SMOKE mode: seeds={seeds} task_n={task_n} "
              f"K={k_demos}", flush=True)
        # Try to load Pythia tokenizer for realistic token counts; fall back to whitespace
        tokenizer = None
        try:
            from transformers import AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME_FULL)
            print("  Using Pythia tokenizer for token counts", flush=True)
        except Exception as e:
            print(f"  Tokenizer load failed ({type(e).__name__}); whitespace fallback",
                  flush=True)
        lm = HeuristicMockLM(d_model=N_SUBSTRATE, num_layers=24, tokenizer=tokenizer)
    else:
        seeds = SEEDS_FULL
        task_n = TASK_N_FULL
        k_demos = K_DEMOS_FULL
        print(f"[{ANCHOR_NAME}] FULL mode: seeds={seeds} task_n={task_n} "
              f"K={k_demos}", flush=True)
        lm = _PythiaWrapper(MODEL_NAME_FULL)
        print(f"  Pythia loaded: num_layers={lm.num_layers} d_model={lm.d_model} "
              f"device={lm.device}", flush=True)

    run_config = {"N": N_SUBSTRATE, "run_mode": run_mode}
    done, remaining = resumable_seeds(seeds, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(seeds)} seeds done; running {remaining}",
          flush=True)

    t0 = time.time()
    for seed in remaining:
        per_task: Dict[str, Any] = {}
        for tt, _gen in TASK_GENERATORS:
            t_tt = time.time()
            res = run_one_seed_task(seed, tt, task_n=task_n, k_demos=k_demos,
                                    lm=lm, run_mode=run_mode)
            per_task[tt] = res
            elapsed_tt = time.time() - t_tt
            c = res["conditions"]
            print(f"  seed={seed} task={tt:<11s} "
                  f"acc_std={c['standard']['accuracy']:.3f} "
                  f"acc_sub={c['substrate']['accuracy']:.3f} "
                  f"acc_zs={c['zero_shot']['accuracy']:.3f}  "
                  f"tok_std={c['standard']['mean_tokens']:.1f} "
                  f"tok_sub={c['substrate']['mean_tokens']:.1f}  "
                  f"({elapsed_tt:.1f}s)", flush=True)
        payload = {
            "seed": seed,
            "N": N_SUBSTRATE,
            "run_mode": run_mode,
            "task_n": task_n,
            "k_demos": k_demos,
            "per_task": per_task,
        }
        write_partial(out_dir, seed, payload)

    per_seed = aggregate_partials(out_dir, seeds, run_config=run_config)
    agg = aggregate(per_seed, seeds)
    verdict, verdict_msg = classify_verdict(agg)
    total_elapsed = time.time() - t0

    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": run_mode,
        "smoke": smoke,
        "N": N_SUBSTRATE,
        "alpha_inject": ALPHA_INJECT,
        "layer_frac": LAYER_FRAC,
        "task_n": task_n,
        "k_demos": k_demos,
        "n_seeds": len(seeds),
        "seeds": seeds,
        "overall_means": agg["overall_means"],
        "per_task_means": agg["per_task_means"],
        "thresholds": {
            "HP_acc_gap": HP_ACC_GAP,
            "HP_tok_ratio": HP_TOK_RATIO,
            "HP_speedup": HP_SPEEDUP,
            "MID_acc_gap": MID_ACC_GAP,
            "MID_tok_ratio_hi": MID_TOK_RATIO_HI,
            "MID_speedup": MID_SPEEDUP,
        },
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": total_elapsed,
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print("", flush=True)
    print(verdict_msg, flush=True)
    print("", flush=True)
    print(f"[{ANCHOR_NAME}] verdict={verdict} elapsed={total_elapsed:.1f}s",
          flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {out_dir / 'metrics.json'}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
