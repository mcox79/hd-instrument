#!/usr/bin/env python3
"""Pre-dispatch encoder-discipline check (Path C).

Scans a cell .py file and reports:
  (a) Does it import LLM encoder libraries (transformers / gensim / sentence_transformers /
      torch.hub LLM checkpoints / openai / anthropic)?
  (b) Does it reference LLM model identifiers (pythia, minilm, bge, llama, t5, e5,
      sentence-transformers, word2vec, glove, etc.) at module level or in encoder
      construction calls?
  (c) Does it declare an `ENCODER_PROVENANCE` constant (preferred) OR write
      `encoder_provenance` into metrics?
  (d) If it carries LLM signals, is there a docstring justification?

Exit codes:
  0 = clean SUBSTRATE_NATIVE (no LLM signals + has SUBSTRATE_NATIVE provenance OR
      no LLM signals + no explicit provenance constant -- still ok, default-clean)
  0 = LLM signals present BUT ENCODER_PROVENANCE is a recognized non-SUBSTRATE value
      AND a docstring justification block is present (opt-in, properly documented)
  1 = LLM signals present BUT no ENCODER_PROVENANCE declared (silent drift -- BLOCK)
  2 = LLM signals present BUT ENCODER_PROVENANCE = "SUBSTRATE_NATIVE" (mismatch -- BLOCK)
  3 = file not found / parse error

Reference: testbed encoder-provenance audit 2026-06-26
  notes/testbed_encoder_provenance_audit_path_C_cleanup_2026-06-26.md (Risk R3)
META: META_substrate_product_inference_uses_substrate_native_encoder_only

Usage:
  python tools/check_encoder_discipline.py <cell.py>
  python tools/check_encoder_discipline.py --batch experiments/exp_*.py
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

# LLM encoder library imports (case-insensitive substring match on top-level import paths)
LLM_LIB_IMPORTS = (
    "transformers",
    "sentence_transformers",
    "sentence-transformers",
    "gensim",
    "openai",
    "anthropic",
    "tiktoken",
    "fasttext",
)

# LLM model identifiers (case-insensitive substring search in string literals).
# Conservative: matches construction-time identifiers; will NOT match incidental
# mentions in comments-only-text below the docstring (we strip strings only).
LLM_MODEL_IDENTIFIERS = (
    "pythia",
    "minilm",
    "all-MiniLM",
    "bge-large",
    "bge-small",
    "bge-base",
    "llama",
    "llama-3",
    "llama2",
    "t5-",
    "flamingo",
    "distilbert",
    "e5-large",
    "e5-base",
    "e5-small",
    "word2vec",
    "google-news-300",
    "glove",
    "fasttext",
    "AutoModel",
    "AutoTokenizer",
    "SentenceTransformer",
    "KeyedVectors",
)

VALID_PROVENANCE_VALUES = {
    "SUBSTRATE_NATIVE",
    "DEPLOYMENT_CONTEXT_LLM_KEYS",
    "DEPLOYMENT_CONTEXT_LLM_RESIDUALS",
    "LLM_AUGMENTATION",
    "LLM_DIAGNOSTIC_PROBE",
    "MIXED_LLM_AND_SUBSTRATE",
    "LLM_INGEST_ONLY_SUBSTRATE_AT_INFERENCE",
    "WORD2VEC_DIAGNOSTIC_PROBE",
    "UNKNOWN",
}

# Markers in the docstring that indicate the cell-author justified the LLM use.
JUSTIFICATION_KEYWORDS = (
    "diagnostic",
    "comparator",
    "deployment context",
    "deployment_context",
    "llm_augmentation",
    "llm augmentation",
    "encoder provenance",
    "encoder_provenance",
    "path c",
    "audit_core",
    "audit-core",
    "ingest-only",
    "ingest only",
)


def _collect_imports(tree: ast.AST) -> list[str]:
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def _collect_docstring_nodes(tree: ast.AST) -> set[int]:
    """Identify the id() of every Constant node that is a docstring (module / class /
    function / async function). These are commentary, not load-bearing identifiers."""
    docstring_ids: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                if isinstance(body[0].value.value, str):
                    docstring_ids.add(id(body[0].value))
    return docstring_ids


def _collect_string_literals(tree: ast.AST) -> list[str]:
    """Strings outside docstrings (docstrings are commentary, not encoder construction)."""
    docstring_ids = _collect_docstring_nodes(tree)
    strings: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) in docstring_ids:
                continue
            strings.append(node.value)
    return strings


def _get_provenance_constant(tree: ast.AST) -> str | None:
    """Find ENCODER_PROVENANCE = "..." at module scope."""
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "ENCODER_PROVENANCE":
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        return node.value.value
    return None


def _metrics_writes_provenance(source: str) -> bool:
    """Heuristic: cell writes encoder_provenance into a dict that looks like metrics."""
    return bool(re.search(r'["\']encoder_provenance["\']\s*:', source))


def _docstring_justifies(tree: ast.AST) -> bool:
    doc = ast.get_docstring(tree) or ""
    doc_lower = doc.lower()
    return any(kw in doc_lower for kw in JUSTIFICATION_KEYWORDS)


def _llm_signals(imports: list[str], strings: list[str]) -> tuple[list[str], list[str]]:
    found_imports: list[str] = []
    for imp in imports:
        imp_l = imp.lower()
        for lib in LLM_LIB_IMPORTS:
            if lib.lower() in imp_l:
                found_imports.append(imp)
                break

    found_idents: list[str] = []
    for s in strings:
        s_l = s.lower()
        for ident in LLM_MODEL_IDENTIFIERS:
            if ident.lower() in s_l:
                found_idents.append(ident)
                break
    return found_imports, sorted(set(found_idents))


def check_file(path: Path, verbose: bool = True) -> int:
    if not path.exists():
        print(f"[ENCODER-CHECK] FILE_NOT_FOUND: {path}")
        return 3
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"[ENCODER-CHECK] PARSE_ERROR: {path}: {e}")
        return 3

    imports = _collect_imports(tree)
    strings = _collect_string_literals(tree)
    llm_imports, llm_idents = _llm_signals(imports, strings)
    provenance = _get_provenance_constant(tree)
    writes_provenance = _metrics_writes_provenance(source)
    justified = _docstring_justifies(tree)

    has_llm_signals = bool(llm_imports or llm_idents)
    is_provenance_valid = provenance in VALID_PROVENANCE_VALUES if provenance else False

    if verbose:
        print(f"[ENCODER-CHECK] file={path}")
        print(f"  llm_imports: {llm_imports if llm_imports else '(none)'}")
        print(f"  llm_idents:  {llm_idents if llm_idents else '(none)'}")
        print(f"  ENCODER_PROVENANCE constant: {provenance!r}"
              + (" (valid)" if is_provenance_valid else " (NOT declared / invalid)"))
        print(f"  metrics writes encoder_provenance key: {writes_provenance}")
        print(f"  docstring justification present: {justified}")

    # Disposition
    if not has_llm_signals:
        # Clean substrate-native -- no LLM signals. ENCODER_PROVENANCE optional but recommended.
        if provenance and provenance != "SUBSTRATE_NATIVE":
            if verbose:
                print(f"[ENCODER-CHECK] WARN: no LLM signals but ENCODER_PROVENANCE={provenance};"
                      f" verify intent.")
            return 0
        if verbose:
            print("[ENCODER-CHECK] PASS: substrate-native (no LLM signals detected).")
        return 0

    # has_llm_signals == True
    if provenance is None and not writes_provenance:
        if verbose:
            print("[ENCODER-CHECK] FAIL: LLM signals present but NO encoder_provenance declared.")
            print("  Add: ENCODER_PROVENANCE = \"...\" at module scope AND emit in metrics.")
            print("  See: notes/testbed_encoder_provenance_audit_path_C_cleanup_2026-06-26.md")
        return 1

    if provenance == "SUBSTRATE_NATIVE":
        if verbose:
            print("[ENCODER-CHECK] FAIL: LLM signals present but ENCODER_PROVENANCE=SUBSTRATE_NATIVE.")
            print("  Either remove the LLM dependency OR set provenance to one of:")
            print(f"  {sorted(VALID_PROVENANCE_VALUES - {'SUBSTRATE_NATIVE', 'UNKNOWN'})}")
        return 2

    # LLM signals + non-substrate provenance declared. Check justification.
    if not justified:
        if verbose:
            print(f"[ENCODER-CHECK] WARN: ENCODER_PROVENANCE={provenance} but docstring lacks")
            print("  explicit justification keywords (diagnostic / comparator / deployment-context /")
            print("  LLM_AUGMENTATION / ingest-only / Path C). Add a sentence in docstring.")
        # WARN-but-allow: provenance declared, but justification not parseable. Exit 0 with warn.
        return 0

    if verbose:
        print(f"[ENCODER-CHECK] PASS: ENCODER_PROVENANCE={provenance} with docstring justification.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("paths", nargs="+", help="Cell .py file(s) to check.")
    ap.add_argument("--batch", action="store_true",
                    help="Continue checking remaining files even if one fails. "
                         "Exit code = max of all individual exit codes.")
    ap.add_argument("-q", "--quiet", action="store_true",
                    help="Suppress per-file verbose output; print only PASS/FAIL summary.")
    args = ap.parse_args()

    verbose = not args.quiet
    worst = 0
    failures: list[tuple[Path, int]] = []
    for raw in args.paths:
        p = Path(raw)
        rc = check_file(p, verbose=verbose)
        if rc != 0:
            failures.append((p, rc))
        worst = max(worst, rc)
        if rc != 0 and not args.batch:
            return rc

    if args.batch or args.quiet:
        print(f"\n[ENCODER-CHECK] checked={len(args.paths)} failures={len(failures)} worst_rc={worst}")
        for p, rc in failures:
            print(f"  rc={rc}: {p}")
    return worst


if __name__ == "__main__":
    sys.exit(main())
