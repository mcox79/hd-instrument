# Skunkworks -> Research (cc all): bundled LANDED-VET — Path C armA_projected HARD_FAIL honest_negative + Path B MKN MIDDLE_BAND measured_mechanism (2026-06-22)

## TL;DR

Two cells landed full-mode and got dispositions through one A5 single-writer pair (delta=0 each; CERT-neutral).

| Cell | Path | Verdict | Cert disposition | Atom | Ledger row |
|------|------|---------|------------------|------|------------|
| `exp_armA_projected_key_revival_v1` (39d614a0) | C angle 4 | HARD_FAIL | `honest_negative` / `pre_reg_miss_proven_bound` | `math::T3/EXP_armA_projected_key_revival_v1` | `f2a658ddda005c98` |
| `exp_n3_mkn_smoothing_v1` (ad25a0a3) | B sub-area b | MIDDLE_BAND | `measured_mechanism` / `mechanism_characterization` | `math::T3/EXP_n3_mkn_smoothing_v1` | `82cb6932f672a8e4` |

A5 PRE: CERT 584 / axiom 206 / atoms 177269 / ledger 633.
A5 POST: CERT 584 / axiom 206 / atoms 177271 / ledger 635.
Verified-off-data (independent .venv numpy recompute reproduced every cited number).

## (a) Ratified dispositions

### Path C HARD_FAIL → honest_negative

- HARD_PASS bar (recall_armA_projected >= 0.60 at M=10k under sigma in {0,0.1}): NOT CLEARED. Observed max armA_proj across all (M, sigma, seed) = **0.0400** (at M=1k, the EASIEST cell); M=10k clean max = 0.0080 / worst = 0.0075 (matches verdict_msg 0.008/0.0075 exactly).
- HARD_FAIL bar (recall < 0.20): observed 0.008 << 0.20 → DIRECTION-CORRECT (no over-claim; the discriminator is genuine).
- CAN-FAIL discriminator armed: shuffled-projection control mean = 0.0072, max = 0.0125 (near chance 0.0039 for C=256). Projection is NOT memorizing — it just fails to rescue sparse-superpos.
- Anchor: armA_raw at M=1k sig=0 mean = 0.0088 (4-arm anchor was 0.013; full-vs-smoke tolerance band holds).
- Substrate-only-decode gate: N/A (KV-storage cell, not LM; documented explicitly in metrics as `substrate_only_decode_gate: "N/A (KV-storage cell, not LM cell; per Path C ARM A discriminator framing)"`).
- run_mode='full' confirmed per_unit on all 3 seeds (7, 17, 23).
- Storage-chain conclusion: **tag-retrieval CLASS is the UNIQUE storage path for substrate KV**; sparse-superpos genuinely dead even with CERT591-style contrastive key projection at full training budget (TRAIN_M=2500, TRAIN_STEPS=600, proj_dim=256).

### Path B MKN MIDDLE_BAND → measured_mechanism

- HARD_PASS bar (mkn substrate_bpc <= 4.86): NOT CLEARED (observed 4.906).
- MIDDLE_BAND band (0.03 <= delta < 0.10): CLEARED at delta mean = **0.0685** (matches verdict_msg 0.068 exactly).
- Pre-reg-direction: positive=MKN_improves → DIRECTION-CORRECT (3/3 seeds positive: seed7=0.145, seed17=0.041, seed23=0.019).
- JM anchor reproducibility: jm mean=4.974 vs N2 anchor 4.96 (within 0.05 → ANCHOR-OK).
- mkn_D mean = 0.6116; all 3 seeds in [0.30, 0.70] → no boundary-clip artifact (cell-author's note re-validated; smoke had D=0.869 near 0.99, full has D in safe range).
- Substrate-only-decode gate VERIFIED: zero `model(`, `forward(`, `generate(`, `AutoModel` matches in source via regex; `total_llm_forward_calls_observed=0` per metrics; `zero_llm_calls_at_inference=true` flag.
- Fix #6 zero-D-overlap fallback PRESENT (line 343-346 + selftest T6 PASS line 561-567).
- run_mode='full' confirmed per_seed on all 3 seeds.
- META atomized in atom metadata: `decode_side_bottleneck_finding: real_and_addressable_MKN_partial_lever_closes_0_068_of_1_13_bits_6_1_pct`.

## (b) Cert-ledger row hashes

- Path C row hash: **`f2a658ddda005c98`** (cert_ruling, honest_negative, delta=0, supersedes=null)
- Path B row hash: **`82cb6932f672a8e4`** (cert_ruling, measured_mechanism, delta=0, supersedes=null)
- Ledger 633 → 635.

## (c) MKN delta-vs-bigram-gap math + Path A composition implications

- substrate-bigram gap (jm anchor - bigram_bpc): 4.974 - 3.844 = **1.130 bits remaining**.
- MKN closes 0.0685 / 1.1303 = **6.1% of the substrate-bigram gap**.
- Decode-side bottleneck is REAL + ADDRESSABLE. The class-of-lever (smoothing) is exhausted at MKN (Chen-Goodman is the strongest practical Kneser-Ney variant); MKN-Power / Pitman-Yor would add ~0.01-0.03 bits if at all.
- For Path A V_C=4096: encoder bottleneck likely closes 0.3-0.6 bits if scaling is linear in log(V_C) (currently V_C=1024 → V_C=4096 = 2 doublings). IF additivity holds, V_C=4096 + MKN ≈ jm@V_C=4096 − 0.068 bits.
- HARD_PASS bar (mkn <= 4.86) requires closing 0.114 bits total → V_C=4096 needs to deliver ~0.045 bits on its own beyond MKN's 0.068 (assuming additivity, no encoder-decoder interaction). **Composition is the open question** — they may NOT be additive (the encoder MAY shift the count statistics MKN exploits).
- **CHAIN-GRADE may be one-cell-away IF V_C=4096 alone closes 0.5+ bits (the bigger lever) and MKN composes additively** — but the additivity assumption is unverified; both could be true and chain-grade only emerges from the composition cell.

### Recommended next L4 step (priority)

**DISPATCH Path A V_C=4096 IMMEDIATELY** without MKN composition first (cleanest discriminator):
- Get the standalone V_C=4096 BPC drop estimate.
- IF V_C=4096 alone closes >= 0.10 bits → MKN composition becomes the chain-grade candidate cell.
- IF V_C=4096 alone closes < 0.05 bits → revisit the decode-side strategy (the lever class may be saturated end-to-end at this N_DIM=16384/K=1 regime).
- Brain-drill async: doesn't affect this priority (Path A is decode-side scaling, brain-drill is downstream LM head). Run in parallel.

## (d) Storage chain status

**Path C confirms storage chain item #3 = tag-retrieval CLASS is the UNIQUE storage path.** Sparse-superposition + kWTA + cerebellar K=5 is dead even under CERT591-style learned contrastive projection (the strongest projection method we have). The chain stack:

1. dense_KV_learned_key (CERT 591) — works on PROJECTED dense keys.
2. tag-retrieval CLASS — works.
3. sparse-superpos under raw keys — dead (the 4-arm anisotropy rescue).
4. sparse-superpos under CERT591 projection — DEAD (this cell; Path C ratifies).

Implication: any sparse-fan-in capacity result (Willshaw super-capacity 8x@f0.10 / 20x@f0.02, the sparse-#2 measured_mechanism) is a STORAGE CLASS distinct from the projected-key class. They don't transfer.

## (e) Honest surprises off per_unit

1. **MKN delta cv = 0.98 across seeds** (seed7=0.145 vs seed17=0.041 vs seed23=0.019). The verdict_msg cites `mkn_cv=0.016` which is post-smoothing BPC cv — NOT delta cv. Both are honest disclosures of different quantities; flagged in atom metadata under `delta_heterogeneity_honest_note`. Paired design preserves direction-correct (all 3 positive), but absolute-magnitude is seed-sensitive. **If Path A V_C=4096 + MKN composition cell is dispatched, seed 7 wall-time should NOT be used as a cell-budget basis (it converged faster with bigger delta); use seed 23 (worst case) wall-time + 20% buffer.**

2. **Path C M=1k armA_proj = 0.0400 mean** — the projection DOES recall above chance (4-arm anchor was 0.013) at low M, but the lift dies fast: at M=5k = 0.023, at M=10k = 0.008. Projection rescues SCALE-DEPENDENTLY but the rescue collapses at the deployment regime. The bound is honest: projection lifts ~10x at M=1k but only ~1.4x at M=10k (vs chance). Worth noting because the FAILURE has a discoverable scaling law — useful Research input for any revival drill that targets very-low-M regimes.

3. **Path B mkn_D mean 0.612** falls comfortably mid-range [0.10, 0.99] — exactly per cell-author's prediction. The smoke's D=0.869 near 0.99 boundary WAS the artifact warning; at full V_TOK=50087 + 100k docs the count-of-counts converges to clean discount.

4. **Path C shuffled-proj ctrl seed-variance**: seed 17 hit max=0.0125 (1.6x chance), other seeds at chance. Mild seed-variance in the CAN-FAIL ctrl but doesn't approach the armed-arm signal of 0.04 → discriminator is still armed, just noisier than chance-pure.

## (f) Recommendations for next L4 step

1. **DISPATCH Path A V_C=4096 immediately** (priority 1). Standalone first (NOT composed with MKN) for clean discriminator.
2. **Path B MKN as composable lever** — register it as a stackable post-hoc smoothing. Don't re-dispatch alone.
3. **Path C honest_negative → route to Research for 2x/3x REVIVAL drill** (per USER 2026-06-20 standing). Angles to surface:
   - low-M regime (M ≈ 500-2000) is where projection rescues — could a low-M-tuned variant exploit this?
   - frozen-projection vs trained-projection: did training help OR hurt? (CERT591 used the same proj — test ablation)
   - alternative sparsity-K (K=2/3/8/10) — Litwin-Kumar K=5 is fly-cerebellar-specific; other K may behave differently.
4. **Brain-drill async** — unrelated, don't gate Path A on it. Independent decision.

## (g) Two completion note filenames

This file: `notes/skunkworks_to_research_cc_all_LANDED_VET_path_c_armA_projected_HARD_FAIL_and_path_b_mkn_MIDDLE_BAND_MM_2026-06-22.md`

## Disciplines exercised

- verify-off-DATA (every cited number reproduced from per_unit via .venv numpy recompute)
- pre-reg-direction-must-match-intent (Path B MIDDLE_BAND direction-correct; Path C HARD_FAIL direction-correct)
- substrate-only-decode-gate (Path B regex-grep + total_llm_forward_calls_observed=0; Path C N/A documented)
- by-construction-saturation (Path C shuffled-proj near chance — discriminator armed; Path B mkn_D not at boundary)
- pre-flight run_mode CHECK (both cells verified `run_mode=='full'` per_unit/per_seed)
- A5 PRE/POST gating (CERT count + axiom 206 + cap_pres 6/6 + Store-load round-trip)
- never `git add -A` (path-scoped commits only)
- 5MM-drift symmetric verify (Path B delta cv=0.98 honest surprise flagged in metadata + this note; not buried)
- cited-number-must-reproduce-from-cell (recompute matched: max 0.008, worst 0.0075, delta 0.068, jm 4.974, mkn 4.906, mkn_D 0.612)

CONTEXT DIES ON REPLY.
