"""exp_hub_spoke_word_g3_cleanup_rescore_v1 -- AMENDMENT A3 to
preregs/exp_hub_spoke_word_representation_v1.md, section 6b gate G3.

WHY THIS EXISTS
---------------
Gate G3 as pre-registered scores "the structure of the UNBOUND MEANING SPOKE". That measure is
DEGENERATE, and the reason is mathematics rather than a coding slip: binding by a bipolar +-1
key is an ISOMETRY.

    (v_i * k) . (v_j * k) = sum_d v_i[d] v_j[d] k[d]^2 = v_i . v_j        since k[d]^2 = 1

so the unbound vectors have EXACTLY the pairwise cosines the bundle already had, and G3 was
silently scoring the BUNDLED vector under a different name. The defect was found by the SMOKE
gate BEFORE the full run and disclosed rather than patched; this cell is the disclosed fix,
executed as a DATED AMENDMENT (A3) rather than a silent edit of the v1 cell. The v1 cell is
NOT modified: it ran unchanged and its pre-registered gates stand as published.

THE FIX (exactly as specified in the v1 cell docstring, so it is not invented twice)
-----------------------------------------------------------------------------------
Measure row (b) as:  unbind -> CLEAN UP against the spoke's own codebook over the vocabulary
-> score the RECOVERED code. Cleanup is the nonlinear step; it is the only place extra
structure can come from, because the linear step provably cannot supply any.

NO THRESHOLD IS CHANGED. G3's criterion is still "CI-separated above
max(orthographic, hardened FREQ_MIN, scramble) on the IDENTICAL pairs, paired bootstrap over
pairs". The SCRAMBLE floor is routed through the IDENTICAL unbind->cleanup path so it stays a
matched floor; the ORTHOGRAPHIC and FREQ_MIN floors are STANDALONE channels, as a floor must be.

WHAT THE RESCORE CAN AND CANNOT SHOW -- read before quoting any number from it
-----------------------------------------------------------------------------
Cleanup snaps each unbound query to a codebook entry. If cleanup is near-perfect, the recovered
concatenation IS the direct spoke code, so the rescored G3 collapses to "do the 12-dim
sensorimotor norms carry SimLex structure above the floors" -- a question about the ASSET, not
about the bundle. The cell therefore reports, side by side and never averaged:
  - the CEILING   : direct spoke codes, never bundled (what the asset carries at best)
  - the RESCORE   : unbind -> cleanup -> recovered code (what asking the hub actually returns)
  - the DEGENERATE: raw unbound (kept, and re-verified at FULL scale, so the defect is visible)
and two cleanup-fidelity statistics, because identity accuracy is the wrong one for a spoke
whose codebook has few distinct entries:
  - cleanup_identity_acc   : the argmax landed on the word's OWN row
  - cleanup_code_exact_acc : the recovered CODE equals the word's own code bit-for-bit
                             (can be 1.0 while identity accuracy is low, when several words
                             share a code -- CONCRETE is 1 dim lifted by SimHash and therefore
                             has very few distinct codes by construction)

NOT_EVALUABLE is a real outcome and is reported as such if cleanup returns noise.

ASCII-only. CPU. No network. No external LLM. data/foundation/** is never opened.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_encoding_quality_instrument_v2 as INS      # THE RULER -- imported, never edited
import exp_meaning_asset_fair_test_v1 as FT           # floors + paired bootstrap, never edited
import exp_hub_spoke_word_representation_v1 as HS     # the v1 cell -- imported, NEVER edited
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "hub_spoke_word_g3_cleanup_rescore_v1"
CODE_VERSION = "v1.0"
AMENDMENT = "A3 (2026-08-15) to preregs/exp_hub_spoke_word_representation_v1.md section 6b G3"

MEANING_SPOKES = list(HS.MEANING_SPOKES4)      # SENSORY, ACTION, CONCRETE


def cleanup(query: np.ndarray, codebook: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Snap each query row to its nearest codebook row (cosine). Returns (picked_idx, recovered).

    This is the NONLINEAR step the pre-registered row (b) was missing. Chance identity accuracy
    is 1/len(codebook).
    """
    Q = INS._l2n(query)
    C = INS._l2n(codebook)
    rng = np.random.default_rng(INS._hash_seed("cleanup", 0))
    sims = Q @ C.T
    sims = sims + rng.random(sims.shape) * 1e-12          # INS tiebreak convention
    idx = np.argmax(sims, axis=1)
    return idx, codebook[idx]


def rescore_arm(arm: str, d: int, seed: int) -> dict:
    """Build the arm through the v1 cell's OWN build_arm, then read the meaning side three ways."""
    vecs, codec, pool_spokes, used = HS.build_arm(arm, d, seed)
    ms = [s for s in pool_spokes if s in MEANING_SPOKES]
    n = vecs.shape[0]

    raw_blocks: List[np.ndarray] = []
    rec_blocks: List[np.ndarray] = []
    per_spoke: Dict[str, dict] = {}
    for s in ms:
        q = codec.ask_for(vecs, s)                        # the DEGENERATE row (b), unchanged
        raw_blocks.append(q)
        idx, rec = cleanup(q, used[s])                    # the FIX
        rec_blocks.append(rec)
        own = np.arange(n)
        per_spoke[s] = {
            "cleanup_identity_acc": float(np.mean(idx == own)),
            "cleanup_identity_chance": 1.0 / float(n),
            "cleanup_code_exact_acc": float(np.mean(np.all(rec == used[s], axis=1))),
            "n_distinct_codes_in_codebook": int(len(np.unique(used[s], axis=0))),
        }
    raw = np.concatenate(raw_blocks, axis=1)
    rec = np.concatenate(rec_blocks, axis=1)
    direct = np.concatenate([used[s] for s in ms], axis=1)
    return {"arm": arm, "d": d, "seed": seed, "meaning_spokes": ms,
            "bundled": INS._l2n(vecs), "raw_unbound": INS._l2n(raw),
            "cleaned_unbound": INS._l2n(rec), "direct_spoke_codes": INS._l2n(direct),
            "per_spoke_cleanup": per_spoke}


def main() -> int:
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    S = HS.shared()
    w2i = S["w2i"]
    pairs = S["pairs"]
    counts = S["counts"]
    gold = np.array([s for _, _, s in pairs], dtype=np.float64)

    d_head = HS.D_SWEEP[-1] if len(HS.D_SWEEP) > 1 else HS.D_SWEEP[0]
    seed0 = HS.SEEDS[0]

    def percos(X):
        cs, gs, _ = FT.simlex_perpair(X, w2i, pairs)
        return cs

    results = {}
    for d in HS.D_SWEEP:
        for seed in HS.SEEDS:
            key = f"d{d}_seed{seed}"
            hs4 = rescore_arm("HS4_GRADED", d, seed)
            scr = rescore_arm("F_SCRAMBLE", d, seed)
            orth_vecs, _, _, _ = HS.build_arm("F_ORTHO", d, seed)
            orth = INS._l2n(orth_vecs)

            cos_bundled = percos(hs4["bundled"])
            cos_raw = percos(hs4["raw_unbound"])
            cos_clean = percos(hs4["cleaned_unbound"])
            cos_direct = percos(hs4["direct_spoke_codes"])
            cos_scr_clean = percos(scr["cleaned_unbound"])
            cos_scr_raw = percos(scr["raw_unbound"])
            cos_orth = percos(orth)

            lf = np.log(counts + 1.0)
            la = np.array([lf[w2i[a]] for a, _, _ in pairs])
            lb = np.array([lf[w2i[b]] for _, b, _ in pairs])
            freq_min = np.minimum(la, lb)

            floors = {
                "ORTHOGRAPHIC": {"vec": cos_orth, "boot": FT.boot_rho(cos_orth, gold)},
                "HARDENED_FREQ_MIN": {"vec": freq_min, "boot": FT.boot_rho(freq_min, gold)},
                "SCRAMBLE_cleaned": {"vec": cos_scr_clean,
                                     "boot": FT.boot_rho(cos_scr_clean, gold)},
            }
            strongest = max(floors, key=lambda k: floors[k]["boot"]["point"])
            margin = FT.boot_rho_diff(cos_clean, floors[strongest]["vec"], gold)

            # the degeneracy re-verified at THIS scale, not carried over from smoke
            degen = {
                "max_abs_cos_delta_bundled_vs_raw_unbound":
                    float(np.max(np.abs(cos_bundled - cos_raw))),
                "rho_bundled": FT.boot_rho(cos_bundled, gold)["point"],
                "rho_raw_unbound": FT.boot_rho(cos_raw, gold)["point"],
            }

            ident = np.mean([v["cleanup_identity_acc"]
                             for v in hs4["per_spoke_cleanup"].values()])
            exact = np.mean([v["cleanup_code_exact_acc"]
                             for v in hs4["per_spoke_cleanup"].values()])
            chance = np.mean([v["cleanup_identity_chance"]
                              for v in hs4["per_spoke_cleanup"].values()])
            evaluable = bool(exact >= 0.50 or ident > 10.0 * chance)

            results[key] = {
                "d": d, "seed": seed,
                "n_pairs": int(len(gold)),
                "DEGENERACY_recheck_at_this_scale": degen,
                "cleanup_fidelity": {"mean_identity_acc": float(ident),
                                     "mean_identity_chance": float(chance),
                                     "mean_code_exact_acc": float(exact),
                                     "per_spoke": hs4["per_spoke_cleanup"],
                                     "scramble_per_spoke": scr["per_spoke_cleanup"]},
                "rho": {
                    "CEILING_direct_spoke_codes": FT.boot_rho(cos_direct, gold),
                    "RESCORED_unbind_then_cleanup": FT.boot_rho(cos_clean, gold),
                    "DEGENERATE_raw_unbound": FT.boot_rho(cos_raw, gold),
                    "bundled_vector": FT.boot_rho(cos_bundled, gold),
                    "SCRAMBLE_cleaned": FT.boot_rho(cos_scr_clean, gold),
                    "SCRAMBLE_raw_unbound": FT.boot_rho(cos_scr_raw, gold),
                },
                "floors": {k: v["boot"] for k, v in floors.items()},
                "strongest_floor": strongest,
                "margin_over_strongest_floor": margin,
                "band": FT.band(margin["ci95"]),
                "G3_RESCORED_passed": bool(margin["ci95"][0] > 0) if evaluable else None,
                "G3_RESCORED_status": ("PASS" if (evaluable and margin["ci95"][0] > 0)
                                       else ("FAIL" if evaluable else "NOT_EVALUABLE")),
                "evaluable": evaluable,
            }
            print(f"  {key}: rescored rho={results[key]['rho']['RESCORED_unbind_then_cleanup']['point']:.4f} "
                  f"floor({strongest})={floors[strongest]['boot']['point']:.4f} "
                  f"margin={margin['point']:.4f} CI={margin['ci95']} "
                  f"-> {results[key]['G3_RESCORED_status']}", flush=True)

    head = results[f"d{d_head}_seed{seed0}"]
    verdict = "G3_RESCORED_" + head["G3_RESCORED_status"]
    vmsg = (f"AMENDMENT A3. G3 rescored through CLEANUP at d={d_head} seed={seed0}: "
            f"rho={head['rho']['RESCORED_unbind_then_cleanup']['point']:.4f} vs strongest floor "
            f"{head['strongest_floor']}={head['floors'][head['strongest_floor']]['point']:.4f}, "
            f"margin {head['margin_over_strongest_floor']['point']:.4f} "
            f"CI {head['margin_over_strongest_floor']['ci95']} -> {head['band']}. "
            f"Degenerate raw-unbound row re-verified at THIS run's scale (V={len(S['words'])}, "
            f"{len(gold)} pairs): max |cos delta| vs bundled = "
            f"{head['DEGENERACY_recheck_at_this_scale']['max_abs_cos_delta_bundled_vs_raw_unbound']:.3e}. "
            f"NO THRESHOLD CHANGED.")

    # LABEL FIX (2026-08-16, no threshold touched): run_mode was HARDCODED "full", so the
    # smoke metrics on disk at data/exp_hub_spoke_word_g3_cleanup_rescore_v1_smoke/metrics.json
    # are mislabelled "full" while carrying only 26 SimLex pairs. It is derived now.
    metrics = {"anchor_name": ANCHOR_NAME, "code_version": CODE_VERSION,
               "run_mode": HS.RUN_MODE,
               "amendment": AMENDMENT,
               "parent_cell": "experiments/exp_hub_spoke_word_representation_v1.py (UNMODIFIED)",
               "prereg": "preregs/exp_hub_spoke_word_representation_v1.md",
               "verdict": verdict, "verdict_msg": vmsg, "summary": vmsg,
               "d_headline": d_head, "seed_headline": seed0,
               "per_config": results, "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics)
    print(json.dumps({"verdict": verdict, "msg": vmsg}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
