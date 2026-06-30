"""substrate_anchor4_encoder_family_phase_diagram_v4 sibling seed=13.

v4 fix for META_RULE_AY enforcement + encoder-specific code paths VERIFIED
distinct at pre-flight gate caught by Skunkworks landed-VET 2026-06-30 on
v3 (MM_PARTIAL_DISCRIMINATION: dense triplet binary_bipolar/hrr_real/fhrr
remained bit-identical; only sparse_bipolar + sparse_real wired -> 2/5 distinct).

v4 changes (per spec notes/director_anchor4_encoder_v4_design_spec_2026-06-30.md):
  - Pre-flight encoder distinctness gate at cell entry (SHA-256 bind output)
  - META_RULE_AY verdict-emitter auto-demotes HARD_PASS on distinctness False
  - Regime: N_DIMS=[2048,4096,8192], LOADS=[2.0,4.0,8.0,12.0], DECAYS=[30,60,180]
  - NOISE_SIGMA=0.1 noise floor to prevent saturation
  - Encoder bind ops VERIFIED distinct: elementwise / FFT / complex-mul / sparse
  - Smoke at full-N range (discriminator-must-survive-scale)

Cardinality (per seed):
  FULL : 5 enc * 3 decay * 4 load * 3 N_DIM = 180 phase points
  SMOKE: 5 enc * 2 decay * 3 load * 3 N_DIM = 90 phase points

CHUNKED architecture (USER 2026-06-28): one seed per sibling file.
Sibling pair: seed_7, seed_19.

PRE-REG: preregs/2026-06-30_substrate_anchor4_encoder_family_phase_diagram_v4.md
CARDINALITY_OK_FULL: 180 phase points per seed
CARDINALITY_OK_SMOKE: 90 phase points per seed

PROT-018: anchor has no _n suffix (sweep is along N_DIM internally).
PROT-020: `import torch` present; routed to overnight_queue (GPU runner).

4 defensive patterns (USER 2026-06-28 hardening):
  1. start_marker: STARTED metrics written before any heavy work
  2. crash-diag: outer try -> import-crash sentinel with full traceback
  3. per-unit checkpoint: write_partial_key per seed via _seed_checkpoint
  4. heartbeat: per-phase-point flush print

ASCII-only. No unicode. No em-dashes. No emojis.

Author: exp_dev 2026-06-30 (Opus 4.7 1M, agent-spawn)
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import torch  # PROT-020 GPU-queue routing gate

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

SEED = 13
ANCHOR_NAME = f"substrate_anchor4_encoder_family_phase_diagram_v4_seed_{SEED}"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _NAME_SAYS_SMOKE)
            else ("selftest" if _ARGS.self_test
                  else os.environ.get("HDLAB_RUN_MODE", "full").lower()))
SELF_TEST_MODE = bool(_ARGS.self_test)
SMOKE_MODE = (RUN_MODE == "smoke")

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},"
    f"encoders=[binary_bipolar,hrr_real,fhrr,sparse_bipolar,sparse_real],"
    f"N_DIM_sweep_full=[2048,4096,8192],N_DIM_sweep_smoke=[2048,4096,8192],"
    f"R_BUCKETS=128,n_atoms=1500,n_days=365,"
    f"decay_full=[30,60,180],load_full=[8.0,12.0,16.0,24.0],"
    f"decay_smoke=[30,180],load_smoke=[8.0,16.0,24.0],"
    f"bundled_memory=M_atoms_per_chunk,"
    f"NOISE_SIGMA=0.1,SEED={SEED},mode={RUN_MODE},"
    f"arms=[TIME_DECAY,RANDOM],"
    f"expected_n_full=180,expected_n_smoke=90,"
    f"discriminator=per_encoder_pareto_dominance_v4_AY_preflight_gate,"
    f"HP_min_pairs_differ=5_of_10,HP_readout_floor=0.30,"
    f"META_AY_HARD_FAIL_FRAC=0.50,META_AY_MM_DEMOTE_FRAC=0.10,"
    f"hardening=L1startmarker+L2crashdiag+L3perunitckpt+L4heartbeat+CHUNKED_PER_SEED"
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}
_LLM_CALL_COUNTER = [0]


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        m = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 2),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v4_anchor4_encoder_family_phase_diagram_chunked",
        }
        if extra:
            m.update(extra)
        tmp = out_dir / "metrics.json.tmp"
        final = out_dir / "metrics.json"
        tmp.write_text(json.dumps(m, indent=2, default=str), encoding="utf-8")
        os.replace(tmp, final)
    except Exception as e:
        print(f"[_write_minimal_metrics] FAIL: {e}", file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        s = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": f"IMPORT_CRASH: {type(exc).__name__}: {exc}",
            "summary": f"IMPORT_CRASH: {type(exc).__name__}: {exc}",
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v4_anchor4_encoder_family_import_crash",
        }
        tmp = out_dir / "metrics.json.tmp"
        final = out_dir / "metrics.json"
        tmp.write_text(json.dumps(s, indent=2), encoding="utf-8")
        os.replace(tmp, final)
        (out_dir / "import_crash.json").write_text(
            json.dumps(s, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[_write_import_crash_sentinel] FAIL: {e}",
              file=sys.stderr, flush=True)


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(
        out_dir, "STARTED",
        f"STARTED: pid={os.getpid()} mode={RUN_MODE} seed={SEED}",
        extra={"_phase": "init"},
    )

    from experiments._substrate_anchor4_encoder_family_phase_diagram_v4_core import (
        run_one_seed_phase_diagram, aggregate_and_verdict, selftest,
        get_backend_label, N_DIM_DEFAULT, _get_device,
    )

    strict_gpu = (RUN_MODE == "full")
    device = _get_device(strict_gpu=strict_gpu)
    backend = get_backend_label()
    print(f"[{ANCHOR_NAME}] mode={RUN_MODE} seed={SEED} backend={backend} "
          f"device={device}", flush=True)

    if SELF_TEST_MODE:
        try:
            ok, msg = selftest(SEED, device=device)
            verdict = "SELFTEST_OK" if ok else "SELFTEST_FAIL"
            _write_minimal_metrics(
                out_dir, verdict, msg,
                extra={"_phase": "selftest_done", "backend": backend},
            )
            print(f"[selftest] {verdict}: {msg}", flush=True)
            return 0 if ok else 1
        except Exception as e:
            _write_minimal_metrics(
                out_dir, "SELFTEST_FAIL", f"SELFTEST_FAIL: {e}",
                extra={"_traceback": traceback.format_exc()},
            )
            print(f"[selftest] FAIL: {e}", file=sys.stderr, flush=True)
            return 1

    seeds_list = [SEED]
    run_config = {"N": N_DIM_DEFAULT, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(seeds_list, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(seeds_list)} done; running {remaining}",
          flush=True)

    for seed in remaining:
        _write_minimal_metrics(
            out_dir, "RUNNING",
            f"RUNNING: seed={seed} mode={RUN_MODE}",
            extra={"_phase": "seed_running", "_current_seed": seed,
                   "backend": backend},
        )
        t0 = time.time()
        result = run_one_seed_phase_diagram(
            seed, run_mode=RUN_MODE, device=device,
        )
        result["N"] = N_DIM_DEFAULT
        result["anchor_name"] = ANCHOR_NAME
        result["config_version"] = CONFIG_VERSION
        write_partial_key(out_dir, seed, result)
        print(f"[seed={seed}] complete in {time.time()-t0:.1f}s "
              f"({result['observed_n_units']} pts)", flush=True)

    per_seed = aggregate_partials(out_dir, seeds_list, run_config=run_config)
    final = aggregate_and_verdict(per_seed, run_mode=RUN_MODE)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 2)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v4_anchor4_encoder_family_phase_diagram_chunked"
    final["backend"] = backend
    final["seed"] = SEED
    final["n_seeds"] = 1
    final["corpus_provenance"] = (
        "synthetic_substrate_5_encoder_family_anchor4_timedecay_v4_AY_preflight_gate"
    )
    final["n_llm_calls"] = _LLM_CALL_COUNTER[0]

    if _LLM_CALL_COUNTER[0] != 0:
        raise RuntimeError(
            f"LLM_CALL_GATE_BREACH: substrate-only required; "
            f"n_llm_calls={_LLM_CALL_COUNTER[0]}"
        )

    tmp = out_dir / "metrics.json.tmp"
    final_path = out_dir / "metrics.json"
    tmp.write_text(json.dumps(final, indent=2, default=str), encoding="utf-8")
    os.replace(tmp, final_path)
    print(f"[{ANCHOR_NAME}] DONE: {final['verdict_msg']}", flush=True)
    print(
        f"[{ANCHOR_NAME}] cardinality observed={final.get('observed_n_units')} "
        f"expected={final.get('expected_n_units')} "
        f"ok={final.get('cardinality_ok')}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_import_crash_sentinel(e)
        print(f"[main] OUTER_EXCEPTION: {e}", file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
