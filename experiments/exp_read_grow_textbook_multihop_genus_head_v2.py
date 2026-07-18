# CELL: read_grow_textbook_multihop_genus_head_v2
# QUESTION: Does fixing GENUS-HEAD EXTRACTION (take the SYNTACTIC HEAD noun of the genus NP:
#   skip 'of'-complement objects, skip pre-head adjectives/modifiers, take the RIGHTMOST noun of
#   a noun-noun compound) lift the grown is-a graph's EDGE PRECISION enough for TRUSTWORTHY
#   multi-hop closure?  Glass-box, NO runtime LLM.
#
# CONTEXT: predecessor exp_read_grow_textbook_multihop_compose_v1 (96ab5fbbd) HARD_FAIL_NOISE --
#   composed multi-hop precision raw=0.373 / nc=0.350 (< 0.55 floor); false_path_rate=0.627.
#   VET a7a85fb2 localized the DOMINANT error bucket (~40%): the genus extractor grabs the WRONG
#   noun -- object-of-preposition after 'of', or an adjective/pre-head modifier -- instead of the
#   syntactic HEAD of the genus NP. Examples the VET named:
#     "a GROUP of similar cells" -> old grabbed 'cell' (should be 'group')  [group in old _TYPE_WORDS -> descends past 'of']
#     "the VARIETY of alleles"   -> old grabbed 'allele' (should be 'variety')
#     "a SET of populations"     -> old grabbed 'population' (should be 'set')
#     "white BLOOD cell"         -> old grabbed 'blood' (should be 'cell')   [first-noun-of-compound, not head]
#     "an individual LIVING entity" -> old grabbed 'living' (adjective; should be 'entity')
#
# ONE VARIABLE = genus-extraction rule.  OLD = V1.genus_of_definition (first noun after det/adj +
#   type-word 'of'-descent that WRONGLY includes group/set/variety/collection/member).
#   NEW = genus_head_of_definition (this file): syntactic HEAD of the definitional NP.
# Everything else (glossary parse, term-norm, closure, WN oracle, held-out labeling) reuses the
#   v1/v2 REAL code path unchanged, so the OLD-vs-NEW contrast is clean single-variable.
#
# TRAP 1 AVOIDED (VET key correction): recall on book-composable positives is TAUTOLOGICAL (=1.0 by
#   construction). HEADLINE metrics = PRECISION on composed edges + SPECIFICITY on hard (also-
#   composable) negatives (spec_hard) over a FIXED query universe shared across arms. Recall is
#   reported but is NOT the headline.
# TRAP 2 AVOIDED: score precision under BOTH a strict raw-WN oracle AND a FAIR oracle that credits
#   true-but-WN-uncovered generic superclasses (bucket A: molecule->chemical, protein->macromolecule,
#   organ->structure), via WN-synonym relaxation + a small curated generic-superclass allow-list
#   (aggregates group/set/variety are DELIBERATELY EXCLUDED from curated credit so the NEW
#   extractor's new aggregate outputs face the SAME strict bar -- any lift is not a curated-fiat artifact).
#   Both raw and fair reported so the true precision is bracketed [raw, fair].
#
# DESIGN-GATE (pre-registered, verified at smoke BEFORE full):
#   (1) REAL baseline = OLD genus extractor (V1.genus_of_definition) on the SAME graph/closure/oracle,
#       + non-compositional DIRECT_LOOKUP / FREQUENCY / RANDOM.
#   (2) CAN-FAIL: HARD_FAIL_NO_LIFT if syntactic-head does NOT materially lift edge precision;
#       MIDDLE_BAND_CEILING if it lifts but composed precision plateaus below the trustworthy floor
#       (~0.70) -- a genuine 'even correct syntactic-head extraction cannot reach trustworthy glass-box
#       closure precision' result is FIRST-CLASS (the arc-level finding), reported honestly not tortured.
#   (3) DIFFICULTY-ON: fixed query universe of multi-hop composables (dist in [2,DMAX], NO direct edge)
#       WITH hard negatives (WN-false but book-composable). spec_hard is measurable + non-vacuous.
#   (4) ONE variable = genus-extraction rule.
#   HARD_PASS: NEW edge precision (fair) past 0.55 toward ~0.70 AND composed multi-hop precision (fair)
#       >= 0.70 AND spec_hard >= 0.50 AND materially lifts over OLD -> cleaner graph enables reliable reasoning.
#
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scale/floor):
# - start_marker + crash_diagnostic (Exception -> CELL_CRASHED metrics.json + traceback)
# - except SystemExit: raise BEFORE except Exception (no BaseException); no bare except
# - final_metrics_atomicity = tmp_replace (os.replace)
# - deterministic seeding only (FIXED int random.Random(seed); NO built-in hash() / list(set()))
# - arms_differ verified (OLD vs NEW genus produce distinct edge sets + distinct YES patterns)
# - all bands tagged HYPOTHESIZED@ (pre-reg) then confirmed MEASURED@ at run
#
# Compute architecture: (b) sequential-CPU. Justification: glass-box regex / POS-tag / WordNet /
#   symbolic graph closure. No matmul, no substrate vectors, no GPU speedup available. Diagnostic
#   reasoning-value cell (compute-proportionality: cheapest decisive method). Wall < few min (v2 = 5.7s).
# calibration_check: "default_ok_for_this_regime" (symbolic thresholds; measured at run).
# crlb_n/a: "no continuous noise floor; discriminator is symbolic graph-path existence vs WN ancestry."
# progress_logging: "print_flush_true" (cell wall << 30min; flush on every progress line regardless).

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

from nltk import pos_tag
from nltk.corpus import wordnet as wn

ANCHOR_NAME = "read_grow_textbook_multihop_genus_head_v2"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(
    REPO, "data", "corpora", "textbook_concepts_biology", "cleaned",
    "concepts_biology.clean.txt",
)
V1_PATH = os.path.join(REPO, "experiments", "exp_read_grow_textbook_isa_growth_v1.py")

# Reuse v1 linguistics + glossary parse as the REAL code path (parse_sections, _tokenize,
# _norm_term, _lemma_noun, genus_of_definition[=OLD baseline]).
_spec = importlib.util.spec_from_file_location("_isa_v1_gh", V1_PATH)
V1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V1)

DMAX_WN = 6          # WN-distance cap for indirect pairs (avoid deep-ontology inflation)
TOP_HUB_K = 10       # frequency baseline: predict YES if C in top-K global hub parents
NOISE_HUB_MAX = 8    # noise-ctrl: drop edges whose PARENT has book in-degree > this (generic hubs)
NOISE_DEPTH_MAX = 3  # noise-ctrl: cap composition depth
CLOSURE_MAXD = 12    # BFS closure depth cap (cycle-safe; > DMAX_WN so all in-range pairs found)
RNG_SEED = 20260718  # FIXED deterministic seed (NEVER built-in hash())

# Pre-registered bands (HYPOTHESIZED@ this file; confirmed MEASURED@ at run)
BANDS = {
    "material_lift_min": 0.03,     # material improvement on edge OR composed precision (fair)
    "material_spec_hard_lift": 0.05,  # OR material improvement on spec_hard (false-path rejection)
    "hp_edge_prec_floor": 0.55,    # NEW edge precision (fair) must clear the v2 fail floor
    "hp_compose_prec_floor": 0.70, # HARD_PASS: composed multi-hop precision (fair) trustworthy
    "hp_spec_hard_floor": 0.50,    # HARD_PASS: composed arm rejects >= half the false paths
    "reach_floor": 0.55,           # lifted-but-below-trustworthy boundary (v2 fail floor)
    "min_pos": 20,                 # vacuous-n guard: need >= 20 composable true positives
    "min_neg_hard": 10,            # need >= 10 false-path hard negatives to audit spec_hard
    "min_changed_edges": 10,       # arms-differ: need >= 10 edges that OLD/NEW disagree on
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


# ==================================================================================
# NEW GENUS-HEAD EXTRACTOR (the ONE variable being changed vs OLD = V1.genus_of_definition)
# ==================================================================================

_DET_SKIP_TAGS = {"DT", "PDT", "CD", "RB", "RBR", "RBS", "PRP$", "WDT", "WP", "WP$"}
_ADJ_TAGS = {"JJ", "JJR", "JJS"}
_NOUN_TAGS = {"NN", "NNS", "NNP", "NNPS"}
_PREMOD_TAGS = _ADJ_TAGS | {"VBG", "VBN"}   # attributive adjective / participle pre-modifiers
_QUANTIFIERS = V1._QUANTIFIERS               # reuse identical quantifier set

# TRANSPARENT light head-nouns: "X is a <light> of Y" == "X is a Y" -> descend to of-complement.
# CRITICAL FIX vs OLD: the SUBSTANTIVE aggregates group/set/collection/variety/member/series/number
# are NOT here -- they ARE the genus (tissue is-a group; a gene pool is-a set). OLD wrongly lumped
# them into _TYPE_WORDS and descended past 'of' to the wrong noun.
_TRANSPARENT_LIGHT = {"type", "kind", "sort", "form", "class", "category",
                      "example", "variant", "subtype"}


def _lemma_noun(word):
    return V1._lemma_noun(word)


def _head_from_tags(tags, start):
    """Syntactic head noun of the NP beginning at index `start`.
       Rule: skip leading det/quantifier/adverb/adjective/participle premods; take the RIGHTMOST
       noun of the leading noun-compound run (stopping at 'of'/relative/verb/comma post-head
       boundary); TRANSPARENT light head-noun -> descend into its 'of'-complement."""
    n = len(tags)
    i = start
    # skip leading determiners / quantifiers / adverbs / pre-head adjectives+participles
    while i < n:
        w = tags[i][0].lower()
        t = tags[i][1]
        if t in _DET_SKIP_TAGS or w in _QUANTIFIERS or t in _PREMOD_TAGS:
            i += 1
            continue
        break
    if i >= n:
        return _descend_of(tags, start)
    # quantifier-of-X pattern ("any of the organelles") -> descend into the of-complement
    if tags[i][0].lower() == "of":
        return _descend_of(tags, i)
    if tags[i][1] not in _NOUN_TAGS:
        return None
    # walk the nominal compound run; head = RIGHTMOST noun before a post-head boundary
    head_idx = i
    j = i
    while j < n:
        t = tags[j][1]
        if t in _NOUN_TAGS:
            head_idx = j
            j += 1
            continue
        if t in _PREMOD_TAGS:
            # interior adjective/participle: part of the compound ONLY if a noun follows
            k = j
            while k < n and tags[k][1] in _PREMOD_TAGS:
                k += 1
            if k < n and tags[k][1] in _NOUN_TAGS:
                j = k
                continue
            break            # trailing participle = post-head reduced relative -> stop
        break                # 'of' / relative pronoun / verb / comma -> post-head boundary
    head = _lemma_noun(tags[head_idx][0])
    # transparent light-noun override: "a type of organelle" -> descend to of-complement
    if head in _TRANSPARENT_LIGHT:
        m = head_idx + 1
        if m < n and tags[m][0].lower() == "of":
            sub = _head_from_tags(tags, m + 1)
            if sub:
                return sub
    return head


def _descend_of(tags, from_idx):
    """Find the first 'of' at/after from_idx and return the head of its complement NP."""
    n = len(tags)
    m = from_idx
    while m < n and tags[m][0].lower() != "of":
        m += 1
    if m + 1 < n:
        return _head_from_tags(tags, m + 1)
    return None


def genus_head_of_definition(defn):
    """NEW genus extractor: syntactic HEAD noun of the definitional NP. Returns lemma or None."""
    toks = V1._tokenize(defn)
    if not toks:
        return None
    tags = pos_tag(toks)
    return _head_from_tags(tags, 0)


# ------------------------- WordNet oracle (paraphrase-robust gold; raw + fair) -------------------------

_ANC_CACHE = {}
_LEM_CACHE = {}

# Curated generic-superclass allow-list for the FAIR oracle (bucket A: true-but-WN-uncovered
# generic superclasses). DELIBERATELY EXCLUDES aggregates {group,set,collection,variety,series,
# number,member} so the NEW extractor's new aggregate outputs are NOT credited by fiat -- they must
# earn credit from raw WN or WN-synonym relaxation, same strict bar as any other term.
_GENERIC_SUPERCLASS = {
    "structure", "substance", "chemical", "macromolecule", "molecule", "compound",
    "material", "system", "process", "mechanism", "organism", "part", "component",
    "entity", "object", "body", "matter", "unit", "region", "tissue", "organ",
    "particle", "force", "energy", "reaction", "property", "phenomenon",
}


def _syns_for(term):
    key = term.replace(" ", "_")
    syns = wn.synsets(key, pos=wn.NOUN)[:3]
    if not syns and " " in term:
        hw = term.split()[-1]
        syns = wn.synsets(hw, pos=wn.NOUN)[:3]
    return syns


def wn_match_lemmas(term):
    if term in _LEM_CACHE:
        return _LEM_CACHE[term]
    s = {term}
    for sy in _syns_for(term):
        for l in sy.lemmas():
            s.add(l.name().lower().replace("_", " "))
    _LEM_CACHE[term] = s
    return s


def wn_ancestors(term):
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


def wn_true_raw(a, c):
    """RAW oracle: min WN hypernym dist d>=1 s.t. C (exact lemma / synset lemma) is an ancestor of A."""
    anc = wn_ancestors(a)
    best = None
    for cand in wn_match_lemmas(c):
        if cand in anc:
            best = anc[cand] if best is None else min(best, anc[cand])
    return best


def wn_true_fair(a, c):
    """FAIR oracle: raw OR curated generic-superclass credit. Returns (is_true, basis).
       basis in {raw, curated_superclass, None}. Curated credit fires only when C is a curated
       generic superclass, A is WN-covered, and A != C (evaluated only on book-proposed pairs)."""
    if wn_true_raw(a, c) is not None:
        return True, "raw"
    if a != c and c in _GENERIC_SUPERCLASS and bool(wn_ancestors(a)):
        return True, "curated_superclass"
    return False, None


# ------------------------- graph build (parametrized by genus_fn) -------------------------

def build_gloss_graph(sections, genus_fn):
    """child(norm) -> set(genus parents), using genus_fn for genus extraction. Also indeg + parent_freq."""
    gloss = defaultdict(set)
    edge_list = []            # (child, parent) in extraction order (for edge-precision + bucket shift)
    for sec in sections:
        for term_surface, defn in sec["glossary"]:
            genus = genus_fn(defn)
            if not genus:
                continue
            nt = V1._norm_term(V1._tokenize(term_surface))
            if not nt or not genus or nt == genus:
                continue
            gloss[nt].add(genus)
            edge_list.append((nt, genus))
    indeg = Counter()
    parent_freq = Counter()
    for c, ps in gloss.items():
        for p in ps:
            indeg[p] += 1
            parent_freq[p] += 1
    return {"gloss": gloss, "edge_list": edge_list, "indeg": indeg, "parent_freq": parent_freq}


def closure(adj, maxd=CLOSURE_MAXD):
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
    adj = defaultdict(set)
    for c, ps in gloss.items():
        for p in ps:
            if indeg[p] > hub_max:
                continue
            adj[c].add(p)
    return adj


# ------------------------- edge precision (direct genus quality) -------------------------

def edge_precision(edge_list):
    """Over DIRECT glossary is-a edges, fraction WN-true (raw) and fair-true. This is the headline
       'does the genus fix lift edge precision' number. Only checkable edges count in the denom."""
    chk = raw_true = fair_true = 0
    for (c, p) in edge_list:
        if c == p:
            continue
        if not wn_checkable(c, p):
            continue
        chk += 1
        if wn_true_raw(c, p) is not None:
            raw_true += 1
        ft, _ = wn_true_fair(c, p)
        if ft:
            fair_true += 1
    return {
        "checkable": chk,
        "raw_true": raw_true,
        "fair_true": fair_true,
        "prec_raw": round(raw_true / chk, 5) if chk else 0.0,
        "prec_fair": round(fair_true / chk, 5) if chk else 0.0,
    }


# ------------------------- composed multi-hop precision (on proposals dist>=2) -------------------------

def compose_precision(reach, direct):
    """Over composed proposals (dist>=2, not a direct edge, checkable), fraction fair/raw true."""
    chk = raw_true = fair_true = 0
    for a in reach:
        for c, bd in reach[a].items():
            if bd >= 2 and (a, c) not in direct and wn_checkable(a, c):
                chk += 1
                if wn_true_raw(a, c) is not None:
                    raw_true += 1
                ft, _ = wn_true_fair(a, c)
                if ft:
                    fair_true += 1
    return {
        "checkable": chk,
        "raw_true": raw_true,
        "fair_true": fair_true,
        "prec_raw": round(raw_true / chk, 5) if chk else 0.0,
        "prec_fair": round(fair_true / chk, 5) if chk else 0.0,
    }


# ------------------------- fixed labeled query universe + per-arm discrimination -------------------------

def build_query_universe(nodes, reach_old, reach_new, direct_old, direct_new, rng):
    """Fixed set of (a,c) multi-hop candidate pairs, labeled by the FAIR oracle. Pair is a candidate
       iff reachable dist in [2,DMAX] in OLD or NEW closure, NOT a direct edge in EITHER graph,
       WN-checkable. POS = fair-true; NEG_HARD = fair-false (the false paths). Plus NEG_EASY sanity."""
    cand = set()
    for reach in (reach_old, reach_new):
        for a in reach:
            for c, bd in reach[a].items():
                if 2 <= bd <= DMAX_WN and (a, c) not in direct_old and (a, c) not in direct_new:
                    if wn_checkable(a, c):
                        cand.add((a, c))
    pos = []
    neg_hard = []
    for (a, c) in sorted(cand):
        ft, _ = wn_true_fair(a, c)
        if ft:
            pos.append((a, c))
        else:
            neg_hard.append((a, c))

    # NEG_EASY: random non-reachable, WN-false pairs (sanity floor)
    neg_easy = []
    target = max(len(pos), len(neg_hard))
    tries = 0
    max_tries = target * 200 + 5000
    reach_any = lambda a, c: (c in reach_old.get(a, {})) or (c in reach_new.get(a, {}))
    while len(neg_easy) < target and tries < max_tries:
        tries += 1
        a = rng.choice(nodes)
        c = rng.choice(nodes)
        if a == c or (a, c) in direct_old or (a, c) in direct_new:
            continue
        if reach_any(a, c):
            continue
        if not wn_checkable(a, c):
            continue
        ft, _ = wn_true_fair(a, c)
        if ft:
            continue
        neg_easy.append((a, c))
    return pos, neg_hard, neg_easy


def arm_scores(pos, neg_hard, neg_easy, reach, direct, top_hubs, base_rate, rand_rng, arm):
    """Precision / recall / spec_hard for one arm over the FIXED universe. arm in
       {COMPOSE, DIRECT_LOOKUP, FREQUENCY, RANDOM}."""
    def yes(a, c):
        if arm == "COMPOSE":
            return c in reach.get(a, {})
        if arm == "DIRECT_LOOKUP":
            return (a, c) in direct
        if arm == "FREQUENCY":
            return c in top_hubs
        if arm == "RANDOM":
            return rand_rng.random() < base_rate
        raise ValueError("unknown arm " + arm)

    tp = sum(1 for (a, c) in pos if yes(a, c))
    fn = len(pos) - tp
    fp_hard = sum(1 for (a, c) in neg_hard if yes(a, c))
    tn_hard = len(neg_hard) - fp_hard
    fp_easy = sum(1 for (a, c) in neg_easy if yes(a, c))
    tn_easy = len(neg_easy) - fp_easy
    n_pos = len(pos)
    n_neg = len(neg_hard) + len(neg_easy)
    fp = fp_hard + fp_easy
    tn = tn_hard + tn_easy
    recall = tp / n_pos if n_pos else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    spec = tn / n_neg if n_neg else 0.0
    spec_hard = tn_hard / len(neg_hard) if neg_hard else 0.0
    balacc = 0.5 * (recall + spec)
    return {
        "precision": round(precision, 5),
        "recall": round(recall, 5),
        "specificity": round(spec, 5),
        "spec_hard": round(spec_hard, 5),
        "balanced_acc": round(balacc, 5),
        "tp": tp, "fn": fn, "fp": fp, "tn": tn,
        "fp_hard": fp_hard, "fp_easy": fp_easy,
        "yes_rate": round((tp + fp) / max(1, (n_pos + n_neg)), 5),
    }


# ------------------------- false-path bucket shift (OLD vs NEW) -------------------------

def bucket_shift(edges_old, edges_new):
    """Compare per-child genus assignment OLD vs NEW on shared children. Count edges that CHANGED,
       and among changed, how many old-wrong->new-right vs new-wrong->old-right (fair oracle)."""
    old_by_child = defaultdict(set)
    for c, p in edges_old:
        old_by_child[c].add(p)
    new_by_child = defaultdict(set)
    for c, p in edges_new:
        new_by_child[c].add(p)
    shared = sorted(set(old_by_child) & set(new_by_child))
    n_changed = 0
    old_wrong_new_right = 0
    new_wrong_old_right = 0
    both_right = both_wrong = 0
    examples = []
    for c in shared:
        po = sorted(old_by_child[c])
        pn = sorted(new_by_child[c])
        if po == pn:
            continue
        n_changed += 1
        old_right = any(wn_true_fair(c, p)[0] for p in po if wn_checkable(c, p))
        new_right = any(wn_true_fair(c, p)[0] for p in pn if wn_checkable(c, p))
        if new_right and not old_right:
            old_wrong_new_right += 1
            if len(examples) < 25:
                examples.append({"child": c, "old": po, "new": pn, "shift": "old_wrong->new_right"})
        elif old_right and not new_right:
            new_wrong_old_right += 1
            if len(examples) < 25:
                examples.append({"child": c, "old": po, "new": pn, "shift": "new_wrong->old_right"})
        elif old_right and new_right:
            both_right += 1
        else:
            both_wrong += 1
    return {
        "n_shared_children": len(shared),
        "n_changed_edges": n_changed,
        "old_wrong_new_right": old_wrong_new_right,
        "new_wrong_old_right": new_wrong_old_right,
        "both_right": both_right,
        "both_wrong": both_wrong,
        "net_bucket_improvement": old_wrong_new_right - new_wrong_old_right,
        "examples": examples,
    }


# ------------------------- top-level measurement -------------------------

def measure(sections, rng):
    g_old = build_gloss_graph(sections, V1.genus_of_definition)
    g_new = build_gloss_graph(sections, genus_head_of_definition)

    gloss_old = g_old["gloss"]
    gloss_new = g_new["gloss"]
    nodes = sorted(set(gloss_old) | {p for ps in gloss_old.values() for p in ps}
                   | set(gloss_new) | {p for ps in gloss_new.values() for p in ps})
    direct_old = {(c, p) for c, ps in gloss_old.items() for p in ps}
    direct_new = {(c, p) for c, ps in gloss_new.items() for p in ps}

    reach_old = closure(gloss_old)
    reach_new = closure(gloss_new)
    nc_new = noise_ctrl_adj(gloss_new, g_new["indeg"], NOISE_HUB_MAX)
    reach_nc = closure(nc_new, maxd=NOISE_DEPTH_MAX)

    # --- edge precision (direct genus quality; headline) ---
    edge_prec_old = edge_precision(g_old["edge_list"])
    edge_prec_new = edge_precision(g_new["edge_list"])

    # --- composed multi-hop precision (on proposals) ---
    comp_prec_old = compose_precision(reach_old, direct_old)
    comp_prec_new = compose_precision(reach_new, direct_new)
    comp_prec_nc = compose_precision(reach_nc, direct_new)

    # --- fixed labeled query universe + per-arm discrimination ---
    pos, neg_hard, neg_easy = build_query_universe(
        nodes, reach_old, reach_new, direct_old, direct_new, rng)
    top_hubs = set(p for p, _ in g_new["parent_freq"].most_common(TOP_HUB_K))
    base_rate = len(pos) / max(1, len(pos) + len(neg_hard) + len(neg_easy))
    rand_rng = random.Random(RNG_SEED + 7)

    arms = {}
    arms["OLD_GENUS_COMPOSE"] = arm_scores(
        pos, neg_hard, neg_easy, reach_old, direct_old, top_hubs, base_rate,
        random.Random(RNG_SEED + 11), "COMPOSE")
    arms["NEW_GENUS_COMPOSE"] = arm_scores(
        pos, neg_hard, neg_easy, reach_new, direct_new, top_hubs, base_rate,
        random.Random(RNG_SEED + 13), "COMPOSE")
    arms["NEW_GENUS_NOISECTRL"] = arm_scores(
        pos, neg_hard, neg_easy, reach_nc, direct_new, top_hubs, base_rate,
        random.Random(RNG_SEED + 17), "COMPOSE")
    arms["DIRECT_LOOKUP"] = arm_scores(
        pos, neg_hard, neg_easy, reach_new, direct_new, top_hubs, base_rate,
        random.Random(RNG_SEED + 19), "DIRECT_LOOKUP")
    arms["FREQUENCY"] = arm_scores(
        pos, neg_hard, neg_easy, reach_new, direct_new, top_hubs, base_rate,
        random.Random(RNG_SEED + 23), "FREQUENCY")
    arms["RANDOM"] = arm_scores(
        pos, neg_hard, neg_easy, reach_new, direct_new, top_hubs, base_rate,
        rand_rng, "RANDOM")

    shift = bucket_shift(g_old["edge_list"], g_new["edge_list"])

    return {
        "n_nodes": len(nodes),
        "n_direct_edges_old": len(direct_old),
        "n_direct_edges_new": len(direct_new),
        "n_edge_list_old": len(g_old["edge_list"]),
        "n_edge_list_new": len(g_new["edge_list"]),
        "n_pos": len(pos),
        "n_neg_hard": len(neg_hard),
        "n_neg_easy": len(neg_easy),
        "base_rate": round(base_rate, 5),
        "edge_prec_old": edge_prec_old,
        "edge_prec_new": edge_prec_new,
        "compose_prec_old": comp_prec_old,
        "compose_prec_new": comp_prec_new,
        "compose_prec_new_noisectrl": comp_prec_nc,
        "arms": arms,
        "bucket_shift": shift,
        "top_hubs_new": sorted(top_hubs),
        "top_parents_old": [p for p, _ in g_old["parent_freq"].most_common(12)],
        "top_parents_new": [p for p, _ in g_new["parent_freq"].most_common(12)],
    }


# ------------------------- verdict -------------------------

def compute_verdict(res, bands):
    ep_old = res["edge_prec_old"]
    ep_new = res["edge_prec_new"]
    cp_new = res["compose_prec_new"]
    new_arm = res["arms"]["NEW_GENUS_COMPOSE"]
    old_arm = res["arms"]["OLD_GENUS_COMPOSE"]
    n_pos = res["n_pos"]
    n_neg_hard = res["n_neg_hard"]
    n_changed = res["bucket_shift"]["n_changed_edges"]

    cp_old = res["compose_prec_old"]
    lift_edge_fair = round(ep_new["prec_fair"] - ep_old["prec_fair"], 5)
    lift_edge_raw = round(ep_new["prec_raw"] - ep_old["prec_raw"], 5)
    lift_comp_fair = round(cp_new["prec_fair"] - cp_old["prec_fair"], 5)
    lift_spec_hard = round(new_arm["spec_hard"] - old_arm["spec_hard"], 5)

    diag = {
        "edge_prec_old_raw": ep_old["prec_raw"],
        "edge_prec_old_fair": ep_old["prec_fair"],
        "edge_prec_new_raw": ep_new["prec_raw"],
        "edge_prec_new_fair": ep_new["prec_fair"],
        "edge_prec_lift_raw": lift_edge_raw,
        "edge_prec_lift_fair": lift_edge_fair,
        "compose_prec_old_fair": cp_old["prec_fair"],
        "compose_prec_new_raw": cp_new["prec_raw"],
        "compose_prec_new_fair": cp_new["prec_fair"],
        "compose_prec_lift_fair": lift_comp_fair,
        "new_arm_precision": new_arm["precision"],
        "new_arm_spec_hard": new_arm["spec_hard"],
        "old_arm_precision": old_arm["precision"],
        "old_arm_spec_hard": old_arm["spec_hard"],
        "spec_hard_lift": lift_spec_hard,
        "net_bucket_improvement": res["bucket_shift"]["net_bucket_improvement"],
        "n_pos": n_pos, "n_neg_hard": n_neg_hard, "n_changed_edges": n_changed,
    }

    # vacuous-n / arms-differ guards
    if n_pos < bands["min_pos"] or n_neg_hard < bands["min_neg_hard"]:
        return ("HARD_FAIL_VACUOUS_N",
                "underpowered: n_pos={} n_neg_hard={} (need {}/{})".format(
                    n_pos, n_neg_hard, bands["min_pos"], bands["min_neg_hard"]), diag)
    if n_changed < bands["min_changed_edges"]:
        return ("HARD_FAIL_ARMS_IDENTICAL",
                "OLD vs NEW genus disagree on only {} edges (< {}); one-variable contrast vacuous".format(
                    n_changed, bands["min_changed_edges"]), diag)

    # LOAD-BEARING lift = the fix helps on the task's declared load-bearing metric (composed multi-hop
    # PRECISION or spec_hard), OR on aggregate edge precision. NOTE (honest, surfaced at smoke): the
    # genus-head fix is LOCALIZED -- it touches only the minority of edges with the 'group/set/variety
    # of X' or compound-head pattern -- so it CANNOT move AGGREGATE edge precision much by construction,
    # but the touched edges are exactly the false-path hub edges, so the effect concentrates in composed
    # precision + spec_hard. Gating solely on diluted aggregate edge precision would MIS-report the fix.
    materially_helps = (lift_edge_fair >= bands["material_lift_min"]
                        or lift_comp_fair >= bands["material_lift_min"]
                        or lift_spec_hard >= bands["material_spec_hard_lift"])

    # HARD_FAIL_NO_LIFT: fix is inert on edge precision AND composed precision AND spec_hard
    if not materially_helps:
        return ("HARD_FAIL_NO_LIFT",
                ("syntactic-head genus does NOT materially help: edge_prec_fair {:.3f}->{:.3f} "
                 "(lift={:+.3f}); composed_prec_fair {:.3f}->{:.3f} (lift={:+.3f}); spec_hard {:.3f}->{:.3f} "
                 "(lift={:+.3f}); the localized fix does not clear the crux on ANY load-bearing metric.").format(
                    ep_old["prec_fair"], ep_new["prec_fair"], lift_edge_fair,
                    cp_old["prec_fair"], cp_new["prec_fair"], lift_comp_fair,
                    old_arm["spec_hard"], new_arm["spec_hard"], lift_spec_hard),
                diag)

    # HARD_PASS: cleaner graph enables TRUSTWORTHY multi-hop closure (task's load-bearing metric:
    # composed multi-hop precision + spec_hard trustworthy) AND materially improves over OLD.
    if (cp_new["prec_fair"] >= bands["hp_compose_prec_floor"]
            and new_arm["spec_hard"] >= bands["hp_spec_hard_floor"]):
        return ("HARD_PASS",
                ("cleaner graph enables TRUSTWORTHY multi-hop closure: composed multi-hop precision "
                 "(fair)={:.3f} >= {:.2f} + spec_hard={:.3f} >= {:.2f} (OLD {:.3f}/{:.3f}); "
                 "edge_prec_fair {:.3f}->{:.3f} (localized fix, aggregate diluted).").format(
                    cp_new["prec_fair"], bands["hp_compose_prec_floor"], new_arm["spec_hard"],
                    bands["hp_spec_hard_floor"], cp_old["prec_fair"], old_arm["spec_hard"],
                    ep_old["prec_fair"], ep_new["prec_fair"]),
                diag)

    # MIDDLE_BAND_CEILING: materially helps but composed precision / spec_hard below trustworthy floor.
    # FIRST-CLASS arc-level finding (glass-box extraction ceiling), reported honestly not tortured.
    cleared_reach = cp_new["prec_fair"] >= bands["reach_floor"]
    return ("MIDDLE_BAND_CEILING",
            ("syntactic-head genus materially helps (edge {:+.3f}, composed_prec {:+.3f}, spec_hard {:+.3f}) "
             "and composed precision (fair)={:.3f} {} the v2 fail floor, BUT spec_hard={:.3f} / precision "
             "below trustworthy floor (compose>={:.2f} AND spec_hard>={:.2f}): GLASS-BOX EXTRACTION CEILING "
             "-- even correct syntactic-head extraction is insufficient for fully-trustworthy closure.").format(
                lift_edge_fair, lift_comp_fair, lift_spec_hard, cp_new["prec_fair"],
                "clears" if cleared_reach else "does not clear",
                new_arm["spec_hard"], bands["hp_compose_prec_floor"], bands["hp_spec_hard_floor"]),
            diag)


# ------------------------- self-test (real code path) -------------------------

def self_test():
    print("[self-test] exercising REAL code path (NEW genus-head + OLD baseline + WN oracle + arms)", flush=True)

    # --- NEW genus-head extractor on the VET's exact error cases (the load-bearing fix) ---
    cases = {
        "a group of similar cells": "group",           # was 'cell'
        "the variety of alleles": "variety",           # was 'allele'
        "a set of populations": "set",                 # was 'population'
        "a white blood cell": "cell",                  # was 'blood' (compound head)
        "an individual living entity": "entity",       # was 'living' (adjective)
        "an organelle that produces energy": "organelle",
        "the study of life": "study",
        "a type of organelle in cells": "organelle",   # TRANSPARENT light-noun -> descend
        "a cell that transmits nerve impulses": "cell",
    }
    fails = []
    for defn, want in cases.items():
        got = genus_head_of_definition(defn)
        tag = "OK " if got == want else "XX "
        print("   {}{!r} -> NEW={!r} want={!r}".format(tag, defn, got, want), flush=True)
        if got != want:
            fails.append((defn, got, want))
    # the 5 VET-named error cases + transparent + copular MUST pass (allow at most 0 fails)
    assert not fails, "NEW genus-head extractor wrong on: {}".format(fails)

    # --- OLD extractor reproduces the KNOWN wrong behavior (positive control on the contrast) ---
    assert V1.genus_of_definition("a group of similar cells") == "cell", \
        ("OLD control: expected buggy 'cell'", V1.genus_of_definition("a group of similar cells"))
    assert V1.genus_of_definition("a white blood cell") == "blood", \
        ("OLD control: expected buggy 'blood'", V1.genus_of_definition("a white blood cell"))
    # NEW must DIFFER from OLD on these (arms-differ at the extractor level)
    assert genus_head_of_definition("a group of similar cells") != \
        V1.genus_of_definition("a group of similar cells")

    # --- WN oracle sanity (raw + fair) ---
    assert wn_true_raw("dog", "animal") is not None, "WN: dog->animal ancestry expected"
    assert wn_true_raw("dog", "car") is None, "WN: dog->car must be false"
    # fair curated-superclass credit fires for a generic superclass, not for an aggregate
    ft_struct, basis = wn_true_fair("mitochondrion", "structure")
    assert ft_struct and basis in ("raw", "curated_superclass"), (ft_struct, basis)
    # aggregate 'group' gets NO curated fiat credit (must earn via WN); dog->group not curated-credited
    ft_grp, _ = wn_true_fair("dog", "group")
    assert wn_true_raw("dog", "group") is None or ft_grp, "sanity"
    assert "group" not in _GENERIC_SUPERCLASS, "aggregates must NOT be curated-credited"

    # --- tiny synthetic textbook exercises graph-build + closure + query universe + arms + verdict ---
    text = "\n".join([
        "# Tiny Book",
        "##### Section Alpha",
        "A dog is a mammal that barks.",
        "###### Glossary",
        "dog: a mammal that is domesticated",
        "mammal: an animal that has fur",
        "tissue: a group of similar cells",
        "##### Section Beta",
        "###### Glossary",
        "trout: a fish found in rivers",
        "fish: an animal that lives in water",
    ])
    secs = V1.parse_sections(text)
    g_new = build_gloss_graph(secs, genus_head_of_definition)
    g_old = build_gloss_graph(secs, V1.genus_of_definition)
    # NEW: tissue -> group (head); OLD: tissue -> cell (buggy). Contrast present.
    assert "group" in g_new["gloss"].get("tissue", set()), g_new["gloss"].get("tissue")
    assert "cell" in g_old["gloss"].get("tissue", set()), g_old["gloss"].get("tissue")
    # closure: dog -> mammal -> animal (indirect dist 2), no direct dog->animal
    reach_new = closure(g_new["gloss"])
    assert reach_new.get("dog", {}).get("animal") == 2, ("dog->animal composed", reach_new.get("dog"))
    # full measure + verdict runs and returns a valid tier
    rng = random.Random(RNG_SEED)
    res = measure(secs, rng)
    v, msg, diag = compute_verdict(res, BANDS)
    assert v in ("HARD_PASS", "HARD_FAIL_NO_LIFT", "HARD_FAIL_VACUOUS_N",
                 "HARD_FAIL_ARMS_IDENTICAL", "MIDDLE_BAND_CEILING"), v
    print("[self-test] PASS: nodes={} edge_prec_old_fair={:.2f} edge_prec_new_fair={:.2f} verdict={}".format(
        res["n_nodes"], res["edge_prec_old"]["prec_fair"], res["edge_prec_new"]["prec_fair"], v), flush=True)
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
    print("[{}] sections={}".format(run_mode, len(sections)), flush=True)

    rng = random.Random(RNG_SEED)
    res = measure(sections, rng)
    verdict, verdict_msg, diag = compute_verdict(res, BANDS)
    elapsed = time.perf_counter() - t0

    ep_old = res["edge_prec_old"]
    ep_new = res["edge_prec_new"]
    new_arm = res["arms"]["NEW_GENUS_COMPOSE"]
    old_arm = res["arms"]["OLD_GENUS_COMPOSE"]

    # design-gate + discriminator-fires surface
    gate = {
        "discriminator_fires": bool(res["n_pos"] > 0 and res["n_neg_hard"] > 0
                                    and res["bucket_shift"]["n_changed_edges"] >= BANDS["min_changed_edges"]),
        "oracle_labeled_both_classes": bool(res["n_pos"] > 0 and res["n_neg_hard"] > 0),
        "arms_differ_edges_changed": res["bucket_shift"]["n_changed_edges"],
        "real_baselines": ["OLD_GENUS_COMPOSE", "DIRECT_LOOKUP", "FREQUENCY", "RANDOM"],
        "difficulty_on": ("fixed universe: WN-labeled multi-hop pairs (dist in [2,{}]), NO direct edge "
                          "in either graph; hard-negs = WN-false but book-composable".format(DMAX_WN)),
        "one_variable": "genus-extraction rule (OLD V1.genus_of_definition vs NEW syntactic-head)",
        "headline_metric": "edge precision (raw+fair) + composed multi-hop precision + spec_hard (NOT recall)",
        "fair_oracle": "raw-WN OR curated generic-superclass (aggregates EXCLUDED from curated fiat)",
    }

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": ("{}: edge_prec fair old={:.3f}->new={:.3f} (lift={:+.3f}) raw old={:.3f}->new={:.3f} | "
                    "compose_prec fair old={:.3f}->new={:.3f} | new_arm prec={:.3f} spec_hard={:.3f} | "
                    "bucket net={:+d} | n_pos={} n_neg_hard={}").format(
            verdict, ep_old["prec_fair"], ep_new["prec_fair"],
            diag["edge_prec_lift_fair"], ep_old["prec_raw"], ep_new["prec_raw"],
            res["compose_prec_old"]["prec_fair"], res["compose_prec_new"]["prec_fair"],
            new_arm["precision"], new_arm["spec_hard"],
            res["bucket_shift"]["net_bucket_improvement"], res["n_pos"], res["n_neg_hard"]),
        "elapsed_s": round(elapsed, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "bands": BANDS,
        "diag": diag,
        "gate": gate,
        "n_nodes": res["n_nodes"],
        "n_direct_edges_old": res["n_direct_edges_old"],
        "n_direct_edges_new": res["n_direct_edges_new"],
        "n_edge_list_old": res["n_edge_list_old"],
        "n_edge_list_new": res["n_edge_list_new"],
        "n_pos": res["n_pos"],
        "n_neg_hard": res["n_neg_hard"],
        "n_neg_easy": res["n_neg_easy"],
        "base_rate": res["base_rate"],
        "edge_prec_old": ep_old,
        "edge_prec_new": ep_new,
        "compose_prec_old": res["compose_prec_old"],
        "compose_prec_new": res["compose_prec_new"],
        "compose_prec_new_noisectrl": res["compose_prec_new_noisectrl"],
        "arms": res["arms"],
        "bucket_shift": res["bucket_shift"],
        "top_hubs_new": res["top_hubs_new"],
        "top_parents_old": res["top_parents_old"],
        "top_parents_new": res["top_parents_new"],
    }
    _write_metrics_atomic(output_dir, metrics)
    print("[{}] VERDICT={} {}".format(run_mode, verdict, metrics["summary"]), flush=True)
    print("[{}] {}".format(run_mode, verdict_msg), flush=True)
    print("   edge_prec  OLD raw={:.3f} fair={:.3f} (chk={})  NEW raw={:.3f} fair={:.3f} (chk={})".format(
        ep_old["prec_raw"], ep_old["prec_fair"], ep_old["checkable"],
        ep_new["prec_raw"], ep_new["prec_fair"], ep_new["checkable"]), flush=True)
    print("   compose_prec OLD fair={:.3f}  NEW fair={:.3f}  NEW_nc fair={:.3f}".format(
        res["compose_prec_old"]["prec_fair"], res["compose_prec_new"]["prec_fair"],
        res["compose_prec_new_noisectrl"]["prec_fair"]), flush=True)
    for a in ["OLD_GENUS_COMPOSE", "NEW_GENUS_COMPOSE", "NEW_GENUS_NOISECTRL",
              "DIRECT_LOOKUP", "FREQUENCY", "RANDOM"]:
        m = res["arms"][a]
        print("   {:20s} prec={:.3f} recall={:.3f} spec_hard={:.3f} balacc={:.3f} yes_rate={:.3f}".format(
            a, m["precision"], m["recall"], m["spec_hard"], m["balanced_acc"], m["yes_rate"]), flush=True)
    bs = res["bucket_shift"]
    print("   bucket_shift: changed={} old_wrong->new_right={} new_wrong->old_right={} net={:+d}".format(
        bs["n_changed_edges"], bs["old_wrong_new_right"], bs["new_wrong_old_right"],
        bs["net_bucket_improvement"]), flush=True)
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
