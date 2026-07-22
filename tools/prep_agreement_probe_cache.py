#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prep_agreement_probe_cache: stream the Linzen 2016 Wikipedia agreement corpus (local, 631MB)
and build a SMALL committed feature cache for the agreement-attractor role-binding CG viability probe.

Input (local only, NOT committed):
  data/corpora/agreement/agr_50.tsv.gz  (Linzen, Dupoux & Goldberg 2016; public Dropbox)
Optional cross-check (local): data/corpora/agreement/gulordava_english/generated.tab (nonce).

Output (SMALL, committed so the remote runner can read it):
  data/corpora/agreement/agreement_probe_cache_v1.json.gz

Per item we store ONLY structural, LEXEME-FREE agreement features (plus the subject word string,
used exclusively to build a novel-lexeme held-out split -- never fed to the substrate encoder):
  ndiff      : attractor count (n_diff_intervening; the difficulty axis 0..4)
  label      : 1 if verb is plural (VBP) else 0 (== subject number in this grammatical corpus)
  nums       : ordered list (prefix order) of each prefix-noun's number (1 plural / 0 singular)
  fwc        : ordered list of each prefix-noun's preceding-function-word class id
  subj_pos   : index into nums/fwc of the SUBJECT noun (the syntactic head; ORACLE, Stage-1 only)
  subj_word  : subject surface word (novel-lexeme split key ONLY)

Ranks are derived at load time: rank_from_verb = len(nums)-i, rank_from_start = i+1.
ASCII only. No push, no store write.
"""
from __future__ import annotations

import gzip
import json
import os
import sys
from collections import Counter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(REPO_ROOT, "data", "corpora", "agreement", "agr_50.tsv.gz")
NONCE_TAB = os.path.join(REPO_ROOT, "data", "corpora", "agreement", "gulordava_english", "generated.tab")
OUT = os.path.join(REPO_ROOT, "data", "corpora", "agreement", "agreement_probe_cache_v1.json.gz")

NOUN_TAGS = {"NN", "NNP", "NNS", "NNPS"}
PLURAL_NOUN = {"NNS", "NNPS"}

# preceding-function-word classes (raw-token derivable; NOT a parse)
FWC = {"START": 0, "DET": 1, "PREP": 2, "REL": 3, "CCONJ": 4, "OTHER": 5}


def fwc_of(prev_tag):
    if prev_tag is None:
        return FWC["START"]
    if prev_tag in ("DT", "PRP$", "POS"):
        return FWC["DET"]
    if prev_tag in ("IN", "TO"):
        return FWC["PREP"]
    if prev_tag in ("WDT", "WP", "WP$", "WRB"):
        return FWC["REL"]
    if prev_tag == "CC":
        return FWC["CCONJ"]
    return FWC["OTHER"]


# per-bin target counts: oversample rare high-attractor bins (all of bin 3/4), cap bin 0/1
BIN_TARGET = {0: 4000, 1: 4000, 2: 3000, 3: 3000, 4: 2000}
# per-bin, balance labels: cap each (bin,label) cell at half the target
def cell_cap(ndiff):
    return BIN_TARGET.get(ndiff, 0) // 2


def parse_row(fields):
    # columns (0-based): 2=pos_sentence 3=subj 5=subj_pos 8=verb_pos 9=subj_index 10=verb_index
    #                    13=n_diff_intervening
    try:
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
    if verb_index < 2 or verb_index > n or subj_index < 1 or subj_index >= verb_index:
        return None
    nums = []
    fwc = []
    subj_pos = -1
    for pos in range(1, verb_index):  # 1-based positions strictly before the verb
        tag = pos_sentence[pos - 1]
        if tag not in NOUN_TAGS:
            continue
        if pos == subj_index:
            subj_pos = len(nums)
        prev_tag = pos_sentence[pos - 2] if pos >= 2 else None
        nums.append(1 if tag in PLURAL_NOUN else 0)
        fwc.append(fwc_of(prev_tag))
    if subj_pos < 0 or len(nums) < 1:
        return None
    # sanity: subject number should equal the label (grammatical corpus). drop the rare mismatch.
    if nums[subj_pos] != label:
        return None
    return {
        "ndiff": ndiff if ndiff <= 4 else 4,  # collapse >=4 into bin 4
        "label": label,
        "nums": nums,
        "fwc": fwc,
        "subj_pos": subj_pos,
        "subj_word": subj_word,
    }


def build_linzen():
    if not os.path.exists(CORPUS):
        print("FATAL: corpus not found at %s" % CORPUS, flush=True)
        sys.exit(2)
    cell_count = Counter()  # (bin,label) -> n
    kept = []
    seen = 0
    with gzip.open(CORPUS, "rt", encoding="utf-8", errors="replace") as f:
        header = f.readline()
        for line in f:
            seen += 1
            if seen % 200000 == 0:
                print("[prep] scanned=%d kept=%d cells=%s" % (seen, len(kept), dict(cell_count)), flush=True)
            fields = line.rstrip("\n").split("\t")
            rec = parse_row(fields)
            if rec is None:
                continue
            key = (rec["ndiff"], rec["label"])
            if cell_count[key] >= cell_cap(rec["ndiff"]):
                continue
            cell_count[key] += 1
            kept.append(rec)
            # early stop once every cell is full
            if all(cell_count[(b, l)] >= cell_cap(b) for b in BIN_TARGET for l in (0, 1)):
                print("[prep] all cells full at scanned=%d" % seen, flush=True)
                break
    print("[prep] Linzen done: scanned=%d kept=%d cells=%s" % (seen, len(kept), dict(cell_count)), flush=True)
    return kept


def build_nonce():
    """Parse Gulordava English nonce constructions into the same schema WHERE derivable from tab fields.
    generated.tab cols: 0 pattern,1 constr_id,2 sent_id,3 correct_number,4 form,5 class,6 type,7 prefix,
    8 n_attr,... We keep ONE row per (constr_id,sent_id,type) using the 'correct' class row. Nonce
    per-noun number extraction requires POS tagging the prefix; we DEFER that to the cell (optional
    transfer arm) and here store only prefix + correct_number + n_attr + type for the cell to tag."""
    if not os.path.exists(NONCE_TAB):
        return []
    out = []
    with open(NONCE_TAB, "r", encoding="utf-8", errors="replace") as f:
        header = f.readline()
        for line in f:
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 9:
                continue
            if fields[5] != "correct":
                continue
            try:
                n_attr = int(fields[8])
            except ValueError:
                continue
            out.append({
                "type": fields[6],                       # generated (nonce) | original
                "label": 1 if fields[3] == "plur" else 0,
                "n_attr": n_attr,
                "prefix": fields[7],
            })
    print("[prep] nonce done: %d correct-form constructions" % len(out), flush=True)
    return out


def main():
    linzen = build_linzen()
    nonce = build_nonce()
    payload = {
        "schema_version": "agreement_probe_cache_v1",
        "source": "Linzen Dupoux Goldberg 2016 (agr_50_mostcommon_10K); Gulordava et al 2018 English nonce",
        "fwc_map": FWC,
        "bin_target": BIN_TARGET,
        "n_linzen": len(linzen),
        "n_nonce": len(nonce),
        "linzen": linzen,
        "nonce": nonce,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with gzip.open(OUT, "wt", encoding="utf-8") as f:
        json.dump(payload, f, separators=(",", ":"))
    print("[prep] wrote %s (%d Linzen + %d nonce items, %.2f MB)"
          % (OUT, len(linzen), len(nonce), os.path.getsize(OUT) / 1e6), flush=True)


if __name__ == "__main__":
    main()
