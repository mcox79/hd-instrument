# ROUTING — Phase B overnight batch (remote CPU + GPU)

**From:** Research session
**To:** Testbed
**Date:** 2026-06-03
**Status:** USER AUTHORIZED 2026-06-03 (overnight; $0 remote + ~$50 cloud if Algorithm 1 ready); dispatch sequence per § 2 below.

---

## What this batch is (plain language)

User stopped both cloud experiments today and adopted the rung-1-2-first methodology. Phase A is running rung-1 brain-inspired validation NOW on laptop CPU (~45 min). This Phase B routing pre-stages the OVERNIGHT batch — testbed dispatches per the conditional sequence in § 2 once Phase A verdicts land.

Goal: load 10-15 hours of overnight CPU work AND prepare the one cloud-scale-locked experiment for overnight GPU IF engineering ready.

---

## Resource breakdown

- **Remote CPU runner (testbed-managed)**: rung-2 brain-inspired escalations + already-shipped variation sweep + already-shipped paired-pattern dual probe + prior batch tiny-scale runs. Total ~10-15 hours CPU. Cost $0.
- **Remote GPU**: not needed for this batch; substrate-physics queue continues separately.
- **Cloud GPU overnight**: Phase 0.5 v1 relaunch with Algorithm 1 + user's bug fixes — IF engineering ready by EOD. Cost ~$50. Scale-locked at Llama-3.1-8B per Hyperprobe paper.

---

## § 1 — What's already in testbed queue from prior routings

These were shipped earlier today; testbed dispatches as bandwidth allows:

1. **Data attribution variation sweep redesigned per drill 2** (`change_request_data_attribution_variation_sweep_drill2_redesign_2026-06-03.md`) — 18 cells, ~20 min CPU, $0. Tests rank-2 Woodbury + LOO ground truth + TRAK-style ensemble vs current rank-1 baseline.
2. **Paired-pattern dual cf probe per drill 1** (`routing_paired_pattern_dual_cf_probe_2026-06-03.md`) — 6 cells, ~2h CPU, $0. Empirically tests substrate's genuine cf sensitivity with paired-pattern dual measurement.

Both fit overnight queue. Dispatch when convenient — no conditional gating needed.

---

## § 2 — Phase A conditional gating (NEW rung-2 escalations)

If Phase A rung 1 verdicts land tonight, escalate to rung 2 on remote CPU per these conditionals:

### IF Phase A Experiment B rung 1 = HARD-PASS → dispatch B rung 2

**Anchor name:** `substrate_spectral_training_monitor_rung2_4layerchar_v1_n4096`

**Test:** spectral training monitor at 4-layer char-LM (~100k params).
- Same κ_2 / κ_3 / κ_4_excess measurement protocol as rung 1
- 4-layer transformer or LSTM; char-level corpus
- ~3000 training steps with held-out validation
- Measure predictive lead time (substrate fingerprint crosses threshold N steps before validation-loss-curve)
- 3 seeds
- Wall: ~60 min CPU. Cost $0.

**Pre-registered bands (scaled to rung 2):**
- HP: substrate signals ≥ 50 steps before validation indicator AND across 3 seeds
- MIDDLE: lead 20-50 steps OR 2/3 seeds
- HF: substrate lags or matches validation

### IF Phase A Experiment C rung 1 = HARD-PASS → dispatch C rung 2

**Anchor name:** `substrate_8channel_orchestration_rung2_4layerchar_v1_n4096`

**Test:** 8-channel orchestration at 4-layer char-LM (~100k params).
- 3 channel-count conditions: 1 / 4 / 8 channels
- Same channel architecture as rung 1 (4 tonic + 4 phasic)
- ~3000 training steps per condition
- 3 seeds per condition
- Metric: validation CE + per-channel gradient norm + per-channel σ_k at convergence
- Wall: ~90 min CPU. Cost $0.

**Pre-registered bands:**
- HP: 8-channel beats 1-channel by > 5% on val CE AND beats 4-channel by > 2% AND no antagonistic channel pairs AND gradient norm > 1% AND 3/3 seeds
- MIDDLE: 8-channel beats 1-channel by 2-5% OR doesn't beat 4-channel OR 2/3 seeds
- HF: 8-channel < 4-channel OR PCGrad collapses gradient OR fails to converge

### IF EITHER A1 or A2 MIDDLE/HF at rung 1 → variant sweep at rung 1 instead of escalating

Do NOT escalate to rung 2 on a broken design. Run 4-6 variant cells at rung 1 (different σ_k initialization, different gating depth, different PCGrad threshold) to identify what fixes the issue cheaply. Cost $0, wall ~30 min total.

---

## § 3 — Prior batch tiny-scale recast (substrate-trained mini LM + siblings)

The prior 3-experiment batch authorized earlier (substrate-trained mini LM, curriculum learning, pre-loaded ICL) was scaled cloud-class. Per the rung-1-2-first methodology, recast all three at rung 1-2 first:

### Experiment 1 — substrate-trained mini LM at rung 1-2

**Anchor name:** `substrate_trained_mini_lm_rung1_tinychar_v1`

**Test:** 2-layer character-level mini LM trained ENTIRELY via substrate operations (no gradient descent).
- ~5k-10k params
- Char-level Shakespeare or simple synthetic corpus
- Substrate primitives: outer-product Hopfield write, anti-Hebbian, hippocampal place tag, multi-bank addressing
- Defensive design per cascade drill: sparse coding regime ~5% activity, binary activations only, explicit α-budget accounting
- Pre-flight watchlist signature checks (BPC plateau, ||W||_2 exponential growth, retrieval accuracy on held-out probe)
- 500-1000 substrate training cycles
- 3 seeds
- Wall: ~2-3h CPU. Cost $0.

**Pre-registered bands:**
- HP: validation BPC ≤ 2.5 nats AND no watchlist signature triggers AND 3/3 seeds
- MIDDLE: BPC 2.5-3.5 OR 2/3 seeds OR 1 watchlist trigger
- HF: BPC > 3.5 OR collapse (BPC trends toward chance 5.5+) OR multiple watchlist triggers

### Experiment 2 — substrate curriculum learning at rung 1

**Anchor name:** `substrate_curriculum_learning_rung1_tinychar_v1`

**Test:** substrate-driven curriculum scheduling for tiny char-LM training.
- 2-layer char-LM ~5k-10k params; standard gradient training
- Substrate observer scores per-batch difficulty via per-channel signal
- Curriculum: easy → medium → hard batches ordered by substrate score
- Baseline: random batch order
- ~2000 training steps per condition (curriculum vs baseline)
- 3 seeds per condition
- Wall: ~2h CPU. Cost $0.

**Pre-registered bands:**
- HP: curriculum beats random by > 5% on val CE AND across 3 seeds AND no instability
- MIDDLE: 2-5% gain OR 2/3 seeds
- HF: curriculum matches or trails baseline

### Experiment 3 — substrate-preloaded ICL at rung 1

**Anchor name:** `substrate_preloaded_icl_rung1_tinychar_v1`

**Test:** pre-loaded substrate as in-context learning prior for tiny char-LM.
- Substrate pre-loaded with K stored character-pair bindings
- Tiny char-LM (2-layer, ~5-10k params) reads substrate via attention
- Compare: (a) no pre-loaded substrate baseline, (b) pre-loaded substrate at K=10/100/1000
- Per-task-SHARED substrate (per earlier orchestrator clarification, not per-problem-fresh)
- Standard ICL eval: held-out character-pair completion accuracy
- 3 seeds per condition
- Wall: ~2h CPU. Cost $0.

**Pre-registered bands:**
- HP: K=100 or K=1000 condition beats no-substrate baseline by > 10% on completion accuracy AND across 3 seeds
- MIDDLE: 5-10% gain
- HF: pre-loaded substrate matches or trails baseline

**Sequence:** these three can run in parallel on remote CPU if bandwidth allows; otherwise serial. Total ~6-7h sequential.

---

## § 4 — Phase 0.5 v1 cloud overnight (CONDITIONAL on engineering)

### IF user's 3 code bug fixes are done by EOD AND Algorithm 1 embedding pipeline implementation is engineered → dispatch overnight

**Anchor name:** `phase05_v1_llama_audit_relaunch_with_algorithm1_v1`

**Test:** Phase 0.5 v1 relaunch with the three drill-1-identified changes:
1. 3-stage embedding pipeline per Algorithm 1, Appendix B of Hyperprobe paper (k-means over layers 16-32 + sum-pool centroids k=5)
2. Extended training schedule: ~421 epochs target, early-stop patience 100, LR=3e-5
3. (Optional) attention-augmented residual blocks num_heads=8

**Resource:** cloud H100 (SXM5 recommended for wall savings; PCIe acceptable)
**Wall:** ~8-12h overnight
**Cost:** under $50 per drill estimate

**Pre-registered bands:**
- HP: val_sim ≥ 0.85 (relaxed) OR ≥ 0.89 (paper-match)
- MIDDLE: val_sim 0.75-0.85
- HF: val_sim < 0.75 → substrate-LLM coupling tests cannot be cleanly interpreted; surface to research for design rework

### IF Algorithm 1 engineering NOT ready by EOD → hold cloud dispatch

Do NOT dispatch Phase 0.5 v1 on the old pipeline. Same 60% ceiling would burn $50 for no new information. Algorithm 1 implementation can engineer in parallel with rung-1-2 work; flag back to research when ready.

**Engineering scoping for Algorithm 1 (testbed):**
- K-means over Llama-3.1-8B layers 16-32 residual streams (sklearn.cluster.KMeans or torch native)
- Sum-pool centroids k=5
- Use this as probe input pipeline (replace prior single-layer residual extraction)
- Reference: arXiv:2509.25045 Appendix B Algorithm 1
- Estimated engineering: 4-8h with testing

If engineering exceeds 8h, surface back to research — may not justify the cloud spend tonight; defer to tomorrow's overnight.

---

## § 5 — Total overnight resource use

**Remote CPU (10-15 hours of work):**
- Data attribution variation sweep redesigned: ~20 min
- Paired-pattern dual cf probe: ~2h
- IF Phase A B rung 1 PASS: B rung 2 ~60 min
- IF Phase A C rung 1 PASS: C rung 2 ~90 min
- Substrate-trained mini LM rung 1-2: ~2-3h
- Substrate curriculum learning rung 1: ~2h
- Substrate-preloaded ICL rung 1: ~2h
- TOTAL: ~10-12 hours CPU (less if parallel bandwidth allows)

**Cloud GPU overnight (CONDITIONAL):**
- Phase 0.5 v1 relaunch: ~8-12h, ~$50 IF Algorithm 1 engineering ready

**Remote GPU:** substrate-physics queue continues separately; not overlapping with this batch.

---

## § 6 — Status synthesis tomorrow morning

Research session synthesizes overnight verdicts in the morning:
- Phase A rung 1 verdicts (B + C)
- Phase B rung 2 verdicts (B + C, conditional)
- Data attribution variation sweep verdict
- Paired-pattern dual cf probe verdict
- Substrate-trained mini LM verdict
- Curriculum learning verdict
- Pre-loaded ICL verdict
- Phase 0.5 v1 relaunch verdict (if dispatched)

Up to 10 verdicts landing overnight. Substantial design-validation progress in one cycle.

---

## Discipline declarations

- Per `feedback_small_scale_first_methodology`: rung-1-2 first; cloud is last validation pass
- Per `feedback_change_request_protocol`: this is a NEW batch routing combining pre-shipped items + new conditional escalations; status-check first per § 2 conditional gating
- Per `feedback_plain_language_experiment_tracking`: experiments described by what they test
- Per `feedback_no_padding_experiments`: each item closes a specific design-validation question
- Per `feedback_no_smoke_preframing_in_task_prompts`: HP/MID/HF bands explicit per cell
- Per `feedback_obey_user_pause_explicitly`: overnight batch user-authorized 2026-06-03
- Per `feedback_batch_cloud_experiments`: cloud overnight is single Phase 0.5 v1 run (no batching possible at this scale)
- Per `feedback_testbed_progress_logging_and_restart`: per-cell partial JSON for all rung-1-2 work
- PROT-018: anchor names use rung-tier-prefix + descriptor + _v1 family

---

**END.**

**Testbed:** § 1 already-shipped items dispatch as bandwidth allows. § 2 rung-2 escalations dispatch conditional on Phase A verdicts. § 3 prior-batch tiny-scale recast dispatches in parallel with the rest. § 4 cloud overnight dispatches IF engineering ready by EOD; else hold and surface engineering ETA back to research.

**Research session:** holds for overnight verdicts; synthesizes morning.

**User:** ~10 verdicts landing overnight; will summarize each + strategic implications in morning standup.
