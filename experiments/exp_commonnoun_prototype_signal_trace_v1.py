"""exp_commonnoun_prototype_signal_trace_v1 -- TRACE where each of the 3 buildable levers loses signal, to
separate WEAK-IMPLEMENTATION loss (fixable -> a better brain-faithful prototype) from a TRUE world-knowledge
wall. Owner discipline: a fair test of a WEAK impl proves THAT setup failed, not the capability.

LEVER 1 (event-centrality situation gate, +0.013): of the >=2 head-match ties it must break, is the gold
antecedent even IN the event memory (recoverable) or absent (event-EXTRACTION miss = weak impl)? And is the
extraction positional (not SRL)?
LEVER 2 (presence/locality, capped ~0.26): is the loss RECALL (antecedent left the recency window) -- and
would a SPATIAL/entrance-based presence (present from first mention until a gap>G, not last-K-sentences) keep
it in view? Compare entrance-presence vs recency-window candidate counts + antecedent-retention.
LEVER 3 (relational binder, +0.0006): the KEY trace. My prototype handled ONLY possessive-PRONOUN role->role
(the small kinship slice). The brain establishes relations by APPOSITION ("Mr. Bennet, her father") and
GENITIVE ("Elizabeth's father"), binding role-descriptions to NAMED entities -- which is the name_antecedent
slice (19%) my prototype never targeted. Measure the STRUCTURE available across role-descriptions
(apposition-adjacent-name / genitive / possessive-pronoun / bare) so we know how much a PROPER relational
binder could reach vs the weak one.

Glass-box, NO LLM. hdlab READ-only. ASCII. own dir.
Run: .venv/Scripts/python.exe experiments/exp_commonnoun_prototype_signal_trace_v1.py --self-test
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import argparse, glob, json, time
from collections import defaultdict
from datetime import datetime, timezone

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.coref import parse_litbank_conll, load_name_gender
from hdlab.scene_segment import parse_conll_sentences
import experiments.exp_commonnoun_coref_diagnostic_v1 as DIAG
import experiments.exp_commonnoun_referent_linker_v1 as LK
import experiments.exp_commonnoun_linktype_decomposition_v1 as DEC

CONLL_DIR = os.path.join(_REPO, "data/litbank/coref_conll")
OUT_DIR = os.path.join(_REPO, "data/exp_commonnoun_prototype_signal_trace_v1")
head_lemma = DIAG.head_lemma
is_name = DIAG.is_name
POSS = {"her", "hers", "his", "their", "my", "your", "its", "our", "whose"}


def _role_structure(m, ms_by_sent, gaz):
    """Classify a role-description mention by the RELATIONAL STRUCTURE available to bind it:
    possessive_pronoun / genitive / apposition(adjacent name) / of_phrase / bare."""
    span = [w.lower() for w in m.get("span_toks", [m["head"]])]
    if span and span[0] in POSS:
        return "possessive_pronoun"
    # genitive inside span ("elizabeth 's father") or 'of' phrase ("father of elizabeth")
    if any("'" in w for w in span) or "of" in span:
        return "genitive_or_of"
    # apposition: a NAME mention ends within 2 tokens before this mention's start, same sentence
    si = m["sent_idx"]; ws = m["wtok_start"]
    for nm in ms_by_sent.get(si, []):
        if nm is m or nm["is_pronoun"] or not is_name(nm, gaz):
            continue
        nm_end = nm["wtok_start"] + max(0, nm["gtok_end"] - nm["gtok_start"])
        if 0 <= ws - nm_end <= 2:                    # name immediately precedes (comma apposition)
            return "apposition_name"
        if 0 <= nm["wtok_start"] - (ws + len(span)) <= 2:   # name immediately follows ("her father, Mr B")
            return "apposition_name"
    return "bare"


def trace_relational(docs_paths, gaz):
    """The relational STRUCTURE ceiling: across ROLE-description mentions whose gold link is relational
    (kinship_role OR name_antecedent -- both need a relation), how much STRUCTURE is available, and how much
    my possessive-only prototype could reach vs a PROPER apposition+genitive binder."""
    struct = defaultdict(int)
    struct_by_cat = {"kinship_role": defaultdict(int), "name_antecedent": defaultdict(int)}
    n = 0
    for path in docs_paths:
        ms, _ = parse_litbank_conll(path, name_gender_map=gaz)
        ms_by_sent = defaultdict(list)
        for m in ms:
            ms_by_sent[m["sent_idx"]].append(m)
        noms = sorted([m for m in ms if not m["is_pronoun"]], key=lambda m: m["midx"])
        prior = defaultdict(list)
        for m in noms:
            hl = head_lemma(m["head"]); person = LK.person_synset(hl) is not None or is_name(m, gaz)
            pri = prior.get(m["cluster"], [])
            if (not is_name(m, gaz)) and person and pri and hl in DEC.KINSHIP_ROLE:
                ante = pri[-1]; ahl = head_lemma(ante["head"])
                if ahl == hl or DEC.wn_bridge(hl, ahl):
                    prior[m["cluster"]].append(m); continue
                cat = "name_antecedent" if is_name(ante, gaz) else "kinship_role"
                s = _role_structure(m, ms_by_sent, gaz)
                struct[s] += 1; struct_by_cat[cat][s] += 1; n += 1
            prior[m["cluster"]].append(m)
    return {"n_role_links": n, "structure_overall": dict(struct),
            "structure_by_category": {c: dict(d) for c, d in struct_by_cat.items()}}


def trace_presence(docs_paths, gaz, W_recency=8, gap_exit=6):
    """LEVER-2 loss: is presence loss RECALL (antecedent outside the window)? Compare recency-window vs an
    ENTRANCE-based presence (present from first mention until a gap>gap_exit sentences) -- does spatial/
    entrance presence RETAIN the antecedent better while keeping candidates fewer?"""
    rec_ante_in = rec_cand = spans_ante_in = spans_cand = n = 0
    for path in docs_paths:
        ms, _ = parse_litbank_conll(path, name_gender_map=gaz)
        by_cluster = defaultdict(list)
        for m in ms:
            by_cluster[m["cluster"]].append(m)
        cl_g = {c: next((mm.get("gender") or mm.get("name_gender") for mm in cms
                         if (mm.get("gender") or mm.get("name_gender")) in ("masc", "fem")), None)
                for c, cms in by_cluster.items()}
        cl_person = {c: any((not mm["is_pronoun"]) and (LK.person_synset(head_lemma(mm["head"])) is not None
                                                        or is_name(mm, gaz)) for mm in cms)
                     for c, cms in by_cluster.items()}
        noms = sorted([m for m in ms if not m["is_pronoun"]], key=lambda m: m["midx"])
        prior = defaultdict(list); cl_last = {}; cl_first = {}
        for m in noms:
            hl = head_lemma(m["head"]); g = m.get("gender") or m.get("name_gender"); si = m["sent_idx"]
            person = LK.person_synset(hl) is not None or is_name(m, gaz)
            pri = prior.get(m["cluster"], [])
            if (not is_name(m, gaz)) and person and pri:
                ante_c = pri[-1]["cluster"]
                # recency-window compatibles
                rec = [c for c, ls in cl_last.items() if cl_person.get(c) and (si - ls) <= W_recency
                       and LK._gender_ok(g, cl_g.get(c))]
                # entrance-presence compatibles: present iff mentioned & last gap <= gap_exit (still on stage)
                pres = [c for c, ls in cl_last.items() if cl_person.get(c) and (si - ls) <= gap_exit
                        and LK._gender_ok(g, cl_g.get(c))]
                if len(rec) >= 2:
                    n += 1
                    rec_ante_in += int(ante_c in rec); rec_cand += len(rec)
                    spans_ante_in += int(ante_c in pres); spans_cand += len(pres)
            prior[m["cluster"]].append(m)
            if person:
                cl_last[m["cluster"]] = si; cl_first.setdefault(m["cluster"], si)
    return {"n_ambiguous": n,
            "recency_window": {"ante_retained": round(rec_ante_in / max(1, n), 4),
                               "mean_candidates": round(rec_cand / max(1, n), 2)},
            "entrance_presence": {"ante_retained": round(spans_ante_in / max(1, n), 4),
                                  "mean_candidates": round(spans_cand / max(1, n), 2)}}


def run(n=None):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    paths = sorted(glob.glob(os.path.join(CONLL_DIR, "*.conll")))
    if n:
        paths = paths[:n]
    gaz = load_name_gender()
    res = {"n_docs": len(paths), "relational": trace_relational(paths, gaz),
           "presence": trace_presence(paths, gaz), "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor": "commonnoun_prototype_signal_trace_v1", "results": res,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def _print(res):
    print("=" * 92)
    print("PROTOTYPE SIGNAL-LOSS TRACE (%d docs)" % res["n_docs"])
    r = res["relational"]
    print("\nLEVER 3 (RELATIONAL) -- structure available across %d role-description links:" % r["n_role_links"])
    tot = max(1, r["n_role_links"])
    for s, c in sorted(r["structure_overall"].items(), key=lambda kv: -kv[1]):
        print("    %-20s %5d  (%.3f)" % (s, c, c / tot))
    print("  by category (kinship_role = role->role ; name_antecedent = role->NAME, the apposition slice):")
    for cat, d in r["structure_by_category"].items():
        nc = sum(d.values())
        print("    %-16s n=%-4d %s" % (cat, nc, {k: "%.2f" % (v / max(1, nc)) for k, v in d.items()}))
    p = res["presence"]
    print("\nLEVER 2 (PRESENCE) on %d ambiguous links -- recency-window vs entrance-presence:" % p["n_ambiguous"])
    print("    recency_window   : ante_retained %.3f  mean_candidates %.2f"
          % (p["recency_window"]["ante_retained"], p["recency_window"]["mean_candidates"]))
    print("    entrance_presence: ante_retained %.3f  mean_candidates %.2f"
          % (p["entrance_presence"]["ante_retained"], p["entrance_presence"]["mean_candidates"]))
    print("=" * 92)


def self_test():
    res = run(n=8)
    assert res["relational"]["n_role_links"] > 0
    print("[self-test] PASS (%d role links over 8 docs)" % res["relational"]["n_role_links"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--n", type=int, default=None)
    a = ap.parse_args()
    if a.self_test:
        self_test(); return
    _print(run(n=a.n))


if __name__ == "__main__":
    main()
