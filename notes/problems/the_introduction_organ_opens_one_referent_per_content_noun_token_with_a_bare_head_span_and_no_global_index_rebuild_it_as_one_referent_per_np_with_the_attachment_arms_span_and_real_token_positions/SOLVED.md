---
problem: the_introduction_organ_opens_one_referent_per_content_noun_token_with_a_bare_head_span_and_no_global_index_rebuild_it_as_one_referent_per_np_with_the_attachment_arms_span_and_real_token_positions
status: PARTIAL
bar: "One referent per NP with real positions from the reader's own parse; the entity partition up CI-separated on 28 GUM test documents against the shipped per-token stream with the random-boundary twin losing CI-separated; the three joins moved (determiner readable, same-gold-mention cross-file pairs down, the crosstype bridge's _can_build accepting the reader's mentions); the pronoun row not down CI-separated on either scorer; every consumer of the stream enumerated and measured; a landing witness. PLUS the three bars strategy added at the pri 136 landing: the entity-set row at or above same-head-string identity 0.738 on the same 874 items; occ_appraisal back to >= 0.90 with the competition ON; the goal register naming a file by its proper name when it holds one."
result: "IN PROGRESS -- see section 1."
floor: "IN PROGRESS."
controls: "IN PROGRESS."
files_changed: "experiments/exp_np_span_introduction_v1.py (NEW cell). verification/test_referent_per_np_span_landing.py (NEW witness). notes/problems/<slug>/np_span_patch.diff (PROPOSED, NOT applied -- hdlab/referent_per_np.py, hdlab/situation_reader.py, hdlab/entity_resolver.py, hdlab/goal_register.py). data/exp_np_span_introduction_v1/* (metrics, logs, and the patched sources the diff is generated from). NO hdlab/ or tools/ file was written."
reverify: "IN PROGRESS."
---

# pri 138 -- one referent per NOUN PHRASE, with real token positions

> **THE TREE THIS WAS MEASURED ON.** pri 134 and pri 136 LANDED (`5617909c7`, `7e6f4c625`); pri 137 LANDED
> (`3d24f41ce`); pri 135's diffs APPLIED UNCOMMITTED in `hdlab/goal_register.py`,
> `hdlab/goal_hierarchy_graph.py`, `hdlab/situation_reader.py`; pri 140 and pri 146 in flight.
> `np_span_patch.diff` is generated against, and `git apply --check`s CLEAN on, that working tree.
> Two other jobs were running on this laptop throughout (`exp_agent_pick_reweigh_v1 --measure` and the
> product board `exp_situation_model_qa_modern_v1 --run`), so wall-clock timings here are contended and are
> not read as cost numbers.

## 1. WHAT WAS BUILT, AND WHAT IT IS MADE OF

**THE OPENING MOVE -- HOW DOES THE BRAIN DO THIS?** One perceived object, one object file (Kahneman,
Treisman & Gibbs 1992). One NOUN PHRASE, one discourse referent (Karttunen 1976's discourse referent; Heim
1982's file card) -- the card is opened by a DETERMINER PHRASE, not by a noun, and the determiner is read ON
the card (Heim's Novelty-Familiarity Condition). The phrase's head is its RIGHTMOST member in English
(Williams 1981's Right-Hand Head Rule), so a content noun lying inside a later noun's phrase is a MEMBER of
that phrase and opens no card of its own. WHERE the mention was said is part of the card.

**THE BOUNDARY IS THE READER'S OWN ORGANS, AND NOTHING IS FITTED.** The phrase is the head plus its PRE-HEAD
dependents from `hdlab/attachment_arm.py` (through `hdlab.frontend.parser`), intersected with the categories
the category organ says can be NP-internal, and CLOSED at the determiner -- the D is the phrase's outermost
layer (Abney 1991), so a second determiner opens a second card. POST-head dependents are never absorbed
(the prior `boundary_nphead` finding). Where the hard arc is missing, the attachment arm's GRADED head
belief decides at its MAP (P(inside) >= P(outside)); 0.5 is the MAP boundary, not a swept threshold.

**REUSE BY STRUCTURE -- what already computed a piece of this, and what I reused instead of rebuilding:**

| existing organ | what it already computes | reused how |
|---|---|---|
| `hdlab/attachment_arm.py` via `hdlab.frontend.parser` | the head of every token + the graded head posterior | THE boundary evidence; no second parser, no chunker |
| `situation_reader._cached_parse_heads` / `_cached_head_posterior` | the ONE shared per-read parse | served to the introduction organ through a new `_CachedTagShim.parse_heads` -- no extra pass |
| `graded_role_assigner.mention_head_wpos` (pri 134, landed) | the head's index inside a multi-token mention | THE accessor every head-index consumer now calls; I did not write a second one |
| `hdlab/np_head_reduce.py` | reduce an NP span to its head (who-did-what stage A) | kept and FED the real head index; the collapse is what it was compensating for |
| `coref.name_content_tokens` + `span_upos` | is this span a NAME, from the category organ | the file card's NAME label (bar 3) |
| `entity_resolver._definiteness` / `_np_boundary_before` (pri 136) | Heim's criterion + "a determiner opens a new nominal" | unchanged; they now read a real span instead of guessing from the token to the left |
| pri 134's `referent_per_np_span_patch.diff` | the canonical schema fields | the STARTING POINT; its arc-free chunk is this cell's `cat` arm |
| pri 136's `np_spans` prototype (inside its cell) | the arc-based grouping | the `arc` arm; promoted out of the cell and onto the organ |

**WHAT IS NEW** (and it is one function, not an organ): `np_groups` -- the Right-Hand-Head collapse that
turns the candidate content-noun tokens into one referent per phrase, plus `np_left_edge`, the boundary. No
second mention stream exists anywhere; the pronoun arm and the nominal arm still hand ONE stream to every
consumer.

## 2. THE UPSTREAM CHAIN, AND WHAT EACH RUNG HANDS DOWN

| rung | organ | hands down | BF status as the disk shows it |
|---|---|---|---|
| categories | `lexical_categories` (`HDLAB_TAG_SOURCE=counts`) | a GRADED posterior per token (`_cached_tag_posterior`) | BF_SPIRIT; graded hand-down present |
| lemma | `lexical_utils.concept_lemma` (WordNet morphy) | a point lemma | offline foundation asset; BF at the computational level |
| heads | `attachment_arm` via `frontend.parser` (`HDLAB_HEADS_SOURCE=attachment_arm`) | the in-order tree AND `P(head\|dep)` | BF_SPIRIT; graded hand-down present -- **this rung is what draws the phrase boundary** |
| roles | `graded_role_assigner` | role posteriors keyed by the ARGUMENT TOKEN | BF_SPIRIT |
| **introduction** | **`referent_per_np`** | **the mention stream** | **BF_SPIRIT -- the rung this brief rebuilds** |
| object-file competition | `entity_resolver.competition_cluster` | the file partition (ACT-R base level + log-odds cue validities, online accrual) | BF_SPIRIT; PLASTIC |
| consumers | coref pick, goal register naming, occ appraisal, crosstype bridge, space where-is | answers | mixed |

**The graded hand-down is intact from categories -> heads -> the boundary**: the boundary reads
`P(head | dep)`, not the argmax alone, which is what the brief's phase-diagram note asks for.

## 3. THE OPERATING POINT, CHOSEN ON THE TRAIN SPLIT

**What evidence should draw the phrase boundary?** Four arms, each a LIVE read of the same 6 GUM **TRAIN**
documents with only the boundary rule changed (`experiments/exp_np_span_introduction_v1.py
--boundary-sweep 6`; log `data/exp_np_span_introduction_v1/boundary6.log`). The decision metric is the
entity-set row's MARGIN OVER ITS OWN FLOOR, because that is the bar's metric.

| arm | what draws the boundary | mentions | multi-token | determiner readable | B-cubed | entity-set | its floor | margin |
|---|---|---|---|---|---|---|---|---|
| `cat` | the category run alone (pri 134's arc-free chunk) | 1,848 | 791 | 564 | **0.6741** | 0.4606 | 0.4449 | +0.0157 |
| `arc` | the attachment arm's projection alone (pri 136's prototype) | 1,901 | 948 | 550 | 0.6648 | 0.4691 | 0.4291 | +0.0400 |
| **`both`** | **the conjunction (SHIPPED DEFAULT)** | **1,917** | **740** | **533** | 0.6657 | **0.4750** | 0.4321 | **+0.0429** |
| `graded` | `both`, with the arm's GRADED head belief deciding at its MAP where the hard arc says no | 1,916 | 741 | 534 | 0.6651 | 0.4731 | 0.4337 | +0.0394 |

**Two things this says, and I am reporting the one that goes against my own design.** (1) The CONJUNCTION
wins the bar's metric, so the shipped default is the arm's arcs AND the category organ's categories -- two
organs voting, neither alone. (2) **The GRADED arm buys nothing here (+0.0394 vs +0.0429, one token absorbed
differently in 1,917):** the hard arc and the graded MAP already agree on virtually every NP-internal token,
because a determiner's head is not a close call. The graded read is kept (it costs nothing and it is the
brain-faithful form -- the boundary is a belief, not a fact) but it is NOT the shipped default and I do not
claim it as a gain. (3) `cat` has the BEST B-cubed and the WORST margin -- the category run over-absorbs
across boundaries the arcs refuse, which flatters a partition score by removing mentions while making the
merge/split decision worse. That is why the decision metric is the entity-set row and not B-cubed.

## 4. THE LOCATED FINDING THIS RUNG EXPOSES -- HEIM'S CRITERION WAS LANDED AND INERT

`entity_resolver._definiteness(span_toks, sents, sent_idx, wpos)` reads the determiner from `span_toks[0]`
and falls back to the sentence token before the mention when `sents` is supplied. **The live call site
(`situation_reader.read` -> `EntityResolver(validities=_V).cluster(role_mentions, gaz=self.gaz)`) passes NO
`sents`.** So on the shipped tree every mention answered `bare` at inference, the criterion shift was the
same constant for every decision, and Heim's Novelty-Familiarity Condition -- pri 136's own headline
mechanism -- was **landed and inert on the live read**. The teacher that built the validities DID pass
`sents`, so it learned shifts (`indefinite` +1.456, `definite` +0.177, `bare` -0.246) that the reader never
applied.

**A real span turns it on, for the first time, at inference.** That is a capability arriving, not a
regression -- but it arrives with a shift calibrated on a different signal, which is why the validities are
RE-ACCRUED here on the phrase stream with the teacher reading definiteness EXACTLY as inference reads it
(`sents=None`). This is the mechanism behind the entity-set movement reported in section 5, and it is the
kind of thing only a live A/B finds.

## 5. EVERY CONSUMER OF THE STREAM, ENUMERATED ON DISK AND DECIDED

`grep -rn "gtok_start|gtok_end|span_toks|wtok_start" --include=*.py hdlab/` returns **197 sites in 17
files** (`referent_per_np` itself excluded: 16 files, 163 sites). Each was read and placed in one of three
classes -- *wants the SPAN* (it was reading a degenerate point and now gets the real thing), *wants the
HEAD* (it read `wtok_start` as the head index and must now call `mention_head_wpos`), or *invariant*.

| # | site | what it reads | class | what this rung does |
|---|---|---|---|---|
| 1 | `crosstype_live_adapter._can_build` | `gtok_start`/`gtok_end` in range | SPAN | rejected 292/292 mentions and abstained the whole document; now accepts (witness [10e]) |
| 2 | `lexical_utils.definiteness` | `span_toks[0]` | SPAN | answered `bare` 100% of the time; now reads the determiner |
| 3 | `lexical_utils.modifiers` | `span_toks[:-1]` | SPAN | empty by construction; now carries the descriptive content |
| 4 | `coref.mention_span` | the gtok extent | SPAN | returned a point; now a real extent |
| 5 | `coref.name_content_tokens` + `span_upos` (9 organs) | the whole span | SPAN | pri 118's SPAN-level name-run cue was inert; it can now fire |
| 6 | `space_reader._cluster_covering` | `wtok_start + len(span)-1` | SPAN | covered one token; now covers the phrase (LOCATED item 11's mover defect) |
| 7 | `entity_resolver` / `online_entity_cluster` aliaser | the span, for the canonical name key | SPAN | 'Elizabeth Bennet' could never be one alias; now it is |
| 8 | `entity_resolver._definiteness` -> Heim's criterion shift | `span_toks[0]` | SPAN | **was inert at inference** (section 4); now live -- validities re-accrued |
| 9 | `entity_resolver` `np` cue distance | `wpos - f.last_wpos` | SPAN | the file now records the phrase's END, so `d` is the gap BETWEEN phrases; validities re-accrued |
| 10 | **`coref.ent_at_pos`** (Principle B's clause-mate ban) | `(si, wtok_start)` keyed | **HEAD** | **REPAIRED IN THIS DIFF** -- the ban is looked up with parse-derived ARGUMENT HEAD positions, so it would have missed on every multi-token mention; every token of the phrase now registers the same card |
| 11 | `situation_reader._nom_head_at` | `wtok_start == pos0` | HEAD | REPAIRED -- head first, then any token of the phrase, then nearest-to-head |
| 12 | `situation_reader._assign_frame_primary_roles` -> `frame_primary_role` | the argument's own token | HEAD | REPAIRED -- `mention_head_wpos` |
| 13 | `situation_reader` np-head-reduce gate (`np_head_reduce.is_np_head`) | the mention's head token | HEAD | REPAIRED -- and the gate is now largely redundant: the collapse is what it was compensating for |
| 14 | `situation_reader` structural-DO probe (`structural_do.is_bare_do`) | the patient's token index | HEAD | REPAIRED |
| 15 | `situation_reader._read_affected_entity` (`decs`, `theme_verb`) | role decisions keyed by the argument token | HEAD | REPAIRED (2 sites) |
| 16 | `graded_role_assigner` `:2580` / `:2665` | the head's index | HEAD | already repaired by pri 134's landed `mention_head_wpos` -- **and it was WRONG on every multi-token GOLD mention before that**, this rung is what makes the repair load-bearing |
| 17 | `graded_role_assigner` pre/post-verbal position cues, `situation_reader._pick_role_mentions`, clause-bound filters | `wtok_start` as a POSITION | INVARIANT | **structurally**: the phrase stops at VERB/AUX/ADP/SCONJ/CCONJ/PUNCT and only ever grows LEFT from its head, so it can never cross its clause's verb and every `< v0` / `> v0` test keeps its answer (witness [6b]) |
| 18 | `situation_reader._gold_alignment`, `referent_per_np`'s own column read | the GOLD coref column's extents | INVARIANT | reads the annotation column, which always carried real spans |
| 19 | `event_centrality_coref`, `coref_distractor_suppress`, `bundle_focus_coref`, `scene_segment`, `gender_organ`, `unified_referent`, `commonnoun_binder`, `state_of_mind.infer_nominal_gender` | `span_toks` as a surface / name test | SPAN | strictly more to read; `gender_organ` and `infer_nominal_gender` now see the modifiers ('the old **woman**') |
| 20 | **the SCORERS** -- `exp_board_rows_on_the_reader_v1.score_entity_set`, `exp_pronoun_pick_identity_contract_v1`'s maps, pri 136's `mention_partition` / `purity` | `(sent_idx, wtok_start)` as the gold key | **HEAD** | **NOT in this diff (they are experiment files) -- a NAMED HAND-OFF: every scorer that aligns a reader mention to gold must key on `mention_head_wpos(m)`, not `wtok_start`. This cell does so; the board's own row does not yet.** |

**Row 20 is the one that would silently misread the landing** and it is the reason this cell re-implements
the board's entity-set row instead of importing it: `score_entity_set` looks a mention up at
`(sent_idx, wtok_start)`, which is the phrase's first token once this lands, so the board's entity-set row
would align on determiners. The scorer repair is one line and is handed to strategy, not applied here.

## 6. A CORRECTION TO MY OWN BRIEF, MADE BEFORE CLAIMING THE NUMBER

The brief's bar 3 asks for "the crosstype bridge's `_can_build` accepting the reader's mentions (docs
reaching the detector 6/6 on pri 134's probe)". **On the tree as it now stands that is ALREADY TRUE and it is
not this rung's doing.** pri 134's LANDED `crosstype_live_adapter._mention_gtok` RECOVERS a global span from
`sent_idx + wtok_start + span_toks` when the mention carries none, so `_can_build` succeeds on the shipped
per-token stream too (measured directly here: the shipped arm builds a Doc on 4 of 4 GUM documents). I will
not claim that repair.

**What this rung actually buys the bridge is the BINDS**, and the mechanism is the one the brief names at
`crosstype_bridge.py:341`: the definite-description gate reads `m.text.lower().split()[0] in _ART`. With a
bare-head span the first token IS the head, so every definite failed the test and the gate fired on nothing.
With the phrase on the card, 'the baker' passes. Measured on the same 4 GUM documents through the live read:
**binds 0 -> 3**, with `_can_build` at 4/4 in BOTH arms.

## 7. ALTERNATE PATHS CONSIDERED (brain structure, the maths, what it would take, why not now)

| path | the brain structure + the computation | what it would take | why not now |
|---|---|---|---|
| **A joint (category, head) posterior over boundaries** | the boundary is `argmax_a P(span = [a,h] | words)`, a proper segmentation posterior rather than a product of two marginals -- what a hierarchical predictive-coding account of chunking (Friston; Dehaene 2015's nested chunk detectors) actually predicts | the attachment arm would have to expose `P(head | dep, category)` jointly instead of marginalising the category away; a new decoding pass over boundary hypotheses | the two marginals are all the substrate hands down today; the `post` arm is the honest approximation and is measured. **Filed as a lead with the number it would have to beat.** |
| **The boundary as a learned cue competition** (like every other rung) | one more arm of `graded_competition`: cue values (a determiner to the left / a PROPN run / an arc / a comma) with counted log-odds validities, the boundary an argmax of accumulated evidence | a builder accruing boundary decisions from reading (the `tools/build_*` pattern), plus a supervision signal that is not a treebank | it would make the boundary PLASTIC, which is the standing discipline; but the boundary as built is already parameter-free and the competition would need an online outcome signal the reader does not yet produce. **This is the strongest single next step** (see section 9). |
| **Post-head dependents inside the phrase** ('the baker of York' as one card) | Heim's file card is opened by the whole DP including its complements | one flag | the prior `boundary_nphead` work measured it as a LOSS and the brief forbids re-treading it; the collapse already costs gold-head alignments (section 8) and this would cost more |
| **Nested cards** (a card for 'New York' INSIDE the card for 'the New York Times') | object files nest under part-whole/containment (Treisman's object files do not, but discourse referents can -- Asher's abstract entities) | a containment relation on the file card + every consumer taught to read it | it changes the mention SCHEMA for every consumer again; the collapse's measured cost has to justify it first. **Filed with its number** (section 8). |

## 8. WHAT IS STILL RUNNING / WHAT REMAINS

Measured and recorded so far: the boundary sweep (section 3, TRAIN), the located criterion finding
(section 4), the consumer enumeration (section 5), the bridge correction (section 6), the alternate paths
(section 7), the landing witness (22/22 green on the diff compiled into the live modules). The validity
re-accrual on 24 GUM TRAIN documents, the headline TEST run (shipped / npspan / random-boundary twin) and
the three pri-136 bars are the remaining measurements; they are written into sections 9-12 as they land.

**Laptop contention is the limiting factor, not the design:** two product-board runs
(`exp_situation_model_qa_modern_v1 --run`) have been resident throughout, and a live GUM read went from
~56 s/document uncontended to ~400 s/document with three jobs resident. Every arm is one live read per
document per arm; the run sizes below are chosen against that, and the population is reported with every
number rather than assumed.

## 9. SECTIONS TO COME

(2) the measured result; (3) the signal-loss trace with counts; (4) the quality push; (5) the verdict
check; (6) alternate paths and next steps.
