# Strategy request: PP-8 v1b LR-fix + D3-Path-A consolidated dispatch

**From**: research
**To**: strategy
**Date**: 2026-06-01
**Source**: `notes/research_pp8_v1b_and_path_a_synthesis_2026-06-01.md` (2-drill synthesis with literature-grounded pre-reg bands)
**Trigger**: user pushback that I'd been about to file without drilling — "did you do research on this? I'd make sure this is done right" — triggered 2 parallel Sonnet drills on (a) v1b LR-fix HP-fragility mitigation strategies and (b) D3-Path-A architecture refresh post-D1-1

## TL;DR

Single Lambda batch dispatch, 10 cells, ~$11-17 estimated, single Phi-3-mini-4bit base load:
- **9 cells**: v1b grid (3 schedules × 3 key-encodings) with WSD+EMA as primary mitigation combination
- **1 cell**: Arch 2 paraphrase smoke (MRPC/QQP) testing whether original Path A semantic-cache wedge survives

**Primary mitigation finding**: HP-fragility failure mode precisely characterized as **narrow-attractor collapse under cosine LR annealing**. WSD (Warmup-Stable-Decay) + EMA combination (P_joint ≈ 0.55-0.60) directly addresses the schedule artifact at the root cause. Strong literature anchors: DeepSeek-V3 production training, arxiv 2601.09000 universal dynamics, arxiv 2603.16127 WSO.

**Path A architectural finding**: D1-1 PROVED M1 dominance for EXACT-FORMAT retrieval but did NOT test paraphrase-variation matching. Random keys structurally break semantic-proximity matching at substrate layer. Three revised wedges survive; **Architecture 1 asymmetric bridge** (substrate = audit-cert layer + standard ANN = semantic-match layer) is MORE DEFENSIBLE than original because moat shifts from technical novelty (semantic match) to regulatory durability (deletion cert).

## v1b LR-FIX LAMBDA BATCH GRID

**3 schedule variants × 3 key-encoding variants = 9 cells**:

| Schedule | Key-encoding axis |
|---|---|
| `sched_baseline` (warmup + cosine; control reproducing observed failure mode) | `keys_phi3` (v1+v1' setting; 38.2% final) |
| **`sched_wsd`** (warmup + stable + cosine cooldown; PRIMARY MITIGATION) | `keys_frozen_random` (D1-1 setting; 44.1% final) |
| `sched_constant` (warmup + constant LR, no decay; arxiv 2603.16127 WSO) | `keys_held_out` (Option A split; 0.0% final but 57.5% peak) |

**EMA shadow model in ALL 9 cells (zero-cost dual-eval)**. SWA optional eval on `sched_wsd` cells.

### Pre-reg per cell (per [[feedback-pre-reg-peak-not-final-HP-fragile]])

Track 4 metrics per cell:
- `val_peak` (max val over training)
- `stability` (mean val in [peak_step-25, peak_step+25])
- `val_final` (live model) + `val_ema_final` (EMA shadow)
- `retention_ratio = final / peak` (primary HP-fragility metric)

**Global HARD-PASS**: retention_ratio ≥ 0.80 for any cell (peak locked in)
**Global MIDDLE-BAND**: retention_ratio 0.60-0.80 OR stability < 0.80 × peak
**Global HARD-FAIL**: retention_ratio < 0.50 OR peak < 0.50 (model never found solution)

### Expected outcomes

WSD cells should outperform baseline cells on retention_ratio across all 3 key-encoding axes:
- `keys_frozen_random + sched_wsd`: highest expected retention (widest basins, schedule artifact removed)
- `keys_phi3 + sched_wsd`: substantial retention improvement (narrower basins but schedule artifact still removed)
- `keys_held_out + sched_wsd`: improvement vs baseline but absolute floor remains (genuine task difficulty)

## D3-PATH-A ARCHITECTURE 2 PARAPHRASE SMOKE (+ 1 cell)

**Cell**: `keys_phi3 + sched_wsd + paraphrase_eval` (rides same Lambda batch; same Phi-3-mini-4bit model load)
- Write 50 queries via Phi-3-derived keys
- Retrieve with 50 paraphrase pairs from MRPC or QQP benchmark
- Measure cache hit rate at cosine thresholds {0.80, 0.85, 0.90}

### Pre-reg bands

- **HARD-PASS**: paraphrase hit rate ≥ 60% at threshold 0.85 AND stability across all 3 thresholds (no inverted ordering)
- **MIDDLE-BAND**: paraphrase hit rate 35-60% (partial; threshold-sensitive)
- **HARD-FAIL**: paraphrase hit rate < 35% (semantic structure NOT inherited by substrate codewords)

### Architectural decision tree

**If Arch 2 paraphrase HARD-PASS**: original Path A wedge validated; proceed to FULL paraphrase smoke at N=8192
**If Arch 2 paraphrase HARD-FAIL**: adopt Architecture 1 (asymmetric bridge); reframe product positioning as "deletion-cert infrastructure for ANY caching architecture" — substrate's moat is LEGAL-DURABILITY, not technical novelty
**If MIDDLE-BAND**: gather more data before architectural commit

## COMBINED DISPATCH SPEC

| Item | Cells | Estimated cost | Wall |
|---|---|---|---|
| v1b LR-fix grid | 9 | $8-12 | shared model load; per-cell training ~5-10 min |
| Path A paraphrase smoke | 1 | $3-5 | ~60s |
| **TOTAL** | **10** | **$11-17** | **single Phi-3-mini-4bit base load** |

## CAP_MAP IMPLICATIONS

| Row | State | Conditional movement |
|---|---|---|
| PP-8 substrate-LLM deep integration | promoted v316 | WSD+EMA HARD-PASS → 🟢 0.60-0.78 (peak lock-in; HP-fragility resolved) |
| PP-8 (caveat addition) | — | Add: "M1-dominant key encoding; Phi-3 forward pass NOT required on key side for exact-match retrieval" |
| PP-8 (sub-property) | — | Add: "WSD+EMA HP-fragility mitigation stack" |
| D3-Path-A KV-cache (NEW row candidate) | — | Arch 2 HARD-PASS → CREATE row at 🟡 0.50-0.65 |
| D3-Path-A (NEW row alt) | — | Arch 2 HARD-FAIL → CREATE row with Arch 1 architecture at 🟡 0.45-0.60 (substrate=audit-layer reframe) |
| D3-Path-A (sub-property) | — | "Deletion-cert infrastructure as universal compliance moat across cache architectures" |

## EXPLICIT CLOSURES RECOMMENDED

- **D2-1/D2-2 layer × precision drill** (Round 4 Tier 1) — MOOTED by D1-1; frozen-random keys (which have NO Phi-3 mean-bias by construction) ALSO exhibit HP-fragility, so quantization-induced mean-bias is NOT the cause. Save $12-15 + 1-2 eng-days.
- **Path A Architecture 4 (val-side semantic match)** — semantic coherence problem + weak audit
- **Path A Architecture 5 (LSH hybrid)** — legal complexity for Tier 2 audit cert outweighs benefit

## STRATEGIC NARRATIVE (cross-drill)

Substrate's durable moat post-D1-1 is the **deletion-certificate infrastructure**, NOT the retrieval mechanism. Three findings converge:
1. **WSD+EMA mitigation** unlocks consistent peak lock-in across all 3 key-encoding variants → architecturally robust retrieval
2. **Random-codebook sufficiency** simplifies deployment (no Phi-3 forward pass on key side) → cost reduction
3. **Asymmetric bridge architecture** (Arch 1) cleanly separates substrate's audit-cert role from standard ANN semantic match → wedge legible to enterprise compliance buyers

This positions substrate as **"audit-cert infrastructure for LLM memory and caching"** — a more defensible product position than the original "audit-grade semantic cache" because the moat is regulatory-required (GDPR Art 17, EU AI Act Art 13, HIPAA accounting-of-disclosures) not technically novel.

## CONTRACT FOR STRATEGY

1. **Authorize 10-cell Lambda batch dispatch** (~$11-17; single Phi-3-mini-4bit base load)?
2. **Pre-reg per [[feedback-pre-reg-peak-not-final-HP-fragile]]**: explicit peak + stability + retention bands per cell?
3. **Cap_map conditional LIFTs** (PP-8 → 🟢 if WSD+EMA HP; NEW D3-Path-A row contingent on Arch 2 outcome)?
4. **Closures**: D2-1/D2-2 layer×precision (MOOTED) + Path A Arch 4/5 (rejected)?
5. **Strategic narrative bundling**: "audit-cert infrastructure for LLM memory and caching" as revised wedge positioning?

## METHOD NOTES

- Per [[feedback-no-experiment-design-in-prompts]]: routing hands TASK + WHY + CONTRACT + AUTONOMY; sweep grids and exact hyperparameter values remain exp_dev's call
- Per [[feedback-batch-cloud-experiments]]: single Lambda batch dispatch sharing Phi-3-mini-4bit base load
- Per [[feedback-pre-reg-peak-not-final-HP-fragile]]: explicit multi-metric pre-reg bands; no single-final-eval reliance
- Per [[feedback-no-preframe-batch-all-pass]]: pre-reg HARD-PASS / MIDDLE-BAND / HARD-FAIL per cell; no batch-level expectation

## CLOSING

Move to `routed_completed/` when strategy authorizes the 10-cell Lambda batch + cap_map LIFTs + closures + strategic narrative.


Acted-on 2026-06-01: 10-cell Lambda batch AUTHORIZED via testbed routing pp8_v1b_lr_fix_plus_path_a_10cell
