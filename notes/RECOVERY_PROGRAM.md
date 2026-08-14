# RECOVERY PROGRAM -- getting the leading systems back up and integrated

**LIVING DOCUMENT. Dateless filename by charter sec 2c. Updated IN PLACE, never re-dated, never
forked into a `_v2`.** Snapshots get dates; this does not. If you are a cold session: read sec 1,
then sec 3 (the rule), then run the two commands in sec 7, then work the ledger in sec 5.

Opened / created 2026-08-14. Last substantive update: 2026-08-14.

---

## 1. IN PLAIN LANGUAGE -- what happened and what this document is

Over roughly three months this project ran several thousand experiments. A lot of them worked.
The results were written to disk correctly. But the **way we searched for them was broken**, so
when we later asked "what do we already have?", the answer we got back was much smaller than the
truth -- and we kept rebuilding things we had already built.

The specific breakage is worth understanding, because it is not "we were careless":

> We looked for finished work by searching for **particular words** -- `HARD_PASS`, `scramble`,
> `chain_grade`. Those words changed over time. In June a control experiment was called
> `random_arm_pathology`; in August the same thing is called `scramble`. The word `scramble`
> appears **zero** times in June, yet **33 of 60** June experiments have a proper control. So the
> search said "June has no controls", and that answer was simply wrong. Separately, the highest
> quality tier ("chain-grade") is stored as a **field in a different file**, not as a word in the
> results -- so searching the results found 32 of them when there are about 574.

Four investigations on 2026-08-14 dug this out. Between them they found: a certification ledger of
2,031 rows nobody had opened; 97 fully-run, properly-controlled brain-mechanism experiments of
which 72 appear in **no** plan; a complete five-step recipe for building and reading the memory
store where **every single step is separately proven and the whole chain was never run once**; and
a measurement showing two genuinely different concepts stored with an **identical** memory vector.

**What this document is.** A single ledger, one row per recovered system, saying for each one:
where the evidence is, what it actually claimed, whether it had a proper control, whether we
opened it and confirmed it, whether it exists as real reusable code or only as a one-off
experiment, whether it is switched on today, and which of our four headline numbers it could move.
Each row carries a **STATE** word, and the job is finished when every row has left the starting
state. Section 7 gives the command that counts them, so nobody has to take anyone's word for it.

**What this document is not.** It is not a claim that the shelf is full of treasure. Several
"assets" turned out to be one-off experiment code with no reusable module behind them. Three of
five specially-flagged leads were wrong on inspection. Two thirds of the provenance links between
results are broken. Where something is unverified, this file says UNVERIFIED, and where a whole
tier was never examined, it says how big that tier is. **A plan that oversells the shelf repeats
the failure it exists to fix.**

---

## 2. THE FOUR SOURCES THIS PROGRAM CONSOLIDATES

Every row in sec 5 traces to one of these. They are complete as of 2026-08-14 and are frozen
inputs; this file is now the working surface.

| src | note | commit | what it contributes |
|---|---|---|---|
| **S1** | `notes/cert_ledger_triage_2026-08-14.md` | `c6cd948dc` | the 2,031-row cert ledger: **574 terminal chain-graded** claims, 552 with an artifact on disk, **155 Class-A floors** (a LOWER BOUND, not a rate); the never-run 5-stage recipe; cosine **1.0000** between two distinct concepts; **127 proven-bound reading cells never triaged** |
| **S2** | `notes/vscode_history_archaeology_2026-08-14.md` | `fb9882893` | 21 brain-mechanism families, **97 FULL floored passes, 72 invisible to all four planning docs**; zero-visibility families (k-WTA 17/17, attractor 12/12, Hebbian/STDP 4/4, cleanup 51/53, binding 42/49); the measurement-convention drift tables |
| **S3** | `notes/stack_review_lineage_2026-08-14.md` | `df4f9101a` | 14 whole-stack reviews since 2026-05-22 under 6 names; **57 modules self-test PASS and are off the live path, 24 with no registry row**; the capabilities that fell off across renames |
| **S4** | `notes/result_index_join_design_2026-08-14.md` + `tools/result_index_join.py` | `fa94a18e2` | registry indexes CODE, ledger indexes RESULTS, intersection **zero**; join key = result DIRECTORY NAME (96.4%); **6,566 of 7,623 results (86%) unindexed**; the shape-first drift alarm |

Supporting, already folded in: `notes/vscode_era_unrecognised_assets_2026-08-14.md` (`6b43be02d`,
the A1-A6 tier-1 shortlist) and `notes/vscode_week_results_validity_audit_2026-08-14.md`
(`0887b54f8`, closed -- attacked results, not re-litigated here).

---

## 3. THE STATE MACHINE -- what "done" means

Five states. Closed vocabulary. Every row in sec 5 carries exactly one, written literally as
`STATE:<WORD>` so it is machine-countable (sec 7).

| STATE | meaning | entry requirement -- what you must have DONE to write it |
|---|---|---|
| **FOUND** | named in a source, nothing checked | it appears in S1-S4. This is the starting state and is **not** evidence of anything |
| **VERIFIED** | opened on disk at HEAD | you opened the primary `metrics.json` (or the module file) with `.venv/Scripts/python.exe`, and recorded VERDICT + RUN_MODE + the floor arm **as they actually read**, not as a note reported them. Any disagreement with the source note is written into the row as a correction |
| **WIRED** | in the substrate and reachable | promoted to `hdlab/`, **observed inside a RUNTIME import closure** (never grep), and carrying a `data/capability_registry.jsonl` row. An opt-in module counts only if the named entry flag/kwarg is written into the row |
| **SHELVED** | verified, deliberately not wired | the row carries an explicit **revival criterion** -- the specific condition that would reopen it. No criterion = not SHELVED, still VERIFIED |
| **REFUTED** | verified and the claim does not hold | its own floor/control kills it, or a later cell replaced it, and the disproving number is quoted in the row |

**Legal transitions:** `FOUND -> VERIFIED -> {WIRED | SHELVED | REFUTED}`. Nothing skips VERIFIED.
`SHELVED -> WIRED` is legal when the revival criterion is met (say which). `WIRED -> SHELVED` is
legal but must cite the measurement that unwired it.

**Two states are terminal-good** (WIRED, REFUTED): the system is either in the substrate or is
provably not worth putting there. SHELVED is terminal-*conditional*. VERIFIED is a work-in-progress
state and a row sitting in it is unfinished business.

**DONE for this program** = zero rows in FOUND, and zero rows in VERIFIED. Not "everything WIRED":
wiring a refuted mechanism would be worse than leaving it alone.

### 3a. Column meanings (read once, then the tables are self-explanatory)

- **evidence** -- the primary artifact path. Result cells: `data/<dir>/metrics.json`. Modules:
  `hdlab/<name>.py`. Commit column omitted per-row because the load-bearing provenance is the
  **path plus the source-note commit in sec 2**; per-cell landing commits are recoverable with
  `git log -1 --format=%h -- <path>` and are not reproduced here (they are tier-1 re-derivable
  per `STATUS_SPEC.md` sec 3).
- **floor** -- the control arm as read from the file. `A` = explicit control/comparison arm.
  `PROSE` = the floor exists but lives inside `verdict_msg` text, not as a key. `ARM` = the floor
  is an arm NAME with no control word in it. `NO FLOOR` = none found and none claimed --
  **an unfloored pass is not evidence**. `UNPINNED` = not checked by me.
- **disk** -- `OK` (metrics.json opened today) / `NO DIR` (no directory resolves).
- **module** -- `HDLAB:<file>` (a reusable module exists) / `EXP-ONLY` (the capability exists only
  as experiment code and one output directory; "wire it" is really **build it**) /
  `NOT LOCATED` (claimed in an index, no artifact found under that name).
- **live** -- membership of the **runtime** import closure measured 2026-08-14 (sec 4). `LIVE` /
  `OFF-PATH`. **`OFF-PATH` means "not on the DEFAULT path", never "does not exist" and never
  "cannot be reached"** -- opt-in and lazily-imported modules are invisible to a default trace.
  EXISTS / IS-REACHED / IS-GOOD are three separate questions and are kept separate here.
- **moves** -- which scoreboard number it could move: `C1` near-neighbour 2AFC 0.698; `C2` context
  gap +0.1005; **`C3` read-out quality 4.80% vs 0.80% floor -- THE GATE, 5.2pp short of 10%**;
  `C4` coref 0.7193; `BOUND` = it constrains C3 rather than moving it; `--` = none.
- **supersede** -- `UNCHECKED` unless stated. This is the honest default: the ledger's supersession
  graph is **52 of 66 edges dangling** (S4) / **93 of 164 raw edges dangling** (S1), so no row here
  may be read as "survives unchallenged to HEAD" without its own check.

---

## 4. THE RUNTIME LIVE-PATH MEASUREMENT (2026-08-14, this session)

Measured, not grepped, per `CLAUDE.md` evidence-discipline sec 3:

```
.venv/Scripts/python.exe -c "import sys; import hdlab.reading_grounding_loop; \
  import hdlab.grounding_acquisition_loop; \
  print(sorted(m for m in sys.modules if m.startswith('hdlab.')))"
```

**39 `hdlab.*` modules** are in the closure of the two live entry points (the acquisition loop adds
**zero** beyond the reading loop's closure). The 39:

`ablation, animacy_lexicon, atoms, binding, bundling, cleanup_family, closed_class_lexicon,
consequence_learning_loop, coreference_resolver, event_bundle, frame_induction, gap_detector,
goal_typing, grounded_similarity, grounding_acquisition_loop, hd_fact_store, iterative_attractor,
learner (+core, +registry, +5 plugins), lexical_similarity, memory, modulators,
reading_grounding_loop, role_slot_summarizer, self_improving_loop, semantic,
situation_model_accumulate, snapshots, state_of_mind, thematic_role_labeler, tracing,
verb_lexical_similarity, working_memory`

**Not one recovered system in sec 5 is in that list.** That is the whole problem stated as one
measurement, and it is why the WIRED count starts at zero.

Registry measured the same session: **`data/capability_registry.jsonl` = 127 rows.** Registry
presence below is a NAME test (substring on `hdlab/<m>.py` or `"<m>"`); it can over- and
under-fire and is labelled as a name test wherever it is used.

---

## 5. THE RECOVERY LEDGER

**95 rows in seven groups** (A 14, B 11, C 16, D 25, E 12, F 12, G 5). Group H (sec 6) holds the
tiers too large to enumerate; **those are counted, not listed, and are explicitly
NOT-YET-TRIAGED.**

Of the 79 result artifacts opened on disk for these rows, **79 are git-tracked and committed**
(checked with `git log -1 --format=%h -- data/<dir>/metrics.json` per row; **0 UNCOMMITTED**), so
the bytes read are the bytes committed. The three names that resolved to **no directory** are
recorded in-row: C6's two mis-named siblings, D22's `..._c1_entmax_alpha_readout_v1`, and F4/F5/F7's
NOT LOCATED sources.

### Group A -- read-out / within-neighbourhood separation (bears on C3, THE GATE)

| # | system | evidence | claim (as read on disk) | floor | disk | module | live | moves | supersede | STATE |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | near-duplicate codebook diagnostic | `data/exp_substrate_codebook_near_duplicate_diagnostic_cpu_v1/metrics.json` | `HARD_PASS`, run_mode **full**, no `ts_iso`. 241 atoms @1024: **49 pairs cos>0.9; 54/241 (22%) have a near-neighbour above threshold; top pair cos = 1.0000 between `probability_space` and `measure_space`, two DISTINCT concepts**. De-dup at 0.95 -> F1 1.0000, F=3 cleanup **+0.1704** | A (near-dup floor 0.1333; de-dup vs full arm; 3 seeds, cv=0) | OK | EXP-ONLY | OFF-PATH | **C3** | UNCHECKED | STATE:VERIFIED |
| A2 | peel / SIC read-out on real codes | `data/exp_encoder_peel_sic_readout_realcodes_v1/metrics.json` | `HARD_PASS_PEEL_SIC_TRANSFERS_TO_REAL_CODES`, **full**, `ts_iso 2026-07-08T17:28:40`, 5 seeds. Flat argmax **0.204** -> peel/SIC **0.940**, lift **+0.736** (bar >=+0.2, cv 0.034) | A (flat argmax declared collapsed if <=0.7) | OK | **EXP-ONLY** -- `hdlab/peel_sic.py` **DOES NOT EXIST** (checked); the one `peel_sic` registry row describes community-bounded routing, a different thing | OFF-PATH | **C3** | UNCHECKED | STATE:VERIFIED |
| A3 | coarse-to-fine retained-trace requery | `data/exp_encoder_retained_trace_requery_coarse_to_fine_v1/metrics.json` | `HARD_PASS_RETAINED_TRACE_RECOVERS`, **full**, `2026-07-08T19:13:00`. Coarse shortlist (rand-proj D=128) then fine read inside it: `final_recall 0.992` against a full-fine **ceiling 0.992** (loses nothing) vs sparse max 0.561; `shortlist_hit@k=0.1 = 1.000` | A (sparse control 0.541 reproducing the v1 wall; Gate-D dense reproduce 0.9933) | OK | EXP-ONLY | OFF-PATH | **C3** | UNCHECKED | STATE:VERIFIED |
| A4 | dense Hopfield read-out, correlated codes | `data/exp_dense_hopfield_readout_capacity_correlated_codes_v1/metrics.json` | `HARD_PASS`, **full**, `2026-07-14T00:42:50`, seeds 7/13/19. **3.25x** capacity lift over pairwise on correlated codes; per-correlation 6.74x mild / 3.12x mod / **1.63x strong** | A (scramble collapses to 0.01; iid positive control 5.48x) | OK | HDLAB:`modern_hopfield_readout.py` (16,478 B, **no registry row** by name test) | OFF-PATH | **C3** | UNCHECKED | STATE:VERIFIED |
| A5 | DG pattern separation at write time | `data/exp_substrate_anisotropy_dg_pattern_separation_prewrite_v1/metrics.json` | `HARD_PASS`, **full**, **no `ts_iso`**, 3 seeds, real Pythia-2.8b keys. `dg_full 0.942` vs bar 0.50; effrank lift **10.08x**; off-diagonal mass 0.179 -> 0.012 | A (`uniform_no_presep` collapses to 0.083) | OK | HDLAB:`dg_pattern_separation.py` (11,526 B). **The registry's `pattern_separation` row points at `hdlab/hippocampal_encoder.py`, a DIFFERENT module** -- this one has no row | OFF-PATH | **C3** | UNCHECKED | STATE:VERIFIED |
| A6 | synonym-vs-sibling pooling interface | `data/exp_diag_learned_encoder_synonym_sibling_deep_wall_v1/metrics.json` | FULL verdict `MIDDLE_BAND_INTERFACE_SEPARATES_BUT_NOT_LEARNING`, **full**, `2026-08-12T03:10:56`. Trained AUC 0.7064 beats grounding 0.3186 -- **but randinit same-arch scores 0.7452, EQUAL OR BETTER**. Reading: the POOLING INTERFACE separates for free; the LEARNING claim is dead | A (scramble 0.5042 -> chance; randinit control) | OK | EXP-ONLY | OFF-PATH | **C3** | UNCHECKED | STATE:VERIFIED |
| A7 | semantic HD encoder meaning-match | `data/exp_semantic_hd_encoder_meaning_match_v1/metrics.json` | `MEANING_MATCH_PASS`, `2026-07-24T15:37:47`. **`run_mode` key ABSENT -- this may not be a FULL run and must not be quoted as one.** semantic AUC 0.960, separation 0.507 vs lexical floor **-0.400** | A (lexical/surface-form control) | OK | EXP-ONLY | OFF-PATH | C3 | UNCHECKED | STATE:VERIFIED |
| A8 | cue-clamped iterative cleanup | `data/exp_substrate_iterative_cleanup_cue_clamped_v1/metrics.json` | `HARD_PASS`, **`run_mode` ABSENT**, no date. Best clamped arm alpha=0.3 -> **0.2250** vs ARM_SINGLE_STEP 0.1500, lift +0.075. **Absolute numbers are low; the cell's own `WHAT_THIS_DOES_NOT_SHOW` says unproven at N=8192** | ARM (`ARM_SINGLE_STEP` / `ARM_CURRENT` are the floor) | OK | EXP-ONLY (but `hdlab/iterative_attractor.py` IS live -- the mechanism family already has a live home) | OFF-PATH | C3 (weak) | **contested by E11** | STATE:VERIFIED |
| A9 | resonator verifier read-out | `data/exp_resonator_verifier_readout_v1/metrics.json` | `HARD_PASS`, **full**, no date, 3 seeds. K4 harvest **0.806**, +0.353 over plurality 0.453 -- **and `oracle_any` = 0.806, i.e. it harvests EXACTLY the oracle and no more**. Ledger tier is `cert_neutral_*`, **NOT chain-grade** (S1 correction) | A (`baseline_K4` 0.133, plurality 0.453, oracle_any) | OK | EXP-ONLY | OFF-PATH | **BOUND** | UNCHECKED | STATE:VERIFIED |
| A10 | anchor-compose identity shuffle (+ scaling ladder) | `data/exp_anchor_compose_identity_shuffle_cskg_v2/metrics.json`; `..._scaling_ladder_cskg_v3/` | `HARD_PASS_INDUCTIVE_ANCHOR_COMPOSE_IDENTITY...` / `SCALING_HOLDS`, both **full**, `2026-07-13`. ANCHOR **0.1275** vs **ORACLE 0.1374** -- **93% of its own oracle**; ADDITIVE 0.0000, ONESHOT 0.0001 | A, unusually complete: RANDOM 0.0005, SCRAMBLE 0.0087, IDSHUF 0.0025, POPULARITY 0.0001, ORACLE 0.1374, n_q 3000 | OK | EXP-ONLY | OFF-PATH | **BOUND** | UNCHECKED | STATE:VERIFIED |
| A11 | metacognitive abstain / signal thresholding | `data/exp_metacog_abstain_readout_signal_thresholding_v1/metrics.json` | `HARD_PASS_EXISTING_SIGNAL_CARRIES_USABLE_CONFIDENCE`, **full**, `2026-07-20T02:08:36`. S1 reader-best-score HARD_PASS (rel_red 0.327 @ cov 0.5); **S3 and S4 HARD_FAIL -- `S4_cleanup_margin` carried no usable signal a month before the SNR-wall diagnosis** | A (`beats_rand=True, p=0.0, rand_p50 0.732`) | OK | EXP-ONLY | OFF-PATH | C3 (precision at partial coverage, **not** hit@1) | UNCHECKED | STATE:VERIFIED |
| A12 | hallucination detection (MiniLM) | `data/exp_substrate_hallucination_detection_minilm_v1/metrics.json` | `HARD_PASS`, **full**, no date. AUC **0.999** separating grounded from hallucinated; grounded_conf 0.204 vs hall 0.107 | ARM (the grounded-vs-hallucinated contrast IS the floor; **S1's lexical detector scored this Class D -- a detector false negative**) | OK | EXP-ONLY | OFF-PATH | C3 (precision) | UNCHECKED | STATE:VERIFIED |
| A13 | common-mode salience detector | `data/exp_attention_salience_common_mode_detector_v1/metrics.json` | `HARD_PASS_COMMON_MODE_DETECTOR_SEPARATES`, **full**, `2026-07-20T05:42:23`. Gap 0.0829, per-seed 5/5. **Explains why rank-1 common-mode removal returned HARD_FAIL_NO_EFFECT: the detector fires only in the correlated mode** | A (shuffle control quiet in both modes, 0.0001/0.0003) | OK | EXP-ONLY | OFF-PATH | C3 (diagnostic, not a lift) | UNCHECKED | STATE:VERIFIED |
| A14 | resonator peel family siblings | `data/exp_resonator_theta_gamma_peel_v1/`, `data/exp_resonator_deflation_lowsnr_v1/` | both `HARD_PASS`, both **full**, both undated | UNPINNED (not opened beyond verdict/run_mode) | OK | EXP-ONLY | OFF-PATH | C3 | UNCHECKED | STATE:VERIFIED |

### Group B -- the five-stage store recipe: every stage proven, the CHAIN NEVER RUN

This is S1's headline structural finding and it survives verification: `last-token pool ->
dimensional expansion -> whitening -> pseudoinverse write -> coarse-to-fine read` (A3 is the last
stage). Each stage below is separately terminal-chain-graded with an artifact on disk. **No cell
tests the chain end-to-end.**

| # | system | evidence | claim (as read on disk) | floor | disk | module | live | moves | supersede | STATE |
|---|---|---|---|---|---|---|---|---|---|---|
| B1 | last-token vs mean-pool x whitening | `data/exp_substrate_last_token_vs_whitening_mean_pool_v1/metrics.json` | `HARD_PASS`, **full**, no date, 3 seeds bit-identical. capacity `last_token_raw` **0** / `mean_pool_whiten` **40** / `last_token_whiten` **122**; best-combined **3.05x** | ARM (raw arm is the floor; **no arm name contains a control word -- S1 flagged this as its clearest lexical false negative**) | OK | EXP-ONLY | OFF-PATH | **C3, C1** | UNCHECKED | STATE:VERIFIED |
| B2 | PCA prewhitening of the codebook | `data/exp_substrate_pca_prewhitening_codebook_v1/metrics.json` | `HARD_PASS`, **full**, no date, 3 seeds. cap 3 -> 7 at N=384, ratio 2.33x. **DEFLATE HARD: the absolute capacities are 3 and 7 items.** "Universal real-encoder rescue" is the cell's own framing and n=7 does not support it | ARM (structurally recovered) | OK | EXP-ONLY | OFF-PATH | C3, C1 | UNCHECKED | STATE:VERIFIED |
| B3 | ETF / MiniLM dimensional expansion | `data/exp_substrate_etf_minilm_dim_expansion_v1/metrics.json` | `HARD_PASS`, **full**, no date. whitened cap D384 **844** -> D4096 **9011** (10.68x); within-D whitening gain 3.06x @D384, 1.29x @D1024/4096 | ARM | OK | EXP-ONLY | OFF-PATH | C3, C1 | UNCHECKED | STATE:VERIFIED |
| B4 | expansion + whitening STACK (no subsumption) | `data/exp_substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1/metrics.json` | `HARD_PASS`, **full**, no date. Expansion and whitening **stack**; production rule stated. **The "7000000000x" headline is a divide-by-zero (`expand_only = 0.0`). DO NOT PROPAGATE IT** | ARM | OK | EXP-ONLY | OFF-PATH | C3, C1 | UNCHECKED | STATE:VERIFIED |
| B5 | pinv write rule -- synthetic | `data/exp_hebb_vs_pseudoinverse_long_v1/metrics.json` | `HARD_PASS`, **full**, no date. N=4096: Hebb 0.050 -> pinv 0.550, **11.0x** (theory ~7x) | ARM (`{hebb_*, pinv_*}` pair; the Hebb arm IS the floor) | OK | EXP-ONLY | OFF-PATH | **C3, C1** | UNCHECKED | STATE:VERIFIED |
| B6 | pinv write rule -- Llama-L15 keys | `data/exp_pb_pinv_llama_l15_keys_v1/metrics.json` | `HARD_PASS`, **full**, no date. cap **122 -> 614 = 5.03x**. **This is the non-degenerate anchor of the family** -- not a divide-by-zero | ARM | OK | EXP-ONLY | OFF-PATH | **C3, C1** | UNCHECKED | STATE:VERIFIED |
| B7 | pinv write rule -- BGE-large keys | `data/exp_f6_bge_large_pinv_mmax_reaudit_v1/metrics.json` | `HARD_PASS`, **full**, no date. Hebb **0.000** -> pinv 0.550. Quote as *"Hebb reaches 0 where pinv reaches 0.55"*, **never as a ratio** | ARM | OK | EXP-ONLY | OFF-PATH | **C3, C1** | UNCHECKED | STATE:VERIFIED |
| B8 | pinv write rule -- E5-large keys | `data/exp_pb_e5_vs_bge_pinv_headtohead_v1/metrics.json` | `HARD_PASS`, **full**, no date. Hebb 0.000 -> pinv 0.550 | ARM | OK | EXP-ONLY | OFF-PATH | **C3, C1** | UNCHECKED | STATE:VERIFIED |
| B9 | pinv write rule -- MiniLM keys | `data/exp_pseudoinverse_real_encoder_keys_v1/metrics.json` | `HARD_PASS`, **full**, no date. Hebb 0.000 -> pinv 0.400. **Its own `verdict_msg` contains the literal figure "400000000x" -- an arithmetic artifact of x/0. Never quote it** | ARM | OK | EXP-ONLY | OFF-PATH | **C3, C1** | UNCHECKED | STATE:VERIFIED |
| B10 | learned KV projection | `data/exp_kv_learned_projection_v1/metrics.json` | `HARD_PASS`, **full**, no date. Held-out worst-seed recall **0.827** (std 0.019), key-separation 0.878, vs analytic ceiling 0.080 and **shuffled control 0.015**. This is the *missing-LEARNING* flavour, reusing `hdlab/learner` rather than a parallel build. `n_enc=2` | A (shuffled control 0.015, held-out split) | OK | EXP-ONLY | OFF-PATH | **C3, C1** | UNCHECKED | STATE:VERIFIED |
| B11 | the whitening module itself | `hdlab/whitening.py` | **EXISTS, 5,852 B.** **Not in the 39-module runtime closure. No registry row** by name test. Imported by `substrate/kv_memory.py` and ~28 `experiments/` scripts -- i.e. **the lever B1-B4 all depend on is islanded from the read-out path** | n/a | OK | HDLAB:`whitening.py` | **OFF-PATH** | C3, C1 | n/a | STATE:VERIFIED |

### Group C -- reading / construction competencies (C4, C2, and the reading arc)

| # | system | evidence | claim (as read on disk) | floor | disk | module | live | moves | supersede | STATE |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 | passive-voice who-did-what | `data/exp_consolidated_reader_passive_mechanism_heldout_v1/metrics.json` | `PASSIVE_MECHANISM_CAPABILITY_EARNED`, **full**, `2026-07-24T00:29:16`. **23/24 = 0.9583 vs naive 0/24**, margin +23, on INDEPENDENT held-out passages; flag ON/OFF **12/13 fired vs 2**; McGuffey composed F1 unchanged 0.5868. **The strongest single invisible result found in any source.** *Caveats: n=24 items / 13 passages; `n_seeds` null; the win is PARSER-side, so file it under reading, not C3* | A (`naive_acc = 0.0`, `naive_hash` for repro; P2 flag-OFF ablation) | OK | EXP-ONLY | OFF-PATH | C4 / reading | UNCHECKED | STATE:VERIFIED |
| C2 | consolidated reader -- in-domain demo | `data/exp_consolidated_reader_chaingrade_demo_v1/metrics.json` | `CHAIN_GRADE_DEMONSTRATED`, **full**, `2026-07-23T21:11:15`. Reader F1 **0.592** vs naive positional 0.3407 (+0.2513); glass-box replay/tamper/causal-edit all held | A (two baselines: naive positional 0.3407, `arm_a_baseline_svo` 0.2708) | OK | EXP-ONLY | OFF-PATH | reading | UNCHECKED | STATE:VERIFIED |
| C3 | consolidated reader -- held-out | `data/exp_consolidated_reader_chaingrade_FULL_v1/metrics.json` | `CHAIN_GRADE_HELDOUT_PARTIAL`, **full**, `2026-07-23T23:24:24`. **`chain_grade_heldout_earned = False`**; 2 of 4 bars held. LitBank held-out **reader 10/13 vs naive 11 -- the reader LOSES**. Together with C2 this is the in-domain-wins / held-out-attenuates shape the project **re-derived in August as the "entity-knowledge wall"** | A | OK | EXP-ONLY | OFF-PATH | reading | UNCHECKED | STATE:VERIFIED |
| C4 | consolidated reader -- hard syntax | `data/exp_consolidated_reader_hardsyntax_heldout_v1/metrics.json` | `CHAIN_GRADE_HARDSYNTAX_EARNED`, **full**, `2026-07-23T23:48:58`. Reader 4/24 vs naive **0/24**. **The cell itself calls this a small-N probe -- cite as a lead, not evidence** | A (true zero) | OK | EXP-ONLY | OFF-PATH | reading | UNCHECKED | STATE:VERIFIED |
| C5 | cross-sentence coref -- local window | `data/exp_read_xsent_coref_scene_protagonist_v1/metrics.json` | `HARD_PASS`, **full**, `2026-07-24T05:45:55`. Same-gender subset 0.4003 vs backbone 0.2462 (+0.1541). **`scene_structure_supported = False`: a dumb fixed-5-sentence window (0.4070) BEATS detected scenes (0.4003).** Commit `cba64a577` (2026-08-14) reached the same conclusion three weeks later from scratch | A (LOCALITY null, two arms: fixed5 0.4070, Kmean-random 0.3710) | OK | EXP-ONLY | OFF-PATH | **C4** | not superseded by the E3 Centering arc (different mechanism; corroborates) | STATE:VERIFIED |
| C6 | leak-proof relational inference | `data/exp_leakproof_relational_inference_heldout_v1/metrics.json` | `HARD_PASS`, **full**, `2026-07-26T20:10:03`. LEARNED 0.6534 vs RAW_GROUNDING 0.5459 (+0.1076); leak witness 0/22299. **NAME CORRECTION: S1 sec 5.2 #15 names the siblings `exp_leakproof_relational_inference_context_sweep_v1` / `_twonew_v1`; those directories DO NOT EXIST. The real names are `data/exp_leakproof_relinfer_context_sweep_v1` and `data/exp_leakproof_relinfer_twonew_v1`** | A, exemplary (RANDOM_INIT 0.5246, STRUCT_2HOP 0.5602, POPULARITY 0.5055, COLLAPSE 0.4978) | OK | EXP-ONLY | OFF-PATH | **C2** | UNCHECKED | STATE:VERIFIED |
| C7 | text-at-scale meaning learning | `data/exp_scale_meaning_learn_arc_heldout_v2/metrics.json` | `HARD_PASS_CLEAN_WIN`, **full**, `2026-07-27T16:01:25`. From-scratch text-at-scale beats grounding on held-out-NEW semantic: zavg 0.6469 vs raw 0.5968 | A (`RAW_TEXT-RANDOM = 0.1034`, per-seed min stated) | OK | EXP-ONLY | OFF-PATH | C3 (supply side) | UNCHECKED | STATE:VERIFIED |
| C8 | grounded inductive concept encoder | `data/exp_grounded_inductive_concept_encoder_heldout_new_v3/metrics.json` | `HARD_PASS`, **full**, `2026-07-26T16:22:42`. enc_poor 0.6741 vs aa_poor 0.4403 (+0.2339 vs bar 0.03), n=2024 power_ok | A | OK | EXP-ONLY | OFF-PATH | C3 | UNCHECKED | STATE:VERIFIED |
| C9 | encoder retrain at scale (assembly) | `data/exp_situation_model_assembly_encoder_retrain_scale_v1/metrics.json` | **CORRECTION: verdict is `CLEAN_PASS` and `run_mode` is `grid`, NOT "full".** `2026-07-31T09:23:53`. Retrain breaks the held-out-entity wall in `d1_div40`/`d1_div80`: all 3 query types >=0.60, `best_loop 0.830`, `name<->name frozen 0.057`. Its own verdict text ends **"ESCALATE TO SCALE"** -- an explicit un-taken next step | A (degenerate `d6` arm FAILS the guard -- a genuine can-fail control) | OK | HDLAB:`encoder_retrain_persist.py` (registered) | **OFF-PATH (opt-in by design -- this is the documented precedent, not an islanding)** | C3 (via anchors), C4 | UNCHECKED | STATE:VERIFIED |
| C10 | encoder transfer stress (harness swap) | `data/exp_encoder_alltype_transfer_stress_v1/metrics.json` | **CORRECTION: `run_mode` is `lite`, NOT "full".** `HARD_PASS`, `2026-08-01T01:27:38`. All 3 stress conditions clear lift >=0.05 on >=2 types incl. non-coref (c1_harder +0.108 / +0.142 / +0.231). It validates C9 rather than adding a lever -- **and a `lite` run is a weaker validation than the source note implies** | A (frozen vs tuned arms, held-out eval-draw, independent harness) | OK | HDLAB:`encoder_retrain_persist.py` | OFF-PATH (opt-in) | C4; C3 indirectly | UNCHECKED | STATE:VERIFIED |
| C11 | frame-order recovery under superposition | `data/exp_frame_order_recovery_hard_comprehension_v2/metrics.json` | `HARD_PASS`, **full**, `2026-07-06T15:05:37`. role->block ORDER recovered at 1.000 vs occupancy control 0.195; parse survives superposition at 0.800 | A (chance 0.167; occupancy control) | OK | EXP-ONLY | OFF-PATH | C4/C3 | UNCHECKED | STATE:VERIFIED |
| C12 | joint operator capstone | `data/exp_joint_operator_capstone_selective_readouts_v1/metrics.json` | `HARD_PASS_JOINT_OPERATOR_CAPSTONE_BOTH_SOLVED...`, **full**, `2026-07-15T23:36:19`. Two operators solved jointly, no interference (rel_drop -0.0061/0.0000); 9 declared gates all True | A (`SHUF 0.4222`, chance 0.52, freq 0.7778) | OK | EXP-ONLY | OFF-PATH | C3 (composition infra) | UNCHECKED | STATE:VERIFIED |
| C13 | read-grow relation identity | `data/exp_read_grow_relation_identity_v3_richness_sweep/metrics.json` | `HARD_PASS`, **full**, `2026-07-17T04:48:28`. failure-rate curve 0.267 -> 0.000; ablation control fired at every level | A | OK | EXP-ONLY | OFF-PATH | C2 | UNCHECKED | STATE:VERIFIED |
| C14 | whitening on the FACT STORE | `data/exp_hd_fact_store_semantic_capacity_whitening_v1/metrics.json` | verdict `MEASURED`, **`run_mode` ABSENT**, `2026-07-24T16:29:41`. **This is the closest thing to B1-B4's whitening lever already touching a live organ** (`hdlab/hd_fact_store.py` IS in the 39-module closure). **Read this before acting on B1** | UNPINNED (verdict is `MEASURED`, not a pass) | OK | related module HDLAB:`hd_fact_store.py` | **the fact store is LIVE; this whitening variant is not** | C3, C1 | UNCHECKED | STATE:VERIFIED |
| C15 | reader component oracle-ablation audit | `data/exp_reader_component_oracle_ablation_audit_v1/metrics.json` | `AUDIT_SANITY_OK`, **full**, `2026-07-23T20:07:04`. An audit artifact, not a capability claim | UNPINNED | OK | EXP-ONLY | OFF-PATH | -- | UNCHECKED | STATE:VERIFIED |
| C16 | multi-turn loop, oracle vs real | `data/exp_multi_turn_loop_realtext_oracle_vs_real_compounding_v1/metrics.json` | **CORRECTION: verdict is `HARD_FAIL`**, **full**, `2026-07-23T04:53:04`. S1 sec 5.3 lists it among cells "a C3 hunt must not skip" without saying it FAILED. It is a closed route, not a lead | UNPINNED | OK | EXP-ONLY | OFF-PATH | -- (closes a route) | UNCHECKED | STATE:REFUTED |

### Group D -- brain-mechanism organs from the zero-visibility families

| # | system | evidence | claim (as read on disk) | floor | disk | module | live | moves | supersede | STATE |
|---|---|---|---|---|---|---|---|---|---|---|
| D1 | k-WTA / sparsity free axis at production N | `data/exp_substrate_sparsity_free_axis_v5_wm_fixed_n4096_seed_7/metrics.json` | `HARD_PASS`, **full**, `2026-07-02T00:26:04Z`, 7 seed dirs, N=4096. `rho_c <= -0.60` at all 9 (M,alpha) pairs; cross-seed cv < 0.15. **Best-evidenced member of a family that is 17-of-17 invisible and has ZERO registry presence for `kwta`** (measured: 0 rows) | A -- rare explicit KEYS for this era (`hp_random_floor`, `positive_control_wm_ok`) | OK | EXP-ONLY | OFF-PATH | C3 (sparse coding is a first-order brain constraint) | UNCHECKED | STATE:VERIFIED |
| D2 | Hopfield attention inside a real LM | `data/exp_substrate_tier4_hopfield_attention_substitution_pythia160m_v1/metrics.json` | `HARD_PASS`, **full**, no date, 2 seeds. Substrate attention is training-stable inside Pythia-160M; **`ppl_ratio(substrate/baseline) = 0.94`** -- slightly BETTER perplexity than the attention it replaced. A `llama_3_2` sibling exists | A-weak (the baseline it is ratioed against; no separate scramble) | OK | related HDLAB:`modern_hopfield_readout.py` | OFF-PATH | C3 (architecture) | UNCHECKED | STATE:VERIFIED |
| D3 | Hopfield spurious-minima control | `data/exp_hopfield_spurious_minima_cpu_v1/metrics.json` | `HARD_PASS`, **run_mode `smoke`**, undated. genuine-convergence 0.957 (bar 0.90). **This is the specific safety property any Hopfield read-out must pass, and A4/D2 do not cite it** | PROSE | OK | EXP-ONLY | OFF-PATH | C3 (prerequisite control) | UNCHECKED | STATE:VERIFIED |
| D4 | sharp-wave ripple organ | `data/exp_hippocampal_sharp_wave_ripple_v1/metrics.json` | `HARD_PASS`, **run_mode `smoke`**, undated. `fidelity_fast 1.0000` vs **random 0.0857**; wrong_fidelity 0.0000. Registry term `ripple` = **0 rows** | PROSE (floor lives inside `verdict_msg`) | OK | EXP-ONLY | OFF-PATH | -- | UNCHECKED | STATE:VERIFIED |
| D5 | ACC / EVC adaptive halting | `data/exp_substrate_acc_evc_adaptive_halting_v1_smoke/metrics.json` | `HARD_PASS`, **run_mode `smoke`**, `2026-07-08T13:53:23`. `acc[FIXED 0.133 ADAPT 0.733 ORC 0.733]` -- **the adaptive arm EQUALS ITS ORACLE** with fewer hops; signal-specificity `corr[A=1.000 S=-0.071]`. **There is NO FULL run: `_v1` and `_v1_selftest` are SELFTEST_OK only.** Registry term `acc_evc` = 0 rows. Same decision the newly-landed foraging organ makes, and foraging's prereg does not cite it | ARM, inside `verdict_msg`: `accpc[FIXED ADAPT RAND SCR ORC]` | OK | EXP-ONLY | OFF-PATH | C3 / foraging | UNCHECKED | STATE:VERIFIED |
| D6 | integrated hippocampal stack (DG+CA3+Marr+CLS+replay) | `data/exp_substrate_concept_encoder_spoke3_dg_ca3_marr_cls_replay_v1_smoke/metrics.json` | `HARD_PASS`, **run_mode `smoke`**, `2026-07-02T23:46:48`. Five-way lesion ladder. **`after=0.000` on BOTH `MARR` and `NO_CONSOL` -- the consolidation arm did not retain**, consistent with E1/E2 | ARM (`CORTEX` / `NO_CONSOL` / `NAIVE_WTA` are the lesions; no key contains "control") | OK | EXP-ONLY | OFF-PATH | -- | UNCHECKED | STATE:VERIFIED |
| D7 | multi-hop PFC chunked decomposition | `data/exp_substrate_multihop_pfc_chunked_2hop_decomposition_v1_smoke/metrics.json` | `HARD_PASS_CHAIN_GRADE_BARRIER_1_VIA_CHUNKING`, **run_mode `smoke`** | UNPINNED | OK | EXP-ONLY | OFF-PATH | C2 | UNCHECKED | STATE:VERIFIED |
| D8 | heterogeneous plasticity / STDP fair harness | `data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness*/metrics.json` (resolved by prefix, 1 match) | `HARD_PASS`, **full**, no date. Built explicitly to be a fair test (see the name). Registry term `stdp` = **0 rows**; family 4-of-4 invisible | UNPINNED | OK | EXP-ONLY | OFF-PATH | learning layer | contested by E12 (the `_v2_RESCUE` HARD_FAILed) | STATE:VERIFIED |
| D9 | multi-scale grid-cell composition | `data/exp_crt_multi_scale_grid_cell_composition_v1/metrics.json` | `HARD_PASS`, **run_mode `smoke`**, undated. **NO FLOOR -- an unfloored pass is not evidence.** The entire entorhinal/grid family is this one cell | **NO FLOOR** | OK | EXP-ONLY | OFF-PATH | -- | UNCHECKED | STATE:VERIFIED |
| D10 | multi-bank working memory (K extension) | `data/exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1/metrics.json` | `HARD_PASS`, **full**, no date. naive random recall 0.0172 vs multi-bank **1.0000**, cv 0.0000, route_acc 1.0000, adversarial within 0.05 | A | OK | HDLAB:`situation_model_multibank.py` (8,044 B, **registered**) | OFF-PATH | C4 | UNCHECKED | STATE:VERIFIED |
| D11 | theory-of-mind Sally-Anne (nested HRR) | `data/exp_theory_of_mind_sally_anne_nested_hrr_v1/metrics.json` | `HARD_PASS`, **full**, `2026-06-28T04:33:44Z`. Gate-decided **WIRE** on 2026-08-05 and never executed. **The registry itself flags a naming defect here: a `state_of_mind.py` row is annotated "MISLABELED NAME, NOT Theory-of-Mind"** -- so this capability's registry trail is actively misleading | UNPINNED (source reports Q2 0.806 vs 0.138, oracle 1.0, 5 seeds -- **not re-read by me**) | OK | EXP-ONLY | OFF-PATH | C4 | UNCHECKED | STATE:VERIFIED |
| D12a | CLIP-era visual grounding coherence | `data/exp_visual_grounding_coherence_v1/metrics.json` | `HARD_PASS`, **`run_mode` ABSENT**, `2026-07-18T13:50:41`. chance 0.050, shuffled 0.074, T1 0.635 | A | OK | **EXP-ONLY -- "wire it" means BUILD it** | OFF-PATH | -- | UNCHECKED | STATE:VERIFIED |
| D12b | vision integrated recognize-bind-ground | `data/exp_vision_integrated_recognize_bind_ground_v1/metrics.json` | `HARD_PASS_INTEGRATED_PIPELINE__NOVEL_CLASS_WALL_CONFIRMED`, **full**, `2026-07-23T12:02:20` | A (chance 0.125, label-shuffle 0.189, SCRAM 0.386, word-scramble 0.143) | OK | EXP-ONLY | OFF-PATH | -- | UNCHECKED | STATE:VERIFIED |
| D12c | reader image-word grounding | `data/exp_reader_image_word_grounding_v1/metrics.json` | `PASS_GROUNDING`, **full**, `2026-07-22T00:28:57`. chance 0.0169; rungs 0.996 / 1.000 / 0.977 | A | OK | EXP-ONLY | OFF-PATH | -- | UNCHECKED | STATE:VERIFIED |
| D13a | MAVEN-ERE gated causal | `data/exp_maven_ere_convergence_gated_causal_v2_fulldev/metrics.json` | **`HARD-PASS` (HYPHEN)**, `run_mode` **`full_dev`**, `2026-08-11T09:19:45`. floor 5.93, scramble 3.48, full_v2 14.78. **Two convention traps in one row: the hyphen AND the `_fulldev` suffix** | A | OK | **EXP-ONLY -- BUILD** | OFF-PATH | C2 | UNCHECKED | STATE:VERIFIED |
| D13b | MAVEN-ERE gated subevent | `data/exp_maven_ere_convergence_gated_subevent_v1_fulldev/metrics.json` | `HARD-PASS`, `full_dev`, `2026-08-11T10:06:27`. floor 2.86, scramble 2.78, full_v2 13.63, transferred=True | A | OK | **EXP-ONLY -- BUILD** | OFF-PATH | C2 | UNCHECKED | STATE:VERIFIED |
| D14 | teacher-free relational encoder | `data/exp_teacher_free_relational_encoder_cn_subgraph_v1/metrics.json` | `HARD_PASS`, **full**, `2026-07-08T15:34:29`, 5 seeds. arm Z **497.90** vs random-init Z 148.97, control Z 21.42; ablation collapses | A | OK | **EXP-ONLY -- BUILD** | OFF-PATH | C3 (supply) | UNCHECKED | STATE:VERIFIED |
| D15 | gated fusion (+0.297) | `data/exp_grounding_gated_fusion_relation_inference_mammal_v1/metrics.json` | `HARD_PASS_GATED_FUSION_RECOVERS_GROUNDING`, **full**, `2026-07-14T03:26:29`. gated MRR **0.6619** vs relational 0.3645. **Gate-decided WIRE on 2026-07-28, tagged "TOP forgotten asset", and named in no plan document since** | A (RANDOM 0.0275, SCRAMBLE 0.5682, ORACLE 1.0) | OK | EXP-ONLY (4 registry rows mention it) | OFF-PATH | C2, C3 | UNCHECKED | STATE:VERIFIED |
| D16 | learned lexicon grounding at scale | `data/exp_lexicon_learned_grounding_scaled_v1/metrics.json` | `HARD_PASS`, **full**, no date. RANDOM 0.010 vs LEARNED 0.940 vs ORACLE 1.000 at V=200 | A | OK | EXP-ONLY | OFF-PATH | C3 (supply) | UNCHECKED | STATE:VERIFIED |
| D17 | social relational grounding axis | `data/exp_social_relational_grounding_axis_v1/metrics.json` | `HARD_PASS`, **full**, `2026-08-07T10:35:52`. scramble 0.483, ablation 0.000, open-vocab 0.833. **UNDERPOWERED: n=12 seed / 6+6 test. Ranked low deliberately** | A | OK | EXP-ONLY (registered) | OFF-PATH | C3 | UNCHECKED | STATE:VERIFIED |
| D18 | cleanup floor (learned encoder) | `data/exp_cleanup_floor_learned_encoder_v1/metrics.json` | `META_BRANCH3_CHAIN_GRADE_ELIGIBLE`, **full**, no date. Shannon floor holds across 3 codebook families (0.0217/0.0267/0.0150). **A negative-shaped positive: it establishes a FLOOR others can be scored against** | it IS a floor | OK | EXP-ONLY (registered) | OFF-PATH | C3 (scoring infra) | UNCHECKED | STATE:VERIFIED |
| D19 | RNS/CRT high-vocabulary decoder | `data/exp_generation_decoder_rns_crt_highvocab_v1/metrics.json` | `HARD_PASS`, **full**, `2026-07-05T18:46:21`. exact-ordered decode **1.000 at V=65536** where correlated single-block falls to 0.160 | A (`scram` collapses to 0.000; iid ceiling 1.000) | OK | EXP-ONLY | OFF-PATH | C3 (scale: 647 -> 5491 anchors) | UNCHECKED | STATE:VERIFIED |
| D20 | GSBC block-local factorizer | `data/exp_generation_decoder_gsbc_native_blocklocal_v1/metrics.json` | `HARD_PASS`, **full**, `2026-07-05T13:32:09`. block-local sparse 1.000 where the **dense bipolar resonator collapses to 0.000 on the same fillers**. Named finding: dense multiply-bind is the encoding mismatch | A (`dense_gsbc_fullreso 0.000` vs `dense_synth_fullreso 1.000`) | OK | EXP-ONLY | OFF-PATH | C3 (architecture) | UNCHECKED | STATE:VERIFIED |
| D21 | learned codebook generalisation gate | `data/exp_learned_codebook_generalization_gate_v1/metrics.json` | `HARD_PASS`, **`run_mode` ABSENT**, `2026-07-20T02:26:34`. ppmi_svd AUC 0.927+-0.001 vs random 0.496; 8M-token corpus, V=10000, N=1024 | A (`random` neg-control 0.496) | OK | EXP-ONLY (registered) | OFF-PATH | C3 (anchor quality) | UNCHECKED | STATE:VERIFIED |
| D22 | entmax sparse read-out envelope | `data/exp_c1_entmax_envelope_sweep_v2/metrics.json` | `HARD_PASS`, **full**, no date. 80/80 discriminating cells win on FLOPs at ISO-recall (median 94% reduction), **recall 1.000 vs 1.000, delta +0.000 -- it EXPLICITLY does not move C3 quality.** Listed so nobody mistakes "read-out WIN" in the title for a quality lift. Its sibling `exp_substrate_c1_entmax_alpha_readout_v1` has **NO DIRECTORY on disk** (confirmed) | B (contrast arms, envelope grid) | OK / sibling **NO DIR** | EXP-ONLY | OFF-PATH | -- (efficiency only) | UNCHECKED | STATE:VERIFIED |

### Group E -- refutations and closed routes (a negative prevents an expensive repeat; these are assets)

| # | system | evidence | claim (as read on disk) | floor | disk | module | live | moves | supersede | STATE |
|---|---|---|---|---|---|---|---|---|---|---|
| E1 | consolidation schedule -- conjunction | `data/exp_consol_conjunction_replay_v1/metrics.json` | `REFUTE_CONSOLIDATION_NO_SCHEDULE_ADVANTAGE_CONJUNCTION_IS_READOUT_EFFECT`, **full, 5 seeds**, `2026-07-15T12:40:33`. INTERLEAVED 1.0000 = CONTINUAL 1.0000, **schedule gap 0.0000**, compute_matched. Positively attributes the effect **to the READ-OUT** -- a July result pointing at the August C3 diagnosis. **ZERO cert-ledger rows: it never entered the certification system at all** | A, textbook: chance 0.5118, FREQ_NULL 0.4768, SHUFFLE 0.5192, MEMO 0.4768, ORACLE 1.0000 | OK | EXP-ONLY | n/a | closes a route | n/a | STATE:REFUTED (the hypothesis; the CELL is sound) |
| E2 | consolidation schedule -- inductive entity | `data/exp_consol_inductive_entity_replay_cskg_v1/metrics.json` | `REFUTE_REPLAY_NO_INDUCTIVE_ADVANTAGE`, **full, 5 seeds**, `2026-07-15T11:40:51`. Replay beats CONTINUAL (+0.0249) but **FAILS to beat popularity** (`beat_pop -0.0020`) -- and reports the failure rather than headlining the arm it won | A: RANDOM 0.0021, SHUFFLE 0.0026, SCRAMBLE 0.0274, POP_RELFREQ 0.0576, ORACLE 0.1030 | OK | EXP-ONLY | n/a | closes a route | n/a | STATE:REFUTED (the hypothesis) |
| E3 | interleaved replay sibling | `data/exp_consol_interleaved_replay_v1/metrics.json` | **CORRECTION: verdict is `HARD_PASS`, full, `2026-07-15T02:51:27`** -- S1 sec 6.3 groups all three 07-15 replay cells as "three properly-floored July refutations". Two are refutations; **this one is a PASS** | UNPINNED | OK | EXP-ONLY | OFF-PATH | -- | UNCHECKED | STATE:VERIFIED |
| E4 | SSP phase-rotation replay operator fix | `data/exp_course_c_operator_fix_ssp_phase_rotation_replay_v1/metrics.json` | `OPERATOR_FIX_CONFIRMED_CONSOLIDATION_INCONCLUSIVE`, **full**, `2026-07-11T03:46:40`. Third independent July result against consolidation advantage | UNPINNED | OK | EXP-ONLY | n/a | closes a route | n/a | STATE:VERIFIED |
| E5 | ATL hub-and-spoke, gen 1 | `data/exp_substrate_hub_spoke_E1_encoder_v1/metrics.json` | **`HARD_FAIL`**, **full**, no date | A | OK | EXP-ONLY | n/a | -- | n/a | STATE:REFUTED |
| E6 | ATL hub-and-spoke, gen 2 | `data/exp_substrate_hub_spoke_E1_v2_diverse_algorithm/metrics.json` | **`MIDDLE_BAND`**, **full**, no date | A | OK | EXP-ONLY | n/a | -- | n/a | STATE:REFUTED |
| E7 | ATL hub-and-spoke, gen 3 | `data/exp_substrate_hub_spoke_E1_v3_MRC_calibrated_routing/metrics.json` | **`HARD_FAIL`**, **full**, no date. **Three in-house refutations of our own ATL implementations. `notes/lit_scan_atl_hub_and_spoke_2026-08-13.md` was commissioned on the same mechanism and cites NONE of them** -- so the scan could not do its most valuable job, which is to explain WHY they failed. Registry term `hub_spoke` = 0 rows | A | OK | EXP-ONLY | n/a | (ATL is the brain's answer to C3's exact defect -- these say our version of it does not work yet) | n/a | STATE:REFUTED |
| E8 | cerebellum SR rollout | `data/exp_pfc_gate_cerebellum_sr_rollout_v1_smoke/metrics.json` | **`HARD_FAIL_NO_CEREBELLAR_CONSUMER`**, smoke, `2026-07-07T18:16:38`. **The verdict string IS the finding: a machine-readable record of the islanding failure mode.** Registry term `cerebell*` = 0 rows | A | OK | EXP-ONLY | n/a | -- | n/a | STATE:REFUTED |
| E9 | cerebellar random expansion write | `data/exp_substrate_cerebellar_random_expansion_write_v1/metrics.json` | **`HARD_FAIL`**, smoke, no date | A | OK | EXP-ONLY | n/a | -- | n/a | STATE:REFUTED |
| E10 | binding operator x capacity | `data/exp_substrate_binding_op_x_capacity_v1_seed_7/metrics.json` | **`HARD_FAIL`**, **full**, `2026-07-01T04:18:36Z`. HARD_FAIL on all three seeds (7/13/19) -- a well-replicated negative, equally invisible | A | OK | EXP-ONLY | n/a | -- | n/a | STATE:REFUTED |
| E11 | iterative settling with depth | `data/exp_grounding_iterative_settling_cascade_depth_v1/metrics.json` | **`HARD_FAIL_NO_EXTENSION`**, **full**, `2026-07-09T13:05:45`. **This is the closest thing to a prior refutation of A8** (cue-clamped iterative cleanup) and no sweep hunting passes would ever have surfaced it | UNPINNED | OK | EXP-ONLY | n/a | contests A8 | n/a | STATE:REFUTED |
| E12 | PCGrad + CFRPE + STDP rescue | `data/exp_substrate_pcgrad_cfrpe_stdp_v2_RESCUE/metrics.json` | **`HARD_FAIL`**, **full**, no date. The rescue attempt on the STDP arc failed. The `_RESCUE` suffix is itself a convention no current search knows | UNPINNED | OK | EXP-ONLY | n/a | contests D8 | n/a | STATE:REFUTED |

### Group F -- capabilities that fell off across the six review renames (module plane)

| # | system | evidence | claim | floor | disk | module | live | moves | supersede | STATE |
|---|---|---|---|---|---|---|---|---|---|---|
| F1 | `glass_box_loop` | `hdlab/glass_box_loop.py` | **EXISTS, 19,174 B.** No registry row (name test), **not in the 39-module closure**, zero importers, no `data/*glass_box_loop*` directory. `architecture_audit_2026-08-11` item 7 names it as *exactly* the arbitration/fusion that `three_tier_loop.answer()` lacks (Gap G1), validated on real ConceptNet V=48000. **The capability CLAIM is unverified by me -- only the file's existence and its off-path status are** | UNPINNED | file OK, **no result dir found** | HDLAB:`glass_box_loop.py` | **OFF-PATH** | C2/C3 (arbitration) | n/a | STATE:VERIFIED (existence + off-path) / claim UNVERIFIED |
| F2 | `wordnet_polarity_propagation` | `hdlab/wordnet_polarity_propagation.py` | **EXISTS, 16,922 B.** No registry row, not in closure. Reported (S3) as **the repo's ONLY live dictionary lookup** (`nltk.corpus.wordnet`). Given the open defect is lexical within-neighbourhood separation, a dictionary path no plan knows about is directly on topic | UNPINNED | file OK | HDLAB | **OFF-PATH** | **C3** | n/a | STATE:VERIFIED (existence) / claim UNVERIFIED |
| F3 | `word_learning_tool` | `hdlab/word_learning_tool.py` | **EXISTS, 6,504 B.** Not in closure. Its one landed evaluation **HARD_FAILED**; the tool itself self-tests PASS. Do not read the tool's existence as a capability | UNPINNED | file OK | HDLAB | OFF-PATH | -- | n/a | STATE:VERIFIED (existence) |
| F4 | `sr_routing` multihop (+0.253) | registry row only | Registry status `orphaned_source_not_locatable_retired_2026-08-03`. **I searched `data/*sr_routing*` and found NOTHING; no `hdlab/sr_routing.py`.** The integration ledger says git-recover before reinventing. **Until the source is located this is a CLAIM, not an asset** | UNPINNED | **NOT LOCATED** | **NOT LOCATED** | n/a | C2 | n/a | STATE:FOUND |
| F5 | `scale_win` TinyTransformer encoder | 3 registry rows | Learned from scratch on 237.7M ARC tokens; claimed "+0.050 semantic / +0.071 relational" over grounding; gate=WIRE, status `TRAPPED_SHARED`, zero `hdlab` imports. **No `data/*scale_win*` directory exists.** **EXPERIMENT-ONLY -- "wire it" means BUILD it.** Flagged in `architecture_audit_2026-08-11` as half of the **#1 shore-up** | UNPINNED | **no dir under this name** | **BUILD** | n/a | C3 | n/a | STATE:FOUND |
| F6 | 39,707-word grounding norms | `data/grounding_testbed` | Lancaster sensorimotor + Brysbaert concreteness + Warriner VAD + AoA. The other half of the 08-11 **#1 shore-up**; a grep-confirmed disconnected island. **Directory contents not enumerated by me** | n/a (a data asset, not a claim) | UNVERIFIED | data asset | OFF-PATH | C3 (supply) | n/a | STATE:FOUND |
| F7 | `vamp_ep_deep_chain_solver` | 1 registry row | "The repo's best deep-chain mechanism", acc 1.000 to depth ~200, K=5000, 30% noise. SHELVE with revival = NL causal-chain transfer smoke; never revisited. **`data/*vamp*` returns only SVAMP math cells -- a NAME COLLISION, not this asset.** Source not located under that name | UNPINNED | **NOT LOCATED** | NOT LOCATED | n/a | C2 | n/a | STATE:SHELVED -- revival criterion (from the 08-04 integration ledger): **an NL causal-chain transfer smoke.** Locate the source first |
| F8 | `k_cliff_scaling`, `profiling` | `hdlab/k_cliff_scaling.py` (1,940 B), `hdlab/profiling.py` (2,134 B) | **Both EXIST and both are REGISTERED.** They are the only two modules that have **provably never executed** (S3). Flagged for quarantine on 2026-07-25; still not quarantined | n/a | OK | HDLAB, registered | OFF-PATH | -- | n/a | STATE:SHELVED -- revival criterion: **none. Quarantine candidates; delete only via a deliberate maintenance pass, never bundled with other work** |
| F9 | the "24 unregistered self-test-PASS modules" | `hdlab/*.py` | **CORRECTION, measured today: 8 of the 24 now CARRY a registry row** (`context_retention, coref_distractor_suppress, definitional_predicate_v61, event_centrality_coref, goal_outcome_relation_grounded, outcome_event_extraction, script_grain_acquisition_loop, semantic_parser`). **16 still do not** (`atom_consultation, bayesian_inference, char_positional_encoder, clarify_gate, conformal, dg_pattern_separation, glass_box_loop, late_combine, mcscript_extraction, modern_hopfield_readout, noise_channel, per_item_log, perceptron, temporal_trace, word_learning_tool, wordnet_polarity_propagation`). **All 24 files exist. NONE of the 24 is in the 39-module closure.** *Caveat: registry presence is a NAME substring test and can mis-fire both ways* | n/a | OK (24/24 files exist) | HDLAB x24 | **0 of 24 LIVE** | mixed | n/a | STATE:VERIFIED |
| F10 | `situation_model_multibank`, `encoder_retrain_persist` | `hdlab/*.py` | Both EXIST (8,044 B / 5,639 B), both **REGISTERED**, both **OFF the default path**. `encoder_retrain_persist` is the documented **opt-in-by-design** precedent -- do not report it as islanded | n/a | OK | HDLAB, registered | OFF-PATH (one opt-in, one unclassified) | C4 / C3 | n/a | STATE:VERIFIED |
| F11 | `pipeline_status` field integrity | `data/capability_registry.jsonl` (127 rows measured today) | Wrong in **BOTH** directions (S3): 3 rows claim `WIRED_AND_PIPELINE_USED` and are not in the closure; **19 claim unreachable and ARE reachable, including `reading_grounding_loop` -- the pipeline entry point itself**; 13 modules sit inside the closure with no row, including `grounding_acquisition_loop`. **A compliance audit run against the registry cannot see the live path** | n/a | OK | infrastructure | n/a | -- | n/a | STATE:VERIFIED |
| F12 | measurement columns retired across renames | `notes/research_substrate_load_bearing_capability_assessment_2026-06-25.md` and the 07-25 integration audit | Three columns present in an old review and in **no** current one: **theoretical limit / closed-form bound per capability** (the exact column that settles "ceiling vs impl-bug"); **"truly enabling? YES/PARTIAL/NO"**; **bypass ratio** (4133/5327 = 78% of exp cells bypass `hdlab`, never recomputed). Plus **PP-217/225/226/227/228** (Tier A, 06-11) which have no successor identifier in any current scheme | n/a | note paths exist | n/a | n/a | -- | n/a | STATE:FOUND |

### Group G -- the index machinery itself (fix these or everything above goes dark again)

| # | system | evidence | claim (as read on disk) | disk | STATE |
|---|---|---|---|---|---|
| G1 | the cert ledger | `data/substrate_index/meta/cert_ledger.jsonl` | 2,031 rows, 0 malformed, **>200 distinct top-level fields, not one present on all rows**. `cert_status` has **357 distinct values** -- not an enum. **574 terminal chain-graded cells; 552 with a live `metrics.json`.** File mtime says 2026-08-03 but the **newest ROW timestamp is 2026-07-25 (21 days stale)** -- the last write was not a last result. Only 157 of 2,031 rows carry a string `ts`. **Recommendation (S4): salvage the 14 resolving `supersedes` edges, freeze the rest read-only with a superseded-by pointer** | OK | STATE:VERIFIED |
| G2 | the supersession graph | same file | 15 fields carry supersession semantics, **164 raw edges; 93 dangle** (32 point at 16-hex content hashes that occur exactly ONCE in the whole 4.5 MB file and resolve to nothing; 61 are self-edges). By S4's count, **52 of 66 edges dangle**. Net effect: supersession removes almost nothing (2 cells). **Liveness must be derived from the LATEST RULING PER CELL, never from the citation graph** | OK | STATE:VERIFIED |
| G3 | the capability registry | `data/capability_registry.jsonl` | **127 rows** (counted today). Indexes CODE. **Intersection with the ledger's result universe = ZERO** -- they were never two views of one thing, so "make them agree" was never the right goal | OK | STATE:VERIFIED |
| G4 | the derived result index | `tools/result_index_join.py`, reports in `data/result_index_reports/` | Join key = result DIRECTORY NAME (96.4%); `atom_id` joins **0/1925**. On disk **7,623** results; **6,566 (86%) unindexed**; 5,136 undated; 53 dangling ledger keys (mostly unexpanded shell brace patterns written literally into the index). **Derived from disk every run -- there is nothing to remember to do, so there is nothing to forget.** Wired into `tools/session_start_hook.py` | OK, runs | **STATE:WIRED** |
| G5 | the 2026-06-25 archaeology tooling | `data/_archaeology_extractor.py`, `_archaeology_synthesize.py`, `_archaeology_inventory_enriched.jsonl` (2.4 MB), `_archaeology_summary.json` | A USER-directed archaeology sweep with almost this exact brief ran on **2026-06-25**; its tooling and its 3,269-experiment enriched inventory are still on disk and **were never read by any 08-14 sweep**. Its own conclusion then: *"2026-06 HARD_PASS NOT in cert ledger at all: 841 (65%)"*. **Today's finding is the same leak one stage downstream and worse.** Its headline numbers are QUOTED, never recomputed | files exist | STATE:FOUND |

---

## 6. Group H -- NOT-YET-TRIAGED TIERS (counted, sampled, explicitly NOT examined)

**These are the honesty backstop. Each line states the tier size, how much of it was actually
looked at, and what remains. Nothing here may be described as reviewed.**

| # | tier | size | sampled / triaged | NOT-YET-TRIAGED | why it matters |
|---|---|---|---|---|---|
| H1 | terminal chain-graded cells in the cert ledger | **574** | 30 slots ranked in S1 sec 5 (covering ~24 distinct entries, several of which are multi-cell families); **28 of their directories re-opened on disk by me** | **~546** | the assigned tier; but only 35 of 574 are dated >= 07-15, so it is mostly June/early-July substrate physics |
| H2 | `proven-bound` reading/grounding cells dated >= 07-15 | **127** (120 with a Class-A floor) | 6 named, **4 opened by me** (C14, C15, C16, A7) | **~121** | **S1's own conclusion is that this tier is probably RICHER for C3 than the chain-graded tier.** It is the obvious next pass and it has never been done |
| H3 | FULL + floored + invisible brain-mechanism passes | **72** (of 97 FULL, of 251 floored) | 9 hand-verified in S2 (its V1-V9); **12 brain-family cells re-opened by me, of which only 4 are in the FULL-72 set** (D1, D2, D8, D10) -- the other 8 are SMOKE-only and were never in the 72. **Overlap between S2's nine and my four was NOT computed** | **at least 59; exact residue uncomputed** | the tightest form of "we missed a lot"; families k-WTA / attractor / Hebbian-STDP / cleanup / binding are at or near zero visibility |
| H4 | results on disk absent from every index | **6,566 of 7,623 (86%)** | 0 individually | **6,566** | the derived index (G4) now SEES them; nobody has read them |
| H5 | drift-alarm results: comparison SHAPE, no recognised floor token | **2,009 of 7,623 (26.4%)** | 0 individually | **2,009** | this count IS the vocabulary-drift alarm (sec 8). It is currently FIRING |
| H6 | dangling 16-hex `supersedes` targets | **32** | 0 | **32** | 4 `cert_ledger.jsonl.bak_*` backups (1.2 MB each, 07-01/02) were never searched; they may hold the superseded rows |
| H7 | passes with NO floor anywhere | **1,653** | 0 | **1,653** | **these are NOT evidence** and are ranked below everything floored. Listed so the tier is visible, not so it is worked |
| H8 | undated results | **5,193 of 7,649 (68%)** | 0 dated | **5,193** | **not a dating gap -- a DIFFERENT HARNESS GENERATION** (leads with `n_seeds`/`per_seed`/`config`, carries `anchor_name` on only 3,053). No current tool matches its conventions |
| H9 | session transcripts | **10,214 `.jsonl`, 6,070 MB** | ~1,000 parsed; the 3.0 GB main file DID complete (658,273 records, continuous 2026-05-31 .. 2026-08-12) | **~9,200 subagent files** | the only source that can answer WHY things were parked. Parser exists: `scratch/arch_scan.py`; outputs land in `scratch/arch_out/` |
| H10 | whole-stack reviews, content | **14-15 reviews since 2026-05-22** | filenames censused; **1 opened (2026-06-25, first 3,000 chars)** | **~13** | each review started over rather than extending the last. `notes/system_accounting_2026-08-13.md` is the most recent whose content is NOT folded into any current doc |

**Standing rule for this section: a tier moves out of H only by being enumerated, never by being
sampled.** If a pass reads 40 of 127 cells, the row becomes "40 triaged / 87 NOT-YET-TRIAGED". It
does not become "reviewed".

---

## 7. HOW WE MEASURE PROGRESS -- two commands, no one's word for it

### 7a. The primary number: STATE counts off this file

```bash
cd /d/AI/hd-instrument && grep -oE 'STATE:(FOUND|VERIFIED|WIRED|SHELVED|REFUTED)' notes/RECOVERY_PROGRAM.md | sort | uniq -c
```

**Baseline at open (2026-08-14), produced by running exactly that command:**

| STATE | count | of 95 |
|---|---|---|
| FOUND | 5 | 5.3% |
| VERIFIED | **76** | 80.0% |
| WIRED | **1** | 1.1% |
| SHELVED | 2 | 2.1% |
| REFUTED | 11 | 11.6% |

The two numbers that must move: **WIRED/95 goes UP** and **VERIFIED/95 goes DOWN** (every VERIFIED
row must exit to WIRED, SHELVED or REFUTED). FOUND must reach **0** first -- an unverified row is
not an asset. The sum must always equal the row count; if it does not, a row lost its STATE token.

> **COUPLING NOTICE (per `CLAUDE.md` "a doc parsed by code is coupled to it"):** the literal token
> `STATE:` and the five state words are an **API** for the command above. If they are reworded, the
> counting command in this section must change in the same commit. Do not introduce a sixth state
> without updating sec 3, this section, and the baseline table together.

### 7b. The disk-derived number: the index that nobody has to remember to update

```bash
cd /d/AI/hd-instrument && .venv/Scripts/python.exe tools/result_index_join.py --hook   # 0.6s, reads the persisted report
cd /d/AI/hd-instrument && .venv/Scripts/python.exe tools/result_index_join.py --scan   # ~290s, recomputes and persists
```

`--hook` output at open, verbatim:

```
[result-index] last join 0.3h ago
    on_disk=7623 undated=5136 orphans=6566 ledger_dangling=53
    DEFECTS: cert_ledger STALE: newest ts 2026-07-25 is 21 days old; FLOOR VOCABULARY DRIFT:
    2009 results have a comparison SHAPE but no recognised floor token
```

**Targets, in priority order:** `orphans` DOWN from 6,566; the `FLOOR VOCABULARY DRIFT` line
resolves as `FLOOR_TOKENS` is widened (sec 8); `ledger_dangling` DOWN from 53 (those are write-side
bugs -- unexpanded shell brace patterns -- now visible). This probe is already in
`tools/session_start_hook.py`, so **it reports itself at every session start, compaction included**,
and its own staleness is part of the report.

### 7c. What a completed row looks like

A row is only allowed to leave VERIFIED with the evidence attached in the row itself:

- **-> WIRED**: name the `hdlab/` module, name the registry row, and paste the RUNTIME closure line
  showing it (sec 4's command, re-run). Not a grep. Not "it should be imported".
- **-> SHELVED**: write the revival criterion as a testable condition ("when a narrative
  multi-sentence reading pipeline exists", not "later").
- **-> REFUTED**: quote the number that kills it and cite the file it came from.

---

## 8. ANTI-RECURRENCE -- detect by SHAPE, never by vocabulary

The cause is measured, so the fix is measured too. **The rule is NOT "search harder".**

**What actually happened.** Every sweep searched `metrics.json` by verdict string. That method is
structurally blind to: a `cert_status` **FIELD** in a different file (the whole 574-cell ledger); a
hyphenated `chain-grade` (10 rows, plus `proven_bound` 35 and `honest-negative` 11 -- **56 rows lost
to punctuation inside a single field of a single file**); an anchor **NAME** containing "chaingrade"
(which produced a confidently-reported "07-23 chain-grade reader triple" that **does not exist** --
two of the three are `proven-bound` and the third has no `cert_status` at all); `_fulldev` /
`_smoke` suffixes; and June's floors entirely -- **`scramble` appears ZERO times in June while 33 of
60 June cells have a genuine control arm.** Verdict vocabulary went **13 distinct strings in June to
444 in July** (one new string per four runs), and **1,357 results carry a verdict with no PASS or
FAIL token at all**; **218 have no `verdict` key whatsoever**. Floors are frequently not keys but
PROSE inside `verdict_msg` (`vs random=0.0857`) or bare ARM NAMES (`CORTEX / NO_CONSOL /
NAIVE_WTA`).

**Therefore, four binding rules.**

1. **SHAPE FIRST, VOCABULARY SECOND, AND COMPARE THE TWO.** A floor is detected by
   `shape_arms_dict` (>=2 sibling dicts sharing a numeric key) and `shape_token_pair` (>=2 sibling
   numeric keys differing in exactly one token position). `FLOOR_TOKENS` is **broad, expandable, and
   NEVER used as a filter**. The disagreement between the two detectors is the alarm:
   **`STRUCT_ONLY` = 2,009 of 7,623 (26.4%) right now, and it is FIRING** -- a comparison shape with
   no recognised token means the lexicon has aged. The tool raises this as a defect rather than
   silently under-counting, which is exactly what the old scheme lacked.
2. **DERIVE THE INDEX FROM DISK; NEVER REQUIRE REGISTRATION.** 6,566 results are unindexed because
   registration is a manual step and manual steps get skipped. `tools/result_index_join.py` walks
   `data/` every run. **There is nothing to remember, so there is nothing to forget.** This is
   `CLAUDE.md` evidence-discipline sec 2 ("enumerate from the filesystem, then reconcile to the
   registry, never the reverse") implemented rather than advised.
3. **AN ABSENCE CLAIM REQUIRES AN ENUMERATION, NOT A SEARCH.** "I looked and did not find it" is no
   evidence of absence when the naming convention is unknown -- and this file contains four fresh
   proofs: `exp_leakproof_relational_inference_context_sweep_v1` (C6) does not exist under that
   name but `exp_leakproof_relinfer_context_sweep_v1` does; `sr_routing` and `scale_win` (F4, F5)
   are NOT LOCATED rather than absent; `data/*vamp*` matches only SVAMP math cells (F7). **State
   HOW you enumerated.**
4. **EXISTS / IS-REACHED / IS-GOOD ARE THREE QUESTIONS.** Reachability is measured by RUNTIME import
   closure (sec 4), never by grep -- grep is wrong in both directions in the same file (lazy imports
   inside function bodies are invisible; a module named only in a string constant or a comment reads
   as an import). And a DEFAULT-path trace measures the default path, **not existence**: the
   `encoder_retrain_persist` case is the standing precedent for that error.

**Cadence, deliberately not a cron.** OS scheduled tasks failed silently twice (11 `hd_*` tasks for
~12 days; the KB ingest for 6 days). The enforcement is `tools/session_start_hook.py`, which fires
on every start / clear / **compact** regardless of scheduler state. The `--scan` recompute (~290s)
stays a deliberate act; the hook only reports the persisted result and its age, so **the checker
going quiet is itself visible**.

---

## 9. PRIORITY ORDER -- the rule, then the ranking

### 9a. The rule, stated before it is applied

```
score = C3_WEIGHT x FLOOR_WEIGHT x SURVIVES_WEIGHT x WIRE_COST_WEIGHT
```

| factor | 1.0 | 0.6 | 0.3 |
|---|---|---|---|
| **C3_WEIGHT** -- bears on the gate | moves C3 (read-out quality / within-neighbourhood separation) | bears on C1/C2/C4, or BOUNDS C3 | neither |
| **FLOOR_WEIGHT** -- has a real control | Class A / ARM, read on disk, margin over floor large | floor is PROSE, or margin small, or n small | NO FLOOR / UNPINNED |
| **SURVIVES_WEIGHT** -- survives to HEAD | opened at HEAD today, verdict + run_mode confirmed | opened, but `run_mode` absent / `smoke` / `lite` | not opened |
| **WIRE_COST_WEIGHT** -- module vs build | an `hdlab/` module already exists | EXP-ONLY: experiment code + outputs, a module must be written | NOT LOCATED / must be built from nothing |

**Two overrides, applied after scoring:**
- **A BOUND outranks a lever it invalidates.** A9 and A10 both say the read-out is oracle-bound;
  A11's `S4_cleanup_margin` HARD_FAIL says the same a month earlier. **Three independent results,
  all predating the SNR-wall diagnosis, say C3's 5.2pp gap will not be closed by a better read-out
  RULE.** So anything that only rescores candidates is demoted, and upstream work is promoted.
- **A cheap diagnostic may MEASURE but may never SET DIRECTION** (`CLAUDE.md` non-negotiable 3).
  #1 below is a measurement, ranked first because of what it would settle, not because it is cheap.

### 9b. The top 10

| rank | item | score drivers | what it buys |
|---|---|---|---|
| **1** | **A1 -- re-run the near-duplicate diagnostic over the 5,491 LIVE anchors** (it ran on 241 math atoms) | C3 1.0 x floor 1.0 x survives 1.0 x cost 0.6 | It is the **only** artifact in the corpus that MEASURES C3's exact failure -- right neighbourhood, wrong member -- and it found **22% of a 241-atom codebook with a near-identical neighbour and one pair at cosine 1.0000 between two genuinely distinct concepts**. If that reproduces at 5,491, median rank 84 has a **mechanical** cause that no cleanup rule can fix, and the three oracle-bound results above are explained |
| **2** | **B5-B9 + B11 -- determine the LIVE store's write rule, then the pinv swap** | C3 1.0 x floor 1.0 x survives 1.0 x cost 0.6 | The single most-replicated result in the whole corpus: **4 independent encoder families plus synthetic**, with a non-degenerate anchor (Llama-L15 **122 -> 614**). Three of five say Hebbian sits at **ZERO** capacity on real MiniLM/BGE/E5 keys. **Quote as "Hebb reaches 0 where pinv reaches 0.4-0.55", never as a ratio.** Blocked on one read: what does the live store actually do? |
| **3** | **B1 + B11 -- check what the live read-out pools and whether it whitens** | C3 1.0 x floor 0.6 (ARM) x survives 1.0 x cost 1.0 | `last_token_raw` 0 / `mean_pool_whiten` 40 / `last_token_whiten` **122**. If the live path mean-pools without whitening it is running at 40 where 122 is available -- **no new mechanism required**. `hdlab/whitening.py` EXISTS and is **OFF-PATH** (verified), so the lever is islanded. **Read C14 (`hd_fact_store_semantic_capacity_whitening_v1`) first -- the fact store IS live** |
| **4** | **The five-stage chain, END TO END** (B1 -> B3/B4 -> B2 -> B5-B9 -> A3) | C3 1.0 x floor 1.0 x survives 1.0 x cost 0.6 | Every stage is separately chain-graded, terminal, and on disk. **No cell tests the chain.** It is the clearest un-run experiment in the corpus and it sits **upstream** of the read-out rule -- the only place the SNR wall leaves room |
| **5** | **A2 -- peel/SIC read-out** (`hdlab/peel_sic.py` must be WRITTEN; it does not exist) | C3 1.0 x floor 1.0 x survives 1.0 x cost 0.6 | Flat argmax **0.204 -> 0.940** on REAL codes, 5 seeds, cv 0.034. C3's failure mode is precisely a collapsed argmax over confusable candidates. Demoted below the upstream work by the BOUND override, but it is the strongest read-out-time candidate that exists |
| **6** | **A4 + A5 -- Hopfield-on-correlated-codes and DG separation at write time** (both modules EXIST, both OFF-PATH) | C3 1.0 x floor 1.0 x survives 1.0 x cost 1.0 | **The lowest wire-cost items on the list** -- the code is written. A5 acts at WRITE time (effrank **10.08x** on real Pythia keys), which the BOUND override favours. A4's honest caveat travels: the lift shrinks 6.74x -> **1.63x** exactly as correlation strengthens, i.e. weakest in the regime C3 needs most. **Gate A4 on D3 (spurious-minima 0.957) first** |
| **7** | **H2 -- triage the 127 `proven-bound` reading cells dated >= 07-15** (120 have Class-A floors) | C3 1.0 x floor 1.0 x survives 0.3 (not opened) x cost n/a | **S1's own conclusion: "terminal chain-graded" is the WRONG filter for C3 work** -- only 35 of 574 are dated >= 07-15, while the entire late-July reading/grounding arc is banked as `proven-bound`. This is the largest untouched tier that is topically on-target |
| **8** | **A6 + F2 -- the pooling interface, and the only live dictionary lookup** | C3 1.0 x floor 1.0 x survives 1.0 x cost 0.6/1.0 | A6 is **a positive being carried as a negative**: the distributional-context POOLING INTERFACE separates synonym from sibling at AUC ~0.74 **for free, untrained**, and it is not the interface the read-out uses. The `randinit >= trained` control kills the LEARNING claim, not the INTERFACE claim. F2 (`wordnet_polarity_propagation`, 16,922 B, off-path, unregistered) is a live dictionary path on the same defect |
| **9** | **C1 -- promote the passive-voice competency** | C3 0.6 x floor 1.0 x survives 1.0 x cost 0.6 | **23/24 vs a true 0/24 floor**, held-out, ablated, non-regressing, glass-box, on a NAMED CONSTRUCTION TYPE. The standing anchor *"comprehension is a growing library of construction-competencies"* asks for exactly this artifact and it has existed since 2026-07-24, in no plan and no registry row. Ranked 9th only because it is a PARSER-side win: **file it under reading, not C3** |
| **10** | **G1/G2/G5 -- salvage the 14 resolving supersedes edges, freeze the ledger, read the 06-25 enriched inventory** | C3 0.3 x floor n/a x survives 1.0 x cost 1.0 | Not a capability -- it is what stops rows 1-9 from going dark a third time. The `supersedes` judgements exist **nowhere else**; 52 of 66 edges dangle, so merging as-is would import the breakage. And `data/_archaeology_inventory_enriched.jsonl` (**2.4 MB, 3,269 experiments already joined to the cert ledger**) is a ready-made answer to much of H1/H4, seven weeks stale but structurally intact, **and was never opened** |

**Deliberately NOT in the top 10, and why** (so the omissions are decisions, not oversights):
D13a/D13b (MAVEN-ERE) and D12a-c (CLIP-era vision) are **EXPERIMENT-ONLY** -- "wire it" is really
"build it" -- and neither serves C3; F5 (`scale_win`) is likewise BUILD and its source is
NOT LOCATED; D5/D6/D3/D4 are **SMOKE-ONLY** and must be promoted to FULL before they mean anything;
A11/A12 raise precision at partial coverage, not hit@1 at full coverage, which is the gate;
D22 (entmax) explicitly reports **delta +0.000 on quality**; E5-E12 are refutations -- their value
is that they **stop** work, and it is already banked by being written here.

---

## 10. COMPACTION SURVIVAL

**Requirement:** a session that has lost all context must find this file and continue correctly
without asking anyone.

### 10a. The mechanism that already works

`tools/session_start_hook.py` runs on every session **start / clear / compact** (wired in
`D:/AI/.claude/settings.json`) and injects `notes/STATUS.md`'s `AS OF:` line and its
`## WHAT IS RUNNING` section, plus the `result-index-join` probe. **The probe is the durable
pointer**: it fires at every compaction and prints the orphan count and the drift alarm, which is
this program's disk-derived metric (sec 7b). No new hook wiring is needed.

### 10b. The STATUS.md stub -- TEXT TO APPLY, NOT APPLIED HERE

**I did not edit `notes/STATUS.md`.** A concurrent agent may be writing it, and `STATUS_SPEC.md`
sec 6 forbids the incidental byte-shave: an agent that came to ADD something is the worst-placed
actor to decide what leaves. **This needs applying by whoever owns the next STATUS.md maintenance
pass.**

Add to the **`## OTHER PATH STATE`** section (it is state, not a lesson, so it belongs in the
capped file's re-derivable half, and it costs 232 bytes):

```
RECOVERY: 95 recovered systems ledgered in notes/RECOVERY_PROGRAM.md (LIVING) -- 5 FOUND /
76 VERIFIED / 1 WIRED / 2 SHELVED / 11 REFUTED at open; 10 tiers NOT-YET-TRIAGED incl 544
chain-graded + 127 proven-bound reading cells. Count: grep -oE 'STATE:[A-Z]+' that file.
```

**Constraints on whoever applies it, all binding:**
- **Do NOT reword `AS OF:` or `## WHAT IS RUNNING`** -- both are parsed by
  `tools/session_start_hook.py` (lines 119 and 124). Rewording them silently degraded every
  compaction recovery once already.
- The cap is **8192 bytes** (`STATUS_SPEC.md` sec 7), and the file measured **8,188 B** on
  2026-08-14 -- **4 bytes of headroom**. This stub does not fit without a trim, and per
  `STATUS_SPEC.md` sec 6 the adder may evict **only from tiers 1-4** (recomputable numbers,
  recoverable paths, finished-work status, emphasis prose) and **must STOP rather than descend into
  sections 5-6**. If tiers 1-4 do not free 232 bytes, hand the trim to a maintenance pass -- do not
  shrink the stub by dropping the count, because the count is the whole point.
- If bytes truly cannot be found, the **minimum viable stub is one line**:
  `RECOVERY LEDGER: notes/RECOVERY_PROGRAM.md (LIVING, 95 systems, states countable in-file).`

### 10c. If this file is the only thing a cold session has

It is self-sufficient by construction: sec 1 says what happened in plain language, sec 3 defines
the states and their transitions, sec 4 records the runtime measurement and the exact command that
reproduces it, sec 5 carries every evidence path, sec 6 states every unexamined tier **with its
size**, sec 7 gives the two progress commands, sec 9 gives the rule and the ranking. **No claim
here depends on a number held only in a session's memory.**

### 10d. Update protocol -- so this file does not rot the way its six predecessors did

The measured failure mode (S3) is that **each review started over rather than extending the last**,
because every rename changed the unit of account (`cycle number -> PP capability -> hdlab module ->
WIRE/SHELVE gate -> brain component -> brain organ`). Anything that did not map onto the new unit
silently vanished.

1. **Unit of account is frozen: one row = one RECOVERED SYSTEM.** Not a cell, not a module, not an
   organ. A system may be an experiment, a module, a data asset, or an index -- and each row says
   which it is in the `module` column. **Do not re-key this ledger.**
2. **Edit rows IN PLACE.** Change the STATE word and append the evidence. Never delete a row: a
   REFUTED row is the cheapest thing in this file and the most expensive to re-learn.
3. **Never let a tier in sec 6 look examined.** Move counts between "triaged" and
   "NOT-YET-TRIAGED"; never delete the row when it hits zero -- record the zero.
4. **A corrected claim gets struck in place, not quietly fixed.** Four corrections are already
   embedded (C9 `grid` not full; C10 `lite` not full; C16 is a `HARD_FAIL`; E3 is a PASS not a
   refutation) plus one name correction (C6) and one registry correction (F9, 8 of 24 now
   registered). That visible-correction habit is the difference between a ledger and a brochure.
5. **When you supersede this document, the successor must carry every row forward or say why not.**
   That sentence is the entire lesson of the six-rename lineage.
