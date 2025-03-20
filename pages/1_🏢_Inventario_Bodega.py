import streamlit as st
import sqlite3
import pandas as pd
import urllib.request
import os

# Ruta local donde se guardará la base de datos
DB_PATH = "ventas_producto.db"

# URL cruda del archivo en GitHub
GITHUB_DB_URL = "https://raw.githubusercontent.com/robertobasta/VentasMBW/main/data/ventas_producto.db"

def get_connection():
    # Si la base de datos no existe o es muy pequeña (puede estar dañada), la descarga
    if not os.path.exists(DB_PATH) or os.path.getsize(DB_PATH) < 10000:
        urllib.request.urlretrieve(GITHUB_DB_URL, DB_PATH)

    return sqlite3.connect(DB_PATH)

# Función para obtener datos de la base de datos
def obtener_datos(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Interfaz para mostrar el inventario en bodega con un diseño simple y claro
def main():
    st.title("🏬 Inventario en Bodega")
    query = "SELECT nombre_producto, cantidad_paquetes, piezas_por_paquete, cantidad_piezas FROM bodega"
    df = obtener_datos(query)
    
    if not df.empty:
        # Mostrar la tabla de forma sencilla y con el ancho completo
        st.dataframe(df.style.set_properties(**{
            'background-color': '#1E1E1E',
            'color': 'white',
            'border-color': 'white'
        }), use_container_width=True)
    else:
        st.warning("No hay productos en la bodega actualmente.")

if __name__ == "__main__":
    main()