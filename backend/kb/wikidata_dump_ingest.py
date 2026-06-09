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
}


@dataclass
class IngestStats:
    bytes_read: int = 0
    lines_seen: int = 0
    triples_parsed: int = 0
    facts_added: int = 0
    skipped_literal: int = 0
    skipped_malformed: int = 0
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


def parse_line(line: str, labels: Optional[dict] = None) -> Optional[str]:
    """Parse one N-triples line into a fact string. Returns None if the line is malformed
    or refers to a literal value we don't render.

    With labels: 'Douglas Adams instance of human.'
    Without:    'Q42 instance of Q5.'
    """
    m = TRIPLE_RE.match(line.strip())
    if not m:
        return None
    subj_uri, pred_uri, obj_part = m.group(1), m.group(2), m.group(3)

    subj_q = extract_qcode(subj_uri)
    pred_p = extract_pcode(pred_uri)
    if subj_q is None or pred_p is None:
        return None

    # Subject label
    subj_label = labels.get(subj_q, subj_q) if labels else subj_q

    # Predicate label
    pred_label = PROPERTY_LABELS.get(pred_p, pred_p)

    # Object: URI (Q-code) or literal?
    obj_label: str
    if obj_part.startswith("<"):
        # URI object
        obj_match = re.match(r'^<([^>]+)>$', obj_part)
        if not obj_match:
            return None
        obj_uri = obj_match.group(1)
        obj_q = extract_qcode(obj_uri)
        if obj_q is None:
            return None
        obj_label = labels.get(obj_q, obj_q) if labels else obj_q
    elif obj_part.startswith('"'):
        # Literal "value"@lang OR "value"^^datatype
        lit_match = re.match(r'^"([^"]*)"(@[a-z-]+|\^\^<[^>]+>)?$', obj_part)
        if not lit_match:
            return None
        literal = lit_match.group(1)
        lang_tag = lit_match.group(2) or ""
        # Only keep English literals or untagged
        if lang_tag and lang_tag != "@en" and not lang_tag.startswith("^^"):
            return None
        if not literal or len(literal) > 200:
            return None
        obj_label = literal
    else:
        return None

    fact = f"{subj_label} {pred_label} {obj_label}."
    if 10 <= len(fact) <= 280:
        return fact
    return None


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


def run_ingest(
    dump_path: Path,
    n_triples: int = 50_000_000,
    output_dir: Path = Path("data/substrate_state/wikidata_truthy_50m"),
    batch_size: int = 64,
    checkpoint_every: int = 50_000,
    labels_path: Optional[Path] = None,
    encoder=None,
    progress_log: Optional[Path] = None,
) -> IngestStats:
    import numpy as np

    output_dir.mkdir(parents=True, exist_ok=True)
    facts_jsonl = output_dir / "facts.jsonl"
    keys_npy = output_dir / "keys.npy"
    stats_path = output_dir / "stats.json"

    if encoder is None:
        from backend.llm.bge_encoder import get_encoder
        encoder = get_encoder()

    labels = load_labels(labels_path)

    stats = IngestStats()
    t0 = time.perf_counter()
    facts_f = open(facts_jsonl, "a", encoding="utf-8")
    all_keys = []
    pending = []

    def flush(force=False):
        if not pending or (not force and len(pending) < batch_size):
            return
        t = time.perf_counter()
        vecs = encoder.encode(pending, batch_size=batch_size)
        stats.encode_wall_s += time.perf_counter() - t
        stats.encode_batches += 1
        all_keys.append(vecs)
        for s in pending:
            facts_f.write(json.dumps({"fact": s}) + "\n")
        stats.facts_added += len(pending)
        pending.clear()

    logger.info("opening dump: %s", dump_path)
    try:
        with bz2.open(dump_path, "rt", encoding="utf-8", errors="replace") as bz:
            for line in bz:
                stats.lines_seen += 1
                if stats.facts_added >= n_triples:
                    break
                fact = parse_line(line, labels=labels)
                if fact is None:
                    if '"' in line:
                        stats.skipped_literal += 1
                    else:
                        stats.skipped_malformed += 1
                    continue
                stats.triples_parsed += 1
                pending.append(fact)
                flush(force=False)

                if stats.lines_seen % checkpoint_every == 0:
                    flush(force=True)
                    stats.total_wall_s = time.perf_counter() - t0
                    logger.info("[ck] lines=%d facts=%d facts/s=%.1f",
                                stats.lines_seen, stats.facts_added,
                                stats.facts_added / max(0.001, stats.total_wall_s))
                    if progress_log:
                        progress_log.write_text(json.dumps(stats.as_dict(), indent=2))

        flush(force=True)
        if all_keys:
            np.save(keys_npy, np.concatenate(all_keys, axis=0))
            logger.info("wrote keys.npy")
    finally:
        facts_f.close()
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
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--checkpoint-every", type=int, default=50_000)
    p.add_argument("--labels", type=Path, default=None, help="optional Q-code -> label JSON")
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
    )


if __name__ == "__main__":
    main()
