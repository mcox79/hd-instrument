"""Provenance/prep: parse Horlbeck 2018 gene-level GI maps (Treeview CDT) -> compact npz.

SOURCE (documented; verified fetchable 2026-07-15):
  Mendeley Data 10.17632/rdzk59n6j4.1 -> GI_map_treeview.zip
    -> 'K562 gene-level map/K562_gene.cdt'   (448 x 448 gene-level GI scores, K562)
    -> 'Jurkat gene-level map/Jurkat_gene.cdt' (gene-level GI scores, Jurkat)
  GI score = paper's OWN quadratic-fit residual (observed double phenotype minus expected
  from a quadratic fit of the two single-gene phenotypes); main effects stripped by construction.
  Using the paper's processed matrix avoids re-deriving the null (design decision).

CDT layout (tab-delimited):
  L0: GID  <empty>  NAME  GWEIGHT  <col_gene_1> <col_gene_2> ...
  L1: AID  ...                     (array ids)   -- skipped
  L2: EWEIGHT ...                                -- skipped
  L3+: <GID> <row_gene> <row_gene> <GWEIGHT> <val> <val> ...

Output npz: data/horlbeck_gi/horlbeck_gene_gi.npz
  k562_genes (str[]), k562_gi (float32 n x n, NaN=missing),
  jurkat_genes (str[]), jurkat_gi (float32 m x m, NaN=missing)
The matrices are symmetrized (average of M and M^T over cells where BOTH present).
ASCII-only. Deterministic. Pure I/O parse (no measurement, no learning).
"""
import os
import sys
import zipfile

import numpy as np

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
RAW_DIR = os.path.join(_REPO, "data", "horlbeck_gi", "raw")
OUT = os.path.join(_REPO, "data", "horlbeck_gi", "horlbeck_gene_gi.npz")
ZIP = os.path.join(RAW_DIR, "GI_map_treeview.zip")
MEMBERS = {
    "k562": "GI_map_treeview/K562 gene-level map/K562_gene.cdt",
    "jurkat": "GI_map_treeview/Jurkat gene-level map/Jurkat_gene.cdt",
}


def _parse_cdt(text):
    """Return (col_genes list[str], row_genes list[str], M float32 [rows x cols], NaN=missing)."""
    lines = text.split("\n")
    header = lines[0].rstrip("\r").split("\t")
    col_genes = [c.strip() for c in header[4:]]
    rows = []
    row_genes = []
    for ln in lines[3:]:
        if not ln.strip():
            continue
        cells = ln.rstrip("\r").split("\t")
        if len(cells) < 4:
            continue
        row_genes.append(cells[1].strip())
        vals = cells[4:]
        r = np.full(len(col_genes), np.nan, dtype=np.float32)
        for j, v in enumerate(vals[: len(col_genes)]):
            v = v.strip()
            if v == "" or v.lower() == "nan":
                continue
            try:
                r[j] = float(v)
            except ValueError:
                pass
        rows.append(r)
    M = np.vstack(rows) if rows else np.zeros((0, len(col_genes)), dtype=np.float32)
    return col_genes, row_genes, M


def _to_symmetric_gene_matrix(col_genes, row_genes, M):
    """Align rows/cols to a shared SORTED gene list; symmetrize (avg over both-present cells)."""
    genes = sorted(set(col_genes) & set(row_genes))
    gi = {g: i for i, g in enumerate(genes)}
    n = len(genes)
    S = np.full((n, n), np.nan, dtype=np.float32)
    cnt = np.zeros((n, n), dtype=np.float32)
    acc = np.zeros((n, n), dtype=np.float64)
    for ri, rg in enumerate(row_genes):
        if rg not in gi:
            continue
        a = gi[rg]
        for cj, cg in enumerate(col_genes):
            if cg not in gi:
                continue
            b = gi[cg]
            v = M[ri, cj]
            if v == v:  # not NaN
                acc[a, b] += v
                cnt[a, b] += 1.0
    # symmetrize: combine (a,b) and (b,a)
    both = acc + acc.T
    bc = cnt + cnt.T
    with np.errstate(invalid="ignore", divide="ignore"):
        Sym = np.where(bc > 0, both / np.maximum(bc, 1.0), np.nan).astype(np.float32)
    return genes, Sym


def _report(tag, genes, S):
    n = len(genes)
    iu = np.triu_indices(n, k=1)
    off = S[iu]
    finite = np.isfinite(off)
    vals = off[finite]
    deg = np.isfinite(S).sum(1) - np.isfinite(np.diag(S)).astype(int)  # off-diag finite partners per gene
    print("[%s] n_genes=%d off_diag_pairs=%d finite=%d (%.1f%%) | GI mean=%.4f std=%.4f min=%.3f max=%.3f"
          % (tag, n, off.size, vals.size, 100.0 * vals.size / max(1, off.size),
             float(vals.mean()), float(vals.std()), float(vals.min()), float(vals.max())), flush=True)
    print("[%s] per-gene finite-partner degree: min=%d median=%d max=%d"
          % (tag, int(deg.min()), int(np.median(deg)), int(deg.max())), flush=True)
    # symmetry check on the RAW (pre-symmetrized already averaged) -- report residual asymmetry proxy
    top = np.nanpercentile(np.abs(vals), 90)
    print("[%s] |GI| 90th pct=%.4f (top-decile hit threshold candidate)" % (tag, top), flush=True)


def main():
    if not os.path.exists(ZIP):
        print("MISSING %s -- download GI_map_treeview.zip from Mendeley 10.17632/rdzk59n6j4.1" % ZIP)
        sys.exit(2)
    z = zipfile.ZipFile(ZIP)
    out = {}
    for line, member in MEMBERS.items():
        text = z.read(member).decode("utf-8", errors="replace")
        cg, rg, M = _parse_cdt(text)
        genes, S = _to_symmetric_gene_matrix(cg, rg, M)
        _report(line, genes, S)
        out["%s_genes" % line] = np.array(genes, dtype=object)
        out["%s_gi" % line] = S
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    np.savez_compressed(OUT, **out)
    sz = os.path.getsize(OUT)
    print("[prep] wrote %s (%d bytes)" % (OUT, sz), flush=True)


if __name__ == "__main__":
    main()
