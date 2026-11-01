import csv
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.config import settings

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
) -> List[Dict[str, Any]]:
    """Queries products with optional search term, category filter, and price threshold."""
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
    """Retrieves full product specifications and details by id or name."""
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
    """Retrieves order details, tracking code and items by order_id or customer info."""
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
