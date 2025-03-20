import streamlit as st
import sqlite3
import pandas as pd
import os
import urllib.request

# Ruta local donde se guardará la base de datos
DB_PATH = "ventas_producto.db"

# URL cruda del archivo en GitHub
GITHUB_DB_URL = "https://raw.githubusercontent.com/robertobasta/VentasMBW/main/data/ventas_producto.db"

def get_connection():
    # Si la base de datos no existe o es muy pequeña (puede estar dañada), la descarga
    if not os.path.exists(DB_PATH) or os.path.getsize(DB_PATH) < 10000:
        urllib.request.urlretrieve(GITHUB_DB_URL, DB_PATH)

    return sqlite3.connect(DB_PATH)

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