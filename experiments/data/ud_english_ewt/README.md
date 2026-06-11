# UD-English-EWT (bundled for dep-parse RESCUE-1)
Source: https://github.com/UniversalDependencies/UD_English-EWT (master).
dev/test = full; train = first 5000 sentences (lean for git; full 12544 available at source).
Load via experiments/_ud_loader.py: load_conllu('train'|'dev'|'test') -> [(idx, form, upos, head, deprel), ...] per sentence.
Resolves the 2-cycle dep-parser corpus blocker (no runtime download -> no UNKNOWN).
