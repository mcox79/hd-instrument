---
problem: the_main_assertion_is_a_scorer_deficit_the_governor_rates_non_verbal_predicates_and_subordinate_first_clauses_as_non_roots
status: SOLVED
bar: "Root recall up CI-separated under both decodes with nsubj/ccomp/advcl not down and UAS not down; knowledge in counts with an online observe path; witness green -- OR a numbered located negative (e.g. the residual is fragments) with counts."
result: "UD-EWT test 700, gold categories, n=700 gold root arcs, paired bootstrap over sentences (4000 draws). POWERED ARM (train 1500, the floor rebuilt at the same cap and reproducing the live asset's root recall exactly). IN-ORDER decode (the live default): root 0.7214 -> 0.7486, +0.0271 CI [+0.0086,+0.0457]; UAS 0.6163 -> 0.6211 (+0.0048 CI [-0.0002,+0.0099]); nsubj 0.771 -> 0.778, ccomp 0.629 -> 0.638, advcl 0.306 -> 0.313, xcomp 0.730 -> 0.715 (the one give-back). WHOLE-SENTENCE SEARCH decode: root 0.7471 -> 0.7729, +0.0257 CI [+0.0071,+0.0443] against the STRONGEST floor run; UAS 0.6178 -> 0.6198; ccomp 0.647 -> 0.681, nsubj 0.776 -> 0.779, advcl 0.328 flat. The search gain needs the existing root-pick option moved from `score` to `left` (traced and counted in section 5; the in-order decode never reads it). LANDED-CAP CONFIRMATION (train 6000, the configuration the shipped asset is built at; point estimates, the paired CIs for this cap were still computing at hand-off): in-order UAS 0.6125 -> 0.6214, root 0.721 -> 0.764, ccomp 0.603 -> 0.664, xcomp 0.715 -> 0.737, obl 0.432 -> 0.463, conj 0.382 -> 0.403, nsubj 0.763 -> 0.776, advcl 0.321 -> 0.313; search UAS 0.6092 -> 0.6089, root 0.747 -> 0.749 (NOT down even under the incumbent root pick). The gain is LARGER at the landed cap than at the powered cap."
floor: "the IDENTICAL pipeline (same teacher, same cap, rounds 3, alpha 0.8, beta 10) with the root cues OFF. At train 6000 it reproduces the LIVE asset to 4 decimals: in-order UAS 0.6125 / root 0.721, search UAS 0.6092 / root 0.747 -- byte-for-byte the numbers the live asset scores. At train 1500: in-order 0.6163 / 0.7214, search 0.6178 / 0.7471. WEAKER FLOORS ALSO RUN, so the strongest is the one gated on: search decode with the `left` root pick and NO cues, root 0.7200 -- WORSE than the incumbent 0.7471, so `left` is not a free win and flips only together with the cues."
controls: "INFORMATION-FREE TWIN (same three cues, same density, cue values PERMUTED across the sentence's tokens), 3 seeds, n=700: in-order root 0.7100 / 0.7086 / 0.7057 vs base 0.7214 -- all BELOW; search root 0.6986 / 0.7029 / 0.7100 vs base 0.7200 -- all BELOW; and at the landed cap under the incumbent pick the twin collapses to root 0.527 vs base 0.747 (UAS 0.5734 vs 0.6178). ORACLE-CEILING probe run BEFORE building (+20 on the gold root arc, nothing else): in-order root 0.721 -> 0.943, UAS 0.6125 -> 0.6574. TIE COUNT: 378 of 700 sentences had >=2 candidates tied at the best root score before the change. UPSTREAM TRACE: teacher posterior mass on a gold ADJECTIVAL root arc 0.001 (100% below 0.05; ADV 0.000, PRON 0.000). CUE ABLATIONS (read-time, n=700, both decodes): rpred alone +0.0286 in-order; rsub alone +0.0029 (NULL, CI spans zero) under both; rpos alone +0.0286 in-order but -0.0114 search; dropping rpred costs the search arm everything (-0.0129). PATCH EQUIVALENCE: the proposed hdlab diff reproduces the cell's monkeypatched activations to max |delta| = 0.0 over 120 sentences, its own reference loop agrees with its fast path to 3.6e-15, and it is git-apply clean. REFUTED-AS-BUILT, each with its number: the zero-mean competition readout; the lateral-inhibition readout; the subordination-DIRECTED clausal construction; the cue-gain sweep."
files_changed: "experiments/exp_attachment_main_assertion_v1.py, notes/problems/the_main_assertion_is_a_scorer_deficit_the_governor_rates_non_verbal_predicates_and_subordinate_first_clauses_as_non_roots/{SOLVED.md,attachment_arm_patch.diff}, data/exp_attachment_main_assertion_v1*/metrics.json. NOTHING under hdlab/ or tools/ was edited -- the proposed change is the diff."
reverify: ".venv/Scripts/python.exe experiments/exp_attachment_main_assertion_v1.py --self-test   (18 scaffold-free checks: cue values on worked sentences, the patch is inert when off and touches only the root row, and the online observe path accrues a ROOT cue cell). Headline: HDLAB_EXP_NAME=attachment_main_assertion_v1_reverify .venv/Scripts/python.exe experiments/exp_attachment_main_assertion_v1.py --smoke --cap 1500 --test-cap 700 --arms base,cues -- writes only its own data/exp_* directory."
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

## 6b. THE SIGNAL TRACE, CHAIN BY CHAIN, WITH COUNTS (supervisor directive)

The signal the end read needs: *for each candidate word, is it the finite / copularly-predicating / non-subordinate
predicate?* Here is every hand-off it depends on, what each rung produces, what the next rung reads, and what is LOST.
UD's FEATS column is used ONLY as a measuring instrument (never read while learning).

| rung | what it produces | what the next rung reads | LOST, with counts |
|---|---|---|---|
| **1 tokens** | the surface string | the form, for morphological decomposition | nothing measurable |
| **2 categories** (`lexical_categories`, the live count organ) | a **HARD tag** (argmax), not a posterior | AUX / SCONJ / VERB / PART / ADJ, to key `rpred`, `rsub`, `rpos` | organ accuracy on exactly the tags the cues read: **AUX 0.9825 (n=572), VERB 0.9369 (967), PART 0.9684 (253), PRON 0.9709 (755), NOUN 0.9138 (1404), PROPN 0.8920 (1065), ADJ 0.8785 (543), SCONJ 0.7326 (172)**. Replacing gold categories with the organ's tags **flips a cue value on 231 tokens for `rpred` (2.4%), 370 for `rsub` (3.9%), 525 for `rpos` (5.5%)** of 9,534, and flips at least one cue value **on the GOLD ROOT TOKEN ITSELF in 59 of 700 sentences (8.4%)**. **SCONJ at 0.7326 is the weakest tag in the whole chain and it is precisely the input of `rsub` — which is why `rsub` measures NULL as a standalone cue.** |
| **3 lemma / morphology** (`hdlab/morphology` via `lemma_verb`) + the auxiliary frame | the finiteness class of a verbal candidate | `rpred` | against UD `VerbForm` (n=967 VERB tokens): Fin 357 → {ed 148, base 146, s 61}; Inf 289 → {to 127, **auxmod 115**, base 46}; Part 282 → {auxbe 111, **ed 65**, auxhave 54, ing 45}; Ger 39 → {ing 39}. **TWO CONFLATED VALUES: `ed` carries 148 finite pasts AND 65 bare participles; `base` carries 146 finite presents AND 46 infinitives — the same cue value for opposite predication status.** (A naive binary "morphologically finite" scores only 0.5874 here, but that is the wrong target: a verb under a modal or a perfect auxiliary is VerbForm=Inf/Part and still heads its clause. The cue's values encode the right distinction and the learned validities prove it: `to` −1.69, `ing` −1.85 against `auxmod` +0.46, `auxbe` +0.26, `s` +0.52.) The residual loss is the two conflated values. |
| **4 cue activations** (`arc_scores`, the root row) | an additive log-odds contrast per candidate — graded, and after this work non-degenerate (before: 17 numbers, 378/700 sentences tied) | the decode | the additive form cannot represent an INTERACTION, so the `ed`/`base` conflation cannot be resolved inside it |
| **5 in-order decode** (`incremental_tree`, beam 8) | a beam posterior over heads — the keep-alternatives-alive hand-off | consumers | **the gold root arc carries non-zero belief in the final beam in only 227 of 300 sentences (0.757); mean belief 0.726.** In ~24% of sentences the true main assertion has already been pruned from the beam, so no root-row evidence can recover it. Beam width is a swept operating point (currently 8) — the cheapest remaining lever. |

**BRAIN-FOUNDATIONAL STATUS OF EACH RUNG *AS IT RELATES TO THIS SIGNAL*** — not the registry label, but whether it
actually hands down the graded signal this read needs:

| rung | graded? | verdict on THIS signal |
|---|---|---|
| categories | **NO — a hard argmax tag.** `arc_scores_graded` exists and keeps the second-best category alive for ordinary arcs, but `root_cue_values` is computed from one hard tag list, so an uncertain AUX/SCONJ is committed before the competition sees it | **NOT BF for this signal.** The brain keeps the category alternative alive (MacDonald 1994); we collapse it. Named fix: route the root cues through the same top-2 mixture |
| morphology | partially — a categorical class with two conflated values | **BF in mechanism, lossy in resolution** |
| cue activations | **YES** — graded, learned, plastic log-odds contrasts | **BF** — this is what the work fixed |
| in-order decode | **YES** — a bounded weighted beam | **BF in form, lossy in width**: 24% of true roots pruned |
| the search decode's root PICK | **NO — an argmax over a tree-filtered subpopulation, using strengths calibrated over a different population** | **NOT BF**; the mismatch is measured in section 5 |

**THE BRAIN'S MATH AT EACH RUNG, AND WHAT IS BUILT**

| rung | the brain's computation | what is built | gap |
|---|---|---|---|
| the root decision | cue competition: activation = Σ (cue validity × cue availability), winner-take-all for one slot (Bates & MacWhinney 1989; MacWhinney 1987) | additive log-odds contrast per (configuration, cue value) learned from soft counts; argmax/beam for the winner | validity learned, availability implicit (a cue that does not apply contributes exactly 0). Matches. |
| finiteness | morpho-orthographic decomposition then a lexical check (Rastle & Davis 2008; Taft 1979) plus frequent frames (Mintz 2003) | token-vs-lemma suffix class + nearest preceding auxiliary / `to` | matches in operation; loses Fin vs bare-Part on `-ed` |
| subordination | the complementizer marks its clause dependent, and children learn dependency FROM the complementizer (Diessel 2004) | nearest preceding clause opener with no intervening predicate | matches; **the input tag is 0.7326, which is where this cue dies** |
| prediction / hold | surprisal-weighted expectation of a head still to come (Levy 2008) decaying by ACT-R base-level activation (Lewis & Vasishth 2005) | `hold_expectation` × decay^age, learned from the organ's own trees | already built by the arm; untouched here |
| reanalysis | an alternative overtakes when later evidence reverses the ranking (MacDonald 1994) | `INCR_ROOT_REANALYSIS` — an arriving word may take the root arc over | already built; it could not help before because the activations it re-ranks on were flat. **After this work it has something to re-rank on.** |

## 6c. THE NEGATIVES, EACH UNDERSTOOD MECHANISTICALLY (supervisor directive)

1. **Zero-mean "competition" readout — REFUTED, and the reason is counted.** Rationale: one root slot, so the
   evidence should be zero-sum. Measured: worse under BOTH decodes (in-order +0.021 vs +0.034 flat; search −0.049 vs
   −0.030). **Mechanism:** decomposing the search decode's root decision showed **120 of 177 root misses have the
   gold root OUTSIDE the unconstrained MAP root set entirely** — the failure is the root-vs-attach MARGIN, which
   centring removes by construction, not the ranking, which centring preserves.
2. **Lateral-inhibition readout (`d − max d`) — REFUTED.** Rationale: a competition is inhibitory (Usher &
   McClelland 2001). Measured in-order root −0.019, search −0.031, at every gain (0.5 / 1 / 2). **Mechanism:** every
   contribution becomes ≤ 0, depressing the root row globally — the same margin damage as (1), one-sided.
3. **Subordination-DIRECTED clausal construction — NULL and costly (xcomp 0.724 → 0.632).** **Mechanism:** splitting
   `clausal` into a forward and a reversed family halves the count mass behind each learned validity and the reversed
   family gets no convention bonus, so both weaken; and the `wh` trigger fires on relative clauses, where the
   reversed arc is *also* wrong (the gold arc is `acl:relcl` to the NOUN, not to the matrix verb).
4. **`rsub` as a standalone cue — NULL (+0.0029 in-order, +0.0029 search; both CIs span zero).** **Mechanism, now
   traced:** its only input is the SCONJ tag, the weakest in the chain at **0.7326**, flipping a cue value on 370
   tokens when the organ's tags replace gold. Subordination is not the problem — the learned validity is a clean
   `ROOT:VERB|sconj` **−1.42** against `|none` **+0.44** — the cue simply cannot fire reliably on the live tags.
5. **Conjunctive finiteness (`ed` × subject-support) — KILLED ON A WORKED EXAMPLE BEFORE SPENDING A BUILD.** The
   rung-3 trace says `ed` conflates 148 finite pasts with 65 bare participles, so I added a conjunctive value. It is
   **the wrong disambiguator**: "the man SEEN yesterday LEFT" and "the man WALKED home" both have a nominal to the
   left with no intervening predicate, so both get `edS`. The real disambiguator is whether ANOTHER finite predicate
   later in the clause already claims that nominal — i.e. candidate RANK, which is what `rpos` encodes, which is why
   `rpos` carries independent signal (+0.0286 alone). The correct next form is `rpred × rpos` as a conjunctive value
   for the ambiguous classes only. Code kept behind the `conj` arm, default OFF, not shipped.
6. **The predication teaching boost is neutral on the end number.** It does exactly what it is for (`ADJ|cop` +3.47 →
   +4.35, `VERB|sconj` −0.74 → −1.42) but the end delta is 0.007 lower than read-time cues alone — inside the CI
   half-width. **Mechanism:** the arm runs 3 self-teaching rounds at alpha 0.8, so the arm's own posterior dominates
   the teacher's and a teacher correction is largely re-absorbed. Kept (it is the brain-foundational upstream repair,
   gamma swept, 0 selectable) but named honestly as not carrying the result.

## 6d. WHAT MADE THIS WORK, RUNG BY RUNG (owner addendum)

The gain came from cracking the chain at the one rung where the brain's math was **entirely absent** — not from tuning.

- **Where the chain WAS cracked.** The root decision was the only place in this organ where a **cue competition had
  been replaced by a per-category prior**: `cues(j, 0)` returned `{}`. Everything downstream of it was already
  brain-faithful and graded — the arc activations are learned log-odds contrasts, the decode keeps a weighted beam of
  alternatives, and root REANALYSIS was already implemented. **Those rungs had nothing to re-rank on.** Supplying real
  graded evidence at the one missing rung is what let the already-BF machinery below it do its job, and the numbers
  show exactly that: the in-order decode (which HAS reanalysis) gains **+0.043 root at the landed cap** while the
  whole-sentence search (which has no reanalysis, only an argmax) gains **+0.002**. The rung that was cracked and the
  rung that gained are the same chain.
- **Where the upstream was cracked.** The acquisition teacher put **0.001** posterior mass on adjectival root arcs.
  Repairing that treebank-free, from the copula frame the organ already had, is what gave the copular cue a validity
  to learn: `ROOT:ADJ|cop` **+4.35** against `ROOT:ADJ|hasv` **−6.20** — from counts, nothing hand-weighted.
- **Where it is NOT cracked — the rungs still handing down a point estimate or a conflated value:**
  (a) **categories hand down a HARD tag**, not the posterior the competition should marginalise over (8.4% of gold
  root tokens already carry a flipped cue value before the competition starts); (b) **`rpred` conflates two opposite
  predication statuses** in `ed` (148 vs 65) and `base` (146 vs 46); (c) **the beam prunes the true main assertion in
  24% of sentences**; (d) **the search decode's root PICK is an argmax whose strengths are calibrated over the wrong
  population.** Each of those is a number, and each is a next build.

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
