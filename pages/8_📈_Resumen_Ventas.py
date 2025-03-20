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


# Obtener datos de ventas por producto
def get_sales_by_product(date):
    conn = get_connection()
    query = """
    SELECT nombre_producto, SUM(cantidad_vendida) AS total_vendido, SUM(total) AS total_dinero
    FROM ventas
    WHERE fecha = ? 
    GROUP BY nombre_producto;
    """
    df = pd.read_sql(query, conn, params=(date,))
    conn.close()
    return df

# Obtener total de dinero por método de pago
def get_sales_by_payment_method(date):
    conn = get_connection()
    query = """
    SELECT metodo_pago, SUM(total) AS total_dinero
    FROM ventas
    WHERE fecha = ? 
    GROUP BY metodo_pago;
    """
    df = pd.read_sql(query, conn, params=(date,))
    conn.close()
    return df

# Obtener total de ventas por turno
def get_sales_by_shift(date):
    conn = get_connection()
    query = """
    SELECT turno, SUM(total) AS total_dinero
    FROM ventas
    WHERE fecha = ?
    GROUP BY turno;
    """
    df = pd.read_sql(query, conn, params=(date,))
    conn.close()
    return df

# Obtener total de ventas por vendedor
def get_sales_by_seller(date):
    conn = get_connection()
    query = """
    SELECT vendedor, SUM(total) AS total_dinero
    FROM ventas
    WHERE fecha = ?
    GROUP BY vendedor;
    """
    df = pd.read_sql(query, conn, params=(date,))
    conn.close()
    return df

# Streamlit UI
st.title("📊 Resumen de Ventas")

# Selector de fecha
date_selected = st.date_input("Selecciona una fecha", pd.Timestamp.today())
date_selected = date_selected.strftime("%Y-%m-%d")

# Mostrar ventas por producto
st.subheader("Ventas por Producto")
df_products = get_sales_by_product(date_selected)
st.dataframe(df_products)

# Mostrar total de dinero por método de pago
st.subheader("Total por Método de Pago")
df_payment = get_sales_by_payment_method(date_selected)
st.dataframe(df_payment)

# Mostrar total de ventas por turno
st.subheader("Ventas por Turno")
df_shift = get_sales_by_shift(date_selected)
st.dataframe(df_shift)

# Mostrar total de ventas por vendedor
st.subheader("Ventas por Vendedor")
df_seller = get_sales_by_seller(date_selected)
st.dataframe(df_seller)
