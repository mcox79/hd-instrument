# Research request — Bet B retention ceiling: FIFTH-MECHANISM candidate

**From**: Orchestrator inline cycle (2026-05-24 14:45 local; verdict_handler role inline)
**To**: Research (next cycle)
**Triggering verdict**: v188 LONGER_PHASEA_MIDDLE_BAND (FOURTH converging-PARTIAL probe in Bet B retention rehab sequence; intrinsic compound ceiling at 91-92% CONFIRMED across four mechanism families)
**Cap_map**: v188 (commit d905aa3 local)

## The question (Research designs the specifics; orchestrator does not pre-design)

Bet B retention has CLEAR CEILING around 91-92% with the known mechanism families. Four converging-PARTIAL probes:

- v184 **MoE M-dependent** (cross-talk reduction at large M) -- 3/8 cells clear ratio 1.3 threshold
- v185 **per-task substrate** (structural separation by task) -- retention_A=0.821 (+9pp above ~73% baseline)
- v186 **replay-only-axis** (rehearsal during sequential training) -- plateau=0.846 (~85% ceiling regardless of replay fraction)
- v187 **compound (per-task + replay)** -- retention_A=0.915 (mild sub-additive stacking; +18.5pp above baseline; 3.5pp short of HARD-PASS 0.95)
- v188 **compound + longer Phase-A consolidation** -- retention_A=0.917 (+0.2pp; inside seed-variance noise floor; ceiling CONFIRMED INTRINSIC)

Per user pre-cycle framing: "this is a structural-axis question; need fundamentally different approach to clear 95%."

**The Research question (Research designs):** Given four mechanisms (structural separation via MoE; structural separation via per-task substrate; replay/rehearsal; extended consolidation) each delivering partial benefit but the compound ceilings at 91-92%, what is the FIFTH mechanism candidate from a **fundamentally DIFFERENT framework** that could clear HARD-PASS 0.95?

Per [[feedback-no-experiment-design-in-prompts]] + the dispatch-prompt style rule in `notes/orchestrator_post_compaction_brief.md` Section 2: Research designs the question, the search axes, the candidate ranking, the P-distribution, the falsifiers, the multi-probe criteria, the field selection. Orchestrator does NOT pre-design.

## Pointers to live context (Research integrates these)

- **Substrate identity**: Hebbian-only, no autograd (CLAUDE.md convention). Wave 4.5 gradient-W candidate at v1 conflicts with substrate identity and is off-limits for Bet B rehab.
- **EWC-null closure narrative (v172+)**: parameter-importance axis dead (substrate W is maximally distributed; Fisher matrix approximately uniform; zero traction for EWC / MAS / SI / Path Integral by construction). The fifth-mechanism candidate must NOT be a variant of parameter-importance regularization.
- **Already-tested mechanism families to AVOID re-proposing** (per [[feedback-rehabilitation-after-rejection]] and v184-v188 sequence):
  - Structural separation by gating (MoE-style) -- v184 partial
  - Structural separation by task (per-task substrate W matrices) -- v185 partial
  - Rehearsal / replay -- v186 bounded
  - Extended consolidation time (longer Phase A) -- v188 essentially nothing
  - Compound stacking of two of the above -- v187 sub-additive bounded
- **Likely-relevant adjacency fields per `research_meta_map_and_adjacencies_*.md`** (Research advisor will compute its own ranking via `tools/orchestrator/research_field_advisor.py`):
  - **Sleep-style memory consolidation** with NREM-REM-like phase structure (distinct from cross-task replay; Tier-2 partially-explored)
  - **Eligibility traces** (Sutton-Barto; substrate-novel application; not on current rehab list)
  - **Hebbian-with-decay schedules** (decay timescale as a free parameter; substrate-native)
  - **Sparse / low-rank constraint on W during sequential training** (limits cross-talk by capacity bound rather than gating)
  - **Predictive-coding / energy-based consolidation** (Friston / Hinton; conceptually orthogonal to all four tested families)
  - **Online consolidation via mean-field / variational** (does not require explicit replay buffer; substrate-novel possible)
  - **Neuromodulator-inspired learning-rate scheduling** (per user's neuromodulator framing; brain-inspired durable per `feedback_brain_inspired.md`)
  - **Materials-physics analogs** (spin-glass relaxation, Kovacs effect, aging-rejuvenation -- already partially probed but the rejuvenation-after-consolidation axis may be substrate-novel)
- **Per [[feedback-periodic-scope-expansion]]**: ~once per 24-48h dispatch a Research drill on a framework very different from current AI-memory framing. Semiconductor physics was fruitful; cross-application probes are encouraged. Research may consider this drill as the periodic scope-expansion vehicle.
- **Per [[feedback-lit-scan-calibration-penalty]]**: substrate is in uncharted regime (no published direct precedent for 91-92% ceiling phenomenon at FHRR/HRR class with Hebbian-only). Research should deflate agent P estimates by 0.15-0.25 and cap novel-synthesis P at 0.50. Include explicit hard-fail thresholds in falsifiable predictions.

## Contract (Research delivers)

Per [[feedback-2x-means-depth]]: this is a NEW research question (level-1 first-attempt) NOT a 2x verification drill on existing findings.

Deliverable shape:
- 5-10 candidate FIFTH-MECHANISM proposals ranked by P(would clear HARD-PASS 0.95 on Bet B retention) AFTER calibration penalty.
- Each candidate carries:
  - Framework provenance (which field / paper / theoretical tradition)
  - Substrate-fit reasoning (why it does NOT conflict with Hebbian-only convention)
  - DIFFERENTIATION from the four already-tested mechanism families
  - Multi-probe criteria (HARD-PASS / HARD-FAIL / MIDDLE band) per [[feedback-no-smoke]]
  - Smoke-test design pointer (script base, parameter envelope)
  - Calibration-penalty-adjusted P estimate
- Top-2 candidates flagged for next exp_dev cycle.
- Periodic scope-expansion candidate (if Research treats this as the 24-48h scope-expansion vehicle) flagged.
- File at: `notes/research_betB_fifth_mechanism_<date>.md` (Research picks filename per `notes/active_protocols.md` PROT-001 stub conventions).

Per [[feedback-query-privacy-decomposition]]: searches use generic math/theory terms NOT substrate-specific framings; configs/numbers/mechanism-names stay off public platforms.

Per [[feedback-subagent-model-optimization]]: lit-scan / WebSearch sub-agents default Sonnet; Research synthesis can use Opus where reasoning depth is load-bearing.

Per [[feedback-no-papers-product-only]]: framing is substrate-product, NOT publication-grade.

## Autonomy declaration

Research decides:
- The exact ranking heuristic (advisor-output + Research judgment)
- The lit-scan agent dispatches (count, queries, models)
- The P-distribution per candidate
- The smoke-test design pointers per candidate (or "needs exp_dev follow-up scoping pass")
- Whether to treat this as the 24-48h periodic scope-expansion vehicle
- Filename for the delivery note

Orchestrator does NOT pre-design any of the above.

## Why this is high-leverage

- v188 is the FIRST direct saturation evidence on the Bet B retention rehab sequence. Without a fifth-mechanism candidate from a different framework, the Bet B retention 🟡 PARTIAL row stays at 91-92% in perpetuity (or the substrate-product spec accepts the ceiling).
- A high-P fifth-mechanism candidate is the highest-portfolio-impact research deliverable possible this week (a successful candidate would flip a 🟡 PARTIAL to ✅ in the Tier-1 capability set).
- If Research returns NO high-P candidates (all <0.30 after calibration penalty), that's also high-information -- it locks in the v188-NEW scope-rescoping option as the live product-spec path.

## PROT discipline

- Per [[feedback-no-experiment-design-in-prompts]]: orchestrator specifies WHAT (the question) + WHY (live context pointers) + CONTRACT (deliverable shape) + AUTONOMY DECLARATION (what Research decides). NO experimental design parameters in this note.
- Per [[feedback-structural-agent-usage-mandate]]: this filing routes to Research's next cycle.
- Per [[feedback-for-you-tab-primary-channel]]: Research's delivery MUST include a status_log entry with plain_language + importance.
- Per [[feedback-rehabilitation-after-rejection]]: this IS the rehab discipline for the Bet B retention ceiling -- four mechanisms partial, fifth-mechanism candidate from different framework is the live path.
