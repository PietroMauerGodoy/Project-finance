import streamlit as st

from components.styles import inject_styles
from components.alerts import generate_insights, generate_alerts, meta_financeira
from services.preprocessing import apply_filters

st.set_page_config(page_title="Insights", layout="wide", initial_sidebar_state="expanded")
inject_styles()

st.markdown(
    "<h2 style='color:#1e3a5f;'>"
    "<i class='fa-solid fa-lightbulb' style='color:#2d5a8e;margin-right:10px;'></i>"
    "Insights & Alertas</h2>",
    unsafe_allow_html=True,
)

if "df" not in st.session_state:
    st.warning("Nenhuma planilha carregada. Volte à página inicial e faça o upload.")
    st.stop()

df = apply_filters(st.session_state["df"].copy())

if df.empty:
    st.warning("Nenhuma transação para os filtros selecionados.")
    st.stop()

receitas = df[df["Valor"] > 0]["Valor"].sum()
despesas = df[df["Valor"] < 0]["Valor"].sum()

col1, col2 = st.columns(2)
with col1:
    generate_insights(df)
with col2:
    generate_alerts(df)

st.divider()
meta_financeira(receitas, despesas)
