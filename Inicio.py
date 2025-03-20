import streamlit as st
import sqlite3
import pandas as pd
import os
import urllib.request

# Configuración de la página
st.set_page_config(page_title="Inicio - Venta de Productos", layout="wide")

# Ruta local donde se guardará la base de datos
DB_PATH = "ventas_producto.db"

# URL cruda del archivo en GitHub
GITHUB_DB_URL = "https://raw.githubusercontent.com/robertobasta/VentasMBW/main/data/ventas_producto.db"

def get_connection():
    # Si la base de datos no existe o es muy pequeña (puede estar dañada), la descarga
    if not os.path.exists(DB_PATH) or os.path.getsize(DB_PATH) < 10000:
        urllib.request.urlretrieve(GITHUB_DB_URL, DB_PATH)

    return sqlite3.connect(DB_PATH)

# 🔹 **DEBUG: Verificar qué base de datos está usando Streamlit Cloud**
st.write(f"📍 Ruta de la base de datos en Streamlit: `{os.path.abspath(DB_PATH)}`")
if os.path.exists(DB_PATH):
    st.write(f"✅ La base de datos existe en Streamlit. Tamaño: `{os.path.getsize(DB_PATH)} bytes`")
else:
    st.write("⚠️ La base de datos NO existe en Streamlit. Se usará una nueva o vacía.")

# Obtener opciones de vendedores y turnos
def get_vendors_and_shifts():
    conn = get_connection()
    vendors = pd.read_sql("SELECT DISTINCT vendedor FROM ventas", conn)["vendedor"].dropna().tolist()
    shifts = pd.read_sql("SELECT DISTINCT turno FROM ventas", conn)["turno"].dropna().tolist()
    conn.close()
    return vendors, shifts

# Obtener resumen de ventas del día con filtros
def get_sales_summary(date, vendedor, turno):
    conn = get_connection()
    query = """
    SELECT SUM(total) AS total_ventas FROM ventas WHERE fecha = ?
    """
    params = [date]
    if vendedor:
        query += " AND vendedor = ?"
        params.append(vendedor)
    if turno:
        query += " AND turno = ?"
        params.append(turno)
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df.iloc[0]['total_ventas'] if not df.empty and df.iloc[0]['total_ventas'] else 0

# Obtener ingresos por método de pago con filtros
def get_payment_summary(date, vendedor, turno):
    conn = get_connection()
    query = """
    SELECT metodo_pago, SUM(total) AS total FROM ventas WHERE fecha = ?
    """
    params = [date]
    if vendedor:
        query += " AND vendedor = ?"
        params.append(vendedor)
    if turno:
        query += " AND turno = ?"
        params.append(turno)
    query += " GROUP BY metodo_pago"
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# Obtener los productos más vendidos con filtros
def get_top_products(date, vendedor, turno):
    conn = get_connection()
    query = """
    SELECT nombre_producto, SUM(cantidad_vendida) AS cantidad FROM ventas WHERE fecha = ?
    """
    params = [date]
    if vendedor:
        query += " AND vendedor = ?"
        params.append(vendedor)
    if turno:
        query += " AND turno = ?"
        params.append(turno)
    query += " GROUP BY nombre_producto ORDER BY cantidad DESC LIMIT 5"
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# Obtener el stock en refrigerador
def get_refrigerator_stock():
    conn = get_connection()
    query = "SELECT nombre_producto, cantidad FROM refri"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Estilo CSS personalizado
st.markdown(
    """
    <style>
        .title { text-align: center; font-size: 40px; font-weight: bold; }
        .metric-box { padding: 20px; border-radius: 10px; background-color: #1E1E1E; text-align: center; }
    </style>
    """, unsafe_allow_html=True
)

st.markdown("<p class='title'>🏪 Dashboard de Venta de Productos</p>", unsafe_allow_html=True)

# Selector de fecha
date_selected = st.date_input("📅 Selecciona una fecha", pd.Timestamp.today())
date_selected = date_selected.strftime("%Y-%m-%d")

# Filtros de vendedor y turno
vendors, shifts = get_vendors_and_shifts()
vendedor_selected = st.selectbox("🧑‍💼 Selecciona un Vendedor", ["Todos"] + vendors)
turno_selected = st.selectbox("⏳ Selecciona un Turno", ["Todos"] + shifts)

if vendedor_selected == "Todos":
    vendedor_selected = None
if turno_selected == "Todos":
    turno_selected = None

# Mostrar métricas principales
col1, col2, col3 = st.columns(3)

total_ventas = get_sales_summary(date_selected, vendedor_selected, turno_selected)
col1.metric("💰 Total Ventas del Día", f"$ {total_ventas:.2f}")

df_payment = get_payment_summary(date_selected, vendedor_selected, turno_selected)
col2.write("**💳 Ingresos por Método de Pago**")
col2.dataframe(df_payment, hide_index=True)

df_top_products = get_top_products(date_selected, vendedor_selected, turno_selected)
col3.write("**🔥 Productos Más Vendidos**")
col3.dataframe(df_top_products, hide_index=True)

st.markdown("---")

# Sección con accesos rápidos
st.subheader("📌 Accesos Rápidos")
col4, col5 = st.columns(2)

with col4:
    st.write("### 🛒 Registrar una Venta")
    if st.button("📌 Ir a Registrar Venta"):
        os.system(f"streamlit run '/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/Venta de Producto/pages/registrar_venta.py'")

with col5:
    st.write("### 🧊 Stock en Refrigerador")
    df_refrigerator = get_refrigerator_stock()
    st.dataframe(df_refrigerator, hide_index=True)

st.markdown("---")
st.write("Desarrollado por MBW 🚀")