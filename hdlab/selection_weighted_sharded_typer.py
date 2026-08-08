"""hdlab/selection_weighted_sharded_typer.py -- discriminativeness-weighted, role-sharded,
shard-selected VSA superposition typer for pragmatic-construction typing.

WIRE-DON'T-ISLAND PROMOTION (2026-08-07) of the overnight-drill winner validated in
experiments/exp_pragmatic_curriculum_dialogue_role_sharded_shard_attention_v1.py (commit
d47643d87): at n_train=40 (5 seeds) on the 72-item clean-modern-DailyDialog scaling set
(experiments/data/dialogue_request_response_dailydialog_scaling_v1.jsonl), the shard-LOO-
weighted role-sharded combine (arm `role_shard_weighted` there) scored mean_acc=0.8333
(std=0.000), beating attention-flat 0.7833, naive-flat 0.65, unweighted role-sharding 0.5333,
MDL 0.7083, majority 0.50; its scramble control collapsed to 0.40 (<= 0.60 band). The hard
one-hot `role_shard_select` variant TIES it at 0.8333.

MECHANISM (biased-competition attention over hippocampal DG/CA3-style pattern-separated
storage): cues are partitioned into named ROLE SHARDS (caller-supplied domain knowledge, e.g.
dialogue's REQUEST / RESPONSE_POLARITY / DISCOURSE / FILLER_META family map) so a near-
universal filler cue physically cannot swamp a sparse discriminative cue's similarity budget
within the SAME bundle (hdlab/role_slot_summarizer.py's validated SHARDED-storage architecture,
reused here structurally: per-slot alpha = K/(S*N) vs FLAT alpha = K/N). On top of that
structural fix, attention (Desimone & Duncan biased competition) is layered at TWO levels:
  (1) per-CUE (within a shard): weight_c = max_y |P(y|c present) - P(y|c absent)|, estimated on
      TRAIN only -- generalizes exp_..._dailydialog_v1.py's arm3 binary formula
      |P(MET|present)-P(MET|absent)| to K labels by taking the largest per-label margin (reduces
      to the EXACT binary formula at K=2, since the two per-label margins are equal in magnitude
      when there are only two classes). Used by predict_composed() only -- see below.
  (2) per-SHARD: weight_r = max(0, loo_acc_r - chance), where loo_acc_r is shard r's OWN TRAIN
      leave-one-out cross-validated readout accuracy (its own sup_map, LOO-folded so an anti-
      informative shard cannot masquerade as informative via small-n self-memorization) and
      chance = 1/n_labels (0.5 for the validated binary construction, matching the source cell's
      formula exactly; K>2 is an unvalidated but natural generalization). This is the DEFAULT /
      VALIDATED route (predict()).
Degenerate guard at both levels: if every weight in a group is <=0 (no cue/shard beats a null
baseline on this TRAIN draw), falls back to equal weight across that group (glass-box --
`*_used_fallback_` attributes report it, never silently substituted). Mirrors the source cells'
own per-item / per-shard fallback convention.

THREE ROUTES, glass-box:
  predict()           DEFAULT / VALIDATED: shard-LOO-weighted combine of UNWEIGHTED cue
                       sub-bundles (reproduces `role_shard_weighted`, 0.8333 at n_train=40/5
                       seeds).
  predict_select()     Hard one-hot: route via ONLY the highest-LOO-accuracy shard (reproduces
                       `role_shard_select`, ties predict() at 0.8333 on the validated
                       construction).
  predict_composed()   BOTH levels at once (cue-weighted sub-bundles + shard-LOO weighting) --
                       exploratory; MEASURED WORSE than predict() on the validated construction
                       (0.80 vs 0.8333, `role_shard_weighted_composed_both_levels`). Kept for
                       glass-box comparison; NOT the recommended default.

REUSE (imported, not byte-copied -- both are already-promoted hdlab organs living on the SAME
FHRR complex64 substrate this typer runs on, so this is genuine reuse, not a re-transcription):
hdlab.situation_model_accumulate.unit_phase_vec (FHRR atom generation -- bit-identical to
atoms.make_atom_fhrr: both draw one torch.rand(n) phase vector per atom off the SAME generator
and map it through unit-magnitude complex exponentiation) + .cleanup_argmax (FHRR unbind-then-
score readout: conj(v)*readback summed then divided by n -- bit-identical to
hdlab.atoms.similarity's a*conj(b) computation, multiplication commutes), hdlab.binding.bind /
.unbind, hdlab.bundling.bundle. The shard-LOO-weighting / cue-discriminativeness FORMULAS
themselves are new (first promoted here) and are REIMPLEMENTED, not imported, from the
validated experiment cells (CLAUDE.md: hdlab must not import experiments/) -- see
exp_pragmatic_curriculum_dialogue_role_sharded_shard_attention_v1.py's shard_weights_from_
loo_acc / shard_train_loo_accuracy and exp_pragmatic_curriculum_dialogue_request_response_
dailydialog_v1.py's compute_cue_weights for the byte-identical originals this module ports
(with the K-class generalizations noted above; both reduce exactly to the source formula at
K=2, the only regime measured so far).

GENERALITY: construction-agnostic. Takes item cue-terms plus a caller-supplied `role_of_term`
(which cues belong to which shard is domain knowledge the caller owns -- e.g. dialogue's
REQUEST/RESPONSE_POLARITY/DISCOURSE/FILLER_META family map) and LEARNS everything else (cue
weights, shard weights, per-shard maps) from TRAIN. No dialogue-specific assumption lives in
this module. Honesty note: validated on ONE construction so far (dialogue request/response
typing, n_train=40, 5 seeds) -- the organ is general, its validation scope is one tier.

Deterministic given a passed torch.Generator (or int seed); no implicit global RNG state.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union

import torch

from . import binding, bundling
from .situation_model_accumulate import cleanup_argmax, unit_phase_vec

RoleOf = Union[Dict[str, str], Callable[[str], str]]


def _role_of(role_map: RoleOf, term: str) -> str:
    """Dispatches a cue-term string to its assigned role/shard name. role_map may be a plain
    {term: role} dict or a callable(term) -> role (e.g. a family-lookup function)."""
    if isinstance(role_map, dict):
        role = role_map.get(term)
        if role is None:
            raise KeyError("_role_of: unassigned cue term %r -- role-map coverage gap" % (term,))
        return role
    return role_map(term)


def compute_cue_weights(items_terms: Sequence[Sequence[str]], labels: Sequence[str],
                         label_set: Sequence[str]) -> Dict[str, float]:
    """TRAIN-only per-cue discriminativeness: weight_c = max_y |P(y|c present) - P(y|c absent)|.
    Reduces EXACTLY to the validated binary formula |P(pos|present)-P(pos|absent)| when
    len(label_set)==2 (the two per-label margins are equal in magnitude by construction --
    P(a|.)+P(b|.)=1). Terms with no evidence in one of the present/absent TRAIN groups get
    weight 0.0 (conservative -- ports exp_pragmatic_curriculum_dialogue_request_response_
    dailydialog_v1.py's compute_cue_weights verbatim formula)."""
    n = len(items_terms)
    term_sets = [set(terms) for terms in items_terms]
    all_terms = sorted({t for s in term_sets for t in s})
    weights: Dict[str, float] = {}
    for term in all_terms:
        present_idx = [i for i in range(n) if term in term_sets[i]]
        absent_idx = [i for i in range(n) if term not in term_sets[i]]
        if not present_idx or not absent_idx:
            weights[term] = 0.0
            continue
        best = 0.0
        for y in label_set:
            p_present = sum(1 for i in present_idx if labels[i] == y) / len(present_idx)
            p_absent = sum(1 for i in absent_idx if labels[i] == y) / len(absent_idx)
            best = max(best, abs(p_present - p_absent))
        weights[term] = best
    return weights


def shard_weights_from_loo_acc(shard_accs: Dict[str, float], roles: Sequence[str],
                                chance: float) -> Tuple[Dict[str, float], bool]:
    """weight_r = max(0, loo_acc_r - chance). Degenerate guard: if every shard's raw weight is
    <=0 (no shard beats chance on this TRAIN draw), falls back to equal weight 1.0 across all
    shards (glass-box: used_fallback returned, never silently substituted). Ports
    exp_pragmatic_curriculum_dialogue_role_sharded_shard_attention_v1.py's shard_weights_from_
    loo_acc verbatim (chance=0.5 there; generalized to chance=1/n_labels here -- identical at
    K=2, the validated regime)."""
    raw = {r: max(0.0, shard_accs[r] - chance) for r in roles}
    used_fallback = sum(raw.values()) <= 0.0
    if used_fallback:
        raw = {r: 1.0 for r in roles}
    return raw, used_fallback


class SelectionWeightedShardedTyper:
    """Discriminativeness-weighted, role-sharded, shard-selected VSA superposition typer.

    Public API:
        fit(train_item_terms, gold_labels, role_of_term, roles=None, vocab_terms=None,
            vocab_generator=None, outcome_generator=None) -> self
        predict(item_terms) -> label             DEFAULT / VALIDATED route (0.8333 @ n_train=40)
        predict_select(item_terms) -> label       hard one-hot best-shard routing
        predict_composed(item_terms) -> label     both-levels (cue+shard weighting); exploratory

    Glass-box (populated by fit(), read-only after fitting):
        cue_weights_                      {term: weight}   (used by predict_composed only)
        shard_loo_acc_ / shard_weights_   {role: value}     (unweighted route, predict()'s basis)
        shard_weights_used_fallback_      bool
        selected_role_                    argmax-LOO-accuracy role (predict_select's route)
        shard_loo_acc_weighted_ / shard_weights_weighted_   (composed route's own shard scoring)
        labels_, roles_, chance_
    """

    def __init__(self, n_dim: int = 1024, seed: int = 0) -> None:
        self.n_dim = int(n_dim)
        self.seed = int(seed)
        self._fitted = False

    # ------------------------------------------------------------------ fit ----------------
    def fit(self, train_item_terms: Sequence[Sequence[str]], gold_labels: Sequence[str],
            role_of_term: RoleOf, roles: Optional[Sequence[str]] = None,
            vocab_terms: Optional[Sequence[str]] = None,
            vocab_generator: Optional[torch.Generator] = None,
            outcome_generator: Optional[torch.Generator] = None) -> "SelectionWeightedShardedTyper":
        """Learns per-cue + per-shard discriminativeness weights and the role-sharded sup_maps.

        train_item_terms: one Sequence[str] of active cue-term strings per TRAIN item (the
            'name=value' / 'name=True' encoded-feature convention used throughout this codebase's
            construction-typing lineage).
        gold_labels: parallel gold label per TRAIN item.
        role_of_term: {term: role} dict or callable(term)->role; caller-supplied domain
            knowledge (which cues belong to which shard).
        roles: optional explicit shard ORDER (also fixes float-summation order in predict()'s
            weighted combine, for byte-identical reproduction of a cited run); inferred
            (sorted) from role_of_term's outputs over the vocabulary if omitted.
        vocab_terms: optional additional cue terms to pre-register atoms for (e.g. terms that
            only appear in a held-out TEST set) -- lets predict() see a corpus-wide vocabulary
            instead of a train-only one, matching this mechanism's source-cell convention of
            building vocab atoms once over the whole corpus. Terms outside the resulting
            vocabulary are silently skipped at predict-time (an honest 'no atom, no vote').
        vocab_generator / outcome_generator: torch.Generator for atom draws; default
            torch.Generator().manual_seed(self.seed) / manual_seed(self.seed + 1) respectively
            (two independent generators so vocab and outcome draws never correlate).
        """
        n = len(train_item_terms)
        if n != len(gold_labels):
            raise ValueError("train_item_terms (%d) and gold_labels (%d) length mismatch"
                              % (n, len(gold_labels)))
        if n < 2:
            raise ValueError("fit requires n_train >= 2 (leave-one-out shard scoring is undefined below that)")
        items_terms: List[List[str]] = [list(t) for t in train_item_terms]
        gold_labels = list(gold_labels)
        vgen = vocab_generator if vocab_generator is not None else torch.Generator().manual_seed(self.seed)
        ogen = outcome_generator if outcome_generator is not None else torch.Generator().manual_seed(self.seed + 1)

        self.labels_ = sorted(set(gold_labels))
        self.chance_ = 1.0 / len(self.labels_)
        self._role_of_term = role_of_term

        train_terms = {t for terms in items_terms for t in terms}
        all_terms = sorted(train_terms | set(vocab_terms or ()))
        self.roles_ = list(roles) if roles is not None else sorted({_role_of(role_of_term, t) for t in all_terms})

        # ---- deterministic FHRR atoms: one per vocab term (sorted order) + one per label ----
        self.vocab_vecs_: Dict[str, torch.Tensor] = {t: unit_phase_vec(self.n_dim, vgen) for t in all_terms}
        self.outcome_vecs_: Dict[str, torch.Tensor] = {y: unit_phase_vec(self.n_dim, ogen) for y in self.labels_}

        # ---- per-cue TRAIN-only discriminativeness (used by predict_composed only) ----
        self.cue_weights_ = compute_cue_weights(items_terms, gold_labels, self.labels_)

        # ---- per-item, per-role sub-bundles: UNWEIGHTED -- the validated/default construction ----
        subb_unw, fb_unw = self._build_role_subbundles(items_terms, weights=None)
        self._items_terms, self._gold_labels = items_terms, gold_labels
        self._subb_unweighted = subb_unw
        self.role_subbundle_fallback_ids_ = fb_unw

        # ---- per-role sup_map over ALL of TRAIN (unweighted) -- the deployed model ----
        self.sup_maps_ = self._build_role_maps(items_terms, gold_labels, subb_unw)

        # ---- per-shard TRAIN-only leave-one-out CV accuracy (honest, not self-memorized) ----
        self.shard_loo_acc_ = {r: self._shard_loo_accuracy(r, items_terms, gold_labels, subb_unw)
                                for r in self.roles_}
        self.shard_weights_, self.shard_weights_used_fallback_ = shard_weights_from_loo_acc(
            self.shard_loo_acc_, self.roles_, self.chance_)
        self.selected_role_ = max(self.roles_, key=lambda r: self.shard_loo_acc_[r])

        # ---- COMPOSED (both-levels): cue-weighted sub-bundles + their own sup_maps/LOO ----
        subb_w, fb_w = self._build_role_subbundles(items_terms, weights=self.cue_weights_)
        self.role_subbundle_fallback_ids_weighted_ = fb_w
        self.sup_maps_weighted_ = self._build_role_maps(items_terms, gold_labels, subb_w)
        self.shard_loo_acc_weighted_ = {r: self._shard_loo_accuracy(r, items_terms, gold_labels, subb_w)
                                         for r in self.roles_}
        self.shard_weights_weighted_, self.shard_weights_weighted_used_fallback_ = shard_weights_from_loo_acc(
            self.shard_loo_acc_weighted_, self.roles_, self.chance_)

        self._fitted = True
        return self

    # ------------------------------------------------------------- internals ---------------
    def _item_role_subbundle(self, terms: Sequence[str],
                              weights: Optional[Dict[str, float]] = None
                              ) -> Tuple[Dict[str, torch.Tensor], List[str]]:
        """Groups this item's active terms by role, bundles each role's (optionally weighted)
        vocab atoms. Empty shard -> zero vector (honest 'no signal offered', not a crash). OOV
        terms (not in vocab_vecs_) are skipped. Weighted mode: per-shard degenerate guard --
        if every active term in a shard has weight 0 (or all its terms are OOV under weighting),
        falls back to equal weight WITHIN that shard."""
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
            out[r] = bundling.bundle(stacked)
        return out, fallback_roles

    def _build_role_subbundles(self, items_terms: Sequence[Sequence[str]],
                                weights: Optional[Dict[str, float]] = None
                                ) -> Tuple[List[Dict[str, torch.Tensor]], List[Tuple[int, List[str]]]]:
        out, fallbacks = [], []
        for idx, terms in enumerate(items_terms):
            sub, fb = self._item_role_subbundle(terms, weights=weights)
            out.append(sub)
            if fb:
                fallbacks.append((idx, fb))
        return out, fallbacks

    def _build_role_maps(self, items_terms: Sequence[Sequence[str]], gold_labels: Sequence[str],
                          subbundles: Sequence[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
        """sup_map[r] = bundle(bind(role_subbundle_i[r], outcome_vec[gold_i])) over items."""
        maps = {}
        for r in self.roles_:
            entries = [binding.bind(subbundles[i][r], self.outcome_vecs_[gold_labels[i]])
                       for i in range(len(items_terms))]
            maps[r] = bundling.bundle(torch.stack(entries, dim=0))
        return maps

    def _shard_loo_accuracy(self, role: str, items_terms: Sequence[Sequence[str]],
                             gold_labels: Sequence[str],
                             subbundles: Sequence[Dict[str, torch.Tensor]]) -> float:
        """LOO-CV accuracy of role `role`'s OWN sub-bundle map on TRAIN itself: fold out each
        TRAIN item once, rebuild the shard's map on the rest, predict the held-out item. TRAIN-
        only (zero test leakage); avoids the trivial ~1.0 self-memorization a naive re-predict-
        on-full-TRAIN readout would give at small n."""
        n = len(items_terms)
        if n < 2:
            return 0.0
        correct = 0
        for i in range(n):
            rest = [j for j in range(n) if j != i]
            entries = [binding.bind(subbundles[j][role], self.outcome_vecs_[gold_labels[j]]) for j in rest]
            sup_map = bundling.bundle(torch.stack(entries, dim=0))
            recovered = binding.unbind(sup_map, subbundles[i][role])
            pred, _scores = cleanup_argmax(recovered, self.outcome_vecs_)
            correct += int(pred == gold_labels[i])
        return correct / n

    def _require_fitted(self) -> None:
        if not self._fitted:
            raise RuntimeError("SelectionWeightedShardedTyper: predict called before fit()")

    # -------------------------------------------------------------- predict ----------------
    def predict(self, item_terms: Sequence[str]) -> str:
        """DEFAULT / VALIDATED route: shard-LOO-weighted combine of UNWEIGHTED role sub-bundles
        (reproduces `role_shard_weighted`, mean_acc=0.8333 at n_train=40/5 seeds, commit
        d47643d87). Sums each shard's label-similarity vector weighted by shard_weights_, then
        argmaxes over labels."""
        self._require_fitted()
        item_sub, _fb = self._item_role_subbundle(list(item_terms), weights=None)
        combined = {y: 0.0 for y in self.labels_}
        for r in self.roles_:
            recovered = binding.unbind(self.sup_maps_[r], item_sub[r])
            _best, scores = cleanup_argmax(recovered, self.outcome_vecs_)
            w = self.shard_weights_[r]
            for y in self.labels_:
                combined[y] += w * scores[y]
        return max(combined, key=combined.get)

    def predict_select(self, item_terms: Sequence[str]) -> str:
        """Hard one-hot shard-select: route via ONLY the single highest-LOO-accuracy role
        (`role_shard_select`, ties predict() at 0.8333 on the validated construction -- the
        one-hot limit of the shard-weighted combine)."""
        self._require_fitted()
        item_sub, _fb = self._item_role_subbundle(list(item_terms), weights=None)
        r = self.selected_role_
        recovered = binding.unbind(self.sup_maps_[r], item_sub[r])
        best, _scores = cleanup_argmax(recovered, self.outcome_vecs_)
        return best

    def predict_composed(self, item_terms: Sequence[str]) -> str:
        """BOTH-levels: cue-weighted sub-bundles (predict-time weighting reuses the SAME
        cue_weights_ learned at fit time) combined with shard-LOO weighting computed on those
        weighted sub-bundles. Exploratory -- MEASURED WORSE than predict() on the validated
        construction (0.80 vs 0.8333, `role_shard_weighted_composed_both_levels`); kept for
        glass-box comparison, not the recommended default."""
        self._require_fitted()
        item_sub, _fb = self._item_role_subbundle(list(item_terms), weights=self.cue_weights_)
        combined = {y: 0.0 for y in self.labels_}
        for r in self.roles_:
            recovered = binding.unbind(self.sup_maps_weighted_[r], item_sub[r])
            _best, scores = cleanup_argmax(recovered, self.outcome_vecs_)
            w = self.shard_weights_weighted_[r]
            for y in self.labels_:
                combined[y] += w * scores[y]
        return max(combined, key=combined.get)


# ===================== formula self-tests (data-independent; the real-data reproduction lives
# in verification/test_selection_weighted_sharded_typer.py, which imports the certified
# experiment cells for byte-identical data/split/vocab reuse) =============================

def _selftest_cue_weight_formula() -> None:
    """Binary reduction: hand-computed 2-item-per-group toy example."""
    items = [["c1=True", "c2=True"], ["c1=True"], ["c2=True"], ["c2=True"]]
    labels = ["A", "A", "B", "B"]
    w = compute_cue_weights(items, labels, ["A", "B"])
    # c1 present in items 0,1 (both A) -> P(A|present)=1.0; absent in 2,3 (both B) -> P(A|absent)=0.0
    assert abs(w["c1=True"] - 1.0) < 1e-9, w
    # c2 present in items 0,2,3 (A,B,B) -> P(A|present)=1/3; absent in item 1 (A) -> P(A|absent)=1.0
    assert abs(w["c2=True"] - abs(1.0 / 3 - 1.0)) < 1e-9, w


def _selftest_shard_weight_formula() -> None:
    """Reproduces exp_..._shard_attention_v1.py's own selftest contrived values verbatim."""
    w, fb = shard_weights_from_loo_acc({"A": 0.9, "B": 0.5, "C": 0.3, "D": 0.6},
                                        roles=["A", "B", "C", "D"], chance=0.5)
    assert abs(w["A"] - 0.4) < 1e-9 and abs(w["B"] - 0.0) < 1e-9 and abs(w["C"] - 0.0) < 1e-9 \
        and abs(w["D"] - 0.1) < 1e-9, w
    assert fb is False
    w2, fb2 = shard_weights_from_loo_acc({"A": 0.5, "B": 0.4, "C": 0.5, "D": 0.2},
                                          roles=["A", "B", "C", "D"], chance=0.5)
    assert fb2 is True and all(abs(v - 1.0) < 1e-9 for v in w2.values()), w2


def _synthetic_shard_separated_task(n_dim=256, n_train=24, n_test=24, seed=0):
    """Two shards, ROLE_A (informative: cue 'a=hi'/'a=lo' perfectly predicts the label) and
    ROLE_B (uninformative: cue 'b=x' fires on every item regardless of label -- a filler)."""
    rng = torch.Generator().manual_seed(seed)

    def make(n, offset):
        items, labels = [], []
        for i in range(n):
            y = "POS" if (i + offset) % 2 == 0 else "NEG"
            a_term = "a=hi" if y == "POS" else "a=lo"
            items.append([a_term, "b=x"])
            labels.append(y)
        return items, labels

    train_items, train_labels = make(n_train, 0)
    test_items, test_labels = make(n_test, 1)
    role_of_term = {"a=hi": "ROLE_A", "a=lo": "ROLE_A", "b=x": "ROLE_B"}
    return train_items, train_labels, test_items, test_labels, role_of_term


def _selftest_synthetic_recovers_informative_shard() -> None:
    """On a shard-separated synthetic task, the informative shard's LOO accuracy must exceed the
    uninformative (constant-cue) shard's, shard_weights_ must up-weight it, and predict() must
    recover the label perfectly (the informative cue determines the label by construction)."""
    tr_items, tr_labels, te_items, te_labels, role_of_term = _synthetic_shard_separated_task()
    typer = SelectionWeightedShardedTyper(n_dim=256, seed=11)
    typer.fit(tr_items, tr_labels, role_of_term, roles=["ROLE_A", "ROLE_B"])
    assert typer.shard_loo_acc_["ROLE_A"] > typer.shard_loo_acc_["ROLE_B"], typer.shard_loo_acc_
    assert typer.shard_weights_["ROLE_A"] > typer.shard_weights_["ROLE_B"], typer.shard_weights_
    correct = sum(1 for it, y in zip(te_items, te_labels) if typer.predict(it) == y)
    acc = correct / len(te_items)
    assert acc >= 0.90, "synthetic shard-separated task: predict() acc=%.3f expected >= 0.90" % acc


def _selftest_determinism() -> None:
    """Same seed -> byte-identical fitted weights and predictions across two independent fits."""
    tr_items, tr_labels, te_items, _te_labels, role_of_term = _synthetic_shard_separated_task()
    t1 = SelectionWeightedShardedTyper(n_dim=256, seed=7).fit(tr_items, tr_labels, role_of_term,
                                                               roles=["ROLE_A", "ROLE_B"])
    t2 = SelectionWeightedShardedTyper(n_dim=256, seed=7).fit(tr_items, tr_labels, role_of_term,
                                                               roles=["ROLE_A", "ROLE_B"])
    assert t1.shard_loo_acc_ == t2.shard_loo_acc_
    assert t1.shard_weights_ == t2.shard_weights_
    p1 = [t1.predict(it) for it in te_items]
    p2 = [t2.predict(it) for it in te_items]
    assert p1 == p2, "predict() not deterministic given the same seed"


def _selftest_predict_select_and_composed_run() -> None:
    """predict_select / predict_composed execute without crashing and return valid labels."""
    tr_items, tr_labels, te_items, _te_labels, role_of_term = _synthetic_shard_separated_task()
    typer = SelectionWeightedShardedTyper(n_dim=256, seed=3).fit(
        tr_items, tr_labels, role_of_term, roles=["ROLE_A", "ROLE_B"])
    assert typer.selected_role_ == "ROLE_A"
    for it in te_items[:5]:
        assert typer.predict_select(it) in typer.labels_
        assert typer.predict_composed(it) in typer.labels_


def _run_all_selftests() -> dict:
    _selftest_cue_weight_formula()
    _selftest_shard_weight_formula()
    _selftest_synthetic_recovers_informative_shard()
    _selftest_determinism()
    _selftest_predict_select_and_composed_run()
    return {
        "cue_weight_formula": "OK", "shard_weight_formula": "OK",
        "synthetic_shard_separation": "OK", "determinism": "OK",
        "provenance_commit": "d47643d87",
        "validated_mean_acc_role_shard_weighted_n_train_40": 0.8333333333333334,
    }


if __name__ == "__main__":
    result = _run_all_selftests()
    print("[selection_weighted_sharded_typer selftest] PASS %r" % result)
