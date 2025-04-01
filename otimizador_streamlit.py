
import streamlit as st
import numpy as np
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Excel Solver Automático", layout="centered")
st.title("🔧 Geração de Excel com Instruções Completas para o Solver")

tipo = st.selectbox("Tipo de problema", ["Maximização", "Minimização"])

def gerar_excel_solver_estilo_final(c, A, b, sinais):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    wb = writer.book
    ws = wb.add_worksheet("Solver")
    writer.sheets["Solver"] = ws

    num_vars = len(c)
    num_rest = len(A[0])

    # Cabeçalhos
    ws.write("A1", "Variável")
    for i in range(num_vars):
        ws.write(0, i + 1, f"x{i+1}")

    ws.write("A2", "Coef. Obj")
    for i in range(num_vars):
        ws.write(1, i + 1, c[i])

    for j in range(num_rest):
        ws.write(j + 2, 0, f"R{j+1}")
        for i in range(num_vars):
            ws.write(j + 2, i + 1, A[i][j])

    # Lado direito
    ws.write("G1", "Sinais")
    ws.write("H1", "LD")
    for j in range(num_rest):
        ws.write(j + 2, 6, sinais[j])
        ws.write(j + 2, 7, b[j])

    # Função objetivo
    coef_range = f"B2:{chr(65 + num_vars)}2"
    var_range = f"B3:{chr(65 + num_vars)}3"
    ws.write("A10", "Função Objetivo:")
    ws.write_formula("B10", f"=SUMPRODUCT({coef_range},{var_range})")

    # Instruções estilo Solver
    base = 12
    ws.write(base, 0, "🧩 Instruções para o Solver do Excel:")
    ws.write(base + 1, 0, "1. Definir objetivo: $B$10")
    ws.write(base + 2, 0, f"2. Tipo: {'Maximizar' if tipo == 'Maximização' else 'Minimizar'}")
    ws.write(base + 3, 0, f"3. Variáveis: $B$3:{chr(65 + num_vars)}$3")
    ws.write(base + 4, 0, "4. Restrições:")
    for j in range(num_rest):
        linha = f"   - $B${j+4}:${chr(65 + num_vars)}${j+4} {sinais[j]} $H${j+4}"
        ws.write(base + 5 + j, 0, linha)

    writer.close()
    output.seek(0)
    return output

if tipo:
    st.subheader("1️⃣ Função Objetivo")
    num_vars = st.number_input("Quantas variáveis?", min_value=2, max_value=10, value=2)
    c = [st.number_input(f"Coef. x{i+1}", value=0.0) for i in range(num_vars)]

    st.subheader("2️⃣ Restrições")
    num_rest = st.number_input("Quantas restrições?", min_value=1, max_value=10, value=2)
    A, b, sinais = [], [], []
    for i in range(int(num_rest)):
        linha = []
        st.markdown(f"**Restrição R{i+1}**")
        for j in range(num_vars):
            linha.append(st.number_input(f"Coef. x{j+1} (R{i+1})", key=f"r{i}v{j}", value=0.0))
        A.append(linha)
        sinais.append(st.selectbox("Sinal", ["<=", ">=", "="], key=f"sinal{i}"))
        b.append(st.number_input("Lado Direito", key=f"b{i}", value=0.0))

    if st.button("📥 Gerar Excel com Instruções Solver"):
        file = gerar_excel_solver_estilo_final(c, A, b, sinais)
        st.download_button("📥 Baixar Excel", data=file,
                           file_name="solver_instrucoes_completas.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
