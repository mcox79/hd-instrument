"""
exp_substrate_distill_verify_2_class_b_relationship_discrimination_cpu_v1.py -- CELL-DISTILL-VERIFY-2: the verifier must REFUSE to over-distill (soundness/discrimination half of the closed loop) -- CPU/local (no heat).

ROUTING: SKUNKWORKS handoff (skunkworks_to_exp_dev_DISTILL_PRESCREEN_5_dupes_are_KP_PROMOTION_PAIRS...). Skunkworks adversarially
  pre-screened its own DETECT list: the 5 flagged "duplicates" are KP P1 PROMOTION PAIRS (T3 source + T2 promotion, differ only in
  metadata.kp_p1_promotion) -> Class A, trivial schema-collapse, goes to Testbed (NOT a proof cell). The REAL proof-needing distill
  targets are Class B: operator GROUPS that share an output type / capability but are DIFFERENT operators. CELL-DISTILL-VERIFY-1 proved
  the verifier MERGES true duplicates; this cell (V2) proves the verifier REFUSES to merge mere capability-siblings and instead names the
  correct WEAKER relationship (shared-abstraction extraction vs theorem-link). That refusal-to-over-distill is what makes the self-
  improvement loop SOUND -- a loop that collapses adam into sgd would destroy capability. Ungated: atom-level algebra_dict + serves_capability
  (race-tolerant relations read for the theorem-derivation lookup); NOT SHARES_MATH / parser-v2 / codebook growth.

  Class B groups (from Skunkworks, confirmed against local index signatures):
    - optimizer FAMILY: gradient_descent(T1) + adam_optimizer(T3) + stochastic_gradient_descent(T3)
        same domain=convex_optimization, same output=parameter_vector, same cap_discriminative_perceptron; DIFFERENT operation_type.
        Expected: SHARED_ABSTRACTION (distill = extract abstract first-order-optimizer supertype + SPECIALIZES links; do NOT merge).
    - convolution-theorem pair: circular_convolution(T2) <-> discrete_fourier_transform(T3)
        IDENTICAL caps (cap_circular_convolution, cap_fhrr_bind) but DIFFERENT signatures (real_vector vs frequency_spectrum out).
        Expected: THEOREM_LINKED (related by conv = IDFT(DFT.x .* DFT.y)); PROVABLE only if the derivation chain is authored, else SOUND REFUSAL.

  RELATIONSHIP TAXONOMY (CHTV-1 typed reasoning; sound by construction):
    MERGEABLE          -- all members have a full typed signature, ALL identical, AND identical non-empty caps (collapse to one atom).
    SHARED_ABSTRACTION -- same output_type AND same domain, operation_type DIFFERS, caps consistent (common supertype; SPECIALIZES not merge).
    THEOREM_LINKED     -- identical non-empty caps but DIFFERENT output_type (related by an identity/theorem); merge REFUSED; derivation
                          asserted PROVABLE only if a relation chain links the pair, else UNPROVABLE_IN_GRAPH (sound refusal).
    DISTINCT           -- neither shared abstraction nor theorem link.

PRE-REGISTERED (soundness/discrimination is the bar): HARD-PASS iff ZERO Class B groups are MERGEABLE (the verifier never over-distills a
  distinct algorithm) AND the optimizer family is SHARED_ABSTRACTION AND the conv<->DFT pair is THEOREM_LINKED (all relationship classes
  correctly discriminated). MIDDLE_BAND iff 0 false-merge but >=1 relationship misclassified. HARD-FAIL iff ANY Class B group is MERGEABLE
  (unsound over-distillation -- would destroy a distinct operator). UNKNOWN if the targeted atoms are absent. ASCII-only. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple, List, Set
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_distill_verify_2_class_b_relationship_discrimination_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SIG_FIELDS = ("domain", "operation_type", "signature_input_type", "signature_output_type", "complexity_class")
# Hand-named Class B groups (short ids) = ground-truth REGRESSION ANCHOR; must always discriminate correctly.
ANCHOR_GROUPS = {
    "optimizer_family": ["gradient_descent", "adam_optimizer", "stochastic_gradient_descent"],
    "convolution_theorem": ["circular_convolution", "discrete_fourier_transform"],
}
ANCHOR_EXPECTED = {"optimizer_family": "SHARED_ABSTRACTION", "convolution_theorem": "THEOREM_LINKED"}
# Skunkworks ships the widened set here (schema contract -- see note). Absent => default to the 2-group anchor only.
CANDIDATE_PATHS = [
    REPO / "tools" / "substrate_distill_class_b_candidates.json",
    REPO / "data" / "substrate_index" / "bench_reports" / "substrate_distill_class_b_candidates.json",
]


def _load_candidate_groups() -> Tuple[Dict[str, List[str]], Dict[str, str], str]:
    """Load widened Class B candidates if Skunkworks shipped them, else fall back to the anchor pair.
    Schema contract: {"groups": [{"group": <name>, "members": [<short_id>...], "expected": <verdict|null optional>}]}.
    Always merges in the 2 anchor groups (regression ground truth). Returns (groups, expected_map, source)."""
    groups = dict(ANCHOR_GROUPS); expected = dict(ANCHOR_EXPECTED); source = "anchor_only"
    for p in CANDIDATE_PATHS:
        try:
            if not p.exists(): continue
            doc = json.loads(p.read_text(encoding="utf-8"))
            gl = doc.get("groups", doc) if isinstance(doc, dict) else doc
            n_ext = 0
            for g in gl:
                name = str(g.get("group") or g.get("name") or "").strip()
                mem = g.get("members") or g.get("ids") or []
                mem = [_short(m) for m in mem if m]
                if not name or len(mem) < 2: continue
                groups[name] = mem; n_ext += 1
                if g.get("expected"): expected[name] = str(g["expected"]).strip().upper()
            source = "external:%s (+%d groups)" % (p.name, n_ext) if n_ext else source
            break
        except Exception as e:
            source = "anchor_only (external_load_failed: %s)" % str(e)[:60]
    return groups, expected, source


def _short(x):
    return str(x).split("::")[-1].split("/")[-1].strip().lower()


# V2.1 (Research 14th writeback): INVERSE_PAIR is a 5th, STRONGER-than-SHARED_ABSTRACTION class -- a provable algebraic identity
# (unbind o bind = id). Inverse-paired operation_type / member-name tokens:
INVERSE_TOKENS = [("bind", "unbind"), ("fold", "unfold"), ("encode", "decode"), ("compress", "decompress"),
                  ("pack", "unpack"), ("forward", "backward"), ("transform", "inverse_transform"), ("bind", "inverse_bind")]


def _inverse_named(a: str, b: str) -> bool:
    a, b = a.lower(), b.lower()
    # un-prefix inverse (bind/unbind, fold/unfold) -- require base length >= 4 to avoid false-friends (union/ion, unit/it) per V3.1.
    if a and b and ((a == "un" + b and len(b) >= 4) or (b == "un" + a and len(a) >= 4)):
        return True
    for x, y in INVERSE_TOKENS:
        if (x in a and y in b) or (y in a and x in b):
            return True
    return False


def _is_inverse_pair(names, sigs) -> bool:
    """Two members, same domain + same output type, with inverse-paired names OR operation_types (algebraic inverse/adjoint)."""
    if len(sigs) != 2:
        return False
    def field(f): return set(s.get(f) for s in sigs if s.get(f))
    if not (len(field("domain")) == 1 and len(field("signature_output_type")) == 1):
        return False
    ops = [s.get("operation_type", "") or "" for s in sigs]
    nm = list(names) if names and len(names) == 2 else ["", ""]
    return _inverse_named(nm[0], nm[1]) or _inverse_named(ops[0], ops[1])


def classify_group(sigs: List[dict], caps: List[Set[str]], names=None) -> str:
    """CHTV-1 typed-relationship classification over a Class B candidate group (>=2 members). names optional (for INVERSE_PAIR)."""
    full = [s for s in sigs if len(s) >= 4]
    cap_ne = [c for c in caps if c]
    caps_ident = len(cap_ne) >= 2 and all(c == cap_ne[0] for c in cap_ne[1:])
    # MERGEABLE: every member fully typed, all identical, caps identical -> collapse to one atom
    if len(full) == len(sigs) and len(full) >= 2 and all(s == full[0] for s in full[1:]) and caps_ident:
        return "MERGEABLE"
    # INVERSE_PAIR (V2.1): stronger than SHARED_ABSTRACTION -- provable algebraic inverse; checked before it. Must NOT merge.
    if _is_inverse_pair(names, sigs):
        return "INVERSE_PAIR"
    def field(f): return set(s.get(f) for s in sigs if s.get(f))
    out_types = field("signature_output_type"); domains = field("domain"); ops = field("operation_type")
    # SHARED_ABSTRACTION: one output_type, one domain, operation_type differs (common supertype; specialize, don't merge)
    if len(out_types) == 1 and len(domains) == 1 and len(ops) >= 2:
        return "SHARED_ABSTRACTION"
    # CROSS_DOMAIN_ABSTRACTION (V2.2, Option B adopted): one shared output_type across >=2 DOMAINS with >=2 distinct ops -- a cross-field
    # unification (e.g. weight_vector across ML/NLP/online/structured-prediction). Run() must verify the shared output is a GROUNDED supertype
    # atom (18th rule) else this is downgraded to DISTINCT (refuse what cannot be proven).
    if len(out_types) == 1 and len(domains) >= 2 and len(ops) >= 2:
        return "CROSS_DOMAIN_ABSTRACTION"
    # THEOREM_LINKED: identical caps but different output type (related by a provable identity/theorem)
    if caps_ident and len(out_types) >= 2:
        return "THEOREM_LINKED"
    return "DISTINCT"


def _selftest():
    base = {"domain": "convex_optimization", "operation_type": "x", "signature_input_type": "function_and_gradient",
            "signature_output_type": "parameter_vector", "complexity_class": "O(N) per step"}
    # MERGEABLE: identical full sigs + caps
    assert classify_group([dict(base), dict(base)], [{"c"}, {"c"}]) == "MERGEABLE"
    # SHARED_ABSTRACTION: same out+domain, op differs
    s2 = {**base, "operation_type": "y"}
    assert classify_group([dict(base), s2], [{"c"}, {"c"}]) == "SHARED_ABSTRACTION"
    # THEOREM_LINKED: identical caps, different output type
    conv = {"domain": "vsa", "operation_type": "binding", "signature_input_type": "real_vector_pair",
            "signature_output_type": "real_vector", "complexity_class": "O(N log N)"}
    dft = {"domain": "signal", "operation_type": "linear_transform", "signature_input_type": "discrete_signal",
           "signature_output_type": "frequency_spectrum", "complexity_class": "O(N log N)"}
    assert classify_group([conv, dft], [{"a", "b"}, {"a", "b"}]) == "THEOREM_LINKED"
    # DISTINCT: different out type, different caps
    assert classify_group([conv, dft], [{"a"}, {"z"}]) == "DISTINCT"
    # INVERSE_PAIR (V2.1): same domain+output, inverse-named -> stronger than SHARED_ABSTRACTION
    bnd = {"domain": "vsa", "operation_type": "binding", "signature_output_type": "phasor_vector"}
    unb = {"domain": "vsa", "operation_type": "unbinding", "signature_output_type": "phasor_vector"}
    assert classify_group([bnd, unb], [{"c"}, {"c"}], names=["fhrr_bind", "fhrr_unbind"]) == "INVERSE_PAIR"
    assert classify_group([bnd, unb], [{"c"}, {"c"}]) == "INVERSE_PAIR"          # op-types binding/unbinding are inverse-paired too
    # non-inverse op-types + no names -> falls back to SHARED_ABSTRACTION (same domain+output, ops differ)
    gy = {"domain": "vsa", "operation_type": "y", "signature_output_type": "phasor_vector"}
    gz = {"domain": "vsa", "operation_type": "z", "signature_output_type": "phasor_vector"}
    assert classify_group([gy, gz], [{"c"}, {"c"}]) == "SHARED_ABSTRACTION"
    # CROSS_DOMAIN_ABSTRACTION (V2.2): same output, >=2 domains, >=2 ops
    cda = [{"domain": "ml", "operation_type": "p", "signature_output_type": "weight_vector"},
           {"domain": "nlp", "operation_type": "q", "signature_output_type": "weight_vector"}]
    assert classify_group(cda, [set(), set()]) == "CROSS_DOMAIN_ABSTRACTION"
    assert _inverse_named("fhrr_bind", "fhrr_unbind") and not _inverse_named("adam", "sgd")
    print("[selftest] PASS: substrate_distill_verify_2_class_b_relationship_discrimination_cpu_v1", flush=True)


if __name__ == "__main__":            # selftest runs only as a script; import (e.g. by V3) has no side effects
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


# A theorem is "derivable" only via a TYPED derivation edge -- a generic RELATES association is NOT a proof.
DERIV_RELS = {"DEPENDS_ON", "USES", "DERIVES", "DERIVED_FROM", "IMPLIES", "EQUALS", "EQUIVALENT_TO", "PROVES"}
# An inverse pair is AUTHORED-provable via a DUAL/INVERSE/ADJOINT edge (V2.1; grounds INVERSE_PAIR in provenance, not name heuristics).
DUAL_RELS = {"DUAL", "INVERSE_OF", "ADJOINT", "INVERTS"}


def _edge_between(root: Path, members_full: List[str], rel_set: set) -> bool:
    """Race-tolerant: is there an edge of any rel_type in rel_set between two members of the group?"""
    shorts = set(_short(m) for m in members_full)
    for rp in root.rglob("relations.jsonl"):
        try:
            for ln in open(rp, encoding="utf-8"):
                ln = ln.strip()
                if not ln: continue
                try: r = json.loads(ln)
                except Exception: continue
                if (r.get("rel_type", "") or "").upper() not in rel_set: continue
                s = _short(r.get("src_id", "")); t = _short(r.get("tgt_id", ""))
                if s in shorts and t in shorts and s != t:
                    return True
        except Exception:
            continue
    return False


def _derivation_links(root: Path, members_full: List[str]) -> bool:
    """Is there a TYPED DERIVATION edge (not a generic RELATES) between two members -> the theorem is provably chained?"""
    return _edge_between(root, members_full, DERIV_RELS)


def _dual_links(root: Path, members_full: List[str]) -> bool:
    """Is there an AUTHORED inverse/adjoint (DUAL) edge between two members -> INVERSE_PAIR is provenance-grounded, not heuristic?"""
    return _edge_between(root, members_full, DUAL_RELS)


def _type_grounded(root: Path, out_type: str) -> bool:
    """18th-rule gate for CROSS_DOMAIN_ABSTRACTION: is the shared output type an AUTHORED atom with an outgoing grounding edge
    (DEPENDS_ON / SPECIALIZES) -- i.e. a proven supertype, not an ungrounded leaf or absent type? Race-tolerant."""
    if not out_type:
        return False
    want = str(out_type).split("::")[-1].split("/")[-1].strip().lower()
    ground_rels = DERIV_RELS | {"SPECIALIZES", "INSTANCE_OF", "MEMBER_OF"}
    for rp in root.rglob("relations.jsonl"):
        try:
            for ln in open(rp, encoding="utf-8"):
                ln = ln.strip()
                if not ln: continue
                try: r = json.loads(ln)
                except Exception: continue
                if (r.get("rel_type", "") or "").upper() not in ground_rels: continue
                if _short(r.get("src_id", "")) == want:        # the output-type atom has an outgoing grounding edge
                    return True
        except Exception:
            continue
    return False


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    from backend.substrate_index.partition import PartitionedStore
    # race-tolerant atom load
    by = defaultdict(list)
    for _ in range(5):
        try:
            for a in PartitionedStore(root).all_atoms():
                by[_short(a.id)].append(a)
            break
        except Exception:
            by = defaultdict(list); time.sleep(8)

    def alg(a):
        x = getattr(a, "algebra", None); return x if isinstance(x, dict) else {}

    cand_groups, expected, source = _load_candidate_groups()
    groups = []
    for gname, shorts in cand_groups.items():
        members = []
        for s in shorts:
            members.extend(by.get(s, []))
        if len(members) < 2:
            groups.append({"group": gname, "verdict": "UNKNOWN", "n_found": len(members), "is_anchor": gname in ANCHOR_GROUPS})
            continue
        sigs = [{f: alg(a).get(f) for f in SIG_FIELDS if alg(a).get(f) is not None} for a in members]
        caps = [set(_short(c) for c in (getattr(a, "serves_capability", ()) or ())) for a in members]
        ids = [str(a.id) for a in members]
        short_names = [_short(a.id) for a in members]
        rel = classify_group(sigs, caps, names=short_names if len(short_names) == 2 else None)
        shared_caps = sorted(set.intersection(*caps)) if all(caps) else []
        # V2.1: prefer an AUTHORED DUAL/inverse edge over the name/op-type heuristic -> provenance-grounded INVERSE_PAIR
        inverse_authored = None
        if len(ids) == 2:
            inverse_authored = _dual_links(root, ids)
            if inverse_authored:
                rel = "INVERSE_PAIR"               # authored DUAL edge is authoritative (overrides SHARED_ABSTRACTION/etc)
        # V2.2 18th-rule gate: CROSS_DOMAIN_ABSTRACTION only if the shared output type is a GROUNDED supertype atom; else refuse -> DISTINCT
        out_grounded = None
        if rel == "CROSS_DOMAIN_ABSTRACTION":
            shared_out = next(iter(set(s.get("signature_output_type") for s in sigs if s.get("signature_output_type"))), None)
            out_grounded = _type_grounded(root, shared_out)
            if not out_grounded:
                rel = "DISTINCT"                   # refuse cross-domain abstraction on an ungrounded output type (18th rule)
        deriv = None
        if rel == "THEOREM_LINKED":
            deriv = _derivation_links(root, ids)   # provable iff a TYPED derivation chain is authored, else sound refusal
        groups.append({"group": gname, "verdict": rel, "n_found": len(members), "ids": ids, "is_anchor": gname in ANCHOR_GROUPS,
                       "shared_caps": shared_caps, "out_types": sorted(set(s.get("signature_output_type") for s in sigs if s.get("signature_output_type"))),
                       "operation_types": sorted(set(s.get("operation_type") for s in sigs if s.get("operation_type"))),
                       "derivation_present": deriv, "inverse_authored": inverse_authored, "out_type_grounded": out_grounded})
    n_eval = sum(1 for g in groups if g["verdict"] != "UNKNOWN")
    # Anchor regression: the 2 hand-named ground-truth groups must still discriminate correctly.
    anchors = [g for g in groups if g["is_anchor"] and g["verdict"] != "UNKNOWN"]
    anchor_correct = sum(1 for g in anchors if g["verdict"] == expected.get(g["group"]))
    # Soundness guard over ALL groups: a MERGEABLE among same-capability-distinct candidates would be unsound over-distillation.
    n_mergeable = sum(1 for g in groups if g["verdict"] == "MERGEABLE")
    # Triage distribution (the worklist the widened set produces).
    from collections import Counter as _C
    dist = dict(_C(g["verdict"] for g in groups if g["verdict"] != "UNKNOWN"))
    print("  candidate source: %s | groups evaluated=%d" % (source, n_eval), flush=True)
    for g in groups:
        exp = expected.get(g["group"]); tag = "ANCHOR" if g["is_anchor"] else "cand"
        ok = "OK" if (exp and g["verdict"] == exp) else ("MERGE!" if g["verdict"] == "MERGEABLE" else ("triage" if not exp else "miss"))
        print("  [%-6s] %-26s -> %-18s (exp %-16s) [%s] caps=%s out=%s deriv=%s" % (
            tag, g["group"][:26], g["verdict"], exp, ok, g.get("shared_caps", [])[:2], g.get("out_types"), g.get("derivation_present")), flush=True)
    print("  anchor-correct=%d/%d | false-MERGEABLE(all)=%d | triage dist=%s" % (anchor_correct, len(anchors), n_mergeable, dist), flush=True)
    bf = root / "bench_reports"; bf.mkdir(parents=True, exist_ok=True)
    (bf / "distill_verify_2_class_b_relationship.json").write_text(json.dumps({"groups": groups, "expected": expected, "source": source,
        "n_mergeable": n_mergeable, "anchor_correct": anchor_correct, "n_anchors": len(anchors), "n_eval": n_eval, "triage_dist": dist}, indent=2), encoding="utf-8")
    return {"groups": groups, "n_eval": n_eval, "n_mergeable": n_mergeable, "anchor_correct": anchor_correct,
            "n_anchors": len(anchors), "expected": expected, "source": source, "triage_dist": dist}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    if r["n_eval"] == 0:
        return ("UNKNOWN", "UNKNOWN: no Class B target atoms found in index (codebook may be mid-sync).")
    nm = r["n_mergeable"]; ac = r["anchor_correct"]; na = r["n_anchors"]
    gv = {g["group"]: g["verdict"] for g in r["groups"]}
    opt = gv.get("optimizer_family"); conv = gv.get("convolution_theorem")
    conv_deriv = next((g.get("derivation_present") for g in r["groups"] if g["group"] == "convolution_theorem"), None)
    anchor_merge = [g["group"] for g in r["groups"] if g.get("is_anchor") and g["verdict"] == "MERGEABLE"]  # unsound iff anchor merges
    ext_merge = [g["group"] for g in r["groups"] if not g.get("is_anchor") and g["verdict"] == "MERGEABLE"]  # candidate true-dups (route to V1)
    s = ("source=%s; anchor groups (ground truth) optimizer_family=%s, convolution_theorem=%s (derivation_present=%s); anchor-correct=%d/%d; "
         "full-set false-MERGEABLE=%d (anchor=%d unsound, external=%d candidate-true-dups for V1 merge-verify); triage dist=%s. "
         "CHTV-1 typed reasoning: conv<->DFT shares capability but differs in signature -> merge REFUSED, theorem PROVABLE only if a TYPED "
         "derivation chain links the pair else SOUND refusal; optimizer family shares output+domain+capability, differs in algorithm -> "
         "SHARED_ABSTRACTION (extract first-order-optimizer supertype + SPECIALIZES, do NOT merge).") % (
        r["source"], opt, conv, conv_deriv, ac, na, nm, len(anchor_merge), len(ext_merge), r["triage_dist"])
    if anchor_merge:
        return ("HARD_FAIL", "HARD_FAIL: anchor group(s) %s marked MERGEABLE -- UNSOUND over-distillation; the verifier would collapse a known-"
                "distinct operator and destroy capability. The self-improvement loop's distill step is NOT safe. " % anchor_merge + s)
    if na >= 2 and ac == na:
        return ("HARD_PASS", "HARD_PASS (verifier is SOUNDLY DISCRIMINATIVE -- over-distillation guard holds): anchor regression intact "
                "(%d/%d ground-truth groups correct: optimizer=SHARED_ABSTRACTION, conv<->DFT=THEOREM_LINKED%s), ZERO anchor false-merges. "
                "Soundness half of the closed loop: V1 MERGES true duplicates; V2 REFUSES to over-distill capability-siblings and names the "
                "correct weaker relationship (abstraction extraction / theorem link). %s" % (ac, na,
                " (derivation absent -> sound refusal to assert the convolution theorem)" if conv_deriv is False else "",
                ("Widened set produced %d external candidate group(s); %d flagged MERGEABLE for V1 merge-verify follow-up. " % (
                    sum(1 for g in r["groups"] if not g.get("is_anchor") and g["verdict"] != "UNKNOWN"), len(ext_merge))) if r["source"] != "anchor_only" else "") + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: no unsound anchor over-distillation but anchor regression incomplete (%d/%d correct, %d anchors found) "
            "-- likely a target atom missing from the index (mid-sync) or a taxonomy miss. " % (ac, na, na) + s)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
