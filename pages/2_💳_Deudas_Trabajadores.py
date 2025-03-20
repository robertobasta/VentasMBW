import streamlit as st
import sqlite3
from datetime import date
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

# Conectar a la base de datos
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

# Crear tablas necesarias
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    # Tabla de trabajadores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trabajadores (
        id INTEGER PRIMARY KEY,
        nombre TEXT UNIQUE
    )
    ''')
    # Tabla de deudas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS deudas (
        id INTEGER PRIMARY KEY,
        nombre_trabajador TEXT,
        nombre_producto TEXT,
        cantidad INTEGER,
        total REAL,
        fecha DATE,
        estado TEXT DEFAULT 'Pendiente',
        FOREIGN KEY (nombre_trabajador) REFERENCES trabajadores(nombre)
    )
    ''')
    conn.commit()
    conn.close()

# Registrar una nueva deuda y actualizar el inventario del refri
def registrar_deuda(nombre_trabajador, nombre_producto, cantidad, total):
    conn = get_connection()
    cursor = conn.cursor()
    fecha_actual = date.today().strftime('%Y-%m-%d')
    # Registrar la deuda
    cursor.execute('''
    INSERT INTO deudas (nombre_trabajador, nombre_producto, cantidad, total, fecha, estado)
    VALUES (?, ?, ?, ?, ?, 'Pendiente')
    ''', (nombre_trabajador, nombre_producto, cantidad, total, fecha_actual))
    # Actualizar el inventario del refri
    cursor.execute('''
    UPDATE refri SET cantidad = cantidad - ? WHERE nombre_producto = ?
    ''', (cantidad, nombre_producto))
    conn.commit()
    conn.close()

# Eliminar deuda y devolver productos al refri
def eliminar_deuda(deuda_id, nombre_producto, cantidad):
    conn = get_connection()
    cursor = conn.cursor()
    # Eliminar la deuda
    cursor.execute('''
    DELETE FROM deudas WHERE id = ?
    ''', (deuda_id,))
    # Devolver los productos al refri
    cursor.execute('''
    UPDATE refri SET cantidad = cantidad + ? WHERE nombre_producto = ?
    ''', (cantidad, nombre_producto))
    conn.commit()
    conn.close()

# Mostrar deudas pendientes
def obtener_deudas_pendientes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, nombre_trabajador, nombre_producto, cantidad, total, fecha, estado
    FROM deudas
    WHERE estado = 'Pendiente'
    ''')
    deudas = cursor.fetchall()
    conn.close()
    return deudas

# Obtener lista de trabajadores
def obtener_trabajadores():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT nombre FROM trabajadores')
    trabajadores = [row[0] for row in cursor.fetchall()]
    conn.close()
    return trabajadores

# Agregar nuevo trabajador a la base de datos
def agregar_trabajador(nombre_trabajador):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO trabajadores (nombre) VALUES (?)', (nombre_trabajador,))
        conn.commit()
    except sqlite3.IntegrityError:
        st.warning('El trabajador ya existe en la base de datos')
    conn.close()

# Eliminar trabajador de la base de datos
def eliminar_trabajador(nombre_trabajador):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM trabajadores WHERE nombre = ?', (nombre_trabajador,))
    conn.commit()
    conn.close()

# Obtener productos disponibles en el refrigerador con lógica para el precio de venta
def obtener_productos_refri_y_precio():
    conn = get_connection()
    cursor = conn.cursor()
    # Obtener productos del refri
    cursor.execute('''
    SELECT nombre_producto, cantidad FROM refri WHERE cantidad > 0
    ''')
    productos_refri = cursor.fetchall()

    # Obtener precios únicos desde compras_de_producto
    precios = {}
    for producto, _ in productos_refri:
        cursor.execute('''
        SELECT precio_venta FROM compras_de_producto 
        WHERE nombre_producto LIKE ?
        LIMIT 1
        ''', (f'%{producto}%',))
        resultado = cursor.fetchone()
        if resultado:
            precios[producto] = resultado[0]

    conn.close()
    # Combinar disponibilidad con precios
    productos_con_precios = [(producto, cantidad, precios.get(producto, 0)) for producto, cantidad in productos_refri]
    return productos_con_precios

# Interfaz en Streamlit
st.title('Gestión de Deudas')
create_tables()

# Registrar una nueva deuda
st.header('Registrar Nueva Deuda')
trabajadores = obtener_trabajadores()
trabajador = st.selectbox('Nombre del trabajador o pendiente', trabajadores + ['Agregar nuevo trabajador...'])

if trabajador == 'Agregar nuevo trabajador...':
    nuevo_trabajador = st.text_input('Ingrese el nombre del nuevo trabajador')
    if st.button('Agregar Trabajador') and nuevo_trabajador:
        agregar_trabajador(nuevo_trabajador)
        st.success('Trabajador agregado exitosamente')

# Selección de productos disponibles en el refri
productos_refri = obtener_productos_refri_y_precio()
if productos_refri:
    producto_seleccionado = st.selectbox(
        'Producto tomado',
        [f'{producto[0]} (Disponibles: {producto[1]}, Precio: ${producto[2]:.2f})' for producto in productos_refri]
    )
    producto, detalles = producto_seleccionado.split(' (Disponibles: ')
    disponibilidad, precio_unitario = detalles.split(', Precio: $')
    disponibilidad = int(disponibilidad)
    precio_unitario = float(precio_unitario[:-1])
else:
    st.warning('No hay productos disponibles en el refrigerador')
    producto = ''
    disponibilidad = 0
    precio_unitario = 0.0

cantidad = st.number_input('Cantidad', min_value=1, max_value=disponibilidad, step=1)
total = cantidad * precio_unitario
st.write(f'Precio Unitario: ${precio_unitario:.2f}')
st.write(f'Total: ${total:.2f}')

if st.button('Registrar Deuda') and trabajador and producto and cantidad > 0 and trabajador != 'Agregar nuevo trabajador...':
    registrar_deuda(trabajador, producto, cantidad, total)
    st.success('Deuda registrada exitosamente')

# Mostrar deudas pendientes
st.header('Deudas Pendientes')
deudas = obtener_deudas_pendientes()
for deuda in deudas:
    st.write(f'Trabajador: {deuda[1]}, Producto: {deuda[2]}, Cantidad: {deuda[3]}, Total: ${deuda[4]:.2f}, Fecha: {deuda[5]}')
    if st.button(f'Eliminar Deuda (ID: {deuda[0]})'):
        eliminar_deuda(deuda[0], deuda[2], deuda[3])
        st.success('Deuda eliminada y productos devueltos al refrigerador')

# Eliminar trabajadores
st.header('Eliminar Trabajador')
trabajador_a_eliminar = st.selectbox('Seleccione un trabajador para eliminar', trabajadores)
if st.button('Eliminar Trabajador') and trabajador_a_eliminar:
    eliminar_trabajador(trabajador_a_eliminar)
    st.success('Trabajador eliminado exitosamente')
