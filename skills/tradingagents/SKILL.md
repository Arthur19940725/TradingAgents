---
name: tradingagents
description: "Work on the TradingAgents repository and package: run or explain the CLI, configure LLM/data providers, debug ticker/data/vendor behavior, maintain LangGraph agent flows, checkpoint resume, report output, tests, and release notes. Use when the user asks about this repo's code, TradingAgentsGraph, tradingagents CLI, TRADINGAGENTS_* settings, market-data validation, multi-provider LLM routing, or safe financial-analysis run setup."
---

# TradingAgents

## Operating Rule

Treat TradingAgents as a research framework, not financial advice. Preserve exact ticker identity, dates, data sources, and provider configuration when running or changing the project.

## First Checks

1. Confirm the working directory is the TradingAgents repository.
2. Read `README.md`, `pyproject.toml`, and the directly relevant files before editing.
3. Check `git status --short --branch` and preserve user changes.
4. For runtime or data questions, identify the entry point first:
   - CLI: `cli/main.py`, `cli/utils.py`
   - Programmatic API: `tradingagents/graph/trading_graph.py`
   - Defaults/env: `tradingagents/default_config.py`
   - Data routing: `tradingagents/dataflows/interface.py`, `tradingagents/dataflows/config.py`
   - Symbol safety: `tradingagents/dataflows/symbol_utils.py`, `tradingagents/dataflows/utils.py`
   - Provider clients: `tradingagents/llm_clients/`

## Run Workflow

Before a live analysis, confirm the ticker, analysis date, asset type, provider and models,
output language, expected API/data costs, and allowed output locations. Live runs can call
external LLM and market-data services and persist reports, caches, checkpoints, and a decision
memory log; do not start one from an ambiguous request.

Use Python 3.10-3.13, matching the repository CI matrix. Verify the selected interpreter and
installed dependencies before treating a runtime failure as a code defect. Use the narrowest
command that matches the task:

```powershell
python -m cli.main
tradingagents
tradingagents --checkpoint
python -m pytest -q tests/test_symbol_utils.py
python -m pytest -q tests/test_market_data_validator.py
python -m ruff check .
```

The CLI is interactive and needs a real Windows Terminal, PowerShell, or `cmd.exe` console.
Do not work around a missing console by launching a credentialed analysis through another entry
point unless the user authorized that run.

For programmatic analysis, use `TradingAgentsGraph` with a copied config:

```python
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph

config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"
config["deep_think_llm"] = "gpt-5.5"
config["quick_think_llm"] = "gpt-5.4-mini"

ta = TradingAgentsGraph(debug=True, config=config)
state, decision = ta.propagate("NVDA", "2026-01-15")
ta.save_reports(state, "NVDA")
```

## Configuration Discipline

- Prefer `DEFAULT_CONFIG.copy()` before changing run settings.
- Use `TRADINGAGENTS_*` environment variables for unattended runs when the repo already exposes one.
- Do not read, echo, hardcode, or commit API keys. Let the user control credential entry and use
  the established environment or `.env` mechanism without exposing its values.
- Keep `backend_url` provider-specific. Avoid carrying one provider's URL into another provider.
- Treat `checkpoint_enabled`, debate round counts, and vendor routing as deterministic config, not model judgment.
- For local or OpenAI-compatible endpoints, preserve the explicit `openai_compatible` provider path.

## Persistence And Recovery

- Expect completed runs to append to the decision memory log. By default, runtime logs, cache,
  checkpoints, and memory live under `~/.tradingagents`; read `DEFAULT_CONFIG` and active
  `TRADINGAGENTS_*` overrides before reporting an exact path.
- Enable `--checkpoint` only when resume state is wanted. Preserve the ticker, date, analyst
  selection, debate/risk depth, and asset type when diagnosing compatibility.
- Treat `--clear-checkpoints` as deletion: resolve the active cache directory, show the exact
  target and checkpoint count when possible, and require explicit user authorization before
  running `tradingagents --clear-checkpoints` or calling the clear helper.

## Market Data And Tickers

- Preserve exchange-qualified tickers such as `0700.HK`, `7203.T`, `RELIANCE.NS`, and crypto symbols such as `BTC-USD`.
- Use the repository normalization path instead of ad hoc ticker rewriting.
- If market data is missing, stale, or contradictory, fail loudly and report unavailability. Do not fabricate prices, indicators, fundamentals, or news.
- For time-sensitive market requests, browse or fetch fresh data and state the source, timestamp, currency, and instrument identity.
- Do not map ADRs, local listings, CFDs, futures, or crypto pairs to each other without an explicit ratio or symbol-normalization rule.

## Change Workflow

1. Search existing tests before changing behavior.
2. Make the smallest change in the nearest active module.
3. Add or update focused tests for config precedence, provider routing, ticker identity, stale-data guards, checkpoints, or CLI behavior when touched.
4. Update `CHANGELOG.md` only for user-visible release notes or when the user requests it.
5. Keep reports and generated runtime output out of source changes unless explicitly requested.

## Verification

Read `pyproject.toml` before choosing commands. Prefer focused tests first, then broader checks if the change affects shared behavior.

Typical checks:

```powershell
python -m pytest -q tests/test_symbol_utils.py tests/test_ticker_symbol_handling.py
python -m pytest -q tests/test_cli_config_precedence.py tests/test_env_overrides.py
python -m pytest -q tests/test_provider_registry.py tests/test_vendor_routing.py
python -m ruff check .
python -c "import tradingagents, cli.main; print('clean-install import OK')"
```

If dependencies, lockfiles, security-sensitive config, or provider auth handling changes, run the ecosystem-appropriate non-mutating audit when available and report the result.

## References

Read [maintenance-map.md](references/maintenance-map.md) when the task touches multiple subsystems, release notes, provider/data routing, or verification selection.
