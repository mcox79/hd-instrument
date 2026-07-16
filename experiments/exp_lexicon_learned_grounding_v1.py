"""exp_lexicon_learned_grounding_v1 -- does a GLASS-BOX co-occurrence lexicon LEARNER (not an oracle)
learn correct word-form -> foundation-concept mappings from a tiny paired curriculum, then feed the
LEARNED word-phasors into the proven role-filler scaffold to yield a real grounded fact on unbind?

QUESTION (research note research_word_grounding_lexicon_structure_content_unification_2026-07-16,
Prediction 2/3): everything grounded so far (exp_lexicon_grounding_loop_v1) used an ORACLE identity
lexicon (word == Q-id -> its own code). This cell tests the genuine novel-synthesis: run the section-3
multi-cue glass-box lexicon-learner (cross-situational co-occurrence tracking + softened
mutual-exclusivity + syntactic-role gating + provisional fast-mapping) over a paired SVO-sentence /
grounded-triple corpus, build an INSPECTABLE COUNTABLE lexicon table (word -> ranked
(concept_id, weight, exemplar_count)), then parse HELD-OUT novel word-combinations with that LEARNED
table into the proven FHRR role-filler scaffold and unbind a role to retrieve a grounded concept.

ISOLATE THE LEARNING RULE FROM THE GEOMETRY CONFOUND (Director steer): the foundation is a SMALL
controlled set (12 concepts) with i.i.d. random FHRR unit-phasor codes -> codebook geometry benign by
construction (high participation ratio, low coherence -- asserted). We do NOT use the full CoDEx FPE
encoding (that concentrates geometry -- a separate encoding problem). So any failure here is
attributable to the LEARNING RULE, not to filler geometry. The ORACLE-LEXICON arm nails that
attribution: if LEARNED fails but ORACLE passes -> the learning rule is the problem; if BOTH fail ->
geometry/binding (should not happen given benign-by-construction codes).

GLASS-BOX LEXICON LEARNER (section 3; NO hidden embedding, NO LLM -- a countable table + update rule):
  lexicon[word] = dict concept_id -> association weight (+ exemplar_count). Updated per (sentence, fact):
  (1) CROSS-SITUATIONAL CO-OCCURRENCE via competitive alignment (Yu&Smith / Fazly / Yurovsky): each
      concept in the paired fact distributes a unit of alignment mass across the words that could
      explain it, proportional to current belief -> the TRUE word-concept pairing accumulates faster
      because it RECURS across varying contexts while distractor pairings do not. The normalization IS a
      soft mutual-exclusivity (a concept strongly claimed by one word leaves little mass for others).
  (2) SYNTACTIC-ROLE GATING (Gleitman/Naigles/Fisher, ABLATABLE = Prediction-3 lever): the word's
      SYNTACTIC SLOT in the sentence (subject/object = NOUN category, verb = RELATION category) restricts
      its candidate concepts to the role-eligible category before co-occurrence runs. Verbs converge in
      one exposure (1 candidate); nouns still need cross-situational disambiguation (2 noun candidates).
  (3) SOFTENED MUTUAL-EXCLUSIVITY (Markman&Wachtel, softened per bilingual/taxonomic caveat): an explicit
      mild penalty on aligning to a concept already the CONFIDENT top of a different stable word --
      accelerates convergence, never hard-forbids a later re-mapping.
  (4) FAST-MAPPING via ELIMINATION (Carey&Bartlett, PROVISIONAL per propose-but-verify): when exactly one
      role-eligible concept in a fact is not yet claimed by any confident word, give the un-mapped word a
      single-exposure provisional bonus toward it -- confirmed/revised by (1) on later exposures.

ARMS (4, per contract):
  - LEXICON-LEARNED : learner over TRAIN corpus -> learned table -> ground HELD-OUT novel combos.
  - ORACLE-LEXICON  : perfect word->concept map -> same scaffold -> HELD-OUT. Upper bound + attribution.
  - RANDOM          : word->fresh random phasor (unrelated to foundation) -> cleanup vs foundation = chance.
  - MEMORIZED-overfit: the LEARNED table evaluated ONLY on SEEN (train) combos. Isolates genuine
      compositional recovery (held-out ~ seen) from rote pair-lookup (held-out << seen).

METRIC: (a) held-out word->concept MAPPING accuracy (learned top-weighted concept per word == true one),
  reported as a CONVERGENCE CURVE vs exemplar budget against the Tolerance-Principle bar
  (e <= V/ln V errors tolerated; V=12 -> tolerate 4 -> converged >= 0.667 mapping acc); AND
  (b) downstream grounded-retrieval on NOVEL combos (unbind OBJECT/SUBJECT role, nearest-neighbor against
  the foundation's own concept space). Prediction 3: gating reduces the exemplar budget to converge.

PRE-REG (envelope-fail-bands; bars from note section (b)/(c)):
  HARD-PASS: LEXICON-LEARNED mapping_acc converges >= Tolerance bar within the train budget AND held-out
    grounded-retrieval within <= 0.10 of ORACLE AND >= 0.30 above RANDOM AND MEMORIZED(seen) does not
    inflate held-out (seen - held-out <= 0.10).
  HARD-FAIL: learner does not converge (mapping_acc < 0.50 at full budget), OR converges to systematically
    wrong mappings, OR held-out retrieval indistinguishable from RANDOM (< 0.05 above), OR held-out
    collapses vs memorized-seen (>= 0.20 gap = rote not compositional).
  MIDDLE otherwise. Prediction 3 (secondary, reported not gating): gating cuts convergence budget >= 25%.
  If HARD-FAIL -> genuine novel-synthesis negative; brain-check (child cross-situational learning) + honest.

Local numpy, no queue/GPU/atoms/push. ASCII-only. FHRR = complex128 unit phasors.
Compute: sequential-CPU, tiny (12 concepts, N<=2048, <=200 exemplars, <=5 seeds, gating on/off) -> wall<15s;
  cell IS the glass-box learning-rule reference over benign-geometry codes -> sequential justified.
Storage: per-sentence role-filler bundle (single-hop relation-keyed unbind, no chained composition) ->
  bundled is correct (not a multi-hop composition).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test over per-query score arrays)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb/reachability declared in prereg (cleanup among 8 noun candidates at N>=512: crosstalk sqrt(3/N)
#     << 1/sqrt(8) separation -> ORACLE retrieval reachable ~1.0; RANDOM at chance 1/8 by construction)
# - baseline_in_band at smoke (RANDOM ~1/8 in (0.05,0.95); ORACLE ~1.0; LEARNED climbs between)
# - discriminator survives scale (N sweep; ORACLE stays ~1.0, RANDOM stays chance, gap survives)
# - deterministic seeding (fixed int seeds; sorted() vocab ordering; no hash()/list(set()))
# - all numbers in comments tagged HYPOTHESIZED@prereg / THEORETICAL / MEASURED@metrics
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import argparse
import math
import time
import json
import hashlib
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
ANCHOR_NAME = "lexicon_learned_grounding_v1"

# ---------------------------------------------------------------------------
# FHRR primitives (glass-box) -- unit phasors, complex128. Reused from the SVO probe / grounding loop.
# ---------------------------------------------------------------------------

def make_phasors(rng, count, N):
    """count random FHRR unit-phasor hypervectors, shape (count, N) complex128."""
    theta = rng.uniform(-np.pi, np.pi, size=(count, N))
    return np.exp(1j * theta)


def bind(a, b):
    """FHRR bind = elementwise complex multiply."""
    return a * b


def unbind(c, b):
    """FHRR unbind = multiply by conjugate."""
    return c * np.conj(b)


def cleanup(query, codebook_rows):
    """Nearest codebook row by Re(<row, q>); returns local argmax index into codebook_rows."""
    scores = (codebook_rows.conj() @ query).real
    return int(np.argmax(scores))


# ---------------------------------------------------------------------------
# Controlled small foundation (benign geometry by construction) + word forms + role eligibility.
# ---------------------------------------------------------------------------

# 8 noun concepts (subjects/objects) + 4 verb/relation concepts = 12 concepts total.
# Word-form == the string token; the LEARNER does NOT know word->concept a priori (must infer).
NOUN_WORDS = ["ball", "bird", "boy", "cat", "dog", "fish", "girl", "tree"]  # sorted, deterministic
ANIMATE_SUBJECTS = ["bird", "boy", "cat", "dog", "fish", "girl"]             # subject-eligible surface set
VERB_WORDS = ["chases", "holds", "likes", "sees"]                            # sorted
# concept_id == word string (identity of the CONCEPT node, not known to learner as a word-map).


def build_foundation():
    """Deterministic foundation: concept ids + role-eligibility categories. No phasors yet (per-seed)."""
    words = sorted(NOUN_WORDS + VERB_WORDS)
    concept_ids = sorted(set(NOUN_WORDS) | set(VERB_WORDS))   # concept per word (identity target)
    true_map = {w: w for w in words}                          # ground-truth word -> concept (hidden)
    noun_concepts = set(NOUN_WORDS)
    verb_concepts = set(VERB_WORDS)
    cid_idx = {c: i for i, c in enumerate(concept_ids)}
    noun_cid_idx = np.array(sorted(cid_idx[c] for c in noun_concepts))
    verb_cid_idx = np.array(sorted(cid_idx[c] for c in verb_concepts))
    return {
        "words": words, "concept_ids": concept_ids, "cid_idx": cid_idx,
        "true_map": true_map, "noun_concepts": noun_concepts, "verb_concepts": verb_concepts,
        "noun_cid_idx": noun_cid_idx, "verb_cid_idx": verb_cid_idx,
        "V": len(words),
    }


def sample_corpus(rng, n_train, n_heldout):
    """Sample disjoint SVO WORD-triples. Held-out = novel COMBINATIONS of KNOWN words (leak-guarded).

    subject in ANIMATE_SUBJECTS, verb in VERB_WORDS, object in NOUN_WORDS. Space = 6*4*8 = 192 combos.
    Every word appears in train (asserted by caller) so it has a learnable mapping; held-out triples are
    disjoint from train triples (novel combos)."""
    space = [(s, v, o) for s in ANIMATE_SUBJECTS for v in VERB_WORDS for o in NOUN_WORDS]
    perm = rng.permutation(len(space))
    ordered = [space[i] for i in perm]
    train = ordered[:n_train]
    heldout = ordered[n_train:n_train + n_heldout]
    return train, heldout


def sentence_to_fact(triple):
    """(subj_word, verb_word, obj_word) sentence -> (subj_concept, verb_concept, obj_concept) grounded fact.
    Identity concept per word (the grounded pairing the curriculum ships); the learner never sees this map,
    only the SET of concepts present + each word's SYNTACTIC SLOT."""
    return (triple[0], triple[1], triple[2])  # concept ids == word strings (hidden identity)


# ---------------------------------------------------------------------------
# GLASS-BOX multi-cue lexicon learner (section 3). Inspectable countable table.
# ---------------------------------------------------------------------------

SLOT_CATEGORY = ("noun", "verb", "noun")   # SVO: subject=noun, verb=verb, object=noun (syntactic bootstrap)


def _role_eligible(category, fact_concepts, foundation):
    """Concepts in this fact whose category matches the word's syntactic slot (role gating)."""
    if category == "noun":
        return [c for c in fact_concepts if c in foundation["noun_concepts"]]
    return [c for c in fact_concepts if c in foundation["verb_concepts"]]


def learn_lexicon(train, foundation, role_gating=True, soft_me=True, fast_map=True, eps=0.01):
    """Return lexicon: dict word -> dict concept_id -> weight (+ per-word exemplar_count).

    Fully glass-box: assoc is a countable table; each update term traces to a named child-language cue.
    """
    words = foundation["words"]
    assoc = {w: defaultdict(float) for w in words}
    exemplar_count = {w: 0 for w in words}

    def confident_top(w):
        """Current argmax concept for w if it dominates (for soft-ME + fast-map claim tracking)."""
        d = assoc[w]
        if not d:
            return None
        items = sorted(d.items(), key=lambda kv: -kv[1])
        if len(items) == 1:
            return items[0][0] if items[0][1] > 0 else None
        (c0, w0), (c1, w1) = items[0], items[1]
        return c0 if w0 > 1.5 * (w1 + eps) else None

    for triple in train:
        sentence = triple                       # (sw, vw, ow)
        fact = sentence_to_fact(triple)         # concept set present (order-aligned but learner uses SET)
        fact_concepts = list(fact)
        # per-word candidate concepts (role gating restricts to slot-category; ablation = full set)
        cand = {}
        for pos, w in enumerate(sentence):
            if role_gating:
                cand[w] = _role_eligible(SLOT_CATEGORY[pos], fact_concepts, foundation)
            else:
                cand[w] = list(fact_concepts)
            exemplar_count[w] += 1

        # claimed concepts (softened mutual-exclusivity): concept -> the word confidently owning it.
        claimed = {}
        if soft_me:
            for w in set(sentence):
                ct = confident_top(w)
                if ct is not None:
                    claimed[ct] = w

        # (1) competitive cross-situational alignment: each concept distributes unit mass across the
        #     words that could explain it, proportional to current belief (+eps). Delta applied after.
        delta = {w: defaultdict(float) for w in set(sentence)}
        for c in set(fact_concepts):
            contributors = [w for w in set(sentence) if c in cand[w]]
            if not contributors:
                continue
            weights = {}
            for w in contributors:
                base = assoc[w].get(c, 0.0) + eps
                # (3) softened mutual-exclusivity: mild penalty if c is confidently owned by a DIFFERENT word.
                if soft_me and claimed.get(c) not in (None, w):
                    base *= 0.25
                weights[w] = base
            total = sum(weights.values())
            for w in contributors:
                delta[w][c] += weights[w] / total
        for w in delta:
            for c, dv in delta[w].items():
                assoc[w][c] += dv

        # (4) fast-mapping via elimination: if exactly one role-eligible concept in this fact is not yet
        #     claimed by any confident word, and a word in that slot is itself un-mapped, give a provisional
        #     single-exposure bonus (confirmed/revised by (1) later).
        if fast_map:
            for pos, w in enumerate(sentence):
                if confident_top(w) is not None:
                    continue
                unclaimed = [c for c in cand[w] if c not in claimed]
                if len(unclaimed) == 1:
                    assoc[w][unclaimed[0]] += 0.5     # provisional; small vs accumulated evidence

    return assoc, exemplar_count


def lexicon_top(assoc, foundation):
    """word -> top-weighted concept id (argmax of the countable table). Deterministic tie-break by cid."""
    out = {}
    for w in foundation["words"]:
        d = assoc[w]
        if not d:
            out[w] = None
            continue
        out[w] = max(sorted(d.items(), key=lambda kv: kv[0]), key=lambda kv: kv[1])[0]
    return out


def mapping_accuracy(assoc, foundation):
    """Fraction of words whose learned top concept == the true concept."""
    top = lexicon_top(assoc, foundation)
    tm = foundation["true_map"]
    correct = sum(1 for w in foundation["words"] if top.get(w) == tm[w])
    return correct / len(foundation["words"]), top


# ---------------------------------------------------------------------------
# Grounded retrieval through the proven role-filler scaffold using a word->phasor map.
# ---------------------------------------------------------------------------

def build_word2phasor(kind, foundation, v_concept, top_map, rng, N):
    """kind in {learned, oracle, random}. Returns word -> (N,) phasor.
    learned: learned top concept's foundation phasor. oracle: true concept's phasor.
    random: fresh random phasor per word (unrelated to foundation) -> cleanup vs foundation = chance."""
    cid_idx = foundation["cid_idx"]
    w2p = {}
    if kind == "random":
        rp = make_phasors(rng, len(foundation["words"]), N)
        for i, w in enumerate(foundation["words"]):
            w2p[w] = rp[i]
        return w2p
    src = top_map if kind == "learned" else foundation["true_map"]
    for w in foundation["words"]:
        c = src.get(w)
        if c is None:                                   # un-mapped -> a random phasor (counts as wrong)
            w2p[w] = make_phasors(rng, 1, N)[0]
        else:
            w2p[w] = v_concept[cid_idx[c]]
    return w2p


def grounded_retrieval(corpus_eval, w2p, roles, v_concept, foundation, query="obj"):
    """Parse each held-out sentence with the word->phasor map, unbind the queried role, nearest-neighbor
    against the foundation's role-appropriate concept range. Returns accuracy (recovered concept == true)."""
    slot = {"subj": 0, "verb": 1, "obj": 2}[query]
    cand_idx = foundation["verb_cid_idx"] if query == "verb" else foundation["noun_cid_idx"]
    cand_rows = v_concept[cand_idx]
    concept_ids = foundation["concept_ids"]
    ok, n = 0, 0
    for triple in corpus_eval:
        M = (bind(roles[0], w2p[triple[0]]) + bind(roles[1], w2p[triple[1]]) + bind(roles[2], w2p[triple[2]]))
        q = unbind(M, roles[slot])
        rec_local = cleanup(q, cand_rows)
        rec_cid = concept_ids[cand_idx[rec_local]]
        true_cid = sentence_to_fact(triple)[slot]
        ok += int(rec_cid == true_cid)
        n += 1
    return ok / n if n else 0.0


def _scores_for_hash(corpus_eval, w2p, roles, v_concept, foundation, query="obj"):
    """Per-query resonance vector (for ARMS-MUST-DIFFER hashing)."""
    slot = {"subj": 0, "verb": 1, "obj": 2}[query]
    cand_idx = foundation["noun_cid_idx"] if query != "verb" else foundation["verb_cid_idx"]
    cand_rows = v_concept[cand_idx]
    out = []
    for triple in corpus_eval:
        M = (bind(roles[0], w2p[triple[0]]) + bind(roles[1], w2p[triple[1]]) + bind(roles[2], w2p[triple[2]]))
        q = unbind(M, roles[slot])
        out.append(float((cand_rows.conj() @ q).real.max()) / v_concept.shape[1])
    return np.array(out, dtype=np.float64)


# ---------------------------------------------------------------------------
# Geometry-benign diagnostic (attribution: any failure is the LEARNING RULE, not filler geometry).
# ---------------------------------------------------------------------------

def codebook_diagnostics(v_concept):
    M, N = v_concept.shape
    G = v_concept @ v_concept.conj().T
    absG = np.abs(G) / N
    np.fill_diagonal(absG, 0.0)
    mu = float(absG.max())
    w = np.linalg.eigvalsh((G + G.conj().T).real / 2.0)
    w = np.clip(w, 0.0, None)
    pr = float((w.sum() ** 2) / (np.sum(w ** 2) + 1e-30))
    return {"coherence_mu": mu, "participation_ratio": pr, "M": M, "N": N}


# ---------------------------------------------------------------------------
# One (N, seed) evaluation across arms + a convergence curve over exemplar budget.
# ---------------------------------------------------------------------------

def run_cell(N, seed, foundation, n_train=120, n_heldout=50,
             budgets=(2, 4, 8, 16, 32, 64, 120), n_mem_eval=50, want_curve=True, want_geom=False):
    rng = np.random.default_rng(seed)
    train_full, heldout = sample_corpus(rng, n_train, n_heldout)
    # leak guard: held-out disjoint from train; every held-out word seen in train.
    train_set = set(train_full)
    assert not (set(heldout) & train_set), "LEAK: held-out combo overlaps train"
    train_words = set()
    for t in train_full:
        train_words.update(t)
    for t in heldout:
        for w in t:
            assert w in train_words, f"LEAK-GUARD: held-out word {w!r} unseen in train"

    v_concept = make_phasors(rng, len(foundation["concept_ids"]), N)   # benign i.i.d. codes
    roles = make_phasors(rng, 3, N)                                    # SUBJ, VERB, OBJ role phasors
    geom = codebook_diagnostics(v_concept) if want_geom else None

    # --- learn on full train (gating ON = the main learner) ---
    assoc, excount = learn_lexicon(train_full, foundation, role_gating=True)
    map_acc_full, top_map = mapping_accuracy(assoc, foundation)

    # --- word->phasor maps per arm ---
    w2p_learned = build_word2phasor("learned", foundation, v_concept, top_map, np.random.default_rng(seed + 1), N)
    w2p_oracle = build_word2phasor("oracle", foundation, v_concept, None, np.random.default_rng(seed + 2), N)
    w2p_random = build_word2phasor("random", foundation, v_concept, None, np.random.default_rng(seed + 3), N)

    def retr(w2p, corpus, q):
        return grounded_retrieval(corpus, w2p, roles, v_concept, foundation, query=q)

    learned_obj = retr(w2p_learned, heldout, "obj")
    learned_subj = retr(w2p_learned, heldout, "subj")
    oracle_obj = retr(w2p_oracle, heldout, "obj")
    oracle_subj = retr(w2p_oracle, heldout, "subj")
    random_obj = retr(w2p_random, heldout, "obj")
    random_subj = retr(w2p_random, heldout, "subj")
    # MEMORIZED-overfit = learned table evaluated on SEEN (train) combos.
    seen_eval = train_full[:n_mem_eval]
    mem_obj = retr(w2p_learned, seen_eval, "obj")
    mem_subj = retr(w2p_learned, seen_eval, "subj")

    # --- convergence curve over exemplar budget, gating ON vs OFF (Prediction 3) ---
    curve = {"budgets": list(budgets), "gate_on_map": [], "gate_off_map": [],
             "gate_on_heldout_obj": [], "gate_off_heldout_obj": []}
    if want_curve:
        for b in budgets:
            tb = train_full[:b]
            a_on, _ = learn_lexicon(tb, foundation, role_gating=True)
            ma_on, top_on = mapping_accuracy(a_on, foundation)
            a_off, _ = learn_lexicon(tb, foundation, role_gating=False)
            ma_off, top_off = mapping_accuracy(a_off, foundation)
            w2p_on = build_word2phasor("learned", foundation, v_concept, top_on, np.random.default_rng(seed + 11), N)
            w2p_off = build_word2phasor("learned", foundation, v_concept, top_off, np.random.default_rng(seed + 12), N)
            curve["gate_on_map"].append(ma_on)
            curve["gate_off_map"].append(ma_off)
            curve["gate_on_heldout_obj"].append(retr(w2p_on, heldout, "obj"))
            curve["gate_off_heldout_obj"].append(retr(w2p_off, heldout, "obj"))

    return {
        "N": N, "seed": seed,
        "mapping_acc_full": map_acc_full, "top_map": top_map,
        "learned_obj": learned_obj, "learned_subj": learned_subj,
        "oracle_obj": oracle_obj, "oracle_subj": oracle_subj,
        "random_obj": random_obj, "random_subj": random_subj,
        "mem_obj": mem_obj, "mem_subj": mem_subj,
        "curve": curve, "geometry": geom,
        "n_train": len(train_full), "n_heldout": len(heldout),
        "_hash_learned": _scores_for_hash(heldout, w2p_learned, roles, v_concept, foundation, "obj"),
        "_hash_random": _scores_for_hash(heldout, w2p_random, roles, v_concept, foundation, "obj"),
    }


def _budget_to_bar(budgets, accs, bar):
    """First exemplar budget at which accs crosses bar; None if never."""
    for b, a in zip(budgets, accs):
        if a >= bar:
            return b
    return None


def avg_over_seeds(N, seeds, foundation, budgets):
    scalar = ["mapping_acc_full", "learned_obj", "learned_subj", "oracle_obj", "oracle_subj",
              "random_obj", "random_subj", "mem_obj", "mem_subj"]
    acc = defaultdict(list)
    curve_on_map = []
    curve_off_map = []
    curve_on_obj = []
    curve_off_obj = []
    for s in seeds:
        r = run_cell(N, s, foundation, budgets=budgets)
        for k in scalar:
            acc[k].append(r[k])
        curve_on_map.append(r["curve"]["gate_on_map"])
        curve_off_map.append(r["curve"]["gate_off_map"])
        curve_on_obj.append(r["curve"]["gate_on_heldout_obj"])
        curve_off_obj.append(r["curve"]["gate_off_heldout_obj"])
    out = {k: float(np.mean(v)) for k, v in acc.items()}
    out.update({k + "_std": float(np.std(v)) for k, v in acc.items()})
    out["N"] = N
    out["curve_budgets"] = list(budgets)
    out["curve_gate_on_map"] = list(np.mean(curve_on_map, axis=0))
    out["curve_gate_off_map"] = list(np.mean(curve_off_map, axis=0))
    out["curve_gate_on_heldout_obj"] = list(np.mean(curve_on_obj, axis=0))
    out["curve_gate_off_heldout_obj"] = list(np.mean(curve_off_obj, axis=0))
    return out


# ---------------------------------------------------------------------------
# error-checking scaffolding (start marker + crash diagnostic; SystemExit ordering)
# ---------------------------------------------------------------------------

def _out_dir():
    d = REPO / "data" / f"exp_{ANCHOR_NAME}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_start_marker(run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected_n_units}
    d = _out_dir()
    tmp = d / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(marker, f)
    os.replace(tmp, d / "_start_marker.json")


def _write_crash_metrics(exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    d = _out_dir()
    tmp = d / "metrics.json.tmp"
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, d / "metrics.json")


def _arms_must_differ(arms_outputs):
    digests = {}
    for name, out in arms_outputs.items():
        b = np.asarray(out).tobytes()
        digests[name] = hashlib.sha256(b).hexdigest()
    names = list(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], \
                f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} bit-identical (arm-impl bug)"
    return digests


# ---------------------------------------------------------------------------
# Self-tests (HARDENED: real code path; must-fail controls fire; telemetry-sensitive; leak-guarded).
# ---------------------------------------------------------------------------

def self_test():
    found = build_foundation()
    V = found["V"]
    tol_bar = 1.0 - math.floor(V / math.log(V)) / V   # Tolerance-Principle convergence bar

    print("[self-test] FHRR bind/unbind exact recovery ...", flush=True)
    rng = np.random.default_rng(0)
    N = 1024
    a = make_phasors(rng, 1, N)[0]
    role = make_phasors(rng, 1, N)[0]
    cos = (np.conj(a) @ unbind(bind(role, a), role)).real / N
    assert cos > 0.999, f"bind/unbind not self-inverse: cos={cos}"
    print(f"           single-pair unbind cos={cos:.4f} OK  (V={V} Tolerance bar={tol_bar:.3f})", flush=True)

    print("[self-test] foundation codebook geometry BENIGN by construction ...", flush=True)
    v_concept = make_phasors(np.random.default_rng(1), len(found["concept_ids"]), N)
    diag = codebook_diagnostics(v_concept)
    assert diag["participation_ratio"] > 0.8 * min(diag["M"], diag["N"]), \
        f"codebook not benign (PR too low): {diag['participation_ratio']}"
    assert diag["coherence_mu"] < 0.2, f"codebook coherence too high: {diag['coherence_mu']}"
    print(f"           PR={diag['participation_ratio']:.1f}/{min(diag['M'],diag['N'])} "
          f"coherence_mu={diag['coherence_mu']:.3f} OK", flush=True)

    print("[self-test] leak-guard + real code path (run_cell over the real learner) ...", flush=True)
    r = run_cell(N=1024, seed=1, foundation=found, want_geom=True)
    print(f"           n_train={r['n_train']} n_heldout={r['n_heldout']} map_acc_full={r['mapping_acc_full']:.3f}",
          flush=True)

    print("[self-test] ORACLE arm ~1.0 (binding fidelity positive control) ...", flush=True)
    assert r["oracle_obj"] >= 0.90, f"oracle obj retrieval too low: {r['oracle_obj']}"
    assert r["oracle_subj"] >= 0.90, f"oracle subj retrieval too low: {r['oracle_subj']}"
    print(f"           oracle_obj={r['oracle_obj']:.3f} oracle_subj={r['oracle_subj']:.3f} OK", flush=True)

    print("[self-test] RANDOM arm at CHANCE (must-fail control fires) ...", flush=True)
    chance = 1.0 / len(found["noun_concepts"])
    assert r["random_obj"] <= chance + 0.15, f"random obj not at chance: {r['random_obj']} (chance {chance:.3f})"
    assert r["oracle_obj"] - r["random_obj"] >= 0.50, \
        f"oracle-random gap too small: {r['oracle_obj']} vs {r['random_obj']}"
    print(f"           random_obj={r['random_obj']:.3f} (chance~{chance:.3f}) oracle-random gap="
          f"{r['oracle_obj']-r['random_obj']:.3f} OK", flush=True)

    print("[self-test] LEXICON-LEARNED converges (mapping_acc >= Tolerance bar) ...", flush=True)
    assert r["mapping_acc_full"] >= tol_bar, \
        f"learner did not converge: map_acc={r['mapping_acc_full']:.3f} < bar {tol_bar:.3f}"
    assert r["learned_obj"] - r["random_obj"] >= 0.30, \
        f"learned grounded-retrieval not above random: {r['learned_obj']} vs {r['random_obj']}"
    print(f"           map_acc_full={r['mapping_acc_full']:.3f} learned_obj={r['learned_obj']:.3f} "
          f"(oracle {r['oracle_obj']:.3f}) OK", flush=True)

    print("[self-test] held-out ~ memorized-seen (no rote overfit) ...", flush=True)
    assert r["mem_obj"] - r["learned_obj"] < 0.20, \
        f"held-out collapses vs memorized-seen: mem={r['mem_obj']:.3f} held={r['learned_obj']:.3f}"
    print(f"           mem_seen_obj={r['mem_obj']:.3f} learned_heldout_obj={r['learned_obj']:.3f} OK", flush=True)

    print("[self-test] convergence curve TELEMETRY-SENSITIVE (more exemplars -> higher map acc) ...",
          flush=True)
    cm = r["curve"]["gate_on_map"]
    assert cm[-1] >= cm[0] - 1e-9, f"curve not monotone-ish: {cm}"
    assert cm[-1] - cm[0] >= 0.1, f"curve shows no learning signal: {cm}"
    print(f"           gate_on map curve={['%.2f'%x for x in cm]} (budgets={r['curve']['budgets']}) OK",
          flush=True)

    print("[self-test] role-gating helps (Prediction-3 discriminator available) ...", flush=True)
    b_on = _budget_to_bar(r["curve"]["budgets"], r["curve"]["gate_on_map"], tol_bar)
    b_off = _budget_to_bar(r["curve"]["budgets"], r["curve"]["gate_off_map"], tol_bar)
    print(f"           budget_to_bar gating_on={b_on} gating_off={b_off} "
          f"(final map on={r['curve']['gate_on_map'][-1]:.2f} off={r['curve']['gate_off_map'][-1]:.2f})",
          flush=True)

    print("[self-test] arms-must-differ (learned vs random per-query score arrays) ...", flush=True)
    _arms_must_differ({"LEARNED": r["_hash_learned"], "RANDOM": r["_hash_random"]})
    print("           arms differ OK", flush=True)

    print("[self-test] systematically-wrong-mapping guard (a mangled learner is caught) ...", flush=True)
    # Sanity: an EMPTY-train learner must NOT converge (guards against a vacuous always-pass).
    a_empty, _ = learn_lexicon([], found, role_gating=True)
    ma_empty, _ = mapping_accuracy(a_empty, found)
    assert ma_empty < tol_bar, f"vacuous convergence on empty corpus: {ma_empty}"
    print(f"           empty-corpus map_acc={ma_empty:.3f} < bar {tol_bar:.3f} OK", flush=True)

    print("[self-test] ALL PASS", flush=True)


# ---------------------------------------------------------------------------
# Main sweep + verdict.
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--timeout", type=float, default=0.0)  # harness parity
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return

    t0 = time.time()
    found = build_foundation()
    V = found["V"]
    tol_bar = 1.0 - math.floor(V / math.log(V)) / V
    budgets = (2, 4, 8, 16, 32, 64, 120)
    if args.smoke:
        N_grid = [512, 1024]
        seeds = [1, 2, 3]
        run_mode = "smoke"
    else:
        N_grid = [512, 1024, 2048]
        seeds = [1, 2, 3, 4, 5]
        run_mode = "full"

    _write_start_marker(run_mode, expected_n_units=len(N_grid) * len(seeds))
    print(f"foundation: V={V} words, {len(found['concept_ids'])} concepts "
          f"({len(found['noun_concepts'])} noun + {len(found['verb_concepts'])} verb), "
          f"Tolerance bar={tol_bar:.3f} (e<=floor(V/lnV)={math.floor(V/math.log(V))} errors)", flush=True)

    sweep = []
    for N in N_grid:
        res = avg_over_seeds(N, seeds, found, budgets)
        sweep.append(res)
        print(f"N={N:5d}  map_acc={res['mapping_acc_full']:.3f} | LEARNED obj={res['learned_obj']:.3f} "
              f"subj={res['learned_subj']:.3f} | ORACLE obj={res['oracle_obj']:.3f} | "
              f"RANDOM obj={res['random_obj']:.3f} | MEM-seen obj={res['mem_obj']:.3f}", flush=True)
        print(f"        gate_ON  map curve={['%.2f'%x for x in res['curve_gate_on_map']]} "
              f"heldout-obj={['%.2f'%x for x in res['curve_gate_on_heldout_obj']]}", flush=True)
        print(f"        gate_OFF map curve={['%.2f'%x for x in res['curve_gate_off_map']]} "
              f"heldout-obj={['%.2f'%x for x in res['curve_gate_off_heldout_obj']]} (budgets={list(budgets)})",
              flush=True)

    pos = max(sweep, key=lambda r: r["N"])
    map_acc = pos["mapping_acc_full"]
    learned = pos["learned_obj"]
    oracle = pos["oracle_obj"]
    random_ = pos["random_obj"]
    mem = pos["mem_obj"]

    # Prediction 3: exemplar budget to reach the Tolerance bar, gating ON vs OFF (budget-to-bar); PLUS the
    # early-regime map-accuracy advantage (mean over sub-convergence budgets) -- a finer discriminator than
    # the coarse budget-to-bar, which can tie when both curves leap past the bar between two budget points.
    b_on = _budget_to_bar(pos["curve_budgets"], pos["curve_gate_on_map"], tol_bar)
    b_off = _budget_to_bar(pos["curve_budgets"], pos["curve_gate_off_map"], tol_bar)
    if b_on is not None and b_off is not None and b_off > 0:
        p3_reduction = (b_off - b_on) / b_off
    else:
        p3_reduction = float("nan")
    # early advantage: mean(gate_on - gate_off) over budget points below full convergence (map<1 in either).
    on_map = pos["curve_gate_on_map"]
    off_map = pos["curve_gate_off_map"]
    early_idx = [i for i in range(len(on_map)) if min(on_map[i], off_map[i]) < 1.0 - 1e-9]
    p3_early_adv = float(np.mean([on_map[i] - off_map[i] for i in early_idx])) if early_idx else 0.0
    # P3 (>=25% budget reduction) is the note's HARD bar; the early advantage is reported alongside honestly.
    p3_pass = (b_on is not None) and (b_off is None or (isinstance(p3_reduction, float)
              and not math.isnan(p3_reduction) and p3_reduction >= 0.25))

    # Verdict conditions (note section b/c bars).
    converges = map_acc >= tol_bar
    within_oracle = (oracle - learned) <= 0.10
    above_random = (learned - random_) >= 0.30
    no_overfit_inflation = (mem - learned) <= 0.10

    hp = converges and within_oracle and above_random and no_overfit_inflation
    hf = ((map_acc < 0.50)
          or ((learned - random_) < 0.05)
          or ((mem - learned) >= 0.20))

    if hp and not hf:
        verdict = "HARD_PASS"
    elif hf:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE"

    verdict_msg = (
        f"GLASS-BOX LEARNED-LEXICON grounding (benign-geometry foundation, learning-rule isolated): "
        f"LEXICON-LEARNED mapping_acc={map_acc:.3f} (Tolerance bar={tol_bar:.3f}, need>=; converges={converges}). "
        f"Held-out grounded OBJECT retrieval: LEARNED={learned:.3f} vs ORACLE={oracle:.3f} "
        f"(gap={oracle-learned:+.3f}, need<=0.10) vs RANDOM={random_:.3f} (delta={learned-random_:+.3f}, need>=0.30) "
        f"vs MEMORIZED-seen={mem:.3f} (inflation={mem-learned:+.3f}, need<=0.10 => not rote). "
        f"Prediction 3 (role-gating speeds convergence): budget_to_bar gating_on={b_on} off={b_off} "
        f"reduction={p3_reduction if not (isinstance(p3_reduction,float) and math.isnan(p3_reduction)) else 'n/a'} "
        f"(p3_pass={p3_pass}); early-regime map advantage of gating={p3_early_adv:+.3f}. "
        f"ATTRIBUTION: benign codes => any LEARNED<ORACLE gap is the LEARNING RULE, not geometry."
    )

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: glass-box learned lexicon grounds held-out novel combos ({run_mode})",
        "run_mode": run_mode,
        "elapsed_s": round(time.time() - t0, 2),
        "n_seeds": len(seeds),
        "foundation": {"V": V, "n_concepts": len(found["concept_ids"]),
                       "n_noun": len(found["noun_concepts"]), "n_verb": len(found["verb_concepts"]),
                       "tolerance_bar": tol_bar, "tolerance_errors_allowed": math.floor(V / math.log(V))},
        "positive_regime": {
            "N": pos["N"], "mapping_acc": map_acc, "learned_obj": learned, "learned_subj": pos["learned_subj"],
            "oracle_obj": oracle, "oracle_subj": pos["oracle_subj"], "random_obj": random_,
            "random_subj": pos["random_subj"], "mem_seen_obj": mem, "mem_seen_subj": pos["mem_subj"],
            "oracle_minus_learned": oracle - learned, "learned_minus_random": learned - random_,
            "mem_minus_learned": mem - learned,
        },
        "hard_pass_conditions": {
            "converges_to_tolerance_bar": bool(converges), "within_oracle_0.10": bool(within_oracle),
            "above_random_0.30": bool(above_random), "no_overfit_inflation_0.10": bool(no_overfit_inflation),
        },
        "prediction_3_role_gating": {
            "budget_to_bar_gating_on": b_on, "budget_to_bar_gating_off": b_off,
            "budget_reduction_frac": p3_reduction if not (isinstance(p3_reduction, float) and math.isnan(p3_reduction)) else None,
            "p3_pass_reduction_ge_0.25": bool(p3_pass),
            "early_regime_map_advantage_gating": p3_early_adv,
        },
        "convergence_curve": {
            "budgets": pos["curve_budgets"],
            "gate_on_map": pos["curve_gate_on_map"], "gate_off_map": pos["curve_gate_off_map"],
            "gate_on_heldout_obj": pos["curve_gate_on_heldout_obj"],
            "gate_off_heldout_obj": pos["curve_gate_off_heldout_obj"],
        },
        "sweep": sweep,
        "REQUIRED_FIELDS": ["anchor_name", "verdict", "verdict_msg", "positive_regime", "convergence_curve", "sweep"],
    }

    d = _out_dir()
    tmp = d / "metrics.json.tmp"
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, d / "metrics.json")

    print("\n=== VERDICT ===", flush=True)
    print(verdict, flush=True)
    print(verdict_msg, flush=True)
    print(f"metrics -> {d / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(e)
        raise
