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

# Ensure repository root is on sys.path when executed directly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.database import init_database, calculate_max_installments

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
        SELECT o.order_id, o.customer_id, c.name, c.email, c.phone, o.total_brl, o.status, o.tracking_code, o.notes
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
    """)
    orders = {row["order_id"]: row for row in cursor.fetchall()}
    
    # Forbidden promise patterns (B5)
    unsupported_patterns = [
        re.compile(r"\b(já reservei|vou reservar|reservei para você|reservei o)\b", re.IGNORECASE),
        re.compile(r"\b(já emiti|emiti a etiqueta|geramos uma etiqueta|vou emitir a etiqueta)\b", re.IGNORECASE),
        re.compile(r"\b(já registrei sua reclamação|registrei seu protocolo de reclamação)\b", re.IGNORECASE),
        re.compile(r"\b(posso iniciar|gerar o link|posso reservar)\b", re.IGNORECASE),
    ]

    for file_path in md_files:
        content = file_path.read_text(encoding="utf-8")
        
        # Split into conversational turns for accurate turn-by-turn verification
        # Turn blocks alternate: Cliente vs Atendente
        turns = re.split(r"\*\*(Cliente|Atendente [^\*]+)\:\*\*", content)
        # turns[1::2] are headers, turns[2::2] are body contents
        client_history_text = ""
        
        for i in range(1, len(turns), 2):
            role = turns[i].strip()
            body = turns[i+1] if (i+1) < len(turns) else ""
            
            if "Cliente" in role:
                client_history_text += " " + body.lower()
            else:
                # Assistant turn:
                # Check B5: Unsupported promises
                # "registrei" or "registrada" without REC-\d{8}-\d{4} in the same turn is a violation
                if re.search(r"\b(registrei|registrada)\b", body, re.IGNORECASE):
                    if not re.search(r"REC-\d{8}-\d{4}", body):
                        divergences.append(
                            f"[{file_path.name}] B5 Violation: Assistant claimed 'registrei' without a valid REC protocol in the same turn: '{body[:60]}...'"
                        )
                for pattern in unsupported_patterns:
                    match = pattern.search(body)
                    if match:
                        divergences.append(
                            f"[{file_path.name}] B5 Violation: Promised unsupported action: '{match.group(0)}'"
                        )
                
                # Check B6: Customer privacy (revealing full name without prior verification in client history)
                for order_id, order_data in orders.items():
                    customer_full_name = order_data["name"]
                    if customer_full_name in body:
                        # Check if user already provided email or phone in previous turns
                        user_email = (order_data["email"] or "").lower()
                        phone_digits = "".join(filter(str.isdigit, str(order_data["phone"] or "")))
                        last_8_phone = phone_digits[-8:] if len(phone_digits) >= 8 else ""
                        
                        verified = (user_email and user_email in client_history_text) or (last_8_phone and last_8_phone in client_history_text)
                        if not verified:
                            divergences.append(
                                f"[{file_path.name}] B6 Violation: Revealed full customer name '{customer_full_name}' before user verified with email/phone"
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
                
                # Check price mentioned for this product within its conversational block (up to 5 lines or next item)
                lines = content.splitlines()
                for line_idx, line in enumerate(lines):
                    if p_name in line:
                        block_lines = [line]
                        for next_line in lines[line_idx + 1 : min(line_idx + 6, len(lines))]:
                            if next_line.strip().startswith("• ") or next_line.strip().startswith("**Cliente") or next_line.strip().startswith("**Atendente"):
                                break
                            block_lines.append(next_line)
                        window_text = "\n".join(block_lines)
                        expected_price = float(p["price_brl"])
                        expected_pix = round(expected_price * 0.95, 2)
                        if p["discount_percent"]:
                            expected_promo = round(expected_price * (1 - p["discount_percent"] / 100), 2)
                            base_price = expected_promo
                            valid_prices = [expected_price, expected_promo]
                        else:
                            base_price = expected_price
                            valid_prices = [expected_price, expected_pix]

                        inst_info = calculate_max_installments(base_price)
                        expected_n = inst_info["max_installments"]
                        expected_inst_val = inst_info["installment_value"]
                        valid_prices.append(expected_inst_val)

                        # Check explicit installment count and value: (\d+)x de R$ ...
                        inst_matches = re.finditer(r"(\d+)x\s+de\s+R\$\s*([\d\.]+(?:,\d{2})?)", window_text, re.IGNORECASE)
                        for im in inst_matches:
                            found_n = int(im.group(1))
                            found_inst_val = float(im.group(2).replace(".", "").replace(",", "."))
                            if found_n != expected_n:
                                divergences.append(
                                    f"[{file_path.name}] Installment count mismatch for '{p_name}': found {found_n}x, expected {expected_n}x (calculated by §3.1)"
                                )
                            if abs(found_inst_val - expected_inst_val) > 0.15:
                                divergences.append(
                                    f"[{file_path.name}] Installment value mismatch for '{p_name}': found R$ {found_inst_val:.2f}, expected R$ {expected_inst_val:.2f}"
                                )

                        # Check that all mentioned prices match expected table, promo, PIX, or calculated max installment
                        price_matches = re.findall(r"R\$\s*([\d\.]+(?:,\d{2})?)", window_text)
                        for pm in price_matches:
                            price_str = pm.replace(".", "").replace(",", ".")
                            found_price = float(price_str)
                            is_valid_price = any(abs(found_price - vp) < 0.15 for vp in valid_prices)
                            if not is_valid_price:
                                divergences.append(
                                    f"[{file_path.name}] Price mismatch for '{p_name}': found R$ {found_price:.2f}, not matching expected table, PIX or calculated max installment"
                                )

    print("\n" + "=" * 60)
    if divergences:
        print(f"❌ FAILED: Found {len(divergences)} divergences:")
        for d in divergences:
            print(f"  - {d}")
        return 1
    else:
        print("✅ PASSED: All structural checks passed with no divergences found.")
        print("=" * 60)
        return 0

if __name__ == "__main__":
    sys.exit(check_examples())
