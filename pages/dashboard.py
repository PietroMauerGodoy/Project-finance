import streamlit as st

from components.styles import inject_styles
from components.kpis import create_kpis
from components.charts import create_charts
from services.preprocessing import apply_filters

st.set_page_config(page_title="Dashboard", layout="wide", initial_sidebar_state="expanded")
inject_styles()

st.markdown(
    "<h2 style='color:#1e3a5f;'>"
    "<i class='fa-solid fa-chart-line' style='color:#2d5a8e;margin-right:10px;'></i>"
    "Dashboard</h2>",
    unsafe_allow_html=True,
)

if "df" not in st.session_state:
    st.warning("Nenhuma planilha carregada. Volte à página inicial e faça o upload.")
    st.stop()

df = apply_filters(st.session_state["df"].copy())

if df.empty:
    st.warning("Nenhuma transação para os filtros selecionados.")
    st.stop()

receitas, despesas, _ = create_kpis(df)
st.divider()
create_charts(df)

with st.expander("Ver dados brutos"):
    fmt = {"Valor": st.column_config.NumberColumn("Valor", format="R$ %.2f")}
    st.dataframe(df.drop(columns=["AnoMes"], errors="ignore"), hide_index=True, column_config=fmt)
