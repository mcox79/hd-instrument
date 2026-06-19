"""DECISION 100a -- CO-EVOLVE Iteration 4: can W-TYPE-SIG produce NEW STRICT edges on the 9 freshly-enabled source atoms (4 tier-corrected per 84a RETRY + 5 Phase 4e substrate-selected)? Resolves Claim 5 (autonomous generalization), the last OPEN claim.
For each source atom's self-model relational pointers (source --pointer--> target):
  EXISTENCE-CHECK (DECISION 78 lesson): skip edges already in substrate.
  TIER-GRADIENT (DECISION 96): TIER_NUM(source) > TIER_NUM(target) => correct foundational direction => STRICT-eligible; else PLAUSIBLE.
  RESOLVE target to an existing atom (no dangling).
Emit NEW-STRICT candidates for Skunkworks adversarial vet. Substrate-internal; laptop; structural (no bge); no LLM. ASCII; --self-test.
HARD-PASS: >=1 genuinely-NEW STRICT edge (post existence-check + tier-gradient). HARD-FAIL: 0 new STRICT (saturation persists)."""
from __future__ import annotations
import sys, json, time, re
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
DATA_ROOT = REPO / "data" / "substrate_index"
SELFMODELS = [DATA_ROOT / "skunkworks_self_model_of_operators_v1.jsonl",
              DATA_ROOT / "skunkworks_self_model_phase_4e_substrate_selected_batch_1.jsonl"]
WALK = {"DEPENDS_ON", "SHARES_MATH", "SPECIALIZES", "USES", "INSTANCE_OF", "DEFINED_OVER", "IMPLEMENTS"}
# reliable forward pointers -> edge type (source --ptr--> target; target is the dependency)
PTR_EDGE = {"derived_from": "DEPENDS_ON", "composed_of": "DEPENDS_ON", "diagonalized_by": "DEPENDS_ON",
            "uses": "USES", "implemented_via": "USES", "computed_via": "USES",
            "computes": "IMPLEMENTS", "instance_of": "INSTANCE_OF", "specializes": "SPECIALIZES"}
EXCLUDE = {"inverse_of", "invertible_via", "right_inverse_of", "distributes_over", "antidistributes_over_product",
           "obeys", "satisfies", "mixed_product", "alternative_to", "basis_for", "used_in", "used_by",
           "diagonalizes", "induced_by"}
TIER_NUM = {"T1": 1, "T2": 2, "T3": 3, "T4": 4}
TARGETS = ["gradient_descent", "newton_method", "hessian", "bayes_rule",
           "expectation_variance", "measure_space", "banach_space", "random_variable", "eisner_parsing"]
SELFTEST = "--self-test" in sys.argv


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def _selftest():
    assert _short("T2/hessian") == "hessian" and PTR_EDGE["derived_from"] == "DEPENDS_ON"
    print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def extract_pointers(rec):
    """Yield (source_short, ptr, target_short) for reliable pointers in a self-model record (handles algebraic_properties
    'ptr:target' strings AND explicit list/field forms)."""
    src = _short(rec.get("atom", "") or rec.get("name", ""))
    if not src: return
    for p in (rec.get("algebraic_properties") or []):
        m = re.match(r"^([a-z_]+):(.+)$", str(p).strip())
        if m: yield src, m.group(1), _short(m.group(2))
    for key in ("derived_from", "uses", "computes", "implemented_via", "composed_of", "computed_via",
                "instance_of", "specializes", "depends_on", "relational_pointers"):
        v = rec.get(key)
        if not v: continue
        if isinstance(v, str): yield src, key, _short(v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, str):
                    m = re.match(r"^([a-z_]+):(.+)$", item.strip())
                    if m: yield src, m.group(1), _short(m.group(2))
                    else: yield src, key, _short(item)
                elif isinstance(item, dict):
                    t = item.get("target") or item.get("tgt") or item.get("atom")
                    pt = item.get("pointer") or item.get("rel") or key
                    if t: yield src, str(pt), _short(t)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(DATA_ROOT)
    atoms = list(ps.all_atoms())
    sset = {_short(a.id) for a in atoms}
    tier = {_short(a.id): str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "") for a in atoms}
    edges = set()
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            if (r.get("rel_type", "") or "").upper() in WALK:
                edges.add((_short(r.get("src_id", "")), _short(r.get("tgt_id", ""))))
    # load all self-model records, index pointers by source
    recs = []
    for f in SELFMODELS:
        if not f.exists(): continue
        for ln in open(f, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try:
                obj = json.loads(ln)
                if isinstance(obj, dict): recs.append(obj)
                elif isinstance(obj, list): recs.extend(x for x in obj if isinstance(x, dict))
            except Exception: continue
    tset = set(TARGETS)
    new_strict, new_plausible, already, unresolved = [], [], [], []
    seen = set()
    for rec in recs:
        for src, ptr, tgt in extract_pointers(rec):
            if src not in tset: continue
            if ptr in EXCLUDE or ptr not in PTR_EDGE: continue
            et = PTR_EDGE[ptr]
            key = (src, tgt, et)
            if key in seen: continue
            seen.add(key)
            if tgt not in sset: unresolved.append({"edge": "%s--%s-->%s" % (src, ptr, tgt), "why": "target-not-found"}); continue
            if src == tgt: continue
            if (src, tgt) in edges: already.append("%s--%s-->%s" % (src, ptr, tgt)); continue
            ts, tt = TIER_NUM.get(tier.get(src, ""), 9), TIER_NUM.get(tier.get(tgt, ""), 9)
            rec_out = {"src": src, "tgt": tgt, "pointer": ptr, "edge_type": et,
                       "tier": "%s->%s" % (tier.get(src, "?"), tier.get(tgt, "?")), "witness": "W_TYPE_SIG"}
            if ts > tt:  # source more-derived than target (foundational direction) -> tier-gradient holds -> STRICT-eligible
                new_strict.append(rec_out)
            else:
                new_plausible.append(rec_out)
    print("  Iter 4 W-TYPE-SIG STRICT-discovery on %d source atoms (4 tier-corrected + 5 Phase 4e):" % len(TARGETS), flush=True)
    print("  NEW-STRICT(tier-gradient holds)=%d | NEW-PLAUSIBLE(no gradient)=%d | already-exist=%d | unresolved=%d" % (
        len(new_strict), len(new_plausible), len(already), len(unresolved)), flush=True)
    print("  --- NEW STRICT candidates (post existence-check + tier-gradient; for Skunkworks vet): ---", flush=True)
    for r in new_strict:
        print("    %-26s --%-14s--> %-26s [%s] %s" % (r["src"], r["pointer"], r["tgt"], r["edge_type"], r["tier"]), flush=True)
    if not new_strict: print("    (none)", flush=True)
    if new_plausible:
        print("  --- NEW PLAUSIBLE (no tier-gradient; not STRICT): ---", flush=True)
        for r in new_plausible[:15]:
            print("    %-26s --%-14s--> %-26s [%s] %s" % (r["src"], r["pointer"], r["tgt"], r["edge_type"], r["tier"]), flush=True)
    return {"n_targets": len(TARGETS), "new_strict": new_strict, "new_plausible": new_plausible,
            "n_new_strict": len(new_strict), "n_new_plausible": len(new_plausible),
            "n_already": len(already), "n_unresolved": len(unresolved), "unresolved": unresolved[:20]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    ns = r["n_new_strict"]
    s = ("Iter 4 on %d source atoms: %d NEW-STRICT (tier-gradient holds; post existence-check), %d NEW-PLAUSIBLE (no gradient), %d already-exist, %d unresolved." % (
        r["n_targets"], ns, r["n_new_plausible"], r["n_already"], r["n_unresolved"]))
    if ns >= 1:
        return ("HARD_PASS", "Iter 4 produces %d GENUINELY NEW STRICT edges via W-TYPE-SIG on tier-corrected/Phase-4e atoms -> substrate's STRICT-discovery GENERALIZES past initial harvest (pending Skunkworks vet). Claim 5 (autonomous generalization) candidate to graduate OPEN->MEASURED. " % ns + s)
    return ("HARD_FAIL", "Iter 4 produces 0 new STRICT edges -> substrate's autonomous STRICT-discovery has a boundary beyond tier-flatness (the tier-corrected atoms' dependencies were already grounded, OR their pointers don't yield new tier-gradient edges). Honest scope: Claim 5 stays OPEN; surface the new boundary. " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_100a_iter4_strict_discovery_tier_corrected", flush=True)
    out_dir = get_output_dir("substrate_100a_iter4_strict_discovery_tier_corrected_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_100a_iter4_strict_discovery_tier_corrected_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
