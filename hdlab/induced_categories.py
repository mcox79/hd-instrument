"""hdlab.induced_categories -- the READING-ACQUIRED lexical-category inventory (the acquisition arm of the category organ).

LANDED 2026-09-13 (owner-DONE pri-15 `reading_induced_categories_merge_the_closed_classes_adv_cconj_sconj_part_and_have_no_token_
level_disambiguation`). The inventory is INDUCED from raw reading with no labels (Simple-Wikipedia, 1M lines): a function-word stratum
(the high-token-frequency clusters re-clustered on their own; Shi-Werker-Morgan / Hochmann prosodic-frequency proxy, PINNED), second-
order DIRECTIONAL frames (the categories of the left and right neighbours; Mintz 2003 joint frames, PINNED), a parallelism cue
P(cat_left == cat_right) (the coordinator), morphology inside the PPMI code (Oja/Hebbian-PCA, MODEL), a label-free predicate-follows
CLAUSE cue, and Hebbian competitive clustering (Rumelhart-Zipser, MODEL). Gold UPOS is the EVALUATION RULER ONLY (type-level
many-to-one 0.7944 at 1M vs v1 0.7385; all four closed classes ADV/CCONJ/SCONJ/PART > 0.4; shuffled twin 0.458).

WHAT LIVES HERE: the READ-TIME side -- the asset-backed inventory (word -> class; class -> the UPOS-shaped NAME gold assigned for
hand-off only) and the consumer API. The ACQUISITION (the builder) is `experiments/exp_reading_induced_categories_v2.py`
(`--lines 1000000 --k0 68 --F 240 --kfw 56 --Lmax 4 --frame-weight 0.15 --strat-top-clusters 16 --fast-svd --joint --clause`),
whose online form is the warm-started competitive learner (`OnlineStratumLearner` lineage; observe -> consolidate).

WHO CONSUMES IT (live): `hdlab.lexical_categories` (the count-based category organ) reads `word2cat` as its reading-acquired
CLUSTER CUE for rare and unknown words -- full UD-EWT test UPOS 0.9271 -> 0.9278, unknown words 0.748 -> 0.752 with this v2
inventory over v1 (`lexical_categories.INDUCED_ASSET`). The role competition's induced-class cue (`graded_role_assigner`) reads the
same kind of asset. The hand-off to the heads rung WITHOUT any label supply (`tools/build_attachment_validities.py --categories`)
measured UAS 0.44-0.45 vs 0.57 with UPOS -- the binding constraint there is ROOT (finite/matrix-verb identification; filed as pri 97),
so the count organ stays the live tagger and this inventory feeds it.
"""
from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Sequence

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET = os.environ.get("HDLAB_INDUCED_ASSET") or os.path.join(_REPO, "data", "frontend_assets", "induced_categories_v2_1m_joint_clause.json")
ASSET_V1 = os.path.join(_REPO, "data", "frontend_assets", "induced_categories_simplewiki_1m_k68.json")

__bf_status__ = "BF"
__bf_note__ = ("reading-induced lexical categories: label-free distributional induction (Harris/Mintz/Redington-Chater-Finch/Elman), "
               "function-word stratum (Shi-Werker-Morgan), Hebbian competitive clustering; gold UPOS = evaluation ruler only | "
               "2026-09-13 v2 landed (pri-15): 126 classes, closed classes separated, type m2o 0.7944")

_CACHE: Dict[str, "InducedCategories"] = {}


class InducedCategories:
    """The asset-backed inventory: word -> induced class id (str); class id -> UPOS-shaped name (hand-off naming only)."""

    def __init__(self, path: str = ASSET):
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        self.path = path
        self.word2cat: Dict[str, str] = {k.lower(): str(v) for k, v in doc["word2cat"].items()}
        self.cat_name: Dict[str, str] = {str(k): v for k, v in (doc.get("cluster_to_upos_name") or {}).items()}
        self.classes = sorted(set(self.word2cat.values()))

    def cluster_of(self, word: str) -> Optional[str]:
        return self.word2cat.get(word.lower())

    def name_of(self, word: str) -> Optional[str]:
        c = self.cluster_of(word)
        return self.cat_name.get(c) if c is not None else None

    def categorize(self, tokens: Sequence[str]) -> List[Optional[str]]:
        """UPOS-shaped names per token (None for a word the reading never covered). Type-level: the token-level causal
        readout lives in the builder (`token_many_to_one(causal=True)`); its per-token gain over the type map was +0.02."""
        return [self.name_of(t) for t in tokens]

    def coverage(self, tokens: Sequence[str]) -> float:
        return sum(1 for t in tokens if t.lower() in self.word2cat) / max(1, len(tokens))


def get(path: str = ASSET) -> InducedCategories:
    if path not in _CACHE:
        _CACHE[path] = InducedCategories(path)
    return _CACHE[path]


def word2cat(path: str = ASSET) -> Dict[str, str]:
    return get(path).word2cat


def self_test() -> bool:
    ic = get()
    assert len(ic.classes) >= 100, ("expected the 126-class v2 inventory", len(ic.classes))
    assert ic.cluster_of("and") is not None and ic.cluster_of("the") is not None, "closed-class words must be covered"
    names = [ic.name_of(w) for w in ("and", "or", "because", "if", "not", "to")]
    assert all(n is not None for n in names), names
    assert ic.name_of("and") in ("CCONJ", "SCONJ", "ADV", "PART"), ("'and' should carry a closed-class name", ic.name_of("and"))
    return True


if __name__ == "__main__":
    print("[induced_categories] self-test", "PASS" if self_test() else "FAIL")
    ic = get(); toks = "the old man and the dog walked quickly because it rained .".split()
    print(list(zip(toks, ic.categorize(toks))), "coverage %.2f" % ic.coverage(toks))
