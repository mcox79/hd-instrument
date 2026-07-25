# Pre-reg: composed_differentiation_loop_v1

Cell: `experiments/exp_composed_differentiation_loop_v1.py`
Metrics: `data/exp_composed_differentiation_loop_v1/metrics.json` (full) / `_smoke/` (smoke)
Contract: INLINE-LOCAL foreground-to-completion; NO borrowed vectors in the composed build; NO push/remote-persist; ASCII-only; deterministic; repo .venv; agent-reported VET-PENDING.

## Scientific question
Can composing our OWN competitive-Hebbian representation (`hdlab/concept_encoder.py`) with our OWN MDL model-selection learner (`hdlab/learner/`) over REAL typed WorldTree relations LEARN fine-meaning discrimination that GENERALIZES to NEW concepts, where frozen GloVe memorizes (held-out ~0.128) and even BGE-learned reaches only 0.228? Generalization MUST be at the FEATURE/RELATION level (shared across concepts), NOT per-concept lookup. If only per-concept memorization works, the learner's compression_ratio < 1 -> KEEP_EPISODIC (the built-in generalize-not-memorize guardrail), reported as an HONEST fail.

## Composition (all our own parts; no borrowed vectors in the build)
1. REPRESENTATION = ConceptEncoder (competitive-Hebbian sparse coding + WTA), pointed at REAL relational data (its active dims become learner feature tokens; held-out concepts get features via nearest-train-concept transfer, measured by ablation).
2. GENERALIZATION ENGINE = learner registry (MDL model-selection: estimation + ruleind + gam; proginduction excluded by default -- see below).
3. LOAD-BEARING: features are typed relations shared across concepts + ASK token; the TARGET relation is EXCLUDED from a concept's own features (non-circular). Held-out concept encoded/scored from its OWN OTHER known relations via the learned rules.

## Brain-fidelity map (element -> mechanism -> SHAPE/ORDER/METRIC + flagged gaps)
- concept_encoder -> cortical competitive-Hebbian/WTA sparse coding (Foldiak/Kohonen). SHAPE ok. GAP: batch accumulator is ORDER-INVARIANT -> cannot express Rogers-McClelland curriculum LEARNING DYNAMICS; label-conditioned aggregation = binding, not error-driven prediction. FLAGGED, not fixed in scope.
- typed-relation features -> Rogers-McClelland PDP relational differentiation. coarse->fine reported as a STATIC signature (coarse KINDOF vs fine held-out), not a dynamic (see gap above).
- learner MDL gate -> Complementary Learning Systems (McClelland-McNaughton-O'Reilly): rule = neocortical SEMANTIC generalization; KEEP_EPISODIC = hippocampal EPISODIC retention. MDL two-part code = computational-level formalization of that trade-off. Right shape.
- working memory -> Cowan ~4: MAX_COACTIVE_REL=4 co-active relations/concept (matches WorldTree ~2.5-central-fact). Right shape+metric.
- supervision = error -> learner is MDL/description-length error-driven (right). concept_encoder is label-conditioned (GAP, flagged).

## Plugins (brain-compliant lead)
PRIMARY: ruleind (PFC rule learning) + estimation/gam (evidence/graded integration). proginduction (enumerative boolean-DSL) has NO direct biological analog AND its <=2-output boolean form is structurally unsuited to a hundreds-of-values multiclass value target -> EXCLUDED by default (`INCLUDE_PROGIND=False`). If ever enabled and MDL-selects it, that is reported explicitly as a measured departure from biology. The MDL-selected plugin per seed is reported.

## Data-integrity preflight (garbage-in guard; gates FULL-run INTERPRETATION)
- Relation-label precision proxy: curated column-stable tables only (KINDOF/MADEOF/PARTOF/HABITAT/CONTAINS/SOURCEOF/USEDFOR/PROP-RESOURCES-RENEWABLE); noisy free-text relations (e.g. IFTHEN ~0.13 precision) EXCLUDED a priori. Report per-relation clean-parse fraction; floor MIN_REL_PRECISION_PROXY=0.70.
- Multi-valid-value rate: reported; distractors EXCLUDE ALL of a concept's valid values + its alias-value set (no false negatives).
- Identity normalization: WordNet morphy lemmatize + plural merge (cat/cats -> cat).
- Density: per-concept relation-count distribution; held-out scorable iff >=2 distinct relations.
Preflight PASS requires: no curated relation below the precision floor AND frac_ge2 >= 0.20. FAIL -> DATA_NOT_READY verdict, STOP before headline accuracy.

## Fairness gates (all pre-registered, all reported in metrics `gate_outcomes`)
- G1 MFV baseline (most-frequent-value per relation): composed win MUST beat MFV by MARGIN_OVER_MFV=0.03, not just chance.
- G2 SHUFFLED-RELATION control: shuffle rel->value in training, re-run learner; held-out MUST collapse to <= MFV + 0.03. Survives => void (spurious shortcut).
- G3 apples-to-apples: GloVe zero-fit AND GloVe-learned (converged ridge) recomputed on the SAME items/split/NEUTRAL distractors. BGE-learned 0.228 is a CITED external bar (inline BGE-model recompute out of scope -> flagged, NOT on the same distractor set). Distractors are REPRESENTATION-NEUTRAL (random from the relation's pool), identical for every arm.
- G4 no-leak + non-circular: held-out concepts NEVER in any training episode; target relation EXCLUDED from a concept's features.
- G5 ablation: (a) GloVe-learned; (b) learner over CE codes only; (c) CE cosine no-learner (nearest-train transfer); plus composed-without-CE (relation-only). Attributes signal to learner / encoder / relations.
- G6 coverage honesty: report scorable held-out fraction; aggregate accuracy over ALL held-out (unscorable counted, not dropped).

## Design gates (design-gate before full)
- real baseline: GloVe zero-fit + GloVe-learned on same set.
- can-fail: KEEP_EPISODIC / held-out <= max(MFV, 0.228) / shuffle-survives are all honest fails, pre-registered.
- difficulty-on: neutral distractors from same-relation pool; frozen below FROZEN_SAT=0.85.
- one variable: only the concept->value predictor changes; identical items/candidates/split.

## Config (a priori; NOT tuned)
K_DISTRACT=5 (chance ~0.167); HELDOUT_FRAC=0.20; MAX_COACTIVE_REL=4; CE_N_DIM=1024; CE_K_SPARSITY=0.02; SEEDS full=(20260725,13,101), smoke=(20260725,); INCLUDE_GAM=True; INCLUDE_PROGIND=False; ruleind max_conjunct=2 min_coverage=3 purity=0.60 max_singles=40.

## Verdict bands (a priori)
- EARNS-GENERALIZING-MEANING: composed held-out CI-lower > max(MFV, 0.228) AND (composed - MFV) >= 0.03 AND compression_ratio > 1 (chosen != KEEP_EPISODIC) AND shuffle collapses AND composed > GloVe-learned.
- MEMORIZES-KEEP-EPISODIC (HARD_FAIL): chosen == KEEP_EPISODIC OR compression <= 1 OR composed held-out <= max(MFV, 0.228) OR shuffle survives.
- MIDDLE: beats MFV + chance with compression > 1 but not to the clear bar.
- DATA_NOT_READY / INVALID: preflight fails / < MIN_HELDOUT_ITEMS=60 held-out fine items / frozen saturates.

## Cell-template compliance
except SystemExit before except Exception (no BaseException/bare); tmp_replace atomic metrics; start-marker; crash-diagnostic; heartbeat; deterministic (hashlib not builtin-hash for per-item RNG); self-test exercises REAL parse + ConceptEncoder + learner.learn AND a planted rule env (generalizes) + planted no-rule env (KEEP_EPISODIC/no-generalize); arms_differ; no-leak + non-circular asserted.
