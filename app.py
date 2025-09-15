import streamlit as st
from datetime import date
from config import supabase  # importa o cliente configurado

st.set_page_config(page_title="Organizador Financeiro", page_icon="💰", layout="wide")

st.title("💰 Organizador Financeiro")

# Formulário para adicionar transações
with st.form("nova_transacao"):
    st.subheader("Adicionar nova transação")
    tipo = st.selectbox("Tipo", ["receita", "despesa"])
    valor = st.number_input("Valor (R$)", min_value=0.01, step=0.01)
    categoria = st.text_input("Categoria", "Geral")
    descricao = st.text_area("Descrição", "")
    data = st.date_input("Data", value=date.today())
    submitted = st.form_submit_button("Adicionar")

    if submitted:
        supabase.table("transacoes").insert({
            "tipo": tipo,
            "valor": valor,
            "categoria": categoria,
            "descricao": descricao,
            "data": str(data)
        }).execute()
        st.success("✅ Transação adicionada!")

# Mostrar todas as transações
st.subheader("📊 Minhas transações")
res = supabase.table("transacoes").select("*").order("data").execute()
transacoes = res.data

if transacoes:
    st.table(transacoes)

    # Calcular saldo
    receitas = sum(t["valor"] for t in transacoes if t["tipo"] == "receita")
    despesas = sum(t["valor"] for t in transacoes if t["tipo"] == "despesa")
    saldo = receitas - despesas

    st.metric("Receitas", f"R$ {receitas:.2f}")
    st.metric("Despesas", f"R$ {despesas:.2f}")
    st.metric("Saldo Atual", f"R$ {saldo:.2f}")
else:
    st.info("Nenhuma transação cadastrada ainda.")
