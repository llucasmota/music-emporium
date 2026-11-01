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
    assert res["total_encontrados"] > 0

def test_consultar_detalhes_produto_tool(tools):
    func = tools["consultar_detalhes_produto"]
    res = func(nome_ou_id="Yamaha C40")
    assert res["status"] == "success"
    assert "Yamaha C40" in res["produto"]["name"]

def test_consultar_pedido_tool(tools):
    func = tools["consultar_pedido"]
    res = func(numero_pedido=1)
    assert res["status"] == "success"
    assert "pedido" in res
    assert res["pedido"]["order_id"] == 1

def test_consultar_politicas_tool(tools):
    func = tools["consultar_politicas"]
    res = func(topico="frete_entregas")
    assert "Campo Grande" in res
    assert "Frete grátis" in res
