# PROPOSED hdlab / board LANDING (Q111 — strategy applies + witnesses; solver never writes hdlab)

Turnkey diff for `rebuild_the_comprehension_board_on_a_modern_corpus_retire_the_19c_litbank_eval`. The **reader
is unchanged** — this is primarily an INSTRUMENT change (retire the 19c aggregate) plus ONE register-safe
guardrail on the landed agent assigner. Reverify each step with `verification/test_modern_board.py` (8/8) + the
named per-step witness. NO external LLM (inference OR gold).

## 0. Make the 19c-FREE MODERN board the reported comprehension board (the core deliverable)
The board (`experiments/exp_situation_model_qa_v1.run` + `tools/baseline_board`) reports a LitBank aggregate +
LitBank coref/events/temporal/causal. Land the modern board so the HEADLINE aggregate is 19c-FREE:
- Add the modern per_dimension arms to the board assembly (or point `run()` at `experiments/
  exp_situation_model_qa_modern_v1.run`): coref (GUM, `exp_board_coref_gum_v1.board_coref_modern_dimension`),
  salience (GUM), common-noun (GUM), who-did-what AGENT (UD-EWT, `exp_board_agent_slot_ud_v1.board_agent_
  dimension`), patient/state/wic (already-modern arms, folded).
- Emit the **19c-free aggregate** (item-weighted over modern dims; NO LitBank dim). DEMOTE the LitBank aggregate
  + per-dim numbers to an `informational_19c_crossref` block (kept, not reported as the headline).
- Keep temporal/causal/goal/affect as **NAMED GAPS** in the board output (not fabricated, not 19c) until their
  modern golds are filed (step 3).
WITNESS: `verification/test_modern_board.py` W1 (19c-free guarantee: no dim's gold is LitBank; gaps named) +
W2/W5/W6 (coref/patient/state CI-sep on modern). This is the bar's PASS.

## 1. Register-safe AGENT guardrail — `hybrid_agent_pick` on `hdlab/graded_role_assigner.py`
The landed CM agent (`agent_competition_pick`, ALWAYS-compete over the tracked set) is REGISTER-TUNED to 19c and
UNDER-performs a positional floor on modern canonical prose (UD-EWT full_cm 0.758 vs positional 0.855; GUM
cm_tracked 0.634 vs positional 0.829; the tracked-set decouple REVERSES sign on modern). Add the AGENT
counterpart to the proven `hybrid_role_patient` (reference impl `experiments/exp_board_agent_slot_ud_v1.
hybrid_agent_pick`): keep the word-order default BYTE-IDENTICAL on canonical clauses, invoke the competition ONLY
on a MARKED override cue — PASSIVE (voice), a PP-GOVERNED positional pick (core_arg), or a NON-NOMINATIVE pronoun
(case). Gate behind a flag (e.g. `agent_hybrid=True`); it recovers 0.758→0.832 on modern and preserves the
passive win, and is byte-identical to the pure positional default on canonical clauses.
WITNESS: `test_modern_board.py` W3 (twin loses; full_cm located below floor) + a no-regress check that the 19c
board AGENT arm (`test_cmrole_agent_landing_organ.py`) is unchanged with the flag OFF.
CAVEAT: even the hybrid sits just under the near-ceiling positional floor on modern sentence-level gold — so on
modern canonical prose the guardrail's job is NO-REGRESS to position (not a lift). Land it as the register-safe
default; do NOT expect a modern lift on canonical text.

## 2. Register-adaptive cue validities (FILED, not landed — do NOT hand-tune)
The Competition Model predicts cue validities are register-specific; the modern re-sweep is the mechanism
(word-order-dominant; DROP the tracked-set restriction on expository prose — it reverses sign). A dev-tuned modern
weight set (`order_up`) still does NOT beat the positional floor (0.780 < 0.857), so there is nothing to adopt
today. File as a follow-on: a register-detector that selects the cue-validity profile (narrative vs expository) —
NOT a hand-tuned modern weight vector.

## 3. File the four NAMED GAPS as follow-on problems
- **A non-canonical modern who-did-what gold** (passives / fronting / embedded clauses) — FIRST; it is what makes
  the agent dimension DISCRIMINATING on modern register (canonical UD-EWT/GUM cannot separate a brain-foundational
  assigner from position).
- **Independent modern temporal-order gold** (TimeBank/TDDiscourse) and **non-circular modern causal gold**
  (BECauSE) — retire the tense-shared / connective-reducible 19c arms.
- **Modern intentionality (goal) + emotion (affect) golds** — retire the last two 19c board arms.

## Cross-consumer note (already actionable)
The brain-foundational (gold) grammatical role assigner lifts the coref **entity-KB hard-link +0.084 CI-sep** on
GUM (this solve) — corroborating the sibling's −0.084 positional cost. When the CM role assigner is live for
who-did-what, route its roles into the coref entity-KB hard-link too (the same upstream, two consumers).

## DO NOT LAND / DO NOT QUOTE
- Do NOT adopt the tracked-set decouple on modern text (it HURTS: cm_dense 0.719 > cm_tracked 0.634).
- Do NOT adopt a dev-tuned modern weight vector as if it beats position (it does not, 0.780 < 0.857).
- Do NOT quote the 19c AGENT 0.69 as a modern result — it is register-specific (the whole point).
- Do NOT put any LitBank-scored dimension in the modern aggregate; do NOT fabricate a modern gold for a NAMED GAP.
- Do NOT treat the item-weighted 19c-free aggregate as a load-bearing single number (it crosses populations) —
  the per_dimension rows are load-bearing.

## AUDIT UPDATE (fold into notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b)
The comprehension board is now available 19c-FREE (GUM + UD-EWT + WiC); coref +0.106 / state CI-sep on modern.
NEW MEASURED DEVIATION: the who-did-what AGENT Competition-Model win (0.041→0.69) is REGISTER-SPECIFIC — on modern
gold the positional floor is near-ceiling (0.83–0.86) and the narrative-tuned CM does not beat it (the tracked-set
decouple reverses sign; a re-sweep does not rescue). Fidelity intact (twin loses; passive win survives;
cross-consumer coref lift +0.084 CI-sep). temporal/causal/goal/affect are NAMED GAPS pending modern golds.
