import streamlit as st

from components.styles import inject_styles, sec
from services.preprocessing import (
    FIELD_ALIASES,
    auto_detect,
    apply_mapping,
    load_data,
    preprocess_data,
)

st.set_page_config(
    page_title="Finance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()

st.markdown(
    "<h1 style='text-align:center;color:#1e3a5f;margin-bottom:0;'>"
    "<i class='fa-solid fa-chart-line' style='color:#2d5a8e;margin-right:12px;'></i>"
    "Finance Dashboard</h1>"
    "<p style='text-align:center;color:#7f8c8d;margin-top:4px;'>"
    "Plataforma de análise financeira pessoal</p>",
    unsafe_allow_html=True,
)
st.divider()

# ── Upload ────────────────────────────────────────────────────────────────────

uploaded_file = st.file_uploader(
    "Faça o upload da sua planilha financeira (.csv)",
    type=["csv"],
    help="Qualquer CSV com movimentações. Você vai mapear as colunas na próxima etapa.",
)

if uploaded_file is None:
    st.session_state.pop("col_mapping", None)
    st.session_state.pop("mapping_confirmed", None)
    st.session_state.pop("df", None)

if uploaded_file is None:
    st.info("Faça o upload de qualquer CSV com suas movimentações financeiras.")
    st.markdown("""
    **O app aceita qualquer planilha** — não importa o nome das colunas.
    Após o upload você indica qual coluna é data, qual é valor, etc.

    Exemplo de estrutura (mas pode ser diferente):
    ```
    Data,Historico,Banco,Valor
    01/01/2026,Salario,Nubank,5000
    02/01/2026,Mercado,Nubank,-350
    ```
    """)
    st.stop()

# ── Mapeamento de colunas ─────────────────────────────────────────────────────

df_raw = load_data(uploaded_file)

if not st.session_state.get("mapping_confirmed"):
    cols       = list(df_raw.columns)
    auto       = auto_detect(cols)
    sem_opcao  = "— não tenho essa coluna —"
    opts_opt   = [sem_opcao] + cols

    st.markdown(sec("table-columns", "Mapeamento de Colunas"), unsafe_allow_html=True)
    st.caption("Diga qual coluna do seu CSV corresponde a cada campo. Campos opcionais podem ficar em branco.")

    mapping: dict = {}
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Campos obrigatórios**")
        for field in ["Data", "Valor"]:
            default = auto.get(field, cols[0])
            idx     = cols.index(default) if default in cols else 0
            mapping[field] = st.selectbox(f"Coluna para **{field}**", cols, index=idx, key=f"map_{field}")

    with c2:
        st.markdown("**Campos opcionais**")
        for field in ["Descricao", "Categoria", "Instituicao", "Tipo"]:
            default = auto.get(field, sem_opcao)
            idx     = opts_opt.index(default) if default in opts_opt else 0
            sel     = st.selectbox(f"Coluna para **{field}**", opts_opt, index=idx, key=f"map_{field}")
            mapping[field] = None if sel == sem_opcao else sel

    if st.button("Confirmar mapeamento e analisar", type="primary"):
        df_mapped                          = apply_mapping(df_raw, mapping)
        st.session_state["df"]             = preprocess_data(df_mapped)
        st.session_state["col_mapping"]    = mapping
        st.session_state["mapping_confirmed"] = True
        st.rerun()

else:
    st.success("Planilha carregada com sucesso! Use o menu lateral para navegar.")
    st.markdown("""
    **Navegue pelas páginas no menu lateral:**
    - **Dashboard** — KPIs e gráficos
    - **Insights** — análises automáticas e alertas
    - **Relatórios** — exportação *(em breve)*
    """)
    if st.sidebar.button("Refazer mapeamento de colunas"):
        st.session_state.pop("col_mapping", None)
        st.session_state.pop("mapping_confirmed", None)
        st.session_state.pop("df", None)
        st.rerun()
