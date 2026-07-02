# Session synthesis 2026-07-02 (full-day arc)

**Latest tally: 32 CG + 2 CG_META + 19 MM + 3 HF + 3 MB + 3 AMEND (34 total chain-grade atoms this session).**

## Late-session addendum (evening arc — USER full-auto)

After the initial 25 CG synthesis below, the session extended significantly:

### Cortex integration debt CLOSED (M3 architecture bottleneck)
- Phase 1: extracted M1.5/M1.7/M1.8 primitives to hdlab modules (context_retention + role_slot_summarizer + clarify_gate)
- Phase 2: authored `hdlab/cortex.py` composed pipeline (532 lines)
- Phase 2b: extracted M1.3 NoiseChannel + wired into cortex.py (USER-locked 2026-06-30 stochastic-noise-at-boundary directive unblocked)
- Phase 3: end-to-end integration test at 3-seed FULL HARD_PASS bit-identical (max_delta=0.0 exact across 4 discriminators)
- Phase 3b: noise-enabled variant CG (wiring live via probe cos-shift 0.005-0.007; backwards-compat with Phase 3 baseline exact; substrate noise-tolerance at σ=0.05-0.15 confirmed)
- Skunkworks filed `META_cortex_M1_stack_integration_proposal_complete` CG_META

### Additional session wins
- stretch2_3 v2 rescue CG (substrate hosts non-temporal STRIPS planning); v1 AMEND-DEMOTE (numpy-costume + oracle-goal)
- Analogy #6 CG_HONEST_NEGATIVE (Level-4 pivot mechanism #6; frozen random codebook + K=10 mean-unbind fails; M3 constraint atom filed)
- Option C activity/energy MB (first confidence signal above chance at 3-seed FULL; brain-analog Kool 2018 EVC theory)
- Scale-free extension probe at N=16384 (smoke HP; FULL blocked by 8GB GPU VRAM — 3 fix iterations; fallback to 1×N ratio in progress)

### USER strategic decisions this session
- **D on confidence architecture** (move on; keep C for later — cortex layer as consumer of confidence signals). Strengthened by Phase 3b CG proving the wiring path works.
- **APPROVED cortex integration proposal** with sharded-storage discipline. Delivered all 3 phases + Phase 2b + Phase 3b.
- **Level-4 analogy pivot #6 authorized** — closed as CG_HONEST_NEGATIVE; M3 cortex-layer design constraint filed.
- **Option C drill authorized** — MB partial evidence with orthogonality lift; brain-analog grounded.

### Pipeline still active at session close
- Scale-free extension fallback fix (option 3: drop NPROP=32000, test at 1×N ratio) in cell-author (a7c4d75 resumed 3rd time)

---

## Original synthesis (afternoon 25-CG arc; kept for history)

**Session tally locked at start of GPU queue drain: 25 CG + 19 MM + 2 HF + 1 MB + 1 AMEND.**

## Two parallel arcs converged in one session

### Arc 1 — Confidence-signal architecture HITS EMPIRICAL WALL

Task framing (via research drills): does the substrate have observable signals that predict when its own retrieval is uncertain? Needed for M3 cortex to route between ACCEPT / CLARIFY / REFUSE / RE-QUERY.

Tested 4 mechanism classes:

| Signal | Brain analog | h4-harness result | Verdict |
|---|---|---|---|
| Density (h4) | population crowding | HARD_FAIL CG (Skunkworks: "hearing one whisper by stadium loudness") | Dead |
| Spatial margin (h4b) | population spread top1-top2 | HARD_FAIL CG at h4-harness + relaxed regime (falsified drill's REGIME_CONFOUND) | Dead across regimes |
| Stochastic consistency (lane_x_prime) | trial-to-trial neural response variability | HARD_FAIL CG at 3-seed FULL | Dead |
| Post-hoc calibration (lap3_12) | metacognitive readout | MIDDLE_BAND (Cramer-Rao ceiling) | Partial |

3 of 4 signals empirically dead. The 4-signal architecture proposal (originally 3-signal → upgraded to 4 after drill abe94cac → rebrand to reality: **doesn't hold up**).

**BUT — this arc produced multiple chain-grade honest negatives + 2 CG META atoms:**
- META regime-hostility CG (3-class evidence, SCOPE-EXPANDED to include relaxed regime)
- **META_RULE smoke-single-seed-inflates-AUC CG** (3 concurrent data points; regression-to-mean at high-side single-seed draws; now baked into exp_dev.md via commit `f07d607c4`; future confidence/contamination cells REQUIRE multi-seed variance-probe smoke)

USER strategic decision now pending on continuation vs pivot. 4 options in proposal `notes/proposal_M3_cortex_three_signal_confidence_architecture_2026-07-02.md`:
- **A** Reframe task (contam=40%, INTRA_COS=0.35) and re-derive signals
- **B** Accept substrate self-detection limit; use external signals for M3
- **C** Deep pivot to substrate ACTIVITY observables (energy/effort proxies; Kool 2018 brain analog)
- **D** Move on; ship CG negatives; return after Stage 2

### Arc 2 — Stage 1 SUBSTRATE-PHYSICS wins hidden inside "boring" saturation

Two cells emerged from the "math4_proof_chains v1 saturated" moment:

1. **`sharded_capacity_beyond_bundle_bound_v1`** (Stage 1 substrate physics; hidden discovery from math4_v1 smoke sweep)
   - SHARDED storage holds NPROP=16000 at N=8192 = **13.9× beyond classical Plate 1995 bundle capacity bound**
   - BUNDLE storage collapses at Plate bound as expected (positive control)
   - Smoke clean HP at full-N; 3-seed FULL queued on GPU (positions 10-12)

2. **`math4_proof_chains_v2_global_bundle_cpu_v1`** (compositional physics; complements sharded_capacity)
   - Tests same storage-strategy question but at multi-hop chain composition
   - Smoke: SHARDED at L=6, NPROP=50 → 1.000; BUNDLE at same → 0.083 (**gap 0.917**)
   - Substrate-physics-law-tier finding: **bundle storage cannot support chain composition; sharded is load-bearing for compositional capability**
   - 3-seed FULL queued on GPU (positions 13-15)

Both cells have strong CG-prognosis. Expected session-end tally after GPU drain: **27-28 CG**.

## Discipline-development wins (invisible but load-bearing)

3 new disciplines baked into `.claude/agents/exp_dev.md` this session:
1. **GPU-batching mandatory** when speedup available (USER 2026-07-02; commit `4c3e0e933`)
2. **Stage progression 1→2→3→4 don't skip + substrate-doesn't-know + cloud-GPU rules** (batched into same commit)
3. **Multi-seed smoke gate for confidence/contamination cells** (Skunkworks META CG; commit `f07d607c4`)

All 3 now durable across sessions — future cell-authors will get them automatically.

3 additional catches by Skunkworks:
- **META_RULE grep-check** discipline (numpy-in-substrate-costume pattern caught in stretch4_1)
- Amended a factually-wrong prior atom (2026-06-10 T3 with `depends_on: math::T2/fhrr_bind` that was never actually called)
- Novel confidence-signal META rule (smoke-vs-FULL inflation pattern)

## Infrastructure fixes shipped

- **remote_state_cache.json emitter** — dead since 2026-06-29T10:06 (3 days stale). Testbed root-caused (ONLOGON-only trigger not surviving reboot) + fixed with SYSTEM ServiceAccount + ONSTART+ONLOGON triggers + staleness detector in runner_status.py. Commit `a759e38f5`.
- Session dashboards + queue-depth reads now reliable again.

## Substrate-KB caught 2 prior-work collisions this session

- **stretch4_2 cross-domain analogy** — reproduced 2026-06-10 HARD_FAIL to 3 decimals (0.244 Hits@1); substrate-KB caught the prior arc before FULL dispatch (~10 min GPU-time saved)
- **h4b top-1/top-2 gap** — closed 8-month-old un-shipped anchor `bio-calibrated-confidence-B1` (2026-06-08); confirmed the Ma et al 2006 population-code analog does NOT transfer to this substrate at commercial N

## Systematic authoring-bias pattern caught (informational)

3 cells this session showed the "cell defines FHRR primitives but never invokes them" pattern:
- stretch4_1 (Skunkworks caught post-FULL)
- stretch4_3 (cell-author aborted pre-flight per grep-check)
- math4_proof_chains v1 (bundle-vs-sharded discriminator saturated by sharded-storage-oracle)

Skunkworks filed the grep-check META rule. Pattern may extend to more of the un-dispatched sibling cells; will surface as they come through pre-flight.

## Session ledger deltas

- **+7 chain-grade atoms** this session (5 substrate/math + 2 META)
- **+4 measured-mechanism atoms**
- **+2 hard-fails** (density + h4b; both CG-tier closures)
- **+1 middle-band** (lap3_12)
- **+1 amendment** (prior 2026-06-10 mislabel)
- **3 GPU 3-seed FULL cells still cooking** — 6-9 more CG possible when Skunkworks tiers them

## Anti-drift note for future me

Narrative pattern to watch for: mid-session I claimed "26 CG" when disk showed 17; Testbed audit corrected. Framing discipline says: **ALWAYS read atoms.jsonl + cert_ledger.jsonl off-disk before quoting a session tally.** Skunkworks' compact VET reports include current cumulative — those are authoritative.
