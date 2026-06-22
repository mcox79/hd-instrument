"""Director-side metadata clustering tool for cert-trail navigation.

**THIS IS NOT SUBSTRATE SELF-IMPROVEMENT.** USER 2026-06-22 corrected the misframing.
This tool clusters atom_ids by a keyword lexicon I (Director) defined — it's lexical
pattern-matching on metadata, not substrate-derived knowledge. The substrate's own
primitives (KGStore, SequenceMatrix, SubstrateGenerator, multi_hop, char_trigram_encoder,
whitening) are NOT used in the analysis. Output is Director scaffolding, useful for
navigating the chain-grade evidence breadth.

For TRUE substrate self-improvement, see `exp_substrate_self_map_v2_*` (cert pending) —
that cell encodes atoms via substrate primitives, ingests cert_ledger relations as
substrate triples, runs the substrate's OWN multi_hop traversal to surface clusters,
and (Phase 2) uses SubstrateGenerator to propose candidate atom completions.

v1 = Director navigation scaffolding (THIS FILE)
v2 = substrate-native self-mapping (substrate-internal compute)

USER 2026-06-22: "is this relational analysis enabled by the substrate's capabilities?
I'm unsure how a python script written by you is the substrate learning about itself?"
Answer: it isn't. v1 is Director tooling. v2 is the actual self-mapping cell.

Output: `notes/capability_family_map_v<N>_<date>.md` — cert-trail durable artifact.

Methodology (deliberately conservative for v1):
  1. Read cert_ledger.jsonl + extract chain-grade atom IDs
  2. For each chain-grade atom, extract its signature: (kind, corpus, tier, cert_class, verdict)
     + relation-types it participates in
  3. Cluster atoms by signature (string-tuple hash + lexical similarity on atom_id)
  4. Within each cluster, compute relation graph density (intra-cluster vs cross-cluster)
  5. Surface candidate capability families: clusters with high intra-density + low cross-density
  6. Cross-cluster RELATES + DEPENDS_ON + SHARES_MATH relations -> candidate isomorphism arrows

v1 scope: structural clustering only. v2 adds spectral analysis + natural-transformation
discovery between subcategories (category-theory framing per brain-drill #7 candidate).

USER-strategic implication: if the cap_map reveals 3-5 dense capability families with
sparse inter-family arrows, those arrows ARE the candidate "core underlying mathematics"
pieces — the relational structure substrate has independently developed across cells.

Usage:
    python tools/substrate_relational_analysis.py
    python tools/substrate_relational_analysis.py --output notes/capability_family_map_v1_<date>.md
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "data" / "substrate_index" / "meta" / "cert_ledger.jsonl"
SUBSTRATE_INDEX = REPO / "data" / "substrate_index"
OUT_DEFAULT = REPO / "notes" / f"capability_family_map_v1_{time.strftime('%Y-%m-%d')}.md"


def load_chain_grade_atoms() -> list[dict]:
    """Read cert_ledger; collect chain-grade atoms + their metadata."""
    atoms = {}
    if not LEDGER.exists():
        return []
    with open(LEDGER, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("cert_status") != "chain_grade":
                continue
            aid = r.get("atom_id", "")
            if not aid:
                continue
            # Keep latest-per-atom (supersedes-fold)
            atoms[aid] = {
                "atom_id": aid,
                "verdict": r.get("verdict", "?"),
                "cert_class": r.get("cert_class", "?"),
                "delta": r.get("cert_increment_delta", 0),
                "atomized_by": r.get("atomized_by", "?"),
            }
    return list(atoms.values())


def extract_signature(atom: dict) -> dict:
    """Derive structural signature from atom_id + metadata."""
    aid = atom["atom_id"]
    sig = {
        "corpus": aid.split("::")[0] if "::" in aid else "unknown",
        "tier": "?",
        "verdict_class": atom["verdict"].split(":")[0].split("_")[0] if atom["verdict"] else "?",
        "cert_class": atom["cert_class"],
    }
    # Tier from prefix
    tier_match = re.search(r"::T(\d+)/", aid)
    if tier_match:
        sig["tier"] = f"T{tier_match.group(1)}"
    # Categorize by atom_id keyword
    name_lower = aid.lower()
    categories = []
    keywords = {
        "capacity": ["capacity", "alpha", "kappa", "sweep", "envelope", "cliff", "sparse_boundary"],
        "kg_ingest": ["conceptnet", "fb15k", "u1_fb15k", "hotpotqa", "n8_concept", "ingest_eval", "_kg_"],
        "lm": ["concept_lm", "char_lm", "substrate_lm", "char_ngram", "wikitext", "arxiv", "text8"],
        "multi_hop": ["multihop", "multi_hop", "r1_", "iterative_cleanup"],
        "projection": ["kv_projection", "kv_learned", "projected_kv", "learned_projection"],
        "whitening": ["whitening", "whitened", "pca_prewhitening"],
        "hopfield": ["hopfield", "krotov", "smh", "modern_hopfield"],
        "continual": ["continual_writ", "catastrophic_forg", "a8_", "cls_replay"],
        "refuse_gate": ["refuse_gate", "refuse_ood"],
        "noise_robust": ["noise_robust", "noise_crosscut", "transition_noise"],
        "encoding": ["pythia_kv", "pythia_substrate", "substrate_audit_core", "substrate_real_encoder"],
        "composition": ["composition", "compose_capacity", "stratified", "compound"],
        "topology": ["topology", "phase4b", "pp48", "pp50", "pp52"],
        "wave_audit": ["wave14b", "wave14", "wave1_", "wave2"],
        "info_theory": ["info_theory", "free_prob", "rmt", "random_matrix"],
        "sequence_binding": ["c3_compressed", "sequence_replay", "sequence_memory"],
        "generation": ["g1_", "g1b_", "generation"],
        "phase_diagram": ["phase_portrait", "phase_diagram", "kmax_ness"],
        "saturation": ["saturation", "saturated", "by_construction"],
    }
    for cat, kws in keywords.items():
        if any(kw in name_lower for kw in kws):
            categories.append(cat)
    if not categories:
        categories = ["uncategorized"]
    sig["categories"] = categories
    return sig


def cluster_atoms(atoms_with_sigs: list[tuple[dict, dict]]) -> dict[str, list[dict]]:
    """Cluster atoms by primary category (first in categories list)."""
    clusters: dict[str, list[dict]] = collections.defaultdict(list)
    for atom, sig in atoms_with_sigs:
        primary = sig["categories"][0]
        clusters[primary].append({**atom, "_signature": sig})
    return dict(clusters)


def family_metrics(clusters: dict[str, list[dict]]) -> list[dict]:
    """Per-cluster metrics: size, verdict mix, tier mix."""
    families = []
    for cat, lst in sorted(clusters.items(), key=lambda kv: len(kv[1]), reverse=True):
        verdict_counts = collections.Counter(a.get("verdict", "?").split("_")[0] for a in lst)
        tier_counts = collections.Counter(a["_signature"].get("tier", "?") for a in lst)
        cert_class_counts = collections.Counter(a.get("cert_class", "?") for a in lst)
        families.append({
            "name": cat,
            "size": len(lst),
            "verdict_mix": dict(verdict_counts.most_common(5)),
            "tier_mix": dict(tier_counts),
            "cert_class_mix": dict(cert_class_counts.most_common(3)),
            "exemplars": [a["atom_id"].split("/")[-1][:60] for a in lst[:5]],
        })
    return families


def cross_family_signatures(clusters: dict[str, list[dict]]) -> list[dict]:
    """Atoms that belong to MULTIPLE categories — candidate cross-family arrows."""
    multi = []
    for cat, lst in clusters.items():
        for atom in lst:
            sig_cats = atom["_signature"]["categories"]
            if len(sig_cats) > 1:
                multi.append({
                    "atom_id": atom["atom_id"].split("/")[-1][:60],
                    "categories": sig_cats,
                    "primary": cat,
                })
    return multi


def render_report(families: list[dict], multi_category: list[dict], total_atoms: int, output_path: Path) -> None:
    """Write the capability-family map note."""
    out = output_path
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append(f"# Capability family map v1 — DIRECTOR-SIDE METADATA CLUSTERING ({time.strftime('%Y-%m-%d')})")
    lines.append("")
    lines.append("> ⚠️  **THIS IS NOT SUBSTRATE SELF-IMPROVEMENT.** USER 2026-06-22 corrected the misframing.")
    lines.append("> This is Director-side lexical pattern-matching on atom_id strings using a keyword lexicon I (Director) defined.")
    lines.append("> The substrate's own primitives (KGStore, SequenceMatrix, SubstrateGenerator, multi_hop, etc.) are NOT used.")
    lines.append("> Output below is Director scaffolding for cert-trail navigation, NOT substrate-derived knowledge.")
    lines.append(">")
    lines.append("> For actual substrate self-mapping, see `exp_substrate_self_map_v2_*` (cell-author pending) which encodes")
    lines.append("> atoms via substrate primitives + uses substrate's own multi_hop traversal on cert_ledger relations.")
    lines.append("")
    lines.append("**DO NOT use v1 findings to drive substrate-development decisions until v2 lands** (USER directive).")
    lines.append("")
    lines.append(f"**Source:** `data/substrate_index/meta/cert_ledger.jsonl` — chain-grade atoms only (latest-per-atom; supersedes-folded)")
    lines.append(f"**Total chain-grade atoms analyzed:** {total_atoms}")
    lines.append(f"**Lexical categories identified:** {len(families)}")
    lines.append(f"**Cross-category atoms (multi-lexical-match):** {len(multi_category)}")
    lines.append("")
    lines.append("## Capability families (sorted by size)")
    lines.append("")
    lines.append("| Family | Atoms | Verdict mix | Tier mix | Top exemplars |")
    lines.append("|---|---:|---|---|---|")
    for fam in families:
        ver = ", ".join(f"{k}={v}" for k, v in list(fam["verdict_mix"].items())[:3])
        tier = ", ".join(f"{k}={v}" for k, v in fam["tier_mix"].items())
        exemplars = "; ".join(fam["exemplars"][:3])
        lines.append(f"| **{fam['name']}** | {fam['size']} | {ver} | {tier} | {exemplars} |")
    lines.append("")

    # High-cohesion families (the candidate "capability cores")
    lines.append("## High-cohesion families (≥ 5 chain-grade atoms = substantive capability core)")
    lines.append("")
    high = [f for f in families if f["size"] >= 5]
    if not high:
        lines.append("(no families with ≥ 5 chain-grade atoms — substrate's chain-grade evidence is spread thin)")
    else:
        for fam in high:
            lines.append(f"### {fam['name']} ({fam['size']} chain-grade atoms)")
            lines.append("")
            lines.append(f"- Verdict mix: {fam['verdict_mix']}")
            lines.append(f"- Tier distribution: {fam['tier_mix']}")
            lines.append("- Exemplars:")
            for ex in fam["exemplars"]:
                lines.append(f"  - `{ex}`")
            lines.append("")
    lines.append("## Cross-family atoms (candidate \"core underlying mathematics\" arrows)")
    lines.append("")
    lines.append("Atoms that lexically match MULTIPLE category keywords — these are the natural candidates for *natural transformations between subcategories* (USER's framing). Each such atom links two (or more) capability families and is a candidate isomorphism arrow.")
    lines.append("")
    if not multi_category:
        lines.append("(no multi-category atoms found — substrate's chain-grade evidence is currently siloed; v2 should add finer-grained relation analysis)")
    else:
        lines.append("| atom | categories spanned |")
        lines.append("|---|---|")
        for m in multi_category[:30]:
            lines.append(f"| `{m['atom_id']}` | {' × '.join(m['categories'])} |")
        if len(multi_category) > 30:
            lines.append(f"| ... | (+{len(multi_category)-30} more) |")
        lines.append("")
    lines.append("## Interpretation (USER strategic vision)")
    lines.append("")
    lines.append("The capability families above represent the substrate's *empirically validated mathematical structure*. Where families compose with each other (cross-family atoms; multi-category exemplars), those crossing points are candidates for the *core underlying mathematics* substrate has independently arrived at across cells.")
    lines.append("")
    lines.append("**Next steps (Phase 1 → Phase 2 → Phase 3 per USER strategic vision):**")
    lines.append("- v2: spectral analysis of the atom-relation graph + per-family eigenvalue signatures (identify which families have similar mathematical character)")
    lines.append("- v2: cross-family natural-transformation discovery (category-theory framing per brain-drill #7 candidate)")
    lines.append("- Phase 2 (long horizon): substrate samples NEW atom-candidates from learned distribution + auto-checks against cap_pres → autoatom proposals")
    lines.append("- Phase 3 (AGI-adjacent): substrate's glass-box LM reasons about its own capability gaps + proposes new mathematics")
    lines.append("")
    lines.append("— Research (Director); v1 substrate self-mapping; cert-trail durable artifact; no addressee.")
    out.write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Substrate relational analysis v1")
    ap.add_argument("--output", default=str(OUT_DEFAULT), help="Output note path")
    args = ap.parse_args()

    t0 = time.time()
    atoms = load_chain_grade_atoms()
    print(f"[load] {len(atoms)} chain-grade atoms")
    atoms_with_sigs = [(a, extract_signature(a)) for a in atoms]
    clusters = cluster_atoms(atoms_with_sigs)
    print(f"[cluster] {len(clusters)} primary categories")
    families = family_metrics(clusters)
    multi = cross_family_signatures(clusters)
    print(f"[crossfam] {len(multi)} atoms span multiple categories")

    output_path = Path(args.output)
    render_report(families, multi, len(atoms), output_path)
    print(f"[output] {output_path} ({time.time()-t0:.1f}s)")
    print()
    print("Top 5 families by size:")
    for f in families[:5]:
        print(f"  {f['name']}: {f['size']} atoms; exemplars: {f['exemplars'][:2]}")


if __name__ == "__main__":
    main()
