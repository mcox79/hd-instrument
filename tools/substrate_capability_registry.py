#!/usr/bin/env python3
"""Substrate Capability Registry.

Centralized index of every substrate capability test result. Walks
`data/exp_*/metrics.json`, extracts a normalized schema row per cell,
writes `data/substrate_capability_registry.jsonl`, and provides a
query CLI so post-compaction sessions can find prior findings by
capability/stage/axis/tier without grep-spelunking 4000+ exp dirs.

Disciplines:
  META_RULE_J (no silent except): every per-file failure is recorded
    in the malformed_count tally with reason; we do NOT silently skip.
  META_RULE_AH (atomic write): registry.jsonl writes via tmp + os.replace.
  Idempotent on re-run; incremental via mtime watermark.

CLI:
  python tools/substrate_capability_registry.py                       # scan + summary
  python tools/substrate_capability_registry.py --rebuild             # ignore watermark
  python tools/substrate_capability_registry.py --capability multi_hop_reasoning
  python tools/substrate_capability_registry.py --stage 3
  python tools/substrate_capability_registry.py --axis depth --value 10
  python tools/substrate_capability_registry.py --tier HARD_PASS
  python tools/substrate_capability_registry.py --audit-atomization   # find unatomized high-tier
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Iterable

# Absolute paths (per CLAUDE.md convention; cwd may be reset between calls)
ROOT = Path("d:/AI/hd-instrument")
DATA = ROOT / "data"
REGISTRY = DATA / "substrate_capability_registry.jsonl"
WATERMARK = DATA / "substrate_capability_registry.watermark.json"
FAMILIES_FILE = ROOT / "tools" / "substrate_capability_families.json"
ATOMS_JSONL = DATA / "substrate_index" / "atoms.jsonl"  # root index (sparse)
ATOMS_ROOT = DATA / "substrate_index"  # partitioned store; walk all atoms.jsonl


# ----- families ---------------------------------------------------------------

def load_families() -> list[dict[str, Any]]:
    """Return the families regex list (compiled)."""
    with open(FAMILIES_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    fams = []
    for entry in cfg["families"]:
        fams.append({
            "regex": re.compile(entry["pattern"], re.IGNORECASE),
            "family": entry["family"],
            "stage": entry.get("stage", -1),
        })
    return fams


def classify(anchor_name: str, fams: list[dict[str, Any]]) -> tuple[str, int]:
    """Return (family, stage). Default ('other', -1)."""
    name = (anchor_name or "").lower()
    for fam in fams:
        if fam["regex"].search(name):
            return fam["family"], fam["stage"]
    return "other", -1


# ----- axis + per-arm extraction ---------------------------------------------

# Common axis keys that experiments report at the top level of metrics.json
AXIS_KEYS = (
    "N", "N_DIM", "M", "K", "V_C", "V_REL", "depth", "alpha",
    "psz_B", "n_train", "n_test", "N_TRAIN", "N_TEST", "n_arms",
    "n_seeds", "T", "k", "d", "e", "batch_size", "n_concepts",
)

# Verdict-tier canonicalization
TIER_NORMALIZE = {
    "HARD_PASS": "HARD_PASS",
    "SMOKE_HARD_PASS": "SMOKE_HARD_PASS",
    "PASS": "PASS",
    "MIDDLE_BAND": "MIDDLE_BAND",
    "MEASURED_MECHANISM": "MEASURED_MECHANISM",
    "HONEST_NEGATIVE": "HONEST_NEGATIVE",
    "HONEST_BOUNDED": "HONEST_BOUNDED",
    "HARD_FAIL": "HARD_FAIL",
    "SMOKE_HARD_FAIL": "SMOKE_HARD_FAIL",
    "FAIL": "FAIL",
    "KILLED": "KILLED",
    "SATURATION": "SATURATION",
    "BY_CONSTRUCTION_SATURATION": "SATURATION",
    "UNKNOWN": "UNKNOWN",
    "ATTRIBUTION": "ATTRIBUTION",
    "ALREADY_SEPARATES": "ALREADY_SEPARATES",
    "SPARSITY_NEUTRAL": "SPARSITY_NEUTRAL",
    "NON_TEST": "NON_TEST",
}

HIGH_TIER = {"HARD_PASS", "PASS", "SMOKE_HARD_PASS", "MEASURED_MECHANISM",
             "HONEST_NEGATIVE", "HONEST_BOUNDED", "ATTRIBUTION"}


def extract_axes(metrics: dict[str, Any]) -> dict[str, Any]:
    """Pull common axis values from top-level metrics + config_version string."""
    axes: dict[str, Any] = {}
    for k in AXIS_KEYS:
        if k in metrics:
            v = metrics[k]
            if isinstance(v, (int, float, str, bool)):
                axes[k] = v
    # parse config_version "k=v k=v" pairs as fallback
    cv = metrics.get("config_version")
    if isinstance(cv, str):
        for tok in cv.replace(":", " ").replace(";", " ").split():
            if "=" in tok:
                k, _, v = tok.partition("=")
                if k in AXIS_KEYS and k not in axes:
                    # best-effort cast
                    for cast in (int, float):
                        try:
                            axes[k] = cast(v)
                            break
                        except (ValueError, TypeError):
                            continue
                    else:
                        axes[k] = v
    return axes


def extract_per_arm(metrics: dict[str, Any]) -> dict[str, Any]:
    """Pull a flattened per-arm dict from metrics.json's various shapes."""
    per_arm: dict[str, Any] = {}
    # shape A: detail.mean_accuracy {arm: val}
    detail = metrics.get("detail")
    if isinstance(detail, dict):
        for key in ("mean_accuracy", "per_arm_accuracy", "mean_score",
                    "per_arm_score", "per_arm_recall"):
            v = detail.get(key)
            if isinstance(v, dict):
                for arm, val in v.items():
                    if isinstance(val, (int, float)):
                        per_arm[f"{key}__{arm}"] = round(float(val), 6)
    # shape B: per_seed[0] is a dict of {arm_metric: val}
    per_seed = metrics.get("per_seed")
    if isinstance(per_seed, list) and per_seed and isinstance(per_seed[0], dict):
        flat0 = per_seed[0]
        for k, v in flat0.items():
            if isinstance(v, (int, float)) and not k.startswith("_"):
                per_arm.setdefault(f"per_seed0__{k}", round(float(v), 6))
    # shape C: top-level scalar metrics that look like per-arm accuracies
    for k, v in metrics.items():
        if (isinstance(v, (int, float))
                and any(tok in k.lower() for tok in
                        ("acc", "recall", "f1", "lift", "score", "auroc",
                         "mult", "ratio", "speedup", "_b_a", "_b_e"))
                and k not in {"n_seeds", "n_llm_calls", "elapsed_s"}):
            per_arm.setdefault(k, round(float(v), 6))
    return per_arm


def arms_differ_sha(per_arm: dict[str, Any]) -> str:
    """Hash of sorted per-arm pairs — quick equality check across runs."""
    s = json.dumps(sorted(per_arm.items()), sort_keys=True)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:12]


def detect_saturation(metrics: dict[str, Any], per_arm: dict[str, Any]) -> bool:
    """Heuristic: any baseline near 1.0 OR explicit by-construction flag."""
    vmsg = (metrics.get("verdict_msg") or "").lower()
    if "by_construction" in vmsg or "saturation" in vmsg:
        return True
    # check for numeric arms hitting cap
    for k, v in per_arm.items():
        kl = k.lower()
        if ("baseline" in kl or "random" in kl) and isinstance(v, (int, float)) and v >= 0.98:
            return True
    return False


def detect_cardinality_ok(metrics: dict[str, Any]) -> bool | None:
    """Read explicit CARDINALITY_OK flag if present; None if unknown."""
    for key in ("cardinality_ok", "CARDINALITY_OK", "card_ok"):
        if key in metrics:
            return bool(metrics[key])
    # check gate0 self-check shape
    g = metrics.get("gate0_self_check")
    if isinstance(g, dict):
        nd = g.get("n_cells_declared")
        ne = g.get("n_cells_emitted")
        if isinstance(nd, (int, float)) and isinstance(ne, (int, float)):
            return nd == ne
    return None


# ----- main row builder -------------------------------------------------------

def iso(ts: float) -> str:
    return dt.datetime.fromtimestamp(ts, tz=dt.timezone.utc).strftime(
        "%Y-%m-%dT%H:%MZ")


def build_row(metrics_path: Path, fams: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Parse one metrics.json into a registry row. Returns None on hard failure
    but only after recording the reason in the caller's malformed tally."""
    try:
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        return {"_malformed": True, "path": str(metrics_path), "reason": f"{type(e).__name__}: {e}"}

    anchor = (metrics.get("anchor_name") or metrics.get("anchor")
              or metrics_path.parent.name.replace("exp_", "", 1))
    verdict_raw = metrics.get("verdict") or "UNKNOWN"
    verdict = TIER_NORMALIZE.get(str(verdict_raw).upper(), str(verdict_raw))
    run_mode = metrics.get("run_mode") or ("smoke" if "smoke" in metrics_path.parent.name.lower() else "unknown")

    family, stage = classify(anchor, fams)
    axes = extract_axes(metrics)
    per_arm = extract_per_arm(metrics)

    row: dict[str, Any] = {
        "anchor_name": str(anchor),
        "path": str(metrics_path).replace("\\", "/"),
        "ts_iso": iso(time.time()),
        "mtime": iso(metrics_path.stat().st_mtime),
        "verdict": verdict,
        "verdict_raw": str(verdict_raw),
        "run_mode": str(run_mode),
        "n_seeds": metrics.get("n_seeds"),
        "axes_tested": axes,
        "per_arm_metrics": per_arm,
        "arms_differ_sha256": arms_differ_sha(per_arm),
        "cardinality_ok": detect_cardinality_ok(metrics),
        "saturation": detect_saturation(metrics, per_arm),
        "stage": stage,
        "capability_family": family,
        "elapsed_s": metrics.get("elapsed_s"),
        "verdict_msg_head": (metrics.get("verdict_msg") or "")[:240],
    }
    return row


# ----- scan + atomic write ----------------------------------------------------

def iter_metrics() -> Iterable[Path]:
    """All metrics.json under data/exp_*/."""
    for child in DATA.iterdir():
        if child.is_dir() and child.name.startswith("exp_"):
            m = child / "metrics.json"
            if m.is_file():
                yield m


def load_watermark() -> float:
    if not WATERMARK.exists():
        return 0.0
    try:
        with open(WATERMARK, "r", encoding="utf-8") as f:
            return float(json.load(f).get("last_scan_mtime", 0.0))
    except (OSError, json.JSONDecodeError, ValueError):
        return 0.0


def save_watermark(latest_mtime: float, n_entries: int) -> None:
    payload = {"last_scan_mtime": latest_mtime,
               "n_entries": n_entries,
               "scanned_at_iso": iso(time.time())}
    tmp = WATERMARK.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, WATERMARK)


def atomic_write_registry(rows: list[dict[str, Any]]) -> None:
    tmp = REGISTRY.with_suffix(".jsonl.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
    os.replace(tmp, REGISTRY)


def load_existing_rows() -> dict[str, dict[str, Any]]:
    """Return path -> row for already-built registry (for incremental merge)."""
    out: dict[str, dict[str, Any]] = {}
    if not REGISTRY.exists():
        return out
    with open(REGISTRY, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            p = row.get("path")
            if p:
                out[p] = row
    return out


def scan(rebuild: bool = False) -> dict[str, Any]:
    """Walk data/exp_*/metrics.json, build/refresh registry rows.

    Returns a summary dict with counts."""
    fams = load_families()
    watermark = 0.0 if rebuild else load_watermark()
    existing = {} if rebuild else load_existing_rows()

    n_scanned = 0
    n_parsed = 0
    n_skipped_old = 0
    n_malformed = 0
    malformed_reasons: list[str] = []
    rows_by_path: dict[str, dict[str, Any]] = dict(existing)
    latest_mtime = watermark

    for m in iter_metrics():
        n_scanned += 1
        mtime = m.stat().st_mtime
        if mtime > latest_mtime:
            latest_mtime = mtime
        # incremental skip: file unchanged since last scan AND already in registry
        path_str = str(m).replace("\\", "/")
        if (not rebuild) and mtime <= watermark and path_str in existing:
            n_skipped_old += 1
            continue
        row = build_row(m, fams)
        if row is None:
            n_malformed += 1
            continue
        if row.get("_malformed"):
            n_malformed += 1
            malformed_reasons.append(f"{row['path']}: {row['reason']}")
            # keep existing row if present, else skip
            continue
        rows_by_path[row["path"]] = row
        n_parsed += 1

    # write sorted by mtime desc for human-readable head
    ordered = sorted(rows_by_path.values(),
                     key=lambda r: r.get("mtime", ""), reverse=True)
    atomic_write_registry(ordered)
    save_watermark(latest_mtime, len(ordered))

    return {
        "n_scanned": n_scanned,
        "n_parsed": n_parsed,
        "n_skipped_unchanged": n_skipped_old,
        "n_malformed": n_malformed,
        "n_total_entries": len(ordered),
        "malformed_reasons_sample": malformed_reasons[:5],
        "watermark_iso": iso(latest_mtime),
        "registry_path": str(REGISTRY),
    }


# ----- query --------------------------------------------------------------

def load_all_rows() -> list[dict[str, Any]]:
    if not REGISTRY.exists():
        return []
    out: list[dict[str, Any]] = []
    with open(REGISTRY, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def query(args: argparse.Namespace) -> list[dict[str, Any]]:
    rows = load_all_rows()
    out = []
    for r in rows:
        if args.capability and r.get("capability_family") != args.capability:
            continue
        if args.stage is not None and r.get("stage") != args.stage:
            continue
        if args.tier and r.get("verdict") != args.tier:
            continue
        if args.anchor_substr and args.anchor_substr.lower() not in (r.get("anchor_name", "").lower()):
            continue
        if args.axis:
            ax = r.get("axes_tested", {}) or {}
            if args.axis not in ax:
                continue
            if args.value is not None:
                want = args.value
                got = ax[args.axis]
                # cast want to type of got
                try:
                    if isinstance(got, (int, float)):
                        want_cast: Any = type(got)(want)
                    else:
                        want_cast = str(want)
                except (ValueError, TypeError):
                    want_cast = want
                if got != want_cast:
                    continue
        out.append(r)
    return out


# ----- atomization audit --------------------------------------------------

def load_atomized_anchors() -> set[str]:
    """Walk every partition's atoms.jsonl + extract anchor-like substrings.

    PartitionedStore layout: data/substrate_index/<partition>/atoms.jsonl
    Each line is a JSON atom; id/name often embed the EXP_ anchor name.
    We also peek at the first 4KB of each atom blob for exp_ substrings.
    Excludes staging/old/.staging/.old shadow partitions (re-ingest leftovers)."""
    seen: set[str] = set()
    pat = re.compile(r"(?:EXP_|exp_)([A-Za-z0-9_]+)")
    if not ATOMS_ROOT.exists():
        return seen
    for atoms_file in ATOMS_ROOT.rglob("atoms.jsonl"):
        # Skip staging/old shadow stores
        parts = {p.lower() for p in atoms_file.parts}
        if any(".staging" in p or ".old" in p for p in parts):
            continue
        try:
            with open(atoms_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        a = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    blob = json.dumps(a)[:4000]
                    for m in pat.finditer(blob):
                        seen.add(m.group(1).lower())
                    aid = a.get("id", "")
                    if isinstance(aid, str):
                        seen.add(aid.lower())
        except OSError:
            continue
    return seen


def audit_atomization(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Find HIGH_TIER registry entries whose anchor doesn't appear in any atoms.jsonl.

    Match policy: anchor_name (lowercased, stripped of _smoke/_selftest/_v\\d+
    suffixes) must appear as a substring of >=1 atomized token. Substring
    direction = anchor_in_atomized (atomized may be longer, e.g. atom id
    'math::T3/EXP_<anchor>'). We do NOT accept the reverse direction
    (atom token inside anchor) because that mis-fires on short common
    suffixes like 'v1'."""
    atomized = load_atomized_anchors()
    # Strip the most common noise tokens from atomized set for faster scan
    unatomized = []
    high_tier_count = 0
    # build a single big blob for fast 'in' search since anchors are unique
    atomized_blob = "\n".join(atomized)
    suffixes = ("_smoke", "_selftest", "_self_test", "_gpu", "_cpu",
                "_h100", "_full", "_smoke2", "_smoke_probe")
    for r in rows:
        if r.get("verdict") not in HIGH_TIER:
            continue
        high_tier_count += 1
        anchor_raw = (r.get("anchor_name") or "").lower()
        if not anchor_raw or len(anchor_raw) < 8:
            continue
        # candidate forms: full anchor, anchor minus suffixes
        candidates = {anchor_raw}
        for s in suffixes:
            if anchor_raw.endswith(s):
                candidates.add(anchor_raw[: -len(s)])
        hit = any(c in atomized_blob for c in candidates if len(c) >= 8)
        if not hit:
            unatomized.append({
                "anchor_name": r.get("anchor_name"),
                "verdict": r.get("verdict"),
                "capability_family": r.get("capability_family"),
                "stage": r.get("stage"),
                "mtime": r.get("mtime"),
                "path": r.get("path"),
            })
    return {
        "n_high_tier_total": high_tier_count,
        "n_unatomized": len(unatomized),
        "n_atomized_anchor_tokens": len(atomized),
        "unatomized_sample": unatomized[:25],
    }


# ----- CLI --------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rebuild", action="store_true",
                    help="Ignore watermark; re-parse every metrics.json.")
    ap.add_argument("--scan-only", action="store_true",
                    help="Scan + write registry; skip query.")
    ap.add_argument("--no-scan", action="store_true",
                    help="Query existing registry; skip scan.")
    ap.add_argument("--capability", "--family", dest="capability",
                    help="Filter by capability_family.")
    ap.add_argument("--stage", type=int, choices=[1, 2, 3, 4],
                    help="Filter by stage.")
    ap.add_argument("--tier", help="Filter by verdict (e.g. HARD_PASS).")
    ap.add_argument("--axis", help="Filter by axis presence (and value if --value).")
    ap.add_argument("--value", help="Required value for --axis filter.")
    ap.add_argument("--anchor-substr", help="Substring match against anchor_name.")
    ap.add_argument("--limit", type=int, default=25,
                    help="Max query rows printed (default 25).")
    ap.add_argument("--audit-atomization", action="store_true",
                    help="Report HIGH_TIER findings missing from atoms.jsonl.")
    ap.add_argument("--json", action="store_true",
                    help="Emit JSON list of query results to stdout.")
    args = ap.parse_args(argv)

    if not args.no_scan:
        summary = scan(rebuild=args.rebuild)
        print(f"[scan] scanned={summary['n_scanned']} parsed={summary['n_parsed']}"
              f" skipped_unchanged={summary['n_skipped_unchanged']}"
              f" malformed={summary['n_malformed']}"
              f" total_entries={summary['n_total_entries']}")
        print(f"[scan] registry: {summary['registry_path']}")
        print(f"[scan] watermark_iso: {summary['watermark_iso']}")
        if summary["malformed_reasons_sample"]:
            print("[scan] malformed sample:")
            for r in summary["malformed_reasons_sample"]:
                print(f"  - {r}")

    if args.scan_only:
        return 0

    if args.audit_atomization:
        rows = load_all_rows()
        audit = audit_atomization(rows)
        print(f"\n[audit] high_tier_total={audit['n_high_tier_total']}"
              f" unatomized={audit['n_unatomized']}"
              f" atomized_tokens_in_atoms_jsonl={audit['n_atomized_anchor_tokens']}")
        print("[audit] sample of un-atomized HIGH_TIER findings (newest first):")
        for u in audit["unatomized_sample"]:
            print(f"  - {u['mtime']}  {u['verdict']:14s}  "
                  f"stage{u['stage']}  {u['capability_family']:30s}  {u['anchor_name']}")
        return 0

    # query mode
    results = query(args)
    if args.json:
        json.dump(results[: args.limit], sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
        return 0

    print(f"\n[query] {len(results)} matching rows; showing top {min(args.limit, len(results))}")
    # by-family count summary
    fam_counts: dict[str, int] = {}
    for r in results:
        fam_counts[r.get("capability_family", "other")] = fam_counts.get(
            r.get("capability_family", "other"), 0) + 1
    if fam_counts:
        print("[query] family counts:")
        for fam, n in sorted(fam_counts.items(), key=lambda x: -x[1]):
            print(f"  {fam:32s} {n}")

    for r in results[: args.limit]:
        axes_str = " ".join(f"{k}={v}" for k, v in (r.get("axes_tested") or {}).items())[:80]
        print(f"\n  {r.get('mtime', '?')}  {r.get('verdict', '?'):14s}  "
              f"stage{r.get('stage', '?')}  {r.get('capability_family', '?')}")
        print(f"    anchor: {r.get('anchor_name')}")
        print(f"    axes:   {axes_str}")
        print(f"    path:   {r.get('path')}")
        if r.get("saturation"):
            print(f"    [SATURATION flagged]")
        if r.get("cardinality_ok") is False:
            print(f"    [CARDINALITY breach flagged]")
        head = r.get("verdict_msg_head", "")
        if head:
            print(f"    msg:    {head[:200]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
