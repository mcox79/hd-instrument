---
problem: reason_over_event_time_order_and_duration_on_a_modern_gold
status: SOLVED
bar: "PASSES only with ALL of: 1. A glass-box temporal reasoner OVER the extracted timeline (built in experiments/, reasoning over sm.timeline_order / _temporal_order_register; REUSE the transitive_ordering magnitude line for graded duration + for interval endpoints, and Allen interval intersection for overlap), doing ALL THREE: (a) BEFORE/AFTER -- query the reordered timeline (Reichenbach place, not telling order); (b) OVERLAP -- read while/during and aspect into event START/END intervals and answer inclusion/overlap (Allen), not precedence; (c) DURATION -- relative (which lasted longer?) off the magnitude line + typical/absolute where the gold demands it. NO external LLM. Copy the Zwaan/Reichenbach/Allen COMPUTATION; SWEEP the interval-endpoint rule / duration representation / abstention thresholds. 2. Answers CI-separated over BOTH controls on MODERN non-circular gold: (a) a surface-order (iconicity) floor recomputed on the same population -- assume telling order == event order -- which MUST LOSE on the flashback/marker items; for DURATION items, a duration-blind majority / most-frequent-answer floor; and (b) the info-free twin -- shuffle the temporal markers and shuffle the tense labels -- which LOSES CI-separated on the order, overlap, AND duration items. Report CI half-width + null p95; recompute each floor on the item's OWN population; report before/after, overlap, and duration SEPARATELY, and aggregate. A POSITIVE control the floor CANNOT get. 3. Isolates the REASONING from extraction -- ablate the reasoner to a narration-order readout (and, for overlap, to a point-order readout with no intervals) and show the lift is the timeline QUERY. 4. One-screen summary. A rigorous NEGATIVE is a FULL PASS."
result: "THREE slices on MODERN gold (n reported per slice), all controls run. BEFORE/AFTER (TB-Dense event-event TLINKs, 1990s newswire, n=445 pairs): composed register 0.5933 vs iconicity floor 0.5236, delta +0.0697 CI[+0.0303,+0.1056] CI-separated; reverse-order positive control (telling!=event order, n=212) reg 0.1557 vs iconicity 0.0000 CI[+0.0632,+0.2331]; cue-bearing subset (n=55) reg 0.9091 vs 0.3455 CI[+0.46,+0.76]; info-free twin collapses to floor (0.5213, p95 0.5744). OVERLAP: constructed can-fail gold (n=160) Allen interval reasoner 0.9938 vs point-order control 0.5000, delta +0.4938 CI[+0.4125,+0.5750], twin 0.4688 (p95 0.5312) loses; TB-Dense real-prose overlap-gold subset (n=121) interval reasoner recovers 0.3967 of the INCLUDES/IS_INCLUDED/SIMULTANEOUS relations the point-order control gets 0.0000 of, CI[+0.30,+0.51]. DURATION: relative magnitude line 1.0000 vs twin 0.5063 on 2520 un-stated transitive 'which lasted longer' pairs (blind 0.5000)."
floor: "BEFORE/AFTER: iconicity (telling order==event order) recomputed on the SAME aligned pairs = 0.5236 full / 0.0000 on the reverse-order subset; reg lower CI +0.0303 > 0. OVERLAP: point-order control (no intervals -> cannot represent overlap -> 'never overlap') = 0.5000 constructed / 0.0000 on the real-prose overlap-gold subset; Allen reasoner CI-separated above both. DURATION relative: duration-blind control 0.5000 (chance). DURATION typical (MCTACO Event Duration): majority 'always-no' floor 0.7404 -- a first-cut distributional prior does NOT beat it (LOCATED NEGATIVE, see below)."
controls: "(1) ICONICITY floor recomputed per-population (before/after) -- reg beats it CI-separated full-pop AND on the reverse-order subset where iconicity is 0. (2) INFO-FREE TWIN (shuffle tense labels + neutralise markers) -- collapses to the floor on before/after (0.521), loses CI-separated on constructed overlap (0.469, p95 0.531) and duration relative (0.506). (3) POSITIVE CONTROL -- before/after reverse-order subset (iconicity=0); overlap real-prose INCLUDES/SIMULTANEOUS subset (point-order control=0). (4) REASONING-vs-EXTRACTION ablation -- overlap point-order control (no intervals) = 0.5 vs Allen 0.994; before/after mechanism-if-cue-else-iconicity isolates the timeline query. (5) NO DOWNSTREAM REGRESSION -- register from the ASPECT extractor (upstream change) vs the ORIGINAL point-order extractor on the SAME pairs: 0.5869 vs 0.5919 (-0.005, within noise) + 48 extra pairs covered from recovered progressives. (6) UPSTREAM FIDELITY -- extracted progressive aspect vs GOLD TimeML aspect: recall 1.000 (all 48 gold progressives), precision 0.857."
files_changed: "experiments/_aspect_interval.py (UPSTREAM: progressive/Vendler aspect -> interval endpoints + Allen overlap); experiments/_tbdense.py (TimeML parser + gold-mention alignment); experiments/_temporal_eval.py (clustered bootstrap + twin p95); experiments/exp_fetch_temporal_gold_v1.py (pinned reproducible fetch: TRACIE/MCTACO/TB-Dense); experiments/exp_temporal_reason_before_after_v1.py; experiments/exp_temporal_reason_overlap_v1.py; experiments/exp_temporal_reason_duration_v1.py; experiments/exp_temporal_reason_timex_probe_v1.py (de-risking probe for the #1 next-organ: TIMEX/DCT anchoring); verification/test_temporal_reasoner_organ.py (12/12); notes/problems/reason_over_event_time_order_and_duration_on_a_modern_gold/SOLVED.md. Gold under data/corpora/{tracie,mctaco,tb_dense}/ (gitignored, re-acquirable via the fetch script)."
reverify: ".venv/Scripts/python.exe verification/test_temporal_reasoner_organ.py   # 12/12 PASS (runs all three slices' load-bearing claims: before/after CI-sep, reverse-order + cue-bearing controls, no-regression, constructed overlap + twin, real-prose overlap-subset, progressive recall=1.0, relative-duration line, typical-duration located negative)"
---

# The timeline is now REASONED over -- before/after + overlap + duration on modern gold, with the two hardest sub-parts drilled to the field-confirmed bottleneck

## What was built (a glass-box temporal reasoner OVER the extracted timeline; NO LLM)
The parent problem (`situation_model_has_no_tested_temporal_order_comprehension`, owner-DONE/EXCELLENT) built and
wired a queryable `before(x,y)` register but tested it at the EXTRACTION level on a construction gold + 19c LitBank.
This problem makes the timeline REASON, on MODERN gold, across all three dimensions the bar asks for:

1. **BEFORE/AFTER** -- a QA over the reordered timeline (Reichenbach place, not telling order). REUSES the parent's
   `ComposedRegister` unchanged. Measured on TB-Dense event-event `BEFORE`/`AFTER` TimeML links (1990s newswire, a
   MODERN non-circular gold) and on TRACIE (ROCStories narrative).
2. **OVERLAP** -- a NEW capability the reader did not have. An **Allen (1983) interval-intersection** reasoner over
   event START/END intervals derived from **viewpoint aspect** (Smith 1991: perfective = closed interval,
   imperfective/progressive = open) plus a **while/during** co-temporal frame. This required an UPSTREAM fix
   (below). Measured on a constructed can-fail gold + TB-Dense `INCLUDES`/`IS_INCLUDED`/`SIMULTANEOUS` links.
3. **DURATION** -- **relative** ("which lasted longer") off the landed `transitive_ordering` magnitude line, and
   **typical** ("how long does a war last") on MCTACO Event Duration.

### The UPSTREAM brain-foundational component (the escalation's requirement -- prototyped + proven, no regression)
Reading the disk showed the extractor the register consumes (`_temporal_ordering_multiframe.extract_events_punct`)
emits only three tenses (VBD, had+VBN, be+VBN) and **DROPS the finite PROGRESSIVE ("was cooking", "were arguing")
entirely** -- exactly the aspect that supplies the ongoing/open interval overlap reasoning needs -- and files
`while/during/as` under NEUTRAL (no relation). So OVERLAP was structurally impossible. I built
`experiments/_aspect_interval.py`, a **strict ADDITIVE SUPERSET** of that extractor:
- recovers the dropped progressive as an IMPERFECTIVE (open-interval) event -- **vs GOLD TimeML aspect, recall
  1.000 (all 48 gold PROGRESSIVE mentions), precision 0.857**;
- adds Smith's second aspect component -- a pre-committed Vendler **lexical situation-type** durative lexicon
  (state/activity -> open interval), which nearly DOUBLED real-prose overlap recall (0.281 -> 0.397);
- maps aspect -> interval endpoints and answers Allen relations.
**No downstream regression:** on the SAME before/after gold pairs the register scores 0.5869 with the aspect
extractor vs 0.5919 with the original (-0.005, within noise) and covers **+48 extra pairs** from the recovered
progressives. Additivity is asserted in the module self-test (byte-identical event set on the point-order tenses).

## What was measured (per slice; each floor recomputed on its own population)

### BEFORE/AFTER -- a CI-separated positive on modern newswire (iconicity is a genuinely weak floor here)
| population | n | register | iconicity floor | delta CI | twin |
|---|---|---|---|---|---|
| ALL pairs | 445 | **0.5933** | 0.5236 | +0.0697 [+0.0303,+0.1056] **sep** | 0.5213 (p95 0.574) |
| REVERSE-ORDER (positive control) | 212 | 0.1557 | **0.0000** | +0.1557 [+0.0632,+0.2331] **sep** | p95 0.100 |
| CUE-bearing (mechanism has evidence) | 55 | **0.9091** | 0.3455 | +0.5636 [+0.46,+0.76] **sep** | 0.436 |

The register beats iconicity CI-separated on the full modern gold, and by construction wins on the reverse-order
(flashback-analog) items where iconicity scores 0. Where an explicit tense/connective cue fires (12.4% of pairs) it
is 91% correct. **TB-Dense is a hard set** -- 47.6% of pairs are reverse-order, so iconicity sits near chance (0.524);
the register still separates.

### OVERLAP -- mechanism PROVEN; real-prose = a positive on the target items + a located full-population limit
- **Constructed can-fail gold (n=160):** Allen reasoner **0.9938** (overlap 1.000 / precedence 0.988) vs the
  point-order control **0.5000** (it has no overlap category), delta +0.4938 CI[+0.4125,+0.5750] **sep**; the
  info-free twin collapses to **0.469** (p95 0.531), losing CI-separated.
- **TB-Dense real-prose serve (n=566, overlap-gold=121):** on the OVERLAP-gold items the interval reasoner recovers
  **0.3967** of the `INCLUDES`/`IS_INCLUDED`/`SIMULTANEOUS` relations the point-order control gets **0.0000** of,
  CI[+0.30,+0.51] **sep**. On the full mixed population it does NOT beat the trivial "never-overlap" majority floor
  (0.776 vs 0.786) -- a LOCATED LIMIT, fully drilled below (fire-precision 0.47 vs base rate 0.21 = 2.2x informative).

### DURATION -- relative REASONING proven; typical is a separate knowledge organ (located negative)
- **RELATIVE (magnitude line):** from only the adjacent-chain premises, the landed `transitive_ordering` line answers
  **1.0000** of 2520 UN-STATED transitive "which lasted longer" pairs; the info-free twin (shuffled durations)
  collapses to **0.5063**; duration-blind control 0.5000. Clean CI-obvious positive -- this IS timeline reasoning.
- **TYPICAL (MCTACO Event Duration, majority floor 0.7404):** a first-cut glass-box event-type duration prior
  (distributionally mined from 251MB simplewiki, NO LLM; 641 lemmas, 38.5% question coverage) does **NOT** beat the
  floor -- it is CI-separated BELOW it, both full (0.7045, delta -0.0359 CI[-0.0587,-0.0148]) and on the covered
  subset (0.6499, delta -0.0900 CI[-0.142,-0.038]). **LOCATED NEGATIVE:** typical duration is a stored
  commonsense-knowledge prior the timeline does not carry, and text-distributional mining cannot supply it.

## THE THREE WALLS, FULLY RESEARCHED (per the standing directive -- each is the field's confirmed conclusion, with a named next-organ)
Three literature drills (~130 sources, majority read full-text) confirm all three limits are correct
brain-foundational conclusions, not artifacts of this setup.

### Wall 1 -- real-prose OVERLAP does not beat the trivial floor (fire-precision ~0.47)
- **Half is a fidelity gap to build across.** Newswire overlap is carried mainly by **TIMEX/DCT reference-time
  anchoring** (event-to-document-time is the EASIEST temporal subtask, TempEval F=0.66-0.80; CAEVO's date sieves run
  at 0.88-0.92 precision) -- a channel my aspect-only reasoner has ZERO access to. And by **discourse relations**:
  Lascarides & Asher (1993) proved with a minimal pair ("Max opened the door / switched off the light. The room was
  pitch dark." -- identical aspect, opposite overlap-vs-sequence reading) that aspect CANNOT resolve overlap alone.
  My Allen+Vendler mechanism is, structurally, the pre-1993 DRT baseline that SDRT exists to supersede.
- **Half is an IRREDUCIBLE annotation ceiling.** `INCLUDES`/`SIMULTANEOUS` are the field's hardest, lowest-agreement
  relations: human two-annotator agreement **~59-64% vs ~82-83% for BEFORE/AFTER** (Cassidy et al. 2014); CAEVO F1
  on INCLUDES = **0.28** (worst of six); **MATRES (Ning et al. 2018) DROPPED these end-point relations entirely**
  because crowd qualification passed only 11% on end-point pairs vs 50% on start-point. My 0.47 fire-precision is
  near the ~60% human ceiling for these relation types, not the 80% BEFORE/AFTER ceiling.
- **Named next-organs (ranked):** (1) TIMEX3/DCT reference-time anchoring (cheapest, highest-precision, glass-box);
  (2) a measured reporting-verb/complement containment rule; (3) an SDRT-lite discourse-relation reader.

### Wall 2 -- BEFORE/AFTER cue-sparsity (12%) + TRACIE implicit-event
- **Cue-sparsity is real and matches the field.** Only ~12% of TB-Dense pairs carry an explicit tense/connective cue
  the register reads -- and the field's own figure is **11.2%** explicit signal words in TimeBank; CAEVO's tense
  sieve gets **2-3% recall** alone; **46.5% of TB-Dense pairs are VAGUE** (no recoverable order by any method). The
  rest of event order rides on TIMEX/DCT anchoring + **SDRT discourse relations** (D'Souza & Ng 2013: discourse-relation
  features add MORE than extra aspectual granularity; Explanation reverses surface order).
- **Iconicity is a genuinely weak baseline** the field doesn't even use (Do/Lu/Roth 2012 iconicity F1=25 vs a real
  classifier's 42) -- so beating it CI-separated is a validated, fair win, not a soft target.
- **TRACIE is ~100% implicit-event by design** (my measured 3.8% story-internal is consistent). SOTA (SymTime) needs
  ~3.5M external distantly-supervised examples; general LLMs score WORSE (46-66%) than the purpose-built model.
  Script theory (Schank & Abelson 1977; Bower/Black/Turner 1979) confirms implicit-event placement is a
  KNOWLEDGE-RETRIEVAL problem (ATOMIC/COMET), categorically distinct from timeline-query. **"Story-internal only" is
  the correct brain-faithful scoping** -- implicit-event inference is a SEPARATE downstream organ.
- **Named next-organs:** TIMEX/DCT anchoring; SDRT-lite; a free transitive/Allen closure lever (+5 F1, Ning 2017); a
  script/schema event-sequence organ for implicit events.

### Wall 3 -- TYPICAL duration cannot be mined from text
- **Triply corroborated.** (1) Gricean reporting bias (Gordon & Van Durme 2013): typical durations are structurally
  UNSTATED -- people report deviations, not the expected. (2) **Vempala et al. 2018** -- the one published study that
  added query-pattern-mined duration signal to a classifier found it made results WORSE (0.71 -> 0.68) -- EXACTLY my
  result. (3) **TacoLM's authors (Zhou et al. 2020)** independently concluded raw pattern-mined duration was too noisy
  to use directly. Pre-LLM neural SOTA on MCTACO Duration is ~33-40% EM vs human 75.8% -- the hardest category.
  Bigger neural models AMPLIFY the sibling (frequency) reporting bias (Shwartz & Choi 2020), so "mine more text"
  does not work. Duration is a distributed/experiential semantic-memory construct (Coll-Florit & Gennari 2011).
- **Named next-organ (concrete, no-LLM, downloadable TODAY):** **UDS-Time** (Vashishtha et al. 2019) -- 32,302
  crowd-annotated events with an 11-bucket ordinal duration scale, `pip install decomp`, static data queried at
  inference with no model. Build a per-lemma bucket table and re-run this exact MCTACO harness (the cheap decisive test).

## What I did NOT establish (withdraw-first if wrong)
- **I would withdraw first any implied claim that the real-prose OVERLAP reasoner beats a strong floor on the full
  population.** It does not (0.776 vs 0.786); the load-bearing overlap claim is (a) the constructed mechanism (0.994
  vs 0.5) and (b) the real-prose OVERLAP-gold subset (0.397 vs the point-order control's 0.0). The full-population
  limit is a located negative with the bottleneck named (DCT/discourse + a ~60% IAA ceiling).
- **The TYPICAL-duration prior is a first-cut NEGATIVE, not a contribution** -- it is CI-below the majority floor. The
  RELATIVE-duration magnitude line (1.0) is the real duration positive; typical duration needs the UDS-Time organ.
- **BEFORE/AFTER on TRACIE is not a result** -- 96% of TRACIE is implicit-event, which the story-internal register
  cannot place; I report coverage (3.8%) and the located limit, not an accuracy claim.
- The before/after headline is on real newswire where iconicity is near-chance; on genres where telling order is
  more reliable the margin would shrink (the register only overrides on the 12% cue-bearing pairs).

## KEY REALIZATIONS (the enabling moves)
1. **The upstream gap was a DROPPED aspect channel, found by reading the extractor, not the brief.** The reader
   literally could not see "was cooking" -- overlap was impossible until the progressive was recovered. Recovering it
   validated at recall 1.0 vs gold TimeML aspect.
2. **The brain-faithful default fixed an unfair comparison.** The register fell back to lemma-first-occurrence order;
   switching the default to EXACT mention order (overridden only by a real cue) turned a spurious full-pop loss
   (0.42<0.52) into a clean CI-separated win (0.59>0.52). The brain indexes event TOKENS, not verb types.
3. **A "wall" can be half fidelity-gap and half annotation-ceiling.** The overlap drill separated my 0.47
   fire-precision into a real missing channel (DCT/discourse) AND the field's own ~60% human-IAA ceiling on
   INCLUDES/SIMULTANEOUS (the reason MATRES deleted those relations). You cannot chase precision past the human floor.
4. **A located negative is stronger when the field reached it independently.** The typical-duration failure is
   Vempala 2018's exact negative result and TacoLM's own design decision -- distributional text mining cannot supply
   typical durations because writers never state them (reporting bias). The fix is a different SOURCE (UDS-Time), not
   more mining.
5. **Relative vs typical duration are two different organs.** Relative is arithmetic on a magnitude line (1.0, reuses
   the landed reasoning primitive); typical is a stored knowledge prior. Conflating them hides that half the
   capability was already in the substrate and half needs a new organ.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md sec.2b -- the TIME dimension)
The TIME dimension is now tested at the REASONING level, not just extraction. PINNED verdicts hold (Reichenbach
E/R/S; Allen interval algebra as the Marr computational-level target; magnitude line for relative duration). NEW
findings to fold in: (a) the point-order extractor DROPPED finite progressive aspect -- an upstream fidelity gap now
prototyped (progressive recall 1.0 vs gold TimeML), plus a Vendler lexical-aspect layer; (b) real-prose OVERLAP is
NOT aspect-resolvable alone (Lascarides & Asher minimal-pair proof) -- it needs TIMEX/DCT anchoring + SDRT discourse
relations, and INCLUDES/SIMULTANEOUS carry an irreducible ~60% human-IAA ceiling (MATRES dropped them); (c) TYPICAL
duration is a SEPARATE knowledge organ the timeline does not carry (reporting bias; UDS-Time is the no-LLM
next-organ); (d) implicit-event ordering (TRACIE) is a separate world-knowledge/script organ, not timeline-query --
"story-internal only" is the correct scoping. Deviation to record: the register reads only tense/connective cues
(~12% of real pairs) and has NO TIMEX/reference-time-anchoring or discourse-relation channel -- the highest-value
next upstream, shared by before/after AND overlap.

## Adjacent components (evaluated for brain-fidelity + next problems, per owner 2026-08-28)
- **TIMEX/DCT reference-time anchoring -- MISSING, highest-value, shared upstream; DE-RISKED with a built probe.**
  The single channel that would most lift BOTH before/after coverage and overlap precision on real prose; glass-box
  (a date comparison), PINNED (Reichenbach R defaults to DCT). **`exp_temporal_reason_timex_probe_v1.py` MEASURES the
  lever on TB-Dense:** anchoring events to a date in their OWN sentence (event-local, CAEVO's high-precision sieve)
  resolves before/after pairs at **0.958** where the cue channel is silent (vs iconicity 0.583), lifting the combined
  reasoner 0.5933 -> **0.6135** CI-separated over cue-only and +0.090 over iconicity. CRITICAL FINDING: NAIVE
  carry-forward anchoring (last-date-seen) HURTS (0.493, below iconicity) -- the organ must use EVENT-LOCAL / proper
  reference-time attachment, not last-date. **Strongest candidate next problem, now with a proven spec + a named
  failure mode to avoid.**
- **SDRT-lite discourse-relation reader -- MISSING.** Narration/Result/Explanation/Background; Explanation reverses
  order, Background = overlap. Adds more than aspectual granularity (D'Souza & Ng 2013). Bigger build; sequence after
  anchoring.
- **Event-type duration lexicon (UDS-Time) -- MISSING, concrete + no-LLM.** The typical-duration organ; `decomp`
  package, 32,302 crowd-annotated events. Cheap decisive test defined.
- **Script/schema event-sequence organ -- MISSING.** For implicit-event ordering (TRACIE) + typical relative
  position; Chambers & Jurafsky narrative event chains; feeds the timeline register as a prior.
- **The point-order extractor -- OUR-INVENTION placeholder, now partly upgraded.** Progressive recovered (recall 1.0);
  lexical situation-type added. A full syntactic aspect parse would raise precision (0.857 -> higher).

## Proposed hdlab landing (strategy lands; Q111 -- I do not write hdlab/)
1. **Promote `experiments/_aspect_interval.py`** as the aspect->interval upstream: fold progressive recovery +
   Vendler lexical aspect into the timeline extractor (ADDITIVE -- keep the point-order tense set byte-identical for
   the order register; the new interval character is used only by the overlap reasoner). No before/after regression.
2. **Add an OVERLAP reasoner** to the situation reader over `sm.events` (Allen intersection over aspect-derived
   endpoints + a while/during co-temporal frame), exposing `overlaps(x,y)` / an Allen relation -- default-ON is
   safe (additive; it only ANSWERS a query the reader could not answer before).
3. **Add RELATIVE-duration** to the timeline: integrate parsed/known event durations into the `transitive_ordering`
   line, expose `longer(x,y)`. (Reuses the landed primitive; proven 1.0.)
4. **Do NOT land the distributional typical-duration prior** (located negative). Instead file UDS-Time as the
   typical-duration organ.
5. Report WHICH signal class produced each order judgment (cue / -- when built -- TIMEX / discourse / closure /
   "VAGUE") and return "unknown -- requires world knowledge" on implicit-event queries, rather than one opaque
   "temporal reasoning" claim (a glass-box property LLM systems cannot make).

## TLDR (plain English)
A reader should not just record what happened -- it should reason about WHEN. Our reader already worked out the real
order of events even when a story tells them out of order; this makes it ANSWER timing questions on modern test text.
On real 1990s news, when asked "did X happen before or after Y?", it beats the naive "things happened in the order
they were told" guess (about 59 right in 100 vs 52), and it is right 91% of the time whenever the sentence gives an
explicit tense/"before"/"after" clue -- while a scrambled-clue version drops to a coin flip. It gained a brand-new
skill it never had -- telling when two events OVERLAP in time ("while she cooked, they argued") -- by first fixing an
upstream blind spot: the reader was throwing away every "was doing" (ongoing) verb, which is exactly the word that
signals overlap; recovering those matched the gold annotation on every case. On clean test sentences the overlap
skill is near-perfect (99% vs a coin flip for the old point-in-time reader). It can also say which of two events
lasted longer, perfectly, even for pairs it was never directly told about, by placing them on a mental "length
ruler". Two honest dead-ends, each chased all the way to the bottom and confirmed by outside science: (1) on messy
real news, spotting overlap needs the story's publish DATE and the logic between sentences, not just verb shape --
and the specific "one thing contains another" case is so fuzzy that trained humans only agree 6 times in 10, so no
tool can score high on it; (2) "how long does a war/glance typically last" simply isn't written down in ordinary
text (people only mention durations when they're surprising), so mining text can't learn it -- the fix is a free,
ready-made dataset where people were asked directly, plugged in as a lookup with no AI model at answer-time.

## QUESTIONS
None. (One judgment call: graded SOLVED. The before/after CI-separated win, the constructed + real-prose-subset
overlap wins, the upstream progressive recovery, and the relative-duration line are positives; the full-population
real-prose overlap limit, the typical-duration prior, and TRACIE implicit-event are rigorous located negatives --
which the brief states are full passes -- and all three are drilled to the field-confirmed mechanism with named
next-organs.)

## NEXT STEPS (ranked)
1. **Strategy: land the upstream aspect->interval upgrade + the OVERLAP reasoner + RELATIVE-duration** (all additive,
   no regression; witness 12/12).
2. **Next problem -- TIMEX/DCT reference-time anchoring** (the highest-value shared upstream for BOTH before/after
   coverage and overlap precision; glass-box, PINNED). Cheap test: measure incremental coverage on TB-Dense.
3. **Next problem -- the event-type duration organ from UDS-Time** (`pip install decomp`; per-lemma bucket table;
   re-run this MCTACO harness). Named, no-LLM, same-day test.
4. **Later -- SDRT-lite discourse-relation reader + a script/schema organ for implicit-event ordering** (TRACIE);
   and a transitive/Allen closure pass over extracted pairs (a free +5 F1 lever).
5. **Measurement upgrade -- re-score real-prose overlap against the ~60% human-IAA ceiling** for INCLUDES/SIMULTANEOUS,
   not an 80% BEFORE/AFTER expectation.
