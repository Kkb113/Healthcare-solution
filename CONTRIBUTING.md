# Repository conventions

Use descriptive filenames that explain the artifact's purpose. Python modules/scripts use `snake_case.py`; documents, configuration, reference packages and evidence use `kebab-case`. Record implementation phase numbers inside documents and manifests, not in new filenames or directory names. Existing versioned paths retain their historical names.

Keep canonical healthcare table/column names consistent with the frozen schema. Generated datasets, public download caches, SQLite stores and temporary test outputs belong under ignored `output/` or `data/`. Commit code, configuration, bounded aggregate reference packages, documentation and explicitly selected review/evidence artifacts. Never commit credentials or real individual records.

Changes to frozen contracts require explicit baseline review. A completed implementation phase must include passing applicable exit checks, reproducibility evidence and a commit/push. A master-data gate never substitutes for final healthcare data acceptance or authorizes solution development.
