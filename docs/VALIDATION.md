# Release validation

Local checks completed on 2026-11-12:

| Check | Outcome |
| --- | --- |
| `make reproduce` | Passed; all analysis stages completed |
| Frozen evidence verification | 247 retained evidence files passed size/SHA-256 checks; current ledger sources also verified |
| Dataset verification | Cached development Parquet matched the pinned SHA-256 |
| Result preservation | Scientific data and table values match the pre-cleanup release; source-path columns and ledger hashes follow the consolidated layout |
| Figures | All eight PDF/PNG figure pairs regenerated |
| `make paper` | Passed; 16-page PDF compiled |
| Tampered evidence check | An altered input with the release manifest was rejected |
| Corrupt dataset check | A cached file with the wrong digest was rejected |
| Cleanup | Retained evidence has no duplicate SHA-256 values or transfer ZIPs; rebuilding creates no duplicate ledger/coverage exports |
| Documentation | Local links and section anchors resolve in the consolidated layout |
| Credential pattern scan | No matches for common Hugging Face, GitHub, OpenAI token formats or private-key headers |

Local analysis environment: Python 3.10.16, NumPy 2.2.6, Matplotlib 3.10.9, PyArrow 25.0.1. Compilation used TeX Live 2022 and latexmk 4.76.

The download URL was not exercised in this network-restricted environment; the pinned bytes already present in the research workspace were verified instead. GitHub Actions is configured for Python 3.11 and will run after the repository is pushed. No GPU generation or benchmark execution was repeated during preparation.

The workspace's auxiliary JEV review helper was invoked but could not reach its service because DNS/network access was unavailable. The source changes were inspected directly, and the reproduction and integrity checks above provide the local validation.
