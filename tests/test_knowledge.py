import pytest
from src.knowledge import get_policy_topic, get_store_policy_summary, AVAILABLE_POLICY_TOPICS

def test_available_topics():
    assert "trocas_devolucoes" in AVAILABLE_POLICY_TOPICS
    assert "formas_pagamento" in AVAILABLE_POLICY_TOPICS
    assert "frete_entregas" in AVAILABLE_POLICY_TOPICS
    assert "promocoes" in AVAILABLE_POLICY_TOPICS
    assert "situacoes_especiais" in AVAILABLE_POLICY_TOPICS
    assert "privacidade" in AVAILABLE_POLICY_TOPICS

def test_get_policy_returns_accurate_terms():
    devolucao_text = get_policy_topic("trocas_devolucoes")
    assert "7 (sete) dias" in devolucao_text
    assert "arrependimento" in devolucao_text.lower()
    # A4: MUST NOT contain "lacrada" (manual §4.3: "em perfeito estado e na embalagem original")
    assert "lacrada" not in devolucao_text.lower()
    assert "em perfeito estado e na embalagem original" in devolucao_text.lower()

    # A4: Topics promocoes, situacoes_especiais, privacidade
    promo_text = get_policy_topic("promocoes")
    assert "cumulativas" in promo_text.lower()
    assert "rain check" in promo_text.lower()

    sit_text = get_policy_topic("situacoes_especiais")
    assert "descontinuado" in sit_text.lower()
    assert "24 horas úteis" in sit_text.lower()

    priv_text = get_policy_topic("privacidade")
    assert "lgpd" in priv_text.lower()
    assert "terceiros" in priv_text.lower()

def test_store_summary_includes_crucial_guardrails():
    summary = get_store_policy_summary()
    assert "não comercializamos acessórios" in summary.lower() or "exclusivamente com instrumentos" in summary.lower()

def test_load_policies_directly_from_pdf():
    from src.knowledge import load_policies_from_pdf, POLICIES
    policies = load_policies_from_pdf()
    assert len(policies) == 10
    assert "sobre_a_loja" in policies
    assert "trocas_devolucoes" in policies
    assert "disposicoes_finais" in policies
    # Confirm verbatim PDF content without transcription drift
    assert "reembolso na hora" not in policies["trocas_devolucoes"].lower()
    assert "diferenças de valor serão cobradas ou reembolsadas conforme o caso" in policies["trocas_devolucoes"].lower()

