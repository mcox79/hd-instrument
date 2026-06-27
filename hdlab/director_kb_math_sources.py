"""Math source fetchers + parsers for Director-KB ingest (v1; 2026-06-27).

USER 2026-06-27: math + science extractor design landed; ProofWiki picked as
rank-1 for highest signal density and strategic prerequisite for USER vision
Phase 3 (substrate proposes new mathematics).

This module mirrors `director_kb_bio_sources.py` exactly. Fetch helpers write
to `data/math_kb_cache/<source>/` (deterministic; principle 2). Network access
ONLY in `fetch_<source>()`, which is idempotent (skip if cached).

Sources (v1):
  1. ProofWiki Featured pages — wikitext via MediaWiki Special:Export. Pages
     are theorems, definitions, axioms, proofs. License CC-BY-SA 3.0; each
     materialized .md file carries license + URL + attribution in YAML
     front-matter so the chunk-ingest pipeline picks them up via the
     `proofwiki` source class registered in `config/director_kb_schema.json`.

Does NOT rewrite the OLD `tools/substrate_ingest_proofwiki_v1.py` extractor
which targets the OLD `data/substrate_index/*/atoms.jsonl` partition. New
module writes to `data/math_kb_cache/proofwiki/<safe_filename>.md` for chunk
ingest to pick up.

ASCII-only. No emojis. No em-dashes.
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

USER_AGENT = "hd-instrument-research/1.0 (substrate Director-KB ingest; contact marshall.cox@gmail.com)"

# ---------- helpers ----------


def _http_get(url: str, timeout_s: int = 60) -> bytes:
    """HTTP GET with User-Agent + timeout; returns raw bytes."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout_s) as r:
        return r.read()


def _http_post(url: str, data: bytes, timeout_s: int = 60,
               content_type: str = "application/x-www-form-urlencoded") -> bytes:
    """HTTP POST with User-Agent + timeout; returns raw bytes."""
    req = urllib.request.Request(
        url, data=data,
        headers={"User-Agent": USER_AGENT, "Content-Type": content_type},
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as r:
        return r.read()


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)


def _atomic_write_text(path: Path, text: str) -> None:
    _atomic_write_bytes(path, text.encode("utf-8"))


def _cache_root(repo_root: Path) -> Path:
    return repo_root / "data" / "math_kb_cache"


def _safe_filename(title: str) -> str:
    """Convert page title to filesystem-safe filename. Deterministic."""
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "_", title.strip())
    safe = safe.strip("_")
    if not safe:
        safe = "untitled"
    return safe[:200]  # cap at 200 chars


# =====================================================================
# ProofWiki (MediaWiki Special:Export)
# =====================================================================

PROOFWIKI_BASE = "https://proofwiki.org"
PROOFWIKI_EXPORT_URL = f"{PROOFWIKI_BASE}/w/index.php?title=Special:Export"
PROOFWIKI_API_URL = f"{PROOFWIKI_BASE}/w/api.php"
PROOFWIKI_FEATURED_CAT = "Category:Featured_Proofs"
PROOFWIKI_THROTTLE_S = 1.0  # politeness

# Hard-coded Featured-tier theorem-name probes for the smoke arm. We do NOT
# rely on Featured-category enumeration alone because category membership may
# shift; instead include canonical-name probes guaranteed to exist in any
# representative ProofWiki snapshot.
PROOFWIKI_PROBE_TITLES = (
    "Cauchy-Schwarz_Inequality",
    "Pythagoras's_Theorem",
    "Bayes'_Theorem",
    "Euler-Lagrange_Equation",
    "Mean_Value_Theorem",
)


def _proofwiki_category_members(category_title: str, limit: int = 500,
                                throttle_s: float = PROOFWIKI_THROTTLE_S) -> list[str]:
    """List up to `limit` titles in a category via MediaWiki API.

    Returns deterministic list of page titles (sorted-stable). Network call.
    """
    titles: list[str] = []
    cmcontinue = None
    while len(titles) < limit:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": category_title,
            "cmlimit": str(min(500, limit - len(titles))),
            "format": "json",
        }
        if cmcontinue:
            params["cmcontinue"] = cmcontinue
        qs = urllib.parse.urlencode(params)
        url = f"{PROOFWIKI_API_URL}?{qs}"
        time.sleep(throttle_s)
        try:
            data = _http_get(url, timeout_s=30)
        except urllib.error.HTTPError as e:
            print(f"[math_sources] ProofWiki API error: {e}", flush=True)
            break
        try:
            resp = json.loads(data.decode("utf-8"))
        except json.JSONDecodeError:
            break
        members = resp.get("query", {}).get("categorymembers", [])
        for m in members:
            t = m.get("title")
            if t:
                titles.append(t)
        cont = resp.get("continue", {})
        cmcontinue = cont.get("cmcontinue")
        if not cmcontinue:
            break
    return sorted(set(titles))[:limit]


def _proofwiki_export_pages(titles: list[str],
                            throttle_s: float = PROOFWIKI_THROTTLE_S) -> bytes:
    """POST to Special:Export with titles list; returns raw XML bytes.

    Special:Export accepts up to ~100 titles per request; we chunk and combine.
    """
    all_xml = []
    chunk = 50
    for i in range(0, len(titles), chunk):
        sub = titles[i:i + chunk]
        body = urllib.parse.urlencode({
            "pages": "\n".join(sub),
            "curonly": "1",
            "wpDownload": "1",
        }).encode("utf-8")
        time.sleep(throttle_s)
        try:
            data = _http_post(PROOFWIKI_EXPORT_URL, body, timeout_s=120)
        except urllib.error.HTTPError as e:
            print(f"[math_sources] ProofWiki export error: {e}", flush=True)
            continue
        all_xml.append(data)
    return b"\n".join(all_xml)


def fetch_proofwiki_featured(repo_root: Path, max_pages: int = 500,
                             force: bool = False) -> Path:
    """Idempotent fetch of ProofWiki Featured pages.

    Returns path to cached combined XML dump
    (`data/math_kb_cache/proofwiki/_export.xml`). If cached, skip fetch
    (deterministic per principle 2).
    """
    out = _cache_root(repo_root) / "proofwiki" / "_export.xml"
    if out.exists() and not force:
        print(f"[math_sources] ProofWiki export cached at {out}", flush=True)
        return out
    print(f"[math_sources] fetching ProofWiki Featured (max_pages={max_pages})",
          flush=True)
    # Enumerate category members + add probe titles
    try:
        cat_titles = _proofwiki_category_members(
            PROOFWIKI_FEATURED_CAT, limit=max_pages,
        )
    except Exception as e:  # noqa: BLE001
        print(f"[math_sources] WARN: featured-cat enum failed ({e}); using probe titles only",
              flush=True)
        cat_titles = []
    # Prepend probes (deterministic ordering); cap at max_pages
    probe_list = list(PROOFWIKI_PROBE_TITLES)
    combined = probe_list + [t for t in cat_titles if t not in set(probe_list)]
    combined = combined[:max_pages]
    if not combined:
        raise RuntimeError(
            "ProofWiki fetch found ZERO titles (category enum + probes both empty); "
            "abort rather than write empty cache"
        )
    print(f"[math_sources] ProofWiki: exporting {len(combined)} pages", flush=True)
    xml_data = _proofwiki_export_pages(combined)
    if len(xml_data) < 1000:
        raise RuntimeError(
            f"ProofWiki export returned only {len(xml_data)} bytes; likely failure"
        )
    _atomic_write_bytes(out, xml_data)
    print(f"[math_sources] ProofWiki cached at {out} ({len(xml_data)} bytes)",
          flush=True)
    return out


def _wikitext_to_markdown(wikitext: str) -> str:
    """Minimal wikitext -> markdown transform. Deterministic.

    Handles:
      [[X]] -> [X](X.md)
      [[X|Y]] -> [Y](X.md)
      == H == -> ## H
      === H === -> ### H
      {{template ...}} -> dropped
      <math>...</math> -> $...$
      <ref>...</ref> -> dropped
    """
    s = wikitext
    # Drop templates iteratively (handles nested up to 8 levels)
    for _ in range(8):
        new_s = re.sub(r"\{\{[^{}]*\}\}", "", s)
        if new_s == s:
            break
        s = new_s
    # Drop refs
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.DOTALL)
    s = re.sub(r"<ref[^/]*/>", "", s)
    # math tags -> LaTeX $$
    s = re.sub(r"<math>(.*?)</math>", r"$\1$", s, flags=re.DOTALL)
    # Wikilinks [[X|Y]] -> [Y](X.md)
    s = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"[\2](\1.md)", s)
    # Wikilinks [[X]] -> [X](X.md)
    s = re.sub(r"\[\[([^\]]+)\]\]", r"[\1](\1.md)", s)
    # Headers: ====== -> ###### then descending
    s = re.sub(r"^======\s*(.+?)\s*======\s*$", r"###### \1", s, flags=re.MULTILINE)
    s = re.sub(r"^=====\s*(.+?)\s*=====\s*$", r"##### \1", s, flags=re.MULTILINE)
    s = re.sub(r"^====\s*(.+?)\s*====\s*$", r"#### \1", s, flags=re.MULTILINE)
    s = re.sub(r"^===\s*(.+?)\s*===\s*$", r"### \1", s, flags=re.MULTILINE)
    s = re.sub(r"^==\s*(.+?)\s*==\s*$", r"## \1", s, flags=re.MULTILINE)
    return s


def _detect_entity_type(title: str, body: str) -> str:
    """Best-effort entity-type detection from title prefix / category tags.

    Returns one of THEOREM / DEFINITION / AXIOM / PROOF / MATHEMATICAL_OBJECT
    (default).
    """
    t_lower = title.lower()
    b_lower = body.lower()
    if t_lower.startswith("definition:"):
        return "DEFINITION"
    if t_lower.startswith("axiom:"):
        return "AXIOM"
    if t_lower.startswith("proof:"):
        return "PROOF"
    # Body-based: presence of "theorem" / "proof" sections
    if "[[category:proofs]]" in b_lower or "proof ==\n" in b_lower:
        return "PROOF"
    if "theorem" in t_lower or "inequality" in t_lower or "equation" in t_lower:
        return "THEOREM"
    if "definition" in t_lower:
        return "DEFINITION"
    return "MATHEMATICAL_OBJECT"


def _detect_mathematical_field(body: str) -> str:
    """Best-effort regex over wikitext categories. Default 'unknown'."""
    m = re.search(
        r"\[\[Category:(Algebra|Analysis|Topology|Geometry|Number_Theory|Set_Theory|"
        r"Combinatorics|Probability|Logic|Calculus|Linear_Algebra|Group_Theory)\b",
        body, flags=re.IGNORECASE,
    )
    if m:
        return m.group(1).replace("_", " ").lower()
    return "unknown"


def parse_proofwiki_xml(xml_path: Path, max_pages: int | None = None) -> list[dict]:
    """Parse MediaWiki XML export -> list of dicts {title, body, entity_type,
    mathematical_field, source_url}.

    Deterministic: iterates pages in file order; emits in same order. Skips
    pages with empty body (revision dropped) and namespace != 0 (talk / user
    / etc).
    """
    out: list[dict] = []
    if not xml_path.exists():
        return out
    text = xml_path.read_text(encoding="utf-8", errors="replace")
    # XML export may concatenate multiple <mediawiki> roots when chunked; split
    # naively on the closing tag to parse each separately.
    chunks = text.split("</mediawiki>")
    page_count = 0
    for chunk in chunks:
        if "<mediawiki" not in chunk:
            continue
        if not chunk.strip().endswith("</page>"):
            chunk = chunk + "\n</mediawiki>"
        else:
            chunk = chunk + "\n</mediawiki>"
        # Strip XML namespace for simpler parsing
        chunk_no_ns = re.sub(r'\sxmlns="[^"]+"', "", chunk, count=1)
        try:
            root = ET.fromstring(chunk_no_ns)
        except ET.ParseError as e:
            print(f"[math_sources] WARN: ProofWiki XML parse error: {e}", flush=True)
            continue
        for page in root.findall("page"):
            if max_pages is not None and page_count >= max_pages:
                break
            ns_el = page.find("ns")
            try:
                ns = int(ns_el.text) if ns_el is not None and ns_el.text else 0
            except ValueError:
                ns = 0
            if ns != 0:
                continue
            title_el = page.find("title")
            rev_el = page.find("revision")
            if title_el is None or rev_el is None:
                continue
            text_el = rev_el.find("text")
            if text_el is None or text_el.text is None:
                continue
            title = title_el.text.strip()
            body = text_el.text
            if not body.strip():
                continue
            entity_type = _detect_entity_type(title, body)
            math_field = _detect_mathematical_field(body)
            url = f"{PROOFWIKI_BASE}/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
            out.append({
                "title": title,
                "body_wikitext": body,
                "entity_type": entity_type,
                "mathematical_field": math_field,
                "source_url": url,
            })
            page_count += 1
        if max_pages is not None and page_count >= max_pages:
            break
    return out


def materialize_proofwiki(parsed: list[dict], out_dir: Path) -> int:
    """Write one markdown file per parsed page to `out_dir/<safe_filename>.md`.

    YAML front-matter carries license + URL + entity_type + field +
    attribution. Body is wikitext-to-markdown transformed. Returns count of
    files written.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    n_written = 0
    for rec in parsed:
        title = rec["title"]
        body_md = _wikitext_to_markdown(rec["body_wikitext"])
        fname = _safe_filename(title) + ".md"
        path = out_dir / fname
        front = (
            "---\n"
            f"title: {json.dumps(title)}\n"
            f"entity_type: {rec['entity_type']}\n"
            f"mathematical_field: {json.dumps(rec['mathematical_field'])}\n"
            f"source_url: {json.dumps(rec['source_url'])}\n"
            "license: \"CC-BY-SA-3.0\"\n"
            "attribution: \"ProofWiki contributors\"\n"
            "---\n\n"
            f"# {title}\n\n"
            f"{body_md}\n"
        )
        _atomic_write_text(path, front)
        n_written += 1
    return n_written


def fetch_and_materialize_proofwiki(
    repo_root: Path,
    max_pages: int = 500,
    force: bool = False,
) -> dict:
    """End-to-end ProofWiki fetch + materialize. Returns summary dict.

    Idempotent: re-running with same cache returns same files (principle 2).
    """
    t0 = time.perf_counter()
    out_dir = _cache_root(repo_root) / "proofwiki"
    errors: list[str] = []
    n_files = 0
    try:
        xml_path = fetch_proofwiki_featured(repo_root, max_pages=max_pages, force=force)
    except Exception as e:  # noqa: BLE001
        errors.append(f"fetch: {type(e).__name__}: {e}")
        return {
            "ok": False,
            "elapsed_s": round(time.perf_counter() - t0, 3),
            "n_files": 0,
            "out_dir": str(out_dir),
            "errors": errors,
        }
    try:
        parsed = parse_proofwiki_xml(xml_path, max_pages=max_pages)
    except Exception as e:  # noqa: BLE001
        errors.append(f"parse: {type(e).__name__}: {e}")
        return {
            "ok": False,
            "elapsed_s": round(time.perf_counter() - t0, 3),
            "n_files": 0,
            "out_dir": str(out_dir),
            "errors": errors,
        }
    try:
        n_files = materialize_proofwiki(parsed, out_dir)
    except Exception as e:  # noqa: BLE001
        errors.append(f"materialize: {type(e).__name__}: {e}")
    elapsed = round(time.perf_counter() - t0, 3)
    return {
        "ok": len(errors) == 0 and n_files > 0,
        "elapsed_s": elapsed,
        "n_files": n_files,
        "out_dir": str(out_dir),
        "errors": errors,
    }


# =====================================================================
# Dispatcher entrypoint hooks (mirrors bio_sources pattern)
# =====================================================================


def parse_proofwiki_text_file(path: Path, class_def: dict) -> list[dict]:
    """Dispatcher entrypoint placeholder.

    ProofWiki uses `mode: "text"` so the existing chunk-ingest pipeline picks
    up the materialized .md files via glob without needing a custom triple
    extractor. This function exists for parallelism with bio_sources but is
    NOT WIRED into the chunk-ingest dispatcher; chunk-ingest reads the .md
    content directly.

    Returns empty list (chunk-ingest pipeline owns extraction).
    """
    return []
