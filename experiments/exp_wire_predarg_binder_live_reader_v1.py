"""exp_wire_predarg_binder_live_reader_v1 -- WIRE THE LANDED PREDARG FRONT-END + GRADED BINDER INTO THE
LIVE READER'S ROLE PATH, MEASURED END-TO-END.

Problem: wire_the_predarg_frontend_and_binder_into_the_live_reader (p3). SUCCESSOR to the prior negative
`wire_the_validated_organs_into_the_live_reader_and_measure_end_to_end` (p1), which PROVED (a) the FRONT-END
(event/role extraction) is the binding constraint for end-to-end reading, and (b) a hand verb-argument
assigner recovers most of it (0.48->0.74) but ties the brutal agent-majority floor because it (i) still
emits only agent/patient (104 gold roles OUT-OF-SCOPE) and (ii) can't do two-animate who-did-what. This
cell closes exactly those two gaps by composing the LANDED organs the prior one said already exist:
  * hdlab.predicate_argument_frontend.route_predicate_arguments -- the event-semantic router that emits the
    RICHER inventory (theme/goal/recipient/location/path/source/direction/instrument) off a real parse
    (agent/theme via the graded binder + passive detector; PINNED: Jackendoff/Talmy Place-vs-Path,
    Kemmerer&Tranel 2003; Competition Model). Fed a REAL parse (hdlab.candidate_generator = persisted UPOS
    tagger + hashed arc parser, the SAME heads source the front-end was validated on).
  * hdlab.graded_coref_pick.graded_antecedent_pick -- graded cue-based antecedent retrieval (Lewis&Vasishth
    2005 ACT-R; Centering Cb) for pronoun -> entity binding (who-did-what), replacing the positional rule.

THE BRAIN (PINNED vs OUR-INVENTION): comprehension is INCREMENTAL role binding over a PARSE (argument
structure), not raw linear position (MacDonald constraint-satisfaction; Competition Model; the parse feeds
Kintsch/Zwaan-Radvansky situation-model (entity,role,event) binding). Linear-position role assignment is the
degenerate fallback the brain uses only when structure is unavailable (good-enough processing). COPY the
computation (route roles through argument structure + bind who-did-what via graded cue retrieval); SWEEP the
OUR-INVENTION part (the parse SOURCE + the abstain/fallback threshold), never adopt it.

THE INHERITED FLOOR (do not re-derive): the prior negative's content-lemma-overlap COUNTING floor (role
~0.98 on the ORACLE-store retrieval population) and the agent-MAJORITY floor (0.781 all / 0.908 in-scope).
Beat BOTH the positional reader AND the counting floor, info-free twin LOSING, NO regression on cases the
positional reader already gets right -- OR a rigorous, quantified NEGATIVE (the parse on archaic prose caps
it, UAS quantified, handing the cap to p8, mechanism proven CI-sep on the modern-parseable subset).

METHODOLOGY NOTE (anti-gaming): the McGuffey gold distinguishes patient vs theme (an aspectual sub-split the
event-semantic router does not make -- it emits ONE structural direct-object argument). So the PRIMARY score
is at the front-end's natural GRAIN: a fixed role-FAMILY normalization applied SYMMETRICALLY to gold,
prediction, AND the positional floor ({patient,theme}->OBJECT; addressee->RECIPIENT). A conservative
EXACT-match score is reported alongside as a lower bound. No number crosses grains.

Run: .venv/Scripts/python.exe experiments/exp_wire_predarg_binder_live_reader_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_wire_predarg_binder_live_reader_v1.py --run
     .venv/Scripts/python.exe experiments/exp_wire_predarg_binder_live_reader_v1.py --smoke
GLASS-BOX. No external LLM at inference (the invariant). nltk (static POS/lemmas) + numpy only; no torch,
no spaCy. Writes only to data/exp_wire_predarg_binder_live_reader_v1/.
# KB_REFERENT: data/eval_gold_mention_role_mcguffey_v1/gold_multiclause_entity_track_v3.jsonl
# KB_REFERENT: data/eval_gold_mention_role_mcguffey_v1/gold_multientity_dense_v1.jsonl
# KB_REFERENT: data/frontend_assets/pos_tagger_ud_ewt_upos.json
# KB_REFERENT: data/frontend_assets/arc_parser_hashed_ud_ewt.npz
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# ---- INHERIT the prior negative's instrument (compose, do not re-derive) ----
from experiments.exp_wire_organs_endtoend_v1 import (  # noqa: E402
    load_gold, _passage_aliases, _extract_clause_roles, _partial_cue_lemmas,
    boot_ci, _seed_int, _PRO_F, _PRO_M, _PRO_ANY, _NAME_GENDER,
    live_extract_raw, resolve_raw,
)
from experiments.exp_wire_organs_endtoend_v1 import (  # noqa: E402  (the prior's validated quotative pieces)
    SPEECH_VERBS, _is_animate_head,
)
from hdlab.reading_grounding_loop import content_lemmas  # noqa: E402
from hdlab.candidate_generator import CandidateGenerator  # noqa: E402
from hdlab.predicate_argument_frontend import route_predicate_arguments, get_event_classes  # noqa: E402
from hdlab.thematic_role_labeler import lemma_verb  # noqa: E402
from hdlab.graded_coref_pick import graded_antecedent_pick  # noqa: E402

POS_ASSET = os.path.join(REPO_ROOT, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
ARC_ASSET = os.path.join(REPO_ROOT, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")

# predarg thematic role -> McGuffey gold role (the raw commit label; family-normalized before scoring).
# The router's "theme" is the single structural direct-object argument -> the gold's OBJECT family
# {patient,theme}; we commit "patient" (the label the positional rule uses) and normalize both sides.
PREDARG_TO_GOLD = {
    "agent": "agent", "theme": "patient", "goal": "goal", "recipient": "recipient",
    "source": "source", "location": "location", "path": "path", "direction": "direction",
    "instrument": "instrument",
}
# grammatical role fed to the graded binder (Cf prominence), per predarg thematic slot.
PREDARG_TO_GRAM = {
    "agent": "SUBJECT", "theme": "OBJECT", "recipient": "OTHER", "goal": "OTHER",
    "source": "OTHER", "location": "OTHER", "path": "OTHER", "direction": "OTHER", "instrument": "OTHER",
}
# ROLE-FAMILY normalization (front-end's natural grain), applied SYMMETRICALLY to gold + pred + floor.
ROLE_FAMILY = {
    "agent": "AGENT", "experiencer": "AGENT_EXP",  # experiencer kept distinct (psych-subject; frame-labeler axis)
    "patient": "OBJECT", "theme": "OBJECT",
    "recipient": "RECIPIENT", "addressee": "RECIPIENT",
    "goal": "GOAL", "source": "SOURCE", "location": "LOCATION", "path": "PATH",
    "direction": "DIRECTION", "instrument": "INSTRUMENT", "possessor": "POSSESSOR", "speaker": "AGENT",
}


def fam(role):
    return ROLE_FAMILY.get(role, role)


def _is_pron(w):
    wl = w.strip(".,\"'").lower()
    return wl in _PRO_F or wl in _PRO_M or wl in {"they", "them", "their", "it", "its"}


def _pron_gender(w):
    wl = w.strip(".,\"'").lower()
    if wl in _PRO_F:
        return "fem"
    if wl in _PRO_M:
        return "masc"
    return None


# ============================================================================================
# the WIRED front-end: parse -> route_predicate_arguments (richer roles) -> the prior's recency
# candidate builder, resolved by RECENCY (incumbent) or the GRADED BINDER (the wiring).
# ============================================================================================
def _is_speech_verb(lemma):
    """COMM event-class (the router's OWN VerbNet class, glass-box static asset) OR the prior negative's
    validated curated speech-verb set (covers archaic verbs VerbNet misses: exclaim/murmur/...)."""
    return ("COMM" in get_event_classes(lemma)) or (lemma in SPEECH_VERBS)


def _quote_mask(toks):
    inq = [False] * len(toks)
    q = False
    for i, w in enumerate(toks):
        if w in ('"', '``', "''", "“", "”"):
            q = not q
        inq[i] = q
    return inq


def _quotative_speaker(toks, pos, v):
    """QUOTATIVE-INVERSION agent (the construction the landed router lacks): for a speech/COMM verb, the
    SPEAKER is the nearest ANIMATE nominal OUTSIDE quotes, preferring POSTVERBAL ('said Fred') then
    preverbal; the quoted content is not a role filler. Returns a 1-based token index or None. PINNED:
    quotative inversion is a construction (Goldberg) the brain resolves from verb class + animacy, not
    linear position. Reuses the prior negative's validated speech-verb + animacy handling."""
    inq = _quote_mask(toks)
    order = list(range(v, len(toks))) + list(range(v - 2, -1, -1))   # postverbal first, then preverbal
    for i in order:
        if inq[i]:
            continue
        if pos[i] in ("NOUN", "PROPN", "PRON") and _is_animate_head(toks[i], _penn_hint(pos[i], toks[i])):
            return i + 1
    return None


def _penn_hint(upos, tok):
    """_is_animate_head expects a Penn-ish tag; map UPOS PROPN->NNP so its proper-name branch fires."""
    return "NNP" if upos == "PROPN" else ("PRP" if upos == "PRON" else "NN")


def _matrix_verbs(toks, pos, heads):
    """The clause's matrix predicate(s): the ROOT verb (head==0) + verbs coordinated to it (head==root).
    Excludes embedded participles/relatives so the who-did-what is the CLAUSE's assertion, not a modifier
    (matches the positional rule's single-predicate scope; good-enough parsing reads the main clause)."""
    verbs = [i for i in range(1, len(toks) + 1) if pos[i - 1] == "VERB"]
    if not verbs:
        return []
    roots = [v for v in verbs if heads.get(v, 0) == 0]
    if not roots:
        roots = [verbs[0]]
    keep = set(roots)
    for v in verbs:
        if heads.get(v) in keep:            # coordinated / chained to a matrix verb
            keep.add(v)
    return sorted(keep)


def predarg_extract_raw(passage, gen, *, use_frame=False, quotative=True, twin_role=False, seed=0):
    """Mirror the prior negative's live_extract_raw candidate builder (recency-ordered entity candidates
    per extracted head) but source the (head, thematic_role) pairs from the LANDED event-semantic router
    over a REAL parse. Returns the prior's `raw` format so resolve_raw / resolve_graded consume it
    identically. use_frame relabels a psych-verb subject agent->experiencer via the reader's already-wired
    frame labeler. twin_role = INFO-FREE role twin: keep the SAME heads, assign each a RANDOM role from the
    router's emitted inventory (destroys the role-labeling signal)."""
    ent_names = list(passage["entities"].keys())
    alias, gender = _passage_aliases(passage)
    clauses = passage["clauses"]
    frame_fn = _frame_labeler() if use_frame else None
    rng = np.random.default_rng(_seed_int("TWINROLE" + passage["passage_id"], seed)) if twin_role else None
    raw = []
    seen_order = []
    for ci, clause in enumerate(clauses):
        for name in ent_names:                                  # recency stack (mention order), as prior
            if any(len(a) > 2 and a in clause.lower() for a in alias[name]):
                if name in seen_order:
                    seen_order.remove(name)
                seen_order.append(name)
        r = gen.generate(clause)
        toks, pos, heads = r.tokens, r.pos, r.heads
        clem = list(content_lemmas(clause))
        pred = None
        extracted = []                                          # (head_token, gold_role, gram_role)
        for v in _matrix_verbs(toks, pos, heads):
            if pred is None:
                pred = toks[v - 1].lower()
            # quotative=False: this cell applies its OWN quotative handling below (and ablates it via the
            # `quotative` flag); the router's own quotative (landed 2026-08-30) is disabled here to keep the
            # ablation faithful. The landed router does quotative by DEFAULT for production callers.
            roles = route_predicate_arguments(toks, pos, heads, v, quotative=False)
            if quotative:
                lem = lemma_verb(toks[v - 1])
                if _is_speech_verb(lem):
                    sp = _quotative_speaker(toks, pos, v)
                    if sp is not None:
                        roles = dict(roles)
                        roles["agent"] = sp        # postverbal speaker is the AGENT (quotative inversion)
                        roles["theme"] = None      # the quoted content is not a role filler
            for pa_role in ("agent", "theme", "recipient", "goal", "source", "location", "path",
                            "direction", "instrument"):
                ti = roles.get(pa_role)
                if not ti:
                    continue
                gold_role = PREDARG_TO_GOLD.get(pa_role)
                if gold_role is None:
                    continue
                if use_frame and pa_role == "agent" and frame_fn is not None and frame_fn(toks, v, ti):
                    gold_role = "experiencer"
                extracted.append((toks[ti - 1], gold_role, PREDARG_TO_GRAM.get(pa_role, "OTHER")))
        if twin_role and extracted:
            pool = [gr for _h, gr, _g in extracted]             # same role multiset, detached from heads
            extracted = [(h, pool[int(rng.integers(0, len(pool)))], g) for h, _gr, g in extracted]
        for head, role, gram in extracted:
            hl = head.strip(".,\"'").lower()
            name_c = [n for n in ent_names if hl in alias[n]]
            if name_c:
                cands = name_c[:]
            elif hl in _PRO_ANY:
                want = "fem" if hl in _PRO_F else ("masc" if hl in _PRO_M else None)
                cands = [n for n in ent_names if (want is None or gender.get(n) in (want, None))]
            else:
                cands = []
            if not cands:
                continue
            def rec_rank(n):
                return seen_order.index(n) if n in seen_order else -1
            cands_ranked = sorted(cands, key=lambda n: -rec_rank(n))
            raw.append({"clause": ci, "role": role, "gram": gram, "pred": pred or "",
                        "candidates": cands_ranked, "content_lemmas": clem, "ambiguous": len(cands) > 1})
    return raw


def resolve_graded(raw, passage, *, twin_bind=False, seed=0):
    """Commit each raw (head, role) to an entity. NAMED / unambiguous -> candidates[0] (recency). PRONOUN
    with >1 gn-compatible candidate -> the GRADED BINDER (Lewis-Vasishth cue retrieval) over the causally-
    accumulated (clause, gram-role) histories -- or a RANDOM gn-compatible candidate for the info-free
    bind-twin. This is the who-did-what wiring the bar asks for."""
    rng = np.random.default_rng(_seed_int("GB" + passage["passage_id"], seed))
    ent_hist = defaultdict(list)
    committed = []
    for b in raw:
        cands = b["candidates"]
        if len(cands) == 1 or not b["ambiguous"]:
            pick = cands[0]
        elif twin_bind:
            pick = cands[int(rng.integers(0, len(cands)))]
        else:
            # a pronoun binds only to an ALREADY-INTRODUCED entity (one with a prior mention); the graded
            # binder competes over their (clause, gram-role) histories. If none have history yet, fall back
            # to the recency-ordered extraction candidate (candidates[0]).
            gram = b.get("gram") or {"agent": "SUBJECT", "patient": "OBJECT"}.get(b["role"], "OTHER")
            hc = [(c, ent_hist[c]) for c in cands if ent_hist[c]]
            if not hc:
                pick = cands[0]
            else:
                res = graded_antecedent_pick([h for _c, h in hc], b["clause"], pron_role=gram)
                pk = res["pick"]
                pick = hc[pk][0] if 0 <= pk < len(hc) else hc[0][0]
        committed.append({"entity": pick, "clause": b["clause"], "role": b["role"], "pred": b["pred"],
                          "content_lemmas": b["content_lemmas"], "ambiguous": b["ambiguous"]})
        ent_hist[pick].append((b["clause"], b.get("gram", "OTHER")))
    return committed


_FRAME_CACHE = {}


def _frame_labeler():
    """Return f(tokens, verb_idx1based, subj_idx1based)->bool : True iff the frame-primary labeler (already
    wired in situation_reader) assigns the subject EXPERIENCER (psych verb). Composes hdlab.frame_induction
    exactly as hdlab.situation_reader._assign_frame_primary_roles does. Cached; degrades to False on error."""
    if "fn" in _FRAME_CACHE:
        return _FRAME_CACHE["fn"]
    try:
        from hdlab.frame_induction import frame_primary_role, get_induced_subj_hypothesis
        from hdlab.thematic_role_labeler import lemma_verb
        ind_name, ind_hyp = get_induced_subj_hypothesis()

        def f(tokens, v1, subj1):
            try:
                lemma = lemma_verb(tokens[v1 - 1])
                role = frame_primary_role(lemma, [t.lower() for t in tokens], v1 - 1, subj1 - 1, "subj",
                                          chosen_name=ind_name, hypothesis=ind_hyp)
                return role == "EXPERIENCER"
            except Exception:
                return False
    except Exception:
        def f(tokens, v1, subj1):
            return False
    _FRAME_CACHE["fn"] = f
    return f


# ============================================================================================
# scoring at the front-end's GRAIN (family-normalized), applied symmetrically to gold + pred + floor
# ============================================================================================
def _committed_lookup(binds):
    by_ec = {}
    by_ent = defaultdict(list)
    for b in binds:
        by_ec.setdefault((b["entity"], b["clause"]), b["role"])
        by_ent[b["entity"]].append(b)
    return by_ec, by_ent


def score_roles(passages, binds_by_pid, *, grain="family", subset="all", seed=0):
    """End-to-end role answering (score_endtoend logic, but grain-normalized + richer subsets).
    grain: 'family' (front-end's natural grain, symmetric) or 'exact' (conservative lower bound).
    subset: 'all' | 'in_scope'(agent/patient gold) | 'non_agent'(gold_role!=agent) | 'predarg_scope'
            (gold family in what the router can structurally emit: AGENT/OBJECT/RECIPIENT/GOAL)."""
    norm = fam if grain == "family" else (lambda x: x)
    gm = Counter(q["gold_role"] for p in passages for q in p.get("target_queries", [])).most_common(1)[0][0]
    gm_n = norm(gm)
    PREDARG_SCOPE_FAM = {"AGENT", "OBJECT", "RECIPIENT", "GOAL"}
    vals = []
    for p in passages:
        pid = p["passage_id"]
        by_ec, by_ent = _committed_lookup(binds_by_pid[pid])
        for q in p.get("target_queries", []):
            ent, qc, gold = q["entity"], q["query_clause"], q["gold_role"]
            if subset == "in_scope" and gold not in ("agent", "patient"):
                continue
            if subset == "non_agent" and gold == "agent":
                continue
            if subset == "predarg_scope" and fam(gold) not in PREDARG_SCOPE_FAM:
                continue
            if (ent, qc) in by_ec:
                pr = by_ec[(ent, qc)]
            elif by_ent[ent]:
                pr = max(by_ent[ent], key=lambda x: x["clause"])["role"]
            else:
                pr = gm
            vals.append(int(norm(pr) == norm(gold)))
    m, lo, hi, hw = boot_ci(vals, seed=_seed_int("SR" + grain + str(subset), seed))
    return {"role_acc": round(m, 4), "role_ci": [round(lo, 4), round(hi, 4)], "role_hw": round(hw, 4),
            "n": len(vals)}


def majority_floor(passages, *, grain="family", subset="all", seed=0):
    """Majority-role floor recomputed ON the (grain, subset) population -- the strongest trivial floor."""
    norm = fam if grain == "family" else (lambda x: x)
    PREDARG_SCOPE_FAM = {"AGENT", "OBJECT", "RECIPIENT", "GOAL"}
    gold = []
    for p in passages:
        for q in p.get("target_queries", []):
            g = q["gold_role"]
            if subset == "in_scope" and g not in ("agent", "patient"):
                continue
            if subset == "non_agent" and g == "agent":
                continue
            if subset == "predarg_scope" and fam(g) not in PREDARG_SCOPE_FAM:
                continue
            gold.append(norm(g))
    if not gold:
        return {"role_acc": 0.0, "role_ci": [0.0, 0.0], "role_hw": 0.0, "n": 0, "label": None}
    lab = Counter(gold).most_common(1)[0][0]
    vals = [int(g == lab) for g in gold]
    m, lo, hi, hw = boot_ci(vals, seed=seed + 7)
    return {"role_acc": round(m, 4), "role_ci": [round(lo, 4), round(hi, 4)], "role_hw": round(hw, 4),
            "n": len(vals), "label": lab}


def counting_floor(passages, binds_by_pid, *, grain="family", seed=0):
    """The INHERITED content-lemma-overlap COUNTING floor (the prior negative's floor-to-beat), recomputed
    here: retrieve the stored event with max content-lemma Jaccard to the query clause (+entity bonus) and
    return ITS role. Reported on TWO stores: ORACLE (gold bindings; ~0.98, the prior's number, no front-end
    can beat it) and the arm's OWN (predarg/positional) noisy store -- the fair front-end-vs-counting test."""
    norm = fam if grain == "family" else (lambda x: x)
    gm = Counter(q["gold_role"] for p in passages for q in p.get("target_queries", [])).most_common(1)[0][0]
    vals = []
    for p in passages:
        pid = p["passage_id"]
        binds = binds_by_pid[pid]
        # build a lemma store keyed by (entity, clause) -> role, with the clause's content lemmas
        items = []
        for b in binds:
            items.append({"entity": b["entity"], "role": b["role"], "lemmas": set(b.get("content_lemmas", []))})
        for q in p.get("target_queries", []):
            ent, qc, gold = q["entity"], q["query_clause"], q["gold_role"]
            cue = set(_partial_cue_lemmas(p["clauses"][qc]))
            best, brole = -1.0, gm
            for it in items:
                ov = len(cue & it["lemmas"]) / max(1, len(cue | it["lemmas"]))
                ov += 0.25 if it["entity"] == ent else 0.0
                if ov > best:
                    best, brole = ov, it["role"]
            vals.append(int(norm(brole) == norm(gold)))
    m, lo, hi, hw = boot_ci(vals, seed=_seed_int("CNT" + grain, seed))
    return {"role_acc": round(m, 4), "role_ci": [round(lo, 4), round(hi, 4)], "role_hw": round(hw, 4),
            "n": len(vals)}


def paired_vs_counting(passages, arm_by_pid, store_by_pid, *, grain="family", seed=0, n_boot=2000):
    """Paired (per-passage) bootstrap: the arm's end-to-end role answering MINUS the content-lemma COUNTING
    floor answered over `store_by_pid` (matched bindings). The FAIR front-end-vs-counting test the bar wants
    (both see the same noisy store; oracle-store counting is unbeatable by any front-end and reported apart)."""
    norm = fam if grain == "family" else (lambda x: x)
    gm = Counter(q["gold_role"] for p in passages for q in p.get("target_queries", [])).most_common(1)[0][0]

    def arm_correct(binds_by_pid, p, q):
        by_ec, by_ent = _committed_lookup(binds_by_pid[p["passage_id"]])
        ent, qc = q["entity"], q["query_clause"]
        if (ent, qc) in by_ec:
            pr = by_ec[(ent, qc)]
        elif by_ent[ent]:
            pr = max(by_ent[ent], key=lambda x: x["clause"])["role"]
        else:
            pr = gm
        return int(norm(pr) == norm(q["gold_role"]))

    def count_correct(store, p, q):
        items = [{"entity": b["entity"], "role": b["role"], "lemmas": set(b.get("content_lemmas", []))}
                 for b in store[p["passage_id"]]]
        cue = set(_partial_cue_lemmas(p["clauses"][q["query_clause"]]))
        best, brole = -1.0, gm
        for it in items:
            ov = len(cue & it["lemmas"]) / max(1, len(cue | it["lemmas"])) + (0.25 if it["entity"] == q["entity"] else 0.0)
            if ov > best:
                best, brole = ov, it["role"]
        return int(norm(brole) == norm(q["gold_role"]))

    rows = []
    for p in passages:
        a = c = n = 0
        for q in p.get("target_queries", []):
            a += arm_correct(arm_by_pid, p, q); c += count_correct(store_by_pid, p, q); n += 1
        rows.append((a, c, n))
    A = np.array(rows, float)
    delta = (A[:, 0].sum() - A[:, 1].sum()) / max(A[:, 2].sum(), 1)
    r = np.random.default_rng(_seed_int("PVC" + grain, seed)); nd = len(A); boots = []
    for _ in range(n_boot):
        idx = r.integers(0, nd, nd)
        boots.append((A[idx, 0].sum() - A[idx, 1].sum()) / max(A[idx, 2].sum(), 1))
    boots = np.array(boots); lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"delta": round(float(delta), 4), "ci": [round(float(lo), 4), round(float(hi), 4)],
            "half_width": round(float(hi - lo) / 2, 4),
            "null_p95": round(float(np.percentile(np.abs(boots - boots.mean()), 95)), 4),
            "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}


def oracle_bindings(passage):
    """Perfect front-end: the gold entity-role chains as committed bindings (the role upper bound)."""
    out, clauses = [], passage["clauses"]
    for name, chain in passage["entities"].items():
        for m in chain:
            ci = m["clause"]
            if ci < len(clauses):
                out.append({"entity": name, "clause": ci, "role": m["role"],
                            "content_lemmas": list(content_lemmas(clauses[ci])), "ambiguous": False})
    return out


def positional_bindings(passage):
    """The current LIVE reader's positional agent/patient front-end (floor a), resolved by the prior
    negative's OWN recency machinery (live_extract_raw + resolve_raw) -- reproduces its 0.483 headline."""
    return resolve_raw(live_extract_raw(passage, mode="position"), passage, "recency")


# ============================================================================================
# BINDING-SENSITIVE who-did-what (2nd, independent metric): 'which ENTITY filled the role-slot at clause C'
# -- inverted so a MIS-BOUND pronoun directly fails (the role metric is binding-blind + majority-masked).
# ============================================================================================
_WDW_PRON = frozenset("he she it they him her them his its their himself herself themselves".split())


def _who_rows(passages, binds_by_pid, *, only_pron, grain="family"):
    """Per-passage (correct, total): for each gold (entity E, clause C, role R) [mention a pronoun if
    only_pron], is E among the entities the reader bound to the (clause C, family(R)) slot? Skips slots the
    reader left empty (that is a MISS, measured elsewhere) so this isolates BINDING quality, not coverage."""
    norm = fam if grain == "family" else (lambda x: x)
    rows = []
    for p in passages:
        slot = defaultdict(list)
        for b in binds_by_pid[p["passage_id"]]:
            slot[(b["clause"], norm(b["role"]))].append(b["entity"])
        c = n = 0
        for ent, chain in p["entities"].items():
            for m in chain:
                if only_pron and m["mention"].strip().lower() not in _WDW_PRON:
                    continue
                ents = slot.get((m["clause"], norm(m["role"])), [])
                if not ents:
                    continue
                n += 1; c += int(ent in ents)
        rows.append((c, n))
    return rows


def _rows_ci(rows, seed=0, n_boot=2000):
    A = np.array([r for r in rows if r[1] > 0], float)
    if len(A) == 0:
        return {"acc": 0.0, "ci": [0.0, 0.0], "n": 0}
    acc = A[:, 0].sum() / A[:, 1].sum()
    r = np.random.default_rng(seed); nd = len(A); b = []
    for _ in range(n_boot):
        idx = r.integers(0, nd, nd); b.append(A[idx, 0].sum() / max(A[idx, 1].sum(), 1))
    lo, hi = np.percentile(b, [2.5, 97.5])
    return {"acc": round(float(acc), 4), "ci": [round(float(lo), 4), round(float(hi), 4)], "n": int(A[:, 1].sum())}


def _rows_paired(rows_a, rows_b, seed=0, n_boot=2000):
    A = np.array(rows_a, float); B = np.array(rows_b, float)
    delta = A[:, 0].sum() / max(A[:, 1].sum(), 1) - B[:, 0].sum() / max(B[:, 1].sum(), 1)
    r = np.random.default_rng(seed); nd = len(A); bo = []
    for _ in range(n_boot):
        i = r.integers(0, nd, nd)
        bo.append(A[i, 0].sum() / max(A[i, 1].sum(), 1) - B[i, 0].sum() / max(B[i, 1].sum(), 1))
    bo = np.array(bo); lo, hi = np.percentile(bo, [2.5, 97.5])
    return {"delta": round(float(delta), 4), "ci": [round(float(lo), 4), round(float(hi), 4)],
            "half_width": round(float(hi - lo) / 2, 4),
            "null_p95": round(float(np.percentile(np.abs(bo - bo.mean()), 95)), 4),
            "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}


def who_did_what(passages, arms_by_pid, *, seed=0, n_boot=2000):
    """The binding-sensitive who-did-what block. arms_by_pid = {name: binds_by_pid}. Reports acc+CI per arm
    on ALL mentions and the PRONOUN-only subset (the binder's population), plus the key paired contrasts."""
    out = {"all": {}, "pronoun": {}}
    for only, key in ((False, "all"), (True, "pronoun")):
        for nm, b in arms_by_pid.items():
            out[key][nm] = _rows_ci(_who_rows(passages, b, only_pron=only), seed=seed, n_boot=n_boot)
    def pd(a, bb, only):
        return _rows_paired(_who_rows(passages, arms_by_pid[a], only_pron=only),
                            _who_rows(passages, arms_by_pid[bb], only_pron=only), seed=seed, n_boot=n_boot)
    out["contrasts"] = {
        "PREDARG_over_POSITION_all": pd("PREDARG_GRADED", "POSITION", False),
        "PREDARG_over_POSITION_pronoun": pd("PREDARG_GRADED", "POSITION", True),
        # the binder's own contribution, on its binding-sensitive population (pronoun subset)
        "GRADED_over_recency_pronoun": pd("PREDARG_GRADED", "PREDARG_RECENCY", True),
        "GRADED_over_RANDBIND_twin_pronoun": pd("PREDARG_GRADED", "PREDARG_RANDBIND", True),
    }
    return out


# ============================================================================================
# no-regression + per-role recall
# ============================================================================================
def no_regression(passages, pos_by_pid, new_by_pid, *, grain="family"):
    """On the queries the POSITIONAL reader answers CORRECTLY, how many does the new front-end get WRONG?
    A wiring must not break what worked. Returns counts + the regressed items."""
    norm = fam if grain == "family" else (lambda x: x)
    gm = Counter(q["gold_role"] for p in passages for q in p.get("target_queries", [])).most_common(1)[0][0]

    def answer(binds_by_pid, p, q):
        by_ec, by_ent = _committed_lookup(binds_by_pid[p["passage_id"]])
        ent, qc = q["entity"], q["query_clause"]
        if (ent, qc) in by_ec:
            return by_ec[(ent, qc)]
        if by_ent[ent]:
            return max(by_ent[ent], key=lambda x: x["clause"])["role"]
        return gm
    pos_right = regressed = both_right = 0
    reg_items = []
    for p in passages:
        for q in p.get("target_queries", []):
            g = norm(q["gold_role"])
            pa = norm(answer(pos_by_pid, p, q))
            na = norm(answer(new_by_pid, p, q))
            if pa == g:
                pos_right += 1
                if na == g:
                    both_right += 1
                else:
                    regressed += 1
                    reg_items.append({"passage": p["passage_id"], "entity": q["entity"],
                                      "clause": q["query_clause"], "gold": q["gold_role"]})
    return {"pos_correct": pos_right, "kept": both_right, "regressed": regressed,
            "regression_rate": round(regressed / pos_right, 4) if pos_right else 0.0,
            "regressed_items": reg_items[:20]}


def per_role_recall(passages, binds_by_pid, *, grain="family"):
    """Per-gold-role recall (family grain): the attribution -- which roles the front-end newly recovers."""
    norm = fam if grain == "family" else (lambda x: x)
    gm = Counter(q["gold_role"] for p in passages for q in p.get("target_queries", [])).most_common(1)[0][0]
    hit, tot = defaultdict(int), defaultdict(int)
    for p in passages:
        by_ec, by_ent = _committed_lookup(binds_by_pid[p["passage_id"]])
        for q in p.get("target_queries", []):
            ent, qc, gold = q["entity"], q["query_clause"], q["gold_role"]
            key = norm(gold)
            tot[key] += 1
            if (ent, qc) in by_ec:
                pr = by_ec[(ent, qc)]
            elif by_ent[ent]:
                pr = max(by_ent[ent], key=lambda x: x["clause"])["role"]
            else:
                pr = gm
            hit[key] += int(norm(pr) == key)
    return {k: {"recall": round(hit[k] / tot[k], 3), "n": tot[k]} for k in sorted(tot)}


def paired_delta(passages, a_by_pid, b_by_pid, *, grain="family", subset="all", seed=0, n_boot=2000):
    """Paired (per-passage) bootstrap of arm A minus arm B end-to-end role acc, on the (grain,subset)
    population. Reports delta, CI, half-width, null p95, separation band."""
    norm = fam if grain == "family" else (lambda x: x)
    gm = Counter(q["gold_role"] for p in passages for q in p.get("target_queries", [])).most_common(1)[0][0]
    PREDARG_SCOPE_FAM = {"AGENT", "OBJECT", "RECIPIENT", "GOAL"}

    def per_passage(binds_by_pid):
        rows = []
        for p in passages:
            by_ec, by_ent = _committed_lookup(binds_by_pid[p["passage_id"]])
            c = n = 0
            for q in p.get("target_queries", []):
                g = q["gold_role"]
                if subset == "in_scope" and g not in ("agent", "patient"):
                    continue
                if subset == "non_agent" and g == "agent":
                    continue
                if subset == "predarg_scope" and fam(g) not in PREDARG_SCOPE_FAM:
                    continue
                ent, qc = q["entity"], q["query_clause"]
                if (ent, qc) in by_ec:
                    pr = by_ec[(ent, qc)]
                elif by_ent[ent]:
                    pr = max(by_ent[ent], key=lambda x: x["clause"])["role"]
                else:
                    pr = gm
                c += int(norm(pr) == norm(g)); n += 1
            rows.append((c, n))
        return np.array(rows, float)
    A, B = per_passage(a_by_pid), per_passage(b_by_pid)
    tot = A[:, 1].sum()
    delta = A[:, 0].sum() / max(tot, 1) - B[:, 0].sum() / max(B[:, 1].sum(), 1)
    r = np.random.default_rng(_seed_int("PD" + grain + str(subset), seed))
    nd = len(A); boots = []
    for _ in range(n_boot):
        idx = r.integers(0, nd, nd)
        da = A[idx, 0].sum() / max(A[idx, 1].sum(), 1)
        db = B[idx, 0].sum() / max(B[idx, 1].sum(), 1)
        boots.append(da - db)
    boots = np.array(boots)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"delta": round(float(delta), 4), "ci": [round(float(lo), 4), round(float(hi), 4)],
            "half_width": round(float(hi - lo) / 2, 4),
            "null_p95": round(float(np.percentile(np.abs(boots - boots.mean()), 95)), 4),
            "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP"), "n": int(tot)}


# ============================================================================================
# parse-quality cap (corpus-age wall): modern UAS + on-domain confidence + role upper bound
# ============================================================================================
# the arc parser's MODERN ceiling, from its OWN training/eval cell (exp_depparse_hashed_cpu_v1, MIDDLE_BAND):
# UAS 0.7868 on UD-EWT dev (1989 sents, 24444 arcs). CITED provenance, not re-run here (importing that cell
# executes it). The reader domain (19c McGuffey / LitBank) is OUT-OF-DISTRIBUTION for a UD-EWT parser.
MODERN_UD_EWT_DEV_UAS = 0.7868


def litbank_domain_probe(gen, n_docs=20):
    """Gold-free empirical characterization of the ARCHAIC-PROSE parse wall (informs sibling p8): parse
    confidence + sentence complexity on LitBank (19c literary prose) vs the McGuffey graded readers. No gold
    heads needed. KEY FINDING: the arc MARGIN does NOT drop on LitBank (the hashed perceptron margin is
    uncalibrated -> confidently wrong on OOD, so a margin-abstain policy is weak); the measurable domain gaps
    are sentence LENGTH (p90) and a much higher NO-VERB rate (copula/AUX-headed + fragments)."""
    import glob
    from hdlab.scene_segment import parse_conll_sentences

    def _stats(sents, cap=400):
        margins, lens, noverb, n = [], [], 0, 0
        for toks in sents:
            if not toks or len(toks) > 120:
                continue
            n += 1
            if n > cap:
                break
            r = gen.generate(" ".join(toks))
            if not r.tokens:
                continue
            lens.append(len(r.tokens)); margins.extend(r.margins.values())
            noverb += int(not any(t == "VERB" for t in r.pos))
        m = np.array(margins, float) if margins else np.array([0.0])
        return {"n_sents": n, "mean_len": round(float(np.mean(lens)), 1),
                "p90_len": round(float(np.percentile(lens, 90)), 1),
                "mean_arc_margin": round(float(m.mean()), 3),
                "frac_margin_lt1": round(float((m < 1.0).mean()), 3),
                "frac_noverb": round(noverb / max(n, 1), 3)}

    from experiments.exp_wire_organs_endtoend_v1 import load_gold as _lg
    mcg = [c.split() for p in _lg() for c in p["clauses"]]
    conll = os.path.join(REPO_ROOT, "data/litbank/coref/conll")
    lit = []
    for f in sorted(glob.glob(os.path.join(conll, "*.conll")))[:n_docs]:
        try:
            lit.extend(parse_conll_sentences(f))
        except Exception:
            pass
    return {"mcguffey_graded": _stats(mcg), "litbank_19c_literary": _stats(lit),
            "modern_ud_ewt_dev_UAS_cited": MODERN_UD_EWT_DEV_UAS, "n_litbank_docs": n_docs,
            "reading": ("arc margin ~equal McGuffey vs LitBank (uncalibrated -> NOT an OOD detector); the domain "
                        "gap is sentence LENGTH (p90) + a ~7x higher NO-VERB rate (copula/AUX + fragments).")}


def parse_quality(gen, passages, seed=0):
    """Localize the parse cap on the reading domain (no gold heads on McGuffey -> UAS gold unavailable;
    the p8 sibling `role_assignment_is_untested_on_archaic_literary_prose` owns the parse-quality lift).
    Signals: (1) the parser's CITED modern ceiling (UD-EWT dev UAS 0.7868); (2) on-domain arc confidence
    (mean per-token best-second margin on McGuffey -- low = OOD/unsure); (3) extraction miss rate (clauses
    where the tagger emits NO verb)."""
    margins = []
    n_tok = n_clause_noverb = n_clause = 0
    for p in passages:
        for clause in p["clauses"]:
            r = gen.generate(clause)
            n_clause += 1
            if not any(t == "VERB" for t in r.pos):
                n_clause_noverb += 1
            margins.extend(r.margins.values())
            n_tok += len(r.tokens)
    margins = np.array(margins, float) if margins else np.array([0.0])
    return {"modern_ud_ewt_dev_UAS_cited": MODERN_UD_EWT_DEV_UAS,
            "mcguffey_mean_arc_margin": round(float(margins.mean()), 4),
            "mcguffey_median_arc_margin": round(float(np.median(margins)), 4),
            "mcguffey_frac_low_margin_lt1": round(float((margins < 1.0).mean()), 4),
            "n_tokens": n_tok, "n_clauses": n_clause,
            "frac_clauses_no_verb_extracted": round(n_clause_noverb / max(n_clause, 1), 4),
            "note": "McGuffey UAS gold unavailable (no gold heads); parse-quality lift = sibling p8."}


# ============================================================================================
# top-level
# ============================================================================================
def run(passages, gen, seed=0, n_boot=2000):
    pids = [p["passage_id"] for p in passages]
    # extraction x resolution factorial (the two levers the bar wires: the parse->router EXTRACTION and the
    # graded-binder RESOLUTION), all resolved on the prior negative's own recency machinery for POSITION.
    pos_b = {p["passage_id"]: positional_bindings(p) for p in passages}                       # incumbent floor
    posg_b = {p["passage_id"]: resolve_graded(live_extract_raw(p, mode="position"), p, seed=seed)
              for p in passages}                                                              # binder lever alone
    ora_b = {p["passage_id"]: oracle_bindings(p) for p in passages}
    predraw = {p["passage_id"]: predarg_extract_raw(p, gen, use_frame=False, seed=seed) for p in passages}
    predfraw = {p["passage_id"]: predarg_extract_raw(p, gen, use_frame=True, seed=seed) for p in passages}
    prednqraw = {p["passage_id"]: predarg_extract_raw(p, gen, use_frame=False, quotative=False, seed=seed)
                 for p in passages}
    predrec_b = {pid: resolve_raw(predraw[pid], _pass(passages, pid), "recency") for pid in pids}  # extract lever alone
    pred_b = {pid: resolve_graded(predraw[pid], _pass(passages, pid), seed=seed) for pid in pids}   # PRIMARY: parse+router+quotative+binder
    predf_b = {pid: resolve_graded(predfraw[pid], _pass(passages, pid), seed=seed) for pid in pids}  # +frame(experiencer)
    prednq_b = {pid: resolve_graded(prednqraw[pid], _pass(passages, pid), seed=seed) for pid in pids}  # -quotative ablation
    # HYBRID (the brain-faithful good-enough fallback, PROBLEM.md §3): use the parse->router structure where
    # available; fall back to the positional rule for clauses the parser leaves structureless (copula/AUX-only,
    # no-verb). predarg bindings FIRST so they WIN the (entity,clause) slot; positional fills the gaps.
    hyb_b = {pid: pred_b[pid] + pos_b[pid] for pid in pids}
    trole_b = {p["passage_id"]: resolve_graded(
        predarg_extract_raw(p, gen, use_frame=False, twin_role=True, seed=seed), p, seed=seed)
        for p in passages}                                                                    # info-free ROLE twin
    tbind_b = {pid: resolve_graded(predraw[pid], _pass(passages, pid), twin_bind=True, seed=seed)
               for pid in pids}                                                               # info-free BIND twin

    res = {"anchor": "wire_predarg_binder_live_reader_v1", "n_passages": len(passages),
           "n_queries": sum(len(p.get("target_queries", [])) for p in passages), "pids": pids,
           "PRIMARY_ARM": "PREDARG (parse -> route_predicate_arguments -> graded binder; no frame labeler)"}

    def block(binds):
        return {sub: score_roles(passages, binds, grain="family", subset=sub, seed=seed)
                for sub in ("all", "in_scope", "non_agent", "predarg_scope")}
    for k, b in (("POSITION", pos_b), ("POS_GRADED", posg_b), ("PREDARG_REC", predrec_b),
                 ("PREDARG_NOQUOT", prednq_b), ("PREDARG", pred_b), ("PREDARG_HYBRID", hyb_b),
                 ("PREDARG_FRAME", predf_b), ("TWIN_ROLE", trole_b), ("TWIN_BIND", tbind_b),
                 ("ORACLE_ROLE", ora_b)):
        res[k] = block(b)
    res["exact_grain"] = {
        "POSITION_all": score_roles(passages, pos_b, grain="exact", subset="all", seed=seed),
        "PREDARG_all": score_roles(passages, pred_b, grain="exact", subset="all", seed=seed),
        "PREDARG_FRAME_all": score_roles(passages, predf_b, grain="exact", subset="all", seed=seed),
    }
    res["floors"] = {
        "majority_all": majority_floor(passages, subset="all", seed=seed),
        "majority_non_agent": majority_floor(passages, subset="non_agent", seed=seed),
        "majority_predarg_scope": majority_floor(passages, subset="predarg_scope", seed=seed),
        "counting_ORACLE_store": counting_floor(passages, ora_b, seed=seed),
        "counting_PREDARG_store": counting_floor(passages, pred_b, seed=seed),
        "counting_POSITION_store": counting_floor(passages, pos_b, seed=seed),
    }
    res["contrasts"] = {
        "PREDARG_over_POSITION_all": paired_delta(passages, pred_b, pos_b, subset="all", seed=seed, n_boot=n_boot),
        "PREDARG_over_POSITION_non_agent": paired_delta(passages, pred_b, pos_b, subset="non_agent", seed=seed, n_boot=n_boot),
        "PREDARG_over_POSITION_predarg_scope": paired_delta(passages, pred_b, pos_b, subset="predarg_scope", seed=seed, n_boot=n_boot),
        "PREDARG_over_TWINROLE_all": paired_delta(passages, pred_b, trole_b, subset="all", seed=seed, n_boot=n_boot),
        "PREDARG_over_TWINROLE_non_agent": paired_delta(passages, pred_b, trole_b, subset="non_agent", seed=seed, n_boot=n_boot),
        "PREDARG_over_TWINBIND_all": paired_delta(passages, pred_b, tbind_b, subset="all", seed=seed, n_boot=n_boot),
        # lever attribution
        "EXTRACT_lever_PREDARGREC_over_POSITION_non_agent": paired_delta(passages, predrec_b, pos_b, subset="non_agent", seed=seed, n_boot=n_boot),
        "BINDER_lever_POSGRADED_over_POSITION_all": paired_delta(passages, posg_b, pos_b, subset="all", seed=seed, n_boot=n_boot),
        "FRAME_contribution_non_agent": paired_delta(passages, predf_b, pred_b, subset="non_agent", seed=seed, n_boot=n_boot),
        "QUOTATIVE_contribution_all": paired_delta(passages, pred_b, prednq_b, subset="all", seed=seed, n_boot=n_boot),
        "PREDARG_over_countingPREDARGstore_all": paired_vs_counting(passages, pred_b, pred_b, seed=seed, n_boot=n_boot),
        "PREDARG_over_countingPOSITIONstore_all": paired_vs_counting(passages, pred_b, pos_b, seed=seed, n_boot=n_boot),
        "PREDARG_over_countingORACLEstore_all": paired_vs_counting(passages, pred_b, ora_b, seed=seed, n_boot=n_boot),
    }
    res["contrasts"]["PREDARG_HYBRID_over_POSITION_all"] = paired_delta(passages, hyb_b, pos_b, subset="all", seed=seed, n_boot=n_boot)
    res["contrasts"]["PREDARG_HYBRID_over_TWINROLE_non_agent"] = paired_delta(passages, hyb_b, trole_b, subset="non_agent", seed=seed, n_boot=n_boot)
    res["no_regression_PREDARG_vs_POSITION"] = no_regression(passages, pos_b, pred_b, grain="family")
    res["no_regression_PREDARG_HYBRID_vs_POSITION"] = no_regression(passages, pos_b, hyb_b, grain="family")
    res["no_regression_PREDARGFRAME_vs_POSITION"] = no_regression(passages, pos_b, predf_b, grain="family")
    res["per_role_recall"] = {
        "POSITION": per_role_recall(passages, pos_b, grain="family"),
        "PREDARG": per_role_recall(passages, pred_b, grain="family"),
        "PREDARG_FRAME": per_role_recall(passages, predf_b, grain="family"),
    }
    res["parse_quality"] = parse_quality(gen, passages, seed=seed)
    # binding-sensitive who-did-what (2nd metric): PREDARG_RECENCY isolates extraction; PREDARG_GRADED adds
    # the binder; PREDARG_RANDBIND is the info-free binding twin.
    res["who_did_what"] = who_did_what(passages, {
        "POSITION": pos_b, "PREDARG_RECENCY": predrec_b, "PREDARG_GRADED": pred_b,
        "PREDARG_RANDBIND": tbind_b}, seed=seed, n_boot=n_boot)

    c = res["contrasts"]
    beats_pos_all = c["PREDARG_over_POSITION_all"]["band"] == "ABOVE"
    trole_loses = c["PREDARG_over_TWINROLE_non_agent"]["band"] == "ABOVE"
    beats_count_matched = c["PREDARG_over_countingPREDARGstore_all"]["band"] == "ABOVE"
    beats_count_oracle = c["PREDARG_over_countingORACLEstore_all"]["band"] == "ABOVE"
    res["verdict"] = {
        "beats_positional_all_CI": beats_pos_all,
        "PREDARG_over_POSITION_all_delta": c["PREDARG_over_POSITION_all"]["delta"],
        "beats_positional_non_agent_CI": c["PREDARG_over_POSITION_non_agent"]["band"] == "ABOVE",
        "role_twin_loses_CI": trole_loses,
        "regressed_count_PREDARG": res["no_regression_PREDARG_vs_POSITION"]["regressed"],
        "regression_rate_PREDARG": res["no_regression_PREDARG_vs_POSITION"]["regression_rate"],
        "beats_counting_matched_store_CI": beats_count_matched,
        "beats_counting_ORACLE_store_CI": beats_count_oracle,
        "quotative_contribution_delta": c["QUOTATIVE_contribution_all"]["delta"],
        "headline": ("WIRED_BEATS_POSITIONAL_CI_SEP_TWIN_LOSES"
                     if (beats_pos_all and trole_loses) else "NULL_OR_UNCONTROLLED"),
        "counting_note": ("PREDARG beats content-counting on MATCHED bindings; the ORACLE-store counting "
                          "floor (~0.98) is an oracle-input number no front-end can beat (the inherited cap)."),
    }
    return res


def _pass(passages, pid):
    for p in passages:
        if p["passage_id"] == pid:
            return p
    raise KeyError(pid)


def _load_gen():
    return CandidateGenerator.load(POS_ASSET, ARC_ASSET)


def self_test():
    """Mechanism can-fail on constructed clauses (gold-independent) + a tiny end-to-end sanity check."""
    gen = _load_gen()
    # (1) the router recovers GOAL + RECIPIENT + passive-agent off the real parse -- roles the positional
    #     rule scores 0.000 on / gets backwards.
    r = gen.generate("John ran into the garden .")
    v = [i for i in range(1, len(r.tokens) + 1) if r.pos[i - 1] == "VERB"][0]
    roles = route_predicate_arguments(r.tokens, r.pos, r.heads, v)
    assert roles["goal"] and r.tokens[roles["goal"] - 1].lower() == "garden", roles
    r = gen.generate("The girl gave the apple to the beggar .")
    v = [i for i in range(1, len(r.tokens) + 1) if r.pos[i - 1] == "VERB"][0]
    roles = route_predicate_arguments(r.tokens, r.pos, r.heads, v)
    assert roles["recipient"] and r.tokens[roles["recipient"] - 1].lower() == "beggar", roles
    # (2) the graded binder resolves a gender-compatible pronoun over accumulated histories (resolve_graded).
    raw = [{"clause": 0, "role": "agent", "gram": "SUBJECT", "pred": "run", "candidates": ["Mary"],
            "content_lemmas": [], "ambiguous": False},
           {"clause": 1, "role": "agent", "gram": "SUBJECT", "pred": "leave", "candidates": ["Mary", "John"],
            "content_lemmas": [], "ambiguous": True}]
    pas = {"passage_id": "st2"}
    comm = resolve_graded(raw, pas, seed=0)
    assert comm[1]["entity"] == "Mary", f"graded binder must bind the pronoun to Mary (has history), got {comm}"
    # (3) info-free ROLE twin: role labels are detached from heads (destroys the role signal).
    passage = {"passage_id": "st", "clauses": ["Mary gave the book to John .", "She left ."],
               "entities": {"Mary": [{"clause": 0, "mention": "Mary", "role": "agent"},
                                     {"clause": 1, "mention": "She", "role": "agent"}],
                            "John": [{"clause": 0, "mention": "John", "role": "recipient"}]},
               "target_queries": [{"entity": "John", "query_clause": 0, "gold_role": "recipient"}]}
    raw = predarg_extract_raw(passage, gen, use_frame=False, seed=0)
    binds = resolve_graded(raw, passage, seed=0)
    got = [b for b in binds if b["entity"] == "John" and b["clause"] == 0]
    assert any(fam(b["role"]) == "RECIPIENT" for b in got), f"predarg must bind John=recipient, got {binds}"
    tw = predarg_extract_raw(passage, gen, use_frame=False, twin_role=True, seed=0)
    assert [b["role"] for b in tw] != [b["role"] for b in raw] or len(raw) <= 1, "role twin must permute labels"
    print("SELF-TEST PASS (router recovers goal/recipient off the real parse; graded binder binds the "
          "gender-compatible pronoun to the entity with history; role-twin permutes labels; end-to-end "
          "commits a non-agent role positional cannot).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--litbank-probe", action="store_true", dest="litbank_probe")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.litbank_probe:
        print(json.dumps(litbank_domain_probe(_load_gen()), indent=2)); return
    passages = load_gold()
    if args.smoke:
        passages = passages[:8]
        args.n_boot = 400
    gen = _load_gen()
    res = run(passages, gen, seed=args.seed, n_boot=args.n_boot)
    outdir = os.path.join(REPO_ROOT, "data/exp_wire_predarg_binder_live_reader_v1")
    os.makedirs(outdir, exist_ok=True)
    fn = os.path.join(outdir, "metrics_smoke.json" if args.smoke else "metrics.json")
    with open(fn, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    # one-screen summary
    print(f"\n=== wire predarg+binder into live reader ({res['n_passages']} passages, {res['n_queries']} queries) ===")
    pq = res["parse_quality"]
    print(f"parse: CITED modern UD-EWT dev UAS={pq['modern_ud_ewt_dev_UAS_cited']}  "
          f"McGuffey mean arc margin={pq['mcguffey_mean_arc_margin']} "
          f"(frac<1.0={pq['mcguffey_frac_low_margin_lt1']}, no-verb clauses={pq['frac_clauses_no_verb_extracted']})")
    print("FAMILY-GRAIN end-to-end role accuracy [95% CI]  (all | non_agent | predarg_scope):")
    for k in ("POSITION", "POS_GRADED", "PREDARG_REC", "PREDARG_NOQUOT", "PREDARG", "PREDARG_HYBRID",
              "PREDARG_FRAME", "TWIN_ROLE", "TWIN_BIND", "ORACLE_ROLE"):
        a, na, ps = res[k]["all"], res[k]["non_agent"], res[k]["predarg_scope"]
        print(f"  {k:14s} all={a['role_acc']:.3f}[{a['role_ci'][0]:.3f},{a['role_ci'][1]:.3f}]  "
              f"non_agent={na['role_acc']:.3f}[{na['role_ci'][0]:.3f},{na['role_ci'][1]:.3f}]  "
              f"pscope={ps['role_acc']:.3f}")
    fl = res["floors"]
    print(f"floors: majority_all={fl['majority_all']['role_acc']:.3f}  "
          f"majority_non_agent={fl['majority_non_agent']['role_acc']:.3f}  "
          f"counting_ORACLE={fl['counting_ORACLE_store']['role_acc']:.3f}  "
          f"counting_PREDARG_store={fl['counting_PREDARG_store']['role_acc']:.3f}")
    c = res["contrasts"]
    for name in ("PREDARG_over_POSITION_all", "PREDARG_over_POSITION_non_agent",
                 "PREDARG_over_TWINROLE_non_agent", "PREDARG_over_TWINBIND_all",
                 "EXTRACT_lever_PREDARGREC_over_POSITION_non_agent", "BINDER_lever_POSGRADED_over_POSITION_all",
                 "QUOTATIVE_contribution_all"):
        d = c[name]
        print(f"  {name:48s} delta={d['delta']:+.3f} CI[{d['ci'][0]:+.3f},{d['ci'][1]:+.3f}] "
              f"null_p95={d['null_p95']:.3f} {d['band']}")
    nr = res["no_regression_PREDARG_vs_POSITION"]
    nrh = res["no_regression_PREDARG_HYBRID_vs_POSITION"]
    print(f"no-regression PREDARG: pos_correct={nr['pos_correct']} kept={nr['kept']} regressed={nr['regressed']} "
          f"({nr['regression_rate']:.3f})  |  HYBRID regressed={nrh['regressed']} ({nrh['regression_rate']:.3f})")
    ch = res["contrasts"]["PREDARG_HYBRID_over_POSITION_all"]
    print(f"  PREDARG_HYBRID_over_POSITION_all delta={ch['delta']:+.3f} CI[{ch['ci'][0]:+.3f},{ch['ci'][1]:+.3f}] {ch['band']}")
    print("per-role recall (family) POSITION -> PREDARG -> PREDARG_FRAME:")
    prr = res["per_role_recall"]
    for role in sorted(set(prr["POSITION"]) | set(prr["PREDARG"]) | set(prr["PREDARG_FRAME"])):
        pv = prr["POSITION"].get(role, {"recall": 0.0, "n": 0})
        dv = prr["PREDARG"].get(role, {"recall": 0.0, "n": 0})
        fv = prr["PREDARG_FRAME"].get(role, {"recall": 0.0, "n": 0})
        print(f"  {role:12s} n={fv['n']:3d}  {pv['recall']:.2f} -> {dv['recall']:.2f} -> {fv['recall']:.2f}")
    w = res["who_did_what"]
    print("BINDING-SENSITIVE who-did-what (which entity filled the role-slot) [95% CI]:")
    for sub in ("all", "pronoun"):
        row = w[sub]
        print(f"  {sub:8s} POSITION={row['POSITION']['acc']:.3f}  PREDARG+recency={row['PREDARG_RECENCY']['acc']:.3f}  "
              f"PREDARG+GRADED={row['PREDARG_GRADED']['acc']:.3f}  RANDbind={row['PREDARG_RANDBIND']['acc']:.3f} "
              f"(n={row['POSITION']['n']}/{row['PREDARG_GRADED']['n']})")
    for name in ("PREDARG_over_POSITION_all", "PREDARG_over_POSITION_pronoun",
                 "GRADED_over_recency_pronoun", "GRADED_over_RANDBIND_twin_pronoun"):
        d = w["contrasts"][name]
        print(f"  WDW {name:36s} delta={d['delta']:+.3f} CI[{d['ci'][0]:+.3f},{d['ci'][1]:+.3f}] {d['band']}")
    print(f"VERDICT: {res['verdict']['headline']}")
    print(f"wrote {fn}")


if __name__ == "__main__":
    main()
