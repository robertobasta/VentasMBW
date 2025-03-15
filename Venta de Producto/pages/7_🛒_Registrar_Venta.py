import streamlit as st
import sqlite3
from datetime import datetime

DB_PATH = "/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/venta de producto/data/ventas_producto.db"

# Función para obtener los productos disponibles en el refri junto con la cantidad disponible
def obtener_productos_disponibles():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre_producto, cantidad FROM refri WHERE cantidad > 0")
    productos = cursor.fetchall()
    conn.close()
    return productos

# Función para obtener el precio de venta de un producto
def obtener_precio_venta(nombre_producto):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT precio_venta 
        FROM compras_de_producto 
        WHERE nombre_producto LIKE ? 
        ORDER BY fecha_compra DESC LIMIT 1
    """, (f"{nombre_producto}%",))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else 0.0

# Función para obtener las opciones de Turno desde la tabla Turnos
def obtener_turnos_disponibles():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT Turnos FROM Turnos")
    turnos = [row[0] for row in cursor.fetchall()]
    conn.close()
    return turnos

# Función para obtener las opciones de Vendedor desde la tabla Vendedor
def obtener_vendedores_disponibles():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT Vendedor FROM Vendedor")
    vendedores = [row[0] for row in cursor.fetchall()]
    conn.close()
    return vendedores

# Función para agregar producto al carrito temporal con turno y vendedor
def agregar_al_carrito(nombre_producto, piezas, metodo_pago, precio_venta, turno, vendedor):
    subtotal = piezas * precio_venta
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO carrito_temporal 
        (nombre_producto, cantidad, metodo_pago, precio_venta, subtotal, turno, vendedor) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nombre_producto, piezas, metodo_pago, precio_venta, subtotal, turno, vendedor))
    conn.commit()
    conn.close()
    st.success(f"🛒 Producto '{nombre_producto}' agregado al carrito con método de pago '{metodo_pago}'")

# Función para mostrar el contenido del carrito temporal
def mostrar_carrito_temporal():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nombre_producto, cantidad, metodo_pago, precio_venta, subtotal, turno, vendedor 
        FROM carrito_temporal
    """)
    carrito = cursor.fetchall()
    conn.close()
    return carrito

# Función para eliminar un producto del carrito
def eliminar_del_carrito(id_producto):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM carrito_temporal WHERE id = ?", (id_producto,))
    conn.commit()
    conn.close()
    st.success("🗑️ Producto eliminado del carrito")

# Función para registrar la venta de productos del carrito temporal y actualizar el refri
def registrar_venta(cambio):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    fecha = datetime.now().strftime('%Y-%m-%d')

    # Obtener productos del carrito temporal
    cursor.execute("""
        SELECT nombre_producto, cantidad, metodo_pago, subtotal, turno, vendedor, precio_venta 
        FROM carrito_temporal
    """)
    carrito = cursor.fetchall()

    for item in carrito:
        # Registrar la venta en la tabla de ventas
        cursor.execute("""
            INSERT INTO ventas 
            (nombre_producto, cantidad_vendida, metodo_pago, fecha, total, turno, vendedor, precio_unitario, subtotal, cambio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (item[0], item[1], item[2], fecha, item[3], item[4], item[5], item[6], item[3], cambio))

        # Actualizar la tabla refri restando la cantidad vendida
        cursor.execute("""
            UPDATE refri 
            SET cantidad = MAX(cantidad - ?, 0) 
            WHERE nombre_producto = ?
        """, (item[1], item[0]))

    # Vaciar el carrito temporal
    cursor.execute("DELETE FROM carrito_temporal")

    conn.commit()
    conn.close()
    st.success("✅ Venta registrada correctamente")

# Interfaz para registrar venta de producto
def main():
    st.title("🛍️ Registrar Venta de Producto")

    productos_disponibles = obtener_productos_disponibles()
    if not productos_disponibles:
        st.warning("No hay productos disponibles en el refri")
        return

    # Mostrar el producto disponible y la cantidad máxima que se puede vender
    producto_seleccionado = st.selectbox(
        "Nombre del Producto", 
        [f"{p[0]} (Disponibles: {p[1]})" for p in productos_disponibles]
    )
    
    nombre_producto, max_piezas = producto_seleccionado.split(" (Disponibles: ")
    max_piezas = int(max_piezas.replace(")", ""))

    precio_venta = obtener_precio_venta(nombre_producto)
    st.write(f"💲 Precio Unitario: ${precio_venta:.2f}")

    # Limitar el input de piezas vendidas a la cantidad disponible
    piezas = st.number_input(
        "Cantidad de Piezas Vendidas", 
        min_value=1, 
        max_value=max_piezas, 
        step=1
    )
    
    metodo_pago = st.selectbox("Método de Pago", ["Efectivo", "Tarjeta", "Transferencia"], key="metodo_pago")

    turnos_disponibles = obtener_turnos_disponibles()
    turno = st.selectbox("Turno", turnos_disponibles, key="turno")

    vendedores_disponibles = obtener_vendedores_disponibles()
    vendedor = st.selectbox("Vendedor", vendedores_disponibles, key="vendedor")

    subtotal = precio_venta * piezas
    st.write(f"🧮 Subtotal: ${subtotal:.2f}")

    if st.button("Agregar al Carrito"):
        if piezas <= max_piezas:
            agregar_al_carrito(nombre_producto, piezas, metodo_pago, precio_venta, turno, vendedor)
        else:
            st.error(f"No puedes vender más de {max_piezas} piezas")

    carrito = mostrar_carrito_temporal()
    if carrito:
        st.subheader("🛒 Resumen de Compra")
        total_general = 0
        for item in carrito:
            st.write(f"📦 {item[1]} - {item[2]} piezas x ${item[4]:.2f} = ${item[5]:.2f}")
            total_general += item[5]
            if st.button(f"Eliminar {item[1]}", key=f"eliminar_{item[0]}"):
                eliminar_del_carrito(item[0])
        st.write(f"💰 **Total a Pagar: ${total_general:.2f}**")

        efectivo_recibido = st.number_input("💵 Dinero Recibido", min_value=0.0, step=1.0)
        if efectivo_recibido >= total_general:
            cambio = efectivo_recibido - total_general
            st.success(f"💸 Cambio a Devolver: ${cambio:.2f}")
        else:
            st.warning("El monto recibido es insuficiente.")

        if st.button("Registrar Venta"):
            if carrito:
                registrar_venta(cambio)
            else:
                st.warning("El carrito está vacío")

if __name__ == "__main__":
    main()