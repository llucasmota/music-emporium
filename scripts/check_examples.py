#!/usr/bin/env python3
"""
Automated verifier for conversation examples in examples/*.md
Confronts prices, stock, order numbers, and tracking codes against CSV/SQLite data.
Checks for private data exposure and unsupported promise claims.
"""
import re
import sys
from pathlib import Path
from decimal import Decimal
from src.database import init_database

def check_examples():
    conn = init_database()
    examples_dir = Path("examples")
    md_files = sorted(examples_dir.glob("*.md"))
    
    print(f"🔍 Found {len(md_files)} example files in {examples_dir}/:")
    for f in md_files:
        print(f"  - {f.name}")
        
    divergences = []
    
    # Pre-fetch all products and orders into lookup dictionaries
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.product_id, p.name, p.price_brl, p.stock_quantity, p.status, pr.discount_percent
        FROM products p
        LEFT JOIN promotions pr ON p.product_id = pr.product_id AND pr.is_active = 1
    """)
    products = cursor.fetchall()
    
    cursor.execute("""
        SELECT o.order_id, o.customer_id, c.name, o.total_brl, o.status, o.tracking_code, o.notes
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
    """)
    orders = {row["order_id"]: row for row in cursor.fetchall()}
    
    # Forbidden promise patterns (B5)
    unsupported_patterns = [
        re.compile(r"\b(já reservei|vou reservar|reservei para você|reservei o)\b", re.IGNORECASE),
        re.compile(r"\b(já emiti|emiti a etiqueta|geramos uma etiqueta|vou emitir a etiqueta)\b", re.IGNORECASE),
        re.compile(r"\b(já registrei sua reclamação|registrei seu protocolo de reclamação)\b", re.IGNORECASE),
    ]

    for file_path in md_files:
        content = file_path.read_text(encoding="utf-8")
        
        # Check B5: Unsupported promises
        for pattern in unsupported_patterns:
            match = pattern.search(content)
            if match:
                divergences.append(
                    f"[{file_path.name}] B5 Violation: Promised unsupported action: '{match.group(0)}'"
                )
                
        # Check B6: Customer privacy (revealing full name without prior verification request)
        for order_id, order_data in orders.items():
            customer_name = order_data["name"]
            # If customer full name appears in assistant response
            if customer_name in content:
                # Check if the text asked for email/phone before showing customer name
                if not re.search(r"(e-mail|email|telefone|confirmar|autenticar)", content, re.IGNORECASE):
                    divergences.append(
                        f"[{file_path.name}] B6 Violation: Revealed customer '{customer_name}' without verification"
                    )

        # Check order numbers and tracking codes
        order_matches = re.finditer(r"(?:Pedido\s+(?:[Nn][ºo°]?\s*)?#?|Nº\s+)(\d+)", content, re.IGNORECASE)
        for om in order_matches:
            oid = int(om.group(1))
            if oid in orders:
                expected_tracking = orders[oid]["tracking_code"]
                # If a tracking code appears near this order, verify match
                tracking_matches = re.findall(r"\b([A-Z]{2}[A-Z0-9]{9}[A-Z]{2})\b", content)
                for tm in tracking_matches:
                    if tm != expected_tracking and expected_tracking:
                        divergences.append(
                            f"[{file_path.name}] Tracking code mismatch for Order {oid}: found {tm}, expected {expected_tracking}"
                        )
            else:
                divergences.append(f"[{file_path.name}] Mentioned non-existent order ID: {oid}")

        # Check specific product data mentioned
        for p in products:
            p_name = p["name"]
            if p_name in content:
                # Check stock mentioned
                stock_pattern = rf"{re.escape(p_name)}.*?(\d+)\s+unidades?"
                stock_match = re.search(stock_pattern, content, re.DOTALL | re.IGNORECASE)
                if stock_match:
                    found_stock = int(stock_match.group(1))
                    if found_stock != p["stock_quantity"]:
                        divergences.append(
                            f"[{file_path.name}] Stock mismatch for '{p_name}': found {found_stock}, expected {p['stock_quantity']}"
                        )
                
                # Check price mentioned for this product
                # e.g., "Takamine GD20 ... R$ 2.890" vs expected 2199
                price_pattern = rf"{re.escape(p_name)}[^\n]*?R\$\s*([\d\.]+(?:,\d{{2}})?)"
                price_match = re.search(price_pattern, content, re.IGNORECASE)
                if price_match:
                    price_str = price_match.group(1).replace(".", "").replace(",", ".")
                    found_price = float(price_str)
                    expected_price = float(p["price_brl"])
                    expected_pix = round(expected_price * 0.95, 2)
                    if p["discount_percent"]:
                        expected_promo = round(expected_price * (1 - p["discount_percent"] / 100), 2)
                        valid_prices = [expected_price, expected_promo]
                    else:
                        valid_prices = [expected_price, expected_pix, round(expected_price * 0.95, 2)]
                    
                    if not any(abs(found_price - vp) < 0.05 for vp in valid_prices):
                        divergences.append(
                            f"[{file_path.name}] Price mismatch for '{p_name}': found R$ {found_price:.2f}, expected R$ {expected_price:.2f} (or PIX/Promo)"
                        )

    print("\n" + "=" * 60)
    if divergences:
        print(f"❌ FAILED: Found {len(divergences)} divergences:")
        for d in divergences:
            print(f"  - {d}")
        return 1
    else:
        print("✅ PASSED: Zero divergences found across all examples!")
        print("=" * 60)
        return 0

if __name__ == "__main__":
    sys.exit(check_examples())
