---
priority:
review: EXCELLENT
review_text: "Reverified 10/10 first-hand. A STRONG-to-EXCELLENT positive: a verb-role EXEMPLAR selector (nearest-exemplar k-NN over GROUNDED fillers of the verb OBJ slot) picks the patient at 0.432 on the modern ambiguous-position slice, CI-separated over EVERY floor run -- the verb-role MEAN centroid 0.365 (+0.067), the coarse holistic prior 0.331 (+0.102), position-only 0.290 (+0.143); the verb-shuffled twin LOSES (+0.097 -> the verb-KEYING does the work) and the centroid-vs-exemplar ablation confirms the lever is the INSTANCE distribution, not richer features (+0.067). Generalizes to UNSEEN fillers (+0.062), replicates in GloVe-300 (+0.126). DEPLOYMENT (full population): a construction-conditional integrated selector (position x exemplar, word-order down-weighted at non-canonical structure) beats the LIVE wired reader 0.481->0.508 (+0.027 CI-sep), twin loses. 19c is a TWO-LAYER located negative (register-drift: an in-domain store beats the modern one +0.081; parser-degradation: the modern frontend cannot extract clean pairs from archaic prose). Exemplary oracle-ladder dissection ruling out features/mechanism/combiner/parse WITH NUMBERS. WIRE QUEUED (Q111, WIRING_MAP): hdlab/verb_role_exemplar_selector.py (load selectional_slots_v1.pkl [14.7MB offline asset] + select_patient via k-NN grounded similarity) wired into the predict_revise drop-fill target selection + a construction-conditional role-assignment tie-breaker at non-canonical order; witness test_verbrole_exemplar_which_arg.py 10/10 is the acceptance gate. The #1 FOLLOW-ON is ISSUED (the_selectional_event_store...register_native_corpus, priority 2): DOMAIN MATCH is the definitively-located #1 who-did-what lever (+0.149)."
---

> **⚠️ CORRECTION 2026-09-01 (from the owner-DONE follow-on `the_selectional_event_store…register_native_corpus`): this problem's "DOMAIN MATCH is the #1 who-did-what lever (+0.149)" was TOPICAL NEAR-LEAKAGE.** On a genuinely DISJOINT corpus the MARGINAL verb→object store (THIS problem's mechanism) TIES the out-of-domain store (−0.007, not CI-sep); the +0.149 came from leave-one-sentence-out on the TEST corpus. The domain lever is REAL but lives in the JOINT (subj,verb,obj) FHRR event code (~+0.035), NOT the marginal exemplar store. **CONSEQUENCE:** the deferred p5 verb-role (marginal) wire gets NO domain lift and is WITHDRAWN as a domain-lift play; the true cross-task who-did-what lever is the PARSER (see the priority-1 problem `the_extraction_front_end_parser_is_the_cross_task_bottleneck…` + AUDIT §2b).

# PROBLEM: the reader's plausibility PRIOR is a COARSE holistic grounded centroid — it can GATE (flag that a bound argument is surprising) but it cannot say WHICH of several candidate nominals is the right argument for a SPECIFIC verb. p2 (`the_reader_parses_as_truth…predict_and_revise`, EXCELLENT, owner-DONE) proved this from both sides: the predict-and-revise DROP-FILL recovers the dropped patient, but the TARGET is picked mostly by POSITION, and the grounded prior only earns its keep on 19c prose where the parser degrades (+0.022); p2's 4-way negative + the drill confirm "the coarse 12-d grounded space cannot make the verb-specific prior a WHICH-argument lever." The brain does NOT use a holistic centroid: it uses VERB-SPECIFIC selectional preferences / thematic fit ("read" takes readable patients, "eat" edible ones), stored as verb-role→typical-filler EXEMPLARS and queried at role-assignment time (McRae et al. 1998; Elman 2009; the eADM). Build a STRUCTURED verb-role exemplar/event store (verb-keyed selectional preferences over GROUNDED argument fillers) and prove it gives a verb-SPECIFIC WHICH-argument lever — selecting the right drop-fill target (and disambiguating role assignment) CI-separated over BOTH the coarse-centroid prior AND a position-only baseline — AT THE REGIME WHERE POSITION IS AMBIGUOUS (multiple pre-verbal nominals / degraded / archaic parses), where p2 measured the coarse prior failing. A rigorous located NEGATIVE is a full PASS (this area has HARD_FAILs — see below — so locate precisely which verb-role structure the exemplar store can and cannot supply, at which regime).

**slug:** `the_plausibility_prior_is_a_coarse_centroid_needs_a_structured_verb_role_exemplar_store` — **opened:** 2026-09-01
by the strategy session (ARCHITECT HEARTBEAT; owner: "new solution dropped [p2, owner-DONE], pointing at a high-priority
next problem — get it on the dash so I can assign it"). It is p2's explicitly-named #3 follow-on: "a RICHER (structured
verb-role exemplar/event) prior — the only route to a verb-specific WHICH-argument lever … the same Phase-1 meaning-supply
build p2 named." **status:** OPEN — a BUILD problem (a structured verb-role exemplar/event store as the drop-fill /
role-assignment prior). You build + validate in `experiments/`; strategy lands any hdlab wire (Q111, default-off, witness
required). Glass-box, NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's; RE-RANK PER THE OWNER):** filed at `5`. p2 named it p2's
> highest-value follow-on and the "ONLY route" to a verb-specific WHICH-argument lever — BUT ranked below the reasoning
> aligner (`4`) and the who-did-what/Phase-1 levers because ⚠️ **its leverage is a BOUNDED slice (do not oversell):** on
> MODERN prose POSITION already carries who-did-what, so p2 measured the verb-role prior earning only +0.022 (19c only,
> where the parser degrades). Its value is concentrated where POSITION IS AMBIGUOUS / the parser is DEGRADED / prose is
> ARCHAIC. That is exactly why the bar (below) targets that regime, not the data-rich modern regime where counting wins.
> RAISE it if you weight the who-did-what extraction line above the reasoning/meaning work. (Priorities must be unique;
> `2` is held by p2 until it integrates.) ⚠️ Compose with the reader's capable flags ON (`python tools/reader_capabilities.py`).

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** — the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau — it is the FIRST thing you do.
>
> **🚀 YOU ARE ENABLED — AND EXPECTED — TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **⛔ "CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **🔁 THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) — RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one — and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps — AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) — that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill — do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across — never a ceiling.
> Each fire: implement → test (can-fail, strongest real floor, info-free twin LOSING) → iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS — but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When a sentence puts the thing-being-acted-on BEFORE the verb ("the book that the man read"), the reader often has to
pick which of several earlier words is the real object. Right now it mostly guesses by POSITION, and it has a rough
"is this plausible?" sense that can say "something's off" but can't say WHICH word is right — because that sense is one
blurry average of "meaning," not verb-specific knowledge. Brains know *per verb* what kind of thing usually fills each
slot: you *read* books and letters, you *eat* food, you *drive* cars — and they use that to pick the right word.
Build the reader that specific knowledge: a store of "for this verb, these are the kinds of things that fill this role,"
learned from many examples and grounded in what those things ARE — then use it to choose the right word to recover,
especially in the hard sentences where position alone is ambiguous.

## 2. WHY THIS ONE
p2 (predict-and-revise, EXCELLENT) built the step that goes back and recovers a dropped who-did-what, and drilled it to
the bottom: the recovery works, but the piece that PICKS which word to recover is position — and where position is
ambiguous, the reader's only other cue is a coarse "plausibility" centroid that p2 proved cannot do verb-specific
WHICH-argument selection. p2 named a structured verb-role exemplar store as "the only route" to that lever. It is the
successor to the who-did-what quality line and it is the reader's `predictive_reader` prior upgraded from a gate into a
selector. Bounded (position already wins on easy modern text) but real on the hard slice, and it composes with the
concurrent filler-gap / interference work.

## MEASURED vs INFERRED
- **MEASURED (inherit from p2; do NOT re-derive):** the predict-and-revise DROP-FILL recovers dropped patients CI-sep
  over the batch parse (QA-SRL +0.0599, LitBank +0.0592); the gain is a STRUCTURAL drop-fill (no surprisal gate needed);
  the fill TARGET is picked mostly by POSITION, and the verb-specific GROUNDED prior adds only +0.022 (19c only, where the
  parser degrades); a NO-PRIOR structural fill TIES on modern QA-SRL. p2's 4-way negative + this drill: the coarse 12-d
  grounded centroid `predictive_reader` is a valid violation GATE but a coarse target-SELECTOR — it cannot make the
  verb-specific prior a WHICH-argument lever. INTERVENING-NP interference collapses position recall 0.754→0.000 (the
  residual is retrieval interference where position is ambiguous).
- **INFERRED (you must measure):** whether a STRUCTURED verb-role exemplar/event store (verb-keyed selectional preferences
  over grounded fillers) supplies a verb-SPECIFIC WHICH-argument signal that selects the right drop-fill target
  CI-separated over the coarse-centroid prior AND position-only, AT THE AMBIGUOUS-POSITION regime — or whether the
  structure is not recoverable/selectable (a full-PASS located negative that names which verb-role structure fails and why).

## 3. HOW THE BRAIN DOES THIS (the opening move)
**PINNED — VERB-SPECIFIC SELECTIONAL PREFERENCE / THEMATIC FIT, exemplar/instance-based (not a centroid).** The brain
holds per-verb expectations about which entities fill each thematic role, learned from experienced verb-argument
co-occurrences, and uses them to anticipate + select arguments online (McRae, Spivey-Knowlton & Tanenhaus 1998 thematic
fit; Elman 2009 "words as cues to event knowledge"; Bicknell et al. 2010; the extended Argument Dependency Model /
Bornkessel-Schlesewsky eADM: role assignment integrates a verb-specific prominence/animacy/plausibility prior). The
representation is EXEMPLAR / instance-based (a distribution over experienced fillers), NOT a single averaged centroid —
so it can say "for *read*, a BOOK fits the patient far better than a MAN," a distinction a holistic centroid blurs. The
fillers are GROUNDED (what the thing IS — ATL hub-and-spoke), so the store generalizes to unseen but similar fillers.
The computation to COPY: a verb-role→filler-distribution store, queried with the candidate nominals for a role, returning
a verb-specific fit score that SELECTS the right candidate — used as the drop-fill TARGET selector (and, where position
is ambiguous, the role-assignment tie-breaker).

## 4. PINNED vs OUR-INVENTION (copy the computation, sweep the parameter)
- **PINNED (COPY exactly):** verb-specific (verb-keyed) selectional preferences; an EXEMPLAR/instance-based distribution
  over experienced fillers (not a centroid); GROUNDED fillers so it generalizes to unseen-but-similar arguments; used as
  a WHICH-argument SELECTOR at role assignment, integrated with (not replacing) the positional/parse evidence.
- **OUR-INVENTION-UNDER-TEST (SWEEP, do NOT adopt a number):** the exemplar-store form (k-NN over grounded fillers /
  a per-verb-role kernel density / a sparse prototype set — the 12-d holistic centroid is EXACTLY what fails, so richer is
  the point; sweep it), the grounded filler space, the number of exemplars / smoothing for rare verbs, how the store's
  score COMBINES with the positional/parse evidence (a noisy-channel product, per the eADM), the confidence gate. Sweep,
  report the frontier, never hard-code a borrowed constant.

## ALREADY TRIED / PRIOR WORK — CHECK `experiment_index` FIRST (this area is DENSE; a re-derivation is the failure mode)
> ⚠️ **RUN `python tools/experiment_index.py query "selectional preference"` AND `"exemplar"` AND `"thematic fit"` BEFORE
> BUILDING.** p6's process lesson was exactly this: it re-derived a known negative by skipping `experiment_index`. Known:
- ✅ **`exp_pivot_selectional_knowledge_richness_2afc_v1` = HARD_PASS "KNOWLEDGE_POVERTY_WAS_THE_WALL"** — richer
  selectional knowledge DOES help when knowledge-poverty is the bottleneck. BUILD ON this (it is the positive evidence for
  a richer structured store); do not re-run the 2AFC richness probe.
- ⚠️ **`exp_graded_thematic_fit_integrated_reader_gate_v1` = MIDDLE_BAND / HARD_FAIL_P_HELP_NULL_OR_NEGATIVE** — a graded
  thematic-fit READER GATE was middling. This problem is NOT "re-run a thematic-fit gate"; it is a verb-specific
  WHICH-ARGUMENT SELECTOR for the drop-fill target at AMBIGUOUS position (a different job than a presence/plausibility gate).
- ⚠️ **`exp_propara_entity_fate_selectional_preference_probe_v1/v2` = HARD_FAIL_NO_GENERALIZATION / NO_INDISTRIBUTION_SIGNAL**
  — a selpref probe that did NOT generalize. Understand WHY before repeating its shape; test at the regime where the
  verb-role signal is load-bearing (ambiguous position), not where it is not.
- **`exp_exemplar_selpref_v1` (prereg 2026-08-28) + `exp_selpref_unseen_lowdata_v1` (Binder-2016 extension, rho 0.69,
  24978 words, referenced by the p3 retrieval-practice drop) + `exp_frontend_thematic_fit_qasrl_v1`** — CHECK whether these
  ran and what they found; reuse the built pieces (a grounded/experiential filler space already exists), do not rebuild.
- ⛔ Do NOT re-run p2's REFUTED role RE-SELECTION (auto-revising an already-committed pick from a fixed parse). This is a
  TARGET-SELECTION prior for the DROP-FILL (recover the missed structure), the recall-scoped route p2 validated.
- ⛔ Do NOT replace the coarse `predictive_reader` centroid with "a bigger centroid" — a centroid cannot separate
  verb-specific fillers (p2's confirmed 4-way negative). The lever is EXEMPLAR/instance structure, not more dimensions on a mean.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- Read p2's `SOLVED.md` (this problem is its follow-on #3) — esp. the drop-fill drill (position carries modern recall; the
  prior earns +0.022 on 19c), the INTERVENING-NP interference collapse, and the ADJACENT COMPONENTS table (`predictive_reader`
  row = "the Phase-1 STRUCTURED verb-role exemplar/event store is the ONLY route").
- Read `hdlab/predictive_reader.py` (the coarse prior you are upgrading — the GATE stays valid) + how p2's `predict_revise`
  drop-fill picks its target (the selector you are improving) + `relcl_resolver.py` (the validated drop-fill target for
  pre-verbal patients). Reuse the promoted GROUNDED meaning codes / the experiential (Binder/Lancaster) filler space.
- Pick REAL role gold where POSITION IS AMBIGUOUS: multiple pre-verbal nominals / non-canonical (passive, object-relative,
  fronted) / a DEGRADED-parse or 19c slice (QA-SRL v2 who-did-what + a LitBank 19c slice, p2's populations). Report n +
  the per-construction breakdown. MIND the corpus-age confound.

## 5. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
PASS = the structured verb-role exemplar store, as the drop-fill TARGET selector, RECOVERS who-did-what CI-SEPARATED over
BOTH (a) the coarse-centroid `predictive_reader` prior AND (b) a POSITION-ONLY selector, ON THE AMBIGUOUS-POSITION slice
(multiple pre-verbal candidates / degraded / 19c), with the info-free TWIN (a VERB-SHUFFLED exemplar store — same fillers,
wrong verb keys — or a filler-shuffled store) LOSING CI-separated, AND a positive control that the win is verb-SPECIFIC
(it concentrates on verbs with a sharp selectional preference and vanishes on flat-preference verbs). Report CI half-width
+ null p95 beside every margin. **A rigorous NEGATIVE is a full PASS if located:** if the verb-role exemplar store,
faithfully built, does not beat the centroid + position on the ambiguous slice, name precisely which verb-role structure
it cannot supply or select (is the signal absent from the available filler co-occurrence, or present-but-not-selectable?)
and localize the ceiling — that tells the assembly whether the WHICH-argument lever is buildable from the substrate's own
grounded knowledge or needs a different source.

## 6. FLOORS + CONTROLS (the strongest trivial methods, actually run)
- **Coarse-centroid `predictive_reader` prior** (the incumbent selector) + **position-only** drop-fill target selector —
  BOTH actually run, on the SAME items; beat WHICHEVER is stronger per slice CI-sep.
- **Info-free twin:** a VERB-SHUFFLED exemplar store (fillers kept, verb keys permuted) OR a filler-shuffled store — must
  LOSE CI-sep (excludes "any per-candidate scorer helps"; the verb-KEYING must do the work).
- **Verb-preference-sharpness stratification** (positive control): the win concentrates on high-selectivity verbs (read/eat)
  and vanishes on flat-preference verbs (have/get) — proves the signal is verb-SPECIFIC selectional structure.
- **Centroid-vs-exemplar ablation:** the SAME grounded fillers as a per-verb-role CENTROID vs an EXEMPLAR/instance store —
  the exemplar structure must beat the centroid (proves it is the instance distribution, not just richer features).
- **Unseen-filler generalization:** held-out fillers not in the store's training (the grounded space should generalize) —
  the regime the propara probe failed; test it explicitly.

## 7. CORPUS-AGE + GENERALIZATION (owner priority — a constructed-gold win is not a capability)
Report on HELD-OUT modern gold (QA-SRL v2, ambiguous-position slice) AND a 19c LitBank slice (p2's finding was the prior
earns its keep exactly on 19c). The win must show on the AMBIGUOUS-POSITION / degraded-parse regime, not the data-rich
easy slice where position already wins — and must generalize to unseen verbs/fillers (per-construction + per-verb-selectivity
breakdown). A gain only on the tuning set or one era is not a capability.

## 8. FILES AND ENTRY POINTS
Build + validate in `experiments/` (compose over `SituationReader.read()` / p2's drop-fill; reuse `predictive_reader` as
the GATE, the grounded/experiential filler space as the fillers, `relcl_resolver` as the drop-fill target). A scaffold-free
witness recomputes, FROM SOURCE: the exemplar-store WHICH-argument selection vs the centroid + position-only floors + the
verb-shuffled twin + the verb-selectivity positive control + the centroid-vs-exemplar ablation, on the ambiguous-position
slice through the live reader. If it clears the bar, strategy lands the hdlab wire (Q111): a default-off structured
verb-role exemplar-store selector for the drop-fill / role-assignment prior, byte-identical when off, witnessed. Fold an
AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the coarse-centroid prior → structured verb-role exemplar store;
whether the substrate's grounded knowledge can supply a verb-specific WHICH-argument lever).

## DO NOT QUOTE / DO NOT REDO
- 🚫 Do NOT quote p2's numbers (+0.0599 drop-fill, +0.022 19c prior) as YOUR result — they are the MOTIVATION. Re-measure
  your exemplar store's selection on your own ambiguous-position population. No number crosses scorers/populations.
- 🚫 Do NOT re-run the refuted / middling prior work as-is (the thematic-fit reader GATE, role RE-SELECTION, a bigger
  centroid). This is a verb-specific WHICH-argument EXEMPLAR selector for the drop-fill at AMBIGUOUS position — a distinct job.
- 🚫 Do NOT claim a win without the VERB-SHUFFLED twin AND the verb-selectivity positive control — the verb-KEYING and the
  instance structure must be shown to do the work (a verb-blind or centroid store winning means the exemplar structure is idle).
- 🚫 Do NOT test only the data-rich modern regime where POSITION already wins — that hides the lever. Test where position is
  AMBIGUOUS / the parse is degraded / prose is archaic (the regime p2 measured the coarse prior failing).
- 🚫 Do NOT use an external LLM as the store or the filler space (the invariant). The exemplar store + fillers must be the
  substrate's own glass-box grounded/experiential representation.
