#!/usr/bin/env python3
"""Phase-portrait v1 scour: enumerate measured operating-regime data points
from cert atoms (CERT_CHAIN_GRADE + MEASURED_MECHANISM) across the Store.

Director Item 3 of next-20h sprint (USER 2026-06-18 ratify; FULL AUTO).
Composes with optimal-per-evidence cert-VET discipline (Skunkworks 2026-06-18):
phase-portrait = optimal-OPERATING-POINT face of the unification with
capability-mining (optimal-APPROACH).

Cert-condition (Skunkworks SCHEMA-VET-on-landing): MEASURED-only-NO-extrapolation;
INVENTORY_NON_CERT tier; algebra=None structural guard; verify ALL sub-counts.

Output: JSON inventory + a draft PHASE_PORTRAIT atom for Skunkworks SCHEMA-VET.
"""
import json
import re
from pathlib import Path
from collections import defaultdict


ROOT = Path("data/substrate_index")


def load_cert_atoms():
    """Yield (corpus, atom_dict) for every CERT_CHAIN_GRADE or MEASURED_MECHANISM atom."""
    target_pq = {"CERT_CHAIN_GRADE", "MEASURED_MECHANISM"}
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
                pq = md.get("provenance_quality")
                if pq in target_pq:
                    yield corpus, a, pq


def classify_task_domain(text):
    """Heuristic classification of task-domain from atom text. Returns a list of tags."""
    text_lower = (text or "").lower()
    tags = set()
    if re.search(r"\b(math|arithmet|svamp|asdiv|mawps|multiarith|operator|equation|mwp|word problem)\b", text_lower):
        tags.add("math")
    if re.search(r"\b(language|nlp|pos.tagg|ner|slot.fill|intent|chunking|dep.pars|conll)\b", text_lower):
        tags.add("language")
    if re.search(r"\b(retrieval|fact.recall|cleanup|fhrr.unbind|fhrr.bind|kb\d|kb_)\b", text_lower):
        tags.add("retrieval")
    if re.search(r"\b(reason|multi.hop|hypernym|partof|wordnet|composition|reasoning routing|broad|narrow)\b", text_lower):
        tags.add("reasoning")
    if re.search(r"\b(drift|kappa|capacity|cap_pres|axiom|axiom_term|integrity|self.cert|cert.suite|gate)\b", text_lower):
        tags.add("substrate_integrity")
    if re.search(r"\b(architectur|encoder|fhrr|sparsit|softmax|entmax|readout|projection|valspace|holographic)\b", text_lower):
        tags.add("architecture")
    if re.search(r"\b(refuse|gate|a2|absten|reject)\b", text_lower):
        tags.add("refuse_gate")
    if re.search(r"\b(linear|nonlinear|bias|capacity)\b", text_lower):
        tags.add("capacity")
    if re.search(r"\b(ingest|wordnet|framenet|conceptnet|corpus|graph|atom)\b", text_lower) and "experiment" not in text_lower[:30]:
        tags.add("ingest")
    return sorted(tags)


def classify_operating_regime(text):
    """Heuristic regime tagging: dense vs sparse, n-level, etc."""
    text_lower = (text or "").lower()
    tags = set()
    if re.search(r"\b(sparse|sparsity|entmax|softmax_sparse)\b", text_lower):
        tags.add("sparse")
    if re.search(r"\b(dense)\b", text_lower):
        tags.add("dense")
    if re.search(r"\b(2.level|2-level|two.level|two level)\b", text_lower):
        tags.add("two_level")
    if re.search(r"\b(1.level|1-level|one.level|one level|first.hop|first-hop|direct.parent)\b", text_lower):
        tags.add("one_level")
    if re.search(r"\b(narrow)\b", text_lower):
        tags.add("narrow_scope")
    if re.search(r"\b(broad)\b", text_lower):
        tags.add("broad_scope")
    # n_seeds / sample sizes are NOT operating-point axes; filtered out per honest-axis discipline
    if re.search(r"\b(kappa.?3|kappa_3|cumulant)\b", text_lower):
        tags.add("kappa3")
    if re.search(r"\b(grown.corpus|pre.ingest|pre-ingest)\b", text_lower):
        tags.add("corpus_scoped")
    if re.search(r"\b(linear.readout|nonlinear.readout)\b", text_lower):
        tags.add("readout_specified")
    return sorted(tags)


def extract_key_metric_hint(metadata, description):
    """Pull a headline metric if possible from key_metrics or description."""
    km = metadata.get("key_metrics") or {}
    if km and isinstance(km, dict):
        # take first numeric value
        for k, v in km.items():
            if isinstance(v, (int, float)):
                return f"{k}={v}"
    # try description first 200 chars for X=Y pattern
    if description:
        m = re.search(r"(recall|accuracy|auroc|f1|recall@1|score)[=:\s]+(\d+\.\d+)", description[:400], re.IGNORECASE)
        if m:
            return f"{m.group(1).lower()}={m.group(2)}"
        m = re.search(r"(\d+\.\d+)\b", description[:200])
        if m:
            return f"~{m.group(1)}"
    return None


def main():
    cert_atoms = list(load_cert_atoms())
    print(f"Loaded {len(cert_atoms)} cert atoms (CERT_CHAIN_GRADE + MEASURED_MECHANISM)")
    print()

    by_pq = defaultdict(int)
    for _, _, pq in cert_atoms:
        by_pq[pq] += 1
    print("By provenance_quality:", dict(by_pq))
    print()

    cells = []
    for corpus, a, pq in cert_atoms:
        md = a.get("metadata") or {}
        text = (a.get("name") or "") + " " + (a.get("description") or "") + " " + (md.get("hypothesis") or "")
        task_tags = classify_task_domain(text)
        regime_tags = classify_operating_regime(text)
        key_metric = extract_key_metric_hint(md, a.get("description"))
        cells.append({
            "qualified_id": f"{corpus}::{a['id']}",
            "kind": a.get("kind"),
            "tier": a.get("tier"),
            "pq": pq,
            "verdict": md.get("verdict"),
            "relevance_tier": md.get("relevance_tier"),
            "era": md.get("era"),
            "task_domain_tags": task_tags,
            "operating_regime_tags": regime_tags,
            "key_metric_hint": key_metric,
        })

    # Group by task-domain for the inventory cells
    by_domain = defaultdict(list)
    for c in cells:
        if not c["task_domain_tags"]:
            by_domain["UNCLASSIFIED"].append(c)
        else:
            for t in c["task_domain_tags"]:
                by_domain[t].append(c)

    by_regime = defaultdict(list)
    for c in cells:
        if not c["operating_regime_tags"]:
            by_regime["UNTAGGED_REGIME"].append(c)
        else:
            for t in c["operating_regime_tags"]:
                by_regime[t].append(c)

    print("=" * 80)
    print("PHASE-PORTRAIT v1 INVENTORY")
    print("=" * 80)
    print()
    print("Task-domain distribution:")
    for t, lst in sorted(by_domain.items(), key=lambda kv: -len(kv[1])):
        print(f"  {t:30s} {len(lst)} atoms")
    print()
    print("Operating-regime tag distribution:")
    for t, lst in sorted(by_regime.items(), key=lambda kv: -len(kv[1])):
        print(f"  {t:30s} {len(lst)} atoms")
    print()

    # Compute coverage: which (task_domain x regime) pairs are populated
    print("Coverage matrix (task_domain x operating_regime; count of atoms):")
    domains_seen = sorted([d for d in by_domain if d != "UNCLASSIFIED"])
    regimes_seen = sorted([r for r in by_regime if r != "UNTAGGED_REGIME"])
    coverage = defaultdict(lambda: defaultdict(int))
    for c in cells:
        for d in c["task_domain_tags"] or ["UNCLASSIFIED"]:
            for r in c["operating_regime_tags"] or ["UNTAGGED_REGIME"]:
                coverage[d][r] += 1
    print(f"  {'domain':25s}", " ".join(f"{r[:10]:10s}" for r in regimes_seen[:6]))
    for d in domains_seen:
        row_counts = [coverage[d].get(r, 0) for r in regimes_seen[:6]]
        print(f"  {d:25s}", " ".join(f"{c:<10}" for c in row_counts))

    # Write the inventory to a JSON file (input for the PHASE_PORTRAIT atom)
    out_path = Path("data/phase_portrait_v1_inventory.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump({
            "schema_version": "v1",
            "scoured_at_ts": "2026-06-18",
            "total_cert_atoms": len(cells),
            "by_pq": dict(by_pq),
            "task_domain_counts": {t: len(lst) for t, lst in by_domain.items()},
            "regime_tag_counts": {t: len(lst) for t, lst in by_regime.items()},
            "cells": cells,
        }, f, indent=2)
    print()
    print(f"Inventory written: {out_path}")
    print(f"Total cert atoms in inventory: {len(cells)}")
    print()
    print("Next step: route inventory + draft PHASE_PORTRAIT atom to Skunkworks SCHEMA-VET-on-landing.")


if __name__ == "__main__":
    main()
