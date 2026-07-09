"""Substrate-native Director-KB ingest module (ANCHOR 1; v1).

Walks a configured set of filesystem source classes (notes/, USER memory/,
data/exp_*/metrics.json, preregs/), extracts typed triples per a
schema-as-config file, encodes entity names via the chain-grade
char-trigram encoder, and ingests via the chain-grade KGStore primitive
into a dedicated KB on disk.

Composes ONLY on chain-grade primitives (Principle 11):
  - hdlab.kg_traversal.KGStore (CERT 584/585)
  - hdlab.char_trigram_encoder.CharTrigramEncoder (substrate-native zero-
    external-model text encoder)

Reads schema from config/director_kb_schema.json (Principle 4); writes a
deterministic on-disk KB (Principle 2) at data/substrate_director_kb_<ver>/.

Public entrypoints:
  build_ingest_plan(schema, repo_root, max_files_per_class=None)
  run_ingest(plan, out_dir, n_dim=2048, seed=17)

The cell + the CLI both call run_ingest; only the inputs (max_files_per_class,
out_dir, source-class subset) vary.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any

import torch

from .char_trigram_encoder import CharTrigramEncoder
from .kb_encoder_registry import resolve_kb_encoder
from .kg_traversal import KGStore

# UNIFIED-KB fold-in 2026-07-02: chunk-emission for text-mode classes is now
# performed inline by run_ingest below. `chunk_text` + related constants are
# lazy-imported inside run_ingest to avoid a circular import with
# `director_kb_chunk_ingest` (which imports `_read_file_text` and other
# helpers from this module). Prior architecture had two KBs (primary
# filename-index + separate chunk KB); the chunk KB went stale (last built
# 2026-06-27) while primary stays fresh via continuous-ingest. Folding
# chunk-emission into run_ingest gives ONE unified KB covering atoms /
# cert_ledger JSONL entities AND text-body content chunks. Chunk primitive is
# retained for backward compat of any legacy call site but is deprecated.


SCHEMA_PATH_DEFAULT = "config/director_kb_schema.json"


def load_schema(repo_root: Path, schema_rel: str = SCHEMA_PATH_DEFAULT) -> dict:
    """Load schema-as-config (Principle 4)."""
    p = repo_root / schema_rel
    if not p.exists():
        raise FileNotFoundError(f"schema config not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def schema_hash(schema: dict) -> str:
    """SHA256 of schema JSON for manifest provenance (catches silent schema-drift)."""
    canonical = json.dumps(schema, sort_keys=True).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _resolve_source_root(repo_root: Path, class_def: dict) -> Path | None:
    """Resolve a source-class root_dir. Returns None if the class is unreachable.

    Supports both in-repo (`root_dir`) and external (`root_dir_external`) source
    classes. External classes (e.g. USER memory at C:/Users/...) try the primary
    path then any fallbacks listed in `root_dir_external_alt`. API-mode classes
    (mode=='api') return a sentinel cache_dir under repo_root.
    """
    if class_def.get("mode") == "api":
        cache = class_def.get("cache_dir", "data/api_cache")
        return repo_root / cache
    if "root_dir" in class_def:
        root = repo_root / class_def["root_dir"]
        return root if root.exists() else None
    if "root_dir_external" in class_def:
        cands = [class_def["root_dir_external"]] + list(class_def.get("root_dir_external_alt", []))
        for c in cands:
            p = Path(c)
            if p.exists():
                return p
        return None
    return None


def _glob_files(root: Path, glob: str, limit: int | None) -> list[Path]:
    """Enumerate matching files in deterministic lexicographic order (Principle 2)."""
    matches = sorted(root.glob(glob))
    if limit is not None and len(matches) > limit:
        matches = matches[:limit]
    return matches


def build_ingest_plan(
    schema: dict,
    repo_root: Path,
    max_files_per_class: int | None = None,
    only_classes: list[str] | None = None,
) -> dict:
    """Enumerate source files per schema; returns a plan dict.

    Plan = {
      class_name: {
        "root": Path | None,
        "files": list[Path] (deterministic order),
        "skipped_unreachable": bool,
      }, ...
    }
    """
    plan: dict[str, dict[str, Any]] = {}
    classes = schema.get("source_classes", {})
    for cname, cdef in classes.items():
        if only_classes is not None and cname not in only_classes:
            continue
        if cdef.get("mode") == "api":
            # API-mode class: one synthetic "file" entry; the per-class extractor
            # iterates over the API directly. Path is the cache dir (created on demand).
            root = _resolve_source_root(repo_root, cdef)
            root.mkdir(parents=True, exist_ok=True)
            sentinel = root / f"{cname}.api"
            plan[cname] = {
                "root": root,
                "files": [sentinel],
                "skipped_unreachable": False,
            }
            continue
        root = _resolve_source_root(repo_root, cdef)
        if root is None:
            plan[cname] = {"root": None, "files": [], "skipped_unreachable": True}
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


# ---------- triple extraction ----------

_REJECT_TOO_LARGE = "body_exceeds_max_bytes"
_REJECT_DECODE_ERROR = "decode_error"
_REJECT_EMPTY_FILE = "empty_file"
_REJECT_NO_EXTRACTABLE_TRIPLES = "no_extractable_triples"


def _read_file_text(path: Path, max_bytes: int) -> tuple[str | None, str | None]:
    """Returns (text, reject_reason). Exactly one is None.

    Determinism: read raw bytes, decode utf-8 with errors=replace (deterministic).
    """
    try:
        raw = path.read_bytes()
    except OSError as e:
        return None, f"io_error:{type(e).__name__}"
    if len(raw) == 0:
        return None, _REJECT_EMPTY_FILE
    if len(raw) > max_bytes:
        return None, _REJECT_TOO_LARGE
    try:
        return raw.decode("utf-8", errors="replace"), None
    except Exception as e:  # noqa: BLE001
        return None, f"{_REJECT_DECODE_ERROR}:{type(e).__name__}"


def _safe_filename_match(pattern: str, name: str) -> dict | None:
    try:
        m = re.match(pattern, name)
    except re.error:
        return None
    if m is None:
        return None
    return m.groupdict()


def _extract_triples_jsonl(
    path: Path,
    class_name: str,
    class_def: dict,
    text: str,
    schema: dict,
    repo_root: Path,
) -> list[dict]:
    """Extract one or more triples per JSONL line per schema config (Principle 4).

    For each line:
      - parse JSON; skip on JSONDecodeError (recorded via reject log)
      - entity = row[jsonl_entity_key] (or row.id / row.atom_id fallback)
      - for each relation entry, emit (entity, rel, str(row[key])) if key present
    Deterministic: file lines iterated in disk order; per-line relations iterated
    in the schema-config-declared order.
    """
    out: list[dict] = []
    try:
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
    except ValueError:
        rel = str(path).replace("\\", "/")
    file_entity = rel

    entity_key = class_def.get("jsonl_entity_key", "id")
    relations = class_def.get("jsonl_relations", [])
    max_lines = int(class_def.get("jsonl_max_lines_per_file", 100000))

    n_lines = 0
    for line in text.splitlines():
        if not line.strip():
            continue
        n_lines += 1
        if n_lines > max_lines:
            break
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict):
            continue
        ent_val = row.get(entity_key)
        if ent_val is None or ent_val == "":
            continue
        ent_name = str(ent_val)
        # Bind file -> ANCHOR_FOR -> entity so coverage links file to its atoms
        out.append({
            "s": file_entity, "p": "ANCHOR_FOR", "o": ent_name,
            "extra_tags": {},
        })
        for rel_cfg in relations:
            k = rel_cfg.get("key")
            r = rel_cfg.get("rel")
            if not k or not r:
                continue
            v = row.get(k)
            if v is None or v == "":
                continue
            out.append({
                "s": ent_name, "p": r, "o": str(v),
                "extra_tags": {},
            })

    cap = int(schema.get("limits", {}).get("max_atoms_per_file", 64))
    # Per-file atom cap is bypassed for jsonl mode: each line is itself a source-of-truth
    # row; capping at 64 would silently truncate the cert ledger / atom corpus. We rely on
    # jsonl_max_lines_per_file instead. Belt-and-suspenders global cap at 2000000 (bumped
    # 50000 -> 2000000 on 2026-07-03: paired with schema jsonl_max_lines_per_file bump
    # 5000 -> 200000. At ~5 triples/atom (ANCHOR_FOR + 4 relations) worst case is
    # 200000 * 5 = 1M triples; 2M is 2x headroom. Rationale: 5000-line cap made today's
    # math atoms unqueryable per USER project_substrate_ingest_completeness_and_addressability.)
    hard_cap = 2000000
    if len(out) > hard_cap:
        out = out[:hard_cap]
    return out


def _extract_triples_jsonl_edges(
    path: Path,
    class_def: dict,
    text: str,
) -> list[dict]:
    """Extract graph edges from a {src,tgt,rel} JSONL edge list (Principle 4).

    Each non-empty line is parsed as JSON; the triple (row[src_key], row[rel_key],
    row[tgt_key]) is emitted verbatim so the relation TYPE becomes the predicate
    (not a fixed relation), landing each row as a genuine directed graph edge.
    Deterministic: file lines iterated in disk order. No per-file atom cap (the
    edge list is itself source-of-truth); bounded by jsonl_max_lines_per_file.
    """
    src_k = class_def.get("edge_src_key", "src_id")
    tgt_k = class_def.get("edge_tgt_key", "tgt_id")
    rel_k = class_def.get("edge_rel_key", "rel_type")
    max_lines = int(class_def.get("jsonl_max_lines_per_file", 500000))
    out: list[dict] = []
    n_lines = 0
    for line in text.splitlines():
        if not line.strip():
            continue
        n_lines += 1
        if n_lines > max_lines:
            break
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict):
            continue
        s = row.get(src_k)
        o = row.get(tgt_k)
        r = row.get(rel_k)
        if not s or not o or not r:
            continue
        out.append({"s": str(s), "p": str(r), "o": str(o), "extra_tags": {}})
    return out


def _extract_triples_api(
    class_name: str,
    class_def: dict,
    schema: dict,
    repo_root: Path,
    max_items: int | None,
) -> list[dict]:
    """Extract triples from an API-backed source (WordNet / VerbNet / FrameNet).

    Determinism: iterate over sorted IDs only; never rely on internal NLTK order.
    The cache_dir holds a per-source manifest of seen IDs for downstream debug;
    it is not consulted for ingest correctness (NLTK install is the source).
    """
    source = class_def.get("api_source", "")
    if source == "wordnet":
        return _extract_triples_wordnet(class_def, schema, repo_root, max_items)
    if source == "verbnet":
        return _extract_triples_verbnet(class_def, schema, repo_root, max_items)
    if source == "framenet":
        return _extract_triples_framenet(class_def, schema, repo_root, max_items)
    return []


def _extract_triples_wordnet(class_def: dict, schema: dict, repo_root: Path, max_items: int | None) -> list[dict]:
    """WordNet via NLTK. Sorted-by-synset-name walk for determinism."""
    try:
        from nltk.corpus import wordnet as wn
    except ImportError:
        return []
    out: list[dict] = []
    # All synsets, sorted by canonical name for deterministic iteration
    synset_names = sorted({s.name() for s in wn.all_synsets()})
    if max_items is not None:
        synset_names = synset_names[:max_items]
    cap = int(class_def.get("api_max_relations_per_entity", 32))
    for sname in synset_names:
        try:
            s = wn.synset(sname)
        except Exception:  # noqa: BLE001
            continue
        # POS tag
        out.append({"s": sname, "p": "POS_TAG", "o": s.pos(), "extra_tags": {}})
        # Gloss (definition) - truncated to keep entity names manageable
        defn = (s.definition() or "").strip()
        if defn:
            out.append({"s": sname, "p": "GLOSS", "o": defn[:200], "extra_tags": {}})
        # Examples
        for ex in s.examples()[:cap]:
            out.append({"s": sname, "p": "EXAMPLE", "o": ex[:200], "extra_tags": {}})
        # Hypernyms / hyponyms (sorted by name for determinism)
        for h in sorted(s.hypernyms(), key=lambda x: x.name())[:cap]:
            out.append({"s": sname, "p": "HYPERNYM_OF", "o": h.name(), "extra_tags": {}})
        for h in sorted(s.hyponyms(), key=lambda x: x.name())[:cap]:
            out.append({"s": sname, "p": "HYPONYM_OF", "o": h.name(), "extra_tags": {}})
        # Member / part holonyms
        for h in sorted(s.member_holonyms(), key=lambda x: x.name())[:cap]:
            out.append({"s": sname, "p": "MEMBER_HOLONYM_OF", "o": h.name(), "extra_tags": {}})
        for h in sorted(s.part_holonyms(), key=lambda x: x.name())[:cap]:
            out.append({"s": sname, "p": "PART_HOLONYM_OF", "o": h.name(), "extra_tags": {}})
        # Similar_to (adjective sim-links)
        for h in sorted(s.similar_tos(), key=lambda x: x.name())[:cap]:
            out.append({"s": sname, "p": "SIMILAR_TO", "o": h.name(), "extra_tags": {}})
        # Lemmas + antonyms (lemmas, not synsets, carry antonyms in WordNet)
        lemma_names = sorted({l.name() for l in s.lemmas()})
        for ln in lemma_names[:cap]:
            out.append({"s": sname, "p": "LEMMA_OF", "o": ln, "extra_tags": {}})
        for l in s.lemmas():
            for ant in sorted(l.antonyms(), key=lambda x: x.name())[:cap]:
                out.append({"s": l.name(), "p": "ANTONYM_OF", "o": ant.name(), "extra_tags": {}})
    return out


def _extract_triples_verbnet(class_def: dict, schema: dict, repo_root: Path, max_items: int | None) -> list[dict]:
    """VerbNet (Levin classes) via NLTK. Sorted-by-classid for determinism."""
    try:
        from nltk.corpus import verbnet as vn
    except ImportError:
        return []
    out: list[dict] = []
    classids = sorted(vn.classids())
    if max_items is not None:
        classids = classids[:max_items]
    cap = int(class_def.get("api_max_relations_per_entity", 64))
    for cid in classids:
        try:
            members = sorted(vn.lemmas(cid))
        except Exception:  # noqa: BLE001
            members = []
        for m in members[:cap]:
            out.append({"s": cid, "p": "CLASS_OF", "o": m, "extra_tags": {}})
        # Thematic roles
        try:
            roles = vn.themroles(cid)
        except Exception:  # noqa: BLE001
            roles = []
        role_entries: list[tuple[str, list[str]]] = []
        for r in roles:
            rtype = r.get("type") if isinstance(r, dict) else None
            if not rtype:
                continue
            sel_restrs: list[str] = []
            for sr in (r.get("modifiers") or []) if isinstance(r, dict) else []:
                v = sr.get("value") if isinstance(sr, dict) else None
                t = sr.get("type") if isinstance(sr, dict) else None
                if v and t:
                    sel_restrs.append(f"{v}{t}")
            role_entries.append((rtype, sorted(set(sel_restrs))))
        # Deterministic: sort by role type
        role_entries.sort(key=lambda x: x[0])
        for rtype, srs in role_entries:
            out.append({"s": cid, "p": "ROLE_OF", "o": rtype, "extra_tags": {}})
            for sr in srs[:cap]:
                out.append({"s": rtype, "p": "RESTRICTS_TO", "o": sr, "extra_tags": {}})
        # Frames (syntactic patterns) - represent as concatenated POS sequence
        try:
            frames = vn.frames(cid)
        except Exception:  # noqa: BLE001
            frames = []
        seen_patterns: set[str] = set()
        for fr in frames:
            syn = fr.get("syntax") if isinstance(fr, dict) else []
            pos_seq: list[str] = []
            for tok in syn or []:
                pos = tok.get("pos") if isinstance(tok, dict) else None
                if pos:
                    pos_seq.append(pos)
                elif isinstance(tok, dict):
                    # NLTK syntax dicts sometimes use 'value' or tag/modifier; fall back
                    val = tok.get("value") or tok.get("modifiers")
                    if isinstance(val, str):
                        pos_seq.append(val)
            if not pos_seq:
                continue
            pattern = " ".join(pos_seq)
            if pattern in seen_patterns:
                continue
            seen_patterns.add(pattern)
            out.append({"s": cid, "p": "FRAME_OF_CLASS", "o": pattern, "extra_tags": {}})
            out.append({"s": pattern, "p": "SYNTAX_PATTERN", "o": cid, "extra_tags": {}})
    return out


def _extract_triples_framenet(class_def: dict, schema: dict, repo_root: Path, max_items: int | None) -> list[dict]:
    """FrameNet via NLTK. Sorted-by-frame-name for determinism."""
    try:
        from nltk.corpus import framenet as fn
    except ImportError:
        return []
    out: list[dict] = []
    try:
        frame_names = sorted({f.name for f in fn.frames()})
    except Exception:  # noqa: BLE001
        return []
    if max_items is not None:
        frame_names = frame_names[:max_items]
    cap = int(class_def.get("api_max_relations_per_entity", 64))
    for fname in frame_names:
        try:
            fr = fn.frame(fname)
        except Exception:  # noqa: BLE001
            continue
        # Frame elements
        fe_names = sorted(fr.FE.keys()) if hasattr(fr, "FE") else []
        for fe in fe_names[:cap]:
            fe_id = f"{fname}::{fe}"
            out.append({"s": fname, "p": "HAS_FE", "o": fe_id, "extra_tags": {}})
            out.append({"s": fe_id, "p": "FRAME_OF", "o": fname, "extra_tags": {}})
        # Lexical units
        lu_names = sorted(fr.lexUnit.keys()) if hasattr(fr, "lexUnit") else []
        for lu in lu_names[:cap]:
            out.append({"s": fname, "p": "EVOKED_BY", "o": lu, "extra_tags": {}})
        # Frame relations
        rel_entries: list[tuple[str, str]] = []
        for rel in getattr(fr, "frameRelations", [])[:cap * 2]:
            try:
                rtype = rel.type.name
                # rel has superFrame / subFrame; pick the OTHER frame
                sup = rel.superFrameName if hasattr(rel, "superFrameName") else None
                sub = rel.subFrameName if hasattr(rel, "subFrameName") else None
                other = sub if sup == fname else sup
                if not other:
                    continue
                rel_entries.append((rtype, other))
            except Exception:  # noqa: BLE001
                continue
        rel_entries = sorted(set(rel_entries))
        for rtype, other in rel_entries[:cap]:
            if rtype == "Inheritance":
                out.append({"s": fname, "p": "INHERITS_FROM", "o": other, "extra_tags": {}})
            elif rtype == "Using":
                out.append({"s": fname, "p": "USES_FRAME", "o": other, "extra_tags": {}})
            elif rtype == "Precedes":
                out.append({"s": fname, "p": "PRECEDES_FRAME", "o": other, "extra_tags": {}})
            else:
                # Generic: stash under USES_FRAME (preserves graph reachability)
                out.append({"s": fname, "p": "USES_FRAME", "o": other, "extra_tags": {}})
    return out


def _extract_triples_for_file(
    path: Path,
    class_name: str,
    class_def: dict,
    text: str,
    schema: dict,
    repo_root: Path,
) -> list[dict]:
    """Extract typed triples from one file. Returns list of triple dicts.

    Each triple dict has:
      {"s": <entity_name>, "p": <relation_name>, "o": <entity_name>, "extra_tags": {...}}

    Triple extraction is deterministic (regex finditer order, fixed pattern set).
    """
    # JSONL mode dispatches to a dedicated extractor (per-line entities)
    mode = class_def.get("mode")
    if mode == "jsonl":
        return _extract_triples_jsonl(path, class_name, class_def, text, schema, repo_root)

    # JSONL edge-list mode: each line is {src_id, tgt_id, rel_type}; emit the
    # genuine directed graph edge (src, rel_type, tgt). Used for ConceptNet-
    # derived word-relation edges (data/substrate_index/concept/relations.jsonl).
    if mode == "jsonl_edges":
        return _extract_triples_jsonl_edges(path, class_def, text)

    # Bio/neuro modes (USER 2026-06-26 bio_trio request).
    # Dispatch by mode; each parser returns ALL triples for the file in
    # deterministic order. We bypass per-file atom cap for these because
    # ontology files are themselves the source-of-truth (capping at 64 would
    # silently truncate ~45k GO terms to 64 atoms = dishonestly selective).
    if mode in ("obo_go", "kegg_kgml", "nif_ttl"):
        from .director_kb_bio_sources import (  # noqa: PLC0415
            parse_gene_ontology_file,
            parse_kegg_kgml_file,
            parse_nif_ttl_file,
        )
        if mode == "obo_go":
            triples = parse_gene_ontology_file(path, class_def)
        elif mode == "kegg_kgml":
            triples = parse_kegg_kgml_file(path, class_def)
        else:  # nif_ttl
            triples = parse_nif_ttl_file(path, class_def)
        hard_cap = int(class_def.get("hard_cap_atoms", 500000))
        if len(triples) > hard_cap:
            triples = triples[:hard_cap]
        for t in triples:
            t.setdefault("extra_tags", {})
        return triples

    out: list[dict] = []
    patterns = schema.get("extraction_patterns_v1", {})
    try:
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
    except ValueError:
        rel = str(path).replace("\\", "/")
    file_entity = rel

    # always_priority_tag: bind file_entity -> <TAG> -> file_entity so query can find
    always_tag = class_def.get("always_priority_tag")
    if always_tag:
        out.append({
            "s": file_entity, "p": always_tag, "o": file_entity,
            "extra_tags": {"priority": always_tag},
        })

    # 1) Always: file -> DATE_FILED -> date (if extractable)
    date_re = patterns.get("date_filed_from_filename_re")
    if date_re:
        m = re.search(date_re, path.name)
        if m:
            out.append({
                "s": file_entity, "p": "DATE_FILED", "o": m.group(1),
                "extra_tags": {"date_filed": m.group(1)},
            })

    # 2) USER_DIRECTIVE for memory class + filenames matching pattern
    user_dir_re = patterns.get("user_directive_filename_re")
    if user_dir_re and re.search(user_dir_re, path.name):
        out.append({
            "s": file_entity, "p": "USER_DIRECTIVE", "o": "USER",
            "extra_tags": {"priority": "USER_DIRECTIVE"},
        })

    # 3) Sender/recipient from note filename
    if class_name == "note":
        fnp = class_def.get("filename_pattern_optional")
        if fnp:
            gd = _safe_filename_match(fnp, path.name)
            if gd:
                if gd.get("sender"):
                    out.append({
                        "s": gd["sender"], "p": "AUTHOR_OF", "o": file_entity,
                        "extra_tags": {"sender": gd["sender"]},
                    })
                if gd.get("topic"):
                    out.append({
                        "s": file_entity, "p": "DESCRIBES", "o": gd["topic"],
                        "extra_tags": {"topic": gd["topic"]},
                    })

    # 4) Body-based extractions
    # Cap text scan length to avoid pathological cases
    scan_text = text[:65536]

    # SUPERSEDES
    sup_re = patterns.get("supersedes_in_body_re")
    if sup_re:
        try:
            for m in re.finditer(sup_re, scan_text):
                tgt = m.group(1)
                out.append({
                    "s": file_entity, "p": "SUPERSEDES", "o": tgt,
                    "extra_tags": {},
                })
        except re.error:
            pass

    # REFERENCES
    ref_re = patterns.get("references_in_body_re")
    if ref_re:
        try:
            for m in re.finditer(ref_re, scan_text):
                tgt = m.group(1) or m.group(2)
                if tgt:
                    out.append({
                        "s": file_entity, "p": "REFERENCES", "o": tgt,
                        "extra_tags": {},
                    })
        except re.error:
            pass

    # CERT_TIER (verdict tier in body)
    cert_re = patterns.get("cert_tier_from_body_re")
    if cert_re:
        try:
            seen_tiers: set[str] = set()
            for m in re.finditer(cert_re, scan_text):
                tier = m.group(1).upper()
                if tier in seen_tiers:
                    continue
                seen_tiers.add(tier)
                # tier -> bound relation
                if tier == "HARD_PASS":
                    out.append({"s": file_entity, "p": "HARD_PASS", "o": file_entity, "extra_tags": {}})
                elif tier == "HARD_FAIL":
                    out.append({"s": file_entity, "p": "HARD_FAIL", "o": file_entity, "extra_tags": {}})
                elif tier in ("MIDDLE_BAND", "MM"):
                    out.append({"s": file_entity, "p": "MIDDLE_BAND", "o": file_entity, "extra_tags": {}})
                elif tier == "CHAIN_GRADE":
                    out.append({"s": file_entity, "p": "CHAIN_GRADE", "o": file_entity, "extra_tags": {}})
        except re.error:
            pass

    # MECHANISM_OF (anchor refs in body)
    mech_re = patterns.get("mechanism_anchor_in_body_re")
    if mech_re:
        try:
            seen_mech: set[str] = set()
            for m in re.finditer(mech_re, scan_text):
                anchor = m.group(1)
                if anchor in seen_mech:
                    continue
                seen_mech.add(anchor)
                out.append({
                    "s": file_entity, "p": "MECHANISM_OF", "o": anchor,
                    "extra_tags": {},
                })
        except re.error:
            pass

    # 5) metrics class: explicit verdict triple from json structure
    if class_name == "metrics":
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = None
        if isinstance(data, dict):
            verdict = data.get(patterns.get("verdict_from_metrics_json_key", "verdict"))
            if verdict:
                anchor_re = patterns.get("anchor_from_metrics_dirname_re")
                dirname = path.parent.name
                anchor = None
                if anchor_re:
                    am = re.match(anchor_re, dirname)
                    if am:
                        anchor = am.group(1)
                if anchor is None:
                    anchor = dirname
                out.append({
                    "s": anchor, "p": "VERDICT_OF", "o": str(verdict).upper(),
                    "extra_tags": {"verdict_value": str(verdict).upper()},
                })
                out.append({
                    "s": anchor, "p": "ANCHOR_FOR", "o": file_entity,
                    "extra_tags": {},
                })

    # FALLBACK: every successfully-read file gets at least one triple so the
    # index reflects that the file exists + its source_class. This is honest
    # (the file IS in the corpus; an index that silently drops it is dishonestly
    # selective) and keeps coverage near 1.0 by construction. Specific
    # extractors above add richer triples on top.
    if not out:
        out.append({
            "s": file_entity, "p": "DESCRIBES", "o": class_name,
            "extra_tags": {"fallback_anchor": True},
        })

    # cap atoms per file
    cap = int(schema.get("limits", {}).get("max_atoms_per_file", 64))
    if len(out) > cap:
        out = out[:cap]

    return out


# ---------- indexer + ingest ----------

def _intern(name: str, lookup: dict[str, int], order: list[str]) -> int:
    """Deterministic first-seen indexer: returns int ID; new names appended at end."""
    if name in lookup:
        return lookup[name]
    idx = len(order)
    lookup[name] = idx
    order.append(name)
    return idx


def run_ingest(
    plan: dict,
    out_dir: Path,
    schema: dict,
    n_dim: int = 2048,
    seed: int = 17,
    wipe: bool = True,
    redact_timestamps_in_atoms: bool = False,
    api_max_items_override: dict[str, int] | None = None,
) -> dict:
    """Run the deterministic ingest. Writes the on-disk KB layout.

    Returns a manifest dict (also persisted to out_dir/manifest.json).

    Args:
      plan: from build_ingest_plan
      out_dir: target dir (data/substrate_director_kb_<ver>/)
      schema: loaded schema dict
      n_dim: KGStore vector dimension (default 2048)
      seed: PRNG seed for entity/relation codebooks (W is Hebbian; deterministic
        given codebooks)
      wipe: if True, remove out_dir contents first (the safe wipe-and-rebuild)
      redact_timestamps_in_atoms: if True, omit `ingest_timestamp_ns` from the
        per-atom record (used by ARM_REINGEST_DETERMINISTIC for byte-equal compare)

    Determinism contract: given identical (plan, schema, n_dim, seed), this
    function produces byte-equal entities.jsonl / relations.jsonl. atoms.jsonl
    is byte-equal modulo `ingest_timestamp_ns` (which is per-run wall clock);
    setting redact_timestamps_in_atoms=True makes atoms.jsonl byte-equal too.
    W.pt is equal within L2 tolerance 1e-6.
    """
    t0 = time.perf_counter()

    # Lazy import to break circular dep (director_kb_chunk_ingest imports from
    # this module for _read_file_text / _glob_files / _resolve_source_root).
    from .director_kb_chunk_ingest import (  # noqa: PLC0415
        CHUNK_RELATIONS_REQUIRED,
        CONTENT_TAG_MAX_CHARS,
        DEFAULT_CHUNK_CLASSES,
        chunk_text,
    )

    out_dir = Path(out_dir)
    if wipe and out_dir.exists():
        for child in sorted(out_dir.iterdir()):
            if child.is_file():
                try:
                    child.unlink()
                except OSError:
                    pass
    out_dir.mkdir(parents=True, exist_ok=True)

    # Encoder resolves through the KB encoder registry by schema encoder_default
    # (default char_trigram_v1). Additive + no-regression: char_trigram_v1
    # returns CharTrigramEncoder exactly as the prior hard-coded construction.
    encoder = resolve_kb_encoder(
        schema.get("encoder_default", "char_trigram_v1"), n_dim)

    # Entity + relation tables: first-seen insertion order from a deterministic
    # walk over (class, file) -> triples
    entity_lookup: dict[str, int] = {}
    entity_order: list[str] = []
    relation_lookup: dict[str, int] = {}
    relation_order: list[str] = []

    # Pre-populate relation order from schema (deterministic; ensures relations
    # missing from the corpus still have stable IDs across reingests where the
    # corpus differs slightly).
    for rname in schema.get("relation_types", []):
        _intern(rname, relation_lookup, relation_order)
    # UNIFIED-KB: chunk relations required for content-chunk atoms
    for rname in CHUNK_RELATIONS_REQUIRED:
        _intern(rname, relation_lookup, relation_order)

    # UNIFIED-KB: side-map of entity_idx -> chunk content string. Any entity in
    # this map is encoded via CONTENT (not entity NAME) in the codebook build
    # below, so cosine retrieval matches on chunk semantics.
    chunk_content_by_entity_idx: dict[int, str] = {}

    # Per-triple records (the atoms.jsonl content)
    atoms: list[dict] = []
    skipped: list[dict] = []
    n_discovered = 0
    n_chunks_total = 0

    # Deterministic class iteration order: sorted by class name
    class_names = sorted(plan.keys())

    classes_def = schema.get("source_classes", {})
    max_body_bytes = int(schema.get("limits", {}).get("max_body_bytes_per_file", 524288))
    schema_ver = schema.get("schema_version", "v1")
    kb_ver = schema.get("kb_version", "v1")
    encoder_name = schema.get("encoder_default", "char_trigram_v1")
    ingest_version = "v1"
    repo_root = Path(__file__).resolve().parent.parent

    for cname in class_names:
        files = plan[cname]["files"]
        cdef = classes_def.get(cname, {})
        is_api = cdef.get("mode") == "api"
        for path in files:
            n_discovered += 1
            try:
                rel_path = str(path.relative_to(repo_root)).replace("\\", "/")
            except ValueError:
                rel_path = str(path).replace("\\", "/")
            if is_api:
                # API-mode: skip file-read; call extractor with per-class max_items
                api_cap = cdef.get("api_max_items")
                if api_max_items_override is not None and cname in api_max_items_override:
                    api_cap = api_max_items_override[cname]
                if api_cap is not None:
                    api_cap = int(api_cap)
                try:
                    triples = _extract_triples_api(cname, cdef, schema, repo_root, api_cap)
                except Exception as e:  # noqa: BLE001
                    skipped.append({"path": rel_path, "skip_reason": f"api_extractor_error:{type(e).__name__}:{e}", "source_class": cname})
                    continue
                if not triples:
                    skipped.append({"path": rel_path, "skip_reason": "api_no_triples_extracted", "source_class": cname})
                    continue
                for tri in triples:
                    s_idx = _intern(tri["s"], entity_lookup, entity_order)
                    p_idx = _intern(tri["p"], relation_lookup, relation_order)
                    o_idx = _intern(tri["o"], entity_lookup, entity_order)
                    rec = {
                        "triple_idx": len(atoms),
                        "s": s_idx, "p": p_idx, "o": o_idx,
                        "s_name": tri["s"], "p_name": tri["p"], "o_name": tri["o"],
                        "source_path": rel_path,
                        "source_class": cname,
                        "schema_version": schema_ver,
                        "encoder": encoder_name,
                        "ingest_version": ingest_version,
                        "kb_version": kb_ver,
                    }
                    if not redact_timestamps_in_atoms:
                        rec["ingest_timestamp_ns"] = int(time.time_ns())
                    for k, v in tri.get("extra_tags", {}).items():
                        rec[k] = v
                    atoms.append(rec)
                continue
            # Bio modes (obo_go/kegg_kgml/nif_ttl) read the file themselves
            # inside the parser (handles large files like GO's 32MB .obo).
            # For text/jsonl modes, we pre-read with the body-bytes cap.
            mode = cdef.get("mode")
            if mode in ("obo_go", "kegg_kgml", "nif_ttl"):
                text = ""  # parser ignores `text` for these modes
            else:
                text, reject = _read_file_text(path, max_body_bytes)
                if reject is not None:
                    skipped.append({"path": rel_path, "skip_reason": reject, "source_class": cname})
                    continue
            triples = _extract_triples_for_file(path, cname, cdef, text, schema, repo_root)
            # _extract_triples_for_file is guaranteed to return >=1 triple (fallback
            # DESCRIBES anchor); keep the empty-check as a defensive belt-and-suspenders
            # in case future extractor refactor removes the fallback.
            if not triples:
                skipped.append({"path": rel_path, "skip_reason": _REJECT_NO_EXTRACTABLE_TRIPLES, "source_class": cname})
                continue
            for tri in triples:
                s_idx = _intern(tri["s"], entity_lookup, entity_order)
                p_idx = _intern(tri["p"], relation_lookup, relation_order)
                o_idx = _intern(tri["o"], entity_lookup, entity_order)
                rec = {
                    "triple_idx": len(atoms),
                    "s": s_idx, "p": p_idx, "o": o_idx,
                    "s_name": tri["s"], "p_name": tri["p"], "o_name": tri["o"],
                    "source_path": rel_path,
                    "source_class": cname,
                    "schema_version": schema_ver,
                    "encoder": encoder_name,
                    "ingest_version": ingest_version,
                    "kb_version": kb_ver,
                }
                if not redact_timestamps_in_atoms:
                    rec["ingest_timestamp_ns"] = int(time.time_ns())
                # extra tags from extractor
                for k, v in tri.get("extra_tags", {}).items():
                    rec[k] = v
                atoms.append(rec)

            # UNIFIED-KB 2026-07-02: for text-mode chunkable classes, ALSO
            # emit content-chunk triples so text-body semantic-content is
            # queryable in the same KB. Excluded classes (atoms/cert_ledger
            # JSONL, api/bio modes, and metrics.json which is machine JSON not
            # narrative prose) get filename+metadata triples only.
            if cname in DEFAULT_CHUNK_CLASSES and mode in (None, "text"):
                chunks = chunk_text(text)
                if chunks:
                    n_chunks_total += len(chunks)
                    for ch in chunks:
                        chunk_id = f"{rel_path}::chunk{ch['chunk_idx']:03d}"
                        content = ch["content"]
                        content_tag = content[:CONTENT_TAG_MAX_CHARS]
                        header = ch["header"]

                        chunk_ent_idx = _intern(chunk_id, entity_lookup, entity_order)
                        # Register content override for encoding (below).
                        chunk_content_by_entity_idx[chunk_ent_idx] = content
                        file_ent_idx = _intern(rel_path, entity_lookup, entity_order)
                        content_ent_idx = _intern(content_tag, entity_lookup, entity_order)

                        # 1. (chunk_id, IS_CHUNK_OF, source_file)
                        is_chunk_p = _intern("IS_CHUNK_OF", relation_lookup, relation_order)
                        chunk_rec = {
                            "triple_idx": len(atoms),
                            "s": chunk_ent_idx, "p": is_chunk_p, "o": file_ent_idx,
                            "s_name": chunk_id, "p_name": "IS_CHUNK_OF", "o_name": rel_path,
                            "source_path": rel_path, "source_class": cname,
                            "schema_version": schema_ver, "encoder": encoder_name,
                            "ingest_version": ingest_version, "kb_version": kb_ver,
                            "chunk_idx": ch["chunk_idx"], "n_chars": len(content),
                        }
                        if not redact_timestamps_in_atoms:
                            chunk_rec["ingest_timestamp_ns"] = int(time.time_ns())
                        atoms.append(chunk_rec)

                        # 2. (chunk_id, SECTION_HEADER, header)  [iff header present]
                        if header:
                            header_ent_idx = _intern(header, entity_lookup, entity_order)
                            sh_p = _intern("SECTION_HEADER", relation_lookup, relation_order)
                            hdr_rec = {
                                "triple_idx": len(atoms),
                                "s": chunk_ent_idx, "p": sh_p, "o": header_ent_idx,
                                "s_name": chunk_id, "p_name": "SECTION_HEADER",
                                "o_name": header,
                                "source_path": rel_path, "source_class": cname,
                                "schema_version": schema_ver, "encoder": encoder_name,
                                "ingest_version": ingest_version, "kb_version": kb_ver,
                                "chunk_idx": ch["chunk_idx"],
                            }
                            if not redact_timestamps_in_atoms:
                                hdr_rec["ingest_timestamp_ns"] = int(time.time_ns())
                            atoms.append(hdr_rec)

                        # 3. (chunk_id, CHUNK_CONTENT, content_tag)  -- content
                        #    text lives on the o_name so query can return snippet
                        cc_p = _intern("CHUNK_CONTENT", relation_lookup, relation_order)
                        cc_rec = {
                            "triple_idx": len(atoms),
                            "s": chunk_ent_idx, "p": cc_p, "o": content_ent_idx,
                            "s_name": chunk_id, "p_name": "CHUNK_CONTENT",
                            "o_name": content_tag,
                            "source_path": rel_path, "source_class": cname,
                            "schema_version": schema_ver, "encoder": encoder_name,
                            "ingest_version": ingest_version, "kb_version": kb_ver,
                            "chunk_idx": ch["chunk_idx"],
                            "content_full_n_chars": len(content),
                        }
                        if not redact_timestamps_in_atoms:
                            cc_rec["ingest_timestamp_ns"] = int(time.time_ns())
                        atoms.append(cc_rec)

    n_entities = len(entity_order)
    n_relations = len(relation_order)
    n_triples = len(atoms)

    # Build entity + relation codebooks (KGStore-style bipolar HD vectors).
    # Use a deterministic seeded generator so same (n_dim, seed, n_ent) -> same E.
    g = torch.Generator()
    g.manual_seed(seed)
    # init_entities=False: E is fully overwritten below with encoder codebook
    # vectors, so skip the wasteful random bipolar init (saves ~4.6 GB transient
    # int8 buffers at KB scale; the random init was OOM-killing the build).
    kg = KGStore(n_ent=max(n_entities, 1), n_rel=max(n_relations, 1), n_dim=n_dim,
                 generator=g, init_entities=False)

    # Override entity codebook with content-deterministic char-trigram encoding
    # (Principle 5: the encoder is the substrate-native one). For entities whose
    # name is empty, fall back to KGStore's random bipolar.
    # UNIFIED-KB 2026-07-02: CHUNK entities (in chunk_content_by_entity_idx) are
    # encoded by CHUNK CONTENT rather than entity NAME (chunk_id like
    # "notes/foo.md::chunk003" carries no semantic signal). This matches the
    # design of the retired chunk KB primitive: cosine query hits chunk atoms
    # by content semantics; non-chunk entities (filenames, headers, atoms,
    # cert_ledger row ids, and the content-tag entities themselves) keep
    # name-encoding.
    if n_entities > 0:
        for ent_name in entity_order:
            idx = entity_lookup[ent_name]
            if idx in chunk_content_by_entity_idx:
                hv_np = encoder.encode(chunk_content_by_entity_idx[idx])
            else:
                hv_np = encoder.encode(ent_name)
            # Convert numpy bipolar to torch float32 [n_dim]
            kg.E[idx] = torch.from_numpy(hv_np.astype("float32"))
    # Relations stay as KGStore's bipolar (deterministic from generator + seed)

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

    # Per-class breakdown (count discovered/skipped per class) for manifest
    per_class: dict[str, dict] = {}
    for cname in class_names:
        per_class[cname] = {
            "n_discovered": len(plan[cname]["files"]),
            "skipped_unreachable": plan[cname].get("skipped_unreachable", False),
            "root": str(plan[cname]["root"]) if plan[cname]["root"] else None,
        }
    for s in skipped:
        cname = s["source_class"]
        per_class.setdefault(cname, {}).setdefault("n_skipped", 0)
        per_class[cname]["n_skipped"] = per_class[cname].get("n_skipped", 0) + 1

    coverage = (n_discovered - len(skipped)) / max(n_discovered, 1)
    manifest = {
        "kb_version": kb_ver,
        "schema_version": schema_ver,
        "schema_hash": schema_hash(schema),
        "encoder": encoder_name,
        "ingest_version": ingest_version,
        "n_dim": n_dim,
        "seed": seed,
        "n_entities": n_entities,
        "n_relations": n_relations,
        "n_triples": n_triples,
        "n_discovered": n_discovered,
        "n_skipped": len(skipped),
        "coverage_ratio": round(coverage, 4),
        "per_class": per_class,
        "elapsed_s": elapsed_s,
        "redact_timestamps_in_atoms": redact_timestamps_in_atoms,
        "n_chunks_total": n_chunks_total,  # UNIFIED-KB 2026-07-02
    }
    with (out_dir / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    return manifest


# ---------- determinism helpers ----------

def files_byte_equal(p1: Path, p2: Path) -> bool:
    """Strict byte-equality on two files; cheap exact-match check."""
    if not p1.exists() or not p2.exists():
        return False
    return p1.read_bytes() == p2.read_bytes()


def W_l2_diff(p1: Path, p2: Path) -> float:
    """L2 norm of (W1 - W2) for the two persisted W.pt files."""
    w1 = torch.load(p1, weights_only=True)
    w2 = torch.load(p2, weights_only=True)
    return float(torch.linalg.norm(w1 - w2).item())
