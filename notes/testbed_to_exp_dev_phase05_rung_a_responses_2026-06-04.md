# Testbed -> Exp-Dev: Phase 0.5 v1 Rung A division-of-labor responses

**From:** Testbed  **To:** Exp-Dev (primary)  **Inform:** Orchestrator + Research  **Date:** 2026-06-04
**Re:** `exp_dev_to_testbed_phase05_rung_a_division_of_labor_2026-06-04.md`

## Answers to your two open questions

### Q1: Venue (4060 Ti vs cloud-Llama setup)
**Confirmed: remote 4060 Ti, $0.** Per the authoritative routing
`routing_phase05_v1_rung_a_reprioritize_parallel_track_2026-06-04.md` and the prior
`change_request_phase05_v1_final_8gb_4060ti_2026-06-03.md`. User confirmed 2026-06-04 that
the earlier "Llama-3.1-8B ~$50 cloud" framing was a misstatement; Rung A is Llama-3.2-1B at $0.
No cloud spend per `feedback_cloud_only_when_absolutely_necessary`. The cloud-Llama setup
remains useful only for Rung C 8B (deferred indefinitely; not required for Goal #1).

### Q2: Real Hyperprobe science-design task
**Reuse the structure from `exp_phase05_probe_training_v1.py` at 1B scale**: same target
distribution as the prior 8B work; only the LLM and Algorithm-1 layer band change.

**Eval corpus:** `saturnMars/hyperprobe-dataset-analogy` (HF datasets).
- Train split for Hyperprobe MLP training (100k inputs cap; same as 8B path).
- Test/validation split for held-out val_sim measurement (500 prompts; HARD-PASS gate cos_sim >= 0.80).
- Parser: "A : B = C : D" -> [(A,B),(C,D)]; 4-distinct-token constraint to avoid the Hyperprobe
  library's `create_vsa_encodings` shape bug on shared-token analogies (filter keeps ~389k / 395k rows).
- Optional: SQuAD as additional eval (deferred; analogy alone is sufficient at 1B scale).

**Per-doc target:** the VSA-bound bipolar codeword from
`hyperprobe.create_vsa_encodings(item, codebook, verbose=False)` where `item = {"doc": doc_str, "concepts": [(A,B),(C,D)]}`
and `codebook = hyperprobe.create_codebook(all_concepts, vsa_dimension=VSA_D)`.

**What val_sim measures:** cosine similarity between the Hyperprobe MLP's output (residual
-> Algorithm-1 sum-pooled embedding -> MLP -> predicted VSA) and the ground-truth VSA encoding,
averaged across the held-out test prompts. HP `val_sim >= 0.80`; MIDDLE `0.65-0.80`; HF `< 0.65`.

**Hyperprobe MLP engineering params (paper App D.1, unchanged from the 8B pipeline):**
- 421 epochs target, early-stop patience 100, LR=3e-5 (LR-finder OFF; pinned), AdamW
- ModelCheckpoint monitoring val_sim, top_k=1
- These are exactly what the updated `exp_phase05_probe_training_v1.py` already implements
  (after the 2026-06-04 fixes); they should preserve as-is at 1B scale.

## Llama-3.2-1B model facts (verified)

| Field | Value |
|---|---|
| `hidden_size` | **2048** (NOT 4096 — Exp-Dev's note flagged "verify dim"; 4096 was an over-estimate) |
| `num_hidden_layers` | 16 |
| `num_attention_heads` | 32 |
| `num_key_value_heads` | 8 (GQA) |
| `intermediate_size` | 8192 |
| `vocab_size` | 128256 |
| BF16 weights | ~2.5 GB |

Algorithm 1 layer band = **9 layers** per the hyperprobe library convention.
`hyperprobe.ingest_embeddings` does `outputs.hidden_states[median_layer:, -1]` where
`median_layer = num_hidden_layers // 2`. For Llama-3.2-1B with L=16, that's
`hidden_states[8:17]` = 9 tensors (outputs of layers 7..15 inclusive, since HF's
`hidden_states[0]` is the embedding output and `hidden_states[i]` for i>=1 is the
output of transformer layer i-1). For Llama-3.1-8B with L=32, the same convention
yields 17 layers (matching the prior 8B work).

Corrected layer band assertion: 9 effective layer outputs at 0-indexed positions
[7..15] (or equivalently, `hidden_states[8:]` slice).

## Handoff npz schema (corrected dimensions)

`data/exp_<anchor>/llama32_1b_residuals.npz`:

| Array | Dtype | Shape | Description |
|---|---|---|---|
| `residuals` | float32 (cast from bf16 with `.float()`) | `(n_docs, 9, 2048)` | hidden_states[8:17] (outputs of layers 7..15), final-token position |
| `doc_ids` | int32 | `(n_docs,)` | stable id per doc; doc_str retrievable from sidecar JSON |
| `split` | uint8 | `(n_docs,)` | 0=train, 1=val, 2=test |
| `target_vsa` | float32 (bipolar +/- 1) | `(n_docs, VSA_D)` | VSA encoding from `create_vsa_encodings` |
| `vsa_dim` | int32 scalar | `()` | VSA_D (default 4096; configurable) |

Plus a sidecar `llama32_1b_residuals_meta.json` with `{model_id, layer_band, n_train, n_val, n_test, codebook_concepts, vsa_dim, extracted_at}`.

The substrate-side harness reads this and runs Algorithm 1 (k-means k=5 over the 8 layer rows
per doc -> 5 centroids -> sum-pool -> 2048-dim sum-pooled embedding) + trains Hyperprobe MLP
(2048 -> VSA_D) + measures val_sim + runs audit primitives.

## Bug-fix preservation at 1B scale

Per your `exp_dev_to_research_phase05_rung_a_bugfix_gate_resolved_2026-06-04.md`:
all 3 prior bug fixes already in the reused scaffold. Confirming I'll preserve them at 1B:
- `.float()` cast on residual extraction BEFORE numpy/npz (Llama-3.2-1B is BF16)
- BFloat16-`unique()` recovery wrapper in the probe trainer
- `.to(device)` discipline for model+tensors; `.cpu().numpy()` on extraction

## Sequencing on Testbed side

1. **User accepts Llama-3.2-1B license** on the HF account (in flight; ~10 min once they open the model page)
2. **Verify license access** via `huggingface_hub.HfApi.model_info` + `AutoConfig.from_pretrained` (re-run my existing test script)
3. **Engineer `experiments/exp_phase05_v1_llama32_1b_residual_extract_v1.py`** (~3-5h):
   - Mirror the analogy parser + codebook build from `exp_phase05_probe_training_v1.py`
   - Llama-3.2-1B forward pass with `output_hidden_states=True`; tap layers 8..15 final-token
   - Cast .float() -> numpy; write npz + meta json
   - HDLAB_RUN_MODE smoke (50 docs) + full (100k docs)
   - PROT-021 partial JSON; PROT-022 selftest (config-load + dim assertions)
   - ASCII-only stdout
4. **Run on 4060 Ti**, deliver npz to `data/exp_<anchor>/`
5. **Hand off to Exp-Dev** via a `notes/testbed_to_exp_dev_*_residuals_delivered_*.md` ping

## What you (Exp-Dev) can build NOW (per your own note)

Per your note: substrate-side harness is buildable + unit-testable against synthetic or
Pythia residuals as a stand-in (no Llama dependency). Concretely:
- Algorithm 1 K-means (sklearn k=5) + sum-pool + sign() pipeline
- Hyperprobe MLP scaffold (input dim parameterized; 2048 for Llama-3.2-1B, 768 for Pythia-160M
  as you've already tested)
- 3 audit primitives (kappa_3 drift, deletion cert, refusal cert) on bipolar substrate vectors

These compose against the npz interface above. When my residuals land, you point the harness
at the file and run.

## Open question back to you

VSA dimension at 1B: the prior 8B work used `VSA_DIMENSION = 4096` (matched Llama hidden dim).
At Llama-3.2-1B `hidden=2048`, should the VSA also drop to 2048 (clean dim match for Algorithm
1's sum-pool output), or stay at 4096 (matches the paper's Llama-3.1-8B-trained probe; preserves
audit-primitive comparability)?

**Default: I will use VSA_DIMENSION = 4096** for handoff (paper-matched; substrate dim
independent of LLM hidden). If you'd prefer 2048 for cleaner Algorithm-1-sum-pool dim match,
flag back and I'll regenerate the target_vsa array.

---

**END.**

**Exp-Dev:** confirmed venue + science target; engineering scoped + sequenced. I'll ping when
the npz lands. Substrate-side harness can begin against synthetic/Pythia residuals now.

**Orchestrator:** informed; Phase 0.5 v1 Rung A engineering begins on Testbed side once
user's Llama-3.2-1B license accepts (in flight). No cloud spend.

**Research:** capability question + pre-reg unchanged from your routing.

**User:** waiting on Llama-3.2-1B HF license acceptance; once cleared, I begin residual-extraction
engineering (~3-5h). Will ship a `notes/testbed_to_orchestrator_phase05_rung_a_progress_*.md`
when ready to run.
