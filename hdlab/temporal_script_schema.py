"""hdlab/temporal_script_schema.py -- the SCRIPT/SCHEMA organ for IMPLICIT-EVENT ordering (no LLM).

Landed (owner-DONE reason_over_event_time_order_and_duration_on_a_modern_gold, Q111 strategy landing
2026-09-06) as an ADDITIVE ISLAND from experiments/exp_temporal_reason_tracie_script_v1.py.

WHAT IT COMPUTES (the brain operation, PINNED). Placing an UNNARRATED event on the timeline ("when did the
paying happen relative to the leaving?") is a SCRIPT/SCHEMA knowledge-retrieval problem (Schank & Abelson
1977; Bower/Black/Turner 1979), CATEGORICALLY DISTINCT from a story-internal timeline query (which can only
order events the text actually narrates). The before/after wall-drill measured that TRACIE is ~100%
implicit-event (3.8% story-internal) -- so the timeline register structurally cannot touch it; this is the
SEPARATE organ that drill named. It is built the brain-foundational, no-LLM way: mine NARRATIVE EVENT
CHAINS (Chambers & Jurafsky 2008) from ROCStories -- the typical ORDER of event-type verb pairs across many
stories (accumulated narrative experience) -- and answer "event1 starts before/after event2" from the
typical order. Aggregate statistics, NOT story memorisation. The verb-pair order estimator + smoothing are
OUR-INVENTION.

VALIDATED (TRACIE implicit-event, mined 98,161 ROCStories -> 177,800 ordered verb-pairs): on the covered
29% the script order scores 0.6022 vs chance 0.500 and the story-internal register's 0.478 -- a real signal
(SymTime reaches 0.80 only with ~3.5M distantly-supervised examples; a glass-box chain mine gets 0.60).
Confirms implicit-event ordering is a buildable SEPARATE organ, exactly as scoped.

DEFAULT-SAFE ISLAND: a NEW module -- importing it changes NO existing behaviour, and NO reader consumes it
yet (a filed follow-on -- it answers implicit-event queries the story-internal timeline abstains on with
UNKNOWN). The frozen verb-pair counts are a static offline asset (data/, gitignored). available()==False ->
every readout abstains (None), never raises, so an asset-less environment is safe. INFERENCE is
stdlib-only (a dict lookup over the frozen counts); only the offline build (python -m
hdlab.temporal_script_schema --build) touches the shared front-end tagger to re-mine ROCStories (a STATIC
ADMISSIBLE FOUNDATION asset). Glass-box, NO external LLM at inference (the invariant). ASCII.
"""
from __future__ import annotations

import json
import os
from collections import defaultdict
from typing import Dict, List, Optional

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# the frozen ordered-verb-pair counts (the static admissible foundation asset loaded at inference)
CHAINS_ASSET = os.path.join(_REPO, "data", "exp_temporal_reason_tracie_script_v1", "chains.json")
ROC_JSONL = os.path.join(_REPO, "data", "corpora", "roc_stories", "train.jsonl")


def _lemma(w: str) -> str:
    """Light stemmer (byte-faithful to the mine): strip a common inflection so verb TYPES collapse."""
    w = w.lower()
    for suf in ("ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[: -len(suf)]
    return w


class TemporalScriptSchema:
    """Narrative event-chain order over frozen verb-pair counts. `counts["a\\tb"]` = # times event-type a
    occurred BEFORE event-type b across the mined stories. Answers the typical order of two event types."""

    def __init__(self, counts: Dict[str, int]) -> None:
        self.counts = counts or {}

    # ---- load / availability -------------------------------------------------
    @classmethod
    def load(cls, path: str = CHAINS_ASSET) -> "TemporalScriptSchema":
        """Load the frozen ordered-verb-pair counts. Returns an EMPTY (abstaining) organ if the asset is
        absent (degrade gracefully -- an asset-less environment is safe)."""
        if not os.path.exists(path):
            return cls({})
        with open(path, encoding="ascii") as fh:
            meta = json.load(fh)
        return cls(meta.get("counts", {}))

    @staticmethod
    def available(path: str = CHAINS_ASSET) -> bool:
        return os.path.exists(path)

    def n_pairs(self) -> int:
        return len(self.counts)

    # ---- readouts ------------------------------------------------------------
    def p_before(self, a: Optional[str], b: Optional[str]) -> Optional[float]:
        """P(event-type a starts before event-type b) from the mined chains; None if the pair has no
        evidence in either direction (the organ abstains rather than guessing)."""
        la, lb = self._key(a), self._key(b)
        if la is None or lb is None:
            return None
        ab = self.counts.get(la + "\t" + lb, 0)
        ba = self.counts.get(lb + "\t" + la, 0)
        if ab + ba == 0:
            return None
        return ab / (ab + ba)

    def order(self, a: Optional[str], b: Optional[str]) -> Optional[str]:
        """'before' iff a typically precedes b, 'after' iff it typically follows, None if no evidence."""
        p = self.p_before(a, b)
        if p is None:
            return None
        return "before" if p >= 0.5 else "after"

    def evidence(self, a: Optional[str], b: Optional[str]) -> int:
        """Total co-occurrence count (both directions) supporting the pair -- the confidence weight."""
        la, lb = self._key(a), self._key(b)
        if la is None or lb is None:
            return 0
        return self.counts.get(la + "\t" + lb, 0) + self.counts.get(lb + "\t" + la, 0)

    @staticmethod
    def _key(x: Optional[str]) -> Optional[str]:
        if x is None:
            return None
        tok = str(x).strip().split()
        return _lemma(tok[-1]) if tok else None


# ---------------------------------------------------------------------------
# Offline build: re-mine ordered verb-pair counts from ROCStories (uses the shared front-end tagger).
# Byte-faithful to experiments/exp_temporal_reason_tracie_script_v1.mine_chains.
# ---------------------------------------------------------------------------
def build_chains(smoke: bool = False, out_path: str = CHAINS_ASSET) -> Dict:
    """Re-mine the ordered verb-pair counts from ROCStories-train and freeze them. For each story, every
    event in sentence i precedes every event in sentence j (i<j). A STATIC ADMISSIBLE FOUNDATION asset
    (aggregate narrative statistics; NO LLM). The tagger is imported LAZILY (build-only dep)."""
    if not os.path.exists(ROC_JSONL):
        raise FileNotFoundError("ROCStories absent: %s (re-acquire via the fetch scripts)" % ROC_JSONL)
    from experiments import _temporal_ordering_multiframe as M   # build-only dep on the shared front-end tagger

    def _sentence_verbs(text: str) -> List[str]:
        ev, _tg = M.extract_events_punct(text)
        return [_lemma(e.lemma) for e in ev]

    lines = open(ROC_JSONL, encoding="utf-8").read().splitlines()
    if smoke:
        lines = lines[:4000]
    counts: Dict[str, int] = defaultdict(int)
    n = 0
    for ln in lines:
        st = json.loads(ln)
        sents = [st[f"sentence{i}"] for i in range(1, 6)]
        per = [_sentence_verbs(s) for s in sents]
        for i in range(5):
            for j in range(i + 1, 5):
                for a in per[i]:
                    for b in per[j]:
                        if a != b:
                            counts[a + "\t" + b] += 1
        n += 1
    meta = {"counts": {k: v for k, v in counts.items()}, "n_stories": n, "n_pairs": len(counts)}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="ascii") as fh:
        json.dump(meta, fh)
    return meta


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true", help="re-mine ordered verb-pair counts from ROCStories")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.build:
        m = build_chains(smoke=a.smoke)
        print("[hdlab.temporal_script_schema] built chains: %d stories -> %d ordered verb-pairs -> %s"
              % (m["n_stories"], m["n_pairs"], CHAINS_ASSET))
    else:
        org = TemporalScriptSchema.load()
        print("[hdlab.temporal_script_schema] available=%s pairs=%d" % (org.available(), org.n_pairs()))
        for pair in (("wake", "eat"), ("pay", "leave"), ("plant", "grow")):
            print("  order(%s,%s)=%s  p_before=%s  evidence=%d"
                  % (pair[0], pair[1], org.order(*pair), org.p_before(*pair), org.evidence(*pair)))
