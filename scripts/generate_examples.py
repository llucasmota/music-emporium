#!/usr/bin/env python3
"""
Script to generate the 5 official conversation examples using the current MusicStoreAgent.
Uses agent.chat() and agent.export_conversation_markdown() directly.
"""
import os
import sys
from pathlib import Path
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
            "Poxa, que decepção! O violão começou a apresentar problemas e eu esperava mais consideração. Quero registrar uma reclamação formal sobre isso!",
            "O braço do violão Martin D-28 apresentou empenamento severo. Pode registrar a queixa para o meu e-mail pedro.oliveira@jmail.com referente ao pedido 1."
        ]
    }
]

def generate():
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)
    
    for sc in SCENARIOS:
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

    print("\n✅ All 5 examples successfully generated!")

if __name__ == "__main__":
    generate()
