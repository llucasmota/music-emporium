import streamlit as st
from src.agent import MusicStoreAgent
from src.config import settings

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
</style>
""", unsafe_allow_html=True)

# Sidebar with store information
with st.sidebar:
    st.title("🎸 Empório da Música")
    st.caption("Sua música começa aqui • Campo Grande/MS")
    st.markdown("---")
    st.markdown("**Status da Loja:**")
    st.markdown('<span class="store-badge">● Aberto</span> (Seg-Sex: 09h às 18h | Sáb: 09h às 13h)', unsafe_allow_html=True)
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

# Render message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Digite sua dúvida ou o instrumento que procura..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando instrumentos e políticas da loja..."):
            reply = st.session_state.agent.chat(prompt)
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
