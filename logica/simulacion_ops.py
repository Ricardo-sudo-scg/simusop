import matplotlib.pyplot as plt
from streamlit_mic_recorder import mic_recorder
import pandas as pd
import streamlit as st
from logica.graficos import mostrar_kpis_operaciones

def vista_operaciones(params, estado, periodo, T):
    if st.session_state.periodo > T:
        st.warning("✅ Simulación finalizada. Todas las semanas completadas.")
        st.stop()
    # 🔧 Inicialización segura
    if "simulaciones_libres" not in st.session_state:
        st.session_state.simulaciones_libres = {}

    st.title(f"📆 Semana {periodo} – Rol: Operaciones")

    # === SIMULACIÓN LIBRE ===
    st.subheader("🔄 Simulación libre de decisiones")
    semana_simulada = st.slider("Selecciona semana para simular", 1, T, value=periodo)

    # Cargar inventario inicial para esa semana simulada si ya hay traza
    inventario_inicial = estado["inventario"]
    if "traza" in st.session_state:
        for t in st.session_state.traza:
            if t["periodo"] == semana_simulada - 1:
                inventario_inicial = t["inventario"]

    # === PARÁMETROS Y CONDICIONES ===
    with st.expander("🔍 Parámetros y condiciones del rol Operaciones", expanded=True):
        cap_reg = params['h_reg'] * params['v']
        cap_ext = params['h_ext'] * params['v_ex']
        col1, col2, col3 = st.columns(3)
        col1.metric("👥 Mínimo trabajadores", params['N_min'])
        col2.metric("👥 Máximo trabajadores", params['N_max'])
        if semana_simulada == 1:
            n_actual = estado["n"]
        else:
            sim_prev = st.session_state.simulaciones_libres.get(semana_simulada - 1, {})
            n_actual = sim_prev.get("trabajadores", estado["n"])
        col3.metric("👥 Actualmente tienes", n_actual)
        st.markdown(f"""
        🛠️ **Capacidad de producción por trabajador (semanal)**  
        - 🕒 **Horas regulares**: {params['h_reg']} horas × {params['v']} u/hora = **{cap_reg} unidades**  
        - 🕓 **Horas extra**: {params['h_ext']} horas × {params['v_ex']} u/hora = **{cap_ext} unidades**
        """)
        st.markdown("### 💰 Costos")
        st.markdown(f"""
        - ⚙️ Producción por unidad: **${params['c_p']}**  
        - 👤 Nómina: **${params['c_n']}**  
        - 📥 Contratación: **${params['c_c']}**  
        - 📤 Despido: **${params['c_d']}**  
        - ⏱️ Hora extra: **${params['c_h']}**  
        - 📦 Inventario semanal: **${params['c_inv']}**  
        - ❌ Faltantes: **${params['c_f']}**
        """)

    # === SIMULACIÓN DE DECISIONES ===
    with st.expander("🔧 Simulación de decisiones (OPS + MKT)", expanded=True):
        st.subheader("👷 Tus decisiones de Operaciones")

        # Cargar trabajadores e inventario de la semana anterior si existen
        if semana_simulada == 1:
            inventario_inicial = estado["inventario"]
            n_actual = estado["n"]
        else:
            sim_prev = st.session_state.simulaciones_libres.get(semana_simulada - 1, {})
            inventario_inicial = sim_prev.get("inventario_final", estado["inventario"])
            n_actual = sim_prev.get("trabajadores", estado["n"])

        # Control de cambios de trabajadores
        delta_min = max(params["N_min"] - n_actual, -3)
        delta_max = min(params["N_max"] - n_actual, 3)
        delta_n = st.slider("👥 Cambio de trabajadores", delta_min, delta_max, 0)
        n = n_actual + delta_n
        if n < params["N_min"] or n > params["N_max"]:
            st.error(f"🚫 El total de trabajadores ({n}) está fuera del rango permitido ({params['N_min']}–{params['N_max']}).")
            st.stop()

        cap_reg = n * params['h_reg'] * params['v']
        cap_ext = n * params['h_ext'] * params['v_ex']
        cap_total = cap_reg + cap_ext

        st.markdown(f"""
        🧾 **Capacidad estimada con {n} trabajadores:**  
        - 🕒 Regular: {cap_reg} unidades  
        - 🕓 Extra: {cap_ext} unidades  
        - 🔧 Total: **{cap_total} unidades**
        """)

        prod_reg = st.number_input("🏭 Producción regular", 0, cap_reg, step=1, key="prod_reg")
        # 1. Calcular el máximo de horas extra posibles
        horas_extra_max = n * params['h_ext']
        horas_extra = st.slider("⏱️ Horas extra a utilizar", 0, horas_extra_max, 0)
        # 2. Calcular producción máxima posible con esas horas
        prod_ext_max = horas_extra * params['v_ex']
        st.caption(f"🔧 Producción máxima posible con {horas_extra}h extra: **{prod_ext_max} unidades**")
        # 3. Elegir producción real con esas horas
        prod_ext = st.number_input("⚙️ Producción extra (basada en horas)", 0, prod_ext_max, step=11)
        prod_total = prod_reg + prod_ext

        if prod_reg > cap_reg or prod_ext > prod_ext_max:
            st.error("🚫 Excedes la capacidad permitida.")
            st.stop()

        # --- Marketing ---
        st.subheader("📢 Decisiones del otro rol (Marketing)")
        P = st.checkbox("💥 Promoción")
        A = st.checkbox("📢 Anuncio")
        E = st.checkbox("🛒 Exhibición")
        # Verificar acumulados previos
        kP_acum = sum(sim.get("P", 0) for sim in st.session_state.simulaciones_libres.values())
        kA_acum = sum(sim.get("A", 0) for sim in st.session_state.simulaciones_libres.values())
        kE_acum = sum(sim.get("E", 0) for sim in st.session_state.simulaciones_libres.values())
        st.caption(f"🔢 Usos acumulados → Promoción: {kP_acum}/{params['K_P']}, Anuncio: {kA_acum}/{params['K_A']}, Exhibición: {kE_acum}/{params['K_E']}")
                # Validación de límites
        if P and kP_acum >= params["K_P"]:
            st.error("🚫 Ya alcanzaste el máximo de promociones permitidas.")
            st.stop()
        if A and kA_acum >= params["K_A"]:
            st.error("🚫 Ya alcanzaste el máximo de anuncios permitidos.")
            st.stop()
        if E and kE_acum >= params["K_E"]:
            st.error("🚫 Ya alcanzaste el máximo de exhibiciones permitidas.")
            st.stop()

        demanda = params['demanda_base'] + params['k_P'] * int(P) + params['k_A'] * int(A) + params['k_E'] * int(E)
        ventas_maximas = min(inventario_inicial + prod_total, demanda)
        ventas = st.number_input("🛒 Unidades a vender", 0, ventas_maximas, ventas_maximas, step=10)

        inv_final = max(0, inventario_inicial + prod_total - ventas)
        faltantes = max(0, demanda - ventas)

        # Cálculos de costos
        descuento_unitario = 0.10 * params['p'] if P else 0
        c_descuento = descuento_unitario * ventas
        c_anuncio = params.get('C_A', 0) if A else 0
        c_exhibicion = params.get('C_E', 0) if E else 0
        c_mkt = c_descuento + c_anuncio + c_exhibicion

        c_prod = params['c_p'] * prod_total
        c_nom = params['c_n'] * n
        c_cont = params['c_c'] * max(0, delta_n)
        c_desp = params['c_d'] * max(0, -delta_n)
        c_ext = params['c_h'] * horas_extra if prod_ext > 0 else 0
        c_inv = params['c_inv'] * inv_final
        c_falt = params['c_f'] * faltantes
        c_total = c_prod + c_nom + c_cont + c_desp + c_ext + c_inv + c_falt

        ingresos = ventas * params['p']
        utilidad_operacional = ingresos - c_total
        utilidad_marketing = ingresos - c_mkt
        utilidad = ingresos - c_total - c_mkt

        st.subheader("📊 Resultados estimados")
        col1, col2, col3 = st.columns(3)
        col1.metric("Inventario inicial", inventario_inicial)
        col2.metric("Producción total", prod_total)
        col3.metric("Inventario final", inv_final)

        col4, col5, col6 = st.columns(3)
        col4.metric("Ventas", ventas)
        col5.metric("Faltantes", faltantes)
        col6.metric("Utilidad neta", f"${utilidad:.2f}")

        col7, col8 = st.columns(2)
        col7.metric("⚙️ Costos OPS", f"${c_total:.2f}")
        col8.metric("📢 Costos MKT", f"${c_mkt:.2f}")

        col1, col2 = st.columns(2)
        st.subheader("📊 Costos unitarios por tipo")

        if prod_total > 0:
            costo_fijo_unitario = (c_nom + c_cont + c_desp) / prod_total
            costo_variable_unitario = (c_prod + c_ext + c_inv + c_falt) / prod_total
            costo_mkt_unitario = c_mkt / prod_total
            costo_total_unitario = (c_total + c_mkt) / prod_total
        else:
            costo_fijo_unitario = costo_variable_unitario = costo_mkt_unitario = costo_total_unitario = 0

        col1, col2 = st.columns(2)
        col1.metric("⚙️ Costo fijo unitario", f"${costo_fijo_unitario:.2f}")
        col2.metric("🔧 Costo variable unitario", f"${costo_variable_unitario:.2f}")

        col3, col4, col5= st.columns(3)
        col3.metric("📢 Costo marketing unitario", f"${costo_mkt_unitario:.2f}")
        col4.metric("💰 Costo total unitario", f"${costo_total_unitario:.2f}")
        col5.metric("Margen utilidad", f"{(utilidad/ingresos*100):.1f}%" if ingresos else "0.0%")

        # Guardar simulación
        if st.button("💡 Guardar esta simulación libre"):
            if "simulaciones_libres" not in st.session_state:
                st.session_state.simulaciones_libres = {}
            st.session_state.simulaciones_libres[semana_simulada] = {
                "semana": semana_simulada,
                "trabajadores": n,
                "produccion_total": prod_total,
                "ventas": ventas,
                "inventario_final": inv_final,
                "utilidad": utilidad,
                "utilidad_operacional": utilidad_operacional,
                "utilidad_marketing": utilidad_marketing,
                "costos_ops": c_total,
                "costos_mkt": c_mkt,
                "faltantes": faltantes,
                "costo_produccion": c_prod,
                "costo_nomina": c_nom,
                "costo_contratacion": c_cont,
                "costo_despido": c_desp,
                "costo_horas_extra": c_ext,
                "costo_inventario": c_inv,
                "P": int(P),
                "A": int(A),
                "E": int(E),
                "costo_faltantes": c_falt
            }
            st.success("📦 Simulación guardada correctamente.")

        mostrar_kpis_operaciones(st.session_state.simulaciones_libres)
    # === CONFIRMACIÓN ===
    with st.expander("✅ Confirmar decisiones y avanzar", expanded=False):
        if semana_simulada == st.session_state.periodo:
            if st.button("✅ Confirmar y pasar a la siguiente semana"):

                simulacion_actual = st.session_state.simulaciones_libres.get(semana_simulada)

                if simulacion_actual:
                    estado["inventario"] = simulacion_actual["inventario_final"]
                    estado["n"] = simulacion_actual["trabajadores"]
                    estado["utilidad"] += simulacion_actual["utilidad"]

                    if "traza" not in st.session_state:
                        st.session_state.traza = []

                    st.session_state.traza.append({
                        'periodo': semana_simulada,
                        'rol': 'Operaciones',
                        'trabajadores': simulacion_actual["trabajadores"],
                        'prod_reg': None,  # Opcional, si quieres guardar más
                        'prod_ext': None,
                        'ventas': simulacion_actual["ventas"],
                        'inventario': simulacion_actual["inventario_final"],
                        'P': None, 'A': None, 'E': None,  # Puedes guardar si lo incluyes en simulación
                        'utilidad': simulacion_actual["utilidad"]
                    })

                    st.success("✅ Semana registrada.")
                    st.session_state.periodo += 1
                    st.rerun()
                else:
                    st.error("❌ Debes guardar primero la simulación de esta semana antes de confirmar.")
        else:
            st.info("☝️ Solo puedes confirmar si estás en la semana actual.")