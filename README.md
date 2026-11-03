# 🎸 Music Emporium — AI Customer Service Agent (`music-emporium`)

> **Artefact Technical Assessment — AI Engineer (Full-Stack para Aplicações com IA Generativa)**  
> **Candidate:** Lucas Mota  
> **Repository:** [https://github.com/llucasmota/music-emporium](https://github.com/llucasmota/music-emporium) (Public Repository)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Framework: LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Model: Gemini 3.5 Flash-Lite](https://img.shields.io/badge/LLM-Gemini%203.5%20Flash--Lite-4285F4.svg)](https://aistudio.google.com/)
[![Tests: Pytest](https://img.shields.io/badge/Tests-26%2F26%20Passing-success.svg)](https://docs.pytest.org/)
[![UI: Rich & Streamlit](https://img.shields.io/badge/UI-CLI%20%2B%20Streamlit-FF4B4B.svg)](https://streamlit.io/)

---

## Executive Summary & Business Scenario

**Empório da Música** is a traditional musical instruments store founded in 2008 in **Campo Grande, Mato Grosso do Sul**. While the store takes pride in its warm, community-driven reputation (*"Sua música começa aqui"*), the customer service team is currently overwhelmed by high volumes of recurring inquiries via WhatsApp: opening hours, catalog pricing, order tracking, real-time stock availability, and return/warranty policies.

This project delivers an **AI Customer Service Agent Prototype in Python**, capable of:
1. **Embodying the Store Persona:** Informal, friendly, technically knowledgeable, and genuinely enthusiastic about music ("an experienced musician friend behind the counter").
2. **Context-Aware Dynamic Routing:** Querying operational databases (stock, specs, prices, order status) and store policies (7-day online repentance, warranties, payment terms) using typed tool-calling.
3. **Firm Business Boundary Guardrails:** Firmly and politely declining out-of-scope inquiries (accessories such as strings, cables, picks, effect pedals, and amplifiers), redirecting customers to local partner stores.
4. **Clean Architecture & Dual Presentation:** Providing an interactive terminal CLI (`main.py`) for developers and automated testing, alongside a WhatsApp-styled Web UI (`app.py`) for stakeholders.

```
                               ┌──────────────────────────────────────────────────────────┐
                               │                 Presentation Layer                       │
                               │  Terminal CLI (`main.py`)  |  Web UI (`app.py` Streamlit)│
                               └────────────────────────────┬─────────────────────────────┘
                                                            │ User Message
                                                            ▼
                               ┌──────────────────────────────────────────────────────────┐
                               │           MusicStoreAgent (`src/agent.py`)               │
                               │  - LangGraph StateGraph & Checkpointing Memory           │
                               │  - Musical Empathy & Guardrails (`src/prompt.py`)        │
                               │  - ReAct ToolNode with SQLite & Dynamic Policies         │
                               └────────────────────────────┬─────────────────────────────┘
                                                            │ Typed Function Calls
                               ┌────────────────────────────┴─────────────────────────────┐
                               ▼                                                          ▼
                ┌──────────────────────────────┐                           ┌──────────────────────────────┐
                │   Database Engine (`src/db`) │                           │ Knowledge Engine (`src/know`)│
                │ - In-Memory SQLite Store     │                           │ - Dynamic PDF Ingestion      │
                │ - Parameterized Catalog/Order│                           │   (`políticas_da_loja.pdf`)  │
                │   Queries (`data/*.csv`)     │                           │ - Structured Policy Lookup   │
                └──────────────────────────────┘                           └──────────────────────────────┘
```

---

## 1. Instructions to Run the Project (Instruções para Rodar o Projeto)

### 1.1 Prerequisites

This project requires **Python 3.11** or higher (developed and evaluated locally with Python 3.14 on macOS). If Python is not yet installed on your system:
- **macOS:** Install via Homebrew (`brew install python@3.12`) or official installer from [python.org](https://www.python.org/downloads/macos/).
- **Linux (Ubuntu/Debian):** `sudo apt update && sudo apt install -y python3 python3-pip python3-venv`
- **Windows:** Download the latest installer from [python.org](https://www.python.org/downloads/windows/) and ensure **"Add python.exe to PATH"** is checked. If PowerShell blocks script execution, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`.

---

### 1.2 Project Setup & Virtual Environment

Once Python is installed, clone the repository and configure an isolated virtual environment:

```bash
# 1. Clone the repository
git clone https://github.com/llucasmota/music-emporium.git
cd music-emporium

# 2. Create the virtual environment
# On macOS / Linux:
python3 -m venv .venv

# On Windows:
python -m venv .venv

# 3. Activate the virtual environment
# On macOS / Linux:
source .venv/bin/activate

# On Windows (Command Prompt):
.venv\Scripts\activate.bat

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# 4. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 1.3 Model Provider Configuration (`.env`)

1. Obtain a free **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com/) (ready in 60s, no credit card required).
2. Copy the sample environment file:
   ```bash
   # On macOS / Linux:
   cp .env.example .env

   # On Windows (CMD / PowerShell):
   copy .env.example .env
   ```
3. Edit `.env` with your API key:
   ```bash
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   MODEL_NAME=gemini-3.5-flash-lite
   DEBUG_MODE=false
   ```

---

### 1.4 Execution Commands

#### Option A: Interactive Terminal CLI (Recommended for Fast Evaluation)

Launch the styled interactive CLI with real-time status spinners and conversation export:

```bash
python main.py
```

**CLI Commands:**
- `sua pergunta`: Type naturally in Portuguese.
- `/export [filename.md]`: Automatically exports the current dialogue to `examples/` in Markdown format.
- `/reset`: Clears session conversational memory.
- `/sair`: Exits the program.

#### Option B: Web UI (Streamlit Chat with Musical Animation)

Launch the WhatsApp-styled web application featuring real-time musical equalizer animations:

```bash
streamlit run app.py
```
*The app will automatically open in your browser at `http://localhost:8501`.*

---

### 1.5 Automated Verification & Tests

#### Pytest Unit Test Suite (26 Passing Tests)

The test suite covers configuration, SQLite ingestion, catalog filtering, orders joins, direct PDF policy ingestion, prompt constraints, calendar/holidays, complaint registration, and agent state management:

```bash
pytest -v
```

Expected output:
```text
tests/test_agent.py::test_agent_initialization PASSED
tests/test_agent.py::test_agent_history_reset PASSED
tests/test_agent.py::test_agent_export_markdown PASSED
tests/test_calendar.py::test_store_hours_and_holidays_fixed_clock PASSED
tests/test_config.py::test_settings_load_defaults PASSED
tests/test_database.py::test_query_products_with_price_limit PASSED
tests/test_database.py::test_query_product_details PASSED
tests/test_database.py::test_a1_pix_price_calculation PASSED
tests/test_database.py::test_a2_max_installments_calculation PASSED
tests/test_database.py::test_c1_order_privacy_and_notes PASSED
tests/test_database.py::test_c2_product_status PASSED
tests/test_database.py::test_c3_robust_search_and_ambiguity PASSED
tests/test_database.py::test_c4_real_total_count PASSED
tests/test_database.py::test_price_budget_fallback_respects_max_price PASSED
tests/test_database.py::test_block_2b_order_return_eligibility_and_phone_validation PASSED
tests/test_database.py::test_block_3_complaints_table_and_registration PASSED
tests/test_knowledge.py::test_available_topics PASSED
tests/test_knowledge.py::test_get_policy_returns_accurate_terms PASSED
tests/test_knowledge.py::test_store_summary_includes_crucial_guardrails PASSED
tests/test_knowledge.py::test_load_policies_directly_from_pdf PASSED
tests/test_prompt.py::test_system_prompt_contains_crucial_elements PASSED
tests/test_tools.py::test_buscar_produtos_tool PASSED
tests/test_tools.py::test_consultar_detalhes_produto_tool PASSED
tests/test_tools.py::test_consultar_pedido_tool PASSED
tests/test_tools.py::test_consultar_politicas_tool PASSED
tests/test_tools.py::test_registrar_reclamacao_tool PASSED
============================== 26 passed in 0.85s ==============================
```

#### Conversational Verification (`scripts/check_examples.py`)

Automatically inspects the recorded conversation files (`examples/*.md`), validating that quoted prices, stock counts, order numbers, tracking codes, and installment formulas correspond to database ground-truth. Enforces LGPD privacy authentication and verifies that complaint confirmations include an official protocol (`REC-AAAAMMDD-NNNN`):

```bash
python scripts/check_examples.py
```

---

## 2. Technical Decisions & Strategic Rationale (Justificativa das Decisões Técnicas)

Following the decision categories specified in the challenge brief, our technical choices balance conversational responsiveness, data integrity, and operational simplicity:

| Decision Area (from the brief) | Guidance / Options | Chosen Implementation | Technical Justification & Rationale |
| :--- | :--- | :--- | :--- |
| **1. Framework & Agent Approach** | *RAG, function calling, ReAct, SQL agent, hybrid, etc.* | **Hybrid ReAct with Typed Tool-Calling on LangGraph (`StateGraph`)** | Cyclic graph execution with decoupled reasoning and execution nodes (`ToolNode`), conditional routing (`tools_condition`), and thread checkpointing, avoiding future architectural rewrites. |
| **2. Model & Provider** | *Paid, free, local, or API models.* | **Google Gemini (`gemini-3.5-flash-lite`) via Google AI Studio API** | Low latency (indicative local measurement: ~1.0s raw, ~4.5s multi-step ReAct loop with tools), reliable structured tool calling, and straightforward onboarding for reviewers and colleagues using standard Google accounts with no credit card required. |
| **3. Interaction Interface** | *CLI, notebook, API, or simple UI — focus on correct functioning.* | **Dual Mode: Interactive CLI (Rich) + WhatsApp Web UI (Streamlit)** | Addresses both engineering and business stakeholders: instant CLI execution (`main.py`) with session export (`/export`) for automated verification, alongside a visual WhatsApp-styled UI (`app.py`) with musical equalizer animations. |
| **4. Conversation History Persistence** | *Implement if it adds value to user experience.* | **Thread-Isolated Checkpointing via LangGraph `MemorySaver`** | Maintains clean conversation state indexed by `thread_id`. Supports session resets (`/reset`) and dialogue export. Upgrading to distributed multi-worker persistence (`PostgresSaver` or `RedisSaver`) in production is a localized change (checkpointer swap and connection configuration). |
| **5. Data Treatment & Retrieval** | *Perform data treatment as deemed necessary.* | **Relational In-Memory SQLite + Direct PDF Policy Ingestion (`pypdf`)** | **Relational SQLite:** Adopts a true relational database schema with multi-table `JOINs` and parameterized queries, enabling straightforward future migration to PostgreSQL while remaining lightweight with no local infrastructure setup.<br>**Business Rules:** 5% PIX discounts (§6.2) and installment limits (§3.1) are not present in raw CSVs; they are calculated deterministically in Python/SQL over catalog prices to prevent LLM arithmetic errors.<br>**Direct PDF Ingestion:** The 8-page manual (~1,680 words) is read from `data/políticas_da_loja.pdf` using `pypdf` and placed entirely into the prompt context (~3k tokens, estimate), with `consultar_politicas` available as a targeted lookup tool. Swapping the PDF immediately updates knowledge without manual transcription or chunking errors. |

---

### Deep Dive into Core Architectural Choices:

#### 2.1 Agent Tools & Retrieval Routing (Data vs. Policies):
The agent must know when to query operational data and when to consult store policies. We address this through a decoupled routing architecture:
- **The 5 Agent Tools (defined in `src/tools.py`):**
  1. `buscar_produtos(termo, categoria, preco_maximo)`: Searches catalog instruments matching text terms, categories, or price limits. Returns matching products with status, specs, stock count, and precalculated PIX price and installment options.
  2. `consultar_detalhes_produto(nome_ou_id)`: Returns full instrument specifications, commercial status (active, discontinued, coming_soon), current warehouse stock, PIX price, and installment breakdown for a given product name or numeric ID.
  3. `consultar_pedido(numero_pedido, email_ou_telefone, codigo_rastreio, termo_cliente)`: Queries order delivery status, carrier tracking code, and itemized purchase breakdown. Enforces customer verification (`email_ou_telefone`) for `numero_pedido` queries, while public courier tracking (`codigo_rastreio`) returns status directly.
  4. `consultar_politicas(topico)`: Retrieves the verbatim text of an official policy section matching one of the 9 official store topics or related keywords.
  5. `registrar_reclamacao(resumo, email, numero_pedido)`: Formally registers a customer complaint in the system database using issue summary (minimum 10 characters), customer email, and optional order number, generating an official sequential protocol (`REC-AAAAMMDD-NNNN`) and quoting the store's 24-business-hour SLA (§7.3).

- **Data vs. Policies Routing Strategy:**
  - **Policies in Context (Prompt + Tool Fallback):** The store manual comprises 8 pages (~1,680 words, ~3k tokens, estimate). Rather than building a vector store with chunking and embeddings, the full text of all unique policy sections is extracted via `pypdf` at startup and embedded directly into the system prompt via `get_store_policy_summary()`. The tool `consultar_politicas` provides an additional targeted retrieval path for focused questions. Because the entire manual fits into the model's context window, this eliminates chunk boundary truncations, cosine similarity retrieval errors, and embedding latency.
  - **Operational Data via Tools Only:** Dynamic data (catalog pricing, stock levels, order delivery stages, complaint protocols) is never hardcoded in prompt instructions; the agent must invoke the database tools to retrieve up-to-date facts.
  - **Deterministic Business Arithmetic:** Complex business logic—such as the 5% PIX discount on non-promotional items (§6.2), installment brackets (§3.1), and return eligibility windows (§4.1, §4.2, §8.1)—is calculated in Python/SQL code, eliminating arithmetic hallucinations.

#### 2.2 Framework Selection: LangGraph & Hybrid ReAct:
LangGraph was selected because it provides a structured, cyclic graph execution model (`StateGraph`) for agentic workflows:
- **Decoupled Architecture:** Clean separation between the reasoning node (`agent`), execution node (`ToolNode`), and conditional edge routing (`tools_condition`).
- **Future-Proofing Without Paradigm Shifts:** Future business requirements—such as human-in-the-loop approvals for refunds or specialized multi-agent subgraphs—can be plugged directly into the existing graph as new nodes and edges without rewriting the core engine.
- **Mitigating Vendor Lock-in:** Decoupled business logic from proprietary provider SDK types (`types.Content`), establishing standardized message schemas (`HumanMessage`, `AIMessage`, `ToolMessage`) compatible with any backend model.
- **Native Observability:** Out-of-the-box integration with tracing frameworks (such as LangSmith) enables granular inspection of latency, token consumption, and tool execution states.

#### 2.3 Model & Provider: Gemini 3.5 Flash-Lite via Google AI Studio:
- **Conversational Latency:** Customer service chatbots require responsive interaction on messaging apps. In local testing, Gemini 3.5 Flash-Lite showed indicative response times of ~1.0s for raw text generation and ~4.5s for complete multi-step tool execution loops.
- **Reliable Tool Calling:** Adheres accurately to Pydantic/JSON schemas for database filters, product IDs, and policy slugs without hallucinating arguments.
- **Frictionless Onboarding for Evaluators and Colleagues:** Because Google accounts are universally adopted, any reviewer or collaborator can generate an API key in under 60 seconds on Google AI Studio without credit card registration or billing hurdles.
- **Economic Production Scaling:** High free-tier quotas and cost-effective production token pricing make it viable for high-volume customer service.

#### 2.4 Dual Interface Strategy (CLI + Streamlit Web UI):
- **Terminal CLI (`main.py`):** Tailored for developers and automated workflows. Features Rich formatting, real-time status spinners, and a built-in `/export` command that saves conversations directly into Markdown files for automated auditing.
- **Streamlit Web UI (`app.py`):** Tailored for business presentations and user testing. Simulates a realistic WhatsApp web experience, complete with customer avatars, responsive chat bubbles, and an animated musical equalizer during model generation.

#### 2.5 Conversation History Persistence (LangGraph `MemorySaver`):
- Replaced unindexed in-memory Python lists with LangGraph's structured `MemorySaver` checkpointing isolated by `thread_id`.
- In a production environment with horizontally scaled WhatsApp webhook workers, transitioning to persistent storage (such as `PostgresSaver` or `RedisSaver`) is a localized change (checkpointer swap and connection configuration) requiring no changes to the agent graph.

#### 2.6 Data Treatment & Retrieval Architecture (Relational SQLite + Direct Native PDF):
- **Relational Foundation with SQLite:** The operational CSVs are ingested into SQLite tables at startup. Choosing SQLite establishes a true relational database paradigm (structured schemas, relational `JOINs` across orders, customers, items, and promotions, and parameterized queries). This makes migrating to an enterprise relational engine (such as PostgreSQL) straightforward in the future, while offering immediate local execution with no server dependencies or container setup.
- **Deterministic Financial Calculations over Raw Data:** In the raw CSV data, only base prices (`price_brl`) and active discount percentages are stored; there are no precomputed PIX prices or installment breakdowns. Our data layer combines catalog prices with store policies (§3.1 and §6.2) in Python/SQL, passing exact precalculated fields (`pix_price` and `installment_text`) to the agent.
- **Direct PDF Ingestion Without Lossy Transformation:** The store policy manual (`data/políticas_da_loja.pdf`) is an 8-page document (~1,680 words). Its text is extracted using `pypdf` at startup. Embedding the full summary directly into the prompt context (~3k tokens, estimate) provides complete normative grounding without the complexity, chunk boundary truncations, or retrieval misses of a vector database.

#### 2.7 Prompt Strategy & Conversational Guardrails:
The system prompt in `src/prompt.py` is engineered around WhatsApp conversational patterns:
- **Mobile-Friendly Readability:** Concise responses (2 to 3 short paragraphs) with bullet items (`•`) placed on separate lines for quick visual scanning on mobile screens.
- **Dynamic Temporal Context:** Injects the local store clock (`America/Campo_Grande`), enabling the agent to know whether the physical store is currently open, closed, or observing a national holiday.
- **Factual Grounding & Anti-Hallucination:** All prices, stock counts, and installment plans must come verbatim from tool responses; calculations are handled deterministically in code.
- **Firm Scope Boundaries:** Inquiries regarding accessories (strings, cables, picks, pedals, amplifiers) or general non-music topics are politely declined, redirecting customers to local partner shops.
- **Customer Privacy Protection:** Order lookup requiring customer verification (Order ID + email or phone) is a project design decision inspired by LGPD data minimization principles, while manual §9 specifically covers marketing consent and deletion requests. Public tracking code lookups remain unauthenticated per courier industry conventions.

---

## 3. Known Limitations & Production Roadmap ("O Que Faria com Mais Tempo")

### 3.1 Current Known Limitations:
1. **In-Memory Checkpointing (`MemorySaver`):** Conversation state is tracked in RAM per process. Restarting the process resets thread history (ideal for isolated evaluation and testing, but requires distributed storage in horizontally scaled environments).
2. **In-Memory Complaint Storage:** Formal complaint tickets (`REC-AAAAMMDD-NNNN`) are recorded in an in-memory SQLite table during runtime. Restarting the process resets newly registered tickets.
3. **Absence of a Decoupled REST/WebSocket API:** The system currently runs via standalone interfaces (`main.py` CLI and `app.py` Streamlit). There is no headless HTTP API endpoint (e.g., FastAPI) to receive external webhooks or serve decoupled third-party frontends.
4. **Deterministic Tokenized Search:** Catalog lookup uses unaccented SQLite token search. While resolving plurals and accents ("violao" $\rightarrow$ "violões"), it does not perform semantic embeddings for subjective, poetic customer descriptions (e.g., *"um violão com som aveludado e vintage"*).
5. **Absence of Automated External Helpdesk Sync:** Customer complaints are recorded locally with an official protocol and 24-business-hour SLA (§7.3), but do not automatically emit webhook notifications or create Zendesk/Jira tickets.
6. **Synchronous Process Execution:** CLI and Streamlit run synchronously within single-worker environments without Celery/Redis queue workers for massive concurrent loads.
7. **Fixed Regional Calendar:** Evaluates Brazilian national holidays (such as Finados, Tiradentes, etc.) per the store closure policy (§2: "Domingos e Feriados: Fechado"), but lacks dynamic integration with local Campo Grande municipal holiday feeds.

---

### 3.2 Production Roadmap ("What I Would Do With More Time"):
1. **Decoupled REST API & Omnichannel Expansion (FastAPI):**
   - Build a high-performance **FastAPI microservice** exposing standardized endpoints (`POST /v1/chat`, `POST /v1/feedback`, `GET /v1/health`).
   - Enable plug-and-play integration with the store's official e-commerce web storefront (embeddable chat widget) and messaging platforms (Telegram Bot API and WhatsApp via Meta Cloud API / Twilio).
2. **Model Benchmarking, Cost Optimization & Fallback Redundancy:**
   - Conduct systematic benchmarking across compact and cost-effective models (e.g., Gemini 3.5 Flash-Lite alongside compact models from other providers via OpenRouter), evaluating the exact tradeoff between latency, token cost, and tool-calling accuracy.
   - Architect a dual-model resilience strategy (**Primary Model + Automatic Fallback**): the agent defaults to a fast, cost-effective model, automatically failing over to a secondary model (via OpenRouter or an extensible Provider Strategy interface) if rate limits (HTTP 429) or upstream outages (HTTP 503) occur.
3. **Persistent Hybrid Storage:**
   - Attach a persistent SQLite or PostgreSQL storage layer (`ATTACH DATABASE 'data/runtime/emporio_runtime.db'` or PostgreSQL in container), keeping catalog queries fast in memory while persisting complaints and conversation history to disk.
   - Maintain complaint lifecycle management (`open` $\rightarrow$ `reviewing` $\rightarrow$ `resolved`) through administrative tools without agent interference.
4. **Complaint Tracking Tool (`consultar_reclamacao`):**
   - Provide a customer-facing tool allowing customers to check ticket status on subsequent days by providing their protocol (`REC-AAAAMMDD-NNNN`) and registered email/phone.
5. **Helpdesk & CRM Integration:**
   - Dispatch automated asynchronous webhooks to ticketing platforms (Zendesk, Jira Service Management) upon complaint creation, dynamically calculating business-hour SLAs based on the store operating calendar.
6. **Hybrid Catalog Retrieval (SQL Filters + Dense Semantic Embeddings):**
   - Combine exact relational SQL filters (price caps, categories, stock availability) with lightweight semantic embeddings on product descriptions to understand subjective musical nuances.
7. **Continuous Turn-Level Evaluation in CI/CD:**
   - Implement an automated behavioral evaluation harness (using tools like LangSmith or DeepEval) to test tone consistency, guardrail integrity, and tool-call precision on every pull request.

---

## 4. Use of AI Coding Assistants & Engineering Workflow (Uso de Assistentes de Código)

As explicitly encouraged by Artefact:
> *"Uso de assistentes de código: caso faça uso de algum recurso de IA (Copilot, Claude, Cursor, etc.), explique qual a escolhida e como utilizou. Queremos entender o seu workflow. A depender de como a ferramenta tenha sido explorada, isso pode ser visto como um ponto positivo e não irá prejudicar a sua avaliação."*

### 4.1 Selected Tools & Specialized Roles:
- **Primary AI Pair Programmer & Architecture Engine: Google Antigravity (powered by Gemini 3.8 Flash)**  
  Enhanced with the **Superpowers** engineering framework (leveraging structured `brainstorming`, `writing-plans`, and `systematic-debugging` workflows) to guide system design, conceptual transposition, and implementation.
- **Independent External Reviewer: Claude Opus (Anthropic)**  
  Used as an independent external reviewer equipped with the challenge brief, policy manual, and datasets, auditing claims against the repository with concrete evidence under the persona of a Senior Applied AI Engineer evaluating the submission.

### 4.2 Engineering Methodology & Workflow:

1. **Multi-Input Intake & Superpowers Brainstorming:**  
   Before writing application code, all project materials were consolidated and cross-referenced in an exhaustive architectural brainstorming phase:
   - The official instruction email from Artefact.
   - The technical challenge specification guide (`desafio_tecnico_ai_eng_artefact.pdf`) with technical decisions table.
   - The store policy manual (`data/políticas_da_loja.pdf`).
   - The 6 operational CSV datasets (`categories`, `customers`, `products`, `orders`, `order_items`, `promotions`).  
   This structured intake produced a formal architectural specification and a phased implementation plan, identifying data inconsistencies, price divergences, and business edge cases upfront.

2. **Conceptual Transposition (TypeScript / Node.js $\rightarrow$ Idiomatic Python):**  
   As an engineer with primary fluency and production experience in **TypeScript, Node.js, and LangGraph.js**, I utilized Antigravity as an active pair programmer to transpose proven software engineering patterns into idiomatic Python 3.11+:
   - **Type Safety & Data Contracts:** TypeScript interfaces and Zod schemas $\rightarrow$ Pydantic v2 settings, typed tool schemas, and static type hints.
   - **Agent Orchestration:** LangGraph.js state machines and channels $\rightarrow$ Python LangGraph `StateGraph` with prebuilt `ToolNode` and `MemorySaver`.
   - **Standard Library Leverage:** Leveraging Python's built-in `sqlite3` for lightweight, dependency-free relational querying and `pypdf` for native document ingestion, replacing external ORMs or complex node-gyp bindings.

3. **Simulated Senior Evaluator Review Loop:**  
   At key delivery milestones, repository states were reviewed with Claude Opus acting as an independent external assessor:
   - Challenging edge cases in customer return windows (§4.1 vs. §4.2 vs. §8.1).
   - Verifying that PIX calculations faithfully obeyed the non-cumulative promotion rule (§6.2).
   - Auditing customer privacy under LGPD principles when handling order tracking.

4. **Test-Driven Verification:**  
   Domain logic, business rules, and guardrails were validated by tests written alongside each module, maintaining a passing test suite (26 unit tests) throughout all architectural iterations.

5. **Transparent Audit Trail:**  
   A complete chronological record of AI collaboration, prompts, and design breakthroughs is preserved in [`docs/ai_workflow_log.md`](docs/ai_workflow_log.md).

---

## 5. Example Interactions & Non-Trivial Scenarios (Exemplos de Interação)

The repository contains recorded end-to-end interactions covering both standard and non-trivial complex scenarios:

1. 📄 [`examples/01_consulta_catalogo.md`](examples/01_consulta_catalogo.md): Acoustic guitars under R$ 1,000, stock checks, and calculation of the 5% PIX discount on non-promotional items.
2. 📄 [`examples/02_informacoes_loja_e_horarios.md`](examples/02_informacoes_loja_e_horarios.md): Physical store location (Rua 14 de Maio, 3200), national holiday closure notice for Finados (§2), and standard operating hours.
3. 📄 [`examples/03_status_e_rastreio_pedido.md`](examples/03_status_e_rastreio_pedido.md): Order lookup with LGPD verification (order ID #4 + customer email), returning delivery status and courier tracking code.
4. 📄 [`examples/04_fora_de_escopo_acessorios.md`](examples/04_fora_de_escopo_acessorios.md): Inquiries for strings, picks, and general knowledge (Moon landing), demonstrating scope boundaries and polite referral to local partners.
5. 📄 [`examples/05_cenario_nao_trivial_hibrido.md`](examples/05_cenario_nao_trivial_hibrido.md): **Non-trivial scenario**: Customer requesting return of historical Order #1 (Martin D-28) after expiration of the 7-day online repentance window, formal complaint registration with a single sequential protocol (`REC-20261102-0001`) and 24-business-hour SLA (§7.3), followed by practical guidance on manufacturer warranty and specialized luthier support for severe neck warping (§8.2).

---

## 6. Business Assumptions & Data Inconsistencies (Suposições e Tratamento de Dados)

During data audit and ingestion across the store CSV files and the policy manual, several real-world dataset inconsistencies were identified and handled deterministically:

1. **Order #3 Total vs. Items Sum:**
   - *Discrepancy:* `orders.csv` registers total R$ 3,450.00, whereas items sum to $2 \times \text{R\$} 1,749.00 = \text{R\$} 3,498.00$ (divergence of R$ 48.00).
   - *Decision:* The agent returns the official order invoice total recorded in the database while listing the itemized breakdown.
2. **Order #20 Total vs. Items Sum & Delivery Notes:**
   - *Discrepancy:* `orders.csv` registers total R$ 1,400.00, whereas items sum to $\text{R\$} 799.00 + \text{R\$} 689.00 = \text{R\$} 1,488.00$ (divergence of R$ 88.00).
   - *Decision:* Returns the order total and explicitly exposes the internal `notes` field (*"Endereço de entrega inválido informado pelo cliente"*) when verified by the customer.
3. **Product #130 (`Kala KA-ABP-CTG`) Status Discrepancy:**
   - *Discrepancy:* Product 130 is marked as `coming_soon` in `products.csv`, but appears in historical orders (Order #3 delivered and Order #14 pending).
   - *Decision:* The catalog tool respects `coming_soon` for active shopping recommendations, while order lookup accurately reports historical order items.
4. **Product Status vs. Stock Discrepancies:**
   - *Discrepancy:* Product #136 (`Ibanez Bass 2X`) is marked `discontinued` but has stock = 13. Product #96 (`Giannini GF-3D`) is marked `active` but has stock = 0.
   - *Decision:* Discontinued products are reported as discontinued regardless of warehouse stock; active products with stock 0 are reported as temporarily out of stock.
5. **Duplicate Customer Email (`bruno.martins@jmail.com`):**
   - *Discrepancy:* The same email is assigned to two distinct customer IDs (11 and 43).
   - *Decision:* As a design decision inspired by LGPD access control principles (while manual §9 specifically covers marketing consent and deletion requests), `consultar_pedido` requires `order_id` authenticated with customer email or phone, preventing ambiguous customer record lookups.
6. **PIX Payment in Historical Orders Without 5% Discount:**
   - *Discrepancy:* Some historical orders marked with payment method `pix` do not reflect the 5% cash discount in the `total_amount` column.
   - *Decision:* Historical transactions are reported as recorded. For active product inquiries, the 5% PIX price is calculated dynamically in code for non-promotional items.
7. **Promotions Without Expiration Dates & Inactive Duplicates:**
   - *Discrepancy:* `promotions.csv` has duplicate entries for products 93, 96, and 99. In the dataset, all duplicate rows have `is_active=0`, with only 4 active promotions overall (products 90, 94, 121, 127).
   - *Decision:* The database query filters `pr.is_active = 1`, ensuring only currently active discounts are applied to catalog pricing.
8. **Woodwinds and Orchestral Strings (Manual §1 vs. Sample Dataset):**
   - *Discrepancy:* Manual §1 states that the store catalog includes woodwinds and orchestral strings ("mais de 300 modelos entre guitarras, baixos, violões, baterias, teclados, instrumentos de sopro, cordas orquestrais e ukuleles"). However, the sample `products.csv` dataset provided for the challenge contains SKUs for 6 categories (1, 2, 3, 4, 5, and 9; with categories 6, 7, and 8 absent).
   - *Decision:* The agent clarifies that while the physical store works with these instruments, items in those categories are currently not available in the online catalog, inviting the customer to contact the store directly.
9. **Dual Store Phone Numbers:**
   - *Discrepancy:* Manual §1.2 lists `(67) 3341-4444` on the store header as "Telefone / WhatsApp", while the intro of §7 lists `(67) 3321-4500` as the dedicated WhatsApp customer service line.
   - *Decision:* Both numbers are preserved and provided in their respective contexts (general contact vs. returns/complaints).
10. **Installment Calculation Specificity:**
    - *Discrepancy:* Summary table mentions "minimum R$ 100 per installment", but §3.1 details gradual brackets: up to 3x without minimum installment (purchases below R$ 50 do not allow installments); 4–6x with minimum R$ 80; 7–12x with minimum R$ 100.
    - *Decision:* Implemented the specific and customer-friendly §3.1 rules directly in code (`src/database.py`).
11. **Absence of Temporal Reference in Static Datasets:**
    - *Discrepancy:* Historical `pending` and `shipped` orders have dispatch dates far in the past relative to the present day.
    - *Decision:* Dynamic `America/Campo_Grande` time is injected for store open/closed status, while order status is reported faithfully from database records.
12. **Estimated Delivery Date as Receipt Reference:**
    - *Discrepancy:* `orders.csv` does not have a separate `actual_delivery_date` column for completed shipments.
    - *Decision:* `estimated_delivery` is used as the receipt reference date for calculating the 7-day online repentance window (§4.1), 30-day defective exchange window (§4.2), and 90-day legal warranty (§8.1) relative to the current `America/Campo_Grande` clock. Defective exchange eligibility (§4.2) is thus counted from delivery date as an operational approximation.
13. **Fixed National Holidays Calendar (2026–2027):**
    - *Assumption:* Store hours (§2: "Domingos e Feriados: Fechado") evaluate Brazilian national holidays for 2026 and 2027 via a fixed calendar module without external dependencies. Carnaval and Corpus Christi are treated as closed in the calendar, reflecting standard retail observance despite legally being optional holidays (*pontos facultativos*). Municipal holidays of Campo Grande (e.g., August 26) are documented as future roadmap.
14. **Public Courier Tracking Code Access:**
    - *Assumption:* Per courier standards (Correios, Jadlog), searching directly by tracking code (`BR...`) returns shipment status without customer identity verification, while `order_id` queries require email or phone confirmation as a project privacy control inspired by LGPD access control principles (while manual §9 specifically governs marketing consent and data deletion requests).
15. **In-Memory Complaint Registration:**
    - *Assumption:* Complaints are registered into an in-memory SQLite table during process runtime (`REC-AAAAMMDD-NNNN` protocol, 24 business hours return time per §7.3). This represents a deliberate simplicity choice for the challenge prototype ("solve it in the simplest way possible"); persistent database attachment and ticketing integrations are detailed in §3 Roadmap.

---

## 7. Repository Structure (Estrutura do Repositório)

```
music-emporium/
├── data/                                # Original store datasets & policies
│   ├── *.csv                            # Categories, products, orders, customers, promotions
│   └── políticas_da_loja.pdf            # Official customer service manual
├── src/                                 # Core Python package
│   ├── __init__.py
│   ├── calendar_utils.py                # Brazilian national holidays & store hours engine
│   ├── config.py                        # Pydantic settings & environment validation
│   ├── database.py                      # SQLite in-memory store & parameterized queries
│   ├── knowledge.py                     # Direct PDF policy ingestion (pypdf) & structured policy lookup
│   ├── prompt.py                        # System prompt with musical persona & guardrails
│   ├── tools.py                         # Typed agent tool declarations
│   └── agent.py                         # Decoupled MusicStoreAgent engine
├── examples/                            # 5 recorded interaction logs (.md)
├── mockups/                             # Visual brainstorming mockups (HTML)
├── tests/                               # Comprehensive Pytest test suite (26 tests)
│   ├── test_calendar.py
│   ├── test_config.py
│   ├── test_database.py
│   ├── test_knowledge.py
│   ├── test_prompt.py
│   ├── test_tools.py
│   └── test_agent.py
├── docs/
│   ├── ai_workflow_log.md               # Detailed AI collaboration log
│   └── superpowers/                     # Architecture specs & implementation plans
├── scripts/
│   ├── check_examples.py                # Automated verifier for example files
│   ├── eval_cenarios.py                 # Smoke tests for conversational scenarios
│   └── generate_examples.py             # Official example generator
├── main.py                              # Interactive CLI runner (Rich)
├── app.py                               # Web UI runner (Streamlit)
├── pyproject.toml / requirements.txt    # Modern dependency management
└── README.md                            # Complete documentation
```
