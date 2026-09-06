---
priority: 5
slug: reason_over_event_time_order_and_duration_on_a_modern_gold
status: CANDIDATE
review:
review_text:
---

# PROBLEM: the reader EXTRACTS an event timeline (whole-passage chronological order, flashbacks resolved) but never REASONS over TIME -- it cannot answer before/after/overlap/duration questions when surface order != event order ("before/after/while/since/by the time" + tense+aspect + flashback), and its one timeline test is extraction-level, on 19c LitBank (BANNED) plus a circular board gold. Build a glass-box temporal reasoner OVER the already-extracted timeline: query it for before/after (Reichenbach place over the reordered timeline), OVERLAP (interval intersection, "while/during"), and DURATION (relative + typical), CI-separated over BOTH a surface-order (iconicity) floor that LOSES on the flashback/marker items AND an info-free twin (shuffled temporal markers / shuffled tense), on a MODERN non-circular temporal-reasoning gold.

**slug:** `reason_over_event_time_order_and_duration_on_a_modern_gold` -- **opened:** 2026-09-06 by the strategy
session. This is the TIME half of the comprehension->REASONING pivot (the causal-network reasoning problem is its
sibling, opened the same day): the substrate spent the program BUILDING the situation model (events, coref, a causal
network, and a queryable event TIMELINE); this runs INFERENCE over the TIME dimension. It COMPOSES the landed timeline
register + the magnitude-line order primitive; it does NOT re-extract tense or rebuild the before/after register.
**status:** CANDIDATE -- a MECHANISM + BUILD problem. You build + validate in `experiments/`; strategy lands any hdlab
change (Q111). Glass-box, NO external LLM at inference (the invariant) -- the timeline query + interval reasoning is
transparent, not a learned temporal-QA model.

> **UPSTREAM CAVEAT (strategy, 2026-09-06) -- the reader's fine TENSE labels are currently DEGRADED, and this brief's
> Reichenbach E/R/S mechanism rests on tense/aspect.** The 2026-09-03 tagger reroute (a real perf/coverage win) coarsened
> the POS-conditioned fine tense labels: coordinated-2nd-conjunct `PAST_PERFECT` propagation, `MODAL_SUBORDINATE`, and
> `PARTICIPIAL` now collapse to `SIMPLE_PAST`/`OTHER` (the 1st-conjunct direct-`had` `PAST_PERFECT` still fires). See
> `notes/PROVISIONAL_WIRINGS.md` sec5. So a REQUIRED can-fail step: measure temporal accuracy WITH vs WITHOUT the fine
> tense labels; if they are load-bearing, re-derive tense from the arc-eager PARSE (dependency structure), not the raw POS
> tagger -- that closes both this brief and that lossy coupling (the full-stack-upstream directive in the checklist below).
>
> **MODERN GOLD ALREADY ON DISK:** `data/corpora/mctaco` (MC-TACO) is a modern temporal-commonsense QA benchmark whose
> categories map directly onto this brief's targets -- event ordering (before/after), event DURATION, and TYPICAL time --
> so it is the natural primary non-circular gold here (confirm its license/provenance before use). Do NOT fall back to the
> 19c/circular timeline gold.

> **PRIORITY NOTE (the call is the strategy session's; provisional -- RE-RANK per the owner):** filed at `5` (a free,
> unique rank). It is HIGH-value -- the TIME sibling of the causal reasoning pivot, the first inference organ over the
> event timeline, and it retires a 19c/circular-gold measurement for a modern one -- but it is a NEW capability that
> DEPENDS on the extracted timeline's real-prose density, so it is ranked with the other CANDIDATE reasoning builds.
> Set the real priority when this is promoted from CANDIDATE to OPEN.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do.
>
> **YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **"CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) -- RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one -- and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps -- AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) -- that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill -- do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across -- never a ceiling.
> Each fire: implement -> test (can-fail, strongest real floor, info-free twin LOSING) -> iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

> ## BRAIN-FOUNDATIONAL CHECKLIST (the owner's standing bar -- work through IN ORDER; the solution is not done until every box holds)
> 1. **OPEN -- how does the BRAIN do THIS?** Name the specific structure + computation and replicate that OPERATION as the FIRST move; mark each choice PINNED vs OUR-INVENTION. RESEARCH AGGRESSIVELY wherever you are unsure -- do not build the tractable thing and cite neuroscience after.
> 2. **REUSE -- does an existing organ already do what you need?** Check `tools/substrate_map.py` / `tools/reader_capabilities.py` / `hdlab/` FIRST; extend a matching organ rather than re-deriving it.
> 3. **GENERALIZE -- does this need to generalize, and HOW does the brain generalize it?** Build for that (register / novelty / transfer), not for the single test.
> 4. **HIT A WALL? GO DEEPER, DON'T STOP.** Research-drill WHY. If the brain can do it, it IS possible and we can too, once we understand it. A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, is what failed (fair test: can-fail, one-variable, real baseline).
> 5. **OPTIMIZE BY EXACT REPLICATION.** Evaluate aggressively, with great precision, EXACTLY how the brain does it, and replicate it exactly -- copy the computation, SWEEP (never adopt) the parameters. No half-effort: the closer we are, the better we do.
> 6. **PERFORMANCE vs THE BRAIN.** How does our performance compare to a competent brain/reader on this task? WHERE ALONG THE CHAIN do we lose signal? What EXACTLY differs between our implementation and the brain's mechanism (an itemized mechanism-diff)?
> 7. **ADJACENT COMPONENTS.** Map the capabilities, limitations, opportunities, and brain-foundational status of the adjacent components -- that seeds the next problems to address.
> 8. **COMPLETION BAR.** Is this a COMPLETE, EXCELLENT solved problem? Is it FULLY brain-foundational, conveying ALL the benefits of the brain function we replicate? If not, keep pushing toward a fully complete, exceptional solution.
>
> **🎛️ (PHASE DIAGRAM — the substrate is not locked to one regime.)** The substrate's operating point — store DENSITY vs SPARSITY, dimensionality, binding regime, capacity, decay/gain, indexed-vs-superposed organization — is FREE to change at ANY time, PER ORGAN. These are parameters to SWEEP, never fixed constraints. A wall "at this configuration" is a cue to MOVE the operating point on the phase diagram BEFORE ever calling it a ceiling.
>
> **🧠🔧 (FULL-STACK UPSTREAM — prototype THIS component AND its upstream, to EXCEL and EXCEED.)** Fully prototype THIS component AND the upstream brain-foundational component it depends on (and ALL the way upstream if the chain is deeper), and SHOW the capability can EXCEL and EXCEED — make it happen. Then: (a) CONFIRM no other downstream consumer of the upstream optimization REGRESSES; (b) CONFIRM whether those other consumers should be REVISITED to be more brain-foundational, now making use of the newly-optimized upstream capabilities; (c) make SURE, VIA RESEARCH, that what you implement upstream is genuinely brain-foundational. **THE ONLY WAY YOU OVERCOME THIS WALL IS FOR EVERY COMPONENT — YOU AND UPSTREAM — TO BE BRAIN-FOUNDATIONAL.** Any wall you encounter must be FULLY RESEARCHED: the brain does it, so we can too — and to do so we must UNDERSTAND it fully.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When a person reads a story, they don't just record the events -- they build a mental timeline of WHEN each thing
happened, and then they can REASON over it. Ask "did she train before or after the race?" and they answer "before",
even though the story said "She won the marathon; she had trained for months" -- the training is mentioned second but
happened first. Ask "were they arguing while she cooked?" and they read "while/during" as an overlap, not a sequence.
Ask "which took longer, the training or the race?" and they know months beat hours. Our reader now BUILDS that timeline
(it reorders flashbacks, reads "had left"/"before"/"after" into a chronological order), but it never REASONS over it:
nobody has ever ASKED it a before/after question as a QA task, it has no notion of two events OVERLAPPING in time, and
it has no notion of how LONG an event lasts. And the one test it does have was scored on 200-year-old prose (now banned)
against a gold that was cut from the reader's own tense reading, so the number tells us nothing about reasoning. Build
the reasoning: query the timeline for before/after when the telling order is scrambled by tense and "before/after/while"
words; read "while/during" as an overlap; and answer "which lasted longer?" -- on modern test text, beating the naive
"things happened in the order they were told" guess.

## 2. WHY THIS ONE
This is the TIME half of the comprehension->REASONING pivot (its sibling, `reason_over_the_causal_network...`, is the
CAUSE half, opened the same day). The whole situation-model program built the model; the TIME dimension in particular is
BUILT and WIRED (`sm.timeline_order`, default-on) and was graded EXCELLENT -- but that grade is EXTRACTION-level: it
proved the reader can RECONSTRUCT chronological order (register 1.000 vs a naive narration floor 0.272) on an ISOLATED
construction gold, and its real-prose evidence was LitBank (19c, now BANNED as load-bearing). It has never been asked a
temporal QUESTION on a modern benchmark, it has NO interval-overlap ("while/during") capability, and it has NO duration
capability at all. So this is where the timeline stops being a data structure and starts supporting inference. It REUSES
the timeline register + the magnitude-line order primitive; it does not re-extract tense or rebuild the before/after
register. It also retires two measurement debts the owner flagged: the 19c gold and the circular board temporal gold.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)
- **PINNED (the computation):** a reader indexes events on a mental TIMELINE -- the TIME dimension of the event-indexing
  situation model (Zwaan 1996; Zwaan & Radvansky 1998): a temporal shift is an event boundary and costs reading time,
  and the reader tracks WHEN each event sits relative to a moving reference time. Event order comes from grammatical
  tense/aspect -- Reichenbach's (1947) E/R/S model: past perfect ("had trained") places the event BEFORE the reference
  time, simple past AT it -- and from explicit temporal connectives (before/after/when/while/since/by-the-time; Bestgen &
  Vonk 2000). The DEFAULT is the narrative ICONICITY assumption -- telling order == event order (Zwaan; Dowty 1986;
  Grice's "be orderly") -- OVERRIDDEN by tense/aspect + explicit markers. OVERLAP ("while/during") is an interval
  relation, not a point order: at the computational level this is Allen's (1983) interval algebra (before/after/meets/
  overlaps/during/starts/finishes/equals) over event START/END intervals, which aspect supplies (perfective = a bounded
  interval; imperfective/progressive = an ongoing one). Neural: the hippocampal-entorhinal system encodes temporal
  context / event sequence (time cells, Eichenbaum 2014) -- episodic sequence memory, the same machinery as the SPACE
  dimension. DURATION rests on two brain systems: interval timing (SMA / striatal-cerebellar) for the magnitude, and
  SEMANTIC event-duration knowledge (typical durations of event types -- "a war lasts years, a glance a second"; Zhou et
  al. 2019).
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the QA readout (how a surface before/after/overlap/duration
  question maps to a timeline query); the interval-endpoint rule for overlap (event start/end read off aspect + the
  connective); the duration representation (the LANDED `transitive_ordering` magnitude line as graded relative-duration,
  vs an event-type duration prior for typical duration); and the abstention thresholds. **Copy the COMPUTATION** (index
  events on the timeline; Reichenbach place; Allen intervals for overlap; a magnitude line for relative duration). SWEEP
  the thresholds / representation. LABEL the timeline<->interval<->duration composition as OUR-SYNTHESIS.
- **NOT brain-faithful:** assuming narration order == event order (that IS the iconicity floor to BEAT); a learned
  end-to-end temporal-QA model over the text; an external LLM at inference; treating the circular board temporal QA gold
  (cut from the reader's own tense reading) as a reasoning target; scoring the headline on 19c prose.

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE -- do not re-derive):**
  - The live reader BUILDS a queryable timeline: `sm.timeline_order` (whole-passage chronological EVENT ORDER incl.
    flashbacks) is default-ON (`timeline_register=True`, `situation_reader._read_timeline_register`), computed by the
    validated `experiments/_temporal_order_register.py` -- a `ComposedRegister` (default narration order OVERRIDDEN by
    tense/aspect + connectives), exposing `before(x, y)` / `order()`, with a discrete toposort as primary and the
    continuous `transitive_ordering` magnitude line layered as a graded-confidence read-out, plus the clause-level
    pluperfect binder for inverted "had"-flashbacks. This is the timeline you REASON over, not rebuild.
  - `hdlab/transitive_ordering.py` -- the magnitude-LINE order primitive (reproduces the human distance-effect signature
    + a calibrated margin): the candidate representation for relative DURATION and for interval endpoints/overlap.
    `hdlab/graded_temporal_context.py` (store clock, event-boundary drift) and `hdlab/temporal_trace.py` (episodic trace)
    are the episodic-sequence-memory side. `sm.events` carries per-event predicate/agent/sent_idx; tense/aspect is a
    faithful Reichenbach parse (the tense-preserving detector landed 2026-08-31).
  - The prior TIME SOLVED (`situation_model_has_no_tested_temporal_order_comprehension`, owner-DONE/EXCELLENT): register
    before/after 1.000 [1.000,1.000] vs the narration floor 0.272 [0.194,0.349]; info-free twin loses (p95 0.602);
    flashback positive control 1.000 vs 0.000; real-prose reorder base rate 8.74% (LitBank -- 19c, informational only).
    This is an EXTRACTION-level, CONSTRUCTION-gold, 19c result -- NOT a modern QA / overlap / duration reasoning number.
  - The board temporal QA gold is CIRCULAR: it is cut from `sm.events`, which shares its tense signal with the
    extraction, so a high score recovers the reader's own tense reading, not reasoning (`BRAIN_FOUNDATIONAL_AUDIT.md`
    instrument-coupling note; "temporal shares its tense signal with its gold -- withdraw-first"). Do NOT use it as the
    reasoning gold.
  - There is NO interval-OVERLAP ("while/during") capability and NO DURATION capability anywhere in `hdlab/` or the
    reader (verify by enumeration -- see VERIFY BEFORE YOU START). THAT ABSENCE, plus the untested modern-QA before/after,
    is the defect this problem targets.
- **INFERRED (you must prove):** that QUERYING the extracted timeline answers modern before/after and OVERLAP questions
  CI-separated over a surface-order (iconicity) floor that LOSES on the flashback/marker items (proving the tense/marker
  override is load-bearing, not a coincidence with telling order), AND that DURATION questions (relative "which lasted
  longer?" + typical) beat a duration-blind majority floor, with the info-free twin (shuffled temporal markers / shuffled
  tense) LOSING CI-separated, on MODERN non-circular gold -- OR a rigorous located NEGATIVE with the cause named and
  counted (e.g. relative-duration works on constructed intervals but the reader's real-prose aspect extraction is too
  sparse to set interval endpoints, so overlap collapses to point order; OR typical-DURATION is a commonsense-knowledge
  prior the timeline does not carry -- a MISSING event-type duration lexicon, enumerated -- so the duration slice is a
  DIFFERENT organ, not a timeline-reasoning result).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT re-extract the timeline or rebuild the `before(x, y)` register. That is the prior TIME line -- read
  `situation_model_has_no_tested_temporal_order_comprehension/{PROBLEM.md,SOLVED.md,OWNER_NOTES.md}` IN FULL: it built +
  wired the register, decided the discrete-vs-continuous representation BY MEASUREMENT, and drilled the extraction wall.
  This problem CONSUMES that timeline and REASONS over it (modern QA + overlap + duration).
- Do NOT re-derive tense/aspect parsing or the clause-pluperfect binder -- the tense-preserving Reichenbach detector is
  landed (`the_tense_agnostic_detector_drops_tense_needed_by_the_time_dimension`, integrated). REUSE it.
- Do NOT rebuild the belief timeline (`the_reader_has_no_belief_timeline_what_an_agent_knew_when`, integrated) -- that is
  belief-OVER-time (what an agent knew WHEN), a sibling that already consumes the temporal-order register. Credit it; do
  not extend it. This is TIME reasoning over the WORLD timeline, not the belief timeline.
- Do NOT collide with the CANDIDATE `transitive_comparison_reasoning_over_the_magnitude_ordering` -- that is general
  magnitude transitivity (A>B, B>C => A>C). REUSE its magnitude line for relative duration, but this problem is temporal
  before/after/overlap/duration QA on a modern temporal gold, a distinct deliverable.
- Do NOT use a 19c corpus (McGuffey/LitBank) as load-bearing gold, and do NOT use the circular board temporal QA gold.
  Do NOT answer by raw-text question-word overlap (that IS the surface-order floor). Do NOT use an external LLM.
- Run `python tools/before_you_start.py "<what you are about to do>"` and `tools/experiment_index.py query "temporal"` /
  `"duration"` / `"before"` / `"timeline"` / `"overlap"` / `"mctaco"` / `"tracie"` (SINGLE keywords) before building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: run `python tools/substrate_map.py` and `python tools/reader_capabilities.py` (confirm `timeline_register`
  is default-ON and see what `sm.timeline_order` / `sm.events` expose), skim `hdlab/`, so you build ON the existing
  organs, not beside them.
- READ IN FULL (build ON it, credit it): `notes/problems/situation_model_has_no_tested_temporal_order_comprehension/
  {PROBLEM.md, SOLVED.md, OWNER_NOTES.md}` and its `adjacent_components_brain_fidelity_map_2026-08-29.md`. Note it CLOSED
  extraction-level before/after; this problem is a different level (modern QA + overlap + duration REASONING).
- INSPECT what you REUSE: `experiments/_temporal_order_register.py` (`ComposedRegister`, `before`/`order`, discrete
  toposort + continuous magnitude line, clause-pluperfect binder); `hdlab/situation_reader.py` `_read_timeline_register`
  + `sm.timeline_order` + `sm.events`; `hdlab/transitive_ordering.py` (magnitude line -- duration/interval candidate);
  `hdlab/graded_temporal_context.py`; `hdlab/temporal_trace.py`; `hdlab/belief_timeline.py` (the sibling that already
  consumes the register).
- READ the audit temporal entries in `notes/BRAIN_FOUNDATIONAL_AUDIT.md`: the 2026-08-29 TIME-register entry, the
  2026-08-31 `timeline_register` live-wiring entry, and the QA-capstone instrument-coupling note (the circular temporal
  gold -- a temporal-REASONING gold must be non-circular).
- ENUMERATE the absence (an absence claim requires an enumeration, not a search):
  `grep -rin "overlap\|interval\|allen\|duration\|how_long\|lasts\|simultaneous" hdlab/ experiments/` and confirm nothing
  does interval-overlap or duration reasoning over the timeline. State how you enumerated in your submission.
- GOLD: no dedicated temporal corpus is on disk. You are PRE-AUTHORIZED to acquire an open MODERN temporal set under
  `data/corpora/<name>/` with a REPRODUCIBLE pinned fetch script in `experiments/` + a provenance note. Candidates:
  **MCTACO** (Zhou et al. 2019 -- modern MC temporal-commonsense QA covering event ORDER + DURATION + typical-time +
  frequency + stationarity; the flagship for order+duration in one set); **TRACIE** (Zhou et al. 2021 -- implicit-event
  start/end ORDER entailment built on ROCStories, whose source `data/corpora/roc_stories` + `story_cloze` are already on
  disk; the best fit for surface-order != event-order on narrative); **TB-Dense / MATRES** (Cassidy et al. 2014 / Ning et
  al. 2018 -- DENSE temporal relations incl. includes/is_included/simultaneous = the OVERLAP relations, on modern news --
  modern English, not 19c). Decide fit per slice (order/overlap = TRACIE/TB-Dense; duration = MCTACO), state provenance +
  license + n, and note any genre confound. Do NOT lean on 19c because it is better-powered -- close the power gap on
  modern data.

## 7. THE BAR
PASSES only with ALL of:
1. **A glass-box temporal reasoner OVER the extracted timeline** (built in `experiments/`, reasoning over
   `sm.timeline_order` / `_temporal_order_register`; REUSE the `transitive_ordering` magnitude line for graded duration +
   for interval endpoints, and Allen interval intersection for overlap), doing ALL THREE: (a) **BEFORE/AFTER** -- query
   the reordered timeline (Reichenbach place, not telling order); (b) **OVERLAP** -- read "while/during" and aspect into
   event START/END intervals and answer inclusion/overlap (Allen), not precedence; (c) **DURATION** -- relative ("which
   lasted longer?") off the magnitude line + typical/absolute where the gold demands it. NO external LLM. Copy the
   Zwaan/Reichenbach/Allen COMPUTATION; SWEEP the interval-endpoint rule / duration representation / abstention thresholds.
2. **Answers CI-separated over BOTH controls on MODERN non-circular gold:**
   (a) a **surface-order (iconicity) floor** recomputed on the same population -- assume telling order == event order --
   which MUST LOSE on the flashback/marker items (the naive answer is wrong exactly when a tense/"before"/"after"/"while"
   cue reorders the events; this is what proves the timeline query is load-bearing, not a coincidence with telling order);
   for DURATION items, a **duration-blind majority / most-frequent-answer floor** recomputed on that population; and
   (b) the **info-free twin** -- shuffle the temporal markers (before/after/while/since/by-the-time) and shuffle the tense
   labels, keeping the event set -- which LOSES CI-separated on the order, overlap, AND duration items.
   Report CI half-width + null p95; recompute each floor on the item's OWN population; NO number crosses populations
   (report before/after, overlap, and duration SEPARATELY, and aggregate). A **POSITIVE control** the floor CANNOT get:
   a flashback / "before"-fronted / past-perfect item where telling order != event order, and a "while/during" item where
   the relation is inclusion, not precedence.
3. **Isolates the REASONING from extraction** -- ablate the reasoner to a narration-order readout (and, for overlap, to a
   point-order readout with no intervals) and show the lift is the timeline QUERY (Reichenbach override + interval overlap
   + duration magnitude), not re-running the tense extraction or the before/after register.
4. **One-screen summary:** timeline source -> modern gold + provenance -> floors -> twin -> before/after + overlap +
   duration accuracy -> what breaks -> verdict. Heavy -> REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "before/after and overlap clear the iconicity floor CI-separated on the modern
gold, but the DURATION slice does not beat the majority floor because typical-duration is a commonsense-KNOWLEDGE prior
the timeline does not carry -- the reader has no event-type duration lexicon; located + enumerated as a distinct
next-organ"; OR "the interval-overlap reasoner is sound on constructed intervals -- 1.00 vs the point-order control --
but the reader's REAL extracted aspect is too sparse to set start/end endpoints on N of M real items, so overlap collapses
to point order; the bottleneck is aspect extraction, enumerated with counts").

## 8. FILES AND ENTRY POINTS
- **REUSE (integrated/wired -- do NOT rebuild):** `experiments/_temporal_order_register.py` (`ComposedRegister`,
  `before`/`order`, discrete toposort + continuous magnitude line, clause-pluperfect binder); `hdlab/situation_reader.py`
  (`sm.timeline_order` via `_read_timeline_register`, `sm.events`, the tense/aspect parse); `hdlab/transitive_ordering.py`
  (magnitude line -- relative duration + interval endpoints); `hdlab/graded_temporal_context.py`; `hdlab/temporal_trace.py`;
  `hdlab/belief_timeline.py` (the sibling belief-over-time consumer of the register).
- **Gold:** none on disk -- acquire a MODERN temporal set under `data/corpora/<name>/` with a pinned fetch script in
  `experiments/`: MCTACO (order+duration commonsense QA), TRACIE (implicit-event order over ROCStories -- source on disk),
  TB-Dense / MATRES (dense interval/overlap relations, modern news). No 19c load-bearing gold.
- **Motivation + fence:** `situation_model_has_no_tested_temporal_order_comprehension/SOLVED.md` (the extraction-level
  parent to build ON); the circular board temporal gold (`BRAIN_FOUNDATIONAL_AUDIT.md` instrument-coupling note). Audit +
  heavy->REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`). Build in `experiments/` + `verification/`; strategy lands
  any hdlab change (Q111). Fold an **AUDIT UPDATE** into `notes/BRAIN_FOUNDATIONAL_AUDIT.md` sec.2b (the TIME dimension:
  extraction-level tested; reasoning-level = this result).

## DO NOT QUOTE / DO NOT REDO
- Do NOT quote the TIME register's construction-gold 1.000-vs-0.272 (or the 8.74% LitBank base rate) as a modern temporal
  REASONING number -- it is an EXTRACTION-level, isolated-construction, 19c-adjacent measurement on a different scorer and
  population. No number crosses scorers/populations; recompute every floor on the item's own population.
- Do NOT use the board's temporal QA gold as the reasoning gold -- it is circular (cut from `sm.events`, which shares its
  tense signal with the extraction), so a high score recovers the reader's own tense reading, not reasoning.
- Do NOT re-extract tense/aspect, rebuild the `before(x, y)` register, or rebuild the belief timeline -- all are landed.
  The timeline + tense parse are the INGREDIENTS; the deliverable is REASONING over the timeline -- modern before/after +
  overlap + duration.
- Do NOT lean on a 19c corpus (McGuffey/LitBank) as load-bearing gold (BANNED 2026-09-06 -- a 19c number is informational
  only; the MODERN number counts); do NOT use an external LLM at inference (the invariant). Strategy owns any hdlab landing.

---

**TLDR (plain English):** Our reader already works out the real order of events in a story even when they are told out of
order (flashbacks, "before/after", "had done"). But it has never been ASKED a timing question as a test, it has no idea of
two things happening AT THE SAME TIME ("while/during"), and no idea of how LONG anything lasts -- and its one existing test
was run on 200-year-old text against a gold copied from its own reading, so it proves nothing about reasoning. Build the
reasoning step -- answer "did X happen before or after Y?", "were they overlapping?", and "which lasted longer?" -- and
prove on MODERN test text that it beats the naive "things happened in the order they were told" guess, with a
scrambled-cue version dropping to chance.

**QUESTIONS:** none.

**NEXT STEPS:** the solver runs VERIFY BEFORE YOU START (confirm `sm.timeline_order` is live and that nothing reasons
about overlap or duration), acquires a modern temporal gold (MCTACO / TRACIE / TB-Dense) with a pinned fetch script + an
info-free twin, builds the glass-box timeline reasoner (before/after via Reichenbach over the reordered timeline, overlap
via Allen intervals, duration via the magnitude line + an event-type prior where needed), and reports the margin over the
surface-order (iconicity) and duration-blind floors with CI half-width + null p95 -- or a located negative naming the
exact cause.
