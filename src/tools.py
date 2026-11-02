import sqlite3
from typing import Any, Callable, Dict, List, Optional
from langchain_core.tools import tool
from src.database import query_products, query_product_details, query_order
from src.knowledge import get_policy_topic, AVAILABLE_POLICY_TOPICS

def create_langchain_tools(db_conn: sqlite3.Connection) -> List[Any]:
    """Creates a list of LangChain @tool objects for use with LangGraph."""

    @tool
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
        total_found = getattr(results, "total_count", len(results))

        if total_found == 0 and preco_maximo is not None:
            # Provide available products without price filter so the agent never hallucinates models
            alternatives = query_products(db_conn, search_term=termo, category=categoria)
            active_alternatives = [p for p in alternatives if p.get("status") == "active"]
            return {
                "total_encontrados": 0,
                "produtos": [],
                "mensagem": f"Nenhum produto encontrado com preço até R$ {preco_maximo:.2f}.",
                "alternativas_em_estoque": active_alternatives
            }

        return {
            "total_encontrados": total_found,
            "produtos": results
        }

    @tool
    def consultar_detalhes_produto(nome_ou_id: str) -> Dict[str, Any]:
        """Retorna a ficha técnica completa e detalhes de especificações de um instrumento musical.
        
        Args:
            nome_ou_id: Nome do produto ou ID numérico (ex: 'Yamaha C40', 'Giannini GN-15', '81').
            
        Returns:
            Ficha técnica com especificações, status comercial (ativo, descontinuado, em breve), preços PIX e parcelamento.
        """
        res = query_product_details(db_conn, nome_ou_id)
        if not res:
            return {"status": "not_found", "mensagem": f"Nenhum instrumento encontrado com o nome ou ID '{nome_ou_id}'."}
        if res.get("status") == "ambiguous":
            return res
        return {"status": "success", "produto": res}

    @tool
    def consultar_pedido(
        numero_pedido: Optional[int] = None,
        email_ou_telefone: Optional[str] = None,
        codigo_rastreio: Optional[str] = None,
        termo_cliente: Optional[str] = None
    ) -> Dict[str, Any]:
        """Consulta o status atual, código de rastreamento e itens de um pedido de cliente com validação de privacidade LGPD (§9).
        
        Args:
            numero_pedido: O ID numérico do pedido (ex: 4, 20).
            email_ou_telefone: E-mail ou telefone cadastrado pelo cliente para autenticação de segurança.
            codigo_rastreio: Código de rastreamento da transportadora (ex: 'BRQM7890123BR').
            termo_cliente: Parâmetro legado de busca (e-mail, telefone, rastreio ou nome).
            
        Returns:
            Status do pedido, itens comprados, notas de entrega ou aviso de verificação necessária.
        """
        cust_query = email_ou_telefone or codigo_rastreio or termo_cliente
        return query_order(db_conn, order_id=numero_pedido, customer_query=cust_query)

    @tool
    def consultar_politicas(topico: str) -> str:
        """Consulta o manual de políticas oficiais da Empório da Música para tirar dúvidas de clientes.
        
        Args:
            topico: O tema da política. Deve ser um entre: 'trocas_devolucoes', 'formas_pagamento', 'frete_entregas', 'horario_funcionamento', 'garantia', 'sobre_a_loja'.
            
        Returns:
            O texto oficial da regra da loja com prazos, condições e diretrizes legais.
        """
        return get_policy_topic(topico)

    return [buscar_produtos, consultar_detalhes_produto, consultar_pedido, consultar_politicas]

def create_tool_registry(db_conn: sqlite3.Connection) -> Dict[str, Callable[..., Any]]:
    """Creates a dictionary of callable tool functions for direct invocation or testing."""
    lc_tools = create_langchain_tools(db_conn)
    registry = {}
    for t in lc_tools:
        # Wrap tool invoke so direct calling func(**kwargs) works identically
        def make_wrapper(tool_obj):
            return lambda **kwargs: tool_obj.invoke(kwargs)
        registry[t.name] = make_wrapper(t)
    return registry
