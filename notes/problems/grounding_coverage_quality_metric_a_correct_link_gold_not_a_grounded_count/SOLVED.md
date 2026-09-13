---
problem: grounding_coverage_quality_metric_a_correct_link_gold_not_a_grounded_count
status: SOLVED
bar: "Deliver a `board_grounding_quality_dimension()` (or an equivalent instrument) that scores CORRECT-LINK quality on independent MODERN gold (grounded referent/sense matches held-out truth), and DEMONSTRATE on a real meaning-fusion change that: (a) the QUALITY dim MOVES when link quality improves CI-separated; (b) it is FLAT when only `n_grounded` grows (quantity without quality); (c) a scrambled-link twin scores at chance. OR a rigorous LOCATED NEGATIVE naming exactly which grounding decision has no affordable independent gold (with the reason). INVARIANT: the gold is INDEPENDENT of the fusion (no circular ground-by-X-grade-by-X); no external tool/LLM at inference; modern gold only."
result: "COMPLETE 2x2 SEPARATION (n=247 scorable queries, n=4235 grounding targets, live reading-grounding loop, full curriculum + 1M-line grown SEQ store). (a) MOVES-on-quality: FUSED - INCUMBENT correct-link MRR@0.5 = +0.3612 CI[0.2977,0.4353] CI-sep (fused 0.3823 vs incumbent bag-cosine 0.0211). (b) FLAT-on-count: the SDT false-alarm knob FA 0.01->0.40 raises the accepted count +0.319 frac CI[0.3053,0.3332] CI-sep (n_accepted targets 2154->3505, +63%) while the correct-link ranking-MRR diff = 0.0000 EXACTLY (FA-invariant by construction; proven byte-identical order+z_top on the live ranker, V1) and correct-rate-among-accepted MONOTONICALLY DECLINES 0.235->0.180 as the count grows (more links, not more correct). (c) scrambled-link TWIN at chance MRR 0.013 (FUSED-TWIN +0.3694 CI[0.301,0.4429]). Smoke (n=87) agrees: MOVES +0.3512 CI[0.235,0.455], count +0.400, Qflat 0.0, twin 0.018. PLUS a rigorous LOCATED NEGATIVE on the referent-link-to-ENTITY slice: the reading-grounding loop makes NO mention->entity/coref decision (0 entity/coref/mention/pronoun tokens across reading_grounding_loop.py's 3022 lines), so GUM/LitBank coref gold (present + parseable on disk) has no decision variable to score in THIS organ -> routes to hdlab/coreference_resolver.py (NEEDS_ADAPTER)."
floor: "INCUMBENT bag-cosine read (the pre-landing live sense-assignment read) correct-link MRR@0.5 = 0.0211 (n=247); it is the strongest non-trivial floor (the loop's own prior read). The COUNT metric itself is the count-side floor: n_grounded moves +63% (2154->3505 accepted targets) under the FA knob while correctness does not -- the exact quality-blindness the instrument exposes."
controls: "(1) scrambled-link TWIN (channel evidence taken from a DIFFERENT query word) at chance MRR 0.013 -- excludes base-rate/lucky-pool. (2) FA-INVARIANCE IDENTITY (V1): the ranked candidate order and z_top are byte-identical across FA=0.01 vs 0.40 on the live ranker; only the accept verdict differs (FA_hi accepts a superset) -- excludes 'the quality metric secretly tracks the accept threshold' (it is an identity, not an underpowered null). (3) COUNT-OUTRUNS-CORRECT (V3): correct-rate-among-accepted does not rise (declines) as FA raises the count -- excludes 'more links = more correct'. (4) GROUNDED-ONLY ablation (landed instrument). INDEPENDENCE: gold = SimLex-999 + SimVerb-3500 human similarity, which is WordNet-independent AND fusion-independent -> no circular ground-by-X-grade-by-X. No external tool/LLM at inference; modern gold only."
files_changed: "experiments/exp_grounding_quality_flat_on_count_v1.py (the FLAT-on-count demonstration: FA-sweep count knob vs FA-invariant correct-link quality, the 2x2), verification/test_grounding_quality_flat_on_count.py (scaffold-free witness, 3/3: FA-invariance of the live ranking, smoke 2x2 verdict, count-outruns-correct), experiments/exp_grounding_quality_predictive_v1.py (the predictive-coding/N400 replacement-instrument PROBE: located negative -- per-token surprisal is surface-collocation-confounded; see body). OPTIMIZATIONS (owner 2026-09-12, all four): experiments/exp_grounding_state_cache_v1.py (#1 byte-identity-gated live-state cache -- 353s build -> 6.6s reload ~53x; self-test PASS), experiments/exp_grounding_quality_powered_v1.py (#3 powered: SimLex+SimVerb n=247 + MEN relatedness n=81 + pooled n=327, full frontier, all CI-sep), experiments/exp_grounding_quality_wic_v1.py (#4 decision-level WiC consequence -- located negative: loop grounds coarse type-level, WiC needs fine token-sense -> route to USR); #2 per-consumer FA = measured curve + hdlab wire spec (body). Data: data/grounding_quality_flat_on_count_v1/metrics_{full,smoke}.json, data/grounding_quality_predictive_v1/metrics_smoke.json, data/grounding_quality_powered_v1/metrics_full.json, data/grounding_quality_wic_v1/metrics_full.json. REUSES (does not rebuild) the landed sense-assignment half: experiments/exp_board_grounding_coverage_quality_v1.py + the live board arm `grounding_coverage_quality` in exp_situation_model_qa_modern_v1.run. NO hdlab/ modified (Q111 -- hdlab wire spec in the body)."
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

## A BETTER, MORE BRAIN-FOUNDATIONAL INSTRUMENT? (owner question 2026-09-12: "is there something that WOULD work well and replace the initial test? How does the brain do this?")
The current instrument uses an EXTERNAL human-similarity gold (SimLex/SimVerb). The brain has no external answer key
while reading; it validates a grounding two intrinsic ways: (1) PREDICTIVE CODING / N400 -- a correct grounding
lowers surprise on the continuation (Rao-Ballard; Kutas-Federmeier; Rabovsky-McClelland 2018 = N400 is the
Rescorla-Wagner prediction error of an online next-item model; Levy surprisal); (2) DOWNSTREAM INFERENTIAL
CONSEQUENCE -- a correct grounding enables correct situation-model QA. Both are gold-free; (1) is self-supervised and
makes EVERY read word scorable (dissolving the n=247 power bottleneck).

PROTOTYPED the predictive-coding instrument (`exp_grounding_quality_predictive_v1.py`): substitute each grounded word
with the sense-anchor the loop chose, then measure held-out cloze surprisal under the landed `PredictiveWorldModel`
(Rescorla-Wagner). Arms FUSED / INCUMBENT / RAW / SCRAMBLED-twin on the same held-out positions.

**RESULT = a rigorous LOCATED NEGATIVE (smoke, n=252 scored, 3905 substitutions):** mean surprisal RAW 7.606 ~
INCUMBENT 7.599 < SCRAMBLED 7.715 < FUSED 7.750. FUSED does NOT lower surprisal -- it is CI-separated HIGHER than
raw/incumbent (INCUMBENT-FUSED -0.151 CI[-0.225,-0.071]; RAW-FUSED -0.144 CI[-0.218,-0.076]). WHY (the mechanism):
per-token cloze surprisal is dominated by SURFACE COLLOCATION (n-grams like "New York", "of the"); replacing a word
with its sense-anchor BREAKS those surface regularities, so the metric penalizes grounding for disrupting surface
statistics rather than rewarding correct meaning. It measures surface-predictability loss, not grounding
correctness. This CORROBORATES the prior owner-DONE W34/W35 (context-prediction beats no-context by only +0.04 bits;
per-word prediction is intrinsically surface-dominated + low-SNR for meaning -- human cloze is genuinely low).

**VERDICT:** the predictive-coding DIRECTION is brain-foundational and appealing (gold-free, unlimited power), but the
per-token sense-substitution instrument is CONFOUNDED and does not replace the SimLex proxy. Two honest conclusions:
(1) the EXTERNAL-human-similarity-gold instrument (SimLex/SimVerb partner-ranking) REMAINS the better isolation
instrument for sense-assignment quality -- it is not beaten by the intrinsic route at the per-token level; (2) the
genuinely better ECOLOGICAL "consequence" instrument is the DOWNSTREAM situation-model QA (which the board already
runs): score grounding quality by its effect on held-out QA (a correct grounding enables correct inference), not by
per-token surprisal. That is the right home for the brain's "you understood if you can answer/act" signal, and it
avoids the surface-collocation confound because the target is the QA answer, not the next surface token. RECOMMEND:
keep SimLex/SimVerb as the sense-isolation quality dim (this problem's instrument), and route the intrinsic
comprehension signal to the downstream-QA board rather than a per-token cloze instrument.

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

## OPTIMIZATIONS & EFFICIENCIES (owner question 2026-09-12; ranked by ROI)
1. **COMPUTE (highest ROI) -- cache the live grounding state (DONE -- built + verified; `exp_grounding_state_cache_v1.py`).**
   Every grounding experiment (this instrument, the board arm, the whole meaning-fusion line) rebuilt the same live
   `ReadingLoopState` from scratch (~500s: full-curriculum ingest + 1M-token grown-store merge). `build_or_load_live_state`
   keyed by (curriculum-limit, grown-store hash) MEASURED: **353s build -> 6.6s reload (~53x)**. REUSES the landed,
   self-tested `foundation_persistence.save_foundation`/`load_foundation` (not a hand-rolled pickle); GATED on a
   byte-identity check (cached vs fresh: anchors, `_sums`, ctx counts, targets -- self-test PASS). #3 and #4 both ran
   off it (59s not 500s). Same pattern as the arc-scorer work's `train_or_load_em`.
2. **LOOP OPERATING POINT (DONE -- measured; evidence-backed, phase-diagram) -- FA as a per-consumer precision knob.**
   The precision/coverage tradeoff from the FLAT-on-count full sweep (n_targets=4235):
   ```
   FA     coverage (accepted/total)   precision (correct-rate among accepted)
   0.01   0.509                       0.235   <- precision-optimal
   0.05   0.638                       0.211   (current fixed default = a middling compromise)
   0.10   0.702                       0.189
   0.20   0.761                       0.188
   0.40   0.828                       0.180   <- coverage-optimal
   ```
   As the SDT gate loosens, coverage rises 0.509->0.828 but precision falls 0.235->0.180 -- the classic recognition-
   memory criterion tradeoff. BRAIN-FOUNDATIONAL (mathematically): the accept gate IS the brain's SDT recognition
   criterion (Yonelinas 2002), and the brain sets that criterion by TASK PAYOFF (Green-Swets; a precision-critical
   action uses a strict criterion, a gist judgment a lax one). So a single fixed FA=0.05 is NOT brain-faithful -- the
   criterion should be TASK/CONSUMER-DEPENDENT. WIRE SPEC (hdlab, Q111 -> strategy lands): expose `false_alarm`
   per-consumer (precision-critical readers strict ~0.01, coverage-critical ~0.2-0.4), defaulting to the payoff of the
   calling consumer. "Ground fewer, righter" beats "ground more" for any consumer that acts on correctness.
3. **INSTRUMENT POWER (DONE -- measured; `exp_grounding_quality_powered_v1.py`, loads the #1 cache -> 59s not 500s).**
   Widened the scorable population + full coverage frontier, gold reported per CONSTRUCT (not silently pooled):
   - SYNONYMY (SimLex+SimVerb, n=247): FUSED AUF-MRR 0.398 vs incumbent 0.027 vs twin 0.018; @0.5 fused-inc +0.357
     CI[0.288,0.433] sep.
   - RELATEDNESS (MEN, human-behavioral, n=81, reported SEPARATELY -- relatedness != synonymy): FUSED AUF 0.746 vs
     incumbent 0.137 vs twin 0.028; @0.5 +0.654 CI[0.529,0.785] sep (even stronger -- grounding+visual-referent shine
     on concrete-noun relatedness).
   - POOLED mixed-construct (n=327): +0.475 CI[0.411,0.542] sep. Full frontier (0.1..1.0) computed per source.
   All CI-separated, twin at chance -- the instrument's moves-on-quality result holds at higher power and on a second
   human-behavioral construct.
4. **PREDICTIVE ROUTE -- the per-token cloze is dead (surface-confounded); the DECISION-level WiC fix is ALSO a
   located negative (a COVERAGE wall), and the two negatives TRIANGULATE on the primary instrument being correct.**
   FIX built + run (`exp_grounding_quality_wic_v1.py`): the WiC grounding-consequence -- ground the target's context in
   each WiC sentence via the loop's own `canonicalize_fast`, predict same/different-sense from whether the two
   contexts ground to the SAME anchor; scored vs WiC dev gold (n=638, balanced, base rate 0.5). RESULT (LOCATED
   NEGATIVE): LOOP_ANCHOR accuracy 0.500 CI[0.459,0.547] = CHANCE; BUNDLE_COS AUC 0.507 CI[0.462,0.551] = chance;
   scrambled twin 0.500. WHY (the drill -- CORRECTED by a coverage diagnostic; an earlier "coarse granularity"
   reading was WRONG and is RETRACTED): the diagnostic shows 0 of 638 WiC instances had BOTH contexts ground (only
   8/638 had EITHER) -- the loop's `canonicalize` almost never clears SENSE_MATCH_THRESH=0.45 on arbitrary OUT-OF-
   CURRICULUM WiC sentences, so it makes NO grounding decision to score and accuracy sits at base rate BY
   CONSTRUCTION. This is a COVERAGE wall, not granularity: the loop's grounding decision is DEFINED OVER ITS OWN
   CURRICULUM FIELD (words it read, in curriculum-like contexts), not arbitrary probe sentences. Forcing grounding by
   lowering the threshold would just inflate coverage without quality (the FLAT-on-count lesson) -- not a fix.
   TRIANGULATION: BOTH proposed replacement instruments are located negatives with clear, DIFFERENT mechanisms --
   per-token cloze (surface-collocation-confounded) and WiC decision-level (the loop does not ground OOD probe
   contexts) -- and BOTH CONFIRM the design of the primary instrument: score the loop on the decisions it ACTUALLY
   makes, on ITS OWN field (SimLex/SimVerb queries restricted to the loop's real grounding targets INTERSECT eligible
   anchors), where it wins CI-separated. Fine token-sense on arbitrary contexts is a DIFFERENT organ
   (`underspecified_sense_reader` / the SCWS board arm), not the grounding loop.

## ADDITIONAL UPGRADES IDENTIFIED THROUGH THIS WORK (owner question 2026-09-12)
- **G1 -- bank GRADED grounding confidence (z_top) with each link.** The loop records binary grounded/not; the
  FLAT-on-count work shows the z_top standout margin IS the correctness signal. Pass z_top downstream so consumers
  weight by reliability instead of treating a link as binary (the "pass graded signal" discipline). (hdlab wire ->
  strategy; provenance already carries part of it, W4.)
- **G2 -- replace the incumbent-bag-cosine FALLBACK with principled ABSTENTION.** When no channel fires the loop
  falls back to a bag-cosine read at floor (MRR ~0.02), emitting a garbage link; abstaining (mark UNKNOWN) raises
  correct-link precision directly. (hdlab wire -> strategy; the board arm's n_fused_fallback_to_incumbent quantifies
  the incidence.)
- **G3 -- the WiC grounding-consequence arm** (the #4 fix) is a NEW decision-level sense instrument, complementary to
  the SimLex-partner RANKING instrument.
- **G4 -- wire #1's state cache into the board's grounding arm** so the whole board run loads the live state in
  seconds instead of rebuilding it.
- **G5 -- the surface-confound finding localizes the loop's ceiling to its SURFACE-level SEQ channel** (per-token
  prediction is surface-dominated); concept-level prediction needs a concept-transition model = the GENERATIVE
  WORLD-MODEL (the named main event) -- a strategic pointer, not a quick fix.

INTEGRATED_BY_STRATEGY 2026-09-12 — owner-DONE 22:30; reverified 3/3 first-hand. Instrument + witness committed (experiment routed through get_output_dir); board guard arm recorded as a follow-on (INTEGRATION_LEDGER).
