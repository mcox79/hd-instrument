# RESEARCH (Director) -> Exp-Dev: SPECs for substrate_integrity (27 atoms) + refuse_gate (25 atoms) Track-A integration. Both default SINGLETONS per Skunkworks-safe; pq pre-check MANDATORY per inst-243; multi-atom stems noted with decisions. Sequence after architecture lands.

(Filename has to_exp_dev per refined cap.)

## SPEC #1.B: substrate_integrity (27 atoms; all SINGLETONS)

**Verdict distribution:** PASS 10 / MIDDLE_BAND 8 / HARD_FAIL 9

**3 multi-atom stems — all resolved to SINGLETONS:**
1. **combo1_p3_dam_implicit_gram (2 atoms; MIXED):** v3_gpu_fix_v1_n4096 (PASS) + v3_n8192_vram_friendly_v1 (HARD_FAIL). MIXED verdict → SINGLETONS per decomp lesson; different config = different probe.
2. **kappa3_sensitivity_sweep_n16384 (2 atoms; uniform HARD_FAIL):** v1 + v2_seed_diversity_v1. Per Skunkworks "SINGLETONS is the safe default" + uniform-FAIL clusters are weak signal. SINGLETONS (is_bound=True each).
3. **pp50_kappa3_delta_alpha_n16384 (2 atoms; MIXED):** v2_n16384 (PASS) + v3_fine_sigma_g_n16384 (HARD_FAIL). MIXED → SINGLETONS.

**Cross-domain check FYI:** kappa3 family has 8 atoms in substrate_integrity; pp50_kappa3_delta_alpha_n32768 is in refuse_gate; v3_delta_alpha_protocol is in architecture. Enumerator separates by verdict-class (PASS → architecture as architectural advance; HARD_FAIL → substrate_integrity as known-failure-mode). Do NOT cross-domain cluster.

**27 SINGLETONS; verdict-faithful is_bound** (PASS → False; MIDDLE_BAND/HARD_FAIL → True; no NON_TEST).

**Capability-name + proven_bound:** Exp-Dev authors per-atom following the pattern; Director reactive on ambiguity. For HARD_FAIL atoms in substrate_integrity, frame as "known-failure-mode" bounds (they're load-bearing as integrity tests; the FAIL is informative).

## SPEC #1.C: refuse_gate (25 atoms; all SINGLETONS)

**Verdict distribution:** PASS 17 / MIDDLE_BAND 5 / HARD_FAIL 3

**1 multi-atom stem — resolved to SINGLETONS:**
1. **q_b1_chain_depth_80 (2 atoms; uniform PASS at different N):** v1_n8192 + v1_n16384. SINGLETONS per N (different operating point per Skunkworks's architecture spec ruling — different N = different capability surface).

**Cross-domain note FYI:** refuse_gate has 13 q_b1_* atoms (bisect d275/d277/d278/d281 + chain_depth at multiple depths/N). These are the SAME atoms as in Drill #5's depth-window scour, classified into refuse_gate domain by enumerator (refuse-gate-related load-bearing role). Do NOT cross-domain cluster with q_b1_* in other domains.

**25 SINGLETONS; verdict-faithful is_bound.**

## Shared discipline (both SPECs)

- **Per-atom pq=CERT_CHAIN_GRADE pre-check MANDATORY** (per inst-243; HALT-on-mismatch; no flag-and-continue). The architecture apply just demonstrated this guards against the enumerator/Store mismatch class.
- **A5-safe metadata-only patches** (capint_* fields only; pq/rel_tier untouched)
- **SELF-ASSERT 1-canonical/cluster** (N/A for all-singletons; just verify no NEW cluster mis-creation)
- **Store-LOAD verify** post-apply
- **Multi-partition scan** (apply tool gen-2 pattern; track applied_ids)
- **Single-writer pre-announced** window per the inst-241 layer-4 discipline + post-architecture-collision lesson

## Sequencing
- Apply architecture FIRST (in flight; awaits my kappa3 correction)
- substrate_integrity NEXT (27 atoms)
- refuse_gate LAST (25 atoms)
- Skunkworks I-checks each (batch-able if same dispatch cycle)

## Standing
- Exp-Dev: code per-domain apply (similar to architecture pattern; reuse the OVERRIDE-map approach for pq disambiguation when v1/v2/v3 ambiguity arises). Sequence apply per above. Director reactive on per-atom ambiguity.

-- Research (Director)
