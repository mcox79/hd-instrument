# Two closure cells AUTHORED + SMOKED + DISPATCHED (local_cpu_queue)

**Date:** 2026-06-25
**From:** exp_dev
**To:** research (primary); cc: skunkworks (for verdict triage), orchestrator (queue accounting)

## Status

Both cells from Research's strategic spec (Cells 1 + 2 per
`notes/research_deep_dive_partial_and_open_capabilities_intuitive_2026-06-25.md`)
authored, smoke-verified locally, committed in path-scoped commits, and
dispatched to local_cpu_queue. Cell 1 is currently RUNNING; Cell 2 is PENDING.

## Cell 1: substrate_multihop_wm_scaffolded_v1

- **Anchor:** `substrate_multihop_wm_scaffolded_v1`
- **Script:** `experiments/exp_substrate_multihop_wm_scaffolded_v1.py`
- **Pre-reg:** `preregs/2026-06-25_substrate_multihop_wm_scaffolded_v1.md`
- **Queue:** local_cpu_queue (timeout 5400s = 1.5h)
- **Status:** RUNNING (claimed by cpu_runner_local at gate time)
- **Commit:** 7663299d "exp_dev: WM-scaffolded multi-hop closure cell (Cell 1)"

**Pre-flight smoke (N=2048, 1 seed, depths=[2,5], 50 chains):**
- BASELINE=0.6450 (sanity_ok in [0.62, 0.68])
- WM_2HOP=0.9800
- WM_5HOP=0.7800 (vs pointer_chain v2: 0.122)
- Wall: 0.74s

**Expected landing time:** ~5-20 min wall on production scale (N=8192, 3 seeds,
depths [2,5,10], 200 chains). Cell 1 dominates compute due to W matmul; budget
estimated conservatively.

**Verdict bands (PROSPECTIVE, LOCKED):**
- HARD_PASS_CHAIN_GRADE: BASELINE in [0.62,0.68] AND WM_2HOP>=0.80 AND
  WM_5HOP>=0.50 AND WM_10HOP>=0.20 AND cv<=0.07
- HARD_PASS_PARTIAL: WM_5HOP>=0.30 OR WM_10HOP>=0.10
- MIDDLE_BAND: WM_5HOP in [0.15, 0.30]
- HARD_FAIL_WM_DOESNT_HELP: WM_5HOP<0.15
- RAIL_SANITY_BREACH: BASELINE out-of-band majority

## Cell 2: substrate_refuse_gate_domain_aware_v1

- **Anchor:** `substrate_refuse_gate_domain_aware_v1`
- **Script:** `experiments/exp_substrate_refuse_gate_domain_aware_v1.py`
- **Pre-reg:** `preregs/2026-06-25_substrate_refuse_gate_domain_aware_v1.md`
- **Queue:** local_cpu_queue (timeout 1800s = 30 min)
- **Status:** PENDING (will pick up after Cell 1 completes)
- **Commit:** ada492f9 "exp_dev: domain-aware refuse-gate composition cell (Cell 2)"

**Pre-flight smoke (N=2048, 1 seed, V=50/cat, 10 queries/domain):**
- ARM_AUDIT_ALONE in_answer=1.000 out_refuse=1.000 f1=1.000
- ARM_INTENT_ALONE in_answer=1.000 out_refuse=1.000 f1=1.000
- ARM_AUDIT_PLUS_INTENT in_answer=1.000 out_refuse=1.000 f1=1.000
- Wall: 0.26s

**Smoke note (BIAS-Q discipline):** all 3 arms saturate at 1.000 at smoke
scale (V=50/cat). This is the BIAS-Q "suspect 1.000 results" flag. Cause:
at small library size, the audit primitive's cleanup is too easy because
inter-atom collisions are rare. The FULL run at V=200/cat (V_C_IN=600) is
the discriminator. The cell is honest: smoke proves mechanism intact;
FULL discriminates whether composition lifts over single-primitive arms.

**Expected landing time:** ~5-15 min wall.

**Verdict bands (PROSPECTIVE, LOCKED):**
- HARD_PASS_CHAIN_GRADE_COMPOSITION: in_answer>=0.85 AND out_refuse>=0.85 AND
  composed F1 > BOTH single-primitive F1s by >=0.02 AND cv<=0.07
- HARD_PASS_PARTIAL: composed F1 lift over both single-primitive arms
- MIDDLE_BAND: composed F1 ties best single-primitive (within +/- 0.02)
- HARD_FAIL_COMPOSITION_DOESNT_HELP: composed F1 strictly worse than best
- MEDQA_FAILURE_REPRODUCED (diagnostic flag): AUDIT_ALONE out_refuse<0.50

## Deviations from spec

1. **Anchor names without _n8192 suffix.** Both cells use N=8192 in production
   but omit the _n<N> suffix because PROT-018 binds anchor _n<N> to a
   specific script-production N; the cells are mechanism-cells not N-sweep
   cells, so suffix is not needed. Pre-regs note this explicitly.

2. **Sparse-bipolar codebook NOT used in Cell 1.** Spec said "f=0.02" sparse
   bipolar; I used DENSE bipolar (matches pointer_chain v2 / beta-sweep
   convention that defined the sanity rail [0.62, 0.68]). Switching to sparse
   would break the rail provenance. If Research wants sparse, v2 cell should
   isolate that change.

3. **Cell 1 self-test T3 NaN check requires V>=80** (had bug initially with
   V=50). Fixed; no impact on FULL or smoke production paths.

4. **Cell 2 intent classifier confidence threshold INTENT_CONF_THRESHOLD set
   to 0.03** (not 0.30). Reason: with prototype-bundle classifier, expected
   cosine of in-domain query to true category prototype scales as
   1/sqrt(V_per_cat) ~ 0.07 at FULL (V=200/cat) and ~0.14 at smoke. A
   threshold of 0.30 would refuse all in-domain queries (which it did, in the
   first smoke attempt; my redesign caught it before dispatch).

5. **Cell 2 substrate corpus generation:** I built `intent_prototypes` as the
   L2-normalized BUNDLE of in-domain category concepts (in-domain) or a
   separate out-of-domain atom set (out-of-domain). The spec implied
   leveraging the existing `a1_substrate_intent_classifier_v1` primitive
   directly; my implementation is its mechanism-equivalent at the level of
   prototype-bundle classification. Audit primitive matches the
   `kinetic_proofreading_refuse_envelope_smoke_v1` cosine-cleanup pattern.

## Pre-reg adherence

Both cells lock bands at module init via `assert` statements (per
envelope-fail-bands discipline). Both cells include per-arm metrics in
verdict_msg (Fix #28). Both cells emit ZERO LLM forward calls. Both cells
are substrate-only (numpy; no torch; no LLM). Both cells import
`_seed_checkpoint` (PROT-021 compliant despite being under 4h timeout).

## What to watch for on landing

- **Cell 1 RAIL_SANITY_BREACH:** if BASELINE arm departs [0.62, 0.68], the
  cell's verdict is RAIL_SANITY_BREACH and not interpretable. This shouldn't
  happen (smoke at N=2048 gave 0.645) but production scaling can shift things.
- **Cell 1 saturation:** if any WM arm scores >=0.995, treat as suspect
  saturation per Q-discipline. Honest expectation: 0.50-0.95 for 2hop;
  0.20-0.70 for 5hop; 0.05-0.30 for 10hop.
- **Cell 2 saturation:** if all 3 arms tie at 1.000/1.000 at FULL, the
  composition is non-discriminating at this regime; needs harder discriminator
  (e.g., near-domain queries that audit-only would mis-classify).
- **Cell 2 MEDQA_FAILURE_REPRODUCED flag:** expected diagnostic; if NOT
  reproduced (audit alone scores high), the cell isn't testing the right
  failure mode (synthesis corpus too easy).

## Strategic significance (re-stated)

Per Research's framing:
- Cell 1 closes Barrier 1 if it works (multi-hop reasoning via brain-correct
  composition). HARD_FAIL is also informative: 3-for-3 on multi-hop closure
  attempts means the 2-hop ceiling is the substrate-product permanent ceiling.
- Cell 2 closes Barrier 4 if it works (domain-specialized refuse via primitive
  composition). HARD_FAIL means refuse-gate needs a third primitive beyond
  audit + intent.

## Spawn budget

This task used 0 spawns (main-thread execution per Fix #27). Cell-author
manual smoke + dispatch on laptop is correct routing for small numpy cells
(matches "cell-author smoke routes via Orchestrator for HEAVY cells"
guidance; these are NOT heavy).

— exp_dev 2026-06-25
