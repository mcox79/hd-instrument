"""DECISION 144b -- INSTANCE_OF forward-walk coverage-impact measurement (Exp-Dev's assigned part: verify cap_pres=1.0 invariant under BOTH FORWARD sets + give the Director coverage data). Measures the substrate-wide effect of adding INSTANCE_OF to the axiom-termination FORWARD set. NON-MUTATING (measurement only; substrate state untouched). Substrate-internal; NO LLM. CPU. ASCII; --self-test.

QUESTION (Skunkworks deviation-4 surfaced; Director measure-first-then-call): should FORWARD = {DEPENDS_ON, SPECIALIZES} become {DEPENDS_ON, SPECIALIZES, INSTANCE_OF}? "X INSTANCE_OF Y" semantically grounds X via Y (is-a), parallel to SPECIALIZES.
METHOD: re-score axiom-termination (reaches a T1 atom via forward-walk) under both FORWARD sets; count newly-grounded / newly-stranded / unchanged; verify cap_pres invariant.
KEY INVARIANT CLAIM (to verify, not assume): adding edges to FORWARD is MONOTONE -> can only ADD reach, never remove it -> newly_stranded MUST be 0 -> cap_pres=1.0 preserved (no served capability lost). If newly_stranded>0 the claim is false (would be a real finding).
HARD-PASS: newly_stranded=0 (monotone confirmed; cap_pres=1.0 invariant under both sets) AND coverage delta (newly_grounded count) reported for the Director's call. HARD-FAIL: newly_stranded>0 (non-monotone -- impossible by construction, would indicate a bug/data anomaly worth surfacing)."""
from __future__ import annotations
import sys, json, time
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
DATA_ROOT = REPO / "data" / "substrate_index"
BASE_FWD = {"DEPENDS_ON", "SPECIALIZES"}
CAND_FWD = {"DEPENDS_ON", "SPECIALIZES", "INSTANCE_OF"}
SELFTEST = "--self-test" in sys.argv


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def _reaches_t1(start, adj, is_t1, max_depth=20):
    if is_t1(start): return True
    seen = {start}; q = deque([(start, 0)])
    while q:
        n, d = q.popleft()
        if d >= max_depth: continue
        for m in adj.get(n, ()):
            if is_t1(m): return True
            if m not in seen: seen.add(m); q.append((m, d + 1))
    return False


def _selftest():
    assert "INSTANCE_OF" in CAND_FWD and "INSTANCE_OF" not in BASE_FWD; print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(DATA_ROOT)
    tier = {_short(a.id): str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "") for a in ps.all_atoms()}
    universe = set(tier)
    base_adj = defaultdict(list); cand_adj = defaultdict(list); inst_edges = 0
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            rt = (r.get("rel_type", "") or "").upper(); s = _short(r.get("src_id", "")); t = _short(r.get("tgt_id", ""))
            if not (s and t and s != t): continue
            if rt in BASE_FWD: base_adj[s].append(t); cand_adj[s].append(t)
            elif rt == "INSTANCE_OF": cand_adj[s].append(t); inst_edges += 1
    is_t1 = lambda n: tier.get(n, "") == "T1"
    base_grounded = {n for n in universe if _reaches_t1(n, base_adj, is_t1)}
    cand_grounded = {n for n in universe if _reaches_t1(n, cand_adj, is_t1)}
    newly_grounded = sorted(cand_grounded - base_grounded)
    newly_stranded = sorted(base_grounded - cand_grounded)   # MUST be empty (monotone)
    n = len(universe)
    cap_pres_invariant = len(newly_stranded) == 0
    print("  CELL-144b INSTANCE_OF forward-walk coverage-impact (NON-MUTATING measurement):", flush=True)
    print("  atoms=%d | INSTANCE_OF edges=%d" % (n, inst_edges), flush=True)
    print("  axiom-grounded under BASE   {DEPENDS_ON,SPECIALIZES}            = %d (%.1f%%)" % (len(base_grounded), 100.0 * len(base_grounded) / n), flush=True)
    print("  axiom-grounded under CAND   {DEPENDS_ON,SPECIALIZES,INSTANCE_OF}= %d (%.1f%%)" % (len(cand_grounded), 100.0 * len(cand_grounded) / n), flush=True)
    print("  NEWLY-GROUNDED by INSTANCE_OF = %d | NEWLY-STRANDED = %d (must be 0) | unchanged = %d" % (
        len(newly_grounded), len(newly_stranded), n - len(newly_grounded) - len(newly_stranded)), flush=True)
    print("  cap_pres=1.0 invariant under BOTH FORWARD sets (newly_stranded==0): %s" % cap_pres_invariant, flush=True)
    if newly_grounded:
        print("  sample newly-grounded atoms (gain axiom-reach via INSTANCE_OF):", flush=True)
        for a in newly_grounded[:15]: print("    %-30s (tier=%s)" % (a, tier.get(a, "?")), flush=True)
    if newly_stranded:
        print("  !! NEWLY-STRANDED (non-monotone anomaly):", newly_stranded[:15], flush=True)
    return {"n_atoms": n, "instance_of_edges": inst_edges, "base_grounded": len(base_grounded),
            "cand_grounded": len(cand_grounded), "newly_grounded": len(newly_grounded),
            "newly_stranded": len(newly_stranded), "cap_pres_invariant": cap_pres_invariant,
            "newly_grounded_sample": newly_grounded[:40], "newly_stranded_list": newly_stranded[:40]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = ("INSTANCE_OF coverage-impact: base-grounded=%d -> cand-grounded=%d (+%d newly-grounded via INSTANCE_OF, %d newly-stranded); INSTANCE_OF edges=%d; cap_pres-invariant=%s." % (
        r["base_grounded"], r["cand_grounded"], r["newly_grounded"], r["newly_stranded"], r["instance_of_edges"], r["cap_pres_invariant"]))
    if not r["cap_pres_invariant"]:
        return ("HARD_FAIL", "NON-MONOTONE anomaly: adding INSTANCE_OF to FORWARD STRANDED %d atoms (impossible by construction unless a data/keying anomaly) -- surface before any methodology call. " % r["newly_stranded"] + s)
    if r["newly_grounded"] > 0:
        return ("HARD_PASS", "cap_pres=1.0 INVARIANT under both FORWARD sets (0 newly-stranded; adding INSTANCE_OF is monotone -> cannot lose served capability). COVERAGE DATA for Director's call: adding INSTANCE_OF newly-grounds %d atoms (e.g. INSTANCE_OF-only atoms like the pre-rescue wright_fisher_process class) that the current FORWARD set leaves stranded. Director call YES (adopt; methodology-rule-25 candidate) raises axiom-term coverage by %d atoms with 0 cap_pres risk; NO keeps stack frozen at 24. Either way safe; this is the substrate-wide measurement DECISION 144b asked for. (Exp-Dev's assigned part: cap_pres-invariant VERIFIED under both sets.) " % (r["newly_grounded"], r["newly_grounded"]) + s)
    return ("HARD_PASS", "cap_pres=1.0 invariant; INSTANCE_OF newly-grounds 0 atoms -> adopting it would change NOTHING (no atom is INSTANCE_OF-only-grounded) -> Director call is a no-op either way; recommend keep stack frozen at 24 (no coverage benefit). " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_144b_instance_of_forward_coverage_impact", flush=True)
    out_dir = get_output_dir("substrate_144b_instance_of_forward_coverage_impact_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_144b_instance_of_forward_coverage_impact_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
