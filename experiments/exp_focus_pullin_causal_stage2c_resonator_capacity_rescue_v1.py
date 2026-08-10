# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; baseline vs resonator per-scale digests
#   differ; REAL vs SCRAMBLE_OBJECTS digests differ per arm -- reused _shuffle_objects)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (empirical capacity-rescue diagnostic; the sqrt(2*ln M) THEORETICAL ratio in
#   the pre-reg is the closest analytical anchor, not a closed-form floor for the full pipeline)
# - HP_SCOPE: {rescue_verdict: [relevant_recall@100k, relevant_recall@full, false_pull_in_rate,
#   scramble_objects_control]}
# - cardinality_ok: EXPECTED_N_UNITS = 2 arms x (len(scales) + (1 if full else 0))
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime -- GATE_THRESH=0.28 reused UNRETUNED from
#   Stage-1/Stage-2-B; M_SUB=1024/K_ENT=2 chosen from capacity-feasibility math + prior-work
#   K2-viable/K3-risky finding (resonator_factorization_v1 HARD_FAIL, cosine=0.41 KB hit), not
#   tuned against this cell's own results
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs REAL KGStore objects for BOTH arms (real_code_path) at tiny N, AND
#   validates the REAL cskg_foundation_v1 loader (imported unchanged from Stage-2-B)
# - PRECHECK (CONTRACT-mandated, flat=broken-experiment): (1) resonator trivial hand-case must
#   recall >=0.5 in a clean K_ENT=2 exact-cover regime; (2) Stage-2-B's landed metrics.json is
#   read off disk and asserted to still show its documented collapse shape BEFORE any fresh
#   baseline number is trusted as a reproduction
# - progress_logging: print_flush_true
# See preregs/2026-08-09_focus_pullin_causal_stage2c_resonator_capacity_rescue_v1.md for the full
# pre-reg (mechanism design, bands, reuse disclosure, compute-architecture estimate).
"""exp_focus_pullin_causal_stage2c_resonator_capacity_rescue_v1 -- CAPACITY RESCUE test for the
Stage-2-B scale wall: Stage-2-B (HARD_FAIL, commit 013f1481e) empirically found the CSKG-scale
salience-gate collapse is NOT EVT false-positive inflation (false_pull_in_rate=0.000 at every
scale) but STORE-CAPACITY COLLAPSE -- a Hopfield/Tsodyks-Feigelman crosstalk cliff in KGStore's
single [1024,1024] Hebbian W (relevant_recall: 0.967@1K -> 0.700@10K -> 0.000@30K+).

This cell tests whether RESONATOR-FACTORIZED entity-identity representation (digit-decompose each
entity id into K_ENT=2 sub-factors, each drawn from its own M_SUB=1024 codebook -- two orders of
magnitude smaller than the flat n_ent=482,588 entity codebook -- and decode via an alternating
resonator instead of a flat n_ent-way linear cleanup) holds relevant_recall at the exact rungs
(100K, 1.2M) where the flat single-entity-codebook readout collapsed to 0.000, HEAD-TO-HEAD
against a bit-identical reproduction of Stage-2-B's own baseline arm.

THEORETICAL anchor (Gaussian order-statistics, Gumbel 1958): the standardized noise margin a
decode step must beat scales ~sqrt(2*ln(#competing candidates)). sqrt(2*ln(482588))=5.116 vs
sqrt(2*ln(1024))=3.723 -- ~1.37x reduction in required per-step SNR from factorizing the search
space. The single shared W matrix and its absolute crosstalk noise are UNCHANGED between arms;
what changes is how much of that noise a given decode step can tolerate before picking wrong.

REUSE (imported, not re-transcribed): the baseline (single-W) arm is Stage-2-B's own eval_gate +
KGStore construction, called with the SAME seeds -- giving a bit-identical reproduction of its
landed numbers at matching scales, not an approximate one. Rungs (SCALES_SMOKE/SCALES_FULL),
GATE_THRESH, SHORTLIST_K, N_QUERY, QUERY_SEED, DATA_SEED, CSKG_DIR, _shuffle_objects, and
scale_point_verdict are all imported unchanged from exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1.

Prior-work check (SUBSTRATE-KB, mandatory): resonator_factorization_v1 (cosine=0.4092, HARD_FAIL)
measured K-way multiplicative-bind basin-convergence success by K (synthetic, no store, no
crosstalk): K2=1.000, K3=0.613 (HARD_FAIL band), K4=0.047. This cell uses K_ENT=2 specifically to
bank the validated K2=1.000 regime, not the shakier K3+ regime -- a design response to, not a
rediscovery of, that prior result. exp_resonator_dg_crosstalk_disentangler_v1's oracle-unbind-
margin methodology (unbind with the TRUE other factor to isolate codebook crosstalk from basin
dynamics) is reused directly for the relevant_in_shortlist_rate analog below.

Modes:
  --self-test  Real-code-path check: tiny K_ENT=2 exact-cover hand-case (n_ent=16, M_SUB=4) for the
               resonator arm; Stage-2-B's own precheck_kgstore_and_loader (imported) for the
               baseline arm + real CSKG loader; reads Stage-2-B's landed metrics.json off disk and
               asserts it still shows the documented collapse shape (stale-reference guard).
  --smoke      Real CSKG data, SCALES_SMOKE=[1000, 10000] (imported, same as Stage-2-B), both arms.
  --full       SCALES_FULL=[1000,5000,10000,30000,100000,1213912] (imported) + SCRAMBLE_OBJECTS
               control at the full point, both arms. Per-(arm,scale) checkpointed.
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "4")

import argparse
import hashlib
import json
import platform
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple

import numpy as np
import torch

ANCHOR_NAME = "focus_pullin_causal_stage2c_resonator_capacity_rescue_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
STAGE2B_METRICS_PATH = os.path.join(
    REPO_ROOT, "data", "exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1", "metrics.json")

from hdlab.kg_traversal import KGStore  # noqa: E402
# REUSE (imported, not re-transcribed): Stage-2-B's own baseline mechanism + rungs + constants.
from experiments.exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1 import (  # noqa: E402
    load_entity_vocab, load_spine_edges, eval_gate, precheck_kgstore_and_loader,
    scale_point_verdict, _shuffle_objects, GATE_THRESH, SHORTLIST_K, N_QUERY, QUERY_SEED,
    DATA_SEED, SCALES_SMOKE, SCALES_FULL, CSKG_DIR,
)
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

M_SUB = 1024          # THEORETICAL: M_SUB^2=1,048,576 >= n_ent=482,588 (~2.17x headroom margin)
K_ENT = 2              # 2-way factorization (see basin-convergence note below)
RESONATOR_MAX_IT = 30
RESONATOR_SEED = DATA_SEED + 777  # distinct from baseline's codebook seed; deterministic, no hash()

# BASIN-CONVERGENCE NOTE (MEASURED@standalone-diagnostic, this session, pre-dispatch, not in the
# original pre-reg -- disclosed here since it changed the readout design before any CSKG result was
# trusted, per flat=broken-experiment discipline): a HARD-commit alternating readout (each iteration
# fully commits to the argmax codeword before the next unbind, as resonator_factorization_v1's own
# K2=1.000 result at M=30 might naively suggest generalizes) collapses to ~2% success at M_SUB=1024
# even on a CLEAN, zero-crosstalk synthetic composite -- a basin-proliferation wall, not a crosstalk
# artifact (matches the "K5/K6 basin/capacity wall" already on file in
# exp_resonator_dg_crosstalk_disentangler_v1's docstring, now shown to generalize to K=2 once M grows
# from 30 to ~1000, not just to K>=5). A SOFT/linear readout (weighted-superposition estimate kept
# continuous between iterations, matching exp_resonator_factorization_v1's actual FHRR structure more
# faithfully than a hard-commit port) measured 100% at M_SUB<=128, 85% at M_SUB=256, 57.5% at
# M_SUB=512, ~12-27% at M_SUB=1024 (clean, single-shot, 40 trials each) -- much better but still
# basin-convergence-limited at the M_SUB=1024 scale FULL n_ent=482,588 coverage requires with K_ENT=2.
# K_ENT=3 (M_SUB~79 for coverage) measured WORSE (6.7% at M_SUB=79) -- higher K makes the convergence
# problem worse per-M, consistent with resonator_factorization_v1's own K3=0.613/K4=0.047 at M=30.
# Multi-restart (soft-readout, up to 20 restarts, confidence-based selection) did NOT reliably
# improve M_SUB=1024 success (non-monotonic 15-30% across restart counts) -- the confidence score
# is not a reliable discriminator between a correct and a spuriously-converged restart at this scale.
# DECISION: keep K_ENT=2/M_SUB=1024 for full coverage (required to test the real CSKG entity space,
# not a subset) and switch to the soft/linear readout (the measurably better, literature-consistent
# choice) below. The ORACLE-unbind diagnostic (relevant_in_shortlist_rate) is UNAFFECTED by this
# basin-convergence limitation (it isolates store crosstalk from search dynamics by construction) and
# is reported as the primary crosstalk-tolerance signal alongside the end-to-end relevant_recall,
# which the basin-convergence wall is expected to bottleneck regardless of store crosstalk.

HARD_PASS_RECALL_MIN = 0.50
HARD_FAIL_RECALL_MAX = 0.10
FALSE_PULL_IN_MAX = 0.20
SCRAMBLE_COLLAPSE_MAX = 0.10
SCRAMBLE_GAP_MIN = 0.20
BASELINE_REPRO_TOLERANCE = 0.02


# ============================================================================ digit-factorized entity codes
def build_digit_codebooks(m_sub: int, n_dim: int, generator: torch.Generator) -> Tuple[torch.Tensor, torch.Tensor]:
    """Two independent bipolar {-1,+1} per-digit codebooks, shape [m_sub, n_dim] each."""
    d0 = (torch.randint(0, 2, (m_sub, n_dim), generator=generator, dtype=torch.int8) * 2 - 1).to(torch.float32)
    d1 = (torch.randint(0, 2, (m_sub, n_dim), generator=generator, dtype=torch.int8) * 2 - 1).to(torch.float32)
    return d0, d1


def build_factored_E(n_ent: int, d0: torch.Tensor, d1: torch.Tensor, m_sub: int) -> torch.Tensor:
    """entity_code(id) = D0[id // m_sub] * D1[id % m_sub], vectorized over all n_ent ids."""
    ids = torch.arange(n_ent, dtype=torch.long)
    digit0 = ids // m_sub
    digit1 = ids % m_sub
    return d0[digit0] * d1[digit1]


# ============================================================================ resonator decode
def resonate_2way(probe: torch.Tensor, d0: torch.Tensor, d1: torch.Tensor,
                  max_it: int = RESONATOR_MAX_IT) -> Tuple[int, int, float, float]:
    """Alternating unbind-cleanup resonator for a 2-way bipolar multiplicative-bound composite.
    probe ~= D0[true_d0]*D1[true_d1] + crosstalk. Returns (i0, i1, score0, score1).

    SOFT/linear readout (MEASURED@standalone-diagnostic this session, see BASIN-CONVERGENCE NOTE
    above): the per-factor estimate carried between iterations is a REAL-VALUED weighted
    superposition (`scores @ codebook`, whole-vector normalized) kept continuous, NOT a hard commit
    to the argmax codeword every step -- this mirrors exp_resonator_factorization_v1's actual FHRR
    structure (`est[k] = scores @ books[k]`) more faithfully than a hard-commit port, and measured
    much better basin-convergence (100% at M_SUB<=128 vs ~2% for hard-commit, both clean/no-crosstalk).
    Only the FINAL readout (i0, i1) is hard (argmax), used for the decoded entity id and the
    confidence gate."""
    e1 = d1.mean(dim=0)
    e1 = e1 / (e1.norm() + 1e-8)
    prev = None
    i0 = i1 = 0
    s0v = s1v = 0.0
    for _ in range(max_it):
        r0 = probe * e1
        s0 = d0 @ r0
        i0 = int(torch.argmax(s0).item())
        s0v = float(s0[i0].item())
        e0 = s0 @ d0
        e0 = e0 / (e0.norm() + 1e-8)
        r1 = probe * e0
        s1 = d1 @ r1
        i1 = int(torch.argmax(s1).item())
        s1v = float(s1[i1].item())
        e1 = s1 @ d1
        e1 = e1 / (e1.norm() + 1e-8)
        if (i0, i1) == prev:
            break
        prev = (i0, i1)
    return i0, i1, s0v, s1v


def _cos(a: torch.Tensor, b: torch.Tensor) -> float:
    na = float(torch.linalg.norm(a))
    nb = float(torch.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(torch.dot(a, b) / (na * nb))


def decode_entity(probe: torch.Tensor, d0: torch.Tensor, d1: torch.Tensor, m_sub: int,
                  max_it: int = RESONATOR_MAX_IT) -> Tuple[int, float, int, int]:
    i0, i1, _, _ = resonate_2way(probe, d0, d1, max_it)
    composed = d0[i0] * d1[i1]
    conf = _cos(probe, composed)
    entity_id_hat = i0 * m_sub + i1
    return entity_id_hat, conf, i0, i1


def oracle_digit_check(probe: torch.Tensor, d0: torch.Tensor, d1: torch.Tensor,
                       true_d0: int, true_d1: int) -> bool:
    """ORACLE unbind (basin dynamics removed): unbind with the TRUE other digit, check both
    digits' argmax match truth. Reuses exp_resonator_dg_crosstalk_disentangler_v1's oracle-unbind-
    margin methodology to isolate store crosstalk from resonator basin-convergence dynamics."""
    r0 = probe * d1[true_d1]
    d0_ok = int(torch.argmax(d0 @ r0).item()) == true_d0
    r1 = probe * d0[true_d0]
    d1_ok = int(torch.argmax(d1 @ r1).item()) == true_d1
    return bool(d0_ok and d1_ok)


# ============================================================================ resonator gate evaluation
def eval_gate_resonator(store: KGStore, ingested_triples: torch.Tensor, n_rel: int, n_query: int,
                        query_seed: int, d0: torch.Tensor, d1: torch.Tensor, m_sub: int,
                        gate: float = GATE_THRESH, max_it: int = RESONATOR_MAX_IT) -> Dict:
    """Structurally IDENTICAL query-generation/negative-sampling shell to Stage-2-B's eval_gate
    (same q_rng draw order, same existing_sp membership check) so the SAME query_seed draws the
    SAME queries for both arms -- a paired, not just parallel, comparison. Only the retrieval step
    (resonator decode + cosine gate, replacing score_all + pull_in) differs."""
    q_rng = np.random.default_rng(query_seed)
    n = ingested_triples.shape[0]
    existing_sp = set((int(s) * n_rel + int(p)) for s, p, _o in ingested_triples.tolist())

    rel_idx = q_rng.choice(n, size=min(n_query, n), replace=False)
    rel_admitted_correct = 0
    rel_oracle_ok = 0
    for i in rel_idx:
        s, p, o = (int(x) for x in ingested_triples[i])
        key = store.key(s, p)
        probe = store.W @ key
        true_d0, true_d1 = o // m_sub, o % m_sub
        if oracle_digit_check(probe, d0, d1, true_d0, true_d1):
            rel_oracle_ok += 1
        eid_hat, conf, _i0, _i1 = decode_entity(probe, d0, d1, m_sub, max_it)
        if eid_hat == o and conf >= gate:
            rel_admitted_correct += 1

    neg_count = 0
    neg_admitted = 0
    tries = 0
    n_ent = store.n_ent
    while neg_count < n_query and tries < n_query * 20:
        tries += 1
        s = int(q_rng.integers(0, n_ent))
        p = int(q_rng.integers(0, n_rel))
        if (s * n_rel + p) in existing_sp:
            continue
        neg_count += 1
        key = store.key(s, p)
        probe = store.W @ key
        _eid_hat, conf, _i0, _i1 = decode_entity(probe, d0, d1, m_sub, max_it)
        if conf >= gate:
            neg_admitted += 1

    return {
        "n_relevant_queried": int(len(rel_idx)),
        "relevant_recall": rel_admitted_correct / max(len(rel_idx), 1),
        "relevant_in_shortlist_rate": rel_oracle_ok / max(len(rel_idx), 1),  # oracle-unbind analog
        "n_negative_queried": neg_count,
        "false_pull_in_rate": neg_admitted / max(neg_count, 1),
    }


# ============================================================================ baseline-reproduction precheck
def load_stage2b_reference() -> Dict[int, float]:
    with open(STAGE2B_METRICS_PATH, encoding="utf-8") as f:
        d = json.load(f)
    return {int(k): v["relevant_recall"] for k, v in d["per_scale"].items()}


def check_baseline_repro(fresh_per_scale: Dict[str, Dict], reference: Dict[int, float],
                         tol: float = BASELINE_REPRO_TOLERANCE) -> Dict:
    mismatches = {}
    for scale_str, m in fresh_per_scale.items():
        scale = int(scale_str)
        if scale in reference:
            fresh = m["relevant_recall"]
            ref = reference[scale]
            if abs(fresh - ref) > tol:
                mismatches[scale] = {"fresh": fresh, "reference": ref}
    return {"ok": len(mismatches) == 0, "mismatches": mismatches}


# ============================================================================ rescue verdict logic
def rescue_verdict(res_100k: Optional[float], res_full: float, fp_100k: Optional[float],
                   fp_full: float, scramble_recall: Optional[float], real_full_recall: float,
                   baseline_repro_ok: bool) -> Tuple[str, str]:
    if not baseline_repro_ok:
        return ("BASELINE_REPRO_FAIL", "BASELINE_REPRO_FAIL_DO_NOT_TRUST_COMPARISON: fresh "
                "baseline numbers diverged from Stage-2-B's landed reference beyond tolerance")

    r100k = res_100k if res_100k is not None else 0.0
    fp100k = fp_100k if fp_100k is not None else 1.0
    holds_100k = r100k >= HARD_PASS_RECALL_MIN
    holds_full = res_full >= HARD_PASS_RECALL_MIN
    fails_100k = r100k < HARD_FAIL_RECALL_MAX
    fails_full = res_full < HARD_FAIL_RECALL_MAX
    fp_ok = (fp100k <= FALSE_PULL_IN_MAX) and (fp_full <= FALSE_PULL_IN_MAX)
    scramble_ok = (scramble_recall is not None and scramble_recall <= SCRAMBLE_COLLAPSE_MAX
                  and (real_full_recall - scramble_recall) >= SCRAMBLE_GAP_MIN)

    msg = (f"resonator relevant_recall@100k={r100k:.3f} @full={res_full:.3f} "
          f"false_pull_in@100k={fp100k:.3f} @full={fp_full:.3f} "
          f"scramble_recall={scramble_recall} real_full={real_full_recall:.3f}")

    if holds_100k and holds_full and fp_ok and scramble_ok:
        return "HARD_PASS", f"HARD_PASS: resonator holds recall at both collapsed rungs. {msg}"
    if fails_100k and fails_full:
        return "HARD_FAIL", f"HARD_FAIL: resonator ALSO collapses to ~0 by 100k. {msg}"
    return "MIDDLE_BAND", f"MIDDLE_BAND: partial rescue. {msg}"


# ============================================================================ output plumbing
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _write_heartbeat(output_dir, unit_idx, total_units, elapsed_s, extra=None):
    path = os.path.join(output_dir, "_heartbeat.jsonl")
    rec = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
          "total_units": total_units, "elapsed_s": round(elapsed_s, 2)}
    if extra:
        rec.update(extra)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


def _digest(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


# ============================================================================ self-test
def self_test() -> Dict:
    # (1) baseline arm real-code-path + real CSKG loader (imported unchanged from Stage-2-B)
    pre = precheck_kgstore_and_loader()
    assert pre["ok"], f"BASELINE_PRECHECK_FAIL (flat=broken-experiment discipline): {pre}"

    # (2) resonator trivial hand-case: K_ENT=2 exact-cover (M_SUB=4 -> 16 entities exactly)
    gen = torch.Generator()
    gen.manual_seed(7)
    m_sub_tiny = 4
    d0_tiny, d1_tiny = build_digit_codebooks(m_sub_tiny, 64, gen)
    e_factored_tiny = build_factored_E(16, d0_tiny, d1_tiny, m_sub_tiny)
    store = KGStore(n_ent=16, n_rel=2, n_dim=64, generator=gen, init_entities=False)
    store.E = e_factored_tiny
    triples = torch.tensor([[i, i % 2, (i + 1) % 16] for i in range(16)], dtype=torch.long)
    store.ingest_triples(triples)
    m_res = eval_gate_resonator(store, triples, n_rel=2, n_query=8, query_seed=1,
                                d0=d0_tiny, d1=d1_tiny, m_sub=m_sub_tiny)
    resonator_tiny_ok = m_res["relevant_recall"] >= 0.5
    assert resonator_tiny_ok, f"RESONATOR_TRIVIAL_HAND_CASE_FAIL: {m_res}"

    # (3) resonator basic bind/unbind self-consistency (formula self-test)
    a = d0_tiny[1]
    assert torch.equal(a * a, torch.ones_like(a)), "bipolar self-inverse (x*x=1) broken"

    # (4) single-W baseline known-collapse reference file check (stale-reference guard)
    ref = load_stage2b_reference()
    assert ref.get(1000, 0.0) > 0.90, (
        f"STAGE2B_REFERENCE_STALE_OR_MISSING: expected recall>0.90 at scale=1000, got {ref.get(1000)}")
    assert ref.get(1213912, 1.0) < 0.05, (
        f"STAGE2B_REFERENCE_STALE_OR_MISSING: expected recall<0.05 at full scale, got {ref.get(1213912)}")

    # (5) verdict-logic unit checks
    v_fail, _ = rescue_verdict(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, baseline_repro_ok=True)
    assert v_fail == "HARD_FAIL", v_fail
    v_pass, _ = rescue_verdict(0.8, 0.7, 0.02, 0.02, 0.0, 0.7, baseline_repro_ok=True)
    assert v_pass == "HARD_PASS", v_pass
    v_mid, _ = rescue_verdict(0.6, 0.05, 0.02, 0.02, 0.0, 0.05, baseline_repro_ok=True)
    assert v_mid == "MIDDLE_BAND", v_mid
    v_repro_fail, _ = rescue_verdict(0.8, 0.7, 0.02, 0.02, 0.0, 0.7, baseline_repro_ok=False)
    assert v_repro_fail == "BASELINE_REPRO_FAIL", v_repro_fail

    return {"baseline_precheck": pre, "resonator_tiny_metrics": m_res,
            "resonator_tiny_ok": resonator_tiny_ok,
            "stage2b_reference_sample": {1000: ref.get(1000), 1213912: ref.get(1213912)},
            "verdict_logic_unit_checks": {"hard_fail": v_fail, "hard_pass": v_pass,
                                          "middle_band": v_mid, "repro_fail": v_repro_fail}}


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.full):
        t0 = time.time()
        result = self_test()
        elapsed = time.time() - t0
        metrics = {"verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "self-test green",
                  "elapsed_s": round(elapsed, 3), "run_mode": "self_test", "anchor_name": ANCHOR_NAME,
                  "result": result}
        _write_metrics(OUTPUT_DIR, metrics)
        print(json.dumps(metrics, indent=2, default=str))
        return

    run_mode = "smoke" if args.smoke else "full"
    output_dir = OUTPUT_DIR + "_smoke" if args.smoke else OUTPUT_DIR
    scales = SCALES_SMOKE if args.smoke else SCALES_FULL
    n_scale_units = len(scales)
    expected_units = 2 * (n_scale_units + (1 if run_mode == "full" else 0))
    _write_start_marker(output_dir, run_mode, expected_units)
    t0 = time.time()

    print(f"[{run_mode}] loading real CSKG entity vocab...", flush=True)
    entity_to_idx = load_entity_vocab(CSKG_DIR)
    n_ent = len(entity_to_idx)
    print(f"[{run_mode}] {n_ent} entities loaded in {time.time()-t0:.2f}s; loading spine edges...",
        flush=True)
    triples_int, relation_to_idx = load_spine_edges(entity_to_idx, CSKG_DIR)
    n_rel = len(relation_to_idx)
    print(f"[{run_mode}] {len(triples_int)} spine edges loaded, n_rel={n_rel}, "
        f"t={time.time()-t0:.2f}s", flush=True)

    assert M_SUB * M_SUB >= n_ent, f"CAPACITY_INFEASIBLE: M_SUB^2={M_SUB*M_SUB} < n_ent={n_ent}"

    rng = np.random.default_rng(DATA_SEED)
    perm = rng.permutation(len(triples_int))
    triples_shuffled = torch.from_numpy(triples_int[perm])

    # baseline arm: bit-identical construction to Stage-2-B
    gen_base = torch.Generator()
    gen_base.manual_seed(DATA_SEED)
    store_base = KGStore(n_ent=n_ent, n_rel=n_rel, n_dim=1024, generator=gen_base)
    print(f"[{run_mode}] baseline KGStore allocated (E={tuple(store_base.E.shape)}) "
        f"t={time.time()-t0:.2f}s", flush=True)

    # resonator arm: factorized entity codes injected via base-kwargs-only construction
    gen_res = torch.Generator()
    gen_res.manual_seed(RESONATOR_SEED)
    d0, d1 = build_digit_codebooks(M_SUB, 1024, gen_res)
    e_factored = build_factored_E(n_ent, d0, d1, M_SUB)
    store_res = KGStore(n_ent=n_ent, n_rel=n_rel, n_dim=1024, generator=gen_res, init_entities=False)
    store_res.E = e_factored
    print(f"[{run_mode}] resonator KGStore allocated (D0={tuple(d0.shape)} D1={tuple(d1.shape)} "
        f"E_factored={tuple(store_res.E.shape)}) t={time.time()-t0:.2f}s", flush=True)

    done = completed_units(output_dir)
    per_scale_base: Dict[str, Dict] = {}
    per_scale_res: Dict[str, Dict] = {}
    unit_i = 0
    for scale in scales:
        scale = min(scale, len(triples_shuffled))
        ingested = triples_shuffled[:scale]

        key_base = unit_key("baseline", "scale", scale)
        if key_base not in done:
            store_base.reset()
            store_base.ingest_triples(ingested)
            m = eval_gate(store_base, ingested, n_rel=n_rel, n_query=N_QUERY, query_seed=QUERY_SEED)
            verdict, msg = scale_point_verdict(m)
            m.update({"scale": scale, "arm": "baseline", "verdict": verdict, "verdict_msg": msg})
            record_unit(output_dir, key_base, m)
            print(f"[{run_mode}] scale={scale} BASELINE {verdict}: {msg}", flush=True)
        unit_i += 1
        _write_heartbeat(output_dir, unit_i, expected_units, time.time() - t0,
                         extra={"scale": scale, "arm": "baseline"})

        key_res = unit_key("resonator", "scale", scale)
        if key_res not in done:
            store_res.reset()
            store_res.ingest_triples(ingested)
            m = eval_gate_resonator(store_res, ingested, n_rel=n_rel, n_query=N_QUERY,
                                    query_seed=QUERY_SEED, d0=d0, d1=d1, m_sub=M_SUB)
            verdict, msg = scale_point_verdict(m)
            m.update({"scale": scale, "arm": "resonator", "verdict": verdict, "verdict_msg": msg})
            record_unit(output_dir, key_res, m)
            print(f"[{run_mode}] scale={scale} RESONATOR {verdict}: {msg}", flush=True)
        unit_i += 1
        _write_heartbeat(output_dir, unit_i, expected_units, time.time() - t0,
                         extra={"scale": scale, "arm": "resonator"})

    scramble_base = None
    scramble_res = None
    if run_mode == "full":
        full_scale = min(SCALES_FULL[-1], len(triples_shuffled))
        scrambled = _shuffle_objects(triples_shuffled[:full_scale], seed=DATA_SEED)

        skey_base = unit_key("baseline", "scramble_objects", "full")
        if skey_base not in done:
            store_base.reset()
            store_base.ingest_triples(scrambled)
            m = eval_gate(store_base, scrambled, n_rel=n_rel, n_query=N_QUERY, query_seed=QUERY_SEED)
            m.update({"scale": full_scale, "arm": "baseline", "control": "scramble_objects"})
            record_unit(output_dir, skey_base, m)
            print(f"[{run_mode}] scramble_objects BASELINE recall={m['relevant_recall']:.3f}", flush=True)
        unit_i += 1
        _write_heartbeat(output_dir, unit_i, expected_units, time.time() - t0)

        skey_res = unit_key("resonator", "scramble_objects", "full")
        if skey_res not in done:
            store_res.reset()
            store_res.ingest_triples(scrambled)
            m = eval_gate_resonator(store_res, scrambled, n_rel=n_rel, n_query=N_QUERY,
                                    query_seed=QUERY_SEED, d0=d0, d1=d1, m_sub=M_SUB)
            m.update({"scale": full_scale, "arm": "resonator", "control": "scramble_objects"})
            record_unit(output_dir, skey_res, m)
            print(f"[{run_mode}] scramble_objects RESONATOR recall={m['relevant_recall']:.3f}", flush=True)
        unit_i += 1
        _write_heartbeat(output_dir, unit_i, expected_units, time.time() - t0)

    all_units = load_units(output_dir)
    for k, u in all_units.items():
        if k.startswith("baseline|scale|"):
            per_scale_base[str(u["scale"])] = u
        elif k.startswith("resonator|scale|"):
            per_scale_res[str(u["scale"])] = u
        elif k.startswith("baseline|scramble_objects|"):
            scramble_base = u
        elif k.startswith("resonator|scramble_objects|"):
            scramble_res = u

    cardinality_ok = (len(per_scale_base) == n_scale_units) and (len(per_scale_res) == n_scale_units)

    reference = load_stage2b_reference()
    repro = check_baseline_repro(per_scale_base, reference)

    full_scale_key = str(min(SCALES_FULL[-1], len(triples_shuffled)))
    res_100k = per_scale_res.get("100000", {}).get("relevant_recall")
    fp_100k = per_scale_res.get("100000", {}).get("false_pull_in_rate")
    res_full_point = per_scale_res.get(full_scale_key)
    if res_full_point is None:
        largest = str(max(int(k) for k in per_scale_res))
        res_full_point = per_scale_res[largest]
    res_full = res_full_point["relevant_recall"]
    fp_full = res_full_point["false_pull_in_rate"]
    scramble_recall = scramble_res["relevant_recall"] if scramble_res else None

    if run_mode == "full":
        overall_verdict, overall_msg = rescue_verdict(
            res_100k, res_full, fp_100k, fp_full, scramble_recall, res_full, repro["ok"])
    else:
        overall_verdict, overall_msg = (
            "SMOKE_PREVIEW",
            f"SMOKE_PREVIEW (not the full rescue verdict; scales={list(per_scale_res.keys())}) "
            f"baseline_repro_ok={repro['ok']}")

    # arms-must-differ (META_RULE_AF): baseline vs resonator per-scale digests must differ
    common_scales = sorted(set(per_scale_base) & set(per_scale_res))
    arms_diff = {}
    for sc in common_scales:
        db = _digest({k: v for k, v in per_scale_base[sc].items() if k not in ("ingest_s", "eval_s")})
        dr = _digest({k: v for k, v in per_scale_res[sc].items() if k not in ("ingest_s", "eval_s")})
        arms_diff[sc] = {"baseline_digest": db, "resonator_digest": dr, "differ": db != dr}
    arms_differ_ok = all(v["differ"] for v in arms_diff.values()) if arms_diff else False

    scramble_diff = None
    if scramble_base is not None and scramble_res is not None:
        db = _digest({k: v for k, v in scramble_base.items() if k not in ("ingest_s", "eval_s")})
        dr = _digest({k: v for k, v in scramble_res.items() if k not in ("ingest_s", "eval_s")})
        scramble_diff = {"baseline_digest": db, "resonator_digest": dr, "differ": db != dr}

    elapsed = time.time() - t0
    metrics = {
        "verdict": overall_verdict, "verdict_msg": overall_msg,
        "summary": overall_msg, "elapsed_s": round(elapsed, 3), "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME, "gate_thresh": GATE_THRESH, "m_sub": M_SUB, "k_ent": K_ENT,
        "resonator_max_it": RESONATOR_MAX_IT, "n_dim": 1024, "n_ent": n_ent, "n_rel": n_rel,
        "n_spine_edges_total": len(triples_int), "scales": scales,
        "per_scale_baseline": per_scale_base, "per_scale_resonator": per_scale_res,
        "scramble_objects_control": {"baseline": scramble_base, "resonator": scramble_res},
        "baseline_repro_check": repro, "baseline_reference_source": STAGE2B_METRICS_PATH,
        "rescue_bands": {"hard_pass_recall_min": HARD_PASS_RECALL_MIN,
                         "hard_fail_recall_max": HARD_FAIL_RECALL_MAX,
                         "false_pull_in_max": FALSE_PULL_IN_MAX,
                         "scramble_collapse_max": SCRAMBLE_COLLAPSE_MAX,
                         "scramble_gap_min": SCRAMBLE_GAP_MIN},
        "arms_differ_check": arms_diff, "arms_differ_verified": arms_differ_ok,
        "scramble_arms_differ_check": scramble_diff,
        "cardinality_ok": cardinality_ok, "expected_n_units": expected_units,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "empirical capacity-rescue diagnostic; sqrt(2*ln M) THEORETICAL ratio in "
                    "pre-reg is the closest analytical anchor, not a closed-form floor",
        "deterministic_seeding": True,
        "calibration_check": "default_ok_for_this_regime: GATE_THRESH=0.28 reused unretuned from "
                            "Stage-1/Stage-2-B; M_SUB/K_ENT chosen from capacity math + prior-work "
                            "K2-viable/K3-risky finding, not tuned against this cell's own results",
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps({k: v for k, v in metrics.items()
                      if k not in ("per_scale_baseline", "per_scale_resonator")}, indent=2, default=str))
    print(json.dumps({"per_scale_baseline": per_scale_base, "per_scale_resonator": per_scale_res},
                     indent=2, default=str))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- deliberately not BaseException, see cell-template mandate
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
