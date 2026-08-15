"""Register and query cached literature sources so a scan can check before hitting the web.

Two entry points:
  add   register a source (computes sha256 when a file is given), append to index.jsonl atomically
  find  query by author/year/keyword/doi and report whether we already have it

Usage:
  python tools/literature_cache.py add --key lambon_ralph_2017_natrevneurosci \\
      --title "The neural and computational bases of semantic cognition" \\
      --authors "Lambon Ralph MA; Jefferies E; Patterson K; Rogers TT" \\
      --year 2017 --venue "Nat Rev Neurosci 18:42-55" \\
      --doi 10.1038/nrn.2016.150 --access metadata_only \\
      --claim "hub pools spoke inputs into cross-modal similarity structure" \\
      --cited-by notes/lit_scan_atl_hub_and_spoke_2026-08-13.md
  python tools/literature_cache.py find --author lambon --year 2017
  python tools/literature_cache.py find --keyword "sparse coding"
  python tools/literature_cache.py find --doi 10.1038/nrn.2016.150
  python tools/literature_cache.py --self-test

ASCII-only. No emojis. No em-dashes. No numpy, so no thread pinning needed here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

REPO = Path(__file__).resolve().parent.parent
CACHE_DIR = (REPO / "data" / "literature_cache").resolve()
INDEX_PATH = CACHE_DIR / "index.jsonl"
FILES_DIR = CACHE_DIR / "files"

# Canonical field order. Rows are serialised in exactly this order so that a
# repeated add of the same source yields a byte-identical line.
FIELD_ORDER = (
    "key",
    "title",
    "authors",
    "year",
    "venue",
    "doi_or_url",
    "sha256",
    "local_path",
    "access",
    "claims_used",
    "cited_by",
    "retrieved_utc",
)

VALID_ACCESS = ("open", "metadata_only")


class CacheGuardError(Exception):
    """Raised when an operation would write outside the cache or clobber a key."""


def safe_path(candidate: str | os.PathLike[str]) -> Path:
    """Resolve candidate and refuse any path that escapes data/literature_cache/."""
    resolved = Path(candidate).resolve()
    try:
        resolved.relative_to(CACHE_DIR)
    except ValueError:
        raise CacheGuardError(
            "refusing to write outside the literature cache: %s is not under %s"
            % (resolved, CACHE_DIR)
        )
    return resolved


def sha256_of(path: str | os.PathLike[str]) -> str:
    """Return the hex sha256 of a file, read in binary in 1 MiB blocks."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical_row(row: dict[str, Any]) -> str:
    """Serialise a row to one deterministic JSON line, fixed key order, sorted lists."""
    out: dict[str, Any] = {}
    for field in FIELD_ORDER:
        value = row.get(field)
        if field in ("claims_used", "cited_by"):
            value = sorted(set(value or []))
        if field == "authors" and isinstance(value, list):
            value = list(value)
        out[field] = value
    return json.dumps(out, ensure_ascii=True, separators=(",", ":"), sort_keys=False)


def read_index(index_path: Optional[Path] = None) -> list[dict[str, Any]]:
    """Read all rows from index.jsonl, returning [] when the file does not exist."""
    path = Path(index_path) if index_path is not None else INDEX_PATH
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with open(path, "r", encoding="ascii", errors="replace", newline="") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _atomic_write_lines(path: Path, lines: Iterable[str]) -> None:
    """Write all lines to path via a temp file plus os.replace, LF endings only."""
    safe_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp_index_", suffix=".jsonl")
    os.close(fd)
    try:
        # Binary mode with explicit LF: text mode on Windows would double the newlines.
        with open(tmp, "wb") as fh:
            for line in lines:
                fh.write(line.encode("ascii"))
                fh.write(b"\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def add_source(
    key: str,
    title: str,
    authors: str,
    year: Optional[int],
    venue: str,
    doi_or_url: str,
    access: str,
    claims_used: Optional[list[str]] = None,
    cited_by: Optional[list[str]] = None,
    file_path: Optional[str] = None,
    retrieved_utc: Optional[str] = None,
    force: bool = False,
    index_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Register one source in index.jsonl, computing sha256 when a file is supplied."""
    if access not in VALID_ACCESS:
        raise ValueError("access must be one of %s, got %r" % (VALID_ACCESS, access))
    path = Path(index_path) if index_path is not None else INDEX_PATH
    safe_path(path)

    existing = read_index(path)
    by_key = {r["key"]: i for i, r in enumerate(existing)}
    if key in by_key and not force:
        raise CacheGuardError(
            "key %r already present in %s; pass --force to overwrite it" % (key, path)
        )

    sha = None
    local_path = None
    if file_path:
        src = Path(file_path).resolve()
        if not src.exists():
            raise FileNotFoundError("no such file: %s" % src)
        sha = sha256_of(src)
        try:
            src.relative_to(CACHE_DIR)
            dest = src
        except ValueError:
            FILES_DIR.mkdir(parents=True, exist_ok=True)
            dest = safe_path(FILES_DIR / ("%s%s" % (key, src.suffix.lower())))
            shutil.copy2(src, dest)
        local_path = dest.relative_to(REPO).as_posix()

    row = {
        "key": key,
        "title": title,
        "authors": authors,
        "year": year,
        "venue": venue,
        "doi_or_url": doi_or_url,
        "sha256": sha,
        "local_path": local_path,
        "access": access,
        "claims_used": claims_used or [],
        "cited_by": cited_by or [],
        "retrieved_utc": retrieved_utc
        or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    if key in by_key:
        existing[by_key[key]] = row
    else:
        existing.append(row)
    _atomic_write_lines(path, [canonical_row(r) for r in existing])
    return row


def find_sources(
    author: Optional[str] = None,
    year: Optional[int] = None,
    keyword: Optional[str] = None,
    doi: Optional[str] = None,
    index_path: Optional[Path] = None,
) -> list[dict[str, Any]]:
    """Return index rows matching every supplied filter, case-insensitive on text."""
    rows = read_index(index_path)
    out = []
    for r in rows:
        if author and author.lower() not in str(r.get("authors", "")).lower():
            continue
        if year is not None and r.get("year") != year:
            continue
        if doi and doi.lower() not in str(r.get("doi_or_url", "")).lower():
            continue
        if keyword:
            hay = " ".join(
                [
                    str(r.get("title", "")),
                    str(r.get("venue", "")),
                    " ".join(r.get("claims_used") or []),
                    str(r.get("key", "")),
                ]
            ).lower()
            if keyword.lower() not in hay:
                continue
        out.append(r)
    return out


def _print_find(rows: list[dict[str, Any]]) -> None:
    """Print find results in a compact human-readable form."""
    if not rows:
        print("NOT CACHED. No matching source. Safe to fetch, then register with 'add'.")
        print("CAVEAT (2026-08-14, measured incident: 4 agents read an empty result here as")
        print("'topic not researched' and spent ~280k tokens re-scanning a topic already covered")
        print("87KB deep in notes/research_context_binding_conjunctive_coding_and_replay_necessity_2026-08-11.md):")
        print("this tool only knows about PAPERS registered via 'add' -- it is a bibliography dedup,")
        print("not a topic-coverage index. It cannot see raw notes/ content. An empty result here is")
        print("NOT evidence the topic is unresearched. Before concluding that, also run")
        print("director_kb_query.py on the topic AND grep/Glob notes/ by keyword -- see")
        print("'an absence claim requires an enumeration, not a search' in CLAUDE.md.")
        return
    print("ALREADY CACHED: %d match(es). Do NOT re-fetch without checking these first." % len(rows))
    for r in rows:
        print("  key=%s" % r["key"])
        print("    %s (%s) %s" % (r.get("title"), r.get("year"), r.get("venue")))
        print("    access=%s doi_or_url=%s local_path=%s" % (r.get("access"), r.get("doi_or_url"), r.get("local_path")))
        for c in r.get("claims_used") or []:
            print("    claim: %s" % c)
        for n in r.get("cited_by") or []:
            print("    cited_by: %s" % n)


def self_test() -> int:
    """Prove the write guard, the no-clobber guard, and byte-identical repeated add."""
    failures = []

    # Guard 1: refuse to write outside data/literature_cache/.
    escapes = [
        REPO / "notes" / "evil.jsonl",
        CACHE_DIR / ".." / ".." / "evil.jsonl",
        Path("C:/Windows/Temp/evil.jsonl") if os.name == "nt" else Path("/tmp/evil.jsonl"),
    ]
    for bad in escapes:
        try:
            safe_path(bad)
            failures.append("GUARD REMOVED: safe_path accepted out-of-cache path %s" % bad)
        except CacheGuardError:
            pass
    # And it must still accept a legitimate in-cache path.
    try:
        safe_path(CACHE_DIR / "index.jsonl")
    except CacheGuardError:
        failures.append("safe_path wrongly rejected a legitimate in-cache path")

    tmpdir = Path(tempfile.mkdtemp(dir=str(CACHE_DIR), prefix=".selftest_"))
    try:
        idx = tmpdir / "index.jsonl"
        common = dict(
            key="selftest_key",
            title="A self test source",
            authors="Doe J; Roe R",
            year=2026,
            venue="J Self Test 1:1-2",
            doi_or_url="10.0000/selftest",
            access="metadata_only",
            claims_used=["b claim", "a claim"],
            cited_by=["notes/selftest.md"],
            retrieved_utc="2026-08-13T00:00:00Z",
            index_path=idx,
        )
        add_source(**common)
        first = idx.read_bytes()

        # Guard 2: must refuse to clobber an existing key without force.
        try:
            add_source(**common)
            failures.append("GUARD REMOVED: duplicate key accepted without --force")
        except CacheGuardError:
            pass

        # Guard 3: repeated add with force must be byte-identical.
        add_source(force=True, **common)
        second = idx.read_bytes()
        if first != second:
            failures.append(
                "NON-DETERMINISTIC: repeated add changed the index bytes\n  %r\n  %r"
                % (first, second)
            )

        # List ordering must not leak into the bytes.
        shuffled = dict(common)
        shuffled["claims_used"] = ["a claim", "b claim"]
        add_source(force=True, **shuffled)
        if idx.read_bytes() != first:
            failures.append("NON-DETERMINISTIC: claim list order changed the index bytes")

        # find must locate what add wrote.
        if len(find_sources(author="doe", year=2026, index_path=idx)) != 1:
            failures.append("find failed to retrieve the row that add wrote")
        if find_sources(author="nobody_at_all", index_path=idx):
            failures.append("find returned a match for an absent author")

        # sha256 must be the real digest of a stored file.
        probe = tmpdir / "probe.txt"
        probe.write_bytes(b"literature cache probe")
        expect = hashlib.sha256(b"literature cache probe").hexdigest()
        if sha256_of(probe) != expect:
            failures.append("sha256_of returned the wrong digest")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    if failures:
        print("SELF-TEST FAIL (%d)" % len(failures))
        for f in failures:
            print("  - %s" % f)
        return 1
    print("SELF-TEST PASS: write-guard, no-clobber guard, byte-identical repeat, find, sha256.")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    """Parse arguments and dispatch to add, find, or the self-test."""
    ap = argparse.ArgumentParser(description="Literature source cache: register and query.")
    ap.add_argument("--self-test", action="store_true", help="Run guard self-test and exit.")
    sub = ap.add_subparsers(dest="cmd")

    a = sub.add_parser("add", help="Register a source in index.jsonl.")
    a.add_argument("--key", required=True)
    a.add_argument("--title", required=True)
    a.add_argument("--authors", default="")
    a.add_argument("--year", type=int, default=None)
    a.add_argument("--venue", default="")
    a.add_argument("--doi", dest="doi_or_url", default="")
    a.add_argument("--access", choices=list(VALID_ACCESS), default="metadata_only")
    a.add_argument("--file", dest="file_path", default=None)
    a.add_argument("--claim", dest="claims", action="append", default=[])
    a.add_argument("--cited-by", dest="cited_by", action="append", default=[])
    a.add_argument("--retrieved-utc", dest="retrieved_utc", default=None)
    a.add_argument("--force", action="store_true")

    f = sub.add_parser("find", help="Query the cache before going to the web.")
    f.add_argument("--author", default=None)
    f.add_argument("--year", type=int, default=None)
    f.add_argument("--keyword", default=None)
    f.add_argument("--doi", default=None)

    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    if args.cmd == "add":
        row = add_source(
            key=args.key,
            title=args.title,
            authors=args.authors,
            year=args.year,
            venue=args.venue,
            doi_or_url=args.doi_or_url,
            access=args.access,
            claims_used=args.claims,
            cited_by=args.cited_by,
            file_path=args.file_path,
            retrieved_utc=args.retrieved_utc,
            force=args.force,
        )
        print("ADDED %s (access=%s sha256=%s)" % (row["key"], row["access"], row["sha256"]))
        return 0

    if args.cmd == "find":
        _print_find(
            find_sources(
                author=args.author, year=args.year, keyword=args.keyword, doi=args.doi
            )
        )
        return 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
