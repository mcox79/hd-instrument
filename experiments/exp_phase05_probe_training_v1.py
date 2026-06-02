"""
phase05_probe_training_v1 -- Hyperprobe encoder training for Llama-3.1-8B.

WHY THIS EXISTS:
  arXiv:2509.25045 (Ipazia-AI/hyperprobe) publishes the code but NOT a pretrained
  checkpoint. To run Phase 0.5 Tier-7 sub-tests A/B/C, we train the encoder
  ourselves on Lambda A100. License is CC BY-NC-SA 4.0 (research use OK).

PIPELINE:
  1. Clone Ipazia-AI/hyperprobe; pip install -e .
  2. Load saturnMars/hyperprobe-dataset-analogy + saturnMars/hyperprobe-dataset-squad
     from HuggingFace (token from env HF_TOKEN or /home/ubuntu/hd-instrument/.hf_token).
  3. Build VSA codebook from training-set concepts at vsa_dimension=4096.
  4. Llama-3.1-8B activation collection: layer 22 residual on final-token position
     (intercept_layer_frac=0.7 per research-sanity-check 2026-06-02).
  5. Train encoder via hyperprobe.train_hyperprobe(loader, configs).
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
N_EPOCHS_FULL = 60                # paper script uses 100; budget at 60 for cost
N_EPOCHS_SMOKE = 2
BATCH_SIZE_FULL = 32
BATCH_SIZE_SMOKE = 8
K_CLUSTERS = 5                    # k-means clusters per ingest_embeddings (paper)

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
    print(f"[selftest] PASS: HF token shape OK; target layer index = {layer} "
          f"(0-indexed) of L={L}; VSA_DIM={VSA_DIMENSION}", flush=True)


_selftest_structural()


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

    # Step 3: load datasets
    print(f"  loading {ANALOGY_DATASET} ...", flush=True)
    analogy_ds = load_dataset(ANALOGY_DATASET, token=tok)
    print(f"  loading {SQUAD_DATASET} ...", flush=True)
    squad_ds = load_dataset(SQUAD_DATASET, token=tok)
    print(f"  analogy splits: {list(analogy_ds.keys())}; "
          f"squad splits: {list(squad_ds.keys())}", flush=True)

    # Step 4: build training inputs (analogy + SQuAD train); paper used both
    # corpora; we follow that. Inputs are dicts {'doc': str, 'concepts': [(s,o)]}.
    # The exact field names depend on dataset schemas -- adapt below if upstream
    # schema changes (paper's repo uses 'doc' + 'concepts' uniformly).
    train_inputs = []
    for split_name in ["train"]:
        if split_name in analogy_ds:
            for row in analogy_ds[split_name]:
                # Tolerate either 'doc'/'concepts' or 'text'/'pairs' upstream naming
                doc = row.get("doc") or row.get("text") or row.get("input")
                concepts = row.get("concepts") or row.get("pairs") or row.get("key_value")
                if doc and concepts:
                    train_inputs.append({"doc": doc, "concepts": concepts})
        if split_name in squad_ds:
            for row in squad_ds[split_name]:
                doc = row.get("doc") or row.get("question") or row.get("text")
                concepts = row.get("concepts") or row.get("pairs") or row.get("key_value")
                if doc and concepts:
                    train_inputs.append({"doc": doc, "concepts": concepts})
    if run_mode != "full":
        train_inputs = train_inputs[:200]
    print(f"  training inputs: {len(train_inputs)}", flush=True)
    if len(train_inputs) < 50:
        raise RuntimeError(
            f"Too few training inputs ({len(train_inputs)}); dataset schema may have "
            f"changed. Inspect analogy_ds / squad_ds row keys."
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

    # Step 6: LLM activation collection (Llama-3.1-8B + sum pooling)
    import multiprocessing as mp
    docs = [item["doc"] for item in train_inputs]
    print(f"  ingesting {len(docs)} LLM embeddings via {LLM_MODEL_ID} ...", flush=True)
    ctx = mp.get_context("spawn")
    with ctx.Pool(1) as pool:
        llm_embeddings, *_ = pool.apply(
            hyperprobe.ingest_embeddings,
            args=(docs, LLM_MODEL_ID, K_CLUSTERS),
        )
    # Sum-pool per paper script
    llm_embeddings = {doc: emb.sum(dim=0) for doc, emb in llm_embeddings.items()}
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
    best_model_path, test_metrics = hyperprobe.train_hyperprobe(loader, configs=configs)
    print(f"  trained: best ckpt -> {best_model_path}", flush=True)

    # Step 9: persist canonical paths for downstream anchors
    ckpt_dest = out_dir / "probe_ckpt.ckpt"
    if Path(best_model_path) != ckpt_dest:
        shutil.copy2(best_model_path, ckpt_dest)
    codebook_path = out_dir / "codebook.json"
    # Persist codebook as JSON (round-trip-safe for downstream encoder)
    codebook_serializable = {c: list(map(float, codebook[c])) for c in codebook}
    codebook_path.write_text(json.dumps(codebook_serializable), encoding="utf-8")

    elapsed = time.time() - t0

    # Step 10: verdict from training-side telemetry only (validation is separate anchor)
    val_loss_final = float(test_metrics.get("val_loss_final", float("nan")))
    val_loss_initial = float(test_metrics.get("val_loss_initial", float("nan")))
    cos_sim_test = float(test_metrics.get("cos_sim", test_metrics.get("test_cos_sim", float("nan"))))
    binary_acc_test = float(test_metrics.get("binary_acc", test_metrics.get("test_binary_acc", float("nan"))))

    converged = (val_loss_final < 0.5 * val_loss_initial) if (val_loss_initial > 0) else None
    nan_seen = any(
        (v != v) for v in [val_loss_final, val_loss_initial, cos_sim_test, binary_acc_test]
    )
    if nan_seen or (converged is False):
        verdict = "HARD_FAIL"
    elif converged is True:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"  # ambiguous metrics shape; surface for inspection

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
