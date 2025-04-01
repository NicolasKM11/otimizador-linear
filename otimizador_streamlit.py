
import streamlit as st
import numpy as np
from scipy.optimize import linprog
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Excel Pronto para Solver", layout="centered")
st.title("🔧 Geração de Excel estruturado para o Solver do Excel")

st.markdown("Este app cria um arquivo Excel com as variáveis, restrições e fórmulas **já posicionadas**, pronto para ser resolvido com o Solver do Excel. Basta abrir e seguir o passo a passo.")

tipo = st.selectbox("Tipo de problema", ["Maximização", "Minimização"])

def gerar_excel_estruturado(c, A, b, sinais):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    wb = writer.book
    ws = wb.add_worksheet("Solver")

    # Cabeçalhos
    ws.write("A1", "Variável")
    ws.write("B1", "Coef. Obj")
    for j in range(len(A[0])):
        ws.write(0, 2 + j, f"R{j+1}")

    # Variáveis e coeficientes
    for i in range(len(c)):
        ws.write(i + 1, 0, f"x{i+1}")
        ws.write(i + 1, 1, c[i])
        for j in range(len(A[0])):
            ws.write(i + 1, 2 + j, A[i][j])

    # Lado direito das restrições
    for j in range(len(b)):
        ws.write(4, 2 + j, b[j])
        ws.write(5, 2 + j, sinais[j])

    # Função objetivo com fórmula automática
    coef_range = f"B2:B{len(c)+1}"
    var_range = f"A2:A{len(c)+1}"
    ws.write("A7", "Função Objetivo:")
    ws.write_formula("B7", f"=SUMPRODUCT({coef_range}, {var_range})")

    # Instruções específicas
    ws.write("A9", "📌 Como usar no Solver do Excel:")
    instrucoes = [
        f"1. Vá na aba 'Dados' > clique em 'Solver'.",
        f"2. Defina a célula objetivo: B7",
        f"3. Marque {'Máx' if tipo == 'Maximização' else 'Min'}.",
        f"4. Defina as variáveis de decisão: A2:A{len(c)+1}",
        f"5. Adicione as restrições:",
        f"   - C2:D{len(c)+1} {'<=', '>=', '='} C5:D5 (use os sinais em C6:D6)",
        f"6. Clique em 'Resolver'."
    ]
    for i, txt in enumerate(instrucoes):
        ws.write(9 + i, 0, txt)

    writer.close()
    output.seek(0)
    return output

if tipo:
    st.subheader("1️⃣ Função Objetivo")
    num_vars = st.number_input("Quantas variáveis?", min_value=2, max_value=10, value=2)
    c = [st.number_input(f"Coeficiente de x{i+1}", value=0.0) for i in range(num_vars)]

    st.subheader("2️⃣ Restrições")
    num_rest = st.number_input("Quantas restrições?", min_value=1, max_value=10, value=2)
    A, b, sinais = [], [], []
    for i in range(int(num_rest)):
        linha = []
        st.markdown(f"**Restrição R{i+1}**")
        for j in range(num_vars):
            linha.append(st.number_input(f"Coef x{j+1} (R{i+1})", key=f"r{i}v{j}", value=0.0))
        A.append(linha)
        sinais.append(st.selectbox("Sinal", ["<=", ">=", "="], key=f"sinal{i}"))
        b.append(st.number_input("Lado direito", key=f"b{i}", value=0.0))

    if st.button("📥 Gerar Excel estruturado"):
        file = gerar_excel_estruturado(c, A, b, sinais)
        st.download_button("📥 Baixar Excel pronto para Solver", data=file,
                           file_name="excel_solver_estruturado.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
