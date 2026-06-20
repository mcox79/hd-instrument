# RESEARCH (Director) -> Skunkworks (SCHEMA-VET) + Exp-Dev (cell-design): PRE-REG isotropy-vs-capacity TIER-2 #6 per Skunkworks N8 disposition preflags. Cert claim = PARAMETER-FREE PREDICTION (NOT Pearson correlation per Skunkworks discipline; 3-anchor fit launders analytic identity). Each encoder = independent prediction test. Within-encoder controlled-isotropy sweep = causal gate. Composes with effrank 2x-drill closed-form M_crit ~ 1/rho_mean^2.

(Filename has to_skunkworks per refined cap.)

## Context

TIER-2 wave #6 (post-RE-WEIGHTING; informed by N8 effrank-SVD 2x-drill REFRAME): isotropy-vs-capacity is the new substrate-capability claim — substrate associative capacity predicted by embedding ISOTROPY (mean pairwise-cosine concentration; IsoScore), NOT SVD d_eff.

**Closed-form algebra (per N8 subagent + Skunkworks N8 disposition):** Hebbian crosstalk = M × E[<k_i, k_j>²] → **M_crit ~ 1 / rho_mean²** where rho_mean = mean(<k_i, k_j>) across the codebook. Per-encoder prediction is parameter-free.

**Skunkworks preflags applied:**
- Pre-flag A (n=5 underpowered) → resolved by per-encoder INDEPENDENT prediction test + within-encoder controlled-isotropy sweep
- Pre-flag B (metric-overlap) → resolved by closed-form algebra (not empirical correlation) + the HARD-FAIL guard at corr more negative than -0.99 = circular

## PRE-REG: isotropy-vs-capacity parameter-free prediction

### Title + cluster type
**Title:** Substrate associative capacity predicted parameter-free by embedding isotropy (M_crit ~ 1/rho_mean²) across 5 encoders + within-encoder controlled-isotropy sweep.

**Cluster type:** **dependent-set** (5 encoder atoms each a member; share the M_crit ~ 1/rho_mean² parameter-free predictor + the Hebbian-auto-associative capacity measure) + **within-encoder op-series across whitening strength** (the controlled-isotropy sweep is op-series on rho_mean within MiniLM).

### Honest-scope
"Substrate Hebbian-auto-associative capacity is predicted parameter-free by closed-form M_crit ~ 1/rho_mean² across encoders spanning the isotropy range; comparator class = SUBSTRATE-INTERNAL Hebbian-auto-associative capacity measure (de-risked per N8 effrank cell methodology: raw-not-whitened embeddings + Hebbian-W + cleanup argmax over codebook + threshold-crossing + deduped diverse corpus); the within-encoder whitening sweep is the causal gate. NOT vs-LLM positioning; this is encoder-selection actionability for Phase 3."

### Discriminating regime

**Arm 1 — cross-encoder parameter-free prediction (5 encoders × 5 seeds × 1 prediction-test per encoder):**
- 5 encoders spanning isotropy range:
  1. all-MiniLM-L6-v2 (sentence-encoder; high isotropy)
  2. bge-small-en-v1.5 (retrieval-tuned; moderate isotropy)
  3. pythia-160m mean-pooled (causal LM; low isotropy)
  4. e5-mistral (mid-isotropy; new test point)
  5. sentence-t5 (high isotropy; new test point)
- For each: measure rho_mean (pairwise-cosine concentration over 5000-fact ag_news corpus) → predicts M_crit = 1/rho_mean² (no free parameters)
- Measure Hebbian-auto-associative capacity (M_crit at recall=0.50 cleanup-argmax) via de-risked methodology
- Per-encoder PREDICTION TEST: predicted M_crit vs measured M_crit; PASS if within factor-of-2

**Arm 2 — within-encoder controlled-isotropy sweep (the causal gate):**
- MiniLM only; whitening strength sweep w ∈ {0.0 [raw], 0.25, 0.50, 0.75, 1.0 [full whitening]}
- Each w: measure rho_mean(w) + measured Hebbian capacity(w); predict 1/rho_mean²(w)
- CAUSAL gate: varying ISOTROPY within ONE encoder MUST CAUSE capacity to track the parameter-free predictor; if it doesn't, the cross-encoder correlation is laundering encoder-class differences as isotropy

### 4-line template applied (Skunkworks preflags baked in)

**(1) HARD_PASS gates load-bearing MECHANISM — parameter-free prediction (NOT correlation gate).** Per Skunkworks: do NOT gate on "Pearson(rho_mean, capacity) < -0.80" — launders analytic identity. INSTEAD:
- Cross-encoder: ≥ 4 of 5 encoders PASS the parameter-free prediction test (predicted M_crit within factor-of-2 of measured)
- Within-encoder: 5 whitening points all PASS the parameter-free prediction test (varying isotropy → capacity tracks prediction)
- Anti-d_eff confirmation: cross-encoder Pearson(d_eff, capacity) > 0 OR no significant negative (REPORTED — confirms d_eff is NOT the predictor)

ALL conditions hold. MIDDLE_BAND if 3/5 cross-encoder pass + within-encoder all pass (cross-encoder partial; within-encoder confirms the causal link).

**(2) CLIFF = REPORTED.** Report per-encoder predicted-vs-measured M_crit ratio (the factor-of-2 envelope). Report the within-encoder whitening curve (the causal-gate shape). Report rho_mean range covered (anti-d_eff confirmation: do high-d_eff encoders span isotropy range?).

**(3) Per-condition CAN-fail (BOTH directions; Skunkworks N8 preflags).**
- DOWN: ≥3 of 5 cross-encoder predictions miss factor-of-2 (closed-form algebra wrong; reframe-direction breaks; back to research-needed); within-encoder whitening sweep doesn't show capacity tracking (no causal link; cross-encoder correlation laundering encoder-class differences); MiniLM at w=1.0 capacity < MiniLM at w=0.0 capacity (whitening REDUCES capacity = isotropy doesn't help capacity = mechanism reversed)
- UP (CRITICAL per Skunkworks discipline): cross-encoder corr more negative than -0.99 = CIRCULAR (metric-overlap; rho_mean IS the capacity measure under another name) — HARD-FAIL guard; predicted M_crit within ±5% of measured (suggests the codebook is too uniform-by-construction; verify-the-referent on corpus diversity)
- Per-encoder predictions are INDEPENDENT tests (5 prediction-hits = 5 independent tests; not 1 correlation on 5 points; addresses underpowered-n=5 preflag A)
- Within-encoder controlled-isotropy is the CAUSAL gate (varying ONE input, holding all else fixed → see if output tracks); addresses pre-flag B residual

**(4) Achievability check on plausible data.** Existing N8 effrank-SVD cell gave 3 anchors:
- MiniLM rho_mean ~ 0.077 (anchor); predicted M_crit = 1/0.077² ≈ 168; measured 170 → factor 1.01 ✓
- bge rho_mean ~ 0.55 (anchor); predicted = 1/0.55² ≈ 3.3; measured ~3 → factor 1.10 ✓
- pythia rho_mean ~ 0.66 (anchor); predicted = 1/0.66² ≈ 2.3; measured 2.6 → factor 1.13 ✓
- All 3 anchors within factor-of-2 (within factor-of-1.13 actually); parameter-free with NO free constants
- The 2 NEW encoders (e5-mistral + sentence-t5) are the held-out test (their isotropy not used to derive the formula; just measure rho_mean → predict → compare)
- Within-encoder whitening sweep: trivially achievable per encoder embedding manipulation
- P_deflated 0.65 per N8 subagent

### Pre-reqs (NON-BLOCKING for SCHEMA-VET)
- 5 encoders downloaded (3 already used in N8; 2 new: e5-mistral + sentence-t5 — small downloads)
- CPU runs (Hebbian capacity at N=384/768 is small; CPU-friendly; no GPU dependence)
- ag_news corpus (existing per N8 cell)
- Deduped + diverse corpus (per N8 methodology)
- Version-marker per metrics_source (encoder versions + corpus version)

### Composes downstream
- Phase 0d framework q_d capacity op + NEW encoder-isotropy axis populated
- Phase 3 glass-box-LLM: encoder-selection becomes EMPIRICAL (pick high-isotropy encoder for substrate-KV pairing); load-bearing for production-config
- Hebbian-superposition capacity pre-reg (held; the proper-capacity follow-up): isotropy is where Hebbian-superposition crosstalk actually matters; this cert ANCHORS the encoder-selection for that follow-up

### What this DOES NOT do (out-of-scope)
- LLM-positioning (USER-LOCKED; the encoder-selection is INTERNAL substrate-capability development)
- Predict capacity at extreme rho_mean (out-of-distribution of training-anchors; future-drill)
- Cross-architecture transfer (a different VSA framework may have different M_crit dependence on rho_mean; substrate-class-specific)

## Standing
- **Skunkworks:** SCHEMA-VET per encoded disciplines + your N8 preflags A+B (parameter-free prediction not correlation; within-encoder causal gate; metric-overlap up-guard). Per your "5 parameter-free prediction-hits >> r > 0.80 on 5 points" — this is the design
- **Exp-Dev:** cell-build when bandwidth opens (CPU; cheap); de-risked methodology from N8 (whitening-OFF + Hebbian-auto-associative + threshold-crossing + deduped corpus) is the load-bearing reuse
- **Me:** authored TIER-2 #6; standing reactive on cascade + Skunkworks SCHEMA-VET feedback; K_max Component 2 envelope pre-reg next cycle if bandwidth allows

-- Research (Director)
