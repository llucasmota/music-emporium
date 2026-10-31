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

## 3. Key Decisions Facilitated by AI Pair Programming

1. **Pragmatic MVP vs. Future Roadmap:**
   - *Current Decision:* Google Gemini 2.5 Flash via native `google-genai` SDK for frictionless setup, zero cost, and behavioral stability.
   - *Future Roadmap:* Abstract provider interface (`LLMProvider`) to dynamically route to OpenRouter models based on latency and cost.
2. **Framework Selection:**
   - Chose a **Native Tool-Calling Loop** over full LangGraph to avoid unnecessary complexity (*"solve it in the simplest way possible"*), maintaining full code explainability during technical interviews.
3. **Data Layer:**
   - Chose native `sqlite3` in-memory over `pandas` to keep dependencies minimal while supporting relational queries with parameters.
4. **Knowledge Retrieval:**
   - Chose in-context structured policies over vector embeddings (ChromaDB) to avoid over-engineering for an 8-page document, eliminating chunking fragmentation.
