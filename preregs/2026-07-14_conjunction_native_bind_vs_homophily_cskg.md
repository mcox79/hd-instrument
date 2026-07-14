# PRE-REG: conjunction_native_bind_vs_homophily_cskg_v1

Filed 2026-07-14. Cell: `experiments/exp_conjunction_native_bind_vs_homophily_cskg_v1.py`.
Author: exp_dev. Decisive conjunction-mechanism experiment (redesign after the single-relation held-out
approach was cleanly REFUTED).

## Question
Single-relation held-out prediction is HOMOPHILY-SOLVABLE, so structured codes TIE/LOSE to a frequency/homophily
null on real CSKG (MEASURED@data/exp_relational_inference_neighbor_vs_unbind_structured_cskg_memsmoke_v3/metrics.json:
gates.mrr.SN=0.1533 < HOM=0.1742). Does moving to a CONJUNCTION target (value depends on a COMBINATION of >=2
constraints, not any single one) dissociate the substrate's native compositional representation from frequency? I.e.
does the substrate NATIVE FHRR bind (matched to the composition) beat the strongest frequency/homophily null on NOVEL
compositional conjunctions, at REAL scale with REAL CSKG value distributions -- with must-fail controls proving the win
requires genuine compositional structure?

## Design (compute-proportionate; NOT the foundation build)
- Real CSKG vocabulary via `build_cskg_core_triples` supplies entity count + value diversity + REAL value-frequency
  skew. Two constituent relations A,B chosen by max DUAL-coverage; each dual-entity gets a deterministic (v_A, v_B).
- PLANTED conjunction target y(e) = h(coord_A(v_A), coord_B(v_B)); coord = deterministic seeded hash into Z_L.
- Mechanism arm = the substrate's ACTUAL FHRR bind `hdlab.binding.bind` on complex64 FPE phasor codes (a group
  homomorphism over Z_L: bind(code[a],code[b]) = code[(a+b) mod L]). NO SGD fit. CPU-only.
- Novel-vs-seen stratification: a query entity is NOVEL iff its (coord_A, coord_B) pair is unseen among TRAIN entities.

## Compositional-structure sweep (all paired on the same held-out entities)
- CLEAN: y = (coord_A + coord_B) mod L (FHRR bind = matched algebra)
- NOISY: CLEAN with prob (1-NOISE_P=0.65) else uniform-random class (label noise)
- ARBITRARY: y = Pi[coord_A, coord_B], Pi fixed random table (NON-compositional; MUST-FAIL)
- CLEAN_SHUFFLE: CLEAN labels freq-preservingly permuted across entities (MUST-FAIL; native-bind -> POP floor)

## Arms (top-1 acc + MRR over L classes)
NATIVE_BIND (headline), MEMORIZE (exact (a,b) lookup, novel->POP backoff), HOMOPHILY (conditional-match vote =
strongest freq/homophily null, subsumes P(y|a),P(y|b)), HOMOPHILY_JAC (Jaccard neighbor-vote over the entity's full
real value-set), POP (marginal floor), UNIFORM (1/L), ORACLE (rule-knower = info-ceiling).
FREQ_NULL = max(HOMOPHILY, HOMOPHILY_JAC, POP) per stratum. Decisive contrast: NATIVE_BIND vs FREQ_NULL on NOVEL.

## Fairness first-class
- Info-ceiling: ORACLE knows the planted rule (CLEAN/ARBITRARY ceiling=1.0; NOISY=irreducible-noise bound). Verdict
  never celebrates sub-ceiling (ceiling_ok gate: ORACLE >= NATIVE_BIND).
- Real null: FREQ_NULL is frequency/homophily, NOT entity-popularity. Steelmanned with two homophily variants.
- Novel-vs-seen stratification; decisive metric on NOVEL (generalization, not memorization).
- Must-fails: ARBITRARY (no compositional structure -> no lift) + SHUFFLE (structure broken -> collapse to POP).
- No leakage: novel entities' (coord_A,coord_B) pairs never in train; native-bind uses only fixed FPE codes (data-
  independent) + the planted target codebook; MEMORIZE/HOMOPHILY train-only.
- The genuinely-empirical unknown at scale: does REAL value-frequency skew let FREQ_NULL climb off chance on NOVEL?
  (native-bind CLEAN ~1.0 is by-construction the mechanism definition; FREQ_NULL's novel behavior on real skew is the
  measured result that gates the foundation build.)

## PRE-REGISTERED BANDS (NOVEL stratum, top-1 accuracy; chance = 1/L; NOT tuned on real data)

### HARD_PASS -> verdict NATIVE_BIND_COMPOSITION_BEATS_FREQUENCY_ON_CONJUNCTIONS (require ALL)
- P1 CLEAN     NATIVE_BIND >= 0.85
- P2 CLEAN     NATIVE_BIND - FREQ_NULL >= 0.50  (the dissociation)
- P3 CLEAN     FREQ_NULL <= 0.15               (null genuinely fails => conjunction homophily-UNSOLVABLE)
- P4 NOISY     NATIVE_BIND - FREQ_NULL >= 0.20 (robust under noise)
- P5 ARBITRARY NATIVE_BIND - FREQ_NULL <= 0.05 (must-fail fires)
- P6 SHUFFLE   NATIVE_BIND - POP <= 0.05       (must-fail fires)
plus ceiling_ok and NOT integrity_breached.

### HARD_FAIL -> verdict CONJUNCTION_REFRAME_REFUTED_NATIVE_BIND_TIES_FREQUENCY (ANY -- report STRAIGHT)
- F1 CLEAN     NATIVE_BIND - FREQ_NULL <= 0.05 (native-bind does NOT beat frequency even clean => reframe dead)
- F2 CLEAN     FREQ_NULL >= 0.40               (homophily SOLVES conjunctions => not homophily-unsolvable)
- F3 INTEGRITY ARBITRARY (NATIVE_BIND-FREQ_NULL) >= 0.20 OR SHUFFLE (NATIVE_BIND-POP) >= 0.20 => a must-fail did NOT
     fire => native-bind leaking/cheating => the CLEAN win is an ARTIFACT => verdict
     INVALID_MUSTFAIL_DID_NOT_FIRE_NATIVE_BIND_LEAKS (integrity guard dominates PASS).

### MIDDLE_BAND: anything else.

## What REFUTES "native-bind composition beats frequency on compositional conjunctions"
F1 (native-bind ties frequency on CLEAN novel) OR F2 (frequency solves conjunctions). Either is the most valuable
outcome and is reported straight, not rescued. F3 invalidates a spurious CLEAN "win".

## Discriminator-survives-scale (option A + B + C)
- (A) self-test runs the FULL regime machinery at synthetic scale and FIRES the discriminator + both must-fails
  (MEASURED@ --self-test 2026-07-14: CLEAN NATIVE_BIND=1.0 FREQ_NULL=0.021 diss=0.979; ARBITRARY gap=-0.021; SHUFFLE
  gap=0.0; homomorphism_ok=True; vp_ok=True; decisive_selftest_verdict=NATIVE_BIND_COMPOSITION_BEATS_FREQUENCY...).
- (B) THEORETICAL@ FPE cleanup: max off-diagonal cosine ~ sqrt(2 ln L / d); at d=1024,L=128 -> ~0.097 << 1.0 (true
  class) => native-bind CLEAN survives scale exactly.
- (C) MEMSMOKE on reduced real CSKG core (cskg_max_lines=600000, k_core=4, L=64, 1 seed) confirms on real data + that
  the chosen relations have adequate dual-coverage before FULL.

## Compute architecture
class (b) sequential-CPU, JUSTIFIED: NO SGD fit (mechanism is native algebra); one batched complex cleanup matmul per
regime + cheap dict/graph votes. Storage: no_storage / no_composition-chain. Route: remote_cpu_queue.

## Schema-vet fields
- cardinality_ok: EXPECTED_N_UNITS = n_seeds (each seed produces all 4 regimes x 7 arms + non-empty novel & seen).
- arms_differ_verified: >=5 distinct top-1 signatures per regime (CLEAN gate).
- final_metrics_atomicity: tmp_replace (write_metrics os.replace + atomic crash-metrics).
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except). Grep-verified.
- crlb_n/a: closed-form FPE cleanup bound stated (B) in lieu of a noise-floor CRLB (no SGD noise floor here).
- calibration_check: default_ok_for_this_regime (bands from mechanism construction + chance=1/L, not tuned on real).
- real_code_path (F.1): self-test calls hdlab.binding.bind on complex64 FPE codes (the FULL native-bind path).
- substrate_signature (F.2): hdlab.binding.bind bound against its live signature.
- guard_baseline_valid: n/a (no control-beats-baseline break-guard; the integrity guard F3 is a magnitude gate).
- progress_logging: print_flush_true (line-buffered stdout + per-seed/per-regime flush + heartbeat).
- run_mode verification: --run-mode/self-test/memsmoke(via HDLAB_EXP_NAME name)/full wired; default cpu device.

## Configs
- MEMSMOKE: n_dim=512, L=64, cskg_max_lines=600000, k_core=4, seeds=[7], min_query=100, min_novel=20.
- FULL:     n_dim=1024, L=128, cskg_max_lines=0, k_core=4, seeds=[7,13,17], min_query=200, min_novel=40.
