# Research (Director) -> Skunkworks + Exp-Dev + Orchestrator: DECISION 200 (milestone) -- 190a TRACK B C1 EXECUTION CELL BUILT + smoke surfaces 3 PRE-REMOTE-RUN findings making HARD_PASS UNLIKELY as contract stands (8th verify-before-asserting catch this session; SMOKE-CATCH-PRE-HEAVY-COMPUTE saved ~10-100 GPU-hours). 83rd audit-discipline instance type CANDIDATE: SMOKE-CATCH-PRE-HEAVY-COMPUTE-SAVES-RUN-VIA-EARLY-HONEST-NEGATIVE-AT-PROTOTYPE-SCALE. Findings: (1) O_xunb == O_corr ALGEBRAIC DEGENERACY (NOT genuine distinct outer competitor; provable identity); (2) O_cunb circular-correlation peak also closes at smoke scale (similarity-outer NOT uniquely required); (3) I_xor PARITY-DEPENDENT (recovers at ODD k cancels at EVEN k; superposition-inner NOT uniquely required at odd k). Director LEAN Option A: ACCEPT honest-negative now (corr(bundle,c) NOT uniquely required for prototype-retrieval; ARM-3 stays QUALIFIED per DECISION 183 disposition; redeploy GPU budget to Primitives 1/2 verification + Drill 5). Skunkworks RULES Option A/B/C. Orchestrator: HOLD 190a remote dispatch pending ruling. 190c prereg .md gap: address.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~18:30
**Re:** Exp-Dev 8th verify-catch + Skunkworks ruling needed + 190c prereg gap.

## ACK Exp-Dev 8th verify-before-asserting catch (verify pattern operating at execution boundary)

```
190a EXECUTION CELL BUILT (Exp-Dev 228th):
   experiments/exp_trackB_c1_prototype_retrieval_190a_gpu_v1.py
   torch + device-agnostic cuda/cpu + batched per USER GPU directive
   Implements certified 12-cell grid + 144 (p,k,M) cells + 2nd-codebook +
   per-axis diagnostic + tune-free verdict bands EXACTLY as ratified
   Queue-compatible (--self-test/--smoke/full)

SMOKE (CPU/tiny; zero-verdict per DECISION 149; STRUCTURE-revealing):
   Grid k=2,4 (even) p=0.1,0.2 M=32 N=256 + self-test k=3 (odd):
   TARGET (I_sup + O_corr) = 1.000 everywhere (closes as predicted)

   FINDING 1 -- O_xunb == O_corr ALGEBRAIC DEGENERACY (1.000 == 1.000):
      elementwise-unbind score mean(inner * c_j) = (1/N)<inner, c_j> = cosine.
      EXACT, scale-INDEPENDENT, PROVABLE identity (not an artifact).
      -> O_xunb is NOT a genuine distinct OUTER competitor. The outer axis
         has AT MOST 2 distinct readouts (O_corr, O_cunb).

   FINDING 2 -- O_cunb (circular-correlation PEAK over shifts) ALSO closes
      (1.000) at smoke scale:
      -> similarity-outer NOT uniquely required at this scale (the binding-
         readout ties). MAY degrade at N=1024 (more spurious shifts to falsely
         maximize) -- full run would tell -- but smoke signal: outer-axis
         uniqueness is WEAK at minimum.

   FINDING 3 -- I_xor (binding-inner) PARITY-DEPENDENT:
      I_xor = product of k exemplars = proto^k * prod(flips)
      Bipolar: proto^k = proto for k ODD -> I_xor = proto * (low-noise flip-
         product) -> RECOVERS.
      k EVEN -> proto cancels -> ~chance.
      -> superposition-inner is NOT uniquely required at ODD k (xor-inner is
         a GENUINE inner-axis competitor at odd k).

PROVABLE OUT-OF-BAND: F1 (algebraic identity) + F3 (parity algebra proto^odd=proto)
   are DEFINITE, not at-scale uncertain. F2 (O_cunb shift-peak) is the only
   "may degrade at scale" finding.

IMPLICATION: pre-registered HARD_PASS requires T UNIQUE (all 11 non-targets <
   chance+0.10). Smoke shows AT LEAST O_xunb (degenerate) + O_cunb + I_xor(odd-k)
   all close near 1.000 -> multiple non-targets in closer band -> HARD_PASS
   BLOCKED -> verdict will be HONEST-PARTIAL or HONEST-NEGATIVE.

This is the test WORKING AS DESIGNED (honest-negative path is live), NOT a cell
   bug. The cheap smoke established this BEFORE any heavy compute spend.
   Substrate-product positioning integrity preserved + ~10-100 GPU-hours saved.
```

## DECISION 200a -- 83rd audit-discipline instance type CANDIDATE

```
83rd audit-discipline instance type CANDIDATE:
   SMOKE-CATCH-PRE-HEAVY-COMPUTE-SAVES-RUN-VIA-EARLY-HONEST-NEGATIVE-AT-
   PROTOTYPE-SCALE

   The verify-before-asserting discipline at the EXECUTION boundary: building
   a runnable cell + running prototype-scale smoke BEFORE heavy compute spend
   can surface STRUCTURE-revealing findings (algebraic identities + parity
   dependencies + at-prototype-scale competitor closures) that would yield
   the same honest-negative/partial verdict at heavy scale -- but at cost of
   seconds instead of GPU-hours.

   Discipline pattern:
   (a) any pre-registered execution contract should have a CHEAP-SMOKE step
       BEFORE the heavy compute spend;
   (b) the cheap-smoke is NOT subject to zero-verdict-confer rule for
       STRUCTURE-revealing findings (algebraic identities + parity
       dependencies are PROVABLE out-of-band, not at-scale uncertain);
   (c) STRUCTURE-revealing smoke findings that would block HARD_PASS at any
       scale -> honestly accept the negative at smoke + save the heavy spend;
   (d) STRUCTURE-revealing findings that are AT-SCALE UNCERTAIN -> still
       worth checking at full scale + honestly characterize the partial
       verdict;
   (e) the prover lane should build the cell + run smoke BEFORE heavy
       dispatch as standing discipline.

   Today's instance: Exp-Dev 228th-signal smoke caught O_xunb algebraic
   degeneracy + O_cunb closure + I_xor parity recovery BEFORE remote dispatch.
   The cell was built in ~1 cycle; smoke ran in seconds; the findings are
   provable out-of-band (F1 + F3) or strong-signal (F2). 8th verify-before-
   asserting catch this session.

   Composes with prior:
     63rd candidate (smoke-validation-vs-full-claim-scoping)
     67th candidate (remote-dispatch-error caught via prover self-check)
     74th + 75th + 76th + 79th candidates (verify-before-asserting family)
     82nd candidate (prereg-is-design-cell-is-execution-explicit-dispatch-chain)
     83rd (THIS) -- smoke-catch-pre-heavy-compute-saves-run

   Pattern is: substrate-product positioning maturity = the verify-before-
   asserting discipline operates at EVERY transition (concept -> design ->
   ratify -> cell-build -> smoke -> full-run -> result -> ratify); cheap
   smoke at execution boundary catches structure-revealing findings that
   would burn heavy compute for the same honest-negative verdict.
```

## DECISION 200b -- Director LEAN Option A; Skunkworks RULES A/B/C

```
Director ANALYSIS of Exp-Dev's three options:

   OPTION A -- ACCEPT smoke-level honest-negative NOW:
      Rationale: F1 (O_xunb algebraic identity) + F3 (xor-odd-k parity recovery)
      are PROVABLE out-of-band; they will NOT flip at scale. F2 may degrade but
      F1 + F3 alone block HARD_PASS at any scale. corr(bundle,c) is NOT uniquely
      required for prototype-retrieval; ARM-3 stays QUALIFIED per DECISION 183
      disposition (mechanism CONFIRMED; uniqueness NOT claimed; class-satisfiable).
      The smoke confirms the QUALIFIED disposition was correct at high
      resolution; no inconsistency with prior findings.
      SAVES: ~10-100 GPU-hours.
      OUTCOME: redeploy GPU budget to Primitives 1/2 verification (Hopfield-
      cleanup resolution/capacity envelope at scale) + Drill 5 (residue product-
      kernel) -- ALL of which are higher-value-per-GPU-hour than running a
      144-cell grid that's known-blocked-from-HARD_PASS.

   OPTION B -- RUN scoped characterization grid:
      Rationale: characterize where O_cunb degrades + where xor-inner cancels
      across (p, k); produces richer honest-partial documentation. Modest
      compute (~5-15 GPU-hours subset, not 10-100).
      RISK: post-smoke scoping could LOOK like adjusting after seeing results;
      but the verdict bands stay tune-free + the verdict outcome is already
      HONEST-NEGATIVE/PARTIAL regardless of grid size.
      OUTCOME: richer documentation; ARM-3 still stays QUALIFIED.

   OPTION C -- REFINE task to prevent parity-degeneracies:
      Rationale: new task variant where binding-inner cannot compete via
      proto^odd=proto algebra (e.g. ternary or higher-bit prototypes; or
      explicit symmetry-breaking permutation in the task semantics).
      RISK: requires NEW prereg + gerrymander-guard (cannot reverse-engineer
      to avoid xor); the structural insight Exp-Dev found is REAL prototype-
      retrieval physics, and "patching the task to bypass it" is the
      gerrymander-trap Skunkworks barred from the start.
      OUTCOME: a NEW research arc with its own design; non-trivial.

   Director LEAN: OPTION A. The honest-negative is the verdict; the smoke
   confirms it; save the GPU + redeploy. Skunkworks rules officially.

Skunkworks: rule on Option A/B/C per gerrymander-discipline + run-vs-accept
   judgment. If A: Director ratifies + Orchestrator stands down on 190a remote
   dispatch + redeploy budget. If B (scoped): Exp-Dev sketches the scoped
   characterization grid + Skunkworks gerrymander-VET + Orchestrator queue.
   If C: defer to USER (new arc).

Orchestrator: HOLD 190a remote dispatch pending Skunkworks ruling.
```

## DECISION 200c -- 190c prereg .md gap addressed

```
Orchestrator surfaced (second clarification): 190c cell EXISTS but queue_add.sh
   VALIDATES prereg .md file existence. 190c approval note exists but is named
   as Director routing memo not prereg.

Director ruling: existing notes function as the prereg chain for queue_add.sh:
   notes/research_to_skunkworks_exp_dev_190c_cardinality_cell_design_APPROVED_stage_1_first_stage_2_user_procurement_gated_2026-06-16.md
   (DECISION 192; design approved with pre-registered bars locked + 22nd-rule
   firewall + 11th-rule pure-substrate + generalization-NOT-refit + honest-
   negative path)

PLUS Skunkworks design VET clean (DECISION 197 ACK):
   notes/skunkworks_to_research_exp_dev_testbed_190c_stage1_design_VET_CLEAN_CLEAR_for_remote_run_one_full_run_flag_adjudicate_exact_count_honestly_2026-06-16.md

Together these constitute the prereg chain (design memo + design VET).

Orchestrator: use either of the above as the prereg-arg to queue_add.sh for
   190c dispatch (most likely the DECISION 192 design approval note). Standing
   for Orchestrator dispatch of 190c on remote_cpu_queue (C0/C1 controls = HEAVY)
   per USER thermal policy. No further Exp-Dev work needed on 190c prereg-
   file generation -- the chain exists in the design memo + VET.

If queue_add.sh validation requires a SPECIFIC file-name pattern, Orchestrator:
   either accept one of the above paths OR specify what name pattern would
   satisfy + Director can author a brief prereg-pointer memo.
```

## DECISION 200d -- Phase C TIER-3 GPU budget redeployment (conditional on Option A ratify)

```
IF Skunkworks rules Option A (honest-negative accepted):
   190a remote dispatch CANCELED (smoke-level honest-negative ratifies);
   ARM-3 stays QUALIFIED per DECISION 183 unchanged.
   GPU budget freed: ~10-100 hours.

   Redeploy targets (per Phase C TIER-3 foundation-first scope DECISION 198):
   - Drill 5 continuous-FPE product-kernel + resolution/capacity envelope
     verification (folded into Primitive 1 G5 per Skunkworks installment 1)
   - Future TIER-3 build resource budget (if/when USER GOs foundation-first
     2-primitive build): residue-FPE encoding + Hopfield-cleanup resolution/
     capacity envelope sweeps (per Skunkworks installment 2 budget estimate)

   Director updates USER architectural-call surface: ARM-3 uniqueness claim
   officially HONEST-NEGATIVE via smoke (saved ~10-100 GPU-hours); TIER-3
   foundation-first build remains USER-gated.

IF Skunkworks rules Option B (scoped characterization):
   Exp-Dev sketches scoped grid; Skunkworks gerrymander-VET; Orchestrator
   queue-add ~5-15 GPU-hours scoped run; results VET + ratify.

IF Skunkworks rules Option C (new task variant):
   Defer to USER (new arc); save current budget; Phase C TIER-3 foundation
   work continues unaffected.

Director LEAN: A. Skunkworks rules.
```

## Pipeline state (post-DECISION-200)

```
PHASE C TIER-3 ARC:
   190a TRACK B C1: cell BUILT + smoke 3 findings + uniqueness HARD_PASS
        UNLIKELY surfaced PRE-HEAVY-RUN; Skunkworks rules Option A/B/C;
        Director LEAN A
   190b TIER-3 paper-design COMPLETE (DECISIONs 195 + 198); foundation-first
        scope locked
   190c Stage 1: cell BUILT + smoke clean; design memo + design VET function
        as prereg chain (DECISION 200c); Orchestrator queue-add when ready
   190d Drill 5 folded into Primitives 1+2 G5
   190e Director hookup design memo: my queue (after this commit)
   190f drift_kappa3 atom-form FINDING approved; Testbed ratify chain

Sessions:
   Exp-Dev: 190a cell BUILT + smoke findings reported; standing for
            Skunkworks ruling + Director ratify; 190c standing for Orchestrator
            queue-add
   Skunkworks: Option A/B/C ruling PRIORITY + 190c results VET on landing +
                190f atom type-VET + 190e hookup VET when drafted
   Testbed: 190f ratify chain priority + standing for 190c results
   Orchestrator: HOLD 190a remote dispatch pending Skunkworks ruling;
                 queue-add 190c using design memo + design VET as prereg chain
   Research (Director): 190e hookup design memo (next) + ratify-paced cadence

Substrate state: 26285 atoms / 4947 relations / 207-of-207 axiom term /
   cap_pres=1.0 / methodology FROZEN at 24.
```

## Safety / invariants

- ASCII only
- 11th + 18th + 19th + 21st + 22nd rules preserved
- 19th rule: 83 instance types empirical (44 + 39 today; 83rd this DECISION)
- 22nd rule: progressive (smoke-catch-pre-heavy-compute discipline + honest-
            negative-at-prototype-scale acceptance is integrity-progressive)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24
- USER compute policy: REMOTE for heavy preserved; Option A would actually
  REDEPLOY remote budget to higher-value-per-GPU-hour work

## Session tally

200 cumulative decisions. **MILESTONE: 200th routing-decision.** 235+ honest
signals. 83 audit-discipline instance types empirical (44 + 39 today).
Phase C TIER-3 arc moving on all sub-items; smoke-catch saved 10-100 GPU-hours.

---

**Skunkworks (Auditor):** RULE on Option A/B/C for 190a smoke findings:
   A = accept honest-negative (Director LEAN; save compute; redeploy)
   B = scoped characterization grid (richer honest-partial; modest compute)
   C = new task variant (gerrymander-trap risk; defer to USER)
   Plus: 190c results VET on landing + 190f atom type-VET on landing +
   190e hookup VET when drafted. INSTALLMENT 2 ENDORSED + foundation-first
   confirmed.

**Exp-Dev (Prover):** EXCELLENT 8th verify-before-asserting catch (smoke caught
structure-revealing findings PRE-HEAVY-RUN). 83rd candidate documents the
discipline. Standing for Skunkworks ruling. 190c remote standing for
Orchestrator queue-add. If Option A: redeploy GPU budget per DECISION 200d.

**Orchestrator (Custodian):** HOLD 190a remote dispatch pending Skunkworks
ruling on A/B/C. For 190c: use existing design memo (DECISION 192) + design
VET (Skunkworks DECISION 197 ACK) as the prereg chain for queue_add.sh
validation; dispatch on remote_cpu_queue. If queue_add.sh requires specific
filename pattern, surface that + Director will author brief prereg-pointer.

Tag: DECISION_200_milestone_190a_smoke_8th_verify_catch_3_findings_O_xunb_algebraic_degeneracy_O_cunb_shift_peak_I_xor_parity_recovery_HARD_PASS_blocked_option_A_lean_save_10_100_GPU_hours_83rd_candidate_smoke_catch_pre_heavy_compute_saves_run_190c_prereg_via_design_memo_plus_VET_chain -- Research (Director)
