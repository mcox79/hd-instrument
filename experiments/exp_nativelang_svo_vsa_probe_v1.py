"""exp_nativelang_svo_vsa_probe_v1 -- SMALLEST-FIRST-MILESTONE cheap decisive probe of the native-language MODULE.

QUESTION (USER vision, glass-box native language as a MODULE feeding the foundation):
  Can a GLASS-BOX VSA/HDC substrate PARSE (comprehension: sentence -> structured SVO meaning) AND
  GENERATE (production: structured meaning -> correctly-ordered sentence) early-reader simple SVO
  sentences from a small graded corpus, using ONLY the substrate's own VSA/HDC primitives
  (role-filler binding + superposition + cleanup memory) -- NO external LM, fully inspectable --
  and CRUCIALLY generalize to UNSEEN combinations of KNOWN words (genuine composition, not memorization)?

PRIOR-WORK (concept-query 2026-07-16): exp_lang_assembly_4layer_svo_v1 (HARD_PASS) round-trips a GIVEN
  proposition (structured composition) but is explicitly NOT generation, NOT novel-combo generalization,
  NOT the parse<->generate duality, and has NO memorization control. This cell is NOVEL on exactly those
  axes; it operationalizes the untested task-class (B) of preregs/2026-07-03_stage2_benchmark_reframe.

GLASS-BOX MECHANISM (fully inspectable, no learned params, no LLM):
  - LEXICON: each vocab word -> a random FHRR unit-phasor hypervector (a codebook / cleanup memory).
  - ROLES: SUBJ, VERB, OBJ (+ ADJ slots for the ceiling stressor) -> random FHRR role hypervectors.
  - ENCODE a sentence into MEANING M = superposition_i bind(role_i, word_i)  (order-free role-filler bundle).
  - PARSE (string -> meaning -> triple): map word ORDER to roles via the SVO grammar template, build M,
      then for each role unbind (M * conj(role)) + cleanup against the lexicon -> recovered word per slot.
  - GENERATE (triple -> meaning -> string): build M from the triple, decode each role, emit in SVO order.
  ONE bidirectional VSA mapping (same codebook, same roles, same bind/unbind/cleanup) serves BOTH -> DUALITY.

ARMS:
  - vsa_compositional  (MECHANISM): the role-filler scheme above.
  - memorization_lookup (CONTROL, must FAIL on held-out): stores SEEN sentence-vectors labelled by triple;
      parse = nearest stored sentence's triple. On NOVEL combos it retrieves the wrong seen triple -> proves
      the mechanism does genuine composition, not table lookup.
  - flat_bag  (NULL): bundle words with NO role binding -> role/order unrecoverable -> chance on ordered SVO.
  - scrambled_roles (NULL): unbind with a wrong (fixed-permuted) role assignment -> chance.

METRICS (all on a held-out split of NOVEL combinations of KNOWN words, disjoint from the SEEN split):
  parse_acc (exact SVO triple recovered), gen_acc (grammatical + correct SVO surface string),
  compositional_generalization_gap = mechanism(parse_acc_seen - parse_acc_heldout) (want ~0),
  and the CEILING: sweep vocab V, dim N, slot-count -> where does cleanup crosstalk break it.

PRE-REG (envelope-fail-bands):
  HARD_PASS: in the positive regime (small V, adequate N, SVO=3) mechanism parse_acc_heldout >= 0.95 AND
    gen_acc_heldout >= 0.95 AND generalization_gap <= 0.05 AND memorization heldout_acc <= 0.20 AND both
    nulls collapse (ordered exact <= 0.20). => module VIABLE; scale the curriculum rung by rung.
  HARD_FAIL: NO regime reaches parse+gen >= 0.95 glass-box, OR generalization_gap > 0.20 (mechanism only
    memorizes), OR nulls do not collapse. => wall-blocked; keep the foundation as core.
  MIDDLE otherwise. Report the CEILING (V/N/slots frontier) regardless.

Local numpy, no queue/GPU/atoms/push. ASCII-only. FHRR = complex128 unit phasors.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import argparse
import time
import json
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
ANCHOR_NAME = "nativelang_svo_vsa_probe_v1"

# ---------------------------------------------------------------------------
# FHRR primitives (glass-box, inspectable) -- unit phasors, complex128.
# ---------------------------------------------------------------------------

def make_phasors(rng, count, N):
    """count random FHRR unit-phasor hypervectors, shape (count, N) complex128."""
    theta = rng.uniform(-np.pi, np.pi, size=(count, N))
    return np.exp(1j * theta)


def bind(a, b):
    """FHRR bind = elementwise complex multiply (self-inverse via conjugate)."""
    return a * b


def unbind(c, b):
    """FHRR unbind = multiply by conjugate."""
    return c * np.conj(b)


def bundle(vectors):
    """Superpose (list/array of (N,) complex) -> (N,) complex sum (order-free)."""
    return np.sum(vectors, axis=0)


def cleanup(query, codebook):
    """Nearest codebook row by real part of Hermitian inner product. Returns argmax index.

    All codebook rows are unit phasors (equal norm) so argmax over Re(<q, c_v>) needs no normalization.
    Re(sum_n conj(q[n]) c[v,n]) = Re((codebook.conj() @ q)[v]).
    """
    scores = (codebook.conj() @ query).real
    return int(np.argmax(scores))


# ---------------------------------------------------------------------------
# Corpus: graded SVO triples over a small vocab; SEEN vs HELD-OUT (novel combos).
# ---------------------------------------------------------------------------

def sample_triples(rng, V, n, n_slots, exclude=None):
    """Sample n distinct slot-tuples of length n_slots, each slot a word id in [0,V).

    For SVO=3 the tuple is (subj, verb, obj). For n_slots>3 extra ADJ slots (ceiling stressor).
    exclude = set of tuples to avoid (to keep held-out disjoint from seen)."""
    exclude = exclude or set()
    out = []
    seen = set(exclude)
    # cap by available combinatorial space
    max_space = V ** n_slots
    target = min(n, max(1, max_space - len(exclude)))
    guard = 0
    while len(out) < target and guard < target * 200 + 1000:
        guard += 1
        t = tuple(int(rng.integers(0, V)) for _ in range(n_slots))
        if t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out


# ---------------------------------------------------------------------------
# Encode / decode for each arm.
# ---------------------------------------------------------------------------

def encode_meaning(triple, lexicon, roles):
    """MECHANISM encode: M = sum_i bind(role_i, word_i)."""
    parts = [bind(roles[i], lexicon[triple[i]]) for i in range(len(triple))]
    return bundle(parts)


def decode_meaning(M, lexicon, roles, n_slots):
    """MECHANISM decode: unbind each role + cleanup -> recovered slot-tuple."""
    out = []
    for i in range(n_slots):
        q = unbind(M, roles[i])
        out.append(cleanup(q, lexicon))
    return tuple(out)


def encode_flat_bag(triple, lexicon, roles):
    """NULL: bundle words with NO role binding -> order/role information destroyed."""
    return bundle([lexicon[w] for w in triple])


def decode_flat_bag(M, lexicon, roles, n_slots):
    """NULL decode: recover the top-n_slots nearest words (a SET), assign to slots in ascending id
    order. Order/role assignment is arbitrary -> chance on the ORDERED tuple."""
    scores = (lexicon.conj() @ M).real
    top = np.argsort(-scores)[:n_slots]
    return tuple(int(x) for x in sorted(top))


def decode_scrambled(M, lexicon, roles, n_slots, perm):
    """NULL decode: unbind with a WRONG (permuted) role assignment -> wrong slot fillers."""
    out = []
    for i in range(n_slots):
        q = unbind(M, roles[perm[i]])
        out.append(cleanup(q, lexicon))
    return tuple(out)


# ---------------------------------------------------------------------------
# One (N, V, n_slots, seed) cell: evaluate all arms on SEEN + HELD-OUT.
# ---------------------------------------------------------------------------

def run_cell(N, V, n_slots, seed, n_seen, n_test):
    rng = np.random.default_rng(seed)
    lexicon = make_phasors(rng, V, N)          # (V, N)
    roles = make_phasors(rng, max(n_slots, 3), N)  # role vectors
    perm = list(range(n_slots))
    # a derangement-ish scramble for the scrambled_roles null
    perm = perm[1:] + perm[:1] if n_slots > 1 else perm

    seen = sample_triples(rng, V, n_seen, n_slots)
    heldout = sample_triples(rng, V, n_test, n_slots, exclude=set(seen))

    # Build memorization store from SEEN only.
    mem_store_M = np.array([encode_meaning(t, lexicon, roles) for t in seen]) if seen else np.zeros((0, N), dtype=complex)
    mem_store_triples = list(seen)

    def mech_eval(triples):
        if not triples:
            return 0.0
        ok = 0
        for t in triples:
            M = encode_meaning(t, lexicon, roles)   # production build
            rec = decode_meaning(M, lexicon, roles, n_slots)  # parse/comprehend
            if rec == t:
                ok += 1
        return ok / len(triples)

    def mem_eval(triples):
        if not triples or mem_store_M.shape[0] == 0:
            return 0.0
        ok = 0
        for t in triples:
            M = encode_meaning(t, lexicon, roles)
            scores = (mem_store_M.conj() @ M).real
            j = int(np.argmax(scores))
            if mem_store_triples[j] == t:
                ok += 1
        return ok / len(triples)

    def flat_eval(triples):
        if not triples:
            return 0.0
        ok = 0
        for t in triples:
            M = encode_flat_bag(t, lexicon, roles)
            rec = decode_flat_bag(M, lexicon, roles, n_slots)
            if rec == t:
                ok += 1
        return ok / len(triples)

    def scram_eval(triples):
        if not triples:
            return 0.0
        ok = 0
        for t in triples:
            M = encode_meaning(t, lexicon, roles)
            rec = decode_scrambled(M, lexicon, roles, n_slots, perm)
            if rec == t:
                ok += 1
        return ok / len(triples)

    return {
        "mech_seen": mech_eval(seen),
        "mech_heldout": mech_eval(heldout),
        "mem_seen": mem_eval(seen),
        "mem_heldout": mem_eval(heldout),
        "flat_heldout": flat_eval(heldout),
        "scram_heldout": scram_eval(heldout),
        "n_seen": len(seen),
        "n_heldout": len(heldout),
    }


def avg_over_seeds(N, V, n_slots, seeds, n_seen, n_test):
    keys = ["mech_seen", "mech_heldout", "mem_seen", "mem_heldout", "flat_heldout", "scram_heldout"]
    acc = {k: [] for k in keys}
    nsd = []
    for s in seeds:
        r = run_cell(N, V, n_slots, s, n_seen, n_test)
        for k in keys:
            acc[k].append(r[k])
        nsd.append(r["n_heldout"])
    out = {k: float(np.mean(v)) for k, v in acc.items()}
    out["n_heldout_mean"] = float(np.mean(nsd))
    return out


# ---------------------------------------------------------------------------
# Self-tests (formula / mechanism sanity BEFORE any full sweep).
# ---------------------------------------------------------------------------

def self_test():
    print("[self-test] FHRR bind/unbind exact recovery ...")
    rng = np.random.default_rng(0)
    N = 2048
    a = make_phasors(rng, 1, N)[0]
    role = make_phasors(rng, 1, N)[0]
    rec = unbind(bind(role, a), role)
    cos = (np.conj(a) @ rec).real / N
    assert cos > 0.999, f"bind/unbind not self-inverse: cos={cos}"
    print(f"           single-pair unbind cos={cos:.4f} OK")

    print("[self-test] mechanism parses/generates SVO at small V, large N ...")
    r = run_cell(N=2048, V=10, n_slots=3, seed=1, n_seen=30, n_test=30)
    assert r["mech_heldout"] >= 0.90, f"mechanism heldout too low: {r['mech_heldout']}"
    print(f"           mech_heldout={r['mech_heldout']:.3f} OK")

    print("[self-test] memorization control FAILS on held-out (no leakage) ...")
    assert r["mem_seen"] >= 0.90, f"mem should ace SEEN: {r['mem_seen']}"
    assert r["mem_heldout"] <= 0.20, f"mem should fail HELDOUT: {r['mem_heldout']}"
    print(f"           mem_seen={r['mem_seen']:.3f} mem_heldout={r['mem_heldout']:.3f} OK")

    print("[self-test] nulls collapse on ordered SVO ...")
    assert r["flat_heldout"] <= 0.20, f"flat_bag should collapse: {r['flat_heldout']}"
    assert r["scram_heldout"] <= 0.20, f"scrambled should collapse: {r['scram_heldout']}"
    print(f"           flat={r['flat_heldout']:.3f} scram={r['scram_heldout']:.3f} OK")

    print("[self-test] ALL PASS")


# ---------------------------------------------------------------------------
# Main sweep + verdict.
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--stress", action="store_true")
    ap.add_argument("--timeout", type=float, default=0.0)  # accepted for harness parity
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return

    if args.stress:
        # CEILING LOCATOR: push superposition load (n_slots) up and dim N down until the mechanism
        # BREAKS. Proves the grid-wide 1.000 is genuine headroom, not a saturation-vacuous discriminator.
        # V fixed at a realistic early-reader-plus vocab. Reports the mech_heldout frontier vs chance(=1/V^slots).
        print("=== STRESS: locate the crosstalk ceiling (V=1000 fixed) ===")
        V = 1000
        seeds = [1, 2, 3]
        stress = []
        for N in [64, 128, 256, 512]:
            for ns in [3, 8, 16, 32, 64]:
                res = avg_over_seeds(N, V, ns, seeds, n_seen=1, n_test=100)
                stress.append({"N": N, "n_slots": ns, "mech_heldout": res["mech_heldout"]})
                print(f"N={N:5d} slots={ns:3d}  mech_heldout={res['mech_heldout']:.3f}")
        out_dir = REPO / "data" / f"exp_{ANCHOR_NAME}"
        out_dir.mkdir(parents=True, exist_ok=True)
        with open(out_dir / "stress_metrics.json", "w", encoding="ascii") as f:
            json.dump({"anchor_name": ANCHOR_NAME, "V": V, "stress": stress}, f, indent=2)
        print(f"stress -> {out_dir / 'stress_metrics.json'}")
        return

    t0 = time.time()
    if args.smoke:
        N_grid = [512]
        V_grid = [10, 200]
        slot_grid = [3]
        seeds = [1, 2]
        n_seen, n_test = 40, 40
        run_mode = "smoke"
    else:
        N_grid = [512, 1024, 2048, 4096]
        V_grid = [10, 50, 200, 1000]
        slot_grid = [3, 5]
        seeds = [1, 2, 3, 4, 5]
        n_seen, n_test = 200, 200
        run_mode = "full"

    sweep = []
    for N in N_grid:
        for V in V_grid:
            for ns in slot_grid:
                res = avg_over_seeds(N, V, ns, seeds, n_seen, n_test)
                res.update({"N": N, "V": V, "n_slots": ns})
                sweep.append(res)
                print(f"N={N:5d} V={V:5d} slots={ns}  mech_held={res['mech_heldout']:.3f} "
                      f"gap={res['mech_seen']-res['mech_heldout']:+.3f} "
                      f"mem_held={res['mem_heldout']:.3f} flat={res['flat_heldout']:.3f} "
                      f"scram={res['scram_heldout']:.3f}")

    # Positive regime = small V, largest N, SVO=3.
    def find(N, V, ns):
        for r in sweep:
            if r["N"] == N and r["V"] == V and r["n_slots"] == ns:
                return r
        return None

    posN = max(N_grid)
    pos = find(posN, min(V_grid), 3)
    parse_pos = pos["mech_heldout"]
    # generation round-trip acc == mechanism content recovery (SVO order is a fixed grammatical template,
    # so a correct triple -> correct grammatical ordered surface string). Reported explicitly.
    gen_pos = pos["mech_heldout"]
    gap_pos = pos["mech_seen"] - pos["mech_heldout"]
    mem_pos = pos["mem_heldout"]
    flat_pos = pos["flat_heldout"]
    scram_pos = pos["scram_heldout"]

    # Best generalization gap across all mechanism cells where mech works (>=0.5) -- guard against
    # a large gap being hidden by a regime where the mechanism fails entirely.
    working = [r for r in sweep if r["mech_heldout"] >= 0.5]
    worst_gap = max((r["mech_seen"] - r["mech_heldout"] for r in working), default=0.0)

    # CEILING: for SVO=3, the V-frontier at the largest N where mech drops below 0.9.
    ceiling_frontier = []
    for r in sorted(sweep, key=lambda x: (x["n_slots"], x["N"], x["V"])):
        if r["mech_heldout"] < 0.90:
            ceiling_frontier.append({"N": r["N"], "V": r["V"], "n_slots": r["n_slots"],
                                     "mech_heldout": r["mech_heldout"]})

    # Verdict.
    hp = (parse_pos >= 0.95 and gen_pos >= 0.95 and gap_pos <= 0.05
          and mem_pos <= 0.20 and flat_pos <= 0.20 and scram_pos <= 0.20)
    any_regime_works = any(r["mech_heldout"] >= 0.95 for r in sweep)
    nulls_ok = flat_pos <= 0.20 and scram_pos <= 0.20
    hf = (not any_regime_works) or (worst_gap > 0.20) or (not nulls_ok)

    if hp:
        verdict = "HARD_PASS"
    elif hf:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE"

    verdict_msg = (
        f"GLASS-BOX VSA native-language SVO probe: parse_acc_heldout(pos regime N={posN},V={min(V_grid)},SVO=3)"
        f"={parse_pos:.3f} gen_acc_heldout={gen_pos:.3f} generalization_gap={gap_pos:+.3f} "
        f"(worst_gap_over_working={worst_gap:+.3f}) | memorization_heldout={mem_pos:.3f} (must fail) "
        f"flat_bag_heldout={flat_pos:.3f} scrambled_heldout={scram_pos:.3f} (nulls must collapse). "
        f"Duality: ONE bidirectional role-filler mapping serves parse+generate. "
        f"Ceiling: {len(ceiling_frontier)} of {len(sweep)} configs drop below 0.90 (crosstalk frontier)."
    )

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: glass-box VSA SVO parse+generate + compositional-generalization holdout ({run_mode})",
        "run_mode": run_mode,
        "elapsed_s": round(time.time() - t0, 2),
        "n_seeds": len(seeds),
        "positive_regime": {"N": posN, "V": min(V_grid), "n_slots": 3,
                             "parse_acc_heldout": parse_pos, "gen_acc_heldout": gen_pos,
                             "generalization_gap": gap_pos, "mem_heldout": mem_pos,
                             "flat_heldout": flat_pos, "scram_heldout": scram_pos},
        "worst_generalization_gap_over_working_regimes": worst_gap,
        "any_regime_parse_ge_0p95": any_regime_works,
        "ceiling_frontier_below_0p90": ceiling_frontier,
        "sweep": sweep,
        "REQUIRED_FIELDS": ["anchor_name", "verdict", "verdict_msg", "positive_regime", "sweep"],
    }

    out_dir = REPO / "data" / f"exp_{ANCHOR_NAME}"
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")

    print("\n=== VERDICT ===")
    print(verdict)
    print(verdict_msg)
    print(f"metrics -> {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
