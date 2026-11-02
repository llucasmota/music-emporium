# 🎸 Music Emporium — AI Customer Service Agent (`music-emporium`)

> **Artefact Technical Assessment — AI Engineer (Full-Stack para Aplicações com IA Generativa)**  
> **Candidate:** Lucas Mota  
> **Repository:** [https://github.com/llucasmota/music-emporium](https://github.com/llucasmota/music-emporium) (Public Repository)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Framework: LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Model: Gemini 3.5 Flash-Lite](https://img.shields.io/badge/LLM-Gemini%203.5%20Flash--Lite-4285F4.svg)](https://aistudio.google.com/)
[![Tests: Pytest](https://img.shields.io/badge/Tests-16%2F16%20Passing-success.svg)](https://docs.pytest.org/)
[![UI: Rich & Streamlit](https://img.shields.io/badge/UI-CLI%20%2B%20Streamlit-FF4B4B.svg)](https://streamlit.io/)

---

## 1. Project Overview & Business Scenario

**Empório da Música** is a traditional musical instruments store founded in 2008 in **Campo Grande, Mato Grosso do Sul**. While the store takes pride in its warm, community-driven reputation (*"Sua música começa aqui"*), the customer service team is currently overwhelmed by high volumes of recurring inquiries via WhatsApp: opening hours, catalog pricing, order tracking, real-time stock availability, and return/warranty policies.

This project delivers an autonomous, production-grade **AI Customer Service Agent in Python**, capable of:
1. **Embodying the Store Persona:** Informal, friendly, technically knowledgeable, and genuinely enthusiastic about music ("an experienced musician friend behind the counter").
2. **Context-Aware Dynamic Routing:** Deterministically querying operational databases (stock, specs, prices, order status) and store policies (7-day online repentance, warranties, payment terms) using typed tool-calling.
3. **Firm Business Boundary Guardrails:** Firmly and politely declining out-of-scope inquiries (accessories such as strings, cables, picks, effect pedals, and amplifiers), redirecting customers to local partner stores.
4. **Clean Architecture & Dual Presentation:** Providing an interactive terminal CLI (`main.py`) for developers and automated testing, alongside a WhatsApp-styled Web UI (`app.py`) for stakeholders.

---

## 2. Architecture & Design Principles

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
                               │  - ReAct ToolNode with SQLite & Policies                 │
                               └────────────────────────────┬─────────────────────────────┘
                                                            │ Typed Function Calls
                               ┌────────────────────────────┴─────────────────────────────┐
                               ▼                                                          ▼
                ┌──────────────────────────────┐                           ┌──────────────────────────────┐
                │   Database Engine (`src/db`) │                           │ Knowledge Engine (`src/know`)│
                │ - In-Memory SQLite Store     │                           │ - Structured Policy Sections │
                │ - Parameterized Catalog/Order│                           │ - Deterministic Policy Terms │
                │   Queries (`data/*.csv`)     │                           │   (`políticas_da_loja.pdf`)  │
                └──────────────────────────────┘                           └──────────────────────────────┘
```

### Key Architectural Strengths:
- **Clean Decoupling:** `MusicStoreAgent` operates as a standalone domain service. It has minimal coupling with the presentation layer; swapping the CLI or Streamlit for an official WhatsApp Business Cloud API webhook requires no modifications to the core engine.
- **Ground-Truth Retrieval & Anti-Hallucination Guardrails:** The agent is programmatically constrained from inventing prices, stock, or policies. Ground-truth data is retrieved directly from relational queries and injected into the prompt context to prevent hallucinations.
- **Graceful Degradation with Musical Metaphors:** When technical issues occur (e.g., connectivity drops), the agent remains fully in character using musical metaphors (*"Oops, sounds like our cable had a loose connection! Let me tune this up—can you resend that message in a minute?"*) while developer logs capture the full stack trace when `DEBUG_MODE=true`.

---

## 3. Technical Decisions & Strategic Rationale

| Architectural Decision | Chosen Implementation | Justification & Rationale |
| :--- | :--- | :--- |
| **Language** | **Python 3.11+** | Required by Artefact. Implemented with modern static typing, Pydantic configuration schemas, and clean packaging. |
| **LLM Provider & Model** | **Google Gemini (`gemini-3.5-flash-lite`)** via `langchain-google-genai` | Ultra-low latency (~1.0s raw, ~4.5s full LangGraph ReAct loop with tools), generous free-tier throughput, high accuracy on tool arguments, and cost-effective production scaling. |
| **Agent Orchestration** | **LangGraph StateGraph (`langgraph`)** | Directly aligns with Artefact's core stack. StateGraph with `ToolNode` to isolate SQLite and policy tools, conditional routing via `tools_condition`, and thread checkpointing using `MemorySaver`. |
| **Data Layer** | **SQLite In-Memory (`sqlite3` built-in)** | No external database dependencies (avoids pandas overhead); sub-millisecond startup ingestion; supports relational JOINs across customers, orders, items, and promotions; parameterized queries eliminate SQL injection risks. |
| **Store Policies (PDF)** | **In-Context Structured Knowledge + Topic Retrieval Tool** | For an 8-page manual (1,787 words / ~2,200 tokens), setting up a Vector Database (ChromaDB/FAISS) with embeddings is classic **over-engineering**. The structured in-context approach eliminates chunk fragmentation, reduces latency, and promotes policy adherence without vector database complexity. |
| **Interface Strategy** | **Dual Mode: CLI (Rich) + Web UI (Streamlit)** | Solves both evaluation and product needs: developer-friendly instant CLI execution (`main.py`) with `/export` command, alongside a visual WhatsApp-like experience (`app.py`) for non-technical business stakeholders. |

---

## 4. Getting Started & Running the Project

### 4.1 System Prerequisites & Python Installation Guide

This project requires **Python 3.11** or higher (tested across Python 3.11, 3.12, 3.13, and 3.14). If Python is not yet installed on your system, please follow the operating system instructions below:

#### 🪟 Windows Installation Guide
1. **Download:** Visit the official [Python Downloads for Windows](https://www.python.org/downloads/windows/) and download the latest stable installer (Python 3.11+).
2. **Install (Crucial Step):** Run the downloaded `.exe` installer. On the very first screen, **check the box: `"Add python.exe to PATH"`** before clicking *"Install Now"*.
3. **Verify:** Open **PowerShell** or **Command Prompt** and run:
   ```powershell
   python --version
   pip --version
   ```
4. *(Optional PowerShell Policy):* If PowerShell displays an execution warning when activating `.venv`, run PowerShell as Administrator and execute:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

#### 🍏 macOS Installation Guide
1. **Option A — Homebrew (Recommended):**
   Open Terminal and install Python 3.12:
   ```bash
   brew install python@3.12
   ```
2. **Option B — Official Universal Installer:**
   Download the macOS 64-bit universal installer from [Python Downloads for macOS](https://www.python.org/downloads/macos/). Run the package and double-click `Install Certificates.command` in `/Applications/Python 3.x/` upon completion.
3. **Verify:**
   ```bash
   python3 --version
   pip3 --version
   ```

#### 🐧 Linux Installation Guide (Ubuntu / Debian / Fedora / Arch)
1. **Ubuntu / Debian / Linux Mint:**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv
   ```
2. **Fedora / RHEL:**
   ```bash
   sudo dnf install -y python3 python3-pip
   ```
3. **Arch Linux / Manjaro:**
   ```bash
   sudo pacman -S python python-pip
   ```
4. **Verify:**
   ```bash
   python3 --version
   ```

---

### 4.2 Project Setup & Virtual Environment

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

### 4.3 Environment Configuration (`.env`)

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

## 5. Running the Agent

### Option A: Interactive Terminal CLI (Recommended for Fast Evaluation)

Launch the styled interactive CLI with real-time status spinners and conversation export:

```bash
python main.py
```

**CLI Commands:**
- `sua pergunta`: Type naturally in Portuguese.
- `/export [filename.md]`: Automatically exports the current dialogue to `examples/` in Markdown format.
- `/reset`: Clears session conversational memory.
- `/sair`: Exits the program.

### Option B: Web UI (Streamlit Chat with Musical Animation)

Launch the WhatsApp-styled web application featuring real-time musical equalizer animations:

```bash
streamlit run app.py
```
*The app will automatically open in your browser at `http://localhost:8501`.*

---

## 6. Running Automated Tests

The test suite covers configuration, SQLite ingestion, catalog filtering, orders joins, policy retrieval, prompt constraints, calendar/holidays, complaint registration, and agent state management:

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

### Conversational Verification & Smoke Tests

1. **Conversation Verifier (`scripts/check_examples.py`):**
   - Automatically inspects the recorded conversation files (`examples/*.md`), validating that quoted prices, stock counts, order numbers, and tracking codes correspond to database ground-truth within conversational blocks.
   - Enforces privacy checks (requiring email or phone authentication before revealing full customer names) and verifies that complaint confirmations include a valid protocol (`REC-AAAAMMDD-NNNN`).

2. **Behavioral Smoke Tests (`scripts/eval_cenarios.py`):**
   - Provides automated smoke test coverage across 11 key conversational flows (catalog budget limits, physical address, GD20 pricing, scope boundaries, general knowledge refusal, LGPD verification, and discontinued item notices). Detailed assertions verify objective boundaries; multi-turn comprehensive benchmark runs are documented in the roadmap.

---

## 7. Example Interactions

The repository contains recorded end-to-end interactions covering both standard and non-trivial complex scenarios:

1. 📄 [`examples/01_consulta_catalogo.md`](examples/01_consulta_catalogo.md): Acoustic guitars under R$ 1,000, stock checks, and calculation of the 5% PIX discount on non-promotional items.
2. 📄 [`examples/02_informacoes_loja_e_horarios.md`](examples/02_informacoes_loja_e_horarios.md): Physical store location (Rua 14 de Maio, 3200), national holiday closure notice for Finados (§2), and standard operating hours.
3. 📄 [`examples/03_status_e_rastreio_pedido.md`](examples/03_status_e_rastreio_pedido.md): Order lookup with LGPD verification (order ID #4 + customer email), returning delivery status and courier tracking code.
4. 📄 [`examples/04_fora_de_escopo_acessorios.md`](examples/04_fora_de_escopo_acessorios.md): Inquiries for strings, picks, and general knowledge (Moon landing), demonstrating scope boundaries and polite referral to local partners.
5. 📄 [`examples/05_cenario_nao_trivial_hibrido.md`](examples/05_cenario_nao_trivial_hibrido.md): **Non-trivial scenario**: Customer requesting return of historical Order #1 (Martin D-28) after expiration of the 7-day online repentance window, formal complaint registration with a single sequential protocol (`REC-20261102-0001`) and 24-business-hour SLA (§7.3), followed by practical guidance on manufacturer warranty and specialized luthier support for severe neck warping (§8.2).

---

## 8. Use of AI Coding Assistants & Engineering Workflow

As encouraged by Artefact:
> *"Uso de assistentes de código: caso faça uso de algum recurso de IA (Copilot, Claude, Cursor, etc.), explique qual a escolhida e como utilizou. Queremos entender o seu workflow. A depender de como a ferramenta tenha sido explorada, isso pode ser visto como um ponto positivo e não irá prejudicar a sua avaliação."*

### The Workflow:
- **Pair Programming Paradigm:** As an engineer with a strong background in **TypeScript, Node.js, and LangGraph.js**, I leveraged **Antigravity (powered by Gemini 3.8)** as a Senior Engineering Coach & Pair Programmer.
- **Conceptual Transposition:** Rather than writing code blindly, the AI assisted in transposing mature architectural patterns from the TypeScript ecosystem (e.g., Zod schemas $\rightarrow$ Pydantic models; LangGraph.js state machines $\rightarrow$ LangGraph Python StateGraph; in-memory stores $\rightarrow$ native `sqlite3`).
- **Test-Driven Specification & Comprehensive Automated Verification:** Test contracts and edge cases (pricing rules, privacy policies, catalog constraints) were designed upfront during the initial architectural specification phase. Tests were implemented alongside core domain modules, maintaining a consistently passing test suite (26 unit tests) across architectural iterations.
- **Comprehensive Workflow Log:** A dedicated log is tracked at [`docs/ai_workflow_log.md`](docs/ai_workflow_log.md).

---

## 9. Current Known Limitations & Future Roadmap ("What I Would Do With More Time")

### Current Known Limitations:
1. **In-Memory Checkpointing (`MemorySaver`):** Conversation state is tracked in RAM per session. Restarting the process resets thread history (ideal for stateless CLI/evaluations, but requires Redis or PostgreSQL checkpointers in distributed deployments).
2. **Deterministic Tokenized Search:** Catalog lookup uses unaccented SQLite token search. While resolving plurals and accents ("violao" $\rightarrow$ "violões"), it does not perform semantic embeddings for vague colloquial descriptions.
3. **Absence of Automated External Helpdesk Sync:** Customer complaints are recorded locally in the in-memory complaints table with sequential protocol, but do not automatically emit webhook notifications or create Zendesk/Jira tickets.
4. **Synchronous Process Execution:** CLI and Streamlit run synchronously within single-worker environments without Celery/Redis queue workers.

### Production Roadmap ("What I Would Do With More Time"):
1. **Persistent Complaint Storage:** SQLite file attached to the connection (`ATTACH DATABASE 'data/runtime/emporio_runtime.db' AS rt`), maintaining the operational catalog loaded in memory while persisting complaints to disk. Complaint lifecycle (`open` $\rightarrow$ `reviewing` $\rightarrow$ `resolved`) managed by store staff (no agent tool modifies complaint status). SLA calculation dynamically computing 24 business hours based on the store operating calendar (§2).
2. **Complaint Tracking Tool (`consultar_reclamacao`):** Customer-facing tool allowing status check via protocol + customer email verification.
3. **Helpdesk & CRM Integration:** Automated webhook/email notifications dispatched to the customer service team or direct integration with ticketing systems (Zendesk, Jira Service Management) upon complaint creation.
4. **Turn-Level Behavioral Evaluation:** Comprehensive eval harness evaluating individual dialogue turns, recording raw model payloads and tool calls, integrated into CI/CD pipelines.
5. **Pagination & Catalog Depth Notices:** Proactively informing the customer when additional items exist beyond the displayed top results (`total_count > len(items)`).
6. **Configurable Holiday Calendar:** Integration of municipal Campo Grande holidays (e.g., August 26) and configurable regional calendar feeds.

---

## 10. Assumptions & Data Inconsistencies

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
   - *Decision:* Per LGPD (§9), `consultar_pedido` requires `order_id` authenticated with email or phone, preventing ambiguous customer record lookups.
6. **PIX Payment in Historical Orders Without 5% Discount:**
   - *Discrepancy:* Some historical orders marked with payment method `pix` do not reflect the 5% cash discount in the `total_amount` column.
   - *Decision:* Historical transactions are reported as recorded. For active product inquiries, the 5% PIX price is calculated dynamically in code for non-promotional items.
7. **Promotions Without Expiration Dates & Inactive Duplicates:**
   - *Discrepancy:* `promotions.csv` has duplicate entries for products 93, 96, and 99. In the dataset, all duplicate rows have `is_active=0`, with only 4 active promotions overall (products 90, 94, 121, 127).
   - *Decision:* The database query filters `pr.is_active = 1`, ensuring only currently active discounts are applied to catalog pricing.
8. **Woodwinds and Orchestral Strings (Manual §1 vs. Sample Dataset):**
   - *Discrepancy:* Manual §1 states that the store catalog includes woodwinds and orchestral strings ("mais de 300 modelos entre guitarras, baixos, violões, baterias, teclados, instrumentos de sopro, cordas orquestrais e ukuleles"). However, the sample `products.csv` dataset provided for the challenge contains SKUs only for 5 categories (no products in categories 6, 7, or 8).
   - *Decision:* The agent clarifies that while the physical store works with these instruments, items in those categories are currently not available in the online catalog, inviting the customer to contact the store directly.
9. **Dual Store Phone Numbers:**
   - *Discrepancy:* Manual §1.2 lists `(67) 3341-4444` as the general store phone, while opening of §7.1 lists `(67) 3321-4500` as the dedicated WhatsApp customer service line.
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
    - *Assumption:* Per courier standards (Correios, Jadlog), searching directly by tracking code (`BR...`) returns shipment status without customer identity verification, while `order_id` queries require email or phone confirmation to protect customer privacy under LGPD (§9).
15. **In-Memory Complaint Registration:**
    - *Assumption:* Complaints are registered into an in-memory SQLite table during process runtime (`REC-AAAAMMDD-NNNN` protocol, 24 business hours return time per §7.3). This represents a deliberate simplicity choice for the challenge prototype ("solve it in the simplest way possible"); persistent database attachment and ticketing integrations are detailed in §9 Roadmap.

---

## 11. Repository Structure

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
│   ├── knowledge.py                     # Direct PDF policy ingestion (pypdf) & structured semantic engine
│   ├── prompt.py                        # System prompt with musical persona & guardrails
│   ├── tools.py                         # Typed agent tool declarations
│   └── agent.py                         # Decoupled MusicStoreAgent engine
├── examples/                            # 5 recorded interaction logs (.md)
├── mockups/                             # Visual brainstorming mockups (HTML)
├── tests/                               # Comprehensive Pytest test suite
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
└── README.md                            # Complete documentation (in English)
```
