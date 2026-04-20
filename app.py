import os
from typing import Any, Dict, List

import streamlit as st
from anthropic import Anthropic

# ---------------------------------
# Configuración de la página
# ---------------------------------
st.set_page_config(
    page_title="LogicAI",
    page_icon="🧠",
    layout="wide"
)

# ---------------------------------
# Cargar API key
# ---------------------------------
def load_api_key():
    if "ANTHROPIC_API_KEY" in st.secrets:
        return st.secrets["ANTHROPIC_API_KEY"]
    return os.getenv("ANTHROPIC_API_KEY")

api_key = load_api_key()

if not api_key:
    st.error("No encontré tu ANTHROPIC_API_KEY. Agrégala en secrets o variables de entorno.")
    st.stop()

client = Anthropic(api_key=api_key)

# ---------------------------------
# Personalidad LogicAI
# ---------------------------------
SYSTEM_PROMPT = """
Eres LogicAI, un asistente de inteligencia artificial ético, profesional y experto en razonamiento complejo.

Reglas:
- Sé claro, preciso y estructurado.
- Explica paso a paso cuando sea necesario.
- No inventes información.
- Señala incertidumbre si existe.
- Da pros, contras y conclusiones en decisiones.
- Mantén tono profesional.
"""

# ---------------------------------
# Estado del chat
# ---------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hola, soy LogicAI. ¿En qué puedo ayudarte?"
        }
    ]

# ---------------------------------
# Sidebar
# ---------------------------------
with st.sidebar:
    st.title("LogicAI")

    model = st.selectbox(
        "Modelo",
        ["claude-opus-4-7", "claude-haiku-4-5"]
    )

    temperature = st.slider("Temperatura", 0.0, 1.0, 0.3)
    max_tokens = st.slider("Max tokens", 256, 4096, 1200)

    if st.button("Limpiar chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Chat reiniciado."}
        ]
        st.rerun()

# ---------------------------------
# Función para formatear mensajes
# ---------------------------------
def format_messages(messages: List[Dict[str, str]]):
    return [
        {"role": m["role"], "content": m["content"]}
        for m in messages
        if m["role"] in ["user", "assistant"]
    ]

# ---------------------------------
# Obtener respuesta
# ---------------------------------
def get_response(messages):
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=SYSTEM_PROMPT,
        messages=format_messages(messages)
    )

    text = ""
    for block in response.content:
        if block.type == "text":
            text += block.text

    return text

# ---------------------------------
# Interfaz
# ---------------------------------
st.title("🧠 LogicAI")
st.write("Asistente de razonamiento avanzado")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Escribe aquí...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                reply = get_response(st.session_state.messages)
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                error = f"Error: {e}"
                st.error(error)
                st.session_state.messages.append({"role": "assistant", "content": error})
