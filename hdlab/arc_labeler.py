"""Glass-box UD dependency-RELATION labeler -- adds deprel LABELS on top of the unlabeled arc parser.

Front-end Asset 3 for the reader-parser pipeline. The persisted hdlab.arc_parser produces UNLABELED
heads (UAS ~0.7868); it cannot tell a subject from an object. This module classifies each arc's UD
RELATION LABEL (nsubj / obj / obl / nsubj:pass / obl:agent / amod / det / ...) with a multiclass averaged
perceptron (Collins-style averaging, the same learning discipline as hdlab.arc_parser.train_arc and
hdlab.pos_tagger), so a candidate-generation stage can restrict patient candidates to the labeled patient
roles (obj / nsubj:pass) instead of "any nominal dependent".

Design: labeling an arc is a per-arc MULTICLASS problem given the head structure (not a Viterbi sequence
decode), so this uses a lightweight dict-keyed averaged multiclass perceptron -- glass-box + json-persistable
exactly like hdlab.pos_tagger (weights are "feature~label" -> float). Subtypes are collapsed to the main UD
relation EXCEPT nsubj:pass and obl:agent, which are kept in full because they carry the patient/agent
distinction the whole asset exists to recover.

Public API:
  train_label(train_sents, epochs, ...) -> ArcLabeler                 # train from UD (id,form,upos,head,deprel)
  ArcLabeler.load(path) / .save(path)                                 # persist json (glass-box)
  labeler.label(tokens, pos, heads) -> Dict[dep_idx, deprel]          # label each arc under given heads
  labeler.label_accuracy(gold_sents) -> (acc, n_correct, n)          # labeling accuracy GIVEN gold arcs
  norm_label(deprel) -> str                                           # subtype-collapse (keeps :pass / :agent)

NO LLM. NO nltk. NO torch. numpy + pure-python only. ASCII-only.
"""
from __future__ import annotations

__bf_status__ = 'NOT_BF'   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = '2026-09-09 BF-certification pass (operation/math read of the pinned computation + key ops; strategy first-hand)'
__bf_note__ = 'multiclass averaged-perceptron dependency-RELATION labeler, FROZEN supervised hard-decode -- NOT_BF for the fine non-argument relations it still decides (compound/appos/conj/nmod:poss...). 2026-09-12: the ARGUMENT roles of nominal dependents (nsubj/obj/nsubj:pass/obl:agent/obl) are decided by the Competition-Model organ graded_role_assigner.coarse_roles (COMPETITION_ROLES overlay, BF_SPIRIT, learned cue validities)'
__bf_corrections__ = []


import json
from collections import defaultdict
from typing import Dict, List, Sequence, Tuple

# Subtypes collapsed to main relation EXCEPT these -- they carry the patient/agent distinction.
KEEP_FULL = {"nsubj:pass", "obl:agent", "csubj:pass"}


# ======================================================================================================
# VOICE POST-CORRECTION (landed 2026-09-12 from owner-DONE pri-7 `harm_help_valence_is_a_fitted_verb_list…`, upstream
# labeler fix; SIGNAL_FLOW_MAP.md §2). THE DEFECT: the frozen perceptron systematically labels the SUBJECT of a passive
# clause `nsubj` (active subject) when it is `nsubj:pass` (the logical object promoted to surface subject), so every
# consumer that reads "obj (active) / nsubj:pass (passive) = the undergoer" loses passive patients.
# THE OPERATION: passive morphology (a be/get auxiliary + the past participle) demotes the logical object to the surface
# subject -- definitional English voice diathesis; the extended Argument Dependency Model (Bornkessel-Schlesewsky &
# Schlesewsky 2006/2009) has comprehenders use morphosyntactic voice marking EARLY as a fast actor/undergoer cue. Label
# (strategy, 2026-09-12 research note RESEARCH_harm_help_and_selectional_math): a deterministic GRAMMATICAL rule
# consistent with eADM -- not a neural-pinning claim. Deterministic, glass-box, no learned part.
# MEASURED (solver, witness test_fd_harm_help_learned_extraction 3/3): undergoer-label recall 0.7778 -> 0.7817 with
# precision HELD; every live label consumer already distinguishes nsubj:pass (map §2), so the correction feeds them
# the label they already want. The obj/obl case is NOT corrected here (over-fires; it needs the learned ranker).
# ======================================================================================================
VOICE_CORRECTION: bool = True     # the LIVE default (owner-DONE; measured no-regress, patient recall up)
_BE_AUX = {"be", "is", "are", "was", "were", "been", "being", "am", "get", "got", "gotten"}


def label_voice_correct(toks: Sequence[str], pos: Sequence[str], heads: Dict[int, int],
                        labels: Dict[int, str]) -> Dict[int, str]:
    """An `nsubj` whose head is a VERB/AUX carrying a be/get auxiliary child and a past-participle form -> `nsubj:pass`.
    Indices 1-based (dep -> head); `labels` is not mutated."""
    n = len(toks)
    out = dict(labels)
    ch: Dict[int, list] = {}
    for i in range(1, n + 1):
        ch.setdefault(heads.get(i, 0), []).append(i)
    for i in range(1, n + 1):
        h = heads.get(i, 0)
        if h and pos[h - 1] in ("VERB", "AUX") and out.get(i) == "nsubj":
            aux = [c for c in ch.get(h, []) if pos[c - 1] == "AUX" and toks[c - 1].lower() in _BE_AUX]
            if aux and toks[h - 1].lower().endswith(("ed", "en")):
                out[i] = "nsubj:pass"
    return out


# ======================================================================================================
# COMPETITION-MODEL ARGUMENT ROLES (landed 2026-09-12, strategy; the first build of the upstream math-BF pass along the
# affected-entity chain -- notes/SIGNAL_LOSS_LEDGER_affected_entity_chain.md, rung 5). THE DEFECT: this frozen perceptron is
# the LOSSY rung of the pronoun-undergoer decision (labels alone -0.0369 of the -0.0705 parse loss; BY_AGENT 0.106,
# PASS_SUBJ 0.581; 25% of gold undergoer pronouns labelled out of the undergoer set). THE OPERATION: grammatical roles
# by PARALLEL CUE COMPETITION (Bates & MacWhinney) with strengths = learned cue validities (hdlab.graded_role_assigner
# .coarse_roles; asset coarse_role_validities_ud_ewt.json from UD-EWT train). The competition decides the ARGUMENT roles
# of nominal dependents (a perceptron argument label the competition rejects becomes 'dep'; probe v13: the competition's own
# abstention beats falling back to the perceptron, +0.0235 CI-sep vs +0.0084 n.s.); fine non-argument relations are kept.
# MEASURED: held-out UD-EWT test (gold heads) coarse-role accuracy 0.872 (SUBJ 0.925 / OBJ 0.951 / PASS_SUBJ 0.769 /
# BY_AGENT 0.944 / OBL 0.887 / OTHER 0.920); the 596-item pronoun-undergoer decision (probe v13, predicted POS+heads):
# 0.4698 -> 0.4933 = +0.0235 CI95 [+0.0033, +0.0436] vs the perceptron (a third of the -0.0705 parse loss recovered).
# ======================================================================================================
COMPETITION_ROLES: bool = True
_ARG_ROLES = {"nsubj", "obj", "nsubj:pass", "obl:agent", "obl", "iobj"}
# every relation inside the competition's CLASS SPACE (SUBJ / OBJ / PASS_SUBJ / BY_AGENT / OBL incl. bare nmod) is the
# competition's to decide: a perceptron label in this space that the competition rejects (OTHER) becomes 'dep'. Measured
# (probe v14, 596 items): keeping the perceptron's `nmod` where the competition says OTHER cost -0.0168 CI-sep -- the
# downstream decision consumes nmod as an object-class role; the competition's OTHER is the correct verdict.
_CM_CLASS_BASES = {"nsubj", "csubj", "obj", "iobj", "obl", "nmod"}


def _in_competition_space(dep: str) -> bool:
    if not dep or dep == "nmod:poss":
        return False          # a possessive is a determiner-like modifier, outside the competition's class space
    return dep.split(":")[0] in _CM_CLASS_BASES


def label_competition_roles(toks: Sequence[str], pos: Sequence[str], heads: Dict[int, int],
                            labels: Dict[int, str]) -> Dict[int, str]:
    """Overlay the Competition-Model argument roles of nominal dependents on `labels` (not mutated)."""
    from hdlab.graded_role_assigner import coarse_roles
    out = dict(labels)
    for i, dep in coarse_roles(list(toks), list(pos), heads).items():
        if dep in _ARG_ROLES:
            out[i] = dep                       # the competition's argument role
        elif _in_competition_space(out.get(i)):
            out[i] = "dep"                     # the competition says NOT an argument; the perceptron's in-space label goes
        # else: a fine non-argument relation (compound / appos / conj / nmod:poss ...) -- kept from the perceptron
    return out


def norm_label(deprel: str) -> str:
    """Collapse UD subtype to the main relation, keeping nsubj:pass / obl:agent / csubj:pass in full."""
    if deprel in KEEP_FULL:
        return deprel
    return deprel.split(":", 1)[0]


def _dist(d: int) -> str:
    a = abs(d)
    return "1" if a == 1 else ("2" if a == 2 else ("3-5" if a <= 5 else ("6-10" if a <= 10 else "11+")))


def _suf(w: str) -> str:
    return w[-3:] if len(w) >= 3 else w


def arc_features(tokens: Sequence[str], pos: Sequence[str], i: int, h: int) -> List[str]:
    """Features for the arc (dependent i -> head h), 1-based indices; h==0 is ROOT. Head structure GIVEN."""
    n = len(tokens)
    dw = tokens[i - 1].lower()
    dp = pos[i - 1]
    if h == 0:
        hw, hp = "<ROOT>", "ROOT"
        d = 0
        drc = "R"
    else:
        hw, hp = tokens[h - 1].lower(), pos[h - 1]
        d = h - i
        drc = "L" if d < 0 else "R"
    db = _dist(d)
    dpl = pos[i - 2] if i >= 2 else "<S>"
    dpr = pos[i] if i < n else "<E>"
    hpl = pos[h - 2] if h >= 2 else "<S>"
    hpr = pos[h] if 0 < h < n else "<E>"
    F = [
        "b",
        "dp:" + dp, "hp:" + hp, "hp_dp:%s_%s" % (hp, dp),
        "hp_dp_dir:%s_%s_%s" % (hp, dp, drc), "hp_dp_dist:%s_%s_%s" % (hp, dp, db),
        "dw:" + dw, "hw:" + hw, "dw_dp:%s_%s" % (dw, dp), "hw_hp:%s_%s" % (hw, hp),
        "hw_dw:%s_%s" % (hw, dw), "hp_dw:%s_%s" % (hp, dw), "hw_dp:%s_%s" % (hw, dp),
        "dp_dir:%s_%s" % (dp, drc), "hp_dir:%s_%s" % (hp, drc), "dp_dist:%s_%s" % (dp, db),
        "dsuf:%s" % _suf(dw), "dsuf_hp:%s_%s" % (_suf(dw), hp), "dsuf_dp:%s_%s" % (_suf(dw), dp),
        "dpl_dp:%s_%s" % (dpl, dp), "dpr_dp:%s_%s" % (dpr, dp),
        "hpl_hp:%s_%s" % (hpl, hp), "hpr_hp:%s_%s" % (hpr, hp),
        "ctx:%s_%s_%s_%s" % (dpl, dp, dpr, drc),
        "hp_dp_dpr:%s_%s_%s" % (hp, dp, dpr),
    ]
    return F


class _FastLabelPlan:
    """Byte-identical variant-C plan for ArcLabeler._predict_label -- promoted VERBATIM (Q111) from
    experiments/exp_arc_labeler_fastpath_v1.FastLabelPlan (owner-DONE add_the_arc_labeler_fast_scoring_path,
    2026-09-05). Built once from the averaged weights: precompute feat -> [(label_idx, weight)] (split each key
    on the LAST '~' -- labels never contain '~', verified 0/36 on the landed asset, so the split is EXACT and
    byte-identity is UNCONDITIONAL in the weights, not a lucky sample); per arc accumulate present weights into
    per-label lanes IN FEATURE ORDER and argmax IN LABEL ORDER -> the float sum is bit-identical to stock _score
    and the first-max strict-'>' tie-break is identical. ~9x faster than the stock 36-label rescan (labeler is
    ~54% of a full-length-doc read). The lane[] it materializes IS the pinned Competition-Model / FLMP net
    activation (graded_competition.net_activation), so the SAME refactor enables the graded readout (label_graded)
    at zero cost -- argmax byte-identical (MAP-optimality), the normalized entropy a gold-free error signal."""

    def __init__(self, weights, labels):
        self.labels = list(labels)
        self.n = len(self.labels)
        li = {l: i for i, l in enumerate(self.labels)}
        self.contrib = {}                      # feat -> [(label_idx, weight)]
        for key, val in weights.items():
            feat, lab = key.rsplit("~", 1)     # labels never contain '~' (verified); features never do either
            self.contrib.setdefault(feat, []).append((li[lab], val))

    def predict(self, feats):
        lane = [0.0] * self.n
        c = self.contrib
        for f in feats:                        # feature order preserved -> per-lane sum order == stock
            lst = c.get(f)
            if lst:
                for k, wv in lst:
                    lane[k] += wv
        best_i = 0
        best_s = lane[0]
        for i in range(1, self.n):             # label order preserved -> identical first-max tie-break
            if lane[i] > best_s:
                best_s = lane[i]; best_i = i
        return self.labels[best_i]

    def lanes(self, feats):
        """The per-label net activation (sum of present feature-weights per label, feature order). Same
        accumulation predict() does; exposed for the graded readout (argmax(lanes) == predict, MAP-optimality)."""
        lane = [0.0] * self.n
        c = self.contrib
        for f in feats:
            lst = c.get(f)
            if lst:
                for k, wv in lst:
                    lane[k] += wv
        return lane


class ArcLabeler:
    """Multiclass averaged perceptron labeling each arc with its UD relation, given the head structure."""

    def __init__(self, labels: Sequence[str], weights: Dict[str, float] | None = None):
        self.labels = list(labels)
        self.weights: Dict[str, float] = dict(weights) if weights else {}
        self._fast: "_FastLabelPlan | None" = None   # byte-identical fast plan, built lazily on first label()

    def _score(self, feats: Sequence[str], lab: str) -> float:
        w = self.weights
        s = 0.0
        for f in feats:
            v = w.get(f + "~" + lab)
            if v is not None:
                s += v
        return s

    def _predict_label(self, feats: Sequence[str]) -> str:
        """The stock 36-label rescan -- KEPT UNCHANGED as the training path AND the byte-identity reference
        (the fast path in label() is provably identical to this; see _FastLabelPlan)."""
        best_l = self.labels[0]
        best_s = float("-inf")
        for lab in self.labels:
            s = self._score(feats, lab)
            if s > best_s:
                best_s = s
                best_l = lab
        return best_l

    def _ensure_fast(self) -> "_FastLabelPlan":
        """Lazily build + cache the byte-identical fast plan (idempotent), mirroring PosTagger._ensure_fast."""
        if self._fast is None:
            self._fast = _FastLabelPlan(self.weights, self.labels)
        return self._fast

    def label(self, tokens: Sequence[str], pos: Sequence[str], heads: Dict[int, int], *,
              voice_correction: "bool | None" = None, competition_roles: "bool | None" = None) -> Dict[int, str]:
        """Label each arc dep->head under the GIVEN head map. Returns {dep_idx(1-based): deprel}. Routes through
        the byte-identical fast plan (~9x); output is identical to _predict_label for ANY weights (theorem). Then
        the VOICE post-correction (module default VOICE_CORRECTION; pass False for the raw perceptron labels)."""
        plan = self._ensure_fast()
        out: Dict[int, str] = {}
        n = len(tokens)
        for i in range(1, n + 1):
            h = heads.get(i, 0)
            if h is None or h < 0 or h > n:
                h = 0
            feats = arc_features(tokens, pos, i, h)
            out[i] = plan.predict(feats)
        use = VOICE_CORRECTION if voice_correction is None else voice_correction
        out = label_voice_correct(tokens, pos, heads, out) if use else out
        use_cm = COMPETITION_ROLES if competition_roles is None else competition_roles
        return label_competition_roles(tokens, pos, heads, out) if use_cm else out

    def label_graded(self, tokens: Sequence[str], pos: Sequence[str], heads: Dict[int, int]) -> Dict[int, tuple]:
        """OPT-IN brain-faithful readout (default-off; NO consumer wired). Returns {dep_idx: (argmax_label,
        posterior[np], normalized_entropy)} -- the graded label competition the brain maintains (Hale/Levy;
        Kiani-Shadlen), materialized for free off the fast plan's lane[]. BYTE-SAFE: argmax(posterior) ==
        label()'s pick (MAP-optimality). normalized_entropy is a validated gold-free difficulty signal
        (AUC 0.930 vs info-free twin 0.481). Reuses hdlab.graded_competition.softmax."""
        import numpy as np
        from hdlab.graded_competition import softmax
        plan = self._ensure_fast()
        out: Dict[int, tuple] = {}
        n = len(tokens)
        logn = float(np.log(plan.n)) if plan.n > 1 else 1.0
        for i in range(1, n + 1):
            h = heads.get(i, 0)
            if h is None or h < 0 or h > n:
                h = 0
            lane = plan.lanes(arc_features(tokens, pos, i, h))
            post = softmax(lane)
            ent = float(-(post * np.log(post + 1e-12)).sum()) / logn
            out[i] = (plan.labels[int(np.argmax(post))], post, ent)
        return out

    def label_accuracy(self, gold_sents: Sequence[Sequence[tuple]], maxlen: int = 50) -> Tuple[float, int, int]:
        """Labeling accuracy GIVEN gold arcs: predict each arc's label under gold heads, compare to gold deprel."""
        correct = 0
        tot = 0
        for s in gold_sents:
            if not (1 <= len(s) <= maxlen):
                continue
            tokens = [t[1] for t in s]
            pos = [t[2] for t in s]
            for i in range(1, len(s) + 1):
                gold_h = s[i - 1][3]
                if gold_h < 0 or gold_h > len(s):
                    continue
                feats = arc_features(tokens, pos, i, gold_h)
                pred = self._predict_label(feats)
                gold_lab = norm_label(s[i - 1][4])
                correct += int(pred == gold_lab)
                tot += 1
        return (correct / tot if tot else 0.0, correct, tot)

    def save(self, path: str) -> None:
        """Persist labels + averaged weights to json (glass-box, inspectable)."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"labels": self.labels, "weights": self.weights}, f)

    @classmethod
    def load(cls, path: str) -> "ArcLabeler":
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        return cls(d["labels"], {k: float(v) for k, v in d["weights"].items()})


def train_label(
    train_sents: Sequence[Sequence[tuple]],
    epochs: int = 8,
    seed: int = 1031,
    maxlen: int = 50,
    min_label_count: int = 30,
) -> ArcLabeler:
    """Train multiclass averaged perceptron on UD (id,form,upos,head,deprel) sentences.

    Labels: norm_label(deprel); relations occurring < min_label_count times are folded into 'dep'
    (the UD catch-all), keeping the frequent + patient-critical relations sharp.
    """
    import numpy as np

    train = [s for s in train_sents if 1 <= len(s) <= maxlen]
    # label set from frequency
    freq: Dict[str, int] = defaultdict(int)
    for s in train:
        for t in s:
            if 0 <= t[3] <= len(s):
                freq[norm_label(t[4])] += 1
    keep = {lab for lab, c in freq.items() if c >= min_label_count}
    keep |= {"obj", "nsubj", "nsubj:pass", "obl", "obl:agent", "iobj", "dep", "root"}
    labels = sorted(keep)

    def lab_of(deprel: str) -> str:
        nl = norm_label(deprel)
        return nl if nl in keep else "dep"

    # precompute features + gold labels per arc
    data = []  # list of (feats, gold_label)
    for s in train:
        tokens = [t[1] for t in s]
        pos = [t[2] for t in s]
        arcs = []
        for i in range(1, len(s) + 1):
            gh = s[i - 1][3]
            if gh < 0 or gh > len(s):
                continue
            arcs.append((arc_features(tokens, pos, i, gh), lab_of(s[i - 1][4])))
        data.append(arcs)

    w: Dict[str, float] = defaultdict(float)
    cw: Dict[str, float] = defaultdict(float)
    c = 1
    rng = np.random.default_rng(seed)
    lab = ArcLabeler(labels)
    lab.weights = w  # share dict during training for scoring

    for ep in range(epochs):
        for si in rng.permutation(len(data)):
            for feats, gold in data[si]:
                pred = lab._predict_label(feats)
                if pred != gold:
                    for f in feats:
                        kg = f + "~" + gold
                        kp = f + "~" + pred
                        w[kg] += 1.0
                        cw[kg] += c
                        w[kp] -= 1.0
                        cw[kp] -= c
                c += 1

    averaged = {f: w[f] - cw[f] / c for f in w}
    return ArcLabeler(labels, averaged)


# ============================================================
# Live-query self-test
# ============================================================
def _self_test() -> bool:
    """Tiny synthetic self-test: labeler must separate subject from object under gold heads."""
    # sentences: (id, form, upos, head, deprel). "dog bites man": dog=nsubj, bites=root, man=obj.
    def mk(triples):
        return [(k + 1, w, p, h, r) for k, (w, p, h, r) in enumerate(triples)]

    train = []
    for subj, obj in [("dog", "man"), ("cat", "bird"), ("boy", "ball"), ("girl", "cup"), ("man", "dog")]:
        train.append(mk([(subj, "NOUN", 2, "nsubj"), ("bit", "VERB", 0, "root"), (obj, "NOUN", 2, "obj")]))
        train.append(mk([("the", "DET", 2, "det"), (subj, "NOUN", 3, "nsubj"),
                         ("saw", "VERB", 0, "root"), (obj, "NOUN", 3, "obj")]))
    lab = train_label(train, epochs=15, min_label_count=1)
    tokens = ["fox", "bit", "hen"]
    pos = ["NOUN", "VERB", "NOUN"]
    heads = {1: 2, 2: 0, 3: 2}
    got = lab.label(tokens, pos, heads)
    print("[selftest] label(fox bit hen) =", got)
    ok = (got[1] == "nsubj" and got[2] == "root" and got[3] == "obj")
    assert ok, "SELF-TEST FAIL: labeler did not separate nsubj(pre-verb) from obj(post-verb)"
    # round-trip persistence
    import tempfile
    import os
    tp = os.path.join(tempfile.gettempdir(), "arc_labeler_selftest.json")
    lab.save(tp)
    lab2 = ArcLabeler.load(tp)
    assert lab2.label(tokens, pos, heads) == got, "SELF-TEST FAIL: persistence round-trip changed labels"
    os.remove(tp)
    print("[selftest] PASS: subject/object separated + persistence round-trips")
    return True


if __name__ == "__main__":
    print("=== ARC LABELER -- live-query self-test ===")
    _self_test()
