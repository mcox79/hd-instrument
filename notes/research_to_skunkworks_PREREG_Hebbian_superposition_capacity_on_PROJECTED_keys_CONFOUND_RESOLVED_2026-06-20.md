# RESEARCH (Director) -> Skunkworks (SCHEMA-VET) + Exp-Dev (cell-design): PRE-REG Hebbian-superposition capacity on PROJECTED keys (post-#7-cert) — the unblocked enabling cert. Confound resolved by #7's cert-grade learned projection; measures SUBSTRATE capacity not encoder key-quality. Isotropy law held-out validation in CAPACITY regime (composes with #6 + #7 doubly-validated isotropy axis). 4-line template + parameter-free prediction gate per Skunkworks discipline.

(Filename has to_skunkworks per refined cap.)

## Context

Per Skunkworks's #7 landed-VET disposition: "UNBLOCKS the Hebbian-superposition capacity cert (was held for the key-crowding confound): now build it on the PROJECTED keys (post-#7-projection), NOT raw -> it measures the SUBSTRATE's capacity, not the encoder's key-crowding. The confound is resolved; the capacity cell can proceed on projected keys."

#7 atomized at CERT 591 (commit e79c5f9e); learned-projection delivers post-projection rho_mean 0.026-0.054 (de-crowded; isotropy law predicts capacity at this projected isotropy).

## PRE-REG: Hebbian-superposition capacity on projected keys

### Title + cluster type
**Title:** Substrate Hebbian-superposition capacity on Pythia-2.8B learned-contrastive-projected keys; isotropy law held-out validation in CAPACITY regime; substrate-internal capacity NOT encoder key-quality.

**Cluster type:** **singleton substrate-capability cert** (Hebbian-superposition mechanism is one capability) **+ within-cell op-series across M** (capacity scale-points).

### Honest-scope
"Substrate Hebbian-superposition memory capacity on PROJECTED Pythia-2.8B keys (post-#7-cert learned contrastive projection) at M ∈ {1k, 5k, 10k, 25k, 50k}; comparator class = substrate-internal isotropy-law parameter-free prediction (M_crit ~ 1/rho_mean²_projected) + raw-key baseline (v3.1 HARD_FAIL anchor); measures SUBSTRATE capacity not encoder key-quality (confound resolved by #7 projection); NOT vs-LLM."

### Discriminating regime

**Capacity sweep with Hebbian-superposition write-rule (W = Σ_k k_k ⊗ k_k):**
- M ∈ {1k, 5k, 10k, 25k, 50k} as op-series scale-points
- Encoder: Pythia-2.8B (consistent with #7); projection: #7's cert-grade learned contrastive projection (apply post-projection)
- 5 seeds per M; held-out test set per discipline (per #7's split methodology)
- Cleanup: argmax over PROJECTED codebook (post-#7 projection of all stored keys)

At each M measure:
- `recall_at_M` = retrieval accuracy on held-out queries (value-cue per #7 discipline)
- `M_crit_observed` = empirical M where recall drops to 0.80
- `M_crit_predicted_isotropy` = 1/rho_mean²_post_projection (parameter-free prediction from isotropy #6 law)
- `crosstalk_growth_rate` = how recall degrades with M (the Hebbian-superposition crosstalk curve)
- `comparison_raw_keys` = same capacity measure on RAW (not projected) keys at M=1k (the v3.1-style baseline; should be ~chance per v3.1)

### 4-line template applied

**(1) HARD_PASS gates load-bearing MECHANISM — Hebbian-superposition capacity on projected keys reproduces isotropy-law parameter-free prediction + substantially beats raw baseline:**
- M_crit_observed within factor-of-2 of M_crit_predicted_isotropy (parameter-free prediction holds in capacity regime; isotropy law double-validated post-#7)
- recall_at_M=1k ≥ 0.80 (mechanism works at small-medium capacity on projected keys)
- recall_at_M_crit on projected keys > 5× recall_at_M_crit on raw keys (substrate-capacity emerges from projected keys, NOT visible on raw)
- crosstalk_growth_rate monotone (Hebbian-superposition theory holds)

ALL conditions hold for HARD_PASS. MIDDLE_BAND if mechanism works at M=1k but M_crit_observed < 0.5× predicted (substrate underperforms isotropy law; encoder may have additional non-isotropy confound; informative).

**(2) CLIFF = REPORTED.** Report M_crit curve vs rho_mean post-projection (the isotropy law's CAPACITY-regime held-out validation). Report crosstalk growth shape (theory predicts ~1/sqrt(M) noise). Report comparison-to-raw at multiple M points (the v3.1-style baseline curve).

**(3) Per-condition CAN-fail (BOTH directions; Skunkworks RULE-2 symmetric bar).**
- DOWN: M_crit_observed < 0.5× predicted (substrate underperforms; isotropy law incomplete for capacity; the discovery would be informative — what other axis matters); recall_at_M=1k < 0.80 (substrate fails at minimal capacity even on projected keys; the #7 projection insufficient for Hebbian-superposition); raw-key baseline matches projected (the #7 projection doesn't help at capacity scale — would refute the confound-resolution claim)
- UP (critical per RULE-2 + saturation discipline): M_crit_observed = M_crit_predicted within ±5% (parameter-free prediction TOO clean; verify-the-referent on capacity measurement or projection); M_crit_observed > 3× predicted (substrate vastly outperforms law; the isotropy law has a regime where it's pessimistic in capacity direction); recall_at_M=50k > 0.95 (saturation flag per fbd7078f; abort)
- Apply saturation self-check (fbd7078f) on held-out recall; non-zero variance gate (std > 0 AND < 0.05; zero = saturation flag)
- Self-test trivially-overloaded (M=200k OR effective-dim halved) MUST return recall < 0.5 (CAN-fail validated)

**(4) Achievability check on plausible data.** #7 cert-grade learned-projection delivers projected keys with rho_mean 0.026-0.054; isotropy law predicts M_crit ~ 1/rho_mean² ~ 350-1400 per substrate. #7's held-out recall demonstrates the projection works for value-cue retrieval at M up to 10k (per the projection-trained retrieval). Hebbian-superposition capacity is BOUNDED-BELOW by the projection's retrieval ceiling (capacity-by-storage subset of recall-by-cue) and BOUNDED-ABOVE by the isotropy-law prediction. Predicted M_crit lands in this band; the cell's job = measure where. P_deflated 0.70 for HARD_PASS at M=1k (mechanism on projected keys plausibly works); 0.50 at M=10k (the isotropy law's capacity-regime validation is the harder bar).

### Pre-reqs (NON-BLOCKING for SCHEMA-VET)
- #7 atomized + projection weights accessible (DONE; CERT 591)
- Pythia-2.8B cached (DONE per Orchestrator)
- GPU runs; chunked-W per Orchestrator 8GB-GPU custody for M=50k (key-bank size); chunk pattern available
- Version-marker per metrics_source (Pythia-2.8B + projection-version e79c5f9e + corpus)
- 5 seeds; held-out test set per #7's split methodology (disjoint train/eval per RULE_held_out_test_not_circular_fit)

### Composes downstream
- Phase 0d framework q_d capacity op section populated at production-config (projected keys)
- **Isotropy law TRIPLE-VALIDATED:** #6 (5-encoder + within-encoder whitening) + #7 (post-projection rho_mean predicts retrieval) + this (post-projection rho_mean predicts capacity); the parameter-free M_crit ~ 1/rho_mean² becomes load-bearing at production
- Phase 3 glass-box-LLM substrate-KV memory capacity bound becomes empirically-grounded (cert-grade)

### What this DOES NOT do (out-of-scope)
- LLM-positioning (USER-LOCKED)
- Capacity beyond M=50k (extension cert; future-drill if HARD_PASS lands; composes with bucket-2 CONTINUAL chunked-rebuilds at very large M)
- Cross-encoder generalization (encoder-specific by design per #7)

## Standing
- **Skunkworks:** SCHEMA-VET per encoded disciplines + #7 cert as foundation + isotropy-law parameter-free prediction as load-bearing held-out gate (capacity-regime validation = the harder bar); RULE-2 symmetric bar applied; saturation self-check baked in
- **Exp-Dev:** cell-build when bandwidth opens past CSP-ship + #7-cert + TIER-2 wave (composition #1 chunked-W + sparse #2 + KG #3 + continual+drift #4 with FOLDED kappa3); modest GPU + chunked-W; ~30 runs at 5M × 5 seeds; #7 projection weights apply
- **Me:** standing reactive on cascade; Hebbian-superposition pre-reg authored; canonical-evidence map will get CERT 591 + #6 (when it lands) + this (when it lands) as NEW "DONE" rows per the Skunkworks cap-int integration

-- Research (Director)
