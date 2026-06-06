# Research -> Testbed: CELL-2 AUTHORIZED -- Wikipedia extraction at 1B BASE L=15 ($30)

**From:** Research session
**To:** Testbed
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-07 ~01:00
**Re:** testbed_to_research_70B_Instruct_ARCHITECTURE_ROBUST_plus_unexpected_finding_2026-06-06.md (cloud queue empty) + testbed_to_research_FAISS_env_fix_DONE_HNSW_cell_unblocked_2026-06-06.md (FAISS env unblock)
**Subject:** User authorized CELL-2 at $30. Wikipedia extraction at Llama-3.2-1B BASE L=15. Production substrate foundation; enables downstream CELL-3 + CELL-4 chain.

---

## User authorized CELL-2 at $30

Specs locked per today's findings:

### Architecture (per CELL-1 + 70B-Instruct locks)

- **Model:** Llama-3.2-1B **BASE** (NOT Instruct; locked per 70B-Instruct cycle "Instruct destroys mid-depth peak by 66%")
- **Layer:** **L=15** (92% depth; locked per CELL-1 cheap-fleet ranking; best causal-LM at top-5-RP = 0.282)
- **Pool method:** last-token (causal LM; per `feedback_causal_lm_last_token_pool` memory)
- **Quantization:** fp16 preferred when feasible (NF4 if needed; NF4 costs 30-40% retrieval at sweet-spot)
- **Task:** Wikipedia subset extraction (10K-100K passages range; your discretion on scale)

### Pre-reg (your call to set formally per envelope-fail-band protocol)

Suggested directional bands (refine per your judgment):
- **HP:** extraction yields stable per-passage embeddings with d_eff at MiniLM-class level (~80-100 measured per cycle 131 framework) at scale; substrate writes succeed at production-target M
- **MID:** extraction succeeds but d_eff drops below MiniLM baseline; substrate writes succeed at smaller M
- **HF:** infrastructure failure (OOM at scale; pipeline crash; or substrate writes fail systematically)

### Strategic value

CELL-2 is the production substrate foundation. Enables downstream:
- **CELL-3:** distilled 22M student from 1B at L=15 ($15; gated on CELL-2 features available)
- **CELL-4:** HP-12 V2 at 100K facts ($10-20; gated on CELL-2 + FAISS env fix already done + HNSW parameter tuning Exp-Dev's lane)

Total downstream chain if CELL-3/4 also authorized: ~$55-65 (well under Drill Y's $100-200 envelope).

### Per FAISS env fix unblock

For CELL-4 specifically, recommend the "cheap-fleet for infrastructure debug" pattern:
- After CELL-2 extracts features, Exp-Dev iterates HNSW parameter sweep LOCALLY at M=100k for $0 (in /root/faiss-env)
- Only commit to CELL-4 cloud spend after HNSW knobs (ef_search >= d=256; sweep ef_search, HNSW_M) found
- Saves potentially $10-20 of failed-config cloud runs

### Dispatch flexibility

- Run independently of CELL-5 (CELL-5 still pending user Together API key)
- Wikipedia subset choice yours (10K simplest; 100K production-scale; your judgment)
- fp16 vs NF4 your judgment per H100 availability + cost budget
- 1xH100 likely sufficient (1B is small; you've proven GH200 + 8xH100 + 2xH100 paths today)
- Report metrics.json + per-passage features in storage layout suitable for downstream cells

### Cost discipline note

Today's cloud spend so far: $3.97 (CELL-1 + 70B-Instruct + CLOUD-1 + 1b + zombies). CELL-2 at $30 is ~7x today's cumulative, but still well under Drill Y's $100-200 envelope. Hardening + dual-SKU polling + smart launcher all proven today; lower spend risk than morning cells.

## Updated standing items (cloud)

Authorized + ready to dispatch:
- **CELL-2** ($30; just authorized)

Pending user (cloud):
- CELL-5 cascade distillation FD smoke ($28; awaits Together API key + auth)
- CELL-3 distilled 22M student ($15; gated on CELL-2 features ready)
- CELL-4 HP-12 V2 at 100K facts ($10-20; gated on CELL-2 features + HNSW parameter tuning)

Standing items (informational):
- HP-12 V1 5-min screen recording (user manual task)

## Cross-references

- Cheap-fleet ranking final (cycle 70B-Instruct): MiniLM 0.890 > 1B base L=15 (0.282) > all causal-LM variants
- CELL-1 layer convention finalized: 1B BASE L=15
- 70B-Instruct lock: USE BASE NOT INSTRUCT
- FAISS env fix landed: /root/faiss-env at $0 (gates removed for CELL-4 downstream)
- Smart launcher hardening: dual-SKU + zombie defenses + 25 known bug catalog

---

**END.**

**Testbed:** CELL-2 authorized at $30. Llama-3.2-1B BASE at L=15 (no Instruct). Wikipedia extraction. Dispatch when convenient. fp16 preferred when H100:1 available. Storage layout suitable for downstream CELL-3 + CELL-4. Standing for completion + features available.

**Exp-Dev:** CELL-2 features will be available after dispatch. HNSW parameter sweep on /root/faiss-env can now iterate locally at $0 before CELL-4 cloud commit.

**User:** CELL-2 authorized + routed to Testbed at $30. Enables downstream CELL-3 + CELL-4 (~$25-35 additional if all authorized later). Total chain ~$55-65 well under envelope. CELL-5 still awaits your Together API key separately. Total today's cloud commitment: $33.97 cumulative if CELL-2 lands as estimated.
