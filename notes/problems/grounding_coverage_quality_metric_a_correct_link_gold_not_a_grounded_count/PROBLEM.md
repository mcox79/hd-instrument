---
priority: 9
slug: grounding_coverage_quality_metric_a_correct_link_gold_not_a_grounded_count
status: OPEN
review:
review_text:
---

# PROBLEM: the grounding loop is scored by a COUNT (`n_grounded` = how many tokens got a grounding link), which cannot tell a CORRECT link from a wrong one — so a meaning-fusion change that improves link QUALITY is invisible, and one that grounds MORE tokens WRONG looks like a win. Build an independent-gold CORRECT-LINK quality metric (does the grounded referent/sense match a held-out gold meaning?) and wire it as a board instrument, so meaning-fusion / grounded-dominant-sense gains are scorable on QUALITY, not quantity. A rigorous located negative (no independent gold is affordably constructible → name the ceiling) is a full pass. Glass-box, NO external LLM at inference.

**slug:** `grounding_coverage_quality_metric_a_correct_link_gold_not_a_grounded_count` — **opened:** 2026-09-11 by strategy. **status:** OPEN. Named by `measure_end_to_end_whether_the_meaning_fusion_lifts_live_grounding_coverage` (#2): the `n_grounded` COUNT is decision-quality-blind. This is a MEASUREMENT-INSTRUMENT problem (the reader's own metric may reward frequency, not meaning) — it unblocks the whole meaning-fusion line by making its quality gains visible. Glass-box, NO external LLM at inference.

> ## SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** — the mission is the most brain-faithful substrate, not the fastest green check.
> **THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure / circuit and the computation it performs, and replicate that OPERATION as exactly as you can — the FIRST move, not a tiebreaker.
> **YOU ARE ENABLED — AND EXPECTED — TO EXPLORE FAR AND WIDE.** Read the neuroscience; cross domains; if a MORE brain-foundational structure than this brief names emerges, submit THAT instead (say what is incompatible and why yours is more faithful).
> **A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
> **"CONVERGED" HAS A HIGH BAR.** Claim it only when you have (a) identified how the brain performs this computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL, and spaCy/GLUCOSE/MAVEN + any off-the-shelf parser/dataset/model are NOT brain-foundational — never reach for a convenient/easy tool without careful consideration** (a vetted static offline FOUNDATION asset / open MODERN gold is admissible SUPPLY; an external tool AT INFERENCE or a fitted/convenient stand-in is a DEFECT that BLOCKS).
> **🧩 ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS (owner 2026-09-10):** this is an INSTRUMENT (a board dimension + a gold), NOT an organ — do not mint an organ; reuse the grounding loop + an admissible modern gold. Consult `BRAIN_STRUCTURE_CONSOLIDATION_AUDIT.md` before adding anything.
> **A rigorous negative is a PASS** — but only if what failed was the brain's actual mechanism, faithfully built.
> **REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale.

> ## BRAIN-FOUNDATIONAL CHECKLIST (work through IN ORDER; the solution is not done until every box holds)
> 1. **OPEN — what is the brain-relevant quantity to MEASURE?** Comprehension is CORRECT reference/sense resolution, not the NUMBER of tokens touched. The metric must score whether the grounded referent/sense MATCHES a held-out gold meaning (WiC sense / WSD supersense / coref chain), the way a comprehension test scores understanding — NOT how many links fired. Mark the gold source admissible (open MODERN gold / offline foundation).
> 2. **REUSE + INSTRUMENT-NOT-ORGAN** — REUSE the live grounding loop (`reading_grounding_loop` / `substrate` / `gap_driven_reader`) as the thing measured, and an ADMISSIBLE modern gold (WiC / a WSD/WordNet supersense gold / GUM coref) as truth. Build a `board_grounding_quality_dimension()`; do NOT build a new organ.
> 3. **GENERALIZE — does it need to, and how?** The quality metric should score BOTH the sense-assignment decision (grounded-dominant sense correct?) and the referent link (grounded to the right entity?), so any meaning-fusion change is scored on the decision it affects.
> 4. **HIT A WALL → GO DEEPER, don't stop.** If no independent gold is affordably constructible for a decision, say so WITH the reason (which decision, why no gold) — a rigorous located negative naming the un-measurable slice is a pass.
> 5. **OPTIMIZE BY EXACT REPLICATION** — the metric copies the comprehension-test logic (match the resolved meaning to gold); sweep nothing that changes truth. Report CI half-width + the null (a scrambled-link twin scores at chance).
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM** — show the metric MOVES when meaning-fusion improves link quality and is FLAT when only the count grows (the whole point: separate quality from quantity). Confirm it does not silently depend on the very fusion it scores (no ground-by-X-grade-by-X).
> 7. **ADJACENT COMPONENTS.** Distinguish this from the existing eval folders (`eval_bank_too_small`, `the_own_metric_may_reward_frequency_not_meaning`, `meaning_read_out_untested_on_the_own_metric`) — those address bank SIZE / metric-VALIDITY; this builds the CORRECT-LINK COVERAGE instrument. Cite them; do not duplicate.
> 8. **COMPLETION BAR.** A `board_grounding_quality_dimension` scoring correct-link quality on independent gold, that MOVES on a quality gain + is FLAT on a count-only gain (with a scrambled-link null at chance, CI-separated) — a COMPLETE instrument — OR a numbered located negative naming exactly which grounding decision has no affordable independent gold.
>
> **(PHASE DIAGRAM.)** The instrument's operating point — gold subset, coverage stratum, abstain threshold — is FREE to SWEEP; a wall "at this config" = move the operating point, not a ceiling.
> **(FULL-STACK UPSTREAM.)** Build the instrument AND demonstrate it on a real meaning-fusion change (grounded-dominant sense / per-spoke fusion): the quality dim moves, the count dim doesn't — proving the instrument is what the meaning-fusion line was missing.

## 1. THE PROBLEM IN PLAIN LANGUAGE
Right now, when the reader "grounds" a word (links it to a meaning), we score how MANY words it managed to link — but not whether those links are RIGHT. That is like grading reading comprehension by counting how many questions a student answered, ignoring whether the answers are correct. So a change that makes the meanings more ACCURATE looks like nothing changed, and a change that links more words to the WRONG meaning looks like an improvement. This problem builds an honest score: for a held-out set of words with known correct meanings, does the reader's grounded meaning MATCH? That single instrument is what makes every future "better meaning" change actually measurable.

## 2. WHY THIS ONE — the deep root, under the HARD 100%-BF gate
The meaning-fusion line (the project's Phase-1 bottleneck) keeps producing changes whose value is invisible because the live metric is a COUNT. Until quality is scorable, we cannot tell a real comprehension gain from a coverage-inflating regression — the owner's own caution ("the own metric may reward frequency not meaning"). It is cheap relative to its leverage: it unblocks scoring for the entire grounding/meaning program.

## 3. MEASURED vs INFERRED
- **MEASURED (on disk):** the grounding loop reports `n_grounded` (a count); the meaning-fusion SOLVED (`measure_end_to_end…`) explicitly flags that the count cannot show a quality gain and that a correct-link metric is the missing instrument; WiC / WordNet-supersense / GUM-coref golds exist as admissible modern truth.
- **INFERRED (to prove or refute WITH A NUMBER):** that a correct-link quality metric on independent gold MOVES on a genuine quality gain and is FLAT on a count-only change, with a scrambled-link null at chance. Do NOT assume every grounding decision has an affordable gold — where none exists, name it (located negative).

## 4. ALREADY TRIED / DO NOT REDO
- Do NOT re-file bank-size or metric-validity concerns — those are the existing `eval_bank_too_small` / `the_own_metric_may_reward_frequency_not_meaning` / `meaning_read_out_untested_on_the_own_metric` folders; cite them, build the correct-link COVERAGE instrument instead.
- Do NOT ground-by-X and grade-by-X (a metric that reads the same signal it scores is circular) — the gold must be INDEPENDENT of the fusion.
- Do NOT build a new organ — this is a board dimension + a gold over the existing grounding loop.
- Barred: spaCy / any external LLM at inference; a fitted metric.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Understand ALL existing organs + evals first: `python tools/substrate_map.py`, skim `hdlab/` (`reading_grounding_loop`, `substrate`, `gap_driven_reader`, `underspecified_sense_reader`, `meaning_foundation`) + the board `experiments/exp_situation_model_qa_modern_v1.py` (how `board_coarse_sense_dimension` / `board_wic_dimension` score sense on modern gold — the pattern to reuse). Read IN FULL: `notes/problems/measure_end_to_end_whether_the_meaning_fusion_lifts_live_grounding_coverage/SOLVED.md` (esp. #2), and the three eval folders named in §4. Read `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (meaning channel). Grade MODERN gold only (WiC / WordNet supersense / GUM; 19c banned). CAP local runs below all cores (`OMP_NUM_THREADS=4 …`); heavy runs go remote. Report CI half-width + the null p95.

## 6. THE BAR (can-fail; a rigorous located-negative naming the exact ceiling WITH a number is a full pass)
Deliver a `board_grounding_quality_dimension()` (or an equivalent instrument) that scores CORRECT-LINK quality on independent MODERN gold (grounded referent/sense matches held-out truth), and DEMONSTRATE on a real meaning-fusion change that: (a) the QUALITY dim MOVES when link quality improves CI-separated; (b) it is FLAT when only `n_grounded` grows (quantity without quality); (c) a scrambled-link twin scores at chance. OR a rigorous LOCATED NEGATIVE naming exactly which grounding decision has no affordable independent gold (with the reason). INVARIANT: the gold is INDEPENDENT of the fusion (no circular ground-by-X-grade-by-X); no external tool/LLM at inference; modern gold only.

## 7. FILES AND ENTRY POINTS
`hdlab/reading_grounding_loop.py`, `hdlab/substrate.py`, `hdlab/gap_driven_reader.py` (the grounding loop measured); `hdlab/underspecified_sense_reader.py`, `hdlab/meaning_foundation*` (the sense read scored); the board `experiments/exp_situation_model_qa_modern_v1.py` (`board_coarse_sense_dimension` / `board_wic_dimension` = the scoring pattern to reuse; register a new `grounding_quality` arm); `notes/problems/measure_end_to_end_whether_the_meaning_fusion_lifts_live_grounding_coverage/SOLVED.md`; `notes/BRAIN_FOUNDATIONAL_AUDIT.md`.

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT duplicate the eval-bank-size / metric-validity folders. Do NOT use spaCy / any external LLM at inference. Do NOT build a circular metric that reads the fusion it scores. Do NOT grade on 19c corpora (modern gold only). Do NOT claim "converged" on engineering variations; the bar is a quality dim that moves-on-quality / flat-on-count with a null at chance, or a numbered located negative.
