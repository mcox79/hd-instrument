# Research -> Exp-Dev: EX-CONCEPT-1 REAL -- honesty correction + stronger baselines required

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator + User
**Date:** 2026-06-05 ~11:30
**Subject:** User flagged that bigram-Markov is a weak baseline; substrate beating it by 1.03x doesn't prove much. Correcting the HP framing + routing stronger-baselines rerun.

---

## The honest read

EX-CONCEPT-1 REAL pre-reg HP label says "substrate beats baselines on real Pythia data." What was actually tested:

- substrate_top1 = 0.613
- unigram = 0.037 (substrate 16.3x; trivial baseline; meaningless)
- bigram-Markov = 0.596 (substrate 1.03x; weak baseline; marginal beat)

**Bigram-Markov is the 1980s pre-neural-LM baseline.** Tiny RNNs from the 1990s beat it. Modern transformers crush it. Substrate beating bigram-Markov by 3% is NOT a strong empirical result for "substrate is a good language model" -- it's table-stakes for any sequence model.

The HP label overstates what was tested. This is a process lesson worth recording.

## What this result DOES show

The honest claim is narrower than the HP label suggests:

- Substrate CAN learn from REAL Pythia-derived concept-ID sequences (not just synthetic proxy)
- Substrate captures SOMETHING beyond pure 1-step Markov transitions (probably 2-3 token context from position-binding + STDP)
- The pipeline works: Pythia residual extraction -> VQ -> substrate Hebbian writes -> retrieval-based next-concept prediction

This is a useful sanity check. It's NOT proof that substrate is GOOD at next-concept-ID prediction.

## What this result does NOT show

The HP label implied substrate is good at this task. What we don't know:

- How substrate compares to **trigram-Markov** (uses 2-item context)
- How substrate compares to a **small neural baseline** (e.g., 1-layer transformer trained on the concept-ID sequences)
- How substrate compares to **Pythia-160M's own next-token-then-VQ predictions** (which is essentially "the LLM we extracted from, doing the same task directly")

Likely ranking (predicted, not measured):
1. Pythia-160M direct: ~0.75-0.90 (it generated the concepts; should be best at predicting them)
2. Small neural on concept-IDs: ~0.70-0.85
3. Trigram-Markov: ~0.65-0.70
4. Substrate: 0.613
5. Bigram-Markov: 0.596

If this ranking holds, substrate may actually be LOSING to all the stronger baselines. The "HP" label is therefore misleading.

## Routing stronger-baselines rerun

### Cell EX-CONCEPT-1-REAL-STRONG-BASELINES-v1

**Anchor:** `ex_concept_1_real_strong_baselines_rerun_v1`

### Add to existing benchmark the following baselines:

**Baseline 1: Trigram-Markov**
- P(next_concept | prev_2_concepts)
- Same training data; same eval set
- Trivial to implement (~30 min eng)

**Baseline 2: Small neural baseline (1-layer transformer)**
- 1-layer transformer with 64 hidden dim trained on concept-ID sequences
- Same training data (VQ Pythia concepts); same eval set
- Train to convergence on the sequence prediction task
- Cost: ~$0 CPU; ~30-60 min wall

**Baseline 3: Pythia-160M direct prediction**
- Run Pythia-160M on the same input sequences
- VQ Pythia's predicted next-token activations
- Measure concept-ID prediction accuracy
- This is the strongest baseline because Pythia "knows" what concepts it would predict next
- Cost: ~$0 (Pythia inference; same hardware)

### Comparison

Report substrate_top1 vs ALL baselines, not just unigram + bigram. Honest verdict:

- If substrate beats all 3 strong baselines: substrate is genuinely good at this task (would be a real HP)
- If substrate beats trigram + small-neural but loses to Pythia-direct: substrate matches LLM-class neural performance (still meaningful)
- If substrate beats trigram but loses to small-neural + Pythia-direct: substrate is mid-tier; not strong at sequence prediction
- If substrate loses to trigram: substrate's context handling is weaker than expected (architectural concern)

### Revised pre-reg

- **HARD-PASS:** substrate >= 0.95x of strongest baseline (Pythia-direct or small-neural, whichever wins)
- **MIDDLE:** substrate beats trigram-Markov but loses to neural baselines
- **HARD-FAIL:** substrate loses to trigram-Markov (architectural concern; substrate context-handling is weaker than 2-step Markov)

### Cost + wall

- $0 (all baselines + substrate rerun on same hardware as original)
- ~1-2 hours wall
- Engineering: ~2-3 hours (baseline implementations)

### Strategic

This is the honest version of EX-CONCEPT-1 REAL. If substrate places competitively in this honest comparison: real win. If it places mid-tier: still useful data but doesn't support audacious claims about "substrate beats LLMs at language modeling."

---

## Process lesson going forward

**HP labels must compare against STRONG baselines, not strawmen.**

For future cells:
1. Pre-reg explicit baselines: at minimum, the best published baseline on the task
2. If pre-reg uses weak baselines (unigram/bigram on text), add stronger baselines in the same run
3. HP threshold should be against the strongest baseline, not the weakest

This applies to all current and future cells. The user's catch on EX-CONCEPT-1 should propagate: every HP we claim should be honest about what was beaten.

Examples for current/upcoming cells:

- **CCC-1 REVISED-v2:** baseline is Pythia-160M direct on the same benchmarks. STRONG baseline by construction. Pre-reg thresholds (substrate >= 1.5x / 2.0x / etc. Pythia) are honest.
- **Tier 4 substrate-attention in Pythia:** baseline is Pythia-160M unchanged. STRONG baseline. ppl_ratio 1.06x is honest (substrate is 6% WORSE than original Pythia at that layer; the framing is honest because we said "training-stable" not "beats").
- **CONT-LRN-1:** baseline is Pythia-160M fine-tune. STRONG baseline. 27x speedup is honest at Pythia scale.
- **EX-CONCEPT-1:** baseline was bigram-Markov. WEAK baseline. HP overstated. Correcting via this routing.

Going forward: every cell pre-reg should pass the "would this comparison convince a skeptical reviewer" sniff test.

---

## What this doesn't change

The substrate-cognitive-core narrative DOES NOT depend on substrate winning at next-concept-ID prediction in isolation. The architectural wins are real and validated:

- Multi-hop reasoning (K=12 single, K=24 hierarchical) -- HP empirical
- Audit-preserving reasoning (B6 x SQ2 HP) -- HP empirical
- Continual learning at 27x with NO catastrophic forgetting (CONT-LRN-1) -- HP empirical
- Substrate-attention training-stable in real Pythia (Tier 4) -- HP empirical
- Real KG multi-hop traversal (CCC-1-EXTRA: 0.987/0.895/1.000) -- HP empirical (this is genuinely strong vs the relevant baseline)
- Cross-session persistence (architectural; trivially beats LLMs at zero context)

These wins remain. EX-CONCEPT-1 reframing just acknowledges we don't have a strong claim about next-token prediction quality specifically.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per user catch 2026-06-05 ~11:15: HP labels must compare against STRONG baselines, not strawmen
- Per [[feedback-no-smoke]]: honest about what was tested vs claimed
- Per [[feedback-no-padding-experiments]]: rerun corrects the existing cell; not adding scope
- ASCII-only

PROT-018: `_strong_baselines_rerun_v1` suffix; explicit baseline names per pre-reg

---

**END.**

**Exp-Dev:** EX-CONCEPT-1 REAL HP was over-stated -- substrate beating bigram-Markov by 1.03x doesn't prove the architectural claim. Adding 3 stronger baselines (trigram-Markov + small neural + Pythia-direct) to the existing cell. Same training data; same eval set; just compare against fair benchmarks. Honest verdict determines whether substrate is genuinely good at next-concept-ID prediction or just mid-tier.

This is process correction, not a setback. The catch came from the user; we should be the team that does this internally going forward.

**Standing for: stronger-baselines rerun verdict + CCC-1 REVISED-v2 critical path build.**

**User:** EX-CONCEPT-1 framing corrected on scorecard. Stronger-baselines rerun routed. Process lesson recorded: HP labels need strong baselines, not strawmen. This is the team practice going forward.
