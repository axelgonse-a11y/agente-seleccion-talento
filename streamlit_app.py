import streamlit as st
import google.generativeai as genai
import PyPDF2

# Configuración de Gemini
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("⚠️ Falta la configuración de la clave en Secrets.")

# Función para extraer texto del PDF
def leer_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    texto = ""
    for pagina in pdf_reader.pages:
        texto += pagina.extract_text()
    return texto

st.set_page_config(page_title="Agente IA - Selección Comfama", layout="wide")

st.title("🤖 Agente de Selección: Analizador de PDFs")
st.write("Axel, ahora puedes subir directamente las hojas de vida en formato PDF.")

# INTERFAZ
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Descripción de la Vacante")
    vacante_txt = st.text_area("Pega los requisitos aquí...", height=250)

with col2:
    st.subheader("👤 Hoja de Vida (PDF)")
    archivo_pdf = st.file_uploader("Sube el PDF del candidato", type=["pdf"])

# PROCESAMIENTO
if st.button("🚀 ANALIZAR CANDIDATO"):
    if vacante_txt and archivo_pdf:
        with st.spinner("Leyendo PDF y analizando con Gemini..."):
            # 1. Convertimos el PDF a texto
            cv_txt = leer_pdf(archivo_pdf)
            
            # 2. Creamos el prompt para Gemini
            prompt = f"""
            Actúa como un psicólogo experto en selección. 
            Analiza esta VACANTE y este CV extraído de un PDF.
            
            VACANTE: {vacante_txt}
            CV: {cv_txt}
            
            Entrega un informe con:
            1. Datos clave (Nombre, contacto, ubicación).
            2. Análisis de brechas técnico-humanas.
            3. 3 preguntas sugeridas para la entrevista.
            """
            
            # 3. Le pedimos la respuesta a Gemini
            response = model.generate_content(prompt)
            st.divider()
            st.markdown("### 📋 Informe del Agente")
            st.write(response.text)
    else:
        st.warning("Asegúrate de pegar la vacante y subir el PDF.")
