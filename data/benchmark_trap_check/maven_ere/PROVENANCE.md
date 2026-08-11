SOURCE: https://github.com/THU-KEG/MAVEN-ERE (Wang et al., EMNLP 2022, arXiv:2211.07342)
Data obtained via the Tsinghua Cloud mirror linked from the repo README / data/download_maven.sh:
https://cloud.tsinghua.edu.cn/f/a7d1db6c44ea458bb6f0/?dl=1 (MAVEN_ERE.zip, ver. 1.0)
Fetched 2026-08-10. train.jsonl (2913 docs) + valid.jsonl (710 docs) kept here (untracked,
too large for git per repo convention -- see .gitignore data/*/** ; NOT force-added).
test.jsonl (857 docs) intentionally NOT copied here: gold causal_relations/subevent_relations
are hidden per the repo README (CodaLab-competition-only evaluation) and are not used by
tools/benchmark_trap_check/maven_ere_trap_check.py, which only reads train.jsonl + valid.jsonl.
