# Pre-registration: cross-module interface HELD-OUT split -- construction vs predictive capability (2026-07-15, v2)

Author: hdi_exp_dev. Fixed BEFORE running. Cell: `experiments/exp_crossmodule_interface_hub_heldout_v2.py`
(ANCHOR `crossmodule_interface_hub_identity_bind_heldout_v2`). This is the v2 UPGRADE of the landed CHAIN_GRADE cell
`exp_crossmodule_interface_hub_identity_bind_costanzo_biogrid_v1.py` (commit 224666483, HUB=0.83 vs single_ceiling=0.254 on
598 queries). It carries over ALL of v1's validated machinery unchanged (HUB / MERGED / NO_HUB / SCRAMBLE / RANDOM /
PHYS_ONLY / GEN_ONLY arms; exact-ORF join; join_precision; edge_jaccard distinctness; the single-constraint-ceiling must-fail
null; real BioGRID + Costanzo parsers; REAL hdlab.binding bind/unbind; planted full-N discriminator preview) and adds ONE
thing: an airtight SEEN-vs-HELD-OUT query split that distinguishes CONSTRUCTION (recovers stored conjunctions) from
PREDICTIVE CAPABILITY (composes conjunctions for pairs never co-attested in any module).

## Why v1 could not be VET'd as predictive (the gap this closes)
v1's landed-VET could not determine from metrics whether the 598 queries were HELD-OUT or IN-SAMPLE. DIAGNOSIS (from the v1
source, this session): v1 is ALREADY-COMPOSITIONAL -- `M_P = sum bind(h(a),h(b))` over PHYSICAL edges and
`M_G = sum bind(h(a),h(b))` over GENETIC edges are superpositions of the INDIVIDUAL module edges ONLY; the gold conjunction
`A(X,Y) = phys_partners(X) INTERSECT gen_partners(Y)` is computed fresh at eval time and is NEVER stored as a unit. So the
conjunction is composed, not looked up. BUT v1 only ASSERTED this in prose ("held-out by construction") -- it never
stratified the queries or machine-checked non-leakage, so a landed-VET could not separate "recovers stored conjunctions"
from "predicts held-out conjunctions." v2 makes the distinction explicit, stratified, and machine-checked.

## The airtight held-out split (the v2 addition)
Store construction is IDENTICAL to v1 and IDENTICAL across strata -- ONLY the EVAL queries are stratified, so there is no
per-stratum store leakage. Each eval query (X,Y) is labelled by whether the pair is a DIRECT stored edge in EITHER module:
- NOVEL / HELD-OUT (primary stratum): (X,Y) is NOT a direct stored edge in phys OR gen. The pair was NEVER presented as
  related in ANY module, so the shared conjunction-neighbour z can ONLY be found by COMPOSING the two independently-stored
  module readouts (there is no pair-attestation to ride on). This is the genuine PREDICTIVE capability slice.
- SEEN (context stratum): (X,Y) IS a direct stored edge (the pair's relationship is directly attested in the data). Reported
  for context; NOT gated. Expected to be a minority (sparse networks; random (X,Y) query pairs rarely share a direct edge).
Machine-checked non-leakage: `novel_no_direct_edge` (every NOVEL pair has NO direct edge in either module) and
`conjunction_never_stored` (structural: stores hold only individual module edges) are asserted in BOTH run_measurement AND
the self-test (planted arena). A NOVEL query with a direct edge -> INCONCLUSIVE_SPLIT_LEAK (split-construction bug, not a
mechanism verdict).

Note on why the split is on PAIRS not EDGES: the mechanism can only recover a conjunction whose constituent edges (X,z) and
(Y,z) are stored (that is what unbind reads back) -- holding out a constituent edge makes z unretrievable and is a
link-prediction test the single-hop-per-module mechanism is not designed for. The honest held-out axis for a query-independent
zero-parameter associative store is the NOVELTY OF THE PAIR: a (X,Y) never co-attested, whose common cross-relation neighbour
is produced purely by intersecting two independent module readouts.

## Arms (unchanged from v1; MAP higher=better, now reported PER STRATUM)
HUB (mechanism) / MERGED (strong baseline, spoke-separation control) / NO_HUB (independent-codebook must-fail) / SCRAMBLE
(scrambled-identity must-fail) / RANDOM (chance floor) / PHYS_ONLY, GEN_ONLY (single-constraint reference ceilings). The
single-constraint ceiling = max(PHYS_ONLY, GEN_ONLY) is the honest must-fail null (gold is a SUBSET of each conjunct so any
arm retaining ONE intact module floats above chance by construction; on real scale-free data the ceiling also absorbs any
degree/frequency leakage into the null). All arm definitions, HP_SCOPE, and the option-b must-fail correction are carried
over verbatim from `preregs/2026-07-15_crossmodule_interface_hub_identity_bind.md`.

## PRE-REGISTERED BANDS (fixed BEFORE running; ALL gates evaluated on the NOVEL stratum for the primary verdict)
Shared gates (join/distinctness/integrity): join_precision >= 0.90 AND fuzzy_gain_frac <= 0.05 AND n_shared_orfs >= 60 AND
edge_jaccard(P,G) <= 0.50 AND arms differ AND determinism AND novel_no_direct_edge (non-leakage) AND n_novel >= 30.

- HARD_PASS_INTERFACE_HUB_HELDOUT_PREDICTIVE_COMPOSES_CROSS_MODULE (PRIMARY): shared gates AND, ON THE NOVEL STRATUM:
  HUB_MAP >= 0.30 AND HUB - max(MERGED,NO_HUB) >= 0.15 AND HUB >= 1.5*MERGED AND HUB - single_ceiling >= 0.15 AND must-fails
  fire (SCRAMBLE,NO_HUB <= single_ceiling+0.05 AND each >= 0.15 below HUB). => identity-anchored bind/unbind PREDICTS
  cross-module conjunctions for pairs it was never given as a unit AND never saw related -> CAPABILITY, not construction.
- HARD_FAIL_CONSTRUCTION_ONLY_NOT_PREDICTIVE_ON_HELDOUT: the ALL-query set passes the same gates but the NOVEL stratum does
  NOT -> the result is construction-scoped (recovers/composes on attested pairs) but does not PREDICT genuinely-held-out
  conjunctions. (This is the honest downgrade the v1 verdict could not rule out; v2 tests it directly.)
- HARD_FAIL_JOIN_LOSSY: join_precision < 0.90 OR fuzzy_gain_frac > 0.05 OR n_shared_orfs < 60 (exact ORF join lossy).
- HARD_FAIL_NO_COMPOSITION_HUB_DOES_NOT_BEAT_BASELINE: HUB does not beat the baseline/ceiling on NOVEL and does not pass ALL.
- INCONCLUSIVE_SPLIT_LEAK: a NOVEL query pair had a direct stored edge (split-construction bug).
- MIDDLE_BAND_LOW_POWER_NOVEL: n_novel < 30. MIDDLE_BAND_RELATIONS_NOT_DISTINCT: edge_jaccard > 0.50.
- INCONCLUSIVE_ARMS_IDENTICAL / INCONCLUSIVE_NONDETERMINISTIC / INCONCLUSIVE_MUSTFAIL_DID_NOT_FIRE: integrity failures.
- ACQUIRE_FAILED / ESCALATE_PARSE_NO_STRUCTURE: honest download/parse-failure diagnostics (not a mechanism refute).

## Expectation (HYPOTHESIZED, NOT a gate)
On real yeast data the vast majority of the ~598 v1 queries are expected to be NOVEL (sparse scale-free networks; random
(X,Y) query pairs rarely share a direct edge), so the NOVEL stratum should be well-powered and track v1's HUB=0.83 vs
single_ceiling=0.254. HYPOTHESIZED@this-prereg: HUB_novel ~ 0.8, single_ceiling_novel ~ 0.25 -> NOVEL passes -> PREDICTIVE.
If instead HUB collapses toward the ceiling ONLY on NOVEL while ALL passes -> HARD_FAIL_CONSTRUCTION_ONLY (informative
downgrade). Numbers are HYPOTHESIZED; the remote run MEASURES them.

## Compute architecture
(b) sequential-CPU with justification (unchanged from v1). VSA core batched over all queries as single torch complex64
matmuls (no python loop over query points); per-seed O(V*N) store-build + O(Q*V*N) cleanup, seconds at V<=400 / N=16384 /
Q<=800 (up to 400 per stratum) x 5 seeds. Dominant cost = BioGRID(178MB) + Costanzo(521MB) download + streaming parse
(CACHED on the remote from the v1 run -> cache-hit; v1 elapsed_s=73 with cache). device=cpu default (runner passes no argv).
Storage: BUNDLED-ASSOCIATIVE per module (the mechanism under test; single-hop-per-module unbind then an identity-anchored
intersection; NOT a depth>=2 chain -> the sharded-vs-bundled chain-grade physics law does not apply). Determinism: FIXED int
seeds; sorted(set()) vocab + deterministic stride PER STRATUM; np.random.default_rng / torch.Generator; NO builtin-hash
seeding; NO list-of-set dedupe (PROT-023 source scan = 0 findings, verified locally).

## SCHEMA-VET fields
- arms_differ_verified: true (self-test hashes HUB/MERGED/NO_HUB/SCRAMBLE score vectors on the planted arena; all 4 differ).
- final_metrics_atomicity: tmp_replace.
- crlb_n/a: retrieval MAP has no closed-form CRLB; the chance floor is the MEASURED RANDOM-arm MAP on the SAME variable-size
  answer sets; the planted full-N preview certifies the HUB-vs-ceiling gap survives scale ON THE NOVEL STRATUM.
- discriminator_reachability: true. Self-test (planted arena, n_v=120, full N=16384) MEASURED: NOVEL stratum n_novel=393,
  HUB=1.0, single_ceiling=0.332, MERGED=0.645, NO_HUB=0.170, SCRAMBLE=0.156 -> HUB - ceiling = 0.67 (>= PLANT_MARGIN 0.15),
  must-fails fire, non-leakage holds. MEASURED@self-test stdout this session.
- baseline_in_band: MERGED/NO_HUB measured (not saturated); planted arena built with DISTINCT relations so MERGED < HUB.
- cardinality_ok: EXPECTED_N_UNITS = n_seeds (5 full / 2 smoke); verdict averages per-seed per-stratum MAP; per_seed length
  == n_seeds; NOVEL stratum has >= MIN_NOVEL_QUERIES.
- calibration_check: adaptive_with_discriminator_gate (must-fail null = MEASURED single-constraint ceiling on EACH stratum;
  edge_jaccard distinctness = discriminator-still-fires check; self-test asserts HUB-beats-ceiling on NOVEL at full N first).
- except SystemExit: raise BEFORE except Exception (no BaseException); no bare except.
- real_code_path_exercised: [parse_biogrid_physical, parse_costanzo_genetic, hd_bind, hd_unbind, run_arms, build_queries,
  stratified_maps] (self-test builds synthetic BioGRID TAB3 + Costanzo zips through the REAL parsers, builds the split, runs
  the REAL VSA arms at full N, and asserts non-leakage on the planted arena).
- substrate_signature_checked: [hdlab.binding.bind, hdlab.binding.unbind] (bound against live inspect.signature in self-test).
- deterministic_seeding: true (FIXED int seeds; sorted(set()); deterministic per-stratum stride; np.random.default_rng /
  torch.Generator; NO builtin-hash seeding; NO list-of-set dedupe; PROT-023 source scan = 0 findings, verified locally).
- cell_chunked: false (single cell; the heavy cost is the shared download+parse, so per-seed chunking would re-download).
  start_marker_written: true. crash_diagnostic_present: true (CELL_CRASHED metrics + traceback). heartbeat_present:
  per-1M-row parse counter + per-seed done lines (flush=True). defensive_error_checking: passed (start marker + crash metrics
  + flush progress; acquire/parse failure classes are explicit verdicts).
- progress_logging: print_flush_true (timeout_s >= 1800).

## SELF-TEST GATE (this session, LOCAL, synthetic-data only, no downloads)
18/18 checks PASS. Both strata populated (seen=343, novel=393); non-leakage (novel_no_direct_edge=true,
seen_all_direct_edge=true); HUB beats ceiling on NOVEL at full N; must-fails fire on NOVEL; arms differ; determinism.
MEASURED@ self-test stdout 2026-07-15.

## Dispatch
Queue: remote_cpu_queue (CPU cell; download/parse-bound; no GPU). timeout_s = 5400 (headroom for a cold cache re-download;
with the v1 remote cache present, VSA compute is ~seconds and total ~1-2 min). exp_dev authored + static-verified
(py_compile OK, PROT-023 scan clean, --self-test 18/18) and hands the queue_add command to the orchestrator; the ORCHESTRATOR
ships remote (SCP/SSH) + owns post-ship REMOTE VERIFY.
