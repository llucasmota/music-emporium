import warnings
warnings.filterwarnings("ignore")

import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from src.agent import MusicStoreAgent
from src.config import settings

console = Console()

def display_welcome_banner():
    banner = """[bold cyan]╔═══════════════════════════════════════════════════════════════╗[/bold cyan]
[bold cyan]║[/bold cyan]   [bold yellow]🎸 EMPÓRIO DA MÚSICA — ATENDIMENTO VIRTUAL INTELIGENTE[/bold yellow]     [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]   [italic]Sua música começa aqui • Campo Grande / MS[/italic]                  [bold cyan]║[/bold cyan]
[bold cyan]╚═══════════════════════════════════════════════════════════════╝[/bold cyan]

[dim]Comandos: [bold]/export[/bold] (salvar conversa em .md) | [bold]/reset[/bold] (reiniciar chat) | [bold]/sair[/bold] (encerrar)[/dim]
"""
    console.print(banner)

def main():
    display_welcome_banner()

    if not settings.gemini_api_key:
        console.print(Panel(
            "[bold red]ATENÇÃO: GEMINI_API_KEY não encontrada no arquivo .env![/bold red]\n\n"
            "1. Crie uma chave gratuita no Google AI Studio: [underline]https://aistudio.google.com/[/underline]\n"
            "2. Copie o arquivo [bold].env.example[/bold] para [bold].env[/bold] e cole sua chave:\n"
            "   [bold green]GEMINI_API_KEY=sua_chave_aqui[/bold green]\n"
            "3. Execute o programa novamente.",
            title="Configuração Necessária",
            border_style="red"
        ))
        sys.exit(1)

    agent = MusicStoreAgent()
    console.print("[green]● Assistente online e pronto para atendimento![/green]\n")

    while True:
        try:
            user_input = console.input("[bold purple]Você > [/bold purple]").strip()
            if not user_input:
                continue

            if user_input.lower() in ["/sair", "sair", "exit", "quit"]:
                console.print("\n[yellow]Atendimento encerrado. A Empório da Música agradece sua visita! 🎸[/yellow]")
                break

            if user_input.lower() == "/reset":
                agent.reset_history()
                console.print("[dim italic]Histórico de conversa reiniciado.[/dim italic]\n")
                continue

            if user_input.lower().startswith("/export"):
                parts = user_input.split(" ", 1)
                filename = parts[1] if len(parts) > 1 else "conversa_exportada.md"
                if not filename.endswith(".md"):
                    filename += ".md"
                
                export_dir = settings.project_root / "examples"
                export_dir.mkdir(exist_ok=True)
                export_path = export_dir / filename
                
                md_content = agent.export_conversation_markdown(title=filename.replace(".md", ""))
                with open(export_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
                console.print(f"[bold green]✔ Conversa salva com sucesso em:[/bold green] [underline]{export_path}[/underline]\n")
                continue

            with console.status("[bold cyan]Consultando sistema da loja...[/bold cyan]", spinner="dots"):
                response = agent.chat(user_input)

            console.print()
            console.print(Panel(
                Markdown(response),
                title="[bold green]Atendente Empório da Música[/bold green]",
                border_style="green",
                padding=(1, 2)
            ))
            console.print()

        except KeyboardInterrupt:
            console.print("\n[yellow]Sessão interrompida pelo usuário. Até logo![/yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]Erro inesperado:[/bold red] {e}")

if __name__ == "__main__":
    main()
