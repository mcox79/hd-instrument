# Skunkworks landed-VET batch 8 (5 cells) — 2026-06-27

**Scope:** 5 HARD_FAIL cells (all metrics.json SCP'd back locally by orchestrator a69069a8cf3bb7df6). Per Fix #28 verify-per-arm-not-verdict-msg discipline + recurring "Skunkworks overrides Director on by-construction-saturation" pattern: all 5 cell-author verdicts examined off-data; tiers re-classified where data supports it.

**Net:** CERT N unchanged (live CERT N=619 chain-grade); ledger rows +5 (1 measured_mechanism + 4 honest_negative).

**Atomizer:** `tools/atomize_skunkworks_5cell_batch8_landed_vet_2026-06-27.py`
**Ledger:** 5 rows appended to `data/substrate_index/meta/cert_ledger.jsonl` (ts 1782550116 – 1782550221).

---

## Cell 1: typed_multibank_K128_adversarial_v1

**Cell verdict:** `HARD_FAIL by_construction_saturation_META_RULE_K: baseline=0.9978 >= Q_SUSPECT_SATURATION=0.95`

**Skunkworks tier:** **HONEST_NEGATIVE_MECHANISM_FAILS** (delta=0)

**Why re-tier (UNDER-claim direction wrong here, NOT under-claim direction):** cell-author verdict is too gentle. Per-arm 3-seed evidence (verified off-data .venv recompute):
- ARM_UNTYPED_BASELINE_ADVERSARIAL: recall=[0.9977, 0.9978, 0.9978] mean=0.9978
- ARM_TYPED_ROUTING_MATCHED: recall=[0.4451, 0.4210, 0.4523] mean=0.4395 cv=0.0305
- ARM_TYPED_ROUTING_ADVERSARIAL_PROBE: refuse=[0.2003, 0.1129, 0.0957] mean=0.1363 cv=0.336

TWO rails fail:
1. typed_lift = -0.5583 (typed arm 56pp WORSE than baseline; HP_typed_lift>=0.10 missed by 65pp)
2. refuse_rate = 0.1363 (HP_refuse_rate_min=0.85 missed by 71pp; 86% of adversarial features WRONG-route)

This is NOT just baseline-saturation — the typed arm comes in at 0.44 (far below saturation), so it IS being exercised in a discriminating regime. The mechanism ACTIVELY HURTS recall at OVERLAP=0.40 N_BANKS=128. Cv on typed arm = 0.0305 < cv_chain_grade_max — the negative finding IS chain-grade-quality measurement.

**Atom:** `math::T3/EXP_typed_multibank_K128_adversarial_v1_HONEST_NEGATIVE_MECHANISM_FAILS_...`

**Flag-back to Research / exp_dev:**
- typed_multibank K=128 mechanism does NOT work at OVERLAP=0.40. Follow-up paths:
  - (i) Sweep OVERLAP from 0.0 to 0.40 to find break point
  - (ii) Harder baseline regime (drop to band [0.60, 0.85]) so lift is observable
- Refuse gate at K_per_bank=64 is broken: 86% wrong on adversarial features. Consider K_per_bank sweep + refuse-threshold ablation.

---

## Cell 2: gap3_cls_two_tier_BCM_slow_replay_v1

**Cell verdict:** `HARD_FAIL methodology_drift: ARM_BASELINE_SINGLE_W=1.0000 >= HF_BASELINE_MAX=0.5 cross-cell rail violated`

**Skunkworks tier:** **HONEST_NEGATIVE_BCM_AT_CHANCE_PLUS_REGIME_DRIFT** (delta=0)

**Why re-tier:** cell-author verdict only catches finding (a) baseline regime drift. There are TWO stacked findings (per-arm verify):
- ARM_BASELINE_SINGLE_W: heldout_acc=[1.0, 1.0, 1.0] cone_cosine=[1.0, 1.0, 1.0] — baseline TOO EASY (HP_BASELINE_MAX=0.5 violated by 50pp)
- ARM_TWO_TIER_HEBBIAN_SLOW: heldout_acc=[1.0, 1.0, 1.0] cone_cosine=[0.458, 0.459, 0.460] entropy_delta=[1.609, 1.609, 1.609] — Hebbian arm holds + measurable compression
- **ARM_TWO_TIER_BCM_SLOW: heldout_acc=[0.20, 0.20, 0.20] = CHANCE (1/N_CAT=5); cone=0.0; entropy_delta=0.0**
- **ARM_TWO_TIER_BCM_GENERATIVE_REPLAY: heldout_acc=[0.20, 0.20, 0.20] = CHANCE; cone=0.0**

Even at harder regime, finding (b) would STILL hold: BCM mechanism ACTIVELY FAILS to learn while Hebbian arm holds at SAME regime. compression_happened=False; max_abs_cor_score_w_mag=0.0. BCM wipes the weight signal entirely.

**Atom:** `math::T3/EXP_gap3_cls_two_tier_BCM_slow_replay_v1_HONEST_NEGATIVE_BCM_AT_CHANCE_PLUS_REGIME_DRIFT_...`

**Flag-back to Research / exp_dev:**
- BCM two-tier mechanism does NOT work out-of-box at (eta_slow=0.0010, theta_window=200, N_REPLAY=5000). Two-tier INFRA is functional (Hebbian arm works); issue specific to BCM update rule.
- Hypothesis: theta_window=200 drives theta past discriminative regime — post-activity always sub-threshold → weights pruned to 0.
- Follow-up: (i) ablate eta+theta_window jointly (try eta=1e-4, theta_window=20-50); (ii) pre-condition BCM theta on Hebbian-pretrained W (not zero-init); (iii) FIRST harden baseline regime past HP_BASELINE_MAX=0.5.

---

## Cell 3: kb_coarse_grain_at_promotion_v3_self_contained

**Cell verdict:** `HARD_FAIL n_ud_in_sample=0 < 10 (RC-1 invariant: test would be vacuously satisfied like v1)`

**Skunkworks tier:** **HONEST_NEGATIVE_INFRA_DEP_MEMORY_DIR_NOT_IN_REPO** (delta=0)

**Why this tier (not chain-grade rescue):** v3 was intended to rescue batch-7 v2 infra-dep by being self-contained, but the self-contained build walks `<repo>/{note,memory,prereg}/` and `<repo>/memory/` doesn't exist. Per-class manifest (verified):
- `memory: n_files=0  n_chunks=0  n_files_zero_chunks=0` (discovery succeeded; directory empty)
- `note:   n_files=200 n_chunks=1138 n_files_zero_chunks=0`
- `prereg: n_files=200 n_chunks=1061 n_files_zero_chunks=1`

`chunk_classes_ingested = ['note', 'memory', 'prereg']` (manifest claims memory included).
`ud_source_class = 'chunk_memory'` (UD label requires memory chunks → 0 → RC-1 halt).

Filesystem-verified by Skunkworks: `ls memory/` empty; `ls C:/dev/hd-instrument/memory/` empty; `ls ~/.claude/projects/d--AI/memory/` → MEMORY.md + 50+ topic files. PATH-SCOPE bug.

**v3 RC-1 invariant IS WORKING AS DESIGNED:** v1 vacuously passed with 0 UDs; v3 EXPLICITLY refuses to run vacuous mechanism. The cell design improvement is correct; only the path-scope of the self-contained build is wrong.

**Atom:** `math::T3/EXP_kb_coarse_grain_at_promotion_v3_self_contained_HONEST_NEGATIVE_INFRA_DEP_MEMORY_DIR_NOT_IN_REPO_...`

**Flag-back to Research / exp_dev:**
- v4 rescue paths (recommend b+a):
  - (a) Pull memory class from `~/.claude/projects/d--AI/memory/` cross-profile read (fallback)
  - (b) Add content-based UD-detection heuristic (files containing 'USER:' / 'USER directive' / 'USER-locked' markers) — preserves self-contained principle
  - (c) Pre-seed inline KB with hand-curated UD canonical set bundled with cell
  - (d) Use canonical-KB UD atoms via tool-helper (simplest but breaks self-contained)

---

## Cell 4: edge_importance_retrieval_trace_x_ultrametric_coreness_v3p1_ULTRA_tuned

**Cell verdict:** `HARD_FAIL: D3 caught setup exception seed=7: META_RULE_K coreness-fires FAIL: coreness_atoms=0 at seed=7 with ULTRA_COS=0.7, ULTRA_MIN_SIZE=3. v3.1 cell is DEGENERATE at these thresholds`

**Skunkworks tier:** **HONEST_NEGATIVE_ULTRAMETRIC_CLUSTER_GEOMETRY_MISMATCH** (delta=0)

**Why this tier:** discriminator (META_RULE_K coreness-fires) is the cell-author's own pre-flight assertion designed to PREVENT v3's silent-reduce-to-TRACE bug. It fired correctly in protective direction. The honest negative is: REAL substrate atom-cluster geometry doesn't cluster tight enough for ULTRA_COS in [0.7, 0.85] at MIN_SIZE in [3, 5] regardless of tuning.

Per-seed (all 3 halted at setup; arms_count=0):
- seed=7: elapsed=1.429s coreness_atoms=None
- seed=17: elapsed=1.381s coreness_atoms=None
- seed=23: elapsed=1.266s coreness_atoms=None

Synthetic selftest at sigma=0.02 passes; real atoms have wider intra-cluster spread (char-trigram encoder hypothesis — same "encoder is THE bottleneck" theme from 2026-06-23).

**Pivot signal: TRACE-only path is clean.** Sister cell `exp_edge_importance_v3_D1_alternative_discriminators_v1` already showed TRACE D1_AUC=1.000 WITHOUT ULTRA composition. ULTRA was a 2-axis hardening attempt that turns out brittle to real atom geometry.

**Atom:** `math::T3/EXP_edge_importance_retrieval_trace_x_ultrametric_coreness_v3p1_ULTRA_tuned_HONEST_NEGATIVE_ULTRAMETRIC_CLUSTER_GEOMETRY_MISMATCH_...`

**Flag-back to Research (authority call):**
- (a) DROP ULTRA composition from edge-importance series; commit to TRACE-only path (RECOMMENDED)
- (b) IF ULTRA desired as separate cell: raise N≥4096 + denser encoder (word2vec/sparse-bipolar)
- (c) IF retaining v3.1 arch: remove META_RULE_K coreness-fires assertion OR downgrade to MIDDLE_BAND_WARN (since silent-degrade to TRACE-only IS the intended fallback per ULTRA composition design)

---

## Cell 5: phase_diagram_capacity_codebook_separated_envelope_v1

**Cell verdict:** `HARD_FAIL_UNIT_EXCEPTION: 1 units raised exceptions (META_RULE_J)`

**Skunkworks tier:** **MEASURED_MECHANISM_MECH_ARM_PARTIAL** plus honest-neg OOM cardinality (delta=0)

**Why MEASURED_MECHANISM (not HONEST_NEG-only):** 10 MECH-arm units DID complete and produced consistent, surprising data — 4 of 10 cells EXCEEDED predicted band. Substrate is OUT-PERFORMING the pre-reg surface at high alpha:

| Cell | V_C | M | rec@1 | pred band | result |
|------|-----|---|-------|-----------|--------|
| alpha=0.5 10x | 2560 | 8192 | 1.0 | [0.99, 1.0] | IN_BAND |
| alpha=0.5 2x | 512 | 8192 | 1.0 | [0.99, 1.0] | IN_BAND |
| alpha=1.0 10x | 5120 | 16384 | 1.0 | [0.99, 1.0] | IN_BAND |
| alpha=1.0 2x | 1024 | 16384 | 1.0 | [0.95, 1.0] | IN_BAND |
| alpha=2.0 10x | 10240 | 32768 | 1.0 | [0.95, 1.0] | IN_BAND |
| alpha=2.0 2x | 2048 | 32768 | 1.0 | [0.85, 0.95] | IN_BAND_at_ceiling |
| **alpha=4.0 10x** | 20480 | 65536 | **1.0** | [0.75, 0.9] | **EXCEEDED** |
| **alpha=4.0 2x** | 4096 | 65536 | **1.0** | [0.60, 0.8] | **EXCEEDED** |
| **alpha=8.0 10x** | 40960 | 131072 | **1.0** | [0.40, 0.65] | **EXCEEDED** |
| **alpha=8.0 2x** | 8192 | 131072 | **1.0** | [0.30, 0.55] | **EXCEEDED** |

All 10 used keys_unique_mode='unique_sr' (consistent with batch-7 capacity_sweep_n16384 unique_sr zone).

**Why NOT chain-grade promotion (Fix #28 under-claim):**
- n=1 seed (only seed=11; seeds=13,19 never started due to upstream OOM halt)
- KNN_sentinel arm = NaN (never ran)
- BARE_E_R arm = NaN (never ran)
- MULTI_BANK arms = NaN (OOM at first cell)
- USER BIAS-Q applies to exceed-band at rec=1.0: NEEDS sentinel arm to rule out saturate-by-construction confound

**OOM root cause:** W matrix at N=16384 fp32=1.07GB. MULTI_BANK_K4 keeps 4 W matrices simultaneously = 4.28GB W alone + V/K matrices for shard ingestion exceeds 6.80GB GPU budget. Cell DESIGN_NOTE acknowledges 'W=N^2 fp32=1.07GB' but didn't account for multi-bank multiplier.

**Atom:** `math::T3/EXP_phase_diagram_capacity_codebook_separated_envelope_v1_MEASURED_MECHANISM_MECH_arm_partial_...`

**Flag-back to Research / exp_dev / orchestrator:**
- Rescue paths (recommend c+d):
  - (a) Memory-frugal multi-bank: K_banks=2 instead of 4 OR torch.cuda.empty_cache() between slots OR bf16/fp16 W
  - (b) Sequential not parallel multi-bank: ingest one-at-a-time, free W between
  - (c) **Split into 2 cells**: MECH+KNN+BARE (small) + MULTI_BANK alone (large)
  - (d) **Route MULTI_BANK to remote GPU with >8GB VRAM via hdi_orchestrator** (per Fix #24)
- The MECH-arm exceed-band finding IS chain-grade-eligible after sentinel arm runs + 3-seed replication.

---

## Compliance + provenance summary

- All 5 cells verified off-data via .venv recompute (`tools/atomize_skunkworks_5cell_batch8_landed_vet_2026-06-27.py` `--apply`)
- Atoms tier-tagged with `cert_status` (5 of 5) and `cert_class` (5 of 5) — coordination-ready post-cert_ledger.jsonl migration
- Ledger rows include `referent_pointer` (notes_path + metrics_path + atom_qualified_id) per A5 discipline
- A5 PRE→POST CERT N delta = 0 (verified)
- All 5 atoms round-trip-survive at intended provenance_quality (verified)

## Recurring pattern this batch

Per recurring "Skunkworks overrides Director on by-construction-saturation" pattern (feedback_fix28_recurring_skunkworks_correct_more_than_director_2026-06-23):
- Cell 1 cell-author UNDER-claimed: it's not just baseline-too-easy; it's mechanism-actively-hurts
- Cell 2 cell-author UNDER-claimed: it's not just regime-drift; BCM is at chance
- Cell 5 cell-author UNDER-claimed: 10 MECH units exceeding predicted bands deserves MEASURED_MECHANISM, not just HARD_FAIL_OOM
- Cells 3, 4 cell-author verdicts ACCURATE; only tier-label refined

3 of 5 cells: per-arm verify revealed STRONGER findings than verdict_msg claimed. The Fix #28 pattern continues to hold: cell-author verdict_msg is summarization-lossy; per-arm metrics.json read is load-bearing.
