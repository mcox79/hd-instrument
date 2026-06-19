"""Deterministic question set tied to synthetic-corpus ground truth.

Each question:
  - Has an exact expected answer derived from CorpusGroundTruth
  - Is identical across both conditions (substrate-with-tools and LLM-only)
  - Carries a structured `keys` list so the mock LLM (and a real LLM in
    deterministic-prompt mode) can resolve the underlying corpus lookups

For real-LLM Tier 2b runs the test_question string is what the LLM sees;
the keys list is used by:
  - The mock LLM (extracts retrieval plan from KEYS: line)
  - The harness for fairness checks (in tool-call mode, did the LLM
    actually hit every required key? -- a coverage metric)
"""

from __future__ import annotations

from dataclasses import dataclass, field

from hdlab_service.corpora.synthetic_corpus import Corpus


@dataclass
class TestQuestion:
    """One row of the comparison-harness question set."""
    qid: str
    category: str                # "single_hop" | "edit_aware" | "multi_hop"
    test_question: str           # What the LLM sees (already includes KEYS line)
    keys: list[str]              # Corpus key(s) to look up for ground truth
    expected_answer: str         # Ground-truth string (or " | "-joined for multi-hop)
    requires_edit_setup: dict | None = field(default=None)
    # If set, the harness applies these edits BEFORE asking the question.
    # Shape: {atom_id_lookup_key: new_value}
    # e.g. {"p_00__name": "EDITED_NAME"} means: edit p_00's name to
    # "EDITED_NAME" before asking the question.


def build_question_set(corpus: Corpus) -> list[TestQuestion]:
    """Return a deterministic question set keyed off the corpus ground truth.

    Default set:
      4 single-hop  : name/role/founded_year/category lookups
      2 edit-aware  : pose a question after a known edit; correct answer
                      reflects the edited value
      2 multi-hop   : "who manages product X" requires 3 hops
                      (product_name + manages-edge + manager_name)
      1 long-tail   : reports_to chain (2 hops)
    """
    gt = corpus.ground_truth
    out: list[TestQuestion] = []

    # ---- Single-hop ----
    p0_id = "p_00"
    p0_name = gt.person_name[p0_id]
    out.append(TestQuestion(
        qid="single_hop_person_name",
        category="single_hop",
        test_question=(
            f"What is the stored name for {p0_id}?\n"
            f"KEYS: {p0_id}__name"
        ),
        keys=[f"{p0_id}__name"],
        expected_answer=p0_name,
    ))

    p1_id = "p_01"
    p1_role = gt.person_role[p1_id]
    out.append(TestQuestion(
        qid="single_hop_person_role",
        category="single_hop",
        test_question=(
            f"What is the role of person {p1_id}?\n"
            f"KEYS: {p1_id}__role"
        ),
        keys=[f"{p1_id}__role"],
        expected_answer=p1_role,
    ))

    c0_id = "c_00"
    c0_year = str(gt.company_founded[c0_id])
    out.append(TestQuestion(
        qid="single_hop_company_year",
        category="single_hop",
        test_question=(
            f"What year was {c0_id} founded?\n"
            f"KEYS: {c0_id}__founded_year"
        ),
        keys=[f"{c0_id}__founded_year"],
        expected_answer=c0_year,
    ))

    prod0_id = "prod_00"
    prod0_cat = gt.product_category[prod0_id]
    out.append(TestQuestion(
        qid="single_hop_product_category",
        category="single_hop",
        test_question=(
            f"What is the category of {prod0_id}?\n"
            f"KEYS: {prod0_id}__category"
        ),
        keys=[f"{prod0_id}__category"],
        expected_answer=prod0_cat,
    ))

    # ---- Edit-aware ----
    # Edit p_02's name then ask; correct answer is the edited value.
    edited_name = "EDIT_AWARE_NAME_2"
    out.append(TestQuestion(
        qid="edit_aware_name",
        category="edit_aware",
        test_question=(
            f"After all updates, what is the current name of p_02?\n"
            f"KEYS: p_02__name"
        ),
        keys=["p_02__name"],
        expected_answer=edited_name,
        requires_edit_setup={"p_02__name": edited_name},
    ))

    edited_year = "9999"
    out.append(TestQuestion(
        qid="edit_aware_year",
        category="edit_aware",
        test_question=(
            f"After all updates, what year is recorded for c_00's founding?\n"
            f"KEYS: c_00__founded_year"
        ),
        keys=["c_00__founded_year"],
        expected_answer=edited_year,
        requires_edit_setup={"c_00__founded_year": edited_year},
    ))

    # ---- Multi-hop (3 hops: product name -> manages-edge -> manager name) ----
    if gt.manager_of_product:
        # Use a stable product (smallest id) so the harness is deterministic.
        target_product = sorted(gt.manager_of_product.keys())[0]
        target_manager = gt.manager_of_product[target_product]
        product_name = gt.product_name[target_product]
        manager_name = gt.person_name[target_manager]
        out.append(TestQuestion(
            qid="multi_hop_product_to_manager",
            category="multi_hop",
            test_question=(
                f"Who manages the product {target_product}? "
                f"Provide product name, the manages-edge fact, and manager name.\n"
                f"KEYS: {target_product}__name "
                f"{target_manager}__manages__{target_product} "
                f"{target_manager}__name"
            ),
            keys=[
                f"{target_product}__name",
                f"{target_manager}__manages__{target_product}",
                f"{target_manager}__name",
            ],
            expected_answer=f"{product_name} | true | {manager_name}",
        ))

        # Second multi-hop: product -> company -> company_name
        target_company = gt.product_of_company[target_product]
        company_name = gt.company_name[target_company]
        out.append(TestQuestion(
            qid="multi_hop_product_to_company",
            category="multi_hop",
            test_question=(
                f"Which company makes {target_product}? "
                f"Provide product name, makes-edge fact, and company name.\n"
                f"KEYS: {target_product}__name "
                f"{target_company}__makes__{target_product} "
                f"{target_company}__name"
            ),
            keys=[
                f"{target_product}__name",
                f"{target_company}__makes__{target_product}",
                f"{target_company}__name",
            ],
            expected_answer=f"{product_name} | true | {company_name}",
        ))

    # ---- Long-tail (reports_to chain) ----
    if gt.reports_to:
        subordinate = sorted(gt.reports_to.keys())[0]
        manager = gt.reports_to[subordinate]
        sub_name = gt.person_name[subordinate]
        mgr_name = gt.person_name[manager]
        out.append(TestQuestion(
            qid="long_tail_reports_to",
            category="multi_hop",
            test_question=(
                f"Who does {subordinate} report to? Provide the report's name "
                f"and the manager's name.\n"
                f"KEYS: {subordinate}__name {manager}__name"
            ),
            keys=[f"{subordinate}__name", f"{manager}__name"],
            expected_answer=f"{sub_name} | {mgr_name}",
        ))

    return out
