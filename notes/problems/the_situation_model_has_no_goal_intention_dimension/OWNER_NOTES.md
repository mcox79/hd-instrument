---
owner_verdict: DONE
---

SOLVED — the_situation_model_has_no_goal_intention_dimension (opus 4.8 solver)

Write-up: notes/problems/the_situation_model_has_no_goal_intention_dimension/
  {SOLVED.md, OWNER_NOTES.md, research_goal_intention_brain_mechanism_2026-09-04.md,
   research_infinitive_attachment_brain_mechanism_2026-09-04.md}
Reverify (re-runs NO landed cell): .venv/Scripts/python.exe verification/test_goal_register.py   # 11/11

WHAT: the missing 5th Zwaan-Radvansky dimension (INTENTIONALITY) — a glass-box per-agent GOAL REGISTER over
the reader's OWN extraction (frontend POS + coref; NO spaCy at inference, NO LLM). Answers "what is X trying
to do", "why did X act" (goal-why), "did X achieve it" (status), off the accumulated model.

RESULT (100 LitBank docs, CI-separated, info-free twin LOSING, floor recomputed per population):
- WANT "what is X trying to do", reliable explicit slice (desire/intend/try + in-order-to, n=234):
  model 0.607 vs most-recent-action floor 0.137 (CI-sep) AND vs shuffled-agent twin 0.017 (CI-sep); twin
  null p95 0.0165. Explicit-slice extraction precision 0.857 = the spaCy oracle (AT the competent-reader
  ceiling; oracle is reference-only, never on the inference path).
- WHY goal-why (n=1372): goal register 0.980 vs the PHYSICAL-CAUSE dimension 0.041 (CI-sep) — and the
  CONVERSE (n=461 because/so questions): causal dim 0.86 vs goal register 0.01. Goal-why and physical-cause
  are DISJOINT, complementary dimensions (Malle reason-vs-cause).
- Binds the RIGHT agent: positive control 816 vs 3. STATUS field (Lutz-Radvansky) authored 1.0 vs 0.33.
  REINSTATEMENT (Suh-Trabasso) authored 1.0 vs a status-blind recency floor 0.0.

UPSTREAM brain-foundational component (built + research-verified, not cited-after): a lexicalist verb
SUBCATEGORIZATION-FRAME filter (P(complement) from UD-EWT gold — a static offline foundation asset, not the
test set) + extraposition detection + a passive-agent guard (PRO -> matrix AGENT). PINNED (MacDonald/
Seidenberg constraint-based lexicalist parsing; filtering = the faithful mechanism for the clear case). It
DECISIVELY fixes the target cases ("to meet a Megalosaurus"/"began to rain" dropped, "went to buy" kept),
removes ~120 over-fires, and lifts WANT-explicit 0.531 -> 0.607. ZERO REGRESSION proven: the frame gates
ONLY the bare branch, so the explicit consumer is BYTE-IDENTICAL off vs on (0.6068==0.6068, n=234; witness
W10); WHY/status/reinstatement/other reader dimensions unchanged.

LOCATED NEGATIVE (the brief's sanctioned full pass, named + numbered): (a) bare-purpose adjuncts are
ATTACHMENT-parse-gated (precision 0.34 vs oracle; residual = causatives/perception-ECM/complex-sentence
attachment) — needs a register-native parser (the modern arc parser is 19c-negative); (b) unstated/abductive
Tier-2 goals ("why this over that") need the world-knowledge/meaning channel. This is the explicit-vs-
inferred split the brief predicted.

BRAIN-FOUNDATIONAL AUDIT (SOLVED.md §9): every mechanism step PINNED or OUR-INVENTION-swept; the only
in-mechanism average is lexical subcat frequency (what the brain stores); NO FHRR/consolidation-style
averaging (the register SELECTS). Bootstrap means are measurement hygiene.

files: experiments/{goal_register.py, verb_subcat_frames.py, exp_goal_register_qa_v1.py} +
verification/test_goal_register.py (11/11) + data/verb_subcat_frames_v1/verb_subcat_frames_ud_ewt.json +
data/exp_goal_register_qa_v1/metrics.json. NO hdlab written (Q111). Ledger malformed/incomplete: 0.

AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT.md §2b): add the GOAL/INTENTION dimension — distinct dmPFC
mentalizing computation (desire FOLDED in), DISJOINT from physical causation (Malle), status field +
reinstatement PINNED; the reader now has all five Zwaan-Radvansky dimensions.

DO / NEXT (strategy, only after owner_verdict: DONE): land the default-off track_goals wire + the `goal`
board arm + promote the upstream subcat-frame asset (SOLVED.md §5). Filed further-growth levers, ranked:
register-native (19c) dependency parser (bare-purpose attachment) > meaning channel (Tier-2 abductive) >
goal->subgoal hierarchy graph.
