# Research drill: discourse reference-time & temporal-order reconstruction (the frontier past per-verb tense)

**Date:** 2026-08-31 | **Drill type:** RESEARCH-ONLY (no code) | **Problem:** `the_tense_agnostic_detector_drops_tense_needed_by_the_time_dimension` (follow-on; the tense-preserving detector is SOLVED)
**Prior-work check:** `experiment_index.py` -- `temporal` 61 cells, `aspect` 11, `tense` 3, `Reichenbach` 0; the built organs are `_read_timeline` (per-sentence, `"had"`-gated flashback detector) + `_read_timeline_register` (whole-passage discrete toposort, default-OFF). No prior lit-scan on discourse reference-time on record.

---

## Q1 -- THE DISCOURSE REFERENCE-TIME COMPUTATION (mostly PINNED; specifics contested)

Per-verb tense/aspect features are necessary but not sufficient; the timeline is built by an **anaphoric, incrementally-updated Reference time** ("where in time is the narrative now?").

- **R-movement / temporal focus -- PINNED as the standard frame.** Partee (1984) established that tense is *anaphoric* like a pronoun: comprehension maintains a "temporal focus" that is updated as the narrative proceeds (Hinrichs 1986; Kamp & Reyle DRT 1993). The default rule: each **eventive** clause locates its event just after the current Reference point and then *advances* R to it; **stative/imperfective** clauses *overlap* R and do **not** advance it. This tense-as-anaphora + eventive-advances/stative-overlaps split is the near-universal formal model.
- **Perfect/pluperfect = anteriority/flashback -- PINNED, licensing CONTESTED.** The pluperfect locates E *before* the current R and does **not** advance the narrative-now (Kamp & Reyle); it is the flashback signal. But "mere temporal precedence does not license a pluperfect" -- its use is constrained by discourse-semantic rules requiring an already-open past perspective point (contested details across DRT variants; de Swart, and the Spanish/French/Italian pluperfect-discourse literature).
- **Connectives/adverbials override text-order -- PINNED (semantics of `when` contested).** *before/after/until* set explicit order; a frame adverbial (*an hour later*, *yesterday*) *resets* R to a new time; *when/while* are famously ambiguous and resolved by aspectual coercion (Moens & Steedman 1988).
- **Aspectual coercion, telic/atelic -- default PINNED, semantics-vs-pragmatics CONTESTED.** Dowty (1986): when no adverbial is present, **aspectual class alone** drives advancement -- accomplishments/achievements (telic) advance R; states/activities (atelic) overlap. Moens & Steedman's *nucleus* (preparatory-process / culmination / consequent-state) + type-coercion formalises how an activity is coerced to an event, etc. Whether advancement is truth-conditional semantics or defeasible pragmatics is Dowty's own open question.

## Q2 -- PROCESSING / NEURAL EVIDENCE (online timeline construction)

- **Order-of-mention is the default; time-shifts cost reading time -- PINNED.** Zwaan (1996) Strong Iconicity: reading time rises at a narrative time-shift (*an hour later* > *a moment later*), and events across a shift are less connected in memory. Time is one of five monitored indices in the event-indexing model (Zwaan & Radvansky 1998); each discontinuity is an updating cost. Readers track **narrated** time, dissociable from real/reading time.
- **The brain does NOT read an explicit global clock -- it RECONSTRUCTS order from relational bindings + a drifting temporal context.** DuBrow & Davachi: temporal-order judgments are supported by *associative relations across the intervening sequence*, and event boundaries disrupt across-boundary order (within-event order preserved, across-boundary order reconstructed). Hippocampal/MTL relational binding + a gradually-changing temporal-context signal (Howard & Kahana TCM; Eichenbaum time cells) are what order is read out from; recency judgments *reactivate* the intervening chain. **This is a direct steer: the computational target is an event-ordering GRAPH (relational before/after links) read out by reconstruction -- not a global coordinate array.**

## Q3 -- EVALUATING OUR ORGAN + MINIMAL FAITHFUL UPGRADE

`_read_timeline` fires **only** on sentences containing `"had"` and reconstructs order via a connective+is_pp toposort. `_read_timeline_register` (default-OFF) already carries R across sentences via a discrete constraint-graph toposort with a pluperfect binder -- its internal shape (edges -> toposort) is *exactly* the brain's relational-graph readout, so the readout is faithful. **The specific brain-UNfaithfulness is in the EDGE SET and the gate:** the `"had"` gate implements only the *marked exception* (pluperfect flashback) and drops the *unmarked productive rule* -- default narrative-now advancement on every eventive simple-past clause, which is the most common case. It inverts the brain's model (default = continuous R-advance; pluperfect = the exception). It also lacks (i) aspectual advancement (telic advances / stative overlaps -- Dowty), (ii) adverbial R-setting, (iii) reference-time anaphora proper.

**Minimal faithful upgrade path (computational target = DRT-style R-update producing an event-ordering graph, read out by toposort = the hippocampal relational-sequence shape):** (1) make the constraint graph primary and consume the tense-preserving detector's per-event Reichenbach E/R/S + finite tense/aspect; (2) add the DEFAULT advance rule -- each telic finite eventive clause advances R and adds an "after prior narrative-now" edge; states/atelic overlap (no advance); (3) keep pluperfect as the anteriority exception (edge-before, no advance -- already built); (4) add adverbial/connective R-setters as edge-overriders; (5) ungate from `"had"`, run whole-passage, default-ON once validated.

## Q4 -- NEXT-PROBLEM FRAMING (ranked)

1. **`the_timeline_dimension_reorders_only_around_pluperfect_and_drops_default_reference_time_advancement`** (PRIMARY -- consumes the detector). *Rationale:* rebuild the TIME dimension as a full event-ordering graph via DRT-style R-update (default advance on telic events, overlap on states, anteriority on perfect, adverbial resets), consuming the tense-preserving Reichenbach features. *Replicates:* Partee's temporal focus + Kamp & Reyle DRT update + Dowty aspectual advancement (computational level); hippocampal relational binding of event order (implementation). *Gold:* pairwise event ordering (before/after/equal/vague) with a can-fail control (text-order baseline + shuffled-tense twin must LOSE).
2. **`aspectual_advancement_needs_a_learned_telic_atelic_signal`** (SECONDARY / a COMPONENT of #1). Dowty's default advancement is aspect-gated but we have no telicity signal; per the prior drill, LEARN telic/atelic distributionally (Aspect Hypothesis), don't hardcode. *Gold:* telicity-annotated verbs; or induce from advancement patterns in the ordering corpora.

**DATA ACQUISITION NEED (flag):** none of the temporal-ordering golds are on disk (only UD-EWT + LitBank + reading corpora). Acquire, as a static FOUNDATION asset: **MATRES** (Ning 2018 -- start-point before/after/equal/vague over TempEval-3/TimeBank docs; free on GitHub) as the primary ordering gold; **CaTeRS** (Mostafazadeh 2016, causal+temporal over 5-sentence ROCStories) as a clean short-narrative sanity set; **TRACIE** (Zhou/NAACL 2021, implicit-event ordering) as a stretch inference test; TempEval-3 / TimeBank (LDC) as source docs.

---

## PINNED vs CONTESTED
- **PINNED:** tense-as-anaphora + updated temporal focus (Partee/Hinrichs); DRT default rule (eventive advances R, stative overlaps); pluperfect = anteriority/no-advance; connectives/adverbials override text-order; Dowty telic-advances/atelic-overlaps default; Zwaan iconicity reading-time cost at time-shifts; brain reconstructs order from relational bindings + temporal context, NOT a global clock.
- **CONTESTED:** exact pluperfect licensing; `when`-clause semantics; whether aspectual advancement is semantics or pragmatics (Dowty's open question).
- **BRAIN-UNFAITHFUL in our current organ:** the `"had"` gate models only the marked exception and drops the unmarked default R-advance rule -- an inversion of the brain's model.

## Sources
- [Partee (1984), Nominal and temporal anaphora, Ling. & Phil.](https://link.springer.com/article/10.1007/BF00627707)
- [Hinrichs (1986) / temporal structure of narrative, EACL](https://aclanthology.org/E87-1042.pdf)
- [Kamp, van Genabith & Reyle, Discourse Representation Theory (handbook)](https://www.ims.uni-stuttgart.de/archiv/kamp/files/2011.kamp.van.genabith.reyle.discourse.representation.theory.pdf)
- [Dowty (1986), Effects of aspectual class on the temporal structure of discourse](https://link.springer.com/article/10.1007/BF00627434)
- [Moens & Steedman (1988), Temporal Ontology and Temporal Reference, Comp. Ling.](https://aclanthology.org/J88-2003.pdf)
- [Zwaan (1996), Processing Narrative Time Shifts, JEP:LMC](https://www.semanticscholar.org/paper/Processing-Narrative-Time-Shifts-Zwaan/43b69adfd637eef0bf8a0226912103778bf55cab)
- [Zwaan & Radvansky (1998), Situation Models in Language Comprehension and Memory](https://sites.ualberta.ca/~dmiall/Cognitive/Readings/Zwaan_Radvansky_1998.pdf)
- [DuBrow & Davachi, Temporal binding within and across events (Neurobiol. Learn. Mem.)](https://pubmed.ncbi.nlm.nih.gov/27422018/)
- [DuBrow, Events and Boundaries (event horizon model)](https://memory.psych.upenn.edu/mediawiki/images/e/e1/DuBrow_Final.pdf)
- [Ning et al. (2018), MATRES (via Crowdaq/temporal relation datasets)](https://arxiv.org/pdf/2010.06694)
- [Zhou et al. (2021), TRACIE -- Temporal Reasoning on Implicit Events, NAACL](https://aclanthology.org/2021.naacl-main.107/)
- [Bos & Bastiaanse, Time reference decoupled from tense (PADILIH)](https://www.semanticscholar.org/paper/Time-reference-decoupled-from-tense-in-agrammatic-Bos-Bastiaanse/cf684773c03ac2441472b198f748c8b9b1a9db34)
