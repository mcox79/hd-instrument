# Phase-diagram gap analysis — next 3-5 cells for Director hand-off

**Filed:** 2026-07-01 03:25 UTC
**Author:** research (Opus)
**Trigger:** USER "explore phase diagram space for all characteristics" (Full Auto 2026-07-01 ~03:20 UTC)
**Input frame:** 16-axis TRUE taxonomy (`director_TRUE_PHASE_DIAGRAM_COVERAGE_2026-06-30.md`) + Stage 1/2/3 characteristics table + META catalog (AC/H/K/L/Q/AO/AR/AW/AX)
**Excludes (per USER):** routing_geometry_v2, seqbind_N_dim, bytes_per_fact, compression_pareto, sparsity_x_encoder, K-cliff v2. No intermediate-confidence-band adaptivity cells (deferred to M3 cortex). No Stage 4.

---

## HEADLINE

The three highest-value uncovered axes are **F-cleanup-family-at-WM-scale**, **J-order-binding-family**, and **H-hierarchical-bank-codebook**. All three are outer-axis substitutions on primitives currently locked at a single family; all three have cross-domain bio + matsci + neuromorphic support; and all three admit CG-eligible discriminators without requiring intermediate-confidence-band noise. Two more (P-3-tier generational, D×O binding-op × capacity cross-product) are ranked below as MEDIUM.

---

## Ranked list (expected CG probability × capability payoff; deflated 0.20)

### 1. **Axis F — cleanup-family at WM K-cliff scale** (CG=0.55, payoff=HIGH)

**Why it matters.** Axis F is CG at PC scale only (4 cleanups convergent, PC v2 N-scaling law). WM chain-grade uses Hadamard bind + WTA-like readout with cleanup UNTESTED at K-cliff regime. If Modern-Hopfield or iterative cleanup lifts K_cliff(B) above 256·B floor, we gain a substrate-only capacity lever without changing binding.

**CG-eligible design.** 4 cleanups × 3 B={4,16,64} × K∈{K_cliff/2, K_cliff, 2·K_cliff}. Discriminator: cleanup-family ordering must be seed-consistent AND at least one non-classical cleanup must lift recall ≥0.10 above WTA at K=2·K_cliff. Regime: N=8192, B=16, K=512. Pre-reg CARDINALITY_OK=36 (4×3×3). Compose with capacity multi-bank α-K CG primitive per META_RULE_AT.

**Cross-domain support.** Bio: CA3 recurrent + CA1 sparse readout literature (Rolls-Treves) predicts iterative cleanup dominates at capacity edge. Matsci: modern-Hopfield exponential capacity (Ramsauer 2020). Neuromorphic: memristor crossbar cleanup dynamics show iterative > single-step at cliff (Sebastian 2020). Three-drill support → **flag for 5x-drill escalation if landed HP.**

**Risk.** META_RULE_Q trip if Modern-Hopfield hits 1.000 at K=K_cliff (by-construction near-saturation lookup). Mitigation: report K=2·K_cliff cross-arm as chain-grade discriminator, not K=K_cliff.

### 2. **Axis J — order-binding-family** (CG=0.50, payoff=HIGH)

**Why it matters.** Cyclic-shift is the ONLY order-binding primitive at chain-grade; permutation / phase-rotation / learned-position untested. Sequence-binding K-cliff is chain-grade at cyclic-shift; axis-J substitution tests whether K* scales differently under permutation (predicted: yes, log-linear vs. linear).

**CG-eligible design.** 3 order-binding ops (cyclic-shift baseline / random-permutation / phase-rotation) × K∈{50,100,200} × 3 seeds. Discriminator: at least one order-binding op must produce K*(op) differing by ≥0.15 log10-units from cyclic baseline, with 3-seed cross-seed cv<8% per op. Pre-reg: order-binding pair-distinctness (META_RULE_AX) MANDATORY.

**Cross-domain support.** Bio: hippocampal theta-phase precession (Buzsaki) supports phase-rotation as order-binding candidate. Matsci: no direct. Neuromorphic: reservoir-computing literature (Jaeger 2001) shows permutation is order-preserving but phase-lossy. Two-drill support only → NOT 5x-drill candidate yet.

**Risk.** META_RULE_AX arm-distinctness across family axis — if phase-rotation and cyclic-shift produce mechanism_hash-identical outputs at N=8192 (rotational aliasing), the arm collapses. Mitigation: cell-author must verify arm mechanism_hash distinct at smoke pre-tier (H discipline).

### 3. **Axis H — hierarchical-bank codebook** (CG=0.45, payoff=HIGH)

**Why it matters.** Axis H is CG at flat / partition-by-source / coarse-grain (3 structures). **Hierarchical bank UNTESTED.** If a 2-level hierarchical bank (context-router → sub-bank) lifts effective capacity above flat B·K_per, it's a Stage 2 architectural lever composable with existing multi-bank CG.

**CG-eligible design.** 3 codebook structures (flat / partition-by-source baselines / hierarchical-2-level) × M∈{4K, 16K, 64K}. Discriminator: hierarchical must show routing_acc>0.95 AND capacity-per-slot ≥1.2× flat baseline at M=64K. Compose with ANCHOR 1 partition-by-source CG per META_RULE_AT.

**Cross-domain support.** Bio: cortical column hierarchy (Mountcastle-Felleman); matsci: content-addressable memory hierarchy; neuromorphic: hierarchical crossbar arrays (IBM TrueNorth). **Three-drill support → flag for 5x-drill escalation if landed HP.**

**Risk.** By-construction saturation if router perfectly separates sub-banks (META_RULE_Q + META_RULE_AR). Mitigation: introduce sub-bank collisions via imperfect router; check routing_acc<1.000.

### 4. **Axis P — 3-tier generational (MEDIUM; CG=0.35, payoff=MED)**
Extends TWO_TIER CG to STM→ITM→LTM. Bio well-supported (systems consolidation, Squire-Alvarez). Discriminator: ITM tier must add ≥0.05 retention at t=100 replays over 2-tier. Compose with NREM replay CG.

### 5. **Axis D × O — binding-op × capacity cross-product (MEDIUM; CG=0.30, payoff=MED)**
Currently binding-op is MM at PC scale only. Cross-product with capacity α-K CG at WM regime tests whether binding-op choice interacts with K_cliff. Discriminator: at least one non-Hadamard op must show K_cliff shift ≥15% at α=0.5.

---

## Next-cell recommendation (Director hand-off to hdi_exp_dev)

**Cell #1 to author (highest CG × payoff): "cleanup_family_WM_K_cliff v1"** — 4 cleanups (classical Hopfield / Modern Hopfield / iterative / WTA baseline) × 3 B × 3 K, N=8192, 3 seeds. Compose ANCHOR H multi-bank CG. Pre-reg: CARDINALITY_OK=36, META_RULE_AX arm-distinctness across cleanup family, META_RULE_Q suspect-1.000 at K=K_cliff, META_RULE_AT compose with capacity CG. Discriminator fires at K=2·K_cliff (well above WTA saturation).

**Falsifiable predictions.**
- HARD_PASS: at least one non-classical cleanup lifts recall ≥0.10 above WTA at K=2·K_cliff across 3 seeds (cv<8%), pair-distinctness True across all 6 cleanup pairs.
- HARD_FAIL: all 4 cleanups collapse to within ±0.05 recall at K=K_cliff/2, K_cliff, 2·K_cliff (cleanup-family capability-orthogonal at WM scale).
- MIDDLE_BAND: cleanup ordering seed-inconsistent OR one cleanup collapses to 0 (Hopfield-2-step failure mode already CLOSED-negative at hippo v2).

**Cross-thread synthesis.** Cleanup PC v2 CG + capacity multi-bank α-K CG compose via META_RULE_AT; the composition is the substrate-product implication — a modular capacity-cleanup lever that Director can turn on/off per capability class.

**Substrate-product implications.** Landing HP would resolve axis F outer at WM scale (adds to E/H/L/N/O CG list → 7 axes outer-CG), close the "cleanup family untested for WM" gap in `director_TRUE_PHASE_DIAGRAM_COVERAGE` doc, and unblock next-cycle sparsity × cleanup cross-product (axis C × F).

**Citations (verified count):** 4 domain-mapping papers (Rolls-Treves 1994 hippocampus; Ramsauer 2020 modern-Hopfield; Sebastian 2020 memristor crossbar; Buzsaki phase-precession) + META catalog 5 rules (H/K/Q/AT/AX) + coverage doc gap list item #1. Novel-synthesis: capacity × cleanup composition prediction — P deflated 0.55 (novel-synthesis cap 0.50 does NOT apply because both primitives are separately CG; composition prediction, not novel-mechanism).

---

**One-liner Director hand-off:** Author `cleanup_family_WM_K_cliff_v1` — 4 cleanups × 3 B × 3 K compose with capacity multi-bank CG at N=8192 to close axis F outer gap at WM regime; CG=0.55, payoff=HIGH, 5x-drill-escalation eligible if HP.

Follow-up cells (order): #2 order-binding-family v1 (axis J), #3 hierarchical-bank v1 (axis H), then #4/#5 as pipeline permits.
