---
problem: the_readers_entity_clustering_is_the_numbered_pronoun_lever_262_of_1486_files_mix_two_gold_entities_and_a_gold_entity_oracle_adds_0_1168_ci_sep_build_the_file_merge_split_decision_as_a_cue_competition_with_online_validities
status: PARTIAL
bar: "Partition quality up CI-sep on the 28 docs; the pronoun instrument up CI-sep with the fraction of the oracle gap closed stated; validities accrued with an observe path (twin at floor); consumers not down (or repaired with items); the board's coref row (after the answer-key fix) not down -- OR a numbered located negative naming the cue that cannot be had without new knowledge."
result: "PENDING"
floor: "PENDING"
controls: "PENDING"
files_changed: "PENDING"
reverify: "PENDING"
---

# PARTIAL -- the object-file competition is built and the partition is CI-separated better; the brief's own premise is corrected by the decomposition, and the residual pronoun loss is located in the pick's antecedent READOUT, not in the files

## 0. THE OPENING MOVE -- how the brain does THIS (PINNED vs OUR-INVENTION)

A new mention either **updates an open file or opens a new one**: Heim (1982) file-change semantics'
Novelty-Familiarity Condition and Kahneman & Treisman (1992) object files. The decision is a **graded match**
of the mention's features against the open files, and retrieval is content-addressable and cue-based
(Lewis & Vasishth 2005). Written out, the organ is

```
A(f) = B_i(f)  +  SUM_c  w_c[ value_c(mention, f) ]
update argmax A   if   max A  >=  tau + lambda(definiteness)      else OPEN A NEW FILE
```

| piece | status |
|---|---|
| a mention updates a FILE or opens one; the file accrues features over its mentions | **PINNED** (Heim; Kahneman-Treisman) |
| B_i = ACT-R base-level (recency x frequency x role prominence) | **PINNED** (Anderson & Schooler 1991) -- **imported**, `salience_binder.actr_activation`, never re-implemented |
| the cues are SUMMED in parallel, not applied as a filter | **PINNED** (Lewis & Vasishth 2005) -- this is the single shared mathematical gap `notes/BRAIN_FOUNDATIONAL_AUDIT.md` names for this organ |
| the additive weight of a cue value is the LOG-LIKELIHOOD RATIO `log P(v\|same) - log P(v\|diff)` | **PINNED IN FORM** (Anderson & Milson 1989 rational analysis: the associative strength S_ji is the log posterior odds) |
| those probabilities are COUNTS, accrued from experience (cue validity = availability x reliability) | **PINNED** (MacWhinney & Bates Competition Model; the pri 108 / pri 117 template) |
| the mismatch PENALTY (L&V `-P * mismatch`) | **LEARNED here rather than hand-set**: a conflicting cue value simply gets a negative log-odds (`phi conflict -0.57`, `name clash -0.47`, `head mismatch -0.57`) |
| opening a new file when nothing clears a threshold = a retrieval FAILURE is the novelty signal | **PINNED** (ACT-R retrieval threshold; Norman & O'Reilly 2003 pattern separation vs completion) |
| definiteness shifts the CRITERION, it is not evidence about which file | **PINNED** (Heim's condition is a constraint on the UPDATE) -- and getting this wrong was a measured defect in my first build (§7) |
| `tau`, the accrual margin, the cue inventory | **OUR-INVENTION** -- swept, never adopted |

**What the shipped organ does instead.** `EntityResolver.cluster` HARD-FILTERS (phi-compatible AND exact
head-lemma identity) and then takes the argmax with `policy='argmax'` -- **always merge**. It therefore
cannot hold two same-head referents apart, cannot use type / predication / definiteness evidence at all,
and has no threshold at which it opens a new file. Heim's second indefinite is merged by construction
(witness W1: the shipped organ files "a doctor / a doctor / the doctor" as ONE file at every setting,
because it has no setting).

## 1. THE BRIEF'S PREMISE, RE-MEASURED -- and it points at the OTHER half

pri 131's oracle probe reproduced first-hand on its own cell (12 GUM test documents, 334 fixed questions,
text only, abstention = wrong): head-string **0.3263** == the reader's own files **0.3263** (delta exactly
0.0000, CI[0,0]); the GOLD-entity oracle **0.4431**, **+0.1168 CI[+0.0241,+0.2614] CI-separated**.

⚠️ **One caveat that did not travel with that number, found here:** `row_identity_basis` runs inside
`arm("entity_pb")`, i.e. with **Principle B ON** -- a configuration that ships **default-OFF**. With the
exclusion off (what actually ships) the reader's files score **0.3144** and the oracle **0.4281**; the
headroom is **+0.1138 CI[+0.0175,+0.2686]**, CI-separated either way. Every number below is reported in
the shipping configuration, with the Principle-B column beside it.

**THE DECOMPOSITION -- the partition ALGEBRA, which is what says where the +0.1138 actually lives.**
Same 12 documents, same 334 questions, one code path; the `shipped` arm is asserted equal to the LIVE
organ item-for-item before any contrast is reported.

| arm (what it fixes) | span | span, Principle B ON | B-cubed F1 | B3 P | B3 R | vs shipped (span) |
|---|---|---|---|---|---|---|
| **shipped** (the live organ) | 0.3144 | 0.3263 | 0.5611 | 0.7983 | 0.4326 | -- |
| **refine = R ∧ G** -- every OVER-MERGE fixed, splits kept | 0.3263 | 0.3383 | 0.6040 | **1.0000** | 0.4326 | **+0.0120 CI[-0.0073,+0.0380] NOT separated** |
| **coarsen = R ∨ G** -- every UNDER-SPLIT fixed, merges kept | 0.3772 | 0.3802 | 0.6565 | 0.4887 | **1.0000** | **+0.0629 CI[+0.0097,+0.1338] CI-SEPARATED** |
| **oracle = G** | 0.4281 | 0.4431 | 1.0000 | 1.0000 | 1.0000 | **+0.1138 CI[+0.0175,+0.2686] CI-SEPARATED** |

🔑 **The brief is named after the over-merge half ("262 of 1486 files mix two gold entities"), and the
over-merge half is the SMALL one.** Fixing every wrong merge and nothing else is **+0.0120 and not
separated**; fixing every missed merge and nothing else is **+0.0629 and separated** -- **55% of the whole
oracle gain**, with the remaining ~34% only reachable by fixing both. The reader's files are **too MANY**,
not too few: 643 files for 293 gold entities on these documents, B-cubed **precision 0.798 but recall
0.433**. 121 files are impure; **175 of 293 gold entities are split**.

## 2. WHY THE SPLIT HALF IS SO LARGE -- and it is mostly not an identity failure at all

**Counted, not narrated.** Of the 3,689 mention pairs that belong to one gold entity and sit in different
reader files, **1,331 (36%) lie INSIDE ONE GOLD MENTION SPAN**; **156 of the 175 split gold entities** have
at least one such pair and **48 are purely that**. The worked example, from `GUM_academic_census`:

> gold entity = *"tenure track university faculty"* → the reader opens **four** files: `tenure`, `track`,
> `university`, `faculty`. Also observed: *"the scientific workforce"* → `scientific` + `workforce`;
> *"the full census"* → `full` + `censu`.

The introduction organ (`referent_per_np`) opens a discourse referent per **content-noun TOKEN** and stores
`span_toks=[head]` -- one token per mention. A complex nominal therefore arrives as N object files where the
discourse has one object. **This is not a missing identity cue; it is a mention-segmentation defect one rung
up**, and pri 118's SOLVED already named it ("keeping the NP span is the next rung"). This session numbers it.

**CUE REACH -- can any cue in the brief's list even link what the reader split?** (the 175 split gold
entities; a cue "reaches" an entity if it fires on at least one of its differently-filed pairs)

| cue | without a nominal-run cue | with it |
|---|---|---|
| **NO CUE REACHES IT** | **122 (69.7%)** | **21 (12.0%)** |
| nominal run (adjacent content heads) | -- | **142 (81.1%)** |
| head is-a (WordNet type) | 26 (14.9%) | 26 |
| same head lemma (phi-blocked) | 26 (14.9%) | 26 |
| entity-type spoke (name ↔ common) | 16 (9.1%) | 16 |
| predication (the crosstype bridge) | **0** | **0** |

## 3. THREE DEAD JOINS, ALL THE SAME ONE-TOKEN-SPAN DEFECT (landed ≠ live, measured)

1. **`merge_crosstype_bridge` returns ZERO binds on 12 of 12 GUM documents.** `_can_build` requires a
   GLOBAL token index on every non-pronoun mention, and since pri 125 made `referent_per_np` the reader's
   mention source those indices are **-1 on every mention**, so the adapter abstains on every read.
   **DE-LEAK PART 2 -- the organ that recovered the +0.0838 CI-sep experiencer gain -- is dead on the live
   path.** The index is fully determined by what the mention already carries
   (`gtok = sum(len(s) for s in sents[:sent_idx]) + wtok_start`); the diff supplies it.
2. **Even with the index, the bridge's own anaphoricity test fails on every definite:** it reads
   `mention.text.split()[0] in {the, a, an, this, that, ...}` and the mention text **is the bare head**.
   The diff reads the determiner from the reader's own preceding token and puts it back.
3. **With BOTH repaired the bridge yields 1 bind on 12 documents** -- through the reader's own
   (pri 129, brain-foundational) relations, because the fine non-argument relations its name-link paths key
   on (`appos`/`flat`/`compound`) read `dep` since the supervised labeler retired. **That is pri 134's rung,
   and this is its number on this population.** The two repairs are shipped anyway: they are correct, they
   cost nothing, and they are the precondition for pri 134 paying anything here.
4. **The same defect makes Heim's Novelty-Familiarity Condition unreadable:** on 24 GUM TRAIN documents
   **every mention reads `bare`** (definite 0, indefinite 0), because the determiner is not on the mention.
   Reading **one token to the left** in the reader's own sentence recovers it -- and the criterion then
   falls out of the counts with the **PINNED sign and the PINNED order**: an indefinite makes opening a new
   file **+1.46** log-odds more likely, a definite **+0.18**, a bare nominal **-0.25**.

## 4. WHAT WAS BUILT

**`competition_cluster`** (the organ; in the cell, ported verbatim by the diff into
`hdlab/entity_resolver.py`), with **`Validities`** (counts → log-odds), **`file_cues`** (the cue reader) and
**`observe_file_decision`** (the online accrual). Six PAIRWISE cues, each with a mutually exclusive and
jointly exhaustive value space, plus one MENTION-level criterion:

**The learned table -- 28,559 mention×file pairs counted on 24 GUM TRAIN documents** (the TEST split
`[1::2]` is never read by the teacher):

```
name         canon_match +2.82   surf_match +2.48   clash -0.47   na -0.53
head         lemma_match +2.50   isa +0.16          mismatch -0.57   no_head +2.84
etype        licensed +0.91      blocked -0.32      na +0.02
predication  linked +2.84        na -0.00
phi          agree +0.12         conflict -0.57     unknown +0.13
cb           prev_cb +0.84       no -0.10
np           gap1_nom +6.23  gap1_x +5.59  gap2_nom +4.15  gap2_x +4.96  same_sent_far +1.44  other_sent -0.98
NOVELTY(tau) indefinite +1.46    definite +0.18     bare -0.25            (a CRITERION shift, not evidence)
```

Every one of the brief's cues is in the competition, including the two the brief said were missing: the
**entity-type spoke** (`licensed +0.91 / blocked -0.32` -- pri 125's `she → youtube` flood is exactly the
`blocked` value, witness W7) and the **predication link** from the crosstype bridge, routed in as a CUE
rather than as an override.

**The observe path.** `observe_file_decision(validities, cues, same)` accrues one confirmed merge/split
outcome and recomputes the strengths, which are a pure function of the counts -- so nothing is frozen.
`competition_cluster(..., online=True)` feeds the reader's own **high-margin** decisions back in as they are
made (self-supervised; no gold on any path -- witness W5 asserts the decision source contains no gold field
name). The asset is re-buildable in one command from GUM TRAIN.

## 5. THE MEASUREMENT -- 12 GUM TEST documents, 334 fixed questions, text only, abstention = wrong

Both arms in ONE process, the replay asserted equal to the live organ item-for-item.
`tau = 0` was chosen on the **TRAIN** split (24 documents) and is reported here on TEST.

| arm | pronoun span | vs shipped | B-cubed F1 | P | R | ΔB3 vs shipped (paired bootstrap over documents) |
|---|---|---|---|---|---|---|
| **shipped** | **0.3144** | -- | **0.5611** | 0.798 | 0.433 | -- |
| **the competition (tau 0)** | 0.3024 | -0.0120 CI[-0.1297,+0.0901] **not separated** | **0.6172** | 0.751 | **0.524** | **+0.0560 CI[+0.0077,+0.1086] CI-SEPARATED** |
| the competition, no sentence context | 0.2335 | -0.0808 CI[-0.1793,+0.0000] n.s. | 0.6291 | 0.632 | 0.626 | +0.0680 CI[+0.0160,+0.1238] CI-sep |
| the competition on the crude lemma key | 0.2605 | -0.0539 n.s. | 0.6175 | 0.756 | 0.522 | +0.0563 CI[+0.0073,+0.1090] CI-sep |
| **INFORMATION-FREE TWIN** (validities permuted) | 0.2126 | -0.1018 n.s. | **0.1864** | 0.105 | 0.848 | **-0.3748 CI[-0.4559,-0.2927] CI-separated BELOW** |
| the competition at tau +2 | 0.2665 | -0.0479 n.s. | 0.5696 | 0.915 | 0.413 | +0.0084 CI[-0.0421,+0.0616] n.s. |

- **Partition quality is up CI-separated** (+0.0560 B3), and it is up where the decomposition said the
  prize is: **recall 0.433 → 0.524**, at essentially unchanged impurity.
- **The information-free twin LOSES by a mile** (-0.3748 below the shipped organ, i.e. -0.43 below the
  competition). The validities are load-bearing, not "any structured pass helps".
- **The pronoun instrument is NOT CI-separated down** (-0.0120) -- and it is not up either.
- **The brain-foundational lemma key is a null here** (+0.0003 B3): an honest negative against my own
  expectation. The crude `head_lemma` regex's over-strip (`census → censu`) is consistent within a document,
  so it costs the *partition* nothing; 0 of the 3,689 split pairs are linked by `concept_lemma` and missed
  by `head_lemma`. (Its false-merge bug -- a non-alphabetic head collapsing to `""` -- is still real and the
  diff keeps the brain-foundational key; it just does not pay on this population.)

## 6. THE RESIDUAL IS THE PICK'S ANTECEDENT READOUT, NOT THE FILES -- proven with an identity control

The pronoun row did not move, so I itemised it: of 334 questions the competition **wins 22 and loses 26**;
the losses concentrate on items like `his → put`, `he → top`, `its → unambiguous`. The mechanism is not the
clustering. `graded_pronoun_resolve` answers with `last_nom[k]` -- **the chosen file's MOST RECENT
non-pronoun mention**. That is right for a head-bucket (every mention in it is the same head word) and wrong
for a FILE: the introduction organ opens a referent on **122 VERB-headed and 30 ADV-headed tokens per 12
documents**, so a real object file's most recent mention is often not its head.

**The HEAD-PREFERRING readout** asks the same chosen file for its most recent NOUN/PROPN mention instead.
Same clustering, same winner, same questions, nothing else changed:

| | pronoun span | |
|---|---|---|
| shipped files, most-recent readout (the live organ) | 0.3144 | -- |
| **shipped files, head-preferring readout** | **0.3144** | **+0.0000 CI[0.0000,0.0000] -- an EXACT identity** |
| the competition, most-recent readout | 0.3024 | -0.0120 vs shipped, n.s. |
| **the competition, head-preferring readout** | **0.3593** | **+0.0449 vs shipped** CI[-0.0395,+0.1295] n.s.; **+0.0569 CI[+0.0173,+0.1017] CI-SEPARATED vs the same files with the old readout** |

🔑 **The readout change is worth EXACTLY ZERO on the shipped files and +0.0569 CI-separated on the
competition's files.** That is the owner's pattern with a control attached: the upstream rung became
brain-foundational, the downstream consumer was built for the old, poorer signal, and repairing it is not a
free win -- it only pays once the files are real. With both, the end read closes **+0.0449 of the +0.1138
oracle gap (39%)**, not CI-separated at 12 documents (half-width 0.085).

**The readout lives in `hdlab/coref.py::graded_pronoun_resolve` (`last_nom[k]`), which this brief may not
diff.** It is a one-line change -- keep `last_nom[k]` as the most recent NOUN/PROPN mention, falling back to
any -- and it is handed to strategy with the number above.

## 7. THE NEGATIVES, RESEARCHED TO THE MECHANISM

**(a) A MENTION-level cue counted as a PAIRWISE cue is a base-rate artifact.** My first teacher run gave
`novelty: indefinite +2.84 == definite +2.84`, i.e. no information. The cause is structural: definiteness is
a property of the mention, so its value is constant across that mention's candidate files, and the
same/different ratio is then driven by the candidate-set SIZE, not by identity. The brain-correct home for
it is the **criterion** (Heim's condition constrains the update, not the choice), and moved there it
produces the pinned ordering (+1.46 / +0.18 / -0.25). **Two cues also overlapped** (`name_id` vs
`name_surf`; `head_id` vs `head_type`, whose `na` value meant both "already matched" and "no head" and so
scored +2.52 by reading the other cue's signal). Re-cut into mutually exclusive value spaces, the table is
interpretable and the double-counting is gone.

**(b) Conditioning the nominal-run cue on the category did NOT fix the junk merges.** I hypothesised that
`his → put` came from merging VERB-headed tokens into their neighbour's file, so I split `np` into
`gap1_nom` / `gap1_x`. The teacher's answer: **+6.23 vs +5.59** -- and `gap2_x` (+4.96) is *higher* than
`gap2_nom` (+4.15). On GUM TRAIN gold, adjacency is diagnostic **regardless of category**, so the cue set
correctly declines to suppress those merges. The merges are not the error; **the readout is** (§6). The
category values are kept because they are the honest shape of the evidence, not because they helped.

**(c) `tau` does not transfer perfectly from TRAIN to TEST.** On TRAIN, `tau=+2` was the point where the
partition rose and the pronoun row did not fall (span -0.0018 n.s., B3 +0.0328); on TEST `tau=+2` buys
almost no partition (+0.0084 n.s.) while `tau=0` buys +0.0560 CI-sep. The activation scale depends on
document length and mention density, so a fixed absolute threshold is not scale-free. The brain-faithful
alternative is the **margin** form already in `entity_resolver.retrieve` (`policy='compete'`: update only if
the top dominates the runner-up), which is scale-free -- named in §10 as the first alternate path, not built
here.

**(d) The crosstype bridge cannot be woken from inside this organ** (§3): two repairs shipped, third
blocker is pri 134's relation rung. `predication` reaches 0 of the 175 split entities today; its learned
validity (+2.84) says it will be worth a lot the moment it fires.

## 8. THE SIGNAL-LOSS TRACE, CHAIN BY CHAIN, WITH COUNTS

For the signal the end read needs -- *which FILE is this mention, and does the pronoun pick get the right
one back* -- on real GUM documents, text only:

| rung | hand-off produces | next rung reads | LOST | BF status **for this signal** |
|---|---|---|---|---|
| tokens → categories (`lexical_categories`) | a graded category posterior; PRON on 0.9855 of gold PRON | the introduction organ | small, but **122 VERB / 30 ADV heads per 12 docs** become mentions | BF (counts + forward-backward) |
| categories → **introduction** (`referent_per_np`) | one referent per content-noun TOKEN, `span_toks=[head]`, a filled phi card | the clustering, the bridge, the criterion | **THE BIGGEST SINGLE LOSS: 1,331 of 3,689 same-entity cross-file pairs are inside ONE gold mention span; the crosstype bridge gets 0 binds; Heim's definiteness reads `bare` on 100% of mentions** | BF in form (DRT referents) but the SPAN is not the brain's unit -- an NP is one object file |
| introduction → **clustering** (`entity_resolver.cluster`) | 643 files for 293 gold entities; B3 0.5611 (P 0.798, **R 0.433**) | the pick, `sm.entities`, goals, world state | **the hard phi+head FILTER cannot express type, predication, definiteness or a novelty threshold at all** | **was NOT BF in its combination rule** (filter-then-rank vs L&V graded sum) -- this is what the diff fixes; B3 → 0.6172, +0.0560 CI-sep |
| clustering → **the pick** (`coref.graded_pronoun_resolve`) | the file id (pri 131) | the record | 0 -- the contract is right | BF (the pinned activation equation over files) |
| the pick → **the answer** (`last_nom[k]`) | the file's MOST RECENT mention | the antecedent span, the scorer, every consumer | **+0.0569 CI-sep, and EXACTLY 0.0000 on the old files** -- the readout is built for head-buckets | **not BF**: an object file is reviewed at its HEAD, not at whatever token came last |
| the fine relations (pri 129 → `dep`) → **the bridge** | `appos`/`flat`/`compound` unavailable | `precise_constructs` | the bridge yields **1 bind on 12 documents** even fully repaired | pri 134's rung |

## 9. THE OWNER'S PUSH SCRIPT, RUN ON MYSELF

**(i) Where is the signal lost, rung by rung?** §8. Nothing is lost above the introduction organ; the
introduction organ loses the NP (1,331 pairs, the bridge, the determiner); the clustering's combination rule
loses the graded cues (+0.0560 B3 recovered); the pick's readout loses +0.0569.
**(ii) Prototyped past every wall; a heuristic is not the landed form.** The nominal-run cue is a LEARNED
validity, not a rule -- the teacher sets its weight and I report the weight it chose (including where it
refused my category hypothesis). The head-preferring readout is a PROTOTYPE that LOCATES the signal; its
landed form is a one-line change in the pick, in another brief's file, handed over with its number.
**(iii) Is the wiring alone enough to reach brain level?** **No, and it is quantified.** The competition
closes 39% of the oracle gap once the readout is repaired. The rest is upstream: the NP span (81% of the
splits are reachable only by a nominal-run cue that would be unnecessary if the mention were the NP) and the
fine relations (pri 134) that the bridge needs.
**(iv) Nothing frozen.** The validities are counts; the strengths are recomputed from them; the online
observe path accrues the reader's own high-margin decisions; the asset is re-buildable in one command.
`tau` is swept on TRAIN and reported on TEST; nothing is adopted from a lab.
**(v) vs the state of the art on this rung's own metric.** A supervised coreference system on GUM scores
B-cubed well above 0.85; our population is strictly harder (text only, no gold mentions, the reader's own
mention inventory) and the glass-box levers that close it are named and numbered: the NP span, the readout,
pri 134's relations, and the entity-type KB for names.
**(vi) False-negative audit of my own negatives.** The "lemma key" negative is reported against my own
expectation with the exact count (0 of 3,689 pairs). The "category-conditioned run cue" negative is reported
with the teacher's own weights rather than hidden. The `tau` transfer failure is reported with both splits'
numbers and the scale-free alternative named. The Principle-B caveat on pri 131's headline number is
reported against a number this session depends on.
**(vii) Prior work reused.** `salience_binder.actr_activation` + `ROLE_PROMINENCE`, `coref.EntityAliaser` +
`name_content_tokens`, `lexical_utils.{head_lemma, concept_lemma}`, `typed_spokes.{coref_type_license,
type_licenses, entity_type_lemmas}` (the frozen entity-type spoke), `crosstype_bridge` via the adapter,
pri 131's cell and scorers, pri 125's file card, the B3/MUC/CEAFe contract of
`exp_commonnoun_coref_diagnostic_v1`, and `notes/BRAIN_MATH_REFERENCE.md` §A.

## 10. ALTERNATE PATHS -- equally or MORE brain-foundational than what I shipped

1. **Make the NP the unit of introduction (the first-class fix).** Structure: Heim/DRT file cards are opened
   at the NP, not at the noun. Maths: the introduction organ emits one referent per maximal nominal, head by
   the Right-Hand Head Rule (Williams 1981), with the determiner and modifiers on the span. What it would
   take: `referent_per_np` + a mention-schema change every organ reads. Why not now: outside these three
   files, and it is a schema blast radius. **It is MORE brain-foundational than my nominal-run cue**, which
   is a repair of a segmentation the brain never makes -- and it would simultaneously restore the crosstype
   bridge, Heim's definiteness, and the modifier-split cue (`the old man` ≠ `the young man`) that
   `commonnoun_binder` already implements and cannot use.
2. **A SCALE-FREE criterion: the margin rule that is already in `retrieve`.** `policy='compete'` updates only
   if the top dominates the runner-up by a margin -- a relative criterion, invariant to document length,
   which is what §7(c) says the absolute `tau` is not. Cheap: the core already supports it.
3. **Noise + a softmax instead of an argmax.** ACT-R's retrieval is stochastic (logistic activation noise);
   a graded posterior over files, handed DOWN to the pick rather than a hard assignment, is the same move the
   substrate made for categories and heads. That would let the pick integrate file uncertainty instead of
   inheriting a point decision -- and it is how the pinned model actually works.
4. **ONE retrieval organ for every anaphor.** `affected_entity_resolver.EntityTokens` holds the same
   activation + Centering + Principle A/B + impletion; with the pick and the clustering now agreeing on what
   a candidate IS, the merge pri 131 named is finally expressible.

## 11. ADJACENT COMPONENTS (capability / limitation / opportunity / BF status)

| component | status for THIS signal | opportunity |
|---|---|---|
| `referent_per_np` (the introduction organ) | BF in form; **`span_toks=[head]` is the single biggest loss on this chain** | the NP span: 1,331 pairs, the bridge, the determiner, the modifier cue -- **the highest-value upstream target found here** |
| `coref.graded_pronoun_resolve` (`last_nom[k]`) | **not BF for this signal**: reviews a file at its most recent token | the head-preferring readout: **+0.0569 CI-sep, and exactly 0.0000 on the old files** |
| `crosstype_live_adapter` + `crosstype_bridge` | **dead on the live path** (0 binds on 12/12); two blockers repaired in the diff, the third is pri 134 | learned validity +2.84 -- it pays the moment the relations exist |
| `typed_spokes` entity-type spoke | BF supply, LIVE in the competition (`licensed +0.91 / blocked -0.32`) | reaches 16 of the 175 split entities; a Wikidata P31 KB (the filed lead) would widen it |
| `lexical_categories` | BF | 122 VERB / 30 ADV heads per 12 docs become mentions -- a referent-eligibility gate is a category-rung question |
| `commonnoun_binder` | NOT_BF, retired | its **modifier-split** cue is a real identity cue that cannot fire on one-token spans |
| `entity_resolver.retrieve` | the shared core; `policy='compete'` unused on this arm | the scale-free margin criterion (§10.2) |

## 12. EVALUATION OF THE MOST SUCCESSFUL IMPROVEMENT -- what let the signal be maximised

The biggest number here is **B-cubed recall 0.433 → 0.524 with the twin 0.43 below**, and the reason is the
owner's pattern exactly: **the chain was cracked to the top for the partition and stopped one rung short for
the read.**

| rung | cracked? |
|---|---|
| tokens → categories | **yes** |
| categories → introduction (the referent + the phi card) | **partly -- the card is filled, the SPAN is not** |
| introduction → **the merge/split decision** | **YES, this session** -- the hard filter became the pinned graded cue sum with counted validities and a learned novelty criterion (+0.0560 B3 CI-sep, twin -0.3748) |
| clustering → the pick's identity | **yes** (pri 131) |
| the pick → **the answer it returns** | **no** -- `last_nom[k]` reviews the file at its most recent token; +0.0569 CI-sep is sitting there |
| the fine relations → the bridge | **no** (pri 134) |

So the partition moved *because this rung's combination rule finally became the brain's*, and the end read
did not move *because the rung below it is still built for the old, poorer signal* -- and the identity
control (0.0000 on the shipped files) is what turns that from a story into a number.

## 13. KEY REALIZATIONS

1. **Decompose an oracle gain with partition algebra before building on it.** `R ∧ G` and `R ∨ G` cost one
   afternoon and they moved the whole target: the brief was named after the over-merge half (+0.0120, not
   separated) and the lever is the under-split half (+0.0629, separated).
2. **A cue that is a property of the MENTION cannot be counted as a property of the PAIR.** The candidate-set
   size, not identity, drives the ratio -- and the fix is not a better count but the right *place*: the
   criterion side of the threshold inequality, which is where Heim's condition belongs anyway.
3. **When a downstream number does not move, itemise it before defending it.** 26 losses, all of the shape
   `pronoun → a non-nominal token`, pointed straight at the readout; and the readout arm's **exact 0.0000 on
   the shipped files** is what proves the gain is the upstream rung's, not the readout's.
4. **Count what a cue can even REACH before weighting it.** 69.7% of the split entities were reachable by no
   cue in the brief's list; that single count redirected the build to the nominal run (81.1%) and exposed the
   segmentation defect behind it.
5. **A dead join looks exactly like a weak cue.** The crosstype bridge has a learned validity of +2.84 and
   fires zero times; without counting the binds I would have concluded the predication cue was worthless.

## 14. WHAT I WOULD WITHDRAW FIRST IF IT TURNED OUT TO BE WRONG

The **`np` (nominal-run) cue's generality**. It is the strongest weight in the table (+6.23) and it is doing
the work of a mention-segmentation fix. Its validity was counted on GUM TRAIN, where adjacency really is
diagnostic; on a genre with heavy apposition or list structure ("Mary, John and Sue") adjacency will merge
distinct entities, and the precision column is where that would show. The honest landing is therefore the
NP-span fix upstream (§10.1), after which the cue should *lose* most of its weight when re-taught -- and if
it does not, that is the signal that I am wrong about what it is doing. Second, the **+0.0449 end-read gain
is a 12-document point estimate** with a half-width of 0.085; it is not CI-separated and must not be quoted
as if it were.

## 15. SUBMISSION PROMPT

```
PENDING
```
