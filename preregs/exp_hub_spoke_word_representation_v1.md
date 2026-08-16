# PRE-REGISTRATION -- exp_hub_spoke_word_representation_v1

**Status: PRE-REGISTERED BEFORE ANY RUN -- but NOT GIT-WITNESSED.** Written before the cell was
executed.

> **PROVENANCE CORRECTION (2026-08-15, made while running the full).** This line previously read
> "Written and **committed** before the cell was executed." That was **false**, and it is
> corrected here rather than left standing. Measured, not inferred:
> `git log --all -- preregs/exp_hub_spoke_word_representation_v1.md` returns **nothing** and
> `git status --porcelain` returns `??` -- the file has never been committed on any branch, and
> neither has `hdlab/hub_spoke_word.py` or `experiments/exp_hub_spoke_word_representation_v1.py`.
> The time ordering (prereg first, run second) is still supported by the smoke report at
> `.claude/scan-out/wall1-hubspoke-word.json`, but it rests on that report rather than on an
> immutable commit, which is strictly weaker. This is the SAME provenance defect the cell's own
> self-test ST9 surfaced for the meaning-asset cells (amendment A1) -- it applies to this cell too.
> A pre-registration that cannot be shown to predate its result is a claim, not a guarantee.
Anchor: `hub_spoke_word_representation_v1`. Author: exp_dev. Date: 2026-08-15.
Branch `dataprep/mcguffey-graded-corpus`. Runner: `cpu_runner_local` (smoke) then local full --
the whole cell is 4096 x d matrix algebra, no torch training, no GPU, minutes not hours.

---

## 0. THE QUESTION, IN PLAIN LANGUAGE

Can one word be stored as a **single vector** that nevertheless keeps its parts **separately
askable** -- so that "what does this word look like on the page" and "what does this word mean"
are two different questions with two different answers, both read out of the same vector -- and
so that a **new part can be added later without invalidating anything already stored**?

Today our production word code is one sha256 hash of the spelling, and we call it meaning. That is
a FORM code wearing a MEANING label (`.claude/scan-out/encoding-step2.json`, measured: structure
axis at the null by construction). This cell builds the alternative and measures it.

---

## 1. WHAT IS BEING BUILT, AND WHY THAT SHAPE

The brain keeps word FORM (visual word form area) and word MEANING (modality spokes in sensory and
motor cortex) in **separate systems**, tied together by a hub in the anterior temporal lobe, each
piece keeping its **own address**. The double dissociation is the evidence: hub damage degrades
meaning across all modalities at once; focal spoke damage produces modality-specific loss with the
rest intact. A single blended store predicts only the first pattern.

**Architecture (hub-and-spoke as a single addressed bundle):**

```
word_vector(w) = Q( SUM over spokes s of  bind( SPOKE_KEY[s], spoke_code_s(w) ) )
ask_for(w_vec, s) = unbind( w_vec, SPOKE_KEY[s] )        # bipolar bind is self-inverse
```

- **PINNED-BY-EVIDENCE:** that word form and word meaning are separate systems; that meaning is
  distributed across modality spokes bound by a hub; that each piece keeps its own address.
- **OUR-INVENTION-BEING-TESTED:** implementing "ask for one facet" as unbind-by-role-key. We are
  NOT claiming the brain does elementwise multiplication. Tagged as such in every claim.

**The extension constraint is FIRST-CLASS, not a nice-to-have.** `SPOKE_KEY[s]` is derived from
`blake2b(seed || spoke_name)` **and nothing else** -- not from a shared generator whose stream
depends on insertion order. Consequence, and it is the point: adding a fifth spoke tomorrow leaves
the four existing keys **bit-identical**, so every word vector already written stays readable and
its facet answers do not change. This is gate G2 and it is pass/fail.

**Spokes, and why these.** The Lancaster sensorimotor norms decompose natively along the lines the
brain does, so the split is not arbitrary:

| spoke | source | dims | brain claim |
|---|---|---|---|
| `FORM` | `hdlab/char_trigram_encoder.py` | d | visual word form area, position-tolerant n-gram coding. **A FORM CODE. Never scored as meaning.** |
| `SENSORY` | Lancaster perceptual: Auditory, Gustatory, Haptic, Interoceptive, Olfactory, Visual | 6 | modality-specific perceptual spokes |
| `ACTION` | Lancaster effector: Foot_leg, Hand_arm, Head, Mouth, Torso | 5 | motor/effector spokes |
| `CONCRETE` | Brysbaert concreteness | 1 | the grounding-in-experience axis |
| `MEANING` | all 12 above, lumped | 12 | the brief's literal two-spoke minimum, reported alongside |
| `VISION` | **NOT POPULATED** | -- | the owner's "add how it looks later". Placeholder content; the point is the mechanics, not the content |

Low-dimensional spoke content is lifted to `d` by a fixed random projection then sign-quantised
(SimHash), which preserves cosine ordering. Words outside the norms get a deterministic per-word
random bipolar code in the meaning spokes -- an **UNPOPULATED** spoke, which is the honest
representation of "no meaning content for this word yet". Coverage is reported, and a
covered-words-only diagnostic is reported beside every headline.

---

## 2. WHAT IS REUSED (enumerated from disk; nothing reinvented that we own)

Enumeration method: `ls hdlab/` in full (144 modules, read by eye, not keyword-filtered first),
then every binding/bundling module opened; then `data/capability_registry.jsonl` read afterwards
and reconciled to the disk enumeration, never the reverse.

| reused | what it gives | how the reuse is PROVEN |
|---|---|---|
| `hdlab/role_slot_summarizer.py` `_bipolar_bind` / `_bipolar_quantize` / `_bipolar_random` | the validated binding primitives | self-test ST1 asserts the new numpy primitives are **bit-identical** to these torch ones |
| `hdlab/event_bundle.py` `EventBundleCodec` | role-bound bundle + unbind-and-cleanup + the thin-label and bag-of-args baselines | self-test ST2 asserts `HubSpokeWord.bundle` reproduces `EventBundleCodec.encode_event` **bit-identically** on a matched configuration |
| `experiments/exp_encoding_quality_instrument_v2.py` | THE RULER, imported unchanged: `build_vocab`, `build_ortho_neighbours`, `build_freq_controls`, `gold_ortho`, `gold_freqband`, `load_simlex`, `simlex_rho`, `structure_ap`, `recoverability`, `discriminability`, `sigma_half`, `bundle_survival`, `fano_bits_list`, `enc_orthographic`, `enc_random_iid`, `_l2n`, `_hash_seed`, and every config constant | the file is imported as a module and **never edited**; `git status --porcelain` on it asserted empty in self-test ST9 |
| `experiments/exp_meaning_asset_fair_test_v1.py` | `enc_norms12`, `enc_frequency`, `_rbf_lift`, `simlex_perpair`, `structure_ap_perprobe`, `boot_rho`, `boot_rho_diff`, `band`, `BOOT_SEED`, `N_BOOT` | imported, never edited |
| `preregs/DRAFT_storage_quality_instrument_v1.md` S3 | the **within-item facet discriminator** and `delta_key` (key sensitivity). Generalised here from a store to a word. Not reinvented. | design credit stated; the pool construction is S3's |
| `hdlab/grounded_similarity.py` | the 36,810-word x 12-dim joined norms asset | called through its own live module `_table()` |
| `experiments/_seed_checkpoint.py` (fixed `ee7c42c0f`) | `get_output_dir`, `write_metrics` | -- |
| `tools/exp_checkpoint.py` | per-unit resume (CLAUDE.md MANDATORY) | **not edited.** Its known defect (`unit_key` ignores config) is neutralised by putting a sha256 config fingerprint into every unit key |

**Built new (and only this):** `hdlab/hub_spoke_word.py` -- the spoke-key derivation, the bundle,
the unbind, and the `add_spoke` extension. Roughly 200 lines. Left **importable** for the agent
concurrently wiring the role-bound fact store; `hdlab/hd_fact_store.py` and
`hdlab/reading_grounding_loop.py` are NOT touched.

---

## 3. CONFIG (identical to the ruler; no value is chosen by this cell)

Vocabulary, corpus, byte budget, golds, sigmas, seeds, probe counts and dimensionalities are taken
from `exp_encoding_quality_instrument_v2` at import time. Nothing is re-tuned.

| | smoke | full |
|---|---|---|
| `V` | 512 | 4096 |
| `CORPUS_BYTES` | 8,000,000 | 64,000,000 |
| `D_SWEEP` | [256] | [1024, 256] |
| `SIGMAS` | [1, 8, 32] | [1, 4, 8, 16, 32] |
| `SEEDS` | [7] | [7, 17, 23] |
| `N_GATE` / `AP_PROBES` | 512 / 128 | 1024 / 1024 |

Bootstrap: `N_BOOT` = 10,000 (2,000 smoke), `BOOT_SEED` = 20260815, resampling over **words** for
facet recovery and over **pairs** for the semantic gold. Never over queries within a word.

`BUNDLE_SIZES = [2, 3, 4, 8]`. `FR_SIGMAS` for the saturation control -- see amendment A2.

---

## 4. ARMS (one variable = HOW THE FACETS ARE COMBINED; content, words, golds, scorer held identical)

| arm | construction | role |
|---|---|---|
| `HS4_GRADED` | 4 spokes (FORM, SENSORY, ACTION, CONCRETE), bound then summed, **no terminal sign** | **THE MEASUREMENT.** chance on facet recovery = 0.25 |
| `HS4_SIGNED` | identical, **with** terminal `sign()` | isolates what the terminal quantiser costs here |
| `HS2_GRADED` | 2 spokes (FORM, MEANING) | the brief's literal minimum. chance = 0.50 |
| `HS5_EXTENDED` | `HS4` **plus** a `VISION` spoke added afterwards to the existing codec | the extension demonstration |
| `FLAT_SUM` | the same spoke codes summed with **NO binding** | the unaddressed sum. **Expected at chance on facet recovery** |
| `K_SLOTTED` | one dedicated vector per (word, spoke), no superposition at all | **KNOWN-ANSWER ceiling** |
| `N_NULLCONTENT` | `HS4` addressing with **random** spoke content | **NULL for structure, and must stay HIGH on facet recovery** |
| `F_ORTHO` | char-trigram code alone, no bundle | floor |
| `F_FREQ` | frequency-only lift, no bundle | floor |
| `F_SCRAMBLE` | `HS4` with the three meaning spokes' rows permuted across words | floor (destroys meaning, preserves identity, norms and marginals) |
| `X_CORRSTRESS` | `HS4` where two spokes are drawn from the SAME source family, so the spokes of one word are strongly correlated | **DIAGNOSTIC, not a gate.** The adjudicated finding (`cd8d15cd2`) is that summing correlated codes destroys them; this is the arm that could genuinely fail |

`delta_key` (key sensitivity) = facet recovery with the true key minus facet recovery with a
shuffled key, computed for every arm that has a bundle.

---

## 5. MEASURES -- REPORTED SEPARATELY, NEVER AVERAGED

A random code is near-optimal on identity and at chance on structure. Any blended scalar is
unfalsifiable. Three axes plus the new one, always reported apart.

**M1 IDENTITY** -- `INS.recoverability` over `SIGMAS` at `N_GATE`, summarised by `INS.sigma_half`;
`INS.discriminability` against the orthographic and frequency-matched pools at `HEADLINE_SIGMA`.
A high score here is **not a win**; it is what a random code does by design.

**M2 STRUCTURE** -- `INS.structure_ap` lift on `GOLD_ORTHO` (spelling) and `GOLD_FREQBAND`
(frequency), and `INS.simlex_rho` (the only semantic gold, 322 of 999 pairs). Measured on **two
different vectors per arm and reported as two rows**:
  - **(a) the BUNDLED vector** -- what a downstream consumer sees;
  - **(b) the UNBOUND MEANING spoke** -- what asking-for-meaning actually returns. A flat sum has
    no (b), and that asymmetry is the hub-and-spoke payoff claim.

**M3 BUNDLING SURVIVAL** -- `INS.bundle_survival` at `B in {2,3,4,8}` with `sign_it` False and
True, converted to bits by `INS.fano_bits_list`. This directly tests the adjudicated claim that
the sum is safe below 4 correlated summands and that the terminal sign is the costly operation at
production sites. **Verified, not assumed.**

**M4 FACET RECOVERY -- the load-bearing new measure.** For word `i` and spoke `s`: unbind the
single bundled vector with `SPOKE_KEY[s]`, then take the argmax cosine over the pool
`{code_{s'}(i) for s' in spokes}` -- **the word's OWN other spokes**. Hit if `s' == s`.
Chance = `1/F`. This is `preregs/DRAFT_storage_quality_instrument_v1.md` S3, generalised from a
store to a word; it is invariant to word frequency and to word spelling because the word is held
fixed and only the spoke varies, which is exactly why a floor cannot beat chance on it.

---

## 6. PRE-REGISTERED THRESHOLDS

### 6a. INSTRUMENT-VALIDITY GATES
All must pass. If any fails: report `INSTRUMENT_STILL_LOOSE` and **publish no quality number**.

| id | condition |
|---|---|
| IV1 | `K_SLOTTED` facet recovery >= 0.99 (known-answer ceiling) |
| IV2 | `FLAT_SUM` facet recovery within chance +/- 0.05 **and** its 95% CI covers chance |
| IV3 | `F_ORTHO` and `F_FREQ` facet recovery within chance +/- 0.05. **A floor beating chance here means the within-item design leaks** -- fix the construction, do not report a number |
| IV4 | `N_NULLCONTENT` structure: `GOLD_ORTHO` lift <= 1.15 **and** `abs(simlex rho)` <= 0.10 |
| IV5 | `N_NULLCONTENT` facet recovery >= 0.95. **Fails independently of IV4**: IV4 says the content is null, IV5 says the instrument reads ADDRESSING rather than meaning |
| IV6 | `FLAT_SUM` `delta_key` within +/- 0.05 of 0 (no address means insensitivity to which key you present) |
| IV7 | saturation: `HS4_GRADED` facet recovery declines monotonically (Spearman rho <= -0.8) across the six `FR_SIGMAS`. **A metric that cannot go down is not a measurement** |
| IV8 | the new numpy binding primitives are bit-identical to `hdlab/role_slot_summarizer.py`, and `HubSpokeWord.bundle` is bit-identical to `EventBundleCodec.encode_event` on a matched configuration |
| IV9 | `INS.recoverability` and `INS.simlex_rho` reproduce a published instrument arm to 1e-9 through this harness (`A_ORTHOGRAPHIC` at d=256), proving the ruler was not perturbed |

### 6b. SCIENTIFIC GATES -- evaluated only if every IV gate passes

**G1 -- ADDRESSED.** `HS4_GRADED` facet recovery CI lower bound > the CI upper bound of
`max(F_ORTHO, F_FREQ, F_SCRAMBLE)` on the identical scorer, n, pool and gold, **AND**
`delta_key >= 0.15` with CI excluding 0.
*Honesty note written before the run: passing G1 is a **CONSTRUCTION PROOF**, not a capability
win. Role binding recovering its own role is algebra. What is genuinely can-fail is whether it
survives OUR spoke codes, which are correlated rather than near-orthogonal -- see `X_CORRSTRESS`.*

**G2 -- EXTENSION WITHOUT INVALIDATION** (the owner's first-class constraint; pass/fail, all three):
  - (a) after adding the `VISION` spoke, `SPOKE_KEY[FORM]`, `[SENSORY]`, `[ACTION]`, `[CONCRETE]`
    are **bit-identical** to before;
  - (b) facet recovery re-measured on the **already-written 4-spoke vectors** using the extended
    codec is **bit-identical** to the pre-extension measurement;
  - (c) newly-written 5-spoke vectors return facet recovery >= 0.95 on the four ORIGINAL spokes.

**G3 -- MEANING (a null here is a real and expected outcome).** SimLex rho of the **unbound
meaning spoke** must be CI-separated above `max(orthographic, hardened FREQ_MIN, scramble)` on the
identical 322 pairs, paired bootstrap over pairs.
*Pre-declared expectation: we expect G3 to FAIL. The 12-dim norms cannot separate a synonym from a
sibling by their own module's numbers (sofa/couch 0.968 vs apple/orange 0.952), the learned
encoder's margin has a CI crossing zero, and `NO_ASSET_CLEARS_THE_HARDENED_FLOOR` is the standing
verdict. Recording that expectation here is what stops a later null being spun as a surprise, and
what stops a fluke pass being over-claimed. G1 and G2 are construction claims and do not depend on
G3.*

**G4 -- BUNDLING SAFE AT SPOKE COUNT.** `HS4_GRADED` bundle survival at `B=2` retains >= 0.90 of
the list-decoding ceiling. `B in {3,4,8}` reported as the curve with no threshold.

**G5 -- SIGN COST.** bits(GRADED) minus bits(SIGNED) at each `B`, reported with a
spread-across-seeds. **No threshold** -- the brief asks whether the terminal sign hurts here, which
is a quantity to report, not a hypothesis to gate.

### 6c. STOP-IF
- Any IV gate fails -> `INSTRUMENT_STILL_LOOSE`, no quality number, stop.
- `K_SLOTTED` scores low -> the instrument is wrong, not the architecture. Say so; do not retune.
- Every addressed arm ties `FLAT_SUM` -> addressing is not the lever at word level. Say so plainly
  and do not propose variants.

---

## 7. WHAT THIS CELL DOES NOT MEASURE (declared before the run, so no later reader over-reads it)

- **No store.** One word, one vector. Whether many of these survive being superposed in a store is
  component #2 and is backlog item 1. A word-level pass says nothing about a store-level pass.
- **No downstream number.** No retrieval, no selection, no hit@1. Whether wiring this changes the
  4.80% read-out is NOT measured and cannot be inferred.
- **No claim that the meaning spokes carry meaning.** That is G3 and it is expected to fail.
- **No external LLM anywhere.** The spoke sources are a character n-gram encoder and two published
  human-rating norm sets. No model is contacted at any point, at build time or at inference.
- The 12-dim norms are lifted by a random projection; identity-axis numbers for meaning spokes are
  dominated by that lift, not by the asset. No comparison is made across dimensionality blocks.

## 9. AMENDMENTS -- both made BEFORE any data run, both found by the cell's own self-test

Recorded as dated amendments rather than silently applied. **No threshold in section 6 was
changed by either.**

**A1 -- ST9 distinguishes "modified" from "never committed".** The ruler-integrity self-test
originally asserted `git status --porcelain` was empty for its imported helpers. It fired on
`experiments/exp_meaning_asset_fair_test_v1.py` with `??` -- which means the file is **UNTRACKED**,
never committed, not that this cell edited it. That is a real provenance fact and it is now
**recorded in the metrics** (tracked flag, porcelain string and sha256 for every ruler file)
instead of being swallowed. The hard assertion is kept for TRACKED files:
`experiments/exp_encoding_quality_instrument_v2.py` is tracked and clean at HEAD.
*Direction: neither tightens nor loosens a measurement. It stops a provenance fact masquerading
as a tamper alarm -- and it surfaces that the meaning-assets cells cited by
`.claude/scan-out/meaning-assets-fair-test.json` are not in git.*

**A2 -- the saturation grid is widened.** Self-test ST12 showed that on the originally
pre-registered grid `[0, 0.25, 0.5, 1, 2, 4]` facet recovery only fell to 0.928 at the top, so
gate IV7 would have been satisfied by four tied `1.0000` readings -- i.e. **vacuously**. The grid
becomes `[0, 1, 2, 4, 8, 16, 32]`, spanning to where the measure must collapse.
*Direction: **TIGHTENS**. IV7 exists to prove the metric can go down; a grid on which it barely
moves defeats the gate. The threshold (Spearman <= -0.80) is unchanged.*

**A3 (2026-08-15, AFTER the full run) -- gate G3's measured vector is rescored through CLEANUP,
because the pre-registered one is mathematically DEGENERATE.**

*Found:* by the SMOKE gate, **before** the full run, and disclosed at the time in
`.claude/scan-out/wall1-hubspoke-word.json` and in the v1 cell's module docstring rather than
silently patched.

*What is wrong:* G3 scores "the SimLex rho of the **unbound meaning spoke**". Binding by a
bipolar +-1 key is an **isometry** --
`(v_i * k) . (v_j * k) = sum_d v_i[d] v_j[d] k[d]^2 = v_i . v_j` because `k[d]^2 = 1` -- so the
unbound vectors carry **exactly** the pairwise cosines the bundle already had. As written, G3
scores the BUNDLED vector under a different name. It is not a coding slip and it cannot be fixed
by re-running: no choice of key makes a linear read-out of a bundle differ from the bundle.

*The finding this actually is, and it is carried forward:* **unbinding buys an ADDRESS, not extra
geometry.** Any structural gain has to come from the CLEANUP step, which is nonlinear.

*The fix, exactly as pre-specified in the v1 cell docstring:* measure row (b) as
**unbind -> clean up against that spoke's own codebook over the vocabulary -> score the RECOVERED
code**, not the raw unbound vector.

*How it was applied, and what was deliberately NOT done:* the v1 cell was **NOT edited**. It ran
unchanged and its pre-registered gates stand exactly as published, degenerate G3 included and
labelled. The rescore is a separate cell,
`experiments/exp_hub_spoke_word_g3_cleanup_rescore_v1.py`, whose metrics land at
`data/exp_hub_spoke_word_g3_cleanup_rescore_v1/`. The gate is **not dropped**: both the
degenerate row and the rescored row are reported side by side, and the degeneracy is
**re-verified at full scale** rather than carried over from smoke.

*Threshold:* **UNCHANGED.** G3 is still "CI-separated above
`max(orthographic, hardened FREQ_MIN, scramble)` on the IDENTICAL pairs, paired bootstrap over
pairs". The SCRAMBLE floor is routed through the **identical** unbind->cleanup path so it stays
matched; ORTHOGRAPHIC and FREQ_MIN stay **standalone** channels, as a floor must be.

*Direction:* **NEITHER tightens nor loosens.** It replaces a measurement that provably could not
vary with one that can. It is nonetheless a **post-hoc** amendment in timing, and that is stated
rather than hidden: the motivation is data-independent (an algebraic identity found at smoke),
but the amendment text was written after the full run, which is weaker than a pre-run amendment
and must be read as such.

*Mandatory caveat on how far the rescore can carry:* cleanup snaps each unbound query to a
codebook entry. Where cleanup is near-perfect the recovered code IS the direct spoke code, so the
rescored G3 collapses into a question about the **sensorimotor-norm asset**, not about the
bundle. The rescore cell therefore reports the ceiling (direct spoke codes), the rescore, and the
degenerate row separately and never averaged, plus two cleanup-fidelity statistics
(identity accuracy and code-exact accuracy -- they differ, because the `CONCRETE` spoke is one
dimension lifted by SimHash and so has very few distinct codes by construction).
**`NOT_EVALUABLE` is a permitted outcome** and is emitted if cleanup returns noise.

**A3 RESULT, recorded 2026-08-16 after the rescore cell was run at FULL scale** (V=4096, 322
SimLex pairs, 3 seeds x 2 dimensionalities; `data/exp_hub_spoke_word_g3_cleanup_rescore_v1/`).
The gate is **not dropped and both rows are published**:

| row | what it is | SimLex rho (d=1024, seed 7) |
|---|---|---|
| DEGENERATE (as pre-registered) | raw unbound meaning spoke | equals the bundled vector to 16 digits; max abs cosine delta ~1.2e-07 at full scale |
| **RESCORED (the A3 fix)** | unbind -> cleanup -> recovered code | **0.1961** |
| CEILING | direct spoke codes, never bundled | ~0.198 |
| strongest floor | HARDENED_FREQ_MIN | 0.0797 |

**G3 RESCORED = FAIL, band NOT_SEPARATED.** Margin over the strongest floor **+0.1164**, 95% CI
**[-0.0308, +0.2653]**, which **crosses zero**. The pre-declared expectation was FAIL and the
rescore does not change it. Threshold unchanged; the rescore was applied to the measured vector,
never to the criterion. The mandatory caveat in A3 is borne out: cleanup is near-perfect
(code-exact accuracy ~0.97), so the rescored row lands essentially **on** the ceiling of the
direct spoke codes, which means the rescored G3 is a question about the **sensorimotor-norm
asset**, not about the bundle.

*Label defect fixed in the rescore cell on the same date, no threshold touched:* `run_mode` was
hard-coded `"full"`, so `data/exp_hub_spoke_word_g3_cleanup_rescore_v1_smoke/metrics.json` on
disk is **mislabelled "full" while carrying only 26 SimLex pairs**. It is derived from the parent
cell's run mode now. The stale smoke file is left in place and flagged rather than deleted.

**A4 (2026-08-16, AFTER the full run) -- the SCOPE of the G1 headline is bounded, and G1's
pre-registered outcome is recorded as it fell.**

*This amendment changes NO threshold and re-runs nothing.* It records two things that a reader of
the headline must have.

**(1) G1 FAILS as pre-registered, and that is the result.** Section 6b defines G1's floor as
`max(F_ORTHO, F_FREQ, F_SCRAMBLE)`. At full scale `F_SCRAMBLE` scores facet recovery **1.0000
with CI [1.0000, 1.0000]**, because scrambling *which word owns which meaning* does not touch the
addressing channel at all. So `HS4_GRADED` CI-lower (1.0000) is **not** strictly greater than the
max-floor CI-upper (1.0000), and the cell's own `evaluate()` returns **G1 = False**. The smoke
report at `.claude/scan-out/wall1-hubspoke-word.json` recorded "G1 would pass" from a **hand
computation that silently excluded `F_SCRAMBLE`** from the floor set; the cell's code never
excluded it. This is the first time the pre-registered gate was evaluated by code, and it fails.
**The threshold is NOT amended to rescue it.** The substantive reading -- that against the floors
which ARE floors on the facet axis (`F_ORTHO` 0.2252, `F_FREQ` 0.2531) the addressed bundle at
1.0000 is CI-separated -- is reported **beside** the failing gate, never in place of it.

**(2) The headline is an EXACT-KEY measurement.** `facet_recovery` presents the exact key the
facet was stored under. A sibling result (`c33e6d338`) established that exact-key retrieval is
precisely the regime that flatters addressing, and that conjunctive addressing scored 1.000 in
isolation and then lost CI-separated on a never-seen partially-overlapping cue. The scope of
G1/M4 is therefore bounded to exact-key retrieval, and the partial-cue behaviour is measured in a
separate cell with its own pre-registration:
`preregs/2026-08-16_exp_hub_spoke_partial_cue_curve_v1.md` ->
`data/exp_hub_spoke_partial_cue_curve_v1/metrics.json`. Nothing in the v1 cell is edited or
re-run by that work.

---

## 8. HAZARDS HONOURED

`data/foundation/**` never opened. No `git add -A`; explicit path list at commit. No origin push.
`hdlab/hd_fact_store.py`, `hdlab/reading_grounding_loop.py`, `CLAUDE.md`,
`data/exp_coref_margin_gated_cleanup_local_window_break050_v1*` and
`data/exp_structured_comparator_v1/probes/` never touched. No existing `preregs/` file modified.
`OMP_NUM_THREADS` / `OPENBLAS_NUM_THREADS` pinned at the top of the .py before numpy is imported,
never as a shell prefix. ASCII only. `sorted(set())` discipline for every iteration order.
