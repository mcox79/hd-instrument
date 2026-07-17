# Pre-reg: exp_read_grow_oov_verb_extension_v1 (RUNG 3 -- OOV VERBS, closed-verb shield lifted)

Cell: `experiments/exp_read_grow_oov_verb_extension_v1.py`
Trigger: RUNG 2's landed-VET (skunkworks a3dd86bc) CP->capability expansion criterion (verbatim): "re-run this
same discriminator design (coverage_gain / precision_newly_covered / guard / oos / floor bands) on a corpus
where VERBS are also OOV (lifting the current closed-verb shield) -- that is the exact condition under which
the tagger mistag mode I found (eat->NN) becomes architecturally live rather than shielded." The VET ALSO
flagged that RUNG 2's morphology/word-shape fallback was DEAD CODE on RUNG 2's corpus (0/156 promotions used
it) -- this cell is designed so verb morphology (-ing/-ed/-s) is genuinely exercised.

Question: with the closed-verb shield lifted (verbs may now be OOV to the closed lexicon, so the tagger's
verb-tagging is load-bearing), does the classical-POS-tagger extension still recover substantial coverage,
and what happens to precision -- does the mistag mode measurably cost precision, coverage, or neither? NO
LLM, NO neural component anywhere.

## Prior-work check (substrate-KB concept-query, per USER-locked discipline)
`bash tools/substrate_query.sh "classical POS tagger OOV verb inflection morphology open text glass-box
extraction verb tag mistag"` -- confidence=0.3008. Top hit: entity='inflectional_morphology' (cosine=0.3008,
source_class=wordnet -- a generic WordNet lexical-concept entry, NOT a prior arc EXPERIMENT CELL); next:
'inflectional morphology' (atoms, cosine=0.3008, same generic concept); 'class action'/'class_action'
(cosine=0.2842, unrelated); 'the inflection of verbs' (cosine=0.2705, wordnet). Verdict: no prior CELL at
cosine>0.30 (the two >=0.30 hits are a generic linguistics dictionary term, not a prior experiment) --
genuinely novel cell design, not a rediscovery.

## Pieces composed (3-layer reuse, with provenance)
- Closed-schema parser + lexicon: `exp_read_grow_foundation_realprose_glassbox_ie_v2.py` -- `ie_extract`,
  `_tag_token`, `_tokenize`, `_resolve_relation`, `_split_coord`, `VERB_LEX`, `ADJS`, `ENTITIES`, `RELATIONS`,
  `ANIMALS`, `FOODS`, `PLACES` -- IMPORTED verbatim, UNMODIFIED.
- RUNG 2 (`exp_read_grow_oov_pos_extension_v1.py`) -- `_extract_core` (imported DIRECTLY, not re-implemented
  a third time; RUNG 2 already parity-proved it against v2's `ie_extract` at its own self-test, so this cell
  inherits that proof by reusing the identical function object -- zero re-implementation-drift risk),
  `_tokenize_cased`, `_morph_noun_shape`, `_oov_lemma`, `NLTK_NOUN_TAGS`, `NLTK_VERB_TAGS`, RUNG 2's OOV noun
  pools (`OOV_ANIMALS`/`OOV_FOODS`/`OOV_PLACES`), and RUNG 2's own `ie_extract_pos_extended` (used as an
  incrementality control, see Result section).
- Classical POS tagger: `nltk.pos_tag` (`averaged_perceptron_tagger_eng`), same as v2/RUNG 2.
- NEW (this cell): `OOV_VERB_BASE_LEX` (9 real-English synonym verbs for the 3 known relations, PRE-DECLARED
  not runtime-invented, disjoint from `VERB_LEX`), `_oov_verb_base_and_form` (morphological suffix-stripper:
  -ing/-ed/-s/-es with silent-e restoration), `_classify_unk_token` (combined noun+verb UNK-promotion
  decision, verb-morph deferring to the tagger's NOUN-family judgment -- mirror-image of RUNG 2's noun-morph
  deferring to the tagger's VERB-family judgment), `_build_tags_verb_extended`, the 12-template corpus
  generator, `MIXED_OOV_DIAGNOSTIC` (secondary, non-gating).

## Design (arms)
- **CURRENT**: `ie_extract` unchanged. Every primary-corpus verb is OOV to the closed `VERB_LEX` -> expected
  full abstain (`NO_VERB`).
- **POS_EXTENDED**: identical grammar (`_extract_core`, imported); a token the closed lexicon tags UNK gets a
  second chance -- VERB path fires if the tagger says VB-family OR (verb-morphology recognizes the base AND
  the tagger does not say NOUN-family); NOUN path (RUNG 2's mechanism, reused) otherwise. A tagger-confirmed
  VERB whose base is NOT in `OOV_VERB_BASE_LEX` still tags VERB with an unresolved lemma -- `_resolve_relation`
  (imported, unmodified) correctly returns None, so the sentence honestly abstains (no relation invented).

## MEASURED pre-design tagger probe (standalone offline `nltk.pos_tag()` run, not hypothesized)
Confirmed the VET's flagged mistag mode is real, reproducible, and VERB-SPECIFIC (not a uniform rule):
- `"Rabbits eat berries."` -> eat/**NN** (direct reproduction of the VET's finding, for reference; "eat" is
  NOT used in this cell's corpus since it is a closed verb).
- Bare-plural-no-determiner frame, this cell's 9 synonym verbs: munch/pursue/hunt -> **NN** (mistagged,
  noun-family, NOT rescued by design -- defers to the tagger's noun judgment); nibble/gobble -> **JJ**
  (mistagged, adjective, NEITHER noun- nor verb-family -- morphology DOES rescue these, since the fallback
  only defers to NOUN-family tags); devour/dwell/stalk/reside -> **VBP** (tagged correctly even bare-plural).
- 3sg+determiner frame ("The X verbs the Y."): all 9 verbs tag correctly (VBZ) in the combinations probed,
  with one noted exception ("The bird resides in the tree." -> resides/NNS, a noun-content-sensitive mistag
  even WITH a determiner) -- confirms tagger behavior is lexically/contextually conditioned, not purely
  frame-based; the FULL corpus draws nouns from the complete closed pools rather than cherry-picked "safe"
  combinations, so this class of surprise is left free to occur and is reported in the measured numbers.

## Corpus (hand-authored; NOT engineered to dodge the mistag mode, per contract)
PRIMARY: 12 template classes (3sg+determiner / bare-plural-no-determiner / passive / past-active /
gerund-progressive / adjective-modified, crossed with the eats/chases/lives_in relation families where the
frame is grammatical) x `N_PER_TEMPLATE=4` draws x 3 seeds = 144 sentences. Nouns held CLOSED (full ANIMALS/
FOODS/PLACES pools, imported from v2) -- isolates the OOV-VERB axis, mirroring RUNG 2's own noun-axis
isolation. Bare-plural frames deliberately INCLUDED (not avoided) since that is the exact context the tagger
probe showed the mistag fires in -- the decisive test the VET asked for. A bare-plural-safe animal subset
(`ANIMALS_BARE_SAFE`) excludes "fish" (invariant plural) and "mouse" (irregular "mice") -- a proactive
avoidance of a known irregular-plural corpus-GENERATION trap (same class RUNG 2 caught for "moss"->"mosss"),
NOT a mistag-mode dodge (the risky VERBS themselves are never filtered).

SECONDARY (non-gating diagnostic): `MIXED_OOV_DIAGNOSTIC` -- 6 hand-authored sentences combining an OOV noun
(RUNG 2's pools) AND an OOV verb, including one bare-plural both-OOV case, per contract's explicit invitation.

GUARD_SENTENCES (fully closed, regression check) and OUT_OF_SCHEMA_CONTROL (a verb genuinely absent from BOTH
`VERB_LEX` and `OOV_VERB_BASE_LEX`, e.g. "sleeps"/"yawns" -- BOTH arms must abstain, proving the extension
does not hallucinate a relation for a truly unmapped verb).

## Bands (pre-committed; envelope-adjusted per contract's honest expectation)
- **HARD-PASS:** `coverage_gain_pp_pooled >= 15.0` AND `precision_newly_covered_pooled >= 0.60` (precision-
  favoring per the corrected classical open-text envelope, NOT RUNG 2's 0.90 ceiling-precision bar -- a live
  mistag mode may cost precision, and 0.60 is the honest floor for "still informative") AND
  `guard_regression_ok` AND `oos_control_fired` AND `current_coverage_floor_ok`.
- **HARD-FAIL:** `coverage_gain_pp_pooled < 5.0` OR `precision_newly_covered_pooled < 0.50` (collapse below
  the classical floor).
- **MIDDLE_BAND:** otherwise, including zero newly-covered sentences.
- HONEST FRAMING: unlike RUNG 2's 100pp/1.000, this cell does NOT expect a ceiling result -- the tagger
  mistag mode is architecturally live by design. Whatever precision/coverage land at is reported as-measured.

## Schema-vet fields
- compute_architecture: sequential-CPU (pure syntactic parsing; wall time MEASURED 0.11s smoke / 0.12s FULL).
- storage_strategy: no_storage (pure parser-layer test).
- final_metrics_atomicity: tmp_replace. progress_logging: print_flush_true (not required at this wall time).
  deterministic_seeding: true (fixed int seeds [7,13,19] via `random.Random(seed)`; `sorted()` everywhere;
  no `hash()`/`list(set(...))`).
- start_marker + crash_diagnostic present (tmp+os.replace atomic write pattern).
- real_code_path (F.1): self_test calls the REAL `nltk.pos_tag`, the REAL imported `ie_extract`, and the REAL
  imported `_extract_core` (inherited parity proof from RUNG 2, not re-derived); runs the full `run_seed` loop
  at tiny scale; additionally asserts the MEASURED tagger-probe mistag/rescue findings reproduce live (not
  just hoped for) and that the architectural no-wrong-triple safety property holds.
- crlb_n/a: no quantitative noise floor -- discrete syntactic role-assignment + the classical tagger's own
  literature-benchmarked accuracy on this corpus's specific verb tokens (MEASURED via standalone probe).
- baseline_in_band: N/A BY DESIGN (declared, matches RUNG 2's own exemption) -- CURRENT-at-floor IS the
  required vacuous-test guard (`current_coverage_floor_ok`), not a measurability failure.
- discriminator-fires: verified at self-test AND smoke -- CURRENT coverage = 0.0 on the primary corpus,
  POS_EXTENDED coverage > 0 (MEASURED 0.875 smoke, 0.882 FULL).
- arms_differ (META_RULE_AF): CURRENT vs POS_EXTENDED accepted-triple-set SHA256 hashes verified to differ at
  self-test (CURRENT empty, EXTENDED non-empty on the tiny OOV-verb corpus).
- glass_box_legal: static regex source-scan confirms no `torch`/`spacy`/`transformers`/`stanza` import in this
  file's source; `nltk`'s `averaged_perceptron_tagger_eng` is classical, non-neural (explicit LEGAL per the
  research note).
- incrementality control: RUNG 2's own `ie_extract_pos_extended` (noun-OOV only, untouched by this cell)
  MEASURED to cover 0.0 of this corpus (asserted at self-test) -- proves the verb-OOV capability is genuinely
  new, not accidentally already solved by RUNG 2's mechanism.

## Dispatch
Wall time trivial (0.11-0.12s) -- COMPUTE-PROPORTIONALITY: self-test, smoke, and FULL all run
INLINE/FOREGROUND locally, matching RUNG 2's own precedent. No queue_add.sh / remote SCP / atomize. Pause
flag `data/orchestrator_paused.flag` re-checked absent immediately before both the smoke and FULL runs
(absent both times).

## Result (MEASURED @ data/exp_read_grow_oov_verb_extension_v1/metrics.json, seeds=[7,13,19], run_mode=full)
HARD_PASS (claim, VET-pending). `coverage_gain_pp_pooled=88.2` (CURRENT coverage=0.000, POS_EXTENDED
coverage=0.882, pooled over 144 sentences across 3 seeds -- consistent per-seed: 87.5/87.5/89.6pp);
`precision_newly_covered_pooled=1.000` (127/127 newly-covered sentences, ALL extracted triples exactly
matched gold -- ZERO wrong triples emitted anywhere on the primary corpus, asserted at self-test as an
architectural safety property and reconfirmed at FULL); `guard_regression_ok=True`; `oos_control_fired=True`;
`current_coverage_floor_ok=True` (CURRENT coverage exactly 0.000, as expected since every primary-corpus
sentence's verb is OOV to the closed lexicon by construction).

KEY FINDING (the honest decisive-test answer to the VET's ask): the tagger mistag mode IS architecturally
live and DOES cost something real -- 17/144 sentences (11.8%) have their verb mistagged by the classical
tagger in a way this extension does not correct (`verb_mistagged_uncorrected_pooled=17`, concentrated in the
bare-plural-no-determiner frame for the "munch"/"pursue"/"hunt" family). BUT the cost lands entirely as a
COVERAGE loss (a clean, honest `NO_VERB` abstain), NOT a precision loss -- this is a STRUCTURAL property of
the shared `_extract_core` grammar engine (imported unmodified from RUNG 2/v2): `verb_idx` is checked and the
function returns immediately if empty, BEFORE any subject/object noun collection runs, so a verb-token
mistagged to NOUN can never leak into a role slot and produce a wrong triple in a single-clause sentence --
it can only cause the whole sentence to abstain. This is a different, more mechanistically precise finding
than "precision drops" (the naive prior framing in the dispatching contract) -- it precisely localizes WHERE
the closed-verb shield was doing its protective work: RUNG 2's shield (never letting the tagger see a verb
token at all) protected COVERAGE from this specific mistag mode, not precision. Precision's protection turns
out to come from the parser's own control-flow structure (verb-idx-first, immediate-return), which survives
the shield's removal intact.

`verb_morph_rescue_pooled=7`: verb morphology (previously DEAD CODE on RUNG 2's corpus per the VET's finding)
IS genuinely exercised and DOES rescue some mistags -- specifically the JJ-tagged "nibble"/"gobble" cases,
where the tagger's mistag lands OUTSIDE the noun-family tag set the fallback defers to, so morphological
suffix-stripping (verified to correctly invert all 9 verb bases x 4 inflections at self-test) recovers the
correct VERB promotion despite the tagger's error. `verb_tagger_and_morph_pooled=120`: the large majority of
promotions have BOTH signals agreeing (the common, non-mistagged case). `verb_unresolved_pooled=0`: no
tagger-confirmed-verb-but-unmapped-lemma cases occurred in the PRIMARY corpus (by construction, all 9 verb
surface forms map to a known relation) -- the OUT_OF_SCHEMA_CONTROL sentences (evaluated separately, not
pooled into this corpus) exercise that path and correctly abstain in both arms.

`rung2_coverage_on_this_corpus_pooled=0.0` (incrementality control, MEASURED): RUNG 2's own noun-OOV
mechanism does not cover ANY sentence in this verb-OOV corpus, confirming the verb-extension capability is
genuinely new, not an accidental overlap with RUNG 2's existing mechanism.

MIXED_OOV_DIAGNOSTIC (non-gating): all 6 combined noun+verb-OOV sentences, including the bare-plural
both-OOV case ("Rabbits munch carrots."), extracted correctly. Notably, "munch" did NOT mistag in the
OOV-subject ("Rabbits") context the way it mistagged with the closed-lexicon subject ("Cats") in the primary
corpus's bare-plural template -- a genuinely interesting, unplanned, MEASURED finding that the specific lexical
identity of the SUBJECT noun also influences the tagger's verb-tagging decision, not just the frame. Reported
honestly as an observation, not incorporated into the gating bands (the diagnostic corpus is too small, n=6,
for a reliable rate estimate).

HONEST CAVEAT (not a HARD-PASS overclaim): this cell's PRIMARY corpus still isolates the verb-OOV axis with
nouns held closed -- a fully open register (OOV nouns AND verbs AND ambiguous function words together, real
prose) would compound these effects and likely land closer to the corrected classical envelope's lower
coverage/precision range (P:60-85%/R:30-55%). The 88.2pp coverage gain / 1.000 precision reflects a
controlled, single-variable-at-a-time test design, exactly as RUNG 2's did for nouns -- this is rung 3 of a
curriculum, not the final open-text number.
