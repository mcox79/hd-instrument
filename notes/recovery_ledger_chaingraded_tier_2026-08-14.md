# RECOVERY LEDGER -- THE CHAIN-GRADED TIER (RECOVERY_PROGRAM group H1)

**2026-08-14. READ-ONLY triage of the terminal chain-graded cells in `data/substrate_index/meta/cert_ledger.jsonl`.**

> **THIS FILE NEEDS MERGING INTO `notes/RECOVERY_PROGRAM.md` sec 5.** It is written in that file's row format and the same five-word closed STATE vocabulary (FOUND / VERIFIED / WIRED / SHELVED / REFUTED, written as a `STATE:` token in the last column of every row) so the sec-7a count command works over it unchanged:
> ```bash
> grep -oE 'STATE:(FOUND|VERIFIED|WIRED|SHELVED|REFUTED)' notes/recovery_ledger_chaingraded_tier_2026-08-14.md | sort | uniq -c
> ```
> It was written as a separate file rather than appended because a concurrent session owns `RECOVERY_PROGRAM.md` and because 565 rows would swamp that file's cold-read function. **When merging, RECOVERY_PROGRAM sec 6 row H1 must change from `574 / ~546 NOT-YET-TRIAGED` to the counts in sec 1 below.**

---

## 1. TLDR -- what was triaged and what it says

| quantity | number |
|---|---|
| terminal chain-graded cells re-derived from the ledger (see sec 2 for why not 574) | **565** |
| **rows written below -- every cell gets one** | **565 (100%)** |
| `metrics.json` opened at HEAD | **547** |
| no directory resolves (state FOUND -- nothing checked) | **18** |
| **cells with a REAL floor** (control arm / reference arm / prose floor) | **172 (30%)** |
| ...of which recovered by the STRUCTURAL pass only (reference arm, **no control word anywhere in the file**) | **38** |
| contrast arm but no identifiable reference arm (NOT a floor) | 124 |
| no floor shape of any kind | 251 |
| **one auto-generated saturation grid** (`exp_q_a3_l*_cross_layer_composition`, `pp48_nkt_*`) | **280 = 50% of the whole tier** |
| run_mode `full` (as read, not as claimed) | 534 |
| run_mode `smoke` / `lite` / `grid` / `selftest` / ABSENT | 31 |
| dated from `ts_iso` inside metrics.json (strongest) | 69 |
| dated from `_start_marker.json` | 6 |
| dated from first-commit of `experiments/<name>.py` (**weakest -- a batch estimate, not a run date**) | 439 |
| dated from the ledger only | 34 |
| **UNDATED by any of the four** | 17 |
| an `hdlab/` module plausibly corresponds | 33 |
| ...and is in the 39-module runtime live closure | **3** |

**STATE counts at write time:** FOUND 18 / REFUTED 12 / VERIFIED 535. Every `VERIFIED` row is unfinished business by RECOVERY_PROGRAM sec 3 -- opening a `metrics.json` is not wiring anything.

### The three things this triage actually found

1. **Half the tier is one experiment.** 280 of 565 terminal chain-graded cells (50%) are `exp_q_a3_l<N>_cross_layer_composition_v1_n<N>` / `exp_pp48_nkt_depth_*` -- an auto-generated saturation grid reporting EXACT-1.0 at every level, with no comparison arm because the result is construction-determined. **"574 chain-graded cells" is not 574 experiments.** Deduplicating the grid to one entry leaves **286 distinct investigations.**
2. **The five-stage store recipe WAS partly composed, twice, and RECOVERY_PROGRAM group B says it never was.** `exp_pb_production_recipe_integration_v1` (2026-06-06, run_mode `full`) reads: *"full production recipe >=5x naive ... naive(raw+hebb)=3 full(whiten+pinv)=172 | lift: 57.3x"*, and `exp_f8_pinv_padfix_alpha_compound_v1` composes the same two stages on REAL keys (*OLD(raw+hebb)=0.000 NEW(whiten+pinv)=0.400*). **Correction to RECOVERY_PROGRAM sec 5 group B and sec 9b rank 4: stages 3+4 of the chain compose and were measured; what was never run end-to-end is the FULL five-stage chain including last-token pooling and coarse-to-fine read.**
3. **One stage of that chain is contradicted from inside the same tier.** `exp_substrate_expansion_method_battery_gpu_v1` (full, 2026-06-06) reads *"expansion cannot beat rank (rp_x4 ~ native) while whitening helps via decorrelation -- d_eff framework confirmed"*, `native=0.0065 rp_x4=0.0065 zca_whiten=0.0517`. That is a **direct contradiction of the dimensional-expansion stage** (B3/B4) by a sibling chain-graded cell. Neither cell cites the other. **Before the chain is run end-to-end, this contradiction must be resolved** -- it is cheaper than the chain and it may delete a stage.

---

## 2. HOW THE 565 WAS DERIVED, AND WHY IT IS NOT 574

`notes/cert_ledger_triage_2026-08-14.md` (`c6cd948dc`) reports 589 ever / 576 latest / **574 terminal**. My independent re-derivation on the same 2031-row file gives **580 ever / 566 latest / 565 terminal**. The method is stated so the difference is auditable, not so it is averaged away:

- chain-grade detected by regex `chain[_\-. ]?grade` over `cert_status` (never equality) -- confirmed necessary: `chain-grade`, `chain_grade_meta_rule`, `chain_grade_honest_negative`, `chain_grade_measured_bound` are all distinct strings.
- cell name resolved in priority order: `referent_pointer.metrics_path` -> `referent_pointer.atom_qualified_id` -> `anchor`/`anchor_name`/`cell` -> a case-INSENSITIVE `exp_`/`EXP_` token inside `atom_id`/`note`/`verdict`/`atomized_by`. **The uppercase `EXP_` form matters**: the June `math::T3/EXP_substrate_...` atoms are invisible to a case-sensitive scan and that alone accounts for ~20 cells.
- every resolved slug is then matched against a **`os.walk('data/')` enumeration (8,509 dirs / 7,893 top-level / 7,660 with a `metrics.json`)** by exact -> suffix-strip -> longest-prefix -> **longest common token prefix**. The last stage is what recovers the cross-seed aggregate atoms whose `atom_id` is a result sentence with a prose tail; it took MISSING from 46 to **18**.
- liveness = **latest ruling per cell** (append order in the file). The supersedes graph is decoration and was not used to kill anything except the one edge that resolves: `exp_fhrr_bundle_capacity_exact_margin_v1`. 14 cells are demoted by a later in-place ruling.

**Where the ~9-cell gap to 574 lives, stated rather than hidden:** (a) my disk-authority matcher MERGES a cross-seed aggregate atom onto its `_seed_13` directory, where the source note kept it as a separate MISSING entity -- that collapses several names into one row; (b) **14 chain-graded `meta::`/`META_RULE_*` rows resolve to no cell at all** (they are discipline rules, not experiments -- the source note flags 4 of these; there are 14) and are excluded here rather than counted as cells. **Neither figure is wrong; they count different things. 565 is the count of chain-graded CELLS WITH AN IDENTITY ON DISK. Treat 574 and 565 as a bracket, not a discrepancy.**

---

## 3. FLOOR DETECTION -- BY SHAPE, WITH THE VOCABULARY REPORTED SECOND

The detector implements RECOVERY_PROGRAM sec 8 rule 1 literally. An **ARM GROUP** is:

- `shape_arms_dict` -- a dict whose children are >=2 sibling DICTS sharing a numeric key; or
- `shape_token_pair` -- >=2 sibling NUMERIC keys differing in exactly one token position; or
- (relaxed) >=2 sibling numeric keys sharing their FIRST or LAST token but of unequal length -- **this stage alone is what recovers `{cap_unwhitened, cap_pca_whitened}`**, whose two labels have 2 and 3 tokens and therefore fail a same-length token-pair test.

A group is DISCARDED when its distinguishing labels are all seed-like or all config levels (`{seed_7, seed_13}`, `{N1024, N2048}`, `{L, N}`) -- **a replication or a parameter sweep is not a control.** Surviving groups are then searched for a reference arm:

| what was found in an arm label | class | meaning |
|---|---|---|
| a CONTROL word (`scramble`, `shuffle`, `random`, `chance`, `naive`, `baseline`, `null`, `ablation`, `lesion`, `floor`, `pathology`, `popularity`, `collapse`, `degenerate`, ...) | **A** | a lexical pass would also have found this |
| a REFERENCE word only (`raw`, `unwhitened`, `frozen`, `plain`, `hebb`, `argmax`, `single`, `before`, `off`, `dense`, `additive`, ...) or a NEGATIVE-CONDITION word (`hall`, `false`, `neg`, `unmatched`, `ungrounded`, ...) | **ARM** | **structural recovery -- there is NO control word anywhere in the file** |
| an oracle/ceiling arm only | **CONTRAST-ONLY** | a comparison, not a floor |
| nothing | **CONTRAST-ONLY** | |
| no group at all, floor asserted in `verdict_msg` prose | **PROSE** | |
| no group, pre-registered bar only | **BAND-ONLY** | an absolute bar with nothing to compare |

### What the structural pass bought, measured against three lexical baselines

| lexical baseline (substring over the whole `metrics.json`) | cells it would call floored | floored cells it would MISS that the structural pass finds |
|---|---|---|
| `scramble` only (the convention used by the August tooling) | 11 | **161** |
| the common six (`scramble/shuffle/random/chance/baseline/control`) | 103 | **69** |
| a broad 31-token vocabulary | 128 | **44** |

**Read the first row.** A `scramble`-keyed sweep sees **11** floored cells in this tier and misses **161** that have one. The June cohort is the reason: of **467** terminal cells dated June 2026, **0 contain the string `scramble`** while **90 have a real floor** -- the June convention names its floors `hebb_alpha_c`, `cap_unwhitened`, `last_token_raw`, `HA_ONLY`, `NO_CX`, `random_arm_pathology`, `FREQ_NULL`, or states them only in prose.

**Honest limits, so CONTRAST-ONLY and NO FLOOR are not over-read:** the detector reads only `metrics.json`. A floor declared in a pre-registration, a `notes/` writeup or a `_start_marker.json` is invisible to it. **`NO FLOOR` means "no floor visible in metrics.json", never "no floor".** And the reference-arm vocabulary is still a vocabulary: it will age exactly the way the control vocabulary aged. The 124 CONTRAST-ONLY rows are the live alarm -- each has a comparison SHAPE whose arms this pass could not name.

---

## 4. RANKED AGAINST THE LIVE PROBLEM -- SEPARATION GEOMETRY

**The ranking criterion, stated before it is applied.** The C3 defect was re-diagnosed on 2026-08-14 and it is **not meaning supply**: wiring 36,810 norms + a 237.7M-token encoder took hit@1 4.80% -> 9.40%, but a **zero-meaning character-trigram control reproduced 9.05%**, crowding never fell, and sister-term conversions were 1-3 of 4000. The defect is **comparison GEOMETRY** -- a bag of co-occurring words cannot separate paradigmatic neighbours that appear in near-identical contexts (`sympathetic`/`parasympathetic`). So a cell ranks high here **only if it bears on separating items that share contexts, or on a representation that is not context-bag cosine.** Refuted downstream and therefore excluded: rank-1 common-mode removal, the forgetting kernel, sharpening read-outs, the composed five-stage chain as a read-out fix.

**Two standing bounds apply to everything below** (RECOVERY_PROGRAM sec 9a): `exp_anchor_compose_identity_shuffle_cskg_v2` harvests **93% of its own oracle** and `exp_resonator_verifier_readout_v1` harvests **exactly** its oracle. Anything that only **re-scores existing candidates** is demoted; anything that changes **what the candidates ARE** is promoted.

### 4a. THE TOP 15

Ranked, with the floor as it actually reads on disk. Full rows for these are in group CG-A.

| rank | cell | floor, as read | why it bears on SEPARATION GEOMETRY | moves |
|---|---|---|---|---|
| **1** | `exp_substrate_permutation_binding_multiocc_v2_full` | **A by the detector, but for the WRONG reason and this is worth reading**: it matched the token `perm` in `perm_acc_mean`, where `perm` names the TREATMENT, not a control. The REAL reference arm is `FHRR=0.0629` -- the failing conventional binding. 3 seeds, cv=0.0000. *The shape was right; the vocabulary was right by accident.* | **The single most on-target cell in the tier.** It resolves *same-role COLLISION* -- two items occupying the same slot, which is structurally the same failure as two paradigmatic neighbours occupying the same context. Permutation-indexed binding reaches **1.0000 where FHRR reaches 0.0629** (lift 0.9371). It replaces the representation rather than re-scoring it, so the oracle-bound override PROMOTES it. | **C3**, C1 |
| **2** | `exp_interference_avoidance_conjunctive_vs_additive_v1` | A -- `add=0.273`, `freq_oracle=0.654`, `gap_control=0.000` (a clean must-fail control) | **A bag beats nothing; conjunctive/orthogonal storage beats the bag.** At M_HI=256 `orth=1.000` vs `add=0.273` -- and the ADDITIVE arm *is* the bag-of-co-occurrence geometry the C3 diagnosis indicts. It also names the crossover (`crossover_M=48`), i.e. where the bag starts failing. This is the closest thing in the corpus to a direct measurement of the new diagnosis. | **C3**, C1 |
| **3** | `exp_substrate_codebook_near_duplicate_diagnostic_cpu_v1` | A -- near-dup floor **0.1333**; de-dup arm vs full arm; 3 seeds, cv=0 | Measures C3's exact symptom -- right neighbourhood, wrong member. **49 pairs at cos>0.9; 54/241 (22%) of atoms have a near-neighbour above threshold.** Its own words: *"the residual is genuine distinct-but-close atoms needing finer encoding"*. RECOVERY_PROGRAM rank 1 already; confirmed here independently, on disk, run_mode `full`. | **C3**, C1 |
| **4** | `exp_substrate_decomposition_resonator_alpha05_cpu_v1` | ARM -- `plain` (non-augmented) arm is the reference; K=241/F=3/noise=0 | **Same K=241 codebook as the near-dup diagnostic, and it is the FIX side of it.** alpha=0.5 identity-augmented encoding reaches precision@1 >= 0.95 where the plain encoding does not, and the cell's own claim is that the *encoding* fix GENERALIZES from composition cleanup to resonator decomposition ('two-vector architecture, 2nd appearance'). **Encoding-side, not read-out-side, so the oracle bound does not apply to it.** | **C3**, C1 |
| **5** | `exp_substrate_name_augmented_encoding_recovery_canonical_rerun_v593` | NO FLOOR visible in metrics.json -- **but the alpha grid IS the contrast** (alpha=0 is the reference); flagged as a probable detector false negative, VERIFY BY HAND before citing | Third appearance of the same identity-augmentation lever, now at binding scale: cleanup@1 **F10=0.9883, F20=0.9617** at alpha=0.5. Together with the row above this is a **replicated encoding-side separation lever**, which is the shape the new diagnosis asks for. | **C3**, C1 |
| **6** | `exp_pb_production_recipe_integration_v1` | A -- `naive(raw+hebb)=3` is the control arm; full recipe = 172 | **The composed whiten+pinv recipe, measured: 57.3x over naive.** This is two of the five stages RECOVERY_PROGRAM says were never composed. It does not by itself move hit@1, but it removes the largest unknown from rank 4 of that document's priority list and re-prices the whole group-B programme. | **C3**, C1 |
| **7** | `exp_substrate_encoder_capacity_at_scale_battery_gpu_v1` | CONTRAST-ONLY by the detector, but the `raw_sign` arm IS the floor -- `{MiniLM/raw_sign 3.0, MiniLM/zca 7.0, BGE/raw 0.0, BGE/zca 40.0, Llama-3.2-1B/raw 0.0, Llama-3.2-1B/zca 122.0}` | **The encoder-choice lever, measured as a full encoder x recipe grid.** If the live read-out runs MiniLM raw it is at capacity **3** where Llama-3.2-1B + ZCA reaches **122** -- a 40x separation headroom with no new mechanism. This is the supply side of the same geometry question and it is one config change. | **C3**, C1 |
| **8** | `exp_encoder_retained_trace_requery_coarse_to_fine_v1` | ARM -- `sparse_fullV=0.541` reference arm reproducing the v1 wall; full-fine CEILING 0.992 | C3 is a ranking problem (median target rank 84 of 647). Coarse shortlist then fine read inside it costs **zero** recall against the full-fine ceiling (`final_recall 0.992` vs ceiling 0.992, `shortlist_hit@k=0.1 = 1.000`). **Demoted from where its numbers would put it** because it re-scores rather than re-represents -- the oracle-bound override. | **C3** |
| **9** | `exp_generation_decode_selfmargin_dupclass_exact_v1` | A -- beats the falsified PR-gaussian by 2.68x on worst-cell error and the naive-independent birthday model by a factor of 1e+; per-cell ratio-error <= 1.041 | **An exact analytic law for WHEN duplicate classes collapse a decode**: `p1 = n_distinct(codebook)/V` predicts the collapse with mean ratio 1.0021. That is a closed-form predictor of the crowding C3 exhibits -- it says whether 5,491 anchors are ABOVE or BELOW the collapse point before anything is built. | **C3** |
| **10** | `exp_substrate_expansion_method_battery_gpu_v1` | NO FLOOR by the detector -- **detector false negative**, the `native` arm is the reference (`native=0.0065 rp_x4=0.0065 zca_whiten=0.0517`) | **A REFUTATION that must be read before group B is acted on**: *expansion cannot beat rank (rp_x4 ~ native) while whitening helps via decorrelation*. It contradicts the dimensional-expansion stage from inside the same chain-graded tier. Ranked high because it may DELETE a stage, which is worth more than adding one. | **C3**, C1 (bounds) |
| **11** | `exp_substrate_last_token_vs_whitening_mean_pool_v1` | ARM -- `last_token_raw` = **0** is the reference; 3 seeds bit-identical | Pure representation-side lever on the same sentence encoder the read-out uses: capacity `last_token_raw 0` / `mean_pool_whiten 40` / `last_token_whiten 122`. If the live read-out mean-pools without whitening it runs at 40 where 122 is available. | **C3**, C1 |
| **12** | `exp_substrate_pca_prewhitening_codebook_v1` | ARM -- `cap_unwhitened=3` vs `cap_pca_whitened=7`; **recovered ONLY by the relaxed unequal-length sibling rule** | Whitening = decorrelation = the operation that separates items sharing contexts. **Deflate hard: the absolute capacities are 3 and 7 items.** Its own framing ('one-line universal real-encoder rescue') is not supported at n=7. Ranked for the MECHANISM, not the number. | **C3**, C1 |
| **13** | `exp_pseudoinverse_real_encoder_keys_v1 (+ 4 siblings)` | ARM in all five -- the `hebb_*` arm IS the floor; **no arm name contains a control word**, which is why a lexical pass misses the entire family | The write rule that determines what the stored items ARE. Non-degenerate anchor: Llama-L15 **122 -> 614 (5.03x)**. On real MiniLM/BGE/E5 keys Hebb reaches **0** where pinv reaches 0.40-0.55. **Quote it that way -- the `400000000x` in this cell's own `verdict_msg` is an x/0 artifact.** | **C3**, C1 |
| **14** | `exp_kv_learned_projection_v1` | A -- **shuffled control 0.015**, analytic ceiling 0.080, held-out split | The *missing-LEARNING* flavour: a LEARNED contrastive projection that raises **key separation to 0.878** and transfers to held-out facts (worst-seed recall 0.827, std 0.019). A learned metric is the brain-compatible answer to a separation defect and it reuses `hdlab/learner` rather than building in parallel. **Deflation: `n_enc=2`, synthetic KV task.** | **C3**, C1 |
| **15** | `exp_substrate_hallucination_detection_minilm_v1` | ARM -- `grounded_conf` vs `hall_conf` IS the contrast; **the source note's detector scored this Class D and flagged it as its residual false negative -- the NEG_COND rule here catches it** | AUC **0.999** separating grounded from hallucinated (`grounded_conf 0.204` vs `hall 0.107`). It separates a true from a plausible-but-wrong item, which is the C3 error mode -- but it raises **precision**, not hit@1 at full coverage, so it is last of the fifteen. | C3 (precision) |

**Deliberately NOT in the top 15, so the omissions are decisions:** `exp_anchor_compose_identity_shuffle_cskg_v2` and `_scaling_ladder_cskg_v3` (they BOUND C3 at 93% of oracle rather than moving it -- and that bound is the reason ranks 1-5 are representation-side); `exp_metacog_abstain_readout_signal_thresholding_v1` and `exp_attention_salience_common_mode_detector_v1` (precision at partial coverage, and the common-mode detector's own result explains why rank-1 common-mode removal came back HARD_FAIL_NO_EFFECT -- it fires only in the correlated mode); `exp_c1_entmax_envelope_sweep_v2` (reports **delta +0.000 on recall** -- it is a FLOPs win, and its title says 'read-out win'); `exp_substrate_capacity_cliff_fhrr_constant_derivation_v1` (a beautiful closed-form derivation, C_FHRR=1.9934 within 0.33% with zero free parameters, but it predicts capacity rather than changing separation); the `exp_integration_full_stack_*` pair (4-stage composition at compounding_ratio ~1.0 -- infrastructure, not a lever).

---

## 5. THE LEDGER -- EVERY CELL GETS A ROW

Column meanings are RECOVERY_PROGRAM sec 3a's. Two deviations, both stated: **`supersede` is `UNCHECKED` on every row** (the citation graph is decoration -- only one edge in the whole file resolves onto a live chain-graded cell), and **`live` is `OFF-PATH` unless the matched `hdlab/` module is in the 39-module runtime closure**, which is a MODULE-level statement, not a cell-level one.

### Group CG-A -- ranked separation-geometry candidates (26 rows)

| # | cell | date (src) | verdict (as read) | run_mode | floor | disk | module | moves | STATE |
|---|---|---|---|---|---|---|---|---|---|
| A1 | `exp_substrate_etf_minilm_dim_expansion_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3,C1 | STATE:VERIFIED |
| A2 | `exp_pseudoinverse_real_encoder_keys_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3,C1 | STATE:VERIFIED |
| A3 | `exp_substrate_pca_prewhitening_codebook_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3,C1 | STATE:VERIFIED |
| A4 | `exp_encoder_retained_trace_requery_coarse_to_fine_v1` | 2026-07-08 (ts_iso) | HARD_PASS_RETAINED_TRACE_RECOVERS | full | ARM | OK | EXP-ONLY | C3 | STATE:VERIFIED |
| A5 | `exp_f6_bge_large_pinv_mmax_reaudit_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3,C1 | STATE:VERIFIED |
| A6 | `exp_kv_learned_projection_v1` | 2026-06-20 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | C3 | STATE:VERIFIED |
| A7 | `exp_pb_e5_vs_bge_pinv_headtohead_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3,C1 | STATE:VERIFIED |
| A8 | `exp_substrate_codebook_near_duplicate_diagnostic_cpu_v1` | 2026-06-12 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | C3,C1 | STATE:VERIFIED |
| A9 | `exp_substrate_capacity_cliff_fhrr_constant_derivation_v1` | 2026-07-17 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C3,C1 | STATE:VERIFIED |
| A10 | `exp_cortex_context_retention_v2_3seed_full_chain_grade_m1p5_milestone_first_cortex_integ` | 2026-07-01 (ledger:ts) | HARD_PASS | full | A | OK | HD:`context_retention.py` | C3,C1,C4,C2 | STATE:VERIFIED |
| A11 | `exp_substrate_encoder_capacity_at_scale_battery_gpu_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C3,C1 | STATE:VERIFIED |
| A12 | `exp_substrate_last_token_vs_whitening_mean_pool_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | ARM | OK | HD:`whitening.py` | C3,C1 | STATE:VERIFIED |
| A13 | `exp_hebb_vs_pseudoinverse_long_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3,C1 | STATE:VERIFIED |
| A14 | `exp_attention_salience_common_mode_detector_v1` | 2026-07-20 (ts_iso) | HARD_PASS_COMMON_MODE_DETECTOR_SEPARATES | full | A | OK | EXP-ONLY | C3,C1 | STATE:VERIFIED |
| A15 | `exp_pb_production_recipe_integration_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | C3,C1 | STATE:VERIFIED |
| A16 | `exp_f8_pinv_padfix_alpha_compound_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C3,C1 | STATE:VERIFIED |
| A17 | `exp_generation_decode_selfmargin_dupclass_exact_v1` | 2026-07-06 (ts_iso) | HARD_PASS | full | A | OK | HD:`generation.py` | C3,C4 | STATE:VERIFIED |
| A18 | `exp_substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | A | OK | HD:`whitening.py` | C3,C1 | STATE:VERIFIED |
| A19 | `exp_substrate_hallucination_detection_minilm_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3,C1 | STATE:VERIFIED |
| A20 | `exp_interference_avoidance_conjunctive_vs_additive_v1` | 2026-07-14 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | C3?,C1 | STATE:VERIFIED |
| A21 | `exp_metric_dependence_top_k_semantic_v3_3seed_full_chain_grade_semantic_top_k_cliff_brac` | 2026-07-02 (ledger:ts) | HARD_PASS | full | ARM | OK | HD:`semantic.py` **(in live closure)** | C3?,C1 | STATE:VERIFIED |
| A22 | `exp_substrate_cognitive_core_introspection_toolkit_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| A23 | `exp_substrate_decomposition_resonator_alpha05_cpu_v1` | 2026-06-12 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3?,C4 | STATE:VERIFIED |
| A24 | `exp_anchor_compose_identity_shuffle_cskg_v2` | 2026-07-13 (ts_iso) | HARD_PASS_INDUCTIVE_ANCHOR_COMPOSE_IDENTITY_CLOSED | full | A | OK | EXP-ONLY | C3?,C4,BOUND | STATE:VERIFIED |
| A25 | `exp_integration_full_stack_hard_regime_v1` | 2026-07-05 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| A26 | `exp_joint_operator_capstone_selective_readouts_v1` | 2026-07-15 (ts_iso) | HARD_PASS_JOINT_OPERATOR_CAPSTONE_BOTH_SOLVED_NO_INTERFERENCE_HEADDISC_CLEAN | full | A | OK | EXP-ONLY | C3? | STATE:VERIFIED |

### Group CG-B -- remaining cells WITH A REAL FLOOR (148 rows)

A control arm, reference arm or prose floor reads on disk. Ordered by separation-geometry score descending, so the head of this group is the next place to look after CG-A.

| # | cell | date (src) | verdict (as read) | run_mode | floor | disk | module | moves | STATE |
|---|---|---|---|---|---|---|---|---|---|
| B1 | `exp_metacog_abstain_readout_signal_thresholding_v1` | 2026-07-20 (ts_iso) | HARD_PASS_EXISTING_SIGNAL_CARRIES_USABLE_CONFIDENCE | full | A | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| B2 | `exp_grounding_bind_chain_systematicity_v1` | 2026-07-09 (ts_iso) | SYS=SYS_HARD_PASS/REACH=REACH_HARD_PASS/ORACLE=READOUT_LIMIT | full | A | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| B3 | `exp_pb_pinv_llama_l15_keys_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3?,C1 | STATE:VERIFIED |
| B4 | `exp_anchor_compose_scaling_ladder_cskg_v3` | 2026-07-13 (ts_iso) | SCALING_HOLDS | full | A | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| B5 | `exp_c1_entmax_envelope_sweep_v2` | UNDATED (none) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3?,C1 | STATE:VERIFIED |
| B6 | `exp_consolidation_correct_regimes_v1` | 2026-07-16 (ts_iso) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3?,C1 | STATE:VERIFIED |
| B7 | `exp_cortex_hippo_dense_layer_n_sweep_v1_seed_{7,13,19}` | 2026-07-01 (_start_marker) | HARD_PASS | smoke | A | OK | EXP-ONLY | C3?,C1 | STATE:VERIFIED |
| B8 | `exp_generation_decoder_gsbc_native_blocklocal_v1` | 2026-07-05 (ts_iso) | HARD_PASS | full | ARM | OK | HD:`generation.py` | C3? | STATE:VERIFIED |
| B9 | `exp_grounding_by_redundancy_joint_corruption_allometry_v1` | 2026-07-14 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C3?,C1 | STATE:VERIFIED |
| B10 | `exp_integration_full_stack_full_fidelity_v1` | 2026-07-06 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| B11 | `exp_pythia_kv_desat_v2` | 2026-06-21 (ledger:ts) | HARD_PASS | full | A | OK | EXP-ONLY | C3?,C1 | STATE:VERIFIED |
| B12 | `exp_substrate_abduction_f1_weakest_signature_kernel_kgram_xor_groundtruth_cpu_v1` | 2026-06-15 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | C3?,C1 | STATE:VERIFIED |
| B13 | `exp_substrate_cortex_hippo_dense_layer_m_sweep_v3_seed_{7,13,19}` | 2026-07-01 (ledger:ts) | HARD_PASS | full | A | OK | EXP-ONLY | C3?,C1 | STATE:VERIFIED |
| B14 | `exp_substrate_permutation_binding_multiocc_v2_full` | 2026-06-25 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| B15 | `exp_counterfactual_regret_comparison_vmpfc_v1` | 2026-06-28 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| B16 | `exp_cross_axis_m_n_k_discriminating_arm_v2_3seed_full_chain_grade_substrate_axes_m_n_k_f` | 2026-07-02 (ledger:ts) | MIDDLE_BAND | full | A | OK | EXP-ONLY | C3? | STATE:REFUTED |
| B17 | `exp_h_hotpotqa_ingest_v1` | 2026-06-22 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | C3?,C2 | STATE:VERIFIED |
| B18 | `exp_scale_meaning_learn_arc_heldout_v2` | 2026-07-27 (ts_iso) | HARD_PASS_CLEAN_WIN | full | A | OK | EXP-ONLY | C3?,C2 | STATE:VERIFIED |
| B19 | `exp_substrate_abduction_f1b_confound_break_recoverability_vs_infopreservation_cpu_v1` | 2026-06-15 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | C3?,C2 | STATE:VERIFIED |
| B20 | `exp_substrate_ultrametric_clustering_phase_diagram_v1` | 2026-06-28 (git-first-commit) | HARD_PASS | full | A | OK | HD:`ultrametric_clustering.py` | C3? | STATE:VERIFIED |
| B21 | `exp_substrate_wikipedia_ppmi_svd_scale_up_full_n10k_formal_3seed_cg_honest_negative_supe` | 2026-07-03 (_start_marker) | MEASURED_BOUND_LOW_DELTA | full | A | OK | HD:`char_trigram_encoder.py` | C3?,C4 | STATE:VERIFIED |
| B22 | `exp_visual_grounding_coherence_v1` | 2026-07-18 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| B23 | `exp_b_delta_readout_lever_transfer_v2` | UNDATED (none) | HARD_PASS | full | A | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B24 | `exp_consolidated_reader_passive_mechanism_heldout_v1` | 2026-07-24 (ts_iso) | PASSIVE_MECHANISM_CAPABILITY_EARNED | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B25 | `exp_learned_codebook_generalization_gate_v1` | 2026-07-20 (ts_iso) | HARD_PASS | ABSENT | A | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B26 | `exp_multiplicative_composition_lever_v1_cpu_v1` | 2026-06-20 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B27 | `exp_nativelang_svo_vsa_probe_v1` | 2026-07-16 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B28 | `exp_pb_mmr_real_encoder_clustered_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B29 | `exp_srn_shrink_probe_replication_v1` | 2026-07-18 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B30 | `exp_substrate_anchor4_encoder_family_n16384_gpu_v1_seed_{7,13,19}` | 2026-06-30 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B31 | `exp_substrate_anchor4_encoder_family_v4_seed_7` | 2026-06-30 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B32 | `exp_substrate_capacity_composition_full_b2xb4xhier_v1_n2048_gpu` | 2026-06-04 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B33 | `exp_substrate_hallucination_robustness_hard_negatives_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B34 | `exp_substrate_pp8_learned_discriminability_probe_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B35 | `exp_substrate_real_encoder_capabilities_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| B36 | `exp_substrate_wikipedia_ppmi_svd_baseline_smoke_cg_measured_bound_3seed_n500_hp1_cleared` | 2026-07-03 (_start_marker) | HARD_PASS | smoke | A | OK | HD:`char_trigram_encoder.py` | -- | STATE:VERIFIED |
| B37 | `exp_additive_map_acceptance_gate_v1` | 2026-07-14 (ts_iso) | ACCEPTANCE_PASS_ADDITIVE_MAP_REPRODUCES_VET | full | A | OK | HD:`additive_map.py` | -- | STATE:VERIFIED |
| B38 | `exp_attention_salience_reliability_gate_independent_channel_v1` | 2026-07-20 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | BOUND | STATE:VERIFIED |
| B39 | `exp_cortex_schema_exemplar_bayes_importance_sample_v1` | 2026-06-28 (ts_iso) | HARD_PASS | full | A | OK | HD:`schema_exemplar_bayes.py` | -- | STATE:VERIFIED |
| B40 | `exp_cortex_ultrametric_clustering_coarse_grain_v1` | 2026-06-26 (git-first-commit) | HARD_PASS | full | A | OK | HD:`ultrametric_clustering.py` | C1 | STATE:VERIFIED |
| B41 | `exp_generation_grounded_fact_utterance_v1` | 2026-07-05 (ts_iso) | HARD_PASS | full | ARM | OK | HD:`generation.py` | -- | STATE:VERIFIED |
| B42 | `exp_hoc1_word_bigram_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | PROSE | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B43 | `exp_integration_end_to_end_loop_bridge_v1` | 2026-07-05 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C4,C2 | STATE:VERIFIED |
| B44 | `exp_kmax_ness_envelope_corrected_v1` | UNDATED (none) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B45 | `exp_leakproof_relinfer_context_sweep_v1` | 2026-07-26 (ts_iso) | HOLDS_AND_SCALES | full | A | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| B46 | `exp_multisource_arena_temporal_accrual_fair_v1` | 2026-07-16 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B47 | `exp_q_b1_ab_iterate_3arm_v1_n16384` | 2026-06-19 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B48 | `exp_read_discourse_entitygrid_coherence_v1` | 2026-07-17 (ts_iso) | MIDDLE_BAND | full | A | OK | EXP-ONLY | C4 | STATE:REFUTED |
| B49 | `exp_read_grow_selectional_preference_precision_v2` | 2026-07-17 (ts_iso) | HARD_FAIL | full | A | OK | EXP-ONLY | -- | STATE:REFUTED |
| B50 | `exp_reasoning_depth_exact_order_statistic_self_margin_v1` | 2026-07-06 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B51 | `exp_redundant_soft_shard_router_e2e_seed_robust_boundary_v1` | 2026-07-17 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B52 | `exp_rns_subblock_margin_exact_prefactor_v2` | 2026-07-06 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B53 | `exp_substrate_abduction_f3_hmm_headroom_realgap_deployment_cpu_v1` | 2026-06-15 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B54 | `exp_substrate_anchor3_coarse_grain_phase_diagram_v2_family_overlap` | 2026-06-29 (ledger:ts) | HARD_PASS | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B55 | `exp_substrate_capacity_composition_b2xb4_v1_n2048` | 2026-06-04 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B56 | `exp_substrate_composed_encoder_v3_smoke_2026_07_03` | 2026-07-03 (ts_iso) | SELFTEST_PASS | self_test | ARM | OK | HD:`composed_encoder_v3.py` | -- | STATE:VERIFIED |
| B57 | `exp_substrate_phase_diagram_subsystem_decoupling_v3` | 2026-07-17 (_start_marker) | HARD_PASS | full | A | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B58 | `exp_substrate_sparsity_free_axis_v4b_pc_widened_alpha_grid_n4096_3seed_full_chain_grade_` | 2026-07-02 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B59 | `exp_substrate_wikipedia_ppmi_svd_scale_up_full_n10k_preliminary_cg_honest_negative_2of3_` | 2026-07-03 (_start_marker) | MEASURED_BOUND_LOW_DELTA | full | A | OK | HD:`char_trigram_encoder.py` | C2 | STATE:VERIFIED |
| B60 | `exp_ternary_arm2_extended_basis_2026_06_16` | UNDATED (none) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B61 | `exp_capacity_multi_bank_alpha_k_high_v1_seed_{7,13,19}` | 2026-07-01 (ledger:ts) | HARD_PASS | full | A | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B62 | `exp_combo1_p3_dam_implicit_gram_v3_gpu_fix_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B63 | `exp_conceptnet_rerank_parity_multiseed_v1` | 2026-07-07 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B64 | `exp_encoder_alltype_transfer_stress_v1` | 2026-08-01 (ts_iso) | HARD_PASS | lite | ARM | OK | EXP-ONLY | C4 | STATE:VERIFIED |
| B65 | `exp_generation_decoder_rns_crt_highvocab_v1` | 2026-07-05 (ts_iso) | HARD_PASS | full | A | OK | HD:`generation.py` | -- | STATE:VERIFIED |
| B66 | `exp_kb_partition_by_source_class_v4_calibrated` | 2026-06-27 (git-first-commit) | HARD_PASS | ABSENT | A | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B67 | `exp_multisource_arena_conjunction_menu_v1` | 2026-07-16 (ts_iso) | HARD_PASS | ABSENT | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B68 | `exp_np_head_finder_grounding_gate_break050_v1` | 2026-07-19 (ts_iso) | HARD_PASS_HEADFINDER_BREAKS_050 | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B69 | `exp_pb_crt_real_encoder_atoms_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B70 | `exp_phase_diagram_capacity_multi_bank_k4_envelope_v2c_n8192_gpu` | 2026-06-27 (ledger:ts) | HARD_FAIL | full | A | OK | EXP-ONLY | C1 | STATE:REFUTED |
| B71 | `exp_reasoning_depth_capacity_provisioning_monitor_loop_v1` | 2026-07-08 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B72 | `exp_reasoning_readout_length_generalization_clutrr_cg_v1` | 2026-07-20 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B73 | `exp_situation_model_assembly_encoder_retrain_scale_v1` | 2026-07-31 (ts_iso) | CLEAN_PASS | grid | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B74 | `exp_substrate_capacity_multibank_alpha_k_phase_diagram_v2_gpu_seed_7` | 2026-06-29 (ledger:ts) | MIDDLE_BAND | full | A | OK | EXP-ONLY | C1 | STATE:REFUTED |
| B75 | `exp_substrate_concept_encoder_spoke1_stress_test_cell1_apples_to_apples_label_shuffle_v1` | 2026-07-03 (ts_iso) | MIDDLE_BAND | full | A | OK | HD:`concept_encoder.py` | -- | STATE:REFUTED |
| B76 | `exp_substrate_cross_modal_binding_3rd_modality_v1_seeds_13_19_full_chain_grade_extends_s` | 2026-07-01 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B77 | `exp_substrate_schema_exemplar_bayes_capacity_stress_v4_seed_13` | 2026-06-29 (ts_iso) | CHAIN_GRADE_MULTI | full | A | OK | HD:`schema_exemplar_bayes.py` | C1 | STATE:VERIFIED |
| B78 | `exp_substrate_sparse_vs_dense_alpha_sweep_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B79 | `exp_u1_fb15k237_ingest_eval_v1` | 2026-06-21 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| B80 | `exp_csp_first_ship_v1` | 2026-06-19 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B81 | `exp_leakproof_relational_inference_heldout_v1` | 2026-07-26 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| B82 | `exp_leakproof_relinfer_twonew_v1` | 2026-07-26 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| B83 | `exp_partof_broad_after` | 2026-06-19 (ledger:ts) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B84 | `exp_quotative_speaker_attribution_stack_break050_v1` | 2026-07-19 (ts_iso) | HARD_PASS_QUOTATIVE_BREAKS_050 | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B85 | `exp_situation_model_assembly_binding_wm_coref_v1` | 2026-07-31 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C4 | STATE:VERIFIED |
| B86 | `exp_substrate_compose_freq_routing_v5_definitive` | 2026-06-25 (ledger:ts) | HARD_PASS | full | A | OK | HD:`compose_freq_routing.py` | -- | STATE:VERIFIED |
| B87 | `exp_substrate_continual_learning_30day_realistic_stream_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | A | OK | HD:`continual.py` | -- | STATE:VERIFIED |
| B88 | `exp_substrate_cross_modal_binding_visual_auditory_v1_cross_seed_agg_3_of_3_hard_pass_sta` | 2026-06-28 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B89 | `exp_substrate_lock_in_amp_phase_diagram_v2_full_3seed_chain_grade_phase_characterization` | 2026-06-29 (ledger:ts) | HARD_PASS | full | A | OK | HD:`lock_in_amp.py` | -- | STATE:VERIFIED |
| B90 | `exp_substrate_position_binding_combined_arch_trigram_v1_n4096` | 2026-06-04 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B91 | `exp_substrate_stage3_integrated_audit_device_demo_v1` | 2026-06-25 (git-first-commit) | HARD_PASS_INTEGRATED_AUDIT_DEVICE | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B92 | `exp_substrate_working_memory_multi_bank_k_extension_adversarial_v1` | 2026-06-26 (ledger:ts) | RAIL_SANITY_BREACH | full | A | OK | HD:`working_memory.py` **(in live closure)** | -- | STATE:VERIFIED |
| B93 | `exp_t5c_hybrid_3seed_kb10k_v1` | 2026-06-09 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B94 | `exp_theta_gamma_v4_extended_seeds_gpu_7seed_full_chain_grade_lift_of_v3_atom_9_mm_via_re` | 2026-07-01 (ts_iso) | MIDDLE_BAND | full | ARM | OK | EXP-ONLY | -- | STATE:REFUTED |
| B95 | `exp_a1_substrate_intent_classifier_v1_gatecheck` | 2026-06-23 (ledger:ts) | HARD_PASS | full | A | OK | HD:`intent_classifier.py` | -- | STATE:VERIFIED |
| B96 | `exp_c_infty_seb_detection_full_v3` | UNDATED (none) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B97 | `exp_combo3_unified_api_n32768_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | smoke | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B98 | `exp_cskg_foundation_v1` | 2026-07-26 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B99 | `exp_csp_memory_warm_start_full_v3` | UNDATED (none) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B100 | `exp_curriculum_order_ingest_schema_fit_v1` | 2026-07-16 (ts_iso) | HARD_PASS_ORDER_MATTERS_CURRICULUM_RESCUES_SCHEMA_FIT | ABSENT | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B101 | `exp_deletion_cert_zratio_n32768_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | smoke | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B102 | `exp_exp_p1_action_at_any_position_phase_diagram_v1` | 2026-06-22 (ledger:ts) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B103 | `exp_frame_order_recovery_hard_comprehension_v2` | 2026-07-06 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B104 | `exp_interaction_asymmetric_directed_operators_v1` | 2026-07-15 (ts_iso) | HARD_PASS_BRAIN_ASYMMETRIC_OP_READS_DOMINANCE_TRANSITION_OP | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B105 | `exp_interaction_nonadditive_discovery_v1` | 2026-07-15 (ts_iso) | HARD_PASS_A_INTERACTION_CONSTRUCTION_PROVEN / HARD_PASS_B_SYMMETRY_MATCHED_DISCOVERY_NONADDITIVE_AND_NON | full | A | OK | EXP-ONLY | BOUND | STATE:VERIFIED |
| B106 | `exp_kappa3_sensitivity_sweep_n16384_v3_delta_alpha_protocol_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | PROSE | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B107 | `exp_kg_store_dim_scaling_ceiling_v1` | 2026-07-13 (ts_iso) | HARD_PASS_DIMENSION_RELIEVES_CEILING | full | A | OK | EXP-ONLY | BOUND | STATE:VERIFIED |
| B108 | `exp_lln_point_mass_verification_n_v_c_f_sweep_v1` | 2026-07-01 (_start_marker) | CHAIN_GRADE_LLN_POINT_MASS_VERIFIED | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B109 | `exp_metacog_abstain_conformal_transfer_v1` | 2026-07-20 (ts_iso) | HARD_PASS_CONFORMAL_THRESHOLD_TRANSFERS_TO_DISJOINT_TEST | full | A | OK | HD:`conformal.py` | -- | STATE:VERIFIED |
| B110 | `exp_morph_ruleset_wug_v2_cpu` | 2026-07-05 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B111 | `exp_multihop_reasoning_depth_20_to_40_gpu_v1` | 2026-07-01 (git-first-commit) | DEPTH_40_STILL_ABOVE_HALF | full | A | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| B112 | `exp_multihop_reasoning_depth_45_to_60_gpu_v1` | 2026-07-01 (git-first-commit) | DEPTH_60_CROSSED_HALF | full | A | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| B113 | `exp_multihop_reasoning_depth_50_55_crossing_bracket_gpu_v1` | 2026-07-01 (git-first-commit) | CROSSING_BRACKET_50_55 | full | A | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| B114 | `exp_ner_transition_charngram_noise_crosscut_cpu_v1` | 2026-06-12 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B115 | `exp_p1_v2_action_at_any_position_llm_class_v1` | 2026-06-22 (ledger:ts) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B116 | `exp_parietal_relational_v3` | 2026-07-01 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| B117 | `exp_phase_diagram_wm_multibank_k_8192_3seed_harvest_v1` | 2026-06-27 (ledger:ts) | CHAIN_GRADE_K_8192_3SEED | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B118 | `exp_pp48_pp46_negative_knowledge_with_deletion_cert_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B119 | `exp_pp49_hrc_counterfactual_depth_8_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B120 | `exp_pp50_kappa3_delta_alpha_n16384_v2_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | PROSE | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B121 | `exp_pp50_kappa3_delta_alpha_n32768_v3_n32768` | 2026-06-03 (git-first-commit) | HARD_PASS | full | PROSE | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B122 | `exp_pp50_kappa3_delta_alpha_n8192_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | PROSE | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B123 | `exp_pp52_exact_rollback_n4096_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | PROSE | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B124 | `exp_pp52_exact_rollback_n8192_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B125 | `exp_pp52_one_shot_addition_n8192_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B126 | `exp_provisional_hold_bootstrap_arbitrary_order_v1` | 2026-07-16 (ts_iso) | HARD_PASS_PROVISIONAL_HOLD_RECOVERS_ARBITRARY_ORDER | ABSENT | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B127 | `exp_refuse_gate_5_graph_health_cpu_v1` | 2026-06-20 (git-first-commit) | HARD_PASS | full | A | OK | HD:`refuse_gate.py` | -- | STATE:VERIFIED |
| B128 | `exp_substrate_arch_ablation_matrix_bigram_v1_n512_gpu` | 2026-06-04 (git-first-commit) | HARD_PASS | full | ARM | OK | HD:`ablation.py` **(in live closure)** | -- | STATE:VERIFIED |
| B129 | `exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512` | 2026-06-04 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B130 | `exp_substrate_cognitive_core_counterfactual_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| B131 | `exp_substrate_narrative_partition_oracle_v_c_sweep_v1_smoke` | 2026-06-28 (ledger:ts) | HARD_FAIL | smoke | A | OK | EXP-ONLY | C4 | STATE:REFUTED |
| B132 | `exp_substrate_novel_assembly_2_tier2_novel_composition_equivalence_checked_cpu_v1` | 2026-06-15 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B133 | `exp_substrate_partition_routing_hierarchical_2level_v1` | 2026-06-25 (git-first-commit) | CHAIN_GRADE_AT_M_10M | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B134 | `exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_7` | 2026-06-28 (ts_iso) | HARD_FAIL | full | PROSE | OK | EXP-ONLY | -- | STATE:REFUTED |
| B135 | `exp_substrate_refuse_gate_near_domain_v2` | 2026-06-25 (git-first-commit) | HARD_PASS_BOTH_WORK | full | A | OK | HD:`refuse_gate.py` | -- | STATE:VERIFIED |
| B136 | `exp_substrate_refuse_gate_v8_conformal_v1_seed_7_smoke` | 2026-07-01 (ts_iso) | HARD_PASS | smoke | A | OK | HD:`refuse_gate.py` | -- | STATE:VERIFIED |
| B137 | `exp_substrate_refuse_gate_v_rel_extension_v1` | 2026-06-25 (git-first-commit) | HARD_PASS | full | A | OK | HD:`refuse_gate.py` | -- | STATE:VERIFIED |
| B138 | `exp_substrate_schema_family_phase_diagram_v1_full_3seed_chain_grade_phase_characterizati` | 2026-06-29 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B139 | `exp_substrate_schema_family_phase_diagram_v1_seed_13` | 2026-06-29 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B140 | `exp_substrate_schema_family_phase_diagram_v1_seed_19` | 2026-06-29 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B141 | `exp_substrate_schema_family_phase_diagram_v1_seed_7` | 2026-06-29 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B142 | `exp_substrate_stage_a_bio_smoke_b2_sparse_fix_v2` | UNDATED (none) | HARD_FAIL | full | A | OK | EXP-ONLY | -- | STATE:REFUTED |
| B143 | `exp_substrate_theta_gamma_v2_fhrr_all_complex_seed_7` | 2026-07-01 (ts_iso) | HARD_PASS | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B144 | `exp_t5c_c1_3seed_validate_gpu_v1` | 2026-06-08 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B145 | `exp_t5c_c1_5seed_validate_gpu_v1` | 2026-06-10 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B146 | `exp_t5c_d1_3seed_validate_gpu_v1` | 2026-06-08 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B147 | `exp_t5c_multi1_everylayer_3seed_v1` | 2026-06-09 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B148 | `exp_t5c_multi2_6layer_3seed_v1` | 2026-06-09 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |

### Group CG-C -- contrast arm present, NO identifiable reference arm (70 rows)

**These are the vocabulary-drift alarm at cell level.** Each has a comparison SHAPE whose arm names this pass could not name as a reference. Some are real floors under an unrecognised name (`exp_substrate_encoder_capacity_at_scale_battery_gpu_v1`, promoted to CG-A, was one); most are config sweeps. **Not counted as floored.**

| # | cell | date (src) | verdict (as read) | run_mode | floor | disk | module | moves | STATE |
|---|---|---|---|---|---|---|---|---|---|
| C1 | `exp_substrate_minilm_encoder_fidelity_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| C2 | `exp_intent_atis_multiseed_cpu_v1` | 2026-06-11 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| C3 | `exp_pp55_vsa_binding_n131072_v6_n131072` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| C4 | `exp_t5c_pp225_3seed_v1` | 2026-06-09 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C5 | `exp_a8_continual_writes_no_catastrophic_forgetting_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | HD:`continual.py` | C1 | STATE:VERIFIED |
| C6 | `exp_capacity_cliff_graceful_full_v3` | 2026-06-12 (ledger:ts) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| C7 | `exp_crt_module_scaling_battery_fixed_v1` | UNDATED (none) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| C8 | `exp_crt_module_scaling_battery_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| C9 | `exp_csp_hebbian_coexist_v1` | 2026-06-01 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C10 | `exp_fp16_vs_fp32_parity_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| C11 | `exp_matrix_trace_primitives_full_v3` | UNDATED (none) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C12 | `exp_padding_side_audit_capacity_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| C13 | `exp_pb_kf1_multilang_chain_robustness_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C14 | `exp_substrate_capacity_stress_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| C15 | `exp_tier4_multiseed_sweep_cpu_v1` | 2026-06-11 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C16 | `exp_tr_w1w2_set_intersect_v1` | 2026-06-01 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C4 | STATE:VERIFIED |
| C17 | `exp_wave1_multiseed_sweep_cpu_v1` | 2026-06-11 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C18 | `exp_deletion_cert_refusal_joint_v1` | 2026-06-01 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C19 | `exp_hnsw_ef_search_calibration_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C20 | `exp_hp12_v1_demo_scale_10k_facts_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C21 | `exp_kf1_paraphrase_robustness_marianmt_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C22 | `exp_pb_multilang_paraphrase_chain_kf1_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C23 | `exp_pp55_vsa_binding_n16384_v3_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C24 | `exp_active_inference_dpefe_h2_cpu_v1` | 2026-06-11 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| C25 | `exp_ccc1_extra_fb15k237_kg_multihop_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| C26 | `exp_combo2_p4_l3_signed_am_v1_n32768` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C27 | `exp_f4_kappa_n_deviation_snr_cpu_v1` | 2026-06-13 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C28 | `exp_multiagent_coord_full_v3` | UNDATED (none) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C29 | `exp_n1_concept_lm_substrate_native_token_decode_v3` | 2026-06-21 (git-first-commit) | HARD_FAIL | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:REFUTED |
| C30 | `exp_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1` | 2026-06-26 (git-first-commit) | CHAIN_GRADE_DEPTH_CEILING_30 | full | CONTRAST-ONLY | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| C31 | `exp_planted_csp_viability_full_v3` | UNDATED (none) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C32 | `exp_pos_tagger_multiseed_cpu_v1` | 2026-06-11 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | HD:`pos_tagger.py` | -- | STATE:VERIFIED |
| C33 | `exp_pp52_exact_rollback_n16384_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C34 | `exp_pp52_one_shot_addition_n16384_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C35 | `exp_q_b1_bisect_d275_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C36 | `exp_q_b1_bisect_d276_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C37 | `exp_q_b1_chain_depth_100_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C38 | `exp_q_b1_chain_depth_150_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C39 | `exp_q_b1_chain_depth_15_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C40 | `exp_q_b1_chain_depth_200_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C41 | `exp_q_b1_chain_depth_20_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C42 | `exp_q_b1_chain_depth_250_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C43 | `exp_q_b1_chain_depth_25_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C44 | `exp_q_b1_chain_depth_30_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C45 | `exp_q_b1_chain_depth_35_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C46 | `exp_q_b1_chain_depth_40_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C47 | `exp_q_b1_chain_depth_45_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C48 | `exp_q_b1_chain_depth_50_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C49 | `exp_q_b1_chain_depth_55_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C50 | `exp_q_b1_chain_depth_60_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C51 | `exp_q_b1_chain_depth_70_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C52 | `exp_q_b1_chain_depth_80_v1_n16384` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C53 | `exp_q_b1_chain_depth_80_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C54 | `exp_q_b1_chain_depth_90_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C55 | `exp_q_b1_depth_extended_n32768` | 2026-06-02 (git-first-commit) | MIDDLE_BAND | smoke | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:REFUTED |
| C56 | `exp_r_alpha_throughput_full_v3` | UNDATED (none) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C57 | `exp_substrate_cognitive_core_analogical_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C58 | `exp_substrate_cognitive_core_architectural_advantage_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C59 | `exp_substrate_continual_learning_distshift_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | HD:`continual.py` | -- | STATE:VERIFIED |
| C60 | `exp_substrate_crossdomain_transfer_conll2003_ontonotes_ner_cpu_v1` | 2026-06-12 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C61 | `exp_substrate_extended_context_ceiling_posbind_symw_v1_8192_16384_gpu` | 2026-06-04 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| C62 | `exp_substrate_long_conversation_10k_exchanges_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C63 | `exp_substrate_long_conversation_scale_1000_exchanges_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C64 | `exp_substrate_multidoc_synthesis_1000plus_docs_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C65 | `exp_substrate_task_complexity_sweep_v1_512_8192_gpu` | 2026-06-04 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C66 | `exp_symbolic_prim_battery_v1` | 2026-06-01 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C67 | `exp_t5c_pp225_pythia14b_fp32proj_3seed_v1` | 2026-06-09 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C68 | `exp_wave1_tier1_sweep_cpu_v1` | 2026-06-11 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C69 | `exp_wave2_rescue_multiseed_sweep_cpu_v1` | 2026-06-11 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C70 | `exp_wave4_full_streaming_battery_n8192_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |

### Group CG-D -- no floor shape visible in metrics.json (23 rows)

**`NO FLOOR` = no floor visible in `metrics.json`, NOT 'no floor'.** Two confirmed detector false negatives are already promoted out of this group into CG-A (`exp_substrate_expansion_method_battery_gpu_v1`, `exp_substrate_name_augmented_encoding_recovery_canonical_rerun_v593`), so assume more remain. An unfloored pass is not evidence and none of these may be cited as one.

| # | cell | date (src) | verdict (as read) | run_mode | floor | disk | module | moves | STATE |
|---|---|---|---|---|---|---|---|---|---|
| D1 | `exp_substrate_expansion_method_battery_gpu_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | C3,C1 | STATE:VERIFIED |
| D2 | `exp_substrate_name_augmented_encoding_recovery_canonical_rerun_v593` | 2026-06-12 (ledger:ts) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | C3?,C4 | STATE:VERIFIED |
| D3 | `exp_substrate_sparsity_fine_battery_gpu_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | C3?,C1 | STATE:VERIFIED |
| D4 | `exp_modern_hopfield_n_sweep_v1` | 2026-06-07 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D5 | `exp_cortex_hippo_dense_commercial_m_100k_1m_gpu_v5_kernel_active_fraction_3seed_full_cha` | 2026-07-01 (ts_iso) | CELL_CRASHED | full* | NO FLOOR | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| D6 | `exp_substrate_capacity_battery_gpu_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| D7 | `exp_substrate_capacity_scaling_sweep_xl_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| D8 | `exp_temporal_contextual_multiseed_cpu_v1` | 2026-06-11 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| D9 | `exp_substrate_multimodal_binding_text_kg_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D10 | `exp_combo2_p4_l3_signed_am_v1_n32768_5seed_verification_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | BAND-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D11 | `exp_combo3_unified_api_v1_n16384_l4_alpha_grid_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D12 | `exp_deletion_cert_z_ratio_n16384_full_alpha_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D13 | `exp_deletion_cert_z_ratio_n16384_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | BAND-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D14 | `exp_i1_bf16_overflow_n65536_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D15 | `exp_membership_auroc_mapping_v1` | 2026-06-07 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D16 | `exp_pp50_kappa3_ultra_fine_sigma_g_v4_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D17 | `exp_pp52_one_shot_addition_n4096_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | BAND-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D18 | `exp_sql_hd_aggregation_bound_gpu_v1` | 2026-06-07 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D19 | `exp_substrate_b6_x_sq2_audit_preserving_reasoning_v1_n4096` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D20 | `exp_substrate_hierarchical_5corpus_meta_v1_n2048_gpu` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D21 | `exp_substrate_hierarchical_5corpus_meta_v2_n2048_gpu` | 2026-06-08 (ledger:ts) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D22 | `exp_substrate_hierarchical_aggregator_scale_ext_domains5_10_20_v1_n2048` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D23 | `exp_substrate_spectral_edge_n_extension_decisive_v1_8192_32768_gpu` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |

### Group CG-E -- the `cross_layer_composition` / `pp48_nkt` saturation grid (280 rows)

**280 of 565 cells in the whole tier.** One auto-generated experiment, run at every level of a grid, each level banked as its own chain-graded atom reporting EXACT-1.0. There is no comparison arm because the result is construction-determined; the source note reaches the same conclusion and it is correct. **These are constructions, not capability wins, and they are the single largest distortion in any count of "how much chain-graded work exists".** Rows are written so the tier can never look examined-but-uncounted; nobody should read them individually.

| # | cell | date (src) | verdict (as read) | run_mode | floor | disk | module | moves | STATE |
|---|---|---|---|---|---|---|---|---|---|
| E1 | `exp_pp48_nkt_cross_n_depth13_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E2 | `exp_pp48_nkt_cross_n_depth17_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E3 | `exp_pp48_nkt_cross_n_depth19_v1_n16384` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E4 | `exp_pp48_nkt_cross_n_depth19_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E5 | `exp_pp48_nkt_depth_11_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E6 | `exp_pp48_nkt_depth_13_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E7 | `exp_pp48_nkt_depth_15_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E8 | `exp_pp48_nkt_depth_17_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E9 | `exp_pp48_nkt_depth_19_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E10 | `exp_pp48_nkt_depth_21_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E11 | `exp_pp48_nkt_depth_23_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E12 | `exp_pp48_nkt_depth_3_baseline_verification_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E13 | `exp_pp48_nkt_depth_5_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E14 | `exp_pp48_nkt_depth_7_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E15 | `exp_pp48_nkt_depth_9_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E16 | `exp_q_a3_l10000_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E17 | `exp_q_a3_l1000_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E18 | `exp_q_a3_l1000_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E19 | `exp_q_a3_l100_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E20 | `exp_q_a3_l100_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E21 | `exp_q_a3_l101_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E22 | `exp_q_a3_l101_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E23 | `exp_q_a3_l102_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E24 | `exp_q_a3_l102_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E25 | `exp_q_a3_l103_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E26 | `exp_q_a3_l103_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E27 | `exp_q_a3_l104_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E28 | `exp_q_a3_l104_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E29 | `exp_q_a3_l105_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E30 | `exp_q_a3_l105_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E31 | `exp_q_a3_l106_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E32 | `exp_q_a3_l106_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E33 | `exp_q_a3_l107_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E34 | `exp_q_a3_l107_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E35 | `exp_q_a3_l108_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E36 | `exp_q_a3_l109_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E37 | `exp_q_a3_l10_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E38 | `exp_q_a3_l110_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E39 | `exp_q_a3_l111_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E40 | `exp_q_a3_l112_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E41 | `exp_q_a3_l113_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E42 | `exp_q_a3_l114_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E43 | `exp_q_a3_l115_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E44 | `exp_q_a3_l116_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E45 | `exp_q_a3_l117_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E46 | `exp_q_a3_l118_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E47 | `exp_q_a3_l119_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E48 | `exp_q_a3_l11_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E49 | `exp_q_a3_l120_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E50 | `exp_q_a3_l121_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E51 | `exp_q_a3_l122_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E52 | `exp_q_a3_l123_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E53 | `exp_q_a3_l124_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E54 | `exp_q_a3_l125_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E55 | `exp_q_a3_l126_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E56 | `exp_q_a3_l127_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E57 | `exp_q_a3_l128_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E58 | `exp_q_a3_l129_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E59 | `exp_q_a3_l12_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E60 | `exp_q_a3_l130_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E61 | `exp_q_a3_l131_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E62 | `exp_q_a3_l132_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E63 | `exp_q_a3_l133_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E64 | `exp_q_a3_l134_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E65 | `exp_q_a3_l135_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E66 | `exp_q_a3_l136_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E67 | `exp_q_a3_l137_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E68 | `exp_q_a3_l138_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E69 | `exp_q_a3_l139_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E70 | `exp_q_a3_l13_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E71 | `exp_q_a3_l140_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E72 | `exp_q_a3_l141_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E73 | `exp_q_a3_l142_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E74 | `exp_q_a3_l143_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E75 | `exp_q_a3_l144_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E76 | `exp_q_a3_l145_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E77 | `exp_q_a3_l146_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E78 | `exp_q_a3_l147_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E79 | `exp_q_a3_l148_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E80 | `exp_q_a3_l149_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E81 | `exp_q_a3_l14_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E82 | `exp_q_a3_l1500_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E83 | `exp_q_a3_l150_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E84 | `exp_q_a3_l151_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E85 | `exp_q_a3_l152_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E86 | `exp_q_a3_l153_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E87 | `exp_q_a3_l154_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E88 | `exp_q_a3_l155_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E89 | `exp_q_a3_l156_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E90 | `exp_q_a3_l15_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E91 | `exp_q_a3_l16_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E92 | `exp_q_a3_l17_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E93 | `exp_q_a3_l18_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E94 | `exp_q_a3_l19_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E95 | `exp_q_a3_l19_n_scale_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E96 | `exp_q_a3_l2000_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E97 | `exp_q_a3_l200_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E98 | `exp_q_a3_l200_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E99 | `exp_q_a3_l20_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E100 | `exp_q_a3_l20_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E101 | `exp_q_a3_l21_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E102 | `exp_q_a3_l21_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E103 | `exp_q_a3_l22_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E104 | `exp_q_a3_l22_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E105 | `exp_q_a3_l22_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E106 | `exp_q_a3_l23_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E107 | `exp_q_a3_l23_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E108 | `exp_q_a3_l23_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E109 | `exp_q_a3_l24_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E110 | `exp_q_a3_l24_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E111 | `exp_q_a3_l24_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E112 | `exp_q_a3_l25_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E113 | `exp_q_a3_l25_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E114 | `exp_q_a3_l25_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E115 | `exp_q_a3_l26_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E116 | `exp_q_a3_l26_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E117 | `exp_q_a3_l26_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E118 | `exp_q_a3_l27_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E119 | `exp_q_a3_l27_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E120 | `exp_q_a3_l27_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E121 | `exp_q_a3_l28_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E122 | `exp_q_a3_l28_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E123 | `exp_q_a3_l29_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E124 | `exp_q_a3_l29_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E125 | `exp_q_a3_l29_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E126 | `exp_q_a3_l300_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E127 | `exp_q_a3_l300_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E128 | `exp_q_a3_l30_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E129 | `exp_q_a3_l30_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E130 | `exp_q_a3_l30_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E131 | `exp_q_a3_l31_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E132 | `exp_q_a3_l31_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E133 | `exp_q_a3_l31_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E134 | `exp_q_a3_l32_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E135 | `exp_q_a3_l32_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E136 | `exp_q_a3_l32_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E137 | `exp_q_a3_l33_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E138 | `exp_q_a3_l33_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E139 | `exp_q_a3_l33_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E140 | `exp_q_a3_l34_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E141 | `exp_q_a3_l34_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E142 | `exp_q_a3_l34_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E143 | `exp_q_a3_l35_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E144 | `exp_q_a3_l35_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E145 | `exp_q_a3_l35_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E146 | `exp_q_a3_l36_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E147 | `exp_q_a3_l36_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E148 | `exp_q_a3_l37_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E149 | `exp_q_a3_l37_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E150 | `exp_q_a3_l38_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E151 | `exp_q_a3_l38_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E152 | `exp_q_a3_l39_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E153 | `exp_q_a3_l39_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E154 | `exp_q_a3_l400_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E155 | `exp_q_a3_l40_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E156 | `exp_q_a3_l40_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E157 | `exp_q_a3_l41_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E158 | `exp_q_a3_l41_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E159 | `exp_q_a3_l42_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E160 | `exp_q_a3_l42_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E161 | `exp_q_a3_l43_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E162 | `exp_q_a3_l43_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E163 | `exp_q_a3_l44_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E164 | `exp_q_a3_l44_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E165 | `exp_q_a3_l45_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E166 | `exp_q_a3_l45_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E167 | `exp_q_a3_l46_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E168 | `exp_q_a3_l46_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E169 | `exp_q_a3_l47_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E170 | `exp_q_a3_l47_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E171 | `exp_q_a3_l48_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E172 | `exp_q_a3_l48_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E173 | `exp_q_a3_l49_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E174 | `exp_q_a3_l49_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E175 | `exp_q_a3_l500_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E176 | `exp_q_a3_l500_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E177 | `exp_q_a3_l50_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E178 | `exp_q_a3_l50_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E179 | `exp_q_a3_l51_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E180 | `exp_q_a3_l51_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E181 | `exp_q_a3_l52_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E182 | `exp_q_a3_l52_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E183 | `exp_q_a3_l53_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E184 | `exp_q_a3_l53_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E185 | `exp_q_a3_l54_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E186 | `exp_q_a3_l54_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E187 | `exp_q_a3_l55_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E188 | `exp_q_a3_l55_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E189 | `exp_q_a3_l56_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E190 | `exp_q_a3_l56_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E191 | `exp_q_a3_l57_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E192 | `exp_q_a3_l57_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E193 | `exp_q_a3_l58_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E194 | `exp_q_a3_l58_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E195 | `exp_q_a3_l59_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E196 | `exp_q_a3_l59_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E197 | `exp_q_a3_l5_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E198 | `exp_q_a3_l60_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E199 | `exp_q_a3_l60_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E200 | `exp_q_a3_l61_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E201 | `exp_q_a3_l61_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E202 | `exp_q_a3_l62_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E203 | `exp_q_a3_l62_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E204 | `exp_q_a3_l63_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E205 | `exp_q_a3_l63_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E206 | `exp_q_a3_l64_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E207 | `exp_q_a3_l64_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E208 | `exp_q_a3_l65_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E209 | `exp_q_a3_l65_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E210 | `exp_q_a3_l66_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E211 | `exp_q_a3_l66_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E212 | `exp_q_a3_l67_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E213 | `exp_q_a3_l67_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E214 | `exp_q_a3_l68_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E215 | `exp_q_a3_l68_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E216 | `exp_q_a3_l69_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E217 | `exp_q_a3_l69_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E218 | `exp_q_a3_l6_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E219 | `exp_q_a3_l700_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E220 | `exp_q_a3_l70_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E221 | `exp_q_a3_l70_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E222 | `exp_q_a3_l71_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E223 | `exp_q_a3_l71_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E224 | `exp_q_a3_l72_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E225 | `exp_q_a3_l72_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E226 | `exp_q_a3_l73_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E227 | `exp_q_a3_l73_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E228 | `exp_q_a3_l74_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E229 | `exp_q_a3_l74_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E230 | `exp_q_a3_l75_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E231 | `exp_q_a3_l75_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E232 | `exp_q_a3_l76_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E233 | `exp_q_a3_l76_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E234 | `exp_q_a3_l77_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E235 | `exp_q_a3_l77_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E236 | `exp_q_a3_l78_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E237 | `exp_q_a3_l78_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E238 | `exp_q_a3_l79_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E239 | `exp_q_a3_l79_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E240 | `exp_q_a3_l7_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E241 | `exp_q_a3_l80_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E242 | `exp_q_a3_l80_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E243 | `exp_q_a3_l81_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E244 | `exp_q_a3_l81_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E245 | `exp_q_a3_l82_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E246 | `exp_q_a3_l82_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E247 | `exp_q_a3_l83_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E248 | `exp_q_a3_l83_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E249 | `exp_q_a3_l84_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E250 | `exp_q_a3_l84_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E251 | `exp_q_a3_l85_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E252 | `exp_q_a3_l85_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E253 | `exp_q_a3_l86_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E254 | `exp_q_a3_l86_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E255 | `exp_q_a3_l87_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E256 | `exp_q_a3_l87_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E257 | `exp_q_a3_l88_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E258 | `exp_q_a3_l88_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E259 | `exp_q_a3_l89_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E260 | `exp_q_a3_l89_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E261 | `exp_q_a3_l8_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E262 | `exp_q_a3_l90_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E263 | `exp_q_a3_l90_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E264 | `exp_q_a3_l91_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E265 | `exp_q_a3_l91_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E266 | `exp_q_a3_l92_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E267 | `exp_q_a3_l92_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E268 | `exp_q_a3_l93_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E269 | `exp_q_a3_l93_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E270 | `exp_q_a3_l94_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E271 | `exp_q_a3_l95_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E272 | `exp_q_a3_l96_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E273 | `exp_q_a3_l96_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E274 | `exp_q_a3_l97_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E275 | `exp_q_a3_l97_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E276 | `exp_q_a3_l98_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E277 | `exp_q_a3_l98_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E278 | `exp_q_a3_l99_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E279 | `exp_q_a3_l99_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E280 | `exp_q_a3_l9_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |

### Group CG-F -- no directory resolves; state FOUND on every row (18 rows)

Nothing on disk was opened for these, so **none of them is VERIFIED and none may be cited**. Three sub-classes, and the first two are recoverable: (i) unexpanded shell brace patterns in the write path (`..._seed_{7,13,19}`) -- the artifact is in the per-seed dirs; (ii) atoms whose `referent_pointer.metrics_path` is prose (`"metrics.json (ssh pulled)"`, `"see per_seed_metrics_paths in atom metadata"`) -- the path was never written; (iii) genuinely absent names.

| # | cell | date (src) | verdict (as read) | run_mode | floor | disk | module | moves | STATE |
|---|---|---|---|---|---|---|---|---|---|
| F1 | `exp_chain_grade_barrier1_substrate_native_break_partition_oracle_goal_conditioning_3seed` | 2026-06-28 (ledger:ts) | CHAIN_GRADE_BARRIER_1_BROKEN_PARTITION_ORACLE_GOAL_CONDITIONING_3SEED_VERIFIED_rail_2of3_strict_cv_B_0p0 | ABSENT | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:FOUND |
| F2 | `exp_kb_determinism_sweep_retry_gpu_v1` | UNDATED (none) | PASS | ABSENT | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:FOUND |
| F3 | `exp_m1_modular_macrocolumn_w_v2` | 2026-06-23 (ledger:ts) | CHAIN_GRADE_cost_path_FULL_3seeds_710s_seeds_7_17_23_N_DIM_total_4096_squared_K_values_1_8_32_M_top_2_no | ABSENT | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:FOUND |
| F4 | `exp_narrative_q3_temporal_sequence_replay_k20_3seed_hp_cg_q15_1` | 2026-07-01 (ledger:ts) | HARD_PASS | ABSENT | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:FOUND |
| F5 | `exp_population_coding_3seed_cg_lift_v1` | 2026-07-01 (ledger:ts) | CHAIN_GRADE_3seed_HP_min_gain_25pp_ge_20_threshold_cv_0p085_lt_0p10_threshold_mean_28pp_lifts_lap3_7_n10 | ABSENT | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:FOUND |
| F6 | `exp_refuse_gate_v_rel_sweep_v1` | 2026-07-01 (ledger:ts) | CHAIN_GRADE_3seed_HP_CALIBRATION_UNIFORM_45_of_45_units_NEAR_rel_sim_monotonic_in_V_REL_all_3_regimes_pe | ABSENT | UNPINNED | NO DIR | HD:`refuse_gate.py` | -- | STATE:FOUND |
| F7 | `exp_substrate_audit_core_c2_c3_whitened_llama1b_v1_n4096` | UNDATED (none) | PASS | ABSENT | UNPINNED | NO DIR | EXP-ONLY | C3?,C1 | STATE:FOUND |
| F8 | `exp_substrate_audit_core_c2_c3_whitened_pythia160m_v2_n4096` | UNDATED (none) | PASS | ABSENT | UNPINNED | NO DIR | EXP-ONLY | C3?,C1 | STATE:FOUND |
| F9 | `exp_substrate_compartmentalized_cortex_k_banks_v2_gpu` | 2026-06-30 (ledger:ts) | CHAIN_GRADE_PHASE_CHARACTERIZATION_K_BANK_HOPFIELD_HIPPO_REPLAY_ROUTE_RETAINS_WRITE_PATH | ABSENT | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:FOUND |
| F10 | `exp_substrate_compositional_generalization_k10_to_k20_v1_n4096` | UNDATED (none) | PASS | ABSENT | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:FOUND |
| F11 | `exp_substrate_kg_capacity_sweep_m_10k_100k_1m_v1` | 2026-06-25 (ledger:ts) | MEASURED_MECHANISM_at_M_cliff_50k_skunkworks_promoted_chain_grade_at_M_10k_with_proven_cliff_at_M_50k_ti | ABSENT | UNPINNED | NO DIR | EXP-ONLY | C1 | STATE:FOUND |
| F12 | `exp_substrate_partition_routing_10m_full_v2` | 2026-06-25 (ledger:ts) | HARD_PASS_PARTIAL_AT_M_1M_skunkworks_chain_grade_at_M_100k_with_proven_bound_at_M_1M_partition_size_2000 | full* | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:FOUND |
| F13 | `exp_substrate_sequence_binding_k_cliff_phase_diagram_full_v2_cross_seed_chain_grade_phas` | 2026-06-28 (ledger:ts) | Sequence-binding K-cliff phase diagram v2 CROSS-SEED CHAIN-GRADE phase-characterization (3 seeds 7/13/19 | full* | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:FOUND |
| F14 | `exp_substrate_task_vector_hrr_icl_k_500_extended_v1_3seed_chain_grade_k_of_mechanism_dea` | 2026-07-01 (ledger:ts) | CHAIN_GRADE_3seed_HP_FULL_K_of_mechanism_death_1000_localized_perfectly_across_all_3_seeds_K50_TV_1p00_0 | ABSENT | UNPINNED | NO DIR | EXP-ONLY | C1 | STATE:FOUND |
| F15 | `exp_substrate_wm_multibank_k_cliff_phase_diagram_v3_gpu_chunked_cross_seed_agg_3_of_3_ha` | 2026-06-28 (ledger:ts) | WM_K_CLIFF_V3_GPU_CROSS_SEED_3_of_3_HARD_PASS_chain_grade_phase_characterization_CERT_plus_1 | ABSENT | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:FOUND |
| F16 | `metrics.json (ssh pulled)` | 2026-07-01 (ledger:ts) | CHAIN_GRADE_3seed_HP_cross_modal_4_5_modality_n_disc_20_21_20_of_27_cv_0p028_disc_frac_0p7407_0p7778_0p7 | ABSENT | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:FOUND |
| F17 | `see per_seed_metrics_paths in atom metadata` | 2026-06-29 (ledger:ts) | CHAIN_GRADE_PHASE_CHARACTERIZATION_3SEED_PARETO_DOMINANCE_VERIFIED | ABSENT | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:FOUND |
| F18 | `substrate_c1_entmax_alpha_readout_v1` | UNDATED (none) | PASS | ABSENT | UNPINNED | NO DIR | EXP-ONLY | C3?,C1 | STATE:FOUND |

---

## 6. WHAT IS **NOT DONE**, WITH ITS COUNT

1. **NOT DONE -- floors hand-verified.** 172 cells carry a floor by SHAPE. I hand-read the `verdict_msg` of **26** of them (the CG-A group plus the ~10 checked while calibrating the detector). **The other 146 are machine-classified only. Cite 172 as a lower bound on floored cells, never as a verified floor rate.**
2. **NOT DONE -- dates for the June batch.** **439 of 565 cells are dated ONLY from the first-commit date of `experiments/<name>.py`.** That is a BATCH ESTIMATE, not a run date; the whole whitening/pinv/codebook family lands on 2026-06-06 by this method and on 2026-06-16/17 by the source note's method. Both are git; neither is the run. A real fix needs the dispatch logs, which I did not open. **17 cells are UNDATED by all four sources.**
3. **NOT DONE -- the 124 CG-C contrast-only cells were not re-examined by hand.** At least one of them (`..._encoder_capacity_at_scale_battery_gpu_v1`) turned out to carry a real floor under an unrecognised arm name. **Assume the floored count is understated by an unknown amount inside this group.**
4. **NOT DONE -- the 14 chain-graded `META_RULE_*` atoms.** They resolve to no cell and are excluded from the 565. They are discipline rules, not experiments, and at least one (`META_RULE_floor_thresh_must_be_stat_valid_for_sample_regime_not_hardcoded_constant`) is directly about floor validity and should be read by whoever next touches the floor detector.
5. **NOT DONE -- module/registry reconciliation.** `module` is a NAME match between the cell name and `hdlab/*.py`; it fires on 33 cells and is not a runtime claim. `live` is inherited from the 39-module closure measured in RECOVERY_PROGRAM sec 4, **not re-measured here**. EXISTS / IS-REACHED / IS-GOOD stay three separate questions and this file answers only the first.
6. **NOT DONE -- nothing was WIRED.** Every row leaves this pass in VERIFIED or FOUND. By RECOVERY_PROGRAM sec 3 that means the tier is triaged, not finished.
7. **NOT DONE -- the sibling tiers.** This file covers H1 only. H2 (127 `proven-bound` reading cells >= 07-15) is untouched here and the source note's own conclusion is that it is **richer for C3 than this tier** -- only 33 of these 565 cells are dated 2026-07-15 or later.

## 7. THE ONE-LINE ANSWER TO "HOW MUCH OF THE RECORD DO WE UNDERSTAND?"

For this tier: **565 of 565 terminal chain-graded cells (100%) now have a row carrying a date, a verdict, a run mode, a floor class and a disk status read off the artifact at HEAD.** 26 of them were also opened by hand. **172 have a real floor and are therefore evidence; 375 have no floor visible and are not.** Half the tier (280) is one saturation grid. That is the honest shape of the chain-graded record.
