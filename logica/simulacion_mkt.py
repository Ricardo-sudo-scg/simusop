import streamlit as st
import pandas as pd
from logica.graficos import mostrar_kpis_operaciones


def vista_marketing(params, estado, periodo, T):
    if st.session_state.periodo > T:
        st.warning("✅ Simulación finalizada. Todas las semanas completadas.")
        st.stop()

    if "simulaciones_libres" not in st.session_state:
        st.session_state.simulaciones_libres = {}

    st.title(f"📆 Semana {periodo} – Rol: Marketing")

    st.subheader("🔄 Simulación libre de decisiones")
    semana_simulada = st.slider("Selecciona semana para simular", 1, T, value=periodo)

    # === PARÁMETROS Y CONDICIONES DE MARKETING ===
    with st.expander("📢 Parámetros y restricciones de Marketing", expanded=True):
        kP_acum = sum(sim.get("P", 0) for sim in st.session_state.simulaciones_libres.values())
        kA_acum = sum(sim.get("A", 0) for sim in st.session_state.simulaciones_libres.values())
        kE_acum = sum(sim.get("E", 0) for sim in st.session_state.simulaciones_libres.values())

        col1, col2, col3 = st.columns(3)
        col1.metric("💥 Promociones usadas", f"{kP_acum}/{params['K_P']}")
        col2.metric("📢 Anuncios usados", f"{kA_acum}/{params['K_A']}")
        col3.metric("🛒 Exhibiciones usadas", f"{kE_acum}/{params['K_E']}")

        st.markdown("### 💰 Costos y efecto en demanda")
        st.markdown(f"""
        - 💥 **Promoción**: -10% por unidad vendida → +{params['k_P']} demanda
        - 📢 **Anuncio**: +{params['k_A']} demanda (costo ${params['C_A']})
        - 🛒 **Exhibición**: +{params['k_E']} demanda (costo ${params['C_E']})
        """)

    # === DECISIONES DE MARKETING ===
    with st.expander("📋 Decisiones de Marketing", expanded=True):
        P = st.checkbox("💥 Promoción")
        A = st.checkbox("📢 Anuncio")
        E = st.checkbox("🛒 Exhibición")

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
        st.info(f"📈 Demanda estimada: **{demanda}** unidades")

    # === DECISIONES DE OPERACIONES y VENTAS MARKETING ===
    with st.expander("👷 Decisiones de Operaciones", expanded=True):
        if semana_simulada == 1:
            inv = estado["inventario"]
            n_actual = estado["n"]
        else:
            sim_prev = st.session_state.simulaciones_libres.get(semana_simulada - 1, {})
            inv = sim_prev.get("inventario_final", estado["inventario"])
            n_actual = sim_prev.get("trabajadores", estado["n"])

        delta_min = max(params["N_min"] - n_actual, -3)
        delta_max = min(params["N_max"] - n_actual, 3)
        delta_n = st.slider("👥 Cambio de trabajadores", delta_min, delta_max, 0)
        n = n_actual + delta_n

        cap_reg = n * params['h_reg'] * params['v']
        cap_ext = n * params['h_ext'] * params['v_ex']

        prod_reg = st.number_input("🏭 Producción regular", 0, cap_reg, step=1, key="prod_reg")
        # 1. Calcular el máximo de horas extra posibles
        horas_extra_max = n * params['h_ext']
        horas_extra = st.slider("⏱️ Horas extra a utilizar", 0, horas_extra_max, 0)
        # 2. Calcular producción máxima posible con esas horas
        prod_ext_max = horas_extra * params['v_ex']
        st.caption(f"🔧 Producción máxima posible con {horas_extra}h extra: **{prod_ext_max} unidades**")
        # 3. Elegir producción real con esas horas
        prod_ext = st.number_input("⚙️ Producción extra (basada en horas)", 0, prod_ext_max, step=1)
        prod_total = prod_reg + prod_ext

        stock_total = inv + prod_total

        # Ayuda visual
        st.markdown("### 📦 Ayuda para decidir ventas")
        col1, col2, col3 = st.columns(3)
        col1.metric("📦 Inventario inicial", inv)
        col2.metric("🏭 Producción estimada", prod_total)
        col3.metric("📦 Stock total disponible", stock_total)

        ventas_max = min(demanda, stock_total)
        ventas = st.number_input("🛒 ¿Cuántas unidades deseas vender?", 0, ventas_max, ventas_max, step=1)

        inv_final = max(0, stock_total - ventas)
        faltantes = max(0, demanda - ventas)

        # Costos MKT
        descuento_unitario = 0.10 * params['p'] if P else 0
        c_descuento = descuento_unitario * ventas
        c_anuncio = params['C_A'] if A else 0
        c_exhibicion = params['C_E'] if E else 0
        c_mkt = c_descuento + c_anuncio + c_exhibicion

        # Costos OPS
        c_prod = params['c_p'] * prod_total
        c_nom = params['c_n'] * n
        c_cont = params['c_c'] * max(0, delta_n)
        c_desp = params['c_d'] * max(0, -delta_n)
        c_ext = params['c_h'] * horas_extra if prod_ext > 0 else 0
        c_inv = params['c_inv'] * inv_final
        c_falt = params['c_f'] * faltantes
        c_total_ops = c_prod + c_nom + c_cont + c_desp + c_ext + c_inv + c_falt

        ingresos = ventas * params['p']
        utilidad_operacional = ingresos - c_total_ops
        utilidad_marketing = ingresos - c_mkt
        utilidad_total = ingresos - c_total_ops - c_mkt

        st.subheader("📊 Resultados estimados")
        col1, col2, col3 = st.columns(3)
        col1.metric("📈 Demanda", demanda)
        col2.metric("🛒 Ventas", ventas)
        col3.metric("❌ Faltantes", faltantes)

        col4, col5, col6 = st.columns(3)
        col4.metric("⚙️ Costos OPS", f"${c_total_ops:.2f}")
        col5.metric("📢 Costos MKT", f"${c_mkt:.2f}")
        col6.metric("💰 Utilidad neta", f"${utilidad_total:.2f}")

        # Guardar simulación
        if st.button("💾 Guardar simulación completa"):
            st.session_state.simulaciones_libres[semana_simulada] = {
                "semana": semana_simulada,
                "P": int(P), "A": int(A), "E": int(E),
                "trabajadores": n,
                "delta_n": delta_n,
                "produccion_total": prod_total,
                "prod_reg": prod_reg,
                "prod_ext": prod_ext,
                "ventas": ventas,
                "inventario_final": inv_final,
                "utilidad_operacional": utilidad_operacional,
                "utilidad_marketing": utilidad_marketing,
                "utilidad": utilidad_total,
                "costos_ops": c_total_ops,
                "costos_mkt": c_mkt,
                "costo_produccion": c_prod,
                "costo_nomina": c_nom,
                "costo_contratacion": c_cont,
                "costo_despido": c_desp,
                "costo_horas_extra": c_ext,
                "costo_inventario": c_inv,
                "costo_faltantes": c_falt,
                "costo_descuento": c_descuento,
                "faltantes": faltantes
            }
            st.success("📦 Simulación guardada correctamente.")

    mostrar_kpis_operaciones(st.session_state.simulaciones_libres)

    with st.expander("✅ Confirmar decisiones y avanzar", expanded=False):
        if semana_simulada == st.session_state.periodo:
            if st.button("✅ Confirmar y pasar a la siguiente semana"):
                sim = st.session_state.simulaciones_libres.get(semana_simulada)
                if sim:
                    estado["inventario"] = sim["inventario_final"]
                    estado["n"] = sim["trabajadores"]
                    estado["utilidad"] += sim["utilidad"]

                    if "traza" not in st.session_state:
                        st.session_state.traza = []

                    st.session_state.traza.append({
                        "periodo": semana_simulada,
                        "rol": "Marketing",
                        "P": sim["P"], "A": sim["A"], "E": sim["E"],
                        "ventas": sim["ventas"],
                        "inventario": sim["inventario_final"],
                        "trabajadores": sim["trabajadores"],
                        "utilidad": sim["utilidad"]
                    })

                    st.success("✅ Semana registrada.")
                    st.session_state.periodo += 1
                    st.rerun()
                else:
                    st.error("❌ Debes guardar primero la simulación antes de confirmar.")
        else:
            st.info("☝️ Solo puedes confirmar si estás en la semana actual.")
