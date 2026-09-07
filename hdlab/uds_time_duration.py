"""hdlab/uds_time_duration.py -- the UDS-Time event-type DURATION organ (typical duration, no LLM).

Landed (owner-DONE reason_over_event_time_order_and_duration_on_a_modern_gold, Q111 strategy landing
2026-09-06) as an ADDITIVE ISLAND from experiments/exp_temporal_reason_duration_udstime_v1.py.

WHAT IT COMPUTES (the brain operation, PINNED). Typical event-type duration ("how long does a war / a
glance last?") is a stored SEMANTIC-MEMORY experiential prior (Schank & Abelson scripts; Coll-Florit &
Gennari 2011 distributed/experiential duration) -- it is NOT recoverable from text distribution (Gordon &
Van Durme 2013 reporting bias: people report durations only when surprising, so text-mining LOSES to the
majority floor -- Vempala et al. 2018 got the same negative; the self-mined prior in _duration_v1 is the
located negative this organ replaces). The no-LLM SOURCE the wall-drill named: UDS-Time (Vashishtha et al.
2019) -- 32k+ predicates HUMAN-annotated with a soft distribution over an 11-point duration scale
(instant .. forever) over UD-EWT. Human annotation = NO model at inference. The bucket->log10(seconds)
midpoints are OUR-INVENTION-UNDER-TEST (swept, not adopted).

VALIDATED (same MCTACO Event-Duration harness as the located-negative mined prior): coverage 0.385 -> 0.698
(~2x), and the result moves from CI-separated BELOW the 'always-no' majority floor (-0.090) to
STATISTICALLY TIED (-0.019, CI includes 0), recovering 15.5% of the plausible durations the floor gets 0%
of. A DRILLED-WALL finding (fairness drill): the organ has REAL duration knowledge that MCTACO's
per-candidate F1/EM undersells -- native threshold-free relative-duration ranking of two REAL events =
concordance 0.6624 CI[0.6303,0.6955], CI-separated over chance. So the organ's LOAD-BEARING readout is the
RELATIVE ranking (compare), not an absolute plausibility threshold.

DEFAULT-SAFE ISLAND: a NEW module -- importing it changes NO existing behaviour, and NO reader consumes it
yet (a filed follow-on: a duration board arm on UDS-Time's own rank-correlation metric). The lookup is a
static offline asset (data/, gitignored). available()==False -> every readout abstains (None), never
raises, so an asset-less environment is safe. The offline build (python -m hdlab.uds_time_duration --build)
reconstructs the lemma prior from the on-disk UDS-Time annotations + UD-EWT (a STATIC ADMISSIBLE FOUNDATION
asset). Glass-box, stdlib+numpy, NO external LLM at inference (the invariant). ASCII.
"""
from __future__ import annotations

import json
import math
import os
from collections import defaultdict
from typing import Dict, Optional

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# the frozen mined lemma-prior (the static admissible foundation asset the organ loads at inference)
PRIOR_ASSET = os.path.join(_REPO, "data", "exp_temporal_reason_duration_udstime_v1", "uds_prior.json")
# the on-disk raw sources the --build reconstructs from (no network; both are on disk)
UDS_TIME_JSON = os.path.join(_REPO, "data", "corpora", "uds_time", "time.json")
EWT_DIR = os.path.join(_REPO, "data", "corpora", "ud_english_ewt")

# UDS-Time 11-point scale bucket -> representative log10(seconds) midpoint (OUR-INVENTION-UNDER-TEST)
BUCKET_LOG_S = {
    "dur-instant": 0.0, "dur-seconds": 1.0, "dur-minutes": 2.3, "dur-hours": 3.5, "dur-days": 4.9,
    "dur-weeks": 5.8, "dur-months": 6.4, "dur-years": 7.5, "dur-decades": 8.5, "dur-centuries": 9.5,
    "dur-forever": 11.0,
}


class UDSTimeDuration:
    """A glass-box event-type duration lookup: lemma -> typical log10(seconds) (median over the human
    UDS-Time annotations joined to UD-EWT). The load-bearing readout is RELATIVE ranking (compare)."""

    def __init__(self, prior: Dict[str, Dict[str, float]]) -> None:
        # prior: lemma -> {"median_log_s": float, "n": int}
        self.prior = prior or {}

    # ---- load / availability -------------------------------------------------
    @classmethod
    def load(cls, path: str = PRIOR_ASSET) -> "UDSTimeDuration":
        """Load the frozen mined lemma-prior. Returns an EMPTY (abstaining) organ if the asset is absent
        (degrade gracefully -- an asset-less environment is safe)."""
        if not os.path.exists(path):
            return cls({})
        with open(path, encoding="ascii") as fh:
            meta = json.load(fh)
        return cls(meta.get("prior", {}))

    @staticmethod
    def available(path: str = PRIOR_ASSET) -> bool:
        return os.path.exists(path)

    def coverage(self) -> int:
        """Number of lemmas with a typical-duration entry."""
        return len(self.prior)

    # ---- readouts ------------------------------------------------------------
    def typical_log_seconds(self, lemma: Optional[str]) -> Optional[float]:
        """Typical event duration for `lemma` in log10(seconds); None if the lemma is uncovered."""
        if not lemma:
            return None
        rec = self.prior.get(str(lemma).lower())
        return float(rec["median_log_s"]) if rec else None

    def compare(self, a: Optional[str], b: Optional[str]) -> Optional[int]:
        """RELATIVE duration (the load-bearing readout): +1 if a typically lasts longer than b, -1 if
        shorter, 0 if equal, None if either lemma is uncovered."""
        la, lb = self.typical_log_seconds(a), self.typical_log_seconds(b)
        if la is None or lb is None:
            return None
        return 1 if la > lb else (-1 if la < lb else 0)

    def longer(self, a: Optional[str], b: Optional[str]) -> Optional[bool]:
        """True iff a typically lasts longer than b; None if undecidable / uncovered."""
        c = self.compare(a, b)
        return None if c is None else (c > 0)

    def plausible(self, lemma: Optional[str], duration_log_s: float, tol: float = 0.7) -> Optional[bool]:
        """Is a candidate duration plausible for the event type? |log(candidate) - typical| <= tol orders
        of magnitude. None if the lemma is uncovered (caller backs off to the majority prior)."""
        typ = self.typical_log_seconds(lemma)
        if typ is None:
            return None
        return abs(float(duration_log_s) - typ) <= tol


# ---------------------------------------------------------------------------
# Offline build: reconstruct the lemma prior from on-disk UDS-Time + UD-EWT (no network, no LLM).
# Byte-faithful to experiments/exp_temporal_reason_duration_udstime_v1.build_uds_prior.
# ---------------------------------------------------------------------------
def _load_ewt_sentences() -> Dict[str, list]:
    """Positional-ordered UD-EWT sentences per split: {split: [ {tokid:int -> (form, lemma, upos)} ]}."""
    out: Dict[str, list] = {}
    for split, fname in (("train", "en_ewt-ud-train.conllu"), ("dev", "en_ewt-ud-dev.conllu"),
                         ("test", "en_ewt-ud-test.conllu")):
        path = os.path.join(EWT_DIR, fname)
        if not os.path.exists(path):
            continue
        sents = []
        cur: Dict[int, tuple] = {}
        for line in open(path, encoding="utf-8", errors="replace"):
            line = line.rstrip("\n")
            if not line:
                if cur:
                    sents.append(cur); cur = {}
                continue
            if line.startswith("#"):
                continue
            cols = line.split("\t")
            if len(cols) < 4 or "-" in cols[0] or "." in cols[0]:
                continue
            cur[int(cols[0])] = (cols[1], cols[2], cols[3])
        if cur:
            sents.append(cur)
        out[split] = sents
    return out


def build_prior(verbs_only: bool = True, out_path: str = PRIOR_ASSET) -> Dict:
    """Reconstruct the lemma duration prior from the on-disk UDS-Time annotations + UD-EWT and freeze it.
    A STATIC ADMISSIBLE FOUNDATION asset (human-annotated durations; NO LLM). Returns the meta dict."""
    if not os.path.exists(UDS_TIME_JSON):
        raise FileNotFoundError("UDS-Time annotations absent: %s (fetch via the solver cell --refetch)" % UDS_TIME_JSON)
    with open(UDS_TIME_JSON, encoding="utf-8") as fh:
        j = json.load(fh)
    datakey = [k for k in j if k != "metadata"][0]
    D = j[datakey]
    ewt = _load_ewt_sentences()
    buckets = defaultdict(list)
    n_nodes = n_mapped = n_verb = 0
    for gkey, nodes in D.items():
        parts = gkey.split("-")                # e.g. 'ewt-train-2255'
        if len(parts) < 3 or parts[0] != "ewt":
            continue
        split = parts[1]
        try:
            sidx = int(parts[2])
        except ValueError:
            continue
        sents = ewt.get(split)
        if not sents or not (1 <= sidx <= len(sents)):
            continue
        sent = sents[sidx - 1]
        for nkey, val in nodes.items():
            n_nodes += 1
            if "-pred-" not in nkey:
                continue
            try:
                tok = int(nkey.split("-pred-")[-1])
            except ValueError:
                continue
            if tok not in sent:
                continue
            form, lemma, upos = sent[tok]
            n_mapped += 1
            if verbs_only and upos != "VERB":
                continue
            n_verb += 1
            tv = val.get("time", {})
            best = max(BUCKET_LOG_S, key=lambda b: tv.get(b, {}).get("value", -9))
            buckets[lemma.lower()].append(BUCKET_LOG_S[best])
    prior = {lem: {"median_log_s": float(np.median(v)), "n": len(v)}
             for lem, v in buckets.items() if len(v) >= 1}
    meta = {"prior": prior, "n_lemmas": len(prior), "n_nodes": n_nodes, "n_mapped": n_mapped,
            "n_verb_nodes": n_verb}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="ascii") as fh:
        json.dump(meta, fh)
    return meta


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true", help="reconstruct the lemma prior from UDS-Time + UD-EWT")
    a = ap.parse_args()
    if a.build:
        m = build_prior()
        print("[hdlab.uds_time_duration] built prior: %d lemmas (%d verb nodes mapped) -> %s"
              % (m["n_lemmas"], m["n_verb_nodes"], PRIOR_ASSET))
    else:
        org = UDSTimeDuration.load()
        print("[hdlab.uds_time_duration] available=%s coverage=%d lemmas" % (org.available(), org.coverage()))
        for pair in (("war", "glance"), ("meeting", "war"), ("blink", "vacation")):
            print("  typical(%s)=%s  typical(%s)=%s  longer(%s,%s)=%s"
                  % (pair[0], org.typical_log_seconds(pair[0]), pair[1], org.typical_log_seconds(pair[1]),
                     pair[0], pair[1], org.longer(*pair)))
