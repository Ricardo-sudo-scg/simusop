import streamlit as st
from logica.registro import mostrar_registro
from logica.estado import cargar_parametros_y_estado
from logica.simulacion_mkt import vista_marketing
from logica.simulacion_ops import vista_operaciones
from logica.resultados import mostrar_resultados

# --- Configuración ---
st.set_page_config(page_title="Simulador S&OP", layout="wide")

# --- Cargar parámetros y estado inicial ---
params, estado_inicial, T = cargar_parametros_y_estado()

# --- Inicializar session_state ---
if "inicio" not in st.session_state:
    st.session_state.inicio = False
if "periodo" not in st.session_state:
    st.session_state.periodo = 1
if "estado" not in st.session_state:
    st.session_state.estado = estado_inicial.copy()
if "fase" not in st.session_state:
    st.session_state.fase = "inputs"
if "log" not in st.session_state:
    st.session_state.log = []
if "evaluacion" not in st.session_state:
    st.session_state.evaluacion = "70% individual / 30% grupal"

# --- Mostrar pantalla de registro ---
mostrar_registro()

# --- Mostrar barra lateral ---
st.sidebar.title("📊 Avance")
st.sidebar.markdown(f"Semana **{st.session_state.periodo} de {T}**")

# --- Ejecutar simulación según el rol ---
if st.session_state.inicio:
    estado = st.session_state.estado
    periodo = st.session_state.periodo
    rol = st.session_state.rol

    if rol == "Marketing":
        vista_marketing(params, estado, periodo, T)
    elif rol == "Operaciones":
        vista_operaciones(params, estado, periodo, T)
    else:
        st.warning("Rol no reconocido.")