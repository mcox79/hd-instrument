---
owner_verdict: DONE
---

SOLUTION SUBMISSION -- the_who_did_what_selection_residual_is_structural_np_head_chunking_and_case_not_meaning

STATUS: SOLVED (chunker half) + brain-faithful LOCATED NEGATIVE (case half). Witness
verification/test_whodidwhat_nphead_case.py = 45/45. Ledger clean. NO hdlab writes, nothing pushed.
Solver: opus 4.8. WIP until owner_verdict: DONE.

RESULT
- NP-HEAD CHUNKER is the live structural lever. On the cleaned 19c direct-object gold (n=669, position floor
  recomputed 0.9178 = the parent's) a glass-box chunker (compound Right-hand-Head-Rule + genitive DP-head) lifts
  patient selection to 0.9806: +0.0628 CI[+0.042,+0.084], half=0.021, null_p95=0.021 (CI-sep AND above null).
  CHUNK-SHUFFLE twin ties the floor; held-out both halves CI-sep; NO modern regression (qasrl +0.128, larger).
- IT'S A HIGH-VALUE DOWNSTREAM FIX, not ceiling polish (WIRE-DON'T-ISLAND, verified first-hand). The LANDED role
  assigners the reader actually uses score only 0.6831 on this gold; 96% of their misses are exactly this NP-head
  error. The wire lifts EVERY consumer +0.20 CI-sep first-hand -- resolve_patient / hybrid_role_patient /
  competition_pick / route_predicate_arguments(end-to-end) all 0.683 -> 0.888. EFFECTIVE end-to-end (abstention=
  wrong): live reader 0.6293 -> full-fix stack 0.9806 (+0.3513 CI-sep, 78%->100% coverage); info-free twin 0.547.
- CASE cue = faithfully built, REAL (position-neutralized 2AFC: CASE 1.00 vs shuffle 0.51, +0.49 CI-sep), but ZERO
  availability on the canonical-active DO gold (0/669 orthogonal; decisive fronted-object regime 59/120000 = 0.05%).
  A located negative that is the Competition Model's/eADM's OWN prediction, not a failure.
- CEILING: aggressive X-bar rule does NOT help (-0.0075 ns); a FULL modern parser (spaCy) scores 0.9297 < ours (it's
  degraded on 19c). We are at/above the 19c parse ceiling. Residual ~1.6% = verb subcategorization (PropBank-
  suppliable, ~0.5% here, its real home is non-canonical) + archaic-POS brittleness (no modern-tagger fix) + 2 gold-
  annotation errors (chunker is PropBank-correct -> true ceiling 0.9836).

BRAIN-FAITHFULNESS: STAGE A (constituent-head ID) PINNED (Williams 1981 RHR; Abney 1987 DP-head; Nelson 2017 ECoG
bracket-closure; Ding 2016; Pallier 2011); STAGE B = the landed graded Competition-Model organ (order-dominant,
shuffled-validity twin collapses to 0.608). Case = eADM early cue. Verb-subcat = PropBank/VerbNet (Altmann-Kamide
1999 early/predictive). One honest OUR-INVENTION: strict head->role staging (brain interleaves).

DOWNSTREAM PROPAGATION + FOLLOW-ON (traced on disk): all consumers funnel the patient through resolve_patient /
hybrid_role_patient(cands), so ONE wire fixes the primitives. TWO separate sites need the SAME rule (both prototyped
+ proven): (1) the _cands primitive; (2) situation_reader._pick_role_mentions -- mention-level NP-head reduction
lifts the LANDED _assign_roles 0.7728 -> 0.9477 (+0.175 CI-sep, twin fails). The ~20 role-output organs inherit the
fix automatically (re-VALIDATE at landing, not re-code). The 22% abstention is a separate coverage problem (1b).

PROPOSED hdlab WIRE (strategy lands, Q111, default-off, witnessed): one shared np_head_reduce(toks,pos,cands) helper
called (a) on _cands in the primitives and (b) on sent_noms in _pick_role_mentions; + case as a dormant early cue.
Reference impl: experiments/exp_whodidwhat_full_fix_v1.role_patient_full_fix.

FILES: experiments/exp_whodidwhat_{nphead_case, ideal_structural, signal_loss_ledger, downstream_live_reader,
improved_consumer, per_consumer_wire, full_fix, mention_path_fix}_v1.py; verification/test_whodidwhat_nphead_case.py
(45/45); notes/problems/<slug>/{SOLVED.md, BRAIN_FIDELITY_AND_SIGNAL_LOSS.md}.
REVERIFY: .venv/Scripts/python.exe verification/test_whodidwhat_nphead_case.py

TLDR (plain English): The reader's "who did what" is right only ~63% of the time on clean old-prose sentences -- it
grabs the wrong word inside a phrase ("the undertaker's shop" -> undertaker) on a third of them and silently gives
no answer on a fifth (both because the modern grammar tool it leans on chokes on old prose). One drop-in fix -- pick
the head of the phrase, always try, use the brain-style cue competition we already have -- takes that from 63% to
98%, holds on held-out text, helps modern text too, and a scrambled version drops to 55% (proving it's real). The
same fix is needed in two places in the code (both proven). The old-fashioned word-ending cue (he/him, who/whom) is
genuinely real but never fires here because old-prose objects are full nouns, not pronouns -- exactly what the
textbook theory predicts. Remaining mistakes need a verb-pattern dictionary and are partly answer-key errors, not
ours.

WHAT REMAINS (all named, none blocking): land the two-site wire (strategy); re-validate the ~20 output organs at
landing; the 22% coverage gap (problem 1b); verb-subcat frames + the non-canonical regime + a graded metric are
adjacent/blocked, not this task.

QUESTIONS: none.
