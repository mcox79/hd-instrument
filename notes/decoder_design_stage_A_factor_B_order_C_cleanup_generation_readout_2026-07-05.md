# Decoder design: substrate-native generation readout (Stage A factor / B order / C cleanup)

Date: 2026-07-05. Owner: Director (research). Type: ready-to-dispatch build spec for the #1 gap (GENERATION).
Status: DRAFT, gated on the factorization-envelope FULL verdict (re-dispatched canonical, remote_cpu_queue).
Do NOT dispatch the build until the envelope lands GO or MIDDLE_BAND; NO_GO forces the Stage-A redesign (see Branch logic).

## Why this exists
The substrate can encode (perception: GSBC_EXPAND2X), remember, and reason ~40%, but it CANNOT SPEAK:
"comprehension engine, no mouth, empty library." Per the build-path drill (a0c4d73d,
research_drill_glassbox_llm_capability_gaps_build_roadmap_2026-07-05.md), GENERATION is the #1 gap and its
brain-grounded mechanism is a resonator-factorization DECODER = the clean INVERSE of the just-built encoder,
faithful-BY-CONSTRUCTION (every emitted token traces to one unbind op on a specific bound structure).

This memo pre-specifies the decoder so the moment the envelope verdict lands, exp_dev can be dispatched with a
crisp design instead of designing from scratch. It is parameterized on the envelope's feasible region.

## Algebra split (grounded, do not confuse the two)
- PERCEPTION frontend = the concept encoder (GSBC_EXPAND2X graded sparse block code). Maps text -> concept HV.
- COMPOSITIONAL algebra = bipolar BSC (bind = elementwise product, superpose = sum), per wave14e/wave14b.
  Propositions are bound in bipolar-BSC. The DECODER factors bipolar-BSC-bound propositions.
- The factorization-envelope probe tests EXACTLY the decoder's Stage A (bipolar-BSC resonator at substrate N).
  So the envelope numbers ARE the Stage-A capacity ceiling (clean codebook = honest upper bound; real
  correlated fillers reduce it).

## Architecture: 3 stages, inverse of encode->reason
INPUT: a bound proposition HV p = sum_{d=1..D} prod_{f=1..F} codebook_f[idx[d][f]]  (bipolar BSC superposition).

### Stage A -- FACTOR (resonator network)  [the envelope measures this]
Recover the F-tuple of each of the D superposed terms via iterative unbind + cleanup + explaining-away peel-off.
High-energy compute lever (USER-allowed): RESTARTS parallel random inits (batched matmul) + iterate-to-fixed-point
+ real-valued exact peel-off between terms. Report single-shot (R=1) vs high-energy (R=RESTARTS) so the single-shot
cliff is not mistaken for a wall.
- Output: D role-filler tuples (unordered).
- Capacity ceiling = the envelope's GEN_svo points (F=2, V in {1024,4096}, D=3, N=8192). If a proposition exceeds
  the envelope's GO region, CHUNK it (factor a bounded sub-proposition, peel, recurse) -- hierarchical factorization.

### Stage B -- ORDER (positional / temporal binding)
Stage A returns tuples with NO surface order. Order must be CARRIED in the proposition, not invented at decode:
at ENCODE time, bind each slot's filler to a POSITION role vector (pos_1, pos_2, ...) i.e. a slot = bind(pos_k, filler).
Then a recovered tuple that includes the position factor sorts trivially by position -> ordered token sequence.
- Brain analog: theta-phase / positional role vectors impose serial order (Levelt formulation stage).
- Design decision (pre-reg it): position is a FACTOR in the bound term (F includes a position slot), NOT a separate
  post-hoc heuristic. This keeps faithfulness mechanical.

### Stage C -- CLEANUP (associative lexicon = the "mental lexicon")
Each recovered factor HV -> surface lexeme via cleanup memory (codebook argmax; already the resonator's decode step).
- KNOWN RISK, and the key cross-connection: under superposition load the cleanup lexicon IS the hub-superposition
  collision limit. The hub-rescue result (exp_deep_reasoning_hub_robustness_v1) is VET-CONFIRMED MM_STANDARD
  (Skunkworks, commit 5eb05b4e5): PROTECTED/INDEX binding -- which is E3 permutation-indexed binding roll(role,occ),
  a PRIOR HARD_PASS mechanism (2026-06-12 PP-398), here EXTENDED to real BGE concept hubs -- rescues high-degree
  recovery cross-seed 0.254 -> 0.712 (+0.458, 3-seed cv~0.02); iterative resonator does NOT (+0.04).
  CAVEAT (honest): it FULLY rescues deg5-7 (0.93-0.98) but only PARTIALLY rescues deg8plus (idx_bind 0.42-0.47, <0.5)
  -- bundle/superposition capacity is the residual limiter even after collisions are resolved.
  => Stage C SHOULD use protected/index binding for the cleanup lexicon (direct reuse; deg5-7 fully covered). The
  extreme-degree tail (deg8plus hubs) still collapses -- needs the bundle-capacity fix (OPEN; the MEMORY 5x-drill is
  investigating the superposition-capacity limit). So the decoder's lexicon is robust for typical fillers, with a
  known soft spot for the most-connected concepts; do not over-claim full hub-robustness.

## First decoder cell -- round-trip go/no-go (what exp_dev builds)
Round-trip: real held-out concept atoms -> S/V/O triples -> ENCODE each as a bound proposition (bipolar BSC, with
position factors per Stage B) -> DECODE (Stage A resonator + Stage B sort + Stage C cleanup) -> ordered surface token seq.
Compare recovered ordered token-id sequence vs truth.

Metrics (report all three co-equally; joint-gate, no single-axis false pass):
1. per-term recovery rate (Stage A alone; matches the envelope's metric -- sanity cross-check vs envelope).
2. exact-ordered-sequence match rate (Stages A+B+C end-to-end -- the real generation goal).
3. per-token cleanup accuracy (Stage C; where the hub limit bites).

Pre-registered bands (PARAMETERIZED on the envelope; set the exact numbers from the landed envelope GEN_svo values):
- HARD_PASS: exact-ordered-sequence match >= 0.70 on D=3 S/V/O at N=8192 high-energy AND per-term recovery within
  ~0.10 of the envelope ceiling (proves the decoder reaches the probed capacity, not below it).
- HARD_FAIL: exact-sequence match < 0.30 (decoder cannot round-trip even S/V/O -> Stage A or C is the wall).
- MIDDLE: 0.30-0.70 -> the chunking wrapper is required for propositions beyond the GO region; ship the chunked decoder.
- Clean-test discipline: real correlated concept fillers (NOT synthetic iid) for the deliverable number; the envelope's
  clean-iid codebook is the ceiling, this cell measures the real-encoder-correlated realized value.
- Controls: shuffled-proposition control (must collapse) so the discriminator fires; single-shot R=1 vs high-energy R=16.

## Branch logic on the envelope verdict (decisive)
- GO (GEN_svo_1k >= 0.90 at N=8192 high-energy): Stage A is capacious enough for S/V/O directly. Dispatch the first
  decoder cell as specified; expect HARD_PASS achievable; build the direct (non-chunked) decoder first.
- MIDDLE_BAND (partial envelope): Stage A works for small propositions, cliffs beyond. Dispatch the decoder WITH the
  chunking wrapper (hierarchical factorization) as the primary deliverable; the go/no-go is on the chunked round-trip.
- NO_GO (B_V64_hi < 0.50 -- even tiny vocab fails high-energy): the BIPOLAR-BSC resonator is not the Stage-A
  factorizer. Do NOT build the bipolar-BSC decoder. Redesign Stage A first. RANKED candidates (per the generation
  5x-drill, 2026-07-05):
  (i) [TOP] SPARSE-BLOCK-CODE resonator geometry (Hersche/Terzic 2025, ~10^5x lit-reported capacity gain) --
      matches our existing GSBC encoder geometry, so it is the geometrically-native factorizer, not a graft.
      Falsifiable pre-reg: >=10x V-headroom over bipolar-BSC OR HARD-FAIL if <2x improvement.
  (ii) resonator with the ACF redundancy lever (exp_wave14b_acf_resonator, ~50x cap lift for F=2).
  (iii) hierarchical/chunked factorization at every level.

- STRATEGIC FLAG (raised by the generation drill; resolve in synthesis): the envelope probes the BIPOLAR-BSC
  resonator (clean iid codebook), but the concept ENCODER is a sparse block code (GSBC). If propositions are bound
  in the sparse-block geometry rather than converted to bipolar BSC, the bipolar-BSC envelope UNDERSTATES achievable
  Stage-A capacity (the sparse-block resonator reportedly ~10^5x). So a bipolar-BSC MIDDLE/NO_GO is NOT the final
  word on generation -- the sparse-block resonator is the ready stronger test. OPEN DESIGN QUESTION for the
  synthesis: are propositions bound in bipolar-BSC (per wave14b/e committed algebra) or directly in the GSBC
  sparse-block code? That choice picks the resonator and may flip a pessimistic envelope verdict. Do NOT change the
  in-flight canonical bipolar-BSC envelope (it is the honest ceiling for THAT algebra); if it lands MIDDLE/NO_GO,
  immediately probe the sparse-block resonator before concluding generation is hard.

## Dispatch trigger (next action when the envelope lands)
1. Read data/exp_factorization_envelope_v1/metrics.json verdict + the GEN_svo_1k / GEN_svo_4k / B_V64 / cliff numbers.
2. Fill the pre-reg bands above with the landed envelope values (per-term target = envelope ceiling - 0.10).
3. GO/MIDDLE -> dispatch hdi_exp_dev with this memo as the design pointer (direct vs chunked per branch).
   NO_GO -> route a research drill for the Stage-A redesign; do NOT dispatch the decoder build.
4. Fold in the hub-rescue Stage-C mechanism IF the Skunkworks VET (in flight) certifies protected/index binding.

## Discipline notes (obey)
- Verify off-disk before claiming (I over-claimed 3x this arc). Lead the go/no-go with VET-surviving numbers.
- No-smoke: rate the decoder honestly GOOD/MEDIOCRE/BAD; deflate OUR claims, not the ambition. Resonator generation
  at scale is genuinely hard (capacity cliff is real) -- do not pre-celebrate.
- Brain = existence proof + high-energy compute allowed: a cliff that only binds at R=1/single-shot is a compute cost,
  not a wall -- throw restarts/iterations at it; only an unlimited-compute cliff is a real Stage-A wall.
- This is CONSTRUCTIVE build work, NOT a vs-LLM comparison (USER-locked reframe).
