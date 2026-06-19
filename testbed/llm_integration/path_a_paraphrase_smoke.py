"""PP-8 Round 4 cell 10: Path A paraphrase smoke (no-training; substrate-only).

Per strategy_response_to_testbed_pp8_v1b_lr_fix_plus_path_a_10cell_authorized:
- Write 50 queries via Phi-3-derived keys (sign(R @ phi3_hidden(sentence_a)))
- Retrieve with 50 paraphrase pairs from MRPC benchmark
- Measure cache hit rate at cosine thresholds {0.80, 0.85, 0.90}

Pre-reg:
- HARD-PASS: paraphrase hit rate >= 60% at threshold 0.85 AND stability across
  all 3 thresholds (no inverted ordering)
- MIDDLE: 35-60% (partial; threshold-sensitive)
- HARD-FAIL: < 35% (semantic structure NOT inherited by substrate codewords)

This is a NO-TRAINING test: substrate stores 50 paraphrase-pair keys; we then
query with the OTHER paraphrase of each pair and measure cosine similarity
between query codeword and the originally-stored key codeword.

Run:
  python -m testbed.llm_integration.path_a_paraphrase_smoke \
    --out-dir data/testbed_pp8_week2/train_cell10_path_a \
    --n-pairs 50 --device cuda
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch

_REPO_ROOT = Path(__file__).parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


_N_SUBSTRATE = 4096
_D_MODEL = 3072
_PHI3_MODEL = "microsoft/Phi-3-mini-4k-instruct"


def _load_phi3_4bit(device: torch.device):
    """Load Phi-3-mini-4bit (no LoRA; pure inference)."""
    from transformers import (AutoModelForCausalLM, AutoTokenizer,
                              BitsAndBytesConfig)
    if device.type != "cuda":
        raise RuntimeError("Phi-3-mini-4bit requires CUDA (bitsandbytes).")
    bnb_cfg = BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16,
    )
    tokenizer = AutoTokenizer.from_pretrained(_PHI3_MODEL, trust_remote_code=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        _PHI3_MODEL, quantization_config=bnb_cfg, device_map={"": 0},
        trust_remote_code=False, attn_implementation="eager",
    )
    model.eval()
    return model, tokenizer


def _load_mrpc_pairs(n_pairs: int, seed: int = 7) -> list[tuple[str, str]]:
    """Load up to n_pairs paraphrase pairs (label=1) from MRPC train."""
    try:
        from datasets import load_dataset
        ds = load_dataset("glue", "mrpc", split="train")
    except Exception as exc:
        raise RuntimeError(
            f"datasets library load_dataset('glue', 'mrpc') failed: {exc}; "
            f"check 'pip install datasets'") from exc
    # Filter label==1 (positive paraphrase pairs)
    positives = [(r["sentence1"], r["sentence2"]) for r in ds if r["label"] == 1]
    import random
    random.Random(seed).shuffle(positives)
    return positives[:n_pairs]


def _phi3_hidden_at_last(model, tokenizer, text: str, device: torch.device):
    """Forward `text` through Phi-3; return last-position hidden state of last layer (d_model,)."""
    enc = tokenizer(text, return_tensors="pt", truncation=True,
                    max_length=128).to(device)
    with torch.no_grad():
        out = model(input_ids=enc.input_ids, output_hidden_states=True)
    return out.hidden_states[-1][0, -1, :].to(dtype=torch.float32)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="PP-8 Round 4 cell 10: Path A paraphrase smoke")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--n-pairs", type=int, default=50)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--projection-seed", type=int, default=23)
    parser.add_argument("--pair-seed", type=int, default=7)
    args = parser.parse_args()

    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = _REPO_ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[path_a] device={device}")
    print(f"[path_a] loading Phi-3-4bit...")
    model, tokenizer = _load_phi3_4bit(device)

    print(f"[path_a] loading MRPC paraphrase pairs (n={args.n_pairs})...")
    pairs = _load_mrpc_pairs(args.n_pairs, seed=args.pair_seed)
    print(f"[path_a] {len(pairs)} positive paraphrase pairs loaded")

    # Fixed Gaussian R for SimHash projection
    g = torch.Generator(device="cpu")
    g.manual_seed(args.projection_seed)
    R = torch.randn(_N_SUBSTRATE, _D_MODEL, generator=g,
                    dtype=torch.float32).to(device)
    print(f"[path_a] R projection matrix: {tuple(R.shape)}")

    # Compute SimHash codewords for both sentences in each pair
    print(f"[path_a] computing SimHash codewords for "
          f"{2 * len(pairs)} sentences...")
    written_keys = []  # codewords for sentence_a (the "stored" key)
    query_keys = []    # codewords for sentence_b (the "query")
    for i, (s_a, s_b) in enumerate(pairs):
        h_a = _phi3_hidden_at_last(model, tokenizer, s_a, device)
        h_b = _phi3_hidden_at_last(model, tokenizer, s_b, device)
        c_a = torch.sign(R @ h_a)  # (n_sub,) bipolar
        c_b = torch.sign(R @ h_b)
        c_a[c_a == 0] = 1.0
        c_b[c_b == 0] = 1.0
        written_keys.append(c_a)
        query_keys.append(c_b)
        if (i + 1) % 10 == 0:
            print(f"  [path_a] {i+1}/{len(pairs)} pairs encoded")
    written_stack = torch.stack(written_keys, dim=0)  # (N, n_sub)
    query_stack = torch.stack(query_keys, dim=0)      # (N, n_sub)

    # Compute pairwise similarity: query[i] vs every written key
    # Normalized cosine: bipolar / sqrt(n_sub); dot product over n_sub
    print(f"[path_a] computing pairwise cosine similarity...")
    sim = (query_stack @ written_stack.T) / float(_N_SUBSTRATE)  # (N, N) in [-1, 1]

    # For each query[i], we want the retrieved key to be written[i] (same pair index).
    # Cache hit rate at threshold t: fraction of queries where sim[i,i] >= t
    # AND sim[i,i] is the max over j (correct retrieval).
    n = len(pairs)
    diag_sims = torch.diag(sim).cpu().tolist()
    # For each row, is the diagonal the argmax?
    argmax_per_row = sim.argmax(dim=-1).cpu().tolist()
    argmax_correct = sum(1 for i, j in enumerate(argmax_per_row) if i == j)
    print(f"[path_a] diagonal cosine similarities (paraphrase pairs): "
          f"min={min(diag_sims):.4f} mean={sum(diag_sims)/n:.4f} "
          f"max={max(diag_sims):.4f}")
    print(f"[path_a] argmax-is-correct (paraphrase retrieved as nearest): "
          f"{argmax_correct}/{n} = {100*argmax_correct/n:.1f}%")

    # Hit rate at thresholds (both conditions: diag >= t AND diag == argmax)
    threshold_results = {}
    for t in [0.80, 0.85, 0.90]:
        hits = sum(1 for i in range(n)
                   if diag_sims[i] >= t and argmax_per_row[i] == i)
        threshold_results[t] = {
            "n_hits": hits,
            "hit_rate": hits / n,
            "threshold": t,
        }
        print(f"  threshold={t}: hits={hits}/{n} = {100*hits/n:.1f}%")

    # Pre-reg interpretation
    rate_85 = threshold_results[0.85]["hit_rate"]
    # Stability across thresholds = monotonic (higher t => lower hits)
    thresholds_sorted = sorted(threshold_results.values(), key=lambda r: r["threshold"])
    monotone = all(thresholds_sorted[i]["n_hits"] >= thresholds_sorted[i+1]["n_hits"]
                   for i in range(len(thresholds_sorted) - 1))
    if rate_85 >= 0.60 and monotone:
        verdict = "HARD-PASS (paraphrase hit rate >= 60% at threshold 0.85 + monotone across thresholds)"
    elif rate_85 >= 0.35:
        verdict = "MIDDLE-BAND (partial; threshold-sensitive)"
    else:
        verdict = "HARD-FAIL (semantic structure NOT inherited by substrate codewords)"

    summary = {
        "schema_version": 1,
        "verdict": verdict,
        "n_pairs": n,
        "diagonal_sim_min": round(min(diag_sims), 6),
        "diagonal_sim_mean": round(sum(diag_sims) / n, 6),
        "diagonal_sim_max": round(max(diag_sims), 6),
        "argmax_correct_n": argmax_correct,
        "argmax_correct_rate": round(argmax_correct / n, 6),
        "threshold_results": {f"{k:.2f}": v for k, v in threshold_results.items()},
        "monotone_across_thresholds": monotone,
        "config": {
            "n_substrate": _N_SUBSTRATE, "d_model": _D_MODEL,
            "phi3_model": _PHI3_MODEL,
            "projection_seed": args.projection_seed,
            "pair_seed": args.pair_seed,
        },
    }
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print()
    print(f"[path_a] verdict: {verdict}")
    print(f"[path_a] summary: {summary_path}")

    if "HARD-FAIL" in verdict:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
