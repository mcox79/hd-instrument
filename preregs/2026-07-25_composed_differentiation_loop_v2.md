# Pre-reg: composed_differentiation_loop_v2

Cell: `experiments/exp_composed_differentiation_loop_v2.py`
Metrics: `data/exp_composed_differentiation_loop_v2/metrics.json` (full) / `_smoke/` (smoke)
Predecessor: v1 (atom 29561, commit 05834fbc8) returned MEMORIZES-KEEP-EPISODIC, but its "foundation-saturated" story was WRONG -- off-disk VET found 2 bugs + 1 partial-density gap. V2 applies the 3 required fixes + a denser source.
Contract: INLINE-LOCAL foreground-to-completion; the encoder under test is NATIVE `hdlab/concept_encoder.py` (WTA); GloVe + BGE are BASELINES ONLY (borrowed-embedding-never-the-encoder); NO push/remote-persist; ASCII-only; deterministic; repo .venv; agent-reported VET-PENDING.

## Scientific question (unchanged from v1)
Does composing our OWN competitive-Hebbian representation (`hdlab/concept_encoder.py`) with our OWN MDL model-selection learner (`hdlab/learner/`) over REAL typed WorldTree relations EARN fine-meaning discrimination that GENERALIZES to NEW concepts (feature/relation-level, NOT per-concept lookup)? The frozen-GloVe forced-choice bar and honest MFV are the real bars; KEEP_EPISODIC / not-beating-the-bar is a pre-registered HONEST NEGATIVE, never hidden.

## V2 fixes (VET-mandated)
- (A) SCORER FIX (standing fairness gate): v1 always placed gold at candidate index 0, and an abstaining predictor returned index 0 -> auto-scored correct -> MFV inflated to 0.9665 (true base-rate ~0.06) contaminating every learned bar. V2 places gold at a RANDOMIZED per-item position (deterministic per-item hash); all scorers score `pick == it['gold_pos']`; a fixed-index / abstain fallback now yields ~chance (1/n_cand). Self-test asserts an always-abstain predictor scores ~chance (MEASURED 0.150 vs chance 0.167), not ~1.0.
- (B) CE->LEARNER BRIDGE: v1 fed the MDL learner ~20 raw high-cardinality ConceptEncoder active-dim tokens/concept (`CE<dim>`) -> description-length blowup -> compression<1 -> false KEEP_EPISODIC. V2 QUANTIZES the native `concept_hds` codes into `CE_N_PROTOTYPES=48` cluster prototypes (deterministic spherical k-means) and emits ONE low-cardinality `CEPROTO<k>` token/concept -- a LEARNED category the MDL plugins compress over. The estimation category-generalizer key uses symbolic KINDOF when present, ELSE the EARNED CEPROTO category (CE supplies a category where the symbolic KB is silent). Held-out concepts -> nearest train concept (CE cosine) -> its prototype. NO borrowed vector enters the CE code or the prototype. Self-test asserts a rule carried ONLY by the CEPROTO token generalizes to held-out (MEASURED acc 1.0, compression 14.8).
- (C) FREQUENCY-MATCHED HARD DISTRACTORS: v1 drew neutral distractors uniformly from the relation pool -> MFV could win trivially. V2 draws distractors from the gold value's SAME marginal-frequency quantile bin (`FREQ_MATCH_BINS=4`, standard freq-matched hard-negative binning) excluding the concept's valid + alias values -> the frequency prior cannot preferentially pick gold; confusability restored WITHOUT representation bias. K adapts to same-bin pool size (chance = mean 1/n_cand, reported).

## Denser source (the real density fix)
Widened from the v1 8-table slice to the FULL WorldTree v2.1 tablestore, AUDITED to 27 CLEAN tables (per-table parse-precision floor 0.70): structural/category FEATURE backbone (KINDOF/MADEOF/PARTOF/HABITAT/LOCATIONS/USEDFOR/CONTAINS/SOURCEOF/FORMEDBY) + multi-valued PROP-* property TARGETS (MAGNETISM/CONDUCTIVITY/CHEM-ACIDITY/HARDNESS/WARM-COLD-BLOODED/SOLUBILITY/MAT-OPACITY/MAT-DURABILITY/FLEX-RIGIDITY/RECYCLABLE/CHEM-REACT/CHEM-CHARGE/RESOURCES-RENEWABLE/INHERITEDLEARNED/STATESOFMATTER-TEMPS) + typed relational targets (XIVORE/PREDATOR-PREY/CONSUMERS-EATING). AFFECT (precision 0.47) + INSTANCES (0.69) DROPPED by the precision audit (< 0.70 floor). Widened frac_ge2 = 0.2398 (MEASURED@full, clears the 0.20 floor; v1 was 0.2017).

## Brain-fidelity map (element -> mechanism -> SHAPE/ORDER/METRIC + flagged gaps)
- concept_encoder -> cortical competitive-Hebbian/WTA sparse coding (Foldiak/Kohonen). SHAPE ok. GAP: batch accumulator is ORDER-INVARIANT -> cannot express Rogers-McClelland curriculum LEARNING DYNAMICS; label-conditioned aggregation = binding, not error-driven prediction. FLAGGED, the NEXT build (not fixed here).
- CE prototype quantization -> categorical abstraction over the learned code manifold (learned category ~ cortical prototype). SHAPE ok; static (no curriculum dynamic).
- typed-relation features -> Rogers-McClelland PDP relational differentiation. coarse->fine reported as a STATIC signature.
- learner MDL gate -> Complementary Learning Systems: rule = neocortical SEMANTIC generalization; KEEP_EPISODIC = hippocampal EPISODIC. MDL two-part code = computational-level formalization. Right shape.
- working memory -> Cowan ~4: MAX_COACTIVE_REL=4 co-active relations/concept. Right shape+metric.
- supervision = error -> learner is MDL/description-length error-driven (right); concept_encoder is label-conditioned (GAP, flagged).

## Fairness gates (all pre-registered, all reported)
- G1 honest MFV/frequency-prior baseline under the FIXED scorer (composed win MUST beat MFV by MARGIN_OVER_MFV=0.03).
- G2 SHUFFLED-RELATION control: shuffle rel->value in training, re-run learner; held-out MUST collapse to <= MFV + 0.03. Survives => void.
- G3 apples-to-apples: GloVe zero-fit (forced-choice) + GloVe-learned (converged ridge) recomputed on the SAME items/split/freq-matched distractors. BGE-learned 0.228 is a CITED external bar.
- G4 no-leak + non-circular: held-out concepts NEVER in any training episode; target relation EXCLUDED from a concept's features.
- G5 ablation: relation-only vs CE-bridged-composition vs GloVe-learned vs CE-no-learner (nearest-train transfer). Attributes signal.
- G6 coverage honesty: report scorable held-out fraction; aggregate over ALL held-out (unscorable counted).
- G7 (NEW) randomized-gold-position + abstain=chance (fix A; self-test-enforced).

## Config (a priori; NOT tuned)
K_DISTRACT=5 (adaptive; chance reported ~0.18); HELDOUT_FRAC=0.20; MAX_COACTIVE_REL=4; CE_N_DIM=1024; CE_K_SPARSITY=0.02; CE_N_PROTOTYPES=48; CE_KMEANS_ITERS=12; FREQ_MATCH_BINS=4; SEEDS full=(20260725,13,101), smoke=(20260725,); INCLUDE_GAM=True; INCLUDE_PROGIND=False; KINDOF cap full=700 / smoke=200; 27 audited tables.

## Verdict bands (a priori; HARD-PASS / HARD-FAIL)
- HARD-PASS = EARNS-GENERALIZING-MEANING: composed held-out CI-lower > max(MFV, 0.228) AND (composed - MFV) >= 0.03 AND compression_ratio > 1 (chosen != KEEP_EPISODIC) AND shuffle collapses AND composed > GloVe-learned.
- HARD-FAIL = MEMORIZES-KEEP-EPISODIC (honest negative): chosen == KEEP_EPISODIC OR compression <= 1 OR composed held-out <= max(MFV, 0.228) OR shuffle survives. Pre-registered as a REAL finding (WorldTree PROP relations lack learnable fine-meaning generalizations at this density), NOT hidden.
- MIDDLE: real rule (compression > 1) that beats MFV+chance but does NOT clear the clear bar (max(MFV, BGE) / GloVe-learned).
- DATA_NOT_READY / INVALID: preflight fails / < MIN_HELDOUT_ITEMS=60 held-out fine items / frozen saturates >= 0.85.

## Design-gate at smoke (verified before full)
- REAL baseline: frozen-GloVe forced-choice 0.5881 + GloVe-learned 0.3836 (MEASURED@_smoke).
- can-fail: KEEP_EPISODIC / <= bar / shuffle-survives all pre-registered honest fails.
- discriminator fires: composed compression 1.18 > 1 (real rule, not KEEP_EPISODIC); arms differ; shuffle collapses to 0.14.
- baseline in-band: frozen-GloVe 0.588 (0.05 < x < 0.85).
- one variable: only the concept->value predictor changes; identical items/candidates/split.
- discriminator-survives-scale: smoke ran the FULL 27-table regime at 1 seed (verdict MIDDLE) -> full 3-seed verdict MIDDLE (consistent).

## MEASURED full results (MEASURED@data/exp_composed_differentiation_loop_v2/metrics.json)
- VERDICT = MIDDLE. run_mode=full, elapsed 194s, 11KB.
- composed held-out = 0.2396 (CI 0.216-0.262), compression_ratio = 1.1706, chosen plugin = gam (all 3 seeds) -> a GENUINE relation-level rule, NOT KEEP_EPISODIC.
- honest MFV = 0.2242 (v1 fake was 0.9665); chance = 0.1824.
- frozen-GloVe forced-choice = 0.5681 (the REAL bar; uncontaminated); GloVe-learned = 0.454; BGE bar = 0.228 (CITED).
- shuffle control = 0.1975 (collapses to ~chance -> control fires; not a spurious shortcut).
- ablations: relation-only 0.2077, CE-only 0.2380, CE-no-learner 0.3386.
- preflight PASS: frac_ge2 = 0.2398, multi_valid_rate = 0.0991, no relation below 0.70 floor; 513 held-out fine items; 48 CE prototypes/seed.

## Honest interpretation (VET-PENDING; skunkworks owns the landed VET)
Our composed native encoder + MDL learner induces a GENUINE, non-spurious relation-level rule (compression 1.17 > 1, shuffle-collapses, gam all seeds) that MODESTLY beats honest MFV/chance -- but it does NOT clear the clear bar and sits FAR below the borrowed frozen-GloVe forced-choice baseline (0.24 vs 0.57). Under the clean (bug-fixed) metric this is the pre-registered HONEST NEGATIVE on the EARNS question: on WorldTree PROP fine-meaning generalization at this density, borrowed-embedding similarity still beats our native composition. The wall restated, now on an uncontaminated measurement. NEXT: the flagged concept_encoder curriculum-dynamics gap (order-invariant batch accumulator) is the leading structural suspect; that is the next build, not this cell.

## Cell-template compliance
except SystemExit before except Exception (no BaseException/bare); tmp_replace atomic metrics; start-marker; crash-diagnostic; heartbeat (flush=True); deterministic (hashlib + fixed int seeds + numpy default_rng + sorted; no builtin-hash-seeded RNG, no list(set)); self-test exercises REAL parse + ConceptEncoder + CE-prototype bridge + learner.learn AND planted rule (generalizes) + planted CE-prototype rule (generalizes) + planted no-rule (KEEP_EPISODIC) + scorer-fairness (abstain~chance) + determinism; arms_differ; no-leak + non-circular asserted. Storage = no_composition (self-contained differentiation cell).
