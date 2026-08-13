"""Backfill PIPELINE provenance for the landed v1 foundation into a NEW store.

READS  data/foundation/reading_grounding_v1/store            (READ-ONLY, never written back)
WRITES data/foundation_provenance_v1/store                   (new, pipeline-tagged)
       data/foundation_provenance_v1/quarantine_report.json
       data/foundation_provenance_v1/backfill_manifest.json

TAGGING RULE (deterministic, derived from the existing `source` field, no guessing):
  source == "seed_base_vocabulary"  -> SEED_VOCABULARY
  source startswith "reading:"      -> READING_GROUNDING   (written by
                                       reading_grounding_loop.commit_grounding as
                                       f"reading:{source_tag}")
  anything else                     -> UNKNOWN_LEGACY  (counted + listed, never guessed)

WHAT IS AND IS NOT CLAIMED. The tag is written to the plaintext ledger only. The landed fact
VECTORS are copied bit-identically and are NOT re-encoded, so they carry no PIPELINE binding
and the glass-box read of a backfilled fact returns UNKNOWN_LEGACY. That is deliberate and
honest: re-encoding 7966 facts would produce a store that is no longer the landed evidence.
Facts written from here on (with an explicit `pipeline=`) ARE HD-bound and glass-box
recoverable. Both properties are pinned by
verification/verify_fact_store_pipeline_provenance.py.

NOTHING IS BANKED HERE. This script only re-homes what is already on disk, with provenance.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import torch  # noqa: E402

from hdlab.closed_class_lexicon import is_closed_class, lemma_verb  # noqa: E402
from hdlab.foundation_persistence import load_store, save_store  # noqa: E402
from hdlab.hd_fact_store import PIPELINE_UNKNOWN  # noqa: E402

SRC_STORE = os.path.join(REPO_ROOT, "data", "foundation", "reading_grounding_v1", "store")
OUT_DIR = os.path.join(REPO_ROOT, "data", "foundation_provenance_v1")
OUT_STORE = os.path.join(OUT_DIR, "store")

MEANING_RELATION = "GROUNDED_MEANING"
KNOWN_RELATION = "KNOWN_WORD"

# Corpora the loop actually read (mirrors notes/foundation_contents_audit_2026-08-13.md sec 5).
ONESTOP = os.path.join(REPO_ROOT, "data", "corpora", "onestop",
                       "Texts-SeparatedByReadingLevel")
BIO_TXT = os.path.join(REPO_ROOT, "data", "corpora", "textbook_concepts_biology", "cleaned",
                       "concepts_biology.clean.txt")

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
# Plain-alphabetic tokenizer. Chosen because it reproduces the audit's closed-class count (119)
# AND its UNKNOWN-too-rare count (11) exactly; an apostrophe/hyphen-tolerant tokenizer shifts 8
# lemmas below the 2-informative-occurrence floor and does NOT reconcile. A +5 residual on the
# PROPER bucket remains -- see `disagreements_with_audit` in quarantine_report.json.
_TOKEN = re.compile(r"[A-Za-z]+")


def _tag(source: str) -> str:
    if source == "seed_base_vocabulary":
        return "SEED_VOCABULARY"
    if source.startswith("reading:"):
        return "READING_GROUNDING"
    return PIPELINE_UNKNOWN


# --------------------------------------------------------------- proper-noun criterion
def _corpus_files() -> list:
    files = []
    for sub in ("Ele-Txt", "Int-Txt", "Adv-Txt"):
        d = os.path.join(ONESTOP, sub)
        files.extend(sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(".txt")))
    if os.path.isfile(BIO_TXT):
        files.append(BIO_TXT)
    return files


def build_proper_noun_table() -> dict:
    """lemma -> (n_informative, n_capitalized). Informative = a NON-sentence-initial token."""
    counts: dict = {}
    for path in _corpus_files():
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        for sent in _SENT_SPLIT.split(text):
            toks = _TOKEN.findall(sent)
            for i, tok in enumerate(toks):
                if i == 0:
                    continue                      # sentence-initial: capitalization uninformative
                lem = lemma_verb(tok.lower())
                n, c = counts.get(lem, (0, 0))
                counts[lem] = (n + 1, c + (1 if tok[0].isupper() else 0))
    return counts


def classify_proper(lemma: str, table: dict) -> str:
    """PROPER / COMMON / UNKNOWN. Conservative: <2 informative occurrences -> UNKNOWN."""
    n, c = table.get(lemma, (0, 0))
    if n < 2:
        return "UNKNOWN"
    return "PROPER" if c * 2 > n else "COMMON"


# ------------------------------------------------------------------------------ backfill
def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    store = load_store(SRC_STORE)
    src_vecs = [f.vec.clone() for f in store._facts]
    src_rows = [(f.subject, f.relation, f.obj, f.source, f.trust_sym, f.status)
                for f in store._facts]

    unknown_sources = Counter()
    for f in store._facts:
        f.pipeline = _tag(f.source)
        if f.pipeline == PIPELINE_UNKNOWN:
            unknown_sources[f.source] += 1

    save_store(store, OUT_STORE)

    # ---- verify-load: the new store must reload with the tags AND with the landed vectors
    re_store = load_store(OUT_STORE)
    assert len(re_store._facts) == len(store._facts), "row count changed on reload"
    for i, f in enumerate(re_store._facts):
        assert f.pipeline == store._facts[i].pipeline, f"pipeline lost on reload at fid {f.fid}"
        assert torch.equal(f.vec, src_vecs[i]), f"fact vec changed at fid {f.fid}"
        assert (f.subject, f.relation, f.obj, f.source, f.trust_sym, f.status) == src_rows[i], \
            f"plaintext row changed at fid {f.fid}"

    # ---- quarantine measurement (on the RELOADED store: measures what is actually on disk)
    table = build_proper_noun_table()
    per_pipeline: dict = {}
    for f in re_store._facts:
        b = per_pipeline.setdefault(f.pipeline, {
            "n_facts": 0, "n_known_word": 0, "n_grounded_meaning": 0,
            "n_tautology": 0, "n_nontautological": 0,
            "closed_class_object": 0, "proper_noun_object": 0, "noise_lower_bound_union": 0,
            "unclassified_object": 0, "unknown_too_rare_object": 0,
            "closed_class_subject": 0,
            "sources": Counter(), "statuses": Counter(),
            "_proper_objects": Counter(), "_closed_class_objects": Counter(),
        })
        b["n_facts"] += 1
        b["sources"][f.source] += 1
        b["statuses"][f.status] += 1
        if f.relation == KNOWN_RELATION:
            b["n_known_word"] += 1
            continue
        if f.relation != MEANING_RELATION:
            continue
        b["n_grounded_meaning"] += 1
        if f.subject == f.obj:
            b["n_tautology"] += 1
            continue
        b["n_nontautological"] += 1
        cc = is_closed_class(f.obj)
        pn = classify_proper(lemma_verb(f.obj.lower()), table)
        if cc:
            b["closed_class_object"] += 1
            b["_closed_class_objects"][f.obj] += 1
        if pn == "PROPER":
            b["proper_noun_object"] += 1
            b["_proper_objects"][f.obj] += 1
        if cc or pn == "PROPER":
            b["noise_lower_bound_union"] += 1
        elif pn == "UNKNOWN":
            b["unknown_too_rare_object"] += 1
        else:
            b["unclassified_object"] += 1
        if is_closed_class(f.subject):
            b["closed_class_subject"] += 1

    for b in per_pipeline.values():
        b["sources"] = dict(sorted(b["sources"].items()))
        b["statuses"] = dict(sorted(b["statuses"].items()))
        # full object lists so the buckets are re-checkable by hand, not just totals
        b["proper_noun_objects"] = dict(sorted(b.pop("_proper_objects").items()))
        b["closed_class_objects"] = dict(sorted(b.pop("_closed_class_objects").items()))

    audit = {  # notes/foundation_contents_audit_2026-08-13.md, whole-store figures
        "rows": 7966, "KNOWN_WORD": 4422, "GROUNDED_MEANING": 3544,
        "seed_KNOWN_WORD": 878, "tautologies": 2328,
        "closed_class_object": 119, "proper_noun_object": 265, "noise_lower_bound_union": 384,
        "nontautological": 1216, "unclassified": 821, "unknown_too_rare": 11,
        "closed_class_subject": 13,
    }
    tot = {
        "rows": len(re_store._facts),
        "KNOWN_WORD": sum(b["n_known_word"] for b in per_pipeline.values()),
        "GROUNDED_MEANING": sum(b["n_grounded_meaning"] for b in per_pipeline.values()),
        "seed_KNOWN_WORD": per_pipeline.get("SEED_VOCABULARY", {}).get("n_known_word", 0),
        "tautologies": sum(b["n_tautology"] for b in per_pipeline.values()),
        "closed_class_object": sum(b["closed_class_object"] for b in per_pipeline.values()),
        "proper_noun_object": sum(b["proper_noun_object"] for b in per_pipeline.values()),
        "noise_lower_bound_union": sum(b["noise_lower_bound_union"] for b in per_pipeline.values()),
        "nontautological": sum(b["n_nontautological"] for b in per_pipeline.values()),
        "unclassified": sum(b["unclassified_object"] for b in per_pipeline.values()),
        "unknown_too_rare": sum(b["unknown_too_rare_object"] for b in per_pipeline.values()),
        "closed_class_subject": sum(b["closed_class_subject"] for b in per_pipeline.values()),
    }
    disagreements = {k: {"audit": audit[k], "recomputed": tot[k]}
                     for k in sorted(audit) if audit[k] != tot[k]}

    report = {
        "generated_ts_iso": datetime.now(timezone.utc).isoformat(),
        "source_store": os.path.relpath(SRC_STORE, REPO_ROOT).replace(os.sep, "/"),
        "provenance_store": os.path.relpath(OUT_STORE, REPO_ROOT).replace(os.sep, "/"),
        "tagging_rule": {
            "seed_base_vocabulary": "SEED_VOCABULARY",
            "reading:*": "READING_GROUNDING",
            "_other": PIPELINE_UNKNOWN,
        },
        "hd_binding_scope": (
            "PLAINTEXT LEDGER ONLY for these backfilled rows: landed fact vectors are copied "
            "bit-identically and carry no PIPELINE binding, so recover_fact() returns "
            "UNKNOWN_LEGACY for every backfilled fact. Facts written with an explicit "
            "pipeline= from now on ARE HD-bound and glass-box recoverable."),
        "criteria": {
            "tautology": "subject == obj on a GROUNDED_MEANING row (exact string, store already lowercased/stemmed)",
            "closed_class": "hdlab.closed_class_lexicon.is_closed_class(obj)",
            "proper_noun": ("corpus-derived: majority of NON-sentence-initial occurrences "
                            "capitalized, >=2 informative occurrences, lemma_verb-normalized"),
            "proper_noun_corpus_files": len(_corpus_files()),
            "scope_note": ("closed-class / proper-noun buckets are measured on the "
                           "NON-TAUTOLOGICAL GROUNDED_MEANING rows only, matching the audit"),
        },
        "per_pipeline": {k: per_pipeline[k] for k in sorted(per_pipeline)},
        "totals_recomputed": tot,
        "audit_reference": audit,
        "audit_reference_doc": "notes/foundation_contents_audit_2026-08-13.md",
        "reconciles_with_audit": not disagreements,
        "disagreements_with_audit": disagreements,
        "unknown_legacy_sources": dict(sorted(unknown_sources.items())),
        "banked_from_definitional_extractor": 0,
        "out_of_scope_notes": [
            "Nothing banked; definitional-extractor facts are NOT in this store.",
            "No tautology was deleted, deduped or cleaned; measurement only.",
            "GROUNDED_MEANING cardinality left FUNCTIONAL (one meaning per word) -- a real "
            "brain-fidelity defect since polysemy is the normal case, but a separate build.",
        ],
    }
    _atomic_json(os.path.join(OUT_DIR, "quarantine_report.json"), report)

    manifest = {
        "generated_ts_iso": report["generated_ts_iso"],
        "format": "HDFactStore snapshot (store/ only); load with "
                  "hdlab.foundation_persistence.load_store",
        "not_a_full_foundation_snapshot": (
            "concept_space.npz / library_pending.* / manifest.json are NOT copied here, so "
            "load_foundation() will NOT read this directory. The canonical full snapshot "
            "remains data/foundation/reading_grounding_v1."),
        "source_store": report["source_store"],
        "n_facts": len(re_store._facts),
        "pipeline_counts": {k: per_pipeline[k]["n_facts"] for k in sorted(per_pipeline)},
        "source_store_sha256": _tree_sha(SRC_STORE),
        "provenance_store_sha256": _tree_sha(OUT_STORE),
    }
    _atomic_json(os.path.join(OUT_DIR, "backfill_manifest.json"), manifest)

    print(json.dumps({"per_pipeline_counts": manifest["pipeline_counts"],
                      "totals": tot, "disagreements": disagreements}, indent=2))
    return 0


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=True).encode("utf-8"))
    os.replace(tmp, path)
    with open(path, encoding="utf-8") as f:          # verify-load
        json.load(f)


def _tree_sha(root: str) -> dict:
    out = {}
    for dp, dn, fn in os.walk(root):
        dn.sort()
        for name in sorted(fn):
            p = os.path.join(dp, name)
            h = hashlib.sha256()
            with open(p, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            out[os.path.relpath(p, root).replace(os.sep, "/")] = h.hexdigest()
    return dict(sorted(out.items()))


if __name__ == "__main__":
    sys.exit(main())
