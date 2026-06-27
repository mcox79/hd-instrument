# Pre-reg: multihop_bidirectional_meet_in_middle_depth_scaling_v3

**Authored:** 2026-06-27 (exp_dev sub-agent; Research drill 2026-06-27)
**Anchor:** `multihop_bidirectional_meet_in_middle_depth_scaling_v3`
**Cell:** `experiments/exp_multihop_bidirectional_meet_in_middle_depth_scaling_v3.py`
**Routing:** `remote_cpu_queue` (recommended; V_C=200 candidate-loop per query is matmul-bound at deeper depths; alternative GPU via hdi_orchestrator)
**Timeout:** 14400s (4hr; cap)
**USER constraint:** NO LOCAL (USER 2026-06-27)

---

## Background

V1/V2 of this cell line ALREADY HARD_PASSED `CHAIN_GRADE_BIDIRECTIONAL_REVIVAL` at depth=5
(`exp_substrate_multihop_bidirectional_meet_middle_v2_META_M7_rail`, 2026-06-25):

- BIDIR_MEET_MID = **0.620** (cv=0.064)
- Lift over matched-binding forward-only = **+0.297**
- META_M7 rail PASS (REPRODUCE_PV2 = 0.122 in [0.08, 0.25])

The mechanism is settled at depth=5. This V3 cell adds **DEPTH-SCALING** (the sqrt-style
scaling that should only emerge at d>5) plus **2 NEW CONTROL ARMS** that v1/v2 never had:

1. **FORWARD_HALF_DEPTH** -- proves "the MEETING helps", not just "the shorter chain helps"
2. **RANDOM_MEET_BASELINE** -- proves "the TRUE midpoint matters", not "any midpoint works"

---

## Drill-grounded hypothesis (per `notes/research_drill_brain_multihop_M3_bidirectional_meet_in_middle_3x_2026-06-27.md`)

- **Math:** classical bidirectional BFS reduces cost from `O(b^d)` to `O(b^(d/2))`; birthday-paradox
  bidirectional random walk has hitting time `O(sqrt(N))` vs `O(N)` for one-sided.
- **Brain:** 4 independent neural anchors (Pfeiffer-Foster 2013, Foster-Wilson 2006, Tanji-Hoshi 2008,
  Skaggs-McNaughton 1996) confirm forward+backward simultaneous trajectory replay in hippocampus + PFC.
- **Cross-domain:** RRT-Connect (robot motion), forward+backward chaining (theorem provers),
  bidirectional dep resolution (build systems).
- **Substrate-native:** all primitives in place (W.T involution, cosine meet, no external libraries).

---

## ARMS (7 -- per drill spec)

| Arm | Mechanism | Purpose | Predicted top1 at d=5 / d=7 / d=9 |
|---|---|---|---|
| **A: ARM_BASELINE_FORWARD_FULL_DEPTH** | forward-only at depth d | compounding-error ceiling | 0.32 / 0.05 / 0.01 |
| **B: ARM_BIDIR_MEET_MID** | forward d/2 + backward d/2 + meet | THE MECHANISM | 0.55-0.65 / 0.30-0.55 / **>=0.45** |
| **C: ARM_FORWARD_HALF_DEPTH** | forward-only at floor(d/2) | CONTROL: meeting > shorter | 0.476 / 0.328 / 0.226 (0.69^(d/2)) |
| **D: ARM_RANDOM_MEET_BASELINE** | meet at RANDOM midpoint (excludes true floor(d/2)) | CONTROL: true midpoint matters | <0.10 across all depths |
| **E: ARM_MULTISCALE_BIDIRECTIONAL** | meet at {1, floor(d/2), d-1}; sum cosines | scale-invariance probe | TBD |
| **F: ARM_META_M7_RAIL_REPLICATE** | pointer-v2-regime W (2000 bindings); both forward + bidir at d=5 | regime drift check; reproduces v2's 0.620 | forward: [0.08, 0.25]; bidir: >=0.60 |
| **G: ARM_SACRED_SANITY** | forward at K=1 | absolute floor sanity rail | [0.60, 1.00] |

**Depths:** {3, 5, 7, 9}.
**Seeds:** [7, 17, 23, 41, 53] (5; was 3 in v2 -- increased for depth-scaling stability).

---

## HARD_PASS_CHAIN_GRADE_DEPTH_SCALING (4 conditions; ALL must hold)

1. **BIDIR_MEET_MID at depth-9 >= 0.45** (sqrt-scaled survival -- breaks the compounding-error curve)
2. **BIDIR_MEET_MID >= FORWARD_HALF_DEPTH + 0.10 at EVERY tested depth** (meeting is the value, not shorter chain)
3. **BIDIR_MEET_MID >= RANDOM_MEET_BASELINE + 0.15 at EVERY tested depth** (true midpoint matters)
4. **META_M7_BIDIR_REPLICATE at d=5 >= 0.60** (regime sanity rail; confirms drift-free reproduction of v2's 0.620)

### MIDDLE_BAND_PARTIAL_DEPTH_SCALING

2 or 3 of 4 conditions hold.

### MIDDLE_BAND_WEAK

0 or 1 of 4 conditions hold but no HARD_FAIL trigger.

### HARD_FAIL_NO_DEPTH_SCALING

BIDIR_MEET_MID at depth-9 < 0.05 (mechanism collapses; no asymptotic advantage).

### HARD_FAIL_NO_MEETING_PREMIUM

BIDIR_MEET_MID <= FORWARD_HALF_DEPTH + 0.05 at ANY depth >= 5 (mechanism is indistinguishable
from shorter chain; bidirectional reveals no premium over half-depth forward).

### SANITY_BREACH

ARM_SACRED_SANITY_K1 outside [0.60, 1.00] in majority of seeds.

---

## SACRED SANITY rail (locked)

- `RAIL_SANITY_K1`: SACRED_SANITY_K1 in [0.60, 1.00] -- below band = SANITY_BREACH pre-empts verdict
- `RAIL_META_M7_FORWARD`: META_M7_RAIL_FORWARD at d=5 in [0.08, 0.25] -- recorded; informational
- `RAIL_META_M7_BIDIR`: META_M7_BIDIR_REPLICATE at d=5 >= 0.60 -- IS condition 4

---

## CARDINALITY_OK (mandatory per META_RULE_H + USER 2026-06-26 cardinality discipline)

**Per-seed expected records:**
- depth in {3, 7, 9}: 5 arms (A, B, C, D, E) = 15 records
- depth = 5: 7 arms (A, B, C, D, E, F_forward, F_bidir) = 7 records
- depth-independent (G sacred sanity): 1 record
- **total per seed = 23**

**Full-mode expected total:** 23 * 5 seeds = **115 records**
**Smoke-mode expected total:** 7 arms at d=5 + 1 sanity = **8 records**

`HARD_FAIL_CARDINALITY_BREACH` if actual < expected. Cell asserts cardinality_ok flag per seed.

---

## CONFIG

**FULL mode:**
- N=8192, V_C=200, V_P=10, n_predicates=10
- Seeds [7, 17, 23, 41, 53]
- W_v1_regime: n=200 chains, max_depth=9 -> 1800 bindings (long enough for max depth in scan)
- W_pointer_v2: n=200 chains, max_depth=10 -> 2000 bindings (v2 META_M7 regime)
- DEPTHS = [3, 5, 7, 9]; midpoint_hop = depth // 2

**SMOKE mode (discriminator-must-survive-scale per USER 2026-06-26):**
- N=2048, V_C=200, 1 seed [7], DEPTHS = [5] only
- W_v1_regime: n=50, max_depth=5 -> 250 bindings
- W_pointer_v2: n=100, max_depth=10 -> 1000 bindings
- Smoke verifies BIDIR_MEET_MID >= 0.50 AND BIDIR_MEET_MID > FORWARD_HALF + 0.10 at d=5
  BEFORE full dispatch (smoke is the discriminator survival check, not just "cell runs")

---

## Self-test (T1-T12; module-init blocks dispatch if any fails)

- T1: primitives (bipolar / ingest_hebbian / make_deep_chains)
- T2: ARM A forward-full-depth returns valid top1 + per-step accuracies
- T3: ARM B bidir-meet-mid returns valid top1 with correct midpoint_hop
- T4: ARM C forward-half-depth returns valid top1 with correct half_depth
- T5: ARM D random-meet excludes true midpoint
- T6: ARM E multiscale uses correct midpoints
- T7: ARM F (forward + bidir) on v2-regime W
- T8: ARM G sacred-sanity K=1
- T9: forward/backward state-cosine math on clean 1-hop W (both cos > 0.2)
- T10: cleanup primitive byte-equivalence (META_M7 invariant)
- T11: cardinality constants honored
- T12: bands locked (numeric value asserts)

All run at module-init (BEFORE any expensive arm); if any fails, cell exits non-zero before dispatch.

---

## Estimated runtime

V2 reported ~2700s/seed at depth=5 with the single V_C-loop ranking arm dominating.

V3 cost scaling per seed:
- Arms A, C, G: cheap (forward-only, <60s combined)
- Arm B at depth=d: ~2700s * (depth / 5) (backward walk depth dominates inner loop)
- Arm D at depth=d: ~same as B
- Arm E at depth=d: ~3x B (3 midpoints)
- Arm F at d=5: ~2700s

Per-seed total estimate:
- d=3: ~900s (B) + 900s (D) + 2700s (E) = 4500s; plus A/C/G = ~4600s
- d=5: 2700 + 2700 + 8100 = 13500; plus F (forward 20s + bidir 2700) = ~16200s; plus A/C/G = ~16400s
- d=7: 3780 + 3780 + 11340 = 18900s
- d=9: 4860 + 4860 + 14580 = 24300s

**WORRYING: per-seed total ~64000s = 17.7 hr. 5 seeds = ~89 hr.**

**MITIGATION OPTIONS (cell-author flags for orchestrator routing):**
1. Route to GPU (hdi_orchestrator) -- arms B/D/E are pure matmul-bound; expected 5-10x speedup
2. Drop ARM E (multiscale) -- reduces cost ~50%; keeps cardinality at 6 arms
3. Drop seeds 41, 53 -- 3 seeds matches v2 cadence; cv estimate weaker
4. Drop depth=9 -- cuts most expensive arm; loses sqrt-scaling test (defeats the cell's purpose)

**RECOMMENDED:** route to GPU. If GPU unavailable, drop ARM E first (multiscale is exploratory;
the 3 core arms B/C/D + F directly serve HARD_PASS conditions).

Per-seed checkpointing + atexit synth ensures partial seed completion still lands metrics.

---

## BIAS guards (per USER 2026-06-24 master checklist)

- **BIAS-Q (suspect 1.000):** verdict flags any arm hitting >= 0.999 at V_C=200 (small enough that 1.000 is suspicious not a saturation)
- **BIAS-R (codebook contamination):** SAME E + R for all arms; W rebuilt per regime from same triples; documented same-cell construction
- **BIAS-O (basis vs use-case):** V_C=200 candidate-set INCLUDES true_Z (intentional; scoped flag in DESIGN_NOTE)
- **BIAS-S (band calibration):** relative bands (BIDIR - FORWARD_HALF, BIDIR - RANDOM) enforced at EVERY depth, not just absolute top1
- **BIAS-N (Cramer-Rao referent):** sacred-sanity K=1 + META_M7 forward rail + META_M7 bidir rail = 3 reference rails
- **BIAS-P (anisotropy hurts retrieval):** beta-sweep arm dropped from v3 in favor of K=1 sanity (closer to drill spec G arm); future cell can re-add

---

## What this cell answers

- **HARD_PASS_CHAIN_GRADE_DEPTH_SCALING:** substrate has sqrt-style multi-hop scaling; meeting (not just shorter chain) is the value; true midpoint matters; v2 regime is drift-free. Route to Skunkworks for chain-grade portfolio addition (M3 stage-3 compositional-understanding building block).
- **MIDDLE_BAND_PARTIAL_DEPTH_SCALING:** mechanism survives partially; queue learned-reverse-W variant (drill primitive A) or bidirectional SR closure (drill primitive B).
- **HARD_FAIL_NO_DEPTH_SCALING:** mechanism has compounding-error floor; the v2 0.620 was a shallow-depth artifact; bidirectional has no asymptotic advantage. Retire as substrate-product positioning claim.
- **HARD_FAIL_NO_MEETING_PREMIUM:** bidirectional gain is entirely explained by shorter chains; the meeting itself doesn't help. Major framing correction needed for v2's chain-grade claim.

---

## DISCRIMINATOR-MUST-SURVIVE-SCALE check (USER 2026-06-26)

Smoke at full V_C=200 at depth=5 must show BIDIR_MEET_MID >= 0.50 AND
BIDIR_MEET_MID > FORWARD_HALF_DEPTH + 0.10 BEFORE full dispatch.

If smoke fails: do NOT dispatch full. v2 already showed 0.620 at d=5 with V_C=200 so the
smoke is mostly an integration test; the discriminator surviving scale = the 2-arm relative
check.

---

## NO_SILENT_EXCEPT (USER 2026-06-26)

All exception handlers in the cell either halt or record-and-re-raise. The `atexit` synth
re-raises after logging so the runner sees the failure.

---

## Per-arm self-test independence

Each arm is invokable independently with the same E/R/W inputs; arms do NOT depend on
prior arm state. This enables debugging single-arm failures without re-running the full cell.
