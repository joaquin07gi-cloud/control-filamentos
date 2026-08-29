import streamlit as st
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Control de Filamentos 3D", page_icon="🧵", layout="wide")

# Conexión solo para LEER los datos actualizados
conn = st.connection("gsheets", type=GSheetsConnection)

URL_SCRIPT = "https://script.google.com/macros/s/AKfycbxrpvcw9yX10yZYF-kcRcVXs9rWk9MIHlsTd2BUV4OMcudgK0TjPFQmrGiwdiHJAXenpw/exec"

st.title("🧵 Control de Filamentos 3D")
st.caption("Inventario sincronizado en tiempo real")

# Formulario para registrar/actualizar rollos
with st.form("form_filamento", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        caja_id = st.text_input("N° Caja / ID *")
        marca = st.text_input("Marca")
        material = st.selectbox("Material", ["PLA", "PETG", "ABS", "TPU", "ASA", "Otro"])
    with col2:
        color = st.text_input("Color")
        gramos = st.number_input("Gramos Restantes", min_value=0, max_value=2000, value=1000, step=50)
    
    btn_guardar = st.form_submit_button("💾 Guardar / Actualizar")

if btn_guardar:
    if not caja_id:
        st.error("Por favor completa el N° de Caja / ID.")
    else:
        payload = {
            "id": caja_id,
            "marca": marca,
            "material": material,
            "color": color,
            "gramos": gramos
        }
        try:
            res = requests.post(URL_SCRIPT, json=payload, allow_redirects=True)
            if res.status_code == 200:
                st.success(f"¡Rollo {caja_id} guardado correctamente en la planilla!")
                st.cache_data.clear()
            else:
                st.error(f"Error {res.status_code}: {res.text}")
        except Exception as err:
            st.error(f"Error de conexión: {err}")

st.divider()

# Mostrar inventario actual
st.subheader("📋 Inventario Actual")
try:
    df = conn.read(ttl="5s")
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.info("Cargá tu primer rollo arriba para ver el inventario.")
