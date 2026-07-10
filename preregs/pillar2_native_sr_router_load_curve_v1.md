# Pre-registration: pillar2_native_sr_router_load_curve_v1

Cell: `experiments/exp_pillar2_native_sr_router_load_curve_v1.py`
Anchor: `pillar2_native_sr_router_load_curve_v1`
Author: exp_dev (2026-07-10)
Spec: `notes/pillar2_native_router_build_spec_2026-07-10.md` + `notes/pillar2_native_router_geometric_design_2026-07-10.md`

## Claim under test (UNTESTED cross-literature inference -- MEASURE, do NOT tune toward a pass)
A native router built from the LOW-RANK normalized-SR / spectral basis (grid cells = leading eigenvectors of
M=(I-gamma T)^-1; here the top-k eigenvectors of S = D^-1/2 W D^-1/2) routes multi-hop bank lookups WITHOUT the
partition-label oracle, and its routing-accuracy-vs-load curve STAYS ABOVE the DENSE (superposition) router's collapse
curve at the same load M. "Low-rank avoids the sqrt(N/M) capacity cliff" is an UNTESTED inference (the SR track and the
Hopfield-capacity track never intersect in the literature). A clean HARD_FAIL (SR collapses at the same M as dense =
low-rank bought nothing) is itself a valuable internally-publishable result.

## Prior-work check (substrate-KB concept query, mandatory)
Query "native router multi-hop routing without partition oracle low-rank successor representation spectral basis load
collapse": top hits at cosine 0.31-0.37 are WordNet definitions (noise) + two `testbed_per_characteristic_phase_diagram_
audit_2026-06-26` chunks documenting the WALL ("Multi-hop partition-per-hop with ORACLE 0.95 at depth-5";
"Substrate-native routing-without-oracle is the open question"). No prior arc cell tests an SR/low-rank native router.
Verdict: NOVEL (the query surfaces the oracle-dependence wall, not a prior attempt at the fix).

## Task (real ingested KG; NOT synthetic partition-oracle chains)
Partition-routing as content-addressable BANK retrieval on a typed ConceptNet subgraph. Nodes are partitioned into P
coherent BANKS (fixed storage layout). A routing query is (source s, relation r); the answer is bank(t). This is the
real routing task: at traversal you hold a KNOWN edge (s,r) of the ingested KG and retrieve the next bank (recall of
stored routing associations, not link-prediction). Load M = number of stored routing associations (edges) swept while P
is held fixed (constant chance floor 1/P). Both the SR eigenbasis and the dense memory are built from ONLY the M stored
edges (fair). Banks are assigned by a balanced spherical-KMeans partition on random-projected propagated-adjacency
structural features -- structure-coherent, hub-robust, and a DIFFERENT algorithm from the SR eigendecomposition (so the
partition is SR-eigenbasis-INDEPENDENT; the SR arm must DISCOVER routable structure, it is not handed the labels).

## Arms (predict bank in {0..P-1}; scored vs true bank(t))
- ORACLE: returns bank(t) (the label channel). Current ceiling / must-fire; collapses under the oracle-leak shuffle.
- DENSE_SUPERPOSITION (dim D): associative memory, key(s,r)=norm(code[s].role[r]) -> onehot bank(t) over M edges;
  readback=(Qk@Kmat^T)@Vmat. Router SNR ~ sqrt(D/M): HIGH at M<D, COLLAPSES at M>>D. THE baseline curve to beat.
- SR_SPECTRAL (rank k): X=top-k eigvecs of S (top constant mode DROPPED = anti-oversmoothing). TEM-style per-relation
  LINEAR transition map A_r [k,k] (closed-form ridge) mapping X[s] -> target-bank centroid; predict argmin_p
  ||X[s]@A_r - centroid_p||. Parameter count n_rels*k^2 FIXED (independent of M) = the concrete embodiment of "low-rank
  avoids the sqrt(N/M) cliff". THE candidate.
- DEGREE_POPULARITY: predict the globally most-populous bank (pure popularity, no geometry).
- RANDOM: uniform random bank (chance 1/P).
- (diagnostic) SR_LEAKY: SR biased by the target-bank hint -> DOES collapse under shuffle (demonstrates on real data
  the shuffle bites a leak while true SR is invariant). Reported, not a primary arm.

## Bands (numeric, pre-registered BEFORE the FULL run)
chance = 1/P (FULL P=20 -> 0.05). M_lo, M_hi = smallest / largest M in the grid. All arm values are seed-means at M_hi.
Separation bands are DIFFERENCES (chance-independent); the SR LEVEL band is CEILING-RELATIVE (never an absolute bar
above the info-ceiling -- the reader-multihop lesson).

HARD_PASS_NATIVE_SR_ROUTER_SURVIVES_LOAD (ALL must hold):
- sep_ok:     SR(M_hi) - DENSE(M_hi) >= 0.20  (curve separation at high load)
- degree_ok:  SR(M_hi) - DEGREE(M_hi) >= 0.15  (routing, not popularity)
- ceil_ok:    SR(M_hi) >= 0.70 * bayes_ceiling(M_hi)  (achieved/ceiling high; ceiling-relative)
- flat_ok:    |SR_HIGH - SR_LOW| <= 0.12  (degree-invariant across target-degree strata)
- sr_self_ok: SR(M_hi) >= SR_peak - 0.15  (SR itself not collapsing across load)
- shuffle_ok: |SR_intact - SR_shuffle| <= 0.05 AND ORACLE collapses under shuffle (<= chance + 0.15) (oracle-free)
- rank_ok:    SR embedding effective rank > 3.0  (no degeneration to the constant mode)

HARD_FAIL (any):
- SR_DEGENERATE_COLLAPSE: SR effective rank <= 3.0
- ORACLE_LEAK_SR_DIES_UNDER_SHUFFLE: |SR_intact - SR_shuffle| > 0.15 (it was leaking the oracle)
- SR_COLLAPSES_LIKE_DENSE_LOWRANK_BOUGHT_NOTHING: SR(M_hi) - DENSE(M_hi) < 0.05 (the key negative result)
- POPULARITY_SHORTCUT_SR_TIES_DEGREE: SR(M_hi) - DEGREE(M_hi) < 0.05
- DEGREE_DEPENDENT_SR_CONCENTRATES: |SR_HIGH - SR_LOW| >= 0.20 (rides degree)

MIDDLE_BAND_PARTIAL_ROUTING_AMBIGUOUS = otherwise (beats degree + survives shuffle but separation / flatness / ceiling
ambiguous).

Precondition gates (else INCONCLUSIVE, do NOT interpret arms):
- enough probes (>= 40 per M); RANDOM <= chance + 0.05 (anti-triviality); ORACLE >= chance + 0.30 (must-fire);
- routable: bayes_ceiling(M_hi) - DEGREE(M_hi) >= 0.10  (there IS (s,r)-conditional routing signal beyond popularity);
- dense_collapses: DENSE(M_lo) >= 0.55 AND DENSE(M_lo) - DENSE(M_hi) >= 0.35  (DENSE is in the loaded/collapsing regime;
  relative-drop criterion = the saturation-vacuous guard: a non-collapsing DENSE makes the separation test vacuous).

## Fair-test controls (from the spec)
1. LOAD SWEEP curve separation (not a single-M number); info-CEILING = Bayes (s,r)->bank predictor on stored group stats
   (same-relation-sibling branching); score achieved/ceiling.
2. ORACLE-LEAK SHUFFLE (killer control): shuffle the target-bank hint channel at query time. Native SR ignores it
   (delta ~ 0); ORACLE collapses (shuffle bites, non-vacuous); SR_LEAKY diagnostic collapses (leak IS caught).
   HARD_FAIL if SR dies under shuffle.
3. DEGREE control: beat DEGREE_POPULARITY AND degree-invariant (LOW/MID/HIGH target-degree strata).
4. RECALIBRATION-necessity: DEFERRED to v2 (multi-hop drift + external-referent recalibration). v1 is the single-hop
   LOAD-CAPACITY test isolating the core untested inference. Documented, not gated.
5. REAL ingested KG (typed ConceptNet subgraph).
6. COLLAPSE discriminator: SR embedding effective-rank floor.

## SCHEMA-VET fields
- arms_differ_verified: true (self-test asserts >= 4 distinct bank-prediction signatures among the 5 primary arms).
- final_metrics_atomicity: tmp_replace (via `_seed_checkpoint.write_metrics` + os.replace; write_partial per seed).
- except-ordering: `except SystemExit: raise` before `except Exception` (no BaseException / no bare except -- grep-clean).
- crlb / discriminator_reachability: chance = 1/P THEORETICAL; separation bands are differences (chance-independent),
  SR level band ceiling-relative; self-test planted-separable world demonstrates SR >> DENSE at high load. OK.
- baseline_in_band: RANDOM ~ chance (anti-triviality gate); ORACLE ~ 1.0 (must-fire); DENSE collapses (relative-drop
  gate) -- the saturation-vacuous guard.
- discriminator-survives-scale: D/P/k/M-grid are load knobs; the survival discriminator (SR-DENSE separation + dense-
  collapse + SR-flat-across-load) fires in the planted self-test; the real-KG survival is the open FULL measurement.
- HP strictly-above-floor: separation margins (0.20 / 0.15) >> tie eps (0.05).
- HP_SCOPE: {SR_SPECTRAL: [sep, degree, ceil, flat, sr_self, shuffle, rank]; ORACLE: [must-fire, shuffle-bites];
  RANDOM: [null]; DENSE_SUPERPOSITION: [collapse-baseline]; SR_LEAKY: [leak-catch demonstrator]}.
- cardinality_ok: true. EXPECTED_N_UNITS = n_seeds; each seed asserts ALL M-grid points ran (CARDINALITY guard); a
  subgraph with fewer edges than M_hi aborts INCONCLUSIVE_TOO_FEW_EDGES_FOR_M_GRID.
- per-unit failure-class instrumentation: per-arm and per-(seed,M) try/except records failure_class (no silent continue).
- calibration_check: default_ok_for_this_regime. P fixed; partition data-driven (balanced KMeans, NOT tuned for PASS);
  degree strata = DATA-driven target-degree tertiles; D/k/M-grid/ridge-lam pre-registered before the run.
- effective_vs_nominal_parameter_audit (Gate A): swept param = M (stored associations); the SR eigenbasis + dense
  memory + partition-membership counts all scale with the SAME M (both arms see the M-edge subgraph). ALIGNED.
- bracket_includes_discriminating_band (Gate B): smoke (measured) SR curve 0.36/0.12/0.42/0.50 and DENSE 0.93/0.63/0.45/
  0.37 both traverse the discriminating band [0.10,0.70]; DENSE crosses HIGH->LOW; discriminating_fraction well > 0.30.
- signal_shape_compatibility_audit (Gate C): X[s] [k] --A_r [k,k]--> centroid [k]: SHAPE_MATCH (linear map in the low-
  rank basis). Dense key(s,r) [D] --W--> bankcode [P]: SHAPE_MATCH.
- positive_control (Gate D): ORACLE reproduces the ~1.0 partition-routed ceiling (chain-grade oracle result); DENSE
  reproduces the documented sqrt(N/M) collapse (HIGH unloaded -> collapsed at high load). Both AT the test regime.
- functional_requirements: (a) address the correct bank from (s,r) without the label oracle -> SR spectral router;
  (b) resist capacity crosstalk under load -> low-rank fixed-parameter readout; (c) not shortcut on popularity ->
  degree control + strata; (d) not leak the oracle -> shuffle control.
- defensive_error_checking: passed_all_4_patterns (start_marker + crash_diagnostic + per-seed write_partial + flush
  logging). heartbeat: not used (each seed logs per-(seed,M) flush lines; FULL wall < ~15 min; progress_logging =
  print_flush_true covers diagnosability). start_marker_written: true. crash_diagnostic_present: true.
- cell_chunked: false (single-cell multi-seed; each seed writes a write_partial checkpoint; runner-death loses at most
  in-progress seed; FULL wall is short enough that chunking is not warranted).
- progress_logging: print_flush_true (line-buffered stdout + per-(seed,M)/per-arm flush prints).
- all numbers in this pre-reg are HYPOTHESIZED@this-prereg (bands, picked before FULL) or MEASURED@data/exp_pillar2_
  native_sr_router_load_curve_v1_smoke/metrics.json (the smoke curve quoted in Gate B).

## Compute architecture
class: (a) batched-GPU (eigh forced to CPU-float64 for numerical robustness on ill-conditioned normalized adjacency;
dense readback + structural-partition matmuls on device). Storage: SHARDED (each node its own spectral code / dense
key). Routes to overnight_queue (GPU) for FULL; local = smoke/self-test only (USER-locked).

## Smoke result (local CPU, MEASURED)
`data/exp_pillar2_native_sr_router_load_curve_v1_smoke/metrics.json` (12.6KB, run_mode=smoke):
VERDICT = MIDDLE_BAND_PARTIAL_ROUTING_AMBIGUOUS (conclusive, non-vacuous). All preconditions pass; DENSE collapses
0.930->0.370; SR rises with load 0.36->0.50 (opposite of DENSE); SHUFFLE bites (ORACLE 1.0->0.071, SR delta 0.000);
SR beats DEGREE (+0.281). Not HARD_PASS at smoke scale (sep 0.125<0.20, SR/ceil 0.62<0.70, flat 0.186>0.12) -- an
honest un-tuned partial. FULL (n=2800, P=20, k=32, M up to 4096, seeds 7/13/17) is the real measurement.

## FULL profile
seeds=[7,13,17], n_nodes=2800, P=20, D=384, k=32, m_grid=[256,512,1024,2048,4096]. Route overnight_queue (GPU).
