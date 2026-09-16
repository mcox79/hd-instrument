---
problem: the_structure_map_every_organ_to_the_brain_structure_it_stands_in_for_the_computation_it_performs_the_organs_that_perform_the_same_computation_and_the_structures_each_task_uses_and_should_use
status: SOLVED
bar: "1. Every organ mapped -- one row per hdlab/*.py module (structure with citation, computation as one sentence of math, BF status reconciled with the registry, arms, importers, copies); zero unmapped. 2. The same-computation groups WITH THE MATH, found by reading what each organ computes, each with the measured evidence that they are the same computation and where each member deviates. 3. The cost table -- read time per organ on the same 6 GUM documents from one profiled full read, per-module attribution, total, redundant work named. 4. The coordination map -- for each board row + where-is + the entity set: the structures used today (traced), the structures the brain uses (cited), every missing conjunction with the rows it would touch. 5. The ranked consolidation list, ordered by duplicated computation x read-time cost x product rows affected, each assigned to pri 143 / 144 / 145 or new brief-ready text. 6. Registry brain_structure + fidelity_basis filled via the locked writer; ORGAN_MAP.md regrouped by structure with the task view kept; BRAIN_FOUNDATIONAL_AUDIT.md gets a 2b entry. 7. No code changed in hdlab/ or tools/ (witness: git diff --stat -- hdlab tools empty for the solver's commits)."
result: "THE MAP IS COMPLETE AND IT FOUND SOMETHING THE BRIEF DID NOT ASK FOR AND NOTHING IN THE ARCHITECTURE MADE VISIBLE. (1) SCOPE, CORRECTED: the substrate is 278 .py modules under hdlab/ (265 package root + 7 learner/ + 6 dashboard/), not the ~70 the brief assumed and not the 155 ORGAN_MAP section 1 records. ALL 278 ARE MAPPED, zero unmapped, into 21 brain structures plus two honest non-brain buckets (37 instrumentation, 9 compute-budget). (2) THE COST TABLE, AND ITS HEADLINE IS NOT A CONSOLIDATION: one profiled full read of 6 GUM TEST documents / 480 sentences, every document re-read for contention (ratios 0.78/0.81/0.80/0.78/0.81/0.78 -- all six stable, none discarded). Honest wall clock 44.7 s per document, 0.559 s per sentence. SIXTY-ONE PER CENT OF A READ IS ONE OPERATION: grounded_semantic_graph._ppr, thirty power iterations of r = (1-d)p + d*T^T r, 204.5 s of 337.4 s profiled, 672 runs, 184.8 s of it sparse matrix-vector product (20,160 of them), all inside force_dynamics_valence's harm/help judgement via situation_reader._assign_affect. The affect dimension reads as 0.1% of the per-module cost table because its whole cost is in the organ it calls -- per-module cost hides cross-organ cost, and that is a lesson for every future profile here. (3) THE OPTIMISATION IS MEASURED, NOT SIZED: a per-read memo keyed on the exact seed index tuple removes 26-40% of the PPR runs inside ONE document (46 of 116 repeats on GUM_academic_census, 7 of 27 on GUM_letter_marcie3) and 28-39% of the whole read (15.11 s -> 9.25 s; 3.18 s -> 2.24 s). ON THE DOCUMENT WHERE THE READER WAS STABLE THE MEMOISED READ IS BYTE-IDENTICAL. (4) AND THE PROBE'S CONTROL FOUND A SECOND THING WORTH MORE: THE READER IS PLASTIC WITHIN A PROCESS -- two consecutive un-shimmed reads of GUM_academic_census do NOT agree, because lexical_categories and the validity tables observe while they read. That is correct and brain-faithful, and it means no experiment may assume a repeated read is a repeated measurement. The first version of this very probe asserted exactly that and failed; the control is now in the cell. (5) THE SELECTION GROUP IS 28 ORGANS, ONE EQUATION, FIVE PRIVATE IMPLEMENTATIONS, 16.8% OF READ TIME. The equation is graded_competition's A_i = SUM_c w_c*support_c(i), softmax = the Bayesian/FLMP posterior (McClelland 2013), argmax = a task-triggered collapse. graded_role_assigner.strengths_from_counts learns log P(k|cfg,value) - log P(k|cfg) from counts and IS the reference implementation -- while AGENT_VALIDITIES BESIDE IT IN THE SAME FILE IS EIGHT HAND-SET CONSTANTS with no observe path (preverbal 3.0, core_arg 2.0, animacy 2.0, salience 2.0, adjacency 1.0, byagent 6.0, structure 2.5, byhead 2.0), affected_entity_resolver uses two hand-swept gammas, attachment_arm uses the same equation from a SECOND table builder (tools/build_attachment_validities.py), and SPACE_READER'S GROUND SELECTION IS NOT A COMPETITION AT ALL -- _pp_ground / _dobj_ground / _anticipated_ground are a first-match linear scan with hand-ordered fallbacks and _anticipated_ground fires only when exactly one candidate exists. The four organs that do share properly all call ONE salience_binder.actr_activation for their base term, so the retrieval math is already shared and only the wrappers are not. (6) THE REGISTER GROUP IS SIX ORGANS IN THREE DATA SHAPES. state_register and location_register are near-identical per-entity interval bookkeeping (state_register's own docstring says so); world_state_register is the same shape keyed on the OBJECT; goal_register and affect_register are FLAT LISTS with no time index and no update rule; belief_timeline HOLDS NO STATE and recomputes from the event list on every query. Traced from situation_reader._read_goals's AST, the goal register imports NO register at all -- so a goal is closed by predicate + agent in a strictly later sentence and never by the result state state_register wrote earlier in the same read. That is the owner's 2026-09-16 concern, located in code -- AND THE REPAIR IS SIZED: on one live read of the same 6 GUM documents, 16 of 26 goals (62%) already have an agent the state register holds a state for, while 10 (38%) cannot be joined at all until the one entity id space lands; all 74 state tracks carry at least one state, so the two registers sit next to each other in the same read with a 62% key overlap and no wire between them. (7) THE THIRD GROUP IS ALREADY DONE AND IS THE MODEL CASE: pri 127 put every read-time lexical lookup behind ONE content-addressed store; ZERO hdlab modules call nltk on the read path; 6.5 million lexical reads per 480 sentences through one address space, 4.2% of read time. temporal_model's 2026-09-11 three-layer consolidation is the second worked example. BOTH remaining groups should be executed the same way -- byte-identical per arm first, then the shared repair. (8) THE BRIEF'S FOURTH INFERRED GROUP DOES NOT EXIST: reading the math, the frozen-table typers ARE the lexical-read group's arms and the counted typers ARE the selection group. There are three groups, not four, and the third is finished. (9) A FIFTH GROUP THE BRIEF DID NOT NAME: four objects can produce heads for one sentence (arc_parser and arceager_parser both NOT_BF, graded_parser, attachment_arm), and the frozen assets say who reads what -- pos_tagger_ud_ewt_upos.json is loaded by SEVEN modules and arc_parser_hashed_ud_ewt.npz by FOUR, while hdlab/frontend.py exists to be the one source and has 40 importers. (10) REDUNDANCY, COUNTED, AND THE BRIEF'S INFERENCE CORRECTED: at the reader level the waste is a factor of ~2, not the ~90k re-parses the brief inferred -- attachment_arm.arc_scores 2.17x per sentence, lexical_categories.posterior 1.98x per sentence, scene_segment.parse_conll_sentences 4x per document. pri 112's one in-order category feed IS genuinely one pass per document (feed_passage = 6 calls / 6 documents) and the point tag IS served from the cache (0.96x); it is the POSTERIOR that is recomputed. (11) THE BF AUDIT'S REAL COVERAGE: notes/bf_status_registry.jsonl rates 94 of 278 modules (8 BF, 80 BF_SPIRIT, 6 NOT_BF); 184 are unrated. Of the 56 modules that execute on a live read, 13 are unrated -- and they include grounded_semantic_graph (60.6% of read time), graded_competition (the engine pri 143 is built around) and situation_reader itself. (12) THE 23 DEFAULT-ON DIMENSIONS, RECONCILED AND FINISHED (pri 139 mapped 10): 17 literal track_* ON + 6 further dimension flags = 23, with track_coherence the one OFF; each is mapped to the board row or ability that scores it; FOUR HAVE NO CONSUMER AT ALL (track_tom_action, track_prediction, bind_event_tokens, read_polarity) and ten are lazy closures costing nothing until invoked. (13) FOUR STAND-INS ON THE LIVE CHAIN, named by reading the math: the agent pick's weights, the goal register, the belief timeline, and ground selection. (14) THE MAP AUDITS ITSELF: 83 of 278 rows had their computation read from CODE this pass, 195 take the module's own stated computation; every row load-bearing to the groups, the ranking and the live chain is a code-read row, and the src column says which is which so a later brief can tell."
floor: "A map is graded by completeness and by what it lets the next brief measure, so the floors here are coverage and stability, recomputed on this pass's own population. COVERAGE: 278 of 278 modules mapped (os.walk over hdlab/, excluding __pycache__) -- the floor is the brief's own assumption of ~70 and ORGAN_MAP section 1's 155, both of which this pass falsifies on disk. REGISTRY: brain_structure was present on 59 of 264 rows before this pass (the brief asserted 'every row'); it is present on 339 of 339 after. BF RATINGS: 94 of 278 -- the floor for any claim about substrate-wide brain-faithfulness, and it is why '5 of 38' is reconciled rather than restated. COST: the contention floor is the unprofiled repeat of every document in the same process -- 0.78, 0.81, 0.80, 0.78, 0.81, 0.78, all six within 4% of each other and every repeat FASTER than its profiled pass, so no row was discarded as unstable and the honest wall clock (268.4 s / 6 documents) is reported separately from the profiled one (337.4 s, ~26% profiler inflation). THE MEMO: its floor is the SAME document read twice with no memo at all -- which is what exposed the reader's plasticity and is why the saving on GUM_academic_census is reported as a timing and not as a certified equivalence. COPIES: verification/test_organ_copies_are_one_object.py re-run 2026-09-16, 4/4 checks PASS, 16 pairs, 14 DRIFTED COPY, 2 THIN SHIM, 0 new drift since the 2026-09-16 baseline -- pri 139's standing witness is the floor for the copy count, not a fresh count of my own."
controls: "(1) THE CONTENTION CONTROL THE BRIEF REQUIRED: every one of the 6 documents is read a SECOND time in the same process, unprofiled; all six ratios landed in 0.78-0.81, so the table is reported whole rather than as 'the stable pairs only'. The laptop had 10 python processes running (a product board and another solver) throughout. (2) A PLASTICITY CONTROL INSIDE THE OPTIMISATION PROBE: each document is read TWICE UN-SHIMMED before the memoised read, so an unsafe cache is told apart from the reader's own plasticity. This control is the reason the probe reports an honest 'not certifiable' on one document instead of a false identity claim -- the probe's FIRST version had no such control, asserted identity, and failed; the failure is reported here rather than hidden. (3) THE MEMO RETURNS THE MEMOISED VALUE VERBATIM, so the read is unchanged by construction, and the situation-model signature (sentences, entities, events, and the sorted (predicate, agent, patient) tuples) is compared anyway. (4) ABSOLUTE SECONDS ARE NOT COMPARED ACROSS PROCESSES: the same document reads in 15.1 s in the memo probe and 48.9 s in the cost profile, so the seconds-per-document figures in the ranked list apply the measured PERCENTAGE to the contention-checked wall clock, and this is stated in the map. (5) THE GROUPS WERE FOUND BY READING THE MATH, NOT THE NAMES, and the map publishes which rows were read from code (83) and which take the docstring (195) so the next brief knows which rows to re-read before touching them. The one group the brief inferred that does NOT survive reading the math (the 'typers') is reported as refuted rather than quietly dropped. (6) THE CALL GRAPH FOR THE COORDINATION MAP IS TRACED FROM THE AST of situation_reader.py (every 'from hdlab' inside each _read_* body plus every module-level name that body references), not from prose -- which is how 'the goal register imports no register at all' became a fact rather than an impression. (7) LANDINGS IN FLIGHT ARE MAPPED AS THEY SAT ON DISK WHEN READ, with the timestamps recorded: entity_resolver.py, coref.py, situation_reader.py at 2026-09-16 07:46-07:47, graded_role_assigner.py 02:15, goal_register.py 2026-09-15 21:45. (7b) A LANDING ARRIVED MID-PASS THAT BEARS ON THE MAP'S BIGGEST FINDING, AND I CHECKED IT AGAINST THE DISK RATHER THAN THE COMMIT MESSAGE: pri 140 committed b14a34d3e at 09:07 under the headline 'the agent cue validities are ACCRUED FROM READING, not hand-set'. That commit did NOT change hdlab/ -- it shipped a proposed diff, a learned asset, a cell and a witness -- and hdlab/graded_role_assigner.py:269-271 still reads the eight hand-set constants at 09:10. The map records the row as the tree stands AND flags that it is about to stop being true, with what changes when pri 140's diff lands. (8) THE REGISTRY WAS WRITTEN ONLY THROUGH THE LOCKED HELPERS (registry_transaction / append_rows); a backup was taken first; and MY OWN FILL HAD TWO DEFECTS WHICH I FOUND AND CORRECTED THROUGH THE SAME HELPER AND REPORT HERE -- a `break` bug gave 19 modules a duplicate row, and multi-path bundle rows had silently taken their first path's structure. After the correction: 339 rows, all with both fields, all 278 modules covered, zero duplicates, unique ids, valid JSON. (9) A COUNT I PUBLISHED WAS WRONG AND IS CORRECTED IN PLACE WITH ITS OWN COMMIT: I wrote '21 of 56 live modules unrated' from memory; recomputed against the disk it is 13, and the 13 are named. (10) NO hdlab/ OR tools/ FILE WAS WRITTEN -- the witness is `git diff --stat 9056ad7bb~1..HEAD -- hdlab tools`, EMPTY. (11) MODERN GOLD ONLY: the cost table and both probes run on the board's own GUM TEST split (odd document index), evenly spaced across genres so a prefix cap cannot hand the profile one or two genres. data/corpora/holdout/ was never read. (12) NO RETIRED FIGURE IS QUOTED; the ORGAN_MAP figure that is retired at the top of that file is not repeated, and the stale counts in its section 1 are flagged in the new section 3b rather than silently overwritten."
files_changed: "notes/STRUCTURE_MAP_2026-09-16.md (NEW -- the map: the counts, the disagreements with the disk, all 278 organ rows by structure, the three same-computation groups with their math, the two groups the brief got wrong, the cost table, the measured optimisation, the ranked consolidation list, the coordination map per board row, the 23 dimensions, the owner's push script answered, and what this pass did NOT measure). experiments/exp_structure_map_cost_v1.py (NEW -- the profiled read with per-module attribution and the contention check (--run), the optimisation probe with its plasticity control (--cache-probe), the coordination probe (--coord-probe), and --self-test 3/3; output dir from experiments._seed_checkpoint.get_output_dir per Q115). data/capability_registry.jsonl (brain_structure + fidelity_basis + computation + bf_status_disk on all 339 rows; 75 modules that had no row now have one -- written ONLY through tools/capability_registry_audit.py's registry_transaction / append_rows). notes/ORGAN_MAP.md (NEW section 3b: regrouped by brain structure, with the task view in section 4 KEPT UNCHANGED and its stale file count flagged). notes/BRAIN_FOUNDATIONAL_AUDIT.md (a section 2b entry, newest-first). data/exp_structure_map_cost_v1/{metrics.json, read_profile.prof, cache_probe.json, coord_probe.json}. NO hdlab/ or tools/ file was written; nothing was renamed; no copy was collapsed (those are pri 143-145)."
reverify: "1) .venv/Scripts/python.exe experiments/exp_structure_map_cost_v1.py --self-test    # 3/3, ~30 s, writes only to data/exp_structure_map_cost_v1_selftest/.  2) THE COST TABLE, ~25 min under load:  OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0 .venv/Scripts/python.exe experiments/exp_structure_map_cost_v1.py --run --docs 6    # expect grounded_semantic_graph._ppr at ~60% of cumulative time, arc_scores ~2.17x per sentence, and all six contention ratios near 0.8.  3) THE OPTIMISATION, ~5 min:  ... --cache-probe --docs 2    # expect a 26-40% repeat share and a byte-identical read on whichever document reports plastic_read_to_read=False.  4) THE COORDINATION COUNT, ~10 min:  ... --coord-probe --docs 6.  5) THE COPY CENSUS (pri 139's standing witness, not mine):  .venv/Scripts/python.exe verification/test_organ_copies_are_one_object.py    # 4/4, 16 pairs, 14 drifted.  6) THE NO-CODE-CHANGE WITNESS:  git diff --stat 9056ad7bb~1..HEAD -- hdlab tools    # EMPTY.  7) THE REGISTRY:  .venv/Scripts/python.exe -c \"import json;rows=[json.loads(l) for l in open('data/capability_registry.jsonl',encoding='utf-8') if l.strip()];print(len(rows), sum(1 for r in rows if r.get('brain_structure') and r.get('fidelity_basis')))\"    # expect 339 339."
---

# The structure map: 278 parts, 21 structures, three same-computation groups — and 61% of a read is one graph walk nobody had named

**STATUS: SOLVED** (solver scope; WIP until the owner marks DONE). Documents + registry fields + one measured
cost table, exactly as the brief scoped it. **No `hdlab/` or `tools/` file was written.** Modern gold only
(GUM TEST split). `data/corpora/holdout/` was never read.

**The map itself is `notes/STRUCTURE_MAP_2026-09-16.md`** — read that, not this file, for the rows. This file
records what the pass established, how it could have failed, and where it was wrong.

---

## THE FIVE THINGS THE OWNER ASKED FOR, AND WHERE EACH ONE LANDED

| the owner's question (2026-09-16) | where the answer is | the number |
|---|---|---|
| "map every organ to the brain structure it stands in for" | STRUCTURE_MAP §4 | **278 of 278**, 21 structures, zero unmapped |
| "the organs that perform the same computation" | §5 | **three groups**: selection (28 organs, 16.8% of read time), register (6 organs, 3 data shapes), lexical read (**already done** — the model case) |
| "include optimization" | §6, §7.1, §7.3 | **60.6% of a read is one operation**; a memo removes **28–39%** of the whole read, byte-identical where certifiable |
| "tasks aren't using other brain components in conjunction when they could and should" | §8 | **11 missing conjunctions**, each with the rows it would touch; the sharpest is the goal register, which imports **no register at all** |
| "once consolidated, research will make it clear whether each component does what it should" | §7 | the **ranked list**, items assigned to pri 143 / 144 / 145 and two new brief-ready texts |

---

## WHAT I GOT WRONG IN THIS PASS, AND FIXED

Recorded because a map whose author does not audit himself is worth less than one who does.

1. **My registry fill had a `break` bug.** It took only the *first* `hdlab/*.py` path of each registry row,
   so 19 modules covered by multi-path bundle rows looked uncovered and got a duplicate row. Found by
   checking my own output, corrected through the same locked transaction, and the bundle rows now name every
   module and structure group they cover. Final state verified: 339 rows, 278 modules, zero duplicates.
2. **I published "21 of 56 live modules are unrated" from memory.** Recomputed against the disk it is **13**,
   and the 13 are worth naming because three of them are the ones this map leans on hardest
   (`grounded_semantic_graph`, `graded_competition`, `situation_reader`). Corrected in its own commit.
3. **The first version of the optimisation probe asserted that two reads of one document are identical.**
   They are not — the reader is plastic. The assertion failed, and the fix was to add the control rather than
   to weaken the assertion. **That failure produced the pass's second-best finding.**
4. **The brief's "~70 parts" and ORGAN_MAP's "155 files" are both wrong on disk (278).** I did not adopt
   either; §3 of the map lists every place a document disagrees with the disk, with the disk winning.

---

## THE THING I WOULD TELL THE NEXT SOLVER

**Per-module cost hides cross-organ cost, and it hid the biggest fact in the system.** The affect dimension
is 0.1% of the per-module cost table. It is also, through one call, **61% of the read**. Any future profile
here must report cumulative time by call chain as well as self time by module, or it will rank the wrong
things. That is why the map's §6.2 exists.

---

## SUBMISSION PROMPT (for the strategy session)

```
pri 142 -- the_structure_map_every_organ_to_the_brain_structure_it_stands_in_for_the_computation_it_
performs_the_organs_that_perform_the_same_computation_and_the_structures_each_task_uses_and_should_use
-- SOLVED (solver scope; WIP until the owner marks DONE).

THE MAP: notes/STRUCTURE_MAP_2026-09-16.md. 278 hdlab modules (not ~70), ALL MAPPED, 21 brain
structures + 2 honest non-brain buckets. Registry: brain_structure + fidelity_basis + computation on
all 339 rows, written only through tools/capability_registry_audit.py's locked transaction (75
modules that had no row now have one). ORGAN_MAP.md regrouped by structure in a new section 3b with
the task view kept unchanged. BRAIN_FOUNDATIONAL_AUDIT.md has a section 2b entry.
NO hdlab/ OR tools/ FILE WAS WRITTEN -- witness: git diff --stat 9056ad7bb~1..HEAD -- hdlab tools,
EMPTY.

THE FIVE NUMBERS TO CARRY FORWARD:
1. 60.6% OF A READ IS ONE OPERATION -- grounded_semantic_graph._ppr, 672 runs, inside the harm/help
   judgement of every event. A per-read memo removes 28-39% of the whole read and is BYTE-IDENTICAL
   on the document where the reader was stable. This is the top of the ranked list and it is NOT a
   consolidation; it wants its own brief (text in STRUCTURE_MAP section 7.1).
2. THE SELECTION GROUP IS 28 ORGANS, ONE EQUATION, FIVE PRIVATE IMPLEMENTATIONS, 16.8% of read time
   -> pri 143. Two members set their weights BY HAND where the reference member learns them from
   counting, and space_reader's ground selection is not a competition at all (a first-match linear
   scan). Note: pri 140 landed a PROPOSED diff for one of the two hand-set members mid-pass; hdlab/
   is unchanged, so read pri 140's SOLVED.md before assuming that row.
3. THE REGISTER GROUP IS SIX ORGANS IN THREE DATA SHAPES -> pri 144. The goal register imports NO
   register at all (traced from the AST), so a goal closes on a verb and an agent and never on a
   result state. MEASURED: 16 of 26 goals (62%) already have an agent the state register holds a
   state for; 10 (38%) cannot be joined until the one entity id space lands.
4. THE LEXICAL-READ GROUP IS ALREADY DONE (pri 127) AND IS THE MODEL CASE -- one content-addressed
   store, zero nltk on the read path. Execute 143 and 144 the same way: byte-identical per arm
   first, then the shared repair. temporal_model's 2026-09-11 consolidation is the second example.
5. THE BF AUDIT RATES 94 OF 278 MODULES. Of the 56 that execute on a live read, 13 are unrated --
   including grounded_semantic_graph (60.6% of read time), graded_competition (the engine pri 143 is
   built around) and situation_reader itself. Brief-ready text in section 7.2.

TWO FINDINGS THE BRIEF DID NOT ASK FOR:
* THE READER IS PLASTIC WITHIN A PROCESS -- two consecutive reads of one document do not agree,
  because the count organs observe while they read. Correct and brain-faithful, and it means no
  experiment may assume a repeated read is a repeated measurement.
* PER-MODULE COST HIDES CROSS-ORGAN COST. The affect dimension is 0.1% of the per-module table and
  61% of the read through one call. Future profiles here must report cumulative-by-call-chain as
  well as self-by-module.

CORRECTIONS THE MAP MAKES TO THE BRIEF AND TO THE DOCS (STRUCTURE_MAP section 3): "~70 parts" ->
278; "the registry's brain_structure exists on every row" -> it was on 59 of 264; ORGAN_MAP's "155
files" -> 278; the inferred "~90k redundant re-parses" -> the reader-level waste is a factor of ~2
(2.17 arc-scorings and 1.98 category posteriors per sentence); the inferred fourth same-computation
group does not survive reading the math (there are three, and one is finished).

THE 23 DEFAULT-ON DIMENSIONS ARE FULLY MAPPED (pri 139 had 10): 17 literal track_* + 6 further
dimension flags; each mapped to the row that scores it; FOUR have no consumer at all.

REVERIFY: the seven commands in the SOLVED.md frontmatter's `reverify` field.
```

---

# PHASE 7 (strategy, 2026-09-16)

## P7.1 — pri 146 BRIEF-READY TEXT: the spreading-activation memo (runs AHEAD of 143/144)

> **PROBLEM: sixty-one per cent of the time it takes to read a document is one graph walk, and two sibling
> functions in the same module ask it the identical question about the same word in the same sentence.**
>
> **THE CALL SITE, EXACTLY.** `hdlab/grounded_semantic_graph.py:88 _ppr(seed_idx, Tt, n, d, iters)` computes
> `r = (1−d)·p + d·Tᵀr` for `PPR_ITERS` (30) iterations over the frozen lexicon graph. It is reached only
> through `grounded_semantic_graph.py:218 _sense_ppr(wn, lemma, pos, context_words, syn2idx, T, n, tgt,
> tgt_names)`, whose seed is *every synset of every context word, minus the target lemma's own synsets*.
> Two callers reach it, **both inside `hdlab/force_dynamics_valence.py`**, and both are driven from
> `situation_reader._assign_affect` → `context_grounded_valence.score_item` → `force_dynamics_event_type`:
>   * `force_dynamics_valence.py:688 sense_posterior_in_context(verb, tokens, gov_idx)` →
>     `:707 _sense_ppr(...)` directly;
>   * `force_dynamics_valence.py:718 context_sense_sign(verb, tokens, gov_idx)` →
>     `:728 g.select_sense_blended(...)` → `grounded_semantic_graph.py:414 _sense_ppr(...)`.
>
> **THE REPEAT IS STRUCTURAL, NOT INCIDENTAL.** The two callers build their context list with
> **byte-identical code** — `[t.lower() for i, t in enumerate(tokens) if i != gov_idx and t.isalpha()]`
> (`:720`) and `[str(t).lower() for i, t in enumerate(tokens) if i != gov_idx and str(t).isalpha()]`
> (`:702`) — behind the same `< 2 content words` guard, and both pass the same `lemmatize_verb(verb)`.
> **For one (verb, tokens, gov_idx) they therefore produce the same seed set and each runs the 30 power
> iterations independently.** Measured call counts on 6 GUM TEST documents agree: `context_sense_sign` 441,
> `sense_posterior_in_context` 447, `_sense_ppr` 672 runs (the shortfall is the abstentions).
>
> **THE MEMO KEY.** `(tuple(seed_idx), n, damping, iters)` — the exact seed index tuple, not the context
> words, so a caller that legitimately seeds differently never collides. Scope: **per read**, held on the
> `SituationReader` instance, not at module level (see P7.2 — module-level plastic state is the thing this
> program is currently removing).
>
> **THE CERTIFIABLE-IDENTITY CONDITION, AND IT IS NOT OPTIONAL.** `_ppr` is a pure function of its arguments,
> so the memo is sound by construction — but the *reader around it is plastic* (P7.2), so a naive
> before/after comparison of two reads cannot certify it. The condition under which identity IS certifiable:
> read the same document twice with no memo first and require the two situation models to agree
> (`reader_is_plastic_read_to_read == False`); only then does a third, memoised read prove byte-identity.
> **Already demonstrated on `GUM_letter_marcie3`: identical situation model, 28% faster.** On
> `GUM_academic_census` the reader was not stable, the memo did not change the read beyond that plasticity,
> and the 39% there is reported as a timing, not as an equivalence. **The brief must handle the plastic
> case** — the clean way is to make the plastic state per-reader (P7.2), which makes every document
> certifiable.
>
> **THE MEASURED SIZE.** 26–40% of the walks inside ONE document are exact repeats (46 of 116; 7 of 27).
> Read time falls 15.11 s → 9.25 s and 3.18 s → 2.24 s, i.e. **28–39% of the whole read**; against the
> contention-checked honest wall clock of 44.7 s per document that is **12.5–17.4 s per document**.
> `_ppr` itself is 204.5 s of 337.4 s profiled, 184.8 s of it `scipy.sparse.csr_matvec` (20,160 products).
>
> **THE ROWS IT TOUCHES: all nine.** This is latency, not accuracy — no board row's answer changes (that is
> the point), and every board run and every solver iteration gets ~2.5x more of them per hour. The laptop's
> read time is the program's bottleneck, which is why this outranks the consolidations.
>
> **THE TWIN AND THE NO-REGRESS GATE.** (a) **No-regress is IDENTITY, not a CI:** the gate is
> byte-identical situation models on every document whose reader is stable — sentences, entities, events and
> the full (predicate, agent, patient) tuple set — and any difference is a FAIL, not a trade-off.
> (b) **The info-free twin is a POISONED memo:** return a *wrong stored vector* for a hit (e.g. the previous
> distinct result) and require the read to CHANGE; a memo that can be poisoned without changing the answer
> would prove the PPR result is not actually consumed, which would be a different and larger finding.
> (c) **A coverage control:** report hits/misses per document, because a 0% hit rate on some genre would mean
> the saving does not generalise. (d) **Cap the memo** (it is per-read, so it dies with the read; report peak
> entries so nobody ships an unbounded one).
>
> **WHAT THIS BRIEF MUST NOT DO:** change `_ppr`'s iteration count, damping, or the graph. The organ is the
> right operation (spreading activation over a content-addressed semantic store, the ATL hub read); the
> defect is that it is invoked per event rather than per distinct question.
>
> **ENTRY POINTS:** `hdlab/grounded_semantic_graph.py:88,218,414`; `hdlab/force_dynamics_valence.py:688,718`;
> `hdlab/situation_reader.py::_assign_affect`; the measurement cell
> `experiments/exp_structure_map_cost_v1.py --cache-probe` and its `data/exp_structure_map_cost_v1/cache_probe.json`.
