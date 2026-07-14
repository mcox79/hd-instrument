# Pre-registration: graph_spectral_compose_sr_ppmi_nystrom_v1

Date: 2026-07-13. Author: exp_dev. Anchor: `graph_spectral_compose_sr_ppmi_nystrom_v1`.
Cell: `experiments/exp_graph_spectral_compose_sr_ppmi_nystrom_v1.py`.
Queue: remote_cpu_queue (device=cpu; zero SGD; closed-form randomized SVD + one-shot Hebbian). Seeds [7,13,17].
Timeout: 5400 s.

## Question

Envelope-push on the VET'd graph-spectral inductive-compose NEAR-MISS
(`data/exp_graph_spectral_entity_codes_cskg_v1/metrics.json`, GRAPH_STRUCTURE_LIFTS_PARTIAL_MIDDLE:
LAP_COMPOSE=0.009852 vs RAND_COMPOSE=0.003957, lift 0.0059, needed >=0.010; scramble-verified real, margin 0.0092).
The parent only ever composed the TRANSDUCTIVELY WORST codebook (LAP: oracle 0.0107) inductively, with a FLAT
unweighted neighbor-mean. The two BEST transductive codebooks were never composed inductively
(PPMI_ORACLE=0.118939 = 11x LAP; SR_ORACLE=0.050790 = 5x LAP), and the flat mean is the aggregation NEITHER brain
theory (Dayan 1993 SR Bellman recursion: new state = own edges + TRANSITION-WEIGHTED neighbor rows) NOR graph
theory (Nystrom / APPNP OOS extension: EDGE-SIMILARITY-WEIGHTED, hub-downweighted) recommends. This cell varies the
one axis never varied -- CODEBOOK (PPMI/SR vs LAP) x AGGREGATION (flat unweighted mean vs symmetric-degree-weighted
mean) -- reusing the shipped harness verbatim on the SAME leak-free held-out-ENTITY CSKG-core arena.

Prior-work check (substrate-KB concept-query, cosine>0.30): top hit `GNN+VSA hybrid` cross-domain drill note
(cosine=0.3574) -- conceptually adjacent (inductive entity representation from neighborhood topology) but it
describes a LEARNED GNN aggregator (disqualified per the standing VSA-native/no-learned-net discipline). This cell
is genuinely distinct: CLOSED-FORM glass-box spectral codebooks (LAP/PPMI/SR) with a closed-form degree-weighted
aggregation, no learned net. Not a rediscovery -- it is the closed-form counterpart the GNN note's mechanism class
is explicitly barred from being. Directly continues the parent arc (same harness, same arena) with the one untested
codebook x aggregation cross.

## Aggregation -- what "better" means, and what was REJECTED at author time (honest apparatus note)

The literature-correct closed form for spectral OOS composition is the Nystrom extension
`phi_k(x) ~= (1/lambda_k) sum_i w(x,x_i) phi_k(x_i)` (Bengio 2004; Levin et al. arXiv:1802.06307). The literal
`1/lambda_k` eigenvalue-INVERSION term was IMPLEMENTED and EMPIRICALLY REJECTED before ship: on the degree-
homogeneous planted-SBM positive-control arena it amplifies the partial-neighborhood reconstruction error in the
low-eigenvalue (noise) dims and drives the mechanism arm BELOW chance
(MEASURED@author self-test: LAP_COMPOSE with 1/lambda = 0.042 < RAND_NULL = 0.10) -- a BROKEN discriminator, not a
lift. The robust core that both routes (Nystrom edge-similarity weighting, APPNP PageRank propagation, SR
transition weighting) share is the EDGE/DEGREE weighting: down-weight promiscuous high-degree hub neighbors that
connect to everything and carry little entity-specific signal. This cell's "NYS" aggregation therefore realizes the
frame-safe robust component -- a symmetric-normalized `w(t,h) = 1/sqrt(deg_train(h))` degree-weighted neighbor
mean, computed in the SAME scaled spectral-embedding frame as the FLAT arm. FLAT vs NYS is thus a PURE aggregation
contrast (identical codebook + frame, only the neighbor weight differs). On a degree-HOMOGENEOUS graph NYS==FLAT by
construction; the contrast appears only under the CSKG graph's MEASURED degree heterogeneity (Gini=0.5368).

## Reference bars (MEASURED, on-disk)

- Parent flat-LAP compose = 0.009852; parent RAND_COMPOSE = 0.003957; parent scramble margin = 0.009171
  MEASURED@data/exp_graph_spectral_entity_codes_cskg_v1/metrics.json:gates.{compose_mrr,compose_scr_margin}.
- Transductive oracle ceilings RAND=0.023083 LAP=0.010685 PPMI=0.118939 SR=0.050790 (same file).
- Additive (SGD TransE) realized compose = 0.128210 (stretch ceiling)
  MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ANCHOR_COMPOSE.

## Design (matched d=1024; CSKG core k_core=12, N~25.7k, frac=0.15, support_frac=0.5, seeds [7,13,17]; split COPIED
VERBATIM / bit-identical to the parent + native + additive arenas)

Codes (closed-form, glass-box, degree-corrected; randomized SVD rank d, n_iter=3, oversample 24; parent's exact
`lap_codes`/`ppmi_codes`/`sr_codes` reused): scaled spectral embedding E = row_norm(U * sqrt(s)), shared by FLAT and
NYS arms for each family.

ORACLE (transductive ceiling + positive controls; reused verbatim from parent):
- RAND_ORACLE (reproduce native ~0.023 + random-code bar), LAP_ORACLE, PPMI_ORACLE, SR_ORACLE.

COMPOSE (inductive; train-only W over train codes; held-out row = aggregate of its SUPPORT-neighbor (head) TRAIN
codes; native recall + score vs the patched codebook):
- FLAT (uniform index_add neighbor-mean; parent aggregation verbatim):
  RAND_COMPOSE (flat random bar), LAP_COMPOSE_FLAT (anchor, reproduce ~0.0099), PPMI_COMPOSE_FLAT, SR_COMPOSE_FLAT.
- NYS (symmetric-degree-weighted mean; SAME scaled codebook + frame; only w(t,h)=1/sqrt(deg_train(h)) differs):
  RAND_COMPOSE_NYS (degree-weighted random bar), LAP_COMPOSE_NYS, SR_COMPOSE_NYS.
- SCRAMBLE must-fail (aggregate over RANDOM entities, not true neighbors):
  PPMI_COMPOSE_FLAT_SCRAMBLE, SR_COMPOSE_FLAT_SCRAMBLE, LAP_COMPOSE_NYS_SCRAMBLE, SR_COMPOSE_NYS_SCRAMBLE.
Controls: RAND_NULL (chance floor); BASELINE_POP (freq baseline / BROKEN guard).

## Leak-free (the crux; the parent's confound-controlled compose kept clean, NOT regressed)

COMPOSE codes are built on the TRAIN-ONLY adjacency A_train (train_int; fold_in=None). Held-out entities have ZERO
train edges. A held-out entity t's code = (flat or degree-weighted) aggregate of its SUPPORT-neighbor heads' TRAIN
codes. Support edges build t's code only, never scored; QUERY edges scored only, never used to build any code. A
per-run `leak_audit` asserts (1) |query INTERSECT support| == 0, (2) every scored held-out tail has train-degree 0,
(3) the compose store W is ingested from train_int ONLY (n_ingested == n_train). Any breach -> INCONCLUSIVE.
Self-test MEASURED leak_audit: query_support_overlap=0, scored_tail_train_degree=0, ingest_equals_train=True.

## Bands (PRE-REGISTERED before the run; each aggregation gets its OWN matched in-run random bar)

A creditable arm X in {PPMI_COMPOSE_FLAT, SR_COMPOSE_FLAT, LAP_COMPOSE_NYS, SR_COMPOSE_NYS} is CREDITED iff:
(i) compose_lift(X) = MRR(X) - MRR(matched random bar) >= LIFT_MARGIN(0.010) [flat->RAND_COMPOSE; nys->RAND_COMPOSE_NYS];
(ii) scramble_margin(X) = MRR(X) - MRR(X_SCRAMBLE) >= COMPOSE_SCRAMBLE_MARGIN(0.005);
(iii) MRR(X) > MRR(LAP_COMPOSE_FLAT) (strictly beats the failed flat-LAP baseline ~0.0099; contract clause c).

- SCAFFOLD_BIND_TRANSFERS : pos-controls hold AND oracle fires AND >=1 creditable arm passes (i)+(ii)+(iii).
- SCAFFOLD_BIND_DOESNT : pos-controls hold AND oracle fires AND NO creditable arm clears LIFT_MARGIN AND none
  improves its scramble margin beyond the parent's 0.009171 -> clean stronger negative than the parent MIDDLE_BAND:
  closes the topology-only compose lens across BOTH new codebooks AND the hub-downweighted aggregation -> redirect
  to the relation-typed additive/reciprocal-edge program (already the dominant lever).
- SCAFFOLD_BIND_MIDDLE_BAND : some creditable arm lands lift in (0.005, 0.010] -> real-but-minor, close as such.
- INCONCLUSIVE : pos-controls/oracle fail, leak_audit breach, too few held-out queries, or POP beats RAND_NULL.
- ISOLATION readout (logged regardless): winner_axis = CODEBOOK (a *_FLAT beats LAP_COMPOSE_FLAT) vs AGGREGATION
  (LAP_COMPOSE_NYS beats LAP_COMPOSE_FLAT) vs INTERACTION (SR_COMPOSE_NYS is the top arm) -- this is the fairness +
  weak-point-localization axis: it tells us WHETHER the parent near-miss was a codebook limitation, an aggregation
  limitation, both, or neither.

## SCHEMA-VET fields

- cardinality_ok: EXPECTED_N_UNITS = 3 (seeds); each seed asserted all-arms + >=8 distinct sigs + finite W + leak-ok.
- arms_differ_verified: yes (17 arms; >=8 sigs/seed asserted; self-test MEASURED 17 distinct).
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace).
- except-ordering: SystemExit/KeyboardInterrupt re-raised BEFORE except Exception; no bare except / no BaseException
  (grep gate CLEAN).
- crlb_n/a: no closed-form noise floor; bands are MEASURED in-run matched-aggregation RANDOM bars (each aggregation
  has its own random bar) + CITED additive-compose 0.1282 -> discriminator_reachability OK by construction.
- baseline_in_band: RAND_ORACLE reproduces native ~0.023 (>> RAND_NULL ~1/N) = the ORACLE-FIRES gate; the
  0.05<baseline heuristic is calibrated for accuracy metrics NOT filtered-MRR-over-25k (calibration_check).
- discriminator_survives_scale: option B analytical -- the FLAT-vs-NYS gap is a DEGREE-HETEROGENEITY effect
  (Gini=0.5368 MEASURED on this graph); the homogeneous planted-SBM self-test cannot show it by construction, so
  the self-test instead fires (a) LAP-recovers-planted (b) embedding-separates-blocks (c) BOTH flat AND
  degree-weighted compose-scramble collapse. The literal 1/lambda Nystrom term was rejected precisely because it
  did NOT survive the positive-control (collapsed below chance) -- shipping the robust degree-weighting instead.
- calibration_check: default_ok_for_this_regime (all dims/ranks/fracs/tols/gammas pre-registered, NOT tuned on real
  data; arena config copied verbatim from the parent VET'd arena).
- HP_SCOPE: the credit gates apply to {PPMI_COMPOSE_FLAT, SR_COMPOSE_FLAT, LAP_COMPOSE_NYS, SR_COMPOSE_NYS} only.
  RAND_COMPOSE / RAND_COMPOSE_NYS = matched random bars; *_SCRAMBLE = must-fail; RAND_NULL = chance; POP = BROKEN.
- real_code_path (F.1): self-test builds the REAL KGStore, injects a scaled spectral codebook, runs ingest_triples
  + BOTH the flat and degree-weighted OOS compose (exercised: build_adjacency, lap_codes, KGStore,
  build_store_with_codes, ingest_triples, native_query_recall, compose_score, compose_score_wdeg).
- substrate_signature (F.2/F.3): KGStore bound against the live signature with BASE/portable kwargs only
  (n_ent,n_rel,n_dim,generator); no optional init_entities.
- guard_baseline_valid (F.4): BROKEN(POP>RAND_NULL) guard validated vs the RAND_NULL/arm floor (RAND_ORACLE above floor).
- defensive_error_checking: start-marker + crash-diagnostic (CELL_CRASHED + traceback) + per-seed heartbeat + per-seed
  failure_class; cell_chunked=false (sweep-free 3-seed loop; single cell).
- progress_logging: print_flush_true (line_buffered stdout + per-seed/per-arm flush prints + heartbeat; timeout>=1800).

## Compute architecture

class (b) sequential-CPU, justified. Same profile as the parent (closed-form randomized-SVD of a ~25.7k-node /
~474k-edge SPARSE operator; NO SGD/epochs/learned aggregator; one-shot Hebbian store). FLAT and NYS reuse the SAME
scaled codebooks. All CPU -> remote_cpu_queue (device=cpu). No GPU. No persisted-store mutation. Parent ran
610s/3seeds; this adds ~1x the compose stores -> timeout 5400 s (wide margin).

## HYPOTHESIZED vs MEASURED

- Parent + oracle + additive reference numbers: MEASURED@ cited metrics.json paths above.
- Self-test planted MRRs (LAP_ORACLE 0.538, SR_ORACLE 0.820, LAP_COMPOSE_FLAT 0.300, LAP_COMPOSE_NYS 0.299,
  SR_COMPOSE_FLAT 0.227, SR_COMPOSE_NYS 0.198, RAND_COMPOSE 0.074, RAND_NULL 0.103, NYS scrambles ~0.086;
  leak_audit clean; 17 distinct sigs): MEASURED@ local self-test (synthetic SBM, apparatus validation only).
- The rejected 1/lambda Nystrom LAP_COMPOSE_NYS=0.042 < RAND_NULL=0.10: MEASURED@ author self-test probe (rejected).
- FULL real-arena compose MRRs + the TRANSFERS/DOESNT verdict: HYPOTHESIZED (not yet run) -- the remote FULL decides.
