# research: next batch standard cells synthesis -- 2026-06-06

Filed-by: research sub-agent
Trigger: orchestrator synthesis task (free-form)
Pause state: check data/orchestrator_paused.flag before acting

---

## HEADLINE

12 ranked CPU/GPU cells cover the four open fronts (capability-matrix gaps,
framework validation, production gates, compound math) with wall times from
<2 min (HOC1) to ~2h (NRO-1). Cheapest-decisive trio: HOC1, EFFECTIVE-RANK,
analogy_map. Highest-leverage trio: DIMSPARSE3-alpha, CS-1, auditable_khop_kf1.
P_deflated (novel-synthesis claims) = 0.35-0.45 after calibration penalty.

---

## Context: what the queues show

Both overnight_queue and remote_cpu_queue are empty (0 pending/running).
Pipeline refill is urgent; no runners are blocked on each other.
All 12 cells below can be dispatched immediately with no dependency conflicts.

---

## 12 Ranked Cells

### Rank 1 -- HOC1 (word bigram order-sensitivity)

Anchor name: hoc1_word_bigram_v1
Strategic value: Resolves the hallucination word-order gap. KF-1 AUC 0.975
hard reached on easy/medium; hard negation and transposition cases are the
residual gap. HOC1 is the cheapest available path to close it, and it is a
PRODUCTION GATE (KF-1 negation gate text says "ships with ... NLI-aware MiniLM"
-- HOC1 either replaces that requirement or confirms NLI remains mandatory).
Wall + tier: <2 min CPU.
HP: bigram-order signal AUC >= 0.70 on hard-negation test set
MID: AUC in [0.55, 0.70)
HF: AUC < 0.55 (no word-order signal; NLI path remains mandatory)
Why-now: Rank 1 because it is trivially cheap, has no dependencies, and
directly closes or re-routes the KF-1 negation gate. Queue it first; result
arrives before any other cell and immediately re-prices NEG1 priority.

---

### Rank 2 -- EFFECTIVE-RANK SVD diagnostic

Anchor name: effective_rank_svd_v1
Strategic value: Validates the intrinsic-dim-limited retrieval framework
(d_eff ~50-80 in 384-dim ambient). This is the Drill W rank-1 cheap decisive
test for the ENTIRE Donoho-Tanner and sparse-KEY theoretical stack. If
d_eff < 100 confirmed empirically, the framework unification is real and all
downstream DT-phase cells inherit the justification.
Wall + tier: 5-10 min CPU.
HP: d_eff measured in [40, 100] range on real MiniLM embeddings, consistent
across N=4096 and N=16384 (ratio within 20%)
MID: d_eff in [100, 200]; partial support for intrinsic-dim hypothesis
HF: d_eff > 300 (embeddings are not low-rank; DT framework applicability
weakened; reassess sparse-KEY operating regime claims)
Why-now: Rank 2 because it validates the theoretical scaffolding all mid-
ranked cells stand on. 10 min cost, framework-level payoff.

---

### Rank 3 -- analogy_map (3rd capability class)

Anchor name: analogy_map_v1
Strategic value: Confirms or denies a 3rd independent capability class
(compositional analogy: A:B::C:? via arithmetic in bundle space). Direct
product implication: if analogy_map HARD-PASS, the substrate can solve
relational reasoning natively without any LLM call. 3 min CPU.
Wall + tier: 3 min CPU.
HP: analogy accuracy >= 0.70 on held-out (A,B,C,?) triples; top-1 correct
MID: accuracy in [0.50, 0.70)
HF: accuracy < 0.40 (chance-level; algebraic analogy does not work in this
binding regime; arithmetic in bundle space fails for relational queries)
Why-now: Rank 3 because it is the cheapest path to discovering a new
capability class. If passes, immediately elevates product story.

---

### Rank 4 -- frame_slot_fill k=16 (multi-attribute entities)

Anchor name: frame_slot_fill_k16_v1
Strategic value: Confirms whether the substrate can store and retrieve
multi-attribute entities (frame: {entity: X, attr1: Y, attr2: Z}) at k=16
slots without interference. Directly relevant to knowledge-graph and
compliance-sidecar use cases where each stored fact has multiple fields.
Wall + tier: 2 min CPU.
HP: slot fill accuracy >= 0.90 at k=16 distinct frames
MID: accuracy in [0.70, 0.90)
HF: accuracy < 0.60 (multi-slot binding breaks at k=16; frames must be
split or capacity must be reduced)
Why-now: Fast, cheap, resolves a real product question about how many
attributes a single stored entity can carry.

---

### Rank 5 -- CS-1 Donoho-Tanner algebraic audit

Anchor name: cs1_dt_algebraic_audit_v1
Strategic value: PARADIGM-SHIFT cell. Audits the full Donoho-Tanner phase
boundary (delta=M/N, rho=k/M) for the substrate's operating regime. Confirms
or refutes the unified framework that all activation-regime rescue axes map
onto a single DT phase diagram. If CS-1 passes: every subsequent capacity
rescue decision becomes algebraically principled rather than empirical
trial-and-error.
Wall + tier: ~1h CPU.
HP: DT phase prediction matches empirical (success/fail) for >=8 of 10 test
points spanning the critical boundary; predicted rho_c within 15% of observed
MID: 6-7 of 10 correct; framework partially predictive
HF: fewer than 5 correct (DT framework does not apply to this binding regime;
sparse-KEY theory needs alternative scaffold)
Why-now: Rank 5 because it is 1h (not trivial) but the payoff is framework-
level. Once validated, it accelerates every subsequent compound-axis design.
Batched with Ranks 1-4 which complete while CS-1 runs.

---

### Rank 6 -- DIMSPARSE3-alpha compound stacking

Anchor name: dimsparse3_alpha_at_mc_v1
Strategic value: Tests Hadamard x sparse-KEY compound at M near M_c on real
encoder. This is the hardest unresolved compound question. Both Hadamard
(38x single-axis on real MiniLM) and sparse-KEY (5-7x) are confirmed;
the compound is unknown. If they add super-linearly near M_c, this becomes
the dominant engineering path for Phase 4 production recipes.
Wall + tier: ~30 min CPU.
HP: compound gain >= 1.5 * max(Hadamard_gain, sparse_KEY_gain) at M near M_c
MID: compound gain >= 1.0 * max(single-axis gains) (additive, not super-
additive, but not destructive)
HF: compound gain < 0.8 * max(single-axis gains) (destructive interference
near M_c; operating point must move away from critical boundary)
Why-now: If super-additive, immediately becomes the Phase 4 v3 default recipe.
~30 min; moderate risk given G7 Hadamard+whitening closed (different mechanism
but warns that compounds can fail).

---

### Rank 7 -- NEG1 DeBERTa NLI drop-in

Anchor name: neg1_deberta_nli_v1
Strategic value: Resolves the KF-1 negation locked gate. "Ships with
adversarial-trained Pythia or NLI-aware MiniLM" -- NEG1 tests whether a
standard DeBERTa NLI classifier (no training, drop-in) gives AUC >= 0.90
on the negation-hard test set. CPU-eligible; no fine-tuning.
Wall + tier: CPU, ~30-60 min (model load + inference over test set).
HP: NLI-based negation AUC >= 0.90 on hard negation test set; drop-in usable
MID: AUC in [0.75, 0.90); useful but needs additional signal (pair with HOC1)
HF: AUC < 0.60 (DeBERTa drop-in fails; adversarial fine-tuning becomes
required; gates NEG1 on model training, not just inference)
Why-now: Rank 7 (after HOC1 because HOC1 may close the gate cheaply). If
HOC1 MID-band, NEG1 complements it. Run in parallel.

---

### Rank 8 -- fact_checked_khop (per-hop hallucination during K-hop reasoning)

Anchor name: fact_checked_khop_v1
Strategic value: Composition: K-hop reasoning x KF-1 hallucination detection.
K-hop K=10 confirmed 100% accuracy, KF-1 AUC 0.975 confirmed separately.
Do they compose? Can the substrate detect per-hop hallucination during a
10-hop chain? Critical for the Phase 4 v3 KILLER demo.
Wall + tier: 10-20 min CPU.
HP: per-hop hallucination AUC >= 0.85 across all 10 hops; localization
accuracy (which hop introduced the error) >= 0.70
MID: AUC in [0.70, 0.85) OR localization in [0.50, 0.70)
HF: AUC < 0.60 (detection collapses in chained setting; KF-1 single-query
mechanism does not transfer to multi-hop; separate per-hop verifier required)
Why-now: Composition validation. If HARD-PASS, auditable_khop_kf1 (Rank 9)
becomes a straightforward integration cell.

---

### Rank 9 -- auditable_khop_kf1 (Phase 4 v3 KILLER demo)

Anchor name: auditable_khop_kf1_v1
Strategic value: The flagship integration demo. Combines K-hop reasoning
(confirmed K=10 100%) + per-hop hallucination detection (KF-1 AUC 0.975) +
full audit trace. This is the "look inside every reasoning step and flag
hallucinations" demo that no transformer KV-cache can replicate. Depends on
fact_checked_khop (Rank 8) passing first.
Wall + tier: 20-40 min CPU.
HP: end-to-end K=10 chain reasoning with per-hop audit, AUC >= 0.85 on
planted-error detection; audit trace recovers which hop and which key erred
MID: chain reasoning intact (K=10 acc >= 0.95) but audit AUC in [0.70, 0.85)
HF: chain reasoning degrades (K=10 acc < 0.90) when audit trace is enabled
(audit overhead corrupts reasoning; pipeline must be restructured)
Why-now: KILLER DEMO directly. Depends on Rank 8.

---

### Rank 10 -- SIG-1 polyphony SNR formula

Anchor name: sig1_polyphony_snr_v1
Strategic value: Product spec formula: SNR(k_concurrent) as a function of
k simultaneous queries on a shared W. Required for multi-tenant capacity
planning (compliance-sidecar architecture: how many concurrent tenants before
crosstalk degrades audit fidelity?). Generates the product data sheet.
Wall + tier: ~1h CPU (algebraic sweep over k and N).
HP: SNR degrades predictably (within 10% of DT-phase prediction) across
k = 1, 2, 4, 8, 16 concurrent queries; product-spec formula validated
MID: SNR prediction within 20% but with systematic bias (needs constant offset)
HF: SNR collapse is non-monotone or non-algebraic (DT framework breaks for
concurrent-query case; multi-tenant operating point requires empirical search)
Why-now: Product-spec cell; low drama but fills the spec gap. ~1h CPU is
acceptable given the output (a validated formula, not just a datapoint).

---

### Rank 11 -- NRO-1 hippocampus chain-binding (K-hop extension)

Anchor name: nro1_khop_chain_binding_v1
Strategic value: Extends K-hop ceiling from K=10 to K=15 using neurologically-
inspired chain-binding primitives (hippocampus-analog: each hop re-encodes
context before binding next hop). If K=15 at >= 95% accuracy, this lifts the
reasoning depth capability significantly.
Wall + tier: ~2h CPU.
HP: K-hop accuracy >= 0.95 at K=15 using chain-binding mechanism
MID: accuracy in [0.85, 0.95) at K=15 OR K=12 at >= 0.95
HF: accuracy < 0.80 at K=15 (chain binding does not extend ceiling above K=10;
K=10 remains the empirical depth limit)
Why-now: Rank 11 (expensive; de-prioritize if queue is full; run overnight).

---

### Rank 12 -- PSE3 codebook collapse monitoring

Anchor name: pse3_codebook_monitor_v1
Strategic value: HARD production gate. Cannot deploy v1 without confirming
that the ETF Hadamard codebook collapse alarm fires correctly under 10k
insertions AND that it does NOT false-positive during normal operation. This
is pure monitoring-infrastructure validation (physics is confirmed; this is
operational engineering).
Wall + tier: ~1-2h CPU (need to run 10k insertion loop + injected collapse).
HP: alarm fires within 100 insertions of a genuine collapse event AND does
not false-positive in 10k normal-insertion control run; H_C threshold holds
MID: alarm fires but with latency > 500 insertions (usable but slow)
HF: alarm false-positives in normal operation OR fails to fire on injected
collapse (production gate BLOCKED; monitoring redesign required)
Why-now: Rank 12 not because it is low value (it is HIGH value) but because
it can be parallelized with everything else and is more infrastructure than
capability research. Run while others are completing.

---

## Cheapest Decisive Top-3 (run FIRST regardless of queue state)

1. HOC1 (hoc1_word_bigram_v1): <2 min CPU. Closes or routes a production gate.
   Result arrives before any other cell; immediately adjusts NEG1 priority.

2. EFFECTIVE-RANK SVD (effective_rank_svd_v1): 5-10 min CPU. Validates the
   entire theoretical framework underpinning CS-1, DIMSPARSE3, and DT-phase
   cells. Zero dependencies; pure algebraic measurement.

3. analogy_map (analogy_map_v1): 3 min CPU. Either opens a new capability
   class (analogy reasoning native) or closes it. 3 minutes, high information
   gain per unit time.

Total for top-3: <15 min CPU, can run in one batch.

---

## Highest Strategic Leverage Top-3 (resolve most uncertainty per unit cost)

1. DIMSPARSE3-alpha (dimsparse3_alpha_at_mc_v1): ~30 min CPU. Resolves the
   most important unknown in the Phase 4 v3 production recipe. Hadamard (38x)
   + sparse-KEY (5-7x) are both confirmed; their compound is the last
   unresolved piece. If super-additive at M_c, it dominates the engineering
   roadmap for months.

2. CS-1 Donoho-Tanner audit (cs1_dt_algebraic_audit_v1): ~1h CPU. Framework-
   level validation. If passes, all activation-regime rescue decisions become
   algebraically principled rather than empirical. Raises the prediction power
   of every future compound-axis design.

3. auditable_khop_kf1 (auditable_khop_kf1_v1): 20-40 min CPU. The flagship
   KILLER DEMO. Resolves whether the two strongest confirmed capabilities
   (K-hop reasoning + hallucination detection) compose into the Phase 4 v3
   centerpiece narrative. Depends on fact_checked_khop (Rank 8) first; if
   Rank 8 runs immediately, Rank 9 can follow within an hour.

---

## Dependency Graph

HOC1 (Rank 1) -> if MID-band -> NEG1 (Rank 7) rises to Rank 3
HOC1 (Rank 1) -> if HARD-PASS -> NEG1 (Rank 7) drops to optional
EFFECTIVE-RANK (Rank 2) -> if HARD-PASS -> CS-1 (Rank 5) gains confidence
EFFECTIVE-RANK (Rank 2) -> if HARD-FAIL -> DT-framework cells need reassessment
analogy_map (Rank 3) -> if HARD-PASS -> new capability class confirmed; open
  follow-up: analogy_map_compositional_stress_v1 (not yet in batch)
fact_checked_khop (Rank 8) -> if HARD-PASS -> auditable_khop_kf1 (Rank 9) queues
fact_checked_khop (Rank 8) -> if HARD-FAIL -> Rank 9 is blocked; debug first
DIMSPARSE3 (Rank 6) -> if super-additive -> Phase 4 v3 default recipe locked;
  CS-1 (Rank 5) runs to validate the DT prediction retroactively
DIMSPARSE3 (Rank 6) -> if destructive at M_c -> move operating point, re-run
  at M = 0.7*M_c; separate follow-up cell needed

Sequence recommendation for empty queues:
  Batch A (immediate, parallel): Ranks 1, 2, 3, 4 (total <20 min CPU)
  Batch B (after Batch A completes or in parallel on GPU): Ranks 5, 6, 7, 8
  Batch C (after Batch B result, sequential): Ranks 9, 10, 11, 12

---

## Capability Matrix Gaps NOT addressed by these 12 cells

(a) Real-encoder dim-expansion true gain (Slot 14 / G1 / G8): broken metric
    was identified but no clean re-run is in this batch. G16 may partially
    close this; needs a dedicated clean-metric cell.

(b) K-hop ceiling above K=15: NRO-1 addresses K=15 but K=20+ is untested.
    After NRO-1, a K=20 probe should be the natural follow-up.

(c) Slot 10 full N=65536 sweep (~60 min CPU; Phase 3 gate; synthetic): not
    in this batch. This confirms the synthetic (ETF Hadamard) operating
    envelope at production N. Should be in the next batch after Batch C.

(d) MULTIHEAD-4 (~20 min CPU; Drill W Rank 4): multi-head binding with 4
    independent retrieval heads. Not in this batch because it depends on
    EFFECTIVE-RANK confirming the dimensionality budget per head.

(e) Cross-encoder generalization: capability transfer confirmed 1.000 across
    3 ops x 2 encoders (MiniLM, DeBERTa), but a 3rd encoder (BGE-large or
    E5-large) is not yet tested. Production requires >= 3 encoder families.

(f) Causal LM integration: all confirmed anchors use MiniLM (encoder-only).
    The KF-1 hallucination test on causal LM output (GPT2 or Llama-3.1-8B)
    is not yet an anchor. CLOUD-1b began this but at model-comparison level,
    not substrate-integration level.

(g) Production latency profiling at N=65536 k=100 concurrent queries: no
    wall-clock profiling under concurrent load. Required for compliance-sidecar
    architecture claim that substrate is NOT on the hot path.

---

## Cheap decisive test summary

Run Ranks 1-4 in one CPU batch (<20 min total). The result of Rank 1 (HOC1)
directly prices NEG1. The result of Rank 2 (EFFECTIVE-RANK) directly prices
CS-1. Ranks 3 and 4 are independent. Total information gain from this 20-min
batch: closes or routes 3 production gates, validates or refutes 1 framework,
discovers or closes 1 new capability class, confirms 1 product feature spec.

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL thresholds)

HARD-PASS (would be surprising positives):
- HOC1 AUC >= 0.90 (word bigrams alone close the negation gap; no NLI needed)
- DIMSPARSE3 compound >= 2.0x single-axis peak (super-additive near M_c)
- analogy_map accuracy >= 0.80 (relational reasoning without LLM call)
- NRO-1 K=15 accuracy >= 0.98 (chain binding extends ceiling by 50%)

HARD-FAIL (would require strategic reassessment):
- HOC1 AUC < 0.55 AND NEG1 AUC < 0.60 (negation gate requires model training,
  not just inference; KF-1 production path changes significantly)
- EFFECTIVE-RANK d_eff > 300 (DT framework loses applicability; CS-1 and
  DIMSPARSE3 theoretical scaffolding weakened)
- DIMSPARSE3 compound < 0.8x single-axis (destructive at M_c; Phase 4 v3
  recipe needs a different operating point or different compound strategy)
- fact_checked_khop AUC < 0.60 (K-hop x KF-1 composition fails; KILLER DEMO
  requires separate per-hop verifier; Phase 4 v3 demo must be redesigned)

P_deflated estimates (calibration penalty applied; lit-scan -0.15 to -0.25):
- HOC1 HARD-PASS (AUC >= 0.90): P = 0.40 (word bigrams are weak on negation
  in NLP literature; partial signal expected, not closure)
- DIMSPARSE3 super-additive: P = 0.30 (compound stacking historically fails
  at M_c; G7 closure is a warning)
- analogy_map >= 0.80: P = 0.45 (bundle arithmetic is theoretically sound
  for bipolar codes; real-encoder noise is the uncertainty)
- NRO-1 K=15 >= 0.95: P = 0.40 (chain binding extends depth but ceiling
  physics is unknown above K=10)
- auditable_khop_kf1 HARD-PASS: P = 0.50 (capped by novel-synthesis rule;
  both components confirmed separately; composition is the open question)

---

## Cross-thread synthesis

Drill W (intrinsic-dim / EFFECTIVE-RANK): all 5 cells that depend on DT-phase
framework (CS-1, DIMSPARSE3, SIG-1, NRO-1, MULTIHEAD-4) are downstream of
the EFFECTIVE-RANK result. Run EFFECTIVE-RANK first.

Drill X (cheap capability classes): analogy_map, frame_slot_fill, fact_checked_
khop, auditable_khop_kf1 form a natural capability-expansion sequence. The
first two are <5 min and independent; the last two form a dependency pair.

Drill Z (cross-domain): SIG-1 and NRO-1 are the cross-domain cells (signal
polyphony from physics, hippocampus chain-binding from neuroscience). Both
have ~1-2h walls; batch them overnight.

Production gates: HOC1 -> NEG1 -> PSE3 form the sequential production-gate
chain. HOC1 is the price-setter; run it first to decide how much engineering
investment NEG1 and PSE3 require.

---

## Substrate-product implications

The 12 cells form a 3-week critical path to Phase 4 v3 demo readiness:

Week 1 (Batches A + B): resolve all capability-matrix composition questions
(analogy, frame-slot, per-hop hallucination) + validate DT framework + close
production gates HOC1 and NEG1.

Week 2 (Batch C): ship auditable_khop_kf1 (KILLER DEMO), validate SIG-1
product spec formula, extend K-hop ceiling to K=15 with NRO-1.

Week 3: clean up PSE3 monitoring, run Slot 10 N=65536, address encoder-
generalization gap, start causal-LM integration cells.

If DIMSPARSE3 super-additive: Phase 4 v3 production recipe is locked by
end of Week 1 and Phase 5 (cloud-scale validation) can be scoped immediately.

---

## Citations (verified count)

This note is a synthesis drill (no external lit-scan required per task spec).
Empirical anchors cited: 29 confirmed flagship anchors (as given in task
input). Framework references: Donoho-Tanner phase boundary (Donoho 2009,
IEEE Trans IT), intrinsic-dim limited retrieval (Drill W synthesis), sparse-KEY
alpha coding (confirmed anchors Slot 3), ETF Hadamard (Slot 2, Slot 9).
Prior drills cross-referenced: Drill W (EFFECTIVE-RANK), Drill X (analogy_map,
frame_slot_fill, fact_checked_khop, auditable_khop_kf1), Drill Z (CS-1, SIG-1,
NRO-1), Drill C (PSE3 codebook collapse monitoring).

Verified citations from existing confirmed anchors: 29.
External lit-scan citations: 0 (synthesis-only drill by task spec).
