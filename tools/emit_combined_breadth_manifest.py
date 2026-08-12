"""Emit a COMBINED manifest describing an ARC + simplewiki + breadth_v1 training
corpus so the data-lever encoder experiment is drop-in. Reads the two prepared
stats.json files + the measured ARC alpha-token count. Pure reporting; writes no
corpus, touches no GPU.

Run: python tools/emit_combined_breadth_manifest.py
Out: data/corpora/breadth_v1/COMBINED_MANIFEST.md
"""
import json
import os

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(_REPO, "data")

# Measured prior session (notes/breadth_corpus_expansion_plan_2026-07-27.md line 36).
ARC_TOKENS = 237_666_846
ARC_TRAIN_BUDGET = 130_000_000  # FULL_CFG train_token_budget actually consumed from the ARC pool

SW_STATS = os.path.join(DATA, "corpora", "simplewiki", "stats.json")
BREADTH_STATS = os.path.join(DATA, "corpora", "breadth_v1", "stats.json")
OUT = os.path.join(DATA, "corpora", "breadth_v1", "COMBINED_MANIFEST.md")


def load(path):
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else None


def main():
    sw = load(SW_STATS)
    br = load(BREADTH_STATS)
    sw_tok = sw["tokens"] if sw else 0
    br_tok = br["total_tokens"] if br else 0
    sw_lines = sw["lines"] if sw else 0
    br_lines = br["total_lines"] if br else 0

    total = ARC_TOKENS + sw_tok + br_tok
    rows = [
        ("ARC science (data/corpora/arc/ARC-V1-Feb2018-2/ARC_Corpus.txt)", ARC_TOKENS),
        ("Simple English Wikipedia (data/corpora/simplewiki/simplewiki_clean_v1.txt)", sw_tok),
        ("breadth_v1 mixed (data/corpora/breadth_v1/breadth_corpus_v1.txt)", br_tok),
    ]
    lines_out = []
    lines_out.append("# COMBINED breadth training corpus — drop-in manifest\n")
    lines_out.append("Emitted by `tools/emit_combined_breadth_manifest.py`. Pure reporting (no corpus "
                     "written, no GPU touched).\n")
    lines_out.append("## Token budget (alpha-token counting: `re.findall(r'[a-z]+', line.lower())`, "
                     "identical across all sources)\n")
    lines_out.append("| Source | Alpha-tokens | % of combined pool |")
    lines_out.append("|---|---|---|")
    for name, tok in rows:
        pct = (100.0 * tok / total) if total else 0.0
        lines_out.append(f"| {name} | {tok:,} | {pct:.1f}% |")
    lines_out.append(f"| **COMBINED POOL** | **{total:,}** | 100% |\n")

    ratio_pool = total / ARC_TOKENS if ARC_TOKENS else 0.0
    sw_ratio = sw_tok / ARC_TOKENS if ARC_TOKENS else 0.0
    lines_out.append("## Scale relative to ARC\n")
    lines_out.append(f"- Simple English Wikipedia alone = **{sw_tok:,}** tokens "
                     f"= **{sw_ratio:.2f}x** the ARC pool ({ARC_TOKENS:,}).")
    lines_out.append(f"- Combined pool = **{total:,}** tokens = **{ratio_pool:.2f}x** the ARC pool.")
    lines_out.append(f"- Note: FULL_CFG's `train_token_budget` = {ARC_TRAIN_BUDGET:,} (130M) — i.e. the "
                     f"v2 run consumes only ~55% of the ARC pool per epoch. Against that BUDGET, "
                     f"simplewiki adds {sw_tok/ARC_TRAIN_BUDGET:.2f}x more distinct tokens, which is "
                     f"the more relevant framing for 'how much new signal per training step'.\n")
    lines_out.append("## Line counts\n")
    lines_out.append(f"- Simple English Wikipedia: {sw_lines:,} lines")
    lines_out.append(f"- breadth_v1 mixed: {br_lines:,} lines")
    lines_out.append("- ARC: ~14.62M sentences (per header of exp_scale_meaning_learn_arc_heldout_v2.py)\n")
    lines_out.append("## Drop-in integration (leak-safe)\n")
    lines_out.append(
        "All three files share the SAME line=sentence, ASCII, mixed-case, quality-gated format "
        "(>=4 alpha-words/line, alpha-ratio >=0.55, citation-fragment filter). To train on the "
        "combined pool leak-safely, a v4/v5 encoder anchor should stream ALL THREE files through the "
        "SAME runtime held-out scrub that `exp_scale_meaning_learn_arc_heldout_v2.py` already applies "
        "to ARC (`collect_pass` / `tokenize_train_stream` build a `scrub` set from "
        "`_scrub_variants(split['heldout_surfaces'])` and drop any line containing a held-out surface "
        "BEFORE it enters `bpe_lines` or the train token stream). Do NOT `cat` the files together and "
        "feed the concatenation — that bypasses the scrub and leaks held-out concept contexts into "
        "training, invalidating the held-out-to-NEW-concept eval. The correct change is to point the "
        "existing per-line reader loop at a list of corpus paths [ARC, simplewiki, breadth_v1] instead "
        "of the single ARC path, keeping the scrub check unchanged.\n")
    lines_out.append("## Provenance / license\n")
    lines_out.append("- ARC: AI2 ARC-V1-Feb2018 corpus.")
    lines_out.append("- Simple English Wikipedia: dump `simplewiki-latest-pages-articles.xml.bz2` "
                     "(dumps.wikimedia.org, 2026-07-02 dump, 351,744,161 bytes verified), CC BY-SA.")
    lines_out.append("- breadth_v1: WordNet glosses + OneStopEnglish + LitBank + RACE + Wikipedia-500 "
                     "+ McGuffey/graded readers + UD-EWT (see data/corpora/breadth_v1/MANIFEST.md).")

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines_out) + "\n")
    print("wrote", OUT)
    print(f"simplewiki tokens = {sw_tok:,}")
    print(f"combined pool tokens = {total:,} ({ratio_pool:.2f}x ARC)")


if __name__ == "__main__":
    main()
