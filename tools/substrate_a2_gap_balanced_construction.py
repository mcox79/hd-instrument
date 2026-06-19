"""Bucket-2 TRACK-1: A2 gap-balanced held-out CONSTRUCTION (per research drill 329eabb9 methodology).

Builds a research-grade GAP-balanced eval set for the refuse-gate: IN-COV questions (substrate DOES cover; gold atoms
present) + GAP questions (genuinely OUTSIDE coverage; verified-absent), with NEAR-gap (on-domain, content-absent) + FAR-gap
(different field) split. Skunkworks ruled: Exp-Dev AUTHORS, she VALIDITY-VETs independently (authorship/validation separation).

Methodology gates implemented:
 - n >= 27 per arm (Hanley-McNeil 80%-power floor; Skunkworks DATA-BLOCKED ruling).
 - VERIFY-ABSENCE (cross-corpus, the verify-the-referent step): each GAP candidate's distinctive key-terms are probed
   against the FULL Store (all 41k atoms: MATH ops + CONCEPT caps + WordNet LEXICON + GO SCIENCE_CONCEPT + schools).
   A gap with > ABSENCE_MAX matching atoms is LEAKY (covered) -> DROPPED. (The WordNet+GO additions make this load-bearing:
   common-noun gap-topics now have lexical atoms -- e.g. baum-welch/bellman-ford/coffee/wine are IN-corpus, NOT clean gaps.)
 - PRESENCE-check: each IN-COV gold atom must EXIST (else drop).
 - LEXICAL-SHORTCUT audit: TF-IDF LOO-CV AUROC on the question text (gap vs in-cov). Must be < TFIDF_MAX (else leaky-by-form).
 - near/far gap split (for the eventual P4 near-vs-far robustness test).

DEFAULT = construct + audit + emit data/exp_a2_gap_balanced/a2_gap_balanced_v1.jsonl + a report. NO Store mutation
(this is EVAL-SET construction, not substrate ingest). NOT the firewalled gold (q54-q65); a fresh independent build.
ASCII-only. No LLM (deterministic authoring + lexical probes). Laptop-safe.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

N_PER_ARM_FLOOR = 27
ABSENCE_MAX = 1          # a gap is "absent" if <= this many atoms lexically match its distinctive key-term
TFIDF_MAX = 0.65         # lexical-shortcut leakage gate (LOO-CV AUROC must be below this)
OUT = Path('data/exp_a2_gap_balanced')

# ---- IN-COV: topics the substrate DOES cover (gold = a real atom local-id; presence-checked) ----
IN_COV = [
    ("Viterbi decoding", "T3/viterbi_decoding"),
    ("forward-algorithm marginals", "T3/forward_algorithm"),
    ("backward-algorithm marginals", "T3/backward_algorithm"),
    ("Hungarian assignment", "T3/hungarian_assignment"),
    ("Chu-Liu-Edmonds maximum spanning arborescence", "T3/chu_liu_edmonds"),
    ("Dijkstra shortest paths", "T3/dijkstra"),
    ("A-star search", "T3/astar"),
    ("beam search decoding", "T3/beam_search"),
    ("Prim's minimum spanning tree", "T3/prims_mst"),
    ("Jonker-Volgenant assignment", "T3/jonker_volgenant"),
    ("PCA whitening", "T3/pca_whitening"),
    ("ZCA whitening", "T3/zca_whitening"),
    ("Bayesian inference", "T3/bayesian_inference"),
    ("circular convolution", "T2/circular_convolution"),
    ("FHRR bind", "T2/fhrr_bind"),
    ("FHRR unbind", "T2/fhrr_unbind"),
    ("cleanup memory", "T2/cleanup"),
    ("cosine cleanup", "T2/cosine_cleanup"),
    ("Hamming distance", "T2/hamming_distance"),
    ("role-filler binding", "T2/role_filler_binding"),
    ("context binding", "T2/context_binding"),
    ("dynamic programming", "T3/dynamic_programming"),
    ("the discriminative perceptron", "T3/discriminative_perceptron"),
    ("naive-Bayes counting", "T3/count_nb"),
    ("vector-symbolic architectures", "SCHOOL/vsa_family"),
    ("Hopfield networks", "SCHOOL/hopfield_family"),
    ("sparse distributed memory", "SCHOOL/sparse_distributed_memory_family"),
    ("HMM sequence labeling", "SCHOOL/hmm_sequence_labeling_family"),
    ("the EM algorithm", "T3/em_algorithm"),
    ("Needleman-Wunsch alignment", "T3/needleman_wunsch"),
    ("superposition bundling", "T2/superposition"),
    ("free probability", "SCHOOL/free_probability_family"),
    ("structured prediction", "SCHOOL/structured_prediction_family"),
    ("categorical NLP", "SCHOOL/categorical_NLP_family"),
]

# ---- GAP POOL: on-domain (NEAR) or different-field (FAR) topics expected ABSENT; verify-absence culls leaky ones ----
# each: (topic_phrase, near|far, distinctive_key_terms_for_absence_probe)
GAP_POOL = [
    # NEAR-gap: on-domain (graph algos / VSA / HMM / linalg) but absent specifics
    ("Tarjan SCC", "near", ["tarjan"]),
    ("Edmonds-Karp", "near", ["edmonds-karp"]),
    ("Hopcroft-Karp", "near", ["hopcroft"]),
    ("Christofides approximation", "near", ["christofides"]),
    ("Boruvka MST", "near", ["boruvka"]),
    ("Johnson reweighting", "near", ["johnson all-pairs", "johnson reweighting"]),
    ("Fibonacci heap decrease-key", "near", ["fibonacci heap"]),
    ("splay tree amortized rotation", "near", ["splay tree"]),
    ("vector-derived transformation binding (VTB)", "near", ["vector-derived transformation", "vtb binding"]),
    ("the MAP multiply-add-permute VSA architecture", "near", ["multiply-add-permute"]),
    ("sparse block-code binding", "near", ["sparse block-code", "block-code binding"]),
    ("IOHMMs", "near", ["input-output hmm", "iohmm"]),
    ("factorial HMMs", "near", ["factorial hmm"]),
    ("the hierarchical Dirichlet process HMM", "near", ["hierarchical dirichlet"]),
    ("randomized SVD via power iteration", "near", ["randomized svd"]),
    ("CUR matrix decomposition", "near", ["cur decomposition", "cur matrix"]),
    ("locality-sensitive hashing with MinHash", "near", ["minhash", "locality-sensitive hashing"]),
    ("suffix automaton construction", "near", ["suffix automaton"]),
    ("Kruskal's minimum spanning tree", "near", ["kruskal"]),
    ("Ford-Fulkerson", "near", ["ford-fulkerson"]),
    ("Knuth-Morris-Pratt", "near", ["knuth-morris-pratt"]),
    ("Aho-Corasick", "near", ["aho-corasick"]),
    ("the union-find disjoint-set structure", "near", ["union-find", "disjoint-set"]),
    ("Welzl's smallest enclosing circle", "near", ["welzl"]),
    # FAR-gap: different fields entirely
    ("Mesopotamian cuneiform accounting tablets", "far", ["cuneiform"]),
    ("Etruscan funerary art", "far", ["etruscan"]),
    ("glacial moraine deposition", "far", ["moraine"]),
    ("terroir soil mineralogy in viticulture", "far", ["terroir"]),
    ("baroque counterpoint voice-leading", "far", ["counterpoint", "voice-leading"]),
    ("subduction-zone seismicity", "far", ["subduction"]),
    ("Noh theater mask carving", "far", ["noh theater", "noh mask"]),
    ("medieval guild apprenticeship contracts", "far", ["guild apprenticeship"]),
    ("the monsoon wind reversal mechanism", "far", ["monsoon"]),
    ("Gregorian chant neume notation", "far", ["gregorian chant", "neume"]),
    ("dendrochronology crossdating", "far", ["dendrochronology"]),
    ("Phoenician alphabet diffusion", "far", ["phoenician"]),
    ("urushi lacquerware technique", "far", ["urushi", "lacquerware"]),
    ("kabuki stage revolving machinery", "far", ["kabuki"]),
    ("Andean quipu knot recording", "far", ["quipu"]),
    ("Polynesian stick-chart navigation", "far", ["stick-chart", "stick chart navigation"]),
    ("Byzantine cloisonne enamel", "far", ["cloisonne"]),
    ("transhumance pastoral migration", "far", ["transhumance"]),
]


def _question(topic):
    return f"What do I have about {topic}?"


def main() -> int:
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(Path('data/substrate_index'))
    atoms = list(ps.all_atoms())
    # full-corpus lexical blob (id + name + description), lowercased, for cross-corpus absence probing
    blob = " ".join((str(a.id) + " " + (a.name or "") + " " + (a.description or "")) for a in atoms).lower()
    atom_ids = {a.id for a in atoms}

    # ---- IN-COV: presence-check the gold atom ----
    in_cov_items, in_cov_dropped = [], []
    for i, (topic, gold) in enumerate(IN_COV):
        present = gold in atom_ids
        if present:
            in_cov_items.append({"id": f"A2-IC-{i:03d}", "type": "in_cov", "question": _question(topic),
                                 "args": {"topic": topic}, "answerable": True, "gold": [gold], "gap_kind": None})
        else:
            in_cov_dropped.append((topic, gold))

    # ---- GAP: verify-absence (cross-corpus lexical probe) ----
    gap_items, gap_dropped = [], []
    for i, (topic, kind, keys) in enumerate(GAP_POOL):
        # count atoms matching ANY distinctive key-term (a term present in the blob -> some atom mentions it)
        matches = sum(1 for k in keys if k.lower() in blob)
        if matches <= 0:                       # 0 key-terms appear anywhere -> genuinely absent
            gap_items.append({"id": f"A2-GAP-{i:03d}", "type": "gap", "question": _question(topic),
                              "args": {"topic": topic}, "answerable": False, "gold": [], "gap_kind": kind,
                              "absence_keys": keys})
        else:
            gap_dropped.append((topic, kind, keys, matches))

    near = [g for g in gap_items if g["gap_kind"] == "near"]
    far = [g for g in gap_items if g["gap_kind"] == "far"]

    # ---- LEXICAL-SHORTCUT audit: TF-IDF LOO-CV AUROC on question text (gap vs in_cov) ----
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import LeaveOneOut
    from sklearn.metrics import roc_auc_score
    import numpy as np
    texts = [it["question"] for it in in_cov_items] + [it["question"] for it in gap_items]
    labels = np.array([0] * len(in_cov_items) + [1] * len(gap_items))   # 1 = gap
    tfidf_auroc = None
    if len(set(labels)) == 2 and len(texts) >= 4:
        X = TfidfVectorizer().fit_transform(texts)
        loo = LeaveOneOut(); preds = np.zeros(len(labels))
        for tr, te in loo.split(texts):
            if len(set(labels[tr])) < 2:
                preds[te[0]] = 0.5; continue
            clf = LogisticRegression(max_iter=1000).fit(X[tr], labels[tr])
            preds[te[0]] = clf.predict_proba(X[te])[0, 1]
        tfidf_auroc = float(roc_auc_score(labels, preds))

    n_ic, n_gap = len(in_cov_items), len(gap_items)
    power_ok = n_ic >= N_PER_ARM_FLOOR and n_gap >= N_PER_ARM_FLOOR
    tfidf_ok = (tfidf_auroc is not None) and (tfidf_auroc < TFIDF_MAX)

    OUT.mkdir(parents=True, exist_ok=True)
    all_items = in_cov_items + gap_items
    with open(OUT / "a2_gap_balanced_v1.jsonl", "w", encoding="utf-8") as f:
        for it in all_items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

    report = {
        "n_in_cov": n_ic, "n_gap": n_gap, "n_near": len(near), "n_far": len(far),
        "power_floor_per_arm": N_PER_ARM_FLOOR, "power_ok": power_ok,
        "tfidf_loo_auroc": round(tfidf_auroc, 4) if tfidf_auroc is not None else None,
        "tfidf_shortcut_gate_max": TFIDF_MAX, "tfidf_ok_no_lexical_shortcut": tfidf_ok,
        "in_cov_dropped_missing_gold": in_cov_dropped,
        "gap_dropped_leaky": [(t, k, m) for (t, k, _ks, m) in gap_dropped],
        "absence_max": ABSENCE_MAX,
        "verify_absence": "cross-corpus lexical key-term probe vs full Store blob (41k atoms incl. WordNet+GO)",
        "methodology": "research drill 329eabb9; Skunkworks validity-VETs independently (authorship/validation separation)",
        "NOTE": "EVAL-SET construction, NOT substrate ingest; NOT the firewalled gold q54-q65; fresh independent build",
        "REMAINING_per_methodology": "Skunkworks independent validity-VET (gaps genuinely absent + verifier-agreement >= 0.85) "
                                     "+ optional substrate-untuned-AUROC decisive test (target [0.45,0.60]) -- pre-LoRA",
    }
    with open(OUT / "a2_construction_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("=" * 72)
    print("A2 gap-balanced construction")
    print("=" * 72)
    print(f"IN-COV: {n_ic} (dropped-missing-gold: {len(in_cov_dropped)})")
    print(f"GAP: {n_gap} (near {len(near)} + far {len(far)}); dropped-leaky (verify-absence): {len(gap_dropped)}")
    if gap_dropped:
        print("  leaky gaps (key-term IN-corpus -> NOT a clean gap):")
        for (t, k, _ks, m) in gap_dropped:
            print(f"    [{k}] {t}  (matched {m} key-term(s))")
    print(f"power floor n>={N_PER_ARM_FLOOR}/arm: {'PASS' if power_ok else 'FAIL'} (in_cov {n_ic}, gap {n_gap})")
    print(f"TF-IDF LOO-CV AUROC: {tfidf_auroc} (gate < {TFIDF_MAX}): {'PASS (no lexical shortcut)' if tfidf_ok else 'FAIL (lexical leakage) -- rebuild'}")
    print(f"emitted: {OUT / 'a2_gap_balanced_v1.jsonl'} ({len(all_items)} items) + report")
    print("=" * 72)
    print("NEXT: Skunkworks INDEPENDENT validity-VET (gaps genuinely absent + no in-cov-phrasing leakage); authorship/validation separation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
