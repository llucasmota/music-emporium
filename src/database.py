import csv
from decimal import Decimal, ROUND_HALF_UP
import json
import sqlite3
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.config import settings

class ProductList(list):
    """Subclass of list that preserves total matching count before pagination/limit."""
    def __init__(self, items: List[Any], total_count: int):
        super().__init__(items)
        self.total_count = total_count

def normalize_text(text: Optional[str]) -> str:
    """Removes diacritics/accents and converts to lowercase for resilient searches."""
    if not text:
        return ""
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn").lower()

def get_word_variants(word: str) -> List[str]:
    """Generates Portuguese singular/plural variants for a search token."""
    w = word.strip().lower()
    variants = {w}
    if w.endswith("ao"):
        variants.add(w[:-2] + "oes")
    elif w.endswith("oes"):
        variants.add(w[:-3] + "ao")
    if w.endswith("s") and len(w) > 3:
        variants.add(w[:-1])
    else:
        variants.add(w + "s")
    return list(variants)

def calculate_pix_price(price: float, is_on_promotion: bool) -> Optional[float]:
    """Calculates PIX price with 5% discount (manual §6.2: not cumulative with promotions)."""
    if is_on_promotion:
        return None
    d = Decimal(str(price)) * Decimal("0.95")
    return float(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

def calculate_max_installments(price: float) -> Dict[str, Any]:
    """Calculates max credit card installments and installment amount per store policy §3.1."""
    if price < 50.0:
        return {
            "max_installments": 1,
            "installment_value": round(price, 2),
            "description": "1x sem juros (compras abaixo de R$ 50,00 não parcelam)"
        }

    # 7x to 12x: minimum installment R$ 100.00
    for n in range(12, 6, -1):
        v = price / n
        if v >= 100.0:
            val = round(v, 2)
            return {
                "max_installments": n,
                "installment_value": val,
                "description": f"{n}x de R$ {val:.2f} sem juros"
            }

    # 4x to 6x: minimum installment R$ 80.00
    for n in range(6, 3, -1):
        v = price / n
        if v >= 80.0:
            val = round(v, 2)
            return {
                "max_installments": n,
                "installment_value": val,
                "description": f"{n}x de R$ {val:.2f} sem juros"
            }

    # Up to 3x: no minimum installment (except purchase < R$ 50.00)
    for n in range(3, 1, -1):
        v = price / n
        val = round(v, 2)
        return {
            "max_installments": n,
            "installment_value": val,
            "description": f"{n}x de R$ {val:.2f} sem juros"
        }

    return {
        "max_installments": 1,
        "installment_value": round(price, 2),
        "description": "1x sem juros"
    }

def _find_data_file(data_dir: Path, pattern: str) -> Optional[Path]:
    """Finds a CSV file matching the pattern in data_dir."""
    matches = list(data_dir.glob(f"*{pattern}*.csv"))
    if matches:
        return matches[0]
    return None

def init_database(data_dir: Optional[Path] = None) -> sqlite3.Connection:
    """Initializes in-memory SQLite database and populates it from the CSV files."""
    if data_dir is None:
        data_dir = settings.project_root / "data"
        if not data_dir.exists() or not list(data_dir.glob("*.csv")):
            alt_dir = settings.project_root / "Desafio Técnico AI Engineer 2026" / "data"
            if alt_dir.exists():
                data_dir = alt_dir

    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.create_function("unaccent", 1, normalize_text)
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

    # Mapping table name to search pattern
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
) -> ProductList:
    """Queries products with optional search term, category filter, and price threshold.
    Returns a ProductList with total_count representing the actual number of matches.
    """
    base_where = "WHERE p.status = 'active'"
    params: List[Any] = []

    # Category filter
    if category:
        cat_norm = normalize_text(category)
        base_where += " AND unaccent(c.name) LIKE ?"
        params.append(f"%{cat_norm}%")

    # Multi-keyword search
    if search_term:
        term_clean = normalize_text(search_term)
        words = term_clean.split()
        if words:
            for w in words:
                variants = get_word_variants(w)
                w_clauses = []
                for v in variants:
                    w_clauses.append("(unaccent(p.name) LIKE ? OR unaccent(c.name) LIKE ?)")
                    params.extend([f"%{v}%", f"%{v}%"])
                base_where += " AND (" + " OR ".join(w_clauses) + ")"

    # Price filter
    if max_price is not None:
        base_where += """
            AND (
                CASE 
                    WHEN pr.is_active = 1 AND pr.discount_percent IS NOT NULL 
                    THEN ROUND(p.price_brl * (1 - (pr.discount_percent / 100.0)), 2)
                    ELSE p.price_brl 
                END
            ) <= ?
        """
        params.append(max_price)

    cursor = conn.cursor()

    # Total matching count (without LIMIT)
    count_sql = f"""
        SELECT COUNT(DISTINCT p.product_id)
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN promotions pr ON p.product_id = pr.product_id AND pr.is_active = 1
        {base_where}
    """
    cursor.execute(count_sql, params)
    total_count = cursor.fetchone()[0]

    # If primary search returned 0 and search_term was given, attempt fallback to description
    if total_count == 0 and search_term:
        desc_where = "WHERE p.status = 'active'"
        desc_params: List[Any] = []
        if category:
            desc_where += " AND unaccent(c.name) LIKE ?"
            desc_params.append(f"%{normalize_text(category)}%")
        desc_where += " AND unaccent(p.description) LIKE ?"
        desc_params.append(f"%{normalize_text(search_term)}%")
        if max_price is not None:
            desc_where += """
                AND (
                    CASE 
                        WHEN pr.is_active = 1 AND pr.discount_percent IS NOT NULL 
                        THEN ROUND(p.price_brl * (1 - (pr.discount_percent / 100.0)), 2)
                        ELSE p.price_brl 
                    END
                ) <= ?
            """
            desc_params.append(max_price)
        cursor.execute(f"SELECT COUNT(DISTINCT p.product_id) FROM products p LEFT JOIN categories c ON p.category_id = c.category_id LEFT JOIN promotions pr ON p.product_id = pr.product_id AND pr.is_active = 1 {desc_where}", desc_params)
        desc_count = cursor.fetchone()[0]
        if desc_count > 0:
            base_where = desc_where
            params = desc_params
            total_count = desc_count
        else:
            # Check if matching products exist in non-active status (e.g., discontinued or coming_soon)
            status_where = "WHERE 1=1"
            status_params: List[Any] = []
            words = normalize_text(search_term).split()
            if words:
                for w in words:
                    variants = get_word_variants(w)
                    w_clauses = ["(unaccent(p.name) LIKE ? OR unaccent(c.name) LIKE ?)" for _ in variants]
                    for v in variants:
                        status_params.extend([f"%{v}%", f"%{v}%"])
                    status_where += " AND (" + " OR ".join(w_clauses) + ")"
                cursor.execute(f"SELECT COUNT(DISTINCT p.product_id) FROM products p LEFT JOIN categories c ON p.category_id = c.category_id LEFT JOIN promotions pr ON p.product_id = pr.product_id {status_where}", status_params)
                status_count = cursor.fetchone()[0]
                if status_count > 0:
                    base_where = status_where
                    params = status_params
                    total_count = status_count

    select_sql = f"""
        SELECT 
            p.product_id,
            p.name,
            p.price_brl AS original_price,
            c.name AS category_name,
            p.stock_quantity,
            p.status,
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
        {base_where}
        ORDER BY effective_price ASC
        LIMIT 10
    """
    cursor.execute(select_sql, params)
    rows = cursor.fetchall()

    results = []
    for r in rows:
        orig = float(r["original_price"])
        eff = float(r["effective_price"])
        is_promo = bool(r["is_on_promotion"])
        pix = calculate_pix_price(orig, is_promo)
        inst = calculate_max_installments(eff)

        results.append({
            "product_id": r["product_id"],
            "name": r["name"],
            "category": r["category_name"],
            "original_price": orig,
            "effective_price": eff,
            "is_on_promotion": is_promo,
            "discount_percent": float(r["discount_percent"]) if r["discount_percent"] else 0.0,
            "pix_price": pix,
            "max_installments": inst["max_installments"],
            "installment_value": inst["installment_value"],
            "installment_text": inst["description"],
            "stock_quantity": int(r["stock_quantity"]),
            "status": r["status"],
            "is_available": int(r["stock_quantity"]) > 0 and r["status"] == "active",
            "availability": "Em estoque" if (int(r["stock_quantity"]) > 0 and r["status"] == "active") else ("Descontinuado pelo fabricante" if r["status"] == "discontinued" else ("Em breve / Lançamento futuro" if r["status"] == "coming_soon" else "Esgotado / Indisponível (estoque: 0)")),
            "description": r["description"]
        })

    return ProductList(results, total_count=total_count)

def query_product_details(conn: sqlite3.Connection, identifier: str) -> Optional[Dict[str, Any]]:
    """Retrieves full product specifications and details by id or name, handling ambiguity and status."""
    cursor = conn.cursor()
    ident_str = str(identifier).strip()

    # 1. Try exact product_id lookup
    if ident_str.isdigit():
        query = """
            SELECT p.*, c.name AS category_name, pr.discount_percent, pr.is_active AS promo_active
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN promotions pr ON p.product_id = pr.product_id AND pr.is_active = 1
            WHERE p.product_id = ?
        """
        cursor.execute(query, [int(ident_str)])
        row = cursor.fetchone()
        if row:
            return _format_product_details_row(row)

    # 2. Search by name with unaccent
    ident_norm = normalize_text(ident_str)
    query = """
        SELECT p.*, c.name AS category_name, pr.discount_percent, pr.is_active AS promo_active
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN promotions pr ON p.product_id = pr.product_id AND pr.is_active = 1
        WHERE unaccent(p.name) LIKE ?
    """
    cursor.execute(query, [f"%{ident_norm}%"])
    matches = cursor.fetchall()

    if not matches:
        return None

    if len(matches) == 1:
        return _format_product_details_row(matches[0])

    # Check for exact name match among multiple matches
    exact = [m for m in matches if normalize_text(m["name"]) == ident_norm]
    if len(exact) == 1:
        return _format_product_details_row(exact[0])

    # Ambiguous match: return candidate list
    return {
        "status": "ambiguous",
        "mensagem": f"A busca por '{identifier}' retornou múltiplos modelos ({len(matches)} encontrados). Por favor, informe o modelo exato.",
        "candidatos": [
            {
                "product_id": m["product_id"],
                "name": m["name"],
                "price_brl": float(m["price_brl"]),
                "status": m["status"]
            }
            for m in matches
        ]
    }

def _format_product_details_row(row: sqlite3.Row) -> Dict[str, Any]:
    """Helper to structure product details dictionary."""
    specs_parsed = {}
    if row["specs"]:
        try:
            specs_parsed = json.loads(row["specs"])
        except Exception:
            specs_parsed = {"raw": row["specs"]}

    original_price = float(row["price_brl"])
    discount = float(row["discount_percent"]) if row["promo_active"] and row["discount_percent"] else 0.0
    effective_price = round(original_price * (1 - (discount / 100.0)), 2) if discount > 0 else original_price
    is_promo = discount > 0
    pix = calculate_pix_price(original_price, is_promo)
    inst = calculate_max_installments(effective_price)

    status_raw = row["status"] or "active"
    if status_raw == "discontinued":
        status_label = "Produto Descontinuado (não faz mais parte do catálogo oficial)"
        status_notice = "ATENÇÃO: Este modelo foi DESCONTINUADO. Conforme a política §7.3, informe ao cliente que ele saiu de linha e sugira alternativas equivalentes."
    elif status_raw == "coming_soon":
        status_label = "Em Breve / Lançamento Futuro"
        status_notice = "ATENÇÃO: Este modelo está marcado como 'Em breve' e ainda não está liberado para venda imediata."
    else:
        status_label = "Ativo no catálogo"
        status_notice = None

    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "category": row["category_name"],
        "status": status_raw,
        "status_label": status_label,
        "status_notice": status_notice,
        "original_price": original_price,
        "effective_price": effective_price,
        "discount_percent": discount,
        "is_on_promotion": is_promo,
        "pix_price": pix,
        "max_installments": inst["max_installments"],
        "installment_value": inst["installment_value"],
        "installment_text": inst["description"],
        "stock_quantity": int(row["stock_quantity"]),
        "is_available": int(row["stock_quantity"]) > 0 and status_raw == "active",
        "description": row["description"],
        "specs": specs_parsed
    }

def query_order(
    conn: sqlite3.Connection,
    order_id: Optional[int] = None,
    customer_query: Optional[str] = None
) -> Dict[str, Any]:
    """Retrieves order details enforcing LGPD privacy (§9).
    Requires order_id + email/phone verification, or valid tracking code.
    """
    cursor = conn.cursor()

    # Case 1: Tracking code direct lookup
    if customer_query and customer_query.startswith("BR") and customer_query.endswith("BR") and len(customer_query) >= 11:
        cursor.execute("""
            SELECT o.*, c.city
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.tracking_code = ?
        """, [customer_query])
        row = cursor.fetchone()
        if not row:
            return {"status": "not_found", "mensagem": f"Nenhum envio localizado com o código de rastreio '{customer_query}'."}
        return {
            "status": "success",
            "tipo_consulta": "rastreamento",
            "pedido": {
                "order_id": row["order_id"],
                "tracking_code": row["tracking_code"],
                "status": row["status"],
                "estimated_delivery": row["estimated_delivery"],
                "notes": row["notes"]
            }
        }

    # Case 2: order_id provided
    if order_id is not None:
        cursor.execute("""
            SELECT o.*, c.name AS customer_name, c.email, c.phone, c.city
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_id = ?
        """, [order_id])
        order_row = cursor.fetchone()
        if not order_row:
            return {"status": "not_found", "mensagem": f"Nenhum pedido encontrado com o número #{order_id}."}

        # Verification required: customer must provide email or phone
        if not customer_query:
            return {
                "status": "verification_required",
                "mensagem": f"Por motivos de privacidade e conformidade com a LGPD (manual §9), para consultar os dados do pedido #{order_id} é necessário informar o e-mail ou telefone cadastrado na compra."
            }

        cust_query_norm = normalize_text(customer_query)
        cust_email_norm = normalize_text(order_row["email"])
        cust_phone_clean = "".join(filter(str.isdigit, str(order_row["phone"])))
        query_phone_clean = "".join(filter(str.isdigit, customer_query))

        is_verified = (
            (cust_query_norm and cust_query_norm == cust_email_norm) or
            (cust_phone_clean and len(query_phone_clean) >= 8 and query_phone_clean in cust_phone_clean)
        )

        if not is_verified:
            # Crucial: NEVER reveal customer name or email on verification failure!
            return {
                "status": "verification_failed",
                "mensagem": f"Os dados informados não conferem com o cadastro do pedido #{order_id}. Por favor, confirme o e-mail ou telefone exato cadastrado."
            }

        # Verification succeeded: return full details
        cursor.execute("""
            SELECT oi.quantity, p.name, p.price_brl
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = ?
        """, [order_row["order_id"]])
        item_rows = cursor.fetchall()
        items = [{"product_name": ir["name"], "quantity": ir["quantity"], "unit_price": float(ir["price_brl"])} for ir in item_rows]

        return {
            "status": "success",
            "pedido": {
                "order_id": order_row["order_id"],
                "customer_name": order_row["customer_name"],
                "order_date": order_row["order_date"],
                "status": order_row["status"],
                "total_brl": float(order_row["total_brl"]),
                "payment_method": order_row["payment_method"],
                "tracking_code": order_row["tracking_code"],
                "estimated_delivery": order_row["estimated_delivery"],
                "notes": order_row["notes"],
                "items": items
            }
        }

    # Case 3: Only customer name or generic text provided without order_id
    return {
        "status": "verification_required",
        "mensagem": "Por motivos de privacidade e conformidade com a LGPD (manual §9), não é permitido buscar pedidos apenas pelo primeiro nome. Por favor, informe o número do seu pedido e o e-mail cadastrado, ou o código de rastreamento completo."
    }

