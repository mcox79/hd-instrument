# Eval growth: cross-span multi-candidate causal attribution (DRAFT, Director-verify-gated)

**Status: DRAFT. Nothing in this note or the companion jsonl is gold_verified. All items require Director review before use in any cell.**

## HEADLINE

Mined the 3 available cleaned public-domain novels (`tom_sawyer`, `little_women`, `anne_of_green_gables`) for scenes matching the multi_candidate_causal_attribution schema (cross-span, >=2 agent-caused candidates, recency- and surface-valence-defeating). Found and drafted **4 new verified-verbatim items** (`grapp_mcca_006..009`), bringing the item-level pool for this eval from n=4 to n=8. This is well short of the 16-24 target — the honest finding is that genuinely discriminating whodunit-style scenes (hidden true cause + a textually salient wrong candidate + confirmed resolution) are RARE in this corpus; most blame/causation scenes in these novels are single-agent-obvious (no real distractor) or resolve immediately (no cross-span gap). I did not manufacture items to hit the target count.

## Source and method

- Sources: `data/corpora/tom_sawyer/cleaned/tom_sawyer.clean.txt`, `data/corpora/anne_of_green_gables/cleaned/anne_of_green_gables.clean.txt` (public-domain Gutenberg texts, cleaned/re-flowed, same corpus family as the 4 existing v1 items).
- Method: manual literary recall of known multi-agent blame/misattribution scenes in these novels, then `grep -n` to locate exact line numbers in the cleaned corpus files, then a purpose-built substring-guard script (`verify_spans.py`, run against the draft jsonl) that reconstructs the file as a single space-joined string and confirms each `text` field is a literal substring at (or immediately around) the claimed `line_range`. All 12 spans across the 4 new items (`true_blocker_span`, `distractor_span`, `query_span` x 4 items) verified `VERBATIM-OK`.
- No paraphrase. No synthesized text. No LLM-authored narrative content — every span is a grep-located, line-numbered excerpt from the on-disk cleaned corpus, in the same `{line_range, text}` schema as the existing v1 items.

## New items (summary)

| id | novel / ch | true blocker | distractor (recency trap) | cross-span gap |
|---|---|---|---|---|
| grapp_mcca_006 | anne_of_green_gables ch14 | Marilla (brooch caught in her own shawl, forgotten) | Anne (last confirmed handler; later gives a false confession) | true-cause reveal is ~230 lines AFTER the query point |
| grapp_mcca_007 | anne_of_green_gables ch16 | Marilla (stored the cordial bottle in the wrong place) | Anne (accused by Mrs. Barry, physically served the drink) | true-cause reveal is ~13 lines after query, but query itself sits ~140 lines after the causal event (bottle mix-up happened off-page before the tea) |
| grapp_mcca_008 | tom_sawyer ch20 | Alfred Temple (poured ink on Tom's spelling-book out of jealousy) | Tom (sincerely but wrongly self-blames) | causal event is ~200 lines BEFORE the query/distractor |
| grapp_mcca_009 | tom_sawyer ch20 | Becky Thatcher (accidentally tore the anatomy-book page) | Tom (reputational suspect: just flogged for a different book-related offense moments earlier) | causal event is ~80 lines before the query |

## Baseline-defeat stats (measured, not asserted)

- **Recency-wrong rate: 4/4 (100%)**. In every new item, the agent most recently and saliently associated with the outcome at the query point is NOT the true cause. Verified by construction (each item's `recency_baseline_prediction` names the wrong agent, matching the pattern already used in v1's 4 items) — this is a design-time claim, not yet measured against a running recency-baseline cell. **Director should run the actual recency-baseline cell over the n=8 combined pool to get a real measured number rather than trusting the by-construction claim.**
- **Surface-valence-nonseparating: qualitative, not yet quantified.** In all 4 items, both the true-blocker span and the distractor span are low-intensity, matter-of-fact register (a bottle mix-up, a punished student, a confession) — neither carries strong sentiment/valence tokens that would let a lexicon-based valence scorer discriminate them. I have NOT run an actual surface-valence classifier against these spans; this is an eyeball judgment. Flagging for Director/exp_dev to run the real check before treating this as passed.
- **True-blocker position varies**: 006/007 true blocker sits BEFORE the distractor in text order (Marilla's habitual brooch-wearing / bottle mix-up predates the accusation), while 008/009 true blocker sits BEFORE the query but the distractor is closer to the query (Alfred's ink-pour and Becky's tear both precede Tom's self-blame/punishment). So position is not uniformly first-or-last across the new set, but note items 006/007 share the SAME true_blocker_span (see caveat below) and 008/009 share the SAME distractor_span — this reduces the effective independence of the n=8 pool, flagged explicitly for Director.

## Honest yield and caveats (read before using)

1. **Span reuse across items**: `grapp_mcca_006` and `grapp_mcca_007` share an identical `true_blocker_span` (the Marilla-storage-mistake passage explains BOTH the missing brooch and the currant-wine mix-up — Marilla's carelessness is a real double-cause in the source text, not an artifact of my mining). `grapp_mcca_008` and `grapp_mcca_009` share an identical `distractor_span` (Tom's whipping passage is the salient recency-trap for two different, adjacent chapter-20 mysteries). This mirrors a precedent already present in v1 (`grapp_mcca_004` / `grapp_irony_001` reuse the same citation for a different judgment dimension), but four-way reuse across only 4 new items is a bigger fraction of the new pool. **Director should decide**: keep all 4 as independent selection tasks (the query/goal/task framing differs even where a span is shared), or treat 006/007 as one item-family and 008/009 as another for power-counting purposes (effectively n=6 independent spans, not n=8).
2. **Rarity finding**: I searched Tom Sawyer, Little Women, and Anne of Green Gables narrative content (not the McGuffey Readers, which are short pedagogical vignettes with essentially no multi-agent whodunit structure, and not Wizard of Oz / Alice in Wonderland, which I scanned for candidates but found no scene with BOTH a genuinely competing plausible-agent distractor AND a confirmed, textually-resolved true cause — Wizard of Oz's causal scenes are single-agent-obvious, and Alice's "Who Stole the Tarts" trial is deliberately never resolved in-text, so it cannot supply a gold true_blocker). I did not exhaustively re-read all three source novels line by line (that would take many more hours); I worked from recalled scene locations and grep-confirmed them. **There may be more valid scenes I did not find** — this is a partial mining pass, not an exhaustive one.
3. **`goal_owner` framing for 007/008 is slightly non-standard** relative to v1 (dual epistemic goal-owners) — flagged in-line in the jsonl `verify_flag` fields for Director judgment call.
4. Nothing here changes power math automatically: even n=8 is still small for binomial rejection of random at reasonable alpha (8/8 needed for p<0.01 two-sided against p=0.5; 7/8 gives p~0.07). Director/exp_dev should treat this as a step toward — not yet at — a fully powered coherence-selector test; recommend continuing to grow toward the original 16-24 target from OTHER sources (e.g. mining `graded_readers_graded`, `race`, `onestop` corpora, or wizard_of_oz's full text more carefully, or considering non-verbatim-but-still-real newspaper/primary-source public-domain narrative) in a follow-up pass, rather than treating this DRAFT as eval-complete.

## Verification artifact

`verify_spans.py` (ad hoc script, written to scratchpad, run against the draft — not committed to the repo) confirmed all 12 spans (4 items x 3 span fields) are verbatim substrings of the on-disk cleaned corpus files at (or within 1 line of) the claimed `line_range`. Re-run command for Director:

```
python verify_spans.py data/eval_gold_mention_role_mcguffey_v1/gold_grounded_causal_crossspan_v2_DRAFT.jsonl
```

(script logic: joins each corpus file's lines with a single space, normalizes whitespace, and checks each `text` field is a literal substring — same reconstruction convention the v1 items already use for line-wrapped multi-line spans, confirmed by cross-checking `grapp_mcca_005`'s existing span against the same joined-file convention before use.)

## Cheap decisive test (for the Director / next cell)

Once Director-verifies these 4 items (sets `gold_verified: true`, promotes out of the `_DRAFT` filename), the cheap decisive test is: run the existing cross-span BINDING mechanism (that already recovered true blockers 0->3/4 on v1) against the combined n=8 pool and measure whether it still discriminates true-vs-distractor at a rate distinguishable from chance, now that distractors are DELIBERATELY constructed to defeat recency (all 8/8 items, v1+new, have `recency_baseline_correct: false`) and (qualitatively) surface valence. HARD-PASS: binding-mechanism recall_true > recall_distr by a margin that would clear binomial significance at n=8 (needs 7-8/8 correct on true, <=4/8 "correct" i.e. wrongly-picked on distr, roughly). HARD-FAIL: recall_true == recall_distr (repeats the v1 finding that binding recovers candidates but doesn't yet select — confirms a genuine coherence-selector capability gap rather than an artifact of n=4).

## Cross-thread synthesis

This is a direct follow-on to the `multi_candidate_causal_attribution` capability row currently blocked at n=4 (per the task brief: cross-span binding shown to recover true blockers 0->3/4 but recall_distr also 0.75, meaning selection — not just recall — is the open gap). This note does not resolve that gap; it only grows the evidence base needed to test it.

## Substrate-product implications

A powered, discriminating coherence-selection eval is a prerequisite for any product claim about "the substrate can tell WHO is actually to blame/responsible," which is a real everyday reading-comprehension task (whodunit narrative, blame attribution, misdirection). Until n is powered, any exp_dev cell result on this capability is anecdote, not evidence — this growth pass is infrastructure, not itself a capability claim.

## Citations (verified count)

4 verbatim on-disk source citations (all internal to this repo's corpora, all script-verified): `tom_sawyer.clean.txt` lines 5081-5083 / 5244-5246 / 5287-5288 / 5299-5301 / 5323; `anne_of_green_gables.clean.txt` lines 3296 / 3325-3326 / 4442-4443 / 4449-4450 / 4462-4464. Zero external/off-platform citations (per query-privacy discipline — this task is entirely local corpus mining, no external search was needed or performed).
