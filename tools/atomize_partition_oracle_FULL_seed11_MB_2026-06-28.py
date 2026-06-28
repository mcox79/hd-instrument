"""
A5-gated atomize: partition_oracle_v5_hardened_FULL_seed_11_v1 MIDDLE_BAND.

Verdict: MIDDLE_BAND. Cert class: mechanism_characterization. CERT delta = 0.

OFF-DATA recompute (verify-OFF-DATA, NOT verdict_msg):
  A=0.295 B=0.835 C=0.905 D=0.585 E=0.000
  lift_B_A=0.540 (>= 0.20) PASS
  lift_B_E=0.835 (>= 0.30) PASS
  ARM_B in HP_band[0.50, 0.95]                  PASS
  saturation=False                               PASS
  arms_distinct=True (5 unique SHA-256)          PASS
  cardinality_ok=True (5 arms observed)          PASS
  ONLY FAILING GATE: baseline_rail_ok=False (A=0.295 < 0.30 floor; breach 0.005)

Smoke->FULL delta (DISCRIMINATOR-MUST-SURVIVE-SCALE check, META_RULE_G):
  A_smoke=0.39 A_full=0.295 delta=-0.095 (baseline drifted DOWN below rail)
  B_smoke=0.90 B_full=0.835 delta=-0.065 (oracle held)
  lift_smoke=0.51 lift_full=0.54 (discriminator did NOT narrow; lift actually grew +0.03)

Honest characterization: this is NOT a discriminator-collapse-at-scale failure.
The mechanism (partition-oracle goal-conditioning) is intact and in the HP band.
The MIDDLE_BAND verdict is driven by baseline rail breach (BIAS-S), NOT mechanism narrowing.
This is a real signal at single-seed FULL. Chain-grade promotion gates on:
  (a) seeds 13 + 19 aggregation (pending in remote_cpu_queue) for cv check
  (b) baseline rail interpretation: 0.005 below floor is within stochastic noise
      at n_chains_test=200 (binomial std ~= sqrt(0.295*0.705/200) = 0.032);
      single-seed rail breach should not block promotion if cross-seed mean recovers

A5 protocol:
  1. Read pre-write line counts; build atom + ledger row in memory
  2. Append to math/atoms.jsonl via tmp -> os.replace
  3. Append to meta/cert_ledger.jsonl via tmp -> os.replace
  4. Verify-load: count delta == +1 each; tail-line parses as JSON; round-trip ID match

Anchors:
  - notes/skunkworks_landed_vet_partition_oracle_FULL_seed11_MB_2026-06-28.md (NOT YET WRITTEN; SKIPPED per discipline)
  - metrics: data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_11_v1/metrics.json
  - prereg:  preregs/2026-06-28_substrate_multihop_partition_oracle_v5_hardened_v1.md
  - cell:    experiments/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_11_v1.py
"""

import json
import os
import time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

METRICS_PATH = "data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_11_v1/metrics.json"
PREREG_PATH = "preregs/2026-06-28_substrate_multihop_partition_oracle_v5_hardened_v1.md"
CELL_PATH = "experiments/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_11_v1.py"

ATOMIZED_BY = "skunkworks_atomize_partition_oracle_FULL_seed11_MB_2026-06-28"
ATOMIZED_DATE = "2026-06-28"
CELL_COMMIT = "e362270f"  # latest staging commit


# ============================================================
# ATOM (math, T3 experiment_record, MIDDLE_BAND mechanism_characterization)
# ============================================================
atom = {
    "id": "T3/EXP_partition_oracle_goal_conditioning_barrier_1_MIDDLE_BAND_at_FULL_2026-06-28",
    "name": (
        "Partition-oracle goal-conditioning v5-hardened FULL seed_11 -- MIDDLE_BAND "
        "(mechanism intact at HP band; baseline rail breached by 0.005 at single seed; "
        "discriminator did NOT narrow at scale)"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Barrier 1 (compositional reasoning depth) test of partition-oracle goal-conditioning. "
        "Single seed (seed=11) FULL at N=8192 V_C=4000 V_P=10 depth=15 n_chains_test=200. "
        "5-arm discriminator (BASELINE_A / ORACLE_B_psz800 / ORACLE_C_psz400 / ORACLE_D_psz2000 / RANDOM_E). "
        "OFF-DATA recompute confirms: A=0.295 B=0.835 C=0.905 D=0.585 E=0.000; "
        "lift_B_A=0.540 (>=0.20 PASS); lift_B_E=0.835 (>=0.30 PASS); ARM_B in HP band [0.50, 0.95] PASS; "
        "saturation=False PASS; arms_distinct=True (5 unique SHA-256); cardinality_ok=True (5 arms). "
        "ONLY failing gate: baseline_rail_ok=False (A=0.295 < 0.30 floor; breach 0.005 = ~1 chain at n=200). "
        "Smoke->FULL delta: A 0.39->0.295 (-0.095); B 0.90->0.835 (-0.065); lift 0.51->0.54 (+0.03). "
        "IMPORTANT: discriminator did NOT narrow at scale; lift actually GREW slightly. "
        "MIDDLE_BAND verdict is driven by baseline rail breach (BIAS-S sanity check), "
        "NOT by mechanism-discriminator-collapse-at-scale (META_RULE_G). "
        "Mechanism (partition-oracle goal-conditioning narrows search via psz_B=800 5-partition oracle) is real. "
        "Cross-seed cv check pending: seeds 13 + 19 still queued in remote_cpu_queue. "
        "Chain-grade promotion gate: (a) seeds 13+19 land + cross-seed cv < 0.15 + at least 2 of 3 "
        "satisfy baseline rail; OR (b) USER + research consensus that 0.005 rail breach is within "
        "stochastic noise at n_chains_test=200 (binomial std ~= 0.032). "
        "Do NOT close partition-oracle direction; do NOT promote to chain-grade yet. "
        "Per feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28: MB does NOT trigger "
        "closure discipline; mechanism is characterized at a regime that did not chain-grade at this single seed."
    ),
    "aliases": [
        "partition_oracle_goal_conditioning_barrier_1_MIDDLE_BAND_at_FULL_2026-06-28",
        "partition_oracle_v5_hardened_FULL_seed_11_MB",
        "barrier_1_compositional_reasoning_depth_15_MIDDLE_BAND_single_seed",
    ],
    "metadata": {
        "provenance_quality": "MEASURED",
        "cert_status": "middle_band",
        "cert_class": "mechanism_characterization",
        "verdict": "MIDDLE_BAND",
        "verdict_subtype": "PARTIAL_MECHANISM_AT_DEPTH15_BASELINE_RAIL_BREACH",
        "cell_commit": CELL_COMMIT,
        "cell_path": CELL_PATH,
        "prereg_path": PREREG_PATH,
        "metrics_path": METRICS_PATH,
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "verified_off_data": True,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via python -c on metrics.json per_seed[0]: "
            "A=0.295 B=0.835 lift_B_A=0.540 lift_B_E=0.835 baseline_rail_ok=False "
            "(A=0.295 < 0.30 by 0.005); HP gates B-in-band + lift_B_A + lift_B_E + saturation + arms_distinct + cardinality all PASS; "
            "ONLY MB-driver is baseline rail breach; smoke->full lift delta +0.03 = NO discriminator narrowing"
        ),
        "n_seeds_run": 1,
        "n_seeds_planned_total": 3,
        "seeds_pending": [13, 19],
        "seeds_pending_queue": "remote_cpu_queue",
        "regime": {
            "N": 8192,
            "V_C": 4000,
            "V_P": 10,
            "depth": 15,
            "n_chains_train": 200,
            "n_chains_test": 200,
            "encoder": "SUBSTRATE_NATIVE_BIPOLAR",
            "n_partitions_B": 5,
            "part_size_B": 800,
            "n_partitions_C": 10,
            "part_size_C": 400,
            "n_partitions_D": 2,
            "part_size_D": 2000,
        },
        "per_arm_top1": {
            "A_baseline_full_V_C": 0.295,
            "B_oracle_part_5_psz_800": 0.835,
            "C_oracle_part_10_psz_400": 0.905,
            "D_oracle_part_2_psz_2000": 0.585,
            "E_no_oracle_random_part_5": 0.000,
        },
        "lifts": {
            "lift_B_A": 0.540,
            "lift_B_E": 0.835,
            "lift_C_A": 0.610,
            "lift_D_A": 0.290,
        },
        "smoke_to_full_delta": {
            "A_smoke": 0.390,
            "A_full": 0.295,
            "A_delta": -0.095,
            "B_smoke": 0.900,
            "B_full": 0.835,
            "B_delta": -0.065,
            "lift_smoke": 0.510,
            "lift_full": 0.540,
            "lift_delta": 0.030,
            "discriminator_narrowed_at_scale": False,
            "discriminator_survives_scale_META_RULE_G": True,
            "mb_driver": "baseline_rail_breach_BIAS_S_only",
        },
        "gates_evaluated": {
            "B_in_HP_band_0p50_0p95": True,
            "lift_B_A_ge_0p20": True,
            "lift_B_E_ge_0p30": True,
            "saturation_lt_0p95": True,
            "arms_distinct_sha256_5_unique": True,
            "cardinality_ok_5_arms_5_expected": True,
            "baseline_A_in_rail_0p30_0p70": False,
            "cv_lt_0p15_cross_seed": "PENDING_seeds_13_19_aggregation",
        },
        "promotion_recommendation": (
            "WAIT for seeds 13 + 19 to land + cross-seed aggregation; "
            "if 2 of 3 seeds satisfy baseline rail AND cross-seed cv < 0.15 AND ARM_B stays in HP band, "
            "promote to chain-grade. If all 3 seeds breach baseline rail by similar margin, "
            "the rail floor itself (0.30) may need re-derivation from substrate-empirical anchor."
        ),
        "barrier_1_status": "MIDDLE_BAND_single_seed_pending_cross_seed_aggregation",
        "capability_closure_status": "DO_NOT_CLOSE_partition_oracle_direction",
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_AC", "META_RULE_AE", "META_RULE_AF", "META_RULE_AG",
            "META_RULE_AH", "META_RULE_AL", "META_RULE_AN", "META_RULE_H",
            "META_RULE_G", "BIAS-Q", "BIAS-N", "BIAS-S",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26",
            "Fix_28_per_arm_metrics_not_verdict_msg",
            "feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28",
        ],
        "next_actions": [
            "wait_for_seeds_13_19_landing_in_remote_cpu_queue",
            "post_hoc_cross_seed_cv_computation_when_all_3_land",
            "re_VET_at_3_seed_aggregation_for_chain_grade_promotion_decision",
            "no_new_dispatch_until_3_seed_aggregation_completes",
        ],
        "supersedes": None,
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================
# CERT_LEDGER ROW (op=cert_ruling; delta=0; mechanism_characterization)
# ============================================================
ledger_row = {
    "ts": time.time(),
    "op": "cert_ruling",
    "atom_id": f"math::{atom['id']}",
    "cert_status": "middle_band",
    "cert_class": "mechanism_characterization",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": CELL_COMMIT,
    "verdict": (
        "MIDDLE_BAND_single_seed_FULL_A0p295_B0p835_lift_0p540_HP_band_PASS_baseline_rail_breach_0p005_only"
        "_discriminator_did_NOT_narrow_at_scale_pending_seeds_13_19_aggregation_for_chain_grade_decision"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "metrics_path": METRICS_PATH,
        "prereg_path": PREREG_PATH,
        "cell_path": CELL_PATH,
        "atom_qualified_id": f"math::{atom['id']}",
    },
    "supersedes": None,
    "note": (
        "partition_oracle_v5_hardened_FULL_seed_11_MIDDLE_BAND_mechanism_intact_in_HP_band_"
        "lift_grew_smoke_to_full_baseline_rail_breach_drives_MB_pending_cross_seed_aggregation_"
        "DO_NOT_close_partition_oracle_direction_DO_NOT_promote_chain_grade_yet_"
        "barrier_1_compositional_reasoning_depth_15_promotion_gated_on_seeds_13_19_landing"
    ),
}


# ============================================================
# A5 WRITE PROTOCOL
# ============================================================
def append_jsonl_a5(path: Path, new_row: dict, label: str):
    """Atomic append with verify-load + integrity-check."""
    print(f"[A5] {label}: path={path}")
    assert path.exists(), f"target does not exist: {path}"

    # PRE: read full file + count
    with open(path, "r", encoding="utf-8") as f:
        pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")

    # Validate every pre-line parses (integrity)
    for i, ln in enumerate(pre_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")

    # Build new content
    new_line = json.dumps(new_row, ensure_ascii=True)
    # Round-trip validate the new row
    parsed_back = json.loads(new_line)
    assert parsed_back.get("id") == new_row.get("id") or parsed_back.get("atom_id") == new_row.get("atom_id"), \
        "round-trip ID mismatch"

    out_lines = pre_lines + [new_line]
    out_text = "\n".join(out_lines) + "\n"

    # tmp -> os.replace (atomic)
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(str(tmp_path), str(path))

    # POST: verify-load
    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1, f"count delta mismatch: {pre_count} -> {post_count}"

    # Tail must parse + match
    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"], f"tail id mismatch: {tail.get('id')} vs {new_row['id']}"
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"], f"tail atom_id mismatch"

    # Re-validate every line parses
    for i, ln in enumerate(post_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"POST integrity fail line {i+1}: {e}")

    print(f"[A5] {label}: OK (atomic append + verify-load + integrity-check)")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    print(f"[A5] atom_id = math::{atom['id']}")
    print(f"[A5] ledger op=cert_ruling cert_status={ledger_row['cert_status']} delta={ledger_row['cert_increment_delta']}")

    append_jsonl_a5(MATH_ATOMS, atom, "math/atoms.jsonl")
    append_jsonl_a5(CERT_LEDGER, ledger_row, "meta/cert_ledger.jsonl")

    print(f"[A5] DONE OK; CERT delta = 0; cert_class = mechanism_characterization")


if __name__ == "__main__":
    main()
