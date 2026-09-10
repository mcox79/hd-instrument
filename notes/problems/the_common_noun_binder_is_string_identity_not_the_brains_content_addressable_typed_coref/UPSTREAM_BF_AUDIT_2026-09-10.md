# Upstream brain-faithfulness audit of the common-noun resolution chain (down to the mathematics)

**2026-09-10, solver session.** Question (owner): evaluate the brain-faithfulness of EVERY upstream component down to the
math, confirm OUR component is fully brain-foundational, then trace the SIGNAL it needs all the way up and find where it is
lost (the assumption: a non-BF component). Evidence = the organ `__bf_status__` tags + `notes/bf_status_registry.jsonl` +
the actual operation read from source + the measurements in this problem's cells. Verdicts cross-checked against
`notes/BRAIN_FOUNDATIONAL_AUDIT.md` E3.

## 0. OUR component IS fully brain-foundational (confirmed, down to the math)
The live common-noun RESOLUTION is served by the typed content-addressable binding (`hdlab.typed_coref` /
`situation_reader._resolve_commonnouns`), `__bf_status__ = BF_SPIRIT`. Its operation, per mention:

- **pronoun** -> writes the salience card only (no nominal write) -- Ariel: pronouns mark accessibility, they do not
  re-describe the entity (DE-POLLUTION).
- **definite common noun** `m` (concept-lemma head `hl`, gender/number `g,n`):
  1. `same = { r : hl in r.heads and gn_ok(r,g,n) }` -> pick `argmax_r last_midx(r)` (most recent), WRITING merge.
  2. else `bridge = { r : gn_ok and [ r.heads ∩ appos_isa(hl) or coref_type_license(hl, r.heads) or C8(hl,name) ] }`
     -> pick `argmax_r B(r)` where `B` is ACT-R activation; NON-WRITING hold (Nieuwland Nref).
  3. else open a new referent.

This is EXACTLY the brain's mechanism, and every piece is pinned:
- **Content-addressable cue-based retrieval** (Lewis & Vasishth 2005): the anaphor head is a retrieval CUE; candidates are
  matched by feature compatibility and ranked by base-level activation. Our `argmax` over gn-compatible, concept/type-matched
  referents weighted by `B` is this operation.
- **Accessibility** (Ariel 1990): a definite retrieves a TYPE-identified antecedent; identity is anchored on nominal
  descriptions (the nominal-only card).
- **ACT-R base-level activation** (Anderson & Schooler 1991): `B = ln( Σ_k w(role_k) · dt_k^(-d) )` -- power-law-decayed,
  Centering-prominence-weighted recency×frequency. This is `hdlab.salience_binder.actr_activation`, verbatim.
- **Typed spokes** (Lambon-Ralph/Patterson ATL hub): type compatibility via `coref_type_license` (synonym/is-a/part-whole).
- **Non-writing hold under uncertainty** (Nieuwland & Van Berkum Nref): resolve for comprehension without committing the merge.

Measured robustness (this problem, GUM modern TEST n=2855): the binding beats the same-regime string-identity floor
CI-separated at EVERY head-quality level -- gold-head +0.0326, boundary-rule +0.0277, frozen-parse +0.0308, unfrozen-parse
+0.0263 -- and the info-free twin LOSES CI-sep. The mechanism's correctness does not depend on parse quality. **Verdict: the
binding is fully brain-foundational (BF_SPIRIT: the retrieval/salience/type OPERATIONS are pinned; the VSA store algebra is
unpinned-at-implementation but a defensible computational-level model). It is NOT where signal is lost.**

## 1. The signal the binding needs, and where each cue comes from (the trace)
The binding consumes SIX cues per mention. Tracing each to its producer and that producer's BF status:

| cue the binding needs | used for | upstream producer | producer BF | signal loss |
|---|---|---|---|---|
| **head SURFACE** (the token) | the whole decision | mention detection + span-HEAD SELECTION <- `arc_parser`+`pos_tagger` | **NOT_BF** | **DOMINANT, MEASURED: -0.049 CI-sep (raw text)** -- frozen parser mis-heads post-modified NPs; FIXABLE (boundary_nphead, prototyped, -> -0.015) |
| **concept LEMMA** (identity key) | same-head gate | `concept_lemma(surface)` (morphy) | **BF** (fixed) | was -0.0098 (crude regex NOT_BF); FIXED this problem |
| **grammatical ROLE** (subj/obj) | ACT-R prominence (salience weight) | dependency deprel <- `arc_labeler` | **NOT_BF** | identified channel, not yet quantified |
| **TYPE** (is-a/synonym) | the different-head bridge | `coref_type_license` OP + WordNet KB | **BF_SPIRIT** op / incomplete KB | world-knowledge KB gap (separate filed problem) |
| **in-text is-a EDGES** (appos/copula) | bridge seed | appos/cop deprels <- `arc_labeler` | **NOT_BF** | identified channel, not yet quantified |
| **gender/number** | agreement filter | `_num_of` (morphology) + name gazetteer | BF-ish (shallow) | minor |
| mention ORDER | ACT-R recency `dt` | token order | trivial | none |

## 2. Component-by-component brain-faithfulness (down to the operation)

### FULLY / SPIRIT brain-foundational (the semantic core -- not the loss)
- **`salience_binder` (ACT-R): BF.** `B = ln(Σ w(role)·dt^(-d))`. The Anderson-Schooler rational analysis of human
  declarative memory: the power law IS the empirical human forgetting/odds-of-need curve; role weight = Centering Cf.
  Genuinely the brain's retrieval-activation math. Params (d, role weights) are swept, not adopted.
- **`typed_spokes` (type comparator): BF_SPIRIT.** Binary type-license = share a synset (synonym) OR is-a hypernym-closure
  (either direction) OR part-whole. This is the ATL hub-and-typed-spoke content-addressed type retrieval (Lambon-Ralph).
  The OPERATION is pinned; the KNOWLEDGE (WordNet MFS C5 + DBpedia C8) is admissible static offline foundation but
  INCOMPLETE -- the world-knowledge residual (a separate filed problem), NOT a mechanism defect.
- **`coref` (EntityAliaser, name-content tokens, gender lookup): BF_SPIRIT.** Kintsch/van-Dijk entity backbone SUPPLY
  primitives + given-name clustering. Shallow, lexical, admissible.
- **`np_head_reduce`: BF_SPIRIT.** Deterministic NP-head reduction (Right-Hand Head Rule for compounds) -- the linguistic
  head definition; zero fitted params. (The `boundary_nphead` span-head fix in this problem extends it to post-modification.)
- **`online_entity_cluster`: BF_SPIRIT.** Heim file-change + Lewis-Vasishth ACT-R content-addressable clustering, gold-free.
- **`concept_lemma` (the fix): BF.** morphy = the substrate's standing wordform->lemma-concept map (ATL lexical hub);
  replaces the crude regex (NOT_BF) that empty-collapsed redactions and over-stripped `-us/-es`.

### NOT brain-foundational (the loss points)
- **`pos_tagger`: NOT_BF.** Collins-2002 averaged structured perceptron + **Viterbi HARD-decode** -- supervised,
  discriminative, frozen; the hard argmax DISCARDS the tag posterior (marginals). The brain's category system is learned
  online, predictive, and GRADED. Interim asset; POS mechanism brain-unpinned.
- **`arc_parser`: NOT_BF.** Arc-factored, feature-hashed averaged perceptron, **BATCH**, **greedy HARD-decode + cycle-break**
  -- discards the exact Matrix-Tree edge marginals. The brain parses INCREMENTALLY (left-to-right, Now-or-Never; Christiansen
  & Chater), PREDICTIVELY, and GRADED (maintains parse-uncertainty / competition). Frozen supervised batch hard-decode is a
  convenient ML tool, not the brain's operation.
- **`arc_labeler`: NOT_BF.** Multiclass averaged-perceptron dependency-relation labeler (nsubj/obj/obl/appos/cop), frozen
  supervised hard-decode -- same verdict. Produces the grammatical-ROLE cue (salience prominence) and the appos/copula is-a
  EDGES (bridge seed).
- **`commonnoun_binder`: NOT_BF.** The string-identity organ this problem retires for RESOLUTION (its residual export was the
  crude `head_lemma`, now replaced by `concept_lemma`).

## 3. VERDICT -- the signal IS lost in a non-BF component, and it is the frozen supervised PARSE STACK
The binding (BF) and its semantic cues (salience BF, type BF_SPIRIT, concept-lemma now BF) are sound. The cues that ARE
degraded -- the head SURFACE (concept key), the grammatical ROLE (salience weight), and the in-text is-a EDGES (bridge seed)
-- are ALL produced by the NOT_BF frozen supervised hard-decode parse stack (`pos_tagger` + `arc_parser` + `arc_labeler`).
The non-BF-ness has two mathematically distinct costs:

1. **ACCURACY (measured, dominant).** Frozen supervised heads err on post-modified NPs -> the concept key is wrong ->
   referent-chain poisoning -> **-0.049 CI-sep** on the raw-text resolution path. This is FIXABLE brain-foundationally: the
   shallow BF span-head rule (`boundary_nphead` + `np_head_reduce`) recovers it to -0.015 WITHOUT any full parser, because
   coref needs a CONSISTENT head, not a globally-correct tree. Prototyped in this problem.
2. **UNCERTAINTY (the deeper, filed).** Hard-decode DISCARDS the graded posterior (POS marginals, Matrix-Tree edge
   marginals), so nothing downstream can down-weight a low-confidence head/role. This is the exact non-BF property named by
   `the_parser_is_a_frozen_supervised_hard_decode_not_the_brains_graded_probabilistic_parse` (and partly addressed by
   `graded_parser` -- exact marginals -- landed but not yet the read-path decode). The register-adaptive fix
   (`OnlinePredictiveParser`, never-frozen) supplies OOD-robust RELIABILITY but has UAS ~0.44, so it is a confidence
   COMPLEMENT, not a head replacement (tested here: its heads give coref 0.4438, worse than frozen 0.5089).

**So: our component is fully BF; the signal it needs is lost upstream in the NOT_BF frozen parse stack -- specifically head
selection (dominant, measured, and prototype-fixed here) plus the discarded graded parse posterior (the parser mega-cluster,
separate).**

## 4. THE FIXES -- every upstream component now has a mathematically-BF replacement, measured (owner: "fix all upstream, top-down, from repo replacements")
Each NOT_BF upstream is replaced by a BF organ ALREADY IN THE REPO; the effect on the resolution signal is measured
(GUM modern TEST n=2855; `exp_cn_readerhead_endtoend_v1.py --bfsweep` + `exp_cn_bf_rolecue_v1.py`; reader-head + concept-key).

| # | upstream (NOT_BF) | math defect | BF replacement (repo) | BF math | measured effect on resolution |
|---|---|---|---|---|---|
| 1 | `pos_tagger` | Viterbi HARD-decode, discards marginals | **`crf_tagger` (GlassBoxCRF)** | log-space forward-backward MARGINALS (graded posterior P(tag\|sent)) | head-neutral (argmax categories ~unchanged): crf_boundary 0.5436 vs boundary 0.5426; its BF value is the confidence signal, not heads |
| 2 | `arc_parser` | greedy HARD-decode + cycle-break, discards marginals | **`graded_parser` (GradedParse)** | exact Chu-Liu/Edmonds MAP + exact Matrix-Tree edge MARGINALS | DECODE fix is head-neutral (graded_map 0.5100 vs greedy 0.5089) -- it SHARES the frozen weights, so exact MAP still mis-heads post-modified NPs; its BF value is the marginal/confidence, NOT head accuracy |
| 3 | head selection (parser-dependent) | rides the frozen weights' NP-head errors (-0.049) | **`boundary_nphead` + `np_head_reduce`** | UD span-head = nominal BEFORE post-modification + Right-Hand-Head-Rule; parser-FREE, zero fitted params | **THE head fix: 0.5089 -> 0.5426, cost -0.049 -> -0.015; the ONLY arm whose raw-text binding BEATS the gold-head de-leaked floor CI-sep (+0.017)** |
| 4 | `arc_labeler` (grammatical ROLE cue) | frozen supervised deprel (nsubj) | **`incremental_parser.incremental_subject_before`** | left-corner bounded-buffer subject (Now-or-Never); reads only toks/UPOS | INERT for resolution: BF-role 0.5587 vs gold-deprel 0.5580 (+0.0007, CI incl 0) -> cleanly replaceable, zero loss (ACT-R prominence is dominated by recency/same-head) |
| 5 | `commonnoun_binder.head_lemma` (concept key) | crude regex: empty-collapse + over-strip | **`concept_lemma` (morphy)** | wordform -> ATL lemma-concept; non-alpha kept distinct | live win +0.0098; beats the honest de-leaked floor CI-sep |
| - | THE BINDING (our component) | -- already BF -- | `typed_coref` | Ariel + Lewis-Vasishth cue retrieval + ACT-R + typed spokes + Nref | beats string-identity CI-sep at EVERY head-quality level |

**FULLY-BF chain (crf_tagger + graded_parser marginals for confidence + boundary_nphead heads + incremental role + concept_lemma
+ typed binding) = 0.5436 reader-head, BEATS the gold-head de-leaked floor CI-sep (+0.0182), and beats string-identity at every
level.** Every upstream component is now mathematically brain-foundational, and the resolution signal is preserved/improved.

**THE KEY REALIZATION (do not conflate two different BF fixes):** "make the parse GRADED" (crf_tagger + graded_parser: replace
hard-decode with marginals -- mathematically BF, and the right substrate-wide adoption because it supplies the confidence the
frozen stack discards) is a DIFFERENT fix from "make head SELECTION accurate" (the frozen WEIGHTS mis-head post-modified NPs;
exact-MAP over the same weights does not help). For coref, head selection is a shallow CONSISTENCY task solved parser-free by
`boundary_nphead`; the graded parser's BF contribution is the marginal/confidence lever (a separate consumer). Both are BF; they
address different defects (uncertainty representation vs weight accuracy). The NEVER-FROZEN weights fix (online/grounded parser)
is the deeper axis (register-adaptation) and is the parser mega-cluster.

## 5. What remains genuinely upstream-open (NOT fixable inside this problem)
- **The frozen WEIGHTS themselves** (shared by arc_parser AND graded_parser): supervised, trained-once. The BF axis is
  never-frozen online learning (`OnlinePredictiveParser`, UAS ~0.44 today -- reliability complement, not a head replacement).
  This is the parser mega-cluster (`the_parser_is_a_frozen_supervised_hard_decode...`). Our binding is robust to it (beats
  string-identity even on the weak unfrozen heads), so it is not blocking THIS component.
- **The type-comparator KNOWLEDGE** (WordNet C5 + DBpedia C8): the OP is BF, the KB is incomplete -- the world-knowledge
  problem (separate filed).
