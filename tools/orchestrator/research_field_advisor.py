#!/usr/bin/env python3
"""Research field advisor: surface high-value next-search candidates.

Read-only helper. Parses notes/research_meta_map_and_adjacencies_*.md
(via tools/dashboard/parsers.parse_research_map) and applies the
field-coverage heuristics documented in tools/orchestrator/agents/research.md.

Outputs three lists:
  1. Top-5 candidate searches ranked by yield-x-cost-x-adjacency
  2. Top-3 fields to probe for scope-expansion (drill count <= 2)
  3. Saturated-recent-field detector: any field with last 3 drills all
     low-yield (none / weak / TBD).

Usage:
    python tools/orchestrator/research_field_advisor.py            # text summary
    python tools/orchestrator/research_field_advisor.py --json     # machine-readable

Per [[feedback-no-papers-product-only]] / [[feedback-value-creation-not-competition]]
the helper consumes only project-internal data; no external API calls.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Locate repo root: this file lives at <repo>/tools/orchestrator/
_REPO_ROOT = Path(__file__).resolve().parents[2]
_DASHBOARD_DIR = _REPO_ROOT / "tools" / "dashboard"

# Ensure we can import the dashboard parser without polluting working dir
if str(_DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(_DASHBOARD_DIR))

try:
    from parsers import parse_research_map  # type: ignore
except Exception as exc:  # pragma: no cover - import surface
    parse_research_map = None  # type: ignore
    _IMPORT_ERR: Exception | None = exc
else:
    _IMPORT_ERR = None


# ---------------------------------------------------------------------------
# Heuristic thresholds (documented in agents/research.md)
# ---------------------------------------------------------------------------

# Tier-1: high-yield fruit-bearing fields worth deeper drilling
TIER1_YIELD_FLOOR = 60.0  # yield_pct > 60
TIER1_DRILL_CEILING = 10  # drill count < 10

# Tier-2: moderate-yield fields worth broadening
TIER2_YIELD_LO = 30.0
TIER2_YIELD_HI = 60.0
TIER2_DRILL_CEILING = 15

# Tier-3: low-yield; only drill on adjacency edge
TIER3_YIELD_CEILING = 25.0

# Scope-expansion: untouched / barely-touched fields
SCOPE_EXPANSION_DRILL_CEILING = 2  # count <= 2

# Saturation detector: last N drills in same field all low-yield
SATURATION_WINDOW = 3
LOW_YIELD_TIERS = {"none", "weak", "TBD"}

# Cost normalization (lower = cheaper)
_COST_KEYWORDS = [
    (r"sec|second", 0.0),
    (r"min", 0.5),
    (r"hr|hour", 1.0),
    (r"1 day|~1 day", 2.0),
    (r"2 day|~2 day", 3.0),
    (r"3 day|~3 day", 4.0),
]


def _parse_cost(cost: str) -> float:
    """Estimate cost weight from free-text cost cell. Lower = cheaper."""
    import re
    s = (cost or "").lower()
    score = 2.0  # default mid-tier
    matched = False
    for pat, val in _COST_KEYWORDS:
        if re.search(pat, s):
            score = min(score, val) if matched else val
            matched = True
    return score


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class FieldStats:
    field: str
    count: int
    yield_pct: float
    tiers: dict
    latest_date: str
    recent_yields: list[str] = field(default_factory=list)  # last N drill tiers

    @property
    def is_saturated(self) -> bool:
        if len(self.recent_yields) < SATURATION_WINDOW:
            return False
        return all(t in LOW_YIELD_TIERS for t in self.recent_yields[-SATURATION_WINDOW:])

    @property
    def tier(self) -> str:
        if self.yield_pct > TIER1_YIELD_FLOOR and self.count < TIER1_DRILL_CEILING:
            return "tier-1"
        if TIER2_YIELD_LO <= self.yield_pct <= TIER2_YIELD_HI and self.count < TIER2_DRILL_CEILING:
            return "tier-2"
        if self.yield_pct < TIER3_YIELD_CEILING:
            return "tier-3"
        return "tier-mid"


@dataclass
class Candidate:
    rank: float
    name: str
    code: str
    field: str
    anchor: str  # e.g. "A. Crooks FT (Cap 1 winner)"
    why: str
    cost: str
    tier: str  # tier-1 / tier-2 / tier-3
    yield_pct: float
    field_count: int

    def to_dict(self) -> dict:
        return {
            "rank": round(self.rank, 3),
            "name": self.name,
            "code": self.code,
            "field": self.field,
            "anchor": self.anchor,
            "why": self.why,
            "cost": self.cost,
            "tier": self.tier,
            "field_yield_pct": self.yield_pct,
            "field_drill_count": self.field_count,
        }


# ---------------------------------------------------------------------------
# Heuristic core
# ---------------------------------------------------------------------------


def _field_recent_yields(matrix: list[dict], field_name: str, k: int = SATURATION_WINDOW + 2) -> list[str]:
    """Return the last k yield tiers for a field, ordered oldest -> newest by matrix idx."""
    rows = [r for r in matrix if r.get("field") == field_name]
    rows.sort(key=lambda r: r.get("idx", 0))
    return [r.get("yield_tier", "TBD") for r in rows[-k:]]


def _build_field_stats(map_data: dict) -> dict[str, FieldStats]:
    out: dict[str, FieldStats] = {}
    matrix = map_data.get("matrix", [])
    for f in map_data.get("fields", []):
        name = f["field"]
        out[name] = FieldStats(
            field=name,
            count=f["count"],
            yield_pct=f["yield_pct"],
            tiers=f["tiers"],
            latest_date=f.get("latest_date", ""),
            recent_yields=_field_recent_yields(matrix, name),
        )
    return out


def _adjacency_index(map_data: dict) -> list[dict]:
    """Flatten adjacency clusters into a list of candidate neighbors with anchor metadata."""
    flat = []
    for cluster in map_data.get("adjacency", []):
        anchor = f"{cluster.get('anchor', '')}. {cluster.get('anchor_label', '')}"
        for n in cluster.get("neighbors", []):
            flat.append({
                "code": n.get("code", ""),
                "name": n.get("name", ""),
                "why": n.get("why", ""),
                "cost": n.get("cost", ""),
                "anchor": anchor,
            })
    return flat


def _tag_neighbor_field(neighbor_name: str) -> str:
    """Re-use the dashboard parser's field tagger to label a neighbor."""
    try:
        from parsers import _tag_field  # type: ignore
        return _tag_field(neighbor_name)
    except Exception:
        return "other"


def rank_candidates(map_data: dict, top_k: int = 5) -> list[Candidate]:
    """Top-K next-drill candidates ranked by heuristic.

    Score = yield_pct_weight + adjacency_bonus - cost_penalty - saturation_penalty.
    Tier-1 candidates (fruit-bearing + under-drilled) dominate; tier-3 only
    appears when it has explicit adjacency to a fruit-bearing field.
    """
    field_stats = _build_field_stats(map_data)
    candidates = _adjacency_index(map_data)
    out: list[Candidate] = []

    for c in candidates:
        # Determine which field this candidate belongs to.
        # The adjacency anchor encodes the parent fruit-bearing field; the
        # candidate's own field tag may differ.
        cand_field = _tag_neighbor_field(c["name"])
        anchor_field = _anchor_to_field(c["anchor"])
        host_field = cand_field if cand_field != "other" else anchor_field

        stats = field_stats.get(host_field)
        # Untouched field => scope-expansion eligible; baseline yield 30
        yield_pct = stats.yield_pct if stats else 30.0
        drill_count = stats.count if stats else 0

        # Tier classification based on the ANCHOR's field (the fruit-bearing parent)
        anchor_stats = field_stats.get(anchor_field)
        anchor_yield = anchor_stats.yield_pct if anchor_stats else 0.0
        anchor_count = anchor_stats.count if anchor_stats else 0

        if anchor_yield > TIER1_YIELD_FLOOR and anchor_count < TIER1_DRILL_CEILING:
            tier = "tier-1"
            tier_score = 5.0
        elif TIER2_YIELD_LO <= anchor_yield <= TIER2_YIELD_HI and anchor_count < TIER2_DRILL_CEILING:
            tier = "tier-2"
            tier_score = 3.0
        elif anchor_yield < TIER3_YIELD_CEILING:
            tier = "tier-3"
            tier_score = 1.0
        else:
            tier = "tier-mid"
            tier_score = 2.0

        cost_penalty = _parse_cost(c["cost"])

        # Saturation penalty: if the host field is saturated, dock the score.
        saturation_penalty = 2.5 if (stats and stats.is_saturated) else 0.0

        # Scope-expansion bonus: untouched / barely-touched fields earn a small lift.
        scope_bonus = 1.0 if drill_count <= SCOPE_EXPANSION_DRILL_CEILING else 0.0

        score = tier_score - cost_penalty - saturation_penalty + scope_bonus

        out.append(Candidate(
            rank=score,
            name=c["name"],
            code=c["code"],
            field=host_field,
            anchor=c["anchor"],
            why=c["why"],
            cost=c["cost"],
            tier=tier,
            yield_pct=anchor_yield,
            field_count=anchor_count,
        ))

    out.sort(key=lambda x: -x.rank)
    return out[:top_k]


def _anchor_to_field(anchor: str) -> str:
    """Map adjacency cluster anchor label to a field tag."""
    return _tag_neighbor_field(anchor)


def scope_expansion_targets(map_data: dict, top_k: int = 3) -> list[FieldStats]:
    """Top-K under-explored fields for scope-expansion (drill count <= 2)."""
    field_stats = _build_field_stats(map_data)
    eligible = [s for s in field_stats.values() if s.count <= SCOPE_EXPANSION_DRILL_CEILING]

    # Add fields-not-explored (mentioned in adjacency, never drilled)
    for nf in map_data.get("fields_not_explored", []):
        name = nf["field"]
        if name not in field_stats:
            eligible.append(FieldStats(
                field=name,
                count=0,
                yield_pct=0.0,
                tiers={"load-bearing": 0, "strong": 0, "weak": 0, "none": 0, "TBD": 0},
                latest_date="",
            ))

    # Rank by: highest mention-count in adjacency (proxy for "lots of unexplored leads"),
    # then by yield_pct descending (so a 100% / 1 drill field beats a 0% / 0 drill field).
    mention_counts = {nf["field"]: nf["count"] for nf in map_data.get("fields_not_explored", [])}
    eligible.sort(key=lambda s: (
        -(mention_counts.get(s.field, 0)),
        -s.yield_pct,
        s.count,
    ))
    return eligible[:top_k]


def saturated_fields(map_data: dict) -> list[FieldStats]:
    """Fields whose last SATURATION_WINDOW drills were all low-yield."""
    return [s for s in _build_field_stats(map_data).values() if s.is_saturated]


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def build_report(map_data: dict) -> dict[str, Any]:
    cands = rank_candidates(map_data, top_k=5)
    scope = scope_expansion_targets(map_data, top_k=3)
    sat = saturated_fields(map_data)
    return {
        "parse_ok": map_data.get("parse_ok", False),
        "error": map_data.get("error"),
        "tiers": map_data.get("tiers", {}),
        "field_count": len(map_data.get("fields", [])),
        "drill_count": len(map_data.get("matrix", [])),
        "top_candidates": [c.to_dict() for c in cands],
        "scope_expansion": [{
            "field": s.field,
            "count": s.count,
            "yield_pct": s.yield_pct,
            "latest_date": s.latest_date,
        } for s in scope],
        "saturated_fields": [{
            "field": s.field,
            "recent_yields": s.recent_yields[-SATURATION_WINDOW:],
            "count": s.count,
            "yield_pct": s.yield_pct,
        } for s in sat],
    }


def format_text(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("=" * 70)
    lines.append("Research field advisor")
    lines.append("=" * 70)
    if not report["parse_ok"]:
        lines.append(f"[parse FAILED] error: {report.get('error')}")
        return "\n".join(lines)

    tiers = report["tiers"]
    lines.append(
        f"Drills: {report['drill_count']} across {report['field_count']} fields"
        f"  | tiers: load-bearing={tiers.get('load-bearing', 0)}, "
        f"strong={tiers.get('strong', 0)}, weak={tiers.get('weak', 0)}, "
        f"none={tiers.get('none', 0)}, TBD={tiers.get('TBD', 0)}"
    )
    lines.append("")

    # Top candidates
    lines.append("TOP 5 NEXT-DRILL CANDIDATES (yield-x-cost-x-adjacency)")
    lines.append("-" * 70)
    for i, c in enumerate(report["top_candidates"], 1):
        lines.append(
            f"{i}. [{c['tier']}] {c['code']} {c['name']}"
        )
        lines.append(
            f"   field={c['field']}  anchor={c['anchor']}  "
            f"anchor_yield={c['field_yield_pct']}%  cost={c['cost']}  "
            f"score={c['rank']}"
        )
        if c.get("why"):
            why = c["why"]
            if len(why) > 120:
                why = why[:117] + "..."
            lines.append(f"   why: {why}")
    lines.append("")

    # Scope expansion
    lines.append("TOP 3 SCOPE-EXPANSION FIELDS (drill count <= 2)")
    lines.append("-" * 70)
    for s in report["scope_expansion"]:
        lines.append(
            f"- {s['field']}  count={s['count']}  yield={s['yield_pct']}%  latest={s['latest_date'] or 'never'}"
        )
    lines.append("")

    # Saturation
    lines.append("SATURATED FIELDS (last 3 drills all low-yield)")
    lines.append("-" * 70)
    if not report["saturated_fields"]:
        lines.append("(none)")
    else:
        for s in report["saturated_fields"]:
            lines.append(
                f"- {s['field']}  recent={s['recent_yields']}  "
                f"overall_yield={s['yield_pct']}%  count={s['count']}"
            )
    lines.append("=" * 70)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Surface high-value next-search candidates for the research sub-agent.",
    )
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON instead of text summary")
    parser.add_argument("--top", type=int, default=5,
                        help="number of top candidates to surface (default: 5)")
    args = parser.parse_args(argv)

    if parse_research_map is None:
        msg = f"failed to import dashboard parser: {_IMPORT_ERR}"
        if args.json:
            print(json.dumps({"parse_ok": False, "error": msg}))
        else:
            print(msg, file=sys.stderr)
        return 2

    map_data = parse_research_map()
    report = build_report(map_data)

    if args.top != 5:
        # Re-rank with a different top_k
        report["top_candidates"] = [c.to_dict() for c in rank_candidates(map_data, top_k=args.top)]

    if args.json:
        out = json.dumps(report, indent=2, default=str)
    else:
        out = format_text(report)

    # Per [[feedback-ascii-only-in-scripts]] strip non-cp1252 chars before stdout
    try:
        sys.stdout.write(out + "\n")
    except UnicodeEncodeError:
        sys.stdout.write(out.encode("ascii", errors="replace").decode("ascii") + "\n")
    return 0 if report["parse_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
