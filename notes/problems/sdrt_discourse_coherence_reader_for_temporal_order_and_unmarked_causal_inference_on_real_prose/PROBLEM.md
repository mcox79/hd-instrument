---
slug: sdrt_discourse_coherence_reader_for_temporal_order_and_unmarked_causal_inference_on_real_prose
status: INTEGRATED
review:
review_text:
---

# PROBLEM: on real prose the temporal ORDER/OVERLAP and the CAUSAL links a reader needs are carried by DISCOURSE COHERENCE relations that are almost always UNMARKED, and the substrate has no reader for them -- build a glass-box SDRT-lite coherence reader (Narration / Result / Explanation / Background / Elaboration) that INFERS the relation from causal-world-knowledge (not surface connectives), corrects temporal order/overlap where the relation overrides telling order, and feeds the causal reasoner the unmarked causal links it currently misses -- proven CI-separated over the iconicity/adjacency floors on a modern gold with a shuffled-coherence-label twin losing.

**slug:** `sdrt_discourse_coherence_reader_for_temporal_order_and_unmarked_causal_inference_on_real_prose`
-- **opened:** 2026-09-06 by the strategy session. This is the SHARED top wall named INDEPENDENTLY by BOTH
just-integrated inference organs: the temporal reasoner (`hdlab/temporal_reasoner.py`, owner-DONE) named it as its
Wall-1/Wall-2 next-organ ("an SDRT-lite discourse-relation reader ... needs causal-world-knowledge inference, not just
connectives -- the reversal is inferred, not marked"), and the causal reasoner (`hdlab/causal_reasoner.py`, owner-DONE)
hit the SAME wall from the other side (its extracted narrative network is too sparse because unstated cross-sentence
causal links are never inferred). The two reasoners are BUILT and landed; what neither has is the reader that INFERS the
unmarked coherence relation that both would consume. **status:** CANDIDATE -- a COUPLING + build problem. You build +
validate in `experiments/`; strategy lands any hdlab change (Q111). Glass-box, a static world-knowledge asset is
admissible, NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's; provisional -- RE-RANK per the owner):** filed at `7` because it
> is high-value (the shared top wall of two landed reasoners; unlocks both at once) but it is a genuine BUILD with real
> risk, not a wiring job -- the world-knowledge coverage wall it must cross is ALREADY LOCATED at a number (the causal
> reasoner's CSKG retrieval route covered only 17.3% of true narrative cause-pairs; the one method that beat topical
> with no LLM, the generative simulator, won by only +0.030). So it sits below the cheaper loop-closure / wiring jobs
> that reuse landed organs directly, and above the merely-important. It stays CANDIDATE until promoted. Set the real
> priority when it goes CANDIDATE -> OPEN.

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
> **(PHASE DIAGRAM -- the substrate is not locked to one regime.)** The substrate's operating point -- store DENSITY vs SPARSITY, dimensionality, binding regime, capacity, decay/gain, indexed-vs-superposed organization -- is FREE to change at ANY time, PER ORGAN. These are parameters to SWEEP, never fixed constraints. A wall "at this configuration" is a cue to MOVE the operating point on the phase diagram BEFORE ever calling it a ceiling.
>
> **(FULL-STACK UPSTREAM -- prototype THIS component AND its upstream, to EXCEL and EXCEED.)** Fully prototype THIS component AND the upstream brain-foundational component it depends on (and ALL the way upstream if the chain is deeper), and SHOW the capability can EXCEL and EXCEED -- make it happen. Then: (a) CONFIRM no other downstream consumer of the upstream optimization REGRESSES; (b) CONFIRM whether those other consumers should be REVISITED to be more brain-foundational, now making use of the newly-optimized upstream capabilities; (c) make SURE, VIA RESEARCH, that what you implement upstream is genuinely brain-foundational. **THE ONLY WAY YOU OVERCOME THIS WALL IS FOR EVERY COMPONENT -- YOU AND UPSTREAM -- TO BE BRAIN-FOUNDATIONAL.** Any wall you encounter must be FULLY RESEARCHED: the brain does it, so we can too -- and to do so we must UNDERSTAND it fully.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When we read a story, most of the connections between sentences are never spelled out. "Max fell. He had spilt water."
-- no word tells you the spilt water came FIRST and CAUSED the fall, yet every reader knows both. The order is reversed
from how it was told, and the cause-and-effect link has no "because" to mark it. A good reader fills these in
automatically, using what they know about how the world works (wet floors make people slip). Our reader cannot do this.
It has two new skills we just gave it -- one that reasons about the timing of events, one that reasons about chains of
cause and effect -- but both are starved: the timing one assumes events happened in the order they were told (so it gets
flashbacks backwards), and the cause one only sees a link when the sentence literally says "because" or "so" (so it
misses almost all of them). The missing piece is the reader that decides what KIND of connection holds between two
sentences -- is the second one continuing the story, explaining the first, or describing the background? -- by reasoning
about plausibility, not by hunting for a connective word. Build that reader, and it does two jobs at once: it tells the
timing reasoner when the told order is wrong, and it hands the cause reasoner the unmarked cause-and-effect links it
never sees. The job is to prove, on modern test text, that inferring these connections really recovers the right order
and the right causes where the naive shortcuts fail -- with a scrambled-connections version falling apart, so we know it
is the real inference doing the work.

## 2. WHY THIS ONE
It is the ONE missing organ that BOTH just-integrated reasoners named as their top wall, from opposite sides. The
temporal reasoner's SOLVED closes with it (Wall-1: real-prose overlap "needs ... SDRT discourse relations ... the 'Max
slipped / had spilt water' reversal is inferred, not marked"; Wall-2: "the rest of event order rides on ... SDRT
discourse relations ... Explanation reverses surface order"; its P4 next-step is literally "SDRT world-knowledge
discourse reader, coupled to the causation organ"). The causal reasoner's SOLVED hit the SAME wall as extraction
sparsity: its live narrative network is 0.077 cross-sentence edges/story because unstated causal links are never
inferred, and its entire residual collapses to one axis -- edge CORRECTNESS = the directed causal-world-knowledge gate.
These are not two problems; they are one. The coherence relation the SDRT reader infers is EXACTLY the latent variable
that (a) tells the timeline when the coherence relation overrides telling order and (b) supplies the causal network the
edges it is missing -- the Trabasso causal network the causal reasoner WALKS is BUILT by this coherence inference
(Graesser/Singer/Trabasso constructionist "search after meaning"). Solving it turns two proven-sound-but-starved
reasoners into two reasoners with something real to reason over. The marker-only shortcut is already a proven located
negative (0.50 < iconicity 0.70), so the value is specifically in the world-knowledge inference, which is the hard part.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)
- **PINNED (the computation).** A reader does NOT read discourse structure off connective words; it INFERS the coherence
  relation between adjacent discourse units by defeasible / abductive reasoning over world knowledge, and the inferred
  relation CONSTRAINS the temporal and causal interpretation (Hobbs 1985; Hobbs, Stickel, Appelt & Martin 1993
  "Interpretation as Abduction"; Kehler 2002; the constructionist "search after meaning" -- Graesser, Singer & Trabasso
  1994; Kintsch 1988 construction-integration). SDRT (Lascarides & Asher 1993; Asher & Lascarides 2003) makes the
  temporal/causal consequences explicit via defeasible axioms (DICE): **Narration** => temporal progression, no overlap;
  **Result** => forward causation (cause told first, then effect); **Explanation** => the second unit CAUSES the first,
  so surface order is REVERSED (the "Max fell. He had spilt water." flashback -- no marker); **Background** => the two
  states/events OVERLAP; **Elaboration** => the second is a subevent of the first (overlap / part-of). Lascarides &
  Asher's minimal pair ("Max switched off the light. The room was pitch dark." = Result/sequence vs "Max opened the
  door. The room was pitch dark." = Background/overlap -- IDENTICAL aspect, opposite reading) is the proof that aspect
  alone cannot resolve this and the coherence relation is the deciding variable. The discriminator between Explanation
  and Narration is causal PLAUSIBILITY (does event B plausibly cause / explain event A?) -- a world-knowledge judgement,
  the "causality-by-default" reading readers apply (Sanders). This is the SAME generative causal knowledge the causal
  reasoner's simulator composes; here it TYPES the discourse edge.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt).** The world-knowledge SOURCE that supplies the causal-plausibility
  contrast (REUSE the causal reasoner's generative simulator -- force dynamics + affect-appraisal congruence + event-type
  cascade, the U8 route that BEAT topical with no LLM; sweep which engines compose); the relation inventory granularity
  (the five above vs a coarser sequence/overlap/reverse triple); the confidence threshold at which an inferred relation
  is allowed to OVERRIDE the iconicity/adjacency default (like the causal reasoner's U5 cue-integration: default to the
  prior, override only on a CONFIDENT relation); and the mapping from a relation to a timeline edit / an inserted causal
  link.
- **NOT brain-faithful (do NOT do).** Reading the coherence relation off surface CONNECTIVES only (that is the PROVEN
  located negative -- explicit causal markers are sparse (10 pairs on TB-Dense) and ambiguous (as/since/for), 0.50 <
  iconicity 0.70); a learned end-to-end discourse-relation classifier; an external LLM at inference; treating the two
  consumers' landed headline numbers as this problem's result (they are the CONSUMERS' baselines, not the coherence
  lift).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE -- do not re-derive):**
  - The temporal reasoner FALLS BACK TO ICONICITY on the majority of pairs. `hdlab/temporal_reasoner.py` `before()`
    resolves by an explicit tense/connective CUE path -> a TIMEX DATE path -> ELSE iconicity (telling order == event
    order). On TB-Dense (1990s newswire, modern) only ~12% of pairs carry a cue and **47.6% are reverse-order**, so on
    the reverse-order subset iconicity scores **0.0000** -- the coherence relation is the only thing that can recover
    those, and the reader has no channel for it.
  - The SDRT causal-MARKER channel is a proven LOCATED NEGATIVE. `experiments/exp_temporal_reason_more_upgrades_v1.py`:
    explicit causal markers are sparse + ambiguous -> **0.50 < iconicity 0.70**. The SOLVED states the real lever is
    CAUSAL-WORLD-KNOWLEDGE inference, not markers -- "the 'Max slipped / had spilt water' reversal has no marker at all."
  - The causal reasoner's network is STARVED of unmarked links. `hdlab/causal_reasoner.py` consumes `sm.causal_links`,
    built by `situation_reader._read_causation` from connectives + within-sentence mental bridges only; on ROCStories it
    is **0.560 edges/story, 0.077 cross-sentence, 3.2% support a >=2-hop chain**. On TellMeWhy (directed human why-gold,
    on disk) the multi-hop cause-ID win is confined to the **non-adjacent-cause subset (~17%)** where adjacency/recency
    score **0.0000**; the residual is the directed causal-knowledge wall (the CSKG retrieval route covered only **17.3%**
    of true cause-pairs; the generative SIMULATOR was the FIRST method to beat topical, **+0.030 CI-sep, NO LLM**).
  - The field agrees the channel is discourse relations, not markers/aspect: Lascarides & Asher 1993 (aspect cannot
    resolve overlap; Explanation reverses order); D'Souza & Ng 2013 (discourse-relation features add MORE than aspectual
    granularity).
- **INFERRED (you must prove):** that a glass-box SDRT-lite coherence reader, inferring the relation from
  causal-world-knowledge (NOT connectives), (a) recovers temporal order/overlap CI-separated over the iconicity floor ON
  THE SUBSET where the coherence relation overrides surface order (the positive control iconicity CANNOT get), AND/OR (b)
  recovers unmarked causal links the connective-only extractor + adjacency floor miss -- with the info-free twin
  (SHUFFLED coherence labels) LOSING CI-separated, floors recomputed per population, no live-consumer regress; OR a
  rigorous LOCATED NEGATIVE with the cause named and counted (most likely: the world-knowledge asset covers too few of
  the causal-plausibility contrasts needed to discriminate Explanation from Narration on real prose, so on N of M items
  the relation cannot be inferred and the reader falls back to iconicity/adjacency -- the same coverage wall the causal
  reasoner located at 17.3%, enumerated with counts).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT re-run the causal-MARKER channel -- it is a landed LOCATED NEGATIVE (0.50 < iconicity 0.70,
  `exp_temporal_reason_more_upgrades_v1.py`). The whole point of this problem is the world-knowledge inference the
  marker channel lacked.
- Do NOT re-derive the RETRIEVAL routes the causal reasoner already closed: the CSKG directed-causal-KB gate (17.3%
  coverage, `exp_causal_reasoner_cskg_v1.py`) and the event-type directed gate (0.28 < topical 0.32, U2). Both are
  coverage-bounded located negatives. The proven direction is the generative SIMULATOR (`exp_causal_reasoner_simulate_v1.py`,
  U8) -- BUILD ON it (compose/deepen the engines), do not rebuild retrieval.
- Do NOT rebuild the temporal reasoner or the causal reasoner -- both are landed (owner-DONE, promoted VERBATIM). You
  COUPLE to them: read `hdlab.temporal_reasoner` (before/overlaps/allen + the iconicity fallback + `from_text`) and
  `hdlab.causal_reasoner` (`CausalGraph.from_edges`, `ultimate_cause`, `is_necessary`).
- Do NOT use a 19c corpus (McGuffey / LitBank) as load-bearing gold, and do NOT use an external LLM at inference.
- Run `python tools/before_you_start.py "<what you are about to do>"` and `tools/experiment_index.py query "discourse"`
  / `"coherence"` / `"sdrt"` / `"explanation"` / `"narration"` / `"background"` / `"rst"` (SINGLE keywords) before building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: run `python tools/substrate_map.py` and `python tools/reader_capabilities.py`; confirm the temporal
  reasoner's `before()` falls back to iconicity and the causal reasoner builds a `CausalGraph` over `sm.causal_links`;
  skim `hdlab/` so you build ON the existing organs, not beside them.
- READ IN FULL (build ON them, credit them): `notes/problems/reason_over_event_time_order_and_duration_on_a_modern_gold/
  SOLVED.md` (the Wall-1/Wall-2 discourse findings, the SDRT causal-marker LOCATED NEGATIVE, the "P4 SDRT world-knowledge
  reader coupled to the causation organ" follow-on) and `notes/problems/reason_over_the_causal_network_multi_hop_chains_
  and_counterfactuals/SOLVED.md` (the non-adjacent/unmarked-cause wall, the phase diagram collapsing the residual to edge
  correctness c, U7 CSKG 17.3%, U8 simulator +0.030).
- INSPECT what you COUPLE to: `hdlab/temporal_reasoner.py` (`TemporalReasoner.before` / `.overlaps` / `.allen`, the
  iconicity fallback, `from_text`, `date_anchors`); `hdlab/causal_reasoner.py` (`CausalGraph`, `from_edges`,
  `ultimate_cause`, `is_necessary`, `AdjacencyFloor`); `hdlab/situation_reader.py` `_read_causation` (how `sm.causal_links`
  is built -- connective + within-sentence mental bridge, misses cross-sentence) and `_read_timeline_register`;
  `experiments/exp_causal_reasoner_simulate_v1.py` (the U8 generative simulator -- the world-knowledge engine to reuse);
  `experiments/exp_temporal_reason_more_upgrades_v1.py` (the marker located negative).
- ENUMERATE the wiring reality (an absence claim requires an enumeration, not a search): grep for every LIVE consumer of
  the two reasoners (`grep -rin "temporal_reasoner\|causal_reasoner\|CausalGraph" hdlab/ experiments/ verification/`) to
  confirm your coherence corrections are ADDITIVE (a new field / an override gated on confidence, not a rewrite of
  `sm.causal_links` / the timeline). State how you enumerated in your submission.
- GOLD: you are PRE-AUTHORIZED to acquire an open MODERN gold under `data/corpora/<name>/` with a REPRODUCIBLE pinned
  fetch script in `experiments/` + a provenance note. On disk already: TB-Dense (`data/corpora/tb_dense`, the
  reverse-order subset where iconicity=0 is the TEMPORAL-OVERRIDE positive control), TellMeWhy (`data/corpora/tellmewhy`,
  the non-adjacent-cause subset is the UNMARKED-CAUSAL positive control), Story Cloze (`data/corpora/story_cloze`, use
  the cross-context twin for coherence, per the temporal SOLVED's Schwartz-artifact caution). For direct discourse-relation
  labels (if you validate the relation reader itself rather than only the downstream correction), prefer GUM
  (`data/corpora/gum/`, modern multi-genre, has eRST/discourse relations) or RST-DT; a constructed minimal-pair gold
  (Lascarides-Asher-style Explanation-vs-Narration pairs) is admissible ONLY as a can-fail mechanism control, LABELLED as
  such, alongside the real-prose slices. State provenance + license + n. Do NOT lean on 19c because it is better-powered.

## 7. THE BAR
PASSES only with ALL of:
1. **A glass-box SDRT-lite coherence reader (built + validated in `experiments/`; strategy lands the hdlab change, Q111).**
   INFER the coherence relation (Narration / Result / Explanation / Background / Elaboration) between adjacent discourse
   units from CAUSAL-WORLD-KNOWLEDGE inference (REUSE the causal reasoner's generative simulator / affect-appraisal
   congruence / a static causal-plausibility asset -- glass-box, NO external LLM), NOT surface connectives. Map the
   relation to (a) a timeline correction fed to `hdlab.temporal_reasoner` (Explanation/flashback => REVERSE told order;
   Background/Elaboration => OVERLAP; Narration => sequence) and (b) an inserted UNMARKED causal link fed to
   `hdlab.causal_reasoner` (Result/Explanation => a cause->effect edge). Copy the Lascarides-Asher / Hobbs
   abductive-coherence COMPUTATION; SWEEP the world-knowledge source, the relation granularity, the override-confidence
   threshold.
2. **CI-separated over the naive floor on the OVERRIDE slice AND/OR recovers unmarked causal links, on MODERN gold,
   reported separately AND aggregated:** (a) TEMPORAL OVERRIDE -- on the subset where the coherence relation overrides
   surface order (TB-Dense reverse-order subset, where the ICONICITY floor recomputed on that population = 0.0000, the
   positive control it CANNOT get), the coherence reader recovers order CI-separated over iconicity; (b) UNMARKED CAUSAL
   -- on the non-adjacent / unmarked-cause subset (TellMeWhy non-adjacent-cause, where ADJACENCY / RECENCY = 0.0000), the
   coherence reader recovers the causal link CI-separated over BOTH the connective-only extractor and the adjacency floor.
   Gate on the floor's UPPER CI bound; report CI half-width + null p95; recompute each floor on the item's OWN population;
   NO number crosses populations.
3. **The info-free twin LOSES CI-separated:** SHUFFLE the INFERRED coherence labels (keep the same relation-count
   distribution / balance) -- this proves the correction uses THIS passage's inferred relation, not a shape artifact.
   (For the Story Cloze coherence slice, the CROSS-CONTEXT twin is the load-bearing one that defeats the style artifact.)
4. **NO-regress on the two live consumers + the world-knowledge is load-bearing, not the marker.** The corrections are
   ADDITIVE: with the coherence channel OFF, the temporal reasoner's `before()`/`overlaps()` and the causal reasoner's
   answers are byte-identical (override only on a CONFIDENT inferred relation, like the causal reasoner's U5
   cue-integration default-to-prior). And show the CONNECTIVE-ONLY channel (the proven located negative) does NOT clear
   the floor on the SAME population while the world-knowledge coherence inference does -- so the lift is the INFERRED
   relation. A POSITIVE control the connective/iconicity floors CANNOT get: an unmarked Explanation ("Max fell. He had
   spilt water.") -- surface order reversed, no connective.
5. **One-screen summary:** world-knowledge source -> modern gold + provenance -> iconicity/adjacency floor -> twin ->
   temporal-override + unmarked-causal margins (with CI half-width + null p95) -> connective-only vs world-knowledge
   isolation -> what breaks -> verdict. Heavy -> REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "the reader infers Explanation/Background correctly on the constructed
minimal-pair control, but on real modern prose the world-knowledge asset covers too few causal-plausibility contrasts to
discriminate Explanation from Narration, so on N of M items the relation cannot be inferred and the reader falls back to
iconicity/adjacency -- the bottleneck is causal-world-knowledge COVERAGE on real prose, the same wall the causal reasoner
located at CSKG 17.3%, enumerated with counts"; OR "the temporal-override slice clears iconicity CI-separated but the
unmarked-causal slice does not, because the inferred coherence edges are TOPICAL not directed-causal -- located and
counted, the causal reasoner's correctness-axis c").
**STRETCH (name it, do NOT require it):** feed the inferred coherence structure into the reader's forward-prediction /
segmentation loop (an unexpected relation is a coherence break) and into the parse attachment competition, and show it
lifts event-boundary detection and/or attachment on a modern gold -- report it as an additional arm if you reach it.

## 8. FILES AND ENTRY POINTS
- **COUPLE (landed / integrated -- do NOT rebuild):** `hdlab/temporal_reasoner.py` (`TemporalReasoner.before` /
  `.overlaps` / `.allen`, the iconicity fallback, `from_text`, `date_anchors`); `hdlab/causal_reasoner.py` (`CausalGraph`,
  `from_edges`, `ultimate_cause`, `is_necessary`, `AdjacencyFloor`); `hdlab/situation_reader.py` `_read_causation` /
  `_read_timeline_register` (how `sm.causal_links` + the timeline are built -- your corrections are ADDITIVE over these).
- **REUSE (the world-knowledge inference direction):** `experiments/exp_causal_reasoner_simulate_v1.py` (the U8
  generative simulator -- force dynamics + affect-appraisal + event-type cascade, the first to beat topical with NO LLM);
  `hdlab/affect_lexicon` (Warriner-valence appraisal congruence); `hdlab/event_type` (MENTAL_TRIGGER->MENTAL_OUTCOME).
- **CONSUME (the located negatives -- do NOT re-derive):** `experiments/exp_temporal_reason_more_upgrades_v1.py` (the
  causal-marker channel 0.50 < iconicity); `experiments/exp_causal_reasoner_cskg_v1.py` (CSKG 17.3% coverage).
- **Gold:** TB-Dense (`data/corpora/tb_dense`, reverse-order subset = temporal-override positive control), TellMeWhy
  (`data/corpora/tellmewhy`, non-adjacent-cause subset = unmarked-causal positive control), Story Cloze
  (`data/corpora/story_cloze`, cross-context twin); acquire GUM/RST-DT under `data/corpora/<name>/` with a pinned fetch
  script if you validate the relation reader directly; a constructed Lascarides-Asher minimal-pair gold is a labelled
  mechanism control only.
- **Motivation + fence:** the two SOLVED.md (temporal + causal); `notes/BRAIN_FOUNDATIONAL_AUDIT.md` Tier 5 (TIME) +
  the causal-network entry. Build in `experiments/` + `verification/`; strategy lands any hdlab change (Q111). Heavy ->
  REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`). Fold an **AUDIT UPDATE** into the audit (the discourse-coherence
  reader is now built and coupled to both inference organs, or a located negative naming the world-knowledge-coverage
  bottleneck).

## DO NOT QUOTE / DO NOT REDO
- Do NOT quote the temporal reasoner's before/after 0.5933 vs iconicity 0.5236 (or the overlap 0.9938 / relative-duration
  1.0 / the causal L1 1.000 / WIQA 0.5852 / TellMeWhy figures) as THIS problem's result -- they are the CONSUMERS' landed
  numbers on their own populations. The bar here is a NEW modern-gold coherence-override / unmarked-causal-recovery
  result with the shuffled-coherence-label twin + no-regress, floors recomputed on the item's own population. No number
  crosses scorers / populations.
- Do NOT re-run the causal-marker channel (0.50 < iconicity, located negative), the CSKG retrieval gate (17.3%), or the
  event-type directed gate (0.28 < topical) -- all landed located negatives. The world-knowledge SIMULATOR (+0.030
  CI-sep, no LLM) is the proven direction to build ON, not retrieval.
- Do NOT rebuild the temporal or causal reasoner -- couple to them; the corrections are ADDITIVE (a confident override /
  a new inferred-link field), never a rewrite of `sm.causal_links` or the timeline.
- Do NOT read coherence off connectives only (the located negative). Do NOT lean on a 19c corpus as load-bearing gold
  (BANNED 2026-09-06 -- a 19c number is informational only); do NOT use an external LLM at inference (the invariant).
  Strategy owns any hdlab landing.

---

**TLDR (plain English):** When we read, we silently fill in how one sentence connects to the next -- which came first,
what caused what -- even though the text almost never says so out loud. Our reader just got two new skills, one for the
timing of events and one for chains of cause and effect, but both are half-blind: the timing one assumes things happened
in the order they were told (so it gets flashbacks backwards), and the cause one only notices a link when the sentence
literally says "because." The fix is the reader that works out what KIND of connection holds between two sentences by
reasoning about what is plausible in the world, not by hunting for a joining word. That one reader feeds both: it tells
the timing skill when the told order is wrong, and it hands the cause skill the unspoken cause-and-effect links it never
sees. The job is to prove on modern test text that this inference really recovers the right order and the right causes
exactly where the naive shortcuts fail -- with a scrambled-connections version falling apart, so we know the real
inference is doing the work.

**QUESTIONS:** none.

**NEXT STEPS:** the solver runs VERIFY BEFORE YOU START (confirm the temporal reasoner falls back to iconicity and the
causal reasoner builds its graph over `sm.causal_links`), reads both SOLVED.md in full, builds a glass-box SDRT-lite
coherence reader driven by the causal reasoner's world-knowledge simulator (not connectives) in `experiments/`, couples
its output to `hdlab.temporal_reasoner` (order/overlap correction) and `hdlab.causal_reasoner` (unmarked causal links),
and reports the margin over the iconicity floor on the TB-Dense reverse-order slice and over the adjacency floor on the
TellMeWhy non-adjacent-cause slice, with the shuffled-coherence-label twin and the connective-only-vs-world-knowledge
isolation -- or a located negative naming the exact cause (most likely causal-world-knowledge coverage on real prose).
The STRETCH (coherence into the forward-prediction/segmentation loop + the parse attachment competition) is named as the
deeper follow-on.
