import pytest
from src.knowledge import get_policy_topic, get_store_policy_summary, AVAILABLE_POLICY_TOPICS

def test_available_topics():
    assert "trocas_devolucoes" in AVAILABLE_POLICY_TOPICS
    assert "formas_pagamento" in AVAILABLE_POLICY_TOPICS
    assert "frete_entregas" in AVAILABLE_POLICY_TOPICS

def test_get_policy_returns_accurate_terms():
    devolucao_text = get_policy_topic("trocas_devolucoes")
    assert "7 (sete) dias" in devolucao_text
    assert "arrependimento" in devolucao_text.lower()

def test_store_summary_includes_crucial_guardrails():
    summary = get_store_policy_summary()
    assert "não comercializamos acessórios" in summary.lower() or "exclusivamente com instrumentos" in summary.lower()
