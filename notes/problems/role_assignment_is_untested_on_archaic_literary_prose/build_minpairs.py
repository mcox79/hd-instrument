"""Register-controlled minimal pairs: archaic sentence <-> meaning/structure-preserving MODERN paraphrase
around the SAME subject entity, length-matched. Only REGISTER varies. Subject/verb given by WORD (index
resolved by the builder, occ = which occurrence) to avoid hand-index errors. Gold known by construction."""
import os, re, json
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(_REPO, "notes", "problems", "role_assignment_is_untested_on_archaic_literary_prose")


def find_tok(text, word, occ=0):
    toks = text.split()
    hits = [i for i, t in enumerate(toks) if re.sub(r"[^\w']", "", t).lower() == word.lower()]
    assert len(hits) > occ, f"'{word}' occ {occ} not found in: {text}"
    return hits[occ]


# (phenomenon, archaic, arch_subj, arch_verb, modern, mod_subj, mod_verb)   subj/verb = (word, occ)
PAIRS = [
    ("inversion_dialogue", "Said she, when the door was shut, that she would go.", ("she", 0), ("Said", 0),
     "She said, when the door was shut, that she would go.", ("She", 0), ("said", 0)),
    ("inversion_dialogue", '"I resolved not to disturb you," replied he to the anxious host.', ("he", 0), ("replied", 0),
     '"I resolved not to disturb you," he replied to the anxious host.', ("he", 0), ("replied", 0)),
    ("inversion_dialogue", '"Nonsense," cried the old man, and he struck the table.', ("man", 0), ("cried", 0),
     '"Nonsense," the old man cried, and he struck the table.', ("man", 0), ("cried", 0)),
    ("inversion_locative", "So was the black horned thing seated aloof upon a rock.", ("thing", 0), ("seated", 0),
     "The black horned thing was seated aloof upon a rock.", ("thing", 0), ("seated", 0)),
    ("inversion_locative", "Down came the heavy rain upon the ruined tower.", ("rain", 0), ("came", 0),
     "The heavy rain came down upon the ruined tower.", ("rain", 0), ("came", 0)),
    ("heavy_presubject", "Thirteen winters' revolving frosts had seen her open the ball.", ("frosts", 0), ("seen", 0),
     "The frosts of thirteen revolving winters had seen her open the ball.", ("frosts", 0), ("seen", 0)),
    ("heavy_presubject", "The whole seizure, progress, and termination of the disease were brief.", ("seizure", 0), ("were", 0),
     "The seizure, the progress, and the end of the disease were all brief.", ("seizure", 0), ("were", 0)),
    ("heavy_presubject", "The astonishment of the ladies at the news was exactly what he wished.", ("astonishment", 0), ("was", 0),
     "The ladies' astonishment at the news was exactly what he wished.", ("astonishment", 0), ("was", 0)),
    ("archaic_morph_hath", "For it hath a rounded and orbicular sound, and rings like bullion.", ("it", 0), ("hath", 0),
     "Because it has a rounded and orbicular sound, and rings like bullion.", ("it", 0), ("has", 0)),
    ("archaic_morph_ere", "Ere the sun had set, the weary knight departed from the hall.", ("knight", 0), ("departed", 0),
     "Before the sun had set, the weary knight departed from the hall.", ("knight", 0), ("departed", 0)),
    ("archaic_morph_thou", "Thou knowest well what a file is, and where it lies.", ("Thou", 0), ("knowest", 0),
     "You know well what a file is, and where it lies.", ("You", 0), ("know", 0)),
    ("archaic_morph_whilst", "Whilst the master slept, the two clerks copied the long document.", ("clerks", 0), ("copied", 0),
     "While the master slept, the two clerks copied the long document.", ("clerks", 0), ("copied", 0)),
    ("fronted_participial", "Observing his daughter at her work, the father addressed her kindly.", ("father", 0), ("addressed", 0),
     "The father, observing his daughter at her work, addressed her kindly.", ("father", 0), ("addressed", 0)),
    ("fronted_adjunct", "At the period just preceding the advent of the stranger, I had two clerks then.", ("I", 0), ("had", 0),
     "I had two clerks at the period just before the stranger arrived.", ("I", 0), ("had", 0)),
    ("long_subj_verb_gap", "The receiver in the great cause has acquired a goodly sum of money.", ("receiver", 0), ("acquired", 0),
     "The receiver in the great lawsuit has acquired a good sum of money.", ("receiver", 0), ("acquired", 0)),
    ("long_subj_verb_gap", "Her father, a proud and idle man, had held a government position for years.", ("father", 0), ("held", 0),
     "Her father, a proud and idle man, held a government position for years.", ("father", 0), ("held", 0)),
    ("subjunctive_inversion", "Were the danger known, they would rank it among their misfortunes.", ("danger", 0), ("Were", 0),
     "If the danger were known, they would rank it among their misfortunes.", ("danger", 0), ("were", 0)),
    ("quoth", "Quoth the raven to the frightened scholar, nevermore shall he rest.", ("raven", 0), ("Quoth", 0),
     "The raven said to the frightened scholar that he would never rest.", ("raven", 0), ("said", 0)),
    ("archaic_negation", "The master affirmed that he cared not for the crowd's opinion.", ("master", 0), ("affirmed", 0),
     "The master affirmed that he did not care for the crowd's opinion.", ("master", 0), ("affirmed", 0)),
    ("heavy_coordinate_subj", "The redness and the horror of the plague were its avatar and its seal.", ("redness", 0), ("were", 0),
     "The redness and the horror of the plague were its symbol and its mark.", ("redness", 0), ("were", 0)),
    ("archaic_relative", "The wall, black by age and everlasting shade, required no spy-glass.", ("wall", 0), ("required", 0),
     "The wall, blackened by age and endless shade, required no telescope.", ("wall", 0), ("required", 0)),
    ("object_fronting", "Full many a gem the dark unfathomed caves of ocean bear.", ("caves", 0), ("bear", 0),
     "The dark unfathomed caves of ocean bear full many a gem.", ("caves", 0), ("bear", 0)),
    ("archaic_aux_drop", "The knight, being wounded, spake not, but turned his horse away.", ("knight", 0), ("spake", 0),
     "The knight, being wounded, did not speak, but turned his horse away.", ("knight", 0), ("speak", 0)),
]

with open(os.path.join(OUT, "register_minimal_pairs_v1.jsonl"), "w", encoding="utf-8") as f:
    f.write("// register-controlled minimal pairs (archaic <-> modernized, same subject); tok indices "
            "into text.split(). Built for this problem; see SOLVED.md.\n")
    for i, (ph, at, asj, avb, mt, msj, mvb) in enumerate(PAIRS):
        a_s, a_v = find_tok(at, *asj), find_tok(at, *avb)
        m_s, m_v = find_tok(mt, *msj), find_tok(mt, *mvb)
        f.write(json.dumps({"pid": f"p{i:02d}", "phenomenon": ph,
                            "archaic": {"text": at, "subj_tok": a_s, "verb_tok": a_v, "subj_head": at.split()[a_s]},
                            "modern": {"text": mt, "subj_tok": m_s, "verb_tok": m_v, "subj_head": mt.split()[m_s]}}) + "\n")
print(f"wrote {len(PAIRS)} minimal pairs")
