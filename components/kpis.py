import pandas as pd
import streamlit as st
from components.styles import sec  # noqa: F401 (re-exported for pages that need sec)


def _delta_html(atual: float, anterior: float, invert: bool = False) -> str:
    if anterior == 0:
        return '<span class="card-delta delta-neu">— sem período anterior</span>'
    pct = (atual - anterior) / abs(anterior) * 100
    up = pct > 0
    good = up if not invert else not up
    css   = "delta-up" if good else "delta-down"
    arrow = "fa-arrow-up" if up else "fa-arrow-down"
    sign  = "+" if up else ""
    return (
        f'<span class="card-delta {css}">'
        f'<i class="fa-solid {arrow}"></i> {sign}{pct:.1f}% vs mês anterior'
        f"</span>"
    )


def _mes_stats(df: pd.DataFrame, anomes: str) -> dict:
    sub = df[df["AnoMes"] == anomes]
    rec = sub[sub["Valor"] > 0]["Valor"].sum()
    des = sub[sub["Valor"] < 0]["Valor"].sum()
    sal = rec + des
    eco = (sal / rec * 100) if rec > 0 else 0
    tkt = sub[sub["Valor"] < 0]["Valor"].mean() if not sub[sub["Valor"] < 0].empty else 0
    return {"receitas": rec, "despesas": des, "saldo": sal,
            "economia": eco, "ticket": tkt, "qtd": len(sub)}


def create_kpis(df: pd.DataFrame) -> tuple[float, float, float]:
    receitas       = df[df["Valor"] > 0]["Valor"].sum()
    despesas       = df[df["Valor"] < 0]["Valor"].sum()
    saldo          = receitas + despesas
    economia_pct   = (saldo / receitas * 100) if receitas > 0 else 0
    ticket_medio   = df[df["Valor"] < 0]["Valor"].mean() if not df[df["Valor"] < 0].empty else 0
    qtd_transacoes = len(df)

    meses = sorted(df["AnoMes"].unique())
    prev: dict | None = None
    if len(meses) >= 2:
        curr = _mes_stats(df, meses[-1])
        prev = _mes_stats(df, meses[-2])
    else:
        curr = {"receitas": receitas, "despesas": despesas, "saldo": saldo,
                "economia": economia_pct, "ticket": ticket_medio, "qtd": qtd_transacoes}

    def delta(key: str, invert: bool = False) -> str:
        if prev is None:
            return '<span class="card-delta delta-neu">— período único</span>'
        return _delta_html(curr[key], prev[key], invert=invert)

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
                f"{dlt}"
                f"</div>",
                unsafe_allow_html=True,
            )

    return receitas, despesas, saldo
