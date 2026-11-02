from typing import Dict, List

POLICIES: Dict[str, str] = {
    "sobre_a_loja": """
• Nome: Empório da Música Instrumentos Musicais Ltda.
• Fundação: 2008 em Campo Grande, Mato Grosso do Sul.
• Endereço: Rua 14 de Maio, 3200 — Centro, Campo Grande - MS, CEP 79202-333.
• Contato: Telefone/WhatsApp: (67) 3341-4444 / (67) 3321-4500 | E-mail: contato@emporiodamusica.com.br.
• Slogan: "Sua música começa aqui."
• ESCOPO ESTRITO: A loja trabalha exclusivamente com instrumentos musicais (atualmente com estoque em violões, guitarras, baixos, baterias, teclados, pianos e ukuleles; categorias de sopro e cordas orquestrais não contam com produtos em estoque ativo no momento). NÃO comercializamos acessórios como cordas avulsas, palhetas, cabos, cases, pedais de efeito ou amplificadores. Pedidos de acessórios devem ser educadamente redirecionados para lojas parceiras de Campo Grande.
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
• Cartão de Crédito (§3.1): Em até 12x sem juros conforme as faixas de valor da compra:
  - Até 3x: sem juros e sem parcela mínima (exceto compras abaixo de R$ 50,00).
  - De 4x a 6x: sem juros, parcela mínima de R$ 80,00.
  - De 7x a 12x: sem juros, parcela mínima de R$ 100,00.
• Boleto Bancário: Pagamento à vista com compensação em até 3 dias úteis.
• Combinação de pagamentos (PIX + Cartão): Permitida para compras acima de R$ 2.000,00.
""",
    "trocas_devolucoes": """
• Direito de Arrependimento (Compras Online - §4.1): Até 7 (sete) dias corridos após o recebimento do produto, sem necessidade de justificativa. O produto deve estar na embalagem original, sem sinais de uso, com manuais e acessórios. O frete de devolução é por conta da loja e o reembolso ocorre em até 10 dias úteis na mesma forma de pagamento original.
• Troca por Defeito de Fabricação (§4.2): Em até 30 (trinta) dias corridos após a compra diretamente com a loja. Após os 30 dias, o cliente deve acionar a garantia do fabricante (a loja pode intermediar). Mau uso, umidade excessiva ou quedas não são cobertos.
• Trocas por Preferência (§4.3): Permitidas em até 7 dias, mediante disponibilidade do produto desejado. O produto deve estar em perfeito estado e na embalagem original. Diferenças de valor serão cobradas ou reembolsadas conforme o caso.
• Itens Não Elegíveis para Troca (§4.4): Instrumentos com personalização ou ajustes sob encomenda (setup, regulagem especial), produtos adquiridos em promoções de liquidação com aviso explícito de "venda final", e boquilhas de instrumentos de sopro (por razões de higiene).
""",
    "frete_entregas": """
• Campo Grande e Região Metropolitana (§5.1): Frete grátis para compras acima de R$ 500,00. Para pedidos abaixo de R$ 500,00, taxa fixa de R$ 35,00. Prazo: 1 a 3 dias úteis (entrega por motoboy próprio, que liga antes para confirmar).
• Outras Cidades e Estados (§5.2): Envios via Correios (PAC: 5 a 12 dias úteis, SEDEX: 2 a 5 dias úteis) ou transportadora Jadlog (3 a 8 dias úteis). O frete é calculado por CEP/peso.
• Código de Rastreamento: Formato padrão BR + 9 caracteres alfanuméricos + BR (ex: BR4K7M2X9P1BR). Rastreável diretamente nos Correios ou Jadlog.
""",
    "garantia": """
• Garantia Legal (CDC - §8.1): 90 (noventa) dias contra defeitos de fabricação contados a partir da data de recebimento pelo cliente.
• Garantia do Fabricante (§8.2): De 6 meses a 2 anos, conforme o certificado de cada marca.
• Não Coberto pela Garantia: Desgaste natural de peças (trastes, cordas, feltros, palhetas de sopro), mau uso, quedas ou modificações por terceiros.
""",
    "promocoes": """
• Regras de Promoções (§6.2):
  - Cumulatividade: Promoções não são cumulativas. O desconto de PIX (5%) não se aplica sobre preços já promocionais.
  - Estoque: Promoções estão estritamente sujeitas à disponibilidade de estoque. Produtos esgotados durante a promoção não geram direito a rain check (reserva de preço).
  - Comunicação: Preços promocionais devem sempre ser apresentados junto ao preço original e o percentual de desconto, para total transparência ao cliente.
""",
    "situacoes_especiais": """
• Situações Especiais de Atendimento (§7.3):
  - Produto fora de estoque: Informar que o produto está temporariamente indisponível e sugerir alternativas semelhantes que estejam disponíveis. Nunca confirmar disponibilidade sem verificar o estoque atual.
  - Produto descontinuado: Informar que o produto não faz mais parte do catálogo e oferecer modelos equivalentes ou sucessores.
  - Promoção expirada: Caso o cliente pergunte sobre uma promoção, verificar se ela encontra-se ativa no sistema. Se a promoção estiver vencida, informar com transparência e apresentar o preço atual. Nunca prometer um desconto que não está mais vigente.
  - Reclamação: Ouvir o cliente com empatia, registrar a reclamação e encaminhar para o responsável. Prazo de retorno: 24 horas úteis.
""",
    "privacidade": """
• Privacidade e Proteção de Dados - LGPD (§9):
  - A Empório da Música está em conformidade com a Lei Geral de Proteção de Dados (LGPD — Lei nº 13.709/2018).
  - Os dados pessoais coletados durante o atendimento (nome, telefone, e-mail, endereço) são utilizados exclusivamente para:
    * Processamento e entrega de pedidos.
    * Comunicação sobre status de pedidos e rastreamento.
    * Envio de promoções e novidades (mediante consentimento explícito do cliente).
    * Cumprimento de obrigações legais e fiscais.
  - Dados de clientes não são compartilhados com terceiros para fins de marketing.
  - O cliente pode solicitar a exclusão de seus dados a qualquer momento entrando em contato pelo WhatsApp ou e-mail.
  - Regra de atendimento do projeto: Por segurança e privacidade, a consulta a dados de pedidos no chat exige confirmação de titularidade (número do pedido acompanhado de e-mail ou telefone cadastrado, ou código de rastreamento). Nunca revele dados de clientes ou status de pedidos sem verificação prévia.
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
    sections = []
    for topic, text in POLICIES.items():
        title = topic.replace("_", " ").title()
        sections.append(f"#### {title}\n{text.strip()}")
    return "\n\n".join(sections)
