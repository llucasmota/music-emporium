"""
Store policy knowledge engine for Empório da Música.
Directly ingests and dynamically parses official store policy PDF ('data/políticas_da_loja.pdf')
at startup, discovering chapters and sections automatically without hardcoded lists.
"""
from typing import Dict, List, Optional
from pathlib import Path
import logging
import re
import unicodedata
import pypdf

logger = logging.getLogger("music_emporium")

# Determine path to the official store policies PDF
_DEFAULT_PDF = Path("data/políticas_da_loja.pdf")
if not _DEFAULT_PDF.exists():
    _candidate = Path(__file__).resolve().parent.parent / "data" / "políticas_da_loja.pdf"
    if _candidate.exists():
        _DEFAULT_PDF = _candidate

def slugify(text: str) -> str:
    """Converts a heading title to a clean snake_case slug."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"^\d+\.?\s*", "", text)  # remove leading chapter number
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "_", text).strip("_")

COMMON_ALIASES = {
    "trocas_devolucoes": ["troca", "devolu"],
    "formas_pagamento": ["pagamento", "pix", "cartao", "parcela"],
    "frete_entregas": ["frete", "entrega", "envio"],
    "promocoes": ["promoc", "desconto"],
    "situacoes_especiais": ["whatsapp", "especia", "atendimento", "reclamac"],
    "garantia": ["garantia", "defeito"],
    "privacidade": ["privacidade", "lgpd", "dados"],
    "sobre_a_loja": ["sobre", "historia", "loja", "empresa"],
    "horario_funcionamento": ["horario", "funcionamento"],
}

def load_policies_from_pdf(pdf_path: Optional[Path] = None) -> Dict[str, str]:
    """Dynamically extracts and indexes all policy sections directly from the PDF without hardcoded lists."""
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

        # 1. Discover section titles dynamically from PDF outline bookmarks if present
        discovered_titles: List[str] = []
        if reader.outline:
            for item in reader.outline:
                if isinstance(item, dict) and "/Title" in item:
                    discovered_titles.append(item["/Title"].strip())

        # 2. Fallback: discover numbered chapter headings if no outline is found
        if not discovered_titles:
            matches = re.finditer(r"(?:^|\s)((?:[1-9]\d?))\.\s+([A-ZÀ-Ú][^\.\:\n\d]{3,50})(?=\s+[A-ZÀ-Úa-zà-ú]|\s*$)", doc)
            for m in matches:
                discovered_titles.append(f"{m.group(1)}. {m.group(2).strip()}")

        # Locate positions of each discovered section in the document text
        positions = []
        for t in discovered_titles:
            pattern = r"\s+".join(re.escape(w) for w in t.split())
            m = re.search(pattern, doc)
            if m:
                positions.append((m.start(), t))

        positions.sort(key=lambda x: x[0])
        policies: Dict[str, str] = {}
        for i in range(len(positions)):
            start_pos, title = positions[i]
            end_pos = positions[i+1][0] if i + 1 < len(positions) else len(doc)
            slug = slugify(title)
            policies[slug] = doc[start_pos:end_pos].strip()

        # Map aliases for backwards compatibility with existing tools and queries
        for alias, keywords in COMMON_ALIASES.items():
            if alias not in policies:
                for k, v in list(policies.items()):
                    if any(kw in k for kw in keywords):
                        policies[alias] = v
                        break

        return policies
    except Exception as e:
        logger.error("Failed to parse PDF %s dynamically: %s. Using fallback.", path, e)
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
    """Retrieves the policy text for a given topic with smart fuzzy/token matching."""
    topic_normalized = slugify(topic)
    if topic_normalized in POLICIES:
        return POLICIES[topic_normalized]

    # Direct substring match with slugified keys
    for k, v in POLICIES.items():
        if topic_normalized in k or k in topic_normalized:
            return v

    # Check word tokens in topic against keys
    tokens = [t for t in topic_normalized.split("_") if len(t) >= 4]
    for token in tokens:
        for k, v in POLICIES.items():
            if token in k:
                return v

    return f"Tópico '{topic}' não encontrado. Tópicos disponíveis: {', '.join(AVAILABLE_POLICY_TOPICS)}"

def get_store_policy_summary() -> str:
    """Returns a full markdown summary of unique policy sections to embed in system prompt."""
    sections = []
    seen_texts = set()
    for topic, text in POLICIES.items():
        if text in seen_texts:
            continue
        seen_texts.add(text)
        title = topic.replace("_", " ").title()
        sections.append(f"#### {title}\n{text.strip()}")
    return "\n\n".join(sections)
