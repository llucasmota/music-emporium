import pytest
from src.database import (
    init_database,
    query_products,
    query_product_details,
    query_order,
    calculate_pix_price,
    calculate_max_installments
)

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

def test_a1_pix_price_calculation(db):
    """A1: PIX price calculated in code (5% off table price, None if on promotion)."""
    # 1. Takamine GD20 (id 95): tabela 2199.00 -> PIX 2089.05
    p95 = query_product_details(db, "95")
    assert p95 is not None
    assert p95["original_price"] == 2199.00
    assert p95["is_on_promotion"] is False
    assert p95["pix_price"] == 2089.05

    # 2. Yamaha C40 (id 81): 599.90 -> PIX 569.91
    p81 = query_product_details(db, "81")
    assert p81 is not None
    assert p81["original_price"] == 599.90
    assert p81["is_on_promotion"] is False
    assert p81["pix_price"] == 569.91

    # 3. Ohana CK-20 (id 121): promoção ativa 20% -> 439.20, SEM PIX (None)
    p121 = query_product_details(db, "121")
    assert p121 is not None
    assert p121["is_on_promotion"] is True
    assert p121["effective_price"] == 439.20
    assert p121["pix_price"] is None

    # 4. Kalani KAL-700T (id 127): promoção ativa 10% -> 323.10, SEM PIX (None)
    p127 = query_product_details(db, "127")
    assert p127 is not None
    assert p127["is_on_promotion"] is True
    assert p127["effective_price"] == 323.10
    assert p127["pix_price"] is None

def test_a2_max_installments_calculation(db):
    """A2: Credit card max installments calculated per manual §3.1."""
    # 1. Shelby SU-21S (id 119, R$ 159.90) -> máx. 3x
    p119 = query_product_details(db, "119")
    assert p119 is not None
    assert p119["max_installments"] == 3

    # 2. Shelby SN-100 (id 89, R$ 549.00) -> máx. 6x
    p89 = query_product_details(db, "89")
    assert p89 is not None
    assert p89["max_installments"] == 6

    # 3. Takamine GD20 (id 95, R$ 2.199.00) -> 12x de R$ 183.25
    p95 = query_product_details(db, "95")
    assert p95 is not None
    assert p95["max_installments"] == 12
    assert p95["installment_value"] == 183.25

def test_c1_order_privacy_and_notes(db):
    """C1: Privacy on order queries (LGPD §9) and notes retention."""
    # 1. Searching by only generic name "Lucas" -> verification_required, no order data exposed
    res_generic = query_order(db, customer_query="Lucas")
    assert res_generic["status"] == "verification_required"
    assert "customer_name" not in res_generic.get("pedido", {})

    # 2. Order 4 + correct email "lucas.mendes@jmail.com" -> success, order 4 returned
    res_success = query_order(db, order_id=4, customer_query="lucas.mendes@jmail.com")
    assert res_success["status"] == "success"
    assert res_success["pedido"]["order_id"] == 4
    assert res_success["pedido"]["customer_name"] == "Lucas Mendes da Silva"

    # 3. Order 4 + wrong email -> verification_failed, NO customer name exposed
    res_wrong = query_order(db, order_id=4, customer_query="wrong.email@test.com")
    assert res_wrong["status"] == "verification_failed"
    assert "pedido" not in res_wrong

    # 4. Order 20 -> notes returned with delivery address invalid issue
    res_20 = query_order(db, order_id=20, customer_query="thiago.barbosa@jmail.com")
    assert res_20["status"] == "success"
    assert res_20["pedido"]["notes"] == "Endereço de entrega inválido informado pelo cliente"

def test_c2_product_status(db):
    """C2: Product status (discontinued, coming_soon, out of stock)."""
    # 1. Ibanez Bass 2X (id 136) -> discontinued even with stock 13
    p136 = query_product_details(db, "Ibanez Bass 2X")
    assert p136 is not None
    assert p136["status"] == "discontinued"
    assert p136["stock_quantity"] == 13

    # 2. Shelby SN-7C (id 113) -> discontinued
    p113 = query_product_details(db, "Shelby SN-7C")
    assert p113 is not None
    assert p113["status"] == "discontinued"

    # 3. Kala KA-ABP-CTG (id 130) -> coming_soon
    p130 = query_product_details(db, "Kala KA-ABP-CTG")
    assert p130 is not None
    assert p130["status"] == "coming_soon"

    # 4. Giannini GF-3D (id 96) in search -> stock 0, marked unavailable
    results = query_products(db, search_term="Giannini GF-3D")
    assert len(results) > 0
    p96 = results[0]
    assert p96["stock_quantity"] == 0
    assert p96["is_available"] is False

def test_c3_robust_search_and_ambiguity(db):
    """C3: Accent-insensitive search, multi-keyword, and ambiguous candidates."""
    # 1. "violao" (unaccented) returns violões
    res_unaccent = query_products(db, search_term="violao")
    assert len(res_unaccent) > 0
    # Ukulele Kala KA-B (id 128) must NOT be returned for "violão"
    ids = [p["product_id"] for p in res_unaccent]
    assert 128 not in ids

    # 2. "guitarra fender" returns both Fender models
    res_fender = query_products(db, search_term="guitarra fender")
    fender_ids = [p["product_id"] for p in res_fender]
    assert 134 in fender_ids # Fender Telecaster
    assert 145 in fender_ids # Fender Stratocaster

    # 3. Ambiguous details lookup for "Kala" returns candidate list
    res_ambiguous = query_product_details(db, "Kala")
    assert res_ambiguous is not None
    assert res_ambiguous["status"] == "ambiguous"
    assert len(res_ambiguous["candidatos"]) > 1

def test_c4_real_total_count(db):
    """C4: Real matching count reported before limit."""
    res = query_products(db, category="Violões", max_price=1000.0)
    assert len(res) <= 10 # Paginated to 10
    assert res.total_count >= 12 # Real total is 13 (or >= 12)

def test_price_budget_fallback_respects_max_price(db):
    """Block 1: Fallback must NEVER relax max_price or category filter."""
    res_violao = query_products(db, search_term="violao", max_price=100.0)
    assert res_violao.total_count == 0
    assert len(res_violao) == 0

    res_guitarra = query_products(db, search_term="guitarra", max_price=200.0)
    assert res_guitarra.total_count == 0
    assert len(res_guitarra) == 0

    # Non-active lookup without max_price continues to find discontinued items
    res_ibanez = query_products(db, search_term="ibanez bass")
    assert res_ibanez.total_count == 1
    assert res_ibanez[0]["status"] == "discontinued"

def test_block_2b_order_return_eligibility_and_phone_validation(db):
    """Block 2b: Order return eligibility against estimated_delivery and endswith phone check."""
    from datetime import datetime
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("America/Campo_Grande")
    fixed_now = datetime(2026, 11, 2, 12, 0, tzinfo=tz)

    # Order 1 (delivered 2025-10-25) checked on 2026-11-02 -> over 370 days elapsed
    res1 = query_order(db, order_id=1, customer_query="pedro.oliveira@jmail.com", current_time=fixed_now)
    assert res1["status"] == "success"
    p1 = res1["pedido"]
    assert p1["dias_desde_entrega"] > 300
    assert p1["elegivel_arrependimento"] is False
    assert p1["elegivel_troca_defeito"] is False
    assert p1["dentro_garantia_legal"] is False

    # Phone test: digits 2-9 of order 4 phone must FAIL
    res_fail = query_order(db, order_id=4, customer_query="79981234")
    assert res_fail["status"] == "verification_failed"

    # Endswith valid suffix (9 digits or 8 digits) must SUCCEED
    res_ok = query_order(db, order_id=4, customer_query="998123456")
    assert res_ok["status"] == "success"

def test_block_3_complaints_table_and_registration(db):
    """Block 3: Complaint registration, sequential protocol, validation, and status constraints."""
    import sqlite3
    from src.database import register_complaint

    # 1. Valid registration
    r1 = register_complaint(db, resumo="Instrumento com tarraxa quebrada", email="cliente@jmail.com", numero_pedido=1)
    assert r1["status"] == "registrada"
    assert r1["protocolo"].endswith("-0001")
    assert r1["prazo_retorno"] == "24 horas úteis"
    assert r1["canal_humano"] == "(67) 3321-4500"

    # 2. Second registration in same day -> 0002
    r2 = register_complaint(db, resumo="Segunda queixa sobre prazo de entrega", email="cliente@jmail.com")
    assert r2["status"] == "registrada"
    assert r2["protocolo"].endswith("-0002")

    # 3. Invalid email -> dados_insuficientes without insert
    r_bad_email = register_complaint(db, resumo="Texto longo sem email valido", email="invalido_sem_arroba")
    assert r_bad_email["status"] == "dados_insuficientes"

    # 4. Short summary (< 10 chars)
    r_short = register_complaint(db, resumo="Curto", email="cliente@jmail.com")
    assert r_short["status"] == "dados_insuficientes"

    # 5. Non-existent order (999) -> pedido_nao_encontrado
    r_bad_order = register_complaint(db, resumo="Pedido que nao existe no banco", email="cliente@jmail.com", numero_pedido=999)
    assert r_bad_order["status"] == "pedido_nao_encontrado"

    # 6. Direct INSERT with invalid status -> IntegrityError
    with pytest.raises(sqlite3.IntegrityError):
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO complaints (protocolo, criado_em, email, order_id, resumo, status)
            VALUES ('REC-TEST-9999', '2026-11-02T10:00:00', 'a@b.com', NULL, 'teste integridade', 'closed')
        """)




