"""Merged substrate-KB concept-query: fans out to primary v1 KB and chunk KB in parallel,
merges by cosine desc, dedupes by entity, tags each hit with [v1] or [chunk] KB origin.

Backs `tools/substrate_query.sh` (USER-canonical wrapper). Fixes 2026-07-02 discovery:
the wrapper had routed exclusively to the chunk KB via --chunk-content, which excludes
atoms class BY DESIGN per build_substrate_director_kb_chunk_v1.py, and had gone stale
(last built 2026-06-27). Every USER-locked pre-dispatch concept-query check via the
canonical wrapper had been architecturally blind to atoms for weeks, including today's
Stage 1 physics-law atoms.

Behavior:
- Passes user args through to director_kb_query.py TWICE in parallel:
  once against primary v1 filename-index KB, once against chunk KB (--chunk-content).
- Merges top_k_atoms by cosine desc; dedupes by entity name keeping best-cosine hit;
  tags each surviving hit with `kb=v1` or `kb=chunk`.
- Prints STALENESS WARNING at top if either KB's manifest.json is >24h old.
- Preserves existing CLI signature: all director_kb_query.py flags flow through.
- --json emits the merged combined payload.

ASCII-only. No emojis. No em-dashes.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CLI = REPO / "tools" / "director_kb_query.py"

PRIMARY_MANIFEST = REPO / "data" / "substrate_director_kb_v1" / "manifest.json"
CHUNK_MANIFEST = REPO / "data" / "substrate_director_kb_chunk_v1" / "manifest.json"

STALE_THRESHOLD_S = 24 * 60 * 60  # 24h


def _run_one(extra_flags: list[str], passthrough: list[str]) -> dict:
    """Invoke director_kb_query.py --json with given flags; parse JSON stdout."""
    cmd = [
        sys.executable,
        str(CLI),
        "--json",
        *extra_flags,
        *passthrough,
    ]
    proc = subprocess.run(
        cmd, capture_output=True, text=True, cwd=str(REPO), check=False,
    )
    if proc.returncode != 0:
        return {
            "_error": f"director_kb_query.py exit {proc.returncode}: {proc.stderr.strip()}",
            "top_k_atoms": [],
        }
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        return {
            "_error": f"JSON parse: {e}; stdout head: {proc.stdout[:200]!r}",
            "top_k_atoms": [],
        }


def _staleness_line(path: Path, label: str, now: float) -> str | None:
    if not path.exists():
        return f"WARN: {label} KB missing at {path} (never built)"
    age_s = now - path.stat().st_mtime
    if age_s > STALE_THRESHOLD_S:
        hours = age_s / 3600.0
        return f"WARN: {label} KB is {hours:.1f}h stale (manifest.json mtime; threshold=24h)"
    return None


def _merge(primary: dict, chunk: dict, k: int) -> list[dict]:
    """Merge top_k lists: tag origin, dedupe by entity (keep best cosine), sort desc, trim to k."""
    by_entity: dict[str, dict] = {}
    for hit in primary.get("top_k_atoms", []):
        tagged = dict(hit)
        tagged["_kb"] = "v1"
        by_entity[hit["entity"]] = tagged
    for hit in chunk.get("top_k_atoms", []):
        e = hit["entity"]
        tagged = dict(hit)
        tagged["_kb"] = "chunk"
        if e in by_entity:
            if hit["cosine"] > by_entity[e]["cosine"]:
                by_entity[e] = tagged
                by_entity[e]["_kb"] = "chunk+v1"
            else:
                by_entity[e]["_kb"] = "v1+chunk"
        else:
            by_entity[e] = tagged
    merged = sorted(by_entity.values(), key=lambda a: a["cosine"], reverse=True)
    return merged[:k]


def _print_human(question: str, merged: list[dict], primary: dict, chunk: dict,
                 warnings: list[str]) -> None:
    for w in warnings:
        print(w)
    if warnings:
        print()
    print(f"Q: {question}")
    p_conf = primary.get("confidence", "?")
    c_conf = chunk.get("confidence", "?")
    p_elap = primary.get("elapsed_s", "?")
    c_elap = chunk.get("elapsed_s", "?")
    print(f"  merged from: v1(conf={p_conf} elap={p_elap}s) + chunk(conf={c_conf} elap={c_elap}s)")
    if primary.get("_error"):
        print(f"  v1 ERROR: {primary['_error']}")
    if chunk.get("_error"):
        print(f"  chunk ERROR: {chunk['_error']}")
    print(f"  top-{len(merged)} atoms (deduped by entity, cosine desc):")
    for i, a in enumerate(merged):
        marker = " [SUPERSEDED]" if a.get("superseded") else ""
        kb_tag = a.get("_kb", "?")
        print(f"    {i+1}. [{kb_tag}] entity='{a['entity']}'{marker}")
        print(f"       cosine={a['cosine']}")
        scs = a.get("source_classes") or []
        if scs:
            print(f"       source_classes: {','.join(scs)}")
        sps = a.get("source_paths") or []
        if sps:
            print(f"       sources: {', '.join(sps[:3])}"
                  + ("..." if len(sps) > 3 else ""))
        rels = a.get("relations") or []
        if rels:
            rel_strs = [f"{r}->{o}" for r, o in rels[:4]]
            print(f"       edges: {' | '.join(rel_strs)}"
                  + ("..." if len(rels) > 4 else ""))
        # chunk-content mode: surface CHUNK_CONTENT snippet
        snippet = None
        for r, o in rels:
            if r == "CHUNK_CONTENT":
                snippet = o
                break
        if snippet:
            preview = snippet if len(snippet) <= 400 else snippet[:400] + "..."
            print(f"       snippet: {preview}")


def main() -> int:
    # Peel off flags we handle specially (--json, --k) from passthrough that goes to both children.
    # Everything else (query, --tau, --schema-version, --source-class, etc.) is forwarded verbatim.
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("-h", "--help", action="store_true")
    args, passthrough = ap.parse_known_args()

    if args.help:
        print(__doc__)
        print("\nAll director_kb_query.py flags are forwarded to BOTH child queries; "
              "--chunk-content is added to one child automatically.")
        return 0

    # Emit --k to both children so their JSON top_k has enough headroom for merge.
    passthrough_with_k = ["--k", str(args.k)] + passthrough

    # Extract query for the human-readable header (last non-flag argv element).
    question = ""
    for a in reversed(passthrough):
        if not a.startswith("--"):
            question = a
            break

    now = time.time()
    warnings = [w for w in (
        _staleness_line(PRIMARY_MANIFEST, "primary v1", now),
        _staleness_line(CHUNK_MANIFEST, "chunk", now),
    ) if w]

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        fut_primary = ex.submit(_run_one, [], passthrough_with_k)
        fut_chunk = ex.submit(_run_one, ["--chunk-content"], passthrough_with_k)
        primary = fut_primary.result()
        chunk = fut_chunk.result()

    merged = _merge(primary, chunk, args.k)

    if args.json:
        payload = {
            "question": question,
            "k": args.k,
            "warnings": warnings,
            "primary_kb": {
                "confidence": primary.get("confidence"),
                "elapsed_s": primary.get("elapsed_s"),
                "refused": primary.get("refused"),
                "refusal_reason": primary.get("refusal_reason"),
                "error": primary.get("_error"),
            },
            "chunk_kb": {
                "confidence": chunk.get("confidence"),
                "elapsed_s": chunk.get("elapsed_s"),
                "refused": chunk.get("refused"),
                "refusal_reason": chunk.get("refusal_reason"),
                "error": chunk.get("_error"),
            },
            "top_k_merged": merged,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        _print_human(question, merged, primary, chunk, warnings)
    return 0


if __name__ == "__main__":
    sys.exit(main())
