# Pre-registration: chem_bind_readout_integration_v1

Filed 2026-07-15 (BEFORE full run). Cell: `experiments/exp_chem_bind_readout_integration_v1.py`.
Artifact: `data/foundation_clusters/chem_pair_hazard_nonadditive_v1.json` (135 vetted_true class-pairs).

## Question
THE synthetic->real integration proof. Does the substrate's LEARNED SYMMETRIC BIND (frontier arm LEARN_SYM =
shared per-symbol code + ELEMENTWISE-PRODUCT composition = swap-symmetric; proven on synthetic PARITY 0.98 vs
additive 0.38, commit 59056b6d4) READ OUT the real generated chem-pair mixing-hazard NON-ADDITIVE conjunction on
HELD-OUT pairs, BEATING (a) a matched-capacity ADDITIVE model and (b) a fair FREQUENCY floor?

## Prior-work check (substrate KB concept-query)
Top hits at cosine ~0.30 = old refuse-gate / readout-C1 VET notes + generic "chemical reaction" wordnet atom;
NONE is this synth->real bind-transfer proof. Novel cell (first mechanism x real-foundation-data connection).

## Arms (matched-capacity contrast is load-bearing)
- LEARN_SYM: shared class code (NCLS x D) + elementwise PRODUCT + linear 5-way readout. Predicted WINNER.
- LEARN_ADD: shared class code + SUM + SAME readout. Differs from SYM ONLY in compose op -> isolates interaction.
- ADD_LSTSQ: optimal closed-form per-class main-effects (ordinal). Classical strong additive baseline.
- LEARN_ROLE: role-keyed (asymmetric) product. ALGEBRA contrast -- must NOT beat SYM on a symmetric target.
- HOMOPHILY / MEMORIZE / POP / ORACLE(ceiling) / FREQ_NULL = max(HOMOPHILY, POP).
best_additive = max(LEARN_ADD, ADD_LSTSQ). SYM must beat BOTH additive arms.

## Strata (entity-level held-out split, query_frac=0.40; both are genuinely novel pairs)
- SEEN class-pair (class-combination in train; the generator's non-additivity regime): PRIMARY.
- NOVEL class-pair (class-combination NEVER in train): STRETCH; thin (~7-10/seed); lookup provably collapses to
  additive here (generator MEASURED int_novel == add_novel == 0.29238), so a WIN here = genuine generalization.

## Regimes / must-fails
CLEAN(real); ARBITRARY (random hazard per unique class-pair; must-fail on NOVEL); SHUFFLE (label permutation;
must-fail on ALL). LEAK guard: query rows disjoint from train + novel-marked class-pairs absent from train.

## Pre-registered bands (fixed before running)
- PRIMARY (SEEN, CLEAN, multi-seed mean): SYM_seen - max(additive_seen) >= 0.10 AND SYM_seen - FREQ_seen >= 0.10
  AND SYM_seen - chance >= 0.15.
- ALGEBRA: SYM_seen >= ROLE_seen - 0.05.
- MUST-FAILS: SHUFFLE (SYM_all - FREQ_all) <= 0.12 AND ARBITRARY (SYM_novel - FREQ_novel) <= 0.12; oracle >= 0.999; leak_ok.
- STRETCH (NOVEL): SYM_novel - max(additive_novel) >= 0.08 -> suffix _NOVEL_GENERALIZES.
- HARD_PASS_TRANSFER: PRIMARY AND ALGEBRA AND MUST-FAILS AND oracle AND leak.
- REFUTE_NO_TRANSFER: SYM_seen - max(additive_seen) <= 0.03 (mechanism does NOT read the conjunction even
  in-distribution; synth->real transfer FAILS -- honest, drill-worthy negative). Trusted only if must-fails fire + oracle=1.0.
- MIDDLE_BAND: anything else.

16% adversarial-vet label noise (truth 0.833) => REAL-DATA ROBUSTNESS test; noise is NOT treated as failure.

## Compute architecture
(b) sequential-CPU with justification: 135 real pairs x NCLS=11; per-seed = a few tiny (<=135x32) Adam fits
(milliseconds); total wall < 60s over 10 seeds. GPU batching gives no speedup on sub-ms matmuls. Storage:
no_storage / no_composition-chaining (single-hop readout). Determinism: fixed int seeds + sorted-unique class-pair
ids; NO hash(), NO list(set()) (PROT-023; queue_add static scan enforces).

## Discipline gates (self-test verified BEFORE ship)
- REAL bind path: fhrr_bind_homomorphism + hadamard_equals_complex_bind (product == substrate FHRR bind op).
- Discriminator FIRES: SYM beats ADD by >=0.12 on the synthetic interaction plant (mechanism works when signal present).
- guard-vs-arena-floor: FREQ >= POP > 0.05 (real floor, not degenerate).
- ARMS-MUST-DIFFER witnessed on REAL data (6/6 distinct; saturated plant excluded per legit coincidence).
- real_code_path: self-test loads the actual artifact + runs full score() (not a synthetic-only branch).
- determinism_ok; oracle ceiling; except SystemExit before except Exception; atomic tmp+os.replace metrics write.

## Seeds
FULL: (7,13,17,23,29,31,37,41,43,47) = 10. SMOKE: (7,13,17) = 3.
