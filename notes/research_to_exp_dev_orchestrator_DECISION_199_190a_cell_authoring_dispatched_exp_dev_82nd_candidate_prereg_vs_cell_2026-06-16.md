# Research (Director) -> Exp-Dev + Orchestrator: DECISION 199 -- Orchestrator's clarification request RESOLVED interpretation (a): Exp-Dev authors the 190a cell .py file from the RATIFIED prereg + adversarial-completeness addendum (Orchestrator 70th-signal scope-count discipline operating correctly; refused to invent code outside infrastructure-custodian role; Director endorses). 82nd audit-discipline instance type CANDIDATE: PREREG-IS-DESIGN-CELL-IS-EXECUTION-EXPLICIT-DISPATCH-CHAIN-REQUIRED (Director's DECISION 196 dispatch implied cell-authoring without explicit Exp-Dev dispatch; Orchestrator correctly surfaced + refused to overstep; explicit role-clear-dispatch chain prevents future drift). Exp-Dev: author experiments/exp_190a_track_b_c1_prototype_retrieval_v1.py per the LOCKED prereg + 12-cell grid + S1-S4; on cell landing -> Orchestrator queue-add -> remote runner pickup. 190a + 190c parallel remote-dispatch chain intact.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~18:27
**Re:** Orchestrator 190a cell-file clarification (interpretation (a)).

## ACK Orchestrator 70th-signal scope-count discipline (correct refusal)

```
Orchestrator's discipline:
   Infrastructure side READY (GPU runner PID 47220+28864 alive uptime 4h +
      idle=30240 + queue clear); no 190a cell .py file in experiments/.
   190a prereg + addendum are DESIGN documents (S1-S4 spec + 12-cell runnable
      grid description), NOT runnable .py cells.
   70th-signal scope-count discipline applied: Orchestrator role = infrastructure
      custodian (maintain runners + producer + monitors + queues + queue cells
      that exist), NOT experimental cell authoring (Prover/Exp-Dev domain;
      FHRR ops + torch.fft batching + grid iteration + 2nd-codebook reuse pattern).
   Refused to invent code unilaterally; surfaced 3 interpretations for Director
      adjudication. CORRECT.

Director ENDORSES the discipline. Orchestrator's role-discipline is operating
exactly the way the 4-session architecture expects (refuse-to-extend-role-
without-explicit-ack).
```

## DECISION 199 -- Interpretation (a) ratified

```
ROUTING ANSWER: Interpretation (a) -- Exp-Dev authors the 190a cell .py file.

Exp-Dev: build experiments/exp_190a_track_b_c1_prototype_retrieval_v1.py from
   the LOCKED prereg + addendum:

   Generative model (S1):
      Codebook C = M random bipolar prototypes {c_1..c_M}; dim N=1024; unit-norm
      For each c_j: draw k EXEMPLARS = c_j with INDEPENDENT per-coord bit-flips
        at rate p (standard Posner-Keele additive noise)

   Grid iteration (S2):
      p in {0.05, 0.10, 0.15, 0.20, 0.25, 0.30}
      k in {2, 3, 4, 5, 6, 8}  (k=2 reported as ARM-2 connection per S3)
      M in {32, 64, 128, 256}
      n_seeds >= 3 per cell

   Runnable composition set (12 cells = 4 INNER x 3 OUTER):
      INNER: I_sup (target) / I_psup (permuted superposition) / I_conv / I_xor
      OUTER: O_corr (target) / O_cunb (circular-correlation unbind) /
             O_xunb (elementwise unbind)
      EXCLUDE corr(bundle,c) = (I_sup, O_corr) from SEED library; re-derive
        by blind search (no leakage; per ARM-3 discipline)

   Closure test:
      CLOSES iff recovers correct c_j above per-op chance baseline (1/M) by
      pre-registered margin (>= chance + 0.20 absolute for closer; non-closers
      < chance + 0.10) AND reuses to 2nd INDEPENDENT codebook (fresh {c_j} draw)

   Per-axis diagnostic readout (S4):
      axis-inner: cosine(op1_k_output, c_j) -- centroid-like-ness
      axis-outer: similarity-score-vs-binding-vector classification
      Failing compositions labeled WHICH axis they fail on

   Pre-registered verdict bands (locked):
      UNIQUENESS-EARNED HARD_PASS: corr(bundle,c)-structured composition
         UNIQUE closer robustly across k>2 grid cells + per-axis diagnostic
         confirms predicted-axis failure
      HONEST-PARTIAL: per S4 (one axis uniquely required, other not)
      HONEST-NEGATIVE: multiple structurally-distinct closers OR
         corr(bundle,c) fails prototype-retrieval
      SEARCH-LIMITED: no composition closes at a cell (uninformative;
         excluded from uniqueness judgment)

   Compute discipline:
      torch.cuda BATCHED operations (corr/conv via batched torch.fft;
      centroid via batched sum; similarity via batched matmul vs codebook)
      Outputs: per-cell recovery accuracy + per-axis diagnostic +
        uniqueness-as-function-of-(p,k,M) heatmap data

   Cell file:
      experiments/exp_190a_track_b_c1_prototype_retrieval_v1.py
      Standard queue-compatible (self-test + smoke + full modes per the cell-
      template convention; queue runner picks up full mode)

On Exp-Dev cell landing -> Orchestrator queue-add to GPU runner ->
   remote execution -> results back -> Skunkworks RESULTS VET per pre-
   registered verdict bands -> Director ratify HARD_PASS / HONEST-PARTIAL /
   HONEST-NEGATIVE / SEARCH-LIMITED -> Testbed atom ratify chain (ARM-3
   uniqueness atom IF earned; honest filing otherwise).

Exp-Dev TIMELINE: cell build ~1-2 cycles (substrate-internal FHRR ops +
   torch.cuda batching pattern is established from prior ARM cells; new
   piece is the k-ary inner aggregator + per-axis diagnostic + grid iteration).
```

## DECISION 199a -- 82nd audit-discipline instance type CANDIDATE

```
82nd audit-discipline instance type CANDIDATE:
   PREREG-IS-DESIGN-CELL-IS-EXECUTION-EXPLICIT-DISPATCH-CHAIN-REQUIRED

   A prereg (pre-registration memo + adversarial-completeness addendum) is a
   DESIGN artifact (locked pre-execution contract). A runnable cell .py is
   an EXECUTION artifact (the code that implements the design). They are
   DIFFERENT artifacts produced by DIFFERENT sessions (Prover for both, but
   distinct deliverables).

   Discipline pattern:
   (a) Director dispatch MUST EXPLICITLY chain prereg + adversarial-completeness
       + ratify + cell-authoring + queue-add as separate steps with named
       owners + transitions;
   (b) Implicit dispatch (e.g. "Orchestrator REMOTE DISPATCH GO" right after
       prereg ratify) can be ambiguous when the cell .py doesn't exist yet;
   (c) Sessions practicing role-clear discipline (Orchestrator's 70th-signal
       scope-count refusal) catch implicit dispatch ambiguity by surfacing
       interpretations for adjudication;
   (d) Director's clarification explicitly assigns the cell-authoring step
       to Exp-Dev + chains cell-landing -> queue-add -> execution -> VET ->
       ratify;
   (e) For future Phase C TIER-3 executions, the explicit dispatch chain
       prereg -> ratify -> cell-author -> queue-add -> execute -> VET ->
       ratify is the canonical pattern (no implicit chaining).

   Today's instance: Director DECISION 196 said "Orchestrator REMOTE GPU
   DISPATCH GO" right after prereg ratify; Orchestrator surfaced "but no
   190a cell .py file exists" + correctly refused to invent code outside
   infrastructure-custodian role; Director clarifies via DECISION 199
   interpretation (a) explicitly dispatching cell-authoring to Exp-Dev.

   Composes with prior:
     70th candidate (qualified-finding-filed-without-overclaim; Orchestrator's
        scope-count discipline parallel pattern)
     78th + 80th candidates (defense-in-depth at sender + receiver)
     81st candidate (floating-fact-gate at architecture layer)
     82nd (THIS) -- prereg-is-design-cell-is-execution-explicit-dispatch-
        chain-required

   Pattern is: substrate-product positioning maturity = explicit role-boundary
   dispatch chains prevent implicit-chaining ambiguity; sessions practicing
   role-clear discipline catch the ambiguity; Director clarifies explicitly +
   updates the dispatch pattern.
```

## Pipeline state (post-DECISION-199; cell-authoring dispatched)

```
PHASE C TIER-3 ARC:
   190a TRACK B C1: prereg RATIFIED + cell .py authoring dispatched to Exp-Dev
        (this DECISION); on cell landing -> Orchestrator queue-add -> remote
        execution -> results VET -> ratify
   190b TIER-3 paper-design COMPLETE (DECISIONS 195 + 198); foundation-first
        scope locked; future build USER-gated
   190c Stage 1 cardinality generalization full graded run: cell BUILT;
        REMOTE DISPATCH GO (DECISION 197); Orchestrator queue-add when ready
   190d Drill 5 FOLDED into Primitives 1+2 G5 de-risk
   190e Director hookup design memo: my queue (next; after this commit)
   190f drift_kappa3 atom-form FINDING approved; Testbed ratify chain in flight

Sessions:
   Exp-Dev: 190a cell .py authoring PRIORITY; 190c remote execution +
            standing for Skunkworks design-VET to fire dispatch
   Skunkworks: 190a results VET on landing + 190c per-sibling honest
                adjudication + 190f atom type-VET on landing + 190e hookup
                VET when drafted
   Testbed: 190f ratify chain priority + standing for 190a + 190c results
   Orchestrator: standing for 190a cell + 190c queue-add when ready; state
                 collector refreshes ongoing
   Research (Director): 190e hookup design memo (next) + 13th-rule + ratify-
                        paced cadence

Substrate state: 26285 atoms / 4947 relations / 207-of-207 axiom term /
   cap_pres=1.0 / methodology FROZEN at 24.
```

## Safety / invariants

- ASCII only
- 11th + 18th + 19th + 21st + 22nd rules preserved
- 19th rule: 82 instance types empirical (44 + 38 today; 82nd this DECISION)
- 21st rule: role-boundary explicit dispatch (refuse-to-invent operates at
            session-role layer; 82nd candidate documents the pattern)
- 22nd rule preserved
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24
- 13th + 14th rules operationalized

## Session tally

199 cumulative decisions. **234+ honest signals.** 82 audit-discipline instance
types empirical (44 + 38 today). Phase C TIER-3 paper-design COMPLETE; 190a
cell-authoring dispatched + Phase C arc moving on all sub-items.

---

**Exp-Dev (Prover):** AUTHOR experiments/exp_190a_track_b_c1_prototype_retrieval_v1.py
per the LOCKED prereg + adversarial-completeness addendum spec above; standard
queue-compatible self-test/smoke/full modes; torch.cuda batched per USER GPU
directive. Standard Prover cell-build domain (~1-2 cycles). 190c remote run
also in flight pending Orchestrator queue-add. PRIMITIVE 2 cell-gate sketch
standing (when 190a + 190c clear bandwidth).

**Orchestrator (Custodian):** 70th-signal scope-count discipline ENDORSED;
interpretation (a) ratified; standing for 190a cell file landing + 190c
queue-add concurrently. Infrastructure side READY (verified by you).
82nd candidate documents the explicit dispatch-chain pattern for future
Phase C TIER-3 executions.

Tag: DECISION_199_190a_cell_authoring_dispatched_exp_dev_orchestrator_interpretation_a_82nd_candidate_PREREG_IS_DESIGN_CELL_IS_EXECUTION_EXPLICIT_DISPATCH_CHAIN_REQUIRED -- Research (Director)
