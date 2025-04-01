import streamlit as st
import numpy as np
from scipy.optimize import linprog
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Otimização Linear", layout="centered")
st.title("🔧 Resolução de Programação Linear (com exportação Excel)")

tipo = st.selectbox("Escolha o tipo de problema", ["Maximização", "Minimização", "Transporte"])

def gerar_excel_solucao(tipo, c, A, b, sinais, resultado, valor_obj):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_obj = pd.DataFrame([c], columns=[f'x{i+1}' for i in range(len(c))])
        df_obj.to_excel(writer, index=False, sheet_name="Funcao_Objetivo")

        df_rest = pd.DataFrame(A, columns=[f'x{i+1}' for i in range(len(c))])
        df_rest["Sinal"] = sinais
        df_rest["Limite"] = b
        df_rest.to_excel(writer, index=False, sheet_name="Restricoes")

        df_sol = pd.DataFrame({"Variável": [f'x{i+1}' for i in range(len(resultado))], "Valor": resultado})
        df_sol.loc[len(df_sol.index)] = ["Função Objetivo", valor_obj]
        df_sol.to_excel(writer, index=False, sheet_name="Resultado")

    output.seek(0)
    return output

def exibir_debug(c, A_ub, b_ub, A_eq, b_eq):
    st.markdown("### 🧪 Debug: Estruturas Internas")
    st.write("**Coeficientes da função objetivo:**", c)
    if A_ub:
        st.write("**Restrições (≤ / ≥) convertidas:**", A_ub)
        st.write("**Limites (b_ub):**", b_ub)
    if A_eq:
        st.write("**Restrições (=):**", A_eq)
        st.write("**Limites (b_eq):**", b_eq)

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

        c_otim = -c if tipo == "Maximização" else c

        res = linprog(c_otim, A_ub=A_ub or None, b_ub=b_ub or None,
                      A_eq=A_eq or None, b_eq=b_eq or None,
                      bounds=[(0, None)] * num_vars, method='highs')

        exibir_debug(c, A_ub, b_ub, A_eq, b_eq)

        if res.success:
            st.success("✅ Solução encontrada!")
            for i, val in enumerate(res.x):
                st.write(f"x{i+1} = {val:.2f}")
            valor_obj = (-1 if tipo == "Maximização" else 1) * res.fun
            st.write(f"Função objetivo = {valor_obj:.2f}")

            excel_data = gerar_excel_solucao(tipo, c, A, b, sinais, res.x, valor_obj)
            st.download_button(label="📥 Baixar Resultado (.xlsx)", data=excel_data,
                               file_name="resultado_otimizacao.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.error("❌ Não foi possível encontrar uma solução viável.")
            st.markdown("🧾 *Verifique se as restrições não estão se contradizendo.*")

