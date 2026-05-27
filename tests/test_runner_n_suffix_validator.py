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
