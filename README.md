# Finance Dashboard

> Plataforma web de análise financeira pessoal — faça upload da sua planilha bancária e receba um dashboard completo com KPIs, gráficos interativos, insights automáticos e alertas financeiros.

Construído com **Python · Streamlit · Pandas · Plotly**

---

## O que é este projeto?

Finance Dashboard é uma aplicação web que transforma qualquer planilha CSV de movimentações bancárias em um painel de análise financeira. O diferencial está no **upload flexível**: o app não exige um formato específico de colunas — você faz o mapeamento na hora, indicando qual coluna do seu arquivo corresponde à data, ao valor, à categoria, etc.

O objetivo é ajudar qualquer pessoa a entender para onde vai seu dinheiro, identificar padrões de consumo e acompanhar metas de economia — sem precisar instalar nada além do Python.

---

## Funcionalidades

### Upload inteligente de planilhas
O app aceita **qualquer CSV**, independente do nome ou ordem das colunas. Após o upload, uma tela de mapeamento exibe as colunas detectadas e sugere automaticamente as correspondências com base em aliases comuns (`data`, `date`, `valor`, `banco`, `historico`, etc.). O usuário confirma ou ajusta antes de prosseguir.

Campos opcionais como Categoria, Instituição e Tipo recebem valores padrão quando ausentes. O campo Tipo (Receita/Despesa) é derivado automaticamente pelo sinal do valor quando não fornecido.

---

### Dashboard — KPIs e Gráficos

**6 cards de KPI** no topo, cada um com variação percentual colorida em relação ao mês anterior:

| KPI | Descrição |
|-----|-----------|
| Receitas | Total de entradas no período |
| Despesas | Total de saídas no período |
| Saldo | Receitas − Despesas |
| Economia | % da renda que sobrou |
| Ticket Médio | Valor médio por transação de saída |
| Transações | Quantidade total de lançamentos |

A variação usa cores intuitivas: verde quando o número melhora, vermelho quando piora. Para despesas, queda é verde (você gastou menos); para receitas, alta é verde.

**Gráficos interativos** (todos construídos com Plotly, com zoom, hover e filtro por legenda):

- **Evolução Financeira** — barras agrupadas de receitas e despesas por mês, com linha de saldo sobreposta
- **Gastos por Categoria** — donut com proporção de cada categoria no total de despesas
- **Gastos por Instituição** — barras horizontais ordenadas por volume
- **Fluxo de Caixa Mensal** — barras empilhadas mostrando entradas e saídas sobrepostas
- **Distribuição de Receitas** — donut de onde vêm as receitas
- **Top 10 Maiores Gastos** — ranking horizontal das 10 maiores despesas do período
- **Evolução Mensal Acumulada** — gráfico de área mostrando acúmulo de saldo ao longo do tempo
- **Padrão por Dia da Semana** — barras por dia mostrando em qual dia você mais gasta

---

### Insights & Alertas

**Insights automáticos** gerados pelo Pandas a partir dos dados:
- Qual categoria consome mais dinheiro
- Em qual dia da semana você mais gasta
- Qual foi o maior gasto registrado e quando ocorreu
- Qual é a sua média mensal de despesas
- Qual o percentual de economia sobre a renda total

**Alertas financeiros** disparados automaticamente quando:
- Gastos do mês atual aumentaram mais de 20% em relação ao mês anterior
- Gastos subiram qualquer percentual positivo (aviso moderado)
- Taxa de economia caiu abaixo de 20% (aviso) ou abaixo de 10% (crítico)

Quando nenhum alerta é disparado, o painel confirma que as finanças estão saudáveis.

---

### Meta Financeira
Defina uma meta de economia mensal em reais. O app exibe uma barra de progresso com percentual atingido e feedback contextual (parabéns ao bater a meta, incentivo quando está perto, alerta quando está longe).

---

### Filtros na sidebar
Presentes em todas as páginas e persistentes entre navegações:
- **Período** — seletor de intervalo de datas
- **Categoria** — filtra por categoria de transação
- **Instituição** — filtra por banco/conta
- **Tipo** — filtra por Receita ou Despesa

---

### Relatórios
- **Exportar CSV filtrado** — baixa os dados exatamente como estão filtrados na sidebar
- Excel (.xlsx) e PDF executivo planejados para versão futura

---

## Estrutura do projeto

```
finance-dashboard/
│
├── app.py                        # Página inicial: upload e mapeamento de colunas
│
├── pages/
│   ├── dashboard.py              # Página 1 — KPIs e todos os gráficos
│   ├── insights.py               # Página 2 — Insights, alertas e meta financeira
│   └── relatorios.py             # Página 3 — Exportação de dados
│
├── components/
│   ├── styles.py                 # CSS global, importação do Font Awesome e helper sec()
│   ├── kpis.py                   # Cards de KPI com lógica de delta vs mês anterior
│   ├── charts.py                 # Todas as funções de gráficos Plotly
│   └── alerts.py                 # Insights automáticos, alertas e meta financeira
│
├── services/
│   ├── preprocessing.py          # Carregamento, mapeamento, pré-processamento e filtros
│   ├── forecasting.py            # Placeholder — previsão de gastos (LinearRegression / Prophet)
│   └── ai_insights.py            # Placeholder — chat financeiro com IA (Claude / OpenAI)
│
├── assets/                       # Recursos estáticos (imagens, ícones locais)
├── requirements.txt
└── README.md
```

A separação em `components/` e `services/` mantém a lógica de negócio desacoplada da interface. Cada página em `pages/` importa apenas o que precisa — se amanhã você quiser trocar uma biblioteca de gráficos, só toca em `charts.py`.

---

## Pré-requisitos

- **Python 3.10+**
- pip

Verifique sua versão:
```bash
python --version
```

---

## Como rodar localmente

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/finance-dashboard.git
cd finance-dashboard
```

### 2. Crie um ambiente virtual (recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

O `requirements.txt` contém:
```
streamlit>=1.32
pandas>=2.0
plotly>=5.18
```

### 4. Inicie o app

```bash
streamlit run app.py
```

O Streamlit abrirá automaticamente o navegador em `http://localhost:8501`.

> **Atenção:** sempre rode com `streamlit run app.py`, não `main.py`. O `app.py` é o ponto de entrada da versão com múltiplas páginas.

### 5. Usando o app

1. Na página inicial (**main**), faça o upload do seu arquivo `.csv`
2. Revise o mapeamento de colunas sugerido automaticamente — ajuste se necessário
3. Clique em **Confirmar mapeamento e analisar**
4. Navegue pelas páginas no menu lateral:
   - **dashboard** — KPIs e gráficos
   - **insights** — análises automáticas e alertas
   - **relatorios** — exportação

---

## Formato da planilha

O app aceita **qualquer CSV**. Os nomes de colunas não precisam ser exatos — o mapeamento é feito na interface.

Exemplo de estrutura compatível:

```csv
Data,Descricao,Categoria,Instituicao,Tipo,Valor
01/01/2026,Salario,Receita,Nubank,Receita,5000
02/01/2026,Supermercado,Alimentacao,Nubank,Despesa,-350
03/01/2026,Netflix,Lazer,Nubank,Despesa,-39
04/01/2026,Gasolina,Transporte,Inter,Despesa,-200
05/01/2026,Aluguel,Moradia,Itau,Despesa,-1500
```

| Campo | Obrigatório | Descrição |
|-------|-------------|-----------|
| Data | Sim | Qualquer formato de data reconhecido pelo Pandas |
| Valor | Sim | Número — negativos = despesa, positivos = receita |
| Descricao | Não | Nome da transação ou histórico |
| Categoria | Não | Alimentação, Transporte, Lazer, etc. |
| Instituicao | Não | Nome do banco ou conta |
| Tipo | Não | "Receita" ou "Despesa" — derivado do sinal do Valor se ausente |

---

## Tecnologias utilizadas

| Tecnologia | Versão mínima | Finalidade |
|------------|---------------|------------|
| [Python](https://python.org) | 3.10 | Linguagem base |
| [Streamlit](https://streamlit.io) | 1.32 | Framework web e roteamento multi-página |
| [Pandas](https://pandas.pydata.org) | 2.0 | Manipulação e análise dos dados |
| [Plotly](https://plotly.com/python) | 5.18 | Gráficos interativos |
| [Font Awesome 6](https://fontawesome.com) | 6.5 (CDN) | Ícones vetoriais na interface |

---

## Roadmap

### Em desenvolvimento
- [ ] Exportação de relatório em PDF com resumo executivo
- [ ] Exportação em Excel (.xlsx) formatado

### Planejado
- [ ] Chat financeiro com IA — pergunte em linguagem natural sobre seus gastos (Claude / OpenAI)
- [ ] Previsão de gastos para os próximos 3 meses (LinearRegression / Prophet)
- [ ] Score de saúde financeira de 0 a 100 com critérios ponderados
- [ ] Detecção automática de assinaturas recorrentes (Netflix, Spotify, etc.)
- [ ] Metas por categoria (ex: limitar gastos com lazer em R$ 500/mês)
- [ ] Heatmap de gastos por semana × dia da semana

---

## Licença

MIT — sinta-se livre para usar, modificar e distribuir.
