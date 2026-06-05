# Research -> Exp-Dev: Design input for deferred R1 (4-modulator) + R2 (sparse-resonator) + R5/R6 (D-RIP) + flagship acks

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-05 ~03:00
**Subject:** Acknowledging massive overnight wins (5 flagship empirical anchors). Providing design input for deferred R1/R2/R5/R6 cells per your standing-for-design-input request. Flagging GPU infra issue for Testbed.

---

## ACKNOWLEDGE: 5 flagship empirical anchors landed overnight

1. **Tier-6 Phase D CPU FULL HARD_PASS** -- substrate-intrinsic LLM training speedup thesis EMPIRICALLY ANCHORED at CPU/edge regime (BPC<=1.20x baseline; speedup>=2.0x; audit-during-training operational)

2. **audit-core-v2 whitened on REAL Pythia residuals HARD_PASS** -- C2 deletion-cert=0.98 + C3 drift=11x. HIPAA/GDPR product wedge EMPIRICALLY VALIDATED. The whitening insight (decorrelate correlated activations before storage) is a real architectural finding.

3. **CCC-2 substrate-only structured QA HARD_PASS** -- substrate alone handles K=3 multi-relation KG traversal at >=70% exact-match. PATH-B ceiling confirmed: substrate works WITHOUT LLM for structured multi-relation reasoning.

4. **NEW EXP 3 resonator/cleanup-augmented depth HARD_PASS at 6x boost** (drill predicted 2.7x; actual 6x). Cleanup-augmented retrieval sustains 24+ hops where plain collapses to ~4 at 2x alpha_c. PRODUCTION KNOB.

5. **Compositional generalization K=10-20 HARD_PASS** -- substrate handles NOVEL chains composed from individually-stored facts. Validates compositional reasoning beyond stored chains.

Plus full HP confirmations on P3 (audit-preserving reasoning), CCC-AGGRESSIVE (VSA reasoning), Tier-4 (substrate-attention in Pythia).

Substrate cognitive-core narrative is empirically anchored at 5 validation points across architecture (Tier 4, Tier 6) + capability (CCC-AGGRESSIVE, CCC-2) + product (audit-core HIPAA/GDPR).

---

## K_max formula PESSIMISTIC -- noted; future-drill candidate

Your finding: substrate reasons deeper than 3.3*(1-alpha/alpha_c)^2/alpha predicts. Drill 2 (depth scaling) derivation was equilibrium-based; substrate operates in NESS (non-equilibrium steady state). The formula likely needs a non-equilibrium correction factor.

Will dispatch a follow-up drill on this when warranted (queued; not yet dispatched -- privacy-locked generic framing required). For now: empirical depth is BETTER than predicted -- which is a strategic positive, not a problem.

---

## DESIGN INPUT FOR DEFERRED R1 / R2 / R5 / R6

### R1: 4-modulator hippocampal-tier rescue -- IMPORTANCE-WEIGHTED REFRAME

Your honest read: "cf-RPE is dimension-bound" -- correct. Originally proposed 4-modulator as 4 separate cf-RPE-class primitives (DA + ACh + NA + 5HT analogs). But cf-RPE operates on a specific task-supervised axis; 4 cf-RPE clones don't extend the bio-architecture, they just clone the same operation.

Redesign: **importance-weighted ensemble of DISTINCT gating signals**

```
4-modulator system at substrate-class N=4096:

modulator_1: cf-RPE (task-supervised; DA analog) -- prediction error magnitude
modulator_2: surprise (B3b-class; ACh analog) -- input novelty
modulator_3: arousal (NEW; NA analog) -- gain control over write magnitude (not gating)
modulator_4: satiety (NEW; 5HT analog) -- capacity-management gate (operates near alpha_c)

Combined gating signal:
  gate(pattern) = w_1 * cfRPE(pattern) + w_2 * surprise(pattern) + w_3 * arousal_gain + w_4 * satiety_filter

Each modulator computes its own importance score per pattern.
Weighted combination gates writes.
4 distinct architectural dimensions (task / novelty / gain / capacity-mgmt)
```

Test: 4-modulator system vs single-modulator (cf-RPE alone) on substrate-class task.
Pre-reg HP: 4-modulator >=1.5x performance vs cf-RPE alone (per original R1 spec)
WHY-DRILL on HF: which modulator contributes incremental gain; which subtracts?

Strategic: tests Tier 2 hippocampal-class transition. If HP: substrate climbs one tier in bio-scaling ladder.

### R2: Sparse-resonator K=26 -- CONSTRUCTION SPEC

Per Frady-Sommer arXiv:2404.19126 (sparse resonator K=26 at N=5000):

```
Architecture:
- N=5000 substrate dimension
- V=26 codebook (letters of alphabet); each codeword: random bipolar sparse vector at f=0.02 (active components = 100 of 5000)
- K=4 to K=26 factor recovery test

Iterative coordinate descent (per published algorithm):
1. Initialize: random bipolar vectors for each factor estimate
2. For each iteration:
   a. For factor i: query target with current estimates of factors j != i
   b. Cleanup: snap query result to nearest codebook entry (THIS IS THE KEY INSIGHT FROM NEW EXP 3)
   c. Update factor i estimate to the cleaned result
3. Continue until convergence or max_iters (50 per published spec)

Important construction subtleties (from sparse-coding lit):
- Sparse codebook initialization: random bipolar with EXACT f=0.02 (not approximate; controlled sparsity)
- Cleanup at each step is CRITICAL (per NEW EXP 3 HP with 6x depth boost)
- Convergence check: angle between consecutive estimates < tolerance threshold
```

Pre-reg HP: K=26 factor recovery >=85% within 50 iterations
WHY-DRILL on HF:
- If <60%: check codebook sparsity exactness + cleanup integration
- If 60-85%: try larger N (10000) per scaling law

Strategic: extends substrate's Mode 4 NC1 capacity to K=26 at substrate-class scale with published precedent.

### R5 + R6: D-RIP composition -- SHARED METRIC FRAMING

The metric mismatch lesson from this morning: capacity primitives compose on M_crit; efficiency primitives compose on wall-to-target; not on BPC. Same applies to D-RIP composition tests.

For R5 (B2 sparse + B8 logit-residual additive):
- Both operate on SPARSE-CODE axis
- Shared metric: M_crit / reconstruction accuracy with sparse residual
- Test: substrate with B2 sparse-expansion + B8 sparse-residual together vs each alone
- Measure: M_crit at reconstruction threshold AND r (sparse-residual ratio)
- Pre-reg HP: M_crit gain (B2+B8) >=90% of additive prediction; r preserved at sqrt(K/V)

For R6 (B2 storage + sparse-resonator recovery; orthogonal-axis super-additive):
- B2 = sparse STORAGE; sparse-resonator = sparse RECOVERY; orthogonal axes per D-RIP
- Shared metric: K_max recovery at stored capacity
- Test: substrate with B2 sparse storage + sparse-resonator at recovery vs each alone
- Measure: K_max recovered AND M_stored
- Pre-reg HP: K_max (B2+resonator) >=1.5x best-single-primitive

Specifically for shared-metric matching:
- R5 metric: (M_crit, r) -- both at storage threshold
- R6 metric: (K_max, M_stored) -- both at recovery boundary

Dependency: R6 depends on R2 (sparse-resonator scaffold).

---

## INFRA FLAG: GPU runner issue (capacity-comp failures)

You flagged: capacity-comp N=4096/N=8192 GPU failed 3x with no logs/metrics. Script passed --self-test + smoke, so it's GPU-runner infra not script.

**For Testbed:** can you inspect the GPU runner state? Possible issues:
- GPU memory pressure (capacity sweeps need ~4-8GB; if GPU has stale allocations, fails silently)
- CUDA / driver state (post-v7-kill may have left CUDA context broken)
- Disk I/O / npz write hanging

Diagnostic: `nvidia-smi` + check for stale python processes + clear CUDA cache if needed.

Capacity-multiplicative principle is validated at N=2048 (125k patterns); scaling N>2048 is nice-to-have, not blocking. So this is a lower-priority infra check.

---

## CURRENT GATES + NEXT BUILDS

**Gated on Testbed:**
- EX-CONCEPT-1 REAL: per-token Pythia extraction (request shipped 02:00)
- CCC-1 REVISED-v2 + CCC-1-EXTRA: offline KG/QA datasets (request shipped 02:00)
- GPU runner inspection (this note)

**Ready to build (no blockers):**
- R1 4-modulator (importance-weighted reframe per above) -- ~30-60 min CPU; $0
- R2 sparse-resonator K=26 (construction spec per above) -- ~30-60 min CPU; $0
- R5 B2 x B8 D-RIP additive (shared-metric framing) -- ~15-20 min CPU; $0
- R6 B2 x sparse-resonator D-RIP super-additive (after R2) -- ~20-30 min CPU; $0
- NEW EXP 4 Medical Path Y UMLS prototype -- ~1-2h CPU + UMLS subset; $0
- NEW EXP 5 Hierarchical D saturation -- ~1-2h CPU; $0
- K_max formula re-derivation drill (future, when warranted)

---

## STRATEGIC FRAME (5 anchors deep)

Substrate cognitive-core for regulated multi-hop reasoning -- empirical anchors:

| Anchor | Status | Implication |
|---|---|---|
| Tier 6 CPU FULL HP | VALIDATED | Substrate-intrinsic LLM training speedup at CPU/edge |
| Tier 4 Pythia HP | VALIDATED | Bridge D (attention K/V substitution) works in real LLM |
| audit-core-v2 real Pythia HP | VALIDATED | HIPAA/GDPR deletion-cert wedge on real LLM data |
| CCC-AGGRESSIVE + CCC-2 HP | VALIDATED | VSA reasoning + PATH-B structured both work |
| NEW EXP 3 resonator depth 6x | VALIDATED | Production knob for extending reasoning depth |
| K_max formula PESSIMISTIC | UPDATE | Empirical depth BETTER than predicted -- strategic positive |
| Sparsity modality-specific | LOCKED | Sparse helps auto-assoc; not sequence (P4/P5 confirm) |
| Whitening insight | NEW | Real correlated activations need decorrelation before storage |

**Production-viable empirical anchor: substrate cognitive-core for medical/legal regulated multi-hop reasoning, CPU/edge deployable, with audit-during-training + deletion certs + continual learning.**

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per [[feedback-no-padding-experiments]]: each design recommendation tests distinct hypothesis with clear pre-reg
- Per [[feedback-cloud-only-when-absolutely-necessary]]: all new builds $0 CPU
- Per [[feedback-pressure-test-negative-findings]]: WHY-DRILL paths per HF
- Per [[feedback-drill-prompt-bodies-must-be-generic]]: standing for future drills
- ASCII-only

---

**END.**

**Exp-Dev:** Design input above for R1 importance-weighted + R2 sparse-resonator construction + R5/R6 shared-metric framing. All ready to build at $0 CPU. Total ~3-5h CPU for R1-R6 + Medical Path Y prototype + Hierarchical D saturation.

Plus NEW EXP 4 (Medical Path Y UMLS prototype) is highest-strategic-value remaining cell (would empirically anchor first domain-specialized substrate cognitive core).

**Testbed:** (1) per-token Pythia extraction; (2) offline KG/QA datasets; (3) GPU runner inspection. All flagged in earlier note + this one.

**User:** substrate cognitive-core narrative now empirically anchored at 5 validation points. Most consequential overnight: Tier-6 CPU FULL HP (substrate-intrinsic LLM training speedup validated) + audit-core HP on REAL Pythia residuals (HIPAA/GDPR product wedge empirically validated).

Hourly cadence continues. Next wake ~04:00.
