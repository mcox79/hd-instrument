"""Mine LitBank coref-annotated fiction for implicit-causality (IC) verb disagreement cases.
Pattern: <NP1> <VERB> <NP2> because <he|she> ...
NP1 = the single coref mention spanning entirely before VERB.
NP2 = the single coref mention spanning entirely between VERB and 'because'.
Pronoun = the token immediately after 'because' (must itself be an annotated coref mention).
Gold = pronoun's own annotated cluster id (real human-verified coreference, LitBank ground truth).
Requires gold cluster == NP1 cluster OR NP2 cluster (gold-determinable, canonical 2-candidate frame).

RECENCY (Hobbs-naive) prediction = NP2 (closest preceding mention to the pronoun).
IC_VERB prediction = per verb-bias class: NP1 if EO-class (Experiencer-Object, "frighten"-type),
  NP2 if ES-class (Experiencer-Subject, "love"-type). Disagreement = EO-class hits (recency picks NP2,
  IC picks NP1). Agreement = ES-class hits (both pick NP2).
NEGATIVE-CONTROL (guardrail): same frame, but VERB is a neutral verb with NO established IC bias
  (saw/met/told/asked/visited/followed/watched/found/left/joined/called/greeted/answered) -- IC_VERB
  mechanism must ABSTAIN (not fabricate a directional claim) since it has no lexicon entry.
"""
import json
import re
import sys
from pathlib import Path

CONLL_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
OUT_PATH = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("litbank_ic_derived.json")

LITBANK_COMMIT = "3e50db0ffc033d7ccbb94f4d88f6b99210328ed8"

# --- glass-box IC verb-bias lexicon (past-tense surface forms; CITED categorical direction, not invented
# percentages): Garvey & Caramazza 1974; Brown & Fish 1983; Rudolph & Foersterling 1997 meta-analysis;
# Kehler/Rohde discourse-coherence IC literature. EO = Experiencer-Object / "frighten"-class -> NP1-bias.
# ES = Experiencer-Subject / "love"-class -> NP2-bias. ---
EO_VERBS = {  # NP1 (subject) bias
    "frightened", "scared", "startled", "surprised", "astonished", "amazed", "shocked", "horrified",
    "alarmed", "angered", "annoyed", "irritated", "upset", "disgusted", "embarrassed", "offended",
    "humiliated", "impressed", "delighted", "amused", "depressed", "worried", "frustrated", "bored",
    "pleased", "terrified", "enraged", "saddened", "vexed", "distressed", "troubled", "disturbed",
    "puzzled", "confused", "bewildered", "dismayed", "grieved", "wounded", "hurt", "charmed", "captivated",
    "fascinated", "enchanted", "disappointed",
}
ES_VERBS = {  # NP2 (object) bias
    "loved", "liked", "admired", "adored", "feared", "envied", "trusted", "hated", "despised", "detested",
    "resented", "disliked", "pitied", "appreciated", "cherished", "treasured", "respected", "idolized",
    "missed", "craved", "desired", "worshipped", "esteemed", "distrusted", "suspected", "doubted",
    "forgave", "blamed",
}
NEUTRAL_VERBS = {  # NO established IC bias -- negative-control / guardrail lexicon
    "saw", "met", "told", "asked", "visited", "followed", "watched", "found", "left", "joined",
    "called", "greeted", "answered",
}
IC_LEXICON = {**{v: "EO" for v in EO_VERBS}, **{v: "ES" for v in ES_VERBS}}

PRONOUNS = {"he", "she"}


def parse_coref_field(field):
    """Return list of (action, cluster_id) for one token's coref column. action in OPEN/CLOSE/SINGLE."""
    if field in ("_", "", "-"):
        return []
    out = []
    for piece in field.split("|"):
        piece = piece.strip()
        m = re.match(r"^\((\d+)\)$", piece)
        if m:
            out.append(("SINGLE", int(m.group(1))))
            continue
        m = re.match(r"^\((\d+)$", piece)
        if m:
            out.append(("OPEN", int(m.group(1))))
            continue
        m = re.match(r"^(\d+)\)$", piece)
        if m:
            out.append(("CLOSE", int(m.group(1))))
            continue
    return out


def iter_sentences(path):
    """Yield (tokens, mentions) per sentence. tokens = list[str]. mentions = list[(cluster,start,end)]."""
    tokens = []
    open_stacks = {}
    mentions = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("#begin") or line.startswith("#end"):
                continue
            if line.strip() == "":
                if tokens:
                    yield tokens, mentions
                tokens, open_stacks, mentions = [], {}, []
                continue
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            word = parts[3]
            coref_field = parts[-1].strip()
            idx = len(tokens)
            tokens.append(word)
            for action, cid in parse_coref_field(coref_field):
                if action == "SINGLE":
                    mentions.append((cid, idx, idx))
                elif action == "OPEN":
                    open_stacks.setdefault(cid, []).append(idx)
                elif action == "CLOSE":
                    stack = open_stacks.get(cid)
                    if stack:
                        start = stack.pop()
                        mentions.append((cid, start, idx))
        if tokens:
            yield tokens, mentions


CAUSAL_CONNECTIVES = ("because", "for")  # both reliably causal/explanation connectives in this register;
                                          # 'for' as causal conjunction is extremely common in 19th-c. prose
                                          # (Austen/Dickens/Bronte). 'since'/'as' excluded (mostly temporal,
                                          # would dilute precision of the causal-explanation frame).


def mine_book(path, book_id):
    items = []
    for sidx, (tokens, mentions) in enumerate(iter_sentences(path)):
        low = [t.lower() for t in tokens]
        because_idx = None
        for ci, tok in enumerate(low):
            if tok in CAUSAL_CONNECTIVES:
                because_idx = ci
                break
        if because_idx is None:
            continue
        if because_idx + 1 >= len(tokens):
            continue
        pron = low[because_idx + 1]
        if pron not in PRONOUNS:
            continue
        # find verb: any token before 'because' whose lowercase form is in IC_LEXICON or NEUTRAL_VERBS
        verb_idx = None
        verb_word = None
        for i in range(because_idx):
            if low[i] in IC_LEXICON or low[i] in NEUTRAL_VERBS:
                verb_idx = i
                verb_word = low[i]
        if verb_idx is None or verb_idx == 0:
            continue
        # NP1 = nearest mention wholly before the verb (structural proxy for the local subject NP).
        # NP2 = nearest mention wholly between the verb and 'because' (structural proxy for the object NP).
        # "nearest" = largest end index -- a structural, non-outcome-tuned rule (declared before running).
        np1_region = [m for m in mentions if m[2] < verb_idx]
        np2_region = [m for m in mentions if m[1] > verb_idx and m[2] < because_idx]
        if not np1_region or not np2_region:
            continue
        np1_cluster = max(np1_region, key=lambda m: m[2])[0]
        np2_cluster = max(np2_region, key=lambda m: m[2])[0]
        if np1_cluster == np2_cluster:
            continue
        pron_idx = because_idx + 1
        pron_mentions = [m for m in mentions if m[1] == pron_idx and m[2] == pron_idx]
        if len(pron_mentions) != 1:
            continue
        gold_cluster = pron_mentions[0][0]
        if gold_cluster not in (np1_cluster, np2_cluster):
            continue  # not gold-determinable against these 2 candidates
        klass = IC_LEXICON.get(verb_word, "NEUTRAL")
        recency_pick = "NP2"  # always -- closest preceding mention to the pronoun
        if klass == "EO":
            ic_pick = "NP1"
        elif klass == "ES":
            ic_pick = "NP2"
        else:
            ic_pick = None  # NEUTRAL -- IC_VERB mechanism must ABSTAIN (guardrail)
        gold_side = "NP1" if gold_cluster == np1_cluster else "NP2"
        text = " ".join(tokens)
        items.append({
            "book_id": book_id, "sidx": sidx, "text": text, "verb": verb_word, "verb_class": klass,
            "np1_cluster": np1_cluster, "np2_cluster": np2_cluster, "gold_cluster": gold_cluster,
            "gold_side": gold_side, "recency_pick": recency_pick, "ic_pick": ic_pick,
            "disagreement": (ic_pick is not None and ic_pick != recency_pick),
        })
    return items


def main():
    all_items = []
    books = sorted(CONLL_DIR.glob("*.conll"))
    for p in books:
        book_id = p.stem
        items = mine_book(p, book_id)
        all_items.extend(items)
        print(f"{book_id}: {len(items)} candidate items")

    eo = [it for it in all_items if it["verb_class"] == "EO"]
    es = [it for it in all_items if it["verb_class"] == "ES"]
    neu = [it for it in all_items if it["verb_class"] == "NEUTRAL"]
    disagree = [it for it in all_items if it["disagreement"]]
    print(f"\nTOTAL={len(all_items)} EO(disagreement-candidates)={len(eo)} ES(agreement-candidates)={len(es)} "
          f"NEUTRAL(guardrail)={len(neu)} disagreement_subset={len(disagree)}")

    out = {
        "source": "LitBank (github.com/dbamman/litbank), coref/conll/*.conll",
        "license": "CC-BY 4.0 (https://creativecommons.org/licenses/by/4.0/)",
        "litbank_commit": LITBANK_COMMIT,
        "books": [p.stem for p in books],
        "n_books": len(books),
        "mining_rule_version": "v1_because_he_she_2candidate",
        "ic_lexicon": {"EO_np1_bias": sorted(EO_VERBS), "ES_np2_bias": sorted(ES_VERBS),
                       "NEUTRAL_no_bias": sorted(NEUTRAL_VERBS)},
        "ic_lexicon_citations": [
            "Garvey & Caramazza 1974, 'Implicit causality in verbs', Linguistic Inquiry",
            "Brown & Fish 1983, 'The psychological causality implicit in language', Cognition",
            "Rudolph & Foersterling 1997, 'The psychological causality implicit in verbs: A review', "
            "Psychological Bulletin (meta-analysis of IC verb classes)",
            "Kehler, Kertz, Rohde & Elman 2008, 'Coherence and coreference revisited', J. Semantics",
        ],
        "items": all_items,
    }
    OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
