"""Substrate-native Director-KB CONTENT-CHUNK ingest module (ANCHOR 1 v2; 2026-06-26).

DEPRECATED 2026-07-02 (UNIFIED-KB): chunk emission has been folded into
`hdlab/director_kb.py::run_ingest` so the primary KB now carries both filename-
index entities AND content-chunk entities. This module remains loadable
(exports `chunk_text`, `CONTENT_TAG_MAX_CHARS`, `CHUNK_RELATIONS_REQUIRED`,
`DEFAULT_CHUNK_CLASSES` which run_ingest imports lazily), but `run_chunk_ingest`
and the separate chunk KB path should not be invoked by new code. Retained for
backward compat until any legacy callers are cleaned up.

Architectural fix for Option A USER 2026-06-26: the v1 KB is a filename-metadata
INDEX (entities are filepaths; cosine query returns "this file has stuff about
your query" -- user still must Read the file). This v2 module ingests CONTENT
as atoms (chunk-granularity), so a query returns ranked content snippets
DIRECTLY.

Design (additive; NOT a v1 replacement -- v1 filename-index keeps working in
parallel):

  - For each source file, split body into paragraph/section CHUNKS, respecting
    markdown `##` boundaries. Target 200-800 chars per chunk; never split a
    paragraph mid-sentence; never merge across `##` headers.
  - Each chunk becomes a SEPARATE atom with `entity = chunk_id` where chunk_id =
    `<rel_path>::chunk<NNN>`. The full content lives in the `content` extra-tag
    field so the query path can return content snippets directly.
  - Bind chunks to their source file + header via 3 relations:
        (chunk_id, IS_CHUNK_OF, source_file_rel_path)
        (chunk_id, SECTION_HEADER, header_text)   [only if a `##` header present]
        (chunk_id, CHUNK_CONTENT, content_first_200_chars)
  - The encoder encodes the CHUNK CONTENT (not the chunk_id) so cosine
    retrieval matches against content semantics (the v1 KB encoded the entity
    name = filename, which is why the filename index ranks filenames).

Composes ONLY on chain-grade primitives (Principle 11):
  - hdlab.kg_traversal.KGStore (CERT 584/585)
  - hdlab.char_trigram_encoder.CharTrigramEncoder

Reads schema source_classes from config/director_kb_schema.json. Adds two new
relation types (IS_CHUNK_OF, SECTION_HEADER, CHUNK_CONTENT) that are appended
to the schema's relation_types ordering if absent (deterministic).

Public entrypoints:
  build_chunk_plan(schema, repo_root, chunk_classes, max_files_per_class=None)
  run_chunk_ingest(plan, out_dir, schema, n_dim=2048, seed=17)

The cell + the CLI both call run_chunk_ingest; only inputs vary.

No-lock-in audit (Principle 1-12):
  - Principle 1 (filesystem canonical): chunk ingest only READS source files.
  - Principle 2 (wipe-and-rebuild): chunk ingest is deterministic given
    (plan, schema, n_dim, seed) -- chunker is content-deterministic.
  - Principle 3 (versioned): atoms tagged `kb_version=v1` and
    `chunk_ingest_version=v1`.
  - Principle 4 (schema-as-config): chunk source classes resolved from schema.
  - Principle 5 (multi-encoder): atom carries `encoder=` tag.
  - Principle 6 (Director read-only): module only WRITES the chunk KB.
  - Principle 7 (graceful degradation): query path returns confidence + content
    snippet OR refuses on max_cosine < tau.
  - Principle 8 (modular): chunk ingest is a SEPARATE module from v1
    filename ingest; both can run side-by-side into different out_dirs.
  - Principle 9 (compute envelope): chunk count is bounded (chunks_per_file
    cap = 200; effectively 2x v1 file count -> ~50k chunks for 25k files).
  - Principle 10 (self-eviction): chunks inherit source-file SUPERSEDES via
    IS_CHUNK_OF traversal.
  - Principle 11 (chain-grade-only): KGStore + CharTrigramEncoder only.
  - Principle 12 (source-controlled arch): this module + the prereg co-shipped.

ASCII-only. No emojis. No em-dashes.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any

import torch

from .char_trigram_encoder import CharTrigramEncoder
from .director_kb import (
    _read_file_text,
    _resolve_source_root,
    _glob_files,
    schema_hash,
)
from .kg_traversal import KGStore


# ---------- chunker (content-deterministic) ----------

CHUNK_MIN_CHARS = 200
CHUNK_TARGET_CHARS = 800
CHUNK_HARD_MAX_CHARS = 1600
CHUNKS_PER_FILE_CAP = 200
CONTENT_TAG_MAX_CHARS = 600  # what we persist as the CHUNK_CONTENT entity name

# Match a markdown `##` header line (1-6 hashes) at line start, capture text
_HEADER_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


def _split_into_header_sections(text: str) -> list[tuple[str, str]]:
    """Split markdown text into (header_text, section_body) pairs.

    The first section before any header is paired with header_text="".
    Deterministic on input bytes.
    """
    out: list[tuple[str, str]] = []
    matches = list(_HEADER_RE.finditer(text))
    if not matches:
        return [("", text)]

    first = matches[0]
    pre = text[: first.start()]
    if pre.strip():
        out.append(("", pre))

    for i, m in enumerate(matches):
        header_text = m.group(2).strip()
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end]
        if body.strip():
            out.append((header_text, body))
    return out


def _split_section_into_chunks(body: str) -> list[str]:
    """Split a section body into chunks bounded by paragraph breaks.

    Greedy: accumulate paragraphs until chunk approaches CHUNK_TARGET_CHARS;
    never split a paragraph; if a single paragraph exceeds CHUNK_HARD_MAX_CHARS,
    split it on sentence boundaries (period+space) as a last resort.

    Skip empty chunks. Strip leading/trailing whitespace per chunk.
    """
    # Paragraph split on blank lines (>=1 blank line)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    chunks: list[str] = []
    cur: list[str] = []
    cur_len = 0
    for p in paragraphs:
        # Oversized paragraph: hard-split on sentence boundary
        if len(p) > CHUNK_HARD_MAX_CHARS:
            # Flush current
            if cur:
                chunks.append("\n\n".join(cur))
                cur = []
                cur_len = 0
            # Hard-split: ". " boundary, fall back to char slice
            parts = re.split(r"(?<=[.!?])\s+", p)
            buf: list[str] = []
            buf_len = 0
            for s in parts:
                if buf_len + len(s) > CHUNK_HARD_MAX_CHARS and buf:
                    chunks.append(" ".join(buf))
                    buf = []
                    buf_len = 0
                buf.append(s)
                buf_len += len(s) + 1
            if buf:
                chunks.append(" ".join(buf))
            continue

        if cur_len + len(p) > CHUNK_TARGET_CHARS and cur_len >= CHUNK_MIN_CHARS:
            chunks.append("\n\n".join(cur))
            cur = [p]
            cur_len = len(p)
        else:
            cur.append(p)
            cur_len += len(p) + 2

    if cur:
        chunks.append("\n\n".join(cur))

    # Drop empty / tiny chunks (<40 chars = noise)
    return [c.strip() for c in chunks if len(c.strip()) >= 40]


def chunk_text(text: str) -> list[dict]:
    """Return list of chunk dicts: [{header, content, chunk_idx}, ...].

    Determinism: given identical text bytes, returns byte-identical chunks in
    identical order. Capped at CHUNKS_PER_FILE_CAP per file (silently truncates
    further chunks; recorded in caller's manifest stats).
    """
    sections = _split_into_header_sections(text)
    out: list[dict] = []
    chunk_idx = 0
    for header, body in sections:
        for c in _split_section_into_chunks(body):
            if chunk_idx >= CHUNKS_PER_FILE_CAP:
                return out
            out.append({
                "chunk_idx": chunk_idx,
                "header": header,
                "content": c,
            })
            chunk_idx += 1
    return out


# ---------- ingest plan ----------

# Default chunk classes: TEXT modes only (notes, memory, prereg, director_plan,
# fleet_state). JSONL/API/bio modes are file-level and not chunkable.
DEFAULT_CHUNK_CLASSES = ("note", "memory", "prereg", "director_plan", "fleet_state")


def build_chunk_plan(
    schema: dict,
    repo_root: Path,
    chunk_classes: tuple[str, ...] = DEFAULT_CHUNK_CLASSES,
    max_files_per_class: int | None = None,
) -> dict:
    """Enumerate source files for chunk-ingest. Same shape as build_ingest_plan.

    Returns: {class_name: {"root": Path|None, "files": [...], "skipped_unreachable": bool}}
    """
    plan: dict[str, dict[str, Any]] = {}
    classes = schema.get("source_classes", {})
    for cname in chunk_classes:
        cdef = classes.get(cname)
        if cdef is None:
            plan[cname] = {"root": None, "files": [], "skipped_unreachable": True,
                           "skip_reason": "class_not_in_schema"}
            continue
        # Chunk ingest is text-only; skip non-text modes.
        mode = cdef.get("mode", "text")
        if mode not in ("text",):
            plan[cname] = {"root": None, "files": [], "skipped_unreachable": True,
                           "skip_reason": f"mode_{mode}_not_chunkable"}
            continue
        root = _resolve_source_root(repo_root, cdef)
        if root is None:
            plan[cname] = {"root": None, "files": [], "skipped_unreachable": True,
                           "skip_reason": "root_unreachable"}
            continue
        limit = max_files_per_class
        if limit is None:
            cmax = cdef.get("max_files")
            if cmax is not None:
                limit = int(cmax)
        files = _glob_files(root, cdef.get("glob", "*"), limit)
        plan[cname] = {
            "root": root,
            "files": files,
            "skipped_unreachable": False,
        }
    return plan


# ---------- intern helper ----------

def _intern(name: str, lookup: dict[str, int], order: list[str]) -> int:
    if name in lookup:
        return lookup[name]
    idx = len(order)
    lookup[name] = idx
    order.append(name)
    return idx


# ---------- chunk-ingest runner ----------

CHUNK_RELATIONS_REQUIRED = ("IS_CHUNK_OF", "SECTION_HEADER", "CHUNK_CONTENT")


def run_chunk_ingest(
    plan: dict,
    out_dir: Path,
    schema: dict,
    n_dim: int = 2048,
    seed: int = 17,
    wipe: bool = True,
    redact_timestamps_in_atoms: bool = False,
) -> dict:
    """Run the deterministic chunk-ingest. Writes the on-disk KB layout.

    Returns manifest dict (persisted to out_dir/manifest.json).

    Determinism contract: given identical (plan, schema, n_dim, seed) and identical
    source bytes, this function produces byte-equal entities/relations/atoms
    (modulo ingest_timestamp_ns; set redact_timestamps_in_atoms=True for byte-equal).
    W.pt equal within L2 tolerance 1e-6.

    Each chunk produces 3 atoms:
      (chunk_id, IS_CHUNK_OF, source_file_rel_path)
      (chunk_id, SECTION_HEADER, header_text)   [iff header present]
      (chunk_id, CHUNK_CONTENT, content_first_600_chars)

    The encoder encodes the CHUNK CONTENT (not the chunk_id) so cosine
    retrieval matches against content semantics.
    """
    t0 = time.perf_counter()

    out_dir = Path(out_dir)
    if wipe and out_dir.exists():
        for child in sorted(out_dir.iterdir()):
            if child.is_file():
                try:
                    child.unlink()
                except OSError:
                    pass
    out_dir.mkdir(parents=True, exist_ok=True)

    encoder = CharTrigramEncoder(n_dim=n_dim)

    entity_lookup: dict[str, int] = {}
    entity_order: list[str] = []
    relation_lookup: dict[str, int] = {}
    relation_order: list[str] = []

    # Pre-populate relation order: schema-declared relations first (for stable
    # IDs across reingest), then required chunk relations if missing.
    for rname in schema.get("relation_types", []):
        _intern(rname, relation_lookup, relation_order)
    for rname in CHUNK_RELATIONS_REQUIRED:
        _intern(rname, relation_lookup, relation_order)

    atoms: list[dict] = []
    skipped: list[dict] = []
    n_discovered = 0
    n_chunks_total = 0
    per_class_stats: dict[str, dict[str, int]] = {}

    schema_ver = schema.get("schema_version", "v1")
    kb_ver = schema.get("kb_version", "v1")
    encoder_name = schema.get("encoder_default", "char_trigram_v1")
    chunk_ingest_version = "v1"
    repo_root = Path(__file__).resolve().parent.parent
    max_body_bytes = int(schema.get("limits", {}).get("max_body_bytes_per_file", 524288))

    # Track which entities are CHUNK entities so encoder can encode chunk
    # CONTENT (looked up from a side-map of chunk_id -> content text).
    chunk_content_by_entity_idx: dict[int, str] = {}

    class_names = sorted(plan.keys())
    for cname in class_names:
        per_class_stats[cname] = {"n_files": 0, "n_chunks": 0, "n_files_zero_chunks": 0}
        files = plan[cname]["files"]
        per_class_stats[cname]["n_files"] = len(files)
        for path in files:
            n_discovered += 1
            try:
                rel_path = str(path.relative_to(repo_root)).replace("\\", "/")
            except ValueError:
                rel_path = str(path).replace("\\", "/")

            text, reject = _read_file_text(path, max_body_bytes)
            if reject is not None:
                skipped.append({"path": rel_path, "skip_reason": reject, "source_class": cname})
                continue

            chunks = chunk_text(text)
            if not chunks:
                skipped.append({"path": rel_path, "skip_reason": "no_chunks_extracted",
                                "source_class": cname})
                per_class_stats[cname]["n_files_zero_chunks"] += 1
                continue

            per_class_stats[cname]["n_chunks"] += len(chunks)
            n_chunks_total += len(chunks)

            for ch in chunks:
                chunk_id = f"{rel_path}::chunk{ch['chunk_idx']:03d}"
                content = ch["content"]
                content_tag = content[:CONTENT_TAG_MAX_CHARS]
                header = ch["header"]

                # Intern entities
                chunk_idx_ent = _intern(chunk_id, entity_lookup, entity_order)
                chunk_content_by_entity_idx[chunk_idx_ent] = content
                file_idx_ent = _intern(rel_path, entity_lookup, entity_order)
                content_idx_ent = _intern(content_tag, entity_lookup, entity_order)

                # 1. IS_CHUNK_OF
                p_idx = relation_lookup["IS_CHUNK_OF"]
                atoms.append(_make_atom(
                    triple_idx=len(atoms),
                    s_idx=chunk_idx_ent, p_idx=p_idx, o_idx=file_idx_ent,
                    s_name=chunk_id, p_name="IS_CHUNK_OF", o_name=rel_path,
                    rel_path=rel_path, cname=cname,
                    schema_ver=schema_ver, encoder_name=encoder_name,
                    chunk_ingest_version=chunk_ingest_version, kb_ver=kb_ver,
                    extra={"chunk_idx": ch["chunk_idx"], "n_chars": len(content)},
                    redact_ts=redact_timestamps_in_atoms,
                ))

                # 2. SECTION_HEADER (only if header present)
                if header:
                    header_idx_ent = _intern(header, entity_lookup, entity_order)
                    p_idx = relation_lookup["SECTION_HEADER"]
                    atoms.append(_make_atom(
                        triple_idx=len(atoms),
                        s_idx=chunk_idx_ent, p_idx=p_idx, o_idx=header_idx_ent,
                        s_name=chunk_id, p_name="SECTION_HEADER", o_name=header,
                        rel_path=rel_path, cname=cname,
                        schema_ver=schema_ver, encoder_name=encoder_name,
                        chunk_ingest_version=chunk_ingest_version, kb_ver=kb_ver,
                        extra={"chunk_idx": ch["chunk_idx"]},
                        redact_ts=redact_timestamps_in_atoms,
                    ))

                # 3. CHUNK_CONTENT (CRITICAL: full content lives in this atom's
                #    o_name; query path returns o_name as the snippet)
                p_idx = relation_lookup["CHUNK_CONTENT"]
                atoms.append(_make_atom(
                    triple_idx=len(atoms),
                    s_idx=chunk_idx_ent, p_idx=p_idx, o_idx=content_idx_ent,
                    s_name=chunk_id, p_name="CHUNK_CONTENT", o_name=content_tag,
                    rel_path=rel_path, cname=cname,
                    schema_ver=schema_ver, encoder_name=encoder_name,
                    chunk_ingest_version=chunk_ingest_version, kb_ver=kb_ver,
                    extra={"chunk_idx": ch["chunk_idx"], "content_full_n_chars": len(content)},
                    redact_ts=redact_timestamps_in_atoms,
                ))

    n_entities = len(entity_order)
    n_relations = len(relation_order)
    n_triples = len(atoms)

    # Build codebook: KGStore-style bipolar HD vectors (deterministic from seed)
    g = torch.Generator()
    g.manual_seed(seed)
    kg = KGStore(n_ent=max(n_entities, 1), n_rel=max(n_relations, 1), n_dim=n_dim, generator=g)

    # CRITICAL OVERRIDE: encode each CHUNK entity by its CONTENT (not chunk_id).
    # Non-chunk entities (filenames, headers, content-tags) keep the
    # content-deterministic char-trigram encoding of their entity NAME.
    if n_entities > 0:
        for ent_name in entity_order:
            idx = entity_lookup[ent_name]
            if idx in chunk_content_by_entity_idx:
                # CHUNK entity: encode content (the WHOLE chunk) for cosine retrieval
                hv_np = encoder.encode(chunk_content_by_entity_idx[idx])
            else:
                # Non-chunk entity: encode entity name (consistent with v1 module)
                hv_np = encoder.encode(ent_name)
            kg.E[idx] = torch.from_numpy(hv_np.astype("float32"))

    # Ingest all triples in one Hebbian pass
    if n_triples > 0:
        triple_tensor = torch.tensor(
            [[a["s"], a["p"], a["o"]] for a in atoms],
            dtype=torch.long,
        )
        kg.ingest_triples(triple_tensor)

    # Persist on-disk layout
    torch.save(kg.W, out_dir / "W.pt")
    torch.save(kg.E, out_dir / "E.pt")
    torch.save(kg.R, out_dir / "R.pt")

    with (out_dir / "entities.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for idx, name in enumerate(entity_order):
            f.write(json.dumps({"idx": idx, "name": name}, sort_keys=True) + "\n")
    with (out_dir / "relations.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for idx, name in enumerate(relation_order):
            f.write(json.dumps({"idx": idx, "name": name}, sort_keys=True) + "\n")
    with (out_dir / "atoms.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for rec in atoms:
            f.write(json.dumps(rec, sort_keys=True) + "\n")
    with (out_dir / "reject_log.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for rec in skipped:
            f.write(json.dumps(rec, sort_keys=True) + "\n")

    elapsed_s = round(time.perf_counter() - t0, 3)

    n_files_with_chunks = n_discovered - len(skipped)
    coverage = n_files_with_chunks / max(n_discovered, 1)
    avg_chunks_per_file = n_chunks_total / max(n_files_with_chunks, 1)

    manifest = {
        "kb_version": kb_ver,
        "schema_version": schema_ver,
        "schema_hash": schema_hash(schema),
        "encoder": encoder_name,
        "chunk_ingest_version": chunk_ingest_version,
        "n_dim": n_dim,
        "seed": seed,
        "n_entities": n_entities,
        "n_relations": n_relations,
        "n_triples": n_triples,
        "n_chunks": n_chunks_total,
        "n_discovered": n_discovered,
        "n_skipped": len(skipped),
        "coverage_ratio": round(coverage, 4),
        "avg_chunks_per_file": round(avg_chunks_per_file, 2),
        "per_class": per_class_stats,
        "elapsed_s": elapsed_s,
        "redact_timestamps_in_atoms": redact_timestamps_in_atoms,
        "chunk_min_chars": CHUNK_MIN_CHARS,
        "chunk_target_chars": CHUNK_TARGET_CHARS,
        "chunk_hard_max_chars": CHUNK_HARD_MAX_CHARS,
        "chunks_per_file_cap": CHUNKS_PER_FILE_CAP,
        "content_tag_max_chars": CONTENT_TAG_MAX_CHARS,
    }
    with (out_dir / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    return manifest


def _make_atom(
    triple_idx: int,
    s_idx: int, p_idx: int, o_idx: int,
    s_name: str, p_name: str, o_name: str,
    rel_path: str, cname: str,
    schema_ver: str, encoder_name: str,
    chunk_ingest_version: str, kb_ver: str,
    extra: dict | None,
    redact_ts: bool,
) -> dict:
    rec = {
        "triple_idx": triple_idx,
        "s": s_idx, "p": p_idx, "o": o_idx,
        "s_name": s_name, "p_name": p_name, "o_name": o_name,
        "source_path": rel_path,
        # source_class is prefixed with "chunk_" so query filters can
        # distinguish chunk atoms from v1 filename atoms when both KBs
        # share an index (which they don't in the default layout, but the
        # tag preserves the distinction in mixed-export scenarios).
        "source_class": f"chunk_{cname}",
        "schema_version": schema_ver,
        "encoder": encoder_name,
        "chunk_ingest_version": chunk_ingest_version,
        "kb_version": kb_ver,
    }
    if not redact_ts:
        rec["ingest_timestamp_ns"] = int(time.time_ns())
    if extra:
        for k, v in extra.items():
            rec[k] = v
    return rec


# ---------- determinism helpers (re-exported from director_kb for convenience) ----------

def files_byte_equal(p1: Path, p2: Path) -> bool:
    if not p1.exists() or not p2.exists():
        return False
    return p1.read_bytes() == p2.read_bytes()


def W_l2_diff(p1: Path, p2: Path) -> float:
    w1 = torch.load(p1, weights_only=True)
    w2 = torch.load(p2, weights_only=True)
    return float(torch.linalg.norm(w1 - w2).item())
