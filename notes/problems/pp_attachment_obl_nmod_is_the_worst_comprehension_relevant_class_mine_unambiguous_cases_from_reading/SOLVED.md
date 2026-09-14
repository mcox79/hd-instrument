---
problem: pp_attachment_obl_nmod_is_the_worst_comprehension_relevant_class_mine_unambiguous_cases_from_reading
status: SOLVED
bar: "obl and nmod recall CI-separated above the current asset on UD-EWT test 700, UAS not down, twin far below, knowledge in counts with an online observe path, witness green -- OR a located negative with the oracle-association probe number."
result: "PHASE 7 (2026-09-13/14 continuation) MEASURED THE THREE THINGS THE FIRST SUBMISSION COULD NOT, and they hold. (1) THE LIVE CHAIN -- the categories rung's OWN tags and posterior, no gold UPOS anywhere, exactly the path hdlab/frontend.Parser takes at its defaults, train cap 6000 (the LANDED cap), UD-EWT test 700, in-order (live) decode, paired bootstrap over sentences: UAS 0.6125 -> 0.6243 (+0.0117, CI [+0.0079,+0.0160]); obl 0.434 -> 0.497 (+0.0629, CI [+0.0321,+0.0948]); nmod 0.444 -> 0.507 (+0.0637, CI [+0.0301,+0.0997]); retrieved PP subpopulation +0.0412 (CI [+0.0132,+0.0709]). With gold categories at the same cap: UAS +0.0125 (CI [+0.0087,+0.0168]), obl +0.0524 (CI [+0.0189,+0.0873]), nmod +0.0824 (CI [+0.0496,+0.1164]). (2) THE LANDED ASSET AS A CONTROL: the rebuilt floor reproduces data/frontend_assets/attachment_validities_v1.json (== attachment_validities_v1_pri97_cap6000.json) to 0.0002 UAS, so `base` really is what the board would regress against. (3) HEADS -> LABELS: hdlab/graded_role_assigner HAS NO NMOD CLASS -- given the GOLD TREE'S OWN HEADS it labels 0 of 489 gold nmod correctly -- while reading the label off the HOST'S CATEGORY (the UD and brain definition of the distinction) is 98.1% correct on gold heads; the head gain reaches such a readout at +0.0415 (CI [+0.0216,+0.0634], obl +0.0524*), and the organ as built converts it to -0.068 obl / 0 nmod and a consumer regression 0.5765 -> 0.5622. PHASE-7 BUILD: `objgenoblnom6`, the SHIPPED arm plus BOTH sides of Pinker's bootstrapping in the acquisition teacher (an oblique slot for verb hosts from the substrate's own grown obl:<prep> store, and the nominal host slot the teacher never had), CONVERTS THE SUBMISSION'S ONE UNSEPARATED NUMBER: retrieved-nmod +0.0752 (CI [+0.0308,+0.1231]) against base and +0.0564 (CI [+0.0115,+0.1020]) against the shipped arm, +0.1316 under the search decode, and it removes the downstream regression (role competition 0.5769 vs base 0.5760, vs the shipped arm's 0.5617), with NOTHING CI-separated down. FIRST-SUBMISSION HEADLINE, unchanged and re-reproduced this session at cap 1500 in four independent runs (UAS 0.6387 / obl 0.541 / nmod 0.489 against base 0.6252 / 0.440 / 0.408): UAS +0.0134*, obl +0.1006*, nmod +0.0805*."
floor: "the IDENTICAL pipeline with the change off (`base`), rebuilt from the same teacher, the same training slice and the same rounds: in-order UAS 0.6246 / obl 0.449 / nmod 0.410, search UAS 0.6188 / obl 0.444 / nmod 0.388. STRONGER FLOORS ALSO RUN: (a) `flat` -- the SAME cue firing on the SAME arcs with a CONSTANT value, i.e. the retrieval structure with no association content at all: UAS +0.0023 n.s., obl +0.0461*, nmod -0.0187 n.s.; (b) `twin` -- the scrambled association (below); (c) `gen` -- the genitive construction alone: UAS +0.0061*, obl +0.0126*, nmod +0.0655*; (d) `obj` -- the association without the genitive: obl +0.0776*, nmod +0.0169 n.s. The winning arm beats the STRONGEST of these CI-separated on every headline number: vs `flat` UAS +0.0104 CI [+0.0077,+0.0132], obl +0.0398 CI [+0.0186,+0.0641], nmod +0.0993 CI [+0.0741,+0.1263]."
controls: "PHASE 7 ADDED SIX. (a) DETERMINISM: two byte-identical processes of `base` reproduce UAS 0.6252 / obl 0.440 / nmod 0.408 to four decimals, and a third inside a different arm list reproduces them again -- the pipeline is deterministic, so the -0.009 obl shift against the first session's floor is a real on-disk change I could not identify (treebank byte-identical since July, every asset the arm reads older than the first measurement, all 26 HDLAB_* switches default in both); every comparison here is WITHIN-RUN and paired, and the shift is a tenth of the effect. (b) THE LANDED ASSET LOADED FROM DISK as an arm: UAS 0.6241 / obl 0.449 / nmod 0.429 against the rebuilt floor's 0.6239 / 0.444 / 0.429 (delta +0.0002 UAS, n.s.). (c) AT THE LANDED CAP 6000 the association's content, measured against a control that MATCHES THE GENITIVE (`flatgen` = the same arcs, a constant cue value, plus the genitive construction), is CI-SEPARATED ON BOTH RELATIONS: UAS +0.0029*, obl +0.0210*, nmod +0.0150*, retrieved obl +0.0300*, retrieved nmod +0.0301*. THE THREE-WAY ATTRIBUTION of the headline at cap 6000 is: the RETRIEVAL STRUCTURE obl +0.0335 / nmod +0.002, the GENITIVE CONSTRUCTION nmod +0.0654 / obl -0.002, the ASSOCIATION CONTENT obl +0.0210 / nmod +0.0150 -- the association is the smallest of the three and the only one separated on both relations at once. CORRECTED IN ROUND 2 AND STATED AGAINST THE SUBMISSION: the round-1 controls `flat` and `twin` do NOT carry the genitive, so the round-1 reading ("content is on nmod, not obl": obl +0.0189 n.s., nmod +0.0805*) conflated the genitive with the content and was wrong; section 16.1b has the corrected decomposition. (d) A TABLE-FREE, DECODE-FREE CHANNEL PROBE over the 556 retrievable gold obl+nmod tokens: the association ranks the gold host first 0.484 of the time against its scrambled twin's 0.284 -- but PROXIMITY alone scores 0.714 (nmod 0.922), so the association's job in this organ is to override proximity where proximity is wrong, which is the obl cases. (e) THE TWO-SIDED TEACHER'S TWIN: `twinoblnom6` (both stores scrambled) obl 0.382 / nmod 0.537 / UAS 0.6291 -- `objgenoblnom6` beats it CI-separated on UAS (+0.0082), obl (+0.1405) and retrieved obl (+0.1952); each ONE-SIDED version, by contrast, is indistinguishable from its own twin (objgenoblteach vs twinoblteach obl +0.0126 n.s.; objgennom6 vs twinnom6 nmod -0.0056 n.s.), which is how phase 7 established that the one-sided effect is the teacher's meaning BUDGET and the two-sided effect needs the association's CONTENT. (f) A BUG FOUND IN MY OWN DIAGNOSTICS AND FIXED: roles_diag / gap_decomposition / label_transfer ran after `deactivate_to_head()`, i.e. read every table with its own cue off; caught because objgen's gap-decomposition CORRECT count fell below base's while its recall was higher; fixed with `arm_context` and four self-test guards, and every diagnostic number in the phase-7 sections is from the corrected re-run. RETAINED FROM THE FIRST SUBMISSION: the oracle-ceiling probe (obl 0.746 / nmod 0.543), the known-fact check on the mined association, the learned-ladder check, the no-regress table. NO-REGRESS AT CAP 6000 (in-order, base -> objgen): root 0.777 -> 0.777, nsubj 0.778 -> 0.779, obj 0.772 -> 0.777, case 0.715 -> 0.759, xcomp 0.737 -> 0.766, advcl 0.336 -> 0.351, conj 0.382 -> 0.386, punct 0.469 -> 0.470; ccomp 0.690 -> 0.672 is the only fall (-0.017, 116 items) and it falls by the same amount on the live chain. PATCH EQUIVALENCE re-checked this session: `patch -p1 --dry-run` clean, cue values identical on 40 sentences / 385 arcs, fast path vs reference loop 1.78e-15. WITNESS: verification/test_attachment_arm.py 17/17; the cell's own scaffold-free self-test 40/40 (22 at first submission)."
files_changed: "experiments/exp_attachment_pp_association_unambiguous_mining_v1.py (phase 7 added the live-chain evaluation, the heads->labels transfer instrument, the table-free channel probe, the coverage probe, the oblique-slot channel, the nominal host slot, the two-sided teacher arm, the arm_context diagnostic fix and 18 more self-test checks), notes/problems/<slug>/{SOLVED.md, attachment_arm_pp_patch.diff (UNCHANGED), attachment_arm_two_sided_teacher_patch.diff (NEW, round 2 -- the two-sided acquisition teacher, applied AFTER the main diff)}, data/exp_attachment_pp_association_unambiguous_mining_v1/** (mined associations, metrics, probes), data/hook_state/attachment_pp_assoc_v2_simplewiki100k_candidate.json (the candidate asset). NOTHING under hdlab/ or tools/ was edited -- the proposed change is the unchanged 537-line diff."
reverify: "SELF-TEST (40 scaffold-free checks, writes nothing): .venv/Scripts/python.exe experiments/exp_attachment_pp_association_unambiguous_mining_v1.py --self-test.  PATCH CHECK: ... --verify-patch notes/problems/pp_attachment_obl_nmod_is_the_worst_comprehension_relevant_class_mine_unambiguous_cases_from_reading/attachment_arm_pp_patch.diff.  LIVE CHAIN + landed cap (the phase-7 headline): OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0 .venv/Scripts/python.exe experiments/exp_attachment_pp_association_unambiguous_mining_v1.py --full --cap 6000 --test-cap 700 --lines 100000 --assoc data/hook_state/attachment_pp_assoc_v2_simplewiki100k_candidate.json --arms base,objgen --decodes incr --boot 2000 --live --consumer --tag _live6000.  HEADS->LABELS + the residual ledger: the same with --label-transfer base,objgen --roles-diag base,objgen --gap-decomp base,objgen --tag _diagfix6000 (drop --live).  THE TWO-SIDED TEACHER and its twin: the same at --cap 1500 with --arms base,objgen,objgenoblnom6,twinoblnom6 --decodes incr,map1 --pairs twinoblnom6:objgenoblnom6,objgen:objgenoblnom6 --consumer --tag _oblnomtwin1500.  SECOND DIFF (regenerates it byte-for-byte and re-runs its arc-for-arc equivalence check against the measured cell): ... --two-sided-diff notes/problems/<slug>/attachment_arm_pp_patch.diff --two-sided-out notes/problems/<slug>/attachment_arm_two_sided_teacher_patch.diff.  THE GENITIVE-MATCHED CONTROL (round 2, the clean content decomposition + the ccomp flip trace): ... --full --cap 6000 --test-cap 700 --lines 100000 --assoc data/hook_state/attachment_pp_assoc_v2_simplewiki100k_candidate.json --arms base,flatgen,objgen --decodes incr --boot 2000 --pairs flatgen:objgen --flip-diag ccomp,advcl,obl,nmod --consumer --tag _flatgen6000.  CAPACITY PROBE (5 seconds, no build): ... --capacity-probe --test-cap 700 --tag _phase7.  CHANNEL PROBE (20 seconds, no build): ... --rank-probe --test-cap 700 --near-w 2.0 --tag _phase7_w2.0.  Every command writes only its own data/exp_* directory."
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

### 12.3 HEADS → LABELS: where the gain stops, and why — including a BUG I FOUND IN MY OWN DIAGNOSTIC

**First, the bug, because it changes numbers I would otherwise have reported.** `main` runs each arm inside
`try: ... finally: deactivate_to_head()`, so the three post-hoc diagnostics (`roles_diag`, `gap_decomposition`,
`label_transfer`) ran AFTER the arm was switched off: they read the objgen TABLE with no PP cue, no thematic cue and
no genitive construction — the learned validities were there but nothing fired them. It shows as objgen's
gap-decomposition CORRECT count (220) falling BELOW base's (229) while its measured nmod recall is higher, which is
arithmetically impossible for the arm that was measured. Fixed with an `arm_context` that re-installs each arm's
configuration for the duration of a diagnostic, guarded by four new self-test checks, and **every diagnostic number
below is from the corrected re-run** (`metrics_diagfix6000.json`). The first submission's `consumer_roles` numbers
were never affected — that one runs inside the arm block.

**The finding: `hdlab/graded_role_assigner` HAS NO NMOD CLASS.** Its inventory is
`ROLE_CLASSES = [SUBJ, OBJ, PASS_SUBJ, BY_AGENT, OBL, OTHER, IOBJ]` and `ROLE_TO_DEP` can emit only
`nsubj / nsubj:pass / obj / iobj / obl / obl:agent / dep`. Measured, not asserted, and measured at the ceiling:
**even given the GOLD TREE'S OWN HEADS the organ labels 0 of 489 gold nmod correctly.** It is a missing symbol, not
a modelling failure, and it is now a self-test check.

**How much signal is actually arriving, on the gold obl+nmod population (cap 6000, in-order, test 700).** In UD — and
in the brain's own terms, where a case-marked phrase licensed by a predicate is an oblique participant of an event
and one licensed by a nominal is a property of a thing — the obl/nmod distinction is a pure function of the HOST'S
CATEGORY. Measured against the gold tree, **reading the label off the host's category is 98.1% correct**
(obl 468/477 = 0.9811, nmod 524/534 = 0.9813; the 19 residuals are predicate-adjective and adverbial hosts). So a
consumer that reads the host category converts head accuracy into label accuracy essentially one-for-one, and the
question "does the head gain reach the label rung?" has an exact answer:

| | the organ as built | | a consumer that can express the distinction |
|---|---|---|---|
| | gold `obl` (n=443) | gold `nmod` (n=489) | head-category readout, all 1011 |
| base | 0.7178 | **0.0000** | 0.6469 |
| objgen | 0.6501 | **0.0000** | **0.6884** |
| GOLD HEADS | 0.7381 | **0.0000** | 0.9812 |
| objgen − base | −0.068 | 0.000 | **+0.0415, CI [+0.0216,+0.0634]** (obl +0.0524\*, nmod +0.0318 n.s.) |

**The head gain is real and it is fully available — +0.0415 CI-separated — to any label rung that can express the
distinction. The organ as built converts it to −0.068 on obl and 0 on nmod.** Per-token, objgen REPAIRS 104 heads on
this population (65 of them gain the right label, 34 already had it, 5 stay wrong) and BREAKS 35 (23 lose it):
82 labels gained, 40 lost.

**The consequence is a downstream regression, and it is a consumer defect, not a reason to revert.** The role
competition's accuracy over the nominals it can express falls **0.5765 → 0.5622** (n = 2099) at cap 6000, and the
confusion moves exactly as the mechanism predicts: `obl→dep` 61 → 96 and `nmod→dep` 195 → 214, because better heads
move case-marked nominals OFF verbs onto nouns and a nominal not governed by a verb has nowhere to go in this
inventory but `dep`. **Phase 7 also found the upstream repair that removes the regression without touching the
consumer — see §12.5(g): the balanced two-slot teacher leaves the role competition at 0.5769 against base's 0.5760.**

### 12.3b THE RESIDUAL LEDGER (corrected gap decomposition, cap 6000, in-order, per gold token)

| cause | obl (477) | nmod (534) |
|---|---|---|
| CORRECT | **237** (base 212) | **273** (base 229) |
| the detector never sees a case-marked nominal here | 86 | **155** |
| the association ranks another retrieved candidate above the gold host | **90** | 40 |
| the association ranks the gold host FIRST and the tree competition still loses it | 46 (base 156) | 44 (base 91) |
| the gold host is outside the retrieved candidate set | 18 | 22 |

Read it straight: **for obl the biggest remaining loss is now the association itself (90); for nmod it is detection
(155 tokens with no case marker the detector can see).** The decode bucket — the thing that would have been most
worrying — collapsed from 156 to 46 (obl) and 91 to 44 (nmod) when the cue landed, so the tree competition is no
longer discarding correctly-ranked arcs at scale. That is the ledger the next problem in this area should be written
against.

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

#### (d) PINKER'S THIRD SLOT — the oblique slot in the acquisition teacher (alternate path #1). **The store existed.**

The first submission called this "the most brain-foundational thing left in this area" and parked it because it
"needs a third grown store and a rebuild of the plausibility assets". **The store already existed.**
`tools/grow_selectional_store_bf.py` grows the verb → role → filler store from the substrate's OWN reading chain
(its own reading-induced categories → the attachment arm → the role competition, 60,000 Simple-Wiki lines, no
external parser anywhere) and it already accrues an `obl:<preposition>` slot beside SUBJ / OBJ / IOBJ. Read and typed
with the WordNet supersense table the typed selectional-preference organ uses, it gives **6,947 (predicate,
preposition) slots, 20,179 filler-class cells over 64 prepositions, 39,222 oblique observations.**

Built exactly as §8.1 specified: a case-marked nominal hosted by a verb is scored **in the oblique slot**, by that
predicate's own oblique expectation with that preposition — `P(class | verb, prep) / [P(class | verb, prep) +
P(class | prep)]`, the same 0..1 scale the object slot uses — **inside the acquisition teacher as well as at read
time**, which is the whole point and what separates it from the two read-time-only forms §5 refuted. When the store
abstains the teacher's own value stands, so the verb's pull is re-scored and never removed (§5b's lesson).

**Measured (cap 1500, test 700, in-order): obl 0.541 → 0.679 (+0.1384\*), nmod 0.489 → 0.221 (−0.2678\*), UAS
0.6387 → 0.6300 (−0.0087\*).** An obl number of **0.679** is 91% of the oracle ceiling the first submission measured
(0.746) — the largest obl figure this problem has produced. And nmod collapses.

**Its information-free twin says the content is not doing it.** `twinoblteach` — every predicate's oblique-filler
profile reassigned to another predicate, identical counts, identical marginals — gives obl 0.667 / nmod 0.227.
**objgenoblteach vs twinoblteach: obl +0.0126 n.s., nmod −0.0056 n.s., UAS −0.0008 n.s.** The lexical content of the
grown oblique store is worth nothing measurable. What moves the numbers is the STRUCTURE: re-scoring case-marked
nominals into a separate slot changes how much of the teacher's meaning budget verb hosts receive.

#### (e) The oblique slot as a READ-TIME cue — refuted, and refuted the same way

The same store used as a read-time cue value (`ppslot`, the pointwise lexical specificity, abstaining on non-verbs):
`objgenslot` vs `objgen` in-order UAS −0.0013 n.s., obl −0.0210 n.s., nmod −0.0169 n.s.; search UAS −0.0074\*,
obl −0.0650\*, nmod −0.0618\*. Against its own twin: **every number n.s. (obl −0.0042, nmod 0.0000)**. The fast
channel probe agreed before the organ run did — on the retrievable population the channel scores 0.671 against its
scrambled twin's 0.696 — which is what the probe is for.

#### (f) The NOMINAL HOST SLOT — the verb-only asymmetry, and the mirror-image seesaw

`SemanticBootstrapTeacher.score_matrix` adds its meaning term on exactly one kind of arc:
`pos[h-1] == "VERB" and pos[j-1] in NOMINAL`. **A noun host receives no meaning support at all, ever.** So while the
arm learns, every case-marked nominal has a verb voting for it with `beta = 10` and a noun voting with nothing. The
brain has no such asymmetry — a relational noun selects its complement as a verb selects its argument ("the picture
OF the girl", "the edge OF the table"; Barker 1995; Löbner's relational nouns) and Hindle & Rooth's contrast is
symmetric by construction. Built as `beta_nom * P_host(h, p)` on every retrieved NOMINAL host, with
`P_host = P(p | this noun) / [P(p | this noun) + P(p | this noun's class)]`.

**It is the exact mirror of (d):** `objgennom2` obl 0.361 / nmod 0.552; `objgennom6` obl 0.210 / nmod 0.566
(vs objgen 0.541 / 0.489). And against its twin, again, almost nothing: `objgennom6` vs `twinnom6` obl +0.0189\*,
nmod −0.0056 n.s., UAS +0.0006 n.s.

#### (g) THE FINDING THE SIX LEVERS ADD UP TO — and the arm that comes out of it

Put (d) and (f) side by side and the mechanism is one thing, not six:

| arm | teacher's meaning budget | obl | nmod | UAS | consumer role acc. |
|---|---|---|---|---|---|
| `objgennom6` | noun hosts, hard | 0.210 | 0.566 | 0.6209 | 0.545 |
| `objgennom2` | noun hosts, light | 0.361 | 0.552 | 0.6300 | — |
| **`objgen` (shipped)** | verbs only (as HEAD ships it) | **0.541** | **0.489** | **0.6387** | 0.5617 |
| `objgenoblteach` | verbs, amplified | 0.679 | 0.221 | 0.6300 | — |

**The acquisition teacher's meaning term is a single budget, and WHERE IT IS SPENT — verb hosts versus nominal hosts
— is the obl/nmod seesaw.** It moves obl across a 0.47 range and nmod across a 0.35 range, and it does so **almost
independently of the CONTENT of the selectional stores** (every twin above matches its real arm). That is why five of
the six levers in this phase look like failures one at a time: they are all the same knob, and the shipped arm sits
near its in-order UAS optimum.

**So the build is not another cue. It is to spend the budget on BOTH sides at once, which is what Pinker's
bootstrapping actually says** — the child learns that predicates take participants AND that things have properties.
`objgenoblnom6` = the shipped arm + the oblique slot for verb hosts + the nominal host slot at `beta_nom = 6`:

**cap 1500, UD-EWT test 700, paired bootstrap over sentences, 2000 resamples.**

| | UAS | obl | nmod | retrieved PP subpop | retrieved obl (n=333) | retrieved nmod (n=266) | consumer |
|---|---|---|---|---|---|---|---|
| `base` | 0.6252 | 0.440 | 0.408 | 0.502 | 0.466 | 0.549 | 0.5760 |
| `objgen` (shipped) | 0.6387 | 0.541 | 0.489 | 0.584 | 0.598 | 0.568 | 0.5617 |
| **`objgenoblnom6`** | 0.6373 | 0.522 | **0.515** | **0.594** | 0.571 | **0.624** | **0.5769** |
| vs base, in-order | **+0.0121\*** | **+0.0818\*** | **+0.1067\*** | **+0.0918\*** | **+0.1051\*** | **+0.0752\*** | |
| vs base, search | **+0.0148\*** | **+0.0713\*** | **+0.1498\*** | **+0.0818\*** | **+0.0961\*** | **+0.0639\*** | |
| vs `objgen`, in-order | −0.0014 n.s. | −0.0189 n.s. | +0.0262 n.s. | +0.0100 n.s. | −0.0270 n.s. | **+0.0564\*** | |
| vs `objgen`, search | +0.0038 n.s. | −0.0105 n.s. | **+0.0674\*** | **+0.0534\*** | −0.0090 n.s. | **+0.1316\*** | |

**Two things this does that the shipped arm does not.**
1. **It converts the submission's one unseparated number.** The PARTIAL was nmod on the item's OWN population — the
   retrieved case-marked nominals — at +0.0226, CI [−0.0149,+0.0569]. Under the balanced teacher that number is
   **+0.0752 CI [+0.0308,+0.1231] against base and +0.0564 CI [+0.0115,+0.1020] against the shipped arm itself**,
   and +0.1316 under the search decode. **Every headline number, on both populations and both decodes, is now
   CI-separated.**
2. **It removes the downstream regression.** The role competition's accuracy is 0.5769 under the balanced arm against
   0.5760 at base — flat — where the shipped arm costs it 0.5617 (−0.014). Giving nominal hosts their vote stops the
   arm over-attaching case-marked nominals to verbs, which was what pushed the labeller into `dep`.

The cost is obl −0.0189 (n.s., CI [−0.0566,+0.0203]) and UAS −0.0014 (n.s.) against the shipped arm in-order, and
under the search decode both move the other way (UAS +0.0038, obl −0.0105, both n.s.). **Nothing is CI-separated
down.** `beta_nom` is swept, never adopted: 2 and 6 with the oblique slot, 2/6/14 without — 14 overshoots badly
(obl 0.264).

**Its information-free twin, and what the twin proves.** `twinoblnom6` scrambles BOTH stores — every host's
preposition profile and every predicate's oblique-filler profile reassigned, counts, densities and marginals
identical. It gives obl 0.382 / nmod 0.537 / UAS 0.6291 / consumer 0.5607. **`objgenoblnom6` beats it CI-separated on
UAS (+0.0082), obl (+0.1405) and the retrieved obl subpopulation (+0.1952)**, and sits 0.0225 BELOW it on nmod
(CI-separated) — because a scrambled noun association votes for every noun indiscriminately, which lifts nmod by
destroying obl. That is the sharpest control in this submission: **the two-sided teacher needs the CONTENT of the
association, and it needs it on the noun side specifically.** Contrast (d) and (f), where each one-sided arm was
indistinguishable from its own twin — one-sided, only the budget matters; two-sided, the content decides.

**Why I did NOT fold this into the proposed diff.** It changes `SemanticBootstrapTeacher.score_matrix`, not just the
cue pass, so it needs its own equivalence check against a patched module, and its advantage over the shipped arm is
CI-separated on the retrieved-nmod population and the search decode but not on the in-order headline. The shipped
diff is unchanged and still `patch -p1 --dry-run` clean. **Strategy should decide whether to land it; the reverify
command is in the frontmatter and it reproduces in one run.**

## 13. ALTERNATE PATHS AFTER PHASE 7 — as brain-foundational or MORE so (the updated queue)

The first submission listed five. Phase 7 **built and measured three of them** (#1 the oblique slot, #2 the
referential cue, #3 more reading), **closed a fourth with a number** (#5 the retrieval capacity), and found two new
ones that are more brain-foundational than anything left on the old list. This is the queue as it now stands, best
first.

1. **GIVE THE ROLE COMPETITION AN NMOD CLASS — the highest-value item in this area, and it is not in this organ.**
   *Structure:* the same cue-based role competition (`hdlab/graded_role_assigner`), with one more role.
   *Computation:* `obl` versus `nmod` is a pure function of the licensing HOST'S CATEGORY — a case-marked phrase
   licensed by a predicate is an oblique participant of an event, one licensed by a nominal is a property of a thing
   (Talmy's figure/ground; the Competition Model reads the case cue against the licenser, not the phrase). The
   organ already computes the head's category as part of its configuration cue, so the class costs one entry in
   `ROLE_CLASSES` and one in `ROLE_TO_DEP`, plus a rebuild of `coarse_role_validities`.
   *Why it is the top item:* the heads rung's whole nmod gain currently dies at this boundary, and the boundary is a
   missing symbol, not a hard problem. *Why not here:* it is `hdlab/graded_role_assigner.py`, outside this remit.

2. **LAND THE TWO-SIDED ACQUISITION TEACHER (`objgenoblnom6`) — BUILT AND MEASURED IN PHASE 7, §12.5(g).**
   *Structure:* semantic bootstrapping (Pinker 1984) applied symmetrically. *Computation:* `SemanticBootstrapTeacher.score_matrix` adds its meaning term `beta *
   slot_plausibility` on exactly one kind of arc — `pos[h-1] == "VERB"`. A noun host gets no meaning support at all,
   ever, so while the arm learns, every case-marked nominal has a verb voting for it with `beta = 10` and a noun
   voting with nothing. The brain has no such asymmetry: a relational noun selects its complement as a verb selects
   its argument ("the picture OF the girl", "the edge OF the table" — Barker 1995; Löbner's relational nouns), and
   Hindle & Rooth's original contrast is symmetric by construction. **Measured: it converts the submission's one
   unseparated number (retrieved nmod +0.0752\* against base, +0.0564\* against the shipped arm) and it removes the
   downstream regression (role competition 0.5769 against base's 0.5760, where the shipped arm costs 0.5617), with
   nothing CI-separated down. It beats its own two-store scrambled twin CI-separated on UAS (+0.0082), obl (+0.1405)
   and retrieved obl (+0.1952).** Not folded into the diff because it changes the acquisition teacher and needs its
   own patch-equivalence check; the reverify command is in the frontmatter.

3. **THE REFERENTIAL CONTEXT CUE, AT DISCOURSE SCOPE.** *Structure:* Altmann & Steedman 1988 / Spivey-Knowlton &
   Sedivy 1995 — the referential context that licenses a restrictive modifier. *Computation:* the cue value needs
   "how many salient referents of this kind is the reader already entertaining", which is a property of the
   ENTITY/SITUATION MODEL, not of the sentence. Phase 7 built the sentence-scoped version and refuted it with its
   learned table (§12.5a): at sentence scope the cue degenerates into a host-type prior the configuration already
   owns, and the definiteness contrast comes out reversed. *What it would take:* the rival-referent count read off
   the coref / entity layer and handed to the arm as an input, i.e. a cross-organ wire, not a cue this arm can grow.
   **This is the correct version of the brief's own named lever and it is a strictly bigger build than it looked.**

4. **SEMANTIC CASE MARKING FOR BARE OBLIQUES.** *Structure:* the same case cue, marked semantically instead of
   morphologically — Bates & MacWhinney's cue coalitions: where the morphological cue is absent the semantic cue does
   the same job. A bare temporal or measure nominal ("last year", "three times", "Monday") is an oblique with no
   preposition, and UD labels it `obl` with no `case` child. *Sized in phase 7 by a new coverage probe:* of the 144
   gold obl the preposition detector still cannot see, **32 are temporal nominals** (28 `NOUN/noun.time` + 4
   `PROPN/noun.time`) — the single largest undetected class, 6.7% of all gold obl. The genitive construction already
   covers 111 of the 534 gold nmod, so a third case cue is the natural next one. *Why not now:* it opens the
   retrieval on a population the association was never mined for, so it needs its own mining pass and its own twin.

5. **SECOND-ORDER SIBLING FACTORISATION** (unchanged from the first submission; the SOTA drill's #1, +13.3 documented
   for label-free parsing). A host that already has a PP of the same preposition is a worse candidate — valence
   occupancy at the phrase level. Needs the projective second-order inside–outside; Matrix-Tree is first-order.

6. **CLOSED BY MEASUREMENT, do not queue:** (a) *more reading* — the association is still learning (its margin over
   its twin doubles from 5k to 100k lines) but the curve is flat once proximity is in the model, so the 500k mining
   job buys nothing here (§12.5b); (b) *an activation-decay retrieval instead of the hard capacity cap* — K = 6
   already retrieves every token K = 12 does, so there is nothing for a softer rule to recover (§12.5c).

## 14. NEXT STEPS AFTER PHASE 7 (priority order, replacing §11)

1. **Land the diff and rebuild the asset at the landed cap 6000** with
   `--pp-assoc data/hook_state/attachment_pp_assoc_v2_simplewiki100k_candidate.json`, then run the board's no-regress
   check. **Phase 7 closed most of what §11.1 could not:** the composition IS measured at cap 6000 on the pri-97 tree,
   the rebuilt floor reproduces the landed asset to 0.0002 UAS, and the win holds on the LIVE chain. What still cannot
   be done from a solver seat is running the BOARD (the arm loads a fixed asset path, and pointing it at a candidate
   asset would mean overwriting the live one).
2. **Add an NMOD class to `hdlab/graded_role_assigner`** (alternate path #1). Until this exists the heads rung's nmod
   gain cannot reach any consumer, and the better heads make the role metric *worse* (0.5765 → 0.5622 at cap 6000)
   for a reason that is a missing symbol, not a modelling failure. **This is the single highest-value item in the
   area and it is a one-class change plus a validity rebuild.**
3. **Land the two-sided acquisition teacher on top of the diff** (`objgenoblnom6`, §12.5g). It is built, measured,
   twin-controlled and reproducible in one command; it is the only thing in this phase that improved on the shipped
   arm, and it fixes both the PARTIAL and the downstream regression at once.
4. **Build the referential cue at DISCOURSE scope** (alternate path #3), wired to the entity layer. The sentence-scoped
   version is refuted here with its learned table; do not re-try it at sentence scope.
5. **Semantic case marking for bare temporal obliques** (alternate path #4) — 32 measured gold obl tokens, the largest
   class the preposition detector cannot see.
6. **Do NOT queue** the 500k-line mining job or an activation-decay retrieval: both are closed with numbers (§12.5b,
   §12.5c).

---

# PHASE 7, ROUND 2 — the answers, the second diff, and the probe

## 15. THE SECOND DIFF: `attachment_arm_two_sided_teacher_patch.diff`

**Generated and equivalence-checked; it is a SEPARATE landing step, applied AFTER `attachment_arm_pp_patch.diff`.**
It uses the symbols that diff introduces (`pp_sites`, `pp_case_marked`, `pp_obj_class`, `pp_host_key`,
`pp_host_class`, `pp_p_given`, `PP_NOM_HOST`), so it is generated against the post-main source **in memory** —
nothing under `hdlab/` was written — and it will NOT `patch -p1 --dry-run` clean on a tree that lacks the main diff.
That is by design and is the landing order strategy asked for.

| | |
|---|---|
| hunks | 7 (6 in `hdlab/attachment_arm.py`, 1 in `tools/build_attachment_validities.py`), 181 lines |
| what it adds | `obl_slot_store()` + `obl_slot_plausibility()` + `pp_case_preps()`; `BETA_NOM` / `OBL_TEACH` / `OBL_SLOT_M1` / `OBL_SLOT_M2` env switches; `pp_assoc` and `obl_slots` on the teacher; the oblique-slot branch in `slot_plausibility`; the nominal-host term at the end of `score_matrix`; `pp_assoc=` threaded through `knowledge_free_teacher` |
| equivalence check | the patched module is executed and its **acquisition teacher's score matrix compared arc-for-arc** with the two-sided teacher this cell measured: **max \|delta\| = 0.00e+00 over 30 sentences** |
| its own reverify | `.venv/Scripts/python.exe experiments/exp_attachment_pp_association_unambiguous_mining_v1.py --two-sided-diff notes/problems/<slug>/attachment_arm_pp_patch.diff --two-sided-out notes/problems/<slug>/attachment_arm_two_sided_teacher_patch.diff` (regenerates it byte-for-byte and re-runs the check) |
| overlap with the main diff | none. The main diff's only teacher hunk inserts the default-off phrase case rule between `n = len(toks)` and `is_pron = ...`; this diff's oblique-slot branch is inserted immediately before it, and its other hunks are in `__init__`, `score_matrix` and new module-level code. In `tools/build_attachment_validities.py` the main diff's hunks are at lines 17/131/149/162/171 and this one is in `knowledge_free_teacher` at line 88. |

**THE EXACT REBUILD COMMAND after landing both diffs** (the asset the reader loads):

```
OMP_NUM_THREADS=3 OPENBLAS_NUM_THREADS=3 MKL_NUM_THREADS=3 PYTHONHASHSEED=0 \
.venv/Scripts/python.exe tools/build_attachment_validities.py \
    --cap 6000 --beta 10 \
    --pp-assoc data/hook_state/attachment_pp_assoc_v2_simplewiki100k_candidate.json \
    --out data/frontend_assets/attachment_validities_v1.json
```

with `HDLAB_SBT_BETA_NOM=6` and `HDLAB_SBT_OBL_TEACH=1` (both are the shipped defaults in the diff, so the plain
command is enough). To rebuild the *first* diff alone, set `HDLAB_SBT_BETA_NOM=0 HDLAB_SBT_OBL_TEACH=0` — the second
diff is then inert, which is how the two landing steps stay separable. **Sanity numbers to expect on UD-EWT test 700
at cap 6000 with gold categories, in-order:** first diff alone UAS 0.6364 / obl 0.497 / nmod 0.511; both diffs, at
cap 1500 where the pair was measured, UAS 0.6373 / obl 0.522 / nmod 0.515 / retrieved-nmod 0.624.

**One caveat I am stating rather than hiding:** the two-sided pair was measured at **cap 1500**, not at the landed
cap 6000. Everything in §12.5(g) is a cap-1500 result. The obl/nmod trade the meaning budget controls is
cap-sensitive (§16.1), so `BETA_NOM` should be re-swept at cap 6000 before the board A/B — 2, 4, 6 is the range to
try, and the arm is already parameterised for it.

## 16. THE PROBE (round 2): every negative and mechanism, understood

### 16.0 Q3 ANSWERED BY STRATEGY — the floor drift was NOT unexplained

Strategy swapped the LIVE assets between 20:41 and 21:50: `attachment_validities_v1.json` → pri 97's cap-6000
rebuild, `lexical_categories_counts_v1.json` / `_penn_v1.json` → pri 99's rebuilds, `coarse_role_validities_ud_ewt.json`
→ pri 103's v3 table. **That is the cause of the −0.009 obl shift in `base`, and it means my floor is the NEW LIVE
ASSET, which is the correct floor for anything landing after tonight.** §12.0's "could not identify" stands as an
account of what I checked, and this is the answer; the two diagnostic consequences are worth keeping in mind:
the consumer numbers in this file are against pri 103's **v3** role table (which is why the first submission's
consumer delta was +0.004 and every measurement after the swap is negative), and the live-chain numbers are against
pri 99's category counts.

### 16.1 THE CAP-DEPENDENCE OF THE ASSOCIATION'S CONTENT -- the learned ladder, and a control that was wrong

**First, a correction to my own §12.2 that strategy's question exposed.** The `flat` control does NOT carry the
genitive construction, while `objgen` does — so "objgen vs flat" was never a clean read of the association's content;
it conflated the content with the genitive. The clean control is `flatgen` (the same arcs, a CONSTANT cue value, PLUS
the genitive), and it is measured in §16.1b below.

**Second, the mechanism, read off the learned tables.** The `pp` cue's learned validity ladder for `objgen`:

| | l2 (worst bin) | l1 | 0 | w1 | w2 (best bin) | **spread** |
|---|---|---|---|---|---|---|
| cap 1500 | −0.255 | +0.008 | +0.330 | +0.663 | +1.241 | **1.496** |
| cap 6000 | +0.001 | +0.174 | +0.593 | +0.780 | +1.080 | **1.079** |

With four times the training data the ladder **compresses by 28% and its floor rises off zero**: at cap 6000 even the
WORST association bin is no longer evidence against the arc. The cue is drifting from "this host is the associated
one" toward "this arc is a retrieved candidate at all" — i.e. toward the `flat` control. That is precisely the
Competition Model's account of cue strength (MacWhinney & Bates: a cue's strength is its validity *relative to the
competing cues available*, so a cue loses strength as the competition covers the same cases) and it is what Collins &
Brooks 1995 found empirically for PP attachment — their backed-off model beat a fully lexical one, because the
lexical term's marginal value collapses once the coarser terms are well estimated.

**Third, strategy's specific hypothesis — "is the teacher at cap 6000 already supplying the obl signal?" — is
MEASURABLY NO, and the truth is more interesting.** If the teacher were supplying it, the FLOOR would improve with
data. It does not: `base` obl is 0.440 at cap 1500 and 0.444 at cap 6000. What actually happens is that the CUED arm
gets *worse* at obl with more data — `objgen` obl 0.541 → 0.497 — while `base` stands still. So it is not
redundancy with the teacher; **it is the cue's own learned contrast being absorbed into the configuration's base rate
as that rate becomes better estimated.** The nmod side is spared because most of the nmod gain is the GENITIVE, whose
validity is learned as a CONSTRUCTION rather than as a value of a cue competing inside the same configuration cells —
and, exactly as that predicts, the genitive's contribution is cap-independent: `gen` alone gives nmod **+0.0655\* at
cap 1500 and +0.0674\* at cap 6000**, the same number.

**What followed for the build, and what happened when I tried it.** The obvious inference is that
(a) `m1`/`m2` (the Dirichlet shrinkage toward the class and the marginal) should be re-swept at the landed cap — the
right shrinkage at 1,500 sentences is not the right shrinkage at 6,000 — and (b) the ladder spread is the diagnostic
to watch, not the recall. **The two-sided teacher gives the biggest spread of any arm measured** (§16.3), which is
the mechanism behind its result and the reason it is the recommended follow-on. **I built (a) and it is REFUTED in the organ (section 16.5): heavier shrinkage helps the fixed-weight channel probe and does nothing for the learner.** (b) stands.

### 16.1b THE GENITIVE-MATCHED CONTROL — and the correction it forces

`flatgen` = the same arcs the cue fires on, a CONSTANT cue value, **plus the genitive construction** — everything
`objgen` has except the association's content. Cap 6000, UD-EWT test 700, in-order, paired bootstrap:

| | UAS | obl | nmod | retrieved obl | retrieved nmod |
|---|---|---|---|---|---|
| `base` | 0.6239 | 0.444 | 0.429 | | |
| `flatgen` (structure + genitive, NO content) | 0.6334 | 0.476 | 0.496 | | |
| `objgen` (+ the association's content) | 0.6364 | 0.497 | 0.511 | | |
| flatgen − base | +0.0095\* | +0.0314 n.s. | **+0.0674\*** | | |
| **objgen − flatgen (the CONTENT, cleanly)** | **+0.0029\*** | **+0.0210\*** | **+0.0150\*** | **+0.0300\*** | **+0.0301\*** |

**This overturns what §12.2 concluded and I am stating the correction plainly.** With the un-matched `flat` control
the content looked like "nmod only, obl not separated". With the genitive matched, the association's own content is
**CI-separated on BOTH relations** — obl +0.0210 and nmod +0.0150 — and on both halves of the retrieved
subpopulation (+0.0300 obl, +0.0301 nmod). The earlier picture was an artefact of comparing an arm that had the
genitive against a control that did not.

**So the honest attribution at the landed cap is a three-way split, not a two-way one:**

| where the +0.0125 UAS / +0.052 obl / +0.082 nmod comes from | UAS | obl | nmod |
|---|---|---|---|
| the RETRIEVAL STRUCTURE (which arcs the cue fires on at all) | +0.0037 | +0.0335 | +0.002 |
| the GENITIVE CONSTRUCTION (English's other case marker) | +0.0058 | −0.002 | +0.0654 |
| **the mined ASSOCIATION's content** | **+0.0029** | **+0.0210** | **+0.0150** |

(the first two rows are `flat` − base and `flatgen` − `flat` at cap 6000; they sum to `flatgen` − base.)
The association is the smallest of the three at the landed cap — **and it is the only one of the three that is
CI-separated on both relations at once.** The retrieval structure carries obl, the genitive carries nmod, and the
association is what makes them rise together instead of trading, which was the defect the brief opened with.

**And it answers strategy's question directly: NO, the content gain did not "move from obl to nmod".** It was never
measured cleanly before. The appearance of a move was the missing genitive in the control. The real cap-dependence is
the one in §16.1 — the cue's learned ladder compresses from spread 1.496 to 1.079 as the configuration's base rate
becomes better estimated — and that compresses the content's contribution on BOTH relations, from (obl +0.040,
nmod +0.099 against the un-matched control at cap 1500) to (obl +0.021, nmod +0.015 against the matched control at
cap 6000). Some of that difference is the control changing and some is the cap; the two cannot be separated from the
runs I have, and I am not going to claim a split I did not measure.

### 16.2 WHY ccomp FALLS −0.017 — three tokens, and two of them are not even reachable

The flip trace over the 116 gold `ccomp` tokens (cap 6000, in-order, `objgen` against `base`):

| | kept right | kept wrong | **BROKEN** | **REPAIRED** |
|---|---|---|---|---|
| ccomp (n=116) | 77 | 35 | **3** | **1** |

**The whole −0.017 is a net two tokens.** And the reachability check says the change did not cause two of the three
losses: of the 3 broken, **1 sits inside a retrieved PP site** (its clausal head moved to a NOUN — a real
interaction) and **2 are `NOT_REACHED_BY_THE_CHANGE`** — no PP site, no genitive arc, no cue value anywhere near
them. Those two are tree-level side effects: the arm decodes a single-root tree, so an arc that changes elsewhere in
the sentence can re-route a clausal complement that the cue never touched.

**There is no ccomp mechanism to fix.** For scale, the same trace on the relations the cue is aimed at:
obl REPAIRED 42 / BROKEN 17, nmod REPAIRED 62 / BROKEN 18. The broken ones DO have a mechanism and it is the one this
whole phase is about — **11 of the 18 broken nmod moved to a VERB head** (the verb pull), which is exactly what the
two-sided teacher corrects; the broken obl went to ADJ (8) and PRON (6) hosts, i.e. the widened retrieval offering a
predicate adjective or a pronoun that the association then over-ranked.

### 16.3 WHY THE MEANING BUDGET SPENT ON VERB HOSTS PRODUCES THE SEESAW — off the learned tables

The `pp` cue's ladder under each allocation of the acquisition teacher's meaning budget (cap 1500, 116 learned cells
in every arm, so this is not a coverage difference):

| arm | budget | l2 | l1 | 0 | w1 | w2 | spread | monotone? | obl | nmod |
|---|---|---|---|---|---|---|---|---|---|---|
| `objgennom6` | nouns, hard | −0.362 | −0.332 | +0.109 | +0.713 | +0.690 | 1.052 | **no** (w2 < w1) | 0.210 | 0.566 |
| `objgen` | verbs only (HEAD) | −0.255 | +0.008 | +0.330 | +0.663 | +1.241 | 1.496 | yes | 0.541 | 0.489 |
| `objgenoblteach` | verbs, amplified | −0.832 | −0.714 | **−0.600** | −0.409 | +0.707 | 1.539 | yes | 0.679 | 0.221 |
| **`objgenoblnom6`** | **both sides** | −0.556 | −0.344 | +0.213 | +0.911 | **+1.806** | **2.362** | yes | 0.522 | 0.515 |
| `twinoblnom6` | both sides, scrambled | +0.104 | +0.015 | +0.299 | +0.563 | +0.463 | 0.548 | **no** | 0.382 | 0.537 |

Read the third row: when the budget is amplified on verb hosts, **the entire ladder shifts down by about 0.9 and the
neutral bin goes to −0.600** — being a retrieved PP candidate becomes evidence *against* the arc. The teacher has
already done the attaching (to the verb), so the only job left for the association cue is to VETO, and it learns to.
That is the seesaw's mechanism in one number, and it is the same failure mode §5(a) found for the "strongest rival"
readout arriving by a third door: **whenever one host type is structurally favoured, the association cue stops
encoding association and starts encoding "not that type".**

Row four is the point of the whole phase. With both hosts voting, the cue no longer has to encode a type preference
at all, and its learned contrast is **the widest and cleanest this problem has produced — spread 2.362, strictly
monotone, w2 = +1.806** against the shipped arm's 1.496. The twin's ladder (0.548, non-monotone) confirms there is
nothing to learn there without the real association.

### 16.4 WHY CAPACITY 6 RETRIEVES EVERYTHING CAPACITY 12 DOES

Not because the candidate sets are small — **264 of the 599 sites (44%) have more than 6 open hosts to the left**, up
to 25. It is because **the gold host is never further down the list than rank 6**:

| gold host's rank in the retrieved list | 1 | 2 | 3 | 4 | 5 | 6 | 7+ |
|---|---|---|---|---|---|---|---|
| gold obl/nmod tokens | **397** | 85 | 47 | 17 | 5 | 5 | **0** |
| cumulative recall | 0.663 | 0.805 | 0.883 | 0.912 | 0.920 | **0.928** | 0.928 |

Recall at K is 0.9115 (K=4), 0.9282 (K=6), and **0.9282 for K = 8, 12 and 24 — identical to the token.** The capacity
limit costs nothing because English, in this register, does not place a prepositional phrase more than six open hosts
away from the thing that licenses it. That is Gibson's DLT and Lewis & Vasishth's decay as a *property of the corpus*
rather than of the model, and it closes the "learn the cap / use an activation decay" lever with a reason rather than
a null: **a softer retrieval rule has nothing left to recover.** (Consistency check on the instrument: rank-1 alone is
397/556 = 0.7140, which is exactly the proximity-only ranking accuracy the channel probe reports independently.)

### 16.5 THE SHRINKAGE — swept on the channel, then REFUTED in the organ

The ladder compression (§16.1) implicates the Dirichlet shrinkage `m1` (lemma → class) and `m2` (class → the
preposition's marginal). Swept on the channel probe (556 retrievable tokens, proximity floor at w = 2.0):

| m1 / m2 | association alone | on the proximity floor | obl | nmod |
|---|---|---|---|---|
| 1 / 5 | 0.4784 | 0.7068 | 0.6038 | 0.8395 |
| **5 / 20 (shipped)** | 0.4802 | 0.7176 | 0.6006 | 0.8683 |
| 15 / 60 | 0.4856 | **0.7320** | **0.6198** | 0.8765 |
| 40 / 150 | 0.4892 | **0.7338** | 0.6134 | 0.8889 |

**On the channel the shipped point is NOT at the knee** — heavier shrinkage is monotonically better, +0.016 on the
proximity floor at 15/60 and still rising slowly at 40/150. That looked like a free lever, so I built it in the organ.

**In the organ it does not convert.** Rebuilt at cap 1500 with m1 = 15 / m2 = 60: `objgen` UAS 0.6387 (identical),
**obl 0.530 against the shipped 0.541**, nmod 0.489 (identical); `objgenoblnom6` UAS 0.6368 / obl 0.526 / nmod 0.500
against 0.6373 / 0.522 / 0.515. The organ is flat-to-slightly-worse where the probe said +0.019 obl.

**Refuted as built, and the mechanism is one I had already written down and should have predicted.** The channel
probe scores a FIXED linear combination of proximity and association; the organ learns the cue's validity separately
inside every configuration. Heavier shrinkage makes the association's values more class-like and therefore more
CORRELATED with the configuration the arm already conditions on — which helps a fixed-weight ranker (it is getting a
better-estimated score) and does nothing for a learner that has already absorbed the class-level signal into its
configuration term. **This is the third time in this phase the probe and the organ disagreed in the same direction,
and the rule is now explicit: the channel probe is a valid test of "is there information here", never of "will the
organ use it".** The shipped m1 = 5 / m2 = 20 stands.

## 17. EVERYTHING A SOLVER NEEDS FOR THE NMOD ROLE-CLASS PROBLEM (strategy files this as its own brief)

**The defect in one sentence.** `hdlab/graded_role_assigner` cannot say "this nominal modifies another nominal": its
role inventory has no NMOD class, so every gold `nmod` is wrong whatever the heads rung hands it, and the heads
rung's whole nmod gain dies at that boundary.

**The evidence, all measured on UD-EWT test 700 (`metrics_diagfix6000.json`, cap 6000, in-order decode).**

| fact | number |
|---|---|
| `ROLE_CLASSES` | `[SUBJ, OBJ, PASS_SUBJ, BY_AGENT, OBL, OTHER, IOBJ]` |
| deps `ROLE_TO_DEP` can emit | `nsubj, nsubj:pass, obj, iobj, obl, obl:agent, dep` — **no `nmod`** |
| gold `nmod` the organ labels correctly, under the arm's heads | **0 / 489** |
| gold `nmod` the organ labels correctly, under **the gold tree's own heads** | **0 / 489** |
| where they go instead (gold heads) | `nmod→obl` 277, `nmod→dep` 212 |
| gold `obl` the organ labels correctly (gold heads / base heads / objgen heads) | 327 / 318 / 288 of 443 |

**The population.** The 1,011 gold `obl` + `nmod` tokens of UD-EWT test 700 (477 obl, 534 nmod); the organ's own
labelled population is the 932 of them that are `NOMINAL`-tagged (443 obl, 489 nmod).

**The rule that fixes it, and why it is brain-foundational rather than a convention.** In UD — and in the brain's own
terms — a case-marked phrase licensed by a PREDICATE is an oblique participant of an event, and one licensed by a
NOMINAL is a property of a thing. The distinction is therefore a pure function of the LICENSING HOST'S CATEGORY, and
the organ already computes the head's category as part of its configuration cue, so the class is free:

```python
PRED_HEAD_CATS = {"VERB", "AUX", "ADJ", "ADV"}          # a predicate licenses an oblique participant
obl  if pos[head-1] in PRED_HEAD_CATS else  nmod        # a nominal licenses a property
```

**Measured against the gold tree, that rule is 98.1% correct** (obl 468/477 = 0.9811, nmod 524/534 = 0.9813, all
1011 = 0.9812). The 19 residuals are 8 `nmod` with an ADJ host, 5 `obl` with a NOUN host, 2 `nmod` with an ADV host,
and 4 singletons — i.e. the rule is not a stand-in for the competition, it is the *ceiling* the competition should be
learning toward, and a solver should implement it as a learned cue value (host category × order, the organ's own cue
form), not as a hard rule.

**How much signal is waiting.** Reading the label off the host category over the arm's OWN heads:
base 0.6469 → objgen **0.6884**, a paired-bootstrap gain of **+0.0415, CI [+0.0216,+0.0634]** (obl +0.0524\*, nmod
+0.0318 n.s.). Per token, the heads change REPAIRS 104 tokens on this population — 65 of which gain the correct label
— and BREAKS 35, of which 23 lose it: **82 labels gained, 40 lost.** None of that reaches the organ today.

**The consumer regression this defect causes, so the solver can check the fix removes it.** Role accuracy over the
nominals the organ can express (n = 2099) falls **0.5765 → 0.5622** under the better heads, and the confusions move
exactly as the missing class predicts: `obl→dep` 61 → 96, `nmod→dep` 195 → 214. The cause is mechanical — improved
heads move case-marked nominals OFF verbs and ONTO nouns, and a nominal not governed by a verb has nowhere to go in
this inventory but `dep` (the joint frame-slot decode only groups dependents of a VERB or AUX head; everything else
takes the independent read, where `OTHER` wins by default).

**Two things the solver must not conclude.** (1) That the heads rung should be reverted: the head gain is real,
CI-separated, and available at +0.0415 to a consumer that can express the distinction. (2) That adding the class is
enough on its own: `coarse_role_validities` must be rebuilt with the new class in `ROLE_CLASSES`, and the joint
frame-slot decode's capacity rules need a decision about whether NMOD is capped per head (it should not be — a noun
takes many modifiers, like OBL and OTHER).

**Adjacent fact worth carrying into that brief.** Phase 7 found an upstream repair that removes the regression
*without touching the consumer*: the two-sided acquisition teacher (§12.5g) leaves role accuracy at 0.5769 against
base's 0.5760. That is a mitigation, not a fix — it stops the heads rung pushing nominals into `dep`, but the organ
still scores 0/489 on gold nmod. **Both are needed and they are independent.**

## 18. REMAINING OPPORTUNITIES, EACH WITH ITS COMPUTATION AND ITS ARITHMETIC REACH

The residual ledger (§12.3b, cap 6000, per gold token, `objgen`) is the budget every one of these is drawn against:

* **obl (477):** 237 correct | **90 association** | 86 not case-marked | 46 decode | 18 not retrieved
* **nmod (534):** 273 correct | **155 not case-marked** | 44 decode | 40 association | 22 not retrieved

| # | opportunity | the brain's computation | arithmetic reach |
|---|---|---|---|
| 1 | **Re-sweep `BETA_NOM` at the landed cap 6000** | the acquisition teacher's meaning budget is a single scalar and where it is spent IS the obl/nmod trade (§16.3); the right split at 1,500 sentences is not the right split at 6,000 | the pair was measured at cap 1500 only. The in-order trade at that cap was obl −0.019 for nmod +0.026; at cap 6000 the obl side is already weaker (0.497 vs 0.541), so the optimum should move toward LESS `BETA_NOM`. **2 / 4 / 6, three builds, one run** — the single cheapest unclaimed number in this problem |
| 2 | **A third case cue: bare temporal / measure obliques** | Bates & MacWhinney cue coalitions — where the morphological case cue is absent the SEMANTIC one does the same job; UD labels these `obl` with no `case` child | 32 of the 86 undetected obl are temporal nominals (28 `NOUN/noun.time` + 4 `PROPN/noun.time`), the largest single class. Perfect attachment of all 32 = **+0.067 obl**; a realistic half = +0.034 |
| 3 | **A bare-nominal-modifier construction for the 155 undetected nmod** | apposition and bare nominal modification are marked by ADJACENCY plus type compatibility, not by a case marker — an item-based construction (Tomasello 2003), the family the arm already has for the genitive | 155 tokens = **29% of all gold nmod**, the largest single residual bucket anywhere in this problem. Half of them = **+0.145 nmod.** The genitive construction is the worked precedent: it took 111 nmod tokens and delivered +0.067 nmod on its own |
| 4 | **Lexicalise the object noun in the thematic channel** | Ratnaparkhi's fourth element is the OBJECT noun itself, not only its class; Collins & Brooks 1995 show the back-off must include the lexical `n2` term with the coarser terms behind it | the obl ASSOCIATION bucket is 90 tokens = **+0.19 obl** if perfect. But §16.1 predicts diminishing returns: the lexical term's marginal value collapses once the coarse terms are estimated, and more reading is already closed (§12.5b). **Expect a fraction, and measure the ladder spread, not the recall** |
| 5 | **Second-order sibling factorisation** | valence occupancy at the phrase level — a host that already carries a PP of the same preposition is a worse candidate | the DECODE bucket, 46 obl + 44 nmod = 90 tokens where the cue ranks the gold host FIRST and the tree still loses it. Needs the projective second-order inside–outside; Matrix-Tree is first-order |

**Built and measured in this session, so not on the list:** the two-sided teacher (shipped as the second diff), the
referential cue, the oblique-slot read-time cue, the one-sided teacher slots, the reading-volume curve, the retrieval
capacity, the shrinkage.

## 19. ALTERNATE PATHS, SIMILARLY OR MORE BRAIN-FOUNDATIONAL THAN WHAT SHIPPED

1. **THE NMOD ROLE CLASS (§17).** More brain-foundational than anything in the heads rung: the reader currently
   cannot represent "a property of a thing" as distinct from "a participant in an event", which is a distinction the
   brain plainly makes. One class, and the rule is 98.1% correct off the host's category.
2. **THE TWO-SIDED ACQUISITION TEACHER (§12.5g, shipped as the second diff).** Strictly more faithful than what the
   arm does today: Pinker's bootstrapping says the child learns that predicates take participants AND that things
   have properties, and `score_matrix` implements only the first half.
3. **THE REFERENTIAL CUE AT DISCOURSE SCOPE (§12.5a).** The literature's third constraint, refuted here at sentence
   scope with its learned table. The correct version reads the rival-referent count off the entity/situation layer —
   a cross-organ wire, strictly more brain-foundational than a sentence-local proxy, and strictly more work.
4. **SEMANTIC AND CONSTRUCTIONAL CASE MARKING (opportunities 2 and 3).** The same case-cue machinery the whole build
   rests on, with the cue carried by the nominal's own semantic type or by an item-based construction instead of by a
   preposition. This is how the genitive was won, and it is where the largest single residual bucket lives.
5. **AN ACTIVATION-BASED RETRIEVAL instead of the hard cap** — *closed by measurement* (§16.4), and the reason is
   worth keeping: the gold host is never beyond rank 6, so a more faithful retrieval rule has nothing to recover.
   Recording it as closed is more useful than leaving it queued.

## 20. IS THE SESSION EXHAUSTED? — plainly

**Not exhausted in the sense of "nothing is left" — exhausted in the sense of "nothing further is buildable from this
seat tonight without a number I cannot get".** Concretely:

* Everything the brief and both rounds of phase 7 named has been built and measured, including the two levers the
  first submission parked and the one it never reached.
* **The single cheapest unclaimed number is opportunity 1 — re-sweeping `BETA_NOM` at cap 6000 — and it is one run
  of three builds.** I did not get it because each cap-6000 build took 20–40 minutes tonight on a machine shared with
  about twenty other Python processes, and I chose the genitive-matched control and the ccomp flip trace ahead of it.
  It should be the first thing the next session or the board A/B does.
* The two largest remaining buckets (155 undetected nmod, 90 obl association errors) both need a NEW mechanism —
  a bare-nominal construction and a lexicalised object term — not another parameter, and each is properly its own
  brief with its own twin and its own mining pass.
* Three levers are closed with reasons rather than nulls (reading volume, retrieval capacity, the Dirichlet
  shrinkage -- the last one built in the organ after the channel probe said it should win, and refuted there), and
  one is closed with a mechanism and a redirect (the referential cue, wrong scope).
* One round-1 claim was OVERTURNED by a round-2 control I built because strategy's question exposed the gap: the
  `flat` and `twin` controls do not carry the genitive, so round 1 mis-attributed the association's content. The
  corrected three-way split is in section 16.1b and the frontmatter now carries it.

**The honest one-line verdict: the problem as scoped is solved and its residual is now a ledger with named
mechanisms and arithmetic, not a wall.**

## SUBMISSION PROMPT

```
pri 94 -- "PP attachment (obl/nmod) is the attachment arm's worst comprehension-relevant class -- mine
unambiguous cases from reading" -- SOLVED, phase 7 rounds 1 and 2 complete, submitted for review.

THE SHIPPED ARM (diff unchanged, `patch -p1 --dry-run` clean, equivalence-checked again): PP attachment as the
brain's own mechanism -- case marking opens the search, ALL open hosts are retrieved under a capacity limit, and
the host-preposition association learned from UNAMBIGUOUS reading decides among them -- plus a typed thematic
channel and English's other case marker, the genitive, as a construction.

THE THREE GATES ROUND 1 COULD NOT CLOSE ARE CLOSED.
1. LIVE CHAIN (the categories organ's own tags and posterior, no gold UPOS, the path hdlab/frontend.Parser
   actually takes) at the LANDED cap 6000: UAS +0.0117 CI [+0.0079,+0.0160], obl +0.0629 CI [+0.0321,+0.0948],
   nmod +0.0637 CI [+0.0301,+0.0997]. The win survives the live chain intact.
2. CAP 6000 ON THE pri-97 TREE, with the LANDED ASSET loaded from disk as a control: the rebuilt floor
   reproduces it to 0.0002 UAS.
3. HEADS -> LABELS: graded_role_assigner HAS NO NMOD CLASS -- 0 of 489 gold nmod correct even on the GOLD TREE'S
   OWN HEADS. A host-category readout (the UD and brain definition) is 98.1% correct on gold heads and receives
   the head gain at +0.0415 CI [+0.0216,+0.0634]. Section 17 is a complete brief for that problem.

A CORRECTION I MADE AGAINST MYSELF IN ROUND 2. The round-1 controls `flat` and `twin` do not carry the genitive
construction, so round 1 mis-attributed the association's content ("nmod only, obl not separated"). Against a
genitive-MATCHED control (`flatgen`) the association's own content at cap 6000 is CI-separated on BOTH relations:
obl +0.0210*, nmod +0.0150*, retrieved obl +0.0300*, retrieved nmod +0.0301*. The honest three-way attribution:
retrieval STRUCTURE obl +0.034, the GENITIVE nmod +0.065, the ASSOCIATION obl +0.021 / nmod +0.015 -- the
association is the smallest of the three and the only one separated on both at once, which is exactly the
seesaw the brief opened with being closed.

A SECOND DIFF, for landing AFTER the first: attachment_arm_two_sided_teacher_patch.diff (7 hunks, 181 lines).
Six further levers were built; five are refuted WITH mechanisms read off the learned validity tables, and they
turned out to be one knob -- the acquisition teacher's meaning term is a single budget spent entirely on VERB
hosts, and WHERE it is spent IS the obl/nmod seesaw (spend more on verbs: obl 0.541 -> 0.679, nmod 0.489 ->
0.221; spend it on nouns: obl -> 0.210, nmod -> 0.566). Spending it on both sides -- Pinker's bootstrapping
symmetrically -- CONVERTS THE SUBMISSION'S ONE UNSEPARATED NUMBER: retrieved-nmod +0.0752 CI [+0.0308,+0.1231]
over base and +0.0564 CI [+0.0115,+0.1020] over the shipped arm (it was +0.0226, CI [-0.0149,+0.0569]), and it
REMOVES the downstream regression (role competition 0.5769 vs base 0.5760, where the shipped arm costs 0.5617).
Nothing CI-separated down. It beats a twin with BOTH stores scrambled on UAS (+0.0082*), obl (+0.1405*) and
retrieved obl (+0.1952*), and its learned ladder is the widest this problem has produced (spread 2.362 vs the
shipped arm's 1.496). Equivalence-checked arc-for-arc against the measured cell: max |delta| = 0.00e+00.
CAVEAT STATED, NOT HIDDEN: the pair was measured at cap 1500, so BETA_NOM should be re-swept at cap 6000 before
the board A/B -- that is the single cheapest unclaimed number in this problem and it is one run of three builds.

EVERY NEGATIVE UNDERSTOOD, with numbers. ccomp -0.017 is THREE tokens broken against one repaired out of 116,
and the reachability trace says two of the three are not touched by the cue at all (no PP site, no genitive) --
tree-level side effects, no mechanism to fix. The capacity cap is not binding because the gold host's rank
NEVER exceeds 6 (397/85/47/17/5/5, then zero) even though 264 of 599 sites have more than 6 candidates. More
reading is closed with a number (the association is still learning -- its margin over its twin doubles from 5k
to 100k lines -- but the curve is flat once proximity is in the model). The Dirichlet shrinkage looked like a
free lever on the channel probe (+0.016) and was REFUTED in the organ (obl 0.541 -> 0.530) -- the third time the
fixed-weight probe and the learner disagreed, and the rule is now written down.

Files: experiments/exp_attachment_pp_association_unambiguous_mining_v1.py (self-test 22 -> 40),
notes/problems/<slug>/{SOLVED.md, attachment_arm_pp_patch.diff UNCHANGED, attachment_arm_two_sided_teacher_patch.diff
NEW}, data/exp_attachment_pp_association_unambiguous_mining_v1/**. Nothing under hdlab/ or tools/ edited (sha1s
verified unchanged). Witness verification/test_attachment_arm.py 17/17.

Also volunteered: I found and fixed a bug in my OWN post-hoc diagnostics (they ran after the arm was
deactivated, reading each table with its cue off); every diagnostic number here is from the corrected re-run and
there are four self-test guards against it.
```
