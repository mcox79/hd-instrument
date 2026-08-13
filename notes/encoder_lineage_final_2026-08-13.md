# Encoder lineage + S8 verdict re-check (2026-08-13)

> **SUPERSEDED IN PART -- 2026-08-13 (later same day) by
> `notes/encoder_landed_correction_2026-08-13.md`. Read that first.** Two load-bearing claims below
> are REFUTED and must not be cited from this file:
> 1. **"No final landed encoder exists -- the line was abandoned, not won" is FALSE.**
>    `hdlab/encoder_retrain_persist.py` landed at `367a42729` (2026-07-31), clean at HEAD, registry
>    `gate_decision: WIRE` / `integration_status: WIRED`, assets
>    `data/exp_encoder_retrain_persist_v1/ckpt_seed_{7,13,19}.pt` (untracked by design, all 3 load,
>    loader verifier OVERALL PASS). It is OPT-IN by design, so the "40 modules, 0 encoders" runtime
>    trace here measured the DEFAULT path and was wrongly reported as measuring EXISTENCE. It also
>    HAS accuracy floors, contrary to sec 0/3 below: `exp_encoder_alltype_transfer_v1`,
>    `..._stress_v1`, `exp_coref_encoder_transfer_v1` (all HARD_PASS 2026-08-01) and the
>    `exp_situation_model_assembly_encoder_retrain_scale_v1` CLEAN_PASS recipe cert. This note
>    never enumerated the 2026-08-01 cells -- grep it for `alltype`, `coref_encoder_transfer` or
>    `load_improved_encoder`: zero matches.
> 2. **The synonym-vs-sibling "0.7064 trained vs 0.7452 random-init" wall has NO evidence behind
>    it.** `exp_diag_learned_encoder_synonym_sibling_deep_wall_v1.py:104-105` hardcodes the
>    `exp_scale_meaning_learn_arc_heldout_v3_relobj` HARD_FAIL checkpoint (all 76/76 tensors differ
>    from v2), so it measured neither the v2 HARD_PASS encoder nor the landed asset; and it was
>    superseded 43 min later by `exp_diag_synonym_sibling_confound_removed_v1`
>    (main_trained 0.5888 vs main_randinit 0.4615 vs main_scramble 0.5074, n=26/26,
>    concreteness balanced). The "pooling interface separates them" framing does NOT survive.
>
> Also note: `exp_scale_meaning_learn_arc_heldout_v2` is NOT superseded by `v3_relobj` -- v3
> changed the training OBJECTIVE and RELOADS v2 as its baseline. Everything else in this note
> (the 18 pass-vs-conflicting-data cases, the CLIP correction, the registry mismatches) stands.

READ-ONLY investigation. No code changed, no commits. Repo HEAD at read time `48a9900c1`,
branch `dataprep/mcguffey-graded-corpus`. Trigger: `notes/STATUS.md:67` "(e) Encoder lineage
under review -- the S8 fault verdict may be on a SUPERSEDED version."

**RULE APPLIED THROUGHOUT: a number without its control floor is not a result.**

---

## 0. The three findings that matter

1. **No encoder of any kind is on the operational path.** Runtime `sys.modules` trace of
   `hdlab.reading_grounding_loop` + `hdlab.grounding_acquisition_loop` loads **40 hdlab modules,
   of which ZERO are encoders** (no vwfa, ppmi, composed_v3, concept_encoder,
   encoder_retrain_persist, random_indexing, hippocampal_encoder). The three lazily-imported
   modules invisible to static search are `hdlab.arc_labeler`, `hdlab.arc_parser`,
   `hdlab.pos_tagger` (+ `hdlab.perceptron`) -- **none is an encoder**. Static cross-check:
   the only hdlab importers of any encoder module are the encoder modules themselves
   (`composed_encoder_v3` -> `ppmi_sparse_encoder`, `vwfa`; `encoder_retrain_persist` -> itself).
   The encoder cluster is a **closed island**.
2. **The registry's named successor was never promoted and its own cell HARD_FAILed.**
   `scale_win_tinytransformer_encoder` (`status: validated_chain_grade_best_encoder`,
   `gate_decision: WIRE`) has `path: experiments/exp_scale_meaning_learn_arc_heldout_v3_relobj.py`
   -- whose `metrics.json` reads **`HARD_FAIL_ARCHITECTURE_BOUND`** (2026-07-28). Its
   `pipeline_status` is `N_A`, `integration_status: TRAPPED_SHARED`, and its own provenance
   concedes "ZERO hdlab imports". Its `gate_decision_target` ("promote to hdlab once
   readout/comprehension work settles") **never happened**.
3. **"Nothing is learned" is TRUE of the module the audit dissected and FALSE of the successor
   -- but the successor's learning does not buy the distinction the project needs.** Detail in
   sec. 3.

---

## 1. Lineage -- every encoder built, in date order

Dates from `git log --diff-filter=A`. Verdicts from `data/exp_*/metrics.json`.

Legend: **FIXED** = hash-seeded random codebook, no fit. **FIT-CF** = closed-form/counting fit,
no gradients. **GRAD** = genuine gradient training.

| # | Encoder (date added) | Path | Mechanism | Landed verdict + headline | **CONTROL FLOOR** | Superseded by |
|---|---|---|---|---|---|---|
| 1 | `whitening` (06-22) | `hdlab/whitening.py` | **FIT-CF** ZCA/PCA whitening; a residual transform, not an encoder | `exp_substrate_pca_prewhitening_codebook_v1` **HARD_PASS**, capacity 3.0 -> **7.0 (2.33x)**, N=384 real MiniLM keys | paired control only: **unwhitened cap = 3.0**. **No chance/scramble arm.** No self-test, no witness | -- (**no registry row**) |
| 2 | `char_trigram_encoder` (06-22) | `hdlab/char_trigram_encoder.py` | **FIXED** blake2b(trigram) -> bipolar HV, sum+sign | `exp_substrate_wikipedia_char_trigram_scale_up_full` **MEASURED_BOUND** r@5 = **0.7030** @ N=10000 | **random r@5 = 0.0003, chance 0.000500**; gap to BGE-100k ref **-0.2890**; -0.1510 vs its own N=500 smoke | -- (registry `WIRED`; **default KB encoder** via `kb_encoder_registry`) |
| 3 | `random_indexing` (06-22, touched 08-06) | `hdlab/random_indexing.py` | **FIT-CF** fixed sparse-ternary index vectors + accumulated context vectors (Hebbian counting) | `exp_n11_random_indexing_semantic_v1` **MIDDLE_BAND**, related/unrelated ratio **1.202** (BEAGLE 1.214) | **CONTROL ratio = 1.001 (chance).** Signal real but tiny. Siblings `exp_n11b_symmetric_pattern_lexical_similarity_v1` and `exp_context_conditioned_sense_selection_v1` both **HARD_FAIL** | -- (registry **VET_PENDING / default-NOT-WIRE**) |
| 4 | `token_vocab` (06-26) | `hdlab/token_vocab.py` | **FIXED** content-free hash-seeded sparse-bipolar basis | **no cell, no landed number at all** | **NO FLOOR RECORDED** | -- (no registry row) |
| 5 | `concept_encoder` (07-02, **1 commit, never touched since**) | `hdlab/concept_encoder.py` | **FIT-CF** "competitive-Hebbian": mean-centre -> per-label sum -> top-K WTA -> `np.sign`. One closed-form pass, no competition | `..._spoke1_v3_D_competitive_hebbian_only` **HARD_PASS**, cat/kitten cos **0.492**, gap 0.472 | Good floors: **RANDOM ck -0.002, TRIGRAM ck -0.008, NAIVE_WTA gap 0.000**, label-shuffle 0.016. **BUT** follow-up `..._stress_test_cell1_apples_to_apples_label_shuffle_v1` = **MIDDLE_BAND**: softmax control **0.461 vs 0.492** -- fails "beats softmax by min" | covered only via registry row `composition` (sec. 5.3) |
| 6 | `vwfa` (07-02) | `hdlab/vwfa.py` | **FIXED** char-ngram HV HRR-bound to position, sign-bundled | `..._concept_encoder_v2_vwfa_late_combine_2spoke` **HARD_FAIL**; VWFA r@5 **0.2533** (best single spoke there), **0.2400 = worst arm** in the composed-v3 smoke | in-cell floors PPMI 0.3400, TRIGRAM 0.2800, late-combine 0.2000; sibling cells give **random r@5 0.0003** | `scale_win_tinytransformer_encoder` (on paper) |
| 7 | `char_positional_encoder` (07-02) | `hdlab/char_positional_encoder.py` | **FIXED**; front-end inside `concept_encoder` | **no cell of its own** | **NO FLOOR RECORDED** | -- (no registry row) |
| 8 | `ppmi_sparse_encoder` (07-02) | `hdlab/ppmi_sparse_encoder.py` | **FIT-CF** PPMI+SVD over **concept labels, not contexts** -> rank capped at ~n_labels, zero-padded to 2048; self-test asserts the collapse (`:324`) | smoke **HARD_PASS** r@5 0.3400 (N=100); **at 20x scale `MEASURED_BOUND_LOW_DELTA` r@5 0.6791 = -0.0239 BELOW char-trigram** | smoke: trigram 0.7030, v1 0.1600, random-bipolar 0.0667. Full: **random 0.0003, chance 0.000500**. **The smoke lift +0.052 did not survive scale** | idem |
| 9 | `composed_encoder_v3` (07-02) | `hdlab/composed_encoder_v3.py` | No new learning: weighted sum of VWFA+PPMI cosines, alpha grid-fit | `..._adaptive_alpha_smoke` **MIDDLE_BAND**, 0.3467 vs best single 0.3400 (**+0.0067**); **fitted alpha = 0.0 on all 3 seeds -- composition collapses to PPMI alone** | PPMI 0.3400, VWFA 0.2400, TRIGRAM 0.2800, v3-equal 0.3333. Smoke only (N=100). **No random arm** | idem |
| 10 | `late_combine` (07-02) | `hdlab/late_combine.py` | Weighted stream sum, weights by 11-point grid search (N400 framing) | **HARD_FAIL** -- combined r@5 **0.2000 < best single spoke 0.2533**. **Composition HURTS** | floor = single-spoke arms (VWFA 0.2533 / SEM 0.1667). Smoke only | -- (no registry row; dead with the v3 cluster) |
| 11 | `hippocampal_encoder` (07-02, 07-08) | `hdlab/hippocampal_encoder.py` | **FIXED** DG random projection + top-K sparsify, then **FIT** one-shot CA3 Hebbian outer product | `..._spoke3_hippocampal_encoder_smoke` **HARD_FAIL_MECHANISM_LOSES**, r@5 **0.1460** | explicit: char_trigram ref **0.854** (bar 0.8240), PPMI 0.9060, **random 0.0073**. **Lost to the trivial trigram bag by 0.71** | -- (registry `ALREADY_WIRED`, ~20 consumers) |
| 12 | `gsbc_graded_encoder` (07-08) | `hdlab/gsbc_graded_encoder.py` | **FIXED** per-block top-m survivors; **requires an EXTERNAL teacher (BGE + trained student MLP)** to touch text at all | `exp_encoder_gsbc_gradedcode_marginpush_v1` (5 seeds) **HARD_PASS** at m=5, ret_agree10 **0.4479** | floor is a **chosen 0.30 bar, not chance**; real can-fail control present: **shuffled_key acc@1 = 0.0** vs 1.0 intact | -- (no row; selectable but not default) |
| 13 | **TinyTransformer v1** (07-27) | `experiments/exp_scale_meaning_learn_arc_heldout_v1.py` | **GRAD** | **MIDDLE_BAND_TIE_NULL**, \|fused-raw\| 0.0076 | -- | -- |
| 14 | **TinyTransformer v2 -- the real headline** (07-27) | `experiments/exp_scale_meaning_learn_arc_heldout_v2.py` | **GRAD**: from-scratch 6-layer/d512/8-head TransformerEncoder, from-scratch 16k BPE, **121,082,196 real ARC tokens/seed, 3.7 h CUDA**, no borrowed vectors | **HARD_PASS_CLEAN_WIN.** semantic AUC text **0.6356**; margin over raw grounding **+0.0500**; relational 0.6327 vs 0.5617 **+0.0710** | **Best-controlled cell in the set:** chance 0.5, **COLLAPSE_SHUFFLE 0.4964, POPULARITY 0.4968, RANDOM_INIT (untrained same-arch) 0.5322**, `learning_text_minus_random = **+0.1034**` | -- |
| 15 | **TinyTransformer v3_relobj** (07-27) | `experiments/exp_scale_meaning_learn_arc_heldout_v3_relobj.py` **(the path the registry points at)** | **GRAD**: v2 + joint InfoNCE relational loss on CSKG typed edges | **HARD_FAIL_ARCHITECTURE_BOUND** (07-28): relational margin **-0.0046 mean / -0.0221 min** (needed >= +0.03); **semantic margin -0.0386**; text-alone over raw grounding **+0.00018** (per-seed min **-0.00054**). rel_loss did fall 4.71->2.93 | same battery: collapse 0.4993, popularity 0.4968, random_init 0.5322 | -- |
| 16 | TinyTransformer v3_grounding / v4_breadth / v5_forwardpc | `experiments/` | **GRAD** | **NEVER RAN FULL** -- v3_grounding smoke only (rel margin **-0.2267**, `ground_loss_decreased=False`); v4 selftest only; v5 smoke only | -- | -- |
| 17 | `encoder_retrain_persist` (07-31) | `hdlab/encoder_retrain_persist.py` | **Loader** (40 lines) for a **GRAD** artefact: v2 ARC ckpt + top-1-layer unfreeze, 3,153,408 trainable params, 220-320 SGD steps | `exp_encoder_retrain_persist_v1` **HARD_PASS** = reload deviation **0.0** x3 seeds | **NO ACCURACY FLOOR -- it is a round-trip determinism check.** Borrowed floors from the source cell only | -- |
| 18 | `exp_situation_model_assembly_encoder_retrain_scale_v1` (07-31) | `experiments/` | **GRAD** minimal unfreeze; cross-mention-consistency + inter-entity-push + VICReg | **CLEAN_PASS**, best held-out loop **0.830** | **Best floor set in the inventory:** chance **0.05**; FROZEN wall 0.4704/0.5182/0.5249; TUNED-oracle ceiling 0.769-0.854; REF_SPAN 0.97; **must-fail control d6 (full unfreeze) craters to 0.2916 and does fail the guard**. Scope: **SYNTHETIC templated harness, 20-colour palette** | -- |
| 19 | `..._retrain_lite_v1` / `..._retrain_role_v1` (07-31) | `experiments/` | **GRAD**, smaller | both **MIDDLE** -- lite 0.474->0.534 (below 0.60 bar); role 0.681->0.738, `lift_ok=False abs_ok=False` | chance 0.05; oracles 0.625-0.855 | -- |
| 20 | `gated_fusion` (07-28) | `hdlab/gated_fusion.py` | Not an encoder: **one scalar lambda** grid-searched on VAL; **grid includes 1.0 so it cannot lose to the fallback by construction** | `..._relation_inference_mammal_v1` **HARD_PASS**, MRR 0.3645 -> **0.6619** (+0.2974), 8/8 seeds | Full battery: **SCRAMBLE 0.5682, RANDOM 0.0275**, POPULARITY 0.5127, ORACLE 1.0, GROUNDED_ONLY 0.6525. **Deflation: gated 0.6619 vs grounded-alone 0.6525 = +0.0094; only +0.094 over SCRAMBLE; n_queries = 27** | -- |
| 21 | gated_fusion **text-grounding encoder** seeds 7/13 (07-28) | `experiments/_gated_fusion_text_grounding_encoder_core.py` + seed cells | lambda gate over the tinytransformer's text vs grounding channels | registry claims LANDED: seed7 sem +0.0030, rel +0.0239; seed13 +0.0055 / +0.0282 | **NO metrics.json EXISTS ON DISK** -- only `_selftest` dirs (`SELFTEST_PASS @ N=24 synthetic`). **Every quoted number is registry PROSE.** No chance/scramble floor quoted at all | -- |
| 22 | `grounded_similarity` (08-11) | `hdlab/grounded_similarity.py` | **Not an encoder** -- closed-form cosine over a FIXED external lookup (39,707-word Lancaster sensorimotor + Brysbaert concreteness), z-scored, hard-capped 0.45 | `exp_grounded_meaning_wire_lexical_fallback_v1` **HARD_PASS_grounded_meaning_wired_without_over_merge**; 400 newly covered words, median synonym **0.3781** | **median unrelated = 0.0000**; anti-over-merge control **19/19 trap pairs stay distinct**. Self-declared ceiling: siblings (apple/orange 0.952) **statistically inseparable** from synonyms (sofa/couch 0.968) at raw cosine -- hence the cap | -- (**LIVE**) |
| 23 | `lexical_similarity` (08-06, 4 commits, last 08-12) | `hdlab/lexical_similarity.py` | **Not an encoder** -- ~230-380 hand-typed concept feature sets, FHRR bundle-cosine | **LIVE.** `concept_similarity()` is the operational concept-similarity call | -- | -- (**LIVE**) |
| -- | `kb_encoder_registry` (07-08) | `hdlab/kb_encoder_registry.py` | Not an encoder -- name->instance resolver (`char_trigram_v1` default) | no cell, no number | n/a | -- |
| -- | `exp_tiny_transformer_baseline` (05-17) | `experiments/` | **GRAD** 0.86M-param decoder-only, byte-level -- a deliberate "real ML ceiling" baseline, **not a substrate encoder** | best test bpc **2.387** | unigram 5.7383, bigram 4.9047, Hebbian-VSA 3.100. **Deflate:** headline uses `best_test_bpc` while `final_test_bpc` = **3.605** (best-checkpoint cherry-pick); corpus is this repo's own markdown | -- |

---

## 2. Which is the FINAL landed encoder?

**There is none. The encoder line was abandoned, not won.**

Evidence, in order of strength:

- **Runtime import (the decisive test).** `import hdlab.reading_grounding_loop,
  hdlab.grounding_acquisition_loop` -> 40 hdlab modules, **encoder-like count = 0**. Adding the
  three lazy modules (`arc_labeler`, `arc_parser`, `pos_tagger`) adds `hdlab.perceptron` and
  still **0 encoders**.
- **What actually serves concept similarity in the live path:**
  `hdlab/lexical_similarity.py::concept_similarity()` (hand lexicon) with
  `hdlab/grounded_similarity.py` as the OOV fallback -- both loaded in the trace. Neither is a
  learned encoder; both are lookup + FHRR bundle-cosine.
- **`grounded_similarity.py`'s own docstring (`:19-20`) states the decision explicitly:**
  the sensorimotor asset was "evaluated ahead of the from-scratch learned encoder
  (`scale_win_tinytransformer_encoder`, see capability_registry.jsonl) as the primary asset to
  wire." So the tinytransformer was **considered and passed over on 2026-08-11**.
- **Registry corroborates non-promotion:** successor is `TRAPPED_SHARED` / `pipeline_status: N_A`
  / "ZERO hdlab imports".

So the user's recollection is **half right**: many encoders were tested and wrong calls were made.
But the thing landed at the end is **not an encoder that worked** -- it is a
lexicon+sensorimotor-norm similarity path that replaced the encoder question rather than answering
it. The best from-scratch encoder (TinyTransformer v2) is real and passed, but sits in
`experiments/`, unpromoted.

---

## 3. Does the S8 ARCHITECTURAL-FAULT verdict survive? -- **YES, but its stated reason is wrong.**

Split the audit's charge in two.

**(a) "`learning_rate` provably cancels" -- CORRECT, but about DEAD CODE only.**
Verified directly at `hdlab/concept_encoder.py:495-505`: `acc[cid] += lr * centered[i]`, then
`magnitudes = np.abs(acc[c]) / counts[c]` and `np.sign(acc[c])`. For any `lr > 0` the magnitude
*ranking* and the *sign* are both invariant -> `lr` cannot change the output. The audit is
mechanically right. **But `concept_encoder.py` has 1 commit, dated 2026-07-02, has never been
modified, has ZERO hdlab importers, and is not in the runtime closure.** This criticism therefore
applies **only to a superseded, unreachable module** and licenses nothing about the project's
encoders as a class.

**(b) "Nothing is learned" -- FALSE for the successor, on the successor's own control.**
TinyTransformer v2 clears a **random-init same-architecture floor** by **+0.1034**
(text 0.6356 vs random_init 0.5322, both seeds). That is the correct control and it fires.
"Nothing is learned" is refuted for the final-generation encoder.

**(c) But the successor fails the distinction the project actually needs -- with a BETTER control
than the audit used.** `exp_diag_learned_encoder_synonym_sibling_deep_wall_v1` (**2026-08-12**, the
most recent encoder evidence in the repo):
> encoder_AUC=**0.7064** (d'=0.752), beats grounding_AUC_matched=0.3186, scramble collapses to
> 0.5042 -- **BUT the untrained same-arch RANDOM-INIT encoder using the SAME corpus-mention-pooling
> interface scores randinit_AUC=0.7452 >= trained.** "the separation is a property of the
> distributional-context POOLING INTERFACE ... NOT of the encoder's LEARNED representation."

So on synonym-vs-sibling (the same-idea wall), the trained encoder does **no better than its own
random-init twin**. The audit's conclusion lands; its evidence should have been this cell, not
`concept_encoder`'s inert `lr`.

**(d) The audit's cited decisive control was also measured on the old cluster.**
`exp_sense_collapse_floor_v1` (`verdict: MEASURED`, 2026-08-05):
`honest_floor=0.562 (encoder=concept_encoder); best_context_sensitive=ppmi_sparse_encoder acc=0.625;
best_starting_encoder_for_CA_extension=none (all 4 encoders collapse at/near chance)`.
The four encoders tested are the 2026-07-02 cluster. **The TinyTransformer was never in this test.**

**Net.** S8's **severity (ARCHITECTURAL-FAULT) and wire verdict (NO) SURVIVE** -- confirmed against
the final encoder by a stronger control on more recent data. Its **headline sentence must be
corrected**: it is not "nothing learned but one loader / inert learning rate" (a fact about
2026-07-02 dead code); it is *"the from-scratch encoder does learn (+0.103 over random-init on
held-out semantic), but its learned representation contributes nothing to the same-idea distinction
-- there a random-init twin matches it (0.7452 vs 0.7064); and no encoder of any generation is on
the operational path."* The audit is right for the wrong reason, and its reason names a superseded
module. **Correction required, verdict retained.**

---

## 4. Glass-box line: SEED/FOUNDATION (permitted) vs OPERATIONAL INFERENCE (barred)

Rule: an LLM/external model **may** build the seed/foundation; it **may not** be in the
operational inference flow.

| Encoder / asset | External model used? | Where | Side of the line |
|---|---|---|---|
| `concept_encoder`, `vwfa`, `ppmi`, `composed_v3`, `char_*`, `token_vocab`, `late_combine`, `whitening`, `random_indexing`, `hippocampal_encoder` | none | -- | **CLEAN** (numpy only) |
| `lexical_similarity`, `grounded_similarity` (**LIVE**) | none. `import torch` present but used **only** as tensor/RNG (`torch.Generator`, `torch.stack`, `torch.real`) for seeded FHRR phasors -- **no learned network** | runtime | **CLEAN** -- verified, not a violation |
| `grounded_similarity` norms asset | Lancaster sensorimotor + Brysbaert concreteness = **human behavioural norms**, a static dataset | seed | **PERMITTED** |
| TinyTransformer v2/v3 | **our own** from-scratch net, no borrowed vectors | would be runtime if promoted | Not an *external* model, but a **learned net at inference** -- promoting it is a glass-box judgement call, not automatic. Flag before any wire. |
| `encoder_retrain_persist` | **our own**, two stages: **(1) base = TinyTransformer v2, MLM on 121M tokens of REAL AI2 ARC text; (2) delta = top-1-layer unfreeze, 3.15M params, 220 SGD steps, on a SYNTHETIC templated situation-model harness (20-colour palette, chance 0.05)** | runtime (loader is `WIRED_BUT_NOT_PIPELINE_REACHABLE`) | same caveat. Scope caveat must travel **verbatim**: the 0.52 -> 0.83 lift is measured **only inside that synthetic harness**; registry's own deploy decision is `PENDING_USER_steer_plus_naturalistic_validation` |
| `gsbc_graded_encoder` | **requires an external neural teacher**, fail-louds without one | runtime | **BARRED as written** -- correctly unwired |

### 4a. CLIP visual grounding -- **PREVIOUSLY RULED OUT IN ERROR; THE RULE PERMITS IT**

`data/exp_visual_grounding_coherence_v1/metrics.json` (2026-07-18), **`verdict: HARD_PASS`**, all
gates true. Its own `glass_box_note` settles the question:

> "CLIP+WordNet+QuickDraw at **INGEST only**; all T1/T2/T3 recovery runs on FHRR phasors with numpy
> bind/unbind/cleanup (**runtime glass-box, no torch/transformers**)."

Numbers **with floors**:

| Arm | Value | Floor |
|---|---|---|
| T1 picture->word top-1 | **0.635** | shuffled control **0.074**; chance **0.050** |
| T1 image-to-image anchor | 0.756 | idem |
| T2a WordNet coherence rho | **0.3532** | null mean -0.0017, **null p95 = 0.1173**, z=5.03, empirical p=0.000 |
| T2b confusable 2-way | **0.8817** | dictionary-only **0.500** (delta **+0.382**) |
| T3 scene recovery | **1.000** | shuffled **0.045** |

This is the **best-floored positive result in the entire encoder-adjacent corpus** -- every arm has
an explicit, collapsing control. CLIP is used to *build the anchors*, then discarded; inference is
numpy FHRR. **That is exactly the permitted side of the line.** Excluding it on glass-box grounds
was wrong. (`notes/STATUS.md:86-88` already carries this as correction C2 -- this investigation
confirms it independently from the metrics file.) Caveat that must travel: **20 words, K=20,
QuickDraw line drawings**; the `CLAIM-VET-pending` tag in the verdict message is still open.

Given (i) sec. 3's finding that the learned encoder adds nothing on the same-idea wall and
(ii) `grounded_similarity`'s measured inability to separate synonyms from siblings, the
**visually-grounded anchor route is the strongest un-cashed asset on disk** and should be
re-ranked, not left aside.

---

## 5. Other PASS-vs-conflicting-data cases (version attributed)

Full sweep of S1-S12 against registry / census / notes. Ordered by load-bearing.

1. **S8 encoders** -- as above. Audit measured `concept_encoder`/`vwfa`/`composed_v3` @ 2026-07-02;
   registry marks that row `superseded_by scale_win_tinytransformer_encoder`. **The string
   "tinytransformer" appears nowhere in the audit or the census.** Verdict survives; headline wrong.
2. **`scale_win_tinytransformer_encoder` -- registry status contradicts its own metrics file.**
   `status: validated_chain_grade_best_encoder` / gate `WIRE`, but the cell at its `path`
   (`v3_relobj`) is **`HARD_FAIL_ARCHITECTURE_BOUND`** (2026-07-28). The `current_best_for`
   numbers (+0.050 semantic / +0.071 relational) come from **v2** (2026-07-27 HARD_PASS), a
   *different* cell. **The row's status was measured on v2; its path points at v3.** Compounded by
   the 2026-08-12 random-init diagnostic. This row needs re-pointing or splitting.
3. **`composition` row `WIRED_AND_PIPELINE_USED` is 2/3 true.** Row bundles
   `binding.py` + `bundling.py` + `concept_encoder.py`. Runtime trace: binding and bundling **are**
   loaded; `concept_encoder` is **not**, and has zero hdlab importers. The audit's remark that
   `concept_encoder` "is the module the registry marks WIRED_AND_PIPELINE_USED" is technically
   sourced but misattributes a bundle-level flag to the one file it does not cover.
4. **Census confirms exactly three false `WIRED_AND_PIPELINE_USED` claims**
   (`notes/system_accounting_2026-08-13.md` Q2, same-day runtime trace):
   `composition`/`concept_encoder.py`; `goal_owner_select_component5_directed_score` and
   `goal_owner_full_selector_enumerate_argmax_tiebreak`, both `hdlab/goal_owner_select.py`.
   **Resolves for the runtime trace; registry stale.** Reverse direction is worse: **19 rows claim
   `WIRED_BUT_NOT_PIPELINE_REACHABLE` while measurably live** -- including
   `reading_grounding_loop_definitional_reading_pipeline`, i.e. **the pipeline entry point filed as
   not-pipeline-reachable** -- and **62 of 141 modules have no registry row at all**, including live
   entry point `grounding_acquisition_loop`.
5. **S5 goal organs -- registry says "WIRED into production", audit says the mechanism failed its
   control. Same commit both sides** (`hdlab/goal_achievement.py` @ `5c11ca697` 2026-08-09), so
   **not** version confusion. Registry row is self-contradictory: "load-bearing scoring layer ...
   WIRED into production" while its own `pipeline_status` is `WIRED_BUT_NOT_PIPELINE_REACHABLE` and
   its `coverage_caveat` records GATE-2 recovery **HARD_FAIL 0/8**. Audit's numbers: top-down
   conditioning real **0.613 vs scrambled 0.704** (below its floor), graded-utility probe **0.278 vs
   >=0.40** required. **Registry wording is the defect; audit right.**
6. **`working_memory_multibank_K_capacity` -- registry row filed against the wrong file.**
   Row claims a "multi-bank K-item capacity primitive (chain-grade K=4096)", recall 0.9927/0.9801,
   gate WIRE. `hdlab/working_memory.py` (`570e0a900` 2026-06-26) is **116 lines of envelope
   constants and guard functions -- no working memory in it**. The real implementation is
   `hdlab/situation_model_multibank.py` (`29fb97354` 2026-08-03) which has **no registry row**.
   Audit right; the passing number was measured on a cell, not on the file the row names.
7. **`cls_discrete_budget_consolidate` -- two registry rows contradict each other.** Audit lists it
   as "built, certified" (HARD_PASS gap 0.913 vs naive control). Registry
   `cls_discrete_budget_consolidate_v6_replay`: `primitive_hard_pass_synthetic_n3;
   v6_wiring_hard_fail_vet_pending`, gate **VET_PENDING** since 2026-07-28. A second row
   (`hippocampal_encoder_dg_ca3_pipeline`, 08-10, `ALREADY_WIRED`) folds the same function in as
   wired. **The certification is primitive-level on synthetic n=3; the v6 wiring HARD_FAILed.**
   The audit cites the optimistic row.
8. **S2 definitional extraction -- audit's "clearest wire case" is anchored to uncommitted code.**
   Audit: wire **YES**, 64% vs 8% control (`director_handscore_b3_v5_termboundary_2026-08-12`,
   single-judge, **not blind**). Registry: `structural_pass_pending_b3_2026-08-12`, gate
   **VET_PENDING**. Registry row is 2 module versions behind (`e01db310b` v5 F7/F8,
   `5e188ac1f` v6/v7); and `5ea354285` (2026-08-13) records **"extraction 70% -> 94%; read-out
   quality NULL; textbook hypothesis REFUTED"**. The audit's wire path sits in an **uncommitted**
   `hdlab/reading_grounding_loop.py`. **Neither side is citable without its version.**
9. **G5 "MDL gate never invoked" -- a stale FAIL still propagating across 3 notes.**
   Origin `director_three_tier_knowledge_architecture_design_audit_2026-08-11.md:232`. Refuted by
   `system_accounting_2026-08-13.md:673-677`: at HEAD `reading_grounding_loop.py:1278` **does** pass
   `mdl_gate_fn=gate` (landed `5c11ca697` 2026-08-09) -- so G5 was **already partly false the day it
   was written**. Still repeated in `multisource_lookup_wiring_audit_2026-08-13.md:284`, committed
   `fd81d9e60` the same day as its refutation. **None of the three notes carries a superseded-by line.**
10. **`false_certification_goal_typing_2026-08-13.md` -- right about history, wrong about the
    present.** Claims `verify_goal_typing.py`'s 18/18 was a broken-stemmer artefact, measured
    against `git show 5da76bf34:hdlab/thematic_role_labeler.py`. At HEAD the witness **passes in
    37.2s with `assert acc == 1.0` intact**.
11. **`uncollected_witness_audit_2026-08-13.md` reports 18 PASS / 9 FAIL**; `system_accounting`
    the same day measures **27/27 PASS**, all persisted status files `passed: true`. The note
    predates `eac20c620` / `1421c21db`. **Resolves for `system_accounting`.**
12. **S3 corroboration -- genuine fidelity-vs-score disagreement, same code both sides.** Landed
    verdict `HARD_FAIL_thin_cross_source_not_mechanism_failure` ("needs MORE independent databases,
    not different code"); audit calls it ARCHITECTURAL-FAULT (constants 1.5/0.15/0.2/2.5 chosen to
    produce the asserted behaviour; no gold-standard check). Not version confusion.
13. **S6 "NO for all ten" vs four `WIRED_AND_PIPELINE_USED` coref rows -- NOT a conflict.** The
    live coref organs (`coreference_resolver`, `situation_model_accumulate`,
    `state_of_mind`) are counted under S1, not among S6's ten. Disjoint sets; the audit explicitly
    preserves `coreference_resolver` as FAITHFUL.

14. **Two "LANDED" gated-fusion text-grounding encoder seed runs have NO metrics.json on disk.**
    `data/` holds only `exp_gated_fusion_text_grounding_encoder_seed_7_selftest/` and
    `_seed_13_selftest/`, each just `SELFTEST_PASS @ N=24 synthetic`. The landed numbers
    (seed7 sem +0.0030 / rel +0.0239; seed13 +0.0055 / +0.0282) exist **only as prose inside
    `capability_registry.jsonl`**, with **no chance or scramble floor quoted at all**. Registry
    status for the parent is `validated_hard_pass_full_8seed`. **A PASS with no artifact.**
15. **`hippocampal_encoder`: audit rates it FAITHFUL / "YES on fidelity", its own cell is a hard
    fail.** `exp_substrate_spoke3_hippocampal_encoder_smoke_2026-07-03` =
    **`HARD_FAIL_MECHANISM_LOSES`**, r@5 **0.1460** against char_trigram ref **0.854** (bar 0.8240),
    PPMI 0.9060, random 0.0073 -- it lost to the trivial trigram bag by 0.71. Registry says
    `ALREADY_WIRED` with ~20 consumers. Fidelity-rating and retrieval-verdict are both defensible
    but must never be quoted without each other; the audit quotes only the former.
16. **`concept_encoder`'s HARD_PASS is overturned by its own stress test.** Headline
    `cat/kitten cos 0.492, gap 0.472` vs excellent floors (RANDOM -0.002, TRIGRAM -0.008,
    NAIVE_WTA 0.000). But `..._spoke1_stress_test_cell1_apples_to_apples_label_shuffle_v1` =
    **MIDDLE_BAND**: a plain **softmax control scores 0.461 vs 0.492**, failing the
    "beats softmax by min" gate. The HARD_PASS is still the one usually cited.
17. **`ppmi_sparse_encoder`'s win did not survive scale.** Smoke HARD_PASS r@5 0.3400 (+0.052 over
    trigram, N=100); at 20x scale **`MEASURED_BOUND_LOW_DELTA` r@5 0.6791 = -0.0239 BELOW
    char-trigram**. Sign flip, same module.
18. **Five encoders in active use have no registry row at all:** `char_positional_encoder`,
    `token_vocab`, `late_combine`, `whitening`, `gsbc_graded_encoder` -- consistent with the
    census's "62 of 141 modules unregistered".

**Meta-caveat on all registry citations:** `data/capability_registry.jsonl` is **modified in the
working tree** vs HEAD `6d422ec98`. The 2026-08-13T09:15:02Z refresh changed `used_by` on 71 rows,
`integration_status` on 13, `pipeline_status` on 4 -- but **no `status` and no `gate_decision`
changed**. Every verdict field still dates to 2026-08-12 or earlier. The audit file itself is
**uncommitted**.

---

## 6. Recommended corrections (not applied -- this file is read-only output)

1. **Rewrite S8's headline** in `notes/brain_fidelity_subsystems_2026-08-13.md`: keep
   ARCHITECTURAL-FAULT and wire NO; replace the `learning_rate`/"nothing learned" reason with the
   2026-08-12 random-init result, and state that no encoder is on the operational path.
2. **Fix `scale_win_tinytransformer_encoder`**: its `path` points at a HARD_FAIL cell while its
   status/numbers come from v2. Re-point to `exp_scale_meaning_learn_arc_heldout_v2.py` or split
   the row, and downgrade `validated_chain_grade_best_encoder` in light of 2026-08-12.
3. **Split the `composition` row** so `concept_encoder.py` is not covered by binding/bundling's
   `WIRED_AND_PIPELINE_USED`.
4. **Re-rank the CLIP visual-grounding route** as permitted-and-best-floored; close its
   `CLAIM-VET-pending` at wider vocabulary.
5. **Add superseded-by lines** to the G5 chain and the two overturned 08-13 notes.
6. **Reconcile the registry against the runtime trace in both directions** (3 false-positive,
   19 false-negative, 62 missing rows).
7. **Produce or retract the gated-fusion text-grounding seed-7/13 numbers** -- currently a
   `validated_hard_pass_full_8seed` status backed by no metrics file on disk.
8. **Never cite `hippocampal_encoder`'s fidelity rating without its retrieval verdict**
   (`HARD_FAIL_MECHANISM_LOSES`, 0.1460 vs trigram 0.854), nor `concept_encoder`'s 0.492 without
   its softmax control (0.461, MIDDLE_BAND).

---

## 7. One-paragraph summary

The audit's S8 verdict is **directionally right and evidentially wrong**. It dissected
`concept_encoder.py` -- a module dated 2026-07-02, one commit, zero importers, not in the runtime
closure -- and correctly showed its `learning_rate` cancels, then generalised that to "the
encoders". The successor it never names, TinyTransformer v2, **does** learn: +0.1034 held-out
semantic AUC over an untrained same-architecture twin, against a 0.4964 shuffle floor. But the
successor's follow-up HARD_FAILed, its own 2026-08-12 diagnostic shows a random-init twin
*matching or beating* it on the same-idea distinction (0.7452 vs 0.7064), and it was never promoted
out of `experiments/`. The runtime trace settles the practical question: **no encoder of any
generation is on the operational path** -- concept similarity is served by a hand-typed lexicon
plus a sensorimotor-norm lookup that itself cannot separate synonyms from siblings. The strongest
un-cashed asset on disk is the CLIP-anchored visual grounding (0.635 vs 0.074 shuffled vs 0.050
chance, every arm floored, CLIP at ingest only), which the glass-box rule **permits** and which was
set aside in error.
