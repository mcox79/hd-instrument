"""Director-KB query module (ANCHOR 2; v1).

Substrate-native query over the Director-KB built by hdlab.director_kb.

Composes ONLY on chain-grade primitives (Principle 11):
  - CharTrigramEncoder (chain-grade text->HD encoder)
  - KGStore (chain-grade KG traversal primitive: single-hop via E @ (W @ key))
  - Refuse-gate (chain-grade trust filter: max-cosine < tau => REFUSE)

Public API (versioned; Principle 4 + Principle 7):
  query(question: str, schema_version: str = "v1", encoder: str = "default",
        k: int = 5, confidence_floor: float = 0.5,
        debug_include_superseded: bool = False,
        source_classes: Iterable[str] | None = None,
        filename_contains: str | None = None) -> QueryResult

QueryResult schema (load-bearing for Director consumer):
  {
    "question": str,
    "kb_version": str,
    "schema_version": str,
    "encoder": str,
    "k": int,
    "confidence_floor": float,
    "refused": bool,
    "refusal_reason": str | None,
    "confidence": float,
    "source_classes_filter": [str, ...] | None,  # echo of filter (None = unfiltered)
    "top_k_atoms": [
      {
        "entity": str,
        "cosine": float,
        "source_paths": [str, ...],
        "source_classes": [str, ...],  # source_class set for this entity
        "relations": [(rel, target), ...],  # from atoms.jsonl
        "kb_version": str,
        "encoder": str,
      }, ...
    ],
    "paths_consulted": [str, ...],   # unique source files surfaced
    "fallback_recommendation": str | None,  # "grep <terms>" if refused
    "elapsed_s": float,
  }

This module is OFFLINE (loads on disk KB once; query is pure tensor op).
"""

from __future__ import annotations

import json
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import torch

from .char_trigram_encoder import CharTrigramEncoder


# Aliases for caller convenience. Schema (config/director_kb_schema.json) uses
# singular source_class keys (note, prereg, kegg_pathway); callers naturally type
# plurals or short forms. Map both to the canonical singular schema key.
_SOURCE_CLASS_ALIASES: dict[str, str] = {
    "notes": "note",
    "preregs": "prereg",
    "kegg": "kegg_pathway",
    "go": "gene_ontology",
}


def _canonicalize_source_class(name: str) -> str:
    """Normalize a user-provided source_class token to the schema canonical form."""
    n = name.strip().lower()
    return _SOURCE_CLASS_ALIASES.get(n, n)


_DATE_RE = re.compile(r"(\d{4})[-_](\d{2})[-_](\d{2})")


def _entity_date_key(entity_name: str) -> tuple[int, int, int]:
    """Extract (YYYY, MM, DD) tuple from entity name for sort; (0,0,0) if absent.
    Recency-sort uses the MAX (most recent) date found in the string.
    """
    matches = _DATE_RE.findall(entity_name)
    if not matches:
        return (0, 0, 0)
    return max((int(y), int(m), int(d)) for (y, m, d) in matches)


def _load_jsonl(path: Path) -> list[dict]:
    out = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


class DirectorKBQuery:
    """Loads a director-KB from disk + answers natural-language queries.

    Load once at process start; query() can be called many times cheaply.
    """

    def __init__(self, kb_dir: Path, schema: dict | None = None, n_dim: int | None = None) -> None:
        kb_dir = Path(kb_dir)
        if not kb_dir.exists():
            raise FileNotFoundError(f"KB dir not found: {kb_dir}")
        self.kb_dir = kb_dir

        manifest_path = kb_dir / "manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"KB manifest missing: {manifest_path}")
        self.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.kb_version = self.manifest.get("kb_version", "v1")
        self.schema_version = self.manifest.get("schema_version", "v1")
        self.encoder_name = self.manifest.get("encoder", "char_trigram_v1")
        self.n_dim = int(self.manifest.get("n_dim", n_dim or 2048))

        # Load codebooks + atoms
        self.E: torch.Tensor = torch.load(kb_dir / "E.pt", weights_only=True)  # [n_ent, n_dim]
        self.R: torch.Tensor = torch.load(kb_dir / "R.pt", weights_only=True)
        # W matrix is loaded but only used for confidence sanity; substrate-cosine on E
        # is the primary retrieval signal in v1 (a single-hop substrate retrieval against
        # the entity codebook approximates "what entity does this question describe").
        try:
            self.W: torch.Tensor | None = torch.load(kb_dir / "W.pt", weights_only=True)
        except Exception:
            self.W = None

        self.entities: list[dict] = _load_jsonl(kb_dir / "entities.jsonl")
        self.entity_names: list[str] = [e["name"] for e in self.entities]
        self.relations: list[dict] = _load_jsonl(kb_dir / "relations.jsonl")
        self.relation_names: list[str] = [r["name"] for r in self.relations]

        atoms = _load_jsonl(kb_dir / "atoms.jsonl")
        # Index atoms by subject entity index for fast outgoing-edge lookup
        self._atoms_by_s: dict[int, list[dict]] = defaultdict(list)
        self._atoms_by_o: dict[int, list[dict]] = defaultdict(list)
        # Per-entity source file set
        self._sources_by_ent: dict[int, set[str]] = defaultdict(set)
        # Per-entity source_class set (for --source-class filter; non-breaking additive)
        self._source_classes_by_ent: dict[int, set[str]] = defaultdict(set)
        for a in atoms:
            self._atoms_by_s[a["s"]].append(a)
            self._atoms_by_o[a["o"]].append(a)
            sp = a.get("source_path")
            if sp:
                self._sources_by_ent[a["s"]].add(sp)
                self._sources_by_ent[a["o"]].add(sp)
            sc = a.get("source_class")
            if sc:
                self._source_classes_by_ent[a["s"]].add(sc)
                self._source_classes_by_ent[a["o"]].add(sc)
        # Detect superseded entities (Principle 10): any entity that appears as the
        # SOURCE of a SUPERSEDES relation is the NEW (current); the TARGET is OLD.
        try:
            supersedes_idx = self.relation_names.index("SUPERSEDES")
        except ValueError:
            supersedes_idx = -1
        self._superseded_entity_indices: set[int] = set()
        if supersedes_idx >= 0:
            for a in atoms:
                if a["p"] == supersedes_idx:
                    self._superseded_entity_indices.add(a["o"])

        self.encoder = CharTrigramEncoder(n_dim=self.n_dim)

        # Pre-normalize E for cosine similarity (load-bearing cheap)
        E_np = self.E.cpu().numpy().astype(np.float32)
        norms = np.linalg.norm(E_np, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self._E_unit = E_np / norms

    def _encode_query(self, question: str) -> np.ndarray:
        """Encode question via the same char-trigram encoder (Principle 5 default)."""
        q = self.encoder.encode(question)
        n = np.linalg.norm(q) + 1e-8
        return q / n

    def _topk_entities(
        self,
        q_unit: np.ndarray,
        k: int,
        allowed_ent_indices: set[int] | None = None,
    ) -> list[tuple[int, float]]:
        sims = self._E_unit @ q_unit
        if allowed_ent_indices is not None:
            # Mask out non-allowed entity indices (set to -inf so they sort last).
            # Required when --source-class filter is active: language ingest (~709k
            # wordnet atoms) drowns ~34k note atoms in raw cosine ranking, so
            # post-filter on top-N candidates would return zero notes hits.
            mask = np.full(len(sims), -np.inf, dtype=sims.dtype)
            idx_arr = np.fromiter(allowed_ent_indices, dtype=np.int64,
                                  count=len(allowed_ent_indices))
            if len(idx_arr) > 0:
                mask[idx_arr] = sims[idx_arr]
            sims = mask
        if k >= len(sims):
            order = np.argsort(-sims)
        else:
            top_idx = np.argpartition(-sims, k - 1)[:k]
            order = top_idx[np.argsort(-sims[top_idx])]
        # Drop -inf entries (no allowed entities or k > n_allowed)
        out = []
        for i in order[:k]:
            s = float(sims[int(i)])
            if not np.isfinite(s):
                continue
            out.append((int(i), s))
        return out

    def _entity_relations(self, ent_idx: int, max_edges: int = 8) -> list[tuple[str, str]]:
        """Return list of (rel_name, target_name) for atoms where ent is subject."""
        out: list[tuple[str, str]] = []
        for a in self._atoms_by_s.get(ent_idx, [])[:max_edges]:
            r = a.get("p_name") or self.relation_names[a["p"]]
            o = a.get("o_name") or self.entity_names[a["o"]]
            out.append((r, o))
        return out

    def query(
        self,
        question: str,
        schema_version: str = "v1",
        encoder: str = "default",
        k: int = 5,
        confidence_floor: float = 0.5,
        debug_include_superseded: bool = False,
        source_classes: Iterable[str] | None = None,
        filename_contains: str | None = None,
    ) -> dict[str, Any]:
        """Substrate-native query. Returns QueryResult dict.

        - encoder == "default" uses the KB's manifest encoder (char_trigram_v1 in v1).
        - schema_version filter is informational in v1 (single schema per KB).
        - Refusal: max_cosine < confidence_floor => refused=True + grep fallback.
        - source_classes: optional iterable of source_class names (e.g.
          {"note", "memory"}). When set, only entities with at least one atom
          tagged with one of these source_classes are eligible for top-k.
          Non-breaking additive (Principle: 12 no-lock-in); default None preserves
          prior unfiltered behavior. Common plurals (notes/preregs) are aliased to
          schema singulars (note/prereg) for caller convenience.
        - filename_contains: optional case-insensitive substring matched against
          entity strings. When set, BYPASSES cosine ranking entirely; returns all
          entities whose name contains the substring, sorted by most-recent
          embedded date (YYYY-MM-DD or YYYY_MM_DD), descending; ties broken
          alphabetically. Use when atom entity strings ARE filenames (notes/,
          memory/) and char-trigram cosine is too noisy to surface a specific
          known doc. Composes with source_classes. Non-breaking additive.
        """
        t0 = time.perf_counter()
        if schema_version != self.schema_version:
            return {
                "question": question, "kb_version": self.kb_version,
                "schema_version": self.schema_version, "encoder": self.encoder_name,
                "k": k, "confidence_floor": confidence_floor,
                "refused": True,
                "refusal_reason": f"schema_version_mismatch: kb={self.schema_version} requested={schema_version}",
                "confidence": 0.0, "top_k_atoms": [], "paths_consulted": [],
                "source_classes_filter": None,
                "fallback_recommendation": f"grep -ri '{question}' notes/ memory/",
                "elapsed_s": round(time.perf_counter() - t0, 4),
            }

        # Normalize + alias source_classes filter
        filter_set: set[str] | None = None
        if source_classes is not None:
            filter_set = {_canonicalize_source_class(sc) for sc in source_classes if sc}
            if not filter_set:
                filter_set = None

        # Build allowed-entity index set if filter is active (computed once per query)
        allowed_idx: set[int] | None = None
        if filter_set is not None:
            allowed_idx = {
                ent_idx for ent_idx, sc_set in self._source_classes_by_ent.items()
                if sc_set & filter_set
            }

        # filename_contains bypass: substring-match on entity strings; recency-sort.
        # No cosine; no refuse-gate (confidence reported as 1.0 if any hit).
        fname_substr = filename_contains.strip() if filename_contains else None
        if fname_substr:
            needle = fname_substr.lower()
            hits: list[int] = []
            for ent_idx, name in enumerate(self.entity_names):
                if needle in name.lower():
                    if allowed_idx is not None and ent_idx not in allowed_idx:
                        continue
                    if not debug_include_superseded and ent_idx in self._superseded_entity_indices:
                        continue
                    hits.append(ent_idx)
            # Sort: most-recent embedded date DESC, then entity name ASC (stable)
            hits.sort(key=lambda i: (
                tuple(-x for x in _entity_date_key(self.entity_names[i])),
                self.entity_names[i],
            ))
            topk = [(i, 1.0) for i in hits[:k]]
            max_cos = 1.0 if topk else 0.0
            refused = not topk
        else:
            q_unit = self._encode_query(question)
            # Get more candidates than k so we can filter superseded.
            # Filter-aware: _topk_entities masks non-allowed entities pre-ranking,
            # avoiding the wordnet-swamp problem (709k lexical atoms drown 34k notes).
            topk_raw = self._topk_entities(q_unit, k=k * 3, allowed_ent_indices=allowed_idx)

            # Filter superseded entities by default (Principle 10)
            if not debug_include_superseded:
                topk_raw = [(i, s) for (i, s) in topk_raw if i not in self._superseded_entity_indices]

            topk = topk_raw[:k]

            max_cos = topk[0][1] if topk else 0.0
            refused = max_cos < confidence_floor

        atom_records: list[dict] = []
        paths_consulted_set: set[str] = set()
        for ent_idx, cos in topk:
            ent_name = self.entity_names[ent_idx]
            sources = sorted(self._sources_by_ent.get(ent_idx, set()))[:4]
            paths_consulted_set.update(sources)
            atom_records.append({
                "entity": ent_name,
                "cosine": round(cos, 4),
                "source_paths": sources,
                "source_classes": sorted(self._source_classes_by_ent.get(ent_idx, set())),
                "relations": self._entity_relations(ent_idx),
                "kb_version": self.kb_version,
                "encoder": self.encoder_name,
                "superseded": ent_idx in self._superseded_entity_indices,
            })

        if fname_substr:
            refusal_reason = (
                f"filename_contains='{fname_substr}' matched zero entities"
                if refused else None
            )
            fallback = (
                f"grep -rli '{fname_substr}' notes/ memory/" if refused else None
            )
        else:
            refusal_reason = (
                f"max_cosine={max_cos:.4f} < confidence_floor={confidence_floor}"
                if refused else None
            )
            fallback = (
                f"grep -ri '{question}' notes/ memory/" if refused else None
            )

        result = {
            "question": question,
            "kb_version": self.kb_version,
            "schema_version": self.schema_version,
            "encoder": self.encoder_name,
            "k": k,
            "confidence_floor": confidence_floor,
            "refused": refused,
            "refusal_reason": refusal_reason,
            "confidence": round(max_cos, 4),
            "source_classes_filter": sorted(filter_set) if filter_set else None,
            "filename_contains_filter": fname_substr,
            "top_k_atoms": atom_records,
            "paths_consulted": sorted(paths_consulted_set),
            "fallback_recommendation": fallback,
            "elapsed_s": round(time.perf_counter() - t0, 4),
            "debug_include_superseded": debug_include_superseded,
        }
        return result


_CANONICAL_KB_DIR = "data/substrate_director_kb_v1"  # written by continuous-ingest + CLI
_ARM_KB_DIR = "data/exp_substrate_director_kb_ingest_v1/_arm_full/kb"  # written by cell ARM_INGEST_FULL


def load_default_kb(repo_root: Path | None = None) -> DirectorKBQuery:
    """Convenience: load the canonical KB (continuous-ingest); fall back to arm-full path."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent
    canon = repo_root / _CANONICAL_KB_DIR
    if (canon / "manifest.json").exists():
        return DirectorKBQuery(kb_dir=canon)
    return DirectorKBQuery(kb_dir=repo_root / _ARM_KB_DIR)
