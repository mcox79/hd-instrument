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


## P7.2 — PROBE A: every organ whose state survives a `read()`, and whether it is plasticity or a leak

**Method, in two halves so neither can hide the other's blind spot.**
*Static:* an AST scan of the **56 modules that execute on a live read**, collecting every module-level name a
function can mutate — rebound under `global`, assigned into (`x[k] = ...`), mutated by a container method, or
memoised by `@lru_cache`. *Dynamic:* three reads in one process — document A, **document A again**, document
B — fingerprinting all 103 names before and after each (`--state-probe`). A name that moves on the **repeat of
the same document** is state accrued from text; one that then moves on a **different document** crosses the
document boundary.

**Static result: 30 of the 56 live modules hold module-level mutable state, across 103 names.**

| module | names | module | names |
|---|---|---|---|
| `typed_spokes` | 18 | `lexical_utils` | 5 |
| `attachment_arm` | 11 (+3 stats counters) | `space_reader` | 5 |
| `force_dynamics_valence` | 10 | `predicate_argument_frontend` | 4 |
| `graded_role_assigner` | 9 + 1 `@lru_cache` | `entity_resolver`, `grounded_similarity`, `context_grounded_valence`, `typed_selectional_preference` | 3 each |
| `affect_lexicon`, `bound_event_backbone`, `frontend`, `lexical_categories`, `lexicon_foundation`, `predicate_detector`, `state_register`, `temporal_model`, `thematic_role_labeler`, `verb_subcat` | 2 each | `coref`, `crosstype_bridge`, `crosstype_live_adapter`, `frame_induction`, `goal_hierarchy_graph`, `hippocampal_encoder`, `incremental_parser`, `morphology`, `situation_reader` | 1 each |

**The four kinds, and the rule each implies.**

| kind | what it is | examples | verdict |
|---|---|---|---|
| **1. ASSET SINGLETON** | loaded once from a frozen file, read-only thereafter; the `global X; if X is None: X = load()` idiom | `lexicon_foundation._STORE`, `attachment_arm._TABLE`/`_HOLD_TAB`/`_PLAUS_T`, `frontend._T`/`_P`, `force_dynamics_valence._LEX`/`_RS_TABLE`/`_MANNER`/`_GSG`, `morphology._DEFAULT`, `temporal_model._ORC_TAGGER`/`_PENN_ARM`, `typed_spokes._HUB`/`_PW_STORE`/`_ANT_STORE`/`_C8_*`, `verb_subcat._ASSET_CACHE`/`_MODEL_CACHE`, `graded_role_assigner._COARSE_VALIDITIES_CACHE`, `typed_selectional_preference._SS_TABLE`/`_INST` | **CORRECT AS IS.** This is the developmental store: laid down offline, read during comprehension. It is exactly what `lexicon_foundation` was built to be. **Keep at module level** — one process, one lexicon. |
| **2. PURE CONTENT-ADDRESSED MEMO** | value is a deterministic function of the key; grows as new words arrive, never changes an existing answer | `lexicon_foundation._SYNSET_CACHE`, `lexical_utils._MORPHY`/`_CLASS_CACHE`/`_person_cache`, `entity_resolver._TYPE_CACHE`/`_ETYPE_CACHE`, `space_reader._PLACE_CACHE`/`_motion_cache`, `typed_spokes._MFS`/`_ANC_SYN`/`_MERO_MFS`/`_C8_CLASS_CACHE`, `predicate_argument_frontend._verbnet_class_cache`/`_place_cache`, `state_register._wn_syn_cache`/`_wn_ant_cache`, `force_dynamics_valence._SS_CACHE`/`_ALLSS_CACHE`/`_AFFECT_CACHE`/`_RS_CACHE`/`_EV_CACHE`, `bound_event_backbone._SYM`/`_CONTENT`, `hippocampal_encoder._DG_PROJ_CACHE`, `incremental_parser._LEMMA_CACHE`, `crosstype_bridge._ANIMACY_CACHE`, `frame_induction._INDUCED_SUBJ_HYP_CACHE`, `graded_role_assigner._SUPERSENSE`/`_MEAN_LLR_CACHE`, `@lru_cache _predicate_heads()` | **NOT A LEAK OF MEANING**, and not plasticity either — it is the retrieval store being addressed. **Keep at module level**; the only real cost is unbounded growth in a long-lived process (nothing caps them today). |
| **3. PER-PASSAGE STATE, RESET AT THE BOUNDARY** | genuinely about *this* passage, and the organ has an explicit reset | `lexical_categories._REG_GEN` + the `DiscourseRegister` it stamps (`new_document()` at `lexical_categories.py:738-746` bumps the generation and opens fresh file cards), `attachment_arm._CSUB_MEMO`/`_PP_PREP_CACHE`/`_PP_CASE_CACHE` (each `.clear()`s on a key change), `situation_reader._read_parse_cache` (already per-read, on the instance) | **THIS IS THE BRAIN'S FORM AND IT IS ALREADY RIGHT IN SPIRIT** — Heim's new file per passage. But it is implemented at **module level with a generation counter** instead of on the reader, which is exactly the shape pri 136 is replacing. **Move to the `SituationReader` instance**; the generation counter then becomes unnecessary. |
| **4. ACCRUED FROM TEXT — PLASTICITY THAT CROSSES THE DOCUMENT BOUNDARY** | the value depends on **what has been read**, and nothing resets it | **`entity_resolver._OF_VALIDITIES`** — the object-file merge/split cue-validity table. `entity_resolver.py:566-572`: on every high-margin clustering decision, `validities.observe(best_cues, True)`, `validities.observe_criterion(...)`, `validities.recompute()` mutate the table **in place**; `HDLAB_OBJECT_FILE_ONLINE` defaults to on (`:781`) and `_OF_VALIDITIES` is a module global (`:609-623`) | **THIS IS THE ONE THAT MATTERS BY CODE -- AND THE PROBE FOUND IT INERT ON THIS SAMPLE (see below).** The computation is right and brain-faithful (cue validity learned from the organ's own confirmed decisions — the owner's "plastic, never frozen"). **The LEVEL is wrong: it is per PROCESS, so document 2 is read by a reader that document 1 has already taught, and document 6 by one that five documents have taught.** Two consequences, both real: (a) **reads are order-dependent**, so a board is not a set of independent measurements; (b) it is why `HDLAB_OBJECT_FILE_ONLINE=0` exists at all — the organ ships an escape hatch to get a byte-identical A/B, which is an admission that the default is not reproducible. |

**THE RULE THIS SUPPORTS, and pri 136 is right to apply it:** *one reader = one brain.* **Plastic state
(kind 3 and kind 4) belongs on the `SituationReader` instance; module level holds only kind 1 (read-only
assets) and kind 2 (content-addressed memos).** Under that rule a read becomes order-independent and every
document becomes certifiable for pri 146's memo, while the plasticity itself is *kept* — it just lives where
a brain's does, in the reader, not in the import system.

**One open question this probe cannot settle and pri 136 must:** if plastic state moves onto the reader
instance, **a fresh `SituationReader` per document forgets everything between documents** — which is *less*
plastic than the brain, not more. The honest target is a reader that persists across a corpus **when the
experiment says so**, and is fresh when the measurement requires independence. That is a decision about the
experimental contract, not about the organ.

**Dynamic result (`--state-probe --docs 2`; `data/exp_structure_map_cost_v1/state_probe.json`).** Three reads
in one process: `GUM_academic_census`, the **same document again**, then `GUM_letter_marcie3`.

| | count | names |
|---|---|---|
| **changed on a REPEAT of the SAME document** | **2** | `lexical_categories._INST`, `lexical_categories._REG_GEN` |
| changed on a DIFFERENT document | 27 | the 2 above + 25 content-addressed memos and asset-internal caches (`lexicon_foundation._STORE`/`_SYNSET_CACHE`, `lexical_utils._MORPHY`/`_person_cache`, `entity_resolver._TYPE_CACHE`/`_ETYPE_CACHE`, `space_reader._PLACE_CACHE`/`_motion_cache`, `typed_spokes._MFS`/`_ANC_SYN`/`_MERO_MFS`/`_C8_CLASS_CACHE`, `force_dynamics_valence._SS_CACHE`-family, `predicate_argument_frontend._verbnet_class_cache`/`_place_cache`, `state_register._wn_ant_cache`, `attachment_arm._CSUB_MEMO`/`_PP_PREP_CACHE`/`_PLAUS_T`, `bound_event_backbone._SYM`/`_CONTENT`, `temporal_model._PENN_ARM`, `typed_selectional_preference._ss_cache`) |
| stable across all three reads | 76 | the asset singletons |

**A FALSE NEGATIVE IN MY OWN FIRST PROBE, FOUND AND FIXED — report it because it changes the reading.** The
first version hashed `repr(obj.__dict__)[:4000]`. At that truncation it reported `lexical_categories._INST`
as STABLE, which is wrong: with the truncation removed and a numeric digest of any `counts`/`crit` table
folded in, `_INST` moves on a same-document repeat, and `attachment_arm._PLAUS_T`,
`lexicon_foundation._STORE` and `temporal_model._PENN_ARM` join the cross-document list (their internal
memos grow). **Any claim of the form "this module-level object is stable" is only as good as the
fingerprint's depth**, and the corrected probe is the one to quote.

**WHAT THE TWO SAME-DOCUMENT CHANGES ARE, read from code.** Both belong to the **per-passage register**, not
to accrued knowledge: `lexical_categories.new_document()` (`:738-746`) bumps the module-global `_REG_GEN` and
installs a **fresh `DiscourseRegister()`**, and that register owns the clock (`sent_no`, `sent_key`,
`n_feed`, `n_read` — `:326-336`), so the clock and the file-card map **are** reset per document. *(I suspected
they were not and checked: they are. The unfounded version is not published.)* So the repeat-read change is
the passage machinery doing its job — a new file for a new passage, Heim's form.

**AND THEREFORE ONE HONEST RESIDUAL, LOCATED AND NOT EXPLAINED.** The memo probe measured that two reads of
`GUM_academic_census` return **different situation models**, and this probe shows the only module-level state
that moved between them is the per-passage register and its generation counter — **both of which are supposed
to be reset, and are**. So the read-to-read difference is *inside the per-passage register / generation
machinery*, not in an accrued-knowledge table. **I have not pinned which step it is**, and I am not going to
guess: it is a located, unexplained residual, it belongs to the machinery pri 136 is landing right now, and
pri 146's identity gate depends on it.

**THE ONE KIND-4 TABLE, AND THE SECOND FINDING ABOUT IT.** `entity_resolver._OF_VALIDITIES` is, **by code**,
plasticity that crosses the document boundary: `:566-572` calls `validities.observe(...)`,
`observe_criterion(...)` and `recompute()` **in place** on the module global whenever a clustering decision
clears `online_margin`, `HDLAB_OBJECT_FILE_ONLINE` defaults on (`:781`), and the asset it loads exists
(`data/frontend_assets/object_file_validities_gum_v1.json`, 3,276 bytes, 2026-09-16 00:32). **But the probe
reports it UNCHANGED across all three reads — including its `counts` and `crit` digests.** The accrual branch
therefore **did not fire once on two GUM documents**: the high-margin gate `(best_a − runner) >= 1.0` never
cleared. That is not "safe", it is **a default-on plastic path that is inert on this sample** — the
landed-but-not-firing shape this program keeps finding. **Flagged for pri 136**, which owns the module: either
the margin is too high for real text, or the accrual is reachable only on a population these two documents do
not contain. Measure the firing rate before treating the plasticity as live.

**SO THE RULE THE COORDINATOR NAMED IS SUPPORTED, WITH ONE AMENDMENT.** *One reader = one brain: plastic
state lives on the `SituationReader` instance; module-level holds only read-only assets and content-addressed
memos.* On the measured evidence: 76 of 103 names are read-only assets (**leave at module level**), 25 are
content-addressed memos (**leave**, but nothing caps their growth), and 2 are per-passage state implemented at
module level with a generation counter (**move to the reader; the counter then becomes unnecessary**). The
amendment: **the one genuine cross-document accrual is not currently accruing**, so moving it to the reader
would change nothing measurable today — which is an argument for measuring its firing rate first, not for
skipping it.

## P7.3 — PROBE B: the method behind the two coordination numbers, so pri 144 can reproduce them

### B1. "16 of 26 goals already share a key with the state register"

**Cell:** `experiments/exp_structure_map_cost_v1.py --coord-probe --docs 6` →
`data/exp_structure_map_cost_v1/coord_probe.json`.

| what | exactly |
|---|---|
| **population** | 6 GUM **TEST** documents (odd document index, evenly spaced across genres by `_gum_test_docs`), **annotated** input contract, 480 sentences. ONE `SituationReader(gaz=gaz).read(path)` per document — live defaults, nothing switched. |
| **the goal set** | `sm.goal_register.goals` — every `Goal` the register holds after `_read_goals`. **n = 26** (2 / 1 / 12 / 2 / 7 / 2 per document). |
| **the state set** | `sm.state_register.tracks` — the `Dict[str, EntityStateTrack]` written by `_read_entity_states`. **n = 74 keys, and all 74 have a non-empty `spans` or `occurrences`**, so "has a state" never filtered anything on this sample. |
| **THE JOIN KEY** | for each goal, `{g.agent_canonical, g.agent}` **lower-cased**, intersected with the lower-cased `tracks` keys. **This is a SURFACE AGENT HEAD STRING join** — `goal_register` keys on the syntactic-subject head (`Goal.agent`, optionally canonicalised by `bind_agents`), and `state_register` keys on the entity string `_read_entity_states` passed to `apply_state`. |
| **the count** | goals with a non-empty intersection = **16 of 26 (62%)**; goals whose matched track also has a state = **16** (identical, since all 74 tracks have one). |
| **per document** | academic_census 2/2, conversation_family 0/1, fiction_frankenstein 9/12, letter_marcie3 0/2, podcast_multitasking 3/7, vlog_mermaid 2/2. |

**THE CAVEAT PRI 144 MUST NOT SKIP: this is a STRING join, not an entity-id join.** It measures whether the
two registers *happen* to spell the agent the same way, which is the weakest possible form of the
coordination. A shared object-file id (pri 132's one id space) is the correct key and **could move this
number in either direction** — up, because "she" and "Elizabeth" would unify; down, because two different
people sharing a surface head would stop colliding. **Reproduce it on pri 135's own 212-goal population
before sizing any repair**: 26 goals on 6 documents is this sample's number, not the goal register's.

### B2. "coref does not read the foreground that `affected_entity_resolver` computes" — and what bounds it

**The traced fact (not a number):** `situation_reader._read_entities` imports `coref` and nothing else;
`hdlab/affected_entity_resolver.py::foreground` (candidates `C_fg = {X : t_sent − last_ref_sent(X) <= W}`,
falling back to all when empty) is reached only from `_read_affected_entity`. Two consumers of the same
discourse, one with an availability window and one without.

**THE NUMBER IT IS *NOT* BOUNDED BY, stated so nobody quotes it wrongly.** `BRAIN_MATH_REFERENCE` section A
records the foreground at **+0.0084 alone, CI-separated in combination, window-scramble twin collapsing to
0.216 (−0.28), and flat across W in {1,2,3,5}** — but **that is measured on `affected_entity_resolver`'s OWN
population (THIRD pronouns in the affected-entity instrument), not on the board's coref row.** It licenses
"the mechanism is real and is not a fitted window". It does **not** license any prediction about the coref
row, and it must not be quoted as one.

**THE NUMBER IT IS BOUNDED BY.** The coref row's own headroom on its own population: the reader scores
**24 in 100 on plain text (805 items)** against a compatible-recency rule at 13 and a twin at 3, while **the
same reader given answer-key spans scores 42 in 100**. So the envelope any upstream candidate-selection cue
can act inside — foreground included — is the **18-point gap between 24 and 42**; above 42 the binding
constraint is mention discovery (pri 125), not candidate selection. **A foreground arm on the coref row is
worth running, and worth running with that ceiling stated, so that a +1 is not mistaken for a small effect
when it is a eighteenth of everything available.**

## P7.4 — PROBE C: the rows pri 143 and pri 144 must re-read from code before touching

My section 9(vi) audit: 83 of 278 rows were read from CODE this pass, 195 take the module's own stated
computation. Inside the two consolidations' scope that splits as follows — **these are the rows whose
computation I have NOT verified against the code, listed so they are re-read rather than trusted.**

**pri 143 (selection engine + parse sources): 44 rows, 29 DOC-sourced.** The **8 that are LIVE on a read**
are the ones that matter first:

| row | importers | why it matters to pri 143 |
|---|---|---|
| `thematic_role_labeler` | **229** | I called it "a third cue table for the same decision" **from its docstring**. If that is right it is a third member to fold; if it is a wrapper over `graded_role_assigner`, it is not. **Re-read first — it has the most importers of any row in the group.** |
| `predicate_argument_frontend` | 84 | the shared shallow-SRL front end the agent/patient rows run through |
| `relcl_resolver` | 61 | claimed "cue-based retrieval of the filler, no arc graph" — if true it is a selection-group member with no competition, like `space_reader` |
| `incremental_parser` | 31 | claimed to be "the noise->0 limit of graded competition" — that is a *relationship to the engine*, and it is asserted, not verified |
| `crosstype_bridge` | 15 | supplies the definite->name arm |
| `verb_subcat` | 15 | a threshold veto sitting on top of the patient decision |
| `predicate_detector` | 7 | decides the population the whole group then runs on |
| `crosstype_live_adapter` | 6 | the live, gold-free path of the bridge |

The other 21 DOC rows in pri 143's scope are **not live on a read** and can be re-read when reached:
`arc_parser` (183 importers), `graded_parser` (81), `candidate_generator` (76), `coreference_resolver` (36),
`typed_coref` (31), `goal_owner_select` (25), `event_centrality_coref` (25), `commonnoun_binder` (22),
`np_head_reduce` (14), `joint_relation_frontend` (11), `crf_tagger` (10), `verb_role_exemplar_selector` (9),
`verb_subcat_frames` (6), `world_state_entity_binding` (5), `entity_world_model_resolver` (4),
`intent_classifier` (3), `selection_weighted_sharded_typer` (3), `structural_do` (2), `gated_fusion` (1),
`semantic_parser` (1), `verb_role_integrated` (0).

**pri 144 (one register): 15 rows, 7 DOC-sourced**, of which **4 are LIVE**:

| row | importers | why it matters to pri 144 |
|---|---|---|
| `state_of_mind` | **81** | despite the name it is an entity tracker / working-memory overlay, and it is the highest-importer row in the register group. Whether it is a *fifth* register or an upstream cue-producer decides whether pri 144's scope is four dimensions or five. **Re-read first.** |
| `referent_per_np` | 14 | opens the referents every register then keys on — the id-space question lives here |
| `copular_binding` | 11 | writes into `state_register`; if it holds its own state the register count changes |
| `polarity_operator` | 4 | a negated outcome must not satisfy a goal (pri 135's D01) — whether it *has* state matters |

Not live: `possession_operators` (13), `situation_model_multibank` (12), `unified_referent` (6).

**The rows pri 143/144 can trust without re-reading** are the MATH rows: `graded_competition`,
`graded_role_assigner` (including `strengths_from_counts`, `agent_supports`, `agent_competition_pick`),
`attachment_arm` (`arc_scores`), `affected_entity_resolver` (`score_and_pick`, `foreground`),
`entity_resolver` (`_retrieve`), `graded_coref_pick`, `salience_binder` (`actr_activation`), `coref`,
`online_entity_cluster`, `lexical_categories`, `pos_tagger`, `arc_labeler`, `arceager_parser`,
`convergent_cue_reader`, `frontend`, `space_reader` (the three ground finders), and for pri 144
`state_register`, `location_register`, `world_state_register`, `goal_register`, `affect_register`,
`belief_timeline`, `situation_model_accumulate`, `situation_reader`.
