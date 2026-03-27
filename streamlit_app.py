import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import time # Importante para las pausas

# CONFIGURACIÓN
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    st.error(f"🔑 Error de llave: {e}")

def extraer_texto_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    return "".join([p.extract_text() for p in pdf_reader.pages])

st.set_page_config(page_title="Agente Selección Comfama", layout="wide")
st.title("🤖 Agente de Selección: Edición Especial (Con Pausas)")

st.header("1. Definición de la Vacante")
vacante_txt = st.text_area("Requisitos del cargo:", height=150)

st.header("2. Carga de Candidatos")
archivos = st.file_uploader("Sube hasta 20 archivos", type=["pdf", "jpg", "png"], accept_multiple_files=True)

if st.button("🚀 INICIAR ANÁLISIS"):
    if vacante_txt and archivos:
        resultados_individuales = []
        barra = st.progress(0)
        
        for i, archivo in enumerate(archivos):
            with st.spinner(f"Analizando a {archivo.name}..."):
                try:
                    # Pausa de seguridad para evitar el error 429
                    time.sleep(3) 
                    
                    if archivo.type == "application/pdf":
                        contenido = extraer_texto_pdf(archivo)
                        prompt = f"Compara este CV contra esta vacante: {vacante_txt}. CV: {contenido}. Resume Match% y 2 debilidades."
                        resp = model.generate_content(prompt)
                    else:
                        img = Image.open(archivo)
                        prompt = f"Analiza esta foto de CV contra la vacante: {vacante_txt}. Resume Match% y 2 debilidades."
                        resp = model.generate_content([prompt, img])
                    
                    resultados_individuales.append(f"CANDIDATO: {archivo.name}\n{resp.text}")
                except Exception as e:
                    if "429" in str(e) or "ResourceExhausted" in str(e):
                        st.warning(f"Saturación detectada en {archivo.name}. Esperando 10 segundos para reintentar...")
                        time.sleep(10) # Pausa más larga si hay error
                        # Reintento único
                        resp = model.generate_content(prompt)
                        resultados_individuales.append(f"CANDIDATO: {archivo.name}\n{resp.text}")
                    else:
                        st.error(f"Error en {archivo.name}: {e}")
            
            barra.progress((i + 1) / len(archivos))

        st.divider()
        st.header("📊 Informe Final y Top 5")
        
        # Pausa final antes del resumen
        time.sleep(4)
        resumen_total = "\n\n".join(resultados_individuales)
        prompt_final = f"Basado en estos análisis: {resumen_total}. Selecciona el Top 5 para la vacante: {vacante_txt} y crea la tabla comparativa con preguntas de entrevista."
        
        informe_final = model.generate_content(prompt_final)
        st.markdown(informe_final.text)
        st.success("¡Análisis terminado respetando los límites de Google!")
    else:
        st.warning("Faltan datos para empezar.")
