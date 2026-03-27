import streamlit as st
import google.generativeai as genai

# Configuración mínima
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🤖 Agente de Selección - Modo Seguro")

# Usar texto en lugar de archivos para asegurar que funcione
vacante = st.text_area("1. Requisitos de la Vacante")
cv_texto = st.text_area("2. Pega aquí el texto de la Hoja de Vida")

if st.button("Analizar Ahora"):
    if vacante and cv_texto:
        try:
            # Enviamos solo lo esencial
            prompt = f"Compara brevemente. Vacante: {vacante}. CV: {cv_texto}. Dame Match% y 3 preguntas."
            response = model.generate_content(prompt)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Error: {e}. Intenta copiar menos texto.")
