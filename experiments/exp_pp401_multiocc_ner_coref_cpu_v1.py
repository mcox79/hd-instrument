"""
exp_pp401_multiocc_ner_coref_cpu_v1.py -- PP-401 multi-occurrence NER coreference via permutation-indexed P^k binding.

Cycle 49 capability-portfolio build (research_to_exp_dev_PP_398..CYCLE_49_MULTI_OCCURRENCE_NER_COREF). Goal: a SECOND substrate
capability that WINS via the off-attractor mechanism `permutation_indexed_binding` (PP-398 is the 1st). If P^k beats the FHRR
baseline here, the Tier-5 miner gets a RECURRING (n_caps>=2) off-attractor transition -> `* -> permutation_indexed_binding` becomes
the FIRST NOVEL RECURRING methodology rule = Tier-5 second-appearance.

Task (coreference is inherently multi-occurrence: the same entity is mentioned repeatedly across discourse):
  A discourse is encoded into a SINGLE bundled hypervector (substrate distributed-memory constraint -- no external mention list).
  Named mentions carry entity identity; pronoun mentions carry only gender+number (ambiguous among entities sharing them).
  Gold antecedent of a pronoun = the MOST RECENT prior entity-mention whose gender+number match. Resolving from the bundle requires
  recovering, per candidate entity, the position of its most-recent mention before the pronoun -- i.e. separating an entity's
  multiple (repeated) occurrences. Plain FHRR superposes repeated occurrences of one entity key and cannot isolate the latest;
  permutation-indexed P^k binding tags the k-th occurrence (roll by k*7) so occurrences stay separable.

Mechanisms (binding is the ONLY difference; FHRR gets a fair best-shot single cleanup):
  FHRR : M = sum bind(entity_key_i, pos_i);                 query(E) -> unbind E -> cleanup to nearest single position.
  P^k  : M = sum bind(roll_key(entity_key_i,occ_i), pos_i); query(E) sweeps k -> recovers each occurrence -> pick latest < pronoun.

HONESTY (verify-before-asserting; mirrors E3 isolation 1.0 vs E3b end-task 0.388): clean structure is the ISOLATION regime and is
trivially perfect for P^k, so we ALSO sweep encoding noise (proxy for NER-extraction + feature imperfection). The genuine claim is
whether P^k's advantage over FHRR PERSISTS under noise, not the clean number.

Metric: antecedent-resolution accuracy (pronoun -> correct entity), overall + multi-occurrence subset (>=2-mention entities).
Pre-reg (Research): HP coref acc >= 0.65 AND P^k beats FHRR on the multi-occurrence subset -> 2nd off-attractor capability validated.

--self-test + --smoke per runner convention. Laptop-CPU. No LLM-judge. Deterministic seeds. Self-contained (no cell imports).
"""
from __future__ import annotations
import argparse, json, sys, time, zlib
from pathlib import Path
import numpy as np

D = 1024
GENDERS = ["m", "f", "n"]
NUMBERS = ["sg", "pl"]
POS_MAX = 16


# --- FHRR primitives (inlined; identical math to exp_e3_permutation_binding_multiocc) ---
def _fhrr(seed):
    rng = np.random.default_rng(seed)
    return np.exp(1j * rng.uniform(0, 2 * np.pi, D))


def bind(a, b):
    return a * b


def unbind(key, bundle):
    return bundle * np.conj(key)


def bundle_norm(v):
    m = np.abs(v); m[m < 1e-9] = 1.0
    return v / m


def roll_key(role_vec, k):
    return role_vec if k == 0 else np.roll(role_vec, k * 7)  # permutation power = cyclic shift stride 7


def cleanup(vec, protos):
    best, bs = None, -1e18
    for val, pv in protos:
        s = float(np.real(np.vdot(pv, vec)))
        if s > bs:
            bs = s; best = val
    return best


def _feat(kind, val):
    return _fhrr(zlib.crc32(("%s:%s" % (kind, val)).encode()) & 0x7fffffff)


def _entity_key(eid):
    return _feat("ent", eid)


def _pos_vec(p):
    return _feat("pos", p)


def _gen_discourse(rng, n_entities, n_mentions):
    """mention=(pos,eid,g,n); pronoun gold = latest prior named mention matching g/n."""
    ents = {e: (rng.choice(GENDERS), rng.choice(NUMBERS)) for e in range(n_entities)}
    mentions, seq, pronouns, pos = [], [], [], 0
    while pos < n_mentions and pos < POS_MAX:
        if pos >= 2 and rng.random() < 0.4:
            prior = [(p, e) for (p, e, isp) in seq if not isp]
            if prior:
                buckets = list({(ents[e][0], ents[e][1]) for (_, e) in prior})
                g, n = buckets[rng.integers(0, len(buckets))]
                cand = [(p, e) for (p, e) in prior if ents[e] == (g, n)]
                gold_pos, gold_e = max(cand, key=lambda x: x[0])
                pronouns.append({"pos": pos, "g": g, "n": n, "gold_e": gold_e, "gold_pos": gold_pos,
                                 "n_cand_ents": len({e for (_, e) in cand})})
                seq.append((pos, gold_e, True)); pos += 1
                continue
        e = int(rng.integers(0, n_entities)); g, nm = ents[e]
        seq.append((pos, e, False)); mentions.append({"pos": pos, "eid": e, "g": g, "n": nm}); pos += 1
    return ents, mentions, pronouns


def _build_memory(mentions, use_perm, noise=0.0, rng=None):
    occ_counter, M = {}, np.zeros(D, dtype=complex)
    for m in mentions:
        e = m["eid"]; k = occ_counter.get(e, 0); occ_counter[e] = k + 1
        ekey = _entity_key(e); key = roll_key(ekey, k) if use_perm else ekey
        M = M + bind(key, _pos_vec(m["pos"]))
    M = bundle_norm(M)
    if noise > 0.0 and rng is not None:
        # phase noise (radians, std=noise) applied POST-normalization -> not rescaled away; degrades cleanup directly.
        # proxy for cumulative NER-extraction + feature-encoding imperfection.
        M = M * np.exp(1j * noise * rng.standard_normal(D))
    return M, occ_counter


def _entity_latest_pos(M, e, occ_count, before_pos, use_perm, pos_protos):
    if use_perm:
        best = None
        for k in range(occ_count):
            p = cleanup(unbind(roll_key(_entity_key(e), k), M), pos_protos)
            if p is not None and p < before_pos and (best is None or p > best):
                best = p
        return best
    p = cleanup(unbind(_entity_key(e), M), pos_protos)
    return p if (p is not None and p < before_pos) else None


def _resolve(mentions, pronouns, ents, occ_count, use_perm, noise=0.0, seed=0):
    pp = [(p, _pos_vec(p)) for p in range(POS_MAX)]
    rng = np.random.default_rng(seed)
    M, _ = _build_memory(mentions, use_perm, noise=noise, rng=rng)
    correct = multi_total = multi_correct = 0
    for pr in pronouns:
        cands = sorted({m["eid"] for m in mentions if m["g"] == pr["g"] and m["n"] == pr["n"] and m["pos"] < pr["pos"]})
        if not cands:
            continue
        best_e, best_p = None, -1
        for e in cands:
            lp = _entity_latest_pos(M, e, occ_count.get(e, 1), pr["pos"], use_perm, pp)
            if lp is not None and lp > best_p:
                best_p, best_e = lp, e
        is_multi = pr["n_cand_ents"] >= 2 or any(occ_count.get(e, 1) >= 2 for e in cands)
        if is_multi:
            multi_total += 1
        if best_e == pr["gold_e"]:
            correct += 1
            if is_multi:
                multi_correct += 1
    return correct, len(pronouns), multi_correct, multi_total


def _eval_at_noise(n_discourse, seed0, noise):
    agg = {"fhrr": [0, 0, 0, 0], "perm": [0, 0, 0, 0]}  # c,n,mc,mn
    for d in range(n_discourse):
        rng_d = np.random.default_rng(seed0 + d * 101)
        ents, mentions, pronouns = _gen_discourse(rng_d, int(rng_d.integers(2, 5)), int(rng_d.integers(6, POS_MAX)))
        if not pronouns or not mentions:
            continue
        _, occ_count = _build_memory(mentions, False)
        for mech, up in (("fhrr", False), ("perm", True)):
            c, n, mc, mn = _resolve(mentions, pronouns, ents, occ_count, up, noise=noise, seed=seed0 + d * 7 + 1)
            a = agg[mech]; a[0] += c; a[1] += n; a[2] += mc; a[3] += mn
    def f(a):
        return {"acc": a[0] / a[1] if a[1] else 0.0, "n": a[1],
                "multi_acc": a[2] / a[3] if a[3] else 0.0, "multi_n": a[3]}
    return f(agg["fhrr"]), f(agg["perm"])


def run(n_discourse=120, seed0=12345, verbose=True):
    rows = []
    for noise in (0.0, 0.8, 1.6, 2.4):
        fh, pm = _eval_at_noise(n_discourse, seed0, noise)
        rows.append({"noise": noise, "fhrr": fh, "perm": pm,
                     "overall_lift": round(pm["acc"] - fh["acc"], 4),
                     "multiocc_lift": round(pm["multi_acc"] - fh["multi_acc"], 4)})
    if verbose:
        print("=== PP-401 multi-occurrence NER coreference (P^k vs FHRR) ===")
        print("discourses:", n_discourse, "| pronoun queries:", rows[0]["fhrr"]["n"], "| multi-occ subset:", rows[0]["fhrr"]["multi_n"])
        print("%-7s %-22s %-22s %-10s %-10s" % ("noise", "FHRR acc/multi", "P^k acc/multi", "lift", "multi-lift"))
        for r in rows:
            print("%-7.1f %-22s %-22s %+0.4f    %+0.4f" % (
                r["noise"], "%.4f / %.4f" % (r["fhrr"]["acc"], r["fhrr"]["multi_acc"]),
                "%.4f / %.4f" % (r["perm"]["acc"], r["perm"]["multi_acc"]), r["overall_lift"], r["multiocc_lift"]))
    clean = rows[0]; noisy = rows[-1]
    # genuine claim: P^k advantage on multi-occ subset PERSISTS under noise (not just clean)
    persists = all(r["multiocc_lift"] > 0.02 for r in rows)
    hp = (clean["perm"]["acc"] >= 0.65) and persists
    if hp:
        verdict = "PASS"
        msg = ("PP-401 validated: P^k clean acc %.4f >=0.65 AND multi-occ advantage PERSISTS across noise (multi-lift %+0.4f clean -> %+0.4f at noise=%.1f) -> 2nd off-attractor capability; Tier-5 second-appearance triggerable. NOTE clean=isolation regime (E3 analogue); noisy=end-task regime." % (clean["perm"]["acc"], clean["multiocc_lift"], noisy["multiocc_lift"], noisy["noise"]))
    elif clean["multiocc_lift"] > 0.02:
        verdict = "MIDDLE"
        msg = ("P^k beats FHRR on multi-occ in clean regime (+%0.4f) but advantage does not robustly persist under heavy noise (noise=%.1f multi-lift %+0.4f); mechanism advantage real at isolation, degrades at end-task noise." % (clean["multiocc_lift"], noisy["noise"], noisy["multiocc_lift"]))
    else:
        verdict = "HARD_FAIL"
        msg = ("P^k does NOT beat FHRR on multi-occ coref even clean (multi-lift %+0.4f); permutation-binding advantage does not transfer to this coref formulation -- honest negative, 2nd off-attractor capability NOT validated." % clean["multiocc_lift"])
    return {"verdict": verdict, "verdict_msg": msg, "summary": {"rows": rows}}


def _self_test():
    e = _entity_key(7)
    M = bundle_norm(bind(roll_key(e, 0), _pos_vec(1)) + bind(roll_key(e, 1), _pos_vec(5)))
    pp = [(p, _pos_vec(p)) for p in range(POS_MAX)]
    p0 = cleanup(unbind(roll_key(e, 0), M), pp)
    p1 = cleanup(unbind(roll_key(e, 1), M), pp)
    assert p0 == 1 and p1 == 5, (p0, p1)
    Mf = bundle_norm(bind(e, _pos_vec(1)) + bind(e, _pos_vec(5)))
    pf = cleanup(unbind(e, Mf), pp)
    assert pf in (1, 5), pf
    print("[self-test] PASS: P^k separates 2 occurrences (pos1,pos5); FHRR single-unbind returns only pos%s (occurrence-blind)" % pf)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--n", type=int, default=120)
    args = ap.parse_args()
    t0 = time.time()
    if args.self_test:
        _self_test(); sys.exit(0)
    res = run(n_discourse=args.n, verbose=True)
    res["elapsed_s"] = round(time.time() - t0, 2)
    print()
    print("VERDICT:", res["verdict"], "--", res["verdict_msg"])
    if args.smoke:
        Path("metrics.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
        print("[smoke] wrote metrics.json")
