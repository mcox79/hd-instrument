"""tools/measure_definitional_pattern_association_v1.py

STEP-1 DIAGNOSIS MEASUREMENT (2026-08-12). Confirm or REFUTE the director's hypothesis:

  "the grounding SIGNAL is same-sentence cosine co-occurrence, which cannot distinguish
   'X means Y' from 'X appears near Y'; the MEANINGFUL hits are overwhelmingly from the biology
   segment because that segment contains EXPLICIT DEFINITIONAL SENTENCES."

Testable decomposition (all measured off disk, nothing assumed):

  M1  Base rate: of the 634 v2 GROUNDED_MEANING facts, how many have ANY evidence sentence
      containing a definitional construction AT ALL, and how many have a construction that
      actually LINKS subject->object? Per segment.
  M2  Labelled association: for pairs that carry an INDEPENDENT bucket label (the previous
      director's v1 audit in notes/foundation_grounding_sample_2026-08-12.md -- labelled by
      someone other than this agent, so not circular), is the definitional-link rate higher for
      MEANINGFUL than for NOISE?
  M3  Segment association: is the corpus-level definitional-sentence DENSITY higher in the bio
      segment than in the general-prose segments? (This is the mechanism the hypothesis needs:
      bio is meaningful BECAUSE it is definitional, not merely because it is bio.)

Outputs JSON to data/analysis_definitional_pattern_association_v1/metrics.json. Read-only over
all evidence stores.
"""

from __future__ import annotations

import json
import os
import random
import sys
from collections import Counter, defaultdict
from typing import Dict, List

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.definitional_extraction import (  # noqa: E402
    extract_definitions, links, sentence_has_definitional_pattern,
)

V2_PROV = os.path.join(REPO_ROOT, "data", "foundation", "reading_grounding_v2_qualityfix",
                       "grounding_provenance.jsonl")
OUT_DIR = os.path.join(REPO_ROOT, "data", "analysis_definitional_pattern_association_v1")

# --- The previous director's INDEPENDENT v1 bucket labels ------------------------------------
# Transcribed verbatim from notes/foundation_grounding_sample_2026-08-12.md, Sample 2 (20 random
# CROSS-grounded pairs, seed=43) + the 7 cross-grounded rows of Sample 1 (seed=42). Only
# cross-grounded rows are usable (self-grounded rows are tautologies, gone from v2 by design).
V1_LABELS: Dict[tuple, str] = {
    # --- Sample 2 (cross-only, n=20) ---
    ("austria", "girlfriend"): "NOISE",
    ("choic", "lanka"): "NOISE",
    ("recruit", "promote"): "RELATED",
    ("tree", "phylogenetic"): "MEANINGFUL",
    ("litter", "cop"): "NOISE",
    ("governor", "jail"): "RELATED",
    ("experimentation", "als"): "RELATED",
    ("organelle", "cytoplasm"): "MEANINGFUL",
    ("huffington", "say"): "NOISE",
    ("pinch", "invaginat"): "MEANINGFUL",
    ("shed", "quirky"): "NOISE",
    ("primer", "polymerase"): "MEANINGFUL",
    ("scholar", "observe"): "RELATED",
    ("alternation", "haploid"): "MEANINGFUL",
    ("variant", "gene"): "MEANINGFUL",
    ("compel", "like"): "NOISE",
    ("physicist", "massachusett"): "NOISE",
    ("nam", "metadata"): "NOISE",
    ("represent", "meaning"): "MEANINGFUL",
    ("monthly", "follower"): "RELATED",
    # --- Sample 1 cross-grounded rows (n=12) ---
    ("mindfulness", "fourth"): "NOISE",
    ("vice", "digitiz"): "NOISE",
    ("inductive", "deductive"): "MEANINGFUL",
    ("retailer", "alliance"): "RELATED",
    ("nuclei", "decay"): "MEANINGFUL",
    ("corridor", "survey"): "NOISE",
    ("chick", "nest"): "RELATED",
    ("mechanism", "identical"): "NOISE",
    ("november", "oberg"): "NOISE",
    ("sulphur", "soot"): "RELATED",
    ("translat", "also"): "NOISE",
    ("mainland", "carnivore"): "NOISE",
}


def load_prov() -> List[dict]:
    with open(V2_PROV, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main() -> None:
    prov = load_prov()
    out: dict = {"n_provenance_rows": len(prov)}

    # ---------------- M1: base rates over the 634 v2 facts ----------------------------------
    per_seg_any: Dict[str, List[int]] = defaultdict(list)
    per_seg_link: Dict[str, List[int]] = defaultdict(list)
    linked_rows: List[dict] = []
    n_any = n_link = n_link_head = 0
    for r in prov:
        sents = [e.get("sentence", "") for e in r.get("evidence", [])]
        any_def = any(sentence_has_definitional_pattern(s) for s in sents)
        link_kind = None
        for s in sents:
            lk = links(s, r["subject"], r["object"])
            if lk is not None:
                link_kind = lk
                if lk.endswith(":HEAD"):
                    break
        n_any += int(any_def)
        n_link += int(link_kind is not None)
        n_link_head += int(bool(link_kind and link_kind.endswith(":HEAD")))
        per_seg_any[r["segment"]].append(int(any_def))
        per_seg_link[r["segment"]].append(int(link_kind is not None))
        if link_kind:
            linked_rows.append({"subject": r["subject"], "object": r["object"],
                                "segment": r["segment"], "link": link_kind})

    out["M1_base_rates"] = {
        "n_facts": len(prov),
        "n_with_any_definitional_sentence": n_any,
        "rate_any_definitional_sentence": round(n_any / len(prov), 4),
        "n_pair_linked_by_definition": n_link,
        "rate_pair_linked_by_definition": round(n_link / len(prov), 4),
        "n_pair_linked_at_HEAD": n_link_head,
        "per_segment": {
            seg: {"n": len(v), "rate_any_def_sentence": round(sum(v) / len(v), 4),
                  "rate_pair_linked": round(sum(per_seg_link[seg]) / len(v), 4)}
            for seg, v in sorted(per_seg_any.items())
        },
        "linked_examples": linked_rows[:25],
    }

    # ---------------- M2: association with INDEPENDENT v1 bucket labels ---------------------
    # Join the v1-labelled pairs onto v2 provenance by (subject, object). Where the pair is not
    # present in v2 (v2 is a different, quality-fixed run), fall back to searching v2's evidence
    # sentence POOL for the subject so a sentence-level test is still possible.
    prov_by_pair = {(r["subject"], r["object"]): r for r in prov}
    all_sents: List[str] = []
    sents_by_lemma: Dict[str, List[str]] = defaultdict(list)
    for r in prov:
        for e in r.get("evidence", []):
            s = e.get("sentence", "")
            if s:
                all_sents.append(s)
                sents_by_lemma[r["subject"]].append(s)

    m2_rows = []
    for (subj, obj), label in V1_LABELS.items():
        r = prov_by_pair.get((subj, obj))
        matched = r is not None
        sents = ([e.get("sentence", "") for e in r.get("evidence", [])] if matched
                 else sents_by_lemma.get(subj, []))
        link_kind = None
        for s in sents:
            lk = links(s, subj, obj)
            if lk is not None:
                link_kind = lk
                if lk.endswith(":HEAD"):
                    break
        any_def = any(sentence_has_definitional_pattern(s) for s in sents)
        m2_rows.append({"subject": subj, "object": obj, "label": label,
                        "in_v2": matched, "n_sentences_available": len(sents),
                        "any_def_sentence": any_def, "pair_linked": link_kind})

    by_label = defaultdict(list)
    for row in m2_rows:
        by_label[row["label"]].append(row)
    out["M2_labelled_association"] = {
        "n_labelled_pairs": len(m2_rows),
        "n_with_sentences_available": sum(1 for r in m2_rows if r["n_sentences_available"] > 0),
        "n_present_in_v2_store": sum(1 for r in m2_rows if r["in_v2"]),
        "per_label": {
            lab: {
                "n": len(rows),
                "n_sentences_available": sum(1 for r in rows if r["n_sentences_available"] > 0),
                "n_pair_linked_by_definition": sum(1 for r in rows if r["pair_linked"]),
                "n_any_def_sentence": sum(1 for r in rows if r["any_def_sentence"]),
            } for lab, rows in sorted(by_label.items())
        },
        "rows": m2_rows,
    }

    # ---------------- M3: corpus-level definitional density per segment ---------------------
    seg_sents: Dict[str, set] = defaultdict(set)
    for r in prov:
        for e in r.get("evidence", []):
            s = e.get("sentence", "")
            if s:
                seg_sents[r["segment"]].add(s)
    m3 = {}
    rng = random.Random(4242)
    for seg, ss in sorted(seg_sents.items()):
        pool = sorted(ss)
        sample = pool if len(pool) <= 1500 else rng.sample(pool, 1500)
        hits = sum(1 for s in sample if sentence_has_definitional_pattern(s))
        m3[seg] = {"n_unique_sentences": len(pool), "n_sampled": len(sample),
                   "n_with_definition": hits, "rate": round(hits / max(1, len(sample)), 4)}
    out["M3_segment_definitional_density"] = m3

    # pattern mix over the whole evidence pool
    pat = Counter()
    uniq_all = sorted(set(all_sents))
    for s in uniq_all:
        for d in extract_definitions(s):
            pat[d.pattern] += 1
    out["M3_pattern_mix_over_all_unique_sentences"] = {
        "n_unique_sentences": len(uniq_all), "pattern_counts": dict(pat)}

    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print(json.dumps({k: v for k, v in out.items()
                      if k != "M2_labelled_association"}, indent=2)[:4000])
    print("--- M2 per_label ---")
    print(json.dumps(out["M2_labelled_association"]["per_label"], indent=2))
    print("wrote", os.path.join(OUT_DIR, "metrics.json"))


if __name__ == "__main__":
    main()
