#!/usr/bin/env python3
"""Item 3 WRITEUP precursor scour: enumerate ALL 571+ CERT_CHAIN_GRADE atoms
across the FULL substrate (per Skunkworks binding condition 1: scour FULL
breadth + 432+ domain-positives NOT depth-cliff arc only).

For each cert atom, classify by:
- task-domain (NLP / cognitive / audit / KG / retrieval / math / substrate /
  architecture / capacity / refuse-gate / ingest / reasoning)
- AtomKind (experiment_record / methodology_rule / finding / audit_lesson /
  proof_record / capability / ...)
- relevance_tier + era
- evidence-anchors (cell + prereg + metrics paths if EXPERIMENT_RECORD)

Output: a structured breadth-inventory for the WRITEUP to honest-scope-cite.
"""
import json
import re
from pathlib import Path
from collections import defaultdict, Counter


ROOT = Path("data/substrate_index")


def load_cert_atoms():
    """Yield (corpus, atom_dict) for every CERT_CHAIN_GRADE atom."""
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
                if pq == "CERT_CHAIN_GRADE":
                    yield corpus, a


# Refined task-domain heuristics (broader than catalog audit's; captures
# substrate-breadth across the 432+ positives Skunkworks flagged in
# feedback_director_intuitive_summary_must_scour_full_substrate_breadth)
DOMAINS = {
    "NLP_language": [
        r"\b(language|nlp|pos.?tag|ner|named.entity|slot.?fill|intent|chunking|"
        r"dep.?pars|conll|udep|ud_ewt|udmwe|partof.speech|tokenizer|lemmati|"
        r"semantic.frame|framenet)\b"
    ],
    "math_arithmetic": [
        r"\b(math|arithmet|svamp|asdiv|mawps|multiarith|operator|equation|mwp|"
        r"word.problem|wk_oracle|3.op|2.op|multistep|multibench)\b"
    ],
    "retrieval": [
        r"\b(retrieval|fact.recall|cleanup|fhrr.unbind|fhrr.bind|kb\d|kb_|kb100k|"
        r"schema.bundle|projection.head)\b"
    ],
    "reasoning_multihop": [
        r"\b(reason|multi.hop|hypernym|partof|meronym|wordnet|composition|"
        r"reasoning.routing|broad.envelope|narrow|hop.\d|b.alpha|2.level|"
        r"depth.cliff|conceptnet)\b"
    ],
    "cognitive_capacity": [
        r"\b(capacity|cap_pres|recall|fhrr|hrr|vsa|capacity.preservation|"
        r"redundancy|kerdock|bsc|kappa.?3|drift.detection|continual)\b"
    ],
    "substrate_integrity": [
        r"\b(axiom|axiom_term|integrity|self.cert|cert.suite|gate0|phantom.dep|"
        r"discrimination.regime|baseline.cliff|corpus.completeness|"
        r"verdict.mappable|multi.hop.provenance)\b"
    ],
    "architecture": [
        r"\b(architectur|encoder|fhrr.architecture|sparsit|softmax|entmax|readout|"
        r"projection|valspace|holographic|circular.convolution|bind|unbind|"
        r"superposition|binding)\b"
    ],
    "refuse_gate_audit": [
        r"\b(refuse.gate|a2_|abstain|reject|coverage.gap|auroc.confidence)\b"
    ],
    "ingest_curation": [
        r"\b(ingest|wordnet|framenet|conceptnet|corpus|graph|atomize|ingestion|"
        r"semantic.frame.add|nltk)\b"
    ],
    "proof_formal": [
        r"\b(proof|axiom|formal|theorem|pythagor|cauchy|triangle|parallelogram|"
        r"t0.proven|lean|mathlib|formal.cert)\b"
    ],
    "training_dynamics": [
        r"\b(training|gradient|hebbian|lora|stage.2|fine.tun|adapter|"
        r"oneshot|catastrophic.forget)\b"
    ],
    "audit_discipline": [
        r"\b(audit|verify.referent|negativity.bias|investigate.first|"
        r"actual.not.bar|degenerate.regime|honest.scope|measured.bounds)\b"
    ],
}


def classify_domains(text):
    text_lower = text.lower()
    matches = set()
    for domain, patterns in DOMAINS.items():
        for p in patterns:
            if re.search(p, text_lower):
                matches.add(domain)
                break
    return sorted(matches)


def extract_evidence(a):
    """Pull evidence anchors (cell + prereg + metrics paths if EXPERIMENT_RECORD)."""
    md = a.get("metadata") or {}
    return {
        "experiment_path": md.get("experiment_path"),
        "prereg_path": md.get("prereg_path"),
        "metrics_path": md.get("metrics_path"),
        "cell_sha": md.get("cell_sha"),
        "remote_run_id": md.get("remote_run_id"),
        "verdict": md.get("verdict"),
        "relevance_tier": md.get("relevance_tier"),
        "era": md.get("era"),
    }


def main():
    cert_atoms = list(load_cert_atoms())
    print(f"Total CERT_CHAIN_GRADE atoms: {len(cert_atoms)}")
    print()

    by_kind = Counter()
    by_corpus = Counter()
    by_relevance_tier = Counter()
    by_era = Counter()
    by_verdict = Counter()

    domain_atoms = defaultdict(list)  # domain -> list of atom-id
    unclassified = []
    multi_domain = defaultdict(int)

    rows = []
    for corpus, a in cert_atoms:
        md = a.get("metadata") or {}
        kind = a.get("kind", "UNK")
        by_kind[kind] += 1
        by_corpus[corpus] += 1
        by_relevance_tier[md.get("relevance_tier", "UNK")] += 1
        by_era[md.get("era", "UNK")] += 1
        by_verdict[md.get("verdict", "UNK")] += 1

        text = " ".join([
            a.get("name") or "",
            a.get("description") or "",
            md.get("hypothesis") or "",
            a.get("id") or "",
        ])
        domains = classify_domains(text)
        if not domains:
            unclassified.append(a["id"])
        else:
            for d in domains:
                domain_atoms[d].append(a["id"])
            multi_domain[len(domains)] += 1

        rows.append({
            "qid": f"{corpus}::{a['id']}",
            "kind": kind,
            "domains": domains,
            "verdict": md.get("verdict"),
            "relevance_tier": md.get("relevance_tier"),
            "era": md.get("era"),
            "evidence": extract_evidence(a),
        })

    print("=" * 80)
    print("PART 1: BY KIND")
    print("=" * 80)
    for kind, n in by_kind.most_common():
        print(f"  {kind:25s} {n}")
    print()

    print("=" * 80)
    print("PART 2: BY CORPUS")
    print("=" * 80)
    for corpus, n in by_corpus.most_common():
        print(f"  {corpus:25s} {n}")
    print()

    print("=" * 80)
    print("PART 3: BY RELEVANCE_TIER (positives breakdown)")
    print("=" * 80)
    for tier, n in by_relevance_tier.most_common():
        print(f"  {tier:25s} {n}")
    print()

    print("=" * 80)
    print("PART 4: BY ERA")
    print("=" * 80)
    for era, n in by_era.most_common():
        print(f"  {era:25s} {n}")
    print()

    print("=" * 80)
    print("PART 5: BY VERDICT (the positive/negative breakdown)")
    print("=" * 80)
    for verdict, n in by_verdict.most_common():
        print(f"  {verdict:25s} {n}")
    print()

    print("=" * 80)
    print("PART 6: DOMAIN-DISTRIBUTION (THE BREADTH SKUNKWORKS WANTS)")
    print("=" * 80)
    print(f"UNCLASSIFIED (heuristic v1 too narrow): {len(unclassified)}")
    for domain in sorted(domain_atoms.keys()):
        atoms = domain_atoms[domain]
        print(f"  {domain:30s} {len(atoms)}")
    print()
    print("Multi-domain overlap distribution (atoms can match multiple):")
    for n_domains, n_atoms in sorted(multi_domain.items()):
        print(f"  {n_domains}-domain matches: {n_atoms} atoms")
    print()

    # Sample atoms per domain (for the writeup to cite)
    print("=" * 80)
    print("PART 7: TOP-5 SAMPLE PER DOMAIN (for WRITEUP citation; honest-scope-anchors)")
    print("=" * 80)
    for domain in sorted(domain_atoms.keys()):
        atoms = domain_atoms[domain]
        print(f"\n  {domain} ({len(atoms)}):")
        for aid in atoms[:5]:
            print(f"    {aid}")
        if len(atoms) > 5:
            print(f"    ... + {len(atoms) - 5} more")

    # Output
    out = {
        "scour_ts": "2026-06-19",
        "total_cert_atoms": len(cert_atoms),
        "by_kind": dict(by_kind),
        "by_corpus": dict(by_corpus),
        "by_relevance_tier": dict(by_relevance_tier),
        "by_era": dict(by_era),
        "by_verdict": dict(by_verdict),
        "domain_counts": {d: len(atoms) for d, atoms in domain_atoms.items()},
        "unclassified_count": len(unclassified),
        "unclassified_sample": unclassified[:30],
        "multi_domain_distribution": dict(multi_domain),
        "atoms": rows,
    }

    out_path = Path("data/writeup_full_substrate_breadth_scour_2026-06-19.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print()
    print(f"Full scour written: {out_path}")


if __name__ == "__main__":
    main()
