---
owner_verdict: DONE
---

Problem: the_assembled_reader_is_never_tested_as_a_whole_all_flags_on — SOLVED (WIP until
owner_verdict: DONE). No hdlab/ touched (Q111 — proposed diffs + exact plan in SOLVED.md).
Glass-box, NO LLM at inference. Reverify: .venv/Scripts/python.exe verification/test_assembled_reader_all_flags_on.py  (19/19)

WHAT IT IS: for the first time, turned ALL validated dimension flags ON together and measured the reader
as a whole (10-config flag matrix, 100 LitBank docs). The brief reads like bookkeeping; the real question
is the brain one: is the assembled reader an INTEGRATED situation model (one bound event token indexed on
all dimensions — Zwaan/Radvansky; SEM/Franklin 2020) or N PARALLEL SILOS? Answer, measured: SILOS.

RESULTS (100 docs, QA-capstone scorer; CI over docs):
- NO-REGRESSION is BYTE-EXACT: every dimension's all-flags-on output == its isolated output (interaction
  exactly 0). Silos confirmed: perturbing the event set leaves every other dimension byte-identical (5
  independent event extractors on 3 tokenizers; no shared token). Holds off-genre (modern passages) too.
- AGGREGATE, met POSITIVELY once the instrument reads each dimension's CORRECT field: fully-on-corrected
  0.399 vs default 0.322, +0.077 CI [+0.066,+0.089] SEPARATED, info-free twin collapses (0.098). Driven by
  events 0.158->0.272; coref/temporal/causal held (no regression).
- The NAIVE aggregate does NOT beat default — but only because the QA temporal+causal GOLDS derive from
  sm.events, which the tense-agnostic keystone rewrites: an INSTRUMENT coupling (temporal Qs 1998->0; causal
  gold inflates 267->461), NOT a reader regression (the dimension fields are byte-identical). Fix shown:
  reading sm.timeline_order answers 0.98 of temporal Qs at 0.91.
- INTERACTION MAP: full matrix + additive marginal/joint on the one shared field (role-acc 0.158 +TA 0.085
  +RR 0.023 = 0.267 ≈ observed 0.272); events null p95 0.024. 5th flag (spacy_pred_gate) measured: changes
  the event set 100/100 docs. Two landed dimensions (typed_causal_links, timeline_order) are INVISIBLE to
  the QA readouts — "wired into the reader, not into the instrument."

DEEPENING (3 brain drills — pushed past the wall instead of stopping):
- WHAT INTEGRATION BUYS: the silo stores the MARGINALS (set of agents/times/causes); a bound token stores
  the JOINT (which goes with which) — the binding problem. Established for the brain by a hippocampal-amnesia
  double dissociation; OPEN for a reader. Demonstrated on the real FHRR algebra (PoC, self-test PASS): JOINT
  disambiguation 1.00 + binding-shuffle SENSITIVE; MARGINAL 0.47 chance + shuffle-INVARIANT. My first
  constructed proof FAILED honestly (at type-cardinality 1 the joint is recoverable from the marginals — a
  design artifact); the non-gameable discriminator is binding-shuffle invariance.
- HOW THE BRAIN SCALES IT: measured "must chunk" — a single passage-level bound register collapses ~1/sqrt(M)
  (0.99 at 64 events -> 0.39 at 256 -> 0.12 at 512; a passage has ~100-250), while a slotted multibank
  register stays flat. So the faithful shared event token is TIERED, not one superposition.
- HAVE WE DONE IT ELSEWHERE (prior-work check, both archives): YES — every tier is a BUILT hdlab organ, none
  wired into the reader: n400_coherence_monitor.py (EST prediction-error boundary/segmentation),
  slot_attention_wm.py + situation_model_multibank (slotted active register), hippocampal_encoder.py (DG
  sparse + CA3 + CLS consolidation = episodic store). This CORRECTED my own draft (segmentation is NOT
  un-built) and reframed the next problem from "build" to "ASSEMBLE existing organs."

HONEST BOUNDS: I proved the reader COMPOSES and that reading it right beats the weak default, and that the
JOINT buys disambiguation the marginal can't — but NOT the end-to-end COMPREHENSION win on real text (that
needs the tiered reader + a real gold). The causation shared-event wire changed 24% of narrative links but
scored parse==reader=0.833 on a curated gold too clean to discriminate. The +0.077 aggregate is single-genre
(no modern coref+who-did-what gold on disk). The temporal "fix" is statistically equal to the working default
readout (no regression, not a gain). DG's prior HARD_FAILs were tested on the WRONG TIER (its faithful job is
the episodic store, not active-read) — re-scope before re-quoting.

KEY REALIZATIONS: silos make no-regression trivially true — composition without interaction is NOT
integration; a negative aggregate can be an instrument artifact (prove it by consuming the actual field); the
silo defect's precise name is the binding problem (marginals vs joint); the brain MUST CHUNK, so "one shared
register" is itself not brain-faithful — the tiers are already built, just unassembled.

FOR STRATEGY (you land hdlab, Q111): (1) make the QA capstone the fully-on instrument reading each dimension's
correct field (timeline_order for temporal; tense-independent temporal/causal golds) — the correct baseline
every solver needs; (2) NO default flip yet (RR is the only aggregate-positive, instrument-safe flag). CORRECT
BASELINE to measure against: SituationReader(tense_agnostic_events=True, role_route="wired",
causation_typed=True, timeline_register=True, spacy_pred_gate=True). NEXT PROBLEM (ranked, in SOLVED.md):
ASSEMBLE the TIERED event-memory backbone into the reader — small slotted active token (multibank/
slot_attention_wm) + n400_coherence_monitor boundary controller (flush+reset) + hippocampal_encoder episodic
store + retrieval; gated on the tense-preserving detector landing. Validate with same-lemma EVENT COREFERENCE
on ECB+ (acquire it) vs a late-fusion-of-marginals baseline + the binding-shuffle control. Then wire the
built-but-island SPACE/STATE dimensions; BELIEF last (adapter-gated, Phase-2 kill-condition aware). Fold the
AUDIT UPDATEs into BRAIN_FOUNDATIONAL_AUDIT.md §2b (the parallel-silo gap; the QA-instrument coupling; the
tiered-organ map; the DG-wrong-tier rehabilitation).
