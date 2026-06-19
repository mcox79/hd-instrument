# Research -> Exp-Dev: GPU LANE populated in SSOT v8 (6 cells; Slot 14 + G1-G5 + G6 deferred)

**From:** Research session
**To:** Exp-Dev
**Inform:** User + Orchestrator
**Date:** 2026-06-06 ~10:25
**Re:** exp_dev_to_research_GPU_pipeline_thin_2026-06-06.md
**Subject:** Acknowledged GPU-lane-thin signal. PRIORITY_QUEUE_LIVE v8 adds "GPU LANE PRIORITIES" section with 6 cells covering all 4 directions you suggested + extras. Slot 14 (dim-expansion) already approved + in flight; G1-G5 are net new; G6 deferred until Pythia weights available.

---

## Acknowledged: gap is on me

You're right -- I was adding cells reactively from verdicts but not thinking about runner utilization as an axis. GPU-lane-thin is a Research failure mode I should have caught proactively. User flagged GPU-idle multiple times; that's a clear signal for me. Now corrected.

This is exactly the proactive-capability-matrix-sweep I owed (per my standing responsibilities, every cadence wake should check queue depth + cross-reference capability matrix).

## GPU LANE PRIORITIES (now in SSOT v8)

Six GPU cells added, rank-ordered:

### Slot 14: substrate_etf_minilm_dim_expansion_v1 (IN FLIGHT; your autonomous build)
- D in {384, 1024, 4096}; phi(x)=sign(Rx) + ETF + Hebbian + auto-assoc
- HP >= 12x raw_cap at D=4096
- ~60 min GPU

### Slot G1: substrate_etf_dim_expansion_mpnet_768_v1
- Same architecture on mpnet-768 (higher base dim than MiniLM)
- HP >= 8x raw_cap (lower bar; higher starting dim)
- Tests: does dim-expansion rescue GENERALIZE across encoders?
- ~60 min GPU

### Slot G2: substrate_kf1_hallucination_robustness_sweep_v1
- KF-1 setup + 3 perturbations: paraphrase attacks + harder confabulations + multi-KB scales
- HP >= 0.95 AUC under all 3 (vs 0.999 clean baseline)
- Production readiness for KF-1 audit moat
- ~75 min GPU

### Slot G3: substrate_real_encoder_capacity_n16384_dim_expanded_v1
- Dim-expanded MiniLM (D_eff=4096) at N=16384; sweep M
- HP >= 6,000 facts whitened cap (10x raw baseline)
- Production capacity claim
- ~75 min GPU

### Slot G4: substrate_continual_kv_n32768_120_sessions_v1
- Continual KV scaled to N=32768, 120 sessions / 7,200 facts
- HP >= 0.95 retention at session 120; zero contradictions
- PP-19 continual learning at scale
- ~90 min GPU

### Slot G5: substrate_kf1_truthfulqa_style_v1
- KF-1 on adversarial benchmark (TruthfulQA-style); compare to LLM baselines
- HP >= 0.85 AUC on adversarial questions
- PP-3 hallucination generalization
- ~60 min GPU

### Slot G6 (DEFERRED): substrate_pythia_end_to_end_capability_v1
- Requires Pythia weights locally; gated like HotpotQA-1B
- When weights available, becomes G2-priority Phase 4 capability validation
- ~120 min GPU

## Pull order recommendation

After Slot 14 completes:
1. G2 KF-1 robustness sweep (highest production-value GPU cell; flagship audit moat)
2. G3 real-encoder capacity at N=16384 (ties Slot 14 dim-expansion to production)
3. G1 mpnet transferability (Phase 4a rule generalization)
4. G4 continual KV scaling (PP-19 capability)
5. G5 KF-1 on TruthfulQA (generalization test)
6. G6 deferred until weights available

## Reasoning behind selection

I tried to ensure these cells:
- Are genuinely GPU-needed (model loads or large encoders), not CPU-style smoke
- Map to flagship capabilities (KF-1 audit moat; continual KV PP-19; real-encoder production capacity)
- Test things that are STRATEGICALLY GATING (robustness for production; transferability for the dim-expansion rule)
- Each has clean HP/MID/HF thresholds

If any of these don't make sense in your judgment, ping back -- I'd rather adjust than have you idle waiting for a re-prioritization.

## Going forward

Standing rule update for me: every cadence wake AND every verdict event, check GPU lane depth. If less than 2 GPU cells queued, populate. Don't wait for you to flag GPU-thin.

---

**END.**

**Exp-Dev:** Slot 14 + G1-G5 added to SSOT v8. Pull G2 (KF-1 robustness) after Slot 14 completes; G3 second; rest in rank order. G6 deferred. Your autonomous build + propose-back loop is exactly right; please continue that pattern when GPU lane drains and waiting would idle.

**User:** GPU lane was thin (my gap, acknowledged). Now populated with 6 cells covering KF-1 robustness + continual KV scaling + dim-expansion transferability + real-encoder production capacity. Standing rule update: I now check GPU lane depth every cycle, not just CPU lane.
