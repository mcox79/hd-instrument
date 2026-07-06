# Research: composing the 4 glass-box language layers -- first end-to-end assembly, scoped (no cell built)

Date: 2026-07-05. Owner: Research. Type: scoping/design drill (task instruction: "write a notes drill; do NOT build a
cell yet"). Level-2 operational drill (2x discipline: drills EXISTING landed cells deeper into their mechanics, not a
re-verification lit-scan). `python tools/orchestrator/research_field_advisor.py` run at cycle start per contract --
confirmed (again, matching the same-day sibling scoping note) that this is an architecture/linguistics composition
question, orthogonal to the physics-field adjacency map; no physics field bears on it, correctly not skipped, just
correctly out of that map's scope. Method: direct filesystem verification of the 3 relevant cells' `metrics.json` AND
their `.py` source (not inference from prior notes) -- `data/exp_morph_ruleset_wug_v2_cpu/metrics.json` +
`experiments/exp_morph_ruleset_wug_v2_cpu.py` (full read), `data/exp_grammar_recursive_function_word_blocklocal_v1_smoke/metrics.json`
+ `experiments/exp_grammar_recursive_function_word_blocklocal_v1.py` (first 280 lines: header, config, codebook
construction), `data/exp_generation_decoder_gsbc_native_blocklocal_v1/metrics.json` -- plus 3 parallel Sonnet lit-scan
sub-agents (generic academic query terms only, per query-privacy discipline) targeting the one gap none of today's
prior sibling drills covered: how do you actually WIRE these 4 mechanisms together, and does the brain's own
production architecture have anything to say about the exact seam this repo's cells expose.

---

## HEADLINE

**The four cells do NOT share one vector algebra -- MORPHOLOGY runs in a completely different representational family
(dense complex-phasor FHRR) than LEXICON/SYNTAX/GRAMMAR (sparse block-local real-valued GSBC codes) -- but this is
NOT a design defect to fix by unifying the algebras. Three independent lines of evidence (VSA/HDC theory, Levelt/
Garrett/RML98 psycholinguistics, and the repo's own existing NLG-precedent citation) converge on the SAME resolution:
bridge the two mechanisms at the DISCRETE SYMBOL boundary (a concept-id + feature tuple), not at the vector boundary.
This is the field's normal readout idiom (cleanup/resonator decode-to-symbol), not an exotic workaround, and it is
independently how the one confirmed biological existence-proof (human sentence production) is architected (lemma and
lexeme are explicitly different "vocabularies" per Roelofs/Meyer/Levelt 1998, bridged by translation, with speech-
error evidence that they are separately manipulable subsystems). Given that resolution, LEXICON+SYNTAX+GRAMMAR are
ALREADY natively compatible (same N=8192, same F_SPARSE=0.02 block-local sparse-code family, and the decoder cell has
already proven its native-lexicon-filler arm hits exact_ordered=1.000 -- identical to its synthetic-filler arm), so
the ONLY new engineering the first assembly cell needs is: (1) a small glue/adapter at the Morphology<->Syntax
symbolic seam (deterministic concept-id -> FHRR-stem derivation, currently absent -- morphology's stems today are
freshly-random per trial, ungrounded to any real lexicon entry) and (2) the already-flagged small closed-class
function-word curation table (Layer C gap from the same-day sibling scoping note, reconfirmed here as a literal
blocker for THIS cell, not yet built). Both are glue, not research. The genuinely NEW empirical risk this cell
introduces -- never tested by any of the 4 cells in isolation -- is CROSS-LAYER IDENTITY CONSISTENCY: does the
concept-id Syntax recovers from the VERB slot actually match the concept-id Morphology inflected to produce the
printed surface string? That joint has never been exercised and is this cell's real discriminator.**

---

## 1. Composition architecture -- order, handoff points, and where the algebras actually differ

### 1a. What's already the SAME family (verified off three metrics.json + two .py sources)

| Layer | Representation | N / block layout | Bind / cleanup | Verified compatible? |
|---|---|---|---|---|
| LEXICON | `GSBC_EXPAND2X` native sparse-bipolar concept codes (`bge_large_v2_name_177899_54f7cf6a.npz` -> `id_order_json` string keys) | GSBC_DIM=8192, K_ACTIVE=192 (~2.34% active) | project into block; matched-filter cleanup | YES -- this IS the decoder's `native_filler` arm |
| SYNTAX (decoder) | Block-local sparse superposition, disjoint blocks by slot | N_DIM=8192, D slots, bs~=N/D (grid: D=3..26) | `algebra=block_superposition_sum`, `position_binding=disjoint_block_index` | YES -- `blocklocal_gsbc` arm (native lexicon fillers) == `blocklocal_synth` arm (clean synthetic fillers) at exact_ordered=1.000 across the WHOLE V/D grid tested (`data/exp_generation_decoder_gsbc_native_blocklocal_v1/metrics.json`, all `blocklocal_gsbc@*` and `blocklocal_synth@*` arms tie at 1.0 through D=12, and 0.86-0.99 at the D=26 edge) -- the architecture is explicitly filler-representation-agnostic as long as fillers are sparse-bipolar codes of the right block size |
| GRAMMAR | Block-local sparse superposition, disjoint BANDS (level x slot) | N_DIM=8192, F_SPARSE=0.02 (matches decoder/comprehension), bs=N/(LEVELS\*S_SLOTS) | same block-disjoint bind/cleanup family; content slots decode "vs the content codebook" | YES BY DESIGN -- grammar cell's own header explicitly says it "reuses" `exp_generation_decoder_gsbc_native_blocklocal_v1` and `exp_comprehension_envelope_superposition_vocab_v1`, cites the decoder's D<=26/V<=1024 ceiling as its own CRLB, and uses the identical F_SPARSE=0.02 sparsity constant |

So LEXICON, SYNTAX, and GRAMMAR are not merely "similar" -- they are the SAME architecture family, deliberately built that way (the grammar cell's header lists the decoder and comprehension cells as direct reuses). The one thing NOT yet verified (see mismatch #3 below) is that grammar's own (LEVELS,S_SLOTS)-based block-size schedule (`bs = N/(LEVELS*8)`, e.g. bs=1024 at LEVELS=1, bs=512 at LEVELS=2) has actually been exercised with REAL lexicon-projected fillers rather than grammar's own synthetic `_sparse_bipolar()` codebook (`experiments/exp_grammar_recursive_function_word_blocklocal_v1.py` lines 250-279 -- confirmed by direct read: the content codebook is freshly generated per (LEVELS,V,seed) via `np.random.default_rng`, not sourced from the lexicon table at all today).

### 1b. What's a GENUINELY different family (verified by direct read of `exp_morph_ruleset_wug_v2_cpu.py`)

MORPHOLOGY is **FHRR** (Fourier/complex Holographic Reduced Representation), confirmed line-by-line:
- `N=8192` complex64 unit-modulus phasors (`cphasor`: `np.exp(1j * ang)`), i.e. EVERY one of the 8192 components is nonzero and lives on the unit circle in the complex plane -- this is a DENSE representation, the opposite of GSBC's ~2% sparse real-valued blocks.
- Bind = elementwise complex multiplication (`surf = stems * TAG`); unbind = multiply by conjugate; cleanup = `argmax(Re(pred @ conj(cand).T))` over a small candidate set -- classical FHRR algebra (Plate 1995's Fourier variant), structurally unrelated to GSBC's block-disjoint-superposition bind.
- Stems are generated FRESH per trial/demo via `cphasor(1, N, g)` -- **not derived from the lexicon table at all.** The morphology cell today has zero wiring to any real concept id; it is a self-contained proof that the RULE-INFERENCE MECHANISM works, tested on synthetic stems in total isolation from the other 3 layers.

**This is the one real, load-bearing mismatch** the task asked to identify: two fully disjoint VSA algebras (dense complex-phasor vs. sparse block-local real), with the morphology side additionally ungrounded from the shared lexicon today.

### 1c. Resolution -- bridge at the symbol, not the vector (three independent lines of evidence)

**Lit-scan A (VSA/HDC theory, generic academic search, no direct precedent for fusing FHRR+block-sparse in one
pipeline found -- MEDIUM-HIGH confidence in that negative):** Kleyko, Rachkovskij, Osipov & Rahimi's HDC/VSA survey
(2022, *ACM Computing Surveys*, Parts I+II, arXiv:2111.06077 / 2112.15424) catalogs HRR/FHRR/MAP/BSC/sparse-block
models side by side but never fuses them in one system. No general dense-phasor <-> sparse-block CONVERSION method
exists in the literature either (closest analog: Frady/Kent/Olshausen/Sommer's Resonator Networks and Hersche et
al.'s "Factorizers for Distributed Sparse Block Codes," which decode a noisy CONTINUOUS product vector to DISCRETE
codebook indices -- decode-only, not a general re-encoding theorem). BUT Smolensky's original Tensor Product
Representation formalism (1990; formal treatment in Smolensky et al. 2016, arXiv:1601.02745) explicitly permits
`Bind(R,F) = R (x) F` with role-space and filler-space of DIFFERENT dimensionality -- the only formal requirement is a
consistent bind/unbind pair AT the binding site, not a shared algebra end-to-end. And critically: **decoding any
hypervector to a discrete symbol via cleanup/item-memory lookup is the field's NORMAL, ubiquitous readout mechanism**
(true since Plate 1995; resonator-network factorization is exactly this generalized to compositional structures) --
"decode-to-symbol-then-re-encode" at a subsystem boundary is not an exotic pattern, it is how VSA systems interface
with anything downstream. A 2026 category-theoretic VSA-foundations paper (arXiv:2501.05368) explicitly flags a
formal bridge between DIFFERENT VSA algebras as *future work*, i.e. openly unfinished theory -- so a literal shared-
vector-space fusion of FHRR and GSBC is NOT an available, proven path today; the symbol-level bridge is.

**Lit-scan B (Levelt/Garrett/Dell psycholinguistics, HIGH confidence on the core claim):** Roelofs, Meyer & Levelt
(1998, *Cognition* 69) state directly that "levels of representation are individuated by their vocabulary" -- the
LEMMA level (an abstract syntactic/semantic node carrying free "diacritic" parameters: tense, number, person, gender
-- explicitly NOT phonologically specified) and the LEXEME/morphological level (morpheme + segment structure --
explicitly NOT syntactically or semantically specified) are two DIFFERENT KINDS of object, not the same
representation at finer grain. Speech-error evidence for exactly this discontinuity: STRANDING errors (Garrett 1975,
1980) -- stems exchange in production ("ordered up ending" for "ended up ordering") while inflectional affixes stay
fixed to the FRAME, not the stem -- prove morphology and word-order/frame are separately-manipulable subsystems, not
one continuous medium. Van Turennout, Hagoort & Brown (1998, *Science* 280) give a hard empirical timing result:
grammatical-gender encoding completes and phonological encoding begins within a measured ~40ms serial window --
direct electrophysiological evidence for a real discrete-stage boundary, not a smooth continuum (their own
architecture is the strongest cited counter-evidence against "it's all one continuous representational medium").
Caveat, HIGH-on-existence/MEDIUM-on-universality: Caramazza & Miozzo (1997) and Dell's (1986) cascading-activation
model are real minority/middle positions arguing for a single lexical level or a softer, non-discrete boundary --
format-discontinuity is the DOMINANT view, not unanimous consensus.

**Lit-scan A + B jointly validate the same design call from two completely unrelated fields** (VSA formal theory and
psycholinguistic production-modeling) -- independent enough that this is a real convergence, not a shared bias.

**Existing repo precedent (already cited by the same-day sibling note, reused not re-derived here):** Reiter & Dale's
(2000) classic symbolic NLG pipeline (content planning -> microplanning -> surface realization) passes a DISCRETE
symbolic tree/feature-structure between every stage, never a shared vector medium -- this is a THIRD, independent
confirmation of "discrete symbolic handoff between structurally-different stages is the standard architecture," this
time from applied NLG engineering rather than theory or brain science.

### 1d. Explicit list of cross-layer representation mismatches (deliverable requirement)

1. **Algebra mismatch (Morphology vs. Lexicon/Syntax/Grammar):** dense FHRR complex-phasor vs. sparse block-local
   real-bipolar GSBC. No literature precedent for fusing them; TPR theory + the VSA field's own cleanup-decode idiom
   license bridging at the discrete symbol level instead. **Resolution: bridge at symbol, not vector. Not a defect to
   engineer away -- a legitimate, brain-analogous, field-standard design pattern.**
2. **Grounding mismatch (Morphology stems vs. real lexicon concept ids):** `exp_morph_ruleset_wug_v2_cpu.py` draws a
   fresh random `cphasor` stem per trial/demo -- ZERO wiring to any of the 177,899 real lexicon concept ids today.
   **Needs a NEW deterministic derivation:** `stem_vector = f(concept_id)` (e.g. an FHRR phasor seeded by a hash of
   the concept's integer id or its `id_order_json` string), so the SAME lexical item gets the SAME FHRR stem every
   time it is referenced, and a downstream identity-consistency check (Section 2) can verify morphology inflected
   the SAME concept syntax decoded. This wiring does not exist; it is a small (a hash/seed function) but REAL gap,
   not glue that is already sitting there unused.
3. **Block-size-schedule mismatch (decoder's native-filler projection vs. grammar's own block schedule):** the
   decoder's `native_filler` field says `"GSBC_EXPAND2X_seed7_FULL_projected_sparse_bipolar"` -- i.e. a projection
   step ALREADY exists to fit the full K_ACTIVE=192-of-8192 native code into the decoder's own flat `bs=N/D` block
   size. Grammar partitions N differently: `bs = N/(LEVELS*S_SLOTS)` (by clause-level-and-slot, not by flat D). The
   *mechanism* (project a sparse code into a smaller block) is proven to work in the decoder's own context; whether
   the SAME projection function composes correctly against grammar's specific bs schedule (e.g. bs=1024 at LEVELS=1,
   bs=512 at LEVELS=2, both smaller than several of the decoder's own tested bs values) has NOT been verified --
   mechanical, lower-risk than #1/#2, but unverified and must be checked (likely reuses the decoder's existing
   projection helper unmodified, but this has not actually been run against grammar's bs values).
4. **Feature-binding location (where does "PAST" or "PLURAL" live?):** neither the decoder nor the grammar cell
   carries a grammatical-feature dimension in its vector algebra at all -- their content slots hold a bare lexical
   concept id, nothing else. Morphology's inflection choice is driven by an EXTERNALLY-SUPPLIED feature tag (which
   rule to fire), not something recovered FROM the sentence-encoding vector. The (slot -> feature) assignment must
   therefore be tracked as a **separate, parallel symbolic sentence-plan structure** alongside the vector-level clause
   encoding -- bookkeeping in the glue code, not a wired vector-algebra property. This mirrors the Reiter & Dale
   precedent (content/feature planning as a symbolic tree, separate from surface realization) -- explicitly not a
   bug, but must be stated so no one expects the vector algebra itself to "carry tense."
5. **Vocabulary-curation gap (closed-class function-word strings):** grammar's function codebook (`DET`/`AUX`/`PREP`/
   `COMP` types, `V_FUNC=8` entries per type) is entirely synthetic/arbitrary-indexed today -- no assigned English
   string (no "the"/"a"/"is" mapped to any index). This is the same Layer-C gap the same-day sibling scoping note
   already flagged (~150-300-entry unbuilt table) -- reconfirmed here as a literal blocking glue-step specifically
   for this composition cell, still not built anywhere in the corpus.

None of these 5 mismatches requires new RESEARCH to close (no open theoretical question is being solved) -- all 5 are
either (a) already-precedented glue (symbol-level bridge, feature-tuple bookkeeping, vocabulary table) or (b) a small
new deterministic function (concept-id -> FHRR stem hash) that composes two already-proven mechanisms. This is
consistent with the same-day sibling note's finding that the remaining language-track work is staged, small,
independently-costed glue -- not a large undertaking.

---

## 2. The first assembly demo -- cell spec (arms / controls / bands), ready for exp_dev

**Scope choice (deliberate, reduces confounds per Fix #28 "never collapse to one aggregate"): LEVELS=1 (flat clause,
no recursive embedding) for demo #1.** Recursion is ALREADY the grammar cell's own proven anchor (LEVELS=2 HARD_PASS)
-- bundling it into the FIRST 4-layer join would confound "does the lexicon-morphology-syntax joint hold" with "does
recursion still hold once real content fills the slots," two different questions. Demo #1 answers the first; a
scoped follow-on (Section 3) answers the second by re-running this SAME chain at LEVELS=2 (no new mechanism, a
parameter change).

**Anchor sentence:** "the cat chased the dog" -> clause template (grammar cell's own S=8 slots, LEVELS=1):
`DET_S=the, SUBJ=cat, VERB=chase[+PAST], DET_O=the, OBJ=dog` (COMP/AUX/PREP empty -- matrix-clause-only, matches
grammar's own `L1_V*` cells, already measured `terminal_perslot=1.0, function_perslot=1.0`).

**Pipeline (encode direction):**
1. LEXICON: look up real GSBC_EXPAND2X native codes for `cat`, `chase`, `dog` from the 177,899-name pool (concept ids
   -- reuse the decoder's own `pool_meta` sampling convention, `data/exp_generation_decoder_gsbc_native_blocklocal_v1`).
2. Project each native code into grammar's LEVELS=1 block size (bs=1024) via the decoder's existing projection
   function (mismatch #3 -- verify it composes, do not assume).
3. GRAMMAR: bind `DET_S/SUBJ/DET_O/OBJ` content-slot fillers + `DET_S/DET_O` function-word fillers (from a NEW small
   curated `{the: DET[0]}`-style table, mismatch #5) into the block-local clause vector; superpose per grammar's
   proven `structured` arm construction.
4. MORPHOLOGY (parallel, off the SAME concept ids via the NEW hash-derived stem function, mismatch #2): apply the
   proven `past_ed` conditioned-transform to the `chase` concept's derived FHRR stem -> selects the correct
   allomorph (voiceless /t/: "chased") via the already-HARD_PASS mechanism.

**Pipeline (decode direction):**
5. SYNTAX/GRAMMAR resonator recovers the ordered slot-content-id sequence from the composite vector (reuses decoder
   Stage A/B/C + grammar's block-local per-slot argmax, both already independently HARD_PASS).
6. Walk the recovered slots in template order; look up each recovered content id's citation string via
   `id_order_json`; substitute the VERB slot's string with MORPHOLOGY's independently-computed inflected surface form.
7. Print the assembled string; compare to gold "the cat chased the dog."

**Arms:**
- `structured_joint` (PRIMARY, mechanism): the full pipeline above.
- `flat_bag` (control, REUSE grammar's existing arm unmodified): all slot codes superposed into one block, no
  positional separation -- already measured to collapse `tree_exact=0.0`, `terminal_perslot` 0.37-0.59.
- `scrambled_roles` (control, REUSE grammar's existing arm unmodified): tokens placed at a random (level,slot)
  permutation at encode, decoded via the true map -- already measured to collapse to near-chance/low term-acc.
- `naive_morphology` (control, REUSE morphology's existing arm unmodified): single blurred transform on the
  allomorphic `past_ed` rule -- already measured to collapse to ~0.33 (chance).
- `identity_scrambled` (control, **NEW -- the one arm that has never been run**): deliberately break the
  concept-id -> FHRR-stem hash mapping between Syntax and Morphology (e.g. morphology infers the stem for a
  DIFFERENT, randomly-chosen concept id than the one Syntax actually decoded for the VERB slot). This tests whether
  the two mechanisms are actually talking about the SAME lemma, not just independently producing plausible-looking
  output. **This is the cell's real discriminator** -- every other arm reuses an already-proven collapse; this one is
  new.

**Metrics (report separately per Fix #28, never collapse to one aggregate):**
- `exact_ordered_slot_match`: recovered slot-content-id sequence == gold sequence (chance ~0, per decoder's
  `noorder_ctrl`).
- `identity_consistency`: P[Morphology's inflected concept id == Syntax's decoded VERB-slot concept id] (chance =
  1/|candidate pool|, near 0 for a reasonably-sized pool).
- `surface_string_exact_match`: final printed string == gold string, on >= 20 held-out curated common-word S-V-O
  sentences (mix: >= 15 regular allomorph-bearing verbs across all 3 allomorph classes, >= 3 rules from the 8-rule
  set beyond just `past_ed`, >= 2 irregular verbs to exercise the dual-route exception gate).
- Per-control collapse values (reuse existing measured numbers for `flat_bag`/`scrambled_roles`/`naive_morphology`;
  measure fresh for `identity_scrambled`).

**Pre-registered bands (lit-scan-calibration-penalized per [[feedback-lit-scan-calibration-penalty]] -- deflate
0.15-0.25 from pre-penalty estimate, cap novel-synthesis P at 0.50):**

- **HARD-PASS:** `exact_ordered_slot_match >= 0.90` AND `identity_consistency >= 0.95` AND
  `surface_string_exact_match >= 0.90` on the >= 20-sentence set AND all 4 controls collapse (`flat_bag`/
  `scrambled_roles`/`naive_morphology` at their EXISTING measured near-chance levels; `identity_scrambled`
  `identity_consistency <= 0.20`).
- **HARD-FAIL:** `exact_ordered_slot_match < 0.50` DESPITE Syntax/Grammar/Morphology each independently clearing
  their own established HARD_PASS bars in isolation (an undiagnosed NEW integration-joint bug between three
  otherwise-proven primitives -- mismatch #3's projection-composition risk is the leading suspect) OR
  `identity_consistency < 0.50` (meaning the hash-derived bridge itself is broken -- the two mechanisms are not
  actually agreeing on which lemma is being discussed, a DESIGN failure of mismatch #2's resolution, not a component
  failure) OR any control fails to collapse (vacuous test, cannot attribute a pass to the mechanism).
- **MIDDLE:** in between -- diagnostic of WHICH joint is weak: slot-recovery fine but identity-consistency weak =
  the hash-derivation bridge (mismatch #2) is the specific problem; identity fine but slot-recovery weak = mismatch
  #3 (block-size projection) is the problem; surface-string weak while both vector-level metrics pass = a pure
  string-formatting/lookup bug (cheapest possible failure, not a mechanism issue).
- **OVER-CLAIM GUARD (HARD-FAIL regardless of numeric result, matches the framing discipline already established for
  all 3 component cells):** representing a HARD-PASS result as "the substrate composes sentences" in any general
  sense, "understands" the sentence, or as a step toward fluent language. Honest scope if it passes: four
  independently-proven glass-box PRIMITIVES chain correctly, via a discrete symbolic bridge, on a KNOWN
  pre-specified proposition and a curated handful of common words -- not generation, not understanding, not a
  language model.
- **P estimate (headline, deflated):** P(HARD-PASS) ~= 0.40, P(MIDDLE) ~= 0.40, P(HARD-FAIL) ~= 0.20. Pre-penalty
  reasoning: the Lexicon<->Syntax/Grammar handoff is essentially already proven (native-filler arm == synthetic-
  filler arm at 1.0 in the decoder cell); the ONLY genuinely untested joint is Morphology<->Syntax identity
  consistency, and the resolution strategy for it (symbol-level bridge) has THREE independent, converging lines of
  supporting evidence (VSA theory, psycholinguistics, existing NLG precedent) but has literally never been run in
  this repo -- hence deflation to 0.40 rather than the ~0.55-0.65 the individual-component maturity alone would
  suggest, per the mandatory novel-composition calibration discipline.

---

## 3. Honest claim line -- what this is, and is NOT, even if it HARD-PASSES

**What a HARD-PASS would prove:** four independently-built, independently-proven glass-box mechanisms (lexicon
lookup, algebraic dual-route morphological inflection, block-local syntactic slot-order recovery, recursive/
function-word grammar operators) can be CHAINED via a small, precedented, discrete symbolic bridge to produce one
legible, correctly-inflected, correctly-ordered English sentence from a fully KNOWN, externally-specified
proposition. Every emitted token traces to one algebraic operation (a rule firing, a resonator argmax, a table
lookup) -- inspectable end to end, matching the same-day sibling note's "printable lexicon + algebraic morphology +
bound-factor frame + resonator search" glass-box argument, now with actual cross-layer wiring verified rather than
asserted in isolation.

**What it would NOT prove, even on a clean HARD-PASS (explicit, per the standing over-claim discipline):**
- NOT that the substrate GENERATES or PLANS language: the proposition ("cat chased dog," not "dog chased cat") is
  given, not decided. That is the separate reason-generate bridge's job (already HARD_PASS elsewhere, per
  `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-05.md`), not exercised by this cell.
- NOT a language model: zero statistics, zero next-token probability, zero learned distribution over strings.
- NOT broad-vocabulary: a curated handful of common S-V-O words plus a ~10-30-entry function-word table (a subset
  of the sibling note's already-scoped ~150-300-entry Layer C target), not the full 177,899-name pool tagged/inflected.
- NOT recursive in this FIRST demo: LEVELS=1 only, by deliberate scope choice (Section 2). Recursion is a SEPARATE,
  already-proven, cheap follow-on (Section 4), not bundled in to avoid confounding two different questions.
- NOT proof of general "composition" or "understanding": proof that 4 SPECIFIC primitives chain, on a narrow curated
  set, nothing broader.

**What WOULD license the narrower, still-honest claim "the substrate composes structured sentences from a known
proposition":** this cell HARD-PASSing, INCLUDING the `identity_consistency` metric (the chain, not just the parts,
holding). What it would NOT additionally require: solving the one-to-many generalization/entropy ceiling (a separate,
already-closed structural bound per the backup doc), the Cortex-2 reasoning layer graduating past parked status, or
any general-knowledge ingest -- none of those gate this narrow claim, exactly as the sibling scoping note's
dependency table already established for the simpler grounded-utterance cell.

---

## 4. Brain grounding -- Levelt frame-slot production, kept honest (mechanism-analog, not task-analog)

Per the standing discipline (`feedback_mechanism_analog_is_not_task_analog...`), the following are claims about
PRODUCTION-ARCHITECTURE parallels, not claims of task-level or cognitive equivalence:

- **The lemma/lexeme representational-format split (Roelofs, Meyer & Levelt 1998) is a genuine, well-evidenced
  discontinuity in the human production architecture, not merely a convenient theoretical fiction** -- directly
  supporting this repo's own forced discontinuity (FHRR morphology vs. GSBC syntax/grammar) as a LEGITIMATE
  architecture pattern rather than an accidental design flaw needing correction. Stranding-error evidence (Garrett
  1975/1980/1988) shows morphological affixes and lexical stems are separately manipulable in human production,
  exactly the same separation this repo's Morphology-vs-Syntax split embodies (mechanism-parallel; NOT a claim the
  substrate has anything like human working memory or planning).
- **Van Turennout, Hagoort & Brown (1998, *Science*)** give a hard empirical timing result for a genuinely SERIAL,
  DISCRETE handoff between grammatical and phonological encoding (~40ms measured window) -- independent
  electrophysiological support for "discrete symbolic handoff between stages" over "one continuous representational
  medium," strengthening (not proving) the design choice in Section 1c.
- **Function words as structural GATES for recursion** (Frazier & Rayner 1982 and the broader NP/S garden-path
  literature: "The girl found (that) the lamb..." parses faster with "that" present because the complementizer lets
  the parser project a CP node immediately) directly cross-validates the grammar cell's own design
  (`function_word_treatment: closed_class_type_partitioned_selectional_restriction_COMP_gates_recursion` -- verified
  off the cell's own metrics.json config) -- the substrate's COMP-gates-recursion mechanism is not an arbitrary
  engineering choice, it mirrors a well-replicated real-time parsing effect (mechanism-parallel only).
- **Center-embedding depth-cliff comparison (honest, directionally-convergent, mechanism-DIFFERENT):** human
  center-embedding comprehension collapses SHARPLY (not gracefully) at a small depth -- Miller & Isard (1964)
  showed 2+ levels of embedding already read as ungrammatical approximations; Karlsson's (2007) 7-language corpus
  study found natural writing almost never exceeds depth 3, speech essentially never. The grammar cell's OWN
  boundary-map probe (verified off its metrics.json comment: `L4(bs256)=1.000 L8(bs128)=0.983 L12(bs85)=0.500
  L16(bs64,k=1)=0.067`) shows an analogously SHARP (not graceful) collapse at a comparably small structural depth.
  **The proximate MECHANISM differs and this must not be blurred:** the human account is dominated by
  similarity-based retrieval interference among simultaneously-open, structurally-identical dependencies (Lewis
  1996; Gibson 1998 Dependency Locality Theory) -- a working-memory/interference story -- while the substrate's
  cliff is a literal per-block signal-to-noise/capacity shrinkage as `bs = N/(LEVELS*S_SLOTS)` shrinks with
  recursion depth -- a raw capacity-partitioning story. Both produce a SHARP cliff at a SMALL depth; the CAUSE is
  not claimed to be the same mechanism, only that "sharp cliff at small depth, not graceful decay" is itself a
  notable directional convergence worth citing as a cheap cross-check, not as evidence of shared computation.

---

## Cheap decisive test

The Section 2 cell IS the cheap decisive test: CPU-local, reuses 4 already-landed mechanisms with one small new
glue layer (concept-id -> FHRR-stem hash, a curated ~10-30-row function-word table, and the decoder's existing
block-projection function reused against grammar's bs schedule) plus one genuinely new control arm
(`identity_scrambled`). No GPU, no new training, no new research questions -- purely a wiring/composition
verification of mechanisms that already independently HARD_PASS in isolation.

## Falsifiable predictions (HARD-PASS / HARD-FAIL, pre-registered -- see Section 2 for full bands)

Summarized: HARD-PASS requires `exact_ordered_slot_match >= 0.90` AND `identity_consistency >= 0.95` AND
`surface_string_exact_match >= 0.90` on >= 20 curated sentences, all 4 controls (3 reused, 1 new) collapsing.
HARD-FAIL is `exact_ordered_slot_match < 0.50` (undiagnosed NEW integration bug between 3 independently-proven
primitives) OR `identity_consistency < 0.50` (the symbolic bridge itself is broken) OR any control failing to
collapse. Over-claim guard (independent of numeric result): any framing as "the substrate composes/generates/
understands sentences" in a general sense is itself the failure condition -- honest scope is narrow chained
composition of a known proposition over a curated word set.

## Cross-thread synthesis

Directly extends, and does not redo, three same-day sibling notes: `notes/research_language_ingest_glassbox_scoping_2026-07-05.md`
(the 4-layer decomposition, the Layer C function-word/recursive-grammar gap this note's mismatch #5 reconfirms, the
dependency table establishing neither the HELD re-encode nor cortex-layer gates this work); `notes/research_substrate_native_language_path_5x_angle5_2026-07-05.md`
(the simpler grounded-fact-utterance cell this note's Section 2 cell is a MORE AMBITIOUS sibling to -- that cell
tests Lexicon+Syntax alone with citation-form words; THIS cell additionally exercises Morphology and Grammar's
recursion-capable template, closing the loop the angle5 note left open); `notes/research_5x_drill_generation_spec_and_brain_mechanism_2026-07-05.md`
(the 5-field convergence on position-as-bound-factor, reused not re-derived); `notes/exp_dev_handoff_research_language_ingest_glassbox_scoping_2026-07-05.md`
(ANCHOR_1/ANCHOR_2 -- this note's Section 2 cell is a natural THIRD anchor, sequenced after both land, since it
consumes the morphology-width-extension result -- already HARD_PASS per `data/exp_morph_ruleset_wug_v2_cpu/metrics.json`
-- and would consume ANCHOR_1's curation glue if built first). Direct filesystem verification this pass (not reused
from any prior note): `data/exp_morph_ruleset_wug_v2_cpu/metrics.json` (HARD_PASS, 8/8 rules >=0.90, dual_route=1.0),
`data/exp_grammar_recursive_function_word_blocklocal_v1_smoke/metrics.json` (SMOKE HARD_PASS, envelope 4/6 cells hold,
max_recursion_depth@V>=256=3), `data/exp_generation_decoder_gsbc_native_blocklocal_v1/metrics.json` (FULL HARD_PASS,
native==synth filler parity through D=12, graceful edge-degradation D=26), `experiments/exp_morph_ruleset_wug_v2_cpu.py`
(full read -- FHRR algebra confirmed), `experiments/exp_grammar_recursive_function_word_blocklocal_v1.py` (first 280
lines -- GSBC block-local algebra + synthetic-codebook confirmed).

## Substrate-product implications

1. **The 4-layer composition is NOT gated on any unsolved research question.** Every one of the 5 identified
   mismatches is either already-precedented glue or a small new deterministic function -- none requires inventing a
   new mechanism or resolving an open theoretical question. This should be messaged explicitly: "assembly is an
   engineering/wiring task now, not a research task."
2. **The representational split between Morphology (FHRR) and Syntax/Grammar/Lexicon (GSBC) should be KEPT, not
   "fixed" by forcing one shared algebra.** Three independent lines of evidence (VSA theory, psycholinguistics,
   existing NLG engineering precedent) converge on discrete-symbol bridging as the correct, standard pattern. Any
   future proposal to "unify" the algebras into one vector space should be treated with suspicion -- it would be
   solving a problem the literature says doesn't need solving, at the cost of the field's own still-unfinished
   cross-VSA-algebra formal theory (per the 2026 category-theory paper explicitly flagging this as open).
3. **The cell's real, novel discriminator is cross-layer identity consistency, not any individual layer's already-
   proven mechanism.** Framing and resourcing should center on the `identity_scrambled` control and the concept-id
   -> FHRR-stem hash bridge (mismatch #2) as the genuinely open empirical question -- everything else in the
   pipeline is composition of already-HARD_PASS pieces.
4. **Recursion (LEVELS=2) is deliberately deferred to a scoped follow-on, not because it is risky, but to avoid
   confounding two independent questions in one cell** (per Fix #28 discipline). This should not be read as recursion
   being in doubt -- the grammar cell's own LEVELS=2 anchor is already HARD_PASS in isolation.
5. **The honest claim ceiling for this cell, even at HARD-PASS, is narrow** ("chains a known proposition through 4
   glass-box primitives over a curated word set") and must not be allowed to drift toward "composes/generates/
   understands sentences" in any general-capability framing -- consistent with every one of the 4 component cells'
   own explicit framing fields (`"NARROW structured glass-box grammar-structure primitive"`, `"STRUCTURED morphology
   LAYER, not fluent language"`).

## Citations (verified count)

**Internal (primary, filesystem-verified this pass):** 3 metrics.json files (`exp_morph_ruleset_wug_v2_cpu`,
`exp_grammar_recursive_function_word_blocklocal_v1_smoke`, `exp_generation_decoder_gsbc_native_blocklocal_v1`) + 2
`.py` source files (`exp_morph_ruleset_wug_v2_cpu.py` full read, `exp_grammar_recursive_function_word_blocklocal_v1.py`
lines 1-280), listed in Cross-thread synthesis above.

**External (literature, 3 parallel Sonnet sub-agents, generic-query-only per query-privacy discipline, ~30 total
citations returned across the 3 sub-agents):**

**A. VSA/HDC hybrid-composition theory:** Plate, T. (1995), "Holographic Reduced Representations," *IEEE
Transactions on Neural Networks*; Kanerva, P. (1996/1997), Binary Spatter Codes; Smolensky, P. (1990), "Tensor
Product Variable Binding...," *Artificial Intelligence*; Smolensky et al. (2016), arXiv:1601.02745; Kleyko,
Rachkovskij, Osipov & Rahimi (2022), HDC/VSA survey Parts I+II, arXiv:2111.06077 / 2112.15424; Frady, Kent,
Olshausen & Sommer (2020), "Resonator Networks 1 & 2," *Neural Computation*; Karunaratne et al. (2023), *Nature
Nanotechnology*; Hersche, Terzić, Karunaratne et al. (2023/2025), "Factorizers for Distributed Sparse Block Codes";
Liu et al. (2025), "Linearithmic Clean-up..."; "Developing a Foundation of Vector Symbolic Architectures Using
Category Theory" (2026, arXiv:2501.05368); "Cross-Layer Design of Vector-Symbolic Computing..." (2026,
arXiv:2508.14245).

**B. Levelt/Garrett/Dell production-stage representational format:** Levelt, W.J.M. (1989), *Speaking: From
Intention to Articulation*, MIT Press; Garrett, M.F. (1975, 1980, 1988) production-stage/speech-error papers;
Kempen & Huijbers (1983), *Cognition* 14; Roelofs, Meyer & Levelt (1998), *Cognition* 69; Levelt, Roelofs & Meyer
(1999), *Behavioral and Brain Sciences* 22; Caramazza & Miozzo (1997), *Cognition* 64; Miozzo & Caramazza (1997),
*J. Cognitive Neuropsychology* 9; Dell, G.S. (1986), *Psychological Review* 93; Stemberger, J. (1985); Van
Turennout, Hagoort & Brown (1998), *Science* 280; Indefrey & Levelt (2004), *Cognition* 92.

**C. Function-word gating + center-embedding depth limits:** Frazier & Rayner (1982); Ferreira & Henderson (1990);
Trueswell, Tanenhaus & Kello (1993); Neville et al. (1992); Chomsky (1986, *Barriers*; 2000/2001 phase papers);
Steedman (2000), *The Syntactic Process*; Miller & Chomsky (1963), *Handbook of Mathematical Psychology*; Miller &
Isard (1964), *Information and Control*; Karlsson (2007); Lewis (1996), *J. Psycholinguistic Research*; Lewis &
Vasishth (2005), *Cognitive Science*; Gibson (1998), *Cognition*.

**P_deflated (headline):** P(this cell HARD-PASSes, including the never-before-tested `identity_consistency` metric)
= **0.40** (pre-penalty ~0.55-0.65 given every individual component's independent maturity; deflated per the
mandatory lit-scan/novel-composition calibration discipline since the specific cross-layer bridge, while
well-precedented in theory, has never been run in this repo). P(MIDDLE) ~= 0.40. P(HARD-FAIL) ~= 0.20.
