"""Bio/neuro source fetchers + parsers for Director-KB ingest (v1; 2026-06-26).

USER 2026-06-26: "more biology (particularly neuro)" - extend Director-KB with
structured biological knowledge aligned with cortex content-extraction work.

This module adds support for 3 bio sources, all reading FROM A LOCAL CACHE
(deterministic; principle 2). Network access happens ONLY in the
`fetch_<source>()` helpers, which write to data/bio_kb_cache/<source>/ and
are idempotent (skip if cached).

Sources:
  1. Gene Ontology (GO) - .obo file from current.geneontology.org. Hierarchical
     functional ontology (~45k terms; biological_process / molecular_function /
     cellular_component). Relations: IS_A, PART_OF, REGULATES,
     POSITIVELY_REGULATES, NEGATIVELY_REGULATES, OCCURS_IN.
  2. KEGG pathways - REST API (rest.kegg.jp). Metabolic + signaling pathways.
     We fetch the human (hsa) pathway list + per-pathway KGML (XML). Entities:
     PATHWAY, REACTION, COMPOUND, ENZYME, GENE. Relations: STEP_OF, CATALYZES,
     REACTANT_OF, PRODUCT_OF, REGULATES_PATHWAY. Throttle: 1.0s between calls.
  3. NeuroLex / NIF - SciCrunch's NIF-Ontology TTL files on GitHub raw. Brain
     regions, cell types, neurotransmitters, receptors. Relations: PROJECTS_TO,
     RECEIVES_FROM, CONTAINS_CELL_TYPE, EXPRESSES_NEUROTRANSMITTER, BINDS_TO,
     IS_A, PART_OF.

Parsers return list[dict] triples in the same shape the rest of director_kb.py
expects: {"s": <name>, "p": <relation>, "o": <name>, "extra_tags": {...}}.

Determinism contract: given the same on-disk cache bytes, parse_* functions
produce byte-equal triple lists (iteration is deterministic over sorted file
lists + line order). Network fetch is NOT in the ingest path.

ASCII-only. No emojis. No em-dashes.
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable

USER_AGENT = "hd-instrument-research/1.0 (substrate Director-KB ingest; contact marshall.cox@gmail.com)"

# ---------- helpers ----------


def _http_get(url: str, timeout_s: int = 60) -> bytes:
    """HTTP GET with User-Agent + timeout; returns raw bytes. Caller handles errors."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
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
    return repo_root / "data" / "bio_kb_cache"


# =====================================================================
# Gene Ontology (.obo)
# =====================================================================

GO_OBO_URL = "https://current.geneontology.org/ontology/go-basic.obo"
GO_CACHE_FILE = "go-basic.obo"
GO_NAMESPACE_TO_TAG = {
    "biological_process": "GO_BIOLOGICAL_PROCESS",
    "molecular_function": "GO_MOLECULAR_FUNCTION",
    "cellular_component": "GO_CELLULAR_COMPONENT",
}
# OBO relationship typedefs -> our schema relation names.
GO_REL_MAP = {
    "is_a": "IS_A",
    "part_of": "PART_OF",
    "regulates": "REGULATES",
    "positively_regulates": "POSITIVELY_REGULATES",
    "negatively_regulates": "NEGATIVELY_REGULATES",
    "occurs_in": "OCCURS_IN",
    "happens_during": "OCCURS_IN",
}


def fetch_gene_ontology(repo_root: Path, force: bool = False) -> Path:
    """Idempotent fetch; returns path to cached .obo file."""
    out = _cache_root(repo_root) / "go" / GO_CACHE_FILE
    if out.exists() and not force:
        return out
    print(f"[bio_sources] fetching GO from {GO_OBO_URL}", flush=True)
    data = _http_get(GO_OBO_URL, timeout_s=120)
    _atomic_write_bytes(out, data)
    print(f"[bio_sources] GO cached at {out} ({len(data)} bytes)", flush=True)
    return out


def parse_gene_ontology(obo_path: Path, max_terms: int | None = None) -> list[dict]:
    """Parse .obo file -> list of triple dicts.

    Emits per [Term] block:
      (term_id, IS_A_NAMESPACE, <namespace_tag>)  -- e.g. GO:0001 -> GO_BIOLOGICAL_PROCESS
      (term_id, NAMED, <name>)
      (term_id, IS_A, <parent_id>) for each is_a line
      (term_id, <rel>, <target_id>) for each relationship line
      (<name_lowercased>, ALIAS_OF, <term_id>) so name-based lookup works (+
        the encoder can hit either id or name).

    Skips [Term] blocks with is_obsolete: true. Deterministic: iterates blocks
    in file order; per-block emits relations in (is_a, then relationship lines)
    file order.
    """
    out: list[dict] = []
    text = obo_path.read_text(encoding="utf-8", errors="replace")

    # Split on [Term] stanza boundary; first chunk is the header.
    chunks = text.split("\n[Term]\n")
    # First chunk includes the header up to (but not including) the first [Term] marker.
    # Drop it; iterate stanzas.
    if not chunks:
        return out
    n_emitted_terms = 0
    for chunk in chunks[1:]:
        if max_terms is not None and n_emitted_terms >= max_terms:
            break
        block_lines = chunk.split("\n")
        term_id = None
        name = None
        namespace = None
        is_obsolete = False
        is_a_list: list[str] = []
        rel_list: list[tuple[str, str]] = []
        alt_id_list: list[str] = []
        for line in block_lines:
            if not line or line.startswith("[") or line.startswith("!"):
                # next stanza boundary or comment; stop processing this block
                if line.startswith("["):
                    break
                continue
            if ": " not in line:
                continue
            key, _, value = line.partition(": ")
            key = key.strip()
            value = value.strip()
            if key == "id" and term_id is None:
                term_id = value
            elif key == "name":
                name = value
            elif key == "namespace":
                namespace = value
            elif key == "is_obsolete" and value.lower() == "true":
                is_obsolete = True
            elif key == "alt_id":
                alt_id_list.append(value)
            elif key == "is_a":
                # "is_a: GO:0000001 ! cell" -> take only the id part
                parent = value.split(" ! ", 1)[0].strip()
                if parent:
                    is_a_list.append(parent)
            elif key == "relationship":
                # "relationship: part_of GO:0000001 ! cell"
                parts = value.split(" ! ", 1)[0].split(maxsplit=1)
                if len(parts) == 2:
                    rel_name, target = parts[0], parts[1].strip()
                    if rel_name in GO_REL_MAP and target:
                        rel_list.append((GO_REL_MAP[rel_name], target))
        if not term_id or is_obsolete:
            continue
        n_emitted_terms += 1
        # Emit namespace tag binding (lets queries reach the term via namespace)
        if namespace and namespace in GO_NAMESPACE_TO_TAG:
            out.append({
                "s": term_id, "p": "IS_A_NAMESPACE",
                "o": GO_NAMESPACE_TO_TAG[namespace],
                "extra_tags": {"go_namespace": namespace},
            })
        if name:
            out.append({
                "s": term_id, "p": "NAMED", "o": name,
                "extra_tags": {"go_name": name},
            })
            # Also reverse-bind name -> term_id under ALIAS_OF so a query for
            # the human-readable name can resolve to the canonical id.
            out.append({
                "s": name, "p": "ALIAS_OF", "o": term_id,
                "extra_tags": {},
            })
        for parent in is_a_list:
            out.append({"s": term_id, "p": "IS_A", "o": parent, "extra_tags": {}})
        for rel_name, target in rel_list:
            out.append({"s": term_id, "p": rel_name, "o": target, "extra_tags": {}})
        for alt in alt_id_list:
            out.append({"s": alt, "p": "ALIAS_OF", "o": term_id, "extra_tags": {}})
    return out


# =====================================================================
# KEGG pathways (REST + KGML)
# =====================================================================

KEGG_BASE = "https://rest.kegg.jp"
KEGG_THROTTLE_S = 1.0  # politeness per KEGG terms

# Neural + signaling pathway pattern: KEGG's hsa04* covers signaling + neural,
# hsa05* covers human diseases (skip), hsa00* metabolic.
# Default selection per handoff: focus on neural + signaling.
KEGG_DEFAULT_FOCUS_PATTERNS = (
    re.compile(r"^hsa04\d{3}$"),   # signal transduction + neural
)


def fetch_kegg_pathway_list(repo_root: Path, force: bool = False) -> Path:
    """Fetch hsa pathway list; returns path to cached list file."""
    out = _cache_root(repo_root) / "kegg" / "pathway_list_hsa.tsv"
    if out.exists() and not force:
        return out
    print(f"[bio_sources] fetching KEGG pathway list", flush=True)
    data = _http_get(f"{KEGG_BASE}/list/pathway/hsa", timeout_s=60)
    _atomic_write_bytes(out, data)
    return out


def fetch_kegg_pathway_kgml(
    repo_root: Path,
    pathway_id: str,
    force: bool = False,
    throttle_s: float = KEGG_THROTTLE_S,
) -> Path | None:
    """Fetch one pathway's KGML XML; returns path or None if 404."""
    out = _cache_root(repo_root) / "kegg" / f"{pathway_id}.kgml"
    if out.exists() and not force:
        return out
    time.sleep(throttle_s)
    try:
        data = _http_get(f"{KEGG_BASE}/get/{pathway_id}/kgml", timeout_s=30)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    if len(data) < 100:
        # Empty or sentinel response; KEGG returns empty body for non-KGML pathways
        return None
    _atomic_write_bytes(out, data)
    return out


def fetch_kegg_pathways(
    repo_root: Path,
    max_pathways: int | None = 50,
    focus_patterns: Iterable[re.Pattern] = KEGG_DEFAULT_FOCUS_PATTERNS,
    force: bool = False,
) -> list[Path]:
    """Fetch focus subset of KEGG pathways (KGML XML). Returns list of cached paths."""
    list_path = fetch_kegg_pathway_list(repo_root, force=force)
    rows = []
    for line in list_path.read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        pid, pname = parts[0], parts[1]
        if any(pat.match(pid) for pat in focus_patterns):
            rows.append((pid, pname))
    rows.sort()  # deterministic
    if max_pathways is not None:
        rows = rows[:max_pathways]
    print(f"[bio_sources] fetching {len(rows)} KEGG pathways (throttle={KEGG_THROTTLE_S}s)",
          flush=True)
    out_paths: list[Path] = []
    for i, (pid, _) in enumerate(rows):
        p = fetch_kegg_pathway_kgml(repo_root, pid, force=force)
        if p is not None:
            out_paths.append(p)
        if (i + 1) % 10 == 0:
            print(f"[bio_sources]   fetched {i+1}/{len(rows)} KEGG pathways", flush=True)
    return out_paths


# KGML parser (no xml.etree -> well, std lib OK; deterministic enough)
def parse_kegg_kgml(kgml_path: Path) -> list[dict]:
    """Parse one KEGG pathway KGML XML -> triples.

    KGML elements we extract:
      <pathway name="path:hsaNNNN" title="..."> -> pathway anchor
      <entry id=... name="hsa:NNN ..." type="gene"> -> GENE entities
      <entry id=... name="cpd:NNN ..." type="compound"> -> COMPOUND entities
      <entry id=... name="ec:N.N.N.N ..." type="enzyme"> -> ENZYME entities
      <reaction id=... name="rn:NNN" type="reversible|irreversible"> with
        <substrate id=... name="cpd:NNN"/> and <product id=... name="cpd:NNN"/>
      <relation entry1=... entry2=... type="..."> for gene/protein relations
    """
    import xml.etree.ElementTree as ET
    out: list[dict] = []
    try:
        tree = ET.parse(kgml_path)
    except ET.ParseError:
        return out
    root = tree.getroot()
    # Pathway anchor
    pathway_name = root.get("name", "").replace("path:", "")
    pathway_title = root.get("title", "")
    if not pathway_name:
        return out
    pathway_anchor = f"PATHWAY:{pathway_name}"
    out.append({
        "s": pathway_anchor, "p": "IS_A_NAMESPACE", "o": "KEGG_PATHWAY",
        "extra_tags": {"kegg_pathway_id": pathway_name},
    })
    if pathway_title:
        out.append({
            "s": pathway_anchor, "p": "NAMED", "o": pathway_title,
            "extra_tags": {"kegg_pathway_title": pathway_title},
        })
        # Reverse name -> anchor for human-readable query
        out.append({
            "s": pathway_title, "p": "ALIAS_OF", "o": pathway_anchor,
            "extra_tags": {},
        })

    # entry table: KGML uses internal numeric ids; we map them to KEGG names
    entry_id_to_kegg: dict[str, list[str]] = {}
    entry_id_to_type: dict[str, str] = {}
    for entry in root.findall("entry"):
        eid = entry.get("id")
        etype = entry.get("type", "")
        ename = entry.get("name", "")
        if not eid or not ename:
            continue
        kegg_names = ename.split()
        entry_id_to_kegg[eid] = kegg_names
        entry_id_to_type[eid] = etype
        for kname in kegg_names:
            ent_anchor = kname  # e.g. "hsa:1234" or "cpd:C00001" or "ec:1.1.1.1"
            # Bind entity to pathway via STEP_OF
            out.append({
                "s": ent_anchor, "p": "STEP_OF", "o": pathway_anchor,
                "extra_tags": {"kegg_entry_type": etype},
            })

    # reactions
    for reaction in root.findall("reaction"):
        rid = reaction.get("id")
        rname = reaction.get("name", "")
        rtype = reaction.get("type", "")
        if not rname:
            continue
        for rn in rname.split():
            rxn_anchor = rn  # e.g. "rn:R00001"
            out.append({
                "s": rxn_anchor, "p": "STEP_OF", "o": pathway_anchor,
                "extra_tags": {"kegg_reaction_type": rtype},
            })
            # substrates -> REACTANT_OF
            for sub in reaction.findall("substrate"):
                sname = sub.get("name", "")
                for sn in sname.split():
                    out.append({
                        "s": sn, "p": "REACTANT_OF", "o": rxn_anchor,
                        "extra_tags": {},
                    })
            for prod in reaction.findall("product"):
                pname = prod.get("name", "")
                for pn in pname.split():
                    out.append({
                        "s": pn, "p": "PRODUCT_OF", "o": rxn_anchor,
                        "extra_tags": {},
                    })
            # Enzyme catalyzes (entry id in reaction -> kegg names)
            if rid in entry_id_to_kegg and entry_id_to_type.get(rid) == "enzyme":
                for enz in entry_id_to_kegg[rid]:
                    out.append({
                        "s": enz, "p": "CATALYZES", "o": rxn_anchor,
                        "extra_tags": {},
                    })

    # relations: gene-gene or protein-protein interactions within pathway
    for rel in root.findall("relation"):
        e1 = rel.get("entry1")
        e2 = rel.get("entry2")
        rtype = rel.get("type", "")
        if not e1 or not e2 or e1 not in entry_id_to_kegg or e2 not in entry_id_to_kegg:
            continue
        # Use first kegg name in each for the triple
        a_names = entry_id_to_kegg[e1]
        b_names = entry_id_to_kegg[e2]
        if not a_names or not b_names:
            continue
        a, b = a_names[0], b_names[0]
        out.append({
            "s": a, "p": "REGULATES_PATHWAY", "o": b,
            "extra_tags": {"kegg_relation_type": rtype, "pathway_context": pathway_name},
        })
    return out


# =====================================================================
# NeuroLex / NIF (curated TTL files)
# =====================================================================

# NIF-Ontology subset URLs (raw GitHub; SciCrunch repo); each file is small
# enough (<5MB) to fetch into cache.
NIF_TTL_FILES = {
    "NIF-Cell.ttl": (
        "https://raw.githubusercontent.com/SciCrunch/NIF-Ontology/master/ttl/NIF-Cell.ttl"
    ),
    "NIF-Neuron-NT-Bridge.ttl": (
        "https://raw.githubusercontent.com/SciCrunch/NIF-Ontology/master/ttl/bridge/"
        "NIF-Neuron-NT-Bridge.ttl"
    ),
    "NIF-GrossAnatomy.ttl": (
        "https://raw.githubusercontent.com/SciCrunch/NIF-Ontology/master/ttl/"
        "NIF-GrossAnatomy.ttl"
    ),
    "NIF-Molecule.ttl": (
        "https://raw.githubusercontent.com/SciCrunch/NIF-Ontology/master/ttl/"
        "NIF-Molecule.ttl"
    ),
}

# A simple curated synthetic fallback shipped with the cell - guarantees
# determinism even if all SciCrunch URLs go offline. Loaded if cache is empty
# after fetch. Each row: (s, p, o).
NIF_CURATED_FALLBACK_TRIPLES = [
    # Brain regions hierarchy
    ("BRAIN", "IS_A_NAMESPACE", "BRAIN_REGION"),
    ("CEREBRUM", "PART_OF", "BRAIN"),
    ("CEREBELLUM", "PART_OF", "BRAIN"),
    ("BRAINSTEM", "PART_OF", "BRAIN"),
    ("CEREBRAL_CORTEX", "PART_OF", "CEREBRUM"),
    ("HIPPOCAMPUS", "PART_OF", "CEREBRUM"),
    ("HIPPOCAMPUS_CA1", "PART_OF", "HIPPOCAMPUS"),
    ("HIPPOCAMPUS_CA2", "PART_OF", "HIPPOCAMPUS"),
    ("HIPPOCAMPUS_CA3", "PART_OF", "HIPPOCAMPUS"),
    ("DENTATE_GYRUS", "PART_OF", "HIPPOCAMPUS"),
    ("THALAMUS", "PART_OF", "CEREBRUM"),
    ("AMYGDALA", "PART_OF", "CEREBRUM"),
    ("STRIATUM", "PART_OF", "CEREBRUM"),
    ("PREFRONTAL_CORTEX", "PART_OF", "CEREBRAL_CORTEX"),
    ("MOTOR_CORTEX", "PART_OF", "CEREBRAL_CORTEX"),
    ("VISUAL_CORTEX", "PART_OF", "CEREBRAL_CORTEX"),
    ("AUDITORY_CORTEX", "PART_OF", "CEREBRAL_CORTEX"),
    ("SOMATOSENSORY_CORTEX", "PART_OF", "CEREBRAL_CORTEX"),
    # Cell types in regions
    ("PYRAMIDAL_NEURON", "CONTAINS_CELL_TYPE", "HIPPOCAMPUS_CA3"),
    ("PYRAMIDAL_NEURON", "CONTAINS_CELL_TYPE", "HIPPOCAMPUS_CA1"),
    ("PYRAMIDAL_NEURON", "CONTAINS_CELL_TYPE", "CEREBRAL_CORTEX"),
    ("GRANULE_CELL", "CONTAINS_CELL_TYPE", "DENTATE_GYRUS"),
    ("GRANULE_CELL", "CONTAINS_CELL_TYPE", "CEREBELLUM"),
    ("PURKINJE_CELL", "CONTAINS_CELL_TYPE", "CEREBELLUM"),
    ("BASKET_CELL", "CONTAINS_CELL_TYPE", "HIPPOCAMPUS"),
    ("INTERNEURON", "CONTAINS_CELL_TYPE", "CEREBRAL_CORTEX"),
    ("DOPAMINERGIC_NEURON", "CONTAINS_CELL_TYPE", "STRIATUM"),
    # Projections
    ("HIPPOCAMPUS_CA3", "PROJECTS_TO", "HIPPOCAMPUS_CA1"),
    ("DENTATE_GYRUS", "PROJECTS_TO", "HIPPOCAMPUS_CA3"),
    ("ENTORHINAL_CORTEX", "PROJECTS_TO", "DENTATE_GYRUS"),
    ("PREFRONTAL_CORTEX", "PROJECTS_TO", "STRIATUM"),
    ("THALAMUS", "PROJECTS_TO", "CEREBRAL_CORTEX"),
    ("CEREBRAL_CORTEX", "PROJECTS_TO", "THALAMUS"),
    ("HIPPOCAMPUS_CA1", "RECEIVES_FROM", "HIPPOCAMPUS_CA3"),
    # Neurotransmitters
    ("GLUTAMATE", "IS_A_NAMESPACE", "NEUROTRANSMITTER"),
    ("GABA", "IS_A_NAMESPACE", "NEUROTRANSMITTER"),
    ("DOPAMINE", "IS_A_NAMESPACE", "NEUROTRANSMITTER"),
    ("SEROTONIN", "IS_A_NAMESPACE", "NEUROTRANSMITTER"),
    ("ACETYLCHOLINE", "IS_A_NAMESPACE", "NEUROTRANSMITTER"),
    ("NOREPINEPHRINE", "IS_A_NAMESPACE", "NEUROTRANSMITTER"),
    ("PYRAMIDAL_NEURON", "EXPRESSES_NEUROTRANSMITTER", "GLUTAMATE"),
    ("INTERNEURON", "EXPRESSES_NEUROTRANSMITTER", "GABA"),
    ("DOPAMINERGIC_NEURON", "EXPRESSES_NEUROTRANSMITTER", "DOPAMINE"),
    ("BASKET_CELL", "EXPRESSES_NEUROTRANSMITTER", "GABA"),
    # Receptors
    ("NMDA_RECEPTOR", "BINDS_TO", "GLUTAMATE"),
    ("AMPA_RECEPTOR", "BINDS_TO", "GLUTAMATE"),
    ("KAINATE_RECEPTOR", "BINDS_TO", "GLUTAMATE"),
    ("GABA_A_RECEPTOR", "BINDS_TO", "GABA"),
    ("GABA_B_RECEPTOR", "BINDS_TO", "GABA"),
    ("D1_RECEPTOR", "BINDS_TO", "DOPAMINE"),
    ("D2_RECEPTOR", "BINDS_TO", "DOPAMINE"),
    ("5HT1A_RECEPTOR", "BINDS_TO", "SEROTONIN"),
    ("MUSCARINIC_RECEPTOR", "BINDS_TO", "ACETYLCHOLINE"),
    ("NICOTINIC_RECEPTOR", "BINDS_TO", "ACETYLCHOLINE"),
]


def fetch_nif(repo_root: Path, force: bool = False) -> list[Path]:
    """Fetch NIF-Ontology TTL subset. Returns list of cached files (skipped if 404)."""
    out_paths: list[Path] = []
    for fname, url in NIF_TTL_FILES.items():
        out = _cache_root(repo_root) / "neurolex" / fname
        if out.exists() and not force:
            out_paths.append(out)
            continue
        try:
            print(f"[bio_sources] fetching NIF {fname}", flush=True)
            data = _http_get(url, timeout_s=60)
            _atomic_write_bytes(out, data)
            out_paths.append(out)
        except urllib.error.HTTPError as e:
            print(f"[bio_sources] WARN: NIF {fname} fetch failed: {e}", flush=True)
    # Always write curated fallback for guaranteed coverage of basic neuro queries
    curated_path = _cache_root(repo_root) / "neurolex" / "_curated_fallback.tsv"
    if not curated_path.exists() or force:
        lines = ["s\tp\to"] + [f"{s}\t{p}\t{o}" for s, p, o in NIF_CURATED_FALLBACK_TRIPLES]
        _atomic_write_text(curated_path, "\n".join(lines) + "\n")
    out_paths.append(curated_path)
    return out_paths


# Minimal Turtle (.ttl) parser - we only need rdfs:label + rdfs:subClassOf style
# triples and a few NIF-specific predicates. Full TTL parsing is over-engineered;
# we do line-based extraction with conservative regexes.
TTL_PREFIX_RE = re.compile(r"@prefix\s+(\S+):\s+<([^>]+)>\s*\.")
TTL_TRIPLE_RE = re.compile(
    r"^(\S+)\s+(\S+)\s+(.+?)\s*\.\s*$"
)
# Predicates we map to our schema (left = ttl predicate, right = our relation)
NIF_PREDICATE_MAP = {
    "rdfs:subClassOf": "IS_A",
    "rdfs:label": "NAMED",
    "BFO:0000050": "PART_OF",  # 'part_of'
    "RO:0002131": "PROJECTS_TO",  # overlaps -- conservative approximation
    "RO:0002150": "PROJECTS_TO",  # continuous_with -- conservative
    "RO:0002202": "CONTAINS_CELL_TYPE",  # develops_from inverse hack
}


def _strip_quotes(s: str) -> str:
    s = s.strip()
    # rdfs:label values like "neuron"@en or "neuron"
    if s.startswith('"'):
        end = s.rfind('"')
        if end > 0:
            return s[1:end]
    return s


def _parse_ttl_stanzas(text: str):
    """Yield (subject, [(predicate, object), ...]) stanzas from TTL text.

    A stanza is a subject followed by ;-separated predicate-object pairs,
    terminated by a `.`. We parse semicolon-statement TTL deterministically
    by splitting on stanza boundaries.

    This skips multi-line string literals that contain ` ;` inside triple-quotes
    by tracking triple-quote depth as we scan.
    """
    # Strip prefix lines + comments
    body_lines = []
    for line in text.splitlines():
        s = line.rstrip()
        if not s or s.lstrip().startswith("@") or s.lstrip().startswith("#"):
            continue
        body_lines.append(s)
    body = "\n".join(body_lines)

    # Walk char-by-char to find stanza-terminating `.`. Track triple-quote
    # state to ignore `.`/`;` inside string literals.
    i = 0
    n = len(body)
    stanzas: list[str] = []
    start = 0
    in_triple_quote = False
    in_single_quote = False
    while i < n:
        c = body[i]
        # Triple quotes (""" or ''') open/close blocks
        if not in_single_quote and i + 2 < n and body[i:i+3] in ('"""', "'''"):
            in_triple_quote = not in_triple_quote
            i += 3
            continue
        if not in_triple_quote:
            if c == '"' and (i == 0 or body[i-1] != '\\'):
                in_single_quote = not in_single_quote
            elif not in_single_quote and c == '.' and (i + 1 >= n or body[i+1] in (' ', '\t', '\n', '\r')) and (i == 0 or body[i-1] in (' ', '\t', '\n', '\r', '>')):
                stanza = body[start:i].strip()
                if stanza:
                    stanzas.append(stanza)
                start = i + 1
        i += 1

    for stanza in stanzas:
        # First whitespace-separated token is the subject (or "a" alias of rdf:type).
        # Then `;`-separated predicate-object pairs.
        parts = stanza.split(None, 1)
        if len(parts) < 2:
            continue
        subj = parts[0]
        rest = parts[1]
        # Split into pred-obj clauses by `;` outside of quotes
        clauses = _split_outside_quotes(rest, ";")
        pred_objs = []
        for clause in clauses:
            clause = clause.strip()
            if not clause:
                continue
            kv = clause.split(None, 1)
            if len(kv) != 2:
                continue
            pred, obj = kv[0], kv[1].strip()
            # Multiple objects: `pred a, b, c` -> emit one per object
            obj_parts = _split_outside_quotes(obj, ",")
            for op in obj_parts:
                op = op.strip()
                if op:
                    pred_objs.append((pred, op))
        if pred_objs:
            yield subj, pred_objs


def _split_outside_quotes(s: str, sep: str) -> list[str]:
    """Split `s` on `sep`, ignoring sep inside "..." or '''...''' or \"\"\"...\"\"\"."""
    out = []
    cur = []
    i = 0
    n = len(s)
    in_triple = False
    in_single = False
    while i < n:
        c = s[i]
        if i + 2 < n and s[i:i+3] in ('"""', "'''"):
            in_triple = not in_triple
            cur.append(s[i:i+3])
            i += 3
            continue
        if not in_triple:
            if c == '"' and (i == 0 or s[i-1] != '\\'):
                in_single = not in_single
            if not in_single and c == sep:
                out.append(''.join(cur))
                cur = []
                i += 1
                continue
        cur.append(c)
        i += 1
    out.append(''.join(cur))
    return out


def parse_nif_ttl(ttl_path: Path) -> list[dict]:
    """Parse a NIF TTL file -> triples (deterministic; semicolon-block aware).

    Supports the common TTL stanza form:
        SUBJ pred1 obj1 ;
             pred2 obj2 .

    Extracts only predicates in NIF_PREDICATE_MAP (high-precision; deterministic).
    Skips blank nodes and quoted string-literal predicates we don't map.

    The curated fallback TSV (synthetic curated brain-region / cell-type /
    neurotransmitter triples) is parsed via the TSV branch and labeled with
    `nif_source: curated_fallback` so it can be filtered or boosted later.
    """
    out: list[dict] = []
    if ttl_path.name == "_curated_fallback.tsv":
        lines = ttl_path.read_text(encoding="utf-8").splitlines()
        for line in lines[1:]:
            parts = line.split("\t")
            if len(parts) != 3:
                continue
            s, p, o = parts
            out.append({"s": s, "p": p, "o": o, "extra_tags": {"nif_source": "curated_fallback"}})
        return out
    text = ttl_path.read_text(encoding="utf-8", errors="replace")
    for subj, pred_objs in _parse_ttl_stanzas(text):
        # Skip blank-node subjects
        if subj.startswith("_:") or subj.startswith("<"):
            # angle-bracketed full IRIs - keep but strip brackets
            if subj.startswith("<") and subj.endswith(">"):
                subj = subj[1:-1]
            else:
                continue
        for pred, obj in pred_objs:
            if pred not in NIF_PREDICATE_MAP:
                continue
            rel = NIF_PREDICATE_MAP[pred]
            if rel == "NAMED":
                o_clean = _strip_quotes(obj)
                if not o_clean:
                    continue
                out.append({
                    "s": subj, "p": "NAMED", "o": o_clean,
                    "extra_tags": {"nif_source": ttl_path.name},
                })
                out.append({
                    "s": o_clean, "p": "ALIAS_OF", "o": subj,
                    "extra_tags": {},
                })
            else:
                # strip type-annotations like `value^^xsd:string` and angle-IRI brackets
                obj_clean = obj.split("^^", 1)[0].strip()
                if obj_clean.startswith("<") and obj_clean.endswith(">"):
                    obj_clean = obj_clean[1:-1]
                if not obj_clean or obj_clean.startswith("_:"):
                    continue
                out.append({
                    "s": subj, "p": rel, "o": obj_clean,
                    "extra_tags": {"nif_source": ttl_path.name},
                })
    return out


# =====================================================================
# Public API for the ingest dispatcher (called from director_kb.py)
# =====================================================================


def parse_gene_ontology_file(path: Path, class_def: dict) -> list[dict]:
    """Dispatcher entrypoint for mode='obo_go'."""
    max_terms = class_def.get("max_terms")
    return parse_gene_ontology(path, max_terms=max_terms)


def parse_kegg_kgml_file(path: Path, class_def: dict) -> list[dict]:
    """Dispatcher entrypoint for mode='kegg_kgml'."""
    return parse_kegg_kgml(path)


def parse_nif_ttl_file(path: Path, class_def: dict) -> list[dict]:
    """Dispatcher entrypoint for mode='nif_ttl'."""
    return parse_nif_ttl(path)


# =====================================================================
# Pre-flight downloader: idempotent fetch of all 3 sources
# =====================================================================


def fetch_all_bio_sources(
    repo_root: Path,
    kegg_max_pathways: int | None = 50,
    force: bool = False,
) -> dict:
    """Idempotent fetch of all 3 bio sources. Returns summary dict.

    Returns {"go": Path|None, "kegg": list[Path], "nif": list[Path], "errors": {...}}.
    Individual source failures (network, 404) are logged but do not raise; the
    cell-level fail-loud check in director_kb_bio_trio cell sees the empty
    cache and raises there.
    """
    errors: dict[str, str] = {}
    go_path: Path | None = None
    try:
        go_path = fetch_gene_ontology(repo_root, force=force)
    except Exception as e:  # noqa: BLE001
        errors["go"] = f"{type(e).__name__}: {e}"
        print(f"[bio_sources] ERROR fetching GO: {e}", flush=True)

    kegg_paths: list[Path] = []
    try:
        kegg_paths = fetch_kegg_pathways(
            repo_root, max_pathways=kegg_max_pathways, force=force,
        )
    except Exception as e:  # noqa: BLE001
        errors["kegg"] = f"{type(e).__name__}: {e}"
        print(f"[bio_sources] ERROR fetching KEGG: {e}", flush=True)

    nif_paths: list[Path] = []
    try:
        nif_paths = fetch_nif(repo_root, force=force)
    except Exception as e:  # noqa: BLE001
        errors["nif"] = f"{type(e).__name__}: {e}"
        print(f"[bio_sources] ERROR fetching NIF: {e}", flush=True)

    return {
        "go": go_path,
        "kegg": kegg_paths,
        "nif": nif_paths,
        "errors": errors,
    }
