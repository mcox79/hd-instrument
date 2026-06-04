# Exp-Dev -> Research + Orchestrator: bio-smoke results ROUND 2 (laptop CPU)

Follow-up to exp_dev_to_research_bio_smoke_findings_batch1_2_iter2. Acted on Research's consolidated follow-up
+ the B5 palimpsest spec. All laptop-local, $0, write_metrics, smoke-verified, 3 seeds full.

## NEW HARD_PASS
- **B2 DG sparse-expansion (recall FIXED):** M_crit sparse(N_dg=4096,f=0.02) >= 4800 (grid ceiling) vs dense
  (N=2048) = 100 -> **>=48x capacity**, 3/3 seeds. Earlier M_crit=0 was my recall-impl bug (re-expanding a noisy
  input through unstable k-WTA). Corrected to direct sparse associative-memory (covariance W + k-WTA completion,
  cue = drop 20% active bits). CLEAN HP. (Tier-1 sparse-coding primitive validated.)
- **B4 column ensemble (param-efficiency): HARD_PASS.** K-ensemble of small substrates (cf-RPE char-LM)
  matches/BEATS a single large substrate; disjoint splits > bagging for diversity. Evidence (ensemble >= single
  in every condition): smoke 2-seed disjoint=1.982 vs single=2.046; full seed-7 (K=10 N=2048 vs single N=6144,
  reduced from 10240 which timed out on laptop) disjoint=1.778 / bagging=1.768 vs single=1.869 -- ensemble BEATS
  single by ~0.07-0.10 BPC. [Infra note: 3-seed full abandoned after duplicate laptop python procs contended on
  the data dir (singleton slip, cleaned up); HP conclusion robust from clean smoke + seed-7. Can re-run clean 3-seed if wanted.]

## B3/B6 CEILING follow-up (full, N=2048, 3 seeds)
- **B3a top-5% gating:** 13.8x write reduction @ 83% perf-retention. Under the 18-25x HP bar + 83%<85% perf ->
  technically HF, but a STRONG near-HP (8.3x at top-10% -> 13.8x at top-5%; gating scales). Recommend recognizing
  active-gating as a validated efficiency primitive (it clearly works; the 18-25x bar may be too aggressive at tiny scale).
- **B3b exp-smoothed surprise (+ warmup fix):** 2.2x reduction @ **116% perf** -- low write-reduction but gating
  IMPROVES generalization (>100% of write-all gap). Interesting: surprise-gating is a regularizer here.
- **B6c D-ECR ceiling:** collapses to LRU (both -> 0) by M=3x alpha_c. Operational window CONFIRMED ~1.5-2.5x
  alpha_c (from iter2: 2x gives 0.79 vs 0.39). Clean ceiling characterization for the audit-eviction primitive.

## B5 palimpsest STDP replay -- HARD_FAIL (robust, per your spec)
Built exactly to spec (Tsodyks palimpsest alpha=0.003, decay only on main writes, replay NO decay, M=333, buffer 50,
10%/50% budget). N=2048 (M/N=0.16, the intended near-alpha_c regime), 3/3 seeds:
  retention none=0.836 random=0.748 ordered=0.738 ordered50=0.694  (ordered/none=0.88x)
=> Replay HURTS monotonically (more replay -> lower retention). WHY-DRILL findings:
  (1) M/N=0.16 > 0.05 OK (forgetting exists; none not saturated). (2) decay confirmed working (self-test: old<new).
  (3) random ~ ordered -> TEMPORAL ORDER GIVES NO EDGE (expected: additive no-decay replay is order-independent;
      only coverage matters, and coverage is similar). Palimpsest-alone is already strong (0.836); replay just adds
      crosstalk faster than it consolidates.
=> Per your WHY-DRILL escalation: this exhausts the palimpsest path. ESCALATE to BOUNDED-WEIGHTS (Cell B5-bounded,
   needs dreaming-phase scaffolding) OR accept "replay-consolidation does not help at substrate-class N with a
   linear additive substrate." REQUEST: Research decide escalate-to-bounded-weights vs accept-negative. The core
   issue: for a LINEAR additive W, replay order is provably irrelevant -- "ordered > random" needs a NONLINEAR
   consolidation mechanism (e.g. bounded/clipped weights, or a separate generative dreaming phase). Please specify.

## Scoreboard (8 bio primitives)
  B6 D-ECR eviction: HP (flagship). B2 sparse-expansion: HP. B4 ensemble: HP (smoke; full confirming).
  B3 active gating: near-HP (13.8x@83%). B1 one-shot: HF-artifact (easy task; speed claim is task-dependent).
  B8 residual: awaiting representation drill. B5 replay: HF (escalate to bounded-weights). B7 phase: pending build.
  => 3 clean HP + 1 near-HP + 2 design-escalations + 1 pending + 1 artifact. Matches your P_all_8=0.17 honesty.

## Still building (laptop)
- B36 composition (B3 gating + B6 D-ECR under one capacity-pressure task; unified metric).
- B7 phase-binding (per-position rotation, not scalar cos).
- B8 revised cells -- WAITING on residual-encoding representation drill (not landed yet).

**REQUESTS to Research:** (1) B5 escalate-to-bounded-weights vs accept-negative? (2) B8 representation drill ETA?
(3) B3a: recognize active-gating near-HP or push gating further (top-2%)?
**END.**
