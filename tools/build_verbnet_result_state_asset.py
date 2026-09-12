"""Build the OFFLINE foundation asset for the result-state ARM of hdlab/force_dynamics_valence.py (strategy, pri-14, 2026-09-12).

WordNet SENSE KEY -> the RESULT STATE the patient is left in, read from VerbNet class semantics (nltk corpus, offline):
  MEMBER wn="<sense key>"  x  FRAME SEMANTICS predicates over the Patient at result(E)/end(E):
    harmed(...)                          -> "harmed"
    alive(...) negated                   -> "!alive"
    suffocate(...)                       -> "suffocate"
    degradation_material_integrity(...)  -> "degradation_material_integrity"
    manner(forceful) + contact(end(E))   -> "forceful_contact_end"   (forceful contact on the patient's body)
Only classes whose thematic roles include a Patient or Experiencer are read (the state must be the PATIENT's).
No verb list: every entry is (sense key -> class -> predicate); the organ values the STATE via the affect lexicon
(the innate nociceptive sign for forceful contact). Rebuild: python tools/build_verbnet_result_state_asset.py  (~5 s).
"""
import collections, datetime, json, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "data", "frontend_assets", "verbnet_result_state_v1.json")
NEG_STATE = ("harmed", "suffocate", "degradation_material_integrity")

def class_states(vn, cid):
    v = vn.vnclass(cid); preds = []
    for fr in v.findall("FRAMES/FRAME"):
        for p in fr.findall("SEMANTICS/PRED"):
            args = [(a.get("type"), a.get("value")) for a in p.findall("ARGS/ARG")]
            preds.append((p.get("value"), p.get("bool") == "!", args))
    roles = {val for _, _, a in preds for t, val in a if t == "ThemRole"}
    if not (roles & {"Patient", "Experiencer"}):
        return []
    out = []
    for n, neg, a in preds:
        if n in NEG_STATE and not neg: out.append(n)
        if n == "alive" and neg: out.append("!alive")
    forceful = any(n == "manner" and any(val == "forceful" for _, val in a) for n, neg, a in preds)
    contact_end = any(n == "contact" and not neg and any(val == "end(E)" for _, val in a) for n, neg, a in preds)
    if forceful and contact_end: out.append("forceful_contact_end")
    return sorted(set(out))

def main():
    from nltk.corpus import verbnet as vn
    states = collections.defaultdict(list); n_mem = n_keys = 0
    for cid in vn.classids():
        st = class_states(vn, cid)
        for m in vn.vnclass(cid).findall(".//MEMBERS/MEMBER"):
            n_mem += 1
            for k in (m.get("wn") or "").split():
                k = k.strip("?"); n_keys += 1
                if st: states[k].append([cid, m.get("name"), st])
    doc = {"source": f"VerbNet (nltk corpus at {vn.root}) MEMBER wn sense keys x class FRAME SEMANTICS; built {datetime.datetime.utcnow().isoformat()}Z",
           "n_members": n_mem, "n_sense_keys_seen": n_keys, "n_sense_keys_with_state": len(states),
           "state_names": ["harmed", "!alive", "suffocate", "degradation_material_integrity", "forceful_contact_end"],
           "states": {k: v for k, v in sorted(states.items())}}
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, sort_keys=False)
    print(f"wrote {OUT}: members={n_mem} keys={n_keys} keys_with_state={len(states)}")

if __name__ == "__main__":
    main()
