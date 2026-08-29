import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Control de Filamentos 3D", page_icon="🧵", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🧵 Control de Filamentos 3D")
st.caption("Inventario sincronizado en tiempo real")

# Formulario para agregar / actualizar rollos
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
        try:
            df_actual = conn.read(ttl=0)
            
            # Convertir IDs a texto para comparar bien
            caja_id_str = str(caja_id).strip()
            df_actual['ID'] = df_actual['ID'].astype(str).str.strip()
            
            # Si el ID ya existe, lo actualiza. Si no existe, crea la fila nueva
            if caja_id_str in df_actual['ID'].values:
                idx = df_actual[df_actual['ID'] == caja_id_str].index[0]
                df_actual.loc[idx, ['Marca', 'Material', 'Color', 'Gramos']] = [marca, material, color, gramos]
            else:
                nueva_fila = pd.DataFrame([{
                    "ID": caja_id_str,
                    "Marca": marca,
                    "Material": material,
                    "Color": color,
                    "Gramos": gramos
                }])
                df_actual = pd.concat([df_actual, nueva_fila], ignore_index=True)
            
            # Escribir la planilla actualizada
            conn.update(data=df_actual)
            st.success(f"¡Rollo {caja_id} guardado correctamente!")
            st.cache_data.clear()
        except Exception as err:
            st.error(f"Error al guardar: {err}")

st.divider()

# Sección para borrar rollos
with st.expander("🗑️ Eliminar un rollo del inventario"):
    id_eliminar = st.text_input("Ingresá el N° de Caja / ID a borrar")
    btn_borrar = st.button("❌ Eliminar rollo")
    
    if btn_borrar:
        if not id_eliminar:
            st.warning("Escribí el ID del rollo que querés borrar.")
        else:
            try:
                df_actual = conn.read(ttl=0)
                id_del_str = str(id_eliminar).strip()
                df_actual['ID'] = df_actual['ID'].astype(str).str.strip()
                
                if id_del_str in df_actual['ID'].values:
                    df_nuevo = df_actual[df_actual['ID'] != id_del_str]
                    conn.update(data=df_nuevo)
                    st.success(f"¡Rollo {id_eliminar} eliminado correctamente!")
                    st.cache_data.clear()
                else:
                    st.warning(f"No se encontró el rollo con ID: {id_eliminar}")
            except Exception as err:
                st.error(f"Error al eliminar: {err}")

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
