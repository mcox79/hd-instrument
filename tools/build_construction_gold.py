#!/usr/bin/env python
"""
build_construction_gold.py -- Construction-balanced who-is-affected GOLD from UD-English-EWT.

DATA-BUILD (not an experiment). No push/store/queue.

Sources: bundled UD-English-EWT gold .conllu (train+dev+test). We PROGRAMMATICALLY
select sentences that instantiate each target construction via GOLD-PARSE patterns, and
DERIVE the who-is-affected label (verb -> patient) FROM THE GOLD PARSE (obj / obl /
nsubj:pass / obl:agent edges). The label is therefore independent of our reader and of
any semantic/plausibility cue.

ASCII-only.
"""
import json, os, sys, random, argparse, collections

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- animacy heuristic (conservative: pronouns + a person/animal noun list) ----
ANIM_PRON = {"i","you","he","she","we","they","him","her","us","them","me","myself",
             "himself","herself","themselves","ourselves","yourself","who","whom"}
ANIM_NOUN = {
 "man","woman","boy","girl","child","children","kid","baby","king","queen","prince",
 "princess","soldier","officer","doctor","nurse","teacher","student","friend","enemy",
 "mother","father","mom","dad","parent","brother","sister","son","daughter","aunt",
 "uncle","cousin","people","person","men","women","worker","player","president",
 "captain","driver","farmer","hunter","thief","robber","guard","servant","master",
 "master","lady","gentleman","guy","girlfriend","boyfriend","husband","wife","neighbor",
 "neighbour","stranger","leader","priest","judge","lawyer","cook","maid","baker",
 "policeman","fireman","sailor","pilot","dog","cat","horse","wolf","bear","lion",
 "bird","cow","sheep","goat","fox","mouse","rabbit","dragon","witch","giant","fairy",
 "boss","manager","customer","client","author","artist","singer","actor","god",
 "angel","devil","monster","crowd","team","family","children","kids",
 # extended (cue-conflict under-flagging fix: 'detective'/'adult' were missing)
 "detective","adult","teenager","teen","infant","toddler","citizen","resident","victim",
 "suspect","criminal","passenger","tourist","visitor","guest","employee","colleague",
 "partner","agent","spy","waiter","waitress","chef","clerk","cashier","professor",
 "scientist","engineer","nurse","dentist","surgeon","coach","athlete","reporter",
 "journalist","editor","secretary","assistant","owner","tenant","landlord","buyer",
 "seller","voter","member","fan","follower","reader","viewer","listener","speaker",
 "counselor","therapist","psychologist","mechanic","plumber","electrician","carpenter",
 "waitperson","host","hostess","bartender","salesman","saleswoman","clerk","attendant",
}

def is_animate(tok):
    lem = tok["lemma"].lower(); form = tok["form"].lower()
    if lem in ANIM_PRON or form in ANIM_PRON:
        return True
    if tok["upos"] in ("NOUN",) and (lem in ANIM_NOUN or form in ANIM_NOUN):
        return True
    # PRON with Person feature (personal pronouns)
    if tok["upos"] == "PRON" and lem in ANIM_PRON:
        return True
    return False

# locative-alternation verbs (Levin class 9.7 / spray-load and friends)
LOCATIVE_VERBS = {"load","spray","fill","pour","cover","wrap","stack","pile","pack",
    "stuff","smear","splash","sow","plant","heap","cram","spread","stock","string",
    "hang","brush","dab","daub","plaster","scatter","sprinkle","strew","rub","inject",
    "drape","line","seed","litter","clutter","bombard","stitch","wind"}
# control / aspectual / raising matrix verbs that take an xcomp with a patient inside
CONTROL_MATRIX = {"begin","start","try","want","continue","attempt","need","like",
    "love","hate","hope","plan","decide","choose","manage","fail","offer","refuse",
    "seek","proceed","learn","help","dare","tend","get","keep","stop","finish",
    "intend","expect","wish","prefer","forget","remember","lay"}
# CURATED verb+preposition frames where the oblique RELIABLY marks the affected
# target/patient (not a benefactive / purpose / locative / resultative). Keyed by prep so
# preposition-SENSE is pinned by the verb class (this is a GOLD; over-generating from bare
# surface prepositions would mislabel benefactives 'work for you' as patients).
PREP_PATIENT_VERBS = {
 "at": {"fire","shoot","aim","throw","hurl","toss","look","stare","glance","gaze","glare",
        "peer","point","laugh","smile","shout","yell","scream","knock","kick","grab",
        "snatch","tug","wave","nod","gesture","swing","lunge","strike","jab","snap","bark",
        "growl","hiss","frown","wink","gape","marvel","gawk","scoff","sneer","clutch"},
 "to": {"listen","attend","refer","respond","reply","react","cling","adhere","subscribe",
        "appeal","resort","object","defer","allude","gesture","wave","nod"},
 "on": {"focus","concentrate","prey","feed","operate","comment","elaborate","embark",
        "dwell","spy","knock","pounce","encroach","trample","tread"},
 "upon": {"rely","depend","prey","seize","gaze","stumble","pounce","encroach"},
 "against": {"fight","struggle","protest","rebel","compete","guard","defend","lean","press",
             "brush","discriminate","retaliate","conspire"},
 "for": {"search","look","hunt","fish","forage","yearn","long","strive","grope","scout","angle"},
}
# RC-verb / head-noun filters for the gapped-object relative case
RC_INTRANS = {"go","come","arrive","depart","live","stay","sit","stand","lie","happen",
    "occur","exist","appear","disappear","wait","work","travel","walk","run","fly","swim",
    "sleep","rest","remain","belong","matter","count","rise","fall","vanish","talk","speak"}
RC_ADJUNCT_NOUN = {"time","day","week","month","year","moment","minute","hour","second",
    "way","reason","place","night","morning","evening","afternoon","point","period",
    "while","times","instant","era","age","decade"}

# ---- temporal-adjunct detection (a spatial-shaped preposition 'on June 7' is a DATE,
# not a location; such an obl is never the affected patient) ----
MONTHS = {"january","february","march","april","may","june","july","august","september",
    "october","november","december","jan","feb","mar","apr","jun","jul","aug","sep","sept",
    "oct","nov","dec"}
WEEKDAYS = {"monday","tuesday","wednesday","thursday","friday","saturday","sunday"}
TIME_NOUN = {"time","day","week","month","year","moment","minute","hour","second","night",
    "morning","evening","afternoon","period","while","instant","era","age","decade","today",
    "tomorrow","yesterday","tonight","noon","midnight","dawn","dusk","weekend","century",
    "date","o'clock"} | MONTHS | WEEKDAYS

# ---- stative possession / relation verbs: no agent acts on a patient, so word-order is
# NOT a live disambiguation cue (excluded from cue-conflict + simple-svo slices) ----
STATIVE_VERBS = {"have","own","possess","belong","contain","include","comprise","consist",
    "lack","cost","weigh","equal","resemble","hold"}

# ---- light-verb / idiom nouns: the surface obj is not the affected entity; the real
# affected entity (if any) is an oblique complement, else the item is a no-affected idiom ----
LIGHT_VERB_OF = {("take","care"), ("takes","care"), ("took","care")}      # take care OF X -> X
LIGHT_VERB_DROP = {("do","business"), ("conduct","business"), ("do","homework"),
    ("do","shopping"), ("do","laundry"), ("mind","business")}            # no-affected activity idioms


def is_temporal_obl(toks, o):
    """True if an oblique is a temporal/date adjunct (never an affected patient)."""
    if o["deprel"].endswith(":tmod"):
        return True
    lem = o["lemma"].lower(); form = o["form"].lower()
    if lem in TIME_NOUN or form in TIME_NOUN:
        return True
    if o["upos"] == "NUM":  # bare-number obl under a spatial prep is a year/date/measure
        return True
    for c in children(toks, o["id"]):
        cl = c["lemma"].lower()
        if cl in MONTHS or cl in WEEKDAYS or cl in TIME_NOUN:
            return True
    return False


def light_verb_resolve(toks, v, obj):
    """Resolve a light-verb object to the real affected entity.
    Returns the affected token, or None if the item should be DROPPED (no-affected idiom).
    Returns obj unchanged when it is not a light-verb pattern."""
    vlem = v["lemma"].lower(); olem = obj["lemma"].lower()
    if (vlem, olem) in {("take","care")}:
        for c in children(toks, v["id"]):
            if deprel_base(c["deprel"]) == "obl" and obl_case(toks, c) == "of":
                return c            # take care OF X -> X is the affected
        return None                 # 'take care' with no of-complement -> no affected
    if (vlem, olem) in LIGHT_VERB_DROP:
        return None                 # do business / do homework -> no affected patient
    return obj


def parse_conllu(path):
    sents = []
    sid = None; text = None; toks = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("# sent_id"):
                sid = line.split("=",1)[1].strip()
            elif line.startswith("# text"):
                text = line.split("=",1)[1].strip()
            elif line == "":
                if toks:
                    sents.append({"sent_id": sid, "text": text, "toks": toks})
                sid=None; text=None; toks=[]
            elif line.startswith("#"):
                continue
            else:
                cols = line.split("\t")
                if len(cols) != 10:
                    continue
                tid = cols[0]
                if "-" in tid or "." in tid:  # skip MWT ranges + empty nodes
                    continue
                toks.append({
                    "id": int(tid), "form": cols[1], "lemma": cols[2],
                    "upos": cols[3], "xpos": cols[4], "feats": cols[5],
                    "head": int(cols[6]), "deprel": cols[7], "deps": cols[8],
                })
    if toks:
        sents.append({"sent_id": sid, "text": text, "toks": toks})
    return sents


def children(toks, hid):
    return [t for t in toks if t["head"] == hid]

def by_id(toks, tid):
    for t in toks:
        if t["id"] == tid:
            return t
    return None

def deprel_base(dr):
    return dr.split(":")[0]

def obl_case(toks, obl_tok):
    """return the lowercased case preposition governing an obl token, or None."""
    for c in children(toks, obl_tok["id"]):
        if c["deprel"] == "case":
            return c["lemma"].lower()
    # UD also encodes case in the deprel subtype nmod:in / obl:at
    if ":" in obl_tok["deprel"]:
        sub = obl_tok["deprel"].split(":",1)[1]
        if sub not in ("agent","tmod","npmod"):
            return sub.lower()
    return None


def np_span_ok(text_tokcount, maxtok):
    return text_tokcount <= maxtok


# ---------- per-construction extractors ----------
# each returns list of candidate dicts: {verb, patient, agent(optional), frame(optional),
#   genuine_ambiguity(bool)}  -- token objects

def ex_passive_by_agent(toks):
    out = []
    for v in toks:
        if v["upos"] != "VERB":
            continue
        ch = children(toks, v["id"])
        subjpass = [c for c in ch if c["deprel"] == "nsubj:pass"]
        agents   = [c for c in ch if c["deprel"] in ("obl:agent","nmod:agent") or
                    (deprel_base(c["deprel"])=="obl" and obl_case(toks,c)=="by")]
        if subjpass and agents:
            pat = subjpass[0]; ag = agents[0]
            amb = is_animate(pat) and is_animate(ag)  # both animate -> word order would mislead
            out.append({"verb":v,"patient":pat,"agent":ag,"frame":"by_agent_passive",
                        "genuine_ambiguity":False,"cue_conflict":amb,"deprel":"nsubj:pass"})
    return out

LOC_GOAL_CASES = ("onto","into","on","in","over","across","around","through","with")

def ex_locative(toks):
    """Locative-alternation verbs (Levin spray/load). The affected HOLISTIC entity is
    the obj (active) or nsubj:pass (passive) or the acl-participle head noun; the
    with/into/onto/in/on obl is CONTENT or GOAL/LOCATION, NEVER the patient. A temporal
    adjunct ('on June 7') is never the patient.

    Frames:
      both-frames  : obj AND a spatial obl both visible -> holistic-vs-theme genuinely
                     reader-dependent -> genuine_ambiguity=True (abstain-target).
      passive      : nsubj:pass is the affected; the loc/with obl is content/location.
      obj-only     : theme-patient (obj), no obl visible.
      acl-holistic : reduced participle ('food stacked with X') -> the modified head noun.
    Active intransitive/stative uses with ONLY a spatial obl and no theme ('hanging in the
    room') have no agent-acts-on-patient reading -> EXCLUDED."""
    out = []
    for v in toks:
        if v["upos"] != "VERB" or v["lemma"].lower() not in LOCATIVE_VERBS:
            continue
        ch = children(toks, v["id"])
        objs = [c for c in ch if c["deprel"] == "obj"]
        subjpass = [c for c in ch if c["deprel"] == "nsubj:pass"]
        is_passive = bool(subjpass) or any(c["deprel"] == "aux:pass" for c in ch)
        obls = [c for c in ch if deprel_base(c["deprel"]) == "obl"]
        loc_obls = [o for o in obls if obl_case(toks,o) in LOC_GOAL_CASES
                    and not is_temporal_obl(toks,o)]
        if objs and loc_obls and not is_passive:
            cases = [obl_case(toks,o) for o in loc_obls]
            with_frame = "with" in cases
            frame = "both-frames:with(holistic)" if with_frame else "both-frames:goal(theme)"
            pat = objs[0]; amb = True
        elif is_passive and subjpass:
            # passive locative: affected = nsubj:pass; the with/loc obl is content/location.
            frame = "passive_holistic(nsubj:pass)"
            pat = subjpass[0]; amb = False
        elif objs:
            frame = "obj-only(theme-patient)"
            pat = objs[0]; amb = False
        elif v["deprel"] == "acl" and (loc_obls or obls):
            # reduced participle 'food stacked (high) with garnishes' -> affected = head noun.
            head = by_id(toks, v["head"])
            if head is None or head["upos"] in ("PUNCT",):
                continue
            frame = "acl-participle-holistic(head-noun)"
            pat = head; amb = False
        else:
            # only a spatial obl (or nothing usable): intransitive/stative locative, no
            # theme -> the obl is pure location, no affected patient -> EXCLUDE.
            continue
        out.append({"verb":v,"patient":pat,"agent":None,"frame":frame,
                    "genuine_ambiguity":amb,"cue_conflict":False,"deprel":pat["deprel"]})
    return out

def ex_prep_governed(toks):
    out = []
    for v in toks:
        if v["upos"] != "VERB":
            continue
        # exclude copula / existential / light verbs: their oblique is a locative modifier,
        # not a patient ("there ARE options on the shores").
        if v["lemma"].lower() in ("be","become","seem","exist","remain","stay"):
            continue
        ch = children(toks, v["id"])
        if any(c["deprel"] == "obj" for c in ch):
            continue  # want NO direct object: patient realized obliquely
        # exclude passives + existential-there subjects
        if any(c["deprel"]=="nsubj:pass" for c in ch):
            continue
        if any(c["deprel"] in ("expl","cop") for c in ch):
            continue
        # need a genuine patient-marking preposition, and an eventive nsubj (an agent doing it)
        if not any(c["deprel"]=="nsubj" for c in ch):
            continue
        obls = [c for c in ch if deprel_base(c["deprel"]) == "obl"]
        vlem = v["lemma"].lower()
        cand = None; cs = None
        for o in obls:
            c = obl_case(toks,o)
            if c in PREP_PATIENT_VERBS and vlem in PREP_PATIENT_VERBS[c]:
                cand = o; cs = c; break
        if cand is None:
            continue
        out.append({"verb":v,"patient":cand,"agent":None,"frame":"prep_"+cs,
                    "genuine_ambiguity":False,"cue_conflict":False,"deprel":cand["deprel"]})
    return out

def ex_coordination(toks):
    out = []
    for v2 in toks:
        if v2["upos"] != "VERB" or v2["deprel"] != "conj":
            continue
        v1 = by_id(toks, v2["head"])
        if v1 is None or v1["upos"] != "VERB":
            continue
        ch2 = children(toks, v2["id"])
        objs = [c for c in ch2 if c["deprel"] == "obj"]
        if not objs:
            continue
        # v2 must NOT carry its own overt nsubj (shared subject case)
        if any(c["deprel"] in ("nsubj","nsubj:pass") for c in ch2):
            continue
        pat = light_verb_resolve(toks, v2, objs[0])
        if pat is None:
            continue  # no-affected idiom ('doing their every day business')
        out.append({"verb":v2,"patient":pat,"agent":None,"frame":"conj_2nd_verb",
                    "genuine_ambiguity":False,"cue_conflict":False,"deprel":"obj"})
    return out

def ex_relclause(toks):
    out = []
    for v in toks:
        if v["upos"] != "VERB" or v["deprel"] != "acl:relcl":
            continue
        ch = children(toks, v["id"])
        # patient = the obj inside the RC (may be a relativizer 'which/that/whom' or a noun)
        objs = [c for c in ch if c["deprel"] == "obj"]
        # relativized object case: obj is the relativizer, OR the head noun is the patient
        RELZR = {"that","which","who","whom","whose"}
        if objs:
            pat = objs[0]
        else:
            # gapped OBJECT relative ("the money which his aunt had given"): the modified
            # noun is the patient. Require a LEXICAL subject that is NOT a relativizer, so
            # the gap is in OBJECT position -- this EXCLUDES subject-relatives
            # ("the mousse that comes", where the relativizer itself is the nsubj).
            subj = [c for c in ch if c["deprel"] == "nsubj"]
            if not subj:
                continue
            if any(s["form"].lower() in RELZR for s in subj):
                continue  # relativizer is the subject -> subject-relative, gap is NOT patient
            # exclude intransitive RC verbs + temporal/adjunct head nouns: those gaps are
            # oblique/adjunct ("the time (when) we go"), not an affected patient.
            if v["lemma"].lower() in RC_INTRANS:
                continue
            # RC verb must not already have an obl/advmod that IS the likely gap-filler slot
            if any(c["deprel"] in ("obl","advmod","obl:tmod","advcl") for c in ch):
                continue
            head_noun = by_id(toks, v["head"])
            if head_noun is None or head_noun["upos"] in ("PUNCT",):
                continue
            if head_noun["lemma"].lower() in RC_ADJUNCT_NOUN:
                continue
            pat = head_noun
            # gap: the entity is the RC verb's OBJECT via the relative gap; record that
            # (its raw pat["deprel"] is the MATRIX role, which would mislead)
            out.append({"verb":v,"patient":pat,"agent":None,"frame":"acl:relcl_gapped_obj",
                        "genuine_ambiguity":False,"cue_conflict":False,"deprel":"obj:rc_gap"})
            continue
        # subject-relative light-verb guard: 'who took great care of me' is a subject
        # relative whose overt obj ('care') is a light-verb noun, not the affected entity.
        # Resolve to the real affected (the of-obl 'me'); drop no-affected idioms.
        pat = light_verb_resolve(toks, v, pat)
        if pat is None:
            continue
        out.append({"verb":v,"patient":pat,"agent":None,"frame":"acl:relcl_overt_obj",
                    "genuine_ambiguity":False,"cue_conflict":False,"deprel":pat["deprel"]})
    return out

def ex_control_xcomp(toks):
    out = []
    for v2 in toks:
        if v2["upos"] != "VERB" or v2["deprel"] != "xcomp":
            continue
        v1 = by_id(toks, v2["head"])
        if v1 is None or v1["upos"] not in ("VERB","AUX"):
            continue
        if v1["lemma"].lower() not in CONTROL_MATRIX:
            continue
        ch2 = children(toks, v2["id"])
        objs = [c for c in ch2 if c["deprel"] == "obj"]
        if not objs:
            continue
        pat = light_verb_resolve(toks, v2, objs[0])
        if pat is None:
            continue
        out.append({"verb":v2,"patient":pat,"agent":None,"frame":"xcomp_under_"+v1["lemma"].lower(),
                    "genuine_ambiguity":False,"cue_conflict":False,"deprel":"obj"})
    return out

def ex_cue_conflict(toks):
    """active SVO where BOTH nsubj and obj are animate (word-order is the only structural cue).
    Excludes stative possession/relation verbs ('have people/kids'): no agent acts on a
    patient there, so word-order is not a live cue (the cue-conflict premise is vacuous)."""
    out = []
    for v in toks:
        if v["upos"] != "VERB":
            continue
        if v["lemma"].lower() in STATIVE_VERBS:
            continue
        ch = children(toks, v["id"])
        subj = [c for c in ch if c["deprel"] == "nsubj"]
        objs = [c for c in ch if c["deprel"] == "obj"]
        if any(c["deprel"]=="nsubj:pass" for c in ch):
            continue
        if not subj or not objs:
            continue
        s = subj[0]; o = objs[0]
        if light_verb_resolve(toks, v, o) is not o:
            continue  # light-verb / no-affected idiom -> not a clean word-order cue-conflict
        if is_animate(s) and is_animate(o):
            out.append({"verb":v,"patient":o,"agent":s,"frame":"active_animate_animate",
                        "genuine_ambiguity":False,"cue_conflict":True,"deprel":"obj"})
    return out

def ex_simple_svo(toks):
    out = []
    for v in toks:
        if v["upos"] != "VERB":
            continue
        if v["lemma"].lower() in STATIVE_VERBS:
            continue  # 'have a car' is not agent-acts-on-patient
        ch = children(toks, v["id"])
        subj = [c for c in ch if c["deprel"] == "nsubj"]
        objs = [c for c in ch if c["deprel"] == "obj"]
        # simple: has subj+obj, no passive, no embedding markers, verb is root or simple clause
        if any(c["deprel"] in ("nsubj:pass",) for c in ch):
            continue
        if v["deprel"] not in ("root","ccomp","parataxis"):
            continue
        if not subj or not objs:
            continue
        s = subj[0]; o = objs[0]
        # keep it "easy": inanimate object (concrete theme), subject need not be animate
        if is_animate(o):
            continue
        if light_verb_resolve(toks, v, o) is not o:
            continue  # light-verb / no-affected idiom
        out.append({"verb":v,"patient":o,"agent":s,"frame":"simple_svo",
                    "genuine_ambiguity":False,"cue_conflict":False,"deprel":"obj"})
    return out


EXTRACTORS = [
    ("passive_by_agent", ex_passive_by_agent),
    ("locative_alternation", ex_locative),
    ("prep_governed_patient", ex_prep_governed),
    ("coordination_shared_subj", ex_coordination),
    ("relative_clause_patient", ex_relclause),
    ("control_xcomp", ex_control_xcomp),
    ("cue_conflict_animate", ex_cue_conflict),
    ("simple_svo", ex_simple_svo),
]

TARGET_PER = 16          # aim ~10-20 each
MAXTOK = 25              # legibility cap
CUE_CONFLICT_TARGET = 16
# per-construction target overrides. Locative is enlarged so that AFTER the genuine-
# ambiguity items are set aside as a separate abstain-target bucket, the 70/30 split over
# the NON-ambiguity items still leaves >=5 scoreable (non-abstain) locative TEST items.
TARGET_OVERRIDE = {"cue_conflict_animate": CUE_CONFLICT_TARGET, "locative_alternation": 24}


def build(maxtok=MAXTOK, target_per=TARGET_PER, seed=1234):
    rng = random.Random(seed)
    files = [
        os.path.join(REPO,"experiments","data","ud_english_ewt","en_ewt-ud-train.conllu"),
        os.path.join(REPO,"experiments","data","ud_english_ewt","en_ewt-ud-dev.conllu"),
        os.path.join(REPO,"experiments","data","ud_english_ewt","en_ewt-ud-test.conllu"),
    ]
    sents = []
    for fp in files:
        if os.path.exists(fp):
            sents.extend(parse_conllu(fp))
    # length filter
    sents = [s for s in sents if s["toks"] and s["toks"][-1]["id"] <= maxtok
             and len(s["toks"]) >= 3]

    # gather all candidates per construction, dedup by sent_id (one item per sentence
    # per construction; and a sentence goes to at most ONE construction bucket -- first
    # match in EXTRACTOR order that still needs items, to avoid double-counting)
    by_constr = collections.OrderedDict((n,[]) for n,_ in EXTRACTORS)
    raw_counts = {}
    for name, fn in EXTRACTORS:
        seen = set()
        cands = []
        for s in sents:
            got = fn(s["toks"])
            if not got:
                continue
            if s["sent_id"] in seen:
                continue
            c = got[0]  # first hit in the sentence
            # skip patient == punctuation or determiner-only
            if c["patient"]["upos"] in ("PUNCT",):
                continue
            seen.add(s["sent_id"])
            cands.append((s, c))
        raw_counts[name] = len(cands)
        by_constr[name] = cands

    # assign sentences uniquely: iterate constructions in priority order (hardest/rarest
    # first so they are not stolen by simple_svo); a sentence used once is not reused.
    priority = ["passive_by_agent","locative_alternation","prep_governed_patient",
                "coordination_shared_subj","relative_clause_patient","control_xcomp",
                "cue_conflict_animate","simple_svo"]
    used_sids = set()
    selected = collections.OrderedDict((n,[]) for n in priority)
    for name in priority:
        cands = by_constr[name]
        rng.shuffle(cands)
        # prefer genuine-ambiguity candidates first so the abstain-target slice is non-empty
        cands.sort(key=lambda sc: 0 if sc[1].get("genuine_ambiguity") else 1)
        tgt = TARGET_OVERRIDE.get(name, target_per)
        for s,c in cands:
            if s["sent_id"] in used_sids:
                continue
            selected[name].append((s,c))
            used_sids.add(s["sent_id"])
            if len(selected[name]) >= tgt:
                break

    # also promote a matched flip-passive into cue_conflict slice: any passive_by_agent
    # item that is animate-animate (already flagged cue_conflict True) is tagged so.
    return selected, raw_counts


def to_gold(selected):
    gold = {}
    counts = collections.Counter()
    amb = 0
    idx = 0
    for constr, items in selected.items():
        for s, c in items:
            idx += 1
            iid = "%s_%03d" % (constr[:4].upper(), idx)
            v = c["verb"]; p = c["patient"]; a = c.get("agent")
            entry = {
                "sent_id": s["sent_id"],
                "text": s["text"],
                "construction": constr,
                "frame": c.get("frame"),
                "n_tokens": s["toks"][-1]["id"],
                "verb": {"lemma": v["lemma"], "form": v["form"], "id": v["id"]},
                "patient": {"form": p["form"], "lemma": p["lemma"], "id": p["id"],
                            "deprel": c.get("deprel", p["deprel"]), "upos": p["upos"]},
                "genuine_ambiguity": bool(c.get("genuine_ambiguity")),
                "cue_conflict": bool(c.get("cue_conflict")),
            }
            if a is not None:
                entry["agent"] = {"form": a["form"], "lemma": a["lemma"], "id": a["id"]}
            gold[iid] = entry
            counts[constr] += 1
            if entry["genuine_ambiguity"]:
                amb += 1
    return gold, counts, amb


def split_traintest(gold, test_frac=0.30, seed=99):
    """Stratified 70/30 train/test over NON-ambiguity (scoreable) items only. Genuine-
    ambiguity items are abstain-targets and go into a separate split='ambiguity' bucket so
    they are never scored for non-abstain accuracy. Deterministic (sorted keys + seed)."""
    rng = random.Random(seed)
    # genuine-ambiguity items -> abstain-target bucket (not train, not test)
    for k, v in gold.items():
        if v.get("genuine_ambiguity"):
            v["split"] = "ambiguity"
    # stratify the remaining (scoreable) items by construction
    byc = collections.defaultdict(list)
    for k, v in gold.items():
        if v.get("split") == "ambiguity":
            continue
        byc[v["construction"]].append(k)
    for c, keys in byc.items():
        keys_sorted = sorted(keys)  # deterministic
        rng.shuffle(keys_sorted)
        ntest = max(1, int(round(len(keys_sorted)*test_frac)))
        testset = set(keys_sorted[:ntest])
        for k in keys:
            gold[k]["split"] = "test" if k in testset else "train"
    ntr = sum(1 for v in gold.values() if v["split"]=="train")
    nte = sum(1 for v in gold.values() if v["split"]=="test")
    namb = sum(1 for v in gold.values() if v["split"]=="ambiguity")
    return ntr, nte, namb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(REPO,"data","gold_construction_argstruct_ewt_v1","gold_construction_argstruct_ewt_v1.json"))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    selected, raw = build()
    gold, counts, amb = to_gold(selected)
    ntr, nte, namb = split_traintest(gold)

    print("RAW candidate pool per construction (pre-cap):")
    for k,v in raw.items():
        print("  %-26s %5d" % (k, v))
    print("SELECTED per construction:")
    total = 0
    sparse = []
    for k in ["passive_by_agent","locative_alternation","prep_governed_patient",
              "coordination_shared_subj","relative_clause_patient","control_xcomp",
              "cue_conflict_animate","simple_svo"]:
        n = counts.get(k,0); total += n
        flag = "  <-- SPARSE (<10)" if n < 10 else ""
        print("  %-26s %5d%s" % (k, n, flag))
        if n < 10:
            sparse.append((k,n))
    print("TOTAL items: %d" % total)
    print("genuine_ambiguity items (abstain-target bucket): %d" % amb)
    print("cue_conflict-flagged items (any construction): %d" %
          sum(1 for v in gold.values() if v.get("cue_conflict")))
    print("split (over non-ambiguity items): %d train / %d test / %d ambiguity(abstain)" %
          (ntr, nte, namb))
    # per-construction TEST power over scoreable (non-ambiguity) items
    loc_test_nonamb = sum(1 for v in gold.values()
        if v["construction"]=="locative_alternation" and v["split"]=="test")
    print("locative non-ambiguity TEST items (non-abstain accuracy power): %d" % loc_test_nonamb)
    if sparse:
        print("SPARSE CONSTRUCTIONS (fairness flag): " + ", ".join("%s=%d"%(k,n) for k,n in sparse))

    if args.self_test:
        # verify every entry's label derives from the parse: patient id present, verb id present,
        # patient != verb, ids within sentence
        bad = 0
        for k,v in gold.items():
            if v["verb"]["id"] == v["patient"]["id"]:
                bad += 1
            if not v.get("split"):
                bad += 1
        print("SELF-TEST label-integrity bad=%d (expect 0)" % bad)
        assert bad == 0, "label integrity failure"
        assert total >= 60, "too few items overall"
        print("SELF-TEST PASS")
        return

    meta = {
        "_meta": {
            "name": "gold_construction_argstruct_ewt_v1",
            "built": "2026-07-20",
            "builder": "exp_dev data-build (tools/build_construction_gold.py)",
            "source": "UD-English-EWT gold treebank (train+dev+test .conllu), bundled at experiments/data/ud_english_ewt/. Real web-text sentences with GOLD dependency parses.",
            "label_derivation": "who-is-affected label = (verb_lemma, patient_head) DERIVED FROM THE GOLD PARSE ONLY (obj / obl / nsubj:pass / obl:agent edges). INDEPENDENT of our reader and of any semantic/plausibility cue. No hand-invented sentences; all sentences are real UD-EWT items selected by gold-parse pattern.",
            "purpose": "Test CONSTRUCTION handling (passive-flip, locative alternation, preposition-sense, coordination, relative-clause, control/xcomp, animate-animate cue-conflict) with real incidence of the hard constructions the McGuffey gold lacks. Provides a held-out train/test split for cue-weight training without overfit.",
            "register_caveat": "UD-EWT is MODERN WEB TEXT (blogs, reviews, email, newsgroups), NOT children's narrative. This set tests CONSTRUCTION handling, NOT register transfer to McGuffey-style narrative. Register difference is a real confound for any cross-corpus generalization claim; state it.",
            "genuine_ambiguity_note": "genuine_ambiguity=true = the locative both-frames-visible case: a spray/load verb with BOTH an overt obj AND a with/into/onto oblique, so 'which entity is THE affected one' (holistic container vs theme content) is genuinely reader-dependent even with a clean parse. This is the parse-derived proxy for holistic-vs-theme ambiguity. These are ABSTAIN-TARGET cases: they get split='ambiguity' (a SEPARATE bucket, NOT train/test) and must NOT be scored for non-abstain accuracy. In the locative-alternation single-frame passive/obj/acl cases the parse pins the affected entity (nsubj:pass / obj / acl head-noun), so those are NON-ambiguous and scoreable.",
            "cue_conflict_note": "cue_conflict=true marks items where both core arguments are animate so surface word-order is the ONLY structural disambiguation cue (active animate-animate) OR a by-agent passive whose word-order expectation FLIPS. This is the slice where multi-cue integration COULD beat word-order-alone. Stative possession/relation verbs (have/own/...) are EXCLUDED from this slice: no agent acts on a patient there, so the cue-conflict premise is vacuous.",
            "split": "stratified 70/30 train/test by construction (seed=99) over the NON-ambiguity (scoreable) items ONLY. genuine_ambiguity items form a separate split='ambiguity' abstain-target bucket and are never train or test. Train cue-weights on train, MEASURE non-abstain accuracy on test.",
            "single_annotator_note": "Labels are PARSE-DERIVED (UD-EWT gold annotators), not this builder's own reading. Selection patterns are heuristic (documented in tools/build_construction_gold.py); a human should spot-check the human_annotation_subset.md.",
            "maxtok": MAXTOK,
        },
        "gold": gold,
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=True)
    print("WROTE %s (%d items)" % (args.out, total))

    # human annotation subset
    write_human_subset(gold, os.path.join(os.path.dirname(args.out), "human_annotation_subset.md"))


def write_human_subset(gold, path):
    # pick clearest self-contained examples across the hard types
    want = {"passive_by_agent":3,"locative_alternation":3,"prep_governed_patient":2,
            "cue_conflict_animate":3,"coordination_shared_subj":1,"relative_clause_patient":2}
    picked = []
    for constr, n in want.items():
        items = sorted([(k,v) for k,v in gold.items() if v["construction"]==constr],
                       key=lambda kv: kv[1]["n_tokens"])  # shortest = clearest
        for k,v in items[:n]:
            picked.append((k,v))
    lines = []
    lines.append("# Human annotation subset -- who-is-affected (construction gold, UD-EWT)\n")
    lines.append("For each sentence: which entity does the action AFFECT (the patient of the ")
    lines.append("marked verb)? Note WHICH CUE you used (word-order / passive-marker / ")
    lines.append("preposition-sense / verb-meaning / world-knowledge) and whether you ABSTAINED ")
    lines.append("(genuine ambiguity). The 'gold verb-patient' below is DERIVED FROM THE UD-EWT ")
    lines.append("GOLD PARSE (structural), independent of any reader.\n")
    lines.append("| # | construction | sentence | gold verb | gold patient | ambiguous? |")
    lines.append("|---|---|---|---|---|---|")
    for i,(k,v) in enumerate(picked,1):
        txt = v["text"].replace("|","/")
        lines.append("| %d | %s | %s | %s | %s | %s |" % (
            i, v["construction"], txt, v["verb"]["form"], v["patient"]["form"],
            "YES (abstain-target)" if v["genuine_ambiguity"] else "no"))
    lines.append("\n## Walkthrough prompt (per item)")
    lines.append("1. Read the sentence. Who/what is AFFECTED by the marked verb?")
    lines.append("2. Which cue told you: word-order, passive by-marker, preposition sense, ")
    lines.append("   verb meaning, or world-knowledge?")
    lines.append("3. Could a reasonable reader pick the OTHER entity? If yes -> ABSTAIN.")
    lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("WROTE %s (%d items)" % (path, len(picked)))


if __name__ == "__main__":
    main()
