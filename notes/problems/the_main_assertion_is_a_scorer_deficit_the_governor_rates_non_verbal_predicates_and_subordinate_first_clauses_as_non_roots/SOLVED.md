---
problem: the_main_assertion_is_a_scorer_deficit_the_governor_rates_non_verbal_predicates_and_subordinate_first_clauses_as_non_roots
status: SOLVED
bar: "Root recall up CI-separated under both decodes with nsubj/ccomp/advcl not down and UAS not down; knowledge in counts with an online observe path; witness green -- OR a numbered located negative (e.g. the residual is fragments) with counts."
result: "UD-EWT test 700, gold categories, n=700 gold root arcs. IN-ORDER decode (the live default): root 0.7214 -> 0.7486, paired delta +0.0271 CI [+0.0086, +0.0457]; UAS 0.6163 -> 0.6211 (+0.0048 CI [-0.0002, +0.0099]); nsubj 0.771 -> 0.778, ccomp 0.629 -> 0.638, advcl 0.306 -> 0.313, xcomp 0.730 -> 0.715. WHOLE-SENTENCE SEARCH decode: root 0.7471 -> 0.7729, paired delta +0.0257 CI [+0.0071, +0.0443] against the STRONGEST floor run (base with the incumbent root-pick, 0.7471); UAS 0.6178 -> 0.6198; nsubj 0.776 -> 0.779, ccomp 0.647 -> 0.681, advcl 0.328 (flat). The search decode's gain requires the root-pick option to move from `score` to `left` -- with the incumbent pick it REGRESSES to 0.7000 (-0.0471 CI [-0.0714,-0.0229]); the reason is traced and counted in section 5, and the in-order decode never reads that option."
floor: "the IDENTICAL pipeline (same teacher, same cap, rounds 3, alpha 0.8, beta 10) with the root cues OFF: in-order root 0.7214 / UAS 0.6163, search root 0.7471 / UAS 0.6178 -- reproducing the LIVE asset's numbers exactly (live in-order root 0.721 UAS 0.6125; live search root 0.747). Weaker floors also run: search decode with the `left` root pick and NO cues, root 0.7200 (worse than the incumbent 0.7471, so `left` is not a free win -- it flips only together with the cues)."
controls: "INFORMATION-FREE TWIN (the same three cues, the same density, values PERMUTED across the sentence's tokens): in-order root 0.717 vs 0.740 base and search root 0.550 vs 0.770 base (train 1.5k / test 300 arm) -- the twin LOSES under both decodes, and loses catastrophically under the search decode, excluding 'any extra root-row signal helps'. ORACLE-CEILING probe (add +20 to the gold root arc, nothing else): in-order root 0.721 -> 0.943, UAS 0.6125 -> 0.6574 -- the headroom behind the root row alone, measured BEFORE building. TIE COUNT: 378 of 700 test sentences had >=2 candidates tied at the best root score before the change (the decision was a tie-break, not evidence). UPSTREAM TRACE: the acquisition teacher's posterior mass on a gold ADJECTIVAL root arc was 0.001 (100% below 0.05; ADV 0.000, PRON 0.000) -- the copular cue had nothing to learn from. REFUTED-AS-BUILT and recorded, each with its number: the competition (zero-mean) readout; the lateral-inhibition (max-centred) readout; the subordination-DIRECTED clausal construction; the predication teaching boost at gamma 8 as a net win; the cue-gain sweep (no gain lifts both decodes)."
files_changed: "experiments/exp_attachment_main_assertion_v1.py, notes/problems/the_main_assertion_is_a_scorer_deficit_the_governor_rates_non_verbal_predicates_and_subordinate_first_clauses_as_non_roots/{SOLVED.md,attachment_arm_patch.diff}, data/exp_attachment_main_assertion_v1*/metrics.json (nothing under hdlab/ or tools/ was edited -- the proposed change is the diff)"
reverify: ".venv/Scripts/python.exe experiments/exp_attachment_main_assertion_v1.py --self-test   (18 checks, scaffold-free; then the headline: HDLAB_EXP_NAME=attachment_main_assertion_v1_reverify .venv/Scripts/python.exe experiments/exp_attachment_main_assertion_v1.py --smoke --test-cap 700 --arms base,cues -- writes only its own data/exp_* directory)"
---

> **COMPLETION.** The main-assertion decision had **no evidence in it at all**: `SentenceCues.cues(j, h)` returned
> `{}` for `h == 0`, so the entire root signal was 17 per-category numbers and every VERB in a sentence had the
> identical root activation — **378 of 700 test sentences (54%) were decided by a tie-break.** The oracle behind
> that row was **root 0.721 → 0.943, UAS 0.6125 → 0.6574**. Building the brain's actual mechanism — the root
> decision as a cue competition among candidate PREDICATES, with finiteness, copular predication, subordination
> marking and main-clause position as cues whose validities are LEARNED from the teacher posterior exactly like
> every other cue — lifts root **+0.027 CI-separated under the live in-order decode** and **+0.026 CI-separated
> under the whole-sentence search** (the latter needing one existing decode option moved, with the reason traced
> and counted). The wall was **upstream and non-brain-foundational**, the same shape as the coordination win: the
> acquisition teacher put **0.001** posterior mass on a gold adjectival root arc. Twin loses under both decodes.
> Three alternative readout forms and one alternative construction were built and REFUTED with numbers.

## 1. How the brain does this (the opening move)

Which word carries the main assertion is not a per-word prior over categories. It is the SAME cue competition that
decides every other attachment (Bates & MacWhinney 1989 Competition Model; MacDonald-Pearlmutter-Seidenberg 1994
constraint satisfaction), run over the sentence's candidate PREDICATES, with cues whose validities are LEARNED:

1. **FINITENESS.** The asserted proposition is the tensed one; tense/agreement morphology is the mark. The child's
   root-infinitive stage (Rizzi 1993; Wexler 1994) is exactly the emergence of this cue — a to-infinitive or a bare
   participle cannot carry the main assertion, a tensed or auxiliary-supported verb can. Read off the visual word
   form by morphological decomposition (Rastle & Davis 2008; Taft 1979 — our `hdlab/morphology.py` route, reached
   through `lemma_verb`) plus the auxiliary frame (Mintz 2003 frequent frames).
2. **COPULAR PREDICATION.** In "the vote is confusing" the assertion is CONFUSING; the copula is the tense carrier
   and the non-verbal predicate is the predication (Pustet 2003). The UD convention the consumers read agrees.
3. **SUBORDINATION MARKING.** A clause opened by a subordinator or relativizer is DEPENDENT — its verb is not the
   main assertion ("When I arrived, she LEFT"). Complementizers are the acquisition cue for clause dependency
   (Diessel 2004).
4. **MAIN-CLAUSE POSITION / SUBJECT SUPPORT.** English asserts matrix-first and a canonical predicate has a nominal
   to its left with no predicate in between — the Competition Model's word-order cue.

PINNED: that the decision is a cue competition, and that finiteness / copular predication / subordination marking
are the cues a reader has. OURS (swept, never adopted): which categorical values, the teacher's boost gammas, and
the candidate set for a verbless utterance.

## 2. The deficit, measured on disk before anything was built

| what | number |
|---|---|
| cue cells on the ROOT configuration in the live asset | **0** (`{'locality': 0, 'frame': 0, 'form': 0, 'boundary': 0, 'agree': 0, 'constr': 0, 'pp': 0, 'plaus': 0}`) |
| the entire root signal | 17 numbers: ROOT:VERB +2.192, NOUN +1.208, PROPN +1.029, ADJ −1.336, NUM −2.775 … |
| test sentences with ≥2 candidates TIED at the best root score | **378 / 700 (54%)** |
| ORACLE on the root row alone (+20 on the gold root arc) | in-order root 0.721 → **0.943**, UAS 0.6125 → **0.6574**; search root 0.747 → 0.964 |
| root misses by gold category (in-order, live asset) | VERB 47, PROPN 35, ADJ 33, NOUN 30, NUM 24, ADV 15 |

So the residual named in the brief ("its own cue activations rate the true main word as a non-root") is not a
calibration problem — there was **nothing in the root row to calibrate**.

## 3. The upstream trace (the wall was not here)

The read-time cue can only learn a validity from what the acquisition teacher's posterior shows it. Teacher
(prior-free co-occurrence EM + semantic bootstrapping β=10, trained on 1.5k train sentences), posterior mass on the
**gold root arc**, by gold-root category, n=400 test sentences:

| gold root category | n | mean mass on the gold root arc | fraction below 0.05 |
|---|---|---|---|
| VERB | 229 | 0.358 | 0.37 |
| NOUN | 42 | 0.404 | 0.14 |
| PROPN | 70 | 0.260 | 0.57 |
| **ADJ** | **30** | **0.001** | **1.00** |
| **ADV** | 9 | **0.000** | 1.00 |
| **PRON** | 6 | **0.000** | 1.00 |

The teacher's root row is `β·(best subject fit + best object fit)` for a VERB and a flat −1.5 for everything else,
so a copular predicate can never out-root a verb. **The copular cue had nothing to learn a validity from** — the
same shape as the coordination win (pri-95: the teacher put 0.054 mass on gold conj arcs). Fixed by
`predication_boost`, the exact analogue of `parallelism_boost`, derived from categories + the copula word list +
morphology, never from a tree. Its measured effect on the learned validities: `ROOT:ADJ|cop` **+3.47 → +4.35**,
`ROOT:VERB|sconj` **−0.74 → −1.42**.

## 4. What was built, and what the organ LEARNED

Three cue families on the ROOT configuration, accrued and read like every other cue (`SentenceCues.cues(j, 0)` now
returns them; `strengths_from_arc_counts` turns the counts into contrasts; `observe_arc_outcome` accrues them
online — self-test verifies the ROOT cell moves after one comprehension outcome):

- `rpred` — a verbal candidate's finiteness class (`to` / `ing` / `ed` / `s` / `base` / `auxbe` / `auxhave` /
  `auxmod`), or a non-verbal candidate's predication status (`cop` / `nov` / `hasv`);
- `rsub` — the clause-dependency marking in force (`sconj` / `wh` / `cc` / `none`);
- `rpos` — rank among the assertion candidates (`1` / `2` / `3` / `x`) × a nominal to the left with no predicate in
  between (`S`).

**Nothing here is hand-weighted.** The validities the organ learned (train 1.5k, rounds 3) are the brain's story,
recovered from counts:

| learned contrast | value |
|---|---|
| `ROOT:ADJ\|cop` vs `ROOT:ADJ\|hasv` | **+4.35** vs **−6.20** — a copular adjective asserts; a bare adjective in a sentence that has a verb does not |
| `ROOT:NOUN\|cop` / `ROOT:PRON\|cop` | +4.50 / +5.16 |
| `ROOT:VERB\|to` / `ROOT:VERB\|ing` | **−1.69 / −1.85** — the infinitive and the gerund do not assert |
| `ROOT:VERB\|s` / `\|ed` / `\|auxhave` | +0.52 / +0.21 / +0.46 — the tensed and auxiliary-supported forms do |
| `ROOT:VERB\|sconj` vs `\|none` | **−1.42** vs **+0.44** — a subordinator-opened clause's verb is not the main assertion |
| `ROOT:PROPN\|nov` vs `\|hasv` | **+2.57** vs **−3.76** — a verbless fragment's head legitimately roots |

## 5. The search decode: the signal is right, the PICK rule was the wrong part

Under the whole-sentence search the cues first looked like a CI-separated **loss** (root 0.7471 → 0.7000). Decomposing
its root decision into OFFER (is the gold root inside the unconstrained MAP root set?) and PICK (given it is offered,
is it chosen?), n=700:

| | root | gold OFFERED | PICKED given offered | mean root-set size |
|---|---|---|---|---|
| base | 0.7471 | 0.800 | **0.934** | 1.67 |
| + root cues | 0.7000 | **0.807** | **0.867** | **1.29** |

**The cues improve the OFFER stage and the incumbent PICK rule then throws it away.** The reason is exact: with the
old 17-number root row every VERB tied, so `max(roots, key=A[0][j])` meant *"prefer a verb, else the leftmost"* —
a strong heuristic (0.934) that was an artifact of having no information. The learned validities are calibrated over
**all tokens**, not over the subpopulation the tree already offered as roots, so as a pick rule among offered
candidates they are worse. Moving the already-provided option `HDLAB_ARM_ROOT_PICK` to `left` (the leftmost offered
candidate — English asserts matrix-first) gives **root 0.7729, +0.0257 CI [+0.0071, +0.0443] over the strongest
floor**, UAS 0.6198 vs 0.6178, ccomp 0.647 → 0.681.

This is not free tuning and the control says so: **without the cues, `left` is WORSE than `score` (0.7200 vs
0.7471)**. It flips only together with the cues. `incremental_tree` — the live default decode — never reads
`ROOT_PICK`, so the change is separable from the live path.

## 6. Refuted as built (each with its number; do not re-try)

| route | why it was the brain's mechanism | measured |
|---|---|---|
| **Competition readout** (cue contribution centred to zero mean over the live candidates — the root slot has capacity one, MacWhinney 1987) | the arm already argues this for the object slot (OCCUPANCY) | WORSE under both decodes: in-order root +0.021 vs +0.034 flat; search −0.049 vs −0.030. Reason, counted: 120 of 177 search root misses have the gold root **outside** the MAP root set, so what is needed is the ABSOLUTE root-vs-attach margin that centring removes |
| **Lateral-inhibition readout** (`d − max d`: the winner keeps its base score, the losers are suppressed — Usher & McClelland 2001) | a competition is inhibitory | in-order root **−0.019**, search **−0.031**; worse than flat at every gain (0.5 / 1 / 2) |
| **Subordination-DIRECTED clausal construction** (`clausal_arcs` always proposes EARLIER→LATER, which is the exact reverse of the gold arc in every subordinate-first sentence) | the complementizer marks the DIRECTION of the dependency (Diessel 2004) | NULL and costly: root +0.003 (in-order) / +0.000 (search), advcl +0.013, **xcomp 0.724 → 0.632**. Kept out of the patch |
| **Cue-gain sweep** (0.25 / 0.5 / 0.75 / 1.0 / 1.5) | the phase-diagram move | no gain lifts BOTH decodes under the incumbent pick rule: in-order peaks at 0.5–0.75 (+0.034/+0.036), search is neutral only at 0.25 (+0.001 n.s.) and −0.050 by 1.5. Gain **1.0 kept** (no knob; the learned validity IS the strength) |
| **Read-time cues WITHOUT the teacher repair** | the ablation that isolates the two halves | root 0.7557 in-order (+0.0343) vs 0.7486 with the teacher repair (+0.0271) -- the read-time cue is the whole lever; the teacher repair is **neutral on the end number** (the 0.007 gap is inside the CI half-width 0.017) while visibly improving the validity table (section 3). Both are CI-separated over base. gamma is swept and 0 is selectable |
| **Predication teaching boost as a net win** | the upstream fix | it does what it is for (it doubles the subordination contrast and raises the copular one, section 3) but at γ=8 the *end* numbers are not better than the read-time cues alone (in-order root +0.017 vs +0.027). **Kept in the patch** because it is the brain-foundational half and the validity table is visibly better; γ is a swept operating point and 0 is selectable |

## 7. Every component touched, and its brain-foundational status

| component | role here | BF status |
|---|---|---|
| `hdlab/attachment_arm.py` — the ROOT configuration | **the defect**: `cues(j, 0)` returned `{}`, so the main assertion was a per-category prior | was **NOT_BF** for this decision (a prior, not a competition) → **BF_SPIRIT** after the patch (competition with learned validities) |
| `hdlab/attachment_arm.SentenceCues` | now carries `rootcues` (one pass per sentence) | BF_SPIRIT (unchanged form) |
| `hdlab/attachment_arm.function_word_arcs` | supplies the copular frame the `cop` cue reads | CONVENTION layer, honestly labelled in the organ; unchanged |
| `hdlab/morphology.py` via `thematic_role_labeler.lemma_verb` | supplies the finiteness cue's stem test | **BF** (Rastle-Davis / Taft / Pinker-Ullman; glass-box, no nltk at inference) |
| `hdlab/lexical_categories` (the live count-based tagger) | the categories the cues are keyed on; SCONJ is the weakest tag (0.733 test) and the `rsub` cue depends on it | BF_SPIRIT; **named as the upstream limiter** (section 8) |
| `tools/build_attachment_validities.py` teacher | the acquisition signal; was **blind to non-verbal predication** (0.001 mass) | the blindness was the non-BF part; `predication_boost` repairs it treebank-free |
| `hdlab/attachment_arm.map_tree_single_root` root pick | the search decode's PICK rule; its 0.934 was a tie-break artifact | decode config, not an organ; one option moved, measured both ways |
| `hdlab/attachment_arm.incremental_tree` | the LIVE decode; consumes the improved activations unchanged | BF (in-order commitment); **untouched** |
| `SemanticBootstrapTeacher` / typed selectional store | the teacher's verb-argument half; unchanged | BF_SPIRIT (foundation-informed) |

**Plasticity:** the root cues live in the same counts as every other cue. `observe_arc_outcome(toks, pos, j, 0)`
accrues a ROOT cue outcome online and recomputes the strengths — verified in the self-test
(`ROOT:ADJ|cop` cell moves to `[1.0, 1.0]` after one observation).

## 8. Where we still lose, with counts (the honest residual)

Root misses remaining under the in-order decode, by cue signature (n=169):

| signature | n | what it is |
|---|---|---|
| `NUM / nov / x` | 16 | bare numerals and phone numbers as list items |
| `PROPN / nov / xS` | 14 | signatures and headline names |
| `NOUN / hasv / xS` | 12 | a nominal root in a sentence that DOES contain a verb (parentheticals, appositive roots) |
| `ADJ / hasv / xS` | 11 | non-copular adjectival predication |
| `ADJ / nov / xS` | 10 | verbless adjectival fragments |
| `VERB / auxbe / 2S` | 8 | the second verb of a progressive; the matrix/embedded call |

Two-thirds of the residual is **fragment and non-canonical predication**, i.e. a population fact about UD-EWT
(email, reviews, forum text) rather than a mechanism failure — but the `hasv` rows (≈30) are a real remaining
mechanism gap: non-copular non-verbal predication has no cue yet.

## 9. Adjacent components, capabilities and the next problems

1. **The SCONJ tag is the `rsub` cue's ceiling.** The category organ reads SCONJ at 0.733 on test; every `sconj`
   value the root competition uses is only as good as that. Worth its own brief (it is already pri-15's territory).
2. **The copular-subject side is NOT moved by this, and I measured it rather than assuming.** Strategy supplied the
   slice (161 gold nsubj whose gold head is a non-verbal predicate). Measured here, same population, same tables:
   in-order 0.4037 -> 0.4224 (+0.019, CI [-0.006, +0.048]); search/score 0.5280 -> 0.5093; search/left 0.5280 ->
   0.5155. **All three CIs include zero -- the root cue does not move copular-subject attachment.** The miss
   breakdown says exactly why: the "subject crowned as ROOT" mode does fall under the in-order decode (20 -> 18 of
   161) but the DOMINANT mode, the subject pulled to a LATER VERB inside the predicate's own clause, is untouched
   (49 -> 47). That is a cue on the *nsubj* arc (the predicate must out-compete a later verb for its subject), not
   on the root arc, and it is the natural next brief. `evaluate()` in the cell now reports `cop_nsubj` with its
   per-sentence vectors, so the next attempt has the instrument and the floor already.
3. **The PICK-vs-SCORE finding generalises.** A validity learned over all tokens is not calibrated for a decision
   taken over a tree-filtered subpopulation. Anywhere the substrate reuses a learned strength as a tie-break inside
   a search, the same mismatch is waiting.
4. **Non-copular non-verbal predication** (≈30 residual misses) — no cue exists.

## KEY REALIZATIONS

- **The activations were not "wrong", they were ABSENT.** The brief said the decode is faithful to bad activations;
  the disk said `cues(j, 0) -> {}` — the root row had *zero* cue cells and 54% of sentences were tie-broken. Reading
  the code for the h == 0 branch, before any modelling, is what turned a calibration story into a build.
- **A 0.93 accuracy can be an artifact of having no information.** The search decode's root PICK was right 93% of
  the time only because every verb tied and `max` returns the first — i.e. "prefer a verb, else leftmost". Adding
  real evidence *broke* it. Decomposing the decision into OFFER and PICK is what made that visible; the headline
  number would otherwise have read as "the mechanism fails under one decode".
- **The teacher was blind again, in the same way as coordination.** Checking what posterior mass the acquisition
  teacher puts on the class of arcs the new cue is about (0.001 for adjectival roots) should be the FIRST move for
  any new cue in this organ, not the last.
- **Three brain-plausible readout forms of the same evidence give three different answers.** Excitatory, zero-mean
  and inhibitory are all defensible as "a competition"; only measurement separated them, and the winner was the
  plainest one. The story ("the slot has capacity one") was not evidence.
