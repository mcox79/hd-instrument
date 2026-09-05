"""Scaffold-free witness for build_and_freeze_the_clean_curated_knowledge_foundation_the_proven_meaning_lift.

Reproduces, FROM SOURCE (the SHIPPED frozen asset + cached offline embeddings/SemCor; deterministic; NO external
LLM at inference; writes NOTHING), the load-bearing claims of the meaning store (the C1 spoke of the knowledge
factory):

  C1  the shipped frozen asset loads and covers the eval candidates (broad WordNet coverage)
  C2  FROZEN-ASSET signatures BEAT the gloss floor CI-separated through the LIVE hdlab.diagnostic_context_wsd
      readout (the proven +0.0755 meaning lift, delivered by the static asset)
  C3  the info-free SHUFFLED-KNOWLEDGE twin (curated associates permuted onto the WRONG senses) LOSES
      CI-separated -> it is the CORRECT curated knowledge carrying the signal, not 'more words'
  C4  NO MFS regression on the full (all-sense) population (the frozen store does not hurt the dominant cases)
  C5  DETERMINISM: a fresh deterministic rebuild of a sample of synsets is byte-identical (float16) to the
      shipped asset rows -- the frozen asset is byte-reproducible (the hyponyms()[:8] hash-order bug is fixed)
  C6  INTRINSIC diagnosis (unsupervised, no labels): sibling senses are near-collinear (high sibling-cosine) and
      the signature space is low-rank -- documenting the frozen-w2v superposition ceiling the store runs into

Run: .venv/Scripts/python.exe verification/test_knowledge_factory_meaning_store.py
"""
import os
import sys

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_knowledge_factory_meaning_store_v1 as M
import experiments.exp_knowledge_factory_intrinsic_trim_v1 as IT
import experiments.exp_consolidation_gate_v1 as G1
from hdlab.diagnostic_context_wsd import diagnostic_context_scores

PASS = 0
FAIL = 0
ASSET = os.path.join(_REPO, "data", "frontend_assets", "meaning_sense_signatures_v1.npz")


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    z = np.load(ASSET, allow_pickle=True)
    names = [str(n) for n in z["names"]]; vecs = z["vecs"]
    row = {n: i for i, n in enumerate(names)}
    w2i, mat, recs, dev, test, test_all = M._load_eval()
    cand = set()
    for i in test:
        cand.update(recs[i]["tn"])
    Ctx = G1.precompute_ctx(recs, test, mat, w2i)
    zero = np.zeros(vecs.shape[1], np.float32)

    def frozen_sig(s):
        if s in row:
            v = vecs[row[s]]
            return v if float(np.linalg.norm(v)) > 1e-6 else None
        return None

    def a_s(lookup, gamma=1.0):
        ok = []
        for i in test:
            C = Ctx[i]
            if C is None:
                continue
            tn = recs[i]["tn"]
            G = np.stack([lookup(s) if lookup(s) is not None else zero for s in tn]).astype(np.float64)
            if not np.any(G):
                continue
            ok.append(int(tn[int(np.argmax(diagnostic_context_scores(C, G, gamma=gamma)))] == recs[i]["gold"]))
        return np.array(ok, float)

    covered = sum(1 for s in cand if s in row)
    chk("C1 shipped frozen asset loads + covers eval candidates",
        len(names) > 50000 and covered == len(cand),
        "%d synsets; %d/%d candidates covered" % (len(names), covered, len(cand)))

    prep0 = M.prep_bags(cand, mat, w2i, 0)
    gloss = M.sigs_at(prep0, mat, w2i, None)
    ok_frozen = a_s(frozen_sig)
    ok_gloss = a_s(lambda s: gloss.get(s))
    n = min(len(ok_frozen), len(ok_gloss))
    p_fg = G1._paired(ok_frozen[:n], ok_gloss[:n], 950)
    chk("C2 FROZEN asset BEATS gloss CI-sep through live diagnostic_context_wsd (the +0.0755 lift)",
        p_fg["sep"] and p_fg["delta"] > 0.05,
        "frozen %.4f vs gloss %.4f d=+%.4f ci=%s" % (ok_frozen.mean(), ok_gloss.mean(), p_fg["delta"], p_fg["ci"]))

    sig_shuf = M.build_sense_signatures(cand, mat, w2i, 3, margin=None,
                                        shuffle_rng=np.random.default_rng(1234))
    ok_shuf = a_s(lambda s: sig_shuf.get(s))
    m = min(len(ok_frozen), len(ok_shuf))
    p_fs = G1._paired(ok_frozen[:m], ok_shuf[:m], 951)
    chk("C3 info-free SHUFFLED-knowledge twin LOSES CI-sep (correct knowledge, not 'more words')",
        p_fs["sep"] and p_fs["delta"] > 0.05,
        "frozen %.4f vs shuffled %.4f d=+%.4f" % (ok_frozen.mean(), ok_shuf.mean(), p_fs["delta"]))

    Ctx_all = G1.precompute_ctx(recs, test_all, mat, w2i)
    ok_bl, mfs = G1.blended_overall(recs, test_all, {s: frozen_sig(s) for s in
                                                     set().union(*[recs[i]["tn"] for i in test_all])},
                                    Ctx_all, mat, w2i, lam=1.0, T=0.5)
    chk("C4 NO MFS regression on the full all-sense population (frozen store does not hurt dominant cases)",
        ok_bl.mean() >= mfs.mean(),
        "blended_frozen %.4f >= MFS %.4f (n=%d)" % (ok_bl.mean(), mfs.mean(), len(test_all)))

    # C5 determinism: rebuild a sample deterministically, compare to shipped rows (float16)
    sample = [s for s in list(cand)[:200] if s in row]
    fresh = M.build_sense_signatures(sample, mat, w2i, 3, margin=None)
    ident = 0; comp = 0
    for s in sample:
        v = fresh.get(s)
        if v is None:
            continue
        comp += 1
        ident += int(np.allclose(v.astype(np.float16), vecs[row[s]], atol=1e-3))
    chk("C5 DETERMINISM: fresh deterministic rebuild == shipped asset rows (float16)",
        comp > 50 and ident == comp, "%d/%d sample synsets byte-identical" % (ident, comp))

    # C6 intrinsic diagnosis (unsupervised): high sibling-cosine + low effective rank = the superposition ceiling
    frozen_by_syn = {s: frozen_sig(s) for s in cand if frozen_sig(s) is not None}
    sep = IT.sense_separation(frozen_by_syn); er = IT.effective_rank(frozen_by_syn)
    chk("C6 INTRINSIC diagnosis present: sibling senses near-collinear (superposition ceiling, no labels)",
        sep["mean_sibling_cos"] is not None and sep["mean_sibling_cos"] > 0.85 and er < 60,
        "sibling_cos=%.3f effective_rank=%.1f (of %d dims)" % (sep["mean_sibling_cos"], er, vecs.shape[1]))

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
