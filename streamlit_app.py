import streamlit as st

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Agente IA - Selección Comfama", layout="wide")

# ESTILO PERSONALIZADO
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; background-color: #004b87; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 Agente de Selección Inteligente")
st.write("Análisis profundo de vacantes vs. candidatos para el Servicio Público de Empleo.")

# INTERFAZ DE ENTRADA
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Descripción de la Vacante")
    vacante_txt = st.text_area("Pega aquí los requisitos del cargo...", height=300)

with col2:
    st.subheader("👤 Hoja de Vida (CV)")
    cv_txt = st.text_area("Pega aquí el texto de la hoja de vida...", height=300)

# BOTÓN DE ACCIÓN
if st.button("🚀 INICIAR ANÁLISIS DEL PERFIL"):
    if vacante_txt and cv_txt:
        st.divider()
        st.header("📋 Informe del Agente")
        
        # Simulación de lógica de IA (Aquí es donde el Agente 'piensa')
        t1, t2, t3 = st.tabs(["📊 Análisis de Brechas", "❓ Guía de Entrevista", "📍 Datos Demográficos"])
        
        with t1:
            st.subheader("Comparativa de Competencias")
            st.info("El agente está analizando las palabras clave y experiencias...")
            # Aquí el código procesa la comparación
            st.warning("**Alerta de Brecha:** El candidato menciona experiencia en liderazgo, pero no especifica manejo de presupuestos, que es vital para la vacante.")
        
        with t2:
            st.subheader("Preguntas Orientadoras Sugeridas")
            st.write("1. 'En su CV menciona que trabajó en X, ¿podría detallar cómo manejó la ubicación geográfica si reside en Chigorodó?'")
            st.write("2. 'La vacante requiere manejo de software Y, ¿qué nivel de dominio real tiene?'")
            st.write("3. 'Cuénteme una situación donde haya tenido que resolver un conflicto de equipo.'")
            
        with t3:
            st.subheader("Ficha del Candidato")
            st.success("Información extraída con éxito.")
            st.json({
                "Ubicación detectada": "Chigorodó / Por confirmar",
                "Años de experiencia": "Cálculo aproximado: 4 años",
                "Alertas": "Falta número de teléfono actual"
            })
    else:
        st.error("Por favor, pega ambos textos para poder realizar el análisis.")
