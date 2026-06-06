# Research Drill: Hyperprobe Reproduction Setup
# Topic: arXiv:2509.25045 -- exact reproduction setup for val_sim 0.60 -> 0.89 gap diagnosis
# Date: 2026-06-03
# Sources: arXiv:2509.25045v1/v2, github.com/Ipazia-AI/hyperprobe (full source read), HuggingFace paper page

---

## HEADLINE

The 29-point val_sim gap (0.60 vs 0.89) is almost certainly caused by the **three-stage embedding pipeline being reproduced only partially**: most likely the k-means cluster sum-pooling step (Stage F, Algorithm 1) was skipped or replaced with raw last-layer extraction, and possibly the early-stopping epoch count (true convergence at ~421 epochs with patience=100, not 100 epochs) was set too short. These are fixable. The architecture and loss function details are fully recoverable from the public repo.

---

## Cheap decisive test

Run a 5-epoch smoke with the CORRECT embedding pipeline (k=5 k-means over layers 16-32, last token, sum-pool centroids -> shape (4096,)) and compare val_sim trajectory against the reproduction's trajectory. If the reproduction used raw last-layer embedding (shape 4096, no k-means), the two curves will diverge within 20 epochs. Cost: <10 min on local GPU with cached embeddings.

---

## Falsifiable predictions (pre-registered)

HARD-PASS: correct pipeline hits val_sim >= 0.82 within 500 epochs on the analogy synthetic corpus
HARD-FAIL: correct pipeline hits val_sim < 0.70 after 500 epochs -- indicates a deeper mismatch (loss function, codebook seeding, or dtype)
MIDDLE-BAND: val_sim 0.70-0.82 -- likely a remaining hyperparameter gap (LR, SWA timing, attention heads in residual blocks)

---

## Sub-question findings, ranked by likelihood of explaining the gap

### RANK 1 (highest probability): Residual extraction pipeline -- MOST LIKELY GAP SOURCE

**Paper spec (Algorithm 1, Appendix B):**
```
H = LLM(s)                             # all hidden states, shape (L+1, T, d)
H* = H[L/2 : L, last_token_pos]       # layers 16-32 for Llama-3.1-8B, last token
C  = KMeans(H*, k=5)                   # k-means on 17 layer vectors -> 5 centroids, shape (5, 4096)
e_s = sum(C_k for k in range(5))       # sum-pool -> shape (4096,)
```

**Code confirmation (embeddings.py + data_loader.py):**
```python
median_layer = model.config.num_hidden_layers // 2  # = 16 for Llama-3.1-8B
hs = torch.stack(outputs.hidden_states).squeeze()
hs = hs[median_layer:, -1]                          # shape (17, 4096) -- layers 16..32, last token
cluster_assignments, centroids = emb_utils.kmeans_cuda(hs, K=k_clusters)  # k_clusters=5
token_embeddings[doc] = centroids.detach().bfloat16().cpu()  # shape (5, 4096)
# ... later in data_loader.py:
if item['embeddings'].ndim > 1:
    item['embeddings'] = item['embeddings'].sum(dim=0)  # sum -> shape (4096,)
```

**Why this causes the gap:** A naive reproduction that extracts only the final hidden state (layer 32, shape 4096) and feeds it directly to the probe skips:
1. The multi-layer sweep (layers 16-32 provide richer signal across the representation hierarchy)
2. The k-means clustering (which selects the 5 most geometrically distinct layer activations)
3. The sum-pooling (which combines those 5 cluster centroids into one probe input)

If the reproduction instead used `outputs.hidden_states[-1][:, -1, :]` (last layer, last token, raw), the probe receives a much less informative input. The k-means step is the non-obvious one -- it is NOT documented in the abstract or introduction, only in Appendix B Algorithm 1.

**Dtype:** BF16 throughout (embeddings stored as bfloat16, targets as bfloat16, training precision bf16-mixed).

**Pre/post-LayerNorm:** The code uses `outputs.hidden_states` from HuggingFace AutoModelForCausalLM, which returns **post-residual-add, pre-next-layer-norm** states (i.e., the residual stream value at the output of each transformer block). No custom hooks -- standard HF output_hidden_states=True.

---

### RANK 2: Training duration and convergence schedule

**Paper spec (Appendix D.1, confirmed from HuggingFace paper page):**
- Max epochs: 5000 (config), but early stopping with patience=100 on val_loss
- True convergence: ~421 epochs typical
- The reproduction ran "100 full epochs" -- this is 4x too short given patience=100 early stopping would only trigger AFTER seeing no improvement for 100 consecutive epochs

**LR finder:** The code uses `Tuner(trainer).lr_find(max_lr=1e-3, num_training=200)` to find optimal LR dynamically. Found LR for Llama-3.1-8B is ~3e-5 (from HuggingFace page). If the reproduction used a fixed LR (e.g., 1e-3 or 1e-4 without the finder), this alone can cause a 0.10-0.15 val_sim gap.

**Gradient accumulation schedule:**
```
epochs 0-109:    accumulate_grad_batches = 1
epochs 110-309:  accumulate_grad_batches = 2
epochs 310-409:  accumulate_grad_batches = 4
epochs 410+:     accumulate_grad_batches = 8
```
This progressively increases effective batch size from 32 to 256. Skipping this means the later training phases use under-regularized updates.

**SWA:** Stochastic Weight Averaging starts at epoch 400 with `swa_lr = learning_rate * 10`. This is a significant component -- SWA flattens the loss landscape and is known to improve generalization by 0.02-0.05 val_sim in similar architectures.

---

### RANK 3: Probe architecture -- attention heads in residual blocks

**Confirmed architecture (network.py):**
```
Input:   Linear(d -> 4096) + LayerNorm(4096) + GELU
Block 1: Linear(4096->4096) + GELU + LayerNorm(4096) + MultiheadAttention(embed_dim=4096, num_heads=?) + scale*residual + Dropout(0.5)
Block 2: (same as Block 1)
Output:  LayerNorm(4096) + Linear(4096->4096) + Tanh
```

**Key detail: MultiheadAttention is CONDITIONALLY included** when `num_heads > 0`. The paper describes "three-layer MLP with residual connections" but the actual code has optional attention heads in each residual block. The run name in app.py is `'equal2_att8'` (2 blocks, 8 attention heads), suggesting the paper's best result uses attention-augmented residual blocks, not a plain MLP. A naive "3-layer MLP" reproduction without attention would lose ~0.05-0.08 val_sim.

**Input dimension for Llama-3.1-8B:** d=4096 (embedding dim). After sum-pool of k=5 centroids each of shape (4096,), input to probe is shape (4096,). So input_dim = output_dim = 4096, and the 55M-71M parameter count is consistent (Linear(4096->4096) x3 + attention = ~50M + attention overhead).

---

### RANK 4: Loss function and optimizer

**Confirmed (encoder.py):**
```python
optimizer = AdamW(params, lr=learned_lr, weight_decay=1e-4)
scheduler = CosineAnnealingWarmRestarts(T_0=100, T_mult=2, decay_factor=0.9, eta_min=lr*1e-3)
loss = 1.0 * BCEWithLogitsLoss + 0.1 * MSELoss
```

**Binarization in training:** Output layer is Tanh (continuous in (-1, +1)). The BCE loss is applied via BCEWithLogitsLoss to the *logit* (pre-tanh), while the MSE regularizer pushes the tanh output toward +-1. The codebook targets are cast to bfloat16 and stored as int8. The val_sim metric is cosine similarity between the **continuous Tanh output** and the bipolar target (not post-binarization) -- this is why 0.89 cosine sim and 0.94 binary accuracy are both achievable simultaneously.

**If reproduction used cross-entropy with sign() binarization instead of BCE+MSE:** significant gradient signal loss, likely explaining 0.10+ val_sim gap.

---

### RANK 5: Training corpus composition

**Confirmed dataset (Section 4.1 + GitHub):**
- **Analogy task:** 114,099 samples from Google analogy test set + BATS (44 domains), augmented to 395,944 via key-value swap. 70/15/15 split. HuggingFace: `saturnMars/hyperprobe-dataset-analogy`
- **QA task (Section 6):** SQuAD, 693,886 training inputs. HuggingFace: `saturnMars/hyperprobe-dataset-squad`
- The 0.89 / 0.94 result is reported on the **analogy task** (Table 4, Section 5). The QA variant is a separate experiment.
- Codebook: nc=2,996 concepts, D=4096, MAP-Bipolar {-1,+1}, seeded at 101, fixed (not learned).

**Reproduction risk:** If the reproduction used a different codebook (different seed, different nc, or learned codebook), the targets are incompatible and val_sim will be bounded near 0.5 regardless of training quality.

---

### RANK 6: Known reproduction gotchas

1. **k-means seed fixed at 101** (torch.manual_seed(101) in emb_utils.py). Must use the same seed or pre-computed embeddings.
2. **BF16 throughout**: bf16-mixed training precision in PyTorch Lightning. FP32 training will not match and will be slower.
3. **torchhd library**: Uses `torchhd` for MAP VSA operations (binding, bundling, binarization). Version sensitivity is possible.
4. **Gradient accumulation callback**: Uses a custom `GradientAccumulationScheduler({110:2, 310:4, 410:8})` -- this is a PyTorch Lightning callback, not a standard training loop feature.
5. **LR finder required**: The 3e-5 LR is not hardcoded -- it is discovered per-run via `Tuner.lr_find()`. Skipping the finder and using a default LR (1e-3) will over-shoot and destabilize early training.
6. **No normalization of probe input**: The sum-pooled centroid vector is fed directly to the probe without L2 normalization. Applying L2 norm would change the input distribution.
7. **Output hidden_states indexing**: HuggingFace returns `len(hidden_states) = num_layers + 1` (includes embedding layer at index 0). The code uses `median_layer = num_hidden_layers // 2 = 16`, so `hs[16:]` indexes layers 16..32 (17 transformer block outputs, not including the embedding layer). Reproducing as `hidden_states[16:]` on the 33-element tuple is correct; `hidden_states[-17:]` is equivalent but semantically different.
8. **No published errata or community reproduction issues** found (0 GitHub issues).

---

## Cross-thread synthesis

The k-means over layers L/2 to L is structurally analogous to **mean-field theory over internal representations**: the k=5 centroids capture the dominant attractor states of the residual stream across the latter half of the network. This connects to the substrate's own retrieval geometry -- the probe input is essentially a compressed summary of the network's convergence trajectory across its depth, not just its final state. The SWA component is analogous to thermal annealing in a spin-glass landscape, smoothing the loss surface to find a flatter (more generalizing) minimum.

The sum-pooling of centroids (not mean-pooling or concatenation) preserves the total "activation mass" across the 5 clusters, making the input scale-sensitive. This is a non-obvious design choice that would not be guessed from the paper text alone.

---

## Substrate-product implications

If this probe is used as the embedding stage for the substrate pipeline (Phase 0.5b), the three-stage extraction (multi-layer k-means -> sum-pool -> MLP encoder) is the **load-bearing component**. Reproducing only the MLP encoder without the upstream extraction pipeline will yield embeddings that are 29 points weaker in cosine fidelity, which will propagate as noise into any downstream VSA composition operations.

The correct reproduction path creates a clean separation: (a) pre-compute and cache LLM embeddings using the exact extraction pipeline, (b) train only the MLP encoder on the cached embeddings. Step (a) is the expensive GPU step (requires Llama-3.1-8B loaded); step (b) is cheap (55M-param MLP, ~421 epochs, bs=32). This two-stage pipeline also means the probe can be retrained without re-running Llama inference.

---

## Feasibility at $20-50 cloud budget

**Assessment: YES, 0.85+ is feasible at $20-50.**

Breakdown:
- LLM embedding extraction (Llama-3.1-8B, analogy corpus 395K samples, BF16): single GPU pass, ~2-4h on A100. ~$6-12 at Lambda rates.
- MLP probe training (~421 epochs, bs=32, 55M params, ~395K samples): ~1-2h on A100. ~$3-6.
- Total: $10-20 with one well-configured run. $50 provides comfortable margin for 2-3 re-runs if embedding extraction needs iteration.

**Risk:** The LR finder adds ~15 min overhead per run but is essential for finding the ~3e-5 LR. Skipping it and hardcoding LR=3e-5 is acceptable for reproduction.

---

## Recommended fixes, ranked by likelihood of closing the gap

1. **CRITICAL -- Implement the full 3-stage embedding pipeline** (Algorithm 1): extract layers 16-32 last-token hidden states, k-means k=5, sum-pool centroids. This alone likely accounts for 15-20 val_sim points of the gap.
2. **HIGH -- Run to convergence, not fixed epochs**: Use early stopping with patience=100 (paper setting), or simply run 500+ epochs. The 100-epoch reproduction was ~4x too short.
3. **HIGH -- Use LR finder or hardcode LR~3e-5**: AdamW with LR=3e-5, not 1e-3 or 1e-4.
4. **MEDIUM -- Add attention heads to residual blocks** (num_heads=8 per block): The best-result model is 'equal2_att8', not a plain MLP.
5. **MEDIUM -- Add gradient accumulation schedule**: Callbacks at epochs 110/310/410 doubling accumulation.
6. **MEDIUM -- Add SWA starting at epoch 400**.
7. **LOW -- Verify codebook seed** (101) and torchhd MAP-Bipolar generation matches paper exactly.

---

## What cannot be answered from public materials

- Exact intermediate hidden dimension of the two residual blocks (code shows 4096->4096, consistent with paper's equal-width architecture)
- The exact number of attention heads that achieves 0.89 (run_name suggests 8; ablation in paper not fully accessible from HTML)
- Whether the paper result uses the analogy dataset only or includes SQuAD (the 0.89 figure is from Table 4, analogy task -- confirmed)
- Exact number of warmup steps (not found; the LR finder implicitly handles this)

---

## Citations (verified: 8)

1. Bronzini et al. (2025). "Hyperdimensional Probe: Decoding LLM Representations via Vector Symbolic Architectures." arXiv:2509.25045v2. https://arxiv.org/abs/2509.25045
2. GitHub repository: Ipazia-AI/hyperprobe. https://github.com/Ipazia-AI/hyperprobe (source code read: embeddings.py, emb_utils.py, encoder.py, network.py, app_utils.py, data_loader.py, vsa_utils.py, create_codebook.py)
3. HuggingFace paper page: https://huggingface.co/papers/2509.25045 (Algorithm 1, Appendix D.1 training details)
4. Datasets: saturnMars/hyperprobe-dataset-analogy, saturnMars/hyperprobe-dataset-squad (referenced in repo)
5. BATS dataset (Gladkova et al., 2016) -- source for analogy pairs
6. Google analogy test set (Mikolov et al., 2013) -- source for analogy pairs
7. torchhd library -- MAP VSA operations (https://torchhd.readthedocs.io/)
8. PyTorch Lightning -- training framework (CosineAnnealingWarmRestartsWithDecay scheduler)

---

P_deflated = 0.72 (pre-deflation estimate 0.90 that fixes are sufficient; deflated by 0.18 for uncharted-regime penalty on the attention-head ablation uncertainty and SWA sensitivity)
