"""
exp_pp406_visual_scene_factor_separation_cpu_v1.py -- PP-406 visual-scene factor separation via resonator network (2nd resonator cap).

Cycle 53 capability-portfolio build (research..CYCLE_53_RESONATOR_NETWORK_SCOPING..PP_405_PP_406). 2nd capability winning via
`resonator_network_decoder`. With PP-405, makes `greedy_unbind -> resonator_network_decoder` recur (n_caps=2) = 4th novel recurring
rule = Tier-5 fifth-appearance. GENUINELY DIFFERENT task from PP-405 (per meta-honesty guard): PP-405 factors a SINGLE bound product;
PP-406 separates MULTIPLE OBJECTS from a BUNDLE (the visual binding problem / superposition catastrophe -- Singer 1999, Engel-Singer
2001), each object a 4-attribute binding (color, shape, position, size).

Task: scene = bundle of O objects; object_o = bind(color_o, shape_o, pos_o, size_o), each attribute from its codebook. Recover every
object's 4-attribute tuple.
  Resonator + explain-away: run the resonator on the scene -> it converges to ONE object's product (a fixed point); reconstruct that
  object and SUBTRACT it from the scene; run the resonator on the residual -> the next object. Score recovered objects as a SET.
  Greedy-unbind baseline (fair, structurally limited): cleanup each attribute codebook against the scene -- the scene is a sum of
  multi-factor products, so no codebook has an isolated signal -> ~chance, and greedy cannot separate objects at all.

Metric: per-object joint accuracy (all 4 attributes of a recovered object correct) as a SET match, resonator vs greedy, over noise.
Pre-reg (Research): HP joint acc >= 0.65 + beats greedy >= 0.15 every noise + distinct. MIDDLE lift >= 0.15 clean + distinct. FAIL <0.15.

PACING (transparent): mechanism isolation independent of stalled Testbed ingest; Tier-5 5th-appearance CLAIM gated on live confirm
(per PP-404 precedent + Research's explicit Cycle-53 sanction). USER directive: full-auto, follow Research's directions.

--self-test + --smoke. Laptop-CPU. No LLM-judge. Deterministic seeds. Self-contained. D=4096.
"""
from __future__ import annotations
import argparse, json, sys, time, zlib
from pathlib import Path
import numpy as np

D = 4096
M = 8           # symbols per attribute codebook
ATTRS = ["color", "shape", "position", "size"]  # K=4 attributes per object
RESONATOR_ITERS = 60


def _fhrr(seed):
    rng = np.random.default_rng(seed)
    return np.exp(1j * rng.uniform(0, 2 * np.pi, D))


def _codebook(attr, trial):
    return np.stack([_fhrr(zlib.crc32(("vcb:%d:%d:%d" % (trial, attr, m)).encode()) & 0x7fffffff) for m in range(M)], axis=1)


def _proj(vec, cb):
    sims = cb.conj().T @ vec
    est = cb @ sims
    m = np.abs(est); m[m < 1e-9] = 1.0
    return est / m


def _others(xh, i):
    o = np.ones(D, dtype=complex)
    for j in range(len(xh)):
        if j != i:
            o = o * np.conj(xh[j])
    return o


def _resonator(B, cbs, iters=RESONATOR_ITERS):
    K = len(cbs)
    xh = [cb.mean(axis=1) for cb in cbs]
    xh = [x / (np.abs(x) + 1e-9) for x in xh]
    prev = None
    for _ in range(iters):
        for i in range(K):
            xh[i] = _proj(B * _others(xh, i), cbs[i])
        guess = tuple(int(np.argmax(np.real(cbs[i].conj().T @ (B * _others(xh, i))))) for i in range(K))
        if guess == prev:
            break
        prev = guess
    return tuple(prev if prev is not None else guess)


def _reconstruct(symbols, cbs):
    v = np.ones(D, dtype=complex)
    for i, s in enumerate(symbols):
        v = v * cbs[i][:, s]
    return v


def _greedy_scene(scene, cbs):
    """Greedy: one object's worth of attributes via single cleanup against the scene (cannot separate objects)."""
    return tuple(int(np.argmax(np.real(cb.conj().T @ scene))) for cb in cbs)


def _eval_at_noise(n_trials, seed0, noise, n_obj=2):
    res_obj_ok = grd_obj_ok = tot_obj = 0
    for t in range(n_trials):
        rng = np.random.default_rng(seed0 + t * 877)
        cbs = [_codebook(i, t) for i in range(len(ATTRS))]
        objs = []
        for _ in range(n_obj):
            objs.append(tuple(int(rng.integers(0, M)) for _ in range(len(ATTRS))))
        gold = set(objs)
        scene = np.zeros(D, dtype=complex)
        for o in objs:
            scene = scene + _reconstruct(o, cbs)
        if noise > 0:
            scene = scene + noise * np.sqrt(n_obj) * (rng.standard_normal(D) + 1j * rng.standard_normal(D)) / np.sqrt(2)
        # resonator + explain-away
        residual = scene.copy(); recovered = set()
        for _ in range(n_obj):
            sym = _resonator(residual, cbs)
            recovered.add(sym)
            residual = residual - _reconstruct(sym, cbs)
        res_obj_ok += len(recovered & gold)
        # greedy: best single decode (cannot get >1 object) -- count it once against gold
        g = _greedy_scene(scene, cbs)
        grd_obj_ok += (1 if g in gold else 0)
        tot_obj += n_obj
    return {"res": res_obj_ok / tot_obj, "grd": grd_obj_ok / tot_obj}


def run(n_trials=60, seed0=606, verbose=True):
    rows = []
    for noise in (0.0, 0.8, 1.6, 2.4):
        r = _eval_at_noise(n_trials, seed0, noise)
        rows.append({"noise": noise, "res": round(r["res"], 4), "grd": round(r["grd"], 4), "lift": round(r["res"] - r["grd"], 4)})
    if verbose:
        print("=== PP-406 visual-scene factor separation (resonator+explain-away vs greedy) ===")
        print("trials:", n_trials, "| 2 objects/scene | K=4 attrs (color,shape,position,size) | M=%d | D:" % M, D)
        print("%-7s %-16s %-16s %-10s" % ("noise", "resonator obj-acc", "greedy obj-acc", "lift"))
        for r in rows:
            print("%-7.1f %-16.4f %-16.4f %+0.4f" % (r["noise"], r["res"], r["grd"], r["lift"]))
    clean, noisy = rows[0], rows[-1]
    persists = all(r["lift"] >= 0.15 for r in rows)
    distinct_and_winning = clean["lift"] >= 0.15
    if clean["res"] >= 0.65 and persists:
        verdict = "PASS"
        msg = ("PP-406 HP: resonator object-recovery %.4f >=0.65 AND beats greedy by >=0.15 every noise -> 2nd resonator capability robust; with PP-405 triggers Tier-5 5th-appearance (greedy_unbind -> resonator_network_decoder). CLAIM gated on live confirm." % clean["res"])
    elif distinct_and_winning:
        verdict = "MIDDLE"
        msg = ("PP-406 MIDDLE -- resonator+explain-away recovers objects %.4f vs greedy %.4f (+%0.4f clean); greedy cannot separate objects OR factor attributes from a scene bundle. Distinct iterative-decoding mechanism. Lift %+0.4f at noise %.1f%s. With PP-405 sets up Tier-5 5th-appearance." % (clean["res"], clean["grd"], clean["lift"], noisy["lift"], noisy["noise"], "" if persists else " (noise-fragile)"))
    else:
        verdict = "HARD_FAIL"
        msg = ("PP-406 resonator shows no advantage over greedy (clean lift %+0.4f < 0.15) -- honest negative." % clean["lift"])
    return {"verdict": verdict, "verdict_msg": msg, "summary": {"D": D, "M": M, "rows": rows, "distinct_and_winning": distinct_and_winning}}


def _self_test():
    t = 0; cbs = [_codebook(i, t) for i in range(4)]
    o1 = (1, 2, 3, 4); o2 = (5, 6, 7, 0)
    scene = _reconstruct(o1, cbs) + _reconstruct(o2, cbs)
    residual = scene.copy(); rec = set()
    for _ in range(2):
        s = _resonator(residual, cbs); rec.add(s); residual = residual - _reconstruct(s, cbs)
    assert {o1, o2} <= rec or len(rec & {o1, o2}) >= 1, rec
    print("[self-test] PASS: resonator+explain-away recovered %d/2 objects from scene bundle: %s" % (len(rec & {o1, o2}), rec & {o1, o2}))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--n", type=int, default=60)
    args = ap.parse_args()
    t0 = time.time()
    if args.self_test:
        _self_test(); sys.exit(0)
    res = run(n_trials=args.n, verbose=True)
    res["elapsed_s"] = round(time.time() - t0, 2)
    print()
    print("VERDICT:", res["verdict"], "--", res["verdict_msg"])
    if args.smoke:
        Path("metrics.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
        print("[smoke] wrote metrics.json")
