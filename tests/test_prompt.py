from src.prompt import format_system_prompt

def test_system_prompt_contains_crucial_elements():
    prompt = format_system_prompt()
    assert "Empório da Música" in prompt
    assert "Campo Grande" in prompt
    assert "acessórios" in prompt.lower()
    assert "pix" in prompt.lower()
    assert "entusiasmo" in prompt.lower()

    # A3: No generic promise in bullet instruction
    assert "até 12x sem juros ou 5% no pix" not in prompt.lower()

    # A5: General out-of-scope rule & removed invented phrase
    assert "conhecimentos gerais" in prompt.lower()
    assert "para garantir a máxima qualidade" not in prompt.lower()
    assert "instrumentos de sopro ou cordas orquestrais" in prompt.lower()
