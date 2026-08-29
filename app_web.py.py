import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de página para que se vea bien en celular
st.set_page_config(page_title="Control Filamentos 3D", page_icon="🧵", layout="centered")

st.title("🧵 Control de Filamentos 3D")
st.write("Inventario sincronizado en tiempo real")

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Cargar datos existentes
def cargar_inventario():
    return conn.read(ttl="0d")

try:
    df = cargar_inventario()
except Exception:
    df = pd.DataFrame(columns=["ID", "Marca", "Material", "Color", "Gramos"])

# --- FORMULARIO DE REGISTRO / ACTUALIZACIÓN ---
with st.form(key="form_filamento", clear_on_submit=True):
    st.subheader("Registrar o Actualizar Rollo")
    
    col1, col2 = st.columns(2)
    with col1:
        caja_id = st.text_input("N° Caja / ID *")
        marca = st.text_input("Marca")
        material = st.selectbox("Material", ["PLA", "PETG", "ABS", "TPU", "ASA", "PCTG", "Otro"])
    
    with col2:
        color = st.text_input("Color")
        gramos = st.number_input("Gramos Restantes", min_value=0, max_value=5000, value=1000, step=10)

    btn_guardar = st.form_submit_button("💾 Guardar / Actualizar")

if btn_guardar:
    if not caja_id:
        st.error("El N° de Caja / ID es obligatorio.")
    else:
        # Convertir ID a string para evitar conflictos de tipo
        caja_id = str(caja_id).strip()
        
        # Filtrar si ya existe el ID para actualizarlo
        df_edit = df[df["ID"].astype(str) != caja_id]
        
        nuevo_registro = pd.DataFrame([{
            "ID": caja_id,
            "Marca": marca,
            "Material": material,
            "Color": color,
            "Gramos": gramos
        }])
        
        df_actualizado = pd.concat([df_edit, nuevo_registro], ignore_index=True)
        
        # Actualizar en Google Sheets
        conn.update(data=df_actualizado)
        st.success(f"¡Rollo ID {caja_id} guardado correctamente!")
        st.rerun()

st.divider()

# --- TABLA Y DESCUENTO RÁPIDO DE GRAMOS ---
st.subheader("📦 Inventario Actual")

if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Sección para descontar gramos tras imprimir
    st.subheader("📉 Descontar Impresión")
    
    col_sel, col_desc, col_btn = st.columns([2, 2, 1])
    
    with col_sel:
        rollo_seleccionado = st.selectbox("Seleccionar Rollo ID", df["ID"].astype(str).tolist())
    
    with col_desc:
        gramos_usados = st.number_input("Gramos consumidos", min_value=1, max_value=1000, value=20)
        
    with col_btn:
        st.write("") # Espaciador
        if st.button("Restar"):
            idx = df[df["ID"].astype(str) == rollo_seleccionado].index
            if not idx.empty:
                gramos_actuales = int(df.loc[idx[0], "Gramos"])
                nuevos_gramos = max(0, gramos_actuales - gramos_usados)
                df.loc[idx[0], "Gramos"] = nuevos_gramos
                
                conn.update(data=df)
                st.success(f"Quedan {nuevos_gramos}g en el rollo {rollo_seleccionado}")
                st.rerun()
else:
    st.info("No hay rollos registrados en la base de datos.")