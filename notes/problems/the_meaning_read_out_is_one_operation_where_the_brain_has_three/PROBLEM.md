---
priority:
review: EXCELLENT
review_text: "Bar MET decisively; re-verified FIRST-HAND (verify_perclass_meaning_operations.py ALL CHECKS PASS). The adjective SIGNED-MAGNITUDE op (GloVe projection onto a bipolar axis ANCHORED by the explicit WordNet antonym relation) recovers human magnitude CI-separated over BOTH the incumbent conceptual cosine AND the info-free random-axis twin, on an ADEQUATELY-POWERED, INDEPENDENT, non-WordNet human gold (Warriner VAD + Brysbaert, n~3600-5300 -- the SimLex n=111 power wall RESOLVED): valence 0.724 vs incumbent 0.165 (+0.559 CI-sep) vs random 0.067 (+0.657 CI-sep); dominance/concreteness/arousal all CI-sep at full power (witness subset confirms valence+dominance); shuffled-gold twin ~0; MOYER distance effect present (far>near +0.318). Per-class operation-specificity reproduced (cosine WINS nouns 0.599 + verbs 0.492, LOSES adjectives 0.479<0.585). REFINES the brief: the cosine is wrong for adjectives ONLY (verbs already served by the gloss channel -- a definition IS a relational description; only the blended distributional vector fails verbs). Exceptional depth (probes A-H): opposition is RELATIONAL not geometric (raw cosine AUC 0.356 inverts -> needs the explicit relation); ATOM single-axis REFUTED (independent per-dim axes); perceptual grounding DOUBLES concreteness (0.26->0.53); intensity is MARKEDNESS (frequency/AoA) not geometry; the magnitude CODE is FPE(log degree) in FHRR (log PINNED by Laughlin efficient coding), VALIDATED against 240k human number-comparison trials (Weber kernel predicts RT rho 0.96, beats a difference kernel CI-sep). Self-caught a signed-rho orientation bug + honest negatives (VerbNet does not beat the gloss). '3-way adjective class' (gradable-magnitude/evaluative-VAD/classificatory-taxonomic) supersedes a single adjective op. NO hdlab landed; a `scalar_adjective_operation` + operation-routing + an FPE-log upgrade of quality_relation Ch.B are EARNED proven-ready."
---

> ## SOLVER REVIEW -- EXCELLENT (integrated 2026-08-27 by the strategy session)
> **Re-verified FIRST-HAND, scaffold-free:** strategy ran `verification/verify_perclass_meaning_operations.py` -> ALL
> CHECKS PASS. Confirmed: adjective signed-magnitude valence rho 0.698 vs incumbent 0.117 (+0.58 CI-sep) / random 0.048
> (+0.65 CI-sep); dominance CI-sep; per-class specificity (nouns 0.599, verbs 0.492 win the cosine; adjectives 0.479<0.585
> lose); Moyer distance effect (far 0.911 > near 0.593); verb relational op beats the blended cosine +0.27 with the
> shuffled-structure twin losing. **Bar MET** -- the adjective op CI-separates at power on an INDEPENDENT non-WordNet human
> gold, resolving the n=111 wall. **Adversarial audit -- a model of depth and honesty:** (1) the op is brain-PINNED
> (Walsh ATOM signed magnitude; opposition anchored by the explicit antonym relation, since antonyms are geometrically
> similar -- the landed valence organ already proved this); (2) it REFINES the brief on disk (the cosine is wrong for
> adjectives ONLY -- verbs win with the gloss because a definition is relational; only the blended vector fails verbs);
> (3) the power fix was 'project before you buy' (Warriner/Brysbaert were already on disk, and DODGE the
> benchmark-selection confound the fetchable WordNet-derived sets carry); (4) the deep probes (A-H) are exceptional and
> each controlled -- opposition is relational not geometric, ATOM's single axis is refuted, perceptual grounding doubles
> concreteness, intensity is markedness not geometry, and the magnitude CODE is FPE(log degree) validated against 240k
> human number-comparison trials (the log PINNED by Laughlin efficient coding); (5) exemplary self-correction (caught a
> signed-rho orientation bug; reported honest negatives -- VerbNet does not beat the gloss, pairwise similarity is the
> wrong currency). **hdlab:** NO file landed (Q111); EARNED proven-ready -- a new `hdlab/scalar_adjective_operation.py`
> (per-dimension bipolar axes, evaluative-from-antonym-poles / denotational-from-Lancaster-perceptual-strength,
> independent axes, opposition from the explicit relation, degree from MARKEDNESS, encoded as FPE(log degree) in FHRR);
> operation-ROUTE the meaning read-out by word class with a gradability gate (noun/verb/classificatory-adj stay on the
> gloss); wire dimension SELECTION to the semantic-control (context-override WSD) organ; upgrade `quality_relation` Ch.B
> linear->log. Do NOT replace the verb gloss with VerbNet (net-neutral). AUDIT UPDATE folded (§2b). Completes the MEANING
> operation-routing line (p3).

# PROBLEM: the meaning read-out uses ONE similarity operation (feature-overlap cosine) where the brain uses a DIFFERENT operation per word class -- nouns by taxonomic overlap, adjectives by SIGNED-MAGNITUDE on a scale, verbs by relational/argument-structure -- and one cosine is the wrong operator for two of the three

**slug:** `the_meaning_read_out_is_one_operation_where_the_brain_has_three` - **opened:** 2026-08-27 by the strategy session
(the deepest finding of the conceptual-meaning-channel integration: meaning-similarity is OPERATION-SPECIFIC per word
class; a single cosine loses adjectives and verbs; the adjective signed-magnitude op was DIRECTIONALLY confirmed but
power-limited at n=111).
**status:** OPEN - **a NEW-MECHANISM problem (parallel-solver-appropriate): build + validate the per-word-class meaning
operations at power. The conceptual channel is landed; the operation-routing is not.**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `3`. The conceptual channel already wins meaning-
> identity; this is the next-fidelity operation-routing, directionally shown but not CI-separated. Re-rank per the owner.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do. If you have
> not identified the brain's mechanism and attempted to build it, you have not started the real work,
> whatever else you have measured.
>
> **🚀 YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> You are NOT boxed in -- not by this brief, not by the existing organs, not by the integration points you
> would tie into: if a MORE brain-foundational method conflicts with any of them, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful). Exploring
> the brain's true method is the work we most want from you; a bold, well-argued brain-faithful direction --
> even unfinished -- beats a tidy engineering result that never asked the question.
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several of your angles hit the
> SAME wall, that is strong evidence that NONE of them was the brain's mechanism -- the faithful method is
> probably DIFFERENT IN KIND, not another variation of what you already tried. A wall is a FIDELITY GAP TO
> BUILD ACROSS, never a ceiling. Hitting one is exactly the moment to LEAVE the family of methods you were
> sweeping and ask the biology again.
>
> **⛔ "CONVERGED" HAS A HIGH BAR, AND EXHAUSTING ENGINEERING VARIATIONS DOES NOT MEET IT.** Claim
> convergence ONLY when you have (a) identified how the brain actually performs this computation AND (b)
> replicated that operation as faithfully as you can and tested it, OR shown with a SPECIFIC reason why it
> cannot be replicated here. "I tried several combining / gating / scoring angles and they all plateaued at
> the same wall" is NOT converged -- it is tuning-limited, and it means the brain's mechanism is still
> UN-TRIED. That is a reason to explore harder, not to submit.
>
> **🔁 THE 30-MIN DEEPENING IS HOW YOU FORCE THIS -- IT IS NOT OPTIONAL BUSYWORK.** Run your own cron
> (`CronCreate "13,43 * * * *"`); each fire asks "how does the brain REALLY do this, one level deeper than
> my current mechanism?" -> implement -> test (can-fail, strongest real floor, info-free twin LOSING) ->
> iterate. Its whole purpose is to make you ask the brain question several more times than your own sense of
> "done" would. CANCEL it (`CronDelete`) and submit ONLY when the brain-mechanism bar above is met.
> Declining it because "my angles converged" is precisely the case it exists to catch.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully
> built.** A negative on a family of convenient engineering methods is not a negative on the capability; it
> is a report that you have not yet found how the brain does it.
>
> **📖 REFERENCE THE BRAIN-FOUNDATIONAL AUDIT, AND HELP KEEP IT TRUE.** Before you start, read the entry for the
> system you are touching in `notes/BRAIN_FOUNDATIONAL_AUDIT.md` -- it gives the brain structure, whether the
> brain's equation is PINNED or something we are INVENTING, our current fidelity, and the known deviation, so you
> inherit that instead of re-deriving it. If your work shows a verdict there is WRONG, STALE, or INCOMPLETE, or you
> find a NEW deviation, put a short **AUDIT UPDATE** note in your submission -- the strategy session folds it into
> the audit at integration. The audit is a living, shared map and you help maintain it.

## 1. THE PROBLEM IN PLAIN LANGUAGE

To judge whether two words mean the same thing, our reader uses ONE method: how much their dictionary features overlap.
That is right for NOUNS ("a dog is a kind of animal" -- shared features). But it is the WRONG tool for two other kinds of
words: ADJECTIVES are points on a SCALE (hot/cold, big/small) -- similarity is DISTANCE along the scale and opposites are
the two ENDS of the same scale, which feature-overlap has no notion of; and VERBS are about WHO-DOES-WHAT-TO-WHOM
(argument structure), which a blended word-vector loses. So the reader mis-judges adjective and verb meaning. The task:
give the meaning read-out the RIGHT operation for each word class, the way the brain does.

## 2. WHY THIS ONE

- **It is the deepest finding of the conceptual-meaning integration** (there is no single similarity operation) -- and
  the adjective fix was DIRECTIONALLY shown from OWNED resources but not yet CI-separated (power-limited, n=111).
- **It is buildable mostly from resources we already own** (GloVe scale-membership + WordNet antonym poles for
  adjectives; VerbNet/FrameNet is the one genuine not-yet-owned resource for verbs) -- "project before buying."
- **It is a clean brain-mechanism problem** (magnitude/ATOM system for scalars; relational structure for verbs),
  parallel to the strategy session's composition work.

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

**PINNED:** meaning-similarity is OPERATION-SPECIFIC per word class -- NOUNS = taxonomic feature/genus overlap (the ATL
conceptual hub, already landed as `hdlab/conceptual_meaning`); ADJECTIVES = SIGNED-MAGNITUDE distance on a shared oriented
axis, opposition = the two POLES of one axis (Walsh ATOM/IPS magnitude system; Moyer distance-effect; Kennedy degree
semantics; Osgood bipolar axes); VERBS = relational/argument-structure (thematic roles), which a single blended vector
fails. A single cosine is structurally the wrong operator for adjectives (no order/sign) and verbs (no relations).

**OUR-INVENTION-UNDER-TEST (mark each; sweep, don't adopt):** the adjective axis construction (GloVe scale-membership +
WordNet antonym-pole signed opposition, SemAxis-style -- the PER-PAIR signed-opposition worked; a global-profile SemAxis
did NOT); the verb relational operation (VerbNet/FrameNet argument-structure -- the not-yet-owned resource); the routing
(by word class). COPY the operation per class; SWEEP the params. Reuse `hdlab/conceptual_meaning` for nouns; do NOT add
an SVD distillation (tested-negative) or a symbolic antonym-flag as the mechanism (mechanism-approximate).

## 4. MEASURED vs INFERRED

**MEASURED (from `the_reader_has_no_conceptual_meaning_channel`, integrated 2026-08-27):** per word class on SimLex --
NOUNS: conceptual taxonomic overlap 0.599 (the channel's home). ADJECTIVES: conceptual 0.479 < GloVe 0.585 (feature
overlap is the wrong op); the OWNED-resource adjective op (GloVe + WordNet antonym-pole signed-magnitude) lifts SimLex
adjectives **0.585 -> 0.6227 with the info-free RANDOM-AXIS control LOSING (0.5528)** -- but CI-separation is
POWER-LIMITED (n=111: antonym-axis vs GloVe +0.038 CI[-0.050,0.127]; vs random +0.070 CI[-0.002,0.151], both straddle 0).
VERBS: gloss carries relational content 0.492; GloVe's single blended vector fails (0.152).

**INFERRED / OPEN (this problem):**
- Does OPERATION-ROUTING the read-out by word class beat the single-cosine conceptual channel on a per-class similarity
  gold CI-separated, with the adjective signed-magnitude op reaching CI-SEPARATION on an ADEQUATELY-POWERED, INDEPENDENT,
  non-WordNet adjective-similarity gold, and info-free twins (random axis / shuffled) LOSING?
- Is the faithful VERB operation a VerbNet/FrameNet argument-structure similarity (the one not-yet-owned resource)?

## 5. ALREADY TRIED / DO NOT RE-RUN

- Do NOT re-derive "one cosine loses adjectives/verbs" -- MEASURED. Do NOT use a global-profile SemAxis (projected onto
  1263 axes) -- it tied its own random control (the wrong operationalisation); the PER-PAIR signed opposition works.
- Do NOT ship a symbolic exact-antonym flag as the mechanism (it helps +0.10 on adj but is mechanism-approximate).
- Do NOT route adjectives to the grounded SENSORIMOTOR spoke -- tested, LOSES CI-separated (it is sensorimotor, not
  scalar-magnitude).
- Query `experiment_index.py query "adjective"`, `query "antonym"`, `query "similarity"`; read the conceptual-meaning
  SOLVED + `hdlab/conceptual_meaning.py` + `experiments/exp_scalar_adjective_operation_v1.py` BEFORE building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Reproduce the per-class numbers (`experiments/exp_scalar_adjective_operation_v1.py`, `exp_conceptual_channel_limits_v1.py`)
  -- confirm the adjective op's directional lift + the power limit (n=111).
- Acquire / locate a LARGER, independent, non-WordNet adjective-similarity gold (the power fix the integration named) --
  the operation refinement AND the powered gold must be done TOGETHER (the crude opposite-pole signal is the weak link,
  not the data alone).

## 7. THE BAR

Operation-routing the meaning read-out by word class must:

- **Beat the single-cosine conceptual channel on a per-class similarity gold CI-separated over its UPPER bound, with
  info-free twins (random axis / shuffled features) LOSING CI-separated.** Report CI half-width + null p95. In
  particular the ADJECTIVE signed-magnitude op must reach CI-SEPARATION on an adequately-powered, independent, non-WordNet
  adjective gold (the n=111 power limit resolved) with the random-axis control losing.
- **DECISIVE EITHER WAY:** operation-routing beats the single cosine CI-separated -> propose the hdlab wiring (strategy
  lands it, composing with the semantic-control router). It does NOT at power -> a rigorous negative localising whether
  the per-class operation is real-but-small or the wrong formalisation.

## 8. FILES AND ENTRY POINTS

- `hdlab/conceptual_meaning.py` (the noun/taxonomic channel) + `experiments/exp_scalar_adjective_operation_v1.py`
  (the adjective op) + `exp_conceptual_channel_limits_v1.py` (the per-class limit map). SimLex/SimVerb + a larger
  adjective gold to acquire.
- Prove in `experiments/` + `verification/`; propose the hdlab diff in `SOLVED.md` (strategy lands it, Q111). **Do NOT
  write `hdlab/`.**

## DO NOT QUOTE / DO NOT REDO

- The adjective op is DIRECTIONAL, power-limited (n=111) -- quote the mechanism + the random-axis control losing, NOT a
  CI-separated pass, until you resolve the power.
- Do NOT quote absolute conceptual rho as domain-general (WordNet provenance) -- the claim is the per-class WIN + twins
  losing. No number crosses populations/word-classes.
