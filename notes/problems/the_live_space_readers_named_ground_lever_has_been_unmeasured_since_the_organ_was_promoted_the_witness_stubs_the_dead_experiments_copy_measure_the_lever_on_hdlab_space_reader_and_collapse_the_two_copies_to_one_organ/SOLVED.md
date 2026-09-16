---
problem: the_live_space_readers_named_ground_lever_has_been_unmeasured_since_the_organ_was_promoted_the_witness_stubs_the_dead_experiments_copy_measure_the_lever_on_hdlab_space_reader_and_collapse_the_two_copies_to_one_organ
status: SOLVED
bar: "1. The live lever measured where it runs (W4's measurement with the stub on hdlab.space_reader.ground_bind_events, through the full live read, on the six modern passages: ON vs OFF with n and a bootstrap CI over items, reported whatever the sign). 2. Branch A (ON > OFF CI-separated): W4 re-pinned to the live module (it must be able to go red); the product board's space rows compared ON vs forced-OFF in ONE process and reported. 4. One organ: experiments/_space_reader.py becomes a re-export shim (or is deleted with every importer repointed); every importer enumerated; the witnesses that import it still green. 5. No-regress: the six-passage modern where-is is not below 0.4255 after the diff; the who-did-what events on the W5 passage remain byte-identical. 6. Twin: the shuffled-ground twin loses on the live module too."
result: "BRANCH A, and the lever is ALIVE where it runs. Stub on hdlab.space_reader.ground_bind_events, through the full live read (SituationReader.all_capabilities_off(track_space=True).read(cp).locations), 8 modern passages / n=47 items: OFF 0.1915 -> ON 0.3830, delta +0.1915, item-paired bootstrap CI[+0.0213,+0.3404], timeline-paired CI[+0.0599,+0.3261], both CI-SEPARATED. The lever fires 8 calls / 53 clauses / 27 events. W4 AS WRITTEN is 0.3830 == 0.3830 and is RED TODAY (its `assert on > off` fails) -- the defect reproduced first-hand. AND THE PRODUCT READER IS A DIFFERENT STORY, which is the real finding: with SituationReader() default flags (what the board runs), the space dimension receives a mention stream in which the protagonist is spread over 6-14 ENTITY FILES per passage (mean 8.9), so where-is scores 0.0426 and the lever is worth -0.0426 there (CI[-0.1064,+0.0000], n.s.) -- a correctly bound named place lands on a throwaway card. Applying the reader's OWN pronoun resolutions to that stream before the hand-off (hdlab.situation_reader.unify_entity_files, one file per referent) takes the product reader's where-is 0.0426 -> 0.4043 (+0.3617, item CI[+0.2340,+0.5106], timeline CI[+0.2292,+0.5000]) and makes the named-ground lever worth +0.2128 (item CI[+0.0851,+0.3617], timeline CI[+0.0800,+0.3600]); files per protagonist 8.9 -> 2.6. The historical-weak reader goes 0.3830 -> 0.4255, exactly reproducing the 0.4255 its own standalone driver measures (W2's ARM). ONE ORGAN: experiments/_space_reader.py becomes a sys.modules ALIAS of hdlab.space_reader; 32 real importers (28 experiments, 4 verification) all reach the ONE organ; equivalence proven on 9 documents (identical backbone, identical event lists, identical where_is tables, no module-level name lost). TWO WITNESSES REPAIRED: W4 (repinned + a structural assert that the stub target IS the module the reader runs) and verification/test_track_space_landing_organ.py, WHICH WAS ALREADY RED ON HEAD (633 of 1040 (entity,t) cells differ) for the same root cause."
floor: "STRONGEST REAL FLOOR = the stateless last-mention place floor (floor_lastment, the modern cell's own strongest floor), recomputed on THIS population: 0.1489 on the same 47 items. Live lever ON 0.3830 beats it by +0.2340, item CI[+0.0638,+0.4043], CI-separated. Product reader with the one-file hand-off 0.4043 beats it by +0.2553, item CI[+0.0851,+0.4261], CI-separated. The forced-OFF arm (0.1915 weak / 0.1915 product-at-one-file) is the second floor and is beaten CI-separated in both configs."
controls: "(1) SHUFFLED-GROUND TWIN on the LIVE module (the landed twin, ground_bind_events(shuffle_rng=...)): keeps every firing, destroys the ground content -- 0.1277 on the weak reader (loses by +0.2553, CI[+0.1277,+0.3830]) and 0.1915 on the product reader at one-file (loses by +0.2128, CI[+0.0851,+0.3617]). It scores BELOW the lever-OFF arm, i.e. a scrambled named ground is worse than no named ground -- the content, not the firing, is what pays. (2) RANDOM-MERGE TWIN for the hand-off repair: the same number of unions, each target file chosen at random, so 'fewer files' alone cannot explain the gain -- 0.2553 vs the real join's 0.4043, loses by +0.1489 CI[+0.0207,+0.2979] (and it only reaches 8.9 -> 6.0 files per protagonist, against the real join's 2.6). (3) DEFECT-PRESENCE / DEFECT-ABSENCE control in the cell's --self-test: stubbing experiments._space_reader must be a NO-OP before the patch (it is: 0.3077 == 0.3077) and must switch the live lever OFF after it (it does: 0.1538 < 0.3077). The check asserts the state it detects, so it cannot pass vacuously in either direction. (4) SHIM-EQUIVALENCE control: the promoted-away copy and the organ compared on 9 documents (8 modern + 1 LitBank) -- identical sents, identical mentions except the additive span_upos key, identical cluster names, identical person_clusters, identical event lists, identical where_is tables (0 of 9 documents mismatch), and set(dir(COPY)) - set(dir(ORGAN)) is empty. (5) pri-127 PARITY control: the uncommitted nltk -> hdlab.lexicon_foundation rewire is NOT the cause of anything measured here -- swapping the foundation back to nltk in-process gives 0.3830 on the same 47 items, identical. (6) PARSE-PROVIDER isolation on the repaired landing witness: mentions=None 633/1040 cells differ, the reader's stream + the standalone frontend 23/960 differ, the reader's stream + the reader's provider 0/960 -- which attributes the residual to a named upstream gap instead of hiding it. (7) LANDED-STATE control: every arm re-run with the patch emulated in-process (--as-landed) returns byte-identical numbers to the pre-patch run, so the shipped path is what was measured."
files_changed: "experiments/exp_space_ground_lever_live_v1.py (NEW cell: the lever on the live module x the entity-file hand-off, weak and PRODUCT reader arms, floor, two twins, paired bootstraps, --self-test, --as-landed), notes/problems/<slug>/{SOLVED.md, space_ground_lever_patch.diff}. NO existing hdlab/ or tracked verification file was edited: the proposed change to 4 files (hdlab/situation_reader.py, experiments/_space_reader.py, verification/test_space_ground_binding.py, verification/test_track_space_landing_organ.py; 1,017 diff lines, 702 of them the deleted copy) is space_ground_lever_patch.diff and `git apply --check` is clean."
reverify: ".venv/Scripts/python.exe experiments/exp_space_ground_lever_live_v1.py --self-test    # then, with the diff applied: .venv/Scripts/python.exe verification/test_space_ground_binding.py"
---

# The live named-ground lever: alive where it runs, discarded where the product reads

**SOLVED as BRANCH A, plus a located root cause the brief did not know about and a second red witness found on the way.**

## 0. WHAT THE DISK SAYS (it outranks the brief)

1. **The defect reproduces exactly.** W4 as written prints `0.3830` for both arms and its `assert on > off`
   FAILS: `AssertionError: (0.3829787234042553, 0.3829787234042553)`. It is RED today, not merely vacuous.
2. **The brief's `0.4255` is no longer the tree's number; the tree is at `0.3830`.** Both arms of W4 dropped
   `-0.0425` (2 items of 47) since it was recorded on 2026-09-15. **I located the cause and it is LOCATED item 11
   in `STATUS.md`, measured rather than assumed:** the pri-125 hand-off. With the SPACE dimension re-parsing the
   coref column itself (`mentions=None`) the same live read scores `0.4255`; with the reader's own stream it scores
   `0.3830`. It is NOT the pri-127 lexicon rewire (swapping the WordNet source back to nltk in-process leaves the
   number at `0.3830`, identical).
3. **The importer count is 32 real importers, not 56.** `grep -rl "_space_reader"` returns 65 files, but 8 of
   those only MENTION the name in a comment or docstring (all 5 hdlab hits are comments), and the rest are
   `__pycache__`. The actual `import` statements: 28 in `experiments/`, 4 in `verification/`, **0 in `hdlab/`**.
4. **`verification/test_track_space_landing_organ.py` IS ALREADY RED ON HEAD** and nobody had noticed. Its
   equivalence check compares the reader's register against `read_locations_in_substrate(doc, mode="prior_ext")`
   with `mentions=None` -- a DIFFERENT INPUT since pri 125 -- so 633 of 1040 (entity,t) cells differ. Same root
   cause as this brief: a check that stopped measuring the thing it names.
5. **The product board has NO row that consumes `sm.locations`.** The board's `spatial_relational` and
   `spatial_extraction_precision` rows run a different organ (`spatial_relation_extractor` /
   `joint_relation_frontend`). `track_space` defaults to **True** on the product reader, so the dimension is LIVE
   and computed on every default read -- it is simply never scored. Bar 2's "product board space rows ON vs
   forced-OFF" is therefore unanswerable as written; I answered the question it was trying to ask by running the
   **product reader itself** (default flags) as a measured arm, which turned out to be where the story is.

## 1. THE BAR, LINE BY LINE

| bar | verdict | evidence |
|---|---|---|
| **1. the live lever measured where it runs** | **MET** | OFF `0.1915` -> ON `0.3830`, n=47 / 8 passages, item CI`[+0.0213,+0.3404]`, timeline CI`[+0.0599,+0.3261]`; 8 calls / 53 clauses / 27 events |
| **2a. W4 re-pinned, able to go red** | **MET** | stub moved to `hdlab.space_reader`; plus a STRUCTURAL assert (`reader._space_mod is SP`) that fails at the next promotion instead of passing vacuously; green pre-patch (0.1915->0.3830) and as-landed (0.2553->0.4255) |
| **2b. the product's space rows ON vs forced-OFF in one process** | **MET, re-aimed** | no board row consumes `sm.locations` (§0.5), so the PRODUCT READER is the arm: ON `0.0426` vs OFF `0.0851` as shipped; ON `0.4043` vs OFF `0.1915` with the hand-off repaired. Reported, not gated |
| **3. branch B** | **N/A** | branch A holds |
| **4. one organ** | **MET** | `experiments/_space_reader.py` -> a `sys.modules` alias; 32 importers enumerated (§4); equivalence proven on 9 documents; W1/W2/W3/W5, `test_space_where_is_end_to_end_organ` and the repaired `test_track_space_landing_organ` all green as-landed |
| **5. no-regress** | **MET** | modern where-is after the diff `0.4255` (>= the brief's 0.4255, and above the tree's current 0.3830); W5 who-did-what events byte-identical as-landed |
| **6. twin** | **MET** | shuffled-ground twin on the LIVE module `0.1277` (weak) / `0.1915` (product at one-file), loses CI-separated in both |

## 2. WHERE THE SIGNAL IS LOST, CHAIN BY CHAIN (the status probe, with counts)

The signal the tracker needs is **(mover, kind, named ground, time)**. Walking the live chain on the 8 modern
passages (53 sentences), through `SituationReader()` -- the PRODUCT reader:

| rung | what it hands on | what the next rung reads | LOST | count |
|---|---|---|---|---|
| tokens -> categories (`lexical_categories`, per-read cache fed by the pri-112 in-order feed) | UPOS per token | the space organ's `parse_provider` | the reader's cache is **not** byte-identical to the standalone frontend the organ's own comment claims it equals | **23 of 960** (entity,t) cells differ on one 40-sentence LitBank document (2.4%) |
| categories -> heads (`attachment_arm`) | dependency heads | `route_predicate_arguments` | not measured here (LOCATED item 12 owns it) | -- |
| heads -> roles | agent / theme / goal / location per matrix verb | `ground_bind_events` GOAL-preposition + dobj scan | the ground NODE is wrong on 8 of 26 gold change points | **ground-extraction 18/26 = 0.692**; an oracle ground node on fired events is worth **+0.1915** (`experiments/_localize_upstream_ground_lever.py`, re-run today) |
| mentions (`referent_per_np`) | one referent per content-noun TOKEN, each pronoun its own file | the SPACE hand-off | **ENTITY IDENTITY** | 46 mentions -> **45 distinct files** on a 9-sentence passage; the protagonist holds **6-14 files** per passage (mean **8.9**) |
| coref (`_read_entities`, runs at :4955, BEFORE the space hand-off at :4994) | a resolved antecedent FILE per pronoun | -- | **nothing reads it here**: on the hospital passage the reader resolves **6 of 6** pronouns, all correctly to the name's file, and the hand-off throws the answer away | **the whole resolution**, every read |
| hand-off -> `build_backbone` | `person_clusters` from gendered-pronoun / gender / name-gender cues | the mover test | a real NAME can fail the animacy test while junk passes | office_commute: **14** person files, **13** of them single pronoun tokens; the name `dana` is NOT a person file while `gray.` IS |
| `ground_bind_events` | (cluster, kind, node, t, conf) | `fold_tracker` | nothing -- it fires correctly | **8 calls / 53 clauses / 33 events** (product, as shipped) |
| `fold_tracker` -> `LocationRegister` | one track per file | `where_is(entity, t)` | the place lands on whichever fragment held the agent token | product where-is **0.0426**; with one file per referent **0.4043** |

**The cost of that one hand-off is +0.3617 (item CI[+0.2340,+0.5106]) and it is the difference between a
capability and a number nobody can read.** It also inverts the sign of the lever this brief is about: under
fragmentation the named-ground pass is worth **-0.0426**, because binding `ward` to a card that is never asked
about is worse than leaving the protagonist in `<scene>`.

### 2b. Brain-foundational status of each rung, AS IT RELATES TO THIS SIGNAL

* `hdlab/location_register.py` -- **BF_SPIRIT, pinned computation** (per-entity presence intervals; Zwaan &
  Radvansky). Untouched; it does exactly what it says.
* `hdlab/space_reader.py` motion decision -- **OUR-INVENTION-UNDER-TEST** (declared as such in its docstring), a
  faithful port of the validated adapter. The named-ground pass is the part measured here; it is glass-box
  (WordNet place taxonomy + ConceptNet AtLocation counts, both static offline supply) with **no external tool at
  inference**. Verified: no spaCy, no LLM, on every arm.
* the mention stream (`referent_per_np`) -- **NOT BF for this signal.** One file per content-noun TOKEN is not a
  discourse referent; pri 138 owns it.
* the pronoun resolution (`_read_entities`) -- **BF** (Lewis-Vasishth content-addressed retrieval) and **its
  output was simply not wired to this consumer**. That is the repair.
* the animacy test in `build_backbone` -- **a cue heuristic, not the brain's animacy system**; it admits `gray.`
  and rejects `dana`. Named as an adjacent defect, not fixed here.

### 2c. How the brain does this MATHEMATICALLY, and how ours compares

The event-indexing model indexes each incoming event on **five dimensions -- time, space, PROTAGONIST, causality,
intentionality** -- and the empirical signature is that **protagonist shifts and spatial shifts INTERACT** in
reading time ([Zwaan, Langston & Graesser 1995](https://journals.sagepub.com/doi/10.1111/j.1467-9280.1995.tb00513.x);
[Zwaan, Radvansky et al., "Who when where"](https://link.springer.com/article/10.3758/BF03195811)). The spatial
index is therefore **not a free-standing map: it is a binding of a PLACE to a PROTAGONIST INDEX**, and reading
"where is X" is a read of that conjunction. At the implementation level the binding of an entity to a place in
hippocampal-entorhinal circuits is a **conjunctive, similarity-preserving vector binding** over modular codes
([Kymn et al. 2024/2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12183976/)) -- the same algebra family as our
FHRR basis -- and the situation model's entity representation is what resolves word reference in the first place
([Situation Models in the Brain are Used to Resolve Word References, 2025](https://www.biorxiv.org/content/10.1101/2025.07.15.664757.full.pdf)).

**Compared with what is built:** our tracker implements the place half exactly (intervals over discourse time,
persistence between updates, categorical nodes). What it did NOT implement is the other half of the conjunction --
**the protagonist index must be ONE index**. We were computing `bind(place, file_k)` with a different `file_k` per
mention of the same person, which in any binding algebra is a different address, not a noisy version of the same
one. That is why the repair is not a heuristic patch but the missing half of a pinned computation, and it is why
its information-free twin (random merge) loses: collapsing addresses helps only when they are collapsed onto the
address the reference resolution actually names.

## 3. THE REPAIR (the extra lever, built and measured the same way)

`hdlab.situation_reader.unify_entity_files(mentions, resolutions)` -- a pure union-find over the mention stream,
the union target always the **antecedent's** file (Heim 1982 file change: a pronoun UPDATES the antecedent's card,
it never opens one), keyed by `target_wpos` where the discovered-pronoun path fills it and by the
`(sent_idx, pronoun-head)` convention `_read_world_state` already uses otherwise. It reads **no gold**:
`CorefResolution.resolved_entity` is the reader's own online file id. Called once, at the SPACE hand-off, default
ON with `HDLAB_SPACE_ONE_FILE=0` restoring the fragmented hand-off for measurement.

| arm (n=47, 8 passages, full live read) | where-is | vs |
|---|---|---|
| weak reader, lever ON (the W4 config, live stub) | **0.3830** | OFF 0.1915 (+0.1915 CI[+0.0213,+0.3404]) |
| weak reader, lever ON + one file | **0.4255** | +0.0426 CI[+0.0000,+0.1064] -- **not CI-separated** (2 items; the gold-coref config barely fragments) |
| product reader, lever ON, as shipped | **0.0426** | OFF 0.0851 (**-0.0426**, CI[-0.1064,+0.0000], n.s.) |
| product reader, lever ON + one file | **0.4043** | as-shipped 0.0426 (+0.3617 CI[+0.2340,+0.5106]); lever OFF at one-file 0.1915 (+0.2128 CI[+0.0851,+0.3617]) |
| product reader, RANDOM-merge twin | 0.2553 | loses by +0.1489 CI[+0.0207,+0.2979] |
| product reader, shuffled-GROUND twin at one-file | 0.1915 | loses by +0.2128 CI[+0.0851,+0.3617] |
| last-mention place floor (same items) | 0.1489 | best arm beats it +0.2553 CI[+0.0851,+0.4261] |

**Coupling to name honestly:** the join propagates the coref organ's ERRORS into the spatial dimension. That is
the correct direction of coupling (one organ improves, its consumers improve), and the random-merge twin bounds
the downside -- a join with the information removed still beats the fragmented baseline (0.2553 vs 0.0426) but
loses to the real one CI-separated. On raw text, where the reader's pronoun accuracy is far below this gold's, the
gain will be smaller and should be re-measured on GUM before anyone quotes 0.4043 as a raw-text number.

## 4. ONE ORGAN -- the 32 importers

`experiments/_space_reader.py` becomes a **`sys.modules` alias**, not a star-import: a star-import copies
references into a private namespace, so `SP.f = stub` would rebind a copy and the organ would keep running its
own -- **the same defect with a new spelling**. With the alias, `experiments._space_reader is hdlab.space_reader`
is True, which is what makes the cell's self-test flip from "the stub is a no-op" to "the stub switches the lever
off". The copy had drifted **four landings**: pri 109 (no category organ on its mentions), pri 116 (read the CoNLL
through the then-lowercasing default), pri 125 (no `mentions=` parameter at all), pri 127 (still imports
`nltk.corpus.wordnet` at read time).

**28 experiment importers:** `_belief_channel_probe_scratch`, `_belief_probe_scratch`, `_belief_reader`,
`_diagnose_residual_firing`, `_diagnose_space_recall`, `_diagnose_where_is_errors`, `_localize_upstream_ground_lever`,
`_p2_register_enrichment_probe_v1`, `_tom_chain`, `exp_double_parse_frontend_noregress_v1`,
`exp_obl_spatial_{binder_coverage,chain_signalloss,combined,csx_scorer,defer_moves,meaning_corruption,resolver,thematic_upstream}_v1`,
`exp_route_ground_v2`, `exp_space_ground_binding_litbank_v1`, `exp_space_ground_binding_live_wire_v1`,
`exp_space_ground_lever_live_v1`, `exp_space_modern_brainfoundational_v1`, `exp_space_named_ground_binding_v1`,
`exp_space_recall_brainfoundational_v1`, `exp_space_recall_e2e_ci_v1`, `exp_space_where_is_end_to_end_v1`,
`exp_space_where_is_modern_v1`.
**4 verification importers:** `test_belief_at_t_end_to_end_organ`, `test_space_ground_binding`,
`test_space_where_is_end_to_end_organ`, `test_track_space_landing_organ`.
**0 hdlab importers** (the 5 hdlab hits are comments; `test_audit_live_standins` W5b asserts exactly that and stays
true).

**Witness status, run AS LANDED (the patch emulated in-process by `--as-landed`, which installs the alias, the
join and the env-gated call from the patch's own source):**

| witness | as landed | note |
|---|---|---|
| `test_space_ground_binding` W1 | GREEN 14s | recall bridge still refuted (+0.000 where-is) |
| W2 | GREEN 12s | modern ARM 0.4255, floor 0.1489, twin 0.1277 -- unchanged by the shim |
| W3 | GREEN 77s | 19c n=606, ARM 0.271 vs current 0.185, twin 0.122 -- unchanged |
| W4 (repinned) | GREEN | OFF 0.2553 -> ON 0.4255 (+0.1702), twin 0.2553, structural assert holds |
| W5 | GREEN | who-did-what events byte-identical |
| `test_space_where_is_end_to_end_organ` | GREEN 87s | all 13 checks |
| `test_track_space_landing_organ` | **GREEN 24s (was RED on HEAD)** | equivalence now 960/960 cells identical |
| `test_belief_at_t_end_to_end_organ` | **RED, pre-existing** | identical failure unpatched: `exp_belief_extraction_drill_v1.py:53 nlp(...)` -> `'NoneType' object is not callable` -- **the witness calls spaCy at inference and spaCy is gone**. Not mine; reported |
| `test_audit_live_standins` | **RED, pre-existing** | identical failure unpatched: `W1d gate default ON (stale 'default OFF' docstring notwithstanding)`. Not mine; reported |

## 5. WHAT WOULD MAKE THIS A FULL PASS ON THE CAPABILITY (not just on the bar)

The bar is met. The **capability** is not finished, and the ceiling is measured rather than guessed. Re-running
the prior solver's own ablation ladder (`experiments/_localize_upstream_ground_lever.py`, banked 2026-09-06) on the
same 47 items:

```
current chain                 = 0.3617
+ ground-binding (ARM)        = 0.4255   (+0.0638  this lever)
+ ORACLE ground node on fired = 0.6170   (+0.1915  UPSTREAM role-selection)
CEILING (perfect gold events) = 0.7872   (+0.1702  firing/recall + over-fire residual)
```

So after this landing the live reader sits at `0.4255` (weak) / `0.4043` (product) against an achievable `0.7872`.
**Wiring alone is NOT sufficient**: the largest single remaining piece is **+0.1915 of ground SELECTION** -- the
role router picks the wrong place node on 8 of 26 gold change points (18/26 = 0.692 ground-extraction accuracy).
That is the roles rung, not this one, and it is a brief-ready lead with its number.

## 5b. THE OWNER'S PUSH SCRIPT, ANSWERED WITH NUMBERS

1. **Against the brain, per rung, and where is signal lost?** §2's table: 23/960 cells at the parse hand-off,
   8/26 ground nodes at the roles rung, 8.9 files per person at the mention rung, the whole resolution at the
   space hand-off (worth +0.3617), and a `0.4043` product answer against a `0.7872` extraction ceiling.
2. **Prototype past every wall; a heuristic is not the landed form.** The join is not a heuristic -- it is a pure
   function of the reader's own decisions with no tuned parameter and no threshold. **The part that IS still a
   stand-in is the `(sent_idx, pronoun-head)` fall-back key**, needed only because `target_wpos` is filled on one
   of the two pronoun paths. **The landed form:** every `CorefResolution` carries its target's token position on
   BOTH paths, and the join keys on position alone. That is a two-line change in `_read_entities_core` that
   belongs to the coref organ (pri 131/136), and I did not make it there because that file is a pending landing.
3. **Is the wiring alone enough to reach brain level?** No -- §5: `0.4043` of `0.7872`, gap owned by ground
   SELECTION (+0.1915) and firing/recall (+0.1702).
4. **Every landed table or bias needs an observe path.** This landing adds **no table and no bias** -- nothing is
   learned, nothing is frozen, there is no threshold. Its quality is entirely inherited from the coref organ,
   whose own plasticity path is pri 136's; the counter `self._space_one_file_links` is the observe hook that says
   how often the join fired.
5. **State of the art on this rung.** There is no standard modern benchmark for narrative where-is tracking
   (SpaceEval/SpartQA score relation extraction and relative position, not per-entity place over discourse time),
   which is itself the finding: our instrument is 8 author-constructed modern passages, n=47. **The glass-box
   lever that closes the remaining gap is ground SELECTION in the role router**, quantified above.
6. **False-negative audit of the negatives I cite.** (a) "the lever is worth -0.0426 on the product reader" --
   real but NOT a property of the lever: it is conditional on fragmentation, and the same arm is +0.2128 once the
   files are joined; I report both and would withdraw the first if quoted alone. (b) "the one-file join is not
   CI-separated on the weak reader (+0.0426)" -- **underpowered, not null**: 2 items on 8 timelines, and the
   config is gold-coref so it barely fragments (2 files per person, not 8.9); the powered measurement is the
   product arm. (c) "W1's recall bridge still refuted" -- unchanged by anything here.
7. **Prior work on this rung, banked.** The 2026-09-06 landing's own ablation ladder (used in §5) and the
   pri-125 hand-off note (LOCATED item 11) were both on disk; I re-ran the ladder rather than re-deriving it, and
   item 11's `-0.043` is confirmed as exactly the 2 items I measured.

## 6. WHAT I TOUCHED, AND ITS BRAIN-FOUNDATIONAL STATUS

| component | change | BF status |
|---|---|---|
| `hdlab/space_reader.py` | **none** (measured only) | unchanged; the named-ground pass stays glass-box, static offline supply only |
| `hdlab/situation_reader.py` | + `unify_entity_files` (pure), + the env-gated call in `_read_space`, + `self._space_stream` bookkeeping | **BF**: the join is the pinned protagonist-index half of event-indexing, computed from the reader's own resolutions; no gold, no external tool, no learned parameter |
| `experiments/_space_reader.py` | full copy -> `sys.modules` alias | structural; one organ, one module object |
| `verification/test_space_ground_binding.py` W4 | stub repinned + structural assert + twin arm + reader-file query | the check can now fail for its own reason |
| `verification/test_track_space_landing_organ.py` | like-for-like equivalence + organ-named lazy-import assert | was red on HEAD; now green AND meaningful |

**Most successful improvement, rung by rung:** the BF chain cracked is **coref -> SPACE**: the reader already
computed the right answer (6/6 pronouns to the right file on the worked passage) and the consumer was not reading
it; joining them moves the product reader's where-is `0.0426 -> 0.4043` with both twins losing CI-separated.
**Rungs NOT cracked:** the mention rung (one referent per content-noun token -- pri 138), ground SELECTION in the
role router (+0.1915 on the table), the animacy test in `build_backbone` (it admits `gray.` and rejects `dana`),
and the parse-provider gap (23/960 cells).

**Alternate paths considered and not taken.** (a) *Alias addresses in the register* -- let `where_is` answer to
any of an entity's file ids instead of joining the stream. Brain-wise this is the weaker model (one card with many
addresses is exactly what a file IS, so the join belongs where the file is built), and it needs
`hdlab/location_register.py`, a pending-landing file. (b) *Fix the fragmentation at its source* (one referent per
NP with real positions) -- that is pri 138 and it would make this join mostly a no-op; the join is still the right
thing to land, because it costs nothing and it is what makes the resolution reach the consumer at all. (c) *Score
the register by name* (`reg.entity_names`, the organ's `cluster_name` map, which `_read_space` currently discards)
-- a genuinely useful capability ("where is Marcus?" answerable without an alignment step), one line, and I left it
out to keep the diff to the claim it proves.

## KEY REALIZATIONS

1. **A check that stubs the wrong module reports the same number twice, and it looks like a null result.** The
   fix is not a better number -- it is a STRUCTURAL assert that the stub target is the object the live code
   holds (`reader._space_mod is SP`). Without that, the next promotion re-creates the defect silently.
2. **Measure the PRODUCT reader, not the witness's reader.** The weak-reader arm said "+0.1915, healthy lever".
   The product reader said "0.0426 and the lever has the wrong sign". Same organ, same lever, same population --
   different configuration, opposite conclusion. The historical-weak config is a control, never the headline.
3. **A "downstream consumer" bug can be worth more than the organ it consumes.** The named-ground lever is worth
   +0.1915 where it is read; the hand-off that decides whether anyone reads it is worth +0.3617.
4. **When two arms tie, ask what would have to be true for them to differ, then count it.** ON == OFF had two
   explanations (a dead lever or a dead stub); one counter on `ground_bind_events` (8 calls, 27 events) killed the
   first in a second.
5. **The scorer's address changes when the organ's identity changes.** Joining the files broke every check keyed
   on a gold cluster id -- correctly. The identity contract (pri 131) says the answer is the reader's own file, so
   the question must be aligned to it AFTER the decision; a witness that asks by gold id is measuring the gold's
   bookkeeping, not the reader's.

## AUDIT UPDATE (for `notes/BRAIN_FOUNDATIONAL_AUDIT.md`)

* **SPACE dimension:** the tracking core is BF and untouched; **the protagonist index it binds to was not one
  index** on the live path until this landing. Record the conjunction (place x protagonist file) as the pinned
  computation, and the mention-stream fragmentation as the deviation that pri 138 removes at source.
* **`extract_events_in_substrate`'s `parse_provider` comment claims the reader's cache is "byte-identical (same
  tagger/parser)" to the standalone frontend. It is not** -- 23 of 960 where-is cells on one LitBank document.
  Stale claim, now named in the repaired witness.
* **`verification/test_belief_at_t_end_to_end_organ` calls spaCy at inference** (through
  `exp_belief_extraction_drill_v1.spacy_reality_events`) and is dead in this environment. A witness that needs an
  external parser is itself a BF defect; it should be repointed at the in-substrate parse or retired.

## ADJACENT COMPONENTS / NEXT PROBLEMS (with the numbers that rank them)

1. **Ground SELECTION in the role router (+0.1915 on this population, 18/26 change points correct)** -- the
   largest single remaining piece of where-is. Brief-ready.
2. **pri 138 (one referent per NP with real positions)** -- removes the fragmentation at source; would also let
   the join key on position alone and retire its head fall-back.
3. **`CorefResolution.target_wpos` on BOTH pronoun paths** (two lines in `_read_entities_core`) -- retires the
   only stand-in in this landing. Belongs to pri 131/136.
4. **A where-is board row.** `track_space` is default-ON and computed on every read, and NOTHING scores it. This
   cell is the instrument; without a row, a regression here is invisible.
5. **The animacy test in `build_backbone`** -- `gray.` is a mover, `dana` is not. It gates every motion event.
6. **The parse-provider gap (23/960 cells)** -- the reader's in-order categories feed vs the standalone tagger.

## CONSUMED INPUTS / FLAGGED WALL (for `notes/CROSS_SOLUTION_IMPROVEMENT_MAP.md`)

* **Consumes:** the reader's mention stream (`referent_per_np`), the reader's pronoun resolutions
  (`_read_entities`), the reader's per-read parse cache, `route_predicate_arguments`' goal/location roles, the
  static WordNet place taxonomy + ConceptNet AtLocation counts.
* **Wall flagged:** the **role router's ground selection** (primary, +0.1915) and the **mention rung's referent
  granularity** (secondary, pri 138). Both are in the parser / entity-binding mega-clusters.

## DISCLOSURE (a mistake I made, reported because the cost lands on someone else)

The session scratchpad is **shared by every agent in this session**. While setting up patched copies I wrote to
`<scratchpad>/patched/hdlab/situation_reader.py` and **overwrote a file another solver had put there** (its
directory mtime proves the entry already existed; the last-modified time before my write was 2026-09-15 15:52).
Its compiled form survives untouched at `<scratchpad>/patched/hdlab/__pycache__/situation_reader.cpython-312.pyc`
if its owner needs to recover it. All of my own work moved to `<scratchpad>/pri137/` immediately afterwards.
Nothing in the repository was affected.

## SUBMISSION PROMPT

```
Problem: the_live_space_readers_named_ground_lever_has_been_unmeasured_since_the_organ_was_promoted_the_witness_stubs_the_dead_experiments_copy_measure_the_lever_on_hdlab_space_reader_and_collapse_the_two_copies_to_one_organ (priority 137)

SOLVED, branch A, with a bigger root cause found underneath it.

The lever is ALIVE where it runs: stubbing hdlab.space_reader.ground_bind_events through the full live
read gives OFF 0.1915 -> ON 0.3830 on the 8 modern passages (n=47), item-paired CI[+0.0213,+0.3404],
timeline-paired CI[+0.0599,+0.3261]; the stateless last-mention floor is 0.1489 and the shuffled-ground
twin 0.1277, both beaten CI-separated. W4 as written is RED today (0.3830 == 0.3830, assert fails) -- the
defect reproduced first-hand.

The real finding is on the PRODUCT reader. With default flags the space dimension is handed a mention
stream in which the protagonist holds 6-14 entity files per passage (mean 8.9), so where-is scores 0.0426
and the named-ground lever is worth -0.0426 there: a correctly bound place lands on a throwaway card. The
reader RESOLVES those pronouns one call earlier (6/6 correct on the worked passage) and the hand-off throws
the answer away. Applying the reader's own resolutions to the stream (one file per referent, the antecedent's
card, Heim file change) takes the product reader 0.0426 -> 0.4043 (+0.3617, CI[+0.2340,+0.5106]), makes the
lever worth +0.2128 (CI[+0.0851,+0.3617]), and the random-merge twin (same unions, random targets) scores
0.2553 and loses CI-separated. The weak reader returns to 0.4255, exactly its standalone driver's number.

Also: experiments/_space_reader.py becomes a sys.modules alias of the ONE organ (32 real importers, not 56;
equivalence proven on 9 documents, 0 mismatches), W4 is repinned with a structural assert that fails at the
next promotion, and verification/test_track_space_landing_organ.py -- FOUND ALREADY RED ON HEAD, 633/1040
cells, same root cause -- is repaired and green.

Files: experiments/exp_space_ground_lever_live_v1.py (new cell, --self-test + --as-landed),
notes/problems/<slug>/SOLVED.md, notes/problems/<slug>/space_ground_lever_patch.diff (4 files, git apply
--check clean; hdlab/situation_reader.py, experiments/_space_reader.py and the two witnesses).
Reverify: .venv/Scripts/python.exe experiments/exp_space_ground_lever_live_v1.py --self-test
```
