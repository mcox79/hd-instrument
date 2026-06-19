# exp_dev hand-off -- research: substrate-classical NL multi-seed variance + Tier-B -> Tier-A lift

Filed-by: research:opus
Filed-at: 2026-06-11 (date-rolled 2026-06-12)
Trigger: 2x DEEP drill delivery
  Source: notes/research_drill_substrate_classical_nl_multiseed_variance_pattern_2x_2026-06-12.md
Pause state: respect data/orchestrator_paused.flag at pickup

Per [[feedback-no-experiment-design-in-prompts]]: this file routes anchor
candidates only. exp_dev owns experiment design.

## Anchor candidates (rank-ordered by P_deflated x lift / cost)

### Anchor 1: E1-SHARED-FEATURE-LIBRARY-SLOT-CHUNK-NERFINE
- Pointer: substrate-CRF Tier-1 shared feature library (Brown clusters bit-prefixes
  2/4/6/8/10/12/16/20 + gazetteer indicator atoms + morphology
  prefix/suffix bigrams/trigrams + position-in-sentence + bidirectional
  context-window=5) applied to slot-filling (ATIS), chunking
  (CoNLL-2000), NER-fine (OntoNotes-18) substrate-only
- Substrate-product reading: lifts 3 Tier-B capabilities at once via
  one architectural addition; expected slot +0.10, chunk +0.01,
  NER-fine +0.07; matches classical-feature ceiling for chunking;
  approaches Tier-A boundary for slot
- Tier hint: Tier-A (HARD-PASS) for slot at 0.82+, boundary for
  chunking at 0.935, Tier-B-firm for NER-fine at 0.62+
- Why now: Tier-B set just stabilized empirically Day 2 evening; lift
  path has strong literature precedent (Brown clusters + gazetteer);
  highest compounding leverage of any single intervention

### Anchor 2: AVERAGED-PERCEPTRON-VARIANCE-REDUCTION-CROSS-CAPABILITY
- Pointer: averaged structured perceptron + bootstrap-aggregation over
  the structured perceptron + count-NB family; apply across all 8
  current NL capabilities
- Substrate-product reading: variance reduction 30-50% on multi-seed
  sigmas without mean shift; tightens Tier-A CIs (defensible publication-
  grade reporting); reduces seed-cherry-picking risk
- Tier hint: variance attack only; no Tier movement on means but
  tightens existing Tier placements
- Why now: gold-standard literature variance reducer (Collins-2002);
  half-day implementation; addresses recurring single-vs-multi-seed
  concern across capabilities; cleanest cheap intervention

### Anchor 3: DISCRIMINATIVE-WEIGHTED-PER-CLASS-NER-FINE-SLOT
- Pointer: discriminative-weighted per-class feature extraction
  (per-class weight matrix learned via averaged structured perceptron)
  applied to NER-fine OntoNotes-18 + slot-filling ATIS
- Substrate-product reading: applies the validated universal mechanism
  (discriminative weighting per north-star-won) to asymmetric span
  tasks; expected NER-fine +0.05-0.10, slot +0.03-0.05
- Tier hint: lifts NER-fine within Tier-B band; lifts slot toward
  Tier-A boundary in combination with Anchor 1
- Why now: validated universal mechanism from north-star empirical win;
  asymmetric multi-class span tasks are the natural next target;
  cross-thread with methodology-benchmark-must-break-symmetry

### Anchor 4: CLASS-AWARE-BOOTSTRAP-REWEIGHTING-SPAN-EVAL
- Pointer: class-aware bootstrap reweighting in eval harness for span
  tasks with class imbalance > 0.80 (CoNLL-2003 O=0.82, OntoNotes-fine
  O=0.88)
- Substrate-product reading: variance attack on span-F1 noise from
  class imbalance; sigma reduction 20-30% without mean change; eval-
  harness-only (no substrate change)
- Tier hint: variance attack only; tightens Tier placements
- Why now: cheap (eval harness only); addresses span-F1 noise
  specifically; pairs with Anchor 2 averaging for cumulative variance
  reduction

### Anchor 5: VARIANCE-FRAMEWORK-PILOT-1 (structural self-knowledge)
- Pointer: fit predicted_sigma = a*sqrt(1/N_test) + b*I(span) +
  c*(1-feature_density) + d*imbalance_O against 8 observed sigmas;
  evaluate R^2 and coefficient CIs
- Substrate-product reading: per substrate-deep-self-evaluation-program
  Layer 1 attribution; demonstrates substrate KNOWS WHY each capability
  sits where it does; substrate-product differentiator vs LLMs
- Tier hint: not a capability lift; meta-evaluation of capability
  predictor; HARD-PASS R^2 > 0.80
- Why now: variance framework is the synthesis output of this drill;
  pilot validates substrate self-knowledge claim cheaply; can run
  same day with existing multi-seed data

## Context pointers (file paths, not summaries)

- notes/research_drill_substrate_classical_nl_multiseed_variance_pattern_2x_2026-06-12.md
- notes/research_drill_substrate_classical_mechanism_transfer_replication_2x_2026-06-12.md
- memory: substrate_classical_NLP_methods_outperform_phasor_2026-06-11.md
- memory: substrate_only_NL_pos_tagger_validated_2026-06-11.md
- memory: substrate_discriminative_beats_generative_asymmetric_NL_2026-06-11.md
- memory: north_star_won_discriminative_weighting_universal_2026-06-11.md
- memory: methodology_benchmark_must_break_symmetry_2026-06-11.md
- memory: feedback_method_overclaim_lift_validation.md
- memory: feedback_smoke_test_methodology.md

## Contract

- Pick highest-ranked anchor first unless cap_map / queue state argues
  otherwise; combine Anchor 1 + Anchor 2 for compounding gain on slot
- Multi-seed (n >= 5) MANDATORY on all Tier-A claims and all lift claims
- Lift must exceed 2 * SE per [[feedback-method-overclaim-lift-validation]]
- Pre-registration: every cell ships with HARD-PASS + HARD-FAIL bands
  from the research note above
- Smoke gate first (composition-matched per [[feedback-smoke-test-methodology]])
- No architectural-ceiling claim without N-sweep + tier-hierarchy + multi-
  benchmark + adversarial probes (per [[feedback-dont-parrot-drill-defeatism]])

## Autonomy declaration

exp_dev owns: cell file path, seed selection, smoke composition, queue
target (overnight / home-cpu / local-cpu), per-cell HARD-PASS/HARD-FAIL
ranges within the bands here, ship order.

research provides: anchor pointers + expected lifts + pre-reg bands +
brain analogues + literature precedent.
