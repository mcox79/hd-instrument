---
owner_verdict: DONE
---

SUBMISSION — audit_the_grounding_acquisition_subsystem_for_non_brain_faithful_stand_ins
Status: SOLVED (audit = the deliverable; fix program = owner-directed bonus, prototyped not landed). Your DONE gates integration.
Reverify: .venv/Scripts/python.exe verification/test_audit_grounding_subsystem.py  → 15/15 PASS   | ledger: malformed 0
Deliverables: notes/problems/audit_the_grounding_acquisition_subsystem_for_non_brain_faithful_stand_ins/{CATALOG.md,SOLVED.md}
NO hdlab/ writes (Q111 — map + proposed diffs + prototypes only).

THE AUDIT (the bar, met). Denominator by a RUNTIME import+call trace of the grounding subsystem's live entry point
Substrate.read() (not comment-grep): 16 LIVE-CALLED / 23 LIVE-IMPORTED-INERT / 6 DORMANT-ISLANDED, positive control fired.
CATALOG.md = 4 LIVE stand-ins + 3 corrections, five disk-verified fields each, top-K:
  G1 (CRITICAL) the meaning read-out decides by a BAG-OF-WORDS CO-OCCURRENCE cosine — loses to word-counting on the loop's
     OWN metric (SUBSTRATE 0.016-0.030 < counting 0.048-0.065). NOT_BF.
  G2 (HIGH) the grounded input channel `grounded_similarity` is imported but INERT (funcs=0) — the comparator has no
     grounded input. G3=C7 attractor-as-RANKER in the gap gate (LIVE, bounded; filed pri-5). G4=C8 store trust-only vetting
     (correctness gated upstream, remediated). N1 dormant+refuted structured encoder; N2 dormant VWFA; N3 six dormant orchestrators.

#1 LOCALIZED on the own metric (powered, can-fail): a DISSOCIATION — a brain-faithful ATL channel beats co-occurrence on
grounded MEANING (SimLex 0.521 vs 0.371, twin loses) but ties it on the loop's OWN relatedness gold → the stand-in is
locally optimal for a MIS-SPECIFIED (relatedness) objective over an UNGROUNDED input.

THE FIX (owner "do all", prototyped, brain-foundational, measured on a SimLex representation proxy — NOT the live loop):
 - You were right that my first "negative" was an UPSTREAM-FIDELITY artifact: I'd hardcoded POS, used a raw sum not the
   ATL's covariance distillation, and a syntagmatic bag not paradigmatic context. Fixing all three (in-substrate UPOS tagger
   + Rogers-McClelland distillation + dependency context) flipped grounded to the best arm.
 - OPTIMIZED FIX = coverage-aware PRECISION-WEIGHTED fusion (direct grounding where covered, context fallback; Ernst-Banks/
   Friston + hub-and-spoke): beats the stand-in +0.125 CI[0.052,0.199] @40% coverage, scales to 0.49.
 - MULTIMODAL ATL HUB (verbal+sensorimotor+affective, covariance distillation): SimLex 0.575 = 86% of human (0.67), +0.042
   CI[0.024,0.062] over verbal-alone; twin loses. Overall the read-out goes 6% → 86% of human, every win stress-tested.
 - TWO HONEST NEGATIVES (leakage-guarded): taxonomic RETROFIT REJECTED (its +0.04 is answer-key leakage — holdout is CI-sep
   WORSE than the hub); BINDER-EXTENSION NO GAIN (valid map R²=0.58 but bounded by inputs; even real Binder for the 14% of
   SimLex words it covers adds nothing — experiential axis is weaker than taxonomic for SimLex). Located ceiling = 86%.

COMPONENTS + BF STATUS and LOAD-BEARING ASSETS TO INGEST are tabled in SOLVED.md. Key ingest list (grounded-meaning
foundation, several on-disk but UNWIRED): WordNet (verbal, live) + Lancaster sensorimotor norms + Warriner VAD + Brysbaert
concreteness (+ Binder-2016 as the experiential reference); AND replace the ConceptNet-RELATEDNESS growth objective with a
grounded-MEANING objective. The ConceptNet own-metric is a relatedness gold (mis-specified); SimLex/WordSim are eval-only.

hdlab WIRE (land together, Q111): (a) DIRECT multimodal grounded spoke = wire the inert `grounded_similarity` + broaden
`definitional_extraction`, fused with Lancaster/Warriner/Brysbaert (reliability-weighted, verbal-dominant); (b) coverage-aware
fusion in `canonicalize` (direct where grounded, context fallback); (c) a MEANING objective (not ConceptNet relatedness);
(d) coverage grows online (propose-verify). C7→graded read is filed pri-5 (don't duplicate). DO NOT: ground the sentence bag,
rebuild the random-code structured encoder (N1), or retrofit-to-WordNet (leaks).

Files: experiments/exp_audit_grounding_subsystem_v1.py, exp_ground_readout_localization_v1.py,
exp_grounded_meaning_readout_{v1,structured_v1,remote_sweep_v1,coverage_fusion_v1}.py, exp_multimodal_hub_v1.py,
exp_semantic_hub_retrofit_v1.py, exp_binder_extension_hub_v1.py, verification/test_audit_grounding_subsystem.py, + CATALOG.md/SOLVED.md.
