import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

def mostrar_kpis_operaciones(simulaciones_libres: dict):
    if not simulaciones_libres:
        st.info("⚠️ Aún no has guardado ninguna simulación.")
        return

    st.markdown("## 📊 KPIs de Operaciones por semana")

    # Construir DataFrame
    df_sim = pd.DataFrame(list(simulaciones_libres.values()))
    df_sim = df_sim.sort_values("semana").reset_index(drop=True)
    df_sim["semana"] = df_sim["semana"].astype(int)

    # Mostrar tabla
    st.dataframe(df_sim.style.format(precision=2), use_container_width=True)

    # KPIs última semana
    ultima_semana = df_sim["semana"].max()
    kpi_ultima = df_sim[df_sim["semana"] == ultima_semana].iloc[0]

    st.markdown(f"### 🔎 Última semana simulada: {ultima_semana}")
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Utilidad", f"${kpi_ultima['utilidad']:.2f}")
    col2.metric("📦 Inventario final", int(kpi_ultima['inventario_final']))
    col3.metric("👥 Trabajadores", int(kpi_ultima['trabajadores']))

    col4, col5 = st.columns(2)
    col4.metric("⚙️ Costos OPS", f"${kpi_ultima['costos_ops']:.2f}")
    col5.metric("📢 Costos MKT", f"${kpi_ultima['costos_mkt']:.2f}")

    # KPIs acumulables
    kpis_acumulables = [
        "utilidad", "utilidad_operacional", "utilidad_marketing",
        "ventas", "costos_ops", "costos_mkt", "produccion_total", "faltantes"
    ]

    graficas = []
    for kpi in kpis_acumulables:
        if kpi in df_sim.columns:
            df_sim[f"{kpi}_acumulado"] = df_sim[kpi].cumsum()

            fig, ax1 = plt.subplots(figsize=(5, 3))
            ax1.bar(df_sim["semana"], df_sim[kpi], color='skyblue')
            ax1.set_xlabel("Semana")
            ax1.set_ylabel(f"{kpi}", color='blue')
            ax1.tick_params(axis='y', labelcolor='blue')

            ax2 = ax1.twinx()
            ax2.plot(df_sim["semana"], df_sim[f"{kpi}_acumulado"], color='red', marker='o')
            ax2.set_ylabel("Acumulado", color='red')
            ax2.tick_params(axis='y', labelcolor='red')

            ax1.set_title(f"{kpi.replace('_',' ').capitalize()} semanal vs acumulado")
            fig.tight_layout()
            graficas.append(fig)

    # Mostrar en filas de 3
    for i in range(0, len(graficas), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(graficas):
                col.pyplot(graficas[i + j])

    # KPIs no acumulables
    graficas_simple = []
    for kpi in ["inventario_final", "trabajadores"]:
        if kpi in df_sim.columns:
            fig, ax = plt.subplots(figsize=(5, 3))
            ax.bar(df_sim["semana"], df_sim[kpi], color='lightgreen')
            ax.set_title(f"{kpi.replace('_', ' ').capitalize()} por semana")
            ax.set_xlabel("Semana")
            ax.set_ylabel(kpi.capitalize())
            graficas_simple.append(fig)

    for i in range(0, len(graficas_simple), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(graficas_simple):
                col.pyplot(graficas_simple[i + j])

        # === GRÁFICA FINAL DE COSTOS DESGLOSADOS POR SEMANA (agrupada con etiquetas) ===
    st.markdown("### 💸 Costos desglosados por semana (valores exactos)")

    import seaborn as sns

    costos_cols = {
        "costo_produccion": "Producción",
        "costo_nomina": "Nómina",
        "costo_contratacion": "Contratación",
        "costo_despido": "Despido",
        "costo_horas_extra": "Horas extra",
        "costo_inventario": "Inventario",
        "costo_faltantes": "Faltantes"
    }

    columnas_presentes = [c for c in costos_cols.keys() if c in df_sim.columns]
    df_costos = df_sim[["semana"] + columnas_presentes].copy()
    df_costos = df_costos.rename(columns=costos_cols)

    df_melt = df_costos.melt(id_vars="semana", var_name="Tipo de costo", value_name="Valor")

    fig, ax = plt.subplots(figsize=(12, 5))
    sns.barplot(data=df_melt, x="semana", y="Valor", hue="Tipo de costo", ax=ax)

    for container in ax.containers:
        ax.bar_label(container, fmt="$%.2f", label_type="edge", fontsize=8, padding=2)

    ax.set_title("Costos por categoría y semana")
    ax.set_ylabel("Costo ($)")
    ax.set_xlabel("Semana")
    ax.set_xticks(sorted(df_melt["semana"].unique()))  # Escala de 1 en 1
    ax.legend(title="Tipo de costo", bbox_to_anchor=(1.05, 1), loc='upper left')
    fig.tight_layout()
    st.pyplot(fig)