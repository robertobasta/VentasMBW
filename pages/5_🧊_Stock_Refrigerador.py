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

# Función para obtener los productos en el refri, sin unificar nombres
def get_refri_data():
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT 
            nombre_producto, 
            SUM(cantidad) AS cantidad 
        FROM refri 
        GROUP BY nombre_producto
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Función para obtener los productos disponibles en la bodega
def get_bodega_data():
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT 
            nombre_producto, 
            cantidad_paquetes AS cantidad, 
            piezas_por_paquete AS cantidad_piezas 
        FROM bodega 
        WHERE cantidad_paquetes > 0
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Función para mover productos entre bodega y refri sin modificar el nombre del producto
def move_to_refri(nombre_producto, paquetes_a_mover, operacion="Agregar"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Obtener la cantidad de piezas por paquete desde la tabla bodega
    cursor.execute("SELECT piezas_por_paquete FROM bodega WHERE nombre_producto = ?", (nombre_producto,))
    piezas_por_paquete = cursor.fetchone()[0]
    
    # Calcular cuántas piezas se deben mover
    piezas_a_mover = paquetes_a_mover * piezas_por_paquete
    
    if operacion == "Agregar":
        # Restar los paquetes y las piezas de la bodega
        cursor.execute(
            """
            UPDATE bodega 
            SET cantidad_paquetes = cantidad_paquetes - ?, 
                cantidad_piezas = cantidad_piezas - ?
            WHERE nombre_producto = ?
            """,
            (paquetes_a_mover, piezas_a_mover, nombre_producto)
        )
        
        # Sumar las piezas al refri sin modificar el nombre del producto
        cursor.execute(
            """
            INSERT INTO refri (nombre_producto, cantidad) 
            VALUES (?, ?) 
            ON CONFLICT(nombre_producto) 
            DO UPDATE SET cantidad = cantidad + ?
            """,
            (nombre_producto, piezas_a_mover, piezas_a_mover)
        )
    
    elif operacion == "Quitar":
        # Sumar los paquetes y las piezas de vuelta a la bodega
        cursor.execute(
            """
            UPDATE bodega 
            SET cantidad_paquetes = cantidad_paquetes + ?, 
                cantidad_piezas = cantidad_piezas + ?
            WHERE nombre_producto = ?
            """,
            (paquetes_a_mover, piezas_a_mover, nombre_producto)
        )
        
        # Restar las piezas del refri, sin permitir cantidades negativas
        cursor.execute(
            """
            UPDATE refri 
            SET cantidad = MAX(cantidad - ?, 0)
            WHERE nombre_producto = ?
            """,
            (piezas_a_mover, nombre_producto)
        )
    
    conn.commit()
    conn.close()

# Función para mostrar la tabla de productos en el refri
def display_refri():
    refri_data = get_refri_data()
    st.dataframe(refri_data, use_container_width=True)

# Función para el formulario de mover productos al refri
def move_product_form():
    st.header("Mover Productos al Refri")
    bodega_data = get_bodega_data()
    
    if not bodega_data.empty:
        producto = st.selectbox("Producto en Bodega", bodega_data['nombre_producto'].unique())
        max_paquetes = bodega_data.loc[bodega_data['nombre_producto'] == producto, 'cantidad'].values[0]
        
        operacion = st.radio("Operación", ["Agregar", "Quitar"], horizontal=True)
        
        paquetes_a_mover = st.number_input(
            f"Paquetes a {operacion.lower()} (máximo {max_paquetes})", 
            min_value=1, 
            max_value=int(max_paquetes), 
            step=1
        )
        
        if st.button(f"{operacion} al Refri"):
            move_to_refri(producto, paquetes_a_mover, operacion)
            st.success(f"Se {operacion.lower()}on {paquetes_a_mover} paquetes de {producto} al refri.")
    else:
        st.warning("No hay productos disponibles en la bodega para mover al refri.")

# Interfaz de la subpágina Refri
st.title("Refri - Control de Stock")

st.subheader("Productos en el Refri")
display_refri()

st.subheader("Mover Productos al Refri")
move_product_form()
