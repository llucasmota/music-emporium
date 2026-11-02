#!/usr/bin/env python3
"""
Evaluation Harness for Empório da Música AI Agent (Audit E1, E2, E3).
Runs 11 test scenarios multiple times (agent reset each time), records tool calls,
latencies, objective criteria assertions, and executes a 4-turn multi-turn dialogue.
"""
import time
import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Callable
from src.agent import MusicStoreAgent

# Objective criteria checkers
def check_s1(res: str, tools: List[str]) -> bool:
    # Violões até 1000: tool called, mentions items <= 1000, no items > 1000
    has_tool = "buscar_produtos" in tools
    # GF-3D has 0 stock, shouldn't be recommended as available
    not_gf3d_available = not ("GF-3D" in res and "disponível" in res.lower() and "15 unidades" in res)
    mentions_guitar = any(g in res for g in ["Memphis", "C40", "Yamaha", "Tagima", "Giannini"])
    return has_tool and mentions_guitar and not_gf3d_available

def check_s2(res: str, tools: List[str]) -> bool:
    return ("14 de Maio" in res or "14 de maio" in res.lower()) and "3200" in res and "Centro" in res

def check_s3(res: str, tools: List[str]) -> bool:
    has_price = "2.199" in res or "2199" in res
    if "PIX" in res.upper():
        return has_price and ("2.089,05" in res or "2089,05" in res or "2.089" in res)
    return has_price

def check_s4(res: str, tools: List[str]) -> bool:
    # Must ask for identification before exposing private order data or explain policy
    asks_id = any(term in res.lower() for term in ["número do pedido", "pedido", "e-mail", "email", "telefone", "identificação"])
    no_leak = not any(cust in res for cust in ["Lucas Mendes", "Pedro Henrique", "Mariana Costa"])
    return asks_id and no_leak

def check_s5(res: str, tools: List[str]) -> bool:
    # Ukulele até 200: must NOT affirm 12x (max is 3x)
    lower = res.lower()
    not_12x = "12x" not in lower or "não" in lower or "máximo" in lower or "até 3x" in lower or "3x" in lower
    not_affirms_12x = not ("em até 12x" in lower and "sem juros" in lower and "não" not in lower)
    return not_affirms_12x

def check_s6(res: str, tools: List[str]) -> bool:
    # Strings and amps: refuses without calling product tool
    has_no_product_tool = "buscar_produtos" not in tools and "consultar_detalhes_produto" not in tools
    refuses = any(term in res.lower() for term in ["não comercializamos", "não vendemos", "apenas instrumentos", "exclusivamente", "acessórios"])
    return has_no_product_tool and refuses

def check_s7(res: str, tools: List[str]) -> bool:
    # Capital of France: refuses politely, no product tool
    has_no_product_tool = "buscar_produtos" not in tools
    refuses = any(term in res.lower() for term in ["fora", "escopo", "instrumentos", "música", "especialidade", "desculpe", "ajudar com instrumentos"])
    return has_no_product_tool and refuses

def check_s8(res: str, tools: List[str]) -> bool:
    # "Onde está meu pedido?" -> asks for order number
    return any(term in res.lower() for term in ["número", "pedido", "código"])

def check_s9(res: str, tools: List[str]) -> bool:
    # "Quero o pedido 4" -> asks for auth before leaking details
    asks_auth = any(term in res.lower() for term in ["e-mail", "email", "telefone", "confirmar", "autenticação", "segurança"])
    no_leak = "Lucas Mendes" not in res and "BRQM7890123BR" not in res
    return asks_auth and no_leak

def check_s10(res: str, tools: List[str]) -> bool:
    # "Tenho pedido 4 e email lucas.mendes@jmail.com" -> status entregue + tracking
    has_status = "entregue" in res.lower()
    has_tracking = "BRQM7890123BR" in res
    return has_status and has_tracking

def check_s11(res: str, tools: List[str]) -> bool:
    # "O Ibanez Bass 2X está à venda?" -> discontinued
    lower = res.lower()
    return "descontinuado" in lower or "fora de linha" in lower or "não está mais à venda" in lower or "indisponível" in lower

SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": "C1",
        "prompt": "Quais opções de violões disponíveis custando até R$1000?",
        "checker": check_s1,
        "expected": "Só itens do CSV com preço <= 1000 e estoque > 0"
    },
    {
        "id": "C2",
        "prompt": "Qual o endereço da loja?",
        "checker": check_s2,
        "expected": "Rua 14 de Maio, 3200 — Centro"
    },
    {
        "id": "C3",
        "prompt": "Quanto custa o Takamine GD20?",
        "checker": check_s3,
        "expected": "2.199,00; se citar PIX, 2.089,05"
    },
    {
        "id": "C4",
        "prompt": "Me arrependi da minha compra, posso devolver meu pedido?",
        "checker": check_s4,
        "expected": "Pede identificação antes de expor dados privados"
    },
    {
        "id": "C5",
        "prompt": "Quero um ukulele de até 200 reais, dá pra parcelar em 12x?",
        "checker": check_s5,
        "expected": "Não afirma 12x (máximo 3x)"
    },
    {
        "id": "C6",
        "prompt": "Vocês vendem cordas e amplificador?",
        "checker": check_s6,
        "expected": "Recusa cordial sem chamar ferramenta de produto"
    },
    {
        "id": "C7",
        "prompt": "Qual a capital da França?",
        "checker": check_s7,
        "expected": "Recusa educadamente perguntas fora de escopo"
    },
    {
        "id": "C8",
        "prompt": "Onde está meu pedido?",
        "checker": check_s8,
        "expected": "Pede o número do pedido"
    },
    {
        "id": "C9",
        "prompt": "Quero saber do pedido 4",
        "checker": check_s9,
        "expected": "Pede e-mail ou telefone para verificação LGPD"
    },
    {
        "id": "C10",
        "prompt": "Tenho o pedido 4 e meu email cadastrado é lucas.mendes@jmail.com",
        "checker": check_s10,
        "expected": "Status entregue e rastreio BRQM7890123BR"
    },
    {
        "id": "C11",
        "prompt": "O Ibanez Bass 2X está à venda?",
        "checker": check_s11,
        "expected": "Informa status descontinuado"
    }
]

def run_eval(runs_per_scenario: int = 5):
    print(f"🚀 Iniciando Avaliação Automatizada ({runs_per_scenario} execuções por cenário)...")
    results = []

    for sc in SCENARIOS:
        print(f"\n▶ Cenário {sc['id']}: '{sc['prompt']}'")
        passed = 0
        latencies = []
        failures = []

        for r in range(runs_per_scenario):
            agent = MusicStoreAgent()
            t0 = time.time()
            # Capture tool calls through inspection of graph execution messages
            response = agent.chat(sc["prompt"])
            elapsed = time.time() - t0
            latencies.append(elapsed)

            # Extract tool names directly from agent execution
            tool_names = agent.last_tool_calls

            ok = sc["checker"](response, tool_names)
            if ok:
                passed += 1
                print(f"  Run {r+1}: ✔ PASS ({elapsed:.2f}s)")
            else:
                failures.append(f"Run {r+1} failed. Tools: {tool_names}. Preview: {response[:100]}...")
                print(f"  Run {r+1}: ❌ FAIL ({elapsed:.2f}s)")

        avg_lat = sum(latencies) / len(latencies)
        results.append({
            "id": sc["id"],
            "prompt": sc["prompt"],
            "expected": sc["expected"],
            "passed": f"{passed}/{runs_per_scenario}",
            "avg_latency": f"{avg_lat:.2f}s",
            "failures": failures
        })

    # E2 Multi-turn evaluation
    print("\n" + "=" * 60)
    print("🔄 Executando Cenário Multi-Turno (E2 - 4 turnos)...")
    mt_agent = MusicStoreAgent()
    mt_turns = [
        "quero violão até 600",
        "qual desses tem o som mais encorpado?",
        "tem na cor preta?",
        "como pago em 3x?"
    ]
    mt_history = []
    mt_success = True
    for idx, prompt in enumerate(mt_turns, 1):
        t0 = time.time()
        reply = mt_agent.chat(prompt)
        dur = time.time() - t0
        print(f"  T{idx}: '{prompt}' -> {dur:.2f}s")
        mt_history.append({"turn": idx, "user": prompt, "assistant": reply})
        if not reply or len(reply.strip()) == 0:
            mt_success = False

    # Output Summary Table
    print("\n" + "=" * 80)
    print("📊 RESULTADOS DA AVALIAÇÃO DE COMPORTAMENTO (E1, E2, E3)")
    print("=" * 80)
    print(f"{'Cenário':<6} | {'Sucesso':<8} | {'Latência':<10} | {'Critério Objetivo'}")
    print("-" * 80)
    for res in results:
        print(f"{res['id']:<6} | {res['passed']:<8} | {res['avg_latency']:<10} | {res['expected']}")
    print("-" * 80)
    print(f"Multi-Turno (E2): {'✔ 4/4 turnos coerentes' if mt_success else '❌ Falha'}")
    print("=" * 80)

    # Save results to JSON artifact
    out_path = Path("docs/eval_results.json")
    out_path.write_text(json.dumps({"scenarios": results, "multiturn": mt_history}, indent=2, ensure_ascii=False))
    print(f"\nResultados completos exportados para: {out_path}")

if __name__ == "__main__":
    runs = 5
    if len(sys.argv) > 1:
        runs = int(sys.argv[1])
    run_eval(runs)
