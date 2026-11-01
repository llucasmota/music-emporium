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
3. **Strict Business Boundary Guardrails:** Firmly and politely declining out-of-scope inquiries (accessories such as strings, cables, picks, effect pedals, and amplifiers), redirecting customers to local partner stores.
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
                │ - Parameterized Catalog/Order│                           │ - 100% Deterministic Terms   │
                │   Queries (`data/*.csv`)     │                           │   (`políticas_da_loja.pdf`)  │
                └──────────────────────────────┘                           └──────────────────────────────┘
```

### Key Architectural Strengths:
- **Clean Decoupling:** `MusicStoreAgent` operates as a standalone domain service. It has zero coupling with the presentation layer; swapping the CLI or Streamlit for an official WhatsApp Business Cloud API webhook requires zero modifications to the core engine.
- **Zero Hallucination Guarantee:** The agent is forbidden from assuming prices or stock quantities. Ground-truth data is retrieved directly from relational queries and injected into the prompt context.
- **Graceful Degradation with Musical Metaphors:** When technical issues occur (e.g., connectivity drops), the agent remains fully in character using musical metaphors (*"Oops, sounds like our cable had a loose connection! Let me tune this up—can you resend that message in a minute?"*) while developer logs capture the full stack trace when `DEBUG_MODE=true`.

---

## 3. Technical Decisions & Strategic Rationale

| Architectural Decision | Chosen Implementation | Justification & Rationale |
| :--- | :--- | :--- |
| **Language** | **Python 3.11+** | Required by Artefact. Implemented with modern static typing, Pydantic configuration schemas, and clean packaging. |
| **LLM Provider & Model** | **Google Gemini (`gemini-3.5-flash-lite`)** via `langchain-google-genai` | Ultra-low latency (~1.0s raw, ~4.5s full LangGraph ReAct loop with tools), zero quota throttling on free tier, high accuracy on tool arguments, and cost-effective production scaling. |
| **Agent Orchestration** | **LangGraph StateGraph (`langgraph`)** | Directly aligns with Artefact's core stack. StateGraph with `ToolNode` to isolate SQLite and policy tools, conditional routing via `tools_condition`, and thread checkpointing using `MemorySaver`. |
| **Data Layer** | **SQLite In-Memory (`sqlite3` built-in)** | Zero heavyweight dependencies (avoids pandas bloat); sub-millisecond startup ingestion; supports relational JOINs across customers, orders, items, and promotions; parameterized queries eliminate SQL injection risks. |
| **Store Policies (PDF)** | **In-Context Structured Knowledge + Topic Retrieval Tool** | For an 8-page manual (~2,500 words / ~3,000 tokens), setting up a Vector Database (ChromaDB/FAISS) with embeddings is classic **over-engineering**. The structured in-context approach eliminates chunk fragmentation, reduces latency, and guarantees 100% legal precision. |
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
4. *(Optional PowerShell Policy):* If PowerShell displays an execution policy restriction when activating `.venv`, run PowerShell as Administrator and execute:
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

The test suite covers configuration, SQLite ingestion, catalog filtering, orders joins, policy extraction, prompt constraints, and agent state management:

```bash
pytest -v
```

Expected output:
```text
tests/test_agent.py::test_agent_initialization PASSED                    [  6%]
tests/test_agent.py::test_agent_history_reset PASSED                     [ 12%]
tests/test_agent.py::test_agent_export_markdown PASSED                   [ 18%]
tests/test_config.py::test_settings_load_defaults PASSED                 [ 25%]
tests/test_database.py::test_query_products_with_price_limit PASSED      [ 31%]
tests/test_database.py::test_query_product_details PASSED                [ 37%]
tests/test_database.py::test_query_order_by_id PASSED                    [ 43%]
tests/test_database.py::test_query_order_by_customer_name PASSED         [ 50%]
tests/test_knowledge.py::test_available_topics PASSED                    [ 56%]
tests/test_knowledge.py::test_get_policy_returns_accurate_terms PASSED   [ 62%]
tests/test_knowledge.py::test_store_summary_includes_crucial_guardrails PASSED [ 68%]
tests/test_prompt.py::test_system_prompt_contains_crucial_elements PASSED [ 75%]
tests/test_tools.py::test_buscar_produtos_tool PASSED                    [ 81%]
tests/test_tools.py::test_consultar_detalhes_produto_tool PASSED         [ 87%]
tests/test_tools.py::test_consultar_pedido_tool PASSED                   [ 93%]
tests/test_tools.py::test_consultar_politicas_tool PASSED                [100%]
============================== 16 passed in 0.50s ==============================
```

---

## 7. Example Interactions

The repository contains 6 recorded end-to-end interactions covering both standard and non-trivial complex scenarios:

1. 📄 [`examples/01_consulta_catalogo.md`](examples/01_consulta_catalogo.md): Acoustic guitars under R$ 1,000, stock checks, and calculation of the 5% PIX discount on non-promotional items.
2. 📄 [`examples/02_informacoes_loja_e_horarios.md`](examples/02_informacoes_loja_e_horarios.md): Physical store location, phone numbers, and weekend/holiday out-of-hours response handling.
3. 📄 [`examples/03_status_e_rastreio_pedido.md`](examples/03_status_e_rastreio_pedido.md): Real-time order lookup (Order #4) fetching tracking code, delivery status, and warranty explanation.
4. 📄 [`examples/04_fora_de_escopo_acessorios.md`](examples/04_fora_de_escopo_acessorios.md): Inquiries for strings, picks, pedals, and amps; demonstration of firm scope boundaries and polite referral to local partners.
5. 📄 [`examples/05_cenario_nao_trivial_hibrido.md`](examples/05_cenario_nao_trivial_hibrido.md): **Non-trivial scenario**: Customer requesting return of an online purchase under the 7-day repentance clause (free return shipping, 10-day refund) while simultaneously checking live stock and price for a higher-tier Takamine GD20 guitar to perform an exchange with price difference adjustment.
6. 📄 [`examples/06_interacao_real_guitarras_e_politicas.md`](examples/06_interacao_real_guitarras_e_politicas.md): **Real interactive evaluation dialogue**: Out-of-budget Floyd Rose search resolved via proactive two-tier suggestions, Fender Telecaster Player Series technical specs (vintage string-through fixed bridge), free shipping rules for Campo Grande, and detailed PIX 5% cash discount vs. 12x interest-free installments.

---

## 8. Use of AI Coding Assistants & Engineering Workflow

As encouraged by Artefact:
> *"Uso de assistentes de código: caso faça uso de algum recurso de IA (Copilot, Claude, Cursor, etc.), explique qual a escolhida e como utilizou. Queremos entender o seu workflow. A depender de como a ferramenta tenha sido explorada, isso pode ser visto como um ponto positivo e não irá prejudicar a sua avaliação."*

### The Workflow:
- **Pair Programming Paradigm:** As an engineer with a strong background in **TypeScript, Node.js, and LangGraph.js**, I leveraged **Antigravity (powered by Gemini 3.8)** as a Senior Engineering Coach & Pair Programmer.
- **Conceptual Transposition:** Rather than writing code blindly, the AI assisted in transposing mature architectural patterns from the TypeScript ecosystem (e.g., Zod schemas $\rightarrow$ Pydantic models; LangGraph state machines $\rightarrow$ native Python tool-calling loops; in-memory stores $\rightarrow$ native `sqlite3`).
- **Atomic TDD Discipline:** Every module was developed using strict Test-Driven Development (failing test $\rightarrow$ minimal code $\rightarrow$ passing test $\rightarrow$ atomic semantic git commit).
- **Comprehensive Workflow Log:** A dedicated log is tracked at [`docs/ai_workflow_log.md`](docs/ai_workflow_log.md).

---

## 9. Known Limitations & Future Roadmap ("What I Would Do With More Time")

While this project delivers an immediate, functional MVP satisfying 100% of the challenge specifications, here is the technical roadmap for production scale:

1. **Abstract LLM Provider Layer (`LLMProvider` Protocol):**
   - Introduce an abstract base class / protocol allowing seamless hot-swapping between Google Gemini, OpenAI (`gpt-4o-mini`), and **OpenRouter** to dynamically route requests based on cost, token limits, and throughput benchmarks.
2. **Hybrid Vector Search for Massive Catalogs:**
   - If the catalog scaled from 64 to 100,000+ SKUs, SQLite `LIKE` queries would be replaced with `pgvector` or an embedded vector store (Chroma/Qdrant) combining semantic search with BM25 keyword filtering (Hybrid Search).
3. **Omnichannel Headless Deployment (WhatsApp, Telegram & Embeddable Web Widget):**
   - Expose a decoupled asynchronous FastAPI service with native webhook connectors for **WhatsApp Business Cloud API** (Meta Graph API with HMAC verification) and **Telegram Bot API**.
   - Provide an embeddable web chat widget (`<script src="emporio-chat.js">`) with Server-Sent Events (SSE) streaming for third-party e-commerce storefronts.
   - Unify customer identity across channels (phone, email) against the `customers` database to enable persistent cross-session memory and tailored recommendations.
4. **Evaluation Harness (LLM-as-a-Judge):**
   - Implement an automated regression test suite using Ragas or DeepEval to score persona tone adherence, tool-calling precision, and hallucination rates across synthetic dialogue batches.

---

## 10. Repository Structure

```
music-emporium/
├── data/                                # Original store datasets & policies
│   ├── *.csv                            # Categories, products, orders, customers, promotions
│   └── políticas_da_loja.pdf            # Official customer service manual
├── src/                                 # Core Python package
│   ├── __init__.py
│   ├── config.py                        # Pydantic settings & environment validation
│   ├── database.py                      # SQLite in-memory store & parameterized queries
│   ├── knowledge.py                     # Structured store policy extraction
│   ├── tools.py                         # Typed agent tool declarations
│   ├── prompt.py                        # System prompt with musical persona & guardrails
│   └── agent.py                         # Decoupled MusicStoreAgent engine
├── examples/                            # 6 real interaction logs (.md)
├── mockups/                             # Visual brainstorming mockups (HTML)
├── tests/                               # Comprehensive Pytest test suite
│   ├── test_config.py
│   ├── test_database.py
│   ├── test_knowledge.py
│   ├── test_tools.py
│   ├── test_prompt.py
│   └── test_agent.py
├── docs/
│   ├── ai_workflow_log.md               # Detailed AI collaboration log
│   └── superpowers/                     # Architecture specs & implementation plans
├── main.py                              # Interactive CLI runner (Rich)
├── app.py                               # Web UI runner (Streamlit)
├── pyproject.toml / requirements.txt    # Modern dependency management
└── README.md                            # Complete documentation (in English)
```
