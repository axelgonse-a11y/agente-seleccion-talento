import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import io

# 1. CONFIGURACIÓN DEL MODELO (Versión 2026)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Actualizado a 2.0 para evitar el error 404
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    st.error(f"🔑 Error de configuración: {e}")

def extraer_texto_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    return "".join([p.extract_text() for p in pdf_reader.pages])

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Agente IA Comfama", layout="wide")

st.title("🤖 Agente de Selección Masiva: El Top 5")
st.write(f"Hola Axel, hoy es {st.date_input('Fecha de análisis', value=None)}. Vamos a priorizar esos perfiles.")

# 2. ENTRADA DE LA VACANTE
st.header("1. Definición de la Vacante")
vacante_txt = st.text_area("Pega los requisitos (Ubicación, Exp, Género, etc.):", 
                           placeholder="Ej: Auxiliar en Chigorodó, mujer, 2 años de experiencia...",
                           height=150)

# 3. CARGA DE HOJAS DE VIDA
st.header("2. Carga de Candidatos (Máximo 20)")
archivos = st.file_uploader("Sube archivos PDF o Fotos (JPG/PNG)", 
                             type=["pdf", "jpg", "png", "jpeg"], 
                             accept_multiple_files=True)

# 4. PROCESAMIENTO
if st.button("🚀 INICIAR ANÁLISIS DE GRUPO"):
    if vacante_txt and archivos:
        if len(archivos) > 20:
            st.error("Por favor, sube máximo 20 archivos para no saturar el sistema.")
        else:
            resultados_individuales = []
            barra = st.progress(0)
            
            for i, archivo in enumerate(archivos):
                with st.spinner(f"Analizando: {archivo.name}..."):
                    try:
                        if archivo.type == "application/pdf":
                            contenido = extraer_texto_pdf(archivo)
                            instruccion = f"Analiza este CV contra esta vacante: {vacante_txt}. Datos: {contenido}. Resume: Nombre, Ubicación, Años Exp, % Match."
                            resp = model.generate_content(instruccion)
                        else:
                            img = Image.open(archivo)
                            instruccion = f"Analiza esta imagen de CV contra esta vacante: {vacante_txt}. Extrae: Nombre, Ubicación, Años Exp, % Match."
                            resp = model.generate_content([instruccion, img])
                        
                        resultados_individuales.append(f"CANDIDATO: {archivo.name}\n{resp.text}")
                    except Exception as e:
                        st.error(f"Error procesando {archivo.name}: {e}")
                
                barra.progress((i + 1) / len(archivos))

            # --- ANÁLISIS FINAL DEL TOP 5 ---
            st.divider()
            st.header("📊 Resultado Final y Priorización")
            
            resumen_total = "\n\n".join(resultados_individuales)
            
            prompt_final = f"""
            Actúa como un psicólogo senior de selección. Basado en estos análisis: {resumen_total}.
            Identifica a los 5 mejores candidatos para la vacante: {vacante_txt}.
            
            Presenta el informe así:
            1. **Tabla Comparativa:** Con Nombre, % de Match y Ubicación.
            2. **Análisis de los 5 mejores:** Explica por qué son los mejores y qué 'vacíos' o dudas encontraste (fechas, falta de datos, etc.).
            3. **Guía de Entrevista:** 3 preguntas potentes por cada uno para validar sus puntos grises.
            """
            
            informe_final = model.generate_content(prompt_final)
            st.markdown(informe_final.text)
            st.success("¡Análisis completado con éxito!")

    else:
        st.warning("Axel, recuerda poner la vacante y subir los archivos.")
