"""
Módulo de chat financeiro com IA.

Fase 2 — integrar com Anthropic Claude:
  - pip install anthropic

Assinatura esperada:
    def ask_financial_question(df: pd.DataFrame, question: str) -> str:
        # Serializa o df em contexto e chama a API
        ...
        return answer  # str com a resposta da IA

Contexto sugerido para o prompt:
    - Resumo das transações (total receitas, despesas, saldo)
    - Top 5 categorias de gasto
    - Meses cobertos
    - Pergunta do usuário
"""
