# Design Specification: Agente de Atendimento Empório da Música

- **Projeto:** Desafio Técnico AI Engineer – Full-Stack para Aplicações com IA Generativa (Artefact)
- **Candidato:** Lucas Mota
- **Data:** 31 de Outubro de 2026
- **Status:** Aprovado para Implementação

---

## 1. Visão Geral e Objetivos do Produto

A **Empório da Música** é uma loja especializada em instrumentos musicais localizada em Campo Grande/MS. O objetivo é desenvolver um assistente conversacional inteligente em Python para atuar no atendimento ao cliente (simulando canal WhatsApp), reduzindo a sobrecarga da equipe humana em dúvidas recorrentes e consultas de catálogo, pedidos e políticas da loja.

### Principais Objetivos:
1. **Persona & Tom de Voz:** Atendimento amigável, informal mas profissional, caloroso, apaixonado por música ("um amigo músico experiente").
2. **Acesso Determinístico a Dados:** Consulta precisa a catálogo de produtos, estoque, especificações técnicas e status de pedidos via ferramentas tipadas contra banco relacional em memória.
3. **Aplicação Fiel de Políticas:** Orientações transparentes sobre direitos do consumidor, prazos de devolução/troca, fretes e formas de pagamento sem alucinações.
4. **Fronteira Rígida de Escopo:** Recusa cordial de itens não comercializados pela loja (acessórios como cordas avulsas, palhetas, cabos, amplificadores e pedais), redirecionando para lojas parceiras.
5. **Arquitetura Desacoplada com Dupla Interface:** Suporte a CLI interativa (com Rich) para desenvolvedores/avaliação rápida e Web UI (com Streamlit) para stakeholders de produto e demonstrações para clientes.

---

## 2. Decisões Técnicas e Justificativas Estratégicas

| Decisão Técnica | Escolha Adotada | Justificativa Estratégica |
| :--- | :--- | :--- |
| **Linguagem Principal** | **Python 3.11+** | Requisito obrigatório único do edital. Estruturação moderna com *type hints* e Pydantic. |
| **Provedor e Modelo LLM** | **Google Gemini (`gemini-2.5-flash`)** via SDK oficial `google-genai` | Minimiza variabilidade estocástica de comportamento com modelo único e testado; latência ultra-baixa; excelente suporte nativo a Function Calling; facilidade de execução pelo avaliador (chave gratuita em 60s). Roadmap futuro documentado para suporte multi-modelo (OpenRouter) via interface abstrata. |
| **Orquestração do Agente** | **Loop Nativo de Tool-Calling / ReAct Leve** | Simplicidade extrema e código 100% auditável sem caixas-pretas de frameworks pesados (LangGraph/LangChain). Controle determinístico sobre execução de ferramentas e retenção de memória na sessão. |
| **Camada de Dados Operacionais** | **SQLite in-memory (`sqlite3` nativo)** | Zero dependências externas de dados (sem pandas). Ingestão instantânea dos 6 CSVs no startup. Suporte a JOINs relacionais entre pedidos, clientes e promoções. Acesso via tools parametrizadas (evitando Text-to-SQL aberto). |
| **Manual de Políticas (PDF)** | **In-Context Structured Knowledge + Tool de Consulta Temática** | O manual possui apenas 8 páginas (~2.500 palavras / ~3.000 tokens). Implementar banco vetorial completo (ChromaDB/FAISS) seria over-engineering desnecessário. A base estruturada no contexto com tool temática garante 100% de precisão e zero fragmentação de cláusulas. |
| **Interfaces de Usuário** | **Dupla Interface: CLI (Rich) + Web UI (Streamlit)** | Desacoplamento arquitetural: CLI rápida (`main.py`) com comando `/export` para desenvolvedores, e Web UI (`app.py`) simulando WhatsApp para clientes e stakeholders de negócio. |
| **Tratamento de Erros & Persona** | **Metáforas Musicais + Modo Debug** | Em produção/cliente, erros inesperados usam metáforas amigáveis da cultura musical ("corda que arrebentou", "cabo com mau contato"). Em modo `DEBUG_MODE=true`, logs e tracebacks técnicos completos são exibidos para desenvolvedores. |

---

## 3. Arquitetura do Sistema e Fluxo de Dados

### 3.1 Diagrama de Arquitetura

```
                     ┌──────────────────────────────────────────────┐
                     │           Camada de Apresentação             │
                     │  CLI Interativa (Rich)  |  Web UI (Streamlit)│
                     └──────────────────────┬───────────────────────┘
                                            │ Mensagem do Usuário
                                            ▼
                     ┌──────────────────────────────────────────────┐
                     │      MusicStoreAgent (src/agent.py)          │
                     │  - Gerenciamento de Histórico (Memória)      │
                     │  - System Prompt com Persona & Guardrails    │
                     │  - Loop de Execução de Tools (google-genai)  │
                     └──────────────┬───────────────────────────────┘
                                    │ Tool Calls
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
       ┌─────────────────────────┐     ┌─────────────────────────┐
       │   database.py (SQLite)  │     │   knowledge.py (PDF)    │
       │ - buscar_produtos       │     │ - consultar_politicas   │
       │ - consultar_detalhes    │     │   (trocas, devoluções,  │
       │ - consultar_pedido      │     │    fretes, pagamentos,  │
       │ (Dados de CSVs)         │     │    garantias, horários) │
       └─────────────────────────┘     └─────────────────────────┘
```

### 3.2 Estrutura de Diretórios
```
artifact-project/
├── data/                                # Dados originais fornecidos pela loja
│   ├── *.csv                            # Tabelas relacionais
│   └── políticas_da_loja.pdf            # Manual interno
├── src/
│   ├── __init__.py
│   ├── config.py                        # Variáveis de ambiente e constantes
│   ├── database.py                      # Ingestão CSV -> SQLite & consultas
│   ├── knowledge.py                     # Extração e estruturação de políticas
│   ├── tools.py                         # Declaração das 4 tools tipadas
│   ├── prompt.py                        # System Prompt, persona e guardrails
│   └── agent.py                         # Orquestrador do agente (Loop Nativo)
├── examples/                            # 5 conversas reais registradas em Markdown
├── mockups/                             # Mockups visuais criados no planejamento
├── tests/                               # Testes unitários automatizados com pytest
│   ├── test_database.py
│   ├── test_knowledge.py
│   └── test_tools.py
├── docs/
│   ├── ai_workflow_log.md               # Log de colaboração e uso de IA
│   └── superpowers/specs/...
├── main.py                              # Entrypoint da CLI Interativa
├── app.py                               # Entrypoint da Web UI (Streamlit)
├── pyproject.toml / requirements.txt
└── README.md                            # Documentação completa em INGLÊS
```

---

## 4. Especificação dos Componentes

### 4.1 Ingestão e Banco de Dados (`src/database.py`)
No startup:
- Inicializa banco SQLite em memória.
- Cria tabelas tipadas: `categories`, `products`, `promotions`, `customers`, `orders`, `order_items`.
- Carrega e normaliza os dados dos arquivos CSV em `data/`.
- Fornece funções de consulta seguras e parametrizadas:
  - `query_products(search_term, category, max_price)` com verificação de promoção ativa e cálculo de preço com desconto.
  - `query_product_details(product_id_or_name)` com decodificação do campo `specs` (JSON).
  - `query_order(order_id, customer_query)` com JOIN em `order_items` e `products`.

### 4.2 Base de Conhecimento de Políticas (`src/knowledge.py`)
- Lê e indexa as 8 páginas de `data/políticas_da_loja.pdf`.
- Divide e estrutura as regras de negócio por tópicos chave:
  - `trocas_devolucoes`: Arrependimento em 7 dias (compras online, frete pago pela loja); trocas por defeito em até 30 dias na loja; exceções (boquilhas de sopro, venda final).
  - `formas_pagamento`: PIX (5% off sobre tabela, não cumulativo com promoções); Cartão até 12x sem juros; boleto em 3 dias úteis.
  - `frete_entregas`: Campo Grande (grátis acima de R$ 500, taxa fixa R$ 35 abaixo; 1-3 dias úteis); Outras cidades (Correios PAC/SEDEX, Jadlog).
  - `horario_funcionamento`: Seg-Sex 09h às 18h, Sáb 09h às 13h, Dom/Feriados fechado.
  - `garantia`: 90 dias legal (CDC); 6 meses a 2 anos fabricante. Exclusões de desgaste natural.
  - `sobre_a_loja`: Fundada em 2008, Campo Grande/MS, foco exclusivo em instrumentos.
- Função `get_policy(topic: str) -> str`.

### 4.3 Ferramentas do Agente (`src/tools.py`)
Declaração de 4 ferramentas tipadas com docstrings detalhadas:
1. `buscar_produtos(termo: str = None, categoria: str = None, preco_maximo: float = None) -> list[dict]`
2. `consultar_detalhes_produto(identificador: str) -> dict`
3. `consultar_pedido(numero_pedido: int = None, termo_cliente: str = None) -> dict`
4. `consultar_politicas(topico: str) -> str`

### 4.4 Persona e System Prompt (`src/prompt.py`)
- **Persona:** Especialista de atendimento da Empório da Música.
- **Tom de Voz:** Informal, amigável, entusiasmado com música ("amigo experiente que toca e entende"), acolhedor e transparente.
- **Entusiasmo Musical Genuíno:** Comemora o início da jornada musical do cliente ou ajuda a encontrar o timbre/instrumento perfeito.
- **Guardrails:**
  - Recusa educada de acessórios (cordas avulsas, palhetas, amplificadores, cabos, pedais, cases).
  - Consulta obrigatória às ferramentas antes de declarar preço, estoque ou status de pedido.
  - Aplicação estrita de regras de não-cumulatividade de promoções com desconto PIX.

### 4.5 Resiliência e Tratamento de Erros
- **Startup Check:** Validação de `GEMINI_API_KEY`. Se ausente, aviso claro no terminal instruindo a configuração no `.env`.
- **Modo Debug (`DEBUG_MODE=true`):** Exibe logs técnicos, chamadas de tools e tracebacks no terminal para desenvolvedores.
- **Modo Cliente (`DEBUG_MODE=false`):** Mensagens humanizadas com metáforas musicais:
  - Falha de conexão: *"Ops! Parece que nosso cabo deu um pequeno mau contato aqui na linha. Me manda essa mensagem de novo em um minutinho pra gente afinar a conversa?"*
  - Falha inesperada: *"Putz, arrebentou uma corda da guitarra aqui no meio do solo! 🎸 Já estamos afinando as coisas por aqui. Pode tentar novamente em instantes?"*

---

## 5. Estratégia de Testes e Casos de Avaliação

### 5.1 Testes Unitários (`tests/`)
- `test_database.py`: Ingestão dos CSVs, contagem de registros, busca de violões com teto de preço, join de pedidos.
- `test_knowledge.py`: Extração e mapeamento dos tópicos de políticas.
- `test_tools.py`: Invocação das funções e validação do formato de retorno (JSON estruturado).

### 5.2 Conversas de Exemplo Registradas (`examples/`)
1. **01_consulta_catalogo.md:** Busca por violões até R$ 1.000 com aplicação de regras de estoque e desconto PIX.
2. **02_status_pedido.md:** Rastreamento de pedido existente informando código de envio e previsão.
3. **03_politica_devolucao.md:** Dúvida sobre devolução por arrependimento e prazos legais do CDC.
4. **04_fora_de_escopo_acessorios.md:** Tentativa de compra de palhetas e amplificador, com recusa cordial e redirecionamento.
5. **05_cenario_nao_trivial_hibrido.md:** Cliente pergunta sobre troca de violão já entregue combinado com consulta de novo instrumento.

---

## 6. Documentação do Workflow de IA (`docs/ai_workflow_log.md`)
Registro transparente do papel da IA no desenvolvimento:
- Uso do Antigravity como Coach e Pair Programmer.
- Transposição guiada da bagagem prévia em TypeScript/LangGraph para padrões modernos e idiomáticos em Python.
- Engenharia de prompts e design orientado a testes.
