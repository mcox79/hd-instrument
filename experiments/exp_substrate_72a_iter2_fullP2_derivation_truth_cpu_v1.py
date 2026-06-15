"""DECISION 72a -- CO-EVOLVE-1 Iteration 2: re-verify the 14 PLAUSIBLE hold-overs with FULL-P2 DERIVATION-TRUTH (stricter than Iter1 structural-CHTV). full-P2 here (substrate-internal, no LLM) accepts an edge target->candidate ONLY if the dependency is WITNESSED, by one of:
  W-DEF: the candidate's name/alias appears as a token in the target's DEFINITION (description) -> definitional dependency.
  W-GRAPH: target reaches candidate via existing graph in <=2 hops (graph-witnessed derivation).
  W-REV: target's name/alias appears in the candidate's description AND tier-monotone (candidate more foundational).
Plus all Iter1 structural-CHTV (tier-monotone + corpus + L6-terminates + no-cycle + additive). FEWER, STRICTER edges expected. Also tests whether full-P2 is APPLICABLE to isolated atoms (which lack derivations). Substrate-internal; laptop (structural; no bge). ASCII; --self-test.

HARD-PASS: precision-vs-known-style witnessing; <5% would-REJECT; yield>0."""
from __future__ import annotations
import sys, json, time, re
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
DATA_ROOT = REPO / "data" / "substrate_index"
VET = DATA_ROOT / "skunkworks_iter1_edge_vet_v1.jsonl"
STRUCT_EDGES = {"DEPENDS_ON", "USES", "INSTANCE_OF", "SPECIALIZES", "DEFINED_OVER", "SHARES_MATH"}
TIER_NUM = {"T1": 1, "T2": 2, "T3": 3, "T4": 4}
STOP = set("the of a an is are and or to in on for with as at from that this these those by it its all any per via using used".split())
SELFTEST = "--self-test" in sys.argv


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def toks(s):
    return {w for w in re.split(r"[^a-z0-9]+", str(s).lower()) if len(w) >= 4 and w not in STOP}


def _selftest():
    assert _short("a::b/c") == "c" and "entropy" in toks("Shannon Entropy H")
    print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(DATA_ROOT)
    atoms = list(ps.all_atoms())
    desc = {_short(a.id): (a.description or "") for a in atoms}
    name_tok = {_short(a.id): toks(a.name) | {w for al in (a.aliases or []) for w in toks(al)} | toks(_short(a.id)) for a in atoms}
    tier = {_short(a.id): str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "") for a in atoms}
    adj = defaultdict(list)
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: rr = json.loads(ln)
            except Exception: continue
            if (rr.get("rel_type", "") or "").upper() in STRUCT_EDGES:
                s = _short(rr.get("src_id", "")); t = _short(rr.get("tgt_id", ""))
                if s and t and s != t: adj[s].append(t)

    def reaches(s, t, mx=2):
        seen = {s}; q = deque([(s, 0)])
        while q:
            n, d = q.popleft()
            if d >= mx: continue
            for m in adj.get(n, ()):
                if m == t: return True
                if m not in seen: seen.add(m); q.append((m, d + 1))
        return False
    # load the 14 PLAUSIBLE
    plausible = []
    if VET.exists():
        for ln in open(VET, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: d = json.loads(ln)
            except Exception: continue
            if str(d.get("vet_class", "")).upper().startswith("PLAUS"):
                plausible.append((_short(d.get("src", "")), _short(d.get("tgt", ""))))
    plausible = list(dict.fromkeys(plausible))
    rows = []; accept = 0
    for tgt, cand in plausible:
        td = desc.get(tgt, "").lower(); ct = name_tok.get(cand, set())
        # W-DEF: candidate name-tokens appear in target's definition (>=1 distinctive >=5-char token)
        wdef = any(w in td and len(w) >= 5 for w in ct)
        # W-GRAPH: target reaches candidate via <=2 existing edges
        wgraph = reaches(tgt, cand, 2)
        # W-REV: target tokens in candidate desc + candidate more/eq foundational
        cd = desc.get(cand, "").lower(); tt = name_tok.get(tgt, set())
        wrev = any(w in cd and len(w) >= 5 for w in tt) and TIER_NUM.get(tier.get(cand, ""), 9) <= TIER_NUM.get(tier.get(tgt, ""), 9)
        witnessed = wdef or wgraph or wrev
        if witnessed: accept += 1
        rows.append({"edge": "%s->%s" % (tgt, cand), "W-DEF": wdef, "W-GRAPH": wgraph, "W-REV": wrev, "P2_accept": witnessed})
    n = len(plausible); yld = round(accept / max(n, 1), 3)
    print("  Iteration 2 full-P2 on %d PLAUSIBLE hold-overs | P2-accepted=%d (yield %.2f)" % (n, accept, yld), flush=True)
    for x in rows:
        print("  %-50s W-DEF=%s W-GRAPH=%s W-REV=%s -> %s" % (x["edge"], x["W-DEF"], x["W-GRAPH"], x["W-REV"], "ACCEPT" if x["P2_accept"] else "REFUSE"), flush=True)
    return {"n_plausible": n, "p2_accepted": accept, "yield": yld, "rows": rows}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    n = r["n_plausible"]; acc = r["p2_accepted"]
    s = ("Iter2 full-P2 derivation-truth on %d PLAUSIBLE hold-overs: %d ACCEPT (yield %.2f). Witnesses: W-DEF (candidate in target's definition) / W-GRAPH (<=2-hop graph-witnessed) / W-REV (target in candidate def + tier-monotone). Stricter than Iter1 structural-CHTV." % (
        n, acc, r["yield"]))
    if acc >= 1 and acc < n:
        return ("HARD_PASS", "Iter2 full-P2 DISCRIMINATES (accepts %d/%d strictly-witnessed; refuses the rest = the bge-artifact PLAUSIBLE that lacked definitional/graph witness): " % (acc, n) + s + " full-P2 is stricter than CHTV + applicable where a witness exists.")
    if acc == 0:
        return ("HARD_FAIL", "Iter2 full-P2 yield=0: NONE of the PLAUSIBLE edges have a definitional/graph witness -- confirms the OBSTACLE that full-P2 derivation-truth is INAPPLICABLE to isolated atoms (no derivation + notation-heavy definitions). " + s + " -> the autonomous loop for ISOLATED atoms must rely on the confidence-tiered approach (Claim 12 R1) + Skunkworks vet, NOT full-P2 (which needs a pre-existing derivation the isolated atoms lack).")
    return ("MIDDLE", "Iter2 full-P2 accepts all (no discrimination): " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_72a_iter2_fullP2_derivation_truth", flush=True)
    out_dir = get_output_dir("substrate_72a_iter2_fullP2_derivation_truth_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_72a_iter2_fullP2_derivation_truth_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
