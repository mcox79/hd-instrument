"""Skunkworks 2026-06-20 -- CERT-INTEGRITY AUDIT (read-only): retroactively apply this session's disciplines to
the EXISTING cert-grade atoms. Part of the USER "certify the backlog" directive -- certifying that the
ALREADY-certified atoms actually meet the bar (artifacts may have slipped in before these disciplines existed).

Audits the CERT_CHAIN_GRADE experiment_records across 3 dimensions:
  (D1) SATURATION-IN-CERT-SET: a PASS-verdict cert whose key_metrics are a [0,1] family pinned at an extreme
       (>= ceiling) across all values with NO sub-extreme value present (= no failure regime in the recorded
       metrics) -> by-construction-saturation candidate (the pythia-KV pattern, retroactive). NOTE: an atom whose
       key_metrics DO contain a sub-extreme value (e.g. a8's mean_acc drops to 0.09) is NOT flagged -- it reached
       the cliff. Honest: key_metrics is a DISTILLED snapshot; a clean here != fully discriminating (cross-check
       the cell), so this is a CANDIDATE flag, not a verdict.
  (D2) SMOKE-MODE CERTS: run_mode == 'smoke' but provenance_quality == CERT_CHAIN_GRADE -> under-powered-cert
       candidate (smoke is preliminary; a full-run or an explicit justification is the bar). REPORTED for review.
  (D3) GRADE-INFLATION: a cert atom whose depends_on resolves to a SUB-CERT experiment_record (load-bearing
       evidence weaker than the citing atom's grade -- the C/D pattern, in the Store dependency graph). Math/axiom
       deps (math::, T2/, primitives) are NOT flagged (they're a different grade axis).

Read-ONLY. ASCII. Prints a report + optional --json. Exit 0 (audit always completes; flags are REPORTED for
cert-owner review, not a gate -- a flag is a candidate to re-VET, not an automatic downgrade).
"""
from __future__ import annotations
import argparse
import ast
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

PASS_VERDICTS = {"HARD_PASS", "PASS"}
GRADE_ORDER = {  # higher = stronger
    "CERT_CHAIN_GRADE": 7, "MEASURED_MECHANISM": 6, "COST_MODEL": 5, "RESEARCH_FINDING": 4,
    "SMOKE_ONLY": 3, "LEGACY_EXCERPT": 2, "UNVERIFIED": 1, "ARCHIVE": 0,
    "INVENTORY_NON_CERT": 0, "None": 0, None: 0,
}
CLIFF_HINTS = ("cliff", "boundary", "m_crit", "onset", "k_max", "no_forget", "stress")


def kn(a):
    return a.kind.value if hasattr(a.kind, "value") else str(a.kind)


def pq(a):
    return (a.metadata or {}).get("provenance_quality")


def _parse_km(s):
    if isinstance(s, dict):
        return s
    if not isinstance(s, str) or not s.strip() or s.strip() == "{}":
        return {}
    try:
        return ast.literal_eval(s)
    except Exception:
        return {}


def _num_leaves_01(obj):
    out = []
    if isinstance(obj, dict):
        for v in obj.values():
            out += _num_leaves_01(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            out += _num_leaves_01(v)
    elif isinstance(obj, bool):
        pass
    elif isinstance(obj, (int, float)):
        if 0.0 <= float(obj) <= 1.0:
            out.append(float(obj))
    return out


# headline metric extractor (D1 fallback for the 422 atoms whose metrics live in metrics_headline text).
# Match "<metric-name>[@/suffix] = / >= value" where value in [0,1]. Skip threshold parentheticals (HP>=..), counts
# (5/5), N=, latency=, writes, and bare integers. Conservative: extract clear metric=value, else report unscannable.
_METRIC_NAME = r"(?:acc|accuracy|recall|precision|f1|auc|cos|mean_cos|min_cos|max_cut|3sat|clique|fidelity|score|rate|purity)"
_HL_PAT = re.compile(_METRIC_NAME + r"[@\w.]*\s*[><]?=\s*([01](?:\.\d+)?)\b", re.IGNORECASE)
_HL_CLIFF = re.compile(r"cliff|onset|boundary|m_crit|degrad|drop|breaks?\b|forget", re.IGNORECASE)


def _headline_vals(text):
    if not isinstance(text, str):
        return []
    out = []
    for m in _HL_PAT.finditer(text):
        # exclude the threshold parentheticals like "(HP>=0.6 HF<0.3)" -- skip if inside parens immediately preceding
        try:
            v = float(m.group(1))
        except Exception:
            continue
        if 0.0 <= v <= 1.0:
            out.append(v)
    return out


def audit_saturation(md, ceiling=0.999):
    km = _parse_km(md.get("key_metrics"))
    vals = _num_leaves_01(km)
    source = "key_metrics"
    if len(vals) < 3:
        # D1 fallback: parse the headline text
        hl = md.get("metrics_headline") or md.get("verdict_msg") or ""
        hvals = _headline_vals(hl)
        if len(hvals) >= 3:
            vmin, vmax = min(hvals), max(hvals)
            cliff_key = bool(_HL_CLIFF.search(hl))
            flag = (vmin >= ceiling) and (vmax <= 1.0) and not (vmin < ceiling) and not cliff_key
            return {"n_vals": len(hvals), "min": round(vmin, 4), "max": round(vmax, 4), "flag": flag,
                    "cliff_key_present": cliff_key, "source": "headline"}
        return None  # truly unscannable (no structured metrics AND no parseable headline metrics)
    vmin, vmax = min(vals), max(vals)
    pinned = vmin >= ceiling
    # cliff-intent: does key_metrics carry a sub-extreme value OR a cliff-ish key? if so, it reached/recorded a regime
    has_subextreme = vmin < ceiling
    km_keys = " ".join(str(k).lower() for k in (km.keys() if isinstance(km, dict) else []))
    cliff_key = any(h in km_keys for h in CLIFF_HINTS)
    # flag: PASS pinned at ceiling, no sub-extreme value recorded, n>=3 distilled metrics
    flag = pinned and not has_subextreme and not cliff_key
    return {"n_vals": len(vals), "min": round(vmin, 4), "max": round(vmax, 4), "flag": flag,
            "cliff_key_present": cliff_key, "source": source}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--ceiling", type=float, default=0.999)
    ap.add_argument("--show", type=int, default=25, help="max atoms to list per dimension")
    args = ap.parse_args()

    ps = PartitionedStore(Path("data/substrate_index"))
    atoms = list(ps.all_atoms())
    by_id = {}
    for a in atoms:
        by_id[str(a.id)] = a
        by_id[str(a.id).split("::")[-1]] = a
    cert = [a for a in atoms if pq(a) == "CERT_CHAIN_GRADE" and kn(a) == "experiment_record"]

    d1, d2, d3 = [], [], []  # saturation / smoke-cert / grade-inflation
    d1_unscannable = 0
    for a in cert:
        md = a.metadata or {}
        aid = str(a.id)
        verdict = str(md.get("verdict", "")).upper()
        # D1 saturation (only meaningful for PASS verdicts)
        if verdict in PASS_VERDICTS:
            s = audit_saturation(md, args.ceiling)
            if s is None:
                d1_unscannable += 1
            elif s["flag"]:
                d1.append((aid, md.get("verdict"), s["n_vals"], s["min"], s["max"], md.get("run_mode"), s.get("source")))
        # D2 smoke-mode cert
        if str(md.get("run_mode", "")).lower() == "smoke":
            d2.append((aid, md.get("verdict"), md.get("era"), md.get("relevance_tier")))
        # D3 grade-inflation via depends_on
        dep_raw = md.get("depends_on_resolved")
        deps = []
        if isinstance(dep_raw, str) and dep_raw.strip().startswith("["):
            try:
                deps = ast.literal_eval(dep_raw)
            except Exception:
                deps = []
        elif isinstance(dep_raw, list):
            deps = dep_raw
        for d in deps:
            if not isinstance(d, str):
                continue
            tgt = by_id.get(d) or by_id.get(d.split("::")[-1])
            if tgt is None:
                continue
            if kn(tgt) != "experiment_record":
                continue  # math/primitive/axiom deps are a different grade axis -- not flagged
            tg = pq(tgt)
            if GRADE_ORDER.get(tg, 0) < GRADE_ORDER["CERT_CHAIN_GRADE"]:
                d3.append((aid, d, tg))

    summary = {
        "cert_experiment_records": len(cert),
        "D1_saturation_candidates": len(d1),
        "D1_unscannable_headline_only": d1_unscannable,
        "D2_smoke_mode_certs": len(d2),
        "D3_grade_inflation_dep_edges": len(d3),
    }

    if args.json:
        import json as _json
        print(_json.dumps({"summary": summary, "D1": d1[:args.show], "D2": d2[:args.show], "D3": d3[:args.show]},
                          indent=2, default=str))
        return 0

    print("=" * 80)
    print("CERT-INTEGRITY AUDIT v1 (read-only) -- %d CERT_CHAIN_GRADE experiment_records" % len(cert))
    print("-" * 80)
    for k, v in summary.items():
        print("  %-38s %s" % (k, v))
    print("-" * 80)
    print("D1 SATURATION CANDIDATES (PASS pinned at ceiling, no sub-extreme/cliff in key_metrics):")
    if not d1:
        print("  (none -- no cert atom's distilled key_metrics show the pinned-no-cliff pattern)")
    for aid, v, n, mn, mx, rm, src in d1[:args.show]:
        print("  [%s] %s  n=%d min=%.3f max=%.3f run=%s src=%s" % (v, aid, n, mn, mx, rm, src))
    print("-" * 80)
    print("D2 SMOKE-MODE CERTS (run_mode=smoke but CERT_CHAIN_GRADE; under-powered-cert candidates):")
    for aid, v, era, tier in d2[:args.show]:
        print("  [%s] %s  era=%s tier=%s" % (v, aid, era, tier))
    if len(d2) > args.show:
        print("  ... +%d more" % (len(d2) - args.show))
    print("-" * 80)
    print("D3 GRADE-INFLATION (cert atom depends_on a SUB-CERT experiment_record):")
    if not d3:
        print("  (none -- no cert atom leans on sub-cert experimental evidence)")
    for aid, dep, tg in d3[:args.show]:
        print("  %s  --depends_on-->  [%s] %s" % (aid, tg, dep))
    if len(d3) > args.show:
        print("  ... +%d more" % (len(d3) - args.show))
    print("=" * 80)
    print("NOTE: flags are CANDIDATES for cert-owner re-VET, not automatic downgrades. D1 uses distilled")
    print("key_metrics (cross-check the cell); D2 smoke-certs may be deliberately promoted; D3 dep-grade is the")
    print("load-bearing check. Read-only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
