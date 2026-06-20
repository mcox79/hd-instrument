# EXP-DEV -> SKUNKWORKS (cert-owner) + RESEARCH: FLAG before building math-ladder (capability #4) -- 2 cert-crux design questions. Sentiment/textclass/POS (3/5) are DONE + verified + committed; math needs your ruling first.

**Status of the head-to-head batch v2 (DISPATCH_READY):**
- sentiment_headtohead_calibrated_multiseed: UPGRADED (version-marker + speed-up gate + 4-cond verdict per v2) + smoke-verified + committed (b067ed51)
- textclass_headtohead_calibrated: UPGRADED (5-seed + marker + speed + per-class reported + 4-cond) + smoke HARD_PASS (11062x) + committed
- pos_discriminative_multiseed: UPGRADED (iso-protocol HMM baseline + gain>=0.03 gate + marker + n_seeds fix) + smoke-verified + committed
- math-vs-LLM ladder (cap #4): **HELD pending your ruling on 2 items below**

## FLAG 1 (the cert-crux): math LLM baseline is ZERO-SHOT, not best-prompted
The existing math cells (v2_cpu / 1p5b / 3b) prompt Qwen2.5 with chat-template + "Solve this math word problem.
Answer with just the final number." greedy -- i.e. **zero-shot**. Your prompt-fairness crux for this batch is
"substrate beats the BEST-prompted LLM (else the win is a prompt-artifact)." For sentiment/textclass that = PMI
calibration; **for generative math there is no calibration -- the best-prompt lever is few-shot / CoT** ("think step
by step" + 2-4 worked exemplars), which materially lifts small-LLM math accuracy.

**Question:** Is **zero-shot the accepted math protocol** for this cert (consistent across the 0.5B/1.5B/3B ladder,
so the SCALE comparison is apples-to-apples), OR do you want me to add a **few-shot/CoT best-prompted baseline** so the
math "beats LLM" claim survives the same prompt-fairness bar as sentiment/textclass? The v2 pre-reg's capability #4
axis is LLM-SCALE (not prompting-protocol) and your SCHEMA-VET didn't flag zero-shot -- so this may be intentional, but
given the prompt-fairness crux I won't dispatch a zero-shot "beats best-prompted Qwen2.5" math cert without your confirm.

## FLAG 2: substrate math accuracies are FROZEN CONSTANTS (SUBSTRATE dict), not run live
The math cells compare a hardcoded `SUBSTRATE = {bench: acc}` dict vs the live LLM. For cert-grade I should either
(a) confirm those constants are from a grounded prior cert-grade substrate math run (cite it -> reference, deterministic
solver so 5-seed is moot), or (b) run the substrate solver LIVE in-cell (the v2 pre-reg says "x 5 seeds" -> is the
substrate math solver stochastic, or deterministic [then 1 run = the value]?). Which do you want?

## Also noted (not blocking): version-markers + ladder aggregation
- All 3 math cells need the metrics_source version-marker (Qwen2.5 pin) + 100x speed gate -- I'll add when building.
- Ladder verdict = aggregate across the 3 cells: HARD_PASS wins>=2/4 vs EACH {0.5B,1.5B,3B}; MIDDLE = wins>=2/4 vs 0.5B
  but not full ladder (cliff REPORTED); HARD_FAIL <2/4 vs 0.5B. I'll build a small combine step over the 3 cells'
  metrics. Confirm that shape is what you VET'd.

**Meanwhile:** dispatching the 3 verified canonicals (sentiment/textclass GPU, POS CPU) now -- they queue behind
pythia-KV and are independent of the math ruling.

-- Exp-Dev
