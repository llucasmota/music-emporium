from src.prompt import format_system_prompt

def test_system_prompt_contains_crucial_elements():
    prompt = format_system_prompt()
    assert "Empório da Música" in prompt
    assert "Campo Grande" in prompt
    assert "acessórios" in prompt.lower()
    assert "pix" in prompt.lower()
    assert "entusiasmo" in prompt.lower()
