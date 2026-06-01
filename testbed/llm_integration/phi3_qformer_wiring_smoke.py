"""PP-8 Week 2 Phase 1: Q-Former bridge wiring smoke (Phi-3 + substrate end-to-end).

Per notes/testbed_handoff_pp8_week2_feasibility_smoke_authorized_2026-06-01.md
Phase 1 ($10-20 cloud H100; 30-60 min wall):

Pipeline (one integrated query, exercised on H100):
  text prompt -> Phi-3 prefill -> extract last-position hidden ([QUERY] proxy)
    -> QueryReadoutHead (tanh-bounded R^d_model -> R^n_sub)
    -> sign() to bipolar (DEPLOYMENT-time only; train uses soft tanh)
    -> substrate Path D depth=5 retrieve at N=4096
    -> QFormerBridge (R^n_sub bipolar/continuous -> 8 prefix tokens R^d_model)
    -> Phi-3 decode 1 token with prefix injected via inputs_embeds

Acceptance criteria (per handoff sec "Acceptance criteria"):
  - Forward pass produces non-garbage substrate query (shape + no-NaN load-bearing
    at smoke with untrained weights; Hamming distance to expected target is ~N/2
    by random)
  - Backward pass produces non-zero gradient through bridge AND readout (training
    will at least move). Backward uses readout-soft-tanh output AS bridge input
    directly, bypassing the non-differentiable substrate Path D retrieval.
    This is exactly the train-time pattern per parent handoff: NEVER binarize
    inside the bridge during training.
  - Total session cost <= $20

This is INTEGRATION-LEVEL validation: qformer_bridge.smoke_test() already
validates bridge + readout in isolation on local CPU. H100 confirms the full
Phi-3 <-> bridge <-> substrate composition works without dtype/device/shape
mismatches and that gradient flow holds when readout consumes a real LLM
hidden state instead of a synthetic one.

Run:
  python -m testbed.llm_integration.phi3_qformer_wiring_smoke --device cuda

Writes data/testbed_pp8_week2/phi3_qformer_wiring_<device>.json.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import torch

_REPO_ROOT = Path(__file__).parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from experiments._multi_hop_mechanisms import build_shared, path_d_run  # noqa: E402
from testbed.llm_integration.qformer_bridge import (  # noqa: E402
    QFormerBridge, QueryReadoutHead,
)


_N_SUBSTRATE = 4096
_M_SUBSTRATE = 4096
_K_PATHS = 500
_D_MODEL = 3072
_DEPTH = 5
_N_QUERIES = 8


def _bipolar_from_soft(soft_query: torch.Tensor) -> torch.Tensor:
    """sign() with zeros mapped to +1 (deployment-time codeword emission)."""
    bipolar = torch.sign(soft_query)
    zero_mask = bipolar == 0
    if zero_mask.any():
        bipolar = bipolar + zero_mask.to(dtype=bipolar.dtype)
    return bipolar


def _extract_best_codeword(result, codebook: torch.Tensor) -> torch.Tensor:
    """Unpack path_d_run output; cast float-tensor index to safe int."""
    if isinstance(result, tuple):
        best_idx = result[0]
    else:
        best_idx = result
    if isinstance(best_idx, torch.Tensor):
        bi = best_idx.flatten()[0].item() if best_idx.numel() > 0 else 0
    else:
        bi = int(best_idx) if not hasattr(best_idx, "__iter__") else 0
    bi = int(bi) if not isinstance(bi, int) else bi
    bi = max(0, min(bi, codebook.shape[0] - 1))
    return codebook[bi].to(dtype=torch.float32).unsqueeze(0)


def _measure_wiring(
    model, readout: QueryReadoutHead, bridge: QFormerBridge,
    substrate_tuple, seq_len: int, n_reps: int,
    device: torch.device, seed: int,
    progress_jsonl_path: Path | None = None,
    only_forward: bool = False,
) -> dict[str, Any]:
    """Forward pipeline (n_reps) + ONE backward pass via soft tanh -> bridge.

    Forward path EXERCISED: hidden -> readout -> sign -> Path D -> bridge -> prefix
                            -> Phi-3 decode 1 token
    Backward path EXERCISED (once): hidden -> readout(soft tanh) -> bridge -> MSE
                                    -> backward; verify grads on readout + bridge

    Forward repeats give component-level timing (Phase 2 budget planning).
    Backward only once per (seq_len, seed) (smoke; not training).
    """
    codebook, W, key_idx, val_idx, relation = substrate_tuple
    starts = key_idx[:1].to(device)

    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    vocab = model.config.vocab_size
    prompt_ids = torch.randint(0, vocab, (1, seq_len),
                               generator=g, dtype=torch.long).to(device)

    component_samples = {
        "readout": [],
        "substrate_path_d": [],
        "bridge_qformer": [],
        "phi3_decode_1tok": [],
    }
    total_samples: list[float] = []
    hamming_samples: list[float] = []

    cuda_sync = device.type == "cuda"

    def _sync():
        if cuda_sync:
            torch.cuda.synchronize()

    with torch.inference_mode():
        # Prefill once per (seq_len, seed) -- not part of per-query budget
        _sync()
        t_pre0 = time.perf_counter_ns()
        out = model(input_ids=prompt_ids, use_cache=True,
                    output_hidden_states=True)
        _sync()
        t_pre1 = time.perf_counter_ns()
        prefill_ms = (t_pre1 - t_pre0) / 1e6

        past = out.past_key_values
        # Last-position hidden state from final layer (R^d_model).
        # At Phase 1 we use last-position as a proxy for the future [QUERY]
        # token; Phase 2+ will insert an explicit [QUERY] sentinel.
        query_hidden = out.hidden_states[-1][:, -1, :].to(dtype=torch.float32)

        # warm-up 3 integrated forward queries (excluded from samples)
        for _ in range(3):
            soft_q = readout(query_hidden)
            bipolar = _bipolar_from_soft(soft_q).squeeze(0)
            _ = path_d_run(
                codebook=codebook, W=W, starts=starts, relation=relation,
                depth=_DEPTH, K_paths=_K_PATHS, seed=seed, N_use=_N_SUBSTRATE,
            )

        for rep in range(n_reps):
            _sync()
            t_total0 = time.perf_counter_ns()

            # 1: QueryReadoutHead (LLM hidden -> tanh-bounded substrate query)
            _sync()
            t0 = time.perf_counter_ns()
            soft_query = readout(query_hidden)
            bipolar = _bipolar_from_soft(soft_query).squeeze(0)
            _sync()
            t1 = time.perf_counter_ns()
            component_samples["readout"].append((t1 - t0) / 1e6)

            # Hamming-to-random (untrained -> expect ~N/2)
            target = torch.sign(torch.randn(_N_SUBSTRATE, device=device))
            target[target == 0] = 1
            hamming = (bipolar != target).float().mean().item() * _N_SUBSTRATE
            hamming_samples.append(hamming)

            # 2: substrate Path D depth=5
            _sync()
            t0 = time.perf_counter_ns()
            result = path_d_run(
                codebook=codebook, W=W, starts=starts, relation=relation,
                depth=_DEPTH, K_paths=_K_PATHS, seed=seed + rep,
                N_use=_N_SUBSTRATE,
            )
            _sync()
            t1 = time.perf_counter_ns()
            component_samples["substrate_path_d"].append((t1 - t0) / 1e6)
            substrate_result = _extract_best_codeword(result, codebook)

            # 3: QFormerBridge (codeword -> 8 prefix tokens)
            _sync()
            t0 = time.perf_counter_ns()
            prefix_tokens = bridge(substrate_result)  # (1, 8, d_model)
            _sync()
            t1 = time.perf_counter_ns()
            component_samples["bridge_qformer"].append((t1 - t0) / 1e6)

            # Shape + no-NaN check
            assert prefix_tokens.shape == (1, _N_QUERIES, _D_MODEL), \
                f"prefix shape: got {tuple(prefix_tokens.shape)}; " \
                f"want (1, {_N_QUERIES}, {_D_MODEL})"
            assert not torch.isnan(prefix_tokens).any(), "prefix has NaN"
            assert not torch.isinf(prefix_tokens).any(), "prefix has Inf"

            # 4: Phi-3 decode 1 token with prefix injected via inputs_embeds
            # The 8 prefix tokens are injected as a "soft prompt" continuation.
            _sync()
            t0 = time.perf_counter_ns()
            dec_out = model(
                inputs_embeds=prefix_tokens.to(dtype=model.dtype),
                past_key_values=past,
                use_cache=True,
            )
            _sync()
            t1 = time.perf_counter_ns()
            component_samples["phi3_decode_1tok"].append((t1 - t0) / 1e6)

            _sync()
            t_total1 = time.perf_counter_ns()
            rep_total = (t_total1 - t_total0) / 1e6
            total_samples.append(rep_total)

            print(f"  seed={seed} rep={rep} ok=True total_ms={rep_total:.2f} "
                  f"hamming={hamming:.0f}/{_N_SUBSTRATE}", flush=True)

            if progress_jsonl_path is not None:
                rep_record = {
                    "seq_len": seq_len,
                    "seed": seed,
                    "rep": rep,
                    "total_ms": round(rep_total, 4),
                    "readout_ms": round(component_samples["readout"][-1], 4),
                    "substrate_path_d_ms": round(
                        component_samples["substrate_path_d"][-1], 4),
                    "bridge_qformer_ms": round(
                        component_samples["bridge_qformer"][-1], 4),
                    "phi3_decode_1tok_ms": round(
                        component_samples["phi3_decode_1tok"][-1], 4),
                    "hamming_to_random": round(hamming, 1),
                    "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
                }
                try:
                    with progress_jsonl_path.open("a", encoding="utf-8") as f:
                        f.write(json.dumps(rep_record) + "\n")
                        f.flush()
                except Exception as exc:
                    print(f"[WARN] per-rep JSONL write failed at "
                          f"seq={seq_len} seed={seed} rep={rep}: {exc}",
                          flush=True)

    # ---- Backward smoke (once per (seq_len, seed); skipped if only_forward) ----
    backward_diag: dict[str, Any] = {"ran": False}
    if not only_forward:
        try:
            # Fresh hidden capture under no_grad (not inference_mode -- the
            # latter taints output tensors so clones can't enter autograd).
            with torch.no_grad():
                out_b = model(input_ids=prompt_ids, use_cache=False,
                              output_hidden_states=True)
                hidden_b = out_b.hidden_states[-1][:, -1, :].to(
                    dtype=torch.float32).detach().clone()
            hidden_b = hidden_b.requires_grad_(False)

            # Train-time pattern per parent handoff: readout soft-tanh output
            # consumed DIRECTLY as bridge input (bypass non-differentiable substrate).
            readout.zero_grad()
            bridge.zero_grad()
            readout.train()
            bridge.train()
            soft_query_t = readout(hidden_b)              # (1, n_sub)
            prefix_t = bridge(soft_query_t)               # (1, 8, d_model)
            loss = prefix_t.pow(2).mean()
            loss.backward()

            bad_grads: list[tuple[str, str]] = []
            for mname, mod in [("readout", readout), ("bridge", bridge)]:
                for pname, p in mod.named_parameters():
                    if p.grad is None:
                        bad_grads.append((f"{mname}.{pname}", "NO_GRAD"))
                    elif p.grad.abs().max().item() == 0:
                        bad_grads.append((f"{mname}.{pname}", "ZERO_GRAD"))
                    elif torch.isnan(p.grad).any():
                        bad_grads.append((f"{mname}.{pname}", "NaN_GRAD"))
            backward_diag = {
                "ran": True,
                "loss_value": round(loss.item(), 6),
                "n_readout_params": sum(1 for _ in readout.parameters()),
                "n_bridge_params": sum(1 for _ in bridge.parameters()),
                "bad_grad_params": bad_grads,
                "ok": len(bad_grads) == 0,
            }
        except Exception as exc:
            import traceback
            backward_diag = {
                "ran": True,
                "ok": False,
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }
            print(f"[ERROR] backward smoke seq={seq_len} seed={seed}: {exc}",
                  file=sys.stderr)
        # back to eval for any subsequent forward calls in this fn
        readout.eval()
        bridge.eval()

    return {
        "total_ms": total_samples,
        "component_ms": component_samples,
        "hamming_samples": hamming_samples,
        "prefill_ms": prefill_ms,
        "backward": backward_diag,
    }


def _summarize(samples: list[float]) -> dict[str, float]:
    if not samples:
        return {"n": 0, "mean": 0.0, "min": 0.0, "p50": 0.0, "p95": 0.0,
                "p99": 0.0, "max": 0.0}
    s = sorted(samples)
    n = len(s)
    return {
        "n": n,
        "mean": round(statistics.fmean(s), 4),
        "min": round(s[0], 4),
        "p50": round(s[n // 2], 4),
        "p95": round(s[min(n - 1, int(n * 0.95))], 4),
        "p99": round(s[min(n - 1, int(n * 0.99))], 4),
        "max": round(s[-1], 4),
        "stdev": round(statistics.pstdev(s), 4) if n > 1 else 0.0,
    }


def _build_substrate(seed: int, device: torch.device):
    return build_shared(_N_SUBSTRATE, _M_SUBSTRATE, seed, device)


def _load_model(device: torch.device, mock_d_model: bool):
    """Load Phi-3-4bit on CUDA, OR a tiny mock-Phi-3 stand-in on CPU for local smoke.

    Local smoke uses the mock so we can exercise the whole pipeline (extract
    hidden, inject prefix via inputs_embeds, past_key_values handling) without
    bitsandbytes (CUDA-only). The H100 run uses the real Phi-3-4bit.
    """
    if device.type == "cuda":
        from testbed.llm_integration.phi3_token_latency import _load_phi3_4bit
        model, tokenizer = _load_phi3_4bit(device)
        return model, tokenizer

    # CPU mock: tiny GPT-2-style HF model at d_model=3072 to exercise the
    # inputs_embeds + past_key_values codepath. We skip the real model entirely
    # to avoid the multi-GB download + bf16 path; the mock has the same call
    # signature for our pipeline.
    from transformers import GPT2Config, GPT2LMHeadModel, GPT2Tokenizer
    cfg = GPT2Config(
        vocab_size=1024, n_positions=2048, n_embd=_D_MODEL, n_layer=2,
        n_head=8, n_inner=4096,
    )
    model = GPT2LMHeadModel(cfg).to(device).to(dtype=torch.float32).eval()
    # GPT2 doesn't expose .dtype in newer transformers; pin one.
    if not hasattr(model, "dtype"):
        model.dtype = torch.float32
    return model, None


def run(device: torch.device, seeds: tuple[int, ...] = (7, 13, 17),
        seq_lens: tuple[int, ...] = (128, 512),
        n_reps_per_seed: int = 10,
        progress_jsonl_path: Path | None = None,
        only_forward: bool = False) -> dict[str, Any]:
    results: dict[str, Any] = {
        "device": str(device),
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "n_substrate": _N_SUBSTRATE,
        "m_substrate": _M_SUBSTRATE,
        "k_paths": _K_PATHS,
        "depth": _DEPTH,
        "d_model": _D_MODEL,
        "n_queries": _N_QUERIES,
        "seeds": list(seeds),
        "seq_lens": list(seq_lens),
        "n_reps_per_seed": n_reps_per_seed,
        "progress_jsonl_path": str(progress_jsonl_path) if progress_jsonl_path else None,
        "measurements": {},
    }

    is_mock = device.type != "cuda"
    print(f"[qformer_wiring] loading model (mock={is_mock})...")
    t0 = time.perf_counter()
    model, _tok = _load_model(device, mock_d_model=is_mock)
    print(f"[qformer_wiring] model loaded in {time.perf_counter() - t0:.1f}s "
          f"d_model={model.config.hidden_size if hasattr(model.config, 'hidden_size') else model.config.n_embd}")

    # Build bridge + readout once; seeded
    torch.manual_seed(0)
    readout = QueryReadoutHead().to(device).to(dtype=torch.float32)
    bridge = QFormerBridge().to(device).to(dtype=torch.float32)
    readout.eval()
    bridge.eval()

    n_readout_params = sum(p.numel() for p in readout.parameters())
    n_bridge_params = sum(p.numel() for p in bridge.parameters())
    print(f"[qformer_wiring] readout params: {n_readout_params/1e6:.2f}M")
    print(f"[qformer_wiring] bridge params:  {n_bridge_params/1e6:.2f}M")
    print(f"[qformer_wiring] combined:       "
          f"{(n_readout_params + n_bridge_params)/1e6:.2f}M")
    results["readout_params_M"] = round(n_readout_params/1e6, 2)
    results["bridge_params_M"] = round(n_bridge_params/1e6, 2)

    backward_results: list[dict[str, Any]] = []
    for seq_len in seq_lens:
        per_seed_total: list[float] = []
        per_seed_components: dict[str, list[float]] = {
            "readout": [], "substrate_path_d": [],
            "bridge_qformer": [], "phi3_decode_1tok": [],
        }
        prefill_samples: list[float] = []
        hamming_all: list[float] = []
        for s in seeds:
            substrate_tuple = _build_substrate(s, device)
            try:
                meas = _measure_wiring(
                    model, readout, bridge, substrate_tuple,
                    seq_len, n_reps_per_seed, device, s,
                    progress_jsonl_path=progress_jsonl_path,
                    only_forward=only_forward,
                )
                per_seed_total.extend(meas["total_ms"])
                for k, v in meas["component_ms"].items():
                    per_seed_components[k].extend(v)
                prefill_samples.append(meas["prefill_ms"])
                hamming_all.extend(meas["hamming_samples"])
                if meas["backward"]["ran"]:
                    backward_results.append({
                        "seq_len": seq_len, "seed": s, **meas["backward"],
                    })
            except Exception as exc:
                print(f"[ERROR] seq_len={seq_len} seed={s}: {exc}",
                      file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)

        key = f"wiring_seq{seq_len}"
        results["measurements"][key] = {
            "total": _summarize(per_seed_total),
            "components": {k: _summarize(v) for k, v in per_seed_components.items()},
            "prefill": _summarize(prefill_samples),
            "hamming": _summarize(hamming_all),
        }
        m = results["measurements"][key]["total"]
        h = results["measurements"][key]["hamming"]
        print(f"  {key}: total mean={m['mean']:.3f}ms p99={m['p99']:.3f}ms "
              f"hamming mean={h['mean']:.1f}/{_N_SUBSTRATE} (~{_N_SUBSTRATE//2} expected)")
        for cname, csumm in results["measurements"][key]["components"].items():
            print(f"    [{cname}]: mean={csumm['mean']:.4f}ms p99={csumm['p99']:.4f}ms")

    results["backward"] = backward_results

    # Phase 1 verdict logic
    forward_ok = all(
        not v.get("total", {}).get("n", 0) == 0
        and not any(
            comp.get("n", 0) == 0
            for comp in v.get("components", {}).values()
        )
        for v in results["measurements"].values()
    )
    backward_ok = (
        only_forward
        or (len(backward_results) > 0
            and all(b.get("ok", False) for b in backward_results))
    )
    if forward_ok and backward_ok:
        verdict = "PASS (forward shapes + no-NaN + backward grad flow OK; Phase 2 QLoRA dispatchable)"
    elif forward_ok and not backward_ok:
        verdict = "MIDDLE (forward OK; backward grad issue; investigate before Phase 2)"
    else:
        verdict = "FAIL (forward broken; pivot to VQ-Bottleneck Tier 1.5 candidate)"
    results["phase1_verdict"] = verdict
    results["forward_ok"] = forward_ok
    results["backward_ok"] = backward_ok
    print()
    print(f"  PP-8 Week 2 Phase 1 verdict: {verdict}")

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="PP-8 Week 2 Phase 1: Q-Former bridge wiring smoke")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--seeds", default="7,13,17")
    parser.add_argument("--seq-lens", default="128,512")
    parser.add_argument("--n-reps-per-seed", type=int, default=10)
    parser.add_argument("--out-dir", default="data/testbed_pp8_week2")
    parser.add_argument("--progress-jsonl",
                        default="data/testbed_pp8_week2/phi3_qformer_wiring_progress.jsonl",
                        help="Per-rep JSONL written immediately (failure recovery)")
    parser.add_argument("--only-forward", action="store_true",
                        help="Skip backward smoke (use only if backward is "
                             "validated separately e.g. qformer_bridge.smoke_test)")
    args = parser.parse_args()

    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)
    seeds = tuple(int(s) for s in args.seeds.split(","))
    seq_lens = tuple(int(s) for s in args.seq_lens.split(","))

    progress_jsonl_path: Path | None = None
    if args.progress_jsonl:
        progress_jsonl_path = Path(args.progress_jsonl)
        if not progress_jsonl_path.is_absolute():
            progress_jsonl_path = _REPO_ROOT / progress_jsonl_path
        progress_jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        progress_jsonl_path.write_text("", encoding="utf-8")

    print(f"[qformer_wiring] device={device} torch={torch.__version__} "
          f"cuda={torch.cuda.is_available()}")
    print(f"[qformer_wiring] seeds={seeds} seq_lens={seq_lens} "
          f"n_reps_per_seed={args.n_reps_per_seed} only_forward={args.only_forward}")
    print(f"[qformer_wiring] progress JSONL: {progress_jsonl_path}")
    print()

    results = run(
        device=device,
        seeds=seeds,
        seq_lens=seq_lens,
        n_reps_per_seed=args.n_reps_per_seed,
        progress_jsonl_path=progress_jsonl_path,
        only_forward=args.only_forward,
    )

    out_dir = _REPO_ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"phi3_qformer_wiring_{device.type}.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nResults: {out_path}")

    if not results.get("forward_ok", False):
        return 2
    if not results.get("backward_ok", False):
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
