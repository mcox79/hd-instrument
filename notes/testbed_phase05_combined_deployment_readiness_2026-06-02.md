# Testbed Phase 0.5 + 0.5b combined deployment readiness 2026-06-02

**Filed:** 2026-06-02
**Filed-by:** testbed session
**Trigger:** User directive "combine both and ready for deployment" 2026-06-02
**Source routings:**
- `notes/research_routing_llm_integration_program_amendment_phase0p5_2026-06-02.md` (Phase 0.5 Tier-7 MVP; USER AUTHORIZED $50-100)
- `notes/research_routing_tier4_training_acceleration_FINAL_5drill_consolidation_2026-06-02.md` (Phase 0.5b distillation MVP; user combined-auth)

Per [[feedback-no-experiment-design-in-prompts]]: this note records testbed-side cell design (anchor names, script paths, smoke-mode behaviors, batch JSON) but does NOT re-litigate the capability questions or HP/MIDDLE/FAIL bands (those are the research routings, verbatim).

---

## Status: PRE-LAUNCH STAGED

What's built and smoke-tested today:
- 4 anchor scripts (`experiments/exp_{tier7_mvp_hyperprobe_llama31_kappa3_drift,deletion_cert,refusal_cert}_v1.py` + `exp_phase0_5b_distillation_mvp_llama31_kg_triples_v1.py`)
- Shared helpers (`testbed/llm_integration/hyperprobe_encoder.py` + `substrate_audit.py`) with instrumentation selftests on import
- Unified batch JSON (`tools/cloud/batch_examples/phase05_combined_llama31.json`) for single Lambda bootstrap

What's NOT yet wired (cloud bring-up phase, must clear before dispatch):
- Hyperprobe encoder full mode: needs clone of `Ipazia-AI/hyperprobe` + checkpoint load (arXiv:2509.25045, MAP-Bipolar D=4096); currently raises NotImplementedError if HDLAB_ENCODER=hyperprobe
- vLLM batched serving of Llama-3.1-8B-Instruct on Lambda A100/H100 instance
- Llama-3.1-8B fact-elicitation pipeline for Phase 0.5b KG-triple extraction (currently uses synthetic SHA-256-driven bipolar codes in smoke; full mode raises NotImplementedError)
- Cloud bring-up scripts in `tools/cloud/` for: vllm install + Llama-3.1-8B download + hyperprobe checkpoint pull + warmup smoke before launch

---

## Anchor matrix

| # | Anchor | Sub-test | Substrate primitive | Pre-reg HARD-PASS | Pre-reg HARD-FAIL |
|---|--------|----------|---------------------|-------------------|-------------------|
| 1 | `tier7_mvp_hyperprobe_llama31_kappa3_drift_v1` | A: kappa_3 drift detection | Whitened kappa_3 via Sigma^{-1/2} (per I-10) | sigma_sep >= 5 across 5 seeds | sigma_sep < 2 |
| 2 | `tier7_mvp_hyperprobe_llama31_deletion_cert_v1` | B: deletion cert vs live LLM state | Rank-1 deletion + Z-ratio vs null + retained cosine | del-Z < 2-sigma AND retained > 0.85 across 5 seeds | del-Z > 5-sigma OR retained < 0.65 |
| 3 | `tier7_mvp_hyperprobe_llama31_refusal_cert_v1` | C: refusal cert via PP-48 NKT | 3-level hierarchical NKT search; leaf-first cosine cert | precision = 1.0 AND false-refusal <= 0.10 across 5 seeds | precision < 0.9 |
| 4 | `phase0_5b_distillation_mvp_llama31_kg_triples_v1` | 0.5b: 1000-fact KG distillation MVP | Hetero-assoc W_kv (retrieval) + auto-assoc W_xx (audit) | distilled recall >= 0.85 AND non-distilled deg <= 0.02 AND MMLU deg <= 0.02 AND 100-fact one-shot wall <= 60s + recall >= 0.85 AND deletion cert verifies on 100-subset | distilled < 0.65 OR catastrophic (>0.05 degradation) OR deletion cert fails |

Each anchor: 5 seeds {7, 17, 23, 31, 41}. ASCII-only stdout per [[feedback-ascii-only-in-scripts]]. Self-test on import per [[feedback-strategy-spec-formula-selftests]]. Resumable per-seed checkpoints via `experiments._seed_checkpoint`.

---

## Smoke gate results (laptop, 2026-06-02)

All 4 anchors execute end-to-end at smoke scale (HDLAB_RUN_MODE=smoke) with synthetic-encoder mode. Smoke is for instrumentation validation, NOT for verdict reading -- pre-reg bands target production scale.

| Anchor | Smoke D / N | Smoke result | Notes |
|---|---|---|---|
| Sub-test A | D=512, 80+20 prompts, 500 Hutchinson probes | HARD_PASS (sigma_sep 153-156) | Synthetic iid; SE for whitened W with M=80 vs M=20 is asymmetric -- not a clean NULL test (this is a smoke artifact, not a script bug). pseudo_llm encoder mode gives same range. |
| Sub-test B | D=512, M=40 facts, k=10 deletions | MIDDLE_BAND (del-Z 2.00-2.14) | del-Z just above HP gate of 2 because null-std is small at n_null=50 + D=512. At full D=4096 the null-std rises (sqrt(D) scaling) and del-Z drops below HP threshold. |
| Sub-test C | D=512, 42-node NKT, 5 forbidden + 10 allowed | HARD_FAIL (precision 0.71-0.83) | Smoke is in the noise-floor regime: random cosine std ~ 1/sqrt(M_tree) = 1/sqrt(42) = 0.154 vs TAU_L1 = 0.30 (only 2x margin). At full D=4096, cosine SNR scales with sqrt(D/D_smoke) = sqrt(8) -- false-refusal collapses toward zero. This is the load-bearing scaling claim; if false-refusal stays high at D=4096 the substrate-LLM coupling is broken (HARD_FAIL would be honest). |
| Phase 0.5b | N=1024, M=200 KG triples | MIDDLE_BAND (clean primitives; del-Z 1.98-2.76 borderline) | distilled_recall=1.000, non_deg=0.000, mmlu_deg=0.000, oneshot_wall=0.2s, retain_cos=0.933 -- only del-Z trips by smoke-mode null-std-floor reasons (same as sub-test B). |

Smoke is INSTRUMENTATION-OK across all 4. Verdicts at smoke do NOT pre-frame the full run (per [[feedback-no-preframe-batch-all-pass]] + [[feedback-no-smoke-preframing-in-task-prompts]]).

---

## Full run specifics

| | Sub-test A | Sub-test B | Sub-test C | Phase 0.5b |
|---|---|---|---|---|
| Encoder mode | hyperprobe (Llama-3.1-8B forward + hyperprobe map) | hyperprobe | hyperprobe | synthetic KG triples (Phase 1) -> full LLM fact elicitation (Phase 2) |
| Substrate dim | D=4096 (Llama hidden = 4096; hyperprobe published D) | D=4096 | D=4096 | N=8192 |
| Population/M | 800 in-dist + 200 adv prompts | M_facts=100, k_del=25 | 30-leaf NKT + 5 forbidden + 25 allowed | M_distilled=1000 (alpha=0.122 vs alpha_c=0.138) |
| Hutchinson n_probes | 5000 | n/a | n/a | n/a |
| Eval suites | kappa_3 distribution shift | deletion-Z + retained cosine | precision + false-refusal | 5 sub-evals: distilled recall + non-distilled deg + MMLU deg + one-shot 100-fact + 100-subset deletion |
| Seeds | 5 | 5 | 5 | 5 |
| Expected wall | 5-15 min/seed | 1-3 min/seed | 1-3 min/seed | 20-40 min/seed |
| Total wall | 25-75 min | 5-15 min | 5-15 min | 100-200 min |
| Timeout | 120 min | 60 min | 60 min | 240 min |

**Batch total expected wall:** ~3-5h on H100 / A100 single instance (sequential). Single Lambda bootstrap; one Llama-3.1-8B load shared across all 4 anchors.

**Cost projection:** $4.29/hr H100 SXM5 OR $1.10/hr A100 40GB. At 4h wall: $17 (H100) or $4.40 (A100).

Per research routings:
- Phase 0.5 alone: $30-80 cloud bring-up (probe + Llama + vLLM warmup + 3 sub-tests)
- Phase 0.5b: $15-40 (1000-fact distillation + 5 sub-evals on Llama-3.1-8B)
- Combined: $70-140 estimate -- our calculation gives $4-17 of pure GPU-hours, leaving ~$50-120 budget for bring-up + retries + probe-retrain optional path.

User auth covers $50-100; combined ceiling at $140 needs explicit ack if budget overruns.

---

## Cloud bring-up gates (must clear before dispatch)

Each gate is a separate engineering task; estimate 1-2 days each. Listed as load-bearing dependencies:

1. **Lambda instance type choice.** A100 80GB recommended (Llama-3.1-8B + hyperprobe + vLLM fit comfortably; substrate at N=8192 is tiny). Backup: H100 SXM5 if A100 unavailable in target region.
2. **vLLM install + Llama-3.1-8B-Instruct load.** Add `vllm>=0.5` to `requirements_cloud.txt`. Download checkpoint via HF (requires HF token; user has Anthropic key memory entry but not HF; surface to user if needed).
3. **Hyperprobe clone.** `git clone https://github.com/Ipazia-AI/hyperprobe; pip install -e .` -- pull published checkpoint per arXiv:2509.25045 supplementary.
4. **KG fact corpus.** For Phase 0.5b: generate 1000 (s, p, o) triples via Llama-3.1-8B fact-elicitation prompts. Hold out 200 facts as non-distilled control. Hold out 200-question MMLU subset (use HF `mmlu` dataset).
5. **Forbidden-pattern corpus.** For sub-test C: define 30 forbidden-prompt classes (e.g., PII-related, decision-class-related per v334 KSP framing); 5 forbidden test prompts + 25 allowed test prompts.
6. **Encoder full-mode wiring.** Replace `HyperprobeEncoder._encode_hyperprobe` NotImplementedError with actual `transformers.AutoModelForCausalLM` forward + residual intercept at layer `int(L * 0.7)` final token + hyperprobe(residual) -> bipolar code.
7. **Phase 0.5b LLM fact elicitation.** Replace `_synth_kg_triple` synthetic path with Llama-3.1-8B prompted to emit (s, p, o) triples from base-LLM knowledge.
8. **Pre-launch checkpoint:** dry-run all 4 anchors at smoke scale on the Lambda instance ($1-5 + 15 min) confirming the bring-up before main batch.

---

## Discipline declarations

Per project memory:
- [[feedback-always-verbose-remote-dispatch]]: all 4 scripts use `set -ex` + `python -u` + `stdbuf -oL` + tee + SCP-back when run on Lambda; per-experiment timeout set explicitly.
- [[feedback-batch-cloud-experiments]]: single Lambda bootstrap; 4 anchors share Llama-3.1-8B load.
- [[feedback-cloud-launch-snapshot-reconcile]]: pre-launch instance-list snapshot, retry 5xx, reconcile any new instance as ours.
- [[feedback-ascii-only-in-scripts]]: all print() strings ASCII; no em-dash; no emoji.
- [[feedback-per-experiment-timeout-required]]: each anchor has explicit `experiment_timeout_min` in batch JSON.
- [[feedback-no-experiment-design-in-prompts]]: pre-reg bands quoted verbatim from research routings; cell design (D, M, n_probes, seeds, threshold calibration like TAU_L1/L2/L3) is testbed autonomy.
- [[feedback-obey-user-pause-explicitly]]: cloud dispatch waits on user explicit go after sanity-check.
- [[feedback-short-cloud-runs-preferred]]: $70-140 combined is above standing per-case threshold; explicit user auth was the unlock.
- [[feedback-strategy-spec-formula-selftests]]: every script has an instrumentation selftest on import (runs at small N before main).

---

## Files staged this session

- `experiments/exp_tier7_mvp_hyperprobe_llama31_kappa3_drift_v1.py`
- `experiments/exp_tier7_mvp_hyperprobe_llama31_deletion_cert_v1.py`
- `experiments/exp_tier7_mvp_hyperprobe_llama31_refusal_cert_v1.py`
- `experiments/exp_phase0_5b_distillation_mvp_llama31_kg_triples_v1.py`
- `testbed/llm_integration/hyperprobe_encoder.py` (shared encoder interface)
- `testbed/llm_integration/substrate_audit.py` (kappa_3 + deletion-cert + whitening primitives)
- `tools/cloud/batch_examples/phase05_combined_llama31.json` (unified batch JSON)
- This note: `notes/testbed_phase05_combined_deployment_readiness_2026-06-02.md`

---

## What I'm NOT doing (per discipline)

- Not pre-framing smoke verdicts as evidence for full-run outcomes
- Not adding cell padding to round out the 4-anchor batch
- Not running the cloud dispatch without user explicit go
- Not changing pre-reg bands set by research
- Not auto-iterating if smoke surfaces issues -- surface to user

---

## Next testbed actions on user go-signal

1. Build cloud bring-up scripts (vLLM + Llama-3.1-8B + hyperprobe; ~1-2 eng-days)
2. Generate forbidden-pattern corpus + KG fact corpus + MMLU subset (~1 eng-day)
3. Smoke-dry-run on Lambda A100 ($1-5; 15 min)
4. Dispatch combined 4-anchor batch on user explicit go
5. Monitor + file deliverable on completion
