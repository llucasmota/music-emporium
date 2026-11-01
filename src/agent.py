import logging
from typing import Any, Dict, List, Optional
from google import genai
from google.genai import types
from src.config import settings
from src.database import init_database
from src.tools import create_tool_registry
from src.prompt import format_system_prompt

logger = logging.getLogger("music_emporium")

class MusicStoreAgent:
    """Core intelligent agent orchestrating the conversational loop with Google Gemini."""

    def __init__(self, db_conn=None, api_key: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        self.db_conn = db_conn or init_database()
        self.tool_registry = create_tool_registry(self.db_conn)
        self.system_prompt = format_system_prompt()
        self.history: List[Dict[str, Any]] = []
        
        # Tools list for Gemini client
        self.tools = list(self.tool_registry.values())

        if self.api_key and self.api_key != "fake-key":
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def reset_history(self) -> None:
        """Clears the conversational memory."""
        self.history = []

    def get_history(self) -> List[Dict[str, Any]]:
        """Returns the current conversation message history."""
        return self.history

    def chat(self, user_message: str) -> str:
        """Processes a customer message through the Gemini model with native tool-calling."""
        if not self.client:
            if settings.debug_mode:
                return "DEBUG ERROR: GEMINI_API_KEY não configurada no ambiente."
            return "Putz, arrebentou uma corda da guitarra aqui no meio do solo! 🎸 Estamos sem conexão com o sistema no momento. Por favor, verifique sua GEMINI_API_KEY no arquivo .env!"

        # Record user message in memory
        self.history.append({"role": "user", "content": user_message})

        try:
            # Build conversation contents for the Gemini API
            contents = []
            for msg in self.history:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])]
                ))

            config = types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                tools=self.tools,
                temperature=0.4,
            )

            # Execution loop for tool calls
            max_iterations = 5
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                response = self.client.models.generate_content(
                    model=settings.model_name,
                    contents=contents,
                    config=config,
                )

                if not response.candidates:
                    break

                candidate = response.candidates[0]
                model_content = candidate.content
                contents.append(model_content)

                # Check if model requested function calls
                function_calls = [p.function_call for p in model_content.parts if p.function_call]
                if not function_calls:
                    # Final text response
                    reply_text = "".join([p.text for p in model_content.parts if p.text])
                    self.history.append({"role": "assistant", "content": reply_text})
                    return reply_text

                # Execute requested functions
                tool_response_parts = []
                for fc in function_calls:
                    fn_name = fc.name
                    fn_args = dict(fc.args) if fc.args else {}
                    
                    if settings.debug_mode:
                        logger.info(f"⚙ Executando tool: {fn_name}({fn_args})")
                    
                    if fn_name in self.tool_registry:
                        fn = self.tool_registry[fn_name]
                        result = fn(**fn_args)
                    else:
                        result = {"error": f"Tool '{fn_name}' não encontrada."}

                    tool_response_parts.append(types.Part.from_function_response(
                        name=fn_name,
                        response={"result": result}
                    ))

                # Feed function results back to the conversation
                contents.append(types.Content(
                    role="tool",
                    parts=tool_response_parts
                ))

            fallback_msg = "Desculpe, precisei fazer muitas consultas ao sistema e não consegui concluir. Pode reformular sua dúvida?"
            self.history.append({"role": "assistant", "content": fallback_msg})
            return fallback_msg

        except Exception as e:
            if settings.debug_mode:
                return f"[DEBUG EXCEPTION]: {str(e)}"
            return "Ops! Parece que o nosso cabo deu um mau contato aqui na linha. 🎸 Me manda essa mensagem de novo em um minutinho pra gente afinar a conversa?"

    def export_conversation_markdown(self, title: str = "Atendimento Empório da Música") -> str:
        """Exports the current session into clean GitHub Markdown format."""
        lines = [f"# Exemplo de Interação: {title}\n"]
        for msg in self.history:
            role = "Cliente" if msg["role"] == "user" else "Atendente (Empório da Música)"
            lines.append(f"**{role}:**\n{msg['content']}\n")
        return "\n".join(lines)
