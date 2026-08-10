# Design: DECISIVE INFERENCE TEST on ProPara -- ARM 1 (oracle structure, isolate the thesis on real prose)

Director design note (2026-08-10, full-auto). Both threads resolved -> this is the payoff: the decisive glass-box comprehension test on real prose. SHAPE + pointers; exp_dev designs params + handles impl.

## Why (both fronts green)
- BENCHMARK (measured, trap-check 16bdfe77f): ProPara chosen -- REAL elicited prose, PASSES content-ceiling (no-memory BoW macro-F1 ~0.24 on the cross-step-dependent/participant-UNMENTIONED subset ~= majority 0.21) + composition-necessity (bag-of-states caps low), NO endpoint shortcut. TRIP rejected (BoW 70%, MCScript-trap). CLUTRR = synthetic secondary diagnostic (k>=4 only; keep for extraction-vs-composition separation).
- EXTRACTION (measured, gate v2 3f23f2fb2): fastcoref runs (system python, no new venv) + extraction MATERIALLY propagates (rule->neural coref lifted organ 0.684->0.807, parity 46%->73%). Extraction viable; gap localized.
- FIT: ProPara = track each participant's STATE (exists / location / created / moved / destroyed) across process steps = EXACTLY hdlab/situation_model_accumulate (entity-state tracking across events) + the Stage-2A retrieve-validate-advance loop (propagate + validate state across steps). The HARD subset (participant UNMENTIONED at the queried step -> must INFER by cross-step propagation) is where BoW collapses and our situation-model tracking should win.

## THE DECISIVE TEST (ARM 1 = ORACLE structure)
Given ProPara's GOLD structure (events + per-step participant states), does our REASONING correctly infer the cross-step / participant-UNMENTIONED states, BEATING the trap baselines, WITH scramble collapse, under the OFFICIAL metric? YES -> the glass-box inference thesis HOLDS on real prose (remaining work = extraction, ARM 2). NO -> the inference approach is the ceiling even given perfect structure -> reconsider the thesis. This isolates INFERENCE from EXTRACTION (the confound that plagued every prior arc).

## MANDATORY precondition (trap-check flagged it)
Use the OFFICIAL ProPara eval (Cat-1/Cat-2/Cat-3 leaderboard metric) OR rigorously justify a proxy + show it tracks the official metric. Reproduce the trap baselines (majority, BoW, bag-of-states, single-step-no-memory) UNDER the official metric. NO claim is legitimate on a self-defined proxy (the same harness-calibration the MCScript2.0 note required).

## Reasoning (brain-faithful; reuse owned organs, do NOT rebuild)
- hdlab/situation_model_accumulate.py (REAL+WIRED) -- AccumulateRegister tracks entity/role/event; ADAPT to carry participant STATE (existence/location/CREATE/MOVE/DESTROY) across steps = the situation model (DMN/AG + WM state maintenance). Flag any state-typing extension needed.
- Stage-2A retrieve-validate-advance loop (experiments/exp_focus_pullin_causal_stage2a_multihop_loop_v1.py, REAL, HARD_PASS 5/5) -- PROPAGATE state changes across steps + VALIDATE persistence/consistency (created-and-not-destroyed => still exists; moved => new location). The unmentioned-state answer = propagation + validation.
- CRUTCH (CSKG) = SECONDARY, measured-marginal ONLY: CSKG is social-commonsense, WEAK on ProPara's SCIENTIFIC-process domain (confirmed in the WIQA arc). Include as an optional arm + measure its marginal impact; do NOT depend on it. The core reasoning here is STRUCTURAL state-propagation, not world-knowledge -- which is a CLEANER test of the loop's core competency.

## Arms + controls
- REASONING arm: situation_model_accumulate + retrieve-validate-advance loop over gold structure.
- Baselines (reuse the trap-check harness/numbers): majority, BoW, BAG-OF-STATES (has states, no cross-step composition), SINGLE-STEP (no memory).
- SCRAMBLE control (load-bearing): shuffle step order -> the reasoning arm MUST collapse toward the no-memory baseline (state-propagation depends on order; if scramble does not collapse, the "win" is not temporal composition -- the exact control that exposed prior false positives).
- FOCUS METRIC: the cross-step-dependent / participant-UNMENTIONED subset (Cat-3-like) where composition is necessary; also report full-set no-regression.
- optional: +crutch arm (marginal-impact measurement).

## HARD-PASS
Reasoning arm beats ALL baselines by a real margin on the cross-step subset UNDER THE OFFICIAL METRIC, scramble COLLAPSES it, no-regression on the full set. A scramble-clean win here = the FIRST genuine glass-box comprehension win on real prose of the entire program.

## Then (staged, after ARM 1 lands)
- ARM 2 = EXTRACTED structure (spaCy/SRL events + fastcoref entities + state-change extraction) -> same reasoning -> measure the extraction COST (arm2 vs arm1 gap). This is where the coref-quality lever (LingMess/mention-alignment) gets pulled IF needed.
- Then crutch-that-fades native-ization of the extraction competency.

## Guardrails
Branch dataprep/mcguffey-graded-corpus. ProPara already pulled (data/benchmark_trap_check + tools/benchmark_trap_check/propara_trap_check.py). OFFICIAL metric mandatory. self-test PASS -> smoke (can-fail, real baseline, difficulty on, one variable) -> multi-seed FULL. Resumable. Targeted commits (git SLOW, never git add -A). VET on disk; scramble is the load-bearing control. This ARM-1 build IS the decisive thesis test -- do it right, not fast.
