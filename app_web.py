import streamlit as st
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Control de Filamentos 3D", page_icon="🧵", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)


URL_SCRIPT = "https://script.google.com/macros/s/AKfycbxrpvcw9yX10yZYF-kcRcVXs9rWk9MIHlsTd2BUV40McudgK0TjPFQmrGiwdiHJAXenpw/exec"

st.title("🧵 Control de Filamentos 3D")
st.caption("Inventario sincronizado en tiempo real")

# Formulario para agregar / actualizar
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
            "action": "save",
            "id": caja_id,
            "marca": marca,
            "material": material,
            "color": color,
            "gramos": gramos
        }
        try:
            res = requests.post(URL_SCRIPT, json=payload, allow_redirects=True)
            if res.status_code == 200:
                st.success(f"¡Rollo {caja_id} procesado correctamente!")
                st.cache_data.clear()
            else:
                st.error(f"Error {res.status_code}: {res.text}")
        except Exception as err:
            st.error(f"Error de conexión: {err}")

st.divider()

# Sección para eliminar rollos
with st.expander("🗑️ Eliminar un rollo del inventario"):
    id_eliminar = st.text_input("Ingresá el N° de Caja / ID a borrar")
    btn_borrar = st.button("❌ Eliminar rollo")
    
    if btn_borrar:
        if not id_eliminar:
            st.warning("Escribí el ID del rollo que querés borrar.")
        else:
            payload = {"action": "delete", "id": id_eliminar}
            try:
                res = requests.post(URL_SCRIPT, json=payload, allow_redirects=True)
                if res.status_code == 200:
                    st.success(f"¡Rollo {id_eliminar} eliminado de la planilla!")
                    st.cache_data.clear()
                else:
                    st.error(f"Error al eliminar: {res.text}")
            except Exception as err:
                st.error(f"Error de conexión: {err}")

st.divider()

# Mostrar inventario actual
st.subheader("📋 Inventario Actual")

if st.button("🔄 Actualizar tabla"):
    st.cache_data.clear()

try:
    df = conn.read(ttl=0)
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error(f"Error al leer la planilla: {e}")
