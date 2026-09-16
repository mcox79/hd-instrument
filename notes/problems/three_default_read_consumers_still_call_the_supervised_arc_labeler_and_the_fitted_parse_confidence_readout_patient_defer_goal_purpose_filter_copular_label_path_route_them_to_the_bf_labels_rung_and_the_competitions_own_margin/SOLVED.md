---
problem: three_default_read_consumers_still_call_the_supervised_arc_labeler_and_the_fitted_parse_confidence_readout_patient_defer_goal_purpose_filter_copular_label_path_route_them_to_the_bf_labels_rung_and_the_competitions_own_margin
status: SOLVED
bar: "The probe witness green on 16 documents (no NOT_BF import during a default read); patient / agent / state rows not down full size (or the consumer repair named with items); the goal witnesses not down; the two stand-ins used by no live consumer (grep-level) -- OR a numbered located negative naming the consumer that cannot read the competition and why."
result: "EVERY LEG MET, AND THE BRIEF'S CONSUMER LIST WAS INCOMPLETE -- the probe on 16 modern GUM documents finds FIVE call sites, not three, and the FIRST importer (`_commonnoun_appos_map`) is one the brief does not name. (1) NO-REGRESS IS EXACT: 16 GUM documents + 400 UD-EWT sentences (20 chunks) through the LIVE SituationReader.read on annotation-free text, BOTH ARMS IN ONE PROCESS -- who_did_what_agent 0.7147 -> 0.7147 (n=389), who_did_what_patient 0.6977 -> 0.6977 (n=301), state 0.7500 -> 0.7500 (n=84), salience 0.3125 -> 0.3125 (n=16); every paired delta EXACTLY 0.0000 with CI [0.0000, 0.0000], and the read is 15.0% FASTER (571.7s -> 485.9s for the same 36 reads, three private supervised asset loads and 1,250 perceptron label calls gone). (2) THE DEFER IS BETTER, NOT MERELY EQUAL: on the whole UD-EWT test set (n=1247 patient items the live chain decides, 872 sentences, blanket accuracy 0.8148) the competition's own patient belief x its object-slot competition separates the reader's RIGHT from WRONG patient decisions at AUC 0.8127 [0.7807, 0.8455] against the frozen fitted logistic's 0.7613 [0.7227, 0.7994] -- paired over sentences +0.0515 CI95 [+0.0166, +0.0881] half=0.0357, CI-SEPARATED -- with the permuted twin at chance (0.5011) and selective accuracy at 50% coverage 0.9470 vs 0.9133. (3) THE BRIEF'S PROPOSED FIX IS REFUTED AND REPLACED BY A BETTER ONE: the competition's MARGIN is at chance for this decision (AUC 0.4962, its count-calibrated reliability 0.4827; paired -0.2652 CI95 [-0.3385, -0.1909], CI-separated BELOW the readout it was proposed to replace) because a large margin can mean confidently-OBL; reliability belongs to the decision the CONSUMER reads, which is the PATIENT-CLASS belief contested for one slot. (4) THE COPULAR PATH IS LOAD-BEARING AND THE REPLACEMENT IS NOT DOWN: 377 gold predicational states on UD-EWT test, read-back recall from the predicate slot 0.7958 vs the perceptron's 0.7905 (+0.0052 CI95 [+0.0000, +0.0134]) with FEWER pairs emitted (429 vs 451), while DROPPING the path is -0.0106 CI95 [-0.0214, -0.0026], CI-separated DOWN -- so the perceptron was doing real work and had to be replaced, not cut. (5) THE LARGEST CALL SITE'S PERCEPTRON OUTPUT IS PROVABLY DISCARDED: structural_patient_pick (620 of 1,468 label calls on four documents) reads only obj / nsubj:pass, both already decided by the Competition-Model overlay -- substituting the organ directly gives 2175/2175 IDENTICAL matrix-verb patient picks over the whole UD-EWT test set (10 tokens of ~25k carry an obj/nsubj:pass label the competition does not emit; none is any matrix verb's chosen patient). (6) THE GOAL PURPOSE FILTER REACHES PARITY: a new PURPOSE arm of the same competition (cue validities accrued from UD-EWT train counts, tau and cue set selected on a train-internal dev split) scores 0.6589 on UD-EWT test against the perceptron deprel filter's 0.6822 -- paired -0.0235 CI95 [-0.1145, +0.0630], separated in NEITHER direction -- over a majority floor of 0.6202, a never-reject floor of 0.3798 and a same-rate random twin at 0.5116, agreeing with the shipped filter on 0.7597 of decisions -- AND THE PARITY IS AN UPSTREAM LOSS, NOT A WEAK MECHANISM: with GOLD heads feeding its two arc-derived cues the SAME arm scores 0.7907, paired +0.1084 CI95 [+0.0157, +0.2031] CI-SEPARATED ABOVE the supervised deprel filter, and the attachment arm's head of the infinitival verb is wrong on 418 of 1,395 sites (30.0%). (7) AND AN AST AUDIT OF THE PATCHED SOURCES CAUGHT A DEFECT IN MY OWN PATCH: a live `from hdlab.parse_confidence import defer` left in the reader's defer branch, invisible to the runtime probe because the default tau is None, which would have re-imported a NOT_BF module the instant the defer was flipped on (next step 3) -- fixed by moving the opt-out to the organ that produces the confidence (graded_role_assigner.defer_below); after the fix exactly ONE import of either module remains anywhere, in a function this patch leaves with no caller. (8) THE PROBE IS THE WITNESS: verification/test_no_not_bf_organ_on_the_default_read.py reproduces the defect, proves it can fire by detecting a PLANTED NOT_BF import, and turns binding the moment the residual is empty. (9) THE IS-A MAP IS DEAD AT THE INSTRUMENT (phase 7: it moves 14 of 2,372 resolution records, none of them scored -- 'dead at the instrument', NOT 'provably inert'): on 8 GUM documents with the reader's own role-mention snapshot, common_noun_coref scores 0.4903 on 155 anaphoric common-noun mentions IDENTICALLY whether the map is the shipped perceptron recipe, the copula-only BF read, or EMPTY (paired 0.0000 CI [0.0000, 0.0000] for both comparisons, every floor and twin identical) -- so retiring its apposition half is measurably free and the whole map is a deletion candidate; the GUM-only read is 36% faster (269.9s -> 172.6s)."
floor: "Each floor recomputed on its arm's OWN population, all arms in one process. PATIENT DEFER: the shipped consumer as it ships -- hdlab.parse_confidence.calibrated_patient_confidence over the live attachment-arm conf/marg -- AUC 0.7613 [0.7227, 0.7994] (n=1247); also run and BEATEN: the competition's margin 0.4962, its count-calibrated margin-reliability 0.4827, the attachment arm's own Matrix-Tree marginal 0.4728 (all at chance), the competition's patient belief WITHOUT the slot competition 0.7861. COPULAR: the shipped `cop`-label detection 0.7905 read-back recall (n=377 gold predicational states) AND the can-fail arm of dropping the label path entirely 0.7798. GOAL: the shipped perceptron deprel filter 0.6822 (n=129 decidable sites), the majority-class floor 0.6202, the never-reject floor 0.3798. IS-A MAP: the shipped perceptron appos+cop recipe, recall 0.3095 / precision 0.2562 (168 gold edges, 1251 sentences). BOARD ROWS: the shipped reader itself, item-identical."
controls: "(1) INFORMATION-FREE TWINS, one per arm, each LOSING: the BF patient confidence permuted across items scores AUC 0.5011 (chance) against the real 0.8127, and the shipped logistic permuted scores 0.5186; the goal filter's same-rate random twin scores 0.5116 against 0.6589/0.6822; the board's own per-row twins are unchanged (patient 0.1595, agent 0.2416, state 0.7024). (2) A CAN-FAIL ARM ON EVERY REPLACEMENT, not just a comparison: the copular path is measured DROPPED as well as replaced, and dropping it loses CI-separated (-0.0106 [-0.0214,-0.0026]) -- had it been flat, the honest answer would have been deletion, not replacement. (3) THE WITNESS CANNOT PASS VACUOUSLY: W0 plants an import of a registry-NOT_BF module inside the probed window in a CHILD process and asserts the probe sees it. (4) THE PROBE METHOD ITSELF IS CONTROLLED: a builtins.__import__ hook MISSES `from hdlab import parse_confidence` (that call passes the name 'hdlab'), so the probe is a sys.meta_path finder; the hook-based version under-reported parse_confidence and was discarded. (5) BOTH ARMS IN ONE PROCESS for every comparison; the bootstrap unit is the population's own (the sentence for UD items, the document/chunk for board rows). (6) TAU AND CUE SET FOR THE PURPOSE ARM SELECTED ON A TRAIN-INTERNAL DEV SPLIT (every 5th train sentence, n=250), never on test -- the first prototype selected tau on test and read 0.6977; the honest dev-selected number is 0.6589. (7) TWO QUALITY-PUSH LEVERS BUILT AND MEASURED AGAINST THEMSELVES, both understood: a THIRD factor (the verb's stored valency expectation) is CI-separated DOWN (-0.0196 [-0.0374,-0.0011]) because the population is gold patient items where every verb has an object by construction, so the cue is constant-true and only adds noise -- it belongs to the verb_subcat_gate decision, not to this one; and the GRADED CATEGORY hand-off (coarse_role_posterior_tagmarg) is flat (0.8073 vs 0.8127, -0.0054 [-0.0214,+0.0106]) because nominals are tagged near-certainly, exactly as the organ's own docstring predicts for a near-certain upstream rung. (8) THE IS-A NEGATIVE DIAGNOSED BY COUNTING, NOT NARRATED: the arc-free apposition construction recovers 17 of 105 gold appositions against the perceptron's 28 (-0.0592 CI95 [-0.1386,+0.0199], NOT separated) at precision 0.0972 vs 0.2562; counting the gold shapes shows only 24 of 105 carry a comma at all, and an ORACLE-ARC arm on gold heads recovers 15 -- so the residual is the SCHEMA, not the heads rung."
files_changed: "experiments/exp_labels_rung_to_live_consumers_v1.py (NEW -- the cell; 8 arms, 17/17 self-test). verification/test_no_not_bf_organ_on_the_default_read.py (NEW -- the import-probe witness, pytest-collectable with the pri-128 wrapper). notes/problems/<slug>/labels_rung_consumers_patch.diff (NEW -- the proposed hdlab change: 12 hunks across 5 files, `git apply --check --ignore-whitespace` CLEAN against the current tree with pri 125 applied; every patched file COMPILES under an in-memory application). data/exp_labels_rung_to_live_consumers_v1/purpose_complement_validities_ud_ewt.json (NEW asset the cell builds; strategy copies it to data/frontend_assets/ at integration -- the verb_subcat_frames precedent; with the asset ABSENT the purpose arm abstains and the filter falls through exactly as an unlabeled deprel did, so the patch is safe to land before the copy). NO hdlab/ or tools/ file written: every arm is installed by rebinding attributes on the reader INSTANCE (and one module function) inside the cell's process."
reverify: ".venv/Scripts/python.exe experiments/exp_labels_rung_to_live_consumers_v1.py --self-test   # 17/17 ON THE TREE AS IT IS, patched or not: S5 detects from the LIVE modules whether the patch is landed (patch_is_landed(): patient_slot_confidence + defer_below on the competition organ, _purpose_deprels on the reader) and asserts accordingly -- on an UNPATCHED tree it asserts the DEFECT (a NOT_BF module imported during a default read, a call-site table with more than the brief's three consumers); on the LANDED tree it asserts the ABSENCE (zero NOT_BF imports during read, an EMPTY call-site table), labelled [landed]. A check that can only pass before the fix is not a reverify. The other 15 are tree-independent: the BF patient confidence ranks the object above the subject, the predicate slot finds the copular predicate with no labeler, observing outcomes MOVES the purpose arm (online plasticity), the AUC/bootstrap helpers, and the 2175/2175 pick identity on a sample.  THEN: .venv/Scripts/python.exe verification/test_no_not_bf_organ_on_the_default_read.py --docs 16   # the probe witness (W0 plants a NOT_BF import in a child process to prove it can fire).  The measurement arms, each writing only to its own directory: --patient --state (UD-EWT test, ~4 min), --goal --isa (~4 min), --probe --identity (~12 min), --infin (~2 min), --isadead (~7 min), --defer --ud-cap 400 (~7 min), --rows --gum-docs 16 --ud-cap 400 (~40 min, both arms one process), --goal --rows --gum-docs 8 --ud-cap 0 (~17 min, THREE arms one process -- the is-a load-bearing test).  On disk: metrics.json, metrics_patient.json, metrics_isa_goal.json, metrics_gumrows.json, metrics_infin.json, metrics_isadead.json, metrics_defer.json."
---

# SOLVED — the default read no longer needs the supervised relation labeler or the fitted confidence readout

## Status in one line

A default, annotation-free read of a modern GUM document loaded **three separate copies of a frozen supervised
relation labeler** and called a **frozen fitted logistic** 218 times, and the brief named **three** of the five
consumers doing it. All five are routed to the ONE Competition-Model role organ and to the predicate slot;
**every board row is byte-identical (delta exactly 0.0000, CI [0,0], 16 GUM documents + 400 UD sentences, both
arms in one process), the read is 15% faster, and the patient defer gets BETTER** — AUC **0.8127 vs 0.7613**,
paired **+0.0515 CI95 [+0.0166, +0.0881]**, twin at chance.

---

## 1. THE PROBE — the defect, reproduced at 16 documents, with the call sites counted

`--probe` installs a `sys.meta_path` finder around `SituationReader(gaz).read(text_only_conll)` and records the
phase of every hdlab module's FIRST import, then counts the call sites in a second pass.

> **THE METHOD MATTERS AND THE OBVIOUS ONE IS WRONG.** A `builtins.__import__` hook **misses**
> `from hdlab import parse_confidence` — that call passes the name `'hdlab'`, not `'hdlab.parse_confidence'`.
> My first probe used a hook and reported `parse_confidence` as NEVER imported while the reader was calling it
> 47 times. The finder fires exactly once per module, on its first import, and returns `None`.

**NOT_BF modules imported DURING `read()` on 16 modern GUM documents: `hdlab.arc_labeler`,
`hdlab.parse_confidence`** — the brief's premise confirmed at scale (mean read 29.4 s/document).

**THE CALL SITES, counted on 4 documents (1,468 label calls + 218 confidence calls):**

| # | call site | calls | in the brief? | what it actually READS |
|---|---|---|---|---|
| 1 | `predicate_argument_frontend.structural_patient_pick` | **620** | **NO** | `obj` / `nsubj:pass` only |
| 2 | `situation_reader._patient_arc_confidence` | 218 label + **218 `calibrated_patient_confidence`** | yes | a binary `is_lab` indicator + the parser's conf/marg |
| 3 | `copular_binding.extract_entity_states` | 210 | yes | the `cop` relation |
| 4 | `situation_reader._commonnoun_appos_map` | 160 — **THE FIRST IMPORTER** | **NO** | `appos` + `cop` |
| 5 | `situation_reader._read_goals` | 42 | yes | `xcomp` / `ccomp` / `acl` |

A separate load-level probe confirms the enumeration is COMPLETE: on one default read `ArcLabeler.load` is
called **exactly three times** (`_frontend_labeler`, `predicate_argument_frontend._labeler`,
`_read_entity_states`) and `parse_confidence` is entered **only** from `_patient_arc_confidence`. No other
importer of either module (`causation_typing`, `crosstype_live_adapter`, `perceptual_access_ledger`,
`reading_grounding_loop`) is reached on a default read.

---

## 2. THE SIGNAL-LOSS TRACE, CHAIN BY CHAIN (the owner's phase-3 question, with counts)

**The end consumer's signal requirement, one sentence each:** the patient defer needs *P(this token is the
verb's patient)*, graded; the goal filter needs *P(this "to VINF" is a complement)*; the state reader needs
*which token holds its clause's predicate slot and which nominal is its holder*; the is-a map needs *which two
nominals the text asserts are the same kind*.

### Chain 1 — the patient defer (tokens → categories → heads → roles → the defer)

| rung | organ | BF | HANDS DOWN | the next rung READS | LOST | count |
|---|---|---|---|---|---|---|
| categories | `lexical_categories` | BF_SPIRIT | a per-token posterior | parser: the posterior; role competition: HARD tags except the head-class cue | the graded category on every other cue | recovering it is worth **+0.0007** AUC (0.8073 vs 0.8066) — nominals are tagged near-certainly, so nothing real is lost here |
| heads | `attachment_arm` | BF_SPIRIT | heads, P(head\|dep), margin | the reader caches all three | nothing in transport | — |
| **reliability** | **`parse_confidence`** | **NOT_BF** | one logistic scalar | the defer | **THE LOSS.** Its features are the ARC-EAGER parser's conf/marg and it was FIT on that parser — not the attachment arm the reader now runs. The attachment marginal separates right-from-wrong patient decisions at **AUC 0.4728 = chance**; what signal the logistic retains comes from its `is_lab` and `gc_conf` features, i.e. **from the competition, laundered through a frozen fitted layer** | **0.7613** vs **0.8127** reading the competition directly |
| roles | `graded_role_assigner.coarse_roles` | BF_SPIRIT | an 8-class posterior + margin + count-calibrated reliability | `labeled_pick` reads the STRING; `parse_confidence` reads a BINARY indicator | the whole posterior | belief alone **0.7861**; belief × slot **0.8127** |

### Chain 2 — the goal purpose filter

`verb_subcat_frames` (BF_SPIRIT) already stores **P(complement)** per verb — but `goal_register` consults it
**only when the governing verb is ADJACENT to "to"**, so an object-control complement (*"told **him** to go"*)
never reaches the lexicalist frame at all. **That is exactly the slice the perceptron deprel was covering.**
The repair turns the adjacency gate into a CONFIGURATION cue (adjacent / object-only / PP / other), which is
what lets the frame speak on the non-adjacent cases.

### Chain 3 — the copular state reader

`attachment_arm.predicate_sites` (BF_SPIRIT, graded) is **already computed on every read** and already unioned
into the state pairs via `state_pairs_from_slot` — but the DETECTION SET the holder binding runs on came off
the perceptron's `cop` label. **The signal was present and not read.**

### Chain 4 — the is-a map

Both halves read the perceptron. The COPULA half transfers to the predicate slot (25 vs 24 of 63 gold edges).
The APPOSITION half does not — see §6.

---

## 3. WHAT WAS BUILT (the brain's mechanism, per consumer)

### 3a. The patient reliability — and why the brief's own proposal is refuted

The brief said: *replace the fitted readout with "the role competition's own patient margin / posterior".*
**The MARGIN is at chance** — AUC **0.4932**, and its count-calibrated reliability 0.4811. The reason is in
`graded_role_assigner`'s own section header: *reliability belongs to the decision the CONSUMER reads, not to
this organ's private 8-way alphabet.* A large margin can mean **confidently OBL**. The consumer asks a
different question, and it is a conjunction of two beliefs the competition already holds:

```
P(pk is the patient of v)  =  P(role(pk) in {OBJ, PASS_SUBJ})  ×  P(pk wins v's object slot)
```

Factor 1 is the organ's posterior for `pk`, marginalised over the heads rung's `P(head | dep)` (the graded
hand-off). Factor 2 is the **slot-level competition** — one object slot, several nominal claimants, normalised
against each other (Vosse & Kempen 2000 competitive unification; the same winner-take-all normalisation
`graded_pick` performs). **Zero fitted parameters**; both factors are pure functions of the count-accrued cue
validities, so `observe_role_outcome` keeps them plastic.

| arm (UD-EWT test, n=1247 patient items, 872 sentences, blanket 0.8148) | AUC | sel@50 | sel@67 |
|---|---|---|---|
| **BF: belief × slot competition** | **0.8127** [0.7807, 0.8455] | **0.9470** | **0.9234** |
| BF: belief alone (no slot competition) | 0.7861 | 0.9374 | 0.9102 |
| SHIPPED: the frozen fitted logistic | 0.7613 [0.7227, 0.7994] | 0.9133 | 0.9078 |
| the competition's MARGIN (the brief's proposal) | 0.4962 | — | — |
| the margin's count-calibrated reliability | 0.4827 | — | — |
| the attachment arm's own Matrix-Tree marginal | 0.4728 | — | — |
| TWIN (BF permuted across items) | **0.5011** | — | — |
| TWIN (shipped permuted) | 0.5186 | — | — |

**PAIRED OVER SENTENCES: +0.0515 CI95 [+0.0166, +0.0881], half-width 0.0357 — CI-SEPARATED above the fitted
readout.** The slot factor is what separates: belief alone is +0.0248 CI95 [-0.0125, +0.0652], not separated.

*(A first full run of the same cell, before the paired statistic was corrected to subtract the shipped arm,
read 0.8154 / 0.7607 on the same population; the difference is the category organ's per-passage file-card
state, which depends on what the process read before. Both runs are on disk; the numbers above are the run
that computes the paired difference.)*

### 3b. The copular detection — the predicate slot

`cop_preds` now comes from `attachment_arm.predicate_sites` (the non-verbal tokens that hold their clause's
predicate slot, graded) instead of the perceptron's `cop` label; the HOLDER comes from the competition's
SUBJ/PASS_SUBJ belief, not a labeler. UD-EWT test, 377 gold predicational states over 341 sentences:

| arm | read-back recall | pairs emitted | paired vs shipped |
|---|---|---|---|
| **BF: the predicate slot** | **0.7958** (300/377) | **429** | **+0.0052 CI95 [+0.0000, +0.0134]** |
| SHIPPED: the perceptron `cop` | 0.7905 (298/377) | 451 | — |
| CAN-FAIL: the label path DROPPED | 0.7798 (294/377) | 396 | **-0.0106 CI95 [-0.0214, -0.0026]** ← CI-separated DOWN |

**The can-fail arm is the load-bearing evidence:** dropping the path loses, so the perceptron was doing real
work and had to be *replaced*, not cut. The replacement matches it with 22 fewer spurious pairs.

### 3c. The purpose/complement decision — a new ARM of the same competition

Infinitive attachment is lexicalist constraint satisfaction (MacDonald, Pearlmutter & Seidenberg 1994;
Trueswell 1996; Garnsey et al. 1997) settled by competition (Vosse & Kempen 2000). Built with the **same
machinery as every other cue table in the organ**: cue values from the categories organ / the attachment arm /
the stored verb frame; strengths = configuration-conditioned CONTRASTS accrued from UD-EWT **train** counts;
additive activation → softmax. `observe_purpose_outcome` accrues one confirmed comprehension outcome at a time
— nothing frozen. Tau (0.60) and cue set (drop `prev`) selected on a **train-internal dev split** (n=250,
dev acc 0.752), never on test.

| arm (UD-EWT test, 129 decidable sites: 80 complement / 49 purpose) | accuracy | reject P | reject R |
|---|---|---|---|
| SHIPPED: perceptron deprel filter | 0.6822 | 0.7746 | 0.6875 |
| **BF: the competition's purpose arm** | **0.6589** | 0.7571 | 0.6625 |
| floor: always reject (majority) | 0.6202 | 0.6202 | 1.0000 |
| floor: never reject | 0.3798 | — | 0.0000 |
| TWIN: same-rate random | 0.5116 | 0.6133 | 0.5750 |

**Paired -0.0235 CI95 [-0.1145, +0.0630] — separated in NEITHER direction: parity.** Agreement with the
shipped filter 0.7597. It clears the majority floor and the twin; it does not beat the supervised label, and
on n=129 it is not shown to be worse either. Per the owner's standing rule, a BF rung at parity with a NOT_BF
stand-in is the rung that ships.

**AND THE RESIDUAL IS LOCATED, NOT SHRUGGED AT.** Broken out by CONFIGURATION (the cell's diagnostic), the
competition BEATS the perceptron exactly where the brief predicted the frame would matter, and loses in ONE
place:

| configuration | n | perceptron | competition | majority |
|---|---|---|---|---|
| `adjacent` ("began to rain") | 42 | 0.7143 | **0.7381** | 0.6429 |
| `objonly` (object control: "told him to go") | 36 | 0.6667 | **0.6944** | 0.7222 |
| `other` | 19 | 0.6842 | 0.6842 | 0.5263 |
| **`pp` ("went to the market to buy")** | **32** | **0.6562** | **0.5000** | 0.5312 |

**My first hypothesis — that object control was the losing slice — is REFUTED by this table: `objonly` is
where the arm WINS.** The whole deficit is `pp`, where the competition is at 0.5000, below even the majority
class. The cause is upstream and it is an OUR-INVENTION stand-in: `goal_register` finds the governing verb by
**scanning backwards for the nearest preceding VERB**, and in a PP-interrupted clause that scan names the wrong
governor, so the lexicalist frame is looked up on the wrong lemma. The perceptron, reading arc features over
the actual tree, does not depend on that scan. **The brain does not scan backwards for a verb — the
attachment organ decides the governor** (see §12.1a for the build and its measurement).

### 3d. The largest call site — a proven identity, not a measurement

`structural_patient_pick` runs the whole perceptron (620 of 1,468 calls) and then has its output **overwritten**
for every relation it reads: `labeled_pick` reads only `obj` / `nsubj:pass`, both inside the Competition-Model
overlay's class space. Substituting `coarse_roles` directly:

* **2175 / 2175 matrix-verb patient picks IDENTICAL** over the whole UD-EWT test set.
* 10 tokens of ~25k (0.04%) carry an `obj`/`nsubj:pass` label the competition does not emit at all; **none of
  them is any matrix verb's chosen patient.**

### 3e. The is-a map — the copula half moves, the apposition half is retired (§6)

---

## 4. NO-REGRESS: EXACT, FULL SIZE, BOTH ARMS IN ONE PROCESS

16 GUM test documents (annotation-free text) + 400 UD-EWT test sentences in 20 pseudo-documents, one
`SituationReader(gaz).read()` per document per arm, scored with the board's own `score_gum_doc` /
`score_ud_chunk`:

| row | shipped | BF routing | n | paired delta |
|---|---|---|---|---|
| who_did_what_agent | 0.7147 | 0.7147 | 389 | **0.0000 CI [0.0000, 0.0000]** |
| who_did_what_patient | 0.6977 | 0.6977 | 301 | **0.0000 CI [0.0000, 0.0000]** |
| state | 0.7500 | 0.7500 | 84 | **0.0000 CI [0.0000, 0.0000]** |
| salience | 0.3125 | 0.3125 | 16 | **0.0000 CI [0.0000, 0.0000]** |

Every floor and twin identical too (patient floor 0.6578 / twin 0.1595; agent floor 0.7789 / twin 0.2416;
state floor 0.4286 / twin 0.7024). **And the read is 15.0% faster: 571.7 s → 485.9 s for the same 36 reads.**

*Why exactly zero rather than nearly zero:* the patient defer is **decision-dead on the live path**
(`precision_weight_tau=None`, so `defer` never fires and the confidence is additive metadata a reasoning
consumer reads); the copular replacement changes the pair SET but not the board's scored answers on these
items; the goal filter feeds no board row. The improvement is therefore **in the reliability signal and in the
BF status of the path**, not in the blanket score — which is exactly what the brief asked for.

---

## 5. WHAT WAS NOT ESTABLISHED

* **The goal witnesses were not re-run under the patch.** They are green at HEAD (`test_goal_register` 10/10,
  `test_parse_goal_extraction`, `test_goal_register_landing_organ`), and the purpose decision is measured
  directly against gold on the consumer's own population — but a solver may not write `hdlab/`, so the
  post-patch witness run is strategy's at integration (it is in `reverify`).
* **The patched hdlab source was never EXECUTED**, only compiled. Every replacement body in the diff is the
  same code the cell runs (the cell's `bf_patient_confidence` / `bf_cop_predicates` / `bf_holders_for` /
  `_purpose_cues` are the landed bodies), and all five patched files compile under an in-memory application —
  but a functional run of the patched tree is strategy's re-verification step.
* **The purpose arm's test population is small (n=129)** and its dev accuracy (0.752) is well above its test
  accuracy (0.6589). The parity claim carries a half-width of 0.0887.
* **The is-a map's row was measured on 8 documents, not 16** (n=155 items; the three arms are exactly
  identical, so the comparison is an identity rather than an underpowered null — but the ABSOLUTE row would
  move on more documents).
* **The governor swap for the purpose arm changed NOTHING** (both arms identical to 4 decimal places, see
  §12.1a): taking the governor from the attachment arm instead of the positional scan does not move the `pp`
  deficit, so the located cause is NOT simply the wrong governor token.

---

## 6. THE NEGATIVE, FULLY UNDERSTOOD: the apposition half of the is-a map

**The number.** UD-EWT test, 168 gold in-text is-a edges over 1251 sentences. The shipped perceptron recipe
recovers 52 (recall 0.3095) at precision 0.2562. The strongest arc-free construction schema I built recovers
42 (0.2500) at precision 0.0972 — paired **-0.0592 CI95 [-0.1386, +0.0199]**, not separated, but emitting
**432 edges against 203**.

**Split by half, which is where the diagnosis lives:**

| half | gold | perceptron | BF |
|---|---|---|---|
| copula (`X is a Y`) | 63 | 24 | **25** (+0.0163 CI95 [-0.0667, +0.0952] — not down) |
| apposition | 105 | 28 | 17 |

**WHY THE APPOSITION SCHEMA LOSES — I counted the gold instead of narrating.** Of 105 gold appositions between
two NOUN/PROPN tokens, **only 24 carry a comma at all**. The dominant shape (65 of 105, gap 1–3 tokens) is
**comma-free CLOSE apposition**: *"the terrorist group **Hamas**"*, *"September 11 ringleader **Muhammad
Atta**"*, *"the word **' terrorist '**"*. My first schema saw only the comma-set-off LOOSE apposition and
recovered **5**; adding close apposition and fixing the UD head conventions (a NAME phrase is headed by its
FIRST token under `flat`, a NOUN compound by its LAST under `compound` — getting that wrong alone cost 5 of
the 17) took it to **17**. An **ORACLE-ARC** arm — the same comma schema on GOLD heads — recovers **15**, so
the residual is the **SCHEMA, not the heads rung**.

**AND THE GOLD IS PART OF THE PROBLEM (change the gold to the ability).** The consumer does not want UD's
`appos` label; it wants *co-typing edges for the conceptual bridge*. A large share of the 432 edges the
construction emits are genuine same-kind assertions that UD labels `compound` or `flat`. Scoring a BF
construction against a treebank convention is an instrument mismatch — which is why the decisive instrument is
the consumer's own row, not edge recall.

**WHAT SHIPS AND WHY — AND WHAT IS STILL MEASURING.** The diff routes the copula half to the predicate slot
and **retires the apposition half**. Keeping it would mean keeping a frozen supervised perceptron on the live
path for a cue whose own precision against the gold it was trained on is 0.2562 — and the owner's rule is
*fix to brain-foundational or REMOVE, never keep for a metric.* A BF replacement is filed as a lead (§9.3).

✅ **AND THE CONSUMER-LEVEL MEASUREMENT SETTLES IT: THE WHOLE MAP IS DEAD ON THE LIVE PATH.** 8 GUM test
documents through the live reader with the reader's own role-mention snapshot installed, THREE arms in one
process, `common_noun_coref` scored on **155 anaphoric common-noun mentions (2,372 resolution records, 442
gold-covered)**:

| arm | common_noun_coref | paired vs shipped |
|---|---|---|
| SHIPPED: the perceptron `appos` + `cop` map | 0.4903 | — |
| BF: copula-only from the predicate slot | 0.4903 | **0.0000 CI [0.0000, 0.0000]** |
| **CAN-FAIL: the map returns NOTHING AT ALL** | **0.4903** | **0.0000 CI [0.0000, 0.0000]** |

Every floor and twin identical too (string-identity 0.6065, recency 0.2323, twin 0.0516), and salience
identical across all three. **Emptying the map entirely changes nothing**, so the apposition half is not a cue
the consumer can see — and neither is the copula half, through this row. The reader was paying 160 perceptron
label calls per document for it. Retiring the apposition half is therefore **measurably free**, and the honest
follow-on is that **the whole map is a deletion candidate**, exactly as `commonnoun_binder.situation_predict`
was found to be (§12.4). *Reported against myself: this row also sits BELOW its own string-identity floor
(0.4903 vs 0.6065) — the consumer is under-performing for reasons this work did not touch.* Read time on the
same 8 documents: 269.9 s → 172.6 s, **36% faster**.

---

## 6b. PHASE 7 (a) THE INFINITIVAL LOSS TRACED ONE RUNG UP, PER CONSTRUCTION, WITH COUNTS

The purpose arm is at parity live because the attachment arm mis-attaches infinitival verbs. **UD-EWT test,
every infinitival VERB (a VERB immediately preceded by `to`), n=337; the arm's head vs the GOLD head, split by
GOLD construction:**

| construction | n | arm head acc | **arm ERROR** | count-accrued prototype |
|---|---|---|---|---|
| `xcomp_control` — *"want **to go**"*, raising | 169 | 0.8757 | 0.1243 | **0.9586** |
| `advcl_purpose` — *"came **to see**"* | 71 | 0.6338 | 0.3662 | 0.5775 |
| **`acl_nominal` — *"a plan **to leave**"*** | **56** | **0.2321** | **0.7679** | **0.8393** |
| `csubj_extrapos` — *"it is hard **to say**"* | 23 | 0.5652 | 0.4348 | 0.7826 |
| `other` | 18 | 0.5000 | 0.5000 | 0.1111 |
| **ALL** | **337** | **0.6766** | **0.3234** | **0.8012** |

Floor (attach to the nearest preceding VERB) 0.6291; **information-free twin (cue strengths permuted) 0.4540**.

**WHICH CUE IS MISSING — and the answer is TWO cues, not one, with the counts separating them.** Tabulating
*where the arm puts it instead*:

| count | pattern | diagnosis |
|---|---|---|
| **24** | `acl_nominal`: arm says **VERB**, gold is a **NOUN** | **a cue the arm DOES NOT HAVE.** Every infinitival cue it owns pushes the clause AWAY from a nominal governor: `to` CLOSES the verb group (`verb_group`, line ~1518), a to-infinitival is NOT finite so it is *penalised* as a predicate (`HOLD_FINITENESS`, ~2208), and `subordination` treats PART-`to` as a clause OPENER attaching to the FOLLOWING verb (~384, ~533). **Nothing says a NOUN can govern an infinitival clause.** |
| 8 | `acl_nominal`: arm says **ROOT**, gold a NOUN | same gap |
| **22** (9+6+5+2) | arm says **PRON**, gold is an **ADJ** | **THIS ONE *IS* pri 101/117's predicate slot, unwired for infinitivals.** The extraposed family (*"it is hard to say"*): `predicate_sites` already computes, graded, that the **ADJ** holds the clause's predicate slot (`attachment_arm.py:1919`, and `host_belief`/`copular_available` at ~1591 explicitly note *"a CLAUSAL / infinitival complement occupies the slot too"*) — but the infinitival ATTACHMENT never reads it, so the clause lands on the expletive `it`. **The signal is computed on every read and thrown away.** |

➡️ **So: 32 of the 43 `acl_nominal` errors need a NEW cue (nominal governor for an infinitival clause); 22
errors across three classes need only the EXISTING predicate slot WIRED into the infinitival arc.**

### (c) THE PROTOTYPE — a validity the arm can ACCRUE ONLINE

Built in the arm's own discipline (`--infin`): candidate governors = every VERB/AUX/nominal/ADJ within ±8, cue
values all arc-free and readable at read time (`candcat`, direction, distance, `adp_between`, `verb_between`,
`nearest_verb`, `nearest_nom`, **`predslot`**), strengths = configuration-conditioned CONTRASTS
`log P(correct | cfg, value) − log P(correct | cfg)` accrued from **UD-EWT train counts** (2,849 sites, 345 cue
strengths), argmax of the additive activation. **Plastic by construction: one confirmed comprehension is a
counter increment**, and the asset is `data/exp_labels_rung_to_live_consumers_v1/infinitival_governor_validities_ud_ewt.json`.

**MEASURED: 0.6766 → 0.8012, paired over sentences +0.1240 CI95 [+0.0663, +0.1802] half 0.0570 —
CI-SEPARATED**, twin 0.4540, floor 0.6291. `acl_nominal` **0.2321 → 0.8393**. *Reported against itself:* it
LOSES on `advcl_purpose` (0.6338 → 0.5775) and on `other` (0.5000 → 0.1111), so this is a **prototype that
locates the signal, not the landed form** — the landed form must enter the arm as one more cue inside
`arc_scores` competing with the rest, not as a separate argmax that overrides them. **That is the heads-rung
brief, with these numbers.**

## 6c. PHASE 7 (b) WHY NOTHING READS THE IS-A MAP — the consumer, at file:line

`hdlab/entity_resolver.py:542`, `tset = appos_map.get(hl, set())`. Two structural reasons it cannot matter:

1. **It is only reached in the DIFF-HEAD branch.** The branch above it (`entity_resolver.py:538`, `if same:`)
   takes the SAME-HEAD recency incumbent and never consults the map.
2. **There it is the FIRST of SIX DISJOINED licences** (:543-549): appos, appos-to-a-name, **the WordNet type
   licence `reader._cn_type_rel`**, the encyclopedic C8 licence, the conceptual bridge, and the coarse-focus
   bridge. **An is-a edge CO-TYPES its pair by definition**, so the WordNet type licence already admits every
   pair the map admits. The map can only ever be redundant.

**MEASURED, AND IT CORRECTS A CLAIM I MADE EARLIER IN THIS FILE.** Re-running the resolver on the SAME mention
stream with the map REAL and EMPTY, 8 GUM documents, **2,372 resolution records, 68 is-a edges**: the map
changes **14 records (0.59%)** and 9 non-writing bridges (403 → 394). **So it is NOT strictly inert** — my
earlier wording ("changes ZERO resolution records") was the stronger claim and it is wrong. What is true, and
is what the retirement rests on: **none of those 14 records is in the scored population**, so
`common_noun_coref` is 0.4903 identically across all three arms (155 anaphoric, gold-covered mentions of the
2,372). The map moves 14 decisions the board cannot see, in a direction nothing measures.

➡️ **That is still a deletion and not a replacement** — a frozen supervised perceptron running 160 times per
document to move 14 unscored decisions is exactly "kept for no measurable reason" — but the honest statement is
**"dead at the instrument", not "provably inert"**, and if a future instrument scores those 14, the answer is to
build the BF successor (§9.3), not to restore the perceptron. `_commonnoun_isa_from_predication` is kept
importable and uncalled for that.

## 6d. PHASE 7 (a) FLIPPING THE DEFER ON — the curve, and why NO default ships in the diff

The defer was decision-dead (`precision_weight_tau=None`). `--defer` reads 400 UD-EWT test sentences in 20
chunks through the LIVE reader, ONE read per arm, collects the reader's OWN patient decisions with their
confidence (n=163 with a confidence), then sweeps tau post-hoc — a threshold gates the READOUT, it cannot
change the read. Dev/test split **by chunk** (even/odd), the dev rule fixed in advance: *the largest tau whose
dev coverage is still ≥ 0.75*.

| arm | dev tau | test coverage | test selective acc | blanket | lift | paired CI |
|---|---|---|---|---|---|---|
| SHIPPED fitted logistic | 0.25 | 0.795 | 0.8788 | 0.8072 | **+0.0715** | **[+0.0136, +0.1510]** CI-sep |
| BF belief × slot | 0.55 | 0.747 | 0.8548 | 0.8072 | +0.0468 | [-0.0081, +0.1190] n.s. |

**THE DEFER HOLDS AS A MECHANISM — and at these taus the CI-separated arm is the NOT_BF one. I am not
shipping a default on that.** The lifts are also not comparable (different coverage). At MATCHED coverage the
two curves say something sharper:

| coverage | SHIPPED selective | BF selective |
|---|---|---|
| ~0.83 | 0.870 | 0.870 (tie) |
| ~0.72 | **0.900** | 0.864 |
| ~0.53 | 0.860 | **0.889** |
| ~0.43 | — | **0.917** |
| 0.27 | **0.773 — BELOW the 0.8072 blanket** | (0.37 → 0.903) |

**THE DIAGNOSIS: the logistic's confidences are BUNCHED.** Its coverage falls 0.83 → 0.80 → 0.72 → 0.52 → 0.27
across five consecutive tau steps and then INVERTS — its most-confident quartile is *worse than average*
(0.773 vs 0.8072). The BF confidence spreads smoothly over the whole range and keeps improving as coverage
tightens (0.917 at 43%). **So the logistic can buy one coarse operating point and nothing else, while the BF
confidence is the one that supports an actual risk-coverage policy** — which is what a Kiani-Shadlen opt-out
needs. On n=83 test items neither conclusion is strong enough to set a default for every reader.

**ACTED ON:** no `precision_weight_tau` default in the diff, stated in the diff header with the one-line change
and the file:line for whoever reads a better-powered curve. **Filed as a next step with the population it
needs** (§12.3).



## 6e. PHASE 7 — THE AUDIT THAT CAUGHT A DEFECT IN MY OWN PATCH

An AST walk of the PATCHED sources (not a text grep) for real `import` statements of the two NOT_BF modules
found **a live `from hdlab.parse_confidence import defer` still in the reader's defer branch**
(HEAD `situation_reader.py:2589`). The import probe cannot see it, because it sits inside
`if p_conf is not None and tau is not None:` and the default tau is `None` — **so it would have re-imported a
NOT_BF module the instant anyone flipped the defer on, which is literally next step 3.** A patch that claims to
take two organs off the live path had left a tripwire for the very next change.

**FIXED in the diff:** the opt-out moves to the organ that PRODUCES the confidence —
`graded_role_assigner.defer_below` (Kiani & Shadlen 2009 opt-out / Kepecs 2008; Friston precision in its
discrete limit), so a consumer that defers never imports a fitted readout for a two-line comparison.

**AFTER THE FIX the patched sources contain exactly ONE import of either module**:
`predicate_argument_frontend._labeler()` at line 56 — and this patch removes its last caller in `hdlab/`
(line 453), so it is dead code that can only load the perceptron if something out-of-tree calls it. Left in
place deliberately; flagged in the diff.

*The lesson for the checklist: a grep for a module name hits docstrings and misses a lazy import inside a
branch that today is unreachable. The import PROBE is a runtime instrument and a dormant wire is invisible to
it by construction — so the static AST audit is not redundant with the probe, it is the half the probe cannot
do.*

## 7. KEY REALIZATIONS

1. **THE PROBE METHOD WAS THE FIRST BUG.** A `builtins.__import__` hook cannot see `from hdlab import X` —
   it is handed the name `'hdlab'`. My hook-based probe reported `parse_confidence` as never imported while
   the reader was calling it 47 times per document. **Switching to a `sys.meta_path` finder is what made the
   defect measurable at all**, and it is why the witness plants an import to prove it can fire.
2. **RELIABILITY BELONGS TO THE DECISION THE CONSUMER READS.** The brief asked for the competition's margin;
   the margin is at chance (0.4932) because it is the certainty of the organ's *private 8-way* choice, and a
   confident OBL looks identical to a confident OBJ. Asking instead "what does the CONSUMER decide" —
   *is this the patient?* — turns the same organ's output into a 0.7852 signal, and remembering that the slot
   is CONTESTED turns it into 0.8154. **The organ had already written this lesson into its own source; I had
   to read it rather than implement the brief literally.**
3. **RUN THE CAN-FAIL ARM, NOT JUST THE COMPARISON.** Measuring "replacement vs incumbent" would have said the
   copular path was a wash. Measuring "incumbent vs *nothing*" is what proved it load-bearing (-0.0106
   CI-separated) and therefore worth replacing rather than deleting — and it is the same test that would have
   told me to delete it had it been flat.
4. **COUNT THE GOLD'S SHAPES BEFORE BUILDING THE CONSTRUCTION.** I built a comma-based apposition schema
   against a gold in which only 24 of 105 items have a comma. Five minutes of counting would have pointed at
   close apposition first.
5. **THE BIGGEST CALL SITE WAS NOT A MEASUREMENT PROBLEM BUT AN IDENTITY.** 620 of 1,468 perceptron calls
   produce labels that are then overwritten by the competition. Proving `2175/2175` identical picks removes the
   largest live user of a NOT_BF organ at **zero** behavioural risk — a free win that no accuracy comparison
   would have surfaced.

---

## 8. EVALUATION OF THE MOST SUCCESSFUL IMPROVEMENT — what let the signal be maximised

**The patient reliability (+0.0515 AUC CI-separated over a frozen fitted readout, with the twin at chance).**
The owner's diagnosis holds exactly: *it is almost always that the real, mathematical brain-foundational chain
was cracked all the way to the top.* Rung by rung, for this one signal:

| rung | cracked? | what made it BF |
|---|---|---|
| tokens | n/a | the corpus token stream |
| **categories** | **YES** | `lexical_categories`: a count-based generative model settled by forward-backward into a per-token posterior; the graded posterior is handed DOWN and the parser reads it |
| **heads** | **YES** | `attachment_arm`: cue competition with strengths learned from soft tree-posterior counts, incremental decode, exact Matrix-Tree posterior handed DOWN |
| **roles** | **YES** | `graded_role_assigner.coarse_roles`: the Competition Model with configuration-conditioned validities accrued from counts |
| **reliability** | **YES — this is the rung this work cracked** | the reliability is now *the deciding accumulator's own belief about the consumer's question*, times the slot competition; no fitted layer remains between the organ and the consumer |
| the consumer | YES | `_patient_arc_confidence` reads the organ directly |

**Every rung on the chain is BF_SPIRIT or better, and the number moved the moment the last NOT_BF link was
removed.** That is the whole finding: the logistic was not adding information, it was *attenuating* it — its
own inputs (`is_lab`, `gc_conf`) were already the competition's, and it discarded the posterior they came from.

**THE RUNGS NOT CRACKED, with their numbers:**

* **The purpose/complement rung is at PARITY on the LIVE chain** (0.6589 vs 0.6822, CI [-0.1145, +0.0630])
  **but CI-SEPARATED ABOVE on a correct input** (0.7907, +0.1084 CI [+0.0157, +0.2031]). **The rung that is not
  cracked is therefore HEADS, not roles**: the attachment arm mis-attaches 30.0% of infinitival verbs (418 of
  1,395), and that is the whole of the gap. A secondary, cheap build is also named: `verb_subcat_frames` stores
  only P(infinitival complement) per verb, not the **object-control frame**.
* **The apposition rung is not cracked at all** (§6) — and the instrument is part of the problem.
* **The blanket patient accuracy is 0.8148, a competent reader is ~0.97.** The defer can only RANK the errors,
  not remove them. That residual is the heads rung: the attachment arm's UAS is 0.43 knowledge-free / 0.53
  prior-informed against a supervised 0.78 (registry). **Wiring alone does not reach brain level here; the
  named gap is meaning feeding structure at the heads rung, with that number attached.**

---

## 9. ALTERNATE PATHS — equally or MORE brain-foundational than what shipped

1. **The patient confidence as a bounded ACCUMULATOR, not a static posterior product.** *Structure:* LIP/FEF
   evidence accumulation. *Computation:* Kiani & Shadlen 2009 / Drugowitsch & Pouget — confidence is the
   posterior over the accumulated evidence at the decision bound, and decision TIME is part of it. What shipped
   is the static limit of that. *What it would take:* the role competition running INCREMENTALLY (it currently
   reads the whole sentence); the heads rung already has an incremental arm (`HDLAB_ARM_DECODE=incr`), the
   roles rung does not. *Why not now:* that is the "organs take data in order" rung, a separate build. **It
   would also yield reading-time predictions, which the static form cannot.**
2. **The purpose decision as SURPRISAL-DRIVEN REANALYSIS.** *Structure:* left IFG / pMTG reanalysis.
   *Computation:* Levy 2008 — attach the "to VP" to the site that minimises expected surprisal given the verb's
   frame DISTRIBUTION, and fire reanalysis when the error exceeds a bound (P600). Strictly richer than my
   two-class softmax. *What it would take:* per-verb frame distributions over all attachment sites (we store
   one scalar) and a P600-style reanalysis organ (the substrate has an N400 coherence monitor, not a P600).
3. **The is-a map as RETRIEVAL, not extraction.** An apposition is an EPISODE that updates the anterior-temporal
   hub's typed knowledge (Rogers & McClelland), not a syntactic rule to be run at read time. More BF: drop the
   extractor, let the conceptual bridge read the hub's typed similarity (already present as `_cn_type_rel`)
   plus an episodic trace of the co-mention. *What it would take:* wiring the co-mention episode into the
   meaning hub's counts — which is pri 114's acquisition path. **Also on disk already:**
   `hdlab/definitional_extraction.py` reads a genus statement straight off the page and is BF_SPIRIT; the
   bridge's is-a seed arguably belongs there rather than in a deprel scan.
4. **ONE eventuality per clause.** `state_pairs_from_slot` (pri 113) already makes the predicate slot supply the
   state reader's PROPERTY. The fully consolidated form makes the state reader a READOUT over the event set
   rather than a second detector — one structure per clause, which is strictly more BF than the union of two
   detectors this work leaves in place (`bind | robust_cop | state_pairs_from_slot`).
5. **Replace the defer THRESHOLD with a reward-based opt-out.** Kiani & Shadlen's opt-out is chosen by expected
   reward, not a fixed tau. The substrate has a reward/vigor cluster; `precision_weight_tau` is an
   OUR-INVENTION knob sitting where a decision should be.

---

## 10. ADJACENT COMPONENTS — capabilities, limits, BF status (seeds for the next briefs)

| component | BF status | what this work learned about it |
|---|---|---|
| `graded_role_assigner` | BF_SPIRIT | its `role_decision` / `margin_reliability` API calibrates the organ's own 8-way label; **no consumer's actual question is 8-way.** A `reliability` entry per CONSUMER DECISION (patient, holder, purpose) would stop every consumer re-deriving one |
| `attachment_arm` | BF_SPIRIT | `predicate_sites` is computed on every read and was read by ONE consumer; its Matrix-Tree marginal is at **chance (0.4728)** for patient right-vs-wrong, which contradicts the note in `parse_confidence` that generalises the obl finding (AUC 0.782) — the marginal is informative for ATTACHMENT, not for ROLE |
| `verb_subcat_frames` | BF_SPIRIT | stores one scalar per verb; the **object-control frame is missing**, and that is where the purpose arm loses |
| `parse_confidence` | NOT_BF | after this patch it has **zero live consumers**; the obl calibrator was already dormant. Candidate for deletion once the obl reader is wired to the marginal |
| `arc_labeler` | NOT_BF | after this patch it has zero live consumers; the module's real remaining value is the `COMPETITION_ROLES` overlay, which is not the perceptron |
| `entity_resolver.resolve_commonnouns` | BF_SPIRIT | the only consumer of the is-a map; its bridge would be better fed by the meaning hub than by a syntactic extractor |

---

## 11. AUDIT UPDATE (for `notes/BRAIN_FOUNDATIONAL_AUDIT.md`)

* `hdlab/parse_confidence.py` — the registry note says the BF replacement is *"the graded_parser Matrix-Tree
  MARGINAL (obl_reliability_marginal in-module: AUC 0.782 > logistic 0.736)"*. **That generalises an obl result
  to the patient and it is wrong there:** measured on UD-EWT test (n=1247), the attachment marginal scores
  **AUC 0.4728 — chance** for patient right-vs-wrong. The BF replacement for the PATIENT is the role
  competition's own patient belief × slot competition (0.8127). The note should be corrected per-decision.
* `hdlab/arc_labeler.py` — the note records that argument roles are decided by the competition. It should also
  record that the fine relations the perceptron still decides reach the live path through exactly **three**
  places, all removed by this patch, and that `structural_patient_pick`'s use is **provably inert**
  (2175/2175 identical picks).
* Both modules move from "NOT_BF, on the live path" to "NOT_BF, no live consumer" — the registry's NOT_BF
  count stays 6, but the *live-path* NOT_BF count goes to zero for a default read.

---

## 12. PRIORITY NEXT STEPS (brief-ready, with numbers)

### 12.1a THE PURPOSE ARM'S RESIDUAL, AND THE TWO THINGS I TRIED THAT DID NOT MOVE IT

The deficit is entirely the **`pp` configuration** (0.5000 vs the perceptron's 0.6562, n=32, majority 0.5312).
**TRIED AND FLAT — take the governor from the ATTACHMENT ARM instead of `goal_register`'s backwards scan for
the nearest preceding VERB.** Result: **identical to four decimal places in every configuration** (0.6589
overall, `pp` 0.5000), because in the PP-interrupted clause the arm's head of the infinitive usually IS the
nearest preceding verb, so the two governors agree. **So the located cause is not the governor token.**

What the bucket actually contains, read off the class counts: `pp` holds 17 complements and 15 purposes, and
the complements are `acl` modifiers of a NOUN *inside* the PP (*"asked for permission **to leave**"*) while the
purposes are `advcl` on the verb (*"went to the market **to buy**"*). **The discriminating fact is whether the
infinitive attaches to the VERB or to the NOUN in the PP** — the heads rung's job, and the arm's head category
is already a cue in the table (`headcat`).

### ✅ THE ORACLE-CEILING PROBE, AND IT CHANGES THE VERDICT ON THIS RUNG

Run the IDENTICAL cue competition with **GOLD heads** feeding only the two arc-derived cues (dev-selected
again, independently: tau 0.65, drop `headismv`, dev 0.8240):

| configuration | n | perceptron | competition (arm heads) | **competition (GOLD heads)** |
|---|---|---|---|---|
| `adjacent` | 42 | 0.7143 | 0.7381 | 0.7381 |
| `objonly` | 36 | 0.6667 | 0.6944 | **0.8333** |
| `pp` | 32 | 0.6562 | 0.5000 | **0.7500** |
| `other` | 19 | 0.6842 | 0.6842 | **0.8947** |
| **ALL** | **129** | **0.6822** | 0.6589 | **0.7907** |

**Paired over sentences: +0.1084 CI95 [+0.0157, +0.2031] — CI-SEPARATED ABOVE the frozen supervised deprel
filter.** And the cause is counted: **the attachment arm's head of the infinitival verb is WRONG on 418 of
1,395 sites — 30.0%.**

➡️ **SO THE PURPOSE ARM IS NOT AT PARITY BECAUSE ITS MECHANISM IS WEAK — IT IS AT PARITY BECAUSE ITS INPUT IS.**
The Competition-Model form BEATS the supervised label by +0.1084 CI-separated the moment the heads rung hands
it a correct attachment, and the 30% figure is the whole of the gap. That is the owner's rule playing out
exactly: *a truly brain-foundational component that is not working almost always means something upstream is
not 100% brain-foundational.* The BF rung ships at parity now and becomes a CI-separated win when the
governor's infinitival attachment is fixed — which is a named, numbered upstream brief, not a mystery.

1. **FIX THE GOVERNOR'S ATTACHMENT OF INFINITIVAL VERBS — the single highest-value item this work found, and
   phase 7 split it into two separable builds with their own counts (§6b).**
   (a) **WIRE THE EXISTING PREDICATE SLOT INTO THE INFINITIVAL ARC** — 22 errors are "the arm says PRON where
   the gold governor is the ADJ": `predicate_sites` already computes, graded, that the ADJ holds the clause's
   predicate slot, and the infinitival attachment never reads it, so *"it is hard **to say**"* lands on the
   expletive. **This is a wire, not a build.**
   (b) **ADD A NOMINAL-GOVERNOR CUE for infinitival clauses** — 32 errors are `acl_nominal` (*"a plan **to
   leave**"*, arm accuracy **0.2321**, error **0.7679** on n=56): every infinitival cue the arm owns pushes the
   clause away from a nominal governor and none admits one.
   **The prototype that proves both are learnable from counts:** 0.6766 → **0.8012** overall, paired **+0.1240
   CI95 [+0.0663, +0.1802]** CI-sep, twin 0.4540, `acl_nominal` 0.2321 → **0.8393**; and with correct heads the
   purpose decision goes 0.6589 → **0.7907, +0.1084 CI95 [+0.0157, +0.2031]** CI-separated above the frozen
   supervised label. The landed form enters `arc_scores` as one more competing cue, NOT as a separate argmax
   (the prototype LOSES on `advcl_purpose` 0.6338 → 0.5775 precisely because it overrides the other cues).
   *Secondary, cheap:* the **object-control frame** in `verb_subcat_frames`.
2. **Give `graded_role_assigner` a per-CONSUMER-DECISION reliability map** (patient / holder / purpose), each
   count-accrued with an `observe_*_outcome` path. *Why:* three consumers each re-derived one this session;
   the organ already has the machinery (`RELIABILITY_KINDS`) and the wrong alphabet.
3. **Flip the patient defer ON — but on a better-powered curve than this one (§6d).** Measured through
   `read()`: the defer HOLDS as a mechanism (shipped logistic +0.0715 CI [+0.0136,+0.1510]; BF +0.0468
   CI [-0.0081,+0.1190]) on only **n=163 decisions / 83 test items** from 400 UD sentences, and at the
   dev-selected taus the CI-separated arm is the NOT_BF one — so **no default ships in the diff**. What the
   curves already show: the logistic is BUNCHED (coverage 0.83→0.80→0.72→0.52→0.27 in five tau steps, and
   its most-confident quartile is 0.773, BELOW the 0.8072 blanket) while the BF confidence spreads smoothly and
   reaches 0.917 at 43% coverage. *What it needs:* the same arm over ~2,000 UD sentences (n ~ 800 decisions) so
   a matched-coverage comparison is powered, then one line at `situation_reader.py:1026`.
4. **DELETE the is-a map, do not just halve it** — all three arms (shipped / copula-only / empty) score
   `common_noun_coref` 0.4903 identically on 155 items, so the map is DEAD on the live path in the same sense
   `commonnoun_binder.situation_predict` was (reader CATALOG C2). Then **re-seed the bridge from
   `definitional_extraction` + the meaning hub** (§9.3) and score it on `common_noun_coref`, not on UD `appos`
   recall. *Also worth a brief on its own:* that row is BELOW its string-identity floor (0.4903 vs 0.6065).
5. **Delete `hdlab/parse_confidence.py`'s patient half** once (3) lands, and wire the obl reader to the
   Matrix-Tree marginal as its own note recommends — then the module goes entirely.

INTEGRATED_BY_STRATEGY 2026-09-15 21:45 local -- DONE by strategy after executing the patched tree first-hand (the agent could only compile it): the 13-hunk diff + both assets APPLIED; cell self-test 17/17 on the landed tree (after the agent's tree-aware S5b/S5c fix c7259c5f0); probe witness green (zero NOT_BF imports during a default read); 20-witness consumer batch green (one 19c copular witness timed out under load); crosstype live wire 6/6, de-leak, affect landing green after the adapter repair; goal landing 6/6 after the canonicaliser repair; state QA consumer green after the floor repair; product board pri129b byte-identical to pri125a on every reader-driven and component row (state +1 item). Repairs made at landing and recorded: the crosstype adapter reads the competition's argument relations (fine relations -> pri 134); the goal canonicaliser maps a graded record through its resolved head (pri 131 lands the id); R01/R02 from the follow-up review; the 19c QA recency floor abstains on an unaligned question. The agent's DENIED shadow-tree command was not retried by it; the landing path executed the tree instead.
