"""A5-gated atomize (raw-jsonl mode): WM K-cliff MEASURED_MECHANISM + pattern_completion MIDDLE_BAND.

VERDICTS (verified OFF DATA, not verdict_msg):

== Landing 1: WM K-cliff 3-seed phase diagram ==
Orchestrator framing: HARD_PASS x3 chain-grade candidate (K=16384 cliff floor).
Cert-owner ruling: MEASURED_MECHANISM / mechanism_characterization (cert-neutral, NOT chain-grade).

Verify-off-data findings (per-arm, per-seed, recomputed from per_unit):
  - Pre-reg expected 45 phase points x 2 arms = 90 units per seed.
  - Per-seed n_units_observed = 54 (only 27 paired (K,ov,rn) points x 2 arms = 54).
  - Pre-reg "5 K-values" = {4096, 8192, 16384, 32768, 65536}; only K in {4096, 8192, 16384} actually RAN.
  - K=32768 and K=65536 hit HP_VRAM_PROBE_BREACH (est_peak=5.51GB > budget=4.88GB on 8GB GPU).
  - Cell treats probe-denials as "CLIFF" markers per pre-reg spec; HARD_PASS gate "corridor_pass>=3 of 5"
    is satisfied via 3-of-5 K-values formally even though 2 of those 5 never ran.
  - Per-arm SUBSTRATE recall: for ALL 27 paired (K,ov,rn) points across K in {4096, 8192, 16384}:
      seed_7:  K=4096 avg=1.0000 (min 1.0000); K=8192 avg=1.0000 (min 0.9999); K=16384 avg=1.0000 (min 0.9999)
      seed_13: K=4096 avg=1.0000 (min 1.0000); K=8192 avg=1.0000 (min 1.0000); K=16384 avg=1.0000 (min 0.9999)
      seed_19: K=4096 avg=1.0000 (min 0.9998); K=8192 avg=1.0000 (min 1.0000); K=16384 avg=1.0000 (min 1.0000)
  - 100% of MEASURED paired points are at saturation (sub_r >= HP_SAT 0.995). n_saturate=27/27 measured.
  - RANDOM arm avg recall ~ 0 to 5.4e-5 (mathematical 1/CB ~ 1.5e-5 floor as designed).
  - arms_differ_sha256 distinct across all 27 points per seed; SHA varies cleanly across seeds 7/13/19.
  - substrate-only-decode gate: _llm_forward_calls_at_inference = 0 across all 54 units per seed (PASS).
  - GPU util p50: 77 / 77 / 88 (Fix #24 satisfied; first phase-diagram cell with proper GPU usage; valid).
  - cardinality_ok=True per cell convention (54 ran + 36 probe-denied = 90 == expected); pre-reg-compliant
    BUT the cell's HARD_FAIL_SATURATION_ONLY check (line 887) tests n_saturate == len(phase_map) where
    len(phase_map) includes probe-denied points marked tier="CLIFF". So n_saturate=27 != 45; the
    saturation_only gate cannot fire when probe-denials inflate the denominator. This is a SCHEMA bug
    in the cell's saturation-only check + a Skunkworks-Q rule trigger (suspect 1.000 results).

Tier disposition rationale:
  (a) By-construction-saturation: SUBSTRATE recall is 1.0000 at every measured point. The "discriminator
      SUBSTRATE - RANDOM > 0.20" is trivially passed since RANDOM is mathematically pinned at 1/65536 ~
      1.5e-5. This is the classic g1-pattern (cert-owner overrides Director via by-construction-saturation,
      atomized 2026-06-22).
  (b) Capacity-bound not phase-cliff: the "cliff at K=16384" is a VRAM-probe ceiling on an 8GB GPU,
      not an empirically observed substrate-mechanism transition. K=32768/65536 may or may not cliff;
      we have no measured evidence.
  (c) Secondary axes (overlap, routing_noise) FULLY SATURATED: at every (ov, rn) combination measured,
      recall stayed at ~1.0. The pre-reg's "F6 phase-coherence: cliff K monotone in (overlap+noise)" has
      no empirical basis -- no cliff observed in any direction within the measurement regime.
  (d) Robustness is REAL: substrate IS robust to overlap=0.3 + routing_noise=0.15 at K up to 16384
      (3 seeds, 9 corners per K, 27 points). This characterization is a proven bound -- the mechanism
      doesn't degrade in the measured regime.

Cert class: mechanism_characterization (proven robustness bound; not a phase-cliff localization).
cert_increment_delta = 0 (CERT-neutral; MM is not chain-grade; same pattern as g1 2026-06-22).

3-seed convergence: all 3 seeds report identical aggregate (pass=27, sat=27, floor=0, probe_cliffs=36,
arms_differ=27/9). This is expected when every point saturates -- 3-seed convergence on saturation is
not 3-seed convergence on a discriminator. Independent SHA per seed confirms genuine independent runs.

Test-design recommendation for v2: need 16GB+ GPU OR smaller K_per_bank to actually localize the cliff
beyond K=16384; or alternatively pivot to discriminating regime (smaller N_DIM or higher k_per_bank to
push alpha past 1.0 where the chain-grade primitive previously cliffed). The pre-reg's HARD_FAIL_
SATURATION_ONLY gate should be RESPECIFIED to fire on measured points only (n_saturate / n_measured),
not against the total phase-map size including probe-denials.

== Landing 2: pattern_completion corruption-cliff phase diagram ==
Orchestrator framing: MIDDLE_BAND by-construction saturation per Fix #28 + BIAS-Q.
Cert-owner ruling: MIDDLE_BAND / mechanism_characterization (cert-neutral). Concurs with orchestrator.

Verify-off-data findings (per phase-map):
  - 72/72 phase points all ran (cardinality_ok=True, observed==expected).
  - Tier distribution: 24 SATURATED + 48 FLOOR + 0 HARD_PASS + 0 MIDDLE_BAND + 0 HARD_FAIL.
  - corruption_frac=0.10: ALL 12 (N x iters) points top1_substrate = 1.0000 (saturation).
  - corruption_frac=0.30: ALL 12 points top1_substrate = 1.0000 (saturation).
  - corruption_frac=0.50: ALL 12 points top1_substrate = 0.0000 to 0.0020 (collapse).
  - corruption_frac=0.70/0.85/0.95: ALL 36 points top1_substrate = 0.0000 (floor).
  - Cliff is a sharp STEP at corruption_frac approx 0.5 -- matches CRLB theory (1-step cliff 0.46-0.49).
  - cleanup_iters in {1, 5, 20}: ZERO difference at every (N, corruption_frac) cell. H2 (iters extend
    cliff to higher corruption) is FALSIFIED -- T=5 and T=20 give identical results to T=1.
  - N in {2048, 4096, 8192, 16384}: cliff at corruption_frac=0.5 for EVERY N (cliff doesn't shift right
    with N as predicted by H1; H1 partially falsified -- 4x N variation produced no shift).
  - arms_differ_sha256.differ=True (substrate SHA vs random SHA; cleanly distinct).
  - device=cuda, gpu_util_estimate=0.95 (high; Fix #24 satisfied).
  - Substrate-only gate: _LLM_CALL_COUNTER asserted 0 at exit (cell-line 1140).
  - No silent except (META_RULE_J satisfied; pre-reg promises halt on unit exception).

Tier disposition rationale:
  (a) Sweep saturates on EASY corruption (<=0.30) and floors on HARD corruption (>=0.50). The pre-reg's
      HARD_PASS band [0.80, 0.95) and MIDDLE_BAND [0.50, 0.80) are EMPTY -- the cell observes a step
      function, not a graded cliff. By-construction saturation per BIAS-Q.
  (b) The cliff IS empirically localized at corruption_frac approx 0.5, matching CRLB theory cleanly.
      This IS measurement, just not a CHARACTERIZATION (we know the cliff is sharp; we don't know what
      the cliff edge looks like at finer resolution).
  (c) H2 (iters help) FALSIFIED -- T=20 doesn't beat T=1 at any (N, corruption_frac). This is a PROVEN
      NEGATIVE for the iterative-attractor-basin-grows hypothesis (CERT-neutral honest result).

Cert class: mechanism_characterization (cliff sharp-step verified; iters falsified; CERT-neutral).
cert_increment_delta = 0 (MIDDLE_BAND not chain-grade).

Test-design recommendation for v2 (META_RULE_AG band-calibration regime check):
  Pre-reg should target the [0.30, 0.70] band where mechanism is NOT saturated NOT floored. Suggested
  finer corruption sweep: {0.40, 0.42, 0.44, 0.46, 0.48, 0.50, 0.52, 0.54, 0.56, 0.60}. THIS IS where the
  iterative cleanup (T=20 vs T=1) might actually differentiate -- the basin-of-attraction question is
  meaningless at saturation OR floor; it only matters at the edge. v1's coarse {0.10, 0.30, 0.50, 0.70,
  0.85, 0.95} grid stepped right over the interesting regime.

A5 PROTOCOL:
  PRE: read full atoms.jsonl + cert_ledger.jsonl, count lines, parse last line.
  WRITE: per-file tmp -> os.replace atomic append.
  POST: re-read full file, count delta = expected, parse last line, verify new atom ID present.

NO PartitionedStore round-trip because schema enum doesn't include "discipline_rule" kind written by
sibling atomize tool today (atomize_partition_oracle_substrate_derived_hint_v1_HF_AP_2026-06-28.py).
Following the raw-jsonl + cert_ledger pattern those sibling atomizes have established.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
META_ATOMS = ROOT / "data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

SOURCE_TAG = "skunkworks_atomize_wm_kcliff_MM_pattern_completion_MB_2026-06-28"
ATOMIZED_DATE = "2026-06-28"


# =========================================================================
# Off-data recompute helpers (verify-OFF-DATA pre-atomization)
# =========================================================================

def verify_wm_kcliff(seed: int) -> dict:
    cell = f"exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_{seed}_v1"
    path = ROOT / f"data/{cell}/metrics.json"
    m = json.loads(path.read_text(encoding="utf-8"))
    pu = m["per_unit"]
    by_kr = {}
    for u in pu:
        by_kr.setdefault((u["k_total"], u["regime"]), []).append(u["recall"])
    paired = {}
    arm_shas = {}
    for u in pu:
        key = (u["k_total"], u["bank_overlap"], u["routing_noise"])
        paired.setdefault(key, {})[u["regime"]] = u["recall"]
        arm_shas.setdefault(key, {})[u["regime"]] = u["arm_sha256"]
    n_pass = n_sat = n_floor = n_discrim = n_arms_differ = 0
    HP_SAT = 0.995
    HP_PASS = 0.50
    HP_DISCRIM = 0.20
    HP_FLOOR = 0.05
    paired_pts = 0
    for key, arms in paired.items():
        if "SUBSTRATE" not in arms or "RANDOM" not in arms:
            continue
        paired_pts += 1
        sub_r = arms["SUBSTRATE"]
        rnd_r = arms["RANDOM"]
        margin = sub_r - rnd_r
        if sub_r >= HP_PASS and margin > HP_DISCRIM:
            n_pass += 1
        if sub_r >= HP_SAT:
            n_sat += 1
        if margin <= HP_FLOOR:
            n_floor += 1
        if margin > HP_DISCRIM:
            n_discrim += 1
        if arm_shas[key]["SUBSTRATE"] != arm_shas[key]["RANDOM"]:
            n_arms_differ += 1
    llm = sum(u.get("_llm_forward_calls_at_inference", -1) for u in pu)
    return {
        "seed": seed,
        "verdict": m["verdict"],
        "n_per_unit": len(pu),
        "n_paired": paired_pts,
        "n_pass": n_pass,
        "n_saturate": n_sat,
        "n_floor": n_floor,
        "n_discrim": n_discrim,
        "n_arms_differ": n_arms_differ,
        "llm_calls": llm,
        "gpu_util_p50": m.get("gpu_util_p50"),
        "K_measured": sorted(set(u["k_total"] for u in pu)),
        "K_pre_reg": [4096, 8192, 16384, 32768, 65536],
    }


def verify_pattern_completion() -> dict:
    cell = "exp_substrate_pattern_completion_corruption_cliff_phase_diagram_v1"
    path = ROOT / f"data/{cell}/metrics.json"
    m = json.loads(path.read_text(encoding="utf-8"))
    pm = m["phase_map"]
    tier = {}
    for p in pm:
        t = p["verdict_tier_per_point"]
        tier[t] = tier.get(t, 0) + 1
    # Per-corruption analysis
    cliff_by_iters = {}
    for p in pm:
        c = p["corruption_frac"]
        it = p["cleanup_iters"]
        N = p["N"]
        cliff_by_iters.setdefault((it, N), {})[c] = p["top1_substrate"]
    # Check iters identical-across-T at each (N, corruption)
    iters_differentiate = False
    for N in {2048, 4096, 8192, 16384}:
        for c in {0.10, 0.30, 0.50, 0.70, 0.85, 0.95}:
            vals = [cliff_by_iters.get((it, N), {}).get(c) for it in (1, 5, 20)]
            if len(set(round(v, 4) if v is not None else None for v in vals)) > 1:
                iters_differentiate = True
    return {
        "verdict": m["verdict"],
        "n_pm": len(pm),
        "tier_dist": tier,
        "iters_differentiate_anywhere": iters_differentiate,
        "arms_differ": m.get("arms_differ_sha256", {}).get("differ"),
        "device": m.get("device"),
        "gpu_util_estimate": m.get("gpu_util_estimate"),
        "cardinality_ok": m.get("cardinality_ok"),
        "obs": m.get("observed_n_units"),
        "exp": m.get("expected_n_units"),
    }


# =========================================================================
# A5 PRE: read + count + parse
# =========================================================================

def a5_pre(p: Path) -> dict:
    if not p.exists():
        return {"path": str(p), "line_count": 0, "last_line_ok": True, "all_parse": True}
    n = 0
    last = ""
    all_parse = True
    with open(p, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                n += 1
                last = line
                try:
                    json.loads(line)
                except Exception:
                    all_parse = False
    last_ok = True
    if last:
        try:
            json.loads(last)
        except Exception:
            last_ok = False
    return {"path": str(p), "line_count": n, "last_line_ok": last_ok, "all_parse": all_parse}


def a5_atomic_append(p: Path, records: list[dict]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    # read existing
    existing = p.read_text(encoding="utf-8") if p.exists() else ""
    tmp = p.with_suffix(p.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(existing)
        if existing and not existing.endswith("\n"):
            f.write("\n")
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, p)


def a5_post(p: Path, pre: dict, expected_delta: int) -> tuple[bool, dict]:
    post = a5_pre(p)
    delta = post["line_count"] - pre["line_count"]
    ok = (
        delta == expected_delta
        and post["last_line_ok"]
        and post["all_parse"]
    )
    return ok, {"pre_count": pre["line_count"], "post_count": post["line_count"],
                "delta": delta, "expected_delta": expected_delta,
                "last_line_ok": post["last_line_ok"], "all_parse": post["all_parse"]}


# =========================================================================
# ATOMS
# =========================================================================

WM_ATOM = {
    "id": "T3/EXP_substrate_wm_multibank_K_cliff_phase_diagram_v1_3seed_MEASURED_MECHANISM_capacity_bound_by_construction_saturation_2026-06-28",
    "name": (
        "WM multi-bank K-cliff phase diagram v1 (3-seed seeds 7/13/19) -- "
        "MEASURED_MECHANISM (robustness bound) NOT chain-grade. SUBSTRATE recall 1.0000 at every measured "
        "(K, ov, rn) in K<=16384 x overlap{0,0.1,0.3} x routing_noise{0,0.05,0.15}; K=32768/65536 "
        "VRAM-probe-denied (not empirically cliffed); cliff at K=16384 is GPU memory ceiling, not "
        "substrate mechanism transition; by-construction-saturation per BIAS-Q + Fix #28."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "3-seed full phase-diagram landing on overnight_queue GPU (devices cuda:0). "
        "Orchestrator framing: HARD_PASS x3 chain-grade candidate; cert-owner ruling: MEASURED_MECHANISM "
        "(cert-neutral). Verify-off-data: of the pre-reg's 5 K-values {4096,8192,16384,32768,65536}, "
        "only K in {4096,8192,16384} actually ran; K=32768 and K=65536 hit HP_VRAM_PROBE_BREACH "
        "(est_peak=5.51GB > budget=4.88GB on 8GB GPU). At every measured (K,ov,rn) point per seed, "
        "SUBSTRATE recall = 1.0000 (n_saturate=27/27 of measured pairs across K<=16384, overlap{0,0.1,0.3}, "
        "routing_noise{0,0.05,0.15}). Discriminator SUBSTRATE-RANDOM>0.20 trivially passes since RANDOM "
        "is mathematically pinned at 1/65536 ~ 1.5e-5. The 'cliff at K=16384' reported by the cell is a "
        "VRAM-probe ceiling (cell treats probe-denials as CLIFF markers per pre-reg spec) NOT an "
        "empirically observed substrate-mechanism transition. Per-seed n_units_observed=54 (27 paired "
        "x 2 arms), 36 probe-denied points, cardinality_ok=True per cell convention (54+36=90 expected). "
        "Substrate-only gate PASSES (_llm_forward_calls_at_inference=0 across all units, all seeds). "
        "GPU util p50 = 77/77/88% across seeds 7/13/19 (Fix #24 satisfied; valid for runtime measurement). "
        "3-seed convergence on aggregate (pass=27 sat=27 floor=0 probe_cliffs=36 arms_differ=27/9 "
        "identical across seeds) is convergence on SATURATION not on a discriminator; arm_sha256 differs "
        "cleanly per seed (48de93/686c87/6ceea1) confirming genuine independent runs. "
        "WHAT THIS DOES PROVE (the proven bound that justifies MEASURED_MECHANISM, not nothing): "
        "the substrate WM multi-bank mechanism is empirically robust to (overlap up to 0.30 + "
        "routing_noise up to 0.15) at K up to 16384. No degradation observed in any direction within the "
        "measurement regime. This is a useful characterization of the mechanism's robustness profile, "
        "with the caveat that the cliff (if it exists below the VRAM ceiling) was not localized. "
        "WHAT THIS DOES NOT PROVE: where the K-cliff actually is; whether overlap or routing_noise can "
        "cliff the mechanism at higher K; whether the cell's cliff_per_ov_rn={'...': 16384} reflects "
        "substrate behavior or hardware limitation. "
        "SCHEMA BUG in the cell (load-bearing for v2): HARD_FAIL_SATURATION_ONLY check at "
        "experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_7_v1.py:887 tests "
        "n_saturate == len(phase_map) where len(phase_map) includes probe-denied points (verdict_tier="
        "'CLIFF'). With 36/45 probe-denied, n_saturate=27 != 45 always, so the gate cannot fire even "
        "when 100% of measured points saturate. v2 should respec to n_saturate / n_measured. "
        "TEST-DESIGN RECOMMENDATION for v2: (a) need 16GB+ GPU OR smaller K_per_bank to localize cliff "
        "beyond K=16384; (b) alternatively pivot to discriminating regime (smaller N_DIM=4096 OR higher "
        "k_per_bank=128 to push alpha past 1.0 where chain-grade primitive previously cliffed); (c) "
        "respec HARD_FAIL_SATURATION_ONLY to fire on measured-points-only fraction; (d) consider sweeping "
        "k_per_bank as primary axis instead of K_total -- crosstalk per bank is the more direct phase "
        "control variable. "
        "ANALOGY TO PRIOR g1 PATTERN: cert-owner overrides Director on by-construction-saturation; "
        "atomized 2026-06-22 (feedback_skunkworks_correctly_overrides_director_via_by_construction_"
        "saturation). Same root cause: discriminator > 0.20 looks like a chain-grade pass when "
        "SUBSTRATE = 1.0 by saturation and RANDOM = mathematical floor by construction. Per-arm metrics "
        "directly read, not from verdict_msg framings (Fix #28)."
    ),
    "aliases": [
        "wm_multibank_K_cliff_phase_diagram_v1_3seed_MM",
        "WM_K_cliff_VRAM_ceiling_not_substrate_cliff_2026-06-28",
        "WM_multibank_robustness_bound_overlap0p3_routingnoise0p15_at_K_le_16384",
    ],
    "metadata": {
        "provenance_quality": "DIRECT_OFF_DATA",
        "cert_status": "measured_mechanism",
        "cert_class": "mechanism_characterization",
        "cert_increment_delta": 0,
        "atomized_by": SOURCE_TAG,
        "atomized_date": ATOMIZED_DATE,
        "verified_off_data": True,
        "raw_metrics_paths": [
            "data/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_7_v1/metrics.json",
            "data/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_13_v1/metrics.json",
            "data/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_19_v1/metrics.json",
        ],
        "prereg_path": "preregs/2026-06-28_substrate_wm_multibank_K_cliff_phase_diagram_v1.md",
        "cell_paths": [
            "experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_7_v1.py",
            "experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_13_v1.py",
            "experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_19_v1.py",
        ],
        "K_measured": [4096, 8192, 16384],
        "K_pre_reg_unmeasured_vram_probe_denied": [32768, 65536],
        "n_saturate_per_seed": 27,
        "n_measured_paired_per_seed": 27,
        "n_probe_denied_per_seed": 36,
        "saturation_fraction_of_measured": 1.0,
        "discriminator_margin_substrate_minus_random": "approximately 1.0 at every measured point (by-construction; RANDOM is mathematical 1/CB floor)",
        "gpu_util_p50_per_seed": [77.0, 77.0, 88.0],
        "fix_24_gpu_util_gate": True,
        "substrate_only_gate_pass_all_seeds": True,
        "llm_calls_at_inference": 0,
        "arms_differ_at_27_pts_per_seed": True,
        "arm_sha_per_seed": {"seed_7": "48de93145adb3df4", "seed_13": "686c8780e7b9a470", "seed_19": "6ceea19df623e6bd"},
        "by_construction_saturation_flag": True,
        "bias_q_suspect_1_000_result": True,
        "fix_28_per_arm_direct_read_not_verdict_msg": True,
        "schema_bug_in_cell_saturation_only_gate_line_887": True,
        "schema_bug_description": "HARD_FAIL_SATURATION_ONLY tests n_saturate == len(phase_map); len(phase_map) includes probe-denied points with verdict_tier='CLIFF'; gate cannot fire when probe denials inflate denominator",
        "test_design_recommendation_v2": [
            "16GB+ GPU OR smaller K_per_bank to localize cliff beyond K=16384",
            "pivot to discriminating regime: N_DIM=4096 or k_per_bank=128 to push alpha past 1.0",
            "respec HARD_FAIL_SATURATION_ONLY to n_saturate / n_measured (exclude probe-denials from denominator)",
            "consider k_per_bank as primary axis (crosstalk per bank is more direct phase control)",
        ],
        "robustness_bound_proven": "substrate WM multi-bank robust to overlap up to 0.30 + routing_noise up to 0.15 at K up to 16384 (no degradation in measured regime, 3 seeds, 27 paired points per seed)",
        "what_not_proven": "where the K-cliff actually is; cliff_per_ov_rn=16384 is VRAM ceiling not substrate cliff",
        "composes_with": [
            "feedback_cert_owner_overrides_director_via_by_construction_saturation_2026-06-22",
            "feedback_fix28_per_arm_metrics_not_summary_verdict_text_2026-06-22",
            "META_RULE_AA_FAIRNESS_BEFORE_TIER (gate (c) regime exercises mechanism)",
            "META_RULE_AG_band_calibration_regime_check",
            "BIAS_Q_suspect_1_000_results",
        ],
        "ts_iso_atomized": "2026-06-28T17:30Z",
        "cell_commit": None,  # commits not auto-tagged; cell-source paths above
    },
}


PC_ATOM = {
    "id": "T3/EXP_substrate_pattern_completion_corruption_cliff_phase_diagram_v1_MIDDLE_BAND_sharp_step_cliff_at_corruption_0p5_iters_falsified_2026-06-28",
    "name": (
        "Pattern completion corruption-cliff phase diagram v1 -- MIDDLE_BAND "
        "(sharp-step cliff localized at corruption_frac approx 0.5; H2 iters-extend-cliff FALSIFIED; "
        "H1 N-shifts-cliff PARTIALLY-FALSIFIED; coarse-grid by-construction saturation per BIAS-Q)"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Single-cell full landing on remote GPU (device=cuda, gpu_util_estimate=0.95). Orchestrator "
        "framing: MIDDLE_BAND by-construction saturation; cert-owner ruling: MIDDLE_BAND / "
        "mechanism_characterization (concurs). Verify-off-data: 72/72 phase points ran "
        "(cardinality_ok=True). Tier distribution: 24 SATURATED + 48 FLOOR + 0 HARD_PASS + 0 "
        "MIDDLE_BAND_per_point + 0 HARD_FAIL. Sweep produces a bimodal step: corruption_frac in "
        "{0.10, 0.30} ALL 24 (N x iters) points saturate at top1_substrate=1.0000; "
        "corruption_frac in {0.50, 0.70, 0.85, 0.95} ALL 48 points floor at top1_substrate <= 0.0020. "
        "The pre-reg's HARD_PASS band [0.80, 0.95) and per-point MIDDLE_BAND [0.50, 0.80) are EMPTY "
        "-- the coarse corruption grid stepped right over the bistable transition zone. H1 prediction "
        "(cliff shifts right with N): FALSIFIED -- cliff at corruption_frac=0.5 for ALL N in {2048, 4096, "
        "8192, 16384}; 4x N variation produced zero shift. H2 prediction (iterative cleanup extends cliff): "
        "FALSIFIED -- cleanup_iters in {1, 5, 20} produces IDENTICAL top1_substrate at every "
        "(N, corruption_frac) cell. T=20 doesn't beat T=1 anywhere. This is a CLEAN PROVEN NEGATIVE for "
        "the iterative-attractor-basin-grows hypothesis. arms_differ_sha256.differ=True (substrate vs "
        "random hashes cleanly distinct). Substrate-only-decode gate PASS (_LLM_CALL_COUNTER asserted "
        "0 at exit line 1140). No silent except (META_RULE_J satisfied). "
        "CLIFF IS REAL AND SHARP: corruption_frac approx 0.5 matches CRLB theory (1-step cliff 0.46-0.49 "
        "per overlap-floor analysis). Mechanism transitions cleanly within a band narrower than the test "
        "grid resolution (0.30 -> 0.50 saw 1.0 -> 0.002 in one step). This IS measurement -- we know the "
        "cliff is sharp -- it's just not a CHARACTERIZATION of the cliff edge. "
        "TEST-DESIGN RECOMMENDATION for v2 (META_RULE_AG band-calibration regime check): respec "
        "corruption_frac grid to target [0.30, 0.70] where mechanism is NOT saturated NOT floored. "
        "Suggested finer sweep: {0.40, 0.42, 0.44, 0.46, 0.48, 0.50, 0.52, 0.54, 0.56, 0.60}. THIS is "
        "where iterative cleanup (T=20 vs T=1) might actually differentiate -- the basin-of-attraction "
        "question is meaningless at saturation OR at floor; it only matters at the edge. v1's coarse "
        "grid stepped right over the interesting regime. Also worth re-examining the H2 falsification "
        "at finer resolution: T may still falsified-everywhere, but if so, that's a STRONGER negative."
    ),
    "aliases": [
        "pattern_completion_corruption_cliff_v1_MB_byconstruction_2026-06-28",
        "pattern_completion_iterative_cleanup_iters_5_vs_20_FALSIFIED",
        "pattern_completion_cliff_at_corruption_0p5_sharp_step",
    ],
    "metadata": {
        "provenance_quality": "DIRECT_OFF_DATA",
        "cert_status": "middle_band",
        "cert_class": "mechanism_characterization",
        "cert_increment_delta": 0,
        "atomized_by": SOURCE_TAG,
        "atomized_date": ATOMIZED_DATE,
        "verified_off_data": True,
        "raw_metrics_path": "data/exp_substrate_pattern_completion_corruption_cliff_phase_diagram_v1/metrics.json",
        "prereg_path": "preregs/2026-06-28_substrate_pattern_completion_corruption_cliff_phase_diagram_v1.md",
        "cell_path": "experiments/exp_substrate_pattern_completion_corruption_cliff_phase_diagram_v1.py",
        "n_phase_points": 72,
        "tier_distribution": {"SATURATED": 24, "FLOOR": 48, "HARD_PASS": 0, "MIDDLE_BAND": 0, "HARD_FAIL": 0},
        "cliff_corruption_frac_empirical": 0.5,
        "cliff_corruption_frac_predicted_CRLB": "0.46 to 0.49 (1-step random-vector overlap floor)",
        "cliff_matches_theory": True,
        "h1_N_shifts_cliff_right": "FALSIFIED (cliff at 0.5 for all N in {2048,4096,8192,16384})",
        "h2_iters_extend_cliff": "FALSIFIED (iters in {1,5,20} produce identical results at every (N, corruption))",
        "iters_differentiate_anywhere": False,
        "arms_differ_sha256": True,
        "device": "cuda",
        "gpu_util_estimate": 0.95,
        "substrate_only_gate_pass": True,
        "llm_calls_at_inference": 0,
        "no_silent_except": True,
        "by_construction_saturation_flag": True,
        "bias_q_suspect_1_000_result": True,
        "test_design_recommendation_v2": [
            "respec corruption_frac grid to {0.40, 0.42, 0.44, 0.46, 0.48, 0.50, 0.52, 0.54, 0.56, 0.60}",
            "target [0.30, 0.70] band where mechanism is neither saturated nor floored (META_RULE_AG)",
            "iters_falsification re-test at finer resolution (T differentiation only matters near cliff edge)",
            "consider M_items sweep: alpha=M/N might modulate cliff sharpness",
        ],
        "proven_negative_h2_iters": "iterative softmax-Hopfield cleanup T=20 does NOT extend the corruption cliff beyond T=1 in the measured regime (CERT-neutral but useful negative bound)",
        "composes_with": [
            "META_RULE_AG_band_calibration_regime_check",
            "BIAS_Q_suspect_1_000_results",
            "feedback_fix28_per_arm_metrics_not_summary_verdict_text_2026-06-22",
            "three_smoke_disciplines_band_floor_is_MIDDLE_BAND_not_HARD_PASS",
        ],
        "ts_iso_atomized": "2026-06-28T17:30Z",
        "cell_commit": None,
    },
}


# =========================================================================
# CERT LEDGER ROWS (rulings)
# =========================================================================

WM_LEDGER = {
    "ts": time.time(),
    "op": "cert_ruling",
    "atom_id": f"math::{WM_ATOM['id']}",
    "cert_status": "measured_mechanism",
    "cert_class": "mechanism_characterization",
    "verified_off_data": True,
    "atomized_by": SOURCE_TAG,
    "cell_commit": None,
    "verdict": (
        "MEASURED_MECHANISM_3_seed_WM_multibank_K_cliff_phase_diagram_v1_saturation_at_every_measured_point_K_le_16384_overlap_up_to_0p30_routing_noise_up_to_0p15_K_32768_65536_VRAM_probe_denied_not_substrate_cliffed_cliff_per_ov_rn_16384_is_GPU_memory_ceiling_not_substrate_mechanism_transition_discriminator_substrate_minus_random_trivially_passes_by_construction_RANDOM_pinned_at_mathematical_1_over_CB_floor_orchestrator_HARD_PASS_framing_OVERRIDDEN_per_g1_pattern_2026-06-22_cert_owner_overrides_director_via_by_construction_saturation"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "metrics_path_seed_7": "data/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_7_v1/metrics.json",
        "metrics_path_seed_13": "data/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_13_v1/metrics.json",
        "metrics_path_seed_19": "data/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_19_v1/metrics.json",
        "prereg_path": "preregs/2026-06-28_substrate_wm_multibank_K_cliff_phase_diagram_v1.md",
        "cell_paths": [
            "experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_7_v1.py",
            "experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_13_v1.py",
            "experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_19_v1.py",
        ],
        "atom_qualified_id": f"math::{WM_ATOM['id']}",
    },
    "supersedes": None,
    "note": (
        "wm_multibank_K_cliff_phase_diagram_v1_3seed_HARD_PASS_orchestrator_framing_overridden_to_MEASURED_MECHANISM_per_by_construction_saturation_at_every_measured_point_K_up_to_16384_secondary_axes_overlap_routing_noise_all_saturate_too_K_32768_65536_VRAM_probe_denied_not_substrate_cliff_robustness_bound_real_proven_substrate_robust_to_overlap_0p30_routing_noise_0p15_at_K_le_16384_test_design_v2_needs_16GB_GPU_OR_pivot_to_discriminating_regime_alpha_above_1p0_OR_swap_to_k_per_bank_as_primary_axis_substrate_only_gate_PASS_fix_24_gpu_util_PASS_arms_differ_PASS_3_seed_convergence_on_saturation_not_on_discriminator_arm_sha_per_seed_genuinely_independent"
    ),
}


PC_LEDGER = {
    "ts": time.time(),
    "op": "cert_ruling",
    "atom_id": f"math::{PC_ATOM['id']}",
    "cert_status": "middle_band",
    "cert_class": "mechanism_characterization",
    "verified_off_data": True,
    "atomized_by": SOURCE_TAG,
    "cell_commit": None,
    "verdict": (
        "MIDDLE_BAND_pattern_completion_corruption_cliff_v1_FULL_72_points_24_SATURATED_48_FLOOR_0_HARD_PASS_sharp_step_cliff_at_corruption_frac_0p5_matches_CRLB_theory_0p46_to_0p49_H1_N_shifts_cliff_FALSIFIED_cliff_at_0p5_for_all_N_in_2048_4096_8192_16384_H2_iters_extend_cliff_FALSIFIED_T_1_T_5_T_20_identical_everywhere_arms_differ_TRUE_substrate_only_gate_PASS_llm_calls_0_no_silent_except_by_construction_saturation_coarse_corruption_grid_stepped_over_bistable_transition_zone_test_design_v2_respec_grid_to_0p40_to_0p60_finer_band_calibration_per_META_RULE_AG"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "metrics_path": "data/exp_substrate_pattern_completion_corruption_cliff_phase_diagram_v1/metrics.json",
        "prereg_path": "preregs/2026-06-28_substrate_pattern_completion_corruption_cliff_phase_diagram_v1.md",
        "cell_path": "experiments/exp_substrate_pattern_completion_corruption_cliff_phase_diagram_v1.py",
        "atom_qualified_id": f"math::{PC_ATOM['id']}",
    },
    "supersedes": None,
    "note": (
        "pattern_completion_corruption_cliff_v1_MIDDLE_BAND_concurs_with_orchestrator_framing_by_construction_saturation_BIAS_Q_cliff_at_corruption_0p5_real_and_sharp_matches_CRLB_predictions_H1_N_dependence_FALSIFIED_H2_iters_extend_cliff_FALSIFIED_proven_negative_for_iterative_attractor_basin_grows_hypothesis_within_measured_grid_test_design_v2_respec_to_finer_corruption_band_0p40_to_0p60_per_META_RULE_AG_to_actually_see_iters_T_differentiation_if_any_exists_near_edge"
    ),
}


def main() -> int:
    if "--dry-run" not in sys.argv and "--apply" not in sys.argv:
        print(__doc__)
        print("\nUSAGE: python tools/skunkworks_atomize_wm_kcliff_MM_pattern_completion_MB_2026-06-28.py --dry-run|--apply")
        return 1

    # OFF-DATA verify first (no writes; abort on any sanity issue)
    print("=== OFF-DATA RECOMPUTE (verify before atomize) ===")
    for seed in (7, 13, 19):
        r = verify_wm_kcliff(seed)
        print(f"WM seed {seed}: {json.dumps(r, sort_keys=True)}")
        assert r["llm_calls"] == 0, f"WM seed {seed} substrate-only gate violated"
        assert r["n_paired"] == 27, f"WM seed {seed} n_paired != 27 (got {r['n_paired']})"
        assert r["n_saturate"] == 27, f"WM seed {seed} saturation count drift (expected 27, got {r['n_saturate']})"
        assert r["n_arms_differ"] == 27, f"WM seed {seed} arms_differ drift"
        assert r["K_measured"] == [4096, 8192, 16384], f"WM seed {seed} K_measured drift"
    pc = verify_pattern_completion()
    print(f"PC: {json.dumps(pc, sort_keys=True)}")
    assert pc["tier_dist"] == {"SATURATED": 24, "FLOOR": 48}, f"PC tier drift: {pc['tier_dist']}"
    assert pc["iters_differentiate_anywhere"] is False, "PC iters DO differentiate somewhere; verify"
    assert pc["arms_differ"] is True, "PC arms collapsed"
    assert pc["n_pm"] == 72, f"PC n_pm drift: {pc['n_pm']}"
    print("OFF-DATA RECOMPUTE: PASS\n")

    if "--dry-run" in sys.argv:
        print("\n=== DRY RUN ===")
        print(f"Would append 2 atoms to math/atoms.jsonl (WM + PC)")
        print(f"Would append 2 cert_ruling rows to meta/cert_ledger.jsonl")
        print(f"WM atom id (truncated): {WM_ATOM['id'][:120]}")
        print(f"PC atom id (truncated): {PC_ATOM['id'][:120]}")
        print(f"CERT delta: +0 (both MM; CERT-neutral)")
        return 0

    # A5 PRE
    print("=== A5 PRE ===")
    math_pre = a5_pre(MATH_ATOMS)
    cert_pre = a5_pre(CERT_LEDGER)
    print(f"math atoms PRE: {math_pre}")
    print(f"cert_ledger PRE: {cert_pre}")
    assert math_pre["all_parse"], "math atoms.jsonl has unparseable line PRE; ABORT"
    assert cert_pre["all_parse"], "cert_ledger.jsonl has unparseable line PRE; ABORT"

    # A5 WRITE: atomic append
    print("\n=== A5 WRITE (atomic tmp -> os.replace) ===")
    a5_atomic_append(MATH_ATOMS, [WM_ATOM, PC_ATOM])
    a5_atomic_append(CERT_LEDGER, [WM_LEDGER, PC_LEDGER])

    # A5 POST verify
    print("\n=== A5 POST ===")
    math_ok, math_info = a5_post(MATH_ATOMS, math_pre, expected_delta=2)
    cert_ok, cert_info = a5_post(CERT_LEDGER, cert_pre, expected_delta=2)
    print(f"math atoms POST: ok={math_ok} {math_info}")
    print(f"cert_ledger POST: ok={cert_ok} {cert_info}")
    if not (math_ok and cert_ok):
        print("\nA5 POST FAILED; ABORT.")
        return 1

    # Round-trip: verify written atoms readable
    print("\n=== ROUND-TRIP VERIFY ===")
    found_ids = set()
    with open(MATH_ATOMS, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                found_ids.add(rec["id"])
    for need in (WM_ATOM["id"], PC_ATOM["id"]):
        if need not in found_ids:
            print(f"ROUND-TRIP FAIL: missing {need[:80]}")
            return 1
        print(f"  PASS: {need[:80]}")

    print("\nDONE. CERT delta: +0 (both MM; cert-neutral; chain-grade headline unchanged).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
