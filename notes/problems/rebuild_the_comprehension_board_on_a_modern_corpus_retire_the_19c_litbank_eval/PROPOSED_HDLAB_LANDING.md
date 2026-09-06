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

## 1. Register-safe AGENT guardrail — `hybrid_agent_pick` on `hdlab/graded_role_assigner.py` (MEASURED no-regress + non-canonical lift)
The landed CM agent (`agent_competition_pick`, ALWAYS-compete over the tracked set) is REGISTER-TUNED to 19c and
UNDER-performs a positional floor on modern canonical prose (UD-EWT full_cm 0.758 vs positional 0.855; GUM
cm_tracked 0.634 vs positional 0.829; the tracked-set decouple REVERSES sign on modern). Add the AGENT
counterpart to the proven `hybrid_role_patient` (reference impl `experiments/exp_board_agent_noncanonical_v1.
_hybrid_idx`): keep the word-order default on canonical clauses, invoke the competition ONLY on a MARKED override
cue — PASSIVE **with an explicit by-phrase** (voice), a PP-GOVERNED positional pick (core_arg), or a
NON-NOMINATIVE pronoun (case). Gate behind a flag (e.g. `agent_hybrid=True`).
MEASURED (UD-EWT train+test, n=13441): full modern set **hybrid_byfix 0.853 ~= positional 0.8525 (+0.0005,
no-regress)**; canonical 0.8855 ~= 0.8903; NON-CANONICAL slice **0.393 vs 0.316 (+0.077 CI-sep)**, twin loses.
The by-phrase gate on the passive override is what closes the canonical no-regress gap (agentless passives have
no agent to flip to). WITNESS: `test_modern_board.py` W3/W9 + a no-regress check that the 19c board AGENT arm
(`test_cmrole_agent_landing_organ.py`) is unchanged with the flag OFF.

## 1b. byagent-cue COVERAGE FIX on `hdlab/graded_role_assigner.py::agent_supports` (MEASURED +0.214 CI-sep on passives)
The landed byagent cue is `by = 1.0 if prevtok == "by"` — it fires ONLY when 'by' is IMMEDIATELY before the
candidate, so it MISSES multi-word by-phrases ('by US **troops**' -> agent head 'troops', prev token 'US'). 'by'
governs the whole by-PP; the agent is its HEAD, which may be separated by compound/DET/ADJ modifiers. FIX: scan
left over NP-internal modifiers to find 'by' (mirror `_agent_pp_governed`'s scan; reference impl
`experiments/exp_board_agent_noncanonical_v1._byagent_fixed`). A coverage fix to the SAME voice cue, NOT a new
cue. MEASURED (passive slice, n=182): landed cm 0.308 -> **cm_byfix 0.522 (+0.214 CI[+0.138,+0.293])**; vs raw
positional 0.028 that is +0.49. Brain-foundational, net-positive, isolated to passives (byte-identical on
actives) -> land it. WITNESS: `test_modern_board.py` W10.
FOLLOW-ON (precision): the `_agent_pp_governed` detector OVER-fires (flags some real subjects), so the
pp-suspect-active slice is a wash — a precision fix to the PP-government scan is a small named follow-on.

## 1c. DECORRELATED CONSTRUCTION cues on the AGENT hybrid (MEASURED +0.018 full-set CI-sep, brain-foundational)
The mechanism drill proved the agent competition is preverbal-DOMINATED (P(cm==floor)=0.84 on canonical), so it
cannot recover position's failures except via a cue DECORRELATED from position; construction-specific rules
(Goldberg 1995) are that class. Add two overrides to the hybrid (reference impl
`experiments/exp_board_agent_construction_v1.hybrid_construction_pick`), tried before the word-order default:
- **EXISTENTIAL** (`_existential_subject`): expletive 'there' pre-verbally -> notional subject = first
  post-copular NOUN/PROPN, NOT 'there'. **0.186→0.6535 (+0.467 CI[+0.392,+0.546])**.
- **NP-COORDINATION** (`_first_conjunct_subject`, GUARDED): 'NP1 and NP2 V' -> subject head = first conjunct NP1.
  Guards (learned from the wall drill, REQUIRED): the coordinator immediately joins the two NPs; NO ', and'
  (clause/list); NP1 not PP-governed. **0.307→0.5817 (+0.275 CI[+0.130,+0.416])**.

MEASURED together (UD-EWT train+test): FULL who-did-what AGENT set **0.855→0.873 (+0.018 CI[+0.015,+0.021])** —
the first clear full-set margin over position — with EXACT zero canonical regress and the twin losing. Land both
with the hybrid (§1). WITNESS: `test_modern_board.py` W12. DO NOT land a cleft override (verified NOT an
agent-dimension opportunity — the nsubj is the relativizer). More constructions (tough-movement) = a filed
follow-on with diminishing per-construction value.

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
