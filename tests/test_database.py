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

def test_query_order_by_customer_name(db):
    order = query_order(db, customer_query="Lucas Mendes")
    assert order is not None
    assert "Lucas Mendes" in order["customer_name"]
