---
owner_verdict: DONE
---

SUBMISSION — the_semantic_graph_is_static_needs_to_grow_from_reading_by_learned_consolidation

STATUS: PARTIAL (rigorous, multiply-controlled LOCATED NEGATIVE with confirmed brain sub-mechanisms).
Ledger-valid; witness verification/test_learned_graph_cls_grow.py = 4/4.
Reverify: .venv/Scripts/python.exe verification/test_learned_graph_cls_grow.py

RESULT (plain): I built the machinery to grow the reader's meaning-graph from its own reading, the brain's
way, and to read it with the brain's meaning-selection circuit. Growing the graph does NOT improve
word-sense choosing on standard tests — and the deep finding is WHY, established from ~8 controlled angles.

WHAT'S PROVEN
- Growth of the discrete graph ≈ static (Raganato argmax −0.0088); density excluded (fails on the weak
  graph too). The failing edge-rule is rich-get-richer (naive learning helps common senses, starves rare
  ones); I built the brain's fix — HOMEOSTATIC BCM — and it CONFIRMED (rescues rare senses vs naive,
  +0.0155 CI-sep). Emergent signatures pass (frequency-dominance ρ=0.36; learned edges connect related
  senses, CI-sep).
- READ-SIDE POSITIVE (validated, controlled): the graded COMPETITIVE-SETTLING readout recovers rare
  (subordinate) senses far better than discrete argmax (+0.19), context-driven (beats shuffled-context
  +0.17 CI-sep), strongest for homonyms (brain-consistent). semantic_control reproduces the predecessor.
- ROOT CAUSE (why growth can't win): the discriminating signal for rare-sense selection is TOP-DOWN
  STRUCTURED COMPREHENSION (predictive coding; the N400 is semantic prediction error), NOT local
  co-occurrence. Confirmed by 5 prototyped routes all failing consistently: 3 gold-blind detectors,
  a continuous-representation prototype, a coherent situation-prediction prototype, and a 3-level
  structured-comprehension series (structure is real+correctly-directed on coarse senses; every
  typical-usage signal reinforces dominance and can't crack rare-sense override).

IMPORTANT: this is NOT a ceiling. "AI-complete" only means "needs full comprehension." The brain does it
glass-box; so can we — the apparent circularity (sense-level constraints need WSD) is BOOTSTRAPPING
(senses + comprehension co-develop through reading).

HOW TO FULLY SOLVE IT — GLASS-BOX, BRAIN-FOUNDATIONAL (NO external LLM at inference):
1. Wire the situation_reader (events/entities/roles) as the TOP-DOWN predictor.
2. Predictive coding: the situation model predicts each word's expected sense; prediction-error gates
   override. Selection = the validated competitive settling + semantic_control (glass-box).
3. Bootstrap: co-develop senses + comprehension via cross-situational reading (start coarse; comprehend →
   disambiguate → re-carve granularity with ultrametric_clustering → refine situation model → iterate).
4. Graded, SENSE-specific continuous representation (meaning_fusion node vectors) for situation-shaded meaning.

FOR STRATEGY (3 tiers, in SOLVED.md):
  TIER 1 — WIRE NOW (default-off, witnessed, Q111): the read organ (reordered-access → competitive
    settling → semantic_control). Real read-side upgrade even though growth doesn't help.
  TIER 2 — DO NOT wire the discrete-edge growth as-is (confirmed non-improvement).
  TIER 3 — FILE next problems where the gains live: (a) the North-Star comprehension/situation model
    [highest], (b) a learned graded-continuous sense space w/ emergent granularity, (c) domain-shift/OOV.

FILES: experiments/exp_learned_graph_cls_grow_v1.py (organ + harnesses + self-test),
  verification/test_learned_graph_cls_grow.py (witness 4/4),
  notes/problems/<slug>/{SOLVED.md, FIDELITY_AUDIT_AND_ADJACENT_MAP.md}.
NEW DATA (owner-authorized earlier): simplewiki, Raganato ALL, SyntagNet, ConceptNet; spaCy (local).

Owner may upgrade to SOLVED under the bar's "rigorous located-negative = full PASS" clause; I left it
PARTIAL as the honest default since the one route to a POSITIVE (build the comprehension model) is the
North Star, out of scope for a graph-growth problem.
