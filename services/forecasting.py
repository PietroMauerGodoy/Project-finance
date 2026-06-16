"""
Módulo de previsão de gastos.

Fase 2 — implementar com:
  - sklearn.linear_model.LinearRegression  (curto prazo, simples)
  - prophet                                (sazonalidade, feriados)

Assinatura esperada:
    def forecast_expenses(df: pd.DataFrame, months: int = 3) -> pd.DataFrame:
        ...
        return df_forecast  # colunas: AnoMes, Valor, Lower, Upper
"""
