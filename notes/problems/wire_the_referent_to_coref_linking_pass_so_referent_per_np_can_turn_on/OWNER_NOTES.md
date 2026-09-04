---
owner_verdict: DONE
---

SUBMISSION — wire_the_referent_to_coref_linking_pass_so_referent_per_np_can_turn_on
STATUS: SOLVED (WIP until owner_verdict: DONE). Glass-box, NO LLM at inference. NO hdlab written
(Q111; proposed diff in SOLVED.md §7). Witnessed 7/7 scaffold-free; ledger clean.
REVERIFY: .venv/Scripts/python.exe verification/test_referent_coref_linking_organ.py   # 7/7 from source

WHAT IT DOES. The referent-per-NP mention source (+0.336 who-did-what) could not turn on because
turning it on collapsed pronoun coref (coref_acc 0.469 -> 0.102): every non-coref NP head became a
fresh singleton, flooding the anaphora pool with feature-blank, inanimate, one-off referents.

THE FIX = DECOUPLE THE TWO CANDIDATE SOURCES. Role-binding (who-did-what) and pronoun anaphora draw
on the referent set through DIFFERENT brain cue-filters (thematic role vs animacy/Centering-gated
retrieval — Lewis-Vasishth, Grosz-Joshi-Weinstein). So referent_per_np should swap ONLY the
who-did-what role-candidate source; pronoun anaphora keeps reading the tracked discourse-entity
(coref-column) source. -> coref byte-identical to baseline (no regression), who-did-what keeps +0.336
-> referent_per_np turns default-ON.

BRIEF MECHANISM REFUTED (disk > brief). The brief's "merge the referent-per-NP referents INTO the
coref pool so the antecedent is always a candidate" REGRESSES coref -0.106 CI-sep: the antecedent was
already coref-covered, so the extra referents are pure distractors.

RESULT (100 docs, held-out; pooled he/she coref_acc). regression reproduced OFF 0.469 -> ON 0.102
(-0.386 CI-sep). Expand-pool LINKER -0.106 CI[-0.169,-0.042] (refuted). DECOUPLE recovers +0.298
CI-sep over the regression, no CI-sep regression vs baseline. Info-free shuffled-link twin LOSES
(-0.151 CI-sep). who-did-what +0.336 inherited byte-identical (W7). BONUS (flagged): unifying the
resolution overlay by the discourse entity lifts coref +0.043-0.054 CI-sep ABOVE baseline.

FILES. experiments/exp_referent_coref_linking_v1.py (reference impl), _diagnosis_v1.py,
verification/test_referent_coref_linking_organ.py (7/7). NO hdlab written.

FRONTIER FLAGGED (SOLVED.md §9) — step-5 person-selection, exploratory, on top of owner-DONE
kehler_rohde. Built + measured the full brain-faithful chain (all glass-box, NO training): a
learned structural combiner (0.490->0.558 held-out), a role-typed FHRR person-file binder over the
reader's OWN extracted facts, and a research-verified brain-foundational Competition-Model upstream
role assigner (fixes inanimate-agent 0.333->0.081). KEY FINDING: the binder's trust in its facts
climbs MONOTONICALLY as each component becomes brain-foundational (bound-weight -0.048 -> +0.101 ->
+0.220), validating "every component must be brain-foundational" — but the chain still doesn't
CI-separate, localizing the LAST non-faithful link to exactly ONE component: the world-knowledge
COHERENCE / next-mention prior (Kehler-Rohde P(referent|coherence)). THREE open challenges flagged
as CRACKABLE (not walls), each with a pinned glass-box first step; the last one's path is
implicit-causality + selectional-preference norms (static cues, NO learned model).
