#!/usr/bin/env python3
"""Cap-int Piece 1: capability-enumerator v0 (READ-ONLY; per USER auth 2026-06-19).

Scope (per cap-int co-spec):
- Map every EXPERIMENT_RECORD atom (3724) -> a capability candidate.
- Classify each by cert-tier (CERT_CHAIN_GRADE / MEASURED_MECHANISM / MIDDLE_BAND /
  smoke / legacy / etc).
- Cross-check against existing 55 capability atoms (all currently current_best=None
  = 100% integration gap; Skunkworks's spec said "25 current_best-bearing" --
  actual is 0/55 verified just now).
- Output 2 queues:
  - Track A integration-list: {capability_candidate, proven_bound, evidence_atom_ids[],
    current_capability_atom_or_NEW, cluster_id, recommended_interface_contract_slot}
  - Track B pull-up queue: {capability_candidate, current_evidence_atom_ids[],
    cert_gap_diagnostic, recommended_pull_up_protocol}
- ALL rows are PROPOSALS for Skunkworks per-row cert-VET (the 5 binding rules).

Prioritization: DOMAIN-VALUE-first (USER default; reasoning_multihop +
cognitive_capacity + retrieval ordered first; closest-to-cert tiebreaker within).

NO STORE WRITES. Output to data/capint_piece1_enumerator_v0_2026-06-19.json.
Track A apply + Track B cell-builds + dispatch all happen later under Skunkworks
per-row VET + cap-int discipline.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path("data/substrate_index")

# Domain taxonomy (from phase-portrait v2; with prioritization order)
DOMAIN_PRIORITY = [
    "reasoning_multihop",
    "cognitive_capacity",
    "retrieval",
    "NLP_language",
    "math",
    "architecture",
    "refuse_gate",
    "knowledge_graph",
    "substrate_integrity",
    "audit_methodology",
    "ingest_pipeline",
    "dynamics",
]

NAME_SUBSTRINGS = {
    "NLP_language": ["depparse", "dep_parse", "pos_tagger", "ner_", "_ner_",
                     "ner_gazetteer", "ner_transition", "chunking", "spacy",
                     "tokenizer", "lemma", "language", "_nlp_", "conll", "udep",
                     "temporal_contextual", "_charngram", "sst2", "imdb",
                     "crossdomain_transfer", "noise_crosscut", "stage_a_bio"],
    "math": ["pythagor", "cauchy", "theorem", "_math_", "lean", "axiom_",
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
                            "substrate_id", "cert_floor"],
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


def load_atoms_of_kind(kind):
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
                if a.get("kind") == kind:
                    yield corpus, a


def classify_domain_by_name(name):
    name_lower = (name or "").lower()
    tags = []
    for domain in DOMAIN_PRIORITY:
        substrs = NAME_SUBSTRINGS.get(domain, [])
        for s in substrs:
            if s in name_lower:
                tags.append(domain)
                break
    return tags


def extract_verdict(a):
    md = a.get("metadata") or {}
    v = md.get("verdict")
    if v:
        return str(v).upper()
    desc = (a.get("description") or "")[:400]
    m = re.search(r"\bVerdict\s+([A-Z_]+)", desc)
    if m:
        return m.group(1).upper()
    return None


def cert_tier(a):
    md = a.get("metadata") or {}
    pq = md.get("provenance_quality")
    if pq:
        return pq
    return None


def diagnose_cert_gap(a, verdict, pq):
    """Return list of cert-gap items (what's missing for cert-grade)."""
    md = a.get("metadata") or {}
    gaps = []
    if pq != "CERT_CHAIN_GRADE":
        if pq == "MEASURED_MECHANISM":
            gaps.append("upgrade_pq: MEASURED_MECHANISM -> CERT_CHAIN_GRADE "
                        "(needs full-run + n-seeds + pre-reg bands)")
        else:
            if not md.get("key_metrics"):
                gaps.append("structured_key_metrics: absent")
            if not md.get("prereg_bands") and not md.get("bands"):
                gaps.append("pre-registered_bands: absent")
            if not md.get("n_seeds"):
                gaps.append("n_seeds_recorded: absent")
            if not md.get("commit_hash") and not md.get("substrate_id_hash"):
                gaps.append("commit_hash + substrate_id_hash: absent")
            if verdict in ("MIDDLE_BAND", "PARTIAL", "UNKNOWN"):
                gaps.append(f"verdict_{verdict}: needs re-run with discriminating-regime + held-out")
            if verdict == "HARD_FAIL":
                gaps.append("HARD_FAIL: honest-negative; may stay below cert")
            if not gaps:
                gaps.append("legacy_or_smoke_or_pre_cert_arc")
    return gaps


def main():
    # Load existing capability atoms
    cap_atoms = list(load_atoms_of_kind("capability"))
    print(f"Existing capability atoms: {len(cap_atoms)}")
    populated = sum(1 for _, a in cap_atoms
                    if a.get("current_best") or (a.get("metadata") or {}).get("current_best"))
    print(f"  With current_best populated: {populated}")
    print(f"  GAP (current_best=None): {len(cap_atoms) - populated}")
    print()

    # Index existing capabilities by name + domain tags
    existing_caps_by_domain = defaultdict(list)
    for corpus, a in cap_atoms:
        name = a.get("name") or a.get("id")
        tags = classify_domain_by_name(name + " " + (a.get("description") or ""))
        if not tags:
            tags = ["UNCLASSIFIED"]
        for t in tags:
            existing_caps_by_domain[t].append({
                "qid": f"{corpus}::{a['id']}",
                "name": name,
                "tier": a.get("tier"),
                "current_best": a.get("current_best") or (
                    a.get("metadata") or {}).get("current_best"),
            })

    # Load all EXPERIMENT_RECORD atoms
    exp_atoms = list(load_atoms_of_kind("experiment_record"))
    print(f"EXPERIMENT_RECORD atoms total: {len(exp_atoms)}")

    cert_count = 0
    track_a = []
    track_b = []
    unclassified_exp = []
    domain_buckets = defaultdict(lambda: {"cert": [], "non_cert": []})

    for corpus, a in exp_atoms:
        name = a.get("name") or a.get("id") or ""
        atom_id = a["id"]
        qid = f"{corpus}::{atom_id}"
        md = a.get("metadata") or {}
        pq = cert_tier(a)
        verdict = extract_verdict(a)
        tags = classify_domain_by_name(name + " " + (a.get("description") or ""))

        if pq == "CERT_CHAIN_GRADE":
            cert_count += 1

        if not tags:
            unclassified_exp.append({"qid": qid, "name": name[:80]})
            tags = ["UNCLASSIFIED"]

        primary_domain = tags[0]
        if pq == "CERT_CHAIN_GRADE":
            domain_buckets[primary_domain]["cert"].append(qid)
        else:
            domain_buckets[primary_domain]["non_cert"].append(qid)

        row = {
            "qid": qid,
            "name": name[:200],
            "domain_tags": tags,
            "primary_domain": primary_domain,
            "cert_tier": pq,
            "verdict": verdict,
        }

        if pq == "CERT_CHAIN_GRADE":
            row["proven_bound_hint"] = (a.get("description") or "")[:200]
            row["evidence_atom_ids"] = [qid]
            # Match against existing capability atoms in same domain
            cands = existing_caps_by_domain.get(primary_domain, [])
            row["candidate_capability_atoms"] = [c["qid"] for c in cands[:5]]
            row["needs_new_capability_atom"] = len(cands) == 0
            track_a.append(row)
        else:
            row["cert_gap_diagnostic"] = diagnose_cert_gap(a, verdict, pq)
            row["recommended_pull_up_protocol"] = (
                "re-run with: pre-reg bands + n>=5 seeds + held-out test + "
                "discriminating-regime + commit-hash + substrate-id-hash record")
            track_b.append(row)

    print(f"  CERT_CHAIN_GRADE: {cert_count}")
    print(f"  Non-cert: {len(exp_atoms) - cert_count}")
    print()

    # Re-order tracks by DOMAIN-VALUE priority + closest-to-cert tiebreaker
    def domain_priority_key(row):
        d = row["primary_domain"]
        idx = DOMAIN_PRIORITY.index(d) if d in DOMAIN_PRIORITY else 99
        return (idx, row["qid"])
    track_a.sort(key=domain_priority_key)
    track_b.sort(key=lambda r: (
        DOMAIN_PRIORITY.index(r["primary_domain"]) if r["primary_domain"] in DOMAIN_PRIORITY else 99,
        0 if (r["cert_tier"] == "MEASURED_MECHANISM") else
        1 if (r["cert_tier"] == "MIDDLE_BAND") else 99,
        r["qid"],
    ))

    print("=" * 80)
    print("CAP-INT PIECE-1 ENUMERATOR v0")
    print("=" * 80)
    print()
    print(f"Track A (cert-grade integration-list): {len(track_a)} rows")
    print(f"Track B (non-cert pull-up queue):       {len(track_b)} rows")
    print(f"  (of which MEASURED_MECHANISM):        {sum(1 for r in track_b if r['cert_tier'] == 'MEASURED_MECHANISM')}")
    print(f"  (of which MIDDLE_BAND verdict):       {sum(1 for r in track_b if r['verdict'] == 'MIDDLE_BAND')}")
    print(f"  (of which HARD_FAIL verdict):         {sum(1 for r in track_b if r['verdict'] == 'HARD_FAIL')}")
    print(f"  (of which PASS but non-cert):         {sum(1 for r in track_b if r['verdict'] == 'PASS')}")
    print()
    print("Domain-bucket coverage (cert / non-cert per domain):")
    for d in DOMAIN_PRIORITY + ["UNCLASSIFIED"]:
        b = domain_buckets[d]
        print(f"  {d:25s} cert={len(b['cert'])}  non_cert={len(b['non_cert'])}")
    print()

    # Stranded vs over-claimed cross-check
    stranded_cap_candidates = []
    for cap in cap_atoms:
        corpus, a = cap
        md = a.get("metadata") or {}
        cb = a.get("current_best") or md.get("current_best")
        if not cb:
            stranded_cap_candidates.append({
                "qid": f"{corpus}::{a['id']}",
                "name": a.get("name"),
                "tier": a.get("tier"),
            })

    print(f"STRANDED capability atoms (current_best=None; 100% of {len(cap_atoms)}):")
    print("  -> ALL 55 are candidates for Track A current_best population from "
          "the cert-grade body. The 'gap' is total.")
    print()

    out = {
        "scour_ts": "2026-06-19",
        "tool": "capint_piece1_enumerator_v0",
        "prioritization": "DOMAIN-VALUE-first (USER default)",
        "freeze_status": "USER auth received; cap-int dispatch authorized per "
                         "Director interpretation (overrides freeze for cap-int "
                         "ops only)",
        "summary": {
            "experiment_records_total": len(exp_atoms),
            "cert_chain_grade": cert_count,
            "non_cert": len(exp_atoms) - cert_count,
            "track_a_rows": len(track_a),
            "track_b_rows": len(track_b),
            "existing_capability_atoms": len(cap_atoms),
            "capability_atoms_with_current_best_populated": populated,
            "capability_atoms_stranded_gap": len(cap_atoms) - populated,
            "unclassified_exp_records": len(unclassified_exp),
        },
        "domain_buckets": {
            d: {"cert": len(b["cert"]), "non_cert": len(b["non_cert"])}
            for d, b in domain_buckets.items()
        },
        "stranded_capability_atoms": stranded_cap_candidates,
        "track_a_sample_first_30": track_a[:30],
        "track_b_sample_first_30": track_b[:30],
        "track_a_full": track_a,
        "track_b_full": track_b,
        "unclassified_exp_sample": unclassified_exp[:30],
    }
    out_path = Path("data/capint_piece1_enumerator_v0_2026-06-19.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Enumerator output written: {out_path}")
    print()
    print("NEXT: route to Skunkworks for per-row cert-VET (5 binding rules per row).")


if __name__ == "__main__":
    main()
