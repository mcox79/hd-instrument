"""
EXTRACT-3 — Wikidata truthy N-triples dump ingest.

Source file: data/wikidata_dump/latest-truthy.nt.bz2 (~40 GB compressed)

Format: each line is `<subject_URI> <predicate_URI> <object_URI> .` (or object literal).

The truthy dump is best-rank statements only, in N-triples format with Q-codes for entities
and P-codes for properties. For human-readable facts, an optional labels file maps each
Q-code to its English label.

Output:
  data/substrate_state/wikidata_truthy_50m/
    facts.jsonl   one fact per line ("Q42 instance of Q5." OR "Douglas Adams instance of human.")
    keys.npy      (N, 1024) bge-large embeddings
    progress.json
    stats.json

Usage:
    .venv-demo\\Scripts\\python.exe -m backend.kb.wikidata_dump_ingest \\
        --dump data/wikidata_dump/latest-truthy.nt.bz2 \\
        --n-triples 50000000 \\
        --output-dir data/substrate_state/wikidata_truthy_50m
"""
from __future__ import annotations
import argparse
import bz2
import json
import logging
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# Top ~150 Wikidata properties hardcoded to readable labels (~80% of all statements
# in the truthy dump use one of these). Without this, every triple would read "P31"
# instead of "instance of".
PROPERTY_LABELS = {
    "P10": "video", "P14": "traffic sign", "P15": "route map",
    "P17": "country", "P18": "image", "P19": "place of birth",
    "P20": "place of death", "P21": "sex or gender", "P22": "father",
    "P25": "mother", "P26": "spouse", "P27": "country of citizenship",
    "P30": "continent", "P31": "instance of", "P35": "head of state",
    "P36": "capital", "P37": "official language", "P38": "currency",
    "P39": "position held", "P40": "child", "P50": "author",
    "P51": "audio", "P53": "family", "P54": "member of sports team",
    "P57": "director", "P58": "screenwriter", "P59": "constellation",
    "P61": "discoverer or inventor", "P65": "site of astronomical discovery",
    "P66": "ancestral home", "P69": "educated at", "P70": "biological variant of",
    "P75": "advocate", "P78": "top-level Internet domain", "P81": "connecting line",
    "P84": "architect", "P85": "anthem", "P86": "composer",
    "P87": "librettist", "P88": "commissioned by", "P91": "sexual orientation",
    "P92": "main regulatory text", "P94": "coat of arms image",
    "P97": "noble title", "P98": "editor", "P101": "field of work",
    "P102": "member of political party", "P103": "native language",
    "P105": "taxon rank", "P106": "occupation", "P108": "employer",
    "P109": "signature", "P110": "illustrator", "P111": "measured physical quantity",
    "P112": "founded by", "P113": "airline hub", "P114": "airline alliance",
    "P115": "home venue", "P117": "chemical structure", "P118": "league",
    "P119": "place of burial", "P121": "item operated", "P123": "publisher",
    "P126": "maintained by", "P127": "owned by", "P129": "physically interacts with",
    "P131": "located in the administrative territorial entity",
    "P135": "movement", "P136": "genre", "P137": "operator",
    "P138": "named after", "P140": "religion or worldview", "P141": "IUCN conservation status",
    "P143": "imported from Wikimedia project", "P144": "based on",
    "P149": "architectural style", "P150": "contains the administrative territorial entity",
    "P154": "logo image", "P155": "follows", "P156": "followed by",
    "P157": "killed by", "P158": "seal image", "P159": "headquarters location",
    "P161": "cast member", "P162": "producer", "P163": "flag image",
    "P166": "award received", "P167": "structure replaced by", "P169": "chief executive officer",
    "P170": "creator", "P171": "parent taxon", "P172": "ethnic group",
    "P175": "performer", "P176": "manufacturer", "P177": "crosses",
    "P178": "developer", "P179": "part of the series", "P180": "depicts",
    "P181": "taxon range map image", "P183": "endemic to", "P184": "doctoral advisor",
    "P185": "doctoral student", "P186": "made from material", "P189": "location of discovery",
    "P190": "twinned administrative body", "P193": "main building contractor",
    "P194": "legislative body", "P195": "collection", "P196": "minor planet group",
    "P197": "adjacent station", "P199": "business division", "P200": "lake inflows",
    "P201": "lake outflows", "P206": "located in or next to body of water",
    "P208": "executive body", "P209": "highest judicial authority",
    "P210": "party chief representative", "P212": "ISBN-13", "P213": "ISNI",
    "P214": "VIAF ID", "P217": "inventory number", "P218": "ISO 639-1 code",
    "P219": "ISO 639-2 code", "P220": "ISO 639-3 code", "P227": "GND ID",
    "P229": "IATA airline designator", "P230": "ICAO airline designator",
    "P233": "canonical SMILES", "P234": "InChI", "P235": "InChIKey",
    "P236": "ISSN", "P237": "coat of arms", "P238": "IATA airport code",
    "P239": "ICAO airport code", "P240": "FAA airport code",
    "P241": "military branch", "P242": "locator map image", "P244": "Library of Congress authority ID",
    "P246": "element symbol", "P249": "ticker symbol", "P263": "official residence",
    "P264": "record label", "P267": "ATC code", "P268": "Bibliotheque nationale de France ID",
    "P269": "IdRef ID", "P270": "CALIS ID", "P271": "CiNii ID",
    "P272": "production company", "P274": "chemical formula", "P275": "copyright license",
    "P276": "location", "P277": "programming language", "P279": "subclass of",
    "P281": "postal code", "P282": "writing system", "P286": "head coach",
    "P287": "designed by", "P289": "vessel class", "P291": "place of publication",
    "P296": "station code", "P297": "ISO 3166-1 alpha-2 code",
    "P298": "ISO 3166-1 alpha-3 code", "P299": "ISO 3166-1 numeric code",
    "P344": "director of photography", "P355": "subsidiary",
    "P364": "original language", "P366": "has use", "P371": "presenter",
    "P373": "Commons category", "P392": "stage name", "P395": "license plate code",
    "P407": "language of work or name", "P410": "military rank",
    "P411": "canonization status", "P412": "voice type", "P413": "position played on team",
    "P417": "patron saint", "P421": "located in time zone", "P425": "field of this occupation",
    "P427": "taxonomic type", "P437": "distribution format", "P439": "German municipality key",
    "P440": "German district key", "P443": "pronunciation audio",
    "P449": "original broadcaster", "P457": "founding charter",
    "P460": "said to be the same as", "P461": "opposite of", "P462": "color",
    "P463": "member of", "P466": "occupant", "P488": "chairperson",
    "P495": "country of origin", "P496": "ORCID iD",
    # Additional semantic properties (post-150)
    "P527": "has part", "P569": "date of birth", "P570": "date of death",
    "P571": "inception", "P576": "dissolved", "P577": "publication date",
    "P580": "start time", "P582": "end time", "P585": "point in time",
    "P657": "RTECS number", "P703": "found in taxon", "P710": "participant",
    "P735": "given name", "P734": "family name", "P800": "notable work",
    "P802": "student", "P840": "narrative location", "P859": "sponsor",
    "P937": "work location", "P941": "inspired by", "P1056": "product or material produced",
    "P1080": "from fictional universe", "P1303": "instrument",
    "P1365": "replaces", "P1366": "replaced by", "P1412": "language spoken",
    "P1416": "affiliation", "P1532": "country for sport", "P1559": "name in native language",
    "P1889": "different from", "P3373": "sibling",
}


# REC-3 from Research WIKIDATA_INGEST_OPTIMIZATION note (15:24 2026-06-09): allow-list
# of semantic properties. Drops ~75-80% of truthy dump (URL/identifier/admin/format noise).
SEMANTIC_KEEP_PROPERTIES = {
    "P17", "P19", "P20", "P21", "P22", "P25", "P26", "P27", "P30", "P31",
    "P35", "P36", "P37", "P38", "P39", "P40", "P50", "P54", "P57", "P58",
    "P61", "P66", "P69", "P78", "P84", "P86", "P88", "P91", "P101", "P102",
    "P103", "P106", "P108", "P110", "P112", "P115", "P118", "P119", "P121",
    "P123", "P127", "P131", "P135", "P136", "P137", "P138", "P140", "P144",
    "P149", "P150", "P155", "P156", "P157", "P159", "P161", "P162", "P166",
    "P169", "P170", "P171", "P172", "P175", "P176", "P177", "P178", "P179",
    "P180", "P183", "P184", "P185", "P186", "P189", "P194", "P195", "P197",
    "P199", "P200", "P201", "P206", "P208", "P209", "P241", "P263", "P264",
    "P272", "P275", "P276", "P277", "P279", "P286", "P287", "P289", "P291",
    "P344", "P355", "P361", "P364", "P366", "P371", "P407", "P410", "P411",
    "P412", "P413", "P417", "P421", "P427", "P437", "P440", "P443", "P449",
    "P461", "P462", "P463", "P466", "P488", "P495", "P527", "P569", "P570",
    "P571", "P576", "P577", "P580", "P582", "P585", "P657", "P703", "P710",
    "P735", "P734", "P800", "P802", "P840", "P859", "P937", "P941", "P1056",
    "P1080", "P1303", "P1365", "P1366", "P1412", "P1416", "P1532", "P1559",
    "P1889", "P3373",
}


@dataclass
class IngestStats:
    bytes_read: int = 0
    lines_seen: int = 0
    triples_parsed: int = 0
    facts_added: int = 0
    skipped_literal: int = 0
    skipped_malformed: int = 0
    skipped_filtered_predicate: int = 0  # REC-3: rejected by SEMANTIC_KEEP_PROPERTIES
    encode_batches: int = 0
    encode_wall_s: float = 0.0
    total_wall_s: float = 0.0

    def as_dict(self) -> dict:
        return {
            "bytes_read": self.bytes_read,
            "lines_seen": self.lines_seen,
            "triples_parsed": self.triples_parsed,
            "facts_added": self.facts_added,
            "skipped_literal": self.skipped_literal,
            "skipped_malformed": self.skipped_malformed,
            "skipped_filtered_predicate": self.skipped_filtered_predicate,
            "encode_batches": self.encode_batches,
            "encode_wall_s": round(self.encode_wall_s, 2),
            "total_wall_s": round(self.total_wall_s, 2),
            "facts_per_sec": round(self.facts_added / max(0.001, self.total_wall_s), 2),
        }


# N-triples regex: matches <subj_uri> <pred_uri> <obj_uri> . OR <subj_uri> <pred_uri> "literal" .
TRIPLE_RE = re.compile(
    r'^<([^>]+)>\s+<([^>]+)>\s+(.+?)\s*\.\s*$'
)


def extract_qcode(uri: str) -> Optional[str]:
    """Extract Q-code from <http://www.wikidata.org/entity/Q42> -> 'Q42'."""
    if "/entity/" in uri:
        return uri.rsplit("/entity/", 1)[-1]
    return None


def extract_pcode(uri: str) -> Optional[str]:
    """Extract P-code from <http://www.wikidata.org/prop/direct/P31> -> 'P31'."""
    if "/prop/direct/" in uri:
        return uri.rsplit("/prop/direct/", 1)[-1]
    if "/prop/" in uri:
        return uri.rsplit("/prop/", 1)[-1]
    return None


def parse_line(line: str, labels: Optional[dict] = None,
               apply_filter: bool = True) -> tuple:
    """Parse one N-triples line. Returns (fact, reason, triple) where:
      fact: human-readable fact string OR None
      reason: 'ok' / 'malformed' / 'no_codes' / 'filtered_predicate' / 'literal_rejected'
      triple: (subj_qcode, pred_pcode, obj_qcode_or_literal) raw codes OR None

    Stage A consumes `fact` for bge-large encoding to facts.jsonl + keys.npy.
    Stage C consumes `triple` for FHRR substrate encoding (per Research Q2 answer).
    """
    m = TRIPLE_RE.match(line.strip())
    if not m:
        return (None, "malformed", None)
    subj_uri, pred_uri, obj_part = m.group(1), m.group(2), m.group(3)

    subj_q = extract_qcode(subj_uri)
    pred_p = extract_pcode(pred_uri)
    if subj_q is None or pred_p is None:
        return (None, "no_codes", None)

    # REC-3 filter: drop predicates not in the semantic allow-list (skips ~75-80%
    # of truthy noise like URL props, external identifiers, format hints).
    if apply_filter and pred_p not in SEMANTIC_KEEP_PROPERTIES:
        return (None, "filtered_predicate", None)

    # Subject label
    subj_label = labels.get(subj_q, subj_q) if labels else subj_q

    # Predicate label
    pred_label = PROPERTY_LABELS.get(pred_p, pred_p)

    # Object: URI (Q-code) or literal?
    obj_label: str
    obj_raw: str  # Q-code OR literal string, for the Stage C triple
    if obj_part.startswith("<"):
        # URI object
        obj_match = re.match(r'^<([^>]+)>$', obj_part)
        if not obj_match:
            return (None, "malformed", None)
        obj_uri = obj_match.group(1)
        obj_q = extract_qcode(obj_uri)
        if obj_q is None:
            return (None, "no_codes", None)
        obj_label = labels.get(obj_q, obj_q) if labels else obj_q
        obj_raw = obj_q
    elif obj_part.startswith('"'):
        # Literal "value"@lang OR "value"^^datatype
        lit_match = re.match(r'^"([^"]*)"(@[a-z-]+|\^\^<[^>]+>)?$', obj_part)
        if not lit_match:
            return (None, "literal_rejected", None)
        literal = lit_match.group(1)
        lang_tag = lit_match.group(2) or ""
        # Only keep English literals or untagged
        if lang_tag and lang_tag != "@en" and not lang_tag.startswith("^^"):
            return (None, "literal_rejected", None)
        if not literal or len(literal) > 200:
            return (None, "literal_rejected", None)
        obj_label = literal
        obj_raw = literal
    else:
        return (None, "malformed", None)

    triple = (subj_q, pred_p, obj_raw)
    fact = f"{subj_label} {pred_label} {obj_label}."
    if 10 <= len(fact) <= 280:
        return (fact, "ok", triple)
    return (None, "literal_rejected", None)


def load_labels(labels_path: Optional[Path]) -> Optional[dict]:
    """Load a Q-code -> English label JSON map. Optional."""
    if labels_path is None or not labels_path.exists():
        return None
    log = logging.getLogger(__name__)
    log.info("loading labels from %s ...", labels_path)
    with open(labels_path, encoding="utf-8") as f:
        labels = json.load(f)
    log.info("loaded %d Q-code labels", len(labels))
    return labels


def _list_partial_keys(output_dir: Path):
    """Return sorted list of keys_partial_NNNNNN.npy paths (incremental save artifacts)."""
    return sorted(output_dir.glob("keys_partial_*.npy"))


def _count_lines(path: Path) -> int:
    """Count newlines in a text file. Used to count facts.jsonl / triples.jsonl rows."""
    if not path.exists():
        return 0
    n = 0
    with open(path, "rb") as f:
        for _ in f:
            n += 1
    return n


def _consolidate_partials_to_keys_npy(output_dir: Path, keys_npy: Path, delete_partials: bool = True):
    """Concatenate keys_partial_*.npy in order -> keys.npy. Optionally delete partials.

    Sanity check: final row count must equal facts.jsonl line count.
    """
    import numpy as np
    parts = _list_partial_keys(output_dir)
    if not parts:
        logger.warning("no partial keys to consolidate; keys.npy not written")
        return
    facts_n = _count_lines(output_dir / "facts.jsonl")
    arrs = [np.load(p) for p in parts]
    total_keys = sum(a.shape[0] for a in arrs)
    logger.info("consolidating %d partials -> keys.npy (%d total keys vs %d facts)",
                len(parts), total_keys, facts_n)
    if total_keys != facts_n:
        logger.warning("MISMATCH: keys=%d facts=%d (delta=%d); writing keys.npy anyway",
                       total_keys, facts_n, facts_n - total_keys)
    keys = np.concatenate(arrs, axis=0)
    np.save(keys_npy, keys)
    logger.info("wrote keys.npy: shape=%s", keys.shape)
    if delete_partials:
        for p in parts:
            p.unlink()
        logger.info("deleted %d partial files", len(parts))


def _read_facts_slice(facts_jsonl: Path, start: int, end: int):
    """Yield fact strings from facts_jsonl at line indices [start, end)."""
    with open(facts_jsonl, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i < start:
                continue
            if i >= end:
                return
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)["fact"]


def _resume_recovery(output_dir: Path, encoder, batch_size: int) -> int:
    """Re-encode facts.jsonl rows that have no corresponding keys saved.

    Returns the total number of rows now represented (partials_rows after recovery).
    This number equals min(facts_n, triples_n) ideally — both should match.
    """
    import numpy as np
    facts_jsonl = output_dir / "facts.jsonl"
    triples_jsonl = output_dir / "triples.jsonl"

    parts = _list_partial_keys(output_dir)
    partials_rows = sum(np.load(p, mmap_mode="r").shape[0] for p in parts)
    facts_n = _count_lines(facts_jsonl)
    triples_n = _count_lines(triples_jsonl)

    logger.info("resume: facts=%d triples=%d partials=%d (rows=%d)",
                facts_n, triples_n, len(parts), partials_rows)

    # If facts.jsonl and triples.jsonl drift (likely never, since flush() writes both
    # in the same tick), truncate to min so we resume cleanly.
    aligned_n = min(facts_n, triples_n)
    if aligned_n != facts_n or aligned_n != triples_n:
        logger.warning("facts/triples line count drift: trimming to %d", aligned_n)
        # Truncating jsonl files: read aligned_n lines + rewrite (small files in practice)
        def _trim(path, keep_n):
            lines = []
            with open(path, encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if i >= keep_n:
                        break
                    lines.append(line)
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(lines)
        _trim(facts_jsonl, aligned_n)
        _trim(triples_jsonl, aligned_n)

    if partials_rows >= aligned_n:
        # Partials are ahead of jsonl; truncate the extra (impossible in practice but safe)
        logger.info("partials already cover all aligned rows; no recovery encode needed")
        return aligned_n

    gap = aligned_n - partials_rows
    logger.info("recovery encode: %d facts to re-encode (partials=%d aligned=%d)",
                gap, partials_rows, aligned_n)
    t0 = time.perf_counter()
    pending = []
    parts_count = len(parts)
    encoded_rows = 0
    for fact in _read_facts_slice(facts_jsonl, partials_rows, aligned_n):
        pending.append(fact)
        if len(pending) >= batch_size * 16:  # flush every ~4K encodes
            vecs = encoder.encode(pending, batch_size=batch_size)
            partial_path = output_dir / f"keys_partial_{parts_count:06d}.npy"
            np.save(partial_path, vecs)
            parts_count += 1
            encoded_rows += len(pending)
            logger.info("recovery: encoded %d / %d (%.1f%%); wrote %s",
                        encoded_rows, gap, 100.0 * encoded_rows / max(1, gap),
                        partial_path.name)
            pending.clear()
    if pending:
        vecs = encoder.encode(pending, batch_size=batch_size)
        partial_path = output_dir / f"keys_partial_{parts_count:06d}.npy"
        np.save(partial_path, vecs)
        parts_count += 1
        encoded_rows += len(pending)
        logger.info("recovery: encoded final %d -> %s", len(pending), partial_path.name)
    logger.info("recovery encode DONE: %d facts in %.0fs (%.1f facts/s)",
                encoded_rows, time.perf_counter() - t0,
                encoded_rows / max(0.001, time.perf_counter() - t0))
    return aligned_n


def run_ingest(
    dump_path: Path,
    n_triples: int = 50_000_000,
    output_dir: Path = Path("data/substrate_state/wikidata_truthy_50m"),
    batch_size: int = 64,
    checkpoint_every: int = 50_000,
    labels_path: Optional[Path] = None,
    encoder=None,
    progress_log: Optional[Path] = None,
    resume: bool = False,
) -> IngestStats:
    import numpy as np

    output_dir.mkdir(parents=True, exist_ok=True)
    facts_jsonl = output_dir / "facts.jsonl"
    triples_jsonl = output_dir / "triples.jsonl"  # Stage C source-of-truth (per Research Q2)
    keys_npy = output_dir / "keys.npy"
    stats_path = output_dir / "stats.json"

    if encoder is None:
        from backend.llm.bge_encoder import get_encoder
        encoder = get_encoder()

    labels = load_labels(labels_path)

    # Resume recovery: re-encode any facts.jsonl rows that have no key (crashed mid-run).
    # Establishes the resume_skip_count = number of parsed-triples we should fast-forward
    # past in the bz2 stream.
    resume_skip_count = 0
    if resume:
        logger.info("RESUME mode: checking existing state at %s", output_dir)
        resume_skip_count = _resume_recovery(output_dir, encoder, batch_size)
        logger.info("RESUME: will skip %d parsed-triples in bz2 stream", resume_skip_count)

    stats = IngestStats()
    t0 = time.perf_counter()
    facts_f = open(facts_jsonl, "a", encoding="utf-8")
    triples_f = open(triples_jsonl, "a", encoding="utf-8")
    all_keys = []           # in-flight buffer; flushed to partial files at checkpoints
    pending = []            # list of fact strings (Stage A bge-large encoding)
    pending_triples = []    # parallel list of (subj_q, pred_p, obj_raw) tuples

    parts_count = len(_list_partial_keys(output_dir))  # next partial index

    def _save_partial():
        """Save accumulated all_keys to a new partial file; clear the buffer."""
        nonlocal parts_count
        if not all_keys:
            return
        import numpy as _np
        keys = _np.concatenate(all_keys, axis=0)
        partial_path = output_dir / f"keys_partial_{parts_count:06d}.npy"
        _np.save(partial_path, keys)
        parts_count += 1
        all_keys.clear()
        logger.info("saved partial %s (rows=%d)", partial_path.name, keys.shape[0])

    def flush(force=False):
        if not pending or (not force and len(pending) < batch_size):
            return
        t = time.perf_counter()
        vecs = encoder.encode(pending, batch_size=batch_size)
        stats.encode_wall_s += time.perf_counter() - t
        stats.encode_batches += 1
        all_keys.append(vecs)
        for s, tri in zip(pending, pending_triples):
            facts_f.write(json.dumps({"fact": s}) + "\n")
            triples_f.write(json.dumps({"s": tri[0], "p": tri[1], "o": tri[2]}) + "\n")
        stats.facts_added += len(pending)
        pending.clear()
        pending_triples.clear()

    logger.info("opening dump: %s", dump_path)
    try:
        with bz2.open(dump_path, "rt", encoding="utf-8", errors="replace") as bz:
            skipped_for_resume = 0
            for line in bz:
                stats.lines_seen += 1
                if stats.facts_added >= n_triples:
                    break
                fact, reason, triple = parse_line(line, labels=labels)
                if fact is None:
                    if reason == "literal_rejected":
                        stats.skipped_literal += 1
                    elif reason == "filtered_predicate":
                        stats.skipped_filtered_predicate += 1
                    else:
                        stats.skipped_malformed += 1
                    continue
                stats.triples_parsed += 1

                # Resume fast-forward: parse but discard the first N already-seen triples
                if skipped_for_resume < resume_skip_count:
                    skipped_for_resume += 1
                    if skipped_for_resume % 100_000 == 0:
                        logger.info("resume skip: %d / %d", skipped_for_resume, resume_skip_count)
                    continue

                pending.append(fact)
                pending_triples.append(triple)
                flush(force=False)

                if stats.lines_seen % checkpoint_every == 0:
                    flush(force=True)
                    # Save incremental partial so future crashes don't lose work
                    _save_partial()
                    stats.total_wall_s = time.perf_counter() - t0
                    logger.info("[ck] lines=%d facts=%d facts/s=%.1f",
                                stats.lines_seen, stats.facts_added,
                                stats.facts_added / max(0.001, stats.total_wall_s))
                    if progress_log:
                        progress_log.write_text(json.dumps(stats.as_dict(), indent=2))

        flush(force=True)
        _save_partial()
        # Final consolidation: concat all partials -> keys.npy
        _consolidate_partials_to_keys_npy(output_dir, keys_npy, delete_partials=True)
    finally:
        facts_f.close()
        triples_f.close()
        stats.total_wall_s = time.perf_counter() - t0
        stats_path.write_text(json.dumps(stats.as_dict(), indent=2))
        if progress_log:
            progress_log.write_text(json.dumps(stats.as_dict(), indent=2))
        logger.info("DONE: %s", stats.as_dict())
    return stats


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dump", type=Path, default=Path("data/wikidata_dump/latest-truthy.nt.bz2"))
    p.add_argument("--n-triples", type=int, default=50_000_000)
    p.add_argument("--output-dir", type=Path, default=Path("data/substrate_state/wikidata_truthy_50m"))
    # Per Research PRIORITY_RANKING_2026-06-09 P1 E2: increase to 256 for ~1.5-2x throughput
    # (vs prior 64/128). Memory cost: ~512 sentences buffered in encoder = ~500 MB more.
    p.add_argument("--batch-size", type=int, default=256)
    p.add_argument("--checkpoint-every", type=int, default=50_000)
    p.add_argument("--labels", type=Path, default=None, help="optional Q-code -> label JSON")
    p.add_argument("--resume", action="store_true",
                   help="resume from existing facts.jsonl + triples.jsonl + keys_partial_*.npy "
                        "by re-encoding any gap, then skipping past already-parsed triples in the "
                        "bz2 stream. Use after a runner crash.")
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    progress_log = args.output_dir / "progress.json"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_ingest(
        dump_path=args.dump,
        n_triples=args.n_triples,
        output_dir=args.output_dir,
        batch_size=args.batch_size,
        checkpoint_every=args.checkpoint_every,
        labels_path=args.labels,
        progress_log=progress_log,
        resume=args.resume,
    )


if __name__ == "__main__":
    main()
