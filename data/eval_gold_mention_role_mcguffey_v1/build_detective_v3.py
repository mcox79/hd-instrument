# -*- coding: utf-8 -*-
"""
Build gold_causal_crossspan_detective_v3_DRAFT.jsonl: cross-span multi-candidate
causal-attribution items mined VERBATIM from public-domain Sherlock Holmes
short-story collections (Doyle, Adventures of Sherlock Holmes / Memoirs of
Sherlock Holmes, Project Gutenberg #1661 / #834). Companion to the
data/corpora/sherlock_holmes/clean_sherlock.py cleaning script.

For every item this script:
  1. Verifies each of the 3 spans (true_blocker_span, distractor_span,
     query_span) is a VERBATIM substring of the cited cleaned corpus file at
     (or within a small tolerance of) the claimed line_range. Any failure
     aborts the build (no item with a failing span guard is written).
  2. Computes a MEASURED recency-baseline prediction: whichever candidate
     span's line-range is numerically closer to the query_span's line
     (i.e., a naive "most recently mentioned agent" heuristic) is the
     recency baseline's pick. Records whether that pick equals the
     distractor (baseline WRONG, as required) or the true blocker
     (baseline right -- would disqualify the item, none observed here).
  3. Computes a MEASURED surface-valence check: a small hand-built
     violence/negative-affect lexicon is scored (raw token-count hits,
     case-insensitive) over each of true_blocker_span.text and
     distractor_span.text. "Nonseparating" is reported as an honest
     aggregate stat (does a naive score(distractor) > score(true) rule
     correctly separate true from distractor across the set, and by how
     much) -- not asserted per item without the number.

No paraphrase, no synthesized narrative text: every `text` field below is
typed out verbatim from the on-disk cleaned corpus files (hand-transcribed
by the item author, then mechanically verified against the source file by
this script -- if verification fails the item is dropped, not "fixed").
"""
import json
import os
import re

BASE = r"d:/AI/hd-instrument/data/corpora/sherlock_holmes/cleaned"
ADV = os.path.join(BASE, "adventures.clean.txt")
MEM = os.path.join(BASE, "memoirs.clean.txt")
OUT = r"d:/AI/hd-instrument/data/eval_gold_mention_role_mcguffey_v1/gold_causal_crossspan_detective_v3_DRAFT.jsonl"

VALENCE_LEXICON = [
    "blood", "villain", "thief", "murder", "murdered", "struck", "strike",
    "kill", "killed", "dead", "died", "stole", "stolen", "guilty", "crime",
    "criminal", "wicked", "cry", "cried", "scream", "shriek", "fear",
    "frightened", "danger", "weapon", "gun", "knife", "stab", "strangle",
    "horror", "terror", "convulsed", "dying", "suicide", "hanged",
]


def load(path):
    with open(path, encoding="utf-8") as f:
        return f.readlines()


ADV_LINES = load(ADV)
MEM_LINES = load(MEM)


def norm(s):
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"')
    s = s.replace("—", "-").replace("–", "-")
    return s


def substring_guard(source, line_range, text):
    lines = ADV_LINES if source == "adventures" else MEM_LINES
    lo, hi = line_range
    # generous window: +/- 2 lines around claimed range to tolerate
    # off-by-one line counting between tools
    window = "".join(lines[max(0, lo - 3):hi + 2])
    hay = norm(window)
    needle = norm(text)
    ok = needle in hay
    return ok


def valence_score(text):
    t = text.lower()
    return sum(len(re.findall(r"\b" + re.escape(w) + r"\b", t)) for w in VALENCE_LEXICON)


def recency_prediction(item):
    q_line = item["query_span"]["line_range"][1]
    tb_line = item["true_blocker_span"]["line_range"][1]
    db_line = item["distractor_span"]["line_range"][1]
    d_true = abs(q_line - tb_line)
    d_distr = abs(q_line - db_line)
    # recency baseline = whichever candidate's span sits closer (in raw
    # line distance) to the query point -- "most recently/saliently
    # mentioned agent wins"
    if d_distr < d_true:
        return item["distractor_agent"], "distractor"
    elif d_true < d_distr:
        return item["true_blocker_agent"], "true_blocker"
    else:
        return "TIE", "tie"


ITEMS = [
    dict(
        id="crossspan_det_001",
        item_type="multi_candidate_causal_attribution",
        source="adventures", story="The Boscombe Valley Mystery",
        goal_owner="Sherlock Holmes / Lestrade / the inquest jury (identify who killed Charles McCarthy)",
        true_blocker_agent="John Turner",
        true_blocker_span=dict(line_range=[3879, 3882], source="adventures", text="and fairly strong of limb, I knew that my own fate was sealed. But my\nmemory and my girl! Both could be saved if I could but silence that\nfoul tongue. I did it, Mr. Holmes. I would do it again. Deeply as I\nhave sinned, I have led a life of martyrdom to atone for it. But that"),
        distractor_agent="James McCarthy (the victim's son)",
        distractor_span=dict(line_range=[2985, 2989], source="adventures", text="the words when young Mr. McCarthy came running up to the lodge to say\nthat he had found his father dead in the wood, and to ask for the help\nof the lodge-keeper. He was much excited, without either his gun or his\nhat, and his right hand and sleeve were observed to be stained with\nfresh blood."),
        query_span=dict(line_range=[3007, 3008], source="adventures", text="must be confessed, however, that the case looks exceedingly grave\nagainst the young man, and it is very possible that he is indeed the"),
        coherence_note="Turner's confession (revealed ~870 lines after the query point) is the true cause: he killed McCarthy, an old associate blackmailing him over a shared criminal past in Australia, to protect his daughter Alice from being forced to marry McCarthy's son. James McCarthy's blood-stained hand and the overheard quarrel are real but coincidental -- he found his father's body and tried to help, which is why he is covered in blood and was 'instantly arrested' with a coroner's verdict of wilful murder against him.",
    ),
    dict(
        id="crossspan_det_002",
        item_type="multi_candidate_causal_attribution",
        source="adventures", story="The Adventure of the Blue Carbuncle",
        goal_owner="the Cosmopolitan Hotel / the police magistrate (identify who stole the Countess of Morcar's blue carbuncle)",
        true_blocker_agent="James Ryder (the hotel upper-attendant)",
        true_blocker_span=dict(line_range=[6562, 6569], source="adventures", text="pretty villain in you. You knew that this man Horner, the plumber, had\nbeen concerned in some such matter before, and that suspicion would\nrest the more readily upon him. What did you do, then? You made some\nsmall job in my lady’s room—you and your confederate Cusack—and you\nmanaged that he should be the man sent for. Then, when he had left, you\nrifled the jewel-case, raised the alarm, and had this unfortunate man\narrested. You then—"),
        distractor_agent="John Horner (the plumber)",
        distractor_span=dict(line_range=[6068, 6070], source="adventures", text="“Hotel Cosmopolitan Jewel Robbery. John Horner, 26, plumber, was\nbrought up upon the charge of having upon the 22nd inst., abstracted\nfrom the jewel-case of the Countess of Morcar the valuable gem known as"),
        query_span=dict(line_range=[6153, 6153], source="adventures", text="“Do you think that this man Horner is innocent?”"),
        coherence_note="Horner is the officially charged suspect throughout (arrested same evening, prior-conviction evidence used against him at the magistrate's hearing) -- a textbook recency/reputation trap. Holmes's reconstruction, confirmed almost 400 lines later when Ryder breaks down and confesses, is that Ryder framed Horner deliberately (arranged for Horner to be the plumber sent for, then staged the theft) to divert suspicion from himself.",
    ),
    dict(
        id="crossspan_det_003",
        item_type="multi_candidate_causal_attribution",
        source="adventures", story="The Adventure of the Beryl Coronet",
        goal_owner="Alexander Holder the banker (identify who broke the beryl coronet and took the missing gems)",
        true_blocker_agent="Mary Holder (the banker's niece) and Sir George Burnwell (her secret lover)",
        true_blocker_span=dict(line_range=[10598, 10600], source="adventures", text="for you to hear: there has been an understanding between Sir George\nBurnwell and your niece Mary. They have now fled together."),
        distractor_agent="Arthur Holder (the banker's son)",
        distractor_span=dict(line_range=[10065, 10066], source="adventures", text="“‘Arthur!’ I screamed, ‘you villain! you thief! How dare you touch that\ncoronet?’"),
        query_span=dict(line_range=[10171, 10171], source="adventures", text="“You have neither of you any doubt as to your son’s guilt?”"),
        coherence_note="Arthur is caught red-handed, at night, physically holding and bending the coronet -- an eyewitness catch that his own father treats as conclusive. The true story, which Arthur silently protects by refusing to explain himself (he was intercepting the gems, not stealing them), only comes out roughly 500 lines later: Mary stole the gems for Burnwell, and Arthur caught and fought Burnwell for them, breaking off the missing piece in the struggle.",
    ),
    dict(
        id="crossspan_det_004",
        item_type="multi_candidate_causal_attribution",
        source="adventures", story="The Adventure of the Speckled Band",
        goal_owner="Holmes / Helen Stoner (identify what killed Julia Stoner, whose last words named 'the speckled band')",
        true_blocker_agent="Dr. Grimesby Roylott (via the trained swamp adder he kept and released through the ventilator)",
        true_blocker_span=dict(line_range=[7768, 7774], source="adventures", text="“The band! the speckled band!” whispered Holmes.\n\nI took a step forward. In an instant his strange headgear began to\nmove, and there reared itself from among his hair the squat\ndiamond-shaped head and puffed neck of a loathsome serpent.\n\n“It is a swamp adder!” cried Holmes; “the deadliest snake in India. He"),
        distractor_agent="the wandering gipsies camped on Dr. Roylott's land",
        distractor_span=dict(line_range=[7061, 7072], source="adventures", text="“Were there gipsies in the plantation at the time?”\n\n“Yes, there are nearly always some there.”\n\n“Ah, and what did you gather from this allusion to a band—a speckled\nband?”\n\n“Sometimes I have thought that it was merely the wild talk of delirium,\nsometimes that it may have referred to some band of people, perhaps to\nthese very gipsies in the plantation. I do not know whether the spotted\nhandkerchiefs which so many of them wear over their heads might have\nsuggested the strange adjective which she used."),
        query_span=dict(line_range=[7056, 7056], source="adventures", text="“What do you think that this unfortunate lady died of, then?”"),
        coherence_note="The word 'band' itself is the misdirection: Julia's dying phrase 'the speckled band' is immediately (and reasonably) read as a 'band of gipsies' with spotted handkerchiefs camped nearby -- surface lexical overlap on the word 'band', not causal evidence. The true referent, confirmed roughly 700 lines later, is literal: a speckled swamp adder Dr. Roylott trained and released into the girls' room through a fake ventilator.",
    ),
    dict(
        id="crossspan_det_005",
        item_type="multi_candidate_causal_attribution",
        source="adventures", story="The Man with the Twisted Lip",
        goal_owner="Mrs. St. Clair / the police (identify what happened to Neville St. Clair, feared murdered)",
        true_blocker_agent="Neville St. Clair himself (living a secret double life as the beggar 'Hugh Boone')",
        true_blocker_span=dict(line_range=[5631, 5632], source="adventures", text="“Let me introduce you,” he shouted, “to Mr. Neville St. Clair, of Lee,\nin the county of Kent.”"),
        distractor_agent="Hugh Boone (the disfigured beggar found in the room)",
        distractor_span=dict(line_range=[5202, 5204], source="adventures", text="“No, sir, but the facts might be met speciously enough. Suppose that\nthis man Boone had thrust Neville St. Clair through the window, there\nis no human eye which could have seen the deed."),
        query_span=dict(line_range=[5226, 5228], source="adventures", text="Neville St. Clair was doing in the opium den, what happened to him when\nthere, where is he now, and what Hugh Boone had to do with his\ndisappearance—are all as far from a solution as ever."),
        coherence_note="Boone is the only human found in the room, blood-stained window ledge and all, and is arrested as the presumed murderer. The true resolution (roughly 400 lines later) is that no crime occurred: St. Clair grimed and disguised himself as Boone years earlier to earn far more as a beggar than as a journalist, and panicked into hiding his identity when his wife nearly caught him mid-transformation.",
    ),
    dict(
        id="crossspan_det_006",
        item_type="multi_candidate_causal_attribution",
        source="memoirs", story="Silver Blaze",
        goal_owner="Inspector Gregory / Colonel Ross (identify who killed trainer John Straker)",
        true_blocker_agent="Silver Blaze (the racehorse), reacting in fright to Straker's own attempt to injure it",
        true_blocker_span=dict(line_range=[1142, 1153], source="memoirs", text="“From that time on all was plain. Straker had led out the horse\nto a hollow where his light would be invisible. Simpson in his\nflight had dropped his cravat, and Straker had picked it up—with\nsome idea, perhaps, that he might use it in securing the horse’s\nleg. Once in the hollow, he had got behind the horse and had\nstruck a light; but the creature frightened at the sudden glare,\nand with the strange instinct of animals feeling that some\nmischief was intended, had lashed out, and the steel shoe had\nstruck Straker full on the forehead. He had already, in spite of\nthe rain, taken off his overcoat in order to do his delicate\ntask, and so, as he fell, his knife gashed his thigh. Do I make\nit clear?”"),
        distractor_agent="Fitzroy Simpson (the stranger found near the stables)",
        distractor_span=dict(line_range=[300, 303], source="memoirs", text="he promptly found and arrested the man upon whom suspicion\nnaturally rested. There was little difficulty in finding him, for\nhe inhabited one of those villas which I have mentioned. His\nname, it appears, was Fitzroy Simpson."),
        query_span=dict(line_range=[654, 656], source="memoirs", text="“It’s this way, Watson,” said he at last. “We may leave the\nquestion of who killed John Straker for the instant, and confine\nourselves to finding out what has become of the horse."),
        coherence_note="Simpson is arrested on the spot (suspicious presence, betting motive, blood-marked stick, dropped cravat found on the body). The true cause, confirmed roughly 300 lines after the query, is that Straker himself was secretly lame-ing the horse for an insurance/betting fraud, and Silver Blaze kicked him in fright mid-attempt -- Straker's own scheme causing his death, not a human murderer.",
    ),
    dict(
        id="crossspan_det_007",
        item_type="multi_candidate_causal_attribution",
        source="memoirs", story="The Crooked Man",
        goal_owner="the Aldershot police / Holmes (identify who killed Colonel James Barclay)",
        true_blocker_agent="Colonel James Barclay himself (died of apoplexy, guilt-triggered by a visit from a wronged man from his own past)",
        true_blocker_span=dict(line_range=[7175, 7177], source="memoirs", text="“The inquest is just over. The medical evidence showed\nconclusively that death was due to apoplexy. You see it was quite\na simple case after all."),
        distractor_agent="Mrs. Nancy Barclay (the Colonel's wife)",
        distractor_span=dict(line_range=[6851, 6853], source="memoirs", text="she held the facts in her possession, and of assuring her that\nher friend, Mrs. Barclay, might find herself in the dock upon a\ncapital charge unless the matter were cleared up."),
        query_span=dict(line_range=[6864, 6866], source="memoirs", text="when so serious a charge is laid against her, and when her\nown mouth, poor darling, is closed by illness, then I think I am\nabsolved from my promise."),
        coherence_note="Mrs. Barclay is found locked in a room with her unconscious husband after a violent quarrel, and is treated by the police as the likely murderer facing a capital charge. The true story, confirmed roughly 150 lines after the query, is that Barclay collapsed of apoplexy from guilt and shock on being confronted by Henry Wood, a man he had once wronged and left for dead decades earlier -- no one struck him.",
    ),
    dict(
        id="crossspan_det_008",
        item_type="multi_candidate_causal_attribution",
        source="memoirs", story="The Naval Treaty",
        goal_owner="Percy Phelps / the police (identify who stole the naval treaty from the Foreign Office)",
        true_blocker_agent="Joseph Harrison (Percy Phelps's future brother-in-law)",
        true_blocker_span=dict(line_range=[10451, 10458], source="memoirs", text="“The facts of the case, as far as I have worked them out, are\nthese: this Joseph Harrison entered the office through the\nCharles Street door, and knowing his way he walked straight into\nyour room the instant after you left it. Finding no one there he\npromptly rang the bell, and at the instant that he did so his\neyes caught the paper upon the table. A glance showed him that\nchance had put in his way a State document of immense value, and\nin an instant he had thrust it into his pocket and was gone."),
        distractor_agent="Tangey the commissionaire (and his wife)",
        distractor_span=dict(line_range=[9694, 9697], source="memoirs", text="“Tangey, the commissionnaire, has been shadowed. He left the\nGuards with a good character and we can find nothing against him.\nHis wife is a bad lot, though. I fancy she knows more about this\nthan appears.”"),
        query_span=dict(line_range=[9692, 9692], source="memoirs", text="“What steps have you taken?”"),
        coherence_note="The commissionaire's household is the only concrete lead the police are actively working (shadowing Tangey, surveilling his wife) for most of the story. The true culprit, confirmed roughly 750 lines later in Holmes's reconstruction, is Joseph Harrison, who happened to walk into the empty office and impulsively pocketed the treaty when he saw it lying on the table.",
    ),
    dict(
        id="crossspan_det_009",
        item_type="multi_candidate_causal_attribution",
        source="memoirs", story="The Resident Patient",
        goal_owner="Dr. Percy Trevelyan / Inspector Lanner (identify what happened to the lodger Blessington)",
        true_blocker_agent="Biddle, Hayward, and Moffat (former confederates of the Worthingdon bank gang Blessington had betrayed)",
        true_blocker_span=dict(line_range=[7954, 7956], source="memoirs", text="“Well, at least I have got their identity. This so-called\nBlessington is, as I expected, well known at headquarters, and so\nare his assailants. Their names are Biddle, Hayward, and Moffat.”"),
        distractor_agent="Blessington himself (the suicide theory)",
        distractor_span=dict(line_range=[7744, 7744], source="memoirs", text="“Blessington has committed suicide!”"),
        query_span=dict(line_range=[7729, 7729], source="memoirs", text="“Any fresh news?”"),
        coherence_note="Blessington is found hanged in his own locked room, and the first, most textually salient explanation offered is straightforward suicide. Roughly 225 lines later, Holmes shows the death was staged: three former gang members Blessington had informed on years earlier broke in and strangled him, then hanged the body to fake self-destruction.",
    ),
    dict(
        id="crossspan_det_010",
        item_type="multi_candidate_causal_attribution",
        source="adventures", story="The Noble Bachelor",
        goal_owner="Lord St. Simon / Inspector Lestrade (identify what became of Lady St. Simon, missing since her own wedding breakfast)",
        true_blocker_agent="Hatty Doran (Lady St. Simon) herself, choosing on impulse to leave with her already-secret husband",
        true_blocker_span=dict(line_range=[9519, 9523], source="adventures", text="“Oh, yes, I know that I have treated you real bad and that I should\nhave spoken to you before I went; but I was kind of rattled, and from\nthe time when I saw Frank here again I just didn’t know what I was\ndoing or saying. I only wonder I didn’t fall down and do a faint right\nthere before the altar.”"),
        distractor_agent="Flora Millar (Lord St. Simon's former mistress)",
        distractor_span=dict(line_range=[9386, 9391], source="adventures", text="upon the table in front of him. “Listen to this: ‘You will see me when\nall is ready. Come at once. F. H. M.’ Now my theory all along has been\nthat Lady St. Simon was decoyed away by Flora Millar, and that she,\nwith confederates, no doubt, was responsible for her disappearance.\nHere, signed with her initials, is the very note which was no doubt\nquietly slipped into her hand at the door and which lured her within"),
        query_span=dict(line_range=[9319, 9320], source="adventures", text="“And I feel dissatisfied. It is this infernal St. Simon marriage case.\nI can make neither head nor tail of the business.”"),
        coherence_note="Lestrade builds a concrete kidnapping theory around Flora Millar (jealous ex-mistress, a note signed with her initials, dragging the Serpentine for a body) roughly 70 lines after the query. The true story, confirmed later when Hatty explains herself directly, is that she left of her own free will on seeing her already-married first husband Frank Moulton at the wedding -- no abduction, no Flora Millar involvement.",
    ),
]


def build():
    out_items = []
    fail = []
    for it in ITEMS:
        ok_tb = substring_guard(it["true_blocker_span"]["source"], it["true_blocker_span"]["line_range"], it["true_blocker_span"]["text"])
        ok_db = substring_guard(it["distractor_span"]["source"], it["distractor_span"]["line_range"], it["distractor_span"]["text"])
        ok_qs = substring_guard(it["query_span"]["source"], it["query_span"]["line_range"], it["query_span"]["text"])
        guard = dict(true_blocker_span=ok_tb, distractor_span=ok_db, query_span=ok_qs)
        if not (ok_tb and ok_db and ok_qs):
            fail.append((it["id"], guard))
            continue

        recency_pick, recency_pick_kind = recency_prediction(it)
        recency_baseline_correct = (recency_pick_kind == "true_blocker")

        v_true = valence_score(it["true_blocker_span"]["text"])
        v_distr = valence_score(it["distractor_span"]["text"])

        rec = dict(
            id=it["id"],
            item_type=it["item_type"],
            source_work=it["story"],
            source_file=("data/corpora/sherlock_holmes/cleaned/adventures.clean.txt" if it["true_blocker_span"]["source"] == "adventures" else "data/corpora/sherlock_holmes/cleaned/memoirs.clean.txt"),
            citation=("Arthur Conan Doyle, The Adventures of Sherlock Holmes, Project Gutenberg eBook #1661 (public domain, US)" if it["true_blocker_span"]["source"] == "adventures" else "Arthur Conan Doyle, The Memoirs of Sherlock Holmes, Project Gutenberg eBook #834 (public domain, US)"),
            goal_owner=it["goal_owner"],
            true_blocker_agent=it["true_blocker_agent"],
            true_blocker_span=it["true_blocker_span"],
            distractor_agent=it["distractor_agent"],
            distractor_span=it["distractor_span"],
            query_span=it["query_span"],
            recency_baseline_prediction=recency_pick,
            recency_baseline_correct=recency_baseline_correct,
            measured_recency_gap_lines=dict(
                query_to_true=abs(it["query_span"]["line_range"][1] - it["true_blocker_span"]["line_range"][1]),
                query_to_distractor=abs(it["query_span"]["line_range"][1] - it["distractor_span"]["line_range"][1]),
            ),
            surface_valence_score=dict(true_blocker=v_true, distractor=v_distr, distractor_minus_true=v_distr - v_true),
            coherence_note=it["coherence_note"],
            span_reuse_check="unique -- sourced from a distinct story from every other item in this file",
            substring_guard=guard,
            gold_verified=False,
            needs_director_review=True,
            verify_flag="VERIFY: substring-guard PASS (script-checked, see substring_guard field); Director should re-confirm agent-caused framing and line_range fidelity by reading the cited passage in context.",
        )
        out_items.append(rec)

    with open(OUT, "w", encoding="utf-8", newline="") as f:
        for rec in out_items:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    return out_items, fail


if __name__ == "__main__":
    items, fail = build()
    n = len(items)
    n_recency_wrong = sum(1 for it in items if not it["recency_baseline_correct"])
    n_valence_separating = sum(1 for it in items if it["surface_valence_score"]["distractor_minus_true"] > 0)
    print(json.dumps(dict(
        n_built=n,
        n_failed_guard=len(fail),
        failed_ids=[f[0] for f in fail],
        recency_wrong_rate=f"{n_recency_wrong}/{n}",
        surface_valence_distractor_gt_true_rate=f"{n_valence_separating}/{n}",
        per_item_valence=[(it["id"], it["surface_valence_score"]) for it in items],
    ), indent=2))
