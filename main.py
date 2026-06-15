import streamlit as st
import pandas as pd

# Configurações da aba do navegador "titulo, ícone e layout"
st.set_page_config(page_title="Finanças", page_icon=":money_with_wings:", layout="wide")


st.markdown(""" 

# Bem-vindo ao meu projeto de finanças pessoais!

## Um app financeiro.
            
Este projeto tem como objetivo ajudar as pessoas a gerenciar suas finanças pessoais de forma eficiente e inteligente. Ele utiliza técnicas de análise de dados e aprendizado de máquina para fornecer insights valiosos sobre os gastos, receitas e investimentos dos usuários.

""")

# Upload de arquivos e exibição dos dados
files_up = st.file_uploader("Faça o upload do seu arquivo financeiro", type=["csv"])
if files_up is not None:
    df = pd.read_csv(files_up)
    columns_fmt = {"Valor": st.column_config.NumberColumn("Valor", format="R$ %f")}
    st.dataframe(df, hide_index=True, column_config=columns_fmt)

    df_intituto = df.pivot_table(index="Data", columns="Instituição", values="Valor")
    st.dataframe(df_intituto)