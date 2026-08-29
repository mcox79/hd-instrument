---
priority:
review: EXCELLENT
review_text: "RIGOROUS NEGATIVE (owner-DONE) = a full pass, integrated 2026-08-29. Reverified FIRST-HAND (test_coref_coherence_next_mention_prior.py 11/11 PASS). The brief's coherence next-mention PRIOR is REFUTED as the residual's fix: the faithful prior (selectional + thematic, Bayesian-product fused, DEV-tuned) recovers 0.068 on the n=205 residual but its 20-shuffle info-free TWIN recovers MORE (0.100, NOT_SEP) -- it does not beat its own noise. SIX independent brain-faithful channels are all measured dead/anti-predictive (coherence prior 2.9% oracle, clean-parse structure BELOW chance on cross-domain GAP, WordNet selectional 2.0%, ConceptNet/CSKG 2.8% despite 86.8% coverage, item-level structural proxies 0/205). UNIFYING INSIGHT (why all six fail identically): the residual is BY CONSTRUCTION the anti-typical cases, so every typicality-tracking cue points the wrong way -- the Winograd core, a SEMANTIC/specific-discourse-knowledge bound, not coherence-prior/parse/static-KG. The POSITIVE CONTROL passes (8/8 selectional + 8/8 implicit-causality on constructed pairs where the mechanism CAN move the metric). Exemplary: led with biology (two 4-lane literature drills), and the cross-domain GAP test CORRECTED the solver's own parse-quality diagnosis (SEMANTIC_WALL_NOT_PARSE_WALL). LANDED the one thing it earns -- the separately-measured POOL CLEANUP (+0.022 CI-sep, info-free random-drop twin loses): a person-feature agreement filter dropping 1st/2nd-person pronoun artifacts from a 3rd-person pronoun's candidate pool, into hdlab/graded_coref_pick.py (is_first_second_person_artifact + keep_after_pool_cleanup, additive/opt-in), witness test_coref_pool_cleanup_organ.py 7/7. Did NOT land any coherence prior / fine-distance override / structural-proxy binder / static-KG cue (all six measured dead). The residual's real levers = separate follow-ons (situation model + p1 distributional semantics), NOT a static commonsense KG."
---

> ## ✅ SOLVER REVIEW — INTEGRATED 2026-08-29 (grade: EXCELLENT; rigorous negative = full pass)
> **Verdict:** the coherence next-mention prior is a RIGOROUS NEGATIVE (owner-DONE) — a full pass per §7. Reverified
> first-hand (`test_coref_coherence_next_mention_prior.py` **11/11 PASS**). The argument is airtight and adversarially
> sound: (1) the honest floor is the 20-shuffle **info-free twin** (0.100), not likelihood-only (0/205 by construction),
> and the real prior (0.068) fails to clear it → carries no usable signal; (2) **six** independent brain-faithful channels
> all measured dead/anti-predictive; (3) one structural reason unifies them — the residual is **anti-typical by
> construction** (the Winograd core), so every typicality cue is anti-predictive; (4) the **positive control** passes
> (8/8 + 8/8), proving the mechanism works and the population lacks the cases, not a broken tool. **Exemplary practice:**
> two 4-lane biology-first literature drills, and a **cross-domain GAP test that corrected the solver's own** parse-quality
> diagnosis to SEMANTIC_WALL_NOT_PARSE_WALL.
> **Landed (Q111):** the one earned win — the separately-measured **pool cleanup** (+0.022 CI-separated, info-free
> random-drop twin loses): a person-feature agreement filter (`is_first_second_person_artifact` +
> `keep_after_pool_cleanup`) into `hdlab/graded_coref_pick.py`, additive/opt-in, witness
> `verification/test_coref_pool_cleanup_organ.py` **7/7 PASS**. **Did NOT land** any coherence prior, fine-distance
> override, structural-proxy binder, or static-KG plausibility cue — all six are measured dead on the residual.
> **Audit:** folded into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b — the coref residual is a SEMANTIC/world-knowledge bound; the
> ~0.78 glass-box no-LLM ceiling is REAL; the two-system boundary is SYNTAX×SEMANTICS×WORLD-KNOWLEDGE, not
> LIKELIHOOD×coherence-PRIOR. Real residual levers = separate follow-ons (situation model + p1), NOT a static KG.

# PROBLEM: pronoun reference is a TWO-TERM Bayesian computation (Kehler & Rohde 2013) — a Centering LIKELIHOOD (grammatical role / topichood, which the integrated graded coref resolver now computes) × a coherence-driven next-mention PRIOR P(referent) (verb-semantic / discourse-coherence expectations, which the substrate does NOT compute). The graded resolver's ~19% structural residual is EXACTLY the prior-decisive cases (no structural cue points to the gold antecedent). Build the missing coherence next-mention PRIOR channel — SUBSTRATE-NATIVE (the predictive-reader organ already computes a next-entity expectation) — multiply it into the graded coref posterior, and validate it lifts resolution on the structurally-dominated residual CI-separated over the likelihood-only resolver with the info-free twin losing

**slug:** `the_reader_has_no_coherence_next_mention_prior` — **opened:** 2026-08-28 by the strategy session (the #1 mapped
adjacency of the integrated `coreference_is_capped_at_065_on_real_narrative`, owner-DONE/EXCELLENT: its KEY REALIZATION 5
+ adjacency 1). **status:** OPEN — a MECHANISM + BUILD problem. You build + validate in `experiments/`; strategy lands any
hdlab change (Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `5` — HIGH leverage: this is the ONLY remaining
> accuracy lever on real-narrative coreference (the graded resolver is at its structural ceiling ~0.78; the residual is
> the prior-decisive cases), AND it is a genuinely new REASONING/discourse capability (coherence-driven expectation) that
> generalises beyond coref (bridging, next-event prediction). **Dependency web:** it consumes verb semantics (p4
> `no_glass_box_verb_sense_disambiguation`) and composes with the graded coref resolver (p3 name-clustering is the OTHER
> coref lever). **Re-rank per the owner.**

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** — the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau — it is the FIRST thing you do.
>
> **🚀 YOU ARE ENABLED — AND EXPECTED — TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **⛔ "CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **🔁 THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) — RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one — and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps — AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) — that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill — do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across — never a ceiling.
> Each fire: implement → test (can-fail, strongest real floor, info-free twin LOSING) → iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS — but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When a story says "Elizabeth scolded Lydia because **she** was reckless", you know "she" = Lydia — not from grammar (both
are prior subjects/objects) but from MEANING: the verb "scold ... because" makes the REASON-giver the person being
scolded. The just-integrated coreference resolver handles the GRAMMAR half well (graded cue-based retrieval over salience
/ recency / subjecthood), but it is missing the MEANING half. Measured: **19.4% of its errors are STRUCTURALLY DOMINATED**
— no grammatical cue points to the right antecedent, so the resolver is at chance on exactly those cases, and that is why
it plateaus at ~0.78. The brain resolves these with the second half of a two-term computation: `P(referent | pronoun) ∝
P(pronoun | referent) × P(referent)`, where `P(referent)` is a coherence-driven NEXT-MENTION expectation computed online
from verb semantics and discourse-coherence relations (who the discourse is likely to keep talking about). The task: build
that missing coherence next-mention PRIOR channel — **substrate-native**, since the reader already has a predictive
(forward-expectation) organ — multiply it into the graded coref posterior, and show it lifts resolution on the
structurally-dominated residual over the likelihood-only resolver. A rigorous NEGATIVE (the prior buys < the CI on real
prose because the residual is irreducible annotation-fiat ambiguity) is a full pass — it closes the question of whether
the coref ceiling is a missing mechanism or a real bound.

## 2. WHY THIS ONE
It is the ONLY remaining accuracy lever on real-narrative coreference (the resolver is at its structural ceiling), and it
is a genuinely new brain capability — coherence-driven expectation — that generalises well beyond coref: bridging
inference, next-event prediction, and the situation model's forward pass all rest on the same `P(what-comes-next)` term.
Building it once turns "the reader tracks who/what grammar points to" into "the reader ANTICIPATES who the discourse is
about", the predictive-reader half the substrate has been moving toward.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the computation):** pronoun reference is a **two-term Bayesian product** — a Centering/structural LIKELIHOOD
  `P(pronoun|referent)` (grammatical role, topichood — what the graded resolver computes) times a **coherence-driven
  next-mention PRIOR** `P(referent)` (Kehler & Rohde 2013; Rohde & Kehler 2014). The PRIOR is computed online from
  **verb-semantic expectations** (implicit causality is epiphenomenal of verb-semantic primitives — Bott & Solstad 2014,
  R²=0.75) and **discourse-coherence relations** (Explanation → re-mention the cause; Result → the affected). Neural:
  anticipatory / predictive pre-activation of the likely next referent (Van Berkum et al. 2007 — a P600 at 400–700 ms to
  a referent that violates the coherence expectation), i.e. the **predictive-reader** system the substrate already models
  (`the_reader_is_feed_forward_where_the_brain_is_predictive`, integrated; audit: "PREDICTING what an entity does next
  uses content-addressable retrieval").
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the exact features that realise `P(referent)` (verb-semantic role
  expectation, coherence-relation type, discourse focus) and the FUSION with the likelihood (a log-linear sum / product,
  and its weight). Copy the COMPUTATION (Bayesian product likelihood × prior; the prior is a next-mention expectation);
  SWEEP the prior's features + the fusion weight. Reuse the substrate's predictive organ as the `P(referent)` source and
  the graded resolver's posterior as the likelihood, rather than hand-rolling.
- **NOT brain-faithful:** a lexical implicit-causality verb→bias LOOKUP alone — the coref solver measured the IC-decisive
  "NP1 VERB NP2 because PRON" frame occurs **n=0 times in LitBank's ~200K tokens**, so a lexical IC cue cannot reach the
  real-prose residual; and a generic semantic-fit feature bought only **+0.3 CoNLL F1** in a full published system
  (Heinzerling, Moosavi & Strube 2017) — so GATE the expectations and do NOT over-promise the semantic channel. A full
  external neural/LLM coref model is barred (the invariant).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE — do not re-derive):** the graded coref resolver + its posterior/entropy
  (`exp_coref_graded_cue_retrieval_litbank_v1.py`, the landed `graded_competition`); its error anatomy — **19.4% of
  errors are structurally dominated** (no most-recent / max-subjecthood / most-frequent cue points to gold); the lexical
  IC frame is ~absent in real prose (n=0); the substrate's predictive-reader organ computes a next-entity expectation.
- **INFERRED (to prove):** that a coherence next-mention PRIOR (verb-semantic + coherence-relation expectation),
  multiplied into the graded likelihood, resolves the structurally-dominated residual above the likelihood-only resolver
  on real narrative — OR that it does not (a rigorous null bounding the coref ceiling as real).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT rebuild the graded LIKELIHOOD resolver (integrated) or the name/nominal clustering (p3). Do NOT build a lexical
  IC verb→bias lookup as the mechanism (the frame is ~absent in real prose — a landed near-null). Do NOT use an external
  coref/LLM at inference. REUSE the predictive-reader organ as the `P(referent)` source + the graded posterior as the
  likelihood; gate the semantic channel (Heinzerling 2017: generic semantic fit buys little).

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `coreference_is_capped_at_065_on_real_narrative/SOLVED.md` (KEY REALIZATION 5 + adjacency 1 — the two-term Bayes,
  the 19.4% structural residual, the substrate-native proposal). Read the predictive-reader organ
  (`the_reader_is_feed_forward_where_the_brain_is_predictive` SOLVED + its hdlab organ) and
  `hdlab/coreference_resolver.py` (the graded resolver + the queued `run_graded_retrieval`). `tools/experiment_index.py
  query "coherence"` / `"predictive"` / `"next-mention"` / `"implicit causality"`. Audit: the newest §2b coref entry (the
  two-term Bayesian sub-claim) + the predictive-coding entry.
- Gold: a coherence/next-mention set (mine the structurally-dominated LitBank residual; or a Rohde-Kehler-style
  passage-completion gold — state how built + verified). **Mind the CORPUS-AGE confound** (LitBank is older literary
  prose; archaic discourse conventions) — factor it into the gold.

## 7. THE BAR
PASSES only with ALL of:
1. **A coherence next-mention PRIOR channel** (built in `experiments/`): `P(referent)` from verb-semantic /
   coherence-relation expectation, fused into the graded coref posterior as a Bayesian product. Copy the computation;
   SWEEP the prior's features + fusion weight.
2. **On the STRUCTURALLY-DOMINATED residual** (the ~19% where grammar gives no signal, recomputed on the same
   population), likelihood×prior beats the likelihood-only resolver **CI-separated**; the **info-free twin** (shuffled
   prior / random next-mention expectation) LOSES CI-separated; report CI half-width + null p95; no number crosses
   populations.
3. **NO REGRESSION on the structure-decisive cases** (where grammar already resolves it, the prior must not corrupt the
   answer — byte-or-CI-equal), and a **POSITIVE control** the metric can move (a coherence-decisive minimal pair the
   prior gets and the likelihood-only resolver cannot).
4. **One-screen summary:** prior features → fusion → residual lift → no-regression → verdict. Heavy → REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "a faithful coherence prior lifts the residual < the CI on real prose because a
large slice is LitBank annotation-fiat ambiguity — so the ~0.78 coref ceiling is a REAL bound, not a missing mechanism",
with the positive control confirming the metric CAN move on constructed coherence-decisive pairs).

## 8. FILES AND ENTRY POINTS
- Compose-with: `hdlab/coreference_resolver.py` (graded resolver + queued `run_graded_retrieval`); the predictive-reader
  organ (`P(referent)` source). Data: LitBank + the structurally-dominated residual; a coherence-completion gold. Audit:
  `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (§2b coref two-term Bayes + predictive-coding). Verb semantics: p4
  `no_glass_box_verb_sense_disambiguation`. Heavy → REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`).

## DO NOT QUOTE / DO NOT REDO
The 19.4%-structural-residual + n=0-IC-frame measurements are the MOTIVATING evidence (from the coref integration), not
your result. Do NOT rebuild the graded likelihood resolver or a lexical IC lookup. Strategy owns any hdlab landing — you
propose the coherence-prior channel + its fusion, you do not write `hdlab/`.
