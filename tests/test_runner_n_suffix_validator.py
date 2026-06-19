"""Test PROT-018 runner-side N-suffix validator (runner_v2_prod.validate_n_suffix_binding).

Run with:  python -m pytest tests/test_runner_n_suffix_validator.py -v
       or:  python tests/test_runner_n_suffix_validator.py    (standalone)

ASCII-only per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "experiments"))

from runner_v2_prod import (  # type: ignore  # noqa: E402
    _extract_anchor_n,
    _extract_metrics_n,
    _validate_metrics_schema,
    validate_n_suffix_binding,
)


def _write_metrics(tmp: Path, body: dict) -> Path:
    p = tmp / "metrics.json"
    p.write_text(json.dumps(body), encoding="utf-8")
    return p


# ---------- _extract_anchor_n ----------

def test_anchor_n_suffix_basic():
    assert _extract_anchor_n("saad_solla_v9_n4096") == 4096
    assert _extract_anchor_n("bid_v2_n8192_5seed_FULL") == 8192


def test_anchor_n_suffix_absent():
    assert _extract_anchor_n("saad_solla_v3") is None
    assert _extract_anchor_n("plain_anchor") is None


def test_anchor_n_no_match_inside_words():
    # _next / _noise / _norm must not be confused with _n<digits>
    assert _extract_anchor_n("exp_next_step_v1") is None
    assert _extract_anchor_n("exp_noise_envelope_v3") is None
    assert _extract_anchor_n("exp_norm_layer_v2") is None


def test_anchor_n_version_suffix_is_not_n():
    # _v<N> is version, not N-binding
    assert _extract_anchor_n("saad_solla_v9") is None
    assert _extract_anchor_n("hatano_sasa_v3") is None


def test_anchor_n_multiple_suffixes_takes_first():
    # _n<N> repeated -> first match wins (re.search default; matches queue_add.py
    # behaviour, which uses the same re.search call). In practice anchors never
    # have two _n suffixes so this is a corner-case-only contract.
    assert _extract_anchor_n("foo_n512_bar_n8192") == 512


# ---------- _extract_metrics_n ----------

def test_metrics_n_from_summary():
    assert _extract_metrics_n({"summary": {"N": 4096}}) == 4096


def test_metrics_n_from_config():
    assert _extract_metrics_n({"config": {"N": 8192}}) == 8192


def test_metrics_n_from_detail():
    assert _extract_metrics_n({"detail": {"N": 2048}}) == 2048


def test_metrics_n_precedence_summary_first():
    # summary > config > detail when multiple present
    body = {
        "summary": {"N": 4096},
        "config": {"N": 1024},
        "detail": {"N": 512},
    }
    assert _extract_metrics_n(body) == 4096


def test_metrics_n_falls_back_to_n_run():
    body = {"config": {"N_run": 512, "N_production": 4096}}
    assert _extract_metrics_n(body) == 512


def test_metrics_n_missing():
    assert _extract_metrics_n({"verdict": "PASS"}) is None
    assert _extract_metrics_n({}) is None
    assert _extract_metrics_n(None) is None


def test_metrics_n_ignores_bool():
    # True/False must not be interpreted as N=1/0
    assert _extract_metrics_n({"summary": {"N": True}}) is None


# ---------- validate_n_suffix_binding ----------

def test_validator_pass_match():
    with tempfile.TemporaryDirectory() as td:
        p = _write_metrics(Path(td), {"summary": {"N": 4096}})
        assert validate_n_suffix_binding("saad_solla_v9_n4096", p) is None


def test_validator_fail_smoke_leaked_into_full_run():
    """The exact 78-times-fired case: anchor _n4096 but metrics N=512."""
    with tempfile.TemporaryDirectory() as td:
        p = _write_metrics(Path(td), {
            "summary": {"N": 512},
            "config": {"mode": "SMOKE", "N": 512},
        })
        err = validate_n_suffix_binding("saad_solla_v9_n4096", p)
        assert err is not None, "validator must REJECT _n4096 anchor with metrics N=512"
        assert "n_mismatch" in err
        assert "4096" in err
        assert "512" in err
        assert "smoke" in err.lower()  # mode tag


def test_validator_fail_8192_smoke_512_case():
    """Second high-recurrence case: bid_v2_n8192 ran at N=512."""
    with tempfile.TemporaryDirectory() as td:
        p = _write_metrics(Path(td), {
            "summary": {"N": 512},
            "config": {"mode": "smoke", "N": 512},
        })
        err = validate_n_suffix_binding("bid_v2_n8192_5seed_FULL", p)
        assert err is not None
        assert "8192" in err and "512" in err


def test_validator_noop_no_suffix():
    """Anchor with no _n<N> suffix -> rule does not apply, returns None."""
    with tempfile.TemporaryDirectory() as td:
        p = _write_metrics(Path(td), {"summary": {"N": 512}})
        assert validate_n_suffix_binding("saad_solla_v3", p) is None


def test_validator_noop_missing_metrics_file():
    """Missing metrics file -> schema validator handles it; we return None."""
    p = Path(tempfile.gettempdir()) / "definitely_does_not_exist.json"
    if p.exists():
        p.unlink()
    assert validate_n_suffix_binding("saad_solla_v9_n4096", p) is None


def test_validator_noop_no_n_in_metrics():
    """Some legitimate scripts (N-sweep) have no scalar N field. Do not reject."""
    with tempfile.TemporaryDirectory() as td:
        p = _write_metrics(Path(td), {
            "verdict": "PASS",
            "summary": {"N_sweep": [512, 1024, 2048, 4096]},
        })
        assert validate_n_suffix_binding("anchor_novel_phase_battery_v3_n8192", p) is None


def test_validator_noop_invalid_json():
    """Unreadable metrics -> schema validator handles it; we return None."""
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "metrics.json"
        p.write_text("not valid json {", encoding="utf-8")
        assert validate_n_suffix_binding("saad_solla_v9_n4096", p) is None


def test_validator_pass_with_n_run_field():
    """If a script writes only N_run (not N), validator must still pass on match."""
    with tempfile.TemporaryDirectory() as td:
        p = _write_metrics(Path(td), {"config": {"N_run": 4096, "mode": "FULL"}})
        assert validate_n_suffix_binding("saad_solla_v9_n4096", p) is None


# ---------- End-to-end runner refusal test (n-mismatch eradication 2026-05-27) ----------

def test_runner_refuses_mismatched_n_suffix_in_real_run():
    """Simulate the end-to-end runner-refusal contract.

    Constructs the exact post-run state the runner sees on disk:
      - anchor name = 'fake_test_n8192_v1' (carries _n8192 contract)
      - metrics.json present with summary.N=512 (smoke leak into FULL slot)
      - the script's argv would lack --N 8192 (or the script ran with N=512)

    Asserts:
      1. validate_n_suffix_binding returns a non-None error.
      2. The error message names BOTH the contracted N (8192) and the
         actual recorded N (512), with 'n_mismatch' as the leading token,
         matching the exact contract documented in
         experiments/runner_v2_prod.py and the runner's mark_outcome
         error= field.

    This guards the runner-side refusal even if a future refactor
    accidentally silently passes the validator.
    """
    with tempfile.TemporaryDirectory() as td:
        # Stage the metrics.json as a real smoke run would have written it.
        p = _write_metrics(Path(td), {
            "verdict": "HARD_PASS",
            "verdict_msg": "smoke 1-seed pass",
            "elapsed_s": 12.3,
            "summary": {"N": 512},
            "config": {"mode": "smoke", "N": 512},
        })
        err = validate_n_suffix_binding("fake_test_n8192_v1", p)
        # Contract 1: refusal must fire (non-None).
        assert err is not None, (
            "Runner validator FAILED to refuse a mismatched anchor: "
            "'fake_test_n8192_v1' with metrics N=512 must be rejected."
        )
        # Contract 2: error message must lead with 'n_mismatch'.
        assert err.startswith("n_mismatch:"), (
            f"Refusal error must lead with 'n_mismatch:' for downstream "
            f"orchestrator error= parsing; got: {err!r}"
        )
        # Contract 3: error must name BOTH numerical Ns.
        assert "8192" in err, f"refusal error missing contracted N=8192: {err!r}"
        assert "512" in err, f"refusal error missing recorded N=512: {err!r}"
        # Contract 4: must surface the PROT-018 reference.
        assert "PROT-018" in err, (
            f"refusal error must cite PROT-018 (the protocol it enforces); "
            f"got: {err!r}"
        )


# ---------- PROT-019 timeout floor (n-mismatch eradication 2026-05-27) ----------

def _import_queue_add():
    """Lazy import for the PROT-019 checker so this test file stays standalone."""
    sys.path.insert(0, str(REPO / "tools"))
    import importlib
    import queue_add as qa
    importlib.reload(qa)
    return qa


def test_prot019_passes_large_n_with_sufficient_timeout():
    """_n8192 anchor with timeout=5400s -- ABOVE floor -- must pass."""
    qa = _import_queue_add()
    # No exception, no SystemExit, no return value.
    qa.check_timeout_floor("tcft_n8192_v6", 5400)


def test_prot019_passes_at_exactly_the_floor():
    """_n8192 anchor with timeout=3600s -- AT floor -- must pass."""
    qa = _import_queue_add()
    qa.check_timeout_floor("tcft_n8192_v6", 3600)


def test_prot019_passes_small_n_with_short_timeout():
    """_n1024 anchor with timeout=600s -- below floor but small N -- must pass.

    PROT-019 only applies to N >= PROT019_LARGE_N_MIN (4096).
    """
    qa = _import_queue_add()
    qa.check_timeout_floor("small_v1_n1024", 600)


def test_prot019_passes_no_suffix_with_short_timeout():
    """anchor with no _n<N> suffix -- timeout floor does not apply."""
    qa = _import_queue_add()
    qa.check_timeout_floor("no_n_suffix_v1", 600)


def test_prot019_rejects_n8192_under_3600s():
    """The exact 83rd-catch case: tcft_n8192_v5 with --timeout 1800 must REJECT."""
    qa = _import_queue_add()
    try:
        qa.check_timeout_floor("tcft_n8192_v5", 1800)
    except SystemExit as e:
        assert e.code == 7, f"PROT-019 must exit 7 on violation; got exit {e.code}"
        return
    raise AssertionError(
        "check_timeout_floor must SystemExit(7) on _n8192 + timeout<3600s"
    )


def test_prot019_rejects_n4096_under_3600s():
    """N=4096 is the floor of large-N classification per PROT019_LARGE_N_MIN."""
    qa = _import_queue_add()
    try:
        qa.check_timeout_floor("any_anchor_n4096", 3599)
    except SystemExit as e:
        assert e.code == 7, f"PROT-019 must exit 7; got {e.code}"
        return
    raise AssertionError("PROT-019 must reject _n4096 with timeout=3599s")


def test_prot019_rejects_n16384_under_3600s():
    """Forward-compatibility: arbitrarily large N still triggers the floor."""
    qa = _import_queue_add()
    try:
        qa.check_timeout_floor("future_anchor_n16384", 60)
    except SystemExit as e:
        assert e.code == 7
        return
    raise AssertionError("PROT-019 must reject _n16384 with timeout=60s")


# ---------- _validate_metrics_schema (DISPATCH_FAILURE_MISCLASSIFICATION fix) ----------
#
# Background: runner_v2_prod historically required ("verdict", "verdict_msg",
# "elapsed_s", "summary") as a hard schema gate. This caused 30+ false-failed
# verdicts on legitimate HARD_PASS runs whose scripts either (a) emit
# `verdict_tag` instead of `verdict` (KF/PB/MoE families) or (b) omit `summary`
# and use `cells` / `all_cells` / `config` instead (T1, anchor_battery, bid,
# kf1_hallu_rescue, kf2_cross_codebook, pb2_corr_len, moe_capacity_v2, etc.).
# The verdict_handler reactively caught these via remote metrics re-read, but
# each catch wastes Opus cycle time and inflates the LABEL-VS-HONEST counter.
# Fix: require only verdict_msg + elapsed_s + a verdict label that can be EITHER
# `verdict` or `verdict_tag`. `summary` is no longer required.


def _staged_metrics(td: str, body: dict) -> Path:
    p = Path(td) / "metrics.json"
    p.write_text(json.dumps(body), encoding="utf-8")
    return p


def test_schema_accepts_verdict_tag_alias():
    """KF2/PB2/MoE families emit `verdict_tag` not `verdict`. Must pass gate."""
    with tempfile.TemporaryDirectory() as td:
        p = _staged_metrics(td, {
            "mode": "smoke",
            "N": 1024,
            "cells": [{"M": 512, "isolation_ratio": 0.01}] * 9,
            "elapsed_s": 3.62,
            "verdict_tag": "KF2_CROSS_HARD_PASS",
            "verdict_msg": "EDIT ISOLATION CODEBOOK-ROBUST: isolation holds across 3 families",
        })
        assert _validate_metrics_schema(p) is None, (
            "verdict_tag must satisfy verdict-label requirement; this is the "
            "exact KF2/PB2/MoE family false-failed signature."
        )


def test_schema_accepts_missing_summary():
    """T1/anchor_battery/bid/kf1 families omit `summary` and use `cells` instead."""
    with tempfile.TemporaryDirectory() as td:
        p = _staged_metrics(td, {
            "anchor": "t1_beta_fine_v2_n4096",
            "N": 1024,
            "cells": [{"seed": 17, "beta_c_est": 10.0, "max_gradient": 0.314}],
            "verdict": "T1_FINE_MIDDLE_BAND",
            "verdict_msg": "DIFFUSE_OR_PARTIAL: gradient=0.314",
            "elapsed_s": 0.34,
        })
        assert _validate_metrics_schema(p) is None, (
            "missing `summary` must NOT fail the gate; the runner does not read "
            "it and 30+ HARD_PASS runs were false-failed by this requirement."
        )


def test_schema_accepts_kf2_actual_payload():
    """End-to-end reproducer of one of the 10 user-cited misclassified runs."""
    with tempfile.TemporaryDirectory() as td:
        p = _staged_metrics(td, {
            "mode": "smoke",
            "N": 1024,
            "m_fracs": [0.5, 1.0, 2.0],
            "seeds": [17],
            "codebook_families": ["kerdock", "bsc", "gaussian"],
            "elapsed_s": 3.62,
            "cells": [],
            "verdict_tag": "KF2_CROSS_HARD_PASS",
            "verdict_msg": "EDIT ISOLATION CODEBOOK-ROBUST",
        })
        # exit=0 + this payload MUST tag completed (validator returns None).
        assert _validate_metrics_schema(p) is None


def test_schema_accepts_moe_capacity_actual_payload():
    """End-to-end reproducer of moe_capacity_v2_n4096 (375s substantive run)."""
    with tempfile.TemporaryDirectory() as td:
        p = _staged_metrics(td, {
            "anchor": "moe_capacity_v2_n4096",
            "N": 1024,
            "K_sweep": [32, 64],
            "M_budget": 400,
            "seeds": [17],
            "cells": [{"K": 32, "seed": 17, "mean_ret": 0.953}],
            "verdict": "MOE_V2_HARD_PASS",
            "verdict_msg": "HIGH_K_SCALING: k64_mean=0.953 >= 0.5",
            "elapsed_s": 114.28,
        })
        assert _validate_metrics_schema(p) is None


# Padding key to push test payloads above the 100-byte METRICS_MIN_BYTES floor
# (which is enforced BEFORE the field-level schema checks).
_PAD = "_padding_to_clear_min_bytes_" + "x" * 64


def test_schema_still_rejects_missing_verdict_msg():
    """verdict_msg remains REQUIRED -- verdict_handler reads it for labelling."""
    with tempfile.TemporaryDirectory() as td:
        p = _staged_metrics(td, {
            "verdict": "PASS",
            "elapsed_s": 1.0,
            "summary": {"N": 1024},
            "pad": _PAD,
        })
        err = _validate_metrics_schema(p)
        assert err is not None, f"expected reject; got None"
        assert "verdict_msg" in err, f"expected verdict_msg in err; got: {err!r}"


def test_schema_still_rejects_missing_elapsed_s():
    """elapsed_s remains REQUIRED -- timeline reconciliation needs it."""
    with tempfile.TemporaryDirectory() as td:
        p = _staged_metrics(td, {
            "verdict": "PASS",
            "verdict_msg": "ok",
            "summary": {"N": 1024},
            "pad": _PAD,
        })
        err = _validate_metrics_schema(p)
        assert err is not None, f"expected reject; got None"
        assert "elapsed_s" in err, f"expected elapsed_s in err; got: {err!r}"


def test_schema_still_rejects_no_verdict_label_at_all():
    """If NEITHER verdict NOR verdict_tag is present, MUST reject."""
    with tempfile.TemporaryDirectory() as td:
        p = _staged_metrics(td, {
            "verdict_msg": "looks ok",
            "elapsed_s": 1.0,
            "summary": {"N": 1024},
            "pad": _PAD,
        })
        err = _validate_metrics_schema(p)
        assert err is not None, f"expected reject; got None"
        # empty_verdict OR no verdict label -> mention verdict in err
        assert "verdict" in err, f"expected verdict in err; got: {err!r}"


def test_schema_still_rejects_empty_verdict_string():
    """Empty-string verdict still rejected (and no verdict_tag fallback)."""
    with tempfile.TemporaryDirectory() as td:
        p = _staged_metrics(td, {
            "verdict": "",
            "verdict_msg": "ok",
            "elapsed_s": 1.0,
            "pad": _PAD,
        })
        err = _validate_metrics_schema(p)
        assert err is not None, f"expected reject; got None"
        assert err == "empty_verdict", f"got: {err!r}"


def test_schema_still_rejects_empty_verdict_msg():
    """Empty-string verdict_msg still rejected."""
    with tempfile.TemporaryDirectory() as td:
        p = _staged_metrics(td, {
            "verdict": "HARD_PASS",
            "verdict_msg": "",
            "elapsed_s": 1.0,
            "pad": _PAD,
        })
        err = _validate_metrics_schema(p)
        assert err is not None, f"expected reject; got None"
        assert err == "empty_verdict_msg", f"got: {err!r}"


def test_schema_still_rejects_missing_file():
    p = Path(tempfile.gettempdir()) / "nonexistent_metrics_xyz_test.json"
    if p.exists():
        p.unlink()
    err = _validate_metrics_schema(p)
    assert err == "missing"


def test_schema_still_rejects_invalid_json():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "metrics.json"
        p.write_text("not json {" + "x" * 200, encoding="utf-8")
        err = _validate_metrics_schema(p)
        assert err is not None
        assert err.startswith("invalid_json")


def test_schema_still_rejects_too_small():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "metrics.json"
        p.write_text("{}", encoding="utf-8")  # only 2 bytes; min is 100
        err = _validate_metrics_schema(p)
        assert err is not None
        assert err.startswith("too_small")


# ---------- Standalone runner ----------

if __name__ == "__main__":
    import inspect
    mod = sys.modules[__name__]
    funcs = [
        (name, fn) for name, fn in inspect.getmembers(mod, inspect.isfunction)
        if name.startswith("test_")
    ]
    n_pass = 0
    n_fail = 0
    for name, fn in funcs:
        try:
            fn()
            print(f"PASS  {name}")
            n_pass += 1
        except AssertionError as e:
            print(f"FAIL  {name}: {e}")
            n_fail += 1
        except Exception as e:
            print(f"ERROR {name}: {type(e).__name__}: {e}")
            n_fail += 1
    print()
    print(f"Summary: {n_pass} passed, {n_fail} failed (of {len(funcs)} total)")
    sys.exit(0 if n_fail == 0 else 1)
