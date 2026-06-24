# exp_dev hand-off — research: neuroscience methodology applied to substrate-as-LM

**Filed-by:** research (3x drill, neuro discipline lane)
**Date:** 2026-06-23
**Trigger:** `d:/AI/hd-instrument/notes/research_neuroscience_methodology_for_substrate_lm_3x_drill_2026-06-23.md` proposed 5 substrate-discipline atoms; 2 of 5 are zero-compute-cost tool-builds shippable THIS cycle.
**Pause state:** check `data/orchestrator_paused.flag` per standard exp_dev contract.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names anchors and points at the research artifact; exp_dev designs the experiment.

---

## Anchor candidates (rank-ordered)

### Anchor A1 (P0, tier=tool-build, zero compute-cost) — ship this cycle
**Anchor pointer:** `tools/cell_viability_gate.py` (new)
**Substrate-product reading:** pre-flight gate analogous to slice-viability filter; runs as smoke pre-stage; emits `gate_pass.json` BEFORE main arms dispatch
**Tier hint:** tool-build, not chain-grade experiment; ships in <1hr
**Why now:** would have caught rigged-harness (#1), OOM-as-failure (#2), un-amplitude-scaled codebook (#3) — 3 of 10 failure categories this arc
**Gates to implement (per research note L3.2):**
- GATE_1: ARM_UNIGRAM reproduces vocab entropy log2(V)±0.05
- GATE_2: ARM_RANDOM_W produces uniform output distribution
- GATE_3: ARM_BASELINE produces non-degenerate output entropy >50%
- GATE_4: smoke-N reproduces full-N qualitative regime
- GATE_5: per-arm runtime variance < 3x
- GATE_6: per-arm output-magnitude L2 within 2x of baseline
**Lit anchor:** Khoshbouei/Campagnola slice-viability tradition; Allen SDK + SpikeInterface unit quality metrics

### Anchor A3 (P0, tier=tool-build, zero compute-cost) — ship this cycle
**Anchor pointer:** `tools/verdict_writer.py` (new) — structural blinding refactor
**Substrate-product reading:** separates per-arm metrics emission from verdict_msg framing; verdict_writer is structurally blinded to which arm is the "novel" one — applies pre-registered HARD-PASS bands only
**Tier hint:** tool-build + process refactor; ships in <30min
**Why now:** preempts Fix #28 recurrences (4x this session); structural fix not exhortative
**Lit anchor:** Kriegeskorte 2009 double-dipping (42% of fMRI papers); Munafò-Nosek 2017 manifesto blinding recommendation; Botvinik-Nezer 2020 NARPS 70-teams

### Anchor A2 (P1, tier=compose-discrimination protocol, 3x compute) — pilot on next compose-cell
**Anchor pointer:** 6-arm compose-discrimination cell-author contract
**Substrate-product reading:** mandatory for ≥2 mechanism cells: NULL / A-only / B-only / A-then-B / B-then-A / RAND-SEQ arms; interaction term = `metric(A+B) - metric(A) - metric(B) + metric(NULL)`
**Tier hint:** pilot on 1 cell (next n1_v4 or g1_v2 compose-cell), measure if interaction-term changes verdict; if yes, graduate to standard
**Why now:** prevents naive-multiplicative-compose collapse (#4) and baseline-mismatch (#5)
**Lit anchor:** Pawlak-Kerr-Cheong 2010, Brzosko 2017 sequential neuromod dissection; classical 2x2 factorial pharmacology design

### Anchor A4 (P2, tier=spec discipline) — light-touch process change
**Anchor pointer:** cell-author norm-matched baseline contract (header field)
**Substrate-product reading:** comparing 2 arms requires L2/L∞ activation-norm within 2x; document in cell-spec header; reject if exceeded
**Tier hint:** process / lint check
**Lit anchor:** Wessberg-Nicolelis 2000 matched-filter / population vector decoder norm-matching tradition

### Anchor A5 (P2, tier=cert-tier promotion contract) — Skunkworks-routable
**Anchor pointer:** multi-analyst tier-claim contract for cert-grade promotion
**Substrate-product reading:** cert-grade tier requires 2 independent verdict-evaluators (Skunkworks + 2nd fresh-eyes process) to agree; disagreement → MIDDLE_BAND, queue capacity-sweep
**Tier hint:** Skunkworks-process change
**Lit anchor:** Botvinik-Nezer 2020 NARPS 70-teams; Kriegeskorte 2009 double-dipping mitigation via independent analysis

---

## Context pointers (file paths; no inline summaries)

- Research artifact: `d:/AI/hd-instrument/notes/research_neuroscience_methodology_for_substrate_lm_3x_drill_2026-06-23.md`
- Companion drill (in flight, will land separately): `a81a04d803ba9e5c6` (ML/statistical experimental design)
- Substrate-as-LM rigged-harness audit: `MEMORY.md` → `project_substrate_as_LM_test_harness_rigged_2026-06-23_methodology_audit.md`
- Fix #28 recurrence history: `feedback_fix28_verify_per_arm_metrics_not_summary_verdict_text_2026-06-22.md` + `feedback_fix28_violation_count_internalize_harder_2026-06-22.md` + `feedback_fix28_recurring_skunkworks_correct_more_than_director_2026-06-23.md`
- Existing pre-dispatch discipline (A1 fits with): `feedback_fix26_predispatch_verify_the_referent_gate_2026-06-22.md`
- Existing per-arm-metrics discipline (A3 fits with): `feedback_use_peek_arm_metrics_before_framing_2026-06-23.md`
- exp_dev contract: `d:/AI/hd-instrument/tools/orchestrator/agents/exp_dev.md`
- Cheap decisive test pre-registered in research note: pilot A1 + A3 on next 3 cells; if A1 catches >=1 non-viable AND A3 changes Director-vs-Skunkworks agreement rate, graduate both to standard practice + ship A2 as P1.

---

## Contract section

- exp_dev SHALL pick the highest-leverage anchor under its current pause state.
- exp_dev SHALL pre-reg HARD-PASS / HARD-FAIL bands per [[feedback-envelope-fail-bands]] BEFORE shipping.
- exp_dev SHALL smoke-gate per [[feedback-smoke-must-discriminate]] (and per A1, if A1 is shipped first, USE it).
- exp_dev SHALL ship via `bash tools/queue_add.sh` per current queue-routing rules (heavy compute → remote_gpu via hdi_orchestrator per USER 2026-06-22 routing rules).
- exp_dev SHALL post-ship REMOTE VERIFY per [[feedback-verify-the-referent]].
- exp_dev SHALL self-test per [[feedback-formula-selftests]].

## Autonomy declaration

exp_dev decides:
- Which anchor to take first (A1 vs A3 ship-order; both are <1hr tool-builds and could ship in same cycle)
- Cell-author spec details (gates 1-6 implementation specifics; verdict_writer.py interface contract)
- Pilot-cell selection for A2 (which compose-cell to test 6-arm pattern on)
- HARD-PASS / HARD-FAIL bands per envelope-fail-bands discipline
- Smoke gate criteria (recursively: if A1 ships first, A1 IS the smoke gate)

Research deliberately does NOT specify cell-design, queue routing, or pilot-cell choice — those are exp_dev's call per role contract.
