---
problem: the_lemmatizer_is_wordnet_morphy_at_inference_not_a_glass_box_morphological_decomposition
status: SOLVED
bar: "One glass-box morphology organ (exception store + affix-detachment rules + lexical check, from a one-time offline export), every read-path `morphy` call repointed, BYTE-IDENTICAL lemmas on the real input distributions (divergence set enumerated, target 0), all named downstream witnesses + the board self-test unchanged, no nltk on the read path -- OR a numbered located negative naming the slice that cannot be made glass-box and why."
result: "BYTE-IDENTICAL to wn.morphy: 0 divergences over 6,326,530 raw morphy comparisons (every WordNet lemma x{n,v,a,r,None} + all exception keys + 1,082,843 generated inflections + 29,217 real UD-EWT/GUM prose tokens) AND 0 divergences on the full hdlab lemma path (lemma_word/lemma_verb/is_known_word/concept_lemma/gek.lemmatize, 29,217 tokens). PLUS an optimum: the brain-faithful dual-route organ EXCEEDS morphy on modern gold lemma 0.9836 vs 0.9603 (+0.0233, doc-paired bootstrap CI [0.0221,0.0246], n=195,045 tokens/285 docs, UD-EWT+GUM), generalizing across 24 genres (23/24 CI-sep, all positive)."
floor: "morphy itself is the byte-identity target (0 divergences = the port is faithful); for the EXCEED arm the floor is morphy's own gold-lemma accuracy 0.9603 (POS-conditioned) / 0.9177 (POS-generic), beaten CI-separated; the info-free wrong-POS twin floor = 0.7255 (loses by +0.2581 CI-sep)."
controls: "(1) EXHAUSTIVE ORACLE byte-identity vs wn.morphy over the entire lexicon + inflections + real prose (excludes: any algorithm/data-port error -- 0 divergences). (2) INFO-FREE TWIN: dual-route stripping to a random WRONG-POS lemma (excludes: 'strip more always wins' -- twin scores 0.7255, loses). (3) RULE-SNAPSHOT self-test: hardcoded detachment rules asserted == vendored nltk snapshot (excludes: silent nltk-version drift). (4) GENERALIZATION across 24 corpus/genre splits (excludes: single-distribution artifact -- 23/24 CI-sep positive, zero fitted params). (5) FREQUENCY-ARBITRATION probe (excludes the WordNet-count tie-break as a clean fix -- counts conflate inflected/lexicalized readings)."
files_changed: "experiments/build_glassbox_morphology_asset_v1.py, experiments/glassbox_morphology.py, experiments/exp_glassbox_morphy_byte_identity_v1.py, experiments/exp_morphy_gold_lemma_diagnosis_v1.py, experiments/exp_dualroute_morphology_exceed_v1.py, experiments/exp_dualroute_generalization_v1.py, experiments/exp_dualroute_optimize_and_upstream_trace_v1.py, experiments/glassbox_pos_bayes.py (the VALIDATED BF POS prototype -- the required upstream upgrade), experiments/exp_glassbox_pos_bf_and_morphology_stack_v1.py (the full BF POS->morphology stack), experiments/glassbox_pos_trigram.py (a second-order/trigram BF-POS prototype -- richer count-based sequential prior; PRESENT but NOT performance-validated, its forward-backward is too slow as written, so NO result is claimed from it -- it stands as the scaffold for the 'richer count-based cue integration' next step), verification/test_glassbox_morphology.py, data/frontend_assets/morphology/ (built asset, gitignored; rebuilt by the build script), notes/problems/the_lemmatizer_is_wordnet_morphy_at_inference_not_a_glass_box_morphological_decomposition/SOLVED.md. NO hdlab/ writes (Q111 -- proposed diff below)."
reverify: ".venv/Scripts/python.exe verification/test_glassbox_morphology.py"
---

> ## 🔑 HEADLINE: FIXING THE MORPHOLOGY REQUIRED UPGRADING THE POS TAGGER.
> The glass-box morphology port is byte-identical and the brain-faithful organ EXCEEDS morphy by +2.33 points **given
> a POS** -- but the live reader lemmatizes with NO part-of-speech signal, and that missing signal costs **+4.84
> points, LARGER than the morphology fix itself**. So this problem could not be fully realized at the morphology rung
> alone: I had to go UP the chain and prototype a mathematically-BF POS tagger (generative, count-based, graded
> posterior -- no gradient training, no external tool). Feeding its POS to the morphology recovers ~half the perfect-
> POS gain (0.9389 -> 0.9614, twin losing) and the whole stack is glass-box. **The POS tagger is the upstream lever,
> and its remaining non-full-BF piece (categories learned from supervised labels, not unsupervised distributional
> induction) is the next thing to fix upstream.** This is the owner's thesis in one line: a brain-faithful component
> was capped by an upstream input that was not yet 100% brain-foundational.

## What the brain does (the opening move)

Visual word recognition decomposes a written form into stem + affix EARLY and form-based (**Rastle & Davis 2008**,
morpho-orthographic segmentation: even `corner` is momentarily segmented `corn+er`), then CHECKS the candidate stem
against the lexicon (**Taft 1979** affix-stripping + lexical decision). Irregulars are STORED whole and retrieved on a
separate route (**Pinker-Ullman** words-and-rules dual route: `went`->`go`, `mice`->`mouse`). That is EXACTLY the
computation WordNet `morphy` performs -- an exception STORE + affix-detachment RULES + a lexical CHECK. The COMPUTATION
is brain-foundational; only the IMPLEMENTATION (nltk/WordNet at read time) violated the invariant. This solves it two
ways: a byte-identical glass-box port (removes the tool with zero risk) AND the brain-faithful *optimum* that morphy
only approximates.

## What I built and measured

**1. The offline export (`build_glassbox_morphology_asset_v1.py`).** nltk runs HERE, at build time only. It exports
the two tables `morphy` reads -- the exception maps (`{pos: {form: [bases]}}`, the stored-irregular route) and the
lemma-POS membership sets (`index.*` reduced to "is X a lemma of pos P", the lexical check) -- plus a snapshot of
morphy's substitution rules. Asset = `data/frontend_assets/morphology/`, WordNet 3.0, **2.19 MB**, `data/` is
gitignored so the ASSET is not committed; the BUILD SCRIPT is, so it is re-buildable.

**2. The glass-box organ (`glassbox_morphology.py`, proposed `hdlab/morphology.py`).** A pure-python EXACT port of
nltk 3.9.4 `WordNetCorpusReader._morphy`/`morphy`, reading only the asset. **No nltk / no WordNet import at inference.**
A `self_test_rules()` asserts the hardcoded detachment rules still equal the vendored nltk snapshot (guards against a
silent nltk upgrade).

**3. BYTE-IDENTITY (the BAR) -- PASSED, divergence set empty.** `exp_glassbox_morphy_byte_identity_v1.py` compares the
organ to `wn.morphy` (the oracle) over four universes whose union covers the lexicon and the real reading distribution:

| universe | forms | comparisons | divergences |
|---|---|---|---|
| exhaustive WordNet lemmas x {n,v,a,r,None} | 147,306 | 736,530 | **0** |
| all exception keys | 5,940 | 29,700 | **0** |
| generated inflections (s/es/ies/ed/ing/er/est/men/ves...) | 1,082,843 | 5,414,215 | **0** |
| real prose (UD-EWT train+test + all 301 GUM conllu) | 29,217 | 146,085 | **0** |
| **total raw morphy** | | **6,326,530** | **0** |
| **full hdlab lemma path** (lemma_word/lemma_verb/is_known_word/concept_lemma/gek, organ swapped in) | 29,217 tok | | **0** |

The proposed diff (replace each `wn.morphy(...)` with `morphology.morphy(...)`) changes NO output on the real
distribution or the whole lexicon. **The divergence set is empty (target 0 met).**

**4. THE OPTIMUM -- the brain-faithful organ EXCEEDS morphy (measure-first, then build).** Following the README's
Test-4 ("measure what the defect COSTS, not just that a fix exists"), I scored `morphy` against **human gold lemmas**
on modern prose (UD-EWT+GUM, gold given, so POS-tagging error is factored out and MORPHOLOGY is isolated). morphy is
**0.9603** (nouns weakest, 0.9379). Its dominant error (**6,238 of 7,747**) is `SURFACE_IS_LEMMA`: morphy checks the
SURFACE form FIRST and returns it whenever it is *coincidentally* a WordNet lemma -- `years`->`years`, `leaders`->
`leaders`, `men`->`men` -- instead of the OBLIGATORY decomposition the brain performs. **6,531 of 7,747 errors have a
base that is itself a WordNet lemma** = measured headroom recoverable with no new knowledge.

The brain-faithful fix is one change: **prefer the decomposed / stored base over the surface** (obligatory
decomposition; the stored route wins). `exp_dualroute_morphology_exceed_v1.py`:

| arm | gold-lemma acc (n=195,045) | vs morphy |
|---|---|---|
| MORPHY (floor) | 0.9603 | -- |
| **DUALROUTE (brain-faithful)** | **0.9836** | **+0.0233, CI [0.0221, 0.0246], sep** |
| TWIN (info-free, wrong-POS strip) | 0.7255 | dual-twin +0.2581 CI-sep (twin LOSES) |

**4,957 fixes vs 404 breaks (NET +4,553).** The 404 breaks are exactly the linguistically-correct STORED slice:
lexicalized plurals (`means`=method, `troops`, `grounds`, `dynamics`, `corps`, `auspices`) and lexicalized
comparatives (`outer`, `further`) -- forms the brain stores (Pinker's stored route covers lexicalized regulars).

**LOAD TIME (bar item "load time <= the current nltk path") -- PASSED with ~80x margin.** Cold load + first lemma,
3 fresh subprocesses each: nltk WordNet **~8.9s** (8.48-9.32s; the zip-corpus load) vs the glass-box organ **~0.11s**
(0.108-0.155s; a 2.19 MB flat asset). Removing the tool also removes the ~9-second cold WordNet load on first
lemmatize.

**5. GENERALIZES (`exp_dualroute_generalization_v1.py`).** The +2.3-point gain holds in the SAME DIRECTION on all 24
corpus/genre splits (weblog, reviews, email, academic, news, fiction, interview, how-to, vlog, conversation, legal,
medical, court, poetry, ...), **23/24 CI-separated** (only syllabus n=1,025 touches zero). The organ has **zero fitted
parameters** -- it is a linguistic mechanism, not a trained model -- so this is distributional robustness, not
train/test generalization.

## UPSTREAM SIGNAL TRACE (the owner's directive: where is signal lost up the chain, and is it non-BF?)

The lemma rung's inputs are (a) the surface form (from the glass-box tokenizer -- BF) and (b) the POS. I measured the
morphology GIVEN the gold POS. But the LIVE `lemma_word` gets **NO POS** -- it tries `n->v->a->r` in a fixed noun-first
order, because the meaning chain removed the POS tagger. `exp_dualroute_optimize_and_upstream_trace_v1.py`:

| arm | gold-lemma acc | note |
|---|---|---|
| MORPHY_GEN (POS-generic, today's `lemma_word` core) | 0.9177 | |
| DUAL_GEN (dual-route, POS-generic) | 0.9352 | +0.0175 over morphy, CI-sep (exceed holds without POS) |
| DUAL_GEN_FB (+ orthographic de-doubling fallback) | 0.9359 | +0.0007 -- near-redundant once decomposition is obligatory |
| **DUAL_POS (given gold POS)** | **0.9836** | |

**The missing POS signal costs +0.0484 (CI [0.0442, 0.0503], sep) -- LARGER than the morphology fix itself.** The
dominant signal loss on the lemma rung is NOT the algorithm; it is that the live path lemmatizes with no POS. This
traces exactly to the **POS tagger**, which `BRAIN_FOUNDATIONAL_AUDIT`/`FULL_CHAIN_BF_AUDIT` already flag **NOT_BF**
(frozen supervised averaged-perceptron + hard Viterbi). This is the owner's thesis confirmed with a number: a
brain-faithful component (morphology) is capped by an upstream input that is not yet 100% BF.

## UPSTREAM PROTOTYPE + FULL-CHAIN BF TRACE (owner ask: prototype the POS upgrade BF, optimize morphology on top, and confirm upstream-of-POS is BF)

I prototyped a **mathematically-BF POS posterior** and ran the whole stack. `glassbox_pos_bayes.py` is a GENERATIVE
count-based hidden-Markov category model: lexical prior P(word|tag) + morphological suffix cue P(suffix|tag) +
sequential prior P(tag|prev), all estimated by COUNTING (Hebbian/frequency accrual, online-compatible -- NOT gradient
/likelihood optimization), combined generatively (Bayes) and settled by FORWARD-BACKWARD into a GRADED per-token
posterior (argmax, not hard Viterbi). This is the owner's "counts + Bayesian cue integration, graded belief" form
(MacDonald 1994 constraint-satisfaction; Kuperberg-Jaeger 2016), and it is strictly MORE BF than the landed glass-box
CRF (`hdlab/crf_tagger.py`), which is likelihood-TRAINED and discriminative.

`exp_glassbox_pos_bf_and_morphology_stack_v1.py` -- trained by counting on UD-EWT, tested on **held-out GUM** (counts
never see GUM), 290,902 tokens:

| | value |
|---|---|
| BF POS -- UPOS accuracy (GUM) | 0.8559 |
| BF POS -- content-category (n/v/a/r) accuracy (GUM) | 0.9018 |
| morphology, DUAL_GEN (no POS, floor) | 0.9389 |
| **morphology, DUAL_POS_bayes (BF POS upstream)** | **0.9614** |
| morphology, DUAL_POS_gold (perfect POS, ceiling) | 0.9844 |
| morphology, DUAL_POS_twin (shuffled POS, info-free) | 0.8917 (LOSES) |

**The BF POS recovers 49.5% of the perfect-POS morphology gain (+0.0225), twin losing.** The whole stack -- tokenizer
-> POS -> morphology -> WordNet check -- is glass-box with no external tool at inference. The count-based HMM is less
accurate than the (less-BF) likelihood-trained CRF, so it recovers about half the available gain; that is an honest
BF-vs-accuracy tradeoff and names the next increment (below).

**Is upstream-of-POS BF? -- traced top-down, each rung:**

| rung | mechanism | at inference | verdict |
|---|---|---|---|
| tokenizer / word segmentation | `_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")` (glass-box regex; **confirmed NO module-level spaCy anywhere in hdlab, NO nltk tokenizer**) | deterministic, no tool | **BF** -- orthographic word-boundary detection (computational-level faithful) |
| POS category (this prototype) | generative count HMM + forward-backward graded posterior | glass-box, no tool, generative Bayesian cue integration | **BF at inference** |
| POS parameter ACQUISITION | emission/transition/suffix COUNTS (Hebbian form) from **gold-POS-labeled UD-EWT** | -- (static asset) | **admissible offline SUPPLY (passes the no-tool-at-inference invariant), but NOT the brain's unsupervised category induction** -- this is the one residual |
| morphology (this problem) | dual-route obligatory decomposition + WordNet export | glass-box, no tool | **BF** |

**Answer:** at INFERENCE the chain is BF top-to-bottom -- there is no external tool anywhere from raw text to lemma
(regex tokenizer -> count-based HMM -> dual-route morphology -> WordNet-export check). The **one residual upstream** is
that the POS category parameters are learned from SUPERVISED POS labels (admissible offline supply, like WordNet, so it
does not break the invariant) rather than the brain's UNSUPERVISED distributional category induction (Mintz frequent
frames; Redington-Chater-Finch). Per the owner's warning, that is the acquisition-fidelity gap to close if "100%
mathematically BF" must include HOW categories are learned; it does not block this problem (no inference-time tool) but
it caps how much of the +4.84 a fully-BF POS can recover.

## What I did NOT establish / would withdraw first

- **The EXCEED is not landed and is not byte-identical (by design).** It changes 4,957+404 lemmas, so it changes the
  KEYS of lemma-keyed stores (GEK event store, grounded vocab, common-noun conceptkeys) built with morphy lemmas.
  Landing it is the **consumer-repair** step (rebuild those keys with the new lemma -- do NOT revert the BF rung). The
  first thing I'd withdraw if wrong is any *downstream* benefit claim for the exceed: I proved the UPSTREAM capability
  (gold-lemma accuracy) and the coverage-proxy was FLAT (0.9743->0.9743), so the value is *correctness* (unifying
  `years`/`year`, `men`/`man` to one concept), not raw coverage -- an honest, bounded claim.
- **Frequency arbitration is a located sub-negative.** WordNet's sense-tagged counts do NOT cleanly separate
  lexicalized plurals (keep) from regular plurals (strip) -- `years` has count 25 (SemCor tags inflected uses under the
  lemma), so a frequency gate would re-break what dual-route fixes. The clean fix for the 404 breaks is a small curated
  STORED lexicalized-form set, which I declined to fit (it would fit to gold); I name it as the next increment.
- **The named downstream witnesses / board self-test** are byte-identity-preserved by construction (0 divergences on
  their exact vocab), so the PORT leaves them unchanged; I did not re-run all three to green under a live swap (I cannot
  write hdlab), but the full-path 0-divergence proof is the equivalent evidence. Ran at HEAD to establish the baseline:
  `test_fused_sense_ranker_live` (8/8) and `test_meaning_fusion_live_coverage` (38/38) are **green**;
  `test_cn_conceptkey_binding` is **RED at HEAD** on its V1 assertion (`resolve_param(crude,string)` reproducing the
  live wire on `GUM_academic_census`) -- a CRUDE-regex-vs-live-wire coref faithfulness check that is **independent of
  morphy's implementation**. Because the port is byte-identical, it neither causes nor fixes this pre-existing failure
  (same outcome under either backend). Flagging it as a pre-existing HEAD issue, not a regression from this work.

## KEY REALIZATIONS
- **`morphy` is a surface-first ENGINEERING heuristic, not the brain's morphology.** Checking `[form]` before the
  stripped candidate makes it return the surface whenever it is coincidentally a lemma (`years`->`years`). The brain
  decomposes obligatorily then checks. This single insight is both why the port is trivially faithful AND why a
  brain-faithful organ *exceeds* it -- the tool was leaving 2.3 points of correctness on the table.
- **Measure the defect before building the fix (Test-4).** The gold-lemma diagnosis turned a vague "make it glass-box"
  into a numbered headroom (6,531 recoverable errors) and told the fix exactly what to change.
- **The upstream trace found the real bottleneck.** The morphology algorithm was worth +2.3; the *missing POS input*
  was worth +4.8. The biggest lemma-rung signal loss is an upstream non-BF component (the POS tagger), exactly as the
  owner predicted.

## COMPONENTS INTERACTED WITH / CREATED + MATHEMATICAL BF STATUS
**A. Interacted with (hdlab, read-only):** `thematic_role_labeler.lemma_word/lemma_verb/is_known_word` (BF_SPIRIT;
irregular table + morphy + guarded fallback -- morphy step is the external-tool defect this removes); `lexical_utils.
concept_lemma` (BF_SPIRIT; noun-morphy of the head); the ~13 read-path `wn.morphy` call sites (`causation_typing`,
`definitional_extraction`, `definitional_predicate_v61`, `event_type`, `generalized_event_knowledge`,
`goal_achievement`, `goal_outcome_relation(_grounded)`, `patient_tendency`, `predictive_world_model`,
`typed_selectional_preference`) -- all BF_SPIRIT in computation, external-tool in implementation.
**B. Created:** the offline morphology asset (FOUNDATION -- static WordNet export, admissible supply); the glass-box
`morphy` port (**BF -- exact computation, glass-box, byte-identical, no tool at inference**); the dual-route organ
(**BF -- Rastle-Davis + Pinker-Ullman obligatory decomposition, validated to EXCEED on human gold, twin-controlled,
generalizes**); the gold-lemma diagnosis + generalization + upstream-trace measurements (measurement, gold = admissible
offline SUPPLY, never on a read path).

## ADJACENT COMPONENTS (remaining nltk on the read path -- for the next brief, NOT this scope)
`hdlab/conceptual_meaning.py` does `from nltk.corpus import wordnet` at read time (noted in the audit). The WordNet
**TAXONOMY** consumers -- `typed_spokes` (is-a), `coarse_cluster`, `animacy_lexicon`, `underspecified_sense_reader`,
`wordnet_polarity_propagation`, and the synset/hypernym users among the 39 nltk-importing modules -- read WordNet's
relational structure (a curated taxonomy foundation, admissible supply per the owner), NOT morphology. They are the
SEPARATE next problem; enumerated here so it can be posted precisely. This problem removes only the MORPHY (morphology)
call sites.

## PROPOSED hdlab DIFF (Q111 -- strategy lands it)
1. Add `hdlab/morphology.py` = `experiments/glassbox_morphology.py` (reads `data/frontend_assets/morphology/`; run the
   build script once to materialize the asset). Ship the port with `self_test_rules()`.
2. Repoint every read-path `wn.morphy(...)` -> `morphology.morphy(...)` (grep `morphy` in `hdlab/`): in
   `thematic_role_labeler` (lemma_word/lemma_verb/is_known_word -- keep `_IRREGULAR_LEMMA` and the guarded fallback,
   just swap the morphy calls), `lexical_utils.concept_lemma`, `causation_typing`, `definitional_extraction`,
   `definitional_predicate_v61`, `event_type`, `generalized_event_knowledge` (incl. the warmup call),
   `goal_achievement`, `goal_outcome_relation(_grounded)`, `patient_tendency`, `predictive_world_model`,
   `typed_selectional_preference`. Do NOT touch the taxonomy/synset uses. This is BYTE-IDENTICAL -> land with no
   downstream change; re-run `test_fused_sense_ranker_live` (8/8 at HEAD), `test_meaning_fusion_live_coverage` (38/38
   at HEAD), board `--self-test`, and confirm 0 change vs HEAD. NOTE `test_cn_conceptkey_binding` is RED at HEAD on its
   V1 crude-vs-wire check (independent of morphy); expect it to stay in the same state (byte-identical), not to flip.
3. (Optimization, follow-on) add `mode="dualroute"` to the organ (the exceed arm) and rebuild the lemma-keyed stores
   (GEK, grounded vocab, coref conceptkeys) with the new lemma -- the consumer-repair for the +2.3-point capability
   gain. Do not enable it until the consumers are rebuilt.
4. Per the strategy addendum: `thematic_role_labeler`'s dormant perceptron role-labeler (`role_feats`/`train_perceptron`
   /`label_roles`, zero live consumers) can be pruned; `frame_slot_role`/`is_strictly_intransitive`/`is_passive_clause`
   are verb-frame utilities (leave, note they belong with the verb-frame supply).

## AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT / FULL_CHAIN_BF_AUDIT rung 1)
Rung 1 (lemma normalize) can move from "BF_SPIRIT w/ EXTERNAL-TOOL DEPENDENCY" to **BF (glass-box)** once the port
lands: the morphological decomposition is now a glass-box exact port (byte-identical, no nltk at inference), and a
brain-faithful dual-route form EXCEEDS the tool. New recorded deviation to add: the live lemma path is **POS-generic**
(noun-first, no POS input), costing +0.0484 gold-lemma accuracy vs POS-conditioned -- the POS tagger (NOT_BF) is the
upstream lever on this rung.

## HIGH-PRIORITY NEXT STEPS
> **STATUS (this solver session):** the IN-SCOPE steps are DONE -- byte-identical port proven, dual-route optimum
> proven + generalized, and the required upstream BF POS prototyped and measured end-to-end. The REMAINING steps are
> either (a) hdlab LANDING (strategy's, per Q111), (b) a SEPARATE filed problem (the POS tagger; the WordNet-taxonomy
> consumers), or (c) a research-sized BF-acquisition build (unsupervised category induction). None is a within-scope
> solver deliverable left undone; each is routed to its correct owner below.

- **[HIGH] Land the byte-identical port** (step 1-2) -- removes the last non-glass-box rung on the meaning chain, zero
  downstream risk. (hdlab write -> strategy, Q111.)
- **[HIGH, upstream -- THE HEADLINE DEPENDENCY] Upgrading the POS tagger was REQUIRED to realize this fix, and it is
  not done.** The missing POS signal costs +0.0484 (> the morphology fix). I prototyped the BF POS (generative
  count-based graded posterior) and it recovers ~half the gain (0.9389->0.9614); the residual is that its categories
  are learned from SUPERVISED labels, not the brain's UNSUPERVISED distributional induction (Mintz/Redington). Next:
  (a) raise the count-based POS accuracy (richer BF cue integration) toward the CRF's, and (b) close the acquisition
  gap with unsupervised category induction. Ties to the open `upgrade_the_pos_tagger_to_a_calibrated_joint_decoded_posterior`
  (which landed a likelihood-trained glass-box CRF, `hdlab/crf_tagger.py` -- BF_SPIRIT, still gradient-trained; the
  count-based generative form here is more BF but currently less accurate).
- **[MED] Land the dual-route optimum** (+2.3 pts, generalizes) with the consumer-rebuild of lemma-keyed stores.
- **[MED] The 404-break stored-lexicalized-form set** (means/troops/grounds/outer...) -- the next fidelity increment,
  from a curated store, not a gold fit.
- **[MED] Adjacent: the WordNet-taxonomy read-path consumers** (conceptual_meaning + the is-a/synset users) are the next
  glass-box/foundation problem.
- **[RESEARCH, the deepest BF POS-category fix] Unsupervised distributional category INDUCTION** -- the only way the POS
  becomes 100% BF including ACQUISITION (not just inference). The brain acquires grammatical category label-free from
  distribution: Mintz 2003 frequent frames (aXb contexts), Redington-Chater-Finch 1998 distributional clustering,
  2-year-olds slotting invented verbs from frame alone (Yuan 2011). Prototype: cluster word types by their local
  context distributions (frequent-frame / left-right neighbour vectors), map clusters to the coarse content categories
  the morphology routes on, feed to the dual-route organ. This replaces the supervised-label count source (the one
  residual named in the upstream trace) with the brain's own mechanism. It is a separate problem-sized build (belongs
  with the POS problem), scaffolded here by `glassbox_pos_bayes.py`/`glassbox_pos_trigram.py` (the generative
  count-based form; swap the supervised tag counts for induced-cluster counts).

---

## TLDR
Before the reader can look a word up it must turn "dogs" into "dog" and "went" into "go". It was asking an outside
dictionary tool to do that on every word it read. I rebuilt that step from a one-time copy of the dictionary so nothing
external runs while reading, and proved the new version gives the **exact same answer** on over six million test words
plus real modern text -- so nothing downstream changes. Going further, I measured the old tool against human-annotated
answers and found it is wrong about 4 times in 100 (it leaves plurals like "years" and "leaders" unchanged instead of
reducing them); the way the brain actually does it -- always peel the ending and check -- is **right about 98.4 times
in 100**, a real improvement that holds across two dozen kinds of writing. I also traced *why* the reader still loses
some accuracy here, and the bigger cause is upstream: the reader currently doesn't know a word's part of speech when it
looks it up, and supplying that (from a brain-faithful part-of-speech step) would help about twice as much as the
morphology fix.

## QUESTIONS
None -- submission-ready as SOLVED (byte-identical glass-box port meeting the bar, plus a measured brain-faithful
optimum). Pending your DONE verdict before strategy integrates.

## NEXT STEPS
In HIGH-PRIORITY NEXT STEPS above; the load-bearing ones are (1) land the byte-identical port to clear the last
non-glass-box rung, and (2) treat the POS tagger as the upstream lever, since the missing part-of-speech signal costs
more here than the morphology itself.

INTEGRATED_BY_STRATEGY 2026-09-12 — owner-DONE 22:30; reverified 4/4 first-hand. Port LANDED as hdlab/morphology.py + 13 read-path repoints (commit 35f8b4dab), byte-identical; dual-route optimum and BF-POS prototype recorded as follow-ons (INTEGRATION_LEDGER).
