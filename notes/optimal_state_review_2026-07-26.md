# Optimal-State + Discoverability Review — 2026-07-26

Read-only audit (redo of dead agent a9e43fd9). AUDIT ONLY — nothing built/dispatched/modified in the canonical store. Auditor: hdi_testbed.

Bottom line: state is largely OPTIMAL — every load-bearing DONE component is present + git-committed, and the store reconciles cleanly to ledger tail 29584. Two real gaps: (1) `notes/` has ballooned to **26,186 `.md` files** so directory-search discovery (grep/glob) times out — discovery now depends ENTIRELY on the 3-tier doc chain + KB; (2) one live tangent doc lacks a superseded banner. Details below.

---

## 1. DISCOVERABILITY — all DONE components PRESENT + git-tracked; discoverable via the doc chain

| Component | Path | Present |
|---|---|---|
| Concept encoder | `hdlab/concept_encoder.py` (54KB, Jul 2) | YES |
| Reasoner (verification-by-derivation) | `hdlab/reasoner.py` (50KB, Jul 25) | YES |
| Binding | `hdlab/binding.py` (4KB, Jul 8) | YES |
| Stage-1 SEMANTIC concept-learner battery v1/v2/v3 | `experiments/exp_substrate_stage1_SEMANTIC_concept_learner_battery_v1.py`, `_v2_FULL.py`, `_v3_CV_TIGHTENING.py` | YES (all 3) |
| Spoke1 competitive-Hebbian | `experiments/exp_substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only_2026-07-02.py` | YES |
| Spoke2 temporal-contiguity Foldiak | `experiments/exp_substrate_concept_encoder_spoke2_temporal_contiguity_foldiak_trace_v1.py` | YES |
| Spoke3 sparse DG-CA3 (Marr/CLS) | `experiments/exp_substrate_concept_encoder_spoke3_dg_ca3_marr_cls_replay_v1.py` | YES |
| Predictive-coding competitive-allocation | `experiments/exp_substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v1.py` + `_v2.py` | YES |
| Sharded CG store | `data/substrate_index/{math,concept,meta,...}/` | YES + committed |
| encoder_rescue diagnosis | `notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md` (4790B) | YES |

- **Findable:** all are named + linked from the authoritative doc chain (`SUBSTRATE_CHARTER_read_first.md` -> `THE_PLAN_learned_grounded_representation_foundation_2026-07-26.md` -> `WHERE_WE_ARE_NOW_2026-07-26.md`). That chain is internally consistent and correctly names concept_encoder.py, reasoner.py, the spokes, stage-1 battery, sharded CG store, and the encoder-migration HARD_FAIL. Discovery via the doc chain is CONFIRMED. None of the DONE components is orphaned.
- **BURIED-RISK (systemic, not per-component):** `notes/` = **26,186 top-level `.md` files**; `grep`/`glob`/`ls` over it TIME OUT. Directory-search discovery is effectively dead. Consequence: the ONLY viable discovery paths are (a) the 3-tier doc chain and (b) the substrate KB (`director_kb_query.py`). Anything not linked from those two is de-facto orphaned regardless of being on disk. The DONE components are safe (they're linked); the hazard is for everything else and for future work. Recommend the Director spot-verify KB-findability of the 10 components above via `director_kb_query.py` and treat the doc chain as the load-bearing index going forward.

## 2. STORE INTEGRITY — CLEAN. 29560-29584 fully reconcile; committed local-only

- Cert ledger = `data/substrate_index/meta/cert_ledger.jsonl`; **tail = 29584** (confirmed; expected).
- Reconciled **by atom_id** (not seq-grep) for all 25 seqs 29560-29584: every ledger atom_id is FOUND in `data/substrate_index/math/atoms.jsonl` at the matching seq. **Zero missing.** (29580-29584 = the inference-arc HONEST_NEG/MM banks; corpus=math.)
- **Committed:** working tree is CLEAN for `data/substrate_index/` — last store commit `dea577fbf` "cert(skunkworks): bank seq 29584". HEAD `1c8baa465`. Only uncommitted files in the repo are `.claude/agents/exp_dev.md` + `PROGRESS.md` (not store).
- **Local-only, by design:** every 29560-84 atom carries `local_write_only_no_origin_push_no_remote_persist:true`; **NOT pushed to origin** (correct — needs in-session USER auth). Not "at risk" beyond the standing single-machine exposure. One pending-sync flag: seq **29584 has `needs_orchestrator_store_sync:true`** — orchestrator store-sync is outstanding (a flag, not a corruption). No push performed here.

## 3. DOC CONFLICTS — one live tangent doc needs a banner; the rest already reconciled

- `research_learned_inference_generalization_analogy_metalearning_2026-07-26.md` — **CONFLICT (needs banner).** Leads with structure-mapping analogy / inference-over-supplied-KBs as "the honest next lever after architecture is exhausted." That is exactly the 2026-07-26 inference arc THE_PLAN §Conflicts demotes to a TANGENT. No superseded/tangent banner. **Fix:** add a top line — "TANGENT per THE_PLAN Conflicts §2: analogy/supplied-KB inference is NOT the frontier; the learned-grounded-representation foundation is. Kept for the brain-drill of both mechanisms." (Do NOT delete — the brain-drill is reusable.)
- `foundation_build_plan_2026-07-14.md` — **already reconciled, no action.** Has a superseded banner pointing to THE_PLAN and explicitly scopes "LLM-generate relations" to layer-2 KNOWLEDGE (not the layer-1 meaning encoder).
- `encoder_rescue_plan_converged_diagnosis_2026-07-04.md` — **not a conflict.** THE_PLAN cites it as the still-valid source of the R1-R5 sequence. Keep as-is.
- **Cannot exhaustively scan** the 26k-file `notes/` for other stale "supply the meaning encoder" docs (grep times out). The governing doc chain is clean; recommend any other doc that leads with supplied-symbol inference or "supply the encoder" get the same one-line tangent banner as found.

## 4. PRIOR ENCODER-WORK INVENTORY (encoder_migration / encoder_rescue / concept_encoder / differentiation) — do NOT reinvent

R1 (global/landmark RKD objective-fix) lineage, MOST RECENT / MOST COMPLETE first:

| Cell (data/…/metrics.json) | Verdict | Load-bearing metric |
|---|---|---|
| `exp_encoder_migration_step1b_v4_joint_reverify_relock_v1_seed7` (+seed13) | **HARD_PASS** ← most complete | "ALREADY_JOINT_SOLVED_VIA_INBATCH": inbatch-RKD-only landed ckpt jointly clears dense=0.8969 (>=0.82), keyed@J5=1.000 (>=0.9), shuffled@J5=0.000 (no leak). Mid-scale n_held=17790. |
| `exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_7` (+13/23/29/31) | HARD_FAIL | FALSE_WIN_ALGEBRA_GLOBAL: dense recovered (global 0.853 / inbatch 0.877) BUT keyed_roundtrip J5=0.133<0.90 — code not a valid composable SBC. |
| `exp_encoder_migration_step1b_v3b_nce_ablation_dense_recovery_diagnostic_v1` | HARD_FAIL | Global-vs-inbatch advantage did NOT confirm at mid scale; KEY diagnostic = dropping the NCE term (NCE_ZERO) recovers dense **0.7336 vs 0.2687** with it (TAIL_CORRUPTION_CONFIRMED). NCE contrastive term corrupts geometry. |
| `exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1` (the actual full-scale R1) | **CELL_CRASHED (OOM)** | tried to alloc 6.55GB; the global/landmark-RKD objective at full scale NEVER ran to completion. |
| `exp_encoder_migration_step1_train_concept_encoder_970K_KB_v1` | CELL_CRASHED | selftest: mean_nnz 616.91 outside [18,22] (sparsity target broken). |
| `exp_encoder_migration_step1b_{distill, v2_mlp_distill}` | (earlier distill attempts) | superseded by v3/v4 line. |
| `exp_encoder_migration_step2_sparse_encode_970K_KB_v1`, `step3_gold_verify_100_queries_A_B_v1` | smoke/downstream | not reached at scale. |

Adjacent lines already on disk (do not rebuild):
- `exp_composed_differentiation_loop_v1` (MEMORIZES / KEEP_EPISODIC) + `_v2` (held-out ~0.24); `exp_learned_meaning_frontend_differentiation_v1` (29556, ho_lift 0, flat-MLP over borrowed GloVe); `exp_selfplay_differentiation_failmask_decorrelation_v1`.
- **R3 teacher-free seed already exists:** `exp_teacher_free_relational_encoder_cn_subgraph_v1` (+ _selftest/_smoke) — the internal-self-teacher direction has a prior cell to build on.
- **Grounded (R4/ground) seeds:** `exp_native_meaning_encoder_binder_grounded_v1`, `_wordnet_mechanism_v1`, `_scale_v1`.
- Large encoder-family capacity/geometry sweep already banked: gsbc gradedcode, v3e/v4–v12, anchor4 phase-diagram, structure_aware_sharpness, objective_swap_kl_rank — reference before any new sparsity/objective sweep.

**Guidance for the R1 rebuild:** the pieces prove dense~0.90 + valid keyed code + no-leak IS reachable at MID scale via inbatch-RKD (v4 HARD_PASS). The genuinely UNSOLVED gaps are only: (a) the global/landmark objective at FULL 178k scale — it has ONLY ever OOM-crashed (v3), never run, so a memory/chunking fix precedes any verdict; (b) teacher-free — every win to date used the BGE teacher (violates the no-borrowed-vector lock), so R3 must wean onto the self-teacher (start from `teacher_free_relational_encoder_cn_subgraph_v1`). Start the objective RKD-only: the NCE term is a KNOWN geometry-corruptor (v3b, +0.46 dense when removed).

---

### Recommended fixes (for Director; none applied here)
1. Add the tangent banner to `research_learned_inference_generalization_analogy_metalearning_2026-07-26.md` (§3).
2. Orchestrator: clear `needs_orchestrator_store_sync` on seq 29584 (§2).
3. Treat the 3-tier doc chain + KB as the sole discovery index; `notes/` (26k files) is no longer directory-searchable — consider archiving/sharding stale notes (§1).
