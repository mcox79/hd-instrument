---
problem: the_agent_competition_loses_with_the_right_answer_on_the_ballot_77_to_80_percent_of_agent_errors_on_sealed_and_test_text_are_pick_errors_split_wrong_entity_from_wrong_name_token_then_reweigh_the_cues
status: PARTIAL
bar: "1. THE SPLIT FIRST. Every pick error on UD-EWT test (109) and, by strategy at landing, on the sealed set (229) labelled wrong-ENTITY vs right-entity-wrong-TOKEN, with the method stated (gold name runs / coref) and the two counts reported; the scorer of the reader-driven agent row gains an entity-level column (right entity counts as right) beside the token-level one -- both reported, the token-level stays the gate until the owner rules otherwise. 2. Wrong-entity pick errors DOWN CI-separated on UD-EWT test (bootstrap over items, both arms in one process) with the re-weighed competition; the agent row ABOVE the word-order floor on UD-EWT test CI-separated; an info-free twin (validities permuted across cues) loses. 3. No-regress: patient / state / the copular subject read on the same populations not down CI-separated; the pri 106/111/117 witnesses green on the landed tree. 4. Plastic: the validities are counts with an observe path (a two-document read shows the second document's decisions used the first's updates); the accrual rate swept, not adopted. 5. Sub-item (LOCATED item 1): the by-phrase candidate set reads the attachment arm's head; the 3 UD-EWT items reported before/after. 6. Hand-off for strategy: the landed competition re-read on the sealed holdout ONCE at landing (pri 126's hook); you predict the sealed number from UD-EWT and the prediction is recorded before the read."
result: "THE SPLIT (bar 1, MET): of the 209 pick errors on the FULL UD-EWT test (2077 sentences, n=1424 gold agent items, the reader's own annotation-free read), 114 (54.6%) are WRONG-ENTITY, 23 (11.0%) are the right entity under a different token of its NAME RUN (the UD first-token-of-a-name convention, `Kori` vs `Schulman`), and 72 (34.5%) are a MODIFIER inside the gold agent's own NP (`The people OF FALLUJAH condemn` -> `Fallujah`), which is a real misread and NOT a convention artifact. On pri 126's own 719-sentence cap the same split is 52 / 16 / 41 of 109, and the cause table reproduces pri 126 EXACTLY (561 items, correct 424 = 0.7558, no_event 3, candidate_set_miss 25, pick_error 109). So the naming convention is ONE ERROR IN NINE, not the story: the brief's hypothesis that most of the 'nearby nominal' errors are wrong-ENTITY picks is CONFIRMED, and a second, larger, previously unnamed bucket is the NP-head choice. THE RE-WEIGHED COMPETITION (bar 2, HALF MET): cue validities ACCRUED FROM READING UD-EWT TRAIN through the live reader (6,000 sentences in the reader's own 20-sentence pseudo-documents, 4,929 gold agent clauses, 29,191 candidate observations), strength(cue value -> AGENT) = log P(agent | voice, cue=value) - log P(agent | voice) with add-alpha counting and Dirichlet shrinkage toward the configuration marginal -- the SAME math `strengths_from_counts` already uses for the coarse role table, replacing the HAND-SET `AGENT_VALIDITIES` dict. LIVE, both arms plus the twin in ONE process, `SituationReader.read` on annotation-free UD-EWT test text (n=1,424 items, 104 pseudo-documents, chunk-paired bootstrap 2,000 resamples): the agent row 0.7900 -> 0.8322, +0.0421 CI95[+0.0237,+0.0627] CI-SEPARATED over the landed competition; WRONG-ENTITY PICK ERRORS 162 -> 135, -0.0190 CI95[-0.0346,-0.0044] CI-SEPARATED DOWN (offline replay of the identical arms: 114 -> 90); the ENTITY-LEVEL column 0.8083 -> 0.8385, +0.0302 CI95[+0.0140,+0.0471]; the info-free twin (the learned strengths permuted within each cue) 0.2640, model-minus-twin +0.5681 CI95[+0.5416,+0.5948] CI-SEPARATED. AGAINST THE WORD-ORDER FLOOR (0.8371, the board's own nearest-pre-verbal-nominal rule on the reader's OWN categories): the landed competition is -0.0471 CI95[-0.0618,-0.0327] CI-SEPARATED BELOW; the re-weighed competition is -0.0049 CI95[-0.0202,+0.0118], i.e. the below-floor defect the brief was opened on is GONE but the row is LEVEL with the floor, not CI-separated ABOVE it -- THAT HALF OF BAR 2 IS NOT MET and this submission is PARTIAL because of it. ON THE COMPETITION'S OWN POPULATION (the reader fired an event AND the gold was on the ballot, n=1,343 -- the decisions the organ actually takes): landed 0.8444 = -0.0290 CI95[-0.0430,-0.0160] CI-SEPARATED BELOW the floor; re-weighed 0.8824 = +0.0089 CI95[-0.0056,+0.0250] ABOVE, not separated. THE REMAINING GAP IS TRACED AND COUNTED, not asserted: of the 61 items where the floor is right and the re-weighed competition is wrong, 15 are `no_event` (the reader fired NO event at the gold verb -- the predicate-slot chain, pri 133, which the brief says to count and not chase), 4 are `candidate_set_miss` (the mention stream, pri 138), 6 are the name-run convention and 6 an NP modifier, leaving 30 genuine wrong-entity losses against 54 genuine wins. SUB-ITEM (bar 5, MET and larger than the brief expected): the passive / by-phrase slice 7/16 -> 13/16 on the full test (the brief scoped this to 3 items at the 719-sentence cap). NO-REGRESS (bar 3, MET): patient 0.6869 and state 0.7989 are BYTE-IDENTICAL across all three live arms (delta +0.0000, CI95[0.0000,0.0000]) -- the change is confined to the agent slot, which is the claim. PLASTIC (bar 4, HALF MET): the table is counts with a live observe path (`observe_agent_outcome`; one comprehended clause grows the counts 29,191 -> 29,290 and moves the strengths) and THE EXPOSURE CURVE on UD-EWT test shows the weights really are read off experience -- 2 clauses read 0.7683 (68 wrong-entity), 5 -> 0.8128, 15 -> 0.8289, 50 -> 0.8271, 200 -> 0.8217, 1000 -> 0.8253, 4,929 -> 0.8289 (35 wrong-entity), with 54 / 15 / 22 / 11 / 7 / 15 decisions changing between consecutive steps. The half NOT met: the brief's own demonstration -- read document 1, observe, and watch document 2's decisions change -- gives ZERO changed decisions, from the shipped table AND from a 960-count cold start, because accruing the reader's OWN settled agent is a FIXED POINT; an online teaching signal has to be an outcome the competition did not itself produce, and the organ has none yet. That is named, not hidden."
floor: "The board's own agent floor, recomputed in place on every population it is quoted against: the nearest PRE-verbal nominal on the READER'S OWN categories -- 0.8371 on the full UD-EWT test (n=1,424), 0.8093 on pri 126's 719-sentence cap (n=561), 0.8734 on the competition's own decided population (n=1,343), 0.7389 on the UD-EWT TRAIN dev slice (n=1,283). The LANDED competition is measured alongside in the same process on each (0.7900 / 0.7963 / 0.8444 / 0.6656) and every delta is quoted against both. The info-free twin, two forms: `within` (each cue's learned strengths re-assigned to its own values by a random bijection -- same availability, same value count, same multiset of strengths, meaning destroyed) 0.2640 live / 0.2640 offline; `across` (the brief's wording -- each cue's table swapped with another cue's; because two cues share no value names every lookup misses and the arm degenerates to 'always the first candidate') 0.5892. The gate is read against `within`, the stronger control."
controls: "(1) INFO-FREE TWIN, both forms, LIVE and offline, CI-separated below on every population (live model-minus-twin +0.5681 CI95[+0.5416,+0.5948]). (2) THE UNGRADED ARM: the same competition with the attachment arm's head belief and the category posterior withheld (both cues fall to the value `na`) scores 0.5948 on the full test, -0.2423 CI-separated BELOW the floor -- so the win is carried by the GRADED upstream reads, not by the re-weighing alone, and the cue that carries it is named (dropping `struct` alone: 0.8322 -> 0.6243). (3) TRAIN / DEV / TEST SEPARATION, enforced by construction: the counts are accrued on UD-EWT TRAIN sentences [0,6000); EVERY arm choice (the cue set, the configuration, the accrual rate) is made on a DEV slice of TRAIN, sentences [6000,7200), that the counts never saw; UD-EWT TEST is read once per reported arm. The dev-chosen arm is {order, govern, struct, cat} under a voice configuration, dev 0.7942 = +0.0553 CI95[+0.0306,+0.0807] CI-SEPARATED above the dev floor. (4) THE ACCRUAL RATE SWEPT, NOT ADOPTED: m_shrink 0.5 / 2 / 8 / 32 / 128 / 512 on dev is a flat plateau (0.7514 / 0.7514 / 0.7514 / 0.7514 / 0.7498 / 0.7482), so 2.0 is kept and the result does not rest on it. (5) THE CONFIGURATION SWEPT ON DEV, three forms (voice; voice x order; voice x order x government) -- all three converge on the SAME decorrelated cue core, and the simplest wins (0.7942 / 0.7872 / 0.7880). (6) TWO CUES BUILT AND REFUTED ON DEV, reported with their numbers rather than deleted: the landed role competition's P(SUBJ) marginalised over the head posterior (`rsubj`, dev 0.7880 -> 0.7794) and the `for X to VERB` infinitival-subject construction as its own government value (dev 0.7942 -> 0.7880). (7) THE EXPOSURE CURVE as a can-fail control on the claim that the weights are learned: a table with 2 clauses of experience scores 0.7683 against the read table's 0.8289. (8) PATCH FIDELITY, in the cell's own `--self-test`: the diff is GENERATED from the cell's ORGAN BLOCK, applied to a COPY of the two target files in a sandbox, both patched files COMPILED, the organ block asserted BYTE-IDENTICAL to the code that was measured, the patched organ IMPORTED, and asked `The company of Fallujah condemned it` -- it answers `company` (the NP head) where the hand-set arm, still reachable for A/B, answers `Fallujah`. hdlab/ is never written. (9) SELF-GATING PROVED: with no asset on disk the patched organ's pick is byte-identical to the landed competition, and HDLAB_AGENT_REWEIGH=0 restores it with the asset present. (10) Chunk-paired bootstrap, 2,000 resamples, resampling the READ UNIT (the pseudo-document), on each population's own items; no floor or twin is pasted across populations."
files_changed: "experiments/exp_agent_pick_reweigh_v1.py (NEW cell: the anatomy + the split, the validity build from reading, the dev arm sweep and backward cue selection, the accrual-rate sweep, the LIVE two-arm gate, the exposure curve, the patch emitter, --self-test 26 checks); verification/test_agent_competition_reweigh_landing.py (NEW witness, green on the tree as it stands AND written to assert the defect's ABSENCE once the diff lands); data/frontend_assets/agent_cue_validities_ud_ewt_v1.json (NEW asset, 6.9 KB: the counts accrued from reading UD-EWT train, plus the strengths rebuilt from them on every load); notes/problems/<slug>/{SOLVED.md, agent_reweigh_patch.diff}. NO hdlab/ or tools/ file is written. The diff touches TWO files: hdlab/graded_role_assigner.py (an `import math`, the 461-line organ block before `__all__`, ONE self-gating branch at the top of `agent_competition_pick_conf`, and the `__all__` additions) and experiments/exp_board_rows_on_the_reader_v1.py (the entity-level column beside the token-level gate). There is exactly ONE call site of `agent_competition_pick_conf` in hdlab/ (situation_reader.py:2357) and NONE in tools/ (enumerated); the branch adds no argument, so every call site is complete by construction. Both target files are CRLF: apply with `git apply --ignore-whitespace`."
reverify: ".venv/Scripts/python.exe verification/test_agent_competition_reweigh_landing.py    (scaffold-free; 17 checks with the arm still in experiments/, 21 once the diff lands -- it detects which tree it is on and says so). Then, for the headline, each writing ONLY into data/exp_agent_pick_reweigh_v1/: .venv/Scripts/python.exe experiments/exp_agent_pick_reweigh_v1.py --self-test (26 checks, ~90s, includes APPLY + COMPILE + IMPORT of the generated patch in a sandbox and the can-fail NP-head behaviour check); --measure --cap 2077 --n-boot 2000 --tag measure (~45 min: the LIVE two-arm gate, all three arms in one process); --anatomy --cap 2077 --tag anat (~12 min: the cause table and the split); --observe --tag obs (~6 min: the observe path and the exposure curve); --build --train-cap 6000 (~25 min: rebuilds the asset from reading, byte-reproducible from the counts). Never a bare run of exp_sealed_modern_holdout_v1.py -- it writes into a landed directory."
---

# The agent competition was weighed by hand. It is now weighed by counting, and the below-floor defect is gone.

**Status: PARTIAL (WIP until `owner_verdict: DONE`).** No `hdlab/` file changed on disk; the exact diff is
`agent_reweigh_patch.diff` in this folder, **generated from the cell's own organ block**, and the cell's
`--self-test` applies it in a sandbox, compiles it, imports it and asks it a question before calling it good.

---

## 1. The bar, restated in my own words

Two jobs. **First**, stop confusing two different mistakes: "the reader named the wrong person" and "the
reader named the right person by the wrong word of their name". They need opposite fixes, and until they are
counted separately nobody knows how big the real problem is. **Second**, fix the weighing: when the reader
decides who did the action, the right answer is usually among the candidates it considered and it picks
another one, so it loses to a rule that just takes the first noun before the verb. Make the wrong-person
mistakes rarer, clearly separated, and get the reader above that rule.

**I met the first job, and half of the second.** Wrong-person picks are down, clearly separated, on the
reader's own read of text it has never seen. The reader is no longer *below* the simple rule — it is level
with it. It is not yet *above* it, and I can tell you exactly which 19 of the 61 remaining losses belong to
two other parts of the system rather than to this one.

## 2. The upstream chain, and the brain-foundational status of each rung as the disk shows it

| rung | organ on disk | what it hands the agent competition | status |
|---|---|---|---|
| tokens -> categories | `hdlab/lexical_categories.py` (count-based, live) | a per-token category POSTERIOR | BF; the competition read it as an ARGMAX until this work |
| lemma | `hdlab/morphology.py` (glass-box morphy / dual-route) | number, for the agreement cue | BF |
| heads | `hdlab/attachment_arm.py` | a GRADED head posterior per token | BF; the competition read a BINARY subject-before flag from `incremental_parser` instead |
| mentions | `hdlab/referent_per_np.py` (+ pri 125 pronoun arm) | the candidate stream | BF in spirit; **57 of 1,424 gold agents never reach the ballot** |
| predicate slot | `hdlab/situation_reader.py` event detection | whether an event fires at all | **24 of 1,424 gold verbs fire no event** -- pri 133 |
| the agent competition | `hdlab/graded_role_assigner.py` | the pick, its margin, its confidence | the Competition-Model OPERATION is PINNED and correct; **its cue WEIGHTS were hand-set**, which is the defect |
| who-did-what row | `sm.events[].agent` | the answer the board scores | -- |

**The defect, stated precisely.** `AGENT_VALIDITIES` is a nine-entry dict of hand-chosen numbers with the
comment *"hand-set from cue validity, NOT trained"*. In the Competition Model a cue's weight **is** its
validity — availability × reliability — **accrued from exposure** (MacWhinney, Bates & Kliegl 1984; Bates &
MacWhinney 1989). A hand-set weight is not a weaker version of that; it is a different object. That is the
one non-brain-foundational component on this rung, and it is what this work replaces.

## 3. THE SPLIT (bar 1), and the method, stated

UD-EWT carries no coreference, so the entity identity available is the **gold dependency structure of the
gold agent token, read only after the reader has answered**:

* **NAME RUN** — the tokens joined to the gold agent head by `flat` / `flat:name` / `compound` / `goeswith`
  in either direction. This is exactly the convention the artifact comes from: UD heads a multi-word name on
  its FIRST token, so `Schulman` in `Kori Schulman` is a different STRING for the same individual.
* **NP** — the gold subtree of the gold agent head.
* A pick inside the name run is **right entity, wrong token**; inside the NP but not the name run it is a
  **modifier of the right entity** (`the South Korean company` → `Korean`) — a real misread of which word
  names the thing; outside both it is a **wrong entity**.

| population | pick errors | wrong entity | right entity, wrong name token | modifier inside the right NP |
|---|---|---|---|---|
| UD-EWT test, pri 126's 719-sentence cap (n=561) | 109 | **52** (47.7%) | **16** (14.7%) | **41** (37.6%) |
| UD-EWT test, FULL (2077 sentences, n=1424) | 209 | **114** (54.6%) | **23** (11.0%) | **72** (34.5%) |

Reported twice more with the stricter convention (only the FIRST occurrence of the model's string counts):
119 / 23 / 67 on the full test. **The naming convention is one error in nine.** The brief's INFERRED
hypothesis — that most of the "nearby nominal" errors are wrong-ENTITY picks — is confirmed, and a second,
larger bucket that the brief did not name is the **NP-head choice**: the reader picks a post-modifier inside
the gold agent's own noun phrase.

**The scorer gains the entity-level column** (`agent_entity_credit` / `entity_level_credit` in the diff), and
it deliberately credits the NAME RUN and nothing else — an NP-internal modifier is still counted wrong, so
the convention fix cannot launder a real misread. **The token-level match remains the gate.**

## 4. What was built, and why each piece is the brain's

**One organ, one arm.** Everything lands inside `hdlab/graded_role_assigner.py`, the Competition-Model role
labeler that already carries the pri 106 / 108 / 111 / 117 / 129 / 134 arms. No second agent picker exists.

1. **The validities are counts from reading.** The counts are accrued by **reading UD-EWT TRAIN through the
   live reader** — the same pseudo-documents, the same mention stream, the same perceived categories, the
   same clause scoping the reader uses at inference — so a cue's availability at build time is its
   availability at read time. 6,000 sentences, 4,929 gold agent clauses, 29,191 candidate observations.
   The strength of cue *c* taking value *x* in configuration *g* (the clause voice) is the contrast
   `log P(agent | g, c=x) - log P(agent | g)`, add-alpha smoothed with Dirichlet shrinkage toward the
   configuration marginal. **Availability and reliability both fall out of that form**: a value seen rarely
   is pulled to the marginal and cannot vote; a value that is nearly deterministic earns a large contrast.
   It is the SAME math `strengths_from_counts` already uses for the coarse role table — one organ, one
   accrual form — and it is a **pure function of the counts**, so the online path and the batch build
   produce the same table from the same experience.
2. **The structure cue reads the attachment arm's graded belief**, not the incremental parser's binary
   subject-before flag: `P(head(candidate) = this predicate)` from `attachment_arm.head_posterior`, binned.
   This is the single strongest cue in the arm (removing it: 0.8322 → 0.6243).
3. **The category posterior is read graded**, not as an argmax: the mass the category organ puts on a
   nominal category at the candidate token, binned. This is the fix for the ADJ-pick pattern, and it is a
   *weight*, not a filter — a confidently-ADJ token loses the competition rather than being deleted from it.
4. **The clause-scope cue** distinguishes `same` / `rel` (the candidate IS the relativizer heading the
   relative clause whose verb this is) / `acrossrel` (a candidate separated from the predicate by an
   intervening relativizer, i.e. outside the embedded clause) / `outside`. The learned contrasts are
   `rel +1.15` and `acrossrel -1.42` — exactly the distant-nominal pattern the brief located, learned
   rather than asserted.
5. **The by-phrase / passive configuration** is learned, not hand-flipped: under `pass` the order cue
   reverses (`post +0.39`, `pre -1.37`), `govern=by` earns `+1.04`, and the nearest post-verbal candidate
   earns `+1.25`. **Passive slice 7/16 → 13/16** (bar 5's sub-item, and larger than the 3 items the brief
   scoped it to, because the full test has 16 passive gold-agent items rather than 3).

**The learned table, `act` configuration (base rate P(agent) = 0.1722 over 28,428 candidates):**

```
order          pre +0.78   post -1.95
nearrank       n0 +1.55  n1 -0.26  n2+ -0.90  p0 -1.55  p1+ -2.13
firstinclause  first +1.09  inclause +0.51  no -1.94
case           nom +1.25  neutral -0.38  nonpron -0.76
govern         free +0.25  by -0.86  prep -2.29
anim           anim +0.62  unk -0.61  inanim -0.88
given          new +0.12  given -0.47
struct         s4 +1.20  s3 +0.05  s2 -0.34  s1 -0.66  s0 -1.48
scope          rel +1.15  same +0.04  outside -0.62  acrossrel -1.42
cat            g3 +0.17  g2 -0.26  g1 -0.97  g0 -3.93
agree          pl_pl +0.83 ... sg_sg +0.18 ... pl_sg -1.35  sg_pl -1.84
vfit           hi +0.21  0 -0.00  mid -0.12  lo -0.48
licensor       l0 +0.60  l1 -0.40  l2 -1.21  l3 -1.43  l4 -2.19
```

This is the Competition Model's English cue hierarchy, **read off counts rather than asserted**: word order
dominant, case marking on pronouns strong, animacy real but small, agreement present and weak and correctly
signed (`sg_pl` −1.84: a singular-marked verb does not take a plural subject), and — the one that contradicts
the landed hand-set table — **`given` is NEGATIVE (−0.47)** where `AGENT_VALIDITIES["salience"]` is +2.0. The
Centering givenness cue as the organ currently computes it (coref-cluster frequency ≥ 2) **anti-predicts**
agenthood on modern UD-EWT. That is a hand-set number that was wrong in sign, found by counting.

## 5. THE NUMBERS (bar 2, 3, 4, 5)

**LIVE, three arms in ONE process, `SituationReader.read` on annotation-free UD-EWT test text**
(2,077 sentences in 104 pseudo-documents, n = 1,424 gold agent items, chunk-paired bootstrap, 2,000 resamples):

| arm | agent | entity-level | wrong-entity picks | patient | state |
|---|---|---|---|---|---|
| **floor** (nearest pre-verbal nominal, reader's own categories) | **0.8371** | — | — | — | — |
| landed competition | 0.7900 | 0.8083 | 162 | 0.6869 | 0.7989 |
| **re-weighed competition** | **0.8322** | **0.8385** | **135** | 0.6869 | 0.7989 |
| info-free twin | 0.2640 | 0.2760 | 939 | 0.6869 | 0.7989 |

| contrast | delta | CI95 | |
|---|---|---|---|
| re-weighed − landed | **+0.0421** | [+0.0237, +0.0627] | **CI-SEPARATED** |
| wrong-entity picks, re-weighed − landed | **−0.0190** | [−0.0346, −0.0044] | **CI-SEPARATED DOWN** ✅ bar 2a |
| entity-level, re-weighed − landed | +0.0302 | [+0.0140, +0.0471] | CI-SEPARATED |
| re-weighed − twin | +0.5681 | [+0.5416, +0.5948] | CI-SEPARATED ✅ the twin loses |
| landed − floor | −0.0471 | [−0.0618, −0.0327] | CI-SEPARATED **BELOW** (the defect) |
| **re-weighed − floor** | **−0.0049** | [−0.0202, +0.0118] | **not separated either way** ❌ bar 2b |
| no-regress patient | +0.0000 | [0.0000, 0.0000] | byte-identical ✅ bar 3 |
| no-regress state | +0.0000 | [0.0000, 0.0000] | byte-identical ✅ bar 3 |

**On the competition's OWN population** — the items where the reader fired an event AND the gold agent was on
the ballot, i.e. the decisions this organ actually takes (n = 1,343): landed 0.8444 = **−0.0290
CI95[−0.0430,−0.0160] CI-separated BELOW** its floor; re-weighed 0.8824 = **+0.0089 CI95[−0.0056,+0.0250]
ABOVE**, not separated.

**Bar 4, plastic.** The table is counts with a live observe path, and **the exposure curve is the
demonstration that survived**:

| clauses read | candidate observations | UD-EWT test | wrong-entity | decisions changed since the previous step |
|---|---|---|---|---|
| 2 | 17 | 0.7683 | 68 | — |
| 5 | 32 | 0.8128 | 41 | 54 |
| 15 | 93 | 0.8289 | 36 | 15 |
| 50 | 331 | 0.8271 | 37 | 22 |
| 200 | 1,280 | 0.8217 | 40 | 11 |
| 1,000 | 7,075 | 0.8253 | 38 | 7 |
| 4,929 | 29,191 | 0.8289 | **35** | 15 |

**And the honest half that is NOT met:** the brief's own demonstration — read document 1, observe, watch
document 2's decisions change — gives **zero changed decisions**, from the shipped 29,191-count table and
from a 960-count cold start alike. **Accruing the reader's own settled agent is a fixed point**: the table is
reinforced toward the argmax it already takes, so its argmax does not move. That is a property of
self-supervised accrual, not a bug in the plumbing (the counts do grow, 29,191 → 29,290, and the strengths do
move — both pinned in the witness). What the online path is missing is a teaching signal the competition did
not itself produce. See NEXT STEPS.

## 6. WHERE THE REMAINING LOSS IS, counted

Of the **61** items where the word-order floor is right and the re-weighed competition is wrong:

| cause | n | whose |
|---|---|---|
| `no_event` — the reader fired no event at the gold verb, so the row scores 0 while the floor still names a noun | **15** | the predicate slot, **pri 133** (the brief: count it, do not chase it) |
| `candidate_set_miss` — the gold agent never reached the ballot | **4** | the mention stream, **pri 138** |
| the name-run convention | 6 | the scoring convention (the entity column already credits these) |
| a modifier inside the right NP | 6 | this organ |
| genuine wrong-entity | **30** | this organ |

Against **54** items where the competition is right and the floor is wrong. **19 of the 61 losses belong to
two other rungs.** The reachable ceiling given the candidate stream as it stands is **0.9431** (1,424 − 24
`no_event` − 57 `candidate_set_miss`). If the predicate slot fired on all 24, the agent row would gain up to
**+0.0169** with no change to this organ — which on its own would put it above the floor.

**The 30 genuine losses, researched until named.** Two constructions dominate them:
* **object-gap reduced relatives** — `the Master draft we discussed`. The attachment arm gives `draft` a high
  belief that it attaches to `discussed` (it does — as its OBJECT), and the `struct` cue reads *attachment*,
  not *relation*, so it cannot tell a subject arc from an object arc.
* **infinitival and absolutive subjects** — `for me to sit in with you`, `for Iraqis to take part`,
  `with Jeff making the call`. English marks the subject of an infinitival clause with `for` + accusative, so
  the same surface preposition that marks an oblique marks a SUBJECT here; `govern=prep` (−2.29) and
  `case=acc` both push the right answer down.

**I built the fix for each and both were REFUTED on dev** (section 7). They are real leads, not dead ends;
what is refuted is these two forms of them.

## 7. NEGATIVES, each researched until understood

| built | dev result | why, understood |
|---|---|---|
| `rsubj` — the landed role competition's P(SUBJ) (P(BY_AGENT) under passive) marginalised over the head posterior, read graded | 0.7880 → **0.7794** | `coarse_role_posterior` is itself an additive competition over head-class × order, case and preposition — **the same evidence this competition already reads**. It is not an independent cue; it is the same measurement passed through a second softmax, so adding it double-counts. **A cue must be a new measurement of the world, not a re-reading of one already taken.** |
| `for_to` — `for X to VERB` / `with X VERBing` given its own government VALUE | 0.7942 → **0.7880** | The value learned the right sign (−0.10 against `prep`'s −2.45) but the split costs more elsewhere than it buys. The construction detector fires on `of`-governed nominals it should not; the lead is right, this detector is not. |
| `licensor` — the graded belief that the candidate is licensed by ANOTHER NOMINAL (pri 108's finding read as a cue) | 0.7942 → 0.7818 added to the chosen arm | Redundant with `struct`: both read the same head posterior, from opposite sides. It stays in the TABLE (accrued, learned, correctly signed: `l4 −2.19`) but does not vote. |
| `agree`, `anim`, `case`, `given`, `vfit`, `nearrank`, `firstinclause`, `scope` | each removal helps on dev | **The integrator, not the cues.** See below. |
| the accrual rate, swept 0.5 → 512 | flat (0.7514 … 0.7482) | with 29,191 observations, shrinkage cannot silence a cue value that has thousands of counts. The redundancy is structural, not a smoothing failure. |
| the configuration, three forms | voice 0.7942 / voice×order 0.7872 / voice×order×government 0.7880 | all three converge on the SAME four-cue core, so the core is a property of the cues, not of one configuration. |

**The finding under all of those, and it is the most useful thing in this submission.** The additive
log-odds integrator is exact only for *conditionally independent* cues. Add the twelve marginal validities
and two cues that carry the same variance each re-count it, so the whole Competition-Model inventory scores
*worse* than a decorrelated subset of it. **The Competition Model's own connectionist simulations do not have
this problem, because they learn the weights by error-driven competition (a delta rule), which is precisely
how overlapping cues get their credit discounted — that is cue competition, i.e. blocking and overshadowing,
in the associative-learning sense.** A pure COUNTS table cannot do that, and the brief bars a fitted
classifier. So the overlap is handled by which cues enter, decided on dev — and **that is the honest limit of
the count form.** It is named here rather than smoothed over, and it is the single clearest candidate for a
follow-on brief (section 9).

## 8. What the diff does, and why it is complete on the shipped path

* `hdlab/graded_role_assigner.py`: `import math`; the 461-line organ block placed before `__all__`; the
  `__all__` additions; and **one self-gating branch** at the top of `agent_competition_pick_conf` — if
  `AGENT_REWEIGH` (default on, `HDLAB_AGENT_REWEIGH=0` restores the old behaviour byte-identically) and the
  caller supplied no weights of its own and the learned asset is on disk, the competition is decided by the
  learned contrasts. Same argmax, same `(pick, margin, conf)` return shape.
* **There is exactly ONE call site of `agent_competition_pick_conf` in `hdlab/`** (`situation_reader.py:2357`)
  **and NONE in `tools/`** — enumerated, not recalled. The branch adds no argument, so every call site is
  complete by construction and nothing outside this one organ changes. `situation_reader.py`, `coref.py`,
  `entity_resolver.py` and `goal_register.py` are untouched (pending landings).
* `experiments/exp_board_rows_on_the_reader_v1.py`: `_name_run_forms` plus the `entity_level_credit` column
  beside `instrument_span_credit`. The row's `model_acc` — the strict head match — **remains the gate**.
* `hdlab/attachment_arm.py` and `hdlab/lexical_categories.py` are **read, never written**: the new graded
  cues call `head_posterior` and `tagger().tag_with_posterior` through cached per-sentence helpers inside the
  organ.
* pri 134's non-argument arm (`RUN_MEMBERS` off) is not touched; the diff applies on it (`git apply --check`
  passes, verified in the self-test).

**Cost.** The live re-weighed read is about 15% slower than the landed one (602 s → 693 s for 104
pseudo-documents) because the attachment arm's head posterior is computed per sentence for this cue. The
reader already computes a parse for the same sentence; a follow-on can share it rather than recompute.

## 9. KEY REALIZATIONS

1. **The naming convention was a decoy, and counting it is what showed that.** The brief reasonably suspected
   the two commonest patterns were partly a scoring artifact. They are not: 11% of pick errors. The bucket
   nobody had named — *a modifier inside the gold agent's own noun phrase* — is three times bigger.
2. **Read the upstream organs' beliefs, not their answers.** Withholding the attachment arm's graded head
   posterior and the category posterior (the "ungraded" arm) costs 0.8322 → 0.5948. The re-weighing is the
   frame; **the graded upstream reads are the content.** This is the same lesson as pri 129's graded patient
   reliability, now on the agent rung.
3. **A cue must be a new measurement, not a second reading of one already taken.** `rsubj` felt like the
   obvious next lever — one organ reading another organ's graded output — and it lost, because the organ it
   reads is computed from the same evidence. That test is cheap and should be run before any cue is added.
4. **A hand-set weight can be wrong in SIGN, and only counting finds it.** `salience` is +2.0 in the landed
   table; counted from reading, givenness is −0.47.
5. **Self-supervised accrual is a fixed point.** Observing your own answer cannot change your answer. Any
   online learning path for a decision organ needs an outcome the organ did not produce.
6. **Score the organ on the population it decides on.** The whole-row number mixes in 24 clauses where the
   reader fired no event and 57 where the gold never reached the ballot; on the 1,343 decisions this organ
   actually takes the story is cleaner and the attribution honest.
7. **Generate the patch from the measured code.** The first draft inserted the block *inside* the `__all__`
   list literal and the patched organ would not compile — `git apply --check` passed anyway. Only
   apply-then-COMPILE-then-IMPORT caught it. That check is now in the self-test.

## 10. THE PREDICTION for the sealed holdout (recorded BEFORE the read, per bar 6)

Sealed HOLDOUT_V1 (UD_English-PUD, n = 806, 806 active / 0 passive; pri 126): correct 510 = **0.6328**,
`no_event` 25, `candidate_set_miss` 42, `pick_error` 229; floor **0.7171**.

On the full UD-EWT test the re-weighed competition converted **51 of 209 pick errors (24.4%)** with no
correct item lost (pick errors 209 → 158, accuracy +0.0359 = +51 items — the two match exactly). Applying the
same conversion rate to the sealed set's 229 pick errors:

* **Point prediction: sealed agent accuracy 0.700** (510 + 56 = 566 of 806).
* **Interval: 0.68 to 0.73.** The sealed set is translated newswire (PUD), a different register from UD-EWT's
  web text, and its pick-error share is higher (28.4% of items vs 14.7%), so the conversion rate could run
  either way. The lower bound assumes a 15% conversion, the upper a 35% conversion.
* **Against the sealed floor (0.7171): I predict the row is still BELOW it**, with the gap narrowing from
  −0.0844 to about **−0.017**, most likely NOT CI-separated in either direction.
* **Wrong-entity pick errors on the sealed set: I predict a fall of 15–25%** of the wrong-entity share.
* **The sealed `no_event` residual is 25 items (3.1%)** — proportionally twice UD-EWT's 1.7% — so I expect a
  larger share of the sealed shortfall to belong to pri 133 than it does on UD-EWT.

## 11. ADJACENT COMPONENTS, capabilities and limitations (seeds for the next briefs)

| component | what this work showed about it | brain-foundational status |
|---|---|---|
| `attachment_arm.head_posterior` | carries this whole result; its graded read is worth 0.23 accuracy on this rung | BF; **but it cannot say what RELATION an arc is**, which is the object-gap failure |
| `lexical_categories` posterior | a graded read is worth +0.0281 on the chosen arm | BF; it was being consumed as an argmax |
| `referent_per_np` mention stream | 57 of 1,424 gold agents never reach the ballot; 72 pick errors are the NP-HEAD choice inside a span it opened | **the largest single lever left on this rung** -- pri 138 |
| the predicate slot (event detection) | 24 gold verbs fire no event; 15 of the 61 floor losses | pri 133 |
| `coarse_role_posterior` | refuted as a cue here, for a reason worth carrying: it re-reads this competition's own evidence | BF but NOT an independent signal |
| `AGENT_VALIDITIES["salience"]` = +2.0 | counted from reading, givenness is **−0.47** on modern text | a hand-set number that is wrong in sign |
| `hybrid_agent_pick` / `agent_override_*` | untouched; it still consumes the hand-set table | should be re-pointed at the learned one, or retired |

## 12. WHAT I WOULD WITHDRAW FIRST if it turned out to be wrong

The **cue SUBSET**. Four of the Competition Model's cues vote and eight do not, chosen by backward
elimination on a 1,283-item dev slice. The choice is stable across three configurations and the four
survivors are the decorrelated ones, but a 1,283-item dev is not a lot, and on the full test the *all-cue*
arm scored 0.8336 with 76 wrong-entity errors against the dev-chosen arm's 0.8322 with 90 — i.e. **the
dev-chosen arm is not the best arm on test**, and I am reporting the dev-chosen one because that is the
protocol. If the subset is wrong, the honest fallback is the full inventory with a delta-rule integrator
(section 13), not a different subset.

Second: the **live landed baseline moved between two runs of the same code** (0.7963 in the offline capture,
0.7900 in the live gate — 9 items). Both runs read the same text with the same reader; the difference is the
process-shared passage state in `lexical_categories` that pri 111 documented. Every contrast in the headline
table is computed **within one process**, so it is unaffected, but the absolute landed number carries that
±9-item uncertainty and should not be quoted on its own.

## 13. NEXT STEPS, in priority order

1. **A delta-rule integrator for the one cue-competition engine** (this is the real follow-on, and it is
   pri 143's territory — "one cue-competition engine, five arms"). MacWhinney's own Competition Model
   simulations learn cue strengths by error-driven competition, which is what discounts overlapping cues.
   The counts stay; what changes is that the strength is updated by prediction error rather than read off a
   marginal. That is *more* brain-foundational than the marginal form (Rescorla-Wagner competition is the
   pinned associative-learning rule), it would let the full Competition-Model inventory vote, **and it gives
   bar 4 the teaching signal it is missing** — the error, not the reader's own answer. Ask the owner whether
   an error-driven count update crosses the "never a fitted classifier" line; I read it as the brain's rule
   rather than a fit, but that is the owner's call, not mine. **This is the specific board question.**
2. **The NP-head choice in the mention stream** (pri 138). 72 of 209 pick errors are a modifier inside the
   gold agent's own NP; the competition already halves them, but the right fix is that a span should offer
   its HEAD to the competition, not every nominal inside it.
3. **A relation-aware structure cue.** The attachment arm's belief plus the *labelled* arc — but read from a
   source that is not this competition's own evidence. The arc labeler's own graded output, or the arm's
   second-order sibling factorisation, are the candidates.
4. **Re-point `hybrid_agent_pick` and `agent_override_licensed`** at the learned table, or retire them: they
   still consult the hand-set weights.
5. **Share the parse.** The reader computes a head posterior for the sentence already; the cue recomputes it.
   Worth about 15% of read time.
6. **Re-run the GUM board rows.** This cell's no-regress covers UD-EWT patient/state (byte-identical); the
   goal, affect and who-has-what rows read the agent and live on GUM, and were NOT measured here.

---

## SUBMISSION PROMPT

```
Problem: the agent competition loses with the right answer on the ballot -- 77 to 80 percent of agent
errors on sealed and test text are pick errors; split wrong entity from wrong name token, then reweigh
the cues  (pri 140)

Status: PARTIAL.

THE SPLIT (bar 1, met): on the full UD-EWT test (2,077 sentences, n=1,424, the reader's own
annotation-free read) the 209 pick errors are 114 WRONG-ENTITY (54.6%), 23 right-entity-wrong-NAME-TOKEN
(11.0%) and 72 a MODIFIER inside the gold agent's own NP (34.5%).  The naming convention is one error in
nine, not the story; the big unnamed bucket is the NP-head choice.  pri 126's cause table reproduced
exactly at its own 719-sentence cap (424/561, no_event 3, candidate_set_miss 25, pick_error 109).  The
board scorer gains an entity-level column that credits the gold NAME RUN and nothing else; the token-level
match stays the gate.

THE RE-WEIGH: the hand-set AGENT_VALIDITIES dict is replaced by cue validities ACCRUED FROM READING
UD-EWT train through the live reader (4,929 clauses, 29,191 candidate observations), same counts->log-odds
math the coarse role table already uses, with the structure cue reading the attachment arm's GRADED head
belief and the category rung read graded instead of as an argmax.  LIVE, three arms in ONE process:
agent 0.7900 -> 0.8322 (+0.0421 CI95[+0.0237,+0.0627] CI-sep); wrong-entity pick errors 162 -> 135
(-0.0190 CI95[-0.0346,-0.0044] CI-SEPARATED DOWN); entity-level 0.8083 -> 0.8385; twin 0.2640
(+0.5681 CI-sep); patient and state byte-identical.  Against the word-order floor 0.8371 the landed
competition is -0.0471 CI-SEPARATED BELOW and the re-weighed one is -0.0049 [-0.0202,+0.0118]: the
below-floor defect is GONE, the row is LEVEL with the floor, NOT above it CI-separated -- that half of
bar 2 is not met, which is why this is PARTIAL.  On the competition's own decided population (n=1,343)
it goes -0.0290 CI-sep below -> +0.0089 above, not separated.  Passive/by-phrase slice 7/16 -> 13/16.

TRACED, not asserted: of the 61 items the floor wins and we lose, 15 are no_event (the predicate slot,
pri 133), 4 are candidate-supply (pri 138), 12 are convention/NP-modifier, 30 are genuine -- against 54
genuine wins.  Ceiling given the candidate stream 0.9431.

NEGATIVES, each understood: the labels rung read graded as a cue (rsubj) LOSES because it re-reads this
competition's own evidence through a second softmax; the `for X to VERB` construction value loses; the
accrual rate is flat 0.5-512.  The finding under them: additive marginal log-odds double-counts correlated
cues, so the full Competition-Model inventory scores worse than a decorrelated subset -- the model's own
simulations avoid this with an error-driven (delta-rule) weight competition, which a counts table cannot
do.  Named as the follow-on and as the board question.

PLASTIC: exposure curve on UD-EWT test 2 clauses read 0.7683 -> 15 clauses 0.8289 -> 4,929 clauses 0.8289
with 35 wrong-entity, decisions changing at every step.  The brief's own two-document probe gives ZERO
changed decisions, because accruing the reader's own settled agent is a fixed point -- reported, not hidden.

SEALED PREDICTION (recorded before the read): 0.700, interval 0.68-0.73, still BELOW the sealed floor
0.7171 with the gap narrowing from -0.0844 to about -0.017 and probably not CI-separated either way.

Files: experiments/exp_agent_pick_reweigh_v1.py, verification/test_agent_competition_reweigh_landing.py,
data/frontend_assets/agent_cue_validities_ud_ewt_v1.json, notes/problems/<slug>/{SOLVED.md,
agent_reweigh_patch.diff}.  No hdlab/ or tools/ file written; the diff touches
hdlab/graded_role_assigner.py (one self-gating branch, one call site in hdlab/, none in tools/) and the
board scorer.  Reverify: .venv/Scripts/python.exe verification/test_agent_competition_reweigh_landing.py
```

---

## 14. THE OWNER'S PUSH SCRIPT, answered with numbers

**(i) Performance vs the brain at each rung, and where the signal is lost.** A competent reader identifies
the agent of an ordinary English clause essentially without error; the organ's ceiling *given the candidate
stream it is handed* is **0.9431** (1,424 items minus 24 clauses where no event fires minus 57 where the gold
agent never reaches the ballot), and it reaches **0.8322** of that. So the loss splits: **4.0% of items the
mention stream never offers** (`referent_per_np`, pri 138), **1.7% where no event fires** (the predicate slot,
pri 133), **11.1% where the competition picks the wrong candidate**. Within that last 11.1%, 6.3% are a
different entity and 4.2% a modifier inside the right entity's noun phrase.

**(ii) Every wall researched and prototyped past.** Four prototypes were built after the first arm cleared:
the labels rung read graded (`rsubj`), the `for X to VERB` construction as a case value, the nominal-licensor
cue, and a richer configuration (voice × order × government). All four are measured on dev with numbers in
§7; three lose and one ties. **None of them is a heuristic**: each is a counts-learned cue value in the same
table, and each is reported with the reason it lost. The learned/graded form of the two that still matter is
named in §13 items 1 and 3.

**(iii) Is wiring alone sufficient — the upstream gap with its number.** No. The re-weighing plus the graded
upstream reads move the row **+0.0421 CI-separated** and remove a **−0.0471 CI-separated** below-floor defect,
and that is where wiring runs out: **19 of the 61 remaining losses to the floor belong to two other rungs**
(15 `no_event`, 4 candidate-supply), and the largest single remaining bucket — **72 pick errors that are a
modifier inside the gold agent's own NP** — is a *span-head* question in `referent_per_np`, not a weighting
question here. Fixing the predicate slot alone is worth up to **+0.0169** with no change to this organ.

**(iv) Every table has an observe path.** `observe_agent_outcome` is live and the strengths are a pure
function of the counts, so the batch build and the online path produce the same table from the same
experience; the exposure curve (§5) shows a table with 2 clauses of experience scores 0.7683 and a read one
0.8289. **The half that is missing is named**: the teaching signal. Self-supervised accrual is a fixed point.

**(v) State of the art on this rung, and the glass-box lever.** The strongest reference *on disk* is the
retired supervised labeler (**0.7081** on pri 134's non-argument population, beaten by the counts arm's
0.7622) and the coarse role competition read at **gold heads** (pri 108: core-role recall **0.9198**) against
**0.5774 → 0.7061** at live heads. The pattern is consistent and it names the lever: **the gap to a supervised
system on this rung is the HEADS rung, not the role competition** — this work's single strongest cue is the
attachment arm's graded head belief (removing it: 0.8322 → 0.6243), so improving the arm improves the agent
row directly. The glass-box lever is therefore the arm's second-order / relation-aware arc quality
(§13 item 3), not a better weighting.

**(vi) My negatives audited for false negatives.** Each was re-run in a form that could have rescued it:
`rsubj` was tested alone, added to the chosen arm, and with the arm reduced to three cues (0.6485 — worse
still); the cue-set choice was re-derived under **three** configurations rather than one; the accrual rate was
swept over three orders of magnitude; the plasticity probe was re-run from a **960-count cold start** before
being reported as a fixed point; and the exposure curve's first run looked flat (0.8307 at 25 clauses) until
it was re-run from **2** clauses, where it became a real learning curve. One negative did change verdict under
audit: the first version of the exposure curve asserted improvement and failed; the honest version measures
saturation and passes.

**(vii) Prior work on disk, read before building.** pri 106 (the `ppc` cue and `role_decision`), pri 108 (the
NMOD class and cue set v4), pri 111 (the clause-local voice cue, and the `_ALL` / call-site enumeration
method reused here), pri 117 (the copular subject), pri 129 (patient reliability from the competition), pri
134 (the non-argument arm, `RUN_MEMBERS` off — the diff applies on it and does not touch it). The
`agent_hybrid` / `agent_hybrid_construction` flags were **not** re-tried (measured worse, 2026-09-16).

## 15. FLIPS AND OPEN ITEMS FOR STRATEGY AT LANDING

1. **`verification/test_byhead_agent_cue_landing.py` will need re-pinning.** At HEAD it is **14/15**, and the
   one failure is **pre-existing** (`byhead changes only a negligible fraction of board answers` — changed
   11/853 = 1.29% against a ~1% threshold; `hdlab/` is untouched by this work, so nothing here caused it —
   and a numeric threshold like that is the kind of pin the standing rule calls a witness defect). It will
   also go **vacuous** once the diff lands: `agent_competition_reweighed` never calls `agent_supports`, so
   `byhead_agent_cue` is structurally unused on the re-weighed path (grep-verified, one line). The by-phrase
   evidence is not lost — it is carried by `govern=by` (+1.04) and `nearrank=p0` (+1.25) in the `pass`
   configuration, and the passive slice goes **7/16 → 13/16** — but the witness's byhead-ON-vs-OFF assertions
   will compare two identical arms. Re-pin it to the `pass` configuration's own contrasts, or to the passive
   slice.
2. `verification/test_cmrole_agent_struct_organ.py` **ALL PASS** and `verification/test_coarse_role_competition.py`
   **37/37** at HEAD, both run first-hand.
3. **`hybrid_agent_pick` / `agent_override_licensed` still read the hand-set table.** They are default-off on
   the reader, so nothing regresses, but they are now the only consumers of `AGENT_VALIDITIES`.
4. **The GUM rows were not measured.** The no-regress here is UD-EWT patient/state (byte-identical). The goal,
   affect and who-has-what rows read the agent and live on GUM; strategy should re-run them before landing.
5. **Read cost +15%** (602 s → 693 s for 104 pseudo-documents) because the attachment arm's head posterior is
   recomputed for this cue; the reader already computes a parse for the same sentence.
