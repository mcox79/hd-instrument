# Pre-reg: does the OWNED learned encoder (proper interface) cross the deep SAME-IDEA wall?

Date: 2026-08-11
Task: standalone diagnostic (director spawn), NOT a wiring cell. Grounding shore-up (commit
584a69eb5) precisely located the deep grounding wall: raw Lancaster sensorimotor + Brysbaert
concreteness norms are TOO COARSE for SAME-IDEA discrimination -- apple/orange (raw cosine 0.952)
is statistically inseparable from happy/joyful (0.962); the wire-in had to CAP itself
(GROUNDED_CAP=0.45) to relatedness-only, sacrificing same-idea/sibling discrimination entirely.
The OTHER candidate asset for that wall -- `scale_win_tinytransformer_encoder`
(capability_registry.jsonl gate=WIRE, "beats grounding +0.050 semantic/+0.071 relational" on ITS
OWN held-out-concept task) -- was tested UNFAIRLY in the grounding pre-reg's "Learned-encoder
diagnostic" section: it was probed via `TinyTransformer.pooled()` on a BARE 1-2-token embedding
(disk-verified MEASURED result: trash/garbage 0.490 < stone/idea 0.548 -- worse than sensorimotor),
when the encoder was actually TRAINED AND EVALUATED via `encode_concept_text_reps` -- pooling over
many REAL CORPUS MENTIONS of a concept (postings), never a bare-token probe. This cell gives it that
fair shot, standalone (does not touch the live grounding wiring).

Prior-work check (`bash tools/substrate_query.sh "learned encoder synonym sibling discrimination
corpus mention pooling deep same-idea wall"`): top hit cosine=0.3486 (DISCRIMINATING_FRACTION
PREDICTION, a per-encoder metric-prediction note from a DIFFERENT encoder-family sweep prereg,
2026-06-28 -- not the same test). Item 4, cosine=0.2998 (below the 0.30 rediscovery threshold but
worth reading): a MEASURED_MECHANISM synthesis atom
(`MM_TENTATIVE_SYNTHESIS_..._char_trigram_infoNCE_learned_encoder_representation_DOES_NOT_SEPARATE_
semantically_relationally_similar_items...`, 2026-07-09) found a DIFFERENT learned encoder family
(char-trigram + InfoNCE, the seqbind/reader-side encoder, NOT this from-scratch MLM+relobj
TinyTransformer) also failing to separate same-relation SIBLINGS from targets ("hop-2 errors 81.5%
same-relation, +0.324 excess"). This is genuinely a DIFFERENT encoder, DIFFERENT training objective,
DIFFERENT task (relational hop-error, not synonym/sibling lexical discrimination) -- NOT a
rediscovery of this specific test -- but it is directionally relevant prior signal that
sibling-collision is a recurring learned-encoder pathology across this project's encoder families,
worth naming honestly in the verdict regardless of outcome.

Cited prior numbers for THIS checkpoint's own eval (data/exp_scale_meaning_learn_arc_heldout_v3_
relobj/metrics.json, HARD_FAIL_ARCHITECTURE_BOUND verdict, seed 7/13): via the SAME
`encode_concept_text_reps` interface on ITS OWN held-out-NEW concept universe, OBJ relational-AUC =
[0.619, 0.638], OBJ semantic-AUC (same-WordNet-lexname) = [0.598, 0.596] -- both meaningfully above
chance (0.5) but the v3 "joint relational objective" experiment itself HARD_FAILED to beat the v2
MLM-only baseline. This cell asks a DIFFERENT, narrower question on a DIFFERENT pair construction
(synonym-vs-sibling at the specific point where the grounding norms provably fail), not a rerun of
that verdict.

## What this cell measures (standalone diagnostic; NOT wired into any live path)

1. Load `data/exp_scale_meaning_learn_arc_heldout_v3_relobj/ckpt_seed_7.pt` (TinyTransformer,
   d_model=512/layers=6/heads=8, vocab=16000, FULL run, glass-box/local/CPU/no external LLM).
2. SIBLING set: the exact 19 sibling-distinct trap pairs from
   `data/exp_grounded_meaning_wire_lexical_fallback_v1/metrics.json` (`T3_anti_over_merge.
   trap_results`), hardcoded, cross-checked at self-test/smoke/full time by re-deriving them via
   the peer cell's own `build_sibling_trap_pairs()` (imported read-only from
   `experiments/exp_grounded_meaning_wire_lexical_fallback_v1.py`) against live WordNet + the SAME
   eligibility gate (`_eligible`: OOV of `hdlab.lexical_similarity.CONCEPT_FEATURES`, IN
   `hdlab.grounded_similarity`'s Lancaster/Brysbaert lexicon) -- asserted BYTE-IDENTICAL to the
   hardcoded list (proves faithful reuse, not a mistyped copy).
3. SYNONYM set: 19 pairs freshly authored for this cell, same-WordNet-noun-synset word pairs
   (true near-synonyms by construction), built by the SAME deterministic `sorted(synsets) ->
   sorted(lemmas) -> first-two-eligible` scan as the peer cell's own `build_synonym_pairs`, reusing
   the identical `_eligible` gate (held out from the hand lexicon + present in the grounded
   lexicon, so the grounding baseline has 100% coverage on literally the same pairs -- true
   apples-to-apples three-way comparison). Sibling-set words are excluded from the synonym-candidate
   pool (no cross-set word reuse). Candidate pool over-provisioned to 60 pairs; final 19 are the
   first (deterministic order) whose BOTH words clear the corpus-mention coverage floor (below).
4. Postings (real corpus-mention sentences) for the union of sibling-set + synonym-candidate-set
   words are collected via a SINGLE bounded pass over `data/corpora/arc/ARC-V1-Feb2018-2/
   ARC_Corpus.txt`, reusing the training cell's OWN `_WORD_RE` (lowercase alpha tokenization),
   `_quality_ok` (length/digit-ratio/citation-fragment filter) and `_line_hash` (dedup) -- so the
   text fed to the encoder is preprocessed identically to how the encoder was trained/evaluated.
   CALIBRATION PROBE (repo scratch, 2026-08-11, MEASURED): a full single pass over all 14,621,856
   lines took 97.1s; EVERY one of the 19 sibling words had >=88 mentions (median 2283); EVERY one
   of 60 synonym candidates had >=19 mentions (median 1613) -- coverage is not the bottleneck; the
   corpus-scan wall-time (~100s) and the encoder forward pass (~47s per 2500 pooled windows on CPU,
   MEASURED) are the two real costs, both cheap.
5. `encode_concept_text_reps(model, tok, postings, cfg, device, spec)` -- imported DIRECTLY (not
   reimplemented) from `experiments/exp_scale_meaning_learn_arc_heldout_v3_relobj.py` -- pools the
   trained encoder's contextual reps over each word's mention windows, mean-pooled + L2-normed.
   This IS the encoder's proper, trained/evaluated interface; zero invocation-mismatch risk since
   the function object is imported, not re-derived.
6. Encoder cosine per pair = dot of the two L2-normed pooled reps. Grounding cosine per pair = raw
   (uncapped) cosine over `hdlab.grounded_similarity.grounded_vector()`'s 12-dim z-scored profile
   (NOT the capped public `grounded_similarity()` -- the cap would flatten the exact effect this
   cell measures; RAW matches the grounding pre-reg's own calibration-table convention).
7. Discriminator: tie-corrected Mann-Whitney AUC (`_auc_from_scores`, imported from the SAME
   training-cell module) treating SYNONYM-pair scores as the positive class and SIBLING-pair
   scores as the negative class (AUC = P(random synonym score > random sibling score); chance =
   0.5 exactly). d-prime = (mean_syn - mean_sib) / sqrt(0.5*(var_syn+var_sib)), sample variance.
   Computed independently for: TRAINED ENCODER (the test), GROUNDING (raw, matched pairs, the
   head-to-head baseline), SCRAMBLE control, RANDOM-INIT control (bonus).

## Positive control (Gate-D-style; the ONE primitive this cell partially reimplements)

`encode_concept_text_reps` / `TinyTransformer` are imported directly (zero reimplementation --
SHAPE_MATCH by construction). The grounding RAW-cosine formula IS reimplemented locally (dot/norm
matching `hdlab.grounded_similarity`'s internal `_raw_cos`, using only the PUBLIC `grounded_vector`
API). Positive control: recompute raw cosine for `("apple","orange")` and `("happy","joyful")` (the
grounding pre-reg's own cited calibration pairs) and assert within 0.005 of the pre-reg's MEASURED
values (0.952, 0.962 respectively) -- proves this cell's grounding-baseline reimplementation is
faithful before trusting the head-to-head comparison. `positive_control_arms.tolerance = 0.005`,
`if_outside_tolerance: HARD_FAIL_GROUNDING_REIMPL_MISMATCH` (would invalidate the grounding-baseline
side of the head-to-head; encoder numbers stand independently regardless).

## Envelope / fail-bands (per-metric; NONE force-fit to a preferred outcome)

Power floor (BOTH required for any verdict other than MIDDLE_BAND/underpowered):
`n_synonym_used >= 12` AND `n_sibling_used >= 12` (out of the 19+19 targeted; a pair is dropped
only if either word fails the corpus-mention coverage floor, `min_mentions >= 10` at FULL scale --
MEASURED calibration above shows this should not bind, but the gate is real, not decorative).

**HARD_PASS** (crossing the wall via LEARNING -- ALL required):
1. `encoder_AUC >= 0.65` (materially, not marginally, above chance -- stronger than the generic
   META_RULE_L "5% of band width above floor" convention; the task asks for a REAL margin).
2. `encoder_d_prime > 0` (directionally consistent with 1).
3. Head-to-head beats grounding: `grounding_AUC_matched` (same pairs) sits in the near-chance band
   `[0.40, 0.60]` (reproduces the sensorimotor-norms' "~0 separation" finding quantitatively on
   THIS matched pair set) OR, if grounding is NOT near chance for some reason, `encoder_AUC -
   grounding_AUC >= 0.15` (decisive margin regardless).
4. `scramble_AUC` (rep-identity permutation control, fixed seed) collapses into `[0.40, 0.60]` --
   proves gate 1 is a genuine per-word representation effect, not a permutation-invariant artifact
   of the pair-scoring machinery.
5. LEARNING-ISOLATION (added post-smoke, layered-self-correcting-controls discipline): `encoder_AUC
   - randinit_AUC >= 0.05` -- the TRAINED encoder must beat the UNTRAINED random-init same-arch
   encoder (which uses the SAME corpus-mention-pooling interface). If a random-init transformer
   separates synonym from sibling equally/better, the separation is a property of the pooling
   INTERFACE, not of what the encoder LEARNED, and the "learned encoder crosses the wall" claim is
   NOT earned. (This gate was NOT in the original envelope; it was added because the smoke's
   random-init BONUS control unexpectedly EXCEEDED the trained encoder -- a control reproducing the
   win from the wrong source. Honest science demotes the mechanism claim; see verdicts below.)
6. `arms_differ_verified` True (trained-encoder reps / scrambled reps / random-init reps are
   pairwise hash-distinct -- META_RULE_AF).
7. Positive control (apple/orange, happy/joyful raw-cosine replication) holds within tolerance.

**MIDDLE_BAND_INTERFACE_SEPARATES_BUT_NOT_LEARNING** (added post-smoke): gates 1-4 + 6-7 hold but
gate 5 (learning-isolation) FAILS -- the corpus-mention-pooling INTERFACE separates synonym from
sibling where the sensorimotor norms could not, but an untrained same-arch encoder does so equally
or better, so the win is attributable to distributional-context pooling (an owned glass-box asset
the encoder architecture provides), NOT to the learned representation. The wall is crossed by the
INTERFACE, not by learning. A concreteness-confound field (Brysbaert-concreteness z gap between the
synonym and sibling probe sets) is logged alongside so a reader can judge how much of the raw AUC
could be an abstract-vs-concrete distributional artifact rather than same-idea-vs-same-category.

**HARD_FAIL** (wall NOT crossable via this asset, at least not through this interface):
Power floor met AND `encoder_AUC <= 0.56` (at/near chance -- the SAME numeric failure class the
sensorimotor norms showed; matches this project's own `COLLAPSE_BAND`-style near-chance convention
used elsewhere in this codebase).

**MIDDLE_BAND** (everything else -- honest partial/ambiguous result, named not forced):
`0.56 < encoder_AUC < 0.65` (real but sub-decisive separation), OR gate 3/4 fails while gate 1
holds (encoder shows *some* separation but the control/head-to-head doesn't cleanly support
attributing it to genuine learned same-idea structure), OR underpowered (`n_used < 12` in either
class), OR positive control fails (grounding-baseline reimplementation is suspect -- encoder number
can still be reported, but the head-to-head framing is downgraded).

## Compute architecture

(b) sequential-CPU with justification: this is a one-shot inference diagnostic (frozen checkpoint,
`torch.no_grad()`), not a training run. MEASURED wall-time budget: corpus scan ~97s (single pass,
whole 14.6M-line file) + encoder forward pass ~47s per ~2500 pooled windows (trained) + ~47s again
(random-init control, same postings) + grounding CSV parse ~5s (lazy-loaded, cached) + WordNet
candidate construction ~3s. Total estimated <4 min, comfortably inside a single foreground Bash
call with `timeout: 600000` (10 min) per the INLINE-LOCAL mandate (no queue/remote authorized for
this task). No GPU-batching candidate exists worth the setup cost at this N (~76 words, one pass).

Storage strategy: no_storage / no_composition -- reads two static assets (checkpoint .pt,
grounding CSVs) + one corpus text file; writes one metrics.json; no persisted multi-item store, no
downstream composition/chaining.

## Metadata (CELL-TEMPLATE MANDATORY fields)

cell_name: diag_learned_encoder_synonym_sibling_deep_wall_v1
cell_chunked: false (single-shot, not multi-seed/multi-unit resumable)
final_metrics_atomicity: tmp_replace (single-shot, `os.replace`)
progress_logging: n/a (`elapsed_s` expected <300s, well under the 1800s Section-17 trigger); prints
use `flush=True` regardless as defense-in-depth.
deterministic_seeding: true (fixed int seeds throughout -- 20260811 for the scramble permutation,
20260812 for random-init model weights; `sorted()`/`sorted(set())` discipline for all WordNet
enumeration and word-list construction; no built-in `hash()`; PROT-023/F.5 compliant).
arms_differ_verified: computed at FULL run (see gate 5 above); declared `arms_differ_exempted: []`
(no legitimately-identical arms expected).
crlb_n/a: "AUC discriminator base=0.5 exactly (Mann-Whitney definition); no Gaussian noise-floor
formula applies to a lexical-similarity discrimination task; scramble + random-init controls
witness the empirical floor directly."
baseline_in_band: n/a in the METdRULE_AG sense (no accuracy-metric baseline arm to saturate-check);
the closest analogue is gate 3/4 above (grounding + scramble near-chance witness), which IS
checked.
calibration_check: default_ok_for_this_regime (MIN_MENTIONS=10 / CAP_MENTIONS=24 at FULL scale are
principled from the MEASURED coverage probe above, not tuned toward a preferred verdict; logged).
cardinality_ok: EXPECTED_N_UNITS = 2 (SIBLING set, SYNONYM set) x 3 (TRAINED / SCRAMBLE / RANDOM_INIT
arms) = 6 cosine-score vectors + 1 GROUNDING arm (2 sets) = 8 total; counted + logged, not merely
asserted.
substrate_signature_checked: `TinyTransformer.__init__` (kwargs bound against the checkpoint's own
saved `model_cfg`, not hand-typed), `encode_concept_text_reps(model, tok, postings, cfg, device,
spec)`, `grounded_vector(word)`.
real_code_path_exercised: self-test constructs the REAL checkpoint + REAL ARC-corpus scan (bounded,
tiny) + REAL `encode_concept_text_reps` call, not a synthetic-only branch.
guard_baseline_validated: n/a (no control-beats-baseline break-guard in this cell; POP-style floor
guard does not apply to a fixed-checkpoint inference diagnostic).

## Smoke vs Full

Self-test (`--self-test`): loads the REAL checkpoint; bounded ARC-corpus scan of 1,000,000 lines
(MEASURED ~7-10s); 2 sibling pairs (`acorn/berry`, `gourd/hip`) + 2 synonym pairs (first 2 from a
6-pair candidate pool); `min_mentions=1`; asserts NO crash, correct shapes, arms differ, checkpoint/
tokenizer load correctly -- does NOT assert the HARD_PASS/HARD_FAIL science verdict (too few pairs
for a meaningful AUC; this stage is real-code-path proof, not the decisive measurement).

Smoke (`--smoke`): 3,000,000-line bounded scan (fast dev-iteration), all 19 sibling pairs, 19-of-40
synonym candidates, `min_mentions=3`, `cap_mentions=12`. Proves the FULL pipeline produces a
non-degenerate AUC/d-prime before committing to the full 14.6M-line scan.

Full (default, no flag): whole-corpus scan (14,621,856 lines, MEASURED ~97s), all 19 sibling pairs,
19-of-60 synonym candidates, `min_mentions=10`, `cap_mentions=24`, `encode_batch=128`. This produces
THE decisive number.

## Hard invariants

STANDALONE diagnostic only -- does NOT modify `hdlab/lexical_similarity.py`,
`hdlab/grounded_similarity.py`, or `data/capability_registry.jsonl` (a confirmed concurrent session
holds those). Does not touch any pre-existing uncommitted `hdlab/` files. Glass-box (owned
from-scratch checkpoint, no external LLM call anywhere). Deterministic. Runs LOCAL, inline,
foreground only -- no queue_add, no remote, no push. ASCII-only.
