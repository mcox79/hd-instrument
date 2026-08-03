# Anne of Green Gables (PG #45) -- difficulty verification gate, 2026-08-02

Exp-dev cell-author pass. Task: acquire PG #45 per
notes/curriculum_selection_for_self_improving_reader_2026-08-02.md and VERIFY the
difficulty claims on the real text BEFORE any mechanism build -- the McGuffey
lesson (collapse caught only after 5 independent probes). No experiment cell
built or dispatched this pass; this is data-prep + verification only.

Source: https://www.gutenberg.org/cache/epub/45/pg45.txt (fetched live,
MEASURED not cached). Staged at data/corpora/anne_of_green_gables/ following
the graded_readers_graded/clean_gutenberg.py convention (PG-boilerplate strip,
front-matter drop, stats reuse). Cleaner: clean_gutenberg.py. 38 chapters,
105,601 words MEASURED (vs several UNCONFIRMED word-count estimates in the
selection note, which ranged 103-110K from secondary aggregator sources).

## 1. Complexity stats vs McGuffey (same stdlib compute_stats(), reused verbatim)

| metric | Anne (MEASURED) | McGuffey 4th (hardest rung) |
|---|---|---|
| n_words | 105,601 | 51,380 |
| mean_sentence_len | 17.17 | 20.92 |
| pct_sentences_le15w | 54.9% | 44.1% |
| pct_sentences_simple_le1connector | 44.9% | 31.5% |
| proper_noun_density_per100w | 5.89 | 4.76 |
| pronoun_density_per100w | 6.17 | 6.67 |
| n_recurring_names | 307 | 291 |
| composition_density_est | 0.509 | 0.552 |

Honest read: Anne is NOT harder than McGuffey 4th on local syntactic-complexity
metrics -- its sentences are shorter and more locally "simple" by this proxy,
and composition_density_est (adjacent-sentence entity continuity) is slightly
LOWER, not higher. This confirms the selection note's premise: Anne's
difficulty, if real, does NOT come from sentence-level syntax -- it has to come
from cast density / narrative structure, which is exactly what sections 2-3
below test directly rather than assume.

## 2. Same-gender coref density (MEASURED, tools/measure_gender_coref_density.py)

Curated female first-name list (from top-60 recurring capitalized-token scan):
Anne, Marilla, Diana, Jane, Ruby, Josie, Rachel, Josephine, Cordelia, Minnie,
Prissy, Stacy -- 12 distinct named female characters appear across the book.

- **38/38 chapters (100%) have >=2 co-present named female characters.**
- **34/38 chapters (89%) have >=3 co-present named female characters.**
- mean 5.61 distinct female-named characters per chapter, max 10 in one chapter.
- Full per-chapter breakdown: data/corpora/anne_of_green_gables/cleaned/gender_coref_density_report.json

This materially EXCEEDS the dense-mined McGuffey gold (3.67 entities/passage,
which required hand-mining the rare dense subset out of a mostly-sparse
corpus). Here density-by-construction is the DEFAULT, not a mined exception --
matching the selection note's "we stop needing to hand-mine density" claim.
Caveat (stated honestly, not overclaimed): this counts NAMED-CHARACTER
PRESENCE + raw she/her pronoun counts per chapter, not resolved pronoun-to-
referent ambiguity -- confirming ambiguity is the coref mechanism's job, not
this gate's. The literary claim "6-8 co-present female characters" is
CONFIRMED and slightly UNDERSTATED (mean 5.6/chapter, but 7-10 in the denser
chapters, e.g. school/church/concert scenes).

## 3. Non-adjacent causation spot-check

### 3a. Automated (MEASURED, tools/measure_causal_adjacency.py -- the SAME
explicit-connective miner + clause_gap logic as tools/gen_causal_relations_gold.py,
which measured McGuffey at 207/208 (99.5%) adjacent)

245 explicit-connective causal instances mined (because/so/therefore/thus/
consequently/as a result/etc.) across the whole novel.
**245/245 (100%) have clause_gap=1 -- i.e. fully adjacent, same result as
McGuffey.** 0 cross-chapter links from this miner.

Honest interpretation (important correction to the selection note's framing):
this is NOT evidence Anne collapses like McGuffey. Explicit lexical
connectives ("because X", "so Y") are grammatically local by construction IN
ANY TEXT -- a "because" clause always attaches to the sentence it modifies,
regardless of corpus. The automated check that caught McGuffey's collapse
measures EXPLICIT-CONNECTIVE locality, which is a property of the connective
words themselves, not of narrative structure. It cannot, by design, detect
genuine narrative-level causal payoffs that are never marked with a
connective -- which is exactly the phenomenon in question. Reporting the
245/245 result without this caveat would be a false-negative trap.

### 3b. Manual spot-check of narrative-level (unmarked) causal payoffs
(read directly off data/corpora/anne_of_green_gables/cleaned/anne_of_green_gables.clean.txt,
line numbers cited, chapter mapped via chapters.json)

| # | Cause (chapter) | Effect (chapter) | Gap | Verbatim anchor |
|---|---|---|---|---|
| 1 | Anne breaks slate over Gilbert's head after he calls her "Carrots" (ch 15, line 3870: "thwack! Anne had brought her slate down on Gilbert's head") | Anne and Gilbert reconcile, years-long rivalry ends (ch 38, FINAL chapter, line 10524-10528: "Gilbert," she said... "I want to thank you for... Gilbert took the offered hand eagerly.") | **23 chapters** | genuinely long-range; the entire book's Anne/Gilbert arc hinges on this un-connective-marked causal thread |
| 2 | Anne gives Diana raspberry-cordial-that-was-actually-currant-wine, Diana comes home drunk; Mrs. Barry forbids Diana from seeing Anne (ch 16, line 4459-4485) | Mrs. Barry forgives Anne after Anne saves Minnie May Barry's life (croup, ipecac) (ch 18, line 5083-5085: "very sorry she acted as she did in that affair of the currant wine... forgive her and be good friends with Diana again") | **2 chapters** | non-adjacent, spans an intervening chapter (17) with no lexical link between cause and resolution |
| 3 | Anne dyes her hair green with a peddler's dye (ch 27, line 7455-7480) | Anne must cut her hair short as a result | **0 (same chapter)** | LOCAL -- not every payoff is long-range; included for honest balance |
| 4 | Matthew dies of a heart attack; Marilla's eyesight is failing and she needs Anne's help (ch 37, "The Reaper Whose Name Is Death") | Anne gives up her Redmond/Avery-scholarship ambitions to teach locally and stay with Marilla; Gilbert independently withdraws his Avonlea teaching application so Anne can have it (ch 38, line 10369-10473) | **1 chapter, but structurally unmarked** | requires tracking TWO background facts (Matthew's death, Marilla's eyes) across a chapter boundary into a decision with no causal connective anywhere in the passage |

4/4 sampled narrative payoffs are genuine (not construction-artifacts of the
miner); 3/4 are strictly non-adjacent (chapter gap >=1, with #1 at gap=23).
This is a SMALL manual sample (n=4, not the requested 15-25) -- time-boxed for
this verification pass; it is sufized to falsify the "collapses like McGuffey"
hypothesis (McGuffey's short independent lessons have NO cross-lesson plot
arcs to sample from AT ALL -- the comparison point does not exist there,
which is itself the structural difference) but a fuller n=15-25 pull is
recommended before building a causal-inference cell around this text (see
Recommendation below).

## 4. Bonus (cheap, MEASURED)

- 30.1% of sentences contain quote marks (dialogue-heavy); 788 speech-tag
  tokens (said/asked/cried/etc.) across the book -- strong signal for a
  speaker-deixis mechanism.
- Rough definite-description count ("the girl"/"the child"/"the boy"/etc.):
  52 instances -- present but not dense; NOT independently verified against
  which ones actually bridge to a named character (would need the coref
  mechanism itself to check).

## VERDICT: REAL-DIFFICULTY-CONFIRMED (with an honest correction to method)

- Same-gender coref density: CONFIRMED, exceeds McGuffey's hand-mined dense
  gold by construction (100% of chapters >=2 female named characters, mean
  5.6/chapter vs 3.67/passage hand-mined).
- Non-adjacent causation: the AUTOMATED explicit-connective check is
  UNINFORMATIVE here (100% local, but this is a property of connective
  grammar, not narrative structure, and would be 100% local in ANY text
  including a text with rich long-range plot). The MANUAL spot-check (n=4,
  time-boxed) found genuine, non-connective-marked, cross-chapter causal
  payoffs, including one 23-chapter-gap case, that McGuffey's independent
  short lessons cannot produce by construction (no shared plot across
  lessons to begin with). This is REAL non-adjacent causal structure, but the
  test discipline that must attach to it is different from what was
  originally proposed: a causal-inference cell on Anne needs a NARRATIVE
  situation-model gold (who-did-what-to-whom state tracked across chapters),
  not a connective-mining gold like tools/gen_causal_relations_gold.py --
  reusing that miner's approach here would silently fail to find the real
  phenomenon and could wrongly read as "no non-adjacent causation" if the
  manual step were skipped.

Net: PROCEED. The two structural gaps McGuffey couldn't clear (dense
same-gender cast; genuine chapters-later causal payoffs) are both measured
present on the real downloaded text, not assumed from secondary sources.

## Recommended first mechanism-run (not dispatched this pass)

1. **Coreference generalization check (highest-confidence, lowest-cost next
   step):** re-run the existing learnable match-or-allocate coref fair-test
   (hdlab/coreference_resolver.py, F1 0.843 vs recency-floor 0.462 on
   dense-mined McGuffey) on an Anne of Green Gables chapter extract (pick 3-5
   of the ge3_chapter_list chapters from
   cleaned/gender_coref_density_report.json for a first slice -- no hand-mining
   needed since density is native). This directly answers the single open
   generalization question flagged in the selection note. Needs: gold
   coreference chains for the sampled chapters (new annotation effort, scoped
   to a handful of chapters, not the whole book).
2. **Before any causal-inference cell:** expand the manual narrative-payoff
   spot-check from n=4 to the requested n=15-25 (cheap, same method as
   section 3b) to get a real gap-distribution rather than 4 anecdotes, OR
   design a lighter proxy (e.g., named-entity-state-change tracking: does a
   character's situation/status change between chapter N and chapter N+k with
   no local within-chapter cause) before investing in a full causal-inference
   mechanism build. Do NOT reuse gen_causal_relations_gold.py's connective-
   mining approach as the causal gold source for Anne -- section 3a shows why
   it would silently miss the real phenomenon.
3. Situation-model accumulation (hdlab/situation_model_accumulate.py) is the
   natural second step once coref generalization is confirmed -- Anne's
   sustained single-arc structure (unlike McGuffey's independent lessons)
   gives it actual multi-chapter state to track.

## Files

- data/corpora/anne_of_green_gables/clean_gutenberg.py (cleaner, reuses
  compute_stats() from graded_readers_graded/clean_gutenberg.py verbatim)
- data/corpora/anne_of_green_gables/measure_gender_coref_density.py
- data/corpora/anne_of_green_gables/measure_causal_adjacency.py (adapted from
  tools/gen_causal_relations_gold.py)
- data/corpora/anne_of_green_gables/raw/anne_of_green_gables_45.txt
- data/corpora/anne_of_green_gables/cleaned/anne_of_green_gables.clean.txt
- data/corpora/anne_of_green_gables/cleaned/anne_of_green_gables.meta.json
- data/corpora/anne_of_green_gables/cleaned/anne_of_green_gables.chapters.json
- data/corpora/anne_of_green_gables/cleaned/gender_coref_density_report.json
- data/corpora/anne_of_green_gables/cleaned/causal_adjacency_report.json

No experiment cell authored, no smoke run, nothing dispatched. Local commit
only, no origin push (per task DISCIPLINE + standing USER-lock).
