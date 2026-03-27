import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import time

# CONFIGURACIÓN
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Usamos 1.5-flash porque tiene una cuota gratuita un poco más amplia que el 2.0
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Revisa tu API Key en Secrets.")

def extraer_texto_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        # Solo extraemos los primeros 2000 caracteres para no saturar la cuota
        texto = " ".join([p.extract_text() for p in pdf_reader.pages])
        return texto[:2000] 
    except:
        return ""

st.set_page_config(page_title="Agente Selección Comfama", layout="wide")
st.title("🤖 Analizador de Talento (Versión Blindada)")

vacante_txt = st.text_area("📝 Requisitos de la Vacante:", height=100)
archivos = st.file_uploader("👤 Sube tus 5-8 CVs (PDF o Imagen):", type=["pdf", "jpg", "png"], accept_multiple_files=True)

if st.button("🚀 INICIAR ANÁLISIS"):
    if vacante_txt and archivos:
        resultados_lista = []
        barra = st.progress(0)
        placeholder = st.empty()
        
        for i, archivo in enumerate(archivos):
            exito = False
            intentos = 0
            
            while not exito and intentos < 3:
                try:
                    placeholder.info(f"Analizando {archivo.name}... (Intento {intentos + 1})")
                    
                    if archivo.type == "application/pdf":
                        texto_cv = extraer_texto_pdf(archivo)
                        prompt = f"CV: {texto_cv} \n VACANTE: {vacante_txt} \n Analiza brevemente: Nombre, % Match y 2 preguntas clave."
                        response = model.generate_content(prompt)
                    else:
                        img = Image.open(archivo)
                        prompt = f"Analiza esta imagen contra la vacante: {vacante_txt}. Resume brevemente Match % y 2 preguntas."
                        response = model.generate_content([prompt, img])
                    
                    resultados_lista.append(f"CANDIDATO: {archivo.name}\n{response.text}")
                    st.success(f"✅ {archivo.name} procesado.")
                    exito = True
                    # Pausa de seguridad entre archivos
                    time.sleep(15) 
                    
                except Exception as e:
                    intentos += 1
                    if "429" in str(e):
                        placeholder.warning("⚠️ Google está saturado. Esperando 30 segundos para reintentar...")
                        time.sleep(30)
                    else:
                        st.error(f"Error en {archivo.name}: {e}")
                        break
            
            barra.progress((i + 1) / len(archivos))

        if resultados_lista:
            st.divider()
            st.header("📊 Informe Final")
            resumen_final = "\n\n".join(resultados_lista)
            # Una última llamada para la tabla final
            try:
                time.sleep(10)
                tabla = model.generate_content(f"Con estos datos: {resumen_final}, genera una tabla comparativa final para Axel.")
                st.markdown(tabla.text)
            except:
                st.write(resumen_final) # Si falla la tabla, al menos muestra los resultados
    else:
        st.warning("Completa los datos.")
