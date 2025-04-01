
import streamlit as st
import numpy as np
from scipy.optimize import linprog
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Otimizador Excel Solver Automático", layout="centered")
st.title("🔧 Otimizador - Gera Excel pronto para Solver")

tipo = st.selectbox("Tipo de problema:", ["Maximização", "Minimização"])

def gerar_excel_solver_pronto(c, A, b, sinais):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    wb = writer.book
    ws = wb.add_worksheet("SolverPronto")
    writer.sheets["SolverPronto"] = ws

    # Cabeçalhos
    ws.write("A1", "Variável")
    ws.write("B1", "Coef. Obj")
    for j in range(len(A[0])):
        ws.write(0, 2 + j, f"R{j+1}")
    ws.write("G1", "Lim. Inf")
    ws.write("H1", "Lim. Sup")

    # Variáveis
    for i in range(len(c)):
        ws.write(i+1, 0, f"x{i+1}")
        ws.write(i+1, 1, c[i])
        for j in range(len(A[0])):
            ws.write(i+1, 2 + j, A[i][j])
        ws.write(i+1, 6, 0)  # Limite inferior
        ws.write(i+1, 7, "")  # Limite superior

    # Restrições (lado direito e sinais)
    row_offset = len(c) + 3
    ws.write(row_offset, 1, "Restrição")
    ws.write(row_offset, 2, "Sinal")
    ws.write(row_offset, 3, "Lado Direito")

    for i in range(len(A[0])):
        ws.write(row_offset + i + 1, 1, f"R{i+1}")
        ws.write(row_offset + i + 1, 2, sinais[i])
        ws.write(row_offset + i + 1, 3, b[i])

    # Função objetivo
    var_cells = [f"A{i+2}" for i in range(len(c))]  # x variáveis (coluna A)
    coef_cells = [f"B{i+2}" for i in range(len(c))]  # coeficientes (coluna B)
    mults = [f"{coef_cells[i]}*{var_cells[i]}" for i in range(len(c))]
    formula = "=" + "+".join(mults)
    obj_row = row_offset + len(A[0]) + 3
    ws.write(obj_row, 0, "Função Objetivo:")
    ws.write_formula(obj_row, 1, formula)

    # Instruções detalhadas
    instr_row = obj_row + 2
    instrucoes = [
        "PASSO A PASSO PARA USAR NO SOLVER:",
        "1. Vá até a aba 'Dados' e clique em 'Solver'.",
        f"2. Defina a célula da função objetivo: B{obj_row+1}",
        f"3. Marque '{'Max' if tipo == 'Maximização' else 'Min'}'.",
        f"4. Defina as variáveis em: A2:A{len(c)+1}",
        "5. Adicione as restrições abaixo:",
    ]
    for i, texto in enumerate(instrucoes):
        ws.write(instr_row + i, 0, texto)

    restr_row_start = instr_row + len(instrucoes)
    for i in range(len(A[0])):
        restr = " + ".join([f"{A[j][i]}*A{j+2}" for j in range(len(c))])
        sinal = sinais[i]
        lado = b[i]
        ws.write(restr_row_start + i, 0, f"{restr} {sinal} {lado}")

    writer.close()
    output.seek(0)
    return output

if tipo in ["Maximização", "Minimização"]:
    st.subheader("Função Objetivo")
    num_vars = st.number_input("Quantas variáveis?", min_value=2, max_value=10, value=2)
    c = [st.number_input(f"Coeficiente de x{i+1}", value=0.0) for i in range(num_vars)]

    st.subheader("Restrições")
    num_rest = st.number_input("Quantas restrições?", min_value=1, max_value=10, value=2)
    A = []
    b = []
    sinais = []

    for i in range(int(num_rest)):
        linha = []
        st.markdown(f"**Restrição R{i+1}**")
        for j in range(num_vars):
            linha.append(st.number_input(f"Coef x{j+1} (R{i+1})", key=f"r{i}v{j}", value=0.0))
        A.append(linha)
        sinais.append(st.selectbox("Sinal", ["<=", ">=", "="], key=f"sinal{i}"))
        b.append(st.number_input("Lado direito", key=f"b{i}", value=0.0))

    if st.button("📤 Gerar Excel pronto para Solver"):
        excel_file = gerar_excel_solver_pronto(c, A, b, sinais)
        st.download_button("📥 Baixar Excel Solver", data=excel_file,
                           file_name="resolver_no_excel.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
