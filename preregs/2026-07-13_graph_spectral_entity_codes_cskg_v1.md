# Pre-registration: graph_spectral_entity_codes_cskg_v1

Date: 2026-07-13. Author: exp_dev. Anchor: `graph_spectral_entity_codes_cskg_v1`.
Cell: `experiments/exp_graph_spectral_entity_codes_cskg_v1.py`.
Queue: remote_cpu_queue (device=cpu; zero SGD; closed-form randomized SVD + one-shot Hebbian). Seeds [7,13,17].

## Question

Structure never lives in the arbitrary entity LABEL (proven dead: residue/CRT closure, Shannon + Kolmogorov). Track-A
5x-drill lever #2 (converged across wildcard/field/neuro lenses): does it live in the RELATION GRAPH? Build entity
codes FROM the co-occurrence graph's OWN spectral structure -- normalized-Laplacian eigenvectors / PPMI-SVD (NetMF) /
discounted successor-representation -- instead of random codes, and test whether that raises the recoverable-signal
ORACLE CEILING and the realized anchor-compose magnitude vs RANDOM codes on the SAME arbitrary-label held-out-entity
arena. Glass-box: closed-form eigendecomposition (randomized SVD), inspectable, no learned aggregator.
Degree-heterogeneity corrected (symmetric-normalized Laplacian D^-1/2 A D^-1/2).

Prior-work check (substrate-KB concept-query, cosine>0.30): NONE. Top hits `spectral_graph_theory` algebra-dict
(0.2998), a `GNN+VSA hybrid` cross-domain drill note (0.2822), `spectral_capacity_monitor_v1` metrics (0.2803) -- all
below 0.30 and none a prior CELL building graph-spectral entity codes on this arena -> GENUINELY NOVEL for the
substrate. Honest adjacency flagged: `grounding_learned_sr_heldout_reasoning_v1` (LEARNED SR, inductive held-out
edges) already found no-better-than-random. This cell differs: closed-form spectral CODEBOOK, measured as (a) a
TRANSDUCTIVE ORACLE CEILING (does a graph-structured codebook beat a random codebook in pure associative capacity)
and (b) a realized INDUCTIVE compose (does deriving a held-out entity's code from its graph-neighbors' spectral
coordinates beat random assignment). Standing-caution honored: `reference_correlation_hurts_associative_store_
capacity_decouple_from_retrieval_2026-07-08` predicts correlated (spectral) store-codes may COLLIDE -> NO_LIFT is a
genuinely possible, informative outcome (construction-proof != capability win; the discriminator CAN fail).

## MP / SPIKED-EIGENVALUE PRE-CHECK (cheap decisive gate; MEASURED on this exact CSKG core graph, N=25752)

Ran FIRST, before authoring the code arms. MEASURED@scratch mp_precheck (re-logged in-run gates.mp_precheck):
- Gini(degree) = 0.5368 (>0.5; top decile carries 51.7% of edges) -- degree heterogeneity present.
- lambda_2 = 0.9499 = 5.76x the random-null bulk radius rho = 1/sqrt(dmean=36.81) = 0.1648; 59 of the top 60
  eigenvalues (excluding the trivial Perron lambda_1=1) exceed rho -> SPIKED/community structure PRESENT (the graph
  is NOT a random/Erdos-Renyi graph; there IS above-null exploitable structure).
- BUT top-20 eigenvalue energy fraction = 0.0133, top-50 = 0.0228 -> the graph is NOT low-rank: most spectral energy
  lives in the incompressible ~25.7k-dim bulk (the "arbitrary/incompressible residual" the drills predicted).

Read: structure EXISTS above the MP bulk edge, but it is a tiny fraction of total energy. This is precisely the
regime where it is an OPEN empirical question whether feeding that above-null structure into the store's CODES raises
recoverable capacity, or whether correlation-hurts-capacity dominates. The FULL run answers it. (The drill's own
combined HARD-PASS -- Gini>0.5 AND top20_energy>0.30 -- is HALF-met: Gini passes, low-rank-energy fails; so this is
neither a clean go nor a clean close, exactly the ambiguity a decisive cell should resolve.)

## Reference bars (MEASURED, on-disk)

- Native monolithic ORACLE @ d1024 = 0.023083 MEASURED@data/exp_kg_store_dim_scaling_ceiling_v1/metrics.json:gates.
  oracle_mrr_by_dim.1024 ; relief @ d8192 = 0.780600 (same file) -> the discriminator (spectral - random @ matched
  d1024) sits FAR below saturation, can move in either direction.
- Additive (SGD TransE k=24) ORACLE = 0.137293 ; realized additive compose = 0.128210
  MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.{ORACLE_ADDITIVE,ANCHOR_COMPOSE}.

## Design (matched code dim d=1024 for ALL code arms; native 0.023 baseline lives at d1024)

Arena: CSKG core k_core=12 (N~25.7k, ~511k core edges, 29 rels), held-out-entity split frac=0.15, support_frac=0.5,
seeds [7,13,17] -- COPIED VERBATIM (bit-identical split) from the native + additive + residue-ceiling arenas.

Codes (closed-form, glass-box, degree-corrected; randomized SVD rank d, n_iter=3, oversample 24):
- LAP  : symmetric-normalized-Laplacian embedding = top-d singular vectors of S = D^-1/2 A D^-1/2 (= smoothest L_sym
  eigenvectors since L_sym = I - S), scaled by sqrt(singval), row-normalized to L2=sqrt(d) (kills degree/norm confound).
- PPMI : PPMI-SVD / NetMF window-1 = rank-d SVD of positive-PMI( (D^-1 A) D^-1 * vol ) (node2vec-equivalent MF).
- SR   : discounted successor representation M_SR = sum_{k=0}^{6} gamma^k (D^-1 A)^k, gamma=0.5 (Horner operator);
  rank-d SVD left singular vectors (Stachenfeld 2017 SR eigenbasis).

ORACLE (transductive ceiling; codes on FULL graph incl held-out edges; held-out edges folded into a one-shot Hebbian
W over the injected codebook; native bilinear recall + score vs the same codebook):
- RAND_ORACLE : base native path VERBATIM (bipolar E) -> POSITIVE CONTROL reproducing ~0.023 + the RANDOM-CODE bar.
- LAP_ORACLE / PPMI_ORACLE / SR_ORACLE : the three graph-structured codebooks. HEADLINE.

COMPOSE (inductive realized; train-only W over train codes; held-out row = row-normalized mean of its SUPPORT-neighbor
(head) codes; native recall + score vs the patched codebook):
- LAP_COMPOSE : held-out code from true support-neighbors' TRAIN spectral codes. HEADLINE.
- RAND_COMPOSE : SAME neighbor-mean aggregation over the bit-identical random codebook (apples-to-apples random bar).
- LAP_COMPOSE_SCRAMBLE : aggregate over RANDOM entities (not the true neighbors) -> MUST-FAIL.

Controls: RAND_NULL (pure chance floor); BASELINE_POP (freq baseline / fit-independence / BROKEN guard).

## Bands (PRE-REGISTERED before the run; bars = a MEASURED same-dim in-run RANDOM arm + CITED ceilings)

best_spec_oracle = max(LAP_ORACLE, PPMI_ORACLE, SR_ORACLE). LIFT_MARGIN = 0.010 (strictly above the random codebook).

- GRAPH_STRUCTURE_LIFTS_BOTH : pos-controls hold AND oracle fires AND (oracle lift: best_spec - RAND_ORACLE >= 0.010)
  AND (compose lift: LAP_COMPOSE - RAND_COMPOSE >= 0.010 AND LAP_COMPOSE - LAP_COMPOSE_SCRAMBLE >= 0.005).
- GRAPH_STRUCTURE_LIFTS_PARTIAL_MIDDLE : exactly ONE of {oracle, compose} lifts (marginal edge; sweep rank/dim/gamma
  before any lever claim).
- NO_LIFT_GRAPH_STRUCTURE_UNEXPLOITABLE : pos-controls hold AND oracle fires AND best_spec - RAND_ORACLE < 0.010 AND
  LAP_COMPOSE - RAND_COMPOSE < 0.010 -> graph structure NOT exploitable by this store despite MP spiked structure ->
  the wall is the STORE/READOUT (correlation-hurts-capacity), not the graph -> closes this lens (2x-drill negative).
- INCONCLUSIVE : oracle does not fire, pos-controls fail (RAND_ORACLE off 0.023 by >0.010, RAND_NULL > 0.004), too
  few held-out queries, or POP beats RAND_NULL (BROKEN; guard validated vs the RAND_NULL/arm floor per Gate F.4).

## SCHEMA-VET fields

- cardinality_ok: EXPECTED_N_UNITS = 3 (seeds); each seed asserted all-arms + >=5 distinct sigs + finite W.
- arms_differ_verified: yes (9 arms; >=5 sigs/seed asserted; self-test measured 9 distinct).
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace).
- except-ordering: SystemExit/KeyboardInterrupt re-raised BEFORE except Exception; no bare except / no BaseException
  (grep gate CLEAN).
- crlb_n/a: no closed-form noise floor; bands are a MEASURED in-run same-dim RANDOM arm (spectral must beat a measured
  random codebook) + CITED additive-oracle 0.137 -> discriminator_reachability OK by construction.
- baseline_in_band: RAND_ORACLE reproduces native ~0.023 (>> RAND_NULL chance ~1/N) = the ORACLE-FIRES gate; the
  0.05<baseline heuristic is calibrated for accuracy metrics NOT filtered-MRR-over-25k (calibration_check documents this).
- discriminator_survives_scale: analytical (option B) -- the discriminator is (spectral - random) at matched d1024,
  BOTH measured in-run at the EXACT CSKG regime that measured 0.023->0.781; RAND_ORACLE far from saturation so the
  gap can move either way; the MP pre-check establishes there IS above-null structure to grab. Self-test additionally
  fires LAP-recovers-planted + spectral-embedding-separates-blocks (purity 0.476 >= 0.45, ~2.8x chance) + compose-
  scramble-collapses on a planted SBM.
- calibration_check: default_ok_for_this_regime (all dims/ranks/fracs/tols/gammas pre-registered, NOT tuned on real
  data; arena config copied verbatim).
- HP_SCOPE: LIFT gates apply to LAP/PPMI/SR_ORACLE + LAP_COMPOSE only. RAND_ORACLE = pos-control + random bar;
  RAND_COMPOSE = compose random bar; LAP_COMPOSE_SCRAMBLE = must-fail; RAND_NULL = chance floor; POP = BROKEN guard.
- real_code_path (F.1): self-test builds the REAL KGStore, injects a closed-form Laplacian codebook, runs
  ingest_triples (exercised: build_adjacency, lap_codes, KGStore, build_store_with_codes, ingest_triples,
  native_query_recall).
- substrate_signature (F.2/F.3): KGStore bound against live signature with BASE/portable kwargs only
  (n_ent,n_rel,n_dim,generator); no optional init_entities.
- guard_baseline_valid (F.4): BROKEN(POP>RAND_NULL) guard validated vs the RAND_NULL/arm floor (RAND_ORACLE above floor).
- defensive_error_checking: start-marker + crash-diagnostic (CELL_CRASHED + traceback) + per-seed heartbeat + per-seed
  failure_class; cell_chunked=false (sweep-free 3-seed loop; single cell).
- progress_logging: print_flush_true (line_buffered stdout + per-seed/per-arm flush prints + heartbeat; timeout>=1800).

## Compute architecture

class (b) sequential-CPU, justified. Codes = closed-form randomized-SVD (rank 1024) of a ~25.7k-node/~474k-edge
SPARSE operator (a few sparse matvecs; NO SGD, NO epochs, NO learned aggregator). Store = one-shot Hebbian. All CPU
-> remote_cpu_queue (device=cpu). No GPU. Storage: cell-local KGStore instances only; no persisted-store mutation.

## HYPOTHESIZED vs MEASURED

- MP pre-check numbers: MEASURED@scratch mp_precheck (Gini 0.5368, lambda2 0.9499, top20E 0.0133).
- Reference ceilings (0.023083, 0.137293, 0.128210, 0.780600): MEASURED@ cited metrics.json paths above.
- Self-test planted MRRs (LAP_ORACLE 0.538, RAND_NULL 0.103, LAP_COMPOSE 0.300, SCRAMBLE 0.157, purity 0.476):
  MEASURED@ local self-test (synthetic SBM, apparatus validation only; NOT a real-arena result).
- FULL real-arena MRRs: HYPOTHESIZED (not yet run) -- the remote FULL produces the verdict.
