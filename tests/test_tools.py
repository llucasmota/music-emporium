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

    # Over budget query must trigger alternatives_em_estoque and empty produtos
    res_budget = func(termo="violão", preco_maximo=100.0)
    assert res_budget["total_encontrados"] == 0
    assert res_budget["produtos"] == []
    assert len(res_budget["alternativas_em_estoque"]) > 0
    for alt in res_budget["alternativas_em_estoque"]:
        assert alt["status"] == "active"

def test_consultar_detalhes_produto_tool(tools):
    func = tools["consultar_detalhes_produto"]
    res = func(nome_ou_id="Yamaha C40")
    assert res["status"] == "success"
    assert "Yamaha C40" in res["produto"]["name"]

def test_consultar_pedido_tool(tools):
    func = tools["consultar_pedido"]
    # Without email -> verification required (privacy LGPD §9)
    res_req = func(numero_pedido=1)
    assert res_req["status"] == "verification_required"

    # With correct email -> success
    res = func(numero_pedido=1, email_ou_telefone="pedro.oliveira@jmail.com")
    assert res["status"] == "success"
    assert "pedido" in res
    assert res["pedido"]["order_id"] == 1

def test_consultar_politicas_tool(tools):
    func = tools["consultar_politicas"]
    res = func(topico="frete_entregas")
    assert "Campo Grande" in res
    assert "Frete grátis" in res

def test_registrar_reclamacao_tool(tools):
    assert "registrar_reclamacao" in tools
    func = tools["registrar_reclamacao"]
    res = func(resumo="Reclamação de teste pelo tool registry", email="cliente@jmail.com", numero_pedido=1)
    assert res["status"] == "registrada"
    assert "protocolo" in res
    assert res["prazo_retorno"] == "24 horas úteis"

