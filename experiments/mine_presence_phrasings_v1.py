"""mine_presence_phrasings_v1 -- mine DIVERSE REAL presence/absence/occlusion/testimony verb-phrasings from
LitBank, for a corpus-grounded perceptual-access gold.

WHY (the finding that motivates this): clean naturally-INTACT false-belief-about-an-object-move scenes are
SPARSE in real literature (mine_false_belief_corpus_v1: 991 marker windows over 100 novels, most idiom/
dialogue/unfamiliar-person, ~dozens clean after curation). The RESIDUAL under test is the OBSERVATION CUE
(did agent A perceive the change?). Its generalization gap vs the fixed lexical baseline lives in the DIVERSE
REAL PHRASINGS of presence/absence the keyword list never enumerated ("had withdrawn to the library", "lay
abed", "rode over to the farm", "with her back to the door", "was told that ..."). So we mine those real VP
phrasings (a BROAD net, deliberately WIDER than either extractor's rules, to avoid circularity), classify each
by construction, and (in the eval cell) slot each into a canonical false-belief frame with a GROUND-TRUTH
label. The cue-bearing clause is REAL corpus prose; the label is by construction; the frame is minimal.

BROAD independent net = a large motion/state/communication lexicon (NOT the ledger's PATH-satellite rules and
NOT the lexical baseline's keyword list) -- so neither extractor is advantaged by the mining criterion.

Writes data/mine_presence_phrasings_v1/phrasings.jsonl. Read-only over data/litbank/original. ASCII only.
"""
from __future__ import annotations
import os, re, glob, json
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(REPO, "data", "litbank", "original")
OUT = os.path.join(REPO, "data", "mine_presence_phrasings_v1")

NAME = r"[A-Z][a-z]+"

# HIGH-PRECISION lexicons. Motion self-departure REQUIRES a directional satellite/PP (excludes transitive
# "left his compliments"). Occlusion is only genuine perceptual-unavailability states (no polysemous "nodded").
# Present/inform drop polysemous heads ("observed"=remarked, "heard"=sound). class -> (observed, pattern).
MOTION_V = (r"went|rode|hurried|slipped|crept|stole|withdrew|retired|hastened|walked|ran|climbed|drove|"
            r"marched|wandered|strolled|sallied|repaired|hurried|scampered|trotted|galloped|stepped|"
            r"passed|set off|set out|hastened|flew|sped|escaped|retreated|vanished|disappeared")
DIREC = (r"out|out of|away|off|upstairs|downstairs|indoors|abroad|forth|home|into|to|toward|towards|"
         r"down to|up to|back to|round to|over to|across to|from the room|from the house")
OCCLUDE_STATE = (r"asleep|fast asleep|sound asleep|abed|unconscious|senseless|insensible|blindfold(?:ed)?|"
                 r"in a swoon|in a faint|in the dark|in darkness")
OCCLUDE_V = r"slept|dozed|slumbered|fainted|swooned|drowsed"
PRESENT_V = r"watched|beheld|witnessed|gazed|stared|looked on|kept watch"
PRESENT_STATIVE = r"(?:stood|sat|remained|stayed|lingered)\s+(?:watching|by|beside|there|in the room|at the window)"
INFORM_V = r"(?:was|had been|were)\s+(?:told|informed|warned|apprised)"

CLASSES = [
    ("depart",  False, rf"\b({NAME})\s+((?:had\s+|was\s+)?(?:{MOTION_V})\s+(?:{DIREC})\b[^.;:!?\"]{{0,40}})"),
    ("occlude", False, rf"\b({NAME})\s+((?:was|lay|had been|had fallen|seemed|still)\s+(?:{OCCLUDE_STATE})\b[^.;:!?\"]{{0,30}})"),
    ("occlude", False, rf"\b({NAME})\s+((?:had\s+|)(?:{OCCLUDE_V})\b[^.;:!?\"]{{0,30}})"),
    ("present", True,  rf"\b({NAME})\s+((?:{PRESENT_V})\b[^.;:!?\"]{{0,45}})"),
    ("present", True,  rf"\b({NAME})\s+({PRESENT_STATIVE}\b[^.;:!?\"]{{0,25}})"),
    ("inform",  True,  rf"\b({NAME})\s+({INFORM_V}\b[^.;:!?\"]{{0,50}})"),
    ("return",  True,  rf"\b({NAME})\s+((?:had\s+|has\s+)?(?:returned|came back|got back|re-?entered|came home|came in)\b[^.;:!?\"]{{0,30}})"),
]

# reject a VP that drags in ANOTHER proper noun (would be incoherent when re-slotted onto a generic agent),
# or that is clearly not about self-motion/state.
OTHER_NAME = re.compile(rf"\b{NAME}\b")
STOP_VP = re.compile(r"\b(said|says|asked|replied|cried|answered|thought|felt|knew|loved|hated)\b", re.I)


def sents_of(txt):
    txt = re.sub(r"\s+", " ", txt)
    return re.split(r"(?<=[.!?\"])\s+(?=[A-Z\"'])", txt)


def clean_vp(vp: str) -> str:
    vp = vp.strip().rstrip(",;: ").strip()
    # cut at a coordinating/subordinating boundary to keep a clean self-contained predicate
    vp = re.split(r"\b(and|but|where|which|who|while|as |because|for the|,)\b", vp)[0].strip()
    return vp


def run():
    files = sorted(glob.glob(os.path.join(ORIG, "*.txt")))
    rows = []
    for f in files:
        book = os.path.basename(f)
        for s in sents_of(open(f, encoding="utf-8", errors="ignore").read()):
            if s.count('"') + s.count("'") >= 4:
                continue  # skip dialogue-heavy
            for cls, observed, pat in CLASSES:
                m = re.search(pat, s)
                if not m:
                    continue
                name, vp = m.group(1), clean_vp(m.group(2))
                if len(vp.split()) < 2 or len(vp.split()) > 12:
                    continue
                # reject VPs mentioning another proper noun (beyond the leading name) or a speech verb
                rest = vp
                if OTHER_NAME.search(rest) or STOP_VP.search(rest):
                    continue
                rows.append({"book": book, "name": name, "cls": cls, "observed": observed,
                             "vp": vp, "sent": s.strip()[:200]})
    # dedupe by normalized VP; keep diversity of head verbs
    seen = set(); uniq = []
    for r in rows:
        key = re.sub(r"\s+", " ", r["vp"].lower())
        if key in seen:
            continue
        seen.add(key); uniq.append(r)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "phrasings.jsonl"), "w", encoding="utf-8") as fh:
        for r in uniq:
            fh.write(json.dumps(r) + "\n")
    by = Counter((r["cls"], r["observed"]) for r in uniq)
    print(f"novels={len(files)}  raw={len(rows)}  unique VP phrasings={len(uniq)}")
    for (cls, obs), n in sorted(by.items()):
        print(f"  {cls:9s} observed={obs!s:5s} {n:4d}")
    print(f"wrote {OUT}/phrasings.jsonl")


if __name__ == "__main__":
    run()
