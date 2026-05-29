"""Pytest tests for the LLM editing-benchmark scaffold.

These tests do NOT load any real dataset; they exercise the SCAFFOLD with
empty/synthetic inputs to confirm interfaces wire together. Phase-2 work
will add real-data integration tests once datasets/README.md downloads land.

Run with: python -m pytest experiments/llm_benchmarks/tests/test_harness.py -v

ASCII-only per CLAUDE.md.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.llm_benchmarks.edit_benchmark_harness import (  # noqa: E402
    EditTriple,
    CounterFactDataset,
    ZsREDataset,
    SequentialEditDataset,
    DEFAULT_METRICS,
    METHOD_REGISTRY,
    DATASET_REGISTRY,
    evaluate_edit,
    build_method,
    build_dataset,
    main,
)
from experiments.llm_benchmarks.methods.substrate import SubstrateEditMethod  # noqa: E402
from experiments.llm_benchmarks.methods.baselines import (  # noqa: E402
    ROMEMethod, MEMITMethod, AlphaEditMethod, MENDMethod,
)


# ----------------------------------------------------------------------------
# Substrate method: single edit + retrieve round-trip
# ----------------------------------------------------------------------------

def test_substrate_initialise_smoke():
    m = SubstrateEditMethod(config={"N": 64, "seed": 17})
    m.initialise()
    assert m._initialised is True
    assert m._codebook is not None
    assert m._W is not None
    assert m._W.shape == (64, 64)


def test_substrate_single_edit_and_retrieve():
    m = SubstrateEditMethod(config={"N": 64, "seed": 17})
    m.initialise()
    triple = EditTriple(
        subject="paris", relation="capital_of",
        target_new="france_v2",
        prompt="paris|||capital_of",
    )
    info = m.apply_edit(triple)
    assert info["first_write"] is True
    assert info["edit_norm"] > 0.0
    # The substrate's deterministic key-text mapping must retrieve the
    # value-row index assigned at write time. (Self-correlation argmax.)
    got = m.query(m._key_text(triple))
    assert got == str(info["value_idx"])


def test_substrate_second_edit_overwrites():
    m = SubstrateEditMethod(config={"N": 64, "seed": 17})
    m.initialise()
    triple_a = EditTriple(subject="x", relation="r", target_new="value_a")
    triple_b = EditTriple(subject="x", relation="r", target_new="value_b")
    info_a = m.apply_edit(triple_a)
    info_b = m.apply_edit(triple_b)
    assert info_a["first_write"] is True
    assert info_b["first_write"] is False
    # Latest write should win on retrieval (single-key, low-load regime).
    got = m.query(m._key_text(triple_b))
    assert got == str(info_b["value_idx"])


# ----------------------------------------------------------------------------
# Dataset stubs: empty load does not crash
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("cls", [CounterFactDataset, ZsREDataset, SequentialEditDataset])
def test_dataset_empty_load(cls):
    ds = cls(path=None)
    ds.load()
    assert ds._loaded is True
    assert list(ds) == []
    assert len(ds) == 0


def test_counterfact_loads_minimal_json():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "tiny_counterfact.json"
        body = [
            {
                "case_id": "c0",
                "requested_rewrite": {
                    "subject": "paris",
                    "prompt": "{} is located in",
                    "target_new": {"str": "Germany"},
                    "target_true": {"str": "France"},
                },
                "paraphrase_prompts": ["paris sits in", "paris is in"],
                "neighborhood_prompts": ["berlin is located in"],
            }
        ]
        p.write_text(json.dumps(body), encoding="utf-8")
        ds = CounterFactDataset(path=p, max_edits=10)
        ds.load()
        cases = list(ds)
        assert len(cases) == 1
        assert cases[0].subject == "paris"
        assert cases[0].target_new == "Germany"
        assert cases[0].target_true == "France"
        assert len(cases[0].paraphrase_prompts) == 2
        assert len(cases[0].neighborhood_prompts) == 1


# ----------------------------------------------------------------------------
# evaluate_edit: returns dict with requested metric keys
# ----------------------------------------------------------------------------

def test_evaluate_edit_returns_metric_keys_empty():
    m = SubstrateEditMethod(config={"N": 64, "seed": 17})
    m.initialise()
    ds = CounterFactDataset(path=None)
    result = evaluate_edit(m, ds, metrics=DEFAULT_METRICS)
    assert isinstance(result, dict)
    assert result["method"] == "substrate"
    assert result["dataset"] == "counterfact"
    assert result["n_cases"] == 0
    assert set(result["aggregate"].keys()) == set(DEFAULT_METRICS)
    assert result["metrics_requested"] == list(DEFAULT_METRICS)


def test_evaluate_edit_runs_on_one_case():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "tiny.json"
        body = [
            {
                "case_id": "c0",
                "requested_rewrite": {
                    "subject": "paris", "prompt": "p",
                    "target_new": {"str": "X"}, "target_true": {"str": "Y"},
                },
                "paraphrase_prompts": ["q1", "q2"],
                "neighborhood_prompts": ["n1"],
            }
        ]
        p.write_text(json.dumps(body), encoding="utf-8")
        m = SubstrateEditMethod(config={"N": 64, "seed": 17})
        m.initialise()
        ds = CounterFactDataset(path=p, max_edits=1)
        result = evaluate_edit(m, ds, metrics=["efficacy", "paraphrase", "specificity"])
        assert result["n_cases"] == 1
        assert result["successful_edits"] == 1
        per = result["per_case"][0]
        assert per["edit_ok"] is True
        assert "efficacy" in per["scores"]


# ----------------------------------------------------------------------------
# Baseline stubs raise NotImplementedError per scaffold contract
# ----------------------------------------------------------------------------

@pytest.mark.parametrize("cls", [ROMEMethod, MEMITMethod, AlphaEditMethod, MENDMethod])
def test_baseline_apply_edit_raises(cls):
    m = cls(config={"N": 4096, "seed": 17})
    m.initialise()
    triple = EditTriple(subject="x", relation="r", target_new="v")
    with pytest.raises(NotImplementedError):
        m.apply_edit(triple)


# ----------------------------------------------------------------------------
# Registry + builders
# ----------------------------------------------------------------------------

def test_method_registry_has_all_five():
    assert set(METHOD_REGISTRY.keys()) == {
        "substrate", "rome", "memit", "alphaedit", "mend"}


def test_dataset_registry_has_all_three():
    assert set(DATASET_REGISTRY.keys()) == {
        "counterfact", "zsre", "sequential"}


def test_build_method_substrate():
    m = build_method("substrate", N=64, seed=17)
    assert m.name == "substrate"
    assert m.config["N"] == 64


def test_build_method_rejects_unknown():
    with pytest.raises(ValueError):
        build_method("not_a_method", N=64, seed=17)


def test_build_dataset_rejects_unknown():
    with pytest.raises(ValueError):
        build_dataset("not_a_dataset", None, None)


# ----------------------------------------------------------------------------
# CLI argument parsing (via main --self-test)
# ----------------------------------------------------------------------------

def test_cli_self_test_substrate_counterfact():
    rc = main([
        "--method", "substrate",
        "--dataset", "counterfact",
        "--N", "64",
        "--seed", "17",
        "--self-test",
    ])
    assert rc == 0


def test_cli_rejects_unknown_method_at_parse():
    with pytest.raises(SystemExit):
        main(["--method", "nonsense", "--dataset", "counterfact",
              "--N", "64", "--seed", "17", "--self-test"])


def test_cli_rejects_unknown_dataset_at_parse():
    with pytest.raises(SystemExit):
        main(["--method", "substrate", "--dataset", "nonsense",
              "--N", "64", "--seed", "17", "--self-test"])
