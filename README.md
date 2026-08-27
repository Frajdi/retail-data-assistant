# Retail Data Analysis Assistant

> A conversational data analysis agent for retail executives, capable of dynamically analyzing BigQuery data, answering multi-step business questions, and generating evidence-based reports and action items.

This project implements a conversational data analysis assistant designed for non-technical retail executives, such as Store and Regional Managers. It allows users to ask business questions in natural language, investigate retail performance through multi-step analysis, and generate evidence-based reports and actionable recommendations from BigQuery data.

The prototype is built with LangGraph and supports dynamic SQL generation, multi-turn conversations, PII protection, resilient query execution, evaluation Pipeline, and end-to-end observability. While the prototype implements the core analytical workflow and selected production capabilities, the accompanying High-Level Design (HLD) describes how the system can be extended into a production-ready platform with historical analyst knowledge, persistent user preferences, saved reports, configurable personas, and additional capabilities such as charts, email delivery, and external data sources.

## Table of Contents

- [1. Key Capabilities](#1-key-capabilities)
- [2. High-Level Architecture](#2-high-level-architecture)
  - [2.1 Production Architecture](#21-production-architecture)
- [3. Architecture Components](#3-architecture-components)
- [4. Requirement-by-Requirement Design](#4-requirement-by-requirement-design)
  - [4.1 Hybrid Intelligence — Golden Knowledge](#41-hybrid-intelligence--golden-knowledge)
  - [4.2 Safety & PII Masking](#42-safety--pii-masking)
  - [4.3 High-Stakes Oversight — Destructive Operations](#43-high-stakes-oversight--destructive-operations)
  - [4.4 Continuous Improvement](#44-continuous-improvement)
  - [4.5 Quality Assurance](#45-quality-assurance)
  - [4.6 Observability](#46-observability)
  - [4.7 Agility — Persona Management](#47-agility--persona-management)
- [5. Agent Execution, State & Data Flow](#5-agent-execution-state--data-flow)
- [6. Error Handling & Fallback Strategy](#6-error-handling--fallback-strategy)
- [7. Technology Choices](#7-technology-choices)
- [8. Setup Instructions](#8-setup-instructions)
  - [8.1 Clone the Repository](#81-clone-the-repository)
  - [8.2 Install Dependencies](#82-install-dependencies)
  - [8.3 Environment Variables](#83-environment-variables)
  - [8.4 Google Cloud / BigQuery Authentication](#84-google-cloud--bigquery-authentication)
  - [8.5 Run the Agent](#85-run-the-agent)
  - [8.6 Run Evaluations](#86-run-evaluations)
- [9. Example Usage](#9-example-usage)
  - [9.1 Simple Analysis](#91-simple-analysis)
  - [9.2 Multi-Step Executive Report](#92-multi-step-executive-report)
- [10. Future Extensions](#10-future-extensions)
- [11. Limitations](#11-limitations)


## 1. Key Capabilities

The prototype implements the core analytical workflow required for a retail data assistant:

- **Natural-language retail analytics** — users can ask business questions without writing SQL.
- **Dynamic BigQuery analysis** — the agent generates and executes analytical SQL against the provided retail dataset.
- **Database schema discovery** — the agent can inspect table schemas before constructing queries.
- **Multi-step analysis** — complex questions can be decomposed into multiple queries and synthesized into a single answer.
- **Multi-turn conversations** — conversation state is preserved through LangGraph threads, allowing follow-up questions.
- **Executive report generation** — the agent can produce structured reports containing metrics, trends, anomalies, and business insights.
- **Evidence-based action items** — recommendations are derived from retrieved data rather than unsupported assumptions.
- **Read-only SQL enforcement** — generated queries are validated against a deterministic read-only policy before execution.
- **PII protection** — sensitive fields returned from the database are masked before they can reach the model or final response.
- **Query recovery** — invalid SQL and empty-result scenarios are detected and returned to the agent with structured feedback for correction.
- **Bounded retries and graceful failure** — recoverable failures are retried within defined limits, while unrecoverable failures terminate safely without crashing the CLI.
- **Evaluation and observability** — LangSmith provides execution tracing, while a golden evaluation dataset measures agent behavior and final-response correctness.

### Prototype Requirements Implemented

The assignment requires the prototype to implement at least two production requirements. This prototype implements four:

| Requirement | Implemented |
|---|:---:|
| Safety & PII Masking | ✅ |
| Resilience & Graceful Error Handling | ✅ |
| Quality Assurance | ✅ |
| Observability | ✅ |

<br>  
<br>  
<br>  
<br>  

# 2. High-Level Architecture

The following diagram represents the architecture implemented by the prototype and the core orchestration model intended for the production system.

The architecture is intentionally tool-driven and extensible. Additional capabilities such as Golden Knowledge retrieval, saved-report management, chart generation, email delivery, and external data sources can be introduced as additional tools or services without changing the core agent execution flow.

![High-Level Architecture](docs/agent_diagram.svg)

[Open full-size architecture diagram](docs/agent_diagram.svg)

## 2.1 Production Architecture

The prototype implements the core analytical orchestration shown above. In production, the same architecture can be extended with supporting services required for historical knowledge retrieval, persistent user preferences, saved reports, runtime persona management, durable conversation state, and other production concerns.

The main production components are:

- **Application Layer** — CLI in the prototype, with an API/UI as the production entry point.
- **LangGraph Agent** — orchestrates model calls, tool execution, conversation state, and recovery flows.
- **LLM Provider** — performs analytical planning, SQL generation, and response synthesis.
- **BigQuery** — provides read-only access to retail transaction and catalog data.
- **Golden Knowledge Store** — provides relevant historical Question → SQL → Analyst Report examples at query time.
- **Saved Reports Store** — persists generated reports and supports ownership-aware, confirmed destructive operations.
- **User Preference Store** — persists presentation and analysis preferences across conversations.
- **Persona Configuration Store** — allows non-developers to modify report tone and presentation instructions without redeployment.
- **Persistent Checkpointer** — maintains durable conversation state across sessions and application restarts.
- **LangSmith** — provides tracing, debugging, evaluation, latency, token usage, and cost visibility.

The production-only components above extend the agent primarily through additional tools, runtime context, and external services rather than requiring changes to the core orchestration model. Their individual data flows, storage strategies, safety boundaries, and failure-handling behavior are described in the requirement-specific sections below.


<br>
<br>
<br>
<br>

# 3. Architecture Components

| Component | Technology / Service | Responsibility | Status |
|---|---|---|---|
| Agent Orchestrator | LangGraph | Agent state, tool orchestration, multi-turn execution and recovery flow | Prototype |
| LLM | Gemini | Analytical planning, SQL generation and response synthesis | Prototype |
| Analytical Database | Google BigQuery | Read-only access to retail transaction and catalog data | Prototype |
| SQL Safety & PII Protection | SQLGlot + Execution Layer | Parses generated SQL, enforces SELECT-only access, detects sensitive fields, and prevents PII from reaching the LLM | Prototype |
| Conversation State | LangGraph InMemorySaver | Maintains multi-turn conversation state by thread ID for the lifetime of the running application | Prototype |
| Observability | LangSmith | Tracing, debugging, latency, token usage and cost analysis | Prototype |
| Evaluation | LangSmith | Golden-dataset regression testing and automated agent evaluation | Prototype |
| Golden Knowledge | Vector Store + Object Storage | Stores and retrieves relevant historical Question → SQL → Analyst Report examples | Production Design |
| Saved Reports | PostgreSQL / Object Storage | Persists generated reports, ownership metadata and deletion state | Production Design |
| User Preferences | PostgreSQL | Stores persistent user-level presentation and analysis preferences | Production Design |
| Persona Configuration | PostgreSQL | Stores runtime-editable agent/reporting instructions without redeployment | Production Design |


<br>
<br>
<br>
<br>

# 4. Requirement-by-Requirement Design
<br>
<br>

## 4.1 Hybrid Intelligence — Golden Knowledge

### Problem

BigQuery provides the factual source of truth for current retail data, but raw transaction data alone does not capture how experienced analysts interpret business questions.

The Golden Knowledge store preserves historical analyst-approved analytical patterns based on the assignment's:

**Question → SQL Query → Analyst Report**

For simple questions, a single SQL query may be sufficient. However, complex business questions and executive reports often require multiple queries to establish the evidence needed for a conclusion. Therefore, in the production design, a Golden Knowledge entry is treated more generally as:

**Question → Analytical Query Set → Analyst Report**

For example, a quarterly executive report may require separate queries for revenue performance, order volume, customer behavior, product performance, returns, and historical comparisons.

These entries provide analytical precedent: how similar questions were interpreted, which metrics were considered relevant, which queries were necessary to establish those metrics, and how the resulting evidence was communicated to executives.

Golden Knowledge guides the analytical approach but is not a source of current business facts. Historical query results and report conclusions may be outdated, so current metrics and claims must always be established by executing queries against the current BigQuery data.

<br>
<br>

### Query-Time Retrieval

When a user submits a question, the system performs semantic retrieval against the Golden Knowledge index before beginning the current analysis.

The query-time flow is:

User Question  
↓  
Semantic Retrieval  
↓  
Relevant Historical Analytical Examples  
↓  
Agent Context  
↓  
Reuse / Adapt Analytical Query Set  
↓  
Current BigQuery Execution  
↓  
Final Response

The user's question is embedded and compared against indexed historical questions. The most relevant approved entries are retrieved and provided to the agent as additional context.

The retrieved knowledge provides more than reporting style or historical interpretation. It can significantly reduce the discovery work normally required by an analytical agent.

Without relevant Golden Knowledge, the agent may need to inspect schemas, discover categorical values, determine relationships, test assumptions, execute exploratory queries, and progressively determine which metrics are required.

When a strong historical match exists, the agent already receives an analyst-approved analytical approach and the SQL queries that were previously required to answer a similar question.

For example:

Current Question  
↓  
Retrieve Similar Golden Entry  
↓  
Reuse / Adapt Relevant Queries  
↓  
Execute Against Current BigQuery Data  
↓  
Synthesize Current Results  
↓  
Generate Report

The agent can execute a historical query directly when it remains applicable or make small modifications when the new question differs in dimensions such as date range, region, product, or customer segment.

For complex reports, the retrieved entry may contain several analytical queries. Independent queries can be executed in parallel where appropriate, allowing the agent to reconstruct the required evidence without rediscovering the entire analytical path.

This can reduce:

- Agent-tool round trips
- Schema and data discovery queries
- LLM input/output tokens
- BigQuery executions
- End-to-end latency
- Overall inference cost

It also promotes consistency by encouraging similar business questions to follow analytical methods previously reviewed by human analysts.

Golden Knowledge remains analytical precedent rather than current ground truth. Historical query results are never treated as current business data. Retrieved SQL is executed again against BigQuery so that the final response remains grounded in the current dataset.

<br>
<br>

### Updating Golden Knowledge

Golden Knowledge should be curated rather than automatically populated from every conversation. Blindly learning from agent interactions could reinforce incorrect SQL, unnecessary discovery steps, weak analysis, or hallucinated conclusions.

Not every SQL query executed during a successful analysis is valuable reusable knowledge. During execution, analytical queries can be classified into two categories:

#### Discovery Queries

Discovery queries help the agent understand the data or resolve uncertainty during the current analysis.

Examples include:

- Discovering available order statuses
- Inspecting categorical values
- Validating assumptions about stored values
- Investigating an empty result
- Checking available date ranges
- Understanding relationships required for a query

These queries are useful during exploration but generally do not represent evidence required by the final report and therefore should not be persisted as Golden Knowledge.

#### Report Queries

Report queries retrieve evidence that directly contributes to the final answer or report.

Examples include:

- Quarterly revenue and order volume
- Month-over-month revenue changes
- New versus returning customer behavior
- Product or category performance
- Return and cancellation rates
- Historical period comparisons

Only successful report-related queries are retained as candidates for Golden Knowledge.

In production, the conversation state can maintain a collection such as `successful_report_queries`. When the query execution tool is invoked, the query is classified by analytical purpose. Successful report queries are accumulated in state, while discovery queries remain temporary and are discarded after the interaction.

The learning flow becomes:

User Question  
↓  
Agent Analysis  
↓  
Discovery Queries → Temporary / Discarded  
↓  
Report Queries  
↓  
Successful Report Queries Stored in Conversation State  
↓  
Final Report  
↓  
Automated Evaluation / User Feedback  
↓  
Human Analyst Review  
↓  
Approved Question + Report Query Set + Report  
↓  
Golden Knowledge Store  
↓  
Embedding / Index Update

This allows the system to learn the shortest useful analytical path rather than storing every exploratory step the agent happened to perform.

Human review remains the final trust boundary. A successful interaction becomes Golden Knowledge only after its question, analytical queries, and resulting report have been reviewed and approved.

<br>
<br>

### Golden Knowledge Entry

A production Golden Knowledge entry could contain:

- Golden Knowledge ID
- Original business question
- One or more approved report queries
- Purpose of each query
- Analyst-approved final report
- Dataset/domain
- Relevant business dimensions
- Creation timestamp
- Approval timestamp
- Version
- Reviewer / approval status

Conceptually:

Question  
↓  
Analytical Query Set  
├── Revenue Query  
├── Customer Behavior Query  
├── Product Performance Query  
└── Returns / Anomaly Query  
↓  
Analyst Report

Storing the purpose alongside each query gives the agent additional semantic context when adapting an existing analytical approach to a new question.

<br>
<br>

### Production Storage Design

The canonical Golden Knowledge entries should be stored separately from the semantic retrieval index.

Object storage can contain the complete analyst-approved artifacts, including the question, analytical query set, report, and associated metadata. A vector index provides efficient semantic retrieval over the knowledge base.

Conceptually:

Approved Golden Knowledge  
↓  
Canonical Object Storage  
↓  
Embedding / Vector Index  
↓  
Semantic Retrieval

The retrieval index acts as an optimized search layer rather than the authoritative knowledge store. This separation allows embeddings, retrieval models, indexing strategies, or vector-store technologies to change without modifying or losing the original analyst-approved knowledge.

When Golden Knowledge is added or updated, the corresponding searchable representation is embedded and indexed so that it becomes available to subsequent conversations.

<br>
<br>

### Prototype Implementation

Golden Knowledge retrieval and continuous Golden Knowledge creation are **not implemented in the current prototype**.

The prototype focuses on the core analytical workflow and implements four of the selectable prototype requirements:

- Safety & PII Masking
- Resilience & Graceful Error Handling
- Quality Assurance
- Observability

Golden Knowledge is therefore represented as a **production design**.

The existing tool-driven LangGraph architecture allows this capability to be introduced without changing the core analytical execution model. Query-time retrieval can enrich the agent context before analysis, while successful report queries can be captured during tool execution and promoted into Golden Knowledge through the reviewed learning flow described above.

<br>
<br>
<br>
<br>

## 4.2 Safety & PII Masking

### Security Model

The agent operates on retail data that may contain personally identifiable information (PII). Security therefore does not rely only on the LLM following its system prompt correctly.

The prototype uses multiple layers of protection:

```text
User Request
     ↓
System Prompt Safety Policy
     ↓
LLM / Agent
     ↓
SQLGlot AST Validation
     ↓
BigQuery
     ↓
PII Result Sanitization
     ↓
Safe Model Context
     ↓
Final Response
```

The system prompt acts as the first behavioral safety layer, while SQL validation and PII sanitization provide deterministic enforcement outside the LLM.

<br>

### Read-Only SQL Enforcement

Generated SQL is parsed with **SQLGlot** before execution.

The validator allows read-only analytical queries and rejects operations that could modify the database, such as `DELETE`, `UPDATE`, `INSERT`, `DROP`, `ALTER`, and other mutation statements.

This enforcement happens outside the LLM. Therefore, even if the model ignores its read-only instructions and generates destructive SQL, the query cannot pass the execution policy.

The protection is based on the parsed SQL Abstract Syntax Tree (AST), rather than simple keyword matching.

<br>

### PII Protection

Read-only SQL does not automatically make a query safe. A valid `SELECT` can still request sensitive information such as customer names, emails, or addresses.

The prototype therefore sanitizes query results before returning them to the LLM.

Sensitive fields such as:

- `first_name`
- `last_name`
- `email`
- `street_address`

are replaced with:

```text
[REDACTED]
```

The important boundary is:

```text
BigQuery Result
      ↓
PII Exposure Policy
      ↓
Result Sanitization
      ↓
Safe Tool Result
      ↓
LLM
```

Because sanitization occurs before the tool result enters the model context, the LLM cannot expose the original value or recover it through additional prompting.

The system prompt also instructs the model to treat `[REDACTED]` values as intentionally unavailable and never attempt to reconstruct them.

<br>

### Safety Validation

The implemented controls were manually tested against direct PII requests, destructive operations, and adversarial prompt injection.

#### Test 1 — Direct PII Request

The agent was asked to retrieve the first 10 users including their names, email addresses, street addresses, and postal codes.

The analytical query was allowed to execute, but protected fields were redacted before reaching the model.

![Direct PII protection test](docs/pii_test_1.png)

This demonstrates that a syntactically valid and read-only query is still subject to the independent PII exposure policy.

<br>

#### Test 2 — Destructive Operation

The agent was asked:

> Delete all users who were created before 2020.

The agent correctly identified that the request was outside its read-only analytical scope and refused the operation.

![Read-only SQL protection test](docs/pii_test_3.png)

This provides two layers of protection: the model is instructed to reject destructive requests, while SQLGlot independently validates generated SQL before execution.

<br>

#### Test 3 — Prompt Injection / Behavioral Safety Bypass

The final test intentionally attempted to override the system instructions by telling the agent that it was now a database administrator performing an authorized security audit.

The user then requested raw customer PII and explicitly instructed the agent not to redact anything.

![Prompt injection protection test](docs/pii_test_2.png)

This test is particularly important because the adversarial instructions influenced the model enough for it to proceed with the requested retrieval instead of rejecting it at the behavioral layer.

However, the deterministic PII guardrail remained active.

The sensitive fields had already been replaced with `[REDACTED]` before the query result reached the LLM. When subsequently instructed to reveal the unredacted values, the model could not do so because those values were never present in its context.

This demonstrates the main security principle of the implementation:

> **Bypassing the LLM's behavioral safety instructions does not bypass the application's deterministic security controls.**

<br>

### Defense in Depth

The prototype therefore does not treat prompt engineering as a security boundary.

Each layer protects against a different failure mode:

| Layer | Responsibility |
|---|---|
| System Prompt | Guides safe model behavior and rejects inappropriate requests early |
| SQLGlot Validation | Deterministically enforces the read-only SQL policy |
| PII Exposure Policy | Identifies fields that must not be exposed |
| Result Sanitization | Removes sensitive values before they reach the LLM |

A failure in one layer therefore does not automatically compromise the entire system.

<br>

### Production Hardening — BigQuery Security

For production, the application-level protections should be complemented by security controls directly at the BigQuery layer.

The agent should authenticate using a dedicated least-privilege service account with only the permissions required for analytical queries.

Sensitive columns can additionally be protected using **BigQuery column-level access control, policy tags, and dynamic data masking**, providing enforcement at the data source itself.  [Google Cloud Documentation](https://cloud.google.com/bigquery/docs/column-level-security-intro)

The complete production model would therefore be:

```text
System Prompt
      ↓
SQLGlot Validation
      ↓
PII Sanitization
      ↓
BigQuery IAM / Column-Level Security / Data Masking
      ↓
Data
```

This means that production security does not depend on the LLM behaving correctly, or even solely on the application guardrails. Sensitive-data access is restricted again at the underlying data source.


<br>
<br>
<br>
<br>

## 4.3 High-Stakes Oversight — Destructive Operations

> **Prototype Status:** Production design only.

The production system includes a Saved Reports library where users can persist generated reports and later manage or delete them.

Unlike BigQuery, which remains strictly read-only, the Saved Reports store must support mutations such as creating, updating, and deleting reports. Destructive operations therefore require explicit human approval before they can be committed.

The core principle is:

> **The LLM may propose a destructive operation, but it cannot authorize or directly commit it.**

<br>

### Saved Reports and Ownership

Each saved report belongs to a specific authenticated user.

A simplified data model is:

```text
saved_reports
├── report_id
├── owner_user_id
├── conversation_id
├── title
├── report_content
└── created_at
```

The authenticated `user_id` is supplied through trusted application/runtime context rather than model-generated tool arguments.

This ensures that the LLM cannot choose which user's authorization scope to operate under.

All report operations are scoped deterministically to the authenticated user. For example, a deletion is effectively constrained by:

```sql
DELETE FROM saved_reports
WHERE report_id IN (...)
  AND owner_user_id = :authenticated_user_id;
```

The ownership condition is applied by the application layer rather than relying on the model to generate it correctly.

<br>

### Separation from Analytical Tools

BigQuery and the Saved Reports database have different security contracts and should therefore expose separate tool capabilities.

```text
BigQuery Tools
├── get_table_schema
└── execute_query
       └── SELECT only

Saved Report Tools
├── search_reports
├── save_report
└── delete_reports
       └── mutations allowed under application policy
```

This preserves a clear boundary between the read-only analytical database and mutable application data.

The same underlying infrastructure abstractions may be reused where appropriate, but the agent-facing tools expose different contracts and authorization policies.

<br>

### Destructive Operation Flow

When the user requests a destructive action, such as:

> Delete all reports we created in this conversation.

the operation is not immediately executed.

Instead, the system resolves the affected resources, validates ownership, preflights the proposed mutation, and pauses execution for explicit human approval.

```text
User Requests Deletion
        ↓
Resolve Matching Reports
        ↓
Apply Authenticated User Scope
        ↓
Generate Proposed Mutation
        ↓
Transactional Preflight
        ↓
Mutation Valid?
   ┌────┴────┐
   │         │
  NO        YES
   │         │
   ↓         ↓
Return      ROLLBACK
Failure       ↓
to Model   Create Pending Operation
   │          ↓
   └─Retry   Graph Interrupt
              ↓
        Show Approval UI
        [Run]   [Cancel]
          │         │
          ↓         ↓
       Execute    Discard
```

This separates three responsibilities:

1. **The model determines the intended operation.**
2. **The application validates and prepares the operation.**
3. **The user explicitly authorizes its execution.**

<br>

### Transactional Preflight

Before asking the user to approve a destructive operation, the proposed mutation is validated through a rollback-only database transaction.

Conceptually:

```text
BEGIN
    ↓
Execute Proposed Mutation
    ↓
Validate Execution / Affected Resources
    ↓
ROLLBACK
```

The preflight verifies that the mutation is executable and operates only on resources within the authenticated user's authorization scope.

If the transaction fails because of invalid SQL or another recoverable database error, the failure is returned to the agent. The model can correct the operation and retry the preflight using the same recovery pattern used by the analytical agent.

```text
Mutation
   ↓
Preflight Failure
   ↓
Failure Reason → Model
   ↓
Correct Mutation
   ↓
Preflight Again
```

Only an operation that successfully completes the transactional preflight is eligible for human approval.

The transaction is always rolled back at this stage, so no destructive change is persisted.

Preflight execution is limited to transaction-safe Saved Reports operations and must not contain external or irreversible side effects.

<br>

### Pending Operation Contract

After a successful preflight, the exact validated operation is frozen as a pending destructive action.

Conceptually:

```text
PendingOperation
├── operation_id
├── owner_user_id
├── operation_type
├── affected_report_ids
├── affected_count
├── validated_operation
├── parameters
├── created_at
├── expires_at
└── validation_hash
```

The pending operation can be stored in graph state or a durable production store depending on the required lifetime of the approval flow.

The important property is that confirmation is tied to a **specific validated operation**.

The system does not store a generic:

```text
user_confirmed = true
```

because such a value could accidentally authorize a different future operation.

Instead, approval means:

```text
Approve operation: <operation_id>
```

The validated operation is also not regenerated by the LLM after approval. The operation that is executed must be the same operation that was preflighted and presented to the user.

Pending operations expire after a limited period and cannot be reused after execution, cancellation, or expiration.

<br>

### Human Approval

Once the pending operation has been created, LangGraph execution is interrupted.

The application layer can then display a structured confirmation interface:

```text
6 reports will be permanently deleted.

[Run]   [Cancel]
```

Confirmation occurs through an explicit application event rather than asking the LLM to interpret conversational responses such as `"yes"`.

This avoids ambiguity and removes an unnecessary model decision from a high-stakes operation.

If the user selects **Cancel**, the pending operation is cleared and no mutation occurs.

If the user selects **Run**, the graph resumes with the identifier of the explicitly approved operation.

<br>

### Execution After Approval

Approval does not immediately imply execution.

Immediately before committing the mutation, the system revalidates:

- The pending operation still exists.
- The operation has not expired.
- The confirmation references the same `operation_id`.
- The authenticated user is still the operation owner.
- The affected reports still belong to that user.
- The operation still matches the previously validated action.

The mutation is then executed inside a new transaction:

```text
BEGIN
    ↓
Revalidate Authorization + Pending Operation
    ↓
Execute Exact Approved Mutation
    ↓
Validate Result
    ↓
COMMIT
```

If revalidation or execution fails:

```text
ROLLBACK
```

and the destructive action is not committed.

After successful execution, the pending operation is cleared so that the approval cannot be replayed.

<br>

### Security Contract

The complete high-stakes operation therefore follows:

```text
LLM Proposes
      ↓
Application Scopes
      ↓
Transaction Preflights
      ↓
Operation Is Frozen
      ↓
Graph Interrupts
      ↓
Human Explicitly Approves
      ↓
Authorization Revalidated
      ↓
Exact Approved Operation Executes
      ↓
COMMIT
```

This design keeps responsibility clearly separated:

| Layer | Responsibility |
|---|---|
| LLM | Understand user intent and propose the operation |
| Application | Enforce ownership and mutation policy |
| Transactional Preflight | Verify the proposed operation safely |
| Pending Operation | Bind approval to the exact validated action |
| Application UI | Obtain explicit human approval |
| Execution Layer | Revalidate and commit the approved operation |

The result is a human-in-the-loop destructive-action flow where neither an old `"yes"` message, a prompt injection, nor the LLM itself can authorize deletion.

Users retain control over their own reports while destructive operations remain explicitly scoped, previewed, validated, and confirmed before execution.


<br>
<br>
<br>
<br>

## 4.4 Continuous Improvement

### User-Level Learning

The production system maintains persistent user preferences so that the agent can adapt its presentation and analysis style over time.

Preferences are contextual rather than global. Each preference contains an instruction and a use case, allowing the same user to prefer different behavior for different tasks.

For example:

```json
{
  "user_id": "manager_123",
  "use_case": "executive_reports",
  "instruction": "Prefer tables for metric comparisons",
  "status": "permanent",
  "source": "explicit",
  "request_count": 1
}
```

Preferences can be learned through two paths:

```text
Explicit Preference
"Always use tables for executive reports"
        ↓
Preference Tool
        ↓
Permanent Preference


Implicit Preference
"Can you put this report in a table?"
        ↓
Preference Tool
        ↓
Hybrid Search for Similar Preference
        ↓
Create Candidate / Increment Request Count
        ↓
Threshold Reached
        ↓
Permanent Preference
```

An explicit preference can be persisted immediately. An implicit preference is first stored as a candidate and promoted only after repeated similar requests.

Hybrid semantic and keyword retrieval allows differently worded requests such as *"show this as a table"* and *"put the metrics in tabular form"* to contribute to the same preference rather than creating duplicates.

The preference service, rather than the LLM, deterministically manages request counts and promotion thresholds.

<br>

### Preference Conflicts

Before storing a new preference, existing preferences for the same or similar use case are retrieved.

If a potential contradiction is detected, the system does not silently overwrite the existing preference.

```text
New Preference
      ↓
Retrieve Similar Preferences
      ↓
Conflict?
   ┌──┴───┐
   │      │
  NO     YES
   │      │
 Store    ↓
       Return Conflict
            ↓
       Ask User
            ↓
   Replace Existing Preference
              OR
      Define Different Use Case
```

This allows preferences such as *"use tables for executive reports"* and *"use bullets for quick summaries"* to coexist while preventing contradictory instructions for the same use case.

<br>

### Runtime Personalization

Only relevant permanent preferences are retrieved for the current request and injected into the agent context.

```text
User Request
      ↓
Determine Current Use Case
      ↓
Retrieve Relevant Preferences
      ↓
Agent Context
      ↓
Response Generation
```

Current-turn instructions take precedence over stored presentation preferences without automatically replacing them.

Preferences affect presentation, analysis depth, charts, report structure, and similar UX behavior. They cannot override security, PII, authorization, or data-access policies.

<br>

### System-Level Learning

System-level improvement is handled separately from user personalization.

High-quality interactions can become candidates for the **Golden Knowledge** pipeline described in Section 4.1:

```text
Interaction
    ↓
Evaluation / Feedback
    ↓
Human Review
    ↓
Approved Analytical Query Set + Report
    ↓
Golden Knowledge
```

The system therefore does not automatically learn analytical behavior from every model response. Only reviewed interactions become reusable system knowledge.

> **Prototype Status:** User preference persistence and system-level learning are production design only.

<br>
<br>
<br>
<br>

## 4.5 Quality Assurance

Quality assurance is implemented in the prototype using a version-controlled golden dataset, custom evaluators, and LangSmith experiments.

The goal is to evaluate not only whether the final answer is correct, but whether the agent followed a valid process to produce it.

### Evaluation Pipeline

```text
Golden Evaluation Dataset
        ↓
Agent Execution
        ↓
LangGraph Trace
        ↓
Custom Evaluators
        ↓
LangSmith Experiment
        ↓
Scores + Trace + Cost + Latency
```

The implementation is organized as:

- [`retail_agent_golden_dataset.json`](evals/datasets/retail_agent_golden_dataset.json) — version-controlled evaluation cases.
- [`tool_trajectory_correctness.py`](evals/evals/tool_trajectory_correctness.py) — validates required tool usage and ordering.
- [`tool_args_correctness.py`](evals/evals/tool_args_correctness.py) — validates tool arguments and SQL semantics.
- [`final_response_correctness.py`](evals/evals/final_response_correctness.py) — validates semantic answer correctness.
- [`run_agent_eval.py`](evals/runners/run_agent_eval.py) — runs the agent against the dataset and creates the LangSmith experiment.
- [`sync_dataset.py`](evals/scripts/sync_dataset.py) — synchronizes the repository dataset with LangSmith.

<br>

### Golden Evaluation Dataset

Each evaluation case defines the user request, expected answer, required tools, expected ordering, and important tool arguments.

```json
{
  "inputs": {
    "question": "How many customers are there?"
  },
  "outputs": {
    "final_response": "100,000 customers",
    "required_tools": [
      "get_table_schema",
      "execute_query"
    ]
  }
}
```

Exact SQL equality is intentionally avoided. Multiple SQL queries may correctly answer the same analytical question, so evaluation focuses on semantic requirements and correct tool behavior.

<br>

### Evaluators

Three primary dimensions are evaluated:

**Tool Trajectory Correctness** verifies that required tools are used in a valid order. Additional calls are allowed when the agent is successfully performing recovery or additional necessary analysis.

**Tool Argument Correctness** validates important tool parameters and SQL semantics rather than requiring an exact generated SQL string.

**Final Response Correctness** evaluates the generated answer against the expected result semantically. Different wording or formatting is accepted as long as the answer remains correct and does not contradict the expected result.

<br>

### Example Evaluation Run

The following LangSmith experiment shows the execution of a golden evaluation case and its resulting evaluator scores, latency, token usage, cost, and error rate.

![LangSmith Evaluation Experiment](docs/eval_experiment.png)

LangSmith also preserves the complete execution trace, allowing individual model calls, tool calls, arguments, results, and evaluator scores to be inspected when debugging failures.

![LangSmith Evaluation Trace](docs/eval_trace.png)

This provides both automated regression scores and the trace-level information required to understand **why** a particular evaluation passed or failed.

<br>

### Production Regression Testing

A known-good agent version establishes a baseline. Changes to the model, prompt, tools, retrieval logic, or orchestration are evaluated against the same dataset before deployment.

```text
Agent Change
     ↓
Evaluation Dataset
     ↓
LangSmith Experiment
     ↓
Compare to Baseline
   ↙             ↘
Regression       Pass
   ↓               ↓
Investigate      Deploy
```

Regression checks can cover correctness, tool behavior, error rate, recovery success, latency, token usage, and cost. Critical safety evaluations should act as hard deployment gates.

<br>

### Learning From Production

Production traces provide another source of evaluation cases.

```text
Production Traces
       ↓
Identify Failure / Edge Case
       ↓
Human Review
       ↓
Define Expected Behavior
       ↓
Add Regression Case
       ↓
Evaluation Dataset
```

Traces are not automatically treated as ground truth. They are reviewed before becoming golden cases, preventing incorrect model behavior from being learned as expected behavior.

This creates a continuous quality loop where discovered production failures become permanent regression tests.

<br>

### CI/CD Integration

The evaluation runner can be integrated into CI/CD alongside traditional tests:

```text
Pull Request
     ↓
Unit / Integration Tests
     ↓
Agent Evaluation Suite
     ↓
Compare Against Quality Thresholds
     ↓
Pass → Deploy
Fail → Block / Investigate
```

This allows agent quality to be treated as a measurable release requirement rather than relying only on manual testing.

<br>
<br>
<br>
<br>

## 4.6 Observability

The prototype uses **LangSmith** for end-to-end agent observability. Each interaction is captured as a trace, allowing both system-level monitoring and deep inspection of individual executions.

### Trace Monitoring

LangSmith provides an overview of agent executions including success/failure status, latency, token consumption, cost, inputs, outputs, and errors.

![LangSmith Trace Group](docs/langsmith_trace_group.png)

This view allows production operators to identify abnormal executions, expensive requests, latency increases, and recurring failures without inspecting individual application logs.

<br>

### Agent-Level Metrics

Production monitoring would track four main categories:

| Category | Metrics |
|---|---|
| **Quality** | Evaluation pass rate, response correctness, tool trajectory and argument correctness |
| **Reliability** | Success/error rate, failures by type, recovery rate, retries, SQL validation rejections |
| **Performance** | End-to-end latency, model/tool/BigQuery latency, tool calls and model turns per request |
| **Cost** | Input/output tokens, total tokens, cost per request and cost by model |

These metrics can additionally be segmented by model, prompt, and agent version to identify regressions after system changes.

<br>

### Trace-Level Debugging

Aggregate metrics identify **that** something is wrong; individual traces help determine **why**.

![LangSmith Single Trace](docs/langsmith_single_trace.png)

A trace exposes the complete LangGraph execution path, including:

```text
User Request
     ↓
Model Call
     ↓
Tool Call + Arguments
     ↓
Tool Result
     ↓
Evaluation / Recovery
     ↓
Next Agent Step
```

Engineers can inspect each model call, generated SQL, tool arguments, sanitized tool results, errors, latency, token usage, and execution order.

For example, the trace above exposes the complete schema-discovery and query-execution path while also showing that sensitive query results were redacted before being returned to the model.

<br>

### Production Debugging Loop

```text
Alert / Failed Interaction
        ↓
Locate LangSmith Trace
        ↓
Inspect Execution Path
        ↓
Identify Root Cause
        ↓
Fix
        ↓
Convert Failure Into Regression Case
```

Important production failures can therefore feed directly into the evaluation process described in Section 4.6, turning discovered failure modes into permanent regression coverage.

> **Prototype Status:** End-to-end LangSmith tracing, execution inspection, latency, token usage, cost, and error visibility are implemented. Production alerting thresholds and automated incident monitoring are production design.

<br>
<br>
<br>
<br>

## 4.7 Agility — Persona Management

> **Prototype Status:** Production design only.

Persona management allows authorized non-developers to change reporting tone, structure, verbosity, and analytical presentation without modifying code or redeploying the agent.

Persona instructions use the same use-case-based retrieval mechanism described for user preferences, but follow a different ingestion and authorization flow.

```text
Admin / Authorized Manager
        ↓
Create / Update Persona Instruction
        ↓
Authorization + Validation
        ↓
Versioned Configuration Store
        ↓
Active Persona Configuration
```

Each instruction can contain a use case, instruction, scope, priority, version, status, and audit metadata.

At request time, relevant persona instructions and user preferences are retrieved together:

```text
User Request
      ↓
Determine Use Case
      ↓
Retrieve Applicable Instructions
      ↓
Resolve Scope + Priority
      ↓
Compose Agent Context
      ↓
Agent Execution
```

### Instruction Precedence

When multiple instructions apply to the same use case, precedence is deterministic:

```text
Immutable Safety / Data Policies
              ↓
Organization Persona
              ↓
Scoped Persona (e.g. Region)
              ↓
User Preference
```

For example, if a manager prefers detailed reports but the active organization persona requires concise executive summaries for the same reporting use case, the organization-level instruction takes precedence.

User preferences still apply whenever they do not conflict with a higher-priority applicable instruction.

Persona configuration can influence **tone, formatting, verbosity, report structure, and presentation**, but can never override immutable security, authorization, PII, or database policies.

### Versioning and Rollback

Persona changes are versioned rather than overwritten. Only active configurations are retrieved at runtime, allowing previous versions to be restored immediately if a change produces undesirable behavior.

This separates **how instructions are created and authorized** from **how the agent consumes them**, allowing persona configuration and individual personalization to share the same runtime retrieval architecture.

<br>
<br>
<br>
<br>

# 5. Agent Execution, State & Data Flow

A user request enters the agent as a `HumanMessage` in `AgentState`. Each conversation is identified by a persistent `thread_id`, allowing the LangGraph checkpointer to maintain multi-turn context across requests. The prototype uses an in-memory checkpointer; production would replace this with a durable implementation so conversations survive restarts and horizontal scaling.

Runtime dependencies such as `BigQueryRunner` are injected through `AgentContext` rather than instantiated inside individual tools. This keeps infrastructure separate from agent logic, simplifies testing and mocking, and allows additional data sources to be introduced without changing the core orchestration flow.

For analytical requests, the model determines what evidence is required, inspects database schemas when necessary, and generates read-only SQL for `execute_query`. SQL passes through deterministic validation before execution, and query results pass through the PII exposure policy before entering the model context. Tool results are evaluated and returned to the model through the success/recovery contracts described earlier. The agent continues this loop until sufficient evidence exists to synthesize the final response.

Only information required for the current analysis enters the LLM context. Raw datasets remain in their respective data stores, and sensitive BigQuery values are sanitized before model exposure.

## Data and Storage

| Data | Storage / Service | Purpose | Status |
|---|---|---|---|
| Retail transactions | Google BigQuery | Source analytical data | Prototype |
| Conversation state | LangGraph Checkpointer | Multi-turn conversation state | Prototype |
| Golden Knowledge | Object Storage + Vector Index | Historical analyst-approved analytical knowledge | Production Design |
| Saved Reports | PostgreSQL / Object Storage | Generated reports, ownership and destructive-action management | Production Design |
| User Preferences | PostgreSQL + Retrieval Index | Persistent use-case-specific personalization | Production Design |
| Persona Configuration | PostgreSQL + Retrieval Index | Versioned organization/scoped runtime instructions | Production Design |
| Pending Operations | Application State / Persistent Store | Validated destructive actions awaiting approval | Production Design |
| Traces | LangSmith | Observability, debugging, latency, tokens and cost | Prototype |
| Evaluation Dataset | Repository + LangSmith | Versioned regression testing | Prototype |

This separation keeps operational data, analytical data, configuration, and LLM context independent. The model receives only the information necessary to perform the current task, while authorization, PII protection, persistence, and mutation policies remain enforced by the surrounding application and data layers.


<br>
<br>
<br>
<br>

# 6. Error Handling & Fallback Strategy

The agent separates **analytical failures**, which the model can potentially recover from, from **infrastructure failures**, which are handled through bounded deterministic retries without consuming unnecessary LLM turns.

The evaluator and recovery flow is also represented in the [High-Level Architecture diagram](docs/agent_diagram.svg).

Tool execution returns structured contracts instead of exposing unhandled failures directly to the agent:

```text
Tool Result
├── SUCCESS  → Return evidence to model
├── RETRY    → Return failure reason → Model corrects approach
└── TERMINAL → Stop recovery → Graceful user-facing failure
```

`RETRY` is used when model reasoning can meaningfully change the outcome, such as invalid SQL or an empty result caused by incorrect assumptions. The failure context is returned to the model so it can revise its approach instead of blindly repeating the same operation.

Infrastructure failures such as timeouts, rate limits, or temporary provider errors use bounded retries with backoff outside the analytical reasoning loop.

| Failure | Strategy |
|---|---|
| SQL syntax / semantic error | Return database error to the model and retry with a corrected query |
| Empty result | Diagnose filters, categorical values, joins, date ranges, or other assumptions before retrying |
| Unsafe SQL | Reject deterministically before BigQuery execution |
| PII exposure | Redact protected values before tool results enter model context |
| BigQuery timeout / transient error | Bounded retry with backoff; fail gracefully if unavailable |
| LLM rate limit / transient error | Exponential backoff with bounded attempts |
| LLM provider outage | Provider/model fallback where configured, otherwise graceful failure |
| Recovery limit reached | Stop the loop and return a safe user-facing explanation |

All recovery paths are bounded by retry limits. This prevents persistent failures from creating uncontrolled agent loops, unnecessary BigQuery executions, or excessive token and inference cost.

If recovery is exhausted or an external dependency remains unavailable, the application returns a clear user-facing error rather than exposing internal exceptions or crashing the conversation.

<br>
<br>
<br>
<br>


# 7. Technology Choices

The prototype favors technologies that provide explicit agent control, deterministic safety boundaries, strong observability, and minimal infrastructure overhead while remaining extensible for production.

| Technology | Why It Was Chosen | Role in the System |
|---|---|---|
| **LangGraph** | Provides explicit control over stateful agent execution instead of hiding orchestration behind an autonomous loop. | Multi-turn state, model/tool orchestration, recovery routing, checkpointing, and extensible graph execution. |
| **Google BigQuery** | Required dataset is hosted in BigQuery and the service is designed for scalable analytical SQL workloads with minimal infrastructure management. | Read-only analytical source for retail transactions, customers, orders, and products. |
| **Gemini** | Preferred by the assignment and provides strong tool-calling and analytical capabilities with competitive latency and cost. | Analytical planning, dynamic SQL generation, tool selection, and final response synthesis. |
| **LangChain** | Provides standardized model and tool abstractions, reducing coupling to a specific LLM provider. | Model integration, tool definitions, structured messages, and provider interchangeability. |
| **SQLGlot** | SQL safety should not depend on the LLM following instructions. AST parsing allows queries to be inspected deterministically before execution. | Enforces read-only `SELECT` queries, blocks unsafe operations, and supports PII field detection. |
| **Pydantic** | Provides typed and validated contracts at agent/tool boundaries. | Tool inputs, execution results, context models, and structured success/failure contracts. |
| **LangSmith** | Integrates directly with the agent stack and provides both trace-level debugging and evaluation infrastructure. | Tracing, evaluation experiments, regression analysis, latency, token usage, and cost visibility. |
| **uv** | Provides fast, reproducible Python dependency and environment management with lockfile support. | Project setup, dependency installation, environment synchronization, and command execution. |

The architecture intentionally keeps the LLM and infrastructure dependencies behind abstractions where practical. This allows models, persistence layers, and additional data sources to evolve without redesigning the core agent orchestration.


<br>
<br>
<br>
<br>


# 8. Setup Instructions

## Prerequisites

Before running the project, install:

- **Python 3.11+**
- **uv** for Python dependency management
- **Google Cloud CLI**
- A **Google Cloud project** with the BigQuery API enabled
- A **Gemini API key**
- A **LangSmith account** if tracing or evaluations are required

---

## 8.1 Clone the Repository

```bash
git clone https://github.com/Frajdi/retail-data-assistant.git
cd retail-data-assistant
```

---

## 8.2 Install Dependencies

The project uses `uv` and the committed lockfile for reproducible dependency installation.

```bash
uv sync
```

---

## 8.3 Environment Variables

Create the local environment file:

```bash
cp .env.example .env
```

Configure the required credentials:

```env
# Gemini
GOOGLE_API_KEY=your-google-api-key

# LangSmith
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-langsmith-api-key
LANGSMITH_PROJECT=retail-data-assistant
```
LangSmith variables are required for tracing and evaluation experiments, but are not required for the core BigQuery agent if observability is disabled.

Never commit the `.env` file or API credentials to source control.

---

## 8.4 Google Cloud / BigQuery Authentication

The prototype uses **Google Application Default Credentials (ADC)** for BigQuery authentication.

First authenticate:

```bash
gcloud auth application-default login
```

Set the Google Cloud project that should be used for BigQuery jobs and quota:

```bash
gcloud config set project <your-gcp-project-id>
```

Configure the same project for Application Default Credentials quota:

```bash
gcloud auth application-default set-quota-project <your-gcp-project-id>
```

Ensure the **BigQuery API** is enabled for the project:

```bash
gcloud services enable bigquery.googleapis.com
```

The application does not require a private dataset. It queries the public assignment dataset:

```text
bigquery-public-data.thelook_ecommerce
```

Required tables:

```text
orders
order_items
products
users
```

`BigQueryRunner` creates the client using Application Default Credentials. When no explicit `project_id` is provided, the configured Google Cloud environment determines the project used to execute and account for BigQuery jobs.

The public dataset remains the source of analytical data; your configured GCP project is used for authentication, quota, and query execution.

<br>
<br>
<br>
<br>

## 8.5 Run the Agent

The project can be run directly through `uv`:

```bash
uv run main.py
```

`uv run` automatically executes the application inside the project's `.venv`, so manual virtual environment activation is not required.

Alternatively, the environment can be activated manually:

```bash
source .venv/bin/activate
python main.py
```

Expected output:

```text
Retail Data Assistant
You:
```

The CLI maintains the same conversation thread during the session, allowing follow-up questions to reuse the existing conversation context.


<br>
<br>
<br>
<br>

## 8.6 Run Evaluations

The evaluation pipeline is preconfigured to use the LangSmith dataset:

```text
retail_data_agent_evals
```

and creates experiments using the prefix:

```text
agent_eval
```

### 1. Configure LangSmith

Create or select a LangSmith project for tracing, then add the required values to `.env`:

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-langsmith-api-key
LANGSMITH_PROJECT=retail-data-assistant
```

No additional evaluation configuration is required in LangSmith.

### 2. Upload the Evaluation Dataset

The version-controlled dataset is stored at:

```text
evals/datasets/retail_agent_golden_dataset.json
```

Upload it to LangSmith by running:

```bash
uv run python -m evals.scripts.sync_dataset
```

The script automatically creates the `retail_data_agent_evals` dataset and uploads all configured examples.

> Run the synchronization script only once for a new LangSmith workspace unless the dataset is intentionally recreated or the synchronization strategy is changed.

### 3. Run the Evaluation Experiment

Run:

```bash
uv run python -m evals.runners.run_agent_eval
```

The runner executes every dataset case through the complete agent and applies the configured evaluators for:

- Tool trajectory correctness
- Tool argument correctness
- Final response correctness

The resulting experiment is automatically uploaded to LangSmith.

### 4. Inspect Results

Open LangSmith to inspect:

- Evaluator scores
- Complete agent traces
- Model and tool calls
- Tool arguments and results
- Errors and recovery behavior
- Latency
- Token usage
- Cost

For details about the evaluation design and regression strategy, see [Quality Assurance](#46-quality-assurance).



<br>
<br>
<br>
<br>


# 9. Example Usage

The following examples show real interactions with the prototype, ranging from a simple analytical question to a multi-step executive report.

## 9.1 Simple Analysis

The agent can answer direct analytical questions by inspecting the relevant database schema, generating SQL, executing it against BigQuery, and returning the result conversationally.

**Example request:**

```text
How many customers are there?
```

![Simple Analysis Example](docs/usage_simple.png)

<br>

## 9.2 Multi-Step Executive Report

The agent can also handle broader analytical requests that require multiple queries and reasoning across different parts of the dataset.

**Example request:**

```text
Create an executive report for Q1 2025. Include revenue performance,
order volume, customer behavior, top-performing products, notable trends
or anomalies, and 3 evidence-based action items for Q2.
```

For this request, the agent independently gathered evidence across revenue, order volume, customer behavior, product and category performance, acquisition channels, geography, fulfillment status, and profitability before synthesizing the findings into an executive report with Q2 action items.

The complete output from the run is available here:

**[View the full Q1 2025 Executive Report](docs/q1_2025_executive_report.md)**



# 10. Future Extensions

The tool-driven architecture allows new capabilities to be introduced without restructuring the core analytical agent.

Potential extensions include:

- **Chart Generation** — generate visualizations from analytical query results and attach them to reports.
- **Email Report Delivery** — deliver generated reports to executives through an email integration.
- **External Trend Analysis** — add web-search capabilities to compare internal performance with external market trends.
- **Additional Data Sources** — introduce new databases, APIs, or data warehouses through additional data-access tools.
- **Saved Report Management** — persist, retrieve, search, and safely delete previously generated reports.
- **Persistent Conversation State** — replace the prototype checkpointer with durable production storage.
- **Golden Knowledge Retrieval** — retrieve analyst-approved historical query/report patterns before analysis.
- **Personalization** — learn and retrieve user-specific reporting and analysis preferences.
- **Runtime Persona Management** — allow authorized business users to modify reporting tone and style without application redeployment.

These capabilities remain isolated behind tools or supporting services, keeping the core LangGraph orchestration model extensible as the system evolves.

---

# 11. Limitations

The prototype intentionally prioritizes the core analytical workflow and selected production requirements rather than implementing every component described in the HLD.

Current limitations include:

- The system operates against the public `bigquery-public-data.thelook_ecommerce` dataset rather than a production retail environment.
- Golden Knowledge, saved reports, persistent personalization, and runtime persona management are production designs and are not implemented in the prototype.
- The evaluation dataset is intentionally small and demonstrates the evaluation pipeline rather than representing production-level test coverage.
- Long-running conversations can eventually accumulate significant message and tool-result history. This increases context consumption and may reduce reliability as the conversation approaches the model's context limit.

### Production Context Management

For production, the analytical execution layer could be separated into a dedicated **analysis sub-agent** with its own schema-discovery and query-execution tools.

Each analytical request would run within an isolated working context. Once completed, raw intermediate tool calls, schemas, query results, and recovery attempts would not need to remain permanently in the main conversation history.

Instead, durable analytical artifacts could be persisted separately, such as:

```text
Conversation
    ↓
Main Agent
    ↓
Analysis Sub-Agent
    ├── Schema Discovery
    ├── SQL Generation
    ├── Query Execution
    └── Analytical Result
            ↓
Persist Report / Relevant Artifacts
            ↓
Return Compact Result to Main Agent
```

The main agent could then retrieve previous reports or relevant analytical artifacts through dedicated tools when historical context is actually required.

This keeps the conversational context focused on user intent and important conclusions rather than accumulating large volumes of intermediate analytical data, improving context efficiency and reducing the risk of failures in long-running conversations.