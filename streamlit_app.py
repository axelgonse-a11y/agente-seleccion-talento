import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import pandas as pd

# Configuración de Gemini
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("🔑 Error: No se encontró la clave en los Secrets de Streamlit.")

def extraer_texto_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    return "".join([p.extract_text() for p in pdf_reader.pages])

st.set_page_config(page_title="Agente Selección Comfama", layout="wide")
st.title("🏆 Agente de Selección Masiva: El Top 5 de Axel")

# 1. LA VACANTE (Lo que te entrega la gestora)
st.header("1. Definición de la Vacante")
vacante_txt = st.text_area("Pega aquí los requisitos (Ubicación, Experiencia, Género, etc.):", 
                           placeholder="Ej: Necesito hombre para Chigorodó con 2 años de experiencia...",
                           height=150)

# 2. LAS HOJAS DE VIDA
st.header("2. Carga de Candidatos")
archivos = st.file_uploader("Sube hasta 20 archivos (PDF o Fotos)", 
                             type=["pdf", "jpg", "png"], 
                             accept_multiple_files=True)

# 3. EL PROCESO
if st.button("🚀 INICIAR ANÁLISIS DE GRUPO"):
    if vacante_txt and archivos:
        resultados_individuales = []
        barra = st.progress(0)
        
        for i, archivo in enumerate(archivos):
            with st.spinner(f"Analizando a: {archivo.name}..."):
                if archivo.type == "application/pdf":
                    contenido = extraer_texto_pdf(archivo)
                    instruccion = f"Analiza este CV contra la vacante: {vacante_txt}. Datos del CV: {contenido}. Resume: Nombre, Ubicación, Años Exp, % de Match (0-100)."
                    resp = model.generate_content(instruccion)
                else:
                    img = Image.open(archivo)
                    instruccion = f"Analiza esta imagen contra la vacante: {vacante_txt}. Resume: Nombre, Ubicación, Años Exp, % de Match (0-100)."
                    resp = model.generate_content([instruccion, img])
                
                resultados_individuales.append(resp.text)
            barra.progress((i + 1) / len(archivos))

        # --- AQUÍ ESTÁ EL FAMOSO 'PROMPT' DE LOS 5 MEJORES ---
        st.divider()
        st.header("📊 Resultado Final y Priorización")
        
        resumen_total = "\n".join(resultados_individuales)
        
        # Esta es la instrucción maestra para elegir el Top 5
        prompt_final = f"""
        De todos estos análisis: {resumen_total}.
        Identifica a los 5 mejores candidatos para la vacante: {vacante_txt}.
        
        Para cada uno de esos 5, entrega:
        1. **Nombre y Porcentaje de Match.**
        2. **Análisis de Ubicación:** ¿Es de la zona o tendría problemas de traslado?
        3. **Vacíos Detectados:** ¿Qué NO puso en la hoja de vida que es importante?
        4. **3 Preguntas 'Al Hueso':** Preguntas de entrevista para confirmar si sus dudas son reales.
        """
        
        informe_final = model.generate_content(prompt_final)
        st.write(informe_final.text)
        st.success("¡Análisis completado, Axel! Ya tienes tu Top 5 listo.")

    else:
        st.warning("Asegúrate de poner la vacante y subir al menos un archivo.")
