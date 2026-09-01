---
owner_verdict: DONE
---

Problem: the_assembled_reader_is_parallel_silos_assemble_the_tiered_bound_event_token — SOLVED (WIP until
owner_verdict: DONE). No hdlab/ touched (Q111 — proposed default-off wire in SOLVED.md).
Glass-box, NO LLM at inference. Reverify: .venv/Scripts/python.exe verification/test_tiered_bound_event_token_coref.py  (10/10)

WHAT IT IS: the p4 test proved the assembled reader is N PARALLEL SILOS — each dimension stores the MARGINALS
(the set of agents / actions / times), nothing stores the JOINT (which agent did which action). That's the
BINDING PROBLEM. I ASSEMBLED the four already-built-but-unwired hdlab organs into a TIERED bound-event-token
backbone — FHRR-bind all dimensions onto ONE event token (situation_model_accumulate) → chunk into a slotted
active register (situation_model_multibank) segmented by prediction-error boundaries (n400_coherence_monitor)
→ consolidate to a DG-sparse + CA3 episodic store (hippocampal_encoder) — and proved it stores the JOINT the
silos cannot, on real event structure from LitBank (old fiction) AND UD-EWT (modern web).

BRAIN FRAME (PINNED): comprehension builds ONE bound event token indexed on all dimensions (Zwaan&Radvansky
event-indexing; Franklin SEM); same-event recognition is CA3 pattern completion (Marr 1971); the decisive
control is RECOMBINATION — same items rebound differently — the conjunctive-memory dissociation (Konkel&Cohen
2009). The brain MUST CHUNK because one passage-scale superposition collapses ~1/√M (Plate/Frady).

RESULTS (witness 10/10, bootstrap CIs, both genres):
- JOINT event-coref 1.000 CI-ABOVE late-fusion-of-marginals 0.600 and lexical 0.600 (sep 0.40, both genres).
- BINDING-SHUFFLE control LOSES CI-separated (0.64; it breaks POSITIVE recognition 1.0→0.12 while marginals
  are untouched — the exact conjunctive-memory signature). Info-free twin = null. Type-cardinality artifact
  ruled out (joint rejects recombinations at card=1 too; marginal fails at every level).
- MUST CHUNK: a single FLAT bundle collapses at passage scale (1.0→0.38 @ M=256) while the multibank +
  DG/CA3 tiered registers hold (1.00). Analytic bridge: a flat superposition of event tokens IS the marginal
  silo (its linear readout = sum of marginals) — the tiers are not optional.
- CUED RETRIEVAL: partial-mention → bound token retrieves the event at 1.00 vs the silo 0.01 (chance 1/M) —
  the silo structurally cannot address an event; pattern completion is binding-only.
- NECESSITY (beyond the bar — where binding BEATS a symbolic dict, not just ties it): under PARAPHRASE (verb→
  WordNet synonym), binding GROUNDED sensorimotor concept vectors (Lancaster, ATL-hub) recovers coref at 0.385
  vs symbolic-exact 0.219 / arbitrary-symbol 0.219 / grounding-twin 0.178 (chance 0.219); exact-control all
  tie at 1.00 → grounded distributed binding is NECESSARY for graded matching, not just sufficient.

WALLS DRILLED TO ROOT CAUSE (owner: "drill all walls" + "the phase diagram"):
- EXTRACTION-ROLE (the real ecological bottleneck): event recall 0.95 but agent-role 0.27 → the integration
  gap is the FRONT-END role assignment, not recall, not the binding codec (the brief's "name WHY").
- N400 chunk tier: bounding the register is NECESSARY (unbounded degrades 0.95→0.88 late), but the N400's
  content boundaries don't beat fixed-size on retrieval — their specific value needs an event-boundary gold.
- CA3 completion: the retrieval path DG-SEPARATED the cue (should be EC→CA3-direct; DG is for ENCODING);
  iterating collapses to a dominant attractor; the direct similarity path completes 1.00.
- GROUNDED-COARSENESS / FUSION (via the PHASE DIAGRAM): the dual-route complementarity is REAL (grounded ⟂
  distributional, correctness corr −0.04, oracle ceiling 0.60), but no simple fusion extracts it — swept the
  distributional corpus scale and it's FLAT because UD-EWT is only ~12.5k sentences: the wall is CORPUS SIZE,
  NOT compute. Familiarity/frequency weighting is the right brain-faithful signal (0.40 > z-sum 0.37). [Fixes
  an n-mismatch: my earlier "fusion 0.44 > grounded 0.41" is WITHDRAWN — on matched n it doesn't beat grounded.]

HONEST BOUNDS / would withdraw first: the coref task uses CONSTRUCTED recombination/paraphrase probes on real
extracted structure, not annotated cross-doc coref (ECB+ is the follow-on). The joint TIES the symbolic
ceiling on the core task (binding's necessity shows under paraphrase + at passage scale, not on clean exact
coref). slot_attention_wm unused (multibank is the slotted register); downstream comprehension not measured.

FOR STRATEGY (you land hdlab, Q111): default-off `bind_event_tokens` flag on SituationReader.read() — after
extraction, build sm.event_tokens (FHRR bind of the dimension fillers) + a tiered store (multibank WM +
hippocampal episodic), byte-identical when off. AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT §2b): hippocampal_
encoder CA3-completion is low-fidelity (DG-at-retrieval) — fix = EC→CA3-direct. FOLLOW-ON PROBLEMS, now
sharply scoped: (1) front-end role assignment (0.27 → the ecological lever); (2) large-corpus distributional +
familiarity/learned fusion = the reader_meaning_channel; (3) faithful CA3 completer; (4) ECB+ real coref.

FILES: experiments/exp_tiered_bound_event_token_coref_v1.py; experiments/exp_grounded_binding_paraphrase_
coref_v1.py (necessity); experiments/exp_grounded_distributional_fusion_paraphrase_v1.py + _build_fusion_
instances.py (fusion/phase-diagram, remote-safe); experiments/_drill_ca3_completion.py + _drill_n400_chunking.py;
verification/test_tiered_bound_event_token_coref.py (10/10); notes/problems/<slug>/SOLVED.md + supporting notes.
