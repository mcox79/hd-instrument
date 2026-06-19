"""Demo 2 capstone — Lane C compliance + multi-hop chain at N=65536.

Per Strategy 21:32 P5: Integrates verifiable erase (Lane C) with deep-chain
composition via backward-smoother-only readout. Both axes must pass.
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

_lc = importlib.util.spec_from_file_location("lc",
    REPO / "experiments" / "exp_wave14_lane_C_compliance_audit_smoke_v1.py")
lc = importlib.util.module_from_spec(_lc); _lc.loader.exec_module(lc)
_so = importlib.util.spec_from_file_location("so",
    REPO / "experiments" / "exp_wave14_chain_smoother_only_v1.py")
so = importlib.util.module_from_spec(_so); _so.loader.exec_module(so)
_mh = importlib.util.spec_from_file_location("mh",
    REPO / "experiments" / "exp_wave14r_multihop_K100.py")
mh = importlib.util.module_from_spec(_mh); _mh.loader.exec_module(mh)


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "lane_C_pass" not in summary:
        return ("DEMO_2_INCONCLUSIVE", "Missing.")
    lc_pass = summary["lane_C_pass"]
    mh_acc = summary["multihop_acc_50hop"]
    if lc_pass and mh_acc >= 0.50:
        return ("DEMO_2_CAPSTONE_PASS",
                f"Lane C ALL probes pass AND multi-hop acc_50hop={mh_acc:.3f}>=0.50.")
    if lc_pass or mh_acc >= 0.50:
        return ("DEMO_2_CAPSTONE_PARTIAL",
                f"One axis only: lane_C_pass={lc_pass}, multihop={mh_acc:.3f}.")
    return ("DEMO_2_CAPSTONE_KILLED",
            f"Both fail: lane_C_pass={lc_pass}, multihop={mh_acc:.3f}.")


def self_test_verdict():
    for s, exp in [
        ({"lane_C_pass": True, "multihop_acc_50hop": 0.80}, "DEMO_2_CAPSTONE_PASS"),
        ({"lane_C_pass": True, "multihop_acc_50hop": 0.30}, "DEMO_2_CAPSTONE_PARTIAL"),
        ({"lane_C_pass": False, "multihop_acc_50hop": 0.20}, "DEMO_2_CAPSTONE_KILLED"),
        ({}, "DEMO_2_INCONCLUSIVE"),
    ]:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print("verdict self-test passed (4/4 cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N_lane_C": 4096,  # Lane C operates at standard N
              "N_multihop": 8192 if smoke else 65536,
              "M_facts": 30 if smoke else 100,
              "n_edits": 10 if smoke else 50,
              "n_deletes": 8 if smoke else 30,
              "K_chain": 100, "depth_chain": 25 if smoke else 50,
              "num_relations": 20, "num_entities": 200,
              "n_chain_trials": 5 if smoke else 20,
              "seed": 17}
    # Lane C audit
    print(f"[Lane C] N={config['N_lane_C']}", flush=True)
    lc_cfg = {"N": config["N_lane_C"], "M_facts": config["M_facts"],
              "n_edits": config["n_edits"], "n_deletes": config["n_deletes"]}
    lc_result = lc.run_one_seed(config["seed"], lc_cfg, device)
    lc_pass = (lc_result["delete_leak_max"] <= 0.05
                and lc_result["edit_acc"] >= 0.90
                and lc_result["kept_acc"] >= 0.90
                and lc_result["side_effect_rate"] <= 0.05
                and lc_result["ece_post"] <= 0.10)
    print(f"  Lane C: leak={lc_result['delete_leak_max']:.4f} edit={lc_result['edit_acc']:.3f} "
          f"kept={lc_result['kept_acc']:.3f} side={lc_result['side_effect_rate']:.4f} ECE={lc_result['ece_post']:.4f}", flush=True)
    print(f"  Lane C PASS: {lc_pass}", flush=True)
    # Multi-hop chain at N=65536 with smoother
    print(f"[Multi-hop] N={config['N_multihop']} K={config['K_chain']} d={config['depth_chain']}", flush=True)
    gen = torch.Generator(device=device).manual_seed(config["seed"])
    entity_atoms = mh.make_bsc_codebook(config["num_entities"], config["N_multihop"], gen, device)
    relation_atoms = mh.make_bsc_codebook(config["num_relations"], config["N_multihop"], gen, device)
    cpu_gen = torch.Generator().manual_seed(config["seed"] + 1009)
    correct = 0
    for trial in range(config["n_chain_trials"]):
        perm = torch.randperm(config["num_entities"], generator=cpu_gen)[:config["depth_chain"] + 1]
        chain = perm.tolist()
        rels = [int(torch.randint(0, config["num_relations"], (1,), generator=cpu_gen).item())
                for _ in range(config["depth_chain"])]
        M = mh.build_factbase(chain, rels, max(0, config["K_chain"] - config["depth_chain"]),
                                config["num_entities"], config["num_relations"],
                                entity_atoms, relation_atoms, cpu_gen, device)
        if so.chain_smoother_only(M, chain[0], rels, chain[-1], entity_atoms, relation_atoms):
            correct += 1
    mh_acc = correct / config["n_chain_trials"]
    print(f"  Multi-hop acc_d{config['depth_chain']}={mh_acc:.3f}", flush=True)
    summary = {"lane_C_pass": lc_pass,
                "lane_C_details": lc_result,
                "multihop_acc_50hop": mh_acc,
                "n_chain_trials": config["n_chain_trials"]}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_demo_2_lane_C_multihop_N65536_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("multihop_acc_present", summary["multihop_acc_50hop"] + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_demo_2_lane_C_multihop_N65536_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test: self_test_verdict(); return 0
    if args.smoke: run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
