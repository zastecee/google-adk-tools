https://gemini.google.com/app/b994398abc337118
<!-- source .venv/bin/activate -->

# ADK Workshop — Getting Started

Welcome to the Vodacom AI Platform ADK hands-on workshop.

This folder is everything you need. Complete the setup steps below **before the session** — we won't have time to troubleshoot environments on the day.

---

## What you'll build

Over four modules you'll build a **Customer Segment Intelligence Agent** — a multi-agent pipeline that takes a CVM brief, queries customer data, runs Python analysis, and produces an interactive HTML dashboard.

| Module | What you build | Your task |
|--------|---------------|-----------|
| 02 | Your first ADK agent | Write the agent instruction |
| 03 | A tool that computes KPIs | Write the tool docstring and register it |
| 04 | Orchestrator + sub-agents | Build a summariser sub-agent from scratch and wire it in |
| 04_01 | Oracle + MCP + Python executor | Live demo — explore and experiment post-session |

Each module builds on the last. The wiring is done for you — your job is to fill in the three things that actually make agents work: **tool docstrings**, **tool registration**, and **agent instructions**.

---

## Setup (do this before the session)

### 1. Prerequisites

- Python 3.11 or higher — check with `python --version`
- AWS credentials configured with access to Bedrock (`eu-west-1`)
- `uv` installed — [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)

### 2. Open a terminal in this folder

You're already in the right place — this README is inside the workshop folder. Open a terminal and navigate to wherever you extracted it:

```bash
cd path/to/workshop
```

### 3. Install dependencies

```bash
uv sync
```

### 4. Configure your environment

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Open `.env` and fill in all values:

- `AWS_REGION` — the AWS region your Bedrock model is deployed in
- `AWS_PROFILE` — your AWS CLI profile name (run `aws configure list-profiles` to check)
- `BEDROCK_MODEL_ID` — your Bedrock model or inference profile ARN
- `ORACLE_*` — Oracle credentials for Module 04_01 only (skip if you're not doing that module)

### 5. Run the setup check

```bash
uv run python setup_check.py
```

You should see all checks passing including a live Bedrock API call:

```
✓ Python 3.13.x
✓ All packages installed
✓ .env loaded — BEDROCK_MODEL_ID set
✓ Bedrock API call succeeded
────────────────────────────────
✓ All checks passed. You're ready.
```

If anything fails, contact the trainer before the session day.

---

## Running each module

Each module is a self-contained ADK project. Run from inside the module directory:

```bash
cd module_02
uv run adk web        # opens the dev UI at http://localhost:8000
```

The `adk web` UI lets you chat with your agent, see every tool call, and inspect the full conversation trace. Use it to test and iterate.

To stop the server: `Ctrl+C`

---

## Module guide

### Module 02 — Your first agent

**File to edit:** `module_02/first_agent/agent.py`

Your only task is to write the `instruction` string. There are no tools in this module — that comes in Module 03.

Try it twice:
1. Write a vague instruction (`"You are a helpful assistant."`) and run it. Ask "Who are you?" and "What do you know about our prepaid segment?" Notice how it behaves — does it stay on topic? Does it make things up?
2. Rewrite it to define the agent's role, scope what it can and can't do, and give it explicit guidance for when it has no data. Run it again. What changed?

This is the core lesson: **the instruction is a prompt. Specificity changes behaviour.**

```bash
cd module_02
uv run adk web
```

---

### Module 03 — Tools

**Files to edit:** `module_03/kpi_agent/tools.py` and `module_03/kpi_agent/agent.py`

`query_customer_data()` is complete — use it as a reference. Your two tasks:
1. Write the **docstring** for `calculate_kpis()` in `tools.py`
2. Uncomment the import and add `calculate_kpis` to `tools=[]` in `agent.py`

The docstring is not documentation — it's instructions to the agent. The agent reads it to decide when to call the tool and what to pass in.

Try it both ways:
1. Run `adk web` without completing either task. Ask for KPIs. Notice that the agent fetches the raw records but then calculates the numbers itself — and gets them wrong.
2. Complete both tasks. Run again and ask the same question. The agent now calls the tool and returns exact, correct numbers.

```bash
cd module_03
uv run adk web
```

Ask: `"What were the KPIs for high_value_prepaid in March 2025?"`

---

### Module 04 — Multi-agent pipeline

**Files to edit:**
- `module_04/pipeline_agent/sub_agents/summariser/agent.py` — write the instruction
- `module_04/pipeline_agent/agent.py` — import the summariser and update the orchestrator instruction

The `data_analyst` sub-agent and all 4 tools are pre-built. Both sub-agents are imported — your job is to wire them into `sub_agents`, write the summariser instruction, and update the orchestrator to delegate to both.

```bash
cd module_04
uv run adk web
```

**Your task — Add the summariser sub-agent**

The pipeline currently produces a dashboard. Your job is to add a `summariser` sub-agent that takes the analyst's findings and produces a 3-bullet executive summary for a non-technical CVM manager.

Step 1 — Open `sub_agents/summariser/agent.py`. The skeleton is already there — your job is to write the `instruction`. It has no tools — it only reasons over the findings passed to it. Write an instruction that produces exactly 3 bullets:
- Bullet 1: the most important finding (lead with the number)
- Bullet 2: the key supporting metric
- Bullet 3: a specific recommended action

Step 2 — Open `agent.py`. Import the summariser and add it to `sub_agents`. Then update the orchestrator instruction to pass the analyst's findings to the summariser and return both the dashboard path and the executive summary.

Ask: `"Summarise how high-value prepaid customers performed in March 2025."`

You should get a dashboard path and a 3-bullet executive summary.

A dashboard HTML file will be saved to `output/`.

---

### Module 04_01 — Oracle, MCP & Python executor

> **This module is a live demo — no exercise.** The agents are pre-built. Follow along, explore the ADK trace, and try the queries yourself after the session.

> **Before running:** Make sure your Oracle credentials are set in `.env`, then load the customer data into your Oracle instance:
> ```bash
> uv run python load_data.py
> ```
> This creates and populates the `customers` table. You only need to do this once.

This module replaces the CSV data with a real Oracle database accessed via MCP. The analytics agent queries Oracle and runs pandas analysis via `execute_python`. The reporting agent writes a complete HTML/Chart.js dashboard from scratch — all driven by the instruction, no hardcoded rendering logic.

```bash
cd module_04_01
uv run adk web
```

Try these during or after the demo:

- `"Analyse high_value_prepaid customers for March 2025 and produce a dashboard."`
- `"What's the correlation between top-up frequency and churn for high_value_prepaid?"`
- `"Compare churn across all three segments for 2025-03."`

---

## Dataset

All modules use the same customer dataset (`data/customers.csv`):

| Column | Description |
|--------|-------------|
| `customer_id` | Unique customer ID |
| `segment` | `high_value_prepaid` / `mid_value_prepaid` / `low_value_prepaid` |
| `month` | `2025-02` or `2025-03` |
| `top_up_count` | Number of top-ups in the month |
| `top_up_amount` | Total top-up spend (ZAR) |
| `data_usage_mb` | Total data consumed (MB) |
| `churn_flag` | `1` = churned, `0` = retained |

---

## Troubleshooting

**Agent never calls the tool**
The docstring is missing or too vague. Add a clear description of when to call the tool and what to pass in.

**Orchestrator doesn't delegate**
The instruction doesn't tell it to use the sub-agent. Make delegation explicit.

**`adk web` says port already in use**
Another server is running. Kill it: `lsof -i :8000` then `kill -9 <PID>`

**Bedrock AuthenticationError**
Your AWS credentials aren't configured or have expired. Run `aws sts get-caller-identity` to check.

**Wrong model ID**
Check `BEDROCK_MODEL_ID` in your `.env` — use the exact ARN or model ID string. A wrong model ID causes silent failures.

**Oracle connection error (module_04_01)**
Check `ORACLE_CONNECTION_STRING`, `ORACLE_USERNAME`, and `ORACLE_PASSWORD` in your `.env`.
