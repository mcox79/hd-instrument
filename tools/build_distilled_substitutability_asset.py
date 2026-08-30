"""Build the STATIC labelled asset for the meaning-channel Route A landing (the #1 substrate gap fix).

Root result (integrated `the_live_meaning_organ_has_no_distributional_channel_to_be_taught_by`,
owner-DONE, EXCELLENT; reverified 4/4 first-hand 2026-08-30): the live meaning organ has no
word-context distributional channel, so it cannot separate synonyms (sofa/couch) from mere associates
(apple/orange) -- both pin at GROUNDED_CAP=0.45. The brain-foundational fix: an OFFLINE PPMI+SVD space
(neocortical consolidation of the reading co-occurrence counts -- CLS) with a grounded-hub-TAUGHT
direction (cross-modal distillation -- the ATL hub shaping each spoke). A pair's substitutability score
is  sign * (phi[a] * phi[b]) @ w  (element-wise product of the two word vectors, projected on the
distilled direction). This CLEARS the substitutability bar at ~0.865 where the dense-bundle incumbent
sits at chance.

This is the "promote to a static labelled asset" HALF of Route A (owner 08-16: a static offline-built
asset is admissible; label kept: PPMI+SVD is offline-built, the grounded teacher is the supplied
Lancaster/Warriner norms). It REUSES the validated distillation cell's functions verbatim (no re-derived
math) and VERIFIES the saved asset reproduces the ~0.865 instrument AUC before writing. The hdlab wiring
(a default-separate distilled channel consulted by grounded_similarity) is the next step; this produces
the asset that step loads. NO external LLM at inference (the asset is static; scoring is a dot product).

Run: .venv/Scripts/python.exe tools/build_distilled_substitutability_asset.py
"""
from __future__ import annotations

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np  # noqa: E402

import experiments.exp_crossmodal_distillation_substitutability_v1 as X  # noqa: E402

OUT_DIR = os.path.join(REPO, "data", "grounded_distilled_substitutability_v1")
ASSET = os.path.join(OUT_DIR, "asset.npz")
EXPECTED_AUC = 0.865      # the reverified positive (solver 0.865; witness reproduced 0.8647)
AUC_TOL = 0.03            # accept build if within tol of the validated number


def build() -> dict:
    print("[build] load_everything() ...", flush=True)
    d = X.load_everything()
    phi = d["phi"]
    words_present = d["words_present"]
    row_idx = d["row_idx"]
    matchedP, matchedS = d["matchedP"], d["matchedS"]
    print("[build] phi=%s  |vocab|=%d  matchedP=%d matchedS=%d"
          % (phi.shape, d["n_vocab"], len(matchedP), len(matchedS)), flush=True)

    hubs = X.build_hubs(words_present, d["freq"])
    grounded_hub, gcov = hubs["GROUNDED"]

    # the instrument pairs whose BOTH words are covered by the store (same construction as the cell's main)
    present = [(w1, w2, p) for (w1, w2, p) in matchedP + matchedS
               if w1 in row_idx and w2 in row_idx]
    i1s = np.array([row_idx[w1] for (w1, w2, _) in present])
    i2s = np.array([row_idx[w2] for (w1, w2, _) in present])
    Xg = phi[i1s] * phi[i2s]
    inst_words = {w for (w1, w2, _) in present for w in (w1, w2)}
    gold_pos = {" ".join((w1, w2)) for (w1, w2, _) in matchedP}

    # distill the direction on arbitrary DISJOINT non-instrument pairs + orient (the validated arm, verbatim)
    r = X.score_arm(phi, Xg, i1s, i2s, grounded_hub, gcov, inst_words, words_present, X.MASTER_SEED + 200)
    w = np.asarray(r["w"], dtype=np.float32)
    sign = float(r["sign"])
    oriented = r["oriented"]

    # VERIFY: the saved (phi, w, sign) reproduces the ~0.865 instrument AUC (positives vs negatives)
    keys = [" ".join((w1, w2)) for (w1, w2, _) in present]
    pos_scores = [oriented[i] for i, k in enumerate(keys) if k in gold_pos]
    neg_scores = [oriented[i] for i, k in enumerate(keys) if k not in gold_pos]
    auc = X.auc_of(pos_scores, neg_scores)
    # independent recompute straight from the saved-asset formula (sign * (phi[a]*phi[b]) @ w)
    recompute = sign * (Xg @ w)
    pos2 = [recompute[i] for i, k in enumerate(keys) if k in gold_pos]
    neg2 = [recompute[i] for i, k in enumerate(keys) if k not in gold_pos]
    auc_recompute = X.auc_of(pos2, neg2)
    print("[verify] instrument AUC (arm oriented) = %.4f | recompute from saved formula = %.4f "
          "(expected ~%.3f)" % (auc, auc_recompute, EXPECTED_AUC), flush=True)
    ok = abs(auc_recompute - EXPECTED_AUC) <= AUC_TOL
    if not ok:
        raise SystemExit("[build] REFUSE to save: recomputed AUC %.4f not within %.3f of the validated "
                         "%.3f -- the asset would not reproduce the fix." % (auc_recompute, AUC_TOL, EXPECTED_AUC))

    # the covered instrument pairs, saved so the witness is SCAFFOLD-FREE (scores them via the hdlab
    # organ off the committed asset alone -- no load_everything / gitignored-cache dependency, which is
    # exactly the bit-rot trap that blocked this fix for a week).
    pos_pairs = np.array([[w1, w2] for (w1, w2, _) in present if " ".join((w1, w2)) in gold_pos], dtype=object)
    neg_pairs = np.array([[w1, w2] for (w1, w2, _) in present if " ".join((w1, w2)) not in gold_pos], dtype=object)

    os.makedirs(OUT_DIR, exist_ok=True)
    np.savez_compressed(
        ASSET,
        phi=phi.astype(np.float32),
        words=np.array(words_present, dtype=object),
        w=w,
        sign=np.float32(sign),
        pos_pairs=pos_pairs, neg_pairs=neg_pairs,
        n_pos=np.int64(len(pos2)), n_neg=np.int64(len(neg2)),
        instrument_auc=np.float32(auc_recompute),
        provenance=np.array(
            "PPMI+SVD offline (SVD_K=%d) over real_cache.npz reading counts; distilled direction over "
            "%d arbitrary DISJOINT non-instrument pairs vs the Lancaster+Warriner grounded hub; sign "
            "oriented by the hub's own (non-gold) ranking; MASTER_SEED=%d. Score(a,b)=sign*(phi[a]*phi[b])@w."
            % (X.SVD_K, X.N_DISTILL_PAIRS, X.MASTER_SEED), dtype=object),
    )
    print("[build] SAVED %s  (phi=%s, |w|=%d, sign=%+d, instrument_auc=%.4f)"
          % (ASSET, phi.shape, len(w), int(sign), auc_recompute), flush=True)
    return {"asset": ASSET, "instrument_auc": float(auc_recompute), "phi_shape": list(phi.shape),
            "n_words": len(words_present)}


if __name__ == "__main__":
    build()
