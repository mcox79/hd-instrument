# -*- coding: utf-8 -*-
"""
Chapter-level same-gender named-entity + pronoun co-presence density for
Anne of Green Gables (cleaned/anne_of_green_gables.clean.txt).

Verifies (does not assume) the literary claim in
notes/curriculum_selection_for_self_improving_reader_2026-08-02.md: "6-8
co-present female characters with genuine pronoun ambiguity." This is a
DENSITY MEASUREMENT, not a coreference SOLVER -- it counts named-entity
first-name mentions per chapter (name list curated by inspecting the top-60
recurring capitalized tokens in the corpus, see console output of that scan)
and 3rd-person-singular-female pronoun tokens ("she"/"her"/"hers"), then
reports how many DISTINCT female characters are co-present per chapter. It
does not resolve which pronoun points to which name -- that ambiguity-
resolution is exactly the coref mechanism's job, not this gate's.

Pure stdlib. ASCII-only script; corpus text itself has curly quotes (data,
not code, kept verbatim per the cleaner's no-content-stripping rule).
"""
import json
import re
from collections import Counter, defaultdict

BASE = r"d:/AI/hd-instrument/data/corpora/anne_of_green_gables/cleaned"
CLEAN = BASE + "/anne_of_green_gables.clean.txt"
CHAPTERS = BASE + "/anne_of_green_gables.chapters.json"
OUT = BASE + "/gender_coref_density_report.json"

# Curated from top-60 recurring capitalized-token scan of the cleaned corpus.
# First names only (avoids surname ambiguity like "Cuthbert" = Matthew OR Marilla).
FEMALE_NAMES = {"Anne", "Marilla", "Diana", "Jane", "Ruby", "Josie", "Rachel",
                 "Josephine", "Cordelia", "Minnie", "Prissy", "Stacy"}
MALE_NAMES = {"Matthew", "Gilbert", "Moody"}

FEMALE_PRON = re.compile(r"\b(she|her|hers|herself)\b", re.I)
MALE_PRON = re.compile(r"\b(he|him|his|himself)\b", re.I)


def load_chapters():
    lines = open(CLEAN, encoding="utf-8").read().split("\n")
    chapters = json.load(open(CHAPTERS, encoding="utf-8"))
    bounds = []
    for i, ch in enumerate(chapters):
        start = ch["start_out_idx"]
        end = chapters[i + 1]["start_out_idx"] if i + 1 < len(chapters) else len(lines)
        bounds.append((ch["num"], ch["title"], start, end))
    return lines, bounds


def name_tokens(text):
    return re.findall(r"[A-Za-z][A-Za-z'\-]*", text)


def main():
    lines, bounds = load_chapters()
    per_chapter = []
    for num, title, start, end in bounds:
        chunk = "\n".join(lines[start:end])
        toks = name_tokens(chunk)
        name_counts = Counter(t for t in toks if t in FEMALE_NAMES or t in MALE_NAMES)
        female_present = sorted(n for n in FEMALE_NAMES if name_counts.get(n, 0) > 0)
        male_present = sorted(n for n in MALE_NAMES if name_counts.get(n, 0) > 0)
        n_female_mentions = sum(name_counts.get(n, 0) for n in FEMALE_NAMES)
        n_male_mentions = sum(name_counts.get(n, 0) for n in MALE_NAMES)
        n_she_pron = len(FEMALE_PRON.findall(chunk))
        n_he_pron = len(MALE_PRON.findall(chunk))
        n_words = len(toks)
        per_chapter.append(dict(
            chapter=num, title=title, n_words=n_words,
            distinct_female_named=len(female_present),
            female_named_present=female_present,
            distinct_male_named=len(male_present),
            male_named_present=male_present,
            n_female_name_mentions=n_female_mentions,
            n_male_name_mentions=n_male_mentions,
            n_she_her_pronouns=n_she_pron,
            n_he_him_pronouns=n_he_pron,
            she_pron_per1kw=round(1000 * n_she_pron / n_words, 2) if n_words else 0,
            multi_female_coref_risk=(len(female_present) >= 2 and n_she_pron >= 5),
        ))

    n_ch = len(per_chapter)
    dist_female = [c["distinct_female_named"] for c in per_chapter]
    risk_chapters = [c["chapter"] for c in per_chapter if c["multi_female_coref_risk"]]
    ge2_chapters = [c["chapter"] for c in per_chapter if c["distinct_female_named"] >= 2]
    ge3_chapters = [c["chapter"] for c in per_chapter if c["distinct_female_named"] >= 3]

    summary = dict(
        n_chapters=n_ch,
        distinct_female_named_distribution=dict(Counter(dist_female)),
        mean_distinct_female_named_per_chapter=round(sum(dist_female) / n_ch, 2),
        max_distinct_female_named_in_a_chapter=max(dist_female),
        chapters_with_ge2_female_named=len(ge2_chapters), ge2_chapter_list=ge2_chapters,
        chapters_with_ge3_female_named=len(ge3_chapters), ge3_chapter_list=ge3_chapters,
        chapters_with_multi_female_coref_risk_ge2named_ge5pron=len(risk_chapters),
        risk_chapter_list=risk_chapters,
        female_names_ever_appearing=sorted({n for c in per_chapter for n in c["female_named_present"]}),
        note="distinct_female_named counts NAMED-CHARACTER PRESENCE per chapter from a curated "
             "first-name list; it does NOT verify pronoun-to-referent ambiguity (that requires "
             "the coref mechanism itself). ge2/ge3 chapter counts are the density proxy for the "
             "literary claim of 6-8 co-present female characters ACROSS THE BOOK (not all-at-once "
             "in one chapter -- see max_distinct_female_named_in_a_chapter for the single-chapter peak).",
    )
    out = dict(summary=summary, per_chapter=per_chapter)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
