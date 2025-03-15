import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/venta de producto/data/ventas_producto.db"

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