"""Synthetic fact corpus generator with controlled ground truth.

Produces a deterministic relational graph (people -> companies -> products ->
managers) plus a property bag, so capability tests have:

  - Exact ground-truth answers (no LLM ambiguity)
  - Reproducible state across runs (seeded RNG)
  - Tunable corpus size (small for fast tests, larger for stress)
  - Clean multi-hop chains (e.g. "who manages the product line that ACME makes?")

This is intentionally domain-neutral. Per the Tier 2 revised goal in
notes/session_kickoff_testbed_v1.md ("capability-generic first, domain
commitment last"), tests should validate substrate properties without
implying a specific deployment target.

Schema:
  Person:   p_<n>  ->  {name, role}
  Company:  c_<n>  ->  {name, founded_year}
  Product:  prod_<n> -> {name, category}
  Edges:
    employs(company, person)
    makes(company, product)
    manages(person, product)
    reports_to(person, person)

Facts emitted as (key, value) pairs suitable for /store_fact:
  ("p_<n>__name", "Alice")
  ("p_<n>__role", "engineer")
  ("c_<n>__name", "ACME Corp")
  ("c_<n>__founded_year", "1987")
  ("prod_<n>__name", "Widget X")
  ("prod_<n>__category", "consumer")
  ("c_<n>__employs__p_<m>", "true")
  ("c_<n>__makes__prod_<m>", "true")
  ("p_<n>__manages__prod_<m>", "true")
  ("p_<n>__reports_to__p_<m>", "true")

The generator returns both the (key, value) sequence AND a ground-truth
dict so tests can ASK substrate a question and check the answer against
the dict without having to re-derive it from the corpus.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from random import Random


# Vocabulary pools (small, deterministic; chosen to be evocative without
# committing to a domain).
_FIRST_NAMES = [
    "Alice", "Bob", "Carol", "Dan", "Eve", "Frank", "Grace", "Hugo",
    "Iris", "Jack", "Kara", "Liam", "Mia", "Noah", "Olive", "Pete",
    "Quinn", "Ravi", "Sara", "Tom", "Uma", "Vic", "Wren", "Xena",
    "Yael", "Zane",
]
_ROLES = ["engineer", "manager", "designer", "analyst", "researcher",
          "operator", "director", "lead"]
_COMPANY_BASES = [
    "ACME", "Globex", "Initech", "Hooli", "Massive Dynamic", "Stark",
    "Tyrell", "Soylent", "Aperture", "Umbrella", "Wayne", "Wonka",
]
_COMPANY_SUFFIXES = ["Corp", "Industries", "Group", "Holdings", "Labs", "Co."]
_PRODUCT_BASES = ["Widget", "Beacon", "Catalyst", "Drift", "Echo",
                  "Forge", "Glow", "Halo", "Iris", "Joule"]
_PRODUCT_SUFFIXES = ["X", "Pro", "Plus", "One", "Mini", "Max", "Ultra"]
_CATEGORIES = ["consumer", "industrial", "enterprise", "healthcare", "edge"]


@dataclass
class CorpusFact:
    """One (key, value) pair to be stored."""
    key: str
    value: str


@dataclass
class CorpusGroundTruth:
    """Ground-truth lookups so tests don't have to re-derive answers."""
    person_name: dict[str, str] = field(default_factory=dict)         # p_n -> name
    person_role: dict[str, str] = field(default_factory=dict)         # p_n -> role
    company_name: dict[str, str] = field(default_factory=dict)        # c_n -> name
    company_founded: dict[str, int] = field(default_factory=dict)     # c_n -> year
    product_name: dict[str, str] = field(default_factory=dict)        # prod_n -> name
    product_category: dict[str, str] = field(default_factory=dict)    # prod_n -> category
    employs: dict[str, list[str]] = field(default_factory=dict)       # c_n -> [p_n,...]
    makes: dict[str, list[str]] = field(default_factory=dict)         # c_n -> [prod_n,...]
    manages: dict[str, list[str]] = field(default_factory=dict)       # p_n -> [prod_n,...]
    reports_to: dict[str, str] = field(default_factory=dict)          # p_n -> p_n
    # Inverse lookups for convenient multi-hop tests.
    product_of_company: dict[str, str] = field(default_factory=dict)  # prod_n -> c_n
    manager_of_product: dict[str, str] = field(default_factory=dict)  # prod_n -> p_n
    employer_of_person: dict[str, str] = field(default_factory=dict)  # p_n -> c_n


@dataclass
class Corpus:
    """A generated synthetic corpus."""
    facts: list[CorpusFact]
    ground_truth: CorpusGroundTruth
    seed: int
    n_people: int
    n_companies: int
    n_products: int


def generate_corpus(
    seed: int = 42,
    n_people: int = 12,
    n_companies: int = 3,
    n_products: int = 6,
) -> Corpus:
    """Generate a deterministic synthetic corpus.

    With the default sizes (12 people, 3 companies, 6 products) the corpus
    has ~50-60 facts: small enough to fit in a single Pattern B context
    window for the LLM-only baseline comparison, large enough to make
    multi-hop traversal non-trivial.

    Args:
        seed: RNG seed; same seed -> identical corpus.
        n_people, n_companies, n_products: corpus sizing knobs.

    Returns:
        Corpus with `.facts` (list of CorpusFact) and `.ground_truth`
        (CorpusGroundTruth) populated.
    """
    rng = Random(seed)
    gt = CorpusGroundTruth()
    facts: list[CorpusFact] = []

    # People (sampled without replacement from name pool; cycle if exhausted).
    name_pool = _FIRST_NAMES * ((n_people // len(_FIRST_NAMES)) + 1)
    rng.shuffle(name_pool)
    for i in range(n_people):
        pid = f"p_{i:02d}"
        name = name_pool[i]
        role = rng.choice(_ROLES)
        gt.person_name[pid] = name
        gt.person_role[pid] = role
        facts.append(CorpusFact(f"{pid}__name", name))
        facts.append(CorpusFact(f"{pid}__role", role))

    # Companies.
    for i in range(n_companies):
        cid = f"c_{i:02d}"
        name = f"{rng.choice(_COMPANY_BASES)} {rng.choice(_COMPANY_SUFFIXES)}"
        year = rng.randint(1950, 2020)
        gt.company_name[cid] = name
        gt.company_founded[cid] = year
        facts.append(CorpusFact(f"{cid}__name", name))
        facts.append(CorpusFact(f"{cid}__founded_year", str(year)))

    # Products.
    for i in range(n_products):
        prid = f"prod_{i:02d}"
        name = f"{rng.choice(_PRODUCT_BASES)} {rng.choice(_PRODUCT_SUFFIXES)}"
        category = rng.choice(_CATEGORIES)
        gt.product_name[prid] = name
        gt.product_category[prid] = category
        facts.append(CorpusFact(f"{prid}__name", name))
        facts.append(CorpusFact(f"{prid}__category", category))

    # Edges: employs (each company gets ~n_people/n_companies employees).
    people_ids = [f"p_{i:02d}" for i in range(n_people)]
    companies_ids = [f"c_{i:02d}" for i in range(n_companies)]
    rng.shuffle(people_ids)
    chunk = max(1, n_people // n_companies)
    for ci, cid in enumerate(companies_ids):
        start, end = ci * chunk, (ci + 1) * chunk if ci < n_companies - 1 else n_people
        members = people_ids[start:end]
        gt.employs[cid] = members
        for pid in members:
            gt.employer_of_person[pid] = cid
            facts.append(CorpusFact(f"{cid}__employs__{pid}", "true"))

    # Edges: makes (products distributed across companies).
    product_ids = [f"prod_{i:02d}" for i in range(n_products)]
    for i, prid in enumerate(product_ids):
        cid = companies_ids[i % n_companies]
        gt.makes.setdefault(cid, []).append(prid)
        gt.product_of_company[prid] = cid
        facts.append(CorpusFact(f"{cid}__makes__{prid}", "true"))

    # Edges: manages (one manager per product, drawn from the maker company's
    # employees so the multi-hop traversal is closed).
    for prid in product_ids:
        cid = gt.product_of_company[prid]
        employees = gt.employs.get(cid, [])
        if not employees:
            continue
        manager = rng.choice(employees)
        gt.manages.setdefault(manager, []).append(prid)
        gt.manager_of_product[prid] = manager
        facts.append(CorpusFact(f"{manager}__manages__{prid}", "true"))

    # Edges: reports_to (one chain per company; first listed employee is the
    # top of the chain).
    for cid, employees in gt.employs.items():
        if len(employees) < 2:
            continue
        for j in range(1, len(employees)):
            gt.reports_to[employees[j]] = employees[0]
            facts.append(CorpusFact(
                f"{employees[j]}__reports_to__{employees[0]}", "true"
            ))

    return Corpus(
        facts=facts,
        ground_truth=gt,
        seed=seed,
        n_people=n_people,
        n_companies=n_companies,
        n_products=n_products,
    )


def corpus_as_context_string(corpus: Corpus) -> str:
    """Render the corpus as a plain text dump for the LLM-only baseline.

    The substrate-backed condition uses tool calls; the LLM-only condition
    needs the same facts in the system prompt. Same corpus, two delivery
    mechanisms -- the controlled comparison.

    Format is line-based "<key> = <value>" so the LLM can scan + retrieve
    without parsing JSON.
    """
    lines = ["# Synthetic fact corpus", ""]
    for f in corpus.facts:
        lines.append(f"{f.key} = {f.value}")
    return "\n".join(lines)


# Convenient single-call factory for tests.
def small_corpus() -> Corpus:
    """Default small corpus used by capability tests (seed=42)."""
    return generate_corpus(seed=42, n_people=12, n_companies=3, n_products=6)
