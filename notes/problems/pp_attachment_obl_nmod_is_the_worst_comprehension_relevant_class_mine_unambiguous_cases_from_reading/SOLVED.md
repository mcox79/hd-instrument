---
problem: pp_attachment_obl_nmod_is_the_worst_comprehension_relevant_class_mine_unambiguous_cases_from_reading
status: SOLVED
bar: "obl and nmod recall CI-separated above the current asset on UD-EWT test 700, UAS not down, twin far below, knowledge in counts with an online observe path, witness green -- OR a located negative with the oracle-association probe number."
result: "UD-EWT test 700, gold categories, train cap 1500, paired bootstrap over sentences (2000 resamples), measured on the CURRENT WORKING TREE (committed HEAD + the pri-97 main-assertion diff that strategy applied at 19:39; hdlab/attachment_arm.py sha1 dd645eebf25d, stamped in every metrics file). ARM `objgen` = the widened case-marked-nominal retrieval + the preposition association mined from 100,000 Simple-Wiki lines + the typed thematic channel + the genitive construction. IN-ORDER decode (the live default): UAS 0.6246 -> 0.6373 (+0.0127, CI [+0.0090,+0.0164]); obl 0.449 -> 0.535 (+0.0860, CI [+0.0577,+0.1167]); nmod 0.410 -> 0.491 (+0.0805, CI [+0.0498,+0.1148]); the retrieved case-marked subpopulation 0.506 -> 0.579 (+0.0735, CI [+0.0448,+0.1018]). SEARCH decode (map1): UAS 0.6188 -> 0.6327 (+0.0138, CI [+0.0105,+0.0173]); obl 0.444 -> 0.532 (+0.0881, CI [+0.0609,+0.1168]); nmod 0.388 -> 0.513 (+0.1255, CI [+0.0904,+0.1644]). On the item's OWN population (the 599 gold obl/nmod tokens the detector retrieves): obl 0.4715 -> 0.5856 (+0.1141, CI [+0.0748,+0.1576], n=333); nmod 0.5489 -> 0.5714 (+0.0226, CI [-0.0149,+0.0569], n=266, NOT separated -- the nmod gain is in the genitive/possessive population, which is outside the PP sites by construction). Downstream consumer (graded_role_assigner.coarse_roles over these heads) 0.5755 -> 0.5793. Reproduced independently in two separate processes to 4 decimals."
floor: "the IDENTICAL pipeline with the change off (`base`), rebuilt from the same teacher, the same training slice and the same rounds: in-order UAS 0.6246 / obl 0.449 / nmod 0.410, search UAS 0.6188 / obl 0.444 / nmod 0.388. STRONGER FLOORS ALSO RUN: (a) `flat` -- the SAME cue firing on the SAME arcs with a CONSTANT value, i.e. the retrieval structure with no association content at all: UAS +0.0023 n.s., obl +0.0461*, nmod -0.0187 n.s.; (b) `twin` -- the scrambled association (below); (c) `gen` -- the genitive construction alone: UAS +0.0061*, obl +0.0126*, nmod +0.0655*; (d) `obj` -- the association without the genitive: obl +0.0776*, nmod +0.0169 n.s. The winning arm beats the STRONGEST of these CI-separated on every headline number: vs `flat` UAS +0.0104 CI [+0.0077,+0.0132], obl +0.0398 CI [+0.0186,+0.0641], nmod +0.0993 CI [+0.0741,+0.1263]."
controls: "INFORMATION-FREE TWIN (each host's preposition profile and each (host-type, preposition) object-class profile reassigned to another host/cell -- identical counts, identical density, identical marginals, only WHICH host has WHICH profile destroyed): in-order UAS 0.6292, obl 0.503, nmod 0.414, i.e. the winning arm beats its twin CI-separated on UAS (+0.0081 CI [+0.0053,+0.0110]), obl (+0.0314 CI [+0.0086,+0.0567]), nmod (+0.0768 CI [+0.0506,+0.1052]) and the retrieved subpopulation (+0.0351 CI [+0.0137,+0.0580]); on the retrieved obl subpopulation +0.0480 CI [+0.0138,+0.0851]. THE TWIN IS NOT AT ZERO and this is reported against the submission: the scrambled association still lifts obl +0.0545, because scrambling preserves WHICH arcs the cue fires on. That is why the `flat` constant-value control exists -- it isolates the retrieval structure (obl +0.046*, nmod -0.019 n.s., UAS n.s.) from the association content (objgen vs flat: obl +0.040*, nmod +0.099*, retrieved-subpopulation obl +0.057* and nmod +0.060*). ORACLE-CEILING PROBE, run before building and again after: with a perfect association over the retrieved candidate set, obl 0.449 -> 0.746 and nmod 0.410 -> 0.543, UAS 0.6246 -> 0.6539 -- the channel is worth ~3 UAS points and the shipped arm takes 43% of it. KNOWN-FACT CHECK on the mined association (no supervision anywhere): log[P(p|verb-class)/P(p|noun-class)] = -1.354 for `of`, -0.921 `during`, -0.682 `between`, +1.613 `by`, +1.449 `about`, +1.320 `to`; P(to|go)=0.538, P(in|live)=0.697, P(of|picture)=0.560, P(in|house)=0.131. LEARNED-LADDER CHECK: the organ learns a monotone validity ladder for the cue values it was never told to order -- l2 -0.255 < l1 -0.041 < 0 +0.334 < w1 +0.613 < w2 +1.281. NO-REGRESS on every core relation (in-order): root 0.759 -> 0.764, nsubj 0.780 -> 0.780, obj 0.777 -> 0.785, case 0.715 -> 0.755, xcomp 0.730 -> 0.730, ccomp 0.647 -> 0.647, conj 0.382 -> 0.386, punct 0.466 -> 0.467; advcl 0.321 -> 0.313 is the only fall (-0.008, 134 items). PATCH EQUIVALENCE: the proposed diff, applied in memory and executed, produces cue values identical to what was measured on 40 sentences / 385 arcs, an identical genitive construction, and its own fast path matches its own reference loop to 1.8e-15. WITNESS: verification/test_attachment_arm.py 17/17 at HEAD; the cell's own scaffold-free self-test 22/22. THREE REFUTED-AS-BUILT routes recorded with numbers and mechanisms (below)."
files_changed: "experiments/exp_attachment_pp_association_unambiguous_mining_v1.py, notes/problems/<slug>/{SOLVED.md,attachment_arm_pp_patch.diff}, data/exp_attachment_pp_association_unambiguous_mining_v1/** (mined associations + metrics), data/hook_state/attachment_pp_assoc_v2_simplewiki100k_candidate.json (the candidate asset). NOTHING under hdlab/ or tools/ was edited -- the proposed change is the 537-line diff."
reverify: ".venv/Scripts/python.exe experiments/exp_attachment_pp_association_unambiguous_mining_v1.py --self-test   (22 scaffold-free checks, writes nothing).  Patch check: .venv/Scripts/python.exe experiments/exp_attachment_pp_association_unambiguous_mining_v1.py --verify-patch notes/problems/pp_attachment_obl_nmod_is_the_worst_comprehension_relevant_class_mine_unambiguous_cases_from_reading/attachment_arm_pp_patch.diff.  Headline: HDLAB_EXP_NAME=attachment_pp_assoc_reverify OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 .venv/Scripts/python.exe experiments/exp_attachment_pp_association_unambiguous_mining_v1.py --full --cap 1500 --test-cap 700 --lines 100000 --arms base,flat,objgen,twin --decodes incr,map1 --boot 2000 --twin-obj --pairs flat:objgen,twin:objgen  -- writes only its own data/exp_* directory."
---

> **COMPLETION.** The PP cue on disk could not see two thirds of its own problem. `pp_site` offered exactly TWO
> candidates and only for a NOUN/PROPN object sitting directly after a determiner or adjective: it fired on 253 of
> 477 gold obl and 195 of 534 gold nmod, and for 109 of those the gold head was neither candidate — **at most 33.5%
> of the obl+nmod population was decidable by the cue at all.** Building the brain's actual mechanism — case marking
> opens the search, ALL open hosts are retrieved under a capacity limit, and the host–preposition association
> learned from unambiguous experience decides among them — takes that to 55.0%, and adding English's OTHER case
> marker (the genitive) reaches the 42% of nmod that no preposition can touch. **obl +0.086 and nmod +0.081, both
> CI-separated, UAS UP +0.0127, every other core relation flat or up, and the arm beats both a scrambled twin and a
> constant-value twin of its own structure CI-separated.** Three routes were refuted as built with their mechanisms
> read off the learned validity tables.

---

## 1. HOW THE BRAIN DOES THIS (the opening move)

A prepositional phrase is a **case-marked nominal looking for a host**, and the reader decides its host with the
same machinery it uses for every other attachment.

| # | the brain's step | status | our counterpart |
|---|---|---|---|
| 1 | **CASE MARKING identifies the dependent and opens the search.** A case marker marks the phrase as oblique (Pinker 1984 semantic bootstrapping; the Competition Model's case cue, Bates & MacWhinney 1989 — the strongest cue in case-marking languages). | PINNED | `pp_sites`: a preposition opens a case-marked nominal whose head is the run head after it. English's other case marker, the genitive, is `genitive_arcs`. |
| 2 | **CANDIDATES ARE RETRIEVED, not enumerated as a fixed pair.** Cue-based retrieval from working memory over everything still open that can license the phrase — verbs, predicate/attributive adjectives, relational nouns — with activation decaying over distance and a capacity limit (Lewis & Vasishth 2005; Gibson 1998 DLT). | PINNED | every open host to the left of the preposition inside the sentence, nearest first, capped at `PP_KCAP`. Distance is not re-encoded here: the arm's own `locality` cue already carries it. |
| 3 | **LEXICAL ASSOCIATION between host and preposition is the discriminating cue** (Hindle & Rooth 1993; MacDonald, Pearlmutter & Seidenberg 1994 constraint integration), and what competes is the CONTRAST across candidates, not an absolute number — divisive normalisation into a population code (Carandini & Heeger 2012; the organ spec's principle 3). | PINNED (that association is the cue) / MODEL (the log-share form) | `pp` cue value = the bin of log[P(p\|h) / mean over the retrieved population]. |
| 4 | **THEMATIC EXPECTATION: what the phrase is ABOUT matters too.** "ate the pizza with a fork" is an instrument of the verb; "with anchovies" is a part of the noun (Taraban & McClelland 1988; Ratnaparkhi 1998's fourth element; typed, not lexical — McRae, Ferretti & Amyote 1997 role-as-feature-bundle). | PINNED (typed thematic fit) / MODEL (the class-conditional form) | `ppobj` cue value = the same contrast on log P(class of the object \| host type, preposition), the class being the WordNet supersense the typed selectional-preference organ already reads. |
| 5 | **IT IS LEARNED FROM UNAMBIGUOUS EXPERIENCE.** The cases where only one host was available give clean evidence; the ambiguous ones are then apportioned by the current estimate and re-estimated (Hindle & Rooth 1993's reallocation; Ratnaparkhi 1998 mines exactly this from ~970k raw sentences: 81.9% against a 70.4 baseline, no treebank). | PINNED | `pp_assoc_v2_from_reading`: 23,026 unambiguous sites seed the counts, 102,499 ambiguous ones are reallocated for 2 rounds. |

**OURS, swept and never adopted:** the retrieval cap (4/6/8/12 → 546/556/556/556 gold hosts retrievable; **6 is the
knee**), the shrinkage constants, the z-bin edges, the reallocation rounds, and the reading volume.

---

## 2. THE SIGNAL-LOSS TRACE (measured on disk before anything was built)

**The chain this read depends on, rung by rung, and what each hands down.**

| rung | organ | BF status on disk | what it hands the PP decision | what is LOST |
|---|---|---|---|---|
| tokens | `hdlab/frontend.tokenize` | glass-box regex | the word forms | nothing here |
| categories | `hdlab/lexical_categories` | BF_SPIRIT (count-based generative model, forward-backward posterior; counts from the UD tag column = offline supply) | a POSTERIOR per token | my numbers use the rung's gold-UPOS stand-in, so category uncertainty is **not** in them; the association mined from Simple-Wiki DOES use the organ's own tags |
| lemma | `hdlab/morphology`, `lemma_verb` | BF | the host key and the noun supersense lookup | nothing measured |
| **heads** | `hdlab/attachment_arm` | BF_SPIRIT | the PP cue lives here | **the loss below** |
| consumers | `graded_role_assigner.coarse_roles`, the situation-model board | BF_SPIRIT | OBL vs OBJ vs NSUBJ off these heads | 283 gold nmod are labelled `obl` and 179 `dep` at base — the head error propagates |

**Where the signal was lost, with counts (UD-EWT test 700):**

| loss | count |
|---|---|
| gold obl tokens the incumbent `pp_site` fires on | **253 / 477 (53%)** |
| gold nmod tokens it fires on | **195 / 534 (37%)** |
| of those, gold head is NEITHER of the two offered candidates | 63 obl + 46 nmod |
| **so: decidable by the cue at all** | **339 / 1011 = 33.5%** |
| PP object is a PRON | 109 nmod + 44 obl |
| PP object is a NUM | 36 nmod + 19 obl |
| a compound/possessive inside the NP stops the leftward scan ("of Google 's new toolbar", "on your hands") | 98 obl + 77 nmod |
| the host is a predicate ADJECTIVE ("capable OF …") | 24 obl |
| the host is a noun that is not the nearest one | 23 nmod |
| the association itself | 6,000 UD sentences → 2,230 verb\|prep + 3,580 noun\|prep cells; **ambiguous sites credited 0.5/0.5 forever** (Hindle & Rooth's initial estimate WITHOUT their reallocation step) |
| the learned cue table | **29 cells** in the live asset |

**A SECOND loss, found by walking the same chain and NOT in the brief.** The read-time meaning cue and the
semantic-bootstrapping teacher both ask "is this nominal case-marked?" with `pos[j-2] == "ADP"` — the preposition
*immediately* before the noun. A case marker marks the **phrase**, and any NP with more than one modifier breaks
adjacency: **684 nominal run heads on the test set are case-marked by the phrase rule and only 396 by the adjacency
rule — 436 missed (63.7%), of which 199 are gold obl and 144 gold nmod**, each handed to the meaning cue as a
candidate SUBJECT or OBJECT of a nearby verb. Two repairs were built for it; **both are refuted as built** (§5), and
understanding why is the most useful thing in this submission.

**After the rebuild:** detection 333/477 obl and 266/534 nmod; gold host inside the retrieved candidate set for
**313 + 243 = 55.0%** of the population (from 33.5%).

---

## 3. WHAT WAS BUILT

1. **`pp_sites`** — case-marked-nominal detection driven by the PREPOSITION, the object taken as the head of the
   nominal run after it (the arm's own NP-run convention widened to compounds, possessives and the enclitic), and
   the candidate hosts = every open verb / adjective / nominal-run-head to the left, nearest first, capped at 6.
2. **`PPAssoc`** — P(preposition | host) held as **plastic counts** with Dirichlet shrinkage lemma → class → the
   preposition's own marginal (verbs and adjectives back off to their category, nouns to their WordNet supersense —
   the Resnik-style type generalisation the typed selectional-preference organ already uses). `observe(...)` accrues
   one comprehension outcome online; the probability is one pure function of the counts.
3. **The thematic channel** — P(class of the prepositional object | host type, preposition), the same count form.
4. **Mining from reading, treebank-free** — 100,000 Simple-English-Wikipedia lines tagged by **the substrate's own
   count-based category organ** (`hdlab.lexical_categories`); 125,525 case-marked sites, **23,026 unambiguous** seeds
   and 102,499 ambiguous ones reallocated for 2 Hindle-Rooth rounds → **17,118 host cells / 58,161 association
   cells** (against 1,914 host cells from the 1,500-sentence UD slice, and 29 learned cue cells in the live asset).
5. **`genitive_arcs`** — English's other case marker, as an item-based construction whose validity the arm learns
   like every other construction.

**No treebank tree is read during learning. No spaCy, no nltk tagger, no supervised parser, no external model.** The
UD treebank appears only as the measuring instrument and as the categories rung's acknowledged gold-UPOS stand-in.

---

## 4. THE RESULT

**UD-EWT test 700, gold categories, train cap 1500, in-order (live) decode. `*` = CI-separated, paired bootstrap.**

| arm | UAS | obl | nmod | retrieved subpop | what it is |
|---|---|---|---|---|---|
| `base` (floor) | 0.6246 | 0.449 | 0.410 | 0.506 | the identical pipeline, change off |
| `flat` | 0.6269 | 0.495* | 0.391 | 0.521 | **control:** same arcs, CONSTANT value |
| `twin` | 0.6292 | 0.503* | 0.414 | 0.544 | **control:** scrambled association |
| `gen` | 0.6307 | 0.461* | 0.476* | 0.512 | the genitive construction alone |
| `obj` | 0.6315 | 0.526* | 0.427 | 0.573 | association + thematic channel |
| **`objgen`** | **0.6373*** | **0.535*** | **0.491*** | **0.579*** | **the shipped build** |
| oracle | 0.6539 | 0.746 | 0.543 | 0.858 | *instrument:* perfect association over the retrieved set |

`objgen` vs base: UAS **+0.0127** CI [+0.0090,+0.0164]; obl **+0.0860** CI [+0.0577,+0.1167]; nmod **+0.0805**
CI [+0.0498,+0.1148]. Search decode: UAS +0.0138, obl +0.0881, nmod **+0.1255** CI [+0.0904,+0.1644].
`objgen` vs `flat`: UAS +0.0104*, obl +0.0398*, nmod +0.0993*. `objgen` vs `twin`: UAS +0.0081*, obl +0.0314*,
nmod +0.0768*. **The seesaw the brief named is gone: obl and nmod rise together, under both decodes.**

**No-regress, in-order, all core relations:** root 0.759→0.764, nsubj 0.780→0.780, obj 0.777→0.785, case
0.715→0.755, xcomp 0.730→0.730, ccomp 0.647→0.647, conj 0.382→0.386, punct 0.466→0.467, **advcl 0.321→0.313** (the
only fall, −0.008 on 134 items). Downstream consumer (§7) 0.5755 → 0.5793.

**Volunteered against the submission.** (a) The scrambled twin is NOT at zero — it gains obl +0.0545 on its own,
because scrambling preserves *which arcs the cue fires on*; the `flat` control was built precisely to separate that,
and the association content is worth obl +0.040 / nmod +0.099 over it. (b) On the *retrieved* subpopulation the nmod
gain over base is **+0.0226, NOT CI-separated** (CI [−0.0149,+0.0569], n=266) — the nmod headline comes from the
genitive/possessive population, which lies outside the PP sites by construction; the association's nmod contribution
shows up cleanly only against `flat` (+0.0602*). (c) The measurement is at train cap 1500, not the landed 6,000.

---

## 5. THE THREE REFUTED ROUTES, EACH WITH ITS MECHANISM

**(a) The "strongest rival" readout (the literal two-candidate Hindle-Rooth contrast, generalised).**
Value = log P(p|h) − log max over the OTHER candidates. Measured (cap 1200, test 250): obl 0.443→0.502 but nmod
0.454→**0.393** under the search decode. **Mechanism:** the strongest rival of a noun host is almost always a verb
(verbs carry far more preposition mass), so inside the `NOUN>NOUN` configuration nearly every value is a losing bin
— the losing bin IS that configuration's baseline, its learned contrast collapses to ~0, and the cue degenerates
into "prefer a verb", a type prior the CONFIGURATION already owns. Replaced by the population share; kept selectable
as `HDLAB_ARM_PP_ZFORM=max`.

**(b) The phrase-level case rule, ZEROING form** (a case-marked nominal is not a core participant, so the meaning
cue is silent). obl 0.449→**0.380** alone; 0.449→**0.199** together with the PP cue. **Mechanism, read straight off
the learned table:** the over-broad adjacency guard was the ONLY thing teaching the arm that a verb takes an oblique
argument at all. Zero it and the acquisition teacher stops putting mass on verb→PP-object arcs, and the organ learns
thematic validities of **−1.5 to −1.8** for every V-family value (from about +0.5) — it concludes that a verb never
hosts a case-marked nominal.

**(c) The phrase-level case rule, OBLIQUE-SLOT form** (still a participant, but in a separate slot value, so the
validity is learned apart from the direct-object slot). obl +0.0335*, nmod +0.0243* — but **worse than leaving the
guard alone** (obl 0.482 vs 0.526, UAS 0.6281 vs 0.6315). **Mechanism:** 87% of gold obl is prepositional and its
host IS a verb, so the blanket verb pull is NET CORRECT; what separates obl from nmod is the ASSOCIATION, not the
guard. Both forms ship default OFF behind `HDLAB_ARM_PP_CASE_RULE`, with the numbers in the source.

---

## 6. KEY REALIZATIONS

1. **Check what the cue can even see before improving what it says.** The brief asked for a better association; the
   first measurement said the detector reached 33.5% of its own population. Coverage, not quality, was the wall.
2. **A twin that preserves structure is not information-free.** The scrambled association still gained obl +0.055,
   because scrambling keeps *which arcs fire*. The constant-value control (`flat`) is what actually separates
   structure from content, and it changed the reading of the result.
3. **A contrast against the strongest rival is not symmetric.** Any readout that compares a candidate to "the best
   other" inherits the type asymmetry of the population and turns an association cue into a type prior. Normalising
   over the whole retrieved population fixed the nmod/obl seesaw in one edit.
4. **When removing a wrong mechanism costs more than it saves, the wrong mechanism was carrying a right signal.**
   The over-broad case guard was the arm's only oblique-argument teacher. The lesson generalises: before deleting an
   over-broad rule, ask what it is the only source of.
5. **A relation is not a population.** Splitting nmod by construction (253 prepositional-with-site at 0.613, 98
   possessive pronouns at 0.449, 27 genitives at 0.074, …) turned "nmod is hard" into two separate, separately
   fixable problems, and the second one was worth more than the first.

---

## 7. ADJACENT COMPONENTS (capabilities, limits, brain status, and the next problems they seed)

| component | status | what this work shows |
|---|---|---|
| `graded_role_assigner.coarse_roles` (the role competition, **not edited**) | BF_SPIRIT | reads these heads and decides OBL vs OBJ. Role accuracy 0.5755 → 0.5793. **The flips strategy should trace:** at base, 283 gold `nmod` are labelled `obl` and 179 `dep`; under `objgen` 276 and 190. The head fix alone barely moves it — the labeler's OBL/NMOD distinction is driven by its own cues, not by the head, so **the head gain is not reaching the label rung.** That hand-off is a problem in itself. |
| `hdlab/lexical_categories` (categories rung) | BF_SPIRIT | supplies the Simple-Wiki tags the association is mined from. Every number here uses gold UPOS at read time (the rung's stand-in), so the live-chain figure will be lower; the association's own quality already survives the organ's tags. |
| `hdlab/typed_selectional_preference` + `noun_supersense_mfs_v1.json` | BF_SPIRIT | supplies the noun classes for the backoff and the thematic channel. Its `covers()` gap is the sparsity ceiling on the thematic channel. |
| `SemanticBootstrapTeacher` (the acquisition teacher) | BF_SPIRIT | its adjacency-based case guard is the single most load-bearing accident in the arm (§5b). **It should be repaired by giving the teacher an oblique slot with its own association, not by narrowing the guard.** |
| `attachment_arm.pp_site` / `pp_assoc_from_reading` / `pp_lr` (the incumbent) | superseded | kept in the patch for any table that carries only the old `pp_assoc`. |
| the `advcl` relation | −0.008 | the only fall; gerund complements ("capable of protecting") are deliberately out of scope for a case-marked-NOMINAL cue and are labelled `acl`/`advcl`. |

---

## 8. ALTERNATE PATHS — as brain-foundational or MORE so, for strategy to queue

1. **Give the acquisition teacher an OBLIQUE SLOT.** *Structure:* semantic bootstrapping (Pinker 1984) with three
   slots instead of two. *Computation:* an OBL-slot selectional association grown the way SUBJ and OBJ already are
   (`tools/grow_selectional_store_bf.py --role OBL`), so a case-marked nominal is scored as a plausible *oblique*
   participant rather than as a bad object. *Why not now:* it needs a third grown store and a rebuild of the
   plausibility assets; the two shortcut versions of it are refuted in §5. **This is the most brain-foundational
   thing left in this area** and it is what would let the case rule finally be right.
2. **Referential/definiteness context (Altmann & Steedman 1988; Spivey-Knowlton & Sedivy 1995).** *Structure:*
   the referential context of the candidate host NP — a definite host with a competing like referent invites the
   modifier reading. *Computation:* a cue value = definiteness of the host NP × whether a like-class referent has
   already occurred. Cheap, form-readable, named in the brief's refresh block and **not built here** — it is the one
   named lever this submission did not reach.
3. **More reading.** The curve is untested above 100k lines: 5k → 2,951 host cells, 100k → 17,118. Ratnaparkhi used
   ~970k sentences. Mining is category-organ-bound at ~35 ms/line; 500k lines is a ~5-hour offline job and the
   association is a static, plastic asset, so it is a pure win if the curve is still rising. **Measure the curve
   before paying for it.**
4. **Second-order sibling factorisation** (the sota drill's #1, +13.3 documented for label-free parsing). A PP host
   that already has a PP of the same preposition is a worse candidate — valence occupancy at the *phrase* level.
   Needs the projective second-order inside–outside; Matrix-Tree is first-order.
5. **Learn the retrieval cap instead of sweeping it.** Capacity-limited retrieval is PINNED; the cap 6 is ours. A
   decay-weighted candidate set (activation, not a hard cap) is strictly more faithful to Lewis & Vasishth.

---

## 9. HOW THIS COMPOSES WITH THE pri-97 DIFF

**It is already composed.** Strategy applied the pri-97 main-assertion diff to the working tree at 19:39, and every
number above was measured on that tree (`hdlab/attachment_arm.py` sha1 `dd645eebf25d`, stamped in each metrics
file). The proposed diff here is generated against **that** file, and `patch -p1 --dry-run` is clean on it.

*Note on a step left undone:* the brief asked me to apply the pri-97 diff to a copy of the module inside my own
experiment directory and measure against it. **That tool call was DENIED** and, per protocol, I did not retry it in
any form — the denial text is in the session log. It became moot: strategy landed pri-97 into the working tree
during the session, so "HEAD + pri-97" is exactly what `base` measures. The pre-97 numbers I do have are from the
19:30 smoke (cap 1200, test 250), labelled as such in `metrics_smoke.json`.

**Hunk-level relationship** (both diffs touch `hdlab/attachment_arm.py` and `tools/build_attachment_validities.py`):

| region | pri-97 | this diff | interaction |
|---|---|---|---|
| the `CUES` line | adds `ROOT_CUES` + `csub` | adds `"ppobj"` | **same line** — this diff is generated on top of the already-applied pri-97 line, so it carries both |
| after `_lr_bin` | inserts the main-assertion block | inserts the PP block | adjacent, sequential, no overlap |
| `SentenceCues.__init__` | adds `self.rootcues`, `self.csub` | adds `self.pp_arc`, `self.ppobj_arc`, `self.pp_cased` and a new keyword argument | same method, different statements |
| `SentenceCues.cues` | `h == 0` returns the root cues; adds the `csub` block | adds the v2 `pp` / `ppobj` values | disjoint arcs: root/subject arcs vs (host, PP-object) arcs |
| `arc_scores` | appends the root-row and `csub` blocks | inserts the v2 PP block before them | disjoint cells |
| `SemanticBootstrapTeacher.slot_plausibility` | untouched | adds the phrase case rule, **default OFF** | no interaction while off |
| `tools/build_attachment_validities.py` | adds `predication_boost` | adds the v2 mining + `--pp-assoc` | different hunks |

No semantic conflict anywhere: pri-97 decides which word carries the main assertion; this decides which word hosts
a case-marked phrase.

---

## 10. AUDIT UPDATE (`notes/BRAIN_FOUNDATIONAL_AUDIT.md`)

- `hdlab/attachment_arm.py` — the `pp` cue's entry should record that the **candidate set**, not the association,
  was the binding constraint (33.5% → 55.0% of the obl/nmod population retrievable) and that the association is now
  mined Hindle-Rooth-style from unambiguous reading with reallocation, at 58,161 cells.
- `SemanticBootstrapTeacher` — a NEW deviation to record: its case guard is `pos[j-2] == "ADP"`, which misses 63.7%
  of case-marked nominals, and that over-broad pull is currently the arm's only source of oblique-argument
  evidence. Narrowing it without an oblique-slot association is refuted with numbers.
- `hdlab/lexical_categories` — used offline here to tag 100k Simple-Wiki lines for a static knowledge asset; that is
  a new, admissible consumer of the categories rung worth listing.

---

## 11. NEXT STEPS (priority order)

1. **Land the diff and rebuild the asset at the landed cap 6000** with `--pp-assoc data/hook_state/attachment_pp_assoc_v2_simplewiki100k_candidate.json`, then re-run the board's no-regress check. *The solver cannot run the board on its own change: the arm loads a fixed asset path, and pointing it at a candidate asset would mean overwriting the live one.* That is the one gate this submission cannot close from here.
2. **Trace the heads → labels hand-off** (§7): the head gain is not reaching the OBL/NMOD label decision.
3. **Grow an OBL-slot selectional store** (§8.1) — the fix the two refuted case-rule forms were reaching for.
4. **Build the referential/definiteness cue** (§8.2) — the one named lever in the brief that was not reached.
5. **Measure the reading-volume curve** past 100k lines before paying for 500k.

---

---

# PHASE 7 — the continuation session (2026-09-13 late)

> A previous session was stopped mid-phase-7 by a compaction. Everything below is new work: the composition at the
> landed training cap, **the LIVE chain with no gold categories anywhere**, the heads → labels hand-off traced to its
> cause, and six further levers built and measured — of which **one is a clean win, four are refuted as built with
> their mechanisms, and one is answered as "measured, do not pay for it"**. The shipped arm and the proposed diff are
> UNCHANGED; nothing in this phase reached the bar to be added to them.

## 12. WHAT PHASE 7 MEASURED

### 12.0 First: is the pipeline even reproducible? (it is, and the floor still moved)

Two byte-identical processes of the `base` arm (cap 1500, test 700) were run concurrently: **UAS 0.6252 / obl 0.440 /
nmod 0.408 (in-order) and 0.6119 / 0.426 / 0.382 (search) in BOTH**, to four decimals, and a third run of the same arm
inside a different arm list reproduced them again. The pipeline is deterministic.

**But the floor is not the same floor the first submission measured** (0.6246 / 0.449 / 0.410 in-order, 0.6188 search).
Between the two sessions something on disk changed. I checked, and could not find it: the treebank is byte-identical
and untouched since July, every asset `attachment_arm` reads (`typed_selectional_preference_bf_v1`,
`..._bf_subj_v1`, `selectional_slots_bf_v1.pkl`, `attachment_hold_expect_v1`) is older than the first measurement,
every module in the teacher path is older, and all 26 `HDLAB_*` switches are at their defaults in both sessions. The
assets that DID change at 20:41 (`attachment_validities_v1.json`, `lexical_categories_counts_v1.json`,
`coarse_role_validities_ud_ewt.json`) are not read by the `base` build path — I traced each `load_attachment_validities()`
call site and every one of them takes the table as an argument.
**Reported against this submission, and the reason it does not invalidate anything: every comparison here is
WITHIN-RUN and paired over the same sentences, and the shift (obl −0.009) is a tenth of the effect (obl +0.10).**

### 12.1 THE LIVE CHAIN — no gold categories anywhere (the headline of this phase)

The first submission measured with the categories rung's **gold-UPOS stand-in**. Phase 7 measured the chain the reader
actually runs: `hdlab.lexical_categories` (the count-based generative category organ) tags the sentence and hands DOWN
its per-token posterior; the attachment competition marginalises over it (`arc_scores_graded`); the PP detector, the
nominal runs and the candidate hosts are all read off the ORGAN'S OWN tags. This is byte-for-byte the path
`hdlab/frontend.Parser.parse` takes at `HDLAB_TAG_SOURCE=counts` (default) and `HDLAB_HEADS_SOURCE=attachment_arm`
(default) — I checked the frontend source against the probe.

**Train cap 6000 (the landed cap), UD-EWT test 700, in-order decode, paired bootstrap over sentences, 2000 resamples.**

| | UAS | obl | nmod | retrieved PP subpop |
|---|---|---|---|---|
| base, gold categories | 0.6239 | 0.4444 | 0.4288 | 0.5175 (n=599) |
| **objgen, gold categories** | **0.6364** | **0.4969** | **0.5112** | **0.5659** |
| delta | **+0.0125** [+0.0087,+0.0168] | **+0.0524** [+0.0189,+0.0873] | **+0.0824** [+0.0496,+0.1164] | **+0.0484** [+0.0182,+0.0808] |
| base, **LIVE** categories | 0.6125 | 0.4340 | 0.4438 | 0.5344 (n=582) |
| **objgen, LIVE categories** | **0.6243** | **0.4969** | **0.5075** | **0.5756** |
| delta | **+0.0117** [+0.0079,+0.0160] | **+0.0629** [+0.0321,+0.0948] | **+0.0637** [+0.0301,+0.0997] | **+0.0412** [+0.0132,+0.0709] |

**The win survives the live chain essentially intact** — every headline number stays CI-separated when the categories
come from the organ instead of from the treebank, and obl is actually LARGER live (+0.063 vs +0.052). The live chain
costs the arm about 1.1 UAS points overall (0.6239 → 0.6125 at base) and the PP cue loses 17 of its 599 detected sites
(599 → 582) to category errors — a 2.8% detection loss, which is the whole price the categories rung charges this cue.

### 12.2 THE COMPOSITION AT THE LANDED CAP 6000

Rebuilt at the training cap the landed asset uses, on the working tree that already carries the pri-97
main-assertion diff (`hdlab/attachment_arm.py` sha1 `dd645eebf25d`, stamped in every metrics file).
**A new control was added that the first submission could not run: the LANDED ASSET ITSELF, loaded from disk rather
than rebuilt** (`data/hook_state/attachment_validities_v1_pri97_cap6000.json`, byte-identical to the live
`data/frontend_assets/attachment_validities_v1.json`).

| arm | UAS | obl | nmod | what it is |
|---|---|---|---|---|
| `base` (rebuilt floor) | 0.6239 | 0.444 | 0.429 | the identical pipeline, change off |
| **the LANDED asset, loaded** | **0.6241** | **0.449** | **0.429** | the file the reader actually loads today |

**The rebuilt floor reproduces the landed asset to 0.0002 UAS.** That closes the one gap the first submission flagged:
its `base` really is the thing the board would regress against.

### 12.3 HEADS → LABELS: where the gain stops, and why (measured, not inferred)

The first submission observed that "the head fix alone barely moves" the role competition and asked strategy to trace
the hand-off. Phase 7 traced it, and the cause is structural, not gradual.

**`hdlab/graded_role_assigner` HAS NO NMOD CLASS.** Its inventory is
`ROLE_CLASSES = [SUBJ, OBJ, PASS_SUBJ, BY_AGENT, OBL, OTHER, IOBJ]` and `ROLE_TO_DEP` can emit only
`nsubj / nsubj:pass / obj / iobj / obl / obl:agent / dep`. **A gold `nmod` cannot be labelled correctly by this organ
whatever the heads rung hands it** — which is why 283 gold nmod came out `obl` and 179 came out `dep` at base, and why
the numbers barely move when the heads improve. This is now a self-test check in the cell, not an assertion.

The consequence at cap 6000 is a **downstream regression**: the role competition's accuracy over the nominals whose
gold relation it can express falls **0.5765 → 0.5622** (n = 2099) under the better heads, and the confusion moves the
way the mechanism predicts — `obl→dep` 61 → 96 and `nmod→dep` 195 → 214, because the improved heads move case-marked
nominals OFF verbs and onto nouns, and a nominal not governed by a verb has nowhere to go in this inventory but `dep`.
**Per the standing discipline this is not a reason to revert the upstream rung; it is a consumer that must be repaired
to receive the richer signal.** The repair is one role class, and the distinction is free: in UD, and in the brain's
own terms, `obl` versus `nmod` is a pure function of the HOST'S CATEGORY — a case-marked phrase licensed by a predicate
is an oblique participant of an event, one licensed by a nominal is a property of a thing. A consumer that reads the
host's category converts every head gain on this population into a label gain one-for-one.

### 12.4 A NEW INSTRUMENT: what the channel decides, with the decode taken out of the way

Per-relation recall confounds four things — whether the case-marked nominal is DETECTED, whether the gold host is
RETRIEVED, whether the association RANKS it first, and whether the tree competition then keeps it. The cell gained a
table-free, decode-free probe (`--rank-probe`) that holds the first two fixed and measures only the third: over the
**556 gold obl+nmod tokens whose gold host is inside the retrieved candidate set**, how often does a given combination
of channels put the gold host on top? It is an instrument (the gold tree selects and scores the population), never a
build, and it costs 20 seconds instead of 40 minutes.

**It reframed the problem, and this is the most useful thing phase 7 learned.**

| ranking channel | all (n=556) | obl (n=313) | nmod (n=243) |
|---|---|---|---|
| **PROXIMITY alone** (the nearest open host) | **0.714** | 0.553 | **0.922** |
| the association alone | 0.480 | 0.463 | 0.502 |
| association + thematic (the shipped pair) | 0.484 | 0.463 | 0.510 |
| its scrambled twin | 0.284 | 0.361 | 0.185 |
| proximity + association | 0.718 | **0.601** | 0.868 |
| proximity + association + thematic | 0.710 | 0.597 | 0.856 |
| proximity + the scrambled twin | 0.610 | 0.572 | 0.658 |

Three things follow, each of which changes how the rest of this phase should be read.

1. **The association carries real signal** — 0.484 against its scrambled twin's 0.284 is not close. That is the
   submission's central claim, re-confirmed on a population and an instrument the submission never used.
2. **But proximity, not the association, is the floor on this population**, and for nmod proximity is almost a
   solved problem (0.922). The arm already carries proximity as its `locality` cue. So the association's job in this
   organ is not "decide the attachment"; it is "override proximity exactly where proximity is wrong", which is
   overwhelmingly the obl cases (proximity 0.553).
3. **Under a single global weight the association trades obl for nmod** (+0.048 obl, −0.054 nmod) — the seesaw the
   brief named. **The organ does not do that**, because it learns the cue's validity separately inside every
   configuration (head category × dependent category × order), so it can pull toward the verb in `VERB>NOUN` and
   toward the noun in `NOUN>NOUN` independently. That is the mechanism behind the submission's headline result — obl
   and nmod rising together — and it is why a fixed-weight probe under-reads what the organ gets. **The probe is a
   valid test of "does this channel carry information"; it is not a test of "will the organ use it".** Every channel
   below was therefore tested on BOTH.

### 12.5 SIX MORE LEVERS, BUILT AND MEASURED

#### (a) The referential / definiteness cue — REFUTED AS BUILT, with the mechanism

The one lever the brief's refresh block named and the first submission did not reach (its alternate path #2):
Altmann & Steedman 1988's referential context and Spivey-Knowlton & Sedivy 1995's definiteness × verb-bias crossing —
a definite host with a competing like referent invites the restrictive-modifier reading. Built as a cue in the arm's
own knowledge form: value = `<host type>:<definiteness of the host's own determiner>` plus an `R` marker when a like
referent (same lemma or same WordNet supersense) occurred earlier, validity learned by the arm's own counts.

**Measured (cap 1500, test 700, paired bootstrap): `objgenref` vs `objgen` — in-order UAS −0.0013 n.s., obl −0.0189
n.s., nmod −0.0187 n.s.; SEARCH decode UAS −0.0081\*, obl −0.0650\*, nmod −0.0693\*, retrieved-nmod −0.1353\*.**
Against its own twin it is indistinguishable everywhere except retrieved-nmod (+0.0301\* in-order). It costs
accuracy and adds no content.

**The mechanism, read straight off the learned validity table** (this is the whole value of the negative):

```
A:na +1.731   V:na +0.315   N:name -1.873   N:nameR -1.800
N:indef +0.515  N:indefR +0.734   N:def +0.369  N:defR +0.599   N:bare +0.184  N:poss +0.417
```

Almost all of the learned mass sits on `A:na`, `V:na` and `N:name` — i.e. on **"is the host an adjective, a verb, or a
proper noun"**, which is a HOST-TYPE PRIOR the configuration already owns. This is the identical failure the first
submission diagnosed for the "strongest rival" readout in §5(a), arriving by a different door. And the definiteness
contrast the literature predicts is not merely small, it is **reversed**: indefinite hosts (+0.515) outrank definite
ones (+0.369), and the rival-referent marker adds only ~+0.22. Because the cue fires on exactly the arcs the `pp` cue
fires on, the additive competition re-splits the credit and **compresses the association's own ladder** (w2 1.241 →
1.046, l2 −0.255 → −0.302) — that is the numeric cause of the loss.

**Why the effect is absent, and what would find it.** Altmann & Steedman's referential context is a property of the
DISCOURSE MODEL — how many salient referents of that kind the listener is already entertaining. My `has_rival_referent`
could only scan the CURRENT SENTENCE, because that is all the attachment arm is handed. **The cue was built at the
wrong scope.** The right build reads the rival-referent count off the entity / situation layer (the coref organs), and
it is a cross-organ lever, not a cue this arm can grow on its own. Logged as a lead below.

#### (b) More reading — MEASURED, AND THE ANSWER IS "DO NOT PAY FOR IT" (alternate path #3)

The first submission asked for the reading-volume curve before paying for a 500k-line mining job. Measured on the
channel probe at 5,000 lines (2,951 host cells) against 100,000 lines (17,118 host cells) — a 20× increase:

| | association alone | its scrambled twin | real − twin | on the proximity floor |
|---|---|---|---|---|
| 5,000 lines | 0.4388 (obl 0.4633, nmod 0.4074) | 0.3327 | **+0.106** | 0.7194 |
| 100,000 lines | 0.4802 (obl 0.4633, nmod 0.5021) | 0.2842 | **+0.196** | 0.7176 |

**The association really is still learning** — its margin over its own twin nearly doubles, and the whole of the gain
is on the NOUN side (nmod 0.407 → 0.502; **obl is 0.4633 at both volumes, identical to four decimals** — the verb side
saturates by 5,000 lines). **But once proximity is in the model the curve is flat** (0.7194 → 0.7176). More reading
buys information the organ cannot convert, because on the noun side proximity already answers the question.
**Recommendation with a number: do not run the 500k job for this cue.**

#### (c) The retrieval capacity — SWEPT, AND IT IS NOT BINDING (alternate path #5)

The first submission chose the capacity cap K = 6 as "the knee" and listed "learn the cap / use an activation decay
instead" as a more faithful alternative (Lewis & Vasishth 2005). Swept on the channel probe:

| K | retrievable population | proximity + association |
|---|---|---|
| 4 | 546 | 0.7344 (obl 0.6197, nmod 0.8797) |
| 6 | 556 | 0.7176 (obl 0.6006, nmod 0.8683) |
| 12 | **556 — identical to K = 6, to the token** | 0.7176 — identical |

**K = 6 already retrieves everything K = 12 does**, so the hard cap is not throwing anything away on this test set and
a soft activation-decay retrieval could not recover a single additional token. The lever is answered and closed: the
capacity limit is not where the loss is. (K = 4 ranks slightly better on a slightly smaller population — a precision /
coverage trade of 10 tokens, not a mechanism.)

## SUBMISSION PROMPT

```
pri 94 -- "PP attachment (obl/nmod) is the attachment arm's worst comprehension-relevant class -- mine
unambiguous cases from reading" -- SOLVED, submitted for review.

The cue on disk could not see two thirds of its own problem: `pp_site` offered exactly two candidate hosts
and only for a NOUN/PROPN object right after a determiner, so at most 33.5% of the gold obl+nmod population
was decidable by it at all. Rebuilt as the brain's mechanism -- case marking opens the search, ALL open hosts
are retrieved under a capacity limit, and the host-preposition association learned from UNAMBIGUOUS reading
(Hindle & Rooth reallocation; 100k Simple-Wiki lines tagged by our own category organ; 23,026 unambiguous
seeds, 58,161 association cells) decides among them -- plus a typed thematic channel (what the phrase is
about, given who would license it) and English's other case marker, the genitive, as a construction.

UD-EWT test 700, gold categories, train cap 1500, on the working tree WITH the pri-97 diff already applied,
paired bootstrap over sentences. In-order (live) decode: UAS 0.6246 -> 0.6373 (+0.0127 CI [+0.0090,+0.0164]),
obl 0.449 -> 0.535 (+0.0860 CI [+0.0577,+0.1167]), nmod 0.410 -> 0.491 (+0.0805 CI [+0.0498,+0.1148]).
Search decode: obl +0.0881, nmod +0.1255. Nothing else down (advcl -0.008 is the only fall). It beats a
SCRAMBLED twin CI-separated (obl +0.031, nmod +0.077) and a CONSTANT-VALUE twin of its own structure
CI-separated (obl +0.040, nmod +0.099) -- that second control exists because the scrambled twin was NOT at
zero, which is volunteered against the submission. Oracle ceiling on the channel: obl 0.746, nmod 0.543.

Three routes refuted as built with their mechanisms read off the learned validity tables, including the one
that looked most obviously right (widening the meaning cue's case guard: it collapses obl 0.449 -> 0.199,
because that over-broad guard is the arm's ONLY oblique-argument teacher).

Files: experiments/exp_attachment_pp_association_unambiguous_mining_v1.py,
notes/problems/<slug>/{SOLVED.md,attachment_arm_pp_patch.diff} (537 lines, `patch -p1 --dry-run` clean on
the current working tree, equivalence-checked by executing it in memory),
data/hook_state/attachment_pp_assoc_v2_simplewiki100k_candidate.json. Nothing under hdlab/ or tools/ edited.

One gate the solver cannot close: the board no-regress run needs the asset landed, because the arm loads a
fixed asset path. Please run it after landing.
```
