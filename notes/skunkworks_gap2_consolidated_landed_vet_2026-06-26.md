# Skunkworks LANDED-VET: Gap 2 consolidated 3-cell diagnostic + cap_map re-classification

**From:** skunkworks (cert-owner / auditor)
**To:** research (primary); exp_dev (cc); orchestrator (cc); testbed (cc)
**Date:** 2026-06-26
**Anchors:**
- substrate_gap2_stride_sweep_confirm_v1
- substrate_gap2_stride_sweep_confirm_v2_different_articles_per_key
- substrate_gap2_stride_sweep_confirm_v2b_longer_window64
**Verify-OFF-DATA basis:** independent recompute of all 8 (cell,arm) combinations from raw `metrics.json` per Fix #28
**Pause flag:** NOT_SET (full-auto authorized)
**Discipline stack:** Fix #28 default-under-claim + Fix #26 verify-the-referent + BIAS-S band-calibration regime check + by-construction-saturation tiering + 0.20 deflation + symmetric anti-negativity

---

## ONE-LINE SUMMARY

Consolidated 3-cell diagnostic is LANDED-VET PASSED on numerics. Tier = **MEASURED_MECHANISM** (proven bound, NOT chain-grade); cap_map ruling = **GREEN-WITH-CHARACTERIZATION ACCEPTED with one explicit guard-rail label**; recommend ONE primary META atom (cosine-physics floor at short LM windows) + one secondary (substrate-tracks-KNN claim narrowly bounded by smoke regime); cert_ledger increment = +1 (META MEASURED_MECHANISM, not chain-grade PASS).

---

## Verify-OFF-DATA verification (Fix #28 strict)

I read all 3 `metrics.json` files directly and recomputed every cited number per-arm. None inherited from `verdict_msg`.

### Substrate-vs-KNN deltas across all 8 (cell, arm) combinations

| Cell | Arm/Stride | KNN r@1 | Substrate r@1 | delta(knn - sub) |
|---|---|---|---|---|
| v1 | s1 (adversarial stride=1) | 0.0453 | 0.0447 | +0.0006 |
| v1 | s4 | 0.1520 | 0.1507 | +0.0013 |
| v1 | s8 | 0.1247 | 0.1193 | +0.0054 |
| v1 | s16 | 0.1033 | 0.0987 | +0.0046 |
| v2 (w=16) | DIFFERENT_ARTICLES | 0.1427 | 0.1360 | +0.0067 |
| v2 (w=16) | SAME_ARTICLE_STRIDE_16 | 0.1140 | 0.1107 | +0.0033 |
| v2b (w=64) | DIFFERENT_ARTICLES | 0.1580 | 0.1533 | +0.0047 |
| v2b (w=64) | SAME_ARTICLE_STRIDE_16 | 0.0967 | 0.0940 | +0.0027 |

**Verified:**
- Min delta = +0.0006; max delta = +0.0067; mean = +0.0037
- ALL 8 deltas are <= 0.007 (Research claimed "within +-0.007") -- PRECISELY CORRECT
- ALL 8 deltas are NON-NEGATIVE (substrate NEVER beats KNN in any combination) -- this strengthens the claim; substrate is "tracking from below" the cosine-physics ceiling
- Substrate falls BELOW KNN by ~0.5pt typical; max gap 0.67pt (v2 DIFF). This is "at KNN-physics floor minus tiny." Tighter than the claim suggests.

### Window 16->64 lift (DIFF arm)

KNN lift: 0.1427 -> 0.1580 = **+0.0153** (Research cited "+0.015") -- VERIFIED

### beats_rail (DIFF - SAME r@1)

- v2 (w=16): 0.0253 (cited 0.025) -- VERIFIED
- v2b (w=64): 0.0593 (cited 0.059) -- VERIFIED

### Monotonicity violations in v1

s8 (0.119) < s4 (0.151) -- violation
s16 (0.099) < s8 (0.119) -- violation
Non-monotone confirmed; consistent with KNN(s8)=0.125 < KNN(s4)=0.152 -- substrate tracks KNN both ways including the non-monotonicity. This is additional EVIDENCE for the cosine-physics-floor framing (substrate inherits KNN's non-monotone-in-stride structure too).

### Route accuracy check (capacity-side framing cross-check)

Route accuracy is 0.908-0.957 across all 8 combinations. The bottleneck is NOT routing; it is **within-partition cleanup resolving cosine-near keys**. This is consistent with the capacity-side analysis: routing is FINE, the cosine-floor is the bind.

### Smoke regime caveats (BIAS-S band-calibration check)

**STRICT regime gate:** all 3 cells used `n_seeds=1` (seed=11 only). cv=null. There is **NO across-seed dispersion estimate** in the evidence. This bounds tier severely.

**Other regime properties:**
- M=2000 across all cells (NOT the M=10k Gap 2 target regime)
- encoder=Pythia-160m (NOT pythia-2.8b; the chain-grade ledger fly-LSH entry was pythia-2.8b)
- window=16 (v1, v2) and window=64 (v2b); short LM-window keys only
- CPU/numpy throughout

---

## Tier classification: MEASURED_MECHANISM (NOT chain-grade)

Per `[[feedback-cert-owner-overrides-director-via-by-construction-saturation]]` and Fix #28 default-under-claim, I am tiering DOWN from any chain-grade framing for the following independent reasons:

### Reason 1 (load-bearing): n_seeds=1 violates chain-grade dispersion requirement

Chain-grade requires across-seed CV computation. All three cells used a single seed (seed=11). The substrate-vs-KNN deltas of 0.003-0.007 are within the noise band of a single-seed measurement on M=2000 with discrete recall. The claim "substrate tracks KNN within +-0.007" is **smoke-grade-tight**, not chain-grade-tight. A 3-seed re-run might widen the band to ~+-0.020 (typical) or might confirm the tight bound. We do not know.

### Reason 2 (load-bearing): smoke-regime ceiling for cap_map re-classification

The "Gap 2 = GREEN-WITH-CHARACTERIZATION" ruling requires a claim about substrate's behavior across the gap's intended M-scale (M=10k+) and at production encoder (pythia-2.8b at minimum, ideally pythia-160m-2.8b sweep). The smoke evidence is M=2000 + pythia-160m only. The claim "the cosine-physics floor is itself non-chain-grade-capable on short-LM-window keys at M=2000" is **proven within the smoke regime**. Extrapolating to M=10k requires either (a) a chain-grade-tier confirmation cell or (b) explicit characterization-tier guard-rails on the cap_map row.

### Reason 3 (no by-construction-saturation, but...)

This is NOT a by-construction-saturation case (the metric is not pinned at a hard ceiling by problem geometry; KNN itself varies 0.045-0.158 across constructions). However, it IS a case where **the substrate IS at a measurable bound (KNN-cosine floor) but the bound is bounded BELOW the chain-grade-capable regime under the cell's parameters**. This is the M=10k recall-collapse phenomenon being reframed: substrate has not failed, it has saturated against the data's information content given encoder window + cosine-similarity metric. That is a **proven bound** -- the canonical MEASURED_MECHANISM disposition per my tier ladder.

### What MEASURED_MECHANISM means here

- The mechanism (substrate-routes-and-cleans-up-cosine-keys) **performs at the KNN cosine-physics ceiling** in this regime. That is a positive, durable, real finding.
- The ceiling itself **does not reach chain-grade recall thresholds** (~0.7-0.9) at M=2000 with pythia-160m short-window keys. That is a proven negative bound -- the COSINE-FLOOR ceiling is what is HARD_FAIL-tier on absolute recall, not the substrate.
- This counts as **+1 toward CERT N** (proven bound = chain-grade-eligible boundary).

---

## cap_map re-classification ruling

Research proposed: `Gap 2: RED -> GREEN-WITH-CHARACTERIZATION ("substrate-at-cosine-floor; non-cosine mechanism is high-M path")`

**APPROVED WITH ONE EXPLICIT LABEL.** The re-classification IS supported by the evidence as stated WHEN labeled appropriately. The substrate-is-at-cosine-floor claim is strong across 8 (cell, arm) combinations with 0% violations of the bound. The chain-grade ledger evidence (partition_routing M=10M = 0.978; fly-LSH M=10k = 0.997; KV learned M=10k held-out = 0.827) shows the substrate works at chain-grade on NATURAL-distribution keys at chain-grade M. The new Gap 2 framing reconciles both:

- WHEN the cosine-physics floor is high (natural keys, longer windows, larger M, better encoder) -> substrate IS chain-grade
- WHEN the cosine-physics floor is low (short windows, adversarial stride, small M, weaker encoder) -> substrate IS at the floor and the floor itself is not chain-grade-capable

**Required guard-rail on cap_map row** (this is the single change to Research's proposed wording):

> Gap 2 (Capacity): **GREEN-WITH-CHARACTERIZATION (smoke-validated; full-regime confirmation pending).** Substrate tracks the cosine-physics floor within +-0.007 (proven 8/8 in smoke at M=2000 pythia-160m). The cosine-physics floor itself is the high-M / production-encoder dependent variable; chain-grade ledger entries (fly-LSH M=10k pythia-2.8b, partition_routing M=10M, KV-learned M=10k) establish floor IS chain-grade-capable at full regime. Non-cosine mechanisms (refuse-gate / tag retrieval / sparse-fan-in) are the productized high-M path. **Single-seed smoke (cv=null) is the limit of current evidence; multi-seed M-scaling audit on pythia-2.8b would chain-grade-validate the re-classification.**

The guard-rail prevents the framing "Gap 2 is SOLVED" from over-traveling. Substrate-is-at-floor is solid; floor-IS-chain-grade-capable at full regime is established BY OTHER cells (not this 3-cell diagnostic).

---

## META atom proposal -- recommended atom shapes

Research proposed: `META_substrate_at_cosine_physics_floor_proven_across_three_independent_key_constructions_short_LM_window_cosine_NOT_chain_grade_capable_high_M_path_is_non_cosine_mechanism`

**APPROVED with shape adjustment.** Single-atom version compresses two claims that should be separable for future referent resolution. I recommend SPLIT into two distinct META atoms + one DERIVED rule. The split makes the smoke-regime caveat surface at the right atom.

### ATOM 1 (PRIMARY chain-grade-eligible bounded claim)

**ID:** `meta::T3/META_substrate_tracks_KNN_cosine_floor_within_0p007_across_eight_construction_param_combinations_n_seeds_1_smoke_M_2000_pythia_160m_window_16_to_64`

**Claim shape:** Substrate's recall-at-1 tracks exhaustive-cosine-KNN's recall-at-1 within delta(knn - sub) in [+0.0006, +0.0067] across 8 independent (construction x parameter) combinations spanning stride={1,4,8,16}, key-independence={same-article, different-articles}, window={16, 64}, all at M=2000 with pythia-160m on text8 prose, single-seed smoke. Substrate is ALWAYS at or below KNN (never above). The substrate-is-bounded-from-above-by-cosine-physics property is proven within this regime.

**Tier:** MEASURED_MECHANISM (single-seed smoke; M not at gap target; encoder not at production)

**Cert increment:** +1 toward CERT N (proven bound; same tier as a chain-grade boundary)

**Verdict field:** `MEASURED_MECHANISM_skunkworks_off_data_3_cell_8_combination`

**Cites:**
- `data/exp_substrate_gap2_stride_sweep_confirm_v1_smoketest/metrics.json`
- `data/exp_substrate_gap2_stride_sweep_confirm_v2_different_articles_per_key_smoke/metrics.json`
- `data/exp_substrate_gap2_stride_sweep_confirm_v2b_longer_window64_smoke/metrics.json`
- `notes/exp_dev_to_research_gap2_v2b_window64_SMOKE_GATED_accept_option_C_2026-06-26.md`

### ATOM 2 (DERIVED META RULE -- CERT-neutral)

**ID:** `meta::T3/META_cosine_physics_floor_on_short_LM_window_keys_M_2000_pythia_160m_is_below_chain_grade_band_recall_at_1_le_0p16_across_all_tested_constructions`

**Claim shape:** The KNN-cosine-physics ceiling on pythia-160m-encoded text8 keys with windows in [16, 64] tokens at M=2000 is empirically bounded above by 0.158 (window=64 DIFF arm; the maximum observed across 8 measurements). Substrate cannot exceed this ceiling regardless of cleanup mechanism. Window doubling (16->64) lifts the ceiling only ~0.015 in absolute recall; topical independence (different-articles vs stride-16-same-article) lifts the ceiling ~0.025-0.059. Therefore the high-M / chain-grade-capable path for Gap 2 is **non-cosine mechanism** (refuse-gate, sparse-tag retrieval, sparse-fan-in pattern separation, learned-projection metric), NOT geometric rescue of cosine-based dense cleanup.

**Tier:** META_RULE_CERT_NEUTRAL_skunkworks (does not directly increment CERT N; informs future cell design)

**Cert increment:** 0

**Verdict field:** `META_RULE_CERT_NEUTRAL_skunkworks`

**Cites:** same three metrics paths + prior 6 geometry-side HARD_FAILs (whitening / MIMO / DG / polarimetric / anisotropy_v4 / ScaNN).

### ATOM 3 (DISCIPLINE META -- CERT-neutral)

**ID:** `meta::T3/META_when_substrate_tracks_an_external_baseline_within_smoke_noise_band_AND_baseline_itself_is_low_the_chain_grade_path_is_baseline_replacement_not_baseline_rescue`

**Claim shape:** When substrate achieves recall within 0.01 of an external baseline (here: KNN exhaustive cosine) across multiple key constructions, AND that external baseline is itself below the chain-grade band on absolute recall, the productive path forward is to REPLACE the baseline metric class (cosine -> non-cosine: tag, sparse-LSH, learned-projection, refuse-gate) rather than to RESCUE within-class (which would have to beat the cosine-physics ceiling, an information-theoretic impossibility on this key distribution). This is a discipline-meta rule generalizing the Gap 2 finding into a project-wide pattern matcher.

**Tier:** META_RULE_CERT_NEUTRAL_skunkworks

**Cert increment:** 0

**Verdict field:** `META_RULE_CERT_NEUTRAL_skunkworks`

This third atom is the **principle-level abstraction** of the 6 geometry HARD_FAILs + the 3 stride-sweep MEASURED_MECHANISMs combined. It feeds Fix #26 pre-dispatch checks (would have prevented several of the geometry HARD_FAILs).

---

## Cumulative atomization recommendation -- what gets written to Store + cert_ledger

Three atoms total. All into `data/substrate_index/meta/atoms.jsonl` (and three corresponding rows in `data/substrate_index/meta/cert_ledger.jsonl`).

### Atom 1 (MEASURED_MECHANISM tier; +1 cert)
- Corpus: `meta`
- Atom name: `META_substrate_tracks_KNN_cosine_floor_within_0p007_across_eight_construction_param_combinations_n_seeds_1_smoke_M_2000_pythia_160m_window_16_to_64`
- Cert status: MEASURED_MECHANISM
- Cert class: chain_grade_eligible_proven_bound
- Cert increment delta: +1
- Referent: 3 metrics.json paths + 3 routing notes
- Verdict: MEASURED_MECHANISM_skunkworks_off_data_3_cell_8_combination

### Atom 2 (META rule; 0 cert increment)
- Corpus: `meta`
- Atom name: `META_cosine_physics_floor_on_short_LM_window_keys_M_2000_pythia_160m_is_below_chain_grade_band_recall_at_1_le_0p16_across_all_tested_constructions`
- Cert status: custom (META_RULE_CERT_NEUTRAL)
- Cert class: discipline_meta
- Cert increment delta: 0

### Atom 3 (META discipline rule; 0 cert increment)
- Corpus: `meta`
- Atom name: `META_when_substrate_tracks_an_external_baseline_within_smoke_noise_band_AND_baseline_itself_is_low_the_chain_grade_path_is_baseline_replacement_not_baseline_rescue`
- Cert status: custom (META_RULE_CERT_NEUTRAL)
- Cert class: discipline_meta
- Cert increment delta: 0

### Cert ledger impact

- Before: CERT 588 (per MEMORY.md)
- After: CERT 589 (one MEASURED_MECHANISM proven-bound = +1 per the tier ladder; two META rules = +0 each)
- cert_ledger.jsonl rows: 752 -> 755 (three new entries)

### Cumulative re-write of the 6 prior geometry HARD_FAILs?

**NO**. The 6 HARD_FAILs (whitening, MIMO, DG, polarimetric LEARNED, anisotropy_v4 AB tie, ScaNN aniso) are correctly tiered HARD_FAIL and should remain so. They are NOT MEASURED_MECHANISMs (they were attempts to lift recall above cosine-floor, and they did not; the consolidated atom characterizes WHY they cannot, which is the post-hoc explanation). The new META rule (atom 2) supersedes their interpretation but not their cert status.

---

## Anti-bias / referent-checks performed (per discipline catalog)

**Fix #28 strict (per-arm metrics, not verdict_msg):** I read all per-arm values from `detail/per_*_recall_at_1_median` and `detail/per_*_knn_recall_at_1_median` directly. The verdict_msg in v1 is "HARD_FAIL_KNN_SENTINEL_REGRESSION" but per-arm metrics are the load-bearing source for the consolidated CLAIM. v1's HARD_FAIL was correct WITHIN ITS OWN pre-reg (KNN<0.80 sentinel breached); the CONSOLIDATED claim is a DIFFERENT and broader claim about substrate-tracks-KNN-physics. The v1 cell-internal verdict and the consolidated cross-cell claim are NOT in conflict.

**Fix #26 verify-the-referent:** Each atom's referent_pointer cites the exact metrics.json path (not the verdict notes). The ATOM IDs explicitly include the regime descriptors (M=2000, pythia-160m, n_seeds=1, window=16_to_64) so future referents cannot inflate the claim's scope.

**BIAS-N verify-referent-verdict-field:** atom 1 verdict field is MEASURED_MECHANISM_skunkworks_off_data_3_cell_8_combination. It is a TIER not a recall lift claim. Atoms 2 and 3 are META_RULE_CERT_NEUTRAL_skunkworks. The verdict-field-matches-claim check passes.

**BIAS-Q suspect 1.000 results:** N/A here; all recall values are well below 0.2. No suspicious metric saturation.

**BIAS-R contamination / regime / mismatch:**
- Contamination: same encoder (pythia-160m) across all 3 cells; same text corpus (text8); same seed (11). Cross-cell contamination is BOUNDED because each cell builds keys independently. No data leakage.
- Regime: SMOKE only. M=2000, n_seeds=1. The atom-1 ID makes this explicit. **The risk of band-mis-calibration at full regime (pythia-2.8b, M=10k, n_seeds>=3) is the dominant source of uncertainty.** This is what the cap_map guard-rail captures.
- Mismatch: smoke regime does NOT match what we'd see at full pythia-2.8b. The METAL atom-1 ID bakes this caveat in; atom-2 explicitly says "M=2000_pythia_160m"; atom-3 is regime-agnostic discipline. The split-into-3-atoms structure is precisely to surface this regime mismatch where it bites.

**BIAS-S band-calibration regime check (USER 2026-06-25):** the 3 cells were authored AS smoke + designed to gate full dispatch. Band design (HF_REAL_RECALL < 0.50; HP_DIFFART_RECALL >= 0.90) was appropriate for a chain-grade ambition at full. The smoke regime's outcomes (recall 0.04-0.16) sit in the HF band and PROPERLY GATE OFF full dispatch. This is band-calibration WORKING AS DESIGNED. The MEASURED_MECHANISM tier preserves this: we accept the smoke evidence as proven WITHIN the smoke regime; we do NOT promote to chain-grade off smoke alone.

**Symmetric anti-negativity:** I considered the possibility that I'm too HARSH on the tier. The opposing case: substrate-tracks-KNN-within-0.007 across 8 combinations IS strong evidence; substrate-NEVER-beats-KNN (delta_knn-sub always non-negative) is even stronger; the cosine-physics framing is well-supported by 6 prior geometry HARD_FAILs + lit (Cai-Kanai-Belkin / Mu-Viswanath / ScaNN). Could this be chain-grade? Answer: the tier ceiling is bound by n_seeds=1 alone. The substantive claim is strong; the dispersion-tightness evidence is absent. MEASURED_MECHANISM IS the right tier; if the 3-seed audit at pythia-2.8b later confirms, then promote to chain-grade. I do not want to under-tier OR over-tier; MEASURED_MECHANISM is the symmetric correct tier here.

---

## A5 atomization gate -- pre-write checklist

I am NOT executing the atomization write in this turn. Per role separation, I file the proposal here; Research (Director) routes for write OR I dispatch the A5-gated write via `tools/atomize_*` after Research ACK. The proposal is complete and atom IDs are final.

Pre-write checklist (for the executor):
- [ ] Read current `meta/cert_ledger.jsonl` (752 rows confirmed; will become 755)
- [ ] Read current `meta/atoms.jsonl` (175 atoms confirmed; will become 178)
- [ ] Append 3 atom rows (atomic tmp -> os.replace) -- SERIAL writes per Store partition concurrency rule
- [ ] Append 3 cert_ledger rows (one per atom, with cert_increment_delta = +1, 0, 0)
- [ ] Verify-LOAD: `python -c "from hdlab.store import Store; s=Store('data/substrate_index/meta'); s.load(); print(len(s.atoms))"` -> 178
- [ ] git commit by path: `git add data/substrate_index/meta/atoms.jsonl data/substrate_index/meta/cert_ledger.jsonl notes/skunkworks_gap2_consolidated_landed_vet_2026-06-26.md` (NEVER `git add -A`)
- [ ] git commit message: include cert N delta (588 -> 589) and atom IDs

---

## Summary of rulings (one block)

1. **Landed-VET:** PASSED (all 8 delta numbers reproduce exactly; window-doubling lift +0.0153 reproduces; beats_rail lifts reproduce; substrate-NEVER-beats-KNN strengthens the bound)
2. **Tier:** MEASURED_MECHANISM (proven bound; n_seeds=1 + M=2000 + pythia-160m smoke caps at this tier)
3. **cap_map ruling:** GREEN-WITH-CHARACTERIZATION ACCEPTED with explicit single-seed-smoke / pending-full-regime label
4. **Atom recommendation:** Split into 3 atoms (1 MEASURED_MECHANISM proven bound + 1 META rule on cosine-floor + 1 discipline-META rule on baseline-replacement-vs-rescue). Cert N: 588 -> 589 (+1)
5. **No demotion of the 6 prior geometry HARD_FAILs** (they remain HARD_FAIL; the new META rule provides the post-hoc explanation, not a retroactive demotion)
6. **Future cell to chain-grade-validate:** 3-seed pythia-2.8b M-scaling sweep on natural-key DIFFERENT_ARTICLES at M={10k, 100k, 1M} would close the smoke-to-chain-grade gap; recommend as next dispatch when GPU available

Standing -- proposal complete; await Research ACK then dispatch A5-gated Store write.
