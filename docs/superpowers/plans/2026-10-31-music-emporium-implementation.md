# Music Emporium AI Customer Service Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-grade, conversational AI customer service agent in Python for "Empório da Música", featuring structured data queries via SQLite in-memory, deterministic policy retrieval, dual presentation layers (Interactive Rich CLI + Streamlit Web UI), and musical empathetic persona with graceful degradation.

**Architecture:** Clean Architecture separating presentation layers (`main.py` CLI and `app.py` Web UI) from the decoupled core engine (`MusicStoreAgent` in `src/agent.py`). The core orchestrates Gemini 2.5 Flash with a native tool-calling loop, accessing operational tabular data through parameterized SQLite queries (`src/database.py`) and store policies via structured in-context retrieval (`src/knowledge.py`).

**Tech Stack:** Python 3.11+, `google-genai` (official Google SDK), `sqlite3` (built-in standard library), `pydantic`, `rich` (CLI terminal styling), `streamlit` (Web UI), `pypdf` (PDF extraction), `pytest` (automated testing).

## Global Constraints

- Primary Language: Python 3.11+ with strict type hinting and Pydantic validation.
- All documentation, code comments, and final README must be in English (per Artefact requirements).
- Customer conversation language: Portuguese (pt-BR), as Empório da Música is based in Campo Grande/MS.
- Repository: Atomic semantic git commits for every step, no giant single commits.
- Business Boundary: The store exclusively sells musical instruments; all inquiries for accessories (strings, cables, picks, pedals, amps) must be politely redirected.
- Discounts: 5% PIX discount is strictly non-cumulative with promotional prices.

---

### Task 1: Environment Setup, Configuration & Dependencies

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `src/__init__.py`
- Create: `src/config.py`
- Test: `tests/test_config.py`

**Interfaces:**
- Consumes: Environment variables (`GEMINI_API_KEY`, `DEBUG_MODE`).
- Produces: `src.config.Settings` (Pydantic settings with `api_key`, `debug_mode`, `data_dir`, `db_path`).

- [ ] **Step 1: Write the failing test for configuration**

```python
# tests/test_config.py
import os
import pytest
from src.config import Settings

def test_settings_load_defaults(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key-12345")
    monkeypatch.setenv("DEBUG_MODE", "false")
    settings = Settings()
    assert settings.gemini_api_key == "test-api-key-12345"
    assert settings.debug_mode is False
    assert settings.model_name == "gemini-2.5-flash"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL (ModuleNotFoundError: No module named 'src.config')

- [ ] **Step 3: Implement dependencies and configuration module**

Create `pyproject.toml`:
```toml
[project]
name = "music-emporium"
version = "0.1.0"
description = "Empório da Música - AI Customer Service Agent"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "google-genai>=1.0.0",
    "pydantic>=2.7.0",
    "pydantic-settings>=2.2.0",
    "rich>=13.7.0",
    "streamlit>=1.35.0",
    "pypdf>=4.2.0",
    "python-dotenv>=1.0.1",
]

[dependency-groups]
dev = [
    "pytest>=8.2.0",
]
```

Create `requirements.txt`:
```txt
google-genai>=1.0.0
pydantic>=2.7.0
pydantic-settings>=2.2.0
rich>=13.7.0
streamlit>=1.35.0
pypdf>=4.2.0
python-dotenv>=1.0.1
pytest>=8.2.0
```

Create `.env.example`:
```bash
# Google Gemini API Key (Obtain free at https://aistudio.google.com/)
GEMINI_API_KEY=your_gemini_api_key_here

# Enable detailed developer logs and tracebacks (true/false)
DEBUG_MODE=false
```

Create `src/__init__.py`:
```python
"""Music Emporium AI Agent Package."""
```

Create `src/config.py`:
```python
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")
    model_name: str = "gemini-2.5-flash"
    
    # Project paths
    project_root: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = Path(__file__).resolve().parent.parent / "data"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml requirements.txt .env.example src/__init__.py src/config.py tests/test_config.py
git commit -m "chore: setup project dependencies, packaging and configuration module"
```

---

### Task 2: Data Ingestion & Relational SQLite Store (`src/database.py`)

**Files:**
- Create: `src/database.py`
- Test: `tests/test_database.py`

**Interfaces:**
- Consumes: CSV files in `data/` (`categories.csv`, `products.csv`, `promotions.csv`, `customers.csv`, `orders.csv`, `order_items.csv`).
- Produces:
  - `init_database(data_dir: Path = None) -> sqlite3.Connection`
  - `query_products(search_term: str = None, category: str = None, max_price: float = None) -> list[dict]`
  - `query_product_details(identifier: str) -> dict | None`
  - `query_order(order_id: int = None, customer_query: str = None) -> dict | None`

- [ ] **Step 1: Write failing tests for database queries**

```python
# tests/test_database.py
import pytest
from src.database import init_database, query_products, query_product_details, query_order

@pytest.fixture(scope="module")
def db():
    return init_database()

def test_query_products_with_price_limit(db):
    results = query_products(db, search_term="violão", max_price=1000.0)
    assert len(results) > 0
    for prod in results:
        assert prod["effective_price"] <= 1000.0
        assert prod["stock_quantity"] >= 0

def test_query_product_details(db):
    product = query_product_details(db, "Yamaha C40")
    assert product is not None
    assert "Yamaha C40" in product["name"]
    assert "specs" in product
    assert isinstance(product["specs"], dict)

def test_query_order_by_id(db):
    order = query_order(db, order_id=1)
    assert order is not None
    assert order["order_id"] == 1
    assert "items" in order
    assert len(order["items"]) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_database.py -v`
Expected: FAIL (ModuleNotFoundError: No module named 'src.database')

- [ ] **Step 3: Implement data ingestion and query engine in `src/database.py`**

```python
# src/database.py
import csv
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.config import settings

def _find_data_file(data_dir: Path, pattern: str) -> Optional[Path]:
    matches = list(data_dir.glob(f"*{pattern}*.csv"))
    if matches:
        return matches[0]
    return None

def init_database(data_dir: Optional[Path] = None) -> sqlite3.Connection:
    if data_dir is None:
        # Check both potential data directories (root/data or subdirectory)
        data_dir = settings.project_root / "data"
        if not data_dir.exists():
            data_dir = settings.project_root / "Desafio Técnico AI Engineer 2026" / "data"
            
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE categories (
            category_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            price_brl REAL NOT NULL,
            name TEXT NOT NULL,
            category_id INTEGER,
            description TEXT,
            stock_quantity INTEGER NOT NULL,
            status TEXT,
            specs TEXT,
            created_at TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (category_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE promotions (
            promotion_id INTEGER PRIMARY KEY,
            product_id INTEGER,
            discount_percent REAL NOT NULL,
            description TEXT,
            is_active INTEGER NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            city TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_date TEXT,
            status TEXT,
            total_brl REAL,
            payment_method TEXT,
            tracking_code TEXT,
            estimated_delivery TEXT,
            notes TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE order_items (
            order_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (order_id),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
    """)

    # Ingest CSVs
    mapping = {
        "categories": "categories",
        "products": "products",
        "promotions": "promotions",
        "customers": "customers",
        "orders": "orders",
        "order_items": "order_items"
    }

    for table, pattern in mapping.items():
        file_path = _find_data_file(data_dir, pattern)
        if file_path and file_path.exists():
            with open(file_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if rows:
                    columns = list(rows[0].keys())
                    placeholders = ", ".join(["?"] * len(columns))
                    col_names = ", ".join(columns)
                    insert_sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
                    
                    data_to_insert = []
                    for row in rows:
                        data_to_insert.append([row[col] if row[col] != "" else None for col in columns])
                    
                    cursor.executemany(insert_sql, data_to_insert)

    conn.commit()
    return conn

def query_products(
    conn: sqlite3.Connection,
    search_term: Optional[str] = None,
    category: Optional[str] = None,
    max_price: Optional[float] = None
) -> List[Dict[str, Any]]:
    query = """
        SELECT 
            p.product_id,
            p.name,
            p.price_brl AS original_price,
            c.name AS category_name,
            p.stock_quantity,
            p.description,
            pr.discount_percent,
            CASE 
                WHEN pr.is_active = 1 AND pr.discount_percent IS NOT NULL 
                THEN ROUND(p.price_brl * (1 - (pr.discount_percent / 100.0)), 2)
                ELSE p.price_brl 
            END AS effective_price,
            CASE 
                WHEN pr.is_active = 1 AND pr.discount_percent IS NOT NULL THEN 1 
                ELSE 0 
            END AS is_on_promotion
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN promotions pr ON p.product_id = pr.product_id AND pr.is_active = 1
        WHERE p.status = 'active'
    """
    params: List[Any] = []

    if search_term:
        query += " AND (p.name LIKE ? OR p.description LIKE ? OR c.name LIKE ?)"
        term = f"%{search_term}%"
        params.extend([term, term, term])

    if category:
        query += " AND c.name LIKE ?"
        params.append(f"%{category}%")

    if max_price is not None:
        query += " AND (CASE WHEN pr.is_active = 1 AND pr.discount_percent IS NOT NULL THEN ROUND(p.price_brl * (1 - (pr.discount_percent / 100.0)), 2) ELSE p.price_brl END) <= ?"
        params.append(max_price)

    query += " ORDER BY effective_price ASC LIMIT 10"

    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()

    results = []
    for r in rows:
        results.append({
            "product_id": r["product_id"],
            "name": r["name"],
            "category": r["category_name"],
            "original_price": float(r["original_price"]),
            "effective_price": float(r["effective_price"]),
            "is_on_promotion": bool(r["is_on_promotion"]),
            "discount_percent": float(r["discount_percent"]) if r["discount_percent"] else 0.0,
            "stock_quantity": int(r["stock_quantity"]),
            "description": r["description"]
        })
    return results

def query_product_details(conn: sqlite3.Connection, identifier: str) -> Optional[Dict[str, Any]]:
    cursor = conn.cursor()
    query = """
        SELECT p.*, c.name AS category_name, pr.discount_percent, pr.is_active AS promo_active
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN promotions pr ON p.product_id = pr.product_id AND pr.is_active = 1
        WHERE (p.product_id = ? OR p.name LIKE ?)
        LIMIT 1
    """
    cursor.execute(query, [identifier, f"%{identifier}%"])
    row = cursor.fetchone()
    if not row:
        return None

    specs_parsed = {}
    if row["specs"]:
        try:
            specs_parsed = json.loads(row["specs"])
        except Exception:
            specs_parsed = {"raw": row["specs"]}

    original_price = float(row["price_brl"])
    discount = float(row["discount_percent"]) if row["promo_active"] and row["discount_percent"] else 0.0
    effective_price = round(original_price * (1 - (discount / 100.0)), 2) if discount > 0 else original_price

    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "category": row["category_name"],
        "original_price": original_price,
        "effective_price": effective_price,
        "discount_percent": discount,
        "is_on_promotion": discount > 0,
        "stock_quantity": int(row["stock_quantity"]),
        "description": row["description"],
        "specs": specs_parsed
    }

def query_order(
    conn: sqlite3.Connection,
    order_id: Optional[int] = None,
    customer_query: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    cursor = conn.cursor()
    query = """
        SELECT o.*, c.name AS customer_name, c.email, c.phone, c.city
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE 1=1
    """
    params: List[Any] = []
    if order_id is not None:
        query += " AND o.order_id = ?"
        params.append(order_id)
    elif customer_query:
        query += " AND (c.name LIKE ? OR c.email LIKE ? OR c.phone LIKE ? OR o.tracking_code = ?)"
        param_term = f"%{customer_query}%"
        params.extend([param_term, param_term, param_term, customer_query])
    else:
        return None

    query += " ORDER BY o.order_date DESC LIMIT 1"
    cursor.execute(query, params)
    order_row = cursor.fetchone()
    if not order_row:
        return None

    # Fetch items
    items_query = """
        SELECT oi.quantity, p.name, p.price_brl
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        WHERE oi.order_id = ?
    """
    cursor.execute(items_query, [order_row["order_id"]])
    item_rows = cursor.fetchall()
    items = [{"product_name": ir["name"], "quantity": ir["quantity"], "unit_price": float(ir["price_brl"])} for ir in item_rows]

    return {
        "order_id": order_row["order_id"],
        "customer_name": order_row["customer_name"],
        "order_date": order_row["order_date"],
        "status": order_row["status"],
        "total_brl": float(order_row["total_brl"]),
        "payment_method": order_row["payment_method"],
        "tracking_code": order_row["tracking_code"],
        "estimated_delivery": order_row["estimated_delivery"],
        "items": items
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_database.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/database.py tests/test_database.py
git commit -m "feat(database): implement in-memory sqlite store and parameterized queries for products and orders"
```

---

### Task 3: Policy Extraction & Structured Knowledge Base (`src/knowledge.py`)

**Files:**
- Create: `src/knowledge.py`
- Test: `tests/test_knowledge.py`

**Interfaces:**
- Consumes: `políticas_da_loja.pdf`
- Produces:
  - `get_policy_topic(topic: str) -> str`
  - `get_store_policy_summary() -> str`
  - `AVAILABLE_POLICY_TOPICS: list[str]`

- [ ] **Step 1: Write failing tests for policy extraction**

```python
# tests/test_knowledge.py
import pytest
from src.knowledge import get_policy_topic, get_store_policy_summary, AVAILABLE_POLICY_TOPICS

def test_available_topics():
    assert "trocas_devolucoes" in AVAILABLE_POLICY_TOPICS
    assert "formas_pagamento" in AVAILABLE_POLICY_TOPICS
    assert "frete_entregas" in AVAILABLE_POLICY_TOPICS

def test_get_policy_returns_accurate_terms():
    devolucao_text = get_policy_topic("trocas_devolucoes")
    assert "7 (sete) dias" in devolucao_text
    assert "arrependimento" in devolucao_text.lower()

def test_store_summary_includes_crucial_guardrails():
    summary = get_store_policy_summary()
    assert "não comercializamos acessórios" in summary.lower() or "exclusivamente com instrumentos" in summary.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_knowledge.py -v`
Expected: FAIL (ModuleNotFoundError: No module named 'src.knowledge')

- [ ] **Step 3: Implement `src/knowledge.py`**

```python
# src/knowledge.py
from typing import Dict, List

POLICIES: Dict[str, str] = {
    "sobre_a_loja": """
• Nome: Empório da Música Instrumentos Musicais Ltda.
• Fundação: 2008 em Campo Grande, Mato Grosso do Sul.
• Endereço: Rua 14 de Maio, 3200 — Centro, Campo Grande - MS, CEP 79202-333.
• Contato: Telefone/WhatsApp: (67) 3341-4444 / (67) 3321-4500 | E-mail: contato@emporiodamusica.com.br.
• Slogan: "Sua música começa aqui."
• ESCOPO ESTRITO: A loja trabalha exclusivamente com instrumentos musicais (cordas orquestrais, violões, guitarras, baixos, baterias, sopros, teclados e pianos). NÃO comercializamos acessórios como cordas avulsas, palhetas, cabos, cases, pedais de efeito ou amplificadores. Pedidos de acessórios devem ser educadamente redirecionados para lojas parceiras.
""",
    "horario_funcionamento": """
• Segunda a Sexta-feira: 09:00 às 18:00.
• Sábado: 09:00 às 13:00.
• Domingos e Feriados: Fechado.
• Atendimento WhatsApp: Segue o mesmo horário comercial; mensagens fora do horário recebem retorno no próximo dia útil.
""",
    "formas_pagamento": """
• PIX: 5% de desconto à vista sobre o preço de tabela. ATENÇÃO: O desconto de PIX NÃO é cumulativo com itens que já estejam em promoção.
• Cartão de Débito: Pagamento à vista (todas as bandeiras aceitas).
• Cartão de Crédito: Em até 12x sem juros.
  - Até 3x: sem juros e sem parcela mínima (exceto compras abaixo de R$ 50,00).
  - De 4x a 6x: sem juros, parcela mínima de R$ 80,00.
  - De 7x a 12x: sem juros, parcela mínima de R$ 100,00.
• Boleto Bancário: Pagamento à vista com compensação em até 3 dias úteis.
• Combinação de pagamentos (PIX + Cartão): Permitida para compras acima de R$ 2.000,00.
""",
    "trocas_devolucoes": """
• Direito de Arrependimento (Compras Online): Até 7 (sete) dias corridos após o recebimento do produto, sem necessidade de justificativa. O produto deve estar na embalagem original, sem sinais de uso, com manuais e acessórios. O frete de devolução é por conta da loja e o reembolso ocorre em até 10 dias úteis na mesma forma de pagamento original.
• Troca por Defeito de Fabricação: Em até 30 (trinta) dias corridos após a compra diretamente com a loja. Após os 30 dias, o cliente deve acionar a garantia do fabricante (a loja pode intermediar). Mau uso, umidade excessiva ou quedas não são cobertos.
• Troca por Preferência (cor, modelo): Em até 7 dias corridos, condicionada à disponibilidade em estoque e embalagem lacrada.
• Itens NÃO Elegíveis para Troca: Instrumentos com regulagem sob encomenda (setup personalizado), produtos em liquidação de "venda final", e boquilhas de instrumentos de sopro (por razões de higiene).
""",
    "frete_entregas": """
• Campo Grande e Região Metropolitana: Frete grátis para compras acima de R$ 500,00. Para pedidos abaixo de R$ 500,00, taxa fixa de R$ 35,00. Prazo: 1 a 3 dias úteis (entrega por motoboy próprio, que liga antes para confirmar).
• Outras Cidades e Estados: Envios via Correios (PAC: 5 a 12 dias úteis, SEDEX: 2 a 5 dias úteis) ou transportadora Jadlog (3 a 8 dias úteis). O frete é calculado por CEP/peso.
• Código de Rastreamento: Formato padrão BR + 9 caracteres alfanuméricos + BR (ex: BR4K7M2X9P1BR). Rastreável diretamente nos Correios ou Jadlog.
""",
    "garantia": """
• Garantia Legal (CDC): 90 (noventa) dias contra defeitos de fabricação contados da entrega.
• Garantia do Fabricante: De 6 meses a 2 anos, conforme o certificado de cada marca.
• Não Coberto pela Garantia: Desgaste natural de peças (trastes, cordas, feltros, palhetas de sopro), mau uso, quedas ou modificações por terceiros.
"""
}

AVAILABLE_POLICY_TOPICS: List[str] = list(POLICIES.keys())

def get_policy_topic(topic: str) -> str:
    topic_normalized = topic.strip().lower()
    if topic_normalized in POLICIES:
        return POLICIES[topic_normalized]
    # Fuzzy match
    for k, v in POLICIES.items():
        if topic_normalized in k or k in topic_normalized:
            return v
    return f"Tópico '{topic}' não encontrado. Tópicos disponíveis: {', '.join(AVAILABLE_POLICY_TOPICS)}"

def get_store_policy_summary() -> str:
    return "\n".join([f"### {k.upper().replace('_', ' ')}\n{v}" for k, v in POLICIES.items()])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_knowledge.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/knowledge.py tests/test_knowledge.py
git commit -m "feat(knowledge): add structured store policy extraction and topic retrieval engine"
```

---

### Task 4: Typed Agent Tools (`src/tools.py`)

**Files:**
- Create: `src/tools.py`
- Test: `tests/test_tools.py`

**Interfaces:**
- Consumes: `src.database` functions, `src.knowledge` functions.
- Produces: Declarations of `buscar_produtos`, `consultar_detalhes_produto`, `consultar_pedido`, `consultar_politicas` with full type annotations and docstrings for Gemini Tool Calling.

- [ ] **Step 1: Write failing tests for tools execution**

```python
# tests/test_tools.py
import pytest
from src.database import init_database
from src.tools import create_tool_registry

@pytest.fixture(scope="module")
def tools():
    db = init_database()
    return create_tool_registry(db)

def test_buscar_produtos_tool(tools):
    func = tools["buscar_produtos"]
    res = func(termo="violão", preco_maximo=1000.0)
    assert "produtos" in res
    assert isinstance(res["produtos"], list)

def test_consultar_politicas_tool(tools):
    func = tools["consultar_politicas"]
    res = func(topico="frete_entregas")
    assert "Campo Grande" in res
    assert "Frete grátis" in res
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_tools.py -v`
Expected: FAIL (ModuleNotFoundError: No module named 'src.tools')

- [ ] **Step 3: Implement `src/tools.py`**

```python
# src/tools.py
import sqlite3
from typing import Any, Callable, Dict, List, Optional
from src.database import query_products, query_product_details, query_order
from src.knowledge import get_policy_topic, AVAILABLE_POLICY_TOPICS

def create_tool_registry(db_conn: sqlite3.Connection) -> Dict[str, Callable[..., Any]]:
    """Creates a dictionary of executable tool functions bound to the database connection."""

    def buscar_produtos(
        termo: Optional[str] = None,
        categoria: Optional[str] = None,
        preco_maximo: Optional[float] = None
    ) -> Dict[str, Any]:
        """Consulta o catálogo de instrumentos musicais disponíveis na loja com filtros opcionais.
        
        Args:
            termo: Nome do instrumento, modelo ou marca (ex: 'violão', 'yamaha', 'tagima', 'teclado').
            categoria: Nome da categoria (ex: 'Violões', 'Guitarras', 'Baixos', 'Teclados e Pianos').
            preco_maximo: Preço limite em Reais (ex: 1000.0).
            
        Returns:
            Dicionário com a lista de instrumentos encontrados, seus preços reais, descontos de promoção ativos e estoque.
        """
        results = query_products(db_conn, search_term=termo, category=categoria, max_price=preco_maximo)
        return {
            "total_encontrados": len(results),
            "produtos": results
        }

    def consultar_detalhes_produto(nome_ou_id: str) -> Dict[str, Any]:
        """Retorna a ficha técnica completa e detalhes de especificações de um instrumento musical.
        
        Args:
            nome_ou_id: Nome do produto ou ID numérico (ex: 'Yamaha C40', 'Giannini GN-15', '81').
            
        Returns:
            Ficha técnica com tipo de madeira, cordas, acabamento, captação, estoque e preço atual.
        """
        res = query_product_details(db_conn, nome_ou_id)
        if not res:
            return {"status": "not_found", "mensagem": f"Nenhum instrumento encontrado com o nome ou ID '{nome_ou_id}'."}
        return {"status": "success", "produto": res}

    def consultar_pedido(
        numero_pedido: Optional[int] = None,
        termo_cliente: Optional[str] = None
    ) -> Dict[str, Any]:
        """Consulta o status atual, código de rastreamento e itens de um pedido de cliente.
        
        Args:
            numero_pedido: O ID numérico do pedido (ex: 1, 4).
            termo_cliente: Nome, e-mail, telefone do cliente ou código de rastreio.
            
        Returns:
            Dados completos do pedido: status (enviado, entregue), data, código de rastreio e itens comprados.
        """
        res = query_order(db_conn, order_id=numero_pedido, customer_query=termo_cliente)
        if not res:
            return {"status": "not_found", "mensagem": "Nenhum pedido localizado com os dados informados."}
        return {"status": "success", "pedido": res}

    def consultar_politicas(topico: str) -> str:
        """Consulta o manual de políticas oficiais da Empório da Música para tirar dúvidas de clientes.
        
        Args:
            topico: O tema da política. Deve ser um entre: 'trocas_devolucoes', 'formas_pagamento', 'frete_entregas', 'horario_funcionamento', 'garantia', 'sobre_a_loja'.
            
        Returns:
            O texto oficial da regra da loja com prazos, condições e diretrizes legais.
        """
        return get_policy_topic(topico)

    return {
        "buscar_produtos": buscar_produtos,
        "consultar_detalhes_produto": consultar_detalhes_produto,
        "consultar_pedido": consultar_pedido,
        "consultar_politicas": consultar_politicas
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_tools.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/tools.py tests/test_tools.py
git commit -m "feat(tools): declare typed agent tools for catalog search, orders and policy retrieval"
```

---

### Task 5: System Prompt Engineering & Persona Guidelines (`src/prompt.py`)

**Files:**
- Create: `src/prompt.py`
- Test: `tests/test_prompt.py`

**Interfaces:**
- Consumes: Store policy summary.
- Produces: `SYSTEM_INSTRUCTION: str`, `format_system_prompt() -> str`.

- [ ] **Step 1: Write test for system prompt generation**

```python
# tests/test_prompt.py
from src.prompt import format_system_prompt

def test_system_prompt_contains_crucial_elements():
    prompt = format_system_prompt()
    assert "Empório da Música" in prompt
    assert "Campo Grande" in prompt
    assert "acessórios" in prompt.lower()
    assert "PIX" in prompt
    assert "entusiasmo" in prompt.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_prompt.py -v`
Expected: FAIL (ModuleNotFoundError: No module named 'src.prompt')

- [ ] **Step 3: Implement `src/prompt.py`**

```python
# src/prompt.py
from src.knowledge import get_store_policy_summary

def format_system_prompt() -> str:
    policy_summary = get_store_policy_summary()
    
    return f"""Você é o Atendente Virtual Oficial da **Empório da Música**, uma tradicional e respeitada loja de instrumentos musicais sediada em Campo Grande/MS (fundada em 2008). Slogan: "Sua música começa aqui."

### PERSONA E TOM DE VOZ
1. **Amigável e Especialista:** Converse de forma acolhedora, informal mas muito profissional, como um amigo músico experiente conversando no balcão da loja. Evite formalidades excessivas ou respostas frias/robotizadas.
2. **Entusiasmo Musical Genuíno:** Demonstre empolgação real e acolhimento caloroso ao atender o cliente, especialmente ao ajudá-lo a encontrar seu instrumento ideal ou dar os primeiros passos na música. Celebre a escolha dele (ex: "Que massa que você vai começar a tocar violão!", "Esse modelo tem uma pegada sensacional!").
3. **Clareza e Transparência:** Seja direto, objetivo e nunca esconda limitações de estoque ou detalhes de prazos.

### DIRETRIZES DE ATENDIMENTO E REGRAS ESTRITAS DE NEGÓCIO

1. **CONSULTA OBRIGATÓRIA DE DADOS (NUNCA ALUCINE):**
   - Antes de informar qualquer preço, disponibilidade de estoque ou especificação, você DEVE acionar a ferramenta `buscar_produtos` ou `consultar_detalhes_produto`.
   - Se o cliente perguntar o status ou rastreamento de uma compra, use `consultar_pedido`.
   - Nunca invente produtos, prazos ou preços da sua imaginação. Se a ferramenta não encontrar, informe com transparência.

2. **FRONTEIRA RÍGIDA DE ESCOPO (NÃO VENDEMOS ACESSÓRIOS):**
   - A loja vende EXCLUSIVAMENTE instrumentos musicais (guitarras, violões, baixos, baterias, teclados, pianos, sopros, ukuleles).
   - A loja NÃO VENDE acessórios (cordas avulsas, palhetas, cabos, pedais de efeito, amplificadores, cases/capas).
   - SE O CLIENTE PEDIR ACESSÓRIOS: NÃO chame nenhuma tool de produto. Recuse imediatamente com cordialidade e simpatia, explicando que o foco da loja é 100% em instrumentos para garantir a máxima qualidade, e recomende educadamente procurar lojas parceiras de Campo Grande.

3. **FORMAS DE PAGAMENTO E DESCONTOS:**
   - PIX: Oferece 5% de desconto à vista sobre o preço de tabela.
   - REGRA DE OURO DO PIX: O desconto do PIX **NÃO É CUMULATIVO** com instrumentos que já estejam em promoção (campo `is_on_promotion = True`). Deixe isso muito claro caso o produto esteja em oferta.
   - Cartão de Crédito: Parcelamento em até 12x sem juros (até 3x sem valor mínimo; 4x-6x parcela mínima de R$ 80; 7x-12x parcela mínima de R$ 100).

4. **POLÍTICAS DA LOJA (TROCAS, FRETE E GARANTIAS):**
   - Use a ferramenta `consultar_politicas` sempre que precisar checar regras detalhadas de trocas, devoluções, fretes, garantias ou horários de atendimento.
   - Arrependimento de compra online: 7 dias corridos após o recebimento, com frete pago pela loja e estorno em até 10 dias úteis.
   - Frete Campo Grande/Região Metropolitana: Grátis acima de R$ 500,00 (abaixo é taxa fixa R$ 35,00, entrega em 1 a 3 dias úteis).

### BASE DE CONHECIMENTO DE POLÍTICAS DA LOJA:
{policy_summary}

### FLUXO DA RESPOSTA:
1. Cumprimente o cliente com calor humano e entusiasmo musical.
2. Forneça a resposta baseada nos dados retornados pelas ferramentas.
3. Se apresentar instrumentos, mencione o nome, preço, disponibilidade em estoque e opções de pagamento (incluindo o PIX se não for promoção).
4. Finalize perguntando com cordialidade se o cliente gostaria de ouvir mais sobre algum modelo ou se precisa de mais alguma informação para fechar a compra.
"""
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_prompt.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/prompt.py tests/test_prompt.py
git commit -m "feat(prompt): create system instruction with musical persona, strict scope guardrails and anti-hallucination rules"
```

---

### Task 6: Core Agent Engine & Native Tool-Calling Loop (`src/agent.py`)

**Files:**
- Create: `src/agent.py`
- Test: `tests/test_agent.py`

**Interfaces:**
- Consumes: `src.config.settings`, `src.database.init_database`, `src.tools.create_tool_registry`, `src.prompt.format_system_prompt`.
- Produces: `MusicStoreAgent` class:
  - `__init__(self, db_conn = None, api_key = None)`
  - `chat(self, user_message: str) -> str`
  - `reset_history(self) -> None`
  - `get_history(self) -> list[dict]`
  - `export_conversation_markdown(self, title: str) -> str`

- [ ] **Step 1: Write test for agent instantiation and conversation state**

```python
# tests/test_agent.py
import pytest
from unittest.mock import MagicMock
from src.agent import MusicStoreAgent

def test_agent_initialization():
    agent = MusicStoreAgent(api_key="fake-key")
    assert agent is not None
    assert len(agent.history) == 0

def test_agent_history_reset():
    agent = MusicStoreAgent(api_key="fake-key")
    agent.history.append({"role": "user", "content": "Olá"})
    assert len(agent.history) == 1
    agent.reset_history()
    assert len(agent.history) == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_agent.py -v`
Expected: FAIL (ModuleNotFoundError: No module named 'src.agent')

- [ ] **Step 3: Implement `MusicStoreAgent` in `src/agent.py`**

```python
# src/agent.py
import logging
from typing import Any, Dict, List, Optional
from google import genai
from google.genai import types
from src.config import settings
from src.database import init_database
from src.tools import create_tool_registry
from src.prompt import format_system_prompt

logger = logging.getLogger("music_emporium")

class MusicStoreAgent:
    """Core intelligent agent orchestrating the conversational loop with Google Gemini."""

    def __init__(self, db_conn=None, api_key: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        self.db_conn = db_conn or init_database()
        self.tool_registry = create_tool_registry(self.db_conn)
        self.system_prompt = format_system_prompt()
        self.history: List[Dict[str, Any]] = []
        
        # Tools list for Gemini client
        self.tools = list(self.tool_registry.values())

        if self.api_key and self.api_key != "fake-key":
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def reset_history(self) -> None:
        """Clears the conversational memory."""
        self.history = []

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history

    def chat(self, user_message: str) -> str:
        """Processes a customer message through the Gemini model and returns the response."""
        if not self.client:
            if settings.debug_mode:
                return "DEBUG ERROR: GEMINI_API_KEY não configurada no ambiente."
            return "Putz, arrebentou uma corda da guitarra aqui no meio do solo! 🎸 Estamos sem conexão com o sistema no momento. Por favor, verifique a chave no arquivo .env!"

        # Record user message in memory
        self.history.append({"role": "user", "content": user_message})

        try:
            # Build conversation contents for the Gemini API
            contents = []
            for msg in self.history:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])]
                ))

            config = types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                tools=self.tools,
                temperature=0.4,
            )

            # Execution loop for tool calls
            max_iterations = 5
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                response = self.client.models.generate_content(
                    model=settings.model_name,
                    contents=contents,
                    config=config,
                )

                candidate = response.candidates[0]
                model_content = candidate.content
                contents.append(model_content)

                # Check if model requested function calls
                function_calls = [p.function_call for p in model_content.parts if p.function_call]
                if not function_calls:
                    # Final text response
                    reply_text = "".join([p.text for p in model_content.parts if p.text])
                    self.history.append({"role": "assistant", "content": reply_text})
                    return reply_text

                # Execute requested functions
                tool_response_parts = []
                for fc in function_calls:
                    fn_name = fc.name
                    fn_args = dict(fc.args) if fc.args else {}
                    
                    if settings.debug_mode:
                        logger.info(f"⚙ Executando tool: {fn_name}({fn_args})")
                    
                    if fn_name in self.tool_registry:
                        fn = self.tool_registry[fn_name]
                        result = fn(**fn_args)
                    else:
                        result = {"error": f"Tool '{fn_name}' não existe."}

                    tool_response_parts.append(types.Part.from_function_response(
                        name=fn_name,
                        response={"result": result}
                    ))

                # Feed function results back to the conversation
                contents.append(types.Content(
                    role="tool",
                    parts=tool_response_parts
                ))

            fallback_msg = "Desculpe, precisei fazer muitas consultas ao sistema e não consegui concluir. Pode reformular sua dúvida?"
            self.history.append({"role": "assistant", "content": fallback_msg})
            return fallback_msg

        except Exception as e:
            if settings.debug_mode:
                return f"[DEBUG EXCEPTION]: {str(e)}"
            return "Ops! Parece que o nosso cabo deu um mau contato aqui na linha. 🎸 Me manda essa mensagem de novo em um minutinho pra gente afinar a conversa?"

    def export_conversation_markdown(self, title: str = "Atendimento Empório da Música") -> str:
        """Exports the current session into clean GitHub Markdown format."""
        lines = [f"# Exemplo de Interação: {title}\n"]
        for msg in self.history:
            role = "Cliente" if msg["role"] == "user" else "Atendente (Empório da Música)"
            lines.append(f"**{role}:**\n{msg['content']}\n")
        return "\n".join(lines)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_agent.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/agent.py tests/test_agent.py
git commit -m "feat(agent): implement core MusicStoreAgent with native Gemini tool-calling loop and memory"
```

---

### Task 7: Interactive Rich CLI Runner (`main.py`)

**Files:**
- Create: `main.py`
- Test: Manual execution test (`python main.py --help` or test harness)

**Interfaces:**
- Consumes: `src.agent.MusicStoreAgent`, `src.config.settings`.
- Produces: CLI interface in terminal with color panels, tool indicators, commands (`/reset`, `/export`, `/sair`).

- [ ] **Step 1: Implement `main.py`**

```python
# main.py
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from src.agent import MusicStoreAgent
from src.config import settings

console = Console()

def display_welcome_banner():
    banner = """[bold cyan]╔═══════════════════════════════════════════════════════════════╗[/bold cyan]
[bold cyan]║[/bold cyan]   [bold yellow]🎸 EMPÓRIO DA MÚSICA — ATENDIMENTO VIRTUAL INTELIGENTE[/bold yellow]     [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]   [italic]Sua música começa aqui • Campo Grande / MS[/italic]                  [bold cyan]║[/bold cyan]
[bold cyan]╚═══════════════════════════════════════════════════════════════╝[/bold cyan]

[dim]Comandos: [bold]/export[/bold] (salvar conversa em .md) | [bold]/reset[/bold] (reiniciar chat) | [bold]/sair[/bold] (encerrar)[/dim]
"""
    console.print(banner)

def main():
    display_welcome_banner()

    if not settings.gemini_api_key:
        console.print(Panel(
            "[bold red]ATENÇÃO: GEMINI_API_KEY não encontrada no arquivo .env![/bold red]\n\n"
            "1. Crie uma chave gratuita no Google AI Studio: [underline]https://aistudio.google.com/[/underline]\n"
            "2. Copie o arquivo [bold].env.example[/bold] para [bold].env[/bold] e cole sua chave:\n"
            "   [bold green]GEMINI_API_KEY=sua_chave_aqui[/bold green]\n"
            "3. Execute o programa novamente.",
            title="Configuração Necessária",
            border_style="red"
        ))
        sys.exit(1)

    agent = MusicStoreAgent()
    console.print("[green]● Assistente online e pronto para atendimento![/green]\n")

    while True:
        try:
            user_input = console.input("[bold purple]Você > [/bold purple]").strip()
            if not user_input:
                continue

            if user_input.lower() in ["/sair", "sair", "exit", "quit"]:
                console.print("\n[yellow]Atendimento encerrado. A Empório da Música agradece sua visita! 🎸[/yellow]")
                break

            if user_input.lower() == "/reset":
                agent.reset_history()
                console.print("[dim italic]Histórico de conversa reiniciado.[/dim italic]\n")
                continue

            if user_input.lower().startswith("/export"):
                parts = user_input.split(" ", 1)
                filename = parts[1] if len(parts) > 1 else "conversa_exportada.md"
                if not filename.endswith(".md"):
                    filename += ".md"
                
                export_dir = settings.project_root / "examples"
                export_dir.mkdir(exist_ok=True)
                export_path = export_dir / filename
                
                md_content = agent.export_conversation_markdown(title=filename.replace(".md", ""))
                with open(export_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
                console.print(f"[bold green]✔ Conversa salva com sucesso em:[/bold green] [underline]{export_path}[/underline]\n")
                continue

            with console.status("[bold cyan]Consultando sistema da loja...[/bold cyan]", spinner="dots"):
                response = agent.chat(user_input)

            console.print()
            console.print(Panel(
                Markdown(response),
                title="[bold green]Atendente Empório da Música[/bold green]",
                border_style="green",
                padding=(1, 2)
            ))
            console.print()

        except KeyboardInterrupt:
            console.print("\n[yellow]Sessão interrompida pelo usuário. Até logo![/yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]Erro inesperado:[/bold red] {e}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add main.py
git commit -m "feat(cli): add interactive rich terminal interface with session export and banner"
```

---

### Task 8: Web UI Runner (`app.py`) with Streamlit

**Files:**
- Create: `app.py`
- Test: Manual check / execution readiness

**Interfaces:**
- Consumes: `src.agent.MusicStoreAgent`, `streamlit`.
- Produces: WhatsApp-style web chat app running via `streamlit run app.py`.

- [ ] **Step 1: Implement `app.py`**

```python
# app.py
import streamlit as st
from src.agent import MusicStoreAgent
from src.config import settings

st.set_page_config(
    page_title="Empório da Música — Atendimento Virtual",
    page_icon="🎸",
    layout="centered"
)

# Custom CSS for styling
st.markdown("""
<style>
    .store-badge {
        background-color: #2e7d32;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar with store information
with st.sidebar:
    st.title("🎸 Empório da Música")
    st.caption("Sua música começa aqui • Campo Grande/MS")
    st.markdown("---")
    st.markdown("**Status da Loja:**")
    st.markdown('<span class="store-badge">● Aberto</span> (Seg-Sex: 09h às 18h | Sáb: 09h às 13h)', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Localização:**")
    st.write("Rua 14 de Maio, 3200 — Centro")
    st.write("Telefone / WhatsApp: (67) 3341-4444")
    st.markdown("---")
    if st.button("🔄 Reiniciar Conversa", use_container_width=True):
        st.session_state.agent = MusicStoreAgent()
        st.session_state.messages = []
        st.rerun()

# Initialize session state
if "agent" not in st.session_state:
    st.session_state.agent = MusicStoreAgent()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Seja muito bem-vindo à **Empório da Música**! 🎸\n\nEu sou o atendente virtual da loja. Como posso te ajudar hoje a encontrar seu próximo som ou tirar alguma dúvida?"}
    ]

st.title("Atendimento ao Cliente")
st.caption("Converse sobre instrumentos, preços, status de pedidos e políticas da loja.")

# Render message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Digite sua dúvida ou o instrumento que procura..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando instrumentos e políticas..."):
            reply = st.session_state.agent.chat(prompt)
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
```

- [ ] **Step 2: Commit**

```bash
git add app.py
git commit -m "feat(ui): add Streamlit web application providing a WhatsApp-style customer experience"
```

---

### Task 9: Real Interaction Examples Generation (`examples/*.md`)

**Files:**
- Create: `examples/01_consulta_catalogo.md`
- Create: `examples/02_status_pedido.md`
- Create: `examples/03_politica_devolucao.md`
- Create: `examples/04_fora_de_escopo_acessorios.md`
- Create: `examples/05_cenario_nao_trivial_hibrido.md`

**Interfaces:**
- Produces: 5 formatted interaction logs covering trivial and non-trivial scenarios as demanded by Artefact's instructions.

- [ ] **Step 1: Write all 5 real conversation examples in Markdown format**
- [ ] **Step 2: Commit**

```bash
git add examples/
git commit -m "docs(examples): add 5 real interaction logs covering catalog, orders, returns, accessories and non-trivial scenarios"
```

---

### Task 10: Production README.md in English & Submission PDF

**Files:**
- Create: `README.md` (Comprehensive, professional, in English)
- Create: Script or documentation for PDF generation (`Lucas Mota - AI Engineer – Full-Stack para Aplicações com IA Generativa.pdf`)

**Requirements to Cover:**
1. Instructions to run (CLI and Streamlit, environment configuration).
2. Technical justifications (Gemini 2.5 Flash, Native Tool-Calling Loop, In-Memory SQLite, In-Context Policies).
3. AI coding assistant workflow section (explaining Antigravity pair-programming, TypeScript to Python acceleration, and test-driven development).
4. Known limitations and what would be built with more time (OpenRouter multi-model interface, persistent vector store for large catalogs, WhatsApp webhook integration).

- [ ] **Step 1: Write `README.md` in English**
- [ ] **Step 2: Run all tests to ensure 100% green suite**
- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: complete comprehensive technical README in English meeting all Artefact requirements"
```
