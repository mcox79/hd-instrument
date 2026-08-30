---
owner_verdict: DONE
---

Problem: the_reader_has_no_belief_timeline_what_an_agent_knew_when — SOLVED, EXCELLENT (self-graded), ready for review.

WHAT IT IS: the reader tracked WHO believes WHAT (belief_partition, a single-change snapshot) and ordered events
in TIME (temporal_order_register), but nothing COMPOSED them — it could not answer "what did agent A know AT THIS
POINT?", the core of a stale belief, dramatic irony, and deception. I built the missing per-agent BELIEF TIMELINE:
belief_A(X,T) = the value of the latest event about X that A OBSERVED with order <= T, persisting between observed
events (Dowty inertia), ordered by the temporal register, read out on the belief_partition FHRR organs. NO external
LLM (invariant). It is a faithful generalization of belief_partition from n=1 snapshot to n ordered changes.

BRAIN-FOUNDATIONAL (5 online drills, each CORRECTED the design — not rubber-stamps; full component audit in SOLVED):
- PINNED & copied: per-agent belief separate from reality (TPJ/mPFC, Saxe); observation-gating (seeing->knowing,
  Wimmer&Perner/Pratt&Bryant); sample-and-hold persistence (Dowty; frame problem); register-ordered chronology
  (Reichenbach; MTL); decoupled store beating the brain's curse-of-knowledge (Birch&Bloom); testimony/deception
  (Harris&Koenig; Sperber); evidence-gated inference (Sodian&Wimmer 1987); the knowledge GAP (dramatic-irony fMRI);
  graded posterior (Bayesian ToM, Baker 2017); confidence-as-precision (Pouget/Kepecs; TCM).
- Honestly OUR-INVENTION (flagged): the FHRR bind() ALGEBRA (unpinned at neural level, defensible computational
  model — SEM/Franklin 2020); the closed inference schema set (boundary to the next problem); threshold/tempering
  forms + parameter ranges (swept, never adopted).

MEASURED (reverify: .venv/Scripts/python.exe verification/test_belief_timeline.py  # 70/70):
- MECHANISM (construction gold, 60 scen / 542 q): timeline 1.000 [1,1] vs the timeline-agnostic current-belief
  floor (SAME cue) 0.460 [.41,.51], CI-separated; info-free order-shuffle twin p95 0.535; positive control (queries
  the floor CANNOT get) 1.000 vs 0.000; distance-flat vs floor collapsing to 0; reality/memory intact 1.000;
  hindsight-decoupling invariant 1.000; independent hand-authored 2nd gold 1.000 vs 0.542, 0 mechanism-vs-human
  mismatches.
- CAPABILITY, LIVE extraction in the loop: driven by the REAL observation-cue extractor (perceptual_access_ledger,
  0.951) on 15 real-English multi-event passages, belief accuracy 0.902 [.81,.98] vs floor 0.463, oracle 1.000,
  gap 0.098 = the known front-end residual (matches the ToM organ's 0.821 live). JOINT live order + live obs on
  flashback prose: 1.000 while narration-order, observation-blind, and floor all fail (0.000).
- SOURCES: observed / communicated (deception) / INFERRED (Sodian-Wimmer dissociation: gated 1.000 while never-
  infer 0.40 under-attributes and omniscient 0.60 over-attributes; inference-based deception representable).
- REPRESENTATION deepened to the brain target: crisp -> SET (superposition + CA3 cleanup_set, F1 1.000 vs crisp
  0.494) -> GRADED POSTERIOR (below-MAP ranking 0.957 vs both floors 0.505) -> recency->PRECISION unification
  (stale belief flattens, entropy Spearman 0.963 vs fixed floor 0.00; confidence = posterior entropy, Spearman 1.0).
- GAP / dramatic irony over time: 1.000 vs floor 0.667; divergence-window 1.0 vs 0.0.

HONEST BOUNDS: CI-separated numbers are on construction + authored real-English prose (the ToM organ's own basis);
full false-belief-over-time SCENES are NOT auto-minable from corpus — ENUMERATED directly (read all 170 real
LitBank staleness windows + 7 irony markers: ingredients present, no gold-labelable scene), so no corpus gold
exists, same limit the ToM organ answered by authoring. First-order belief only. FHRR read-out is substrate-native
in rep B / cleanup_set / the weighted posterior; rep A's selection is a computational-level model.

FILES (no hdlab/ touched, Q111): experiments/belief_timeline.py + belief_timeline_gold.py + 11 exp cells
(query, flashback_register, gap, authored, confidence, inference, uncertain, posterior, precision, live_e2e,
live_flashback_e2e) + real_prose incidence; verification/test_belief_timeline.py (70/70); the problem folder
SOLVED.md + 1 research note (4 drill sections). Ledger --check: EXIT 0.

FOR STRATEGY (you own hdlab, Q111): promote the spaCy-free core to hdlab/belief_timeline.py composing
belief_partition + temporal_order_register + graded_temporal_context — keep the DECOUPLED store (world writes a
belief slot only via an observed/communicated/inferred edge, the anti-hindsight invariant); wire the three update-
edge types + the graded posterior + confidence-as-entropy; make the belief-vs-reality / belief-vs-belief GAP a
first-class query. Fold the AUDIT UPDATE (new belief-TIMELINE sub-entry) into BRAIN_FOUNDATIONAL_AUDIT.md. Two
clean NEXT problems the drills seeded: (1) POMDP inverse-planning (infer the posterior from an agent's ACTIONS —
this problem built the representation); (2) the general derivation engine (arbitrary-premise reasoning, neurally
distinct). SOLVED.md is WIP until owner_verdict: DONE in OWNER_NOTES.md.
