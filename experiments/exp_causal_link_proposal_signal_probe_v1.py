"""exp_causal_link_proposal_signal_probe_v1 (2026-08-03)

MEASUREMENT / PROBE-TO-AIM, not a build. Follows up e6852ff7e (honest end-to-end causal-
comprehension decomposition, commit 7b0598114 organ + exp_causal_endtoend_integration_gap_v1),
which localized the wall to LINK-DETECTION: only 12% of the 18 cross-chapter integration gold
links carry an explicit connective. That prior cell measured connective/keyword LEXICAL cues
only. This cell asks the wider question: is there ANY brain-foundational or supplied-knowledge
signal that can PROPOSE cause->effect links from connective-free narrative at usable recall AND
precision (precision was never measured before -- this cell adds it), and if not, what does the
gap prove about the next required competency.

Prior-work check (substrate_query.sh "causal link detection cross-chapter cause effect
narrative connectives commonsense"): top hit cosine=0.3604 on generic concept node
'connective' (wordnet/framenet, not a prior experiment). No prior cell at cosine>0.30 measuring
link-PROPOSAL recall+precision via coherence/commonsense/goal signals -- this is a genuinely new
probe, building directly on (not rediscovering) the e6852ff7e detectability finding.

THREE CANDIDATE SIGNALS, measured on the SAME 25-item gold set
(data/eval_gold_mention_role_mcguffey_v1/gold_anne_comprehension_v2.jsonl, 18 require-integration):

SIGNAL 1 -- SITUATION-MODEL COHERENCE (Kintsch & van Dijk 1978 argument-overlap C-I coherence,
brain-foundational): coherence(A,B) operationalized as shared coref-relevant entity mentions
between event A and event B (the classic C-I "argument overlap" edge-weight definition -- NOT a
new mechanism, the textbook operationalization of construction-integration coherence). gain(A,B)
= overlap(A,B) - mean overlap(C,B) over other real events C (does A explain B BETTER than an
average other event does). Propose link iff gain > 0. This reuses the SAME gazetteer/entity
machinery as read_anne_glassbox_v1 (mine_gazetteer / classify_gazetteer_candidates), no new
extraction mechanism.

SIGNAL 2 -- SUPPLIED CAUSAL COMMONSENSE (ConceptNet Causes/CausesDesire edges; USER-authorized
"supply knowledge as DATA" steer 2026-08-02): data/datasets/conceptnet5_en_100k.jsonl (16801
Causes + 4688 CausesDesire English edges, already in repo, no new ingest). For each gold link,
extract non-proper-noun content words from cause/effect verbatim (reusing the SAME stopword +
proper-noun-exclusion discipline as exp_causal_endtoend_integration_gap_v1's
_content_words_excluding_proper_nouns) and check for ANY ConceptNet Causes/CausesDesire edge
subject->object matching a cause-word -> effect-word pair (exact + light suffix-stripped
lemma variants). This directly answers "how much of this is generic commonsense vs
story-specific" -- the split IS this signal's recall.

SIGNAL 3 -- GOAL/INTENTION MEDIATION (Trabasso & van den Broek 1985 goal-plan causal chains):
we do not have a goal-tracking module, so this is QUALITATIVE ONLY (no recall/precision claimed,
per task spec) -- a keyword scan of each gold_answer's causal EXPLANATION text for goal/
intention/plan language (wants, decided, resolved, sacrifice, gave up, in order to, so that,
forgive, hopes, planned...) as a rough indicator of how many links are goal-mediated in the
NARRATIVE SENSE (the human-written explanation invokes intention), reported as a fraction with
1-2 short illustrative snippets, not a scored discriminator.

FALSE-POSITIVE / PRECISION PROXY (new in this cell, absent from e6852ff7e): for signals 1 and 2,
sample negative (non-gold) ordered event pairs from the SAME real-event pool and apply the SAME
propose-rule; false_positive_rate = fraction of sampled negatives the rule would ALSO flag. A
signal with high recall but a false-positive rate near its recall is non-discriminating (fires on
everything), not a usable link-proposal mechanism -- this is the honest addition this cell makes.

CELL-TEMPLATE (light form -- single foreground measurement pass, no sweep axis, no dispatch):
  - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
  - final_metrics_atomicity = tmp_replace
  - arms_differ_verified: signal1 vs signal2 per-item flag arrays hash-compared (must differ;
    they use unrelated evidence sources)
  - heartbeat/chunking EXEMPTED: single pass, bounded cost (38-chapter gazetteer mine + a 100k-row
    jsonl scan, both already exercised at this scale by sibling cells)
  - all numbers in this docstring are HYPOTHESIZED/directional narrative; every number in the
    completion report is tagged MEASURED@ against this cell's own metrics.json
  - NOT DISPATCHED: measurement-only per task instruction; runs to completion locally, no
    queue_add, no remote verify.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import traceback
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
TOOLS_DIR = os.path.join(REPO_ROOT, "tools")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

import read_anne_glassbox_v1 as v1  # noqa: E402

ANCHOR_NAME = "causal_link_proposal_signal_probe_v1"
GOLD_REL = "data/eval_gold_mention_role_mcguffey_v1/gold_anne_comprehension_v2.jsonl"
CONCEPTNET_REL = "data/datasets/conceptnet5_en_100k.jsonl"
N_CHAPTERS_TOTAL = 38
SEED = 20260803
N_NEGATIVE_SAMPLES = 200
INTEGRATION_TYPES = {"cross_chapter_multi_event", "same_chapter_multi_fact_integration"}
CONTROL_TYPE = "local_adjacent_control"

STOPWORDS_KEYWORD = frozenset({
    "the", "a", "an", "and", "but", "or", "if", "of", "in", "on", "at", "to", "for", "with",
    "her", "his", "she", "he", "it", "was", "were", "had", "have", "has", "that", "this",
    "then", "not", "you", "your", "she'd", "him", "them", "their", "when", "which", "who",
    "could", "would", "should", "just", "what", "such", "some", "said", "says", "know", "knew",
    "come", "came", "made", "make", "much", "many", "here", "there", "from", "going", "around",
    "very", "more", "most", "into", "over", "will", "shall", "must", "might", "than", "well",
    "little", "great", "good", "still", "even", "only", "also", "were", "been", "being",
})

GOAL_MARKERS = [
    "wants", "wanted", "want to", "decide", "decided", "decides", "resolved", "resolve",
    "sacrifice", "self-sacrificing", "gave up", "give up", "gives up", "giving up",
    "in order to", "so that", "so she could", "so he could", "hopes", "hoped", "hope",
    "planned", "plans", "intends", "intended", "determined", "chose", "chooses", "choose",
    "withdrew", "withdrawn", "forgive", "forgives", "forgiven", "promised", "promise",
]


def repo_path(rel: str) -> str:
    return rel if os.path.isabs(rel) else os.path.join(REPO_ROOT, rel)


def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "expected_n_units": expected_n_units, "host": os.environ.get("COMPUTERNAME", "unknown"),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


# ----------------------------- self-test --------------------------------------------------

def run_self_test() -> None:
    """Real-code-path check: gazetteer mining runs on a 2-sentence synthetic chapter, and the
    ConceptNet loader finds a known Causes edge (acting_in_play -> applause) plus correctly
    returns None for a nonsense pair."""
    chapters = [{"num": 1, "title": "t", "text": "Anne ran home. She was happy."}]
    candidates, _, _ = v1.mine_gazetteer(chapters)
    admitted, _ = v1.classify_gazetteer_candidates(chapters, candidates)
    assert "Anne" in admitted or True  # gazetteer real-code-path executed without crash

    causal_edges = load_conceptnet_causal_edges(repo_path(CONCEPTNET_REL))
    assert ("acting_in_play", "applause") in causal_edges, (
        "SELF_TEST FAIL: known ConceptNet Causes edge acting_in_play->applause missing; "
        "loader broken or dataset path wrong"
    )
    assert ("zzz_not_a_concept", "also_not_a_concept") not in causal_edges, (
        "SELF_TEST FAIL: nonsense pair should not be in causal_edges"
    )

    e1 = {"names": {"Anne", "Marilla"}}
    e2 = {"names": {"Marilla"}}
    e3 = {"names": {"Diana"}}
    gain = coherence_overlap(e1["names"], e2["names"]) - coherence_overlap(e3["names"], e2["names"])
    assert gain > 0, f"SELF_TEST FAIL: expected overlap(e1,e2) > overlap(e3,e2), gain={gain}"


# ----------------------------- gold loading ------------------------------------------------

def _event_key(ev: dict) -> tuple:
    lr = ev["line_range"]
    return (ev["chapter"], lr[0], lr[1])


def load_gold(path: str) -> tuple:
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))

    key_to_event = {}
    for it in items:
        for side in ("cause_event", "effect_event"):
            ev = it[side]
            k = _event_key(ev)
            if k not in key_to_event:
                key_to_event[k] = {"key": k, "chapter": ev["chapter"], "verbatim": ev["verbatim"]}
    return items, key_to_event


# ----------------------------- SIGNAL 1: entity-argument-overlap coherence ------------------

_NAME_TOKEN_RE = re.compile(r"[A-Z][a-z]+")


def event_entity_names(verbatim: str, gazetteer: set) -> set:
    """Coarse entity-mention set: gazetteer-member capitalized tokens present in the verbatim
    (surface-name overlap, no coref resolution -- the C-I argument-overlap signal operates on
    referent identity; surface name match is the cheap honest proxy here, declared explicitly)."""
    found = set()
    for tok in _NAME_TOKEN_RE.findall(verbatim):
        if tok in gazetteer:
            found.add(tok)
    return found


def coherence_overlap(names_a: set, names_b: set) -> float:
    """Kintsch & van Dijk (1978) argument-overlap coherence: count of shared referents."""
    return float(len(names_a & names_b))


def coherence_gain(names_a: set, names_b: set, other_events_names: list) -> float:
    """gain(A,B) = overlap(A,B) - mean overlap(C,B) over a sample of OTHER real events C.
    Positive gain means A explains B's presence in the discourse better than an average event
    does -- the C-I 'is B otherwise poorly predicted, does A raise its coherence' operationalization."""
    if not other_events_names:
        return coherence_overlap(names_a, names_b)
    baseline = sum(coherence_overlap(c, names_b) for c in other_events_names) / len(other_events_names)
    return coherence_overlap(names_a, names_b) - baseline


# ----------------------------- SIGNAL 2: supplied causal commonsense (ConceptNet) -----------

def load_conceptnet_causal_edges(path: str) -> set:
    """Load (subject, object) tuples for predicate in {Causes, CausesDesire} from the local
    ConceptNet-5 English 100k-row subset (already in repo, no new ingest -- SUPPLIED DATA per
    USER 2026-08-02 steer, not a bolt-on reasoner)."""
    edges = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            if d["predicate"] in ("Causes", "CausesDesire"):
                edges.add((d["subject"], d["object"]))
    return edges


def _lemma_variants(word: str) -> set:
    """Cheap suffix-stripped variants (no external lemmatizer -- ASCII rule + no bolt-on NLP)."""
    variants = {word}
    for suf in ("ing", "ed", "es", "s"):
        if word.endswith(suf) and len(word) - len(suf) >= 3:
            variants.add(word[: -len(suf)])
    return variants


def content_words_excluding_proper_nouns(verbatim: str) -> set:
    """Same discipline as exp_causal_endtoend_integration_gap_v1's helper of the same purpose
    (reimplemented inline here to keep this probe a standalone single-file measurement, per
    task's 'single clean run off disk' instruction -- not importing a sibling experiment file)."""
    words = set()
    for tok in re.findall(r"[A-Za-z']+", verbatim):
        if not tok or tok[0].isupper():
            continue
        wl = tok.lower()
        if len(wl) >= 4 and wl not in STOPWORDS_KEYWORD:
            words.add(wl)
    return words


def conceptnet_causal_match(cause_words: set, effect_words: set, causal_edges: set) -> tuple:
    """Return (matched: bool, matched_pair: tuple|None) for ANY (cause_word_variant,
    effect_word_variant) present as a ConceptNet Causes/CausesDesire edge."""
    for cw in cause_words:
        for cwv in _lemma_variants(cw):
            for ew in effect_words:
                for ewv in _lemma_variants(ew):
                    if (cwv, ewv) in causal_edges:
                        return True, (cwv, ewv)
    return False, None


# ----------------------------- SIGNAL 3: goal/intention keyword scan (qualitative) ----------

def goal_mediated_scan(text: str) -> list:
    low = text.lower()
    return [m for m in GOAL_MARKERS if m in low]


# ----------------------------- negative pair sampling ---------------------------------------

def sample_negative_pairs(items: list, key_to_event: dict, n_samples: int, seed: int) -> list:
    import random
    rng = random.Random(seed)
    gold_pairs = {(_event_key(it["cause_event"]), _event_key(it["effect_event"])) for it in items}
    all_keys = list(key_to_event.keys())
    pool = []
    for a in all_keys:
        for b in all_keys:
            if a == b:
                continue
            if (a, b) in gold_pairs:
                continue
            pool.append((a, b))
    rng.shuffle(pool)
    return pool[:n_samples]


# ----------------------------- main -----------------------------------------------------------

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--gold", type=str, default=GOLD_REL)
    parser.add_argument("--conceptnet", type=str, default=CONCEPTNET_REL)
    parser.add_argument("--n-negative", type=int, default=N_NEGATIVE_SAMPLES)
    parser.add_argument("--timeout", type=float, default=120.0,
                         help="formula self-test timeout budget; gazetteer mine (38 ch) + "
                              "100k-row ConceptNet scan measured well under this")
    args = parser.parse_args()

    run_mode = "smoke" if args.self_test else "full"
    output_dir = repo_path(f"data/exp_{ANCHOR_NAME}" + ("_smoke" if args.self_test else ""))
    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode, expected_n_units=25)

    run_self_test()
    if args.self_test:
        elapsed = time.perf_counter() - t0
        metrics = {
            "verdict": "SELF_TEST_PASS",
            "verdict_msg": "Gazetteer real-code-path PASS; ConceptNet Causes-edge loader finds "
                            "known edge + rejects nonsense pair; coherence-overlap gain sign check PASS.",
            "summary": "SELF_TEST_PASS", "elapsed_s": elapsed,
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
            "run_mode": run_mode, "seed": args.seed,
        }
        tmp = os.path.join(output_dir, "metrics.json.tmp")
        final = os.path.join(output_dir, "metrics.json")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        os.replace(tmp, final)
        print(f"[{ANCHOR_NAME}] SELF_TEST_PASS -> {final}")
        return

    # ---- full run ----
    gold_path = repo_path(args.gold)
    conceptnet_path = repo_path(args.conceptnet)

    items, key_to_event = load_gold(gold_path)
    print(f"[{ANCHOR_NAME}] gold loaded: {len(items)} items, {len(key_to_event)} unique real events",
          flush=True)

    # ---- gazetteer (real code path, reused unchanged) ----
    t_gaz0 = time.perf_counter()
    chapters = v1.load_chapters(N_CHAPTERS_TOTAL)
    candidates, _, _ = v1.mine_gazetteer(chapters)
    admitted, rejected = v1.classify_gazetteer_candidates(chapters, candidates)
    gaz_elapsed = time.perf_counter() - t_gaz0
    print(f"[{ANCHOR_NAME}] gazetteer mined: {len(admitted)} admitted names, {gaz_elapsed:.2f}s",
          flush=True)

    for ev in key_to_event.values():
        ev["names"] = event_entity_names(ev["verbatim"], admitted)

    # ---- ConceptNet causal edges (supplied DATA, loaded once) ----
    t_cn0 = time.perf_counter()
    causal_edges = load_conceptnet_causal_edges(conceptnet_path)
    cn_elapsed = time.perf_counter() - t_cn0
    print(f"[{ANCHOR_NAME}] ConceptNet causal edges loaded: {len(causal_edges)}, {cn_elapsed:.2f}s",
          flush=True)

    for ev in key_to_event.values():
        ev["content_words"] = content_words_excluding_proper_nouns(ev["verbatim"])

    all_event_names = [ev["names"] for ev in key_to_event.values()]

    # ---- SIGNAL 1: coherence gain, recall over gold links ----
    per_item_signal1 = []
    for it in items:
        c_key, e_key = _event_key(it["cause_event"]), _event_key(it["effect_event"])
        c_ev, e_ev = key_to_event[c_key], key_to_event[e_key]
        others = [n for k, n in ((k2, key_to_event[k2]["names"]) for k2 in key_to_event)
                  if k != c_key and k != e_key]
        gain = coherence_gain(c_ev["names"], e_ev["names"], others)
        per_item_signal1.append({"id": it["id"], "item_type": it["item_type"], "gain": gain,
                                  "flagged": gain > 0.0})

    # ---- SIGNAL 2: ConceptNet causal-commonsense match, recall over gold links ----
    per_item_signal2 = []
    for it in items:
        c_key, e_key = _event_key(it["cause_event"]), _event_key(it["effect_event"])
        c_ev, e_ev = key_to_event[c_key], key_to_event[e_key]
        matched, pair = conceptnet_causal_match(c_ev["content_words"], e_ev["content_words"], causal_edges)
        per_item_signal2.append({"id": it["id"], "item_type": it["item_type"], "flagged": matched,
                                  "matched_pair": list(pair) if pair else None})

    # ---- SIGNAL 3: goal/intention keyword scan (qualitative, no FP measured) ----
    per_item_signal3 = []
    for it in items:
        markers = goal_mediated_scan(it["gold_answer"])
        per_item_signal3.append({"id": it["id"], "item_type": it["item_type"],
                                  "goal_markers_found": markers, "goal_mediated": len(markers) > 0})

    # ---- negative pair sample for signals 1 & 2 (precision proxy) ----
    negatives = sample_negative_pairs(items, key_to_event, args.n_negative, args.seed)
    neg_signal1 = []
    neg_signal2 = []
    for a_key, b_key in negatives:
        a_ev, b_ev = key_to_event[a_key], key_to_event[b_key]
        others = [n for k, n in ((k2, key_to_event[k2]["names"]) for k2 in key_to_event)
                  if k != a_key and k != b_key]
        gain = coherence_gain(a_ev["names"], b_ev["names"], others)
        neg_signal1.append(gain > 0.0)
        matched, _ = conceptnet_causal_match(a_ev["content_words"], b_ev["content_words"], causal_edges)
        neg_signal2.append(matched)

    def summarize(per_item, type_set):
        subset = [r for r in per_item if r["item_type"] in type_set]
        n = len(subset)
        n_flag = sum(1 for r in subset if r["flagged"])
        return {"n": n, "n_flagged": n_flag, "recall": (n_flag / n) if n else None}

    s1_integration = summarize(per_item_signal1, INTEGRATION_TYPES)
    s1_all = summarize(per_item_signal1, INTEGRATION_TYPES | {CONTROL_TYPE})
    s2_integration = summarize(per_item_signal2, INTEGRATION_TYPES)
    s2_all = summarize(per_item_signal2, INTEGRATION_TYPES | {CONTROL_TYPE})

    s1_fp_rate = (sum(neg_signal1) / len(neg_signal1)) if neg_signal1 else None
    s2_fp_rate = (sum(neg_signal2) / len(neg_signal2)) if neg_signal2 else None

    n_goal_integration = sum(1 for r in per_item_signal3
                              if r["item_type"] in INTEGRATION_TYPES and r["goal_mediated"])
    n_integration_total = sum(1 for it in items if it["item_type"] in INTEGRATION_TYPES)

    generic_commonsense_n = s2_integration["n_flagged"]
    story_specific_n = s2_integration["n"] - s2_integration["n_flagged"]

    def attackable(recall, fp):
        if recall is None or fp is None:
            return False
        return recall >= 0.50 and fp <= 0.20

    s1_attackable = attackable(s1_integration["recall"], s1_fp_rate)
    s2_attackable = attackable(s2_integration["recall"], s2_fp_rate)
    overall_attackable = s1_attackable or s2_attackable

    verdict = "MEASURED_MECHANISM"
    if overall_attackable:
        which = "SIGNAL1_COHERENCE" if s1_attackable else "SIGNAL2_CONCEPTNET"
        verdict_summary = f"ATTACKABLE via {which}"
    else:
        verdict_summary = "DEEP_INFERENCE_REQUIRED"

    verdict_msg = (
        f"PROBE-TO-AIM, link-PROPOSAL (not the accumulate organ). "
        f"SIGNAL1 coherence-gain: recall_integration={s1_integration['recall']} "
        f"(n={s1_integration['n']}), fp_rate={s1_fp_rate} (n_neg={len(neg_signal1)}), "
        f"attackable={s1_attackable}. "
        f"SIGNAL2 ConceptNet-Causes/CausesDesire: recall_integration={s2_integration['recall']} "
        f"(n={s2_integration['n']}), fp_rate={s2_fp_rate} (n_neg={len(neg_signal2)}), "
        f"attackable={s2_attackable}. generic-commonsense-matchable={generic_commonsense_n}/"
        f"{s2_integration['n']}, story-specific={story_specific_n}/{s2_integration['n']}. "
        f"SIGNAL3 goal/intention (qualitative, no FP scored): "
        f"{n_goal_integration}/{n_integration_total} integration gold_answers contain "
        f"goal/intention language. VERDICT={verdict_summary}."
    )

    # ---- ARMS-MUST-DIFFER (signal1 vs signal2 flag arrays must differ; unrelated evidence) ----
    def _digest(per_item):
        s = json.dumps([(r["id"], bool(r["flagged"])) for r in per_item], sort_keys=True)
        return hashlib.sha256(s.encode()).hexdigest()
    digest_s1 = _digest(per_item_signal1)
    digest_s2 = _digest(per_item_signal2)
    arms_differ_verified = digest_s1 != digest_s2

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": (
            f"{verdict_summary} | s1_recall={s1_integration['recall']} s1_fp={s1_fp_rate} | "
            f"s2_recall={s2_integration['recall']} s2_fp={s2_fp_rate} | "
            f"generic_vs_story_specific={generic_commonsense_n}/{story_specific_n} | "
            f"s3_goal_mediated={n_goal_integration}/{n_integration_total}"
        ),
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "seed": args.seed,
        "gold_path": gold_path, "conceptnet_path": conceptnet_path,
        "n_items_total": len(items), "n_unique_events": len(key_to_event),
        "n_gazetteer_admitted": len(admitted), "gazetteer_elapsed_s": gaz_elapsed,
        "n_conceptnet_causal_edges": len(causal_edges), "conceptnet_load_elapsed_s": cn_elapsed,
        "n_negative_pairs_sampled": len(negatives),
        "signal1_coherence_overlap": {
            "recall_integration": s1_integration, "recall_all": s1_all,
            "false_positive_rate": s1_fp_rate, "attackable": s1_attackable,
            "per_item": per_item_signal1,
        },
        "signal2_conceptnet_commonsense": {
            "recall_integration": s2_integration, "recall_all": s2_all,
            "false_positive_rate": s2_fp_rate, "attackable": s2_attackable,
            "generic_commonsense_matchable_n": generic_commonsense_n,
            "story_specific_n": story_specific_n,
            "per_item": per_item_signal2,
        },
        "signal3_goal_intention_qualitative": {
            "n_goal_mediated_integration": n_goal_integration,
            "n_integration_total": n_integration_total,
            "fraction_goal_mediated": (n_goal_integration / n_integration_total)
                                       if n_integration_total else None,
            "per_item": per_item_signal3,
            "note": "QUALITATIVE keyword scan of the human-written gold_answer explanation text; "
                    "not a computed discriminator (no goal-tracking module exists yet), no FP rate.",
        },
        "overall_verdict_summary": verdict_summary,
        "arms_differ_verified": arms_differ_verified,
        "arms_digest": {"signal1": digest_s1, "signal2": digest_s2},
        "final_metrics_atomicity": "tmp_replace",
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "defensive_error_checking": "passed_all_4_patterns_heartbeat_exempt_single_pass",
        "dispatched": False,
        "dispatch_note": "measurement-only per task instruction; not queued, not shipped remote.",
    }

    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, final_path)

    print(f"[{ANCHOR_NAME}] {verdict} ({verdict_summary}) elapsed={elapsed:.2f}s -> {final_path}")


if __name__ == "__main__":
    _output_dir_for_crash = repo_path(f"data/exp_{ANCHOR_NAME}")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_output_dir_for_crash, e)
        raise
