# CHANGE REQUEST — substrate-trained mini language model experiment

**From:** Research session
**To:** Orchestrator + Testbed
**Date:** 2026-06-03
**Subject:** Design-change request for the substrate-trained mini language model experiment (anchor name `phase_d_tier6_full_pipeline_4_core_char_lm_v1`)

---

## What this experiment is (plain language)

A 4-layer character-level mini language model trained ENTIRELY via substrate operations — no gradient descent at any layer. Tests whether substrate can serve as the entire training mechanism for an LM, not just augment it. Runs on cloud A100 in ~2-4 hours at ~$5-10 cost. Was the most aggressive swing in the recently-authorized 3-experiment batch.

## Status check requested

Before applying changes below, please verify:

- [ ] Has orchestrator ingested the experiment into `notes/experiment_queue_pending.md` yet?
- [ ] Has testbed started engineering scaffolding for it?
- [ ] Is it currently dispatched / running on a cloud instance?
- [ ] Has it completed?

## Instructions

### IF NOT YET dispatched / engineered / running → apply these design changes

Cascade research drill landed 2026-06-03 with finding: the anti-Hebbian / bipartite-contrastive primitive used in this experiment has P=0.55 of becoming the load-bearing failure mode at LM-class scale. Three failure modes ranked by severity:

1. **Shared capacity budget** — anti-Hebbian patterns consume the same α_c=0.138 capacity as positive patterns. With equal positive/negative split, capacity cliff hits at half the corpus size.
2. **Bipartite correlation breakdown** — for correlated natural-language inputs (ρ ~0.3-0.6), α_c shrinks 30-50% and negative-phase activations become biased estimators.
3. **Gradient degeneration** — soft/continuous activations make the rule converge to gradient-descent equivalent (Melchior & Wiskott 2024). Binary activations safe; continuous risky.

**Defensive design changes (best lit-mitigation per cascade drill):**

- **A. Sparse coding regime** (Tsodyks-Sejnowski class): activity level ~5% per pattern (not dense). Gives ~25× α_c lift over dense coding. Strongest published mitigation.
- **B. Binary activations only** (no continuous-valued activations anywhere in the loop). Avoids gradient-degeneration failure mode entirely.
- **C. Explicit α-budget accounting** in training loop: (positive pattern count P + anti-Hebbian pattern count Q) / dimension N must satisfy < α_c_sparse (~3.45 with sparse coding). Prevents the shared-capacity-budget cliff.
- **D. NEW pre-flight gate experiment**: dispatch a cheap CPU ablation BEFORE this experiment hits the cloud. Anchor name `phase_d_pre_ablation_antihebbian_failure_signatures_v1_n128`. 2-layer N=128 substrate-native loop at <2h CPU, $0 cost. Tests three watchlist signatures: (i) BPC plateau within 100-500 steps with positive-only control improving, (ii) ||W||_2 exponential growth within 200 steps, (iii) retrieval accuracy on held-out probe drops toward chance. **Gate rule:** if any signature triggers → ABORT main experiment cloud dispatch; pivot to defensive variant or hybrid path. If no signatures trigger → main experiment dispatches as updated.
- **E. Auto-abort mid-run** on any watchlist signature trigger during the main experiment (cost protection — saves cloud spend if anti-Hebbian collapses mid-run).

Cost ceiling unchanged ($5-10 for main experiment + $0 for pre-flight). Engineering effort increases ~1 day to wire sparse coding + binary-only enforcement + pre-flight ablation.

### IF ALREADY dispatched / engineered / running → do this instead

Do not apply the above changes mid-flight. Instead:

1. Let the originally-authorized experiment complete as designed (the version without sparse coding + binary-only enforcement + pre-flight gate).
2. Report verdict back via standard verdict_handler.
3. **If verdict = HARD-PASS:** great — the defensive changes weren't needed; substrate-trained mini LM works as designed.
4. **If verdict = MIDDLE or HARD-FAIL with anti-Hebbian-specific failure signature visible in metrics:** the defensive design becomes the obvious follow-up variant; file it as a new experiment (`phase_d_tier6_full_pipeline_4_core_char_lm_v2_defensive`) for next-cycle dispatch.
5. **Either way:** do NOT cancel the original mid-run.

### IF ALREADY completed → just confirm verdict status; no action needed

Verdict landed → defensive variant or follow-up scoping at next research cycle.

## Why this change request

I shipped the original experiment design after the substrate-as-full-LLM-training research drill landed. Then a follow-up cascade drill on the riskiest primitive (anti-Hebbian at transformer scale) landed AFTER I'd already shipped the original design. The cascade drill's findings materially change the risk profile (P=0.22 without mitigation; P=0.38 with sparse coding) and identify a $0 pre-flight that can save the cloud spend if the failure mode triggers. Worth folding in IF the experiment hasn't been picked up yet.

## What I am NOT changing

The other two experiments in the same authorized batch:
- **substrate-curriculum-learning experiment** (anchor `substrate_curriculum_learning_small_lm_v1`) — unchanged
- **substrate-pre-loaded ICL experiment** (anchor `tier2_substrate_preloaded_icl_pythia410m_v1`) — unchanged

Only the substrate-trained mini language model experiment has the cascade-drill-driven design change.

## Discipline declarations

- Per `feedback_change_request_protocol`: this note is the standard change-request format, not a silent edit-in-place
- Per `feedback_plain_language_experiment_tracking`: experiment described in plain language; technical anchor name as backup label only
- Per `feedback_obey_user_pause_explicitly`: original experiment was user-authorized; changes are risk-mitigations within same cost envelope, not scope expansion

---

**END.**

**Orchestrator + Testbed:** please status-check first, then apply or defer per the conditional instructions above. Reply via standard verdict_handler / status_log channels so research session sees the disposition.
