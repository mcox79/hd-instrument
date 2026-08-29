"""read_terminal_bundle_stores_normalize_per_component_not_pooled -- the SELECTION-WEIGHTED-SHARDED-TYPER.

The map (ADJACENT_COMPONENTS_brain_fidelity_map.md) classified `selection_weighted_sharded_typer` as a
single READ-terminal `cleanup_argmax` caller and said "NO caller re-binds the bundle as an operand." THE DISK
DISAGREES, and this cell measures it. The typer has TWO distinct `bundling.bundle` sites with OPPOSITE roles:

  (A) `_item_role_subbundle` (line 274): the per-item, per-role sub-bundle `item_sub[r]`. This is NOT
      read-terminal -- it is used as the SECOND OPERAND of `binding.bind(sub, outcome)` (lines 293, 311) AND
      as the UNBIND KEY of `binding.unbind(sup_map, sub)` (lines 313, 332, 346, 360). For FHRR, an unbind key
      MUST have per-component UNIT magnitude for the bind/unbind round-trip to recover the value (torus
      closure) -- so PER-COMPONENT renorm is the CORRECT, brain-faithful op here, exactly the "re-bound
      operand" case the brief itself says per-component is for. The map missed this.
  (B) `_build_role_maps` / `_shard_loo_accuracy` (lines 295, 312): `sup_map[r]` = bundle of the bound
      (sub, outcome) pairs. THIS is read-terminal (unbind + `cleanup_argmax` over the outcome vocab).

So the honest per-site verdict is a MIXED one, and this cell measures each:
  PERCOMP        both sites per-component (the DEFAULT / FLOOR = validated mean_acc 0.8333 @ n_train=40, 5 seeds)
  DIVNORM_SUPMAP sup_map (B) -> divnorm; key (A) stays per-component   [the brief's proposed switch, on the
                 site where it is actually read-terminal]
  DIVNORM_KEY    key (A) -> divnorm; sup_map (B) stays per-component    [REFUTATION control: divnorm on the
                 RE-BOUND unbind key should DEGRADE recovery -- proves (A) is not read-terminal and must stay
                 per-component]

READOUT NOTE: the sup_map is read by ARGMAX cleanup (`cleanup_argmax`), which is SCALE-INVARIANT -- so within
a role, divnorm on the sup_map cannot change the argmax. The only channel by which sup_map divnorm can move
predict() is the CROSS-ROLE combine (`combined[y] += w * scores[y]`), where a per-role divnorm scale reweights
roles. So the hypothesis (measured, not assumed) is that DIVNORM_SUPMAP is a NEAR-NULL and DIVNORM_KEY HURTS.
This is the argmax analog of the register's "argmax no-regression" (divnorm helps only the SERIAL readout).

POSITIVE CONTROL: sweep n_train (the number of bound pairs superposed in each sup_map). If per-component ever
breaks the read at high load, DIVNORM_SUPMAP should pull ahead there (the register's overload regime). If no
gap opens even at max load, that CONFIRMS the argmax readout is scale-invariant -> sup_map divnorm is a
principled no-op, and the null is interpretable.
INFO-FREE TWIN: scrambled TRAIN labels (the organ's own validated collapse to ~0.40) -- must LOSE for every arm.

Faithfulness gate: PERCOMP (norm=None at both sites) MUST reproduce the landed mean_acc 0.8333 bit-for-bit,
proving the subclass copies are byte-faithful to the promoted organ.

Run:
  .venv/Scripts/python.exe experiments/exp_read_terminal_divnorm_typer_v1.py --self-test
  .venv/Scripts/python.exe experiments/exp_read_terminal_divnorm_typer_v1.py --run
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, List, Optional, Sequence, Tuple

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import torch

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENTS = os.path.join(REPO, "experiments")
for _p in (REPO, EXPERIMENTS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from hdlab import binding, bundling  # noqa: E402
from hdlab.situation_model_accumulate import cleanup_argmax  # noqa: E402
from hdlab.selection_weighted_sharded_typer import (  # noqa: E402
    SelectionWeightedShardedTyper,
    _role_of,
    shard_weights_from_loo_acc,
)

# KB_REFERENT: the certified data/atoms the promotion witness imports (never re-authored)
import experiments.exp_pragmatic_curriculum_dialogue_request_response_first_test_v1 as MDL_BASE  # noqa: E402
import experiments.exp_pragmatic_curriculum_vsa_superposition_map_v1 as VSA_BASE  # noqa: E402
import experiments.exp_pragmatic_curriculum_dialogue_request_response_dailydialog_v1 as DD  # noqa: E402
import experiments.exp_pragmatic_curriculum_dialogue_role_sharded_binding_v1 as RS  # noqa: E402
import experiments.exp_pragmatic_curriculum_dialogue_role_sharded_scaling_v1 as SCALE  # noqa: E402

VALIDATED_ACC = 0.8333333333333334
BOOT_SEED = 20260828
N_BOOT = 2000


class NormTyper(SelectionWeightedShardedTyper):
    """SelectionWeightedShardedTyper with a norm knob on EACH of its two bundle sites, so the read-terminal
    sup_map and the re-bound unbind-key can be normed independently. The three overridden methods are
    BYTE-FAITHFUL copies of the promoted organ's (commit d47643d87) with ONLY the `norm=` argument added to
    the two `bundling.bundle` calls -- PERCOMP (norm=None at both) reproduces the landed 0.8333 exactly
    (asserted in the faithfulness gate), which certifies the copies did not drift."""

    def __init__(self, *args, sup_map_norm: str = "percomp", key_norm: str = "percomp",
                 combine_norm: str = "none", weight_mode: str = "loo", **kw):
        super().__init__(*args, **kw)
        self._sup_map_norm = None if sup_map_norm == "percomp" else sup_map_norm
        self._key_norm = None if key_norm == "percomp" else key_norm
        # combine_norm: divisive normalization of each role's cleanup-score vector BEFORE the cross-role
        # weighted combine -- the "gain-matched readout" the divnorm store needs (Carandini-Heeger divisive
        # normalization at the DECISION population; Louie & Glimcher 2011/2017 LIP/OFC value normalization).
        # "none" = the landed readout; "l2" = divide by ||scores||_2; "divisive" = divide by sum|scores|.
        self._combine_norm = combine_norm
        # weight_mode: how the cross-role combine is weighted. "loo" = the landed LOO-fit shard_weights_ (an
        # OFFLINE-fit explicit per-role precision weight); "raw" = all weights 1 (a straight SUM of the raw
        # per-role evidence -- the Ma/Beck/Latham/Pouget PPC form where per-source MAGNITUDE is the reliability
        # code, self-calibrating, no fit); "margin" = weight each role by its OWN per-trial cleanup margin
        # (top1-top2), a within-trial self-calibrating reliability signal (magnitude-as-reliability).
        self._weight_mode = weight_mode

    def _per_role_norm(self, scores):
        """PER-ROLE independent normalization (ERASES cross-role relative magnitude -- the literature's
        clearly-NON-brain-faithful move; Ma/Beck/Latham/Pouget: magnitude IS the reliability code)."""
        if self._combine_norm == "l2":
            import math
            nrm = math.sqrt(sum(v * v for v in scores.values())) or 1.0
            return {y: v / nrm for y, v in scores.items()}
        if self._combine_norm == "divisive":
            s = sum(abs(v) for v in scores.values()) or 1.0
            return {y: v / s for y, v in scores.items()}
        raise ValueError("unknown per-role combine_norm %r" % self._combine_norm)

    def predict(self, item_terms):
        """Copy of the promoted organ's predict() (lines 322-337) + optional decision-population normalization.
        combine_norm='none' is byte-identical to the landed predict(). 'shared_pool' = the brain-faithful
        Carandini-Heeger form (ONE scalar over ALL roles+labels, ratio-preserving); 'l2'/'divisive' = per-role
        independent equalization (erases cross-role magnitude, literature-discouraged)."""
        self._require_fitted()
        item_sub, _fb = self._item_role_subbundle(list(item_terms), weights=None)
        role_scores = {}
        for r in self.roles_:
            recovered = binding.unbind(self.sup_maps_[r], item_sub[r])
            _best, scores = cleanup_argmax(recovered, self.outcome_vecs_)
            role_scores[r] = scores
        if self._combine_norm == "shared_pool":
            D = 1e-12 + sum(abs(v) for sc in role_scores.values() for v in sc.values())  # ratio-preserving
            role_scores = {r: {y: v / D for y, v in sc.items()} for r, sc in role_scores.items()}
        elif self._combine_norm in ("l2", "divisive"):
            role_scores = {r: self._per_role_norm(sc) for r, sc in role_scores.items()}
        combined = {y: 0.0 for y in self.labels_}
        for r in self.roles_:
            if self._weight_mode == "loo":
                w = self.shard_weights_[r]
            elif self._weight_mode == "raw":
                w = 1.0                                        # PPC: magnitude IS the weight (self-calibrating)
            elif self._weight_mode == "margin":
                vals = sorted(role_scores[r].values(), reverse=True)
                w = max(0.0, vals[0] - vals[1]) if len(vals) >= 2 else 1.0   # per-trial reliability = cleanup margin
            else:
                raise ValueError("unknown weight_mode %r" % self._weight_mode)
            for y in self.labels_:
                combined[y] += w * role_scores[r][y]
        return max(combined, key=combined.get)

    # (A) the RE-BOUND unbind KEY -- default per-component (torus closure). Copy of lines 243-275 + key_norm.
    def _item_role_subbundle(self, terms: Sequence[str], weights: Optional[Dict[str, float]] = None
                             ) -> Tuple[Dict[str, torch.Tensor], List[str]]:
        by_role: Dict[str, List[str]] = {r: [] for r in self.roles_}
        for t in terms:
            r = _role_of(self._role_of_term, t)
            if r not in by_role:
                raise KeyError("term %r maps to role %r not in fitted roles_ %r" % (t, r, self.roles_))
            by_role[r].append(t)
        out: Dict[str, torch.Tensor] = {}
        fallback_roles: List[str] = []
        for r in self.roles_:
            terms_r = [t for t in by_role[r] if t in self.vocab_vecs_]
            if not terms_r:
                out[r] = torch.zeros(self.n_dim, dtype=torch.complex64)
                continue
            vecs = [self.vocab_vecs_[t] for t in terms_r]
            if weights is None:
                stacked = torch.stack(vecs, dim=0)
            else:
                w = [weights.get(t, 0.0) for t in terms_r]
                if sum(w) <= 0.0:
                    stacked = torch.stack(vecs, dim=0)
                    fallback_roles.append(r)
                else:
                    stacked = torch.stack([wi * v for wi, v in zip(w, vecs)], dim=0)
            out[r] = bundling.bundle(stacked, norm=self._key_norm)   # <-- key_norm injected
        return out, fallback_roles

    # (B) the READ-TERMINAL sup_map -- default per-component; divnorm candidate. Copy of lines 288-296 + sup_map_norm.
    def _build_role_maps(self, items_terms: Sequence[Sequence[str]], gold_labels: Sequence[str],
                         subbundles: Sequence[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
        maps = {}
        for r in self.roles_:
            entries = [binding.bind(subbundles[i][r], self.outcome_vecs_[gold_labels[i]])
                       for i in range(len(items_terms))]
            maps[r] = bundling.bundle(torch.stack(entries, dim=0), norm=self._sup_map_norm)   # <-- sup_map_norm
        return maps

    # (B') the LOO sup_map used to compute shard weights -- same read-terminal site. Copy of lines 298-316.
    def _shard_loo_accuracy(self, role: str, items_terms: Sequence[Sequence[str]],
                            gold_labels: Sequence[str], subbundles: Sequence[Dict[str, torch.Tensor]]) -> float:
        n = len(items_terms)
        if n < 2:
            return 0.0
        correct = 0
        for i in range(n):
            rest = [j for j in range(n) if j != i]
            entries = [binding.bind(subbundles[j][role], self.outcome_vecs_[gold_labels[j]]) for j in rest]
            sup_map = bundling.bundle(torch.stack(entries, dim=0), norm=self._sup_map_norm)   # <-- sup_map_norm
            recovered = binding.unbind(sup_map, subbundles[i][role])
            pred, _scores = cleanup_argmax(recovered, self.outcome_vecs_)
            correct += int(pred == gold_labels[i])
        return correct / n


# ---------------------------------------------------------------- data plumbing (mirrors the witness) ----
_DATA = {}


def _load():
    if _DATA:
        return _DATA
    raw_items = SCALE.load_scaling_items()
    items = MDL_BASE.build_episodes(raw_items)
    pool_items, test_items = SCALE.stratified_test_split(items, seed=SCALE.SPLIT_SEED, test_size=SCALE.TEST_SIZE)
    _vocab_vecs, vocab_terms = VSA_BASE.build_vocab(items)
    _DATA.update(pool_items=pool_items, test_items=test_items, vocab_terms=vocab_terms,
                 gold=[it["gold_class"] for it in test_items])
    return _DATA


def _fit_predict(train_items, test_items, vocab_terms, sup_map_norm, key_norm, combine_norm="none",
                 weight_mode="loo", scramble=False):
    train_terms = [MDL_BASE.feat_fn(it) for it in train_items]
    if scramble:
        train_scr = MDL_BASE.scramble_train_labels(train_items, seed=DD.SCRAMBLE_SEED)
        labels = [it["gold_class"] for it in train_scr]
    else:
        labels = [it["gold_class"] for it in train_items]
    typer = NormTyper(n_dim=VSA_BASE.N_DIM, seed=0, sup_map_norm=sup_map_norm, key_norm=key_norm,
                      combine_norm=combine_norm, weight_mode=weight_mode)
    typer.fit(train_terms, labels, RS.role_of_term, roles=RS.ROLES, vocab_terms=vocab_terms,
              vocab_generator=torch.Generator().manual_seed(VSA_BASE.VOCAB_SEED),
              outcome_generator=torch.Generator().manual_seed(VSA_BASE.OUTCOME_SEED))
    return [typer.predict(MDL_BASE.feat_fn(it)) for it in test_items]


def weight_mode_matrix(n_train, n_seeds, weight_mode, scramble=False):
    """(n_seeds, n_test) correctness for a WEIGHT_MODE arm (per-component store, no combine-norm) -- the PPC
    magnitude-as-reliability drill: does self-calibrating magnitude tie/beat the LOO-fit shard_weights_?"""
    d = _load()
    rows = []
    for si in range(n_seeds):
        seed = SCALE.SUBSAMPLE_SEED_BASE + n_train * 1000 + si
        train_items = SCALE.subsample_train(d["pool_items"], n_train, seed)
        preds = _fit_predict(train_items, d["test_items"], d["vocab_terms"], "percomp", "percomp",
                             weight_mode=weight_mode, scramble=scramble)
        rows.append([int(p == g) for p, g in zip(preds, d["gold"])])
    return np.array(rows, dtype=float)


def weight_mode_drill(n_seeds=12, n_boot=N_BOOT):
    """DRILL 5: brain-faithful PPC magnitude-as-reliability combine (raw sum / per-trial margin weight) vs the
    landed LOO-fit shard_weights_ floor, across load. Retiring the offline-fit weight for a self-calibrating one
    is the higher-fidelity direction the research drill flagged; this MEASURES whether it holds up."""
    rng = np.random.default_rng(BOOT_SEED + 7)
    out = {"by_load": {}, "twin": {}}
    for nt in (8, 16, 40):
        loo = weight_mode_matrix(nt, n_seeds, "loo")
        row = {"loo": round(float(loo.mean()), 4)}
        for wm in ("raw", "margin"):
            m = weight_mode_matrix(nt, n_seeds, wm)
            dd, lo, hi = _paired_boot(m, loo, n_boot, rng)
            row[wm] = {"acc": round(float(m.mean()), 4), "delta": round(dd, 4), "ci": [round(lo, 4), round(hi, 4)]}
        out["by_load"]["n_train=%d" % nt] = row
    for wm in ("loo", "raw", "margin"):
        out["twin"][wm] = round(float(weight_mode_matrix(40, n_seeds, wm, scramble=True).mean()), 4)
    return out


# The research-drill 4-arm test (notes/research_divisive_norm_decision_stage_reliability_2026-08-29.md) +
# the store-norm arms. shared_pool = the BRAIN-FAITHFUL ratio-preserving Carandini-Heeger form (one scalar over
# ALL roles); l2 = the literature's NON-brain-faithful per-role equalization (erases cross-role magnitude =
# the reliability code, Ma/Beck/Latham/Pouget PPC).
ARMS = {
    "PERCOMP": ("percomp", "percomp", "none"),                 # Arm 1: the landed floor (validated 0.8333)
    "DIVNORM_SUPMAP": ("divnorm", "percomp", "none"),          # Arm 2: divnorm store, old readout -> hurts
    "PERCOMP_SHAREDPOOL": ("percomp", "percomp", "shared_pool"),  # Arm 3: brain-faithful decision norm (argmax-invariant?)
    "PERCOMP_L2": ("percomp", "percomp", "l2"),               # Arm 4: NON-brain-faithful per-role equalization
    "DIVNORM_SUPMAP_GM": ("divnorm", "percomp", "l2"),        # divnorm store + per-role equalization (my earlier "win")
    "DIVNORM_SHAREDPOOL": ("divnorm", "percomp", "shared_pool"),  # divnorm store + brain-faithful decision norm
    "DIVNORM_KEY": ("percomp", "divnorm", "none"),            # map-refutation control (re-bound key)
}


def _correct_matrix(n_train, n_seeds, arm, scramble=False):
    """(n_seeds, n_test) 0/1 correctness for one arm -- SAME seeds/atoms/items across arms (paired)."""
    d = _load()
    sup_norm, key_norm, combine_norm = ARMS[arm]
    rows = []
    for si in range(n_seeds):
        seed = SCALE.SUBSAMPLE_SEED_BASE + n_train * 1000 + si
        train_items = SCALE.subsample_train(d["pool_items"], n_train, seed)
        preds = _fit_predict(train_items, d["test_items"], d["vocab_terms"], sup_norm, key_norm,
                             combine_norm=combine_norm, scramble=scramble)
        rows.append([int(p == g) for p, g in zip(preds, d["gold"])])
    return np.array(rows, dtype=float)


def _paired_boot(a_mat, b_mat, n_boot, rng):
    """Paired bootstrap over the (seed x item) cells of two arms' correctness matrices -> delta(a-b) CI."""
    a = a_mat.reshape(-1); b = b_mat.reshape(-1)
    n = len(a)
    idx = rng.integers(0, n, size=(n_boot, n))
    da = a[idx].mean(axis=1) - b[idx].mean(axis=1)
    return float(a.mean() - b.mean()), float(np.percentile(da, 2.5)), float(np.percentile(da, 97.5))


def cell(n_seeds=12, n_boot=N_BOOT):
    d = _load()
    rng = np.random.default_rng(BOOT_SEED)
    res = {"n_test": len(d["test_items"]), "n_seeds": n_seeds, "arms": {}, "overload": {}, "twin": {}}

    # (1) validated task @ n_train=40
    mats = {arm: _correct_matrix(40, n_seeds, arm) for arm in ARMS}
    for arm in ARMS:
        res["arms"][arm] = {"mean_acc": round(float(mats[arm].mean()), 4)}
    floor = mats["PERCOMP"]
    for arm in [a for a in ARMS if a != "PERCOMP"]:
        delta, lo, hi = _paired_boot(mats[arm], floor, n_boot, rng)
        res["arms"][arm].update(delta_vs_percomp=round(delta, 4), ci=[round(lo, 4), round(hi, 4)],
                                 ci_separated=bool(hi < 0 or lo > 0))

    # (2) info-free twin (scrambled labels) -- must lose
    for arm in ARMS:
        tw = _correct_matrix(40, n_seeds, arm, scramble=True)
        res["twin"][arm] = round(float(tw.mean()), 4)

    # (3) DRILL: the research 4-arm test across load -- is the WIN from the BRAIN-FAITHFUL shared pooled divisor
    # (ratio-preserving) or the NON-brain-faithful per-role equalization? And is shared_pool argmax-inert?
    pool_n = len(d["pool_items"])
    sweep_arms = ["DIVNORM_SUPMAP", "PERCOMP_SHAREDPOOL", "PERCOMP_L2", "DIVNORM_SUPMAP_GM", "DIVNORM_SHAREDPOOL"]
    for nt in [nt for nt in (8, 16, 40) if nt <= pool_n]:
        pmat = _correct_matrix(nt, n_seeds, "PERCOMP")
        row = {"percomp": round(float(pmat.mean()), 4)}
        for arm in sweep_arms:
            amat = _correct_matrix(nt, n_seeds, arm)
            dd, lo, hi = _paired_boot(amat, pmat, n_boot, rng)
            row[arm] = {"acc": round(float(amat.mean()), 4), "delta": round(dd, 4), "ci": [round(lo, 4), round(hi, 4)]}
        res["overload"]["n_train=%d" % nt] = row
    res["pool_n"] = pool_n

    # (4) refutation control: the re-bound unbind KEY (multi-term keys) -- does key norm matter under load?
    res["key_roundtrip_loadsweep"] = key_roundtrip_loadsweep(n_dim=256, k_terms=4, n_trials=30)
    # singleton diagnostic: what fraction of (item,role) sub-bundles have >=2 terms (where the norm matters)?
    res["multiterm_frac"] = _multiterm_frac()
    return res


def _multiterm_frac():
    d = _load()
    seed = SCALE.SUBSAMPLE_SEED_BASE + 40 * 1000 + 0
    train_items = SCALE.subsample_train(d["pool_items"], 40, seed)
    n_multi = n_total = 0
    for it in list(train_items) + list(d["test_items"]):
        terms = MDL_BASE.feat_fn(it)
        by_role = {}
        for t in terms:
            r = RS.role_of_term(t)
            by_role.setdefault(r, []).append(t)
        for r, ts in by_role.items():
            n_total += 1
            if len(ts) >= 2:
                n_multi += 1
    return round(n_multi / n_total, 4) if n_total else 0.0


def _print(res):
    print("=== TYPER: read-terminal sup_map vs re-bound unbind-KEY, per-component vs divnorm ===")
    print("  validated task: role-sharded MET/UNMET typing, n_train=40, %d seeds, n_test=%d\n"
          % (res["n_seeds"], res["n_test"]))
    print("  arm                  mean_acc   delta_vs_percomp  [CI]              CI-separated")
    for arm in ARMS:
        a = res["arms"][arm]
        if arm == "PERCOMP":
            print("  %-19s %.4f     (floor; validated 0.8333)" % (arm, a["mean_acc"]))
        else:
            print("  %-19s %.4f     %+.4f          [%+.3f,%+.3f]     %s"
                  % (arm, a["mean_acc"], a["delta_vs_percomp"], a["ci"][0], a["ci"][1], a["ci_separated"]))
    print("\n  info-free twin (scrambled labels; must lose vs ~0.83):")
    for arm in ARMS:
        print("    %-19s mean_acc=%.4f" % (arm, res["twin"][arm]))
    print("\n  DRILL (research 4-arm test): brain-faithful shared-pool (ratio-preserving) vs NON-faithful per-role")
    print("  L2 equalization vs divnorm store. delta vs per-component floor, [CI]. pool=%d" % res["pool_n"])
    sweep_arms = ["DIVNORM_SUPMAP", "PERCOMP_SHAREDPOOL", "PERCOMP_L2", "DIVNORM_SUPMAP_GM", "DIVNORM_SHAREDPOOL"]
    for nt, row in res["overload"].items():
        print("    %s  (floor percomp=%.4f)" % (nt, row["percomp"]))
        for arm in sweep_arms:
            a = row[arm]
            sep = "CI-sep" if (a["ci"][0] > 0 or a["ci"][1] < 0) else "  --  "
            print("       %-20s %.4f  %+.4f [%+.3f,%+.3f] %s" % (arm, a["acc"], a["delta"], a["ci"][0], a["ci"][1], sep))
    print("\n  RE-BOUND KEY CONTROL: does the unbind-KEY norm matter? (synthetic assoc-memory round-trip, k=4, n_dim=256)")
    print("    (the typer's own data is %.0f%% singleton sub-bundles, where percomp==divnorm exactly)"
          % (100 * (1 - res["multiterm_frac"])))
    print("    load(n_pairs)   percomp_key_acc   divnorm_key_acc")
    for k, row in res["key_roundtrip_loadsweep"].items():
        print("    %-14s %.4f            %.4f" % (k, row["percomp"], row["divnorm"]))


def key_roundtrip_control(n_dim=256, k_terms=4, n_pairs=32, n_trials=40, seed=0):
    """SYNTHETIC associative-memory round-trip that probes whether the KEY norm matters when a bundle is used
    as a re-bound unbind KEY (the typer's (A) site). M = sum_j bind(key_j, val_j) with each key_j a bundle of
    k_terms>=2 atoms; recover val_i via unbind(M, key_i) + argmax cleanup. Per-component gives |key_i|=1 per
    component (exact torus closure: key*conj(key)=1); divnorm gives varying |key_i| (distorted self-inverse).
    Reports mean recovery accuracy per key-norm at a given LOAD (n_pairs/n_dim). Sweeping load reveals whether
    argmax cleanup is robust to the key distortion (it is, until deep overload)."""
    from hdlab.situation_model_accumulate import unit_phase_vec, cleanup_argmax as _ca
    accs = {"percomp": [], "divnorm": []}
    for t in range(n_trials):
        g = torch.Generator().manual_seed(seed * 1000 + t)
        vocab = {f"v{i}": unit_phase_vec(n_dim, g) for i in range(n_pairs)}
        atoms = [unit_phase_vec(n_dim, g) for _ in range(n_pairs * k_terms)]
        names = list(vocab.keys())
        for kn in ("percomp", "divnorm"):
            arg = None if kn == "percomp" else "divnorm"
            keys = [bundling.bundle(torch.stack(atoms[j * k_terms:(j + 1) * k_terms]), norm=arg) for j in range(n_pairs)]
            M = None
            for j, name in enumerate(names):
                pair = binding.bind(keys[j], vocab[name])
                M = pair if M is None else M + pair
            correct = sum(int(_ca(binding.unbind(M, keys[j]), vocab)[0] == names[j]) for j in range(n_pairs))
            accs[kn].append(correct / n_pairs)
    return {"percomp": round(float(np.mean(accs["percomp"])), 4), "divnorm": round(float(np.mean(accs["divnorm"])), 4)}


def key_roundtrip_loadsweep(n_dim=256, k_terms=4, n_trials=30):
    """Sweep LOAD (n_pairs from light to deep overload) to see whether per-component ever beats divnorm as an
    unbind key. If a gap opens only at deep overload, the key norm is a soft convention that argmax tolerates."""
    return {("load=%d" % np_): key_roundtrip_control(n_dim=n_dim, k_terms=k_terms, n_pairs=np_, n_trials=n_trials)
            for np_ in (n_dim // 8, n_dim // 4, n_dim // 2, n_dim, 2 * n_dim)}


def _self_test():
    # faithfulness gate: PERCOMP reproduces the landed 0.8333 at n_train=40, 5 seeds, bit-for-bit.
    mat = _correct_matrix(40, 5, "PERCOMP")
    acc = float(mat.mean())
    assert abs(acc - VALIDATED_ACC) < 1e-9, "FAITHFULNESS FAIL: PERCOMP mean_acc=%.16f != landed %.16f" % (acc, VALIDATED_ACC)
    # knob wiring: a MULTI-term (k>=2) bundle differs under divnorm vs percomp (singletons coincide, so use k=3).
    g = torch.Generator().manual_seed(1)
    from hdlab.situation_model_accumulate import unit_phase_vec
    stk = torch.stack([unit_phase_vec(256, g) for _ in range(3)])
    assert not torch.equal(bundling.bundle(stk), bundling.bundle(stk, norm="divnorm")), "norm knob inert on k=3 bundle"
    print("[self-test] PASS: PERCOMP=landed 0.8333 (byte-faithful subclass); norm knob live on k>=2 bundles")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--n-seeds", type=int, default=12)
    ap.add_argument("--n-boot", type=int, default=N_BOOT)
    args = ap.parse_args()
    if args.self_test:
        _self_test()
        raise SystemExit(0)
    _self_test()
    _print(cell(n_seeds=args.n_seeds, n_boot=args.n_boot))
