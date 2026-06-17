"""B4 (overnight plan FINAL): run the USER's actual questions as cross-experiment queries against the
atomized EXPERIMENT_RECORD set, and report what the atomization SURFACES vs what manual grep / strategy
prose claimed (91st-rule corroborate-vs-prose). Consumer-pull: the USER is the consumer.

Validates the Tier-3 atomizer payoff (the searchability that Skunkworks's manual 2-min grep demonstrated,
now a one-step query) + exposes silent gaps for second-pass enrichment.

Data source:
  - PRE-APPLY (default): reads the dry-run spec set via atomize_experiment_records (no substrate dependency).
  - POST-APPLY (HDLAB_QUERY_SOURCE=store): reads in-store kind=EXPERIMENT_RECORD atoms (graph-grounded).

Read-only; no mutation; laptop-safe (no NxN).
"""
from __future__ import annotations
import os
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tools.atomize_experiment_records as A
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Corpus


def load_records():
    """Return list of dicts {name, verdict, relevance_tier, provenance_quality, era, run_mode, headline,
    depends_on, key_metrics} from spec set (pre-APPLY) or in-store atoms (post-APPLY)."""
    src = os.environ.get("HDLAB_QUERY_SOURCE", "spec")
    ps = PartitionedStore(A.REPO / "data/substrate_index")
    if src == "store":
        out = []
        for a in ps.all_atoms():
            if str(a.kind.name) != "EXPERIMENT_RECORD":
                continue
            m = a.metadata or {}
            out.append(dict(name=a.id, verdict=m.get("verdict"), relevance_tier=m.get("relevance_tier"),
                            provenance_quality=m.get("provenance_quality"), era=m.get("era"),
                            run_mode=m.get("run_mode"), headline=m.get("metrics_headline"),
                            depends_on=m.get("depends_on_resolved") or [], key_metrics=m.get("key_metrics") or {}))
        return out, "in-store EXPERIMENT_RECORD atoms (post-APPLY)"
    # pre-APPLY: build specs from dry-run
    allq, pt, cs = A.build_atom_index(ps)
    recs, _ = A.discover()
    out = []
    for r in recs:
        s = A.build_atom_spec(r, allq, pt, cs)
        md = s["metadata"]
        out.append(dict(name=r["name"], verdict=s["verdict"], relevance_tier=s["relevance_tier"],
                        provenance_quality=s["provenance_quality"], era=s["era"], run_mode=s["run_mode"],
                        headline=md.get("metrics_headline"), depends_on=s["depends_on"],
                        key_metrics=md.get("key_metrics") or {}))
    return out, "dry-run spec set (pre-APPLY; same content as atoms-to-be)"


def q1_pre_substrate(recs):
    pre = [r for r in recs if r["era"] == "PRE_SUBSTRATE_BUILD"]
    by_verdict = Counter(r["verdict"] for r in pre)
    by_prov = Counter(r["provenance_quality"] for r in pre)
    # notable foundational series (the ones the USER worried about losing)
    series = ("m1", "m2", "m3", "m4", "m5", "m6", "m7", "scaling", "depth", "wave13", "wave14", "charlm",
              "pointer_chain", "traceable_multi_hop", "resonator", "capacity")
    notable = []
    for key in series:
        hits = [r for r in pre if key in r["name"].lower()]
        if hits:
            notable.append((key, len(hits)))
    print(f"\n== Q1: experiments BEFORE the substrate build (era=PRE_SUBSTRATE_BUILD) ==")
    print(f"   count: {len(pre)} of {len(recs)}")
    print(f"   by verdict: {dict(by_verdict.most_common())}")
    print(f"   by provenance_quality: {dict(by_prov.most_common())}")
    print(f"   notable foundational series present: {dict(notable)}")


def q2_best_results(recs):
    high = [r for r in recs if r["relevance_tier"] == "HIGH"]
    cert_pass = [r for r in recs if r["provenance_quality"] == "CERT_CHAIN_GRADE"
                 and r["verdict"] in ("PASS", "LOAD_BEARING")]
    print(f"\n== Q2: best results (metric-grounded; current-verified-linkage) ==")
    print(f"   HIGH relevance_tier: {len(high)}; CERT_CHAIN_GRADE + PASS/LOAD_BEARING: {len(cert_pass)}")
    print(f"   top cert-grade positives (headline):")
    for r in sorted(cert_pass, key=lambda x: x["name"])[:12]:
        print(f"     [{r['verdict']}/{r['relevance_tier']}] {r['name'][:48]} :: {str(r['headline'])[:80]}")


def q3_analogous_p2(recs):
    # reproduce Skunkworks's manual capacity-analog grep as a one-step query
    fam = ("capacity", "cliff", "resonator", "decompos", "factoriz", "k_sweep", "k4", "alpha_c", "frady")
    hits = [r for r in recs if any(k in (r["name"].lower() + " " + str(r["headline"]).lower()) for k in fam)]
    by_verdict = Counter(r["verdict"] for r in hits)
    print(f"\n== Q3: analogous to P2 GATE-F capacity envelope (capacity-cliff / resonator / decompose family) ==")
    print(f"   count: {len(hits)} (one-step query == Skunkworks's manual 2-min grep)")
    print(f"   by verdict: {dict(by_verdict.most_common())}")
    # the corrected metric-grounded prior art (236e/236f)
    keys = ("decomposition_resonator_alpha05", "resonator_k4_multiaxis", "resonator_capacity_rescue",
            "resonator_factorization", "decompose_k_cliff", "scaling_capacity")
    print(f"   corrected-prior-art records (236e/236f bind-to-metrics):")
    for r in hits:
        if any(k in r["name"].lower() for k in keys):
            print(f"     [{r['verdict']}/{r['provenance_quality']}] {r['name'][:50]} :: {str(r['headline'])[:78]}")


def main():
    recs, src = load_records()
    print("=" * 84)
    print(f"B4 USER-QUESTION cross-experiment validation | source: {src} | {len(recs)} records")
    print("=" * 84)
    q1_pre_substrate(recs)
    q2_best_results(recs)
    q3_analogous_p2(recs)
    print("\n" + "=" * 84)
    print("NOTE: pre-APPLY pass runs on the spec set; finalize against the in-store graph post-APPLY")
    print("(HDLAB_QUERY_SOURCE=store) for DEPENDS_ON/ANALOGOUS_TO graph-walk answers.")
    print("=" * 84)
    return 0


if __name__ == "__main__":
    sys.exit(main())
