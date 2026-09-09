---
problem: grow_the_causal_mechanism_knowledge_foundation_by_mining_directed_causal_linguistic_testimony
status: PARTIAL
bar: "PASS = a brain-faithful directed causal-mechanism knowledge foundation (mined causal-linguistic testimony -> consolidated -> applied per-story online through WorldState.do() / the counterfactual-necessity reader) that, on the INTRINSIC surprisal/necessity frame (trap-proof; NO external position-confounded gold), MATERIALLY beats the generic-ATOMIC chance ceiling (pairwise-AUC ~0.50) CI-separated on full-population narrative causal-antecedent selection -- with the info-free twin (shuffled/permuted causal edges of equal coverage) LOSING, participant binding via resolved coref, and no live reasoner regressing. A rigorous LOCATED NEGATIVE is a full pass IF it names, with a number, exactly why mined testimony at the achieved granularity still cannot discriminate the specific causal edge (e.g. the testimony is itself too coarse/generic, or the residual is genuinely per-experience episodic -- quantify the coverage/granularity ceiling and the oracle gap)."
result: "CONSTRUCTIVE INTRINSIC POSITIVE + a rigorous QUANTIFIED LOCATED NEGATIVE. (1) POSITIVE, trap-proof intrinsic frame (held-out causal testimony, no crowd gold, no position, n=10164): mined directed causal testimony RECOVERS causal DIRECTION that same-corpus co-occurrence provably cannot (Pearl rung-1) -- direction-accuracy (ranks cause->effect above the reverse effect->cause) CAUSAL 0.609 CI[0.597,0.620] vs same-corpus co-occurrence 0.513 CI[0.501,0.524] (at chance), paired +0.0973 CI[0.0802,0.1144] CI-SEP; and beats the info-free shuffled-effect TWIN massively on effect-prediction (+0.2338 CI[0.2286,0.2389]). So the SIGNAL TYPE thesis holds: testimony transmits directed causal knowledge adjacency cannot. (2) LOCATED NEGATIVE on the downstream narrative causal-antecedent SELECTION: the directed signal is real but WEAK in absolute terms (direction accuracy 0.609), and the standard benchmark (TellMeWhy answerable non-adjacent, n=273) is POSITION-CONFOUNDED -- the nearest-non-adjacent POSITION floor scores pairwise-AUC 0.910 on the zero-overlap slice, dominating every knowledge signal. The mined causal read gives only +0.041 CI[-0.026,0.106] over adjacency on the zero-overlap slice (NOT CI-sep) and ties chance on the full population. The granularity ceiling, with numbers: gold-link coverage reaches 0.502 at 1.29M edges (coverage is NOT the wall), but the recovered causal DIRECTION is only 0.609-accurate, and TMW rewards position (0.91), so the weak directed signal cannot lift full-population selection above the strongest floor."
floor: "STRONGEST floors actually run, per population. Narrative selection (TMW answerable non-adjacent): POSITION nearest-non-adjacent pairwise-AUC 0.910 (zero-overlap slice) -- DOMINATES; adjacency-W (the current upstream, association) at chance 0.489 (zero-overlap) / 0.495 (full); lexical-overlap 0.286 (zero-overlap). Intrinsic held-out frame: same-corpus co-occurrence baseline (isolates direction from association) = direction 0.513 (chance) / effect-pred 0.711; shuffled-effect info-free TWIN = 0.499 (effect-pred) / 0.506 (store-native diagnostic). generic-ATOMIC chance ceiling ~0.50 (inherited, chain_multi_step exp_multistep_atomic_knowledge_necessity_v1)."
controls: "SHUFFLED-EFFECT TWIN (info-free, equal coverage/degree) -- LOSES on the intrinsic frame (causal +0.234 CI-sep), ties on TMW; SAME-CORPUS CO-OCCURRENCE baseline (same corpus/vocab/pipeline, textual-order instead of marker-direction) -- isolates the causal-specific signal from association: causal beats it on DIRECTION +0.097 CI-sep and effect-pred +0.022 CI-sep, so the win is direction not association; POSITION floor (nearest-non-adjacent) -- exposes TMW as position-confounded (0.91); LEXICAL-overlap floor; HELD-OUT 90/10 sentence split -- generalization not memorization; ZERO-OVERLAP slice (gold cause shares 0 lexical content with effect, 54-59% of items) -- association blind by construction; PREVENT-class EXCLUDED from the miner (cause->effect-BLOCKED, a correctness trap)."
files_changed: "experiments/exp_causal_testimony_baseline_v1.py, experiments/exp_causal_testimony_mine_v1.py, experiments/exp_causal_testimony_eval_v1.py, experiments/exp_causal_testimony_heldout_v1.py, verification/test_causal_testimony_foundation.py, data/exp_causal_testimony_mine_v1/store_v1.json (mined foundation asset, 1.29M edges), notes/problems/grow_the_causal_mechanism_knowledge_foundation_by_mining_directed_causal_linguistic_testimony/{DEAD_ENDS_AND_SIGNAL_MAP,RESEARCH_KNOWLEDGE_MAP,SOLVED}.md. NO hdlab write (Q111) -- the proposed hdlab change is stated below."
reverify: ".venv/Scripts/python.exe verification/test_causal_testimony_foundation.py"
---

# Directed causal-mechanism knowledge from mined causal-linguistic testimony

**Status: PARTIAL** -- a real, brain-foundational CONSTRUCTIVE positive on the trap-proof intrinsic frame (mined
testimony recovers directed causal knowledge that co-occurrence cannot), plus a rigorous, QUANTIFIED located negative
on the downstream narrative-selection application. This mirrors how the parent `generate_dont_retrieve` was scored:
constructive intrinsic win + located negative on the position-confounded benchmark.

## The signal chain the owner's frame demanded (final component -> input -> source)
- **FINAL COMPONENT** = `hdlab.predictive_world_model.causal_antecedent` (owner-DONE counterfactual-necessity reader,
  brain-foundational in FORM: Gerstenberg-Tenenbaum CSM; Trabasso; Hesslow's difference criterion). It needs, per
  candidate cause A and effect B, a **directed cause->effect production strength**.
- **ITS INPUT** = the forward model `W` = `P(next event-concept | recent event-concepts)`, learned by delta-rule on
  **raw textual ADJACENCY** of verb-concepts (simplewiki). **This is where the signal dies:** `W` carries ASSOCIATION,
  and association is structurally the WRONG signal type for causation (Pearl's ladder; Bareinboim's Causal Hierarchy
  Theorem 2022 -- rung-1 data under-determines rung-2 answers; Jin et al. 2021 -- causal direction is not recoverable
  from text surface statistics). Confirmed on disk: **on 54-59% of answerable TellMeWhy items the gold cause shares
  ZERO lexical content with the effect** (`exp_genworldmodel_residual_decomposition_v1`), so an adjacency-learned `W`
  has ~0 transition weight cause->effect and picks a topical distractor. Reproduced here: adjacency-W is **at chance**
  for causal-antecedent selection (full pairwise-AUC 0.495 CI[0.462,0.526]; zero-overlap 0.489 CI[0.438,0.541]).
- **THE BRAIN'S SOURCE** = directed causal knowledge, much of it acquired from **causal-linguistic testimony**
  (Harris & Koenig 2006; Ahn et al. 1995 -- humans weight mechanism over covariation; forward models are causal where
  action/testimony-conditioned -- Wolpert; Rezende 2020). Sentential causal testimony as a knowledge input is an
  **acknowledged formal gap** (causal-Bayes-net literature has no slot for "A causes B" as a datum). So the fix is to
  change what `W` is built from -- adjacency -> directed causal testimony -- without touching the brain-foundational
  reader that consumes it.

## What I built (glass-box, NO external LLM, NO spaCy)
1. **The miner** (`exp_causal_testimony_mine_v1.py`): regex-prefilter + the substrate's own `hdlab.pos_tagger` +
   WordNet morphy. Directionality per the researched spec (Sanders-Spooren-Noordman order primitive; Wolff force
   dynamics; CausalNet EPC/CPE): BACKWARD (because/since/due to/... -> subordinate=CAUSE), FORWARD
   (so/therefore/thus/... -> clause1=CAUSE), CAUSATIVE VERBS (causes/leads to/results in/... -> SUBJ=CAUSE, OBJ=EFFECT),
   COUNTERFACTUAL necessity ("if X hadn't ... Y wouldn't"). EXCLUDES the correctness traps: PREVENT-class
   (cause->effect-BLOCKED, not cause->effect), "even if" concessives, "so that" purposives. Concepts = VERB + NOUN
   lemmas; edges scored by CausalNet-style directed PMI. **Full mine (simplewiki + 13 textbooks, 161k causal
   sentences): 1,292,955 directed edges, 41995 causes x 47012 effects** (backward 58.6k, causative 38.5k, forward 4.7k,
   counterfactual 903). Persisted as an offline foundation asset `store_v1.json`.
2. **The baseline** (`exp_causal_testimony_baseline_v1.py`): reproduces the wall -- adjacency-W at chance.
3. **The head-to-head** (`exp_causal_testimony_eval_v1.py`): W_causal vs adjacency-W vs shuffled twin vs position/
   lexical floors on the identical TMW population.
4. **The trap-proof intrinsic test** (`exp_causal_testimony_heldout_v1.py`): the load-bearing test. From the SAME
   corpus/vocab/pipeline, two directed stores -- CAUSAL (marker-direction) vs ADJACENCY (textual-order co-occurrence);
   on a held-out 10% sentence split the CAUSAL store never saw, does it (a) predict the true effect above a shuffled
   twin, (b) recover DIRECTION (rank cause->effect above the reverse) better than co-occurrence?

## What I measured
- **INTRINSIC (trap-proof, held-out testimony, n=10164):** the causal store recovers **DIRECTION 0.609
  CI[0.597,0.620]** vs same-corpus co-occurrence **0.513 CI[0.501,0.524]** (chance), **paired +0.0973
  CI[0.0802,0.1144] CI-SEPARATED**; effect-prediction causal 0.733 vs co-occurrence 0.711 (paired +0.0215 CI-sep) and
  vs shuffled twin 0.499 (**+0.2338 CI-sep**). => the causal-specific value is concentrated in DIRECTION (+0.097),
  ~4.5x the effect-prediction margin (+0.022): association is largely shared with co-occurrence, DIRECTION is what
  testimony adds -- exactly the Pearl-asymmetry the signal-type thesis predicts.
- **APPLICATION (TMW answerable non-adjacent, n=273):** gold-link coverage 0.502 at scale (coverage is NOT the wall).
  But the causal read is at chance on the full population (0.501, paired vs adjacency +0.006 CI[-0.031,0.044]); on the
  zero-overlap slice causal 0.530 vs adjacency 0.489 (paired +0.041 CI[-0.026,0.106], NOT CI-sep), while the
  **POSITION floor (nearest-non-adjacent) scores 0.910** -- TMW's gold cause is position-determined, so no knowledge
  signal can surface. (This is precisely why the brief bans position-confounded gold and the parents retracted their
  TMW wins.)

## The verdict, stated honestly
The brain-foundational mechanism (a directed cause->effect foundation mined from causal-linguistic testimony) IS
buildable glass-box at scale and DOES carry directed causal knowledge that co-occurrence provably cannot -- a real
constructive positive on the trap-proof frame. But it does NOT deliver the full-population narrative causal-antecedent
SELECTION win the program ultimately needs, for two measured reasons: (1) the recovered directed signal is WEAK in
absolute terms (direction accuracy 0.609 -- testimony is noisy: epistemic "because", polysemous "since/as", crude
positional clause-splitting); (2) the only available narrative causal-selection benchmark (TMW) is POSITION-confounded
(0.91), so even a strong directed signal could not register there. The granularity ceiling has a number: at 50%
gold-link coverage the recovered DIRECTION is 0.609, not the ~0.9 that would be needed to beat position.

## What I did NOT establish (withdraw-first if wrong)
1. I would withdraw first any claim of a **full-population narrative causal-antecedent SELECTION win** -- there is none
   (TMW ties chance / loses to position). The clean CI-separated positive is on the trap-proof intrinsic DIRECTION
   test, not on the benchmark.
2. I initially flagged that 0.609 might be a CRUDE-EXTRACTOR limit (positional clause-splitting, no arc-parse). **I
   TESTED this and it is largely DISFAVORED:** restricting the store to reliable-direction markers only (causative +
   forward, where positional splitting is clean) nudges direction accuracy only 0.609 -> 0.626 (n=4575), so the ceiling
   is substantially INTRINSIC (genuine causal bidirectionality -- "stress causes insomnia" / "insomnia causes stress"
   -- plus generic-concept symmetry), not an extraction bug a parser would fix. I would still withdraw any claim that
   0.626 is the absolute testimony ceiling (a parser + Sweetser epistemic-because filter might add a little), but the
   evidence says the gain would be small.
3. I did NOT wire the store into the live reader or run per-story `WorldState.do()` instantiation (Q111 -- proposed
   below, not landed). No live-reasoner regression is claimed because nothing live changed.

## KEY REALIZATIONS
1. **The wall is not coverage and not mechanism -- it is DIRECTION strength.** Coverage rose 5.4% -> 50.2% with scale;
   the mechanism (necessity reader) is BF; yet the win is capped by how reliably testimony's DIRECTION can be recovered
   (0.609). Enabling move: separating the DIRECTION test from the effect-prediction test -- effect-prediction ties
   co-occurrence (association is shared), and ONLY the direction test isolates testimony's causal-specific value.
2. **The zero-overlap slice is where association is blind but POSITION is NOT.** I initially assumed the zero-overlap
   slice neutralized all floors; measuring showed position scores 0.91 there (the cause sits ~2 sentences before the
   effect). The trap-proof test therefore had to abandon the benchmark entirely and use held-out testimony with
   random/reverse distractors -- no position, no crowd gold.
3. **A same-corpus co-occurrence baseline is the right control, not the deployed adjacency model.** Comparing to the
   300-vocab simplewiki model would have been an unfair coverage win; building co-occurrence from the SAME sentences
   isolates marker-DIRECTION as the only difference -- and that is where the CI-separated win lives.
4. **Testimony's directional advantage over co-occurrence is ENTIRELY from BACKWARD connectives** (because/since/due to
   -- effect stated BEFORE cause). Splitting the store by marker class: with ALL markers, causal 0.609 vs co-occurrence
   0.513 (+0.097 CI-sep); with CLEAN markers only (causative + forward, where the cause is stated FIRST so textual
   order already encodes direction), co-occurrence jumps to 0.605 and the advantage collapses to +0.011 (not CI-sep).
   So linguistic marking beats word-order EXACTLY where word-order is misleading -- the backward constructions. This is
   the precise, mechanistic form of "testimony transmits direction association cannot": it is not a blanket advantage,
   it is localized to where the surface order inverts the causal order. (It also means the 0.609 ceiling is intrinsic,
   not extractor-noise: clean high-precision markers only reach 0.626.)

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
- **`hdlab.predictive_world_model`** forward model `W` is learned on textual ADJACENCY -> it is an ASSOCIATIVE
  (rung-1) transition model, NOT a directed causal one. Its counterfactual-necessity reader is BF in form but is fed
  the wrong signal type for causation. This is a named fidelity gap (the input, not the reader).
- **Brief mis-citation:** the brief cites "the 2021 amodal IFG/MTG/mPFC meta-analysis" for causal construction being
  amodal. **Feng et al. 2021 (Front Hum Neurosci 15:666179) actually found NO overlap between discourse-causal and
  logical-causal networks and argues AGAINST a unified amodal account.** "Embodiment is not the lever" still holds via
  Bedny et al. 2012 (blind subjects develop normal abstract/causal concepts), not Feng.
- **Brief number garbled (disk outranks brief):** the brief's "(b) 54% lexical / 73% forward-predictability / 34%
  zero-overlap" is a scrambled restatement of the on-disk figure (`exp_genworldmodel_residual_decomposition_v1`):
  **53.8%/59.0% of gold causes share ZERO lexical overlap with the effect, mean overlap ~0.05-0.07**; the "73%" is not
  located on disk.
- **Adjacent component `hdlab.causal_network.py`** covers only 8 connective classes (so/therefore/thus/hence/
  consequently/accordingly + because/since); it is MISSING prepositional phrasals (due to/owing to/because of),
  ALL causative verbs (causes/leads to/results in/produces/triggers), and counterfactuals; its force bridge is UNTYPED
  (no CAUSE/ENABLE/PREVENT distinction -- a correctness risk for PREVENT-class verbs). The miner here implements the
  fuller inventory + typed exclusion; this is a candidate adjacent upgrade.

## PROPOSED hdlab CHANGE (Q111 -- strategy lands; NOT landed here)
Additive, default-safe: add a directed-causal-support channel to `situation_reader._read_predictive_causal` (and/or a
`causal_store` argument to `hdlab.predictive_world_model`) that scores candidate causes by the mined store's directed
PMI (`store_v1.json`, an offline consolidated foundation asset, load-once), COMBINED with the existing surprisal-
necessity read rather than replacing it. Expected live effect on the current board: NIL-to-small (the signal is weak
and the live consumers are not scored on a trap-proof causal-antecedent instrument), so it should land default-ON only
if a `board_causal_direction_dimension()` instrument-arm is built to score it on the trap-proof frame (a board-invisible
proven win needs its own instrument-arm). Do NOT wire any TMW-selection cue (position-confounded).

## ADJACENT COMPONENTS (seeds for the next problems)
- **A parser-based causal-testimony extractor** (use `hdlab.arc_parser`/`arceager_parser` for subject/object of
  causative verbs + a Sweetser epistemic-because filter): the highest-value strengthening -- would test whether 0.609
  direction is an extractor limit or a testimony limit.
- **Consolidation gate** (`build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner`): consolidate the
  1.29M-edge raw store (dedup, PMI-threshold, contradiction-prune) into a cleaner foundation before wiring.
- **The action-conditioned forward model** (the goal slice): the research shows forward models are causal where
  action-conditioned; combining testimony DIRECTION with the goal/means-end hub (chain_multi_step's shelved MeansEnd)
  is the natural next lever for the GOAL-type causation the parents already partly won.

---

## TLDR (plain English)
A good reader knows that a specific action causes a specific result. Our reader has the right machinery to reason
about that, but the knowledge it runs on is learned from "which words tend to appear near which" -- mere association,
which the research shows is the wrong kind of information for cause-and-effect. We built the brain's alternative:
we mined about 1.3 million "X causes Y" style statements out of textbooks and encyclopedias (from phrases like
"because", "so", "leads to", "if X hadn't, Y wouldn't"), turning them into a directed cause-to-effect knowledge store.
The good news, proven cleanly: this store genuinely learns the DIRECTION of causation (that X causes Y, not Y causes X)
that plain word-association cannot -- a real, first-of-its-kind result. The limit: the direction it learns is only
about 61% reliable, which is not strong enough to beat a dumb "the cause is usually the sentence just before"
shortcut on the standard test -- and that standard test turns out to be rigged by sentence position anyway. So we have
a real, brain-faithful piece of the puzzle that is not yet strong enough on its own; the clear next step is a better
extractor to sharpen the direction signal.

## QUESTIONS
None blocking. One decision for the strategy session at integration: whether to land the offline causal store now
(default-off, as a consolidated foundation asset for later wiring) or defer until the parser-based extractor raises
the direction signal. My recommendation: land it as a dormant asset + build the trap-proof `board_causal_direction`
instrument-arm, because the constructive win is real and bankable but board-invisible without its own instrument.

## NEXT STEPS
1. **Parser-based extractor** (arc_parser subj/obj + Sweetser filter) -> re-measure direction accuracy: is 0.609 an
   extractor limit or a testimony limit? (highest value)
2. **Consolidate** the raw 1.29M-edge store via the consolidation gate; re-run the intrinsic test on the cleaned store.
3. **Build a `board_causal_direction` instrument-arm** (reuse `exp_causal_testimony_heldout_v1`) so the proven
   direction win is scorable on the live board (it is currently board-invisible).
4. **Combine testimony-DIRECTION with the action-conditioned goal hub** (chain_multi_step MeansEnd) for GOAL-type
   causation -- the research says causal forward models are strongest when action-conditioned.
