"""Phase D A1: cross-experiment EVIDENCE-BASE AUDIT over the EXPERIMENT_RECORD atoms (read-only).

Full-corpus complement to Testbed's C4 scorecard reconciliation (C4 audited 5 specific scorecard rows; this
audits all ~1935 records). Surfaces the substrate's evidence-base shape: how many positive results rest on
cert-chain-grade vs legacy/smoke/unverified evidence -- the over-claim-RISK POOL (an audit surface, NOT a list
of confirmed over-claims; a smoke HARD_PASS is honest AS a smoke result -- it is only an over-claim if a
SCORECARD presents it as more). Scorecard revision is Director/USER domain (18th-rule); this is the data.

Read-only; no mutation; laptop-safe; deterministic (reads atom metadata fields the atomizer populated).
"""
from __future__ import annotations
import sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.substrate_index.partition import PartitionedStore

PROVS = ["CERT_CHAIN_GRADE", "LEGACY_EXCERPT", "SMOKE_ONLY", "UNVERIFIED"]
TIERS = ["HIGH", "MEDIUM", "LOW", "ARCHIVE"]


def md(a, k):
    return (a.metadata or {}).get(k)


def main():
    ps = PartitionedStore(Path(__file__).resolve().parents[1] / "data/substrate_index")
    exp = [a for a in ps.all_atoms() if str(a.kind.name) == "EXPERIMENT_RECORD"]
    print(f"=== EVIDENCE-BASE AUDIT | {len(exp)} EXPERIMENT_RECORD atoms | Phase D A1 (full-corpus; complements C4) ===\n")

    # 1. relevance_tier x provenance_quality cross-tab
    ct = defaultdict(Counter)
    for a in exp:
        ct[md(a, "relevance_tier")][md(a, "provenance_quality")] += 1
    print("relevance_tier x provenance_quality:")
    print(f"  {'tier':<8} " + " ".join(f"{p[:11]:>12}" for p in PROVS) + f"{'row_total':>11}")
    for t in TIERS:
        row = [ct[t].get(p, 0) for p in PROVS]
        print(f"  {t:<8} " + " ".join(f"{v:>12}" for v in row) + f"{sum(row):>11}")
    col = {p: sum(ct[t].get(p, 0) for t in TIERS) for p in PROVS}
    print(f"  {'TOTAL':<8} " + " ".join(f"{col[p]:>12}" for p in PROVS) + f"{sum(col.values()):>11}")

    # 2. era x provenance
    era = defaultdict(Counter)
    for a in exp:
        era[md(a, "era")][md(a, "provenance_quality")] += 1
    print("\nera x provenance_quality:")
    for e in ("PRE_SUBSTRATE_BUILD", "SUBSTRATE_BUILD"):
        print(f"  {e:<20} " + " ".join(f"{p[:4]}={era[e].get(p,0)}" for p in PROVS))

    # 3. OVER-CLAIM RISK POOL: HIGH/MEDIUM relevance + positive verdict but NON-cert provenance
    risk = [a for a in exp if md(a, "relevance_tier") in ("HIGH", "MEDIUM")
            and md(a, "verdict") in ("PASS", "LOAD_BEARING") and md(a, "provenance_quality") != "CERT_CHAIN_GRADE"]
    print(f"\nOVER-CLAIM RISK POOL (HIGH/MEDIUM + PASS/LOAD_BEARING but NOT cert-grade): {len(risk)}")
    print("  (audit surface -- NOT confirmed over-claims; a smoke HARD_PASS is honest AS smoke. Scorecard"
          " revision = Director/USER per 18th-rule.)")
    hi_risk = [a for a in risk if md(a, "relevance_tier") == "HIGH"]
    print(f"  of which HIGH-relevance (the sharpest audit targets): {len(hi_risk)}")
    for a in sorted(hi_risk, key=lambda x: x.id)[:20]:
        print(f"    [{md(a,'provenance_quality')}] {a.id[:54]} :: {str(md(a,'metrics_headline'))[:55]}")

    # 4. genuinely solid foundation
    solid = [a for a in exp if md(a, "provenance_quality") == "CERT_CHAIN_GRADE" and md(a, "verdict") in ("PASS", "LOAD_BEARING")]
    print(f"\nCERT-GRADE-BACKED positives (the genuinely solid wins): {len(solid)}")
    for a in sorted(solid, key=lambda x: x.id):
        print(f"    {a.id[:56]} :: {str(md(a,'metrics_headline'))[:52]}")

    # 5. REFINEMENT (verify-before-asserting on the risk pool): many risk entries are LEGACY versions of a
    # capability that ALSO has a CERT-GRADE sibling (same capability family). Those are NOT over-claim risks --
    # the capability IS cert-validated by the sibling; the legacy atom is just an older record. Sharpen the pool
    # by a deterministic capability-family key (first 2 underscore-tokens of the name, after stripping run-mode
    # suffixes). This is APPROXIMATE grouping; flag, don't over-claim.
    def fam(a):
        stem = a.id.split("/")[-1]
        for suf in ("_smoke", "_cpu_v1", "_cpu_v2", "_gpu_v1", "_v1", "_v2", "_v3"):
            if stem.endswith(suf):
                stem = stem[:-len(suf)]
        toks = [t for t in stem.replace("EXP_", "").split("_") if t][:2]
        return "_".join(toks)
    cert_fams = {fam(a) for a in solid}
    hi_risk = [a for a in exp if md(a, "relevance_tier") == "HIGH" and md(a, "verdict") in ("PASS", "LOAD_BEARING")
               and md(a, "provenance_quality") != "CERT_CHAIN_GRADE"]
    no_sibling = [a for a in hi_risk if fam(a) not in cert_fams]
    with_sibling = [a for a in hi_risk if fam(a) in cert_fams]
    print(f"\nHIGH-risk SHARPENED (cert-grade-sibling check; approximate family grouping):")
    print(f"  HIGH-risk total: {len(hi_risk)}")
    print(f"  ...with a cert-grade sibling (capability IS validated elsewhere; NOT a real over-claim): {len(with_sibling)}")
    for a in sorted(with_sibling, key=lambda x: x.id):
        print(f"      sibling-covered: {a.id[:54]} (family '{fam(a)}')")
    print(f"  ...NO cert-grade sibling (the GENUINELY thin-evidence HIGH claims -- sharpest audit targets): {len(no_sibling)}")
    for a in sorted(no_sibling, key=lambda x: x.id):
        print(f"      NO-sibling: [{md(a,'provenance_quality')}] {a.id[:50]} :: {str(md(a,'metrics_headline'))[:45]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
