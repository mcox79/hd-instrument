"""Apply blind subject-head annotations to the sampled candidates -> gold JSONL in the problem folder.
Annotation = index (into text.split()) of the HEAD token of the MAIN finite clause's grammatical subject.
verb = index of that clause's main predicate (optional, for the strict secondary metric). None = SKIP
(no overt subject: imperative / fragment / existential-there expletive ambiguity)."""
import os, sys, json
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CAND = os.path.join(_REPO, "scratch", "role_candidates.jsonl")
OUT = os.path.join(_REPO, "notes", "problems", "role_assignment_is_untested_on_archaic_literary_prose")

# {cid: (subj_head_tok, verb_tok_or_None)}  ; cid absent or value None -> skipped
ARCH = {
    "arch-00": (1, 2), "arch-01": (0, 1), "arch-02": (0, 1), "arch-03": (6, 7), "arch-04": (0, 1),
    "arch-05": (6, 5), "arch-06": None, "arch-07": (1, 2), "arch-08": (2, 3), "arch-09": (0, 1),
    "arch-10": (1, 4), "arch-11": (1, 0), "arch-12": (0, 1), "arch-13": (1, 2), "arch-14": (1, 2),
    "arch-15": (3, 12), "arch-16": (12, 15), "arch-17": (5, 6), "arch-18": (8, 11), "arch-19": (19, 18),
    "arch-20": (1, 3), "arch-21": (0, 1), "arch-22": (0, 1), "arch-23": (0, 1), "arch-24": (0, 1),
    "arch-25": (5, 6), "arch-26": None, "arch-27": (1, 5), "arch-28": (0, 1), "arch-29": (12, 13),
    "arch-30": None, "arch-31": (1, 3), "arch-32": (14, 27), "arch-33": (13, 12), "arch-34": (10, 11),
    "arch-35": (2, 3), "arch-36": (1, 3), "arch-37": (10, 12), "arch-38": None, "arch-39": (19, 17),
    "arch-40": (1, 6), "arch-41": (10, 12), "arch-42": (0, 3), "arch-43": (0, 5), "arch-44": (1, 3),
    "arch-45": (0, 1), "arch-46": (1, 5), "arch-47": (4, 6), "arch-48": (0, 1), "arch-49": (4, 5),
    "arch-50": (0, 7), "arch-51": (1, 6), "arch-52": (0, 2), "arch-53": (9, 10), "arch-54": (0, 1),
    "arch-55": (0, 1),
}
MOD = {
    "mode-00": (1, 4), "mode-01": (0, 2), "mode-02": None, "mode-03": (2, 4), "mode-04": (0, 9),
    "mode-05": (2, 5), "mode-06": (1, 4), "mode-07": (0, 1), "mode-08": (0, 1), "mode-09": (1, 2),
    "mode-10": (1, 2), "mode-11": (3, 4), "mode-12": (3, 6), "mode-13": (2, 3), "mode-14": (6, 8),
    "mode-15": (3, 4), "mode-16": (0, 1), "mode-17": (2, 8), "mode-18": (1, 2), "mode-19": (1, 7),
    "mode-20": (1, 2), "mode-21": (1, 2), "mode-22": (1, 4), "mode-23": (12, 13), "mode-24": (9, 16),
    "mode-25": (2, 6), "mode-26": (2, 4), "mode-27": (0, 2), "mode-28": (5, 7), "mode-29": (3, 4),
    "mode-30": (2, 3), "mode-31": (2, 7), "mode-32": (3, 9), "mode-33": (4, 5), "mode-34": (2, 4),
    "mode-35": (0, 2), "mode-36": (2, 5), "mode-37": (1, 3), "mode-38": (1, 13), "mode-39": (1, 3),
    "mode-40": (1, 2), "mode-41": (18, 20), "mode-42": (1, 2), "mode-43": (18, 19), "mode-44": (7, 14),
    "mode-45": (0, 1), "mode-46": (2, 6), "mode-47": (19, 22), "mode-48": (6, 6), "mode-49": (0, 2),
    "mode-50": (18, 20), "mode-51": (1, 2), "mode-52": (16, 17), "mode-53": (0, 1), "mode-54": (0, 9),
    "mode-55": (1, 5),
}

cands = {}
with open(CAND, encoding="utf-8") as f:
    for line in f:
        d = json.loads(line)
        cands[d["cid"].lower()] = d


def emit(ann, fname, src_tag):
    n_skip = 0
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write("// blind subject-head gold; subj_tok/verb_tok index into text.split(); "
                "built from real corpus sentences (scratch/role_candidates). See SOLVED.md.\n")
        for cid, v in ann.items():
            d = cands[cid]
            toks = d["text"].split()
            if v is None:
                n_skip += 1
                continue
            subj, verb = v
            assert 0 <= subj < len(toks), f"{cid} subj {subj} oob"
            rec = {"cid": cid, "text": d["text"], "subj_tok": subj, "verb_tok": verb,
                   "src": d["src"], "len_bin": d["len_bin"],
                   "subj_head": toks[subj], "verb_word": toks[verb] if verb is not None else None}
            f.write(json.dumps(rec) + "\n")
    print(f"{fname}: {len(ann)-n_skip} items ({n_skip} skipped)")


emit(ARCH, "archaic_subject_gold_v1.jsonl", "archaic_litbank")
emit(MOD, "modern_subject_gold_v1.jsonl", "modern_textbook")
