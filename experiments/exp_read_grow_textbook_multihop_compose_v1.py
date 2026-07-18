# CELL: read_grow_textbook_multihop_compose_v1
# QUESTION: Does a foundation GROWN from reading a full textbook (dense direct is-a graph)
#   support MULTI-HOP TRANSITIVE COMPOSITION -- answering held-out INDIRECT "is A a type-of C?"
#   queries (book states A->B and B->C in different sections, NEVER A->C directly) that
#   non-compositional baselines (direct-lookup, single-section, frequency, random) structurally
#   CANNOT do -- AND does that win SURVIVE extraction noise (transitive closure amplifies edge
#   errors: one bad edge -> many false paths)?  Glass-box, NO runtime LLM.
#
# GLASS-BOX: NLTK PerceptronTagger POS + WordNetLemmatizer + WordNet (as INDEPENDENT gold oracle)
#   + regex/symbolic Hearst is-a extraction. NO spaCy-default / Stanza / torch / transformers.
#   Reuses v1 (exp_read_grow_textbook_isa_growth_v1) extractor + graph-build (imported as real code path).
#
# DESIGN (design-gate compliant):
#   GRAPH   = glossary genus-differentia is-a edges (child term -> genus parent), dense direct graph.
#             (prose Hearst edges built too, reported for density + a noise-variant arm.)
#   ORACLE  = WordNet hypernym ancestry (paraphrase-robust: head-noun + top-3 noun synsets +
#             hypernym closure) -- an INDEPENDENT gold labeler, NOT the book's own closure
#             (the book's raw closure is majority-false, so it cannot be its own gold).
#   HELD-OUT / DIFFICULTY-ON: query pairs (A,C) have NO direct book is-a edge; the answer is only
#             reachable by COMPOSING >=2 book edges across sections. Gold = WordNet TRUE/FALSE.
#   POS  = WN-true indirect pairs (WN-dist in [2, DMAX]) among book nodes, no direct book edge,
#          book-composable (book path dist>=2 exists).  [tests: does the grown graph assemble
#          true relations the baselines cannot? compositional YES vs direct-lookup structurally NO]
#   NEG-HARD = WN-FALSE but book-composable (dist>=2, no direct edge) = the closure's OWN false
#          paths.  [tests PRECISION / false-path amplification -- the key noise failure mode]
#   NEG-EASY = WN-FALSE, NOT book-reachable random pairs.  [sanity floor]
#   ARMS (one variable = composition/closure ON vs OFF):
#     COMPOSITIONAL      : YES iff book path (dist>=1) reaches C  [closure ON]
#     COMPOSE_NOISE_CTRL : YES iff path in noise-controlled graph (drop generic-hub parents +
#                          depth cap)  [does controlling extraction noise rescue precision?]
#     DIRECT_LOOKUP      : YES iff DIRECT book edge A->C  [closure OFF; fails multi-hop by construction]
#     SINGLE_SECTION     : YES iff path within the single richest-edge section subgraph only
#     FREQUENCY          : YES iff C is a top-K global hub parent  [real non-compositional baseline]
#     RANDOM             : Bernoulli(base_rate), fixed-seed floor
#   METRIC = balanced accuracy over POS + NEG per arm (recall_pos + specificity_neg)/2; plus
#            per-arm precision / recall / F1; plus compose_precision_on_proposals (false-path audit,
#            raw + noise-ctrl) and honest coverage_recall_full over ALL WN-true indirect pairs.
#   CAN-FAIL: HARD_FAIL_NOISE if closure precision < floor (majority-false) even with noise control
#            -> "grown graph too sparse/noisy for reliable multi-hop" (first-class informative null,
#            reported honestly, NOT tortured). HARD_PASS iff compositional (or noise-ctrl) is a
#            RELIABLE multi-hop answerer (balanced-acc + precision above floor) AND beats every
#            non-compositional baseline by a real margin.
#
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scale/floor):
# - start_marker + crash_diagnostic (Exception -> CELL_CRASHED metrics.json + traceback)
# - except SystemExit: raise BEFORE except Exception (no BaseException); no bare except
# - final_metrics_atomicity = tmp_replace (os.replace)
# - deterministic seeding only (FIXED int random.Random(seed); NO built-in hash() / list(set()))
# - arms_differ verified (YES-rate per arm distinct)
# - all bands tagged HYPOTHESIZED@ (pre-reg) then confirmed MEASURED@ at run
#
# Compute architecture: (b) sequential-CPU. Justification: glass-box regex / POS-tag / WordNet /
#   symbolic graph closure. No matmul, no substrate vectors, no GPU speedup available. Diagnostic
#   reasoning-value cell (compute-proportionality: cheapest decisive method). Wall < few min.
# calibration_check: "default_ok_for_this_regime" (no primitive-default inheritance; symbolic thresholds
#   set from pre-reg + measured at run).
# crlb_n/a: "no continuous noise floor; discriminator is symbolic graph-path existence vs WN ancestry."

import os
import sys
import json
import time
import random
import argparse
import traceback
import importlib.util
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone

from nltk.corpus import wordnet as wn

ANCHOR_NAME = "read_grow_textbook_multihop_compose_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(
    REPO, "data", "corpora", "textbook_concepts_biology", "cleaned",
    "concepts_biology.clean.txt",
)
V1_PATH = os.path.join(REPO, "experiments", "exp_read_grow_textbook_isa_growth_v1.py")

# Reuse v1 extractor + graph-build as the REAL code path (per task: REUSE v1's extractor).
_spec = importlib.util.spec_from_file_location("_isa_v1", V1_PATH)
V1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V1)

DMAX_WN = 6          # WN-distance cap for positive indirect pairs (avoid deep-ontology inflation)
TOP_HUB_K = 10       # frequency baseline: predict YES if C in top-K global hub parents
NOISE_HUB_MAX = 8    # noise-ctrl: drop edges whose PARENT has book in-degree > this (generic hubs)
NOISE_DEPTH_MAX = 3  # noise-ctrl: cap composition depth
RNG_SEED = 20260717  # FIXED deterministic seed (NEVER built-in hash())

# Pre-registered bands (HYPOTHESIZED@ this file; confirmed MEASURED@ at run)
BANDS = {
    "hp_precision_floor": 0.70,      # HARD_PASS: closure/noise-ctrl proposals >=70% WN-true (reliable)
    "hp_balacc_floor": 0.70,         # HARD_PASS: balanced accuracy >= 0.70
    "hp_beat_margin": 0.10,          # HARD_PASS: beats every non-compositional baseline by >= 0.10 balacc
    "fail_precision_max": 0.55,      # HARD_FAIL_NOISE: majority-false proposals (precision < 0.55)
    "min_pos": 20,                   # vacuous-n guard: need >= 20 composable true positives
    "min_neg_hard": 10,              # need >= 10 false-path hard negatives to audit precision
}

# ------------------------- error-checking scaffolds -------------------------

def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics_atomic(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "{}: {}".format(type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: {}".format(type(exc).__name__),
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    _write_metrics_atomic(output_dir, diag)


# ------------------------- WordNet oracle (paraphrase-robust gold) -------------------------

_ANC_CACHE = {}
_LEM_CACHE = {}


def _syns_for(term):
    """Top-3 noun synsets for a term; fall back to head noun (last word) for multiword terms."""
    key = term.replace(" ", "_")
    syns = wn.synsets(key, pos=wn.NOUN)[:3]
    if not syns and " " in term:
        hw = term.split()[-1]
        syns = wn.synsets(hw, pos=wn.NOUN)[:3]
    return syns


def wn_match_lemmas(term):
    """Own-synset lemmas of a term (paraphrase-robust node identity for the oracle)."""
    if term in _LEM_CACHE:
        return _LEM_CACHE[term]
    s = {term}
    for sy in _syns_for(term):
        for l in sy.lemmas():
            s.add(l.name().lower().replace("_", " "))
    _LEM_CACHE[term] = s
    return s


def wn_ancestors(term):
    """lemma -> min WN hypernym distance, over hypernym+instance_hypernym closure of top-3 synsets."""
    if term in _ANC_CACHE:
        return _ANC_CACHE[term]
    anc = {}
    for s in _syns_for(term):
        frontier = [(s, 0)]
        seen = {s}
        while frontier:
            nxt = []
            for node, d in frontier:
                for h in node.hypernyms() + node.instance_hypernyms():
                    if h not in seen:
                        seen.add(h)
                        for l in h.lemmas():
                            ln = l.name().lower().replace("_", " ")
                            if ln not in anc or d + 1 < anc[ln]:
                                anc[ln] = d + 1
                        nxt.append((h, d + 1))
            frontier = nxt
    _ANC_CACHE[term] = anc
    return anc


def wn_checkable(a, c):
    """Both endpoints have WN coverage -> the pair is judgeable by the oracle."""
    return bool(wn_ancestors(a)) and bool(wn_match_lemmas(c))


def wn_true_dist(a, c):
    """Return min WN hypernym distance d>=1 s.t. C is an ancestor of A (paraphrase-robust), else None."""
    anc = wn_ancestors(a)
    best = None
    for cand in wn_match_lemmas(c):
        if cand in anc:
            best = anc[cand] if best is None else min(best, anc[cand])
    return best


# ------------------------- graph build (reuse v1 extractor) -------------------------

def build_graphs(sections):
    """Return (gloss_adj, prose_adj, full_adj, indeg, parent_freq, richest_section_adj).
       adj: child -> set(parents). indeg: parent -> book in-degree (generic-hub proxy)."""
    gloss = defaultdict(set)
    gloss_edge_count = 0
    for sec in sections:
        for term_surface, defn in sec["glossary"]:
            genus = V1.genus_of_definition(defn)
            if not genus:
                continue
            nt = V1._norm_term(V1._tokenize(term_surface))
            if not nt or not genus or nt == genus:
                continue
            if genus not in gloss[nt]:
                gloss_edge_count += 1
            gloss[nt].add(genus)

    prose = defaultdict(set)
    prose_edge_count = 0
    section_edges = []  # per-section list of (child,parent) from prose+glossary for single-section arm
    for sec in sections:
        se = set()
        for term, genus in V1.extract_section(sec["prose"]):
            if term == genus:
                continue
            if genus not in prose[term]:
                prose_edge_count += 1
            prose[term].add(genus)
            se.add((term, genus))
        # add this section's glossary edges to its local subgraph too
        for term_surface, defn in sec["glossary"]:
            genus = V1.genus_of_definition(defn)
            if not genus:
                continue
            nt = V1._norm_term(V1._tokenize(term_surface))
            if nt and genus and nt != genus:
                se.add((nt, genus))
        section_edges.append(se)

    full = defaultdict(set)
    for c, ps in gloss.items():
        full[c] |= ps
    for c, ps in prose.items():
        full[c] |= ps

    indeg = Counter()
    parent_freq = Counter()
    for c, ps in gloss.items():
        for p in ps:
            indeg[p] += 1
            parent_freq[p] += 1

    # richest section subgraph (most edges) for the SINGLE_SECTION arm
    richest = max(section_edges, key=lambda s: len(s)) if section_edges else set()
    richest_adj = defaultdict(set)
    for c, p in richest:
        richest_adj[c].add(p)

    return {
        "gloss": gloss, "prose": prose, "full": full, "indeg": indeg,
        "parent_freq": parent_freq, "richest_adj": richest_adj,
        "gloss_edges": gloss_edge_count, "prose_edges": prose_edge_count,
    }


def closure(adj, maxd=15):
    """child -> {reachable_target: shortest_dist}. Cycle-safe (BFS, first-visit dist)."""
    reach = {}
    for s in list(adj.keys()):
        dist = {s: 0}
        q = deque([s])
        while q:
            u = q.popleft()
            if dist[u] >= maxd:
                continue
            for v in adj.get(u, ()):
                if v not in dist:
                    dist[v] = dist[u] + 1
                    q.append(v)
        del dist[s]
        reach[s] = dist
    return reach


def noise_ctrl_adj(gloss, indeg, hub_max):
    """Drop edges whose PARENT is a generic hub (book in-degree > hub_max)."""
    adj = defaultdict(set)
    for c, ps in gloss.items():
        for p in ps:
            if indeg[p] > hub_max:
                continue
            adj[c].add(p)
    return adj


# ------------------------- query-set construction + arms -------------------------

def build_query_set(graphs, rng):
    """Construct WN-labeled query set + per-arm predictions. Returns dict of everything measured."""
    gloss = graphs["gloss"]
    indeg = graphs["indeg"]
    parent_freq = graphs["parent_freq"]

    nodes = sorted(set(gloss.keys()) | {p for ps in gloss.values() for p in ps})
    direct = {(c, p) for c, ps in gloss.items() for p in ps}

    reach_book = closure(gloss)                 # compositional closure (book path dists)
    nc_adj = noise_ctrl_adj(gloss, indeg, NOISE_HUB_MAX)
    reach_nc = closure(nc_adj, maxd=NOISE_DEPTH_MAX)
    reach_single = closure(graphs["richest_adj"])

    # inverted index: match-lemma -> book nodes (for fast WN-true positive discovery)
    lemma_to_nodes = defaultdict(set)
    for c in nodes:
        for lem in wn_match_lemmas(c):
            lemma_to_nodes[lem].add(c)

    top_hubs = set(p for p, _ in parent_freq.most_common(TOP_HUB_K))

    # ---- enumerate WN-true indirect pairs among book nodes (honest coverage universe) ----
    wn_true_all = []           # (a,c,wn_dist)  WN-true, dist in [2,DMAX], no direct book edge
    for a in nodes:
        anc = wn_ancestors(a)
        if not anc:
            continue
        seen_c = set()
        for lem, d in anc.items():
            if d < 2 or d > DMAX_WN:
                continue
            for c in lemma_to_nodes.get(lem, ()):
                if c == a or c in seen_c or (a, c) in direct:
                    continue
                seen_c.add(c)
                # use min WN dist for this (a,c)
                wd = wn_true_dist(a, c)
                if wd is not None and 2 <= wd <= DMAX_WN:
                    wn_true_all.append((a, c, wd))

    # book-composable subset of WN-true (POSITIVES for the well-posed discrimination test)
    pos = []
    for a, c, wd in wn_true_all:
        bd = reach_book.get(a, {}).get(c)
        if bd is not None and bd >= 2:
            pos.append((a, c, wd, bd))

    # ---- NEG-HARD: book-composable (dist>=2, no direct edge) but WN-FALSE (the false paths) ----
    neg_hard = []
    for a in nodes:
        for c, bd in reach_book.get(a, {}).items():
            if bd >= 2 and (a, c) not in direct and wn_checkable(a, c):
                if wn_true_dist(a, c) is None:
                    neg_hard.append((a, c, bd))

    # ---- NEG-EASY: random book-node pairs, WN-false, NOT book-reachable ----
    neg_easy = []
    target_easy = max(len(pos), len(neg_hard))
    tries = 0
    max_tries = target_easy * 200 + 5000
    while len(neg_easy) < target_easy and tries < max_tries:
        tries += 1
        a = rng.choice(nodes)
        c = rng.choice(nodes)
        if a == c or (a, c) in direct:
            continue
        if c in reach_book.get(a, {}):
            continue
        if not wn_checkable(a, c):
            continue
        if wn_true_dist(a, c) is not None:
            continue
        neg_easy.append((a, c, None))

    # ---------- per-arm YES/NO predictions ----------
    def arm_predict(a, c, arm):
        if arm == "COMPOSITIONAL":
            return c in reach_book.get(a, {})
        if arm == "COMPOSE_NOISE_CTRL":
            return c in reach_nc.get(a, {})
        if arm == "DIRECT_LOOKUP":
            return (a, c) in direct
        if arm == "SINGLE_SECTION":
            return c in reach_single.get(a, {})
        if arm == "FREQUENCY":
            return c in top_hubs
        if arm == "RANDOM":
            return None  # handled separately (seeded per-query)
        raise ValueError("unknown arm " + arm)

    arms = ["COMPOSITIONAL", "COMPOSE_NOISE_CTRL", "DIRECT_LOOKUP",
            "SINGLE_SECTION", "FREQUENCY", "RANDOM"]

    pos_q = [(a, c) for (a, c, _, _) in pos]
    neg_q = [(a, c) for (a, c, _) in neg_hard] + [(a, c) for (a, c, _) in neg_easy]
    neg_is_hard = [True] * len(neg_hard) + [False] * len(neg_easy)

    base_rate = len(pos_q) / max(1, (len(pos_q) + len(neg_q)))
    rand_rng = random.Random(RNG_SEED + 7)

    arm_metrics = {}
    arm_yes_signature = {}
    for arm in arms:
        tp = fn = 0
        for (a, c) in pos_q:
            if arm == "RANDOM":
                yes = rand_rng.random() < base_rate
            else:
                yes = arm_predict(a, c, arm)
            tp += 1 if yes else 0
            fn += 0 if yes else 1
        tn_hard = fp_hard = tn_easy = fp_easy = 0
        yes_flags = []
        for (a, c), is_hard in zip(neg_q, neg_is_hard):
            if arm == "RANDOM":
                yes = rand_rng.random() < base_rate
            else:
                yes = arm_predict(a, c, arm)
            yes_flags.append(1 if yes else 0)
            if is_hard:
                fp_hard += 1 if yes else 0
                tn_hard += 0 if yes else 1
            else:
                fp_easy += 1 if yes else 0
                tn_easy += 0 if yes else 1
        n_pos = len(pos_q)
        n_neg = len(neg_q)
        fp = fp_hard + fp_easy
        tn = tn_hard + tn_easy
        recall = tp / n_pos if n_pos else 0.0
        specificity = tn / n_neg if n_neg else 0.0
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
        balacc = 0.5 * (recall + specificity)
        spec_hard = tn_hard / len(neg_hard) if neg_hard else 0.0
        arm_metrics[arm] = {
            "recall_pos": round(recall, 5),
            "specificity_neg": round(specificity, 5),
            "specificity_hard": round(spec_hard, 5),
            "precision": round(precision, 5),
            "f1": round(f1, 5),
            "balanced_acc": round(balacc, 5),
            "tp": tp, "fn": fn, "fp": fp, "tn": tn,
            "fp_hard": fp_hard, "fp_easy": fp_easy,
            "yes_rate": round((tp + fp) / max(1, (n_pos + n_neg)), 5),
        }
        # arms-differ signature: YES pattern over neg_q (deterministic, arm-distinguishing)
        arm_yes_signature[arm] = tuple(yes_flags)

    # ---------- compose precision-on-proposals (false-path audit) ----------
    def proposal_precision(reach, maxd_note):
        chk = tr = 0
        for a in reach:
            for c, bd in reach[a].items():
                if bd >= 2 and (a, c) not in direct and wn_checkable(a, c):
                    chk += 1
                    if wn_true_dist(a, c) is not None:
                        tr += 1
        return chk, tr, (tr / chk if chk else 0.0)

    chk_raw, tr_raw, prec_raw = proposal_precision(reach_book, "raw")
    chk_nc, tr_nc, prec_nc = proposal_precision(reach_nc, "noise_ctrl")

    # honest coverage recall (book-composable WN-true / ALL WN-true indirect in [2,DMAX])
    coverage_recall_full = len(pos) / max(1, len(wn_true_all))

    hop_hist = Counter(bd for (_, _, _, bd) in pos)

    return {
        "n_nodes": len(nodes),
        "n_direct_edges": len(direct),
        "n_wn_true_all": len(wn_true_all),
        "n_pos": len(pos),
        "n_neg_hard": len(neg_hard),
        "n_neg_easy": len(neg_easy),
        "base_rate": round(base_rate, 5),
        "coverage_recall_full": round(coverage_recall_full, 5),
        "hop_depth_hist_pos": dict(sorted(hop_hist.items())),
        "compose_precision_raw": round(prec_raw, 5),
        "compose_precision_raw_checkable": chk_raw,
        "compose_precision_raw_true": tr_raw,
        "compose_precision_noise_ctrl": round(prec_nc, 5),
        "compose_precision_nc_checkable": chk_nc,
        "compose_precision_nc_true": tr_nc,
        "false_path_rate_raw": round(1.0 - prec_raw, 5),
        "arm_metrics": arm_metrics,
        "arm_yes_signature": arm_yes_signature,
        "top_hubs": sorted(top_hubs),
    }


# ------------------------- verdict -------------------------

def compute_verdict(res, bands):
    am = res["arm_metrics"]
    comp = am["COMPOSITIONAL"]
    nc = am["COMPOSE_NOISE_CTRL"]
    direct = am["DIRECT_LOOKUP"]
    single = am["SINGLE_SECTION"]
    freq = am["FREQUENCY"]
    rand = am["RANDOM"]
    n_pos = res["n_pos"]
    n_neg_hard = res["n_neg_hard"]

    diag = {
        "compose_balacc": comp["balanced_acc"],
        "noise_ctrl_balacc": nc["balanced_acc"],
        "direct_balacc": direct["balanced_acc"],
        "single_section_balacc": single["balanced_acc"],
        "frequency_balacc": freq["balanced_acc"],
        "random_balacc": rand["balanced_acc"],
        "compose_recall_pos": comp["recall_pos"],
        "direct_recall_pos": direct["recall_pos"],
        "compose_precision_on_proposals_raw": res["compose_precision_raw"],
        "compose_precision_on_proposals_noise_ctrl": res["compose_precision_noise_ctrl"],
        "false_path_rate_raw": res["false_path_rate_raw"],
        "compose_specificity_hard": comp["specificity_hard"],
        "coverage_recall_full": res["coverage_recall_full"],
        "n_pos": n_pos, "n_neg_hard": n_neg_hard,
    }

    # vacuous-n guard
    if n_pos < bands["min_pos"] or n_neg_hard < bands["min_neg_hard"]:
        return ("HARD_FAIL_VACUOUS_N",
                "insufficient composable positives ({}) or false-path negatives ({}); test underpowered".format(
                    n_pos, n_neg_hard), diag)

    best_compose_prec = max(res["compose_precision_raw"], res["compose_precision_noise_ctrl"])
    best_compose_balacc = max(comp["balanced_acc"], nc["balanced_acc"])
    best_baseline_balacc = max(direct["balanced_acc"], single["balanced_acc"],
                               freq["balanced_acc"], rand["balanced_acc"])
    beat_margin = best_compose_balacc - best_baseline_balacc

    # HARD_FAIL_NOISE: closure majority-false even under noise control
    if best_compose_prec < bands["fail_precision_max"]:
        return ("HARD_FAIL_NOISE",
                ("grown graph too noisy for reliable multi-hop: closure proposal precision "
                 "raw={:.3f} noise_ctrl={:.3f} (< {:.2f} floor); false paths dominate. "
                 "compose recovers recall={:.3f} that direct-lookup ({:.3f}) structurally lacks, "
                 "but cannot be trusted (majority-false).").format(
                    res["compose_precision_raw"], res["compose_precision_noise_ctrl"],
                    bands["fail_precision_max"], comp["recall_pos"], direct["recall_pos"]),
                diag)

    # HARD_PASS: reliable AND beats every non-compositional baseline
    if (best_compose_prec >= bands["hp_precision_floor"]
            and best_compose_balacc >= bands["hp_balacc_floor"]
            and beat_margin >= bands["hp_beat_margin"]):
        return ("HARD_PASS",
                ("reliable multi-hop: compose precision={:.3f} balacc={:.3f} beats best baseline "
                 "({:.3f}) by {:.3f}; recovers recall={:.3f} vs direct-lookup {:.3f}").format(
                    best_compose_prec, best_compose_balacc, best_baseline_balacc,
                    beat_margin, comp["recall_pos"], direct["recall_pos"]),
                diag)

    # MIDDLE_BAND: structural composition capability shown (recall gap over baselines) but not reliable
    return ("MIDDLE_BAND",
            ("composition recovers multi-hop recall={:.3f} that direct-lookup ({:.3f}) structurally "
             "cannot, but precision={:.3f} / balacc={:.3f} below HARD_PASS reliability; "
             "beat_margin={:.3f}").format(
                comp["recall_pos"], direct["recall_pos"], best_compose_prec,
                best_compose_balacc, beat_margin),
            diag)


# ------------------------- self-test (real code path) -------------------------

def self_test():
    print("[self-test] exercising REAL code path (v1 extractor + WN oracle + arms + verdict)", flush=True)
    # WN oracle sanity: dog is-a animal (indirect via carnivore/mammal); dog is NOT a type of car.
    assert wn_true_dist("dog", "animal") is not None, "WN: dog->animal ancestry expected"
    d = wn_true_dist("dog", "animal")
    assert d >= 1, ("WN dist", d)
    assert wn_true_dist("dog", "car") is None, "WN: dog->car must be false"
    assert wn_checkable("dog", "animal")
    # paraphrase-robust head-noun fallback: multiword term uses head noun
    assert wn_ancestors("guard dog"), "head-noun fallback for multiword"

    # tiny synthetic textbook exercising v1 extractor + graph-build + closure + arms
    text = "\n".join([
        "# Tiny Book",
        "##### Section Alpha",
        "A dog is a mammal that barks.",
        "A mammal is an animal with fur.",
        "###### Glossary",
        "dog: a mammal that is domesticated",
        "mammal: an animal that has fur",
        "##### Section Beta",
        "A trout is a fish that swims.",
        "A fish is an animal that lives in water.",
        "###### Glossary",
        "trout: a fish found in rivers",
        "fish: an animal that lives in water",
    ])
    secs = V1.parse_sections(text)
    graphs = build_graphs(secs)
    gloss = graphs["gloss"]
    # glossary is-a edges present
    assert "mammal" in gloss.get("dog", set()), gloss.get("dog")
    assert "animal" in gloss.get("mammal", set()), gloss.get("mammal")
    reach = closure(gloss)
    # composition: dog -> mammal -> animal (indirect, dist 2), no direct dog->animal edge
    assert reach.get("dog", {}).get("animal") == 2, ("dog->animal composed dist", reach.get("dog"))
    assert ("dog", "animal") not in {(c, p) for c, ps in gloss.items() for p in ps}
    # run query-set + arms
    rng = random.Random(RNG_SEED)
    res = build_query_set(graphs, rng)
    am = res["arm_metrics"]
    # ARMS-MUST-DIFFER: compositional and direct_lookup must give different YES patterns
    sig = res["arm_yes_signature"]
    assert sig["COMPOSITIONAL"] != sig["DIRECT_LOOKUP"] or res["n_neg_hard"] == 0, \
        "META_RULE_AF: COMPOSITIONAL vs DIRECT_LOOKUP must differ on negatives"
    # compositional recall should exceed direct-lookup recall on composable positives (structural)
    assert am["COMPOSITIONAL"]["recall_pos"] >= am["DIRECT_LOOKUP"]["recall_pos"]
    # verdict function runs and returns a valid tier
    v, msg, diag = compute_verdict(res, BANDS)
    assert v in ("HARD_PASS", "HARD_FAIL_NOISE", "HARD_FAIL_VACUOUS_N", "MIDDLE_BAND"), v
    # discriminator-fires: WN oracle labels BOTH classes on the real corpus is exercised at run;
    # here just assert oracle produced true + false in synthetic (dog->animal true, dog->car false)
    print("[self-test] PASS: nodes={} pos={} neg_hard={} neg_easy={} compose_recall={:.2f} "
          "direct_recall={:.2f} verdict={}".format(
              res["n_nodes"], res["n_pos"], res["n_neg_hard"], res["n_neg_easy"],
              am["COMPOSITIONAL"]["recall_pos"], am["DIRECT_LOOKUP"]["recall_pos"], v), flush=True)
    return True


# ------------------------- main -------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--smoke-sections", type=int, default=40,
                    help="leading sections used in smoke mode")
    args, _ = ap.parse_known_args()

    if args.self_test:
        ok = self_test()
        sys.exit(0 if ok else 1)

    run_mode = args.mode
    output_dir = os.path.join(REPO, "data", "exp_{}{}".format(
        ANCHOR_NAME, "_smoke" if run_mode == "smoke" else ""))
    _write_start_marker(output_dir, run_mode, expected_n_units=1)

    t0 = time.perf_counter()
    with open(CORPUS, "r", encoding="utf-8") as f:
        text = f.read()
    sections_all = V1.parse_sections(text)
    sections = sections_all[:args.smoke_sections] if run_mode == "smoke" else sections_all

    graphs = build_graphs(sections)
    print("[{}] sections={} gloss_nodes/edges={}/{} prose_edges={} full_edges={}".format(
        run_mode, len(sections),
        len(set(graphs["gloss"].keys()) | {p for ps in graphs["gloss"].values() for p in ps}),
        graphs["gloss_edges"], graphs["prose_edges"],
        sum(len(v) for v in graphs["full"].values())), flush=True)

    rng = random.Random(RNG_SEED)
    res = build_query_set(graphs, rng)
    verdict, verdict_msg, diag = compute_verdict(res, BANDS)
    elapsed = time.perf_counter() - t0

    am = res["arm_metrics"]
    # discriminator-fires gate: WN oracle labeled both classes + arms give distinct YES-rates
    yes_rates = {a: am[a]["yes_rate"] for a in am}
    distinct_yes = len(set(round(v, 3) for v in yes_rates.values())) >= 2
    gate = {
        "discriminator_fires": bool(res["n_pos"] > 0 and res["n_neg_hard"] > 0 and distinct_yes),
        "oracle_labeled_both_classes": bool(res["n_pos"] > 0 and res["n_neg_hard"] > 0),
        "arms_differ": bool(distinct_yes),
        "arm_yes_rates": yes_rates,
        "real_baselines": ["DIRECT_LOOKUP", "SINGLE_SECTION", "FREQUENCY", "RANDOM"],
        "difficulty_on": "positives = WN-true indirect (dist>=2), NO direct book edge, book-composable",
        "one_variable": "composition/closure ON (COMPOSITIONAL/NOISE_CTRL) vs OFF (DIRECT_LOOKUP)",
        "noise_control": "drop generic-hub parents (indeg>{}) + depth<= {}".format(
            NOISE_HUB_MAX, NOISE_DEPTH_MAX),
    }

    # drop large signature from persisted metrics (keep sizes)
    arm_sig_sizes = {a: sum(res["arm_yes_signature"][a]) for a in res["arm_yes_signature"]}

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": ("{}: compose_prec_raw={:.3f} nc={:.3f} false_path_rate={:.3f} | "
                    "balacc compose={:.3f} direct={:.3f} freq={:.3f} | "
                    "recall compose={:.3f} direct={:.3f} | n_pos={} n_neg_hard={}").format(
            verdict, res["compose_precision_raw"], res["compose_precision_noise_ctrl"],
            res["false_path_rate_raw"], am["COMPOSITIONAL"]["balanced_acc"],
            am["DIRECT_LOOKUP"]["balanced_acc"], am["FREQUENCY"]["balanced_acc"],
            am["COMPOSITIONAL"]["recall_pos"], am["DIRECT_LOOKUP"]["recall_pos"],
            res["n_pos"], res["n_neg_hard"]),
        "elapsed_s": round(elapsed, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "bands": BANDS,
        "diag": diag,
        "gate": gate,
        "n_nodes": res["n_nodes"],
        "n_direct_edges": res["n_direct_edges"],
        "gloss_edges": graphs["gloss_edges"],
        "prose_edges": graphs["prose_edges"],
        "full_edges": sum(len(v) for v in graphs["full"].values()),
        "n_wn_true_all": res["n_wn_true_all"],
        "n_pos": res["n_pos"],
        "n_neg_hard": res["n_neg_hard"],
        "n_neg_easy": res["n_neg_easy"],
        "base_rate": res["base_rate"],
        "coverage_recall_full": res["coverage_recall_full"],
        "hop_depth_hist_pos": res["hop_depth_hist_pos"],
        "compose_precision_raw": res["compose_precision_raw"],
        "compose_precision_raw_checkable": res["compose_precision_raw_checkable"],
        "compose_precision_raw_true": res["compose_precision_raw_true"],
        "compose_precision_noise_ctrl": res["compose_precision_noise_ctrl"],
        "compose_precision_nc_checkable": res["compose_precision_nc_checkable"],
        "false_path_rate_raw": res["false_path_rate_raw"],
        "arm_metrics": am,
        "arm_yes_counts_on_neg": arm_sig_sizes,
        "top_hubs": res["top_hubs"],
    }
    _write_metrics_atomic(output_dir, metrics)
    print("[{}] VERDICT={} {}".format(run_mode, verdict, metrics["summary"]), flush=True)
    print("[{}] {}".format(run_mode, verdict_msg), flush=True)
    for a in ["COMPOSITIONAL", "COMPOSE_NOISE_CTRL", "DIRECT_LOOKUP", "SINGLE_SECTION", "FREQUENCY", "RANDOM"]:
        m = am[a]
        print("   {:20s} balacc={:.3f} recall={:.3f} spec={:.3f} spec_hard={:.3f} prec={:.3f} f1={:.3f}".format(
            a, m["balanced_acc"], m["recall_pos"], m["specificity_neg"], m["specificity_hard"],
            m["precision"], m["f1"]), flush=True)
    print("[{}] metrics -> {}".format(run_mode, os.path.join(output_dir, "metrics.json")), flush=True)


if __name__ == "__main__":
    OUT_FOR_CRASH = os.path.join(REPO, "data", "exp_{}".format(ANCHOR_NAME))
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUT_FOR_CRASH, e)
        raise
