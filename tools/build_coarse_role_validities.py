"""Learn the CUE VALIDITIES of the Competition-Model coarse role labeler (hdlab.graded_role_assigner.coarse_roles) from a
training treebank -- the brain's cue strengths are learned from experience as cue VALIDITY (MacWhinney, Bates & Kliegl
1984: availability x reliability), never hand-set. v2 (2026-09-12): every cue (config = head-class x order, voice_order,
prep, cop, case, post_rank) takes a categorical VALUE; for each value the strength toward each role is
    strength(value -> role) = log P(role | cue value)      (add-0.5 smoothed over the 6 roles)
plus the role prior log P(role). v3: every secondary cue is read WITHIN its head-class x order configuration as a CONTRAST
log P(role | config, value) - log P(role | config) (absent/uninformative values contribute ~0; no majority-class double
counting). The labeler adds the strengths of the fired values (graded_competition.net_activation)
and takes softmax / argmax -- the normative limit of additive cue competition. Also reports per-cue availability
(P(value fires)) and reliability (max_r P(r | value)) so the cue's validity is auditable.
Source: UD-EWT TRAIN with gold heads/POS (the cue functions read only toks/pos/heads); evaluation treebanks never used.
Writes data/frontend_assets/coarse_role_validities_ud_ewt.json.   Run: python tools/build_coarse_role_validities.py
"""
import json
import math
import os
import sys
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab import graded_role_assigner as GRA

TRAIN = os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu")
OUT = os.path.join(REPO, "data", "frontend_assets", "coarse_role_validities_ud_ewt.json")
ALPHA = 0.5
M_SHRINK = 2.0


def coarse_of(dep: str) -> str:
    d = (dep or "").split(":")[0]; full = dep or ""
    if full.startswith("nsubj:pass") or full == "nsubjpass": return "PASS_SUBJ"
    if d in ("nsubj", "csubj"): return "SUBJ"
    if d in ("obj", "dobj", "iobj"): return "OBJ"
    if full == "obl:agent": return "BY_AGENT"
    if full == "nmod:poss": return "OTHER"   # possessive = determiner-like modifier, not an oblique
    if d in ("obl", "nmod"): return "OBL"
    return "OTHER"


def sentences(path):
    toks, pos, heads, deps = [], [], {}, {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if toks:
                    yield toks, pos, heads, deps
                toks, pos, heads, deps = [], [], {}, {}
                continue
            if line.startswith("#"):
                continue
            cols = line.split("\t")
            if "-" in cols[0] or "." in cols[0]:
                continue
            i = int(cols[0]); toks.append(cols[1]); pos.append(cols[3]); heads[i] = int(cols[6]); deps[i] = cols[7]
    if toks:
        yield toks, pos, heads, deps


def _perceive(toks, pos, heads):
    """Predicted POS + predicted heads from the live front-end (hdlab.causation_typing._frontend: tagger, parser)."""
    global _FE
    if _FE is None:
        import hdlab.causation_typing as CT
        _FE = CT._frontend()
    tg, pp, _ = _FE
    ppos = list(tg.tag(list(toks)))
    pheads = dict(pp.parse(list(toks), ppos).heads)
    return ppos, pheads


_FE = None


def main():
    perceived = "--perceived" in sys.argv
    out_path = OUT.replace(".json", "_perceived.json") if perceived else OUT
    K = len(GRA.ROLE_CLASSES)
    ix = {r: k for k, r in enumerate(GRA.ROLE_CLASSES)}
    cfg_counts = defaultdict(lambda: [0] * K)                      # config value -> role counts
    counts = defaultdict(lambda: defaultdict(lambda: [0] * K))     # cue -> "cfg|value" -> role counts
    prior = [0] * K; decisions = 0
    for toks, gpos, gheads, deps in sentences(TRAIN):
        pos, heads = _perceive(toks, gpos, gheads) if perceived else (gpos, gheads)
        for i in range(1, len(toks) + 1):
            if gpos[i - 1] not in GRA.NOMINAL:
                continue
            decisions += 1
            g = ix[coarse_of(deps.get(i))]
            prior[g] += 1
            cues = GRA.coarse_role_cues(toks, pos, heads, i)
            cfg = cues["config"]
            cfg_counts[cfg][g] += 1
            for cue, val in cues.items():
                if cue != "config":
                    counts[cue][f"{cfg}|{val}"][g] += 1
    logprior = [math.log((c + ALPHA) / (decisions + ALPHA * K)) for c in prior]
    p_cfg = {}; strength = {"config": {}}; audit = {"config": {}}
    for cfg, vec in cfg_counts.items():
        n = sum(vec); probs = [(c + ALPHA) / (n + ALPHA * K) for c in vec]
        p_cfg[cfg] = probs
        strength["config"][cfg] = [round(math.log(p) - lp, 4) for p, lp in zip(probs, logprior)]
        best = max(range(K), key=lambda k: vec[k])
        audit["config"][cfg] = {"n": n, "availability": round(n / decisions, 4), "reliability": round(vec[best] / n, 4),
                                "cued_role": GRA.ROLE_CLASSES[best]}
    for cue, vals in counts.items():
        strength[cue] = {}; audit[cue] = {}
        for key, vec in vals.items():
            cfg = key.split("|", 1)[0]; base = p_cfg[cfg]; n = sum(vec)
            # Dirichlet prior CENTERED ON the configuration's own distribution (m pseudo-counts): a rare value's
            # contrast shrinks to 0; a frequent value's zero-count role is genuinely excluded (large negative contrast);
            # a value that ALWAYS fires within its configuration carries no information -> contrast exactly 0.
            if n == sum(cfg_counts[cfg]):
                strength[cue][key] = [0.0] * K
            else:
                probs = [(c + M_SHRINK * b) / (n + M_SHRINK) for c, b in zip(vec, base)]
                strength[cue][key] = [round(math.log(p) - math.log(b), 4) for p, b in zip(probs, base)]
            best = max(range(K), key=lambda k: vec[k])
            audit[cue][key] = {"n": n, "availability": round(n / decisions, 4), "reliability": round(vec[best] / n, 4),
                               "cued_role": GRA.ROLE_CLASSES[best]}
    doc = {"source": "UD-EWT train (gold heads/POS). Competition Model, configuration-conditioned: activation(role) = "
                     "log P(role) + [log P(role|config) - log P(role)] + sum_c [log P(role|config,c=v) - log P(role|config)]; "
                     "add-0.5 on config, Dirichlet shrinkage m=%g on contrasts; availability = P(value fires), "
                     "reliability = max_r P(r|value)." % M_SHRINK,
           "decisions": decisions, "roles": GRA.ROLE_CLASSES, "prior": [round(x, 4) for x in logprior],
           "strength": strength, "audit": audit}
    doc["perceived"] = perceived
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
    print(f"decisions={decisions}  prior={dict(zip(GRA.ROLE_CLASSES, prior))}")
    print("[config]")
    for val, a in sorted(audit["config"].items(), key=lambda kv: -kv[1]["n"])[:12]:
        print(f"   {val:16s} n={a['n']:6d} avail={a['availability']:.4f} rel={a['reliability']:.3f} -> {a['cued_role']}")
    for cue in GRA.COARSE_CUES[1:]:
        print(f"[{cue}] (within VERB_pre / VERB_post / NOUN_pre / NOUN_post)")
        for key, a in sorted(audit[cue].items(), key=lambda kv: -kv[1]["n"]):
            if key.split("|")[0] in ("VERB_pre", "VERB_post", "NOUN_pre", "NOUN_post") and a["n"] >= 30:
                print(f"   {key:28s} n={a['n']:6d} rel={a['reliability']:.3f} -> {a['cued_role']}")
    print("wrote", out_path)


if __name__ == "__main__":
    main()
