# Research -> Exp-Dev: EX-CONCEPT-1 -- substrate PERFORMANCE improvement variants (not just baselines)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-05 ~12:00
**Subject:** Adding stronger baselines just exposes the gap. We need to ACTIVELY IMPROVE substrate performance on next-concept-ID prediction. 6 architectural improvement variants to test.

---

## The actual problem

Substrate at 0.613 vs predicted strong baselines (trigram 0.65-0.70; small neural 0.70-0.85; Pythia-direct 0.75-0.90+):

Substrate is likely LOSING to fair baselines. Adding the baselines just makes this visible. Honest framing matters but we also need to MAKE SUBSTRATE BETTER.

## Why might substrate be under-performing?

Honest diagnostics:

1. **Context too narrow.** Current substrate uses position-binding + STDP which captures ~2-3 token context. Modern LLMs use 50-500 token context per prediction. Substrate isn't using its multi-hop capability for sequence prediction.

2. **No cleanup augmentation.** NEW EXP 3 showed cleanup-augmented retrieval gives 6x depth boost. Is this being applied to next-concept prediction?

3. **Concept granularity (V_c=256) too coarse.** Larger V_c captures more distinctions. Pythia-160M's vocabulary is 50000 tokens; we're compressing to 256 concepts. May lose too much.

4. **Single-pass retrieval, not iterated.** Substrate has Mode 4 NC1 iterated retrieval validated for reasoning. Is this being used for prediction?

5. **No hierarchical aggregation for prediction.** NEW EXP 5 showed D=20 hierarchical capacity scaling. Is multi-substrate prediction being tried?

6. **No Mode 5 controller.** Mode 5 + Architecture A was the production architecture. Is the controller doing anything for prediction or just substrate alone?

7. **cf-RPE drilled as inverted-for-generative.** Maybe this needs revisiting. The drill said cf-RPE inverts for generative, but with cleanup + iterated retrieval, the situation may differ.

## 6 substrate improvement variants to test

These are architectural improvements applied to next-concept-ID prediction. Test each individually then combine the winners.

### Variant 1: Extended context (5-10 token position-binding)

Instead of bigram-class context (2-3 tokens), use 5-10 prior tokens via position-binding stack.

```
substrate retrieval query = bind(c_{t-1}, pos_1) + bind(c_{t-2}, pos_2) + ... + bind(c_{t-K}, pos_K)
```

Test at K=2, 5, 10. Hypothesis: longer context improves prediction.

### Variant 2: Cleanup-augmented prediction (per NEW EXP 3 HP)

Apply cleanup-augmented retrieval at every prediction step:
- Each retrieval result snapped to nearest stored concept
- Reduces noise; sharpens prediction

NEW EXP 3 showed 6x depth boost; should give some prediction-quality lift too.

### Variant 3: Larger concept vocabulary (V_c sweep)

Sweep V_c in {256, 1024, 5000, 10000}:
- Larger V_c = more concept granularity
- Tradeoff: substrate capacity load increases (more codebook entries)
- Hypothesis: V_c=1024 or 5000 hits sweet spot

### Variant 4: Iterated retrieval prediction (Mode 4 NC1)

Instead of single-pass W*q for prediction, do iterated:
```
For i = 1..K:
  q_{i+1} = cleanup(W * q_i)
Final prediction = top-K of q_K
```

This uses substrate's Mode 4 capability for prediction. Hypothesis: iteration sharpens prediction over single-pass.

### Variant 5: Hierarchical multi-substrate prediction (NEW EXP 5 architecture)

D parallel substrates each train on the same concept-ID corpus:
- Different domain decomposition (e.g., topic-clustered training subsets)
- Ensemble prediction via weighted aggregation
- D = 4, 8, 16

Hypothesis: ensemble exceeds single-substrate (validated for capacity; should help prediction too).

### Variant 6: Mode 5 controller + isolated substrate (Architecture A applied)

W_s storage substrate stores concept-ID transitions. W_r isolated substrate handles iterated factor decomposition (for higher-order patterns).

Controller routes:
- For "easy" predictions (high-confidence single retrieval): W_s only
- For "hard" predictions (low confidence): controller queries W_r for factor decomposition + iterates

Mode 5 Architecture A was 4.5x improvement on shared-W; should help here too.

---

## Combined test: substrate-MAX configuration

After single-variant ablations, build the COMBINED variant with all winning improvements:

```
Substrate-MAX config:
- Extended K-token position-binding (best K from Variant 1)
- Cleanup augmentation at all retrieval steps (Variant 2)
- V_c at sweet spot (Variant 3)
- Mode 4 iterated retrieval at inference (Variant 4)
- Hierarchical D substrates (Variant 5)
- Mode 5 controller routing (Variant 6)
```

This is "substrate doing its best at next-concept-ID prediction with all architectural advantages applied."

### Pre-reg

Single-variant pre-reg: each variant adds >= 0.05 absolute accuracy over baseline substrate (0.613)

Substrate-MAX combined pre-reg:
- **HARD-PASS:** substrate-MAX accuracy >= 0.85 (matches or beats Pythia-direct prediction)
- **MIDDLE:** substrate-MAX accuracy in [0.70, 0.85] (matches small-neural baseline; loses to Pythia-direct)
- **HARD-FAIL:** substrate-MAX accuracy < 0.70 (substrate architecturally not suited for next-concept-ID prediction at this scale; revisit substrate's value proposition for this task)

### Honest interpretation

If substrate-MAX HP: substrate IS good at next-concept-ID prediction; EX-CONCEPT-1 reframes as legitimate flagship anchor.

If substrate-MAX MIDDLE: substrate matches neural-class for this task; not "vastly better" but competitive. Other architectural advantages (audit, continual learning, multi-hop reasoning) are still the real wins.

If substrate-MAX HF: substrate is NOT good at next-concept-ID prediction even with all architectural advantages. **This is important honest data.** Substrate's value proposition needs to be specifically about the tasks where it DOES win (multi-hop reasoning, audit, continual learning, cross-session memory), not language modeling. Adjust audacious vision accordingly.

---

## Cost + wall

- All 6 variants individually: ~$0 CPU + ~1 day eng each = ~6 days
- Substrate-MAX combined: ~$0 + ~2-3 days eng
- Total: ~$0 + ~1-2 weeks engineering
- Per user "engineering time is not a constraint": run all variants

---

## Why this matters strategically

User correctly pushed back: "we need to improve our performance, no?" Yes.

The audacious vision of "Wikipedia substrate cognitive core that beats frontier LLMs" requires substrate to be competitive at LANGUAGE MODELING tasks (next-token prediction is foundational), not just at the architectural-advantage tasks (multi-hop reasoning, audit, continual learning).

If substrate cannot match small neural baselines at next-concept-ID prediction even with all its primitives applied: the Wikipedia substrate cognitive-core story has a real gap that needs to be addressed honestly.

Either:
(a) Substrate-MAX is competitive -> we proceed with audacious vision
(b) Substrate-MAX is not competitive -> we narrow the vision honestly to "substrate for architectural advantages (audit, continual learning, multi-hop reasoning) coupled to LLM for language modeling" -- which is STILL valuable but smaller than "Wikipedia substrate replaces LLM."

Either outcome is informative. We need this data.

---

## Sequencing

**Priority:**
1. **Substrate-MAX combined first** (highest information value; if it beats Pythia-direct, we know substrate has the architecture to win at this task)
2. **If substrate-MAX HF or MIDDLE:** ablations to find which variants help (Variants 1-6 individually)
3. **If substrate-MAX HP:** ablations to see which are critical (could simplify the architecture)

Substrate-MAX combined is the fastest path to honest empirical answer.

---

## What this doesn't change

The OTHER 10 flagship empirical anchors stand. They are validated against fair baselines for the tasks they test:
- Multi-hop reasoning (vs LLM CoT failure beyond K=4-7)
- Audit-preserving reasoning (vs LLM no-audit baseline)
- Continual learning (vs LLM fine-tune; no catastrophic forgetting)
- Cross-session persistence (vs LLM zero memory across sessions)
- Multi-hop KG traversal (CCC-1-EXTRA 0.987/0.895/1.000 vs frequency baseline)
- Tier 4 substitution (vs unchanged Pythia; ppl_ratio 1.06x)
- Tier 6 Phase D (vs gradient baseline; 2x speedup CPU)

These wins are architectural and don't depend on next-concept-ID prediction quality.

EX-CONCEPT-1 reframing affects ONE claim, not the broader story.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per user 2026-06-05 ~11:45: don't just measure honestly; ACTIVELY IMPROVE substrate performance
- Per [[feedback-pressure-test-negative-findings]]: substrate-MAX HF would be honest negative requiring vision narrowing
- Per [[feedback-no-padding-experiments]]: each variant tests distinct architectural improvement hypothesis
- ASCII-only

---

**END.**

**Exp-Dev:** stronger baselines + 6 substrate performance improvement variants + substrate-MAX combined. Sequence: substrate-MAX first (fastest to honest answer); then ablations. Total ~1-2 weeks eng + $0.

**User:** correctly pushed -- we need substrate to actually be good at this, not just measured against fair baselines. Substrate-MAX configuration is the honest test of substrate's architectural ceiling for next-concept-ID prediction. If HP: vision holds. If HF: vision narrows to architectural-advantage tasks (which are still valuable; just smaller than "substrate replaces LLM at language modeling").

**Standing for: substrate-MAX verdict + CCC-1 REVISED-v2 critical path build.**
