"""verification/test_scorecard_resolution.py -- pytest witness for the scorecard's expanded resolution
(owner 2026-09-15: "more resolution on which parts are performing well and which aren't; it's very hard to
understand what you're working on in context of that").

Builds the three new sections straight from data/exp_situation_model_qa_modern_v1_pri125a/metrics.json -- a
fixed on-disk example, independent of today's live BOARD_TREND.jsonl state, so this witness is deterministic
-- and checks: 7 product rows each carry a verdict, the coref row is NOT MEASURED with a reason, the 13-rung
reading chain each carries a brain-faithful status, the regenerated notes/SCORECARD.md carries the three new
section headings, and tools/scorecard_gui.py --parser-smoke prints PASS (a subprocess; the GUI window itself
is never opened here).

Run: .venv/Scripts/python.exe verification/test_scorecard_resolution.py   (also pytest-collectable)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO / "tools") not in sys.path:
    sys.path.insert(0, str(REPO / "tools"))
import scorecard as SC  # noqa: E402

METRICS = REPO / "data" / "exp_situation_model_qa_modern_v1_pri125a" / "metrics.json"


def _metrics() -> dict:
    return json.loads(METRICS.read_text(encoding="utf-8"))


def test_product_rows_seven_with_verdict() -> None:
    m = _metrics()
    rows = SC.build_product_rows(m, m.get("ts_iso"), [])
    assert len(rows) == 7, rows
    for r in rows:
        assert r.get("verdict"), r
        assert r.get("question"), r
    assert {r["key"] for r in rows} == set(SC.PRODUCT_DIMS)


def test_coref_row_not_measured_with_reason() -> None:
    m = _metrics()
    rows = SC.build_product_rows(m, m.get("ts_iso"), [])
    coref = next(r for r in rows if r["key"] == "coref")
    assert "NOT MEASURED" in coref["verdict"], coref
    assert coref.get("reason"), "the coref row must carry a reason it wasn't measured this run"


def test_chain_has_13_rungs_each_with_bf_status() -> None:
    rows = SC.build_chain_rows()
    assert len(rows) == 13, rows
    for r in rows:
        assert r.get("bf_status"), r
        assert r.get("name") and r.get("organ"), r
        assert r.get("health") in ("strong", "improving", "weak", "unmeasured"), r


def test_product_and_chain_degrade_gracefully_with_no_metrics() -> None:
    """An older/failed run with no reader-driven rows must still render, never crash."""
    rows = SC.build_product_rows(None, None, [])
    assert len(rows) == 7
    assert all("NOT MEASURED" in r["verdict"] for r in rows)
    assert SC.build_chain_rows()  # never touches metrics.json; must still build


def test_scorecard_md_carries_the_three_headings() -> None:
    sc = SC.build()
    SC.write_outputs(sc)
    txt = (REPO / "notes" / "SCORECARD.md").read_text(encoding="utf-8")
    for heading in ("### THE PRODUCT, QUESTION BY QUESTION", "### THE READING CHAIN, RUNG BY RUNG",
                    "### WHAT STRATEGY IS DOING NOW"):
        assert heading in txt, heading


def test_gui_parser_smoke_passes() -> None:
    out = subprocess.run([sys.executable, str(REPO / "tools" / "scorecard_gui.py"), "--parser-smoke"],
                          cwd=str(REPO), capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stdout + out.stderr
    assert "PASS" in out.stdout, out.stdout + out.stderr


def main() -> int:
    test_product_rows_seven_with_verdict()
    test_coref_row_not_measured_with_reason()
    test_chain_has_13_rungs_each_with_bf_status()
    test_product_and_chain_degrade_gracefully_with_no_metrics()
    test_scorecard_md_carries_the_three_headings()
    test_gui_parser_smoke_passes()
    print("[test_scorecard_resolution] PASS: 7 product rows verdicted, coref NOT MEASURED with a reason, "
          "13 chain rungs with a BF status, graceful with no metrics, 3 headings in notes/SCORECARD.md, "
          "GUI --parser-smoke PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
