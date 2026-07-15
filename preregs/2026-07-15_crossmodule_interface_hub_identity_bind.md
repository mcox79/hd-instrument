# Pre-registration: cross-module interface -- hub-identity + spoke-relation bind/unbind traversal (2026-07-15)

Author: hdi_exp_dev. Fixed BEFORE running. Cross-module INTERFACE stress-test (foundation module #2 = BioGRID physical,
registered against the same canonical-ID hub as module #1 = Costanzo genetic). Cell:
`experiments/exp_crossmodule_interface_hub_identity_bind_costanzo_biogrid_v1.py`. All compute REMOTE; the network-independent
remote `--self-test` (synthetic-zip real parsers + a planted two-module arena at full N) is the gate.

## What this tests (and why it is INDEPENDENT of module #1's thesis verdict)
Module #1 asks whether symmetric bind READS the interaction MAGNITUDE (epsilon regression). This cell asks a DIFFERENT
question: can we register a SECOND real-data module against a shared canonical-ID HUB and compose a CROSS-MODULE conjunction
via IDENTITY-ANCHORED bind/unbind traversal (hub-identity + spoke-relation; brain-aligned ATL hub-and-spoke), beating a
no-hub / merged-embedding baseline? It uses only the EDGE STRUCTURE of both modules (which genes interact), NOT the Costanzo
epsilon magnitude -- so it is robust to module #1's epsilon-noise verdict.

## Prior-work check (substrate-KB concept-query gate, cosine>0.30)
`bash tools/substrate_query.sh "cross-module interface identity-anchored bind unbind hub-and-spoke canonical ID join
cross-module conjunction composition"` -> top hit cosine=0.3213 ("Cross-cycle composition", cortex ultrametric/edge-importance
prereg = consolidation cross-cycle, a DIFFERENT mechanism); #2 cosine=0.2793 (`crt_module_scaling_battery_v1` = CRT capacity
MULTIPLICATION across modules, not entity-identity federation of independently-built real-data modules). No prior cell tests
cross-module IDENTITY-ANCHORED bind/unbind over a shared canonical-ID hub joining two independently-built REAL-data modules.
This cell is GENUINELY NOVEL (not a rediscovery); the CRT battery is about capacity scaling, not identity-join composition.

## Two real modules (provenance/versioning per module-registry conventions)
- Module P (PHYSICAL) = BioGRID yeast TAB3, release 5.0.259 (scout-verified live). Per-organism S. cerevisiae member inside
  the Latest-Release all-organisms zip (`downloads.thebiogrid.org/BioGRID/Latest-Release/BIOGRID-ORGANISM-LATEST.tab3.zip`,
  ~178MB). Filter Experimental-System-Type == physical; entity columns 6/7 = "Systematic Name Interactor A/B" (SGD ORF ids).
- Module G (GENETIC) = Costanzo 2016 yeast SGA (`thecellmap.org/yeast/costanzo2016`). Significant genetic edges (|epsilon| >
  0.08 AND p < 0.05, pairwise; |epsilon|-only for the 35MB matrix fallback). Reuses the module-#1 canonical-ORF extraction.
- SHARED JOIN KEY = SGD systematic ORF name (e.g. YAL001C), used natively by BOTH files -> exact string-equality join, ZERO
  crosswalk service. Cell records `provenance.json` (both modules' url/bytes/ok, join_key, acquire_errors, filter).

## The cross-module query + mechanism (identity-anchored bind/unbind traversal)
Query "which gene Z PHYSICALLY interacts with X AND GENETICALLY interacts with Y?"; gold A(X,Y) = phys_partners(X) INTERSECT
gen_partners(Y), excluding X,Y. Each module is its OWN associative store built from SHARED hub codes h(.):
`M_P = sum bind(h(a),h(b))` over physical edges; `M_G = sum bind(h(a),h(b))` over genetic edges (REAL substrate
hdlab.binding.bind/unbind, complex64 FHRR). Traversal: `s_P(z) = <unbind(M_P,h(X)), h(z)>`, `s_G(z) = <unbind(M_G,h(Y)), h(z)>`;
conjunction = rank z by `s_P(z)*s_G(z)`. The join is exact BY CONSTRUCTION because h(z) is the SAME hub vector in both readouts.

## Arms (retrieval, MAP higher=better; HP_SCOPE below)
- HUB (mechanism, WINNER hypothesis): shared hub codes + SEPARATE relation-typed stores (spokes) + identity-anchored product.
- MERGED (STRONG baseline; isolates SPOKE-SEPARATION): SAME shared hub codes but ONE FLAT store (physical+genetic merged, no
  relation typing) -> relation smearing pollutes the conjunction. Still has shared identity -> a fair strong baseline.
- NO_HUB (isolates SHARED-IDENTITY; MUST-FAIL): separate relation-typed stores but module G built with an INDEPENDENT
  codebook -> no canonical-ID correspondence -> the genetic readout cannot be re-identified against the physical readout
  (learned alignment out-of-scope: independent random codes carry no signal to align on, per the interface drill Rank-3
  rejection). It RETAINS the intact PHYSICAL module, so its honest null is the single-constraint ceiling (below), NOT chance.
- SCRAMBLE (MUST-FAIL): HUB but module G edges stored under a scrambled identity permutation (identity anchor broken); like
  NO_HUB it retains the intact physical module, so its null is the single-constraint ceiling, NOT chance.
- PHYS_ONLY / GEN_ONLY (single-constraint reference ceilings): rank by ONE module's real readout alone. Because the gold
  A(X,Y) = phys(X) INTERSECT gen(Y) is a SUBSET of BOTH phys(X) and gen(Y), a single intact module already scores ABOVE the
  pure-random floor (a conjunction's answer set is a subset of each conjunct's neighbourhood). These MEASURE the irreducible
  "one intact module retained" residual = the honest null for NO_HUB/SCRAMBLE, and (on real scale-free data) also absorb any
  degree/frequency leakage into the null automatically.
- RANDOM (pure-chance floor): random candidate scores -> empirical MAP floor for the variable-size answer sets (reporting
  context only; it is NOT the must-fail null -- see the CORRECTION note below).
HP_SCOPE: HARD_PASS margin gates apply to HUB vs max(MERGED, NO_HUB, single_ceiling) ONLY; RANDOM is a reporting floor.

## CORRECTION (must-fail null re-specified after the first remote self-test 9/11)
The first self-test FAILED 2/11: NO_HUB=0.183 and SCRAMBLE=0.181 did NOT collapse to the RANDOM floor (0.056); they sat ~3.2x
above it. DIAGNOSIS (static, off the planted-arena numbers): this is NOT the hypothesized degree/frequency leakage -- the
planted arena is degree-uniform (no hub genes), yet the residual persists, so degree-matched candidates (the literal option-a)
would NOT remove it. The true mechanism is a CONJUNCTIVE-SUBSET property: gold is a SUBSET of BOTH phys(X) and gen(Y), so any
arm retaining ONE intact module (NO_HUB/SCRAMBLE keep the PHYSICAL module; only the GENETIC identity bridge is broken) floats
to the single-constraint ceiling by construction. The candidate-restriction form of option-a (rank only within phys(X)) WOULD
remove it, but it (i) changes the HUB/MERGED scoring metric -- disallowed (HUB/MERGED machinery held fixed) -- and (ii) raises
the chance floor to ~0.29 and compresses the HUB_MAP>=0.30 band below META_RULE_L. So option-a is not viable within scope.
FIX = option-b done rigorously: the identity-broken arms' honest null is the MEASURED single-constraint ceiling
max(PHYS_ONLY_MAP, GEN_ONLY_MAP), and the HONEST discriminator is HUB beating that ceiling (genuine conjunction gain from the
shared-identity bridge, ABOVE the residual-leakage level). This directly separates "hub identity does the work" from "residual
leakage floats every arm." Two new reference arms (PHYS_ONLY, GEN_ONLY) MEASURE the null; HUB/MERGED/join_precision/parsers
are unchanged.

## Held-out slice
The mechanism has ZERO learned parameters (no fitting): every cross-module query is HELD-OUT BY CONSTRUCTION (nothing is fit
on the queries; no threshold is calibrated on them). The reported MAP is over all qualifying (X,Y) pairs with nonempty gold,
capped at MAX_QUERIES=600 by deterministic stride. Stated explicitly rather than an artificial train/test split, because a
zero-parameter retrieval mechanism cannot overfit a held-out query.

## Primary reported field -- JOIN PRECISION (exact-ORF, NOT fuzzy)
- `join_precision` = fraction of BioGRID physical-edge endpoints whose systematic-name token is a well-formed canonical SGD
  ORF id (the join-key link precision; near-1.0 = clean deterministic exact join, NOT fuzzy string match).
- `fuzzy_gain_frac` = extra ORF-vocab matches a case/whitespace-normalizing fuzzy pass adds OVER exact string equality, as a
  fraction of the exact overlap. ~0 => the exact join is NOT lossy (a fuzzy layer buys nothing).
- `n_shared_orfs` = |BioGRID_orfs INTERSECT Costanzo_orfs| under exact string equality.

## PRE-REGISTERED BANDS (fixed BEFORE running)
- HARD_PASS_INTERFACE: JOIN clean (join_precision >= 0.90 AND fuzzy_gain_frac <= 0.05 AND n_shared_orfs >= 60) AND relations
  DISTINCT (edge_jaccard(P,G) <= 0.50) AND HUB above chance (HUB_MAP >= 0.30) AND HUB beats the STRONG baseline
  (HUB_MAP - max(MERGED_MAP,NO_HUB_MAP) >= 0.15 AND HUB_MAP >= 1.5*MERGED_MAP) AND HUB is a GENUINE conjunction
  (HUB_MAP - single_ceiling >= 0.15, single_ceiling = max(PHYS_ONLY_MAP,GEN_ONLY_MAP)) AND must-fails FIRE
  (SCRAMBLE_MAP <= single_ceiling+0.05 AND NO_HUB_MAP <= single_ceiling+0.05, AND each >= 0.15 below HUB_MAP) AND
  n_queries >= 30 AND arms differ AND determinism.
- HARD_FAIL_JOIN_LOSSY: join_precision < 0.90 OR fuzzy_gain_frac > 0.05 OR n_shared_orfs < 60 (exact ORF join lossy / needs a
  fuzzy layer -> the "canonical-ID dissolves the ~51% link problem" claim fails for this pair).
- HARD_FAIL_NO_COMPOSITION: join clean + relations distinct but HUB does NOT beat the baseline (identity-anchored composition
  does not retrieve the cross-module intersection better than merged/no-hub) -> the hub-and-spoke interface does not deliver.
- MIDDLE_BAND_RELATIONS_NOT_DISTINCT: edge_jaccard(P,G) > 0.50 (physical/genetic edges too coincident -> not a genuine
  cross-module test). MIDDLE_BAND / MIDDLE_BAND_LOW_POWER: partial / < 30 held-out queries.
- ACQUIRE_FAILED / ESCALATE_PARSE_NO_STRUCTURE: honest download/parse-failure diagnostics (not a mechanism refute).

## Compute architecture
(b) sequential-CPU with justification. VSA core (bind = complex64 elementwise multiply, unbind, cleanup matmul against a
[V,N] codebook) is BATCHED over all held-out queries as single torch complex64 matmuls (NO python loop over independent query
points). Per-seed cost O(V*N) store-build + O(Q*V*N) cleanup; seconds at V<=400/N=16384/Q<=600 x 5 seeds. Dominant cost =
the BioGRID(~178MB) + Costanzo(521MB pairwise / 35MB matrix) download + streaming parse (cached after first run). GPU yields
little over batched-CPU at this size; device=cpu default (runner passes no argv). Storage: BUNDLED-ASSOCIATIVE per module (each
store = a superposition of bound edges) -- this IS the mechanism under test (single-hop-per-module unbind then an
identity-anchored intersection; NOT a depth>=2 chain, so the sharded-vs-bundled chain-grade physics law does not apply);
capacity sized (MAX_EDGES_PER_MODULE=4000, DEG_CAP=30, N=16384) so HUB cleanup clears while MERGED/NO_HUB stay below ceilings.

## SCHEMA-VET fields
- arms_differ_verified: true (self-test hashes HUB/MERGED/NO_HUB/SCRAMBLE score vectors on the planted arena; all 4 differ).
- final_metrics_atomicity: tmp_replace.
- crlb_n/a: retrieval MAP has no closed-form CRLB; the chance floor is the MEASURED RANDOM-arm MAP on the SAME variable-size
  answer sets; the planted full-N preview certifies the HUB-vs-baseline gap survives scale.
- discriminator_reachability: true (planted arena full-N preview asserts HUB - MERGED >= 0.15, HUB - NO_HUB >= 0.15,
  HUB - single_ceiling >= 0.15, and NO_HUB/SCRAMBLE <= single_ceiling + 0.05 AND >= 0.15 below HUB).
- baseline_in_band: MERGED/NO_HUB measured (not saturated); planted arena built with DISTINCT relations so MERGED < HUB.
- cardinality_ok: EXPECTED_N_UNITS = n_seeds (5 full / 2 smoke); verdict averages per-seed MAP; per_seed length == n_seeds.
- calibration_check: adaptive_with_discriminator_gate (must-fail null = MEASURED single-constraint ceiling
  max(PHYS_ONLY,GEN_ONLY), NOT the pure-random floor -- gold is a subset of each conjunct so one intact module floats the
  identity-broken arms above chance by construction; on real scale-free data the ceiling also absorbs degree/frequency
  leakage into the null; edge_jaccard distinctness gate is the discriminator-still-fires verification; self-test asserts the
  single-constraint ceiling + HUB-vs-MERGED gap + HUB-beats-ceiling on a planted arena first).
- except SystemExit: raise BEFORE except Exception (no BaseException); no bare except.
- real_code_path_exercised: [parse_biogrid_physical, parse_costanzo_genetic, hd_bind, hd_unbind, run_arms] (self-test builds
  synthetic BioGRID TAB3 + Costanzo zips through the REAL parsers + runs the REAL VSA arms at full N).
- substrate_signature_checked: [hdlab.binding.bind, hdlab.binding.unbind] (bound against live inspect.signature in self-test).
- deterministic_seeding: true (FIXED int seeds; sorted(set()) vocab; deterministic stride; np.random.default_rng /
  torch.Generator; NO builtin-hash seeding; NO list-of-set dedupe; PROT-023 source scan = 0 findings, verified locally).
- cell_chunked: false (single cell; seeds vary the codebook draw within one run; the heavy cost is the shared download+parse,
  so per-seed chunking would re-download). start_marker_written: true. crash_diagnostic_present: true (CELL_CRASHED metrics +
  traceback). heartbeat_present: per-1M-row parse counter + per-seed done lines (flush=True). defensive_error_checking:
  passed (start marker + crash metrics + flush progress; acquire/parse failure classes are explicit verdicts).
- progress_logging: print_flush_true (timeout_s >= 1800).

## Dispatch
Queue: remote_cpu_queue (CPU cell; download/parse-bound; no GPU needed). timeout_s = 5400 (headroom for the 178MB + 521MB
downloads + streaming parse on a cold remote cache; VSA compute is seconds). exp_dev authors + static-verifies (py_compile +
import + PROT-023 scan = clean); the ORCHESTRATOR ships remote (SCP/SSH) + owns post-ship REMOTE VERIFY.
