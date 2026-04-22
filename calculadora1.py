import streamlit as st
import pandas as pd
import itertools

def traducir(expr):
    expr = expr.replace("¬", " not ")
    expr = expr.replace("∧", " and ")
    expr = expr.replace("∨", " or ")
    return expr

def evaluar(expr, contexto):
    # condicional y bicondicional manejados explícitamente
    if "→" in expr:
        partes = expr.split("→",1)
        izq = traducir(partes[0])
        der = traducir(partes[1])
        return (not eval(izq, {}, contexto)) or eval(der, {}, contexto)
    elif "↔" in expr:
        partes = expr.split("↔",1)
        izq = traducir(partes[0])
        der = traducir(partes[1])
        return eval(izq, {}, contexto) == eval(der, {}, contexto)
    else:
        return eval(traducir(expr), {}, contexto)

def generar_tabla(expr, variables):
    combinaciones = list(itertools.product([0,1], repeat=len(variables)))
    resultados = []
    for comb in combinaciones:
        contexto = {var: bool(val) for var, val in zip(variables, comb)}
        try:
            valor = evaluar(expr, contexto)
            resultados.append(int(valor))
        except:
            resultados.append("Error")
    df = pd.DataFrame(combinaciones, columns=variables)
    df[expr] = resultados
    return df

def clasificar(resultados):
    if all(r == 1 for r in resultados):
        return "Tautología"
    elif all(r == 0 for r in resultados):
        return "Contradicción"
    else:
        return "Contingencia"

# --- INTERFAZ ---
st.set_page_config(page_title="Calculadora Lógica", layout="centered")
st.title("Calculadora de Tablas de la Verdad")

if "expr" not in st.session_state:
    st.session_state.expr = ""

# Recuadro superior (vista intacta)
st.markdown(f"""
<div style="background-color:#111; color:#0f0; padding:15px; border-radius:10px; text-align:center; font-size:24px;">
{st.session_state.expr if st.session_state.expr else " "}
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Funciones para callbacks ---
def agregar_simbolo(simbolo):
    st.session_state.expr += simbolo

def borrar_expr():
    st.session_state.expr = ""

# Botones estilo calculadora (vista intacta, pero con callbacks)
botones = [
    ["p","q","r","a","b"],
    ["¬","∧","∨","→","↔"],
    ["(",")","Borrar"]
]

for fila in botones:
    cols = st.columns(len(fila))
    for i, b in enumerate(fila):
        if b == "Borrar":
            cols[i].button(b, use_container_width=True, on_click=borrar_expr)
        else:
            cols[i].button(b, use_container_width=True, on_click=agregar_simbolo, args=(b,))

# Botón calcular
if st.button("Calcular"):
    if st.session_state.expr:
        variables = sorted(set([c for c in st.session_state.expr if c in ["p","q","r","a","b"]]))
        df = generar_tabla(st.session_state.expr, variables)
        st.dataframe(df)

        st.subheader("Clasificación:")
        st.success(clasificar(df[st.session_state.expr].tolist()))

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descargar CSV", csv, "tabla_verdad.csv", "text/csv")
