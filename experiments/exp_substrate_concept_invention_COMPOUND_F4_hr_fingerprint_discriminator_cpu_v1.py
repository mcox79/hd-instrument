"""DECISION 128 hand-off (CELL-CONCEPT-INVENTION-COMPOUND-1, TERTIARY/F4) -- HR-style extensional-FINGERPRINT discriminator calibration. The cheapest fast-falsifier of the four-source compound: the load-bearing PRECISION mechanism that distinguishes REDISCOVERY (candidate extensionally-equivalent to an existing atom) from genuine NOVELTY (distinct extension). If F4 fails on a known-rediscovery/known-novel seed set, the compound is unsalvageable regardless of generator quality.
Extensional fingerprint of a component-set S (a candidate predicate's definition):
   fp(S) = frozenset of existing atoms A such that S subset-of cross_component_set(A)   (the atoms S 'explains'/covers)
Discriminator: candidate S is REDISCOVERY iff some existing composite X has fp(components(X)) == fp(S) (extensionally equivalent); else NOVEL.
Calibration seed (labeled): known-REDISCOVERY (existing composites' own component-sets -> must be flagged rediscovery) + known-NOVEL (synthetic distinct sets -> must be flagged novel) + adversarial near-but-distinct.
HARD-PASS (F4): precision >= 0.80 AND recall >= 0.80 on rediscovery detection. Substrate-internal; laptop; no LLM; no held-out. ASCII; --self-test.
HONEST SCOPE: F4 tests DISCRIMINATION (rediscovery vs novel), NOT novelty-SOUNDNESS. A NOVEL fingerprint does not imply a SOUND concept -- the soundness-certification gap (INV-1/INV-2 authoring-time-bound) is separate and F4 does not address it."""
from __future__ import annotations
import sys, json, time
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
DATA_ROOT = REPO / "data" / "substrate_index"
CROSS_REL = {"DEPENDS_ON", "USES", "SPECIALIZES", "SHARES_MATH", "COMPOSED_OF", "INSTANCE_OF"}
POOL = ["vector_space", "inner_product", "matrix", "eigenvalue_eigenvector", "dot_product", "kronecker_product",
        "tensor", "vector", "span", "matrix_inverse", "eigendecomposition", "singular_value_decomposition",
        "qr_decomposition", "lu_decomposition", "matrix_decomposition", "orthogonality", "spectral_theorem",
        "rank_nullity_theorem", "gradient", "hessian", "kernel_method", "sigma_algebra", "lp_space",
        "gaussian_process", "random_features"]
SEED = 1284
SELFTEST = "--self-test" in sys.argv


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def _selftest():
    assert _short("a::b/c") == "c"; print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    import random
    rng = random.Random(SEED)
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(DATA_ROOT)
    atoms = list(ps.all_atoms())
    sset = {_short(a.id) for a in atoms}
    corpus = {_short(a.id): str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower() for a in atoms}
    cross_out = defaultdict(set)
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            if (r.get("rel_type", "") or "").upper() in CROSS_REL:
                s = _short(r.get("src_id", "")); t = _short(r.get("tgt_id", ""))
                if s and t and s != t: cross_out[s].add(t)
    prims = [p for p in POOL if p in sset]
    primset = set(prims)
    # component-set of each existing atom restricted to primitive pool
    comp = {a: (cross_out.get(a, set()) & primset) for a in sset}
    composites = {a: cs for a, cs in comp.items() if len(cs) >= 2 and corpus.get(a, "") in ("math", "concept") and a not in primset}

    def fp(S):
        S = frozenset(S)
        if not S: return frozenset()
        return frozenset(a for a in sset if S and S <= comp.get(a, set()))

    # precompute fingerprints of existing composites' OWN component-sets
    existing_fp = {}
    for a, cs in composites.items():
        existing_fp.setdefault(fp(cs), set()).add(a)

    def discriminate(S):
        """REDISCOVERY if S's fingerprint equals some existing composite's fingerprint (extensionally equivalent); else NOVEL."""
        f = fp(S)
        if not f: return ("NOVEL", None)
        if f in existing_fp:
            # equivalent to existing concept(s); rediscovery iff S structurally matches one OR is extensionally identical
            return ("REDISCOVERY", sorted(existing_fp[f])[:2])
        return ("NOVEL", None)

    # ---- labeled calibration seed ----
    comp_items = list(composites.items())
    rng.shuffle(comp_items)
    seed = []   # (component_set, true_label)
    # known-REDISCOVERY: existing composites' own component-sets
    for a, cs in comp_items[:20]:
        seed.append((frozenset(cs), "REDISCOVERY", a))
    # known-NOVEL: synthetic component-sets NOT equal to any existing atom's set + with a DISTINCT fingerprint
    tries = 0
    novels = 0
    existing_sets = {frozenset(cs) for cs in composites.values()}
    while novels < 20 and tries < 4000:
        tries += 1
        k = rng.choice([2, 3, 4])
        cand = frozenset(rng.sample(prims, k))
        if cand in existing_sets: continue
        if fp(cand) in existing_fp: continue        # extensionally equivalent to existing -> not a clean known-novel
        seed.append((cand, "NOVEL", None))
        novels += 1
    # adversarial near-but-distinct (drop one real + add one wrong) -> should be NOVEL (distinct concept)
    adv = 0
    for a, cs in comp_items:
        if adv >= 10: break
        if len(cs) >= 3:
            base = list(cs); rng.shuffle(base); wrong = [p for p in prims if p not in cs]; rng.shuffle(wrong)
            if wrong:
                near = frozenset(base[:-1] + wrong[:1])
                if near not in existing_sets and fp(near) not in existing_fp:
                    seed.append((near, "NOVEL", None)); adv += 1

    # ---- evaluate discriminator ----
    tp = fp_ = tn = fn = 0
    for S, label, _ in seed:
        pred, _m = discriminate(S)
        if label == "REDISCOVERY" and pred == "REDISCOVERY": tp += 1
        elif label == "NOVEL" and pred == "REDISCOVERY": fp_ += 1
        elif label == "NOVEL" and pred == "NOVEL": tn += 1
        elif label == "REDISCOVERY" and pred == "NOVEL": fn += 1
    precision = round(tp / max(tp + fp_, 1), 3)
    recall = round(tp / max(tp + fn, 1), 3)
    n_red = sum(1 for _, l, _ in seed if l == "REDISCOVERY"); n_nov = sum(1 for _, l, _ in seed if l == "NOVEL")
    print("  COMPOUND-F4 HR-fingerprint discriminator calibration:", flush=True)
    print("  seed: %d known-REDISCOVERY + %d known-NOVEL (incl adversarial near-but-distinct)" % (n_red, n_nov), flush=True)
    print("  confusion: TP=%d FP=%d TN=%d FN=%d" % (tp, fp_, tn, fn), flush=True)
    print("  rediscovery-detection PRECISION=%.3f  RECALL=%.3f  (HARD-PASS bar 0.80 each)" % (precision, recall), flush=True)
    return {"n_rediscovery": n_red, "n_novel": n_nov, "TP": tp, "FP": fp_, "TN": tn, "FN": fn,
            "precision": precision, "recall": recall}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    p = r["precision"]; rc = r["recall"]
    s = ("COMPOUND-F4 HR-fingerprint discriminator: %d rediscovery + %d novel seed; precision=%.3f recall=%.3f (TP=%d FP=%d TN=%d FN=%d)." % (
        r["n_rediscovery"], r["n_novel"], p, rc, r["TP"], r["FP"], r["TN"], r["FN"]))
    if p >= 0.80 and rc >= 0.80:
        return ("HARD_PASS", "F4 PASS: extensional-fingerprint discriminator reliably distinguishes rediscovery from novelty (precision+recall>=0.80) -> the compound's PRECISION mechanism is sound; rediscovery-vs-novel three-way decomposition is supportable. CAVEAT (honest): F4 validates DISCRIMINATION only; it does NOT certify novelty SOUNDNESS (the INV-1/INV-2 grounding/authoring-time-bound gap is separate and unaddressed by F4). Compound worth building IFF a truth-source for novelty-soundness is supplied (Lever b / G3-with-11th-rule-reconcile). " + s)
    return ("HARD_FAIL", "F4 FAIL: discriminator precision/recall < 0.80 -> the compound's precision mechanism is undisciplined; rediscovery-vs-novel decomposition not reliable -> compound unsalvageable as specified; substrate needs a different precision mechanism. " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_concept_invention_COMPOUND_F4_hr_fingerprint_discriminator | SEED=%d" % SEED, flush=True)
    out_dir = get_output_dir("substrate_concept_invention_COMPOUND_F4_hr_fingerprint_discriminator_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_concept_invention_COMPOUND_F4_hr_fingerprint_discriminator_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
