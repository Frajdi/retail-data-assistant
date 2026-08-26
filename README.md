# Retail Data Assistant

A CLI-based data analysis agent for retail executives built with LangGraph, LangChain, BigQuery, and LLM tool calling.

The assistant allows non-technical users to ask natural-language questions about retail data, perform multi-step analysis, investigate trends, and generate executive reports with evidence-based action items.

The prototype includes:

- Natural-language data analysis
- Dynamic BigQuery SQL generation
- Multi-step analytical reasoning
- Conversational memory
- Query self-correction and bounded retries
- Read-only SQL enforcement using SQLGlot
- PII-aware result masking
- Executive report generation
- LangSmith observability and tracing
- CLI-based interaction

---

## Project Structure

```text
src/
├── agent/
│   ├── graph.py
│   ├── prompts.py
│   ├── state.py
│   └── tools/
│       ├── query_tool.py
│       ├── schema_tool.py
│       └── think_tool.py
│
├── domain/
│   ├── data_policy.py
│   ├── errors.py
│   ├── query_models.py
│   └── sql_policy.py
│
└── infrastructure/
    └── big_query.py

main.py
pyproject.toml
uv.lock
.env.example
```

## High-Level Architecture

![Retail Data Assistant Architecture](docs/architecture.svg)

## Requirements

Before running the project, make sure you have:

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Google Cloud CLI (`gcloud`)
- Access to a Google Cloud project with BigQuery enabled
- An OpenAI API key
- Optionally, a Google Gemini API key
- Optionally, a LangSmith account for tracing and observability

---

## 1. Clone the Repository

```bash
git clone <REPOSITORY_URL>
cd agent-assignment
```

---

## 2. Install Dependencies

This project uses `uv` for dependency and virtual environment management.

Install `uv` if it is not already available:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install the project dependencies:

```bash
uv sync
```

`uv` will create the local `.venv` automatically.

---

## 3. Configure Environment Variables

Create a local `.env` file from the provided example:

```bash
cp .env.example .env
```

The expected environment variables are:

```env
GOOGLE_API_KEY=
OPENAI_API_KEY=

LANGSMITH_TRACING=
LANGSMITH_ENDPOINT=
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=
```

### OpenAI

Add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key
```

The current implementation uses an OpenAI model by default.

### Google Gemini

If using the Gemini configuration instead, provide a Google API key:

```env
GOOGLE_API_KEY=your_google_api_key
```

---

## 4. Configure Google Cloud and BigQuery

The prototype queries Google's public BigQuery dataset:

```text
bigquery-public-data.thelook_ecommerce
```

Your own Google Cloud project is used for authentication, quota, and query execution.

### Authenticate with Google Cloud

Log in to Google Cloud:

```bash
gcloud auth login
```

Then configure Application Default Credentials:

```bash
gcloud auth application-default login
```

These credentials are automatically discovered by the Google Cloud Python SDK.

### Select a Google Cloud Project

List your available projects:

```bash
gcloud projects list
```

Select the project you want to use:

```bash
gcloud config set project YOUR_PROJECT_ID
```

### Configure the ADC Quota Project

Configure the selected project as the quota project for Application Default Credentials:

```bash
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

### Enable BigQuery

Make sure the BigQuery API is enabled:

```bash
gcloud services enable bigquery.googleapis.com \
  --project=YOUR_PROJECT_ID
```

Verify the active project:

```bash
gcloud config get-value project
```

---

## 5. Configure LangSmith Observability

LangSmith can be used to inspect and debug the agent's execution, including:

- LangGraph runs
- LLM calls
- Tool calls
- Generated SQL queries
- Tool results
- Token usage
- Latency
- Query recovery flows
- Errors and failures

### Create a LangSmith Project

1. Sign in to LangSmith.
2. Create a new project for the application.
3. Create a LangSmith API key.
4. Copy the API key and project name into your `.env` file.

Configure the following variables:

```env
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=your_project_name
```

For example:

```env
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=lsv2_xxxxxxxxxxxxxxxxx
LANGSMITH_PROJECT=retail-data-assistant
```

After running the application and submitting a query, the corresponding agent trace should appear inside the configured LangSmith project.

---

## 6. Run the Assistant

Start the CLI:

```bash
uv run main.py
```

You should see:

```text
Retail Data Assistant
You:
```

You can now ask questions about the retail dataset using natural language.

---

## Example Queries

### Revenue Analysis

```text
Show me monthly revenue for the last 6 complete months and tell me which month performed worst.
```

You can then ask a contextual follow-up:

```text
Why did that month perform worse? Investigate whether it was driven more by fewer orders, fewer items sold, or lower average selling prices.
```

### Customer Analysis

```text
Which 5 states have the highest number of customers, and how does their average spending compare?
```

### Product Analysis

```text
Find the 5 products generating the most revenue. Compare their sales volume and average selling price and explain what appears to drive their performance.
```

### Executive Report

```text
Create an executive report for Q1 2025. Include revenue performance, order volume, customer behavior, top-performing products, notable trends or anomalies, and 3 evidence-based action items for Q2.
```

### Privacy Protection

```text
Who are the top 5 customers by total spending? Show their email, state, number of orders, and total spend.
```

Sensitive fields such as customer email addresses are masked before query results are exposed to the LLM.

---

## Safety and PII Handling

The application enforces data-access restrictions at the tool and domain layers rather than relying exclusively on LLM instructions.

### Read-Only SQL Enforcement

Generated SQL is parsed using SQLGlot before execution.

Only read-only `SELECT` statements are allowed.

Mutation statements such as:

```sql
INSERT
UPDATE
DELETE
DROP
ALTER
```

are rejected before reaching BigQuery.

### Metadata-Driven Data Policies

Dataset fields can be assigned exposure policies such as:

```text
ALLOW
MASK
DROP
```

Sensitive columns can still participate in legitimate analytical operations while their raw values remain protected.

For example:

```sql
SELECT COUNT(DISTINCT email)
FROM users;
```

can return the aggregate count without exposing individual email addresses.

Direct selection:

```sql
SELECT email
FROM users
LIMIT 5;
```

returns masked values instead.

### SQL Lineage

The policy layer analyzes the source columns contributing to query outputs.

This prevents simple aliases from bypassing field policies.

For example:

```sql
SELECT email AS customer_contact
FROM users;
```

still inherits the exposure policy configured for `users.email`.

---

## Query Recovery

Query execution returns structured success or failure results to the LangGraph workflow.

The agent distinguishes between recoverable and non-recoverable failures.

Recoverable cases include:

- Empty query results
- Invalid SQL
- Read-only policy violations

For recoverable failures, the model can investigate the problem and attempt a corrected analytical path.

Retries are bounded to prevent uncontrolled loops and unnecessary LLM or BigQuery usage.

For example, an empty result may cause the agent to investigate:

- Incorrect categorical values
- Abbreviations
- Date ranges
- Join assumptions
- Overly restrictive filters

before reformulating the original analysis.

---

## Conversational Analysis

The application uses a LangGraph checkpointer to maintain conversation state across turns.

This allows contextual follow-up questions such as:

```text
Show me monthly revenue for the last 6 complete months and tell me which month performed worst.
```

followed by:

```text
Why did that month perform worse?
```

The agent can continue the analysis using the context established during the previous turn.

The current prototype uses an in-memory checkpointer. A production deployment could replace this with persistent storage.

---

## Environment Example

The repository includes an `.env.example` containing:

```env
GOOGLE_API_KEY=
OPENAI_API_KEY=

LANGSMITH_TRACING=
LANGSMITH_ENDPOINT=
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=
```

Copy it before running the application:

```bash
cp .env.example .env
```

Never commit real API keys or credentials to the repository.

---

## Quick Start

```bash
git clone <REPOSITORY_URL>
cd agent-assignment

uv sync

cp .env.example .env
# Add the required API keys to .env

gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default set-quota-project YOUR_PROJECT_ID

uv run main.py
```

Then try:

```text
Create an executive report for Q1 2025 with insights and action items for Q2.
```