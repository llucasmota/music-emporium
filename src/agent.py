import uuid
import logging
from typing import Any, Dict, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from src.config import settings
from src.database import init_database
from src.tools import create_langchain_tools
from src.prompt import format_system_prompt

logger = logging.getLogger("music_emporium")

class MusicStoreAgent:
    """Intelligent customer service agent orchestrated by LangGraph StateGraph with Google Gemini."""

    def __init__(self, db_conn=None, api_key: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        self.db_conn = db_conn or init_database()
        self.tools = create_langchain_tools(self.db_conn)
        self.system_prompt = format_system_prompt()
        self.thread_id = str(uuid.uuid4())
        self.memory = MemorySaver()
        self.history: List[Dict[str, Any]] = []
        self.last_tool_calls: List[str] = []

        if self.api_key and self.api_key != "fake-key":
            self.llm = ChatGoogleGenerativeAI(
                model=settings.model_name,
                google_api_key=self.api_key,
            )
            self.model_with_tools = self.llm.bind_tools(self.tools)
            self.graph = self._build_graph()
        else:
            self.llm = None
            self.graph = None

    def _build_graph(self):
        """Constructs the LangGraph StateGraph: START -> agent -> tools_condition -> tools -> agent -> END."""
        def call_model(state: MessagesState):
            current_prompt = format_system_prompt()
            messages = [SystemMessage(content=current_prompt)] + state["messages"]
            response = self.model_with_tools.invoke(messages)
            return {"messages": [response]}

        workflow = StateGraph(MessagesState)
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", ToolNode(self.tools))

        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges("agent", tools_condition)
        workflow.add_edge("tools", "agent")

        return workflow.compile(checkpointer=self.memory)

    def reset_history(self) -> None:
        """Clears the conversational memory and starts a new thread."""
        self.history = []
        self.thread_id = str(uuid.uuid4())

    def get_history(self) -> List[Dict[str, Any]]:
        """Returns the current conversation message history."""
        return self.history

    def chat(self, user_message: str) -> str:
        """Processes a customer message through the LangGraph agent graph."""
        if not self.graph:
            if settings.debug_mode:
                return "DEBUG ERROR: GEMINI_API_KEY não configurada no ambiente."
            return "Putz, arrebentou uma corda da guitarra aqui no meio do solo! 🎸 Estamos sem conexão com o sistema no momento. Por favor, verifique sua GEMINI_API_KEY no arquivo .env!"

        # Record user message
        self.history.append({"role": "user", "content": user_message})

        try:
            config = {"configurable": {"thread_id": self.thread_id}}
            inputs = {"messages": [HumanMessage(content=user_message)]}

            output = self.graph.invoke(inputs, config=config)
            
            # Record executed tool calls
            self.last_tool_calls = [
                tc["name"]
                for msg in output.get("messages", [])
                if hasattr(msg, "tool_calls")
                for tc in getattr(msg, "tool_calls", [])
            ]

            final_message = output["messages"][-1]
            reply_text = final_message.content

            if isinstance(reply_text, list):
                # If multimodal or structured parts
                reply_text = "".join([str(p.get("text", p)) if isinstance(p, dict) else str(p) for p in reply_text])

            self.history.append({"role": "assistant", "content": reply_text})
            return reply_text

        except Exception as e:
            logger.exception("Error during agent processing: %s", e)
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
