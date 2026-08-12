"""
A5-gated atomize: substrate-native char-trigram Wikipedia SCALE-UP N=10K FULL

INDEPENDENT OFF-DATA RECOMPUTE via .venv python (skunkworks 2026-07-03):

Pre-reg: preregs/2026-07-03_substrate_wikipedia_char_trigram_scale_up_full.md
Metrics: data/exp_substrate_wikipedia_char_trigram_scale_up_full_2026_07_03/metrics.json
Cell landed by cpu_runner_0 at commit 84c53803e.

Verify-per-arm (Fix#28) OFF DISK:
  run_mode=full VERIFIED
  cardinality_ok=True (6/6 expected units)
  arms_differ_verified=True; arm digests distinct across arms:
    ARM_CHAR_TRIGRAM_WIKIPEDIA_N10K = 591c3a5be65600cf (identical all 3 seeds -- see caveat)
    ARM_RANDOM_BASELINE_N10K seed_11=e2ecc070467df3fb seed_17=4fc1ff0c71481e0e seed_23=4508efcf6fd37b18
  ARM_CHAR_TRIGRAM_WIKIPEDIA_N10K per_seed r@5 = [0.7030, 0.7030, 0.7030]  mean 0.7030  std 0.0
  ARM_RANDOM_BASELINE_N10K per_seed r@5 = [0.0003, 0.0001, 0.0005]  mean 0.0003
  chance_r5 = 5/N = 5/10000 = 0.0005  (band_max_r5 = 0.0025)  baseline in-band VERIFIED

Cross-cell reference verifies:
  Smoke reference off disk: data/exp_substrate_wikipedia_char_trigram_baseline_smoke_2026_07_03/metrics.json
    ARM_CHAR_TRIGRAM_WIKIPEDIA r@5 = 0.854 at N=500
  delta_from_smoke_r5 = 0.703 - 0.854 = -0.151  VERIFIED
  bge_100k reference (2026-06-19 exp_wikipedia_ingest_100k_gpu_v1) r@5 = 0.992
  gap_to_bge_100k_ref_r5 = 0.992 - 0.703 = 0.289  VERIFIED
  Band [0.60, 0.90]: 0.703 IN-BAND -> MEASURED_BOUND per HP_MEASURED_BOUND_EXPECTED_BAND

DETERMINISM CAVEAT (recorded on atom, not a red flag):
  ARM_CHAR_TRIGRAM_WIKIPEDIA_N10K arm digest 591c3a5be65600cf is IDENTICAL across all 3 seeds
  (seeds 11, 17, 23) and r@5=0.7030 exactly. This is EXPECTED and CORRECT: the char-trigram
  encoder is a deterministic hash-based surface encoder (n_unique_trigrams=43986 identical
  across seeds; body_char_cap=800 fixed; n_dim=2048 fixed). The seed varies ONLY the random
  baseline arm (as intended). The 3-seed run does not provide cross-seed variance for the
  char-trigram arm because the mechanism is deterministic wrt corpus+encoder-params; the
  3-seed structure serves to verify baseline chance ~= observed random and confirm cardinality.
  Consequence: single-realization r@5=0.703 on wikipedia_100k title-body pair corpus at N=10K.

TIER RULING: CG_MEASURED_BOUND (proven bound; MEASURED MECHANISM).
  This is NOT a capability claim. It is a MECHANISM CHARACTERIZATION of the substrate-native
  char-trigram surface encoder's title<-body retrieval performance at N=10000 on Wikipedia
  title-body pair test corpus in a SUPERVISED-Wikipedia regime (test corpus IS the ground
  truth). Substrate has ingested no general knowledge; this measures the encoder mechanism.

  cert_increment_delta = +1 (proven bound counts toward CERT N per disposition ladder).

SCALING-LAW DATAPOINT (composes with smoke atom via arc):
  N=500  -> r@5 = 0.854
  N=10K  -> r@5 = 0.703  (delta -0.151 for 20x scale)
  N=100K -> r@5 = 0.992 with bge (different mechanism; not comparable for substrate encoder)
  Char-trigram degrades roughly log-scale as corpus grows (increasing hash-collision + shared
  trigram density between distinct articles). Discriminates from the concept-encoder arc:
  is PPMI/SVD better than surface trigrams at N=10K on Wikipedia? Open question.

META candidate deferred: only 2 datapoints (N=500, N=10K) -- not a scaling-law atom yet;
  the N=10K MEASURED_BOUND atom below documents the datapoint. If PPMI Wikipedia N=10K
  lands with r@5 that differentiates from char-trigram, a META synthesis atom composing
  char-trigram-vs-PPMI-Wikipedia-scaling becomes warranted.

Cross-arc concept-overlap check (substrate KB):
  bash tools/substrate_query.sh "char-trigram Wikipedia surface encoder scale retrieval"
  Top hits at cosine 0.30-0.32 are 2026-06-27 char-trigram-sufficiency drill for Mathlib
  (different corpus + task) and clean-encoder-tests notes. No prior "char-trigram Wikipedia
  scaling" atom in KB. Prior Wikipedia atom is T3/EXP_wikipedia_ingest_100k_gpu_v1 which
  is the BGE encoder reference used here as gap comparator. This atom is NOVEL for the
  substrate-native encoder-Wikipedia-scaling arc.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_landed_VET_substrate_wikipedia_char_trigram_scale_up_full_N10K_MB_2026-07-03"
ATOMIZED_DATE = "2026-07-03"

atom_MB = {
    "id": (
        "T3/EXP_substrate_wikipedia_char_trigram_scale_up_full_N10K_MEASURED_BOUND_"
        "substrate_native_surface_encoder_r5_0p703_in_band_0p60_0p90_3seed_"
        "delta_from_smoke_neg_0p151_gap_to_bge_100k_ref_pos_0p289_"
        "deterministic_encoder_seed_only_varies_random_baseline_"
        "supervised_wikipedia_regime_mechanism_characterization_not_capability_2026-07-03"
    ),
    "name": (
        "MEASURED_BOUND substrate-native char-trigram Wikipedia scale-up FULL N=10000: "
        "r@5 = 0.7030 (3-seed deterministic; cross-seed std=0 by design) IN expected "
        "band [0.60, 0.90]. delta_from_smoke_r5 = -0.151 (smoke N=500 r@5=0.854). "
        "gap_to_bge_100k_ref_r5 = +0.289 (bge N=100K r@5=0.992). random_baseline r@5 "
        "= 0.0003 in-band (chance = 5/N = 5e-4). MECHANISM CHARACTERIZATION at "
        "supervised-Wikipedia title<-body retrieval regime; NOT a capability claim -- "
        "substrate has ingested no general knowledge and cannot narrate this signal "
        "as English understanding. CERT +1 as proven bound."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "3-seed FULL substrate-native char-trigram surface encoder Wikipedia title<-body "
        "retrieval at N=10000. Pre-reg: preregs/2026-07-03_substrate_wikipedia_char_trigram_"
        "scale_up_full.md. Cell landed by cpu_runner_0 at commit 84c53803e.\n"
        "\n"
        "OFF-DATA VERIFY (skunkworks 2026-07-03 via .venv python on metrics.json):\n"
        "  run_mode=full VERIFIED (Fix#28 selftest-vs-FULL disambiguation clean)\n"
        "  cardinality_ok=True (expected_n_units=6 observed_n_units=6)\n"
        "  arms_differ_verified=True (char-trigram digest 591c3a5be65600cf; baseline digests distinct across seeds)\n"
        "  ARM_CHAR_TRIGRAM_WIKIPEDIA_N10K per_seed r@5 = [0.7030, 0.7030, 0.7030] mean 0.7030\n"
        "  ARM_RANDOM_BASELINE_N10K per_seed r@5 = [0.0003, 0.0001, 0.0005] mean 0.0003\n"
        "  chance_r5 = 5/N = 5/10000 = 0.0005; band_max_r5 = 0.0025; baseline in-band OK\n"
        "  Smoke reference OFF DISK: 0.854 at N=500 (data/exp_substrate_wikipedia_char_trigram_baseline_smoke_2026_07_03/metrics.json)\n"
        "  delta_from_smoke_r5 = 0.703 - 0.854 = -0.151 VERIFIED\n"
        "  bge reference: 0.992 at N=100K (2026-06-19 exp_wikipedia_ingest_100k_gpu_v1)\n"
        "  gap_to_bge_100k_ref_r5 = 0.992 - 0.703 = +0.289 VERIFIED\n"
        "  Band [0.60, 0.90]: 0.703 IN-BAND -> HP_MEASURED_BOUND per prereg\n"
        "\n"
        "DETERMINISM CAVEAT (not a red flag; recorded honestly):\n"
        "  Char-trigram encoder digest 591c3a5be65600cf IDENTICAL across all 3 seeds and r@5=0.7030 exact.\n"
        "  This is EXPECTED: char-trigram is a deterministic hash-based surface encoder\n"
        "  (n_unique_trigrams=43986 identical across seeds; body_char_cap=800 fixed; n_dim=2048 fixed).\n"
        "  Seed only varies the random baseline arm. Consequence: r@5=0.703 is a SINGLE-\n"
        "  REALIZATION property of (corpus, encoder-params); the 3-seed structure serves\n"
        "  to verify baseline chance ~= observed random and confirm cardinality. To get\n"
        "  cross-seed variance for the char-trigram arm would require varying encoder\n"
        "  hyperparameters (hash seed, n_dim, body_char_cap) or corpus subsampling.\n"
        "\n"
        "TIER: CG_MEASURED_BOUND (proven bound; mechanism characterization).\n"
        "  Not a capability claim. Substrate has ingested no general knowledge; this\n"
        "  atom measures the substrate-native char-trigram surface encoder's title<-body\n"
        "  retrieval performance on a SUPERVISED-Wikipedia test corpus (test corpus IS\n"
        "  the ground truth pair set) at N=10K articles.\n"
        "  cert_increment_delta = +1 (proven-bound counts toward CERT N per ladder).\n"
        "\n"
        "SCALING-LAW DATAPOINT:\n"
        "  N=500  -> r@5 = 0.854 (smoke)\n"
        "  N=10K  -> r@5 = 0.703 (this atom; -0.151 for 20x scale)\n"
        "  N=100K -> r@5 = 0.992 (bge encoder; different mechanism; not directly comparable)\n"
        "  Char-trigram degrades under scale (increasing shared-trigram density between\n"
        "  distinct articles as corpus grows -> more collision-driven false positives).\n"
        "  Discriminates from concept-encoder arc: PPMI/SVD Wikipedia N=10K is the\n"
        "  matched-scale comparator (cell authored, holding for Director green-light).\n"
        "\n"
        "SUBSTRATE-KNOWS-NOTHING FRAMING:\n"
        "  r@5=0.703 measures the encoder mechanism's ability to bring a body-vector\n"
        "  close to its own title-vector under substrate binding+bundling primitives\n"
        "  on a fixed Wikipedia corpus. It is NOT evidence that the substrate understands\n"
        "  Wikipedia content. Test corpus is the supervised ground truth. Bge N=100K\n"
        "  reference at 0.992 is a stronger encoder on the same task; substrate-native\n"
        "  encoder must eventually match/beat bge for KB retire.\n"
        "\n"
        "META candidate deferred: only 2 datapoints (N=500, N=10K) is not a scaling-law\n"
        "  atom yet. If PPMI Wikipedia N=10K lands with differentiating r@5, a META\n"
        "  synthesis atom composing char-trigram vs PPMI Wikipedia scaling becomes\n"
        "  warranted (STANDARD_META_SYNTHESIS with tier MM_TENTATIVE_SYNTHESIS unless 3+\n"
        "  datapoints with tight cross-encoder discrimination)."
    ),
    "metadata": {
        "provenance_quality": "CERT_MEASURED_BOUND",
        "verdict": "MEASURED_BOUND",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on metrics.json: run_mode=full; "
            "cardinality_ok=True (6/6); arms_differ_verified=True; ARM_CHAR_TRIGRAM_WIKIPEDIA_N10K "
            "per-seed r@5 = [0.7030,0.7030,0.7030] (deterministic encoder; cross-seed std=0 by "
            "design); ARM_RANDOM_BASELINE_N10K per-seed r@5 = [0.0003,0.0001,0.0005] mean 0.0003 "
            "in-band vs chance 5e-4; delta_from_smoke_r5 = -0.151 (smoke off disk 0.854 at N=500); "
            "gap_to_bge_100k_ref_r5 = +0.289; band [0.60,0.90] observed 0.703 IN-BAND -> MB"
        ),
        "regime": {
            "N_articles": 10000,
            "n_dim": 2048,
            "body_char_cap": 800,
            "corpus": "wikipedia_title_body_pair_supervised_test_corpus",
            "encoder_family": "substrate_native_char_trigram_surface",
            "encoder_determinism": "deterministic_hash_based_seed_only_varies_random_baseline",
            "arms": ["ARM_CHAR_TRIGRAM_WIKIPEDIA_N10K", "ARM_RANDOM_BASELINE_N10K"],
            "seeds": [11, 17, 23],
            "topK_metric": "recall_at_5",
        },
        "metrics_off_disk": {
            "char_trigram_r5_per_seed": [0.7030, 0.7030, 0.7030],
            "char_trigram_r5_mean": 0.7030,
            "char_trigram_r5_std": 0.0,
            "char_trigram_r1_mean": 0.4872,
            "char_trigram_r10_mean": 0.7726,
            "char_trigram_mrr_mean": 0.5864,
            "random_baseline_r5_per_seed": [0.0003, 0.0001, 0.0005],
            "random_baseline_r5_mean": 0.0003,
            "chance_r5": 0.0005,
            "band_max_r5_baseline": 0.0025,
            "baseline_in_band": True,
            "smoke_reference_r5_N500_off_disk": 0.854,
            "delta_from_smoke_r5": -0.151,
            "bge_100k_reference_r5": 0.992,
            "gap_to_bge_100k_ref_r5": 0.289,
            "measured_band": [0.60, 0.90],
            "observed_r5_in_band": True,
            "n_unique_trigrams": 43986,
            "hash_collision_prob_estimate": 0.2252,
        },
        "scaling_law_datapoints_partial": {
            "N_500_r5": 0.854,
            "N_10000_r5": 0.703,
            "delta_20x_scale": -0.151,
            "bge_N_100000_r5_different_mechanism": 0.992,
            "meta_synthesis_deferred_until_ppmi_landed_at_N_10K": True,
        },
        "cross_arc_prior_atom_check": {
            "prior_wikipedia_atom_id": "T3/EXP_wikipedia_ingest_100k_gpu_v1",
            "prior_wikipedia_atom_role": "bge_encoder_reference_r5_0p992_at_N_100K_used_as_gap_comparator",
            "novel_arc_for_substrate_native_encoder_wikipedia_scaling": True,
            "substrate_kb_top_hits_cosine_0p30_to_0p32": (
                "2026-06-27 char-trigram-sufficiency drill for Mathlib (different corpus); "
                "clean-encoder-tests notes; no prior char-trigram Wikipedia scaling atom"
            ),
        },
        "framing_discipline": {
            "substrate_knows_nothing_USER_LOCKED_2026-07-02": True,
            "mechanism_characterization_not_capability_claim": True,
            "supervised_wikipedia_regime_not_brain_analog_task": True,
            "test_corpus_is_ground_truth_pair_set": True,
            "no_llm_comparisons_no_english_narration": True,
        },
        "cert_increment_delta": 1,
        "discipline_tags": [
            "cert_disposition_proven_bound_MEASURED_MECHANISM",
            "fix28_verify_per_arm_off_disk_not_verdict_msg",
            "run_mode_full_verified_not_selftest",
            "baseline_in_band_verified_chance_5e-4_observed_3e-4",
            "deterministic_encoder_cross_seed_std_zero_by_design_not_bug",
            "supervised_wikipedia_regime_ground_truth_is_test_corpus",
            "substrate_knows_almost_nothing_USER_LOCKED_2026-07-02",
            "mechanism_analog_not_task_analog_USER_LOCKED_2026-07-02",
            "gap_to_bge_bookkept_bge_never_in_substrate_but_bar_for_KB_retire",
            "meta_synthesis_deferred_pending_ppmi_wikipedia_N10K",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# CERT LEDGER ROW
# ============================================================================
_t0 = time.time()

ledger_MB = {
    "ts": _t0,
    "op": "cert_ruling_measured_bound",
    "atom_id": f"math::{atom_MB['id']}",
    "cert_status": "measured_bound",
    "cert_class": "measured_mechanism",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": "84c53803e",
    "verdict": (
        "MEASURED_BOUND_substrate_native_char_trigram_Wikipedia_N10K_r5_0p703_in_band_"
        "0p60_0p90_delta_from_smoke_neg_0p151_gap_to_bge_100k_pos_0p289_"
        "deterministic_encoder_baseline_in_band_supervised_regime_mechanism_characterization"
    ),
    "cert_increment_delta": 1,
    "cv": 0.0,  # cross-seed std 0 by design (deterministic encoder); baseline cv non-zero and in-band
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_wikipedia_char_trigram_scale_up_full_2026_07_03/metrics.json",
        "smoke_ref_metrics_path": "data/exp_substrate_wikipedia_char_trigram_baseline_smoke_2026_07_03/metrics.json",
        "bge_ref_metrics_path": "data/exp_wikipedia_ingest_100k_gpu_v1/metrics.json",
        "prereg_path": "preregs/2026-07-03_substrate_wikipedia_char_trigram_scale_up_full.md",
        "cell_path": "experiments/exp_substrate_wikipedia_char_trigram_scale_up_full_2026-07-03.py",
        "atom_qualified_id": f"math::{atom_MB['id']}",
    },
    "supersedes": None,
    "note": (
        "substrate_native_char_trigram_Wikipedia_scale_up_FULL_N10K_MEASURED_BOUND_"
        "r5_0p703_3seed_deterministic_encoder_std_zero_by_design_baseline_in_band_"
        "chance_5e-4_observed_3e-4_delta_from_smoke_N500_neg_0p151_gap_to_bge_100k_pos_0p289_"
        "supervised_wikipedia_regime_mechanism_characterization_not_capability_"
        "meta_synthesis_deferred_pending_ppmi_wikipedia_N10K_landing"
    ),
}


# ============================================================================
# A5 write protocol
# ============================================================================
def append_jsonl_a5(path: Path, new_row: dict, label: str):
    print(f"[A5] {label}: path={path}")
    assert path.exists()

    with open(path, "r", encoding="utf-8") as f:
        pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")

    for i, ln in enumerate(pre_lines):
        if not ln.strip(): continue
        try: json.loads(ln)
        except Exception as e: raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")

    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row: assert parsed_back.get("id") == new_row.get("id")
    if "atom_id" in new_row: assert parsed_back.get("atom_id") == new_row.get("atom_id")

    out_text = "\n".join(pre_lines + [new_line]) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text); f.flush(); os.fsync(f.fileno())
    import time as _time
    for _attempt in range(10):
        try: os.replace(str(tmp_path), str(path)); break
        except PermissionError:
            if _attempt == 9: raise
            _time.sleep(0.1 * (2 ** _attempt))

    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1

    tail = json.loads(post_lines[-1])
    if "id" in new_row: assert tail["id"] == new_row["id"]
    if "atom_id" in new_row: assert tail["atom_id"] == new_row["atom_id"]

    for i, ln in enumerate(post_lines):
        if not ln.strip(): continue
        try: json.loads(ln)
        except Exception as e: raise RuntimeError(f"POST integrity fail line {i+1}: {e}")

    print(f"[A5] {label}: OK")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    append_jsonl_a5(MATH_ATOMS, atom_MB,     "math/atoms (substrate wikipedia char-trigram scale-up N10K MB)")
    append_jsonl_a5(CERT_LEDGER, ledger_MB,  "cert_ledger (MB +1)")
    print(f"[A5] DONE OK")
    print(f"[A5] substrate_wikipedia_char_trigram_scale_up_full_N10K: MEASURED_BOUND +1")
    print(f"[A5] r@5 = 0.703 in band [0.60, 0.90]; delta_from_smoke -0.151; gap_to_bge_100k +0.289")
    print(f"[A5] CERT delta = +1")


if __name__ == "__main__":
    main()
