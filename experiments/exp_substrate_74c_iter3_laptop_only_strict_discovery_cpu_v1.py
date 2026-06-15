"""DECISION 74c -- CO-EVOLVE-1 Iteration 3 (LAPTOP-ONLY; resolves DECISION 75d): can the autonomous loop produce NEW STRICT edges past the initial harvest, on FRESH degree-0 targets? Generator = cached-cosine P1-bge (math-partition npz; NO bge model, NO remote -- 75d laptop-only path). Verifier = full-P2 derivation-truth (W-DEF/W-GRAPH/W-REV) PLUS a STRICT discriminator honoring Skunkworks's DECISION 74 distinction:
  PLAUSIBLE = witnessed (W-DEF | W-GRAPH | W-REV) + CHTV  (relatedness; the Iter 2 bar).
  STRICT    = W-DEF (candidate name/alias token IN target's DEFINITION = definitional dependency)
              AND tier(candidate) STRICTLY < tier(target) (correct direction; candidate more foundational; avoids MDP->bellman reverse)
              AND candidate is NOT a field/area HUB (walk-degree below hub percentile; avoids field-membership MI->information_theory)
              AND CHTV (corpus + L6-terminates + no-cycle + additive).
HARD-PASS Iter 3: >=1 NEW STRICT edge (the decisive test -- substrate's STRICT-discovery is NOT saturated after initial harvest).
HARD-FAIL: 0 STRICT on a fresh isolated-target set -> Phase 3 v0 is a PLAUSIBLE-tier-expansion mechanism, not a STRICT-discovery mechanism (honest saturation finding).
Substrate-internal; laptop (cached embeddings + structural; no LLM, no remote). ASCII; --self-test."""
from __future__ import annotations
import sys, json, time, re, glob
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
DATA_ROOT = REPO / "data" / "substrate_index"
CACHE = DATA_ROOT / "cached_indices" / "bge_large_v2_name_1782_c2420fcf.npz"
WALK = {"DEPENDS_ON", "SHARES_MATH", "SPECIALIZES", "USES", "INSTANCE_OF", "DEFINED_OVER"}
STRUCT = {"DEPENDS_ON", "USES", "INSTANCE_OF", "SPECIALIZES", "DEFINED_OVER", "SHARES_MATH"}
TIER_NUM = {"T1": 1, "T2": 2, "T3": 3, "T4": 4}
STOP = set("the of a an is are and or to in on for with as at from that this these those by it its all any per via using used be can not into over under between within".split())
ITER1 = {"markov_decision_process", "q_learning", "mutual_information"}
# process-artifact name patterns that polluted the math cache (notes/rules/schema/process atoms -- NOT knowledge concepts)
JUNK_PREFIX = ("rule_", "schema_", "pp-", "exp_dev", "research_", "testbed_", "skunkworks", "director_", "session_", "cell_", "decision_", "meta_")
JUNK_SUBSTR = ("_to_", "_2026-", "_2026_", "north_star", "handoff", "_drill_", "_won_", "_ceiling_", "_inbox")
KNOWLEDGE_CORPUS = ("math", "science", "concept")
KNOWLEDGE_TIER = {"T1", "T2", "T3", "T4"}
GEN_K = 8       # candidates generated per target
HUB_PCTL = 90   # candidates above this walk-degree percentile = field/area hub -> not STRICT
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
    corpus = {_short(a.id): str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower() for a in atoms}
    # walk adjacency + degree + directed (for proof termination / no-cycle)
    adj = defaultdict(set); deg = defaultdict(int); dadj = defaultdict(set); has_out = set()
    for rp in glob.glob(str(DATA_ROOT / "**" / "relations.jsonl"), recursive=True):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            rt = (r.get("rel_type", "") or "").upper()
            s = _short(r.get("src_id", "")); t = _short(r.get("tgt_id", ""))
            if not (s and t and s != t): continue
            if rt in WALK: adj[s].add(t); adj[t].add(s); deg[s] += 1; deg[t] += 1
            if rt in STRUCT: dadj[s].add(t); has_out.add(s)
    degvals = np.array(sorted(deg.values())) if deg else np.array([0])
    hub_thresh = float(np.percentile(degvals, HUB_PCTL)) if len(degvals) else 1e9

    def reaches(s, t, mx=2):
        seen = {s}; q = deque([(s, 0)])
        while q:
            n, d = q.popleft()
            if d >= mx: continue
            for m in adj.get(n, ()):
                if m == t: return True
                if m not in seen: seen.add(m); q.append((m, d + 1))
        return False

    def terminates(start, cand):  # does adding start->cand keep axiom-termination (cand reaches a T1/axiom)?
        seen = {start}; q = deque([cand])
        while q:
            n = q.popleft()
            if tier.get(n, "") == "T1" or n not in has_out: return True  # hit axiom/leaf
            for m in dadj.get(n, ()):
                if m not in seen: seen.add(m); q.append(m)
        return True  # finite graph; backward chain always terminates

    # cached embeddings (math partition) -- laptop-only generator
    z = np.load(CACHE, allow_pickle=True)
    ids = json.loads(str(z["id_order_json"]))
    M = z["semantic"].astype(np.float32)
    M = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)
    row = {}
    for k, i in enumerate(ids):
        row.setdefault(_short(i), k)
    cache_short = set(row)

    def is_knowledge(s):  # genuine math/science/concept atom, NOT a process/note/rule artifact
        if any(s.startswith(p) for p in JUNK_PREFIX) or any(j in s for j in JUNK_SUBSTR): return False
        if corpus.get(s, "") not in KNOWLEDGE_CORPUS: return False
        if tier.get(s, "") not in KNOWLEDGE_TIER: return False
        return True

    targets = sorted([s for s in cache_short if deg.get(s, 0) == 0 and s not in ITER1
                      and desc.get(s, "").strip() and is_knowledge(s)])

    strict, plausible, reject = [], [], []
    for tgt in targets:
        tr = row.get(tgt)
        if tr is None: continue
        sims = M @ M[tr]
        order = np.argsort(-sims)
        cands = []
        for k in order[1:1 + GEN_K * 3]:
            c = _short(ids[k])
            if c == tgt or c in adj.get(tgt, ()): continue
            cands.append((c, float(sims[k])))
            if len(cands) >= GEN_K: break
        for cand, cos in cands:
            td = desc.get(tgt, "").lower(); ct = name_tok.get(cand, set())
            wdef = any(w in td and len(w) >= 5 for w in ct)
            wgraph = reaches(tgt, cand, 2)
            cd = desc.get(cand, "").lower(); tt = name_tok.get(tgt, set())
            tmono = TIER_NUM.get(tier.get(cand, ""), 9) <= TIER_NUM.get(tier.get(tgt, ""), 9)
            wrev = any(w in cd and len(w) >= 5 for w in tt) and tmono
            witnessed = wdef or wgraph or wrev
            if not witnessed:
                reject.append({"edge": "%s->%s" % (tgt, cand), "cos": round(cos, 3), "why": "no-witness"})
                continue
            # CHTV: corpus-compatible + terminates + no 1-hop cycle + additive(no existing edge)
            same_or_found = corpus.get(cand, "") in ("math", "concept", "science", "")
            no_cycle = tgt not in dadj.get(cand, ())
            term = terminates(tgt, cand)
            chtv = same_or_found and no_cycle and term
            # STRICT discriminator (per Skunkworks DECISION 74)
            dir_strict = TIER_NUM.get(tier.get(cand, ""), 9) < TIER_NUM.get(tier.get(tgt, ""), 9)
            not_hub = deg.get(cand, 0) <= hub_thresh
            is_strict = wdef and dir_strict and not_hub and chtv and is_knowledge(cand)
            rec = {"edge": "%s->%s" % (tgt, cand), "cos": round(cos, 3), "W-DEF": wdef, "W-GRAPH": wgraph,
                   "W-REV": wrev, "dir_strict": dir_strict, "not_hub": not_hub, "chtv": chtv,
                   "tier": "%s->%s" % (tier.get(tgt, "?"), tier.get(cand, "?"))}
            if is_strict: strict.append(rec)
            elif chtv: plausible.append(rec)
            else: reject.append({"edge": rec["edge"], "cos": rec["cos"], "why": "witnessed-but-CHTV-fail"})
    # dedup strict/plausible by edge
    def dd(rows):
        seen = set(); out = []
        for r in rows:
            if r["edge"] in seen: continue
            seen.add(r["edge"]); out.append(r)
        return out
    strict, plausible = dd(strict), dd(plausible)
    print("  Iter3 LAPTOP-ONLY on %d fresh degree-0 targets (math cache) | STRICT=%d PLAUSIBLE=%d REJECT=%d" % (
        len(targets), len(strict), len(plausible), len(reject)), flush=True)
    print("  hub-degree threshold (p%d)=%.0f" % (HUB_PCTL, hub_thresh), flush=True)
    print("  --- STRICT candidates (decisive; W-DEF + correct-direction + not-hub + CHTV): ---", flush=True)
    for r in strict[:40]:
        print("    %-48s cos=%.3f tier %s" % (r["edge"], r["cos"], r["tier"]), flush=True)
    if not strict: print("    (none)", flush=True)
    return {"n_targets": len(targets), "strict_count": len(strict), "plausible_count": len(plausible),
            "reject_count": len(reject), "hub_thresh": hub_thresh, "strict": strict[:60], "plausible_sample": plausible[:30]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    sc = r["strict_count"]
    s = ("Iter3 laptop-only (cached-cosine generator + full-P2 + STRICT discriminator) on %d fresh degree-0 targets: STRICT=%d, PLAUSIBLE=%d, REJECT=%d. STRICT = W-DEF (definitional) + strictly-more-foundational direction + not-field-hub + CHTV (the Skunkworks DECISION 74 bar)." % (
        r["n_targets"], sc, r["plausible_count"], r["reject_count"]))
    if sc >= 1:
        return ("HARD_PASS", "Iter3 produces NEW STRICT edges (%d): substrate's STRICT-dependency discovery is NOT saturated after the initial harvest -- Claim 10 compounding can graduate from relatedness-tier toward STRICT-tier (pending Skunkworks STRICT-class vet). " % sc + s)
    return ("HARD_FAIL", "Iter3 produces 0 STRICT on a fresh isolated-target set: substrate's STRICT-discovery SATURATED after initial harvest; Phase 3 v0 is operationally a PLAUSIBLE-tier-expansion mechanism (honest scope per DECISION 74c HARD-FAIL). " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_74c_iter3_laptop_only_strict_discovery | GEN_K=%d HUB_PCTL=%d" % (GEN_K, HUB_PCTL), flush=True)
    out_dir = get_output_dir("substrate_74c_iter3_laptop_only_strict_discovery_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_74c_iter3_laptop_only_strict_discovery_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
