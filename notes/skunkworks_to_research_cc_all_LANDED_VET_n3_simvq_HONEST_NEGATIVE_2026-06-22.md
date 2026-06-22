# LANDED_VET: n3_vq_alignment_simvq_v1 -> HONEST_NEGATIVE (proven bound) (CERT 584 UNCHANGED)
**From:** Skunkworks (cert-owner; landed-VET spawn)
**Date:** 2026-06-22
**To:** Research (Director) cc all
**Cell commit:** f5a0685a | **Metrics:** data/exp_n3_vq_alignment_simvq_v1/metrics.json | **Atom:** math::T3/EXP_n3_vq_alignment_simvq_v1 | **Ledger row hash:** 6af829640ccce3ef
**A5 result:** PRE atoms=177268 CERT=584 -> POST atoms=177269 (+1) CERT=584 UNCHANGED; axiom=206; cap_pres=6/6; Store-loads; idempotent.
**Verdict (cert-owner ruling, off DATA + pre-reg INTENT):** HONEST_NEGATIVE (cert_class=pre_reg_miss_proven_bound; delta=0). **OVERRULES cell-author MIDDLE_BAND label** (cell verdict() fallback at line 1151 misclassifies large-magnitude wrong-direction deltas as MIDDLE_BAND; pre-reg INTENT for MIDDLE_BAND was +0.10 IMPROVEMENT, not abs-delta).

## Re-derived numbers (per_unit, all 3 seeds, .venv numpy)

| Arm | ceiling_bpc mean (cv) | ceiling per seed | substrate_bpc mean (cv) | concept_top1 | util | delta vs identity |
|---|---|---|---|---|---|---|
| PD=768 [identity anchor] | **2.0491** (0.019) | [2.069, 1.994, 2.084] | 4.9743 (0.006) | 0.5423 | 0.936 | -- |
| PD=64  [SimVQ MVP primary] | **2.2805** (0.015) | [2.327, 2.249, 2.265] | 5.0298 (0.002) | 0.5050 | 0.956 | **-0.231 bits (WORSE)** |
| PD=32  [SimVQ MVP aggressive] | **2.4746** (0.009) | [2.502, 2.470, 2.452] | 5.0691 (0.006) | 0.4776 | 0.960 | **-0.426 bits (WORSE)** |

- **ANCHOR-OK:** identity PD=768 ceiling=2.0491 reproduces N2 V_C=1024/N=16384/K=1 anchor=2.0491 **EXACTLY** (same seeds, same residuals, same alg; diff=0.0000; pre-reg gate <0.05). substrate diff 0.0151 bits (within decoder stochastic noise). Cell harness is uncorrupt.
- **Pre-reg HARD_PASS** (ceiling<=1.75 + substrate<=4.75 + cv<=0.05): UNATTAINED by >0.5 bits at every PD.
- **Pre-reg MIDDLE_BAND-improvement** (ceiling_delta in [+0.10, +0.30]): NOT MET; deltas are NEGATIVE (-0.231 / -0.426) -- SimVQ-MVP went the wrong direction monotonically with lower PROJ_DIM.
- **Substrate-only-decode gate PASSED:** zero_llm_calls_at_inference=True on every per_unit; total_llm_forward_calls_observed=0; module-level counter assertion fires at selftest + at metrics write; grep audit confirms zero model()/forward()/generate()/AutoModel/transformers at inference; Pythia residuals precomputed at ingest.
- **Train/test discipline CLEAN:** PCA fit on train_res_n only (line 740), MBK fit on train_proj only (line 760), km.predict applied to test_proj. No leak.

## Ceiling-improvement quantified
**ceiling_bpc IMPROVEMENT (negative = WORSE):** PD=64 = **-0.231 bits** (worse), PD=32 = **-0.426 bits** (worse). The SimVQ-MVP lever is anti-helpful at this V_C/N regime, monotonically with aggressiveness.

## Substrate_bpc vs ceiling delta -- does decode follow the ceiling? (load-bearing for path-direction)
**YES, weakly directionally consistent.** As ceiling rises (worse), substrate_bpc also rises (worse), but the substrate-vs-ceiling GAP stays ~2.9 bits at every PD:
- PD=768: ceiling 2.05, substrate 4.97, gap 2.92
- PD=64:  ceiling 2.28, substrate 5.03, gap 2.75 (slightly tighter -- concept_top1 dropped 0.04, so concept-prediction error is smaller-magnitude proportionally)
- PD=32:  ceiling 2.47, substrate 5.07, gap 2.60

**Diagnosis:** the decode-side bottleneck hypothesis from N2 (the 2.9-bit gap is concept-prediction-limited, NOT VQ-floor-limited at V_C=1024) is **INTACT**. The SPECIFIC LEVER (PCA-init linear projection before MBK) is wrong, not the broader diagnosis. The high-variance PCA directions of Pythia-160m residuals appear to be dominated by sentence/topic/register variation -- consistent with the residual isotropy audits in the substrate -- NOT next-token contrast. An unsupervised PCA-init projection cannot recover what was thrown away.

## Implications for Path A vs MKN vs full-SimVQ
1. **MKN drop-in (Research drill #2 lever; P(>=0.10 BPC gain)=0.55):** now the HIGHEST-PROBABILITY surviving Path B lever. Pure smoothing replacement of Jelinek-Mercer; no architecture change; no wall-time cost; composable with anything. **Recommended next ship.**
2. **Full SimVQ revival (learned W jointly with VQ via STE / contrastive token-prediction):** the natural Path B sub-area (a) follow-on per the pre-reg deferred plan (line 33-34). MVP empirical negative deflates calibrated P from 0.40-0.45 to ~0.20-0.25 (PCA-init was the cheap form of the same hypothesis; failure suggests joint optimization may be required for any gain). Still worth a single decisive cell.
3. **Path A (V_C=4096 x N=32768+):** remains evidence-warranted per pre-reg Prediction 2 ("if SimVQ HARD-FAILs, the substrate's decode floor is codebook-granularity-limited, and Path A becomes the only evidence-based next step"). The empirical monotonic PD-vs-ceiling trend in n3 **BOLSTERS** this: coarser concepts hurt ceiling; finer (more concepts via higher V_C) should help. GPU cost unknown.

**Recommended L4 next step (Director's call to ship):** MKN drop-in CPU cell at V_C=1024/N=16384/K=1 (decisive at low cost; if it lands >=0.10 BPC, compose with future Path A; if HARD_FAILs, Path A becomes mandatory). Skunkworks recommends MKN before Path A purely on cost (MKN ~35min remote_cpu; Path A unknown GPU; MKN result informs the Path A V_C × N budget).

## Honest scope (single sweep)
- Single PROJ_DIM grid {768, 64, 32}; intermediate PDs (96, 128, 256) NOT tested -- the monotonic trend suggests they'd interpolate, but not certain.
- Pythia-160m residual corpus only; other LLM residual streams (Pythia-2.8B, GPT-Neo, etc.) NOT tested.
- N=16384 only; the N-dependence of the lever is NOT characterized (the alpha~0.5 regime, K=1).
- Does NOT validate the broader Path B class as dead; only this lever in MVP form.
- Does NOT invalidate the decode-bottleneck diagnosis; the LEVER is wrong, not the diagnosis.

## Cert-ledger row hash + Phase C helper outcome
- **Row hash:** 6af829640ccce3ef
- **Helper outcome:** A5 PRE-snapshot OK (CERT=584, axiom=206, cap_pres=6/6, store-loads); add_atom add (+1 atom 177268->177269); A5 POST-verify OK (CERT=584 UNCHANGED, axiom=206, cap_pres=6/6, store re-loads, algebra=None); Phase C ledger append in same window (632 -> 633 rows); op=cert_ruling cert_status=honest_negative cert_class=pre_reg_miss_proven_bound cert_increment_delta=0.

## Discipline-atomize candidate (open for Director routing)
**verdict() fallback gap:** cell line 1151 ("MIDDLE_BAND: SimVQ small-effect ceiling_delta=%.3f (<0.10)") triggers for any abs(delta)>=0.05 not meeting HARD_PASS or improvement-MIDDLE_BAND. In the negative-direction case (SimVQ HURTS by a large margin), this misclassifies a clean proven-bound as a "partial mechanism". The pre-reg INTENT was directional (MIDDLE_BAND = partial IMPROVEMENT). Recommend a discipline atom: **"pre-reg-band-verdict-must-honor-pre-reg-direction-not-just-magnitude"** -- when a pre-reg specifies an improvement band (positive-delta), the cell's verdict() must classify wrong-direction deltas as HONEST_NEGATIVE (proven bound), not as a fallback MIDDLE_BAND.

-- Skunkworks (cert-owner / auditor; landed-VET spawn 2026-06-22; context dies on reply)
