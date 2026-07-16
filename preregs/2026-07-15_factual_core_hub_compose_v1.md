# Pre-reg: factual_core_hub_compose_v1 (2026-07-15)

## Question
Does an LLM-GENERATED factual CORE tier compose seamlessly with a CONJUNCTION MODULE via the SHARED canonical-ID
(SGD systematic-ORF) HUB? This builds the SECOND half of the two-tier foundation (module #1/#2 = ingested
Costanzo/BioGRID, VET'd CHAIN_GRADE in exp_crossmodule_interface_hub_heldout_v2, HUB novel MAP=0.83). Design pointer:
notes/research_factual_core_tier_architecture_2026-07-15.md (section 5 linchpin) + notes/foundation_module_registry_architecture_and_module1_spec_2026-07-15.md.

## Honest scope (CONSTRUCTION-grade INTEGRATION pilot, NOT a capability claim)
Proves: (a) the LLM-generated core composes with a conjunction module via the shared canonical-ID hub, (b) the identity
join is EXACT string-equality (no crosswalk), (c) storage is INTERFERENCE-FREE (adding generated core facts does not
corrupt the module store). Does NOT claim frequency-beating (structurally capped, out of scope). Core VALUE metrics =
canonical-ID coverage/density + glass-box auditability, reported directionally (design note section 1).

## Prior-work check
substrate_query "factual core tier canonical ID hub cross-tier composition": top hits are dictionary words
(corer/CORE/core, cosine <= 0.35) + one unrelated 2026-06-10 controls note; NONE are prior factual-core-tier arc cells
at cosine>0.30. Genuinely novel (this is the first factual-core-tier build). Directly extends the VET'd cross-module
hub cell by swapping module-P (BioGRID physical) for the LLM-GENERATED factual core (property facts, cross-TYPE conjunction).

## Mechanism (VSA shared-hub-codebook; the VET'd cross-module mechanism, core swapped in for module-P)
One random unit-modulus FHRR hub code h(orf) per canonical ORF, shared read-only across both tiers.
- CORE store  M_CORE = sum over property-facts (gene g, prop-value p) of bind(h(g), h_prop(p)).
- MODULE store M_MOD = sum over genetic edges (a,b) of bind(h(a), h(b)).
- Cross-tier query CT(P,Y): gold A = genes_with(P) INTERSECT partners(Y), a PROPER subset of BOTH conjuncts.
  s_core(z)=Re<unbind(M_CORE,h_prop(P)),h(z)>; s_mod(z)=Re<unbind(M_MOD,h(Y)),h(z)>; HUB rank = norm(s_core)*norm(s_mod).

## Arms (retrieval MAP, higher=better)
HUB (shared hub + separate stores + identity product; WINNER) | CORE_ONLY, MODULE_ONLY (single-constraint ceilings;
gold is a subset of each) | SCRAMBLE (core stored under permuted gene identity; MUST-FAIL) | NO_HUB (core on an
independent codebook + random alignment; MUST-FAIL) | RANDOM (chance floor).
HP_SCOPE: HARD_PASS gates apply to HUB vs max(CORE_ONLY,MODULE_ONLY,SCRAMBLE,NO_HUB). RANDOM = chance-floor contrast.

## Pre-registered bands (fixed BEFORE running)
Multi-seed mean over 5 hub-codebook seeds (7,13,17,23,29). The ONLY randomness is the hub codebook.
- **HARD_PASS_FACTUAL_CORE_COMPOSES_VIA_HUB**: JOIN clean (join_precision >= 0.99 AND fuzzy_gain_frac <= 0.05 AND
  n_shared_orfs >= 25) AND discriminator fires (n_queries >= 30 proper-subset gold) AND HUB_MAP >= 0.30 AND
  HUB - max(CORE_ONLY,MODULE_ONLY) >= 0.15 (genuine conjunction) AND HUB - max(SCRAMBLE,NO_HUB) >= 0.15 AND
  SCRAMBLE,NO_HUB <= single_ceiling + 0.05 (identity NEEDED) AND interference-free (module MAP delta <= 1e-9 AND module
  store hash bit-identical with vs without the core tier) AND arms differ AND determinism.
- **HARD_FAIL_JOIN_LOSSY**: join_precision < 0.99 OR fuzzy_gain_frac > 0.05 OR n_shared_orfs < 25.
- **HARD_FAIL_NO_COMPOSITION**: JOIN clean but HUB does not beat the single-constraint ceiling by >= 0.15.
- **HARD_FAIL_IDENTITY_NOT_NEEDED**: SCRAMBLE or NO_HUB not >= 0.15 below HUB (conjunction without identity -> hub claim vacuous).
- **HARD_FAIL_INTERFERENCE**: module MAP changes OR module store hash changes with the core tier present.
- **MIDDLE_BAND_LOW_POWER**: n_queries < 30 with proper-subset gold.

## Discriminator-survives-scale
Scale is FIXED (small curated pilot; the smoke IS full scale). The `--self-test` ALSO builds a PLANTED arena and runs the
FULL VSA arms at N_DIM=16384, asserting HUB - {CORE_ONLY,MODULE_ONLY,SCRAMBLE,NO_HUB} >= 0.15 and interference delta == 0
at full N BEFORE the curated population is trusted (option A + C). Discriminator fires STRUCTURALLY: gold is a PROPER
subset of both conjuncts, so the single-constraint ceiling is bounded by |gold|/|conjunct| < 1 (cannot saturate) and HUB
beats it by construction; the query builder enforces the proper-subset condition.

## Compute architecture
(b) sequential-CPU with justification -- VSA core batched as single complex64 matmuls (no python per-query loop); V=30
genes, N=16384, tens of queries -> seconds on CPU; GPU yields nothing at this size. Storage: BUNDLED-ASSOCIATIVE per tier
(single-hop-per-tier unbind + identity-anchored intersection; NOT a depth>=2 chain -> sharded-vs-bundled chain-grade law
does not apply). device=cpu (runner passes no argv). Determinism: FIXED seeds + sorted(set()) vocab + np.random.default_rng;
NO hash() seeding, NO list(set()) dedupe (PROT-023). ASCII-only; no bare except; SystemExit before Exception; atomic write.

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = 5 seeds; verdict counts per-seed MAP == n_seeds per arm.
- arms_differ_verified: true (self-test hashes per-arm score matrices on the planted arena).
- final_metrics_atomicity: tmp_replace.
- crlb_n/a: retrieval MAP has no closed-form CRLB; floor = empirical RANDOM-arm MAP + planted-arena full-N preview.
- baseline_in_band: single-ceiling bounded < 1 by construction; RANDOM bounds chance; discriminator fires (proper-subset gold).
- calibration_check: adaptive_with_discriminator_gate (must-fail null = MEASURED single-constraint ceiling, not random floor;
  proper-subset query filter = discriminator-still-fires; self-test asserts HUB beats ceiling on a planted arena first).
- real_code_path: self-test builds REAL hd_bind/hd_unbind VSA arms at full N on a planted arena.
- substrate_signature: hd_bind/hd_unbind bound against live hdlab.binding signatures.
- deterministic_seeding: FIXED int seeds; sorted(set()); default_rng; no hash()/list(set()).
- start_marker_written + crash_diagnostic_present: true. heartbeat: exempt (single-shot, wall < 60s).
- cell_chunked: false (single-shot, no per-seed runner-death risk at seconds-scale).

## Functional requirements -> primitives
- exact identity join (canonical ID) -> string-equality set intersection + SGD-ORF regex well-formedness (compute_join).
- retrieve genes-by-property (CORE) -> associative store bind + unbind cleanup (hd_bind/hd_unbind; VET'd primitive).
- retrieve genetic partners (MODULE) -> same associative store (VET'd cross-module mechanism).
- cross-tier conjunction -> identity-anchored product of normalized per-tier readouts (VET'd cross-module hub pattern).
- interference-free storage -> separate tier tensors + bit-identical store-hash assertion (pattern-separation hedge, CHAIN_GRADE).

## Generation provenance (factual core)
LLM (Claude Opus 4.8), template factual_core_yeast_v1, 2026-07-15. Crispness allowlist only (taxonomic / compositional /
quantitative-measured); NO causal/severity relation. Per-fact relation-category tag + cross_check flag
(derived_from_orf_id = mechanically re-derivable, strongest; knowledge_based = LLM-training-knowledge, not externally
re-verified this session -- a flagged follow-up). ORF ids canonical-FORMAT (regex-validated at load). Module genetic edges
= structured cross-pathway SGA stand-in (EDGE STRUCTURE only; shared SGD-ORF vocabulary; exact-string identity join).

## Density audit (design note section 3; REPORTED directionally, NOT gated)
Per-gene attributes / relation-categories / exposures vs the 13/3/6 brain floor. Expected: categories floor met (>=3);
attributes partway; exposures low (only 2 provenance sources in this pilot) -- reported as directional, not a pass/fail
gate (gating a 2-source pilot on a 6-exposure floor would be a fake fail). HARD-PASS (iv) = on-path WITHOUT any crispness
violation (no causal/severity relation needed to reach the categories).

## Dispatch
Local self-test + full run to completion (small; local re-authorized for this task; wall < 60s). Report real numbers.
