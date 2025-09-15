import streamlit as st
from datetime import date
from config import supabase as db
import pandas as pd

st.set_page_config(page_title="Organizador Financeiro", page_icon="💰", layout="wide")

# ===== MENU LATERAL =====
menu = st.sidebar.radio(
    "📌 Menu",
    ["Dashboard", "Adicionar Transação", "Relatórios", "Configurações"]
)

st.sidebar.markdown("---")
st.sidebar.info("Organizador Financeiro v1.0")

# ===== DASHBOARD =====
if menu == "Dashboard":
    st.title("📊 Dashboard")
    res = db.table("transacoes").select("id, tipo, valor, categoria, descricao, data").order("data").execute()
    transacoes = res.data

    if transacoes:
        # Filtro de pesquisa
        filtro = st.text_input("🔍 Pesquisar (categoria, descrição ou tipo):")

        if filtro:
            filtro = filtro.lower()
            transacoes_filtradas = [
                t for t in transacoes
                if filtro in str(t["categoria"]).lower()
                or filtro in str(t["descricao"]).lower()
                or filtro in str(t["tipo"]).lower()
            ]
        else:
            transacoes_filtradas = transacoes

        # Calcular métricas (com base na tabela filtrada)
        receitas = sum(t["valor"] for t in transacoes_filtradas if t["tipo"] == "receita")
        despesas = sum(t["valor"] for t in transacoes_filtradas if t["tipo"] == "despesa")
        saldo = receitas - despesas

        # ===== CARDS NO TOPO =====
        col1, col2, col3 = st.columns(3)

        col1.markdown(
            f"""
            <div style="background-color:#0f5132; padding:5px; border-radius:10px; text-align:center; color:white;">
                <h3>Receitas</h3>
                <h2>R$ {receitas:.2f}</h2>
            </div>
            """, unsafe_allow_html=True
        )

        col2.markdown(
            f"""
            <div style="background-color:#842029; padding:5px; border-radius:10px; text-align:center; color:white;">
                <h3>Despesas</h3>
                <h2>R$ {despesas:.2f}</h2>
            </div>
            """, unsafe_allow_html=True
        )

        col3.markdown(
            f"""
            <div style="background-color:#0a52be; padding:5px; border-radius:10px; text-align:center; color:white;">
                <h3>Saldo Atual</h3>
                <h2>R$ {saldo:.2f}</h2>
            </div>
            """, unsafe_allow_html=True
        )

        st.markdown("---")

        # ===== TABELA EMBAIXO =====
        if transacoes_filtradas:
            st.subheader("📑 Minhas Transações")

            # Criar DataFrame
            df = pd.DataFrame(transacoes_filtradas)

            # Reordenar colunas (mantendo id)
            colunas = ["id", "tipo", "valor", "categoria", "data", "descricao"]
            df = df[[c for c in colunas if c in df.columns]]
            df = df.rename(columns={
                "id": "ID",
                "tipo": "Tipo",
                "valor": "Valor (R$)",
                "categoria": "Categoria",
                "descricao": "Descrição",
                "data": "Data"
            })
            # Formatar valor como moeda
            df["Valor (R$)"] = df["Valor (R$)"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            
            #Formatar Tipo para mostra a 1° letra em maiusculo
            df["Tipo"] = df["Tipo"].str.capitalize()
            
            # Formatar data para ptbr
            df["Data"] = pd.to_datetime(df["Data"]).dt.strftime("%d/%m/%Y")

            # Resetar índice para não aparecer coluna fantasma
            st.table(df.reset_index(drop=True))

        else:
            st.warning("Nenhuma transação encontrada com esse filtro.")

    else:
        st.info("Nenhuma transação cadastrada ainda.")


# ===== ADICIONAR =====
elif menu == "Adicionar Transação":
    st.title("➕ Adicionar nova transação")

    with st.form("nova_transacao"):
        tipo = st.selectbox("Tipo", ["receita", "despesa"])
        valor = st.number_input("Valor (R$)", min_value=0.01, step=0.01)
        categoria = st.text_input("Categoria", "Geral")
        descricao = st.text_area("Descrição", "")
        data = st.date_input("Data", value=date.today())
        submitted = st.form_submit_button("Adicionar")

        if submitted:
            db.table("transacoes").insert({
                "tipo": tipo,
                "valor": valor,
                "categoria": categoria,
                "descricao": descricao,
                "data": str(data)
            }).execute()
            st.success("✅ Transação adicionada!")

# ===== RELATÓRIOS =====
elif menu == "Relatórios":
    st.title("📈 Relatórios (em construção)")
    st.write("Aqui você poderá ver gráficos de despesas/receitas por mês, categorias etc.")

# ===== CONFIGURAÇÕES =====
elif menu == "Configurações":
    st.title("⚙️ Configurações")
    st.write("Aqui futuramente você poderá ajustar categorias, exportar dados, etc.")
