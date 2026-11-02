"""
Store policy knowledge engine for Empório da Música.
Directly ingests and parses official store policy PDF ('data/políticas_da_loja.pdf')
at startup (Approach A), ensuring zero transcription drift from the official document.
"""
from typing import Dict, List, Optional
from pathlib import Path
import logging
import re
import pypdf

logger = logging.getLogger("music_emporium")

# Determine path to the official store policies PDF
_DEFAULT_PDF = Path("data/políticas_da_loja.pdf")
if not _DEFAULT_PDF.exists():
    _candidate = Path(__file__).resolve().parent.parent / "data" / "políticas_da_loja.pdf"
    if _candidate.exists():
        _DEFAULT_PDF = _candidate

MAIN_SECTIONS = [
    (1, "sobre_a_loja", r"1\.\s+Sobre a Empório da Música"),
    (2, "horario_funcionamento", r"2\.\s+Horário de Funcionamento"),
    (3, "formas_pagamento", r"3\.\s+Formas de Pagamento"),
    (4, "trocas_devolucoes", r"4\.\s+Política de Trocas e Devoluções"),
    (5, "frete_entregas", r"5\.\s+Política de Frete e Entregas"),
    (6, "promocoes", r"6\.\s+Promoções e Descontos"),
    (7, "situacoes_especiais", r"7\.\s+Atendimento via WhatsApp"),
    (8, "garantia", r"8\.\s+Garantia"),
    (9, "privacidade", r"9\.\s+Privacidade e Proteção de Dados"),
    (10, "disposicoes_finais", r"10\.\s+Disposições Finais"),
]

def load_policies_from_pdf(pdf_path: Optional[Path] = None) -> Dict[str, str]:
    """Extracts and parses all policy sections directly from the official store policy PDF."""
    path = pdf_path or _DEFAULT_PDF
    if not path.exists():
        logger.warning("Policies PDF %s not found. Using fallback policies.", path)
        return _FALLBACK_POLICIES

    try:
        reader = pypdf.PdfReader(str(path))
        doc = "\n".join([p.extract_text() or "" for p in reader.pages])
        doc = re.sub(r"\n\s*\n", " ", doc)
        doc = re.sub(r"[ \t]+", " ", doc)
        doc = re.sub(r"Empório da Música Manual de Políticas e Procedimentos", "", doc)
        doc = re.sub(r"Página \d+", "", doc)

        positions = []
        for sec_num, key, pattern in MAIN_SECTIONS:
            m = re.search(pattern, doc)
            if m:
                positions.append((m.start(), sec_num, key))

        positions.sort()
        policies: Dict[str, str] = {}
        for i in range(len(positions)):
            start_pos, sec_num, key = positions[i]
            end_pos = positions[i+1][0] if i + 1 < len(positions) else len(doc)
            policies[key] = doc[start_pos:end_pos].strip()

        return policies
    except Exception as e:
        logger.error("Failed to parse PDF %s: %s. Using fallback.", path, e)
        return _FALLBACK_POLICIES

_FALLBACK_POLICIES: Dict[str, str] = {
    "sobre_a_loja": "1. Sobre a Empório da Música: fundada em 2008 em Campo Grande/MS. Trabalhamos exclusivamente com instrumentos musicais — não comercializamos acessórios como cordas, palhetas, cabos, cases, pedais ou amplificadores.",
    "horario_funcionamento": "2. Horário de Funcionamento: Segunda a Sexta das 09:00 às 18:00, Sábados das 09:00 às 13:00. Domingos e Feriados: Fechado.",
    "formas_pagamento": "3. Formas de Pagamento: PIX (5% de desconto à vista, não cumulativo com promoções), Cartão de Débito, Cartão de Crédito em até 12x sem juros (conforme faixas do §3.1), Boleto.",
    "trocas_devolucoes": "4. Política de Trocas e Devoluções: Arrependimento de compras online em até 7 (sete) dias corridos (§4.1). Troca por defeito em até 30 dias (§4.2). Troca por preferência em até 7 dias em perfeito estado e na embalagem original, mediante disponibilidade; diferenças de valor serão cobradas ou reembolsadas conforme o caso (§4.3).",
    "frete_entregas": "5. Frete e Entregas: Frete grátis para Campo Grande acima de R$ 500,00 (abaixo taxa de R$ 35,00). Outras cidades via Correios e Jadlog.",
    "promocoes": "6. Promoções e Descontos: Promoções não são cumulativas. Desconto de PIX não se aplica sobre preços promocionais. Sem rain check.",
    "situacoes_especiais": "7. Atendimento via WhatsApp: Canal (67) 3321-4500. Produto descontinuado, fora de estoque e registro de reclamações (prazo de retorno: 24 horas úteis).",
    "garantia": "8. Garantia: Garantia legal de 90 dias contra defeitos de fabricação (§8.1) e garantia do fabricante de 6 meses a 2 anos (§8.2).",
    "privacidade": "9. Privacidade e Proteção de Dados: LGPD (Lei nº 13.709/2018). Dados não são compartilhados com terceiros para fins de marketing.",
    "disposicoes_finais": "10. Disposições Finais: Documento interno de referência para a equipe e assistente virtual."
}

POLICIES: Dict[str, str] = load_policies_from_pdf()
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
