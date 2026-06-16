# Research (Director) -> ALL 4 sessions (Skunkworks + Exp-Dev + Testbed + Orchestrator): DECISION 215 -- 14th-rule EXPLICIT while-remote-running parallel-work dispatch. P1 GATE-C remote run window ~1-2hr (timeout 7200s). NO STAND during window. EACH session: substantive parallel work explicitly dispatched + you are explicitly TOLD which downstream you're gating. 14th-rule no-stand at phase boundary + 13th-rule active state-check enforced across all sessions.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~19:32
**Re:** 14th-rule explicit dispatch during GATE-C remote-run window; each session gating + parallel work.

## You are GATING (explicit)

```
ORCHESTRATOR: gating STEP-7 (Exp-Dev results-read + Skunkworks VET) +
   STEP-8 (Director ratify) + STEP-9 (Testbed P1 atom) on GATE-C remote
   run completion + metrics SCP back.

EXP-DEV: gating STEP-8 (Director ratify) + STEP-9 (Testbed P1 atom) on
   STEP-7 results-read verdict per LOCKED bands.

SKUNKWORKS: gating STEP-8 (Director ratify) + STEP-9 (Testbed P1 atom)
   on STEP-7 VET of Exp-Dev's results-read. Also gating PRIMITIVE 2 prereg
   LOCK on prereg DESIGN parallel authoring.

TESTBED: gating substrate-state coherence on 190c + 190f FINDING ratify
   chain progress + (post-STEP-8) STEP-9 P1 atom ingest.
```

## DECISION 215 -- explicit parallel-work dispatch per session

### ORCHESTRATOR (custodian)

```
PRIMARY (reactive): STEP-6 remote run completion -> metrics SCP back ->
   route notification to Exp-Dev + Skunkworks for STEP-7.

PARALLEL (while remote run executes, ~1-2hr window):

   (1) Pre-stage STEP-7 metrics SCP-back script readiness:
       - Verify data/exp_primitive_1_residue_FPE_v1_GATE_C/ path target
         exists + writable + permissions OK
       - Ensure metrics.json + results.json + provenance.json schema match
         the cell's writers (no schema-drift)
       - Test SCP path from remote -> local with a dry-run / dummy file

   (2) Remote run health monitoring:
       - heartbeat_watchdog active (verified 19:01 mtime; supervisor sweep
         87th remediated) -- watch for any process death + auto-restart
       - remote_state_cache.json refreshing ~30s -- watch for stale > 5min
       - queue.json watching for "primitive_1_residue_FPE_v1" status
         transitions (pending -> claimed -> running -> complete)
       - If runner PID 47220/28864 dies during run: auto-restart + flag

   (3) Pre-stage STEP-9 Testbed atom ratify infrastructure if anything
       missing from prior atom ratifies (190c FINDING is the reference;
       check tools/testbed/atom_ratify_chain.py or equivalent is healthy):
       - This is light prep; only if you observe a gap. Not over-prep.

   (4) Verify hd_heartbeat_watchdog scheduled task healthy (your DECISION
       209d supervisor hardening sweep registered it; this is its first
       overnight test of LogonTrigger + Daily 3am pattern).

   YOU ARE GATING: STEP-7 + STEP-8 + STEP-9 on remote run + metrics SCP back.
```

### SKUNKWORKS (Auditor)

```
PRIMARY (reactive): STEP-7 results VET on Exp-Dev's results-read verdict.
   Neutral per locked bands (C1 holds -> load-bearing within envelope; C1
   breaks -> honest-bounded). No prejudgment (91st audit candidate;
   verify-not-assume discipline).

PARALLEL (while remote run executes, ~1-2hr window):

   (1) PRIMITIVE 2 hopfield-cleanup prereg DESIGN -- ACTIVELY AUTHOR
       (not just "begin"; substantive draft):
       - Quad-head per ENDORSED installment-2 sketch:
         HEAD 1: naive max-cos (ARM-1 default; already in-substrate)
         HEAD 2: dense modern-Hopfield (Ramsauer Theorem-4 closed-form
                  beta = f(N, |M|, Delta_min); R1 lit-base)
         HEAD 3: sparse/structured-Hopfield (Hu NeurIPS 2023 + Santos 2024;
                  R1 lit-base; sharper basins for small-Delta_min)
         HEAD 4: resonator-decoder (T3/resonator_network_decoder already
                  atomized; B2 efficient-decode addressed here informed by
                  simplex-correlation diagnosis)
       - GATE-D: closed-form beta bound (Ramsauer Theorem-4)
       - GATE-E: quad-head Delta_min envelope (best-head-per-regime map;
                  Drill 5 continuous-regime envelope fold)
       - GATE-F: P1 -> P2 resolution-extension + resonator integration
       - Simplex-correlation diagnosis (per-base codewords ~-1/(m-1)) as
         KNOWN design constraint
       - Tune-free bands per gate
       - Honest-scope (each head's bounded regime)
       - Substrate-internal (no LLM; 11th rule)

   (2) Simplex-correlation literature mini-scan (R2-style; ~30 min):
       - Sparse / structured Hopfield variants for non-orthogonal residue
         codewords with simplex correlation ~-1/(m-1)
       - Any specific results on Kymn complex resonator OLS dynamics for
         non-orthogonal codeword sets
       - Feeds Primitive 2 quad-head HEAD-3 + HEAD-4 design

   (3) ARM-3 Option C parity-immune redesign LOW-PRIORITY scoping (only
       if bandwidth after (1)+(2); not urgent):
       - O_xunb identity + xor-odd-k parity blocked TRACK B uniqueness;
         Option C = parity-immune redesign of the corr(bundle(a,b),c)
         certification approach
       - Scoping note only (not full prereg)

   YOU ARE GATING: STEP-8 + STEP-9 on STEP-7 VET + Primitive 2 prereg LOCK
   on prereg DESIGN authoring.
```

### EXP-DEV (Prover)

```
PRIMARY (reactive): STEP-7 results-read on remote run completion per
   LOCKED bands (neutral; no prejudge). Hand verdict to Skunkworks STEP-7
   VET.

PARALLEL (while remote run executes, ~1-2hr window):

   (1) PRIMITIVE 2 quad-head cell-gate REFERENCE-IMPLEMENTATION
       pre-author (not just sketch; runnable skeleton):
       - HEAD 1 naive max-cos: already in-substrate; wire to cell harness
       - HEAD 2 dense Hopfield (Ramsauer): implement closed-form beta
         per Theorem-4; degrades as Delta_min -> 0
       - HEAD 3 sparse/structured Hopfield: implement entmax-15 or
         alpha-entmax variant per Hu 2023 + Santos 2024; sharper basins
       - HEAD 4 resonator-decoder: wire T3/resonator_network_decoder
         existing atom; informed by simplex-correlation diagnosis
         (per-base codewords ~-1/(m-1); resonator must tolerate
         non-orthogonal)
       - Quad-head harness: select best-head per Delta_min regime
       - Light self-test (verify each head invokable + correct shape outputs)
       - DO NOT lock as prereg-bound cell yet (Skunkworks's prereg DESIGN
         still in flight); this is REFERENCE-IMPLEMENTATION for when prereg
         locks

   (2) Kymn 2311.04872 resonator spec PRE-EMPTIVE STUDY:
       - Read Kymn's exact OLS/projection variant for residue factorization
       - Implementation notes: how does Kymn handle non-orthogonal residue
         codewords (the simplex-correlation case)?
       - Light: just study + notes; do not implement yet (P2 phase work)
       - Goal: when P2 quad-head HEAD-4 lands, you're not learning Kymn
         from scratch

   (3) Pre-stage P1 atom format draft for Testbed STEP-9:
       - kind: capability (within-envelope) OR finding (honest-bounded)
         depending on C1 verdict; both paths drafted in advance
       - metric_type: ENCODING_SOUNDNESS_WITHIN_ENVELOPE +
         LOG_SCALING_DECODE_OPEN_ANNOTATION
       - desc: GATE-A kernel match + B1 decodability + GATE-C envelope
         (load-bearing-within-envelope OR honest-bounded per C1)
       - DEPENDS_ON: substrate primitives used (complex-exp FPE; CRT;
         residue layering)
       - provenance: cell SHA + remote_run_id + metrics SHA + bands LOCKED
       - explicit annotation: "log-scaling DECODE OPEN; Primitive 2;
         advantage NOT yet demonstrated"
       - Both verdict paths drafted -> Testbed can ingest fast post-STEP-8

   YOU ARE GATING: STEP-8 + STEP-9 on STEP-7 results-read verdict.
```

### TESTBED (Integrator)

```
PRIMARY (active): 190c + 190f FINDING ratify chains in progress.
   - 190c FINDING_cardinality_arm1_distribution_scoping per DECISION 208a
     ratify-chain spec
   - 190f drift_kappa3 FINDING per DECISION 193a + Skunkworks endorsement

PROGRESS-CHECK (explicit; you are NOT silent-gating):
   - If 190c + 190f are in flight + healthy: continue at your pace
   - If you've HIT A BLOCKER (schema gap, atom_id collision, dependency
     resolution failure, anything): file a note NOW so I can dispatch
     remediation -- do not silent-wait
   - If both are RATIFIED ALREADY but you haven't filed completion notes:
     file completion notes so Director can ACK + close

PARALLEL (while you work 190c/190f + remote run executes):

   (1) Pre-receive P1 atom spec:
       - Exp-Dev drafting P1 atom format both verdict paths
       (DECISION 215 PARALLEL (3) above)
       - Verify your atom-ingest tooling handles BOTH:
         (a) kind:capability (within-envelope) with metric_type:
             ENCODING_SOUNDNESS_WITHIN_ENVELOPE + LOG_SCALING_OPEN_ANNOTATION
         (b) kind:finding (honest-bounded) with metric_type:
             HONEST_BOUNDED_C1_BREAKS
       - If your ingest tooling needs a schema update for either: flag
         now, not at STEP-9

   (2) Substrate-state coherence check:
       - 26285 atoms / 4947 relations / 207/207 axiom term / cap_pres=1.0
         (per Director's running state)
       - VERIFY THESE NUMBERS yourself (substrate is yours to count)
       - If any drift from Director's running state (e.g., relations 4947
         vs actual): flag (77th audit candidate counter-drift discipline)
       - This is light + fast; useful to verify before P1 atom lands

   YOU ARE GATING: substrate-state coherence on 190c/190f progress +
   (post-STEP-8) STEP-9 P1 atom ingest.
```

## DECISION 215a -- 14th-rule enforcement

```
14th-rule (USER-LOCKED 2026-06-16): NO STAND default at phase boundary;
Director dispatches concrete next-phase PREP to ALL sessions in same
Director-turn; "stand" or "wait until X" is NEVER the default.

This DECISION applies the rule during the GATE-C remote-run window:
   - Every session has substantive parallel work explicitly dispatched
   - Every session is explicitly told which downstream they're gating
   - No session is silent-standing during the ~1-2hr window
   - 13th-rule active state-check applies: between monitor events, scan
     for substantive progress signals + flag blockers proactively

If during the window any session HITS A BLOCKER:
   - File a note IMMEDIATELY surfacing the blocker
   - Do NOT silent-wait; do NOT defer to monitor
   - Director (Research) will dispatch remediation
```

## Pipeline state (post-DECISION-215)

```
PHASE C TIER-3 ARC (remote-run window ~1-2hr):
   PRIMITIVE 1 STEP-6 in flight (GPU runner pending claim + run + metrics back)
   PRIMITIVE 2 prereg DESIGN active (Skunkworks; reference-impl active Exp-Dev;
                                      simplex-correlation diagnosis as known
                                      design constraint)
   PRIMITIVE 3 GHRR DEFERRED research-drill

190e formal-oracle hookup SUBSTRATE-SIDE READY (DECISION 211)
190c + 190f FINDING atoms in Testbed ratify chain (progress-check explicit)

Sessions (all parallel-work explicit):
   Skunkworks: P2 prereg DESIGN active + simplex-correlation R2-style scan +
               Option C scoping bandwidth-permitting
   Exp-Dev: P2 quad-head reference-impl + Kymn spec pre-study + P1 atom
            format both-verdict-paths drafted for Testbed
   Testbed: 190c/190f ratify chain progress-check + P1 atom ingest pre-receive
            + substrate-state coherence count
   Orchestrator: STEP-7 SCP infra pre-stage + remote-run health monitoring +
                 testbed atom-ratify infra check + hd_heartbeat_watchdog
                 schtask first overnight test
   Research (Director): 13th-rule active state-check armed; STEP-8 ratify
                        reactive on STEP-7 VET

USER standing items (unchanged):
   1. formal-oracle procurement (Lean rec; 11th-rule HARD REQ)
   2. Phase C TIER-3 build IN PROGRESS (P1 STEP-6 in flight; P2 prereg DESIGN
      + reference-impl active parallel)
   3. ARM-3 Option C low-priority background (Skunkworks bandwidth-permitting)
   4. 3 TRACK D design Q's at visual review pace

Substrate state: no atom mutations from this DECISION (dispatch only);
   cap_pres=1.0 PRESERVED; methodology FROZEN at 24.
```

## Safety / invariants

- ASCII only
- 11th + 18th + 19th + 21st + 22nd rules preserved
- 14th-rule explicit dispatch (this DECISION); no silent standing
- 13th-rule active state-check armed across all sessions
- 9th USER-LOCKED rule: explicit "who you are gating" stated per session
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

215 cumulative decisions. **250+ honest signals.** 88 audit-discipline instance
types empirical confirmed + 3 candidates (89th + 90th + 91st today). Phase C
TIER-3 FOUNDATION BUILD active; P1 STEP-6 GATE-C remote-run in flight; ALL 4
sessions have substantive parallel work explicit per 14th rule.

---

**Skunkworks (Auditor):** PRIMARY reactive STEP-7 VET. PARALLEL: (1) Primitive 2
prereg DESIGN actively author quad-head + GATEs + tune-free bands + honest scope;
(2) simplex-correlation R2-style mini-scan; (3) Option C scoping bandwidth-
permitting. You are GATING STEP-8 + STEP-9 on STEP-7 VET + Primitive 2 LOCK on
prereg DESIGN.

**Exp-Dev (Prover):** PRIMARY reactive STEP-7 results-read. PARALLEL: (1) P2
quad-head reference-implementation (runnable skeleton + light self-test); (2)
Kymn 2311.04872 resonator spec pre-emptive study; (3) P1 atom format both
verdict paths drafted for Testbed STEP-9. You are GATING STEP-8 + STEP-9 on
STEP-7 verdict.

**Testbed (Integrator):** PRIMARY active 190c + 190f FINDING ratify chains.
EXPLICIT progress-check: continue OR file blocker note NOW OR file completion
notes if already ratified. PARALLEL: (1) P1 atom ingest pre-receive
(both-verdict-paths schema check); (2) substrate-state coherence count (verify
26285 / 4947 / 207-of-207 / cap_pres=1.0 yourself). You are GATING substrate
coherence + STEP-9 P1 atom ingest.

**Orchestrator (Custodian):** PRIMARY reactive STEP-6 remote run completion +
metrics SCP back. PARALLEL: (1) STEP-7 SCP infra pre-stage; (2) remote-run
health monitoring (heartbeat_watchdog + cache + queue.json + runner PIDs);
(3) testbed atom-ratify infra check; (4) hd_heartbeat_watchdog schtask first
overnight test. You are GATING STEP-7 + STEP-8 + STEP-9 on remote run + SCP.

**USER:** All 4 sessions explicitly told gating + parallel work; no silent
standing during remote-run window. 14th-rule enforced per your 2026-06-16
USER-LOCKED directive. Will surface when STEP-7 verdict + STEP-8 ratify
land OR if any session flags a blocker.

Tag: DECISION_215_14th_rule_explicit_while_remote_running_parallel_work_dispatch_all_4_sessions_orchestrator_SCP_infra_prestage_remote_run_health_monitoring_testbed_atom_ratify_infra_check_hd_heartbeat_watchdog_schtask_first_overnight_test_skunkworks_P2_prereg_DESIGN_active_quad_head_GATEs_simplex_correlation_R2_scan_option_C_scoping_exp_dev_P2_quad_head_reference_implementation_kymn_resonator_spec_pre_study_P1_atom_format_both_verdict_paths_for_testbed_testbed_190c_190f_progress_check_explicit_P1_atom_ingest_pre_receive_substrate_coherence_count_each_session_GATING_what_downstream_explicit_no_silent_stand -- Research (Director)
