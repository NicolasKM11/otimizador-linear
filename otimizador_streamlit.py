
import streamlit as st
import numpy as np
from scipy.optimize import linprog
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Otimização Linear + Transporte", layout="centered")
st.title("🔧 Otimizador com Exportação estilo Solver (Max, Min, Transporte)")

tipo = st.selectbox("Escolha o tipo de problema", ["Maximização", "Minimização", "Transporte"])

def gerar_excel_estilo_solver(c, A, b, sinais, resultado, valor_obj):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    ws = writer.book.add_worksheet("ResultadoSolver")
    writer.sheets["ResultadoSolver"] = ws

    row = 0
    ws.write(row, 0, "Função Objetivo:")
    row += 1
    z_eq = "Z = " + " + ".join([f"{int(c[i])}·x{i+1}" for i in range(len(c))])
    ws.write(row, 0, z_eq)
    row += 2

    ws.write(row, 0, "Restrição")
    ws.write(row, 1, "Expressão")
    row += 1
    for i, linha in enumerate(A):
        restr = " + ".join([f"{linha[j]}·x{j+1}" for j in range(len(c))])
        ws.write(row, 0, f"R{i+1}")
        ws.write(row, 1, f"{restr} {sinais[i]} {b[i]}")
        row += 1

    row += 2
    ws.write(row, 0, "Solução")
    ws.write(row, 1, "Valor")
    for i, val in enumerate(resultado):
        ws.write(row+1+i, 0, f"x{i+1}")
        ws.write(row+1+i, 1, val)
    ws.write(row+1+len(resultado), 0, "Z")
    ws.write(row+1+len(resultado), 1, valor_obj)

    row += len(resultado) + 4
    ws.write(row, 0, "Como resolver isso no Solver do Excel:")
    instrucoes = [
        "1. Vá até a aba 'Dados' > clique em 'Solver'.",
        "2. Defina a célula da função objetivo (ex: célula do Z).",
        "3. Escolha 'Máx' ou 'Min', dependendo do problema.",
        "4. Defina o intervalo de variáveis (ex: x1, x2...).",
        "5. Clique em 'Adicionar' para inserir as restrições.",
        "6. Clique em 'Resolver'.",
    ]
    for i, instrucao in enumerate(instrucoes):
        ws.write(row+1+i, 0, instrucao)

    writer.close()
    output.seek(0)
    return output

if tipo in ["Maximização", "Minimização"]:
    st.subheader("1️⃣ Função Objetivo")
    num_vars = st.number_input("Quantas variáveis?", min_value=2, max_value=10, value=2)
    c = []
    for i in range(num_vars):
        c.append(st.number_input(f"Coeficiente de x{i+1}", value=0.0))
    c = np.array(c)

    st.subheader("2️⃣ Restrições")
    num_rest = st.number_input("Quantas restrições?", min_value=1, max_value=10, value=2)
    A, b, sinais = [], [], []
    for i in range(int(num_rest)):
        st.markdown(f"**Restrição R{i+1}**")
        linha = []
        for j in range(int(num_vars)):
            linha.append(st.number_input(f"Coef x{j+1} (R{i+1})", key=f"r{i}v{j}", value=0.0))
        A.append(linha)
        sinais.append(st.selectbox("Sinal", ["<=", ">=", "="], key=f"sinal{i}"))
        b.append(st.number_input("Limite (lado direito)", key=f"b{i}", value=0.0))

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

        c_solve = -c if tipo == "Maximização" else c

        res = linprog(c_solve, A_ub=A_ub or None, b_ub=b_ub or None,
                      A_eq=A_eq or None, b_eq=b_eq or None,
                      bounds=[(0, None)] * num_vars, method='highs')

        if res.success:
            valor_obj = (-1 if tipo == "Maximização" else 1) * res.fun
            st.success("✅ Solução encontrada!")
            for i, val in enumerate(res.x):
                st.write(f"x{i+1} = {val:.2f}")
            st.write(f"Z = {valor_obj:.2f}")

            excel_file = gerar_excel_estilo_solver(c, A, b, sinais, res.x, valor_obj)
            st.download_button("📥 Baixar resolução estilo Solver (.xlsx)", data=excel_file,
                               file_name="solver_resultado.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.error("❌ Não foi possível encontrar solução viável.")

elif tipo == "Transporte":
    st.subheader("🔄 Problema de Transporte")
    origem = st.number_input("Número de origens", min_value=2, max_value=10, value=3)
    destino = st.number_input("Número de destinos", min_value=2, max_value=10, value=3)

    st.markdown("**Custos de Transporte**")
    custos = []
    for i in range(origem):
        linha = []
        for j in range(destino):
            linha.append(st.number_input(f"Custo O{i+1}-D{j+1}", key=f"c{i}{j}", value=0.0))
        custos.append(linha)

    st.markdown("**Ofertas**")
    oferta = [st.number_input(f"Oferta O{i+1}", key=f"of{i}", value=0.0) for i in range(origem)]

    st.markdown("**Demandas**")
    demanda = [st.number_input(f"Demanda D{j+1}", key=f"dem{j}", value=0.0) for j in range(destino)]

    if st.button("🚚 Resolver Transporte"):
        custo = np.array(custos).flatten()
        A_eq = []
        b_eq = []

        for i in range(origem):
            linha = [0] * (origem * destino)
            for j in range(destino):
                linha[i * destino + j] = 1
            A_eq.append(linha)
            b_eq.append(oferta[i])

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
