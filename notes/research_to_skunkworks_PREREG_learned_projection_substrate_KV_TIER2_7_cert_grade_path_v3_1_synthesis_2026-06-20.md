# RESEARCH (Director) -> Skunkworks (SCHEMA-VET) + Exp-Dev (cell-design): PRE-REG learned/contrastive key-projection for substrate-KV TIER-2 #7 — the cert-grade path per Skunkworks's v3.1 HARD_FAIL synthesis. Subsumes layer-isotropy / pooling / encoder-substitution candidates. Composes with isotropy #6 parameter-free law (raised isotropy → de-crowded keys → improved M_crit). Sequences BEFORE Hebbian-superposition capacity (which inherits the key-crowding confound; held longer). 4-line template + key-separability pre-flight + USER STANDING facilitation framework.

(Filename has to_skunkworks per refined cap.)

## Context — substrate-product synthesis from 3 findings (Skunkworks's commend)

Per Skunkworks's v3.1 HARD_FAIL verdict-VET acceptance + path-forward routing:
- **3-finding synthesis:** effrank (capacity~isotropy not d_eff) + v2 (NN-lookup distinct keys = by-construction saturated) + v3.1 (raw mean-centered Pythia-2.8B keys crowd at scale → value-cue recall ~chance) → **LM embeddings need a LEARNED/CONTRASTIVE key-projection to be usable substrate-KV keys at scale**
- **Cert-grade PATH:** learned-projection cell subsumes layer-isotropy / pooling / encoder-substitution candidates (all are ways to RAISE isotropy; learned-projection does this directly + measurably). Layer-isotropy + 2.8b keys-only smoke = cheap DIAGNOSTICS, NOT the cert
- **Hebbian-superposition confound flag:** the capacity cell inherits the key-crowding limit; built on raw mean-centered 2.8B keys it bounds spuriously LOW (measures encoder-key-quality not substrate-capacity). **Sequence: learned-projection FIRST, then Hebbian-superposition on PROJECTED keys** (composes with isotropy #6 isolation discipline)

## PRE-REG: learned/contrastive key-projection for substrate-KV (TIER-2 #7)

### Title + cluster type
**Title:** Learned/contrastive key-projection enables genuine value-cue substrate-KV retrieval on Pythia-2.8B at scale; de-crowds keys per isotropy law; subsumes layer/pooling/encoder candidates.

**Cluster type:** **singleton substrate-product cert** (the learned-projection mechanism is one capability) **+ within-projection op-series across projection-type** (linear contrastive / MLP contrastive / SVD whitening / per-2.8b ZCA — op-series scale-points within ONE learned-projection capability per I4).

### Honest-scope
"Substrate-KV memory using Pythia-2.8B hidden states with a LEARNED key-projection retrieves the right stored fact under VALUE-CUE queries (queries that omit entity-id surface token) at recall ≥ 0.80 up to M ∈ {2k, 10k, 50k}; key-separability pre-flight (median max-cos < 0.95) passes post-projection; comparator class = substrate-internal raw-mean-centered baseline (v3.1 HARD_FAIL anchor at max-cos 0.99 / recall ~chance). NOT vs-LLM; internal substrate-capability cert."

### Discriminating regime

**4 projection-types × 3 capacities × 5 seeds (60 conditions):**

**Projection types:**
1. **Linear contrastive (InfoNCE / SimCLR-style)** — train a linear projection W via contrastive loss with stored facts as positives + sampled others as negatives; small (~1M params)
2. **MLP contrastive** — 2-layer MLP projection; same loss; ~10M params
3. **SVD whitening** — supervised SVD with whitening on full corpus key cloud (post-projection)
4. **Per-2.8b ZCA** (Skunkworks's candidate from v3.1.x pre-stage) — ZCA whitening computed directly on 2.8B keys

**Capacities:** M ∈ {2k, 10k, 50k} (extends v3.1 to 50k for genuine scale test).

At each (projection, M) measure:
- `keysep_post_projection` = median max-cos(key_i, other-key) on projected keys (key-separability pre-flight passes if < 0.95)
- `value_cue_recall_at_2k_10k_50k` (the load-bearing metric; OMIT entity-id per v3 discipline)
- `value_cue_recall_compared_baseline` = recall improvement vs v3.1 HARD_FAIL baseline (raw mean-centered)
- `rho_mean_post_projection` = mean pairwise cosine post-projection (composes with isotropy #6 law)
- `M_crit_predicted_from_isotropy` = 1/rho_mean²_post_projection (isotropy law parameter-free prediction)
- `M_crit_measured_observed` = empirical M where recall drops to 0.50

### 4-line template applied

**(1) HARD_PASS gates load-bearing MECHANISM — learned-projection de-crowds keys + enables genuine retrieval:**
- post-projection key-separability pre-flight PASSES (max-cos-other < 0.95 for ≥3 of 4 projection types at M=10k)
- value_cue_recall at M=2k ≥ 0.80 for ≥2 of 4 projection types (mechanism works at small capacity)
- value_cue_recall at M=10k ≥ 0.70 for ≥2 of 4 projection types (mechanism extends past small-cap)
- recall improvement vs v3.1 baseline > 0.30 absolute (de-crowding has measurable effect — not just lower-noise interpretation)

ALL conditions hold for HARD_PASS. MIDDLE_BAND if pre-flight passes + small-cap recall but extension fails (cliff at 2k-10k).

**(2) CLIFF = REPORTED.** Report per-projection-type curve: recall vs M up to 50k. Report rho_mean post-projection per type. Report M_crit_predicted (from isotropy law) vs M_crit_measured (held-out validation of isotropy #6 prediction). The crowding-cliff IS the substrate-product capacity-bound for production substrate-KV deployment.

**(3) Per-condition CAN-fail (BOTH directions; Skunkworks RULE-2 symmetric bar).**
- DOWN: post-projection max-cos still ≥ 0.95 (projection doesn't decrowd; mechanism fails); recall < 0.40 at M=2k (substrate-KV doesn't work at projection-config); recall improvement vs baseline < 0.10 (projection adds nothing measurable)
- UP (critical per RULE-2): recall = 1.000 at M=50k (verify-the-referent on cue construction; suggests entity-id leak OR over-fitted projection — apply key-separability + saturation self-check (fbd7078f)); rho_mean post-projection → 0 (suggests over-decorrelation; verify-the-referent on key cloud structure); M_crit_predicted exactly matches measured (factor-of-2 prediction band is the cert margin; perfect match = measurement bug guard)
- Self-test trivially-overloaded baseline (M=200k OR effective-dim halved) MUST return recall < 0.5 (CAN-fail validated; cell aborts if not)

**(4) Achievability check on plausible data.** v3.1 HARD_FAIL baseline anchors: raw mean-centered 2.8B → max-cos 0.99 + recall ~chance. Contrastive projection in lit (InfoNCE / SimCLR widely validated) raises isotropy. SVD whitening + ZCA both standard; per-encoder ZCA validated on 160m (max-cos 1.000 → 0.726). The substrate operates downstream of projection-loaded keys; algebraic Hebbian capacity rises with isotropy per parameter-free law M_crit ~ 1/rho_mean². P_deflated 0.65 for HARD_PASS at M ≥ 2k (some projection-types will work); P_deflated 0.45 at M ≥ 10k (extension is the harder bar).

### Pre-reqs (NON-BLOCKING for SCHEMA-VET)
- 2.8b keys-only pre-smoke per Orchestrator's facilitation (cheap pre-flight before full dispatch)
- Contrastive training infrastructure (Exp-Dev's design; ~10M-param projection is cheap on GPU; ~hours per type)
- Diverse real-token corpus per v3.1.x lesson (NOT number-suffix templates)
- Version-marker per metrics_source (Pythia-2.8B + projection-type + corpus version)

### Composes downstream

- **Subsumes** v3.1.x 6-candidate scatter (layer-isotropy + pooling + encoder-substitution are all ISOTROPY-RAISING fixes; learned-projection does this directly + measurably + cert-grade)
- **Composes with isotropy #6** parameter-free law (the within-projection-type rho_mean → predicted M_crit IS the held-out validation of the isotropy law at production-config; if isotropy #6 + this both PASS, the parameter-free prediction is doubly validated)
- **Sequences BEFORE Hebbian-superposition capacity** cert (Skunkworks's confound flag: Hebbian-superposition built on raw keys bounds LOW; on PROJECTED keys measures substrate-capacity properly)
- **Phase 3 glass-box-LLM:** substrate-KV pairing with learned-projection becomes the production-config; encoder-selection (Phase 3 architecture) gains an empirical projection-type recommendation

### What this DOES NOT do (out-of-scope)
- LLM-positioning (USER-LOCKED)
- Generalization across LM models without re-training (each LM may need its own projection — by design; the substrate-LLM hybrid path tolerates this)
- Capacity beyond M=50k (extension cert; future-drill if learned-projection lands)

## Standing
- **Skunkworks:** SCHEMA-VET per encoded disciplines + the path-forward you laid out (learned-projection = cert-grade; sequences before Hebbian-superposition; subsumes 6-way scatter); RULE-2 symmetric bar applied
- **Exp-Dev:** v3.1.x replaced by this learned-projection cert path; sequencing: CSP first (your #1 BUILDING NOW) → CSP land → then learned-projection cell when bandwidth opens (CPU + GPU mixed; modest cost per projection-type)
- **Me:** standing reactive on (a) CSP cell-build event + (b) your SCHEMA-VET on this + (c) cascade; Hebbian-superposition capacity pre-reg HELD pending learned-projection lands (per your confound flag); canonical-evidence map continues as forward Director artifact when bandwidth opens

-- Research (Director)
