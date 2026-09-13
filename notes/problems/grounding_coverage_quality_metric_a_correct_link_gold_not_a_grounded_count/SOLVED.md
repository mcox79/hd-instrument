---
problem: grounding_coverage_quality_metric_a_correct_link_gold_not_a_grounded_count
status: SOLVED
bar: "Deliver a `board_grounding_quality_dimension()` (or an equivalent instrument) that scores CORRECT-LINK quality on independent MODERN gold (grounded referent/sense matches held-out truth), and DEMONSTRATE on a real meaning-fusion change that: (a) the QUALITY dim MOVES when link quality improves CI-separated; (b) it is FLAT when only `n_grounded` grows (quantity without quality); (c) a scrambled-link twin scores at chance. OR a rigorous LOCATED NEGATIVE naming exactly which grounding decision has no affordable independent gold (with the reason). INVARIANT: the gold is INDEPENDENT of the fusion (no circular ground-by-X-grade-by-X); no external tool/LLM at inference; modern gold only."
result: "COMPLETE 2x2 SEPARATION (n=247 scorable queries, n=4235 grounding targets, live reading-grounding loop, full curriculum + 1M-line grown SEQ store). (a) MOVES-on-quality: FUSED - INCUMBENT correct-link MRR@0.5 = +0.3612 CI[0.2977,0.4353] CI-sep (fused 0.3823 vs incumbent bag-cosine 0.0211). (b) FLAT-on-count: the SDT false-alarm knob FA 0.01->0.40 raises the accepted count +0.319 frac CI[0.3053,0.3332] CI-sep (n_accepted targets 2154->3505, +63%) while the correct-link ranking-MRR diff = 0.0000 EXACTLY (FA-invariant by construction; proven byte-identical order+z_top on the live ranker, V1) and correct-rate-among-accepted MONOTONICALLY DECLINES 0.235->0.180 as the count grows (more links, not more correct). (c) scrambled-link TWIN at chance MRR 0.013 (FUSED-TWIN +0.3694 CI[0.301,0.4429]). Smoke (n=87) agrees: MOVES +0.3512 CI[0.235,0.455], count +0.400, Qflat 0.0, twin 0.018. PLUS a rigorous LOCATED NEGATIVE on the referent-link-to-ENTITY slice: the reading-grounding loop makes NO mention->entity/coref decision (0 entity/coref/mention/pronoun tokens across reading_grounding_loop.py's 3022 lines), so GUM/LitBank coref gold (present + parseable on disk) has no decision variable to score in THIS organ -> routes to hdlab/coreference_resolver.py (NEEDS_ADAPTER)."
floor: "INCUMBENT bag-cosine read (the pre-landing live sense-assignment read) correct-link MRR@0.5 = 0.0211 (n=247); it is the strongest non-trivial floor (the loop's own prior read). The COUNT metric itself is the count-side floor: n_grounded moves +63% (2154->3505 accepted targets) under the FA knob while correctness does not -- the exact quality-blindness the instrument exposes."
controls: "(1) scrambled-link TWIN (channel evidence taken from a DIFFERENT query word) at chance MRR 0.013 -- excludes base-rate/lucky-pool. (2) FA-INVARIANCE IDENTITY (V1): the ranked candidate order and z_top are byte-identical across FA=0.01 vs 0.40 on the live ranker; only the accept verdict differs (FA_hi accepts a superset) -- excludes 'the quality metric secretly tracks the accept threshold' (it is an identity, not an underpowered null). (3) COUNT-OUTRUNS-CORRECT (V3): correct-rate-among-accepted does not rise (declines) as FA raises the count -- excludes 'more links = more correct'. (4) GROUNDED-ONLY ablation (landed instrument). INDEPENDENCE: gold = SimLex-999 + SimVerb-3500 human similarity, which is WordNet-independent AND fusion-independent -> no circular ground-by-X-grade-by-X. No external tool/LLM at inference; modern gold only."
files_changed: "experiments/exp_grounding_quality_flat_on_count_v1.py (the FLAT-on-count demonstration: FA-sweep count knob vs FA-invariant correct-link quality, the 2x2), verification/test_grounding_quality_flat_on_count.py (scaffold-free witness, 3/3: FA-invariance of the live ranking, smoke 2x2 verdict, count-outruns-correct), data/grounding_quality_flat_on_count_v1/metrics_full.json + metrics_smoke.json. REUSES (does not rebuild) the landed sense-assignment half: experiments/exp_board_grounding_coverage_quality_v1.py + the live board arm `grounding_coverage_quality` in exp_situation_model_qa_modern_v1.run. NO hdlab/ modified (Q111 -- hdlab wire spec in the body)."
reverify: ".venv/Scripts/python.exe verification/test_grounding_quality_flat_on_count.py"
---

# The grounding coverage-QUALITY instrument now has BOTH halves: MOVES-on-quality (landed) AND the missing FLAT-on-count (here) -- so the correct-link quality dim provably measures quality, not quantity, and cannot be gamed by grounding more tokens wrongly. The requested referent-link-to-ENTITY half is a rigorous LOCATED NEGATIVE (the loop makes no entity decision).

## What the brief asked, and what was already done (STATUS UPDATE 2026-09-11)
The CORE sense-assignment quality instrument already existed (strategy-landed): `experiments/exp_board_grounding_coverage_quality_v1.py` -> the live board arm `grounding_coverage_quality` (in `exp_situation_model_qa_modern_v1.run`, lines 2580-2582, OUT of the headline aggregate). It scores the LIVE grounding decision (`FusedSenseRanker` over the loop's real ingest) against independent modern human-similarity gold and already showed (a) MOVES-on-quality and (c) twin-at-chance. The solver scope was NARROWED to three items: (a) the referent-link-to-ENTITY half (GUM coref gold), (b) the explicit FLAT-on-count demonstration, (c) POWER. This submission delivers all three.

## (b) THE FLAT-ON-COUNT DEMONSTRATION -- the missing half of the bar (the headline build)
The loop's grounding gate accepts a link iff the SDT familiarity standout `z_top >= criterion(n_cand)`, where `criterion = (1-FA)` quantile of `z_top` on an info-free iid null (Yonelinas 2002 recognition SDT; `FusedSenseRanker.criterion`). `FA = SDT_FALSE_ALARM` is a SWEPT precision knob. Raising FA LOWERS the criterion -> more links clear the gate -> `n_grounded` rises. **But FA never enters the RANKING (the argsort over the fused convergent-cue combination) or `z_top`, so link CORRECTNESS is untouched.** This is the brain-faithful count-only lever the strategy update named ("lower the SDT false-alarm rate").

THE 2x2 (full run, n=247 queries / n=4235 targets):

| | QUALITY dim (correct-link MRR@0.5) | COUNT dim (n_grounded / accepted) |
|---|---|---|
| **quality change** (incumbent -> FUSED, fixed FA) | **MOVES +0.3612 CI[0.298,0.435]** (0.021 -> 0.382) | not a count lever |
| **count-only change** (FUSED, FA 0.01 -> 0.40) | **FLAT: diff 0.0000** (FA-invariant identity) | **MOVES +0.319 CI[0.305,0.333]** (2154 -> 3505 accepted, +63%) |

- The FA sweep: accepted targets **2154 -> 2702 -> 2972 -> 3221 -> 3505** (monotone up, +63%), while correct-rate-among-accepted **0.235 -> 0.211 -> 0.189 -> 0.188 -> 0.180** (monotone DOWN). The count nearly doubles the grounded set; the fraction that is CORRECT falls. This IS "grounds MORE tokens WRONG looks like a win under the count," made numeric.
- The quality-ranking FLATNESS is not an underpowered null -- it is an **identity by construction** (V1 proves order + z_top are byte-identical across FA on the live ranker). That is the strongest possible form of "the quality metric cannot be gamed by the count knob."
- Twin (scrambled-link) at chance MRR **0.013**. Smoke (n=87) reproduces every conclusion.

## (a) THE REFERENT-LINK-TO-ENTITY HALF -- a rigorous LOCATED NEGATIVE (checklist-4 pass)
ENUMERATION (full-file grep + import-trace, not a keyword search): `hdlab/reading_grounding_loop.py` (3022 lines) contains **ZERO** occurrences of entity / coref / mention / pronoun / antecedent. It makes exactly two grounding decisions: (1) lexical SENSE-ASSIGNMENT (`canonicalize`/`canonicalize_fast`/`FusedSenseRanker.rank`: word -> word-sense anchor), and (2) perceptual VISUAL grounding (`use_referent` -> `sensorimotor_spoke.referent_vector`: a per-WORD DINOv2 photo centroid). The `use_referent` "referent" is PERCEPTUAL (word -> photo), **not** a discourse entity. `gap_driven_reader.py`/`substrate.py` import only the loop's own functions; neither imports any coref/entity organ.

So the loop makes **NO mention->entity / pronoun->antecedent decision** -- there is no decision variable in THIS organ for a coref gold to score. The gold is AFFORDABLE (301 GUM `.conllu` carry Universal-Anaphora coref in MISC col 10 `# global.Entity`, `(N`/`N)` clusters; 25 LitBank `*_brat.conll` in CoNLL-2012 bracket format) -- but the DECISION is absent. A coref-quality instrument would have to score `hdlab/coreference_resolver.py` (`run_match_or_allocate`/`run_strict_cb`/`run_principle_b`), which is a STRUCTURALLY SEPARATE organ (out of this brief's "reuse the grounding loop" scope) and is gold-mention-dependent (substrate slot E3 = **NEEDS_ADAPTER**: it consumes GOLD mentions, not the loop's raw stream; its prior 0.7193=41/57 is flagged not CI-separated at n=57). ROUTE: cross-solution-map Target 3 (coref/entity-binding, ~14 solutions) + a raw-prose mention adapter. This is the brief's blessed located negative, sharper than anticipated: the gold is affordable; the decision does not exist in the measured organ.

## (c) POWER
The full run is the powered version: n=247 scorable queries (vs smoke 87) and n=4235 grounding targets. CI half-widths: MOVES-on-quality ~0.069, count ~0.014, count-of-targets population 4235 -- the flat-on-count and count-moves claims are well-powered; the moves-on-quality effect (+0.36) dwarfs its half-width. The binding limit on the query population is the loop's LIVE vocabulary coverage (gold partner must be an eligible anchor AND query a non-seed grounding target), not gold size; MEN (human-behavioral, on disk) is the next gold if more power is wanted.

## KEY REALIZATIONS (the enabling moves)
1. **The count knob and the ranking are ORTHOGONAL by construction.** The SDT accept criterion (FA) sets WHICH links clear the gate; the fused convergent-cue argsort sets the RANKING; FA never enters the argsort. So FLAT-on-count is an IDENTITY (byte-invariant ranking under FA, V1), not a weak null -- the strongest form of "the quality metric cannot be gamed by the count knob."
2. **"Referent" was overloaded.** The brief's checklist-3 "referent-link" meant DISCOURSE ENTITY (coref); the loop's `use_referent` is a PERCEPTUAL/VISUAL referent (word -> photo centroid). Disambiguating turned item (a) into a sharper located negative: the gold is affordable, the DECISION is absent from the measured organ.
3. **Gold != component.** The 100%-BF gate is on the inference MECHANISM (already 100% BF/parser-free per the prior FULL_CHAIN_BF_AUDIT); the gold is a human-competence answer key (SimLex/SimVerb human similarity), the right truth for a comprehension metric, and WordNet-independent.

## The gold is a HUMAN-COMPETENCE truth signal, not a machine/taxonomy (owner question 2026-09-12)
The 100%-BF requirement is on the mechanism AT INFERENCE, not on the measuring stick -- the gold never enters inference; it is the exam answer key, and the requirement on it is that it be an INDEPENDENT, non-circular signal of what a competent human reader comprehends ("change the gold to the ability"). SimLex-999/SimVerb-3500 are AGGREGATED HUMAN BEHAVIORAL similarity judgments (a direct measurement of the human semantic system's own verdict on meaning-sameness -- the brain's answer key) and WordNet-INDEPENDENT. WordNet (hand-built ontology) is admissible as a static offline asset but is NOT used as gold here -- to avoid taxonomic circularity and keep the gold WordNet-independent (the representation chain is deliberately WordNet-free). The metric COMPUTATION is the comprehension-test logic (match the resolved meaning to the human key); it sweeps nothing that changes truth.

## Phase-diagram framing (owner reminder 2026-09-12)
The instrument's operating point is FREE to SWEEP, not adopted: the accept threshold (FA), the coverage stratum (the 50% MRR-frontier point), and the gold subset are all swept. The FA sweep IS a phase-diagram sweep of the accept-criterion operating point -- and it is precisely what exposes the count's quality-blindness (the count is a function of the operating point; the correct-link quality is, for the ranking, invariant to it).

## Full-stack upstream (owner directive 2026-09-12)
The upstream component the instrument scores -- the reading-grounding loop's fused sense-assignment read -- was made 100% brain-foundational (parser-free directional-SEQ + grounded-ATL + SDT gate; prior owner-DONE pri-5) and PROVEN to lift coverage QUALITY CI-separated by a REAL brain-foundational change (grow-by-reading to 1M+ modern lines: +0.16 -> +0.26 CI-sep, monotone, twin losing). This instrument is what makes that upstream gain SCORABLE: the count could not see it (item b proves the count is quality-blind), the quality dim does, and the count cannot be gamed past it. No downstream consumer regresses -- the instrument is measurement-only (a board dimension out of the headline aggregate); it changes no organ.

## INSTRUMENT SIGNAL-LOSS TRACE (owner directive 2026-09-12: where up the chain do we lose signal on the inputs?)
The instrument's INPUTS and where each could lose signal, traced rung by rung:
1. RAW read -> the loop's ingest (`process_sentence`): the scorable QUERY population = non-seed words the loop
   actually encountered with traces INTERSECT gold partners that are eligible anchors. SIGNAL LOSS HERE: the
   population is loop-vocabulary-bound (n=247 of the full SimLex+SimVerb pool) -- words the loop never read are
   unscorable. This is a POWER limit, not a bias (the gold is external); MEN/more reading widens it.
2. sense-assignment decision (`FusedSenseRanker.rank`): produces z_top ranking + accept verdict. The instrument
   reads the RANKING (correct-link MRR). NO LOSS: the ranking is the full graded signal; the metric consumes it
   directly (not a thresholded count).
3. the accept GATE (SDT/FA): the COUNT metric reads ONLY the accept verdict and DISCARDS the ranking -> that is the
   quality-blindness this whole problem is about (item b quantifies it: +63% count, 0 quality). The QUALITY metric
   deliberately does NOT read the gate (it reads the ranking) -> it loses NO correctness signal to the gate.
4. the DISCOURSE-ENTITY rung: ABSENT from this organ (item a located negative) -> the instrument cannot see
   entity-link correctness because the loop produces no such signal. This is the one real un-measurable slice; it is
   NOT lost in transmission, it is not produced -> routes to the coref organ.
NET: the only signal the QUALITY instrument loses is (1) population power (addressable) and (4) a decision the organ
does not make (routed). It loses NONE of the correctness signal the loop DOES produce -- unlike the count, which
discards all of it at the gate (3).

## hdlab WIRE SPEC (Q111 -- strategy lands; a proposed change, not a landed one)
Expose the count-vs-quality SEPARATION as a standing board guard so any future meaning-fusion change is auto-scored on QUALITY, not the `n_grounded` count: add a companion board arm that runs the FA-sweep on the live loop and asserts the invariant "count moves, correct-link quality flat" (fail the guard if a change moves the count without moving the quality dim). No change to the grounding organ itself.

## What was NOT established / what I would withdraw first
- The referent-link-to-ENTITY quality is NOT measured (located negative: the loop makes no such decision). If asked to withdraw one thing first, it is any implication that entity-link quality is scorable on this loop -- it is not, and belongs to the coref line.
- The moves-on-quality arm compares FUSED vs the INCUMBENT bag-cosine read (the loop's own pre-landing read); it is not a claim that FUSED is optimal, only that the quality dim MOVES on a real, brain-foundational quality change while the count does not.
- The gold population is loop-vocabulary-bound (n=247); the flat-on-count and count-moves claims are well-powered, the moves-on-quality effect is large relative to its CI, but a smaller quality effect would need MEN/more reading to resolve.

## TLDR (plain English)
We already had a way to score whether the reader links a word to the RIGHT meaning, not just how MANY words it links. This finishes the check: if you simply loosen the reader's acceptance threshold so it grounds MORE words, the plain count jumps 63% but the correctness score does NOT move (and the share of correct links actually falls) -- proving the correctness score measures quality, not quantity, and cannot be fooled by grounding more words wrongly. We also found that one requested piece -- checking whether a word is tied to the right CHARACTER/thing in the story -- cannot be scored on this reader, because this reader never makes that decision; it belongs to a separate part of the system.

## QUESTIONS
None blocking.

## NEXT STEPS
1. STRATEGY WIRE (hdlab, Q111): the count-vs-quality separation guard above, so meaning-fusion changes are auto-scored on quality.
2. Build the referent-link-to-ENTITY instrument on `hdlab/coreference_resolver.py` (Target 3) once a RAW-PROSE MENTION ADAPTER exists -- filed as the named follow-on (this loop cannot supply that decision).
3. POWER: add MEN (human-behavioral, on disk) to widen the scorable population if tighter CIs are wanted; the binding limit is the loop's live vocabulary coverage, not gold size.
