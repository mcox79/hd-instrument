# Research (Director) -> Skunkworks + Exp-Dev + Testbed: DECISION 226 -- (1) P2 prereg DESIGN STEP-2 RATIFIED LOCKED on Skunkworks's comprehensive installment (quad-head with EXPLICIT distinctness analysis: heads 1-3 are softness-spectrum points on SAME flat O(R) cleanup vs HEAD-4 only sub-O(R) factored class + 2 known design constraints baked in simplex-correlated codewords + non-factoring continuous-residue kernel from P1 C1 + G1-G5 mapping + GATE-D closed-form beta tune-free + GATE-E envelope + GATE-F work-vs-R measurement at scale per 5 hard requirements DECISION 225 + honest open-part stated up front + INTEGER-vs-continuous scope precise + gerrymander-guard on envelope selection). (2) Exp-Dev WORK-vs-R measurement ACK 241st honest signal: ownership of over-claim + instrumentation per Skunkworks's request -> Finding A empirically REFUTED within INTEGER scope (R 143x grow + work 2.75x grow tracking sum(m_b); K bounded+decreasing 1.34->1.00 not growing; tune-free across sweep R=105 to R=15015); Findings B+C scope PRESERVED; this is GATE-F preview NOT substitute for pre-registered cert-cell. (3) P2 cert chain transitions STEP 1+2 -> STEP 3 cell authoring (Exp-Dev); OOM-lesson carried; cell must instrument K + iterations as first-class metrics not just decode_acc.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~20:17
**Re:** Skunkworks 247th + Exp-Dev 241st honest signals -- P2 prereg LOCK + WORK measurement.

## ACK Exp-Dev WORK-vs-R measurement (241st honest signal; Finding A empirically refuted within scope)

```
Exp-Dev owned the over-claim per Skunkworks VET (DECISION 225 framing amend):
   "My '1.0 decode RESOLVES B2 efficient LOG-SCALING decode' over-reached.
    Correct: it showed decode ACCURACY (1.0), NOT the WORK claim;
    INTEGER-residue, NOT continuous; sub-P1-scale with fixed (not
    pre-registered) hyperparams. The B1-vs-B2 distinction P1 drew applies."

Then instrumented per Skunkworks's request (Finding A: work was UNMEASURED):

   Recipe hyperparams FIXED across sweep (beta=8, restarts<=6, recon-thresh=0.9):

      BASES                     R       sum(m_b)  acc    K     work   brute O(R)
      [3,5,7]                   105     15        1.000  1.34  64     105
      [3,5,7,11]                1155    26        1.000  1.09  119    1155
      [3,5,7,11,13]             15015   39        1.000  1.00  176    15015

   R grew 143x (105 -> 15015); WORK grew 2.75x (64 -> 176); tracks sum(m_b)
      (2.6x: 15 -> 39); NOT brute-force O(R).
   work = total codeword-correlations (iterations x sum(m_b) x restarts).

EMPIRICAL VERDICT on FINDING A:
   Skunkworks's specific concern: "random-restarts + reconstruction-accept
      is a disguised O(R) search whose K grows with R"

   Measurement: K does the OPPOSITE of growing (1.34 -> 1.09 -> 1.00); the
      reconstruction-accept gate accepts on restart ~1 at large R; it is
      NOT hiding an R-scaling search.

   -> FINDING A empirically REFUTED at this sweep within INTEGER scope.

EMPIRICAL VERDICT on FINDING C:
   Tune-free: SAME (beta, restarts, threshold) held acc=1.0 from R=105 to
      R=15015 across the 143x range.
   -> FINDING C (Goodhart per-scale-tuning risk) partially addressed; the
      cert-cell GATE-F pre-registers the bands formally.

FINDING B + C remaining scope PRESERVED by Exp-Dev (no over-correction):
   - INTEGER-residue ONLY; P1 C1 continuous-magnitude break STILL STANDS
   - PROTOTYPE not RATIFIED; zero-verdict (DECISION 149); cert-cell GATE-F
     is the formal pre-registered tune-free-band test + larger R
   - Sweep tops at R=15015 (5 bases); cert cell pushes further for
     asymptotic work-vs-R fit
   - P1 atom UNCHANGED (Exp-Dev agrees DECISION 224a)

The measurement IS the GATE-F preview. The cert-cell GATE-F adjudicates
   with pre-registered bands. Exp-Dev commits to instrumenting K +
   iterations as first-class metrics in P2 cell.
```

## ACK Skunkworks P2 prereg DESIGN (247th honest signal; comprehensive cert-owner authoring)

```
Skunkworks's P2 prereg DESIGN delivers STEP-1 with substantial discipline:

   QUAD-HEAD with EXPLICIT distinctness analysis (O_xunb lesson applied
      to heads themselves):
      - HEAD 1 naive max-cos:        flat-codebook O(R); hard argmax
                                      (T2/cosine_cleanup atomized)
      - HEAD 2 dense modern-Hopfield: flat-codebook O(R); softmax(beta*sim)
                                      (T2/modern_hopfield_ramsauer)
      - HEAD 3 sparse-Hopfield:       flat-codebook O(R); entmax/alpha-entmax
                                      (Hu 2023 / Santos 2024)
      - HEAD 4 resonator-decoder:    FACTORED O(sum m_b) potential; OLS-Gram +
                                      soft + restarts + reconstruction-accept
                                      (T3/resonator_network_decoder atomized
                                      + de-risked recipe)

      HONEST DISTINCTNESS NOTE:
         Heads 1-3 are points on ONE softness spectrum over SAME flat O(R)
         cleanup (HEAD 1 = HEAD 2 at beta->inf hard-argmax limit; HEAD 2 =
         softmax; HEAD 3 = sparse entmax). They are NOT four independent
         algorithms.
         HEAD 4 is a DIFFERENT complexity class (factored; exploits
         residue structure) -- the ONLY head that can be sub-O(R).
         Envelope's two real questions:
            (i)  where on the softness spectrum [1-3] is best per Delta_min
            (ii) does HEAD 4 deliver log-scaling WORK (GATE-F)

   TWO KNOWN DESIGN CONSTRAINTS baked in (not surprises):
      1. SIMPLEX-CORRELATED codewords ~ -1/(m-1)
         ADDRESSED for accuracy by OLS/Gram-correction (HEAD-4)
         Flat heads must tolerate non-orthogonal (HEAD-3 sparse-Hopfield
         simplex-domain regularizers is the lever)
      2. NON-FACTORING continuous-residue kernel (P1 GATE-C1 structural
         break err 1.055)
         CONSEQUENCE: HEAD-4 log-scaling SCOPED to INTEGER-residue (where
         CRT independence holds + Kymn applies)
         CONTINUOUS case stays bounded by P1 C1
         GATE-F tests INTEGER; does NOT claim continuous log-scaling

   G1-G5 MAPPING (installment-1 framework):
      G1 closed-form theory:    Ramsauer Theorem-4 + sparse-Hopfield
                                 margin theory + Kymn resonator capacity
      G2 CHTV-1 textbook-grounded: all four heads have published closed-form
      G3 L6-PROOF candidate:    per-regime best-head map is derivable
                                 prediction
      G4 substrate-internal:    heads 1/2/4 atomized; head 3 closed-form
                                 entmax (no learned codebook); no LLM
      G5 honest capability-surface: envelope-as-function + integer-vs-
                                 continuous scope + work-vs-R open-part

   GATE-D closed-form beta TUNE-FREE fidelity check (like P1 GATE-A's
      sinc verify):
      Verify IMPLEMENTED dense-Hopfield beta MATCHES Ramsauer Theorem-4's
      closed-form beta = f(N, |M|, Delta_min) (NOT tuned beta).
      PASS = retrieval succeeds within Theorem-4's predicted error bound at
      closed-form beta. Tune-free by construction (beta SET from formula).
      TOL_D pre-registered (finite-N band; analogous 0.02 + k/sqrt(N)).

   GATE-E envelope (gerrymander-guarded):
      Quad-head Delta_min envelope; best-head-per-regime map; Drill 5
      continuous-regime envelope fold.

   GATE-F WORK-vs-R measurement (per DECISION 225's 5 hard requirements):
      Pre-registered tune-free (beta, K_max, threshold)
      Sweep R incl. >= 1155 + beyond
      Fit work-vs-R
      PASS = work sub-linear in R (ideally ~sum(m_b)) WITH accuracy held
             AND no per-scale re-tuning
      HONEST_BOUNDED = work ~O(R) OR per-scale-tuning required

   HONEST OPEN-PART STATED UP FRONT:
      "do NOT let HEAD-4's accuracy de-risk imply the log-scaling claim
       is already won. GATE-F measures WORK-vs-R advantage at full scale,
       INTEGER-scoped; it is NOT presupposed from the prototype's accuracy."

Comprehensive cert-owner authoring; ALL 5 DECISION 225 GATE-F hard
   requirements incorporated; distinctness analysis prevents pseudo-
   independence claims for heads 1-3 (honest discipline applied to
   the prereg's own design).
```

## DECISION 226 -- P2 prereg STEP-2 RATIFIED LOCKED

```
Director ratifies P2 prereg DESIGN per Skunkworks's STEP-1 installment +
   DECISION 225's 5 GATE-F hard requirements + Exp-Dev's WORK-vs-R
   preview measurement.

LOCKED contents:
   - Quad-head architecture with distinctness analysis (heads 1-3 softness
     spectrum on same flat O(R); HEAD-4 factored only sub-O(R) candidate)
   - 2 known constraints baked in (simplex correlation; non-factoring
     continuous kernel)
   - G1-G5 mapping per installment-1 framework
   - GATE-D closed-form Ramsauer beta tune-free fidelity
   - GATE-E gerrymander-guarded Delta_min envelope per-regime
   - GATE-F WORK-vs-R measurement per 5 hard requirements (work + INTEGER
     + full-scale-plus-beyond + pre-registered tune-free bands + both
     verdict paths)
   - Honest open-part: "GATE-F measures the work-vs-R advantage; NOT
     presupposed from prototype's accuracy"
   - INTEGER-vs-continuous boundary precise: HEAD-4 log-scaling scoped to
     INTEGER; continuous stays bounded by P1 C1
   - Tune-free bands pre-registered per gate
   - 11th rule preserved (substrate-internal; no LLM)

Substrate state: no atom mutations from this DECISION (specification ratify
   only); cap_pres=1.0 PRESERVED; methodology FROZEN at 24.

Exp-Dev's WORK measurement (R=105 -> 1155 -> 15015 sweep; K bounded+
   decreasing; tune-free across 143x range) is the SANITY PREVIEW of
   GATE-F + the EMPIRICAL EVIDENCE that the recipe can pass GATE-F at
   integer scope. It is NOT a substitute for the formal pre-registered
   cert-cell GATE-F run.

   Increased confidence in the P2 path WITHOUT pre-supposing GATE-F
   verdict: the prereg's verdict tree remains both-paths (PASS or
   HONEST_BOUNDED); the cert cell adjudicates.
```

## DECISION 226a -- P2 cert chain transitions to STEP-3

```
P2 cert chain progression:
   STEP-1 design (Skunkworks)                       COMPLETE (this DECISION)
   STEP-2 prereg LOCK (Director ratify)             COMPLETE (this DECISION)
   STEP-3 cell authoring (Exp-Dev)                  GO
   STEP-4 cell-vs-cert VET (Skunkworks)             standing
   STEP-5 Director ratify                            standing
   STEP-6 Orchestrator remote dispatch               standing
   STEP-7 results-read + VET (Exp-Dev + Skunkworks) standing
   STEP-8 Director ratify                            standing
   STEP-9 Testbed P2 atom                            standing

EXP-DEV STEP-3 cell authoring:
   - experiments/exp_primitive_2_hopfield_cleanup_v1.py (or per Skunkworks
     naming)
   - Quad-head implementation (HEAD 1 atomized; HEAD 2 atomized; HEAD 3
     sparse-Hopfield entmax/alpha-entmax; HEAD 4 OLS-Gram + soft + restarts
     + reconstruction-accept recipe)
   - GATE-D closed-form beta fidelity protocol
   - GATE-E envelope protocol per Delta_min
   - GATE-F work-vs-R measurement protocol with PRE-REGISTERED tune-free
     bands (beta + K_max + reconstruction-threshold)
   - INSTRUMENT K + iterations as FIRST-CLASS METRICS not just decode_acc
   - INTEGER-residue scope; continuous-magnitude bounded by P1 C1
   - OOM-lesson carried: NO big broadcasts; loop-not-tensor pattern; per-
     point loops where memory matters
   - Sweep R: incl. R=1155 (P1 full scope) + R=15015 + larger if feasible
   - 11th rule: substrate-internal; no LLM in cell authoring
   - Self-test: closed-form theorem-verify (Ramsauer beta; sparse margin;
     Kymn capacity)
   - Honest both-verdict-paths verdict logic per Skunkworks's prereg

   Estimated cell authorship: ~1-2 cycles substantive work; OOM-fix lesson
   carried; pre-stage prereg .md was provided by Skunkworks.

TESTBED + ORCHESTRATOR standing for STEP-4 onward.
```

## Pipeline state (post-DECISION-226)

```
PHASE C TIER-3 ARC:
   PRIMITIVE 1: CLOSED 8f96cb93 (atom UNCHANGED through all this)
   PRIMITIVE 2: STEP 1-2 COMPLETE (prereg LOCKED this DECISION); STEP-3
                cell authoring GO; remaining steps standing
   PRIMITIVE 3: DEFERRED

USER 3-TIER + 4a + 4c (unchanged from DECISION 225):
   TIER 1: COMPLETE 5bcca90d
   TIER 2: spec updated; PHASE 1 standing
   TIER 3: DEFERRED
   TIER 4a broader: list compilation parallel (Kymn-OLS + simplex bound +
                     reconstruction-accept + Ramsauer + VFA + SSPs + etc.)
   TIER 4c: assessment authoring parallel

Sessions:
   Skunkworks: P2 STEP-4 cell-vs-cert VET reactive; Tier 2 spec batch +
                Tier 4a list + Tier 4c assessment continue
   Exp-Dev: STEP-3 P2 cell authoring GO (~1-2 cycles); instrument K +
            iterations as first-class metrics; OOM-lesson carried;
            INTEGER scope
   Testbed: standing for P2 STEP-9 reactive; Tier 2 PHASE 1 standing
   Orchestrator: standing for P2 STEP-6 remote dispatch; Tier 1 COMPLETE
   Research (Director): STEP-5 ratify reactive on Skunkworks STEP-4 VET

Substrate state: 26289 atoms / 5206 relations / 206-206 axiom-term /
   cap_pres=1.0 PRESERVED / methodology FROZEN at 24. Audit ledger:
   89 CONFIRMED + 3 candidates (89th + 90th + 92nd).
```

## Safety / invariants

- ASCII only
- 11th + 18th + 19th + 21st + 22nd rules preserved
- 18th-rule: framing softened per DECISION 225 maintained; GATE-F is
  measurement-not-presupposition
- 19th-rule: Exp-Dev's ownership of over-claim + instrumentation per
  Skunkworks's request; Skunkworks's distinctness analysis applied to
  prereg's own design (heads 1-3 not pseudo-independent)
- 22nd-rule: Lakatos-progressive content; P1 atom unchanged; P2 will
  characterize at P2 scope
- 84th cert chain integrity PRESERVED (STEP 1+2 -> STEP 3)
- Tune-free bands pre-registered (DECISION 225 GATE-F req 4 enforced)
- INTEGER scope precise (DECISION 225 GATE-F req 2 enforced)
- Both verdict paths preserved (DECISION 225 GATE-F req 5 enforced)
- Work-vs-R measurement protocol (DECISION 225 GATE-F req 1 enforced)
- Full-scale + beyond sweep (DECISION 225 GATE-F req 3 enforced)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

226 cumulative decisions. **261+ honest signals.** 89 CONFIRMED audit-discipline
instance types + 3 candidates (89th + 90th + 92nd). Phase C TIER-3 Primitive 2
STEP 1+2 COMPLETE; STEP-3 cell authoring GO; remaining steps standing.

---

**Skunkworks (Auditor):** P2 prereg DESIGN STEP-1 + STEP-2 LOCK ACK; comprehensive
delivery + distinctness analysis + 5 GATE-F reqs incorporated + honest open-part.
Standing for P2 STEP-4 cell-vs-cert VET. Continue Tier 2 + Tier 4a + Tier 4c
parallel.

**Exp-Dev (Prover):** WORK-vs-R measurement empirically REFUTES Skunkworks Finding
A within INTEGER scope (K bounded+decreasing not growing; work ~sum(m_b) not O(R);
tune-free across 143x R range). Ownership of over-claim ACK. Findings B+C preserved.
P2 cert chain STEP-3 cell authoring GO per LOCKED prereg; OOM-lesson carried;
instrument K + iterations as first-class metrics.

**Testbed (Integrator):** P2 cert chain standing for STEP-9 reactive; Tier 2
PHASE 1 small-batch ingest standing on Skunkworks spec batch arrival.

**Orchestrator (Custodian):** P2 STEP-6 remote dispatch standing; cert chain
monitoring continues; Tier 1 COMPLETE.

**USER:** P2 cert chain progressing per LOCKED prereg with: (a) Skunkworks's
comprehensive DESIGN incorporating distinctness analysis + 2 known constraints
+ G1-G5 + GATE-D/E/F per 5 hard requirements; (b) Exp-Dev's WORK-vs-R measurement
preview empirically supporting log-scaling within INTEGER scope (Finding A
refuted at this sweep); (c) honest scope precise (INTEGER not continuous;
prototype not ratified; cert-cell adjudicates with pre-registered bands).
P1 atom UNCHANGED. System self-corrects throughout: Exp-Dev owned over-claim;
Skunkworks delivered substantive prereg + folded VET findings into requirements;
Director ratifies with full discipline preserved. ~2 cycles light to P2 STEP-3
cell authoring; remaining steps standing on cert-chain rhythm.

Tag: DECISION_226_P2_prereg_DESIGN_STEP_2_LOCK_RATIFIED_comprehensive_quad_head_distinctness_analysis_heads_1_3_softness_spectrum_same_flat_O_R_HEAD_4_only_sub_O_R_factored_2_known_constraints_simplex_correlation_non_factoring_continuous_residue_kernel_G1_G5_mapping_GATE_D_closed_form_Ramsauer_beta_tune_free_GATE_E_envelope_gerrymander_guard_GATE_F_work_vs_R_measurement_5_hard_requirements_DECISION_225_enforced_honest_open_part_INTEGER_vs_continuous_scope_precise_Exp_Dev_WORK_measurement_R_143x_grow_work_2p75x_grow_track_sum_m_b_K_bounded_decreasing_tune_free_across_sweep_Finding_A_empirically_REFUTED_within_INTEGER_scope_Findings_B_C_PRESERVED_P1_atom_UNCHANGED_22nd_Lakatos_progressive_P2_STEP_3_cell_authoring_GO -- Research (Director)
