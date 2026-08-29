---
owner_verdict: DONE
---

═══════════════════════════════════════════════════════════════════════════════════════════════════
SOLVER SUBMISSION — the_reader_has_no_coherence_next_mention_prior          (STATUS: REFUTED — rigorous negative = full pass)
hdlab/ UNTOUCHED (proposed diffs only, board Q111). AWAITING owner_verdict: DONE.
REVERIFY: .venv/Scripts/python.exe verification/test_coref_coherence_next_mention_prior.py   -> 11/11 PASS
Ledger:   python tools/problem_ledger.py --check   -> malformed/incomplete: 0
═══════════════════════════════════════════════════════════════════════════════════════════════════

BAR (§7): PASSES with ALL of — (1) a coherence next-mention PRIOR channel fused into the graded coref posterior as a
Bayesian product; (2) on the structurally-dominated residual it beats likelihood-only CI-separated with the info-free
twin LOSING (report CI half-width + null p95); (3) NO regression on structure-decisive + a POSITIVE control the metric
can move; (4) one-screen summary. A rigorous NEGATIVE is a FULL PASS.

VERDICT: RIGOROUS NEGATIVE — the coherence next-mention prior is REFUTED as the fix for the coref residual, with a
research-grounded, cross-domain-robust diagnosis. SIX independent brain-faithful channels are all measured dead or
anti-predictive on the residual (n=205, LitBank competitive pronoun subset, doc-bootstrap CI):
  1. Coherence next-mention prior (selectional-fit + thematic/coherence-relation, Bayesian-product fusion, weight tuned
     on DEV-residual): recovers 0.068 [0.031,0.108] but its 20-shuffle info-free TWIN recovers MORE (0.100 [0.083,0.120]);
     prior−twin −0.032 NOT_SEP (null p95 0.036). It does NOT beat its own noise. Oracle ceilings: selectional 1.5%,
     thematic 1.0%, combined 2.9%.
  2. Fine linear-distance (recency at token grain): 37.6% oracle but UNGATEABLE — every residual gain costs an
     equal-or-greater structure-decisive regression (tradeoff curve); global weight 0; intra-sentential gate breaks 432.
  3. Brain-faithful item-level structural-proxy cues (Kush 2013 — the brain binds via weighted structural proxies, NOT a
     c-command tree): jointly re-tuned, recovers 0/205.
  4. CLEAN-parse structure (cross-domain GAP, modern Wikipedia prose): on the GAP residual clean-parse structural cues
     score 0.256 — BELOW chance 0.5. A perfect parse does NOT recover the residual (verdict SEMANTIC_WALL_NOT_PARSE_WALL).
  5. WordNet-supersense selectional plausibility: 2.0% (0/29 on the distinct-supersense subset).
  6. ConceptNet/CSKG commonsense connectivity: 2.8% DESPITE 86.8% coverage — the KB connects every candidate to the
     context but cannot DISCRIMINATE.
POSITIVE CONTROL (bar item 3, PASSES): on constructed coherence-decisive minimal pairs the SAME prior mechanism flips
the pick — selectional 8/8, implicit-causality 8/8 — where the structural likelihood + info-free shuffle sit at chance
(~5/8). The mechanism WORKS; the real residual just lacks the cases.

THE UNIFYING INSIGHT (why all six fail identically): the residual is BY CONSTRUCTION the ANTI-TYPICAL cases (gold is NOT
most-recent / max-subjecthood / most-frequent; measured: gold recency-rank ~2, resolver grabs the most-frequent entity
36% of the time). So EVERY cue that tracks typicality — salience, structure, selectional plausibility, commonsense
connectivity — is anti-predictive on it. The disambiguator is a SPECIFIC-DISCOURSE fact ("who did what in THIS text"),
which a commonsense KG structurally lacks and plausibility cannot supply. This is the WINOGRAD core.

TWO OWNER-DRIVEN CORRECTIONS (leading with biology + drilling past the first negative paid off):
  * I nearly filed "fix the parser" as the #1 next problem — the cross-domain GAP test proved it wrong (clean parse ⇒
    still below chance). The wall is SEMANTIC, not parse-quality.
  * The obvious "add a world-knowledge KG" move is MEASURED DEAD (87% coverage, 2.8% discrimination) — the knowledge
    needed is this-discourse-specific, not general. Winograd pre-LLM ceiling confirms: no fully-automatic static-KG
    system cracked WSC-273 (the one full-set 57% used LIVE web search — not admissible).

A MEASURED POSITIVE FOUND WHILE DRILLING "any more optimizations?" (exp_coref_pool_cleanup_v1, adjacency #4, separate
lever): the candidate pool (mean ~39 vs the brain's ~4-entity focus) is polluted with mis-extracted FIRST/SECOND-PERSON
clusters ("I"/"we"/"my") the agreement filter wrongly admits — they cause 13.3% of resolver errors. Dropping them lifts
full accuracy 0.775 [0.730,0.816] -> 0.797 [0.754,0.836], +0.022 CI-SEPARATED [+0.007,+0.040]; the info-free random-drop
twin LOSES (0.756, beaten +0.041). Brain-foundational (the brain never tracks a first-person speaker as a 3rd-person
referent — a person-feature agreement fix). READY FOR STRATEGY TO LAND.

HONEST CAVEATS (withdraw first if wrong): the residual is n=205 (CIs honest but wide, half-widths ~0.03-0.07); the
negative rests on the prior failing to beat its 20-shuffle twin (robust) + the cross-domain confirmation, not a tight
point estimate. The fine-distance 37.6% oracle is real but ungateable — not a usable win. A slice (specific
interpersonal world-facts) is a genuine no-LLM bound, not proven irreducible in principle (Sharma et al. solved some
WSC with HAND-BUILT facts).

KEY REALIZATIONS: (1) the info-free twin — not likelihood-only (0/205 by construction) — is the meaningful floor; any
perturbation "beats" a definitionally-zero baseline. (2) When a mechanism fails, test the DIAGNOSIS on a domain where
the suspected cause is absent (GAP) BEFORE committing to "fix component X" — it caught my wrong parse-quality diagnosis.
(3) The residual is anti-typical by construction, so every general cue is anti-predictive — one structural reason for six
identical failures. (4) "Measure the oracle ceiling FIRST" (before building fusion) caught the coherence prior AND the
KB cue as near-chance, saving wasted builds. (5) A measured limitation + a control is fix-drivable; a flagged gap is not.

AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT.md, coref two-term-Bayes sub-claim ~line 214): the residual is NOT
coherence-prior-decisive — it is the ANTI-TYPICAL Winograd core, a SEMANTIC/world-knowledge bound (not coherence-prior,
not parse, not static-KG). The brain uses distributional semantics (ATL PDP hub — our 12-dim grounded space is the p1
gap; a symbolic KG is not implementation-faithful) + a situation model built by reading. The ~0.78 pronoun-coref ceiling
is REAL for a glass-box no-LLM structural resolver; the residual is a defer-and-flag case (the parent's Track B entropy
abstain), not a resolve case.

PROPOSED hdlab (strategy lands; I did not write hdlab/): do NOT land a coherence prior, a fine-distance override, a
structural-proxy binder, OR a static-KG plausibility cue (all six measured dead). DO land POOL CLEANUP (+2.2, ready).
Real residual levers = separate follow-on problems: (a) the SITUATION MODEL accumulating specific-discourse entity facts
+ reasoning (Garrod-Sanford RESOLUTION; the n400/situation-model program); (b) richer DISTRIBUTIONAL semantics (p1);
(c) mention-cache full spans + entity type -> name unification. NOT a static commonsense KG.

FILES: experiments/{exp_coref_coherence_next_mention_prior_v1 (incl. brain_faithful_cue_binding arm),
exp_coref_residual_crossdomain_gap_v1, exp_coref_residual_world_knowledge_ceiling_v1, exp_coref_pool_cleanup_v1}.py;
verification/test_coref_coherence_next_mention_prior.py (11/11); notes/problems/the_reader_has_no_coherence_next_mention_prior/
{SOLVED.md, research_intrasentential_binding_mechanism_2026-08-29.md, research_world_knowledge_for_reference_2026-08-29.md}.
hdlab/ UNTOUCHED.

TLDR (plain language): The reader still misses ~1-in-5 of the genuinely hard "who is she?" cases. The brief guessed a
MEANING step (guess who the story talks about next) would fix them — I built it exactly as the brain does and measured
it does no better than a scrambled copy of itself. I then tried every brain-faithful alternative (finer word-distance,
the brain's grammar-cue mechanism, world-knowledge from a 1.2M-fact knowledge base) and tested on clean modern text to
rule out our noisy old-book parser — all dead. The reason: these hard cases are defined as the ones where the OBVIOUS
answer is wrong, so any "typical answer" method points the wrong way by design. They need specific knowledge of who-did-
what in THAT exact passage — which our no-outside-AI reader gets only from a richer memory of the story it's reading
(a separate build), not from a fixed fact-book (measured: the fact-book connects everything but can't pick the right
one). ALONG THE WAY I found a real, clean fix worth +2 points: the reader was wrongly treating "I"/"we" (the narrator)
as candidates for "he"/"she" — removing them helps, with clean statistics. QUESTIONS: one label call — I marked this
REFUTED (the brief's mechanism is the wrong fix) not SOLVED; a rigorous negative is a full pass either way. NEXT: land
the +2 pool-cleanup fix; open the situation-model problem as the residual's real lever.
═══════════════════════════════════════════════════════════════════════════════════════════════════
