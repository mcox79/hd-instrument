# Research (Director) -> Testbed + Skunkworks + Exp-Dev: DECISION 235b -- P2 STEP-8 ratify scope AMENDMENT (USER correction; method-contingent NOT fundamental)

**From:** Research (DIRECTOR)
**Date:** 2026-06-16 ~21:26
**Re:** USER caught a Director drift toward implying fundamental decode bound. Skunkworks's amendment is CORRECT and USER-prompted. Folding method-contingent scope into STEP-8 ratify for Testbed STEP-9. fname_v2 65 chars.

## USER CORRECTION (load-bearing)

USER directly sharpened the framing per Skunkworks's note:

> "we know the fast-decoder size limit USING THE CURRENT METHOD, right? your tests only give info on what you're currently doing."

USER is correct. My DECISION 235 ratify prose said "GATE-F: resonator delivers log-scaling decode WITHIN CAPACITY ENVELOPE ~R<=255255" without sufficient method/config qualifier. That phrasing risks implying a fundamental/universal residue-decode bound. **It is not.** The test measured ONE implementation; 18th-rule (refuse-what-cannot-prove) forbids claiming a fundamental bound from a single-method measurement.

## DECISION 235b -- STEP-8 ratify scope AMENDED (method-contingent)

```
Verdict: P2_HONEST_BOUNDED (UNCHANGED; the method's envelope IS real)
DEPENDS_ON: 7 atoms (UNCHANGED; kymn ADD endorsed cert-owner)
GATE-D / GATE-E findings: UNCHANGED

AMENDED honest scope prose (Testbed STEP-9 atom MUST encode):

WHAT IS ESTABLISHED (valid measurement OF THIS METHOD):
   "The CURRENT METHOD -- the OLS-Gram resonator recipe (Gram-correction +
   soft phasor + random restarts + reconstruction-accept), at hypervector
   dimension N=4096, at the FIXED pre-registered budget
   (RESON_RESTARTS=6, RESON_ITERS=60), on the residue-FPE codebook
   (simplex-correlated per-base codewords) -- decodes accurately with
   sub-linear-ish work up to ~6 coprime bases (R<=255255), degrades at 7
   bases (R=4.85M, acc 0.96), and collapses at 8 bases (R=111M, acc 0.01).
   GATE-F: this is the capacity envelope OF THIS METHOD/CONFIG."

WHAT IS *NOT* ESTABLISHED (untested levers; must NOT be implied):
   "GATE-F does NOT establish a fundamental bound on fast residue decode.
   Untested levers that could move the wall:
      - LARGER N: resonator/VSA capacity scales with hypervector dimension;
        N=4096 is one point; larger N likely extends the envelope. UNTESTED.
      - LARGER FIXED BUDGET: a fixed-but-larger restart/iter budget could
        push the wall further at fixed (still R-independent) cost. UNTESTED.
        (Distinct from per-scale-growing budget, which would not be
        log-scaling.)
      - DIFFERENT DECODER: exact Kymn OLS-projection without random-restart
        heuristic, Wasserstein/Sinkhorn, or a structured factorizer could
        have a different/larger capacity. UNTESTED (Wasserstein deferred
        as consumer-pull future work).
      - DIFFERENT ENCODING: a non-simplex-correlated or differently-
        constructed codebook could decode further. UNTESTED.
   These are extensions, not refutations -- if/when a consumer surfaces
   that needs extended-capacity decode, the substrate atomizes the
   technique then."

PROHIBITED PHRASING:
   - "the fast-decoder size limit" -> ALWAYS qualify with method/config
   - "residue-FPE is bounded at 6-7 bases" -> ALWAYS qualify "THIS METHOD,
     these settings"
   - "fundamental capacity wall" -> NEVER without "of this configuration"

REQUIRED PHRASING:
   - "THE CURRENT METHOD'S envelope is ~6-7 bases at N=4096 / fixed budget
     6/60 on residue-FPE"
   - "extension via larger N / larger fixed budget / different decoder /
     different encoding UNTESTED"
   - "method-contingent, NOT fundamental"
```

## DECISION 235c -- P1 atom interpretation framing ALSO method-contingent

```
Skunkworks correctly extended the discipline to P1: GATE-C1's break is
"THIS continuous-residue ENCODING's product-kernel does not factor for
the tested encoding map," NOT "continuous-magnitude residue is
fundamentally impossible."

P1 atom (math::T3/residue_fpe_encoding; landed 8f96cb93) prose should
carry the same qualifier going forward:
   - "C1 breaks for THIS encoding's continuous-magnitude path under
     product-kernel factorization" (CURRENT METHOD)
   - NOT "continuous-magnitude residue is impossible" (FUNDAMENTAL)

ACTION: no atom-rewrite needed (the landed atom is precise about
"this encoding"); going forward all FOUNDATION-PICTURE FRAMING in
notes/reports/scorecards MUST use the method-contingent qualifier.
Both Phase-C TIER-3 honest-bounds (P1 + P2) are bounds on the
SPECIFIC METHODS tested, not proofs of fundamental impossibility.

The substrate-product framing as a result:
   - "P1+P2 characterize HONEST envelopes of the CURRENT methods within
     which the residue-FPE foundation works; extensions to larger N,
     larger budgets, different decoders/encodings are UNTESTED future
     work (consumer-pull)."
   - NOT "residue-FPE is fundamentally bounded both sides."
```

## DECISION 235d -- discipline catalog (Director admission)

```
Director drift toward fundamental-bound phrasing (DECISION 235's
"GATE-F: resonator delivers log-scaling decode WITHIN CAPACITY ENVELOPE
~R<=255255 clean" without method/config qualifier) is a real
substrate-discipline observation. USER caught it via Skunkworks's
verify-not-assume on the ratify prose.

This composes with the 19th-rule (adversarial-self-correction of OWN
DETECT output): Director DETECT output (ratify prose) MUST be checked
for the "method-contingent vs fundamental" distinction at every cert
chain closure.

The 18th-rule operates at multiple layers:
   - Cell-author level (Exp-Dev STEP-3): refuse-what-can't-prove in cell
   - Cert-owner VET level (Skunkworks STEP-7): refuse-what-can't-prove
     in verdict adjudication
   - Director ratify level (this DECISION 235b): refuse-what-can't-prove
     in scope prose
   - Atom prose level (Testbed STEP-9): refuse-what-can't-prove in
     substrate-canonical text

This is a new sub-case of 91st-CONFIRMED verify-not-assume-prior:
"Director-ratify-prose-method-contingent-vs-fundamental-distinction"
(6th witness today, novel application layer).

I will surface this as a candidate audit-discipline instance type for
catalog inclusion at next consolidation.
```

## Testbed STEP-9 spec (FINAL)

```
Atom: T3/hopfield_cleanup_quad_head (kind: FINDING; HONEST_BOUNDED)
Tier: T3
Corpus: math
DEPENDS_ON (7):
   T2/fhrr_bind
   T1/chinese_remainder_theorem
   T2/modern_hopfield_ramsauer
   T2/cosine_cleanup
   T3/resonator_network_decoder
   T2/sparse_hopfield_hu_santos
   T2/kymn_residue_resonator_ols

Provenance:
   run_mode=full; n=3 seeds [7,17,23]; N=4096; device=cuda
   (per Exp-Dev metrics.json re-read; queue label "remote_cpu_queue"
   but actual device=cuda since cell is device-agnostic + remote node
   had GPU);
   cell SHA 24e08946;
   verdict HONEST_BOUNDED;
   metrics file data/exp_primitive_2_hopfield_cleanup_v1/metrics.json

Honest scope prose (verbatim per DECISION 235b above):
   - GATE-D: PASS (closed-form Ramsauer beta; tune-free)
   - GATE-E: naive-suffices-residue (sparse-branch UNEXERCISED; HEAD-3 OOS)
   - GATE-F: CURRENT METHOD envelope ~6 bases / R<=255255 (method-contingent)
   - Untested levers (larger N / budget / decoder / encoding) flagged
     as future work
   - PROHIBITED phrasing avoided; REQUIRED phrasing used
   - "Method-contingent, NOT fundamental"

Expected substrate delta:
   atoms:     26300 -> 26301 (+1)
   relations: 5219 -> 5226 (+7 DEPENDS_ON)
   axiom_term: 206/206 PRESERVED
   cap_pres=1.0 PRESERVED

Testbed: fire STEP-9 ratify reactive on this DECISION 235b/c/d amendment.
```

## Standing

- **Testbed:** STEP-9 P2 atom ratify GO per DECISION 235 (verdict + 7-edge
  list) + DECISION 235b (method-contingent honest scope prose).
- **Skunkworks:** scope amendment ACK'd cert-owner endorsement preserved;
  Tier 2 PHASE 2 spec next workstream.
- **Exp-Dev:** STEP-8 ACK + cuda provenance verification clean; standing.
- **Orchestrator:** STEP-9 ingest event standing.
- **Research (Director):** 18th-rule discipline at scope-prose layer
  caught (6th witness for 91st-CONFIRMED verify-not-assume at novel
  layer); 3 research drills in-flight.
- **USER:** correction acknowledged + folded; substrate-product framing
  must carry method-contingent qualifier going forward at all reports/
  scorecards.

Tag: DECISION_235b_P2_STEP_8_ratify_scope_AMENDED_method_contingent_NOT_fundamental_USER_correction_skunkworks_amendment_18th_rule_refuse_what_cant_prove_at_director_ratify_prose_layer_91st_CONFIRMED_6th_witness_novel_layer_GATE_F_envelope_OF_CURRENT_METHOD_OLS_Gram_resonator_N_4096_fixed_budget_6_60_residue_FPE_codebook_simplex_correlated_6_to_7_coprime_bases_untested_levers_larger_N_larger_budget_different_decoder_kymn_exact_wasserstein_sinkhorn_different_encoding_flagged_future_work_consumer_pull_DECISION_235c_P1_atom_framing_method_contingent_also_C1_break_THIS_encoding_NOT_fundamental_impossibility_DECISION_235d_director_drift_catch_discipline_observation_atom_prose_layer_inherits_method_contingent_scope_Testbed_STEP_9_fire_reactive_7_edge_DEPENDS_ON_kymn_ADD_endorsed_cert_owner_verdict_unchanged_scope_prose_sharpened_substrate_26300_to_26301_relations_5219_to_5226_cap_pres_1p0_axiom_term_206_206_methodology_FROZEN_24_fname_v2_compliant_86_chars

-- Research (Director)
