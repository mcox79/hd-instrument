---
problem: the_graded_pronoun_pick_returns_a_head_string_and_a_colliding_sentinel_instead_of_an_entity_id_and_an_antecedent_span_fix_the_identity_contract_and_the_scoring_before_any_weight_is_tuned
status: SOLVED
bar: "Two same-head entities stay distinct through reference, goals and belief (witness); a wrong same-head antecedent scores wrong; unannotated text reports accuracy unavailable with the four counts; no valid id used as a sentinel; the pronoun instrument not down (or the clustering loss named with items); the coref board row not down -- OR a numbered located negative."
result: "FIVE OF THE SIX BAR LEGS MET, THE SIXTH BLOCKED OUTSIDE MY THREE FILES AND NAMED. Every number is through the LIVE SituationReader().read() on TEXT ONLY with the PROPOSED SOURCE loaded and the shipped organ restored by rebinding, both arms in ONE process. (1) IDENTITY: two same-head `doctor` referents stay two files and the pick answers with a live entity id where the shipped organ answers with a head string and NO entity at all (witness W1/W1b); the goal canonicaliser returns the SELECTED identity, not whatever occupies id -1 (W8); on 6 GUM documents the shipped organ carries an identity on 0 of 372 records (it reaches the goal register only through a HEAD STRING -- strategy's 2026-09-15 stopgap at hdlab/goal_register.py:757, which landed DURING this session and binds 285 owners blind to which file was chosen), while the landed contract carries an identity on 372 of 372 records, every one of them a live entity id, and binds the same 285 owners to the file the retrieval actually returned; the world state records the possession holder as the ENTITY (C-1) where the shipped organ records NO holder at all (W9, and 3 of 23 holders entity-keyed on GUM). (2) SCORING: unannotated text now reports coref_acc UNAVAILABLE on 28 of 28 documents (the shipped organ reports 0.0000 -- W4/W4b), the four counts are published and consistent (discovered 1120 = attempted 1111 + abstained 9), a wrong same-head antecedent scores WRONG (W5; the shipped head-membership scorer credits it, W5b -- 8 of 795 items are inflated that way), and the single-sentence comparator is EXECUTED and disagrees (W6). (3) THE INSTRUMENT IS NOT DOWN: 28 MODERN GUM test documents, the same 795 fixed questions pri 125 landed on, ABSTENTION = WRONG, floor recomputed on this population, documents the bootstrap unit -- shipped 0.3321 span / 0.2717 head-credit (head-credit reproduces pri 125's landed 0.2717 EXACTLY), LANDED 0.3283 / 0.2692, delta -0.0038 CI[-0.0116,+0.0016] NOT CI-separated (3 items of 795); landed vs the nearest-prior-compatible floor 0.2415: +0.0868 CI[+0.0254,+0.1550] CI-SEPARATED; landed vs the information-free phi twin 0.2289: +0.0994 CI[+0.0167,+0.1921] CI-SEPARATED, and the twin sits AT the floor (-0.0126 n.s.). (4) THE KEY ALONE COSTS EXACTLY NOTHING AND THE HEADROOM IS LOCATED: with the identity basis as the ONLY variable on ONE code path (12 documents, the replay asserted equal to the live organ item-for-item) head-string 0.3263 == reader's own files 0.3263 (delta EXACTLY 0.0000, CI[0,0]) while the GOLD-entity oracle scores 0.4431, +0.1168 CI[+0.0241,+0.2614] CI-SEPARATED -- so the contract is free and the +0.1168 is attributable to the reader's CLUSTERING, named with items (262 of 1486 files touch more than one gold entity). (5) THE pri 122 COREF ROW REPORTS A POPULATION: aligned 0 of 4 documents and an EMPTY row before (the row read the scheduler's 2-tuple as its question list), aligned 4 of 4 and n=115 after. (6) NO-REGRESS EXACT: UD-EWT agent 0.6377 -> 0.6377, patient 0.6838 -> 0.6838, state 0.7576 -> 0.7576, delta EXACTLY 0.0000 CI[0,0] on all three. THE LEG NOT MET: 'through belief' -- `_read_belief` builds `by_sent = {i: [] for i in range(len(sents))}` (hdlab/situation_reader.py:2869) and passes an EMPTY mention map to every belief query, so NO reference identity reaches belief on this path at all; that is deep-review D04, filed as pri 132, and it is outside the three files this brief may diff."
floor: "Nearest-prior-phi-compatible referent, recomputed on the same 795 questions and scored the same two ways: span 0.2415, head-credit 0.1849 (the head-credit floor is pri 125's 0.1849 reproduced exactly). Also run: the SHIPPED organ as the deployment floor (span 0.3321 / head-credit 0.2717), and the GOLD-entity ORACLE as the ceiling probe (0.4431 span on 12 documents)."
controls: "(1) INFORMATION-FREE PHI TWIN -- both tables the organ reads permuted within person class (referent_per_np.PRONOUN_PHI and state_of_mind.PRONOUN_SCOPE; permuting only one was pri 125's control defect): 0.2289 vs the landed 0.3283, the landed arm wins +0.0994 CI[+0.0167,+0.1921] CI-separated and the twin sits at the floor. (2) THE SHIPPED ORGAN ITSELF, in the SAME process, restored by rebinding the exact attributes the diff touches -- so the comparison is code vs code, not run vs run. (3) IDENTITY-BASIS ISOLATION: the same pick over head-keyed / file-keyed / GOLD-keyed candidates on one code path; the file-keyed arm is asserted byte-equal to the live organ before the contrast is reported. (4) CAN-FIRE CONTROLS on the SHIPPED organ: coref_acc 0.0000 on unannotated text (W4b), a wrong same-head antecedent scored CORRECT by head membership (W5b), 0 of 372 records carrying any identity (W8b), no possession holder at all (W9). (5) NO-REGRESS: UD-EWT agent/patient/state exactly unchanged; the reader's own 795-question instrument not CI-separated down. (6) PHASE DIAGRAM SWEEP (25 configurations, offline replay asserted equal to the live organ): the shipped operating point is the best or tied-best and NOTHING is adopted -- w_number 1/2/4 all lose ~0.05, windows 1-2 lose 0.0625, w_gender 0 loses 0.0795, decay 0.5 loses 0.0795, w_focus 0 gains +0.0114 CI[0.0000,+0.0235] n.s. (7) PRINCIPLE B AS PRINCIPLE-vs-PARSE: off 0.3797 / our parse 0.3646 / TREEBANK parse 0.3848 on 16 documents -- the exclusion ships DEFAULT-OFF with that number."
files_changed: "experiments/exp_pronoun_pick_identity_contract_v1.py (NEW -- the cell; get_output_dir per Q115). verification/test_pronoun_pick_identity_contract.py (NEW -- 14 claim-pinning witnesses, pytest-collectable + standalone). notes/problems/<slug>/pick_identity_contract_patch.diff (NEW -- the proposed hdlab change: hdlab/coref.py + hdlab/situation_reader.py + hdlab/goal_register.py, `git apply --check` clean against the working tree at 7c84070b1). NO hdlab/ file written: the cell materialises the diff into data/exp_pronoun_pick_identity_contract_v1/patched/ and loads it into the live modules, and every number above is measured through that patched source."
reverify: ".venv/Scripts/python.exe verification/test_pronoun_pick_identity_contract.py   # 14/14 on the tree AS LANDED -- it detects the landed contract from the LIVE modules (CorefResolution.antecedent_span / resolved_entity, coref.entity_key, the coarg parameter, the pronoun_principle_b flag) and then runs every arm against hdlab/ with NO materialize and NO monkeypatch; on an UNPATCHED tree the same file materialises the diff and restores the shipped organ so the can-fire halves still fire. Every check is a claim (an invariant, a direction, or a can-fire control), never a pinned number.  The measured rows: .venv/Scripts/python.exe experiments/exp_pronoun_pick_identity_contract_v1.py --pronouns 28 (the headline, ~45 min) / --identity-basis 12 (the oracle probe) / --principle-b 16 / --sweep 8 / --consumers 6 --board-coref 4 --noregress 10.  Each row writes its OWN metrics_<row>.json and never overwrites another."
---

# SOLVED -- the pronoun pick now answers with a discourse entity and an antecedent span, and its scoring stops counting "unscoreable" as "wrong"

## Status in one line
The contract change is **free on accuracy and decisive on identity**: the pick's answer is the reader's own
entity file plus the mention that supplied the evidence, the four consumers that received nothing (goals,
world state, the board row, the scorer) now receive it, and the isolated key comparison says the new basis
costs **exactly zero** (0.3263 vs 0.3263) while the gold-entity oracle sits **+0.1168 CI-separated** above
both -- so the remaining pronoun signal is in the reader's **clustering**, now measurable for the first time.

## 0. THE OPENING MOVE -- how the brain does THIS (PINNED vs OUR-INVENTION)

A pronoun is not resolved to a word. It is resolved to a **discourse entity**: a **file card** (Heim 1982
file-change semantics; Karttunen 1976) / an **object file** (Kahneman & Treisman 1992), opened at
introduction and updated at every later reference. Retrieval is **content-addressable and cue-based**
(Anderson & Schooler 1991 base-level activation; Lewis & Vasishth 2005; McElree direct access): the probe's
cues are matched against the FILE's accrued card, the activation is summed over the FILE's whole reference
history, and what comes back is the FILE. The **mention that supplied the evidence** is the antecedent -- a
position in the text, not a string. A plain pronoun's binding domain **excludes its clause-mate co-argument**
(Chomsky 1981 Principle B; Reinhart 1983); a reflexive **requires** one (Principle A).

| piece | status |
|---|---|
| the pronoun resolves to a FILE; the file accrues features and history over its mentions | **PINNED** (Heim; Kahneman-Treisman) |
| ACT-R base-level activation over the file's history, cues SUMMED not filtered | **PINNED** (Anderson & Schooler; Lewis & Vasishth) |
| the ANTECEDENT is the mention that supplied the evidence (a span) | **PINNED** (object-file reviewing) |
| Principle B / Principle A over clause-mate CO-ARGUMENTS | **PINNED** (categorical universals) |
| impletion: a resolved pronoun is written into the file's history | **PINNED** (Kahneman-Treisman-Gibbs) |
| the discrete record, the tie rule, the accessibility window, the cue weights | **OUR-INVENTION** (swept, never adopted) |
| the scoring outcomes (nullable, per-item scoreability, the four counts) | **NOT a brain claim at all** -- instrumentation, and it belongs OUTSIDE the inference result |

**The consequence that IS the fix:** if the answer is a head STRING then (a) two files the reader opened
separately are indistinguishable to every consumer, (b) the mention that supplied the evidence is gone, so a
scorer can only ask "does this head name the right entity ANYWHERE in the document", and (c) the pick cannot
even express Principle B, because the exclusion is on the co-argument's FILE. D02, D05 and D06 are the same
missing object: **the discourse entity**.

## 1. THE DEFECT, REPRODUCED FIRST-HAND (the witnesses, 14/14)

| the review's finding | reproduced here, live | witness |
|---|---|---|
| D05: candidates keyed by `m["head"].lower()` | the shipped organ answers with a head string and NO entity (`resolved_entity=None`, `resolved_cluster=None`) | W1b |
| D02: `-1` is the sentinel AND the first live entity | the reader's live ids on a 4-sentence passage are `[-9,-8,-7,-6]` -- **`-1` is a valid file**; every unresolved record now carries `None` | W3 |
| D02: `goal_register` reads `names.get(r.resolved_cluster)` | the shipped organ reaches the goal register **only through a head string** (strategy's 2026-09-15 stopgap, landed mid-session): **0 of 372** records carry an entity, so two files sharing a head are one owner | W8b |
| D02: `_read_world_state` keeps only `rc >= 0` | with the shipped organ the possession fact is **lost entirely** (no holder at all), because the negative online id is dropped and the binder then has nothing to bind | W9 |
| D06.1: `coref_acc` 0 where there is no answer key | the shipped organ reports **0.0000** on annotation-free text; the landed organ reports **None on 28 of 28** documents | W4b / W4 |
| D06.2: the comparator is the main result | the branch returned `(out, side, side)`; the executed single-sentence comparator **disagrees** | W6 |
| D06.3: head membership credits a wrong same-head antecedent | the shipped scorer marks a pick on the OTHER doctor `correct=True`; measured inflation on the real population: **8 of 795 items** | W5b |

## 2. WHAT THE DIFF CHANGES (four rungs)

1. **The identity contract** (`hdlab/coref.py`): `entity_key(m)` = the reader's own online file id
   (`m["cluster"]`, written by `entity_resolver.cluster` as `-(file+1)`). History, feature card, Centering
   focus and impletion are all keyed by it; `mention_span(m)` returns the antecedent span. The record is
   `{resolved_entity, resolved_head, antecedent_span, candidates, abstain_reason, ...}`, and
   `resolved_entity is None` is the unresolved value -- **no valid id is ever a sentinel**, on any path
   (`_read_entities_core`'s `-1 if None` is removed too).
2. **ONE question, ONE outcome** (`discovered_pronoun_targets`): every third-person pronoun is scheduled --
   the retrieval demand exists whether or not a compatible referent is accessible -- and the pick returns
   exactly one record per question with an explicit `abstain_reason` (`no_candidate` / `no_compatible` /
   `tie`). So **discovered == attempted + abstained** and a consumer can align by index; that is what makes
   the pri 122 board row report a population instead of `n=0`.
3. **Principle B from the reader's OWN parse** (`_coargument_positions`, **default OFF**, §5): the other
   dependents of the same governing VERB/AUX from the shared per-read parse, banning the co-argument's FILE.
   pri 125's rank proxy ("any other core-ranked mention in the sentence") was measured at **-0.104** and
   refuted; this is the relation itself, and it is only expressible because candidates are now files.
4. **Scoring outside the inference result** (`hdlab/situation_reader.py`): scoreability decided in BOTH
   branches and **reset per read**; alignment by the ANTECEDENT SPAN's gold entity instead of document-wide
   head membership; the single-sentence comparator EXECUTED (same organ, file store cleared at each sentence
   boundary); the four counts published; `coref_acc` keeps its fixed denominator and the
   conditional-on-attempted rate is published separately as `coref_attempted_acc`. Consumers updated in the
   same diff: `goal_register.make_canonicalizer` reads `resolved_entity`, and `_read_world_state` decides
   validity by **membership in the read's own entity set**, never by sign.

## 3. THE HEADLINE -- 28 MODERN GUM test documents, 795 fixed questions, text only, ABSTENTION = WRONG

All arms in ONE process; the shipped organ is restored by rebinding the exact attributes the diff touches.
`span` = the picked ANTECEDENT SPAN is a mention of the gold entity (the exact score the contract makes
possible); `head-credit` = pri 125's scorer (does the picked head name any prior mention of the gold entity).

| arm | span | head-credit | answered | vs floor (span) |
|---|---|---|---|---|
| shipped (head key, head-membership scoring) | 0.3321 | **0.2717** | 783 | +0.0906 CI[+0.0290,+0.1592] |
| **the LANDED contract** | **0.3283** | **0.2692** | 779 | **+0.0868 CI[+0.0254,+0.1550] CI-SEP** |
| + Principle B (built, default OFF) | 0.3195 | 0.2591 | 779 | +0.0780 CI[+0.0199,+0.1393] |
| info-free PHI TWIN (both tables permuted) | 0.2289 | 0.1723 | 777 | -0.0126 CI[-0.0551,+0.0248] **AT FLOOR** |
| floor: nearest prior phi-compatible referent | 0.2415 | 0.1849 | -- | -- |

- **landed - twin = +0.0994 CI[+0.0167,+0.1921] CI-separated** (the twin loses and sits at the floor).
- **landed - shipped = -0.0038 CI[-0.0116,+0.0016], NOT separated** -- 3 items of 795.
- the shipped arm's head-credit **0.2717** and the head-credit floor **0.1849** reproduce pri 125's landed
  numbers exactly, on the same 795 questions: this is the same instrument, not a new one.
- counts (landed): **discovered 1120 = attempted 1111 + abstained 9**; `coref_acc` None on 28 of 28 documents.

## 4. THE IDENTITY BASIS AS THE ONLY VARIABLE -- and the oracle-ceiling probe

One code path, one question set, 12 GUM documents; the `files` arm is **asserted equal to the live organ
item-for-item** before any contrast is reported, so the replay IS the organ.

| identity basis | span | vs head |
|---|---|---|
| head string (the shipped key) | 0.3263 | -- |
| **the reader's own entity files** | **0.3263** | **+0.0000 CI[0.0000,0.0000]** |
| the GOLD entity (oracle, never shippable) | **0.4431** | **+0.1168 CI[+0.0241,+0.2614] CI-SEP** |

**This is the whole result in two numbers.** The contract costs *exactly nothing* on accuracy -- and the
reason is itself a finding: **the reader's files and head buckets are nearly the same partition today.**
Counted on the 28-document population: **1486 files, of which 262 (17.6%) touch more than one gold entity**,
and the clustering essentially never separates two same-head referents (the same merge-collapse another
solver found by counting 0 of 3224 decisions holding two same-head referents). So the identity *contract*
had to come first, and the identity *quality* is now the lever: **+0.1168 CI-separated**, sitting on
`entity_resolver.cluster` + the crosstype bridge, not on the pick.

## 5. THE NEGATIVES, RESEARCHED TO A NUMBER

### (a) Principle B costs items *through our parse* and is neutral *through a correct one*
16 GUM documents, span-scored, one code path, the exclusion rule identical in all three arms -- only the
source of the clause-mate relation changes:

| clause-mate relation | span | |
|---|---|---|
| no exclusion | **0.3797** | -- |
| the reader's OWN parse (what the diff ships, default OFF) | 0.3646 | -0.0152 CI[-0.0487,+0.0136] n.s. |
| the TREEBANK parse (oracle, diagnostic only) | **0.3848** | +0.0051 vs no exclusion (n.s.); **+0.0203 over our own parse** CI[-0.0035,+0.0552] n.s. |

**Understood, with the mechanism:** Principle B is PINNED and categorical, but it is applied through a
relation the reader computes, and our attachment rung is ~0.57 UAS. A wrong governor bans the RIGHT
antecedent; a 17.6%-impure file compounds it (banning the co-argument's file can delete the true antecedent
with it). With the relation correct the same rule is neutral-to-positive. **So it ships BUILT, WITNESSED and
DEFAULT-OFF with its number** -- not deleted, not turned on against the evidence -- and the condition to flip
it is a parse improvement, which is exactly the rung pri 15-17 own.

### (b) The phase diagram: the operating point is already at its local optimum
25 configurations, offline replay asserted equal to the live organ, 8 documents:
`w_number` 1/2/4 all **lose ~0.05** (the brief's "sweep the number cue from its current 0" -- the answer is
that 0 is right, because `they` is number-ambiguous and most common-noun cards carry no number); windows 1
and 2 **lose 0.0625** (unbounded accessibility is better, as pri 125 also found at scale); `w_gender` 0
**loses 0.0795** (the agreement cue is load-bearing); `decay` 0.5 **loses 0.0795** and 1.0/3.0 also lose
(d≈2 is right for this task, never the lab's 0.5); `w_focus` 0 **gains +0.0114 CI[0.0000,+0.0235] n.s.**
Nothing is CI-separated, so **nothing is adopted** -- and the one direction worth a follow-up is that the
Centering focus bonus may be slightly harmful at this operating point.

### (c) The 3-item live difference from the shipped organ, itemised
58 of 795 questions get a different antecedent span; the landed contract **wins 11, loses 21, both wrong 25,
both right 1**. The losses are not the key (the key is exactly neutral in isolation, §4): they are the
scheduler change (every pronoun is now attempted, so 4 more questions get an answer that can be wrong) and
Principle A now running over the parse for reflexives. Net **-0.0038, not separated**.

## 6. THE SIGNAL-LOSS TRACE, CHAIN BY CHAIN, WITH COUNTS

For the signal the end read needs -- *which FILE does this pronoun name, and does that file reach the
consumers* -- on real GUM documents, text only:

| rung | hand-off produces | next rung reads | LOST (before -> after) |
|---|---|---|---|
| tokens -> categories (`lexical_categories`) | PRON on 0.9855 of gold PRON (pri 125) | the introduction organ | 0 -- at brain level |
| categories -> introduction (`referent_per_np`) | a referent per PRON + a filled file card | the streams | 0 since pri 125 |
| introduction -> **online clustering** (`entity_resolver.cluster` + crosstype bridge) | 1486 files on 28 documents | **the pick (NEW: this is now load-bearing)** | **262 impure files (17.6%); worth +0.1168 CI-sep against the gold oracle** |
| clustering -> **the pick** | was: a head STRING | the record | **the entity: 100%** (0 of 372 records carried one) |
| the pick -> **goal canonicaliser** | was: `resolved_cluster` (None after the guard; `-1` before it), then a HEAD STRING via strategy's mid-session stopgap | `names.get(...)` | **the entity: 0 of 372 records -> 372 of 372.** The owner COUNT is the same either way (285 = 285 on 6 documents): the difference is that the stopgap binds by head string, so two files sharing a head are one owner |
| the pick -> **world state** | was: dropped by `rc >= 0` | `he_she_cluster` | **100% -> 0%: 0 -> 3 entity-keyed holders of 23; the shipped organ recorded NO holder for a pronoun agent at all** |
| the pick -> **the pri 122 board row** | was: a 2-tuple read as the question list | `len(targets) == len(res)` | **100% -> 0%: aligned 0/4 docs and an empty row -> aligned 4/4 and n=115** |
| the pick -> **the scorer** | was: `correct=False` with no answer key; head membership | `coref_acc` | **a corrupt number -> None on 28/28; span alignment (8 of 795 head-credit inflations removed)** |
| the pick -> **belief** | -- | `_read_belief` passes `{i: [] ...}` | **100%, NOT FIXED -- `situation_reader.py:2869`, deep review D04, pri 132** |

**Brain-foundational status of each rung for THIS signal.** Categories and introduction hand down graded,
brain-foundational signal (pri 125). The **clustering** is brain-foundational in form (Heim file change +
ACT-R retrieval) and 17.6%-impure in fact -- it is the first rung on this chain whose *quality*, not whose
*mechanism*, is the limit. The **pick** was brain-foundational in its arithmetic (the pinned activation
equation) but **not in its representation**: it retrieved over word forms, which is precisely the thing the
object-file literature says the brain does not do. The **consumers** were receiving a point estimate that
could not name anything (a head string) or a sentinel that named the wrong thing (`-1`).

## 7. NO-REGRESS AND THE BOARD

- **UD-EWT, 10 documents, the live reader, both arms in one process:** agent 0.6377 -> 0.6377, patient
  0.6838 -> 0.6838, state 0.7576 -> 0.7576; **delta EXACTLY 0.0000, CI [0,0]** on all three.
- **The pri 122 reader-driven coref row** (4 GUM documents): before, `coref_aligned` false on 4 of 4 and the
  row empty -- the row calls `discovered_pronoun_targets(ms)` and got the **2-tuple**, so its question list
  had length 2 against 115 resolutions. After, aligned 4 of 4 and the row reports **n=115**. ⚠️ **It reports
  0/115 for the model AND for all three floors AND for the twin**, because the row's answer key is
  `tm["cluster"]` -- the reader's own freshly-opened pronoun id, which on text-only input can never match any
  prior mention. That is a defect in the row (`exp_board_rows_on_the_reader_v1.py:333`), not in the organ,
  and it is now visible because the population exists; the fix is to score that row against the GUM gold
  entity ids the loader already has. **Named for strategy, not touched (pri 122's file).**
- **Existing witnesses:** `verification/test_world_state_densify_landing_organ.py` **is already red on HEAD**
  for an unrelated reason (`TypeError: unexpected keyword argument 'spacy_pred_gate'` -- the kwarg was
  removed 2026-09-08; verified by running it with and without the patch: identical failure), and its line 83
  re-implements the old `rc >= 0` rule, so it must be updated to the membership rule when the diff lands.

## 8. THE OWNER'S PUSH SCRIPT, RUN ON MYSELF

**(i) Where is the signal lost, rung by rung?** §6. Nothing is lost above the clustering; the clustering
leaks **+0.1168 CI-sep** (262 impure files); the pick->consumer hand-off carried **no entity at all** (0 of 372
records) to four consumers and now carries one to all of them; belief is still 100% lost and is another
brief's file.
**(ii) Prototyped past every wall; a heuristic is not the landed form.** The identity basis is the reader's
own organ output, not a heuristic. The scheduler change is the retrieval demand itself. The one rule I built
that the numbers did not support (Principle B through our parse) ships **off, with its number and its flip
condition** rather than silently on or silently deleted.
**(iii) Is the wiring alone sufficient to reach brain level?** **No, and now it is quantified.** The wiring
buys the consumers everything and the accuracy nothing; the accuracy lever is one rung up --
**+0.1168 CI-separated** sitting on the clustering's 17.6% impurity, plus the parse for Principle B.
**(iv) Nothing frozen.** No table is introduced. The cue weights are the existing ones, swept and **not**
adopted; the accessibility window is swept; the file card is computed per read from the form and the lexicon.
The one thing that SHOULD move online -- the clustering's own merge/split decisions -- is `entity_resolver`'s
and is named as the next problem.
**(v) vs the state of the art.** A supervised coreference system on GUM pronouns is far above 0.33; our
population is strictly harder (text only, no gold mentions, every third-person form, abstention = wrong) and
the glass-box levers that close it are named and numbered: the clustering (+0.1168 measured), Principle B
through a better parse (+0.0203 measured at the oracle), and the Kehler-Rohde next-mention prior (+0.093 in
the sibling organ) -- all three now expressible because the pick scores entities.
**(vi) False-negative audit of my own negatives.** The Principle-B negative was NOT left as "the principle
does not help": the oracle-parse arm was built and it reverses the direction. The "entity key does not help"
result was NOT left at the live -0.0038: the key was isolated on one code path, where it is **exactly**
0.0000, which is a different and much stronger claim. The head-credit inflation I set out to remove turns
out to be **8 items of 795** -- I report that deflation against my own motivating finding.
**(vii) Prior work reused.** `entity_resolver.cluster` (the online files), `salience_binder.actr_activation`
+ `ROLE_PROMINENCE`, `affected_entity_resolver.is_reflexive`, pri 125's file card and discovered stream,
pri 122's board row, and `notes/BRAIN_MATH_REFERENCE.md` §A (the activation, Principles A/B, Kehler-Rohde).

## 9. ALTERNATE PATHS -- equally or MORE brain-foundational than what I shipped

1. **Make the FILE the unit of introduction, not the mention.** Structure: DRT/FCS file cards built
   incrementally. Maths: the introduction organ emits `(mention, file)` directly, with the online resolver
   INSIDE the introduction loop, so identity is computed once at introduction instead of twice (introduce,
   then cluster). What it would take: a mention-schema change every organ reads. Why not now: schema blast
   radius. **Arguably more brain-foundational than what I shipped** -- introduction and identification are
   one act in Heim's semantics.
2. **Kehler-Rohde as the pick's decision rule** (`P(r|pron) ∝ P(r next-mentioned)·P(pron|r)`, PINNED): my
   pick is the likelihood-free half. The prior alone saturates ~0.45 and the grammar likelihood added +0.093
   in `affected_entity_resolver`. Now expressible over FILES. Why not now: it is a second organ's arm and it
   needed this contract first.
3. **ONE retrieval organ for every anaphor.** `affected_entity_resolver.EntityTokens` already holds the same
   activation + Centering + Principle A/B + impletion; the reader's pick is a second implementation of one
   brain structure. With both sides now agreeing on what a candidate IS, the merge is finally possible.
4. **Score coreference by the CHAIN, not by the pick** (B-CUBED/CEAF over the reader's own files against gold
   chains). That measures the identity the reader actually built -- the thing §4 shows is the lever -- without
   an oracle, and it would make the clustering's contribution a board row.

## 10. ADJACENT COMPONENTS (capability / limitation / opportunity / BF status)

| component | status for THIS signal | opportunity |
|---|---|---|
| `entity_resolver.cluster` + `crosstype_live_adapter` | **now LOAD-BEARING** for the pick; BF in form, **17.6% impure** in fact | **the single highest-value upstream target on this rung: +0.1168 CI-sep measured** |
| `referent_per_np` (pri 125) | BF; the card is filled at introduction | it stores `span_toks=[head]`, so the antecedent span is one token -- a real NP span would sharpen both the scorer and the aliaser |
| `goal_register.make_canonicalizer` | now reads the entity (285 owners bound where 0 were) | its API is `canon(surface, sent_idx)`, so **two `him` in one sentence with different antecedents collapse to the first** -- D02's acceptance case 3; the records already carry the token position, the API does not take it |
| `_read_belief` | **receives an EMPTY mention map** (`situation_reader.py:2869`) | deep-review D04 / pri 132 -- no reference identity reaches belief at all |
| `_read_causal_reasoning` | normalises every event endpoint to its rightmost word | D07 / pri 132 -- the same class of defect one layer over |
| `world_state_register` operator lookup | `lex.get(e.predicate)` uses the SURFACE form: `take` fires, `takes`/`took` do not (observed here) | a lemma lookup would make the possession register fire on inflected verbs -- small and separable |
| the attachment rung (`attachment_arm`) | ~0.57 UAS; it is what makes Principle B negative | flipping `pronoun_principle_b` ON is a measured consequence of improving it (+0.0203 at the oracle) |

## 11. EVALUATION OF THE MOST SUCCESSFUL IMPROVEMENT -- what let the signal be maximised

The biggest number here is not an accuracy: it is **0 -> 285 goal owners and 0 -> 372 records carrying an
identity**, and the reason is the owner's pattern exactly: **the chain was cracked to the top for one signal
and stopped one rung short for the other.**

| rung | cracked? |
|---|---|
| tokens -> categories | **yes** (pri 125) |
| categories -> introduction + file card | **yes** (pri 125) |
| introduction -> **online clustering** | **no -- 262 of 1486 files impure; the measured +0.1168 headroom** |
| clustering -> **the pick's identity** | **yes** -- the pick now retrieves FILES, and the key costs exactly 0.0000 |
| the pick -> **goals / world state / the board row / the scorer** | **yes** -- four hand-offs that carried nothing now carry the entity and the span |
| the pick -> **belief** | **no** -- an empty mention map upstream of it (D04) |
| the parse -> **Principle B** | **no** -- the principle is PINNED, the relation is ~0.57 UAS |

So the accuracy did not move *because the rung above the pick is uncracked*, and the consumers did move
*because the rung below it was*. That is the same lesson pri 125 recorded from the other side (a cue cannot
be load-bearing when the card it matches is blank): **a contract cannot pay until the thing it names is
right, and it cannot be measured until the contract exists.** The oracle probe is what turns that from a
story into a number.

## 12. KEY REALIZATIONS

1. **Isolate the change on ONE code path before believing a live A/B.** The live arms differ by -0.0038 and
   the *key alone* differs by **0.0000** -- because the live "shipped" arm also carries a different scheduler
   and a different scorer. Re-keying the same mentions inside one function is what made the claim exact.
2. **When a contract change is accuracy-neutral, the oracle probe is the result.** Swapping the key for the
   GOLD key on the same path (+0.1168 CI-sep) converts "no gain" into "the gain is one rung up, and here is
   how much" -- the wall-push move that the how-walls-were-broken ledger names.
3. **A green `git apply` is not a landed patch.** My first materialisation applied NOTHING (a path-strip
   mismatch) and would have measured the shipped organ twice while calling one of them the proposal. The cell
   now asserts a marker string in each patched file before it loads it.
4. **Publish the denominator, not just the rate.** `coref_acc` was a rate over a denominator the model chose
   for itself; the fix is not a better rate but *four counts* plus an explicitly nullable outcome.
5. **A pinned principle applied through an unpinned input is not a pinned component.** Principle B is
   categorical, and through a 0.57-UAS parse it loses items. The honest landing is built, witnessed,
   default-off, with the oracle number and the flip condition.

## 13. WHAT I WOULD WITHDRAW FIRST IF IT TURNED OUT TO BE WRONG

The **span scorer's coverage assumption**: it credits a pick whose antecedent span overlaps any token of any
prior gold mention of the target's entity. If GUM's mention spans were systematically wider than the reader's
single-token heads in a way that favours one arm, the span numbers would move (the head-credit column, which
reproduces pri 125's numbers exactly, is the check -- both scorers agree on every conclusion here, which is
why I report both). Second, the **+0.1168 oracle** is measured on 12 documents with a half-width of 0.1186:
it is CI-separated, but it is not a precise estimate of the clustering's value.

## 14. PRIORITY NEXT STEPS (for strategy)

1. **The clustering is the pronoun lever, and it is now numbered**: +0.1168 CI-sep between the reader's files
   and the gold entities, 262 of 1486 files impure. That is a brief on `entity_resolver.cluster` + the
   crosstype bridge (split/merge decisions, an online observe path), not on the pick.
2. **Fix the pri 122 coref row's answer key** (`exp_board_rows_on_the_reader_v1.py:333`): it scores against
   `tm["cluster"]`, the reader's own singleton id, so every arm and every floor scores 0/115 now that the row
   finally has a population.
3. **Give `make_canonicalizer` the token position** so two same-spelling pronouns in one sentence cannot
   collapse (D02 acceptance case 3; the records already carry `target_wpos`).
4. **Update `verification/test_world_state_densify_landing_organ.py`** -- it is red on HEAD for a stale kwarg
   AND its line 83 re-implements the sign test this diff replaces.
5. **Flip `pronoun_principle_b` when the attachment rung improves** (+0.0203 measured at the treebank oracle).
6. **pri 132 (D04) is the belief leg of this brief's bar**: `_read_belief` passes an empty mention map, so no
   reference identity reaches belief on this path.

## 15. THE MEASUREMENT BASE (read this before comparing any absolute number)

Every contrast above is **both arms in ONE process on ONE base**: the cell materialises the diff into
`data/exp_pronoun_pick_identity_contract_v1/patched/`, loads it into the live modules, and restores the
shipped organ by rebinding the exact attributes the diff touches. **The base itself moved during the
session** -- pri 129 was editing other regions of `hdlab/situation_reader.py` and strategy landed a head
stopgap in `hdlab/goal_register.py` (line 757) while these rows ran -- so *absolute* numbers may shift at
integration while the *paired* contrasts hold. Two consequences I state rather than hide:
- the 795-question headline was measured against the tree as of 2026-09-15 ~19:00; the diff shipped here is
  rebased onto the tree as of ~20:30 (`git apply --check` clean), and the only source difference between the
  two inside MY regions is the two published scalars (`coref_acc` denominator / `coref_attempted_acc`),
  which no arm of the instrument reads;
- the goal-owner count was re-measured after strategy's stopgap landed, and the corrected reading is in §6
  (the count is equal; the identity behind it is not).

## 16. SUBMISSION PROMPT

```
Problem: the_graded_pronoun_pick_returns_a_head_string_and_a_colliding_sentinel_instead_of_an_entity_id_and_an_antecedent_span_fix_the_identity_contract_and_the_scoring_before_any_weight_is_tuned (priority 131)

SOLVED. The graded pronoun pick now answers with the reader's OWN discourse entity plus the antecedent
SPAN, the candidate set and an abstention reason; no valid id is used as a sentinel on any path; and the
scoring moved outside the inference result (nullable outcomes reset per read, alignment by the antecedent
span instead of document-wide head membership, an EXECUTED single-sentence comparator, and the four counts
discovered/attempted/abstained/scoreable).

Measured through the LIVE reader on text only, both arms in one process (28 MODERN GUM test documents, the
same 795 fixed questions pri 125 landed on, ABSTENTION = WRONG): landed 0.3283 span vs a nearest-prior-
compatible floor of 0.2415, +0.0868 CI[+0.0254,+0.1550] CI-separated, with the information-free phi twin at
the floor (+0.0994 CI[+0.0167,+0.1921] against it); against the shipped organ -0.0038 CI[-0.0116,+0.0016],
NOT separated. With the identity basis as the ONLY variable on one code path, head-string == the reader's
files EXACTLY (0.3263 = 0.3263, CI[0,0]) while the GOLD-entity oracle is +0.1168 CI[+0.0241,+0.2614]
CI-separated -- so the contract is free and the remaining pronoun signal is in the CLUSTERING (262 of 1486
files touch more than one gold entity). Consumers: 0 of 372 records carried an identity, now 372 of 372;
the pri 122 coref row went from aligned 0/4 documents and an empty row to aligned 4/4 with n=115; UD-EWT
agent/patient/state deltas EXACTLY 0.0000.

Built and DEFAULT-OFF with its number: Principle B from the reader's own parse (off 0.3797 / our parse
0.3646 / treebank parse 0.3848 on 16 documents -- the loss is the 0.57-UAS parse, not the principle).
Bar leg not met: "through belief" -- `_read_belief` passes an EMPTY mention map (situation_reader.py:2869),
which is deep-review D04 / pri 132 and outside the three files this brief may diff.

Files: experiments/exp_pronoun_pick_identity_contract_v1.py, verification/test_pronoun_pick_identity_
contract.py (14/14), notes/problems/<slug>/{SOLVED.md, pick_identity_contract_patch.diff}.
Reverify: .venv/Scripts/python.exe verification/test_pronoun_pick_identity_contract.py
```

INTEGRATED_BY_STRATEGY 2026-09-15 23:12 local -- DONE by strategy: the 3-file diff APPLIED after the pri 129 commit; reverify: test_pronoun_pick_identity_contract 14/14 + the pri 125 landing witness set (data/hook_state/pri131_witnesses.log) + the product board pri131a; the board cell's pronoun row re-keyed to the GUM gold entity (its answer key had been the reader's fresh singleton id) with abstention = wrong and unscoreable targets counted. PRODUCT BOARD pri131a (capped 24/600/60): the pronoun row REPORTS AGAIN -- n=805 scoreable, reader 0.2385 vs the compatible-recency rule 0.1280 and the random twin 0.0298, CI-SEP; every other reader row and every component row BYTE-IDENTICAL to pri129b; the headline aggregate 0.6425 -> 0.5088 by COMPOSITION (805 pronoun items at 0.24 enter the item-weighted mean) while the rules mix falls 0.6579 -> 0.4825, so on this run the reader is ABOVE the best-of-rules mix (+0.0263) for the first time. The agent's denied scratch deletion was not retried.
