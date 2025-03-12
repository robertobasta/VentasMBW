import streamlit as st
import sqlite3
import pandas as pd

# Conectar a la base de datos
def get_connection():
    return sqlite3.connect("/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/venta de producto/data/ventas_producto.db")

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
