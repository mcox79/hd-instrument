"""Convert Phase-2-light smoke JSON output to a Research-reviewer-friendly markdown table.

Adds:
- Single-line ACCEPT / REJECT / UPDATE / DEFER decision checkbox per proposal
- Source-file links + raw-mention context
- Distant-supervision similarity table
- Proposed algebra_additions template (for ACCEPT-as-CREATE proposals)
- One-line decision space

Usage: python tools/substrate_phase_2_light_review_table.py <json_path> [<output_md>]
       defaults to the most recent phase_2_light_smoke_*.json
"""
from pathlib import Path
import sys
import json
import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_path", nargs="?", help="Smoke output JSON; defaults to latest")
    ap.add_argument("--out", help="Markdown output path; defaults to alongside JSON")
    args = ap.parse_args()

    DATA_ROOT = Path("data/substrate_index")
    if args.json_path:
        json_p = Path(args.json_path)
    else:
        candidates = sorted(DATA_ROOT.glob("phase_2_light_smoke_*.json"),
                             key=lambda p: p.stat().st_mtime, reverse=True)
        if not candidates:
            print("no phase_2_light_smoke_*.json files found", file=sys.stderr)
            sys.exit(1)
        json_p = candidates[0]

    with open(json_p, "r", encoding="utf-8") as f:
        data = json.load(f)

    out_p = Path(args.out) if args.out else json_p.with_suffix(".review.md")

    lines: list[str] = []
    lines.append(f"# Phase-2-light proposal batch review")
    lines.append("")
    lines.append(f"- Smoke run: `{json_p.name}`")
    lines.append(f"- n_input_files: {data.get('n_input_files', '?')}")
    lines.append(f"- n_atoms_baseline: {data.get('n_atoms_baseline', '?')}")
    lines.append(f"- elapsed: {data.get('elapsed_s', '?'):.1f}s")
    lines.append(f"- proposals: {len(data.get('proposals', []))}")
    lines.append("")
    lines.append("## Instructions")
    lines.append("")
    lines.append("For each proposal: replace `[ ]` with `[A]`=ACCEPT, `[R]`=REJECT, `[U]`=UPDATE (existing atom), `[D]`=DEFER, `[M]`=MODIFY (note in comment).")
    lines.append("")
    lines.append("---")
    lines.append("")

    for p in data.get("proposals", []):
        rank = p["rank"]
        name = p["canonical_name"]
        z = p["z_count"]
        route = p["route"]
        nearest = p.get("nearest_cluster")
        density = p.get("nearest_density")
        novelty = p.get("novelty", 0)
        sim_ex = p.get("similarity_to_existing_T3", [])
        ds_score = p.get("distant_supervision_score", 0)
        algebra_tpl = p.get("algebra_additions_template", {})
        sources = p.get("source_files", [])
        raw = p.get("raw_mentions", [])

        lines.append(f"### #{rank}. `{name}` (Z={z})")
        lines.append("")
        lines.append(f"**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY")
        lines.append("")
        lines.append(f"- Tool route: `{route}`")
        lines.append(f"- Nearest cluster: {nearest} (density={density} atoms; novelty={novelty:.2f})")
        lines.append(f"- Distant supervision: max score {ds_score:.2f}")
        if sim_ex:
            lines.append(f"- Closest existing atoms (token-Jaccard):")
            for qid, s in sim_ex[:3]:
                lines.append(f"  - {qid} (sim={s:.2f})")
        lines.append(f"- Raw mentions: {raw[:3] if raw else '?'}")
        lines.append(f"- Source files (sample): {sources[:3] if sources else '?'}")
        if algebra_tpl:
            lines.append(f"- Proposed algebra_additions template (if ACCEPT-as-CREATE):")
            lines.append("  ```yaml")
            for k, v in algebra_tpl.items():
                lines.append(f"  {k}: {v}")
            lines.append("  ```")
        lines.append("")

    md = "\n".join(lines)
    out_p.write_text(md, encoding="utf-8")
    print(f"wrote review table: {out_p}")
    print(f"({len(data.get('proposals', []))} proposals; {len(md)} chars)")


if __name__ == "__main__":
    main()
