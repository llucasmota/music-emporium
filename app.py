import warnings
warnings.filterwarnings("ignore")

import re
from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
from src.agent import MusicStoreAgent
from src.config import settings
from src.calendar_utils import is_store_open

def get_store_status_badge() -> str:
    """Calculates whether store is open based on current time in Campo Grande/MS (manual §2)."""
    try:
        now_cg = datetime.now(ZoneInfo("America/Campo_Grande"))
    except Exception:
        now_cg = datetime.now()

    is_open, desc = is_store_open(now_cg)
    time_label = now_cg.strftime("%H:%M")
    if is_open:
        return f'<span class="store-badge" style="background-color: #2e7d32;">● Aberto</span> ({time_label})'
    else:
        return f'<span class="store-badge" style="background-color: #d32f2f;">○ Fechado</span> ({time_label})'

st.set_page_config(
    page_title="Empório da Música — Atendimento Virtual",
    page_icon="🎸",
    layout="centered"
)

# Custom CSS for styling
st.markdown("""
<style>
    .store-badge {
        background-color: #2e7d32;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* Musical Loading Animation */
    .music-loader-box {
        display: inline-flex;
        align-items: center;
        gap: 14px;
        padding: 10px 18px;
        border-radius: 12px;
        background: rgba(46, 125, 50, 0.08);
        border: 1px solid rgba(46, 125, 50, 0.3);
        margin: 6px 0;
        animation: fadeIn 0.3s ease-in;
    }

    .equalizer {
        display: flex;
        align-items: flex-end;
        gap: 4px;
        height: 24px;
    }

    .eq-bar {
        width: 4px;
        background: linear-gradient(180deg, #81c784 0%, #2e7d32 100%);
        border-radius: 3px;
        animation: bounceBar 0.9s infinite ease-in-out alternate;
    }

    .bar1 { height: 8px; animation-delay: 0.1s; }
    .bar2 { height: 18px; animation-delay: 0.35s; }
    .bar3 { height: 24px; animation-delay: 0.15s; }
    .bar4 { height: 14px; animation-delay: 0.45s; }
    .bar5 { height: 20px; animation-delay: 0.25s; }

    @keyframes bounceBar {
        0% { height: 6px; }
        100% { height: 24px; }
    }

    .loader-label {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.92rem;
        font-weight: 500;
    }

    .guitar-icon {
        display: inline-block;
        font-size: 1.1rem;
        animation: rockGuitar 0.7s infinite ease-in-out alternate;
        transform-origin: bottom center;
    }

    @keyframes rockGuitar {
        0% { transform: rotate(-10deg) scale(0.95); }
        100% { transform: rotate(12deg) scale(1.05); }
    }

    .note {
        display: inline-block;
        font-size: 1.1rem;
        color: #2e7d32;
        font-weight: bold;
        animation: floatNote 1.4s infinite ease-in-out;
        opacity: 0;
    }

    .note-1 { animation-delay: 0.1s; }
    .note-2 { animation-delay: 0.6s; }

    @keyframes floatNote {
        0% { transform: translateY(4px) scale(0.8); opacity: 0; }
        50% { opacity: 0.95; }
        100% { transform: translateY(-14px) scale(1.15); opacity: 0; }
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(4px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# Sidebar with store information
with st.sidebar:
    st.title("🎸 Empório da Música")
    st.caption("Sua música começa aqui • Campo Grande/MS")
    st.markdown("---")
    st.markdown("**Status da Loja:**")
    st.markdown(f'{get_store_status_badge()} (Seg-Sex: 09h às 18h | Sáb: 09h às 13h)', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Localização & Contato:**")
    st.write("Rua 14 de Maio, 3200 — Centro")
    st.write("Telefone / WhatsApp: (67) 3341-4444")
    st.write("contato@emporiodamusica.com.br")
    st.markdown("---")
    if st.button("🔄 Reiniciar Conversa", use_container_width=True):
        st.session_state.agent = MusicStoreAgent()
        st.session_state.messages = []
        st.rerun()

# Check for API key
if not settings.gemini_api_key:
    st.warning("⚠️ **GEMINI_API_KEY** não foi configurada no arquivo `.env`. Configure sua chave gratuita do Google AI Studio para interagir com o agente.")

# Initialize session state
if "agent" not in st.session_state:
    st.session_state.agent = MusicStoreAgent()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Seja muito bem-vindo à **Empório da Música**! 🎸\n\nEu sou o atendente virtual da loja. Como posso te ajudar hoje a encontrar seu próximo som ou tirar alguma dúvida sobre pedidos e instrumentos?"}
    ]

st.title("Atendimento ao Cliente")
st.caption("Converse sobre instrumentos, preços, status de pedidos e políticas da loja.")

def format_for_display(text: str) -> str:
    """Formats Markdown for Streamlit: ensures newlines before bullets and escapes $ for KaTeX."""
    if not isinstance(text, str):
        return text
    # Ensure bullets start on their own line
    text = re.sub(r'([^\n])\s*•\s*', r'\1\n• ', text)
    # Escape R$ to R\$ for Streamlit KaTeX
    return text.replace(r"R\$", "R$").replace("R$", r"R\$")

# Render message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(format_for_display(msg["content"]))

# User input
if prompt := st.chat_input("Digite sua dúvida ou o instrumento que procura..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(format_for_display(prompt))

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("""
        <div class="music-loader-box">
            <div class="equalizer">
                <span class="eq-bar bar1"></span>
                <span class="eq-bar bar2"></span>
                <span class="eq-bar bar3"></span>
                <span class="eq-bar bar4"></span>
                <span class="eq-bar bar5"></span>
            </div>
            <div class="loader-label">
                <span class="guitar-icon">🎸</span>
                <span>Afinando os instrumentos e consultando o estoque...</span>
                <span class="note note-1">♪</span>
                <span class="note note-2">♫</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        reply = st.session_state.agent.chat(prompt)
        message_placeholder.markdown(format_for_display(reply))
        st.session_state.messages.append({"role": "assistant", "content": reply})
