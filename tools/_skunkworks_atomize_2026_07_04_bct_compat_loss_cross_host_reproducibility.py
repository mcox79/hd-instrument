"""
A5-gated atomization -- Skunkworks landed-VET of Encoder BCT (backward-compatible
-training) compatibility-loss cell, FULL run. 2026-07-04.

CELL: experiments/exp_encoder_bct_compatibility_loss_v1_core.py (commit 8f0ad202d)
PREREG: preregs/2026-07-04_exp_encoder_bct_compatibility_loss_v1.md

===================== CRITICAL FIX#28 FINDING: TWO DIFFERENT RUNS, NOT ONE =====================
The prereg's "Measured results" / commit message cite a LOCAL FULL-scale PREVIEW
(min_ratio_with_bct=0.8910, quality_retention=0.9886) run BEFORE remote dispatch, and
assert the official remote_cpu_queue landing is "fully deterministic given fixed seeds,
so a close match is expected, not a new discovery." THIS ASSUMPTION IS FALSE, verified
off-disk:

  git status shows data/exp_encoder_bct_compatibility_loss_v1/metrics.json as MODIFIED
  in the working tree relative to the git-committed blob (8f0ad202d) -- the ORIGINAL
  committed file (ckpt_a_path="D:\\AI\\hd-instrument\\...") is the local preview
  (_start_marker pid=8992 host=FrameworkMPC, started 18:12:57Z, elapsed_s=421.68,
  ts_iso completion 18:19:59Z). The file CURRENTLY on disk (uncommitted, overwritten
  post-commit by a sync-back mechanism) has ckpt_a_path="C:\\dev\\hd-instrument\\..."
  -- this is the ACTUAL remote_cpu_queue landing (_start_marker pid=13096 host=Home,
  started 18:22:01Z, elapsed_s=211.59, ts_iso completion 18:25:33Z). SSH byte-verified:
  SHA256 of the working-tree local file == SHA256 of C:/dev/hd-instrument/data/
  exp_encoder_bct_compatibility_loss_v1/metrics.json pulled via scp from marsh@home
  (265f56b279aa4f8cc2c120c86e8bebe3a2b297c12ae6aaf67d167322fbeda288, both sides) --
  confirms the working-tree copy genuinely IS the remote landing, synced back.
  Cell source SHA256-verified IDENTICAL both sides (c5fd1e9a112d585d365a655264e833c
  364991e88333b9fe9796e3710f407beed) -- rules out code-version drift as the cause.
  CONFIRMED torch version DRIFT: local .venv torch==2.12.0+cpu vs remote .venv
  torch==2.5.1+cu121 (remote is CUDA-capable but this cell never calls .cuda()/.to()
  anywhere -- all tensors stay on default CPU device both sides, confirmed by direct
  code read: no device placement code exists in this cell). Different torch minor
  versions can (and evidently do) produce different floating-point trajectories over
  1200 gradient steps from bit-identical seeds/inputs (different default kernel/
  reduction-order implementations across releases) -- no torch.use_deterministic_
  algorithms() call or thread-count pin exists in this cell, so bit-exact cross-
  version reproducibility was never actually guaranteed despite the prereg's claim.

RECOMPUTE (off metrics.json per_unit/ratios fields, NOT verdict_msg alone), both runs:
  LOCAL PREVIEW (git-committed, non-canonical -- superseded by the official landing):
    min_ratio_no_bct=0.0 (block=0.0, dense=0.002); min_ratio_with_bct=0.891
    (block=0.891, dense=0.996); semantic_spearman NO_BCT=0.7126949576130638,
    WITH_BCT=0.70455647270534; quality_retention=0.9885806896473901 (recomputed
    0.70455647270534/0.7126949576130638 -- matches file exactly).
  REMOTE OFFICIAL (remote_cpu_queue landing, CANONICAL -- this is the dispatched run):
    min_ratio_no_bct=0.0 (block=0.0, dense=0.0); min_ratio_with_bct=0.887
    (block=0.887, dense=0.998); semantic_spearman NO_BCT=0.8282158400220667,
    WITH_BCT=0.692550782864785; quality_retention=0.8361960124384157 (recomputed
    0.692550782864785/0.8282158400220667 -- matches file exactly). cardinality_ok=
    true (14/14) both runs; arms_differ_verified=true (6 distinct sha256 arm digests)
    both runs, digests differ BETWEEN the two runs too (confirms genuinely different
    trained weights, not a stale-copy bug). SAME_A/SAME_B >=0.999 both runs (baseline_
    in_band gate holds); RANDOM_CONTROL <=0.002 both runs (discriminator-fires gate
    holds); NO_BCT baseline collapses completely in BOTH runs (min_ratio=0.0), so the
    BASELINE_MUST_COLLAPSE positive-control/discriminator-fires check is satisfied
    and robust both runs.

FINDING 1 -- RETRIEVAL-RESTORATION MECHANISM: ROBUST, CONFIRMED (not the fragile part).
  min_ratio_with_bct: 0.891 (local) vs 0.887 (remote) -- delta 0.004, i.e. this specific
  statistic is STABLE across the cross-host/cross-torch-version discrepancy. The BCT
  loss (anchored to version A's frozen CONTINUOUS output during training) genuinely and
  robustly restores cross-version retrieval from total collapse (min_ratio_no_bct=0.0,
  both runs, both codes in the remote run) to ~0.887-0.891 of same-checkpoint ceiling,
  BOTH on the BLOCK-sparse code AND the DENSE sign code (both are quantized/discretized
  readouts, per direct code read of _encode_hard_block/_dense_sign_codes -- retrieval
  is NOT measured on raw continuous cosine similarity in either unit). This directly
  answers the task's design-soundness question (item 2): continuous-anchoring DOES
  transfer through discretization to produce compatible discrete codes -- and BLOCK
  (the coarser, harder-to-align quantization) is consistently the LOWER of the two
  ratios in both runs (0.891 block vs 0.996 dense locally; 0.887 block vs 0.998 dense
  remotely), correctly setting the min_ratio/HARD_PASS gate (HP_SCOPE uses min() over
  both codes) -- i.e. the reported number is not inflated by only measuring the easier
  code. DISPOSITION: MM_STANDARD -- single-seed, but the two accidental quasi-
  independent executions (different host, different torch version) that happened to
  occur here function as a de facto 2-sample cross-check on THIS statistic, and it
  passed.

FINDING 2 -- QUALITY-RETENTION MAGNITUDE: NOT ROBUST, HEADLINE FRAMING CORRECTED.
  quality_retention: 0.9886 (local preview) vs 0.8362 (remote official) -- a 0.153
  ABSOLUTE swing (18% relative) between nominally-identical fixed-seed executions of
  bit-identical code. The commit message / prereg "Verdict routing" section frames this
  as "98.9% retention... essentially no quality cost" and treats the remote landing as
  merely confirmatory. THIS IS WRONG: the prereg's own headline number describes ONLY
  the non-canonical local preview. The CANONICAL number (the actual remote_cpu_queue
  dispatch, per the dispatch architecture where FULL landings happen on remote_cpu_
  queue, not local preview) is quality_retention=0.8362 -- a genuine ~16% relative
  quality cost, not negligible, clearing the pre-registered QUALITY_RETENTION_HARD_PASS
  gate (>=0.80) by a margin of only 0.036. Given the demonstrated ~0.15-point swing on
  this EXACT statistic between two runs that should have been identical, a margin of
  0.036 cannot be certified as a stable/safe clearance -- a third run on different
  hardware/torch version could plausibly land below 0.80 (demoting to MIDDLE_BAND per
  the cell's own pre-registered bands) or lower. DIAGNOSTIC (recomputed from per_unit):
  the swing is driven almost entirely by the NO_BCT baseline's OWN semantic_spearman
  moving (0.7127 local -> 0.8282 remote, +0.115), while WITH_BCT's semantic_spearman
  stayed comparatively stable (0.7046 local -> 0.6926 remote, -0.012) -- i.e. the
  instability lives in the untreated baseline arm's absolute quality score, not in the
  BCT-anchored arm itself. Plausible mechanistic note (not fully resolved here): top-1
  retrieval accuracy (a coarse, discrete statistic -- only the single best match per
  query matters) is far more robust to small per-step floating-point perturbations
  than Spearman rank-correlation over thousands of nearby-ranked random pairs (many
  near-tied pairwise orderings can flip from tiny numeric differences without changing
  any top-1 winner) -- consistent with Finding 1 (retrieval) being stable while Finding
  2 (rank-correlation quality metric) is not, under the same cross-host/cross-torch-
  version perturbation. DISPOSITION: MEASURED_MECHANISM (proven-bound) -- the mechanism
  clears its own pre-registered quality gate on the one official landing measured
  (0.8362 >= 0.80), so the cell's own on-disk verdict field (HARD_PASS) is CONFIRMED
  CORRECT and not overturned/demoted here, but the specific "98.9%, no cost" magnitude
  claim is REFUTED as the citable number; the correct citable canonical number is
  83.6% retention with a demonstrated +/-15-point cross-host noise band on this exact
  statistic, i.e. a proven bound (clears >=0.80), not a comfortably-tight one.

INTEGRITY CHECKS (task item 3): arms differ (verified, 6 distinct digests both runs,
differ between runs too). No leakage (probe drawn from held split he_idx, disjoint
from train tr_idx via the EXPECTED_MID_SPLIT hard-abort check, which did not fire --
split reproduced correctly both runs). bct_weight=0.15 selection: prereg's own smoke-
scale sweep table (16 values) is NON-monotonic/noisy at N=500 (e.g. w=0.10 measured
HIGHER retention=0.8361 than w=0.12's 0.7628 and the SELECTED w=0.15's 0.7139) --
0.15 is a defensible "principled midpoint of the non-saturated regime" per the prereg's
own framing and was NOT the single best-scoring smoke value (rules out p-hacking-for-
verdict), but the selection process itself is somewhat arbitrary given how noisy the
16-point smoke sweep is; a minor integrity note, not a red flag. BEST-VS-FINAL-
CHECKPOINT scrutiny (per the v3c precedent this audit was asked to apply): DOES NOT
APPLY structurally to this cell -- confirmed via direct code read of run_probe/
_train_b: both arms train for a SINGLE FIXED step budget (1200 steps) and are
evaluated ONCE at the terminal checkpoint; there is no eval-every/best-of-N-checkpoint
-selection code path in this cell at all (unlike v3c's argmax-over-13-eval-points
design). The actual analogous risk here was NOT best-of-many-checkpoints but best-of-
two-RUNS at the human-reporting level (local preview vs remote official) -- caught and
corrected above (Finding 2).

METRIC CAVEAT (task item 4): semantic_spearman is Spearman rank-correlation of
(code-cosine, teacher-cosine) over n_pairs=40000 RANDOM pairs drawn from the held-out
probe set -- the same class of metric flagged in this session's own prior v3c audit
(meta::T4/META_best_checkpoint_selection...goal_metric_fidelity atom, 2026-07-04) as
weaker evidence than raw cosine-to-gold for a stated raw-cosine capability goal. This
cell's own stated goal, however, is RELATIVE ("compatible stored vectors" / retrieval-
compatibility), not the encoder's separate absolute ~0.85-cosine-to-gold goal, so
rank-correlation is a reasonably-matched proxy for THIS cell's specific question
(does the code preserve enough relative semantic structure) -- it is the retrieval
top-1 units, not semantic_spearman, that answer the cell's PRIMARY decisive question
(does BCT restore cross-version identity-retrieval), and those units ARE the directly
correct metric (discrete top-1 match against the actual use case: nearest-neighbor
retrieval against an existing index). semantic_spearman here is secondary/gating-only
(quality-cost check), appropriately scoped. No metric-substitution violation found on
the PRIMARY claim; the caveat is about semantic_spearman's demonstrated instability
(Finding 2), not about it being the wrong metric class for this specific secondary
question.

NET: cell's own on-disk verdict (HARD_PASS) STANDS and is CONFIRMED by independent
recompute on the canonical (remote_cpu_queue official) landing. What is CORRECTED:
the citable headline numbers are min_ratio_with_bct=0.887 (not 0.891) and quality_
retention=0.8362 (not 0.9886) -- the retrieval-restoration finding is robust and
genuine (Finding 1, MM_STANDARD); the "negligible quality cost" framing is REFUTED
and replaced with "clears the pre-registered >=0.80 gate at 0.836, but this exact
statistic swings +/-0.15 across cross-host/cross-torch-version reruns of nominally
identical code, so treat the margin as unverified-stable, not comfortable" (Finding 2,
MEASURED_MECHANISM proven-bound).

CROSS-ARC OVERLAP CHECK (USER-locked 2026-07-01): bash tools/substrate_query.sh
"backward compatible training BCT compatibility loss anchor frozen continuous
embedding block sparse code cross checkpoint retrieval nondeterminism reproducibility"
-> top hits cosine=0.3564/0.3564/0.3486 (WordNet/FrameNet lexical "compatibility"
entries, generic dictionary sense) and cosine=0.3252 ("Versioning + backwards
compatibility" deployment-ops note, already cited and dismissed as NOT this mechanism
in the prereg's own prior-work check). NONE address the specific BCT-loss mechanism
or the cross-host/cross-torch-version nondeterminism finding -- GENUINELY NOVEL cell.
Separately: this session's own EARLIER v3c audit (2026-07-04, same day, ledger already
contains it) flagged an UNRESOLVED "REPRODUCIBILITY GAP" open question (v3b vs v3c
GLOBAL/seed7 nominally-identical config produced a 0.082 final-dense gap, candidate
causes "GPU non-determinism absent explicit determinism flags, OR RNG-consumption-
order differences between scripts" -- left unresolved, not promoted to a standalone
META rule). THIS finding is a SECOND, CLEANER instance of the same general pattern
(fixed-seed "deterministic" claim does not hold across environments) -- cleaner here
because code SHA256 is confirmed byte-identical both sides (ruling out the v3c case's
"different script" confound) and a concrete root-cause candidate is now identified
(confirmed torch version drift, 2.12.0 vs 2.5.1). Filed as a fresh MM_TENTATIVE meta
atom that explicitly composes with/cites the v3c precedent as catch #1, this as catch
#2 toward the ledger's own "2 more independent catches" MM_TENTATIVE->MM_STANDARD
promotion convention.
"""
import json
import os
import time
import tempfile

MATH_ATOMS = "d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl"
META_ATOMS = "d:/AI/hd-instrument/data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = "d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl"

TS = time.time()
TS_ISO = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(TS))

ANCHOR = "encoder_bct_compatibility_loss_v1"
METRICS_CANONICAL = "data/exp_encoder_bct_compatibility_loss_v1/metrics.json"  # working-tree = remote-synced official
CELL_SRC = "experiments/exp_encoder_bct_compatibility_loss_v1_core.py"
CELL_COMMIT = "8f0ad202d53e6e80aaf3f88122d3434c393d282c"
PREREG = "preregs/2026-07-04_exp_encoder_bct_compatibility_loss_v1.md"
V3C_META_ATOM_PRECEDENT = ("meta::META_best_checkpoint_selection_from_small_number_of_coarse_eval_points_can_"
                            "cherry_pick_transient_peak_from_declining_trajectory_cross_seed_agreement_of_MAX_"
                            "statistic_does_NOT_establish_stability_PLUS_goal_metric_verification_rank_"
                            "correlation_over_random_pairs_is_NOT_equivalent_to_cosine_to_gold_when_goal_is_"
                            "stated_as_raw_cosine_case_study_v3c_encoder_2026-07-04")

math_atom_retrieval_robust = {
    "id": ("math::MM_STANDARD_BCT_compat_loss_v1_RETRIEVAL_RESTORATION_MECHANISM_CONFIRMED_ROBUST_"
           "cross_host_cross_torch_version_local_preview_torch2p12_min_ratio_with_bct_0p891_remote_"
           "official_torch2p5p1_0p887_delta_0p004_both_BLOCK_AND_DENSE_discretized_codes_not_"
           "continuous_block_is_harder_lower_ratio_correctly_gates_HP_SCOPE_min_baseline_collapses_"
           "0p000_both_runs_2026-07-04"),
    "name": ("MATH BCT (backward-compatible-training) compatibility loss: cross-version retrieval "
             "restoration mechanism CONFIRMED, robust across an accidental cross-host/cross-torch-"
             "version 2-execution check (min_ratio_with_bct 0.891 local-preview-torch2.12 vs 0.887 "
             "remote-official-torch2.5.1, delta 0.004)."),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record_measured_mechanism",
    "description": (
        "MM_STANDARD: an explicit BCT compatibility loss (L_bct = mean(1-cos(z_B(x), z_A_frozen(x))), "
        "anchored against an already-existing frozen checkpoint's RAW CONTINUOUS pre-quantization "
        "output, weight=0.15) restores cross-version top-1 retrieval (queries from a newly-trained "
        "'version B' encoder against an already-built 'version A' index) from TOTAL collapse "
        "(min_ratio_no_bct=0.0, both BLOCK and DENSE codes, both of two independent executions) to "
        "0.887-0.891 of same-checkpoint ceiling. RECOMPUTE (off metrics.json per_unit/ratios, NOT "
        "verdict_msg alone): the officially-dispatched remote_cpu_queue landing (CANONICAL; SSH byte-"
        "verified via SHA256, working-tree copy == C:/dev/hd-instrument/data/exp_encoder_bct_"
        "compatibility_loss_v1/metrics.json on marsh@home, 265f56b279aa4f8cc2c120c86e8bebe3a2b297c"
        "12ae6aaf67d167322fbeda288 both sides) measures CROSS_AIDX_BQUERY_WITH_BCT_BLOCK=0.887, "
        "CROSS_AIDX_BQUERY_WITH_BCT_DENSE=0.998 (both /SAME_A=1.0) -> min_ratio_with_bct=0.887; "
        "CROSS_AIDX_BQUERY_NO_BCT_{BLOCK,DENSE}=0.0/0.0 -> min_ratio_no_bct=0.0 (baseline collapses "
        "completely). A SEPARATE, non-canonical local FULL-scale preview run (git-committed blob at "
        "8f0ad202d, pre-dating the remote landing) measured 0.891/0.996 -> min_ratio_with_bct=0.891, "
        "min_ratio_no_bct=0.0 (block=0.0, dense=0.002) -- the min_ratio_with_bct statistic is STABLE "
        "(delta 0.004) across this accidental 2-execution cross-check, despite the two runs using "
        "DIFFERENT torch versions (local .venv torch==2.12.0+cpu vs remote .venv torch==2.5.1+cu121; "
        "cell source SHA256-confirmed byte-identical both sides, c5fd1e9a112d585d365a655264e833c"
        "364991e88333b9fe9796e3710f407beed; no .cuda()/.to() device placement anywhere in the cell, "
        "confirmed by direct code read -- both executions genuinely ran on CPU despite remote's CUDA-"
        "capable build). DESIGN-SOUNDNESS CHECK (task item 2): retrieval is measured on the ACTUAL "
        "discretized readouts used for storage/retrieval (BLOCK = per-block argmax one-hot*sign code "
        "via _encode_hard_block; DENSE = full-4096-dim sign code via _dense_sign_codes), NEVER on raw "
        "continuous cosine similarity, in either run -- and BLOCK (the coarser, harder-to-align "
        "quantization) is consistently the LOWER of the two ratios in both runs (0.887/0.891 block vs "
        "0.998/0.996 dense), correctly setting the HP_SCOPE min()-gated verdict statistic -- i.e. "
        "continuous-anchoring during training genuinely transfers through post-hoc discretization to "
        "produce compatible BLOCK codes, not merely an artifact of measuring the easier continuous/"
        "dense-only readout. cardinality_ok=true (14/14), arms_differ_verified=true (6 distinct sha256 "
        "digests, DIFFERENT between the two runs too -- confirms genuinely different trained weights "
        "each time, not a stale-copy bug), SAME_A/SAME_B>=0.999, RANDOM_CONTROL<=0.002, both runs. "
        "ACTIONABLE: the retrieval-restoration mechanism itself (encoder-version compatibility via a "
        "continuous-anchoring BCT term) is a genuine, reasonably robust positive finding -- safe to cite "
        "as a validated mechanism for future encoder-version-promotion work. See the companion bounded-"
        "characterization atom for why the accompanying 'negligible quality cost' framing is NOT equally "
        "safe to cite."
    ),
    "aliases": ["bct_compat_loss_retrieval_restoration_confirmed", "continuous_anchoring_transfers_to_block_code",
                "encoder_version_compatibility_mechanism_v1"],
    "metadata": {
        "record_class": "experiment_measured_mechanism_cross_execution_corroborated",
        "cert_status": "mm_standard_cross_host_corroborated_measured_mechanism",
        "cert_class": "MM_STANDARD_BCT_retrieval_restoration_confirmed_robust",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_bct_compat_loss_audit",
        "anchor_name": ANCHOR,
        "cell_source_path": CELL_SRC, "cell_commit": CELL_COMMIT, "prereg_path": PREREG,
        "raw_metrics_path_canonical_remote_official": METRICS_CANONICAL,
        "ssh_byte_verify": "SHA256 265f56b279aa4f8cc2c120c86e8bebe3a2b297c12ae6aaf67d167322fbeda288 "
                          "identical working-tree local vs C:/dev/hd-instrument remote, 2026-07-04",
        "cell_sha256_identical_both_hosts": "c5fd1e9a112d585d365a655264e833c364991e88333b9fe9796e3710f407beed",
        "run_mode": "full", "seed": 7, "device": "cpu",
        "verdict_on_disk_canonical_remote": "HARD_PASS",
        "recompute_check": {
            "min_ratio_with_bct_remote_official": 0.887, "min_ratio_with_bct_local_preview": 0.891,
            "min_ratio_no_bct_both_runs": 0.0,
            "block_vs_dense_remote": {"block": 0.887, "dense": 0.998},
            "block_vs_dense_local": {"block": 0.891, "dense": 0.996},
            "torch_version_local": "2.12.0+cpu", "torch_version_remote": "2.5.1+cu121",
        },
        "cross_arc_overlap_check_2026_07_04_USER_locked": (
            "no cosine>0.30 hit against this specific mechanism; top hits (0.356/0.349/0.325) are "
            "generic WordNet/FrameNet 'compatibility' lexical entries and the already-dismissed "
            "deployment-ops versioning note cited in this cell's own prior-work check."
        ),
        "cert_increment_delta": 1,
    }
}

math_atom_quality_retention_bounded = {
    "id": ("math::MEASURED_MECHANISM_BCT_compat_loss_v1_QUALITY_RETENTION_HEADLINE_CORRECTED_98p9pct_"
           "was_noncanonical_local_preview_ONLY_canonical_remote_cpu_queue_official_landing_measures_"
           "83p6pct_delta_15p3_points_absolute_between_nominally_identical_fixed_seed_torch2p12_vs_"
           "torch2p5p1_reruns_still_clears_0p80_gate_margin_0p036_unverified_stable_swing_driven_by_"
           "NO_BCT_baseline_semantic_spearman_0p713_to_0p828_not_by_WITH_BCT_arm_2026-07-04"),
    "name": ("MATH bounded characterization: the BCT compat-loss cell's 'quality_retention=98.9%, "
             "essentially no quality cost' headline describes ONLY a non-canonical local preview run; "
             "the actual official remote_cpu_queue landing measures 83.6% retention (still clears the "
             "pre-registered >=0.80 gate, but with a demonstrated 15.3-point cross-run swing on this "
             "exact statistic -- margin not verified stable)."),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record_measured_mechanism",
    "description": (
        "MEASURED_MECHANISM (proven-bound tier): Fix#28 landed-VET correction. The cell's prereg "
        "'Verdict routing' / commit message headline ('retaining 98.9% of NO_BCT's held-out semantic "
        "quality... essentially no quality cost') is drawn from data/exp_encoder_bct_compatibility_"
        "loss_v1/metrics.json AS ORIGINALLY GIT-COMMITTED (8f0ad202d) -- verified via `git show "
        "8f0ad202d:<path>`, that blob has ckpt_a_path='D:\\\\AI\\\\hd-instrument\\\\...' (the LOCAL "
        "machine) and _start_marker host=FrameworkMPC, i.e. a LOCAL FULL-scale PREVIEW run made BEFORE "
        "remote dispatch, not the official landing. `git status` shows this same path as MODIFIED "
        "(uncommitted) in the current working tree -- the file was silently overwritten post-commit by "
        "a sync-back mechanism with the ACTUAL remote_cpu_queue landing (ckpt_a_path='C:\\\\dev\\\\"
        "hd-instrument\\\\...', _start_marker host=Home matching marsh@home, pid=13096, started "
        "2026-07-04T18:22:01Z, completed 18:25:33Z, elapsed_s=211.59) -- SSH byte-verified (SHA256 "
        "identical, working-tree copy vs scp-pulled C:/dev/hd-instrument copy). RECOMPUTE (off per_unit, "
        "matches the file's own ratio/retention fields exactly both runs): LOCAL PREVIEW (non-canonical) "
        "semantic_spearman NO_BCT=0.7126949576130638 / WITH_BCT=0.70455647270534 -> quality_retention="
        "0.9885806896473901. REMOTE OFFICIAL (CANONICAL) semantic_spearman NO_BCT=0.8282158400220667 / "
        "WITH_BCT=0.692550782864785 -> quality_retention=0.8361960124384157 (recomputed 0.692550782864785"
        "/0.8282158400220667, matches file exactly). ABSOLUTE DELTA on this one statistic between two "
        "nominally-identical fixed-seed (seed=7) executions of BYTE-IDENTICAL code (cell source SHA256 "
        "confirmed identical both hosts): 0.1524 (18.2% relative) -- NOT a close match, contradicting "
        "the prereg's own explicit claim that the remote landing was 'fully deterministic given fixed "
        "seeds, so a close match is expected.' CONFIRMED CONTRIBUTING FACTOR: torch version drift (local "
        ".venv torch==2.12.0+cpu vs remote .venv torch==2.5.1+cu121) -- no torch.use_deterministic_"
        "algorithms() call or thread-pin exists in this cell, so bit-exact cross-version/cross-host "
        "reproducibility over a 1200-step training loop was never actually guaranteed. DIAGNOSTIC "
        "(recomputed from per_unit): the swing is driven almost entirely by the UNTREATED NO_BCT arm's "
        "own semantic_spearman moving (0.7127->0.8282, +0.115), while the BCT-anchored WITH_BCT arm's "
        "semantic_spearman stayed comparatively stable (0.7046->0.6926, -0.012) -- the instability lives "
        "in the baseline arm, not in the mechanism under test. Companion observation: min_ratio_with_bct "
        "(a discrete top-1-match statistic) was STABLE (delta 0.004) across the SAME cross-host/cross-"
        "torch-version perturbation that produced this 0.1524 swing in semantic_spearman (a continuous "
        "rank-correlation statistic over many nearby-ranked random pairs) -- consistent with top-1 "
        "accuracy being materially more robust to small floating-point perturbation than Spearman rank-"
        "correlation, which can flip many near-tied pairwise orderings without changing any single "
        "top-1 winner. TIER RATIONALE: the cell's own on-disk verdict (HARD_PASS) on the CANONICAL "
        "(remote official) data is CONFIRMED CORRECT and NOT overturned -- 0.887>=0.50 (min_ratio) AND "
        "0.836>=0.80 (retention) both hold on the actual dispatched run. What is corrected: (1) the "
        "citable retention number is 83.6%, not 98.9%; (2) 'essentially no quality cost' is REFUTED -- "
        "the genuine cost is ~16% relative, not negligible; (3) the 0.036 margin above the 0.80 gate "
        "cannot be certified as stable given the demonstrated 0.15-point cross-run noise band on this "
        "exact statistic -- a third rerun on different hardware/torch version could plausibly fall below "
        "0.80 (which would demote to this cell's own pre-registered MIDDLE_BAND). NOT filed as a demote "
        "of the HARD_PASS verdict (which correctly reflects the canonical data), NOT filed as a proven "
        "negative (the mechanism does clear its own gate) -- filed as a proven BOUND: the finding "
        "narrower/weaker than the prereg's own framing, but real."
    ),
    "aliases": ["bct_quality_retention_headline_corrected_98_9_to_83_6", "local_preview_vs_remote_official_"
                "citation_error_case_study", "torch_version_drift_causes_semantic_spearman_instability"],
    "metadata": {
        "record_class": "experiment_measured_mechanism_bounded_characterization",
        "cert_status": "measured_mechanism_bounded_characterization_headline_corrected",
        "cert_class": "MEASURED_MECHANISM_BCT_quality_retention_headline_corrected_not_stable_margin",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_bct_compat_loss_audit",
        "anchor_name": ANCHOR,
        "cell_source_path": CELL_SRC, "cell_commit": CELL_COMMIT, "prereg_path": PREREG,
        "raw_metrics_path_canonical_remote_official": METRICS_CANONICAL,
        "run_mode": "full", "seed": 7, "device": "cpu",
        "recompute_check": {
            "quality_retention_remote_official_canonical": 0.8361960124384157,
            "quality_retention_local_preview_noncanonical": 0.9885806896473901,
            "absolute_delta": 0.1523846771910256,
            "semantic_spearman_no_bct": {"local": 0.7126949576130638, "remote": 0.8282158400220667},
            "semantic_spearman_with_bct": {"local": 0.70455647270534, "remote": 0.692550782864785},
            "gate_threshold": 0.80, "gate_margin_remote": 0.0361960124384157,
        },
        "composes_with_atoms": [math_atom_retrieval_robust["id"]],
        "cross_arc_overlap_check_2026_07_04_USER_locked": (
            "no cosine>0.30 hit; distinct from but composes with this session's own earlier v3c "
            "reproducibility-gap observation (see meta atom precedent citation)."
        ),
        "cert_increment_delta": 1,
    }
}

meta_atom_cross_host_reproducibility = {
    "id": ("meta::META_local_FULL_preview_and_remote_official_landing_of_a_fixed_seed_cell_are_NOT_"
           "guaranteed_to_reproduce_even_with_byte_identical_code_verify_via_SSH_byte_hash_pull_before_"
           "citing_either_number_case_study_BCT_compat_loss_v1_torch2p12_vs_2p5p1_15p3_point_absolute_"
           "swing_in_semantic_spearman_retention_second_independent_catch_composes_with_v3c_2026-07-04"),
    "name": ("META rule (MM_TENTATIVE, catch #2): a 'local FULL-scale preview, run before remote "
             "dispatch' is NOT a safe stand-in for the actual official remote landing even when the "
             "cell is fixed-seed / nominally deterministic -- byte-verify (SSH pull + SHA256) and cite "
             "the OFFICIAL dispatched run's own metrics.json, never the preview's, once the official "
             "run exists."),
    "corpus": "meta",
    "tier": "T4",
    "kind": "methodology_rule",
    "description": (
        "MM_TENTATIVE methodology rule (2nd independent catch toward this ledger's established "
        "'2 more independent catches' MM_TENTATIVE->MM_STANDARD promotion convention; catch #1 was this "
        "session's own earlier v3c audit, which flagged an unresolved 'REPRODUCIBILITY GAP' -- v3b's "
        "GLOBAL/seed7 config vs v3c's nominally-identical GLOBAL/seed7 config differed by 0.082 final-"
        "dense, candidate causes left unresolved as 'GPU non-determinism absent explicit determinism "
        "flags, OR RNG-consumption-order differences between scripts' -- not promoted to a standalone "
        "meta atom at the time, see composes_with). THIS is a CLEANER second instance: same cell script "
        "(SHA256-confirmed byte-identical both hosts, c5fd1e9a112d585d365a655264e833c364991e88333b9fe"
        "9796e3710f407beed), same fixed seed (7), same every training/eval seed knob (B_INIT_SEED, "
        "BATCH_GEN_SEED, TRAIN_SUBSAMPLE_SEED, PROBE_SEED, RAND_CTRL_SEED_1/2, SEM_PAIR_SEED all fixed "
        "constants in the shipped cell) -- CPU-only execution confirmed both sides (no .cuda()/.to() "
        "device placement anywhere in the cell), ruling out the v3c case's GPU-nondeterminism and "
        "different-script confounds. The two runs (local FULL-scale preview, torch==2.12.0+cpu; remote "
        "official landing on remote_cpu_queue, torch==2.5.1+cu121-but-CPU-execution) produced a min_"
        "ratio_with_bct delta of only 0.004 (stable) but a semantic_spearman/quality_retention delta of "
        "0.1524 absolute (18.2% relative, UNSTABLE) -- confirming that even genuinely fixed-seed, byte-"
        "identical-code CPU training loops are NOT bit-exactly reproducible across torch releases (no "
        "torch.use_deterministic_algorithms() call or thread-count pin exists in this cell, so this was "
        "never actually guaranteed despite the prereg's explicit claim otherwise: 'fully deterministic "
        "given fixed seeds, so a close match is expected, not a new discovery'). RULE: (1) when a cell's "
        "own documentation asserts a local preview will 'closely reproduce' an official remote landing "
        "on grounds of fixed-seed determinism, do NOT accept that assertion without independently SSH-"
        "pulling and SHA256-byte-verifying the actual official metrics.json and diffing the two runs' "
        "per_unit numbers -- especially for any metric more sensitive than coarse discrete top-1/"
        "accuracy statistics (rank-correlation and continuous-similarity statistics appear, in this case "
        "study, to be considerably MORE sensitive to cross-version float perturbation than top-1 "
        "retrieval accuracy, plausibly because many near-tied pairwise rankings can flip without "
        "changing any single top-1 winner -- worth checking for in future cross-run comparisons). "
        "(2) when a repo's working-tree copy of a data file differs from its last-committed git blob "
        "(`git status` shows Modified with no corresponding new commit), that is itself a signal an "
        "automated sync-back process silently replaced a committed preview/interim result with a later "
        "official one -- diff the committed blob (`git show <commit>:<path>`) against the working-tree "
        "file before assuming they are the same data; they were NOT in this case study. (3) prefer citing "
        "the OFFICIALLY-DISPATCHED run's own numbers, never a preview's, in any downstream capability "
        "claim, verdict framing, or cert atom, once the official run exists -- this is a specific "
        "instance of the general Fix#28 discipline (verify off the actual landed data, not a producer's "
        "summary claim about what the landed data will show)."
    ),
    "aliases": ["local_preview_vs_official_remote_reproducibility_gap_rule", "torch_version_drift_"
                "nondeterminism_case_study_2", "verify_official_landing_not_preview_before_citing"],
    "metadata": {
        "record_class": "methodology_rule_reproducibility_and_citation_discipline",
        "cert_status": "mm_tentative_methodology_rule",
        "cert_class": "MM_TENTATIVE_META_RULE_local_preview_vs_official_landing_reproducibility_gap",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_bct_compat_loss_audit",
        "cell_source_path": CELL_SRC, "cell_commit": CELL_COMMIT,
        "raw_metrics_path_canonical_remote_official": METRICS_CANONICAL,
        "composes_with_atoms": [math_atom_quality_retention_bounded["id"], math_atom_retrieval_robust["id"]],
        "cites_precedent_catch_1": V3C_META_ATOM_PRECEDENT,
        "promotion_path": "MM_TENTATIVE -> MM_STANDARD after 1 more independent catch (this is catch #2; "
                          "catch #1 was the v3c reproducibility-gap observation, folded into a different "
                          "meta atom's item (b) rather than filed standalone -- if a 3rd independent case "
                          "surfaces, promote to MM_STANDARD and consider hardening as an A5-gate check: "
                          "auto-diff working-tree metrics.json against last-committed git blob before "
                          "any cert-atom recompute).",
        "cert_increment_delta": 1,
    }
}


def a5_append(path, atom):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_atoms_", suffix=".jsonl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as src:
                    for line in src:
                        f.write(line)
            f.write(json.dumps(atom, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    n_lines = 0
    found = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n_lines += 1
            obj = json.loads(line)  # integrity: raises on corrupt line
            aid = obj.get("id") or obj.get("atom_id")
            if aid == atom["id"]:
                found += 1
    if found != 1:
        raise RuntimeError(f"verify-load failed: atom id found {found}x (expected 1) in {path}")
    return n_lines


def ledger_append(atom, session_tag, ledger_path=CERT_LEDGER):
    entry = {
        "ts": TS,
        "ts_iso": TS_ISO,
        "atom_id": atom["id"],
        "corpus": atom["corpus"],
        "cert_status": atom["metadata"].get("cert_status"),
        "cert_class": atom["metadata"].get("cert_class"),
        "cert_increment_delta": atom["metadata"].get("cert_increment_delta", 0),
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_bct_compat_loss_audit",
        "landed_VET_session": session_tag,
    }
    d = os.path.dirname(ledger_path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_ledger_", suffix=".jsonl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if os.path.exists(ledger_path):
                with open(ledger_path, "r", encoding="utf-8") as src:
                    for line in src:
                        f.write(line)
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, ledger_path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


if __name__ == "__main__":
    print(f"[atomize] ts_iso={TS_ISO}")
    tag = "2026-07-04_bct_compat_loss_audit"
    n_math1 = a5_append(MATH_ATOMS, math_atom_retrieval_robust)
    print(f"[atomize] math MM_STANDARD retrieval-restoration-robust atom appended; math lines={n_math1}")
    n_math2 = a5_append(MATH_ATOMS, math_atom_quality_retention_bounded)
    print(f"[atomize] math MEASURED_MECHANISM quality-retention-headline-corrected atom appended; "
          f"math lines={n_math2}")
    n_meta = a5_append(META_ATOMS, meta_atom_cross_host_reproducibility)
    print(f"[atomize] meta MM_TENTATIVE cross-host/cross-torch-version reproducibility rule appended; "
          f"meta lines={n_meta}")
    ledger_append(math_atom_retrieval_robust, tag)
    ledger_append(math_atom_quality_retention_bounded, tag)
    ledger_append(meta_atom_cross_host_reproducibility, tag)
    print("[atomize] DONE 3 atoms + 3 ledger entries; A5-gated (tmp+os.replace+verify-load+json-integrity); "
          "matching TS_ISO")
    print("[atomize] NET CERT DELTA: CG 0, MM +3 (2 math MM_STANDARD/MEASURED_MECHANISM, 1 meta "
          "MM_TENTATIVE), HF 0")
    print("[atomize] BCT compat loss v1: cell's own on-disk HARD_PASS verdict CONFIRMED on canonical "
          "(remote official) data (min_ratio_with_bct=0.887>=0.50, quality_retention=0.8362>=0.80). "
          "HEADLINE CORRECTED: citable retention is 83.6%, not the local-preview's 98.9% -- the working "
          "tree's committed blob was a non-canonical preview, silently overwritten post-commit by the "
          "actual remote landing (git status Modified, uncommitted).")
