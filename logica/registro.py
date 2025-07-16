import streamlit as st

def mostrar_registro():
    if not st.session_state.get("inicio", False):
        st.title("📝 Registro Inicial – Simulación S&OP")
        st.markdown("Por favor, completa tus datos para comenzar la simulación.")

        col1, col2 = st.columns(2)
        with col1:
            st.session_state.correo = st.text_input("📧 Correo UTEC")
            st.session_state.turno = st.selectbox("⏰ Turno", ["Turno 1 (4:00pm)", "Turno 2 (6:00pm)"])
        with col2:
            st.session_state.duo = st.selectbox("👥 Número de dúo", list(range(1, 8)))
            st.session_state.rol = st.selectbox("🎭 Rol asignado", ["Marketing", "Operaciones"])
        
        st.session_state.evaluacion = st.selectbox(
            "🌟 Esquema de incentivos final:",
            ["70% individual / 30% grupal", "30% individual / 70% grupal"]
        )

        st.markdown("---")
        st.subheader("📋 Resumen")
        st.markdown(f"""
        - **Correo:** {st.session_state.get('correo', 'No ingresado')}
        - **Turno:** {st.session_state.get('turno', 'No seleccionado')}
        - **Dúo:** {st.session_state.get('duo', 'No seleccionado')}
        - **Rol:** {st.session_state.get('rol', 'No seleccionado')}
        - **Incentivo:** {st.session_state.get('evaluacion', '')}
        """)

        if st.button("🚀 Iniciar simulación"):
            st.session_state.inicio = True
            st.rerun()  # <-- Esto es clave

        st.stop()  # Detener el flujo si aún no inicia