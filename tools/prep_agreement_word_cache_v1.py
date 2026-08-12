#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prep_agreement_word_cache_v1: build a SMALL committed WORD-STREAM cache for the FAIR (Elman-faithful)
agreement predictive-hierarchy probe. Unlike agreement_probe_cache_v1 (lexeme-free 12-symbol stream),
this stores the REAL WORD prefix (orig_sentence up to the verb) so a CA3 next-WORD predictor can learn
from the real lexical stream (Elman's result requires the real words).

Input (local only, NOT committed): data/corpora/agreement/agr_50.tsv.gz (Linzen Dupoux Goldberg 2016).
Output (SMALL, committed): data/corpora/agreement/agreement_word_cache_v1.json.gz

Per item (reuses parse_row's noun/number/subject logic; ADDS the real word prefix):
  words        : real prefix word tokens (orig_sentence[0:verb_index-1]), lowercased
  noun_word_idx: word-position (0-based into words) of each prefix noun
  nums         : number per prefix noun (1 plural / 0 singular) -- surface morphology (POS), allowed input
  subj_pos     : index into nums/noun_word_idx of the SUBJECT noun (SNF key + head-identity ORACLE;
                 NOT fed to the inducer -- head identity must be INDUCED)
  label        : verb number (1 plural / 0 singular) == subject number
  ndiff        : attractor count (0..4)
  subj_word    : subject surface word (novel-lexeme held-out split key ONLY; never fed to encoder)

Same per-bin balancing caps as agreement_probe_cache_v1 so the majority-SNF bar stays comparable
(29443 majority SNF = 0.6269). ASCII only. No push, no store write.
"""
from __future__ import annotations

import gzip
import json
import os
import sys
from collections import Counter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(REPO_ROOT, "data", "corpora", "agreement", "agr_50.tsv.gz")
OUT = os.path.join(REPO_ROOT, "data", "corpora", "agreement", "agreement_word_cache_v1.json.gz")

NOUN_TAGS = {"NN", "NNP", "NNS", "NNPS"}
PLURAL_NOUN = {"NNS", "NNPS"}

BIN_TARGET = {0: 4000, 1: 4000, 2: 3000, 3: 3000, 4: 2000}


def cell_cap(ndiff):
    return BIN_TARGET.get(ndiff, 0) // 2


def parse_row_word(fields):
    # 1=orig_sentence 2=pos_sentence 3=subj 8=verb_pos 9=subj_index 10=verb_index 13=n_diff_intervening
    try:
        orig = fields[1].split()
        pos_sentence = fields[2].split()
        subj_word = fields[3]
        verb_pos = fields[8]
        subj_index = int(fields[9])   # 1-based
        verb_index = int(fields[10])  # 1-based
        ndiff = int(fields[13])
    except (IndexError, ValueError):
        return None
    if verb_pos not in ("VBP", "VBZ"):
        return None
    label = 1 if verb_pos == "VBP" else 0
    n = len(pos_sentence)
    if len(orig) != n:            # orig_sentence must be token-aligned with pos_sentence
        return None
    if verb_index < 2 or verb_index > n or subj_index < 1 or subj_index >= verb_index:
        return None
    words = [orig[k].lower() for k in range(verb_index - 1)]   # tokens strictly before the verb
    nums = []
    noun_word_idx = []
    subj_pos = -1
    for pos in range(1, verb_index):  # 1-based positions strictly before the verb
        tag = pos_sentence[pos - 1]
        if tag not in NOUN_TAGS:
            continue
        if pos == subj_index:
            subj_pos = len(nums)
        nums.append(1 if tag in PLURAL_NOUN else 0)
        noun_word_idx.append(pos - 1)   # 0-based word position of this noun
    if subj_pos < 0 or len(nums) < 1 or len(words) < 1:
        return None
    if nums[subj_pos] != label:         # grammatical-corpus sanity (drop rare mismatch)
        return None
    return {
        "words": words,
        "noun_word_idx": noun_word_idx,
        "nums": nums,
        "subj_pos": subj_pos,
        "label": label,
        "ndiff": ndiff if ndiff <= 4 else 4,
        "subj_word": subj_word,
    }


def build_linzen():
    if not os.path.exists(CORPUS):
        print("FATAL: corpus not found at %s" % CORPUS, flush=True)
        sys.exit(2)
    cell_count = Counter()
    kept = []
    seen = 0
    with gzip.open(CORPUS, "rt", encoding="utf-8", errors="replace") as f:
        f.readline()  # header
        for line in f:
            seen += 1
            if seen % 200000 == 0:
                print("[prep-word] scanned=%d kept=%d" % (seen, len(kept)), flush=True)
            rec = parse_row_word(line.rstrip("\n").split("\t"))
            if rec is None:
                continue
            key = (rec["ndiff"], rec["label"])
            if cell_count[key] >= cell_cap(rec["ndiff"]):
                continue
            cell_count[key] += 1
            kept.append(rec)
            if all(cell_count[(b, l)] >= cell_cap(b) for b in BIN_TARGET for l in (0, 1)):
                print("[prep-word] all cells full at scanned=%d" % seen, flush=True)
                break
    print("[prep-word] done: scanned=%d kept=%d cells=%s" % (seen, len(kept), dict(cell_count)), flush=True)
    return kept


def main():
    linzen = build_linzen()
    payload = {
        "schema_version": "agreement_word_cache_v1",
        "source": "Linzen Dupoux Goldberg 2016 (agr_50_mostcommon_10K); real word stream (orig_sentence)",
        "bin_target": BIN_TARGET,
        "n_linzen": len(linzen),
        "linzen": linzen,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with gzip.open(OUT, "wt", encoding="utf-8") as f:
        json.dump(payload, f, separators=(",", ":"))
    print("[prep-word] wrote %s (%d items, %.2f MB)"
          % (OUT, len(linzen), os.path.getsize(OUT) / 1e6), flush=True)


if __name__ == "__main__":
    main()
