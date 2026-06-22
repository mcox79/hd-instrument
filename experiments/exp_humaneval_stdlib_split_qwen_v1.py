"""
exp_humaneval_stdlib_split_qwen_v1.py -- HumanEval Anchor-1 stdlib-class split: substrate-augmented Qwen-1.5B vs bare Qwen-1.5B.

ROUTING: Research 2026-06-22 scope-drill Anchor-1 (the 2026-06-07 HumanEval stdlib-class split, hardened to +15 points).
  Substrate role: PROMPT_AUGMENTATION (substrate-as-tool-for-LLM; substrate_native=False). Pipeline per Class A (stdlib)
  problem: parse problem keywords -> retrieve top-K Python stdlib doc snippets from a SUBSTRATE-indexed corpus
  (cosine over MiniLM embeddings; substrate is the index) -> prepend snippets to the prompt -> Qwen-1.5B-Instruct
  greedy generates code -> subprocess execute canonical tests -> pass@1. Compared against BARE Qwen (problem only).
  Class A (stdlib-class) = canonical_solution uses Python stdlib modules; Class B (algorithm-class) = no stdlib.
  Discriminating-regime check: Class B improvement < +5 (confirms lift is stdlib-retrieval-specific).
PRE-REGISTERED: HARD_PASS gain_A >= +15 points. MIDDLE_BAND gain_A in [+5,+15). HARD_FAIL gain_A <+5 OR sub<bare-5.
ASCII-only. write_metrics. PROT-018 _v1. substrate_native=False; substrate_role=prompt_augmentation.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, re, tempfile, subprocess, hashlib, json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "humaneval_stdlib_split_qwen_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N_DIM = 1024  # substrate phasor dim; substrate is used only as an INDEX (cosine retrieval)
MAX_NEW_TOKENS = 256
GEN_TIMEOUT_S = 10  # subprocess test execution timeout
TOP_K_RETRIEVE = 3

# Discipline: declare auditable substrate role (not substrate-native)
SUBSTRATE_NATIVE = False
SUBSTRATE_ROLE = "prompt_augmentation"
_LLM_CALL_COUNTER = [0]  # incremented per Qwen forward at inference (substrate-only audit hook; this cell IS NOT substrate-only)

# Stdlib-class label heuristic (on canonical_solution)
STDLIB_PATTERNS = [
    "import ", "math.", "re.", "itertools.", "collections.",
    "os.", "string.", "functools.", "operator.", "bisect.",
    "heapq.", "datetime", "json.",
]

# Manually-curated Python stdlib doc snippets (the substrate-indexed corpus).
# Each entry: (snippet_id, snippet_text). The snippet is the "doc" we retrieve and prepend.
# Coverage targets HumanEval's actual stdlib usage: math, re, itertools, collections, string, functools.
STDLIB_SNIPPETS: List[Tuple[str, str]] = [
    # math module
    ("math.floor", "math.floor(x): Return the floor of x, the largest integer less than or equal to x. Example: math.floor(3.7) -> 3."),
    ("math.ceil", "math.ceil(x): Return the ceiling of x, the smallest integer greater than or equal to x. Example: math.ceil(3.2) -> 4."),
    ("math.sqrt", "math.sqrt(x): Return the square root of x. Example: math.sqrt(9) -> 3.0."),
    ("math.gcd", "math.gcd(a, b): Return the greatest common divisor of the integers a and b. Example: math.gcd(12, 8) -> 4."),
    ("math.factorial", "math.factorial(n): Return n!, the factorial of n. Example: math.factorial(5) -> 120."),
    ("math.pow", "math.pow(x, y): Return x raised to the power y. Example: math.pow(2, 3) -> 8.0."),
    ("math.log", "math.log(x, base): Return the logarithm of x to the given base. Default base is e. Example: math.log(8, 2) -> 3.0."),
    ("math.pi", "math.pi: The mathematical constant pi = 3.14159..."),
    # re module
    ("re.findall", "re.findall(pattern, string): Return all non-overlapping matches of pattern in string, as a list of strings. Example: re.findall(r'[A-Z]', 'aBcD') -> ['B', 'D']."),
    ("re.sub", "re.sub(pattern, repl, string): Return the string obtained by replacing the leftmost non-overlapping occurrences of pattern with repl. Example: re.sub(r'\\d+', 'X', 'a1b22') -> 'aXbX'."),
    ("re.search", "re.search(pattern, string): Scan through string looking for the first location where the regular expression pattern matches. Returns a Match object, or None."),
    ("re.match", "re.match(pattern, string): If zero or more characters at the beginning of string match the regular expression pattern, return a corresponding Match object."),
    ("re.split", "re.split(pattern, string): Split string by the occurrences of pattern. Example: re.split(r'\\s+', 'a b  c') -> ['a', 'b', 'c']."),
    # itertools module
    ("itertools.combinations", "itertools.combinations(iterable, r): Return r-length subsequences of elements from the input iterable. Example: list(itertools.combinations('ABC', 2)) -> [('A','B'),('A','C'),('B','C')]."),
    ("itertools.permutations", "itertools.permutations(iterable, r): Return successive r-length permutations of elements in the iterable. Example: list(itertools.permutations('AB')) -> [('A','B'),('B','A')]."),
    ("itertools.product", "itertools.product(*iterables): Cartesian product of input iterables. Example: list(itertools.product([1,2],[3,4])) -> [(1,3),(1,4),(2,3),(2,4)]."),
    ("itertools.chain", "itertools.chain(*iterables): Chain iterables together into one iterator. Example: list(itertools.chain([1,2],[3,4])) -> [1,2,3,4]."),
    ("itertools.groupby", "itertools.groupby(iterable, key): Group consecutive elements with the same key. Example: [(k, list(g)) for k,g in itertools.groupby('AAABBC')] -> [('A',['A','A','A']),('B',['B','B']),('C',['C'])]."),
    # collections module
    ("collections.Counter", "collections.Counter(iterable): Dict subclass for counting hashable objects. Example: Counter('abca') -> {'a':2,'b':1,'c':1}. .most_common(n) returns the n highest-count items."),
    ("collections.defaultdict", "collections.defaultdict(default_factory): Dict subclass that calls default_factory to supply missing values. Example: d = defaultdict(list); d['k'].append(1)."),
    ("collections.OrderedDict", "collections.OrderedDict: Dict that remembers insertion order (regular dicts also do since 3.7, but OrderedDict has .move_to_end)."),
    ("collections.deque", "collections.deque([iterable], maxlen): List-like container with fast O(1) appends and pops from either end. .appendleft, .popleft."),
    # functools / operator
    ("functools.reduce", "functools.reduce(function, iterable, initial): Apply function of two arguments cumulatively. Example: reduce(lambda a,b: a+b, [1,2,3], 0) -> 6."),
    ("functools.lru_cache", "functools.lru_cache(maxsize): Decorator to wrap a function with a memoizing callable. Useful for recursive functions."),
    # string methods (common ones HumanEval uses)
    ("string.isdigit", "str.isdigit(): Return True if all characters in the string are digits and there is at least one character. Example: '123'.isdigit() -> True."),
    ("string.isalpha", "str.isalpha(): Return True if all characters in the string are alphabetic and there is at least one character."),
    ("string.split", "str.split(sep): Return a list of the words in the string, using sep as the delimiter. Default sep is whitespace."),
    ("string.join", "str.join(iterable): Return a string which is the concatenation of the strings in iterable, separated by the str. Example: ','.join(['a','b']) -> 'a,b'."),
    ("string.lower", "str.lower(): Return a copy of the string with all cased characters converted to lowercase."),
    ("string.upper", "str.upper(): Return a copy of the string with all cased characters converted to uppercase."),
    ("string.replace", "str.replace(old, new): Return a copy of the string with all occurrences of substring old replaced by new."),
    ("string.startswith", "str.startswith(prefix): Return True if string starts with the prefix."),
    ("string.endswith", "str.endswith(suffix): Return True if string ends with the suffix."),
    ("string.strip", "str.strip([chars]): Return a copy of the string with the leading and trailing characters removed."),
    # list operations (Python builtin patterns)
    ("list.enumerate", "enumerate(iterable, start=0): Return an enumerate object yielding (index, value) pairs. Example: list(enumerate(['a','b'])) -> [(0,'a'),(1,'b')]."),
    ("list.zip", "zip(*iterables): Aggregate elements from each of the iterables. Example: list(zip([1,2],[3,4])) -> [(1,3),(2,4)]."),
    ("list.sorted", "sorted(iterable, key, reverse): Return a new sorted list. key=function to extract comparison key; reverse=True for descending."),
    ("list.map_filter", "map(fn, iterable) returns iterator of fn applied to each item; filter(fn, iterable) returns iterator of items where fn(item) is True."),
    ("list.sum", "sum(iterable, start=0): Return the sum of items in the iterable plus start."),
]

# ============================================================================
# Substrate-as-index: phasor codebook for keyword retrieval (lightweight)
# but the actual retrieval uses MiniLM cosine since stdlib docs are short text.
# The phasor substrate component is mostly bookkeeping (substrate_role tracked).
# ============================================================================
_BOOK: Dict[str, np.ndarray] = {}
_RNG = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "991")))
def _phasor(w: str) -> np.ndarray:
    if w not in _BOOK:
        ang = (_RNG.random(N_DIM) * 2 - 1) * math.pi
        _BOOK[w] = np.exp(1j * ang).astype(np.complex64)
    return _BOOK[w]
def _kw(text: str) -> List[str]:
    return [w for w in re.findall(r"[a-z_]+", text.lower()) if len(w) > 2]
def _bundle(words: List[str]) -> np.ndarray:
    v = np.zeros(N_DIM, dtype=np.complex64)
    for w in words:
        v = v + _phasor(w)
    n = np.abs(v); n[n == 0] = 1
    return (v / n).astype(np.complex64)

# ============================================================================
# MiniLM-based retrieval over the stdlib snippet corpus
# (substrate role = INDEX; the embedding model is the encoder; cosine is the retrieval op)
# ============================================================================
_ENC = None
_SNIP_EMB = None
def _load_encoder():
    global _ENC, _SNIP_EMB
    if _ENC is not None:
        return _ENC, _SNIP_EMB
    from sentence_transformers import SentenceTransformer
    print("[encoder] loading MiniLM-L6-v2 ...", flush=True)
    t0 = time.time()
    _ENC = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    snip_texts = [s for (_id, s) in STDLIB_SNIPPETS]
    _SNIP_EMB = _ENC.encode(snip_texts, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
    print("[encoder] loaded MiniLM + indexed %d snippets in %.1fs" % (len(STDLIB_SNIPPETS), time.time() - t0), flush=True)
    return _ENC, _SNIP_EMB

def _retrieve_snippets(prompt: str, top_k: int = TOP_K_RETRIEVE) -> List[Tuple[str, str, float]]:
    enc, snip_emb = _load_encoder()
    q = enc.encode([prompt], normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)[0]
    sims = snip_emb @ q
    top_idx = np.argsort(-sims)[:top_k]
    return [(STDLIB_SNIPPETS[i][0], STDLIB_SNIPPETS[i][1], float(sims[i])) for i in top_idx]

# ============================================================================
# Class label heuristic
# ============================================================================
def _classify(canonical_solution: str) -> str:
    """Return 'A' if canonical_solution uses Python stdlib modules, else 'B'."""
    s = canonical_solution
    for pat in STDLIB_PATTERNS:
        if pat in s:
            return "A"
    return "B"

# ============================================================================
# Qwen-1.5B inference (CPU, fp32, greedy)
# ============================================================================
_TOK = None
_MODEL = None
def _load_qwen():
    global _TOK, _MODEL
    if _TOK is not None:
        return _TOK, _MODEL
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    print("[qwen] loading Qwen2.5-1.5B-Instruct (cpu, fp32) ...", flush=True)
    t0 = time.time()
    _TOK = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
    _MODEL = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct", dtype=torch.float32)
    _MODEL.eval()
    print("[qwen] loaded in %.1fs (%dM params)" % (time.time() - t0, sum(p.numel() for p in _MODEL.parameters()) // 1_000_000), flush=True)
    return _TOK, _MODEL

def _qwen_generate(prompt_text: str) -> Tuple[str, float, int]:
    """Greedy-generate code completion. Returns (generated_text, wall_s, n_new_tokens)."""
    import torch
    tok, model = _load_qwen()
    msgs = [{"role": "user", "content": prompt_text}]
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    inputs = tok(text, return_tensors="pt")
    t0 = time.time()
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            pad_token_id=tok.eos_token_id,
        )
    wall = time.time() - t0
    _LLM_CALL_COUNTER[0] += 1
    n_new = int(out.shape[1] - inputs.input_ids.shape[1])
    gen = tok.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    return gen, wall, n_new

# ============================================================================
# Prompt builders
# ============================================================================
def _bare_prompt(problem_prompt: str) -> str:
    return (
        "Complete the Python function below. Output ONLY the function body (or the full function definition); "
        "do not include any text outside a single Python code block. Wrap your code in ```python ... ```.\n\n"
        + problem_prompt
    )

def _augmented_prompt(problem_prompt: str, snippets: List[Tuple[str, str, float]]) -> str:
    docs = "\n".join("- %s: %s" % (sid, stext) for (sid, stext, _sim) in snippets)
    return (
        "You are completing a Python function. The following Python stdlib reference snippets "
        "may be relevant; use them only if they help:\n"
        + docs
        + "\n\nNow complete the function below. Output ONLY the function body (or the full function definition); "
        "do not include any text outside a single Python code block. Wrap your code in ```python ... ```.\n\n"
        + problem_prompt
    )

# ============================================================================
# Code extraction + sandbox execution
# ============================================================================
_CODE_BLOCK = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)
def _extract_imports_from_prompt(problem_prompt: str) -> str:
    """Extract import statements + 'from typing import ...' lines from the HumanEval prompt header.

    HumanEval prompts typically begin with imports (e.g., 'from typing import List') BEFORE the def
    signature. Qwen's generated code block usually omits these even when it uses List/Tuple types,
    causing NameError at test time. We always prepend the prompt's imports to the executed module."""
    lines = problem_prompt.split("\n")
    imports = []
    for ln in lines:
        s = ln.strip()
        if s.startswith("from ") or s.startswith("import "):
            imports.append(ln)
        elif s.startswith("def ") or s.startswith("class "):
            break
    return "\n".join(imports)

def _extract_code(gen_text: str, problem_prompt: str, entry_point: str) -> str:
    """Extract a runnable Python module given Qwen's generation + the original prompt + entry_point."""
    m = _CODE_BLOCK.search(gen_text)
    code = m.group(1) if m else gen_text
    imports = _extract_imports_from_prompt(problem_prompt)
    # If the extracted code already defines entry_point, prepend just the imports from the prompt
    # (Qwen wrote the full def but typically omits 'from typing import List' etc.).
    if re.search(r"def\s+" + re.escape(entry_point) + r"\s*\(", code):
        return (imports + "\n" + code) if imports else code
    # Otherwise treat as a body: combine the full problem_prompt (signature + docstring + imports) with the body.
    return problem_prompt + "\n" + code

def _run_tests(module_src: str, test_src: str, entry: str) -> Tuple[bool, str]:
    """Returns (pass, brief_error)."""
    src = module_src + "\n\n" + test_src + "\n\ncheck(%s)\n" % entry
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(src)
        path = f.name
    try:
        p = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=GEN_TIMEOUT_S)
        if p.returncode == 0:
            return True, ""
        err = (p.stderr or p.stdout or "")[-200:].strip()
        return False, err
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, "EXC:" + str(e)[:100]
    finally:
        try:
            os.unlink(path)
        except Exception:
            pass

# ============================================================================
# Config version (load-bearing for resume + Skunkworks audit)
# ============================================================================
def _config_version() -> str:
    snip_hash = hashlib.sha1(("\n".join("%s:%s" % t for t in STDLIB_SNIPPETS)).encode("utf-8")).hexdigest()[:8]
    return "v1_N%d_K%d_T%d_snip%s" % (N_DIM, TOP_K_RETRIEVE, MAX_NEW_TOKENS, snip_hash)

CONFIG_VERSION = _config_version()

# ============================================================================
# Selftest (mechanism check, no LLM load)
# ============================================================================
def _selftest():
    """Mechanism unit-test (no encoder load; sentence_transformers + torch only required at run() time).

    NOTE: queue_add.py's --self-test gate uses system python, NOT .venv (the runner itself uses .venv).
    Keep this selftest dependency-free: only stdlib + numpy. Encoder/MiniLM/torch tests live in run()."""
    # classification
    assert _classify("import math\n  return math.floor(x)") == "A"
    assert _classify("    return sum(x)") == "B"
    assert _classify("from collections import Counter\n  return Counter(s)") == "A"
    # phasor bundle round-trip (substrate as index)
    qv = _bundle(_kw("compute factorial of n using math"))
    assert qv.shape == (N_DIM,)
    # snippet corpus integrity
    assert len(STDLIB_SNIPPETS) >= 30, "need >=30 stdlib snippets for non-trivial coverage"
    ids = [s[0] for s in STDLIB_SNIPPETS]
    assert "math.factorial" in ids and "itertools.combinations" in ids and "collections.Counter" in ids
    # code extraction
    fake_gen = "Sure here's the code:\n```python\ndef foo(x):\n    return x+1\n```"
    code = _extract_code(fake_gen, "def foo(x):\n", "foo")
    assert "def foo" in code and "return x+1" in code
    # sandbox runs and passes a trivial test
    src = "def foo(x):\n    return x+1\n"
    test = "def check(c):\n    assert c(1) == 2\n"
    ok, _e = _run_tests(src, test, "foo")
    assert ok, "sandbox should pass trivial test"
    # typing-import bug fix: Qwen often writes `def foo(x) -> List[int]:` without `from typing import List`.
    # _extract_code MUST prepend imports from the problem prompt.
    typing_prompt = "from typing import List\n\n\ndef foo(x: int) -> List[int]:\n    \"\"\"return [x]\"\"\"\n"
    typing_gen = "```python\ndef foo(x: int) -> List[int]:\n    return [x]\n```"
    typing_code = _extract_code(typing_gen, typing_prompt, "foo")
    assert "from typing import List" in typing_code, "must prepend typing import from prompt"
    typing_test = "def check(c):\n    assert c(3) == [3]\n"
    ok2, e2 = _run_tests(typing_code, typing_test, "foo")
    assert ok2, "typing-import sandbox should pass, got: " + e2
    # config version reproducible
    cv = _config_version()
    assert cv.startswith("v1_") and len(cv) > 10
    print("[selftest] PASS: humaneval_stdlib_split_qwen (%d snippets, %d patterns, config=%s)" % (len(STDLIB_SNIPPETS), len(STDLIB_PATTERNS), CONFIG_VERSION), flush=True)

# ============================================================================
# Run
# ============================================================================
def run() -> Dict:
    try:
        from datasets import load_dataset
        ds = load_dataset("openai_humaneval", split="test")
    except Exception as e:
        print("[data] fail %s" % str(e)[:120], flush=True)
        return {"error": "load_failed:" + str(e)[:120]}
    items = list(ds)
    # classify all (cheap; needed for both smoke + full)
    for it in items:
        it["_class"] = _classify(it.get("canonical_solution", ""))
    # smoke: 10 problems, mixed classes (first 6 of class A + first 4 of class B if available)
    if SMOKE:
        a_items = [it for it in items if it["_class"] == "A"][:6]
        b_items = [it for it in items if it["_class"] == "B"][:4]
        items = a_items + b_items
        print("[smoke] selected %d problems (A=%d B=%d)" % (len(items), len(a_items), len(b_items)), flush=True)

    n_total = len(items)
    n_A = sum(1 for it in items if it["_class"] == "A")
    n_B = n_total - n_A
    print("[run] n_total=%d n_A=%d n_B=%d" % (n_total, n_A, n_B), flush=True)

    per_problem = []
    for i, it in enumerate(items):
        cls = it["_class"]
        prompt = it["prompt"]
        test = it["test"]
        entry = it["entry_point"]
        # Bare arm
        bare_p = _bare_prompt(prompt)
        bare_gen, bare_wall, bare_ntok = _qwen_generate(bare_p)
        bare_code = _extract_code(bare_gen, prompt, entry)
        bare_pass, bare_err = _run_tests(bare_code, test, entry)
        # Substrate-augmented arm
        snips = _retrieve_snippets(prompt, TOP_K_RETRIEVE)
        sub_p = _augmented_prompt(prompt, snips)
        sub_gen, sub_wall, sub_ntok = _qwen_generate(sub_p)
        sub_code = _extract_code(sub_gen, prompt, entry)
        sub_pass, sub_err = _run_tests(sub_code, test, entry)
        per_problem.append({
            "task_id": it["task_id"],
            "class": cls,
            "entry_point": entry,
            "bare_pass": bool(bare_pass), "bare_wall": round(bare_wall, 2), "bare_ntok": bare_ntok, "bare_err": bare_err[:120],
            "sub_pass": bool(sub_pass), "sub_wall": round(sub_wall, 2), "sub_ntok": sub_ntok, "sub_err": sub_err[:120],
            "snippets_top": [sid for (sid, _t, _s) in snips],
            "snippet_top_sim": float(snips[0][2]) if snips else 0.0,
        })
        elapsed_total = sum(p["bare_wall"] + p["sub_wall"] for p in per_problem)
        print("  [%d/%d] %s class=%s bare=%s sub=%s top_snip=%s wall=%.1f|%.1fs elapsed=%.0fs"
              % (i + 1, n_total, it["task_id"], cls, "P" if bare_pass else "f",
                 "P" if sub_pass else "f", snips[0][0] if snips else "-",
                 bare_wall, sub_wall, elapsed_total), flush=True)

    # Aggregate
    def _rate(items_subset, key):
        if not items_subset:
            return 0.0
        return sum(1 for p in items_subset if p[key]) / len(items_subset)

    A_items = [p for p in per_problem if p["class"] == "A"]
    B_items = [p for p in per_problem if p["class"] == "B"]
    pass1_A_bare = _rate(A_items, "bare_pass")
    pass1_A_sub = _rate(A_items, "sub_pass")
    pass1_B_bare = _rate(B_items, "bare_pass")
    pass1_B_sub = _rate(B_items, "sub_pass")
    gain_A = pass1_A_sub - pass1_A_bare
    gain_B = pass1_B_sub - pass1_B_bare

    print("\n[aggregate] Class A (stdlib, n=%d): bare=%.3f sub=%.3f gain=%+.3f" % (len(A_items), pass1_A_bare, pass1_A_sub, gain_A), flush=True)
    print("[aggregate] Class B (algo, n=%d): bare=%.3f sub=%.3f gain=%+.3f" % (len(B_items), pass1_B_bare, pass1_B_sub, gain_B), flush=True)

    return {
        "per_problem": per_problem,
        "class_label_counts": {"A": n_A, "B": n_B, "total": n_total},
        "pass1_A_bare": round(pass1_A_bare, 4), "pass1_A_sub": round(pass1_A_sub, 4),
        "pass1_B_bare": round(pass1_B_bare, 4), "pass1_B_sub": round(pass1_B_sub, 4),
        "gain_A": round(gain_A, 4), "gain_B": round(gain_B, 4),
        "substrate_native": SUBSTRATE_NATIVE, "substrate_role": SUBSTRATE_ROLE,
        "llm_calls_at_inference": _LLM_CALL_COUNTER[0],
        "n_stdlib_snippets": len(STDLIB_SNIPPETS), "top_k_retrieve": TOP_K_RETRIEVE,
        "max_new_tokens": MAX_NEW_TOKENS,
    }

# ============================================================================
# Verdict (pre-reg bands; honors direction)
# ============================================================================
def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    gA = r["gain_A"]; gB = r["gain_B"]
    pA_b = r["pass1_A_bare"]; pA_s = r["pass1_A_sub"]; pB_b = r["pass1_B_bare"]; pB_s = r["pass1_B_sub"]
    summary = "ClassA bare=%.3f sub=%.3f gain=%+.3f; ClassB bare=%.3f sub=%.3f gain=%+.3f" % (pA_b, pA_s, gA, pB_b, pB_s, gB)
    # Pre-reg-direction check: gain_A < -0.05 = HARD_FAIL (sub harms)
    if gA < -0.05:
        return ("HARD_FAIL", "HARD_FAIL (wrong-direction): substrate augmentation HARMS Qwen on Class A (gain=%+.3f). " % gA + summary)
    if gA >= 0.15:
        # Discriminating-regime check: if Class B also gained >= +0.05, the lift is NOT stdlib-retrieval-specific
        if gB >= 0.05:
            return ("MIDDLE_BAND",
                    "MIDDLE_BAND: ClassA gain %+.3f >= +0.15 BUT ClassB gain %+.3f >= +0.05 -- lift not retrieval-specific (any context helps); discriminating-regime FAIL. " % (gA, gB) + summary)
        return ("HARD_PASS",
                "HARD_PASS: substrate-augmented Qwen-1.5B improves Class A (stdlib) pass@1 by %+.3f over bare, AND Class B gain %+.3f confirms the lift is retrieval-specific. " % (gA, gB) + summary)
    if gA >= 0.05:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: ClassA gain %+.3f in [+0.05, +0.15); below HARD_PASS bar but mechanism shows signal. " % gA + summary)
    return ("HARD_FAIL",
            "HARD_FAIL: ClassA gain %+.3f < +0.05; substrate augmentation does not meaningfully help Qwen on stdlib problems. " % gA + summary)

# ============================================================================
# Entry point
# ============================================================================
if __name__ == "__main__" or _ARGS.self_test:
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)
    print("[config] anchor=%s mode=%s N_DIM=%d top_k=%d max_new=%d config_version=%s"
          % (ANCHOR_NAME, RUN_MODE, N_DIM, TOP_K_RETRIEVE, MAX_NEW_TOKENS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    r = run()
    v, vmsg = verdict(r)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": 1,
        "config_version": CONFIG_VERSION,
        "substrate_native": SUBSTRATE_NATIVE,
        "substrate_role": SUBSTRATE_ROLE,
        "per_seed": [r],
        "elapsed_s": round(time.time() - t0, 1),
    }
    write_metrics(out_dir, metrics, [r])
    print("[metrics] written to %s" % out_dir, flush=True)
