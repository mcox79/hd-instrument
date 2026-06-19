"""
phase05_probe_training_v1 -- Hyperprobe encoder training for Llama-3.1-8B.

WHY THIS EXISTS:
  arXiv:2509.25045 (Ipazia-AI/hyperprobe) publishes the code but NOT a pretrained
  checkpoint. To run Phase 0.5 Tier-7 sub-tests A/B/C, we train the encoder
  ourselves on Lambda A100. License is CC BY-NC-SA 4.0 (research use OK).

PIPELINE (Algorithm 1, Appendix B of arXiv:2509.25045):
  1. Clone Ipazia-AI/hyperprobe; pip install -e .
  2. Load saturnMars/hyperprobe-dataset-analogy + saturnMars/hyperprobe-dataset-squad
     from HuggingFace (token from env HF_TOKEN or /home/ubuntu/hd-instrument/.hf_token).
  3. Build VSA codebook from training-set concepts at vsa_dimension=4096.
  4. Llama-3.1-8B activation collection PER ALGORITHM 1:
       Stage 1: collect residuals from layers [L/2 .. L] (Llama-3.1-8B L=32 ->
                layers 16..32 inclusive = 17 layers) at final-token position.
       Stage 2: k-means cluster the 17 layer-residuals with k=5 -> 5 centroids
                per doc (shape: (5, 4096) for D=4096).
       Stage 3: sum-pool the 5 centroids -> final (4096,) embedding fed to
                encoder.
       Implementation: hyperprobe.ingest_embeddings(docs, model, k_clusters=5)
       returns the (5,D) centroids tensor per doc. Sum-pool happens at line
       259 ('emb.sum(dim=0)'). Algorithm 1 is fully realized by the library;
       earlier versions of this script ran k=5 in training but validation used
       k=1, which broke the train/eval embedding-distribution match.
  5. Train encoder via _train_hyperprobe_v2(loader, configs) -- replaces the
     library's train_hyperprobe to (a) pin LR=3e-5 explicitly (skip LR finder
     which was unreliable in the 2026-06-03 run that landed val_sim=0.60),
     (b) early-stop patience=100 (paper Appendix D.1) vs library default 200,
     (c) max_epochs=421 (paper converges ~421 epochs; library default fell
     into the run-too-short bin at 100 epochs).
  6. Save checkpoint to data/exp_phase05_probe_training_v1/probe_ckpt.ckpt.

PRE-REGISTERED BANDS (training-side; validation handled by separate anchor):
  HARD-PASS: training converges (final val loss < initial val loss * 0.5;
             no NaN; no divergence in last 10 epochs).
  HARD-FAIL: NaN or loss increase in last 10 epochs OR convergence fails to
             reach the 0.5x threshold within configured epoch budget.

PROT-018: no _nN suffix (LLM-native VSA_DIM=4096 -> probe_D=4096; doesn't bind
substrate N).

THIS SCRIPT IS LAMBDA-ONLY. Will not run on laptop (requires Llama-3.1-8B
checkpoint + GPU). Local smoke = import + structural checks only.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "phase05_probe_training_v1"

LLM_MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
LAYER_FRAC = 0.7                  # research-confirmed: layer 22 of 32 = 69% depth
VSA_DIMENSION = 4096              # Llama hidden = 4096; probe D = 4096

# Training schedule per paper Appendix D.1 (corrects 2026-06-03 H100 run that
# landed val_sim=0.60 vs paper 0.89). Three causes diagnosed by research:
#   (1) Algorithm 1 already implemented by ingest_embeddings(k=5) -- preserved.
#   (2) Run was 4x too short: 100 epochs -> 421 epochs (true convergence).
#   (3) LR finder was unreliable: pin LR=3e-5 explicitly (paper-derived value).
# Library defaults: epochs=configs['epochs'] (uncapped), LR=1e-4 with lr_find
# override, EarlyStopping patience=200. Our overrides match paper Appendix D.1.
N_EPOCHS_FULL = 421
N_EPOCHS_SMOKE = 2
BATCH_SIZE_FULL = 32
BATCH_SIZE_SMOKE = 8
K_CLUSTERS = 5                    # paper Algorithm 1: k=5 k-means clusters
EARLY_STOP_PATIENCE = 100         # paper Appendix D.1 (library default 200)
LEARNING_RATE = 3e-5              # paper Appendix D.1 (override library 1e-4)

# Embedding-pipeline version stamp (cached pickle invalidation marker).
# Bump when changing layer range, k_clusters, or pooling scheme so resume
# code rejects stale caches.
EMBEDDING_PIPELINE_VERSION = "alg1_v1_median_to_final_k5_sum"

HYPERPROBE_REPO_URL = "https://github.com/Ipazia-AI/hyperprobe.git"
HYPERPROBE_LOCAL_DIR = "/home/ubuntu/hyperprobe"  # Lambda standard
ANALOGY_DATASET = "saturnMars/hyperprobe-dataset-analogy"
SQUAD_DATASET = "saturnMars/hyperprobe-dataset-squad"


def _load_hf_token() -> str:
    """Read HF token from env HF_TOKEN, fallback to .hf_token file at repo root.

    Lambda bring-up sets HF_TOKEN as env var; .hf_token is the local-dev path.
    """
    tok = os.environ.get("HF_TOKEN", "").strip()
    if tok:
        return tok
    tok_path = REPO / ".hf_token"
    if tok_path.exists():
        return tok_path.read_text(encoding="utf-8").strip()
    raise RuntimeError(
        "HF token not found: set HF_TOKEN env var or place token at <repo>/.hf_token"
    )


def _ensure_hyperprobe_repo() -> Path:
    """Clone + pip install Ipazia-AI/hyperprobe if not already present.

    Looks first at HYPERPROBE_LOCAL_DIR (Lambda standard path); falls back to
    REPO/extern/hyperprobe for laptop/CI.
    """
    candidates = [Path(HYPERPROBE_LOCAL_DIR), REPO / "extern" / "hyperprobe"]
    for path in candidates:
        if path.exists() and (path / "pyproject.toml").exists():
            return path
    # Clone to extern/
    target = REPO / "extern" / "hyperprobe"
    target.parent.mkdir(parents=True, exist_ok=True)
    print(f"  cloning {HYPERPROBE_REPO_URL} -> {target}", flush=True)
    subprocess.run(["git", "clone", HYPERPROBE_REPO_URL, str(target)],
                   check=True, capture_output=False)
    print(f"  installing hyperprobe via pip install -e .", flush=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(target)],
                   check=True, capture_output=False)
    return target


def _selftest_structural():
    """Local smoke: verify imports + structural assumptions without GPU."""
    # Token presence (don't echo)
    try:
        tok = _load_hf_token()
        assert tok.startswith("hf_") and len(tok) >= 20, "token shape wrong"
    except Exception as e:
        print(f"[selftest] WARN: HF token not available ({e}); skipping token check",
              flush=True)
    # Layer 22 sanity: Llama-3.1-8B has 32 layers; 0.7 * 32 = 22.4 -> layer 22 (0-indexed 21)
    L = 32
    layer = int(round(LAYER_FRAC * L)) - 1  # 0-indexed
    assert 18 <= layer <= 25, f"layer {layer} outside expected band 18-25"
    # Paper Algorithm 1 uses median-to-final layer band, not single layer:
    median_layer = L // 2            # 16 for Llama-3.1-8B
    band_size = L - median_layer + 1  # layers 16..32 inclusive = 17 layers
    assert median_layer == 16, f"median layer L/2 wrong: got {median_layer}"
    assert band_size == 17, f"alg1 band size wrong: got {band_size}"
    # Training config (paper Appendix D.1):
    assert N_EPOCHS_FULL == 421, f"FULL epochs must be 421 (paper); got {N_EPOCHS_FULL}"
    assert K_CLUSTERS == 5, f"k_clusters must be 5 (paper alg1); got {K_CLUSTERS}"
    assert EARLY_STOP_PATIENCE == 100, (
        f"early-stop patience must be 100 (paper appendix D.1); "
        f"got {EARLY_STOP_PATIENCE}")
    assert abs(LEARNING_RATE - 3e-5) < 1e-9, (
        f"learning rate must be 3e-5 (paper appendix D.1); got {LEARNING_RATE}")
    print(f"[selftest] PASS: HF token shape OK; target layer index = {layer} "
          f"(0-indexed) of L={L}; VSA_DIM={VSA_DIMENSION}; "
          f"alg1 band=layers[{median_layer}..{L}]={band_size}layers; "
          f"k_clusters={K_CLUSTERS}; epochs={N_EPOCHS_FULL}; "
          f"LR={LEARNING_RATE}; patience={EARLY_STOP_PATIENCE}",
          flush=True)


def _selftest_algorithm1_embedding_pipeline():
    """Verify Algorithm 1 (Appendix B) pipeline on synthetic data.

    Stages (per paper):
      1. Collect residuals from layers [L/2 .. L] at final-token position.
      2. K-means cluster the stacked layer-residuals with k=5 -> 5 centroids.
      3. Sum-pool the 5 centroids -> final (D,) embedding.

    Synthetic data: fake hidden_states tuple of (L+1) tensors of shape
    (1, n_tokens, hidden). Tuple has length L+1 because HuggingFace includes
    the embedding layer (index 0) plus L transformer layers (indices 1..L).
    Verifies: median_layer slicing matches paper, k-means produces k=5
    centroids, sum-pool produces shape (D,), seed determinism.
    """
    import numpy as np
    # sklearn is required for FULL run; absence on local-dev is acceptable as
    # long as we test the algebra surrogate (numpy KMeans via lloyd's algorithm
    # would be too heavy here; instead verify shapes against a stub).
    try:
        from sklearn.cluster import KMeans
        sklearn_available = True
    except Exception as e:
        sklearn_available = False
        sklearn_err = str(e)

    L = 32                # Llama-3.1-8B has 32 transformer layers
    n_tokens = 8          # arbitrary prompt length
    hidden = 32           # small surrogate for D=4096
    k_clusters = 5
    seed = 101

    # Synthesize hidden_states tuple of length L+1 (embedding layer + 32 layers)
    rng = np.random.default_rng(seed)
    hidden_states = []
    for i in range(L + 1):
        hs_i = rng.standard_normal((1, n_tokens, hidden)).astype(np.float32)
        hidden_states.append(hs_i)
    hidden_states = tuple(hidden_states)
    assert len(hidden_states) == L + 1, (
        f"expected L+1={L+1} hidden states; got {len(hidden_states)}")

    # Stage 1: slice [median..L] inclusive at final token position
    # (mirrors hyperprobe.ingest_embeddings: hs[median:, -1] over stacked layers)
    median = L // 2     # 16
    layer_slice = np.stack([hidden_states[i][0, -1, :] for i in range(median, L + 1)],
                            axis=0)
    # Note: hyperprobe's torch.stack(outputs.hidden_states).squeeze()[median:, -1]
    # yields shape (L+1-median, hidden) = (17, hidden) for Llama-3.1-8B.
    assert layer_slice.shape == (L + 1 - median, hidden), (
        f"stage1 shape wrong: got {layer_slice.shape}, "
        f"expected ({L+1-median}, {hidden})")
    assert layer_slice.shape[0] == 17, (
        f"alg1 band size must be 17 for Llama-3.1-8B; got {layer_slice.shape[0]}")

    if not sklearn_available:
        print(f"[selftest] alg1 partial PASS (sklearn unavailable: {sklearn_err}); "
              f"stage1 shape={layer_slice.shape} OK; "
              f"k-means + sum-pool checks skipped (run on Lambda where sklearn "
              f"is installed)", flush=True)
        return

    # Stage 2: k-means with k=5
    km = KMeans(n_clusters=k_clusters, random_state=seed, n_init=10)
    km.fit(layer_slice)
    centroids = km.cluster_centers_   # shape (5, hidden)
    assert centroids.shape == (k_clusters, hidden), (
        f"stage2 centroids shape wrong: got {centroids.shape}, "
        f"expected ({k_clusters}, {hidden})")

    # Stage 3: sum-pool the 5 centroids -> (hidden,)
    pooled = centroids.sum(axis=0)
    assert pooled.shape == (hidden,), (
        f"stage3 sum-pool shape wrong: got {pooled.shape}, "
        f"expected ({hidden},)")

    # Determinism: re-run with same seed should yield same pooled vector
    km2 = KMeans(n_clusters=k_clusters, random_state=seed, n_init=10)
    km2.fit(layer_slice)
    centroids2 = km2.cluster_centers_
    pooled2 = centroids2.sum(axis=0)
    # k-means centroid ordering may differ across runs; compare sum-of-sorted
    # centroid magnitudes (rotation-invariant) AND the pooled sum (which
    # IS order-invariant since it just sums).
    diff = float(np.abs(pooled - pooled2).max())
    assert diff < 1e-5, (
        f"alg1 sum-pool not deterministic across seeded re-runs: "
        f"max abs diff = {diff}")

    print(f"[selftest] alg1 PASS: stage1 shape={layer_slice.shape}; "
          f"stage2 centroids={centroids.shape}; stage3 pooled={pooled.shape}; "
          f"deterministic across re-runs (max_abs_diff={diff:.2e})",
          flush=True)


_selftest_structural()
_selftest_algorithm1_embedding_pipeline()


def _train_hyperprobe_v2(loader, configs: dict, *,
                          learning_rate: float = LEARNING_RATE,
                          early_stop_patience: int = EARLY_STOP_PATIENCE,
                          weight_decay: float = 1e-4,
                          drop_p: float = 0.5,
                          run_mode: str = "full"):
    """Train VSAEncoder mirroring hyperprobe.train_hyperprobe but with paper-
    aligned overrides for the 2026-06-03 H100 val_sim=0.60 regression.

    Differences vs library train_hyperprobe:
      * learning_rate is PINNED to `learning_rate` (default 3e-5 per paper
        Appendix D.1). Library uses LR=1e-4 + Tuner.lr_find(max_lr=1e-3)
        which has been unreliable across runs and likely sourced the 60%
        regression.
      * EarlyStopping patience = `early_stop_patience` (default 100 per paper
        Appendix D.1). Library default is 200 which is too loose given the
        421-epoch run length.
      * SWA disabled when max_epochs < 400 (paper convergence is ~421 so SWA
        does run in FULL, but a smoke max_epochs=2 must NOT enable a SWA
        callback with swa_epoch_start=400 -- this triggered a
        ValueError in pre-1.x Lightning when swa_epoch_start > max_epochs).
      * GradientAccumulationScheduler restricted to keys < max_epochs.
      * No Tuner.lr_find() call (cuts ~200 training iterations of warmup time
        AND the unreliable LR override).
      * LR-finder PDF artifact not produced (no Tuner step).
      * All other callbacks (ModelCheckpoint, LearningRateMonitor, logger
        setup) preserved.

    Returns: (best_model_path, test_metrics)
    """
    # Imports deferred to keep local-smoke (no Lightning) clean.
    from datetime import datetime
    from os import path, makedirs
    import json as _json
    import torch as _torch
    from lightning import Trainer
    from lightning.pytorch.loggers import TensorBoardLogger
    from lightning.pytorch.callbacks.early_stopping import EarlyStopping
    from lightning.pytorch.callbacks import (
        ModelCheckpoint,
        StochasticWeightAveraging,
        LearningRateMonitor,
        GradientAccumulationScheduler,
    )
    import hyperprobe as _hp

    # Random seed for reproducibility (matches upstream)
    _torch.manual_seed(101)

    # Build VSAEncoder with explicit LR override
    model = _hp.VSAEncoder(
        input_dim=loader.get_input_dim(),
        output_dim=loader.get_target_dim(),
        learning_rate=learning_rate,
        weight_decay=weight_decay,
        drop_p=drop_p,
    )

    logger = TensorBoardLogger(
        save_dir=path.join(configs['app']['folder'], '_logs'),
        name=datetime.now().strftime("%d%b").lower(),
        version=configs['app']['run_name'] + '_' + model.model.name + "_v2",
        sub_dir=datetime.now().strftime("%Hh%Mm"),
        default_hp_metric=False,
    )
    makedirs(logger.log_dir, exist_ok=True)
    with open(path.join(logger.log_dir, 'app_configs.json'), 'w', encoding='utf-8') as f:
        _json.dump({
            **configs,
            "_overrides": {
                "learning_rate": learning_rate,
                "early_stop_patience": early_stop_patience,
                "weight_decay": weight_decay,
                "drop_p": drop_p,
                "lr_finder": False,
                "trainer_v2": True,
            },
        }, f, indent=4)
    with open(path.join(logger.log_dir, 'model_summary.txt'), 'w', encoding='utf-8') as f:
        f.write(str(model.model))

    _torch.cuda.empty_cache()

    # Callbacks: SWA + GradientAccumulationScheduler gated on max_epochs >= 400.
    # For smoke (max_epochs=2) these would fire after training and ValueError.
    max_epochs = int(configs['epochs'])
    callbacks = [
        EarlyStopping(monitor="val_loss", patience=early_stop_patience,
                       mode='min', verbose=False),
        ModelCheckpoint(
            monitor="val_sim", mode='max', save_top_k=1,
            dirpath=path.join(configs['app']['folder'], 'models',
                              datetime.now().strftime("%d%b").lower()),
            filename=configs['app']['run_name'] + '_' + model.model.name + '_{val_sim:.0%}',
        ),
        LearningRateMonitor(logging_interval='epoch'),
    ]
    # GradientAccumulationScheduler at 110/310/410 only if those epochs are in
    # range. Library hardcodes {110: 2, 310: 4, 410: 8}; keep keys < max_epochs.
    grad_accum_full = {110: 2, 310: 4, 410: 8}
    grad_accum_filtered = {k: v for k, v in grad_accum_full.items() if k < max_epochs}
    if grad_accum_filtered:
        callbacks.append(GradientAccumulationScheduler(scheduling=grad_accum_filtered))
    # SWA starts at epoch 400 in upstream; only enable for FULL-length runs.
    swa_epoch_start = 400
    if max_epochs >= swa_epoch_start + 1:
        callbacks.append(StochasticWeightAveraging(
            swa_lrs=learning_rate * 10, swa_epoch_start=swa_epoch_start))

    trainer = Trainer(
        devices=[_torch.cuda.device_count() - 1] if _torch.cuda.is_available() else 1,
        precision='bf16-mixed',
        logger=logger,
        max_epochs=max_epochs,
        deterministic=True,
        callbacks=callbacks,
    )

    print(f"  [trainer_v2] LR={learning_rate} (pinned, no LR-finder); "
          f"patience={early_stop_patience}; max_epochs={max_epochs}; "
          f"SWA@{swa_epoch_start}={'yes' if max_epochs >= swa_epoch_start + 1 else 'no'}; "
          f"grad_accum_keys={list(grad_accum_filtered.keys())}", flush=True)

    trainer.fit(model, datamodule=loader)
    best_model_path = trainer.checkpoint_callback.best_model_path

    # Evaluate on test set (may hit the known torchmetrics BFloat16 unique bug;
    # caller wraps with the same recovery path as the legacy train_hyperprobe).
    test_metrics = trainer.test(model=model, datamodule=loader, ckpt_path='best')[0]
    with open(path.join(trainer.log_dir, 'results.json'), 'w', encoding='utf-8') as f:
        _json.dump(test_metrics, f)
    return best_model_path, test_metrics


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "smoke")
    epochs = N_EPOCHS_FULL if run_mode == "full" else N_EPOCHS_SMOKE
    batch_size = BATCH_SIZE_FULL if run_mode == "full" else BATCH_SIZE_SMOKE

    print(f"[{ANCHOR_NAME}] run_mode={run_mode} llm={LLM_MODEL_ID} "
          f"layer_frac={LAYER_FRAC} vsa_dim={VSA_DIMENSION} "
          f"epochs={epochs} batch_size={batch_size}", flush=True)
    print(f"  HF_TOKEN: required (read from env or .hf_token)", flush=True)
    print(f"  GPU: required (Llama-3.1-8B + activation collection)", flush=True)

    t0 = time.time()
    tok = _load_hf_token()
    os.environ["HF_TOKEN"] = tok
    os.environ["HUGGINGFACE_HUB_TOKEN"] = tok

    # Step 1: ensure hyperprobe repo
    hp_dir = _ensure_hyperprobe_repo()
    print(f"  hyperprobe repo: {hp_dir}", flush=True)

    # Step 2: imports (guarded; this script is Lambda-only for real run)
    try:
        import hyperprobe  # noqa: F401
        from datasets import load_dataset
        from huggingface_hub import login as hf_login
    except Exception as e:
        raise RuntimeError(
            f"hyperprobe/datasets/huggingface_hub import failed: {e}. "
            f"Run on Lambda after bring-up (pip install -e {hp_dir})."
        )
    hf_login(token=tok, add_to_git_credential=False)

    # Step 3: load analogy dataset (the parseable one). SQuAD's schema is
    # title/doc/answers/question_features/answer_features -- different shape,
    # doesn't fit hyperprobe's create_vsa_encodings(item, concepts=[(s,o),...])
    # API without additional engineering. Analogy alone has 395k train /
    # 114k test rows -- plenty for MVP encoder training.
    print(f"  loading {ANALOGY_DATASET} ...", flush=True)
    analogy_ds = load_dataset(ANALOGY_DATASET, token=tok)
    print(f"  analogy splits: {list(analogy_ds.keys())} "
          f"columns={analogy_ds['train'].column_names}", flush=True)

    # Step 4: parse analogy "A : B = C : D" docs into concept pairs.
    # Example row: doc=' 10 : 1 = 100 : 10' -> concepts=[('10','1'), ('100','10')]
    def _parse_analogy(doc):
        """'A : B = C : D' -> [(A,B),(C,D)] iff {A,B,C,D} are 4 distinct
        (case-folded) tokens. Hyperprobe's create_vsa_encodings has a
        tensor-shape bug when pairs share tokens (e.g., math '10:1=100:10');
        we filter those out at parse time. 389k of 395k analogy rows pass."""
        s = (doc or "").strip()
        if "=" not in s or ":" not in s:
            return None
        parts = s.split("=")
        if len(parts) != 2:
            return None
        pairs = []
        for part in parts:
            sub = part.strip().split(":")
            if len(sub) == 2:
                a = sub[0].strip()
                b = sub[1].strip()
                if a and b:
                    pairs.append((a, b))
        if len(pairs) < 2:
            return None
        # 4-distinct-tokens constraint (no overlap between pairs)
        all_toks = set(t.lower() for t in pairs[0] + pairs[1])
        if len(all_toks) != 4:
            return None
        return pairs

    # R1-aggressive per research 2026-06-02: 100k inputs x 100 epochs (was 5k
    # x 60). Dispatch 10 probe landed val_sim=58%; research's analysis: 5k x 60
    # = 300k samples seen is 132x less than paper's 39.5M. 100k x 100 = 10M
    # samples expected to land probe quality 0.78-0.86 (vs paper 0.89).
    MAX_INPUTS_FULL = 100000
    MAX_INPUTS_SMOKE = 200
    target_n = MAX_INPUTS_FULL if run_mode == "full" else MAX_INPUTS_SMOKE

    train_inputs = []
    for row in analogy_ds["train"]:
        concepts = _parse_analogy(row["doc"])
        if concepts is None:
            continue
        train_inputs.append({"doc": row["doc"], "concepts": concepts})
        if len(train_inputs) >= target_n:
            break
    print(f"  training inputs after parse: {len(train_inputs)} "
          f"(target {target_n})", flush=True)
    if len(train_inputs) < 50:
        raise RuntimeError(
            f"Too few training inputs ({len(train_inputs)}) parsed from analogy; "
            f"check 'A : B = C : D' format -- first row doc: "
            f"{analogy_ds['train'][0]['doc']!r}"
        )

    # Step 5: codebook from training-set concepts
    all_concepts = set()
    for item in train_inputs:
        for pair in item["concepts"]:
            for c in pair:
                if isinstance(c, str):
                    all_concepts.add(c)
    codebook = hyperprobe.create_codebook(concepts=list(all_concepts),
                                           vsa_dimension=VSA_DIMENSION)
    print(f"  codebook: {len(all_concepts)} concepts @ D={VSA_DIMENSION}", flush=True)

    # Step 6: LLM activation collection (Llama-3.1-8B + sum pooling).
    # Dispatch 12 lesson: the multiprocessing.Pool(1).apply(...) wrapper from
    # hyperprobe's paper script hits torch's per-tensor mmap shared-memory
    # limit at 100k scale (RuntimeError: unable to mmap 40960 bytes ... Cannot
    # allocate memory). Drop the subprocess; call directly. Llama-3.1-8B
    # forward + downstream encoder training fit comfortably in H100 80GB.
    #
    # Also: persist embeddings to disk after ingest so encoder-training
    # failures don't waste the 53-min Llama forward pass.
    import pickle
    docs = [item["doc"] for item in train_inputs]
    emb_cache_path = out_dir / "ingested_embeddings.pkl"
    # PROT-021-style cache invalidation: the pickle now carries a version stamp
    # so a stale single-layer or wrong-k cache cannot silently be reused by a
    # new k_clusters / pooling pipeline. Cache header schema:
    #   {"_pipeline_version": str, "_k_clusters": int, "_pooling": str,
    #    "_llm_model_id": str, "embeddings": dict[doc -> tensor]}
    # Legacy caches (bare dict, no _pipeline_version) are REJECTED.
    cache_valid = False
    if emb_cache_path.exists():
        try:
            with open(emb_cache_path, "rb") as f:
                cache_obj = pickle.load(f)
        except Exception as e:
            print(f"  [resume] cache load failed ({e}); re-ingesting",
                  flush=True)
            cache_obj = None
        if isinstance(cache_obj, dict) and cache_obj.get("_pipeline_version") == EMBEDDING_PIPELINE_VERSION \
                and cache_obj.get("_k_clusters") == K_CLUSTERS \
                and cache_obj.get("_llm_model_id") == LLM_MODEL_ID:
            llm_embeddings = cache_obj["embeddings"]
            print(f"  [resume] loading cached embeddings from {emb_cache_path} "
                  f"({len(llm_embeddings)} docs; pipeline={EMBEDDING_PIPELINE_VERSION}; "
                  f"k={K_CLUSTERS})", flush=True)
            cache_valid = True
        else:
            # Legacy / stale cache: warn + ignore. Don't auto-delete the file
            # so operators can inspect it; just overwrite atomically below.
            stamp = (cache_obj or {}).get("_pipeline_version") if isinstance(cache_obj, dict) else "<legacy_bare_dict>"
            print(f"  [resume] REJECTED stale cache at {emb_cache_path} "
                  f"(stamp={stamp!r}, expected={EMBEDDING_PIPELINE_VERSION!r}); "
                  f"re-ingesting", flush=True)
    if not cache_valid:
        print(f"  ingesting {len(docs)} LLM embeddings via {LLM_MODEL_ID} "
              f"(Algorithm 1: median-to-final layer band, k_clusters={K_CLUSTERS}, "
              f"sum-pool centroids; direct call, no subprocess) ...", flush=True)
        # hyperprobe.ingest_embeddings implements Algorithm 1 stages 1+2:
        #   stage 1: hs[median_layer:, -1] over outputs.hidden_states (last token,
        #            layers L/2..L) -- 17 layers for Llama-3.1-8B L=32.
        #   stage 2: kmeans_cuda over those 17 layer-residuals with K=k_clusters
        #            returns (k_clusters, D)=(5, 4096) centroids per doc.
        # Stage 3 (sum-pool) is the .sum(dim=0) below.
        llm_embeddings, *_ = hyperprobe.ingest_embeddings(
            docs, LLM_MODEL_ID, K_CLUSTERS,
        )
        # Stage 3: sum-pool the 5 centroids -> (D,). This matches Algorithm 1
        # ("sum pooling" per paper Section 4.3 / Appendix B) and the upstream
        # paper script in hyperprobe's examples.
        llm_embeddings = {
            doc: emb.sum(dim=0).detach().cpu()
            for doc, emb in llm_embeddings.items()
        }
        print(f"  persisting {len(llm_embeddings)} embeddings -> "
              f"{emb_cache_path} (insurance for trainer.fit failures; "
              f"pipeline_version={EMBEDDING_PIPELINE_VERSION})",
              flush=True)
        cache_obj = {
            "_pipeline_version": EMBEDDING_PIPELINE_VERSION,
            "_k_clusters": K_CLUSTERS,
            "_pooling": "sum",
            "_llm_model_id": LLM_MODEL_ID,
            "embeddings": llm_embeddings,
        }
        tmp_path = emb_cache_path.with_suffix(".pkl.tmp")
        with open(tmp_path, "wb") as f:
            pickle.dump(cache_obj, f, protocol=pickle.HIGHEST_PROTOCOL)
        tmp_path.replace(emb_cache_path)
    for item in train_inputs:
        item["embeddings"] = llm_embeddings.get(item["doc"])
    train_inputs = [it for it in train_inputs if it.get("embeddings") is not None]
    print(f"  inputs with embeddings: {len(train_inputs)}", flush=True)

    # Step 7: VSA encodings per item
    for item in train_inputs:
        item["vsa"] = hyperprobe.create_vsa_encodings(item, codebook, verbose=False)

    # Step 8: dataloader + train
    configs = {
        "splits": {"val": 0.1, "test": 0.1},
        "epochs": epochs,
        "batch_size": batch_size,
        "app": {
            "folder": str(out_dir),
            "run_name": LLM_MODEL_ID.split("/")[-1].replace("-", "_") + "_phase05",
        },
    }
    dataset = hyperprobe.inputDataset(train_inputs)
    loader = hyperprobe.llm2VSA_dataloader(
        dataset,
        batch_size=configs["batch_size"],
        val_size=configs["splits"]["val"],
        test_size=configs["splits"]["test"],
    )
    print(f"  training {epochs} epochs at batch={batch_size} ...", flush=True)
    # _train_hyperprobe_v2 mirrors hyperprobe.train_hyperprobe but pins
    # LR=3e-5 + EarlyStopping patience=100 + skips LR-finder (paper Appendix
    # D.1). See _train_hyperprobe_v2 docstring for the full diff vs upstream.
    # Known hyperprobe issue: trainer hardcodes precision='bf16-mixed', and
    # torchmetrics.BinaryAccuracy.update calls torch.unique() on the target
    # tensor -- which fails on BFloat16. Wrap with recovery: if the post-fit
    # test_step crashes on this specific error, find the saved checkpoint
    # ourselves and proceed (training succeeded; only the test-metric reporting
    # failed). Validation anchor downstream computes the real quality metrics
    # independently anyway.
    test_metrics = {}
    best_model_path = None
    try:
        best_model_path, test_metrics = _train_hyperprobe_v2(
            loader, configs=configs, run_mode=run_mode)
        print(f"  trained: best ckpt -> {best_model_path}", flush=True)
    except RuntimeError as e:
        msg = str(e)
        if "unique" in msg and ("BFloat16" in msg or "bfloat16" in msg.lower()):
            print(f"  [recover] hyperprobe trainer.test BFloat16 unique bug "
                  f"(known); locating saved checkpoint manually...", flush=True)
            import glob
            ckpt_glob = str(out_dir / "models" / "*" / "*.ckpt")
            ckpts = sorted(glob.glob(ckpt_glob))
            if not ckpts:
                # Fall back to logger subdirectory layout
                ckpt_glob2 = str(out_dir / "_logs" / "**" / "*.ckpt")
                ckpts = sorted(glob.glob(ckpt_glob2, recursive=True))
            if not ckpts:
                print(f"  [recover] no checkpoint found under {out_dir}/models/* "
                      f"or {out_dir}/_logs/**", flush=True)
                raise
            best_model_path = ckpts[-1]
            test_metrics = {"_recovered": True,
                             "_test_step_error": "torchmetrics BFloat16 unique"}
            print(f"  [recover] best_model_path={best_model_path}", flush=True)
        else:
            raise

    # Step 9: persist canonical paths for downstream anchors
    ckpt_dest = out_dir / "probe_ckpt.ckpt"
    if Path(best_model_path) != ckpt_dest:
        shutil.copy2(best_model_path, ckpt_dest)
    codebook_path = out_dir / "codebook.json"
    # Persist codebook as JSON (round-trip-safe for downstream encoder)
    codebook_serializable = {c: list(map(float, codebook[c])) for c in codebook}
    codebook_path.write_text(json.dumps(codebook_serializable), encoding="utf-8")

    elapsed = time.time() - t0

    # Step 10: verdict from training-side telemetry. The validation anchor
    # downstream computes the real cos_sim/binary_acc on a held-out set; here
    # we just gate on "checkpoint exists" + (if available) test metrics.
    val_loss_final = float(test_metrics.get("val_loss_final", float("nan")))
    val_loss_initial = float(test_metrics.get("val_loss_initial", float("nan")))
    cos_sim_test = float(test_metrics.get("cos_sim", test_metrics.get("test_cos_sim", float("nan"))))
    binary_acc_test = float(test_metrics.get("binary_acc", test_metrics.get("test_binary_acc", float("nan"))))
    test_recovered = bool(test_metrics.get("_recovered", False))

    ckpt_exists = (best_model_path is not None) and Path(best_model_path).exists()
    converged = (val_loss_final < 0.5 * val_loss_initial) if (val_loss_initial > 0) else None

    # NaN/Inf check: training-side metrics must be finite to claim HARD_PASS.
    # Per [[feedback-verdict-msg-honest-reread]]: do NOT stamp HARD_PASS based
    # on "checkpoint exists" alone -- the test_step recovery path (BFloat16
    # unique bug in upstream torchmetrics) leaves all training-side metrics
    # as NaN, and a HARD_PASS stamp under those conditions is a label-vs-honest
    # violation. The 2026-06-03 H100 run crashed with this exact issue.
    def _finite(x: float) -> bool:
        return x == x and abs(x) != float("inf")

    training_metrics_finite = (_finite(val_loss_initial) and _finite(val_loss_final)
                                and _finite(cos_sim_test) and _finite(binary_acc_test))

    if not ckpt_exists:
        verdict = "HARD_FAIL"
    elif test_recovered or not training_metrics_finite:
        # Either explicit recovery (BFloat16 unique bug) OR any of the test
        # metrics are NaN/Inf. We cannot honestly claim HARD_PASS without
        # finite quality numbers. Downstream validation anchor (Wave 2) will
        # compute real cos_sim + binary_acc on a held-out set; until then,
        # this run is MIDDLE_BAND (ckpt usable, quality unknown).
        verdict = "MIDDLE_BAND"
    elif converged is False:
        verdict = "HARD_FAIL"
    elif converged is True:
        verdict = "HARD_PASS"
    else:
        # Have ckpt + finite metrics but no converged signal (no val_loss_initial
        # in test_metrics); MIDDLE_BAND -- not a hard fail (ckpt usable),
        # surface for inspection.
        verdict = "MIDDLE_BAND"

    msg = (f"Phase 0.5 probe training: val_loss {val_loss_initial:.4f} -> "
           f"{val_loss_final:.4f}; test cos_sim={cos_sim_test:.4f} "
           f"binary_acc={binary_acc_test:.4f}; epochs={epochs}; "
           f"wall={elapsed:.1f}s. Verdict: {verdict}.")
    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": run_mode,
        "llm_model_id": LLM_MODEL_ID,
        "layer_frac": LAYER_FRAC,
        "vsa_dimension": VSA_DIMENSION,
        "epochs": epochs,
        "batch_size": batch_size,
        "k_clusters": K_CLUSTERS,
        "early_stop_patience": EARLY_STOP_PATIENCE,
        "learning_rate": LEARNING_RATE,
        "embedding_pipeline_version": EMBEDDING_PIPELINE_VERSION,
        "n_training_inputs": len(train_inputs),
        "n_concepts": len(all_concepts),
        "ckpt_path": str(ckpt_dest),
        "codebook_path": str(codebook_path),
        "training_metrics": test_metrics,
        "val_loss_initial": val_loss_initial,
        "val_loss_final": val_loss_final,
        "cos_sim_test": cos_sim_test,
        "binary_acc_test": binary_acc_test,
        "verdict": verdict,
        "elapsed_s": elapsed,
        "verdict_msg": msg,
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2),
                                            encoding="utf-8")
    print(f"[{ANCHOR_NAME}] verdict={verdict} elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {out_dir / 'metrics.json'}", flush=True)
    return 0 if verdict != "HARD_FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())
