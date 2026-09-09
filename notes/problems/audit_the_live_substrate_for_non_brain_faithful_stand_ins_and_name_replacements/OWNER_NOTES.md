---
owner_verdict: DONE
---

SOLVER SUBMISSION — audit_the_live_substrate_for_non_brain_faithful_stand_ins_and_name_replacements

STATUS: SOLVED. A prioritized CATALOG of the live reader's non-brain-foundational stand-ins + a powered,
fully-drilled localization of the one deep fix + the pri-1 interface specified per consumer. Glass-box, NO LLM,
NO hdlab/ writes (Q111 — a map + proposed fixes; strategy lands). Reverify: verification/test_audit_live_standins.py
(30/30, pure-disk witness); ledger-clean.

DELIVERABLES (all in the problem folder): CATALOG.md (the catalog), PARSER_SIGNAL_TRACE.md (per-signal accuracy +
per-consumer binding constraint + generalization), PRI1_INTEGRATION_MAP.md (how pri-1 feeds every consumer that
needs it), SOLVED.md, verification/test_audit_live_standins.py + 3 drill cells.

THE CATALOG. 8 LIVE non-brain-foundational stand-ins (5 disk-verified fields each) + 3 located-negatives/corrections,
top-K ranked, denominator = every organ situation_reader.read() consumes (reconciled against the __init__ flag
defaults, not the stale comments). #1 by blast = the GOLD-COREF-INHERITANCE LEAK (_apply_commonnoun_gate reads the
gold cluster column at inference, situation_reader.py:3844/3854/3861 — masks experiencer 0.15→0.80; = pri-6). Then
the arc-eager surface-feature scorer (C3), the string-identity common-noun binder that trails the naive floor (C2),
the experiments/-at-inference self-containment debt (C4), a fitted-logistic pure-defer (C5), a cert-fit governor
perceptron (C6, decision-dead), and two live in the grounding subsystem not this reader (C7/C8).

DISK OUTRANKED THE BRIEF (re-verified every claim; several already fixed): spaCy fully purged from hdlab; the
test-fitted force-verb list retired; state/location hand-lists → WordNet; cleanup_family/hd_fact_store are DORMANT
wrt this reader (live only in the grounding pipeline); "coref name-Jaccard" misattributed to a dormant module;
scene_segment's fixed window is dead code. AT FINALIZATION: strategy CONT-29 began landing what I catalogued — C4
partially remediated (reader's direct experiments imports promoted; residual = context_grounded_valence +
temporal_reasoner, verified first-hand), C1 de-leak step 1 landed, pri-1 integrated.

THE PARSER DEEP-DIVE (owner-directed, beyond the catalog bar). Traced every signal the parser passes downstream +
its measured accuracy (the ladder: POS 0.944 → heads 0.76-0.84 → LAS 0.72 → passive/oblique roles collapse to
0.06-0.40) and each consumer's binding constraint. Then drilled the OOD-reliability wall with 3 powered experiments:
(1) EVERY frozen-parser confidence signal collapses to ~chance out-of-register (marginal 0.548, entropy 0.536,
arc-eager conf 0.4995 on QA-SRL n=8173); (2) the dormant unfrozen learner alone can't rescue it (POS-only, adaptation
anti-load-bearing OOD); (3) the FULL brain-foundational in-sentence fix — never-frozen online learning + lexical-grounded
codes + global-coherence settle — MATCHES but cannot EXCEED the frozen marginal (composite 0.538 < 0.548), each layer
working directionally so the mechanism is real. AIRTIGHT LOCATED NEGATIVE: in-sentence signal is exhausted; the one
register-robust signal the reader lacks is a CONTENT-DERIVED top-down expectation = pri-1.

PRI-1 INTERFACE (PRI1_INTEGRATION_MAP.md). pri-1 is the SOURCE of that expectation; it emits E1 next-event/participant,
E2 result-state, E3 goal-state, E4 cause, and each consumer reads its projection as the top-down term (attachment-bound:
who-did-what/spatial-attach/goal-purpose/polarity; detection/coverage-bound: spatial-coverage/temporal/causal/copular/
world-state; discourse-adjacent: coref prior/bridging). Honest exclusions: filler-gap + the common-noun type comparator
are NOT fed by pri-1. Ordering: de-leak (pri-6) + wire meaning channel → pri-1 → C3 parser cluster first → descend.

KEY REALIZATIONS: (a) re-verifying every defect against current bytes before cataloguing turned a stale brief into an
accurate one (3 items were already fixed); (b) "LIVE" has three failure modes (live-defective / live-but-inert /
dormant-wrt-this-reader) and conflating them mis-ranks the work; (c) the parser fix is NOT a better bottom-up scorer or
a cleverer confidence readout — I built and powered-tested every in-sentence lever and they're exhausted; the fix is the
world-model (pri-1); (d) the do-not-over-fire discipline kept ~7 knowledge-supply lexicons off the defect list.

QUESTIONS: none blocking. NEXT: land the C3 local moves + C4 residual promotion now; the spine is pri-1 with the
interface pre-specified; a second breadth pass over the grounding-acquisition pipeline (C7/C8) is a new follow-on.

PLAIN ENGLISH: I made one ranked list of every place the reader takes a convenient shortcut instead of working like a
brain, checked each against the live code (several were already fixed), and found the worst is that it peeks at the
answer key when grouping mentions of a person. Then, on your steer, I went deep on the parser: I traced exactly what it
hands downstream and how accurate each piece is, and I built the real brain-style fix — a parser that keeps learning,
sees word meanings, and settles on a coherent reading. Tested hard, every piece helped a little but none beat the
current parser on unfamiliar text. That proves the fix isn't a parser tweak — it's tracking the story across sentences
(the priority-1 "imagine forward" rebuild), and I wrote down exactly how that plugs into the parser and every other part
that needs it.
