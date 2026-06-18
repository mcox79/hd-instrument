"""Director-authored CAPABILITY_MAP scour + atom builder. Regeneratable.

Scours the substrate for CERT_CHAIN_GRADE atoms, categorizes by domain (substring
heuristic, 11th-rule clean), splits HIGH/LOW relevance, separates HARD_FAIL companion,
flags 2 UNSET legacy atoms for cert-owner re-classification. Writes the DRAFT atom
JSON for Skunkworks's pre-Store-write FINAL VET.
"""
import json
import os
import collections

ROOT = "data/substrate_index"

POSITIVE_VERDICTS = {"PASS", "HARD_PASS", "PARTIAL_PASS", "CONFIRMED", "POSITIVE"}
APPLIED_DOMAINS = {
    "NLP/Language",
    "Cognitive/Reasoning",
    "KnowledgeGraph/MultiHop",
    "Audit/Capability",
    "Retrieval/Memory",
}


def categorize(name: str, description: str) -> str:
    """Approximate substring-match domain heuristic. Substrate-internal, no LLM."""
    n = name.lower().replace("exp ", "").replace("_", " ")
    d = description.lower()[:300].replace("_", " ")
    t = f"{n} {d}"
    if any(k in t for k in ["fb15k", "wn18", "multihop", "multi hop", "hop qa",
                             "knowledge graph", " kg ", "nkt ", "fb15k237",
                             "mutlimodal binding text kg"]):
        return "KnowledgeGraph/MultiHop"
    if any(k in t for k in ["atis", "intent", " ner ", "conll", "ontonotes",
                             "pos tag", "cross domain", "wordnet", "framenet",
                             "conceptnet", "charlm", "charngram", "sentence",
                             "crossdomain"]):
        return "NLP/Language"
    if any(k in t for k in ["proof ", "theorem", "math::", "inner product",
                             "orthogon", "pythag", "cauchy", "triangle",
                             "parallelogram", " lean "]):
        return "Math/Formal"
    if any(k in t for k in ["abduction", "compositional", "decomposit",
                             "resonator", "active inference", "dpefe", " crt ",
                             "crt module", " hmm ", "symbolic",
                             "world knowledge", "wk aug", "asdiv", "k10", "k20",
                             "novel assembly", "csp ", "csp hebbian",
                             "drosophila", "reasoning"]):
        return "Cognitive/Reasoning"
    if any(k in t for k in ["audit core", "audit ", "cert refus",
                             "capacity cliff", "graceful", "seb det",
                             "metrics provenance", "capability atom", "gate 0",
                             "sqa ", "capability"]):
        return "Audit/Capability"
    if any(k in t for k in ["hnsw", "retrieval", "recall@", "recall at",
                             "cleanup", "codebook"]):
        return "Retrieval/Memory"
    if any(k in t for k in ["capacity", "composition", "binding", "unbind",
                             "bundle", "fhrr", "hrr", "tier ", "wave",
                             "multi seed", "sparse", "softmax", "entmax",
                             "nonlinear", "readout", "sparsity", "arch a",
                             "arch b", "arch-a", "arch-b", "deletion"]):
        return "SubstrateMechanism"
    return "Other/Mixed"


def scour():
    cert = []
    for p in sorted(os.listdir(ROOT)):
        fp = os.path.join(ROOT, p, "atoms.jsonl")
        if not os.path.isfile(fp):
            continue
        with open(fp, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    a = json.loads(line)
                except Exception:
                    continue
                md = a.get("metadata") if isinstance(a.get("metadata"), dict) else {}
                if md.get("provenance_quality") != "CERT_CHAIN_GRADE":
                    continue
                cert.append({
                    "partition": p,
                    "aid": a.get("id", ""),
                    "name": a.get("name", ""),
                    "description": (a.get("description") or ""),
                    "verdict": md.get("verdict") or "",
                    "relevance_tier": md.get("relevance_tier", ""),
                    "experiment_path": md.get("experiment_path", ""),
                    "metric_type": md.get("metric_type", ""),
                })
    return cert


def build_atom(cert, corpus_total):
    positives = [c for c in cert if c["verdict"] in POSITIVE_VERDICTS]
    high = [c for c in positives if c["relevance_tier"] == "HIGH"]
    low = [c for c in positives if c["relevance_tier"] == "LOW"]
    hard_fail = [c for c in cert if c["verdict"] == "HARD_FAIL"]
    unset = [c for c in cert if c["verdict"] in ("", "UNSET")]

    high_by_dom = collections.Counter(categorize(c["name"], c["description"]) for c in high)
    low_by_dom = collections.Counter(categorize(c["name"], c["description"]) for c in low)
    hard_fail_by_dom = collections.Counter(categorize(c["name"], c["description"]) for c in hard_fail)

    def per_dom_list(items, with_metric=False):
        out = collections.defaultdict(list)
        for c in items:
            d = categorize(c["name"], c["description"])
            entry = {
                "aid": c["aid"],
                "name": (c["name"] or "").replace("EXP ", "").strip(),
            }
            if with_metric:
                entry["metric_type"] = c["metric_type"]
            out[d].append(entry)
        return dict(out)

    applied_total = sum(high_by_dom[d] + low_by_dom[d] for d in APPLIED_DOMAINS)
    core_total = (high_by_dom["SubstrateMechanism"] + low_by_dom["SubstrateMechanism"]
                  + high_by_dom.get("Math/Formal", 0) + low_by_dom.get("Math/Formal", 0)
                  + high_by_dom.get("Other/Mixed", 0) + low_by_dom.get("Other/Mixed", 0))

    description = (
        "Director-authored substrate-breadth inventory pointing AT CERT_CHAIN_GRADE atoms "
        "in the substrate as of 2026-06-18. HONEST FRAMING (per Skunkworks 432-map VET, "
        "negativity-bias-symmetric toward PRECISION): the substrate contains "
        f"{len(cert)} CERT_CHAIN_GRADE atoms, of which {len(positives)} are PASS-verdict. "
        f"The {len(positives)} PASS atoms split into {len(high)} distinct HIGH-relevance "
        f"capability claims + {len(low)} LOW-relevance replication/sweep/parameter atoms "
        "(all CERT_CHAIN_GRADE; LOW are robust replication evidence, NOT independent "
        "capability claims). DOMAIN DISTRIBUTION: "
        f"{core_total}/{len(positives)} are substrate-mechanism CORE (VSA/HDC capacity, "
        f"binding, retrieval, formal proofs); {applied_total}/{len(positives)} are across "
        "5 applied domains (NLP, Cognitive, KG, Audit, Retrieval). The substrate's "
        "STRONGEST cert-grade claim is the substrate-mechanism CORE; applied-domain breadth "
        f"is more modest. NEGATIVE COMPANION: {len(hard_fail)} HARD_FAIL CERT atoms "
        "(recapture-program honest-negatives + 8a measured-fail + others); the POSITIVES "
        "are credible BECAUSE the negatives are at cert tier (cert-architecture catches its "
        "own custodians). DOMAIN HEURISTIC IS APPROXIMATE (substring-match on name + "
        "description, 11th-rule clean, NOT authoritative). THIS ATOM IS AN INVENTORY/INDEX, "
        "NOT itself a CERT (structural guards: algebra=None excluded from axiom_term, "
        "provenance_quality NOT CERT_CHAIN_GRADE). Regeneratable via "
        "tools/scour_capability_map_432.py for honest refresh."
    )

    atom = {
        "id": "meta::CAPABILITY_MAP_substrate_breadth_2026_06_18_v1",
        "name": "CAPABILITY_MAP substrate breadth 2026-06-18 v1",
        "corpus": "meta",
        "tier": "NA",
        "kind": "capability_map",
        "description": description,
        "aliases": [],
        "metadata": {
            "record_class": "capability_map",
            "term_class": "INVENTORY_NON_MATH",
            "algebra": None,
            "provenance_quality": "INVENTORY_NON_CERT",
            "verdict": "INVENTORY",
            "relevance_tier": "HIGH",
            "authored_by": "research_director",
            "cert_owner_vet": "PENDING_FINAL_PRE_STORE_WRITE",
            "scour_query": {
                "tool": "tools/scour_capability_map_432.py",
                "pattern": "metadata.provenance_quality == CERT_CHAIN_GRADE",
                "corpus_root": "data/substrate_index/*/atoms.jsonl",
                "date": "2026-06-18",
                "corpus_total_atoms_at_scour": corpus_total,
            },
            "domain_heuristic": "APPROXIMATE substring-match on name+description; NOT authoritative",
            "honest_framing_correction_applied": (
                "PRECISION: distinct HIGH-relevance claims + LOW-relevance replication "
                "(not all-432-as-capabilities or all-432-as-applied-domains); mirror of "
                "morning 2026-06-18 NEGATIVITY-BIAS-symmetric catch which cut UPWARD"
            ),
            "capability_inventory": {
                "cert_chain_grade_total": len(cert),
                "positives_total": len(positives),
                "cert_by_verdict": dict(collections.Counter(c["verdict"] for c in cert)),
                "positives_high_relevance": len(high),
                "positives_low_relevance": len(low),
                "positives_high_by_domain": dict(high_by_dom),
                "positives_low_by_domain": dict(low_by_dom),
                "positives_high_exemplars_per_domain": per_dom_list(high, with_metric=True),
                "positives_low_samples_per_domain": {
                    d: items[:8] for d, items in per_dom_list(low).items()
                },
                "applied_domain_total": applied_total,
                "core_total": core_total,
                "hard_fail_total": len(hard_fail),
                "hard_fail_by_domain": dict(hard_fail_by_dom),
                "hard_fail_exemplars_per_domain": {
                    d: items[:8] for d, items in per_dom_list(hard_fail).items()
                },
                "unset_legacy_count": len(unset),
                "unset_aids_for_flag_dont_auto": [c["aid"] for c in unset],
            },
        },
        "current_best_solution": None,
        "solution_history": [],
    }
    return atom


def _live_atom_count():
    """Count current total atoms in Store at scour time (verify-the-referent on corpus_total)."""
    n = 0
    for p in sorted(os.listdir(ROOT)):
        fp = os.path.join(ROOT, p, "atoms.jsonl")
        if not os.path.isfile(fp):
            continue
        with open(fp, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    n += 1
    return n


def main():
    cert = scour()
    corpus_total = _live_atom_count()
    atom = build_atom(cert, corpus_total=corpus_total)
    out_path = "data/capability_map_atom_DRAFT_pre_skunkworks_FINAL_VET.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(atom, f, indent=2)
    print(f"DRAFT written: {out_path}")
    inv = atom["metadata"]["capability_inventory"]
    print(f"  CERT_CHAIN_GRADE total: {inv['cert_chain_grade_total']}")
    print(f"  PASS total: {inv['positives_total']}")
    print(f"  HIGH-relevance distinct claims: {inv['positives_high_relevance']}")
    print(f"  LOW-relevance replication/sweep: {inv['positives_low_relevance']}")
    print(f"  Substrate-mechanism CORE: {inv['core_total']}")
    print(f"  Applied-domain breadth (5 domains): {inv['applied_domain_total']}")
    print(f"  HARD_FAIL companion: {inv['hard_fail_total']}")
    print(f"  UNSET (flag-don't-auto): {inv['unset_legacy_count']}")


if __name__ == "__main__":
    main()
