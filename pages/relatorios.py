import streamlit as st

from components.styles import inject_styles, sec
from services.preprocessing import apply_filters

st.set_page_config(page_title="Relatórios", layout="wide", initial_sidebar_state="expanded")
inject_styles()

st.markdown(
    "<h2 style='color:#1e3a5f;'>"
    "<i class='fa-solid fa-file-chart-column' style='color:#2d5a8e;margin-right:10px;'></i>"
    "Relatórios</h2>",
    unsafe_allow_html=True,
)

if "df" not in st.session_state:
    st.warning("Nenhuma planilha carregada. Volte à página inicial e faça o upload.")
    st.stop()

df = apply_filters(st.session_state["df"].copy())

st.markdown(sec("screwdriver-wrench", "Em desenvolvimento"), unsafe_allow_html=True)
st.info(
    "Esta seção está reservada para exportação de relatórios.\n\n"
    "**Funcionalidades planejadas:**\n"
    "- Exportar para Excel (.xlsx)\n"
    "- Exportar para CSV filtrado\n"
    "- Gerar PDF com resumo executivo"
)

# Preview: exportar CSV filtrado já funciona
st.subheader("Exportar dados filtrados")
csv = df.drop(columns=["AnoMes"], errors="ignore").to_csv(index=False).encode("utf-8")
st.download_button(
    label="Baixar CSV filtrado",
    data=csv,
    file_name="financas_filtrado.csv",
    mime="text/csv",
)
