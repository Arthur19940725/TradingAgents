# TradingAgents Maintenance Map

## Repository Sources

- `README.md`: installation, CLI use, required API keys, markets and tickers, programmatic usage, persistence, checkpoint resume, reproducibility, and project disclaimer.
- `pyproject.toml`: package metadata, Python version, dependencies, optional Bedrock extra, CLI entry point, pytest defaults, and Ruff rules.
- `.github/workflows/ci.yml`: CI import and test expectations.
- `CHANGELOG.md`: release-facing behavior changes and regression history.

## Core Modules

- `tradingagents/default_config.py`: default runtime config and `TRADINGAGENTS_*` environment overrides.
- `cli/main.py`: Typer CLI command, interactive analysis flow, report saving, checkpoint flags, and Rich live display.
- `cli/utils.py`: ticker input, asset detection, provider/model selection, API-key checks, and backend URL resolution.
- `tradingagents/graph/trading_graph.py`: `TradingAgentsGraph`, LLM initialization, LangGraph compilation, checkpoint resume, memory-log resolution, report saving, and signal processing.
- `tradingagents/graph/checkpointer.py`: checkpoint storage, thread IDs, and clear behavior.
- `tradingagents/graph/analyst_execution.py`: analyst ordering and wall-time tracking.
- `tradingagents/reporting.py`: markdown report tree generation shared by CLI and programmatic API.
- `tradingagents/llm_clients/`: provider registry, model catalog, provider-specific clients, capabilities, validators, and API-key env mapping.
- `tradingagents/dataflows/`: vendor routing, symbol normalization, stale-data guards, market snapshots, macro/news/fundamental data tools, and safe filesystem ticker components.
- `tradingagents/agents/`: analyst, researcher, trader, risk, and manager prompts plus structured-output schemas.

## Test Routing

- CLI/config: `tests/test_cli_config_precedence.py`, `tests/test_env_overrides.py`, `tests/test_cli_symbol_handling.py`, `tests/test_cli_no_console.py`
- Symbols and path safety: `tests/test_symbol_utils.py`, `tests/test_ticker_symbol_handling.py`, `tests/test_safe_ticker_component.py`, `tests/test_symbol_normalization_paths.py`
- Market data and vendors: `tests/test_market_data_validator.py`, `tests/test_vendor_routing.py`, `tests/test_vendor_errors.py`, `tests/test_yfinance_stale_ohlcv_guard.py`, `tests/test_alpha_vantage_hardening.py`
- LLM providers: `tests/test_provider_registry.py`, `tests/test_model_validation.py`, `tests/test_openai_compatible_provider.py`, `tests/test_openai_responses_base_url.py`, `tests/test_google_api_key.py`, `tests/test_bedrock_provider.py`, `tests/test_temperature_config.py`, `tests/test_llm_max_retries.py`
- Graph behavior: `tests/test_checkpoint_resume.py`, `tests/test_analyst_execution.py`, `tests/test_signal_processing.py`, `tests/test_structured_agents.py`, `tests/test_structured_agent_prompts.py`
- Reporting and memory: `tests/test_reporting.py`, `tests/test_memory_log.py`

## Common Failure Boundaries

- Missing API key: use the provider's documented environment variable; do not prompt for or store secrets in code.
- No market data: preserve the repo's explicit unavailable-data path and test with the relevant vendor/symbol tests.
- Ticker ambiguity: resolve through `normalize_symbol`, `normalize_ticker_symbol`, and instrument-context helpers rather than rewriting inside prompts.
- Checkpoint behavior: include ticker, date, analyst selection, debate depth, risk depth, and asset type in reasoning about resume compatibility.
- Runtime output: logs, caches, reports, and memory live under `~/.tradingagents` by default unless overridden.
