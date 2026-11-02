# AI Collaboration & Engineering Workflow Log

- **Candidate:** Lucas Mota
- **Role:** AI Engineer – Full-Stack para Aplicações com IA Generativa (Artefact)
- **Primary Development Paradigm:** AI-Assisted Engineering & Pair Programming

---

## 1. Executive Summary

As an Applied AI Engineering student with strong production background in **TypeScript, Node.js, LangGraph.js, and Google Gemini APIs**, this project presented an exciting opportunity: delivering a production-grade AI Agent in **Python** within a tight timeframe while adhering to strict business rules and architectural simplicity.

Rather than hiding the use of AI tools, we embraced it fully as recommended in the Artefact test instructions:
> *"Uso de assistentes de código: caso faça uso de algum recurso de IA (Copilot, Claude, Cursor, etc.), explique qual a escolhida e como utilizou. Queremos entender o seu workflow. A depender de como a ferramenta tenha sido explorada, isso pode ser visto como um ponto positivo e não irá prejudicar a sua avaliação."*

---

## 2. The AI Engineering Workflow

### 2.1 Division of Responsibilities

| Dimension | Candidate (Lucas Mota) | AI Assistant (Antigravity) |
| :--- | :--- | :--- |
| **Architectural Vision** | Defined core principles, identified business trade-offs, chose Gemini Flash over multi-model chaos to ensure deterministic evaluation. | Suggested structural patterns, mapped LangGraph concepts to Python tool loops. |
| **Product Strategy** | Proposed the Dual Interface (CLI + Web UI) so both technical evaluators and business stakeholders could experience the product. | Generated visual mockups and comparison fragments for evaluation. |
| **UX & Personality** | Conceived the musical empathy ("entusiasmo musical") and musical metaphors for graceful error handling. | Formulated prompt constraints and system instruction structure. |
| **Language Transposition** | Validated typing, business logic, and behavioral correctness against challenge specifications. | Accelerated boilerplate generation in idiomatic Python (Pydantic, typing, sqlite3). |

---

## 3. Key Architectural Evolutions Facilitated by AI Pair Programming

### Phase 1 (31/10/2026): Initial Architectural Scaffolding & Pragmatic Prototype
- **Data Layer:** Selected native `sqlite3` in-memory over `pandas` to keep runtime dependencies lightweight while supporting relational `JOIN` queries across orders, items, and promotions with sanitized parameters.
- **Store Policies:** Chose in-context structured policies over vector embeddings (ChromaDB) to avoid over-engineering for an 8-page document, eliminating chunk fragmentation and latency overhead.
- **Initial Prototype:** Explored a minimal single-loop function-calling prototype to validate tool execution and error handling.

### Phase 2 (01/11/2026): Production Upgrade to LangGraph StateGraph & Model Optimization
- **LangGraph StateGraph Orchestration:**
  - Upgraded the agent core to a formal **LangGraph `StateGraph(MessagesState)`** with `ToolNode` and conditional routing via `tools_condition`.
  - *Reasoning:* The job description explicitly values experience with LangGraph. As the candidate already builds agents in TypeScript using LangGraph.js, translating this architecture to Python demonstrates advanced multi-paradigm mastery, state auditability, and clear separation between cognitive agent nodes and deterministic tool execution nodes.
  - Thread-level persistence was integrated natively using LangGraph's `MemorySaver` checkpointer.
- **Model Latency Benchmarking & Selection:**
  - *Initial Exploration:* Evaluated `gemini-3.8-flash` (heavy thinking latency) and legacy `gemini-2.5-flash` (deprecated endpoint on current API keys).
  - *Benchmarking Decision:* Standardized default on **`gemini-3.5-flash-lite`**, which delivered sub-second raw model latency and a ~4.5s end-to-end multi-step ReAct loop with zero rate-limit throttling on Google AI Studio's tier.
- **Conversational UX & Policy §7.3 Calibration:**
  - Implemented proactive two-tier suggestions (*bracketing*) when items fall outside the user's budget.
  - Enforced WhatsApp-style concise formatting, suppressed library-level warnings, and eliminated artificial conversational clichés.

### Phase 3 (02/11/2026): Rigorous External Review & Compliance Hardening
- **Deterministic Pricing (Manual §3.1 & §6.2):** Delegated PIX 5% discount (non-cumulative with promotions) and credit card installment calculations entirely to code, ensuring the LLM never hallucinates payment terms.
- **Privacy & LGPD (Manual §9):** Restricted order queries to require authentication (order ID + email/phone), preventing unauthorized access to customer records.
- **Real-Time Context:** Injected real-time Campo Grande date/time context on every conversational turn, making store hour verification dynamic.
