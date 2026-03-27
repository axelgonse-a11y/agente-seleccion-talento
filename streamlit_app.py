import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import io

# CONFIGURACIÓN
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Error en la API Key")

def extraer_texto_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        return " ".join([p.extract_text() for p in pdf_reader.pages])
    except:
        return "[Error leyendo este archivo]"

st.set_page_config(page_title="Agente Selección Comfama", layout="wide")
st.title("🤖 Agente de Selección: Modo Unificado")

vacante_txt = st.text_area("📝 Requisitos de la Vacante:", height=150)
archivos = st.file_uploader("👤 Sube tus candidatos (PDF o Imagen):", type=["pdf", "jpg", "png"], accept_multiple_files=True)

if st.button("🚀 INICIAR ANÁLISIS"):
    if vacante_txt and archivos:
        with st.spinner("Preparando datos y consultando al Agente..."):
            
            # PASO 1: Consolidar toda la info en una sola variable
            cuerpo_analisis = ""
            for i, archivo in enumerate(archivos):
                if archivo.type == "application/pdf":
                    texto_cv = extraer_texto_pdf(archivo)
                    cuerpo_analisis += f"\n--- CANDIDATO {i+1} (Archivo: {archivo.name}) ---\n{texto_cv}\n"
                else:
                    # Para imágenes, pondremos un aviso (la carga masiva de fotos es más pesada)
                    cuerpo_analisis += f"\n--- CANDIDATO {i+1} (Imagen: {archivo.name}) ---\n[El Agente analizará esta imagen directamente]\n"

            # PASO 2: Una única petición a la IA con TODO el contenido
            prompt_unico = f"""
            Actúa como psicólogo de selección senior. 
            Tengo esta VACANTE: {vacante_txt}
            
            Y tengo estos CANDIDATOS:
            {cuerpo_analisis}
            
            POR FAVOR:
            1. Haz una tabla comparativa con: Nombre, Match %, Ubicación y Años de Experiencia.
            2. Selecciona a los 3 mejores (Top 3).
            3. Para cada uno de esos 3, dime 2 debilidades y 3 preguntas clave para la entrevista.
            """
            
            try:
                # Aquí está el truco: solo llamamos a la IA UNA VEZ
                response = model.generate_content(prompt_unico)
                
                st.divider()
                st.header("📊 Informe de Selección Unificado")
                st.markdown(response.text)
                st.success("¡Análisis completado en un solo paso!")
                
            except Exception as e:
                st.error(f"Hubo un problema con la consulta: {e}")
                st.info("Sugerencia: Prueba con máximo 5 archivos si son muy largos.")
    else:
        st.warning("Completa la vacante y sube archivos.")
