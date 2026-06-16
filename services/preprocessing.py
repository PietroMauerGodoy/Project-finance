import pandas as pd
import streamlit as st

FIELD_ALIASES = {
    "Data":        ["data", "date", "dt", "dia", "competencia", "lancamento"],
    "Valor":       ["valor", "value", "amount", "quantia", "montante", "preco", "debito/credito"],
    "Descricao":   ["descricao", "descricão", "description", "historico", "histórico", "memo", "titulo", "lancamento", "lançamento"],
    "Categoria":   ["categoria", "category", "tipo_gasto", "grupo", "tag"],
    "Instituicao": ["instituicao", "instituição", "banco", "bank", "conta", "account", "origin"],
    "Tipo":        ["tipo", "type", "natureza", "movimentacao", "movimentação"],
}


def load_data(uploaded_file) -> pd.DataFrame:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    return df


def auto_detect(cols: list[str]) -> dict[str, str]:
    cols_lower = {c.lower(): c for c in cols}
    mapping: dict[str, str] = {}
    for field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if alias in cols_lower:
                mapping[field] = cols_lower[alias]
                break
    return mapping


def apply_mapping(df_raw: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    df = pd.DataFrame()
    df["Data"]        = df_raw[mapping["Data"]]
    df["Valor"]       = df_raw[mapping["Valor"]]
    df["Descricao"]   = df_raw[mapping["Descricao"]]   if mapping.get("Descricao")   else "Sem descrição"
    df["Categoria"]   = df_raw[mapping["Categoria"]]   if mapping.get("Categoria")   else "Sem categoria"
    df["Instituicao"] = df_raw[mapping["Instituicao"]] if mapping.get("Instituicao") else "Sem instituição"

    if mapping.get("Tipo"):
        df["Tipo"] = df_raw[mapping["Tipo"]]
    else:
        df["Tipo"] = df["Valor"].apply(
            lambda v: "Receita" if pd.to_numeric(v, errors="coerce") > 0 else "Despesa"
        )
    return df


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Data"]  = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    df.dropna(subset=["Data", "Valor"], inplace=True)

    df["Ano"]    = df["Data"].dt.year
    df["Mes"]    = df["Data"].dt.month
    df["Dia"]    = df["Data"].dt.day
    df["Semana"] = df["Data"].dt.day_name()
    df["AnoMes"] = df["Data"].dt.to_period("M").astype(str)

    df["Categoria"]   = df["Categoria"].astype(str).str.strip().str.title()
    df["Instituicao"] = df["Instituicao"].astype(str).str.strip()
    df["Tipo"]        = df["Tipo"].astype(str).str.strip().str.title()
    return df


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filtros")

    min_date = df["Data"].min().date()
    max_date = df["Data"].max().date()
    date_range = st.sidebar.date_input(
        "Período", value=(min_date, max_date),
        min_value=min_date, max_value=max_date,
        key="filter_date",
    )
    if len(date_range) == 2:
        df = df[(df["Data"].dt.date >= date_range[0]) & (df["Data"].dt.date <= date_range[1])]

    cats = ["Todas"] + sorted(df["Categoria"].unique().tolist())
    cat = st.sidebar.selectbox("Categoria", cats, key="filter_cat")
    if cat != "Todas":
        df = df[df["Categoria"] == cat]

    insts = ["Todas"] + sorted(df["Instituicao"].unique().tolist())
    inst = st.sidebar.selectbox("Instituição", insts, key="filter_inst")
    if inst != "Todas":
        df = df[df["Instituicao"] == inst]

    tipos = ["Todos"] + sorted(df["Tipo"].unique().tolist())
    tipo = st.sidebar.selectbox("Tipo", tipos, key="filter_tipo")
    if tipo != "Todos":
        df = df[df["Tipo"] == tipo]

    return df
