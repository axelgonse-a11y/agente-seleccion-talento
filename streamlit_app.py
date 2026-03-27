import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import time

# 1. CONFIGURACIÓN ROBUSTA
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Usamos la versión estable más ligera para evitar bloqueos
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error de conexión: {e}")

def extraer_texto_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        texto = ""
        for pagina in pdf_reader.pages:
            texto += pagina.extract_text() or ""
        return texto[:10000] # Limitamos el texto para no saturar la memoria
    except:
        return "No se pudo leer el PDF"

st.set_page_config(page_title="Agente Selección Comfama", layout="wide")
st.title("🤖 Analizador de Candidatos (Modo Seguro)")

# INTERFAZ
vacante_txt = st.text_area("📝 Requisitos de la Vacante:", height=150, placeholder="Pega aquí el perfil...")
archivos = st.file_uploader("👤 Sube tus 5-8 Hojas de Vida:", type=["pdf", "jpg", "png"], accept_multiple_files=True)

if st.button("🚀 INICIAR PROCESO"):
    if vacante_txt and archivos:
        resultados = []
        barra = st.progress(0)
        status_text = st.empty()
        
        for i, archivo in enumerate(archivos):
            status_text.text(f"Procesando candidato {i+1} de {len(archivos)}: {archivo.name}...")
            
            try:
                # PAUSA OBLIGATORIA: Para que el servidor de Google no nos bloquee
                time.sleep(6) 
                
                if archivo.type == "application/pdf":
                    cv_texto = extraer_texto_pdf(archivo)
                    prompt = f"Compara este CV con la Vacante. Vacante: {vacante_txt}. CV: {cv_texto}. Responde breve: Nombre, % Match, y 2 preguntas de entrevista."
                    response = model.generate_content(prompt)
                else:
                    img = Image.open(archivo)
                    prompt = f"Analiza esta imagen de CV. Vacante: {vacante_txt}. Responde breve: Nombre, % Match, y 2 preguntas de entrevista."
                    response = model.generate_content([prompt, img])
                
                resultados.append(f"--- CANDIDATO: {archivo.name} ---\n{response.text}")
                st.success(f"✅ {archivo.name} analizado correctamente.")
                
            except Exception as e:
                st.error(f"❌ Error en {archivo.name}: {e}")
                time.sleep(10) # Pausa extra si hay error
            
            barra.progress((i + 1) / len(archivos))
        
        # INFORME FINAL
        if resultados:
            st.divider()
            st.header("📊 Informe Comparativo Final")
            status_text.text("Generando cuadro comparativo final...")
            time.sleep(5)
            
            resumen_total = "\n\n".join(resultados)
            prompt_final = f"Basado en estos análisis: {resumen_total}. Crea una tabla comparativa con los nombres, el match y selecciona el Top 3 para la vacante: {vacante_txt}."
            
            final_resp = model.generate_content(prompt_final)
            st.markdown(final_resp.text)
            status_text.text("¡Proceso completado!")
    else:
        st.warning("Faltan datos para iniciar.")
