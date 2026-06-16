import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.styles import sec


def create_charts(df: pd.DataFrame) -> None:
    despesas_df = df[df["Valor"] < 0].copy()
    receitas_df = df[df["Valor"] > 0].copy()

    monthly = (
        df.groupby("AnoMes")["Valor"]
        .agg(
            Receitas=lambda x: x[x > 0].sum(),
            Despesas=lambda x: x[x < 0].sum(),
        )
        .reset_index()
    )
    monthly["Despesas"] = monthly["Despesas"].abs()
    monthly["Saldo"]    = monthly["Receitas"] - monthly["Despesas"]
    monthly             = monthly.sort_values("AnoMes")

    # Evolução financeira
    st.markdown(sec("chart-line", "Evolução Financeira"), unsafe_allow_html=True)
    fig_evo = go.Figure()
    fig_evo.add_trace(go.Bar(x=monthly["AnoMes"], y=monthly["Receitas"], name="Receitas", marker_color="#27ae60"))
    fig_evo.add_trace(go.Bar(x=monthly["AnoMes"], y=monthly["Despesas"], name="Despesas", marker_color="#e74c3c"))
    fig_evo.add_trace(go.Scatter(x=monthly["AnoMes"], y=monthly["Saldo"], name="Saldo",
                                  mode="lines+markers", line=dict(color="#2980b9", width=3)))
    fig_evo.update_layout(barmode="group", template="plotly_white", height=380,
                           legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig_evo, use_container_width=True)

    # Gastos por categoria | Gastos por instituição
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(sec("chart-pie", "Gastos por Categoria"), unsafe_allow_html=True)
        if not despesas_df.empty:
            cat_data = despesas_df.groupby("Categoria")["Valor"].sum().abs().reset_index()
            fig = px.pie(cat_data, values="Valor", names="Categoria", hole=0.45,
                         color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(template="plotly_white", height=350)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(sec("building-columns", "Gastos por Instituição"), unsafe_allow_html=True)
        if not despesas_df.empty:
            inst_data = (despesas_df.groupby("Instituicao")["Valor"].sum().abs()
                         .reset_index().sort_values("Valor", ascending=True))
            fig = px.bar(inst_data, x="Valor", y="Instituicao", orientation="h",
                         color="Valor", color_continuous_scale="Blues",
                         labels={"Valor": "Total (R$)", "Instituicao": ""})
            fig.update_layout(template="plotly_white", height=350,
                               showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    # Fluxo de caixa | Distribuição de receitas
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(sec("arrows-left-right", "Fluxo de Caixa Mensal"), unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=monthly["AnoMes"], y=monthly["Receitas"],  name="Receitas",  marker_color="#27ae60", opacity=0.85))
        fig.add_trace(go.Bar(x=monthly["AnoMes"], y=-monthly["Despesas"], name="Despesas", marker_color="#e74c3c", opacity=0.85))
        fig.update_layout(barmode="relative", template="plotly_white", height=350,
                           legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown(sec("dollar-sign", "Distribuição de Receitas"), unsafe_allow_html=True)
        if not receitas_df.empty:
            rec_cat = receitas_df.groupby("Categoria")["Valor"].sum().reset_index()
            fig = px.pie(rec_cat, values="Valor", names="Categoria", hole=0.45,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(template="plotly_white", height=350)
            st.plotly_chart(fig, use_container_width=True)

    # Top 10 maiores gastos
    st.markdown(sec("ranking-star", "Top 10 Maiores Gastos"), unsafe_allow_html=True)
    if not despesas_df.empty:
        top10 = despesas_df.nsmallest(10, "Valor").copy()
        top10["Valor_abs"] = top10["Valor"].abs()
        top10["Label"] = top10["Data"].dt.strftime("%d/%m") + " – " + top10["Descricao"]
        fig = px.bar(top10, x="Valor_abs", y="Label", orientation="h",
                     color="Valor_abs", color_continuous_scale="Reds",
                     labels={"Valor_abs": "Valor (R$)", "Label": ""})
        fig.update_layout(template="plotly_white", height=380, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # Evolução mensal acumulada
    st.markdown(sec("chart-area", "Evolução Mensal Acumulada"), unsafe_allow_html=True)
    monthly["Saldo_Acum"] = monthly["Saldo"].cumsum()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["AnoMes"], y=monthly["Saldo_Acum"],
        fill="tozeroy", mode="lines+markers",
        line=dict(color="#2980b9", width=2),
        fillcolor="rgba(41,128,185,0.15)",
        name="Saldo Acumulado",
    ))
    fig.update_layout(template="plotly_white", height=300)
    st.plotly_chart(fig, use_container_width=True)

    # Padrão por dia da semana (heatmap de barras)
    st.markdown(sec("calendar-days", "Padrão de Gastos por Dia da Semana"), unsafe_allow_html=True)
    day_order  = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_labels = {"Monday": "Seg", "Tuesday": "Ter", "Wednesday": "Qua",
                  "Thursday": "Qui", "Friday": "Sex", "Saturday": "Sáb", "Sunday": "Dom"}
    if not despesas_df.empty:
        week_data = (despesas_df.groupby("Semana")["Valor"].sum().abs()
                     .reindex(day_order).fillna(0).reset_index())
        week_data["Semana_PT"] = week_data["Semana"].map(day_labels)
        fig = px.bar(week_data, x="Semana_PT", y="Valor",
                     color="Valor", color_continuous_scale="Oranges",
                     labels={"Valor": "Total Gasto (R$)", "Semana_PT": "Dia da Semana"})
        fig.update_layout(template="plotly_white", height=300, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
