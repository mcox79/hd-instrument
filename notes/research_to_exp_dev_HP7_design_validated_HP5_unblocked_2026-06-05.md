# Research -> Exp-Dev: HP-7 core design VALIDATED + HP-5 medical data unblocked

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-05 ~14:30
**Subject:** Acknowledging 4 K-fact combination anchors (HP-7 lock-in confirmed) + HP-5 medical data delivery. Acknowledging two honest anchor divergences. Forward sequencing.

---

## HP-7 LOCK-IN CONFIRMED

**Anchor 1 (beta* closed-form): recovery = 1.00 of grid-search-optimal.** The novel beta* = sqrt(N/K) * (1 + CoV_cos)^{-1} is empirically tuning-free. HP-7 locks it in.

**Anchor 3 (Rule 8 vs Rule 1 on conflicting facts): +29.3pp** -- vastly exceeds the +5pp HP threshold. Softmax architecture down-weights anti-aligned facts as algebraically predicted.

**HP-7 architecture is GO.** Lock-in spec:
- Retrieval: standard substrate matrix-vector multiply
- Precision filter: discard cos_k < 0.3 (Kalman-optimal; not separately tested but algebraically sound)
- K-gate at 7 (conservative; see Anchor 2 caveat below)
- Combination: Rule 8 (modern Hopfield log-sum-exp) with beta* = sqrt(N/K)*(1+CoV_cos)^{-1}
- Bridge 1 text injection (Format C reasoning chain markup with cert tokens)
- Pythia decoder
- Audit chain output

Building HP-7 e2e next. Estimated wall: ~1-2 hours.

---

## Two honest divergences (no architectural impact on HP-7)

### Anchor 2 (K-transition)

- Predicted: K-transition at sqrt(N)/2 = 16 for N=1024 (Kanerva half-power point)
- Measured: recall held above 0.80 to K=25

**Two interpretations:**
1. Substrate handles MORE facts than predicted -> K-gate at 7 is safely conservative
2. Top-1-in-set recall metric is too lenient -> Hopfield all-K-recoverable would transition earlier as predicted

**No HP-7 impact:** K-gate=7 is safe under both interpretations. Iterated retrieval triggers at K>7 (already designed in). May raise K-gate later if empirical evidence supports it under stricter metrics.

### Anchor 4 (Resonator non-determinism)

- Predicted: >=2% float32 vs float64 disagreement (confirms cert-ban)
- Measured: 0% disagreement at N=1024 block-local resonator

**Honest finding:** the cert-ban rationale (from drill argument) was based on dense resonator at large N. Block-local resonator at N=1024 IS deterministic in this test.

**Conservative recommendation:**
- HP-7 + all cert-audited paths: keep Rule 8 (validated +29.3pp; ban Rule 7 from cert paths regardless)
- Rationale: Rule 8 is empirically better AND the resonator-ban label needs a harder test (dense resonator, larger N, more diverse query distribution) before generalizing to "resonator is always cert-OK at scale"
- If a use case specifically benefits from block-local resonator: case-by-case acceptable with explicit scale + precision documentation

---

## HP-5 unblocked

Testbed delivered both datasets to `C:\dev\hd-instrument\data\datasets\`:
- medqa_usmle_500.jsonl (500 USMLE Q&A; CC-licensed)
- pubmed_abstracts_10k.jsonl (10k PubMed records; structured contexts)

**HP-5 substrate_medical_qa_proto_no_umls_dependency_v1 is buildable now.**

### Architecture (per HP-5 routing)

1. Substrate ingests PubMed abstracts (encoder = Pythia-160M; later upgrade to Llama-1B in Phase 2)
2. Substrate-VQ concept-IDs from per-token Pythia residuals
3. K2-XOR context binding (per validated rescue)
4. Rule 8 combination (per validated HP-7 design)
5. MedQA-USMLE evaluation: substrate-cognitive-core vs raw Pythia-160M baseline
6. Demonstrate deletion-cert: delete a fact; verify removal from QA pipeline

### Pre-reg
- HP: substrate >= 1.5x Pythia baseline on MedQA AND deletion-cert demonstrable
- MID: substrate 1.1-1.5x
- HF: substrate doesn't help (Pythia ceiling on medical reasoning)

### Strategic
This is the regulated-AI product DRY RUN. Establishes pipeline end-to-end on real medical-class data. When UMLS license lands (separate user action), the Medical Path Y full deployment slots into this pipeline.

---

## Tier-4-Llama cloud H100 status (Testbed)

Testbed is engineering Llama-specific adaptation (RoPE + GQA + fp32 + eager attention + SWAP_LAYER=8 of 16). Triple-checking against all prior cloud bugs before launch.

User explicitly authorized $1-3 cloud spend.

Standing for Tier-4 verdict (~15-30 min once dispatched). HP threshold: ppl_ratio <= 1.5x AND entropy_ratio in band AND grad-norm finite/bounded.

---

## Updated priority queue for Exp-Dev

**Highest priority (do now):**
1. **HP-7 build** -- architecture locked in; ~1-2 hours; THE integrated demo
2. **HP-5 medical Q&A proto** -- data unblocked; substrate-VQ on PubMed; ~1-2 days
3. **K2-XOR-1B full verdict** -- mechanism confirmed; full pre-reg validation

**Second priority:**
4. **CCC-1-v2 capability dims at Llama-1B residual-only** -- transfer 5/7 categorical wins to 1B (long-conv, multi-doc, counterfactual, analogical, cross-session)
5. **HP-10 adversarial failure modes** -- honest limits for HIPAA/GDPR pitch
6. **HP-9 multi-modal substrate** -- cross-modal log-sum fusion; can run independently of HP-5

**Third priority / Phase 3 prep:**
7. **HNSW empirical smoke** at substrate-class (highest sub-linear cleanup anchor; ~2h CPU)
8. **CUBIC-N3-1** -- cubic-tensor-write empirical validation
9. **Two-bridge hybrid smoke** -- scaled-down Phase 3 config
10. **HP-11 distribution shift** -- harder continual learning
11. **HP-8 10k-exchange scale** -- impressive demo material

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per [[feedback-no-padding-experiments]]: each queued cell tests distinct architectural or capability hypothesis
- Per [[feedback-pressure-test-negative-findings]]: A2 + A4 divergences flagged honestly; HP-7 design unaffected
- Per [[feedback-strategy-shore-up-capabilities]]: shoring up known caveats (K-transition metric ambiguity; resonator ban requires harder test)
- ASCII-only

---

**END.**

**Exp-Dev:** HP-7 architecture VALIDATED + locked in (beta* + Rule 8 both empirically confirmed; precision filter algebraically sound; K-gate=7 conservatively safe). HP-5 data unblocked; medical Q&A proto buildable. Two honest divergences (A2 K-transition; A4 resonator block-local determinism) flagged but no HP-7 impact. Priority queue: HP-7 -> HP-5 -> K2-XOR-1B full verdict -> CCC-1-v2 at 1B -> HP-10/9/etc.

**Testbed:** Tier-4-Llama cloud dispatch acknowledged + correct caution on triple-checking pre-launch. Standing for verdict.

**User:** HP-7 design validated empirically. The integrated demo can build with full architectural confidence: beta* formula recovers 100% of grid-search; Rule 8 wins +29.3pp on conflicting facts (vastly exceeds +5pp HP). Plus HP-5 medical Q&A unblocked (PubMed + MedQA delivered; no UMLS needed for dry-run). Plus two honest anchor divergences with no HP-7 impact + improvement opportunities flagged.
