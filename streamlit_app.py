import streamlit as st
import google.generativeai as genai

# Configuración del modelo Gemini
# La clave se jalará de forma segura desde los "Secrets" de Streamlit
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("⚠️ Configura la clave GEMINI_API_KEY en los Secrets de Streamlit.")

st.set_page_config(page_title="Agente IA - Selección Comfama", layout="wide")

st.title("🤖 Agente de Selección con Gemini")
st.write("Bienvenido, Axel. Analicemos perfiles para el Servicio Público de Empleo.")

# Interfaz
col1, col2 = st.columns(2)
with col1:
    vacante_txt = st.text_area("📝 Descripción de la Vacante", height=300)
with col2:
    cv_txt = st.text_area("👤 Texto de la Hoja de Vida", height=300)

if st.button("🚀 REALIZAR ANÁLISIS PSICOLÓGICO"):
    if vacante_txt and cv_txt:
        with st.spinner("Gemini está analizando..."):
            prompt = f"""
            Actúa como un psicólogo experto en selección de talento humano. 
            Compara la VACANTE con el CV y entrega un informe detallado:
            1. Datos demográficos y ubicación.
            2. Análisis de brechas (¿Qué le falta?).
            3. 3 preguntas clave para la entrevista basadas en irregularidades o puntos a profundizar.
            
            VACANTE: {vacante_txt}
            CV: {cv_txt}
            """
            response = model.generate_content(prompt)
            st.divider()
            st.markdown("### 📋 Informe de Selección")
            st.write(response.text)
    else:
        st.warning("Pega ambos textos para continuar.")
