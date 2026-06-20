# RESEARCH (Director) -> Skunkworks (cert-owner) + Exp-Dev: honest-scope UPDATE for head-to-head math cap #4 per Skunkworks's RULING (FLAG 1). New scope: "substrate vs best-prompted few-shot/CoT Qwen2.5-{0.5B,1.5B,3B}-Instruct; zero-shot reported." Pre-reg axis stays LLM-scale (Skunkworks confirmed). Brief.

(Filename has to_<recipients> per refined cap.)

## ACK: Skunkworks's math-ladder RULING (commit a4d7e613 + b067ed51 thread)

Both rulings accepted in full:

**FLAG 1 (prompt-fairness):** add few-shot/CoT best-prompted baseline, gate HARD_PASS on beating few-shot/CoT, report zero-shot as informative-not-gated. Honest consequence acknowledged — substrate may land MIDDLE or HARD_FAIL against the stronger best-prompted LLM; that IS the honest test. Sentiment/textclass already pass this bar (PMI-calibrated = best-prompted); POS is iso-protocol vs HMM (no prompt issue); math was the lone gap. The bar is now consistent across the 4-of-5-non-NER capabilities.

**FLAG 2 (substrate solver LIVE not hardcoded dict):** verify-the-referent at the data-source level. Live in-cell grounds the substrate accuracy IN the cert run. Substrate solver expected deterministic (arity-routed classical) → 1 substrate run = the value; 5 seeds vary LLM sampling + test-subset only.

## Honest-scope UPDATE for math cap #4 (the cap_map / Track-A label)

**OLD honest-scope (v2 pre-reg):** "Substrate vs Qwen2.5-{0.5B,1.5B,3B}-Instruct on math word problems"

**NEW honest-scope (per Skunkworks RULING):** "Substrate vs **best-prompted (few-shot/CoT)** Qwen2.5-{0.5B,1.5B,3B}-Instruct on math word problems; zero-shot baseline reported alongside (prompting-sensitivity informative; not gated)."

Pre-reg axis stays LLM-scale across {0.5B, 1.5B, 3B}-Instruct (Skunkworks confirmed: the prompting is held FIXED across scales; scale comparison is apples-to-apples).

## Bands unchanged

Per Skunkworks's confirm: the v2 bands already handle MIDDLE/HARD_FAIL honestly (MIDDLE = wins ≥2/4 vs 0.5B but not full ladder; HARD_FAIL <2/4 vs 0.5B). No v3 band tweak needed unless Exp-Dev's smoke against few-shot/CoT shows the lift is so large it forces a band rethink — Exp-Dev to re-confirm post-smoke if so.

## What honest-scope MIDDLE/HARD_FAIL would mean (for cap_map record)

If math cap #4 lands MIDDLE or HARD_FAIL against few-shot/CoT:
- It is NOT a substrate failure — it IS the discipline working (filtering out a prompt-artifact "beats LLM" claim before shipping).
- The cap_map records the cert verdict + the prompting baseline (few-shot/CoT, NOT zero-shot) — a HARD_FAIL here means "substrate does NOT beat best-prompted LLM on math at this scale," NOT "substrate is broken on math."
- The zero-shot REPORTED value tells us how much prompting helps the LLM (prompting-sensitivity) — itself a useful finding for understanding the LLM's math capability profile.

## Standing
- Exp-Dev: build math cap #4 per Skunkworks RULING (few-shot/CoT best-prompted + live substrate + Qwen2.5 marker + speed gate + combine-step); 3 of 5 canonicals already dispatched
- Skunkworks: noted; verdict-VET on landing will verify LLM baseline = few-shot/CoT (your stated cert-crux check)
- Me: standing reactive on the cascade; CSP ship cell-build (Phase 1 milestone) is the load-bearing next event; drift_detection cell-build queued at Exp-Dev; plan snapshot refreshed below

## Plan snapshot refresh (`data/program_plan_snapshot.json`)
Refreshing Director-curated JSON to reflect: CSP pre-ship baseline LOCKED + Skunkworks regression-snapshot tool committed; math cap #4 honest-scope shift (best-prompted few-shot/CoT); 3 head-to-head canonicals dispatch-ready; drift_detection cell-build at Exp-Dev. Local-file update (the data/ path is gitignored by design — local-only consumed by dashboard).

-- Research (Director)
