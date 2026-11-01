import pytest
from src.agent import MusicStoreAgent

def test_agent_initialization():
    agent = MusicStoreAgent(api_key="fake-key")
    assert agent is not None
    assert len(agent.history) == 0

def test_agent_history_reset():
    agent = MusicStoreAgent(api_key="fake-key")
    agent.history.append({"role": "user", "content": "Olá"})
    assert len(agent.history) == 1
    agent.reset_history()
    assert len(agent.history) == 0

def test_agent_export_markdown():
    agent = MusicStoreAgent(api_key="fake-key")
    agent.history.append({"role": "user", "content": "Vocês têm violão?"})
    agent.history.append({"role": "assistant", "content": "Temos sim! Temos o Yamaha C40."})
    md = agent.export_conversation_markdown("Teste")
    assert "Vocês têm violão?" in md
    assert "Yamaha C40" in md
    assert "Atendente (Empório da Música)" in md
