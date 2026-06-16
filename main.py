import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Finanças", page_icon=":money_with_wings:", layout="wide")

st.markdown("""
<link rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"
      crossorigin="anonymous" referrerpolicy="no-referrer"/>
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #2d5a8e);
        border-radius: 12px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .metric-card .card-icon { font-size: 1.6rem; opacity: 0.9; margin-bottom: 6px; }
    .metric-card .card-label { font-size: 0.8rem; opacity: 0.75; letter-spacing: 0.05em; text-transform: uppercase; }
    .metric-card .card-value { font-size: 1.5rem; font-weight: 700; margin-top: 4px; }
    .metric-card .card-delta { font-size: 0.75rem; margin-top: 6px; font-weight: 600; }
    .metric-card .delta-up   { color: #a8f5c2; }
    .metric-card .delta-down { color: #ffb3b3; }
    .metric-card .delta-neu  { color: rgba(255,255,255,0.5); }
    .insight-card {
        background: #f0f4ff;
        border-left: 4px solid #2d5a8e;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 6px 0;
        color: #1a1a2e;
    }
    .insight-card i { color: #2d5a8e; margin-right: 8px; }
    .alert-card {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 6px 0;
        color: #856404;
    }
    .alert-card i { color: #856404; margin-right: 8px; }
    .alert-danger {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 6px 0;
        color: #721c24;
    }
    .alert-danger i { color: #dc3545; margin-right: 8px; }
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1e3a5f;
        margin: 24px 0 12px 0;
        border-bottom: 2px solid #2d5a8e;
        padding-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-title i { color: #2d5a8e; font-size: 1.1rem; }
</style>
""", unsafe_allow_html=True)


def sec(icon: str, label: str) -> str:
    """Gera HTML de título de seção com ícone Font Awesome."""
    return f'<div class="section-title"><i class="fa-solid fa-{icon}"></i>{label}</div>'

# Campos internos do dashboard → aliases que tentamos detectar automaticamente
FIELD_ALIASES = {
    "Data":       ["data", "date", "dt", "dia", "competencia", "lancamento"],
    "Valor":      ["valor", "value", "amount", "quantia", "montante", "preco", "debito/credito"],
    "Descricao":  ["descricao", "descricão", "description", "historico", "histórico", "memo", "titulo", "lancamento", "lançamento"],
    "Categoria":  ["categoria", "category", "tipo_gasto", "grupo", "tag"],
    "Instituicao":["instituicao", "instituição", "banco", "bank", "conta", "account", "origin"],
    "Tipo":       ["tipo", "type", "natureza", "movimentacao", "movimentação"],
}
CAMPOS_OBRIGATORIOS = {"Data", "Valor"}
CAMPOS_OPCIONAIS    = {"Descricao", "Categoria", "Instituicao", "Tipo"}


def load_data(uploaded_file) -> pd.DataFrame:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    return df


def _auto_detect(cols: list[str]) -> dict[str, str]:
    """Tenta mapear automaticamente colunas do CSV para campos internos."""
    cols_lower = {c.lower(): c for c in cols}
    mapping = {}
    for field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if alias in cols_lower:
                mapping[field] = cols_lower[alias]
                break
    return mapping


def column_mapping_ui(df_raw: pd.DataFrame) -> dict[str, str] | None:
    """
    Exibe UI de mapeamento de colunas e retorna o mapeamento confirmado.
    Retorna None enquanto o usuário não confirmar.
    """
    cols = list(df_raw.columns)
    auto = _auto_detect(cols)

    st.markdown(sec("table-columns", "Mapeamento de Colunas"), unsafe_allow_html=True)
    st.caption(
        "Seu arquivo tem colunas diferentes do padrão. "
        "Diga qual coluna corresponde a cada campo. "
        "Campos opcionais podem ficar em branco."
    )

    sem_opcao = "— não tenho essa coluna —"
    opcoes_opcionais = [sem_opcao] + cols

    mapping = {}
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Campos obrigatórios**")
        for field in ["Data", "Valor"]:
            default = auto.get(field, cols[0])
            idx = cols.index(default) if default in cols else 0
            mapping[field] = st.selectbox(f"Coluna para **{field}**", cols, index=idx, key=f"map_{field}")

    with col2:
        st.markdown("**Campos opcionais**")
        for field in ["Descricao", "Categoria", "Instituicao", "Tipo"]:
            default = auto.get(field, sem_opcao)
            opcoes = opcoes_opcionais
            idx = opcoes.index(default) if default in opcoes else 0
            sel = st.selectbox(f"Coluna para **{field}**", opcoes, index=idx, key=f"map_{field}")
            mapping[field] = None if sel == sem_opcao else sel

    if st.button("✅ Confirmar mapeamento e analisar", type="primary"):
        st.session_state["col_mapping"] = mapping
        st.session_state["mapping_confirmed"] = True
        st.rerun()

    return None


def apply_mapping(df_raw: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """Renomeia/cria colunas conforme o mapeamento e retorna df padronizado."""
    df = pd.DataFrame()
    df["Data"]       = df_raw[mapping["Data"]]
    df["Valor"]      = df_raw[mapping["Valor"]]
    df["Descricao"]  = df_raw[mapping["Descricao"]]  if mapping.get("Descricao")   else "Sem descrição"
    df["Categoria"]  = df_raw[mapping["Categoria"]]  if mapping.get("Categoria")   else "Sem categoria"
    df["Instituicao"]= df_raw[mapping["Instituicao"]]if mapping.get("Instituicao") else "Sem instituição"

    if mapping.get("Tipo"):
        df["Tipo"] = df_raw[mapping["Tipo"]]
    else:
        # deriva automaticamente pelo sinal do valor
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
    st.sidebar.header("🔍 Filtros")

    min_date = df["Data"].min().date()
    max_date = df["Data"].max().date()
    date_range = st.sidebar.date_input(
        "Período", value=(min_date, max_date), min_value=min_date, max_value=max_date
    )
    if len(date_range) == 2:
        df = df[(df["Data"].dt.date >= date_range[0]) & (df["Data"].dt.date <= date_range[1])]

    categorias = ["Todas"] + sorted(df["Categoria"].unique().tolist())
    cat_sel = st.sidebar.selectbox("Categoria", categorias)
    if cat_sel != "Todas":
        df = df[df["Categoria"] == cat_sel]

    instituicoes = ["Todas"] + sorted(df["Instituicao"].unique().tolist())
    inst_sel = st.sidebar.selectbox("Instituição", instituicoes)
    if inst_sel != "Todas":
        df = df[df["Instituicao"] == inst_sel]

    tipos = ["Todos"] + sorted(df["Tipo"].unique().tolist())
    tipo_sel = st.sidebar.selectbox("Tipo", tipos)
    if tipo_sel != "Todos":
        df = df[df["Tipo"] == tipo_sel]

    return df


def _delta_html(atual: float, anterior: float, invert: bool = False) -> str:
    """
    Retorna HTML do badge de variação percentual.
    invert=True: queda é positiva (ex: Despesas caindo é bom).
    """
    if anterior == 0:
        return '<span class="card-delta delta-neu">— sem período anterior</span>'
    pct = (atual - anterior) / abs(anterior) * 100
    up = pct > 0
    good = up if not invert else not up
    css = "delta-up" if good else "delta-down"
    arrow = "fa-arrow-up" if up else "fa-arrow-down"
    sign = "+" if up else ""
    return (
        f'<span class="card-delta {css}">'
        f'<i class="fa-solid {arrow}"></i> {sign}{pct:.1f}% vs mês anterior'
        f'</span>'
    )


def _mes_stats(df: pd.DataFrame, anomes: str) -> dict:
    sub = df[df["AnoMes"] == anomes]
    rec = sub[sub["Valor"] > 0]["Valor"].sum()
    des = sub[sub["Valor"] < 0]["Valor"].sum()
    sal = rec + des
    eco = (sal / rec * 100) if rec > 0 else 0
    tkt = sub[sub["Valor"] < 0]["Valor"].mean() if not sub[sub["Valor"] < 0].empty else 0
    return {"receitas": rec, "despesas": des, "saldo": sal, "economia": eco, "ticket": tkt, "qtd": len(sub)}


def create_kpis(df: pd.DataFrame):
    receitas = df[df["Valor"] > 0]["Valor"].sum()
    despesas = df[df["Valor"] < 0]["Valor"].sum()
    saldo = receitas + despesas
    economia_pct = (saldo / receitas * 100) if receitas > 0 else 0
    ticket_medio = df[df["Valor"] < 0]["Valor"].mean() if not df[df["Valor"] < 0].empty else 0
    qtd_transacoes = len(df)

    # Comparação com período anterior (últimos dois meses presentes nos dados)
    meses = sorted(df["AnoMes"].unique())
    prev: dict | None = None
    if len(meses) >= 2:
        curr_stats = _mes_stats(df, meses[-1])
        prev = _mes_stats(df, meses[-2])
    else:
        curr_stats = {"receitas": receitas, "despesas": despesas, "saldo": saldo,
                      "economia": economia_pct, "ticket": ticket_medio, "qtd": qtd_transacoes}

    def delta(key: str, invert: bool = False) -> str:
        if prev is None:
            return '<span class="card-delta delta-neu">— período único</span>'
        return _delta_html(curr_stats[key], prev[key], invert=invert)

    cols = st.columns(6)
    kpis = [
        ("arrow-trend-up", "Receitas",     f"R$ {receitas:,.2f}",          "#27ae60", delta("receitas")),
        ("credit-card",    "Despesas",     f"R$ {abs(despesas):,.2f}",     "#e74c3c", delta("despesas", invert=True)),
        ("wallet",         "Saldo",        f"R$ {saldo:,.2f}",             "#2980b9" if saldo >= 0 else "#e74c3c", delta("saldo")),
        ("piggy-bank",     "Economia",     f"{economia_pct:.1f}%",         "#8e44ad", delta("economia")),
        ("receipt",        "Ticket Médio", f"R$ {abs(ticket_medio):,.2f}", "#f39c12", delta("ticket", invert=True)),
        ("list-check",     "Transações",   str(qtd_transacoes),            "#16a085", delta("qtd")),
    ]
    for col, (icon, label, value, color, dlt) in zip(cols, kpis):
        with col:
            st.markdown(
                f'<div class="metric-card" style="border-top: 4px solid {color};">'
                f'<div class="card-icon"><i class="fa-solid fa-{icon}"></i></div>'
                f'<div class="card-label">{label}</div>'
                f'<div class="card-value">{value}</div>'
                f'{dlt}'
                f"</div>",
                unsafe_allow_html=True,
            )

    return receitas, despesas, saldo


def create_charts(df: pd.DataFrame):
    despesas_df = df[df["Valor"] < 0].copy()
    receitas_df = df[df["Valor"] > 0].copy()

    # --- Evolução financeira ---
    st.markdown(sec("chart-line", "Evolução Financeira"), unsafe_allow_html=True)
    monthly = (
        df.groupby("AnoMes")["Valor"]
        .agg(
            Receitas=lambda x: x[x > 0].sum(),
            Despesas=lambda x: x[x < 0].sum(),
        )
        .reset_index()
    )
    monthly["Despesas"] = monthly["Despesas"].abs()
    monthly["Saldo"] = monthly["Receitas"] - monthly["Despesas"]
    monthly = monthly.sort_values("AnoMes")

    fig_evo = go.Figure()
    fig_evo.add_trace(go.Bar(x=monthly["AnoMes"], y=monthly["Receitas"], name="Receitas", marker_color="#27ae60"))
    fig_evo.add_trace(go.Bar(x=monthly["AnoMes"], y=monthly["Despesas"], name="Despesas", marker_color="#e74c3c"))
    fig_evo.add_trace(go.Scatter(x=monthly["AnoMes"], y=monthly["Saldo"], name="Saldo", mode="lines+markers", line=dict(color="#2980b9", width=3)))
    fig_evo.update_layout(barmode="group", template="plotly_white", height=380, legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig_evo, use_container_width=True)

    # --- Pizza e Barras instituição ---
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(sec("chart-pie", "Gastos por Categoria"), unsafe_allow_html=True)
        if not despesas_df.empty:
            cat_data = despesas_df.groupby("Categoria")["Valor"].sum().abs().reset_index()
            fig_pizza = px.pie(cat_data, values="Valor", names="Categoria", hole=0.45,
                               color_discrete_sequence=px.colors.qualitative.Set3)
            fig_pizza.update_layout(template="plotly_white", height=350)
            st.plotly_chart(fig_pizza, use_container_width=True)

    with col2:
        st.markdown(sec("building-columns", "Gastos por Instituição"), unsafe_allow_html=True)
        inst_data = despesas_df.groupby("Instituicao")["Valor"].sum().abs().reset_index().sort_values("Valor", ascending=True)
        fig_inst = px.bar(inst_data, x="Valor", y="Instituicao", orientation="h",
                          color="Valor", color_continuous_scale="Blues",
                          labels={"Valor": "Total (R$)", "Instituicao": ""})
        fig_inst.update_layout(template="plotly_white", height=350, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_inst, use_container_width=True)

    # --- Fluxo de caixa e distribuição receitas ---
    col3, col4 = st.columns(2)

    with col3:
        st.markdown(sec("arrows-left-right", "Fluxo de Caixa Mensal"), unsafe_allow_html=True)
        fig_fluxo = go.Figure()
        fig_fluxo.add_trace(go.Bar(x=monthly["AnoMes"], y=monthly["Receitas"], name="Receitas", marker_color="#27ae60", opacity=0.85))
        fig_fluxo.add_trace(go.Bar(x=monthly["AnoMes"], y=-monthly["Despesas"], name="Despesas", marker_color="#e74c3c", opacity=0.85))
        fig_fluxo.update_layout(barmode="relative", template="plotly_white", height=350,
                                 legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig_fluxo, use_container_width=True)

    with col4:
        st.markdown(sec("dollar-sign", "Distribuição de Receitas"), unsafe_allow_html=True)
        if not receitas_df.empty:
            rec_cat = receitas_df.groupby("Categoria")["Valor"].sum().reset_index()
            fig_rec = px.pie(rec_cat, values="Valor", names="Categoria", hole=0.45,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_rec.update_layout(template="plotly_white", height=350)
            st.plotly_chart(fig_rec, use_container_width=True)

    # --- Top 10 maiores gastos ---
    st.markdown(sec("ranking-star", "Top 10 Maiores Gastos"), unsafe_allow_html=True)
    if not despesas_df.empty:
        top10 = despesas_df.nsmallest(10, "Valor").copy()
        top10["Valor_abs"] = top10["Valor"].abs()
        top10["Label"] = top10["Data"].dt.strftime("%d/%m") + " – " + top10["Descricao"]
        fig_top = px.bar(top10, x="Valor_abs", y="Label", orientation="h",
                         color="Valor_abs", color_continuous_scale="Reds",
                         labels={"Valor_abs": "Valor (R$)", "Label": ""})
        fig_top.update_layout(template="plotly_white", height=380, coloraxis_showscale=False)
        st.plotly_chart(fig_top, use_container_width=True)

    # --- Evolução mensal acumulada ---
    st.markdown(sec("chart-area", "Evolução Mensal Acumulada"), unsafe_allow_html=True)
    monthly["Saldo_Acum"] = monthly["Saldo"].cumsum()
    fig_area = go.Figure()
    fig_area.add_trace(go.Scatter(
        x=monthly["AnoMes"], y=monthly["Saldo_Acum"],
        fill="tozeroy", mode="lines+markers",
        line=dict(color="#2980b9", width=2),
        fillcolor="rgba(41,128,185,0.15)",
        name="Saldo Acumulado"
    ))
    fig_area.update_layout(template="plotly_white", height=300)
    st.plotly_chart(fig_area, use_container_width=True)

    # --- Heatmap de gastos por dia da semana ---
    st.markdown(sec("calendar-days", "Padrão de Gastos por Dia da Semana"), unsafe_allow_html=True)
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_labels = {"Monday": "Seg", "Tuesday": "Ter", "Wednesday": "Qua",
                  "Thursday": "Qui", "Friday": "Sex", "Saturday": "Sáb", "Sunday": "Dom"}
    if not despesas_df.empty:
        week_data = despesas_df.groupby("Semana")["Valor"].sum().abs().reindex(day_order).fillna(0).reset_index()
        week_data["Semana_PT"] = week_data["Semana"].map(day_labels)
        fig_week = px.bar(week_data, x="Semana_PT", y="Valor",
                          color="Valor", color_continuous_scale="Oranges",
                          labels={"Valor": "Total Gasto (R$)", "Semana_PT": "Dia da Semana"})
        fig_week.update_layout(template="plotly_white", height=300, coloraxis_showscale=False)
        st.plotly_chart(fig_week, use_container_width=True)


def generate_insights(df: pd.DataFrame):
    st.markdown(sec("lightbulb", "Insights Automáticos"), unsafe_allow_html=True)
    despesas_df = df[df["Valor"] < 0].copy()
    receitas_df = df[df["Valor"] > 0].copy()

    insights = []

    if not despesas_df.empty:
        top_cat = despesas_df.groupby("Categoria")["Valor"].sum().abs().idxmax()
        top_cat_val = despesas_df.groupby("Categoria")["Valor"].sum().abs().max()
        insights.append(f'<i class="fa-solid fa-trophy"></i> Sua maior categoria de gastos é <b>{top_cat}</b> com R$ {top_cat_val:,.2f}.')

        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_labels = {"Monday": "Segunda", "Tuesday": "Terça", "Wednesday": "Quarta",
                      "Thursday": "Quinta", "Friday": "Sexta", "Saturday": "Sábado", "Sunday": "Domingo"}
        top_day_en = despesas_df.groupby("Semana")["Valor"].sum().abs().reindex(day_order).idxmax()
        insights.append(f'<i class="fa-solid fa-calendar-day"></i> Você gasta mais às <b>{day_labels.get(top_day_en, top_day_en)}</b>.')

        maior_gasto = despesas_df.loc[despesas_df["Valor"].idxmin()]
        insights.append(f'<i class="fa-solid fa-credit-card"></i> Maior gasto registrado: <b>{maior_gasto["Descricao"]}</b> em {maior_gasto["Data"].strftime("%d/%m/%Y")} — R$ {abs(maior_gasto["Valor"]):,.2f}.')

        media_mensal = despesas_df.groupby("AnoMes")["Valor"].sum().abs().mean()
        insights.append(f'<i class="fa-solid fa-chart-bar"></i> Sua média mensal de despesas é <b>R$ {media_mensal:,.2f}</b>.')

    if not receitas_df.empty:
        receitas_total = receitas_df["Valor"].sum()
        despesas_total = despesas_df["Valor"].sum() if not despesas_df.empty else 0
        saldo = receitas_total + despesas_total
        economia_pct = (saldo / receitas_total * 100) if receitas_total > 0 else 0
        insights.append(f'<i class="fa-solid fa-piggy-bank"></i> Você economizou <b>{economia_pct:.1f}%</b> da sua renda no período.')

    for insight in insights:
        st.markdown(f'<div class="insight-card">{insight}</div>', unsafe_allow_html=True)


def generate_alerts(df: pd.DataFrame):
    st.markdown(sec("triangle-exclamation", "Alertas Financeiros"), unsafe_allow_html=True)
    despesas_df = df[df["Valor"] < 0].copy()
    alertas = []

    if not despesas_df.empty and "AnoMes" in despesas_df.columns:
        monthly_despesas = despesas_df.groupby("AnoMes")["Valor"].sum().abs().sort_index()
        if len(monthly_despesas) >= 2:
            ultimo = monthly_despesas.iloc[-1]
            penultimo = monthly_despesas.iloc[-2]
            variacao = ((ultimo - penultimo) / penultimo * 100) if penultimo != 0 else 0
            if variacao > 20:
                alertas.append(("danger", f'<i class="fa-solid fa-arrow-trend-up"></i> Gastos aumentaram <b>{variacao:.1f}%</b> em relação ao mês anterior.'))
            elif variacao > 0:
                alertas.append(("warning", f'<i class="fa-solid fa-circle-up"></i> Gastos subiram <b>{variacao:.1f}%</b> em relação ao mês anterior.'))

    receitas = df[df["Valor"] > 0]["Valor"].sum()
    despesas = df[df["Valor"] < 0]["Valor"].sum()
    saldo = receitas + despesas
    if receitas > 0:
        economia_pct = saldo / receitas * 100
        if economia_pct < 10:
            alertas.append(("danger", f'<i class="fa-solid fa-circle-exclamation"></i> Taxa de economia muito baixa: <b>{economia_pct:.1f}%</b>. Meta recomendada: 20%.'))
        elif economia_pct < 20:
            alertas.append(("warning", f'<i class="fa-solid fa-circle-info"></i> Taxa de economia abaixo do ideal: <b>{economia_pct:.1f}%</b>.'))

    if not alertas:
        st.markdown('<div class="insight-card"><i class="fa-solid fa-circle-check"></i> Nenhum alerta identificado. Suas finanças estão saudáveis!</div>', unsafe_allow_html=True)
    else:
        for tipo, msg in alertas:
            css_class = "alert-danger" if tipo == "danger" else "alert-card"
            st.markdown(f'<div class="{css_class}">{msg}</div>', unsafe_allow_html=True)


def meta_financeira(receitas: float, despesas: float):
    st.markdown(sec("bullseye", "Meta Financeira"), unsafe_allow_html=True)
    saldo = receitas + despesas
    meta = st.number_input("Defina sua meta de economia mensal (R$)", min_value=0.0, value=1000.0, step=100.0)
    if meta > 0:
        progresso = min(saldo / meta, 1.0) if meta > 0 else 0
        st.progress(progresso)
        st.markdown(
            f"**Economia atual:** R$ {saldo:,.2f} &nbsp;|&nbsp; "
            f"**Meta:** R$ {meta:,.2f} &nbsp;|&nbsp; "
            f"**Progresso:** {progresso * 100:.1f}%"
        )
        if progresso >= 1.0:
            st.success("🎉 Parabéns! Você atingiu sua meta de economia!")
        elif progresso >= 0.75:
            st.info("👍 Você está quase lá! Continue assim.")
        else:
            st.warning("💪 Continue focado para atingir sua meta.")


# ────────────────────────────── Layout principal ──────────────────────────────

st.markdown(
    "<h1 style='text-align:center; color:#1e3a5f; margin-bottom:0;'>"
    "<i class='fa-solid fa-chart-line' style='color:#2d5a8e;margin-right:12px;'></i>"
    "Finance Dashboard</h1>"
    "<p style='text-align:center; color:#7f8c8d; margin-top:4px;'>Plataforma de análise financeira pessoal</p>",
    unsafe_allow_html=True,
)
st.divider()

uploaded_file = st.file_uploader(
    "📂 Faça o upload da sua planilha financeira (.csv)",
    type=["csv"],
    help="Qualquer CSV com colunas de data e valor. Você vai mapear as colunas na próxima etapa.",
)

# Limpa mapeamento anterior quando troca de arquivo
if uploaded_file is None:
    st.session_state.pop("col_mapping", None)
    st.session_state.pop("mapping_confirmed", None)

if uploaded_file is None:
    st.info("👆 Faça o upload de qualquer CSV com suas movimentações financeiras.")
    st.markdown("""
    **O app aceita qualquer planilha** — não importa o nome das colunas.
    Após o upload você vai indicar qual coluna é a data, qual é o valor, etc.

    Exemplo de estrutura (mas pode ser diferente):
    ```
    Data,Historico,Banco,Valor
    01/01/2026,Salario,Nubank,5000
    02/01/2026,Mercado,Nubank,-350
    ```
    """)
else:
    df_raw = load_data(uploaded_file)

    if not st.session_state.get("mapping_confirmed"):
        column_mapping_ui(df_raw)
    else:
        mapping = st.session_state["col_mapping"]

        # Botão para refazer o mapeamento
        if st.sidebar.button(" Refazer mapeamento de colunas"):
            st.session_state.pop("col_mapping", None)
            st.session_state.pop("mapping_confirmed", None)
            st.rerun()

        df_mapped = apply_mapping(df_raw, mapping)
        df = preprocess_data(df_mapped)
        df = apply_filters(df)

        if df.empty:
            st.warning("Nenhuma transação encontrada para os filtros selecionados.")
        else:
            receitas, despesas, saldo = create_kpis(df)
            st.divider()
            create_charts(df)
            st.divider()

            col_ins, col_alt = st.columns(2)
            with col_ins:
                generate_insights(df)
            with col_alt:
                generate_alerts(df)

            st.divider()
            meta_financeira(receitas, despesas)

            with st.expander("📋 Ver dados brutos"):
                fmt = {"Valor": st.column_config.NumberColumn("Valor", format="R$ %.2f")}
                st.dataframe(df.drop(columns=["AnoMes"]), hide_index=True, column_config=fmt)
