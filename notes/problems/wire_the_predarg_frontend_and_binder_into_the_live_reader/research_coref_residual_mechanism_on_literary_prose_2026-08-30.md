# Research drill: the brain mechanism of the coref RESIDUAL on literary prose — and the highest-yield glass-box next build (2026-08-30)

Author: hdi_research (Director). Seeds the next problem after `wire_the_predarg_frontend_and_binder_into_the_live_reader`.
Motivating finding (just measured, decisive): on real 19c literary prose (LitBank/Dickens, 100 docs) end-to-end
who-did-what is ENTIRELY coreference-bound (perfect pronoun binding -> metric 1.000; parse + name-clustering are NOT the
bottleneck — the real arc parse TIES gold parse). The landed graded STRUCTURAL binder (Centering Cb + ACT-R base-level
activation + gender agreement; Lewis & Vasishth 2005) recovers only ~12% of the binding headroom; ~67% of pronouns
remain mis-bound. Humans resolve these easily.

**Lit-scan calibration penalty applied** (P estimates deflated 0.15–0.25; interpretations flagged SPECULATIVE; PINNED =
a primary result directly on the claim). **Sourcing caveat:** ScienceDirect/Wiley/Springer full text and the primary PDFs
(Jäger 2017; GAP) returned binary/403; effect DIRECTIONS are solid, exact numbers from abstracts/citing-text are
unverified. **This drill BUILDS ON two on-disk sibling drills — DO NOT re-derive them:**
`the_reader_has_no_coherence_next_mention_prior/research_intrasentential_binding_mechanism_2026-08-29.md` and
`.../research_world_knowledge_for_reference_2026-08-29.md`, plus the strategy-side ~50-source note
`notes/research_world_knowledge_reference_resolution_glassbox_2026-08-29.md`.

---

## BOTTOM LINE (one screen)

1. **The residual is NOT general-world-knowledge-bound and NOT a "better interference model" away.** Our own on-disk
   oracle decomposition (n=205 LitBank structural residual, `exp_coref_residual_world_knowledge_ceiling_v1`) is the
   strongest available evidence and it is decisive: a WordNet selectional oracle recovers **2%**, a CSKG commonsense
   oracle **2.8%** (coverage was HIGH at 87% but the KB does not DISCRIMINATE), while a fine TOKEN-DISTANCE oracle
   recovers **37.6%**. And the gold antecedent is **anti-typical** (mean recency rank 1.99; the resolver grabs the
   typical/topical entity `resolver_pick_is_most_frequent_frac`=0.356). **The answer is a SPECIFIC-DISCOURSE fact — what
   THIS text just established about these entities — not a general commonsense fact and not a marginal salience cue.**

2. **The dominant residual mechanism is a DISCOURSE / attentional-state one, and it has a glass-box, KB-FREE structural
   implementation we have NOT yet built:** a Grosz-Sidner (1986) focus-STACK / QUD-tracked LOCAL focus over the situation
   model the reader already accumulates. The anti-typicality signature IS the classic **topic-shift** case
   (topic-shift impairs resolution; Yang/topic-shift literature) — the gold is the *local* focus of the current
   sub-event, which differs from the *global* topic that flat Centering Cb + recency track. This is the one
   brain-faithful STRUCTURAL lever the sibling drills did NOT test.

3. **Ranked answer to point 4 (one line):** BUILD a glass-box discourse-focus / QUD entity-tracker (Grosz-Sidner focus
   stack over the accumulating situation model) as the NEXT problem — **measure its oracle ceiling on the 205-case
   residual FIRST, can-fail with an info-free twin**; it is the only untapped brain-faithful STRUCTURAL lever and needs
   no knowledge base. The coherence next-mention PRIOR, a static commonsense KB (WordNet/CSKG), and a "better
   interference model" are PROVEN DEAD ENDS on this residual; general meaning-supply (Phase-1) serves only the ~2–3%
   Winograd slice and should NOT be the primary route for THIS residual.

---

## 1. What is the brain using where structural cue-integration is WRONG? — mechanisms RANKED by residual share

Estimates fuse the literature with our on-disk oracle decomposition (the disk OUTRANKS the literature where they touch
the same population). Shares are of the NATURAL residual (they overlap; not additive).

**RANK 1 — DISCOURSE ATTENTIONAL-STATE / QUD-tracked LOCAL focus (specific-discourse fact). ~50–60% (SPECULATIVE, by
elimination).** By construction the residual is anti-typical: the gold is the entity the *current sub-event / QUD* is
about, which has just DIVERGED from the global topic. The brain tracks this with an attentional-state focus STACK that
pushes/pops with discourse-segment purpose — not a flat prominence score. PINNED substrate: Grosz & Sidner 1986
(*Computational Linguistics* 12(3):175–204) attentional state = a stack of focus spaces; Grosz, Joshi & Weinstein 1995
Centering (the *local* coherence layer of that same theory); topic-shift raises resolution cost and forces referential
re-ranking (topic-shift-impairs-resolution studies; focus-status studies, Frontiers 2021 PMC8351791). Readers build and
update entity mental models online (situation-model tracking; Frontiers frai 2023 PMC10060885). **Why this is the residual:**
our flat Cb + recency binder models global topic CONTINUATION; the residual is exactly the topic/focus-SHIFT cases it
cannot represent. This is glass-box and KB-FREE.

**RANK 2 — FINER-LOCALITY STRUCTURE (intra-sentential / token-distance). 37.6% oracle, but UNGATEABLE as-is.** On-disk:
the token-distance channel is the largest reachable slice (37.6%) where sentence-bucket recency scores 0%. PINNED brain
basis: cue-based retrieval uses ITEM-LEVEL structural PROXIES (clause-mate-hood, local-domain, subjecthood) as weighted,
nonlinearly-combined cues — NOT a c-command read off a parse tree (Kush 2013 diss.; Kush, Lidz & Phillips 2015 *JML* 82;
Parker 2019 *Cog. Sci.* 43(3)). BUT the sibling already found it ungateable: fusing it drags structure-decisive accuracy
1.000->0.814 (every residual gain costs an equal-or-greater regression), AND the cross-domain GAP test (clean spaCy parse,
modern Wikipedia) showed structural cues on the residual score BELOW chance (0.256). So the parse is not the wall and this
oracle is not deployable globally — only a confidence/entropy-GATED intra-sentential version is a live (medium-yield) retry.

**RANK 3 — VERB SEMANTICS / IMPLICIT CAUSALITY. Small on the NATURAL residual (few %); large on CONSTRUCTED pairs.** Real
per-verb bias exists and is graded (PINNED: Garvey & Caramazza 1974 *Ling. Inquiry* 5:459–464; Ferstl et al. 2011
*Behavior Research Methods* 43:124–135, 305-verb norms; Hartshorne & Snedeker 2013; Hartshorne 2014). BUT (a) IC affects
WHICH ARGUMENT SLOT is re-mentioned, NOT WHICH ENTITY fills it — a per-verb table cannot in principle discriminate
person-vs-person (Bott & Solstad 2014/2021, empty-slot); (b) IC fires only under specific coherence relations (esp.
Explanation), a LATENT variable in free narrative. On-disk confirmation: the IC/selectional prior flips **8/8 CONSTRUCTED**
implicit-causality pairs (mechanism works) but recovers **0/205** of the real residual (population lacks the trigger cases).

**RANK 4 — WORLD KNOWLEDGE / selectional restriction (Winograd-style). ~2–3% oracle (KB-needed, LOW yield here).**
On-disk WordNet oracle 2%, CSKG oracle 2.8%. PINNED brain basis: selectional/thematic fit is graded, statistical,
IMMEDIATE (McRae, Spivey-Knowlton & Tanenhaus 1998 *JML*; Hagoort et al. 2004 *Science* 304:438–441 — a world-knowledge
violation gives an N400 as fast as a lexical one) and lives in a distributional ATL "semantic hub" (Patterson, Nestor &
Rogers 2007), NOT a symbolic KB. This is REAL but is a SMALL fraction of THIS residual.

**RANK 5 — SIMILARITY-BASED MEMORY INTERFERENCE. NOT a resolver (~0% incremental).** Decisive for point 1(c): Jäger,
Engelmann & Vasishth 2017 (*JML* 94:316–339; doi:10.1016/j.jml.2017.01.004) — **"no evidence for interference is found in
configurations with a FULLY cue-matching subject/antecedent"**; interference (facilitatory in agreement, inhibitory in
reflexives) appears only with a PARTIALLY-matching distractor. Our residual is precisely TWO FULLY-cue-matching candidates
(two same-gender human characters, both licit "he" antecedents). In that configuration cue-based retrieval predicts a TIE,
not a resolution — interference explains the DIFFICULTY/error, never the answer. So our binder is not MIS-modeling
interference in a fixable way; a "correct interference model" would still return a tie on exactly these cases. (Empirical
support for inhibitory interference even in grammatical two-licit-candidate sentences is itself weak/contested — Jäger 2017;
model-fit failures of Lewis & Vasishth 2005 are strongest in the retroactive/prominence conditions.)

**RANK 6 — PREDICTION / anticipation.** Subsumed into the next-mention prior term below; weak as a standalone lever on the
residual (the anticipatory signal is collinear with the salience the binder already uses — see §2).

---

## 2. Meaning-bound vs still-untapped STRUCTURAL mechanism — and WHY the coherence prior failed

**Answer: the residual is PRIMARILY DISCOURSE-MEMORY-bound (glass-box, KB-free), NOT general-meaning/world-knowledge-bound.**
The precise reading that sharpens the sibling's `SEMANTIC_WALL` / `WORLD_KNOWLEDGE_DEAD` verdicts: general commonsense is
high-coverage but NON-discriminating (CSKG 87% coverage, 2.8% accuracy) — the disambiguator is a fact THIS discourse
established, so the right instrument is a richer DISCOURSE/situation model, which has a STRUCTURAL implementation (focus
tracking). There IS an untapped structural mechanism: the Grosz-Sidner focus STACK / QUD (Rank 1). The small genuinely
KB-bound slice (~2–3%, Winograd person-vs-person) is what routes to the Phase-1 meaning-supply bottleneck — but it is a
minority here, so meaning-supply is the wrong PRIMARY route for this residual.

**Why a coherence / next-mention PRIOR failed on a STRUCTURAL residual (three PINNED reasons):**
- **(a) The Kehler-Rohde asymmetry — the prior is the WRONG term.** In the strong Bayesian model
  `P(ref|pron) ∝ P(pron|ref) · P(ref)`, the PRODUCTION likelihood `P(pron|ref)` carries the STRUCTURAL factors
  (subjecthood, topicality) and DOMINATES interpretation, while the next-mention PRIOR `P(ref)` carries the semantic
  factors but has a SMALLER effect on interpretation — production and interpretation biases DISSOCIATE (Kehler & Rohde
  2013 *Theoretical Linguistics* 39:1–37; Rohde & Kehler 2014 *LCN* 29:912–927; Kehler & Rohde 2019 *J. Pragmatics*
  "Prominence and coherence"). Fixing structural errors needs a strong *orthogonal* term; the marginal prior is weak.
- **(b) Collinearity — the prior POINTS THE SAME WAY as the term that is already wrong.** Next-mention frequency is itself
  correlated with topicality/salience, so on the residual (where salience is misleading) the real prior largely AGREES
  with the wrong likelihood and adds little orthogonal signal. This EXPLAINS the disk result that the info-free twin BEAT
  the real prior (0.1005 vs 0.0683, NOT_SEP): the prior's tiny true signal is dominated by its collinear-with-salience mass.
- **(c) The coherence relation is a LATENT variable.** IC/coherence only bias re-mention CONDITIONAL on the relation
  (Explanation, Result...); in free narrative the relation is rarely marked by a connective, so marginalizing over
  relations washes the signal to a diffuse verb-average (Bott & Solstad 2014; Kehler & Rohde 2016 QUD model). The RIGHT
  formulation is not a marginal P(ref) — it is an interpretation-time term conditioned on the INFERRED QUD/focus and the
  SPECIFIC entities' discourse state (Rank 1), which is why a focus/QUD tracker, not a verb-average prior, is the fix.

---

## 3. Winograd-schema (world-knowledge-decisive) fraction of literary-narrative pronoun ambiguities

**PINNED direct bound (our disk): a general-world-knowledge KB resolves only ~2–3% of the LitBank residual as an oracle**
(WordNet 2%, CSKG 2.8%) — so the Winograd-decisive slice of the NATURAL residual is SMALL. **Corroborating literature
(SPECULATIVE for exact fractions):** WSC-273 is a tiny, hand-crafted set (Levesque, Davis & Morgenstern 2012); GAP
(Webster et al. 2018, arXiv:1810.05201) had to actively BALANCE/filter Wikipedia to assemble same-gender ambiguous
pronouns because they are a MINORITY of running-text pronouns; in OntoNotes "simpler high-frequency coreference examples
greatly outnumber ambiguous pronouns." No paper gives a clean "X% of LITERARY pronouns are Winograd" number — treat our
own oracle decomposition as the load-bearing estimate. **So the meaning-bound vs structure-bound split for THIS residual:
~2–3% general-world-knowledge (KB), ~37% finer-locality structure (ungateable), the remaining ~50–60% specific-discourse
attentional-state (Rank 1).** The residual is mostly STRUCTURE/discourse-bound, not Winograd-bound.

---

## 4. Decision-useful: highest-fidelity, highest-yield next glass-box mechanism (ranked)

Constraints: NO external LLM at inference (the invariant); a STATIC offline-built asset is admissible.

- **#1 — BUILD, route to a NEW problem: glass-box DISCOURSE-FOCUS / QUD entity-tracker.** A Grosz-Sidner (1986) focus
  STACK (push/pop on discourse-segment shift) + Centering transition types tracked as a stack — NOT a flat Cb — over the
  situation model the reader already accumulates (`exp_wire_coref_accumulate_situation_model_v1` exists). Motivated by the
  anti-typicality signature (gold = local focus after a topic-SHIFT). Highest brain-fidelity (pinned discourse theory),
  only untapped STRUCTURAL lever, KB-free. **GATE: measure the ORACLE ceiling on the 205-case residual FIRST**, then a
  can-fail build with an info-free twin (the coherence-prior negative is the cautionary precedent — a rigorous negative
  here is a full pass, and would upgrade the verdict to "the residual is a genuine no-LLM glass-box bound").
- **#2 — BUILD (secondary): a parse-CONFIDENCE / entropy-GATED intra-sentential finer-locality retrieval** — the gateable
  form of the 37.6% token-distance oracle, firing only where a reliable local dependency exists. Medium yield, medium
  fidelity; the sibling proved the UNgated global form regresses.
- **#3 — ROUTE to Phase-1 meaning-supply, LOW priority for THIS residual: a static selectional/world-model asset** — real
  and brain-faithful (ATL semantic hub) but serves only the ~2–3% Winograd slice here; it is the right long-term
  FOUNDATION, wrong primary fix for THIS wall.
- **DEAD ENDS — do not repeat (all refuted on-disk):** the coherence next-mention PRIOR (marginal P(ref), verb-average) —
  loses to its own info-free twin; a static commonsense KB (WordNet/CSKG) as a selectional prior on the residual — 2–3%
  oracle, non-discriminating; a "better interference model" — Jäger 2017 says fully-cue-matching candidates give a TIE,
  not a resolution; the token-distance channel applied GLOBALLY/ungated — catastrophic structure-decisive regression.

---

## Key citations (PINNED unless marked)
- Grosz & Sidner 1986, *Computational Linguistics* 12(3):175–204 — attentional state = focus-space STACK (aclanthology.org/J86-3001). **[Rank-1 foundation]**
- Grosz, Joshi & Weinstein 1995, *Computational Linguistics* 21(2) — Centering (local coherence layer).
- Kehler & Rohde 2013, *Theoretical Linguistics* 39:1–37 — Bayesian reconciliation; 2019 *J. Pragmatics* "Prominence and coherence"; Rohde & Kehler 2014, *LCN* 29:912–927 — production/interpretation dissociation. **[why the prior fails]**
- Kehler & Rohde 2016 — expectation-driven QUD model of discourse. **[QUD formulation]**
- Jäger, Engelmann & Vasishth 2017, *JML* 94:316–339, doi:10.1016/j.jml.2017.01.004 — no interference with a fully-cue-matching antecedent. **[interference is not a resolver]**
- Lewis & Vasishth 2005, *Cognitive Science* 29:375–419 — the ACT-R cue-based model our binder implements.
- Kush 2013 (diss., Maryland); Kush, Lidz & Phillips 2015, *JML* 82; Parker 2019, *Cog. Sci.* 43(3) — item-level structural proxies, nonlinear cue combination.
- Garvey & Caramazza 1974, *Ling. Inquiry* 5:459–464; Ferstl et al. 2011, *Behav. Res. Methods* 43:124–135; Hartshorne 2014 — implicit causality norms.
- Bott & Solstad 2014/2021 — IC selects the argument SLOT, not the ENTITY.
- McRae, Spivey-Knowlton & Tanenhaus 1998, *JML*; Hagoort et al. 2004, *Science* 304:438–441; Patterson, Nestor & Rogers 2007 — selectional fit / ATL semantic hub.
- Levesque, Davis & Morgenstern 2012 (WSC); Rahman & Ng 2012 (DPR); Webster et al. 2018, arXiv:1810.05201 (GAP) — Winograd/ambiguous-pronoun corpora.
- On-disk (OUTRANKS lit on shared populations): `exp_coref_residual_world_knowledge_ceiling_v1` (WK 2%, CSKG 2.8%, anti-typicality); `exp_coref_coherence_next_mention_prior_v1` (coherence prior loses to twin); `exp_coref_residual_crossdomain_gap_v1` (clean parse below chance on residual).

---

## TLDR (plain language)
Our reader mis-links about two-thirds of the pronouns in old novels, and people find these easy — so something is
missing. We checked the usual suspects and, on our own data, they mostly do NOT explain the misses: a general
"common-sense fact" dictionary answers only about 3 in 100 of the hard cases, and simply modelling "two candidates
compete in memory" cannot pick a winner when both fit equally (that only explains why it is HARD, not the answer). The
real pattern is that the correct answer is usually the character the CURRENT bit of the story is about — which is often
NOT the character the story has been mostly about. Our reader only tracks the overall main character, so it grabs the
wrong one. The fix that matches how the brain does it, and that we can build as clear glass-box code with no outside AI
and no fact-dictionary, is a "who are we talking about right now" tracker that follows attention as it shifts scene to
scene. We should build that next — but measure its best-possible ceiling on the hard cases FIRST, because three related
ideas already looked promising and then failed the honest test.

## QUESTIONS
None — the on-disk oracle decomposition already bounds the routing decision.

## NEXT STEPS
1. Open a new problem: glass-box discourse-focus / QUD entity-tracker (Grosz-Sidner focus stack over the accumulating
   situation model). GATE: oracle ceiling on the 205-case LitBank residual FIRST; then a can-fail build with an info-free
   twin (a rigorous negative is a full pass and settles whether the residual is a real no-LLM glass-box bound).
2. Fold this into `notes/BRAIN_FOUNDATIONAL_AUDIT.md`: the binder's flat Centering Cb is an OUR-INVENTION simplification
   of the pinned Grosz-Sidner attentional STACK — a named fidelity gap, not a placeholder to leave silent.
3. Do NOT re-open the coherence next-mention prior, a static commonsense KB, or an interference-remodel for this residual
   (refuted on-disk / by Jäger 2017); keep the Winograd person-vs-person slice as a small, explicit Phase-1 meaning-supply
   dependency, not the primary route.
