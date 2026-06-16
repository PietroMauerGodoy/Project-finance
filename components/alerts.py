import pandas as pd
import streamlit as st

from components.styles import sec


def generate_insights(df: pd.DataFrame) -> None:
    st.markdown(sec("lightbulb", "Insights Automáticos"), unsafe_allow_html=True)

    despesas_df = df[df["Valor"] < 0].copy()
    receitas_df = df[df["Valor"] > 0].copy()
    insights: list[str] = []

    if not despesas_df.empty:
        top_cat     = despesas_df.groupby("Categoria")["Valor"].sum().abs().idxmax()
        top_cat_val = despesas_df.groupby("Categoria")["Valor"].sum().abs().max()
        insights.append(f'<i class="fa-solid fa-trophy"></i> Sua maior categoria de gastos é <b>{top_cat}</b> com R$ {top_cat_val:,.2f}.')

        day_order  = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        day_labels = {"Monday":"Segunda","Tuesday":"Terça","Wednesday":"Quarta",
                      "Thursday":"Quinta","Friday":"Sexta","Saturday":"Sábado","Sunday":"Domingo"}
        top_day = despesas_df.groupby("Semana")["Valor"].sum().abs().reindex(day_order).idxmax()
        insights.append(f'<i class="fa-solid fa-calendar-day"></i> Você gasta mais às <b>{day_labels.get(top_day, top_day)}</b>.')

        maior = despesas_df.loc[despesas_df["Valor"].idxmin()]
        insights.append(
            f'<i class="fa-solid fa-credit-card"></i> Maior gasto: '
            f'<b>{maior["Descricao"]}</b> em {maior["Data"].strftime("%d/%m/%Y")} — R$ {abs(maior["Valor"]):,.2f}.'
        )

        media = despesas_df.groupby("AnoMes")["Valor"].sum().abs().mean()
        insights.append(f'<i class="fa-solid fa-chart-bar"></i> Média mensal de despesas: <b>R$ {media:,.2f}</b>.')

    if not receitas_df.empty:
        rec   = receitas_df["Valor"].sum()
        des   = despesas_df["Valor"].sum() if not despesas_df.empty else 0
        eco   = ((rec + des) / rec * 100) if rec > 0 else 0
        insights.append(f'<i class="fa-solid fa-piggy-bank"></i> Você economizou <b>{eco:.1f}%</b> da sua renda no período.')

    for item in insights:
        st.markdown(f'<div class="insight-card">{item}</div>', unsafe_allow_html=True)


def generate_alerts(df: pd.DataFrame) -> None:
    st.markdown(sec("triangle-exclamation", "Alertas Financeiros"), unsafe_allow_html=True)

    despesas_df = df[df["Valor"] < 0].copy()
    alertas: list[tuple[str, str]] = []

    if not despesas_df.empty and "AnoMes" in despesas_df.columns:
        monthly = despesas_df.groupby("AnoMes")["Valor"].sum().abs().sort_index()
        if len(monthly) >= 2:
            last, prev = monthly.iloc[-1], monthly.iloc[-2]
            var = ((last - prev) / prev * 100) if prev != 0 else 0
            if var > 20:
                alertas.append(("danger",  f'<i class="fa-solid fa-arrow-trend-up"></i> Gastos aumentaram <b>{var:.1f}%</b> em relação ao mês anterior.'))
            elif var > 0:
                alertas.append(("warning", f'<i class="fa-solid fa-circle-up"></i> Gastos subiram <b>{var:.1f}%</b> em relação ao mês anterior.'))

    receitas = df[df["Valor"] > 0]["Valor"].sum()
    despesas = df[df["Valor"] < 0]["Valor"].sum()
    if receitas > 0:
        eco = (receitas + despesas) / receitas * 100
        if eco < 10:
            alertas.append(("danger",  f'<i class="fa-solid fa-circle-exclamation"></i> Taxa de economia muito baixa: <b>{eco:.1f}%</b>. Meta recomendada: 20%.'))
        elif eco < 20:
            alertas.append(("warning", f'<i class="fa-solid fa-circle-info"></i> Taxa de economia abaixo do ideal: <b>{eco:.1f}%</b>.'))

    if not alertas:
        st.markdown(
            '<div class="insight-card"><i class="fa-solid fa-circle-check"></i> '
            'Nenhum alerta identificado. Suas finanças estão saudáveis!</div>',
            unsafe_allow_html=True,
        )
    else:
        for kind, msg in alertas:
            css = "alert-danger" if kind == "danger" else "alert-card"
            st.markdown(f'<div class="{css}">{msg}</div>', unsafe_allow_html=True)


def meta_financeira(receitas: float, despesas: float) -> None:
    st.markdown(sec("bullseye", "Meta Financeira"), unsafe_allow_html=True)
    saldo = receitas + despesas
    meta  = st.number_input("Meta de economia (R$)", min_value=0.0, value=1000.0, step=100.0)
    if meta > 0:
        prog = min(saldo / meta, 1.0)
        st.progress(prog)
        st.markdown(
            f"**Economia atual:** R$ {saldo:,.2f} &nbsp;|&nbsp; "
            f"**Meta:** R$ {meta:,.2f} &nbsp;|&nbsp; "
            f"**Progresso:** {prog * 100:.1f}%"
        )
        if prog >= 1.0:
            st.success("Parabéns! Você atingiu sua meta de economia!")
        elif prog >= 0.75:
            st.info("Você está quase lá! Continue assim.")
        else:
            st.warning("Continue focado para atingir sua meta.")
