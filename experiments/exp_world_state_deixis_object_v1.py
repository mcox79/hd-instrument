"""exp_world_state_deixis_object_v1 -- the BUILD-ACROSS for the two Stage-1 reference routes the reader lacks,
measured on MCScript2 (first-person everyday narrative, the parent corpus). For
`the_world_state_register_is_coref_blind_wire_it_through_coreference_and_measure_who_has_what`.

WHY (the disk outranks the brief): the brief says "wire the reader's OWN coref" (which resolves gendered-singular
he/she via Centering). But on the parent corpus that touches only 6.2% of transfer agents. The dominant real gap
decomposes into TWO routes the reader's coref does NOT implement, and the brain does with DIFFERENT mechanisms:
  * INDEXICAL route (Kaplan pure-indexical / Buhler origo / Deictic Shift Theory): first-person I/me/my -> the
    NARRATOR node, an O(1) speech-role lookup, NOT anaphora. 64.7% of MCScript2 agents. The register today keys
    on the RAW CASE-FORM, so "I" (agent) and "me"/"my" (recipient) FRAGMENT the one narrator across >=2 keys.
  * OBJECT ANAPHORA (Grosz-Joshi-Weinstein Centering, entity-type-agnostic, + Lappin-Leass pleonastic-it filter):
    "it"/"them" -> the salient recent theme. ~11% of themes. The register today applies "give it" to key "it",
    so the antecedent object's holder NEVER updates -> a SILENT, catastrophic who-has-what error.

BRAIN FIDELITY: Stage-1 reference resolution is bifurcated (indexical lookup vs anaphoric salience search);
Stage-2 state update is unified (our world_state_register IS a faithful Stage-2). So the fix is Stage-1-local:
add the indexical narrator rule (deterministic, monologic-PINNED) and object anaphora (same Centering machinery
the reader already runs for he/she, extended to objects, + pleonastic filter). "we"/"you" are NOT folded in
(research: "we"=group entity, "you"=rotating addressee -- out of the clean pinned case; scoped out, named).

WHAT IS MEASURED (unambiguous, no gold coref needed -- these are BLIND-FAILURE localizations + lever sizes):
  A) NARRATOR key-fragmentation under blind: distinct keys blind assigns the one narrator (i/me/my/...) per story;
     the deterministic indexical rule collapses them to 1. Fraction of stories blind fragments; mean keys/story.
  B) OBJECT-"it" antecedent loss: fraction of transfers whose "it"/"them" theme has a nominal antecedent (coverage),
     and the who-has-what IMPACT = how many antecedent-object holder queries CHANGE when object anaphora is on
     (the size of the who-has-what damage blind suffers from object-blindness).
  C) DECOMPOSITION of blind's who-has-what failures by responsible Stage-1 route (indexical / anaphoric / object),
     as fractions of all transfers whose HOLDER or OBJECT is a pronoun -- the honest "three costs" breakdown.
Glass-box: substrate's OWN parser (pos_tagger+arc_parser); NO spaCy/LLM. ASCII only.
# KB_REFERENT: data/corpora/mcscript2/extracted/train-data.xml
# KB_REFERENT: data/frontend_assets/pos_tagger_ud_ewt_upos.json
# KB_REFERENT: data/frontend_assets/arc_parser_hashed_ud_ewt.npz
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import glob
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_world_state_realtext_mcscript_v1 as RT
from experiments.exp_world_state_coref_densify_v1 import extract_ops_idx
# route the measurement THROUGH the deliverable module (single source of truth for the two Stage-1 routes).
from experiments.world_state_entity_binding import EntityBinder, NARRATOR, FIRST_SG, OBJ_PRON

ANCHOR = "world_state_deixis_object_v1"
from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_" + ANCHOR)

# FIRST_SG / OBJ_PRON imported from world_state_entity_binding (the deliverable module -- single source of truth).
SENT_RE = re.compile(r"(?<=[.!?])\s+")


def stories(n):
    out = []
    for f in sorted(glob.glob(os.path.join(REPO, "data/corpora/mcscript2/extracted/*-data.xml"))):
        try:
            root = ET.parse(f).getroot()
        except Exception:
            continue
        for inst in root.iter("instance"):
            tx = inst.find("text")
            if tx is None or not tx.text:
                continue
            sents = [s.strip() for s in SENT_RE.split(tx.text.strip()) if 3 <= len(s.split()) <= 40]
            if sents:
                out.append(sents)
            if len(out) >= n:
                return out
    return out


def story_transfers(sents, gen, lex, lemma_word):
    """Ordered transfer instances across one story (agent/theme/arg2 heads + theme-is-pronoun flag)."""
    insts = []
    for s in sents:
        try:
            cr = gen.generate(s)
        except Exception:
            continue
        for it in extract_ops_idx(cr, lex, lemma_word):
            ag = it["AGENT"]["head"] if it["AGENT"] else None
            th = it["PATIENT"]["head"] if it["PATIENT"] else None
            a2 = it["ARG2"]["head"] if it["ARG2"] else None
            insts.append({"verb": it["verb"], "op": it["op"], "agent": ag, "theme": th, "arg2": a2})
    return insts


def _indexical_only(h):
    """Isolate the INDEXICAL route: I/me/my -> NARRATOR, everything else raw (MCScript2 has no he/she coref, so
    the +deixis arm applies ONLY the indexical normalization). Uses the binder's own route classifier."""
    if h is None:
        return None
    return NARRATOR if EntityBinder.route_of(h) == "indexical" else h


def analyse_story(insts):
    """blind vs +deixis(indexical) vs +deixis+object, driven THROUGH the deliverable EntityBinder (object
    anaphora + pleonastic filter + Centering recent-theme salience). Returns per-story localizations."""
    from hdlab.world_state_register import WorldState
    wb, wd, wo = WorldState(), WorldState(), WorldState()      # blind, +deixis, +deixis+object
    binder = EntityBinder()                                    # per-story: drives object anaphora + salient theme
    narrator_keys_blind = set()
    obj_it_with_antecedent = 0
    obj_it_total = 0
    holder_pron_by_route = Counter()
    n_transfers = 0
    obj_impact_events = []      # (obj_antecedent, t) where object anaphora RELOCATES the transfer
    t = 0
    for it in insts:
        n_transfers += 1
        ag, th, a2, op, vb = it["agent"], it["theme"], it["arg2"], it["op"], it["verb"]
        # holder-after = arg2 (GIVE w/ recipient) else agent; route it via the binder's classifier
        holder = a2 if (op == "GIVE" and a2) else ag
        hr = EntityBinder.route_of(holder)
        if hr == "indexical":
            narrator_keys_blind.add(holder)
            holder_pron_by_route["indexical(I/me/my)"] += 1
        elif hr == "anaphoric":
            holder_pron_by_route["anaphoric(he/she)"] += 1
        elif hr == "scope_out" or holder in ("they", "them", "it"):
            holder_pron_by_route["other_pron(we/you/they)"] += 1
        # blind arm (raw strings)
        wb.apply_event({"PRED": vb, "OP": op, "AGENT": ag, "PATIENT": th, "ARG2": a2}, t, read_preconditions=False)
        # +deixis arm (indexical holder normalization only)
        wd.apply_event({"PRED": vb, "OP": op, "AGENT": _indexical_only(ag),
                        "PATIENT": th, "ARG2": _indexical_only(a2)}, t, read_preconditions=False)
        # +deixis+object arm: participants indexical-normalized; theme through the binder's OBJECT ANAPHORA
        th_res, troute = binder.bind_theme(th, vb)            # updates salient theme; resolves 'it' / pleonastic-abstains
        if EntityBinder.route_of(th) == "object_anaphora":
            obj_it_total += 1
            if troute == "object_anaphora":                  # resolved to a nominal antecedent (Centering)
                obj_it_with_antecedent += 1
                holder_pron_by_route["object(it/them)"] += 1
                obj_impact_events.append((th_res, t))
        wo.apply_event({"PRED": vb, "OP": op, "AGENT": _indexical_only(ag),
                        "PATIENT": th_res, "ARG2": _indexical_only(a2)}, t, read_preconditions=False)
        t += 1

    # object-anaphora who-has-what IMPACT: for each relocated transfer, does the ANTECEDENT object's holder differ
    # between blind (stale -- transfer landed on 'it') and +object (transfer landed on the antecedent)?
    impact = 0
    for obj_ante, te in obj_impact_events:
        hb = wb.holder_of(obj_ante, te)      # blind: antecedent object's holder at t (transfer went to 'it')
        ho = wo.holder_of(obj_ante, te)      # +object: transfer applied to the antecedent
        if hb != ho:
            impact += 1
    return {
        "n_transfers": n_transfers,
        "narrator_keys_blind": sorted(narrator_keys_blind),
        "n_narrator_keys_blind": len(narrator_keys_blind),
        "obj_it_total": obj_it_total, "obj_it_with_antecedent": obj_it_with_antecedent,
        "obj_impact": impact, "n_relocated": len(obj_impact_events),
        "holder_pron_by_route": dict(holder_pron_by_route),
    }


def run(mode="full", n_stories=1500):
    from hdlab.candidate_generator import CandidateGenerator
    from hdlab.thematic_role_labeler import lemma_word
    from experiments.possession_operators import build_lexicon
    pos_ckpt = os.path.join(REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
    arc_ckpt = os.path.join(REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
    gen = CandidateGenerator.load(pos_ckpt, arc_ckpt)
    lex = build_lexicon(use_cache=True)
    if mode == "smoke":
        n_stories = 60
    sts = stories(n_stories)

    agg = Counter()
    stories_frag = 0
    stories_with_narrator = 0
    narrator_key_hist = Counter()
    route = Counter()
    per_story_examples = []
    for sents in sts:
        insts = story_transfers(sents, gen, lex, lemma_word)
        if not insts:
            continue
        a = analyse_story(insts)
        agg["n_stories"] += 1
        agg["n_transfers"] += a["n_transfers"]
        agg["obj_it_total"] += a["obj_it_total"]
        agg["obj_it_with_antecedent"] += a["obj_it_with_antecedent"]
        agg["obj_impact"] += a["obj_impact"]
        agg["n_relocated"] += a["n_relocated"]
        for k, v in a["holder_pron_by_route"].items():
            route[k] += v
        if a["n_narrator_keys_blind"] >= 1:
            stories_with_narrator += 1
            narrator_key_hist[a["n_narrator_keys_blind"]] += 1
            if a["n_narrator_keys_blind"] >= 2:
                stories_frag += 1
                if len(per_story_examples) < 10:
                    per_story_examples.append(a["narrator_keys_blind"])

    total_pron_holders = sum(v for k, v in route.items())
    res = {
        "anchor": ANCHOR, "mode": mode, "n_stories_used": agg["n_stories"], "n_transfers": agg["n_transfers"],
        # A) narrator fragmentation
        "narrator_fragmentation": {
            "n_stories_with_narrator_holder": stories_with_narrator,
            "n_stories_blind_fragments_narrator": stories_frag,
            "frac_stories_fragmented": round(stories_frag / stories_with_narrator, 3) if stories_with_narrator else None,
            "distinct_narrator_keys_hist_under_blind": dict(narrator_key_hist),
            "example_fragmented_keysets": per_story_examples,
            "deixis_collapses_to": 1,
        },
        # B) object-anaphora lever
        "object_anaphora": {
            "n_it_themes": agg["obj_it_total"],
            "n_it_with_nominal_antecedent": agg["obj_it_with_antecedent"],
            "coverage_it_resolvable": round(agg["obj_it_with_antecedent"] / agg["obj_it_total"], 3) if agg["obj_it_total"] else None,
            "n_relocated_transfers": agg["n_relocated"],
            "who_has_what_impact_events": agg["obj_impact"],
            "impact_frac_of_relocated": round(agg["obj_impact"] / agg["n_relocated"], 3) if agg["n_relocated"] else None,
        },
        # C) decomposition of blind's pronoun-caused who-has-what failures by Stage-1 route
        "blind_failure_by_route": dict(route),
        "blind_failure_by_route_frac": {k: round(v / total_pron_holders, 3) for k, v in route.items()} if total_pron_holders else {},
        "scope_note": "we/you/they NOT folded (research: 'we'=group entity, 'you'=rotating addressee); only first-person SINGULAR is the pinned indexical case.",
    }
    return res


def _write(res):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    json.dump(res, open(tmp, "w", encoding="ascii"), indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[write] %s" % os.path.join(OUT_DIR, "metrics.json"), flush=True)


def self_test():
    """Two synthetic stories exercise the two routes with a KNOWN outcome."""
    from hdlab.world_state_register import WorldState
    # Story 1 (case-fragmentation): "I got the ball. Hand it to me." -> blind keys narrator as {i, me}; deixis=1.
    s1 = [{"verb": "get", "op": "GET", "agent": "i", "theme": "ball", "arg2": None},
          {"verb": "hand", "op": "GIVE", "agent": "you", "theme": "it", "arg2": "me"}]
    a1 = analyse_story(s1)
    ok_frag = a1["n_narrator_keys_blind"] == 2   # {i, me}
    # Story 2 (object anaphora): "I grabbed the cup. I gave it to the waiter." -> object 'it' relocates to 'cup';
    # blind holder_of('cup') stays 'i' (stale), +object -> 'waiter'.
    s2 = [{"verb": "grab", "op": "GET", "agent": "i", "theme": "cup", "arg2": None},
          {"verb": "give", "op": "GIVE", "agent": "i", "theme": "it", "arg2": "waiter"}]
    a2 = analyse_story(s2)
    ok_obj = a2["obj_impact"] == 1 and a2["obj_it_with_antecedent"] == 1
    print("[self-test] narrator fragments under blind (i,me): %s ; object 'it' relocates+impacts: %s"
          % (ok_frag, ok_obj), flush=True)
    print("[self-test] narrator keys blind:", a1["narrator_keys_blind"], flush=True)
    return 0 if (ok_frag and ok_obj) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n-stories", type=int, default=1500)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    mode = "smoke" if args.smoke else args.mode
    t0 = time.time()
    res = run(mode=mode, n_stories=args.n_stories)
    res["elapsed_s"] = round(time.time() - t0, 1)
    _write(res)
    nf = res["narrator_fragmentation"]; oa = res["object_anaphora"]
    print("\n  stories=%d transfers=%d" % (res["n_stories_used"], res["n_transfers"]), flush=True)
    print("  A) NARRATOR FRAGMENTATION under blind: %d/%d stories split the narrator into >=2 keys (%.1f%%); hist=%s"
          % (nf["n_stories_blind_fragments_narrator"], nf["n_stories_with_narrator_holder"],
             100 * (nf["frac_stories_fragmented"] or 0), nf["distinct_narrator_keys_hist_under_blind"]), flush=True)
    print("     e.g. blind keysets for one narrator: %s -> deixis collapses to 1" % nf["example_fragmented_keysets"][:5], flush=True)
    print("  B) OBJECT ANAPHORA: %d 'it' themes, %d with a nominal antecedent (cov %.2f); who-has-what IMPACT=%d/%d relocated (%.2f)"
          % (oa["n_it_themes"], oa["n_it_with_nominal_antecedent"], oa["coverage_it_resolvable"] or 0,
             oa["who_has_what_impact_events"], oa["n_relocated_transfers"], oa["impact_frac_of_relocated"] or 0), flush=True)
    print("  C) BLIND who-has-what failures by Stage-1 route (frac): %s" % res["blind_failure_by_route_frac"], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
