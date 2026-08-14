# VS Code-era assets the current plan does not know about (sweep, 2026-08-14)

READ-ONLY sweep. Nothing under `hdlab/`, `experiments/`, `verification/` was modified. No experiment
was run. `notes/STATUS.md`, `notes/STATUS_LESSONS.md`, `CLAUDE.md`, `notes/ORGAN_MAP.md`,
`notes/SUBSTRATE_STRATEGY.md`, `data/exp_structured_comparator_v1/probes/` were read, never written.
Only this file is committed.

**The question here is NOT the one settled in `notes/vscode_week_results_validity_audit_2026-08-14.md`
(`0887b54f8`).** That audit adjudicated results that were ATTACKED (~271 of 284 hold up; 11 wrongly
demoted vs 10 genuinely overstated). That is closed and is not re-litigated. This sweep asks the
complementary question: **what was measured, floored, passed, and then never attacked, never wired,
and is simply ABSENT from the current plan?**

---

## 0. ANSWER IN ONE PARAGRAPH

**There is a shelf of floored, passing, full-run results that neither `SUBSTRATE_STRATEGY.md` nor
`ORGAN_MAP.md` mentions, and three of them attack the substrate's currently-diagnosed defect
head-on.** The live read-out fails by putting a paradigmatic SISTER where the target belongs
(axon->dendrite) — a WITHIN-NEIGHBOURHOOD SEPARATION failure at read-out time. The repo already
contains (a) a read-out that lifts a collapsed argmax from **0.204 to 0.940** on real codes,
(b) a read-out whose capacity advantage is **specifically largest on CORRELATED codes** (3.25x, and
6.74x at mild correlation), and (c) a measurement that the substrate's own encoder interface
separates synonym-from-sibling at **AUC 0.7064** while the grounding path scores 0.3186. None of the
three is mentioned in either plan document. `hdlab/modern_hopfield_readout.py` and
`hdlab/dg_pattern_separation.py` exist on disk and are **NOT REACHED** by either live loop.

---

## 1. METHOD — how each known trap was defeated

Enumerated from the FILESYSTEM first, reconciled to docs after. Scripts under `scratch/`.

| trap | how it was defeated | measured |
|---|---|---|
| **Verdict-string drift** | Normalised substring match (uppercase, `-`->`_`), pass-words vs fail-words, never a literal | **329 distinct pass-flavoured verdict strings accepted**. Exact `HARD_PASS`/`PASS` filter = 2,410; normalised = 3,153. **An exact-match filter misses 743 passes (24%).** |
| **Suffix traps** | Enumerated DIRECTORIES via `os.walk`, never expected names. `_fulldev` classified as FULL, not smoke | Confirmed on both MAVEN cells (`_fulldev` + hyphenated `HARD-PASS`) and on `exp_diag_learned_encoder_synonym_sibling_deep_wall_v1`, whose `_smoke` reads `HARD_PASS_ENCODER_CROSSES_DEEP_WALL` while the FULL reads `MIDDLE_BAND_...` |
| **Dating** | Keyed on `ts_iso` INSIDE metrics.json, recursively (6 levels). mtime and git dates never used | 7,649 parsed, **0 unparseable**. 2,456 carry a date (2026-06: 386, 2026-07: 1,699, 2026-08: 371). **5,193 carry NO date field at all** — see §4, they are NOT dropped |
| **Untracked results** | Diffed the full walk against `git ls-files data/ \| grep metrics.json` | 7,630 tracked, **28 untracked**, of which **9 are pass-flavoured**, incl. 3 `HARD_PASS` (`exp_encoder_swap_behind_fixed_brain_stack_v1` + 2 smokes, 2026-08-13). **The headline comparator cell `exp_capacity_vs_format_2x2_livepath_v1` is itself UNTRACKED** (not gitignored — `.gitignore:50` `!data/*/metrics.json` negates it; simply uncommitted) |
| **Wiredness** | RUNTIME `importlib` + `sys.modules`, never grep | See §5 |
| **Floor** | Recursive key/value scan for floor/scramble/chance/random/baseline/control/lesion/naive/randinit/permut/untrained/surrogate/placebo | 3,153 passes -> **1,500 have a floor, 1,653 do NOT**. A number with no floor is ranked below anything floored |

**Reconciliation to the plan.** Of the 1,500 floored passes, `SUBSTRATE_STRATEGY.md` mentions **2**
and `ORGAN_MAP.md` mentions **13**; **1,485 are mentioned in neither.** So *invisibility is the norm,
not the signal* — the plan docs are curated prose, they do not name cells. Ranking therefore uses
topical relevance to the live scoreboard, not invisibility alone. 554 floored passes carry a
C3/separation/comprehension token; 337 distinct cell-stems; the shortlist below is the top of that
ranking, hand-verified against primary metrics.

---

## 2. RANKED RECOVERED ASSETS

Rank = (has a real floor) x (survives to HEAD) x (serves a live scoreboard number).
Live scoreboard: C1 near-neighbour 2AFC **0.698**; C2 context gap +0.1005;
**C3 read-out quality 4.80% vs 0.80% floor — THE GATE, 5.2pp short of 10%**; C4 coref 0.7193.

### TIER 1 — plausibly serves C3 or the SEPARATION defect (these rank above everything else)

**A1. `exp_encoder_peel_sic_readout_realcodes_v1`** — `HARD_PASS_PEEL_SIC_TRANSFERS_TO_REAL_CODES`,
`ts_iso 2026-07-08T17:28:40Z`, **FULL**, 5 seeds (7/13/19/23/29), tracked.
**Floor:** flat argmax = **0.204** (declared collapsed if <=0.7); confidence-ordered peel/SIC readout
= **0.940**, lift **+0.736** against a stated bar of >=+0.2 AND abs>=0.6 AND cv<=0.15 (cv=0.034);
lift persists at deeper J (+0.778). **Plan: MENTIONED IN NEITHER.** Registry: `peel_sic` present.
**SERVES C3 — the strongest single candidate in this sweep.** C3's failure mode is precisely a
*flat/collapsed argmax over confusable candidates*: the substrate picks a sister because the argmax
cannot separate within the neighbourhood. This cell measures exactly that pathology on REAL codes
(not clean synthetic ones — it is explicitly a transfer test) and reports a 4.6x lift from replacing
argmax with confidence-ordered successive-interference-cancellation peeling. It is a read-out-time
mechanism, which is where the C3 defect is diagnosed to live.

**A2. `exp_dense_hopfield_readout_capacity_correlated_codes_v1`** — `HARD_PASS` /
`CAPACITY_LIFT_REAL`, `ts_iso 2026-07-14T00:42:50Z`, **FULL**, seeds 7/13/19, tracked.
**Floor:** scramble collapses to **0.01**; pairwise baseline explicit per cell; iid positive control
5.48x. Headline **3.25x** capacity lift over pairwise on the substrate's CORRELATED codes against a
declared >=1.5x bar. Per-correlation: `corr_mild 6.74x, corr_mod 3.12x, corr_strong 1.63x`.
**Plan: MENTIONED IN NEITHER.** Registry: no `dense_hopfield` row.
**SERVES C3 AND SEPARATION.** Sisters ARE correlated codes — that is what "same neighbourhood"
means geometrically. This is the one recovered result whose advantage is *defined on the axis the
defect lies along*. Caveat stated honestly: the lift SHRINKS as correlation strengthens
(6.74 -> 1.63), so it is a partial, not a solution, in the very regime C3 needs most.

**A3. `exp_diag_learned_encoder_synonym_sibling_deep_wall_v1`** — FULL verdict
`MIDDLE_BAND_INTERFACE_SEPARATES_BUT_NOT_LEARNING`, `ts_iso 2026-08-12T03:10:56Z`, **FULL**, tracked.
**Floor:** scramble **0.5042** (collapses to chance); grounding_AUC_matched **0.3186**;
**randinit same-arch encoder 0.7452**. Trained encoder AUC **0.7064** (d'=0.752), clears the declared
>=0.65 bar and beats the grounding path — **but the untrained random-init encoder on the SAME
corpus-mention-pooling interface scores EQUAL OR BETTER.**
**Plan: MENTIONED IN NEITHER.** Registry: no row.
**SERVES SEPARATION — and it is a POSITIVE result being carried as a negative one.** The honest
reading is not "the encoder fails". It is: **the distributional-context POOLING INTERFACE separates
synonym from sibling at AUC ~0.74, for free, without training.** That interface is owned, glass-box,
no-external-LLM, and it is currently NOT the interface the read-out uses. The `randinit >= trained`
result kills the *learning* claim; it does not kill the *interface* claim, and the interface claim is
the one C3 needs. This is the single most likely mis-filed asset in the sweep.
*Trap note:* the `_smoke` sibling reads `HARD_PASS_ENCODER_CROSSES_DEEP_WALL` (AUC 0.7175). Do not
cite the smoke — the FULL is MIDDLE_BAND and the difference is the randinit control, which is the
whole point.

**A4. `exp_substrate_anisotropy_dg_pattern_separation_prewrite_v1`** — `HARD_PASS`, **FULL**, real
Pythia-2.8b keys, 3 seeds (11/13/19). **NO `ts_iso`** (see §4; git-add date places it in the
July arc). Tracked.
**Floor:** `uniform_no_presep` collapses to **0.083**; dg_full **0.942** vs a declared >=0.50 bar;
lift_over_uniform 0.859 (>=0.20); effrank lift 10.08x (>=1.30x); std 0.004; knn sentinel 1.000.
Off-diagonal mass 0.179 -> 0.012.
**Plan: ORGAN_MAP mentions the topic; SUBSTRATE_STRATEGY does not.** Registry: `pattern_separation`
present. **RUNTIME: `hdlab/dg_pattern_separation.py` EXISTS and is NOT REACHED by either live loop.**
**SERVES SEPARATION DIRECTLY.** This is a pattern-separation organ applied AT WRITE TIME that
decorrelates representations by an order of magnitude in effective rank on real model keys. The C3
defect is that sisters are not separated. This is the brain's own answer to that (dentate gyrus), it
is landed, and it is not in the live path.

**A5. `exp_semantic_hd_encoder_meaning_match_v1`** — `MEANING_MATCH_PASS`,
`ts_iso 2026-07-24T15:37:47Z`, **FULL**, tracked.
**Floor:** lexical separation **-0.400** (i.e. the surface-form control is worse than nothing);
semantic AUC **0.960**, semantic separation **0.507**, gap **0.907**. Downstream ARC climb
0.354 -> 0.396 (+0.042) vs scramble +0.149.
**Plan: MENTIONED IN NEITHER.** Registry: no `meaning_match` row.
**SERVES SEPARATION.** A separation of 0.507 against a lexical floor of -0.400 is a large,
well-floored margin on exactly the meaning-vs-surface axis. Worth re-pointing at the C3 candidate set.

**A6. `exp_substrate_iterative_cleanup_cue_clamped_v1`** — `HARD_PASS`, **NO `ts_iso`**, no
`run_mode`, tracked. **WEAKEST of Tier 1 — flagged accordingly.**
**Floor:** ARM_SINGLE_STEP **0.1500**; ARM_CURRENT (alpha=0) **0.1250**. Best clamped arm
alpha=0.3 -> **0.2250**, lift +0.0750 against a >=0.05 bar, CV 0.0000.
**Plan: MENTIONED IN NEITHER.** Registry: no `cue_clamped` row.
**SERVES C3, WITH A REAL CAVEAT.** Cue-clamping is a brain-canonical fix for multi-iteration cleanup
drifting off the cue — a plausible mechanism for "right neighbourhood, wrong member". But the
absolute numbers are low (0.225) and the cell's OWN `WHAT_THIS_DOES_NOT_SHOW` field states it is
unproven at production N=8192. Cite as a lead, never as evidence.

### TIER 2 — floored and passing, does NOT serve C3/separation, invisible to the plan

| cell | verdict | ts_iso | floor | plan |
|---|---|---|---|---|
| `exp_teacher_free_relational_encoder_cn_subgraph_v1` | `HARD_PASS` | 2026-07-08T15:34:29Z | random-init Z=**148.97**, control Z=21.42, ablation collapses; arm Z=**497.90**, 5 seeds | NEITHER; no registry row |
| `exp_visual_grounding_coherence_v1` | `HARD_PASS` | 2026-07-18T13:50:41Z | chance **0.050**, shuffled **0.074**; T1=**0.635**; T2a null95 0.117 vs rho 0.353 (z=5.03); T2b delta +0.382 | ORGAN_MAP only; **NO registry row** |
| `exp_vision_integrated_recognize_bind_ground_v1` | `HARD_PASS_INTEGRATED_PIPELINE__NOVEL_CLASS_WALL_CONFIRMED` | 2026-07-23T12:02:20Z | chance 0.125, label-shuffle 0.189, SCRAM 0.386, word-scramble 0.143 | NEITHER |
| `exp_reader_image_word_grounding_v1` | `PASS_GROUNDING` | 2026-07-22T00:28:57Z | chance **0.0169**; rung1 0.996 / rung2_edge 1.000 / rung2b_ink 0.977 | NEITHER |
| `exp_maven_ere_convergence_gated_causal_v2_fulldev` | `HARD-PASS` | 2026-08-11T09:19:45Z | floor **5.93**, scramble **3.48**, full_v2 **14.78** | NEITHER |
| `exp_maven_ere_convergence_gated_subevent_v1_fulldev` | `HARD-PASS` | 2026-08-11T10:06:27Z | floor **2.86**, scramble **2.78**, full_v2 **13.63**, transferred=True | NEITHER |
| `exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1` | `HARD_PASS` (`CHAIN_GRADE_K_4096`) | **NO DATE** | naive random recall **0.0172** vs multi-bank **1.0000**, cv 0.0000, route_acc 1.0000, adversarial within 0.05 | ORGAN_MAP only. **RUNTIME: `hdlab/situation_model_multibank.py` NOT REACHED** |
| `exp_read_grow_relation_identity_v3_richness_sweep` | `HARD_PASS` | 2026-07-17T04:48:28Z | failure-rate curve 0.267 -> 0.000; ablation control fired at all levels | NEITHER |
| `exp_grounding_gated_fusion_relation_inference_mammal_v1` | `HARD_PASS_GATED_FUSION_RECOVERS_GROUNDING` | 2026-07-14T03:26:29Z | RANDOM **0.0275**, SCRAMBLE 0.5682, ORACLE 1.0; gated MRR 0.6619 vs relational 0.3645 | NEITHER |
| `exp_lexicon_learned_grounding_scaled_v1` | `HARD_PASS` | **NO DATE** | RANDOM **0.010** vs LEARNED 0.940 vs ORACLE 1.000 at V=200 | NEITHER |
| `exp_social_relational_grounding_axis_v1` | `HARD_PASS` | 2026-08-07T10:35:52Z | scramble 0.483, ablation 0.000; open-vocab 0.833. **n=12 seed / 6+6 test — UNDERPOWERED, rank low** | NEITHER |
| `exp_joint_operator_capstone_selective_readouts_v1` | `HARD_PASS_..._NO_INTERFERENCE_HEADDISC_CLEAN` | 2026-07-15T23:36:19Z | chance 0.52 / SHUF 0.4222; joint 0.9980 & 1.0000, 6 gates all True | NEITHER |
| `exp_metacog_abstain_readout_signal_thresholding_v1` | `HARD_PASS_EXISTING_SIGNAL_CARRIES_USABLE_CONFIDENCE` | 2026-07-20T02:08:36Z | rand_p2.5 0.6619, base_wrong 0.7324; best rel_reduction 0.327 at cov 0.5. **2 of 4 tiers HARD_FAIL** | ORGAN_MAP only |
| `exp_grounded_inductive_concept_encoder_heldout_new_v3` | `HARD_PASS` | 2026-07-26T16:22:42Z | aa_poor 0.4403 vs enc_poor 0.6741 (+0.2339 vs >=0.03 bar), n=2024 power_ok | NEITHER |
| `exp_cleanup_floor_learned_encoder_v1` | `META_BRANCH3_CHAIN_GRADE_ELIGIBLE` | **NO DATE** | Shannon floor holds across 3 codebook families (0.0217 / 0.0267 / 0.0150, all <0.10) | NEITHER. *This is a NEGATIVE-shaped positive: it establishes a FLOOR others can be scored against* |

---

## 3. THE 0.6980 / 0.69975 / 0.6997 RECONCILIATION

**It is TWO DIFFERENT ARMS, not a rounding convention. The number to use everywhere is 0.698.**

Decisive evidence: `data/exp_graded_divisive_comparator_v1/metrics.json` carries BOTH values as
SEPARATE KEYS IN THE SAME `arm_accuracy` DICT of the SAME FILE, same n=4000, same n_anchors=2377,
same items — so it cannot be rounding, and cannot be an n/dedupe difference:
- `arm_accuracy.A_GGN` = **0.698**  (graded, NORM = **none**)
- `arm_accuracy.A_GGZ` = **0.69975** (graded, NORM = **Z** = centre+scale divisive normalisation)

Confirmed in the primary cell: `data/exp_capacity_vs_format_2x2_livepath_v1/metrics.json` ->
`arm_accuracy.A_d256_GRAD` = **0.698** exactly (and `A_d256_QUANT` = 0.6395,
`A_d1024_QUANT` = 0.703, `A_d1024_GRAD` = 0.7495). Its `verdict_msg` states
`F256=+0.0585 CI[+0.0422,+0.0745]`, and 0.6395 + 0.0585 = **0.6980**.

**The Z arm was not shipped.** `hdlab/reading_grounding_loop.py:526` is
`def freeze_graded(self, normalise: str = "none")` — the Z pool-norm is OFF by default, and its own
docstring calls the normalisation NULL (+0.0018, CI [-0.0030, +0.0065]).

Therefore:
- `SUBSTRATE_STRATEGY.md` PART 1 line 74 (**0.6980**) is **CORRECT**.
- `SUBSTRATE_STRATEGY.md` PART 2 STEP 4's caveat (**0.69975**) quotes the **non-shipped Z arm**.
- `vscode_week_results_validity_audit_2026-08-14.md` (**0.6997**) is the 4-dp rounding of that same
  non-shipped Z arm, and its stated delta `+0.0602 CI[+0.0440,+0.0762]` belongs to the Z arm, not the
  live path. The live-path delta is **+0.0585 CI[+0.0422,+0.0745]**.

Not edited here, per instruction — reported only. Also noted: commit `38f7a0d5c`'s own message
headlines "0.6395 -> 0.7495" for the live path; 0.7495 is `A_d1024_GRAD`, a dimensionality arm, and
was not shipped. This matches the banner's existing correction.

---

## 4. THE 5,193 UNDATED RESULTS — how they were handled, NOT DROPPED

5,193 of 7,649 metrics.json carry **no date field anywhere** (searched `ts_iso`, `timestamp_iso`,
`ts`, `run_ts`, `started_iso`, `start_iso`, `finished_iso`, `completed_at`, `date`, recursively to
6 levels). They are an older cell-template that predates the `ts_iso` convention. **They were kept in
the sweep, not filtered out** — three Tier-1/Tier-2 assets above are undated
(`..._dg_pattern_separation_prewrite_v1`, `..._multi_bank_K_extension_adversarial_v1`,
`exp_cleanup_floor_learned_encoder_v1`, `exp_lexicon_learned_grounding_scaled_v1`).

For those, the note states **NO DATE** explicitly rather than substituting mtime or a git date, both
of which are known to lie here (mtime drifted 24 days; git-add dates over-count the window ~12x).
Their era is inferred only from cell-template and neighbouring content, and that inference is
labelled as inference. **NOT DONE:** per-file dating of the undated 5,193 from `_start_marker.json`
siblings or run logs. That is the largest remaining gap in this sweep and it is the natural next
step if the shelf is worked.

---

## 5. WIRED-NESS, BY RUNTIME

Measured by `importlib` + `sys.modules`, never by grep.

- `import hdlab.reading_grounding_loop` -> **39** `hdlab.*` modules in `sys.modules`
- `+ import hdlab.grounding_acquisition_loop` -> still **39** (the acquisition loop adds no new
  hdlab module beyond the reading loop's closure)
- `hdlab/*.py` on disk: **143**. Reached by the two live loops: **31**.

**Organs that EXIST on disk but are NOT REACHED** (directly relevant to §2):
- `hdlab/dg_pattern_separation.py` — the A4 organ. EXISTS, NOT REACHED.
- `hdlab/modern_hopfield_readout.py` — the A2 organ. EXISTS, NOT REACHED.
- `hdlab/situation_model_multibank.py` — the multi-bank WM organ. EXISTS, NOT REACHED.
- Also unreached: `hdlab/encoder_retrain_persist.py`, `hdlab/concept_encoder.py`,
  `hdlab/composed_encoder_v3.py`, `hdlab/coref.py`, `hdlab/bundle_focus_coref.py`,
  `hdlab/coref_distractor_suppress.py`, `hdlab/event_centrality_coref.py`,
  `hdlab/definitional_extraction.py`, and ~100 more.

**Reached:** `hdlab.cleanup_family`, `hdlab.coreference_resolver`, `hdlab.animacy_lexicon`,
`hdlab.closed_class_lexicon`, and 27 others.

**MANDATORY CAVEAT — this measures the DEFAULT path, NOT EXISTENCE.** A top-level import does not
see lazy imports inside function bodies (e.g. `reading_grounding_loop.py:300-303`), and it does not
see opt-in modules gated behind a flag or kwarg. `hdlab/encoder_retrain_persist.py` is the known
precedent: it is landed and functional but OPT-IN BY DESIGN, and a default-path trace was previously
mis-reported as proving no encoder exists. **NOT-REACHED above therefore means "not on the default
path", NOT "does not exist" and NOT "cannot be reached".** EXISTS / IS-REACHED / IS-GOOD are three
separate questions and are kept separate here. **NOT DONE:** per-module classification of
UNREACHED into genuinely-islanded vs reachable-but-lazy vs opt-in-with-a-named-flag.

---

## 6. REGISTRY STATUS

`data/capability_registry.jsonl`: **127 rows**, 37 distinct fields. Assets above with **NO registry
row at all**: visual grounding / CLIP, teacher-free relational encoder, dense Hopfield readout,
meaning-match encoder, cue-clamped cleanup, anisotropy rescue, read-grow relation identity,
metacog abstain, joint operator, learned lexicon grounding. Absence from the registry is common
(the standing audit records 62 of 141 modules unregistered) and is itself the finding, not a defect
of any individual asset.

---

## 7. WHAT IS NOT DONE

Stated explicitly so the gap is visible rather than silently absent:
1. Dating of the 5,193 undated results from sibling markers or run logs (§4).
2. Per-module UNREACHED triage: islanded vs lazy vs opt-in-flag (§5).
3. Supersession analysis: for each Tier-1 asset, whether a LATER cell superseded it and whether that
   later cell KEPT or CHANGED the task. **Partially done only** — A3's smoke/full relationship is
   established, and A4's ORGAN_MAP presence is established. The other Tier-1 assets are reported as
   floored-and-passing **at their own run date**, and no claim is made here that they survive
   unchallenged to HEAD. That check must be run before any of them is acted on.
4. The 1,653 floored-absent passes (passes with NO floor) are ranked below everything here and were
   not individually examined. They are not evidence.

---

## 8. RECOMMENDATION (one line)

If the shelf is worked, work **A1 (peel/SIC read-out)** and **A2 (dense Hopfield on correlated
codes)** first, and re-read **A3** as an interface positive rather than a learning negative — those
three are the only recovered assets that attack C3's diagnosed within-neighbourhood separation
defect at the place it occurs. Confirm supersession (§7.3) before shipping anything.
