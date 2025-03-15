import streamlit as st
import sqlite3
import pandas as pd

# Ruta de la base de datos
DB_PATH = "/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/venta de producto/data/ventas_producto.db"

st.title("📊 Historial de Ventas")

def cargar_historial_ventas():
    # Conectar a la base de datos y cargar la tabla de ventas
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM ventas"
    df_ventas = pd.read_sql(query, conn)
    conn.close()
    return df_ventas

# Cargar el historial de ventas
df_ventas = cargar_historial_ventas()

# Mostrar el historial de ventas en la interfaz
if not df_ventas.empty:
    st.dataframe(df_ventas, use_container_width=True)
else:
    st.warning("No hay registros de ventas disponibles.")