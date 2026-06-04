"""cornerstone C1: read probe_validation metrics, apply cornerstone HP=0.85 gate.

ROUTING: testbed/cornerstone batch on Lambda H100. C1 reuses the existing
phase05 probe_training_v1 + probe_validation_v1 pipeline (Algorithm 1 Hyperprobe
MLP training + held-out cos_sim measurement). This post-processor reads the
validation metrics and re-emits them with cornerstone's HP/MID/HF bands so the
batch verdict has a uniform per-cell schema.

CAPABILITY QUESTION (per routing_cornerstone_audit_c1_c2_c3_llama_8b_frontier):
  Does substrate's Hyperprobe encoder replicate the arXiv:2509.25045 paper
  baseline val_sim at Llama-3.1-8B frontier scale?

PRE-REGISTERED BANDS (cornerstone-specific; differ from phase05 validation gate):
  HARD-PASS: val_sim (= cos_sim_mean) >= 0.85 (paper reports 0.89 at 8B).
  MIDDLE:    val_sim in [0.70, 0.85].
  HARD-FAIL: val_sim < 0.70 (substrate algorithm does not replicate at frontier).

This is a POST-PROCESSOR; it does NOT train. Run AFTER probe_validation_v1.

ASCII-only stdout. No em-dash. PROT-018: no _nN suffix (LLM-native D=4096).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

import json
import os
import time
import traceback
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402

ANCHOR_NAME = "substrate_hyperprobe_llama_3_1_8b_val_sim_replication_v1_h100"

PROBE_VAL_REL = "data/exp_phase05_probe_validation_v1/metrics.json"

HP_VAL_SIM = 0.85
MID_LO = 0.70
PAPER_TARGET_VAL_SIM = 0.89


def _classify(val_sim: float) -> str:
    if val_sim != val_sim:
        return "UNKNOWN"
    if val_sim >= HP_VAL_SIM:
        return "HARD_PASS"
    if val_sim >= MID_LO:
        return "MIDDLE_BAND"
    return "HARD_FAIL"


def _verdict_msg(verdict: str, val_sim: float, binary_acc: float,
                 probe_val_verdict: str) -> str:
    base = (f"C1 cornerstone (Hyperprobe replication at Llama-3.1-8B): "
            f"val_sim (cos_sim) = {val_sim:.4f}, binary_acc = {binary_acc:.4f}; "
            f"upstream probe_validation verdict = {probe_val_verdict}; "
            f"cornerstone HP gate >= {HP_VAL_SIM:.2f} (paper target {PAPER_TARGET_VAL_SIM:.2f}). ")
    if verdict == "HARD_PASS":
        cap = ("Substrate Hyperprobe encoder REPLICATES the paper val_sim at "
               "frontier 8B scale; Algorithm 1 (k-means k=5 over layers 16-32 + "
               "sum-pool) is faithful at production model size. Tier 1 audit "
               "primitive C1 is empirically anchored at 8B.")
    elif verdict == "MIDDLE_BAND":
        cap = ("Partial replication: encoder learns the analogy structure but "
               "falls short of paper-grade. Either training schedule needs more "
               "epochs / better LR OR Algorithm 1 has scale-specific drift; "
               "diagnostic next step is val_sim trajectory vs epoch count.")
    elif verdict == "HARD_FAIL":
        cap = ("Substrate Hyperprobe FAILS to replicate at 8B frontier scale; "
               "either Algorithm 1 ports do not generalize or training was "
               "configured wrong. Tier 1 product narrative needs reassessment "
               "for the encoder-replication claim.")
    else:
        cap = ("Could not parse upstream probe_validation metrics; verdict UNKNOWN.")
    return base + cap


def main() -> int:
    t0 = time.monotonic()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "startup.log"

    def log(msg: str) -> None:
        line = f"[{time.monotonic() - t0:7.2f}s] {msg}"
        print(line, flush=True)
        try:
            with open(log_path, "a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        except Exception:
            pass

    log(f"C1 post-processor START anchor={ANCHOR_NAME}")
    log(f"reading probe_validation metrics from {PROBE_VAL_REL}")

    val_path = REPO / PROBE_VAL_REL
    if not val_path.exists():
        log(f"FAILED_SETUP: probe_validation metrics not found at {val_path}")
        metrics = {
            "anchor": ANCHOR_NAME,
            "verdict": "FAILED_SETUP",
            "verdict_msg": (f"C1 post-processor could not find upstream "
                            f"probe_validation metrics at {PROBE_VAL_REL}; "
                            f"phase05_probe_validation_v1 did not write its "
                            f"output (likely upstream failure)."),
            "elapsed_s": time.monotonic() - t0,
            "summary": "probe_validation metrics absent",
        }
        write_metrics(out_dir, metrics)
        return 0

    try:
        raw = json.loads(val_path.read_text(encoding="utf-8"))
    except Exception as e:
        log(f"FAILED_SETUP: probe_validation metrics could not be parsed: {e}")
        metrics = {
            "anchor": ANCHOR_NAME,
            "verdict": "FAILED_SETUP",
            "verdict_msg": (f"C1 post-processor could not parse upstream "
                            f"probe_validation metrics at {PROBE_VAL_REL}: {e}"),
            "elapsed_s": time.monotonic() - t0,
            "summary": "probe_validation metrics unparseable",
            "exception": traceback.format_exc(),
        }
        write_metrics(out_dir, metrics)
        return 0

    val_sim = float(raw.get("cos_sim_mean", float("nan")))
    binary_acc = float(raw.get("binary_acc_mean", float("nan")))
    probe_val_verdict = str(raw.get("verdict", "UNKNOWN"))

    verdict = _classify(val_sim)
    msg = _verdict_msg(verdict, val_sim, binary_acc, probe_val_verdict)

    log(f"val_sim = {val_sim:.6f}  binary_acc = {binary_acc:.6f}")
    log(f"cornerstone verdict = {verdict}")
    log(f"verdict_msg = {msg}")

    metrics = {
        "anchor": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": time.monotonic() - t0,
        "summary": {
            "val_sim": val_sim,
            "binary_acc": binary_acc,
            "hp_threshold": HP_VAL_SIM,
            "mid_threshold": MID_LO,
            "paper_target_val_sim": PAPER_TARGET_VAL_SIM,
            "upstream_probe_validation_verdict": probe_val_verdict,
            "upstream_metrics_path": PROBE_VAL_REL,
        },
        "cell": "C1",
        "cornerstone_batch": "cornerstone_c1_c2_c3_llama_3_1_8b_h100",
    }
    write_metrics(out_dir, metrics)
    log(f"wrote metrics.json -> {out_dir}/metrics.json")
    log(f"C1 post-processor DONE in {time.monotonic() - t0:.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
