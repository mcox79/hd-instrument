"""Mine experiencer/psych-verb sentences from litbank novels. One-off data-build helper.
Outputs candidate sentences grouped by verb lemma + rough construction, for HUMAN (agent) labeling.
Does NOT assign thematic roles -- labeling is done by reading (non-circular)."""
import os, re, json, glob, random

LITBANK = os.path.join(os.path.dirname(__file__), "..", "data", "litbank", "original")

# Curated psych-verb inventory (SUPPLIED KNOWLEDGE). Each lemma -> (exp_type, inflected surface forms).
# subj = experiencer-subject (subj=EXPERIENCER, complement=STIMULUS/THEME)
# obj  = experiencer-object  (subj=STIMULUS, obj=EXPERIENCER)  <- the hard case
SUBJ_EXP = {
    "fear": ["fear", "fears", "feared", "fearing"],
    "want": ["want", "wants", "wanted", "wanting"],
    "love": ["love", "loves", "loved", "loving"],
    "like": ["like", "likes", "liked", "liking"],
    "hate": ["hate", "hates", "hated", "hating"],
    "hope": ["hope", "hopes", "hoped", "hoping"],
    "dread": ["dread", "dreads", "dreaded", "dreading"],
    "long": ["long", "longs", "longed", "longing"],
    "wish": ["wish", "wishes", "wished", "wishing"],
    "desire": ["desire", "desires", "desired", "desiring"],
    "admire": ["admire", "admires", "admired", "admiring"],
    "adore": ["adore", "adores", "adored", "adoring"],
    "envy": ["envy", "envies", "envied", "envying"],
    "pity": ["pity", "pities", "pitied", "pitying"],
    "loathe": ["loathe", "loathes", "loathed", "loathing"],
    "cherish": ["cherish", "cherishes", "cherished", "cherishing"],
    "crave": ["crave", "craves", "craved", "craving"],
    "yearn": ["yearn", "yearns", "yearned", "yearning"],
    "grieve": ["grieve", "grieves", "grieved", "grieving"],
    "mourn": ["mourn", "mourns", "mourned", "mourning"],
    "regret": ["regret", "regrets", "regretted", "regretting"],
    "miss": ["miss", "misses", "missed", "missing"],
    "trust": ["trust", "trusts", "trusted", "trusting"],
    "doubt": ["doubt", "doubts", "doubted", "doubting"],
    "marvel": ["marvel", "marvels", "marvelled", "marveled", "marvelling", "marveling"],
    "wonder": ["wonder", "wonders", "wondered", "wondering"],
    "rejoice": ["rejoice", "rejoices", "rejoiced", "rejoicing"],
    "fret": ["fret", "frets", "fretted", "fretting"],
    "esteem": ["esteem", "esteems", "esteemed", "esteeming"],
    "scorn": ["scorn", "scorns", "scorned", "scorning"],
    "despise": ["despise", "despises", "despised", "despising"],
    "relish": ["relish", "relishes", "relished", "relishing"],
    "enjoy": ["enjoy", "enjoys", "enjoyed", "enjoying"],
    "value": ["value", "values", "valued", "valuing"],
    "abhor": ["abhor", "abhors", "abhorred", "abhorring"],
    "resent": ["resent", "resents", "resented", "resenting"],
    "covet": ["covet", "covets", "coveted", "coveting"],
    "revere": ["revere", "reveres", "revered", "revering"],
    "pine": ["pine", "pines", "pined", "pining"],
}
OBJ_EXP = {
    "frighten": ["frighten", "frightens", "frightened", "frightening"],
    "please": ["please", "pleases", "pleased", "pleasing"],
    "anger": ["anger", "angers", "angered", "angering"],
    "delight": ["delight", "delights", "delighted", "delighting"],
    "amuse": ["amuse", "amuses", "amused", "amusing"],
    "astonish": ["astonish", "astonishes", "astonished", "astonishing"],
    "annoy": ["annoy", "annoys", "annoyed", "annoying"],
    "terrify": ["terrify", "terrifies", "terrified", "terrifying"],
    "alarm": ["alarm", "alarms", "alarmed", "alarming"],
    "surprise": ["surprise", "surprises", "surprised", "surprising"],
    "disgust": ["disgust", "disgusts", "disgusted", "disgusting"],
    "shock": ["shock", "shocks", "shocked", "shocking"],
    "startle": ["startle", "startles", "startled", "startling"],
    "comfort": ["comfort", "comforts", "comforted", "comforting"],
    "trouble": ["trouble", "troubles", "troubled", "troubling"],
    "grieve_o": ["grieved", "grieves"],  # transitive "it grieved him" -- handled sep
    "vex": ["vex", "vexes", "vexed", "vexing"],
    "charm": ["charm", "charms", "charmed", "charming"],
    "disturb": ["disturb", "disturbs", "disturbed", "disturbing"],
    "console": ["console", "consoles", "consoled", "consoling"],
    "distress": ["distress", "distresses", "distressed", "distressing"],
    "torment": ["torment", "torments", "tormented", "tormenting"],
    "puzzle": ["puzzle", "puzzles", "puzzled", "puzzling"],
    "irritate": ["irritate", "irritates", "irritated", "irritating"],
    "soothe": ["soothe", "soothes", "soothed", "soothing"],
    "enrage": ["enrage", "enrages", "enraged", "enraging"],
    "horrify": ["horrify", "horrifies", "horrified", "horrifying"],
    "fascinate": ["fascinate", "fascinates", "fascinated", "fascinating"],
    "interest": ["interest", "interests", "interested", "interesting"],
    "worry": ["worry", "worries", "worried", "worrying"],
    "sadden": ["sadden", "saddens", "saddened", "saddening"],
    "gladden": ["gladden", "gladdens", "gladdened", "gladdening"],
    "embarrass": ["embarrass", "embarrasses", "embarrassed", "embarrassing"],
    "bore": ["bore", "bores", "bored", "boring"],
    "thrill": ["thrill", "thrills", "thrilled", "thrilling"],
    "offend": ["offend", "offends", "offended", "offending"],
    "displease": ["displease", "displeases", "displeased", "displeasing"],
    "perplex": ["perplex", "perplexes", "perplexed", "perplexing"],
}

# Build surface->(lemma, exp_type) map; prefer finite/base forms as "main verb" signals.
# We will require the surface form to appear as a whole word, and we down-weight -ing/-ed adjectival uses
# by keeping them but tagging so the reader can filter.
form2lemma = {}
for lem, forms in SUBJ_EXP.items():
    for f in forms:
        form2lemma[f] = (lem, "subj")
for lem, forms in OBJ_EXP.items():
    for f in forms:
        form2lemma.setdefault(f, (lem, "obj"))

all_forms = sorted(form2lemma.keys(), key=len, reverse=True)
FORM_RE = re.compile(r"\b(" + "|".join(re.escape(f) for f in all_forms) + r")\b")

def sent_split(text):
    text = re.sub(r"\s+", " ", text)
    # naive sentence splitter on . ! ? followed by space+capital/quote
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z"\'])', text)
    return parts

random.seed(13)
by_verb = {}  # lemma -> list of (sent, exp_type, novel_id, matched_form)
files = sorted(glob.glob(os.path.join(LITBANK, "*.txt")))
for fp in files:
    novel = os.path.basename(fp).replace(".txt", "")
    try:
        raw = open(fp, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue
    for s in sent_split(raw):
        w = s.split()
        if not (5 <= len(w) <= 26):
            continue
        m = FORM_RE.search(s)
        if not m:
            continue
        form = m.group(1)
        lem, et = form2lemma[form]
        # skip when the psych word is clearly a plain noun ("no fear", "with pleasure") -- light filter
        by_verb.setdefault(lem, []).append({"text": s.strip(), "exp_type": et, "novel": novel, "form": form})

# print a compact digest: up to 6 candidate sentences per verb, prefer variety of forms
out = []
for lem in sorted(by_verb):
    cands = by_verb[lem]
    random.shuffle(cands)
    seen_forms = set()
    picked = []
    for c in cands:
        if len(picked) >= 8:
            break
        picked.append(c)
    out.append((lem, by_verb[lem][0]["exp_type"], len(cands), picked))

print("VERB, exp_type, n_hits")
for lem, et, n, picked in out:
    print(f"### {lem} [{et}] hits={n}")
    for c in picked:
        print(f"  ({c['form']}|{c['novel']}) {c['text']}")

# also dump full json for programmatic access
with open(os.path.join(os.path.dirname(__file__), "..", "notes", "_mined_psych_candidates_raw.json"), "w", encoding="utf-8") as f:
    json.dump({lem: by_verb[lem] for lem in by_verb}, f, ensure_ascii=False, indent=1)
print("\nTOTAL verbs with hits:", len(by_verb))
print("TOTAL sentences:", sum(len(v) for v in by_verb.values()))
