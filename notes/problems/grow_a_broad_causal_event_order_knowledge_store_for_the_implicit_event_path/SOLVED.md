---
problem: grow_a_broad_causal_event_order_knowledge_store_for_the_implicit_event_path
status: SOLVED
bar: "PASSES only with ALL of: 1. A BROADER glass-box causal / event-order KNOWLEDGE STORE, built + validated in experiments/ (the seed verb-pair-order store EXTENDED with (a) MORE narrative + causal-cue corpora and (b) CAUSAL / IRREVERSIBILITY typing, every mined association admitted through the consolidation gate). 2. WIRED to the temporal reasoner's IMPLICIT-EVENT / abstention path as a STRENGTH-GATED OVERRIDE on the iconicity default; headline = implicit-event ordering ACCURACY and COVERAGE, CI-separated over BOTH (a) the current ABSTENTION baseline AND (b) the SEED store's 0.6022@29% floor recomputed on the SAME population, on a MODERN gold. 3. The info-free twin LOSES CI-separated (shuffle the store's verb-pair orders). 4. The COVERAGE lever is named and measured (29% -> N%) with a can-fail POSITIVE control the seed cannot get. 5. NO-regress full-stack (narrated before/after / overlap / duration BYTE-IDENTICAL). 6. One-screen summary. A rigorous NEGATIVE is a FULL PASS."
result: "TRACIE iid TEST (implicit-event before/after, n=1924, MODERN ROCStories-derived gold; paired clustered bootstrap over stories). BROADER store (tense-agnostic UPOS re-mine of 98,161 ROCStories -> 454,129 ordered verb-pairs, +causal-cue blend), UNGATED headline: FULL accuracy 0.5655 vs SEED floor 0.5296 delta +0.0359 CI[+0.0117,+0.0616] CI-SEP (hw 0.025, null_p95 0.0217); vs ABSTENTION floor 0.5000 delta +0.0655 CI[+0.0403,+0.0911] CI-SEP. COVERAGE 0.29 -> 0.607 (2.1x); per-covered-pair accuracy 0.606 (ungated) rising to 0.65-0.68 under the confidence gate (matches/exceeds the seed's 0.6022). AS-WIRED under the reasoner's EXISTING gate (evidence>=10, |p-0.5|>=0.10, zero code change): 0.5582 @ cov 0.326, +0.0286 CI[+0.0080,+0.0496] CI-SEP."
floor: "SEED store full accuracy 0.5296 @ cov 0.29 (the landed tense-gated mine, recomputed here on the SAME n=1924 population, abstain->majority) -- the strongest floor actually run; ABSTENTION baseline 0.5000 (majority). The seed's per-covered 0.6022@29% is matched-or-beaten on covered pairs (0.606 ungated / 0.65-0.68 gated) while coverage more than doubles."
controls: "(1) INFO-FREE TWIN -- shuffle each pair's directional orientation, node set + counts kept: collapses to 0.4896 (below chance), headline beats it +0.0759 CI[+0.0434,+0.1103] CI-SEP -> the EXTRACTED ORDER is load-bearing, not corpus frequency. (2) NARRATED BYTE-IDENTITY -- swapping the store cannot touch the narrated path (the reasoner consults the store ONLY when a key is off the timeline); verified identical before() on all both-on-timeline pairs across 3 texts; landed reasoner witness 18/18 unchanged (hdlab untouched). (3) POSITIVE CONTROL -- 41 pairs the broader store places correctly where the seed ABSTAINS (e.g. hold-before-hand: you hold the paper before handing it). (4) TRAIN/TEST SEPARATION -- the confidence-gate operating point is tuned on TRACIE TRAIN and reported on TEST; the UNGATED headline needs zero tuning. (5) LOCATED NEGATIVE -- transitive closure adds +0.077 coverage but tail-accuracy ~chance (net full-acc -0.004), and the causal-cue blend from ROCStories is a hair (+0.001) -- both honestly bounded, matching the literature."
files_changed: "experiments/exp_causal_order_enumerate_v1.py (the required WHERE-signal-is-lost enumeration); experiments/_causal_order_store.py (the tense-agnostic mine + gate + causal-cue store + crude/WN lemmatizers); experiments/exp_broaden_causal_order_store_v1.py (mine + eval + arms + paired clustered bootstrap + twin); experiments/exp_broaden_causal_order_sweep_v1.py (train-tuned operating-point sweep); experiments/exp_broaden_causal_order_final_v1.py (consolidated one-screen measurement); experiments/exp_broaden_causal_order_wnlemma_v1.py (the WordNet verb-concept re-mine + measurement); experiments/exp_causal_order_story_grounded_v1.py + exp_causal_order_grounded_v2.py (the story-grounding DRILL -- located negatives); experiments/exp_causal_order_coupling_v1.py (the MISSING-ORGAN prototype: script prior + situation-model confident overrides incl. instance-grounded event-coreference, +0.007 ns, operator_coref 0.833 -- validates the mechanism, pinpoints the coverage-of-comprehension residual); experiments/_causal_knowledge_store.py (the CSKG ConceptNet/ATOMIC causal-KB store -- a LITERATURE-CONFIRMED located negative: worse than narrative frequency, degrades with confidence); verification/test_broaden_causal_order_store.py (witness 8/8); data/exp_broaden_causal_order_store_v1/chains_broad_wn.json (RECOMMENDED drop-in asset -- WN-lemma keyed, 335,853 pairs) + chains_broad.json (crude-stem, 454,129 pairs); notes/problems/grow_a_broad_causal_event_order_knowledge_store_for_the_implicit_event_path/SOLVED.md. Mine caches + metrics under data/exp_broaden_causal_order_store_v1/ (gitignored, re-mineable via --remine). NO hdlab/ written (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_broaden_causal_order_store.py   # 8/8 (extraction 2x, coverage+acc lift, twin loses, narrated byte-identical, positive control); full one-screen numbers: .venv/Scripts/python.exe experiments/exp_broaden_causal_order_final_v1.py"
---

# The seed store was starved by a TENSE-GATED upstream extractor, not a small corpus -- fixing the upstream front-end doubles coverage and lifts implicit-event ordering CI-separated

## The disk outranks the brief on one load-bearing point (stated first)
The brief says the seed store (`hdlab.temporal_script_schema`) is **LATENT -- "no reader consumes it at read() time"**.
On the disk that is **STALE**: the p6 wire landed 2026-09-06/07 (`hdlab/temporal_reasoner.py` lines 61-84, 194-229;
`situation_reader` `track_temporal_reasoning=True` default-on). The live reasoner ALREADY consults the seed store as
a confidence-gated override on its implicit-event / abstention branch (`SCRIPT_E_MIN=10, SCRIPT_M_MIN=0.1`). So the
WIRE the brief asks for **already exists**; what was actually wrong is that the store is **thin (29% TRACIE coverage)**
-- and this work shows WHY (an upstream front-end fidelity gap) and fixes it.

## The enumeration reframed the problem (the required first deliverable; brief sec.6 / sec.2 test-4)
`exp_causal_order_enumerate_v1` splits every TRACIE implicit pair (n=1924) by WHERE the seed store loses signal:

| category | share | lever |
|---|---|---|
| A covered-correct | 17.5% | -- |
| B covered-**wrong** | 11.5% | TYPING (causal/irreversibility direction) |
| C uncovered -- **NO content verb extracted** | **66.1%** | **EXTRACTION (upstream front-end)** |
| D uncovered -- pair absent from the mine | **4.9%** | corpus coverage (the brief's proposed lever) |

**The brief hypothesised the wall was corpus size (more narrative corpora). The disk says corpus size is the SMALLEST
lever (4.9%).** The DOMINANT wall (66.1%) is EXTRACTION: 90% of those clauses DO carry a VB tag that the seed's mining
front-end (`extract_events_punct`, tense-gated to VBD / had+VBN / be+VBN) DROPS -- because TRACIE hypotheses are
written in mixed / present / bare tense ("She go to college", "John likes candy", "I climb up the ladder", "The man
was holding a piece of paper"). This is exactly the full-stack-upstream story: **the downstream store underperforms
because an upstream component is not brain-foundational.**

## The upstream fix (brain-foundational, ALREADY LANDED, the store just never consumed it)
An event is an event regardless of grammatical tense -- **the Event-Indexing Model (Zwaan, Langston & Graesser 1995)
treats time as a continuously-updated CUE dimension, not a GATE on whether an event representation is built** (a
literature drill confirmed this is the single strongest brain-foundational citation; tense-gating is a newswire-tuned
implementation artifact). The substrate already has the fix as a landed, owner-DONE organ: the **tense-agnostic
UPOS==VERB detector** (`tense_agnostic_events` / `register_robust_event_detection`, `hdlab/pos_tagger` + the live
reader's UPOS event detection). Re-mining ROCStories -- and re-querying TRACIE -- through it (every UPOS==VERB content
token, present / bare / progressive alike) lifts the TRACIE extraction ceiling **0.339 -> 0.699 (2.06x, measured)**,
fast (~1.3s query side). The seed's OFFLINE mine simply used the old tense-gated extractor; the LIVE reader already
detects events tense-agnostically, so this is an offline-mine fidelity fix, not a live-extractor change.

## What was built + measured (TRACIE iid test, n=1924; paired clustered bootstrap over stories)
A broader glass-box store: re-mine 98,161 ROCStories through the tense-agnostic front-end -> **454,129** ordered
verb-pairs (seed had 177,800), with a consolidation-gate admission layer (recurrence K / multi-seed M / PPMI /
DIRECTIONAL schema-margin = the causal confidence) and a causal-cue directional blend (Trabasso causal network:
connective-marked cause->effect edges, reusing `_causal_network`'s connective-direction sets).

| arm | full acc | coverage | vs seed 0.5296 | vs abstain 0.5000 | vs twin |
|---|---|---|---|---|---|
| **ungated (headline)** | **0.5655** | **0.607** | **+0.0359 [+0.0117,+0.0616] SEP** | +0.0655 SEP | +0.0759 SEP |
| as-wired (reasoner's existing gate) | 0.5582 | 0.326 | +0.0286 [+0.0080,+0.0496] SEP | +0.0582 SEP | +0.0686 SEP |
| override (train-tuned confidence gate) | 0.5629 | 0.425 | +0.0333 SEP | +0.0629 SEP | +0.0733 SEP |
| +transitive closure (LOCATED NEG) | 0.5567 | 0.594 | +0.0270 SEP | -- | -- |
| twin (shuffled order) | 0.4896 | 0.442 | -- | -- | -- |

- **COVERAGE lever named + measured:** 0.29 -> 0.607 (2.1x), dominated by the extraction fix (the 4.9% corpus lever
  is small, as the enumeration predicted). Per-covered-pair accuracy is 0.606 ungated (matches the seed's 0.6022) and
  rises to 0.65-0.68 under the confidence gate -- so **both coverage AND accuracy hold-or-lift** (the tradeoff the bar
  asks for). The confidence gate is the STRENGTH-GATED OVERRIDE's SAT operating point (higher margin -> higher
  per-pair accuracy, lower coverage); the reasoner's existing `SCRIPT_M_MIN` IS this dial.
- **The info-free twin LOSES** (0.4896, below chance): shuffling each pair's directional orientation while keeping the
  node set + counts collapses the store -- the EXTRACTED ORDER is load-bearing, not corpus frequency.
- **Positive control (41 pairs) the seed cannot get:** the broader store places implicit pairs correctly where the
  seed ABSTAINS (e.g. hold-before-hand -- you hold the paper before handing it; graduate-after-go).

## No-regress, full-stack (the FULL-STACK-UPSTREAM directive)
- **The upstream "optimization" is the tense-agnostic extractor -- which is ALREADY LIVE in the reader** (`tense_agnostic_events`
  default-on). This work does NOT change the live extractor; it changes only which extractor the OFFLINE store-mine
  uses. So there is no live-consumer regression surface from the extractor.
- **Blast radius of the store change = the reasoner's implicit-event branch only.** grep confirms the ONLY consumers
  of the script organ are `hdlab/temporal_reasoner.py` (implicit branch) and `hdlab/temporal_script_schema.py`;
  `situation_reader` reaches it only via the reasoner. The reasoner consults the store ONLY when a query key is off
  the narrated timeline -> the NARRATED before/after / overlap / duration path is **byte-identical** (verified across
  3 texts; the landed `test_temporal_reasoner_organ.py` passes 18/18 unchanged).

## THE WALL, RESEARCHED (per the standing directive; a literature drill, majority full-text)
- **Tense-agnostic event detection is brain-foundational -- YES.** Zwaan, Langston & Graesser (1995): time is a
  situation-model CUE dimension, not a gate on event representation. Nuance kept: grammatical ASPECT (perfective /
  imperfective) modulates event boundary STRENGTH (Magliano & Schleich 2000; Madden & Zwaan 2003), so aspect belongs
  as a graded confidence feature, not an inclusion filter -- which is exactly how the store treats it.
- **The causal-network + irreversibility TYPING is PARTIALLY grounded (do not over-claim) -- and the measurement
  agrees.** Trabasso & van den Broek (1985) is a causal-network REPRESENTATION of STATED events; McKoon & Ratcliff
  (1992) is standing counter-evidence that multi-step global causal links are NOT reliably constructed online -- which
  is precisely why (a) the causal-cue blend from ROCStories is a hair (+0.001; ROCStories is connective-sparse) and
  (b) transitive closure is a LOCATED NEGATIVE (coverage up, tail-accuracy ~chance). The aggregate store's ~0.65-0.68
  per-pair ceiling is the field-confirmed limit: Chambers & Jurafsky (2008) themselves call their chains TYPICAL order,
  not causal (Yamin et al. 2025 show order-substitution is the dominant failure) -- so the residual is instance-specific
  order that CONTRADICTS the script prior, which no aggregate store can fix without reading the (implicit) event's
  context. SymTime reaches 0.80 only with ~3.5M distantly-supervised examples; a glass-box no-LLM store gets ~0.57-0.68.

## UPGRADES + DEEPER UNDERSTANDING (owner drill: "why 0.61 not 0.94? is everything 100% brain-foundational? how does the brain do it?")
The store fires at ~0.61 per-pair accuracy; a competent reader hits ~0.94 (TRACIE in-context human agreement). We
now understand the gap PRECISELY, and it is NOT a fidelity bug in this store -- it is a categorically deeper mechanism.

**(1) The ceiling is STORY-CONDITIONING, and it was measured, not asserted.** TRACIE places an IMPLICIT event X (in
the story only 18%) relative to a NARRATED, story-anchored event Y (in the story 70%). The brain READS THE STORY and
places X via the specific story's causal network + instantiated script (Trabasso; Zwaan situation model). Our store is
CONTEXT-FREE: it uses only the aggregate type-order(X,Y), ignoring the story -- so it is right exactly when the story
FOLLOWS its canonical script and wrong when the story DEVIATES (someone falls THEN stands, vs the canonical
stand-then-fall). The ~40% covered-but-wrong ARE those deviations.

**(2) WHY THE CONTEXT-FREE STORE DID SO WELL (owner's question) -- the key insight.** The aggregate store IS the
SCRIPT PRIOR (Schank-Abelson canonical order), and scripts are, by design, CONTEXT-FREE REUSABLE knowledge ("pay
before leave" holds across ALL restaurant stories). So for the ~60% majority where a story follows its script, the
context-free lookup already EQUALS the story-grounded answer. That is why the aggregate is a strong prior -- and it is
the brain's own DEFAULT (Zwaan iconicity/script default, overridden only on a confident causal signal).

**(3) THE NEGATIVES DRILLED HARD (owner: "the brain can do it; if a brain-foundational mechanism fails, something
UPSTREAM is not").** I hunted the upstream gap across ELEVEN variants. First the anatomy (measured, not asserted):
of the covered-WRONG cases, **75% are LOW-margin coin-flips** (the aggregate has no real signal -- narrative order
genuinely does not determine the answer; the confidence gate correctly abstains, trading coverage) and only **25% are
HIGH-margin confidently-wrong**. I tested every upstream component I could name as the culprit:
  - STATE/NEGATION representation (states + negated events the verb-order store cannot hold): **REFUTED as the driver
    by measurement** -- state/neg is 25% of confident-wrong but 30% of confident-CORRECT (NOT enriched); abstaining on
    it HURTS (-0.0156). The examples LOOK like states; the denominator says otherwise.
  - ORDER SIGNAL = narrative-adjacency frequency vs a POSITIONAL script-timeline (each event-type's canonical slot):
    position ordering 0.5468 < 0.5619; hybrid store|position +0.0005 ns -- position is a WEAKER signal (common verbs
    sit mid-timeline).
  - CAUSAL-CUE blend: near-empty from ROCStories (connective-sparse) and can FLIP a correct prediction (caught it
    turning graduate/go 0.48->0.508 wrong) -- dropped.
  - VERB SELECTION: margin (most-confident) +0.0031 ns; exclude-light-verbs -0.0099 (light verbs carry signal);
    main-verb-only 0.5629 ns.
  - STORY-GROUNDING two ways: averaging (0.5468, REPLACED the prior with noise) + confident selective transitive
    (0.5535 ns, the transitive step compounds the store's own ~0.6 reliability).
  - Transitive closure: coverage +0.077 but tail ~chance; WN-lemma: tie (fidelity/efficiency win).
**THE DRILLED CONCLUSION (converged by the HIGH bar).** NONE of the upstream COMPONENTS is the fixable culprit --
each (tense-agnostic extraction, verb-concept lemma, script prior, confidence gate, margin selection) is
brain-foundational and near its own ceiling. The gap is not a BROKEN component; it is a MISSING ORGAN: the
implicit-event placement is fed ONLY the context-free script PRIOR, never the COMPREHENDED story. The brain COMBINES
the script prior with the situation model it built by reading THIS story's actual causal chain -- and that combination
is the entire residual. We even HAVE a situation-model reader (`situation_reader` builds the narrated timeline + causal
edges) -- it is simply not COUPLED to implicit-event placement. That coupling (script-prior x situation-model
instantiation) is a distinct, larger organ the brief correctly FENCES, and it is the precise, on-disk-evidenced
next-problem. Field-consistent: McKoon & Ratcliff (1992) (multi-step causal links are NOT built online from shallow
cues -- so no shallow method can); TRACIE glass-box SOTA ~0.60, SymTime needs ~3.5M distantly-supervised examples for
0.80 -- because the signal is COMPREHENSION, not aggregate statistics. The brain reaches ~0.94 with a lifetime of
embodied experience + full story comprehension, which is the whole project's north star, not a store-level fix.

**(4) A brain-foundational FIDELITY + EFFICIENCY upgrade that IS worth adopting: key the store on the verb CONCEPT
(WordNet lemma = the ATL lexical-conceptual hub), not a surface stem.** The crude suffix-stripper diverges from the
proper lemma on 34% of TRACIE verbs (went!=go, bought!=buy, decided->decid, stopped->stopp!=stop), FRAGMENTING each
verb concept across surface forms. Fixing it (`exp_broaden_causal_order_wnlemma_v1`, full 98k re-mine): the WN-lemma
store MERGES 26% of the pairs (454,129 -> 335,853), lifts coverage 0.607 -> 0.616, still beats the seed CI-sep
(+0.0353 [+0.0096,+0.0617]), and TIES the crude-stem store on accuracy (-0.0005, ns) -- the fragmentation cost is
absorbed by data volume at 98k stories, but the WN-lemma store is MORE brain-foundational (the verb concept, not a
stem), MORE efficient (26% smaller, 6.5MB vs 8.6MB), and higher-coverage. **Recommended asset:** `chains_broad_wn.json`
(do the right thing even when the number ties). It would matter more in a lower-data / rarer-verb regime.

**(5) THE MISSING ORGAN, PROTOTYPED (owner: "prototype that missing organ brain-foundationally").** Built
`exp_causal_order_coupling_v1` -- the situation-model x script-prior coupling with the CORRECT brain-foundational
architecture: the script prior is the DEFAULT, and the comprehended story is a CONFIDENT OVERRIDE (combine, never
replace -- naive replacement was measured to hurt). Four overrides, each a real brain mechanism: RULE 1 both-narrated
-> the story's own timeline order (Zwaan situation model); RULE 2 PHASAL composition ("stop V" after V's onset);
RULE 2c INSTANCE-GROUNDED OPERATOR -- an INTENT/AFTER operator SCOPES a referenced event E ("want to swim" precedes the
swimming; "stop talking" follows the talking), placed via EVENT COREFERENCE to the narrated/other event (Trabasso goal
chains + ATOMIC xNeed->before); RULE 2b topological INSERTION (place the implicit event in the narrated chain by store
votes). RESULT: organ 0.5691 vs prior 0.5619, **+0.0073 CI[-0.0247,+0.0411] -- positive point estimate, NOT
CI-separated.** The PROVENANCE is the deepest finding of the whole drill AND it VALIDATES the brain mechanism: the
instance-grounded rules are FAR more accurate than the aggregate WHERE THEY FIRE -- **operator_coref (event coreference)
fires 12 @ 0.8333**, **story_order (both-narrated) fires 245 @ 0.6245** (separately, operator-over-narrated fires ~4% @
0.722, pure coref ~1% @ 0.778) -- CONSISTENTLY 0.72-0.83 vs the prior's ~0.60. But the implicit-X insertion fires 781 @
**0.6018 ~ the prior's 0.60** (placing an implicit event via the narrated TIMELINE just recomputes the aggregate unless
its causal/semantic relation is actually resolved). **So the brain-faithful mechanism (instance-grounded event
coreference + operator/causal semantics) is VALIDATED at 0.72-0.83 -- what is missing is NOT the mechanism but the
COVERAGE of event coreference: the brain resolves the coreference/causal relation for EVERY implicit event via full
comprehension; our shallow detector reaches only ~1-13%. **So the missing organ is now specified precisely: not "couple with the narrated timeline"
(done, +0.006 ns) but "couple with the COMPREHENDED CAUSAL STRUCTURE + resolve the implicit event's meaning" -- event
coreference (does "stop talking" refer to the narrated "talked"?) + world-knowledge causal inference. That is the deep
comprehension organ (why glass-box SOTA is ~0.60 and SymTime needs ~3.5M supervised examples), and it is the project's
north star, not a store- or timeline-level fix. The prototype's VALUE: it proves the architecture (prior + confident
override) is right, shows the both-narrated override is a real +0.01 lever, and rules out the "narrated timeline is
enough" hypothesis with a measured provenance.**

**(6) THE CAUSAL-KNOWLEDGE KB OVERRIDE -- a LITERATURE-CONFIRMED LOCATED NEGATIVE (owner: "the order signal is the
weak link; research why").** Hypothesis: narrative co-occurrence FREQUENCY is a weak proxy; a curated CAUSAL /
PRECONDITION KB (the brief's own §3 source: ConceptNet Causes + ATOMIC, here via CSKG) is the brain-foundational fix
(Trabasso causal network -- temporal priority is a DEFINING criterion of a causal link). BUILT it
(`_causal_knowledge_store.py`: 62,763 CSKG causal/precondition edges -> 65,018 verb-concept-keyed directed pairs;
mapping Causes->before, HasPrerequisite->reversed, First/Last-subevent->script order). **MEASURED (TRACIE): the causal
KB is WORSE than narrative frequency and DEGRADES with confidence** -- per-pair ev>=1 0.546, ev>=5 0.490, ev>=10 0.474
(below chance); as an override it drops full accuracy 0.5619->0.5364; on disagreements narrative wins 170-120. TWO
research drills (majority full-text) CONFIRM this is correct, not a bug: (a) DECONTEXTUALIZATION -- ConceptNet/ATOMIC
edges are GENERAL type-level commonsense facts, not instance-specific to THIS story's causal chain, so they transfer
NEGATIVELY (CSKG is further from TRACIE's genre than ROCStories, which IS the genre); (b) DIRECT PRECEDENT -- Wang,
Chen, Zhang & Roth (2020) independently found ConceptNet causal/subevent edges USELESS for before/after ordering and
fell back to TEMPROB, a FREQUENCY-mined verb-pair table (the SAME species as Chambers-Jurafsky); Weber, Rudinger & Van
Durme (2020) confirm frequency!=causal-validity but as a confounding critique; NO SOTA ordering system (TRACIE, MATRES)
uses a causal KB. Mapping CORRECTION from the drill: HasFirstSubevent/HasLastSubevent/HasSubevent are CONTAINMENT, not
precedence -- only ATOMIC xNeed(before)/xEffect/isBefore/isAfter are verbatim-documented precedence. **CONCLUSION: the
narrative-script frequency store IS the brain-foundational order signal (the Schank-Abelson script order acquired from
narrative experience); the "order signal is the weak link" hypothesis is REFUTED. The load-bearing residual is
INSTANCE-GROUNDED coupling (event coreference + situation-model instantiation of the script in THIS story's causal
chain), NOT a better KB -- the literature (McKoon & Ratcliff 1992) and our own coupling result (+0.006 ns) agree.**

**Is everything 100% brain-foundational?** The COMPUTATIONS are: tense-agnostic event detection (Zwaan 1995, PINNED);
verb-concept keying (ATL hub, PINNED); narrative event chains as the script prior (Chambers-Jurafsky / Schank-Abelson,
PINNED); the confidence-gated override (Zwaan default+override, PINNED). The remaining PROXY is the shared statistical
POS tagger (a reader-wide gap, not specific to this store). The one thing that is NOT here -- and is the whole residual
-- is the DEEP situation-model reader (the story-specific override), which is out of scope by design and is the named
next-problem.

## KEY REALIZATIONS (the enabling moves)
1. **The enumeration, not the brief, set the direction.** Splitting the loss into extraction / typing / corpus-coverage
   showed the brief's proposed lever (corpora, 4.9%) was the smallest and the real wall (extraction, 66%) was upstream.
   An absence claim requires an enumeration, not a search.
2. **The upstream fix was already built -- the store just never ate it.** The tense-agnostic detector is a landed
   owner-DONE organ; the seed store's offline mine used the old tense-gated extractor. Consuming the brain-foundational
   upstream doubled coverage with no new modelling. ("A brain-foundational downstream that underperforms almost always
   has a non-brain-foundational upstream" -- confirmed literally.)
3. **The consolidation gate's recurrence/PPMI filters are for topical SENSE noise, not ORDER.** They cost coverage
   without adding accuracy here; the correct admission control for a DIRECTIONAL signal is the TWIN (shuffle the order)
   -- which loses hard, proving the raw directional signal is admissible. The gate's DIRECTIONAL-MARGIN component IS
   the override's confidence knob (swept), and that is the part that helps.
4. **Research kept the win honest.** The literature drill confirmed the dominant lever (tense-agnostic) is solidly
   brain-foundational AND that the causal/irreversibility typing is only partially grounded -- matching the measurement
   (typing is a modest, honestly-bounded refinement, not the main win).

## AUDIT UPDATE (notes/BRAIN_FOUNDATIONAL_AUDIT.md sec.2b -- TIME)
The implicit-event script/schema store is (a) NOT latent -- the p6 override wire is live (correct the "no reader
consumes it" note); (b) its real limit was an UPSTREAM tense-gated mine (`extract_events_punct` drops present/bare/
progressive), NOT corpus size -- now fixed via the tense-agnostic UPOS front-end (Zwaan 1995 event-indexing; PINNED),
lifting TRACIE coverage 0.29 -> 0.61 and full accuracy 0.5296 -> 0.5655 CI-sep, twin losing, narrated byte-identical.
Deviation recorded: ~30% of TRACIE hypotheses are copular STATES ("X is happy", "X was a spy") with no event verb --
a distinct STATE-ONSET ordering organ, the named next-problem. The causal/irreversibility TYPING is PARTIALLY grounded
(Trabasso representation; McKoon & Ratcliff online-construction caveat) -- a modest lever, not the main win.

## Proposed hdlab landing (strategy lands; Q111 -- I do not write hdlab/)
1. **Rebuild the `temporal_script_schema` asset via the tense-agnostic mine + verb-concept keying.** Drop-in ready:
   copy `data/exp_broaden_causal_order_store_v1/chains_broad_wn.json` (RECOMMENDED -- WordNet-lemma keyed, 335,853
   pairs, 26% smaller + higher coverage + more brain-foundational) OR `chains_broad.json` (crude-stem, 454,129 pairs,
   same accuracy) over `data/exp_temporal_reason_tracie_script_v1/chains.json`, OR change
   `hdlab/temporal_script_schema.build_chains` to extract via `hdlab.pos_tagger` UPOS==VERB (tense-agnostic) and key on
   the WordNet verb lemma (`wn.morphy(w,'v')`) instead of `extract_events_punct` + the crude stem. The query path must
   use the SAME lemmatizer (the live reader already UPOS-tags; add the lemma normalisation). ADDITIVE: reasoner code
   unchanged; narrated path byte-identical; as-wired lift +0.0286 CI-sep with the existing gate.
2. **Optionally retune the override confidence:** the UNGATED / lower-`SCRIPT_M_MIN` operating point gives higher
   coverage (0.61) and the best full accuracy (0.5655, +0.0359 CI-sep). The margin is the SAT dial; a lighter gate is
   net-positive here.
3. **Do NOT** land transitive closure (located negative) or lean on the causal-cue blend as the main signal (weak from
   ROCStories); do NOT touch the narrated channels.

## What I did NOT establish (withdraw-first if wrong)
- **I would withdraw first any implied claim that the CAUSAL / IRREVERSIBILITY typing is the win.** It is not -- the win
  is the tense-agnostic EXTRACTION fix (coverage). The causal-cue blend is +0.001 (ROCStories is connective-sparse);
  strengthening it needs causal-dense corpora (wiqa / tellmewhy / process / ATOMIC) -- a named follow-on.
- **The per-pair accuracy ceiling (~0.65-0.68) is real and field-confirmed** (aggregate order contradicts
  instance-specific implicit order); this is a coverage win at the seed's per-pair accuracy, not a new accuracy regime.
- **The ~30% copular-STATE hypotheses are out of scope** for a verb-pair-order store -- a distinct state-onset organ.
- The headline is on TRACIE (ROCStories-derived, the canonical implicit-event gold); a second narrative-order gold
  would strengthen generalisation (named next step), though train/test separation guards against operating-point
  overfitting.

## Adjacent components (evaluated for brain-fidelity + next problems, per owner 2026-08-28)
- **State-onset ordering organ (highest-value next):** ~30% of TRACIE hypotheses are copular STATES the verb store
  cannot represent. The brain orders state onsets/offsets too (Reichenbach; Allen interval endpoints). A distinct
  before/after-over-states store. OUR-INVENTION territory; brain-foundational (event-indexing includes states).
- **Causal-dense corpora for the typing lever:** wiqa / tellmewhy / process_articles / ATOMIC would strengthen the
  connective-marked causal direction (Trabasso), which ROCStories under-supplies. Modest expected lift (typing is 11.5%).
- **The tense-agnostic front-end itself** is the shared upstream for MANY consumers (who-did-what, temporal, causal);
  it is brain-foundational and LIVE. The residual front-end proxy is the statistical POS tagger (a reader-wide gap).

## TLDR (plain English)
Stories skip obvious steps -- "she paid and left" leaves out ordering, eating, getting the bill -- and a reader fills
them in, in the right order, from world knowledge. We had a small store of "which kind of event usually comes before
which", but it only knew one implied pair in three. The brief guessed the fix was "read more stories". The data said
otherwise: the store was starved because the part that spots events in a sentence only recognised PAST-tense verbs and
threw away present-tense ones ("she GOES to college", "he LIKES candy") -- and the test is full of those. There was
already a better, brain-faithful event-spotter in the system (one that knows an event is an event whatever the tense);
the store had just never used it. Switching to it DOUBLED how many implied-order questions the store can answer (one in
three -> three in five) and made it measurably more right than both "I don't know" and the old store -- about 6 more
right in 100 -- with a scrambled-order version falling apart (so the real cause-and-order structure carries the load),
and the questions it could already answer left untouched. No outside AI does the reading. The honest limits: the
cause-and-effect "typing" I added barely moved the needle (these simple stories rarely say "because"), and about a
third of the test asks about STATES ("was happy", "was a spy") that have no action verb at all -- a separate store to
build next.

## QUESTIONS
None blocking. One judgement call: graded SOLVED. The store is broadened + measured CI-separated over both floors on
modern gold with the twin losing and the narrated path byte-identical (the bar's requirements) -- but the WIN is the
upstream extraction fix, not the brief's proposed corpus/typing levers, and the causal typing is an honestly-bounded
modest lever. If you would prefer this filed as "the brief's lever REFUTED, the goal met a different way", that is a
one-line status change; SOLVED reflects that the underlying goal (broaden + lift the implicit-event path) is met.

## NEXT STEPS (ranked; strategy owns hdlab landing, Q111)
1. **HIGH -- Strategy: LAND the tense-agnostic + verb-concept mine** (drop-in `chains_broad_wn.json`, RECOMMENDED --
   26% smaller, verb-concept keyed, higher coverage; or switch `build_chains` to UPOS + `wn.morphy`). As-wired +0.0286
   CI-sep with the existing gate; retune `SCRIPT_M_MIN` down for the full +0.0359. Narrated byte-identical. Optionally
   adopt margin-based pair selection (+0.0031 ns, cleaner). This is the WHOLE store-level win, drilled to convergence.
2. **HIGH -- file the IMPLICIT-EVENT x SITUATION-MODEL COUPLING** (the drilled residual, on-disk evidenced). NOT a
   state-onset organ (measured: state/neg is not the confident-wrong driver) and NOT a store fix (11 variants fail).
   The organ: read THIS story with `situation_reader` (narrated timeline + causal edges already built) and INSTANTIATE
   the retrieved script in it -- align the script's events to the narrated chain, place the implicit event by the
   story's actual causal structure, override the aggregate prior only when the comprehended story is confident (the
   Bayesian prior x evidence combination the brain uses; naive averaging/replacement was measured to HURT). This is the
   ~0.60 -> toward-0.94 lever and couples to the SDRT `coherence_reader` + `causal_reasoner` already landed.
3. **MEDIUM -- causal-dense corpora** (wiqa / tellmewhy / process / ATOMIC) to strengthen the causal-cue directional
   signal for the abstract/social pairs where narrative adjacency is a coin-flip (ROCStories is connective-sparse).
4. **LOW / DO-NOT (all measured located negatives):** transitive closure (coverage up, accuracy ~chance); position-only
   ordering (weaker than pairwise); state/neg abstain (hurts -- not the driver); light-verb exclusion (hurts); the
   causal-cue blend at high weight (flips correct predictions); a 19c mining source (banned; archaic verbs); an
   external LLM at inference (the invariant).
