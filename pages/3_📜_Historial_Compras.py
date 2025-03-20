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

# Función para obtener datos de la base de datos
def obtener_datos(query):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error al obtener los datos: {e}")
        return pd.DataFrame()

# Interfaz para mostrar el historial de compras
def main():
    st.title("📜 Historial de Compras de Producto")

    query = """
    SELECT 
        id,
        nombre_producto AS "Producto",
        cantidad AS "Cantidad (paquetes)",
        cantidad_piezas AS "Cantidad (piezas)",
        precio AS "Precio por pieza",
        precio_paquete AS "Precio por paquete",
        precio_venta AS "Precio de venta por pieza",
        fecha_compra AS "Fecha de compra",
        comentarios AS "Comentarios",
        proveedor AS "Proveedor",
        metodo_pago AS "Método de pago",
        precio_total_lote AS "Precio total del lote",
        ganancia_por_pieza AS "Ganancia por pieza",
        ganancia_por_paquete AS "Ganancia por paquete",
        precio_venta_total AS "Precio de venta total",
        ganancia_total AS "Ganancia total"
    FROM compras_de_producto
    """

    df = obtener_datos(query)

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No hay registros de compras de productos disponibles.")

if __name__ == "__main__":
    main()