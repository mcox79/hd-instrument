research: crutch-fade acquisition loop -- owned-organ wiring audit (DRILL 3)
2026-08-10

## HEADLINE

Every piece of the gap-driven crutch-that-fades loop the Director sketched (FLAG -> consult
crutch for the specific gap -> CONSOLIDATE -> GENERALIZE into schema -> crutch fires less)
already exists on disk as a REAL, mostly self-test-verified organ. This is a WIRING JOB, not a
build job -- with one important twist: the two most on-target, most recently-built organs
(hdlab/grounding_acquisition_loop.py and hdlab/script_grain_acquisition_loop.py, both dated
2026-08-09, i.e. built ONE DAY before this drill) are TOTAL INVISIBLE ISLANDS as of this
session's fresh `capability_registry_audit.py` run: zero rows in data/capability_registry.jsonl,
zero consumers anywhere in experiments/*.py. They were about to become the "4th rediscovery"
this drill exists to prevent. The genuine CRUTCH connector (WordNet dictionary lookup -> fading
Bayesian pseudo-counts, hdlab/wordnet_polarity_propagation.py) also exists and also has zero
registry row -- and it plugs into an OLDER, weaker consolidation path
(hdlab/consequence_learning_loop.py's vote-margin-only consolidate()), not into the NEWER
schema-consistency-guarded path (grounding_acquisition_loop.consolidation_pass) that is the
actually-correct false-memory-safe consolidator. That mis-connection -- crutch wired to the
wrong consolidator -- is the single load-bearing gap. Two small connectors close it (Section 3).

KB-CHECK done first: `capability_registry_query.py --serves` (multi-term substring probes:
acquisition/consolidation/gap/schema/grounding/learner/predictive/abstain/false/consequence/
replay/cls/situation/goal) + a fresh `capability_registry_audit.py` run (report written to
data/capability_registry_reports/registry-audit-20260810T115325Z.json). Prior drilling avoided:
no 2026-08 research note previously mapped this specific 6-piece loop end-to-end.

## The loop-piece -> owned-organ table (every organ read on disk, not just its docstring; two
modules' self_test() re-run live this session to confirm PASS, not just cited)

| # | Loop piece | Owned organ (file::symbol) | Real vs synthetic | Wired status (this session's audit) | Gap |
|---|---|---|---|---|---|
| 1 | GAP-FLAG | hdlab/predictive_coding.py (threshold_gate / relative_threshold_gate, generic residual-mismatch novelty gate, Friston/Rao-Ballard) | Real generic math; ALREADY_WIRED, touched by 10+ experiment cells | WIRED (registry: predictive_coding, ALREADY_WIRED) | The actual "is this word/concept novel" test built on top of it, `word_acquisition_loop.word_is_novel()`, is a TOY binary formalization (observed=ones(8) vs zeros(8) depending on lexicon membership) -- it reuses the gate's plumbing but not its graded surprise signal. `script_grain_acquisition_loop.py`'s own docstring (Correction #6) reports the graded RELATIVE gate actually UNDERPERFORMS the absolute gate on this substrate's residual (f1 0.697 vs 0.905, MIDDLE_BAND) -- an honest negative result, not yet resolved. |
| 2 | ACQUISITION LOOP (word-grain FLAG + credit) | hdlab/consequence_learning_loop.py (teacher_verdict + referent-linked credit_window, structural MET/UNMET teacher from hdlab.goal_typing) | Real: corpus-window mechanism with referent-linkage via coref, not a bag-of-words stoplist; self-test exercises real micro-episodes | **NOT in capability_registry.jsonl** (1 of 69 unregistered hdlab/*.py flagged by this session's audit) despite being a direct dependency of 3 other modules (wordnet_polarity_propagation, grounding_acquisition_loop, script_grain_acquisition_loop) | Needs a registry row. Its sibling, the OLDER 2-channel `hdlab/word_acquisition_loop.py`, IS registered and is SHELVE/HARD_FAIL (held-out acc 2/7, noise 2/8) -- do not confuse the two lineages; consequence_learning_loop is the mechanistically different, newer, and (per Section 4) more promising line. |
| 3 | SAFE CONSOLIDATION + FALSE-MEMORY GUARD | hdlab/grounding_acquisition_loop.py::consolidation_pass -- schema_consistency_split_half (context-coherence guard over independently-accumulated trace halves) + Dumay-Gaskell mandatory intervening-pass rule + patience-then-ESCALATED (never force-commits), explicitly citing Warren et al. 2014 (vmPFC/DRM: the SAME circuit that fast-tracks true learning manufactures false memories, so vote-agreement alone cannot be the only gate) | REAL. Self-test RE-RUN live this session (`PYTHONPATH=. python hdlab/grounding_acquisition_loop.py`): PASS -- coherent_score=1.0, scrambled_score=0.108, and the adversarial can-fail case (consistent VOTES but scrambled CONTEXT) correctly ESCALATES rather than grounding -- this is exactly the guard behavior the loop design needs, verified not just claimed. | Built 2026-08-09. **ZERO consumers in experiments/*.py. NOT in capability_registry.** Complete island; the single most on-target and most invisible piece in this whole audit. | Needs (a) a registry row, (b) any experiment-cell wire-point (the established pattern used elsewhere is a thin `experiments/verify_grounding_acquisition_loop_v1.py` importing the module so `tools/integration_health.py`'s import-graph scan registers it as pipeline-reachable). |
| 3b | generic vote-margin guard (reused by #2, #3, word_acquisition_loop) | hdlab/self_improving_loop.py::decide_keep_or_revert (abstain-band adoption rule) | Real, reused across the whole codebase | WIRED, one of only 10 active-pipeline-reachable hdlab modules per the audit | None structural. Worth flagging explicitly: vote-margin-only gating (this function alone) is EXACTLY the false-memory-prone mechanism Warren et al. 2014 describes -- #3's schema-consistency split-half is the mandatory SECOND, independent gate, not decoration. Any acquisition path that calls decide_keep_or_revert WITHOUT also calling schema_consistency_split_half (i.e. word_acquisition_loop.py and consequence_learning_loop.py's own consolidate()) is running the pre-guard, false-memory-vulnerable version of this loop. |
| 4 | CLS CONSOLIDATION ("sleep"/replay, storage-dynamics) | hdlab/hippocampal_encoder.py -- DG-analog sparse expansion + CA3 Hebbian pattern completion + cls_discrete_budget_consolidate (discrete-budget offline replay, McClelland/McNaughton/O'Reilly 1995) | Real, chain-grade (exp_cls_ca3complete_consolidation_v1, commit 92e01cf3f) | WIRED, ALREADY_WIRED, 5+ real experiment consumers | **Mislabel-adjacent trap avoided**: this is a DIFFERENT problem than #3. #3 asks "is this flagged item trustworthy enough to write at all" (truth-gating); #4 asks "how do I integrate a write into a Hopfield-style associative store without catastrophically forgetting old associations" (storage dynamics). The crutch-fade loop needs #3 to gate, then (optionally, at scale) #4 to physically integrate the write. They are not substitutes for each other. Separately: `cls_discrete_budget_consolidate_v6_replay` (the specific v6-replay wiring experiment) is VET_PENDING and STALE 12.7 days per this audit -- needs a decision, not a re-drill. |
| 5 | SCHEMA INDUCTION (generalize specific fills into a schema) | hdlab/learner/ (registry.py `learn()` -- MDL two-part-code model selection across estimation/ruleind/GAM/proginduction plugins, Perfors & Tenenbaum 2009) consumed two ways: (a) as Channel A inside word_acquisition_loop (construction-cue -> polarity), (b) as an optional CONJUNCTIVE `mdl_gate_fn` inside grounding_acquisition_loop.consolidation_pass, (c) directly inside hdlab/script_grain_acquisition_loop.py's ScriptLibrary.match_or_spawn (CA3/DG attractor keying, hdlab.cleanup_family.iterative_attractor, clusters raw episodes into recurring event-TYPES) | hdlab.learner itself: real, mature, widely reused (frame_induction.py's own pattern). script_grain_acquisition_loop: REAL, self-test RE-RUN live this session -- PASS: matched-pair cosine 0.361 vs wrong-pair -0.013 (clean separation), scramble control collapses to 0.003, singleton-noise-never-merges holds. This is a genuine brain-fidelity-audited (2026-08-09 audit) CA3/DG generalization mechanism, not a toy. | hdlab.learner: WIRED, solid. **script_grain_acquisition_loop.py: ZERO consumers, NOT in capability_registry** -- same invisibility as #3, built the same day. | **MISLABEL FLAG (per the 9+ mislabels-this-session pattern)**: `hdlab/schema_exemplar_bayes.py` is NOT a schema-induction/generalization organ despite its name -- read on disk, it is an LSE-Bayes RETRIEVAL-COMPRESSION/routing primitive (10x cheaper cluster-routed lookup for already-stored facts), unrelated to generalizing specific instances into an abstract schema. Separately, the registry's OTHER "schema_abstraction" row (ALREADY_WIRED, glossed "template/slot-filling extraction") is ALSO not this drill's schema-induction mechanism when read on disk (experiments/exp_read_grow_schema_abstraction_predictive_precision_v2.py) -- it is UD-dependency SYNTACTIC-fragment abstraction (dropping function-word children from a construction shape), a genuine but SYNTAX-grain generalization mechanism, not the SEMANTIC/event-script generalization this loop needs. The correct organ for "generalize specific fills into a schema" at the semantic/event grain is `script_grain_acquisition_loop.ScriptLibrary.match_or_spawn` + hdlab.learner's MDL gate, not either of the two same-named-sounding rows already in the registry. |
| 6 | THE STORE (where consolidated/generalized knowledge lives) | hdlab/situation_model_accumulate.py (episodic/working-memory FHRR register) + hdlab/kg_traversal.py::KGStore ((s,p,o) Hebbian KG store, CERT 585 chain-grade, 36.49x over frozen-encoder baseline) + hdlab/hd_fact_store.py (source-trust-vetted fact store, provenance+trust natively bound into the fact vector, not side metadata) | All three real, CERT/chain-grade-validated | All 3 WIRED (situation_model_accumulate: pipeline-reachable; kg_traversal/kg_ingest: ALREADY_WIRED; hd_fact_store: WIRED) | None structural -- the store layer is the most mature part of the whole loop. The open question is a CONNECTOR, not a missing organ: nothing currently writes an acquisition-loop's GROUNDED output into kg_traversal or hd_fact_store. Today word_acquisition_loop/grounding_acquisition_loop write only into hdlab.verb_lexical_similarity's Tier-3 overlay (a flat lexicon dict) -- see Section 3, connector (c). hd_fact_store's native SOURCE/TRUST binding is an unusually good fit for a "crutch-sourced fact starts low-trust, gets promoted as real corpus evidence accumulates" design, but nobody has pointed at it yet. |

## The loop's actual current shape (both lineages, read off the code, not the docstrings)

Two acquisition-loop LINEAGES exist and should not be conflated:

- **Lineage A (2026-08-06, older, weaker, already triaged)**: `word_acquisition_loop.py` --
  two-channel (construction-cue MDL "Channel A" + reward-grounded appraisal "Channel B"),
  STRICT two-channel agreement, consolidated via `decide_keep_or_revert` alone (no
  schema-consistency guard). Registered, SHELVE, measured HARD_FAIL (held-out 2/7,
  noise_consolidated 2/8). The registry's own revival_criteria diagnose the missing lever as
  "a telicity/result-state discriminator or richer antecedent-goal context" -- it does NOT
  mention a false-memory guard, because this lineage predates the Warren-2014 audit.
- **Lineage B (2026-08-06 FLAG + 2026-08-09 GUARD, newer, structurally stronger, currently
  invisible)**: `consequence_learning_loop.py` (structural MET/UNMET teacher + referent-linked
  credit) feeds `grounding_acquisition_loop.py`'s trace-level Library, gated by BOTH vote-margin
  (self_improving_loop) AND schema-consistency split-half (the Warren-2014-motivated guard) AND
  an optional MDL compressibility check (hdlab.learner). `script_grain_acquisition_loop.py`
  extends the SAME guard machinery to the event-TYPE/script grain via CA3/DG attractor keying.
  This lineage is unregistered and unwired, but on the evidence (both self-tests PASS, both
  correctly reject the adversarial scrambled-context case) it is the mechanistically correct
  successor to Lineage A -- reviving/registering Lineage A without first wiring Lineage B's guard
  on top would be reintroducing the exact false-memory failure mode Lineage B was built to close.

## Section 3: the minimal wiring to compose the existing organs

Nothing below requires a new algorithm. In order of cheapest-first:

1. **Registry hygiene (mechanical, ~30 min)**: add capability_registry.jsonl rows for the 4
   unregistered-but-real modules this audit found: `consequence_learning_loop.py`,
   `wordnet_polarity_propagation.py`, `grounding_acquisition_loop.py`,
   `script_grain_acquisition_loop.py`. This alone stops the 69-unregistered-module list (this
   session's audit) from silently regrowing and prevents a future session re-discovering the
   same organs from scratch (exactly the failure `working_overlay_situation_reader`'s own
   registry row was created to stop a 4th time of).
2. **Pipeline-reachability (mechanical, ~1-2 hrs)**: give `grounding_acquisition_loop.py` and
   `script_grain_acquisition_loop.py` a thin `experiments/verify_*_v1.py` wire-point consumer,
   the same established pattern already used for `situation_model_accumulate.py` and
   `coreference_resolver.py` (see those two registry rows for the exact recipe: a small cell
   that imports the module and calls its self_test, nothing more). This flips both from ISLAND
   to WIRED under `tools/integration_health.py`'s import-graph scan without touching either
   module's internals.
3. **The CRUTCH connector (real design work, small scope, the load-bearing gap)**: today
   `wordnet_polarity_propagation.pseudo_counts_from_dictionary` only feeds
   `consequence_learning_loop.learn_corpus`'s OWN vote-margin-only `consolidate()` (Lineage A's
   consolidation shape) via its `dictionary_priors` parameter -- and that injection already has a
   proven FADE property (self-test item 7 in consequence_learning_loop.py: a fixed-size
   dictionary pseudo-count's PROPORTIONAL vote-share shrinks automatically as real corpus
   MIN_CONFIRM exposures accumulate on top of it -- this is genuinely "crutch fires less over
   time," already built, just not connected to the guarded consolidator). It has never been
   wired into `grounding_acquisition_loop.Library`/`consolidation_pass` (Lineage B, the guarded
   one). The correct connector: extend `Library.flag` (or add a sibling `Library.flag_prior`) to
   accept a dictionary-sourced pseudo-trace that contributes to the VOTE-MARGIN/patience
   accounting exactly like consequence_learning_loop's existing injection, but is EXCLUDED from
   `schema_consistency_split_half`'s context-coherence computation (a dictionary lookup has no
   corpus context vector to contribute honestly). This preserves the false-memory guard's
   invariant -- the crutch can bias the vote tally and buy patience, but genuine schema-coherence
   from >= MIN_CONFIRM independent REAL episodes is still required before anything BANKs. This is
   a signature extension to one function plus a small adapter, not a new mechanism.
4. **The BANK/GENERALIZE-to-STORE connector (real design work, small scope, currently a dead
   end)**: a `script_grain_acquisition_loop.ScriptLibraryItem` that reaches `GROUNDED_*` status
   currently just sits in the in-memory `ScriptLibrary` -- nothing persists it. Its structural
   register (TRIGGER/CONSEQUENT/AGENT/PATIENT role-filler bundle) is exactly (s,p,o)-shaped, so
   the natural target is either `kg_traversal.KGStore.ingest_triples` (bulk Hebbian write) or
   `hd_fact_store.HDFactStore.store` (source-trust-vetted, which is the better fit: a
   crutch-assisted grounding can be tagged TRUST_MID/LOW at write time and a later
   independently-reconfirmed one promoted, giving the loop a SECOND place "fade" is visible --
   trust-weighted store confidence, not just vote dilution). This connector does not exist in
   either direction today.

No 4th connector is needed: the GAP-FLAG (#1), generic guard (#3b), CLS/replay (#4 in the table),
MDL schema-worthiness check (#5), and all three stores (#6) already compose with each other via
existing call signatures; the only calls that have never actually been MADE are #3 and #4 above.

## Honest verdict: wiring job vs build job

**Overwhelmingly a WIRING job.** Every organ the Director's 6-piece loop description named has a
real, on-disk, mostly self-test-verified counterpart -- most of them (Lineage B: FLAG, guard,
script-grain schema induction) were built in the 4 days immediately preceding this drill
(2026-08-06 through 2026-08-09), evidently already converging on this exact design before this
audit was requested. Two self-tests were re-run live this session (not just cited) and both
PASS, including their adversarial can-fail cases. The only genuine (small) BUILD work is the two
connectors in Section 3 items 3-4 -- a vote-margin-only injection path adapted onto the
schema-guarded consolidator, and a persist-to-long-term-store call that doesn't exist yet for a
freshly-grounded script schema. Both are signature extensions / new call sites on top of
existing, validated functions, not new algorithms.

The bigger risk this audit surfaces is PROCESS, not mechanism: the single most on-target,
most-recently-built, most rigorously self-tested pair of modules in the entire codebase for this
exact task (`grounding_acquisition_loop.py`, `script_grain_acquisition_loop.py`) were, until this
drill, completely invisible to every discovery mechanism the project has (capability_registry
query returned 0 hits on either name; the audit's own 69-unregistered-module list is the only
thing that surfaced them). If DRILL 3 had not been run, the natural next step would likely have
been to re-derive a crutch-fade design from scratch -- a 3rd or 4th rediscovery of work already
done, per the exact failure pattern `working_overlay_situation_reader`'s registry row already
warns about once.

## Cheap decisive test (if the Director wants a fast go/no-go before investing in the connectors)

Wire connector #3 first (cheapest, most load-bearing) and re-run
`grounding_acquisition_loop.py`'s self_test plus one new adversarial case: a lemma whose
WordNet-dictionary crutch vote DISAGREES with what >= MIN_CONFIRM real corpus episodes eventually
show. HARD-PASS: the loop banks the CORPUS-supported polarity once real evidence accumulates
(the crutch's influence fades/gets overridden, not locked in). HARD-FAIL: the dictionary prior's
initial vote persists and out-votes >= MIN_CONFIRM disagreeing real episodes (the crutch never
fades -- would mean the pseudo-count weighting needs recalibrating, K_MAX=MIN_CONFIRM=3 may be
too strong relative to real per-episode evidence weight of 1).

## Falsifiable predictions

- HARD-PASS: connector #3, once wired, reproduces consequence_learning_loop's own self-test
  item-7 INJECT-ONCE fade property (prior seeded once, real evidence dilutes it proportionally)
  AND grounding_acquisition_loop's adversarial scrambled-context case still ESCALATES even when a
  dictionary crutch votes confidently on that same lemma (the schema-consistency guard must still
  block a confidently-wrong crutch vote from banking without real coherent context -- this is the
  actual point of keeping schema_consistency_split_half computed from REAL traces only).
- HARD-FAIL: wiring the crutch causes ANY previously-ESCALATED adversarial (scrambled-context,
  consistent-vote) case to newly GROUND -- would mean the crutch injection leaked into the
  schema-consistency computation and reintroduced the exact false-memory failure mode the guard
  exists to prevent.

## Cross-thread synthesis

This drill sits directly downstream of the 2026-08-09 brain-fidelity architecture audit
(notes/research_brain_fidelity_architecture_audit_2026-08-09.md, cited inline by
script_grain_acquisition_loop.py's own docstring) which is what motivated Lineage B's 6
corrections over Lineage A. It is a SEPARATE lineage from the currently-active SIMULATION-ENGINE
program (hdlab/situation_focus.py, RETRIEVE->VALIDATE->ADVANCE over an activated-LTM field,
per the MEMORY banner's CURRENT FOCUS) -- the two should not be conflated; this crutch-fade
acquisition loop is about HOW new word/script-level knowledge enters the substrate, not about
inference-time retrieval over already-consolidated knowledge. They will eventually need to meet
at the STORE layer (kg_traversal / situation_model_accumulate are common ground to both), but
that convergence is not yet designed and is out of scope for this drill.

## Substrate-product implications

A working crutch-fade loop is a directly demoable product story ("the system starts by looking
things up, then stops needing to") distinct from raw benchmark accuracy -- the auditable trace
(dictionary-vote vs corpus-vote vs schema-guard verdict, all inspectable per item) is exactly the
glass-box differentiator the substrate's whole value proposition rests on. The connectors named
in Section 3 are the last mile between "the mechanism exists" and "the product story is
demoable end-to-end on a real passage."

## Citations (verified count: 0 external; this was an internal owned-organ code audit per the
Director's DRILL 3 instructions, not a literature scan. All citations above are to files read
directly on disk this session, quoted by path, or to prior internal research notes cited inline
by those files' own docstrings (Warren et al. 2014, Dumay & Gaskell 2007, Tamminen et al. 2010,
van Kesteren et al. 2012, Ghosh & Gilboa 2014, Perfors & Tenenbaum 2009, McClelland/McNaughton/
O'Reilly 1995, Treves-Rolls, Lisman & Grace 2005 -- all as already cited by the audited modules
themselves, not independently verified against the primary literature this session).
