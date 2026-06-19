# Research (Director) -> Skunkworks + Exp-Dev + Testbed + Orchestrator: DECISION 196 -- 190a TRACK B C1 prototype-retrieval execution prereg RATIFIED (Exp-Dev 225th addendum 12-cell runnable grid 4 INNER {I_sup target / I_psup / I_conv / I_xor} x 3 OUTER {O_corr target / O_cunb / O_xunb} BOTH-AXIS COMPLETE around corr(bundle,c) = (I_sup, O_corr) with all 5 one-axis-off neighbors present + ARM-2 corrperm3 lesson applied UP-FRONT complete-by-construction; Skunkworks CONDITION SATISFIED VET ALL conditions met S1+S2+S3+S4+no-leakage+2nd-codebook+tune-free). Orchestrator: REMOTE GPU DISPATCH GO (heavy ~10-100 GPU-hours per USER compute policy; torch.cuda batched). 190c Stage 1 cell BUILT + smoke-clean per DECISION 149 zero-verdict discipline (most-sibling directional HARD_PASS + exact-count smoke MIDDLE artifact at tiny VOCAB=60; full run needed at VOCAB=200 N=4096); Skunkworks: design VET on the built cell standing.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~18:20
**Re:** 190a final ratify + 190c smoke ack; pipeline momentum.

## DECISION 196 -- 190a TRACK B C1 prereg RATIFIED + Orchestrator REMOTE DISPATCH GO

```
ALL PREREG CONDITIONS MET:
   S1 NOISE MODEL: standard Posner-Keele additive noise + rationale ON RECORD
   S2 (p,k,M) grid 144 cells: uniqueness across grid not single-point
   S3 k>2 LOAD-BEARING: k=2 reported separately as ARM-2 connection
   S4 HONEST-NEGATIVE PER AXIS: per-axis diagnostic preserved
   NO-LEAKAGE: corr(bundle,c) excluded from seed library; re-derived blind
   2ND-CODEBOOK REUSE: honest negative protection
   TUNE-FREE VERDICT BANDS: chance+0.20 for closer; non-closers chance+0.10
   HONEST-SCOPE: 12 runnable compositions NOT "38 signatures"
   ADVERSARIAL-COMPLETENESS: both-axis 12-cell runnable grid + all 5
      one-axis-off neighbors of corr(bundle,c) present (no omitted competitor)

12-CELL RUNNABLE GRID (Exp-Dev addendum; Skunkworks VET'd):
                  O_corr      O_cunb      O_xunb
      I_sup    |   TARGET  |   OUT-N   |   OUT-N   |  <- OUTER-axis neighbors
      I_psup   |   IN-N    |     .     |     .     |
      I_conv   |   IN-N    |     .     |     .     |  <- INNER-axis neighbors
      I_xor    |   IN-N    |     .     |     .     |

   Where TARGET = corr(bundle,c) = (superposition-inner, similarity-outer);
   OUT-N tests OUTER-axis uniqueness (does similarity-outer uniquely matter?);
   IN-N tests INNER-axis uniqueness (does superposition-inner uniquely matter?).
   Inner spans superposition-class + binding-class; outer spans similarity +
   binding-readout. NO competitor omitted on either axis.

Director RATIFIES the prereg + adversarial-completeness addendum + Skunkworks
   CONDITION SATISFIED VET. Post-hoc-impossible contract LOCKED.

Orchestrator: REMOTE GPU DISPATCH GO.
   Compute: ~10-100 GPU-hours estimate (144 cells x 12 runnable compositions x
      (k+1) atoms x 2 codebooks x n_seeds>=3 x batch x N=1024).
   torch.cuda BATCHED per USER GPU directive (corr/conv via batched torch.fft;
      centroid via batched sum; similarity via batched matmul vs codebook).
   Compute backend: REMOTE DESKTOP per USER policy (heavy GPU-batched, NOT
      laptop).
   Reporting: per-cell recovery accuracy + per-axis diagnostic + uniqueness-
      as-function-of-(p,k,M) heatmap + reuse to 2nd independent codebook.
   On completion: Skunkworks RESULTS VET + Director ratify HARD_PASS / HONEST-
      PARTIAL / HONEST-NEGATIVE per pre-registered verdict bands -> Testbed
      atomic ratify chain (ARM-3 uniqueness atom IF earned; honest filing
      otherwise).

Pipeline standing: results timeline ~1-3 days depending on grid; ratify-paced
   chain on landing.
```

## DECISION 196a -- 190c Stage 1 smoke ACK (zero-verdict per DECISION 149)

```
Exp-Dev built Stage 1 cell:
   experiments/exp_cardinality_generalization_stage1_190c_cpu_v1.py
   OPERATOR LOCKED: CLEANUP_THRESH=0.30 (ARM-1 ratified FROZEN; re-tuning would
                                          be refit not generalization)
   DISTRIBUTION SHIFTED vs ARM-1: VOCAB=200 ROLES=5 n_distinct[2,13) mult[1,6)
                                   N{2048,4096} vs ARM-1's VOCAB=120 ROLES=4
                                   n_distinct[1,9) mult[1,4) N{1024,2048,4096}
   GOLD FIREWALLED (22nd rule; same discipline as q54-q65 / 56d)
   PIPELINE pure-substrate (no LLM): FHRR superpose(bind(role,filler)) ->
                                      cleanup_distinct_count -> readout
   CONTROLS (FAIR-NULL): C0 graph-walk-trace (B^T@B; HEAVY) + C1 basis-norm null

PRE-REGISTERED BARS (ARM-1 carried; LOCKED):
   exact-count: RMSE<=1.0 + >=2x reduction vs C1 + beats C0 within envelope
   most(A>B): acc>=0.80 + margin>=0.20 + no-drift

SMOKE RESULTS (zero-verdict per DECISION 149 smoke-vs-full discipline):
   SINGLE-ROLE exact-count RMSE: C0=9.02 / C1=40.02 / C2=2.26 (envelope frac=0.0137)
   MOST(A>B) acc: C1=0.538 / C2=0.838 (no-drift)
   Most directional HARD_PASS; exact-count smoke MIDDLE (smoke ARTIFACT: tiny
   VOCAB=60 inflates cleanup collisions; full run VOCAB=200 N=4096 has far
   lower collision rate).

Director ACK: smoke confers ZERO verdict per DECISION 149 + 63rd candidate
   smoke-validation-vs-full-claim-scoping discipline. The exact-count smoke
   MIDDLE is honestly disclosed + diagnosed as VOCAB=60 collision artifact +
   directionally encouraging on most-sibling + pipeline + envelope-targeting
   + verdict-logic VERIFIED. Smoke is process validation NOT result.

   Honest-negative path preserved: if full run shows operator does NOT transfer
   -> ARM-1 capabilities stay scoped + no manufactured transfer claim.

Standing for Skunkworks 190c design VET (22nd-rule gold firewall + 11th-rule
   no-LLM + generalization-NOT-refit-discipline + verdict bands).
Standing for Skunkworks design VET clear -> Director GO -> Orchestrator REMOTE
   DESKTOP dispatch (C0 control = laptop-overheater class per USER policy).
```

## Pipeline state (post-DECISION-196)

```
PHASE C TIER-3 ARC (live; substantial parallel motion):
   190a TRACK B C1 prereg RATIFIED (DECISION 196 this turn); Orchestrator
        REMOTE GPU DISPATCH GO; execution wall-clock ~1-3 days; results
        ratify chain standing
   190b TIER-3 paper-design INSTALLMENT 1 ENDORSED (DECISION 195); standing
        for INSTALLMENT 2 (Primitives 2-3 + budget + integration architecture)
   190c Stage 1 cell BUILT + smoke CLEAN (zero-verdict ACK this turn); standing
        for Skunkworks design VET + Director GO + Orchestrator remote dispatch
        of full graded run
   190d Drill 5 FOLDED into Primitive 1 G5 (no separate work)
   190e Director hookup design memo: my queue (after this commit)
   190f drift_kappa3 atom-form FINDING approved; Testbed ratify chain in flight

Sessions:
   Exp-Dev: 190c full graded run on Skunkworks-VET + Director-GO + remote
            dispatch; standing for 190a results; PARALLEL: ratify-paced
   Skunkworks: 190c design VET (priority) + 190b INSTALLMENT 2 + 190f
               type-discipline VET on landing + 190a results VET on landing +
               190e hookup VET when drafted
   Testbed: 190f drift_kappa3 ratify chain; standing for 190a + 190c results
            ratify chains
   Orchestrator: 190a REMOTE GPU DISPATCH GO (priority; this turn); 190c
                 remote dispatch on design VET clear + Director GO; state
                 collector refreshes ongoing
   Research (Director): 190e hookup design memo (next on my queue) +
                        13th-rule active state-check armed + ratify-paced
                        cadence on all sub-items

USER touches surfaced (non-blocking):
   1. formal-oracle external-rater procurement direction (190e; when ready)
   2. 190c Stage 2 external-data procurement direction (when Stage 1 passes)
   3. 3 TRACK D design Q's (palette / tab strategy / corpus scope; iterate at
      visual review)
```

## Safety / invariants

- ASCII only
- 11th + 18th + 19th + 21st + 22nd rules preserved
- 19th rule: 80 instance types empirical (no new candidate this turn; existing
            discipline operating)
- 22nd rule: progressive (190a prereg execution = falsifiable uniqueness
            prediction now in flight; 190c Stage 1 smoke = falsifiable
            generalization prediction process-validated)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24
- 13th + 14th rules operationalized
- USER compute policy enforced (190a + 190c full-run controls REMOTE not laptop)

## Session tally

196 cumulative decisions. **231+ honest signals.** Phase C TIER-3 arc substantially
in motion; 190a prereg RATIFIED + execution GO via Orchestrator; 80 audit-discipline
instance types empirical (44 + 36 today).

---

**Skunkworks (Auditor):** 190a CONDITION SATISFIED VET ENDORSED; 190a RATIFIED
+ Orchestrator REMOTE DISPATCH GO; STANDING for 190c design VET (priority) +
INSTALLMENT 2 (190b Primitives 2-3 + budget + integration); 190f type-discipline
VET on landing; results VETs on 190a + 190c full-run as they land.

**Exp-Dev (Prover):** 190a addendum + adversarial-completeness ENDORSED + RATIFIED;
PREREG LOCKED post-hoc-impossible; 190c Stage 1 cell BUILT + smoke CLEAN ACKED
(zero-verdict per 149); standing for Skunkworks design VET on 190c. Excellent
post-redispatch parallel delivery (3 deliverables in ~10 min).

**Testbed (Integrator):** 190f drift_kappa3 ratify chain (kind:FINDING +
metric_type:DETECTION + STRICT type-discipline + cap_pres=1.0); standing for
190a + 190c results ratify chains as they land.

**Orchestrator (Custodian):** 190a REMOTE GPU DISPATCH GO PRIORITY -- execute
the 144-cell (p,k,M) grid x 12 runnable compositions x (k+1) atoms x 2 codebooks
x n_seeds>=3 x batch x N=1024 on remote desktop GPU; torch.cuda batched per
USER policy; results back to Skunkworks VET -> Director ratify chain. Continue
state collector refreshes for dashboard freshness.

Tag: DECISION_196_190a_RATIFIED_remote_dispatch_GO_12_cell_runnable_grid_both_axis_complete_5_neighbors_present_adversarial_completeness_ARM2_corrperm3_lesson_up_front_complete_by_construction_190c_smoke_ack_zero_verdict_per_149_full_run_pending_skunkworks_design_VET -- Research (Director)
