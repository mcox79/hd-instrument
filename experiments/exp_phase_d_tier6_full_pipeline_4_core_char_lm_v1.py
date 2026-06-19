"""phase_d_tier6_full_pipeline_4_core_char_lm_v1
   -- Probe 11+ FULL-PIPELINE 4-CORE substrate-native char-LM.

CAPABILITY QUESTION:
  Can a 4-layer character-LM be trained ENTIRELY via the substrate 4-primitive
  core (outer-product Hopfield write + anti-Hebbian bipartite contrastive +
  hierarchical recurrent retrieval + stacked-independent-W composition),
  achieving useful BPC on Wikitext-2 with NO gradient descent at any layer?

PRE-REGISTERED BANDS (per dossier section 2 Probe 11+):
  HARD-PASS: bpc_substrate <= 2.0 * bpc_baseline
             AND train_wall_s <= 0.5 * baseline_train_wall_s
             AND all 4 primitives operational across all seeds (no collapse)
  MIDDLE:    bpc_substrate in (2.0, 4.0] * bpc_baseline
  HARD-FAIL: bpc_substrate > 4.0 * bpc_baseline
             OR any primitive collapse on any seed

P_deflated: 0.38 (Drill 4)

ANCHOR NAME (PROT-018):  phase_d_tier6_full_pipeline_4_core_char_lm_v1
  (no _n<N> suffix; N is run_config, not name).

PROT-021 checkpoint key includes (N, n_layers, corpus_chars) so smoke partials
cannot leak into FULL runs.
"""
from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import os
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (  # noqa: E402
    aggregate_partials,
    get_output_dir,
    resumable_seeds,
    write_partial_key,
)
from testbed.substrate_lm.char_lm import SubstrateCharLM  # noqa: E402
from testbed.substrate_lm.baseline_gradient_lm import GradientCharLM  # noqa: E402
from testbed.substrate_lm.data import (  # noqa: E402
    wikitext2_char_corpus,
    char_vocab_from_corpus,
)

ANCHOR_NAME = "phase_d_tier6_full_pipeline_4_core_char_lm_v1"

# Pre-reg bands
HP_BPC_RATIO = 2.0
HP_WALL_RATIO = 0.5
HF_BPC_RATIO = 4.0
# MIDDLE = (HP_BPC_RATIO, HF_BPC_RATIO]

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]


def _smoke_config() -> dict:
    return dict(
        corpus_chars=10_000,
        n_layers=2,
        N=512,
        alpha_max=0.10,
        n_steps_per_layer=3,
        seeds=SEEDS_SMOKE,
        # Baseline GRU: keep VERY small so it trains FAST (~half substrate time)
        baseline_hidden=32,
        baseline_seq_len=32,
        baseline_batch=16,
        baseline_lr=5e-3,
        baseline_n_layers=2,
    )


def _full_config() -> dict:
    return dict(
        corpus_chars=10_000_000,
        n_layers=4,
        N=2048,
        alpha_max=0.10,
        n_steps_per_layer=3,
        seeds=SEEDS_FULL,
        # Baseline GRU at FULL scale: still tiny (HP-band reference, not competitive)
        baseline_hidden=64,
        baseline_seq_len=64,
        baseline_batch=32,
        baseline_lr=5e-3,
        baseline_n_layers=4,
    )


# ---------------------------------------------------------------------------
# Per-seed runner
# ---------------------------------------------------------------------------

def _run_one_seed(seed: int, cfg: dict, train_text: str, test_text: str,
                  vocab: set) -> dict:
    """Train substrate + baseline on the SAME corpus, score both. Returns metrics."""
    t_seed0 = time.time()
    print(f"[seed {seed}] starting; corpus={len(train_text)} test={len(test_text)} "
          f"vocab={len(vocab)}", flush=True)

    # ---- Substrate LM ----
    print(f"[seed {seed}] training SubstrateCharLM ...", flush=True)
    sub_lm = SubstrateCharLM(
        n_layers=cfg["n_layers"],
        N=cfg["N"],
        alpha_max=cfg["alpha_max"],
        n_steps_per_layer=cfg["n_steps_per_layer"],
        seed=seed,
    )
    sub_fit = sub_lm.fit(
        train_text,
        n_chars_train=cfg["corpus_chars"],
        char_vocab=vocab,
        health_every=max(500, cfg["corpus_chars"] // 50),
        verbose=False,
    )
    sub_score = sub_lm.score_bpc(test_text)
    sub_health = sub_lm.primitive_health()

    # ---- Baseline (gradient) ----
    print(f"[seed {seed}] training GradientCharLM ...", flush=True)
    grad_lm = GradientCharLM(
        n_layers=cfg["baseline_n_layers"],
        hidden=cfg["baseline_hidden"],
        seq_len=cfg["baseline_seq_len"],
        batch_size=cfg["baseline_batch"],
        lr=cfg["baseline_lr"],
        seed=seed,
    )
    grad_fit = grad_lm.fit(train_text, n_chars_train=cfg["corpus_chars"],
                           char_vocab=vocab, max_epochs=1, verbose=False)
    grad_score = grad_lm.score_bpc(test_text)

    seed_wall = time.time() - t_seed0
    result = {
        "seed": seed,
        "N": cfg["N"],
        "n_layers": cfg["n_layers"],
        "corpus_chars": cfg["corpus_chars"],
        "run_mode": cfg.get("run_mode", "smoke"),
        "vocab_size": len(vocab),
        # Substrate
        "substrate": {
            "train_wall_s": sub_fit["train_wall_s"],
            "n_train_pairs": sub_fit["n_train_pairs"],
            "n_pos_pairs": sub_fit["n_pos_pairs"],
            "n_neg_pairs": sub_fit["n_neg_pairs"],
            "final_alphas": sub_fit["final_alphas"],
            "any_primitive_collapse": sub_fit["any_primitive_collapse"],
            "bpc": sub_score["bpc"],
            "n_scored": sub_score["n_scored"],
            "uniform_bpc": sub_score["uniform_bpc"],
            "max_alpha": float(max(sub_fit["final_alphas"])) if sub_fit["final_alphas"] else 0.0,
            "health_per_layer": sub_health["per_layer"],
        },
        # Baseline
        "baseline": {
            "train_wall_s": grad_fit["train_wall_s"],
            "n_steps": grad_fit["n_steps"],
            "final_loss": grad_fit["final_loss"],
            "bpc": grad_score["bpc"],
            "n_scored": grad_score["n_scored"],
            "uniform_bpc": grad_score["uniform_bpc"],
        },
        "seed_wall_s": float(seed_wall),
    }
    print(
        f"[seed {seed}] DONE in {seed_wall:.1f}s | "
        f"substrate bpc={sub_score['bpc']:.3f} wall={sub_fit['train_wall_s']:.2f}s "
        f"alpha_max={max(sub_fit['final_alphas']):.3f} "
        f"collapse={sub_fit['any_primitive_collapse']} | "
        f"baseline bpc={grad_score['bpc']:.3f} wall={grad_fit['train_wall_s']:.2f}s",
        flush=True,
    )
    return result


# ---------------------------------------------------------------------------
# Smoke end-to-end self-test (called at module import)
# ---------------------------------------------------------------------------

def _selftest_end_to_end() -> None:
    """Tiny 2-seed mini-pipeline at N=128 -- runs at import time, fast."""
    rng_corpus = wikitext2_char_corpus(split="train", max_chars=1500)
    rng_test = wikitext2_char_corpus(split="validation", max_chars=300)
    vocab = set(rng_corpus) | set(rng_test)
    cfg = dict(
        n_layers=2, N=128, alpha_max=0.10, n_steps_per_layer=3, corpus_chars=1500,
        baseline_hidden=16, baseline_seq_len=16, baseline_batch=8, baseline_lr=5e-3,
        baseline_n_layers=2, run_mode="smoke",
    )
    for seed in [7, 17]:
        r = _run_one_seed(seed, cfg, rng_corpus, rng_test, vocab)
        assert np.isfinite(r["substrate"]["bpc"]), "substrate BPC non-finite in selftest"
        assert np.isfinite(r["baseline"]["bpc"]), "baseline BPC non-finite in selftest"
        assert not r["substrate"]["any_primitive_collapse"], "selftest collapsed"
    print("[exp selftest] PASS: 2-seed end-to-end mini-pipeline at N=128", flush=True)


# ---------------------------------------------------------------------------
# Verdict classification
# ---------------------------------------------------------------------------

def _classify(per_seed: Dict[str, dict]) -> dict:
    """Aggregate per-seed metrics and apply HP/MIDDLE/HF bands."""
    if not per_seed:
        return {"verdict": "INFRA_FAILURE", "reason": "no seeds completed"}

    sub_bpcs = [s["substrate"]["bpc"] for s in per_seed.values()]
    base_bpcs = [s["baseline"]["bpc"] for s in per_seed.values()]
    sub_walls = [s["substrate"]["train_wall_s"] for s in per_seed.values()]
    base_walls = [s["baseline"]["train_wall_s"] for s in per_seed.values()]
    collapses = [s["substrate"]["any_primitive_collapse"] for s in per_seed.values()]

    sub_bpc_mean = float(np.mean(sub_bpcs))
    sub_bpc_std = float(np.std(sub_bpcs, ddof=1)) if len(sub_bpcs) > 1 else 0.0
    base_bpc_mean = float(np.mean(base_bpcs))
    base_bpc_std = float(np.std(base_bpcs, ddof=1)) if len(base_bpcs) > 1 else 0.0
    sub_wall_mean = float(np.mean(sub_walls))
    base_wall_mean = float(np.mean(base_walls))
    bpc_ratio = sub_bpc_mean / max(base_bpc_mean, 1e-9)
    wall_ratio = sub_wall_mean / max(base_wall_mean, 1e-9)
    any_collapse = any(collapses)

    # HARD-FAIL conditions take priority.
    if bpc_ratio > HF_BPC_RATIO or any_collapse:
        verdict = "HARD_FAIL"
        reason = []
        if bpc_ratio > HF_BPC_RATIO:
            reason.append(f"bpc_ratio={bpc_ratio:.2f} > {HF_BPC_RATIO}")
        if any_collapse:
            reason.append(f"primitive collapse in {sum(collapses)}/{len(collapses)} seeds")
        reason_str = "; ".join(reason)
    elif bpc_ratio <= HP_BPC_RATIO and wall_ratio <= HP_WALL_RATIO and not any_collapse:
        verdict = "HARD_PASS"
        reason_str = (
            f"bpc_ratio={bpc_ratio:.2f}<=2.0, wall_ratio={wall_ratio:.2f}<=0.5, "
            f"no collapse across {len(collapses)} seeds"
        )
    else:
        verdict = "MIDDLE_BAND"
        if bpc_ratio <= HP_BPC_RATIO and wall_ratio > HP_WALL_RATIO:
            reason_str = (
                f"bpc_ratio={bpc_ratio:.2f}<=2.0 but wall_ratio={wall_ratio:.2f}>0.5"
            )
        else:
            reason_str = (
                f"bpc_ratio={bpc_ratio:.2f} in (2.0, 4.0]; wall_ratio={wall_ratio:.2f}"
            )

    return {
        "verdict": verdict,
        "reason": reason_str,
        "sub_bpc_mean": sub_bpc_mean,
        "sub_bpc_std": sub_bpc_std,
        "base_bpc_mean": base_bpc_mean,
        "base_bpc_std": base_bpc_std,
        "bpc_ratio": float(bpc_ratio),
        "sub_wall_mean": sub_wall_mean,
        "base_wall_mean": base_wall_mean,
        "wall_ratio": float(wall_ratio),
        "any_primitive_collapse": bool(any_collapse),
        "n_seeds": len(per_seed),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    run_mode = os.environ.get("HDLAB_RUN_MODE", "smoke").lower()
    cfg = _full_config() if run_mode == "full" else _smoke_config()
    cfg["run_mode"] = run_mode

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    seeds = cfg["seeds"]
    # PROT-021 run_config: N + run_mode keyed (corpus_chars + n_layers also captured
    # in body but the loader only checks N/M/run_mode; we use the compound _ckpt_key
    # to encode all three so smoke partials at different (N, n_layers) can't leak in).
    run_config = {"N": cfg["N"], "run_mode": run_mode}

    print(
        f"[{ANCHOR_NAME}] run_mode={run_mode} N={cfg['N']} "
        f"n_layers={cfg['n_layers']} corpus_chars={cfg['corpus_chars']} "
        f"alpha_max={cfg['alpha_max']} seeds={seeds}",
        flush=True,
    )
    print(
        f"[{ANCHOR_NAME}] pre-reg bands: "
        f"HP bpc_substrate<={HP_BPC_RATIO}x baseline AND "
        f"wall<={HP_WALL_RATIO}x baseline AND no collapse; "
        f"HF bpc_substrate>{HF_BPC_RATIO}x baseline OR any collapse; "
        f"MIDDLE in between",
        flush=True,
    )

    # Load corpora ONCE (shared across seeds; deterministic).
    train_text = wikitext2_char_corpus(split="train", max_chars=cfg["corpus_chars"])
    # Test set is much smaller; cap at min(corpus/20, 50000).
    test_max = min(max(cfg["corpus_chars"] // 20, 1000), 50_000)
    test_text = wikitext2_char_corpus(split="validation", max_chars=test_max)
    vocab = set(train_text) | set(test_text)
    print(
        f"[{ANCHOR_NAME}] corpus loaded: train={len(train_text)} test={len(test_text)} "
        f"vocab={len(vocab)}",
        flush=True,
    )

    # Per-seed checkpoint key: include N, n_layers, corpus_chars per PROT-021 spec.
    def _ckpt_key(seed: int) -> str:
        return f"N{cfg['N']}_L{cfg['n_layers']}_C{cfg['corpus_chars']}_seed{seed}"

    # Resumable: check which compound-key partials are done.
    all_keys = [_ckpt_key(s) for s in seeds]
    done_keys, remaining_keys = resumable_seeds(
        all_keys, out_dir, run_config=run_config
    )
    print(
        f"[ckpt] {len(done_keys)}/{len(all_keys)} seeds already complete; "
        f"running {len(remaining_keys)} remaining",
        flush=True,
    )
    key_to_seed = {_ckpt_key(s): s for s in seeds}

    for key in remaining_keys:
        seed = key_to_seed[key]
        try:
            result = _run_one_seed(seed, cfg, train_text, test_text, vocab)
        except Exception as e:
            print(f"[seed {seed}] FAILED: {type(e).__name__}: {e}", flush=True)
            continue
        # Stamp PROT-021 fields in the payload body.
        payload = dict(result)
        payload["N"] = cfg["N"]
        payload["run_mode"] = run_mode
        write_partial_key(out_dir, key, payload)

    # Aggregate all valid partials.
    agg = aggregate_partials(out_dir, all_keys, run_config=run_config)
    per_seed_clean: Dict[str, dict] = {}
    for key, body in agg.items():
        # Map compound key back to seed for readable summaries.
        seed = key_to_seed.get(key)
        sid = str(seed) if seed is not None else key
        per_seed_clean[sid] = body

    band = _classify(per_seed_clean)
    verdict = band["verdict"]

    # Build verdict_msg with intuitive explanation + capability implication.
    if verdict == "HARD_PASS":
        capability_implication = (
            "Substrate-4-core LM trains end-to-end with NO gradient; opens Phase E "
            "(Pythia-160M-scale substrate-native LM with full 12-primitive surface)."
        )
        plain = (
            f"4-primitive substrate-native char-LM trains: BPC {band['sub_bpc_mean']:.2f} "
            f"vs baseline {band['base_bpc_mean']:.2f} ({band['bpc_ratio']:.2f}x, HP cap 2.0x) "
            f"at wall {band['sub_wall_mean']:.1f}s vs {band['base_wall_mean']:.1f}s baseline "
            f"({band['wall_ratio']:.2f}x, HP cap 0.5x); all primitives operational across "
            f"{band['n_seeds']} seeds. No gradient at any layer."
        )
    elif verdict == "MIDDLE_BAND":
        capability_implication = (
            "Substrate-4-core trains but underperforms gradient baseline; informs "
            "which auxiliary primitives (rank-1 deletion / Sherman-Morrison / kappa3 "
            "fingerprint / counterfactual abduction / etc.) close the gap."
        )
        plain = (
            f"Substrate-4-core BPC {band['sub_bpc_mean']:.2f} vs baseline "
            f"{band['base_bpc_mean']:.2f} ({band['bpc_ratio']:.2f}x); MIDDLE: "
            f"partial training -- {band['reason']}. {band['n_seeds']} seeds."
        )
    elif verdict == "HARD_FAIL":
        capability_implication = (
            "Substrate-4-core does NOT carry the LM loop in its current form. "
            "Pivots to hybrid Hebbian-attention + gradient-head per Drill 3 alt path."
        )
        plain = (
            f"Substrate-4-core BPC {band['sub_bpc_mean']:.2f} vs baseline "
            f"{band['base_bpc_mean']:.2f} ({band['bpc_ratio']:.2f}x); HARD-FAIL: "
            f"{band['reason']}."
        )
    else:
        capability_implication = "Inconclusive; investigate partials."
        plain = f"Verdict {verdict}: {band['reason']}"

    verdict_msg = (
        f"Probe 11+ FULL-PIPELINE 4-CORE substrate-native char-LM: "
        f"{verdict}. {plain} Capability implication: {capability_implication} "
        f"Bands: HP bpc<=2.0x AND wall<=0.5x AND no collapse; "
        f"MID bpc in (2.0, 4.0]; HF bpc>4.0x OR any collapse."
    )

    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": run_mode,
        "config": {
            "N": cfg["N"],
            "n_layers": cfg["n_layers"],
            "alpha_max": cfg["alpha_max"],
            "n_steps_per_layer": cfg["n_steps_per_layer"],
            "corpus_chars": cfg["corpus_chars"],
            "seeds": seeds,
            "baseline_hidden": cfg["baseline_hidden"],
            "baseline_n_layers": cfg["baseline_n_layers"],
        },
        "thresholds": {
            "HP_bpc_ratio": HP_BPC_RATIO,
            "HP_wall_ratio": HP_WALL_RATIO,
            "HF_bpc_ratio": HF_BPC_RATIO,
        },
        "verdict": verdict,
        "band_summary": band,
        "per_seed": per_seed_clean,
        "verdict_msg": verdict_msg,
        "n_seeds_attempted": len(seeds),
        "n_seeds_completed": len(per_seed_clean),
    }
    (out_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, default=str), encoding="utf-8"
    )
    print(f"[{ANCHOR_NAME}] verdict={verdict}", flush=True)
    print(f"[{ANCHOR_NAME}] {verdict_msg}", flush=True)
    return 0 if verdict != "HARD_FAIL" else 1


if __name__ == "__main__":
    # End-to-end smoke selftest BEFORE the real run (so import-time validates code).
    _selftest_end_to_end()
    sys.exit(main())
