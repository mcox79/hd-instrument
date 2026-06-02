"""
phase05_probe_validation_v1 -- Held-out validation of trained Hyperprobe encoder.

PRE-REGISTERED BANDS (per research sanity-check 2026-06-02 Addition 1, MANDATORY):
  HARD-PASS:  cos-sim >= 0.85  AND  binary_acc >= 0.90
              (within 0.04 of paper's published 0.89/0.94 on Llama-3.1-8B)
  HARD-FAIL:  cos-sim < 0.75  OR  binary_acc < 0.80
              -> STOP; do NOT run sub-tests A/B/C with this probe.
  MIDDLE:    in between (acceptable to proceed but downstream verdicts qualified).

EXIT CODE: 1 on HARD_FAIL so the Lambda batch launcher aborts the sequence
before the 4 main anchors run on a weak probe.

DESIGN:
  - Load probe checkpoint from prior anchor (phase05_probe_training_v1).
  - Load held-out validation set: 500 SQuAD test-split prompts NOT seen during
    training (paper's eval distribution).
  - For each prompt:
      r = Llama-3.1-8B residual at layer 22 final-token (sum-pooled per paper)
      vsa_pred = encoder(r)
      vsa_true = create_vsa_encodings(ground_truth_concepts)
      cos = cosine(vsa_pred, vsa_true)
      binary_acc = mean(sign(vsa_pred) == sign(vsa_true))
  - Aggregate cos_sim_mean, binary_acc_mean across 500 prompts.

THIS SCRIPT IS LAMBDA-ONLY (requires Llama-3.1-8B + GPU).
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import os
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "phase05_probe_validation_v1"

# Pre-reg bands (research sanity-check 2026-06-02 Addition 1)
HP_COS_SIM = 0.85
HP_BINARY_ACC = 0.90
HF_COS_SIM = 0.75
HF_BINARY_ACC = 0.80

# Paper's published numbers (for diagnostic context, not gating)
PAPER_COS_SIM = 0.89
PAPER_BINARY_ACC = 0.94

N_VAL_PROMPTS_FULL = 500
N_VAL_PROMPTS_SMOKE = 50

LLM_MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
LAYER_FRAC = 0.7
VSA_DIMENSION = 4096

# Training-anchor outputs we depend on
PROBE_CKPT_REL = "data/exp_phase05_probe_training_v1/probe_ckpt.ckpt"
CODEBOOK_REL = "data/exp_phase05_probe_training_v1/codebook.json"
ANALOGY_DATASET = "saturnMars/hyperprobe-dataset-analogy"


def _parse_analogy(doc):
    """'A:B=C:D' -> [(A,B),(C,D)] iff {A,B,C,D} are 4 distinct case-folded
    tokens. Mirrors filter in exp_phase05_probe_training_v1 (hyperprobe
    create_vsa_encodings shape-bug under overlap)."""
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
    all_toks = set(t.lower() for t in pairs[0] + pairs[1])
    if len(all_toks) != 4:
        return None
    return pairs


def _load_hf_token() -> str:
    tok = os.environ.get("HF_TOKEN", "").strip()
    if tok:
        return tok
    tok_path = REPO / ".hf_token"
    if tok_path.exists():
        return tok_path.read_text(encoding="utf-8").strip()
    raise RuntimeError(
        "HF token not found: set HF_TOKEN env var or place token at <repo>/.hf_token"
    )


def _selftest_structural():
    """Verify the dependency chain is encoded correctly without GPU."""
    L = 32
    layer = int(round(LAYER_FRAC * L)) - 1
    assert HP_COS_SIM > HF_COS_SIM > 0, "band ordering inverted"
    assert HP_BINARY_ACC > HF_BINARY_ACC > 0, "binary acc band ordering inverted"
    print(f"[selftest] PASS: bands HP cos>=0.85+acc>=0.90; HF cos<0.75 or acc<0.80; "
          f"target layer = {layer} (0-indexed)", flush=True)


_selftest_structural()


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-30 or nb < 1e-30:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _binary_acc(a: np.ndarray, b: np.ndarray) -> float:
    sa = np.sign(a); sa[sa == 0] = 1
    sb = np.sign(b); sb[sb == 0] = 1
    return float(np.mean(sa == sb))


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "smoke")
    n_val = N_VAL_PROMPTS_FULL if run_mode == "full" else N_VAL_PROMPTS_SMOKE

    print(f"[{ANCHOR_NAME}] run_mode={run_mode} n_val={n_val} "
          f"HP cos>=0.85 acc>=0.90; HF cos<0.75 OR acc<0.80; "
          f"paper target {PAPER_COS_SIM:.2f}/{PAPER_BINARY_ACC:.2f}", flush=True)

    # Dependency: probe checkpoint + codebook must exist (produced by prior anchor)
    ckpt_path = REPO / PROBE_CKPT_REL
    codebook_path = REPO / CODEBOOK_REL
    if not ckpt_path.exists():
        raise RuntimeError(
            f"Probe checkpoint not found at {ckpt_path}. Run "
            f"experiments/exp_phase05_probe_training_v1.py first."
        )
    if not codebook_path.exists():
        raise RuntimeError(f"Codebook not found at {codebook_path}.")

    tok = _load_hf_token()
    os.environ["HF_TOKEN"] = tok
    os.environ["HUGGINGFACE_HUB_TOKEN"] = tok

    try:
        import hyperprobe
        from datasets import load_dataset
        from huggingface_hub import login as hf_login
    except Exception as e:
        raise RuntimeError(
            f"hyperprobe/datasets import failed: {e}. Run on Lambda after bring-up."
        )
    hf_login(token=tok, add_to_git_credential=False)

    t0 = time.time()

    # Load codebook back (round-trip from JSON)
    cb_raw = json.loads(codebook_path.read_text(encoding="utf-8"))
    # Reconstruct codebook in hyperprobe's expected dict-of-arrays shape; if the
    # library expects DataFrame we'll need to adapt at integration time.
    codebook = {c: np.array(v, dtype=np.float32) for c, v in cb_raw.items()}
    print(f"  codebook loaded: {len(codebook)} concepts @ D={VSA_DIMENSION}", flush=True)

    # Load probe encoder from checkpoint
    encoder = hyperprobe.VSAEncoder.load_from_checkpoint(str(ckpt_path))
    encoder.eval()
    print(f"  encoder loaded from {ckpt_path}", flush=True)

    # Load LLM
    llm = hyperprobe.load_llm(model_name=LLM_MODEL_ID)
    print(f"  LLM loaded: {LLM_MODEL_ID}", flush=True)

    # Held-out validation set: analogy TEST split (114k rows, not seen during
    # training which uses TRAIN split). Same 'A : B = C : D' parser as training.
    analogy_ds = load_dataset(ANALOGY_DATASET, token=tok)
    if "test" in analogy_ds:
        held_out_raw = analogy_ds["test"]
    elif "validation" in analogy_ds:
        held_out_raw = analogy_ds["validation"]
    else:
        raise RuntimeError(f"No test/validation split in {ANALOGY_DATASET}; "
                           f"splits: {list(analogy_ds.keys())}")
    # Build parsed-items list of n_val
    held_out = []
    for row in held_out_raw:
        concepts = _parse_analogy(row["doc"])
        if concepts is None:
            continue
        held_out.append({"doc": row["doc"], "concepts": concepts})
        if len(held_out) >= n_val:
            break
    print(f"  validation prompts (parsed): {len(held_out)} / target {n_val}",
          flush=True)
    if len(held_out) < min(10, n_val):
        raise RuntimeError(
            f"Too few parsed validation prompts ({len(held_out)})."
        )

    cos_vals = []
    bin_accs = []
    import torch
    for i, item in enumerate(held_out):
        doc = item["doc"]
        concepts = item["concepts"]
        # Get LLM embedding (sum-pooled per paper)
        emb_dict, *_ = hyperprobe.ingest_embeddings(
            docs=[doc], model_name=LLM_MODEL_ID, k_clusters=1, llm=llm,
        )
        emb = emb_dict[doc].sum(dim=0)
        # Encoder forward
        with torch.no_grad():
            vsa_pred = encoder(emb.unsqueeze(0)).squeeze(0).cpu().numpy()
        # Ground-truth VSA encoding from concepts via codebook
        vsa_true_item = {"doc": doc, "concepts": concepts}
        vsa_true = hyperprobe.create_vsa_encodings(vsa_true_item, codebook, verbose=False)
        if hasattr(vsa_true, "numpy"):
            vsa_true = vsa_true.numpy()
        vsa_true = np.asarray(vsa_true, dtype=np.float32).flatten()
        cos_vals.append(_cosine(vsa_pred, vsa_true))
        bin_accs.append(_binary_acc(vsa_pred, vsa_true))
        if (i + 1) % 50 == 0:
            print(f"  progress: {i+1}/{len(held_out)} cos_mean={np.mean(cos_vals):.3f} "
                  f"acc_mean={np.mean(bin_accs):.3f}", flush=True)

    cos_mean = float(np.mean(cos_vals))
    cos_std = float(np.std(cos_vals, ddof=1)) if len(cos_vals) > 1 else 0.0
    acc_mean = float(np.mean(bin_accs))
    acc_std = float(np.std(bin_accs, ddof=1)) if len(bin_accs) > 1 else 0.0

    if cos_mean >= HP_COS_SIM and acc_mean >= HP_BINARY_ACC:
        verdict = "HARD_PASS"
    elif cos_mean < HF_COS_SIM or acc_mean < HF_BINARY_ACC:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    msg = (f"Phase 0.5 probe quality validation: cos_sim={cos_mean:.4f} +/- "
           f"{cos_std:.4f}; binary_acc={acc_mean:.4f} +/- {acc_std:.4f} "
           f"over {len(cos_vals)} held-out prompts. Paper target {PAPER_COS_SIM:.2f}/"
           f"{PAPER_BINARY_ACC:.2f}. HP gate cos>=0.85 AND acc>=0.90; "
           f"HF gate cos<0.75 OR acc<0.80. Verdict: {verdict}.")
    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": run_mode,
        "n_val_prompts_attempted": len(held_out),
        "n_val_prompts_used": len(cos_vals),
        "cos_sim_mean": cos_mean,
        "cos_sim_std": cos_std,
        "binary_acc_mean": acc_mean,
        "binary_acc_std": acc_std,
        "paper_target_cos_sim": PAPER_COS_SIM,
        "paper_target_binary_acc": PAPER_BINARY_ACC,
        "thresholds": {
            "HP_cos_sim": HP_COS_SIM, "HP_binary_acc": HP_BINARY_ACC,
            "HF_cos_sim": HF_COS_SIM, "HF_binary_acc": HF_BINARY_ACC,
        },
        "verdict": verdict,
        "elapsed_s": elapsed,
        "verdict_msg": msg,
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2),
                                            encoding="utf-8")
    print(f"[{ANCHOR_NAME}] verdict={verdict} elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] {msg}", flush=True)
    # Exit code: 1 on HARD_FAIL so launcher stops; 0 otherwise.
    return 0 if verdict != "HARD_FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())
