# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Startup workflow and scope

Before writing code:

1. Read this file and the relevant source/tests.
2. Read `feature_list.json` and `progress.md`; continue the single `in-progress` feature, or select one ready `not-started` feature whose dependencies are complete.
3. Run `./init.sh` to establish the baseline. If it fails because the environment is unavailable, record the exact failure in `progress.md` and use the narrowest check that can still run.
4. **One feature at a time:** Keep one feature active. Stay in scope: do not mix unrelated cleanup or refactors into the active feature.

Use `feature_list.json` only for concrete repository work, not as a permanent roadmap. Replace or remove completed placeholder-free entries as work changes.

## Definition of done

A feature is done only when its stated behavior is complete, meaningful tests were added or updated when behavior changed, `./init.sh` (or documented equivalent checks) ran, and verification evidence is recorded in both the feature entry and `progress.md`. Do not mark work done while required checks fail.

## End of session

Before ending a substantive session:

1. Update the active feature status and evidence in `feature_list.json`.
2. Update `progress.md` with what changed, verification results, blockers, and the next action.
3. For interrupted or multi-session work, update `session-handoff.md` with files changed and the exact restart step.
4. Leave no ambiguous `in-progress` item; there should be exactly one only when active work will resume.

## Development commands

TradingAgents is a Python package requiring Python 3.10 or newer. CI covers Python 3.10–3.13; the README and Docker image use Python 3.12.

```bash
# Editable development install
python -m pip install -e ".[dev]"

# Interactive CLI
tradingagents
python -m cli.main

# Full test suite (the CI command)
pytest -q

# One test file
pytest -q tests/test_reporting.py

# One test
pytest -q tests/test_api_key_env.py::test_ollama_has_no_key

# Marker selection
pytest -q -m unit
pytest -q -m integration

# Full-repository lint (the CI command)
ruff check .

# Clean-install/import smoke check used by CI
python -m pip install .
python -c "import tradingagents, cli.main; print('clean-install import OK')"
```

There is no configured type-checking command or standalone package-build command. Whole-repository `ruff format` adoption is intentionally deferred in `pyproject.toml`; do not introduce a mass-formatting diff.

The normal pytest suite is isolated with placeholder provider keys in `tests/conftest.py`. Real-provider structured-output checks are opt-in and require the corresponding configured credential:

```bash
python scripts/smoke_structured_output.py openai
python scripts/smoke_structured_output.py google
python scripts/smoke_structured_output.py anthropic
python scripts/smoke_structured_output.py deepseek
```

Optional Docker entry points:

```bash
cp .env.example .env
docker compose run --rm tradingagents
docker compose --profile ollama run --rm tradingagents-ollama
```

## Runtime architecture

The repository has two user-facing execution surfaces and no HTTP server:

- `tradingagents.graph.trading_graph.TradingAgentsGraph` is the reusable library composition root. `propagate(ticker, date, asset_type=...)` returns the final LangGraph state and a deterministic rating.
- `cli.main:app` is the Typer console entry point installed as `tradingagents`. The root `main.py` is only a hard-coded example, and root `test.py` is an ad-hoc yfinance benchmark rather than the pytest entry point.

`TradingAgentsGraph` creates the deep/quick provider clients, data tool nodes, decision memory, conditional routing, and compiled workflow. `tradingagents/graph/setup.py` is the authoritative graph topology, while `tradingagents/agents/utils/agent_states.py` is the shared state contract.

The graph runs the selected analysts serially. Each tool-calling analyst loops through its `ToolNode`, then clears the message history before the next analyst. The fixed tail is:

```text
selected analysts
  -> Bull/Bear research debate
  -> Research Manager
  -> Trader
  -> Aggressive/Conservative/Neutral risk debate
  -> Portfolio Manager
  -> END
```

The sentiment analyst is deliberately different: it pre-fetches Yahoo news, StockTwits, and Reddit context and uses structured output rather than a graph `ToolNode`. The internal analyst key remains `social` for saved configuration and caller compatibility even though the visible agent and state field are named Sentiment/`sentiment_report`.

The CLI does not call `TradingAgentsGraph.propagate()`. It resolves instrument context, creates initial state, streams `graph.graph` directly for Rich progress output, and manually merges per-node chunks. Changes to initial state, graph arguments, callbacks, or stream merging must keep both `TradingAgentsGraph._run_graph()` and the CLI path in `cli/main.py` aligned.

## Configuration and process state

- `tradingagents/default_config.py` is the configuration authority. Add environment-driven configuration through its `_ENV_OVERRIDES` map rather than adding entry-point-specific parsing.
- Importing `tradingagents` loads `.env` and `.env.enterprise` from the working directory without overriding already-exported values.
- Persistent defaults live under `~/.tradingagents/`; `TRADINGAGENTS_RESULTS_DIR`, `TRADINGAGENTS_CACHE_DIR`, and `TRADINGAGENTS_MEMORY_LOG_PATH` override them.
- `tradingagents/dataflows/config.py` stores process-global mutable data configuration. Constructing a graph installs its config globally, so graph instances with different configurations in one process are not isolated. Tests reset this state in `tests/conftest.py`.
- CLI configuration precedence is intentional: explicit `TRADINGAGENTS_*` values survive unless a corresponding CLI option explicitly overrides them. Preserve the logic in `_build_run_config()`.
- Every report-producing agent obtains its output-language instruction through `get_language_instruction()`; `tests/test_i18n_coverage.py` enforces coverage.

## LLM and structured-output layers

`tradingagents/llm_clients/factory.py` routes native Anthropic, Google, Azure, and optional Bedrock clients; other providers use the registry in `llm_clients/openai_client.py`. Model-specific behavior belongs in the declarative table in `llm_clients/capabilities.py`, not scattered model-name conditionals.

Adding a provider usually requires coordinated updates to the factory/registry, model catalog and validators, API-key mapping, CLI provider selection, and provider tests. Bedrock is an optional dependency installed with `pip install ".[bedrock]"`.

Decision agents use Pydantic schemas and render back to Markdown via `tradingagents/agents/schemas.py`. `agents/utils/structured.py` is the shared structured-output-with-plain-text-fallback seam. The rendered Markdown is part of the application contract: the deterministic rating parser, memory log, CLI, report writer, and external callers consume headings such as `**Rating**`, `**Recommendation**`, and `**Action**`. Do not casually rename these headings or the `AgentState` fields.

## Data and reporting layers

Agent-facing LangChain tools in `tradingagents/agents/utils/*_tools.py` delegate to `tradingagents/dataflows/interface.py`. That module owns category configuration, vendor registration, and fallback routing:

- Tool-level vendor settings override category-level settings.
- An explicit comma-separated vendor list is the exact fallback chain; the router does not add unselected vendors. `default` means all implementations available for that method.
- Core vendor failures remain observable. Optional macro and prediction-market failures degrade to explicit sentinels, and exhausted no-data chains return `NO_DATA_AVAILABLE` rather than prose that could invite fabricated values.

Preserve the data-integrity seams when changing providers or symbol handling:

- `dataflows/symbol_utils.py` is the canonical broker-to-Yahoo symbol normalizer; all yfinance paths must use it.
- `stockstats_utils.py` excludes rows after the analysis date, rejects stale data, and avoids caching empty downloads.
- `market_data_validator.py` supplies deterministic OHLCV/indicator snapshots for exact market claims.
- `dataflows/errors.py` defines vendor failure semantics used by the router.
- `safe_ticker_component()` must guard ticker-derived cache, checkpoint, result, and log paths.

`tradingagents/reporting.py` is the shared report-tree writer used by both CLI and programmatic callers. It writes numbered analyst/research/trading/risk/portfolio directories plus `complete_report.md`; keep both paths on this shared writer. Completed runs also append to the Markdown decision log, later resolve same-ticker outcomes for reflection, and optionally use per-ticker SQLite LangGraph checkpoints. Checkpoints resume only for the same ticker/date and are removed after successful completion.

## Tests and contracts

Tests are primarily mocked unit tests. Architectural regression coverage is organized around graph planning (`test_analyst_execution.py`), checkpoint resume, reporting parity, provider registries/capabilities, structured-output fallback, vendor routing, symbol normalization, market-date fidelity, no-data behavior, internationalization, and CLI configuration precedence.

When changing cross-cutting behavior, preserve these non-obvious contracts unless the task explicitly changes them:

- literal `AgentState` and nested debate-state keys;
- analyst execution order and the legacy `social` wire key;
- parity between CLI streaming and library propagation;
- deterministic rating extraction and rendered Markdown headings;
- shared numbered report layout;
- configured-vendor-only routing and typed failure behavior;
- symbol normalization, no-look-ahead filtering, stale-data rejection, and safe ticker paths.

LLM output and live news/social inputs are intentionally non-deterministic. A fixed ticker/date pins historical market windows but does not guarantee byte-identical reports. The project is a research framework, not a live order-execution service or financial-advice system.
