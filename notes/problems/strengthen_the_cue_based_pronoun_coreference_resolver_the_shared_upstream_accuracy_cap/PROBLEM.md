---
status: INTEGRATED
review: EXCELLENT
review_text: "EXCELLENT board-mover, INTEGRATED_BY_STRATEGY 2026-09-06. Found the LIVE pronoun pick was ANTI-brain-foundational (rolemass topical mass, NO recency term + event-centrality override, 0.4693 -- BELOW plain recency 0.6052); the PINNED graded ACT-R retrieval (hdlab.graded_coref_pick, Lewis & Vasishth) was already built but consumed only by commonnoun_binder, never the live pronoun path. WIRE LANDED default-on (EventCentralityReader.graded_pick=True, event-centrality forced off; graded_pick=False = self-checkable fallback). MEASURED first-hand: live pooled coref 0.4693->0.6019 (+0.1327 CI-sep); named coref no-regress 0.4883->0.6165; who-has-what board dim 0.4035->0.4735 (+0.070 CI-sep); info-free twin loses; coref-independent dims byte-identical 12/12. Reverify test_coref_graded_live_transfer.py 5/5 (21/21 suite) + landing test_coref_graded_pick_landing.py 7/7. BRAIN_FOUNDATIONAL_AUDIT.md 2b (2026-09-06). Follow-ons: entity-unification shared lever (p2 filed); +0.043 overlay-by-entity bonus (owner call); a modern pronoun coref corpus."
---

# PROBLEM: the reader's own coreference is only ~0.58-accurate, and that ONE number caps at least three dimensions at once — it is the single most SHARED upstream bottleneck. The brain resolves reference by cue-based content-addressable RETRIEVAL (recency + centrality + gender/number/animacy agreement + semantic fit, Lewis-Vasishth 2005); build a faithful stronger resolver so a pronoun/mention binds to the right discourse entity, and the affect experiencer / entity-world-model / who-has-what dimensions it feeds all rise with it.

**slug:** `strengthen_the_cue_based_pronoun_coreference_resolver_the_shared_upstream_accuracy_cap` — **opened:** 2026-09-05 by the strategy session (the highest-leverage SHARED lever surfaced across the recent submissions: the entity-KB resolver, affect, and who-has-what all bottom out on the reader's own coref accuracy). **status:** OPEN. Glass-box, NO external LLM. Strategy lands the Q111 wire.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** Iterate to the OPTIMAL brain-foundational solution; do NOT submit the first thing that clears. The OPENING MOVE is "how does the BRAIN actually do this?" — name the structure/circuit + replicate the OPERATION. A located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed. Run a 30-min deepening cron; cancel + submit only when the brain-mechanism bar is met AND nothing more of value remains.

> ## 🧠 BRAIN-FOUNDATIONAL CHECKLIST (work through IN ORDER; not done until every box holds)
> 1. **OPEN — how does the BRAIN do THIS?** Name the structure + computation; PINNED vs OUR-INVENTION. RESEARCH where unsure.
> 2. **REUSE — does an existing organ already do it?** Check `tools/substrate_map.py` / `hdlab/` FIRST.
> 3. **GENERALIZE — how does the brain generalize it?** Build for that.
> 4. **HIT A WALL? GO DEEPER.** A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, failed.
> 5. **OPTIMIZE BY EXACT REPLICATION.** Copy the computation, SWEEP the parameters.
> 6. **PERFORMANCE vs THE BRAIN.** Where do we lose signal? The mechanism-diff.
> 7. **ADJACENT COMPONENTS.** Map the neighbours — seeds the next problems.
> 8. **COMPLETION BAR.** COMPLETE + EXCELLENT + conveys the full benefit?

## 1. THE PROBLEM IN PLAIN LANGUAGE
When a story says "he", "she", "the old man", the reader has to decide *which* character that is. It gets this right only about 58% of the time — and almost everything else the reader does about people rides on it: how a character feels, what they own, what they want, who did what. So one weak step quietly drags down several parts of the scoreboard. Make the "who is this referring to" step markedly better, the brain's way.

## 2. WHY THIS ONE — one fix lifts several dimensions
Coref is the most SHARED upstream lever in the reader. Measured caps that all trace to it: the entity-world-model resolver reaches hard-link 0.434 vs its 0.540 ceiling and the residual is the reader's own 0.58-accurate coref; affect's own signal-loss study found **87% of the end-to-end affect loss is coref** (83.5% of emotion-experiencers are common-noun entities the reader tracks poorly); who-has-what and goal experiencers bind through the same resolution. A stronger resolver is BIDIRECTIONAL — it also feeds the just-landed entity-KB resolver, which itself named "a better substrate pronoun/coref resolver" as its next lever. This is the biggest single accuracy multiplier available without relaxing the invariant.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: reference resolution is CUE-BASED, content-addressable RETRIEVAL from working memory (Lewis & Vasishth 2005 ACT-R; McElree direct-access) — a pronoun/description is a partial cue that reactivates the memory trace matching best on a WEIGHTED SUM of cues: recency, discourse CENTRALITY/topicality (Centering: Cb/Cf; Grosz-Sidner), gender/number/person AGREEMENT, animacy, and SEMANTIC/selectional fit (verb-argument plausibility) — with interference from similar competitors (the fan effect). NOT a single positional/recency rule. REUSE (do NOT re-derive): `hdlab/graded_coref_pick` (the landed ACT-R cue-based op — its "cue-based-activation wins on real narrative" is already established), `hdlab/event_centrality_coref` / the reader's `EventCentralityReader` (centrality), `hdlab/commonnoun_binder` (common-noun clustering), the reader's coref column (`hdlab.coref.parse_litbank_conll`), `hdlab/animacy_lexicon`, `hdlab/psych_verb_frames` (experiencer). The lever is INTEGRATING these cues in the retrieval competition (graded, weighted, interference-aware), not adding a new organ.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive):** the live reader coref board dim ≈ 0.51; the reader's pronoun coref ≈ 0.58-accurate (entity-KB signal-loss); affect loss is 87% coref; the entity-KB hard-link 0.434 vs 0.540 ceiling is coref-residual-bound; `graded_coref_pick` (ACT-R cue-based) already beats surface heuristics on real narrative.
- **INFERRED (you must measure):** whether a stronger cue-INTEGRATED retrieval resolver lifts the LIVE coref board dim CI-separated over the current reader with a shuffled-cue info-free twin LOSING; and whether that propagates CI-separated to at least one downstream (affect experiencer accuracy OR the entity-KB hard-link) — the bidirectional payoff. Which cue is the binding lever (centrality? semantic fit? interference?) via ablation.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: understand ALL the coref organs (`python tools/substrate_map.py`) + read IN FULL the recent coref/entity SOLVEDs: `seed_the_entity_world_model_resolver...` (the 0.58-cap + the pronoun-into-entity finding), `form_a_discourse_referent_for_every_entity...` (the surface-head baseline + the located negatives), `wire_the_referent_to_coref_linking_pass...` (the decouple + the +0.043 overlay bonus). Read `hdlab/graded_coref_pick.py`, `hdlab/event_centrality_coref.py`, the reader's coref path in `hdlab/situation_reader.py`.
- Reproduce first-hand: the live coref board number (`experiments/exp_situation_model_qa_v1.py`) + the pronoun-slice accuracy.

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = a cue-integrated retrieval resolver that lifts the LIVE reader coref (pooled pronoun `coref_acc` on real narrative) CI-separated over the current reader, with a shuffled-cue-validity info-free twin LOSING and NO-regress on named coref — AND at least one downstream (affect experiencer OR entity-KB hard-link) rises CI-separated from consuming the better coref (the bidirectional payoff). Report CI half-width + null p95; recompute floors per population. A rigorous located NEGATIVE — the faithful cue-based resolver cannot beat the current reader, with the binding cue/interference cause named + measured — is a FULL PASS.

## ALREADY TRIED / DO NOT REDO
- Surface-head grouping is the current baseline (0.605); a NAIVE cue-based former did NOT beat it (+0.0008, located negative) — the lever is cue INTEGRATION + interference, not a single reweight. Measured-capped DEAD ENDS (do not re-open): WordNet lexical bridging (+7.8%-only), possessor-relational binder (+0.0006), 2-pass consolidation (+0.0045), confidence-gating (+0.0056), the step-5 per-character individuation chain (converges ~0.55, does not separate).
- Do NOT re-solve COMMON-NOUN linking — that is the just-landed entity-KB resolver (this problem is PRONOUN + general resolution ACCURACY; they compose).

## COORDINATION (does NOT conflict with the in-flight substrate streamlining)
The pass wires the entity-KB resolver into `commonnoun_binder` (common-noun LINKING); THIS problem is the PRONOUN + general resolution ACCURACY — a different sub-path that the entity-KB SOLVED itself named as the bidirectional next lever. Prototype in `experiments/` against the current reader; strategy lands the Q111 wire (after/alongside the entity-KB coref tier). No live-code overlap.

## FILES AND ENTRY POINTS
Prototype + measure in `experiments/` + `verification/`; the wire is the reader's coref path in `hdlab/situation_reader.py` + `hdlab/graded_coref_pick.py` (cue integration) + `hdlab/event_centrality_coref.py`. REUSE `hdlab/animacy_lexicon`, `hdlab/psych_verb_frames`, `hdlab/commonnoun_binder`. Strategy lands the Q111 wire; fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

## DO NOT QUOTE
- Do NOT quote a coref gain without the shuffled-cue-validity info-free twin LOSING + named no-regress.
- Do NOT quote the downstream (affect/entity-KB) payoff without measuring it on its OWN right instrument.
- NO external LLM (the invariant); cue-based retrieval is glass-box (WordNet/lexicon cues + the landed ACT-R op).
