import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import pandas as pd

# Configuración Gemini
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("🔑 Configura la API Key en los Secrets de Streamlit.")

def extraer_texto_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    return "".join([p.extract_text() for p in pdf_reader.pages])

st.set_page_config(page_title="Agente Selección Comfama", layout="wide")

st.title("🏆 Agente de Selección Masiva: El Top 5")
st.write("Axel, este sistema analiza hasta 20 perfiles y prioriza a los mejores para tu entrevista.")

# ENTRADA DE LA VACANTE
vacante_txt = st.text_area("📋 Requisitos de la Vacante (Ubicación, Exp, Sexo, etc.)", height=150)

# CARGA MASIVA
archivos = st.file_uploader("👤 Sube hasta 20 Hojas de Vida (PDF o Imagen)", 
                             type=["pdf", "jpg", "png"], 
                             accept_multiple_files=True)

if st.button("🚀 INICIAR PROCESO DE SELECCIÓN"):
    if vacante_txt and archivos:
        if len(archivos) > 20:
            st.error("Por favor, sube máximo 20 archivos.")
        else:
            resultados = []
            progreso = st.progress(0)
            
            for i, archivo in enumerate(archivos):
                with st.spinner(f"Analizando a: {archivo.name}..."):
                    # Extraer contenido según formato
                    if archivo.type == "application/pdf":
                        contenido = extraer_texto_pdf(archivo)
                        prompt = f"Analiza este CV contra la vacante. VACANTE: {vacante_txt}. CV: {contenido}. Extrae en formato JSON: nombre, ubicacion, años_exp, match_porcentaje (0-100), razon_principal."
                        response = model.generate_content(prompt)
                    else:
                        img = Image.open(archivo)
                        prompt = f"Analiza esta imagen de CV contra la vacante. VACANTE: {vacante_txt}. Extrae en formato JSON: nombre, ubicacion, años_exp, match_porcentaje (0-100), razon_principal."
                        response = model.generate_content([prompt, img])
                    
                    # Guardamos la respuesta (limpiando el texto para que sea legible)
                    texto_ia = response.text.replace("```json", "").replace("```", "")
                    resultados.append({"nombre_archivo": archivo.name, "analisis": texto_ia, "raw_file": archivo})
                
                progreso.progress((i + 1) / len(archivos))

            # --- MATRIZ COMPARATIVA ---
            st.divider()
            st.header("📊 Matriz de Priorización")
            
            # Aquí le pedimos a Gemini que haga el ranking final de todos los analizados
            resumen_completo = "\n".join([r['analisis'] for r in resultados])
            prompt_ranking = f"Basado en estos análisis individuales: {resumen_completo}. Crea una tabla comparativa de los mejores. Devuelve solo los datos de: Nombre, Ubicación, Años Exp, % Match. Ordena por % Match de mayor a menor."
            tabla_final = model.generate_content(prompt_ranking)
            st.markdown(tabla_final.text)

            # --- EL TOP 5 Y PREGUNTAS ORIENTADORAS ---
            st.divider()
            st.header("🎯 Guía de Entrevista: Los 5 Finalistas")
            
            prompt_top5 = f"""
            Identifica a los 5 mejores candidatos de estos datos: {resumen_completo}.
            Para cada uno de esos 5, genera 3 preguntas de entrevista específicas.
            Las preguntas DEBEN basarse en sus 'Red Flags' (vacíos en fechas, si la ubicación no coincide con Chigorodó, si falta el sexo si era requisito, o si hay dudas en su experiencia).
            Se muy agudo y profesional, como un psicólogo de Comfama.
            """
            guia_entrevista = model.generate_content(prompt_top5)
            st.info("Estas preguntas van directo a los puntos grises detectados por el Agente.")
            st.write(guia_entrevista.text)

    else:
        st.warning("Axel, necesito la vacante y los archivos para empezar.")
