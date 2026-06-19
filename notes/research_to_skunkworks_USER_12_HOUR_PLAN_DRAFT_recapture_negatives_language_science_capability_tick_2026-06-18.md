# Research (Director) -> Skunkworks (cert-owner): USER DIRECTIVE 12-HOUR ALL-NIGHT PLAN DRAFT (~midnight to ~noon). 4 buckets: A=recapture-negatives remote heavy (8a phase-transition + refuse-gate learned-adapter NON-LLM + C1 entmax envelope + ARCH-B replicate) + B=language ingest (WordNet APPLY queued + text8/enwik8 fetch + 5-7 lit-scan drills) + C=science via Lean batch (3 more proofs Cauchy-Schwarz/triangle/parallelogram; USER bandwidth signal opens mathlib4 expansion) + D=general tick + cleanup. NO BUSY WORK guards explicit per all 6 USER-LOCKED rules. Standing for your AGREE/REFINE/ESCALATE before filing to USER for GO.

**From:** Research (DIRECTOR)
**To:** Skunkworks (cert-owner; VET on plan)
**Date:** 2026-06-18 ~01:00
**Re:** USER direct: "OK - let's build an all night, 12 hour plan. it should include remote experiments to bring up capabilities that have negatives, it should ingest language and science into the substrate, it should generally bring up all our capabilities a solid tick. coordinate with skunkworks on this" + USER follow-up "we have good bandwidth now so we can make use of that"
**fname_v2** 52 chars.

## USER directives (verbatim)

```
"OK - let's build an all night, 12 hour plan. it should include remote
 experiments to bring up capabilities that have negatives, it should
 ingest language and science into the substrate, it should generally
 bring up all our capabilities a solid tick. coordinate with skunkworks
 on this"

"we have good bandwidth now so we can make use of that"
```

Bandwidth signal = mathlib4 expansion + large corpus downloads + multiple Lean proofs in flight = in scope.

## BUCKET A: RECAPTURE THE NEGATIVES (remote heavy; 4 cells; ~6h staggered)

```
A1. 8a phase-transition regime sweep (FULL on remote GPU)
    Pre-reg HARD-PASS: non-monotone measured boundary with crossover
                       regime identified (where 8a separates)
    Pre-reg HARD-FAIL: uniformly negative across all swept regimes
    Pre-reg MIDDLE:    some regime separates, but not flagship 13.8x
    Sweep: T x N x sparsity x small-T-cold-start corner per Skunkworks
           condition; measured GPU wall-time (METHOD-GATE)
    Cost: ~2-3h GPU; structured provenance fields fleet-wide

A2. Refuse-gate learned-adapter NON-LLM (small parametric mapping)
    11th-rule explicit: NO LLM in invention loop -- a learned adapter
       = small parametric mapping (linear or shallow MLP; <10k params)
       trained via gradient descent on bge embeddings of q54-q65
       held-out; the ADAPTER is parametric, NOT an LLM-judge
    Pre-reg HARD-PASS: discriminates=True at any beta (in_cov > gap)
    Pre-reg HARD-FAIL: still NON_TEST (no discriminating regime)
    Pre-reg MIDDLE:    partial discrimination at one beta
    Cost: ~1h GPU + train/eval; use Action A bge cache (cleared)
    Composes with Skunkworks "T2 next-step hypothesis NOT cert-proven"
       framing: A2 IS that test

A3. C1 entmax envelope sweep (measured-bounds-config-contingent rule)
    Sweep: N {512, 1024, 2048, 4096} x cluster {4, 8, 16, 32} x noise
           {0.05, 0.10, 0.15, 0.20, 0.30}
    Pre-reg HARD-PASS: 8x cheaper holds across full envelope
    Pre-reg HARD-FAIL: collapses outside spread regime (only narrow
                       config works) -- envelope-claim falsified
    Pre-reg MIDDLE:    config-dependent (range of valid configs); state
                       the envelope explicitly per USER rule
    Cost: ~2-3h GPU; per-batch + envelope summary

A4. ARCH-B replicate at N=2048 (replicate-not-rely-on-single-config)
    Pre-reg HARD-PASS: SPARSITY_NEUTRAL replicates at N=2048
    Pre-reg HARD-FAIL: doesn't replicate (single-N artifact)
    Pre-reg MIDDLE:    partial replicate with caveats
    Cost: ~1h GPU
```

## BUCKET B: LANGUAGE INGESTION (laptop + light remote + research lane)

```
B1. WordNet APPLY 5k high-frequency noun synsets -> LEXICON atoms
    QUEUED FROM MORNING (Director + Skunkworks open questions answered
       earlier today: LEXICON kind + per-synset granularity + bears_on
       scope to math + sub_op atoms; no-algebra structural guard)
    Pre-reg HARD-PASS: 0 phantom edges + axiom_term 206/206 + cap_pres
       1.0 + AtomKind LEXICON populated; per-synset gloss + relations
       (hypernym/hyponym/meronym/holonym) within WordNet namespace
    Pre-reg HARD-FAIL: any structural-guard mutation (axiom_term mutated;
       cap_pres < 1.0; phantom edges introduced; algebra field set)
    Cost: ~2-4h on laptop (network bandwidth + DuckDB writes serial per
       gotcha discipline); per-batch fresh-load + os.replace-race retry

B2. text8 + enwik8 corpus fetch + light tokenization staging
    Tier-6 stays PAUSED (data-gated per USER directive); this is
       PREP only, not Tier-6 launch
    Fetch: text8 (~100MB) + enwik8 (~1GB) via mirror; no atomize
    Stage: token-level structural prep + corpus stats (char-LM scope
       per drill 3 substrate-novel finding); NO atomization
    Cost: bandwidth + ~1h prep; benefits Tier-6 future-resume

B3. STEP-B research lit-scan extension (5-7 focused drills via research
    lane / Sonnet sub-agents; Director-owned not other sessions)
    Drills (priority order per substrate-novel weak-spot signals):
       1. Spectral-gap codebook analysis (cleanup-memory-as-graph;
          held-out generalization predicted by spectral separation;
          drill 1 next-candidate)
       2. PCN-AM-on-VSA compositional generalization (drill 2 ZERO
          published papers = substrate-novel territory; deepen the
          ARCH-B nonlinear-readout lever)
       3. Char-LM HD/VSA scope details (drill 3 ZERO published =
          uncharted; ARCH-B nonlinear-readout bypasses real ceilings)
       4. PAWS-style hard-negative paraphrase adapted to VSA cleanup
          (drill 1 underexplored single-cell experiment T3 prediction)
       5. Scientific concept corpora landscape (what's available for
          structured-concept ingestion beyond WordNet -- BabelNet,
          ConceptNet, GeneOntology, etc.; lit-scan for substrate fit)
       6. Learned-adapter literature (for A2 cell pre-reg confidence;
          what works in associative-memory adapter training; non-LLM)
       7. (Optional) Discrete-vs-continuous adapter architectures
          for VSA representation rescaling
    Discipline: SAFE generic queries per loop SAFETY block + 11th-rule
       clean (factual retrieval not LLM-judge); evidence-of-search +
       ASCII + auto-save to notes/
    Output: T2/T3 RESEARCH_FINDING atoms via STEP-B atomize cron
    Cost: ~2h parallel (sub-agent concurrent dispatch); ~5-7 RF atoms
```

## BUCKET C: SCIENCE INGESTION via Lean (USER bandwidth = mathlib4 enabled)

```
C1. Cauchy-Schwarz inequality (real inner product space)
    Theorem: |<u,v>| <= ||u|| * ||v||
    Lean: rely on mathlib4 inner_mul_le_norm; in PythagorasIpV1 project
    Skunkworks SEMANTICS-MATCH VET: exact-R + exact-not-approximate
       (real-bound not complex)
    -> +1 T0_PROVEN_FORMAL atom (31305 -> 31306 on cron pickup)
    Cost: ~30 min build + 30 min VET

C2. Triangle inequality (real inner product space)
    Theorem: ||u + v|| <= ||u|| + ||v||
    Lean: mathlib4 norm_add_le
    Skunkworks SEMANTICS-MATCH VET: same exact-R framing
    -> +1 T0_PROVEN_FORMAL atom

C3. Parallelogram identity (real inner product space)
    Theorem: ||u + v||^2 + ||u - v||^2 = 2*(||u||^2 + ||v||^2)
    Lean: build from norm_add_sq_real + norm_sub_sq + ring
    Skunkworks SEMANTICS-MATCH VET: same exact-R framing
    -> +1 T0_PROVEN_FORMAL atom

These are PHASE II BATCH (additional proofs in existing
   PythagorasIpV1/ project); NOT PHASE III (production lean_oracle
   infrastructure = USER architectural decision; ESCALATE preserved
   for full PHASE III when USER bandwidth signals).

Each requires Skunkworks SEMANTICS-MATCH VET cycle (the discipline
   already running). Cost per: ~30 min build + 30 min VET = ~3h total.
```

## BUCKET D: GENERAL CAPABILITY TICK + cleanup

```
D1. T0_PROVEN_FORMAL atom landing (Skunkworks A/B/C path executed)
    First atom (PHASE II Pythagoras-IP cert): 31304 -> 31305
    Subsequent atoms (Bucket C C1+C2+C3): 31305 -> 31308
    AtomKind populated 16 -> 17 of 23 on first; methodology rule
       RULE_M_LEAN_semantics_match already ratified

D2. Testbed VERIFY-THE-REFERENT parent + A1/A2/A4 gated-ratify
    AUDIT_LESSON Store: 43 -> ~48 on chain ratify
    (pending from earlier; cleanup)

D3. Action A bge-index-refresh full coverage VET cleanup
    Joint Skunkworks indexed + Testbed atom invariant verify
    On next hd_metrics_sync cycle (autonomous 20-min)

D4. Brief refresh DELIVERY (morning USER consumption when USER ready)
    DRAFT already consolidates 9 cert-owner self-catches + PHASE II
       VET PASS + 2 cert-grade + 2 honest-negatives + substrate state

D5. Heartbeat + memory + Director session-arc commit before compaction
```

## SUBSTRATE GROWTH TARGET by end of 12h

```
atoms:               31304 -> ~31360+ (+~55 conservative:
                       4 T0_PROVEN_FORMAL (1 Pythagoras + 3 Bucket C)
                       + 5-7 RF atoms (Bucket B3)
                       + 5000 LEXICON atoms (Bucket B1 WordNet 5k)
                       + 4 EXPERIMENT_RECORD (Bucket A cells A1-A4)
                       + ~5 AUDIT_LESSON (Bucket D2 chain ratify))
                       = +~5020 (mostly WordNet LEXICON)
                       
                       Note: WordNet 5k synsets may be batched into
                       fewer "container" LEXICON atoms or 1-atom-per-
                       synset; per-synset granularity per earlier
                       open-question answer -- so ~5000 individual
                       LEXICON atoms is the target. Standing on
                       Skunkworks confirm per-synset still preferred.

CERT_CHAIN_GRADE:    563 -> 564+ (any Bucket A cells that recapture-
                       positive land cert-grade; conservative target
                       563 -> 564 from A4 ARCH-B replicate, possibly
                       +1 from A3 entmax envelope HARD-PASS)
AUDIT_LESSON:        43 -> ~48-50 (chain ratify + Bucket B3 drill
                       insights becoming candidates)
T0_PROVEN_FORMAL:    0 -> 4 (PHASE II + Bucket C)
AtomKind populated:  16 -> 17-18 of 23 (T0_PROVEN_FORMAL + LEXICON
                       if not already)
axiom_term:          206/206 PRESERVED (HARD-FAIL gate)
cap_pres:            1.0 PRESERVED (HARD-FAIL gate)
methodology:         FROZEN-24 + 8 PHASE-2 UNCHANGED
```

## NO BUSY WORK GUARDS (per USER-LOCKED rules)

```
1. NO BUSY WORK (USER 2026-06-17 evening):
   - Every bucket has scarce-resource advance (GPU runs, USER decision,
     atom growth, ratify queue progress); no make-work-disguised-as-
     preparation
2. SINGLE-SESSION DISPATCH (USER 2026-06-17 evening):
   - Each bucket items have explicit single owner; no ambiguous
     parallel; no Director-timer-automated fallback
3. CHECK WITH CERT-OWNER (USER 2026-06-17 evening):
   - This plan is being VET'd by Skunkworks BEFORE USER sees the GO
4. SUBSTRATE-BUILD = atomizing (USER 2026-06-17 evening):
   - +~55-5025 atoms target; not process work
5. NEGATIVITY-BIAS symmetric (USER 2026-06-17):
   - Pre-reg HARD-PASS + HARD-FAIL + MIDDLE-BAND bands sacrosanct
     both directions; honest-negatives counted as cert-grade outcome
6. NO LLM in invention loop (USER 11th rule):
   - Refuse-gate learned-adapter A2 is small parametric mapping
     <10k params trained by gradient descent on bge embeddings;
     the ADAPTER is parametric NOT LLM-judge; lit-scan drills are
     factual retrieval not LLM-judge
7. Remote-for-heavy compute policy (USER 2026-06-16):
   - Bucket A (4 GPU cells) on REMOTE; Bucket B1 WordNet on laptop;
     Bucket C Lean builds on laptop (proof type-checking fast); B2
     fetch leverages bandwidth window
8. Measured-bounds-config-contingent (USER 2026-06-16):
   - A3 entmax envelope sweep IS that discipline applied
9. 18th-rule refuse-what-can't-prove (USER):
   - Learned-adapter "needs" framing scoped to T2 hypothesis per
     Skunkworks's lock; A2 either proves or doesn't
10. VERIFY-THE-REFERENT (today's meta-discipline):
    - Field-check provenance on all Bucket A results via fleet-wide
      provenance_fields helper (already shipped fcb4abd5)
```

## SESSIONS / COORDINATION

```
Director (me):     research lane Sonnet drills B3 (5-7 parallel) +
                   brief refresh refinements as morning approaches +
                   coordination + USER touchpoints
Skunkworks:        VET this plan AGREE/REFINE/ESCALATE; SEMANTICS-MATCH
                   VETs for Bucket C Lean proofs (3 cycles); cert-
                   condition pre-regs for A1-A4 cells; SCHEMA-VET on
                   T0_PROVEN_FORMAL atomize script (Skunkworks-picked
                   path A/B/C); ongoing E1/E4/E5 substrate-eval
Exp-Dev:           cell-author A1-A4 (4 recapture-the-negatives cells);
                   use shared provenance_fields helper; pre-reg in cell
                   metadata
Testbed:           VERIFY-THE-REFERENT parent + A1/A2/A4 ratify;
                   invariant-verify on T0_PROVEN_FORMAL atoms (4 over
                   the 12h); WordNet B1 structural-guard verify
Orchestrator:      dispatch refused_gate-style for A1-A4; T0_PROVEN_
                   FORMAL atomize cron creation per Skunkworks path;
                   in-flight progress notes per imperative (>15min);
                   manifest pipeline; Lean lake builds for Bucket C
USER:              GO post-Skunkworks VET; PHASE III architectural
                   decision (ESCALATE; can defer past this plan)
```

## What I'm NOT including (DELIBERATELY OMITTED)

```
- PHASE III production lean_oracle infrastructure: USER-architectural;
  ESCALATE preserved; not in 12h window without USER signal
- 13.8x flagship recapture (the original SMW launch-overhead claim):
  stays downgraded; learned-adapter A2 is the next legitimate test
- Tier-6 char-LM full launch: data-gated; B2 staging only
- 8b cell redesign: lower-priority per evening arc; A1 8a sweep is
  more directly load-bearing
- ARM-3 Option C: KEEP DEFERRED low-priority (carryover)
- USER E4 #13 scope decision: deferred (carryover)
```

## STANDING / who I'm waiting on (9th rule)

- **Skunkworks (cert-owner; SOLE on plan VET):** AGREE/REFINE/ESCALATE
  ruling on this 12h plan; cert-condition pre-regs for A1-A4 once plan
  ratified; path A/B/C signal for T0_PROVEN_FORMAL atomize (separately
  filed earlier); brief response format per CHECK-WITH-CERT-OWNER
- **USER:** GO signal post-Skunkworks-VET; specific REDIRECTS on any
  bucket I've mis-scoped (priorities, NO BUSY WORK calls, NEGATIVITY-
  BIAS catches)
- **Other sessions:** standing for plan ratify before dispatch; once
  USER GO + Skunkworks-VET PASS + cert-condition pre-regs from
  Skunkworks land, Director dispatches per bucket
- **Director (me):** plan DRAFT filed; standing for Skunkworks VET +
  USER GO; in the meantime, brief refresh refinements + monitor
  reactive chain firings

Tag: USER_directed_12_hour_plan_draft_recapture_negatives_remote_heavy_a1_a2_a3_a4_8a_phase_transition_sweep_refuse_gate_learned_adapter_non_llm_c1_entmax_envelope_arch_b_replicate_language_ingest_b1_wordnet_5k_synsets_b2_text8_enwik8_stage_b3_5_7_drills_spectral_pcn_am_char_lm_paws_science_corpora_learned_adapter_lit_science_lean_batch_c1_cauchy_schwarz_c2_triangle_inequality_c3_parallelogram_identity_t0_proven_formal_general_tick_d1_atom_landing_d2_verify_referent_ratify_d3_action_a_coverage_d4_brief_delivery_d5_memory_substrate_growth_target_31304_31360_4_t0_proven_formal_5_7_rf_5000_lexicon_4_experiment_record_5_audit_lesson_cert_chain_grade_563_564_audit_lesson_43_48_atomkind_16_17_18_axiom_term_206_preserved_cap_pres_1_methodology_frozen_24_no_busy_work_guards_no_busy_work_single_session_dispatch_check_cert_owner_substrate_build_negativity_bias_no_llm_invention_remote_heavy_measured_bounds_config_18th_rule_verify_referent_sessions_director_research_drills_skunkworks_vet_semantics_match_atomize_path_exp_dev_cells_a1_a4_testbed_verify_referent_invariant_orchestrator_dispatch_cron_progress_notes_user_go_phase_iii_escalate_omitted_phase_iii_138x_tier_6_full_8b_redesign_arm_3_e4_13_skunkworks_vet_user_go_post_vet_other_sessions_dispatch_post_ratify_director_brief_refresh_monitor_reactive_fname_v2_52

-- Research (Director); DRAFT for Skunkworks VET cycle
