"""Gates and measurement for goal_bearing_modern_eval_v2 (the eval_bank_too_small solver task).

Durable, reusable acceptance criteria for the new bank. Every function here is READ-ONLY with
respect to the goal-typing organ: it NEVER calls the outcome-valence predictor and never reads any
per-item MET/UNMET organ output (contamination rule). It imports:
  - tools.floor_battery  -> the EXACT cheat features the acceptance test scores (shared definition).
  - hdlab.goal_owner_select -> the production positional-OWNER resolver, used only as fairness
    FLOORS (predicts a roster entity, never the outcome valence). Imported, never written.

Gates:
  verbatim_coverage   -- item text must be a (normalized) substring-ish of its cited source. Kills
                         any hallucinated or paraphrased gold text produced by an annotator.
  roster_gate         -- every roster key / goal_owner / gold_outcome_owner is a single alpha token
                         present in the item's own trimmed text (7 of the original 44 failed this).
  cheat_report        -- floor_battery on the scorable subset; PASS iff text_length_chars AND both
                         negation counters sit at their own permutation nulls (clears_own_null False).
  positional_baselines-- recency / first_mention / nearest_subject / majority + all-four-defeated.
  curate_balanced     -- stratified matched pruning so length and negation are ~orthogonal to label.

Run `python verification/goal_bearing_eval_v2_gates.py --self-test`.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")

import json
import re
import sys
from collections import defaultdict, Counter
from typing import Dict, List, Sequence, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# EXACT cheat features the acceptance test uses -- shared definition, not a re-implementation.
from tools.floor_battery import FEATURES, NEG, _last_sentence, run_battery  # noqa: E402


# --------------------------------------------------------------------------- text normalization
_CURLY = {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "--", "…": "...", " ": " ",
}


def normalize_display(s: str) -> str:
    """Curly punctuation -> ASCII, whitespace collapsed. This is the readable form stored in `text`."""
    for k, v in _CURLY.items():
        s = s.replace(k, v)
    return re.sub(r"\s+", " ", s).strip()


def _match_tokens(s: str) -> List[str]:
    """Lowercase alnum-apostrophe word tokens, for source-overlap matching (ignores punctuation/quoting)."""
    return re.findall(r"[a-z0-9']+", normalize_display(s).lower())


def _shingles(tokens: Sequence[str], n: int = 4) -> set:
    if len(tokens) < n:
        return {tuple(tokens)} if tokens else set()
    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


# --------------------------------------------------------------------------- verbatim gate
def source_shingles(source_text: str, n: int = 4) -> set:
    """All word-n-grams of a source file, for verbatim checking of items cited to it."""
    return _shingles(_match_tokens(source_text), n)


def verbatim_coverage(item_text: str, src_shingles: set, n: int = 4) -> float:
    """Fraction of the item's word-n-grams that occur verbatim in the source. 1.0 = fully verbatim;
    light trimming / bracketed editorial bridges / ellipsis lower it slightly. A hallucinated or
    paraphrased passage scores near 0. Bracketed [editorial] spans are excluded before checking."""
    stripped = re.sub(r"\[[^\]]*\]", " ", item_text)  # drop clearly-delimited editorial bridges
    toks = _match_tokens(stripped)
    sh = _shingles(toks, n)
    if not sh:
        return 0.0
    hit = sum(1 for g in sh if g in src_shingles)
    return hit / len(sh)


# --------------------------------------------------------------------------- roster structural gate
def _ordered_tokens_local(text: str) -> List[str]:
    return re.findall(r"[a-z']+", normalize_display(text).lower())


def roster_gate(item: dict) -> Tuple[bool, str]:
    """Every roster key, goal_owner, gold_outcome_owner is a single [a-z'] token present in `text`."""
    toks = set(_ordered_tokens_local(item.get("text", "")))
    keys = list(item.get("roster", {}).keys())
    for k in keys:
        if not re.fullmatch(r"[a-z']+", k):
            return False, f"roster key {k!r} is not a single alpha token"
        if k not in toks:
            return False, f"roster key {k!r} does not occur in text"
    for field in ("goal_owner", "gold_outcome_owner"):
        v = item.get(field)
        if v is None:
            return False, f"missing {field}"
        if v not in item.get("roster", {}):
            return False, f"{field}={v!r} not in roster"
        if v not in toks:
            return False, f"{field}={v!r} does not occur in text"
    return True, "ok"


# --------------------------------------------------------------------------- cheat battery
def _scorable(items: Sequence[dict]) -> List[dict]:
    return [it for it in items if it.get("outcome_in_lexicon") is False]


def cheat_report(items: Sequence[dict], on: str = "scorable") -> dict:
    """floor_battery on the chosen population. PASS iff text_length_chars and BOTH negation counters
    sit at their own nulls (clears_own_null False). `on` in {'scorable','all'}."""
    pop = _scorable(items) if on == "scorable" else list(items)
    texts = [it["text"] for it in pop]
    labels = [1 if it["gold_outcome_polarity"] == "met" else 0 for it in pop]
    rep = run_battery(texts, labels)
    rows = {r["floor"]: r for r in rep["rows"]}
    watched = ["text_length_chars", "negation_cue_last_sentence", "negation_cue_whole_text",
               "text_length_words"]
    cheats_at_null = all(not rows[f]["clears_own_null"] for f in watched if f in rows)
    return {
        "population": on, "n": rep["n"], "majority_floor": rep["majority_floor"],
        "strongest": rep["strongest"],
        "strongest_that_clears_its_own_null": rep["strongest_that_clears_its_own_null"],
        "watched": {f: rows[f] for f in watched if f in rows},
        "all_watched_at_their_null": bool(cheats_at_null),
        "rows": rep["rows"],
    }


# --------------------------------------------------------------------------- balance metrics
def _perm_diff_p(values: np.ndarray, labels: np.ndarray, n_perm: int = 2000, seed: int = 7) -> float:
    """Two-sided permutation p for difference in MEANS of `values` between the two label classes.
    A LARGE p (>~0.2) means the feature does not separate the classes -- what we want for a cheat."""
    rs = np.random.default_rng(seed)
    obs = abs(values[labels == 1].mean() - values[labels == 0].mean())
    cnt = 0
    for _ in range(n_perm):
        p = rs.permutation(labels)
        if abs(values[p == 1].mean() - values[p == 0].mean()) >= obs - 1e-12:
            cnt += 1
    return (cnt + 1) / (n_perm + 1)


def balance_metrics(items: Sequence[dict], on: str = "scorable") -> dict:
    pop = _scorable(items) if on == "scorable" else list(items)
    y = np.array([1 if it["gold_outcome_polarity"] == "met" else 0 for it in pop])
    lens = np.array([float(len(it["text"])) for it in pop])
    neg_last = np.array([float(len(NEG.findall(_last_sentence(it["text"])))) for it in pop])
    neg_whole = np.array([float(len(NEG.findall(it["text"]))) for it in pop])

    def rate(flagvec):
        return {"met": float((flagvec[y == 1] > 0).mean()) if (y == 1).any() else None,
                "unmet": float((flagvec[y == 0] > 0).mean()) if (y == 0).any() else None}
    return {
        "population": on, "n": len(pop), "n_met": int((y == 1).sum()), "n_unmet": int((y == 0).sum()),
        "len_mean_met": float(lens[y == 1].mean()) if (y == 1).any() else None,
        "len_mean_unmet": float(lens[y == 0].mean()) if (y == 0).any() else None,
        "len_perm_p": _perm_diff_p(lens, y),
        "neg_last_perm_p": _perm_diff_p(neg_last, y),
        "neg_last_rate": rate(neg_last),
        "neg_whole_rate": rate(neg_whole),
    }


# --------------------------------------------------------------------------- positional baselines
def positional_baselines(items: Sequence[dict]) -> dict:
    """recency / first_mention / nearest_subject / majority, reusing the production resolver.
    Predicts the OWNER (a roster entity), used as fairness floors -- NOT the outcome valence."""
    from hdlab.goal_owner_select import GeneralRecencyEntityResolver, _sentences, _ordered_tokens

    per_item = []
    correct = defaultdict(int)
    defeat_all = []
    for it in items:
        text = it["text"]
        roster = it.get("roster", {})
        gold = it.get("gold_outcome_owner")
        toks = _ordered_tokens(text)
        mentions = [t for t in toks if t in roster]
        recency = mentions[-1] if mentions else None
        first = mentions[0] if mentions else None
        if mentions:
            cnt = Counter(mentions)
            top = max(cnt.values())
            majority = next(t for t in mentions if cnt[t] == top)  # ties -> earliest
        else:
            majority = None
        sents = _sentences(text)
        near = None
        if len(sents) >= 2:
            # nearest_subject = subject of the sentence IMMEDIATELY before the outcome sentence
            # (sents[-2]) only. Prior sentences are fed in to build the resolver's recency state for
            # pronoun resolution, but the prediction is the last pre-final sentence's subject, even
            # if that is None. Matches the committed v1 baseline (byte-identical to its behaviour).
            resolver = GeneralRecencyEntityResolver(roster)
            pre = sents[:-1]
            for s in pre:
                near = resolver.subject_entity(s)
        preds = {"recency": recency, "first_mention": first,
                 "nearest_subject": near, "majority": majority}
        row = {"id": it.get("id"), "gold": gold, "trap_type": it.get("trap_type")}
        allcorrect = True
        for k, v in preds.items():
            c = (v == gold)
            row[f"{k}_pred"] = v
            row[f"{k}_correct"] = bool(c)
            correct[k] += int(c)
            allcorrect = allcorrect and c
        if not any(row[f"{k}_correct"] for k in preds):
            defeat_all.append(it.get("id"))
        per_item.append(row)
    n = len(items)
    overall = {k: round(correct[k] / n, 4) for k in ("recency", "first_mention",
                                                      "nearest_subject", "majority")} if n else {}
    return {"n": n, "overall_acc": overall,
            "n_defeat_all_four": len(defeat_all), "defeat_all_four_ids": defeat_all,
            "per_item": per_item}


# --------------------------------------------------------------------------- curation (balancing)
def _len_bucket(x: float, edges: Sequence[float]) -> int:
    for i, e in enumerate(edges):
        if x <= e:
            return i
    return len(edges)


def curate_balanced(pool: Sequence[dict], target_scorable: int = 120, n_len_bins: int = 3,
                    seed: int = 11) -> Tuple[List[dict], dict]:
    """Select a subset whose SCORABLE part has length and negation ~orthogonal to label, by matched
    pruning: within each (neg_last_flag, length_bin) stratum keep MET:UNMET at the global target
    ratio. Non-scorable items pass through untouched (they are not part of the acceptance test).
    Returns (selected_items, diagnostics). The yield IS the finding: a small kept-count means the
    rare quadrants (MET+negation, long UNMET) could not fill the strata -- brief failure mode (a)."""
    rs = np.random.default_rng(seed)
    scorable = [it for it in pool if it.get("outcome_in_lexicon") is False]
    passthrough = [it for it in pool if it.get("outcome_in_lexicon") is not False]

    lens = np.array([len(it["text"]) for it in scorable], dtype=float)
    if len(lens) == 0:
        return list(passthrough), {"kept_scorable": 0, "note": "no scorable items"}
    edges = [float(np.quantile(lens, q)) for q in np.linspace(0, 1, n_len_bins + 1)[1:-1]]

    def key(it):
        neg = 1 if len(NEG.findall(_last_sentence(it["text"]))) > 0 else 0
        lb = _len_bucket(len(it["text"]), edges)
        return (neg, lb)

    strata = defaultdict(lambda: {"met": [], "unmet": []})
    for it in scorable:
        cls = "met" if it["gold_outcome_polarity"] == "met" else "unmet"
        strata[key(it)][cls].append(it)

    tot_met = sum(len(s["met"]) for s in strata.values())
    tot_unmet = sum(len(s["unmet"]) for s in strata.values())
    if tot_met == 0 or tot_unmet == 0:
        return list(passthrough), {"kept_scorable": 0, "note": "one class empty"}
    ratio = tot_met / tot_unmet  # global met:unmet; kept per stratum will hold this ratio

    kept = []
    strat_diag = {}
    for k, s in strata.items():
        m, u = s["met"], s["unmet"]
        rs.shuffle(m); rs.shuffle(u)
        # keep k_u unmet and k_m = round(ratio*k_u) met, maximizing total under availability
        best = (0, 0, 0)
        for k_u in range(len(u) + 1):
            k_m = min(len(m), round(ratio * k_u))
            if k_u == 0:
                k_m = 0
            tot = k_m + k_u
            # require the per-stratum met:unmet to stay close to global ratio
            if tot > best[0]:
                best = (tot, k_m, k_u)
        _, k_m, k_u = best
        kept.extend(m[:k_m] + u[:k_u])
        strat_diag[str(k)] = {"avail_met": len(m), "avail_unmet": len(u),
                              "kept_met": k_m, "kept_unmet": k_u}

    diag = {"kept_scorable": len(kept),
            "kept_met": sum(1 for it in kept if it["gold_outcome_polarity"] == "met"),
            "kept_unmet": sum(1 for it in kept if it["gold_outcome_polarity"] != "met"),
            "target": target_scorable, "ratio_met_unmet": round(ratio, 3),
            "len_edges": [round(e) for e in edges], "strata": strat_diag,
            "met_available": tot_met, "unmet_available": tot_unmet}
    return kept + list(passthrough), diag


# --------------------------------------------------------------------------- balance refinement
def greedy_balance_prune(selected: Sequence[dict], min_scorable: int = 124) -> List[dict]:
    """After stratified curation, greedily drop the scorable item whose removal most reduces the
    residual class imbalance (length-mean gap + negation-rate gap), keeping >= min_scorable scorable
    items. Non-scorable (in-lexicon) items pass through. This kills the residual diff-in-means that
    matched-stratum selection alone leaves, so BOTH the fitted-threshold cheat (floor_battery) and a
    diff-in-means permutation test come back clean, on the scored subset and the full bank."""
    scor = [it for it in selected if it.get("outcome_in_lexicon") is False]
    rest = [it for it in selected if it.get("outcome_in_lexicon") is not False]

    def _neg(it):
        return 1 if len(NEG.findall(_last_sentence(it["text"]))) > 0 else 0

    def imbalance(items):
        y = np.array([1 if it["gold_outcome_polarity"] == "met" else 0 for it in items])
        if (y == 1).sum() == 0 or (y == 0).sum() == 0:
            return 1e9
        L = np.array([len(it["text"]) for it in items], float)
        N = np.array([_neg(it) for it in items], float)
        return abs(L[y == 1].mean() - L[y == 0].mean()) / (L.std() + 1e-9) + \
            abs(N[y == 1].mean() - N[y == 0].mean())

    while len(scor) > min_scorable:
        base = imbalance(scor)
        best_i, best_v = None, base
        for i in range(len(scor)):
            v = imbalance(scor[:i] + scor[i + 1:])
            if v < best_v:
                best_v, best_i = v, i
        if best_i is None:
            break
        scor.pop(best_i)
    return scor + rest


# --------------------------------------------------------------------------- self-test
def _self_test() -> int:
    ok = True
    # verbatim gate: a real substring scores 1.0; a hallucination near 0.
    src = "the quick brown fox jumped over the lazy dog and then ran home to sleep soundly"
    sh = source_shingles(src)
    real = verbatim_coverage("The quick brown fox jumped over the lazy dog.", sh)
    fake = verbatim_coverage("A spaceship landed on the moon carrying purple aliens.", sh)
    print(f"  verbatim: real={real:.2f} fake={fake:.2f}", end="  ")
    if real > 0.9 and fake < 0.2:
        print("PASS")
    else:
        print("FAIL"); ok = False

    # roster gate: compound key must fail, single present token must pass.
    good = {"text": "jo tried. jo won.", "roster": {"jo": "f"}, "goal_owner": "jo",
            "gold_outcome_owner": "jo"}
    bad = {"text": "she tried. she won.", "roster": {"mr_laurence": "m"}, "goal_owner": "mr_laurence",
           "gold_outcome_owner": "mr_laurence"}
    g_ok, _ = roster_gate(good)
    b_ok, b_reason = roster_gate(bad)
    print(f"  roster: good={g_ok} bad={b_ok} ({b_reason})", end="  ")
    if g_ok and not b_ok:
        print("PASS")
    else:
        print("FAIL"); ok = False

    # cheat report on a CONFOUNDED set must flag the cheats NOT at null; on a balanced set, at null.
    def mk(label, negate, pad):
        s = "She set out to do it. "
        s += ("She never managed it. " if negate else "She managed it fine. ")
        s += "word " * pad
        return {"text": s.strip(), "gold_outcome_polarity": label, "outcome_in_lexicon": False}
    # confounded: MET long+affirmative, UNMET short+negation
    conf = ([mk("met", False, 20) for _ in range(30)] + [mk("unmet", True, 2) for _ in range(30)])
    rep_c = cheat_report(conf)
    # balanced: negation and length independent of label
    bal = []
    for i in range(60):
        lab = "met" if i % 2 == 0 else "unmet"
        neg = (i % 4 < 2)          # half of each class negated
        pad = 2 + (i % 10) * 2     # length independent of label
        bal.append(mk(lab, neg, pad))
    rep_b = cheat_report(bal)
    print(f"  cheat: confounded_at_null={rep_c['all_watched_at_their_null']} "
          f"balanced_at_null={rep_b['all_watched_at_their_null']}", end="  ")
    if (not rep_c["all_watched_at_their_null"]) and rep_b["all_watched_at_their_null"]:
        print("PASS")
    else:
        print("FAIL"); ok = False

    print("SELF-TEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(_self_test())
    print(__doc__)
