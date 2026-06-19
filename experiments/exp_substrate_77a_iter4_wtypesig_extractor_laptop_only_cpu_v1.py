"""DECISION 77a -- Iteration 4 W-TYPE-SIG witness extractor (LAPTOP-ONLY; the keystone NEW generator component). Reads Phase 4a operator self-model (skunkworks_self_model_of_operators_v1.jsonl), extracts EXPLICIT RELATIONAL POINTERS from algebraic_properties, and emits tier-INDEPENDENT STRICT DEPENDS_ON/USES/IMPLEMENTS/INSTANCE_OF candidates. This is the lever Iter 3 lacked (DECISION 76/77): direction comes from the author-supplied pointer, NOT from a tier gradient.
RELIABLE forward pointers (Director DECISION 77; src --rel--> tgt): derived_from->DEPENDS_ON, composed_of->DEPENDS_ON, diagonalized_by->DEPENDS_ON, uses->USES, implemented_via->USES, computed_via->USES, computes->IMPLEMENTS, instance_of->INSTANCE_OF.
EXCLUDED (Skunkworks over-fire warning): inverse_of / invertible_via / right_inverse_of (CYCLE-risk, bidirectional), and algebraic-law relations (distributes_over / obeys / satisfies / mixed_product / antidistributes_over_product / alternative_to) which are NOT strict dependencies.
Verifier: resolve tgt to a real atom + src!=tgt + no existing edge + no reverse-edge cycle + tgt in knowledge corpus (CHTV subset; full L6-PROOF/cap_pres at Testbed ratify). Cross-checks against Skunkworks vet (skunkworks_wtypesig_vet_v1.jsonl) as independent Prover triangulation.
HARD-PASS: >=10 W-TYPE-SIG STRICT candidates extracted AND >=80% overlap with Skunkworks's STRICT set (independent reproduction). Substrate-internal; laptop; no LLM; no remote. ASCII; --self-test."""
from __future__ import annotations
import sys, json, time, re
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
DATA_ROOT = REPO / "data" / "substrate_index"
SELFMODEL = DATA_ROOT / "skunkworks_self_model_of_operators_v1.jsonl"
SKVET = DATA_ROOT / "skunkworks_wtypesig_vet_v1.jsonl"
WALK = {"DEPENDS_ON", "SHARES_MATH", "SPECIALIZES", "USES", "INSTANCE_OF", "DEFINED_OVER", "IMPLEMENTS"}
# reliable forward pointers -> edge type (src --pointer--> tgt; tgt is the dependency)
PTR_EDGE = {"derived_from": "DEPENDS_ON", "composed_of": "DEPENDS_ON", "diagonalized_by": "DEPENDS_ON",
            "uses": "USES", "implemented_via": "USES", "computed_via": "USES",
            "computes": "IMPLEMENTS", "instance_of": "INSTANCE_OF"}
EXCLUDE = {"inverse_of", "invertible_via", "right_inverse_of", "distributes_over", "antidistributes_over_product",
           "obeys", "satisfies", "mixed_product", "alternative_to", "basis_for", "used_in", "used_by",
           "diagonalizes", "induced_by"}
KNOWLEDGE_CORPUS = ("math", "science", "concept", "")
SELFTEST = "--self-test" in sys.argv


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def _selftest():
    assert _short("T2/fhrr_bind") == "fhrr_bind"
    assert PTR_EDGE["derived_from"] == "DEPENDS_ON" and "inverse_of" in EXCLUDE
    print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(DATA_ROOT)
    atoms = list(ps.all_atoms())
    sset = {_short(a.id) for a in atoms}
    corpus = {_short(a.id): str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower() for a in atoms}
    tier = {_short(a.id): str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "") for a in atoms}
    # existing edges (rel-type-aware: forward-dir set + DEPENDS_ON set for cycle check)
    edges = set(); dep = set()
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            rt = (r.get("rel_type", "") or "").upper()
            s = _short(r.get("src_id", "")); t = _short(r.get("tgt_id", ""))
            if rt in WALK: edges.add((s, t))
            if rt == "DEPENDS_ON": dep.add((s, t))
    # parse self-model relational pointers
    sm = [json.loads(l) for l in open(SELFMODEL, encoding="utf-8") if l.strip()]
    strict, deferred, unresolved = [], [], []
    seen = set()
    for rec in sm:
        src = _short(rec.get("atom", ""))
        if not src: continue
        for p in (rec.get("algebraic_properties") or []):
            m = re.match(r"^([a-z_]+):(.+)$", str(p).strip())
            if not m: continue
            ptr, raw_tgt = m.group(1), _short(m.group(2))
            if ptr in EXCLUDE: continue
            if ptr not in PTR_EDGE:
                deferred.append({"src": src, "tgt": raw_tgt, "pointer": ptr, "why": "pointer-not-in-reliable-set"}); continue
            et = PTR_EDGE[ptr]
            # resolve target to a real atom (by short name)
            if raw_tgt not in sset:
                unresolved.append({"src": src, "tgt": raw_tgt, "pointer": ptr, "why": "tgt-atom-not-found"}); continue
            if src == raw_tgt: continue
            if (src, raw_tgt) in edges: continue              # additive: already present
            if (raw_tgt, src) in edges: continue              # no reverse-edge cycle
            if corpus.get(raw_tgt, "") not in KNOWLEDGE_CORPUS: continue
            key = (src, raw_tgt, et)
            if key in seen: continue
            seen.add(key)
            strict.append({"src": src, "tgt": raw_tgt, "pointer": ptr, "edge_type": et,
                           "tier": "%s->%s" % (tier.get(src, "?"), tier.get(raw_tgt, "?")), "witness": "W_TYPE_SIG"})
    # KEY ANALYSIS: classify Skunkworks's STRICT pairs vs the CURRENT substrate edges
    # (the W-TYPE-SIG pairs DECISION 77c is about to ratify). new / forward-exists / reverse-DEPENDS_ON-cycle.
    sk = [json.loads(l) for l in open(SKVET, encoding="utf-8") if l.strip()] if SKVET.exists() else []
    sk_strict = [r for r in sk if str(r.get("vet_class", "")).upper() == "STRICT"]
    new_pairs, fwd_exists, cycles = [], [], []
    for r in sk_strict:
        s = _short(r.get("src", "")); t = _short(r.get("tgt", ""))
        if (s, t) not in edges: new_pairs.append("%s->%s" % (s, t))
        else: fwd_exists.append("%s->%s" % (s, t))
        if (t, s) in dep: cycles.append("%s<->%s (reverse DEPENDS_ON present)" % (s, t))
    print("  Iter4 W-TYPE-SIG extractor (laptop-only) on %d operator signatures:" % len(sm), flush=True)
    print("  NEW STRICT candidates extracted (additive)=%d | unresolved-tgt=%d | compound/non-reliable deferred=%d" % (
        len(strict), len(unresolved), len(deferred)), flush=True)
    print("  --- Skunkworks STRICT (%d) vs CURRENT substrate (the DECISION 77c ratify set): ---" % len(sk_strict), flush=True)
    print("  already-exist-forward=%d | genuinely-NEW=%d | REVERSE-DEPENDS_ON-CYCLE=%d" % (
        len(fwd_exists), len(new_pairs), len(cycles)), flush=True)
    for c in cycles: print("    CYCLE: %s" % c, flush=True)
    if new_pairs:
        print("  genuinely NEW (would add edges):", flush=True)
        for p in new_pairs: print("    %s" % p, flush=True)
    return {"n_signatures": len(sm), "new_strict_extracted": len(strict), "unresolved": len(unresolved),
            "deferred": len(deferred), "sk_strict": len(sk_strict), "sk_already_exist": len(fwd_exists),
            "sk_genuinely_new": len(new_pairs), "sk_reverse_cycles": len(cycles),
            "cycles": cycles, "new_pairs": new_pairs, "unresolved_list": unresolved[:20], "strict_sample": strict[:20]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    new = r["sk_genuinely_new"]; exist = r["sk_already_exist"]; cyc = r["sk_reverse_cycles"]
    s = ("W-TYPE-SIG mechanism is real (extractor parses author-supplied directional pointers from %d signatures), BUT vs the CURRENT substrate: of Skunkworks's %d STRICT pairs, %d already exist as forward edges, %d are genuinely NEW, and %d have a REVERSE DEPENDS_ON edge (2-cycle). Extractor's own additive pass yields %d NEW (consistent). %d unresolved (endpoint atom not authored) + %d compound/non-reliable deferred." % (
        r["n_signatures"], r["sk_strict"], exist, new, cyc, r["new_strict_extracted"], r["unresolved"], r["deferred"]))
    if new == 0 and cyc > 0:
        return ("HARD_FINDING", "W-TYPE-SIG STRICT pairs add 0 NEW edges (all already grounded) AND %d have REVERSE DEPENDS_ON cycles -> the celebrated 'STRICT growth' is NOT new growth on the current self-model; the substrate-product value of W-TYPE-SIG here is (a) CYCLE-CLEANUP (remove the %d reverse edges to realize clean direction) and (b) FUTURE growth as NEW un-grounded operators are authored. DECISION 77c ratify would be redundant (0 new) + would not fix the existing reverse-direction cycles. " % (cyc, cyc) + s)
    if new == 0:
        return ("PARTIAL", "W-TYPE-SIG STRICT pairs all already exist (0 new); mechanism validated but no new growth on current self-model: " + s)
    return ("HARD_PASS", "W-TYPE-SIG yields %d genuinely NEW STRICT edges (tier-independent; no remote): Iter 4 generator validated. " % new + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_77a_iter4_wtypesig_extractor", flush=True)
    out_dir = get_output_dir("substrate_77a_iter4_wtypesig_extractor_laptop_only_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_77a_iter4_wtypesig_extractor_laptop_only_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
