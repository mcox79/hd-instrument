# 2x Research Drill: Understanding the v3b Batch-Ratio-Match HARD_FAIL (2026-07-04)

**Author:** Research (Director role).
**Trigger:** v3b (`data/exp_encoder_migration_step1b_v3b_nce_ablation_dense_recovery_diagnostic_v1/metrics.json`)
landed `HARD_FAIL` on its primary tier (`BATCH_RATIO_MATCH_DID_NOT_CONFIRM`): matching the FULL-scale
batch/N coverage ratio at MID (batch 128 over N_train=39,515) did NOT reproduce the predicted in-batch
collapse signature. Per SOP (negatives -> 2x research drill), this is a 2x operational drill on the
existing findings, not a re-scan-as-verification. Method: direct on-disk re-derivation from
`metrics.json`'s `recovery{}` block plus the actual training-loop code
(`experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py`,
functions `_mine_teacher`, `_cluster_batch_idx`, `_train_student`), cross-checked against 4 parallel
Sonnet lit-scans using generic ML terms only (query-privacy discipline observed — no
substrate/mechanism-specific vocabulary used off-platform). Per role contract: lit-scan calibration
penalty applied throughout (deflate 0.15-0.25 off naive reads; novel-synthesis extrapolation to our
exact combined setup capped at 0.50).

**No experiments dispatched by this drill** — decision/diagnostic memo only, per instruction.

---

## HEADLINE

**The batch-ratio-match sweep did not fail because MID was still underpowered — it failed because the
sweep's own construction leaves a much larger, oppositely-behaving confound active throughout, and because
part of the motivating collapse is very likely driven by raw vocabulary cardinality, a variable no batch
ratio can stand in for.** Direct code read confirms: the near-neighbor/contrastive (NCE) term's positives
and semi-hard negatives are mined **once, globally, over the entire training vocabulary**
(`_mine_teacher`, called before any batch loop begins), and are indexed **per-item** in every training
step regardless of which items happen to co-occur in the current batch (`_cluster_batch_idx` with
`cluster_frac=0.0` — the value actually used — draws a **pure random** batch; the near-neighbor structure
enters entirely through the pre-mined `pos_idx`/`semi_cands` lookup, not through batch composition).
`semi_hard_coverage: 1.0` in the landed metrics (virtually every item has a valid mined semi-hard set)
confirms this channel is fully populated at MID. Two independent lit-scans (offline/ANCE-style mining;
MoCo/CompRess/SEED memory-queue lineage) support that this exact mining-once pattern decouples
near-neighbor gradient from batch size — which is why `in_batch` DENSE did **not** degrade as batch shrank
(`{512: 0.412, 256: 0.381, 128: 0.466, 64: 0.432}`, `inbatch_trend_corr=-0.474`, i.e. essentially flat/
noisy, not the predicted monotonic decline). Separately, the NCE term itself is held at **constant weight
(nce_weight=0.5) across the entire sweep** — and the secondary tier of this SAME run shows that ablating
that one term alone moves DENSE by **+0.465** (0.269 -> 0.734), 3-5x larger than any batch-driven delta
observed anywhere in the primary sweep. A third lit-scan independently supports that InfoNCE-style
uniformity/repulsion pressure scales with negative count (which itself scales with batch size), meaning
the swept variable (batch) simultaneously moves *two* mechanisms in the loss (the intended in-batch
coverage axis, and the unintended contrastive-antagonism-strength axis) — "a batch-size sweep at constant
contrastive weight is confounded by construction" (lit-scan read, ~70% confidence). Finally, the raw
numbers themselves point at a third, likely-dominant driver that ISN'T ratio-shaped at all: DENSE fell
from **0.825 at smoke scale (V~3,000)** to **~0.36-0.47 at MID (V=39,515)** even at the *most generous*
tested ratio (batch=512, 4x more generous than FULL's own collapse point) — a drop no batch trick can
explain, because the ratio there was *better*, not worse, than FULL's. A fourth lit-scan independently
supports that fixed-capacity-embedding degradation as raw item-count grows is a recognized, structurally
separate phenomenon from batch-relative coverage (generalized neural-collapse theory for many-classes
regimes; a sign-rank/combinatorial capacity-ceiling result that holds even with **no training or batch
effects at all**).

**P_deflated(confound-plus-decoupled-mining is the dominant explanation for the null sweep trend) = 0.50**
(capped; novel synthesis of our exact combined setup, though each component is independently
lit-supported).
**P_deflated(raw cardinality/vocabulary-size ceiling is a real, independent contributor to the smoke->MID
drop) = 0.45** (capped; strong structural analogs, no source runs our exact ceteris-paribus design).

---

## Q1 — Why did coverage-ratio-matching fail to reproduce the FULL pathology at MID?

Ranking the four candidates the task posed, against on-disk evidence + lit-scan:

| Rank | Candidate | Verdict | Evidence |
|---|---|---|---|
| **1 (joint-primary)** | **(d) the harmful NCE term confounded both arms** | **CONFIRMED, dominant** | Directly measured: NCE ablation (same run, same batch=128, global objective) moved DENSE 0.269->0.734 (+0.465) — 3-5x the magnitude of anything the batch sweep produced (sweep range across all 8 batch/objective cells: 0.269-0.466, span 0.197). Lit-scan 3: contrastive-term antagonism strength is itself batch-size-dependent (uniformity/repulsion scales with negative count — Wang & Isola 2020; Wu et al., IJCAI 2022), so sweeping batch at constant NCE weight moves the confound *and* the intended variable together — "a batch-size sweep at constant contrastive weight is confounded by construction" (~70% confidence per lit-scan). This alone is sufficient to explain why neither arm showed the hypothesized clean monotonic trend. |
| **1 (joint-primary)** | **(b) mining/semi-hard-negative sampling supplies near-neighbor gradient independent of in-batch co-occurrence** | **CONFIRMED by direct code read** | `_mine_teacher` computes `pos_idx` (global top-1 teacher-nearest-neighbor per item) and `semi_cands` (per-item semi-hard candidate pool) **once**, before any batch loop, over the full `V`. Every training step's NCE term (`l_nce`) draws these per-item, **regardless of the current batch draw or its size** (`_cluster_batch_idx(batch, cluster_frac=0.0, ...)` returns a pure `torch.randint` — no clustering is active; near-neighbor structure enters *only* via the pre-mined lookup). `semi_hard_coverage=1.0` in the landed metrics confirms near-total population of this channel at MID. Lit-scan 1 independently supports that this exact "mine once, index per-item" pattern (ANCE, offline triplet mining, MoCo/CompRess/SEED memory-queue lineage) structurally decouples near-neighbor supervision from batch composition — precisely the mechanism that would mask a pure in-batch-coverage-collapse signal. |
| **2 (secondary, real, independent)** | **(c) the 43.9k held-set geometry is intrinsically easier (scale-of-VOCAB not scale-of-ratio)** | **LIKELY, real, independent axis** | Raw magnitude check: DENSE dropped from 0.825 (smoke, V~3,000) to 0.36-0.47 across the *entire* MID sweep (V=39,515) — including at batch=512, whose coverage ratio (1.296%) is **4x more generous** than FULL's own collapse-inducing ratio (0.32%). A ratio-based story predicts MID-at-batch-512 should look close to smoke-level (generous coverage); it does not. This is direct evidence that raw item-count, not the batch/V ratio, is doing a large share of the work. Lit-scan 2 independently supports cardinality-driven degradation as a *structurally separate* failure axis from batch-relative coverage (generalized neural collapse in the many-classes-vs-dimension regime, Jiang et al. ICML 2024; a fixed-embedding-dimension sign-rank/combinatorial capacity bound that holds even with **zero training/batch effects**, Google DeepMind LIMIT paper, arXiv:2508.21038) — moderate confidence, no source runs our exact controlled design, but the structural argument is strong and holds independent of anything this cell measured. |
| **3 (not independently load-bearing)** | **(a) cumulative distinct near-neighbors seen over TRAINING (steps x batch) exceeds per-step coverage** | **Real but subsumed, not separately diagnostic** | With 1,800 steps, even batch=64 yields 115,200 batch-draws against V=39,515 — every item is drawn multiple times in expectation regardless of the batch axis, so this mechanism would blunt a pure-random-co-occurrence starvation story on its own. But it is functionally redundant with (b): the actually-operative near-neighbor channel is the globally-mined NCE term, not accumulated random RKD-target co-occurrence, so (a) doesn't need to be separately invoked to explain the null result — (b) already fully accounts for it. |

**What this means for whether ANY MID proxy can stand in for the FULL in-batch collapse:**

A ratio-matched reduced-scale proxy is valid **only when (i) the swept ratio is the sole/dominant
mechanism at work, and (ii) every other loss term that could also respond to the same swept variable is
neutralized or held at a known-safe value.** This test satisfied neither condition: the NCE term shares
the batch-size knob (via its in-batch-negative count) and was left at a materially harmful constant
weight throughout, and part of the target phenomenon (cardinality-driven ceiling) is not a ratio-representable
quantity at all — no batch/N trick at a smaller V can manufacture a "large V" effect. This is a genuine
sharpening of the standing memory rule
(`feedback_scale_dependent_failure_validation_must_match_batch_N_ratio_not_absolute_N_2026-07-04`), not a
contradiction of it: ratio-matching remains necessary for ratio-driven mechanisms, but it is not
**sufficient** — before ratio-matching, isolate the target mechanism by zeroing/holding-constant every
co-active loss term that also depends on the swept variable, or the sweep risks a phantom-null result for
an entirely different reason than underpowering (a confound, the mirror image of the underpowering trap
the memory rule was written to catch). A closely-analogous methodological finding surfaced independently
in lit-scan 4: critical-batch-size in pretraining scales with **dataset size** (~D^0.47), essentially
independent of model size (Zhang et al., arXiv:2410.21676, ICLR 2025) — a case in the wild where an
intuitive "ratio" framing was empirically falsified in favor of an absolute-scale driver, reinforcing that
ratio-vs-absolute-scale confusion is a known trap, not a one-off here.

**Practical upshot:** no reduced-V proxy, however ratio-matched, can currently be trusted as a stand-in for
the FULL in-batch collapse question on its own. Two cheap (not-yet-run) diagnostics would meaningfully
sharpen this before spending a FULL-scale GPU dispatch: (1) rerun the batch sweep with NCE weight pinned
to 0 throughout (isolates the true coverage-ratio mechanism from the antagonism confound), and (2) a
raw-V sweep at a fixed, generous batch/N ratio (varies vocabulary size directly, holding coverage safely
non-starved, to test the cardinality-ceiling hypothesis in isolation). Neither is dispatched by this
drill — flagged as candidate cheap follow-ups only.

---

## Q2 — Is the landmark/global objective hypothesis DEAD, untestable-at-MID, or worth the FULL test?

**Current measured state (this run, NCE held at its current constant weight throughout the sweep):**
`in_batch` beat `global` at **every** tested batch size — `{512: 0.412 vs 0.362, 256: 0.381 vs 0.309, 128:
0.466 vs 0.269, 64: 0.432 vs 0.301}` — and `global` was *more* batch-size-sensitive than `in_batch`
(`global_trend_corr=0.883`, positive = shrinking batch hurts global; `inbatch_trend_corr=-0.474`, weak/
noisy), the **opposite** of the fixed-landmark-frame-should-be-batch-independent rationale the objective
was built on. This is a real, measured reversal — not something the confound erases.

**But it is genuinely unresolved, not falsified**, for one specific reason: the single decisive tie-breaker
datapoint was never run. The NCE ablation (the mechanism now shown to move DENSE by +0.465) was applied
**only to the `global` arm** at batch=128 (per this cell's own pre-reg design, Section B: "ABLATE the NCE
term at the decisive batch (global objective only)"). There is no `in_batch + NCE_ZERO` datapoint at
batch=128 to compare against `global + NCE_ZERO`'s 0.734. Given lit-scan 3's finding that the sweep is
confounded by construction, we cannot yet tell whether `in_batch`'s current lead is a genuine, antagonism-
independent advantage, or an artifact of `in_batch` merely tolerating the shared NCE antagonism *better*
than `global` does (plausible: `in_batch`'s own RKD target lives in the same batch-relative space as the
NCE term, so the two may interfere less geometrically than `global`'s fixed-landmark-space target does
against a batch-relative NCE term — this is a mechanism-level hypothesis, not yet tested, offered at
P_deflated 0.30, capped, no direct lit precedent for this specific interaction).

**Rank call: CONDITIONAL DROP, gated on one free confirmatory arm — do not dispatch the FULL-scale
landmark test yet.**

- The NCE-schedule fix (Rank 1 from the prior ranked-levers drill) is now unambiguously the dominant,
  cheapest, best-evidenced lever (+0.465 measured, converging with 3 independent lit-scans this cycle and
  last cycle).
- The landmark/global mechanism currently *loses* every head-to-head comparison run so far, even though
  those comparisons are confound-tainted. A hypothesis that is both (a) unconfirmed and (b) behind in
  every measured comparison does not merit spending the once-per-stage FULL-scale GPU budget before the
  cheapest remaining test that could settle it is run.
- That cheapest remaining test — `in_batch` objective + `nce_weight=0` at batch=128 — reuses 100% of this
  cell's existing infrastructure (mining shards, split, seed; `in_batch` needs no landmark indices at all)
  and costs roughly one more training arm at MID scale (a fraction of the ~35-90 min this whole 10-arm
  cell took). It is the single highest-information-per-dollar action available before committing FULL-scale
  compute to either objective.

**Falsifiable pre-registered bands for that next cheap arm** (HARD-PASS / HARD-FAIL, per lit-scan
calibration discipline — explicit thresholds, not vibes):

- **HARD-PASS (drop landmark mechanism entirely; FULL dispatch = `in_batch` + NCE-off/schedule fix only,
  no landmark bookkeeping needed):** `in_batch_NCE_ZERO_dense_final` (batch=128, same infra) `>= 0.70` AND
  within `0.05` of `global_NCE_ZERO`'s `0.734` (i.e. `delta_vs_global_nce_zero >= -0.05`). Interpretation:
  once the antagonism confound is removed, the simpler objective matches or beats the more complex one —
  the landmark frame was solving a problem (in-batch coverage starvation) that, per Q1, does not actually
  bind at this scale/ratio.
- **HARD-FAIL (landmark mechanism still earns its complexity; worth a FULL-scale test, paired with the
  now-validated NCE-off fix):** `in_batch_NCE_ZERO_dense_final <= 0.60`, i.e. a gap of `>= 0.13` below
  `global_NCE_ZERO`'s `0.734`. Interpretation: once the antagonism confound is removed, `global`'s
  advantage re-emerges — the earlier reversal was antagonism-driven, not a genuine ceiling on the landmark
  mechanism, and the fixed-landmark-frame idea should get its FULL-scale test after all, using the NCE-off
  schedule.
- **MIDDLE BAND:** `in_batch_NCE_ZERO_dense_final` in `[0.60, 0.70)`. Ambiguous; default to the simpler
  objective (`in_batch`, no landmark-refresh bookkeeping) for the FULL dispatch unless Director/USER
  judgment sees a reason to prefer the extra complexity, rather than re-running further MID arms to
  resolve a small gap.

**P_deflated(landmark/global objective adds value beyond the NCE-schedule fix alone, pending that arm) =
0.35** — below even odds, reflecting that current measured evidence (confounded though it is) consistently
favors the simpler alternative, while acknowledging the decisive test genuinely has not been run.

---

## Cheap decisive test (restated, single most important action)

Run one additional MID arm reusing 100% of v3b's existing infrastructure: `in_batch` objective, batch=128,
`nce_weight=0.0` (mirrors the existing `NCE_ZERO` ablation but on the `in_batch` arm instead of `global`).
No new mining, no new landmarks, no new split. This is the single cheapest action that discriminates
"the landmark mechanism was never the fix; the NCE-schedule fix is sufficient alone" from "the landmark
mechanism's advantage was there all along, masked by the antagonism confound" — settling Q2 with data
instead of the current confound-limited inference. **Not dispatched by this drill** (per instruction);
flagged for Director to route to exp_dev if judged worth the near-zero marginal cost.

Two further, slightly more expensive but still cheap, follow-up diagnostics (also not dispatched):
1. Re-run the primary batch sweep with NCE weight pinned to 0 throughout (isolates the true coverage-ratio
   mechanism, addressing the Q1 confound directly).
2. A raw-vocabulary-size sweep (e.g. V = 10k / 20k / 40k) at a fixed, generous batch/N ratio, to test the
   cardinality-ceiling hypothesis (Q1 candidate (c)) in isolation from any batch-ratio effect.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL) — summary table

| Question | HARD-PASS | HARD-FAIL | Gates |
|---|---|---|---|
| Q2 decisive arm (`in_batch`+NCE_ZERO@batch=128) | `>=0.70` and within `0.05` of `0.734` | `<=0.60` (gap `>=0.13`) | Drop-landmark vs earn-FULL-test call |
| (Optional) NCE-pinned-zero batch sweep | `inbatch_degradation >= 0.10` AND `inbatch_trend_corr >= 0.50` (reproduces original v3b primary-tier bands, now deconfounded) | `inbatch_degradation < 0.05` even with NCE=0 | Confirms/kills the ORIGINAL coverage-ratio mechanism cleanly, independent of antagonism |
| (Optional) raw-V sweep at fixed generous ratio | DENSE degrades `>=0.15` from V=10k to V=40k at constant generous ratio | DENSE flat (`<0.05` change) across V at constant generous ratio | Confirms/kills the cardinality-ceiling hypothesis (Q1 candidate c) independent of batch tricks |

---

## Cross-thread synthesis

- **`research_drill_encoder_052_to_085_ranked_levers_2026-07-04.md`** (prior cycle, same day): correctly
  identified the NCE-schedule fix as the top lever (P_deflated=0.55) via a separate lit-scan pass; this
  drill's independent 3-lit-scan re-confirmation (contrastive antagonism batch-dependence; alignment-
  uniformity theory) converges on the same mechanism from a different angle (why the *sweep* failed,
  rather than what the *fix* should be) — mutually reinforcing, not redundant.
- **`encoder_rescue_plan_converged_diagnosis_2026-07-04.md`**: sequenced R1 (global/landmark objective) as
  the lead rescue lever, assuming the in-batch-coverage-starvation diagnosis was the primary mechanism.
  This drill's Q1 finding (cardinality may be co-dominant, and the sweep was confound-tainted) does not
  overturn R1's underlying motivation (FULL genuinely did collapse, DENSE_SIGN 0.825->0.368), but it does
  mean the ORIGINAL causal story ("in-batch coverage starves the RKD target") is now only one of at least
  two plausible co-contributors (the other being raw-cardinality ceiling), and the fix that has actually
  demonstrated a large, clean, reproducible effect (NCE-off) does not require the landmark mechanism at
  all to obtain its win.
- **`feedback_scale_dependent_failure_validation_must_match_batch_N_ratio_not_absolute_N_2026-07-04`**
  (memory rule, filed same day from the R1 phantom-negative case): this drill sharpens rather than
  contradicts that rule — ratio-matching is necessary-but-not-sufficient; it must be paired with isolating
  the target mechanism from co-active confounds, and it cannot substitute for a true-scale test when part
  of the phenomenon is driven by an absolute (non-ratio) variable like raw cardinality.
- **`research_drill_sparse_code_semantic_fidelity_frontier_2026-07-04.md`**: sparsity was already ruled
  out as the bottleneck (2% vs 3.1%, DENSE~0.52 vs ~0.51, no material gap) — unaffected by this drill;
  the cardinality-ceiling hypothesis surfaced here is about the DENSE (pre-sparsifier) readout itself, a
  layer upstream of that prior finding, not a reopening of it.

---

## Substrate-product implications

- **No new build required for the single highest-value next step.** The decisive Q2 tie-breaker
  (`in_batch`+NCE_ZERO@batch=128) is a config variant of an arm this cell already runs — zero new
  infrastructure, near-zero marginal compute.
- **The once-per-stage FULL-scale GPU dispatch should NOT be spent on the landmark/global objective yet.**
  Current evidence (even confound-tainted) consistently favors the simpler `in_batch` alternative; spending
  the scarce FULL-scale budget on the more complex, currently-losing mechanism before the free tie-breaker
  runs would be premature.
- **A new, previously-unflagged risk for the USER/Director decision layer:** if the cardinality-ceiling
  hypothesis (Q1 candidate c) is correct, then even after the NCE-schedule fix and the best objective are
  both chosen optimally, there may be a residual ceiling on DENSE quality driven by raw vocabulary size
  (V=160k-178k at true FULL scale) that neither the objective choice nor the antagonism fix can remove —
  this would reopen, at a different layer, the outer-bound caution the prior design-correctness drill
  already flagged (P=0.05 for the pre-distillation design reaching 0.85) as a residual risk on the
  distillation redesign itself, not just its predecessor. This drill does NOT resolve that question (the
  raw-V sweep diagnostic above would); it surfaces it as a live possibility that the smoke-vs-MID gap
  cannot currently be explained away purely by batch tricks or NCE-schedule fixes.
- **Methodology hardening for future reduced-scale validations** (applies beyond this specific encoder
  arc): before trusting a ratio-matched cheap proxy, explicitly check (1) whether any other loss/config
  term shares the swept knob and would need to be neutralized first, and (2) whether the target failure
  has a plausible absolute-scale (non-ratio) component that no downscale can reproduce. Both checks are
  cheap (a code read + a magnitude sanity-check against the smallest available scale point) and would have
  caught this confound before the sweep was dispatched.

---

## Citations (verified count)

**4 parallel Sonnet lit-scan sub-agents, each independently verifying sources via WebSearch/WebFetch this
cycle** (not merely cited from memory — existence checks performed live). Load-bearing citations, by
lit-scan:

- **Mined-negative batch-independence (lit-scan 1):** Xiong et al., "Approximate Nearest Neighbor Negative
  Contrastive Learning for Dense Text Retrieval" (ANCE), ICLR 2021, arXiv:2007.00808 (verified); He et al.,
  MoCo, CVPR 2020 (verified); Musgrave, Lim, Belongie, "A Metric Learning Reality Check," ECCV 2020
  (verified); Kim et al., "Proxy Anchor Loss for Deep Metric Learning," CVPR 2020 (verified); offline vs
  online triplet mining, arXiv:2007.02200 (verified). One PD-Loss preprint (arXiv:2508.17082) flagged
  lower-confidence by the sub-agent itself.
- **Cardinality vs ratio scaling (lit-scan 2):** Jiang et al., "Generalized Neural Collapse for a Large
  Number of Classes," ICML 2024, arXiv:2310.05351 (verified); "On the Theoretical Limitations of
  Embedding-Based Retrieval" (LIMIT benchmark), Google DeepMind, arXiv:2508.21038 (verified, holds with
  zero training/batch confound); ArcFace/Partial-FC large-scale face-recognition line (secondary-source
  described, not independently re-fetched). One cluster-discrimination paper (arXiv:2407.17331) flagged
  unverified-numeric-claim by the sub-agent itself.
- **Contrastive antagonism batch-dependence (lit-scan 3):** Wang & Isola, "Understanding Contrastive
  Representation Learning through Alignment and Uniformity," ICML 2020 (verified); Wu et al., "Rethinking
  InfoNCE: How Many Negative Samples Do You Need?" IJCAI 2022 (verified); "Contrastive Supervised
  Distillation for Continual Representation Learning," arXiv:2205.05476 (verified); "Relational
  Representation Distillation," arXiv:2407.12073 (verified). One 2026 preprint (arXiv:2604.13313) flagged
  lower-confidence by the sub-agent itself.
- **Reduced-scale proxy methodology (lit-scan 4):** Wortsman et al., "Small-scale proxies for large-scale
  Transformer training instabilities," ICLR 2024, arXiv:2309.14322 (verified); Yang et al., Tensor Programs
  V / muP, Microsoft Research (verified); Wei et al., "Emergent Abilities of Large Language Models," TMLR
  2022, arXiv:2206.07682 (verified); Zhang et al., "How Does Critical Batch Size Scale in Pre-training?"
  ICLR 2025, arXiv:2410.21676 (verified — the dataset-size-not-model-size finding is the load-bearing
  analog for this drill's methodology point); Wang et al., "Can Small Training Runs Reliably Guide Data
  Curation?", ICLR 2026, arXiv:2512.24503 (verified).

**Total distinct sources across all 4 scans: ~20, of which ~17 were live-verified to exist by the
searching sub-agent (title/venue/arXiv-id confirmed via fetch), 3 flagged explicitly as
lower-confidence/unverified by the sub-agents themselves** (reported honestly above, not silently dropped).
None were independently re-fetched by this synthesizing agent; apply the standard discount for that tier
of citation confidence, per standing lit-scan-calibration discipline.

---

## Intuitive summary (plain language, 6-10 lines)

We tried a cheap trick to test an expensive idea: instead of running the full-size training job, we shrunk
it down but kept the "crowding" ratio the same, hoping to see the same failure show up in miniature. It
didn't show up — but not because the trick failed to shrink correctly. Reading the actual code, we found
the training loop has a SECOND source of near-neighbor teaching (a pre-computed lookup table built once,
before training starts) that works exactly the same at every batch size, so shrinking the batch never
truly starved that channel the way we assumed. On top of that, the training run's own "turn off one
ingredient" test (already done, same run) shows a single other ingredient — a nitpicking comparison term —
explains a change five times bigger than anything the batch-size trick produced, and outside research
confirms that ingredient's strength itself shifts with batch size too, so our test was quietly comparing
two moving targets, not one. There's also a third, simpler possibility outside literature independently
supports: maybe it's not about batch size tricks at all — maybe a fixed-size code just gets harder to use
correctly as the number of things it needs to tell apart grows, no matter how you draw your training
batches. **Methodology takeaway: a shrunk-down "ratio-matched" stand-in test is only trustworthy if (a) you
first neutralize every other ingredient in the recipe that also reacts to the same batch-size dial you're
turning, and (b) the failure isn't secretly driven by sheer scale of "how many things to tell apart" rather
than any ratio at all — shrinking never fixes that second kind. Go/drop call: keep the landmark-based fix
idea alive but do NOT spend the expensive full-scale test on it yet — run one more free, already-built
variant first (the simple objective with the nitpicking term turned off) to see if it alone already wins,
which the current evidence leans toward.**

ASCII-only. No emojis. No em dashes.
