#!/usr/bin/env python3
"""
Script to generate the 5 official conversation examples using the current MusicStoreAgent.
Uses agent.chat() and agent.export_conversation_markdown() directly.
"""
import os
import sys
from pathlib import Path

# Ensure repository root is on sys.path when executed directly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.agent import MusicStoreAgent

SCENARIOS = [
    {
        "filename": "01_consulta_catalogo.md",
        "title": "01: Consulta ao Catálogo de Produtos e Regras de Pagamento",
        "turns": [
            "Olá, boa tarde! Quais opções de violões disponíveis vocês têm na loja custando até R$ 1.000?",
            "Quanto custa o Yamaha C40 e quanto fica com desconto no PIX? Dá para parcelar?"
        ]
    },
    {
        "filename": "02_informacoes_loja_e_horarios.md",
        "title": "02: Informações Institucionais e Horários de Atendimento",
        "turns": [
            "Qual é o endereço físico da loja de vocês e qual o horário de funcionamento hoje?",
            "Vocês abrem aos domingos ou feriados?"
        ]
    },
    {
        "filename": "03_status_e_rastreio_pedido.md",
        "title": "03: Consulta de Status e Rastreamento de Pedido com Autenticação LGPD",
        "turns": [
            "Oi, bom dia! Gostaria de consultar o andamento de uma compra que fiz com vocês. O número do pedido é 4.",
            "Meu e-mail cadastrado na compra é lucas.mendes@jmail.com"
        ]
    },
    {
        "filename": "04_fora_de_escopo_acessorios.md",
        "title": "04: Guardrails de Escopo (Acessórios e Conhecimento Geral)",
        "turns": [
            "Olá! Vocês vendem encordoamento D'Addario 0.10 para guitarra e um jogo de palhetas Dunlop?",
            "Entendi! E aproveitando, você sabe me dizer quem foi o primeiro homem a pisar na Lua?"
        ]
    },
    {
        "filename": "05_cenario_nao_trivial_hibrido.md",
        "title": "05: Cenário Não-Trivial Híbrido (Prazos de Devolução/Garantia e Registro de Reclamação Formal)",
        "turns": [
            "Olá! Fiz uma compra online com vocês (Pedido 1) e gostaria de solicitar a devolução por arrependimento. Meu e-mail é pedro.oliveira@jmail.com.",
            "Poxa, que decepção! O braço do violão Martin D-28 apresentou empenamento severo e eu esperava mais consideração. Quero registrar uma reclamação formal sobre isso!",
            "E o que eu faço com o violão?"
        ]
    }
]

def generate():
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)
    
    selected_args = sys.argv[1:]
    target_scenarios = SCENARIOS
    if selected_args:
        target_scenarios = [
            sc for sc in SCENARIOS
            if any(arg in sc["filename"] for arg in selected_args)
        ]
    
    for sc in target_scenarios:
        print(f"\n🎵 Generating {sc['filename']}...")
        agent = MusicStoreAgent()
        for turn_idx, user_msg in enumerate(sc["turns"], 1):
            print(f"  Turn {turn_idx}: {user_msg}")
            bot_reply = agent.chat(user_msg)
            print(f"  Reply preview: {bot_reply[:120].strip()}...")
        
        md_text = agent.export_conversation_markdown(title=sc["title"])
        out_file = examples_dir / sc["filename"]
        out_file.write_text(md_text, encoding="utf-8")
        print(f"  ✔ Saved {out_file}")

    print(f"\n✅ Generated {len(target_scenarios)} examples successfully!")

if __name__ == "__main__":
    generate()
