# Pre-reg: does the distributional-pooling same-idea/same-category signal survive with concreteness balanced AND on a low-exposure held-out slice?

Date: 2026-08-11
Task: standalone diagnostic (director spawn), NOT a wiring cell. Follow-up to
`f6c6c843e` (`diag_learned_encoder_synonym_sibling_deep_wall_v1`, MIDDLE_BAND_INTERFACE_
SEPARATES_BUT_NOT_LEARNING): that cell found the corpus-mention distributional-pooling
INTERFACE (TinyTransformer.pooled() over real corpus mentions, `encode_concept_text_reps`)
separates synonym pairs from sibling pairs at AUC=0.7064 (trained) / 0.7452 (random-init,
same interface, untrained) -- far above sensorimotor-norm grounding (0.3186, below chance)
-- but flagged TWO confounds that block the claim: (a) the sibling probe set is +1.60
Brysbaert-concreteness-z MORE concrete than the synonym set (the AUC may reflect an
abstract-vs-concrete axis, not same-idea-vs-same-category); (b) every probe word had >=10-24
corpus mentions in the scan, i.e. very likely inside MLM training exposure, not held out.
This cell runs the DECISIVE clean test: build a pair set where BOTH confounds are removed
by construction, and see whether the separation survives.

## Prior-work check (SUBSTRATE-KB CONCEPT-QUERY, mandatory before authoring)

`bash tools/substrate_query.sh "concreteness balanced synonym sibling held-out distributional
pooling same-idea"` -- top hit cosine=0.2881 (a grounding-rung2 design note recommending
adding a SECOND psycholinguistic norm (valence/arousal) to confirm grounding isn't
concreteness-specific -- a different, though thematically adjacent, idea; not the same test).
All 5 returned hits are below the cosine>0.30 rediscovery threshold. Verdict: **genuinely
novel** -- no prior cell has built a concreteness-matched + exposure-restricted synonym/
sibling probe set. Not a rediscovery.

## Root-cause of the confound (why a NEW pair-construction method is required, not just a filter)

Re-reading `f6c6c843e`'s own construction code: the SIBLING pool was drawn from 9
HAND-PICKED, all-CONCRETE WordNet categories (fruit/vehicle/furniture/metal/fuel/hand_tool/
bird/beverage/vegetable). The SYNONYM pool was drawn by enumerating `wn.all_synsets(pos=NOUN)`
and taking the FIRST 19-60 eligible same-synset pairs in enumeration order -- which, per
WordNet's lexicographer-file layout, front-loads the small `noun.Tops` file of abstract
top-level concepts (`unit/whole`, `individual/mortal`, `act/deed`, `cognition/knowledge` --
literally observed in the confounded pair list). **The confound is baked into the
CONSTRUCTION METHOD itself** (categories chosen concrete; synonym search stopped too early
to reach concrete territory), not an incidental sampling accident. Fix: (1) widen the sibling
category list to include ABSTRACT WordNet top-categories (emotion/feeling/trait/quality/
relation/activity/belief/state/attribute, MEASURED@repo-scratch-probe-2026-08-11: all 13
abstract category-name guesses resolve in the live WordNet install, 3-147 hyponyms each), (2)
widen the synonym pool to a much DEEPER `wn.all_synsets()` scan (cap=700, not 60) so it moves
past `noun.Tops` into the broader (mixed concrete/abstract) noun hierarchy, (3) explicitly
MATCH the two resulting pools on Brysbaert-concreteness by construction (binned equal-count
selection, not post-hoc hope).

## Design

### A) Concreteness-balanced pair construction (removes confound (a))

1. **Sibling candidate pool**: `build_sibling_pool_diverse(wn, SIBLING_CATEGORIES, per_cat_cap)`
   -- direct hyponyms of each of 30 WordNet category synsets (17 concrete + 13 abstract,
   listed in the cell; superset of `f6c6c843e`'s 9 concrete categories), same eligibility gate
   (`_eligible`, imported read-only from `exp_grounded_meaning_wire_lexical_fallback_v1.py`:
   OOV of hand lexicon `CONCEPT_FEATURES`, IN the grounded lexicon), `sorted()` throughout
   (deterministic), up to `per_cat_cap` non-overlapping consecutive pairs per category.
2. **Synonym candidate pool**: `build_synonym_candidates(wn, exclude_words, max_pairs)` --
   imported DIRECTLY (not reimplemented) from `f6c6c843e`'s own cell
   (`exp_diag_learned_encoder_synonym_sibling_deep_wall_v1.py`), called with a much larger
   `max_pairs` (700 at FULL, vs. that cell's 60) to scan deep enough into `wn.all_synsets()`
   to reach concreteness diversity. Sibling-pool words excluded (no cross-set word reuse).
3. Per-pair concreteness = mean of both words' Brysbaert-concreteness z (`grounded_vector(w)[-1]`,
   the SAME dim `f6c6c843e` used for its confound measurement). Pairs where either word lacks
   grounded-lexicon coverage are dropped (should not happen given `_eligible` gate, but
   defensively checked).
4. **Balanced selection** (`balanced_match`): bin BOTH pools into the SAME 5 concreteness bins
   (`CONC_BIN_EDGES = [-4.0, -1.2, -0.4, 0.4, 1.2, 4.0]`, roughly symmetric around the
   population mean of 0); for each bin, take `min(n_syn_avail, n_sib_avail, per_bin_cap)` pairs
   from EACH class (deterministic: sorted by concreteness then alphabetically). This guarantees
   the two final sets have matched per-bin counts BY CONSTRUCTION (not post-hoc verification --
   the achieved `|mean_conc_gap|` is still measured and reported, but the selection mechanism
   itself is what earns the balance, per the task's request for a DECISIVE not a lucky test).
   This produces the **MAIN** (concreteness-balanced, exposure-unrestricted) set.

### B) Held-out slice (removes confound (b))

5. ONE bounded pass over `ARC_Corpus.txt` (reusing `_WORD_RE`/`_quality_ok`/`_line_hash`, same
   preprocessing convention as the training pipeline and `f6c6c843e`) collects, per candidate
   word (union of BOTH pools, pre-selection): (i) capped postings (`cap_mentions`, for pooling)
   and (ii) an **UNCAPPED true mention count** (the original `f6c6c843e` cell only tracked
   capped counts, so it could not see true exposure beyond its cap=24 -- this cell fixes that).
6. Held-out threshold = the 25th percentile of true mention count among all candidate words
   with count >= `min_mentions_heldout_floor` (adaptive/self-calibrating to the actual measured
   exposure distribution of THIS candidate pool at THIS scan scope -- not a hand-picked magic
   number, and not claiming to reproduce the training pipeline's own official ~800-concept
   held-out split, which requires the full CSKG universe + a second full corpus pass and is out
   of scope for a standalone diagnostic, per `f6c6c843e`'s own honest-scoping precedent).
7. A word is "held-out-eligible" iff `min_mentions_heldout_floor <= true_count <= P25`. A pair
   is held-out-eligible iff BOTH words are. `balanced_match` is applied AGAIN, restricted to
   this held-out-eligible candidate pool (same 5 concreteness bins), producing the **DECISIVE**
   set: concreteness-balanced AND (relatively) minimal-exposure by construction, simultaneously.
8. Honest reporting (not gated): per-word true-count distribution for MAIN vs. DECISIVE vs. the
   ORIGINAL `f6c6c843e` set (all capped at its cap_mentions=24, i.e. true count >= 24 for every
   probe word there); `n_zero_mention_candidates` (words with truly 0 corpus mentions, the
   strongest form of held-out, called out separately if any exist).

### C) Encoding + scoring

9. Encoder = the SAME pooling interface as `f6c6c843e` (`TinyTransformer.pooled()` via
   `encode_concept_text_reps`, imported directly). PRIMARY arm = **RANDOM-INIT** same-architecture
   encoder (per task direction: "random-init encoder is fine -- proven it's the interface not
   the learning" -- `f6c6c843e`'s learning-isolation gate already showed random-init >= trained,
   so this cell tests the INTERFACE claim on its own terms). SECONDARY arm = TRAINED checkpoint
   (`ckpt_seed_7.pt`), reported for head-to-head context, not gated.
10. GROUNDING arm (raw Brysbaert/Lancaster cosine, `grounded_vector`) computed on the SAME
    DECISIVE pairs for a fully matched three-way comparison (encoder / grounding / chance).
11. SCRAMBLE control: fixed-seed permutation of the encoder reps matrix (collapses to chance if
    gate 1 is a genuine per-word effect, not an artifact of the scoring machinery).
12. Positive control: replicate `f6c6c843e`'s own cited raw-cosine values for (apple,orange)=
    0.952 and (happy,joyful)=0.962 within tolerance 0.005 (sanity on the grounding-reimpl path).
13. Discriminator: tie-corrected Mann-Whitney AUC (`_auc_from_scores`, imported from the training
    cell) + d-prime, computed independently for MAIN and DECISIVE sets, each arm.

## Envelope / fail-bands

Power floors:
- MAIN set: `n_syn_main >= 12` AND `n_sib_main >= 12` (matches `f6c6c843e`'s convention).
- DECISIVE set: `n_syn_decisive >= 8` AND `n_sib_decisive >= 8` (RELAXED floor -- the
  concreteness x low-exposure double-restriction is expected to shrink the candidate pool
  materially; 8 is chosen as the smallest N at which a Mann-Whitney AUC still carries real
  power against pure noise, not tuned to a preferred outcome. If the achieved N is below this,
  verdict is `MIDDLE_BAND_HELDOUT_UNDERPOWERED`, an explicitly honest non-forced outcome).

**HARD_PASS_CONFOUND_REMOVED_SIGNAL_SURVIVES** (the deep wall IS crossed by the interface, ALL
required, gated on the DECISIVE set, random-init arm):
1. `decisive_power_ok` (both power floors above).
2. `concreteness_balanced_decisive`: `abs(mean_conc_z_sib - mean_conc_z_syn) < 0.3` on the
   DECISIVE set (the task's own stated tolerance).
3. `decisive_randinit_AUC >= 0.65` (materially above chance, matching `f6c6c843e`'s own HARD_PASS
   bar -- not loosened for this harder test).
4. `decisive_randinit_d_prime > 0` (directional consistency).
5. `decisive_scramble_AUC` in `[0.40, 0.60]` (near-chance -- proves gate 3 is a genuine per-word
   effect surviving both confound removals, not a scoring-machinery artifact).
6. `arms_differ_verified` True (random-init reps / trained reps / scrambled reps pairwise
   hash-distinct).
7. Positive control holds within tolerance.

**HARD_FAIL_CONFOUND_WAS_THE_SIGNAL** (the 0.71 was largely a concreteness/exposure artifact;
the deep same-idea wall STILL STANDS): `decisive_power_ok` AND `decisive_randinit_AUC <= 0.56`
(collapses to at/near chance once both confounds are controlled -- same near-chance convention
`f6c6c843e` used for its own HARD_FAIL band).

**MIDDLE_BAND_HELDOUT_UNDERPOWERED**: `decisive_power_ok` is False (could not build >= 8 pairs
per class after concreteness+exposure double-restriction at this corpus scope). The MAIN
(concreteness-balanced-only) set's AUC is still reported as a secondary, non-gating data point
that isolates whether concreteness ALONE explains the original 0.71 (independent of exposure).

**MIDDLE_BAND_PARTIAL**: power OK but `0.56 < decisive_randinit_AUC < 0.65` (real but
sub-decisive separation survives), OR concreteness balance gate fails despite the matching
construction (would indicate a `balanced_match` bug -- investigate before trusting the AUC), OR
scramble control fails to collapse (scoring-machinery concern).

Chance / sensorimotor reference values (CITED, not recomputed): chance AUC = 0.5 exactly
(Mann-Whitney definition); original confounded `encoder_AUC` = 0.7064
CITED@d:/AI/hd-instrument/data/exp_diag_learned_encoder_synonym_sibling_deep_wall_v1/metrics.json:encoder.auc;
original `randinit_AUC` = 0.7452
CITED@d:/AI/hd-instrument/data/exp_diag_learned_encoder_synonym_sibling_deep_wall_v1/metrics.json:randinit_control.auc;
sensorimotor/grounding `grounding_AUC_matched` = 0.3186
CITED@d:/AI/hd-instrument/data/exp_diag_learned_encoder_synonym_sibling_deep_wall_v1/metrics.json:grounding.auc.

## Compute architecture

(b) sequential-CPU with justification: one-shot inference diagnostic (frozen/random-init
weights, `torch.no_grad()`), not training. HYPOTHESIZED@this-prereg (by analogy to `f6c6c843e`'s
MEASURED ~97s full-corpus scan + ~47s/2500-window encode): corpus scan at FULL (whole
14,621,856-line file, more target words than `f6c6c843e` but per-line cost is the dominant
term, not target-word-set size) estimated 100-250s; WordNet pool construction (pure in-memory,
30 categories + a 700-pair-deep synonym scan) estimated <15s; encode pass(es) over the union of
MAIN+DECISIVE final selected words (bounded well below the full candidate pool, comparable
order to `f6c6c843e`'s ~76 words) estimated <60s each (random-init + trained). Total estimated
well under 10 min, run foreground with explicit Bash `timeout: 600000` per the INLINE-LOCAL
mandate (no queue/remote authorized for this task). If FULL measured wall-time approaches the
budget, reduce `synonym_pool_max` / `per_cat_cap` before re-running (documented as a smoke-gate
follow-up, not a silent scope cut after the fact).

Storage strategy: no_storage / no_composition -- reads the checkpoint (for tokenizer/model_cfg
only; trained weights loaded but only used by the secondary arm), grounding CSVs, one corpus
text file; writes one metrics.json; no persisted multi-item store, no downstream chaining.

## Metadata (CELL-TEMPLATE MANDATORY fields)

cell_name: diag_synonym_sibling_confound_removed_v1
cell_chunked: false (single-shot)
final_metrics_atomicity: tmp_replace (`os.replace`)
progress_logging: print_flush_true (all `_log()` calls use `flush=True`; `elapsed_s` expected
well under the 1800s Section-17 trigger regardless, defense-in-depth).
deterministic_seeding: true (fixed int seeds for scramble permutation and random-init weights;
`sorted()`/`sorted(set())` discipline throughout for WordNet enumeration, category/word-list
construction, and the `balanced_match` bin traversal; no built-in `hash()` anywhere; PROT-023/F.5
compliant).
arms_differ_verified: computed at FULL run; `arms_differ_exempted: []`.
crlb_n/a: "AUC discriminator base=0.5 exactly (Mann-Whitney definition); no Gaussian noise-floor
formula applies; scramble control witnesses the empirical near-chance floor directly, same
convention as f6c6c843e."
baseline_in_band: n/a (no accuracy-metric baseline arm to saturate-check); analogue is the
scramble-near-chance gate (checked) and the positive control (checked).
calibration_check: adaptive_with_discriminator_gate -- the held-out P25 threshold is COMPUTED
from the measured true-count distribution of this run's own candidate pool (not a fixed a
priori number), and the discriminator-still-fires check is the DECISIVE power floor + AUC gates
above (if the adaptive threshold produced a degenerate/empty pool, `decisive_power_ok` would
correctly fail and the verdict would honestly say so, not silently pass).
cardinality_ok: EXPECTED_N_UNITS = 2 pair-sets (MAIN, DECISIVE) x 2 encoder-arms (random-init,
trained) + 1 grounding arm (on DECISIVE) + 1 scramble arm (on DECISIVE) = 6 scored-pair-vector
units; counted + logged against actual achieved N per set.
substrate_signature_checked: `TinyTransformer.__init__` (kwargs from checkpoint's own saved
`model_cfg`), `encode_concept_text_reps(model, tok, postings, cfg, device, spec)`,
`grounded_vector(word)`, `build_synonym_candidates(wn, exclude_words, max_pairs)` (imported from
`f6c6c843e`'s cell -- signature bound, not hand-typed).
real_code_path_exercised: self-test constructs the REAL checkpoint + REAL bounded ARC-corpus
scan + REAL `encode_concept_text_reps` call + REAL `balanced_match` selection at tiny scale, not
a synthetic-only branch.
guard_baseline_validated: n/a (no control-beats-baseline break-guard; fixed-checkpoint inference
diagnostic).

## Smoke vs Full

Self-test (`--self-test`): 1,000,000-line bounded scan, 6 sibling categories (4 concrete + 2
abstract) x `per_cat_cap=1`, `synonym_pool_max=20`, `min_mentions_main=1`,
`min_mentions_heldout_floor=1`, `per_bin_cap_main=1`, `per_bin_cap_heldout=1` -- asserts no
crash, correct shapes, arms differ, checkpoint/tokenizer load, `balanced_match` runs and returns
non-empty output at this tiny scale. Does NOT assert the HARD_PASS/HARD_FAIL science verdict
(too few pairs for a meaningful AUC at this scale) -- real-code-path proof only.

Smoke (`--smoke`): 3,000,000-line bounded scan, all 30 sibling categories x `per_cat_cap=3`,
`synonym_pool_max=300`, `min_mentions_main=3`, `min_mentions_heldout_floor=1`,
`per_bin_cap_main=4`, `per_bin_cap_heldout=3`. Proves the full pipeline produces a
non-degenerate MAIN set (power floor met) and reports whatever DECISIVE-set N is achievable at
this reduced scan scope (may legitimately be small/zero at smoke scale -- reduced scan means
fewer words clear even the low `min_mentions_heldout_floor`, and P25 is computed over a smaller,
noisier pool; this is expected and not itself a gate failure at smoke time, only at FULL).

Full (default, no flag): whole-corpus scan (14,621,856 lines), all 30 categories x
`per_cat_cap=4`, `min_mentions_main=10`, `min_mentions_heldout_floor=2`, `per_bin_cap_main=6`,
`encode_batch=128`. THE decisive number.

ACTUAL FULL RUN (2026-08-11, MEASURED wall 254.1s foreground): the foreground-fit scope
reduction pre-registered in the Compute-architecture section above was applied to keep the run
inside one <=10-min foreground call (the INLINE-LOCAL mandate; cap_mentions=24 + synonym_pool_max=700
would have auto-backgrounded = the forbidden bail). Reduced params: `cap_mentions=12` (proven in
smoke to give a stable pooled rep), `synonym_pool_max=300` (smoke showed 300 already yields a
well-balanced MAIN set; the DECISIVE synonym side had 35 candidates -- the sibling side is the
structural bottleneck, unaffected by synonym pool depth), `per_bin_cap_heldout=6`. Full corpus
scan preserved (the load-bearing part: the exposure/held-out split must be over the real corpus).

## Hard invariants

STANDALONE diagnostic only -- does NOT modify `hdlab/lexical_similarity.py`,
`hdlab/grounded_similarity.py`, or `data/capability_registry.jsonl` (confirmed concurrent
session holds those; this cell only imports them + `f6c6c843e`'s cell read-only). Glass-box (no
external LLM call anywhere -- random-init and trained arms both an owned from-scratch
checkpoint architecture). Deterministic. Runs LOCAL, inline, foreground only -- no queue_add, no
remote, no push. ASCII-only.
