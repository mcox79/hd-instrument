# RESEARCH — the brain-foundational lever for OBL/PP-attachment (Path A)

**Why this note (owner 2026-09-13):** the oracle-ceiling probe proved that fixing the BF attachment arm's
CORE-ARGUMENT heads (nom-UAS 0.58 -> 0.81) makes the role-occupancy win CI-separated on the all-BF stack
(+0.0156 CI[+0.004,+0.028]). The binding failure is OBL/PP-attachment (head-acc 0.439; 208 to-noun vs 153
to-verb errors). This note synthesizes the literature so the fix copies the brain's operation, not a
convenient hack.

## How the brain resolves PP/oblique attachment (the operation to copy)
PP-attachment ("saw the man WITH the telescope" — verb or noun host?) is resolved by CONSTRAINT SATISFACTION
integrating graded cues in parallel (MacDonald-Pearlmutter-Seidenberg 1994; Spivey-Knowlton & Sedivy 1995),
NOT a single rule:
1. **Verb argument-structure expectation / SUBCATEGORIZATION** (Boland; Tanenhaus & Trueswell): a verb expects
   specific prepositions for its oblique arguments (rely ON, put ON, give TO). If the verb subcategorizes for
   the preposition, the PP attaches to the verb. This is verb VALENCE — the SAME frame knowledge the role
   occupancy factor uses (one structure, many functions).
2. **Lexical association** (Hindle & Rooth 1993): P(prep|verb) vs P(prep|noun) as a log-likelihood ratio,
   bootstrapped from unambiguous PPs. ALREADY LANDED in the arm (`SentenceCues.pp`) — but seeded from ~12k
   UD-EWT train sentences, so SPARSE (2231 verb-prep / 3580 noun-prep pairs) -> most test triples back off to
   the prep marginal -> weak. Sparsity is the diagnosed failure.
3. **SEMANTIC-CLASS backoff** (Resnik 1996; Stetina & Nagao 1997; Collins & Brooks 1995 backed-off model): back
   the association off from the LEMMA to the semantic CLASS of the verb/noun (and of the prep-object) — this is
   what beats sparsity and is the single biggest accuracy lever in the classic literature (Stetina-Nagao ~88%
   with WordNet classes vs ~80% lexical-only). BF because the brain generalizes over semantic classes, not word
   forms. Our substrate HAS the classes: the distributional meaning channel (PPMI+SVD phi) and the reading-
   induced categories (`lexical_categories`) — cluster verbs/nouns and count CLASS-level prep associations.
4. **Prep-OBJECT semantics** (Collins-Brooks quadruple v,n1,p,n2): "with the TELESCOPE" (instrument -> verb) vs
   "with the HAT" (attribute -> noun). The object of the preposition disambiguates; include n2's class.
5. **Locality / Late Closure default** (Frazier): attach low/local unless lexical-semantic evidence overrides —
   the arm has a locality cue.

## The refined BF lever (strongest first), for the attachment arm's core-argument arcs
- **A. Semantic-class-backed prep association (Resnik/Stetina-Nagao).** Extend `pp_assoc_from_reading` to count
  associations at the level of the verb/noun's INDUCED CATEGORY (and the prep-object's category), with lemma ->
  class -> prep-marginal backoff (Collins-Brooks). This directly fixes the sparsity that makes the landed
  Hindle-Rooth cue weak. HIGHEST leverage; uses organs we already have (lexical_categories / distributional phi).
- **B. Verb-subcategorization prepositions.** Add P(prep | verb) from the verb-frame counts (the lemma_frames
  structure), so a verb that subcategorizes a preposition pulls its PP. Cheap; reuses the frame organ.
- **C. Data scaling.** Seed A/B from a LARGE modern corpus (simplewiki_clean_v1.txt, 251MB, modern) via the BF
  tagger — the brain learns these from massive exposure. Necessary complement to A (class counts need volume).
- **D. Prep-object class (n2).** Add the prep-object's category to the association key (Collins-Brooks) — the
  instrument-vs-attribute disambiguator.

## Scope reality
Raising core-arg nom-UAS from 0.58 to the ~0.81 the oracle needs is a LARGE parser improvement (the OBL host
is wrong 56% of the time). A single lever (even semantic-class association) will not fully close it; this is a
multi-lever attachment-arm project (briefs pri 15-17). The right increment to prove NOW: build lever A+C
(semantic-class-backed association from a large corpus), inject it, and measure whether OBL/core-arg UAS moves
up CI-separated — a proven step toward the oracle ceiling, with the remaining levers (B, D) named.

## MEASURED (2026-09-13): lever C (data-scaling the lexical cue) is REFUTED
Rebuilt the Hindle-Rooth associations from 149,744 Simple-Wiki sentences (12x the UD-EWT-train seed) via the BF
tagger, merged into the arm, re-measured on UD-EWT test 700:
- OBL head-acc: floor 0.4429 -> enriched 0.4480 (+0.0051, CI[-0.004,+0.015] -- NOT CI-separated); enriched ~= twin.
- core-arg head-acc: 0.6348 -> 0.6373 (+0.0025, CI incl 0).
So MORE lexical association data barely moves OBL attachment -> SPARSITY IS NOT THE BINDING CONSTRAINT. The
landed pp cue's LEARNED VALIDITY caps its influence on the decode (even the 4k-line smoke showed enriched==twin:
the cue rarely flips an arc regardless of the association values). => data-scaling the lexical cue is a located
negative. The remaining BF levers are STRUCTURAL, not more data:
- **Lever A (semantic-class backoff)** still the strongest candidate, but it requires re-keying the pp cue
  lemma->class and changing pp_lr (a change to hdlab/attachment_arm.py's cue architecture) -- the attachment-arm
  problem (pri 15-17), not a role-side prototype.
- **Cue re-weighting / decode leverage:** the pp cue's contribution may be too small in the competition or not
  propagated by the incremental decode; raising its validity or its role in the arc score is a parser-internal
  change. Also attachment-arm scope.
=> Path A's tractable role-side lever is exhausted; reaching the oracle's 0.81 core-arg UAS is a multi-lever
attachment-arm rebuild (class-backoff + verb-subcat + prep-object + cue-weighting), a distinct hard problem.

## Controls for any PP lever (so it is a real BF win, not a fit)
Floor = the arm as-is (landed lexical Hindle-Rooth). Twin = shuffled associations (class labels permuted).
Gate = OBL/core-arg head-acc up CI-separated, no regress on non-PP relations, on UD-EWT test; then re-run the
oracle/occupancy chain to confirm the all-BF role win appears.
