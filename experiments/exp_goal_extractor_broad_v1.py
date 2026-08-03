"""exp_goal_extractor_broad_v1 (2026-08-03)

MEASUREMENT cell (not a probe, not a full re-architecture): does a BROADER glass-box goal
extractor -- syntactic-pattern goal CONSTRUCTIONS, not just a broader keyword lexicon -- lift the
goal-extraction recall AND the end-to-end causal-link recall above the commit 1400331cc lexicon
baseline (extraction_recall_explicit=2/18=0.111, causal-link recall_goal_mediated=1/9=0.111,
fp_rate=0.000)?

Prior-work check (mandatory, USER-locked 2026-07-01): `bash tools/substrate_query.sh "goal
desiderative purpose clause causal link extraction"` -> top cosine=0.3359 ("relative clause",
concept atoms / wordnet), next "Cause_change::Purpose" FrameNet frame at cosine=0.3164. No prior
arc cell above cosine 0.30 builds a construction-based (non-lexicon) goal extractor. commit
1400331cc IS the cited baseline this cell attacks, not a duplicate of it -- this is a genuine
extension (ONE lever: broaden the EXTRACTION mechanism from marker-substring-only to
marker-substring + two syntactic constructions), not a rediscovery.

ONE LEVER UNDER TEST: broaden goal-OPEN extraction from lexicon-substring-only to THREE detection
channels, all glass-box (regex/substring over the SAME hdlab clause-split stream, NO dependency
parser, NO bolt-on/LLM):
  (a) LEXICAL marker (unchanged mechanism, BROADENED list): the original GOAL_OPEN_MARKERS
      (commit 1400331cc, imported unchanged) plus supplied desiderative/commissive LUs in the
      spirit of the FrameNet Desiring / Intentionally_act frames (want, wish, long, hope, mean,
      intend, resolve, decide, aim + commissive "I'll"/"I will"/"I shall"). NOTE: data/framenet_cache
      is empty on disk (checked this cell -- no framenet.api file present); these additions are
      CITED@FrameNet Desiring frame LU conventions (linguistic knowledge), not pulled from a local
      cache file -- reported honestly, not claimed as "loaded from repo".
  (b) PURPOSE_CLAUSE construction: a clause (after the existing hdlab clause-split) that begins
      with a bare infinitival "to VERB" -- catches purpose clauses split off by the clause
      splitter's comma/semicolon boundary (e.g. ", to win the race she trained every day") that no
      lexical marker would catch.
  (c) MODAL_VOLITION construction: a clause containing "would"/"'d" AND "if" -- catches
      counterfactual-wish/conditional-desire constructions (e.g. "I'd be ever so much gratefuller
      if--if you'd made just one of them with puffed sleeves", the anne_goal_001 gold item
      EXPLICITLY named in the task brief as motivating this construction).

Everything downstream of goal-OPEN extraction (agent-binding via
hdlab.coreference_resolver.run_match_or_allocate, the CLOSE-marker search, the
hdlab.situation_model_accumulate.CausalLinkRegister open/close proposal organ, the fuzzy
clause<->event gold matching, the negative-pair sampling) is REUSED UNCHANGED from
experiments/exp_goal_register_causal_link_v1.py (imported, not re-implemented) so the ONLY
variable between this cell and the 1400331cc baseline is the goal-open extraction breadth.

MEASURE (three questions from the task):
  1. extraction_recall_explicit / a chapter+same-character precision proxy vs the same 18-item
     explicit-goal gold, broad-extractor vs the 1400331cc lexicon-only baseline (read live off
     data/exp_goal_register_causal_link_v1/metrics.json, not hardcoded).
  2. END-TO-END causal-link recall_goal_mediated / fp_rate over the SAME 9 goal-mediated gold
     links + SAME seed=20260803/n=200 negative-pair methodology, broad vs baseline.
  3. RESIDUAL ceiling: for each of the 21 gold goal items (18 explicit + 3 inferred), test the
     GOLD VERBATIM SPAN ITSELF (not the noisy extraction pipeline) against all three construction
     channels -- this isolates true pattern-coverage (can ANY glass-box pattern conceivably fire on
     this text) from pipeline noise (agent-binding / clause-boundary mismatches). Items where no
     channel fires are the honest NEEDS-DEEPER-inference residual (no marker, no purpose-infinitive,
     no modal-volition -- e.g. implied-speech-act or purposeful-action goals with zero lexical
     surface signal).

CAN-FAIL / VERDICT (per task instruction, not forced): HARD_PASS-ish if extraction recall lifts
materially (targeting >=0.5) AND end-to-end causal-link recall lifts to >=0.4 at low FP (materially
below coherence-baseline fp, same gate shape as 1400331cc's own HARD_PASS gate) -> the broadened
glass-box lever WORKS, recommend wiring. Otherwise: honest MIDDLE_BAND/NULL with a diagnosis
(extraction-still-noisy vs pairing-too-loose vs residual dominated by inferential goals) -- no
regime-tuning to force a pass; a reasonable, once-through pattern set, not endless iteration.

CELL-TEMPLATE (light form -- single foreground measurement pass, no sweep axis, no dispatch):
  - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
  - final_metrics_atomicity = tmp_replace
  - arms_differ_verified: broad-extractor flagged-pair set vs baseline (1400331cc) flagged-pair
    set digest-compared (must differ if the broadening changes anything)
  - heartbeat/chunking EXEMPTED: single pass, <=3s book pipeline (measured on baseline cell,
    elapsed_s=2.63s at N=38 chapters) + cheap regex scans, no training
  - determinism: fixed SEED=20260803 (matches baseline for apples-to-apples negative sampling),
    python random.Random(seed) only, sorted() wherever iteration order matters
  - all narrative numbers in this docstring are HYPOTHESIZED/directional; every number in the
    completion report is tagged MEASURED@ against this cell's own metrics.json (or the baseline's,
    when read live for comparison)
  - NOT DISPATCHED: runs to completion locally, no queue_add, no remote verify, per task instruction.
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

import torch  # noqa: E402

import read_anne_glassbox_v1 as v1  # noqa: E402
import experiments.exp_goal_register_causal_link_v1 as baseline  # noqa: E402
from hdlab.situation_model_accumulate import CausalLinkRegister  # noqa: E402

ANCHOR_NAME = "goal_extractor_broad_v1"
BASELINE_METRICS_REL = "data/exp_goal_register_causal_link_v1/metrics.json"
N_CHAPTERS_TOTAL = baseline.N_CHAPTERS_TOTAL
SEED = baseline.SEED
N_NEGATIVE_SAMPLES = baseline.N_NEGATIVE_SAMPLES
FHRR_DIM = baseline.FHRR_DIM
GOAL_MEDIATED_CAUSAL_IDS = baseline.GOAL_MEDIATED_CAUSAL_IDS
INTEGRATION_TYPES = baseline.INTEGRATION_TYPES
GOAL_GOLD_REL = baseline.GOAL_GOLD_REL
CAUSAL_GOLD_REL = baseline.CAUSAL_GOLD_REL

# Supplied DATA: original lexicon (commit 1400331cc) unchanged, plus NEW desiderative/commissive
# additions in the spirit of the FrameNet Desiring frame (want/wish/long/hope/mean/intend/aim) and
# commissive speech-acts ("I'll"/"I will"/"I shall" + VERB). CITED@FrameNet Desiring frame LU
# conventions (linguistic knowledge -- data/framenet_cache has no local LU list file on disk, see
# docstring) -- this is a hand-broadened lexicon extension, not a pulled-from-repo list.
NEW_DESIDERATIVE_MARKERS = [
    "wish", "wishes", "wished", "long to", "longs to", "longed to",
    "mean to", "means to", "meant to", "aim to", "aims to", "aimed to",
    "i'll", "i will", "i shall", "crave", "craved", "yearn", "yearned", "vowed", "vow to",
]
ALL_LEXICAL_MARKERS = list(baseline.GOAL_OPEN_MARKERS) + NEW_DESIDERATIVE_MARKERS

PURPOSE_CLAUSE_RE = re.compile(r"^\s*to\s+[a-z]")
MODAL_VOLITION_WOULD_RE = re.compile(r"\b(?:would|'d)\b")
MODAL_VOLITION_IF_RE = re.compile(r"\bif\b")


def construction_fire(low: str):
    """Return (construction_type, marker) for the FIRST channel that fires on a lowercased clause,
    or (None, None). Channel order: lexical, purpose_clause, modal_volition (order is a reporting
    convention only -- a clause firing more than one channel is still counted once as "reachable").
    Normalizes the curly apostrophe (U+2019) to straight (') FIRST -- the book source uses curly
    quotes throughout ("I’ll", "I’d") and marker/regex literals are written with straight
    apostrophes; without this normalization "i'll"/"'d" never match (same bug class documented in
    read_anne_glassbox_v1's _base_token clitic-stripping fix, 2026-08-02)."""
    low = low.replace("’", "'")
    hit = next((m for m in ALL_LEXICAL_MARKERS if m in low), None)
    if hit is not None:
        return "lexical", hit
    if PURPOSE_CLAUSE_RE.match(low.strip()):
        return "purpose_clause", "to+VERB"
    if MODAL_VOLITION_WOULD_RE.search(low) and MODAL_VOLITION_IF_RE.search(low):
        return "modal_volition", "would/'d...if"
    return None, None


def extract_goal_opens_broad(clauses_text, agent_eid):
    """AUTOMATED explicit-goal-open detection over THREE construction channels (see module
    docstring). Same clause-level agent-binding precondition as the baseline extractor: the
    clause's agent-role entity must be resolved (non-None)."""
    opens = []
    for idx, ctext in enumerate(clauses_text):
        eid = agent_eid.get(idx)
        if eid is None:
            continue
        low = ctext.lower()
        ctype, marker = construction_fire(low)
        if ctype is None:
            continue
        opens.append({"clause_idx": idx, "eid": eid, "marker": marker,
                       "construction_type": ctype, "text": ctext})
    return opens


def pattern_fires_on_text(text: str):
    """Residual-ceiling probe: does ANY of the three construction channels fire ANYWHERE in this
    raw gold verbatim span, independent of the extraction pipeline's agent-binding / clause
    boundaries? Splits the same way the real pipeline would (v1.sentence_split + v1.clause_split)
    so the test is apples-to-apples with what the extractor could ever see, but skips the
    agent-resolved precondition (this measures PATTERN reachability, not pipeline recall)."""
    for sent in v1.sentence_split(text):
        for clause in v1.clause_split(sent):
            low = clause.lower()
            ctype, marker = construction_fire(low)
            if ctype is not None:
                return True, ctype, marker
    return False, None, None


def lexical_only_fires_on_text(text: str, markers):
    for sent in v1.sentence_split(text):
        for clause in v1.clause_split(sent):
            low = clause.lower()
            if any(m in low for m in markers):
                return True
    return False


# --------------------------------------------------------------------------------------------
# Self-test: construction fixtures + reuse of the baseline module's own self-test (organ +
# lexical-branch sanity), per real-code-path gate F.1.
# --------------------------------------------------------------------------------------------
def run_self_test() -> None:
    baseline.run_self_test()  # underlying register organ + baseline lexical extractor still sane

    clauses_text = [
        "Anne wished to win the race",                    # (0) lexical: "wish"
        "the sky was blue that afternoon",                 # (1) no agent -> must skip
        "to win the race she trained every day",           # (2) purpose_clause
        "she would be happier if she trained harder",      # (3) modal_volition
        "Diana laughed at the joke",                       # (4) no construction -> must NOT fire
    ]
    agent_eid = {0: 0, 1: None, 2: 0, 3: 0, 4: 1}
    opens = extract_goal_opens_broad(clauses_text, agent_eid)
    fired_idxs = {o["clause_idx"] for o in opens}
    assert {0, 2, 3}.issubset(fired_idxs), f"SELF_TEST FAIL: expected constructions to fire, got {opens}"
    assert 1 not in fired_idxs and 4 not in fired_idxs, f"SELF_TEST FAIL: unexpected fire in {opens}"
    types = {o["clause_idx"]: o["construction_type"] for o in opens}
    assert types[0] == "lexical", f"SELF_TEST FAIL: {types}"
    assert types[2] == "purpose_clause", f"SELF_TEST FAIL: {types}"
    assert types[3] == "modal_volition", f"SELF_TEST FAIL: {types}"

    # residual-ceiling probe fixtures
    fires, ctype, _ = pattern_fires_on_text("She was determined to leave at once.")
    assert fires and ctype == "lexical"
    fires2, ctype2, _ = pattern_fires_on_text("Mary looked at the door quietly and said nothing.")
    assert not fires2, f"SELF_TEST FAIL: unexpected residual-probe fire: {ctype2}"

    # real-code-path check on the actual gold-goal jsonl schema (gate F.1): confirm the file loads
    # and the residual probe runs cleanly over a real verbatim span from the gold file.
    with open(baseline.repo_path(GOAL_GOLD_REL), "r", encoding="utf-8") as f:
        first_item = json.loads(next(iter(f)))
    assert "verbatim_evidence" in first_item and "verbatim" in first_item["verbatim_evidence"]
    _ = pattern_fires_on_text(first_item["verbatim_evidence"]["verbatim"])


# --------------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------------
def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--n-negative", type=int, default=N_NEGATIVE_SAMPLES)
    parser.add_argument("--timeout", type=float, default=300.0,
                         help="formula self-test timeout budget; 38-chapter extraction + coref + "
                              "forward-scan measured ~2.6s at baseline (1400331cc); this cell adds "
                              "only cheap regex checks on top, well under this budget")
    args = parser.parse_args()

    run_mode = "smoke" if args.self_test else "full"
    output_dir = baseline.repo_path(f"data/exp_{ANCHOR_NAME}" + ("_smoke" if args.self_test else ""))
    t0 = time.perf_counter()
    baseline._write_start_marker(output_dir, run_mode, expected_n_units=25)

    run_self_test()
    if args.self_test:
        elapsed = time.perf_counter() - t0
        metrics = {
            "verdict": "SELF_TEST_PASS",
            "verdict_msg": "construction-fire fixtures PASS (lexical/purpose_clause/modal_volition); "
                            "negative fixtures PASS; residual-ceiling probe fixtures PASS; "
                            "baseline module self-test (organ + lexical branch) PASS.",
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

    # ---- 1. book-wide automated extraction + coreference (reused pipeline, unchanged) ----
    t_pipe0 = time.perf_counter()
    pipe = baseline.build_book_pipeline(N_CHAPTERS_TOTAL)
    pipe_elapsed = time.perf_counter() - t_pipe0
    print(f"[{ANCHOR_NAME}] book pipeline built: {len(pipe['clauses_text'])} clauses, "
          f"{len(pipe['gazetteer'])} gazetteer names, {pipe_elapsed:.2f}s", flush=True)

    opens_broad = extract_goal_opens_broad(pipe["clauses_text"], pipe["agent_eid"])
    opens_lex_only = baseline.extract_goal_opens(pipe["clauses_text"], pipe["agent_eid"],
                                                  markers=baseline.GOAL_OPEN_MARKERS)
    print(f"[{ANCHOR_NAME}] automated goal-opens: broad={len(opens_broad)} "
          f"lex_only_rebuilt={len(opens_lex_only)}", flush=True)

    construction_counts = {}
    for o in opens_broad:
        construction_counts[o["construction_type"]] = construction_counts.get(o["construction_type"], 0) + 1

    # ---- 2. extraction recall/precision vs the 18-item explicit goal gold ----
    with open(baseline.repo_path(GOAL_GOLD_REL), "r", encoding="utf-8") as f:
        goal_gold_items = [json.loads(line) for line in f if line.strip()]
    explicit_gold = [it for it in goal_gold_items if it["explicit_vs_inferred"] == "explicit"]
    inferred_gold = [it for it in goal_gold_items if it["explicit_vs_inferred"] == "inferred"]

    def name_matches(extracted_name, gold_character):
        en = extracted_name.lower()
        gc = gold_character.lower()
        gc_toks = set(re.findall(r"[a-z]+", gc))
        return en in gc_toks or en in gc

    def score_extraction(opens, label):
        n_matched = 0
        per_item = []
        for it in explicit_gold:
            ev = it["verbatim_evidence"]
            chapter, verbatim = ev["chapter"], ev["verbatim"]
            matched_open = None
            for o in opens:
                if pipe["clause_chapter"][o["clause_idx"]] != chapter:
                    continue
                if not baseline.clause_matches_event(o["text"], verbatim):
                    continue
                ename = pipe["eid_to_name"].get(o["eid"], "")
                if not name_matches(ename, it["character"]):
                    continue
                matched_open = o
                break
            found = matched_open is not None
            n_matched += int(found)
            per_item.append({"id": it["id"], "matched": found,
                              "construction_type": matched_open.get("construction_type") if matched_open else None})
        recall = n_matched / len(explicit_gold) if explicit_gold else None
        gold_chapters = {it["verbatim_evidence"]["chapter"] for it in explicit_gold}
        n_in_gold_ch = sum(1 for o in opens if pipe["clause_chapter"][o["clause_idx"]] in gold_chapters)
        # stronger precision proxy: opens in a gold chapter AND matching a gold character's resolved
        # name in that chapter (weak proxy still, gold is a SAMPLE not exhaustive, but tighter than
        # chapter-only).
        gold_names_by_ch = {}
        for it in explicit_gold:
            gold_names_by_ch.setdefault(it["verbatim_evidence"]["chapter"], set()).add(it["character"].lower())
        n_ch_and_char = 0
        for o in opens:
            ch = pipe["clause_chapter"][o["clause_idx"]]
            if ch not in gold_names_by_ch:
                continue
            ename = pipe["eid_to_name"].get(o["eid"], "").lower()
            if any(ename in gc or ename in set(re.findall(r"[a-z]+", gc)) for gc in gold_names_by_ch[ch]):
                n_ch_and_char += 1
        chapter_precision_proxy = n_in_gold_ch / len(opens) if opens else None
        chapter_and_character_precision_proxy = n_ch_and_char / len(opens) if opens else None
        return {
            "label": label, "n_opens_total": len(opens), "n_matched_explicit_gold": n_matched,
            "extraction_recall_explicit": recall, "chapter_precision_proxy": chapter_precision_proxy,
            "chapter_and_character_precision_proxy": chapter_and_character_precision_proxy,
            "per_item": per_item,
        }

    extraction_broad = score_extraction(opens_broad, "broad_construction")
    extraction_lex_rebuilt = score_extraction(opens_lex_only, "lexical_only_rebuilt_this_run")

    # ---- 3. residual ceiling: pattern-reachability test on the GOLD VERBATIM SPANS themselves ----
    residual = []
    n_reachable_broad = 0
    n_reachable_lexonly = 0
    for it in goal_gold_items:
        verbatim = it["verbatim_evidence"]["verbatim"]
        fires, ctype, marker = pattern_fires_on_text(verbatim)
        lex_fires = lexical_only_fires_on_text(verbatim, baseline.GOAL_OPEN_MARKERS)
        n_reachable_broad += int(fires)
        n_reachable_lexonly += int(lex_fires)
        residual.append({
            "id": it["id"], "explicit_vs_inferred": it["explicit_vs_inferred"],
            "lexical_goal_marker_present_gold_field": it["lexical_goal_marker_present"],
            "broad_pattern_reachable": fires, "broad_construction_type": ctype,
            "lexical_only_baseline_reachable": lex_fires,
        })
    n_total_gold = len(goal_gold_items)
    n_explicit = len(explicit_gold)
    unreachable_broad = [r for r in residual if not r["broad_pattern_reachable"]]
    unreachable_broad_explicit = [r for r in unreachable_broad
                                   if r["explicit_vs_inferred"] == "explicit"]
    residual_unreachable_fraction_all = len(unreachable_broad) / n_total_gold if n_total_gold else None
    residual_unreachable_fraction_explicit = (
        len(unreachable_broad_explicit) / n_explicit if n_explicit else None)

    # ---- 4. OPEN/CLOSE GOAL REGISTER + causal-link proposal, broad extractor (reuse organ) ----
    def run_register_and_causal(opens, label):
        gen = torch.Generator().manual_seed(args.seed)
        proposed_links = []
        n_self_consistent = 0
        for o in opens:
            close_idx, close_marker = baseline.find_close_for_open(
                o["clause_idx"], o["eid"], pipe["clauses_text"], pipe["agent_eid"])
            if close_idx is None:
                continue
            reg = CausalLinkRegister(d=FHRR_DIM, generator=gen, max_event_slots=2)
            reg.add_causal_link(0, 1)
            eff, _ = reg.query_effect_of(0)
            cau, _ = reg.query_cause_of(1)
            self_consistent = (eff == 1 and cau == 0)
            n_self_consistent += int(self_consistent)
            proposed_links.append({
                "open_clause_idx": o["clause_idx"], "close_clause_idx": close_idx,
                "eid": o["eid"], "open_chapter": pipe["clause_chapter"][o["clause_idx"]],
                "close_chapter": pipe["clause_chapter"][close_idx],
                "register_self_consistent": self_consistent,
            })
        organ_rate = n_self_consistent / len(proposed_links) if proposed_links else None

        with open(baseline.repo_path(CAUSAL_GOLD_REL), "r", encoding="utf-8") as f:
            causal_items = [json.loads(line) for line in f if line.strip()]

        def event_key(ev):
            lr = ev["line_range"]
            return (ev["chapter"], lr[0], lr[1])

        key_to_event = {}
        for it in causal_items:
            for side in ("cause_event", "effect_event"):
                ev = it[side]
                k = event_key(ev)
                if k not in key_to_event:
                    key_to_event[k] = {"chapter": ev["chapter"], "verbatim": ev["verbatim"]}
        event_key_by_chapter = {}
        for k, ev in key_to_event.items():
            event_key_by_chapter.setdefault(ev["chapter"], []).append(k)

        flagged_pairs = set()
        for link in proposed_links:
            open_candidates = [
                k for k in event_key_by_chapter.get(link["open_chapter"], [])
                if baseline.clause_matches_event(pipe["clauses_text"][link["open_clause_idx"]],
                                                  key_to_event[k]["verbatim"])
            ]
            close_candidates = [
                k for k in event_key_by_chapter.get(link["close_chapter"], [])
                if baseline.clause_matches_event(pipe["clauses_text"][link["close_clause_idx"]],
                                                  key_to_event[k]["verbatim"])
            ]
            for ko in open_candidates:
                for kc in close_candidates:
                    flagged_pairs.add((ko, kc))

        per_item = []
        n_flagged_goal_mediated = 0
        n_goal_mediated_total = 0
        for it in causal_items:
            ck, ek = event_key(it["cause_event"]), event_key(it["effect_event"])
            flagged = (ck, ek) in flagged_pairs
            is_goal_mediated = it["id"] in GOAL_MEDIATED_CAUSAL_IDS
            if is_goal_mediated:
                n_goal_mediated_total += 1
                n_flagged_goal_mediated += int(flagged)
            per_item.append({"id": it["id"], "goal_mediated": is_goal_mediated, "flagged": flagged})
        recall_goal_mediated = (n_flagged_goal_mediated / n_goal_mediated_total
                                 if n_goal_mediated_total else None)

        import random
        rng = random.Random(args.seed)
        gold_pairs = {(event_key(it["cause_event"]), event_key(it["effect_event"])) for it in causal_items}
        all_keys = sorted(key_to_event.keys())
        pool = [(a, b) for a in all_keys for b in all_keys if a != b and (a, b) not in gold_pairs]
        rng.shuffle(pool)
        negatives = pool[: args.n_negative]
        neg_flags = [(a, b) in flagged_pairs for a, b in negatives]
        fp_rate = (sum(neg_flags) / len(neg_flags)) if neg_flags else None

        return {
            "label": label, "n_proposed_links": len(proposed_links),
            "organ_self_consistency_rate": organ_rate,
            "recall_goal_mediated": recall_goal_mediated, "n_goal_mediated_total": n_goal_mediated_total,
            "fp_rate": fp_rate, "n_negative_sampled": len(negatives),
            "flagged_ids": sorted(r["id"] for r in per_item if r["flagged"]),
            "per_item": per_item,
        }

    causal_broad = run_register_and_causal(opens_broad, "broad_construction")

    # ---- 5. baseline comparison, read LIVE off disk (single source of truth, not hardcoded) ----
    with open(baseline.repo_path(BASELINE_METRICS_REL), "r", encoding="utf-8") as f:
        baseline_metrics = json.load(f)
    baseline_extraction_recall = baseline_metrics["automated_goal_extraction"]["extraction_recall_explicit"]
    baseline_causal_recall = baseline_metrics["causal_link_proposal"]["recall_goal_mediated"]
    baseline_causal_fp = baseline_metrics["causal_link_proposal"]["fp_rate"]
    coherence_recall = baseline_metrics["comparison"]["coherence_baseline"]["recall_integration"]
    coherence_fp = baseline_metrics["comparison"]["coherence_baseline"]["fp_rate"]
    upper_bound_explicit = baseline_metrics["comparison"]["hand_matched_upper_bound"]["explicit_only_fraction"]

    # ---- 6. verdict (per task instruction gate: NOT forced) ----
    def hard_pass_ish(extraction_recall, link_recall, fp):
        if extraction_recall is None or link_recall is None or fp is None:
            return False
        return extraction_recall >= 0.5 and link_recall >= 0.4 and fp <= max(0.15, 0.5 * coherence_fp)

    hp = hard_pass_ish(extraction_broad["extraction_recall_explicit"],
                        causal_broad["recall_goal_mediated"], causal_broad["fp_rate"])
    lifted_materially = (
        extraction_broad["extraction_recall_explicit"] is not None
        and baseline_extraction_recall is not None
        and extraction_broad["extraction_recall_explicit"] > baseline_extraction_recall + 1e-9
    ) or (
        causal_broad["recall_goal_mediated"] is not None
        and baseline_causal_recall is not None
        and causal_broad["recall_goal_mediated"] > baseline_causal_recall + 1e-9
    )
    if hp:
        verdict_summary = "HARD_PASS_BROAD_EXTRACTOR_BEATS_TARGET"
    elif lifted_materially:
        verdict_summary = "MIDDLE_BAND_LIFTS_BUT_BELOW_TARGET"
    else:
        verdict_summary = "NULL_NO_MATERIAL_LIFT_RESIDUAL_IS_INFERENTIAL"

    diagnosis = None
    if verdict_summary != "HARD_PASS_BROAD_EXTRACTOR_BEATS_TARGET":
        if residual_unreachable_fraction_explicit is not None and residual_unreachable_fraction_explicit >= 0.25:
            diagnosis = (
                f"RESIDUAL_DOMINATED_BY_INFERENTIAL_GOALS: {len(unreachable_broad_explicit)}/{n_explicit} "
                "explicit gold items have NO textual construction (lexical, purpose-infinitive, or "
                "modal-volition) anywhere in their gold verbatim span -- these need deeper inference "
                "(speech-act / purposeful-action goals), not a broader pattern set.")
        elif not lifted_materially:
            diagnosis = ("NO_LIFT: broadened construction set found the same or fewer matches than "
                          "the lexicon-only baseline on this pipeline run; pipeline-level noise "
                          "(agent-binding / clause-boundary mismatch) likely dominates over pattern "
                          "coverage as the bottleneck, not marker/construction breadth.")
        else:
            diagnosis = ("LIFTED_BUT_BELOW_TARGET: broadening helped measurably but pipeline noise "
                          "or open/close pairing looseness still caps recall below the HARD_PASS bar.")

    verdict_msg = (
        f"EXTRACTION: broad_recall_explicit={extraction_broad['extraction_recall_explicit']} "
        f"vs baseline_lexicon_recall={baseline_extraction_recall} (n={n_explicit}); "
        f"broad_chapter_precision_proxy={extraction_broad['chapter_precision_proxy']} "
        f"broad_chapter_and_char_precision_proxy={extraction_broad['chapter_and_character_precision_proxy']}. "
        f"CAUSAL-LINK: broad_recall_goal_mediated={causal_broad['recall_goal_mediated']} "
        f"broad_fp={causal_broad['fp_rate']} vs baseline_recall={baseline_causal_recall} "
        f"baseline_fp={baseline_causal_fp} vs coherence_recall={coherence_recall} "
        f"coherence_fp={coherence_fp} vs hand_matched_upper_bound_explicit={upper_bound_explicit}. "
        f"RESIDUAL: unreachable_fraction_explicit={residual_unreachable_fraction_explicit} "
        f"({len(unreachable_broad_explicit)}/{n_explicit}), unreachable_fraction_all_21={residual_unreachable_fraction_all}. "
        f"VERDICT={verdict_summary}." + (f" DIAGNOSIS={diagnosis}" if diagnosis else "")
    )

    # ---- ARMS-MUST-DIFFER: broad-flagged pair set vs baseline (1400331cc)-flagged pair set ----
    baseline_flagged_ids = set(baseline_metrics["causal_link_proposal"].get(
        "flagged_ids", [r["id"] for r in baseline_metrics["causal_link_proposal"]["per_item"] if r["flagged"]]))
    broad_flagged_ids = set(causal_broad["flagged_ids"])
    digest_broad = hashlib.sha256(json.dumps(sorted(broad_flagged_ids)).encode()).hexdigest()
    digest_baseline = hashlib.sha256(json.dumps(sorted(baseline_flagged_ids)).encode()).hexdigest()
    arms_differ_verified = digest_broad != digest_baseline

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": "HARD_PASS" if hp else "MEASURED_MECHANISM",
        "verdict_msg": verdict_msg,
        "summary": (
            f"{verdict_summary} | broad_extraction_recall={extraction_broad['extraction_recall_explicit']} "
            f"(baseline={baseline_extraction_recall}) | broad_link_recall={causal_broad['recall_goal_mediated']} "
            f"fp={causal_broad['fp_rate']} (baseline_recall={baseline_causal_recall} baseline_fp={baseline_causal_fp}) "
            f"| residual_unreachable_explicit={residual_unreachable_fraction_explicit}"
        ),
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "seed": args.seed,
        "n_chapters": N_CHAPTERS_TOTAL, "n_clauses": len(pipe["clauses_text"]),
        "n_gazetteer_admitted": len(pipe["gazetteer"]), "pipeline_elapsed_s": pipe_elapsed,
        "construction_counts_broad_extractor": construction_counts,
        "extraction": {"broad": extraction_broad, "lexical_only_rebuilt_this_run": extraction_lex_rebuilt,
                       "baseline_1400331cc_recall_explicit": baseline_extraction_recall},
        "residual_ceiling": {
            "n_total_gold_items": n_total_gold, "n_explicit_gold": n_explicit,
            "n_inferred_gold": len(inferred_gold),
            "n_reachable_broad_construction": n_reachable_broad,
            "n_reachable_lexical_only": n_reachable_lexonly,
            "unreachable_fraction_explicit": residual_unreachable_fraction_explicit,
            "unreachable_fraction_all": residual_unreachable_fraction_all,
            "unreachable_explicit_ids": [r["id"] for r in unreachable_broad_explicit],
            "per_item": residual,
        },
        "causal_link_proposal": causal_broad,
        "comparison": {
            "baseline_1400331cc": {"extraction_recall_explicit": baseline_extraction_recall,
                                    "recall_goal_mediated": baseline_causal_recall, "fp_rate": baseline_causal_fp,
                                    "source": BASELINE_METRICS_REL},
            "coherence_baseline": {"recall_integration": coherence_recall, "fp_rate": coherence_fp,
                                    "source_commit": "912077b81"},
            "hand_matched_upper_bound_explicit": upper_bound_explicit,
        },
        "hard_pass_gate": {
            "extraction_recall_threshold": 0.5, "link_recall_threshold": 0.4,
            "fp_rate_threshold": max(0.15, 0.5 * coherence_fp), "hard_pass": hp,
            "lifted_materially_vs_baseline": lifted_materially,
            "diagnosis_if_not_hard_pass": diagnosis,
        },
        "arms_differ_verified": arms_differ_verified,
        "arms_digest": {"broad_construction": digest_broad, "baseline_1400331cc": digest_baseline},
        "final_metrics_atomicity": "tmp_replace",
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "defensive_error_checking": "passed_all_4_patterns_heartbeat_exempt_single_pass",
        "deterministic_seeding": True,
        "dispatched": False,
        "dispatch_note": "measurement-only per task instruction; not queued, not shipped remote.",
    }

    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, final_path)

    print(f"[{ANCHOR_NAME}] {metrics['verdict']} ({verdict_summary}) elapsed={elapsed:.2f}s -> {final_path}")


if __name__ == "__main__":
    _output_dir_for_crash = baseline.repo_path(f"data/exp_{ANCHOR_NAME}")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        baseline._write_crash_metrics(_output_dir_for_crash, e)
        raise
