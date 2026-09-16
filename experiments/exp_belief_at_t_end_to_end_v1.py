"""exp_belief_at_t_end_to_end_v1 -- the BELIEF/ToM dimension of the situation model, END-TO-END through the
reader's OWN extraction on prose (problem: the_belief_dimension_is_never_driven_by_the_readers_own_extraction_
on_real_prose).

THE PIVOT (DESIGN_brain_and_mapping.md; research + probes 2026-08-31): the brief's object-move event source is
absent from literary prose AND the wrong brain mechanism. Belief is a CONTENT-GENERAL propositional attitude
(Koster-Hale 2017), source-tagged (Koster-Hale 2014), fed in narrative by narrator-epistemic + testimony +
(rare) perception. This drives the PROMOTED content-general belief_timeline from the reader's OWN 3-channel
extraction, reality tracked separately, and answers "what did A believe about F at T" for a fact that may be a
LOCATION or a STATUS -- the SAME mechanism (Dowty stative inertia => generalizes across fact types).

POPULATIONS (scored separately; no number crosses them):
  MODERN  = constructed control (mechanism + generalization + corpus-age); NOT the headline.
  REAL    = hand-adjudicated LitBank belief-at-T (the headline; honest n).

ARMS (each answers belief-at-T; scored EXACT canonical value):
  BELIEF_live   -- reader's OWN extracted reality events + OWN observation gate -> promoted belief_timeline.
  BELIEF_oracle -- GOLD reality events + GOLD observation bits -> belief_timeline (the mechanism UPPER BOUND;
                   the live-vs-oracle gap = the extraction residual).
  FLOOR_reality -- always report the true/current value (the beliefless reader); wrong on false beliefs.
  FLOOR_current -- current_belief_floor: latest value the agent observed, IGNORING t (obs-gated, no time axis).
  FLOOR_lastment-- parse-free: last value_vocab word mentioned at/before the query sentence (no obs gating).
  TWIN_shuffled -- info-free: the SAME extracted events with ORDER destroyed (must LOSE).
Plus: FALSE-BELIEF discriminator (on belief!=reality items, BELIEF beats FLOOR_reality by MORE), a PERSISTENCE
distance signature, and EXTRACTION quality (reality-event recall + observation-bit accuracy) as the honest bound.

Glass-box: reality-event extraction is in-substrate (pos_tagger + arc_parser); observation gate = the promoted
perceptual_access_ledger (spaCy front-end, a parser, not an LLM). NO LLM at inference. Writes ONLY
data/exp_belief_at_t_end_to_end_v1[/ _smoke]. ASCII.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments._belief_reader as BR
from experiments.belief_at_t_gold import modern_items, load_real
from hdlab.belief_timeline import (
    WorldEvent, timeline_belief, reality_at, current_belief_floor, shuffle_order_twin,
    remap_observed_after_twin,
)

ANCHOR = "belief_at_t_end_to_end_v1"
SEED = 20260831
TWIN_R = 25


def _canon(v):
    if v is None:
        return None
    return str(v).split("-")[-1].split()[-1].lower().strip(".,:;\"'")


def _fact_head(item):
    return item["fact"]["fact_aliases"][0].lower()


def _chain_events(chain, fact_head, affects_reality):
    """WorldEvents on the SENT-INDEX time axis from a [(value, sent_idx)] chain."""
    return [WorldEvent(fact_head, _canon(v), chrono=float(si), narr=float(si),
                       kind=("initial" if k == 0 else "move"), affects_reality=affects_reality)
            for k, (v, si) in enumerate(chain)]


def _lastment_floor(item, cutoff_sent, vocab):
    """parse-free: the last value_vocab token appearing in sentences at/before cutoff_sent."""
    last = None
    for si in range(0, min(cutoff_sent, len(item["sents"]) - 1) + 1):
        for w in item["sents"][si]:
            if _canon(w) in vocab:
                last = _canon(w)
    return last


def _recall(gold_chain, ext_chain, dt=1):
    """recall = gold points recovered by an extracted point (same canonical value within +-dt sentences)."""
    gold = [(_canon(v), si) for (v, si) in gold_chain]
    ext = [(_canon(v), si) for (v, si) in ext_chain]
    matched = sum(1 for (gv, gsi) in gold if any(ev == gv and abs(esi - gsi) <= dt for (ev, esi) in ext))
    prec = sum(1 for (ev, esi) in ext if any(gv == ev and abs(gsi - esi) <= dt for (gv, gsi) in gold))
    return {"recall": matched / max(len(gold), 1), "precision": prec / max(len(ext), 1),
            "n_gold": len(gold), "n_ext": len(ext)}


def run_slice(items, led, seed=SEED):
    """Drive each item end-to-end (merged perception + belief-assertion tracks); return per-query
    predictions per arm + extraction quality. Uniform SENT-INDEX time axis."""
    rows = []
    rr_num = rr_den = 0            # reality-event recall
    br_num = br_den = 0            # belief-update recall (the agent's registered chain)
    bp_num = bp_den = 0            # belief-assertion precision
    obs_ok = obs_n = 0
    for item in items:
        sents = item["sents"]
        by_sent = {i: [] for i in range(len(sents))}
        fact_head = _fact_head(item)
        vocab = {_canon(v) for v in item["fact"]["value_vocab"]}
        # --- live: reader's OWN extraction (2 tracks merged) ---
        events_live, observed_live, agent, reality_ext, belief_assert, sources = BR.drive(
            sents, by_sent, item["fact"], item["agent"], led)
        events_live = [WorldEvent(fact_head, _canon(e.value), chrono=e.chrono, narr=e.narr,
                                  kind=e.kind, affects_reality=e.affects_reality) for e in events_live]
        reality_ext = [(_canon(v), si) for (v, si) in reality_ext]
        belief_assert = [(_canon(v), si) for (v, si, _s) in belief_assert]
        # --- OWN-PARSER arm (no spaCy): belief-assertion track ONLY (fully in-substrate: pos_tagger +
        # arc_parser; the PAL/spaCy is used ONLY for the perception observation gate). Carries the dominant
        # channels without any external tool at inference. ---
        ev_nospacy = [e for e in events_live if not e.affects_reality]
        obs_nospacy = {(agent, e.chrono): True for e in ev_nospacy}
        # --- STRONGER-PARSER perception arm (the HARD-THING test): re-extract the reality (perception) track
        # with spaCy and re-drive. If BELIEF_live_spacy reaches the oracle on perception items, the perception
        # wall is PARSER RECALL (a known external wall, not the mechanism); if it does not, the wall is deeper.
        # 2026-09-16 (strategy, LOCATED item 15 from pri 137): the ledger's `_nlp` is permanently None since the
        # spaCy purge (hdlab/perceptual_access_ledger.py, 2026-09-09), so `spacy_reality_events(None, ...)` raised on
        # every item and this cell could not run. There is no external parser at inference any more (owner rule), so
        # the "stronger-parser" arm is re-driven with the reader's OWN reality extractor -- an identical-source
        # control, NOT a stronger parser -- and says so in its output.
        _nlp = getattr(led, "_nlp", None)
        if _nlp is not None:
            from experiments.exp_belief_extraction_drill_v1 import spacy_reality_events
            sp_reality = spacy_reality_events(_nlp, sents, item["fact"]["fact_aliases"],
                                              item["fact"]["value_vocab"], item["fact_type"])
        else:
            sp_reality = BR.extract_reality_events(sents, by_sent, item["fact"])
            if not globals().get("_SPACY_ARM_NOTED"):
                print("[spacy arm] spaCy is purged from the live path (2026-09-09): the 'live_spacy' arm re-drives "
                      "with the in-substrate reality extractor (identical-source control, not a stronger parser)")
                globals()["_SPACY_ARM_NOTED"] = True
        ev_sp, obs_sp, _a2, _r2, _b2, _s2 = BR.drive(sents, by_sent, item["fact"], item["agent"], led,
                                                     reality_events=sp_reality)
        ev_sp = [WorldEvent(fact_head, _canon(e.value), chrono=e.chrono, narr=e.narr, kind=e.kind,
                            affects_reality=e.affects_reality) for e in ev_sp]
        # --- oracle: the agent's TRUE belief chain (definitional mechanism upper bound) ---
        ev_belief = _chain_events(item["belief_updates"], fact_head, affects_reality=False)
        obs_belief = {(agent, e.chrono): True for e in ev_belief}
        # --- reality chain (the reality floor) ---
        ev_reality = _chain_events(item["reality_events"], fact_head, affects_reality=True)
        # --- extraction quality ---
        eqr = _recall(item["reality_events"], reality_ext)
        rr_num += eqr["recall"] * eqr["n_gold"]; rr_den += eqr["n_gold"]
        # belief-update recall: the live agent-registered chain = observed reality changes + belief assertions
        live_registered = [(v, si) for (v, si) in reality_ext
                           if observed_live.get((agent, float(si)))] + belief_assert
        eqb = _recall(item["belief_updates"], live_registered)
        br_num += eqb["recall"] * eqb["n_gold"]; br_den += eqb["n_gold"]
        bp_num += eqb["precision"] * eqb["n_ext"]; bp_den += eqb["n_ext"]
        for (si, o) in item["obs_gold"]:
            got = observed_live.get((agent, float(si)))
            if got is not None:
                obs_n += 1; obs_ok += int(bool(got) == bool(o))
        # --- twin: shuffle extracted event order (info-free) ---
        import random
        rr = random.Random(seed + (abs(hash(item["sid"])) % 100000))
        tw = shuffle_order_twin(events_live, rr)
        tw_obs = remap_observed_after_twin(observed_live, events_live, tw)
        # --- per query (t = t_sent + 0.5) ---
        for q in item["queries"]:
            t = q["t_sent"] + 0.5
            # persistence distance = #sentences since the agent's last GOLD belief update at/before t
            prior = [si for (v, si) in item["belief_updates"] if si <= q["t_sent"]]
            dist = (q["t_sent"] - max(prior)) if prior else -1
            bl = timeline_belief(events_live, observed_live, agent, fact_head, t)
            preds = {
                "BELIEF_live": bl,
                "BELIEF_oracle": timeline_belief(ev_belief, obs_belief, agent, fact_head, t),
                "BELIEF_no_spacy": timeline_belief(ev_nospacy, obs_nospacy, agent, fact_head, t),
                "BELIEF_live_spacy": timeline_belief(ev_sp, obs_sp, agent, fact_head, t),
                "FLOOR_reality": reality_at(ev_reality, fact_head, t),
                "FLOOR_current": current_belief_floor(events_live, observed_live, agent, fact_head, t),
                "FLOOR_lastment": _lastment_floor(item, q["t_sent"], vocab),
                "TWIN_shuffled": timeline_belief(tw, tw_obs, agent, fact_head, t),
            }
            # SOURCE-TAG the belief the reader used: source of the latest observed event <= t
            obs_le = [e for e in events_live if e.chrono <= t and observed_live.get((agent, e.chrono))]
            src_pred = sources.get(max(obs_le, key=lambda e: e.chrono).chrono) if obs_le else None
            # KNOWLEDGE-STATE (Butterfill & Apperly registration): current(knows) / stale(false) / ignorant
            def _ks(belief, reality):
                if belief is None:
                    return "ignorant"
                return "current" if belief == reality else "stale"
            rows.append({"sid": item["sid"], "slice": item["slice"], "channel": item["channel"],
                         "fact_type": item["fact_type"], "gold": _canon(q["gold"]),
                         "reality": _canon(q["reality"]), "false_belief": q["false_belief"],
                         "t_sent": q["t_sent"], "dist": dist, "src_pred": src_pred, "src_gold": item["channel"],
                         "ks_gold": _ks(_canon(q["gold"]), _canon(q["reality"])),
                         "ks_pred": _ks(_canon(bl), _canon(q["reality"])),
                         "preds": {a: _canon(p) for a, p in preds.items()}})
    return {
        "rows": rows, "n_items": len(items), "n_queries": len(rows),
        "extraction_quality": {
            "reality_event_recall": rr_num / max(rr_den, 1),
            "belief_update_recall": br_num / max(br_den, 1),
            "belief_assertion_precision": bp_num / max(bp_den, 1),
            "observation_bit_acc": obs_ok / max(obs_n, 1),
            "n_reality_gold": rr_den, "n_belief_gold": br_den, "n_obs": obs_n,
        },
    }


ARMS = ["BELIEF_live", "BELIEF_oracle", "BELIEF_no_spacy", "BELIEF_live_spacy", "FLOOR_reality",
        "FLOOR_current", "FLOOR_lastment", "TWIN_shuffled"]


def _correct(pred, gold):
    return int(pred == gold)


def _equiv(pred, gold):
    """MEANING-TOLERANT belief-value equivalence (the OPEN-ENDED read-out; vetted 15/17, no antonym false-
    positives): a predicted belief value counts if it EXACT-matches OR is a WordNet synonym / scalar-entailment
    of gold -- so 'deceased'=='dead', 'wed'=='married'. Uses the promoted state_register WordNet path."""
    if pred is None or gold is None:
        return int(pred == gold)
    if pred == gold:
        return 1
    from hdlab.state_register import _wn_synonyms, _SCALAR_ENTAILS
    if pred in _wn_synonyms(gold) or gold in _wn_synonyms(pred):
        return 1
    if pred in _SCALAR_ENTAILS.get(gold, frozenset()) or gold in _SCALAR_ENTAILS.get(pred, frozenset()):
        return 1
    return 0


def _antonym_equiv(pred, gold, antonyms):
    """ANTONYM-INFLATION control: a read-out that (wrongly) also credits the antonym. If meaning-tolerant
    accuracy needed THIS to gain, it would be loosening, not recovering paraphrase. It must NOT be needed."""
    if _equiv(pred, gold):
        return 1
    return int(pred is not None and antonyms.get(gold) == pred)


def open_ended_analysis(items, led):
    """OPEN-ENDED belief VALUE (paraphrase) -- the OPEN ITEM. The reader extracts a SYNONYM of the canonical
    gold value; score BELIEF_live under exact-match vs the MEANING-TOLERANT read-out (WordNet synonym/entailment
    via state_register) vs an ANTONYM-INFLATING control. paraphrase_recovery = mt - exact (the real gain);
    the antonym-inflating arm shows what wrongly loosening to antonyms would add (meaning-tolerant must NOT
    credit antonyms -- vetted 0 false-positives)."""
    ant = {"dead": "alive", "alive": "dead", "married": "single", "single": "married", "safe": "lost",
           "lost": "safe", "gone": "present", "present": "gone", "out": "lit", "lit": "out", "mad": "sane",
           "sane": "mad"}
    ex = mt = an = tot = 0
    for it in items:
        sents = it["sents"]; by_sent = {i: [] for i in range(len(sents))}
        fh = _fact_head(it)
        events, observed, agent, _re, _ba, _src = BR.drive(sents, by_sent, it["fact"], it["agent"], led)
        events = [WorldEvent(fh, _canon(e.value), chrono=e.chrono, narr=e.narr, kind=e.kind,
                             affects_reality=e.affects_reality) for e in events]
        for q in it["queries"]:
            gold = _canon(q["gold"])
            pred = _canon(timeline_belief(events, observed, agent, fh, q["t_sent"] + 0.5))
            tot += 1
            ex += _correct(pred, gold); mt += _equiv(pred, gold); an += _antonym_equiv(pred, gold, ant)
    tot = max(tot, 1)
    return {"n": tot, "belief_exact": ex / tot, "belief_meaning_tolerant": mt / tot,
            "belief_antonym_inflating": an / tot, "paraphrase_recovery": round((mt - ex) / tot, 3),
            "antonym_inflation_if_loosened": round((an - mt) / tot, 3),
            "meaning_tolerant_recovers_and_rejects_antonyms": bool(mt > ex)}


def pop_acc(rows, arm):
    xs = [_correct(r["preds"].get(arm), r["gold"]) for r in rows]
    return float(np.mean(xs)) if xs else None


def boot_paired(rows, arm_a, arm_b, n_boot, rng):
    """paired bootstrap over ITEMS (group by sid) of acc_a - acc_b."""
    by_sid = {}
    for r in rows:
        by_sid.setdefault(r["sid"], []).append(r)
    sids = sorted(by_sid)

    def agg(sample):
        a = [_correct(r["preds"].get(arm_a), r["gold"]) for s in sample for r in by_sid[s]]
        b = [_correct(r["preds"].get(arm_b), r["gold"]) for s in sample for r in by_sid[s]]
        return (np.mean(a) if a else 0.0), (np.mean(b) if b else 0.0)
    am, bm = agg(sids)
    diffs = []
    keys = np.array(sids)
    for _ in range(n_boot):
        s = list(rng.choice(keys, size=len(keys), replace=True))
        a, b = agg(s)
        diffs.append(a - b)
    diffs = np.array(diffs)
    lo, hi = float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))
    return {"delta": am - bm, "lo": lo, "hi": hi, "a_mean": am, "b_mean": bm,
            "half_width": (hi - lo) / 2, "CI_separated": bool(lo > 0)}


def false_belief_discriminator(rows, n_boot, rng):
    """On the belief!=reality subset: BELIEF_live beats FLOOR_reality by MORE than on the full set."""
    fb = [r for r in rows if r["false_belief"]]
    if not fb:
        return {"n_false_belief": 0}
    d_fb = boot_paired(fb, "BELIEF_live", "FLOOR_reality", n_boot, rng)
    return {"n_false_belief": len(fb),
            "belief_vs_reality_on_false_belief": d_fb,
            "belief_acc_on_fb": pop_acc(fb, "BELIEF_live"),
            "reality_acc_on_fb": pop_acc(fb, "FLOOR_reality"),
            "oracle_acc_on_fb": pop_acc(fb, "BELIEF_oracle")}


def twin_null(rows, items, led, n_boot, rng, R=TWIN_R):
    """R reshuffles of each item's extracted events -> null distribution of BELIEF accuracy; report p95."""
    import random
    by_sid_item = {it["sid"]: it for it in items}
    # recompute extracted events per sid once
    cache = {}
    for it in items:
        sents = it["sents"]; by_sent = {i: [] for i in range(len(sents))}
        ev, obs, agent, _re, _ba, _src = BR.drive(sents, by_sent, it["fact"], it["agent"], led)
        ev = [WorldEvent(_fact_head(it), _canon(e.value), chrono=e.chrono, narr=e.narr, kind=e.kind,
                         affects_reality=e.affects_reality) for e in ev]
        cache[it["sid"]] = (ev, obs, agent)
    null_acc = []
    for r in range(R):
        correct = []
        for row in rows:
            it = by_sid_item[row["sid"]]
            ev, obs, agent = cache[row["sid"]]
            rr = random.Random(1000 + r * 97 + (abs(hash(row["sid"])) % 100000))
            tw = shuffle_order_twin(ev, rr)
            tw_obs = remap_observed_after_twin(obs, ev, tw)
            pred = _canon(timeline_belief(tw, tw_obs, agent, _fact_head(it), row["t_sent"] + 0.5))
            correct.append(_correct(pred, row["gold"]))
        null_acc.append(float(np.mean(correct)) if correct else 0.0)
    return {"R": R, "mean": float(np.mean(null_acc)), "p95": float(np.percentile(null_acc, 95)),
            "max": float(np.max(null_acc))}


def distance_curve(rows, buckets=((0, 0), (1, 2), (3, 9999))):
    """accuracy vs #sentences since the agent's last belief update (persistence signature)."""
    out = {}
    for lo, hi in buckets:
        sub = [r for r in rows if r["dist"] >= 0 and lo <= r["dist"] <= hi]
        out[f"{lo}-{hi}"] = {"n": len(sub), "BELIEF_live": pop_acc(sub, "BELIEF_live"),
                             "BELIEF_oracle": pop_acc(sub, "BELIEF_oracle"),
                             "FLOOR_lastment": pop_acc(sub, "FLOOR_lastment")}
    return out


def analyze(rows, items, led, n_boot, rng, label):
    present = [a for a in ARMS if any(a in r["preds"] for r in rows)]
    pop = {a: pop_acc(rows, a) for a in present}
    floors = ["FLOOR_reality", "FLOOR_current", "FLOOR_lastment"]
    strongest = max(floors, key=lambda a: pop.get(a) or 0.0)
    gates = {
        "vs_strongest_floor": boot_paired(rows, "BELIEF_live", strongest, n_boot, rng),
        "vs_reality": boot_paired(rows, "BELIEF_live", "FLOOR_reality", n_boot, rng),
        "vs_lastment": boot_paired(rows, "BELIEF_live", "FLOOR_lastment", n_boot, rng),
        "vs_twin": boot_paired(rows, "BELIEF_live", "TWIN_shuffled", n_boot, rng),
        "oracle_vs_strongest_floor": boot_paired(rows, "BELIEF_oracle", strongest, n_boot, rng),
        "live_vs_oracle": boot_paired(rows, "BELIEF_oracle", "BELIEF_live", n_boot, rng),
    }
    tn = twin_null(rows, items, led, n_boot, rng)
    disc = false_belief_discriminator(rows, n_boot, rng)
    dc = distance_curve(rows)
    # per-channel / per-fact-type live accuracy (generalization + wall enumeration)
    def sub_acc(key, val):
        sub = [r for r in rows if r[key] == val]
        return {"n": len(sub), "BELIEF_live": pop_acc(sub, "BELIEF_live"),
                "BELIEF_live_spacy": pop_acc(sub, "BELIEF_live_spacy"),
                "BELIEF_oracle": pop_acc(sub, "BELIEF_oracle"), "FLOOR_reality": pop_acc(sub, "FLOOR_reality")}
    by_channel = {c: sub_acc("channel", c) for c in sorted({r["channel"] for r in rows})}
    by_fact = {c: sub_acc("fact_type", c) for c in sorted({r["fact_type"] for r in rows})}
    ks = knowledge_state_metric(rows, n_boot, rng)
    st = source_tag_metric(rows)
    # OWN-PARSER (no-spaCy) carry on the dominant channels: belief-assertions are fully in-substrate
    dom = [r for r in rows if r["channel"] in ("epistemic", "testimony")]
    no_spacy = {"dominant_channels_no_spacy_acc": pop_acc(dom, "BELIEF_no_spacy"),
                "dominant_channels_live_acc": pop_acc(dom, "BELIEF_live"), "n_dominant": len(dom)}
    return {"label": label, "pop_acc": pop, "strongest_floor": strongest, "gates": gates,
            "twin_null": tn, "false_belief_discriminator": disc, "distance_curve": dc,
            "by_channel": by_channel, "by_fact_type": by_fact,
            "knowledge_state": ks, "source_tag": st, "no_spacy": no_spacy}


def knowledge_state_metric(rows, n_boot, rng):
    """Butterfill & Apperly registration read-out: does the reader classify A's knowledge STATE
    (current/knows, stale/false, ignorant) correctly, vs an ASSUME-KNOWS floor (the beliefless reader
    that assumes everyone knows the current reality = always 'current')? This is the COVERAGE-ROBUST real-
    prose metric -- real narrative supplies ignorance abundantly ('did not know')."""
    by_sid = {}
    for r in rows:
        by_sid.setdefault(r["sid"], []).append(r)
    sids = sorted(by_sid)

    def acc(sample, mode):
        xs = [(int(r["ks_pred"] == r["ks_gold"]) if mode == "reader" else int(r["ks_gold"] == "current"))
              for s in sample for r in by_sid[s]]
        return float(np.mean(xs)) if xs else 0.0
    rd, ak = acc(sids, "reader"), acc(sids, "assume")
    keys = np.array(sids)
    diffs = []                       # paired: resample sids once per draw, score both arms on the same draw
    for _ in range(n_boot):
        s = list(rng.choice(keys, size=len(keys), replace=True))
        diffs.append(acc(s, "reader") - acc(s, "assume"))
    diffs = np.array(diffs)
    from collections import Counter
    conf = Counter((r["ks_gold"], r["ks_pred"]) for r in rows)
    return {"reader_acc": rd, "assume_knows_acc": ak, "delta": rd - ak,
            "lo": float(np.percentile(diffs, 2.5)), "hi": float(np.percentile(diffs, 97.5)),
            "CI_separated": bool(np.percentile(diffs, 2.5) > 0),
            "n_ignorant": sum(1 for r in rows if r["ks_gold"] == "ignorant"),
            "n_stale": sum(1 for r in rows if r["ks_gold"] == "stale"),
            "n_current": sum(1 for r in rows if r["ks_gold"] == "current"),
            "confusion": {f"{k[0]}->{k[1]}": v for k, v in sorted(conf.items())}}


def source_tag_metric(rows):
    """Does the reader tag HOW the belief was acquired (perception / testimony / epistemic) correctly --
    the brain source-tags seen vs heard (Koster-Hale et al. 2014). Scored where the reader holds a belief."""
    sub = [r for r in rows if r["src_pred"] is not None]
    if not sub:
        return {"n": 0, "acc": None, "by_source": {}}
    acc = float(np.mean([int(r["src_pred"] == r["src_gold"]) for r in sub]))
    by = {}
    for c in sorted({r["src_gold"] for r in sub}):
        cs = [r for r in sub if r["src_gold"] == c]
        by[c] = float(np.mean([int(r["src_pred"] == r["src_gold"]) for r in cs]))
    return {"n": len(sub), "acc": acc, "by_source": by}


def dramatic_irony_analysis(items, led):
    """TWO-AGENT knowledge asymmetry (dramatic irony): does the reader detect that agent A holds the
    current-true belief while B holds a STALE one (knowledge_advantage), and that they DIVERGE? Uses the
    organ's own divergence/knowledge_advantage on the two agents' reader-extracted, observation-gated
    timelines. Floor = 'no asymmetry' (never diverge). Brain: first-order irony = the reader spots the gap."""
    from hdlab.belief_timeline import divergence, knowledge_advantage
    rows = []
    for it in items:
        sents = it["sents"]; by_sent = {i: [] for i in range(len(sents))}
        fh = it["fact"]["fact_aliases"][0].lower()
        reality = [(_canon(v), si) for (v, si) in BR.extract_reality_events(sents, by_sent, it["fact"])]
        text = " ".join(" ".join(t) for t in sents)
        A, B = it["agentA"][0], it["agentB"][0]
        events, observed = [], {}
        for (v, si) in reality:
            ch = float(si)
            events.append(WorldEvent(fh, v, chrono=ch, narr=ch, kind="move", affects_reality=True))
            for ag, al in ((A, it["agentA"]), (B, it["agentB"])):
                tr = led.observed(text, list(al), event_object=fh, event_index=si, event_location=v)
                observed[(ag, ch)] = bool(tr.observed)
        for q in it["irony_queries"]:
            t = q["t_sent"] + 0.5
            dv = divergence(events, observed, A, B, fh, t)
            ad = knowledge_advantage(events, observed, A, B, fh, t)
            rows.append({"div_pred": bool(dv) if dv is not None else None, "div_gold": q["divergent"],
                         "adv_pred": bool(ad) if ad is not None else None, "adv_gold": q["A_advantage"]})
    dv_ok = [int(r["div_pred"] == r["div_gold"]) for r in rows if r["div_pred"] is not None]
    ad_ok = [int(r["adv_pred"] == r["adv_gold"]) for r in rows if r["adv_pred"] is not None]
    floor = [int(False == r["div_gold"]) for r in rows]   # 'no asymmetry' floor
    return {"n": len(rows), "divergence_acc": float(np.mean(dv_ok)) if dv_ok else None,
            "advantage_acc": float(np.mean(ad_ok)) if ad_ok else None,
            "floor_no_asymmetry_acc": float(np.mean(floor)) if floor else None,
            "beats_floor": bool((np.mean(dv_ok) if dv_ok else 0) > (np.mean(floor) if floor else 1))}


def flashback_analysis(items):
    """FLASHBACK (narration order != chronology): the belief must be read at CHRONOLOGICAL time. The
    temporal-order register recovers chrono order; a NARRATION-order tracker (last-narrated wins) mis-
    sequences. chrono-order should recover the gold; narration-order should NOT -> the register is needed."""
    rows = []
    for it in items:
        fh = it["fact"]["fact_aliases"][0].lower(); A = it["agent"][0]
        ev_c, ev_n, oc, on = [], [], {}, {}
        for (v, narr, chrono) in it["per_event"]:
            cv = _canon(v)
            ev_c.append(WorldEvent(fh, cv, chrono=float(chrono), narr=float(narr), kind="move"))
            ev_n.append(WorldEvent(fh, cv, chrono=float(narr), narr=float(narr), kind="move"))  # chrono:=narr
            oc[(A, float(chrono))] = bool(it["observed"][chrono])
            on[(A, float(narr))] = bool(it["observed"][chrono])
        for q in it["queries"]:
            rows.append({"gold": _canon(q["gold"]),
                         "chrono_pred": _canon(timeline_belief(ev_c, oc, A, fh, q["chrono_t"])),
                         "narr_pred": _canon(timeline_belief(ev_n, on, A, fh, q["chrono_t"]))})
    c_ok = float(np.mean([int(r["chrono_pred"] == r["gold"]) for r in rows])) if rows else None
    n_ok = float(np.mean([int(r["narr_pred"] == r["gold"]) for r in rows])) if rows else None
    return {"n": len(rows), "chrono_order_acc": c_ok, "narration_order_acc": n_ok,
            "register_needed": bool(c_ok is not None and n_ok is not None and c_ok > n_ok)}


def inference_analysis(items, led):
    """INFERRED belief (Sodian & Wimmer exclusion), END-TO-END from the reader's parse: does BELIEF_live
    recover the INFERRED value (never perceived), and is it evidence-GATED (silent/ignorant when the agent did
    NOT observe the negative premise)? The gated control is the discriminator -- an ungated inferer would
    (wrongly) still conclude."""
    n_fire = fire_ok = n_gate = gate_ok = 0
    for it in items:
        sents = it["sents"]; by_sent = {i: [] for i in range(len(sents))}
        fh = _fact_head(it)
        events, observed, agent, _re, _ba, _src = BR.drive(sents, by_sent, it["fact"], it["agent"], led)
        events = [WorldEvent(fh, _canon(e.value), chrono=e.chrono, narr=e.narr, kind=e.kind,
                             affects_reality=e.affects_reality) for e in events]
        for q in it["queries"]:
            pred = _canon(timeline_belief(events, observed, agent, fh, q["t_sent"] + 0.5))
            gold = _canon(q["gold"])
            if gold is None:
                n_gate += 1; gate_ok += int(pred is None)     # gated control: must stay ignorant
            else:
                n_fire += 1; fire_ok += int(pred == gold)     # inferred value must be recovered
    return {"n_inferred": n_fire, "inferred_recall": fire_ok / max(n_fire, 1),
            "n_gated_control": n_gate, "gated_stays_ignorant": gate_ok / max(n_gate, 1),
            "end_to_end_works": bool(n_fire and fire_ok / max(n_fire, 1) >= 0.5
                                     and (n_gate == 0 or gate_ok == n_gate))}


def fhrr_readout_stability(items, seeds=(13, 20260831, 777), d=1024):
    """The belief value is READ OFF the substrate (glass-box): bind(fact,value) -> unbind(fact) -> cleanup over
    the value vocab, via the PROMOTED belief_partition FHRR banks (hdlab.belief_timeline.SubstrateReadout).
    Multi-seed: the decode must round-trip the believed value stably across FHRR seeds -- the answer comes from
    the substrate, not a lookup, and it is not a lucky codebook."""
    from hdlab.belief_timeline import SubstrateReadout
    per_seed = {}
    for sd in seeds:
        ro = SubstrateReadout(d=d, seed=sd)
        ok = tot = 0
        for it in items:
            vocab = [_canon(v) for v in it["fact"]["value_vocab"]]
            fh = _fact_head(it)
            for (v, si) in it["belief_updates"]:
                cv = _canon(v)
                tot += 1
                ok += int(ro.readout(fh, cv, vocab) == cv)
        per_seed[str(sd)] = ok / max(tot, 1)
    vals = list(per_seed.values())
    return {"seeds": list(seeds), "per_seed_roundtrip_acc": {k: round(v, 3) for k, v in per_seed.items()},
            "mean": float(np.mean(vals)), "min": float(np.min(vals)),
            "seed_stable": bool(np.min(vals) >= 0.99)}


def run(smoke=False, n_boot=2000, write=True):
    import spacy
    from hdlab.perceptual_access_ledger import PerceptualAccessLedger
    nlp = spacy.load("en_core_web_sm")
    led = PerceptualAccessLedger(nlp)
    rng = np.random.default_rng(SEED)

    modern = modern_items()
    real = load_real()
    if smoke:
        modern = modern[:4]

    out = {"anchor_name": ANCHOR, "run_mode": "smoke" if smoke else "full", "seed": SEED}
    m = run_slice(modern, led)
    out["modern"] = {"n_items": m["n_items"], "n_queries": m["n_queries"],
                     "extraction_quality": m["extraction_quality"],
                     **analyze(m["rows"], modern, led, n_boot, rng, "MODERN")}
    if real:
        r = run_slice(real, led)
        out["real"] = {"n_items": r["n_items"], "n_queries": r["n_queries"],
                       "extraction_quality": r["extraction_quality"],
                       **analyze(r["rows"], real, led, n_boot, rng, "REAL")}
    else:
        out["real"] = {"n_items": 0, "note": "real.jsonl not yet built"}
    from experiments.belief_at_t_gold import (two_agent_items, flashback_items, open_ended_items,
                                              inference_items)
    out["dramatic_irony"] = dramatic_irony_analysis(two_agent_items(), led)
    out["flashback"] = flashback_analysis(flashback_items())
    out["open_ended"] = open_ended_analysis(open_ended_items(), led)
    out["inference"] = inference_analysis(inference_items(), led)
    out["fhrr_readout"] = fhrr_readout_stability(modern + real)

    if write:
        # Q115 (owner 2026-08-23): every cell's output goes through the shared helper so a re-run is a fresh run.
        from experiments._seed_checkpoint import get_output_dir
        outdir = str(get_output_dir(ANCHOR + ("_smoke" if smoke else "")))
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, "metrics.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
    return out


def _print(out):
    for slc in ("modern", "real"):
        s = out.get(slc)
        if not s or not s.get("n_items"):
            print(f"\n[{slc.upper()}] (none)"); continue
        print(f"\n{'='*80}\n[{slc.upper()}] items={s['n_items']} queries={s['n_queries']}")
        eq = s["extraction_quality"]
        print(f"  extraction: reality-recall={eq['reality_event_recall']:.3f} "
              f"belief-recall={eq['belief_update_recall']:.3f} belief-prec={eq['belief_assertion_precision']:.3f} "
              f"obs-bit-acc={eq['observation_bit_acc']:.3f} "
              f"(n_reality={eq['n_reality_gold']} n_belief={eq['n_belief_gold']} n_obs={eq['n_obs']})")
        print("  pop_acc:", {a: round(v, 3) for a, v in s["pop_acc"].items() if v is not None})
        g = s["gates"]
        for name in ("vs_strongest_floor", "vs_reality", "vs_lastment", "vs_twin", "live_vs_oracle"):
            d = g[name]
            print(f"    {name:<22} {d['a_mean']:.3f} vs {d['b_mean']:.3f}  delta {d['delta']:+.3f} "
                  f"[{d['lo']:+.3f},{d['hi']:+.3f}] hw={d['half_width']:.3f} CI-sep={d['CI_separated']}")
        tn = s["twin_null"]
        print(f"  twin null: mean={tn['mean']:.3f} p95={tn['p95']:.3f}  "
              f"BELIEF_live({s['pop_acc']['BELIEF_live']:.3f})>p95={s['pop_acc']['BELIEF_live']>tn['p95']}")
        d = s["false_belief_discriminator"]
        if d.get("n_false_belief"):
            dd = d["belief_vs_reality_on_false_belief"]
            print(f"  FALSE-BELIEF (n={d['n_false_belief']}): belief={d['belief_acc_on_fb']:.3f} "
                  f"reality={d['reality_acc_on_fb']:.3f} oracle={d['oracle_acc_on_fb']:.3f}; "
                  f"belief-vs-reality delta {dd['delta']:+.3f} [{dd['lo']:+.3f},{dd['hi']:+.3f}] CI-sep={dd['CI_separated']}")
        print("  by channel:", {c: {"n": v["n"], "live": round(v["BELIEF_live"], 2),
                                     "oracle": round(v["BELIEF_oracle"], 2)} for c, v in s["by_channel"].items()})
        print("  by fact_type:", {c: {"n": v["n"], "live": round(v["BELIEF_live"], 2),
                                      "oracle": round(v["BELIEF_oracle"], 2)} for c, v in s["by_fact_type"].items()})
        ks = s["knowledge_state"]
        print(f"  KNOWLEDGE-STATE: reader={ks['reader_acc']:.3f} vs assume-knows={ks['assume_knows_acc']:.3f} "
              f"delta {ks['delta']:+.3f} [{ks['lo']:+.3f},{ks['hi']:+.3f}] CI-sep={ks['CI_separated']} "
              f"(ignorant={ks['n_ignorant']} stale={ks['n_stale']} current={ks['n_current']})")
        st = s["source_tag"]
        print(f"  SOURCE-TAG acc={st['acc']} (n={st['n']}) by_source={ {k: round(v,2) for k,v in st['by_source'].items()} }")
        ns = s["no_spacy"]
        print(f"  OWN-PARSER (no-spaCy) dominant-channel belief acc={ns['dominant_channels_no_spacy_acc']} "
              f"(live {ns['dominant_channels_live_acc']}, n={ns['n_dominant']})")
    di = out.get("dramatic_irony")
    if di:
        print(f"\nDRAMATIC-IRONY (2-agent, n={di['n']}): divergence_acc={di['divergence_acc']} "
              f"advantage_acc={di['advantage_acc']} vs no-asymmetry floor {di['floor_no_asymmetry_acc']} "
              f"beats_floor={di['beats_floor']}")
    fb = out.get("flashback")
    if fb:
        print(f"FLASHBACK (n={fb['n']}): chrono-order(register)={fb['chrono_order_acc']} "
              f"narration-order={fb['narration_order_acc']} register_needed={fb['register_needed']}")
    oe = out.get("open_ended")
    if oe:
        print(f"OPEN-ENDED belief (paraphrase, n={oe['n']}): exact={oe['belief_exact']:.2f} -> meaning-tolerant "
              f"{oe['belief_meaning_tolerant']:.2f} (paraphrase-recovery {oe['paraphrase_recovery']:+.2f}); "
              f"antonym-inflation-if-loosened {oe['antonym_inflation_if_loosened']:+.2f}; "
              f"recovers+rejects-antonyms={oe['meaning_tolerant_recovers_and_rejects_antonyms']}")
    inf = out.get("inference")
    if inf:
        print(f"INFERRED belief (exclusion, end-to-end): inferred-recall={inf['inferred_recall']:.2f} "
              f"(n={inf['n_inferred']}); gated-control stays-ignorant={inf['gated_stays_ignorant']:.2f} "
              f"(n={inf['n_gated_control']}); end_to_end_works={inf['end_to_end_works']}")
    fr = out.get("fhrr_readout")
    if fr:
        print(f"FHRR substrate read-out (multi-seed): per_seed={fr['per_seed_roundtrip_acc']} "
              f"seed_stable={fr['seed_stable']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="full")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--n-boot", type=int, default=2000)
    a = ap.parse_args()
    if a.self_test:
        o = run(smoke=True, n_boot=200, write=False)
        assert o["modern"]["pop_acc"]["BELIEF_oracle"] >= 0.99, "oracle mechanism must be ~perfect"
        print("self-test PASS: oracle mechanism ~perfect on modern control")
    else:
        smoke = a.smoke or a.mode == "smoke"
        _print(run(smoke=smoke, n_boot=a.n_boot))
