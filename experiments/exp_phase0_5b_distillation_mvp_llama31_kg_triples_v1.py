"""
phase0_5b_distillation_mvp_llama31_kg_triples_v1 -- Phase 0.5b empirical capstone.

SCIENTIFIC QUESTION:
  Does Pathway B knowledge-graph distillation deliver the 10^2-10^4x speedup at
  10K-fact production scale, on Llama-3.1-8B, while preserving base capability
  AND supporting one-shot fact addition AND audit primitives?

DESIGN (per research_routing_tier4_training_acceleration_FINAL_5drill_consolidation):
  - Base model: Llama-3.1-8B-Instruct via vLLM.
  - Distillation: knowledge-graph triple extraction via fact-elicitation prompts.
    Each (subject, predicate, object) triple bound via VSA into bipolar pattern
    xi = bind(s, p, o) in {-1,+1}^N.
  - Substrate: N = 8192, alpha = 0.122 (M = 1000 facts; well within alpha_c=0.138
    Hopfield capacity); for MVP we test at M = 1000 with extrapolation gates to
    M = 10000.
  - Hebbian write: W = (1/N) sum xi xi^T.

  Eval suites (per pre-reg):
    (i)   Distilled-fact recall: query each (s, p) -> retrieve, verify o.
    (ii)  Non-distilled-fact degradation: hold 200 base-LLM facts NOT in
          distilled set; check Llama-3.1-8B answers them unchanged.
    (iii) MMLU degradation: 200-question MMLU subset; compare base vs
          substrate-augmented.
    (iv)  One-shot 100-new-fact addition: streaming write 100 fresh facts,
          measure wall-time + retrieval, must be <60s total + recall >= 0.85.
    (v)   Deletion cert on 100-fact subset: rank-1 subtract + cert + retrieval
          confirms erased.

PRE-REGISTERED BANDS (per FINAL 5-drill consolidation):
  HARD-PASS (all five must hold):
    - distilled-fact recall >= 0.85
    - non-distilled-fact degradation <= 0.02
    - MMLU degradation <= 0.02
    - one-shot 100-fact addition: wall <= 60s AND recall >= 0.85
    - deletion cert verifies (deleted < noise floor; retained > 0.85) on 100-subset
  HARD-FAIL (any one trips):
    - distilled recall < 0.65 (worse than RAG baseline)
    - catastrophic interference (>0.05 on non-distilled OR MMLU)
    - deletion cert fails (would refute Drill 5 mechanism-class-separation)
    - audit primitives fail
  MIDDLE: 0.65 <= recall < 0.85 OR degradation in [0.02, 0.05] -- implies
    distillation works but needs hierarchical PP-12 L=3 scaling or whitening.

PROT-018: no _nN suffix -> LLM-native; substrate N=8192 driven by Hopfield
capacity analysis (alpha_c=0.138; M=1000 -> alpha=0.122).

KG-TRIPLE STAGING:
  - smoke mode: synthetic (subject, predicate, object) triples encoded via
    deterministic bipolar bind from string hashes. Substrate primitives fully
    testable. LLM-side eval (i)-(iii) is mocked with a synthetic recall function.
  - full mode: Llama-3.1-8B fact elicitation -> KG extraction -> Hebbian write;
    evaluation via vLLM-batched query/answer scoring against ground-truth o.

This script is substrate-complete in smoke; the LLM-coupled bits surface
as NotImplementedError in full mode until cloud bring-up wires vLLM + the
fact-elicitation/extraction pipeline.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import hashlib
import json
import math
import os
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)
from testbed.llm_integration.substrate_audit import (  # noqa: E402
    build_W_from_patterns, deletion_cert, retrieval_cosine,
    null_distribution_norm, hebbian_write, probe_quality_tag,
)

ANCHOR_NAME = "phase0_5b_distillation_mvp_llama31_kg_triples_v1"

# Substrate sizes (per Drill 4 + capacity analysis).
# CAPACITY-CLIFF NOTE (research sanity-check 2026-06-02): at p=2 dense W,
# alpha_c=0.138 (classical Hopfield). M=1000 at N=8192 -> alpha=0.122 = 88% of
# cliff; r_basin ~ sqrt(1 - alpha/alpha_c) ~ 0.34, degraded from alpha<<alpha_c.
# A HARD-FAIL at M=1000 would conflate capacity-cliff failure with distillation-
# pathway failure. Per research recommendation option (B): reduce to M=500
# (alpha=0.061 = 44% of cliff; r_basin ~ 0.75) until p=4 implicit-storage path is
# wired (waiting on COMBO-1 v3 redesign). All pre-reg bands unchanged.
N_FULL = 8192
N_SMOKE = 1024
M_DISTILLED_FULL = 500
M_DISTILLED_SMOKE = 200

# Eval sizes
N_NONDISTILLED_FULL = 200
N_NONDISTILLED_SMOKE = 40
N_MMLU_FULL = 200
N_MMLU_SMOKE = 40
N_ONESHOT_NEW = 100  # both modes
N_ONESHOT_NEW_SMOKE = 30
N_DELETION_SUBSET = 100
N_DELETION_SUBSET_SMOKE = 30
N_NULL_PROBES = 50

# Pre-reg bands
HP_DISTILLED_RECALL = 0.85
HF_DISTILLED_RECALL = 0.65
HP_DEGRADATION = 0.02
HF_DEGRADATION = 0.05
HP_ONESHOT_WALL_S = 60.0
HP_ONESHOT_RECALL = 0.85
HP_DEL_Z = 2.0
HP_RETAIN_COSINE = 0.85

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]


def _hash_to_bipolar(s: str, N: int) -> np.ndarray:
    """Deterministic bipolar code from a string via SHA-256-driven PRNG."""
    h = hashlib.sha256(s.encode("utf-8")).digest()
    seed_int = int.from_bytes(h[:8], "big")
    rng = np.random.default_rng(seed_int)
    return rng.choice([-1.0, 1.0], size=N).astype(np.float32)


def _vsa_bind(s: np.ndarray, p: np.ndarray, o: np.ndarray) -> np.ndarray:
    """VSA bind via element-wise product (multiplicative MAP/MAP-B)."""
    return (s * p * o).astype(np.float32)


def _synth_kg_triple(seed: int, i: int) -> tuple[str, str, str]:
    """Generate i-th synthetic (s, p, o) triple."""
    s = f"S_{seed}_{i // 5}"          # ~5 facts per subject
    p = f"P_{i % 7}"                  # ~7 predicates
    o = f"O_{seed}_{i}"
    return (s, p, o)


def _build_triple_patterns(M: int, N: int, seed: int) -> tuple[list, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return (triples, Xi_auto, Keys, Values, queries).

    - Xi_auto[i] = s_i * p_i * o_i (auto-associative pattern; used for kappa_3 +
      deletion-cert primitives via the symmetric W_xx = (1/N) Sum xi xi^T).
    - Keys[i] = s_i * p_i (hetero-associative key).
    - Values[i] = o_i (hetero-associative value).
    - queries[i] = Keys[i] (the partial-key probe used at retrieval time).
    """
    triples = []
    Xi_auto = np.zeros((M, N), dtype=np.float32)
    Keys = np.zeros((M, N), dtype=np.float32)
    Values = np.zeros((M, N), dtype=np.float32)
    queries = []
    for i in range(M):
        (s, p, o) = _synth_kg_triple(seed, i)
        triples.append((s, p, o))
        cs = _hash_to_bipolar(s, N)
        cp = _hash_to_bipolar(p, N)
        co = _hash_to_bipolar(o, N)
        Xi_auto[i] = _vsa_bind(cs, cp, co)
        Keys[i] = (cs * cp).astype(np.float32)
        Values[i] = co
        queries.append(Keys[i])
    return triples, Xi_auto, Keys, Values, queries


def _build_W_hetero(Keys: np.ndarray, Values: np.ndarray) -> np.ndarray:
    """Hetero-associative: W = (1/N) Sum Values[k] outer Keys[k] -> shape (N, N).

    Retrieval: W @ key_q = (1/N) Sum (key_k . key_q) value_k.
    For matching k*: (key_k* . key_q) = N -> contributes value_k* with weight 1.
    """
    M, N = Keys.shape
    W = (Values.T.astype(np.float32) @ Keys.astype(np.float32)) / float(N)
    return W


def _eval_distilled_recall(W_kv: np.ndarray, Keys: np.ndarray, Values: np.ndarray,
                            N: int) -> tuple[float, list]:
    """Hetero-associative recall: for each key_i, y = W_kv @ key_i; cosine to value_i.

    For matched k*: W_kv @ key_k* approx value_k* + crosstalk (M-1)/N.
    recall = fraction with cosine > 0.5.
    """
    cos_vals = []
    for i in range(Keys.shape[0]):
        y = W_kv @ Keys[i]
        yn = float(np.linalg.norm(y))
        vn = float(np.linalg.norm(Values[i]))
        cos = float((y @ Values[i]) / (max(yn, 1e-30) * max(vn, 1e-30)))
        cos_vals.append(cos)
    recall = float(np.mean([c > 0.5 for c in cos_vals]))
    return recall, cos_vals


def _eval_nondistilled_degradation(W_kv: np.ndarray, N: int, n_non: int,
                                    seed: int) -> float:
    """Substrate degradation proxy for non-distilled facts.

    In full mode: Llama-3.1-8B answer accuracy on a held-out fact corpus, with
    substrate read-side passive (so should be 0 degradation IF substrate is
    correctly read-side-only).

    In smoke mode: synthesize n_non bipolar 'key' patterns NOT in stored Keys;
    check that ||W_kv @ key|| stays in the null-correlation regime; spurious
    high norms (above noise floor) count as degradation proxy.
    """
    rng = np.random.default_rng(seed * 41 + 17)
    # Reference noise floor: random eta should give ||W_kv @ eta|| approx sqrt(M/N)
    M_ref = max(1, int(W_kv.shape[1]))  # used only as floor scale
    n_spurious = 0
    threshold = 0.5  # any cosine to stored values exceeding this counts as spurious
    for _ in range(n_non):
        eta = rng.choice([-1.0, 1.0], size=N).astype(np.float32)
        y = W_kv @ eta
        yn = float(np.linalg.norm(y))
        if yn > 0.5 * np.sqrt(N):
            # absolute norm too high; substrate is "responding" to non-stored key
            n_spurious += 1
    return float(n_spurious) / max(1, n_non)


def _eval_mmlu_degradation(W_kv: np.ndarray, N: int, n_q: int, seed: int) -> float:
    """Substrate degradation proxy for MMLU.

    In full mode: Llama-3.1-8B MMLU subset accuracy with substrate read-side
    coupled vs base.

    In smoke mode: synthesize n_q reasoning-style query keys (random bipolar);
    check substrate doesn't produce strong value-vector output (norm above
    noise floor) for these unrelated queries.
    """
    rng = np.random.default_rng(seed * 47 + 23)
    n_hallu = 0
    for _ in range(n_q):
        q = rng.choice([-1.0, 1.0], size=N).astype(np.float32)
        y = W_kv @ q
        yn = float(np.linalg.norm(y))
        if yn > 0.75 * np.sqrt(N):
            n_hallu += 1
    return float(n_hallu) / max(1, n_q)


def _eval_oneshot_addition(W_kv: np.ndarray, N: int, n_new: int,
                            seed: int) -> tuple[float, float]:
    """Stream-write n_new new facts to hetero-associative W_kv; return (wall_time, recall)."""
    _, _, Keys_new, Values_new, _ = _build_triple_patterns(n_new, N, seed=seed + 5555)
    t0 = time.time()
    W2 = W_kv.copy()
    for i in range(n_new):
        # Hetero-associative streaming write: W2 += (1/N) * outer(value_i, key_i)
        W2 = W2 + np.outer(Values_new[i], Keys_new[i]).astype(W2.dtype) / float(N)
    wall = time.time() - t0
    recall, _ = _eval_distilled_recall(W2, Keys_new, Values_new, N)
    return wall, recall


def _eval_deletion_subset(W_xx: np.ndarray, Xi_auto: np.ndarray, N: int,
                            n_del: int, seed: int) -> tuple[float, float]:
    """Pick n_del facts; delete on auto-associative W_xx; verify (del_Z, retain_cos_min).

    Uses the symmetric W_xx (Sum xi xi^T / N) for the audit-cert primitive
    because deletion_cert / null_distribution_norm are defined on the symmetric
    form. Distinct from W_kv (hetero) used for retrieval.
    """
    rng_sel = np.random.default_rng(seed * 19 + 3)
    M = Xi_auto.shape[0]
    n_del = min(n_del, M)
    del_idx = rng_sel.choice(M, size=n_del, replace=False).tolist()
    retain_idx = [i for i in range(M) if i not in set(del_idx)]
    W_post = W_xx.copy()
    for idx in del_idx:
        W_post, _, _ = deletion_cert(W_post, Xi_auto[idx])
    rng_null = np.random.default_rng(seed * 53 + 7)
    null_mean, null_std = null_distribution_norm(W_post, N_NULL_PROBES, rng_null)
    del_zs = []
    for idx in del_idx:
        nrm = float(np.linalg.norm(W_post @ Xi_auto[idx]))
        del_zs.append(abs(nrm - null_mean) / max(null_std, 1e-30))
    retain_coss = [retrieval_cosine(W_post, Xi_auto[i]) for i in retain_idx]
    return float(max(del_zs)), float(min(retain_coss) if retain_coss else 1.0)


def _instrumentation_selftest():
    N = 256
    triples, Xi_auto, Keys, Values, queries = _build_triple_patterns(20, N, seed=0)
    W_kv = _build_W_hetero(Keys, Values)
    recall, cos_vals = _eval_distilled_recall(W_kv, Keys, Values, N)
    assert recall > 0.85, f"hetero recall too low: {recall} (cos_vals mean {np.mean(cos_vals):.3f})"
    # Verify deletion-cert primitive still works on the auto-associative W_xx
    W_xx = build_W_from_patterns(Xi_auto)
    W_xx_post, cert, _ = deletion_cert(W_xx, Xi_auto[3])
    assert cert < 0, f"deletion cert should be negative scalar, got {cert}"
    print(f"[selftest] PASS: KG-triple hetero recall = {recall:.3f}; deletion-cert OK",
          flush=True)


_instrumentation_selftest()


def run_one_seed(seed: int, N: int, M: int, n_non: int, n_mmlu: int,
                 n_oneshot: int, n_del: int) -> dict:
    t0 = time.time()
    run_mode = os.environ.get("HDLAB_RUN_MODE", "smoke")
    if run_mode == "full" and os.environ.get("HDLAB_ENCODER", "") != "synthetic":
        # Real LLM-coupled path requires vLLM + Llama-3.1-8B + fact-elicitation
        # pipeline; not implemented in smoke-staged build. Surface clearly.
        raise NotImplementedError(
            "Phase 0.5b full mode requires Llama-3.1-8B fact elicitation pipeline; "
            "set HDLAB_ENCODER=synthetic to run the substrate-side scaffold or "
            "complete the LLM bring-up first (see testbed_phase05_deployment_*.md)."
        )

    triples, Xi_auto, Keys, Values, _ = _build_triple_patterns(M, N, seed=seed)
    # Dual storage per research-sanity-check 2026-06-02: hetero W_kv carries the
    # retrieval load (distilled recall, non-deg, mmlu-deg, oneshot); auto W_xx
    # carries the audit primitives (deletion cert, kappa_3 -- both algebraic on
    # the symmetric form). Diagnostic clarity required: log primitive -> matrix.
    W_kv = _build_W_hetero(Keys, Values)      # for retrieval (hetero)
    W_xx = build_W_from_patterns(Xi_auto)     # for audit primitives (auto-symmetric)

    # Retrieval suite on W_kv
    distilled_recall, _ = _eval_distilled_recall(W_kv, Keys, Values, N)
    non_deg = _eval_nondistilled_degradation(W_kv, N, n_non, seed)
    mmlu_deg = _eval_mmlu_degradation(W_kv, N, n_mmlu, seed)
    oneshot_wall, oneshot_recall = _eval_oneshot_addition(W_kv, N, n_oneshot, seed)
    # Audit suite on W_xx
    del_z_max, retain_cos_min = _eval_deletion_subset(W_xx, Xi_auto, N, n_del, seed)

    elapsed = time.time() - t0
    # Capacity-cliff diagnostic: alpha = M / (N for p=2 dense). Surface so
    # downstream verdict reading can distinguish capacity issue from pathway issue.
    alpha = float(M) / float(N)
    return {
        "seed": seed,
        "N": N, "M": M,
        "alpha": alpha,
        "alpha_c_p2": 0.138,
        "primitive_to_matrix": {
            "distilled_recall": "W_kv",
            "non_distilled_degradation": "W_kv",
            "mmlu_degradation": "W_kv",
            "oneshot_addition": "W_kv",
            "deletion_cert": "W_xx",
        },
        "distilled_recall": distilled_recall,
        "non_distilled_degradation": non_deg,
        "mmlu_degradation": mmlu_deg,
        "oneshot_wall_s": oneshot_wall,
        "oneshot_recall": oneshot_recall,
        "deletion_Z_max": del_z_max,
        "deletion_retained_cosine_min": retain_cos_min,
        "elapsed_s": elapsed,
    }


def classify_verdict(seeds_results: list[dict]) -> tuple[str, str]:
    rec_min = min(r["distilled_recall"] for r in seeds_results)
    non_deg_max = max(r["non_distilled_degradation"] for r in seeds_results)
    mmlu_max = max(r["mmlu_degradation"] for r in seeds_results)
    one_wall_max = max(r["oneshot_wall_s"] for r in seeds_results)
    one_rec_min = min(r["oneshot_recall"] for r in seeds_results)
    del_z_max = max(r["deletion_Z_max"] for r in seeds_results)
    retain_min = min(r["deletion_retained_cosine_min"] for r in seeds_results)

    hp_pass = (rec_min >= HP_DISTILLED_RECALL
               and non_deg_max <= HP_DEGRADATION
               and mmlu_max <= HP_DEGRADATION
               and one_wall_max <= HP_ONESHOT_WALL_S
               and one_rec_min >= HP_ONESHOT_RECALL
               and del_z_max < HP_DEL_Z
               and retain_min > HP_RETAIN_COSINE)
    hf_trip = (rec_min < HF_DISTILLED_RECALL
               or non_deg_max > HF_DEGRADATION
               or mmlu_max > HF_DEGRADATION
               or del_z_max > 5.0
               or retain_min < 0.65)
    if hp_pass:
        v = "HARD_PASS"
    elif hf_trip:
        v = "HARD_FAIL"
    else:
        v = "MIDDLE_BAND"
    msg = (f"Phase 0.5b distillation MVP: distilled_recall_min={rec_min:.3f} "
           f"(HP>={HP_DISTILLED_RECALL} HF<{HF_DISTILLED_RECALL}); "
           f"non_deg_max={non_deg_max:.3f} (HP<={HP_DEGRADATION}); "
           f"mmlu_deg_max={mmlu_max:.3f} (HP<={HP_DEGRADATION}); "
           f"oneshot wall={one_wall_max:.1f}s (HP<={HP_ONESHOT_WALL_S}) "
           f"recall={one_rec_min:.3f} (HP>={HP_ONESHOT_RECALL}); "
           f"del_Z_max={del_z_max:.2f} (HP<{HP_DEL_Z}); "
           f"retain_cos_min={retain_min:.3f} (HP>{HP_RETAIN_COSINE}). "
           f"Verdict: {v}."
           + probe_quality_tag())
    return v, msg


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "smoke")
    if run_mode == "full":
        seeds = SEEDS_FULL
        N = N_FULL
        M = M_DISTILLED_FULL
        n_non = N_NONDISTILLED_FULL
        n_mmlu = N_MMLU_FULL
        n_oneshot = N_ONESHOT_NEW
        n_del = N_DELETION_SUBSET
    else:
        seeds = SEEDS_SMOKE
        N = N_SMOKE
        M = M_DISTILLED_SMOKE
        n_non = N_NONDISTILLED_SMOKE
        n_mmlu = N_MMLU_SMOKE
        n_oneshot = N_ONESHOT_NEW_SMOKE
        n_del = N_DELETION_SUBSET_SMOKE
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} N={N} M_distilled={M} "
          f"n_non={n_non} n_mmlu={n_mmlu} n_oneshot={n_oneshot} n_del={n_del} "
          f"seeds={seeds}", flush=True)

    done, remaining = resumable_seeds(seeds, out_dir)
    t0 = time.time()
    for seed in remaining:
        print(f"  seed={seed}: distilling {M} KG triples, eval (i)-(v) ...",
              flush=True)
        result = run_one_seed(seed, N, M, n_non, n_mmlu, n_oneshot, n_del)
        write_partial(out_dir, seed, result)
        print(f"    distilled_recall={result['distilled_recall']:.3f} "
              f"non_deg={result['non_distilled_degradation']:.3f} "
              f"mmlu_deg={result['mmlu_degradation']:.3f} "
              f"oneshot_wall={result['oneshot_wall_s']:.1f}s "
              f"oneshot_recall={result['oneshot_recall']:.3f} "
              f"del_Z={result['deletion_Z_max']:.2f} "
              f"retain_cos={result['deletion_retained_cosine_min']:.3f} "
              f"({result['elapsed_s']:.1f}s)", flush=True)

    per_seed = aggregate_partials(out_dir, seeds)
    seeds_results = [per_seed[str(s)] for s in seeds]
    verdict, verdict_msg = classify_verdict(seeds_results)
    total_elapsed = time.time() - t0

    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": run_mode,
        "N": N, "M": M,
        "n_non": n_non, "n_mmlu": n_mmlu,
        "n_oneshot_new": n_oneshot, "n_deletion_subset": n_del,
        "n_seeds": len(seeds),
        "per_seed_results": seeds_results,
        "distilled_recall_min": min(r["distilled_recall"] for r in seeds_results),
        "non_distilled_degradation_max": max(r["non_distilled_degradation"] for r in seeds_results),
        "mmlu_degradation_max": max(r["mmlu_degradation"] for r in seeds_results),
        "oneshot_wall_max_s": max(r["oneshot_wall_s"] for r in seeds_results),
        "oneshot_recall_min": min(r["oneshot_recall"] for r in seeds_results),
        "deletion_Z_max_across_seeds": max(r["deletion_Z_max"] for r in seeds_results),
        "deletion_retained_cosine_min_across_seeds": min(r["deletion_retained_cosine_min"] for r in seeds_results),
        "verdict": verdict,
        "elapsed_s": total_elapsed,
        "thresholds": {
            "HP_distilled_recall": HP_DISTILLED_RECALL,
            "HF_distilled_recall": HF_DISTILLED_RECALL,
            "HP_degradation": HP_DEGRADATION,
            "HF_degradation": HF_DEGRADATION,
            "HP_oneshot_wall_s": HP_ONESHOT_WALL_S,
            "HP_oneshot_recall": HP_ONESHOT_RECALL,
            "HP_deletion_Z_max": HP_DEL_Z,
            "HP_retain_cosine_min": HP_RETAIN_COSINE,
        },
        "verdict_msg": verdict_msg,
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"[{ANCHOR_NAME}] verdict={verdict} elapsed={total_elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {out_dir / 'metrics.json'}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
