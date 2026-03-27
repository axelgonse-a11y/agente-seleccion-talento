import streamlit as st
import pandas as pd

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Agente de Selección Comfama", layout="wide")

st.title("🔍 Agente de Análisis de Brechas - Selección")
st.write("Bienvenido, Axel. Esta herramienta analiza la compatibilidad entre vacantes y candidatos.")

# CARGA DE DATOS
st.sidebar.header("Panel de Control")
file = st.sidebar.file_uploader("Sube el Excel (Hojas: 'Requerido' y 'Actual')", type=["xlsx"])

if file:
    try:
        req = pd.read_excel(file, sheet_name="Requerido")
        act = pd.read_excel(file, sheet_name="Actual")
        
        st.success("✅ Datos cargados correctamente.")
        
        # Mostrar tablas
        col1, col2 = st.tabs(["🎯 Perfil Vacante", "👤 Perfil Candidato"])
        with col1: st.dataframe(req, use_container_width=True)
        with col2: st.dataframe(act, use_container_width=True)

        # Cálculo de Brecha (Gap)
        # La fórmula matemática es: $Brecha = Requerido - Actual$
        st.subheader("📉 Análisis de Brechas")
        merged = pd.merge(req, act, on="Competencia")
        merged["Diferencia"] = merged["Nivel_Requerido"] - merged["Nivel_Actual"]
        
        st.table(merged[["Competencia", "Nivel_Requerido", "Nivel_Actual", "Diferencia"]])

        # Sugerencia de la IA
        st.info("💡 **Sugerencia del Agente:** Enfócate en las competencias donde la diferencia sea mayor a 0.")

    except Exception as e:
        st.error(f"Error: Revisa que el Excel tenga las columnas 'Competencia', 'Nivel_Requerido' y 'Nivel_Actual'.")
else:
    st.info("👋 Por favor, sube un archivo Excel para comenzar el análisis.")
