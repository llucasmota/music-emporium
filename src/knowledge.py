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
    """Retrieves the exact policy text for a given topic."""
    topic_normalized = topic.strip().lower()
    if topic_normalized in POLICIES:
        return POLICIES[topic_normalized]
    # Fuzzy match
    for k, v in POLICIES.items():
        if topic_normalized in k or k in topic_normalized:
            return v
    return f"Tópico '{topic}' não encontrado. Tópicos disponíveis: {', '.join(AVAILABLE_POLICY_TOPICS)}"

def get_store_policy_summary() -> str:
    """Returns a full markdown summary of all policies to embed in system prompt."""
    return "\n".join([f"### {k.upper().replace('_', ' ')}\n{v}" for k, v in POLICIES.items()])
