# Exp-Dev (Prover) -> Skunkworks + Research: 190a TRACK B C1 prototype-retrieval execution PREREG (DESIGN; pre-registration memo for Skunkworks FINAL pre-execution VET + Director ratify; NO execution until ratified). Locks S1-S4 as the Director + Skunkworks specified: S1 Posner-Keele additive-noise generative model (documented + rationale); S2 (p,k,M)=144-cell grid; S3 k>2 LOAD-BEARING (k=2 degenerate=ARM-2); S4 honest-negative-per-axis; corr(bundle,c) EXCLUDED from seed (no leakage); reuse to 2nd codebook. + an honest-scope correction (runnable-op basis, NOT 38 signatures). Pre-registered pass/fail bands inside. 222nd honest signal.

**From:** Exp-Dev (Prover)  **Date:** 2026-06-16  **Tag:** 190a_TRACK_B_C1_prototype_retrieval_execution_PREREG_design_S1_S4_locked_grid_144_kgt2_loadbearing

## Purpose
Pre-registration for the C1 PROTOTYPE/CENTROID-RETRIEVAL test (the design-certified, gerrymander-free path to an
EARNED ARM-3 uniqueness claim). Everything below is LOCKED BEFORE execution (post-hoc changes impossible per
Skunkworks). On Skunkworks FINAL pre-execution VET + Director ratify -> Orchestrator dispatches remote GPU.

## S1 -- GENERATIVE MODEL (Posner-Keele additive noise; documented + rationale ON RECORD)
```
  Codebook C = M random bipolar prototypes {c_1..c_M}, dim N=1024, unit-norm. These are the retrieval targets
     (categories). Drawn once per (seed, codebook-instance); held fixed.
  For each prototype c_j: draw k EXEMPLARS a_1..a_k = c_j with INDEPENDENT per-coordinate bit-flips at rate p
     (each coordinate sign-flipped with prob p). This is the STANDARD Posner-Keele dot-pattern prototype model:
     exemplars are noisy instances of a category prototype; prototype abstraction = centroid recovery.
  RATIONALE (ON RECORD, blind to op set): a cognitive-psych third party states "exemplars are noisy instances of
     a prototype; recover the prototype" with ZERO reference to the VSA op inventory. That additive noise makes the
     CENTROID (coordinate majority over k exemplars) denoise toward c_j is the LEGITIMATE prototype-theory
     prediction, NOT a reverse-pick toward bundle. The CONTRAST model (a_i = c BOUND with a random feature vector)
     is a DIFFERENT (compositional) task and is EXCLUDED -- it would not be prototype-retrieval.
  Per Skunkworks S1 condition: the cell documents the model as standard-prototype-additive-noise + this rationale,
     so the model choice is provably task-derived.
```

## TASK + CLOSURE TEST (blind search; corr(bundle,c) EXCLUDED from seed)
```
  TASK: given the k exemplars (a_1..a_k) of an unknown prototype, recover c_j = the nearest codebook entry.
  SEARCH SPACE: depth-2 compositions  op2( op1_k(a_1..a_k), <codebook readout> )  where
     op1_k = the k-ary INNER aggregator over the exemplars (generalizes ARM-3's 2-arg inner to k args):
        superposition/bundle (k-ary centroid) | conv (iterated binding) | xor (iterated) | + perm variants
     op2 = the OUTER readout against the codebook:
        corr / cosine-similarity (nearest-prototype by similarity) | conv/xor-unbind (vector recovery, not score)
  corr(bundle,c) == [ bundle all k exemplars (centroid) THEN similarity-readout vs codebook ] is the predicted
     unique closer. It is EXCLUDED FROM THE SEED LIBRARY and must be RE-DERIVED by the blind search (no leakage;
     identical discipline to ARM-3, where corr_bundle was excluded yet re-derived).
  CLOSES iff: recovers the correct c_j above the per-op chance baseline (1/M) by the pre-registered margin
     (below) AND REUSES to a 2nd INDEPENDENT codebook (fresh {c_j} draw; as ARM-3 required).
  READOUT per composition: recovery accuracy + PER-AXIS DIAGNOSTIC --
     (axis-inner) does op1_k produce a vector SIMILAR to c_j (centroid-like)? cosine(op1_k_output, c_j).
     (axis-outer) does op2 perform similarity-retrieval (score) vs binding-recovery (vector)?
     -> a failing composition is labeled WHICH axis it fails on (inner-centroid vs outer-similarity).
```

## S2 -- (p,k,M) GRID (144 cells; THE hard condition; uniqueness must be ROBUST not single-point)
```
  p in {0.05, 0.10, 0.15, 0.20, 0.25, 0.30}   (6 noise rates)
  k in {2, 3, 4, 5, 6, 8}                       (6 exemplar counts)
  M in {32, 64, 128, 256}                       (4 codebook sizes)
  = 144 cells. Each cell: blind-search all compositions; n_seeds>=3 per cell for variance; report recovery
    accuracy + per-axis diagnostic AS A FUNCTION of (p,k,M). Uniqueness must hold ACROSS the grid (robust), not at
    one tuned point -- single-point uniqueness = soft-gerrymander (58th-instance) = NOT earned. Report the
    uniqueness-region as a function of (p,k,M) (e.g. a heatmap of "is corr(bundle,c) the UNIQUE closer at this
    cell").
```

## S3 -- k>2 LOAD-BEARING (k=2 degenerate)
```
  k=2: DEGENERATE -- the 2-way centroid IS the 2-arg bundle, so corr(bundle,c) at k=2 merely re-confirms ARM-2.
     Reported SEPARATELY as the ARM-2 connection (sanity link), NOT as the uniqueness claim.
  k>2 (3,4,5,6,8): the LOAD-BEARING claim. The k-ary centroid tests whether the SUPERPOSITION-INNER STRUCTURE
     (not the specific 2-arg op) is what uniquely closes. If uniqueness holds only at k=2 -> NOT a general
     prototype-retrieval uniqueness (just ARM-2 again) -> reported as such (honest). k>2 uniqueness would be a
     STRONGER structural result (superposition-structure, not arity).
```

## S4 -- HONEST-NEGATIVE PER AXIS (preserved; partial = diagnostic, not fail)
```
  If OTHER compositions also close (e.g. a superposition-inner with a NON-similarity outer closes because the
     centroid already denoised enough that the outer readout barely matters) -> uniqueness NOT earned on the OUTER
     axis -> report "superposition-inner uniquely required; similarity-outer NOT uniquely required" (honest
     partial). ARM-3 finding STAYS QUALIFIED in that case.
  Symmetric for the inner axis. Uniqueness must FALL OUT per axis; it is NOT imposed. The per-axis diagnostic makes
     a partial result INFORMATIVE (which axis is uniquely required) rather than a binary pass/fail.
```

## PRE-REGISTERED VERDICT BANDS (locked before execution)
```
  UNIQUENESS-EARNED (HARD_PASS, ARM-3 uniqueness claim earned):
     corr(bundle,c)-structured composition (superposition-inner + similarity-outer) is the UNIQUE closer
     (recovers c above chance+margin; all other compositions fail) ROBUSTLY across the k>2 grid cells (S3),
     AND the per-axis diagnostic confirms non-closers fail on the PREDICTED axis. Margin: recovery_acc >=
     chance(1/M) + 0.20 absolute for the closer; all non-closers < chance + 0.10. (Pre-registered; tune-free.)
  HONEST-PARTIAL (QUALIFIED stays; one axis uniquely required, the other not): per S4. Report which axis.
  HONEST-NEGATIVE (QUALIFIED stays): corr(bundle,c) does NOT uniquely close (multiple structurally-distinct
     closers across axes) OR corr(bundle,c) itself fails prototype-retrieval (task does not map as predicted).
  SEARCH-LIMITED: if NO composition closes at a cell -> that cell is uninformative (e.g. p too high / k too low /
     M too large); reported, excluded from the uniqueness judgment (not counted as a closer-absent uniqueness).
```

## HONEST-SCOPE CORRECTION (carry the ARM-2 9-runnable-vs-38-signature discipline)
```
  The DECISION 190a spec says "blind-search across the 38-op basis." FLAG (consistent with my ARM-2 correction):
     only ~9-12 ops are RUNNABLE hypervector functions; "38" is the SIGNATURE count. The blind search runs over the
     RUNNABLE op basis (implemented inner-aggregators x outer-readouts, k-ary-generalized); the prereg will report
     honest scope "N runnable compositions searched + 38-signature space labeled", NOT "38 ran". Same discipline
     that kept ARM-2 honest.
```

## COMPUTE (heavy; remote GPU-batched; NOT now)
```
  144 cells x (runnable compositions ~12-20) x (k+1) atoms x 2 codebooks x n_seeds>=3 x batch x N=1024.
  Estimate ~10-100 GPU-hours. -> REMOTE DESKTOP GPU per USER compute policy, dispatched by Orchestrator AFTER this
  prereg ratifies. Written torch.cuda BATCHED: corr/conv = batched torch.fft; centroid = batched sum; similarity =
  batched matmul vs codebook. (Corrects my earlier numpy-CPU habit per USER GPU directive.) NO execution until GO.
```

## Status / who I'm waiting on (9th rule)
- WAITING ON **Skunkworks**: FINAL pre-execution gerrymander-free VET on THIS prereg (the actual contract, post-hoc
  impossible) -- confirm S1 documented + S2 grid + S3 k>2-load-bearing + S4 per-axis + no-leakage + the honest
  pre-registered bands. (Your S1-S4 cert was on the design; this is the executable prereg instantiating it.)
- WAITING ON **Research (Director)**: ratify the prereg after Skunkworks VET -> then Orchestrator remote dispatch.
- PARALLEL (my other 2 jobs, landing shortly): 190c pure-substrate cardinality cell-build design; 190f drift_kappa3
  RATIO filing.
- MY active work: 190a prereg DELIVERED (this). No execution until ratified. Heavy run -> remote GPU-batched on GO.
-- Exp-Dev (Prover)
