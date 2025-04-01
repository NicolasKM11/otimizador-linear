
import streamlit as st
import numpy as np
from scipy.optimize import linprog

st.set_page_config(page_title="Otimização Linear", layout="centered")
st.title("🔧 Resolução de Programação Linear")

tipo = st.selectbox("Escolha o tipo de problema", ["Maximização", "Minimização", "Transporte"])

if tipo in ["Maximização", "Minimização"]:
    st.subheader("1️⃣ Dados da Função Objetivo")
    num_vars = st.number_input("Quantas variáveis?", min_value=2, max_value=10, value=3)
    c = []
    for i in range(num_vars):
        val = st.number_input(f"Coeficiente de x{i+1}", value=0.0, step=1.0, format="%.2f")
        c.append(val)
    c = np.array(c)

    st.subheader("2️⃣ Restrições")
    num_rest = st.number_input("Quantas restrições?", min_value=1, max_value=10, value=3)
    A = []
    b = []
    sinais = []

    for i in range(int(num_rest)):
        st.markdown(f"**Restrição {i+1}**")
        linha = []
        for j in range(int(num_vars)):
            linha.append(st.number_input(f"Coef x{j+1} (R{i+1})", key=f"r{i}v{j}", value=0.0))
        sinal = st.selectbox("Sinal", ["<=", ">=", "="], key=f"sinal{i}")
        limite = st.number_input("Limite (lado direito)", key=f"b{i}", value=0.0)
        A.append(linha)
        b.append(limite)
        sinais.append(sinal)

    st.subheader("3️⃣ Resolver")
    if st.button("🔍 Resolver"):
        A_ub, b_ub, A_eq, b_eq = [], [], [], []
        for i, sinal in enumerate(sinais):
            if sinal == "<=":
                A_ub.append(A[i])
                b_ub.append(b[i])
            elif sinal == ">=":
                A_ub.append([-a for a in A[i]])
                b_ub.append(-b[i])
            else:
                A_eq.append(A[i])
                b_eq.append(b[i])

        if tipo == "Maximização":
            c = -c  # Maximizar = minimizar negativo

        res = linprog(c, A_ub=A_ub or None, b_ub=b_ub or None,
                      A_eq=A_eq or None, b_eq=b_eq or None,
                      bounds=[(0, None)] * num_vars, method='highs')

        if res.success:
            st.success("✅ Solução encontrada!")
            for i, val in enumerate(res.x):
                st.write(f"x{i+1} = {val:.2f}")
            st.write(f"Função objetivo = {(-1 if tipo == 'Maximização' else 1) * res.fun:.2f}")
        else:
            st.error("❌ Não foi possível encontrar uma solução viável.")

elif tipo == "Transporte":
    st.subheader("🔄 Problema de Transporte")
    origem = st.number_input("Número de origens", min_value=2, max_value=10, value=3)
    destino = st.number_input("Número de destinos", min_value=2, max_value=10, value=4)

    st.markdown("**Custos de Transporte**")
    custos = []
    for i in range(int(origem)):
        linha = []
        for j in range(int(destino)):
            linha.append(st.number_input(f"Custo O{i+1}-D{j+1}", key=f"c{i}{j}", value=0.0))
        custos.append(linha)

    st.markdown("**Ofertas**")
    oferta = [st.number_input(f"Oferta O{i+1}", key=f"of{i}", value=0.0) for i in range(int(origem))]

    st.markdown("**Demandas**")
    demanda = [st.number_input(f"Demanda D{j+1}", key=f"dem{j}", value=0.0) for j in range(int(destino))]

    if st.button("🚚 Resolver Transporte"):
        from scipy.optimize import linprog

        custo = np.array(custos).flatten()
        A_eq = []
        b_eq = []

        # Restrições de oferta
        for i in range(origem):
            linha = [0] * (origem * destino)
            for j in range(destino):
                linha[i * destino + j] = 1
            A_eq.append(linha)
            b_eq.append(oferta[i])

        # Restrições de demanda
        for j in range(destino):
            linha = [0] * (origem * destino)
            for i in range(origem):
                linha[i * destino + j] = 1
            A_eq.append(linha)
            b_eq.append(demanda[j])

        res = linprog(c=custo, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)] * len(custo), method='highs')

        if res.success:
            st.success("✅ Solução encontrada!")
            solucao = res.x.reshape((origem, destino))
            for i in range(origem):
                st.write([f"{solucao[i][j]:.2f}" for j in range(destino)])
            st.write(f"🔢 Custo total mínimo: {res.fun:.2f}")
        else:
            st.error("❌ Não foi possível encontrar solução.")
