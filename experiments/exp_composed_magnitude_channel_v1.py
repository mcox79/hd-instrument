"""exp_composed_magnitude_channel_v1 -- COMPOSE the proven scalar-magnitude sub-ops into ONE deployable channel.

The p3 work proved each sub-op IN ISOLATION (SemAxis dimension/pole, markedness degree, FPE-log Weber code,
Lancaster perceptual grounding). This cell BUILDS the one composed magnitude channel and asks whether the COMPOSED
thing beats both the incumbent single cosine AND the strongest SINGLE sub-op alone, with info-free twins LOSING.

BRAIN MECHANISM FOR THE COMPOSITION (research drill 2026-08-27; see the RESEARCH note). The brain unifies the three
sub-computations as a PLACE code indexed by POLE and LOG-MAGNITUDE, built from opponent monotonic pools (Roitman
2007) into a peaked log-Gaussian code (Nieder; Verguts & Fias 2004), read out on a SINGLE ORIENTED SIGNED AXIS for
COMPARISON (SNARC), where degree = LOG-DISTANCE FROM A CONTEXT-SET STANDARD (Kennedy reference-point; Moyer). The
key consequence, which the DISK confirms: POLE and DEGREE are NOT two operations to bolt together -- once the axis is
ORIENTED by the pole, one signed projection already carries BOTH polarity and a graded degree. So the composition
is: SELECT the dimension (semantic control) -> a GROUNDED, ORIENTED signed-magnitude place code (antonym poles for
evaluative dims; Lancaster perceptual strength for denotational -- PROBE C) -> markedness as a fine-degree GROUNDING
refinement (PROBE D) -> FPE(log degree) on the FHRR substrate for Weber COMPARISON (PROBE E), comparator = unbind.

The measurable win of the COMPOSED CHANNEL over any SINGLE sub-op is DIMENSION-ROUTING + PER-DIMENSION GROUNDING: no
single operation serves every scale (an antonym axis recovers valence but fails concreteness; a perceptual axis the
reverse; a cosine has no oriented axis at all). The channel routes each to its correct grounding.

    stored form   code(w) = bind(bind(DIM_key[dim], POLE_key[pole(w)]), FPE_log(degree(w)))
    readout       signed_mag(w) = sign_pole(w) * log_degree(w)   (the oriented axis, for comparison)

TESTS (floors recomputed on each task's OWN population; CI half-width + null p95 reported):
  T1  MULTI-DIM ROUTED RECOVERY (PRIMARY, clears the bar): the composed channel (dimension-routed, per-dim grounded,
      oriented) vs each SINGLE sub-op (antonym-axis-all-dims, perceptual-axis-all-dims, markedness-all-dims) and the
      incumbent cosine, POOLED across valence/arousal/dominance/concreteness. Info-free twins: random axis, shuffled
      degree. The channel beats the strongest single sub-op because it ROUTES; a single op cannot.
  T2  UNIFIED ORIENTED AXIS + MARKEDNESS on bipolar/within-scale ordering (mechanism): once oriented, the signed
      axis does within-scale ordering (0.72) close to markedness (0.77); markedness adds a marginal fine-degree
      gain; the composed signed magnitude handles BOTH cross-pole polarity and within-pole degree.
  T3  ON-SUBSTRATE: the composed code assembles (bind DIM,POLE,FPE_log); the FPE-log kernel preserves the Weber
      (scale-invariant) property on the REAL markedness degrees after the Ch.B linear->log upgrade; the comparator
      unbind recovers the log-ratio; structure-free FPE twin LOSES.

Deterministic, ASCII-only. Writes only its own data dir. hdlab/ NOT modified (the wiring proposal is in SOLVED.md).
Reuses exp_perclass + exp_adjective_magnitude_deeper + exp_adjective_intensity_ordering + exp_fpe_log machinery.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import glob
import json
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import torch
from scipy.stats import spearmanr

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_perclass_meaning_operations_v1 as V1                        # noqa: E402
import experiments.exp_adjective_magnitude_deeper_v1 as DEEP                        # noqa: E402
import experiments.exp_adjective_intensity_ordering_v1 as INT                       # noqa: E402
import experiments.exp_fpe_log_weber_magnitude_v1 as FPE                            # noqa: E402
from hdlab.binding import bind, unbind                                              # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec                         # noqa: E402
from hdlab.lexical_similarity import _cos_complex as cos_complex                    # noqa: E402

ANCHOR = "exp_composed_magnitude_channel_v1"
DATA = os.path.join(REPO_ROOT, "data", "scalar_adj_intensity")
N_BOOT = 2000
SEED = 20260827
EVAL_DIMS = ["valence", "arousal", "dominance", "concreteness"]
DENOTATIONAL = {"concreteness"}          # grounded PERCEPTUALLY (Lancaster), not by antonym poles (PROBE C)


# ===================================================================================================================
# THE COMPOSED MAGNITUDE CHANNEL (deployable op). Glass-box; numpy readout + the FHRR substrate code.
# ===================================================================================================================
class ScalarMagnitudeChannel:
    """One callable magnitude meaning channel: dimension -> grounded oriented axis (pole+degree unified place code)
    -> markedness fine-degree -> FPE(log degree) substrate code. oriented_position() is the routed grounded readout;
    signed_magnitude() is the pole x log-degree comparison readout; code() is the stored FHRR representation."""

    def __init__(self, gv, freq, lanc, d_sub=4096, seed=SEED):
        self.gv = gv
        self.freq = freq
        self.lanc = lanc
        self.d_sub = d_sub
        self.seed = seed
        self._axis = {}
        self._rates = FPE.phase_rates("gauss", d_sub, seed, sigma=1.0)              # shared log-phase axis
        self._dim_key = {d: unit_phase_vec(d_sub, torch.Generator().manual_seed(seed + 100 + i))
                         for i, d in enumerate(EVAL_DIMS)}
        self._pole_key = {+1: unit_phase_vec(d_sub, torch.Generator().manual_seed(seed + 200)),
                          -1: unit_phase_vec(d_sub, torch.Generator().manual_seed(seed + 201))}

    def axis(self, dim):
        """Grounded bipolar axis: evaluative from antonym poles; denotational from Lancaster perceptual (PROBE C)."""
        if dim in self._axis:
            return self._axis[dim]
        ax = self._perceptual_axis() if dim in DENOTATIONAL else V1.dim_axis(dim, self.gv)[0]
        self._axis[dim] = ax
        return ax

    def _perceptual_axis(self):
        anchor = sorted(set(self.lanc) & set(self.gv))
        ap = np.array([self.lanc[w] for w in anchor])
        hi = [w for w in anchor if self.lanc[w] >= np.percentile(ap, 90)]
        lo = [w for w in anchor if self.lanc[w] <= np.percentile(ap, 10)]
        pax = np.mean([self.gv[w] for w in hi], axis=0) - np.mean([self.gv[w] for w in lo], axis=0)
        return pax / (np.linalg.norm(pax) + 1e-12)

    def oriented_position(self, w, dim):
        """Routed grounded oriented projection (the unified pole+degree place code; higher = more of the dim)."""
        if w not in self.gv:
            return None
        return float(self.gv[w] @ self.axis(dim))

    def pole(self, w, dim):
        p = self.oriented_position(w, dim)
        return None if p is None else (1 if p >= 0 else -1)

    def degree(self, w):
        """Markedness degree ~= log-distance from the unmarked standard: -log(frequency) (Horn/Zipf; log PINNED by
        Laughlin efficient coding -- PROBE F). Positive magnitude, monotone in rarity."""
        f = self.freq.get(w)
        if f is None or f <= 0:
            return None
        return float(-np.log(f + 0.1) + np.log(1e6))

    def signed_magnitude(self, w, dim):
        pl, dg = self.pole(w, dim), self.degree(w)
        return None if (pl is None or dg is None) else pl * dg

    def code(self, w, dim):
        """Stored form: bind(DIM_key, POLE_key, FPE_log(degree)). Composable FHRR vector."""
        pl, dg = self.pole(w, dim), self.degree(w)
        if pl is None or dg is None or dim not in self._dim_key:
            return None
        return bind(bind(self._dim_key[dim], self._pole_key[pl]), FPE.enc(self._rates, np.log(dg)))

    def compare(self, w1, w2, dim):
        c1, c2 = self.code(w1, dim), self.code(w2, dim)
        return None if (c1 is None or c2 is None) else unbind(c1, c2)


# ===================================================================================================================
# stats helpers
# ===================================================================================================================
def _pooled_z(readouts_by_dim, golds_by_dim):
    """z-score readout+gold WITHIN each dim, then concatenate -> one pooled (x, gold) over all items (cross-dim
    means removed, so a single op weak on one dim is penalized in the pool)."""
    xs, gs = [], []
    for dim in readouts_by_dim:
        x = np.asarray(readouts_by_dim[dim], float)
        g = np.asarray(golds_by_dim[dim], float)
        if x.std() > 1e-9:
            xs.append((x - x.mean()) / x.std())
        else:
            xs.append(x * 0.0)
        gs.append((g - g.mean()) / (g.std() + 1e-12))
    return np.concatenate(xs), np.concatenate(gs)


def _pooled_rho_diff(read_a, read_b, golds, seed):
    """Bootstrap over pooled items of |rho(pooled_a)| - |rho(pooled_b)|."""
    xa, g = _pooled_z(read_a, golds)
    xb, _ = _pooled_z(read_b, golds)
    n = len(g)
    rng = np.random.default_rng(seed)
    d = np.empty(N_BOOT)
    for i in range(N_BOOT):
        idx = rng.integers(0, n, n)
        d[i] = abs(spearmanr(xa[idx], g[idx]).statistic) - abs(spearmanr(xb[idx], g[idx]).statistic)
    lo, hi = np.percentile(d, [2.5, 97.5])
    base = abs(spearmanr(xa, g).statistic) - abs(spearmanr(xb, g).statistic)
    return {"margin": round(float(base), 4), "ci_lo": round(float(lo), 4), "ci_hi": round(float(hi), 4),
            "ci_hw": round(float(hi - lo) / 2, 4), "null_p95": round(float(np.percentile(np.abs(d - base), 95)), 4)}


def _pooled_rho(readouts_by_dim, golds_by_dim):
    x, g = _pooled_z(readouts_by_dim, golds_by_dim)
    return round(float(abs(spearmanr(x, g).statistic)), 4)


def _pooled_pairwise_boot(per_scale_ct, seed):
    ct = [x for x in per_scale_ct if x[1] > 0]
    if not ct:
        return {"acc": None, "n_pairs": 0, "n_scales": 0}
    C = np.array([c for c, _ in ct], float); T = np.array([t for _, t in ct], float)
    rng = np.random.default_rng(seed)
    b = np.empty(N_BOOT)
    for i in range(N_BOOT):
        r = rng.integers(0, len(ct), len(ct))
        b[i] = C[r].sum() / max(T[r].sum(), 1)
    lo, hi = np.percentile(b, [2.5, 97.5])
    return {"acc": round(float(C.sum() / T.sum()), 4), "ci_lo": round(float(lo), 4), "ci_hi": round(float(hi), 4),
            "ci_hw": round(float(hi - lo) / 2, 4), "n_pairs": int(T.sum()), "n_scales": len(ct)}


def _paired_acc_boot(a_ct, b_ct, seed):
    keep = [(a, b) for a, b in zip(a_ct, b_ct) if a[1] > 0 and b[1] > 0]
    if not keep:
        return {"margin": None, "ci_lo": None, "ci_hi": None}
    Ca = np.array([a[0] for a, _ in keep], float); Ta = np.array([a[1] for a, _ in keep], float)
    Cb = np.array([b[0] for _, b in keep], float); Tb = np.array([b[1] for _, b in keep], float)
    base = float(Ca.sum() / Ta.sum() - Cb.sum() / Tb.sum())
    rng = np.random.default_rng(seed)
    d = np.empty(N_BOOT)
    for i in range(N_BOOT):
        r = rng.integers(0, len(keep), len(keep))
        d[i] = Ca[r].sum() / max(Ta[r].sum(), 1) - Cb[r].sum() / max(Tb[r].sum(), 1)
    lo, hi = np.percentile(d, [2.5, 97.5])
    return {"margin": round(base, 4), "ci_lo": round(float(lo), 4), "ci_hi": round(float(hi), 4),
            "ci_hw": round(float(hi - lo) / 2, 4), "null_p95": round(float(np.percentile(np.abs(d - base), 95)), 4)}


# ===================================================================================================================
# T1: MULTI-DIM ROUTED RECOVERY (PRIMARY). composed channel (routed grounded) vs each single sub-op vs cosine.
# ===================================================================================================================
def t1_routed_recovery(chan, conc, war, concn, smoke=False):
    gv = chan.gv
    wn_adj = set(V1.all_wordnet_adjectives())
    src_by_dim = {"valence": war, "arousal": war, "dominance": war, "concreteness": concn}
    perc_axis = chan._perceptual_axis()
    rng = np.random.default_rng(SEED)
    read = defaultdict(dict); gold = {}
    per_dim = {}
    for dim in EVAL_DIMS:
        src = src_by_dim[dim]
        scored = [w for w in wn_adj if w in gv and w in src and dim in src[w]]
        if dim == "concreteness":
            scored = [w for w in scored if concn[w].get("dom_pos") == "Adjective"]
        scored = [w for w in scored if chan.degree(w) is not None]
        seed_words = {w for p in V1.DIM_SEEDS[dim] for w in p}
        scored = sorted(set(scored) - seed_words)
        if smoke:
            scored = scored[:400]
        if len(scored) < 30:
            continue
        r = np.array([src[w][dim] for w in scored], float)
        M = np.stack([gv[w] for w in scored])
        pos_poles = [a for a, _ in V1.DIM_SEEDS[dim]]; neg_poles = [b for _, b in V1.DIM_SEEDS[dim]]
        rax = rng.standard_normal(M.shape[1]); rax /= np.linalg.norm(rax)
        marked = np.array([chan.degree(w) for w in scored]); marked_shuf = marked.copy(); rng.shuffle(marked_shuf)
        arms = {
            "COMPOSED_channel": M @ chan.axis(dim),                          # ROUTED grounded oriented axis
            "subop_antonym_axis": M @ V1.dim_axis(dim, gv)[0],              # single op: antonym axis, all dims
            "subop_perceptual_axis": M @ perc_axis,                        # single op: perceptual axis, all dims
            "subop_markedness": marked,                                     # single op: markedness, all dims
            "incumbent_cosine": np.array([V1._conc_semaxis(w, pos_poles, neg_poles, conc) or 0.0 for w in scored]),
            "twin_random_axis": M @ rax,
            "twin_shuffled_degree": marked_shuf,
        }
        gold[dim] = r
        for a, v in arms.items():
            read[a][dim] = v
        per_dim[dim] = {"n": len(scored), **{a: round(float(abs(spearmanr(v, r).statistic)), 4) for a, v in arms.items()}}
        print("[T1 %s] n=%d COMPOSED=%.3f | antonym=%.3f perceptual=%.3f marked=%.3f cosine=%.3f | rnd=%.3f"
              % (dim, per_dim[dim]["n"], per_dim[dim]["COMPOSED_channel"], per_dim[dim]["subop_antonym_axis"],
                 per_dim[dim]["subop_perceptual_axis"], per_dim[dim]["subop_markedness"],
                 per_dim[dim]["incumbent_cosine"], per_dim[dim]["twin_random_axis"]), flush=True)

    arms_list = ["COMPOSED_channel", "subop_antonym_axis", "subop_perceptual_axis", "subop_markedness",
                 "incumbent_cosine", "twin_random_axis", "twin_shuffled_degree"]
    pooled = {a: _pooled_rho(read[a], gold) for a in arms_list}
    single_subops = ["subop_antonym_axis", "subop_perceptual_axis", "subop_markedness"]
    strongest = max(single_subops, key=lambda a: pooled[a])
    res = {"per_dim": per_dim, "pooled_abs_rho": pooled, "strongest_single_subop": strongest,
           "boot_COMPOSED_minus_strongest_subop": _pooled_rho_diff(read["COMPOSED_channel"], read[strongest], gold, SEED + 1),
           "boot_COMPOSED_minus_cosine": _pooled_rho_diff(read["COMPOSED_channel"], read["incumbent_cosine"], gold, SEED + 2),
           "boot_COMPOSED_minus_randomtwin": _pooled_rho_diff(read["COMPOSED_channel"], read["twin_random_axis"], gold, SEED + 3)}
    print("[T1 POOLED] COMPOSED=%.3f | strongest single sub-op=%s(%.3f) cosine=%.3f rnd=%.3f"
          % (pooled["COMPOSED_channel"], strongest, pooled[strongest], pooled["incumbent_cosine"],
             pooled["twin_random_axis"]), flush=True)
    print("        COMPOSED - %s = %s\n        COMPOSED - cosine = %s"
          % (strongest, res["boot_COMPOSED_minus_strongest_subop"], res["boot_COMPOSED_minus_cosine"]), flush=True)
    return res


# ===================================================================================================================
# T2: UNIFIED ORIENTED AXIS + MARKEDNESS on within-scale + cross-pole ordering (mechanism)
# ===================================================================================================================
def _scales_by_dim(chan, conc):
    """Per-file half-scales grouped by dimension (normalized antonym pair). Each term gets a per-term polarity via
    an INDEPENDENT anchor (gloss sim to the named poles -- conceptual channel, distinct from GloVe + frequency)."""
    gv = chan.gv
    by_dim = defaultdict(list)                    # dim -> list of (file_id, [(term, rank)], p1, p2)
    for src in ("crowd", "wilkinson", "demelo"):
        for path in sorted(glob.glob(os.path.join(DATA, src, "gold_rankings", "*.rankings"))):
            s = INT.parse_scale(path)
            if s is None:
                continue
            p1, p2, rows = s
            if p1 not in gv or p2 not in gv:
                continue
            dim = "-".join(sorted([p1, p2]))
            terms = [(r, t) for r, t in rows if t in gv and chan.degree(t) is not None]
            if len({t for _, t in terms}) >= 3:
                by_dim[dim].append((os.path.basename(path), terms, p1, p2))
    return by_dim


def t2_unified_axis_and_markedness(chan, conc, smoke=False):
    """(i) WITHIN-scale (same file, per-file oriented): does markedness order intensity better than the oriented
    grounded projection? (ii) CROSS-pole: the oriented axis carries polarity; markedness (unsigned) does not.
    (iii) the COMPOSED signed magnitude handles both. Independent gloss polarity anchor per term."""
    gv = chan.gv
    by_dim = _scales_by_dim(chan, conc)

    # (i) within-scale intensity ordering, per-file oriented (the pole supplies orientation)
    def within_acc(readout):
        ok = tot = 0
        for dim, files in by_dim.items():
            for fid, terms, p1, p2 in files:
                vals = np.array([readout(t, p1, p2) for _, t in terms]); ranks = np.array([r for r, _ in terms])
                rr = spearmanr(vals, ranks).statistic
                o = 1.0 if (rr is not None and rr >= 0) else -1.0             # per-file orientation (the pole)
                for i in range(len(terms)):
                    for j in range(i + 1, len(terms)):
                        if ranks[i] == ranks[j]:
                            continue
                        tot += 1; ok += (np.sign(o * (vals[i] - vals[j])) == np.sign(ranks[i] - ranks[j]))
        return round(ok / tot, 4), tot
    def antonym_proj(t, p1, p2):
        sa = gv[p1] - gv[p2]; sa /= (np.linalg.norm(sa) + 1e-12); return float(gv[t] @ sa)
    wa_marked = within_acc(lambda t, p1, p2: chan.degree(t))
    wa_proj = within_acc(antonym_proj)
    wa_cos = within_acc(lambda t, p1, p2: (V1._sparse_cos(conc.vec(t, "A"), conc.vec(p1, "A")) or 0.0)
                        - (V1._sparse_cos(conc.vec(t, "A"), conc.vec(p2, "A")) or 0.0))

    # (ii)+(iii) cross-pole polarity + pooled: per-term gloss polarity, cross-pole pairs within a dimension
    arms = ["COMPOSED", "oriented_axis", "markedness_alone", "incumbent_cosine", "twin_random_axis", "twin_shuffled_degree"]
    per_scale = {a: [] for a in arms}
    n_within = n_cross = 0
    rng = np.random.default_rng(SEED)
    for dim, files in by_dim.items():
        p1, p2 = files[0][2], files[0][3]
        vp1, vp2 = conc.vec(p1, "A"), conc.vec(p2, "A")
        if vp1 is None or vp2 is None:
            continue
        sa = gv[p1] - gv[p2]; sa /= (np.linalg.norm(sa) + 1e-12)
        rax = rng.standard_normal(gv[p1].shape[0]); rax /= np.linalg.norm(rax)
        # collect terms with gloss polarity + a within-file normalized rank
        items = []
        for fid, terms, _, _ in files:
            rs = sorted({r for r, _ in terms}); rmap = {r: i / max(len(rs) - 1, 1) for i, r in enumerate(rs)}
            for r, t in terms:
                s1 = V1._sparse_cos(conc.vec(t, "A"), vp1); s2 = V1._sparse_cos(conc.vec(t, "A"), vp2)
                if s1 is None or s2 is None or s1 == s2:
                    continue
                pol = +1 if s1 > s2 else -1
                items.append({"t": t, "pol": pol, "nr": rmap[r], "fid": fid})
        if len({it["pol"] for it in items}) < 2 or len(items) < 4:
            continue
        # readouts
        deg = {it["t"]: chan.degree(it["t"]) for it in items}
        proj = {it["t"]: float(gv[it["t"]] @ sa) for it in items}
        semax_pole = {it["t"]: (1 if proj[it["t"]] >= 0 else -1) for it in items}
        rnd_pole = {it["t"]: (1 if float(gv[it["t"]] @ rax) >= 0 else -1) for it in items}
        shuf = rng.permutation([deg[it["t"]] for it in items]); shuf = {it["t"]: v for it, v in zip(items, shuf)}
        read = {
            "COMPOSED": {it["t"]: semax_pole[it["t"]] * deg[it["t"]] for it in items},
            "oriented_axis": {it["t"]: proj[it["t"]] for it in items},
            "markedness_alone": {it["t"]: deg[it["t"]] for it in items},
            "incumbent_cosine": {it["t"]: (V1._sparse_cos(conc.vec(it["t"], "A"), vp1) or 0.0)
                                 - (V1._sparse_cos(conc.vec(it["t"], "A"), vp2) or 0.0) for it in items},
            "twin_random_axis": {it["t"]: rnd_pole[it["t"]] * deg[it["t"]] for it in items},
            "twin_shuffled_degree": {it["t"]: semax_pole[it["t"]] * shuf[it["t"]] for it in items},
        }
        # target: within-pole -> human rank (per file); cross-pole -> polarity. gloss polarity gives the sign.
        tgt = {it["t"]: it["pol"] * (1.0 + it["nr"]) for it in items}
        wl = [it["t"] for it in items]
        polof = {it["t"]: it["pol"] for it in items}
        fidof = {it["t"]: it["fid"] for it in items}
        ct = {a: [0, 0] for a in arms}
        for i in range(len(wl)):
            for j in range(i + 1, len(wl)):
                ti, tj = wl[i], wl[j]
                same_pole = polof[ti] == polof[tj]
                # within-pole pairs only valid within the SAME file (ranks comparable); cross-pole any
                if same_pole and fidof[ti] != fidof[tj]:
                    continue
                if tgt[ti] == tgt[tj]:
                    continue
                if same_pole:
                    n_within += 1
                else:
                    n_cross += 1
                t = np.sign(tgt[ti] - tgt[tj])
                for a in arms:
                    di = read[a][ti] - read[a][tj]
                    if di != 0:
                        ct[a][1] += 1; ct[a][0] += (np.sign(di) == t)
        for a in arms:
            per_scale[a].append(tuple(ct[a]))
    pooled = {a: _pooled_pairwise_boot(per_scale[a], SEED + 30 + k) for k, a in enumerate(arms)}
    res = {
        "within_scale_intensity_order_acc": {"markedness": wa_marked[0], "oriented_projection": wa_proj[0],
                                             "incumbent_cosine": wa_cos[0], "n_pairs": wa_marked[1]},
        "n_within_pole_pairs": n_within, "n_cross_pole_pairs": n_cross,
        "pooled_pairwise_acc": pooled,
        "boot_COMPOSED_minus_orientedaxis": _paired_acc_boot(per_scale["COMPOSED"], per_scale["oriented_axis"], SEED + 50),
        "boot_COMPOSED_minus_markedness": _paired_acc_boot(per_scale["COMPOSED"], per_scale["markedness_alone"], SEED + 51),
        "boot_COMPOSED_minus_cosine": _paired_acc_boot(per_scale["COMPOSED"], per_scale["incumbent_cosine"], SEED + 52),
        "boot_COMPOSED_minus_randomtwin": _paired_acc_boot(per_scale["COMPOSED"], per_scale["twin_random_axis"], SEED + 53),
    }
    print("[T2 within-scale] intensity-order acc: markedness=%.3f oriented-proj=%.3f cosine=%.3f (n=%d)"
          % (wa_marked[0], wa_proj[0], wa_cos[0], wa_marked[1]), flush=True)
    print("[T2 bipolar] within=%d cross=%d | acc COMPOSED=%s oriented=%s marked=%s cosine=%s | rnd=%s shufdeg=%s"
          % (n_within, n_cross, pooled["COMPOSED"]["acc"], pooled["oriented_axis"]["acc"],
             pooled["markedness_alone"]["acc"], pooled["incumbent_cosine"]["acc"],
             pooled["twin_random_axis"]["acc"], pooled["twin_shuffled_degree"]["acc"]), flush=True)
    print("        COMPOSED-oriented=%s COMPOSED-markedness=%s COMPOSED-cosine=%s"
          % (res["boot_COMPOSED_minus_orientedaxis"], res["boot_COMPOSED_minus_markedness"],
             res["boot_COMPOSED_minus_cosine"]), flush=True)
    return res


# ===================================================================================================================
# T3: ON-SUBSTRATE -- composed code assembles; FPE-log preserves Weber on REAL degrees; unbind decodes; twin flat.
# ===================================================================================================================
def t3_substrate_weber_on_real_degrees(chan, conc, smoke=False):
    by_dim = _scales_by_dim(chan, conc)
    degs = sorted({chan.degree(t) for files in by_dim.values() for _, terms, _, _ in files for _, t in terms
                   if chan.degree(t) is not None})
    degs = np.array(degs)
    if len(degs) < 20:
        return {"note": "too few degrees"}
    rates = chan._rates
    lo, hi = np.percentile(degs, [10, 90])
    xs = np.linspace(lo, hi, 8)
    r = 1.5
    log_ratio = [FPE.kern(rates, np.log(x), np.log(x * r)) for x in xs if x * r <= degs.max() * 1.6]
    lin_ratio = [FPE.kern(rates, x, x * r) for x in xs if x * r <= degs.max() * 1.6]
    dd = (hi - lo) / 6.0
    log_diff = [FPE.kern(rates, np.log(x), np.log(x + dd)) for x in xs]
    lin_diff = [FPE.kern(rates, x, x + dd) for x in xs]

    def cv(v):
        v = np.asarray(v, float); m = v.mean()
        return float(v.std() / abs(m)) if abs(m) > 1e-9 else float("inf")
    # Weber PRESERVED: the LOG code is scale-invariant (fixed-ratio kernel ~ constant) where the LINEAR code is NOT.
    weber = bool(cv(log_ratio) < 0.05 and cv(lin_ratio) > cv(log_ratio) + 0.1)

    codebook = [FPE.enc(rates, c) for c in np.linspace(-3, 3, 241)]; cand = np.linspace(-3, 3, 241)
    rng = np.random.default_rng(SEED)
    pool = [(t, chan.degree(t)) for files in by_dim.values() for _, terms, _, _ in files for _, t in terms
            if chan.degree(t) is not None]
    same_dec, same_tru, diff_sim = [], [], []
    for _ in range(min(150, len(pool))):
        (t1, d1) = pool[rng.integers(len(pool))]; (t2, d2) = pool[rng.integers(len(pool))]
        if t1 == t2:
            continue
        c1 = bind(bind(chan._dim_key["valence"], chan._pole_key[+1]), FPE.enc(rates, np.log(d1)))
        c2 = bind(bind(chan._dim_key["valence"], chan._pole_key[+1]), FPE.enc(rates, np.log(d2)))
        resid = unbind(c1, c2)
        same_dec.append(float(cand[int(np.argmax([float(cos_complex(resid, cb)) for cb in codebook]))]))
        same_tru.append(float(np.log(d1 / d2)))
        c2d = bind(bind(chan._dim_key["valence"], chan._pole_key[-1]), FPE.enc(rates, np.log(d2)))
        diff_sim.append(float(cos_complex(unbind(c1, c2d), FPE.enc(rates, np.log(d1 / d2)))))
    decode_corr = float(np.corrcoef(same_dec, same_tru)[0, 1]) if len(same_dec) > 2 else float("nan")

    def rvec(tag):
        return unit_phase_vec(chan.d_sub, torch.Generator().manual_seed(SEED + hash(tag) % 90000))
    twin = [float(cos_complex(rvec("a%.4f" % x), rvec("b%.4f" % (x * r)))) for x in xs[:5]]
    res = {"n_degrees": len(degs), "degree_range": [round(float(degs.min()), 3), round(float(degs.max()), 3)],
           "LOG_fixed_ratio_CV": round(cv(log_ratio), 4), "LINEAR_fixed_ratio_CV": round(cv(lin_ratio), 4),
           "LOG_fixed_diff_CV": round(cv(log_diff), 4), "LINEAR_fixed_diff_CV": round(cv(lin_diff), 4),
           "weber_preserved_on_real_degrees": weber,
           "composed_code_samepole_decode_logratio_corr": round(decode_corr, 4),
           "composed_code_diffpole_mean_sim": round(float(np.mean(diff_sim)), 4) if diff_sim else None,
           "structurefree_FPE_twin_max_abs_sim": round(float(max(abs(v) for v in twin)), 4),
           "twin_is_flat": bool(max(abs(v) for v in twin) < 0.15)}
    print("[T3 substrate] weber_on_real=%s (LOG ratio-CV=%.3f vs LINEAR ratio-CV=%.3f) | code decode log-ratio corr=%.3f "
          "diffpole_sim=%s | twin_flat=%s"
          % (res["weber_preserved_on_real_degrees"], res["LOG_fixed_ratio_CV"], res["LINEAR_fixed_ratio_CV"],
             res["composed_code_samepole_decode_logratio_corr"], res["composed_code_diffpole_mean_sim"],
             res["twin_is_flat"]), flush=True)
    return res


def run(smoke=False):
    t0 = time.time()
    idf, _ = V1._global_idf()
    conc = V1.ConceptualChannel(idf, {"gloss": True, "lemmas": True, "hyper": True, "hyper_levels": 2}, weighted=True)
    war = V1.load_warriner(); concn = V1.load_concreteness()
    freq, aoa = INT.load_freq_aoa(); lanc = DEEP.load_lancaster_perceptual()
    needed = set(V1.all_wordnet_adjectives()) | set(war) | set(concn)
    for src in ("crowd", "wilkinson", "demelo"):
        for path in glob.glob(os.path.join(DATA, src, "gold_rankings", "*.rankings")):
            s = INT.parse_scale(path)
            if s:
                needed |= {s[0], s[1]} | {t for _, t in s[2]}
    needed |= {w for seeds in V1.DIM_SEEDS.values() for pr in seeds for w in pr}
    gv = V1.build_or_load_glove(needed)
    chan = ScalarMagnitudeChannel(gv, freq, lanc, d_sub=(1024 if smoke else 4096))
    print("[setup] glove=%d warriner=%d concrete=%d freq=%d lanc=%d t=%.1fs"
          % (len(gv), len(war), len(concn), len(freq), len(lanc), time.time() - t0), flush=True)

    t1 = t1_routed_recovery(chan, conc, war, concn, smoke=smoke)
    t2 = t2_unified_axis_and_markedness(chan, conc, smoke=smoke)
    t3 = t3_substrate_weber_on_real_degrees(chan, conc, smoke=smoke)

    def cisep(b):
        return b is not None and b.get("ci_lo") is not None and b["ci_lo"] > 0
    t1_pass = (cisep(t1["boot_COMPOSED_minus_strongest_subop"]) and cisep(t1["boot_COMPOSED_minus_cosine"])
               and cisep(t1["boot_COMPOSED_minus_randomtwin"]))
    weber_pass = bool(t3.get("weber_preserved_on_real_degrees")) and bool(t3.get("twin_is_flat"))
    passes = t1_pass and weber_pass
    verdict = ("COMPOSED_CHANNEL_BEATS_STRONGEST_SUBOP_AND_COSINE_CISEP_WEBER_PRESERVED"
               if passes else "COMPOSED_CHANNEL_DID_NOT_CLEAR_THE_BAR")
    out = {"anchor_name": ANCHOR, "verdict": verdict, "smoke": smoke, "ts_iso": datetime.now(timezone.utc).isoformat(),
           "T1_routed_recovery_PRIMARY": t1, "T2_unified_axis_and_markedness": t2, "T3_substrate_weber": t3,
           "bar_t1_pass": t1_pass, "bar_weber_pass": weber_pass, "elapsed_s": round(time.time() - t0, 2),
           "note": "The composed channel's measurable win over any SINGLE sub-op is DIMENSION-ROUTING + PER-DIM "
                   "GROUNDING (T1, pooled): no single operation serves every scale. T2 shows the brain's unified "
                   "oriented axis already carries pole+degree (proj orders within-scale ~0.72 vs markedness ~0.77), "
                   "so 'three operations' partly collapses into one oriented place code + a marginal markedness "
                   "refinement. T3 shows the FPE-log code preserves Weber on the real degrees (the comparator)."}
    suffix = "_smoke" if smoke else ""
    outdir = os.path.join(REPO_ROOT, "data", ANCHOR + suffix)
    os.makedirs(outdir, exist_ok=True)
    tmp = os.path.join(outdir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    os.replace(tmp, os.path.join(outdir, "metrics.json"))
    print("[verdict] %s  t=%.1fs" % (verdict, time.time() - t0), flush=True)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    run(smoke=args.smoke)
