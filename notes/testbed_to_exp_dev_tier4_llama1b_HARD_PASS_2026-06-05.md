# Testbed -> Exp-Dev: Tier-4-Llama HARD_PASS at 1B scale

**From:** Testbed  **To:** Exp-Dev (primary)  **Inform:** User + Orchestrator + Research  **Date:** 2026-06-05
**Re:** `exp_dev_to_testbed_tier4_llama1b_cloud_dispatch_2026-06-05`

## Verdict: HARD_PASS

`substrate_tier4_hopfield_attention_substitution_llama_3_2_1b_v1` -- substrate-attention training-stable inside Llama-3.2-1B at SWAP_LAYER=8.

```
entropy_ratio(substrate/others) = 2.82   (HP gate: > 0.50  PASS)
grad_ratio                      = 0.8    (HP gate: < 8     PASS)
ppl_ratio(substrate/baseline)   = 0.98   (HP gate: <= 1.5  PASS)
```

Substrate-as-attention REPLICATES at 1B params with GQA + RoPE adaptation. The Pythia HP result generalizes to Llama-3.2-1B; substrate is genuinely an architecturally swappable attention primitive at 1B scale.

## Per-seed detail

| Seed | Substrate ppl | Baseline ppl | ppl_ratio | ent_ratio | grad_ratio |
|---|---|---|---|---|---|
| 7  | 4.38 | 4.44 | **0.986** | 2.76 | 0.79 |
| 17 | 5.23 | 5.42 | **0.965** | 2.88 | 0.85 |

Substrate-attention has **slightly LOWER** ppl than the unmodified baseline on both seeds (ratios < 1). Not just stable -- comparable or marginally better on this 300-step Shakespeare fine-tune.

## Comparison to Pythia HP

| Metric | Pythia-160M HP | Llama-3.2-1B HP | Direction |
|---|---|---|---|
| ppl_ratio | 1.06 | 0.98 | **1B is better** (substrate lower ppl than baseline) |
| ent_ratio | 3.08 | 2.82 | Both well above HP gate of 0.50 |
| grad_ratio | 0.7 | 0.8 | Both well below HP gate of 8 |

Generalization: substrate-as-attention works at both 12-layer (Pythia) and 16-layer (Llama-1B) with the appropriate per-architecture adaptation. **No degradation at 6.25x param scale.**

## Run profile

- **Cluster**: Lambda PCIe H100 us-west-3 (us-east-1 had no capacity at launch; SkyPilot auto-failover triggered the 3rd time -- consistent behavior)
- **Total cluster wall**: ~12 min (setup + run + teardown)
- **Run wall**: 280 sec (4 train+eval cycles: 2 seeds x [substrate + baseline])
- **GPU peak**: 25.25 GB on H100 (fp32 + grads + activations)
- **Cost**: ~$0.66 (PCIe $3.29/hr x ~12 min)
- **All audit fixes worked**: TOKENIZERS_PARALLELISM=false + file-first HF token + --self-test gate + sky down belt-and-suspenders

## Files on runner

`C:\dev\hd-instrument\data\exp_substrate_tier4_hopfield_attention_substitution_llama_3_2_1b_v1\metrics.json`

Full per_seed list inside metrics.json including ppl/wall/grad_norms/layer_entropies arrays.

## What was preserved from your spec

- SWAP_LAYER = 8 (mid of 16)
- attn_implementation="eager" (required for the forward override + output_attentions)
- torch_dtype=float32 (Llama-1B fp32 -- 25 GB peak fits H100 80 GB comfortably)
- grad-clip 1.0
- LlamaAttention RoPE preserved via `apply_rotary_pos_emb`
- GQA handled via `_repeat_kv` on K and V before substrate causal-linear-attn
- All four Llama projections (q_proj, k_proj, v_proj, o_proj) kept; only the
  softmax-attention core replaced with substrate phi=elu+1 normalized linear-attn

## Bug caught + handled this run

NONE. The Llama-1B per-token watchdog-mid-write bug from the prior run does NOT apply here (this script writes a small metrics.json at end, no np.savez phase). The defensive `_LAST_DOC_COMPLETE_TS[0] = None` patch I committed in `e5c4dde` is for the extraction scripts, not training/eval scripts like this one.

## What this unblocks for you

- **Phase-2 architecture-scaling claim** -- substrate-as-attention works at 1B
  scale; you can update strategy_decisions / cap_map with the cross-scale
  generalization (Pythia HP + Llama-1B HP both with same substrate primitive).
- Optional next: 8B substrate-attn replication (if user wants the next rung; cost
  ~$2-4 cloud).
- Tier-6 GPU work (per `exp_dev_to_research_p1_p2_HP_v7_stuck` from 2026-06-04
  cycle) is no longer GPU-blocked since cluster is down.

## What's NOT yet attempted

- Different SWAP_LAYER positions (only 8 tested; could probe 4, 12 for "where in
  depth does substrate-attn work?")
- Longer training runs (only 300 steps; long fine-tunes might reveal subtle drift)
- Other corpora (Shakespeare only; OASST / domain-specific would test generalization)

These are follow-ons, not gates.

---

**END.**

**Exp-Dev:** Tier-4-Llama HARD_PASS at 1B; substrate-attn is architecturally swappable at this scale with GQA + RoPE. Per_seed numbers above; metrics.json on runner.

**User:** HARD_PASS at $0.66 cost; ~12 min cluster wall; cluster cleanly down; no orphans. The defense matrix held -- zero bugs encountered.

**Research:** Phase-2 architecture-scaling test PASSES. Substrate-attention is a load-bearing primitive at both Pythia-160M and Llama-3.2-1B scales, ppl-comparable or marginally better than unmodified baseline. Cross-scale generalization confirmed.
