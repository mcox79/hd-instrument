#!/usr/bin/env python3
"""Phase-portrait v2 scour-deepening: deepen v1 with 5 additions per 40h Next-6.

DELTAS over v1:
1. Deepen UNCLASSIFIED domain coverage (refined domain heuristics; broader patterns
   from scour_writeup_full_substrate_breadth.py).
2. Structured key_metrics axes: {metric_name -> {value, units?, source_atom_id}}
   instead of free-text key_metric_hint.
3. Scaling-rule capture: surface atoms describing how metric scales with N / seeds /
   depth / corpus-size (the operating-regime axes the substrate exhibits).
4. Item-1 PART_OF held-out bound boundary marker: classify each atom as
   bound-bearing (the actual bound) vs bound-extending (composes / replicates)
   vs bound-suffering (a result limited by the bound) vs bound-irrelevant.
5. Honest-scoped proven-bound capture: per Skunkworks's cert-emphasis, extract
   the EXACT thing each cert atom proves (not the headline). Flagged as a
   freeform field; cert-VET'd elsewhere.

Composes with the capability-integration cycle's Director-half Piece-1
(capability-enumerator) -- this scour's structured output is the basis for
the enumerator at USER launch (does NOT pre-empt the launch; just makes the
substrate-insight legible).

Output: data/phase_portrait_v2_inventory.json (gitignored data/).
NO STORE WRITES. Atom-landing happens under SCHEMA-VET later.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path("data/substrate_index")


def load_cert_atoms():
    """Yield (corpus, atom) for every CERT_CHAIN_GRADE atom."""
    for atoms_file in ROOT.glob("*/atoms.jsonl"):
        corpus = atoms_file.parent.name
        with atoms_file.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    a = json.loads(line)
                except json.JSONDecodeError:
                    continue
                md = a.get("metadata") or {}
                if md.get("provenance_quality") == "CERT_CHAIN_GRADE":
                    yield corpus, a


# Refined domain taxonomy (broader; merges v1 + scour_writeup_full_substrate_breadth)
DOMAINS = {
    "reasoning_multihop": [
        r"\b(multi.?hop|n.?hop|hypernym|part.?of|wordnet|"
        r"narrow.?qa|broad.?qa|reasoning.?routing|composition.?reasoning)\b",
    ],
    "cognitive_capacity": [
        r"\b(capacity|cap.?pres|crosstalk|bundle.?capacity|n.?\d+\s*ad|"
        r"working.?memory|short.?term)\b",
    ],
    "retrieval": [
        r"\b(retriev|fact.?recall|cleanup|unbind|kb.?\d|kb_|recall@\d|"
        r"nearest.neighbor|knn)\b",
    ],
    "NLP_language": [
        r"\b(language|nlp|pos.?tag|ner|named.entity|slot|intent|chunking|"
        r"dep.?pars|conll|udep|udmwe|tokenizer|lemmati|spacy|english)\b",
    ],
    "math": [
        r"\b(math|arithmet|svamp|asdiv|mawps|multiarith|operator|equation|"
        r"mwp|word.?problem|pythagor|cauchy|theorem|proof|lean|axiom)\b",
    ],
    "substrate_integrity": [
        r"\b(integrity|axiom_term|cert.?suite|self.?cert|gate|drift|kappa|"
        r"substrate.?id|cert.?floor|provenance)\b",
    ],
    "architecture": [
        r"\b(architectur|encoder|fhrr|sparsi|softmax|entmax|readout|"
        r"projection|valspace|holographic|hopfield|attention)\b",
    ],
    "refuse_gate": [
        r"\b(refuse|gate|absten|reject|a2|threshold|calibrat)\b",
    ],
    "audit_methodology": [
        r"\b(audit|lesson|methodology|verify|referent|negativ.?bias|"
        r"corpus.?completeness|honest|symmetric|actual.?not.?bar)\b",
    ],
    "knowledge_graph": [
        r"\b(knowledge.?graph|kg|conceptnet|framenet|wordnet|fb15k|"
        r"freebase|wikidata|nell|graph.?ingest|edge|triple|relation)\b",
    ],
    "ingest_pipeline": [
        r"\b(ingest|atomize|atom.?add|pipeline|consumer|dispatch|"
        r"hd_metrics_sync|reconcile)\b",
    ],
    "dynamics": [
        r"\b(dynam|phase.?portrait|fixed.?point|attractor|trajectory|"
        r"flow|orbit|limit.?cycle)\b",
    ],
}


NAME_SUBSTRINGS = {
    "NLP_language": ["depparse", "dep_parse", "pos_tagger", "ner_", "_ner_",
                     "ner_gazetteer", "ner_transition", "chunking", "spacy",
                     "tokenizer", "lemma", "language", "_nlp_", "conll", "udep",
                     "temporal_contextual", "_charngram", "sst2", "imdb",
                     "crossdomain_transfer", "noise_crosscut", "stage_a_bio"],
    "math": ["pythagor", "cauchy", "theorem", "_math_", "lean", "axiom",
             "arithmet", "_proof_", "svamp", "asdiv", "mawps", "multiarith"],
    "retrieval": ["retriev", "fact_recall", "cleanup", "unbind", "_kb_",
                  "recall_at", "knn", "nearest_neighbor"],
    "reasoning_multihop": ["multihop", "multi_hop", "n_hop", "hypernym",
                           "partof", "part_of", "wordnet", "composition",
                           "narrow_qa", "broad_qa", "reasoning_routing"],
    "cognitive_capacity": ["capacity", "cap_pres", "crosstalk", "bundle_cap",
                           "working_memory", "short_term", "palimpsest"],
    "substrate_integrity": ["integrity", "axiom_term", "cert_suite",
                            "self_cert", "_gate_", "drift", "kappa",
                            "substrate_id", "cert_floor", "tier4_multiseed",
                            "tier3", "caching_eviction", "deletion_cert",
                            "refusal_joint"],
    "architecture": ["architectur", "encoder", "fhrr", "sparsi", "softmax",
                     "entmax", "readout", "projection", "valspace",
                     "holographic", "hopfield", "attention"],
    "refuse_gate": ["refuse_gate", "_a2_", "abstention", "_reject_",
                    "threshold", "calibrat"],
    "audit_methodology": ["audit_", "lesson", "methodology", "verify_",
                          "referent", "negativ_bias", "corpus_completeness",
                          "honest_", "symmetric_", "actual_not_bar"],
    "knowledge_graph": ["knowledge_graph", "_kg_", "conceptnet", "framenet",
                        "wordnet", "fb15k", "freebase", "wikidata", "nell",
                        "graph_ingest", "_edge_", "triple_", "relation_"],
    "ingest_pipeline": ["ingest", "atomize", "atom_add", "_pipeline_",
                        "_consumer_", "dispatch", "hd_metrics_sync",
                        "reconcile"],
    "dynamics": ["dynam", "phase_portrait", "fixed_point", "attractor",
                 "trajectory", "_flow_", "_orbit_", "limit_cycle"],
}


def classify_domain(text, name=None):
    """Combine word-boundary regex on text + substring scan on atom name."""
    text_lower = (text or "").lower()
    name_lower = (name or "").lower()
    tags = set()
    for domain, patterns in DOMAINS.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                tags.add(domain)
                break
    for domain, substrs in NAME_SUBSTRINGS.items():
        if domain in tags:
            continue
        for s in substrs:
            if s in name_lower:
                tags.add(domain)
                break
    return sorted(tags)


# Structured key_metrics extraction
METRIC_PATTERNS = [
    (r"\b(recall@\d+)\b[^\d]*(\d+\.\d+)", "recall_at_k"),
    (r"\b(accuracy)\b[^\d]*(\d+\.\d+)", "accuracy"),
    (r"\b(auroc|au_roc|au.?roc)\b[^\d]*(\d+\.\d+)", "auroc"),
    (r"\b(f1)\b[^\d]*(\d+\.\d+)", "f1"),
    (r"\b(cap_pres|cap.?pres)\b[^\d]*(\d+\.\d+)", "cap_pres"),
    (r"\b(precision)\b[^\d]*(\d+\.\d+)", "precision"),
    (r"\b(perplexity|ppl)\b[^\d]*(\d+\.\d+)", "perplexity"),
    (r"\b(score)\b[^\d]*(\d+\.\d+)", "score"),
    (r"\b(kappa.?3?)\b[^\d]*(\d+\.\d+)", "kappa3"),
    (r"\b(n.?seeds)\b[=:\s]+(\d+)", "n_seeds"),
    (r"\b(n.?dim|n=)\b[=:\s]*(\d+)", "n_dim"),
]


def extract_structured_metrics(metadata, description, atom_id):
    metrics = {}
    km = metadata.get("key_metrics") or {}
    if isinstance(km, dict):
        for k, v in km.items():
            if isinstance(v, (int, float)):
                metrics[k] = {"value": v, "source": "metadata.key_metrics"}
            elif isinstance(v, str):
                m = re.search(r"(-?\d+\.?\d*)", v)
                if m:
                    try:
                        metrics[k] = {"value": float(m.group(1)),
                                      "source": "metadata.key_metrics (parsed)"}
                    except ValueError:
                        pass

    # Description-extracted metrics
    text = (description or "")[:1000]
    for pat, metric_name in METRIC_PATTERNS:
        m = re.search(pat, text, re.IGNORECASE)
        if m and metric_name not in metrics:
            try:
                val = float(m.group(2))
                metrics[metric_name] = {"value": val,
                                        "source": f"description (regex {pat[:30]})"}
            except (ValueError, IndexError):
                pass

    return metrics


# Scaling-rule capture patterns
SCALING_PATTERNS = [
    (r"\b(n.?dim|n=|n_seeds|n.?seeds|depth|hops|n_levels|"
     r"corpus.?size|atoms|partitions)\b[\s\S]{0,150}?"
     r"\b(scal|grow|increas|saturat|asymptot|plateau|cap|ceiling|floor)\b",
     "scaling_pattern"),
    (r"\bk.?fold\b|\bn.?fold\b|\bcross.?valid", "kfold_scaling"),
    (r"\b(log|exponential|polynomial|linear)\s*(?:scal|growth)\b", "scaling_class"),
]


def extract_scaling_hints(metadata, description):
    text = ((metadata.get("hypothesis") or "") + " " + (description or ""))[:2000]
    hits = []
    for pat, label in SCALING_PATTERNS:
        for m in re.finditer(pat, text, re.IGNORECASE):
            snippet = text[max(0, m.start() - 30): m.end() + 30]
            hits.append({"label": label, "snippet": snippet.strip()})
    return hits


# Item-1 PART_OF held-out bound classifier
ITEM_1_KEYWORDS_BOUND = [
    "part_of_heldout", "partof_heldout", "held_out_part_of", "held-out part_of",
    "EXP_partof_heldout", "coverage-completion", "coverage_completion",
    "not-reasoning", "not_reasoning",
]
ITEM_1_KEYWORDS_EXTENDING = [
    "hypernym_heldout", "depth_extended", "depth-5", "multi-relation",
    "multi_relation_robust", "depth_ceiling", "discriminating",
]
ITEM_1_KEYWORDS_SUFFERING = [
    "narrow QA", "n-hop QA", "wordnet reasoning", "reasoning_capability",
    "broad reasoning",
]


def classify_item_1_bound(text):
    text_lower = (text or "").lower()
    for kw in ITEM_1_KEYWORDS_BOUND:
        if kw.lower() in text_lower:
            return "bound_bearing"
    for kw in ITEM_1_KEYWORDS_EXTENDING:
        if kw.lower() in text_lower:
            return "bound_extending"
    for kw in ITEM_1_KEYWORDS_SUFFERING:
        if kw.lower() in text_lower:
            return "bound_suffering"
    return "bound_irrelevant"


# Honest-scoped proven-bound capture (preliminary; cert-VET later)
PROVEN_BOUND_HINTS = [
    r"PROVEN[:\s]+([^\.\n]{20,200})",
    r"DEMONSTRATES?[:\s]+([^\.\n]{20,200})",
    r"VERIFIED[:\s]+([^\.\n]{20,200})",
    r"CONFIRMED[:\s]+([^\.\n]{20,200})",
    r"\bHONEST_NEGATIVE\b[:\s]*([^\.\n]{20,200})",
    r"\bHONEST.SCOPED\b[:\s]*([^\.\n]{20,200})",
]


def extract_proven_bound_hint(metadata, description):
    text = ((metadata.get("verdict") or "") + "\n" + (description or ""))[:2000]
    hints = []
    for pat in PROVEN_BOUND_HINTS:
        for m in re.finditer(pat, text, re.IGNORECASE):
            hints.append(m.group(1).strip())
            if len(hints) >= 3:
                return hints
    return hints


def main():
    cert_atoms = list(load_cert_atoms())
    print(f"Loaded {len(cert_atoms)} CERT_CHAIN_GRADE atoms")
    print()

    cells = []
    by_domain = defaultdict(int)
    by_bound_class = defaultdict(int)
    unclassified = []
    metric_counts = defaultdict(int)
    scaling_atoms = []

    for corpus, a in cert_atoms:
        md = a.get("metadata") or {}
        atom_id = a["id"]
        text = " ".join([
            a.get("name") or "",
            a.get("description") or "",
            md.get("hypothesis") or "",
            md.get("verdict") or "",
        ])

        domain_tags = classify_domain(text, name=a.get("name"))
        if not domain_tags:
            unclassified.append({"qualified_id": f"{corpus}::{atom_id}",
                                 "name": a.get("name"),
                                 "snippet": text[:150]})

        metrics = extract_structured_metrics(md, a.get("description"), atom_id)
        for m_name in metrics:
            metric_counts[m_name] += 1

        scaling_hints = extract_scaling_hints(md, a.get("description"))
        if scaling_hints:
            scaling_atoms.append({
                "qualified_id": f"{corpus}::{atom_id}",
                "name": a.get("name"),
                "hints": scaling_hints[:3],
            })

        bound_class = classify_item_1_bound(text)
        by_bound_class[bound_class] += 1

        proven_bound = extract_proven_bound_hint(md, a.get("description"))

        cell = {
            "qualified_id": f"{corpus}::{atom_id}",
            "name": a.get("name"),
            "kind": a.get("kind"),
            "tier": a.get("tier"),
            "domain_tags": domain_tags,
            "structured_metrics": metrics,
            "scaling_hints": scaling_hints[:3],
            "item_1_bound_class": bound_class,
            "proven_bound_hints": proven_bound,
        }
        cells.append(cell)
        for d in domain_tags:
            by_domain[d] += 1

    # Output summary
    print("=" * 80)
    print("PHASE-PORTRAIT v2 DEEPENED INVENTORY")
    print("=" * 80)
    print()
    print(f"Total CERT_CHAIN_GRADE atoms: {len(cells)}")
    print()
    print("Domain distribution (deepened taxonomy; atoms can match multiple):")
    for d, n in sorted(by_domain.items(), key=lambda kv: -kv[1]):
        print(f"  {d:30s} {n}")
    print(f"  {'UNCLASSIFIED':30s} {len(unclassified)}")
    print()
    print("Item-1 PART_OF held-out bound classification:")
    for cls, n in sorted(by_bound_class.items(), key=lambda kv: -kv[1]):
        print(f"  {cls:30s} {n}")
    print()
    print(f"Structured metrics surfaced (atoms with >=1 structured metric):")
    print(f"  Total: {sum(1 for c in cells if c['structured_metrics'])}")
    print("  By metric name:")
    for name, count in sorted(metric_counts.items(), key=lambda kv: -kv[1]):
        print(f"    {name:25s} {count}")
    print()
    print(f"Scaling-hint atoms: {len(scaling_atoms)}")
    print()
    print(f"Proven-bound hints surfaced: "
          f"{sum(1 for c in cells if c['proven_bound_hints'])} atoms with >=1 hint")
    print()

    # Sample bound-bearing and bound-extending
    bound_bearing = [c for c in cells if c["item_1_bound_class"] == "bound_bearing"]
    bound_extending = [c for c in cells if c["item_1_bound_class"] == "bound_extending"]
    print(f"Bound-BEARING atoms (sample, first 5; central to Item-1 negative result):")
    for c in bound_bearing[:5]:
        print(f"  - {c['qualified_id']}: {c['name'][:80] if c['name'] else '(unnamed)'}")
    print()
    print(f"Bound-EXTENDING atoms (sample, first 5; multi-relation-robust + depth-extended):")
    for c in bound_extending[:5]:
        print(f"  - {c['qualified_id']}: {c['name'][:80] if c['name'] else '(unnamed)'}")
    print()

    out_path = Path("data/phase_portrait_v2_inventory.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump({
            "schema_version": "v2",
            "scoured_at_ts": "2026-06-19",
            "total_cert_atoms": len(cells),
            "domain_counts": dict(by_domain),
            "unclassified_count": len(unclassified),
            "item_1_bound_class_counts": dict(by_bound_class),
            "metric_counts": dict(metric_counts),
            "atoms_with_structured_metrics": sum(
                1 for c in cells if c["structured_metrics"]),
            "atoms_with_scaling_hints": len(scaling_atoms),
            "atoms_with_proven_bound_hints": sum(
                1 for c in cells if c["proven_bound_hints"]),
            "cells": cells,
            "unclassified_sample": unclassified[:30],
            "scaling_atoms_sample": scaling_atoms[:30],
        }, f, indent=2)
    print(f"Inventory written: {out_path}")
    print()
    print("NEXT: draft PHASE_PORTRAIT v2 atom for Skunkworks SCHEMA-VET-on-landing")
    print("(Atom would supersede v1; structural guards stay: algebra=None, "
          "INVENTORY_NON_CERT tier, MEASURED-only-no-extrapolation.)")


if __name__ == "__main__":
    main()
