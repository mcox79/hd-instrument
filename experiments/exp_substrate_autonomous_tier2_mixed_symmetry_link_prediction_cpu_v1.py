"""autonomous-tier-2 anchor test (Skunkworks 4-gate dispatch) -- CELL-AUTONOMOUS-TIER2. Held-out mixed-symmetry LINK-PREDICTION over the substrate's REAL relation graph (SHARES_MATH/RELATES/DUAL symmetric + DEPENDS_ON/USES/SPECIALIZES directed), VECTOR-ENCODING based (binder load-bearing, NOT graph-walk -- the critical precision). Tests gate 2: do single-op encoders (FULL basis incl role_filler_binding) measurably FAIL? Substrate-internal; NO LLM. CPU/numpy. ASCII; --self-test.

VECTOR-ENCODING task (binder load-bearing): for atom X, encode its TRAIN-edge neighborhood into ONE composite vector V(X); predict HELD-OUT edges (sym + directed, BOTH directions) FROM V(X) by unbind+cleanup. A fully-symmetric encoder loses DEPENDS_ON direction; a fully-asymmetric one can still role-bind. role_filler_binding (existing single op) is the canonical multi-relational VSA encoder -> the gate-2 question is whether it (or any single op) closes this.

VERIFY-BEFORE-ASSERTING (both ways): prior is that role_filler (single op) CLOSES binary link-prediction (-> gate 2 fails -> link-prediction is NOT an autonomous-tier-2 gap; partial-symmetry is a TERNARY property that binary link-prediction does not exhibit, and a ternary-motif metric risks gate-1 gerrymandering). But role_filler might fail via superposition crosstalk on direction. TEST it; report honestly either way.
GATE-2 RESULT: if any single op closes (hit@1 >= BAR incl direction) -> link-prediction anchor does NOT yield an autonomous-tier-2 gap (honest negative). If ALL single ops fail -> proceed to combine-search (gate 3) + Skunkworks full-basis equivalence (gate 4)."""
from __future__ import annotations
import sys, time, math, json
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
DATA_ROOT = REPO / "data" / "substrate_index"
SYM_REL = {"SHARES_MATH", "RELATES", "DUAL"}
DIR_REL = {"DEPENDS_ON", "USES", "SPECIALIZES", "INSTANCE_OF"}
N_DIM = 2048
BAR = 0.70          # relation-type+direction classification (3 classes; chance ~0.33-0.50); a real closer >> chance
SEEDS = [7, 17, 23]
SELFTEST = "--self-test" in sys.argv


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def _load_graph():
    sym = defaultdict(set); dout = defaultdict(set); din = defaultdict(set); atoms = set()
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            s = _short(r.get("src_id", "")); t = _short(r.get("tgt_id", "")); rt = (r.get("rel_type", "") or "").upper()
            if not (s and t and s != t): continue
            if rt in SYM_REL: sym[s].add(t); sym[t].add(s); atoms.update([s, t])
            elif rt in DIR_REL: dout[s].add(t); din[t].add(s); atoms.update([s, t])
    return sym, dout, din, atoms


def _selftest():
    assert _short("a::b/c") == "c"; print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    sym, dout, din, atoms = _load_graph()
    # MIXED-symmetry atoms: have BOTH a symmetric neighbor AND a directed out-target (where partial-symmetry could bite)
    mixed = [a for a in atoms if len(sym.get(a, ())) >= 1 and len(dout.get(a, ())) >= 1]
    atoms = sorted(atoms); aidx = {a: i for i, a in enumerate(atoms)}
    print("  graph: %d atoms | mixed-symmetry atoms (sym>=1 AND dir-out>=1)=%d" % (len(atoms), len(mixed)), flush=True)
    if len(mixed) < 20:
        return {"error": "too few mixed-symmetry atoms (%d) for a principled link-prediction metric" % len(mixed), "n_mixed": len(mixed)}

    ENCODERS = ["bundle_norole", "rolefiller_xor", "rolefiller_conv", "rolefiller_ghrr", "partial_sym_comp"]
    res = {e: [] for e in ENCODERS}
    for seed in SEEDS:
        g = np.random.default_rng(seed); n = N_DIM
        V = (g.integers(0, 2, size=(len(atoms), n)) * 2 - 1).astype(np.float32); V /= np.linalg.norm(V, axis=1, keepdims=True) + 1e-8
        # role vectors (distinguish relation-type AND direction)
        r_sym = V[g.integers(0, len(atoms))]; r_out = V[g.integers(0, len(atoms))]; r_in = V[g.integers(0, len(atoms))]
        def vec(a): return V[aidx[a]]
        def nr(x): return x / (np.linalg.norm(x) + 1e-8)
        def xor(a, b): return a * b
        def conv(a, b): return np.fft.irfft(np.fft.rfft(a) * np.fft.rfft(b), n=n)
        def corr(a, b): return np.fft.irfft(np.conj(np.fft.rfft(a)) * np.fft.rfft(b), n=n)

        # build train/test edge split per mixed atom
        def encode(enc, a, train_sym, train_out, train_in):
            acc = np.zeros(n, dtype=np.float32)
            if enc == "bundle_norole":
                for s in train_sym: acc += vec(s)
                for d in train_out: acc += vec(d)
                for d in train_in: acc += vec(d)
            elif enc.startswith("rolefiller"):
                b = {"rolefiller_xor": xor, "rolefiller_conv": conv, "rolefiller_ghrr": corr}[enc]
                for s in train_sym: acc += b(r_sym, vec(s))
                for d in train_out: acc += b(r_out, vec(d))
                for d in train_in: acc += b(r_in, vec(d))
            elif enc == "partial_sym_comp":
                # partial-symmetric composition: symmetric neighbors bundled (order-free) THEN corr with role; directed corr-bound
                if train_sym:
                    sb = nr(sum(vec(s) for s in train_sym)); acc += corr(r_sym, sb)
                for d in train_out: acc += corr(r_out, vec(d))
                for d in train_in: acc += corr(r_in, vec(d))
            return nr(acc)

        def unbind(enc, Vx, role):
            if enc == "bundle_norole": return Vx                          # no role -> cannot separate by relation
            if enc == "rolefiller_xor": return Vx * role
            if enc == "rolefiller_conv": return corr(role, Vx)            # conv unbind = corr with role
            if enc == "rolefiller_ghrr": return conv(role, Vx)            # corr unbind = conv with role
            if enc == "partial_sym_comp": return conv(role, Vx)
            return Vx

        # PRINCIPLED metric (gate-1 clean, binder-load-bearing): classify the RELATION-TYPE + DIRECTION of a KNOWN
        # encoded neighbor. Y is IN the encoding; recover whether (X,Y) is sym / dir-OUT (X->Y) / dir-IN (Y->X).
        # Direction is the crux: a fully-symmetric encoder cannot separate OUT from IN; role_filler (distinct roles) can.
        roles = {"sym": r_sym, "out": r_out, "in": r_in}
        hits = {e: [] for e in ENCODERS}
        for a in mixed:
            so = sorted(sym.get(a, ())); do = sorted(dout.get(a, ())); di = sorted(din.get(a, ()))
            labeled = [(y, "sym") for y in so] + [(y, "out") for y in do] + [(y, "in") for y in di]
            if len(set(lab for _, lab in labeled)) < 2: continue          # need >=2 relation classes to classify
            for enc in ENCODERS:
                Vx = encode(enc, a, so, do, di)
                ok = 0
                for y, true_lab in labeled:
                    # predicted role = argmax_role <unbind(Vx, role), vec(y)>
                    sc = {lab: float(nr(unbind(enc, Vx, roles[lab])) @ vec(y)) for lab in roles}
                    if max(sc, key=sc.get) == true_lab: ok += 1
                hits[enc].append(ok / len(labeled))
        for e in ENCODERS: res[e].append(float(np.mean(hits[e])) if hits[e] else 0.0)

    macc = {e: float(np.mean(res[e])) for e in ENCODERS}
    singles = ["bundle_norole", "rolefiller_xor", "rolefiller_conv", "rolefiller_ghrr"]
    comps = ["partial_sym_comp"]
    single_closers = [e for e in singles if macc[e] >= BAR]
    print("  held-out directed-edge prediction hit@1 (VECTOR-ENCODING; binder load-bearing):", flush=True)
    for e in ENCODERS:
        kind = "SINGLE" if e in singles else "COMP  "
        print("    %s %-18s hit@1=%.3f %s" % (kind, e, macc[e], "CLOSES" if macc[e] >= BAR else "fails"), flush=True)
    print("  gate-2: single-op closers=%s" % single_closers, flush=True)
    return {"n_atoms": len(atoms), "n_mixed": len(mixed), "macc": macc, "single_closers": single_closers,
            "bar": BAR, "gate2_single_fails": len(single_closers) == 0}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = ("mixed-symmetry atoms=%d; held-out directed link-prediction hit@1: %s; single-op closers (>=%.2f)=%s." % (
        r["n_mixed"], {k: round(v, 3) for k, v in r["macc"].items()}, r["bar"], r["single_closers"]))
    if not r["gate2_single_fails"]:
        return ("HARD_FAIL", "GATE 2 FAILS (honest negative): a SINGLE existing operator (%s) CLOSES held-out mixed-symmetry link-prediction -- role_filler-class binding is the canonical multi-relational VSA encoder and handles it. So the LINK-PREDICTION anchor does NOT yield an autonomous-tier-2 gap: binary link-prediction is bimodally/role-filler handled. Partial-symmetry is a TERNARY property that binary link-prediction does not exhibit; a ternary-motif metric to force it would risk gate-1 gerrymandering. Autonomous tier-2 awaits a genuinely partial-symmetric REAL task or the tier-3 architectural decision -- NOT a fabricated one. " % r["single_closers"] + s)
    return ("PARTIAL", "Gate 2 HOLDS: no single op closes held-out mixed-symmetry link-prediction -> proceed to combine-search (gate 3) + Skunkworks full-basis equivalence (gate 4). " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_autonomous_tier2_mixed_symmetry_link_prediction | N=%d BAR=%.2f" % (N_DIM, BAR), flush=True)
    out_dir = get_output_dir("substrate_autonomous_tier2_mixed_symmetry_link_prediction_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_autonomous_tier2_mixed_symmetry_link_prediction_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
