import streamlit as st
import sqlite3
from datetime import datetime
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

# Función para agregar un nuevo producto
def agregar_producto(nombre_producto):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO productos (producto) VALUES (?)", (nombre_producto,))
        conn.commit()
        conn.close()
        st.success(f"Producto '{nombre_producto}' agregado correctamente.")
    except Exception as e:
        st.error(f"Error al agregar el producto: {e}")

# Función para eliminar un producto
def eliminar_producto(nombre_producto):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE producto = ?", (nombre_producto,))
        conn.commit()
        conn.close()
        st.success(f"Producto '{nombre_producto}' eliminado correctamente.")
    except Exception as e:
        st.error(f"Error al eliminar el producto: {e}")

# Función para agregar un nuevo proveedor
def agregar_proveedor(nombre_proveedor):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO proveedores (proveedor) VALUES (?)", (nombre_proveedor,))
        conn.commit()
        conn.close()
        st.success(f"Proveedor '{nombre_proveedor}' agregado correctamente.")
    except Exception as e:
        st.error(f"Error al agregar el proveedor: {e}")

# Función para eliminar un proveedor
def eliminar_proveedor(nombre_proveedor):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM proveedores WHERE proveedor = ?", (nombre_proveedor,))
        conn.commit()
        conn.close()
        st.success(f"Proveedor '{nombre_proveedor}' eliminado correctamente.")
    except Exception as e:
        st.error(f"Error al eliminar el proveedor: {e}")

# Función para registrar la compra en la base de datos
def registrar_compra(nombre_producto, cantidad, cantidad_piezas, precio_por_pieza, precio_por_paquete, precio_venta, fecha_compra, comentarios, proveedor, metodo_pago, precio_total_lote, ganancia_por_pieza, ganancia_por_paquete, precio_venta_total, ganancia_total):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO compras_de_producto (nombre_producto, cantidad, cantidad_piezas, precio, precio_paquete, precio_venta, fecha_compra, comentarios, proveedor, metodo_pago, precio_total_lote, ganancia_por_pieza, ganancia_por_paquete, precio_venta_total, ganancia_total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (nombre_producto, cantidad, cantidad_piezas, precio_por_pieza, precio_por_paquete, precio_venta, fecha_compra, comentarios, proveedor, metodo_pago, precio_total_lote, ganancia_por_pieza, ganancia_por_paquete, precio_venta_total, ganancia_total)
        )
        conn.commit()
        conn.close()
        st.success("✅ Compra registrada correctamente y la bodega actualizada")
    except Exception as e:
        st.error(f"Error al registrar la compra: {e}")

# Función para actualizar la bodega
def actualizar_bodega(nombre_producto, cantidad_paquetes, piezas_por_paquete):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"Intentando actualizar bodega con: {nombre_producto}, {cantidad_paquetes} paquetes, {piezas_por_paquete} piezas/paquete")
    
    cursor.execute("SELECT cantidad_paquetes, cantidad_piezas FROM bodega WHERE nombre_producto = ?", (nombre_producto,))
    resultado = cursor.fetchone()
    
    if resultado:
        cantidad_paquetes_actual, cantidad_piezas_actual = resultado
        nueva_cantidad_paquetes = cantidad_paquetes_actual + cantidad_paquetes
        nueva_cantidad_piezas = nueva_cantidad_paquetes * piezas_por_paquete
        
        cursor.execute("""
            UPDATE bodega
            SET cantidad_paquetes = ?, piezas_por_paquete = ?, cantidad_piezas = ?
            WHERE nombre_producto = ?
        """, (nueva_cantidad_paquetes, piezas_por_paquete, nueva_cantidad_piezas, nombre_producto))
        
        print(f"Producto actualizado en bodega: {nombre_producto}")
    
    else:
        cantidad_piezas = cantidad_paquetes * piezas_por_paquete
        cursor.execute("""
            INSERT INTO bodega (nombre_producto, cantidad_paquetes, piezas_por_paquete, cantidad_piezas)
            VALUES (?, ?, ?, ?)
        """, (nombre_producto, cantidad_paquetes, piezas_por_paquete, cantidad_piezas))
        
        print(f"Producto agregado a bodega: {nombre_producto}")
    
    conn.commit()
    conn.close()

# Interfaz para registrar compra de producto
def main():
    st.title("📝 Registrar Compra de Producto")
    
    productos_df = obtener_datos("SELECT producto FROM productos")
    proveedores_df = obtener_datos("SELECT proveedor FROM proveedores")
    
    nombre_producto = st.selectbox("Producto", ["Selecciona un producto"] + productos_df['producto'].tolist() if not productos_df.empty else [])
    proveedor = st.selectbox("Proveedor", ["Selecciona un proveedor"] + proveedores_df['proveedor'].tolist() if not proveedores_df.empty else [])
    
    cantidad = st.number_input("Cantidad (en paquetes)", min_value=1, step=1)
    piezas_por_paquete = st.number_input("Piezas por paquete", min_value=1, step=1)
    precio_total_lote = st.number_input("Precio Total del Lote", min_value=0.0, step=0.01)
    precio_venta = st.number_input("Precio de Venta por pieza", min_value=0.0, step=0.01)
    fecha_compra = st.date_input("Fecha de Compra")
    comentarios = st.text_input("Comentarios adicionales")
    metodo_pago = st.selectbox("Método de Pago", ["Efectivo", "Tarjeta", "Transferencia"])

    cantidad_piezas = cantidad * piezas_por_paquete
    precio_por_pieza = precio_total_lote / cantidad_piezas if cantidad_piezas > 0 else 0
    precio_por_paquete = precio_total_lote / cantidad if cantidad > 0 else 0

    ganancia_por_pieza = precio_venta - precio_por_pieza
    ganancia_por_paquete = ganancia_por_pieza * piezas_por_paquete
    precio_venta_total = precio_venta * cantidad_piezas
    ganancia_total = precio_venta_total - precio_total_lote

    st.write(f"📦 Precio por pieza: ${precio_por_pieza:.2f}")
    st.write(f"🛍️ Precio por paquete: ${precio_por_paquete:.2f}")
    st.write(f"💰 Ganancia por pieza: ${ganancia_por_pieza:.2f}")
    st.write(f"📦 Ganancia por paquete: ${ganancia_por_paquete:.2f}")
    st.write(f"🛒 Precio de venta total: ${precio_venta_total:.2f}")
    st.write(f"🏆 Ganancia total: ${ganancia_total:.2f}")

    if st.button("Registrar Compra") and nombre_producto != "Selecciona un producto" and proveedor != "Selecciona un proveedor":
        registrar_compra(
            nombre_producto, cantidad, cantidad_piezas, precio_por_pieza, precio_por_paquete, precio_venta, fecha_compra.strftime('%Y-%m-%d'), 
            comentarios, proveedor, metodo_pago, precio_total_lote, ganancia_por_pieza, ganancia_por_paquete, precio_venta_total, ganancia_total
        )
        actualizar_bodega(nombre_producto, cantidad, piezas_por_paquete)

if __name__ == "__main__":
    main()