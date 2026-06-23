# exp_dev hand-off — research: 2x revival overnight negatives cluster

**Filed-by.** research (Opus 4.7) 2026-06-23  
**Trigger.** 2x revival research drill on 5 overnight HARD_FAIL anchors completed. 3 of 5 have actionable substrate-native revival angles ready for empirical test.  
**Pause state.** Honors `data/orchestrator_paused.flag`. If paused, file only; do not ship.  
**Cite.** `notes/research_2x_revival_overnight_negatives_2026-06-23.md` (parent research note; pre-reg bands + HARD_PASS/HARD_FAIL thresholds verbatim).  
**Discipline.** Per [[feedback-no-experiment-design-in-prompts]] — this handoff names anchor candidates + pointers, not implementations.

---

## Anchor candidates (rank-ordered, highest-leverage first)

### Anchor 1: `substrate_self_map_v2d_discriminator_corrected_v1`

**Anchor pointer.** `notes/research_2x_revival_overnight_negatives_2026-06-23.md` section "Revival 1"; parent data `data/exp_substrate_self_map_v2c/metrics.json` (3 seeds, cluster_gap = -3 across all).  
**Substrate-product reading.** Genuine substrate-native self-mapping (Phase 1 of USER self-improvement program). v2c finding was likely a discriminator-direction bug (real relations BUNDLE chain-grade anchors into LARGER coherent clusters; shuffle FRAGMENTS them — cluster-COUNT inverted, but Jaccard-vs-v1-families and new-cross-family-arrows both favor real). Re-running v2c primitives with ARI(real, v1_families) vs ARI(shuffle, v1_families) — or modularity Q, mean cluster size — could flip 3 consecutive verdicts simultaneously.  
**Tier hint.** Discriminator-fix re-test of an existing FULL run; reuses v2c primitives (char_trigram + KGStore multivalue Hebbian + 2hop Jaccard cluster). Mechanically straightforward; substantial verdict-flip upside.  
**Why-now.** v2/v2b MIDDLE_BAND + v2c HARD_FAIL is a 3-fail cascade; per Fix #28, we have hard evidence the verdict_msg framing on a wrong-direction discriminator masked the actual signal. ARI/modularity are standard community-detection null-comparison statistics; substituting them is a 1-function-swap. P_revival capped at 0.50 per novel-synthesis discipline.  
**HARD_PASS thresholds (verbatim from parent §"Falsifiable predictions"):** ARI_real >= 0.10 AND ARI_real / ARI_shuffle >= 2.0; OR mean_cluster_size_real / mean_cluster_size_shuffle >= 1.5.  
**HARD_FAIL thresholds:** ARI_real <= 0.02 OR ratio <= 1.1.  
**Cost.** ~2hr remote_cpu (re-uses v2c ingest + clustering); ~3 seeds.

### Anchor 2: `att1_iterative_attractor_v2_low_storage_ratio_krotov_v1`

**Anchor pointer.** `notes/research_2x_revival_overnight_negatives_2026-06-23.md` section "Revival 2"; parent data `data/exp_att1_iterative_attractor_cleanup_v1_smoke/metrics.json` (4 arms all plateau recall_harder=0.04 at sigma=1.5; ARGMAX_BASELINE basin already gone at sigma=1.0).  
**Substrate-product reading.** Substrate is over-capacity at M/N=200/512=0.39 — past linear-Hopfield envelope (alpha_c~0.138). Cell tested ONLY Ramsauer-softmax variants (T=2,4,16); NEVER tested Krotov dense-polynomial f(x)=x^n or f(x)=exp(x), which give exponential capacity AND larger basin radius at finite T. If the iter-attractor primitive can lift at M/N=0.10 with Krotov interaction, it becomes substrate-mine usable across n4/n9/n10/p1 argmax-cleanup failures (all of which currently cap at one-shot argmax).  
**Tier hint.** Smoke at N_DIM=512, M=50 (M/N=0.10), 3 arms: ARGMAX_BASELINE / ITER_KROTOV_POLY (f=x^4) / ITER_KROTOV_EXP (f=exp). Sigmas {0.5, 1.0, 1.5}. ~30min CPU.  
**Why-now.** att1 was filed as HARD_FAIL with verdict_msg "mechanism rejected as substrate-mine swap-in" — but the cell tested half of the lit-anchor's recommendation (Ramsauer only, not Krotov). Per Fix #29 and USER "empowered to experiment where lit dismissed", revival is exactly the substrate-native variant that pushes past the over-capacity regime. P_revival=0.35 (deflated 0.20 for substrate-binary vs Krotov-real-valued unknown).  
**HARD_PASS thresholds (verbatim):** best_iter_arm recall_harder >= 0.10 AND best_iter_arm lift_over_argmax >= 0.05 absolute at sigma=1.5.  
**HARD_FAIL thresholds:** best_iter_arm recall_harder < argmax_recall_harder + 0.01 at sigma=1.5.  
**Cost.** ~30min CPU smoke; ~3hr CPU at N_DIM=4096 full if smoke PASSes.

### Anchor 3: `text8_substrate_pseudoLM_v2_temperature_calibrated_v1`

**Anchor pointer.** `notes/research_2x_revival_overnight_negatives_2026-06-23.md` section "Revival 3"; parent data `data/exp_text8_substrate_pseudoLM_gpu_v1_smoke_remote/metrics.json` (substrate BPC 9.371 vs unigram 8.024 BUT substrate acc 0.198 ~ bigram acc 0.213).  
**Substrate-product reading.** Substrate's top-1 accuracy is competitive (better than unigram, near bigram) but BPC is bad because Hebbian outer-product produces single-spike distributions with low mass on correct token when top-1 wrong. **Calibration problem, not mechanism failure.** Lit (Stolcke 1998 log-linear interp; Guo 2017 temperature scaling) gives standard fixes. text8 revival unlocks Path A pseudo-LM viability at GPU scale — core to bigram-gap closure and L2 glass-box-LLM vision.  
**Tier hint.** Smoke at N_DIM=4096, N_TRAIN=100k, V=4000, 3 arms: SUBSTRATE_HEBBIAN_BPC_RAW (control) / SUBSTRATE_HEBBIAN_TEMP_CALIBRATED (sweep T in {0.5, 1.0, 2.0, 5.0} on dev split) / SUBSTRATE_LOG_LINEAR_UNIGRAM (lambda * log P_sub + (1-lambda) * log P_uni; sweep lambda in {0.1, 0.3, 0.5, 0.7}). ~1hr GPU.  
**Why-now.** Backoff arm in v1 used HARD threshold (substrate prob < 0.05); backoff is the wrong composition — log-linear interp is the standard. Cell never tried temperature-calibration at all. P_revival=0.30 (deflated 0.25 — BPC gap of 1.35 bits is LARGE; calibration usually closes 0.2-0.5 bits, not 1.35).  
**HARD_PASS thresholds (verbatim):** best calibrated arm BPC <= 7.5 AND cv across seeds <= 0.10.  
**HARD_FAIL thresholds:** best calibrated arm BPC >= 8.024 (no calibration arm beats unigram).  
**Cost.** ~1hr GPU smoke; ~6hr GPU full at N_TRAIN=1M.

---

## Parked anchors (do NOT dispatch)

### `cross_corpus_compose_chat_v1_n4096`
**Park reason.** Power-bound (n=17 total; per-corpus n=5-6 too small for lift detection). Two HARD_FAIL arms (hotpotqa, fb15k) have ZERO single-arm signal to compose from — composition is a mechanism multiplier, not a generator.  
**Revival gates.** (i) hotpotqa or fb15k achieves >=0.10 single-arm acc AND (ii) n>=200. Until then, the cell is not measuring what its name suggests.

### `b2_substrate_only_tinystories_lm_v1`
**Park reason.** Subsumed by text8 revival. Same calibration root cause; text8 has 8x more training data (better test of the same mechanism). If text8 revival fails, b2 will also fail; if text8 PASSes, re-test b2 at scaled N_TRAIN=50k to confirm small-corpus regime.

---

## Context pointers (NOT summaries)

- Parent research note (full diagnosis + thresholds + calibration penalty): `d:/AI/hd-instrument/notes/research_2x_revival_overnight_negatives_2026-06-23.md`
- Per-anchor failure metrics:
  - `d:/AI/hd-instrument/data/exp_substrate_self_map_v2c/metrics.json`
  - `d:/AI/hd-instrument/data/exp_att1_iterative_attractor_cleanup_v1_smoke/metrics.json`
  - `d:/AI/hd-instrument/data/exp_text8_substrate_pseudoLM_gpu_v1_smoke_remote/metrics.json`
  - `d:/AI/hd-instrument/data/exp_cross_corpus_compose_chat_v1_n4096_smoke/metrics.json`
  - `d:/AI/hd-instrument/data/exp_b2_substrate_only_tinystories_lm_v1_smoke/metrics.json`
- Existing att1 pre-reg (for delta): `d:/AI/hd-instrument/notes/exp_dev_att1_iterative_attractor_pre_reg_2026-06-22.md`
- Existing self_map v2 lineage: prior research_brain_mechanism_x_HD_broad_exploration_drill_2026-06-22
- Existing primitive: `hdlab/iterative_attractor.py` (att1 v1 primitive; revival needs Krotov dense interaction variant)
- Field advisor: `tools/orchestrator/research_field_advisor.py` (semiconductor + free-probability remain top scope-expansion candidates; revival is orthogonal to field-expansion this cycle)

---

## Contract

Per [[feedback-no-experiment-design-in-prompts]] this handoff names anchors + thresholds; exp_dev owns:
- Implementation details (Krotov f(x) choice; temperature sweep grid; ARI library choice — sklearn `adjusted_rand_score` or manual)
- Queue routing (Anchor 1: remote_cpu; Anchor 2: local_cpu_queue smoke then remote_cpu full; Anchor 3: remote_gpu via hdi_orchestrator per Fix #24 GPU dispatch discipline)
- Smoke gate before full
- Post-ship REMOTE VERIFY per role contract
- ship_name uniqueness check pre-ship per [[feedback-ship-name-collision]]
- Per-cell SCHEMA-VET + checkpoint discipline per [[feedback-long-cells-must-checkpoint-resume]] (Anchor 1 multi-seed long-running)
- Honest verdict_msg per [[feedback-verdict-msg-honest-reread]] — verdict_handler will compare claimed labels vs per-cell numbers
- Pre-flight `tools/predispatch_check.py <anchor>` per Fix #26

## Autonomy declaration

exp_dev's call on:
- Whether to bundle Anchors 1+2 in one dispatch (both CPU; both ~hours; both have well-defined smoke gates) or stagger
- Anchor 3 GPU sequencing — must route via hdi_orchestrator per Fix #24 (GPU dispatch must actually use GPU; numpy cells run on GPU machine CPU at 1% util)
- Exact ARI implementation for Anchor 1 (sklearn vs manual; v1 Director families location — check `data/director_v1_families.json` or equivalent)
- Whether to add ITER_KROTOV_QUADRATIC (f=x^2) as 4th arm in Anchor 2 (lit "Hopfield-Fenchel-Young Networks" arxiv:2411.08590 covers the unified family — could span the interaction spectrum)
- Whether Anchor 3 smoke should run on remote_cpu first per [[feedback-cell-author-smoke-and-dispatch-route-via-orchestrator-for-heavy-cells]] (matmul-bound at N=4096; laptop is slowest)

Hard rules (from role contract):
- ASCII-only in print()/verdict_msg per [[feedback-ascii-only-in-scripts]]
- run_mode='full' required for cert-grade; smoke first per [[feedback-smoke-gate-before-full]]
- HDLAB_EXP_NAME + REQUIRED_FIELDS per remote dispatch checklist
- Commit pre-reg notes to origin/main BEFORE remote dispatch per [[feedback-commit-prereg-notes-before-remote-dispatch]]
- Self-test per [[feedback-strategy-spec-formula-selftests]]:
  - Anchor 1: synthetic 2-block partition; ARI should be 1.0 vs identical partition, ~0 vs random partition; small n (10-20 nodes); helper returns within 1% of expected
  - Anchor 2: at zero noise (sigma=0) all arms should give recall=1.0 (perfect retrieval); at infinite noise (sigma=100) all arms should give recall ~= 1/V (random); helper verifies endpoints
  - Anchor 3: at lambda=1.0 SUBSTRATE_LOG_LINEAR_UNIGRAM should reproduce SUBSTRATE_HEBBIAN_BPC_RAW; at lambda=0.0 should reproduce UNIGRAM_BASELINE; helper verifies endpoints

## Status_log discipline

exp_dev to log events per anchor:
- `event_kind = "experiment_ship"`, `importance = HIGH` on queue_add (these revivals could flip 3 HARD_FAIL verdicts)
- `event_kind = "experiment_verdict"`, `importance = HIGH` on verdict
- `plain_language` field MANDATORY per [[feedback-for-you-tab-primary-channel]]
