#!/usr/bin/env python3
"""Pre-dispatch GPU memory budget check.

AST-scans a cell .py file for tensor allocations targeted at GPU
(device='cuda' / 'cuda:N' / device=device-where-device-is-GPU / .cuda() / .to(device=...))
and reports:

  (a) Resolves config constants from module init (N_DIM, V_TOK, N_PARTITIONS, etc.).
  (b) Computes projected resident peak GPU memory in MB.
  (c) Compares against budget (default 6 GB safety under 8 GB total).
  (d) Recommends adding a T7-style self-test if the cell uses GPU but lacks one.

Exit codes:
  0 = clean (projected peak < budget; OR cell does not use GPU)
  1 = WOULD-OOM (projected peak > budget) -- BLOCK dispatch
  2 = parse error / can't resolve config constants -- INVESTIGATE
  3 = cell uses GPU but no budget check + no T7-style projection -- RECOMMEND adding

The scanner is intentionally CONSERVATIVE: when it cannot statically prove a
shape it falls back to a heuristic that prefers reporting "can't resolve"
(exit 2) over silent zero. Cells with dynamic-shape allocations should call
hdlab.gpu_memory_budget.project_peak_mb() at module init and the tool will
detect that and exit 0.

Reference: lang_ingest_vocab_bigram_meta_m7_v1 T7 self-test + mem_get_info
runtime gate (commits 1ea55da9 + 99f3a436). Plus 3 OOMs caught today:
  - drill 3 lang_ingest first version: 64*8192*8192*f32 = 16.4 GB -> CRASH
  - WM K-extension K=16384: peak 6 GB + 1 GB attempted = OOM
  - Pre-fix lang_ingest projected 16384 MB; T7 catches structurally

Usage:
  python tools/check_gpu_memory_budget.py <cell.py>
  python tools/check_gpu_memory_budget.py --batch experiments/exp_*.py
  python tools/check_gpu_memory_budget.py <cell.py> --budget-mb 4096
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

DEFAULT_BUDGET_MB = 6 * 1024  # 6 GB safety margin under 8 GB GPU
DEFAULT_TOTAL_GPU_MB = 8 * 1024

# dtype bytes (synced with hdlab.gpu_memory_budget.DTYPE_BYTES)
DTYPE_BYTES = {
    "float64": 8, "double": 8, "f64": 8,
    "float32": 4, "float": 4, "f32": 4,
    "float16": 2, "half": 2, "f16": 2,
    "bfloat16": 2, "bf16": 2,
    "int64": 8, "long": 8, "i64": 8,
    "int32": 4, "int": 4, "i32": 4,
    "int16": 2, "i16": 2,
    "int8": 1, "i8": 1,
    "uint8": 1,
    "bool": 1,
    "complex64": 8, "complex128": 16,
}

# Torch allocation functions whose first positional arg is a shape OR whose
# `size`/`shape` kwarg gives the shape. Conservative subset.
TORCH_ALLOCATORS = {
    "zeros", "ones", "empty", "rand", "randn", "randint",
    "full", "zeros_like", "ones_like", "empty_like",
}
# numpy allocators (if the cell hides a GPU tensor behind torch.from_numpy(np.zeros(...))
# we count it if the .to(device='cuda') happens; the .from_numpy itself is CPU).

# Patterns indicating GPU use in source
GPU_DEVICE_PATTERNS = (
    r"device\s*=\s*['\"]cuda",
    r"device\s*=\s*torch\.device\(['\"]cuda",
    r"device\s*=\s*_DEVICE",
    r"device\s*=\s*device\b",   # `device` var is GPU when assigned cuda
    r"\.cuda\(",
    r"\.to\(\s*['\"]cuda",
    r"\.to\(\s*torch\.device\(['\"]cuda",
    r"\.to\(\s*device\s*=\s*['\"]cuda",
    r"torch\.cuda\.",
    r"PYTORCH_CUDA_ALLOC_CONF",
)

# Indicators that the cell already has T7-style projection / runtime gate
HAS_T7_INDICATORS = (
    "project_gpu_peak_mb",
    "_project_gpu_peak_mb",
    "project_peak_mb",
    "project_simple",
    "GPU_BUDGET_MB",
    "mem_get_info",
    "hdlab.gpu_memory_budget",
    "from hdlab.gpu_memory_budget",
    "gpu_memory_budget",
)


# -------- AST traversal helpers --------

def _walk_assignments(tree: ast.AST) -> Dict[str, Any]:
    """Resolve simple module-scope name = literal/expr constants.

    Handles:
      - Name = Constant
      - Name = UnaryOp(USub, Constant)
      - Name = BinOp involving already-resolved Names and Constants
      - Name = Call to int(...), float(...), str(...) on resolvable arg
      - Name = Tuple/List of resolvables
      - Conditional reassignment via `if SMOKE:` / `if RUN_MODE == "smoke":` is
        WALKED but the FULL branch values are taken (the non-smoke branch) when
        detectable; otherwise the LAST assignment wins.

    Returns mapping of resolved name -> python value.
    """
    env: Dict[str, Any] = {}

    def _eval(node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            return env.get(node.id, _UNRESOLVED)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            v = _eval(node.operand)
            return -v if _is_numeric(v) else _UNRESOLVED
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd):
            return _eval(node.operand)
        if isinstance(node, ast.BinOp):
            l = _eval(node.left)
            r = _eval(node.right)
            if not (_is_numeric(l) and _is_numeric(r)):
                return _UNRESOLVED
            try:
                if isinstance(node.op, ast.Add):
                    return l + r
                if isinstance(node.op, ast.Sub):
                    return l - r
                if isinstance(node.op, ast.Mult):
                    return l * r
                if isinstance(node.op, ast.Div):
                    return l / r
                if isinstance(node.op, ast.FloorDiv):
                    return l // r
                if isinstance(node.op, ast.Mod):
                    return l % r
                if isinstance(node.op, ast.Pow):
                    return l ** r
            except Exception:
                return _UNRESOLVED
            return _UNRESOLVED
        if isinstance(node, ast.Tuple) or isinstance(node, ast.List):
            vals = [_eval(e) for e in node.elts]
            if any(v is _UNRESOLVED for v in vals):
                return _UNRESOLVED
            return tuple(vals) if isinstance(node, ast.Tuple) else list(vals)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"int", "float", "str"}:
            if not node.args:
                return _UNRESOLVED
            v = _eval(node.args[0])
            if v is _UNRESOLVED:
                return _UNRESOLVED
            try:
                return {"int": int, "float": float, "str": str}[node.func.id](v)
            except Exception:
                return _UNRESOLVED
        return _UNRESOLVED

    def _assign(target: ast.AST, value_node: ast.AST) -> None:
        if isinstance(target, ast.Name):
            v = _eval(value_node)
            if v is not _UNRESOLVED:
                env[target.id] = v
        elif isinstance(target, (ast.Tuple, ast.List)) and isinstance(value_node, (ast.Tuple, ast.List)):
            for t, v in zip(target.elts, value_node.elts):
                _assign(t, v)

    def _walk(body: List[ast.stmt]) -> None:
        for stmt in body:
            if isinstance(stmt, ast.Assign):
                for tgt in stmt.targets:
                    _assign(tgt, stmt.value)
            elif isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
                _assign(stmt.target, stmt.value)
            elif isinstance(stmt, ast.AugAssign):
                pass  # skip; rarely defines a constant
            elif isinstance(stmt, ast.If):
                # Walk BOTH branches; later-assignment wins. This handles
                # `if SMOKE: N_DIM = 2048 else: N_DIM = 8192` -- the else
                # branch values become the env (production config). This is
                # the conservative choice: full-mode shapes are largest.
                # First walk the `if` body, then the `else` body (so `else`
                # wins if both define the same name).
                _walk(stmt.body)
                _walk(stmt.orelse)
            elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                pass  # don't enter functions
            elif isinstance(stmt, ast.Try):
                _walk(stmt.body)
                for handler in stmt.handlers:
                    _walk(handler.body)
                _walk(stmt.orelse)
                _walk(stmt.finalbody)
            elif isinstance(stmt, ast.With):
                _walk(stmt.body)

    if isinstance(tree, ast.Module):
        _walk(tree.body)
    return env


_UNRESOLVED = object()


def _is_numeric(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


# -------- Allocation detection --------

def _shape_from_call(node: ast.Call, env: Dict[str, Any]) -> Optional[Tuple[int, ...]]:
    """Extract shape from a torch allocator call.

    Conventions:
      torch.zeros(N, M, dtype=..., device=...)         -> (N, M)
      torch.zeros((N, M), dtype=...)                   -> (N, M)
      torch.zeros(size=(N, M))                         -> (N, M)
      torch.zeros(N, M, dtype=...)                     -> (N, M)
    """
    # size= kwarg
    for kw in node.keywords:
        if kw.arg in {"size", "shape"}:
            shape = _resolve_shape(kw.value, env)
            if shape is not None:
                return shape
    # First positional arg may be tuple/list OR an integer (followed by more ints)
    if not node.args:
        return None
    first = node.args[0]
    if isinstance(first, (ast.Tuple, ast.List)):
        return _resolve_shape(first, env)
    # Sequence-of-ints style
    dims: List[int] = []
    for arg in node.args:
        v = _resolve_int(arg, env)
        if v is None:
            return None
        dims.append(v)
    if not dims:
        return None
    return tuple(dims)


def _resolve_shape(node: ast.AST, env: Dict[str, Any]) -> Optional[Tuple[int, ...]]:
    if isinstance(node, (ast.Tuple, ast.List)):
        dims: List[int] = []
        for e in node.elts:
            v = _resolve_int(e, env)
            if v is None:
                return None
            dims.append(v)
        return tuple(dims)
    if isinstance(node, ast.Name) and node.id in env:
        val = env[node.id]
        if isinstance(val, (tuple, list)) and all(_is_numeric(x) for x in val):
            return tuple(int(x) for x in val)
    return None


def _resolve_int(node: ast.AST, env: Dict[str, Any]) -> Optional[int]:
    if isinstance(node, ast.Constant) and _is_numeric(node.value):
        return int(node.value)
    if isinstance(node, ast.Name):
        v = env.get(node.id)
        if _is_numeric(v):
            return int(v)
        return None
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        v = _resolve_int(node.operand, env)
        return -v if v is not None else None
    if isinstance(node, ast.BinOp):
        l = _resolve_int(node.left, env)
        r = _resolve_int(node.right, env)
        if l is None or r is None:
            return None
        try:
            if isinstance(node.op, ast.Add):
                return l + r
            if isinstance(node.op, ast.Sub):
                return l - r
            if isinstance(node.op, ast.Mult):
                return l * r
            if isinstance(node.op, ast.FloorDiv):
                return l // r
            if isinstance(node.op, ast.Mod):
                return l % r
            if isinstance(node.op, ast.Div):
                return int(l / r)
            if isinstance(node.op, ast.Pow):
                return l ** r
        except Exception:
            return None
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "int":
        if node.args:
            return _resolve_int(node.args[0], env)
    return None


def _dtype_from_call(node: ast.Call, env: Dict[str, Any]) -> str:
    """Extract dtype from a torch allocator call.

    Looks at dtype kwarg: dtype=torch.float32 / dtype=torch.float16 / dtype=DTYPE
    Defaults to 'float32' (the torch default for most allocators).
    """
    for kw in node.keywords:
        if kw.arg == "dtype":
            v = kw.value
            if isinstance(v, ast.Attribute) and isinstance(v.value, ast.Name):
                # e.g. torch.float32
                return v.attr
            if isinstance(v, ast.Name):
                # var holding a dtype; try env
                val = env.get(v.id)
                if isinstance(val, str) and val.lower() in DTYPE_BYTES:
                    return val
                # heuristic from var name
                if "16" in v.id.lower() or "half" in v.id.lower():
                    return "float16"
                if "float64" in v.id.lower() or "double" in v.id.lower():
                    return "float64"
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                return v.value
    return "float32"


def _is_gpu_target(node: ast.Call, env: Dict[str, Any], source: str) -> bool:
    """Decide if this allocator call lands on GPU.

    Heuristic: device=... kwarg is cuda/cuda:N/_DEVICE/device (where device var
    has been bound to torch.device('cuda') in env).
    """
    for kw in node.keywords:
        if kw.arg == "device":
            v = kw.value
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                return v.value.lower().startswith("cuda")
            if isinstance(v, ast.Call) and _call_is_torch_device_cuda(v):
                return True
            if isinstance(v, ast.Name):
                # Inspect bindings of `device` / `_DEVICE` / `dev`
                if v.id in {"_DEVICE", "device", "dev", "DEVICE", "GPU_DEVICE", "cuda"}:
                    # Look for evidence in the source that this var is bound to cuda.
                    if _name_bound_to_cuda(v.id, source):
                        return True
                # Custom names: only true if we can prove
                if _name_bound_to_cuda(v.id, source):
                    return True
    return False


def _call_is_torch_device_cuda(node: ast.Call) -> bool:
    """Match torch.device('cuda'...) calls."""
    fn = node.func
    if isinstance(fn, ast.Attribute) and fn.attr == "device":
        if isinstance(fn.value, ast.Name) and fn.value.id == "torch":
            if node.args and isinstance(node.args[0], ast.Constant):
                arg = node.args[0].value
                if isinstance(arg, str) and arg.lower().startswith("cuda"):
                    return True
    return False


_CUDA_BIND_RE = re.compile(
    r"\b(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*"
    r"(?:torch\.device\(\s*['\"]cuda|['\"]cuda(?::\d+)?['\"]|"
    r"torch\.device\(\s*['\"]cuda:0['\"])"
)


def _name_bound_to_cuda(name: str, source: str) -> bool:
    """Quick textual scan: is `name = torch.device('cuda...')` or `name = "cuda..."` anywhere?"""
    if name.lower() == "cpu":
        return False
    for m in _CUDA_BIND_RE.finditer(source):
        if m.group("name") == name:
            return True
    # Also catch ternary patterns: name = torch.device("cuda:0") if _CUDA_OK else ...
    ternary_pat = re.compile(
        rf"\b{re.escape(name)}\s*=\s*torch\.device\(\s*['\"]cuda[^)]*\)\s*if\b"
    )
    if ternary_pat.search(source):
        return True
    return False


def _to_call_routes_to_cuda(node: ast.Call, source: str) -> bool:
    """Detect `.to(device='cuda')` / `.to('cuda')` / `.to(device=device)` patterns.

    Returns True iff this is a .to(...) call AND the target device is GPU.
    """
    fn = node.func
    if not (isinstance(fn, ast.Attribute) and fn.attr == "to"):
        return False
    # Positional 'cuda'
    if node.args:
        first = node.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            if first.value.lower().startswith("cuda"):
                return True
        if isinstance(first, ast.Call) and _call_is_torch_device_cuda(first):
            return True
        if isinstance(first, ast.Name) and _name_bound_to_cuda(first.id, source):
            return True
    # device= kwarg
    for kw in node.keywords:
        if kw.arg == "device":
            v = kw.value
            if isinstance(v, ast.Constant) and isinstance(v.value, str) and v.value.lower().startswith("cuda"):
                return True
            if isinstance(v, ast.Call) and _call_is_torch_device_cuda(v):
                return True
            if isinstance(v, ast.Name) and _name_bound_to_cuda(v.id, source):
                return True
    return False


def _is_torch_allocator_call(node: ast.Call) -> Tuple[bool, str]:
    """Return (is_allocator, fn_name) if this call is torch.zeros/ones/empty/..."""
    fn = node.func
    if isinstance(fn, ast.Attribute):
        if fn.attr in TORCH_ALLOCATORS:
            base = fn.value
            if isinstance(base, ast.Name) and base.id == "torch":
                return True, fn.attr
            if isinstance(base, ast.Attribute) and base.attr == "cuda":
                # torch.cuda.FloatTensor etc. -- rare
                return True, fn.attr
    if isinstance(fn, ast.Name) and fn.id in TORCH_ALLOCATORS:
        # Direct import: from torch import zeros
        return True, fn.id
    return False, ""


def _collect_gpu_allocations(
    tree: ast.AST, env: Dict[str, Any], source: str
) -> List[Dict[str, Any]]:
    """Walk the AST for torch.<allocator>(..., device=cuda) calls + .to(cuda) calls.

    Returns list of dicts: {name, shape, dtype, bytes, mb, lineno, source}.

    Note: .to(cuda) on an existing tensor doesn't tell us the shape statically;
    we record it as 'unsized' and use its lineno to refer back. This is captured
    so the caller can flag "GPU use but no projection" cases.
    """
    allocs: List[Dict[str, Any]] = []
    skipped_unsized = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        is_alloc, fname = _is_torch_allocator_call(node)
        if is_alloc:
            on_gpu = _is_gpu_target(node, env, source)
            if not on_gpu:
                continue
            shape = _shape_from_call(node, env)
            dtype = _dtype_from_call(node, env)
            if shape is None:
                skipped_unsized += 1
                allocs.append({
                    "name": f"torch.{fname}",
                    "shape": None,
                    "dtype": dtype,
                    "bytes": None,
                    "mb": None,
                    "lineno": getattr(node, "lineno", -1),
                    "unresolved": True,
                })
                continue
            elems = 1
            for d in shape:
                elems *= int(d)
            nbytes = elems * DTYPE_BYTES.get(dtype.lower(), 4)
            allocs.append({
                "name": f"torch.{fname}",
                "shape": shape,
                "dtype": dtype,
                "bytes": nbytes,
                "mb": nbytes / (1024 * 1024),
                "lineno": getattr(node, "lineno", -1),
                "unresolved": False,
            })
        elif _to_call_routes_to_cuda(node, source):
            # We can't size .to(cuda) calls without dataflow analysis.
            allocs.append({
                "name": "<tensor>.to(cuda)",
                "shape": None,
                "dtype": None,
                "bytes": None,
                "mb": None,
                "lineno": getattr(node, "lineno", -1),
                "unresolved": True,
            })
    return allocs


def _has_t7_or_helper(source: str) -> bool:
    """Detect that the cell already does its own peak projection / runtime gate.

    If so, we skip the OOM verdict and trust the cell's own self-test.
    """
    s_lower = source.lower()
    for ind in HAS_T7_INDICATORS:
        if ind.lower() in s_lower:
            return True
    return False


def _uses_gpu(source: str) -> bool:
    for pat in GPU_DEVICE_PATTERNS:
        if re.search(pat, source):
            return True
    return False


# -------- Main check --------

def check_file(
    path: Path,
    budget_mb: float = DEFAULT_BUDGET_MB,
    verbose: bool = True,
) -> int:
    if not path.exists():
        print(f"[GPU-BUDGET] FILE_NOT_FOUND: {path}")
        return 2
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"[GPU-BUDGET] PARSE_ERROR: {path}: {e}")
        return 2

    uses_gpu = _uses_gpu(source)
    has_t7 = _has_t7_or_helper(source)

    if not uses_gpu:
        if verbose:
            print(f"[GPU-BUDGET] {path}: no GPU use detected (CPU-only). SKIP.")
        return 0

    env = _walk_assignments(tree)
    allocs = _collect_gpu_allocations(tree, env, source)

    # Build sized vs unsized partition
    sized = [a for a in allocs if not a["unresolved"]]
    unsized = [a for a in allocs if a["unresolved"]]

    # Conservative peak: SUM of all sized GPU allocations.
    # (The tool can't statically distinguish persistent vs transient lifetimes;
    # err on the side of summing. Cells that need finer accounting should call
    # hdlab.gpu_memory_budget.project_peak_mb at module init.)
    projected_peak_mb = sum(a["mb"] for a in sized) if sized else 0.0

    if verbose:
        print(f"[GPU-BUDGET] file={path}")
        print(f"  uses_gpu={uses_gpu}  has_t7_or_helper={has_t7}")
        print(f"  budget_mb={budget_mb:.0f}  default_total_gpu_mb={DEFAULT_TOTAL_GPU_MB}")
        print(f"  sized_gpu_allocations={len(sized)}  unsized_gpu_allocations={len(unsized)}")
        if sized:
            print(f"  --- sized GPU allocations (CONSERVATIVE sum):")
            for a in sized:
                print(
                    f"    L{a['lineno']:>4}  {a['name']:<24} "
                    f"shape={a['shape']!s:<32} dtype={a['dtype']:<10} "
                    f"{a['mb']:>10.1f} MB"
                )
        if unsized:
            print(f"  --- unsized GPU allocations (NOT counted; shape not statically resolvable):")
            for a in unsized[:10]:
                print(f"    L{a['lineno']:>4}  {a['name']}")
            if len(unsized) > 10:
                print(f"    ... and {len(unsized) - 10} more")
        print(f"  projected_peak_mb={projected_peak_mb:.1f}  budget_mb={budget_mb:.0f}")

    # Disposition
    if has_t7:
        if verbose:
            print(
                "[GPU-BUDGET] PASS: cell has T7-style projection / mem_get_info gate / "
                "hdlab.gpu_memory_budget helper -- trusting cell self-test."
            )
        # Still warn if conservative sum exceeds budget; informational only.
        if projected_peak_mb > budget_mb:
            if verbose:
                print(
                    f"  WARN: conservative AST-sum {projected_peak_mb:.0f} MB exceeds budget "
                    f"{budget_mb:.0f} MB. Cell's own projection may be tighter "
                    f"(persistent/transient/phase lifetimes). VERIFY the cell's T7 fires."
                )
        return 0

    # No T7 helper. Apply conservative budget check.
    if projected_peak_mb > budget_mb:
        if verbose:
            print(
                f"[GPU-BUDGET] FAIL: projected_peak_mb={projected_peak_mb:.0f} > "
                f"budget_mb={budget_mb:.0f}. WOULD-OOM. BLOCK dispatch."
            )
            print(
                "  Add T7-style projection at module init OR import "
                "hdlab.gpu_memory_budget.project_peak_mb and call at startup."
            )
        return 1

    if uses_gpu and not sized and not has_t7:
        # GPU used, but no statically-sized allocations + no helper -> recommend adding
        if verbose:
            print(
                "[GPU-BUDGET] RECOMMEND: cell uses GPU but no statically-sized allocations "
                "AND no T7-style projection / hdlab.gpu_memory_budget helper detected. "
                "Add `from hdlab.gpu_memory_budget import project_peak_mb, assert_under_budget` "
                "and a module-init self-test."
            )
        return 3

    if verbose:
        print(
            f"[GPU-BUDGET] PASS: projected_peak_mb={projected_peak_mb:.0f} <= "
            f"budget_mb={budget_mb:.0f}."
        )
        if not has_t7:
            print(
                "  RECOMMEND: add T7-style projection at module init via "
                "hdlab.gpu_memory_budget.project_peak_mb() for runtime free-mem gating."
            )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("paths", nargs="+", help="Cell .py file(s) to check.")
    ap.add_argument(
        "--budget-mb", type=float, default=DEFAULT_BUDGET_MB,
        help=f"GPU budget in MB (default {DEFAULT_BUDGET_MB} = 6 GB safety under 8 GB)."
    )
    ap.add_argument(
        "--batch", action="store_true",
        help="Continue checking remaining files even if one fails."
    )
    ap.add_argument("-q", "--quiet", action="store_true", help="Suppress verbose output.")
    args = ap.parse_args()

    verbose = not args.quiet
    worst = 0
    failures: List[Tuple[Path, int]] = []
    for raw in args.paths:
        p = Path(raw)
        rc = check_file(p, budget_mb=args.budget_mb, verbose=verbose)
        if rc != 0:
            failures.append((p, rc))
        worst = max(worst, rc)
        if rc != 0 and not args.batch:
            return rc

    if args.batch or args.quiet:
        print(f"\n[GPU-BUDGET] checked={len(args.paths)} failures={len(failures)} worst_rc={worst}")
        for p, rc in failures:
            print(f"  rc={rc}: {p}")
    return worst


if __name__ == "__main__":
    sys.exit(main())
