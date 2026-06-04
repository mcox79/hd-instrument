# CHANGE REQUEST — Brain-inspired Experiments B + C recast at rung 1-2 scale first

**From:** Research session
**To:** Testbed
**Date:** 2026-06-03
**Subject:** Recast spectral training monitor + 8-channel orchestration ablation at tiny scale BEFORE any cloud bootstrap

---

## What this is (plain language)

Earlier today I shipped the brain-inspired probe batch (Experiments A + B + C). Experiment A landed on laptop in 43 seconds. Experiments B + C were scaled to GPT-2-small ~117M params on cloud. Pre-launch audit response on Experiment B (your question about GPT-2-small real path) flagged that the code only builds a CharGRU; I recommended Option A (add real GPT-2-small path, 1-2h engineering).

User has redirected the methodology: **we should validate at tiny scale FIRST, only escalate to cloud after the tiny-scale design works.** Reason: iteration speed × cost = where the science happens. Cloud is where the final validation pass happens, not where we figure out what works.

This change request RECASTS Experiments B + C at rung 1-2 scale (CPU, <30 min, $0) before any cloud bootstrap. Option A engineering still happens later (rung 4-5) but only after rung 1-2 verifies the design.

Original routing: `notes/routing_brain_inspired_multi_channel_probe_batch_2026-06-03.md`
Pre-launch audit context: in current research-session conversation history

---

## Status check requested

Before applying changes:

- [ ] Has Option A (GPT-2-small real path) engineering started for Experiment B?
- [ ] Has Experiment C engineering scaffolding started?
- [ ] Has either been dispatched to cloud yet?

Expected: Option A engineering not started; nothing dispatched (pre-launch audit was awaiting research-session call).

---

## The recast — rung-by-rung ladder

### Rung 1 — Tiny char-LM CPU test (~5 min, $0)

**Experiment B at rung 1: Spectral training monitor on 1-2 layer char-LM**

- Model: 1-2 layer LSTM/GRU/tiny-transformer with ~5k-10k params; char-level Shakespeare or simple synthetic corpus
- Substrate observer attached at single hidden state
- Compute κ_2 / κ_3 / κ_4_excess every 5 steps (faster than original 50-step cadence; tiny model trains fast)
- Train for 500-1000 steps
- Annotate ground-truth phases from validation loss
- Measure predictive lead time (substrate fingerprint trajectory crosses threshold N steps before validation-loss-curve crosses corresponding threshold)
- 3 seeds

**Pre-registered bands (same logic, scaled to tiny-LM training duration):**
- HARD-PASS at rung 1: substrate signals each phase change ≥ 20 steps before validation-loss indicator AND across 3 seeds
- MIDDLE: lead time 10-20 steps OR 2/3 seeds
- HARD-FAIL: substrate signal lags or matches validation loss

**Outcome interpretation:**
- HP at rung 1 → design works at tiny scale; escalate to rung 2-3 with confidence
- MIDDLE at rung 1 → design needs tuning (which substrate cumulant carries the predictive signal? which gating threshold?); iterate cheaply at rung 1
- HF at rung 1 → design is broken at tiny scale; do not escalate (would burn cloud budget on a known-broken design)

**Experiment C at rung 1: 8-channel orchestration ablation on tiny char-LM**

- Same 1-2 layer char-LM scaffold
- 3 channel-count conditions: 1-channel (CE baseline) / 4-channel (CE + 3 substrate) / 8-channel (CE + 7 substrate)
- 1000 training steps per condition
- 3 seeds per condition
- Metric: validation cross-entropy (simpler than BLiMP for tiny LM) + per-channel gradient norm + per-channel σ_k weight at convergence

**Pre-registered bands:**
- HARD-PASS at rung 1: 8-channel beats 1-channel by > 5% on validation CE AND beats 4-channel by > 2% AND no majority-antagonistic channel pairs detected AND gradient norm > 1% of input
- MIDDLE: 8-channel beats 1-channel by > 2% but < 5% OR doesn't beat 4-channel
- HARD-FAIL: 8-channel < 4-channel OR PCGrad projection collapses gradient norm < 1% OR 8-channel fails to converge

**Wall:** rung 1 takes ~5 min per experiment × 3 conditions × 3 seeds. Total ~45 min on CPU.
**Cost:** $0
**Information per dollar:** infinite improvement over cloud rung 5.

### Rung 2 — Validate at depth (4-layer char-LM, ~30 min CPU, $0)

Run the rung-1 PASS designs at 4-layer char-LM (~100k params). Confirms the orchestration pattern holds with depth. 30-60 min per experiment on CPU.

### Rung 3-5 — Only after rung 1-2 PASS

Rung 3: 4-layer subword-LM at ~1-5M params (laptop GPU, ~1-2h, $0)
Rung 4: Pythia-70M cheap cloud (~$1-2, ~2-4h)
Rung 5: GPT-2-small ~117M on cloud (~$3-5, ~3-6h) — ONLY if rungs 1-4 all PASS

---

## Why this is the right move

**Information per dollar.** At rung 1 ($0, 5 min), we can run 100+ design variants per day. At rung 5 ($5, 4h), we can run ~5 design variants per day. The 8-channel orchestration has ~100 design choices (channel selection, σ_k init, gating depth, PCGrad threshold, layer-zone gain, tonic/phasic split). At cloud-scale-first methodology, we'd hit budget before exploring half of them.

**Failure-mode isolation.** At rung 1, we can stare at each channel's gradient flow individually. Which channel dominates? Which one gets zeroed by PCGrad? Which σ_k saturates? At cloud-scale, channels mix and we can't see individual behaviors — only the final loss.

**De-risk before spend.** If the 8-channel orchestration design is fundamentally broken at tiny scale, we waste $5-15 finding out at cloud scale. If it works at tiny scale and we have to recast at cloud scale, we waste 0 cloud dollars and gain confidence.

**Methodology lock-in.** This becomes a standing rule: rung 1-2 first for ANY novel substrate-LLM-coupling design, regardless of how exciting the cloud-scale claim is. The brain-inspired 8-channel claim is a perfect test case.

---

## What stays unchanged

- **Phase 0.5 v1 relaunch stays at Llama-3.1-8B** (scale-locked to Hyperprobe published probe at arXiv:2509.25045; cannot iterate at smaller scale because the probe specification IS the published benchmark)
- **Experiment A result stands** (rho=0.69 at 4.16× speedup; MIDDLE; data attribution variation sweep redesigned per drill 2 already shipped to testbed)
- **Cost ceiling stays $15-20** for the eventual cloud rung 4-5 runs IF rung 1-2 pass
- **Pre-registered bands logic unchanged** (just scaled to rung-appropriate training durations)

---

## IF NOT YET dispatched / engineered → apply this recast

Engineer rung 1 scaffolds for Experiment B + Experiment C on CPU. Run both. Surface results. Decide whether to escalate to rung 2-3 based on rung 1 outcome.

Sequence:
1. Rung 1 Experiment B (spectral monitor on tiny char-LM) — 15 min
2. Rung 1 Experiment C (8-channel ablation on tiny char-LM) — 30 min
3. Rung 1 verdict synthesis — surface to research
4. IF either HP at rung 1 → engineer rung 2 (4-layer char-LM); run; verdict
5. ONLY after rung 1-2 PASS → consider Option A GPT-2-small engineering for rung 4-5 cloud bootstrap

---

## IF Option A engineering ALREADY STARTED → pause it

If Option A (GPT-2-small real path) engineering has started, pause it. Rung 1-2 design verification comes first. Option A engineering effort is not wasted (still needed for rung 4-5), just sequenced later.

---

## IF ALREADY DISPATCHED → abort and recast

If any cloud dispatch happened, abort it. Burn-rate at cloud scale on an unvalidated design isn't justified when rung 1 CPU validation is $0.

---

## Discipline declarations

- Per `feedback_change_request_protocol`: status check first; both-cases instructions
- Per `feedback_plain_language_experiment_tracking`: experiments described by what they test at each rung
- Per `feedback_skills_first_for_rote_work`: methodology lock-in becomes a memory rule (separate file)
- Per `feedback_no_padding_experiments`: each rung is a specific de-risk step before the next-larger-scale spend
- Per `feedback_obey_user_pause_explicitly`: methodology change user-authorized 2026-06-03

---

**END.**

**Testbed:** apply per "NOT YET dispatched" branch (expected case). Surface rung 1 results when both Experiment B and C land. Escalation to rung 2-3 only after rung 1 PASS.

**Research session:** if rung 1 PASS, ship rung-2 routing. If MIDDLE/HF, ship rung-1 variant sweep (cheaper to iterate than escalate).
