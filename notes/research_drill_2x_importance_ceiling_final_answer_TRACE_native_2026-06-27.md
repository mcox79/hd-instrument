# 2x Drill — Importance-Ceiling Final Scientific Conclusion

**Date:** 2026-06-27 (afternoon)
**Author:** Research (Director)
**Trigger:** USER 2x-drill request after claimed full-scale falsification at d=16384/M=4096/n=8 seeds with quoted numbers (TRACE=0.998, Rand=0.006, PCA=0.010 cv=8.234, Fisher=0.036).
**Predecessor:** `research_drill_5x_progressive_importance_ceiling_load_bearing_2026-06-27.md` (the load-bearing drill that proposed the falsification cell).
**Discipline applied:** Verify-the-referent + Fix #28 (read metrics.json per-arm, not verdict text) + Skunkworks-style refusal pattern when data is phantom.

---

## TL;DR

**REFUSE to atomize a META_FINDING from the numbers in the prompt.** The cited full-scale d=16384/M=4096/n=8 result does NOT exist on local disk. The only on-disk artifact for `exp_importance_ceiling_falsification_multi_readout_d16384_n8seeds_v1` is a SELFTEST_OK smoke (verdict line: `TRACE=0.093, RAND=0.292, PCA=0.384, CRLB_k1=0.2421, CRLB_k8=0.0856`) — completely different numbers, NOT a full-scale falsification result.

The prompt's framing — "TRACE saturates at 0.998; everything else at chance with cv=8" — is the same pattern Skunkworks flagged this morning in batch7 (orchestrator-reported verdicts with no on-disk evidence: `skunkworks_to_research_FLAGBACK_batch7_4cell_phantom_no_full_landings_2026-06-27.md`). Atomizing it would be a Fix #28 violation in exactly the way Skunkworks just refused.

**The honest conclusion is structural, not data-driven:** the importance-ceiling drilling arc CAN be cleanly bounded by what we already know (5x drill + on-disk smoke), but the META_FINDING the prompt asks for needs the actual full-scale metrics.json to land first. Below I do the 2x drill on the WELL-FOUNDED claims that survive the verify-the-referent gate, then state what to do once real data arrives.

---

## What the on-disk evidence actually says

**Cells that exist with full metrics.json:**
- `exp_importance_ceiling_falsification_multi_readout_d16384_n8seeds_v1/metrics.json` — `verdict: SELFTEST_OK`, `run_mode: smoke`, N=1024, M=60, seeds=[7]. Structure-verification only. NOT the d=16384 full run.
- `exp_multi_readout_fisher_importance_v1/metrics.json` — `verdict: HARD_FAIL`, smoke at N=2048, M=100, n=2 seeds. Per-arm cv=1.23 for Fisher (not cv=8). PCA-basis seed-17 hit +0.144 (above CRLB floor of 0.078).
- Six earlier edge_importance cells — all in capacity-saturated regimes (M/d ≥ 0.8) where the CRLB floor itself exceeds 0.5. TRACE arms cleared +0.30 routinely via the recency-side-channel.

**Cells that do NOT exist:**
- No full (non-smoke) `exp_importance_ceiling_falsification_multi_readout_d16384_n8seeds_v1` metrics.json on local disk.
- No recent_landings.jsonl entry for this anchor (ledger last touched 2026-06-23; stale).
- No cell .py script in `cells/` for this anchor (cell-author smoke wrote metrics directly without persisting source).

**Conclusion:** the cited full-scale results are unverifiable. They may exist on a remote runner not yet replicated; they may be a hallucinated framing from an upstream session; they may be a partial that wasn't written. Until the actual file appears, refusing to atomize is the correct cert-discipline.

---

## ANGLE A — Multi-readout Fisher: what we ACTUALLY know

The prompt asks "why does Fisher fusion fail entirely (not just hit ceiling)?" — but on the evidence we have, **Fisher hasn't yet failed at the relevant regime**. The smoke at N=2048/M=100/k=8/n=2-seeds gave Fisher mean = +0.039 with cv=1.23. The 5x drill correctly noted:

- The Fisher cell-mean is below the CRLB floor (0.078 at this regime), which is consistent with statistical noise on n=2 seeds — NOT proof Fisher fails.
- PCA-basis seed-17 hit +0.144 — above the CRLB floor, supporting the hypothesis that ORTHOGONALIZED basis (not random Gaussian) is the discriminator.
- The proposed falsification at d=16384 + n=8 seeds would put the CRLB floor at 0.055 (3x headroom over the +0.15 chain-grade bar) and would resolve the question.

The prompt's hypothesized mechanism for failure ("substrate's HD vector basis has REAL underlying structure; random Gaussian readouts collapse to the same latent subspace") is **plausible and worth keeping as a hypothesis**, but it has not been falsified or confirmed by data. If the actual full-scale run lands and Fisher really does collapse to chance with cv=8, then Angle A's three revival approaches (PCA-derived bases from substrate data; cluster-aware bases; supervised basis training) become live cell proposals. Until then, they're speculation.

**What I'm willing to atomize today on Angle A:**
- The CRLB headroom calculation (drill 3 of the 5x drill) — already supported by analytical math.
- The Drill-4 falsification cell spec — already self-consistent and falsifiable.
- A bias-13/15 flag: if the substrate's effective dimension is << nominal d, the CRLB floor calculation is optimistic; this should be checked empirically via singular-value decomposition of the bundle covariance before claiming the proposed cell would resolve the question.

**What I'm NOT willing to atomize today on Angle A:** any conclusion of the form "Fisher fusion fails entirely on substrate" — because the data to support that doesn't exist on disk.

---

## ANGLE B — Is TRACE the substrate-native importance primitive?

This is where I want to take an honest position. The prompt frames TRACE = 0.998 as proof TRACE "is the answer." The 5x drill is more careful and I'll restate it:

**TRACE genuinely IS a high-signal importance lever in our cells (+0.30 to +0.42 across all seeds across V3-V6).** The 5x drill confirmed this from raw per-seed metrics — this is verified, not phantom.

**BUT TRACE operates via a SIDE-CHANNEL, not the bundle-readout pathway:**
- TRACE counts explicit retrieval events per atom — it's a per-atom counter that bypasses the HD bundle's interference-limited readout.
- This is NOT a "substrate-native" primitive in the deep sense; it's an instrumentation channel that records what was queried.
- It has bounded utility: TRACE can rank "what was retrieved how often" but cannot answer "what WOULD have been useful if queried" or "what should I attend to next given context."

**The "TRACE is the answer" framing is partially correct and partially overclaim:**
- ✓ For importance ranking of already-retrieved content (memory consolidation tagging, replay weighting) — TRACE is chain-grade adequate TODAY. Atomize this.
- ✗ For attention/saliency over UNRETRIEVED content, multi-channel readout is still required, still untested at proper regime, still possibly chain-grade-eligible.
- ✗ For "compositional importance" over derived atoms — TRACE has nothing to say.

**This is a TWO-CHANNEL story, not a single-primitive story.** The honest atomization is:

**META_FINDING_substrate_importance_two_channel_2026-06-27:**
> Substrate importance signaling has two pathways: (1) TRACE side-channel (explicit retrieval-event counting; chain-grade-adequate for ranking already-retrieved content; sel +0.30-0.42 robustly across regimes); (2) bundle-readout multi-channel (Fisher / PCA-basis over k independent readouts; CRLB-limited; UNTESTED at adequate d/k/n regime; falsification cell specified in 5x drill is the resolver). The two channels are not interchangeable: TRACE handles "what was queried"; bundle-readout would handle "what should be queried." Recommendation: ship TRACE NOW for downstream importance ranking in KG-consolidation / replay-weighting cells; DO NOT close the bundle-readout direction until the proposed falsification cell actually lands.

---

## What I AM atomizing today

1. **META_FINDING_substrate_importance_two_channel_2026-06-27** (atom body above) — covers what's actually known + clearly demarcates what's NOT known + recommends shipping TRACE for downstream USE while keeping the multi-channel question open.

2. **DISCIPLINE_PHANTOM_VERDICT_REFUSAL_pattern_recurrence_2026-06-27** — flag the recurring pattern (3+ instances now: batch7 morning + the multi-channel ceiling framing today + the broader Fix #28 backlog). The pattern is: upstream session reports verdict numbers + downstream session asked to atomize without verifying disk. Recommended hard rule: every meta-finding atomization request from Director's own framing must include a path to a metrics.json that exists on disk + the verdict field from that file. If those two pieces aren't present, refuse and respond with this rule.

3. **CELL_QUEUE_BUMP_falsification_d16384_n8seeds** — bump priority of the actual falsification cell (5x drill Drill 4 spec). It's <1 CPU-hr; high information value; the missing data IS the question. Route to hdi_exp_dev for full dispatch (NOT smoke; smoke already SELFTEST_OK'd).

---

## What I am NOT atomizing today

- "TRACE is the answer; close multi-readout-Fisher direction" — over-claim; premature; closes a chain-grade-eligible direction on phantom data.
- "Multi-readout Fisher fails entirely on substrate" — unverifiable from existing data; the proposed mechanism (Gaussian readouts collapse to substrate's latent subspace) is plausible but untested.
- "Importance ceiling is closed" — wrong direction; ceiling is bounded but not resolved.

---

## Recommended Director actions

1. **Dispatch the actual d=16384/n=8 full cell** via hdi_exp_dev (full, not smoke) — it's been queued for hours; this is the missing piece.
2. **Atomize the two-channel meta-finding** above (NOT the phantom-data version).
3. **Add a hard rule to the SESSION-START checklist:** before any atomization request, verify the metrics.json file exists on disk and quote the verdict field directly. This is the Fix #28 strengthening that the morning's batch7 refusal also implies.
4. **When the actual full data lands** (whether tomorrow morning or after another spawn cycle), come back to this question with real per-arm metrics. The 5x drill's Drill-4 discriminator (FALSIFIED if PCA-basis mean ≥ +0.12, cv < 0.25) is the operational answer; report from the file, don't extrapolate from the framing.

---

## Closing — honest scientific position

The importance-ceiling drilling arc IS near its natural end, but NOT because TRACE solved it. It's near its end because:

(a) the question has been operationalized to a single bounded cell (Drill 4 spec, <1 CPU-hr);
(b) the chain-grade-adequate-TODAY answer for downstream USE is TRACE side-channel; ship that;
(c) the chain-grade-EXTENSION question (does multi-readout bundle-readout clear +0.12 at d=16384/k=8/n=8?) is one experiment away from resolution.

What's NOT honest is closing the arc by atomizing a phantom-data meta-finding. The discipline learned from morning's batch7 refusal applies here exactly: verify the referent, refuse to atomize on numbers that can't be reproduced from disk, and let the actual experiment land before declaring a winner.

---

**Words: ~1180. Slightly over the ~800 target, because the refusal-with-positive-recommendations structure needs to clearly demarcate verified-vs-phantom. The "atomize TRACE-is-the-answer cleanly" path is the wrong move; the "atomize two-channel-with-pending-falsification" path is honest and forward-moving.**
