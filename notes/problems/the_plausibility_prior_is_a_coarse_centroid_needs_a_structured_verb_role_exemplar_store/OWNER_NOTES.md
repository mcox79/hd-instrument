---
owner_verdict: DONE
---

NEXT PRIORITY PROBLEM — for a solver session (opus 4.8).

WHAT THIS PROBLEM IS (plain language):
The reader decides who-did-what partly from per-verb knowledge of "what kinds of
things this verb usually acts on" (you READ books, you DRIVE cars). Right now that
knowledge is learned from Simple-English-Wikipedia — the WRONG kind of text for what
we read. We proved, definitively, that this is THE wall: build the exact same
knowledge from text of the SAME KIND as what's being read and who-did-what jumps by
nearly the whole available gap — even with the same imperfect parser, even with no
answer key. So the reader must learn its per-verb / event knowledge from its OWN
reading domain (register-native), not from a generic pile of unrelated text.

WHY THIS ONE: it is the DEFINITIVELY-LOCATED #1 lever for who-did-what, isolated by an
oracle-ladder dissection that ruled out every other candidate WITH NUMBERS — it is NOT
the grounding/feature space (grounded similarity adds +0.20 over memorization), NOT the
mechanism (FHRR role-filler binding is faithful), NOT the combination (a learned
arbitrator ties the better single system), NOT parse cleanliness (a minor +0.036). It
is DOMAIN MATCH of the selectional/event corpus (+0.149, ~80% of the gap). Same root
cause as the 19c register-drift wall: selectional/event knowledge is DOMAIN-RELATIVE.

THE BUILD: a no-gold, REGISTER-NATIVE selectional/event store, built OFFLINE from a
genuinely DISJOINT domain-matched corpus (NOT the test corpus), bound with the
substrate's wired FHRR event codec (hdlab.binding / event_bundle / bound_event_backbone
— do NOT reinvent event binding, p4 owns it). NOTE the measured refinement: the JOINT
(subject,verb,object) FHRR store is SPARSER than the marginal (verb,object) store, so it
needs a LARGER domain corpus to be dense enough.

THE BAR (can-fail, CI-separated): the register-native store RECOVERS who-did-what
CI-separated over the current out-of-domain (simplewiki) store on a HELD-OUT
domain-matched test, with a VERB-SHUFFLED twin LOSING and a DOMAIN-SCRAMBLE control
(same corpus, wrong-domain labels) LOSING — so the DOMAIN, not leakage or any in-corpus
signal, does the work. A rigorous located negative (the domain lever fails to transfer
to a disjoint corpus) is a full PASS if it names why.

DO NOT REDO (measured non-levers / closed routes): richer features (Binder-65/GloVe-300),
a cleverer combiner / arbitration / hybrid, parser register-adaptation via self-training,
a bigger OUT-OF-DOMAIN corpus, or the leave-one-sentence-out probe (that was a probe, not
a disjoint deliverable — leakage risk).

FULL BRIEF ON DISK: notes/problems/the_plausibility_prior_is_a_coarse_centroid_needs_a_
structured_verb_role_exemplar_store/PROPOSED_FOLLOWON_domain_matched_selectional_store.md
Proposed slug: the_selectional_event_store_is_learned_from_the_wrong_domain_needs_a_
register_native_corpus
