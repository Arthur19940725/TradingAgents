---
name: tradingagents
description: "Work on the TradingAgents repository and package: run or explain the CLI, configure LLM/data providers, debug ticker/data/vendor behavior, maintain LangGraph agent flows, checkpoint resume, report output, tests, and release notes. Use when the user asks about this repo's code, TradingAgentsGraph, tradingagents CLI, TRADINGAGENTS_* settings, market-data validation, multi-provider LLM routing, or safe financial-analysis run setup."
---

# TradingAgents

## Operating Rule

Treat TradingAgents as a research framework, not financial advice. Preserve exact ticker identity, dates, data sources, and provider configuration when running or changing the project.

## First Checks

1. Confirm the working directory is the TradingAgents repository.
2. Read `CLAUDE.md`, `feature_list.json`, and `progress.md` before editing; they define the active scope and restart state.
3. Read `README.md`, `pyproject.toml`, and the directly relevant files before editing.
4. Check `git status --short --branch` and preserve user changes.
5. Before production-code changes, run `./init.sh` for a baseline. If the environment blocks it, record the exact failure and use the narrowest meaningful check instead.
6. Keep exactly one repository feature active. Do not mix unrelated cleanup or refactors into the requested change.
7. For runtime or data questions, identify the entry point first:
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
3. If a change touches graph inputs, callbacks, initial state, or stream merging, compare the CLI path in `cli/main.py` with `TradingAgentsGraph._run_graph()` and preserve their behavior parity.
4. Preserve compatibility contracts: literal `AgentState` and debate-state keys, Markdown headings such as `**Rating**`, `**Recommendation**`, and `**Action**`, and the shared numbered report layout.
5. Add or update focused tests for config precedence, provider routing, ticker identity, stale-data guards, checkpoints, or CLI behavior when touched.
6. Update `CHANGELOG.md` only for user-visible release notes or when the user requests it.
7. Keep reports and generated runtime output out of source changes unless explicitly requested.

## Verification

Read `pyproject.toml` before choosing commands. Prefer focused tests first, then broader checks if the change affects shared behavior. For a substantive coding task, finish by updating the active entry in `feature_list.json` and `progress.md` with the exact checks and results; update `session-handoff.md` when work will continue in another session.

Typical checks:

```powershell
python -m pytest -q tests/test_symbol_utils.py tests/test_ticker_symbol_handling.py
python -m pytest -q tests/test_cli_config_precedence.py tests/test_env_overrides.py
python -m pytest -q tests/test_provider_registry.py tests/test_vendor_routing.py
python -m ruff check .
python -c "import tradingagents, cli.main; print('clean-install import OK')"
```

For repository-local skill maintenance, run `python skills/tradingagents/scripts/validate_skill.py` to verify frontmatter, lifecycle references, eval shape, and current CLI syntax.

If dependencies, lockfiles, security-sensitive config, or provider auth handling changes, run the ecosystem-appropriate non-mutating audit when available and report the result.

## Response Contract

For every substantive diagnosis or code change, report the result first, then:

- files inspected and changed;
- verification commands and their outcomes;
- skipped checks and the reason (especially missing dependencies or credentials);
- blockers and remaining uncertainty.

Distinguish facts confirmed from source/tests, assumptions, and live-provider observations. Do not present an unverified market value, provider capability, or successful test run as fact.

## References

Read [maintenance-map.md](references/maintenance-map.md) when the task touches multiple subsystems, release notes, provider/data routing, or verification selection.
