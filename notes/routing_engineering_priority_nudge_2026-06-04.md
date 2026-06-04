# ROUTING — Engineering priority nudge for multi-channel orchestration test

**From:** Research session
**To:** Orchestrator (primary)
**Date:** 2026-06-04
**Subject:** Status-check on testbed engineering queue; priority recommendation for Experiment C rung 1 (multi-channel orchestration) given it's the load-bearing test of an unvalidated product claim

---

## What this is (plain language)

The substrate's multi-channel training-signal capability claim ("8 channels orchestrated jointly beat 4 channels beat 1 channel during LM training; predicted 15-30% training compute savings") has NOT yet been empirically tested. Experiment C rung 1 (the cheapest, fastest test of this claim) was routed yesterday in `routing_phase_A_now_rung1_brain_inspired_plus_hrc_audit_2026-06-03.md` but isn't engineered yet.

Meanwhile, several other items are also queued for testbed engineering. This note asks orchestrator to surface engineering priority + recommend Experiment C rung 1 moves to first position.

---

## Status check requested

- [ ] What's testbed's current engineering queue order?
- [ ] What ETA does testbed have for the brain-inspired Experiment C rung 1 engineering?
- [ ] What ETA for prior batch (substrate-trained mini LM + curriculum + ICL tiny-scale)?
- [ ] What ETA for paired-pattern dual cf probe + data attribution variation sweep?
- [ ] Is testbed currently engineering Phase 0.5 v1 Rung A scaffold (Llama-3.2-1B Algorithm 1 escalation)?

---

## Why Experiment C rung 1 should be priority

Comparing what's in flight vs what's NOT tested:

**Tested (extensively):**
- Substrate observing live LLM (tier 0): cross-layer composition L=83, drift detection 851×, deletion certificate, spectral gap
- Substrate auditing finished LLM (tier 1): Phase 0.5 v1 Rung 0 PASSed; Rung A about to dispatch

**Designed + queued but NOT TESTED:**
- **Substrate as multi-channel training-signal source (tier 3): Experiment C — the load-bearing test of the 8-channel orchestration claim**
- Substrate as single training-signal source (tier 2): Experiment B
- Substrate as entire training mechanism (tier 6): substrate-trained mini LM

**The multi-channel claim is the LOAD-BEARING product story** for the "substrate-multi-channel-LLM-training" capability narrative. Until Experiment C rung 1 lands a verdict, the 8-channel orchestration claim is a RESEARCH PREDICTION, not a measured capability. Other tests strengthen substrate's audit / observability story, but they don't validate the training-integration story.

**Scope efficiency:**
- Experiment C rung 1: 1-2 layer char-LM ~5-10k params, CPU, ~30 min wall, $0
- Substrate-trained mini LM rung 1: 4-layer char-LM ~10k params, CPU, ~2-3h wall, $0 (also queued)
- Experiment C rung 1 is SMALLER scope + tests a MORE LOAD-BEARING claim

**Engineering shared infrastructure:**
- The tiny char-LM scaffold + substrate observer wiring + 8-channel architecture is shared infrastructure across MULTIPLE pending experiments (Experiment B rung 1, Experiment C rung 1, substrate-trained mini LM rung 1, curriculum learning rung 1, pre-loaded ICL rung 1)
- Engineering Experiment C rung 1 FIRST unlocks scaffold for all the others

---

## Recommended priority order

If testbed has limited engineering bandwidth, the order with highest information per engineering-hour:

1. **Tiny char-LM scaffold + substrate observer wiring** (shared infrastructure; ~4-6h engineering)
2. **Experiment C rung 1** (8-channel orchestration ablation; runs on the scaffold above; ~30 min wall once dispatched)
3. **Experiment B rung 1** (spectral training monitor; same scaffold; ~15 min wall)
4. **Substrate-trained mini LM rung 1** (extends scaffold to substrate-as-training-mechanism; ~2-3h wall)
5. **Curriculum learning rung 1** (extends scaffold; ~2h wall)
6. **Pre-loaded ICL rung 1** (extends scaffold; ~2h wall)
7. **Phase 0.5 v1 Rung A** (Llama-3.2-1B; separate scaffold; ~2-4h wall on remote GPU; runs in parallel)
8. Data attribution variation sweep + paired-pattern dual cf probe (existing scripts; no new engineering)

Total scaffold engineering: ~4-6h. Once engineered, all rung-1 verdicts land within 24h cumulative wall on CPU.

---

## What this changes vs prior routings

Nothing changes in:
- Experimental design (per `routing_phase_A_now_rung1_brain_inspired_plus_hrc_audit_2026-06-03.md` + Phase B overnight routing)
- Pre-registered bands
- Resource targets ($0 throughout)

Only changes:
- Surfaces engineering priority question
- Recommends scaffold-first engineering pattern (shared infrastructure)
- Notes Experiment C rung 1 is highest-information-per-hour test

---

## Strategic context

The substrate-as-training-mechanism narrative has 100+ design choices (channels, σ_k init, gating depth, PCGrad threshold, etc.). At rung 1 ($0, 30 min wall per variant), we can iterate many design variants per day. At cloud rung 4-5 ($5-15/run, hours wall), we couldn't explore the space efficiently. The rung-1-2-first methodology is precisely the right approach — but only if engineering keeps pace.

If testbed engineering bandwidth is limited, the bottleneck shifts from "what experiments to run" (which we have lots of) to "engineering capacity to scaffold them." Worth surfacing back to user if testbed needs additional support.

---

## Discipline declarations

- Per `feedback_routings_address_orchestrator_not_testbed`: orchestrator primary addressee
- Per `feedback_plain_language_experiment_tracking`: experiments described by what they test
- Per `feedback_no_padding_experiments`: this is a priority-surfacing nudge, not a new experiment design
- Per `feedback_small_scale_first_methodology`: rung-1-first methodology requires engineering to keep pace with research design
- Per `feedback_change_request_protocol`: not a change to prior routings; supplemental priority recommendation

---

**END.**

**Orchestrator:** surface testbed engineering ETA + queue order; consider scaffold-first pattern for shared infrastructure; flag back if engineering bandwidth is a bottleneck for the rung-1-first methodology.
