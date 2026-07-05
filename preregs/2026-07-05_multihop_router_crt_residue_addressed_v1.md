# Pre-registration: exp_multihop_router_crt_residue_addressed_v1

**Anchor:** `multihop_router_crt_residue_addressed_v1`
**Cell:** `experiments/exp_multihop_router_crt_residue_addressed_v1.py`
**Date:** 2026-07-05
**Author:** exp_dev
**Brain component:** Thalamic dynamic router (Sherman-Guillery 2017; Halassa-Kastner 2017). RC2 (algebraic/CRT) candidate from `notes/research_brain_component_rerank_thalamus_cerebellum_load_2026-07-05.md`.
**Compute architecture:** batched-torch-CPU (all chains transited in one matmul per hop; no matmul in a python loop). Storage: no_storage beyond the certified Hebbian W (sharded-per-entity codebook E; not bundled). Task-mandated CPU probe (no LLM/GPU).

## Question
Can the ALREADY-CHAIN_GRADE CRT-residue decode (`exp_generation_decoder_rns_crt_highvocab_v1`, HARD_PASS, V=65536) be repurposed AS the dynamic router for the certified 5-hop `partition_routed_chain` (hdlab/multi_hop.py, 0.955 cv=0.007 ONLY under `oracle_routing=True`), replacing the oracle cheat with a deterministic, glass-box, algebraic address-by-residue router?

## Design
- Regime matched to the certified atom: N=8192, V_C=200, N_PARTITIONS=20, PART_SIZE=10, K=5, N_RELATIONS=8, n_chains=200, seeds {7,13,19}.
- CRT-residue partition scheme: `partition(id) = id mod 20 = CRT(id mod 4, id mod 5)`, coprime moduli (4,5), product=20=N_PARTITIONS.
- Entity codebook E: dims [0,768) carry the residue ADDRESS (two disjoint sub-blocks, residue codebooks m1=4-way / m2=5-way, shared within a partition); dims [768,8192) = iid identity (within-partition discrimination). All bipolar.
- Router decodes each residue by sub-block argmax on the post-transit state, CRT-reconstructs the partition. Within-partition argmax (identity dims) then picks the exact entity, exactly as the certified mechanism.

## Arms (paired on identical chains per seed; only the router differs)
1. `oracle` — partition = true_target mod 20 (CEILING / Gate-D reproduce). HYPOTHESIZED ~0.955 e2e.
2. `crt_residue` — decode residues + CRT (MECHANISM under test).
3. `naive_centroid` — full V-way argmax; partition = argmax_id mod 20 (BASELINE / prior real candidate).
4. `static_bridge` — partition = relation_idx mod 20 (content-independent static plumbing CONTROL).
5. `random_router` — uniform partition (chance anchor / broken-router CONTROL).
6. `scrambled_crt` — decode residues then DERANGE before CRT (CRT-load-bearing CONTROL).

## Bands (envelope-fail-bands; HP_SCOPE = crt_residue only)
- **HARD_PASS:** crt per-hop route >= 0.90 AND crt e2e >= 0.70 AND cross-seed cv(e2e) < 0.05 AND crt route > naive route + 0.05.
- **HARD_FAIL:** crt route <= naive route + 0.05 (doesn't beat prior real candidate) OR crt e2e <= 0.20 (below naive-composed floor).
- **MIDDLE_BAND:** real improvement over naive but below the chain-grade-composable bar (needs learned top-up / RC3).
- **Discriminator-fires gates (all modes):** oracle e2e >= 0.85 (Gate-D reproduce), random route <= 0.15 (setup not vacuous), scrambled_crt e2e <= 0.10 (CRT load-bearing), naive route in (0.05,0.95) (META_RULE_AG baseline in band).

## SCHEMA-VET (§15 gates)
- Gate A (effective vs nominal): no swept axis (fixed regime + arm comparison); n_partitions fixed. **ALIGNED**.
- Gate B (discriminating band): arms predicted to span [oracle ~0.98 ceiling, naive ~0.5, controls ~0.05]; the test metric (crt route) predicted in [0.30,0.95] discriminating band. **>=0.30 fraction**.
- Gate C (shape): state (n,N) -> residue argmax (n,) per modulus -> CRT (n,) partition -> masked within-partition argmax. **SHAPE_MATCH** end-to-end.
- Gate D (reproduce prior CG at test regime): `oracle` arm reproduces certified 5-hop 0.955 at the CRT-residue-structured-codebook regime, tolerance 0.10. Regime-extension audit: **SHAPE_DRIFT** (codebook changed random-iid -> CRT-residue-structured; risk that the shared-address correlation perturbs the base chain — measured: it does NOT, oracle reproduces 0.980).
- Gate E (functional requirements): (1) coarse partition routing -> CRT residue decode; (2) fine within-partition retrieval -> certified argmax cleanup; (3) chain composition -> certified partition-routed chain.
- CRLB: within-partition random floor = 1/PART_SIZE = 0.10; routing random floor = 1/N_PARTITIONS = 0.05. HP e2e 0.70 and HP route 0.90 both reachable.
- META_RULE_AF arms_differ_verified: per-arm route-vectors hash-distinct. META_RULE_AH: tmp_replace atomic write. except SystemExit before except Exception. cell_chunked: false (n_chains-batched single cell; multi-seed loop is cheap, not runner-zombie-exposed). start_marker + crash_diagnostic + heartbeat present.
- progress_logging: print_flush_true (timeout_s would be >=1800 for a remote FULL; per-arm/per-seed flush lines emitted).

## RESULT (full-config local smoke == full config: n_chains=200, seeds {7,13,19})
MEASURED@data/exp_multihop_router_crt_residue_addressed_v1_smoke/metrics.json:
- oracle: route=1.000, e2e=0.980 (Gate-D reproduce PASS; base mechanism intact).
- crt_residue: route=0.415, e2e=0.147 (cv 0.129).
- naive_centroid: route=0.503, e2e=0.237.
- static_bridge route=0.048; random_router route=0.054; scrambled_crt e2e=0.005 (all controls collapse as designed).
- crt_minus_naive_route = **-0.088**.

**VERDICT (applying FULL bands): HARD_FAIL.** The CRT-residue router does NOT beat naive-centroid (delta -0.088) and e2e (0.147) is below the composable floor (0.20). Discriminator fired cleanly (oracle reproduces, controls collapse), so this is a genuine mechanism failure, not a test-design artifact.

**Address-size sensitivity (scratch, 1 seed, 200 chains):** ADDR 2x{384,1024,2048,3072} -> crt route {0.384, 0.208, 0.106, 0.078}; crt-minus-naive route negative at every size. Larger address makes it WORSE -> failure is FUNDAMENTAL, not under-resourcing.

**Mechanism (why RC2 fails):** the generation decoder's CRT residue decode worked because each token's residues sat in interference-free DISJOINT blocks of a clean composed sum. Here the router decodes residues from a Hebbian-retrieved state that is a SUPERPOSITION of ~1000 triples; the crosstalk lands in the same low-cardinality residue subspace (only m_i distinct residue codes) and biases the residue argmax, so the low-arity address decode is LESS noise-robust than a full-vector argmax, not more. Same primitive, different regime -> primitive does not extend (Gate-D-class regime mismatch caught at the router, while the base chain reproduces).

**Next:** RC2 algebraic-router hypothesis is falsified at this regime. RC3 (learned no-LLM router) is the indicated next candidate (as the drill anticipated for this branch). A remote canonical FULL is redundant (smoke IS the full config; robust cross-seed HARD_FAIL + 4-point sweep) -> honest-abort the full dispatch per DISCRIMINATOR-MUST-SURVIVE-SCALE.
