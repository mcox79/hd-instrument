# Pre-reg: phase_diagram_capacity_codebook_separated_v2a_mech_plus_sentinels (RESCUE Cell A; 2026-06-27)

**Anchor:** `phase_diagram_capacity_codebook_separated_v2a_mech_plus_sentinels`
**Cell:** `experiments/exp_phase_diagram_capacity_codebook_separated_v2a_mech_plus_sentinels.py`
**Queue:** `remote_cpu_queue` (NO LOCAL per USER 2026-06-27)
**Tier hint:** CHAIN_GRADE_TRIO candidate (substrate-beats-baseline at high alpha confirmed across 3 seeds + sentinel + bare lift).
**Wave:** Tier-2 rescue from `notes/skunkworks_landed_vet_5cell_batch8_2026-06-27.md` Cell 5 split (A of 2).

## Parent (cell v1) finding being rescued

Skunkworks batch 8 (Cell 5) re-tiered parent as `MEASURED_MECHANISM_MECH_arm_partial`
plus honest-neg OOM cardinality. Off-data .venv recompute confirmed:

| alpha_N | headroom | rec@1 | predicted band | result |
|---------|----------|-------|----------------|--------|
| 0.5 | 10x | 1.000 | [0.99, 1.0] | IN_BAND |
| 0.5 | 2x  | 1.000 | [0.99, 1.0] | IN_BAND |
| 1.0 | 10x | 1.000 | [0.99, 1.0] | IN_BAND |
| 1.0 | 2x  | 1.000 | [0.95, 1.0] | IN_BAND |
| 2.0 | 10x | 1.000 | [0.95, 1.0] | IN_BAND |
| 2.0 | 2x  | 1.000 | [0.85, 0.95] | IN_BAND_at_ceiling |
| **4.0** | **10x** | **1.000** | [0.75, 0.90] | **EXCEEDED** |
| **4.0** | **2x**  | **1.000** | [0.60, 0.80] | **EXCEEDED** |
| **8.0** | **10x** | **1.000** | [0.40, 0.65] | **EXCEEDED** |
| **8.0** | **2x**  | **1.000** | [0.30, 0.55] | **EXCEEDED** |

KNN_SENTINEL + BARE_E_R + MULTI_BANK arms were NaN'd (OOM from MULTI_BANK
K=4 N=16384 evicting GPU memory; sentinels never ran). n_seeds=1.

## Split rescue rationale (Skunkworks rec c + d)

- **Cell A (this file):** MECH + KNN_SENTINEL + BARE_E_R only; 3 seeds; remote_cpu_queue.
  NO multi-bank arm here -> no GPU OOM risk -> CPU runner can complete the
  envelope + exceeded + codebook + sentinel-lift evidence at honest cardinality.
- **Cell B (sibling cell):** MULTI_BANK_K4 at alpha=4 headroom=10x alone;
  3 seeds; overnight_queue (GPU mandate; >8GB VRAM).

## v2a mechanism (UNCHANGED from v1; new band semantics only)

Identical primitive set: bipolar codebook E (V_C * N) + R (V_R * N), Hebbian
ingest W (N * N), bipolar bind keys = E[s] * R[r] * sqrt(N), retrieve via
(W @ keys.T).T @ E.T -> argmax. V_R=32 fixed; alpha_N axis [0.5, 1, 2, 4, 8];
headroom axis [10x, 2x, 1.0x, 0.5x].

## PREDICTED_SURFACE UPDATED (v2a; embeds substrate-beats-baseline finding)

v1 predicted bands at high alpha drilled from prior-N studies; substrate
EXCEEDED at alpha in {4, 8} x headroom in {10x, 2x} (rec=1.000 vs predicted
[0.40, 0.90] floors). v2a tightens to:

| alpha_N | headroom | v1 band | v2a band |
|---------|----------|---------|----------|
| 4.0 | 10x | [0.75, 0.90] | **[0.95, 1.00]** |
| 4.0 | 2x  | [0.60, 0.80] | **[0.95, 1.00]** |
| 8.0 | 10x | [0.40, 0.65] | **[0.95, 1.00]** |
| 8.0 | 2x  | [0.30, 0.55] | **[0.95, 1.00]** |

Other 16 cells unchanged from v1.

## PER-ARM HP-SCOPE (SCHEMA-VET 5b; codified in exp_dev.md 2026-06-27)

| Arm | HP gate | Scope |
|-----|---------|-------|
| MECH (envelope) | HP_ENVELOPE_REC_MIN >= 0.95 | alpha in {0.5,1,2} headroom=10x |
| MECH (exceeded) | HP_EXCEEDED_REC_MIN >= 0.95 | alpha in {4,8} headroom in {10x,2x} |
| MECH (codebook) | HP_CODEBOOK_DELTA >= 0.20 | 1.0x/0.5x columns below 10x at >=3 alphas |
| KNN_SENTINEL | HP_KNN_SENTINEL >= 0.95 | sigma=0.10 sentinel arm only |
| BARE_E_R | HP_BARE_E_R >= 0.99 | bijective encoder arm only |
| MULTI_BANK | EXEMPT (routed to Cell B) | declared in HP_SCOPE.MECH.exempt |

CV_MAX = 0.05 across 3 seeds for any HP-gated cell.

## HARD_PASS tiering (v2a verdict tree)

- **CHAIN_GRADE_TRIO**: envelope HP + exceeded HP + codebook separation all pass.
  Substrate exceeds baseline-predicted-band AND sentinel/bare hold AND
  USER BIAS-Q (suspect 1.000) ruled out by sentinel-lift evidence.
- **CHAIN_GRADE_BOTH**: envelope HP + exceeded HP (codebook may or may not pass).
- **CHAIN_GRADE_ENV_CB**: envelope HP + codebook (no exceeded).
- **MIDDLE_BAND_EXCEEDED_ONLY**: exceeded HP only.
- **MIDDLE_BAND_ENVELOPE_ONLY** / **MIDDLE_BAND_CODEBOOK_ONLY**: one or other.
- **MIDDLE_BAND_NO_HP**: band-floor result (META_RULE_L).

## HARD_FAIL conditions

- Unit exception (META_RULE_J halt-on-error).
- Cardinality breach: observed n_units < EXPECTED_N_UNITS=66 (META_RULE_H).
- Substrate-only violation: any _llm_forward_calls > 0.
- Scoped HP_KNN_SENTINEL or HP_BARE_E_R missed (catch substrate-broke condition).
- BIAS-S regime drift on any mechanism cell (alpha_N / headroom / keys_unique_mode).

## Cardinality (D4 mandatory)

EXPECTED_N_UNITS at full = (20 mech cells + 1 KNN + 1 BARE) * 3 seeds = 66.
META_RULE_H HARD_FAIL on breach. cardinality_ok mandatory; pre-flight selftest
asserts at module load.

## Substrate-only-decode gate

n_llm_forward_calls per arm = 0 (bipolar primitives + Hebbian + cosine
retrieval; no transformers).

## Real data / synthetic provenance

100% synthetic-substrate-bipolar-codebook (no external data).
CORPUS_PROVENANCE = synthetic_substrate_bipolar_codebook_capacity_v2a_mech_plus_sentinels.

## REQUIRED_FIELDS

`verdict`, `verdict_msg`, `elapsed_s`, `summary`, `summary.cardinality_ok` (via
top-level `cardinality_ok`), `detail.surface`, `detail.envelope_pass`,
`detail.exceeded_pass`, `detail.codebook_pass`, `detail.knn_sentinel_mean`,
`detail.bare_e_r_mean`, `HP_SCOPE`.

## Discipline gates

- Fix #26 predispatch: parent v1 anchor in atoms.jsonl; this is split-rescue;
  no duplicate-prevention needed (anchor name differs).
- PROT-018 + PROT-019: no `_n<N>` suffix in anchor (anchor doesn't include
  literal N digits; N is config-only).
- META_RULE_H: cardinality_ok mandatory + asserted in selftest.
- META_RULE_J: no silent except (halt on unit error + write failures to
  metrics + atexit synth).
- META_RULE_K n/a (NO_LOCAL per USER 2026-06-27; selftest + formula asserts
  are gate substitute).
- META_RULE_L: band-floor MIDDLE_BAND not HARD_PASS (preserved verbatim).
- SCHEMA-VET 5b: per-arm HP scope declared in metrics.HP_SCOPE.

## Estimated cost

remote_cpu_queue at N=16384 V_C up to 40960. W=N^2 fp32=1.07GB. 20 mech cells * 3
seeds + 2 sentinels * 3 seeds = 66 units. Per-unit wall ~30-90s on remote_cpu;
total ~30-90 min.

## Routing

`remote_cpu_queue` on marsh@home (NO LOCAL per USER 2026-06-27). Push + queue_add
via orchestrator (push harness-DENIED to exp_dev).

## Suggested --timeout

5400s (90 min) for 66 units * ~60s avg + 50% buffer. Per queue_add formula:
ceil(1.5 * 5400) = 8100s; but remote_cpu is steady-state runner so 5400s is
the honest envelope.
